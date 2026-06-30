---
name: standard-charts
description: Canonical defaults for every common investment research chart. Read this before charting to determine chart type, time frame, unit, and data source without asking the user. Use as a lookup table inside chart-writeup.
---

# Standard Charts

This skill is a **defaults lookup table**. When a user asks for a chart without
specifying type, time frame, or unit, apply the row below that matches the metric.
Do not ask the user — use the default. Only ask (`request_user_input`) if the user's
request is genuinely ambiguous between two *different* metrics (e.g. "revenue or EBITDA?").

---

## Rendering method guide

| Frontend token | Backend tool | Supported shapes |
|---|---|---|
| `chart-bar` fenced block | D3 (interactive SVG) | Vertical bar, negative bars auto-colored red |
| `chart-line` fenced block | D3 (interactive SVG) | Line/area, single series |
| `generate_chart_matplotlib` | Python (base64 SVG) | Everything else: scatter, histogram, heatmap, candlestick, pie/donut, stacked bar, waterfall, area, dual-axis |

Use D3 fenced blocks whenever the shape is `bar` or `line`. Use `generate_chart_matplotlib` for all other shapes.

---

## Color conventions (apply automatically)

- **Positive / gains / long** → `#22c55e` (green)
- **Negative / losses / short / drawdown** → `#ef4444` (red)
- **Neutral / benchmark / index** → `#94a3b8` (blue-gray)
- **Primary series** → `#4a90d9` (blue, default)
- **Forecast / estimate** → lighter shade of the primary color or dashed line

---

## Axis & formatting conventions (apply automatically)

- Time series: time always on x-axis, oldest left → newest right
- Percentages: label axis `%`, values as plain numbers (e.g. `42.3` not `0.423`)
- Large numbers: abbreviate with K / M / B suffix (see Unit scaling rules below)
- Bar charts: always include zero baseline on y-axis
- Dual y-axes: only acceptable for price + volume; avoid all other combos
- Positive/negative bars: positive green (`#22c55e`), negative red (`#ef4444`) by convention

---

## Defaults Table

### Price & Market Data

| Metric (user may say…) | Chart type | Rendering | Time frame | Unit | Tools needed | Field / derivation |
|---|---|---|---|---|---|---|
| **Stock price / price history** | `chart-line` | D3 | Daily, last 1 year | $ | `TIME_SERIES_DAILY` | `"Time Series (Daily)"[date]["4. close"]` |
| **Price vs. benchmark / relative performance** | `chart-line` (dual series, indexed to 100) | D3 | Daily, last 1 year | index | `TIME_SERIES_DAILY` × 2 tickers | Both series normalized to 100 at start |
| **Intraday price** | `chart-line` | D3 | Intraday (1-day) | $ | `TIME_SERIES_INTRADAY` | `"Time Series (5min)"[datetime]["4. close"]` |
| **Volume** | `chart-bar` (below price) | D3 | Daily, last 3 months | shares | `TIME_SERIES_DAILY` | `"Time Series (Daily)"[date]["5. volume"]` |
| **Candlestick / OHLC** | candlestick | matplotlib | Daily, last 6 months | $ | `TIME_SERIES_DAILY` | open/high/low/close per day |
| **Moving averages (SMA/EMA)** | `chart-line` overlaid | D3 | Daily, last 1 year | $ | `TIME_SERIES_DAILY` | Compute SMA-50, SMA-200 from close prices |

### Returns

| Metric (user may say…) | Chart type | Rendering | Time frame | Unit | Tools needed | Field / derivation |
|---|---|---|---|---|---|---|
| **Cumulative returns / total return** | `chart-line` | D3 | Daily, last 1–5 years | % (indexed to 0%) | `TIME_SERIES_DAILY` | `(price_t / price_0 − 1) × 100` |
| **Monthly / periodic returns** | `chart-bar` (green/red) | D3 | Monthly, last 2 years | % | `TIME_SERIES_DAILY` | Month-end close pct change; positive green, negative red |
| **Return distribution** | histogram | matplotlib | Daily, last 2 years | % | `TIME_SERIES_DAILY` | Daily log returns; optional normal overlay |
| **Rolling returns** | `chart-line` | D3 | Daily with rolling window | % | `TIME_SERIES_DAILY` | Rolling N-day return; x-axis = window end date |
| **Drawdown** | area chart (red fill below zero) | matplotlib | Daily, last 1–5 years | % | `TIME_SERIES_DAILY` | `(price_t / rolling_max − 1) × 100`; shaded red |

