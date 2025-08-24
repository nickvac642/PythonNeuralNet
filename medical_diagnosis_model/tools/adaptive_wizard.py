#!/usr/bin/env python3
"""
Interactive adaptive questioning wizard (no server required).

Runs in-process using FastAPI TestClient to call /api/v2/adaptive/* endpoints.
This bypasses API key by unsetting MDM_API_KEY in the local process.
"""
from __future__ import annotations

import os
import sys
from typing import Dict, List, Tuple
import argparse


def _setup_paths() -> None:
    here = os.path.abspath(os.path.dirname(__file__))
    model_root = os.path.dirname(here)
    repo_root = os.path.dirname(model_root)
    for p in (repo_root, model_root):
        if p not in sys.path:
            sys.path.append(p)


def _prompt_seed() -> Dict[str, float]:
    print("Seed prior symptoms (format: Name:Severity,Name:Severity). Example: Fever:8,Cough:6")
    line = input("Prior (or press Enter to skip): ").strip()
    if not line:
        return {}
    seeds: Dict[str, float] = {}
    for part in line.split(','):
        part = part.strip()
        if not part:
            continue
        if ':' not in part:
            print(f"  Skipping '{part}' (expected Name:Severity)")
            continue
        name, val = part.split(':', 1)
        try:
            sev = float(val)
        except Exception:
            print(f"  Skipping '{part}' (severity not a number)")
            continue
        seeds[name.strip()] = max(0.0, min(sev, 10.0))
    return seeds


