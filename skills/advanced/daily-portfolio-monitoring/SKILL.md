---
name: daily-portfolio-monitoring
description: Monitors thesis drift across holdings using daily news, earnings releases, price moves, and regulatory filings; outputs thesis status and action recommendations. Use during the daily execution cycle.
---

# Daily Portfolio Monitoring

Purpose: Detect thesis drift in real time.

Trigger: Daily execution cycle.

Inputs:
- News flow
- Earnings releases
- Price moves
- Regulatory filings

## Data Sources

Follow this order — do not ask the user which source to use:

1. **Context first**: Check `<stock_context>` and `<acquired_data>` for holdings
   list, yesterday's prices, and any recent news or earnings already fetched.
   If today's price moves and recent news are present → proceed directly to Process.
2. **Fetch if missing**: Call for each holding:
   - `GLOBAL_QUOTE` — current price and daily % change
   - `NEWS_SENTIMENT` — last 24-hour news and sentiment for each ticker
   - `EARNINGS` — check for surprise if an earnings release was today
3. **Ask only if both fail**: Call `request_user_input` asking for the specific
   missing field only (e.g. "Please provide your current holdings list").

Process:
1. Map news to thesis assumptions.
2. Detect deviation from KPIs.
3. Identify volatility-driven opportunities.
4. Flag structural risk changes.

Output:
- Thesis intact / weakened / broken classification
- Action recommendation
## Output Format

Write a daily monitoring report in markdown format:

```markdown
## Daily Portfolio Monitoring Report
**Report Date**: {Date}

### Holdings Review
[For each monitored position:]

#### {TICKER} — {Position Size}%
- **Price**: $X (±Y% today)
- **Thesis Status**: [INTACT / WEAKENED / BROKEN]
- **Action**: [Hold / Review / Alert]

**Material Developments**:
- [News headline or event, if any]
- [Earnings surprise, guidance change, regulatory filing]
- [Insider transaction, analyst action]

**Thesis Impact**:  
[One sentence: Does this reinforce or contradict the original investment case?]

---

### Action Required
[List any positions requiring immediate attention with specific next steps]

### Monitoring Queue
[List positions with upcoming catalysts or events to track]
```

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete daily monitoring report. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete analysis into the `thesis` field; it is the ONLY output that reaches the Thesis panel.