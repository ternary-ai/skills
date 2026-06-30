---
name: compare
description: Compare two or more tickers, segments, or time periods across one or more metrics. Fetches data for every comparison target via tools, builds a summary table, and optionally embeds it in the Thesis. Use whenever the user asks to compare, benchmark, rank, or contrast — e.g. "compare MVIS vs peers", "how does MVIS revenue compare to LAZR?", "benchmark margins across sector".
---

# Compare

## Overview

Four-step workflow: frame → fetch → table → return.
Act on defaults immediately. Do NOT ask before producing the first result.
The user will revise if needed.

---

## DEFAULTS — apply these unless the user states otherwise

| Dimension | Default |
|---|---|
| **Metrics** | Revenue, Gross Margin, Net Income (3-row quick table) |
| **Period** | Latest single quarter (`quarterlyReports[0]`) |
| **Unit** | $M — auto-upgrade to $B if all values exceed 1 000 |
| **Targets** | Tickers named in the message; if "vs peers" → use peers list from `<stock_context>` |
| **Section heading** | `## Peer Comparison — {Metrics} (Latest Quarter, $M)` |

Only deviate from a default when the user explicitly names something different.
Never ask about defaults.

---

## Step 1 — Frame (thought only, no tool call)

In your reasoning state:
1. Targets list (from message or peers in stock_context).
2. Metric(s) — apply default if not specified.
3. Period — apply default if not specified.
4. Which tool each metric requires (see Data Source Map in Step 2).

Only call `request_user_input` when targets cannot be determined at all
(e.g. user says "compare" with no tickers and no peers in context).

---

## Step 2 — Collect Data for Every Target

Fetch sequentially: one tool call per target.
Check `<stock_context>` / `<acquired_data>` first — skip the call if the value is already there.

**Critical:** Use the **exact tool** specified in the data source map below for each metric family. The defaults (Revenue, Gross Margin, Net Income) ALL require `INCOME_STATEMENT`, not `OVERVIEW`.

### Data Source Map

| Metric family | Primary tool | Key field(s) |
|---|---|---|
| Revenue, Gross Profit, Operating Income, Net Income, EBITDA | `INCOME_STATEMENT(symbol=…)` | `totalRevenue`, `grossProfit`, `operatingIncome`, `netIncome` |
| Free Cash Flow, Operating Cash Flow, CapEx | `CASH_FLOW(symbol=…)` | `operatingCashflow`, `capitalExpenditures` |
| EPS (actual + estimate), beat/miss | `EARNINGS(symbol=…)` | `reportedEPS`, `estimatedEPS`, `surprise` |
| Total Debt, Cash, Book Value, Current Ratio | `BALANCE_SHEET(symbol=…)` | `totalDebt`, `cashAndCashEquivalentsAtCarryingValue`, `totalShareholderEquity` |
| Market price, P/E, Market Cap, Beta | `OVERVIEW(symbol=…)` | `MarketCapitalization`, `PERatio`, `Beta`, `52WeekHigh`, `52WeekLow` |
| Latest price / daily return | `GLOBAL_QUOTE(symbol=…)` | `price`, `changePercent` |

### Fallback chain
1. `<stock_context>` / `<acquired_data>` — use if present.
2. Primary tool from the map above.
3. On failure: `CASH_FLOW` for FCF-adjacent; `OVERVIEW` for market metrics.
4. All tools fail for a target → cell = `N/A`. Never abort the whole comparison.

### Rules
- One tool call at a time, no preamble.
- `quarterlyReports` for quarterly; `annualReports` for annual.
- Normalise all values to the same unit before building the table.

---

## Step 3 — Build the Summary Table

Construct a clean markdown comparison table.

### Table format

```
| Metric | {Target A} | {Target B} | {Target C} | Notes |
|---|---|---|---|---|
| Revenue (TTM, $M) | 123.4 | 456.7 | 89.0 | |
| Gross Margin | 42% | 61% | 38% | |
| Net Income (TTM, $M) | (12.1) | 34.5 | (5.6) | Losses in () |
| EPS (last Q) | (0.08) | 0.22 | (0.15) | |
```

### Formatting rules
- One row per metric, one column per target.
- Use the **same period** for every target in a given row. If a target has no data for
  that period, show `N/A`.
- Losses and negatives in parentheses: `(12.1)`.
- Percentages to one decimal place: `42.3%`.
- Dollar values in $M (or $B if all values > 1000) to one decimal place.
- Multiples to one decimal place: `18.4x`.
- Add a **Notes** column only when a cell needs qualification (e.g. "FY estimate", "TTM").
- Do NOT add a prose paragraph restating the numbers — the table is self-contained.
- Add a single **bold callout line** below the table identifying the standout finding:
  `**Standout:** {Target X} leads on {metric} by {magnitude} vs peers.`

### Section heading

Place the table under:
```
## Peer Comparison — {Metric(s)} ({Period})
```

### Optional: add a multi-series line chart

If the comparison is time-series (multiple periods, not a single snapshot), append a
`chart-line` multi-series block **immediately after the table** using the format from
`chart-writeup` Step 5 → Multi-series. Use `null` for missing periods.

Example for quarterly revenue across 4 peers:
```chart-line
{
  "title": "Quarterly Revenue — Peer Comparison ($M)",
  "unit": "$M",
  "labels": ["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4"],
  "series": [
    { "label": "LAZR", "values": [20.97, 16.45, 15.49, 22.48] },
    { "label": "INVZ", "values": [null,  null,  null,  6.03]  },
    { "label": "OUST", "values": [null,  null,  null,  30.09] }
  ]
}
```

---

## Step 4 — Return Results

Populate the output JSON:

- `thesis`: include the full updated thesis with the new `## Peer Comparison` section
  appended. Preserve all prior content.
- `chat`: one sentence stating what was compared, how many targets, and the key takeaway.
- `assessment`: one sentence describing what was just done.
- `skill`: `"compare"`

### When data is missing for a target
- Mark that cell `N/A` — do NOT omit the row or the target column.
- Mention missing targets briefly in `chat` only: "AEVA data unavailable from API."
- Never add disclaimers, caveats, or "Note:" blocks inside the thesis table.

---

## Quick Reference — Common Comparison Patterns

| User asks | Targets | Metric | Tool |
|---|---|---|---|
| "compare revenue" | named tickers | `totalRevenue` quarterly | `INCOME_STATEMENT` × N |
| "benchmark margins" | named tickers | `grossProfit / totalRevenue` | `INCOME_STATEMENT` × N |
| "how does EPS compare" | named tickers | `reportedEPS` | `EARNINGS` × N |
| "compare FCF" | named tickers | `operatingCashflow − capitalExpenditures` | `CASH_FLOW` × N |
| "vs peers" | ticker + FMP peers from `<stock_context>` | as specified | appropriate tool × N |
| "sector comparison" | tickers from `<stock_context>` peers list | as specified | appropriate tool × N |
