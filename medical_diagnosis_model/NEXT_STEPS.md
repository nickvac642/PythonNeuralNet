# Next Steps: From Prototype to Real‑Data Medical Model

Use this as a checklist to evolve v2 into a clinically useful, data‑driven system.

## Immediate (week 1–2)

- Define schema mapping
  - Single source of truth for: symptoms (IDs/labels), vitals (units/ranges), labs (normalization), demographics, context (season/exposure), unknown/NA encoding.
- Label policy
  - For each disease: criteria for “confirmed” (ICD‑10 + test) vs “presumptive”; clinician adjudication rules.
- PHI‑safe ingestion scaffolding
  - De‑identify; normalize units; provenance/audit logging; no raw PHI on disk.

## Foundation upgrades (week 2–3)

- Splits & imbalance
  - Patient‑level train/val/test split (no leakage); stratify; add class weights or weighted sampling.
- Training
  - Switch to Adam; add L2 weight decay; optional dropout in hidden layer; expose via config.
- Metrics & calibration
  - AUROC, AUPRC, F1, Top‑k, confusion per class.
  - Reliability diagrams + ECE; re‑tune temperature on held‑out set; subgroup calibration.

## Clinical fit (week 3–4)

- Rules expansion
  - Centor (with age), CURB‑65, seasonality priors, exposure risks; test‑gating suggestions.
- Safety rails
  - Red‑flag escalation list; conservative defaults on missing/conflicting data; “need more info” branch.

## Ops & tooling (parallel)

- Experiment tracking & configs
  - YAML configs, fixed seeds, run logs; simple experiment registry.
- Batch CLI
  - Score CSV/JSONL → outputs with predictions, differentials, confidence, flags.
- Docs & tests
  - Data dictionary (fields, ranges, encodings); update legal/privacy notes.
  - Unit tests for rules and pipeline; lightweight CI (lint + tests).

### Optional: Retrieval‑Augmented Generation (RAG)

- Purpose: supplement deterministic rules with up‑to‑date clinical context (guidelines, pathways, medication interactions) without hard‑coding everything.
- Where it fits: post‑prediction explanation and test suggestions.
  - Input: symptoms + top‑k differential + key findings
  - Retrieval: semantic search over curated clinical notes/guidelines (local vector store)
  - Generation: small prompt to produce “why” and “next steps” text; never overwrite the model’s probabilities, only annotate.
- Data hygiene:
  - Keep the RAG corpus de‑identified and versioned; source only trusted content.
  - Cache citations/URLs in exports; show provenance in the PDF.
- Minimal path to implement:
  1. Create `knowledge/` with curated markdown/JSON of guidelines (Centor, CURB‑65, flu season, red flags).
  2. Build an embedding index (e.g., sentence‑transformers) in `knowledge/index/`.
  3. After inference, retrieve top 3–5 passages with a query built from the case and top‑k differential.
  4. Generate a short rationale + test suggestions; include citations in the report.

#### Proof‑of‑Concept plan (baked into this project)

- Directory & files

  - `knowledge/` → curated content (markdown/json) with metadata: `title`, `source`, `url`, `version_date`, `tags`, `icd10`, `rule_id`.
  - `knowledge/index/` → vector index (FAISS/Chroma) + `meta.json` mapping ids → {text, metadata}.
  - `rag/index.py` → offline: chunk, embed, persist index.
  - `rag/retriever.py` → runtime: load index, retrieve top‑k passages.
  - `rag/generator.py` → compose rationale from retrieved passages (template‑based or small LLM).
  - `rag/config.yaml` → enable flag, model name, top_k, filters, paths.

- Offline indexing (one‑time)

  - Chunk to 300–600 tokens with overlap; embed with `sentence-transformers/all-MiniLM-L6-v2` (or similar); store normalized embeddings.
  - Persist index + `meta.json`; record index version and corpus snapshot date.

- Runtime integration (v2)

  - In `versions/v2/enhanced_medical_system.py`, after `diagnose_with_reasoning`:
    - Build query from: primary diagnosis, ICD‑10, key findings (from `clinical_reasoning`), top‑k differential, and any red flags.
    - `passages = retriever.search(query, top_k, filters={"icd10": primary_icd10})`
    - `rationale_text = generator.summarize(results, symptom_responses, passages)`
    - Display `rationale_text` in UI and include it (plus citations) in PDF/Text exports.

