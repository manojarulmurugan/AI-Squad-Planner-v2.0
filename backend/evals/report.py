"""Render an evaluation scorecard from recorded results or the baseline."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

_ROOT = Path(__file__).resolve().parent


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = round((len(ordered) - 1) * percentile)
    return ordered[index]


def render(data: dict[str, Any]) -> str:
    lines = [
        "SquadPlanner evaluation scorecard",
        f"Tier: {data.get('tier', 'offline').upper()}",
    ]
    if data.get("tier", "offline") == "offline":
        lines.append("WARNING: frozen LLM output; these numbers do NOT measure itinerary quality.")
    scores: defaultdict[str, list[bool]] = defaultdict(list)
    unscorable: defaultdict[str, int] = defaultdict(int)
    costs: list[float] = []
    node_latencies: defaultdict[str, list[float]] = defaultdict(list)
    for case in data.get("cases", []):
        for group in ("deterministic", "trajectory"):
            for name, result in case.get(group, {}).items():
                score_name = f"{group}.{name}"
                if result.get("scorable", True):
                    scores[score_name].append(bool(result.get("passed")))
                else:
                    unscorable[score_name] += 1
        telemetry = case.get("telemetry", {})
        costs.append(float(telemetry.get("totals", {}).get("cost_usd", 0) or 0))
        for node, values in telemetry.get("nodes", {}).items():
            if "duration_ms" in values:
                node_latencies[node].append(float(values["duration_ms"]))
    for name, values in sorted(scores.items()):
        suffix = f", {unscorable[name]} unscorable" if unscorable[name] else ""
        lines.append(
            f"{name}: {sum(values)}/{len(values)} "
            f"({100 * sum(values) / max(len(values), 1):.1f}%){suffix}"
        )
    for name, count in sorted(unscorable.items()):
        if name not in scores:
            lines.append(f"{name}: unscorable ({count} cases)")
    lines.append(f"Cost per trip: ${sum(costs) / max(len(costs), 1):.6f}")
    for node, values in sorted(node_latencies.items()):
        lines.append(
            f"{node} latency: p50={median(values):.1f}ms p95={_percentile(values, 0.95):.1f}ms"
        )
    misses = data.get("replay_misses") or []
    if misses:
        lines.append(
            "Live run needed: YES — replay keys missed for "
            + ", ".join(item["case_id"] for item in misses)
        )
    else:
        lines.append("Live run needed: no prompt replay misses recorded.")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", action="store_true")
    args = parser.parse_args()
    path = _ROOT / ("baseline.json" if args.baseline else "results/offline.json")
    if not path.is_file():
        print(f"No {'baseline' if args.baseline else 'offline results'} yet: {path}")
        return
    print(render(json.loads(path.read_text(encoding="utf-8"))))


if __name__ == "__main__":
    main()
