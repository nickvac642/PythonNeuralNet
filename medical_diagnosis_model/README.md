# Medical Diagnosis Neural Network System

A comprehensive medical diagnosis system that uses neural networks with clinical reasoning capabilities.

## Overview

This system implements a medically-accurate diagnostic tool that thinks like a doctor:

- Starts with syndrome-level diagnosis (e.g., "Viral URI" not "Influenza")
- Knows when confirmatory testing is required
- Provides appropriate differential diagnoses
- Includes 15 diseases across multiple categories
- Uses ICD-10 medical coding standards

## Project Structure

```
medical_diagnosis_model/
├── Core Neural Network
│   └── NeuralNet.py                    # Foundational neural network
│
├── Shared Modules
│   ├── medical_symptom_schema.py       # 30 symptoms with medical terminology
│   ├── medical_training_generator.py   # Generates realistic patient cases
│   ├── diagnosis_history.py            # Patient history tracking
│   ├── pdf_exporter.py                 # PDF report generation
│   ├── models/  data/  exports/  diagnosis_history/
│
├── versions/
│   ├── v1/
│   │   ├── medical_disease_schema.py
│   │   ├── medical_neural_network.py
│   │   ├── interactive_medical_diagnosis.py
│   │   ├── quick_medical_demo.py
│   │   ├── demo_all_features.py  demo_interface_example.py  medical_diagnosis_example.py
│   └── v2/
│       ├── medical_disease_schema_v2.py
│       ├── medical_neural_network_v2.py
│       ├── enhanced_medical_system.py
│       └── demo_clinical_reasoning.py
│
└── Documentation
    ├── README.md                      # This file
    └── training_architecture_diagram.md # Visual training process
```

## Key Features

### 1. Clinical Reasoning

- Syndrome-level diagnosis without tests
- Specific diagnosis with confirmatory testing
- Appropriate differential diagnosis
- Clinical decision rules (Centor criteria, CURB-65)

### 2. Medical Accuracy

- 30 symptoms with ICD-10 codes
- 15 diseases across categories
- Realistic symptom patterns
- Etymology for educational value

### 3. Enhanced UI

- Symptom categories (Respiratory, GI, etc.)
- Severity assessment (0-10 scale)
- Confidence visualization
- Clear medical recommendations

### 4. Additional Features

- Patient history tracking
- PDF report export
- Training data generation
- Model persistence

## Quick Start

```bash
# Dynamic menu (recommended)
python run.py

# Or run specific versions directly
python versions/v2/enhanced_medical_system.py
python versions/v2/demo_clinical_reasoning.py
python versions/v1/quick_medical_demo.py
python versions/v1/interactive_medical_diagnosis.py
```

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install reportlab  # For PDF export

# Models are saved/loaded here by default
# medical_diagnosis_model/models/enhanced_medical_model.json
```

## Medical Disclaimer

This system is for educational purposes only. It should NOT be used as a substitute for professional medical advice. Always consult qualified healthcare providers for medical diagnosis and treatment.

## Disease Categories

- **Respiratory**: URI, Influenza, COVID-19, Pneumonia, Bronchitis, Sinusitis
- **Gastrointestinal**: Gastroenteritis
- **Cardiovascular**: Hypertension
- **Metabolic**: Type 2 Diabetes
- **Rheumatologic**: Rheumatoid Arthritis
- **Neurological**: Migraine
- **Psychiatric**: Depression, Anxiety
- **Genitourinary**: UTI
- **Allergic**: Allergic Rhinitis

## Diagnostic Certainty Levels

1. **CLINICAL**: Can diagnose based on symptoms alone (e.g., Viral URI)
2. **PRESUMPTIVE**: Likely diagnosis but benefits from testing (e.g., ILI)
3. **CONFIRMATORY**: Requires specific test (e.g., Influenza, COVID-19)

## Training Architecture

See `training_architecture_diagram.md` for a visual representation of how the system learns medical patterns.

## Version History

- **V1**: Basic medical diagnosis with 10 diseases
- **V2**: Enhanced with clinical reasoning, syndrome-level diagnosis, and 15 diseases

---

## Legal, Safety, and Responsible Use

### Intended Use

- This software is provided for educational and research purposes only.
- It is not a medical device and must not be used for diagnosis, triage, or treatment decisions.
- The included data generation and demos use synthetic patterns; no real patient data are provided or required.

### Regulatory Status

- Not FDA/EMA/MDR approved; not validated as SaMD (Software as a Medical Device).
- Any clinical use would require a compliant quality system and regulatory pathway (e.g., IEC 62304, ISO 14971, ISO 13485, FDA 510(k)/De Novo as applicable).

### Medical Disclaimer

- Not a substitute for professional medical advice, diagnosis, or treatment.
- Always consult licensed healthcare professionals. In emergencies, call local emergency services.

### Data Privacy and PHI

- Do not use real patient data with this repository.
- If adapted for PHI: de-identify data, define retention policies, encrypt at rest and in transit, enforce access controls and audit logging, and ensure HIPAA/other regional compliance.
- Generated files and outputs are written to:
  - `models/` (saved model artifacts)
  - `data/` (generated datasets/examples)
  - `exports/` (PDF/text reports)
  - `diagnosis_history/` (session logs)
- Avoid committing any sensitive data to version control.

### Security

- No external network calls by default. Use a virtual environment and keep dependencies updated.
- Do not store secrets in the repository. Review and restrict file permissions as needed.

### Bias, Limitations, and Validation

- Training uses synthetic data with heuristic medical patterns for demonstration; results are illustrative.
- No prospective/clinical validation; accuracy metrics (if any) would reflect synthetic evaluation.
- Coverage of ICD-10 codes is partial; logic is syndrome-first and does not include labs/imaging unless added by you.

### Responsible AI Usage

- Human-in-the-loop is required; outputs are suggestions, not decisions.
- Red flags are heuristic and do not replace clinical judgment; never delay emergency care.
- Avoid deployment in high-risk settings without formal validation and oversight.

### Testing and Versioning

- Model versions: v1.x (baseline), v2.x (clinical reasoning and syndrome-first diagnosis).
- Maintain a changelog for medically relevant changes.
- To reproduce training: set a fixed random seed and record generator parameters.

### Third-Party Licenses

- This project uses `reportlab` for PDF export; see its license.
- The repository is licensed under MIT (see root `LICENSE`).

### Contact and Issues

- Report bugs and safety concerns via issues in the repository.
- For requests to remove mistakenly uploaded data, open an issue or contact the maintainer.

### Purging History/Outputs Safely

Run these commands from the `medical_diagnosis_model/` folder.

```bash
# Preview what will be deleted
ls -la exports diagnosis_history data models || true

# Purge ALL generated artifacts (irreversible)
rm -rf exports/* diagnosis_history/* data/* models/*

# Alternatively, remove only PDFs from exports
find exports -type f -name "*.pdf" -delete

# Recreate placeholder files if you want git to keep empty folders
for d in exports diagnosis_history data models; do
  [ -d "$d" ] || mkdir -p "$d"; touch "$d/.gitkeep";
done
```
