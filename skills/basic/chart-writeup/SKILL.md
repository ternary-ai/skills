---
name: chart-writeup
description: "[CHARTS ONLY] Renders interactive visual charts — bar, line, area, revenue, EBITDA, FCF, EPS, price, or peer charts — using D3 fenced blocks (chart-bar / chart-line) or matplotlib. ALWAYS use this skill when the user asks for a chart, bar chart, line chart, plot, or any visual rendering. NEVER use table-writeup for chart requests — table-writeup cannot render visuals."
---

# Chart Writeup

## ⛔ CALL ORDER — data-source MUST run before this skill

Before executing any step in this skill, `read_skill("data-source")` must already have been called.
The plan always starts with `data-source`, then `chart-writeup`, then `standard-charts`:

```
1. read_skill("data-source")     — identify tool, check context
2. read_skill("chart-writeup")   — this skill
3. read_skill("standard-charts") — chart type, time frame, unit defaults
```

If `data-source` has not been called yet, call it now before proceeding with Step 1 below.

---

## ⛔ NEVER ask the user for any of the following

Asking any of these is a skill execution failure. Resolve them from the defaults below:

| What the agent might want to ask | How to resolve it instead |
|---|---|
| "Bar chart or line chart?" | Use the **Chart type** column in the Defaults table below |
| "Annual or quarterly?" | If the user said "quarterly" → use quarterly; otherwise → use the annual default |
| "How many periods / quarters?" | Use the **Time frame** default from the table below |
| "Which data source should I use?" | Always follow the fallback chain: context → Alpha Vantage → ask. Never offer the user a choice. |
| "Should I create a new thesis document?" | **Never ask this.** If `<current_thesis>` is empty or absent → create one immediately (see **New thesis document** below). If it already exists → append to it. |
| "Which section should the chart go in?" | Always add under `## {MetricName} ({Annual/Quarterly})` |
| "Should I use INCOME_STATEMENT or CASH_FLOW?" | Skill defines the tool order. Call `INCOME_STATEMENT` first; if it errors, fall back as documented in Step 2. |
| "What is the dividend per share / quarterly dividend / annual DPS?" | ⛔ **Never ask.** Call `get_dividend_history(ticker)` and read `dividendHistory[].amount` verbatim. Do not derive per-payment amounts from `trailingAnnualDividendRate`. |

---

## New thesis document

If the user says "new thesis document", "create a thesis", "start a thesis", or "add to a new thesis", **or if `<current_thesis>` is empty or absent**:
- Create a thesis immediately with header: `# {TICKER} Investment Thesis\n_{Date}_\n\n`
- Do not ask for confirmation, section placement, or ticker — it is already in the session context.
- Embed the chart result under `## {MetricName} ({Frequency})`.

---

## Defaults — reference only

> ⚠️ **Always call `read_skill("standard-charts")` first** — it is the single authoritative source for chart type, rendering method, time frame, unit, and which tool to call. The table below is a quick-reference summary only; in case of conflict, `standard-charts` wins.

> **Rendering:** Use `chart-bar` / `chart-line` D3 fenced blocks for bar and line shapes.
> Use `generate_chart_matplotlib` for everything else (scatter, heatmap, candlestick, pie/donut, waterfall, stacked area, histogram).

#### Price & Market Data

| User said | Chart type | Rendering | Time frame | Unit | First tool(s) to call |
|---|---|---|---|---|---|
| **price / stock price / price history** | `chart-line` | D3 | Daily, last 1 year | $ | `TIME_SERIES_DAILY(symbol=…)` |
| **price vs benchmark / relative performance** | `chart-line` dual | D3 | Daily, last 1 year | index (100) | `TIME_SERIES_DAILY(symbol=…)` × 2 |
| **intraday / intraday price** | `chart-line` | D3 | 1-day, 5-min intervals | $ | `TIME_SERIES_INTRADAY(symbol=…)` |
| **volume** | `chart-bar` | D3 | Daily, last 3 months | shares | `TIME_SERIES_DAILY(symbol=…)` |
| **candlestick / OHLC** | candlestick | matplotlib | Daily, last 6 months | $ | `TIME_SERIES_DAILY(symbol=…)` |
| **moving average / SMA / EMA** | `chart-line` | D3 | Daily, last 1 year | $ | `TIME_SERIES_DAILY(symbol=…)` |

#### Returns

