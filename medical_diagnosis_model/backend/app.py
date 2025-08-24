from fastapi import FastAPI
from pydantic import BaseModel
import os
import sys

# Ensure foundational_brain is importable
MODEL_ROOT = os.path.dirname(os.path.dirname(__file__))
REPO_ROOT = os.path.dirname(MODEL_ROOT)
for p in (REPO_ROOT, MODEL_ROOT):
    if p not in sys.path:
        sys.path.append(p)

from medical_diagnosis_model.versions.v2.medical_neural_network_v2 import ClinicalReasoningNetwork
from medical_diagnosis_model.pdf_exporter import PDFExporter


app = FastAPI(title="Medical Diagnosis API", version="0.1.0")
model = ClinicalReasoningNetwork(hidden_neurons=25, learning_rate=0.3, epochs=1000)
MODEL_PATH = os.path.join(MODEL_ROOT, "models", "enhanced_medical_model.json")
exporter = PDFExporter(export_dir=os.path.join(MODEL_ROOT, "exports"))


def _ensure_model_loaded():
    quick_train = os.environ.get("MDM_QUICK_TRAIN") == "1"
    try:
        model.load_model(MODEL_PATH)
    except Exception:
        cases = 5 if quick_train else 50
        model.train(cases_per_disease=cases, verbose=False)
        model.save_model(MODEL_PATH)


@app.on_event("startup")
def load_model():
    _ensure_model_loaded()


class Symptoms(BaseModel):
    data: dict


@app.post("/api/v2/diagnose")
def diagnose(payload: Symptoms):
    if model.network is None:
        _ensure_model_loaded()
    results = model.diagnose_with_reasoning(payload.data)
    return results


class ExportRequest(BaseModel):
    patient_id: str | None = None
    symptoms: dict
    results: dict


@app.post("/api/v2/export")
def export_report(req: ExportRequest):
    patient_info = {"patient_id": req.patient_id or "anonymous"}
    path = exporter.export_diagnosis_to_pdf(patient_info, req.symptoms, req.results)
    return {"path": path}


