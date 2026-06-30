---
name: position-sizing-concentration
description: Recommends position size and concentration tier based on expected IRR, downside scenario, liquidity, and current portfolio exposure. Use after an investment idea passes triage and underwriting.
---

# Position Sizing & Concentration Logic

Purpose: Determine optimal capital allocation.

Trigger: Post-approval investment decision.

Inputs:
- Expected IRR
- Downside case
- Liquidity profile
- Portfolio exposure map

## Data Sources

Follow this order — do not ask the user which source to use:

1. **Context first**: Check `<stock_context>` and `<acquired_data>` for expected
   IRR, downside scenario value, current portfolio holdings and weights.
   If IRR estimate and portfolio exposure are present → proceed directly to Process.
2. **Fetch if missing**: Call:
   - `calculate_portfolio_exposure_map` — sector, factor, and position weights
   - `calculate_irr` — if IRR has not been computed already
   - `GLOBAL_QUOTE` — current price to anchor the downside case
3. **Ask only if both fail**: Call `request_user_input` asking for the specific
   missing field only (e.g. "Please provide your expected IRR and downside
   price target for this position").

Process:
1. Compute expected value.
2. Evaluate correlation to existing holdings.
3. Apply tier sizing model:
   - 2–3% exploratory
   - 5–7% high conviction
   - 10%+ asymmetric core
4. Simulate portfolio drawdown impact.

## Output Format

Write a dedicated thesis section in markdown format as follows:

```markdown
## Position Sizing Analysis
**Analysis Date**: {Date}

### Recommended Sizing
- **Position Size**: X%–Y% of portfolio
- **Concentration Tier**: [Exploratory 2–3% / High Conviction 5–7% / Core Asymmetric 10%+]
- **Dollar Amount**: $X based on [portfolio size if available]

### Risk-Reward Profile
- **Expected IRR**: X% (state timeframe)
- **Downside Case**: -X% or $Y price target
- **Upside/Downside Ratio**: X:1
- **Expected Value**: $X per dollar invested

### Portfolio Impact Analysis
- **Existing Exposure**: [sector/industry/factor correlations with current holdings]
- **Concentration Risk**: [assessment of adding this position to current portfolio]
- **Diversification Benefit**: [low/medium/high]
- **Liquidity Constraint**: [Daily trading volume vs. position size]

### Sizing Rationale
[2–3 sentences explaining why this specific size tier is appropriate — tie to conviction level, asymmetry, existing exposure, and risk tolerance]

### Drawdown Simulation
- **Standalone Max Loss**: -X% or -$Y (if position goes to downside case)
- **Portfolio Impact**: -X% portfolio drawdown (accounting for correlation)
- **Position at Risk**: $X total exposure

### Action Summary
"Allocate X%–Y% of capital to [TICKER], representing a [tier] position. Size reflects [key constraint: high conviction / asymmetric payoff / moderate conviction with capped downside / exploratory exposure pending catalyst]."
```

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete markdown section above. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete analysis into the `thesis` field; it is the ONLY output that reaches the Thesis panel.

Output:
- Recommended position size
- Risk-adjusted capital allocation
