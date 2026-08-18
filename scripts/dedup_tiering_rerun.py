#!/usr/bin/env python3
# ============================================================================
# dedup_tiering_rerun.py
# ----------------------------------------------------------------------------
# Re-run a committed permutation tiering with the preregistered within-pass
# deduplication (preregistration § 8.5 Step 1, 20 m) applied to the inputs that
# never received it, so that tie-set and tier membership — not just point
# estimates — can be re-decided.
#
# WHY
# ---
# ``reports/scoring-sensitivity-review-2026-08-18.md`` § 5 gap 1 states plainly:
# every deduplicated figure it reports is a point estimate, and "I cannot say
# whether the tie survives. That requires re-running the permutation tiering."
# This script is that re-run. It changes NOTHING about the inference: the
# statistic, the probability-0.5 tile swap, the ``default_rng(seed)`` stream,
# the two-sided p-value, the Benjamini-Hochberg False Discovery Rate (FDR)
# correction at q = 0.05, and the greedy-clique tier merge are imported verbatim
# from the scripts that built the committed boards. The only change is what the
# per-tile arrays are computed FROM.
#
# BOARDS
# ------
# ``diversity-dividend-384``
#     ``scripts/consensus_vs_baseline_tiering.py`` — F1@20 m round-robin over
#     4 consensus champions + the 18 ``n1-baseline-matrix-384`` single-pass
#     cells. The three-member Tier-1 tie mixes one unexposed consensus cell with
#     two dedup-exposed Pro single-pass cells, which is the mixed comparison the
#     review flagged as materially at risk.
# ``55map-mcc``
#     ``scripts/mcc_tiering_55map.py`` — tile-MCC round-robin over the eight
#     canonical (or standardised) 55-map deployment cells. Its sole Tier-1
#     member, ``IM-k3``, is the only dedup-exposed cell on the board, and the
#     board ranks on MCC — the metric the review never measured.
#
# CONTROLS (run these first; they are cheap and they are the audit trail)
# ----------------------------------------------------------------------
#   --dedup none --rank-by eval_f1
#       must reproduce the committed tiers and tie_set exactly;
#   --dedup none --rank-by observed_micro_f1
#       isolates the effect of the ranking-key change alone (the committed board
#       ranks by each cell's ``evaluation.json`` F1, which cannot be recomputed
#       for a deduplicated artefact without re-running the scorer, so the
#       deduplicated arm must rank by the micro-F1 of its own per-tile arrays);
#   --dedup single-pass --rank-by observed_micro_f1
#       the treatment: only artefacts that never reached ``merge_passes`` are
#       deduplicated. ``--dedup all`` additionally re-deduplicates the consensus
#       cells, which quantifies the residual non-idempotency of greedy star
#       clustering.
#
# COST: US$0.00. COMPUTE: sapphire (round-robin permutation sweep).
#
# Usage:
#     python scripts/dedup_tiering_rerun.py --board diversity-dividend-384 \
#         --dedup single-pass --rank-by observed_micro_f1 \
#         --output results/dedup-metric-impact-2026-08-18/tiering-dd384-dedup.json
#
# Author: Shawn Ross & Claude (Anthropic)
# Created: 2026-08-18 (Session 136)
# Licence: Apache 2.0
# ============================================================================

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))

from scripts.apply_fdr_correction import apply_bh_correction  # noqa: E402
from scripts.consensus_vs_baseline_tiering import (  # noqa: E402
    DEFAULT_CELLS,
    read_tile_mcc,
)
from scripts.dedup_metric_impact import dedup_with_provenance  # noqa: E402
from scripts.lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    FDR_Q,
    HEADLINE_BUFFER_M,
    N_PERMUTATIONS,
    PASS_GLOBS,
    SEED,
    TARGET_CRS,
    board_f1_at_20m,
    git_commit,
    greedy_clique_tiers,
    load_baseline_cells,
    micro_f1,
    permutation_test_float,
)
from scripts.pairwise_permutation_test import assign_source_tiles  # noqa: E402


# ── Shared helpers ────────────────────────────────────────────────────