| User said | Chart type | Rendering | Time frame | Unit | First tool(s) to call |
|---|---|---|---|---|---|
| **cumulative returns / total return** | `chart-line` | D3 | Daily, last 1–5 years | % (0-indexed) | `TIME_SERIES_DAILY(symbol=…)` |
| **monthly returns / periodic returns** | `chart-bar` (green/red) | D3 | Monthly, last 2 years | % | `TIME_SERIES_DAILY(symbol=…)` |
| **return distribution / histogram** | histogram | matplotlib | Daily, last 2 years | % | `TIME_SERIES_DAILY(symbol=…)` |
| **drawdown / max drawdown** | area (red fill) | matplotlib | Daily, last 1–5 years | % | `TIME_SERIES_DAILY(symbol=…)` |

#### Risk & Volatility

| User said | Chart type | Rendering | Time frame | Unit | First tool(s) to call |
|---|---|---|---|---|---|
| **volatility / realized vol** | `chart-line` | D3 | Daily, last 1 year (30-day rolling) | % ann. | `TIME_SERIES_DAILY(symbol=…)` |
| **correlation matrix** | heatmap | matplotlib | Single period | −1 to +1 | `TIME_SERIES_DAILY(symbol=…)` × N tickers |
| **beta / beta vs market** | scatter + regression | matplotlib | Daily, last 1 year | — | `TIME_SERIES_DAILY(symbol=…)` + benchmark |

#### Portfolio & Allocation

| User said | Chart type | Rendering | Time frame | Unit | First tool(s) to call |
|---|---|---|---|---|---|
| **asset allocation / portfolio weights** | donut | matplotlib | Current snapshot | % | context / `calculate_portfolio_exposure_map` |
| **allocation over time** | stacked area | matplotlib | Monthly/quarterly | % | context |
| **factor exposure** | horizontal bar | matplotlib | Current | z-score or % | `pca_factor_decomposition` |

#### Financial Statements & Fundamentals

| User said | Chart type | Rendering | Time frame | Unit | First tool(s) to call |
|---|---|---|---|---|---|
| **quarterly EBITDA** | `chart-bar` | D3 | Last 8 quarters | $M | `INCOME_STATEMENT(symbol=…)` + `CASH_FLOW(symbol=…)` |
| **EBITDA** (no frequency stated) | `chart-bar` | D3 | Annual, last 5 FY | $M | `INCOME_STATEMENT(symbol=…)` + `CASH_FLOW(symbol=…)` |
| **quarterly revenue / sales** | `chart-bar` | D3 | Last 8 quarters | $M or $B | `INCOME_STATEMENT(symbol=…)` |
| **revenue / sales / top line** | `chart-bar` | D3 | Annual, last 5 FY | $M or $B | `INCOME_STATEMENT(symbol=…)` |
| **revenue growth rate** | `chart-line` | D3 | Annual, last 5 FY | % | `INCOME_STATEMENT(symbol=…)` |
| **quarterly net income / earnings** | `chart-bar` | D3 | Last 8 quarters | $M | `INCOME_STATEMENT(symbol=…)` |
| **net income / earnings** | `chart-bar` | D3 | Annual, last 5 FY | $M | `INCOME_STATEMENT(symbol=…)` |
| **gross profit** | `chart-bar` | D3 | Annual, last 5 FY | $M | `INCOME_STATEMENT(symbol=…)` |
| **gross margin** | `chart-line` | D3 | Annual, last 5 FY | % | `INCOME_STATEMENT(symbol=…)` |
| **operating income / EBIT** | `chart-bar` | D3 | Annual, last 5 FY | $M | `INCOME_STATEMENT(symbol=…)` |
| **operating margin** | `chart-line` | D3 | Annual, last 5 FY | % | `INCOME_STATEMENT(symbol=…)` |
| **margins** (combined gross/EBITDA/net) | `chart-line` 3 series | D3 | Annual, last 5 FY | % | `INCOME_STATEMENT(symbol=…)` + `CASH_FLOW(symbol=…)` |
| **EPS / earnings per share** | `chart-bar` | D3 | Last 8 quarters | $ | `EARNINGS(symbol=…)` |
| **EPS actual vs estimate / beat/miss** | bar + line | matplotlib | Last 8 quarters | $ | `EARNINGS(symbol=…)` |
| **FCF / free cash flow** | `chart-bar` | D3 | Annual, last 5 FY | $M | `CASH_FLOW(symbol=…)` |
| **FCF yield** | `chart-line` | D3 | Annual, last 5 FY | % | `CASH_FLOW(symbol=…)` + `OVERVIEW(symbol=…)` |
| **operating cash flow** | `chart-bar` | D3 | Annual, last 5 FY | $M | `CASH_FLOW(symbol=…)` |
| **capex** | `chart-bar` | D3 | Annual, last 5 FY | $M | `CASH_FLOW(symbol=…)` |
| **balance sheet composition** | stacked bar | matplotlib | Annual, last 5 FY | $M | `BALANCE_SHEET(symbol=…)` |
| **total debt / net debt** | `chart-bar` | D3 | Annual, last 5 FY | $M | `BALANCE_SHEET(symbol=…)` |
| **cash & equivalents** | `chart-bar` | D3 | Annual, last 5 FY | $M | `BALANCE_SHEET(symbol=…)` |
| **current assets** (any frequency) | `chart-bar` | D3 | Annual last 5 FY / Qtrly last 8 Q | $M | `BALANCE_SHEET(symbol=…)` |
| **current liabilities** | `chart-bar` | D3 | Annual, last 5 FY | $M | `BALANCE_SHEET(symbol=…)` |
| **working capital** | `chart-bar` | D3 | Annual, last 5 FY | $M | `BALANCE_SHEET(symbol=…)` |
| **total assets** | `chart-bar` | D3 | Annual, last 5 FY | $M | `BALANCE_SHEET(symbol=…)` |
| **P/E / EV/EBITDA / valuation multiples** | `chart-line` + ±1σ bands | matplotlib | Annual, last 5 FY | x | `OVERVIEW(symbol=…)` + `calculate` |
| **peer comparison** | `chart-bar` | D3 | Single period (latest) | % or $M | `INCOME_STATEMENT(symbol=…)` × N |

