---
name: exit-discipline-engine
description: Enforces rational exit decisions by comparing current price to intrinsic value and evaluating opportunity cost. Use when a position approaches full valuation or fundamentals deteriorate.
---

# Exit Discipline Engine

Purpose: Enforce rational sell decisions.

Trigger: Position exceeds intrinsic value or thesis weakens.

Inputs:
- Current price
- Updated valuation
- Opportunity cost

## Data Sources

Follow this order — do not ask the user which source to use:

1. **Context first**: Check `<stock_context>` and `<acquired_data>` for the
   original intrinsic value estimate, current price, and any updated thesis.
   If current price and intrinsic value are both present → proceed directly to Process.
2. **Fetch if missing**: Call:
   - `GLOBAL_QUOTE` — current price and 52-week range
   - `OVERVIEW` — updated forward P/E, analyst price target, EPS estimates
3. **Ask only if both fail**: Call `request_user_input` asking for the specific
   missing field only (e.g. "Please provide your intrinsic value estimate
   and current position size").

Process:
1. Compare price to intrinsic value.
2. Evaluate risk/reward reversal.
3. Assess superior capital alternatives.
4. Remove emotional bias.

Output:
- Exit / Trim / Maintain decision

## Output Format

Write an exit discipline analysis in markdown format:

```markdown
## Exit Discipline Analysis
**Analysis Date**: {Date}

### Current Position Status
- **Entry Price**: $X (date)
- **Current Price**: $X
- **Position P/L**: +/-X% or $Y
- **Position Size**: X% of portfolio

### Intrinsic Value vs Market Price
- **Updated Intrinsic Value**: $X per share
- **Current Price**: $X
- **Margin of Safety**: +/-X% (overvalued/undervalued)

### Risk/Reward Assessment
- **Upside to Fair Value**: +X%
- **Downside Risk**: -X%
- **Asymmetry Ratio**: X:1 [favorable/unfavorable]

### Opportunity Cost Analysis
[Compare IRR of continuing to hold vs deploying capital to next-best alternative idea. Include specific alternative ticker or asset class if applicable.]

### Emotional Bias Check
☐ Anchoring to entry price
☐ Loss aversion (reluctance to realize loss)
☐ Endowment effect (attachment to winner)
☐ Confirmation bias (ignoring contrary evidence)
☐ **None detected** — decision is rational

### Decision
**[EXIT / TRIM TO X% / MAINTAIN]**

**Rationale**: [One paragraph explaining why exit/trim/hold is the optimal capital allocation decision based on intrinsic value, asymmetry, and opportunity cost.]

### Action Items
- [If EXIT: liquidation plan, timeframe, tax consideration]
- [If TRIM: target %, reinvestment destination]
- [If MAINTAIN: monitoring metric, re-evaluation trigger]
```

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete exit discipline analysis. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete analysis into the `thesis` field; it is the ONLY output that reaches the Thesis panel.
