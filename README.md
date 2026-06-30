# Ternary Capital — Skills

**Agent-native finance. Build for markets.**

A library of cognitive agent skills for agentic financial intelligence. Skills are step-by-step playbooks loaded on demand ; covering research, portfolio management, risk, and crisis protocols.

---

## What is a Skill?

A skill is a structured playbook the agent loads via `read_skill("<name>")`. It defines which tools to call, in what order, and what defaults to apply. The agent never improvises tool sequences — it follows the loaded skill exactly.

Skills are organized into two tiers:

| Tier | Description |
|---|---|
| `basic/` | Utilities and data primitives: charting, tables, calculators, data sourcing |
| `advanced/` | Full investment workflows: underwriting, portfolio construction, risk, crisis |

---

## Skill Index

### Data Sourcing

| Skill | When to use | Output |
|---|---|---|
| `data-source` | Start of every quantitative request requiring external data | Data plan: which tool to call, in which order |
| `url-ingest` | User supplies an `https://` or `http://` link | Fetched and analysed content |
| `news-analysis` | User asks to check, summarise, or analyse news for a ticker | News fetch + sentiment summary |

### Charting & Visualisation

| Skill | When to use | Output |
|---|---|---|
| `chart-writeup` | User asks for a bar or line chart of financial or price data | `chart-bar` / `chart-line` fenced block |
| `standard-charts` | Called internally by `chart-writeup` to look up defaults | Canonical chart type, time frame, unit, and tool |
| `graph-writeup` | User asks for a relationship map, peer network, or business model diagram | Mermaid `graph` block |
| `table-writeup` | User asks to present data in a table | Markdown table |

### Research & Analysis

| Skill | When to use | Output |
|---|---|---|
| `equity-research-report` | Full institutional research report with BUY/SELL/HOLD and price target | 8-section report with recommendation table |
| `investment-quick-screen` | New ticker, pitch, or idea needs initial screening | Proceed / Reject + 1-page hypothesis |
| `deep-fundamental-underwriting` | Post-triage: full intrinsic value and earnings power analysis | Intrinsic value band, IRR distribution, investment memo |
| `variant-perception-detection` | After underwriting: find where consensus is wrong | "Market is wrong because…" + mispricing thesis |
| `thesis-integrity-audit` | Position down 10%+ or material event occurs | Hold / Add / Reduce / Exit decision |
| `news-article-deep-dive` | User asks to explain or analyse a headline in stock context | Full article summary with investor angle |
| `technical-analyst` | User provides chart images and requests technical analysis | Trend, support/resistance, pattern, probability-weighted targets |
| `explain` | User asks about a financial concept, mechanism, or term | Plain-English explanation |
| `compare` | User wants to compare tickers, segments, or time periods | Summary comparison table |
| `backtest-expert` | Developing, testing, or validating a quantitative strategy | Deploy / Refine / Abandon verdict + methodology report |
| `options-strategy-advisor` | User asks about options strategies, P/L simulation, or Greeks | Strategy comparison, P/L diagram, Greeks breakdown |

### Portfolio & Position Management

| Skill | When to use | Output |
|---|---|---|
| `portfolio-snapshot` | Load portfolio with live quotes | Market value, unrealised P&L, weights table + allocation chart |
| `position-sizer` | User asks how many shares to buy or how to size a trade | Risk-based position size (Fixed Fractional / ATR / Kelly) |
| `position-sizing-concentration` | Idea has passed triage and underwriting | Recommended position size and concentration tier |
| `conviction-calibration-engine` | Ongoing management or after a thesis update | Size adjustment recommendation |
| `portfolio-construction-optimizer` | Adding a new position or quarterly review | Rebalancing recommendation + concentration health score |
| `portfolio-rebalance` | Compare current weights to target allocation | Trade list: buy/sell N shares per holding |
| `daily-portfolio-monitoring` | Daily execution cycle | Thesis intact / weakened / broken + action recommendation |
| `exit-discipline-engine` | Position near full valuation or fundamentals deteriorating | Exit / Trim / Maintain decision |
| `portfolio-risk-report` | Check concentration, sector exposure, and factor correlations | Risk breakdown table with breach flags |
| `portfolio-stress-test` | Scenario stress test across all holdings | Portfolio-level P&L per scenario (crash, rate shock, recession) |
| `portfolio-performance-attribution` | Portfolio-level return attribution rollup | Position contributors, factor attribution, error patterns |
| `performance-attribution-error-analysis` | Monthly or quarterly review of a single position | Performance report + process refinements |

### Risk & Crisis

| Skill | When to use | Output |
|---|---|---|
| `capital-preservation-protocol` | Portfolio drawdown exceeds threshold or leverage elevated | Defensive restructuring plan |
| `crisis-capital-allocation` | Market-wide stress, volatility spike, or liquidity crisis | Capital deployment plan + liquidity survival assessment |
| `activist-feasibility-analysis` | Holding shows persistent underperformance + governance misalignment | Passive / Engage / Full Activism decision + engagement roadmap |

### Utilities

| Skill | When to use | Output |
|---|---|---|
| `calculator` | Arithmetic, percentages, ratios, growth rates, unit conversions | Precise numeric result with units |
| `anthropic-sdk` | Building or modifying AI applications with the Anthropic SDK | Code and architecture guidance |

Full step-by-step documentation for each skill: [skills/README.md](skills/README.md)

---

## Adding a Skill

1. Create `skills/basic/<name>/SKILL.md` or `skills/advanced/<name>/SKILL.md`
2. Add YAML frontmatter: `name`, `description` (one-line trigger for the agent)
3. Write: Purpose · Trigger · Inputs · Process · Tools · Output
4. Register it in the Skill Index in [skills/README.md](skills/README.md)

---

Part of [github.com/ternary-ai](https://github.com/ternary-ai) — open-source agents, models, synthetic data, prompt engineering, and scaffolding.

[contact@ternary.capital](mailto:contact@ternary.capital) · US · Japan · Est. 2020