#### Dividends & Yield

> ⚠️ **Dividend data is NEVER present in `<stock_context>`.** Do NOT look for it there. Always call `get_dividend_history` first.

| User said | Chart type | Rendering | Time frame | Unit | First tool(s) to call |
|---|---|---|---|---|---|
| **dividend / dividend history / dividends paid** | `chart-bar` | D3 | All available (max) | $/share | `get_dividend_history(ticker=…, period="max")` |
| **dividend yield / yield history** | `chart-line` | D3 | Max available | % | `get_dividend_history(ticker=…)` + price from `TIME_SERIES_DAILY` |
| **quarterly dividend / quarterly payout** | `chart-bar` | D3 | Last 5 years of payments | $/share | `get_dividend_history(ticker=…, period="5y")` |
| **annual dividend / forward dividend** | `chart-bar` | D3 | Annual, last 5 FY | $/share | `get_dividend_history(ticker=…, period="5y")` — sum per calendar year |
| **payout ratio** | `chart-line` | D3 | Annual, last 5 FY | % | `get_dividend_history(ticker=…)` + `INCOME_STATEMENT(symbol=…)` |

#### Performance Reporting

| User said | Chart type | Rendering | Time frame | Unit | First tool(s) to call |
|---|---|---|---|---|---|
| **vs benchmark / composite vs benchmark** | `chart-bar` (annual) + `chart-line` (cumulative) | D3 | Annual last 5 FY / Daily last 3 yr | % | `TIME_SERIES_DAILY(symbol=…)` × 2 |
| **Sharpe ratio / information ratio** | horizontal `chart-bar` | D3 | Single period | ratio | `calculate` |
| **up/down capture** | scatter quadrant | matplotlib | Single period | % | `calculate` |

> **Assumption rule:** When you apply a default the user did not explicitly state (e.g. defaulting to 8 quarters),
> note it in **`chat`** in one sentence: "Defaulting to last 8 quarters — let me know if you want a different range."
> Then proceed immediately. Do not wait for confirmation.

---

## Overview

Turn raw financial or market data into a **rendered visual chart** embedded in the Thesis.
Never use ASCII bar art. Two rendering methods are available:

| Method | When to use | How |
|---|---|---|
| **D3 fenced block** (`chart-bar` / `chart-line`) | Any time-series or comparison chart | Emit a fenced code block — the frontend renders it as an interactive SVG |
| **`generate_chart_matplotlib`** tool | When a pre-rendered image is preferred | Call the tool — returns a markdown image tag with a base64 SVG data URI |

