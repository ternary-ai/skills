---
name: backtest-expert
description: Expert guidance for systematic backtesting and strategy validation. Use when developing, testing, stress-testing, or validating quantitative trading strategies. Covers robustness methodology, parameter sensitivity, slippage modeling, bias prevention (survivorship, look-ahead, curve-fitting), sample size requirements, and interpreting backtest results with a Deploy/Refine/Abandon verdict. No API key required.
---

# Backtest Expert

## Core Philosophy

**Goal**: Find strategies that "break the least", not strategies that "profit the most" on paper.

**Principle**: Add friction, stress test assumptions, and see what survives. A strategy that holds up under pessimistic conditions is far more likely to work in live trading than one that looks perfect in hindsight.

**Time allocation**: Spend 20% generating ideas, 80% trying to break them.

## When to Use

- Developing or validating systematic trading strategies
- Evaluating whether a trading idea is robust enough for live implementation
- Troubleshooting why a backtest might be misleading
- Learning proper backtesting methodology
- Avoiding common pitfalls (curve-fitting, look-ahead bias, survivorship bias)
- Assessing parameter sensitivity and regime dependence
- Setting realistic expectations for slippage and execution costs

## Workflow

### Step 1: State the Hypothesis

Define the edge in one clear sentence.

**Example**: "Stocks that gap up >3% on earnings and pull back to the prior day's close within the first hour provide a mean-reversion opportunity."

If you cannot articulate the edge clearly, do not proceed to testing.

### Step 2: Codify Rules with Zero Discretion

Define with complete specificity — no subjective judgment allowed:

- **Entry**: Exact conditions, timing, price type (open, close, limit, stop)
- **Exit**: Stop loss, profit target, time-based exit — all rule-based
- **Position sizing**: Fixed $, % of portfolio, or volatility-adjusted
- **Filters**: Market cap, volume, sector, volatility conditions
- **Universe**: What instruments are eligible (and why)

### Step 3: Run Initial Backtest

Test over:
- **Minimum 5 years** (preferably 10+)
- **Multiple market regimes** (bull, bear, high/low volatility)
- **Realistic costs**: Commissions + conservative slippage

Examine initial results for basic viability. If fundamentally broken, iterate on hypothesis before proceeding.

### Step 4: Stress Test the Strategy

This is where 80% of testing time belongs.

**Parameter sensitivity:**
- Test stop loss at 50%, 75%, 100%, 125%, 150% of baseline
- Test profit target at 80%, 90%, 100%, 110%, 120% of baseline
- Vary entry/exit timing by ±15–30 minutes
- Look for "plateaus" of stable performance, not narrow spikes

**Execution friction:**
- Increase slippage to 1.5–2x typical estimates
- Model worst-case fills (buy at ask+1 tick, sell at bid−1 tick)
- Add realistic order rejection scenarios
- Test with pessimistic commission structures

**Time robustness:**
- Analyse year-by-year performance
- Require positive expectancy in majority of years
- Ensure strategy doesn't rely on 1–2 exceptional periods
- Test in different market regimes separately

**Sample size requirements:**

| Trades | Confidence Level |
|--------|----------------|
| < 30 | No statistical meaningfulness — stop here |
| 30–100 | Preliminary only — results directional at best |
| 100–200 | Acceptable for initial deployment at small size |
| 200+ | High confidence — suitable for full deployment |

### Step 5: Out-of-Sample Validation

**Walk-forward analysis:**
1. Optimise on training period (e.g., Years 1–3)
2. Test on validation period (Year 4)
3. Roll forward and repeat
4. Compare in-sample vs. out-of-sample performance

**Warning signs:**
- Out-of-sample < 50% of in-sample performance
- Need frequent parameter re-optimisation
- Parameters change dramatically between periods

### Step 6: Evaluate and Render Verdict

**Questions to answer:**
- Does the edge survive pessimistic assumptions?
- Is performance stable across parameter variations?
- Does the strategy work in multiple market regimes?
- Is the sample size sufficient for statistical confidence?
- Are results realistic, or "too good to be true"?

**Decision criteria:**

| Verdict | Criteria |
|---------|---------|
| ✅ **Deploy** | Survives all stress tests with acceptable performance; positive expectancy in most years; parameters stable |
| 🔄 **Refine** | Core logic sound but needs parameter adjustment; some regime weakness; execution assumptions need tightening |
| ❌ **Abandon** | Fails stress tests; relies on fragile assumptions; negative expectancy with realistic costs; small sample |

