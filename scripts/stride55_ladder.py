#!/usr/bin/env python3
"""
55-map portfolio N-ladder: first-N rungs with inherited verification.

The card's § 3 secondary contract, item 2 (`planning/
55map-portfolio-2026-08-25.md`): the K-subset ladder N ∈ {1, 3, 5} by the
preregistered first-N rule for both deployment runs, verifier
probabilities INHERITED from the committed K = 10 verification (the
method validated at ±0.008 on the gold standard, 2026-08-25). N = 10 is
the committed primary/sweep itself (`stride55_sweep_oracle.py`); it is
rebuilt here only as a gate. Settles bets P2, P4, and P7.

Derivation per cell and rung, mirroring `stride55_prepare_and_union.py`
exactly (no carrier clip — the 55-map corpus is scored full-extent):
first-N deduped passes → `cluster_votes` at c = 1 → standard-grid tile
assignment → probability inheritance by nearest K = 10 candidate within
10 m (unmatched clusters counted, excluded from scoring, included in
cost) → full (prob_t × k ≤ N) sweep of corrected-F1 at 50 m against the
same fixed extended GT as the primary evaluations.

REPLICATION GATES (nothing is written unless all pass):

1. The first-10 rebuild must reproduce the committed K = 10 union:
   exact candidate count, votes identical, every centroid within
   0.2 m of the verifier manifest's (the manifest carries a 4326
   GeoJSON round-trip, so centimetre-scale coordinate drift is
   storage precision, not a clustering difference).
2. The rebuilt N = 10 rung evaluated at the registered primary point
   must equal the engine's committed evaluation @ 50 m to 1e-6
   (`results/stride55-2026-08-27/<run>/primary/eval/corrected-f1.csv`).

P7 (saturation) instrument: per-map paired sign-swap permutation
(10,000, seed 42) of N = 5 versus N = 10, at the carried points and at
the rung oracles.

EXTENDED 2026-09-12 (K-ladder § 4.1, the PI's ruling that the tile-MCC
direction be tested rather than described). Three additive changes; the
committed P7 block and every gate are unchanged:

1. ``--pairs-output-dir`` writes an ADDITIONAL ``ladder_pairs.json``
   covering EVERY rung pair (N = 1 vs the best rung, and each adjacent
   pair), not only N = 5 vs N = 10, with Benjamini-Hochberg (BH)
   adjustment within each cell's ladder.
2. Each pair carries BOTH statistics: the registered corrected-F1
   sign-swap (``paired_permutation``) and its tile-MCC sibling
   (``paired_permutation_mcc``), which uses the SAME 55 pairing units,
   the same seed, the same permutation count and therefore the same
   per-map swap masks — two statistics of one permutation.
3. ``--reuse-oracles`` takes each rung's operating point from the
   COMMITTED ``ladder.json`` instead of re-deriving it by full sweep,
   and gates the rebuilt rung against that file's committed
   ``corrected_f1`` to 1e-6. This is strictly more evidence than the
   sweep (it proves the committed oracle reproduces) at a small
   fraction of the compute.
4. ``--output-dir`` redirects the sweep CSVs and ``ladder.json`` so a
   re-run cannot overwrite the committed 2026-08-27 artefacts.

Usage::

    python scripts/stride55_ladder.py

    # the K-ladder § 4.1 run: committed artefacts untouched
    python scripts/stride55_ladder.py --reuse-oracles \
        --output-dir results/k-ladder-2026-09-12/mcc-test/sign-swap/rebuild \
        --pairs-output-dir results/k-ladder-2026-09-12/mcc-test/sign-swap

Zero API. Run on sapphire (~360 sweep points × 55 Hungarian problems;
``--reuse-oracles`` cuts that to the eight committed operating points).

Created: 2026-08-27 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv as csvmod
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.compute_corrected_f1_multi_buffer import (  # noqa: E402
    DEFAULT_CRS,
    build_extended_gt,
    build_phantom_gdf,
    compute_counts_at_r,
    compute_point_estimate,
)
from scripts.grid_prepare_scoring import CoverageError, load_pass  # noqa: E402
from scripts.h13_k_sensitivity import cluster_votes  # noqa: E402
from scripts.merge_passes import deduplicate_within_pass  # noqa: E402
from scripts.pin_pass_provenance import (  # noqa: E402
    PINNED_CELLS,
    tag_for_cell_dir,
    verify_pin,
)
from scripts.stride55_prepare_and_union import (  # noqa: E402
    CELLS,
    DEDUP_METRES,
    MANDIR,
    OUTROOT,
    VF_CALL_USD,
    resolve_pass_paths,
)
from scripts.stride55_score import (  # noqa: E402
    assign_standard_tile,
    build_map_constrained_index,
)
from scripts.stride55_sweep_oracle import (  # noqa: E402
    BOUNDS,
    BUFFER_R,
    CANONICAL_REVIEW,
    N_PERMS,
    OUT_BASE,
    RUNS,
    SEED,
    STUDENT_GT,
    load_candidates,
    paired_permutation,
    paired_permutation_mcc,
    per_map_counts,
    per_map_tile_confusion,
)
from scripts.apply_fdr_correction import apply_bh_correction  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

NS = (1, 3, 5)
INHERIT_TOL_M = 10.0  # the GS-validated inheritance radius
# First-10 rebuild vs the committed union's verifier manifest. The
# manifest coordinates carry a 4326 GeoJSON round-trip (~7 decimal
# places) plus the extract-stage reprojection, so centimetre-scale
# drift is expected (observed max 0.069 m); identity of the clustering
# is proven by exact count + exact votes, and the 1e-6 primary
# reproduction (gate 2) is the decisive equality test.
UNION_GATE_M = 0.2

# Audited K = 10 proposer flex (card § 4) and the GS-carried N = 5
# operating points (card § 3b, bets P2/P4).
PROP10_USD = {"g384_ov128_55map": 77.31, "g384_ov192_55map": 134.10}
CARRIED_N5 = {"g384_ov128_55map": (0.15, 4), "g384_ov192_55map": (0.15, 5)}

#: The committed ladder result `--reuse-oracles` reads its rung operating
#: points from, and gates the rebuilt rungs against.
COMMITTED_LADDER = OUT_BASE / "ladder.json"
#: BH level, matching every other board in the programme.
FDR_Q = 0.05


def load_deduped_passes(cell: str) -> list[list[dict]]:
    """The ten deduped passes, coverage-gated exactly as the union build.

    Gated first on the cell's committed pass pin
    (``inputs/stride-55map-2026-08-25/<cell>_passes.json``): every
    ``run_<i>`` must carry the pinned ``run_id`` and file hashes, and no
    unpinned pass may exist beyond K. The first-N rungs are ``passes[:n]``
    in this order, so a re-run, a rename or a stray extra pass would
    otherwise change a rung silently (Session 149, MINOR 14).
    """
    manifest = set(json.loads((MANDIR / CELLS[cell]).read_text()))
    cell_dir = OUTROOT / cell
    tag = tag_for_cell_dir(cell_dir)
    verify_pin(tag, PINNED_CELLS[tag])
    passes: list[list[dict]] = []
    for i in range(1, 11):
        run = f"run_{i}"
        raw, processed = load_pass(resolve_pass_paths(cell_dir, run))
        if processed != manifest:
            raise CoverageError(
                f"{cell}/{run}: {len(processed)} tiles vs "
                f"{len(manifest)} pinned")
        passes.append(deduplicate_within_pass(raw, distance_thresh=DEDUP_METRES))
    return passes


def cluster_first_n(passes: list[list[dict]], n: int,
                    index: dict) -> gpd.GeoDataFrame:
    """First-N clusters with votes and standard-grid tile assignment."""
    subset = passes[:n]
    centroids, votes = cluster_votes(subset, 1)
    tiles_flat = [d["source_tiles"][0] for p in subset for d in p]
    pooled = np.asarray([d["centroid"] for p in subset for d in p], dtype=float)
    gdf = gpd.GeoDataFrame(
        {"vote_count": np.asarray(votes)},
        geometry=[Point(xy) for xy in centroids], crs=DEFAULT_CRS)
    _, idx = cKDTree(pooled).query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
    gdf["source_tile"] = [
        assign_standard_tile(index, tiles_flat[i], x, y)
        for i, x, y in zip(idx, gdf.geometry.x, gdf.geometry.y)]
    return gdf



def committed_oracle_points(cell: str) -> dict[int, tuple[float, int, float]]:
    """Each rung's committed operating point and corrected-F1 for one cell.

    Read from the committed ``results/stride55-2026-08-27/ladder.json`` (rungs
    N = 1/3/5) and ``sweep_oracle.json`` (the N = 10 rung, which is the
    committed primary sweep itself). ``--reuse-oracles`` evaluates exactly
    these points instead of re-deriving them, and gates the rebuilt value
    against the committed ``corrected_f1``.

    Args:
        cell: Deployment cell key, e.g. ``g384_ov128_55map``.

    Returns:
        ``{N: (prob_t, min_votes, committed_corrected_f1)}`` for N in 1/3/5/10.
    """
    ladder = json.loads(COMMITTED_LADDER.read_text())["runs"][cell]
    sweep = json.loads((OUT_BASE / "sweep_oracle.json").read_text())["runs"][cell]
    points = {int(n): (r["oracle"]["prob_t"], r["oracle"]["min_votes"],
                       r["oracle"]["corrected_f1"])
              for n, r in ladder["N"].items()}
    points[10] = (sweep["oracle"]["prob_t"], sweep["oracle"]["min_votes"],
                  sweep["oracle"]["corrected_f1"])
    return points


def ladder_pairs(f1_by_n: dict[int, float]) -> list[tuple[int, int, str]]:
    """The rung pairs the K-ladder ruling asks for, as ``(low, high, kind)``.

    Args:
        f1_by_n: Rung N -> corrected-F1 at that rung's operating point.

    Returns:
        N = 1 versus the best rung first, then each adjacent pair not already
        covered by it.
    """
    ns = sorted(f1_by_n)
    best = max(ns, key=lambda n: f1_by_n[n])
    adjacent = [(ns[i], ns[i + 1]) for i in range(len(ns) - 1)]
    out: list[tuple[int, int, str]] = []
    if best != ns[0]:
        kind = ("k1-vs-best+adjacent" if (ns[0], best) in adjacent
                else "k1-vs-best")
        out.append((ns[0], best, kind))
    for lo, hi in adjacent:
        if (lo, hi) == (ns[0], best):
            continue
        out.append((lo, hi, "adjacent"))
    return out


def write_ladder_pairs(out_dir: Path, map_counts_at: dict, map_tiles_at: dict,
                       rung_f1: dict[str, dict[int, float]]) -> None:
    """Sign-swap every rung pair on BOTH statistics, and write the collation.

    The committed ``p7_saturation`` block tests one pair per cell (N = 5 versus
    N = 10) on corrected-F1 alone. The K-ladder ruling asks for N = 1 versus the
    best rung and every adjacent pair, on F1 *and* tile-MCC. This runs the
    registered per-map sign-swap over that pair set with both statistics —
    ``paired_permutation`` and ``paired_permutation_mcc``, which share the seed,
    the permutation count and therefore the per-map swap masks — and
    Benjamini-Hochberg-adjusts each statistic as its own family within each
    cell's ladder.

    Args:
        out_dir: Directory for ``ladder_pairs.json``.
        map_counts_at: ``"<cell>:N<n>:<basis>"`` -> per-map (TP, FP, FN).
        map_tiles_at: the same keys -> per-map (TP, TN, FP, FN) tile confusion.
        rung_f1: cell -> {N: corrected-F1 at that rung's oracle point}.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    payload: dict = {
        "buffer_m": BUFFER_R,
        "basis": "oracle",
        "instrument": {
            "name": "per-map paired sign-swap permutation",
            "script": "scripts/stride55_ladder.py --pairs-output-dir",
            "kernels": [
                "stride55_sweep_oracle.paired_permutation",
                "stride55_sweep_oracle.paired_permutation_mcc",
            ],
            "pairing_unit": "map sheet (55)",
            "f1_statistic": f"corrected-F1 @ {BUFFER_R} m, pooled TP/FP/FN",
            "mcc_statistic": (
                "tile-level MCC, buffer-invariant, pooled per-map tile "
                "confusion"
            ),
            "n_permutations": N_PERMS,
            "seed": SEED,
            "bh_q": FDR_Q,
            "bh_family": "within each cell's ladder, F1 and MCC separately",
            "reference": (
                "the extended GT this instrument was registered against "
                "(student references + canonical adjudicated phantoms gated at "
                "50 m) — NOT the board's materialised r2 reference, which is "
                "why its F1 values differ from the board cells'"
            ),
        },
        "runs": {},
    }
    for cell, f1_by_n in rung_f1.items():
        rows = []
        for lo, hi, kind in ladder_pairs(f1_by_n):
            key_lo = f"{cell}:N{lo}:oracle"
            key_hi = f"{cell}:N{hi}:oracle"
            f1_res = paired_permutation(map_counts_at[key_hi],
                                        map_counts_at[key_lo])
            mcc_res = paired_permutation_mcc(map_tiles_at[key_hi],
                                            map_tiles_at[key_lo])
            rows.append({
                "pair": f"N{lo}-vs-N{hi}", "kind": kind,
                "n_low": lo, "n_high": hi,
                "delta_convention": "higher N minus lower N",
                "f1": {"low": round(f1_by_n[lo], 6),
                       "high": round(f1_by_n[hi], 6),
                       "delta": round(f1_res["delta_f1"], 6),
                       "p_raw": f1_res["p_two_sided"]},
                "mcc": {"delta": round(mcc_res["delta_mcc"], 6),
                        "p_raw": mcc_res["p_two_sided"]},
            })
            logger.info("%s %s: dF1=%+.4f p=%.4f | dMCC=%+.4f p=%.4f",
                        cell, rows[-1]["pair"], f1_res["delta_f1"],
                        f1_res["p_two_sided"], mcc_res["delta_mcc"],
                        mcc_res["p_two_sided"])
        for metric in ("f1", "mcc"):
            adjusted = apply_bh_correction([r[metric]["p_raw"] for r in rows],
                                           q=FDR_Q)
            for r, adj in zip(rows, adjusted):
                r[metric]["p_bh"] = round(adj, 6)
                r[metric]["significant"] = bool(adj < FDR_Q)
        payload["runs"][cell] = {"pairs": rows}
    (out_dir / "ladder_pairs.json").write_text(
        json.dumps(payload, indent=2) + "\n")
    logger.info("wrote %s/ladder_pairs.json", out_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, default=OUT_BASE,
        help="Where the sweep CSVs and ladder.json are written (default: the "
             "committed results/stride55-2026-08-27). Point this elsewhere to "
             "leave the committed artefacts untouched.",
    )
    parser.add_argument(
        "--pairs-output-dir", type=Path, default=None,
        help="When given, also write ladder_pairs.json here: every rung pair "
             "(N=1 vs best, and each adjacent pair) tested on BOTH the "
             "registered corrected-F1 sign-swap and its tile-MCC sibling, "
             "BH-adjusted within each cell's ladder.",
    )
    parser.add_argument(
        "--reuse-oracles", action="store_true",
        help="Take each rung's operating point from the committed ladder.json "
             "instead of re-deriving it by full sweep, and gate the rebuilt "
             "rung against the committed corrected_f1 to 1e-6. Skips the "
             "sweep CSVs.",
    )
    args = parser.parse_args()
    out_base: Path = args.output_dir

    student = gpd.read_file(STUDENT_GT).to_crs(DEFAULT_CRS)
    bounds = gpd.read_file(BOUNDS).to_crs(DEFAULT_CRS)
    empty_y = pd.DataFrame(columns=[
        "candidate_id", "human_label", "buffer_metres", "x", "y", "map_name"])
    review_t = pd.read_csv(CANONICAL_REVIEW)
    phantoms = build_phantom_gdf(empty_y, review_t, BUFFER_R)
    ext_gt = build_extended_gt(student, phantoms)
    logger.info("extended GT at %dm: %d (student %d + phantoms %d, deduped)",
                BUFFER_R, len(ext_gt), len(student), len(phantoms))
    index = build_map_constrained_index()
    committed_points = ({cell: committed_oracle_points(cell) for cell in RUNS}
                        if args.reuse_oracles else {})

    payload: dict = {"buffer_m": BUFFER_R, "inherit_tol_m": INHERIT_TOL_M,
                     "runs": {}}
    map_counts_at: dict[str, dict] = {}
    map_tiles_at: dict[str, dict] = {}
    rung_f1: dict[str, dict[int, float]] = {}
    for cell, spec in RUNS.items():
        passes = load_deduped_passes(cell)
        k10 = load_candidates(cell, spec, bounds)
        tree = cKDTree(np.c_[k10.geometry.x, k10.geometry.y])
        probs10 = k10["mound_probability"].to_numpy()

        # Gate 1: the first-10 rebuild reproduces the committed union.
        rebuilt = cluster_first_n(passes, 10, index)
        if len(rebuilt) != spec["union_n"]:
            raise RuntimeError(
                f"{cell}: union gate FAILED — rebuilt {len(rebuilt)} vs "
                f"committed {spec['union_n']}")
        d10, i10 = tree.query(np.c_[rebuilt.geometry.x, rebuilt.geometry.y],
                              k=1)
        votes_match = (rebuilt["vote_count"].to_numpy()
                       == k10["vote_count"].to_numpy()[i10])
        if d10.max() > UNION_GATE_M or not votes_match.all():
            raise RuntimeError(
                f"{cell}: union gate FAILED — max centroid distance "
                f"{d10.max():.6f} m, vote mismatches "
                f"{int((~votes_match).sum())}")
        logger.info("%s: union gate OK (n=%d, max dist %.6f m)",
                    cell, len(rebuilt), d10.max())

        # Gate 2: the rebuilt N = 10 rung reproduces the committed primary.
        rebuilt["mound_probability"] = probs10[i10]
        pt, pk = spec["primary"]
        sub = rebuilt[(rebuilt["mound_probability"] >= pt)
                      & (rebuilt["vote_count"] >= pk)]
        tp, fp, fn, _ = compute_counts_at_r(sub, ext_gt, bounds, BUFFER_R)
        f1_primary = compute_point_estimate(tp, fp, fn)[2]
        committed = None
        with (OUT_BASE / cell / "primary" / "eval"
              / "corrected-f1.csv").open() as fh:
            for row in csvmod.DictReader(fh):
                if int(row["R_m"]) == BUFFER_R:
                    committed = float(row["F1"])
        if committed is None or abs(f1_primary - committed) > 1e-6:
            raise RuntimeError(
                f"{cell}: primary gate FAILED — ladder-path "
                f"{f1_primary:.6f} vs committed {committed}")
        logger.info("%s: primary gate OK (%.6f)", cell, f1_primary)
        map_counts_at[f"{cell}:N10:carried"] = per_map_counts(
            sub, ext_gt, bounds)
        map_tiles_at[f"{cell}:N10:carried"] = per_map_tile_confusion(
            sub, ext_gt, bounds)

        cell_out = {"prop10_flex_usd": PROP10_USD[cell], "N": {}}
        rows_all = []
        for n in NS:
            gdf = cluster_first_n(passes, n, index)
            d, idx = tree.query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
            gdf["mound_probability"] = probs10[idx]
            matched = d <= INHERIT_TOL_M
            n_total = int(len(gdf))
            gdf = gdf[matched].copy()
            n_unmatched = n_total - int(len(gdf))

            if args.reuse_oracles:
                # Evaluate ONLY the committed operating point, and gate the
                # rebuilt value against the committed corrected-F1. A pass here
                # is strictly stronger evidence than re-deriving the argmax:
                # it proves this code path reproduces the committed rung.
                o_pt, o_k, o_f1 = committed_points[cell][n]
                thresholds = [o_pt]
                votes = [o_k]
            else:
                thresholds = sorted({0.0} | {round(float(v), 4)
                                             for v in gdf["mound_probability"]})
                votes = list(range(1, n + 1))
            rung_rows = []
            for prob_t in thresholds:
                for k in votes:
                    s = gdf[(gdf["mound_probability"] >= prob_t)
                            & (gdf["vote_count"] >= k)]
                    tp, fp, fn, _ = compute_counts_at_r(s, ext_gt, bounds,
                                                        BUFFER_R)
                    p, r, f1 = compute_point_estimate(tp, fp, fn)
                    rung_rows.append({
                        "cell": cell, "N": n, "prob_t": prob_t,
                        "min_votes": k, "n_detections": int(len(s)),
                        "tp": tp, "fp": fp, "fn": fn, "precision": p,
                        "recall": r, "corrected_f1": f1})
            rows_all.extend(rung_rows)
            best = max(rung_rows, key=lambda r: r["corrected_f1"])
            if args.reuse_oracles:
                o_pt, o_k, o_f1 = committed_points[cell][n]
                if abs(best["corrected_f1"] - o_f1) > 1e-6:
                    raise RuntimeError(
                        f"{cell} N={n}: oracle gate FAILED — rebuilt "
                        f"{best['corrected_f1']:.6f} vs committed {o_f1:.6f}")
                logger.info("%s N=%d: oracle gate OK (%.6f at (%.2f, k%d))",
                            cell, n, best["corrected_f1"], o_pt, o_k)

            rung = {
                "union_n": n_total, "unmatched": n_unmatched,
                "match_dist_p50_m": float(np.percentile(d, 50)),
                "match_dist_p95_m": float(np.percentile(d, 95)),
                "oracle": best,
                "est_all_in_flex_usd": round(
                    PROP10_USD[cell] * n / 10 + n_total * VF_CALL_USD, 2),
            }
            if n == 5:
                ct, ck = CARRIED_N5[cell]
                carried = next(r for r in rung_rows
                               if r["prob_t"] == ct and r["min_votes"] == ck)
                rung["carried"] = carried
                s = gdf[(gdf["mound_probability"] >= ct)
                        & (gdf["vote_count"] >= ck)]
                map_counts_at[f"{cell}:N5:carried"] = per_map_counts(
                    s, ext_gt, bounds)
                map_tiles_at[f"{cell}:N5:carried"] = per_map_tile_confusion(
                    s, ext_gt, bounds)
            s = gdf[(gdf["mound_probability"] >= best["prob_t"])
                    & (gdf["vote_count"] >= best["min_votes"])]
            map_counts_at[f"{cell}:N{n}:oracle"] = per_map_counts(
                s, ext_gt, bounds)
            map_tiles_at[f"{cell}:N{n}:oracle"] = per_map_tile_confusion(
                s, ext_gt, bounds)
            rung_f1.setdefault(cell, {})[n] = best["corrected_f1"]
            cell_out["N"][n] = rung
            logger.info(
                "%s N=%d: union %5d (unmatched %d, p95 %.2f m) | oracle "
                "F1=%.4f at (%.2f, k%d) | est $%.2f all-in",
                cell, n, n_total, n_unmatched, rung["match_dist_p95_m"],
                best["corrected_f1"], best["prob_t"], best["min_votes"],
                rung["est_all_in_flex_usd"])

        if not args.reuse_oracles:
            out_csv = out_base / cell / "ladder_sweep_50m.csv"
            out_csv.parent.mkdir(parents=True, exist_ok=True)
            with out_csv.open("w", newline="") as fh:
                w = csvmod.DictWriter(fh, fieldnames=list(rows_all[0].keys()))
                w.writeheader()
                w.writerows(rows_all)
        payload["runs"][cell] = cell_out

    # P7: N = 5 vs N = 10, carried and oracle, per cell. The N = 10
    # oracle counts come from the committed sweep output.
    sweep = json.loads((OUT_BASE / "sweep_oracle.json").read_text())
    for cell, spec in RUNS.items():
        k10 = load_candidates(cell, spec, bounds)
        o = sweep["runs"][cell]["oracle"]
        s = k10[(k10["mound_probability"] >= o["prob_t"])
                & (k10["vote_count"] >= o["min_votes"])]
        map_counts_at[f"{cell}:N10:oracle"] = per_map_counts(s, ext_gt, bounds)
        map_tiles_at[f"{cell}:N10:oracle"] = per_map_tile_confusion(
            s, ext_gt, bounds)
        rung_f1.setdefault(cell, {})[10] = compute_point_estimate(
            *compute_counts_at_r(s, ext_gt, bounds, BUFFER_R)[:3])[2]
        payload["runs"][cell]["p7_saturation"] = {
            "carried_N5_vs_N10": paired_permutation(
                map_counts_at[f"{cell}:N5:carried"],
                map_counts_at[f"{cell}:N10:carried"]),
            "oracle_N5_vs_N10": paired_permutation(
                map_counts_at[f"{cell}:N5:oracle"],
                map_counts_at[f"{cell}:N10:oracle"]),
            "convention": "delta = N5 - N10, corrected-F1@50m",
        }
        for tag, res in payload["runs"][cell]["p7_saturation"].items():
            if isinstance(res, dict) and "delta_f1" in res:
                logger.info("%s N5 - N10 %s: dF1=%+.4f p=%.4f",
                            cell, tag, res["delta_f1"], res["p_two_sided"])

    out_base.mkdir(parents=True, exist_ok=True)
    (out_base / "ladder.json").write_text(json.dumps(payload, indent=2) + "\n")

    if args.pairs_output_dir is not None:
        write_ladder_pairs(args.pairs_output_dir, map_counts_at, map_tiles_at,
                           rung_f1)
    logger.info("LADDER COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
