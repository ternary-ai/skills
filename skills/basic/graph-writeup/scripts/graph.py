#!/usr/bin/env python3
"""Generate a simple SVG line chart from time series JSON.

Input format:
[
  {"time": "2026-02-20", "value": 123.4},
  {"time": "2026-02-21", "value": 125.1}
]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def _parse_points(raw: Iterable[dict]) -> list[tuple[str, float]]:
    points: list[tuple[str, float]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        time = str(item.get("time") or item.get("date") or "").strip()
        value = item.get("value")
        try:
            value_f = float(value)
        except Exception:
            continue
        if not time:
            time = str(len(points) + 1)
        points.append((time, value_f))
    return points


def _scale(values: list[float], vmin: float, vmax: float) -> list[float]:
    if vmax <= vmin:
        return [0.5 for _ in values]
    return [(v - vmin) / (vmax - vmin) for v in values]


def build_svg(points: list[tuple[str, float]], width: int = 640, height: int = 240) -> str:
    if not points:
        return ""  # caller should handle
    padding = 30
    plot_w = width - padding * 2
    plot_h = height - padding * 2

    values = [v for _, v in points]
    vmin = min(values)
    vmax = max(values)
    scaled_y = _scale(values, vmin, vmax)

    step = plot_w / max(1, len(points) - 1)
    coords = []
    for i, y in enumerate(scaled_y):
        x = padding + i * step
        y_px = padding + (1 - y) * plot_h
        coords.append((x, y_px))

    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)

    # Labels: first/last time, min/max values
    first_time = points[0][0]
    last_time = points[-1][0]

    svg = f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\">
  <rect x=\"0\" y=\"0\" width=\"{width}\" height=\"{height}\" fill=\"#0b1020\" rx=\"12\"/>
  <g stroke=\"#1f2a44\" stroke-width=\"1\">
    <line x1=\"{padding}\" y1=\"{padding}\" x2=\"{padding}\" y2=\"{height - padding}\"/>
    <line x1=\"{padding}\" y1=\"{height - padding}\" x2=\"{width - padding}\" y2=\"{height - padding}\"/>
  </g>
  <polyline fill=\"none\" stroke=\"#38bdf8\" stroke-width=\"2\" points=\"{line}\"/>
  <g fill=\"#93c5fd\" font-family=\"JetBrains Mono, ui-monospace, monospace\" font-size=\"11\">
    <text x=\"{padding}\" y=\"{padding - 8}\">max {vmax:.2f}</text>
    <text x=\"{padding}\" y=\"{height - padding + 18}\">min {vmin:.2f}</text>
    <text x=\"{padding}\" y=\"{height - 6}\">{first_time}</text>
    <text x=\"{width - padding}\" y=\"{height - 6}\" text-anchor=\"end\">{last_time}</text>
  </g>
</svg>"""
    return svg


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SVG line chart from JSON series.")
    parser.add_argument("--input", required=True, help="Path to JSON input file")
    parser.add_argument("--output", required=True, help="Path to output SVG file")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    raw = json.loads(in_path.read_text(encoding="utf-8"))
    points = _parse_points(raw)
    if not points:
        raise SystemExit("No valid points in input JSON.")

    svg = build_svg(points)
    if not svg:
        raise SystemExit("Failed to build SVG.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
