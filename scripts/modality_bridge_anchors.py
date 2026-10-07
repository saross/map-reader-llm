#!/usr/bin/env python3
"""
Run B's anchor gate: reproduce the six original cells before any bridge number.

Why this exists
---------------
Run B (``planning/modality-bridge-2026-10-07.md`` § 9) scores each bridge
cell with the scripts that scored the originals — ``image_b_analysis.py``
(union joined to its verifier probabilities, the full (prob_t × k) sweep at
20 m, the best point) and ``gemini37_image_gap_test.py`` (per-tile counts
and the round-robin tile-swap permutation). A bridge-against-original
comparison is only a date-and-mode comparison if that path still scores the
ORIGINAL data as it did when the original cells were registered. This gate
re-runs the path on the six original cells, from their committed unions and
probabilities, and refuses unless every one reproduces:

========================  =====  ==============  =========================
Cell                      K      Best point      F1 at 20 m (registered)
========================  =====  ==============  =========================
Gemini 3 text             10     (0.15, k10)     0.8961
Gemini 3 image            10     (0.15, k9)      0.8412
3.7 text, G3 verifier     5      (0.10, k5)      0.9139
3.7 text, 3.7 verifier    5      (0.80, k5)      0.9265
3.7 image, G3 verifier    5      (0.10, k5)      0.9254
3.7 image, 3.7 verifier   5      (0.90, k5)      0.9308
========================  =====  ==============  =========================

Each cell must reproduce its F1 to ``1e-3`` (the card's tolerance) through
BOTH instruments — the sweep's scorer and the per-tile micro-F1 the gap
test permutes — and its best point exactly. The three original gaps
(text − image: +0.0549 within Gemini 3; −0.0115 under the Gemini 3
verifier and −0.0043 all-3.7 within 3.7) are re-derived through the gap
test's permutation as a further check of that instrument.

Usage::

    python scripts/modality_bridge_anchors.py [--json-out PATH]

``image_b_analysis.py --six-cell-gate`` and ``gemini37_image_gap_test.py
--six-cell-gate`` call :func:`run_six_cell_gate` before they write anything.

Zero API. Run on sapphire (six sweeps and three 10,000-permutation tests).

Created: 2026-10-07
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

#: The card's tolerance on every reproduced F1.
TOLERANCE = 1e-3


class AnchorGateError(RuntimeError):
    """An original cell or gap did not reproduce; no bridge number may be written."""


@dataclass(frozen=True)
class AnchorCell:
    """One original cell: where its union and probabilities live, what it scored."""

    label: str
    outputs_root: str
    cell: str
    union_name: str
    verify_dir: str
    k: int
    f1: float
    prob_t: float
    min_votes: int


#: The six original cells (card § 2.2, operating points and F1 at 20 m).
ORIGINAL_CELLS: tuple[AnchorCell, ...] = (
    AnchorCell("g3-text", "outputs/grid-2026-08-18", "g384_ov192",
               "union_k10.geojson", "verify", 10, 0.8961, 0.15, 10),
    AnchorCell("g3-image", "outputs/image-b-gs-2026-08-28", "g384_ov192_image",
               "union_k10.geojson", "verify", 10, 0.8412, 0.15, 9),
    AnchorCell("g37-text-g3v", "outputs/gemini37-screen-2026-08-28", "g384_ov192_g37",
               "union_k5.geojson", "verify", 5, 0.9139, 0.10, 5),
    AnchorCell("g37-text-g37v", "outputs/gemini37-screen-2026-08-28", "g384_ov192_g37",
               "union_k5.geojson", "verify_swap37", 5, 0.9265, 0.80, 5),
    AnchorCell("g37-image-g3v", "outputs/gemini37-image-gs-2026-09-01",
               "g384_ov192_g37img", "union_k5.geojson", "verify_arm1", 5, 0.9254,
               0.10, 5),
    AnchorCell("g37-image-g37v", "outputs/gemini37-image-gs-2026-09-01",
               "g384_ov192_g37img", "union_k5.geojson", "verify_arm2", 5, 0.9308,
               0.90, 5),
)

#: The three original gaps, text − image at 20 m: (text cell, image cell,
#: registered difference). Sources: results/image-b-gs-2026-08-28/
#: analysis.json (head_to_head_20m) and results/gemini37-image-gs-2026-09-01/
#: gap_test.json.
ORIGINAL_GAPS: tuple[tuple[str, str, float], ...] = (
    ("g3-text", "g3-image", 0.0549),
    ("g37-text-g3v", "g37-image-g3v", -0.0115),
    ("g37-text-g37v", "g37-image-g37v", -0.0043),
)


def score_cell(vroot: Path, union_name: str, verify_dir: str, k: int,
               label: str) -> dict[str, Any]:
    """Score one cell through ``image_b_analysis``'s own path.

    Joins the union to its probabilities (join-gated), re-derives carrier
    tiles (reassignment-gated), sweeps every (prob_t, k) point at 20 m and
    takes the best F1, as ``image_b_analysis.main`` does; then counts the
    best set per tile, as ``gemini37_image_gap_test`` does.

    Args:
        vroot: ``<outputs root>/verifier/<cell>``.
        union_name: Union filename under ``vroot``.
        verify_dir: Verify-stage directory under ``vroot``.
        k: Pass count (the sweep's vote range is 1..k).
        label: Name for error messages.

    Returns:
        ``best`` (the sweep's best row), ``best_set`` (the verified set),
        ``counts`` (per-tile TP/FP/FN arrays) and ``micro_f1``.
    """
    import geopandas as gpd

    from scripts import image_b_analysis as iba
    from scripts.grid_analysis import CRS
    from scripts.grid_verifier_analysis import per_tile_counts, verified_subset
    from scripts.n1_baseline_leaderboard_tiering import micro_f1
    from scripts.stride_verifier_analysis import (
        COMMON_BOUNDS,
        GROUND_TRUTH,
        reassign_gate,
    )

    bounds = gpd.read_file(COMMON_BOUNDS)
    gdf_ref = gpd.read_file(GROUND_TRUTH).to_crs(CRS)
    union = iba.load_image_union(vroot, union_name, verify_dir)
    union = reassign_gate(union, bounds, label)
    rows = iba.sweep(union, gdf_ref, bounds, range(1, k + 1))
    best = max(rows, key=lambda r: r["f1"])
    best_set = verified_subset(union, best["prob_t"], best["min_votes"])
    counts = per_tile_counts(best_set, bounds, gdf_ref)
    return {
        "best": best,
        "rows": rows,
        "union": union,
        "best_set": best_set,
        "counts": counts,
        "micro_f1": float(micro_f1(counts["tp"].sum(), counts["fp"].sum(),
                                   counts["fn"].sum())),
    }


def run_six_cell_gate(tolerance: float = TOLERANCE,
                      cells: tuple[AnchorCell, ...] = ORIGINAL_CELLS,
                      gaps: tuple[tuple[str, str, float], ...] = ORIGINAL_GAPS,
                      ) -> dict[str, Any]:
    """Reproduce the original cells and gaps; raise unless every one holds.

    Args:
        tolerance: Largest permitted |reproduced − registered| on an F1 or gap.
        cells: The cells to reproduce (default: the six originals).
        gaps: Text − image pairs to re-derive (labels from ``cells``).

    Returns:
        The gate record: per cell the reproduced sweep F1, per-tile micro-F1,
        best point, precision, recall and MCC; per gap the reproduced
        difference and p; ``passed``.

    Raises:
        AnchorGateError: Listing every cell or gap that failed.
    """
    from scripts.image_b_analysis import N_PERMS, SEED
    from scripts.n1_baseline_leaderboard_tiering import permutation_test_float

    record: dict[str, Any] = {"tolerance": tolerance, "cells": {}, "gaps": {}}
    failures: list[str] = []
    scored: dict[str, dict[str, Any]] = {}
    for c in cells:
        vroot = PROJECT_ROOT / c.outputs_root / "verifier" / c.cell
        s = score_cell(vroot, c.union_name, c.verify_dir, c.k, c.label)
        scored[c.label] = s
        b = s["best"]
        point_ok = (abs(b["prob_t"] - c.prob_t) < 1e-9 and b["min_votes"] == c.min_votes)
        f1_ok = abs(b["f1"] - c.f1) <= tolerance
        micro_ok = abs(s["micro_f1"] - c.f1) <= tolerance
        entry = {
            **asdict(c),
            "reproduced_f1": b["f1"], "reproduced_micro_f1": s["micro_f1"],
            "reproduced_point": [b["prob_t"], b["min_votes"]],
            "precision": b["precision"], "recall": b["recall"], "mcc": b["mcc"],
            "n_detections": b["n_detections"], "union_n": int(len(s["union"])),
            "f1_ok": f1_ok, "micro_f1_ok": micro_ok, "point_ok": point_ok,
        }
        record["cells"][c.label] = entry
        if not (f1_ok and micro_ok and point_ok):
            failures.append(
                f"{c.label}: F1 {b['f1']:.4f} / micro {s['micro_f1']:.4f} at "
                f"({b['prob_t']}, k{b['min_votes']}) vs registered {c.f1} at "
                f"({c.prob_t}, k{c.min_votes})")
        logger.info("anchor %-15s F1 %.4f (registered %.4f) micro %.4f point (%.2f, k%d) %s",
                    c.label, b["f1"], c.f1, s["micro_f1"], b["prob_t"], b["min_votes"],
                    "OK" if f1_ok and micro_ok and point_ok else "FAILED")
    for text, image, registered in gaps:
        if text not in scored or image not in scored:
            continue
        t, i = scored[text]["counts"], scored[image]["counts"]
        res = permutation_test_float(t["tp"], t["fp"], t["fn"], i["tp"], i["fp"], i["fn"],
                                     n_permutations=N_PERMS, seed=SEED)
        ok = abs(res["observed_diff"] - registered) <= tolerance
        record["gaps"][f"{text} - {image}"] = {
            "registered": registered, "reproduced": res["observed_diff"],
            "p_value": res["p_value"], "ok": ok}
        if not ok:
            failures.append(f"gap {text} - {image}: {res['observed_diff']:+.4f} vs "
                            f"registered {registered:+.4f}")
        logger.info("anchor gap %s - %s: %+.4f (registered %+.4f) p=%.4f %s", text, image,
                    res["observed_diff"], registered, res["p_value"],
                    "OK" if ok else "FAILED")
    record["passed"] = not failures
    record["failures"] = failures
    if failures:
        raise AnchorGateError("six-cell anchor gate FAILED — no bridge number may be "
                              "written: " + "; ".join(failures))
    return record


def main(argv: list[str] | None = None) -> int:
    """Run the gate and optionally write its record.

    Args:
        argv: Command-line arguments (default ``sys.argv[1:]``).

    Returns:
        0 when every cell and gap reproduced, 1 otherwise.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--tolerance", type=float, default=TOLERANCE)
    args = ap.parse_args(argv)
    try:
        record = run_six_cell_gate(args.tolerance)
        status = 0
    except AnchorGateError as exc:
        logger.error("%s", exc)
        record = {"passed": False, "error": str(exc)}
        status = 1
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(record, indent=1, default=float) + "\n")
    return status


if __name__ == "__main__":
    sys.exit(main())
