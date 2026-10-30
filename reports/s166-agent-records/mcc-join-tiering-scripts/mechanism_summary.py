#!/usr/bin/env python3
"""
Summarise the ``id``-join mechanism diagnostic against the per-join results.

Part of the S166 MCC robustness job, part (b)
(``reports/s166-agent-records/mcc-join-tiering.md``). Reads
``id_join_mechanism.py``'s per-cell counts, the results ``summary.json`` (for
each cell's proposer track) and the committed board tiering (for F1 tiers),
and writes a small JSON of the aggregates the record quotes. Descriptive only.

Usage: python mechanism_summary.py <mechanism_json> <summary_json> <tiering_json> <out_json>

Author: Shawn Ross, Claude Code (S166). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

from scipy.stats import spearmanr


def main() -> int:
    """Aggregate the diagnostic and write the figures the record cites."""
    mech_path, summary_path, tiering_path, out = (Path(p) for p in sys.argv[1:5])
    cells = json.loads(mech_path.read_text())["cells"]
    track = json.loads(summary_path.read_text())["tracks"]
    tiering = json.loads(tiering_path.read_text())
    f1 = {r["ref"]: r["eval_f1"] for r in tiering["ranking"]}
    f1_tier = {r["ref"]: r["tier"] for r in tiering["ranking"]}

    def delta(cell: dict, join: str) -> float:
        return cell["mcc"][join] - cell["mcc"]["id"]

    inside = [c["fn_with_detection_inside"] for c in cells]
    result = {
        "n_cells": len(cells),
        "total_fn_id": sum(c["fn"] for c in cells),
        "total_fn_with_detection_inside": sum(inside),
        "share_fn_with_detection_inside": round(sum(inside) / sum(c["fn"] for c in cells), 4),
        "n_det_outside_named_tile_total": sum(c["n_det_outside_named_tile"] for c in cells),
        "spearman_fn_inside_vs_delta_mcc": {
            join: round(float(spearmanr(inside, [delta(c, join) for c in cells]).statistic), 4)
            for join in ("geometric-primary", "geometric-contains")
        },
        "spearman_fn_inside_vs_f1": round(
            float(spearmanr(inside, [f1[c["ref"]] for c in cells]).statistic), 4),
        "by_track": {},
        "by_f1_tier_band": {},
        "named_cells": {},
    }
    for name in ("image", "text"):
        sub = [c for c in cells if track[c["ref"]] == name]
        result["by_track"][name] = {
            "n": len(sub),
            "median_fn": statistics.median(c["fn"] for c in sub),
            "median_fn_with_detection_inside": statistics.median(
                c["fn_with_detection_inside"] for c in sub),
            "median_delta_mcc_primary": round(statistics.median(
                delta(c, "geometric-primary") for c in sub), 4),
        }
    for lo, hi in ((1, 3), (4, 8), (9, 14)):
        sub = [c for c in cells if lo <= f1_tier[c["ref"]] <= hi]
        result["by_f1_tier_band"][f"{lo}-{hi}"] = {
            "n": len(sub),
            "median_fn_with_detection_inside": statistics.median(
                c["fn_with_detection_inside"] for c in sub),
            "median_delta_mcc_primary": round(statistics.median(
                delta(c, "geometric-primary") for c in sub), 4),
            "median_delta_mcc_contains": round(statistics.median(
                delta(c, "geometric-contains") for c in sub), 4),
        }
    named = list(tiering["tie_set"]) + [
        "pv-diag-384::verified-adv-image-baseline-pro-vf-era2b",
        "pv-diag-384::verified-adv-text-consensus-16of30-era2b",
    ]
    for ref in named:
        cell = next(c for c in cells if c["ref"] == ref)
        result["named_cells"][ref] = {
            k: cell[k] for k in ("n_detections", "confusion_id", "fn",
                                 "fn_with_detection_inside", "mcc")
        }
    Path(out).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