def main() -> int:
    _setup_paths()
    parser = argparse.ArgumentParser(description="Interactive adaptive questioning wizard")
    parser.add_argument("--debug-k", type=int, default=0, help="Print top-K candidate questions by EIG at each step")
    args = parser.parse_args()
    # Disable API-key auth for local wizard
    os.environ.pop("MDM_API_KEY", None)

    from fastapi.testclient import TestClient
    from backend.app import (
        app,
        _ADAPTIVE_SESSIONS,  # type: ignore
        _answers_to_vectors,  # type: ignore
        _compute_adjusted_probs,  # type: ignore
    )
    from versions.v2.medical_disease_schema_v2 import DISEASES_V2  # type: ignore
    from medical_symptom_schema import SYMPTOMS  # type: ignore

    client = TestClient(app)

    prior = _prompt_seed()
    payload = {"prior_answers": prior} if prior else {}
    r = client.post("/api/v2/adaptive/start", json=payload)
    if r.status_code != 200:
        print("Failed to start adaptive session:", r.status_code, r.text)
        return 1
    data = r.json()
    session_id = data.get("session_id")
    next_q = data.get("next_question")

    print(f"\nSession: {session_id}")
    asked = 0

    def _print_q(q):
        if not q:
            print("No next question (ready to finish).")
            return
        print("\nNext question:")
        print(f"  ID:   {q.get('symptom_id')}")
        print(f"  Name: {q.get('name')}  (ICD-10: {q.get('icd_10')})")

    def _entropy(probs: List[float]) -> float:
        import math
        eps = 1e-12
        return -sum(p * math.log(max(p, eps)) for p in probs)

    def _rank_candidates(session_id: str, k: int = 5) -> Tuple[List[Tuple[int, float, str]], List[Tuple[int, float, str]]]:
        # Collect answers and compute current posterior P(d)
        sess = _ADAPTIVE_SESSIONS.get(session_id) or {}
        answers = sess.get("answers") or {}
        sv, sev, present = _answers_to_vectors(answers)  # type: ignore
        probs = _compute_adjusted_probs(sv, sev, present)  # type: ignore
        d_ids = list(DISEASES_V2.keys())
        p_map = {did: probs[did] for did in d_ids}
        h_before = _entropy(list(p_map.values()))
        asked = set(int(sid) for sid in answers.keys())
        ranked: List[Tuple[int, float, str]] = []
        for sid in range(30):
            if sid in asked:
                continue
            py_d = {did: DISEASES_V2[did].get("symptom_patterns", {}).get(sid, {}).get("frequency", 0.0) for did in d_ids}
            p_yes = sum(p_map[did] * py_d[did] for did in d_ids)
            p_no = 1.0 - p_yes
            if p_yes <= 1e-9 or p_no <= 1e-9:
                eig = 0.0
            else:
                post_yes = [(p_map[did] * py_d[did]) / p_yes for did in d_ids]
                post_no = [(p_map[did] * (1.0 - py_d[did])) / p_no for did in d_ids]
                h_yes = _entropy(post_yes)
                h_no = _entropy(post_no)
                eig = h_before - (p_yes * h_yes + p_no * h_no)
            name = (SYMPTOMS.get(sid, {}) or {}).get("name", str(sid))
            ranked.append((sid, eig, name))
        ranked.sort(key=lambda t: t[1], reverse=True)
        # Also compute top diseases by current posterior
        top_diseases: List[Tuple[int, float, str]] = []
        for did in d_ids:
            top_diseases.append((did, p_map[did], DISEASES_V2[did]["name"]))
        top_diseases.sort(key=lambda t: t[1], reverse=True)
        return ranked[: max(1, k)], top_diseases[:3]

    while True:
        _print_q(next_q)
        if args.debug_k and session_id:
            topk, topd = _rank_candidates(session_id, args.debug_k)
            print("Top diseases (current posterior):")
            for did, p, name in topd:
                print(f"  {name:30s}  P={p:.3f}")
            print("Top candidates by EIG:")
            for sid, eig, name in topk:
                print(f"  {sid:2d}  {name:28s}  EIG={eig:.4f}")
        if not next_q:
            break
        qid = next_q.get("symptom_id")
        ans = input("Answer [y]es/[n]o/[u]nknown (Enter to finish, q to quit): ").strip().lower()
        if ans == "" or ans == "q" or ans == "quit" or ans == "exit":
            break
        if ans not in {"y", "n", "u", "yes", "no", "unknown"}:
            print("  Please answer y/n/u, press Enter to finish, or 'q' to quit.")
            continue
        answer = {"y": "yes", "n": "no", "u": "unknown"}.get(ans, ans)
        sev = None
        if answer == "yes":
            try:
                sval = input("  Severity 0-10 (Enter to skip): ").strip()
                if sval:
                    sev = max(0.0, min(float(sval), 10.0))
            except Exception:
                sev = None

        body = {"session_id": session_id, "question": qid, "answer": answer}
        if sev is not None:
            body["severity"] = sev
        r2 = client.post("/api/v2/adaptive/answer", json=body)
        if r2.status_code != 200:
            print("  Error:", r2.status_code, r2.text)
            break
        A = r2.json()
        if A.get("finished"):
            print("\nReached stop condition.")
            next_q = None
            break
        next_q = A.get("next_question")
        asked += 1

    # Finish and print results
    r3 = client.post("/api/v2/adaptive/finish", json={"session_id": session_id})
    if r3.status_code != 200:
        print("Finish error:", r3.status_code, r3.text)
        return 1
    R = r3.json()
    results = R.get("results") or {}
    pd = (results.get("primary_diagnosis") or {})
    print("\nPrimary diagnosis:")
    print(f"  {pd.get('name')}  (ICD-10: {pd.get('icd_10')})")
    conf = pd.get("confidence")
    if conf is not None:
        print(f"  Confidence: {conf:.3f}")
    print("\nKey reasoning excerpts:")
    cr = results.get("clinical_reasoning") or {}
    for k in (cr.get("key_findings") or [])[:3]:
        print(f"  + {k.get('symptom')}: {k.get('significance')}")
    for inc in (cr.get("inconsistent_features") or [])[:2]:
        print(f"  - {inc.get('symptom')}: {inc.get('significance')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


