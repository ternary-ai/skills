---
name: crisis-capital-allocation
description: Allocates capital during market-wide stress by prioritising liquidity preservation and asymmetric opportunity deployment. Use during volatility spikes, liquidity crises, or broad market drawdowns.
---

# Crisis Capital Allocation

Purpose: Exploit dislocations while preserving survival.

Trigger: Market-wide stress event.

Inputs:
- Liquidity position
- Portfolio drawdown
- Volatility spike

## Data Sources

Follow this order — do not ask the user which source to use:

1. **Context first**: Check `<stock_context>` and `<acquired_data>` for current
   drawdown magnitude, cash reserves, and volatility readings.
   If liquidity position and drawdown data are present → proceed directly to Process.
2. **Fetch if missing**: Call:
   - `calculate_liquidity_profile` — available cash and liquid asset buffer
   - `GLOBAL_QUOTE` (top 5 holdings) — current price and daily % move
   - `TOP_GAINERS_LOSERS` — market-wide stress signal (broad dislocation check)
3. **Ask only if both fail**: Call `request_user_input` asking for the specific
   missing field only (e.g. "Please provide your current cash balance and
   portfolio peak-to-trough drawdown").

Process:
1. Freeze non-essential activity.
2. Re-evaluate top 5 positions.
3. Rank opportunities by asymmetry.
4. Deploy capital selectively.

Output:
- Capital deployment plan
- Liquidity survival assessment

## Output Format

Write a crisis capital allocation plan in markdown format:

```markdown
## Crisis Capital Allocation Plan
**Analysis Date**: {Date}  
**Crisis Type**: [Market crash / Liquidity freeze / Sector collapse / Recession / Credit event]

### Market Conditions
- **S&P 500**: $X (-Y% from peak)
- **VIX**: X (panic level: [Low/Medium/High])
- **Credit Spreads**: X bps (vs normal Z bps)
- **Liquidity**: [Normal / Impaired / Frozen]

### Available Dry Powder
- **Cash Reserve**: $X (Y% of portfolio)
- **Liquidatable Positions**: [Tickers that can be sold without excessive loss]
- **Total Deployable Capital**: $X

### Opportunity Assessment

#### High-Conviction Ideas Now Trading Below Intrinsic Value
| Ticker | Intrinsic Value | Current Price | Discount | Upside |
|--------|-----------------|---------------|----------|--------|
| XXX | $X | $X | -Y% | +Z% |
| XXX | $X | $X | -Y% | +Z% |

#### Crisis-Specific Opportunities
[Dislocations unique to this event — forced selling, index rebalancing, margin calls, sector rotation]

### Deployment Plan

**Phase 1 (Immediate)**: Deploy X% of dry powder  
- {TICKER}: $X at $Y (Z shares)
- {TICKER}: $X at $Y (Z shares)

**Phase 2 (If market drops another -X%)**: Deploy X% of remaining dry powder  
- Lower entry prices, larger positions

**Phase 3 (Full capitulation)**: Deploy final X%  
- Maximum aggression at maximum pessimism

### Risk/Reward Analysis
- **Expected Return (probability-weighted)**: +X%  
- **Downside Risk**: -Y% (if market falls another -Z%)
- **Upside/Downside Ratio**: X:1

### Liquidity Survival Assessment
- **Minimum Cash Reserve Required**: $X (to survive X months without forced selling)
- **Current vs Required**: [Sufficient / Borderline / Insufficient]
- **Survival Horizon**: X months at current burn rate

### Behavioral Discipline Checklist
☐ Deploying into genuine undervaluation (not catching falling knife)  
☐ Sufficient liquidity to survive further drawdown  
☐ Position sizing accounts for volatility spike  
☐ No forced selling pressure on existing positions  
☐ Clear thesis — not just buying because "it's cheap"

### Action Summary
[One paragraph: deploy $X into {tickers}, staged over {timeframe}, targeting X% return with discipline to add more if market provides better entry.]
```

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete crisis capital allocation plan. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete analysis into the `thesis` field; it is the ONLY output that reaches the Thesis panel.
