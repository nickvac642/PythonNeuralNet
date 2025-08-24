# Phase 1 Backend Tests

This suite exercises the FastAPI endpoints for the medical diagnosis model.

## Structure

- `cases.json`: Named input symptom sets grouped by scenario.
- `run_tests.py`: Runs all cases against `/api/v2/diagnose`, optionally `/api/v2/export`, and writes results to `outputs/`.
- `outputs/`: Timestamped responses per case.

## Usage

From `medical_diagnosis_model/` with the API running on port 8000:

```bash
python tests/phase_1_backend/run_tests.py
```

Outputs will be saved under `tests/phase_1_backend/outputs/`.
