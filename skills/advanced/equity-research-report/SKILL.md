---
name: equity-research-report
description: Generates an institutional-grade equity research report — BUY/SELL/HOLD with price target, fundamental analysis, catalyst analysis, bull/base/bear valuation, risk assessment, technical context, options flow, sector positioning, and insider signals. Adapted from quant-sentiment-ai/claude-equity-research.
---

# Equity Research Report

Purpose: Produce a full sell-side-style research report for a single ticker with a clear recommendation, price target, and probability-weighted scenarios.

Trigger: User asks for a comprehensive equity analysis, full research report, trading ideas, or "banker-style" writeup on a ticker.

## Data Sources

Follow this order — do not ask the user which source to use:

1. **Context first**: Check `<stock_context>` and `<acquired_data>` for financials,
   news, sector, peers, and existing thesis. Use what is already loaded.
2. **Fetch if missing** — call in parallel where possible:
   - `INCOME_STATEMENT` — revenue, gross profit, EBIT, net income (annual, 5yr)
   - `CASH_FLOW` — OCF, capex, FCF (annual, 5yr)
   - `BALANCE_SHEET` — debt, equity, cash
   - `EARNINGS` — EPS history, surprises, forward estimates
   - `OVERVIEW` — sector, description, peers, dividend history
   - `get_technical_indicators` — RSI, MACD, 50/200-day MAs, 52-week range
   - `get_news` — recent headlines (last 30 days)
   - `get_analyst_estimates` — consensus price target, range, rating distribution
3. **Web search** (if tools missing specific data):
   - Search in parallel: recent earnings, options flow, insider filings, analyst upgrades/downgrades, sector rotation data.
4. **Ask only if both fail**: use `request_user_input` asking for the specific missing values.

## Process

### 1. Research — Execute in Parallel
- Financial performance: revenue growth, margins, key KPIs with exact numbers and YoY/QoQ timeframes.
- Market positioning: peer valuation multiples (P/E, EV/EBITDA, P/S, P/B), competitive analysis.
- Advanced intelligence: technical levels, options flow (put/call ratios, unusual activity, IV trends), insider filings (Form 4, dollar amounts, executive names), institutional ownership changes.

### 2. Build the Report — Sections in Order

**Executive Summary**
- Clear BUY / SELL / HOLD with conviction level (High/Medium/Low).
- 12-month price target with % upside/downside from current price.
- 1–2 sentence investment thesis: primary catalyst + risk-reward characterisation.

**Fundamental Analysis**
- Recent financial metrics: revenue growth %, margins (gross/operating/net), FCF yield — all with specific numbers and timeframes.
- Peer comparison: P/E, EV/EBITDA, P/S vs sector median with named competitors.
- Forward outlook: management guidance, analyst consensus EPS/revenue estimates.

**Catalyst Analysis**
- Near-term (0–6 months): earnings dates, product launches, regulatory decisions — include specific dates where known.
- Medium-term (6–24 months): strategic initiatives, market expansion, competitive shifts.
- Event-driven: M&A potential, index inclusion/exclusion, spin-offs, capital returns.

**Valuation & Price Targets**
- Analyst consensus: $X (range $low–$high).
- Bull case $X — state the specific assumption (e.g. margin expansion, market share gain).
- Base case $X — consensus assumptions, stable execution.
- Bear case $X — risk scenario (e.g. competition, margin compression).
- Probability weighting: Bull X% / Base Y% / Bear Z% summing to 100%.

**Risk Assessment**
- Company risks: competitive threats, regulatory exposure, execution risk, leverage.
- Macro risks: rate sensitivity, economic cycle, sector rotation impact.
- Position sizing: X%–Y% allocation based on beta / volatility / conviction.
- ESG: flag only if material to institutional ownership.

**Technical Context & Options Intelligence**
- Current price vs 52-week range; distance from 50-day and 200-day MA.
- Key support and resistance levels (specific prices).
- Volume patterns: accumulation or distribution signal.
- Options flow: put/call ratio, unusual block activity, IV level vs historical, term structure skew.
- Momentum: RSI (overbought/oversold), MACD signal.

**Market Positioning**
- Stock performance vs sector ETF and S&P 500 over 1M / 3M / YTD (specific %).
- Sector rotation trends affecting the position.
- Relative strength vs closest peers.

**Insider Signals**
- Recent insider buy/sell transactions: name, role, dollar amount, date.
- Share buyback programme status and remaining authorisation.
- Institutional ownership trend: latest 13F changes (add/reduce/new/exit).
- Pattern interpretation: what the insider behaviour signals about management conviction.

### 3. Recommendation Summary Table

| Metric | Value |
|---|---|
| Rating | BUY / SELL / HOLD |
| Conviction | High / Medium / Low |
| Price Target | $X |
| Timeframe | 12 months |
| Upside/Downside | X% |
| Suggested Position | X%–Y% |

## Output Standards

- Use institutional terminology: EBITDA, EV/Sales, FCF yield, WACC, beta.
- All financial metrics must include specific numbers; no vague qualitative statements without data.
- Price targets must show the upside/downside calculation.
- Cite analyst firms by name when referencing price target updates.
- Include both bullish and bearish scenarios — no one-sided reports.
- Keep each section tight and scannable: short paragraphs or bullet lists.
- End every report with: *"This analysis is for educational and research purposes only. Not financial advice. All investments carry risk of loss."*

## Output Format

The entire research report must be formatted as a thesis-ready markdown document. Write all sections listed under "Build the Report" above in order. The complete report goes into the `thesis` field of the JSON output.

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete equity research report following the structure above. Include:
- Executive Summary with BUY/SELL/HOLD and price target
- Fundamental Analysis with specific financial metrics
- Catalyst Analysis with dated events
- Valuation & Price Targets (bull/base/bear)
- Risk Assessment
- Technical Context & Options Intelligence
- Market Positioning
- Insider Signals
- Recommendation Summary Table

This is an **advanced skill** — thesis upserting is mandatory. Never return empty thesis field. ⚠️ Extended thinking is discarded — copy the complete report into the `thesis` field; it is the ONLY output that reaches the Thesis panel.

## Escalate / Hand-off

- If thesis meets high-conviction long criteria → escalate to `deep-fundamental-underwriting` for full intrinsic value model.
- If significant downside risk identified → escalate to `capital-preservation-protocol`.
- If insider/senator signal is anomalous → surface to user before final recommendation.
