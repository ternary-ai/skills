---
name: options-strategy-advisor
description: Options strategy analysis, education, and simulation. Use when the user asks about options strategies (covered calls, iron condors, spreads, straddles, etc.), wants P/L simulation, Greeks calculation, earnings plays, or volatility analysis. Uses Black-Scholes theoretical pricing. FMP API optional for live stock data; all core analysis works with user-provided inputs.
---

# Options Strategy Advisor

## Overview

Comprehensive options strategy analysis using theoretical pricing models. Helps traders understand, analyse, and simulate options strategies without requiring real-time options data subscriptions.

**Core Capabilities:**
- **Black-Scholes Pricing**: Theoretical option prices and Greeks
- **Strategy Simulation**: P/L analysis for 17+ strategies
- **Earnings Strategies**: Pre-earnings volatility plays
- **Risk Management**: Position sizing, Greeks exposure, max loss/profit
- **Educational Focus**: Clear explanations of every strategy

## When to Use

- "What's a covered call?" / "How does an iron condor work?"
- "What's my max profit on a bull call spread?"
- "Should I buy a straddle before NVDA earnings?"
- "Calculate my delta exposure"
- "How many contracts should I trade?"
- "Is IV high right now?"

## Supported Strategies

**Income**: Covered Call, Cash-Secured Put, Poor Man's Covered Call  
**Protection**: Protective Put, Collar  
**Directional**: Bull Call Spread, Bull Put Spread, Bear Call Spread, Bear Put Spread  
**Volatility**: Long Straddle, Long Strangle, Short Straddle, Short Strangle  
**Range-Bound**: Iron Condor, Iron Butterfly  
**Advanced**: Calendar Spread, Diagonal Spread, Ratio Spread

## Analysis Workflow

### Step 1: Gather Inputs

**Required from user:**
- Ticker symbol
- Strategy type
- Strike prices
- Expiration date(s)
- Number of contracts

**Optional from user:**
- Implied Volatility (IV) — if not provided, use Historical Volatility calculated from price data
- Risk-free rate — default to current 3-month T-bill rate (~5.3%)

**If FMP API is available:** Fetch current stock price, 90 days of historical prices (for HV), dividend yield, and upcoming earnings date.

### Step 2: Calculate Historical Volatility (if IV not provided)

```python
# 90 days of daily prices → daily log returns → annualise
import numpy as np
returns = np.log(prices / prices.shift(1)).dropna()
HV = returns.std() * np.sqrt(252)  # annualised
```

Note to user: "HV = XX%. Provide current IV from your broker for better accuracy."

### Step 3: Price Options with Black-Scholes

```
d1 = [ln(S/K) + (r - q + σ²/2) × T] / (σ × √T)
d2 = d1 - σ × √T

Call = S × e^(−qT) × N(d1) − K × e^(−rT) × N(d2)
Put  = K × e^(−rT) × N(−d2) − S × e^(−qT) × N(−d1)

S = Current stock price, K = Strike, r = Risk-free rate,
T = Time to expiry (years), σ = Volatility, q = Dividend yield
```

Note: Black-Scholes assumes European-style options. For American options, actual market prices may be slightly higher for ITM puts.

### Step 4: Calculate Greeks

| Greek | Meaning | Direction |
|-------|---------|-----------|
| **Delta (Δ)** | $ change per $1 stock move | Call: 0 to +1; Put: −1 to 0 |
| **Gamma (Γ)** | Delta change per $1 stock move | Always positive for long options |
| **Theta (Θ)** | $ decay per day | Negative for long, positive for short |
| **Vega (ν)** | $ change per 1% IV move | Positive for long, negative for short |
| **Rho (ρ)** | $ change per 1% rate move | Minor for most short-dated options |

**Position Greeks** = sum of (leg quantity × individual leg Greek) across all legs.

### Step 5: Simulate P/L at Expiration

Generate price range ±30% from current price. For each price point:
- Long option: max(0, intrinsic_value) − premium_paid
- Short option: premium_received − max(0, intrinsic_value)

