#!/usr/bin/env python3
"""
Generate v0.2 balanced JSONL training data with explicit negative evidence.

Format per line:
  {
    "symptoms": {"Cough": 6, "Runny Nose": 5, ...},
    "label_name": "Viral Upper Respiratory Infection"
  }
"""
from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Dict, Tuple, List


def _load_schema():
    # Resolve imports locally
    import sys
    here = Path(__file__).resolve().parent
    model_root = here.parent
    repo_root = model_root.parent
    for p in (str(repo_root), str(model_root)):
        if p not in sys.path:
            sys.path.append(p)
    from versions.v2.medical_disease_schema_v2 import DISEASES_V2
    from medical_symptom_schema import SYMPTOMS
    return DISEASES_V2, SYMPTOMS


def _sample_case(disease_id: int, diseases: dict, symptoms: dict, explicit_neg: bool) -> Tuple[Dict[str, float], str]:
    dis = diseases[disease_id]
    name = dis["name"]
    pats = dis.get("symptom_patterns", {})
    out: Dict[str, float] = {}
    # Positive sampling from patterns
    for sid, pat in pats.items():
        if sid not in symptoms:
            continue
        freq = pat.get("frequency", 0.0)
        sev_lo, sev_hi = pat.get("severity_range", (0.2, 0.6))
        if random.random() < freq:
            sev = random.uniform(sev_lo, sev_hi)
            out[symptoms[sid]["name"]] = round(min(max(sev * 10.0, 0.0), 10.0), 1)

    # Mild/early tweak: 30% chance reduce severities
    if random.random() < 0.3:
        for k in list(out.keys()):
            out[k] = round(out[k] * random.uniform(0.5, 0.8), 1)

    # Explicit negatives across syndromes
    if explicit_neg:
        # For respiratory: ensure GU keys absent; for GU: reduce respiratory signals
        if name in ("Viral Upper Respiratory Infection", "Influenza-like Illness", "COVID-19-like Illness", "Viral Syndrome", "Pneumonia Syndrome"):
            for sid in (26, 27):  # Frequency, Dysuria
                out.setdefault(symptoms[sid]["name"], 0.0)
        if name == "Urinary Tract Infection":
            for sid in (3, 7, 8):  # Cough, Rhinorrhea, Congestion
                out.setdefault(symptoms[sid]["name"], 0.0)

    return out, name


def generate_balanced(per_disease: int = 200, seed: int = 42) -> List[Dict]:
    random.seed(seed)
    DISEASES_V2, SYMPTOMS = _load_schema()
    # Focus set: common respiratory + GU UTI
    target_names = {
        "Viral Upper Respiratory Infection",
        "Influenza-like Illness",
        "COVID-19-like Illness",
        "Viral Syndrome",
        "Urinary Tract Infection",
    }
    target_ids = [did for did, d in DISEASES_V2.items() if d["name"] in target_names]
    data: List[Dict] = []
    for did in target_ids:
        for _ in range(per_disease):
            s, label = _sample_case(did, DISEASES_V2, SYMPTOMS, explicit_neg=True)
            data.append({"symptoms": s, "label_name": label})
    random.shuffle(data)
    return data


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "data" / "v02"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "cases_v02.jsonl"
    data = generate_balanced(per_disease=150)
    with path.open("w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row) + "\n")
    print(f"Wrote {len(data)} cases to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


