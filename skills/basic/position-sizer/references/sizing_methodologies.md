# Position Sizing Methodologies

## Overview

Position sizing determines how many shares to buy on each trade. Correct sizing is the single most important factor in long-term portfolio survival. A great stock pick with bad sizing can destroy an account; a mediocre pick with proper sizing preserves capital for the next opportunity.

---

## Fixed Fractional Method

### Concept
Risk a fixed percentage of the account on every trade. The most widely used method among professional traders, popularised by Van Tharp and applied by Mark Minervini and William O'Neil.

### Formula
```
risk_per_share = entry_price - stop_price
dollar_risk    = account_size * risk_pct / 100
shares         = int(dollar_risk / risk_per_share)
```

### Standard Risk Levels

| Risk % | Trader Profile | Notes |
|--------|---------------|-------|
| 0.25–0.50% | Conservative / large account | Institutional-grade |
| 0.50–1.00% | Experienced swing trader | Minervini recommended range |
| 1.00–1.50% | Active trader, proven edge | Standard for tested systems |
| 1.50–2.00% | Aggressive, high win-rate | Maximum for most strategies |
| > 2.00% | Dangerous | Ruin risk increases rapidly |

### Example
- Account: $100,000  
- Entry: $155.00, Stop: $148.50  
- Risk per share: $6.50  
- At 1% risk: $1,000 / $6.50 = **153 shares**  
- Position value: $23,715 (23.7% of account)

### When to Use
- Default method for most swing and position trades
- When you have a clear technical stop level (support, MA, prior low)
- When trading a system with established risk parameters

### Minervini / O'Neil Guidelines
- Risk no more than 1% per trade during early stages of a rally
- Tighten to 0.5% after consecutive losses
- Maximum portfolio heat (total open risk): 6–8%
- Cut losses at 7–8% below purchase price (hard maximum)

---

## ATR-Based Method (Volatility Sizing)

### Concept
Use Average True Range (ATR) to set stop distance, automatically adjusting position size to a stock's volatility. Originated with the Turtle Traders (Richard Dennis, 1983).

### Formula
```
stop_distance  = atr * atr_multiplier
stop_price     = entry_price - stop_distance
dollar_risk    = account_size * risk_pct / 100
shares         = int(dollar_risk / stop_distance)
```

### ATR Multiplier Guidance

| Multiplier | Stop Width | Style |
|-----------|-----------|-------|
| 1.0x | Tight | Day trading |
| 1.5x | Moderate | Swing trading, 2–5 day holds |
| 2.0x | Standard | Default for most swing trades |
| 2.5x | Wide | Position trading, 2–8 week holds |
| 3.0x | Very wide | Trend following, multi-month |

### Example
- Account: $100,000, Risk: 1%
- Entry: $155.00, ATR(14) = $3.20, Multiplier = 2.0x
- Stop distance: $6.40, Stop: $148.60
- Dollar risk: $1,000
- Shares: int($1,000 / $6.40) = **156 shares**

### When to Use
- When you want volatility-adjusted sizing across different stocks
- When a stock lacks clear support/resistance for a discrete stop
- For systematic/mechanical trading systems

### Advantages Over Fixed Stop
1. Low-volatility stocks get larger positions (tighter stop relative to price)
2. High-volatility stocks get smaller positions (wider stop protects against noise)
3. Normalises risk across the portfolio regardless of stock price

---

## Kelly Criterion

### Concept
The Kelly Criterion calculates the mathematically optimal fraction of capital to risk, given known win rate and payoff ratio. Developed by John L. Kelly Jr. (1956).

### Formula
```
R         = avg_win / avg_loss       (payoff ratio)
kelly_pct = W - (1 - W) / R          (full Kelly %)
half_kelly = kelly_pct / 2           (recommended)
```
Where W = historical win rate (0 to 1).

### Full Kelly vs. Half Kelly

