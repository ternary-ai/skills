---
name: thesis-integrity-audit
description: Re-underwrites a position after a drawdown or major event to determine whether the thesis is intact, weakened, or broken, and outputs a hold/add/reduce/exit decision. Use when a position declines 10%+ or a material event affects the original investment case.
---

# Thesis Integrity Audit

Purpose: Prevent emotional bias during volatility.

Trigger: 10% position drawdown or major event.

Inputs:
- Original investment memo
- Updated financials
- Market reaction

## Data Sources

Follow this order — do not ask the user which source to use:

1. **Context first**: Check `<stock_context>` and `<acquired_data>` for the
   original thesis, prior intrinsic value estimate, updated financial results,
   and current price.
   If updated financials and current price are present → proceed directly to Process.
2. **Fetch if missing**: Call:
   - `GLOBAL_QUOTE` — current price and % change
   - `INCOME_STATEMENT` — latest reported revenue, margins, net income
   - `CASH_FLOW` — latest FCF
   - `OVERVIEW` — updated market cap, forward P/E, EPS estimates
3. **Ask only if both fail**: Call `request_user_input` asking for the specific
   missing field only (e.g. "Please paste the original investment memo or
   the most recent earnings release").

Process:
1. Re-underwrite fundamentals.
2. Compare new data vs original assumptions.
3. Determine permanent vs temporary impairment.
4. Update intrinsic value.

Output:
- Hold / Add / Reduce / Exit decision

## Output Format

Write a thesis integrity audit in markdown format:

```markdown
## Thesis Integrity Audit
**Audit Date**: {Date}  
**Trigger Event**: [Drawdown -X% / Earnings miss / Competitive threat / Regulatory news / Other material event]

### Original Investment Thesis (Summary)
[1–2 paragraphs restating the core investment case at entry — why we bought, key assumptions, expected value drivers]

### What Changed
- **Price Movement**: Entry $X → Current $X (-Y%)
- **Fundamental Updates**: [Most recent earnings, guidance revision, margin shift, competitive loss]
- **External Factors**: [Macro, sector rotation, regulatory change]

### Re-Underwriting Analysis

#### Updated Fundamentals
[Revenue, margins, FCF — compare current run-rate vs original projections]

#### Assumption Check
| Original Assumption | Current Reality | Verdict |
|---------------------|-----------------|---------|
| [e.g., 15% revenue growth] | [e.g., 8% actual] | ☐ Intact / ☑ Weakened / ☐ Broken |
| [e.g., Gross margin 40%+] | [e.g., 38% and declining] | ☐ Intact / ☑ Weakened / ☐ Broken |
| [e.g., Market share gain] | [e.g., Flat share] | ☐ Intact / ☐ Weakened / ☑ Broken |

#### Intrinsic Value Update
- **Original Estimate**: $X per share
- **Updated Estimate**: $X per share  
- **Change**: -Y% or "reaffirmed"

### Thesis Status
**[INTACT / WEAKENED / BROKEN]**

[2–3 sentences explaining the verdict — is this a temporary setback or a permanent impairment?]

### Decision
**[HOLD / ADD / REDUCE / EXIT]**

**Rationale**: [One paragraph explaining the recommended action based on updated intrinsic value, thesis integrity, and opportunity cost vs other ideas]

### Action Items
- [Specific monitoring metric or catalyst to watch]
- [Position adjustment if applicable: trim to X%, add Y shares, exit Z%]
- [Re-audit trigger: set alert for next earnings, next filing, price level]
```

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete thesis integrity audit. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete analysis into the `thesis` field; it is the ONLY output that reaches the Thesis panel.