---

## Step 1 — Resolve data source and defaults

Call both skills in order:

1. `read_skill("data-source")` — identify the correct tool(s) to call, in priority order, for the data needed. Confirm whether the data exists in `<stock_context>` / `<acquired_data>` before making any API call.
2. `read_skill("standard-charts")` — extract chart type, rendering method, time frame, and unit for the requested metric.

From the combined output extract:
- **Chart type** (e.g. `chart-bar`, `chart-line`, matplotlib)
- **Rendering method** (D3 vs `generate_chart_matplotlib`)
- **Time frame** (e.g. Annual last 5 FY, Quarterly last 8 Q)
- **Unit** (e.g. `$M`, `%`, `$/share`)
- **Tool(s) to call** and their priority order
- **Field / derivation** (exact response key or computation)

You now have everything needed to proceed — do not ask the user to confirm any of these.

---

## Step 2 — Source the data

Follow this fallback chain in order. Move to the next step only if the current one yields fewer than 3 valid (non-None, numeric) data points.

### 2a — Use existing context (free, instant)

Check `<stock_context>` and `<acquired_data>`. Extract the required series.
If you find ≥ 3 valid periods → proceed to Step 3. Do not fetch anything.

### 2b — Fetch from Alpha Vantage (authoritative, ~1 API call)

Call the appropriate MCP tool by exact name with a `symbol` parameter, e.g.
`INCOME_STATEMENT(symbol="INDI")`. Never use TOOL_LIST, TOOL_GET, or TOOL_CALL.

| Need | Tool | Key fields |
|---|---|---|
| Revenue, gross profit, operating income | `INCOME_STATEMENT` | `annualReports[].totalRevenue`, `grossProfit`, `operatingIncome` |
| D&A, operating cash flow, capex | `CASH_FLOW` | `annualReports[].depreciationDepletionAndAmortization`, `operatingCashflow`, `capitalExpenditures` |
| Balance sheet items | `BALANCE_SHEET` | `annualReports[].totalAssets`, `totalLiabilities` |
| EPS by quarter | `EARNINGS` | `quarterlyEarnings[].reportedEPS` |
| Price history | `TIME_SERIES_DAILY` | `"Time Series (Daily)"[date]["4. close"]` |
| **Dividend payments & yield** | **`get_dividend_history(ticker, period)`** | **`dividendHistory[].date`, `dividendHistory[].amount`, `trailingAnnualDividendYield`, `trailingAnnualDividendRate`, `fiveYearAvgDividendYield`, `payoutRatio`** |

> **Dividend data is not available from Alpha Vantage or `<stock_context>`.** It is sourced exclusively via `get_dividend_history`. Call it directly — no fallback to `INCOME_STATEMENT` or `CASH_FLOW` for dividend values.

Both `INCOME_STATEMENT` and `CASH_FLOW` return `annualReports` and `quarterlyReports`
arrays — always iterate the array, never read a single top-level field.

**Error detection:** If the response contains an `"Information"`, `"Note"`, or
`"Error Message"` top-level key instead of `annualReports`/`quarterlyReports`,
or if the response body contains the string "Invalid API call", that is an API
error. Immediately report the exact error string in `chat`, then proceed to **2b-alt**.

If the tool returns data with ≥ 3 valid periods after skipping `"None"` values → proceed to Step 3.

If the tool returns all `"None"` / blank values → proceed to **2b-alt**.

### 2b-alt — INCOME_STATEMENT failed: reconstruct from CASH_FLOW

Use this step only when `INCOME_STATEMENT` returned an API error (already
reported in `chat` per Step 2b). `CASH_FLOW` is a separate Alpha Vantage
endpoint that frequently succeeds independently.

Call `CASH_FLOW(symbol="<ticker>")`. In the quarterly/annual reports, locate:
- `netIncome` — starting line of the indirect cash flow statement
- `depreciationDepletionAndAmortization` — D&A add-back

Compute a **EBITDA proxy**:
```
EBITDA proxy = netIncome + depreciationDepletionAndAmortization
```
This approximation omits explicit interest and tax add-backs, which are small
relative to D&A for most companies. Label the chart axis/title as
**"EBITDA (proxy)"** and note in `chat` that operating income
was unavailable so the proxy uses net income + D&A.

**Error detection for CASH_FLOW:** Apply the same check — if the response
contains `"Information"`, `"Note"`, or `"Error Message"` keys, report the
exact error in `chat` and proceed to the metric fallback below.