Present the verdict with supporting rationale for each dimension.

## Key Testing Principles

### Punish the Strategy
Add friction everywhere:
- Commissions higher than reality
- Slippage 1.5–2x typical
- Worst-case fills
- Order rejections and partial fills

**Rationale**: Strategies that survive pessimistic assumptions often outperform expectations in live trading.

### Seek Plateaus, Not Peaks
Look for parameter ranges where performance is stable, not optimal single values.

- **Good**: Strategy profitable with stop loss anywhere from 1.5% to 3.0%
- **Bad**: Strategy only works at exactly 2.13%

Narrow performance peaks indicate curve-fitting, not genuine edge.

### Test All Cases, Not Cherry-Picked Examples
- **Wrong**: Study hand-picked "winners" that worked
- **Right**: Test every stock that met criteria, including failures

Selective examples create survivorship bias and dramatically overestimate strategy quality.

### Separate Idea Generation from Validation
- Intuition: Useful for generating hypotheses
- Validation: Must be purely data-driven

Never let attachment to an idea influence interpretation of test results.

## Common Failure Patterns

Recognise these early to save time:

1. **Parameter sensitivity**: Only works with exact values — classic curve-fitting
2. **Regime-specific**: Great in some years, terrible in others — no robustness
3. **Slippage sensitivity**: Unprofitable with realistic costs — no real edge
4. **Small sample**: Too few trades for statistical confidence
5. **Look-ahead bias**: "Too good to be true" results — audit for data peeking
6. **Over-optimisation**: Many parameters, catastrophic out-of-sample performance

## Evaluation Framework

When presenting a full backtest evaluation, score across 5 dimensions:

| Dimension | Key Questions |
|-----------|--------------|
| **Sample Size** | Total trades ≥ 100? Adequate per year? Statistical significance? |
| **Expectancy** | Positive net expectancy after full costs? Win rate vs. payoff ratio sensible? |
| **Risk Management** | Max drawdown within tolerance? Worst losing streak survivable? Portfolio heat controlled? |
| **Robustness** | Parameters tested in ranges? Works across multiple years/regimes? Walk-forward positive? |
| **Execution Realism** | Slippage modelled? Liquidity constraints considered? Order types realistic? |

**Scoring**: Score each dimension 0–20 for a total out of 100. Scores below 60 → Abandon. 60–79 → Refine. 80+ → Deploy at appropriate size.

## Output Format

Present the evaluation as:

```markdown
# Backtest Evaluation: [Strategy Name]
**Date**: [YYYY-MM-DD]

## Parameters Tested
[Entry rule, exit rule, stop, target, universe, period]

## Results Summary
| Metric | Value |
|--------|-------|
| Total Trades | XXX |
| Win Rate | XX% |
| Avg Win | +X.X% |
| Avg Loss | -X.X% |
| Expectancy | +$XX per trade |
| Max Drawdown | -XX% |
| Years Tested | X |
| Parameters | X |

## Dimension Scores
| Dimension | Score | Notes |
|-----------|-------|-------|
| Sample Size | XX/20 | ... |
| Expectancy | XX/20 | ... |
| Risk Management | XX/20 | ... |
| Robustness | XX/20 | ... |
| Execution Realism | XX/20 | ... |
| **Total** | **XX/100** | |

## Red Flags
[List any concerns found during testing]

## Verdict
**[DEPLOY / REFINE / ABANDON]**

[Rationale paragraph]
```

## Critical Reminders

- **Statistical significance**: Small edges require large sample sizes. A 5% edge per trade needs 100+ trades to distinguish from luck.
- **Red flag**: If backtest results look "too good" (>80% win rate, minimal drawdowns, perfect timing) — audit for look-ahead bias or data issues.
- **Context-free requirement**: If the strategy requires "perfect context" to work, it is not robust enough for systematic trading.
- **This skill is for systematic strategies** — all rules codified in advance, no discretion, every historical example included.

**Thesis Field Rule**: Always populate the `thesis` field in the JSON output with the complete backtest evaluation. This is an **advanced skill** — thesis upserting is mandatory. ⚠️ Extended thinking is discarded — copy the complete evaluation into the `thesis` field; it is the ONLY output that reaches the Thesis panel.
