# Next Steps: From Prototype to Real‑Data Medical Model

Use this as a checklist to evolve v2 into a clinically useful, data‑driven system.

## Quick checklist

- [10‑minute Quickstart](#quickstart)
- [Immediate (week 1–2)](#immediate)
- [Foundation upgrades (week 2–3)](#foundation)
- [Clinical fit (week 3–4)](#clinical)
- [Adaptive questioning (clinical fit)](#adaptive)
- [Ops & tooling (parallel)](#ops)
- [RAG (optional)](#rag)
- [Full‑stack web app roadmap](#fullstack)
- [Security & privacy](#security)
- [Deployment](#deployment)
- [Stretch goals](#stretch)
- [Governance checklist](#governance)
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
  - Dataset scaffolding (v0)
    - Acceptance criteria:
      - [x] JSON Schema for clinical cases present at `data/case.schema.json`.
      - [x] Canonical dictionaries at `data/dictionaries/{symptoms.json,diseases.json}`.
      - [x] Sample JSONL at `data/samples/cases_v0.1.jsonl` following the schema.
      - [x] Validator CLI `data/validate_cases.py` passes on samples; `jsonschema` added to requirements.
      - [x] Command: `python data/validate_cases.py data/samples/cases_v0.1.jsonl` prints `Validation passed: 0 errors`.
    - References: `data/README.md`, `data/case.schema.json`, `data/dictionaries/`, `data/samples/`, `data/validate_cases.py`.

- [x] Training data v0.2 (balance + explicit negatives)
  - Goal: reduce early UTI bias; encode negative GU evidence in respiratory cases and vice‑versa; strengthen URI patterns and mild/early variants.
  - Acceptance criteria:
    - [x] Generator emits JSONL to schema with balanced class counts (or class weights are configured). See `data/generate_v02.py` → `data/v02/cases_v02.jsonl`.
    - [x] Respiratory cases explicitly mark `dysuria=0`, `frequency=0`; GU cases often mark `cough=0`, `rhinorrhea=0`, `congestion=0`.
    - [x] URI patterns included (cough + rhinorrhea + congestion ± low fever, sore throat); GU patterns (dysuria + frequency).
    - [x] Mild/early and atypical variants present; unknowns used appropriately.
    - [x] Dataset versioned as v0.2; training pipeline `tools/train_pipeline.py` writes model to `models/enhanced_medical_model_v02.json`.
    - [x] Re‑train + calibration performed; quick confusion/ECE report at `reports/metrics_v02.json` shows improved Resp vs GU separation.
- Label policy
  - For each disease: criteria for “confirmed” (ICD‑10 + test) vs “presumptive”; clinician adjudication rules.
  - Acceptance criteria:
    - `docs/label_policy.md` describes labels and confirmatory evidence mapping.
    - Dataset fields include `diagnostic_certainty` and `evidence` (tests performed, results).
    - Unit tests assert mapping logic from raw cases → gold labels.
    - Clinician sign-off required for any label policy change; changelog entry records reviewer and date.
    - PRs modifying label policy carry a "Clinical-Reviewed" label before merge.
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
    - Class weighting or balanced sampling applied if class counts are imbalanced; documented in DATA_CARD.

- Transformer baseline
  - Implement a tiny Transformer classifier as a comparative baseline to the current MLP.
  - Acceptance criteria:
    - `foundational_brain/nano_transformer.py` with tokenization (symptom IDs), embeddings, 2–4 attention blocks, and classifier head; trained with cross‑entropy.
    - CLI to train/evaluate on v0.2 data and save metrics: `python -m foundational_brain.nano_transformer --jsonl medical_diagnosis_model/data/v02/cases_v02.jsonl`.
    - Report comparing MLP vs Transformer on accuracy, confusion, and ECE written to `medical_diagnosis_model/reports/transformer_baseline.json`.
    - README snippet explaining differences (sequence modeling, attention) and when Transformer helps.
- Metrics & calibration
  - AUROC, AUPRC, F1, Top‑k, confusion per class.
  - Reliability diagrams + ECE; re‑tune temperature on held‑out set; subgroup calibration (age/sex/season). Add drift monitors for class priors and feature distributions.
  - Acceptance criteria:
    - `backend/metrics/` outputs metrics JSON and plots (confusion, reliability) to `reports/`.
    - Temperature scaling recalibrates on validation set; ECE reported overall and by subgroup.
    - Drift check script flags shifts in class priors and key feature distributions.
    - Quarterly subgroup error and calibration review documented with mitigation action items.
    - For adaptive mode: track median questions to reach decision threshold, and question distribution per syndrome.

<a id="clinical"></a>

## Clinical fit (week 3–4)

- Rules expansion
  - Centor (with age), CURB‑65, seasonality priors, exposure risks; test‑gating suggestions.
  - Acceptance criteria:
    - Unit tests for Centor and CURB‑65 thresholds; seasonality/exposure rules documented and tested.
    - Rules integrated in reasoning step without overriding probabilities unless gated by evidence.
    - Implemented guardrails:
      - Pneumonia triad (cough+dyspnea+chest pain+fever, no anosmia) favors `Pneumonia Syndrome`.
      - Strep/URI pattern (sore throat high, cough absent, no anosmia) downweights ILI/COVID and nudges `Viral Upper Respiratory Infection`.
    - Clinician review and approval required for rule thresholds; changes logged in `docs/rules_changelog.md`.
- Safety rails
  - Red‑flag escalation list; conservative defaults on missing/conflicting data; “need more info” branch.
  - Acceptance criteria:
    - Red flags trigger explicit warnings and suggested actions; entropy/confidence threshold routes to “need more info”.
    - Test cases cover missing/contradictory inputs and red‑flag handling.
    - Red‑flag list reviewed and signed off by clinician reviewer; escalation path tested in a tabletop exercise.

<a id="adaptive"></a>

### Adaptive questioning (Akinator‑style)

- Purpose: adaptively select the next most informative question (symptom) while preserving clinical safety, syndrome‑first gating, and negative‑evidence handling.
- Core method: expected information gain (entropy reduction) over current disease posterior; answers support yes/no/unknown.
- Stop rules: threshold on top‑1 confidence or maximum question count; downgrade to syndrome if confirmatory test is required.
- Acceptance criteria:
  - [x] Selector module exists (e.g., `backend/selector/eig_selector.py`) that scores candidate questions by expected entropy reduction; supports yes/no/unknown and missing data.
  - [x] Integrated with v2 reasoning: selector respects syndrome gates and negative evidence; endpoints return diagnosis when threshold reached or max questions hit.
  - [x] Stop rules implemented and configurable (env/params); unknown answers supported.
  - [x] Unit tests cover end‑to‑end adaptive sessions (FastAPI TestClient) reaching a stable decision with stop rules; question count target to be tuned later.
  - [x] Cross‑references: API exposes interactive endpoints (`/api/v2/adaptive/{start,answer,finish}`); frontend Adaptive mode planned; metrics to include question efficiency.

<a id="ops"></a>

## Ops & tooling (parallel)

- Experiment tracking & configs
  - YAML configs, fixed seeds, run logs; MLflow for runs/artifacts; Hydra for hierarchical configs.
  - Acceptance criteria:
    - MLflow tracking enabled locally: params/metrics/artifacts (model, reports) recorded per run under `mlruns/`.
    - Hydra‑based configs under `medical_diagnosis_model/configs/` with overrides for optimizer, regularization, and model type (mlp|transformer).
    - Each run logs code commit hash, dataset version, seed; outputs in `runs/{timestamp}/` include a summary JSON and links to MLflow artifacts.
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
    - [ ] `docs/data_dictionary.md` added; CI workflow runs lint + unit tests on PRs.
    - [x] EIG selector unit tests validate entropy reduction and expected next‑question behavior on toy distributions.
    - [x] CI executes `python medical_diagnosis_model/data/validate_cases.py` against `data/samples/*.jsonl` and any tracked dataset JSONL files.

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
    - Quarterly citation/source review; `knowledge/README.md` lists sources, review dates, and curators; untrusted sources disallowed.

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

Interactive (adaptive) endpoints (alpha):

- `POST /api/v2/adaptive/start` → { optional: prior_answers } → { session_id, next_question }
- `POST /api/v2/adaptive/answer` → { session_id, question, answer: yes|no|unknown, optional: severity } → { next_question or results }
- `POST /api/v2/adaptive/finish` → { session_id } → final results

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

<a id="quickstart"></a>

### 10‑minute Quickstart

Pre‑flight (macOS/zsh):

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install fastapi uvicorn pydantic
```

Scaffold directories:

```bash
mkdir -p backend api models rag knowledge knowledge/index configs reports runs exports
```

Create the API:

- Copy the FastAPI scaffold from “FastAPI specifics (quick start)” into `backend/app.py`.

Run locally:

```bash
uvicorn backend.app:app --reload --port 8000
```

Smoke test:

```bash
curl -X POST http://localhost:8000/api/v2/diagnose \
  -H 'Content-Type: application/json' \
  -d '{"data": {"Fever":8, "Fatigue":7, "Cough":6}}'
```

Next steps:

- Add `configs/clinical_schema.yaml` and `configs/training.yaml` per sections below.
- If enabling RAG later, populate `knowledge/` and build `knowledge/index/`.

- Run locally: `uvicorn backend.app:app --reload --port 8000`
- Try a request:

```bash
curl -X POST http://localhost:8000/api/v2/diagnose \
  -H 'Content-Type: application/json' \
  -d '{"data": {"Fever":8, "Fatigue":7, "Cough":6}}'
```

- Add CORS in dev (optional): `pip install fastapi[all]` and configure `from fastapi.middleware.cors import CORSMiddleware` with allowed origins (e.g., http://localhost:3000).

### Backend tasks (phase 1)

- [x] Package v2 model as a module with a simple `predict(symptoms_dict)` façade; warm‑load on app start
- [x] FastAPI app with `/diagnose` and `/export` (text/PDF export); OpenAPI docs accessible
- [x] Config files (YAML/ENV): model path, calibration T, quick‑train flag
- [x] Add CORS for local dev (http://localhost:3000)
- [x] Basic auth (API key or JWT) for dev; request logging and rate limiting

- Acceptance criteria:
  - [x] `/api/v2/diagnose` returns v2 payload in local runs and TestClient
  - [x] `/api/v2/export` returns a file path; artifact saved under `exports/`
  - [x] CORS enabled for dev origin; requests succeed from browser
  - [x] Auth key/JWT check in dev; basic rate limiting in place

### Frontend tasks (phase 1)

1. Create a Next.js app with a symptom wizard (common + full), severity sliders, red‑flag badges
2. Call `/diagnose` and render: primary dx, confidence bar, differential table, rules triggered
3. Show RAG rationale + citations (when enabled); button to export report
4. Minimal history page (local only) until Postgres is wired

- Acceptance criteria:
  - Wizard flow submits to API and renders primary diagnosis, confidence, differential, rules.
  - Export button downloads a text report; basic error states covered.

Adaptive mode (alpha):

- Interactive wizard calls `/api/v2/adaptive/*` to fetch next question and submit answers (Yes/No/Unknown). Feature‑flagged; respects red‑flag interrupts and stop‑on‑confidence.

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
    - Data Use Agreement (DUA) checklist required for any data import/export; stored in `docs/dua.md`.
    - Incident response runbook in `docs/incident_runbook.md`; exercise performed at least once.
    - Scheduled purge verification job runs and logs results; report stored in `reports/purge_checks/`.

#### Auth: OAuth2/OIDC + JWT (production)

- Identity & flow

  - Choose provider (Auth0/Okta/Cognito/Keycloak). Use OIDC Authorization Code + PKCE for browser logins; Client Credentials for service‑to‑service.
  - Prefer BFF pattern: frontend calls a server route that exchanges code → tokens and sets httpOnly, Secure, SameSite=strict session cookie; tokens never stored in browser.

- Token model

  - Access tokens 5–15 min TTL; refresh tokens with rotation + reuse detection.
  - Claims: `sub`, `aud`, `iss`, `exp`, `iat`, `scope`/roles; optional tenant/org.
  - Validate via JWKS (`/.well-known/jwks.json`); support key rotation using `kid`.

- FastAPI protection

  - Add Bearer dependency that caches JWKS, verifies signature and `iss`/`aud`/`exp`, and extracts user/roles from claims.
  - Apply to routers/endpoints; return 401 (unauthenticated) / 403 (forbidden) appropriately.

- Authorization

  - Define RBAC scopes (e.g., `read:diagnosis`, `write:export`, `admin:*`).
  - Enforce at route level and within business logic for resource ownership.

- App/infra hardening

  - Strict redirect URI allowlist; `state` + PKCE; HTTPS only; CORS locked to prod domains.
  - Secrets in secret manager; structured audit logs with `sub`/`jti`; per‑IP and per‑subject rate limiting.
  - Token revocation list (store `jti`) for logout/compromise handling.

- Lifecycle & ops

  - Session idle and absolute timeouts; logout clears session and revokes refresh.
  - Metrics/alerts on auth failures, token errors, rate‑limit hits.
  - Runbooks for key rotation, incident response, and compromised credentials.

- Testing & CI

  - Mock provider for unit tests; E2E against a dev tenant.
  - Negative tests: expired token, wrong `aud`/`iss`, revoked `jti`, missing scopes.
  - CI secrets stored in GitHub Actions secrets; no tokens in logs.

- Suggested implementation order

  1. Pick provider and create dev tenant/app; set `OIDC_ISSUER`, `OIDC_AUDIENCE`.
  2. Implement JWKS validation dependency and scope checks in FastAPI behind a feature flag.
  3. Add Next.js BFF login/callback routes using Authorization Code + PKCE; issue server session cookie.
  4. Gate endpoints by scopes; add role mapping and ownership checks.
  5. Add refresh rotation, logout, revocation list; structured audit logs.
  6. E2E tests (happy path + negatives), CI secrets, and a staging rollout.

- Acceptance criteria
  - `backend/security/jwt_dep.py` with JWKS caching and verification; unit tests for `iss`/`aud`/`exp` and invalid `kid`.
  - Protected routes use dependency with scope checks; 401/403 paths covered by tests.
  - Next.js server routes implement code exchange with PKCE and set httpOnly cookies; tokens not accessible to JS.
  - Staging environment configured with provider; E2E passes; rollback plan documented.

<a id="deployment"></a>

### Deployment

- Dockerize backend and frontend; docker‑compose for local; persistent volumes for model and embedding index.
- Deploy to Fly.io/Render/DigitalOcean (simple) or Kubernetes (scaling)
- CI/CD: lint/tests → build → deploy; environment‑specific configs
- Database migrations with Alembic; pre‑deploy smoke tests.

  - Acceptance criteria:
    - Local dev via docker‑compose brings up API + frontend; migrations run automatically.
    - CI pipeline builds images and deploys to staging; smoke test hits `/healthz` and `/api/v2/versions`.
    - Shadow-mode/pilot evaluation enabled behind feature flags; clinician scoring collected before enablement.
    - Canary deployment with rollback plan documented; feature toggles for RAG and new rules.

### Suggested directory layout

```
medical_diagnosis_model/
  backend/
    app.py (FastAPI)
    api/ (routers: diagnose, export, batch, history)
    models/ (loaders, calibration)
    rag/ (retriever, generator, config)
  data/
    case.schema.json
    dictionaries/
      symptoms.json
      diseases.json
    samples/
      cases_v*.jsonl
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

<a id="governance"></a>

## Appendix: Governance checklist

- Clinical sign‑off
  - Label policy changes reviewed and approved by a clinician; changelog records reviewer and date.
  - Clinical rules/thresholds (Centor, CURB‑65, red flags) changes reviewed; updates logged in `docs/rules_changelog.md`.
- Data governance
  - Data Use Agreement (DUA) required for any import/export; tracked in `docs/dua.md`.
  - PHI purge verification runs on schedule; logs saved under `reports/purge_checks/`.
  - Incident response runbook maintained in `docs/incident_runbook.md`; tabletop exercise performed at least annually.
- RAG provenance
  - Quarterly source/citation review; `knowledge/README.md` lists sources, last review dates, and curators; untrusted sources disallowed.
- Fairness & calibration
  - Quarterly subgroup error/ECE review; mitigation actions tracked and assigned owners.
- Rollout controls
  - Shadow‑mode/pilot behind feature flags; clinician scoring collected prior to enablement.
  - Canary deployments with rollback plan; toggles for RAG and new rules.
- Review cadence (suggested)
  - Monthly: drift reports for features/class priors; check for distribution shifts.
  - Quarterly: calibration/fairness review; RAG sources review; purge verification report.
  - Semi‑annual: incident response tabletop exercise.
- Ownership & audit
  - Roles: Clinical reviewer, Data steward, Security lead, ML owner, Ops owner (document in `docs/governance_log.md`).
  - Artifacts retained: run configs/metrics in `runs/`, schema versions, code commit hashes, decision logs.

<a id="first-actionable"></a>

## First actionable tasks (suggested order)

1. Create `configs/clinical_schema.yaml` with symptom/vitals/labs mappings.
2. Regenerate training data v0.2 (balanced counts or class weights; explicit negative GU for respiratory and vice‑versa; URI patterns; mild/early/atypical). Retrain + recalibrate; update DATA_CARD.
3. Write `docs/label_policy.md`; wire gold labels (confirmed vs presumptive) into dataset.
4. Build PHI‑safe ingestion CLI: de‑identify, normalize units, audit logs → `data/clean/`.
5. Implement patient‑ and time‑based splits with stratification; add class weighting.
6. Add training toggles (Adam, L2, dropout) and fixed seeds via `configs/training.yaml`.
7. Add metrics module (AUROC/AUPRC/F1/Confusion) and reliability diagram + ECE.
8. Expand rules: Centor + CURB‑65; add “need more info” if entropy/confidence threshold.
9. Build batch CLI to score CSV and emit results JSON/CSV.

10. Implement adaptive questioning selector stub (`backend/selector/eig_selector.py`) with unit tests on toy distributions; wire a no‑UI CLI demo.
11. Add nano‑Transformer baseline (`foundational_brain/nano_transformer.py`) + CLI; compare vs MLP and write `reports/transformer_baseline.json`.
12. Wire MLflow tracking and Hydra configs for both MLP and Transformer runs; log params/metrics/artifacts and enable easy overrides.

> Tip: keep a changelog and version datasets/runs (seed, config, code commit) for reproducibility.
