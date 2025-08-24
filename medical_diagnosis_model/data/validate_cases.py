import json
import sys
from pathlib import Path

try:
    import jsonschema  # type: ignore
except Exception as exc:
    print("jsonschema is required. Try: pip install jsonschema", file=sys.stderr)
    raise


def load_schema(schema_path: Path) -> dict:
    with schema_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_jsonl(jsonl_path: Path):
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield line_num, json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON at line {line_num}: {e}")


def validate_file(schema: dict, jsonl_path: Path) -> int:
    validator = jsonschema.Draft202012Validator(schema)
    errors = 0
    for line_num, obj in iter_jsonl(jsonl_path):
        for err in validator.iter_errors(obj):
            errors += 1
            print(f"{jsonl_path.name}:{line_num}: {err.message}")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python data/validate_cases.py data/samples/cases_v0.1.jsonl", file=sys.stderr)
        return 2
    root = Path(__file__).resolve().parents[1]
    schema_path = root / "data" / "case.schema.json"
    schema = load_schema(schema_path)
    total_errors = 0
    for path_str in argv[1:]:
        path = Path(path_str)
        total_errors += validate_file(schema, path)
    if total_errors == 0:
        print("Validation passed: 0 errors")
        return 0
    print(f"Validation failed: {total_errors} error(s)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))


