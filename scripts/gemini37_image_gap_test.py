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

Parameterised entry point (Run B, ``planning/modality-bridge-2026-10-07-stage2.md``;
added 2026-10-07). ``--pair LABEL TEXT_DIR IMAGE_DIR`` (repeatable)
replaces the hard-coded pairs: each directory is an
``image_b_analysis.py`` output holding ``verified_best_20m.geojson`` and
``analysis.json``, whose ``image_best.f1`` is the value the replication gate
checks (``--set-name`` picks another set, e.g. ``verified_op_20m`` with
``operating_point.f1``). ``--reference-pair LABEL`` takes the gap change
against a pair computed in the same run instead of the committed Gemini 3
gap; ``--six-cell-gate`` refuses to write until the six original cells
reproduce (``scripts/modality_bridge_anchors.py``)::

    python scripts/gemini37_image_gap_test.py --six-cell-gate \\
        --pair g3 results/modality-bridge-2026-10-07/g3-text-g3v \\
                  results/modality-bridge-2026-10-07/g3-image-g3v \\
        --pair carried-verifier results/modality-bridge-2026-10-07/g37-text-g3v \\
                  results/modality-bridge-2026-10-07/g37-image-g3v \\
        --reference-pair g3 --out-dir results/modality-bridge-2026-10-07

With no new flag the behaviour is the original's.

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


#: Where an image_b_analysis.py output keeps each set's F1 (a key path into
#: its analysis.json). ``verified_ladder_n5_20m`` is the inherited K = 5 rung
#: written by ``--write-rung-sets`` (Run B § 9 item 5).
SET_F1_KEY = {"verified_best_20m": ("image_best", "f1"),
              "verified_op_20m": ("operating_point", "f1"),
              "verified_ladder_n5_20m": ("ladder", "5", "best", "f1")}


def pairs_from_dirs(specs: list[list[str]], set_name: str = "verified_best_20m",
                    ) -> list[tuple[str, Path, float, Path, float]]:
    """Build gap-test pairs from image_b_analysis.py output directories.

    Args:
        specs: ``[label, text_dir, image_dir]`` triples (repository-relative
            or absolute directories).
        set_name: Which verified set to pair (a key of :data:`SET_F1_KEY`);
            its committed F1 is read from the same directory's
            ``analysis.json``.

    Returns:
        Tuples in the shape of :data:`PAIRS`.

    Raises:
        KeyError: If ``set_name`` is unknown or ``analysis.json`` lacks it.
    """
    path = SET_F1_KEY[set_name]
    out = []
    for label, text_dir, image_dir in specs:
        sides = []
        for d in (text_dir, image_dir):
            root = PROJECT_ROOT / d
            node = json.loads((root / "analysis.json").read_text())
            for key in path:
                node = node[key]
            sides.extend([root / f"{set_name}.geojson", float(node)])
        out.append((label, sides[0], sides[1], sides[2], sides[3]))
    return out


def main(argv: list[str] | None = None) -> int:
    import argparse

    import geopandas as _g
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pair", nargs=3, action="append", default=None,
                    metavar=("LABEL", "TEXT_DIR", "IMAGE_DIR"),
                    help="A text/image pair of image_b_analysis.py outputs "
                         "(repeatable; replaces the original pairs).")
    ap.add_argument("--set-name", default="verified_best_20m",
                    choices=sorted(SET_F1_KEY),
                    help="Which verified set each --pair directory supplies.")
    ap.add_argument("--reference-pair", default=None,
                    help="Gap change against this --pair's gap (default: the "
                         "committed Gemini 3 gap, +0.0549).")
    ap.add_argument("--out-dir", default=None,
                    help="Where gap_test.json is written (default: the "
                         "original results/gemini37-image-gs-2026-09-01).")
    ap.add_argument("--six-cell-gate", action="store_true",
                    help="Refuse to write unless the six original cells reproduce.")
    args = ap.parse_args(argv)
    pairs = PAIRS if not args.pair else pairs_from_dirs(args.pair, args.set_name)
    out_dir = PROJECT_ROOT / args.out_dir if args.out_dir else OUT
    labels = [p[0] for p in pairs]
    if args.reference_pair is not None and args.reference_pair not in labels:
        ap.error(f"--reference-pair {args.reference_pair!r} is not a --pair label")
    if args.six_cell_gate:
        from scripts.modality_bridge_anchors import run_six_cell_gate
        run_six_cell_gate()
        logger.info("six-cell anchor gate PASSED")
    bounds = _g.read_file(COMMON_BOUNDS)
    gdf_ref = _g.read_file(GROUND_TRUTH).to_crs(CRS)
    payload: dict = {"buffer_m": 20, "g3_gap_committed": G3_GAP,
                     "pairs": {}}
    if args.pair:
        payload["pair_sources"] = {lab: [t, i] for lab, t, i in args.pair}
        payload["set_name"] = args.set_name
    for label, text_path, text_f1, img_path, img_f1 in pairs:
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

    if args.reference_pair is not None:
        ref = payload["pairs"][args.reference_pair]["observed_diff"]
        payload["gap_change_reference"] = args.reference_pair
        payload["gap_change"] = {
            lab: res["observed_diff"] - ref for lab, res in payload["pairs"].items()
            if lab != args.reference_pair}
        logger.info("gap change vs %s: %s", args.reference_pair,
                    {k: round(v, 4) for k, v in payload["gap_change"].items()})
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "gap_test.json").write_text(
        json.dumps(payload, indent=2, default=float) + "\n")
    logger.info("GAP TEST COMPLETE -> %s", out_dir.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
