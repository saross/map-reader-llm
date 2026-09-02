#!/usr/bin/env python3
"""
The within-3.7 modality gap: text vs image, both verifier arms.

The image-GS card's I2 test (`planning/gemini37-image-gs-2026-08-30.md`)
is a difference-in-differences: (text − image) WITHIN Gemini 3.7
against the committed (text − image) within Gemini 3 (+0.0549 @20 m,
p = 0.001). `image_b_analysis.py`'s built-in head-to-head pairs the
image cell against the GEMINI-3 text anchor (its original campaign
design), so this script runs the correct within-family pairs:

- carried-verifier pair: 3.7-text screen best vs 3.7-image arm 1
- all-3.7 pair: 3.7-text swap best vs 3.7-image arm 2

Instrument: per-tile counts at 20 m + round-robin tile-swap micro-F1
permutation (10,000, seed 42) — identical to the screen's committed
head-to-heads. REPLICATION GATE per side: the per-tile micro-F1 must
match the committed verified-best value to 1e-3 (the board chain's
documented mechanism bound), or nothing is written.

The Gemini-3 gap is quoted with its own committed test; the gap
CHANGE is reported descriptively (no cross-campaign permutation is
defined).

Usage::

    python scripts/gemini37_image_gap_test.py

Zero API, seconds. Run where the verified sets live (sapphire).

Created: 2026-09-02 (Session 145)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

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

OUT = PROJECT_ROOT / "results/gemini37-image-gs-2026-09-01"

#: (pair label, text set, committed text F1@20, image set, committed
#: image F1@20). Committed values re-read from the cells' analyses.
PAIRS = [
    ("carried-verifier",
     PROJECT_ROOT / "results/gemini37-screen-2026-08-28/verified_best_20m.geojson", 0.9139,
     OUT / "arm1/verified_best_20m.geojson", 0.9254),
    ("all-3.7",
     PROJECT_ROOT / "results/gemini37-screen-2026-08-28/swap37/verified_best_20m.geojson", 0.9265,
     OUT / "arm2/verified_best_20m.geojson", 0.9308),
]

G3_GAP = {"delta_f1": 0.0549, "p": 0.001,
          "source": "results/image-b-gs-2026-08-28/analysis.json"}


def main() -> int:
    import geopandas as _g
    bounds = _g.read_file(COMMON_BOUNDS)
    gdf_ref = _g.read_file(GROUND_TRUTH).to_crs(CRS)
    payload: dict = {"buffer_m": 20, "g3_gap_committed": G3_GAP,
                     "pairs": {}}
    for label, text_path, text_f1, img_path, img_f1 in PAIRS:
        sides = {}
        for side, path, committed in (("text", text_path, text_f1),
                                      ("image", img_path, img_f1)):
            det = gpd.read_file(path).to_crs(CRS)
            counts = per_tile_counts(det, bounds, gdf_ref)
            f1 = micro_f1(counts["tp"].sum(), counts["fp"].sum(),
                          counts["fn"].sum())
            if abs(f1 - committed) > 1e-3:
                raise RuntimeError(
                    f"{label}/{side}: gate FAILED — per-tile {f1:.4f} "
                    f"vs committed {committed:.4f}")
            logger.info("%s/%s: gate OK (%.4f)", label, side, f1)
            sides[side] = counts
        res = permutation_test_float(
            sides["text"]["tp"], sides["text"]["fp"], sides["text"]["fn"],
            sides["image"]["tp"], sides["image"]["fp"], sides["image"]["fn"],
            n_permutations=N_PERMS, seed=SEED)
        res["convention"] = "delta = text - image @20m"
        payload["pairs"][label] = res
        logger.info("%s: text-image dF1=%+.4f p=%.4f (G3 committed "
                    "+0.0549 p=0.001 -> gap change %+.4f)", label,
                    res["observed_diff"], res["p_value"],
                    res["observed_diff"] - G3_GAP["delta_f1"])

    (OUT / "gap_test.json").write_text(
        json.dumps(payload, indent=2, default=float) + "\n")
    logger.info("GAP TEST COMPLETE -> %s", OUT.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
