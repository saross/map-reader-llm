#!/usr/bin/env python3
"""
Check the join-aware MCB builder against the default path, under ``id``, on the board.

Part of the S166 MCC robustness job, part (b)
(``reports/s166-agent-records/mcc-join-tiering.md``). The tile-MCC MCB's
default path derives each cell's predicted-populated indicators from the F1
arm's per-tile TP + FP and the reference occupancy by intersection
(``selection_aware_intervals.build_board_tile_counts``). The geometric
sensitivity runs instead read both off each cell's gated per-tile
classification (``build_board_tile_classification``). Run under the published
``id`` join on the real board, the two must agree exactly; if they do, a
geometric MCB result differs from the published one because of the join and
not because of the builder.

Usage: python builder_id_check.py <clone_root> <analysis_id> <analyses_json> <out_json>

Author: Shawn Ross, Claude Code (S166). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


def main() -> int:
    """Compare the two builders and write the verdict as JSON."""
    clone, analysis_id, analyses, out = sys.argv[1:5]
    sys.path.insert(0, clone)
    from scripts import selection_aware_intervals as sai  # noqa: PLC0415

    specs, counts, occupancy = sai.build_board_tile_counts(
        analysis_id, analyses_path=Path(analyses))
    j_specs, j_counts, j_occupancy, j_has_det = sai.build_board_tile_classification(
        analysis_id, "id", analyses_path=Path(analyses))
    legacy_has_det = (counts[:, :, 0] + counts[:, :, 1]) > 0
    result = {
        "analysis_id": analysis_id,
        "n_cells": len(specs),
        "n_tiles": int(counts.shape[1]),
        "specs_equal": j_specs == specs,
        "counts_equal": bool(np.array_equal(j_counts, counts)),
        "occupancy_equal": bool(np.array_equal(j_occupancy, occupancy)),
        "has_det_equal": bool(np.array_equal(j_has_det, legacy_has_det)),
        "n_has_det_cells_differing": int(
            (j_has_det != legacy_has_det).any(axis=1).sum()),
        "n_reference_tiles": int(occupancy.sum()),
    }
    result["passed"] = all(result[k] for k in (
        "specs_equal", "counts_equal", "occupancy_equal", "has_det_equal"))
    Path(out).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
