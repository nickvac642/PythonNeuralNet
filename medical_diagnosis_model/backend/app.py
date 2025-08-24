from fastapi import FastAPI, Header, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from pydantic import BaseModel
import os
import sys
import uuid
from typing import Dict, List, Tuple

# Ensure foundational_brain is importable
MODEL_ROOT = os.path.dirname(os.path.dirname(__file__))
REPO_ROOT = os.path.dirname(MODEL_ROOT)
for p in (REPO_ROOT, MODEL_ROOT):
    if p not in sys.path:
        sys.path.append(p)

from medical_diagnosis_model.versions.v2.medical_neural_network_v2 import ClinicalReasoningNetwork
from medical_diagnosis_model.pdf_exporter import PDFExporter
from medical_diagnosis_model.backend.security.jwt_dep import verify_bearer
from medical_diagnosis_model.versions.v2.medical_disease_schema_v2 import DISEASES_V2
from medical_diagnosis_model.medical_symptom_schema import SYMPTOMS


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
_ADAPTIVE_SESSIONS: Dict[str, Dict] = {}


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
def diagnose(payload: Symptoms, x_api_key: str | None = Header(default=None), claims: dict = Depends(verify_bearer)):
    # If not in OIDC mode, fall back to API key header
    if os.environ.get("MDM_AUTH_MODE", "api_key").lower() != "oidc":
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
def export_report(req: ExportRequest, x_api_key: str | None = Header(default=None), claims: dict = Depends(verify_bearer)):
    if os.environ.get("MDM_AUTH_MODE", "api_key").lower() == "oidc":
        scopes = (claims.get("scope") or "") if isinstance(claims, dict) else ""
        if "write:export" not in scopes.split():
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        _auth_check(x_api_key)
    patient_info = {"patient_id": req.patient_id or "anonymous"}
    path = exporter.export_diagnosis_to_pdf(patient_info, req.symptoms, req.results)
    return {"path": path}


# ===================== Adaptive (alpha) =====================

class AdaptiveStartRequest(BaseModel):
    prior_answers: dict | None = None  # {"Fever": "yes"|"no"|"unknown"|number}
    threshold: float | None = None     # stop threshold for top-1 prob
    max_questions: int | None = None


class AdaptiveStartResponse(BaseModel):
    session_id: str
    next_question: dict | None = None  # {symptom_id, name}


class AdaptiveAnswerRequest(BaseModel):
    session_id: str
    question: str | int
    answer: str  # yes|no|unknown
    severity: float | None = None  # 0-10 scale (optional)


class AdaptiveAnswerResponse(BaseModel):
    session_id: str
    finished: bool
    next_question: dict | None = None
    results: dict | None = None


def _symptom_id_from_key(key: str | int) -> int | None:
    if isinstance(key, int):
        return key if key in SYMPTOMS else None
    # Try exact name match
    for sid, meta in SYMPTOMS.items():
        if meta.get("name", "").lower() == str(key).lower():
            return sid
    return None


def _answers_to_vectors(answers: Dict[int, dict]) -> tuple[list[int], list[float], list[int]]:
    symptom_vector = [0] * 30
    severity_vector = [0.0] * 30
    present_ids: list[int] = []
    for sid, info in answers.items():
        ans = info.get("answer")
        sev_raw = info.get("severity")
        if ans == "yes":
            symptom_vector[sid] = 1
            present_ids.append(sid)
            if sev_raw is None:
                severity_vector[sid] = 0.6
            else:
                try:
                    severity_vector[sid] = max(0.0, min(float(sev_raw) / 10.0, 1.0))
                except Exception:
                    severity_vector[sid] = 0.6
        elif ans == "no":
            # explicitly absent → keep present=0, severity=0
            continue
        else:
            # unknown → ignore
            continue
    return symptom_vector, severity_vector, present_ids


def _compute_adjusted_probs(symptom_vector: list[int], severity_vector: list[float], present_ids: list[int]) -> list[float]:
    if model.network is None:
        _ensure_model_loaded()
    # Neutral prior when no evidence yet to avoid premature certainty
    if not present_ids:
        n = len(DISEASES_V2)
        adjusted = [1.0 / n] * n
    else:
        features = symptom_vector + severity_vector
        base = model._predict_proba(features)
        adjusted = model._apply_clinical_rules(base, present_ids, severity_vector, has_test_results=None)
    total = sum(adjusted)
    return [p / total for p in adjusted] if total else adjusted


def _entropy(probs: list[float]) -> float:
    import math
    eps = 1e-12
    return -sum(p * math.log(max(p, eps)) for p in probs)


def _select_next_symptom(disease_probs: list[float], asked: set[int]) -> int | None:
    # Build mapping disease_id -> prob
    d_ids = list(DISEASES_V2.keys())
    p_map = {did: disease_probs[did] for did in d_ids}
    h_before = _entropy(list(p_map.values()))
    best_symptom = None
    best_eig = -1.0
    # Precompute per-disease symptom frequencies
    triage_sids = [27, 26, 3, 7, 8, 11]  # Dysuria, Frequency, Cough, Rhinorrhea, Congestion, Diarrhea
    candidate_sids = triage_sids if len(asked) == 0 else list(range(30))
    for sid in candidate_sids:
        if sid in asked:
            continue
        # P(yes|d)
        py_d = {did: DISEASES_V2[did].get("symptom_patterns", {}).get(sid, {}).get("frequency", 0.0) for did in d_ids}
        # Priors for yes/no
        p_yes = sum(p_map[did] * py_d[did] for did in d_ids)
        p_no = 1.0 - p_yes
        if p_yes <= 1e-9 or p_no <= 1e-9:
            eig = 0.0
        else:
            # Posteriors
            post_yes = []
            post_no = []
            for did in d_ids:
                post_yes.append((p_map[did] * py_d[did]) / p_yes)
                post_no.append((p_map[did] * (1.0 - py_d[did])) / p_no)
            h_yes = _entropy(post_yes)
            h_no = _entropy(post_no)
            eig = h_before - (p_yes * h_yes + p_no * h_no)
        if eig > best_eig:
            best_eig = eig
            best_symptom = sid
    return best_symptom


