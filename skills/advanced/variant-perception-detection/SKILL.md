---
name: variant-perception-detection
description: Identifies where consensus is likely wrong by comparing modelled projections to market expectations and surfacing overlooked catalysts. Use after underwriting to define the differentiated insight that justifies the position.
---

# Variant Perception Detection

Purpose: Identify where consensus may be wrong.

Trigger: After underwriting.

Inputs:
- Market valuation
- Analyst expectations
- Earnings consensus
- Media narrative

## Data Sources

Follow this order — do not ask the user which source to use:

1. **Context first**: Check `<stock_context>` and `<acquired_data>` for current
   valuation multiples, analyst price targets, recent earnings results, and any
   existing thesis or variant perception notes.
   If consensus data is present → proceed directly to Process.
2. **Fetch if missing**: Call:
   - `OVERVIEW` — P/E, forward P/E, analyst target price, 52-week range
   - `EARNINGS` — EPS consensus vs actual surprises (last 8 quarters)
   - `NEWS_SENTIMENT` — dominant media narrative and sentiment scores
3. **Ask only if both fail**: Call `request_user_input` asking for the specific
   missing field only (e.g. "Please provide consensus EPS estimates").

Process:
1. Compare modeled projections vs consensus.
2. Identify embedded assumptions.
3. Map mispriced risks or overlooked catalysts.
4. Define the differentiated insight.

Output:
- “Market is wrong because…” statement
- Mispricing thesis
## Output Format

Write a variant perception analysis in markdown format:

```markdown
## Variant Perception Analysis
**Analysis Date**: {Date}

### Consensus View
[What the market currently believes — cite analyst reports, media narratives, price action]

### Our Contrarian Thesis
[Where we disagree and why — specific evidence the market is missing or misinterpreting]

### Overlooked Catalysts
1. **[Catalyst Name]**: [Description, timing, impact]
2. **[Catalyst Name]**: [Description, timing, impact]  
3. **[Catalyst Name]**: [Description, timing, impact]

### Evidence Supporting Variant View
- [Specific data point, filing, insider action, competitive dynamic, or operational change]
- [Additional evidence]
- [Additional evidence]

### Why The Market Is Wrong
[2–3 paragraphs explaining the behavioral or structural reason for the mispricing — anchoring bias, stale narrative, misunderstood segment, overlooked inflection]

### Variant Perception Scorecard
| Dimension | Score | Notes |
|-----------|-------|-------|
| Information Asymmetry | X/10 | [How hard is this insight to discover?] |
| Catalyst Visibility | X/10 | [How obvious is the upcoming catalyst?] |
| Magnitude of Mispricing | X/10 | [How large is the gap vs intrinsic value?] |
| Time Horizon | X/10 | [How long until the market reprices?] |
| **Total** | **XX/40** | |

### Recommended Action
[One paragraph: position stance, sizing guidance, monitoring plan]
```

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete variant perception analysis. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete analysis into the `thesis` field; it is the ONLY output that reaches the Thesis panel.