### Risk & Volatility

| Metric (user may say…) | Chart type | Rendering | Time frame | Unit | Tools needed | Field / derivation |
|---|---|---|---|---|---|---|
| **Volatility / realized vol** | `chart-line` | D3 | Daily, last 1 year (rolling 30-day) | % annualized | `TIME_SERIES_DAILY` | `std(daily_returns) × √252 × 100` |
| **VaR (Value at Risk)** | `chart-bar` | D3 | Point-in-time or rolling | % or $ | `TIME_SERIES_DAILY` + `calculate` | 95%/99% confidence; label interval |
| **Correlation matrix** | heatmap | matplotlib | Single period | −1 to +1 | `TIME_SERIES_DAILY` × N tickers | Pearson correlations; red(−1)→white(0)→green(+1) |
| **Beta vs. market** | scatter + regression line | matplotlib | Daily, last 1 year | — | `TIME_SERIES_DAILY` × ticker + benchmark | Security returns on y, market on x |
| **Risk/return tradeoff** | scatter | matplotlib | Single period | % | `TIME_SERIES_DAILY` × N tickers | σ on x-axis, return on y-axis |

### Portfolio & Allocation

| Metric (user may say…) | Chart type | Rendering | Time frame | Unit | Tools needed | Field / derivation |
|---|---|---|---|---|---|---|
| **Asset allocation / portfolio weights** | donut chart | matplotlib | Current snapshot | % | context / `calculate_portfolio_exposure_map` | Weights by position or sector |
| **Allocation over time** | stacked area (100%) | matplotlib | Monthly/quarterly | % | context | Weights history; time on x-axis |
| **Factor exposure** | horizontal bar (pos/neg from center) | matplotlib | Current | z-score or % | `pca_factor_decomposition` | Positive right, negative left |
| **Attribution (Brinson)** | waterfall | matplotlib | Period | % or bps | `calculate` | Contribution of each sleeve to total return |

### Financial Statements & Fundamentals

