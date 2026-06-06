# 📊 Personal Data Report Automator

**An AI-assisted data pipeline that turns raw CSV files into cleaned datasets and professional, insight-rich reports — automatically.**

Drop a messy CSV into `inputs/`, run one command (or one prompt), and get back analysis-ready data, ranked quantified insights, and a polished markdown report with executive summary, tables, and honest data-quality caveats.

```
inputs/orders.csv → clean → analyze → outputs/orders_report_2026-06-06.md
```

---

## Key Features

- **End-to-end automation** — ingest → clean → analyze → report in a single run; no manual spreadsheet work.
- **Skill-driven architecture** — each stage is a documented, reusable skill (`skills/*/SKILL.md`) with explicit contracts: structured JSON in, structured JSON out. Stages can be re-run or swapped independently.
- **Schema-agnostic** — auto-detects date, metric, and category columns; works on any reasonably tabular CSV without configuration.
- **Transparent cleaning** — raw inputs are never modified; every transformation (dedup, date parsing, currency stripping, casing fixes) is recorded in a cleaning log that surfaces in the final report.
- **Honest analytics** — insights are computed with pandas, not eyeballed; outliers are flagged rather than silently dropped, and headline trends are reported with and without them.
- **Professional output** — reports follow a consistent structure: executive summary, key metrics, severity-ranked findings with tables, data-quality notes, and an appendix.

## How to Run

### With Cowork (Claude)

Open this project folder in Cowork and prompt:

> "Run the full pipeline on `inputs/<yourfile>.csv` and show me the report."

Claude applies the skills in order (`data-cleaner` → `insight-generator` → `report-formatter`), with the added benefit of natural-language polish on the final report and the ability to answer follow-up questions about the data.

### With Python (standalone)

```bash
# Process every CSV in inputs/
python3 scripts/run_pipeline.py

# Process a single file
python3 scripts/run_pipeline.py warehouse_orders.csv
```

Requires Python 3 and pandas. Outputs land in `outputs/`.

## Example Outputs

Validated on a 30-row warehouse orders sample with planted quality issues (duplicate rows, mixed date formats, currency strings, missing values, inconsistent casing, a bulk outlier). The pipeline produced:

| Output | Contents |
|--------|----------|
| `warehouse_orders_cleaned.csv` / `.json` | 29 clean rows + metadata + 8-step cleaning log |
| `warehouse_orders_insights.json` | 7 ranked insights with evidence and severity |
| `warehouse_orders_report_2026-06-06.md` | Full report with exec summary and 8 tables |

Headline findings from the sample: revenue up 542% Jan→May (225% excluding one bulk order the pipeline flagged as 24.2% of total revenue), West region leading at 48.1% share, Business customers at 4.6× Consumer average order value.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data processing | Python 3, pandas |
| Pipeline definition | SKILL.md skills (Claude-compatible) |
| Orchestration | `scripts/run_pipeline.py` or Cowork (Claude) |
| Output formats | CSV, structured JSON, Markdown |

## Project Structure

```
inputs/     Raw CSV files (read-only)
outputs/    Cleaned data, insights JSON, reports
skills/     Pipeline stage definitions
examples/   Sample inputs and outputs
scripts/    End-to-end runner
docs/       Documentation
```

## Portfolio Value

This project demonstrates practical AI-engineering patterns beyond one-off prompting:

- **Agent skill design** — decomposing a workflow into documented, composable skills with clear I/O contracts, the same pattern used in production Claude agent systems.
- **Hybrid human/AI pipelines** — the same pipeline runs fully scripted (deterministic, CI-ready) or AI-orchestrated (flexible, conversational), showing where each approach earns its keep.
- **Data engineering fundamentals** — defensive cleaning, audit logging, outlier handling, and reporting that states its caveats instead of hiding them.
- **Token-efficient AI workflows** — large datasets are summarized (shape, dtypes, samples) rather than dumped into context, keeping costs predictable.

## Roadmap

.xlsx input support · PDF/DOCX export · GitHub deployment with CI batch processing
