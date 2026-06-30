---
name: capital-preservation-protocol
description: Protects against permanent capital loss by stress-testing aggregate exposure and restructuring fragile positions. Use when portfolio drawdown exceeds a risk threshold or leverage becomes elevated.
---

# Capital Preservation Protocol

Purpose: Avoid permanent capital loss.

Trigger: Portfolio drawdown threshold breach.

Inputs:
- Aggregate exposure
- Leverage
- Liquidity profile

## Data Sources

Follow this order — do not ask the user which source to use:

1. **Context first**: Check `<stock_context>` and `<acquired_data>` for current
   portfolio weights, leverage ratio, and cash/liquid reserves.
   If aggregate exposure and liquidity data are present → proceed directly to Process.
2. **Fetch if missing**: Call:
   - `calculate_liquidity_profile` — cash buffer, liquid vs illiquid breakdown
   - `calculate_portfolio_exposure_map` — gross/net exposure, sector concentration
   - `GLOBAL_QUOTE` (per holding) — refresh prices for accurate NAV
3. **Ask only if both fail**: Call `request_user_input` asking for the specific
   missing field only (e.g. "Please provide your current leverage ratio and
   cash balance as % of portfolio").

Process:
1. Stress test extreme downside.
2. Reduce fragile positions.
3. Increase liquidity buffer.
4. Protect core high-conviction holdings.

Output:
- Defensive restructuring plan

## Output Format

Write a capital preservation analysis in markdown format:

```markdown
## Capital Preservation Protocol
**Analysis Date**: {Date}  
**Risk Environment**: [Benign / Elevated / Crisis]

### Portfolio Risk Assessment
- **Total Equity Exposure**: X%
- **Gross Leverage**: X.Xx
- **Net Exposure**: X%
- **Largest Position**: {TICKER} at X%
- **Top 5 Concentration**: X%

### Stress Test Results
**Worst-Case Portfolio Drawdown**: -X%  
[Assumes: market down -30%, factor correlation increases, liquidity dries up]

**Position at Risk**:  
- **Capital**: $X  
- **% of Portfolio**: X%

### Fragile Positions Identified
[Positions that fail stress tests — high beta, illiquid, overleveraged, binary event risk]

| Ticker | Issue | Current Weight | Action |
|--------|-------|----------------|--------|
| XXX | [High beta, illiquid] | X% | Trim to Y% |
| XXX | [Binary event risk] | X% | Exit |

### Restructuring Plan
1. **Reduce gross exposure**: X% → Y%
2. **Trim concentrated positions**: [List tickers and target weights]
3. **Increase cash buffer**: X% → Y%  
4. **Add hedges**: [VIX calls, put spreads, rate hedges — if applicable]

### Exposure Limits (Updated)
- **Max single position**: X%
- **Max sector**: X%
- **Max gross leverage**: X.Xx
- **Min cash reserve**: X%

### Implementation Timeline
[Immediate / Over X days — considering liquidity and market impact]

### Monitoring Triggers
[Set alerts: if portfolio down -X%, if volatility exceeds X, if liquidity metric degrades]
```

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete capital preservation analysis. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete analysis into the `thesis` field; it is the ONLY output that reaches the Thesis panel.
