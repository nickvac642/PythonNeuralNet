# Next Steps: From Prototype to Real‑Data Medical Model

Use this as a checklist to evolve v2 into a clinically useful, data‑driven system.

## Immediate (week 1–2)

- Define schema mapping
  - Single source of truth for: symptoms (IDs/labels), vitals (units/ranges), labs (normalization), demographics, context (season/exposure), unknown/NA encoding.
- Label policy
  - For each disease: criteria for “confirmed” (ICD‑10 + test) vs “presumptive”; clinician adjudication rules.
- PHI‑safe ingestion scaffolding
  - De‑identify; normalize units; provenance/audit logging; no raw PHI on disk.

## Foundation upgrades (week 2–3)

- Splits & imbalance
  - Patient‑level train/val/test split (no leakage); stratify; add class weights or weighted sampling.
- Training
  - Switch to Adam; add L2 weight decay; optional dropout in hidden layer; expose via config.
- Metrics & calibration
  - AUROC, AUPRC, F1, Top‑k, confusion per class.
  - Reliability diagrams + ECE; re‑tune temperature on held‑out set; subgroup calibration.

## Clinical fit (week 3–4)

- Rules expansion
  - Centor (with age), CURB‑65, seasonality priors, exposure risks; test‑gating suggestions.
- Safety rails
  - Red‑flag escalation list; conservative defaults on missing/conflicting data; “need more info” branch.

## Ops & tooling (parallel)

- Experiment tracking & configs
  - YAML configs, fixed seeds, run logs; simple experiment registry.
- Batch CLI
  - Score CSV/JSONL → outputs with predictions, differentials, confidence, flags.
- Docs & tests
  - Data dictionary (fields, ranges, encodings); update legal/privacy notes.
  - Unit tests for rules and pipeline; lightweight CI (lint + tests).

### Optional: Retrieval‑Augmented Generation (RAG)

- Purpose: supplement deterministic rules with up‑to‑date clinical context (guidelines, pathways, medication interactions) without hard‑coding everything.
- Where it fits: post‑prediction explanation and test suggestions.
  - Input: symptoms + top‑k differential + key findings
  - Retrieval: semantic search over curated clinical notes/guidelines (local vector store)
  - Generation: small prompt to produce “why” and “next steps” text; never overwrite the model’s probabilities, only annotate.
- Data hygiene:
  - Keep the RAG corpus de‑identified and versioned; source only trusted content.
  - Cache citations/URLs in exports; show provenance in the PDF.
- Minimal path to implement:
  1. Create `knowledge/` with curated markdown/JSON of guidelines (Centor, CURB‑65, flu season, red flags).
  2. Build an embedding index (e.g., sentence‑transformers) in `knowledge/index/`.
  3. After inference, retrieve top 3–5 passages with a query built from the case and top‑k differential.
  4. Generate a short rationale + test suggestions; include citations in the report.

#### Proof‑of‑Concept plan (baked into this project)

- Directory & files

  - `knowledge/` → curated content (markdown/json) with metadata: `title`, `source`, `url`, `version_date`, `tags`, `icd10`, `rule_id`.
  - `knowledge/index/` → vector index (FAISS/Chroma) + `meta.json` mapping ids → {text, metadata}.
  - `rag/index.py` → offline: chunk, embed, persist index.
  - `rag/retriever.py` → runtime: load index, retrieve top‑k passages.
  - `rag/generator.py` → compose rationale from retrieved passages (template‑based or small LLM).
  - `rag/config.yaml` → enable flag, model name, top_k, filters, paths.

- Offline indexing (one‑time)

  - Chunk to 300–600 tokens with overlap; embed with `sentence-transformers/all-MiniLM-L6-v2` (or similar); store normalized embeddings.
  - Persist index + `meta.json`; record index version and corpus snapshot date.

- Runtime integration (v2)

  - In `versions/v2/enhanced_medical_system.py`, after `diagnose_with_reasoning`:
    - Build query from: primary diagnosis, ICD‑10, key findings (from `clinical_reasoning`), top‑k differential, and any red flags.
    - `passages = retriever.search(query, top_k, filters={"icd10": primary_icd10})`
    - `rationale_text = generator.summarize(results, symptom_responses, passages)`
    - Display `rationale_text` in UI and include it (plus citations) in PDF/Text exports.

- Safety & provenance

  - Do not change probabilities; RAG only annotates.
  - Show source name/URL/version for each citation; keep `knowledge/README.md` of sources and update cadence.
  - Keep index local; avoid sending PHI to external services.

- Minimal evaluation
  - Retrieval precision@k spot‑checks by clinician reviewer.
  - Helpfulness rating of rationale/test suggestions.
  - Guardrails for disallowed content; keep output terse and cited.

## Stretch goals

- Uncertainty‑aware UX
  - Monte‑Carlo dropout; route low‑confidence to more data/tests.
- External/temporal validation
  - Evaluate on time‑separated or out‑of‑site cohorts.
- Monitoring
  - Drift detection for feature distributions and calibration; periodic re‑train.

## First actionable tasks (suggested order)

1. Create `configs/clinical_schema.yaml` with symptom/vitals/labs mappings.
2. Implement patient‑level splitter and class weighting; add Adam/L2/dropout toggles.
3. Add metrics module (AUROC/AUPRC/F1/Confusion) and reliability diagram + ECE.
4. Expand rules: Centor + CURB‑65; add “need more info” if entropy/confidence threshold.
5. Build batch CLI to score CSV and emit results JSON/CSV.

> Tip: keep a changelog and version datasets/runs (seed, config, code commit) for reproducibility.
