---
name: portfolio-snapshot
description: Load a portfolio, fetch live quotes for all holdings, compute market value, unrealised P&L, allocation weights, and render results as a table and allocation chart.
---

# Portfolio Snapshot

Purpose: Provide a real-time view of portfolio holdings with current market values, unrealised gains/losses, and allocation breakdown.

Trigger: User asks "show my portfolio", "portfolio snapshot", "what's in my portfolio", or uses `/portfolio-snapshot`.

## Data Flow

### 1. Load Portfolio Context
- **Check `<current_portfolio>` first** — if present, skip `load_portfolio()` tool call.
- If not present: call `load_portfolio(portfolio_id)` to read the JSON.
- Extract: holdings list, cash balance, portfolio name.

### 2. Fetch Live Quotes — Batch in Parallel
- For each ticker in holdings, call `GLOBAL_QUOTE(ticker)` to get current price.
- **Session cache rule**: Check `<acquired_data>` first — if quote already exists from this session, do not refetch.
- If any ticker returns an error, note it in the output but continue with others.

### 3. Compute Metrics for Each Holding

For each position:
```
Market Value = shares × current_price
Cost Basis = shares × avg_cost
Unrealised P&L = Market Value - Cost Basis
% Gain/Loss = (Unrealised P&L / Cost Basis) × 100
Weight % = (Market Value / Total Portfolio Value) × 100
```

Where `Total Portfolio Value = Cash + Sum(all market values)`.

### 4. Render Output

**Table** — use `render_table()`:
| Ticker | Shares | Avg Cost | Current Price | Market Value | Unrealised P&L | % Gain/Loss | Weight % |
|---|---|---|---|---|---|---|---|
| AAPL | 50 | $172.30 | $185.00 | $9,250 | $635 | +3.7% | 48.6% |
| MSFT | 25 | $350.00 | $380.00 | $9,500 | $750 | +8.6% | 49.9% |
| Cash | — | — | — | $300 | — | — | 1.6% |
| **Total** | — | — | — | **$19,050** | **$1,385** | **+7.8%** | **100%** |

**Allocation Chart** — use `generate_chart()`:
- Type: `bar` or `pie` (bar preferred for 5+ holdings)
- Series: `[{label: "AAPL", value: 48.6}, {label: "MSFT", value: 49.9}, {label: "Cash", value: 1.6}]`
- X-axis: Ticker
- Y-axis: Weight %
- Title: "{Portfolio Name} — Allocation Breakdown"
- Unit: "%"

### 5. Thesis Upsert — MANDATORY

**This is an advanced skill** → the snapshot table and chart MUST be appended to the portfolio's thesis section. ⚠️ Extended thinking is discarded — copy the complete snapshot into the `thesis` field; it is the ONLY output that reaches the Thesis panel.

Thesis structure:
```markdown
## Portfolio Snapshot — {Date}

{Table from render_table()}

{Chart spec from generate_chart()}

**Summary**: Total value ${X}, cash ${Y} ({Z}%), unrealised P&L ${A} ({B}%).
Top holding: {ticker} at {weight}%.
```

If no portfolio thesis exists, create the header:
```markdown
# {Portfolio Name} Portfolio Analysis
_{Date}_

## Portfolio Snapshot — {Date}
...
```

### 6. Chat Response

State in `chat` field:
- Portfolio name and total value.
- Number of holdings.
- Total unrealised P&L ($ and %).
- Largest position (ticker and weight %).
- Tools used: `load_portfolio` (or skipped if context present), `GLOBAL_QUOTE` (N times), `render_table`, `generate_chart`.

## Cost Controls

- **Skip `load_portfolio()` if `<current_portfolio>` is present** — this is injected automatically when the user's message references a portfolio.
- **Batch quote fetches in a single plan step** rather than sequential calls.
- **Check session cache** (`<acquired_data>`) before calling `GLOBAL_QUOTE` — if already fetched this session, reuse it.

## Error Handling

- If a ticker's quote fetch fails, set `current_price = null` and exclude from P&L calculation but show in table with "—" for price.
- If portfolio file not found, call `request_user_input("No portfolio loaded. Create one or specify portfolio ID?", "Create new portfolio|Load existing portfolio|Cancel")`.

## Output Standards

- All dollar amounts formatted with commas: $1,234.56.
- Percentages with one decimal: 12.3%.
- Table must include a Total row.
- Chart must render successfully — if `generate_chart()` errors, fall back to table only and note it in `chat`.
