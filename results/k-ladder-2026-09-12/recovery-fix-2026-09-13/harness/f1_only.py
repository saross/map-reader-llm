#!/usr/bin/env python3
"""
F1-only scoring for cells whose per-tile table the tile-join invariant refuses
=============================================================================

Description:
    The three Gemini 3.7 gold-standard text cells cannot be re-scored with
    ``scripts/evaluate_detections.py`` at current HEAD: the tile-join invariant
    (``lib_advanced_metrics.compute_per_tile_tp_fp_fn``) raises on their
    192 px-stride ``source_tile`` vocabulary, and because the F1 bootstrap
    resamples tiles, the refusal aborts the whole evaluation rather than only
    the tile-MCC block. Their committed evaluations predate that invariant.

    Everything the invariant does NOT touch is still computable, and that is
    exactly what the PI asked for ("F1 only"): the precision, recall and F1
    POINT estimates, from the very function ``evaluate_detections.py`` calls
    for them — ``lib_advanced_metrics.calculate_f1_internal`` — over the same
    reference, the same board frame, the same 14 buffers and the same
    EPSG:32635 evaluation CRS.

    Withheld, and named as such rather than silently omitted: every bootstrap
    confidence interval and the whole per-tile confusion / tile-MCC block.

    Both the committed ("before") and the rebuilt ("after") detection sets are
    scored by THIS script in the SAME process, so a difference is a difference
    in detections and not an artefact of the scorer having changed between
    2026-09-12 and now.

Usage::

    python f1_only.py --repo <root> --pair before=<a.geojson>,after=<b.geojson> \
        --label g37-text-k1-verified-opmax --out <report.json>

Outputs:
    A JSON report: per-buffer precision/recall/F1 for both members of each
    pair, their deltas, and an explicit withheld block.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def main() -> None:
    """Score every named GeoJSON on the recorded recipe's F1 arm."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--label", type=str, required=True)
    parser.add_argument(
        "--set",
        action="append",
        required=True,
        metavar="NAME=PATH",
        help="A named detection GeoJSON to score (repeatable)",
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo.resolve()
    sys.path.insert(0, str(repo))
    from scripts.evaluate_detections import load_geojson  # noqa: E402
    from scripts.lib_advanced_metrics import (  # noqa: E402
        DEFAULT_CRS,
        calculate_f1_internal,
    )
    from scripts.score_k_ladder_phase2_rungs import (  # noqa: E402
        BOARD_BOUNDS,
        BUFFERS,
        GROUND_TRUTH,
    )

    reference = load_geojson(repo / GROUND_TRUTH)
    bounds = load_geojson(repo / BOARD_BOUNDS)

    results: dict[str, Any] = {
        "label": args.label,
        "recipe": {
            "ground_truth": str(GROUND_TRUTH),
            "bounds": str(BOARD_BOUNDS),
            "buffers": list(BUFFERS),
            "evaluation_crs": DEFAULT_CRS,
            "metric_function": (
                "scripts/lib_advanced_metrics.py::calculate_f1_internal"
            ),
        },
        "withheld": {
            "bootstrap_ci": (
                "WITHHELD — the tile-join invariant refuses this cell's "
                "per-tile table, and the F1 bootstrap resamples tiles"
            ),
            "tile_classification": (
                "WITHHELD — tile_join_detection_shortfall under the 'id' join; "
                "the cell's 192 px-stride source_tile vocabulary is not the "
                "board frame's 336 px-stride one"
            ),
        },
        "n_reference_mounds": int(len(reference)),
        "n_frame_tiles": int(len(bounds)),
        "sets": {},
    }

    for spec in args.set:
        name, _, path = spec.partition("=")
        detections = load_geojson(Path(path))
        per_buffer = {}
        for buffer_m in BUFFERS:
            precision, recall, f1 = calculate_f1_internal(
                detections, reference, bounds, buffer_metres=buffer_m
            )
            per_buffer[str(buffer_m)] = {
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
            }
        results["sets"][name] = {
            "path": str(path),
            "n_detections": int(len(detections)),
            "per_buffer": per_buffer,
        }

    names = list(results["sets"])
    if len(names) == 2:
        before, after = names
        deltas = {}
        for buffer_m in BUFFERS:
            key = str(buffer_m)
            deltas[key] = {
                metric: round(
                    results["sets"][after]["per_buffer"][key][metric]
                    - results["sets"][before]["per_buffer"][key][metric],
                    4,
                )
                for metric in ("precision", "recall", "f1")
            }
        results["delta"] = {
            "basis": f"{after} minus {before}",
            "n_detections": (
                results["sets"][after]["n_detections"]
                - results["sets"][before]["n_detections"]
            ),
            "per_buffer": deltas,
        }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
