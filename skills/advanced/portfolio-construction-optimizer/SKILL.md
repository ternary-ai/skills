---
name: portfolio-construction-optimizer
description: Optimizes portfolio concentration and risk by evaluating sector exposure, factor correlations, and macro stress tests. Use when adding a new position or running a quarterly portfolio review.
---

# Portfolio Construction Optimizer

Purpose: Ensure concentration without fragility.

Trigger: New addition or quarterly review.

Inputs:
- Current holdings
- Sector weights
- Beta exposure
- Factor exposures

## Data Sources

Follow this order — do not ask the user which source to use:

1. **Context first**: Check `<stock_context>` and `<acquired_data>` for current
   holdings with weights, sector breakdown, and any prior factor analysis.
   If full holdings list with weights is present → proceed directly to Process.
2. **Fetch if missing**: Call:
   - `calculate_portfolio_exposure_map` — sector, factor, beta weights
   - `pca_factor_decomposition` — identify hidden correlation clusters
   - `GLOBAL_QUOTE` (per holding) — refresh current prices for accurate weights
3. **Ask only if both fail**: Call `request_user_input` asking for the specific
   missing field only (e.g. "Please paste your current holdings as ticker:
   weight pairs").

Process:
1. Evaluate top 5 concentration.
2. Stress test macro shocks: rate spike, liquidity freeze, demand collapse.
3. Identify hidden correlation clusters.

Output:
- Rebalancing recommendation
- Concentration health score

## Output Format

Write a portfolio optimization report in markdown format:

```markdown
## Portfolio Construction Analysis
**Analysis Date**: {Date}

### Current Portfolio Snapshot
- **Total Positions**: X
- **Top 5 Concentration**: X% of portfolio
- **Largest Position**: {TICKER} at X%
- **Cash Weight**: X%

### Concentration Analysis
| Position | Ticker | Weight | Sector | Conviction |
|----------|--------|--------|--------|------------|
| 1 | XXX | X% | [Sector] | [High/Med/Low] |
| 2 | XXX | X% | [Sector] | [High/Med/Low] |
| ... | | | | |

**Concentration Health Score**: X/10  
[Comments on whether concentration aligns with edge and conviction]

### Sector & Factor Exposure
- **Sector Breakdown**: [List major sector allocations]
- **Factor Exposures**: [Growth/Value, Quality, Momentum, Size]
- **Hidden Correlations**: [Identify positions that move together despite different sectors]

### Stress Test Results
**Scenario 1: Rate Spike (+200 bps)**  
Portfolio Impact: -X%  
Most Vulnerable: [Tickers]

**Scenario 2: Liquidity Freeze (credit spreads widen 300 bps)**  
Portfolio Impact: -X%  
Most Vulnerable: [Tickers]

**Scenario 3: Demand Collapse (recession, -5% GDP)**  
Portfolio Impact: -X%  
Most Vulnerable: [Tickers]

### Rebalancing Recommendations
1. **[Trim/Increase] {TICKER}**: Current X% → Target Y% [Reason]
2. **[Trim/Increase] {TICKER}**: Current X% → Target Y% [Reason]
3. **Sector Adjustment**: [Over/underweight sector, target shift]

### Optimal Portfolio Structure
[One paragraph describing the recommended adjustments to improve concentration-conviction alignment, reduce hidden correlation risk, and enhance portfolio resilience.]
```

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete portfolio construction analysis. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete analysis into the `thesis` field; it is the ONLY output that reaches the Thesis panel.
