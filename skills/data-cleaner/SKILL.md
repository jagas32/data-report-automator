---
name: data-cleaner
description: Clean raw CSV/Excel files into validated, analysis-ready data. Use when a new file lands in inputs/ or the user asks to clean, fix, or prepare a dataset.
---

# Data Cleaner

Transform raw tabular files into clean, structured data with a documented cleaning log.

## Steps

1. **Profile first.** Load with pandas; report shape, dtypes, null rates, duplicate count, and 5 sample rows. Never dump the full dataset into context.
2. **Clean.**
   - Normalize column names to `snake_case`.
   - Parse dates to ISO 8601; coerce numerics (strip `$`, `,`, `%`).
   - Drop exact duplicate rows; flag near-duplicates instead of deleting.
   - Handle nulls explicitly: impute only when justified, otherwise keep and note.
   - Flag outliers (>3 IQR) — never silently remove.
3. **Validate.** Re-check dtypes, ranges, and row counts before/after.
4. **Output.** Write to `outputs/<dataset>_cleaned.json`:

```json
{
  "metadata": {"source": "...", "rows_in": 0, "rows_out": 0, "cleaned_at": "YYYY-MM-DD"},
  "cleaning_log": ["dropped 12 duplicate rows", "..."],
  "data": [...]
}
```

Also write `outputs/<dataset>_cleaned.csv` for human use.

## Rules
- Never modify files in `inputs/`.
- Every transformation goes in `cleaning_log` — the report cites it.
- If a file is ambiguous (multiple header rows, merged cells), ask before guessing.
