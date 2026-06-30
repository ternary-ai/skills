---
name: calculator
description: Perform accurate numeric calculations and conversions. Use when the user asks for arithmetic, percentages, ratios, growth rates, unit conversions, or any multi-step computation where precision matters.
---

# Calculator

## Overview

Compute precise results from user inputs, using a reliable calculation method, and return a clear final value with units and rounding.

## Quick Use

1. Restate inputs and assumptions (units, rounding, time basis).
2. Build a single expression or small sequence of steps.
3. Compute with a calculator tool or the local script at `scripts/calc.py` (prefer deterministic math).
4. Return the final result with units and any requested precision.

## Tasks

### Arithmetic and percentages

Use explicit formulas. Example: "X is 12% of 350" -> 350 * 0.12.

### Ratios and growth rates

Normalize to consistent units, then compute. Example: growth rate = (new - old) / old.

### Unit conversions

Convert to base units before combining values. If a conversion factor is ambiguous, ask a clarifying question.

### Ranges and rounding

If inputs are ranges, compute min and max. Round only at the end unless the user specifies otherwise.

## Output

Use a short, direct result format.

Example:

```text
Result: 42.75 USD
```

## Script

Use `scripts/calc.py` for deterministic evaluation when the math is non-trivial or the user requests strict accuracy.
