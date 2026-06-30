---
name: portfolio-performance-attribution
description: Delegate to the existing performance-attribution-error-analysis skill per holding, then roll up into a portfolio-level summary showing which positions contributed positively/negatively, factor attribution, and decision error patterns.
---

# Portfolio Performance Attribution

Purpose: Decompose portfolio returns into per-holding contributions, factor exposures, and decision errors to understand what drove performance.

Trigger: User asks "portfolio performance", "what drove my returns", "attribution analysis", or uses `/portfolio-performance-attribution`.

## Data Flow

### 1. Load Portfolio & Determine Time Period
- Check `<current_portfolio>` first — skip tool call if present.
- Otherwise: `load_portfolio(portfolio_id)`.
- Extract holdings with cost basis and current shares.

**Time Period:**
- If user specifies "YTD", "last month", "last quarter", "last year" → parse and use.
- **Default if unspecified**: YTD (year-to-date) from Jan 1 to today.

### 2. Fetch Historical Prices for Each Holding
- For each ticker: call `PRICE_HISTORY(ticker, start=period_start, end=today)` to get daily OHLCV.
- For each ticker: call `GLOBAL_QUOTE(ticker)` to get current price.
- **Batch in parallel** — single plan step for all price fetches.

### 3. Compute Per-Holding Returns

For each holding:
```
price_start = closing price on period_start date (or avg_cost if later)
price_end = current_price
total_return = (price_end - price_start) / price_start × 100
contribution = (shares × price_end - shares × price_start) / total_portfolio_value_start × 100
```

**Holding contribution to portfolio return = contribution %.**

### 4. Factor Attribution — Call Existing Skill

For each holding, delegate to `performance-attribution-error-analysis` skill:
- Call `read_skill("performance-attribution-error-analysis")`.
- Execute the skill for each ticker over the same time period.
- Tool will return:
  - Market factor contribution (beta × market return).
  - Sector factor contribution.
  - Alpha (stock-specific return).
  - Decision errors (if buy/sell signals were evaluated).

**Batch skill execution in a single plan step** — "Run performance attribution for all N holdings."

### 5. Aggregate Portfolio-Level Attribution

Sum contributions across all holdings:
```
Total Portfolio Return = sum(contribution for all holdings)
Market Factor = sum(market_contribution for all holdings)
Sector Factor = sum(sector_contribution for all holdings)
Alpha = sum(alpha for all holdings)
```

Residual = Total Return - (Market + Sector + Alpha).

### 6. Render Output

**Per-Holding Performance Table** — use `render_table()`:
| Ticker | Start Price | End Price | Total Return % | Contribution to Portfolio % | Market Factor | Alpha |
|---|---|---|---|---|---|---|
| AAPL | $170.00 | $185.00 | +8.8% | +4.3% | +3.5% | +5.3% |
| MSFT | $350.00 | $380.00 | +8.6% | +4.2% | +3.5% | +5.1% |
| TSLA | $200.00 | $175.00 | -12.5% | -1.2% | +3.5% | -16.0% |
| **Total** | — | — | **+7.8%** | **+7.3%** | **+10.5%** | **-5.6%** |

**Factor Attribution Summary**:
- **Market Factor**: +10.5% (beta-weighted S&P 500 return).
- **Sector Factor**: +2.4% (overweight Technology vs benchmark).
- **Alpha (Stock Selection)**: -5.6% (underperformance vs sector).
- **Residual**: +0.5% (unexplained).

**Top Contributors**:
1. AAPL: +4.3% (strong alpha, +5.3%).
2. MSFT: +4.2% (strong alpha, +5.1%).
3. Cash: +0.0% (no contribution).

**Top Detractors**:
1. TSLA: -1.2% (negative alpha, -16.0%).

**Chart** — use `generate_chart()`:
- Type: `bar`
- Series: Contribution % by holding
- X-axis: Ticker
- Y-axis: Contribution %
- Title: "{Portfolio Name} — Performance Contribution ({Period})"
- Colour: Green for positive, red for negative.

### 7. Decision Error Analysis (Optional)

If the `performance-attribution-error-analysis` skill identifies decision errors for individual holdings:
- Aggregate error types across all holdings:
  - Confirmation bias (held losers too long).
  - Recency bias (chased momentum).
  - Premature exit (sold winners too early).
- Report the most common error pattern.

Example:
- **Most common error**: Premature exit (sold 2 winners early, left $X on table).
- **Worst single error**: Held TSLA through -16% decline (cost $Y).

### 8. Thesis Upsert — MANDATORY

**This is an advanced skill** → append performance attribution to portfolio thesis. ⚠️ Extended thinking is discarded — copy the complete report into the `thesis` field; it is the ONLY output that reaches the Thesis panel.

Thesis structure:
```markdown
## Portfolio Performance Attribution — {Period} — {Date}

**Total Portfolio Return**: +{X}% (${Y})

{Per-holding performance table}

{Chart spec}

### Factor Attribution
- **Market Factor**: +{A}% (portfolio beta × S&P 500 return)
- **Sector Factor**: +{B}% (overweight {sector})
- **Alpha (Stock Selection)**: +{C}%
- **Residual**: +{D}%

### Top Contributors
1. {ticker}: +{X}% contribution ({reason})
2. {ticker}: +{Y}% contribution ({reason})

### Top Detractors
1. {ticker}: -{X}% contribution ({reason})

### Decision Errors
- {Most common error pattern}
- {Costliest single error}

**Key Insight**: {One sentence — e.g. "Strong market factor offset by weak stock selection; TSLA drag was largest single detractor."}
```

### 9. Chat Response

State in `chat` field:
- Time period analysed.
- Total portfolio return ($ and %).
- Market factor contribution vs alpha.
- Top contributor and top detractor.
- Decision error summary (if any).
- Tools used: `load_portfolio`, `PRICE_HISTORY` (N times), `GLOBAL_QUOTE`, `read_skill` (performance-attribution-error-analysis), `render_table`, `generate_chart`.

## Cost Controls

- **Skip `load_portfolio()` if `<current_portfolio>` is present.**
- **Batch `PRICE_HISTORY()` calls in parallel** — single plan step for all holdings.
- **Reuse session cache** — don't refetch price data already in `<acquired_data>`.
- **Delegate to existing skill** — don't reimplement performance attribution logic; use `performance-attribution-error-analysis` per holding.

## Error Handling

- If `PRICE_HISTORY(ticker)` fails for a holding, use `avg_cost` as start price and current quote as end price; note estimation in `chat`.
- If `performance-attribution-error-analysis` skill fails for a ticker, compute simple return attribution only (no factor decomposition) and continue.
- If period_start predates the holding's `added_at` date, use `added_at` as start and note partial period in `chat`.

## Output Standards

- All percentages with one decimal: 12.3%.
- Dollar amounts formatted with commas: $1,234.56.
- Table must include a Total row summarising portfolio-level metrics.
- Chart must show both positive and negative contributions.
- Factor attribution must sum to Total Return (within ±1% residual tolerance).
