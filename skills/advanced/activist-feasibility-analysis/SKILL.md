---
name: activist-feasibility-analysis
description: Assesses whether activist engagement can unlock value given ownership structure, governance weaknesses, and legal constraints. Use when a holding shows persistent underperformance combined with governance misalignment.
---

# Activist Feasibility Analysis

Purpose: Determine whether intervention increases expected return.

Trigger: Underperformance + governance misalignment.

Inputs:
- Ownership structure
- Board composition
- Voting thresholds
- Shareholder base

## Data Sources

Follow this order — do not ask the user which source to use:

1. **Context first**: Check `<stock_context>` and `<acquired_data>` for
   institutional ownership %, board member names, and any prior activist filings.
   If ownership structure and board data are present → proceed directly to Process.
2. **Fetch if missing**: Call:
   - `sec_get_overview` — DEF 14A proxy data: board composition, insider ownership
   - `OVERVIEW` — institutional ownership %, shares outstanding, float
   - `NEWS_SENTIMENT` — recent activist news, 13D/13G filing mentions
3. **Ask only if both fail**: Call `request_user_input` asking for the specific
   missing field only (e.g. "Please paste the top 10 institutional shareholders
   or the most recent proxy statement summary").

Process:
1. Estimate influence threshold.
2. Evaluate management vulnerability.
3. Model value creation via intervention.
4. Assess legal and reputational risks.

Output:
- Passive / Engage / Full Activism decision
- Engagement roadmap

## Output Format

Write an activist feasibility analysis in markdown format:

```markdown
## Activist Feasibility Analysis
**Analysis Date**: {Date}

### Value Unlock Opportunity
- **Current Market Cap**: $X
- **Current Trading Multiple**: X.Xx (P/E, EV/EBITDA, or P/B)
- **Potential Value with Changes**: $Y
- **Implied Upside**: +X%

### Proposed Changes
1. [Specific operational, strategic, or capital allocation change]
2. [Board composition, management incentives, or governance reform]
3. [Asset sale, spin-off, buyback program, or dividend policy]

### Feasibility Assessment

#### Ownership Structure
- **Float**: X%
- **Insider Ownership**: X%
- **Institutional Ownership**: X% (top holders: [names])
- **Entrenchment Devices**: [Dual-class shares, poison pill, staggered board, supermajority provisions]

#### Governance & Management
- **Board Independence**: X/Y independent directors
- **Management Tenure**: X years (CEO name)
- **Historical Activism**: [Prior campaigns? Outcomes?]
- **Management Receptiveness**: [Receptive / Neutral / Hostile]

#### Economic & Execution Risk
- **Cost of Campaign**: $X (proxy fight, legal, PR)
- **Timeline**: X months to achieve changes
- **Probability of Success**: X%
- **Expected Value**: $Y (probability-adjusted upside minus campaign cost)

### Decision
**[PASSIVE / ENGAGE / FULL ACTIVISM]**

**Rationale**: [One paragraph explaining whether and how activist engagement can unlock value, considering ownership structure, governance barriers, campaign cost, and expected outcome.]

### Engagement Roadmap
[If ENGAGE or FULL ACTIVISM: Step-by-step plan — private dialogue, 13D filing, proxy fight, board seats, public campaign, litigation]  
[If PASSIVE: Why direct engagement won't work — wait for third-party activist or pass on the opportunity]
```

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete activist feasibility analysis. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete analysis into the `thesis` field; it is the ONLY output that reaches the Thesis panel.
