#!/usr/bin/env python3
# ============================================================================
# consensus_vs_baseline_tiering.py
# ----------------------------------------------------------------------------
# The diversity-dividend statistical test (H3): a combined, statistically
# tiered leaderboard placing the best consensus operating points against the
# N=1 single-pass baseline board, using the project-canonical round-robin
# tile-swap permutation + Benjamini-Hochberg FDR + greedy-clique tiering.
#
# WHAT THIS PRODUCES
# ------------------
# A single tiered leaderboard over (consensus champions + the 18 single-pass
# baseline cells of ``n1-baseline-matrix-384``). The tiers answer the two
# named claims of the diversity-dividend test:
#   1. Diversity dividend -- HIGH-thinking consensus tiers above (or with)
#      minimal-thinking consensus at matched modality.
#   2. Consensus vs single-pass -- where each consensus champion lands
#      relative to its matched Flash single-pass baseline and the genuine-Pro
#      single-pass leader.
#
# WHY THIS REUSES THE N=1 LEADERBOARD MACHINERY
# ---------------------------------------------
# The beacon's brief is "round-robin tile-swap permutation + BH-FDR, a la the
# n1 leaderboard". This script imports ``permutation_test_float``,
# ``micro_f1``, ``greedy_clique_tiers``, ``pass_averaged_per_tile``,
# ``board_f1_at_20m`` and ``load_baseline_cells`` from
# ``n1_baseline_leaderboard_tiering`` so the statistic, the probability-0.5
# tile swap, the ``numpy.random.default_rng(seed)`` stream, the two-sided
# p-value, the BH-FDR (q=0.05), and the greedy clique are BYTE-FOR-BYTE the
# same test the single-pass board already passed.
#
# THE ONE NEW PIECE: consensus cells are a single aggregated set
# --------------------------------------------------------------
# A single-pass board cell is an EXPECTATION over replicate passes, so it is
# summarised as the pass-AVERAGED (float) per-tile TP/FP/FN. A consensus cell
# is ONE aggregated detection set (the vote-thresholded pool), so its per-tile
# TP/FP/FN are the INTEGER counts of that one set -- ``consensus_per_tile``
# below. Both are float arrays on the same fixed 487-tile order, so they feed
# the identical ``permutation_test_float`` unchanged. The micro-F1 of a single
# set and the micro-F1-of-the-pass-mean are both "the F1 the leaderboard
# ranks", so the comparison is like-for-like on the quantity each cell
# represents.
#
# OPERATING-POINT PROVENANCE (E56)
# --------------------------------
# The consensus champions sit at their best-F1@20 m vote threshold, which is
# selected on the 487-tile EVALUATION (= test) set and is therefore IN-SAMPLE
# (E56). The companion ``--kinds champion,deployable`` run adds the honest
# a-priori N=5 operating points (text 4-of-5, image 3-of-5; the 55maps
# deployment thresholds) so the deployable performance is tiered too. The
# output records ``operating_point_provenance`` on every consensus cell.
#
# METRIC
# ------
# Tiering ranks F1@20 m (the preregistered headline). MCC (buffer-agnostic
# tile-level discrimination, ``summary.tile_classification.mcc.point``) is
# carried as a reported column on every cell, per the standing
# report-MCC-with-F1 preference; it is NOT the permutation statistic (the n1
# board tiers on F1 too).
#
# COMPUTE LOCATION
# ----------------
# A round-robin permutation sweep -- "computationally intensive" per the
# project CLAUDE.md. Run on zbook or sapphire, never on amd-tower.
#
# Usage:
#     python scripts/consensus_vs_baseline_tiering.py \
#         --cells planning/diversity-dividend-cells-2026-06-06.json \
#         --kinds champion \
#         --output-dir results/diversity-dividend-384/tiering-champions
#
# Author: Shawn Ross & Claude (Anthropic)
# Created: 2026-06-06
# Licence: Apache 2.0
# ============================================================================

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

# Import the canonical N=1 leaderboard machinery verbatim -- the statistic,
# the float tile-swap, the tiering, and the per-cell helpers are shared so
# this test is identical to the one the single-pass board passed.
from n1_baseline_leaderboard_tiering import (  # noqa: E402
    FDR_Q,
    HEADLINE_BUFFER_M,
    N_PERMUTATIONS,
    SEED,
    TARGET_CRS,
    board_f1_at_20m,
    git_commit,
    greedy_clique_tiers,
    load_baseline_cells,
    micro_f1,
    pass_averaged_per_tile,
    permutation_test_float,
)

