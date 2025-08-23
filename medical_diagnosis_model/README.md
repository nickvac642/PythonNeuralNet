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
├── Medical Knowledge Base
│   ├── medical_symptom_schema.py       # 30 symptoms with medical terminology
│   ├── medical_disease_schema.py       # Original 10 diseases
│   └── medical_disease_schema_v2.py    # Enhanced with syndrome-level diagnoses
│
├── Neural Network Implementation
│   ├── medical_neural_network.py       # Basic medical NN
│   └── medical_neural_network_v2.py    # Clinical reasoning NN
│
├── Training & Data Generation
│   └── medical_training_generator.py   # Generates realistic patient cases
│
├── User Interfaces
│   ├── enhanced_medical_system.py      # Full-featured system
│   ├── interactive_medical_diagnosis.py # User-friendly interface
│   └── quick_medical_demo.py          # Quick demonstration
│
├── Additional Features
│   ├── diagnosis_history.py           # Patient history tracking
│   └── pdf_exporter.py               # PDF report generation
│
├── Demonstrations
│   ├── demo_all_features.py          # Shows all features
│   ├── demo_clinical_reasoning.py    # Clinical reasoning demo
│   └── demo_interface_example.py     # Interface examples
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

```python
# Basic usage
python enhanced_medical_system.py

# Quick demo
python quick_medical_demo.py

# Clinical reasoning demo
python demo_clinical_reasoning.py
```

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install reportlab  # For PDF export
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
