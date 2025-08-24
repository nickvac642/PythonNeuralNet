#!/usr/bin/env python3
"""
Unified runner for the Medical Diagnosis Model

- Dynamically discovers versions under ./versions/
- Presents run targets (interactive systems, demos) with descriptions
- Offers utilities (clean model, clean outputs)

Usage:
  python run.py
"""

from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VERSIONS_DIR = ROOT / "versions"


DESCRIPTION_HINTS = {
    # v2
    "enhanced_medical_system.py": "Full interactive system (Clinical Reasoning)",
    "demo_clinical_reasoning.py": "Clinical reasoning demo (non-interactive)",
    "medical_neural_network_v2.py": "Model v2 self-test (module main)",
    # v1
    "quick_medical_demo.py": "Quick 7-symptom flow (Legacy v1)",
    "interactive_medical_diagnosis.py": "Full interactive flow (Legacy v1)",
    "demo_all_features.py": "All features demo (Legacy v1)",
    "demo_interface_example.py": "Interface example (Legacy v1)",
    "medical_diagnosis_example.py": "Simple diagnosis example (Legacy v1)",
    "medical_neural_network.py": "Model v1 self-test (module main)",
}


def ensure_notice():
    if os.environ.get("VIRTUAL_ENV") is None:
        print("[notice] No virtual environment detected. For best results run:\n"
              "         python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt\n")


def discover_targets() -> list[dict]:
    targets = []
    if not VERSIONS_DIR.exists():
        return targets
    for version_dir in sorted([p for p in VERSIONS_DIR.iterdir() if p.is_dir()]):
        version = version_dir.name
        # scan for python entry scripts in this version
        for py in sorted(version_dir.glob("*.py")):
            name = py.name
            # skip private/internal
            if name.startswith("_"):
                continue
            desc = DESCRIPTION_HINTS.get(name, f"Run {name}")
            targets.append({
                "version": version,
                "path": py,
                "name": name,
                "desc": desc,
            })
    return targets


def utility_targets() -> list[dict]:
    return [
        {
            "version": "utils",
            "path": None,
            "name": "clean_model",
            "desc": "Delete saved model (models/enhanced_medical_model.json)",
        },
        {
            "version": "utils",
            "path": None,
            "name": "clean_outputs",
            "desc": "Purge exports/, diagnosis_history/, data/, models/",
        },
        {
            "version": "utils",
            "path": None,
            "name": "rescan",
            "desc": "Rescan versions and refresh menu",
        },
        {
            "version": "utils",
            "path": None,
            "name": "quit",
            "desc": "Exit",
        },
    ]


def print_menu(targets: list[dict]):
    print("\n=== Medical Diagnosis Model Runner ===\n")
    print("Select a target to run:\n")
    for idx, t in enumerate(targets, 1):
        print(f" {idx:2d}) [{t['version']}] {t['desc']}")
    print("")


def run_target(t: dict):
    if t["version"] == "utils":
        name = t["name"]
        if name == "clean_model":
            model = ROOT / "models" / "enhanced_medical_model.json"
            if model.exists():
                model.unlink()
                print(f"✓ Removed {model}")
            else:
                print("(no model to remove)")
        elif name == "clean_outputs":
            for d in ["exports", "diagnosis_history", "data", "models"]:
                p = ROOT / d
                if p.exists():
                    for child in p.iterdir():
                        try:
                            if child.is_dir():
                                import shutil
                                shutil.rmtree(child)
                            else:
                                child.unlink()
                        except Exception as e:
                            print(f"! Failed to remove {child}: {e}")
                    print(f"✓ Cleared {p}")
                else:
                    print(f"(missing {p}, skipped)")
        elif name == "rescan":
            return "rescan"
        elif name == "quit":
            sys.exit(0)
        return None

    # Run a python target
    cmd = [sys.executable, str(t["path"])]
    print(f"\n→ Running: {' '.join(cmd)}\n")
    try:
        env = os.environ.copy()
        # Ensure imports can resolve shared modules at model root and foundational_brain
        repo_root = ROOT.parent
        paths = [str(ROOT), str(repo_root)]
        existing = env.get("PYTHONPATH") or ""
        env["PYTHONPATH"] = os.pathsep.join([p for p in paths + ([existing] if existing else []) if p])
        subprocess.run(cmd, cwd=ROOT, check=False, env=env)
    except KeyboardInterrupt:
        pass
    return None


def main():
    ensure_notice()
    while True:
        discovered = discover_targets()
        # Put utils at the end
        targets = discovered + utility_targets()
        print_menu(targets)
        choice = input("Enter number: ").strip()
        try:
            idx = int(choice)
            if idx < 1 or idx > len(targets):
                raise ValueError
        except ValueError:
            print("Please enter a valid number.\n")
            continue
        result = run_target(targets[idx - 1])
        if result == "rescan":
            continue
        # pause before showing menu again
        input("\nPress Enter to return to menu...")


if __name__ == "__main__":
    main()


