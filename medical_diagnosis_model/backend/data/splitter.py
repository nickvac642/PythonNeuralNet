from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def load_jsonl(path: str | Path) -> List[Dict]:
    rows: List[Dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def report_distribution(rows: List[Dict], label_key: str = "label_name") -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for r in rows:
        lbl = r.get(label_key)
        if lbl is None:
            continue
        counts[lbl] = counts.get(lbl, 0) + 1
    return counts


def compute_class_weights(rows: List[Dict], label_key: str = "label_name") -> Dict[str, float]:
    counts = Counter(r.get(label_key) for r in rows if r.get(label_key) is not None)
    counts = {k: v for k, v in counts.items() if k is not None}
    if not counts:
        return {}
    total_classes = len(counts)
    total_samples = sum(counts.values())
    # Raw inverse-frequency weights
    raw: Dict[str, float] = {}
    for cls, cnt in counts.items():
        raw[cls] = 0.0 if cnt == 0 else (total_samples / (total_classes * cnt))
    # Normalize so mean weight across classes is 1.0
    avg = sum(raw.values()) / max(1, total_classes)
    if avg <= 0:
        return raw
    weights: Dict[str, float] = {cls: w / avg for cls, w in raw.items()}
    return weights


def stratified_split(
    rows: List[Dict],
    label_key: str = "label_name",
    ratios: Tuple[float, float, float] = (0.7, 0.15, 0.15),
    seed: int = 42,
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    random.seed(seed)
    by_label: Dict[str, List[Dict]] = defaultdict(list)
    for r in rows:
        lbl = r.get(label_key)
        if lbl is None:
            continue
        by_label[lbl].append(r)
    train: List[Dict] = []
    val: List[Dict] = []
    test: List[Dict] = []
    for lbl, items in by_label.items():
        random.shuffle(items)
        n = len(items)
        n_train = int(ratios[0] * n)
        n_val = int(ratios[1] * n)
        train.extend(items[:n_train])
        val.extend(items[n_train:n_train + n_val])
        test.extend(items[n_train + n_val:])
    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(test)
    return train, val, test


def patient_time_split(
    rows: List[Dict],
    patient_key: str = "patient_id",
    time_key: str = "onset_day",
    label_key: str = "label_name",
    ratios: Tuple[float, float, float] = (0.7, 0.15, 0.15),
    seed: int = 42,
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Group by patient, sort by time, and assign entire patients to splits to avoid leakage.
    If patient/time fields are missing for many rows, fall back to stratified.
    """
    random.seed(seed)
    have_keys = [r for r in rows if patient_key in r and time_key in r]
    if len(have_keys) < int(0.8 * len(rows)):
        # Fallback to stratified split if insufficient metadata
        return stratified_split(rows, label_key=label_key, ratios=ratios, seed=seed)

    # Bucket rows by patient
    by_patient: Dict[str, List[Dict]] = defaultdict(list)
    for r in have_keys:
        by_patient[str(r[patient_key])].append(r)
    patients = list(by_patient.keys())
    random.shuffle(patients)

    n_pat = len(patients)
    n_train = int(ratios[0] * n_pat)
    n_val = int(ratios[1] * n_pat)
    train_pat = set(patients[:n_train])
    val_pat = set(patients[n_train:n_train + n_val])
    test_pat = set(patients[n_train + n_val:])

    train: List[Dict] = []
    val: List[Dict] = []
    test: List[Dict] = []

    for pid, items in by_patient.items():
        # Sort by time within patient for potential future temporal analyses
        items_sorted = sorted(items, key=lambda r: r.get(time_key, 0))
        if pid in train_pat:
            train.extend(items_sorted)
        elif pid in val_pat:
            val.extend(items_sorted)
        else:
            test.extend(items_sorted)

    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(test)
    return train, val, test


def write_jsonl(rows: List[Dict], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def write_summary(
    out_dir: str | Path,
    train: List[Dict],
    val: List[Dict],
    test: List[Dict],
    label_key: str = "label_name",
) -> None:
    out_dir = Path(out_dir)
    summary = {
        "counts": {
            "train": len(train),
            "val": len(val),
            "test": len(test),
        },
        "distribution": {
            "train": report_distribution(train, label_key),
            "val": report_distribution(val, label_key),
            "test": report_distribution(test, label_key),
        },
        "class_weights": compute_class_weights(train, label_key),
    }
    with (out_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


