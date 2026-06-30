#!/usr/bin/env python3
"""Render a markdown table from a JSON array of objects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def render_table(rows: list[dict[str, Any]], title: str | None = None) -> str:
    if not rows:
        return ""
    headers = []
    for row in rows:
        for key in row.keys():
            if key not in headers:
                headers.append(key)

    def fmt(value: Any) -> str:
        if value is None:
            return ""
        return str(value)

    lines: list[str] = []
    if title:
        lines.append(f"### {title}")
        lines.append("")

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(fmt(row.get(h, "")) for h in headers) + " |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render markdown table from JSON array.")
    parser.add_argument("--input", required=True, help="Path to JSON input file")
    parser.add_argument("--title", default="", help="Optional table title")
    parser.add_argument("--output", default="", help="Optional output path (writes to stdout if omitted)")
    args = parser.parse_args()

    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise SystemExit("Input JSON must be an array of objects.")

    rows = [r for r in raw if isinstance(r, dict)]
    md = render_table(rows, title=args.title or None)
    if not md:
        raise SystemExit("No rows to render.")

    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