from apply_fdr_correction import apply_bh_correction  # noqa: E402
from lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402
from pairwise_permutation_test import assign_source_tiles  # noqa: E402

DEFAULT_GT = BASE_DIR / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
DEFAULT_BOUNDS = (
    BASE_DIR / "inputs" / "vectors" / "bounds" / "384" / "full_evaluation_bounds.geojson"
)
DEFAULT_CELLS = BASE_DIR / "planning" / "diversity-dividend-cells-2026-06-06.json"
DEFAULT_OUTPUT = BASE_DIR / "results" / "diversity-dividend-384" / "tiering"

# The genuine-Pro single-pass leader (Tier 1 of the n1 board) -- the
# cross-architecture comparator for the headline "Flash consensus vs Pro
# single-pass" contrast. NB this ref is hard-coded: an E-series board edit that
# REPLACED the Pro leader would leave this contrast unresolved -- ``contrast()``
# returns None and the row is filtered out (no crash), so re-point it here if
# the n1 board's Tier-1 leader ever changes.
PRO_LEADER_REF = "n1-pro-rerun-384::baseline-pro-text-high-t-0-0"


def read_tile_mcc(eval_path: Path) -> float | None:
    """Read a cell's buffer-agnostic tile-level MCC point estimate.

    The MCC lives in ``summary.tile_classification.mcc.point`` (NOT in the
    per-buffer block, where ``mcc`` is always null). This is the same field
    the n1 board reports as its secondary metric.

    Args:
        eval_path: Path to the cell's evaluation.json.

    Returns:
        The tile-level MCC point estimate, or ``None`` if absent.
    """
    summary = json.loads(eval_path.read_text())["summary"]
    return summary.get("tile_classification", {}).get("mcc", {}).get("point")


