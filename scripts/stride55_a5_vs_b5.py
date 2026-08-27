#!/usr/bin/env python3
"""
55-map portfolio: paired A-versus-B at the N = 5 carried points.

PI question (2026-08-27, interactive): Run A is cheaper, Run B looks
better — is B *statistically* better at the deployment-recommendation
rung? The ladder tested N = 5 versus N = 10 within each run and the
sweep tested A versus B at N = 10; this fills the one missing
decision-relevant pair: A N = 5 carried (0.15, k4 of 5, est ~$60)
versus B N = 5 carried (0.15, k5 of 5, est ~$97).

Same instrument as the committed comparisons: per-map paired sign-swap
permutation over the 55 sheets, 10,000 draws, seed 42, corrected-F1 at
50 m against the fixed extended GT.

REPLICATION GATE: each side's per-map counts must total to the
ladder's committed carried F1 (`results/stride55-2026-08-27/
ladder.json`, A 0.832223 / B 0.843775) to 1e-6, or nothing is written.

Usage::

    python scripts/stride55_a5_vs_b5.py

Zero API. Run on sapphire.

Created: 2026-08-27 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.compute_corrected_f1_multi_buffer import (  # noqa: E402
    DEFAULT_CRS,
    build_extended_gt,
    build_phantom_gdf,
)
from scripts.stride55_ladder import (  # noqa: E402
    CARRIED_N5,
    INHERIT_TOL_M,
    cluster_first_n,
    load_deduped_passes,
)
from scripts.stride55_score import build_map_constrained_index  # noqa: E402
from scripts.stride55_sweep_oracle import (  # noqa: E402
    BOUNDS,
    BUFFER_R,
    CANONICAL_REVIEW,
    OUT_BASE,
    RUNS,
    STUDENT_GT,
    f1_from_map_counts,
    load_candidates,
    paired_permutation,
    per_map_counts,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    student = gpd.read_file(STUDENT_GT).to_crs(DEFAULT_CRS)
    bounds = gpd.read_file(BOUNDS).to_crs(DEFAULT_CRS)
    empty_y = pd.DataFrame(columns=[
        "candidate_id", "human_label", "buffer_metres", "x", "y", "map_name"])
    review_t = pd.read_csv(CANONICAL_REVIEW)
    phantoms = build_phantom_gdf(empty_y, review_t, BUFFER_R)
    ext_gt = build_extended_gt(student, phantoms)
    index = build_map_constrained_index()

    ladder = json.loads((OUT_BASE / "ladder.json").read_text())
    counts: dict[str, dict] = {}
    for cell, spec in RUNS.items():
        passes = load_deduped_passes(cell)
        k10 = load_candidates(cell, spec, bounds)
        tree = cKDTree(np.c_[k10.geometry.x, k10.geometry.y])
        probs10 = k10["mound_probability"].to_numpy()
        gdf = cluster_first_n(passes, 5, index)
        d, idx = tree.query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
        gdf["mound_probability"] = probs10[idx]
        gdf = gdf[d <= INHERIT_TOL_M].copy()
        ct, ck = CARRIED_N5[cell]
        sub = gdf[(gdf["mound_probability"] >= ct)
                  & (gdf["vote_count"] >= ck)]
        counts[cell] = per_map_counts(sub, ext_gt, bounds)
        f1 = f1_from_map_counts(counts[cell])
        committed = ladder["runs"][cell]["N"]["5"]["carried"]["corrected_f1"]
        if abs(f1 - committed) > 1e-6:
            raise RuntimeError(
                f"{cell}: replication gate FAILED — per-map total "
                f"{f1:.6f} vs committed carried {committed:.6f}")
        logger.info("%s: replication gate OK (N=5 carried %.6f)", cell, f1)

    a, b = "g384_ov128_55map", "g384_ov192_55map"
    result = paired_permutation(counts[a], counts[b])
    result["convention"] = (
        "delta = A(N5 carried, 0.15/k4) - B(N5 carried, 0.15/k5), "
        "corrected-F1@50m")
    logger.info("A(N5c) - B(N5c): dF1=%+.4f p=%.4f",
                result["delta_f1"], result["p_two_sided"])

    out = OUT_BASE / "a5_vs_b5.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    logger.info("A5-VS-B5 COMPLETE -> %s", out.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
