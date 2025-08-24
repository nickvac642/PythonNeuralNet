#!/usr/bin/env python3
import os, json, time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

API = os.environ.get("API_URL", "http://localhost:8000")


def main():
    cases = json.load(open(ROOT / "cases.json"))
    ts = time.strftime("%Y%m%d_%H%M%S")
    summary = []
    failures = 0
    for case in cases:
        name = case["name"]
        symptoms = case["symptoms"]
        expected = case.get("expected_primary")
        r = requests.post(f"{API}/api/v2/diagnose", json={"data": symptoms})
        status = r.status_code
        try:
            data = r.json()
        except Exception:
            data = {"raw": r.text}
        pd = (data.get("primary_diagnosis") or {})
        primary = pd.get("name")
        line = {
            "case": name,
            "status": status,
            "primary": primary,
            "icd_10": pd.get("icd_10"),
            "confidence": pd.get("confidence"),
            "expected_primary": expected,
            "match": (expected is None or primary == expected)
        }
        if expected and primary != expected:
            failures += 1
        summary.append(line)
        with open(OUT / f"{ts}_{name}.txt", "w") as f:
            f.write(json.dumps({"symptoms": symptoms, "response": data}, indent=2))
        status_str = "OK" if line["match"] else "MISMATCH"
        print(f"{name}: {status} -> {primary} (exp={expected}) conf={line['confidence']} [{status_str}]")
    with open(OUT / f"{ts}_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary: {len(cases)-failures}/{len(cases)} matched expected primaries")


if __name__ == "__main__":
    main()
