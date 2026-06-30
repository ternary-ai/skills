---
name: portfolio-stress-test
description: Run scenario_stress_test() across all portfolio holdings simultaneously, aggregate P&L per scenario (market crash, rate shock, sector rotation, recession), and render results as a table showing portfolio-level stress impact.
---

# Portfolio Stress Test

Purpose: Quantify portfolio-level downside exposure across multiple adverse scenarios to assess resilience and identify vulnerabilities.

Trigger: User asks "stress test my portfolio", "worst case scenario", "portfolio in a crash", or uses `/portfolio-stress-test`.

## Data Flow

### 1. Load Portfolio
- Check `<current_portfolio>` first — skip tool call if present.
- Otherwise: `load_portfolio(portfolio_id)`.
- Extract holdings list with tickers, shares, and current market values.

### 2. Fetch Live Quotes & Metadata
- For each ticker: call `GLOBAL_QUOTE(ticker)` to get current price.
- For each ticker: call `OVERVIEW(ticker)` to get sector, beta, market cap.
- **Batch in parallel** — single plan step for all fetches.

### 3. Define Stress Scenarios

Use these standard scenarios unless user specifies custom:

| Scenario | Market (S&P) | Rates (10Y) | Sector Impact |
|---|---|---|---|
| **Market Crash** | -30% | -50bp | Tech -35%, Financials -40%, Defensive -20% |
| **Rate Shock** | -10% | +200bp | Growth -25%, Banks +5%, Utilities -15% |
| **Recession** | -20% | -100bp | Cyclicals -30%, Consumer Staples -10%, Healthcare -5% |
| **Sector Rotation** | +5% | +50bp | Growth -15%, Value +10%, Small Cap -20% |
| **Inflation Spike** | -15% | +150bp | Energy +15%, Materials +10%, Tech -20% |

### 4. Run Stress Test for Each Holding

For each ticker, call `scenario_stress_test(ticker, current_price, beta, sector, scenarios_json)`.

Input structure:
```json
{
  "ticker": "AAPL",
  "current_price": 185.00,
  "shares": 50,
  "beta": 1.2,
  "sector": "Technology",
  "scenarios": [
    {"name": "Market Crash", "market_move": -0.30, "rate_change": -0.005},
    {"name": "Rate Shock", "market_move": -0.10, "rate_change": 0.02}
  ]
}
```

Output from tool:
```json
{
  "Market Crash": {"price": 120.25, "value": 6012.50, "pnl": -3237.50, "pnl_pct": -35.0},
  "Rate Shock": {"price": 157.25, "value": 7862.50, "pnl": -1387.50, "pnl_pct": -15.0}
}
```

- **Batch all `scenario_stress_test()` calls in parallel** — single plan step.

### 5. Aggregate Portfolio-Level Results

For each scenario:
```
portfolio_pnl = sum(pnl for all holdings)
portfolio_pnl_pct = portfolio_pnl / total_portfolio_value × 100
new_portfolio_value = total_portfolio_value + portfolio_pnl
```

### 6. Render Output

**Stress Test Table** — use `render_table()`:
| Scenario | Portfolio P&L ($) | Portfolio P&L (%) | New Value | Worst Holding | Best Holding |
|---|---|---|---|---|---|
| Market Crash | -$6,500 | -34.1% | $12,550 | AAPL (-35%) | Cash (0%) |
| Rate Shock | -$2,800 | -14.7% | $16,250 | AAPL (-15%) | XOM (+5%) |
| Recession | -$4,200 | -22.0% | $14,850 | TSLA (-30%) | JNJ (-5%) |
| Sector Rotation | -$1,900 | -10.0% | $17,150 | AAPL (-15%) | BRK.B (+10%) |
| Inflation Spike | -$3,100 | -16.3% | $15,950 | AAPL (-20%) | XOM (+15%) |

**Vulnerability Analysis**:
- **Worst scenario**: {scenario} → portfolio drops {X}% (${Y}).
- **Best scenario**: {scenario} → portfolio drops only {X}% (${Y}).
- **Average stress impact**: {X}% decline.
- **Most vulnerable holding**: {ticker} (average {X}% decline across scenarios).
- **Most resilient holding**: {ticker} (average {X}% change across scenarios).

**Chart** — use `generate_chart()`:
- Type: `bar`
- Series: P&L % by scenario
- X-axis: Scenario name
- Y-axis: Portfolio P&L %
- Title: "Portfolio Stress Test — Scenario Impact"
- Colour: Red bars for negative, green for positive (if any).

### 7. Thesis Upsert — MANDATORY

**This is an advanced skill** → append stress test results to portfolio thesis. ⚠️ Extended thinking is discarded — copy the complete results into the `thesis` field; it is the ONLY output that reaches the Thesis panel.

Thesis structure:
```markdown
## Portfolio Stress Test — {Date}

{Stress test table}

{Chart spec}

### Vulnerability Summary
- **Worst case**: {scenario} → portfolio value drops to ${X} ({Y}%).
- **Average stress**: Portfolio loses {Z}% across 5 scenarios.
- **Most vulnerable**: {ticker} ({sector}) — average {A}% decline.
- **Most resilient**: {ticker} ({sector}) — average {B}% impact.

**Recommendation**: {One-line guidance — e.g. "Reduce Technology allocation to limit downside in Market Crash scenario."}
```

### 8. Chat Response

State in `chat` field:
- Number of scenarios tested.
- Worst-case scenario and impact ($ and %).
- Average portfolio decline across scenarios.
- Most vulnerable holding.
- Tools used: `load_portfolio`, `GLOBAL_QUOTE`, `OVERVIEW`, `scenario_stress_test` (N times), `render_table`, `generate_chart`.

## Cost Controls

- **Skip `load_portfolio()` if `<current_portfolio>` is present.**
- **Batch all quote and metadata fetches in parallel** — single plan step.
- **Batch all `scenario_stress_test()` calls in parallel** — one plan step for all holdings.
- **Reuse session cache** — don't refetch data already in `<acquired_data>`.

## Error Handling

- If `scenario_stress_test(ticker)` fails, assume that holding declines by the market beta × market move for that scenario and continue.
- If sector data missing from `OVERVIEW()`, classify as "Unknown" and apply market beta-only stress (no sector overlay).
- If all stress tests fail, fall back to simple beta-based calculation: `pnl = shares × price × beta × market_move`.

## Output Standards

- All dollar amounts formatted with commas: $1,234.56.
- Percentages with one decimal: -12.3%.
- Table must include all scenarios and a summary row (if applicable).
- Chart must show negative values as red bars, positive as green.
- Vulnerability analysis must name specific tickers and sectors.
