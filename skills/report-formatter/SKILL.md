---
name: report-formatter
description: Generate a professional markdown report with tables and summaries from cleaned data and insights. Use as the final pipeline step, or when the user asks for a report, summary document, or formatted writeup.
---

# Report Formatter

Assemble `outputs/<dataset>_cleaned.json` + `outputs/<dataset>_insights.json` into a markdown report at `outputs/<dataset>_report_YYYY-MM-DD.md`.

## Process

1. **Outline first.** Before generating the full markdown, produce a structured JSON summary of the report sections:

```json
{
  "title": "...",
  "sections": [
    {"heading": "Executive Summary", "points": ["..."]},
    {"heading": "Key Metrics", "metrics": ["..."]},
    {"heading": "Findings", "findings": ["one entry per insight, ordered by severity"]},
    {"heading": "Data Quality Notes", "points": ["..."]}
  ]
}
```

2. Generate the full markdown report from this outline.

## Report Structure

```markdown
# <Dataset> Report — <Month YYYY>

## Executive Summary
3–5 sentences: primary insight first, then key findings, then one caveat if material. Self-contained for readers who read only this section.

## Key Metrics
| Metric | Value | Change |
|--------|------:|-------:|

## Findings
One H3 per insight, ordered by severity. Each: 1–2 sentence claim, supporting table or figures, brief interpretation.

## Data Quality Notes
Summarize cleaning_log and caveats. Rows in/out, what was imputed or flagged.

## Appendix
Method notes, column definitions, source file name and date.
```

## Formatting Rules

- **Tables:** right-align numerics, thousands separators, consistent decimals (money 2, percents 1), units in headers (`Revenue ($K)`). Limit to ~10 rows; show top N with an "Other" rollup row.
- **Numbers in prose:** include a comparison or baseline ("up 12% vs. April") rather than standalone figures.
- **Summaries:** state the conclusion first, followed by supporting evidence. Omit introductory filler.
- **Tone:** neutral and factual. Avoid evaluative adjectives and speculation. Use bold only for genuine emphasis.
- **Length:** 1–2 pages of markdown. Low-severity insights receive one line each.

## Rules
- Always start with the structured JSON summary of report sections (see Process) before generating full markdown.
- Use numbers only from the JSON inputs; do not recompute or estimate values in prose.
- Include all items from `caveats` in Data Quality Notes.
- If the insights JSON is missing, run insight-generator first.
- After writing the markdown, offer docx/pdf conversion; create those files only on request.