def consensus_per_tile(
    geojson_path: Path,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_order: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute a consensus cell's per-tile TP/FP/FN from one aggregated set.

    A consensus cell is a SINGLE vote-thresholded detection set, so -- unlike
    a single-pass board cell -- there is no replicate averaging: the per-tile
    counts are the integer TP/FP/FN of that one set. The matching is the
    canonical ``compute_per_tile_tp_fp_fn`` (Hungarian per map, 20 m), aligned
    to the fixed ``tile_order``. Returned as float arrays so they drop
    straight into ``permutation_test_float`` beside the pass-averaged board
    cells.

    Args:
        geojson_path: The consensus_tK.geojson for this operating point.
        gdf_ref: Ground-truth references (projected to TARGET_CRS).
        gdf_bounds: Evaluation tile boundaries (projected to TARGET_CRS).
        tile_order: Fixed list of tile_name values defining array positions.

    Returns:
        Tuple ``(tp, fp, fn)`` of float arrays, length ``len(tile_order)``.

    Raises:
        FileNotFoundError: If the consensus geojson does not exist.
    """
    full_path = BASE_DIR / geojson_path
    if not full_path.exists():
        raise FileNotFoundError(f"Consensus geojson not found: {geojson_path}")

    gdf_det = gpd.read_file(full_path)
    if len(gdf_det) == 0:
        # A vote threshold higher than any tile's agreement empties the pool.
        # The cell is not dropped (it is a legitimate F1=0 operating point), but
        # the operator must be told rather than left to infer it from a 0.0 row.
        print(f"  WARNING: consensus set {geojson_path} has zero detections "
              f"-> enters the board as an F1=0 cell", flush=True)
    if gdf_det.crs is None:
        gdf_det = gdf_det.set_crs("EPSG:4326")
    gdf_det = gdf_det.to_crs(TARGET_CRS)
    gdf_det = assign_source_tiles(gdf_det, gdf_bounds)
    tile_metrics = compute_per_tile_tp_fp_fn(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=HEADLINE_BUFFER_M
    )

    tile_index = {name: i for i, name in enumerate(tile_order)}
    n_tiles = len(tile_order)
    tp = np.zeros(n_tiles, dtype=float)
    fp = np.zeros(n_tiles, dtype=float)
    fn = np.zeros(n_tiles, dtype=float)
    for _, row in tile_metrics.iterrows():
        idx = tile_index.get(row["tile_name"])
        if idx is None:
            continue
        tp[idx] = float(row["tp"])
        fp[idx] = float(row["fp"])
        fn[idx] = float(row["fn"])
    return tp, fp, fn


def load_board_cells_with_stats(
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_order: list[str],
) -> list[dict]:
    """Load the 18 single-pass board cells with per-tile stats, F1 and MCC.

    Reuses ``load_baseline_cells`` (board membership = the
    ``n1-baseline-matrix-384`` analysis's ``conditions_compared``) and
    ``pass_averaged_per_tile`` so these cells are byte-identical to the n1
    tiering.

    Args:
        gdf_ref: Ground-truth references (projected to TARGET_CRS).
        gdf_bounds: Evaluation tile boundaries (projected to TARGET_CRS).
        tile_order: Fixed list of tile_name values.

    Returns:
        List of uniform cell dicts (see ``_uniform_cell``).
    """
    cells = []
    for raw in load_baseline_cells(
        BASE_DIR / "results" / "run-conditions.json",
        BASE_DIR / "results" / "run-analyses.json",
    ):
        tp, fp, fn, n_passes = pass_averaged_per_tile(
            Path(raw["detections"]), gdf_ref, gdf_bounds, tile_order
        )
        eval_path = BASE_DIR / raw["eval_path"]
        cells.append(
            _uniform_cell(
                ref=raw["ref"],
                label=raw["label"],
                kind="single-pass",
                tp=tp,
                fp=fp,
                fn=fn,
                eval_f1=board_f1_at_20m(eval_path),
                mcc=read_tile_mcc(eval_path),
                meta={"n_passes": n_passes, "operating_point_provenance": "single-pass"},
            )
        )
    return cells


def load_consensus_cells_with_stats(
    spec: dict,
    kinds: set[str],
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_order: list[str],
) -> list[dict]:
    """Load the requested consensus cells (champions and/or deployable).

    Args:
        spec: The parsed cell-spec JSON (champions + deployable lists).
        kinds: Which kinds to include, subset of {"champion", "deployable"}.
        gdf_ref: Ground-truth references (projected to TARGET_CRS).
        gdf_bounds: Evaluation tile boundaries (projected to TARGET_CRS).
        tile_order: Fixed list of tile_name values.

    Returns:
        List of uniform cell dicts.
    """
    cells = []
    for group in ("champions", "deployable"):
        for c in spec.get(group, []):
            if c["kind"] not in kinds:
                continue
            tp, fp, fn = consensus_per_tile(
                Path(c["detections"]), gdf_ref, gdf_bounds, tile_order
            )
            eval_path = BASE_DIR / c["eval_path"]
            provenance = (
                "in-sample best-F1@20m (test-set-selected; E56)"
                if c["kind"] == "champion"
                else f"a-priori N=5 vote {c['vote']}-of-{c['pool_N']} (55maps-matched)"
            )
            cells.append(
                _uniform_cell(
                    ref=c["label"],
                    label=c["label"],
                    kind=c["kind"],
                    tp=tp,
                    fp=fp,
                    fn=fn,
                    eval_f1=board_f1_at_20m(eval_path),
                    mcc=read_tile_mcc(eval_path),
                    meta={
                        "thinking": c["thinking"],
                        "modality": c["modality"],
                        "temperature": c["temperature"],
                        "pool": c["pool"],
                        "vote": f"{c['vote']}-of-{c['pool_N']}",
                        "matched_single_pass_ref": c.get("matched_single_pass_ref"),
                        "operating_point_provenance": provenance,
                    },
                )
            )
    return cells


def _uniform_cell(
    ref: str,
    label: str,
    kind: str,
    tp: np.ndarray,
    fp: np.ndarray,
    fn: np.ndarray,
    eval_f1: float,
    mcc: float | None,
    meta: dict,
) -> dict:
    """Assemble a uniform cell dict shared by board and consensus cells.

    Args:
        ref: Unique cell identifier (board ``<run>::<label>`` or consensus label).
        label: Display label.
        kind: One of "single-pass", "champion", "deployable".
        tp, fp, fn: Per-tile count arrays (float).
        eval_f1: The cell's F1@20 m as reported by its evaluation.json (the
            ranked headline metric).
        mcc: The cell's tile-level MCC point estimate.
        meta: Extra per-kind metadata.

    Returns:
        The uniform cell dict.
    """
    return {
        "ref": ref,
        "label": label,
        "kind": kind,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "eval_f1": round(float(eval_f1), 6),
        "observed_micro_f1": round(micro_f1(tp.sum(), fp.sum(), fn.sum()), 6),
        "mcc": round(float(mcc), 6) if mcc is not None else None,
        **meta,
    }


def run_round_robin(cells: list[dict], n_permutations: int, seed: int) -> list[dict]:
    """Run the C(N, 2) float tile-swap permutation tests over all cell pairs.

    Args:
        cells: Uniform cell dicts (each with tp/fp/fn arrays).
        n_permutations: Permutations per pair.
        seed: Random seed.

    Returns:
        List of pairwise result dicts (``ref_a``, ``ref_b`` + permutation stats).
    """
    pairwise = []
    for a, b in combinations(range(len(cells)), 2):
        ca, cb = cells[a], cells[b]
        res = permutation_test_float(
            ca["tp"], ca["fp"], ca["fn"], cb["tp"], cb["fp"], cb["fn"],
            n_permutations=n_permutations, seed=seed,
        )
        pairwise.append({"ref_a": ca["ref"], "ref_b": cb["ref"], **res})
    return pairwise


def extract_named_contrasts(
    cells: list[dict], significant: dict[frozenset, bool], pair_lookup: dict[frozenset, dict]
) -> list[dict]:
    """Extract the headline diversity-dividend contrasts from the round-robin.

    Pulls the specific pairs that answer the two named claims, so they are
    reported explicitly rather than buried in the C(N, 2) table:
      - diversity dividend: HIGH vs minimal consensus at matched modality;
      - consensus vs matched single-pass: each champion vs its matched cell;
      - consensus vs Pro leader: text-HIGH champion vs the Pro single-pass leader.

    Args:
        cells: The tiered cells.
        significant: Map ``frozenset({ref_a, ref_b})`` -> BH-significant.
        pair_lookup: Map ``frozenset({ref_a, ref_b})`` -> the pairwise result.

    Returns:
        List of contrast dicts (claim, ref_a, ref_b, f1s, diff, p, bh_p, significant).
    """
    by_ref = {c["ref"]: c for c in cells}

    def contrast(claim: str, ref_a: str, ref_b: str) -> dict | None:
        key = frozenset({ref_a, ref_b})
        pair = pair_lookup.get(key)
        if pair is None or ref_a not in by_ref or ref_b not in by_ref:
            return None
        return {
            "claim": claim,
            "ref_a": ref_a,
            "ref_b": ref_b,
            "f1_a": by_ref[ref_a]["eval_f1"],
            "f1_b": by_ref[ref_b]["eval_f1"],
            "f1_diff": round(by_ref[ref_a]["eval_f1"] - by_ref[ref_b]["eval_f1"], 6),
            "mcc_a": by_ref[ref_a]["mcc"],
            "mcc_b": by_ref[ref_b]["mcc"],
            "p_value": pair["p_value"],
            "bh_adjusted_p": pair.get("bh_adjusted_p"),
            "significant": significant.get(key),
        }

    contrasts = []
    # One champion per (modality, thinking) is assumed by the diversity-dividend
    # contrast. Fail loud rather than silently overwrite if a spec ever supplies
    # two champions for the same combination.
    champs: dict[tuple[str, str], str] = {}
    for c in cells:
        if c["kind"] != "champion":
            continue
        key = (c["modality"], c["thinking"])
        if key in champs:
            raise ValueError(
                f"Two champion cells share (modality, thinking)={key} "
                f"({champs[key]} and {c['ref']}); the diversity-dividend contrast "
                f"expects exactly one champion per modality x thinking — fix the cell spec."
            )
        champs[key] = c["ref"]
    # 1. Diversity dividend (HIGH vs minimal) at matched modality.
    for modality in ("text", "image"):
        hi, lo = champs.get((modality, "high")), champs.get((modality, "minimal"))
        if hi and lo:
            contrasts.append(contrast(
                f"diversity-dividend ({modality}): HIGH vs minimal consensus", hi, lo))
    # 2. Consensus champion vs its matched single-pass baseline.
    for c in cells:
        if c["kind"] in ("champion", "deployable") and c.get("matched_single_pass_ref"):
            contrasts.append(contrast(
                f"consensus vs matched single-pass ({c['label']})",
                c["ref"], c["matched_single_pass_ref"]))
    # 3. Text-HIGH champion vs the genuine-Pro single-pass leader.
    text_high = champs.get(("text", "high"))
    if text_high:
        contrasts.append(contrast(
            "Flash text-HIGH consensus vs Pro single-pass leader",
            text_high, PRO_LEADER_REF))
    return [c for c in contrasts if c is not None]


def main() -> int:
    """CLI entry point: load cells, round-robin, tier, write results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cells", type=Path, default=DEFAULT_CELLS)
    # Default None so the cell spec stays authoritative for bounds + ground
    # truth (an explicit CLI value overrides it); see resolution below.
    parser.add_argument("--ground-truth", type=Path, default=None)
    parser.add_argument("--bounds", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--kinds", type=str, default="champion",
        help="Comma-separated consensus kinds to include: champion[,deployable].",
    )
    parser.add_argument("--n-permutations", type=int, default=N_PERMUTATIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    kinds = {k.strip() for k in args.kinds.split(",") if k.strip()}
    spec = json.loads(args.cells.read_text())

    # Resolve bounds + ground truth: explicit CLI arg wins; else the spec's own
    # declaration (so the analysis carries its evaluation scope with it); else
    # the module defaults. Guards the audit's "spec bounds silently ignored" gap.
    ground_truth = args.ground_truth or (
        BASE_DIR / spec["ground_truth"] if "ground_truth" in spec else DEFAULT_GT)
    bounds = args.bounds or (
        BASE_DIR / spec["bounds"] if "bounds" in spec else DEFAULT_BOUNDS)

    print(f"Loading references {ground_truth.name} and bounds {bounds.name} ...",
          flush=True)
    gdf_ref = gpd.read_file(ground_truth).to_crs(TARGET_CRS)
    gdf_bounds = gpd.read_file(bounds).to_crs(TARGET_CRS)
    tile_order = list(gdf_bounds["tile_name"].unique())
    print(f"  {len(tile_order)} evaluation tiles", flush=True)

    board = load_board_cells_with_stats(gdf_ref, gdf_bounds, tile_order)
    consensus = load_consensus_cells_with_stats(
        spec, kinds, gdf_ref, gdf_bounds, tile_order
    )
    cells = consensus + board
    print(f"Loaded {len(consensus)} consensus cells ({sorted(kinds)}) "
          f"+ {len(board)} single-pass cells = {len(cells)} total", flush=True)
    for c in cells:
        gap = c["observed_micro_f1"] - c["eval_f1"]
        print(f"  {c['kind']:12s} {c['label']:46s} "
              f"eval-F1={c['eval_f1']:.4f} micro-F1={c['observed_micro_f1']:.4f} "
              f"gap={gap:+.4f} MCC={c['mcc']}", flush=True)

    pairs = list(combinations(range(len(cells)), 2))
    print(f"Running {len(pairs)} pairwise permutation tests "
          f"({args.n_permutations} perms each, seed {args.seed}) ...", flush=True)
    pairwise = run_round_robin(cells, args.n_permutations, args.seed)

    raw_p = [r["p_value"] for r in pairwise]
    adjusted = apply_bh_correction(raw_p, q=FDR_Q)
    significant: dict[frozenset, bool] = {}
    pair_lookup: dict[frozenset, dict] = {}
    for r, adj in zip(pairwise, adjusted):
        r["bh_adjusted_p"] = round(adj, 6)
        r["significant"] = bool(adj < FDR_Q)
        key = frozenset({r["ref_a"], r["ref_b"]})
        significant[key] = r["significant"]
        pair_lookup[key] = r

    # Rank by the cell's eval-reported F1@20m (the headline the leaderboard
    # presents), while the permutation/tiering operate on observed_micro_f1 (the
    # F1-of-the-per-tile-arrays). For consensus cells the two are identical; for
    # single-pass cells they can differ slightly (micro-F1-of-the-pass-mean vs
    # the eval's mean F1 -- the printed `gap` above). This is the same split the
    # n1 board uses (it sorts by board_f1); the gaps here are <=0.0005, so the
    # ranking and the tier-merge decisions agree.
    ordered = sorted(cells, key=lambda c: c["eval_f1"], reverse=True)
    ordered_refs = [c["ref"] for c in ordered]
    tiers = greedy_clique_tiers(ordered_refs, significant)
    tie_set = tiers[0]
    n_sig = sum(1 for r in pairwise if r["significant"])
    print(f"FDR: {n_sig}/{len(pairwise)} pairs significant at q={FDR_Q} "
          f"-> {len(tiers)} tiers; Tier 1 = {len(tie_set)} cell(s)", flush=True)

    contrasts = extract_named_contrasts(ordered, significant, pair_lookup)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    tier_of = {ref: t for t, members in enumerate(tiers, 1) for ref in members}
    result = {
        "analysis": "diversity-dividend-consensus-vs-baseline-384",
        "metric": "f1",
        "buffer_metres": HEADLINE_BUFFER_M,
        "n_permutations": args.n_permutations,
        "seed": args.seed,
        "fdr_q": FDR_Q,
        "kinds_included": sorted(kinds),
        "n_consensus_cells": len(consensus),
        "n_single_pass_cells": len(board),
        "replicate_handling": (
            "single-pass: pass-averaged per-tile; consensus: single aggregated "
            "set per-tile (integer)"
        ),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "ranking": [
            {
                "rank": i + 1,
                "ref": c["ref"],
                "label": c["label"],
                "kind": c["kind"],
                "thinking": c.get("thinking"),
                "modality": c.get("modality"),
                "vote": c.get("vote"),
                "eval_f1": c["eval_f1"],
                "observed_micro_f1": c["observed_micro_f1"],
                "mcc": c["mcc"],
                "operating_point_provenance": c.get("operating_point_provenance"),
                "tier": tier_of[c["ref"]],
            }
            for i, c in enumerate(ordered)
        ],
        "tiers": [{"tier": i + 1, "members": m} for i, m in enumerate(tiers)],
        "tie_set": tie_set,
        "headline_contrasts": contrasts,
        "pairwise": pairwise,
    }
    json_path = args.output_dir / "tiering_20m.json"
    json_path.write_text(json.dumps(result, indent=2))
    print(f"Wrote {json_path}", flush=True)

    _write_markdown(args.output_dir / "tiering_20m.md", result, ordered, tier_of)
    print(f"Wrote {args.output_dir / 'tiering_20m.md'}", flush=True)
    return 0


def _write_markdown(md_path: Path, result: dict, ordered: list[dict],
                    tier_of: dict[str, int]) -> None:
    """Write the human-readable tiering Markdown."""
    lines = [
        "# Diversity dividend — consensus vs single-pass baseline (20 m)",
        "",
        f"- **Cells**: {result['n_consensus_cells']} consensus "
        f"({', '.join(result['kinds_included'])}) + "
        f"{result['n_single_pass_cells']} single-pass = "
        f"{result['n_consensus_cells'] + result['n_single_pass_cells']}",
        f"- **Metric**: micro-average F1 @ {result['buffer_metres']} m; "
        f"MCC reported (tile-level, buffer-agnostic)",
        f"- **Test**: round-robin tile-swap permutation, "
        f"{result['n_permutations']:,} perms, seed {result['seed']}, two-sided; "
        f"**BH-FDR** q = {result['fdr_q']}",
        f"- **Tiers**: {len(result['tiers'])}; **Tier 1** = "
        f"{', '.join('`' + r + '`' for r in result['tie_set'])}",
        "",
        "| rank | cell | kind | think | mod | vote | F1@20m | MCC | tier |",
        "|---:|---|---|---|---|---|---:|---:|---:|",
    ]
    for i, c in enumerate(ordered, 1):
        mcc = f"{c['mcc']:.3f}" if c["mcc"] is not None else "—"
        lines.append(
            f"| {i} | `{c['label']}` | {c['kind']} | {c.get('thinking') or '—'} | "
            f"{c.get('modality') or '—'} | {c.get('vote') or '—'} | "
            f"{c['eval_f1']:.3f} | {mcc} | {tier_of[c['ref']]} |"
        )
    lines += ["", "## Headline contrasts", "",
              "| claim | F1 a | F1 b | ΔF1 | p | BH-p | sig |",
              "|---|---:|---:|---:|---:|---:|:--:|"]
    for ct in result["headline_contrasts"]:
        sig = "**yes**" if ct["significant"] else "no"
        lines.append(
            f"| {ct['claim']} | {ct['f1_a']:.3f} | {ct['f1_b']:.3f} | "
            f"{ct['f1_diff']:+.3f} | {ct['p_value']:.4f} | "
            f"{ct['bh_adjusted_p']:.4f} | {sig} |"
        )
    md_path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
