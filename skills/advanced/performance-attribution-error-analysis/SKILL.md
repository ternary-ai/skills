---
name: performance-attribution-error-analysis
description: Attributes portfolio returns to stock selection, sector allocation, and macro exposure, then identifies decision errors to improve the investment process. Use during monthly and quarterly portfolio reviews.
---

# Performance Attribution & Error Analysis

Purpose: Improve decision quality over time.

Trigger: Monthly and quarterly review.

Inputs:
- Return data
- Benchmark data
- Decision log

## Data Sources

Follow this order — do not ask the user which source to use:

1. **Context first**: Check `<stock_context>` and `<acquired_data>` for periodic
   return data, benchmark returns, and any trade decision log.
   If return series and benchmark data are present → proceed directly to Process.
2. **Fetch if missing**: Call:
   - `TIME_SERIES_DAILY` (per holding) — price history to compute period returns
   - `TIME_SERIES_DAILY` (benchmark ticker, e.g. SPY) — benchmark return series
   - `calculate` — attribution arithmetic (stock selection, allocation, residual)
3. **Ask only if both fail**: Call `request_user_input` asking for the specific
   missing field only (e.g. "Please paste your trade decision log or portfolio
   return series for the review period").

Process:
1. Attribute returns to stock selection, sector allocation, and macro exposure.
2. Identify mistakes: thesis error, timing error, sizing error.
3. Update playbook rules.

Output:
- Performance report
- Process refinements

## Output Format

Write a performance attribution report in markdown format:

```markdown
## Performance Attribution & Error Analysis
**Period**: {Start Date} to {End Date}

### Portfolio Performance Summary
- **Total Return**: +/-X%
- **Benchmark Return**: +/-X% (S&P 500 or relevant index)
- **Alpha**: +/-X%
- **Best Performer**: {TICKER} (+X%)
- **Worst Performer**: {TICKER} (-X%)

### Attribution by Position
| Ticker | Weight | Return | Contribution | Decision Quality |
|--------|--------|--------|--------------|------------------|
| XXX | X% | +/-X% | +/-X% | [Good/Neutral/Error] |
| XXX | X% | +/-X% | +/-X% | [Good/Neutral/Error] |
| ... | | | | |

### Decision Error Identification

#### Thesis Errors
[Positions where the fundamental investment case was wrong]
- **{TICKER}**: [What we believed vs what actually happened]

#### Timing Errors  
[Right thesis, wrong entry/exit timing]
- **{TICKER}**: [Entered too early/late, exited prematurely/late]

#### Sizing Errors
[Right thesis, wrong position size]
- **{TICKER}**: [Undersized winner / oversized loser]

### Process Improvements
[Specific, actionable lessons to refine screening, underwriting, sizing, or exit discipline]

### Key Takeaways
1. [First lesson]
2. [Second lesson]
3. [Third lesson]
```

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete performance attribution report. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete analysis into the `thesis` field; it is the ONLY output that reaches the Thesis panel.