def prepare_detections(
    path: Path,
    gdf_bounds: gpd.GeoDataFrame,
    deduplicate: bool,
) -> gpd.GeoDataFrame:
    """Load one detection artefact, optionally deduplicating it at 20 m.

    Reproduces the committed loaders' CRS handling (a GeoJSON with no declared
    ``crs`` member is EPSG:4326 per RFC 7946) and their ``assign_source_tiles``
    call, which fills a missing ``source_tile`` by spatial join while preserving
    any the artefact already carries.

    Args:
        path: Detection GeoJSON.
        gdf_bounds: Tile bounds in ``TARGET_CRS``.
        deduplicate: Whether to apply the preregistered within-pass 20 m
            deduplication before scoring.

    Returns:
        Detections in ``TARGET_CRS`` with a ``source_tile`` column.
    """
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    gdf = gdf.to_crs(TARGET_CRS)
    gdf = assign_source_tiles(gdf, gdf_bounds)
    if deduplicate:
        gdf, _, _ = dedup_with_provenance(gdf, gdf_bounds)
    return gdf


def per_tile_arrays(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_order: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Align one detection set's per-tile TP/FP/FN onto the fixed tile order.

    Args:
        gdf_det: Detections with ``source_tile``, in ``TARGET_CRS``.
        gdf_ref: References in ``TARGET_CRS``.
        gdf_bounds: Tile bounds in ``TARGET_CRS``.
        tile_order: Fixed tile-name order defining array positions.

    Returns:
        Tuple of float arrays ``(tp, fp, fn)``.
    """
    metrics = compute_per_tile_tp_fp_fn(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=HEADLINE_BUFFER_M
    )
    index = {name: i for i, name in enumerate(tile_order)}
    tp = np.zeros(len(tile_order), dtype=float)
    fp = np.zeros(len(tile_order), dtype=float)
    fn = np.zeros(len(tile_order), dtype=float)
    for _, row in metrics.iterrows():
        i = index.get(row["tile_name"])
        if i is None:
            continue
        tp[i] = float(row["tp"])
        fp[i] = float(row["fp"])
        fn[i] = float(row["fn"])
    return tp, fp, fn


def run_round_robin_and_tier(
    cells: list[dict[str, Any]],
    rank_key: str,
    n_permutations: int,
    seed: int,
) -> tuple[list[dict[str, Any]], list[list[str]], list[dict[str, Any]]]:
    """Round-robin permutation, BH-FDR, and greedy-clique tiering.

    Args:
        cells: Uniform cell dicts carrying ``ref``, ``tp``/``fp``/``fn`` arrays
            and the ranking key.
        rank_key: Cell field to sort by, descending.
        n_permutations: Permutations per pair.
        seed: Random seed.

    Returns:
        Tuple ``(pairwise, tiers, ordered)``.
    """
    pairwise: list[dict[str, Any]] = []
    for a, b in combinations(range(len(cells)), 2):
        ca, cb = cells[a], cells[b]
        res = permutation_test_float(
            ca["tp"], ca["fp"], ca["fn"], cb["tp"], cb["fp"], cb["fn"],
            n_permutations=n_permutations, seed=seed,
        )
        pairwise.append({"ref_a": ca["ref"], "ref_b": cb["ref"], **res})

    adjusted = apply_bh_correction([r["p_value"] for r in pairwise], q=FDR_Q)
    significant: dict[frozenset, bool] = {}
    for r, adj in zip(pairwise, adjusted):
        r["bh_adjusted_p"] = round(adj, 6)
        r["significant"] = bool(adj < FDR_Q)
        significant[frozenset({r["ref_a"], r["ref_b"]})] = r["significant"]

    ordered = sorted(cells, key=lambda c: c[rank_key], reverse=True)
    tiers = greedy_clique_tiers([c["ref"] for c in ordered], significant)
    return pairwise, tiers, ordered


# ── Board: diversity-dividend-384 ─────────────────────────────────────

def board_diversity_dividend(
    dedup_mode: str,
    rank_by: str,
    n_permutations: int,
    seed: int,
    mcc_impact: dict[str, Any] | None,
) -> dict[str, Any]:
    """Rebuild the ``diversity-dividend-384`` tiering under a deduplication mode.

    Cell membership, bounds, ground truth, replicate handling and the statistic
    are all as ``scripts/consensus_vs_baseline_tiering.py`` defines them. Only
    the artefacts fed to ``compute_per_tile_tp_fp_fn`` change.

    Args:
        dedup_mode: ``none``, ``single-pass`` (only artefacts that never reached
            ``merge_passes``), or ``all``.
        rank_by: ``eval_f1`` or ``observed_micro_f1``.
        n_permutations: Permutations per pair.
        seed: Random seed.
        mcc_impact: Optional parsed ``dedup_metric_impact.py`` output, used to
            report each single-pass cell's deduplicated MCC.

    Returns:
        Result dict ready to serialise.
    """
    spec = json.loads(DEFAULT_CELLS.read_text())
    gdf_ref = gpd.read_file(BASE_DIR / spec["ground_truth"]).to_crs(TARGET_CRS)
    gdf_bounds = gpd.read_file(BASE_DIR / spec["bounds"]).to_crs(TARGET_CRS)
    tile_order = list(gdf_bounds["tile_name"].unique())
    print(f"{len(tile_order)} evaluation tiles", flush=True)

    dedup_mcc = {}
    if mcc_impact:
        for cell in mcc_impact["cells"]:
            key = cell.get("condition_id") or cell["name"]
            dedup_mcc[key] = {
                "as_committed": cell["mean_over_passes"]["mcc"]["as_committed"],
                "first_source_tile": cell["mean_over_passes"]["mcc"][
                    "first_source_tile"
                ],
                "nearest_centroid": cell["mean_over_passes"]["mcc"][
                    "nearest_centroid"
                ],
                "union_contributing": cell["mean_over_passes"]["mcc"][
                    "union_contributing"
                ],
            }

    cells: list[dict[str, Any]] = []

    # Consensus champions — one aggregated set each, already through
    # merge_passes, so deduplicated only under --dedup all.
    for champion in spec["champions"]:
        gdf = prepare_detections(
            BASE_DIR / champion["detections"], gdf_bounds, dedup_mode == "all"
        )
        tp, fp, fn = per_tile_arrays(gdf, gdf_ref, gdf_bounds, tile_order)
        eval_path = BASE_DIR / champion["eval_path"]
        cells.append({
            "ref": champion["label"],
            "label": champion["label"],
            "kind": "champion",
            "tp": tp, "fp": fp, "fn": fn,
            "eval_f1": round(board_f1_at_20m(eval_path), 6),
            "observed_micro_f1": round(micro_f1(tp.sum(), fp.sum(), fn.sum()), 6),
            "mcc_committed": read_tile_mcc(eval_path),
            "mcc_deduplicated": None,
            "deduplicated": dedup_mode == "all",
            "n_passes": 1,
        })

    # Single-pass board cells — pass-averaged per-tile arrays.
    for raw in load_baseline_cells(
        BASE_DIR / "results" / "run-conditions.json",
        BASE_DIR / "results" / "run-analyses.json",
    ):
        pool = BASE_DIR / raw["detections"]
        pass_files = sorted({f for g in PASS_GLOBS for f in pool.glob(g)})
        if not pass_files:
            raise FileNotFoundError(f"No passes under {raw['detections']}")
        tp = np.zeros(len(tile_order))
        fp = np.zeros(len(tile_order))
        fn = np.zeros(len(tile_order))
        for pass_file in pass_files:
            gdf = prepare_detections(
                pass_file, gdf_bounds, dedup_mode in ("single-pass", "all")
            )
            a, b, c = per_tile_arrays(gdf, gdf_ref, gdf_bounds, tile_order)
            tp += a
            fp += b
            fn += c
        tp /= len(pass_files)
        fp /= len(pass_files)
        fn /= len(pass_files)
        eval_path = BASE_DIR / raw["eval_path"]
        mcc_block = dedup_mcc.get(raw["ref"], {})
        cells.append({
            "ref": raw["ref"],
            "label": raw["label"],
            "kind": "single-pass",
            "tp": tp, "fp": fp, "fn": fn,
            "eval_f1": round(board_f1_at_20m(eval_path), 6),
            "observed_micro_f1": round(micro_f1(tp.sum(), fp.sum(), fn.sum()), 6),
            "mcc_committed": read_tile_mcc(eval_path),
            "mcc_deduplicated": mcc_block.get("first_source_tile"),
            "mcc_deduplicated_union_contributing": mcc_block.get(
                "union_contributing"
            ),
            "deduplicated": dedup_mode in ("single-pass", "all"),
            "n_passes": len(pass_files),
        })
        print(
            f"  {raw['ref']:65s} passes={len(pass_files):2d} "
            f"micro-F1={cells[-1]['observed_micro_f1']:.4f} "
            f"(eval {cells[-1]['eval_f1']:.4f})",
            flush=True,
        )

    pairwise, tiers, ordered = run_round_robin_and_tier(
        cells, rank_by, n_permutations, seed
    )
    tier_of = {ref: t for t, members in enumerate(tiers, 1) for ref in members}
    return {
        "board": "diversity-dividend-384",
        "source_script": "scripts/consensus_vs_baseline_tiering.py",
        "metric": "f1",
        "buffer_metres": HEADLINE_BUFFER_M,
        "dedup_mode": dedup_mode,
        "dedup_metres": 20.0,
        "rank_by": rank_by,
        "n_permutations": n_permutations,
        "seed": seed,
        "fdr_q": FDR_Q,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "ranking": [
            {
                "rank": i + 1,
                **{k: v for k, v in c.items() if k not in ("tp", "fp", "fn")},
                "tier": tier_of[c["ref"]],
            }
            for i, c in enumerate(ordered)
        ],
        "tiers": [{"tier": i + 1, "members": m} for i, m in enumerate(tiers)],
        "tie_set": tiers[0],
        "pairwise": pairwise,
    }


# ── Board: 55-map tile-MCC ────────────────────────────────────────────

def board_55map_mcc(
    dedup_mode: str,
    reference: str,
    n_permutations: int,
    seed: int,
) -> dict[str, Any]:
    """Rebuild the 55-map tile-MCC tiering under a deduplication mode.

    Imports the committed board's own machinery — ``tile_vectors``,
    ``permutation_test_mcc``, ``mcc_from_confusion`` and the extended
    ground-truth construction — so only the detection artefacts change.

    Args:
        dedup_mode: ``none`` or ``all`` (every cell on this board is a single
            verified accepted set; ``single-pass`` is treated as ``all``).
        reference: ``canonical`` or ``standardised``.
        n_permutations: Permutations per pair.
        seed: Random seed.

    Returns:
        Result dict ready to serialise.
    """
    import pandas as pd

    from scripts.compute_corrected_f1_multi_buffer import (
        DEFAULT_CRS,
        build_extended_gt,
        build_phantom_gdf,
        load_standardised_extension,
    )
    from scripts.mcc_tiering_55map import (
        BUFFER_M,
        CANONICAL_REVIEW,
        CELLS,
        EXTENSION_STD,
        REVIEW_YESTERDAY,
        STUDENT_GT,
        STUDENT_STD,
        TRACK2,
        TRACK2_STD,
        _load_cell_inputs,
        mcc_from_confusion,
        permutation_test_mcc,
        tile_vectors,
    )
    from scripts.mcc_tiering_55map import BOUNDS as MAP55_BOUNDS

    standardised = reference == "standardised"
    gdf_bounds = gpd.read_file(MAP55_BOUNDS)
    if gdf_bounds.crs is None:
        gdf_bounds = gdf_bounds.set_crs("EPSG:4326")
    gdf_bounds = gdf_bounds.to_crs(DEFAULT_CRS)

    if standardised:
        gdf_student = gpd.read_file(STUDENT_STD).to_crs(DEFAULT_CRS)
        gdf_phantoms = load_standardised_extension(EXTENSION_STD, crs=DEFAULT_CRS)
    else:
        gdf_student = gpd.read_file(STUDENT_GT).to_crs(DEFAULT_CRS)
        gdf_phantoms = build_phantom_gdf(
            pd.read_csv(REVIEW_YESTERDAY),
            pd.read_csv(CANONICAL_REVIEW),
            BUFFER_M,
            crs=DEFAULT_CRS,
        )
    gdf_ref = build_extended_gt(gdf_student, gdf_phantoms)
    print(f"reference: {len(gdf_ref)} points; {len(gdf_bounds)} tiles", flush=True)

    cell_base = TRACK2_STD if standardised else TRACK2
    truth: np.ndarray | None = None
    cells: list[dict[str, Any]] = []
    for name, dirname in CELLS.items():
        gdf_det, committed = _load_cell_inputs(cell_base / dirname)
        _, cell_truth, pred_committed = tile_vectors(gdf_det, gdf_ref, gdf_bounds)
        if truth is None:
            truth = cell_truth
        elif not np.array_equal(truth, cell_truth):
            sys.exit("GATE FAIL: truth vector differs between cells")

        gate = {
            "tp": int((pred_committed & truth).sum()),
            "tn": int((~pred_committed & ~truth).sum()),
            "fp": int((pred_committed & ~truth).sum()),
            "fn": int((~pred_committed & truth).sum()),
        }
        expected = {k: committed[k] for k in ("tp", "tn", "fp", "fn")}
        if gate != expected:
            sys.exit(
                f"GATE FAIL: {name} rebuilt confusion {gate} != committed {expected}"
            )

        if dedup_mode == "none":
            pred = pred_committed
            n_removed = 0
        else:
            gdf_dedup, contributing, stats = dedup_with_provenance(
                gdf_det, gdf_bounds
            )
            _, _, pred = tile_vectors(gdf_dedup, gdf_ref, gdf_bounds)
            n_removed = stats["n_removed"]
            # Membership-preserving control: every contributing tile stays
            # predicted-populated, which by construction reproduces the
            # committed prediction vector.
            union = {t for tiles in contributing for t in tiles}
            union_pred = np.array(
                [t in union for t in gdf_bounds["tile_name"].unique()], dtype=bool
            )
            if not np.array_equal(union_pred, pred_committed):
                print(
                    f"  NOTE: {name} union-contributing prediction vector differs "
                    "from the committed one (unexpected — inspect provenance)",
                    flush=True,
                )

        confusion = {
            "tp": int((pred & truth).sum()),
            "tn": int((~pred & ~truth).sum()),
            "fp": int((pred & ~truth).sum()),
            "fn": int((~pred & truth).sum()),
        }
        mcc = float(mcc_from_confusion(**confusion))
        cells.append({
            "ref": name,
            "label": name,
            "condition_dir": str((cell_base / dirname).relative_to(BASE_DIR)),
            "mcc_committed": committed["mcc"],
            "mcc_committed_ci": committed.get("mcc_CI"),
            "mcc": round(mcc, 6),
            "delta_mcc": round(mcc - committed["mcc"], 6),
            "confusion": confusion,
            "confusion_committed": expected,
            "n_removed_by_dedup": n_removed,
            "pred": pred,
        })
        print(
            f"  {name:<24} MCC {committed['mcc']:.4f} -> {mcc:.4f} "
            f"(Δ {mcc - committed['mcc']:+.4f}; {n_removed} feature(s) removed)",
            flush=True,
        )

    assert truth is not None
    pairwise = []
    significant: dict[frozenset, bool] = {}
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            a, b = cells[i], cells[j]
            res = permutation_test_mcc(
                a["pred"], b["pred"], truth,
                n_permutations=n_permutations, seed=seed,
            )
            pairwise.append({"ref_a": a["ref"], "ref_b": b["ref"], **res})
    adjusted = apply_bh_correction([p["p_value"] for p in pairwise], q=FDR_Q)
    for p, adj in zip(pairwise, adjusted):
        p["bh_adjusted_p"] = round(adj, 6)
        p["significant"] = bool(adj < FDR_Q)
        significant[frozenset({p["ref_a"], p["ref_b"]})] = p["significant"]

    ordered = sorted(cells, key=lambda c: -c["mcc"])
    tiers = greedy_clique_tiers([c["ref"] for c in ordered], significant)
    tier_of = {ref: t for t, members in enumerate(tiers, 1) for ref in members}
    return {
        "board": f"55map-mcc-{reference}",
        "source_script": "scripts/mcc_tiering_55map.py",
        "metric": "tile_mcc",
        "buffer_metres": BUFFER_M,
        "dedup_mode": dedup_mode,
        "dedup_metres": 20.0,
        "rank_by": "tile_mcc",
        "n_permutations": n_permutations,
        "seed": seed,
        "fdr_q": FDR_Q,
        "n_tiles": int(len(truth)),
        "n_populated_tiles": int(truth.sum()),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "gate": "rebuilt committed confusion == summary.json (exact), 8/8",
        "ranking": [
            {"rank": i + 1,
             **{k: v for k, v in c.items() if k != "pred"},
             "tier": tier_of[c["ref"]]}
            for i, c in enumerate(ordered)
        ],
        "tiers": [{"tier": i + 1, "members": m} for i, m in enumerate(tiers)],
        "tie_set": tiers[0],
        "pairwise": pairwise,
    }


# ── Board: any run-analyses board via the generic Era-1 harness ───────

def board_generic_analysis(
    analysis_id: str,
    dedup_mode: str,
    rank_by: str,
    n_permutations: int,
    seed: int,
) -> dict[str, Any]:
    """Rebuild any ``run-analyses.json`` board through ``era1_leaderboard_tiering``.

    That harness is already generic: it reads board membership from a named
    analysis's ``conditions_compared`` and reproduces each cell's per-tile
    counts from the cell's own recorded ``cli_args``, dispatching between
    single-set and replicate-mean cells. Both branches funnel through one
    function, ``_per_tile_one_set``, which receives a detection set that already
    carries ``source_tile``.

    Deduplication is therefore injected by replacing that single function for
    the duration of the run, rather than by reimplementing the loader — the cell
    dispatch, the CRS contract, the ranking, the permutation and the tiering all
    stay byte-identical to the committed board. The injection is uniform: every
    cell is scored through the same 20 m deduplication, which is the point (an
    asymmetric scoring path is the confound being removed). Cells already built
    by ``merge_passes`` lose only their residual, measured at 0–3.4 %.

    Args:
        analysis_id: The analysis whose ``conditions_compared`` defines the board.
        dedup_mode: ``none`` or anything else (treated as "deduplicate uniformly").
        rank_by: ``eval_f1`` or ``observed_micro_f1``.
        n_permutations: Permutations per pair.
        seed: Random seed.

    Returns:
        Result dict ready to serialise.
    """
    from scripts import era1_leaderboard_tiering as era1

    original = era1._per_tile_one_set

    def _dedup_then_score(gdf_det, gdf_ref, gdf_bounds, tile_order):
        """Deduplicate at 20 m, then delegate to the committed per-tile scorer."""
        gdf_dedup, _, _ = dedup_with_provenance(gdf_det, gdf_bounds)
        return original(gdf_dedup, gdf_ref, gdf_bounds, tile_order)

    if dedup_mode != "none":
        era1._per_tile_one_set = _dedup_then_score
    try:
        cells, _gdf_ref, _gdf_bounds, _tile_order = era1.load_cells(
            BASE_DIR / "results" / "run-conditions.json",
            BASE_DIR / "results" / "run-analyses.json",
            analysis_id,
            None,
            None,
        )
    finally:
        era1._per_tile_one_set = original

    for cell in cells:
        cell["mcc_committed"] = cell.pop("mcc", None)

    pairwise, tiers, ordered = run_round_robin_and_tier(
        cells, rank_by, n_permutations, seed
    )
    tier_of = {ref: t for t, members in enumerate(tiers, 1) for ref in members}
    return {
        "board": analysis_id,
        "source_script": "scripts/era1_leaderboard_tiering.py",
        "metric": "f1",
        "buffer_metres": HEADLINE_BUFFER_M,
        "dedup_mode": dedup_mode,
        "dedup_metres": 20.0,
        "rank_by": rank_by,
        "n_permutations": n_permutations,
        "seed": seed,
        "fdr_q": FDR_Q,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "ranking": [
            {
                "rank": i + 1,
                **{k: v for k, v in c.items() if k not in ("tp", "fp", "fn")},
                "tier": tier_of[c["ref"]],
            }
            for i, c in enumerate(ordered)
        ],
        "tiers": [{"tier": i + 1, "members": m} for i, m in enumerate(tiers)],
        "tie_set": tiers[0],
        "pairwise": pairwise,
    }


def main() -> int:
    """CLI entry point.

    Returns:
        Process exit code (0 on success).
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", required=True,
                        choices=["diversity-dividend-384", "55map-mcc", "analysis"])
    parser.add_argument("--analysis-id", type=str, default=None,
                        help="--board analysis only: the run-analyses.json board.")
    parser.add_argument("--dedup", default="single-pass",
                        choices=["none", "single-pass", "all"])
    parser.add_argument("--rank-by", default="observed_micro_f1",
                        choices=["eval_f1", "observed_micro_f1"])
    parser.add_argument("--reference", default="canonical",
                        choices=["canonical", "standardised"],
                        help="55map-mcc board only.")
    parser.add_argument("--mcc-impact", type=Path, default=None,
                        help="dedup_metric_impact.py output, for the MCC column.")
    parser.add_argument("--n-permutations", type=int, default=N_PERMUTATIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.board == "diversity-dividend-384":
        impact = (
            json.loads(args.mcc_impact.read_text()) if args.mcc_impact else None
        )
        result = board_diversity_dividend(
            args.dedup, args.rank_by, args.n_permutations, args.seed, impact
        )
    elif args.board == "55map-mcc":
        result = board_55map_mcc(
            args.dedup, args.reference, args.n_permutations, args.seed
        )
    else:
        if not args.analysis_id:
            parser.error("--board analysis requires --analysis-id")
        result = board_generic_analysis(
            args.analysis_id, args.dedup, args.rank_by,
            args.n_permutations, args.seed,
        )

    print(
        f"Tier 1 ({len(result['tie_set'])} member(s)): "
        f"{', '.join(result['tie_set'])}",
        flush=True,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote {args.output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
