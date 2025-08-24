from fastapi import FastAPI
from pydantic import BaseModel
import os
import sys

# Ensure foundational_brain is importable
MODEL_ROOT = os.path.dirname(os.path.dirname(__file__))
REPO_ROOT = os.path.dirname(MODEL_ROOT)
if REPO_ROOT not in sys.path:
    sys.path.append(REPO_ROOT)

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
    data: dict


@app.post("/api/v2/diagnose")
def diagnose(payload: Symptoms):
    results = model.diagnose_with_reasoning(payload.data)
    return results


