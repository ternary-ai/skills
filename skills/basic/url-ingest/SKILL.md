---
name: url-ingest
description: Fetch and analyse any public URL — news article, press release, SEC filing, earnings transcript, research note. Auto-triggered whenever the user supplies an https:// or http:// link.
---

# URL Ingest

Purpose: Retrieve the full text of a public URL the user provides and deliver a
substantive analysis of its content, with investment framing when relevant.

Trigger: User message contains an `https://` or `http://` URL, regardless of any
other text in the message. This skill takes absolute priority — do not wait for a
skill dispatch prefix.

## Process

1. **Extract the URL** — Pull the bare URL from the user message. If multiple URLs
   are present, process each in sequence.

2. **Fetch the content** — Call `fetch_url(url, max_chars=8000)`.
   Use `max_chars=8000` as the default — articles need room.
   If the response contains "paywall", "subscribe", "sign in", or fewer than 200
   words of body text, note it clearly and summarise from what is available.

3. **Classify the content type** — Determine what was fetched:
   - News article / blog post
   - Press release / investor relations page
   - SEC filing (10-K, 10-Q, 8-K, DEF 14A, etc.)
   - Earnings call transcript
   - Research note / analyst report
   - Other (describe)

4. **Analyse** — Deliver a structured summary appropriate to the content type:

   **News / Press Release:**
   - One-line recap: source, date, core claim.
   - Key facts (3–6 bullets).
   - What this means for the company / sector.

   **SEC Filing:**
   - Filing type, period, date.
   - Material disclosures: revenue, guidance, risks, management commentary.
   - What changed vs. prior filing (if context available).

   **Earnings Transcript:**
   - EPS beat/miss, revenue beat/miss.
   - Management tone: confident / cautious / defensive.
   - Key forward guidance quotes (verbatim short snippets).
   - Analyst Q&A highlights.

   **Research Note:**
   - Analyst firm, rating, price target.
   - Core thesis in 2 sentences.
   - Key estimates and assumptions.

5. **Investment Framing** — For any content that is material to the active ticker
   (or to a ticker named in the article), append:

   > **Investor Angle**
   > - Bull case implication: …
   > - Bear case implication: …
   > - What to watch next: …

   Skip this section if the content is clearly unrelated to investable assets.

6. **Thesis update** — If the article is material (earnings, deal, restructuring,
   regulatory action, management change, guidance revision), populate the `thesis`
   JSON field with a brief new section appended to the existing thesis.
   For routine news or background reading, leave `thesis` empty.

## Fallbacks

- Paywall / login wall → summarise from any visible text + headline; state clearly
  that the full article was behind a paywall.
- Fetch error → report the exact error in `chat`; do not hallucinate content.
- Non-English content → translate key passages; flag language in the recap.
- PDF / binary → `fetch_url` will return raw text extraction; parse what is readable.

## Output Rules

- Lead with the source domain and content type (e.g. "**Yahoo Finance · News article**").
- Do NOT write "I fetched..." — present content directly.
- Cite publication date and author when visible in the fetched text.
- Keep summaries tight: short paragraphs, bullet lists for key facts.
- Never fabricate quotes — only use text that appears in the fetched content.