| Metric (user may say…) | Chart type | Rendering | Time frame | Unit | Tools needed | Field / derivation |
|---|---|---|---|---|---|---|
| **Revenue** (revenue, sales, top line) | `chart-bar` | D3 | Annual, last 5 FY | $M or $B | `INCOME_STATEMENT` | `totalRevenue` |
| **Revenue — quarterly** | `chart-bar` | D3 | Quarterly, last 8 Q | $M or $B | `INCOME_STATEMENT` | `quarterlyReports[].totalRevenue` |
| **Revenue growth rate** | `chart-line` | D3 | Annual, last 5 FY | % | `INCOME_STATEMENT` | `(rev_t / rev_{t−1} − 1) × 100` |
| **Gross Profit** | `chart-bar` | D3 | Annual, last 5 FY | $M | `INCOME_STATEMENT` | `grossProfit` |
| **Gross Margin** | `chart-line` | D3 | Annual, last 5 FY | % | `INCOME_STATEMENT` | `grossProfit / totalRevenue × 100` |
| **EBITDA — annual** | `chart-bar` | D3 | Annual, last 5 FY | $M | `INCOME_STATEMENT` + `CASH_FLOW`; fallback: `CASH_FLOW` only | `operatingIncome + D&A`; proxy: `netIncome + interestExpense + incomeTaxExpense + D&A` (⚠️ understated if those fields absent) |
| **EBITDA — quarterly** | `chart-bar` | D3 | Quarterly, last 8 Q | $M | `INCOME_STATEMENT` + `CASH_FLOW`; fallback: `CASH_FLOW` only | same, `quarterlyReports[]` |
| **EBIT / Operating Income** | `chart-bar` | D3 | Annual, last 5 FY | $M | `INCOME_STATEMENT` | `operatingIncome` |
| **Operating Margin** | `chart-line` | D3 | Annual, last 5 FY | % | `INCOME_STATEMENT` | `operatingIncome / totalRevenue × 100` |
| **Net Income** (earnings, profit) | `chart-bar` | D3 | Annual, last 5 FY | $M | `INCOME_STATEMENT` | `netIncome` |
| **Net Income — quarterly** | `chart-bar` | D3 | Quarterly, last 8 Q | $M | `INCOME_STATEMENT` | `quarterlyReports[].netIncome` |
| **Net Margin** | `chart-line` | D3 | Annual, last 5 FY | % | `INCOME_STATEMENT` | `netIncome / totalRevenue × 100` |
| **Margins combined** (gross + EBITDA + net) | `chart-line` (3 series) | D3 | Annual, last 5 FY | % | `INCOME_STATEMENT` + `CASH_FLOW` | Three overlaid lines |
| **EPS** (earnings per share) | `chart-bar` | D3 | Quarterly, last 8 Q | $ | `EARNINGS` | `quarterlyEarnings[].reportedEPS` |
| **EPS actual vs. estimate** | bar (actual) + line (estimate) | matplotlib | Quarterly, last 8 Q | $ | `EARNINGS` | `reportedEPS` (bars) vs `estimatedEPS` (line/dots) |
| **FCF** (free cash flow) | `chart-bar` | D3 | Annual, last 5 FY | $M | `CASH_FLOW` | `operatingCashflow − capitalExpenditures` |
| **FCF yield** | `chart-line` | D3 | Annual, last 5 FY | % | `CASH_FLOW` + `OVERVIEW` | `FCF / marketCap × 100` |
| **Operating Cash Flow** | `chart-bar` | D3 | Annual, last 5 FY | $M | `CASH_FLOW` | `operatingCashflow` |
| **CapEx** | `chart-bar` | D3 | Annual, last 5 FY | $M | `CASH_FLOW` | `capitalExpenditures` (negate if negative) |
| **Balance sheet composition** | stacked bar (assets vs liabilities+equity) | matplotlib | Annual, last 5 FY | $M | `BALANCE_SHEET` | `totalAssets` vs `totalLiabilities` + `totalShareholderEquity` |
| **Total Debt / Net Debt** | `chart-bar` | D3 | Annual, last 5 FY | $M | `BALANCE_SHEET` | `shortLongTermDebtTotal` or `longTermDebt + shortTermDebt` |
| **Cash & Equivalents** | `chart-bar` | D3 | Annual, last 5 FY | $M | `BALANCE_SHEET` | `cashAndCashEquivalentsAtCarryingValue` |
| **Current Assets** | `chart-bar` | D3 | Annual, last 5 FY | $M | `BALANCE_SHEET` | `totalCurrentAssets` |
| **Current Assets — quarterly** | `chart-bar` | D3 | Quarterly, last 8 Q | $M | `BALANCE_SHEET` | `quarterlyReports[].totalCurrentAssets` |
| **Current Liabilities** | `chart-bar` | D3 | Annual, last 5 FY | $M | `BALANCE_SHEET` | `totalCurrentLiabilities` |
| **Working Capital** | `chart-bar` | D3 | Annual, last 5 FY | $M | `BALANCE_SHEET` | `totalCurrentAssets − totalCurrentLiabilities` |
| **Total Assets** | `chart-bar` | D3 | Annual, last 5 FY | $M | `BALANCE_SHEET` | `totalAssets` |
| **Valuation multiples (P/E, EV/EBITDA, P/S)** | `chart-line` with ±1σ bands | matplotlib | Annual, last 5 FY | x | `OVERVIEW` + `calculate` | Forward P/E or trailing; mean ± 1σ bands |
| **Revenue + Margins** (combined) | `chart-bar` revenue + `chart-line` margin | D3 (two charts) | Annual, last 5 FY | $M / % | `INCOME_STATEMENT` | Two separate chart blocks |
| **Peer comparison** (vs peers) | `chart-bar` | D3 | Single period (latest) | % or $M | `INCOME_STATEMENT` × N tickers | Same metric across tickers |

### Dividends & Yield

> ⚠️ **Dividend data is never present in `<stock_context>` or in any Alpha Vantage endpoint.** Always call `get_dividend_history(ticker, period)` — never ask the user, never fall back to `INCOME_STATEMENT` or `CASH_FLOW` for dividend values.

