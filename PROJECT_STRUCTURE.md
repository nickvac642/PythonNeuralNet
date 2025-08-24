# Neural Network Project Structure

This project is organized into modular components for easy reuse and development of different neural network applications.

## Folder Organization

### 📁 `foundational_brain/`

The core neural network implementation that can be used as a foundation for any pattern recognition task.

**Contents:**

- `NeuralNet.py` - The foundational neural network with forward/backpropagation
- `README.md` - Documentation for the foundational network
- `.gitignore` - Version control configuration

**Use this when:** You want to build a new neural network application from scratch.

### 📁 `medical_diagnosis_model/`

A complete medical diagnosis system built on top of the foundational neural network.

**Contents:**

- All medical diagnosis source files (20+ files)
- Training architecture diagram
- Complete documentation
- Demo scripts
- Requirements file

**Use this when:** You want to run or extend the medical diagnosis system.

## How to Use

### For New Projects

1. Copy the `foundational_brain` folder
2. Rename it to your project (e.g., `image_recognition_model`)
3. Import and extend the base neural network:
   ```python
   from NeuralNet import initialize_network, train_network
   ```

### For Medical Diagnosis

1. Navigate to `medical_diagnosis_model/`
2. Create virtual environment and install dependencies
3. Run `python enhanced_medical_system.py`

## Moving Between Projects

Each folder is self-contained with all necessary dependencies:

```bash
# Work on medical diagnosis
cd medical_diagnosis_model/
python enhanced_medical_system.py

# Start a new project
cp -r foundational_brain/ my_new_model/
cd my_new_model/
# Begin development...
```

## Architecture Overview

```
PythonNeuralNet/
├── foundational_brain/          # Core neural network
├── medical_diagnosis_model/     # Medical application
└── future_model/               # Your next project
```

This modular structure allows you to:

- Keep models separate and organized
- Reuse the foundational code
- Develop multiple applications in parallel
- Easily share specific models without unnecessary files

## Medical Model Directory Map (v2)

```
medical_diagnosis_model/
  backend/
    app.py                 # FastAPI app: /api/v2/diagnose, /export, /adaptive/*
    security/jwt_dep.py    # OIDC/JWT scaffold (feature-flagged)
    selector/eig_selector.py # EIG ranking util (math-only)
  configs/
    clinical_schema.yaml   # Clinical data mappings (scaffold)
    training.yaml          # Training/optimizer toggles (scaffold)
  data/
    case.schema.json       # JSON Schema for clinical cases
    dictionaries/          # Canonical symptoms/diseases
    samples/               # Example JSONL dataset
    validate_cases.py      # Schema validator CLI
  tests/
    test_api_phase1.py     # API TestClient expected primaries
    test_selector.py       # EIG selector unit test
    phase_1_backend/       # cURL-based test harness & outputs
  tools/
    sanity.py              # Modular sanity CLI (data/tests/api/export/rate/adaptive/suite)
  versions/
    v1/, v2/               # Model implementations and demos
  exports/                 # Generated reports (gitignored)
  models/                  # Saved models (dev artifacts)
  diagnosis_history/       # Session logs (gitignored)
  README.md                # Usage + Auth
  NEXT_STEPS.md            # Roadmap & acceptance criteria
```

## Task Map (completed → pending)

- Completed
  - Data scaffolding: `data/case.schema.json`, `data/dictionaries/*`, `data/samples/*`, `data/validate_cases.py`
  - Backend phase 1: `/diagnose`, `/export` endpoints; CORS; API key auth; request logging; rate limiting
  - Security scaffold: OIDC/JWT dependency (`backend/security/jwt_dep.py`) behind `MDM_AUTH_MODE=oidc`
  - CI: GitHub Actions runs dataset validation and unit tests via sanity CLI
  - Adaptive (alpha): `/api/v2/adaptive/{start,answer,finish}` + EIG selector; sanity CLI coverage

- Pending (next)
  - Synthetic generator → emit JSONL to schema (`medical_training_generator.py` refactor)
  - Golden set (100 curated cases) with rationale/certainty
  - Data quality tests (sanity rules, leakage, balance) and `DATA_CARD.md`
  - Metrics & calibration module (AUROC/AUPRC/F1, reliability/ECE)
  - Batch scoring CLI (`backend/tools/batch`) and outputs
  - Adaptive end-to-end unit tests (FastAPI TestClient)
  - RAG PoC (knowledge/, index/, retriever/generator)
  - Frontend adaptive mode; persistence/workers; deployment

## Quick Testing Commands

```bash
# From medical_diagnosis_model/
python tools/sanity.py data
python tools/sanity.py tests
python tools/sanity.py api --auto-start --api-key devkey
python tools/sanity.py export --auto-start --api-key devkey
python tools/sanity.py rate --auto-start --api-key devkey --count 140 --expect-over-limit
python tools/sanity.py adaptive --auto-start --api-key devkey
python tools/sanity.py suite --auto-start --api-key devkey --with-api --with-export --with-rate --with-adaptive
```
