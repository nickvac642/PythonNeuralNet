from __future__ import annotations

import json
from pathlib import Path


def _setup_paths():
    import sys
    here = Path(__file__).resolve().parents[2]
    # ensure repo root and model root are importable
    repo_root = here.parent
    for p in (str(repo_root), str(here)):
        if p not in sys.path:
            sys.path.append(p)


def test_patient_time_no_leakage(tmp_path):
    _setup_paths()
    from medical_diagnosis_model.backend.data.splitter import patient_time_split

    # Create a small synthetic dataset with patients and times
    rows = []
    for pid in range(10):
        for t in range(3):
            rows.append({
                "patient_id": f"P{pid:02d}",
                "onset_day": t,
                "label_name": "A" if pid % 2 == 0 else "B",
            })

    train, val, test = patient_time_split(rows, ratios=(0.6, 0.2, 0.2), seed=123)

    def pids(split):
        return {r["patient_id"] for r in split}

    # No overlap across splits
    assert pids(train).isdisjoint(pids(val))
    assert pids(train).isdisjoint(pids(test))
    assert pids(val).isdisjoint(pids(test))


def test_stratified_distribution_similarity():
    _setup_paths()
    from medical_diagnosis_model.backend.data.splitter import stratified_split, report_distribution

    # Build a label-imbalanced dataset
    rows = []
    rows += [{"label_name": "A"} for _ in range(80)]
    rows += [{"label_name": "B"} for _ in range(20)]

    train, val, test = stratified_split(rows, ratios=(0.7, 0.15, 0.15), seed=7)

    total_dist = report_distribution(rows)
    train_dist = report_distribution(train)

    # Ratios should roughly match (within 5 absolute count tolerance for this toy set)
    for label, total_count in total_dist.items():
        expected = 0.7 * total_count
        assert abs(train_dist[label] - expected) <= 5


def test_class_weights_inverse_frequency():
    _setup_paths()
    from medical_diagnosis_model.backend.data.splitter import compute_class_weights

    rows = []
    rows += [{"label_name": "A"} for _ in range(90)]
    rows += [{"label_name": "B"} for _ in range(10)]

    w = compute_class_weights(rows)
    assert set(w.keys()) == {"A", "B"}
    # Rarer class should have larger weight
    assert w["B"] > w["A"]
    # Sum of weights is not constrained, but average should be ~1.0 by construction
    avg = (w["A"] + w["B"]) / 2.0
    assert 0.5 <= avg <= 1.5


