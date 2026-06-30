---
name: deep-fundamental-underwriting
description: Builds intrinsic value estimates, earnings power analysis, and a 3-scenario investment memo for an approved candidate. Use after triage approval when full fundamental underwriting is required.
---

# Deep Fundamental Underwriting

Purpose: Determine intrinsic value and long-term earnings power.

Trigger: Approved from triage.

Inputs:
- 5–10 years financials
- Competitive landscape
- Management history
- Capital allocation record

## Data Sources

Follow this order — do not ask the user which source to use:

1. **Context first**: Check `<stock_context>` and `<acquired_data>` for multi-year
   income, cash flow, balance sheet data, and any existing investment memo.
   If 5+ years of financials are present → proceed directly to Process.
2. **Fetch if missing**: Call in sequence:
   - `INCOME_STATEMENT` — revenue, gross profit, EBIT, net income (annual, 10yr)
   - `CASH_FLOW` — operating cash flow, capex, FCF (annual, 10yr)
   - `BALANCE_SHEET` — debt, equity, cash (annual, 10yr)
   - `EARNINGS` — EPS history and surprises
   - `OVERVIEW` — sector, description, management tenure, dividend history
3. **Ask only if both fail**: Call `request_user_input` asking for the specific
   missing data (e.g. "Please paste the last 5 years of revenue and EBITDA").

Process:
1. Analyze revenue durability.
2. Evaluate margin sustainability.
3. Review capital intensity.
4. Build 3-scenario model (Base/Bull/Bear).
5. Estimate intrinsic value range.
6. Map risks: structural, cyclic, regulatory.

Output:
- Intrinsic value band
- Expected IRR distribution
- Investment memo

## Output Format

Write a comprehensive deep fundamental analysis in markdown format. Include all sections:

```markdown
## Deep Fundamental Underwriting
**Analysis Date**: {Date}

### Revenue Durability Analysis
[5–10 year revenue trend, growth rate stability, customer concentration, recurrence]

### Margin Sustainability
[Gross margin, operating margin, net margin — trends, competitive positioning, pricing power]

### Capital Intensity
[Capex as % of revenue, FCF conversion, ROIC, reinvestment requirements]

### Intrinsic Value Model

#### Base Case
- **Assumptions**: [normalized earnings, growth rate, terminal multiple]
- **Intrinsic Value**: $X per share
- **IRR @ Current Price**: Y%

#### Bull Case
- **Assumptions**: [positive scenario drivers]
- **Intrinsic Value**: $X per share  
- **IRR @ Current Price**: Y%

#### Bear Case
- **Assumptions**: [downside scenario]
- **Intrinsic Value**: $X per share
- **IRR @ Current Price**: Y%

### Probability-Weighted Valuation
- **Expected Value**: $X (Bull X% | Base Y% | Bear Z%)
- **Current Price**: $X
- **Implied Upside/Downside**: +X% / -Y%
- **Asymmetry Ratio**: X:1

### Risk Map
- **Structural Risks**: [competitive threats, business model vulnerabilities]
- **Cyclical Risks**: [economic sensitivity, margin variability]
- **Regulatory Risks**: [policy exposure, compliance burden]
- **Execution Risks**: [management track record, capital allocation history]

### Investment Memo Summary
[3–5 paragraph narrative tying together the analysis — why the company is undervalued or overvalued, what the key value drivers are, what could go wrong, and what the recommended action is]
```

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete deep fundamental underwriting analysis. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete analysis into the `thesis` field; it is the ONLY output that reaches the Thesis panel.

Escalate if:
- High asymmetry identified (>2:1 upside/downside).
