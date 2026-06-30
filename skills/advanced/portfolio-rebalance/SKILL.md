---
name: portfolio-rebalance
description: Compare current portfolio weights to target allocation (risk parity, equal weight, or user-specified), then output a trade list (buy/sell N shares) to reach target weights.
---

# Portfolio Rebalance

Purpose: Generate a rebalancing trade list to align current holdings with a target allocation strategy.

Trigger: User asks "rebalance my portfolio", "reallocate to equal weight", "shift to risk parity", or uses `/portfolio-rebalance`.

## Data Flow

### 1. Load Portfolio & Determine Target Strategy
- Check `<current_portfolio>` first — skip tool call if present.
- Otherwise: `load_portfolio(portfolio_id)`.
- Extract holdings, cash, total portfolio value.

**Target Strategy:**
- If user specifies "equal weight" or "equal allocation" → equal weight across all holdings.
- If user specifies "risk parity" or "risk-balanced" → call `risk_parity_weights()`.
- If user specifies "dynamic" or "Kelly" → call `dynamic_position_size()` for each holding.
- If user provides custom targets → parse them (e.g. "40% AAPL, 30% MSFT, 30% cash").
- **Default if unspecified**: call `request_user_input("Which rebalancing strategy?", "Equal weight|Risk parity|Dynamic (Kelly)|Custom targets")`.

### 2. Fetch Live Quotes
- For each ticker, call `GLOBAL_QUOTE(ticker)` to get current price.
- Compute current market value and weight % for each holding.
- **Batch in parallel** — single plan step for all quotes.

### 3. Compute Target Weights

**Equal Weight:**
```
target_weight = 1 / number_of_holdings (excluding cash)
```

**Risk Parity:**
- Fetch historical price data for volatility: `PRICE_HISTORY(ticker, period="1y")` for each holding.
- Compute annualised volatility for each ticker.
- Call `risk_parity_weights(volatilities_json)` → returns target weights inverse to volatility.

**Dynamic (Kelly):**
- For each holding: call `dynamic_position_size(ticker, expected_return, volatility, sharpe)`.
- User must provide expected returns or you must compute from analyst targets.
- Sum to 1.0 and normalise.

**Custom:**
- Parse user-provided target weights and validate they sum to ≤ 100% (remainder = cash).

### 4. Compute Trade List

For each holding:
```
current_value = shares × current_price
target_value = total_portfolio_value × target_weight
delta_value = target_value - current_value
delta_shares = delta_value / current_price
```

If `|delta_shares| < 1`, skip (no trade needed).

Output:
- BUY {ticker}: +N shares @ ${price} = ${value}
- SELL {ticker}: -N shares @ ${price} = ${value}

### 5. Rebalancing Cost Estimate
- Call `transaction_cost_estimate(trade_list_json)` to compute:
  - Total trade value.
  - Bid-ask spread impact (estimate 0.1% for liquid stocks, 0.5% for illiquid).
  - Estimated commission (if applicable).
  - Total rebalancing cost.

### 6. Render Output

**Current vs Target Table** — use `render_table()`:
| Ticker | Current Weight % | Target Weight % | Delta | Trade |
|---|---|---|---|---|
| AAPL | 48.6% | 33.3% | -15.3% | SELL 8 shares |
| MSFT | 49.9% | 33.3% | -16.6% | SELL 5 shares |
| TSLA | 0.0% | 33.3% | +33.3% | BUY 10 shares |
| Cash | 1.6% | 0.0% | -1.6% | Deploy $300 |

**Trade Summary**:
- Total trades: 3
- Total buy value: $X
- Total sell value: $Y
- Estimated cost: $Z (W% of portfolio)
- Net cash impact: ${buy_value - sell_value}

### 7. Thesis Upsert — MANDATORY

**This is an advanced skill** → append the rebalancing plan to the portfolio thesis. ⚠️ Extended thinking is discarded — copy the complete plan into the `thesis` field; it is the ONLY output that reaches the Thesis panel.

Thesis structure:
```markdown
## Portfolio Rebalance — {Date}

**Strategy**: {Equal Weight / Risk Parity / Dynamic / Custom}

{Current vs Target table}

### Trade List
1. SELL 8 shares of AAPL @ $185.00 = $1,480
2. SELL 5 shares of MSFT @ $380.00 = $1,900
3. BUY 10 shares of TSLA @ $175.00 = $1,750

**Estimated Cost**: ${Z} ({W}% of portfolio)  
**Net Cash Impact**: ${X} (deploy from cash / add to cash)

**Rationale**: {One sentence — e.g. "Reallocating to equal weight to reduce concentration risk."}
```

### 8. Chat Response

State in `chat` field:
- Rebalancing strategy used.
- Number of holdings before and after.
- Number of trades required.
- Estimated cost ($ and % of portfolio).
- Top rebalancing move (e.g. "Largest change: reduce MSFT by 16.6%").
- Tools used: `load_portfolio`, `GLOBAL_QUOTE`, `risk_parity_weights` (if used), `transaction_cost_estimate`, `render_table`.

## Cost Controls

- **Skip `load_portfolio()` if `<current_portfolio>` is present.**
- **Batch `GLOBAL_QUOTE()` calls** — single plan step.
- **Skip `PRICE_HISTORY()` if not doing risk parity** — equal weight requires no historical data.
- **Reuse session cache** — don't refetch quotes already in `<acquired_data>`.

## Error Handling

- If user specifies invalid custom targets (not summing to ≤100%), call `request_user_input("Invalid target weights. Provide new targets or choose a strategy:", "Equal weight|Risk parity|Cancel")`.
- If `GLOBAL_QUOTE(ticker)` fails, exclude that ticker from rebalancing but note it in `chat`.
- If `risk_parity_weights()` fails, fall back to equal weight and note in `chat`.

## Output Standards

- All weights as percentages with one decimal: 12.3%.
- Trade quantities as whole shares (no fractional).
- Dollar amounts formatted with commas: $1,234.56.
- Cost as percentage of portfolio with two decimals: 0.15%.
- Table must show current, target, and delta for all holdings.