def _session_should_stop(probs: list[float], num_questions: int, threshold: float, max_q: int) -> bool:
    return (max(probs) >= threshold) or (num_questions >= max_q)


def _build_next_question(sid: int | None) -> dict | None:
    if sid is None:
        return None
    meta = SYMPTOMS.get(sid, {})
    return {
        "symptom_id": sid,
        "name": meta.get("name"),
        "medical_term": meta.get("medical_term"),
        "icd_10": meta.get("icd_10"),
    }


@app.post("/api/v2/adaptive/start")
def adaptive_start(req: AdaptiveStartRequest, x_api_key: str | None = Header(default=None), claims: dict = Depends(verify_bearer)):
    if os.environ.get("MDM_AUTH_MODE", "api_key").lower() != "oidc":
        _auth_check(x_api_key)
    # Create session
    session_id = str(uuid.uuid4())
    threshold = req.threshold if req.threshold is not None else float(os.environ.get("MDM_ADAPTIVE_CONFIDENCE", "0.85"))
    max_q = req.max_questions if req.max_questions is not None else int(os.environ.get("MDM_ADAPTIVE_MAX_Q", "10"))
    answers: Dict[int, dict] = {}
    # Seed prior answers
    if req.prior_answers:
        for key, val in req.prior_answers.items():
            sid = _symptom_id_from_key(key)
            if sid is None:
                continue
            if isinstance(val, (int, float)):
                answers[sid] = {"answer": "yes", "severity": float(val)}
            elif isinstance(val, str):
                answers[sid] = {"answer": val.lower(), "severity": None}
    _ADAPTIVE_SESSIONS[session_id] = {
        "answers": answers,
        "threshold": threshold,
        "max_q": max_q,
        "num_q": 0,
    }
    # Compute next question
    sv, sev, present = _answers_to_vectors(answers)
    probs = _compute_adjusted_probs(sv, sev, present)
    sid_next = _select_next_symptom(probs, set(answers.keys()))
    return AdaptiveStartResponse(session_id=session_id, next_question=_build_next_question(sid_next))


@app.post("/api/v2/adaptive/answer")
def adaptive_answer(req: AdaptiveAnswerRequest, x_api_key: str | None = Header(default=None), claims: dict = Depends(verify_bearer)):
    if os.environ.get("MDM_AUTH_MODE", "api_key").lower() != "oidc":
        _auth_check(x_api_key)
    sess = _ADAPTIVE_SESSIONS.get(req.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    sid = _symptom_id_from_key(req.question)
    if sid is None:
        raise HTTPException(status_code=400, detail="Invalid question")
    ans = req.answer.lower()
    if ans not in {"yes", "no", "unknown"}:
        raise HTTPException(status_code=400, detail="Invalid answer")
    sess["answers"][sid] = {"answer": ans, "severity": req.severity}
    sess["num_q"] = int(sess.get("num_q", 0)) + 1
    # Recompute
    sv, sev, present = _answers_to_vectors(sess["answers"]) 
    probs = _compute_adjusted_probs(sv, sev, present)
    if _session_should_stop(probs, sess["num_q"], sess["threshold"], sess["max_q"]):
        # Build diagnosis using current answers (convert to name: severity 0-10)
        symptom_dict = {}
        for sid_k, info in sess["answers"].items():
            if info.get("answer") == "yes":
                name = SYMPTOMS.get(sid_k, {}).get("name")
                if name:
                    val = info.get("severity")
                    symptom_dict[name] = float(val) if val is not None else 6.0
        results = model.diagnose_with_reasoning(symptom_dict)
        return AdaptiveAnswerResponse(session_id=req.session_id, finished=True, next_question=None, results=results)
    # Else ask next
    sid_next = _select_next_symptom(probs, set(sess["answers"].keys()))
    return AdaptiveAnswerResponse(session_id=req.session_id, finished=False, next_question=_build_next_question(sid_next), results=None)


class AdaptiveFinishRequest(BaseModel):
    session_id: str


@app.post("/api/v2/adaptive/finish")
def adaptive_finish(req: AdaptiveFinishRequest, x_api_key: str | None = Header(default=None), claims: dict = Depends(verify_bearer)):
    if os.environ.get("MDM_AUTH_MODE", "api_key").lower() != "oidc":
        _auth_check(x_api_key)
    sess = _ADAPTIVE_SESSIONS.pop(req.session_id, None)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    symptom_dict = {}
    for sid_k, info in sess["answers"].items():
        if info.get("answer") == "yes":
            name = SYMPTOMS.get(sid_k, {}).get("name")
            if name:
                val = info.get("severity")
                symptom_dict[name] = float(val) if val is not None else 6.0
    results = model.diagnose_with_reasoning(symptom_dict)
    return {"session_id": req.session_id, "results": results}

