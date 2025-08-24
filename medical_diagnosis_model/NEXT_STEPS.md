# Next Steps: From Prototype to Real‑Data Medical Model

Use this as a checklist to evolve v2 into a clinically useful, data‑driven system.

## Quick checklist

- [Immediate (week 1–2)](#immediate)
- [Foundation upgrades (week 2–3)](#foundation)
- [Clinical fit (week 3–4)](#clinical)
- [Ops & tooling (parallel)](#ops)
- [RAG (optional)](#rag)
- [Full‑stack web app roadmap](#fullstack)
- [Security & privacy](#security)
- [Deployment](#deployment)
- [Stretch goals](#stretch)
- [First actionable tasks](#first-actionable)

<a id="prompt-examples"></a>

### Prompt examples (copy/paste)

```text
Task: Implement patient- and time-based train/val/test split with stratification
Source: NEXT_STEPS.md → Foundation → Splits & imbalance
Context: macOS 14, Python 3.11 venv ./venv, repo root PythonNeuralNet
Constraints: non-interactive commands; add unit tests; idempotent CLI
Acceptance:
- backend/data/splitter.py with patient/time split; no-leakage tests
- CLI: python -m backend.tools.split --input data/clean/ --out data/splits/
- Outputs include class distribution report (per split)
```

```text
Task: Expose /api/v2/diagnose and /api/v2/export in FastAPI
Source: NEXT_STEPS.md → Full‑stack → Backend tasks (phase 1)
Context: FastAPI + Pydantic; v2 model packaged; local dev only
Constraints: CORS enabled for http://localhost:3000; typed responses
Acceptance:
- backend/app.py serves /api/v2/diagnose returning v2 payload
- /api/v2/export returns text report path
- OpenAPI docs load; simple request succeeds via curl
```

```text
Task: RAG PoC: index curated knowledge and return cited rationale
Source: NEXT_STEPS.md → Optional: RAG → Proof‑of‑Concept plan
Context: Local FAISS/Chroma only; no external PHI; minimal template generation
Constraints: RAG annotates only; never changes probabilities
Acceptance:
- knowledge/ populated; knowledge/index/ built; rag/index.py & retriever.py
- For 4/5 sample cases: retrieved passages relevant; rationale includes citations
- Export includes citation URLs/titles; inputs sanitized
```

<a id="immediate"></a>

## Immediate (week 1–2)

- Define schema mapping
  - Single source of truth for: symptoms (IDs/labels), vitals (units/ranges), labs (normalization), demographics, context (season/exposure), unknown/NA encoding.
  - Canonical ontology & synonym map for symptoms; explicit schema versioning and change log.
  - Acceptance criteria:
    - `configs/clinical_schema.yaml` exists with symptom/vitals/labs definitions and synonyms.
    - `backend/tools/validate_schema.py` validates ranges, encodings, and uniqueness; CI runs it.
    - Version tag and changelog updated when schema changes.
- Label policy
  - For each disease: criteria for “confirmed” (ICD‑10 + test) vs “presumptive”; clinician adjudication rules.
  - Acceptance criteria:
    - `docs/label_policy.md` describes labels and confirmatory evidence mapping.
    - Dataset fields include `diagnostic_certainty` and `evidence` (tests performed, results).
    - Unit tests assert mapping logic from raw cases → gold labels.
- PHI‑safe ingestion scaffolding
  - De‑identify; normalize units; provenance/audit logging; no raw PHI on disk.
  - Acceptance criteria:
    - `backend/ingest/ingest.py` with de‑id functions and unit normalization.
    - Audit log written per record; dry‑run mode produces no persistent PHI.
    - Command: `python -m backend.ingest.ingest --input data/raw.csv --out data/clean/` creates clean artifacts.

<a id="foundation"></a>

## Foundation upgrades (week 2–3)

- Splits & imbalance
  - Patient‑level and time‑based train/val/test split (no leakage); stratify; add class weights or weighted sampling.
  - Acceptance criteria:
    - `backend/data/splitter.py` implements patient/time‑based splits; no leakage tests pass.
    - CLI: `python -m backend.tools.split --input data/clean/ --out data/splits/` writes CSV lists and a class distribution report.
- Training
  - Switch to Adam; add L2 weight decay; optional dropout in hidden layer; expose via config.
  - Acceptance criteria:
    - Config toggles in `configs/training.yaml` enable Adam/L2/dropout; seed fixed.
    - Training summary logs include optimizer, regularization, and early stopping status.
- Metrics & calibration
  - AUROC, AUPRC, F1, Top‑k, confusion per class.
  - Reliability diagrams + ECE; re‑tune temperature on held‑out set; subgroup calibration (age/sex/season). Add drift monitors for class priors and feature distributions.
  - Acceptance criteria:
    - `backend/metrics/` outputs metrics JSON and plots (confusion, reliability) to `reports/`.
    - Temperature scaling recalibrates on validation set; ECE reported overall and by subgroup.
    - Drift check script flags shifts in class priors and key feature distributions.

<a id="clinical"></a>

## Clinical fit (week 3–4)

- Rules expansion
  - Centor (with age), CURB‑65, seasonality priors, exposure risks; test‑gating suggestions.
  - Acceptance criteria:
    - Unit tests for Centor and CURB‑65 thresholds; seasonality/exposure rules documented and tested.
    - Rules integrated in reasoning step without overriding probabilities unless gated by evidence.
- Safety rails
  - Red‑flag escalation list; conservative defaults on missing/conflicting data; “need more info” branch.
  - Acceptance criteria:
    - Red flags trigger explicit warnings and suggested actions; entropy/confidence threshold routes to “need more info”.
    - Test cases cover missing/contradictory inputs and red‑flag handling.

<a id="ops"></a>

## Ops & tooling (parallel)

- Experiment tracking & configs
  - YAML configs, fixed seeds, run logs; simple experiment registry.
  - Acceptance criteria:
    - Each run saves `configs/*.yaml`, seed, code commit, and metrics in `runs/{timestamp}/`.
    - A summary index CSV lists runs with key metrics for comparison.
- Batch CLI
  - Score CSV/JSONL → outputs with predictions, differentials, confidence, flags.
  - Acceptance criteria:
    - CLI: `python -m backend.tools.batch --input data/cases.csv --out outputs/` writes per‑row results JSON/CSV.
    - Exit codes: 0 on success; non‑zero on validation errors; logs include row numbers.
- Docs & tests
  - Data dictionary (fields, ranges, encodings); update legal/privacy notes.
  - Unit tests for rules and pipeline; lightweight CI (lint + tests).
  - Acceptance criteria:
    - `docs/data_dictionary.md` added; CI workflow runs lint + unit tests on PRs.

<a id="rag"></a>

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
  - Sanitize prompts/inputs; enforce citation presence in generated text.

- Minimal evaluation
  - Retrieval precision@k spot‑checks by clinician reviewer.
  - Helpfulness rating of rationale/test suggestions.
  - Guardrails for disallowed content; keep output terse and cited.
  - Acceptance criteria:
    - `knowledge/` populated with curated content and `knowledge/index/` built.
    - Retrieval returns relevant passages for at least 4/5 sample cases; rationale includes citations.

<a id="fullstack"></a>

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
  - Provide an OpenAPI spec and generate a TypeScript client for the frontend to prevent schema drift.

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

- Acceptance criteria:
  - API responds on `/api/v2/diagnose` with v2 payload; OpenAPI docs accessible; CORS works in dev.
  - Text export endpoint returns a file; config toggles read from ENV/YAML.

### Frontend tasks (phase 1)

1. Create a Next.js app with a symptom wizard (common + full), severity sliders, red‑flag badges
2. Call `/diagnose` and render: primary dx, confidence bar, differential table, rules triggered
3. Show RAG rationale + citations (when enabled); button to export report
4. Minimal history page (local only) until Postgres is wired

- Acceptance criteria:
  - Wizard flow submits to API and renders primary diagnosis, confidence, differential, rules.
  - Export button downloads a text report; basic error states covered.

### Persistence & workers (phase 2)

- Postgres schema: patients, sessions, diagnoses, exports
- Move PDF export and batch scoring to a worker (Celery/RQ) with Redis; expose `/jobs/:id`
- Store artifacts in `exports/` (dev) → S3‑compatible object store (prod)

  - Acceptance criteria:
    - Postgres schema applied; `/jobs/:id` reflects worker progress; artifacts saved and retrievable.

<a id="security"></a>

### Security & privacy

- HTTPS, CORS, CSRF (if needed), JWT/OAuth2 for user auth
- PHI‑safe mode: omit patient identifiers; encrypt at rest/in transit; audit logs
- Retention policy for history/exports; admin endpoint to purge

  - Acceptance criteria:
    - Auth on protected endpoints; PHI‑safe mode verified; purge endpoint removes records and artifacts.

<a id="deployment"></a>

### Deployment

- Dockerize backend and frontend; docker‑compose for local; persistent volumes for model and embedding index.
- Deploy to Fly.io/Render/DigitalOcean (simple) or Kubernetes (scaling)
- CI/CD: lint/tests → build → deploy; environment‑specific configs
- Database migrations with Alembic; pre‑deploy smoke tests.

  - Acceptance criteria:
    - Local dev via docker‑compose brings up API + frontend; migrations run automatically.
    - CI pipeline builds images and deploys to staging; smoke test hits `/healthz` and `/api/v2/versions`.

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

<a id="stretch"></a>

## Stretch goals

- Uncertainty‑aware UX
  - Monte‑Carlo dropout; route low‑confidence to more data/tests.
- External/temporal validation
  - Evaluate on time‑separated or out‑of‑site cohorts.
- Monitoring
  - Drift detection for feature distributions and calibration; periodic re‑train.

<a id="first-actionable"></a>

## First actionable tasks (suggested order)

1. Create `configs/clinical_schema.yaml` with symptom/vitals/labs mappings.
2. Write `docs/label_policy.md`; wire gold labels (confirmed vs presumptive) into dataset.
3. Build PHI‑safe ingestion CLI: de‑identify, normalize units, audit logs → `data/clean/`.
4. Implement patient‑ and time‑based splits with stratification; add class weighting.
5. Add training toggles (Adam, L2, dropout) and fixed seeds via `configs/training.yaml`.
6. Add metrics module (AUROC/AUPRC/F1/Confusion) and reliability diagram + ECE.
7. Expand rules: Centor + CURB‑65; add “need more info” if entropy/confidence threshold.
8. Build batch CLI to score CSV and emit results JSON/CSV.

> Tip: keep a changelog and version datasets/runs (seed, config, code commit) for reproducibility.