| Metric | Full Kelly | Half Kelly | Quarter Kelly |
|--------|-----------|-----------|---------------|
| Growth rate | 100% | ~75% | ~50% |
| Max drawdown | Severe (50%+) | Moderate (25–35%) | Mild (15–20%) |
| Practical use | Never | Aggressive | Conservative |

**Use Half Kelly always.** Full Kelly produces extreme volatility that virtually no trader can psychologically sustain.

### Example
- Win rate: 55%, Avg win: $2.50, Avg loss: $1.00
- R = 2.5 / 1.0 = 2.5
- Kelly = 0.55 − 0.45 / 2.5 = 0.55 − 0.18 = **37%**
- Half Kelly = **18.5%**
- On $100,000 account: risk budget = $18,500

### Negative Expectancy
When the formula produces a negative value, the system has negative expected value — **do not trade it**. The Kelly % is floored at 0%.

Example of negative expectancy:
- Win rate: 30%, Avg win: $1.00, Avg loss: $1.50
- Kelly = 0.30 − 0.70 / 0.667 = **−0.75 → 0%**

### Two Modes of Use
1. **Budget Mode** (no entry price): Returns recommended risk % of account
2. **Shares Mode** (with entry + stop): Converts half-Kelly budget into specific share count

### When to Use
- After accumulating 100+ trade records with reliable statistics
- For portfolio-level capital allocation across strategies
- As a ceiling check: "Am I risking more than Kelly suggests?"
- NOT for discretionary traders without a track record

---

## Portfolio Constraints

### Maximum Position Size
Limit any single position to a % of account:
```
max_shares = int(account_size * max_position_pct / 100 / entry_price)
```

**Guidelines:**
- 5–10%: Conservative (10–20 positions)
- 10–15%: Moderate (7–10 positions)
- 15–25%: Aggressive (4–7 positions)
- > 25%: Speculative — not recommended

### Sector Concentration
Limit total exposure to any single sector:
```
remaining_pct     = max_sector_pct - current_sector_exposure
remaining_dollars = remaining_pct / 100 * account_size
max_shares        = int(remaining_dollars / entry_price)
```

**Guidelines:** Single sector max = 25–30% of portfolio

### Binding Constraint Logic
When multiple constraints apply, the strictest (minimum share count) wins. Priority order:
1. Risk-based shares (from Fixed Fractional, ATR, or Kelly)
2. Max position % limit
3. Max sector % limit
4. Final = minimum of all candidates

---

## Method Comparison

| Feature | Fixed Fractional | ATR-Based | Kelly |
|---------|-----------------|-----------|-------|
| Input needed | Entry, stop, risk % | Entry, ATR, multiplier, risk % | Win rate, avg win/loss |
| Adjusts for volatility | No | Yes | No |
| Requires track record | No | No | Yes (100+ trades) |
| Best for | Discretionary trades | Systematic | Capital allocation ceiling |
| Complexity | Low | Medium | Medium |

### Recommended Workflow
1. Start with Fixed Fractional at 1% for new strategies
2. Switch to ATR-based when comparing across different volatility profiles
3. Use Kelly as a ceiling after 100+ trade records
4. Always apply constraints (position limit, sector limit) as final filter
5. Reduce risk after consecutive losses

---

## Risk Management Principles

### The 1% Rule
Never risk more than 1% of account equity on a single trade:
- 10 consecutive losses at 1% = 9.6% drawdown (recoverable)
- 10 consecutive losses at 5% = 40.1% drawdown (devastating)
- 10 consecutive losses at 10% = 65.1% drawdown (account-threatening)

### Portfolio Heat
Total open risk across all positions should not exceed 6–8% of account:
```
portfolio_heat = sum(shares_i * risk_per_share_i) / account_size * 100
```

### Asymmetry of Losses

| Loss | Gain to Recover |
|------|----------------|
| 10% | 11.1% |
| 20% | 25.0% |
| 30% | 42.9% |
| 50% | 100.0% |
| 75% | 300.0% |

This asymmetry is why position sizing and loss-cutting are more important than stock selection.
