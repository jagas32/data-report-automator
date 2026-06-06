---
name: insight-generator
description: Derive ranked, quantified insights from cleaned data. Use after data-cleaner, or when the user asks what the data shows, trends, anomalies, or key takeaways.
---

# Insight Generator

Turn cleaned data (`outputs/<dataset>_cleaned.json`) into a ranked set of quantified insights.

## Steps

1. **Load** the cleaned JSON; read `metadata` and `cleaning_log` for context.
2. **Analyze** (compute, don't eyeball — use pandas):
   - Descriptive stats per numeric column; distributions per categorical.
   - Trends over time (if a date column exists): direction, % change, inflection points.
   - Segment comparisons: top/bottom performers, concentration (e.g., top 5 = X%).
   - Anomalies and outliers, correlations worth noting (|r| > 0.5).
3. **Rank** insights by business relevance, not statistical novelty. Lead with what changed or surprises.
4. **Output** to `outputs/<dataset>_insights.json`:

```json
{
  "headline": "One-sentence biggest takeaway",
  "insights": [
    {"finding": "...", "evidence": "metric + numbers", "severity": "high|medium|low", "suggested_chart": "bar|line|none"}
  ],
  "caveats": ["data quality issues from cleaning_log that limit conclusions"]
}
```

## Rules
- Every insight needs a number. "Sales grew" → "Sales grew 23% QoQ ($410K → $504K)".
- 3–7 insights. More dilutes; fewer undersells.
- State caveats honestly — cleaning issues propagate to conclusions.
