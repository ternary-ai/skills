---
name: conviction-calibration-engine
description: Aligns position size with current thesis conviction, edge, and asymmetry; adjusts only when evidence changes. Use during ongoing portfolio management or after a material thesis update.
---

# Conviction Calibration Engine

Purpose: Continuously align size with edge.

Trigger: Ongoing portfolio management or post-update review.

Inputs:
- Expected asymmetry
- Thesis updates
- Market mispricing changes
- Risk profile changes

## Data Sources

Follow this order — do not ask the user which source to use:

1. **Context first**: Check `<stock_context>` and `<acquired_data>` for the
   current thesis conviction score, upside/downside targets, and current
   position size vs portfolio.
   If asymmetry data and current thesis are present → proceed directly to Process.
2. **Fetch if missing**: Call:
   - `GLOBAL_QUOTE` — current price to recompute upside/downside %
   - `OVERVIEW` — updated analyst target for consensus anchor
3. **Ask only if both fail**: Call `request_user_input` asking for the specific
   missing field only (e.g. "Please provide your current upside and downside
   price targets, and your current position size as % of portfolio").

Process:
1. Recalculate expected asymmetry.
2. Adjust size only if thesis improves, mispricing widens, or risk declines.
3. Prevent creeping overconfidence with explicit criteria.

## Output Format

Write a dedicated thesis section in markdown format as follows:

```markdown
## Conviction Calibration Update
**Analysis Date**: {Date}

### Current Position Status
- **Current Size**: X% of portfolio
- **Current Price**: $X
- **Original Entry**: $X (state date if available)
- **Unrealized P/L**: +/-X% or $Y

### Updated Expected Payoff
- **Upside Target**: $X (+Y% from current)
- **Downside Target**: $X (-Y% from current)
- **Upside/Downside Ratio**: X:1
- **Expected Value**: $X per dollar invested

### Thesis Conviction Assessment
- **Conviction Level**: [Low / Medium / High]
- **Conviction Change**: [Strengthened / Unchanged / Weakened] since last review
- **Edge Status**: [Widened / Stable / Narrowing]
- **Key Evidence Changes**: [bullet list of what changed — earnings, news, management action, competitor move, macro shift]

### Recommended Action
- **Action**: [Hold current size / Add X% / Trim X% / Exit]
- **Target Size**: X%–Y% of portfolio (vs X% current)
- **Rationale**: [2–3 sentences explaining why the size adjustment is warranted — must reference specific thesis updates, asymmetry changes, or risk profile shifts]

### Size Adjustment Criteria Applied
[State which trigger condition was met:]
- ☐ Thesis materially improved → warrant size increase
- ☐ Mispricing widened → warrant size increase  
- ☐ Risk declined → warrant size increase
- ☐ Thesis weakened → warrant size decrease
- ☐ Risk increased → warrant size decrease
- ☐ No material change → hold current size

### Action Summary
"[Hold / Increase / Decrease] position to X% of portfolio. [Brief justification in one sentence.]"
```

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete markdown section above. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete analysis into the `thesis` field; it is the ONLY output that reaches the Thesis panel.

Output:
- Size adjustment recommendation
- Conviction rationale
