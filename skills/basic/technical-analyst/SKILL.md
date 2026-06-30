---
name: technical-analyst
description: Analyze weekly price charts for stocks, indices, cryptocurrencies, or forex. Use when the user provides chart images and requests technical analysis, trend identification, support/resistance levels, moving average analysis, chart pattern recognition, scenario planning, or probability-weighted price targets. Pure chart-only analysis — no fundamentals or news.
---

# Technical Analyst

## Overview

Comprehensive technical analysis of weekly price charts. Analyzes chart images to identify trends, support/resistance levels, moving average relationships, volume patterns, and develop probabilistic scenarios for future price movement. All analysis is conducted exclusively using chart data — no influence from news, fundamentals, or market sentiment.

## Core Principles

1. **Pure Chart Analysis**: Base all conclusions exclusively on technical data visible in the chart
2. **Systematic Approach**: Follow a structured methodology for every chart
3. **Objective Assessment**: Avoid subjective bias; focus on observable patterns and data
4. **Probabilistic Scenarios**: Express future possibilities as probability-weighted scenarios
5. **Sequential Processing**: Analyze each chart individually and document findings immediately

## When to Use

- User provides one or more weekly chart images
- User asks about trend, support/resistance, moving averages, volume, or chart patterns
- User wants probabilistic price scenarios — "what's the bull/bear/base case?"
- User wants purely technical analysis without fundamental influence

## Workflow

### Step 1: Receive Charts

1. Confirm receipt of all chart images
2. Identify the number of charts to analyze
3. Note any specific focus areas (e.g., "will it break resistance?")
4. Confirm analysis will be purely technical

### Step 2: Analyze Each Chart Systematically

For each chart, conduct analysis in this sequence:

#### 2.1 Trend Analysis
- Identify trend direction (uptrend, downtrend, sideways)
- Assess trend strength (strong, moderate, weak)
- Note trend duration and potential exhaustion signals
- Examine higher highs/lows or lower highs/lows pattern

#### 2.2 Support and Resistance
- Mark significant horizontal support levels
- Mark significant horizontal resistance levels
- Identify trendline support/resistance
- Note any support–resistance role reversals
- Assess confluence zones where multiple levels align

#### 2.3 Moving Average Analysis
- Determine price position relative to 20-week, 50-week, and 200-week MAs
- Assess MA alignment (bullish, bearish, or neutral configuration)
- Note MA slope (rising, falling, flat)
- Identify recent or pending MA crossovers
- Observe MAs acting as dynamic support or resistance

#### 2.4 Volume Analysis
- Assess overall volume trend (increasing, decreasing, stable)
- Identify volume spikes and their context (at S/R levels, on breakouts)
- Check for volume confirmation or divergence with price
- Note any volume climax or exhaustion patterns

#### 2.5 Chart Patterns and Price Action
- Identify reversal patterns (hammers, shooting stars, engulfing, etc.)
- Identify continuation patterns (flags, triangles, wedges, etc.)
- Note significant candlestick formations
- Observe recent breakouts or breakdowns with volume confirmation

#### 2.6 Synthesise Observations
- Integrate all technical elements into a coherent current assessment
- Identify the most significant factors influencing the chart
- Note any conflicting signals or ambiguity
- Establish key levels that will determine future direction

### Step 3: Develop Probabilistic Scenarios

Create 2–4 distinct scenarios for future price movement. Each scenario must include:

1. **Scenario Name**: Clear, descriptive title (e.g., "Bull Case: Breakout Above Resistance")
2. **Probability Estimate**: Percentage likelihood — must sum to 100% across all scenarios
3. **Description**: How this scenario would unfold
4. **Supporting Factors**: Technical evidence (minimum 2–3 factors)
5. **Target Levels**: Expected price levels if scenario plays out
6. **Invalidation Level**: Specific price level that would negate this scenario

**Typical framework:**
- **Base Case (40–60%)**: Most likely outcome based on current structure
- **Bull Case (20–40%)**: Requires upside breakout
- **Bear Case (20–40%)**: Requires downside breakdown
- **Alternative Case (5–15%)**: Lower probability but technically plausible

Adjust probabilities based on strength of supporting technical factors. Never assign 0% to any technically plausible scenario.

### Step 4: Generate the Analysis Report

Present the analysis in this structure:

```markdown
# Technical Analysis: [SYMBOL/INSTRUMENT]
**Date**: [YYYY-MM-DD]
**Timeframe**: Weekly

---

## Chart Overview
[Brief description of chart characteristics and time range covered]

## 1. Trend Analysis
[Direction, strength, duration, key trend features]

## 2. Support and Resistance Levels
| Level | Type | Significance |
|-------|------|-------------|
| $XXX | Strong Support | Multiple tests, high volume |
| $XXX | Key Resistance | Prior high, breakout target |

## 3. Moving Average Analysis
- **20-week MA**: [price / slope / price relationship]
- **50-week MA**: [price / slope / price relationship]
- **200-week MA**: [price / slope / price relationship]
- **MA Configuration**: [Bullish / Bearish / Mixed — explain]

## 4. Volume Analysis
[Volume trend, notable spikes, divergences, confirmation/non-confirmation]

## 5. Chart Patterns and Price Action
[Patterns identified, where in pattern, implications]

## 6. Current Market Assessment
[Overall technical picture, most significant factors, conflicting signals if any]

## 7. Scenario Analysis

### [Scenario 1 Name] — XX% Probability
**Description**: ...
**Supporting factors**: ...
**Target levels**: $XXX–$XXX
**Invalidation**: Price below/above $XXX

### [Scenario 2 Name] — XX% Probability
[Same structure]

## 8. Summary
[One-paragraph synthesis: overall bias, key level to watch, most likely near-term outcome]

---
*Disclaimer: This analysis is based solely on price chart data. It is not financial advice. Trade at your own risk.*
```

## Quality Standards

### Objectivity Requirements
- Base all analysis strictly on observable chart data
- Do NOT incorporate external information (news, earnings, macro)
- Express uncertainty clearly when signals are ambiguous
- Present both bullish and bearish possibilities — no confirmation bias
- Use precise technical language, not subjective phrases like "I think" or "looks good"

### Completeness Requirements
- Address all sections of the report structure
- Provide specific price levels for support, resistance, and targets
- Justify probability estimates with technical factors
- Include invalidation levels for each scenario
- Note limitations when chart quality limits confidence

## Key Technical Reference

**Trend qualification:**
- Uptrend: Series of higher highs AND higher lows
- Downtrend: Series of lower highs AND lower lows
- Sideways: No consistent directional progress

**MA alignment (bullish):** Price > 20w > 50w > 200w, all rising
**MA alignment (bearish):** Price < 20w < 50w < 200w, all falling

**Volume confirmation:** Rallies on above-average volume, pullbacks on below-average volume = healthy uptrend

**Breakdown flags:** Rally on falling volume, support test on rising volume = distribution
