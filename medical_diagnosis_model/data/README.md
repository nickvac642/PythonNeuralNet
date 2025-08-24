Data directory

Structure:

- case.schema.json: JSON Schema for a single clinical case (v2)
- dictionaries/: canonical symptom and disease dictionaries
- samples/: small hand-made sample dataset for quick validation

Conventions:

- All datasets are JSONL (one JSON object per line)
- Use UTC ISO8601 timestamps
- Version datasets with a semantic version in the filename, e.g., cases_v0.1.jsonl
