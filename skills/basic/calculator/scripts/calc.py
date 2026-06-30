#!/usr/bin/env python3
"""Simple calculator CLI.

Usage:
  python calc.py "2 + 2"
  python calc.py "(100 - 35) * 1.08"
"""

from __future__ import annotations

import math
import sys


_ALLOWED_NAMES = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "pow": pow,
    "sum": sum,
    "math": math,
}


def safe_eval(expr: str) -> float:
    if not expr or not expr.strip():
        raise ValueError("Empty expression")
    code = compile(expr, "<calc>", "eval")
    for name in code.co_names:
        if name not in _ALLOWED_NAMES:
            raise ValueError(f"Disallowed name: {name}")
    return eval(code, {"__builtins__": {}}, _ALLOWED_NAMES)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: calc.py <expression>")
        return 2
    expr = " ".join(argv[1:])
    try:
        result = safe_eval(expr)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
