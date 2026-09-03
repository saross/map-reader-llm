"""Census of the AB+ tail run from the manifest and verdict JSONs (read-only).

Promoted 2026-09-03 from the S147 scratch driver. Prints manifest status
counts, the verdict distribution, per-point verdict tallies, edit counts,
and summary word counts. Nothing is written.

Usage (from the repo root)::

    python3 scripts/ab_plus/tail/tail_census.py
"""

from __future__ import annotations

import json
import os
import statistics
from collections import Counter

REPO = "/home/shawn/Code/map-reader-llm"
MANIFEST = f"{REPO}/outputs/ab-plus/manifests/tail-2026-09-02.json"
WORK = f"{REPO}/outputs/ab-plus/_work"


def main() -> None:
    """Print the census."""
    rows = json.load(open(MANIFEST))["sources"]
    print("status:", dict(Counter(r["status"].split(":")[0] for r in rows)))
    overall: Counter = Counter()
    per_point: Counter = Counter()
    n_edits: list[int] = []
    unsupported: list[tuple[str, object, str]] = []
    words: list[int] = []
    n_kp: Counter = Counter()
    hooks = 0
    for r in rows:
        key = r["citekey"]
        verdict_path = f"{WORK}/{key}.verdict.json"
        if os.path.exists(verdict_path):
            verdict = json.load(open(verdict_path))
            overall[verdict.get("overall")] += 1
            for point in verdict.get("per_point", []):
                per_point[point.get("verdict")] += 1
                if point.get("verdict") == "UNSUPPORTED":
                    unsupported.append((key, point.get("index"), (point.get("note") or "")[:120]))
            n_edits.append(len(verdict.get("edits", [])))
        entry_path = f"{WORK}/{key}.entry.json"
        if os.path.exists(entry_path):
            entry = json.load(open(entry_path))
            words.append(len(entry["summary"].split()))
            n_kp[len(entry["key_points"])] += 1
            hooks += bool(entry.get("framing_hook"))
    print("overall:", dict(overall))
    print("per_point:", dict(per_point))
    if n_edits:
        print(
            f"edits per verdict: n={len(n_edits)} median={statistics.median(n_edits)} "
            f"min={min(n_edits)} max={max(n_edits)} total={sum(n_edits)}"
        )
    if words:
        print(
            f"summary words: n={len(words)} median={statistics.median(words)} "
            f"min={min(words)} max={max(words)}"
        )
    print("key points per entry:", dict(sorted(n_kp.items())), "hooks:", hooks)
    print("UNSUPPORTED points:")
    for item in unsupported:
        print("  ", item)
    print("gate:", dict(Counter(r.get("gate", "?").split(" ")[0] for r in rows)))
    print("cluster:", dict(Counter(r.get("cluster", "?") for r in rows)))


if __name__ == "__main__":
    main()