- Safety & provenance

  - Do not change probabilities; RAG only annotates.
  - Show source name/URL/version for each citation; keep `knowledge/README.md` of sources and update cadence.
  - Keep index local; avoid sending PHI to external services.

- Minimal evaluation
  - Retrieval precision@k spot‑checks by clinician reviewer.
  - Helpfulness rating of rationale/test suggestions.
  - Guardrails for disallowed content; keep output terse and cited.

## Full‑stack Web App (conversion roadmap)

### Architecture (high level)

- Backend API (Python/FastAPI): inference, RAG rationale, history, batch, export
- RAG service (can be a module or microservice): vector index + retrieval + citation
- Persistence: Postgres (sessions/history), object store for PDFs/models; optional Redis for queues
- Frontend (React/Next.js or SvelteKit): symptom wizard, results, history, batch upload
- Workers (Celery/RQ + Redis): long‑running jobs (batch scoring, PDF export)
- Observability: structured logs; metrics (Prometheus/OpenMetrics); optional tracing (OTel)

### API design (initial endpoints)

- `POST /api/v2/diagnose` → { symptoms: {name: severity}, options } → results (primary, differential, certainty, rationale refs)
- `POST /api/v2/rationale` → { results } → { text, citations } (if RAG decoupled)
- `POST /api/v2/export` → { patient_id, symptoms, results } → file path or download URL
- `POST /api/v2/batch` → CSV/JSONL upload → job id → progress → result file
- `GET  /api/v2/history/:patient_id` → sessions
- `GET  /api/v2/versions` → available model versions

### FastAPI specifics (quick start)

- Install deps (dev): `pip install fastapi uvicorn pydantic`
- Minimal backend scaffold:

```python
# backend/app.py
from fastapi import FastAPI
from pydantic import BaseModel
from versions.v2.medical_neural_network_v2 import ClinicalReasoningNetwork

app = FastAPI(title="Medical Diagnosis API", version="0.1.0")
model = ClinicalReasoningNetwork(hidden_neurons=25, learning_rate=0.3, epochs=1000)

@app.on_event("startup")
def load_model():
    try:
        model.load_model("medical_diagnosis_model/models/enhanced_medical_model.json")
    except Exception:
        model.train(cases_per_disease=50, verbose=False)
        model.save_model("medical_diagnosis_model/models/enhanced_medical_model.json")

class Symptoms(BaseModel):
    data: dict  # {"Fever": 8, "Cough": 6, ...}

@app.post("/api/v2/diagnose")
def diagnose(payload: Symptoms):
    results = model.diagnose_with_reasoning(payload.data)
    return results
```

- Run locally: `uvicorn backend.app:app --reload --port 8000`
- Try a request:

```bash
curl -X POST http://localhost:8000/api/v2/diagnose \
  -H 'Content-Type: application/json' \
  -d '{"data": {"Fever":8, "Fatigue":7, "Cough":6}}'
```

