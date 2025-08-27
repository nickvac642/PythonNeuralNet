#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def _setup_paths() -> None:
    import sys
    here = Path(__file__).resolve()
    model_root = here.parents[2]  # medical_diagnosis_model/
    repo_root = model_root.parent
    for p in (str(repo_root), str(model_root)):
        if p not in sys.path:
            sys.path.append(p)


def main() -> int:
    _setup_paths()
    from medical_diagnosis_model.backend.data.splitter import (
        load_jsonl,
        stratified_split,
        patient_time_split,
        write_jsonl,
        write_summary,
    )

    ap = argparse.ArgumentParser(description="Split JSONL dataset into train/val/test")
    ap.add_argument("--input", default="medical_diagnosis_model/data/v02/cases_v02.jsonl")
    ap.add_argument("--out", default="medical_diagnosis_model/data/splits/v02")
    ap.add_argument("--patient-key", default="patient_id")
    ap.add_argument("--time-key", default="onset_day")
    ap.add_argument("--label-key", default="label_name")
    ap.add_argument("--ratios", nargs=3, type=float, default=[0.7, 0.15, 0.15])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--strategy", choices=["patient_time", "stratified"], default="patient_time")
    args = ap.parse_args()

    rows = load_jsonl(args.input)
    if args.strategy == "patient_time":
        train, val, test = patient_time_split(
            rows,
            patient_key=args.patient_key,
            time_key=args.time_key,
            label_key=args.label_key,
            ratios=tuple(args.ratios),
            seed=args.seed,
        )
    else:
        train, val, test = stratified_split(
            rows,
            label_key=args.label_key,
            ratios=tuple(args.ratios),
            seed=args.seed,
        )

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(train, out_dir / "train.jsonl")
    write_jsonl(val, out_dir / "val.jsonl")
    write_jsonl(test, out_dir / "test.jsonl")
    write_summary(out_dir, train, val, test, label_key=args.label_key)
    print(f"Wrote splits to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


