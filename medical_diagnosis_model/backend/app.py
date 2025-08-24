from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
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

# CORS (dev-friendly): allow localhost:3000 by default; configurable via env
allowed_origins = os.environ.get("MDM_CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
model = ClinicalReasoningNetwork(hidden_neurons=25, learning_rate=0.3, epochs=1000)
MODEL_PATH = os.path.join(MODEL_ROOT, "models", "enhanced_medical_model.json")
exporter = PDFExporter(export_dir=os.path.join(MODEL_ROOT, "exports"))
_RATE_LIMIT_STORE: dict[str, dict[str, float | int]] = {}


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


# Basic request logging (structured)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    path = request.url.path
    method = request.method
    # Basic rate limiting (dev): requests per window per client IP
    try:
        rpm = int(os.environ.get("MDM_RATE_LIMIT_RPM", "120"))
    except ValueError:
        rpm = 120
    try:
        window_s = int(os.environ.get("MDM_RATE_LIMIT_WINDOW_S", "60"))
    except ValueError:
        window_s = 60

    if rpm > 0 and window_s > 0:
        client_ip = (request.client.host if request.client else "unknown")
        now = time.time()
        rl = _RATE_LIMIT_STORE.get(client_ip)
        if not rl or (now - rl["win_start"]) > window_s:
            rl = {"win_start": now, "count": 0}
        rl["count"] += 1
        _RATE_LIMIT_STORE[client_ip] = rl
        if rl["count"] > rpm:
            return JSONResponse({"detail": "Too Many Requests"}, status_code=429)

    response = await call_next(request)
    try:
        status = response.status_code
    except Exception:
        status = 500
    print(f"api_log method={method} path={path} status={status}")
    return response


class Symptoms(BaseModel):
    data: dict


def _auth_check(x_api_key: str | None):
    required = os.environ.get("MDM_API_KEY")
    if not required:
        return  # auth disabled for local dev if not set
    if not x_api_key or x_api_key != required:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/api/v2/diagnose")
def diagnose(payload: Symptoms, x_api_key: str | None = Header(default=None)):
    _auth_check(x_api_key)
    if model.network is None:
        _ensure_model_loaded()
    results = model.diagnose_with_reasoning(payload.data)
    return results


class ExportRequest(BaseModel):
    patient_id: str | None = None
    symptoms: dict
    results: dict


@app.post("/api/v2/export")
def export_report(req: ExportRequest, x_api_key: str | None = Header(default=None)):
    _auth_check(x_api_key)
    patient_info = {"patient_id": req.patient_id or "anonymous"}
    path = exporter.export_diagnosis_to_pdf(patient_info, req.symptoms, req.results)
    return {"path": path}


