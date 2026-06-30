---
name: news-analysis
description: Fetch, source, and analyze the latest news for a stock. Use when the user asks to check the news, summarize news, analyze press sentiment, or understand what is driving a move. Always fetches fresh news (updates the News panel) before analyzing.
---

# News Analysis

## Purpose

Source fresh news for the active ticker, persist it to the workspace news panel, then deliver a structured analysis: what happened, why it matters, and what it signals for the investment thesis.

## ⛔ NEVER do these

| What the agent might do | What to do instead |
|---|---|
| Ask "Should I fetch fresh news or use the cache?" | Always call `fetch_latest_news` first — it refreshes the panel |
| Summarize only headlines without any analysis | Add a **Signals** section with investment-relevant take-aways |
| Ask which ticker to use | It is always in the session context — never ask |
| Add a disclaimer about news being incomplete | If data is sparse, note it in chat only |

---

## Steps

### Step 1 — Fetch fresh news

```
fetch_latest_news(ticker=TICKER, limit=15)
```

- This refreshes the **News panel** in the UI (same as clicking "Reload now?").
- Use the ticker from the session context.
- Default limit is 15. Use 20+ if the user wants a deep news scan.

### Step 2 — Scan for notable headlines

From the returned list, identify:
- **Catalyst events** — earnings, guidance, M&A, product launches, regulatory decisions.
- **Management / insider signals** — executive comments, Form 4 activity, buybacks.
- **Macro / sector cross-winds** — broader trends affecting the thesis.

If a headline looks highly relevant, fetch the full article body:
```
fetch_url(url=ARTICLE_URL, max_chars=4000)
```
Only do this for 1–2 most relevant articles — not for every headline.

### Step 3 — Classify sentiment

For each notable headline classify as: **Positive / Negative / Neutral** for the stock.
Do not hedge classifications. Be decisive.

### Step 4 — Write the analysis

Output a concise structured analysis:

```
## News Analysis — {TICKER} ({DATE})

### Key Headlines
- {DATE} | {SOURCE} | {HEADLINE} — **{POSITIVE/NEGATIVE/NEUTRAL}**
  *Why it matters: one sentence.*
- ...

### Signals
- **Catalyst present?** YES / NO — brief explanation.
- **Sentiment trend:** Broadly positive / Mixed / Broadly negative.
- **Thesis impact:** One sentence on what this means for the current thesis.

### Raw headlines (for reference)
{paste full list from fetch_latest_news output}
```

---

## Output rules

- Do NOT include full article bodies in the Thesis — only the analysis.
- Keep "Key Headlines" to the 3–5 most investment-relevant items.
- "Signals" must always be populated, even if news is thin.
- If no news is found: state it clearly in chat → do not create an empty section in the Thesis.

---

## When to escalate to deeper research

After the news analysis, suggest follow-up actions if you find:
- A missed earnings catalyst → suggest `fetch_latest_news` + financials review.
- Insider buying/selling mentioned → suggest `fetch_insider_transactions`.
- Analyst upgrade/downgrade → suggest `fetch_technical_insights`.
- M&A rumour → suggest running the `activist-feasibility-analysis` skill.
