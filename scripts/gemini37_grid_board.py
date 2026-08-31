#!/usr/bin/env python3
"""
Gemini 3.7 campaign grid board: all-pairs significance + tiers.

PI commission (2026-08-31, interactive): once the fourth grid cell
lands, recalculate the campaign leaderboard via pairwise permutations
and report which differences are statistically significant —
specifically (a) carried → oracle within every cell, and (b) the
N=1 → N=3 → N=5 rung transitions within each arm (especially arm 2).

Membership (16 cells, canonical chain throughout):

- Incumbents: BN5-carried, BN10-carried (committed Gemini-3 sets).
- Arm 1 / arm 2 at N ∈ {1, 3, 5}, each at its carried(-analogue)
  point (committed prob_t, unanimity k = N) and its rung oracle.
- Fourth cell (G3 K=10 union + 3.7 verifier) at carried (0.98, k10)
  and at its 55-map oracle.

Instrument: per-sheet paired sign-swap permutation of corrected-F1
@ 50 m (10,000 draws, seed 42 — the campaign instrument) over all
120 pairs; Benjamini–Hochberg FDR q = 0.05 across the full pairwise
family; greedy-clique tiers on the BH-significant matrix (the board
chain's `apply_bh_correction` + `greedy_clique_tiers`, imported
verbatim). The named contrasts are read off the same matrix, so their
p-values carry the family-wide correction.

REPLICATION GATES (nothing is written unless every cell passes): each
cell's per-map F1 total must reproduce its committed value — primary
corrected-f1.csv, sweep_oracle.json, ladder.json, or
ladder_sweep_50m.csv — to 1e-6.

Usage::

    python scripts/gemini37_grid_board.py

Zero API. Run on sapphire (~16 x 55 Hungarian problems + 120 x
10,000 permutations). Requires the completed fourth-cell chain
(primary scoring + full three-cell sweep + fourth-cell ladder).

Created: 2026-08-31 (Session 145)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import csv as csvmod
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.apply_fdr_correction import apply_bh_correction  # noqa: E402
from scripts.compute_corrected_f1_multi_buffer import (  # noqa: E402
    DEFAULT_CRS,
    build_extended_gt,
    build_phantom_gdf,
)
from scripts.gemini37_arm_ladder import (  # noqa: E402
    cluster_first_n,
    load_deduped_passes,
)
from scripts.gemini37_sweep_oracle import (  # noqa: E402
    CELLS as CAMPAIGN_CELLS,
    INCUMBENTS,
    committed_f1_at_50,
    incumbent_committed_f1,
    load_candidates,
)
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    greedy_clique_tiers,
)
from scripts.stride55_ladder import INHERIT_TOL_M  # noqa: E402
from scripts.stride55_score import build_map_constrained_index  # noqa: E402
from scripts.stride55_sweep_oracle import (  # noqa: E402
    BOUNDS,
    BUFFER_R,
    CANONICAL_REVIEW,
    STUDENT_GT,
    f1_from_map_counts,
    paired_permutation,
    per_map_counts,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

RESULTS = PROJECT_ROOT / "results/gemini37-55map-2026-08-31"
OUT_DIR = RESULTS / "grid-board"
SWEEP_JSON = RESULTS / "sweeps/sweep_oracle.json"
LADDER_JSON = RESULTS / "ladder/ladder.json"
LADDER_CSV = RESULTS / "ladder/ladder_sweep_50m.csv"
BH_Q = 0.05
ARMS = ("arm1", "arm2")
RUNG_NS = (1, 3)

#: Named contrasts to read off the pairwise matrix: carried → oracle
#: within each cell, and the rung transitions within each arm at both
#: bases. Filled programmatically in main().


def rung_committed_f1(arm: str, n: int, prob_t: float, k: int) -> float:
    """Committed rung F1 from the arm ladder sweep CSV."""
    with LADDER_CSV.open() as fh:
        for row in csvmod.DictReader(fh):
            if (row["arm"] == arm and int(row["N"]) == n
                    and abs(float(row["prob_t"]) - prob_t) < 1e-9
                    and int(row["min_votes"]) == k):
                return float(row["corrected_f1"])
    raise RuntimeError(f"ladder CSV: no row for {arm} N={n} ({prob_t}, k{k})")


def main() -> int:
    import pandas as pd

    sweep = json.loads(SWEEP_JSON.read_text())
    ladder = json.loads(LADDER_JSON.read_text())
    for tag in ("arm1", "arm2", "fourth"):
        if tag not in sweep["runs"]:
            raise SystemExit(
                f"sweep_oracle.json lacks '{tag}' — run the full three-cell "
                "sweep (gemini37_sweep_oracle.py, no --cells subset) first")

    student = gpd.read_file(STUDENT_GT).to_crs(DEFAULT_CRS)
    bounds = gpd.read_file(BOUNDS).to_crs(DEFAULT_CRS)
    empty_y = pd.DataFrame(columns=[
        "candidate_id", "human_label", "buffer_metres", "x", "y", "map_name"])
    review_t = pd.read_csv(CANONICAL_REVIEW)
    phantoms = build_phantom_gdf(empty_y, review_t, BUFFER_R)
    ext_gt = build_extended_gt(student, phantoms)
    index = build_map_constrained_index()

    cells: list[dict] = []          # label, f1, counts, point, basis
    counts_of: dict[str, dict] = {}

    def add_cell(label: str, det: gpd.GeoDataFrame, committed: float,
                 point: str, basis: str) -> None:
        counts = per_map_counts(det, ext_gt, bounds)
        f1 = f1_from_map_counts(counts)
        if abs(f1 - committed) > 1e-6:
            raise RuntimeError(
                f"{label}: gate FAILED — per-map {f1:.6f} vs "
                f"committed {committed:.6f}")
        logger.info("%s: gate OK (%.6f, n=%d)", label, f1, len(det))
        counts_of[label] = counts
        cells.append({"label": label, "f1_50": f1, "point": point,
                      "basis": basis, "n_detections": int(len(det))})

    # Incumbents (committed Gemini-3 sets).
    for name, spec in INCUMBENTS.items():
        det = gpd.read_file(spec["detections"]).to_crs(DEFAULT_CRS)
        add_cell(f"{name}-carried", det, incumbent_committed_f1(spec),
                 "(0.15, unanimity)", "carried")

    # Arm N=5 cells and the fourth cell, from the full candidate sets.
    for tag in ("arm1", "arm2", "fourth"):
        spec = CAMPAIGN_CELLS[tag]
        gdf = load_candidates(tag, spec)
        pt, pk = spec["carried"]
        n_label = "N5" if tag in ARMS else "N10"
        sub = gdf[(gdf["mound_probability"] >= pt) & (gdf["vote_count"] >= pk)]
        add_cell(f"{tag}-{n_label}-carried", sub,
                 committed_f1_at_50(spec["committed"]),
                 f"({pt:.2f}, k{pk})", "carried")
        o = sweep["runs"][tag]["oracle"]
        sub = gdf[(gdf["mound_probability"] >= o["prob_t"])
                  & (gdf["vote_count"] >= o["min_votes"])]
        add_cell(f"{tag}-{n_label}-oracle", sub, o["corrected_f1"],
                 f"({o['prob_t']:.2f}, k{o['min_votes']})", "oracle")

    # Arm rung cells (N in {1, 3}) by the gated ladder derivation.
    passes = load_deduped_passes()
    k5 = load_candidates("arm1", CAMPAIGN_CELLS["arm1"])
    tree = cKDTree(np.c_[k5.geometry.x, k5.geometry.y])
    probs = {arm: load_candidates(arm, CAMPAIGN_CELLS[arm])
             ["mound_probability"].to_numpy() for arm in ARMS}
    for n in RUNG_NS:
        gdf_base = cluster_first_n(passes, n, index)
        d, idx = tree.query(np.c_[gdf_base.geometry.x, gdf_base.geometry.y],
                            k=1)
        matched = d <= INHERIT_TOL_M
        for arm in ARMS:
            gdf = gdf_base[matched].copy()
            gdf["mound_probability"] = probs[arm][idx[matched]]
            pt = CAMPAIGN_CELLS[arm]["carried"][0]
            sub = gdf[(gdf["mound_probability"] >= pt)
                      & (gdf["vote_count"] >= n)]
            add_cell(f"{arm}-N{n}-carried", sub,
                     rung_committed_f1(arm, n, pt, n),
                     f"({pt:.2f}, k{n})", "carried-analogue")
            o = ladder["arms"][arm][str(n)]["oracle"]
            sub = gdf[(gdf["mound_probability"] >= o["prob_t"])
                      & (gdf["vote_count"] >= o["min_votes"])]
            add_cell(f"{arm}-N{n}-oracle", sub, o["corrected_f1"],
                     f"({o['prob_t']:.2f}, k{o['min_votes']})", "oracle")

    # All-pairs paired permutation + BH + greedy-clique tiers.
    labels = [c["label"] for c in cells]
    pairs: list[dict] = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            a, b = labels[i], labels[j]
            r = paired_permutation(counts_of[a], counts_of[b])
            pairs.append({"a": a, "b": b, "delta_f1": r["delta_f1"],
                          "p_value": r["p_two_sided"]})
    adjusted = apply_bh_correction([p["p_value"] for p in pairs], q=BH_Q)
    significant: dict[frozenset, bool] = {}
    for p, adj in zip(pairs, adjusted):
        p["bh_adjusted_p"] = round(adj, 6)
        p["significant"] = bool(adj < BH_Q)
        significant[frozenset({p["a"], p["b"]})] = p["significant"]
    ordered = sorted(cells, key=lambda c: c["f1_50"], reverse=True)
    tiers = greedy_clique_tiers([c["label"] for c in ordered], significant)
    for rank, tier in enumerate(tiers, start=1):
        for label in tier:
            next(c for c in cells if c["label"] == label)["tier"] = rank
    logger.info("board: %d cells, %d pairs, %d BH-significant, %d tiers",
                len(cells), len(pairs),
                sum(p["significant"] for p in pairs), len(tiers))

    # Named contrasts, read off the family-corrected matrix.
    def pair_of(a: str, b: str) -> dict:
        return next(p for p in pairs
                    if {p["a"], p["b"]} == {a, b})

    named: dict[str, dict] = {}
    for tag, n_label in (("arm1", "N5"), ("arm2", "N5"), ("fourth", "N10")):
        named[f"{tag}-{n_label}: carried vs oracle"] = pair_of(
            f"{tag}-{n_label}-carried", f"{tag}-{n_label}-oracle")
    for arm in ARMS:
        for n in RUNG_NS:
            named[f"{arm}-N{n}: carried vs oracle"] = pair_of(
                f"{arm}-N{n}-carried", f"{arm}-N{n}-oracle")
        for basis in ("carried", "oracle"):
            for lo, hi in ((1, 3), (3, 5)):
                named[f"{arm}: N{lo} vs N{hi} ({basis})"] = pair_of(
                    f"{arm}-N{lo}-{basis}", f"{arm}-N{hi}-{basis}")
    for name, p in named.items():
        logger.info("%s: d=%+.4f p=%.4f adj=%.4f %s", name,
                    p["delta_f1"], p["p_value"], p["bh_adjusted_p"],
                    "SIG" if p["significant"] else "ns")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / "pairwise.csv").open("w", newline="") as fh:
        w = csvmod.DictWriter(fh, fieldnames=list(pairs[0].keys()))
        w.writeheader()
        w.writerows(pairs)
    (OUT_DIR / "grid_board.json").write_text(json.dumps({
        "buffer_m": BUFFER_R, "instrument": (
            "per-sheet paired sign-swap permutation (10000, seed 42) + "
            f"BH q={BH_Q} over all pairs + greedy-clique tiers"),
        "reference": "canonical adjudicated extended GT",
        "cells": ordered, "tiers": tiers, "named_contrasts": named,
    }, indent=2) + "\n")
    logger.info("GRID BOARD COMPLETE -> %s", OUT_DIR.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
