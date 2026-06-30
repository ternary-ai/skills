---
name: investment-quick-screen
description: Rapidly assesses a new ticker, thesis, or pitch to decide Proceed or Reject and produce a 1-page hypothesis summary. Use when a new stock idea, inbound pitch, or unfamiliar ticker needs initial screening before committing research time.
---

# Investment Opportunity Triage

Purpose: Rapidly determine if an idea deserves deep research.

Trigger: New ticker, thesis, or inbound pitch.

Inputs:
- Company name
- Industry
- Basic financial snapshot
- Initial thesis

## Data Sources

Follow this order — do not ask the user which source to use:

1. **Context first**: Check `<stock_context>` and `<acquired_data>` for company name,
   sector, revenue, margins, debt level, and any existing thesis text.
   If sufficient for a triage decision → proceed directly to Process.
2. **Fetch if missing**: Call `OVERVIEW` (company profile, market cap, P/E, sector)
   and `INCOME_STATEMENT` (revenue, gross profit, net income — last 2 years) if
   context is insufficient.
3. **Ask only if both fail**: Call `request_user_input` asking for the specific
   missing field only (e.g. "Please provide the company name or ticker").

Process:
1. Clarify the business model in one sentence.
2. Evaluate structural industry health.
3. Check for durable competitive advantage indicators.
4. Assess management credibility at a high level.
5. Screen for fatal flaws: structural decline, excess leverage, governance impossibility, binary regulatory risk.

Output:
- Proceed / Reject decision
- 1-page investment hypothesis summary

## Output Format

Write a quick screening analysis in markdown format:

```markdown
## Investment Quick Screen: {TICKER}
**Screening Date**: {Date}

### Business Model (One Sentence)
[What the company does, how it makes money, who the customers are]

### Industry Structure
- **Health**: [Growing / Stable / Declining]
- **Competitive Intensity**: [Low / Medium / High]
- **Key Tailwinds/Headwinds**: [One sentence each]

### Competitive Advantage Screen
☐ **Brand or reputation moat**  
☐ **Network effects**  
☐ **Switching costs**  
☐ **Economies of scale**  
☐ **Proprietary technology or IP**  
☐ **Regulatory or license barrier**  
☐ **No clear moat** (commodity business)

### Management & Capital Allocation  
[Insider ownership? Track record? Recent buybacks, M&A, or strategic shifts?]

### Fatal Flaw Check
☐ Structural decline (disrupted business model, dying end market)  
☐ Overleveraged balance sheet (Net Debt/EBITDA >4x with no deleveraging path)  
☐ Governance red flags (serial dilution, related-party deals, audit issues)  
☐ Binary regulatory risk (single product awaiting FDA/FCC, potential ban)  
☐ **None detected**

### Quick Valuation Sense
- **Current Valuation**: [P/E, EV/EBITDA, P/S — vs sector median]  
- **First Impression**: [Cheap / Fair / Expensive]

### Decision
**[PROCEED TO DEEP DIVE / REJECT]**

**1-Paragraph Investment Hypothesis**:  
[If PROCEED: Why this is potentially interesting — moat strength, valuation gap, catalyst, asymmetry]  
[If REJECT: What disqualified it — fatal flaw, no moat, overvalued, better alternatives available]
```

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete quick screen analysis. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete analysis into the `thesis` field; it is the ONLY output that reaches the Thesis panel.

Escalate if:
- Expected IRR potential exceeds 20% with durable moat characteristics.
