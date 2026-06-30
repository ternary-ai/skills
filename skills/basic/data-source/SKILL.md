```skill
---
name: data-source
description: "Universal data-source resolver. Call this skill at the start of EVERY quantitative request — before fetching anything — to identify which tool or API to use. Maps any data need (financials, price, dividends, news, filings, insider, options, transcripts, peers, etc.) to the correct tool and priority order. Always check <stock_context> and <acquired_data> first before making any API call."
---

# Data Source Resolver

This skill is the **first call for every quantitative request**. It prevents blind API calls and stops the agent asking users for data it can source itself.

**Do not call any data tool before consulting this skill.**

---

## Rule 1 — Check context before fetching

Before calling any tool, scan:

1. **`<stock_context>`** — pre-loaded per-session snapshot. Contains: latest price, price change %, 52-week range, market cap, sector/industry, recent news headlines, financial statement summary (income, cash flow), insider trades, technical signals, SEC filings list.
2. **`<acquired_data>`** — everything the agent has already fetched in this session.

If 3 or more valid (non-null, numeric) data points exist in context → use them directly. Do **not** fetch.

If context is insufficient (fewer than 3 valid points, data type absent, or stale) → proceed to the source map below.

---

## Rule 2 — Never ask the user for data you can fetch

The only time to call `request_user_input` about data is when:
- All tools in the priority chain below have been tried **and** all failed with explicit errors.
- The metric requires user-specific information that no API can provide (e.g. a private portfolio cost basis).

**Dividend data is explicitly exempted from `request_user_input` under any circumstance.** `get_dividend_history` is always available and always authoritative. Asking the user for dividend amounts, DPS figures, or yield values is a hard failure — call `get_dividend_history` instead.

---

## Data Source Map

### Financial Statements (Income, Cash Flow, Balance Sheet)

| Data need | Check context first? | Tool (priority order) | Key response fields |
|---|---|---|---|
| Revenue, gross profit, operating income | ✅ `<stock_context>` financials | `INCOME_STATEMENT(symbol)` → `annualReports[]` / `quarterlyReports[]` | `totalRevenue`, `grossProfit`, `operatingIncome` |
| Net income, EPS (annual) | ✅ | `INCOME_STATEMENT(symbol)` | `netIncome`, `eps` |
| EPS (quarterly, beat/miss) | ✅ | `EARNINGS(symbol)` | `quarterlyEarnings[].reportedEPS`, `estimatedEPS`, `surprise` |
| D&A, operating cash flow, capex, FCF | ✅ | `CASH_FLOW(symbol)` | `operatingCashflow`, `capitalExpenditures`, `depreciationDepletionAndAmortization` |
| EBITDA | ✅ | `INCOME_STATEMENT` + `CASH_FLOW` → compute: `operatingIncome + D&A`; proxy: `netIncome + interestExpense + incomeTaxExpense + D&A` if income stmt fails (omit missing terms but label as approximate) | — |
| Balance sheet (assets, liabilities, equity, debt, cash) | ✅ | `BALANCE_SHEET(symbol)` | `totalAssets`, `totalLiabilities`, `totalShareholderEquity`, `longTermDebt`, `cashAndCashEquivalentsAtCarryingValue` |
| Company overview (market cap, P/E, sector, description) | ✅ | `OVERVIEW(symbol)` | `MarketCapitalization`, `PERatio`, `ForwardPE`, `52WeekHigh`, `52WeekLow`, `Sector` |
| Key statistics (valuation multiples, margins, float) | ✅ | `yahoo_key_statistics(ticker)` | `trailingPE`, `forwardPE`, `priceToBook`, `profitMargins`, `floatShares` |

> **Alpha Vantage tools** (`INCOME_STATEMENT`, `CASH_FLOW`, `BALANCE_SHEET`, `EARNINGS`, `OVERVIEW`) are called as direct Python function tools by exact name with `symbol=` parameter. If a tool returns a top-level `"Information"`, `"Note"`, or `"Error Message"` key — that is an API error. Report the exact string in `chat`, then try the next tool in the chain.

---

### Price & Market Data

| Data need | Check context first? | Tool | Key response fields |
|---|---|---|---|
| Current price, % change, volume | ✅ `<stock_context>` price block | `yahoo_key_statistics(ticker)` → `price` dict | `regularMarketPrice`, `regularMarketChangePercent` |
| Daily OHLCV / price history (free) | ✅ if recent | `PRICE_HISTORY(symbol, period="2y")` or `PRICE_HISTORY(symbol, start="2025-01-01", end="2025-12-31")` | `rows[].date`, `rows[].close` |
| Daily OHLCV / price history (AV, premium key) | ✅ if recent | `TIME_SERIES_DAILY(symbol, outputsize="full")` ⚠️ requires premium AV key; free key returns only last 100 days | date keys → `"4. close"` |
| Intraday price | ❌ never in context | `TIME_SERIES_INTRADAY(symbol)` | `"Time Series (5min)"[datetime]["4. close"]` |
| Technical indicators (SMA, EMA, RSI, MACD) | ✅ partial | `fetch_technical_insights(ticker)` — Trading Central / Argus | `outlooks`, `keyTechnicals`, `recommendation` |
| 52-week range | ✅ `<stock_context>` | `yahoo_key_statistics(ticker)` | `fiftyTwoWeekHigh`, `fiftyTwoWeekLow` |

---

### Dividends & Yield

> ⚠️ **Dividend data is NEVER in `<stock_context>` or in any Alpha Vantage endpoint.** Always call `get_dividend_history` — do not look in context, do not ask the user.

> ⛔ **NEVER call `request_user_input` for dividend amounts, DPS values, or yield figures.** `get_dividend_history` always has the authoritative payment history. Use the `dividendHistory[].amount` values verbatim — do not derive per-payment amounts from `trailingAnnualDividendRate` (that field is a trailing sum, not a per-payment figure).

| Data need | Tool | Key response fields |
|---|---|---|
| Dividend payment history (any period) | `get_dividend_history(ticker, period="max")` | `dividendHistory[].date`, `dividendHistory[].amount` |
| Trailing annual yield / rate | `get_dividend_history(ticker)` | `trailingAnnualDividendYield`, `trailingAnnualDividendRate` |
| 5-year average yield | `get_dividend_history(ticker)` | `fiveYearAvgDividendYield` |
| Payout ratio | `get_dividend_history(ticker)` | `payoutRatio` |
| Annual DPS (per calendar year) | `get_dividend_history(ticker, period="5y")` → sum `dividendHistory[].amount` per year | — |

---

### News & Sentiment

| Data need | Check context first? | Tool (priority order) | Notes |
|---|---|---|---|
| Recent headlines (cached) | ✅ `<stock_context>` news | `get_cached_news(ticker)` — instant, no API call | Use unless headlines are >24 h stale |
| Fresh news | ❌ | `fetch_news(ticker)` → Benzinga + TickerTick + MarketAux aggregated | Prefer over individual sources |
| Sentiment scores | ❌ | `alphavantage_news_sentiment(ticker)` | Returns ticker sentiment label + score |
| Finnhub headlines | ❌ | `finnhub_company_news(ticker, days=7)` | Good for same-day events |
| Benzinga specifically | ❌ | `benzinga_news(ticker)` | Use when Benzinga sourcing is required |
| News article full text | ❌ | `get_news_item_url(ticker, title_fragment)` → `fetch_url(url)` | Two-step: resolve URL then fetch body |
| Conference call transcripts | ❌ | `benzinga_transcript_calls()` → `benzinga_transcript_call(call_id)` or `benzinga_transcript_summary(call_id)` | List then fetch specific call |

---

### SEC Filings

| Data need | Tool | Notes |
|---|---|---|
| List of recent filings (10-K, 10-Q, 8-K) | `sec_search_filings(ticker)` | Returns filing URLs + types |
| Full section of a filing (MD&A, Risk Factors) | `sec_get_section(filing_url, section_id)` | section_id: "1A", "7", "8" etc. |
| Company SEC overview (CIK, filing history) | `sec_get_overview(ticker)` | — |

---

### Insider & Institutional Activity

| Data need | Tool (priority order) | Notes |
|---|---|---|
| Insider buys/sells (Yahoo/SEC) | `fetch_insider_transactions(ticker)` | Uses yahooquery — most reliable |
| Insider transactions (Alpha Vantage) | `alphavantage_insider_transactions(ticker)` | Fallback |
| Insider transactions (Benzinga SEC) | `benzinga_sec_insider_transactions(symbol=ticker)` | Most granular, use for deep dives |
| Management purchase activity summary | `fetch_insider_transactions(ticker)` → `summary` block | 6-month buy/sell counts + share totals |

---

### Government & Senate Trades

| Data need | Tool | Notes |
|---|---|---|
| US Senate eFD trades | `get_senate_trades(ticker)` | Periodic transaction reports |
| Benzinga government trades | `benzinga_government_trades(symbols=ticker)` | Broader gov coverage |
| Benzinga government reports | `benzinga_government_trade_reports(symbols=ticker)` | Summarised reports |
| Lobbying activity | `finnhub_stock_lobbying(ticker)` | Federal lobbying disclosures |

---

### Options & Derivatives

| Data need | Tool | Notes |
|---|---|---|
| Unusual options flow / large prints | `benzinga_unusual_options(tickers=ticker)` | Block trades, sweeps, unusual size |

---

### Peers & Comparables

| Data need | Tool | Notes |
|---|---|---|
| Peer list | `fmp_company_peers(ticker)` | FMP sector/industry peers |
| Peer 1-year performance vs focal ticker | `fmp_peers_performance(ticker)` | Returns peers + % return for chart |
| Related tickers (Yahoo similarity) | `fetch_recommendations(ticker)` | Yahoo recommendation engine |

---

### Qualitative / Company Profile

| Data need | Check context first? | Tool | Notes |
|---|---|---|---|
| Business description, sector, industry | ✅ `<stock_context>` | `yahoo_ticker_metadata(ticker)` → `asset_profile` | CEO, employees, description |
| Corporate events (M&A, buybacks, guidance) | ✅ `<stock_context>` | `fetch_corporate_events(ticker)` | Significant corporate actions |
| Bulls/Bears analyst views | ❌ | `benzinga_bulls_bears_say(symbols=ticker)` | Structured bull vs bear arguments |
| Multi-agent analysis score | ❌ | `get_analysis_report(ticker)` | Entry/risk/exit/valuation sub-scores |

---

### Calculations (no external API)

| Data need | Tool | Notes |
|---|---|---|
| Arithmetic, %, ratios | `calculate(expression)` | Safe eval; no API call |
| IRR, MOIC, NPV | `calculate_irr(...)` | Entry/exit/dividend/holding; or cash_flows_json |

---

## Fallback Chain (when a tool fails)

```
1. Try primary tool from map above.
2. If API error (check for "Information" / "Note" / "Error Message" key):
   a. Report exact error string in `chat`.
   b. Try the next tool in priority order.
3. If all tools for a category fail:
   a. For financial statements: try OVERVIEW for single-period fallback values.
   b. For price: yahoo_key_statistics has trailing metrics.
   c. For news: try finnhub_company_news or benzinga_news as independent fallbacks.
4. Only if ALL tools exhausted → call request_user_input with a specific question
   naming the exact data point needed.
```

---

## Output of this skill

After loading this skill, the agent outputs a **data plan** — a short numbered list (in the agent's `thought`) naming:
1. Which data is already in context (can be used immediately).
2. Which tools to call, in which order, for the missing pieces.
3. What to compute from the fetched data.

Then the agent executes the plan before rendering any output.

```