- Add CORS in dev (optional): `pip install fastapi[all]` and configure `from fastapi.middleware.cors import CORSMiddleware` with allowed origins (e.g., http://localhost:3000).

### Backend tasks (phase 1)

1. Package v2 model as a module with a simple `predict(symptoms_dict)` façade; warm‑load on app start
2. FastAPI app with `/diagnose` and `/export` (text export first), CORS configured for local dev
3. Config files (YAML/ENV): model path, calibration T, RAG enable, knowledge paths
4. Basic auth (API key or JWT) for dev; request logging and rate limiting

### Frontend tasks (phase 1)

1. Create a Next.js app with a symptom wizard (common + full), severity sliders, red‑flag badges
2. Call `/diagnose` and render: primary dx, confidence bar, differential table, rules triggered
3. Show RAG rationale + citations (when enabled); button to export report
4. Minimal history page (local only) until Postgres is wired

### Persistence & workers (phase 2)

- Postgres schema: patients, sessions, diagnoses, exports
- Move PDF export and batch scoring to a worker (Celery/RQ) with Redis; expose `/jobs/:id`
- Store artifacts in `exports/` (dev) → S3‑compatible object store (prod)

### Security & privacy

- HTTPS, CORS, CSRF (if needed), JWT/OAuth2 for user auth
- PHI‑safe mode: omit patient identifiers; encrypt at rest/in transit; audit logs
- Retention policy for history/exports; admin endpoint to purge

### Deployment

- Dockerize backend and frontend; docker‑compose for local
- Deploy to Fly.io/Render/DigitalOcean (simple) or Kubernetes (scaling)
- CI/CD: lint/tests → build → deploy; environment‑specific configs

### Suggested directory layout

```
medical_diagnosis_model/
  backend/
    app.py (FastAPI)
    api/ (routers: diagnose, export, batch, history)
    models/ (loaders, calibration)
    rag/ (retriever, generator, config)
  frontend/
    nextjs/ (pages, components, api client)
  workers/
    tasks.py (pdf export, batch)
  infra/
    docker/ docker-compose.yml, k8s/
```

### MVP milestone (2–3 days)

- `/diagnose` returns current v2 results; frontend wizard submits and renders
- Optional RAG rationale (if knowledge/ and index present)
- `/export` returns a text report; button in UI to download

## Interview‑aligned capabilities (must‑haves and nice‑to‑haves)

### React/Next.js, Python, TypeScript (Must‑Have)

- Frontend: convert the wizard to Next.js (TypeScript) with strong types for symptoms, results, and RAG citations.
- API client: typed fetch layer (Zod or OpenAPI client) for `/api/v2/diagnose`, `/export`, `/batch`.
- Backend: FastAPI with Pydantic models and explicit response schemas; mypy/ruff for typing/linting.

### LLM/AI API integration (Must‑Have)

- Add an optional `rag/generator.py` path using a hosted LLM (or local) for fluent but grounded rationale.
- Prompt design: templates that include primary dx, key findings, differential, and retrieved passages; enforce citation markers.
- Guardrails: max tokens, disallow medication/dose advice, output schema validation.

### RAG, prompt design, vector search (Must‑Have)

- Build `rag/index.py` (chunk → embed → store FAISS/Chroma) and `rag/retriever.py` (semantic search with filters).
- Add retrieval evaluation (precision@k), prompt ablations (different templates), and a small prompt library.

### Docker & Kubernetes on AWS (Must‑Have)

- Dockerfiles for backend and frontend; multi‑stage builds.
- docker‑compose for dev; k8s manifests or a Helm chart (`infra/k8s/`) with: Deployment, Service, HPA, ConfigMap/Secret, Ingress.
- AWS path: ECR for images, EKS for cluster, ALB ingress; S3 for exports/models; IAM roles for service accounts.

### CI/CD, API design, distributed systems (Must‑Have)

- CI: GitHub Actions to run lint/tests, build images, push to ECR, deploy to EKS.
- API: versioning (`/api/v2`), pagination for history, idempotent batch endpoints, health/readiness (`/healthz`, `/readyz`).
- Distributed: add Redis + Celery/RQ workers; retry strategy, dead‑letter queue; structured logs; Prometheus metrics.

### Data analytics & unstructured pipelines (Nice‑to‑Have)

- Add analytics jobs to compute cohort stats, calibration by subgroup, and drift reports; store in Postgres + dashboards (Grafana/Metabase).
- Unstructured pipeline: parse uploaded PDFs/notes (local OCR/NLP) into symptom candidates for human review; do not auto‑ingest as truth.

### Secure architecture & privacy‑first (Nice‑to‑Have)

- Secrets: use AWS Secrets Manager/SSM; no secrets in env files; rotate regularly.
- Network: VPC, private subnets for services, public only for ingress; least‑privilege IAM.
- App: CORS/CSRF where relevant, JWT/OAuth2; audit logs; encryption at rest/in transit; explicit retention and purge endpoints.

## Stretch goals

- Uncertainty‑aware UX
  - Monte‑Carlo dropout; route low‑confidence to more data/tests.
- External/temporal validation
  - Evaluate on time‑separated or out‑of‑site cohorts.
- Monitoring
  - Drift detection for feature distributions and calibration; periodic re‑train.

## First actionable tasks (suggested order)

1. Create `configs/clinical_schema.yaml` with symptom/vitals/labs mappings.
2. Implement patient‑level splitter and class weighting; add Adam/L2/dropout toggles.
3. Add metrics module (AUROC/AUPRC/F1/Confusion) and reliability diagram + ECE.
4. Expand rules: Centor + CURB‑65; add “need more info” if entropy/confidence threshold.
5. Build batch CLI to score CSV and emit results JSON/CSV.

> Tip: keep a changelog and version datasets/runs (seed, config, code commit) for reproducibility.