If `CASH_FLOW` also errors → try switching the metric:

**Metric fallback order** (when all income-statement endpoints fail):
1. `EARNINGS` → quarterly EPS — `quarterlyEarnings[].reportedEPS` (separate endpoint, rarely fails)
2. `OVERVIEW` → trailing EPS, P/E, revenue TTM as single-period fallback
3. → proceed to **2c** (ask user) only after all above fail

If the tool returns data with ≥ 3 valid periods after skipping `"None"` values → proceed to Step 3.

If the tool returns all `"None"` / blank values or an error → proceed to **2c**.

### 2c — Ask the user to provide data manually (last resort only)

Only reach here if both 2a and 2b failed to produce ≥ 3 valid data points.
Call `request_user_input` with a single, specific question:

> "The Alpha Vantage data for [metric] on [ticker] is unavailable or blank.
> Please paste the [annual/quarterly] figures (period and value) so I can render the chart."

Do not offer the user a choice of data source — that decision is made automatically by this fallback chain.

---

## Step 3 — Derive missing metrics

If a metric is not a named field, compute it from components:

```
EBITDA  = operatingIncome + depreciationDepletionAndAmortization
            (INCOME_STATEMENT)   (CASH_FLOW operatingActivities)

EBIT    = operatingIncome
  (or)  = grossProfit - totalOperatingExpenses

FCF     = operatingCashflow - capitalExpenditures  (both CASH_FLOW)

Gross Margin %   = grossProfit / totalRevenue x 100
Operating Margin = operatingIncome / totalRevenue x 100
Net Margin       = netIncome / totalRevenue x 100
```

**Rules:**
- If any component is `"None"` or blank, **skip that period** — do not abort the series.
- Annual view: use the last 4-5 fiscal years, oldest to newest left to right.
- Quarterly view: use the last 6-8 quarters.
- Values in the JSON must be **plain numbers** (not formatted strings like `"\.9B"`).

---

## Step 4 — Render the chart

### Method A — D3 fenced block (preferred)

Emit a fenced code block with language `chart-bar` or `chart-line`.
The content must be a single valid JSON object.

**`chart-bar` — vertical bar chart:**

```chart-bar
{
  "title": "EBITDA (Annual)",
  "unit": "",
  "data": [
    { "label": "FY2021", "value": 1900 },
    { "label": "FY2022", "value": 2600 },
    { "label": "FY2023", "value": 2400 },
    { "label": "FY2024", "value": 2500 },
    { "label": "FY2025", "value": 2800 }
  ]
}
```

**`chart-line` — line/area chart:**

```chart-line
{
  "title": "Revenue (Quarterly)",
  "unit": "",
  "color": "#4a90d9",
  "data": [
    { "label": "Q1-24", "value": 520 },
    { "label": "Q2-24", "value": 610 },
    { "label": "Q3-24", "value": 580 },
    { "label": "Q4-24", "value": 690 }
  ]
}
```

