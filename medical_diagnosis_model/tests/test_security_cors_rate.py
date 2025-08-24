import os
from fastapi.testclient import TestClient

from medical_diagnosis_model.backend.app import app, _RATE_LIMIT_STORE


def test_cors_preflight_allows_localhost_3000():
    client = TestClient(app)
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
    }
    r = client.options("/api/v2/diagnose", headers=headers)
    assert r.status_code in (200, 204)
    # Header may vary case; TestClient lowercases internally
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_api_key_auth_enforced_and_allows_valid_key(monkeypatch):
    client = TestClient(app)
    monkeypatch.setenv("MDM_API_KEY", "testkey")

    resp = client.post("/api/v2/diagnose", json={"data": {"Fever": 8}})
    assert resp.status_code == 401

    resp = client.post(
        "/api/v2/diagnose",
        headers={"X-API-Key": "wrong"},
        json={"data": {"Fever": 8}},
    )
    assert resp.status_code == 401

    resp = client.post(
        "/api/v2/diagnose",
        headers={"X-API-Key": "testkey"},
        json={"data": {"Fever": 8}},
    )
    assert resp.status_code == 200


def test_rate_limiting_triggers_429(monkeypatch):
    client = TestClient(app)
    monkeypatch.setenv("MDM_API_KEY", "testkey")
    monkeypatch.setenv("MDM_RATE_LIMIT_RPM", "5")
    monkeypatch.setenv("MDM_RATE_LIMIT_WINDOW_S", "60")
    _RATE_LIMIT_STORE.clear()

    url = "/api/v2/diagnose"
    headers = {"X-API-Key": "testkey"}
    ok = 0
    over = 0
    for _ in range(8):
        r = client.post(url, headers=headers, json={"data": {"Fever": 8}})
        if r.status_code == 200:
            ok += 1
        elif r.status_code == 429:
            over += 1
    assert over >= 1

