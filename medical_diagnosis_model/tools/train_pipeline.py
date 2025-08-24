#!/usr/bin/env python3
"""
One-shot training pipeline:
 - Generate v0.2 balanced dataset (explicit negatives)
 - Train v2 from JSONL
 - Calibrate and save model to models/enhanced_medical_model_v02.json
 - Optionally run a quick confusion summary on held-out set (counts only)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _setup_paths() -> None:
    import os, sys
    here = Path(__file__).resolve().parent
    model_root = here.parent
    repo_root = model_root.parent
    for p in (str(repo_root), str(model_root)):
        if p not in sys.path:
            sys.path.append(p)


def generate_dataset(per_disease: int) -> Path:
    from data.generate_v02 import generate_balanced
    root = Path(__file__).resolve().parents[1]
    out = root / "data" / "v02"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "cases_v02.jsonl"
    data = generate_balanced(per_disease=per_disease)
    with path.open("w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row) + "\n")
    return path


def train_model(jsonl_path: Path, epochs: int) -> Path:
    from versions.v2.medical_neural_network_v2 import ClinicalReasoningNetwork
    m = ClinicalReasoningNetwork(hidden_neurons=25, learning_rate=0.3, epochs=epochs)
    m.train_from_jsonl(str(jsonl_path), verbose=False)
    out = Path(__file__).resolve().parents[1] / "models" / "enhanced_medical_model_v02.json"
    m.save_model(str(out))
    return out


def main() -> int:
    _setup_paths()
    ap = argparse.ArgumentParser(description="Train v0.2 model from generated data")
    ap.add_argument("--per-disease", type=int, default=200)
    ap.add_argument("--epochs", type=int, default=5000)
    args = ap.parse_args()

    jsonl = generate_dataset(args.per_disease)
    print(f"Generated dataset: {jsonl}")
    model_path = train_model(jsonl, args.epochs)
    print(f"Saved model: {model_path}")
    print("Set MDM_MODEL_PATH to use this model in the API if not picked by default.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


