---
name: news-article-deep-dive
description: Fetch and analyze ALL unique recent news articles for a ticker. Evaluates each article's full text, extracts key facts, investment implications, and synthesizes a comprehensive news report showing what's driving the stock narrative.
---

# News Article Deep-Dive

Purpose: Provide comprehensive analysis of all recent news by fetching and evaluating the full text of every unique article, not just headlines.

Trigger: User asks "news deep dive", "analyze all news", "what's driving the news", "comprehensive news analysis", or `/news-article-deep-dive`.

## Process

### 1. Extract News from Stock Context
- Read the `## News` section in `<stock_context>` — this contains news already fetched by prior turns.
- Parse each news item to extract: headline, source, date, URL.
- **Do NOT call `fetch_news()` unless the news list is empty or clearly outdated (>24 hours).**

### 2. Deduplicate URLs
- Build a dictionary mapping URL → news item.
- If multiple headlines point to the same URL, keep the most descriptive headline.
- Count: `{N} unique articles found after deduplication`.

### 3. Prioritize Articles
- Sort by:
  1. **Material events** (earnings, M&A, regulatory, insider activity)
  2. **Recency** (within last 7 days preferred)
  3. **Credible sources** (Bloomberg, Reuters, WSJ, company press releases)
- Select top 5-8 articles (or all if fewer than 8 unique URLs).

### 3. Fetch Full Article Text — Batch Process
For each selected article:
```
fetch_url(url=ARTICLE_URL, max_chars=6000)
```

**Batching:** Process articles in a single plan step:
- "Fetch full text for 7 unique articles" (not one tool call per article in sequence)

### 4. Analyze Each Article
For each fetched article, extract:
- **Date & Source**
- **Core Event/Claim** (1-2 sentences)
- **Key Facts** (3-5 bullet points from article body)
- **Investment Implication** (Bull/Bear/Neutral with reasoning)
- **Credibility** (Hard news vs speculation vs opinion)

### 5. Synthesize Report

Output structure:

```markdown
## News Deep-Dive Report — {TICKER} ({DATE})

### Summary
{2-3 sentence overview: what's driving the narrative, sentiment trend, key catalyst identified}

### Article-by-Article Analysis

#### 1. {HEADLINE} ({SOURCE}, {DATE})
**Event:** {one-line summary}  
**Key Facts:**
- {fact 1}
- {fact 2}
- {fact 3}

**Investment Angle:** {Bull/Bear/Neutral} — {one sentence reasoning}  
**Source Credibility:** {Primary source/Established media/Aggregator/Opinion}

---

#### 2. {HEADLINE} ...
{repeat structure}

---

### Cross-Article Signals
- **Consensus Theme:** {what all articles agree on}
- **Divergence:** {any conflicting narratives or data points}
- **Sentiment Balance:** X bullish / Y neutral / Z bearish articles
- **Catalyst Status:** {Confirmed/Developing/Speculative}

### Thesis Impact
{One paragraph: how this news collectively affects the investment thesis. What changed? What's confirmed? What to monitor?}
```

### 6. Thesis Upsert — MANDATORY
**This is an advanced skill** → the complete deep-dive report MUST be appended to the ticker's thesis under a new section. ⚠️ Extended thinking is discarded — copy the complete report into the `thesis` field; it is the ONLY output that reaches the Thesis panel:

```markdown
## News Deep-Dive — {Date}
{Full report from step 5}
```

## Cost Controls

- **Use `<stock_context>` as primary source** — news has already been fetched by prior turns; extract from there first
- **Only call `fetch_news()` if news list is empty or >24 hours old** — avoid redundant fetches
- **Batch fetch_url calls** — single plan step for all articles, not sequential
- **Limit to 8 articles max** — even if more are available
- **Use session cache** — if articles already fetched this session, reuse from `<acquired_data>`

## Error Handling

- If `<stock_context>` has no news or news is >24 hours old: call `fetch_news(ticker, limit=20)` as fallback
- If `fetch_url(article_url)` fails (paywall/404): skip that article, note in final count ("Analyzed 6 of 8 articles; 2 unavailable")
- If no URLs available after deduplication: analyze from headlines + snippets only, state limitation in report
- If ticker has <3 unique news items: note "Limited news coverage" in summary, proceed with available data

## Output Standards

- Lead with synthesis, not mechanics ("I fetched X articles" → just present findings)
- Every article gets the 4-part structure: Event / Key Facts / Investment Angle / Credibility
- Cross-Article Signals section is mandatory even if thin
- Thesis Impact must tie back to valuation, moat, or catalyst framework
- Use present tense for recent events, past tense for historical comparisons

## When NOT to Use This Skill

- User asks about ONE specific headline → not needed; answer directly from stock_context
- **User wants to refresh news cache** → use `news-analysis` skill first (fetches + caches), THEN run this skill
- User wants headline sentiment only → use `news-analysis` (doesn't fetch full articles)
- Real-time news during market hours → this skill is for comprehensive post-analysis, not breaking news

## Workflow Pattern

Typical two-step execution:
1. **User**: "refresh news for AAPL"  
   **Agent**: Calls `news-analysis` → fetches fresh news, updates stock_context, delivers sentiment summary
   
2. **User**: "now do a deep dive on all those articles"  
   **Agent**: Calls `news-article-deep-dive` → extracts URLs from stock_context, fetches full text, delivers comprehensive report
