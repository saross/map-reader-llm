#!/usr/bin/env python3
"""
Gemini 3.8 Flash screen, Arm V: the verifier-seat pair tests.

Arm V of `planning/gemini38-screen-2026-09-04.md` re-verifies the Gemini
3.7 K=5 union (791 candidates, `outputs/gemini37-screen-2026-08-28/
verifier/g384_ov192_g37/`) with Gemini 3.8 Flash as the verifier, so
the two verifier models are compared on IDENTICAL candidates. This
script runs the paired tests the card's E1 expectation needs:

- ``all-3.7 vs 3.8-verifier``: the 3.7 swap best (0.9265 @20 m, the
  incumbent all-3.7 stack) against the 3.8-verifier best.
- ``carried-G3 vs 3.8-verifier``: the 3.7 screen best under the carried
  Gemini 3 verifier (0.9139 @20 m) against the 3.8-verifier best.

Instrument: per-tile counts at 20 m + round-robin tile-swap micro-F1
permutation (10,000, seed 42) — identical to the screen's committed
head-to-heads and to `gemini37_image_gap_test.py`. REPLICATION GATE per
side: the per-tile micro-F1 must match the committed verified-best value
to 1e-3 (the board chain's documented mechanism bound), or nothing is
written. The 3.8 side's committed value is read from its own
`analysis.json` (written by `image_b_analysis.py --verify-dir
verify_swap38`), so the gate checks mechanism identity between the two
scoring paths rather than a hand-typed number.

Usage::

    python scripts/gemini38_armv_pair_test.py \
        [--armv-dir results/gemini38-screen-2026-09-04/armV]

Zero API, seconds. Run where the verified sets live (sapphire).

Created: 2026-09-04 (Session 148)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.grid_analysis import CRS  # noqa: E402
from scripts.grid_verifier_analysis import per_tile_counts  # noqa: E402
from scripts.image_b_analysis import N_PERMS, SEED  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    micro_f1,
    permutation_test_float,
)
from scripts.stride_verifier_analysis import (  # noqa: E402
    COMMON_BOUNDS,
    GROUND_TRUTH,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: The two 3.7-era incumbents on the same union, with their committed
#: verified-best F1@20 (re-read from the cells' analyses, S148).
INCUMBENTS = [
    ("all-3.7",
     PROJECT_ROOT / "results/gemini37-screen-2026-08-28/swap37/verified_best_20m.geojson",
     0.9265),
    ("carried-G3",
     PROJECT_ROOT / "results/gemini37-screen-2026-08-28/verified_best_20m.geojson",
     0.9139),
]

#: Mechanism-identity bound for the replication gate (board chain).
GATE_TOL = 1e-3


def gated_counts(label: str, path: Path, committed: float, bounds, gdf_ref):
    """Per-tile counts for a verified set, gated on its committed F1@20.

    Args:
        label: Human-readable side label for logging.
        path: Verified-best GeoJSON.
        committed: The F1@20 the set's own analysis committed.
        bounds: Common-footprint evaluation bounds.
        gdf_ref: Ground-truth reference points in ``CRS``.

    Returns:
        The per-tile tp/fp/fn frame.

    Raises:
        RuntimeError: if the per-tile micro-F1 misses the committed value
            by more than ``GATE_TOL`` — nothing is written in that case.
    """
    det = gpd.read_file(path).to_crs(CRS)
    counts = per_tile_counts(det, bounds, gdf_ref)
    f1 = micro_f1(counts["tp"].sum(), counts["fp"].sum(), counts["fn"].sum())
    if abs(f1 - committed) > GATE_TOL:
        raise RuntimeError(
            f"{label}: gate FAILED — per-tile {f1:.4f} vs committed {committed:.4f}")
    logger.info("%s: gate OK (%.4f, committed %.4f)", label, f1, committed)
    return counts


def main() -> int:
    """Run both pair tests and write ``pair_test.json`` beside the Arm V analysis."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--armv-dir", default="results/gemini38-screen-2026-09-04/armV",
                    help="Arm V results dir holding analysis.json and "
                         "verified_best_20m.geojson from image_b_analysis.py.")
    args = ap.parse_args()
    armv = PROJECT_ROOT / args.armv_dir
    analysis = json.loads((armv / "analysis.json").read_text())
    best = analysis["image_best"]  # the scorer's field name; this is the 3.8-verifier best
    armv_f1 = float(best["f1"])
    logger.info("Arm V (3.8 verifier) committed best: F1@20 %.4f at (prob_t %s, k %s), "
                "P %.4f R %.4f MCC %s", armv_f1, best["prob_t"], best["min_votes"],
                best["precision"], best["recall"], best.get("mcc"))

    bounds = gpd.read_file(COMMON_BOUNDS)
    gdf_ref = gpd.read_file(GROUND_TRUTH).to_crs(CRS)
    armv_counts = gated_counts("3.8-verifier", armv / "verified_best_20m.geojson",
                               armv_f1, bounds, gdf_ref)

    payload: dict = {
        "buffer_m": 20,
        "union": "gemini37-screen K=5 union (791 candidates) — identical for all sides",
        "armv_best": best,
        "n_permutations": N_PERMS,
        "seed": SEED,
        "pairs": {},
    }
    for label, path, committed in INCUMBENTS:
        inc = gated_counts(label, path, committed, bounds, gdf_ref)
        res = permutation_test_float(
            armv_counts["tp"], armv_counts["fp"], armv_counts["fn"],
            inc["tp"], inc["fp"], inc["fn"],
            n_permutations=N_PERMS, seed=SEED)
        res["convention"] = f"delta = 3.8-verifier - {label} @20m"
        res["committed_incumbent_f1"] = committed
        payload["pairs"][label] = res
        logger.info("3.8-verifier vs %s: dF1 %+.4f p=%.4f", label,
                    res["observed_diff"], res["p_value"])

    (armv / "pair_test.json").write_text(json.dumps(payload, indent=2, default=float) + "\n")
    logger.info("PAIR TEST COMPLETE -> %s", (armv / "pair_test.json").relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
