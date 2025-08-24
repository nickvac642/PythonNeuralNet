import os
from fastapi.testclient import TestClient

from medical_diagnosis_model.backend.app import app


def test_adaptive_flow_start_answer_finish(monkeypatch):
    client = TestClient(app)
    monkeypatch.setenv("MDM_API_KEY", "testkey")

    # start
    r = client.post(
        "/api/v2/adaptive/start",
        headers={"X-API-Key": "testkey"},
        json={"prior_answers": {"Fever": 8}},
    )
    assert r.status_code == 200
    data = r.json()
    session_id = data["session_id"]
    # answer (if a question is suggested)
    nq = data.get("next_question")
    if nq:
        r2 = client.post(
            "/api/v2/adaptive/answer",
            headers={"X-API-Key": "testkey"},
            json={"session_id": session_id, "question": nq["symptom_id"], "answer": "no"},
        )
        assert r2.status_code == 200

    # finish
    r3 = client.post(
        "/api/v2/adaptive/finish",
        headers={"X-API-Key": "testkey"},
        json={"session_id": session_id},
    )
    assert r3.status_code == 200
    out = r3.json()
    assert "results" in out

