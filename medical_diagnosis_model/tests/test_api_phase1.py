import json
import os
from pathlib import Path
from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)
ROOT = Path(__file__).resolve().parent / "phase_1_backend"


def load_cases():
    return json.loads((ROOT / "cases.json").read_text())


def test_phase1_expected_primaries():
    cases = load_cases()
    mismatches = []
    for case in cases:
        name = case["name"]
        symptoms = case["symptoms"]
        expected = case.get("expected_primary")
        headers = {}
        api_key = os.environ.get("MDM_API_KEY")
        if api_key:
            headers["X-API-Key"] = api_key
        resp = client.post("/api/v2/diagnose", json={"data": symptoms}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        primary = (data.get("primary_diagnosis") or {}).get("name")
        if expected and primary != expected:
            mismatches.append((name, primary, expected))
    assert not mismatches, f"Mismatches: {mismatches}"
