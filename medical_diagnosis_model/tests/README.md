# Tests Overview

This directory contains unit tests and harnesses for the medical diagnosis model.

## What we test

- API v2 core
  - `test_api_phase1.py`: validates responses against sample cases using FastAPI TestClient.
- Selector math
  - `test_selector.py`: checks Expected Information Gain (EIG) ranking on toy distributions.
- Security & Ops
  - `test_security_cors_rate.py`: CORS preflight (localhost:3000), API key auth (401 vs 200), rate limiting (429 on bursts).
- Adaptive endpoints (alpha)
  - `test_adaptive_endpoints.py`: start → answer → finish flow.

## How to run

```bash
# From repo root
PYTHONPATH="$PWD:$PWD/medical_diagnosis_model" MDM_QUICK_TRAIN=1 \
pytest -q medical_diagnosis_model/tests
```

## Sanity CLI (recommended)

Run end-to-end checks and write a JSON report:

```bash
cd medical_diagnosis_model
python tools/sanity.py suite --auto-start --api-key devkey \
  --with-api --with-export --with-rate --with-adaptive \
  --report-json reports/sanity_latest.json
```

## Outputs and artifacts

- tests/phase_1_backend/outputs/: cURL-based runs and summaries (gitignored)
- exports/: generated PDFs from /export (gitignored)
- reports/sanity_latest.json: suite status summary
