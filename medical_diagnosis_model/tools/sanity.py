#!/usr/bin/env python3
"""
Modular sanity CLI for the medical diagnosis model.

Subcommands (composable):
  - data: validate JSONL datasets against schema
  - tests: run unit tests (pytest) for API and selector
  - api: smoke test /api/v2/diagnose endpoint
  - export: call /api/v2/export using prior diagnose results
  - rate: probe rate limiting behavior
  - adaptive: exercise /api/v2/adaptive/* flow (start → answer → finish)
  - suite: orchestrate data + tests (+ optional api/export/rate)

Notes:
  - API tests require the FastAPI server to be running, or pass --auto-start to spawn uvicorn.
  - Defaults target http://localhost:8000; configure with --url.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import requests


ROOT = Path(__file__).resolve().parents[2]  # repo root
MODEL_ROOT = ROOT / "medical_diagnosis_model"


def _run(cmd: list[str], env: Optional[dict] = None, check: bool = True) -> int:
    print("$", " ".join(cmd))
    proc = subprocess.run(cmd, env=env)
    if check and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.returncode


def cmd_data(args: argparse.Namespace) -> None:
    schema = MODEL_ROOT / "data" / "case.schema.json"
    samples = getattr(args, "paths", None) or [str(MODEL_ROOT / "data" / "samples" / "cases_v0.1.jsonl")]
    py = sys.executable
    _run([py, str(MODEL_ROOT / "data" / "validate_cases.py"), *samples])


def cmd_tests(args: argparse.Namespace) -> None:
    pyenv = os.environ.copy()
    pyenv["PYTHONPATH"] = f"{ROOT}:{MODEL_ROOT}"
    pyenv.setdefault("MDM_QUICK_TRAIN", "1")
    # Ensure unit tests don't require API key or OIDC bearer
    pyenv.pop("MDM_API_KEY", None)
    pyenv.pop("MDM_AUTH_MODE", None)
    py = sys.executable
    tests = [
        str(MODEL_ROOT / "tests" / "test_api_phase1.py"),
        str(MODEL_ROOT / "tests" / "test_selector.py"),
    ]
    _run([py, "-m", "pytest", "-q", *tests], env=pyenv)


def _wait_for(url: str, timeout_s: int = 30) -> None:
    deadline = time.time() + timeout_s
    last_err = None
    while time.time() < deadline:
        try:
            requests.get(url, timeout=2)
            return
        except Exception as e:
            last_err = e
            time.sleep(0.5)
    raise RuntimeError(f"Service not ready at {url}: {last_err}")


def _start_server(args: argparse.Namespace) -> tuple[Optional[subprocess.Popen], str]:
    if not args.auto_start:
        return None, args.url
    env = os.environ.copy()
    env.setdefault("MDM_QUICK_TRAIN", "1")
    if args.api_key:
        env.setdefault("MDM_API_KEY", args.api_key)
    # silence access logs for brevity
    py = sys.executable
    cmd = [
        py, "-m", "uvicorn", "medical_diagnosis_model.backend.app:app",
        "--port", str(args.port), "--log-level", "warning"
    ]
    proc = subprocess.Popen(cmd, env=env, cwd=str(ROOT))
    try:
        _wait_for(f"http://localhost:{args.port}/docs", timeout_s=60)
    except Exception:
        try:
            proc.terminate()
        finally:
            proc.wait(timeout=5)
        raise
    return proc, f"http://localhost:{args.port}"


def _stop_server(proc: Optional[subprocess.Popen]) -> None:
    if not proc:
        return
    try:
        proc.send_signal(signal.SIGINT)
        proc.wait(timeout=10)
    except Exception:
        proc.kill()


def cmd_api(args: argparse.Namespace) -> None:
    proc, base = _start_server(args)
    try:
        url = f"{base}/api/v2/diagnose"
        headers = {"Content-Type": "application/json"}
        if args.api_key:
            headers["X-API-Key"] = args.api_key
        payload = {"data": {"Fever": 8, "Cough": 6}}
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        print("status:", r.status_code)
        print("body:", json.dumps(r.json(), indent=2))
        if r.status_code != 200:
            raise SystemExit(1)
    finally:
        _stop_server(proc)


def cmd_export(args: argparse.Namespace) -> None:
    proc, base = _start_server(args)
    try:
        h = {"Content-Type": "application/json"}
        if args.api_key:
            h["X-API-Key"] = args.api_key
        # 1) diagnose
        d_url = f"{base}/api/v2/diagnose"
        data = {"data": {"Fever": 8, "Cough": 6}}
        dr = requests.post(d_url, headers=h, json=data, timeout=10)
        dr.raise_for_status()
        results = dr.json()
        # 2) export
        e_url = f"{base}/api/v2/export"
        ex_payload = {"patient_id": "sanity", "symptoms": data["data"], "results": results}
        er = requests.post(e_url, headers=h, json=ex_payload, timeout=20)
        print("status:", er.status_code)
        print("body:", er.text)
        er.raise_for_status()
        path = er.json().get("path")
        if not path or not Path(path).exists():
            print("Export path missing or not found:", path)
            raise SystemExit(1)
    finally:
        _stop_server(proc)


def cmd_rate(args: argparse.Namespace) -> None:
    proc, base = _start_server(args)
    try:
        h = {"Content-Type": "application/json"}
        if args.api_key:
            h["X-API-Key"] = args.api_key
        url = f"{base}/api/v2/diagnose"
        ok = 0
        over = 0
        count = getattr(args, "count", 140)
        for i in range(count):
            r = requests.post(url, headers=h, json={"data": {"Fever": 8}}, timeout=10)
            if r.status_code == 200:
                ok += 1
            elif r.status_code == 429:
                over += 1
            else:
                print("Unexpected status:", r.status_code)
        print(f"OK={ok} OVER_LIMIT={over}")
        expect_over = bool(getattr(args, "expect_over_limit", False))
        if expect_over and over == 0:
            raise SystemExit(1)
    finally:
        _stop_server(proc)


def cmd_adaptive(args: argparse.Namespace) -> None:
    proc, base = _start_server(args)
    try:
        h = {"Content-Type": "application/json"}
        if args.api_key:
            h["X-API-Key"] = args.api_key
        # Start session with a hint
        start = requests.post(f"{base}/api/v2/adaptive/start", headers=h, json={"prior_answers": {"Fever": 8}}, timeout=10)
        start.raise_for_status()
        session = start.json()["session_id"]
        next_q = start.json().get("next_question")
        # Answer one question if provided
        if next_q:
            qid = next_q["symptom_id"]
            ans = requests.post(f"{base}/api/v2/adaptive/answer", headers=h, json={
                "session_id": session,
                "question": qid,
                "answer": "no"
            }, timeout=10)
            ans.raise_for_status()
        # Finish session
        fin = requests.post(f"{base}/api/v2/adaptive/finish", headers=h, json={"session_id": session}, timeout=10)
        fin.raise_for_status()
        print("adaptive finished status:", fin.status_code)
    finally:
        _stop_server(proc)


def cmd_suite(args: argparse.Namespace) -> None:
    # Always run data + tests
    cmd_data(args)
    cmd_tests(args)
    # Optionally run API-related checks
    if args.with_api:
        cmd_api(args)
    if args.with_export:
        cmd_export(args)
    if args.with_rate:
        cmd_rate(args)
    if args.with_adaptive:
        cmd_adaptive(args)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Sanity CLI for medical model v2")
    sub = p.add_subparsers(dest="cmd", required=True)

    # Shared options for API-related commands
    def add_api_opts(sp):
        sp.add_argument("--url", default="http://localhost:8000", help="Base API URL")
        sp.add_argument("--api-key", default=os.environ.get("MDM_API_KEY", None))
        sp.add_argument("--auto-start", action="store_true", help="Auto-start uvicorn for this check")
        sp.add_argument("--port", type=int, default=8000)

    sp_data = sub.add_parser("data", help="Validate datasets against schema")
    sp_data.add_argument("paths", nargs="*", help="JSONL files to validate (defaults to samples)")
    sp_data.set_defaults(func=cmd_data)

    sp_tests = sub.add_parser("tests", help="Run unit tests (pytest)")
    sp_tests.set_defaults(func=cmd_tests)

    sp_api = sub.add_parser("api", help="Smoke test /diagnose endpoint")
    add_api_opts(sp_api)
    sp_api.set_defaults(func=cmd_api)

    sp_export = sub.add_parser("export", help="End-to-end export (diagnose + export)")
    add_api_opts(sp_export)
    sp_export.set_defaults(func=cmd_export)

    sp_rate = sub.add_parser("rate", help="Rate-limit probe against /diagnose")
    add_api_opts(sp_rate)
    sp_rate.add_argument("--count", type=int, default=140)
    sp_rate.add_argument("--expect-over-limit", action="store_true")
    sp_rate.set_defaults(func=cmd_rate)

    sp_adapt = sub.add_parser("adaptive", help="Exercise adaptive start/answer/finish flow")
    add_api_opts(sp_adapt)
    sp_adapt.set_defaults(func=cmd_adaptive)

    sp_suite = sub.add_parser("suite", help="Run a suite: data + tests + optional API checks")
    add_api_opts(sp_suite)
    sp_suite.add_argument("--with-api", action="store_true")
    sp_suite.add_argument("--with-export", action="store_true")
    sp_suite.add_argument("--with-rate", action="store_true")
    sp_suite.add_argument("--with-adaptive", action="store_true")
    sp_suite.set_defaults(func=cmd_suite)

    return p


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


