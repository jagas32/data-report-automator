#!/usr/bin/env python3
"""Personal Data Report Automator — end-to-end pipeline runner.

Processes any CSV in inputs/ through: clean -> insights -> markdown report.
Schema-agnostic: auto-detects date, metric, and category columns.

Usage:
    python3 scripts/run_pipeline.py              # all CSVs in inputs/
    python3 scripts/run_pipeline.py orders.csv   # one file
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUTS, OUTPUTS = ROOT / "inputs", ROOT / "outputs"
TODAY = date.today().isoformat()
METRIC_NAME_HINT = re.compile(r"amount|sales|revenue|price|total|cost|value", re.I)


# ---------------------------------------------------------------- cleaning
def snake(name):
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")


def clean(src: Path):
    raw = pd.read_csv(src)
    df, log = raw.copy(), []
    rows_in = len(df)

    df.columns = [snake(c) for c in df.columns]
    log.append("normalized column names to snake_case")

    n_dupes = int(df.duplicated().sum())
    if n_dupes:
        df = df.drop_duplicates().reset_index(drop=True)
        log.append(f"dropped {n_dupes} exact duplicate row(s)")

    date_cols, metric_cols = [], []
    for col in df.columns:
        s = df[col]
        if s.dtype == object:
            s = s.str.strip()
            # date detection
            parsed = pd.to_datetime(s, format="mixed", errors="coerce")
            if parsed.notna().mean() >= 0.9 and not s.str.fullmatch(r"-?[\d,.$%\s]+").all():
                df[col] = parsed.dt.strftime("%Y-%m-%d")
                date_cols.append(col)
                log.append(f"parsed '{col}' to ISO 8601 dates")
                continue
            # numeric detection (strip currency/thousands/percent)
            stripped = s.str.replace(r"[$,%\s]", "", regex=True)
            nums = pd.to_numeric(stripped, errors="coerce")
            non_null = s.notna()
            if non_null.any() and nums[non_null].notna().mean() >= 0.9:
                df[col] = nums
                metric_cols.append(col)
                log.append(f"coerced '{col}' to numeric (stripped $ , %)")
                continue
            # casing conflicts in categoricals
            if s.nunique() > s.str.title().nunique():
                df[col] = s.str.title()
                log.append(f"normalized casing in '{col}'")
            else:
                df[col] = s
        elif pd.api.types.is_numeric_dtype(s):
            metric_cols.append(col)

    null_counts = {c: int(n) for c, n in df.isna().sum().items() if n}
    for c, n in null_counts.items():
        log.append(f"{n} missing value(s) in '{c}' kept and flagged (not imputed)")

    # outlier flags (>3 IQR above Q3) on numeric columns
    outlier_flags = {}
    for col in metric_cols:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr > 0:
            mask = df[col] > q3 + 3 * iqr
            if mask.any():
                outlier_flags[col] = df.index[mask].tolist()
                log.append(f"flagged {int(mask.sum())} outlier(s) in '{col}' (>3 IQR), kept in data")

    meta = {
        "source": f"inputs/{src.name}", "rows_in": rows_in, "rows_out": len(df),
        "cleaned_at": TODAY, "date_cols": date_cols, "metric_cols": metric_cols,
        "outlier_rows": outlier_flags,
    }
    payload = {"metadata": meta, "cleaning_log": log, "data": df.to_dict(orient="records")}
    stem = src.stem
    (OUTPUTS / f"{stem}_cleaned.json").write_text(json.dumps(payload, indent=2, default=str))
    df.to_csv(OUTPUTS / f"{stem}_cleaned.csv", index=False)
    return df, payload


# ---------------------------------------------------------------- insights
def pick_metric(df, metric_cols):
    named = [c for c in metric_cols if METRIC_NAME_HINT.search(c)]
    pool = named or metric_cols
    return max(pool, key=lambda c: df[c].abs().sum()) if pool else None


def categoricals(df):
    out = []
    for col in df.select_dtypes(include=object).columns:
        nu = df[col].nunique()
        if 1 < nu <= max(12, int(len(df) * 0.3)) and nu < len(df) * 0.8:
            out.append(col)
    return out


def insights(df, cleaned, stem):
    meta = cleaned["metadata"]
    metric = pick_metric(df, meta["metric_cols"])
    date_col = meta["date_cols"][0] if meta["date_cols"] else None
    cats = categoricals(df)
    found, computed = [], {"metric_column": metric, "date_column": date_col, "category_columns": cats}

    d = df[df[metric].notna()] if metric else df
    total = float(d[metric].sum()) if metric else None
    computed["total"] = total
    computed["rows"] = int(len(df))

    if metric and date_col:
        m = d.copy()
        m["_month"] = pd.to_datetime(m[date_col]).dt.strftime("%Y-%m")
        monthly = m.groupby("_month")[metric].sum().round(2)
        computed["monthly"] = monthly.to_dict()
        if len(monthly) >= 2 and monthly.iloc[0]:
            growth = (monthly.iloc[-1] - monthly.iloc[0]) / abs(monthly.iloc[0]) * 100
            found.append({
                "finding": f"{metric} changed {growth:+.1f}% from {monthly.index[0]} to {monthly.index[-1]}",
                "evidence": f"{monthly.iloc[0]:,.0f} -> {monthly.iloc[-1]:,.0f}; total {total:,.0f} across {len(d)} rows",
                "severity": "high", "suggested_chart": "line",
            })

    if metric:
        for cat in cats:
            g = d.groupby(cat)[metric].sum().sort_values(ascending=False).round(2)
            computed[f"by_{cat}"] = g.to_dict()
            share = g.iloc[0] / total * 100 if total else 0
            found.append({
                "finding": f"'{g.index[0]}' leads {cat} by {metric}",
                "evidence": f"{g.iloc[0]:,.0f} = {share:.1f}% of total; next: {g.index[1] if len(g) > 1 else 'n/a'} ({g.iloc[1]:,.0f})" if len(g) > 1 else f"{g.iloc[0]:,.0f}",
                "severity": "high" if share >= 40 else "medium", "suggested_chart": "bar",
            })

    for col, rows in meta["outlier_rows"].items():
        worst = df.loc[rows, col].max()
        share = (worst / total * 100) if (total and col == metric) else None
        ev = f"max outlier value {worst:,.0f} in '{col}' across {len(rows)} flagged row(s)"
        if share:
            ev += f" = {share:.1f}% of total {metric}"
        found.append({"finding": f"Outlier(s) detected in '{col}'", "evidence": ev,
                      "severity": "high" if share and share > 15 else "medium", "suggested_chart": "none"})

    found.sort(key=lambda f: {"high": 0, "medium": 1, "low": 2}[f["severity"]])
    found = found[:7]

    caveats = [line for line in cleaned["cleaning_log"]
               if any(k in line for k in ("missing", "duplicate", "outlier"))]
    headline = found[0]["finding"] if found else "No quantifiable insights detected"

    payload = {"headline": headline, "insights": found, "caveats": caveats, "computed": computed}
    (OUTPUTS / f"{stem}_insights.json").write_text(json.dumps(payload, indent=2))
    return payload


# ---------------------------------------------------------------- report
def md_table(series_dict, key_hdr, val_hdr, max_rows=10):
    items = list(series_dict.items())
    rows = items[:max_rows]
    lines = [f"| {key_hdr} | {val_hdr} |", "|---|---:|"]
    lines += [f"| {k} | {v:,.0f} |" for k, v in rows]
    if len(items) > max_rows:
        lines.append(f"| Other ({len(items) - max_rows}) | {sum(v for _, v in items[max_rows:]):,.0f} |")
    return "\n".join(lines)


def report(stem, cleaned, ins):
    meta, comp = cleaned["metadata"], ins["computed"]
    metric = comp.get("metric_column")

    outline = {"title": f"{stem.replace('_', ' ').title()} Report — {TODAY}",
               "sections": [
                   {"heading": "Executive Summary", "points": [ins["headline"]] + [f["finding"] for f in ins["insights"][1:3]]},
                   {"heading": "Key Metrics", "metrics": [m for m in ("total", "rows") if comp.get(m) is not None]},
                   {"heading": "Findings", "findings": [f"{f['severity']}: {f['finding']}" for f in ins["insights"]]},
                   {"heading": "Data Quality Notes", "points": cleaned["cleaning_log"]},
                   {"heading": "Appendix", "points": ["source, method, columns"]},
               ]}
    (OUTPUTS / f"{stem}_report_outline.json").write_text(json.dumps(outline, indent=2))

    parts = [f"# {outline['title']}", "", "## Executive Summary", ""]
    summary = [ins["headline"] + "."]
    summary += [f["finding"] + f" ({f['evidence']})." for f in ins["insights"][1:3]]
    if ins["caveats"]:
        summary.append(f"Caveat: {ins['caveats'][0]}.")
    parts.append(" ".join(summary))

    parts += ["", "## Key Metrics", ""]
    rows = [("Rows analyzed", f"{comp['rows']:,}")]
    if comp.get("total") is not None:
        rows.insert(0, (f"Total {metric}", f"{comp['total']:,.0f}"))
    parts += ["| Metric | Value |", "|---|---:|"] + [f"| {k} | {v} |" for k, v in rows]

    parts += ["", "## Findings", ""]
    for f in ins["insights"]:
        parts += [f"### {f['finding']}", "", f"{f['evidence']}.", ""]
    if comp.get("monthly"):
        parts += ["### Monthly trend", "", md_table(comp["monthly"], "Month", f"{metric}"), ""]
    for cat in comp.get("category_columns", []):
        key = f"by_{cat}"
        if comp.get(key):
            parts += [f"### {metric} by {cat}", "", md_table(comp[key], cat.title(), metric), ""]

    parts += ["## Data Quality Notes", "",
              f"Rows in: {meta['rows_in']}; rows out: {meta['rows_out']}. " +
              " ".join(s.capitalize() + "." for s in cleaned["cleaning_log"]), ""]
    parts += ["## Appendix", "",
              f"- **Source:** `{meta['source']}`, cleaned {meta['cleaned_at']}",
              "- **Method:** `scripts/run_pipeline.py` (data-cleaner → insight-generator → report-formatter skills)",
              f"- **Detected columns:** metric=`{metric}`, date=`{comp.get('date_column')}`, categories={comp.get('category_columns')}",
              f"- **Intermediates:** `outputs/{stem}_cleaned.json`, `outputs/{stem}_insights.json`", ""]

    path = OUTPUTS / f"{stem}_report_{TODAY}.md"
    path.write_text("\n".join(parts))
    return path


# ---------------------------------------------------------------- main
def run(src: Path):
    print(f"=== {src.name} ===")
    df, cleaned = clean(src)
    ins = insights(df, cleaned, src.stem)
    path = report(src.stem, cleaned, ins)
    print(f"rows {cleaned['metadata']['rows_in']} -> {cleaned['metadata']['rows_out']} | "
          f"{len(ins['insights'])} insights | report: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    OUTPUTS.mkdir(exist_ok=True)
    if len(sys.argv) > 1:
        targets = [INPUTS / sys.argv[1]]
    else:
        targets = sorted(INPUTS.glob("*.csv"))
    if not targets or not all(t.exists() for t in targets):
        sys.exit("No CSV files found in inputs/")
    for t in targets:
        run(t)