**ChartSpec schema:**

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | string | no | Chart heading |
| `unit` | string | no | Axis label / tooltip unit (e.g. `\`, `%`, `x`) |
| `color` | string | no | Positive bar / line color (default `#4a90d9`) |
| `negativeColor` | string | no | Negative bar color (default `#ef4444`) |
| `data` | array | **yes** | `[{ "label": string, "value": number }, ...]` |

- Use `\` for values >= 1000 (billions), `\` for millions, `%` for margins, `x` for multiples.
- Fewer than 3 data points: use a markdown table instead. Follow the time-series layout: periods as column headers (top), metric as row label (left). e.g. `| Metric | 2024-Q1 | 2024-Q2 | ... |` with values in the row below.
- Limit to ~20 bars / 60 line points for readability.

---

### Method B — `generate_chart_matplotlib` tool

Call when the user wants a rendered image or D3 blocks are unavailable.

Parameters:
- `series_json` — JSON string: `'[{"label":"FY2021","value":1900},...]'`
- `chart_type` — `"bar"` (default) or `"line"`
- `title` — chart heading
- `unit` — axis unit (e.g. `""`)

Returns a markdown image tag — paste verbatim into the `thesis` field.

---

## Step 5 — Embed in Thesis

The thesis entry for a chart is **exactly this structure and nothing else:**

```
## {MetricName} ({Annual/Quarterly})

{One or two sentence qualitative assessment of the trend. E.g. "Revenue has been broadly flat around $55M over the last six quarters, with modest sequential fluctuation." No numbers repeated as a list.}

```chart-bar
{ … }
```
```

Rules:
- The `##` section heading is mandatory.
- The assessment is **1–2 sentences max** — qualitative observation only (trend direction, notable inflection, key takeaway). No numbers, no lists.
- The chart fenced block immediately follows.
- **Nothing else.** No bullet list. No table. No "Latest N quarters:" header. No raw values. No notes.
- Append — **never replace** — existing thesis content.
- Return the **complete updated thesis** in the `thesis` JSON field.
- If data was too sparse to chart, note it in `chat` only; leave `thesis` unchanged.
- Any proxy/assumption note (e.g. "used EBITDA proxy") goes in `chat`, never in `thesis`.

**⛔ BANNED in thesis — these always go in `chat` instead:**
- Bullet list or numbered list of the data values
- Markdown table of the data values
- "Latest N quarters (USD, $M):" block
- "(negative values indicate losses)" or any parenthetical explanation
- Any sentence that restates the numbers already shown in the chart
- Mermaid fenced blocks (`xychart-beta`, `graph`, etc.) — always use `chart-bar` / `chart-line`

### Multi-series line chart format

Use this format when comparing 2+ tickers or segments on the same axis.
The `labels` array is the shared x-axis. Every `values` array must be the **same length** as `labels`. Use `null` for periods where a ticker has no data — the renderer draws a gap.

```chart-line
{
  "title": "Quarterly Revenue — Peer Comparison ($M)",
  "unit": "$M",
  "labels": ["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4", "2025-Q1"],
  "series": [
    { "label": "LAZR", "values": [20.97, 16.45, 15.49, 22.48, 18.89] },
    { "label": "INVZ", "values": [null,  null,  null,  6.03,  17.39] },
    { "label": "OUST", "values": [null,  null,  null,  30.09, 32.63] }
  ]
}
```

Key rules for multi-series:
- Always use `chart-line` (not `chart-bar`) for multi-series comparisons.
- Use `null` (not `0`, not `"N/A"`) for missing periods.
- Label values are the ticker symbols, not long names.
- Use the normalised period format consistently: `"YYYY-MM-DD"` from `fiscalDateEnding`, or short-form `"YYYY-QN"` if derived.

---

## Full example — EBITDA bar chart

1. **Step 1** — Call `read_skill("data-source")` first (tool priority + context check), then `read_skill("standard-charts")` (defaults). Resolved: `chart-bar`, annual last 5 FY, `$M`, tools = `INCOME_STATEMENT` + `CASH_FLOW`.
2. **Step 2a** — Check `<stock_context>` and `<acquired_data>` for `operatingIncome` and `depreciationDepletionAndAmortization` by year. If ≥ 3 valid pairs found, skip to step 4.
3. **Step 2b** — Call `INCOME_STATEMENT(symbol="AAPL")` and `CASH_FLOW(symbol="AAPL")`. Join by `fiscalDateEnding`. Compute `EBITDA = operatingIncome + D&A`. Skip periods where either is `"None"`. If ≥ 3 valid periods, proceed.
4. **Step 2b-alt** — If `INCOME_STATEMENT` errored: call `CASH_FLOW(symbol="AAPL")` alone. Compute proxy. Note in `chat`.
5. **Step 2c** — Only if still < 3 valid periods: ask user to paste figures.
6. **Step 3** — Derive: `EBITDA = operatingIncome + D&A`.
7. **Step 4** — Build `chart-bar` fenced block with 5 most recent fiscal years.
8. **Step 5** — Append to thesis in **exactly** this format:

```markdown
## EBITDA (Annual)

AAPL's EBITDA has expanded steadily from $110B in FY2021 to $135B in FY2025, driven by margin improvement and revenue growth.

\`\`\`chart-bar
{
  "title": "AAPL Annual EBITDA ($M)",
  "unit": "$M",
  "data": [
    { "label": "FY2021", "value": 110000 },
    { "label": "FY2022", "value": 119000 },
    { "label": "FY2023", "value": 124000 },
    { "label": "FY2024", "value": 130000 },
    { "label": "FY2025", "value": 135000 }
  ]
}
\`\`\`
```

That is the complete thesis addition — nothing before the heading, nothing after the chart block.