**Key metrics:**
- Max Profit, Max Loss
- Breakeven point(s)
- Probability of profit (% of range that's profitable)

### Step 6: Generate ASCII P/L Diagram

Present a visual P/L diagram showing profit (█), loss (░), breakeven (─), and current price (│) across the price range.

### Step 7: Provide Strategy-Specific Analysis

Present tailored guidance:

**Covered Call:**
```
Setup: Own 100 shares, sell OTM call
Max Profit: (short_strike - cost_basis + premium) × 100
Max Loss: Cost basis - premium received (owns stock)
Breakeven: Cost basis - premium received
Use when: Neutral to slightly bullish, want income
Risk: Shares called away if above short strike
```

**Iron Condor:**
```
Setup: Bull put spread + bear call spread (4 legs)
Max Profit: Net credit received
Max Loss: Spread width - net credit
Breakeven: Lower breakeven and upper breakeven
Profit zone: Between the two short strikes
Use when: Expect low volatility, range-bound movement
```

**Long Straddle (Earnings Play):**
```
Setup: Buy ATM call + ATM put
Max Profit: Unlimited (either direction)
Max Loss: Total premium paid
Breakeven: Current price ± total premium
Use when: Expect big move but unsure of direction
⚠️ IV CRUSH RISK: Pre-earnings IV typically collapses 40-60% post-announcement
  IV drop example: 40% → 25% IV = -$750 loss even if stock doesn't move
```

**Short Iron Condor (Earnings):**
```
⬆ Benefits from IV crush post-earnings
Setup: Sell OTM put spread + OTM call spread
Profit if: Stock stays within the two short strikes
Use when: Expect normal earnings reaction (<8% move)
```

### Step 8: Earnings Strategy Analysis

When the user asks about earnings options plays:

1. Calculate days to earnings (DTE is critical for IV)
2. Estimate IV percentile if user provides current IV
3. Calculate implied move: `± IV × √(DTE/365) × S`
4. Compare implied move vs. breakeven needed
5. Recommend long volatility (straddle/strangle) if expecting move > implied; short volatility (iron condor) if expecting normal reaction
6. **Always warn about IV crush**: IV typically drops 30–60% immediately after earnings

**IV guidance:**
- IV > 75th percentile → Consider selling premium (iron condors, credit spreads)
- IV < 25th percentile → Consider buying options (long calls/puts, debit spreads)
- IV ≈ 50th percentile → Any strategy appropriate

### Step 9: Risk Management and Position Sizing

```
Max risk per trade = account_size × risk_tolerance %
Max contracts = int(max_risk / max_loss_per_contract)

Example: $50,000 account, 2% risk = $1,000 max
Iron Condor max loss = $300 → max 3 contracts
Bull Call Spread max loss = $250 → max 4 spreads
```

**Portfolio Greeks guidelines:**
- Delta: Keep within −10 to +10 per position (mostly neutral)
- Theta: Positive preferred (time decay working for you)
- Vega: Monitor if > $500; if short vega + VIX rising → reduce exposure

**Exit rules by strategy:**
| Strategy | Profit Target | Stop Loss | Time Rule |
|----------|--------------|-----------|-----------|
| Spreads | 50% of max profit | 2× debit | Close at 21 DTE |
| Iron Condor | 50% of credit | One side tested (2× credit) | Close at 21 DTE |
| Covered Call | 50–75% of premium | Stock drops >5% | Roll at 7–10 DTE |
| Straddle | Breakeven exceeded | Theta eating without move | Day after earnings |

## Output Format

```markdown
# Options Strategy Analysis: [STRATEGY] on [TICKER]
**Date**: [YYYY-MM-DD]  
**Expiration**: [Date] ([DTE] days)  
**Contracts**: [N]

## Strategy Setup
| Leg | Type | Strike | Theoretical Price | Position |
|-----|------|--------|-------------------|----------|
| 1   | Call | $XXX   | $X.XX             | Long     |
| 2   | Call | $XXX   | $X.XX             | Short    |

**Net Debit / Credit**: $X.XX

## P/L Analysis
- **Max Profit**: $XXX (at $XXX+)
- **Max Loss**: −$XXX (at $XXX−)
- **Breakeven**: $XXX
- **Risk/Reward**: X:X

## Greeks (1 spread)
| Greek | Value | Interpretation |
|-------|-------|----------------|
| Delta | +X.XX | Gains $XX if stock +$1 |
| Theta | −$X/day | Loses $X daily from time decay |
| Vega  | +$XX | Gains $XX if IV increases 1% |

## P/L Diagram
[ASCII diagram]

## Risk Assessment
- Max loss is XX% of account
- Earnings on [date] — [IV crush warning if applicable]

## Trade Management
- **Enter if**: [conditions]
- **Target (50% profit)**: [price]
- **Stop loss**: [trigger and action]
- **Roll/adjust**: [when and how]

---
*Theoretical pricing via Black-Scholes. Actual market prices will differ. Not financial advice.*
```

## Key Principles

### Black-Scholes Limitations
1. European-style pricing (no early exercise)
2. Assumes constant volatility (IV varies in practice)
3. No transaction costs in formula
4. Use as educational benchmark, not precise market price
5. Actual mid-market price ≈ theoretical; get real quotes from broker before trading

### Volatility Framework
- **HV (Historical Volatility)**: What happened — calculated from past prices, objective
- **IV (Implied Volatility)**: What market expects — derived from option prices, user provides
- When IV >> HV: Options expensive → consider selling premium
- When IV << HV: Options cheap → consider buying

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete options strategy analysis. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete analysis into the `thesis` field; it is the ONLY output that reaches the Thesis panel.
