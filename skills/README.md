# Ternary Capital — Skills

Skills are step-by-step playbooks the agent loads on demand via `read_skill("<name>")`.
Each skill defines what tools to call, in what order, and what defaults to apply.
The agent never improvises tool sequences — it follows the loaded skill.

---

## How skills work

1. Agent receives a user request.
2. Agent matches it against the **Skill Index** in the system prompt.
3. Agent calls `read_skill("<name>")` to load the full playbook.
4. Agent follows the skill's steps exactly — including which tools to call.

Skills are located in `skills/basic/<folder-name>/SKILL.md` or `skills/advanced/<folder-name>/SKILL.md`.

---

## Skill Index

### Data Sourcing

| Skill | Trigger | Output |
|---|---|---|
| [data-source](#data-source) | Called at the start of every quantitative request that requires external data | Data plan: which tool to call, in which order, after checking context |

### Charting & Visualisation

| Skill | Trigger | Output |
|---|---|---|
| [chart-writeup](#chart-writeup) | User asks for any bar/line chart of financial or price data | `chart-bar` / `chart-line` fenced block embedded in Thesis |
| [standard-charts](#standard-charts) | Called internally by `chart-writeup` to look up defaults | Canonical chart type, time frame, unit, and tool for each metric |
| [graph-writeup](#graph-writeup) | User asks for a relationship map, peer network, or business model diagram | Mermaid `graph` block embedded in Thesis |
| [table-writeup](#table-writeup) | User asks to present data in a table | Markdown table embedded in Thesis |

### Research & Analysis

| Skill | Trigger | Output |
|---|---|---|
| [equity-research-report](#equity-research-report) | User wants a full institutional research report with BUY/SELL/HOLD, price target, and scenarios | 8-section report with recommendation table |
| [investment-quick-screen](#investment-quick-screen) | New ticker, pitch, or idea needs initial screening | Proceed / Reject decision + 1-page hypothesis |
| [deep-fundamental-underwriting](#deep-fundamental-underwriting) | Post-triage: full intrinsic value and earnings power analysis | Intrinsic value band, IRR distribution, investment memo |
| [variant-perception-detection](#variant-perception-detection) | After underwriting: find where consensus is wrong | "Market is wrong because…" statement + mispricing thesis |
| [thesis-integrity-audit](#thesis-integrity-audit) | Position down 10%+ or material event occurs | Hold / Add / Reduce / Exit decision |
| [news-article-deep-dive](#news-article-deep-dive) | User asks to explain or analyse a headline visible in stock context | Full article summary with investor angle |

### Portfolio & Position Management

| Skill | Trigger | Output |
|---|---|---|
| [position-sizing-concentration](#position-sizing-concentration) | Idea has passed triage and underwriting | Recommended position size and tier |
| [conviction-calibration-engine](#conviction-calibration-engine) | Ongoing management or after a thesis update | Size adjustment recommendation |
| [portfolio-construction-optimizer](#portfolio-construction-optimizer) | Adding a new position or quarterly review | Rebalancing recommendation + concentration health score |
| [daily-portfolio-monitoring](#daily-portfolio-monitoring) | Daily execution cycle | Thesis intact / weakened / broken + action recommendation |
| [exit-discipline-engine](#exit-discipline-engine) | Position near full valuation or fundamentals deteriorating | Exit / Trim / Maintain decision |
| [performance-attribution-error-analysis](#performance-attribution-error-analysis) | Monthly or quarterly review | Performance report + process refinements |

### Risk & Crisis

| Skill | Trigger | Output |
|---|---|---|
| [capital-preservation-protocol](#capital-preservation-protocol) | Portfolio drawdown exceeds threshold or leverage elevated | Defensive restructuring plan |
| [crisis-capital-allocation](#crisis-capital-allocation) | Market-wide stress, volatility spike, or liquidity crisis | Capital deployment plan + liquidity survival assessment |
| [activist-feasibility-analysis](#activist-feasibility-analysis) | Holding shows persistent underperformance + governance misalignment | Passive / Engage / Full Activism decision |

### Utilities

| Skill | Trigger | Output |
|---|---|---|
| [calculator](#calculator) | Arithmetic, percentages, ratios, growth rates, unit conversions | Precise numeric result with units |
| [anthropic-sdk](#anthropic-sdk) | Building or modifying AI applications with the Anthropic SDK | Code and architecture guidance |

---

## Data Sources by Skill

Every skill follows the same fallback order: **context first → fetch → ask**.
The table below documents what each skill checks and which tools it calls.

| Skill | Context fields checked | Fetch tools |
|---|---|---|
| `equity-research-report` | financials, news, thesis, sector, peers | `INCOME_STATEMENT`, `CASH_FLOW`, `BALANCE_SHEET`, `EARNINGS`, `OVERVIEW`, `get_technical_indicators`, `get_news`, `get_analyst_estimates` |
| `investment-quick-screen` | company, sector, revenue, margins | `OVERVIEW`, `INCOME_STATEMENT` |
| `deep-fundamental-underwriting` | multi-year financials, memo | `INCOME_STATEMENT`, `CASH_FLOW`, `BALANCE_SHEET`, `EARNINGS`, `OVERVIEW` |
| `variant-perception-detection` | multiples, targets, thesis | `OVERVIEW`, `EARNINGS`, `NEWS_SENTIMENT` |
| `thesis-integrity-audit` | prior thesis, intrinsic value, price | `GLOBAL_QUOTE`, `INCOME_STATEMENT`, `CASH_FLOW`, `OVERVIEW` |
| `conviction-calibration-engine` | conviction score, targets, position size | `GLOBAL_QUOTE`, `OVERVIEW` |
| `position-sizing-concentration` | IRR estimate, holdings, weights | `calculate_portfolio_exposure_map`, `calculate_irr`, `GLOBAL_QUOTE` |
| `portfolio-construction-optimizer` | holdings + weights, sector breakdown | `calculate_portfolio_exposure_map`, `pca_factor_decomposition`, `GLOBAL_QUOTE` |
| `daily-portfolio-monitoring` | holdings, yesterday's prices, news | `GLOBAL_QUOTE`, `NEWS_SENTIMENT`, `EARNINGS` |
| `exit-discipline-engine` | intrinsic value, current price, thesis | `GLOBAL_QUOTE`, `OVERVIEW` |
| `performance-attribution-error-analysis` | return series, benchmark, decision log | `TIME_SERIES_DAILY`, `calculate` |
| `capital-preservation-protocol` | weights, leverage, cash reserves | `calculate_liquidity_profile`, `calculate_portfolio_exposure_map`, `GLOBAL_QUOTE` |
| `crisis-capital-allocation` | drawdown, cash balance, volatility | `calculate_liquidity_profile`, `GLOBAL_QUOTE`, `TOP_GAINERS_LOSERS` |
| `activist-feasibility-analysis` | ownership %, board names, filings | `sec_get_overview`, `OVERVIEW`, `NEWS_SENTIMENT` |

---

## Skill Details

### chart-writeup

Renders an interactive bar or line chart from financial or price data and embeds it in the Thesis.

**Workflow:**
1. Load `standard-charts` to get defaults (chart type, time frame, unit, tool).
2. Check `<stock_context>` and `<acquired_data>` — use if already present.
3. Fetch missing data via Alpha Vantage MCP tools.
4. Derive metrics if not directly available (EBITDA, FCF, margins).
5. Emit a `chart-bar` or `chart-line` fenced JSON block.

**Alpha Vantage tools used:**

| Tool | Data |
|---|---|
| `INCOME_STATEMENT` | Revenue, gross profit, operating income, net income |
| `CASH_FLOW` | D&A, operating cash flow, capex |
| `BALANCE_SHEET` | Total assets, liabilities, debt, cash |
| `EARNINGS` | Quarterly EPS |
| `TIME_SERIES_DAILY` | Daily close prices for line charts |

**Derivations:**
- `EBITDA = operatingIncome + depreciationDepletionAndAmortization`
- `FCF = operatingCashflow − capitalExpenditures`
- `Gross Margin = grossProfit / totalRevenue × 100`
- `Operating Margin = operatingIncome / totalRevenue × 100`
- `Net Margin = netIncome / totalRevenue × 100`

**Output format:** `chart-bar` or `chart-line` fenced block containing a `ChartSpec` JSON object.

---

### standard-charts

Defaults lookup table for every common investment chart. Called internally by `chart-writeup`.

**Canonicalises:** chart type, time frame, unit, tool, and derivation formula for:
Revenue, Gross Profit, Gross Margin, EBITDA, EBIT, Operating Margin, Net Income,
Net Margin, EPS, FCF, Operating Cash Flow, CapEx, Total Debt, Cash,
Price history, Peer comparison.

**No tools called directly** — provides metadata consumed by `chart-writeup`.

---

### graph-writeup

Creates Mermaid network diagrams showing relationships between companies, sectors, industries, and news sources.

**Tools used:**

| Tool | Data |
|---|---|
| `graph_peer_network(ticker)` | Peer company relationships via FMP + stock context |
| `graph_news_sources(ticker)` | News API sources and article counts |
| `graph_business_model(ticker, extra_links_json)` | Company → sector/industry hierarchy; accepts ad-hoc triples from 10-K text |

**Output format:** Mermaid `graph LR` or `graph TD` fenced block embedded in Thesis.

---

### table-writeup

Generates clean markdown tables from structured data.

**Tools used:** `render_table(rows_json, title)` — accepts a JSON array of objects.

**Output format:** Markdown table appended to the Thesis.

---

### equity-research-report

Produces a full institutional-grade equity research report for a single ticker.
Adapted from [quant-sentiment-ai/claude-equity-research](https://github.com/quant-sentiment-ai/claude-equity-research).

**Inputs needed:** Ticker symbol. All other data is fetched automatically.

**Process:**
1. Load available data from `<stock_context>` and `<acquired_data>`.
2. Fetch missing data in parallel (financials, technicals, analyst estimates, news).
3. Run parallel web searches for options flow, insider filings, sector rotation data.
4. Build the 8-section report in order.
5. Emit recommendation table with rating, conviction, price target, and position size.

**Sections:**
1. Executive Summary — BUY/SELL/HOLD + price target + thesis
2. Fundamental Analysis — revenue growth, margins, peer multiples
3. Catalyst Analysis — near-term (0–6M), medium-term (6–24M), event-driven
4. Valuation & Price Targets — bull/base/bear with probability weights
5. Risk Assessment — company + macro risks + position sizing
6. Technical Context & Options Intelligence — support/resistance, RSI/MACD, put/call, IV
7. Market Positioning — stock vs sector ETF, relative strength, rotation
8. Insider Signals — Form 4 activity, buybacks, institutional 13F changes

**Escalation:** High-conviction long → `deep-fundamental-underwriting` | Downside risk → `capital-preservation-protocol`.

---

### investment-quick-screen

Rapid initial screening to decide Proceed or Reject before committing research time.

**Inputs needed:** Company name, industry, basic financial snapshot, initial thesis.

**Process:**
1. Clarify business model in one sentence.
2. Evaluate structural industry health.
3. Check for durable competitive advantage indicators.
4. Assess management credibility.
5. Screen for fatal flaws (structural decline, excess leverage, governance, binary regulatory risk).

**Tools used:** Stock context, `yahoo_key_statistics`, `sec_get_overview` (if available).

**Escalate if:** Expected IRR > 20% with durable moat characteristics.

---

### deep-fundamental-underwriting

Full intrinsic value model after triage approval.

**Inputs needed:** 5–10 years of financials, competitive landscape, management history, capital allocation record.

**Process:**
1. Analyse revenue durability.
2. Evaluate margin sustainability.
3. Review capital intensity.
4. Build 3-scenario model (Base / Bull / Bear).
5. Estimate intrinsic value range.
6. Map structural, cyclic, and regulatory risks.

**Tools used:** `INCOME_STATEMENT`, `CASH_FLOW`, `BALANCE_SHEET`, `EARNINGS`, `OVERVIEW`, `calculate`.

**Output:** Intrinsic value band, expected IRR distribution, investment memo.

---

### variant-perception-detection

Identifies where consensus is likely wrong and surfaces overlooked catalysts.

**Inputs needed:** Market valuation, analyst expectations, earnings consensus, media narrative.

**Process:**
1. Compare modelled projections vs consensus.
2. Identify embedded assumptions in current price.
3. Map mispriced risks or overlooked catalysts.
4. Define the differentiated insight.

**Tools used:** `OVERVIEW`, `EARNINGS`, `calculate`, stock context.

**Output:** "Market is wrong because…" statement + mispricing thesis.

---

### thesis-integrity-audit

Re-underwrites a position after a drawdown or material event.

**Inputs needed:** Original investment memo, updated financials, market reaction.

**Process:**
1. Re-underwrite fundamentals.
2. Compare new data vs original assumptions.
3. Determine permanent vs temporary impairment.
4. Update intrinsic value.

**Tools used:** `INCOME_STATEMENT`, `CASH_FLOW`, `OVERVIEW`, `calculate`, stock context.

**Output:** Hold / Add / Reduce / Exit decision.

---

### news-article-deep-dive

Fetches and analyses a full news article already visible in the stock context.

**Tools used (in order):**
1. `get_news_item_url(ticker, title_fragment)` — resolves the article URL from the news cache.
2. `fetch_url(url, max_chars=6000)` — retrieves the full article body.

**Fallback:** If no URL, summarise from the headline snippet already in context.

**Output:** Article summary with source, date, key facts, and investor angle (bull/bear/watch).

---

### position-sizing-concentration

Recommends position size and concentration tier after underwriting.

**Inputs needed:** Expected IRR, downside case, liquidity profile, portfolio exposure map.

**Process:**
1. Compute expected value.
2. Evaluate correlation to existing holdings.
3. Apply tier sizing model: 2–3% exploratory / 5–7% high conviction / 10%+ asymmetric core.
4. Simulate portfolio drawdown impact.

**Tools used:** `calculate`, `calculate_portfolio_exposure_map`, stock context.

---

### conviction-calibration-engine

Continuously aligns position size with current thesis conviction and edge.

**Inputs needed:** Expected asymmetry, thesis updates, market mispricing changes, risk profile.

**Process:**
1. Recalculate expected asymmetry.
2. Adjust size only if thesis improves, mispricing widens, or risk declines.
3. Prevent creeping overconfidence with explicit criteria.

**Tools used:** `calculate`, stock context, current thesis.

---

### portfolio-construction-optimizer

Ensures portfolio concentration without fragility.

**Inputs needed:** Current holdings, sector weights, beta exposure, factor exposures.

**Process:**
1. Evaluate top-5 concentration.
2. Stress test macro shocks: rate spike, liquidity freeze, demand collapse.
3. Identify hidden correlation clusters.

**Tools used:** `calculate_portfolio_exposure_map`, `pairs_trading_signal`, `pca_factor_decomposition`, `calculate`.

---

### daily-portfolio-monitoring

Detects thesis drift in real time using news, earnings, price moves, and filings.

**Inputs needed:** News flow, earnings releases, price moves, regulatory filings.

**Process:**
1. Map news to thesis assumptions.
2. Detect deviation from KPIs.
3. Identify volatility-driven opportunities.
4. Flag structural risk changes.

**Tools used:** Stock context news, `finnhub_company_news` (if news not loaded), `EARNINGS`, `GLOBAL_QUOTE`.

---

### exit-discipline-engine

Enforces rational sell decisions vs intrinsic value and opportunity cost.

**Inputs needed:** Current price, updated valuation, opportunity cost.

**Process:**
1. Compare price to intrinsic value.
2. Evaluate risk/reward reversal.
3. Assess superior capital alternatives.
4. Remove emotional bias.

**Tools used:** `OVERVIEW`, `GLOBAL_QUOTE`, `calculate`, current thesis.

---

### performance-attribution-error-analysis

Attributes returns and identifies decision errors to improve the investment process.

**Inputs needed:** Return data, benchmark data, decision log.

**Process:**
1. Attribute returns to stock selection, sector allocation, and macro exposure.
2. Identify mistake types: thesis error, timing error, sizing error.
3. Update playbook rules.

**Tools used:** `calculate`, `cross_sectional_regression`, historical price data.

---

### capital-preservation-protocol

Protects against permanent capital loss during elevated drawdown or leverage.

**Inputs needed:** Aggregate exposure, leverage, liquidity profile.

**Process:**
1. Stress test extreme downside.
2. Reduce fragile positions.
3. Increase liquidity buffer.
4. Protect core high-conviction holdings.

**Tools used:** `calculate_liquidity_profile`, `calculate_portfolio_exposure_map`, `calculate`.

---

### crisis-capital-allocation

Allocates capital during market-wide stress events.

**Inputs needed:** Liquidity position, portfolio drawdown, volatility spike.

**Process:**
1. Freeze non-essential activity.
2. Re-evaluate top-5 positions.
3. Rank opportunities by asymmetry.
4. Deploy capital selectively.

**Tools used:** `calculate_liquidity_profile`, `calculate`, stock context.

---

### activist-feasibility-analysis

Assesses whether activist engagement can unlock value.

**Inputs needed:** Ownership structure, board composition, voting thresholds, shareholder base.

**Process:**
1. Estimate influence threshold.
2. Evaluate management vulnerability.
3. Model value creation via intervention.
4. Assess legal and reputational risks.

**Tools used:** `sec_get_overview`, stock context, `calculate`.

**Output:** Passive / Engage / Full Activism decision + engagement roadmap.

---

### calculator

Precise arithmetic for any numeric request.

**Tools used:** `calculate(expression)` — safe arithmetic evaluator.

**Output:** Numeric result with units and rounding.

---

### anthropic-sdk

Reference skill for building AI applications with the Anthropic Python SDK.

**Tools used:** None (knowledge-only skill — provides code patterns and architecture guidance).

**Covers:** `Anthropic` client, `messages.create`, tool use loop, multi-agent orchestration, streaming, structured output, guardrails.

---

## Adding a new skill

1. Create `skills/basic/<folder-name>/SKILL.md` or `skills/advanced/<folder-name>/SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: <folder-name>
   description: <one-line trigger description for the agent's skill index>
   ---
   ```
2. Write the skill body: Purpose, Trigger, Inputs, Process (numbered steps), Tools used, Output.
3. Add it to the Skill Index table in this README.
4. Add it to the `── SKILL INDEX ──` section in `clients/agent_client.py`.

---

Part of [github.com/ternary-ai](https://github.com/ternary-ai) — open-source agents, models, synthetic data, prompt engineering resources, and scaffolding maintained for the community.

[contact@ternary.capital](mailto:contact@ternary.capital) · US · Japan · Est. 2020
