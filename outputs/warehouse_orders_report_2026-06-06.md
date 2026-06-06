# Warehouse Orders Report — 2026-06-06

## Executive Summary

sales_amount changed +541.9% from 2026-01 to 2026-05. 'West' leads region by sales_amount (26,559 = 48.1% of total; next: North (19,334)). 'Delivered' leads status by sales_amount (50,012 = 90.5% of total; next: Shipped (2,513)). Caveat: dropped 1 exact duplicate row(s).

## Key Metrics

| Metric | Value |
|---|---:|
| Total sales_amount | 55,243 |
| Rows analyzed | 29 |

## Findings

### sales_amount changed +541.9% from 2026-01 to 2026-05

4,214 -> 27,049; total 55,243 across 28 rows.

### 'West' leads region by sales_amount

26,559 = 48.1% of total; next: North (19,334).

### 'Delivered' leads status by sales_amount

50,012 = 90.5% of total; next: Shipped (2,513).

### 'Business' leads customer_type by sales_amount

48,494 = 87.8% of total; next: Consumer (6,749).

### Outlier(s) detected in 'sales_amount'

max outlier value 13,350 in 'sales_amount' across 1 flagged row(s) = 24.2% of total sales_amount.

### 'Standing Desk' leads product by sales_amount

20,271 = 36.7% of total; next: Monitor Arm (16,020).

### Outlier(s) detected in 'quantity'

max outlier value 150 in 'quantity' across 1 flagged row(s).

### Monthly trend

| Month | sales_amount |
|---|---:|
| 2026-01 | 4,214 |
| 2026-02 | 5,494 |
| 2026-03 | 10,830 |
| 2026-04 | 7,656 |
| 2026-05 | 27,049 |

### sales_amount by product

| Product | sales_amount |
|---|---:|
| Standing Desk | 20,271 |
| Monitor Arm | 16,020 |
| Office Chair | 12,558 |
| Bookshelf | 3,504 |
| Filing Cabinet | 2,890 |

### sales_amount by region

| Region | sales_amount |
|---|---:|
| West | 26,559 |
| North | 19,334 |
| East | 6,194 |
| South | 3,156 |

### sales_amount by status

| Status | sales_amount |
|---|---:|
| Delivered | 50,012 |
| Shipped | 2,513 |
| Pending | 1,495 |
| Cancelled | 1,223 |

### sales_amount by customer_type

| Customer_Type | sales_amount |
|---|---:|
| Business | 48,494 |
| Consumer | 6,749 |

## Data Quality Notes

Rows in: 30; rows out: 29. Normalized column names to snake_case. Dropped 1 exact duplicate row(s). Parsed 'date' to iso 8601 dates. Coerced 'sales_amount' to numeric (stripped $ , %). Normalized casing in 'region'. 1 missing value(s) in 'sales_amount' kept and flagged (not imputed). Flagged 1 outlier(s) in 'quantity' (>3 iqr), kept in data. Flagged 1 outlier(s) in 'sales_amount' (>3 iqr), kept in data.

## Appendix

- **Source:** `inputs/warehouse_orders.csv`, cleaned 2026-06-06
- **Method:** `scripts/run_pipeline.py` (data-cleaner → insight-generator → report-formatter skills)
- **Detected columns:** metric=`sales_amount`, date=`date`, categories=['product', 'region', 'status', 'customer_type']
- **Intermediates:** `outputs/warehouse_orders_cleaned.json`, `outputs/warehouse_orders_insights.json`
