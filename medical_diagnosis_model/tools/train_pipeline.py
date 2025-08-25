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


def evaluate_model(jsonl_path: Path, model_path: Path, report_path: Path) -> None:
    """Compute a small confusion matrix and ECE (top-1) on the dataset."""
    from versions.v2.medical_neural_network_v2 import ClinicalReasoningNetwork, DISEASES_V2, get_symptom_by_name
    import json
    # Load dataset
    rows = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    # Build vectors
    def vec(row):
        sym = row.get("symptoms", {})
        symptom_vector = [0] * 30
        severity_vector = [0.0] * 30
        for name, sev in sym.items():
            sid, _ = get_symptom_by_name(name)
            if sid is None or sid >= 30:
                continue
            try:
                sevn = float(sev) / 10.0
            except Exception:
                sevn = 0.0
            if sevn > 0.0:
                symptom_vector[sid] = 1
                severity_vector[sid] = sevn
        return symptom_vector, severity_vector
    # Model
    m = ClinicalReasoningNetwork()
    m.load_model(str(model_path))
    # Metrics containers
    labels = {did: d["name"] for did, d in DISEASES_V2.items()}
    cm = {labels[i]: {labels[j]: 0 for j in labels} for i in labels}
    n = 0
    correct = 0
    # ECE bins
    B = 10
    bins = [
        {"low": b / B, "high": (b + 1) / B, "confs": [], "accs": []}
        for b in range(B)
    ]
    for row in rows:
        true_name = row.get("label_name")
        if true_name is None:
            continue
        s, sev = vec(row)
        probs = m._predict_proba(s + sev)
        pred_id = max(range(len(probs)), key=lambda i: probs[i])
        pred_name = labels.get(pred_id, str(pred_id))
        cm[true_name][pred_name] = cm.get(true_name, {}).get(pred_name, 0) + 1
        n += 1
        top_conf = probs[pred_id]
        match = int(pred_name == true_name)
        if pred_name == true_name:
            correct += 1
        # ECE binning
        for b in bins:
            if b["low"] <= top_conf < b["high"] or (top_conf == 1.0 and b["high"] == 1.0):
                b["confs"].append(top_conf)
                b["accs"].append(match)
                break
    # Compute stats
    acc = correct / max(1, n)
    ece = 0.0
    for b in bins:
        if not b["confs"]:
            b["mean_conf"] = None
            b["mean_acc"] = None
            continue
        mean_conf = sum(b["confs"]) / len(b["confs"])
        mean_acc = sum(b["accs"]) / len(b["accs"])
        b["mean_conf"] = mean_conf
        b["mean_acc"] = mean_acc
        ece += (len(b["confs"]) / n) * abs(mean_conf - mean_acc)
    # Write report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump({"accuracy": acc, "ece": ece, "confusion": cm, "bins": bins}, f, indent=2)
    # Pretty print confusion and reliability to console (Rich if available)
    try:
        from rich.table import Table
        from rich.console import Console
        console = Console()
        # Confusion matrix (compact)
        ordered = list(cm.keys())
        tbl = Table(title="Confusion Matrix (counts)")
        tbl.add_column("True/Pred")
        for p in ordered:
            tbl.add_column(p, justify="right")
        for t in ordered:
            row = [t] + [str(cm[t].get(p, 0)) for p in ordered]
            tbl.add_row(*row)
        console.print(tbl)
        # Reliability / ECE bins
        bt = Table(title=f"Reliability Bins (ECE={ece:.3f}, Acc={acc:.3f})")
        bt.add_column("Bin")
        bt.add_column("Mean Conf")
        bt.add_column("Mean Acc")
        bt.add_column("N")
        bt.add_column("Bar")
        for b in bins:
            n_b = len(b["confs"]) if b["confs"] else 0
            mc = b.get("mean_conf")
            ma = b.get("mean_acc")
            mc_s = f"{mc:.2f}" if mc is not None else "-"
            ma_s = f"{ma:.2f}" if ma is not None else "-"
            # simple ascii bars
            bar_c = "█" * int((mc or 0) * 20)
            bar_a = "░" * int((ma or 0) * 20)
            bt.add_row(f"{b['low']:.1f}-{b['high']:.1f}", mc_s, ma_s, str(n_b), f"{bar_c}\n{bar_a}")
        console.print(bt)
    except Exception:
        print(f"Accuracy={acc:.3f}  ECE={ece:.3f}")


def main() -> int:
    _setup_paths()
    ap = argparse.ArgumentParser(description="Train v0.2 model from generated data")
    ap.add_argument("--per-disease", type=int, default=200)
    ap.add_argument("--epochs", type=int, default=5000)
    ap.add_argument("--jsonl", default=None, help="Use existing JSONL instead of generating")
    ap.add_argument("--use-existing-model", default=None, help="Skip training and evaluate this model path")
    ap.add_argument("--report", default="medical_diagnosis_model/reports/metrics_v02.json")
    args = ap.parse_args()

    # Dataset
    if args.jsonl:
        jsonl = Path(args.jsonl)
    else:
        jsonl = generate_dataset(args.per_disease)
        print(f"Generated dataset: {jsonl}")
    # Train or reuse model
    if args.use_existing_model:
        model_path = Path(args.use_existing_model)
        print(f"Using existing model: {model_path}")
    else:
        model_path = train_model(jsonl, args.epochs)
        print(f"Saved model: {model_path}")
    # Evaluate and write report
    report_path = Path(args.report)
    evaluate_model(jsonl, model_path, report_path)
    print(f"Wrote metrics to {report_path}")
    print("Set MDM_MODEL_PATH to use this model in the API if not picked by default.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


