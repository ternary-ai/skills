---
name: portfolio-risk-report
description: Analyse portfolio holdings for concentration risk, sector exposure, factor correlations, and flag breaches (>20% single name, >40% single sector). Uses calculate_portfolio_exposure_map() and generates risk breakdown table.
---

# Portfolio Risk Report

Purpose: Identify concentration breaches, sector imbalances, and factor exposures across all portfolio holdings.

Trigger: User asks "portfolio risk", "check concentration", "risk exposure", or uses `/portfolio-risk-report`.

## Data Flow

### 1. Load Portfolio
- Check `<current_portfolio>` first — skip tool call if present.
- Otherwise: `load_portfolio(portfolio_id)`.
- Extract holdings list with tickers and current weights.

### 2. Fetch Quote Data for Weights (if not in context)
- If weights are not already computed: fetch `GLOBAL_QUOTE(ticker)` for each holding to calculate current market value and weight %.
- Re-use from session cache if available.

### 3. Fetch Metadata for Each Holding
- For each ticker, call `OVERVIEW(ticker)` to get:
  - Sector
  - Industry
  - Market cap (classify as Large/Mid/Small)
  - Beta (factor exposure)
- **Batch in parallel** — plan step: "Fetch OVERVIEW for all N tickers."

### 4. Run Exposure Map
- Call `calculate_portfolio_exposure_map(holdings_json)` where `holdings_json` is:
  ```json
  [
    {"ticker": "AAPL", "weight": 0.486, "sector": "Technology", "beta": 1.2},
    {"ticker": "MSFT", "weight": 0.499, "sector": "Technology", "beta": 1.1}
  ]
  ```
- Tool returns:
  - Sector exposure breakdown (% per sector).
  - Factor exposure (aggregate beta, volatility).
  - Geographic exposure (if data available).

### 5. Flag Concentration Breaches

**Single Name Risk:**
- If any holding > 20% → **WARNING**: "Over-concentrated in {ticker} ({weight}%)."
- If any holding > 30% → **CRITICAL**: "Dangerous concentration in {ticker} ({weight}%)."

**Sector Risk:**
- If any sector > 40% → **WARNING**: "Over-concentrated in {sector} sector ({weight}%)."
- If any sector > 60% → **CRITICAL**: "Dangerous sector concentration in {sector} ({weight}%)."

**Factor Risk:**
- If portfolio beta > 1.5 → **WARNING**: "High market sensitivity (β={beta})."
- If portfolio beta < 0.5 → **NOTE**: "Low market correlation (β={beta})."

### 6. Render Output

**Concentration Table** — use `render_table()`:
| Ticker | Weight % | Sector | Beta | Flag |
|---|---|---|---|---|
| AAPL | 48.6% | Technology | 1.2 | — |
| MSFT | 49.9% | Technology | 1.1 | — |
| Cash | 1.6% | Cash | 0.0 | — |

**Sector Exposure Table**:
| Sector | Weight % | Flag |
|---|---|---|
| Technology | 98.4% | ⚠️ CRITICAL |
| Cash | 1.6% | — |

**Factor Summary**:
- Portfolio Beta: 1.15
- Estimated Volatility: 22% annualised
- Correlation to S&P 500: 0.85

### 7. Thesis Upsert — MANDATORY

**This is an advanced skill** → append the risk report to the portfolio thesis. ⚠️ Extended thinking is discarded — copy the complete report into the `thesis` field; it is the ONLY output that reaches the Thesis panel.

Thesis structure:
```markdown
## Portfolio Risk Report — {Date}

### Concentration Analysis
{Concentration table}

### Sector Exposure
{Sector table}

### Factor Risk
- Portfolio Beta: {beta}
- Volatility: {vol}%
- Correlation: {corr}

**Flags:**
- {List all warnings/critical flags}

**Recommendation**: {One-line guidance — e.g. "Rebalance to reduce Technology concentration below 40%."}
```

### 8. Chat Response

State in `chat` field:
- Number of holdings analysed.
- Concentration breaches (if any).
- Sector exposure summary (top 2 sectors).
- Portfolio beta.
- Tools used: `load_portfolio`, `OVERVIEW` (N times), `calculate_portfolio_exposure_map`, `render_table`.

## Cost Controls

- **Skip `load_portfolio()` if `<current_portfolio>` is present.**
- **Batch `OVERVIEW()` calls in parallel** — single plan step for all tickers.
- **Reuse data from session cache** — if `OVERVIEW` or quote already fetched this session, skip refetch.

## Error Handling

- If `OVERVIEW(ticker)` fails, set sector = "Unknown" and beta = 1.0 (market neutral assumption).
- If `calculate_portfolio_exposure_map()` errors, fall back to manual aggregation: sum weights by sector from `OVERVIEW` results.

## Output Standards

- All weights as percentages with one decimal: 12.3%.
- Beta with two decimals: 1.15.
- Volatility as annualised percentage: 22%.
- Flags: Use ⚠️ for WARNING, 🔴 for CRITICAL.
- Tables must include subtotals for each category (e.g. total sector exposure = 100%).
