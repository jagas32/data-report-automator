# Personal Data Report Automator

## Overview & Goal
Turn raw CSV/Excel files into cleaned datasets and professional reports with insights. Pipeline: ingest → clean → analyze → report.

## Folder Structure
```
inputs/     Raw CSV/Excel files (never modified)
outputs/    Cleaned data + generated reports
skills/     Pipeline skills (SKILL.md each)
examples/   Sample inputs and example outputs
scripts/    Reusable Python helpers
docs/       Project documentation
```

## Key Conventions
- Intermediate results passed as structured JSON (`outputs/<dataset>_cleaned.json` with `data`, `metadata`, `cleaning_log` keys).
- Outputs are clean and deterministic: no debug prints, timestamped filenames (`YYYY-MM-DD`).
- Token efficiency: summarize large datasets (shape, dtypes, sample rows) rather than dumping full contents into context.
- Raw inputs are read-only; all transforms write to `outputs/`.

## Running the Pipeline
1. Drop raw file(s) into `inputs/`.
2. Apply skills in order: `data-cleaner` → `insight-generator` → `report-formatter`.
3. Final report lands in `outputs/` as markdown (convertible to docx/pdf on request).

## Status: COMPLETE (2026-06-06)
- All three pipeline skills done: `data-cleaner`, `insight-generator`, `report-formatter` (JSON section outline required before markdown).
- `scripts/run_pipeline.py`: schema-agnostic runner — processes any CSV in `inputs/` end-to-end (clean → insights → report). Run `python3 scripts/run_pipeline.py [filename]`.
- Validated on `inputs/warehouse_orders.csv` (30 rows, planted quality issues); full output set in `outputs/`.
- Portfolio README.md at root (features, Cowork + Python usage, example outputs, tech stack, portfolio value).
- Decision: CSV + Markdown only — no native Excel integration.

## Future Enhancements
- Support for .xlsx files (pandas)
- GitHub repo deployment
- Optional PDF/DOCX export via skills
