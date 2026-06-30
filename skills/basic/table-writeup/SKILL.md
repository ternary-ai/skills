---
name: table-writeup
description: "[TABLES ONLY] Generates plain markdown text tables (rows and columns). Use ONLY when the user explicitly asks for a table, comparison table, or tabular summary. DO NOT use this skill for charts, bar charts, line charts, plots, or any visual rendering — use chart-writeup instead."
---

# Table Writeup

## ⏱ Time-series layout rule (applies to ALL tables with a time dimension)

Whenever the data has a time axis (quarters, years, months, dates), the periods go **across the top as column headers** and the metric(s) go **as row labels on the left**. Values fill the cells.

**Correct ✔**
| Metric | 2024-Q1 | 2024-Q2 | 2024-Q3 | 2024-Q4 | 2025-Q1 | 2025-Q2 | 2025-Q3 | 2025-Q4 |
|---|---|---|---|---|---|---|---|---|
| DPS ($) | 0.65 | 0.65 | 0.65 | 0.65 | 0.70 | 0.70 | 0.70 | 0.70 |

**Wrong ✘** (never do this for time-series data)
| Quarter | Dividend / Share ($) |
|---|---|
| 2024-Q1 | 0.65 |
| 2024-Q2 | 0.65 |

Rules:
- If more than one metric is shown for the same time periods, each metric gets its own row.
- Period labels: use `YYYY-QN` for quarters, `FYYYY` for annual fiscal years, `YYYY-MM` for months.
- If there are more than 12 periods, split into two rows (oldest half, newest half) with the same column layout.
- This rule applies whether the table is a standalone output or the sparse-data fallback from chart-writeup.

---

## Overview

Generate markdown tables from structured data and append them to the Thesis.

## Quick Use

1. Gather structured data (list of dict rows).
2. Use `scripts/table.py` to render a markdown table.
3. Append the table into the Thesis section.

## Data Input

Provide a JSON array of objects, each object is a row:

```json
[
  {"metric": "Revenue", "value": "$2.1B", "delta": "+8%"},
  {"metric": "Gross Margin", "value": "78%", "delta": "+2pp"}
]
```

## Script

Render a markdown table:

```bash
python skills/table-writeup/scripts/table.py --input rows.json --title "Key Metrics"
```

## Writeup Insertion

Append the generated markdown table to the Thesis section. Do not remove existing content.

## Notes

Prefer short tables (3–8 rows). If data is missing, note it in chat but do not add that disclaimer to the writeup.