| Metric (user may say…) | Chart type | Rendering | Time frame | Unit | Tools needed | Field / derivation |
|---|---|---|---|---|---|---|
| **Dividend history / dividends paid** | `chart-bar` | D3 | All available (max) | $/share | `get_dividend_history(ticker, period="max")` | `dividendHistory[].amount` (y-axis), `dividendHistory[].date` (x-axis) |
| **Quarterly dividend / quarterly payout** | `chart-bar` | D3 | Last 5 years of payments | $/share | `get_dividend_history(ticker, period="5y")` | `dividendHistory[].amount` |
| **Annual dividend / annual DPS** | `chart-bar` | D3 | Per calendar year, last 5 years | $/share | `get_dividend_history(ticker, period="5y")` | Sum `dividendHistory[].amount` per calendar year |
| **Dividend yield / yield history** | `chart-line` | D3 | Annual, last 5 years | % | `get_dividend_history(ticker)` + `TIME_SERIES_DAILY` | `(annual_DPS / year_end_price) × 100` |
| **Trailing annual yield** | single-value callout | — | Point-in-time | % | `get_dividend_history(ticker)` | `trailingAnnualDividendYield × 100` |
| **Trailing annual rate** | single-value callout | — | Point-in-time | $/share | `get_dividend_history(ticker)` | `trailingAnnualDividendRate` |
| **5-year average yield** | single-value callout | — | Point-in-time | % | `get_dividend_history(ticker)` | `fiveYearAvgDividendYield` |
| **Payout ratio** | `chart-line` | D3 | Annual, last 5 FY | % | `get_dividend_history(ticker)` + `INCOME_STATEMENT` | `annual_DPS / EPS × 100` or `payoutRatio` directly |

### Performance Reporting

| Metric (user may say…) | Chart type | Rendering | Time frame | Unit | Tools needed | Field / derivation |
|---|---|---|---|---|---|---|
| **Composite vs. benchmark (annual)** | grouped `chart-bar` | D3 | Annual, last 5 FY | % | `TIME_SERIES_DAILY` × 2 | Annual returns side-by-side |
| **Composite vs. benchmark (cumulative)** | `chart-line` (2 series) | D3 | Daily, last 3–5 years | % | `TIME_SERIES_DAILY` × 2 | Both indexed to 0% |
| **Sharpe / information ratio** | horizontal `chart-bar` | D3 | Single period | ratio | `calculate` | Peer comparison; horizontal |
| **Up/down capture ratio** | scatter (quadrant) | matplotlib | Single period | % | `calculate` | Up capture on y, down capture on x |

---

## Unit scaling rules

Apply automatically — never ask the user:

- Value ≥ 1 000 000 M (i.e. ≥ 1 000 B) → express in **$T** (trillions)
- Value ≥ 1 000 M → express in **$B**, e.g. `"unit": "$B"`, divide values by 1000
- Value ≥ 1 M → express in **$M**, e.g. `"unit": "$M"`
- Value ≥ 1 000 (raw $) → express in **$K**, e.g. `"unit": "$K"`, divide by 1000
- Margins / ratios → `"unit": "%"`, values as plain percentages (e.g. `42.3` not `0.423`)
- EPS → `"unit": "$"`, values as reported (e.g. `1.84`)
- Multiples (EV/EBITDA, P/E) → `"unit": "x"`, values as plain numbers
- Index (price-indexed to 100, cumulative returns from 0) → `"unit": ""`, label in title

---

## Time frame rules

- **Annual default**: use the 5 most recent `annualReports`, oldest → newest
- **Quarterly default** (EPS, revenue growth): use the 8 most recent `quarterlyReports`
- **Never mix annual and quarterly** in the same series
- If fewer than 3 valid periods exist after skipping Nones → emit a markdown table instead

---

## Workflow (when invoked from chart-writeup)

1. Match the user's metric request to a row in the Defaults Table above.
2. Note the Chart type, Time frame, Unit, and Tools needed.
3. Return to `chart-writeup` Step 1 and proceed with those defaults.
4. Do **not** ask the user to confirm type, unit, or time frame — proceed directly.
