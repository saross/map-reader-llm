#!/usr/bin/env python3
# ============================================================================
# n1_baseline_leaderboard_tiering.py
# ----------------------------------------------------------------------------
# Round-robin paired permutation test, Benjamini-Hochberg False Discovery
# Rate (FDR) correction, and greedy-clique tiering for the N=1 single-pass
# baseline leaderboard (18 cells) at the preregistered headline 20 m buffer.
#
# WHAT THIS PRODUCES
# ------------------
# The statistical ``tie_set`` for the ``n1-baseline-matrix-384`` analysis:
# the set of single-pass conditions that are statistically indistinguishable
# from the F1@20 m leader (the leader's clique, ``tiers[0]``). This lifts the
# analyses-manifest leaderboard row from a stub to a finding. See
# ``docs/methodology/n1-baseline-matrix.md`` and
# ``planning/leaderboard-construction-plan.md``.
#
# REPLICATE-MEAN HANDLING (the one bespoke piece)
# -----------------------------------------------
# Each baseline cell's headline metric is the MEAN over its replicate single
# passes (1, 3, 5, 10, or 30 of them). The project's canonical permutation
# test, ``scripts/pairwise_permutation_test.py::run_permutation_test``,
# compares two SINGLE detection sets via an INTEGER per-tile TP/FP/FN
# tile-swap. A single-pass baseline cell is not a single detection set; it is
# an expectation over replicates. So here each cell is summarised as its
# pass-AVERAGED (float) per-tile TP/FP/FN — exactly the statistic the
# bootstrap confidence intervals in each ``evaluation.json`` already use — and
# the permutation tests the quantity the leaderboard actually ranks: the
# expected single-pass micro-average F1.
#
# The tile-swap algorithm, micro-average F1 statistic, probability-0.5 swap,
# ``numpy.random.default_rng(seed)`` draw, and two-sided p-value are otherwise
# IDENTICAL to ``run_permutation_test`` (protocol erratum E45 motivates the
# micro-average choice). The only changes are: per-tile arrays are float
# (pass means) rather than int, and the ``int()`` casts on the aggregate sums
# are dropped. Empty tiles (TP+FP+FN == 0) are inert under label-swapping, so
# this test is robust to the ``sparse_cross_grid`` flag that makes the
# bootstrap F1 CIs unreliable for the two precise Pro-text leaders.
#
# WHY NOT THE OTHER REPLICATE OPTIONS
# -----------------------------------
# - Picking one representative pass discards the replicate information we have
#   and is arbitrary.
# - Pooling/union-ing passes tests a DIFFERENT quantity (a 30-pass union has
#   far higher recall and lower precision than a single pass).
# - A two-sample test on the distribution of per-pass F1 is undefined for the
#   1-pass cells (which include the F1 leader, pro-text-medium-t-0-0).
# Only the pass-averaged per-tile route handles 1-pass and 30-pass cells
# uniformly, which is why it is used.
#
# TIERING
# -------
# BH-FDR is applied to the C(18, 2) = 153 raw p-values via
# ``scripts/apply_fdr_correction.py::apply_bh_correction`` (q = 0.05, the
# project default). Conditions are then sorted by their board F1@20 m
# (descending) and grouped by the same greedy clique algorithm as
# ``build_tiered_leaderboard.py::apply_fdr_and_tier``: a condition joins the
# current tier iff it is statistically indistinguishable (NOT BH-significant)
# from ALL current members. ``tie_set`` is the first tier.
#
# COMPUTE LOCATION
# ----------------
# This is a pairwise permutation sweep — explicitly "computationally
# intensive" per the project CLAUDE.md. Run on zbook (or sapphire when free),
# never on amd-tower.
#
# Usage:
#     python scripts/n1_baseline_leaderboard_tiering.py \
#         --output-dir results/paper-eval/n1/384px-14buf-mcc/tiering
#
# Author: Shawn Ross & Claude (Anthropic)
# Created: 2026-06-03
# Licence: Apache 2.0
# ============================================================================

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from apply_fdr_correction import apply_bh_correction  # noqa: E402
from lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402
from pairwise_permutation_test import assign_source_tiles  # noqa: E402

# --- Project-standard constants (kept identical to the canonical pipeline) ---
TARGET_CRS = "EPSG:32635"  # UTM Zone 35N (Bulgaria) — metric matching CRS
HEADLINE_BUFFER_M = 20  # preregistered headline buffer
N_PERMUTATIONS = 10_000  # matches run_permutation_test + the bootstrap n
SEED = 42  # project-standard reproducibility seed
FDR_Q = 0.05  # build_tiered_leaderboard DEFAULT_FDR_Q

DEFAULT_CONDITIONS = BASE_DIR / "results" / "run-conditions.json"
DEFAULT_ANALYSES = BASE_DIR / "results" / "run-analyses.json"
DEFAULT_GT = BASE_DIR / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
DEFAULT_BOUNDS = (
    BASE_DIR / "inputs" / "vectors" / "bounds" / "384" / "full_evaluation_bounds.geojson"
)
DEFAULT_OUTPUT = BASE_DIR / "results" / "paper-eval" / "n1" / "384px-14buf-mcc" / "tiering"

# Board membership is the SINGLE SOURCE OF TRUTH in run-analyses.json: the
# ``conditions_compared`` list of this analysis. Reading it here (rather than
# re-deriving "all baseline-* cells in runs X/Y/Z") means edits to the board
# — e.g. the E57 replace of the four Flash-misdispatched n1-outstanding "Pro"
# cells with the genuine-Pro re-run (n1-pro-rerun-384) — take effect with no
# change to this script. Each ref ``<run>::<label>`` is resolved against
# run-conditions.json for its detections dir and evaluation.json.
ANALYSIS_ID = "n1-baseline-matrix-384"

# Candidate replicate-pass globs, UNION-ed (not first-non-empty). The original
# baseline pools carry batch-style ``detections_<pool>_runNN.geojson``
# (underscore); the genuine-Pro realtime(+flex) passes carry
# ``detections-<prompt>-3.1-pro-<date>.geojson`` (hyphen). Most pools are one
# style, but the two pv-diag MEDIUM-T=0.0 cells are MIXED after the n=3 top-up
# (Session 98): batch run_1 + realtime run_2/run_3. A filename is either
# ``detections_…`` or ``detections-…`` (never both), so unioning the two
# patterns and de-duplicating collects every replicate without double-counting.
PASS_GLOBS = ("*/detections_*.geojson", "*/detections-*.geojson")


def git_commit() -> str:
    """Return the short HEAD commit hash, or ``"unknown"`` on failure."""
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], cwd=BASE_DIR
            )
            .decode()
            .strip()
        )
    except Exception:  # pragma: no cover - provenance best-effort only
        return "unknown"


def micro_f1(tp: float, fp: float, fn: float) -> float:
    """Micro-average F1 from aggregate counts (mirrors ``_compute_f1``).

    Accepts float counts (pass-averaged per-tile sums). Returns 0.0 for the
    degenerate ``tp == 0`` and zero-denominator cases, identically to
    ``pairwise_permutation_test._compute_f1``.

    Args:
        tp: Aggregate true positives (may be a float pass-mean sum).
        fp: Aggregate false positives.
        fn: Aggregate false negatives.

    Returns:
        The micro-average F1 score in ``[0, 1]``.
    """
    if tp == 0:
        return 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def load_baseline_cells(conditions_path: Path, analyses_path: Path) -> list[dict]:
    """Load the N=1 baseline cells named by the analysis's ``conditions_compared``.

    Board membership is read from run-analyses.json (the single source of truth);
    each ``<run>::<label>`` ref is then resolved against run-conditions.json for
    its detection pass directory and evaluation.json.

    Each returned dict has: ``ref`` (``<run>::<label>``), ``run``, ``label``,
    ``detections`` (the pass directory the cell aggregates), and ``eval_path``
    (the cell's evaluation.json, the source of the board F1@20 m).

    Args:
        conditions_path: Path to results/run-conditions.json.
        analyses_path: Path to results/run-analyses.json.

    Returns:
        List of cell dicts, in ``conditions_compared`` order.

    Raises:
        KeyError / StopIteration: if the analysis is absent, or a ref does not
            resolve to a condition in run-conditions.json (a board/sidecar
            inconsistency that should fail loudly rather than silently drop a cell).
    """
    analyses = json.loads(analyses_path.read_text())["analyses"]
    board = next(a for a in analyses if a["analysis_id"] == ANALYSIS_ID)
    refs: list[str] = board["conditions_compared"]

    decomposition = json.loads(conditions_path.read_text())["decomposition"]
    cells: list[dict] = []
    for ref in refs:
        run, label = ref.split("::", 1)
        cond = next(
            c for c in decomposition[run]["conditions"] if c["label"] == label
        )
        cells.append(
            {
                "ref": ref,
                "run": run,
                "label": label,
                "detections": cond["detections"],
                "eval_path": cond["eval_path"],
            }
        )
    return cells


def board_f1_at_20m(eval_path: Path) -> float:
    """Read a cell's headline board F1@20 m (mean over replicate passes).

    This is the metric the leaderboard ranks by, and the value the
    permutation's micro-F1-of-the-mean is cross-checked against.

    Args:
        eval_path: Path to the cell's evaluation.json.

    Returns:
        The F1 at the 20 m buffer from ``summary.buffers``.
    """
    summary = json.loads(eval_path.read_text())["summary"]
    buf = next(b for b in summary["buffers"] if b["buffer_metres"] == HEADLINE_BUFFER_M)
    return float(buf["f1"])


def pass_averaged_per_tile(
    detections_dir: Path,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_order: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """Compute a cell's pass-averaged per-tile TP/FP/FN arrays.

    Globs the cell's replicate passes, computes per-tile TP/FP/FN for each
    pass via the canonical ``compute_per_tile_tp_fp_fn`` (Hungarian matching
    per map, 20 m), aligns each pass to the fixed ``tile_order``, and returns
    the per-tile MEAN across passes (float arrays). This is the expected
    single-pass per-tile statistic the leaderboard cell represents.

    Args:
        detections_dir: The cell's ``detections`` directory (holds run_N/).
        gdf_ref: Ground-truth references (projected to TARGET_CRS).
        gdf_bounds: Evaluation tile boundaries (projected to TARGET_CRS).
        tile_order: Fixed list of tile_name values defining array positions.

    Returns:
        Tuple ``(tp_mean, fp_mean, fn_mean, n_passes)`` where the three
        arrays are float, length ``len(tile_order)``.

    Raises:
        FileNotFoundError: If no replicate passes match the glob.
    """
    pool_dir = BASE_DIR / detections_dir
    pass_files = sorted({f for g in PASS_GLOBS for f in pool_dir.glob(g)})
    if not pass_files:
        raise FileNotFoundError(
            f"No replicate passes under {detections_dir} matching any of {PASS_GLOBS}"
        )

    tile_index = {name: i for i, name in enumerate(tile_order)}
    n_tiles = len(tile_order)
    tp_sum = np.zeros(n_tiles, dtype=float)
    fp_sum = np.zeros(n_tiles, dtype=float)
    fn_sum = np.zeros(n_tiles, dtype=float)

    for pass_file in pass_files:
        gdf_det = gpd.read_file(pass_file)
        if gdf_det.crs is None:
            gdf_det = gdf_det.set_crs("EPSG:4326")
        gdf_det = gdf_det.to_crs(TARGET_CRS)
        gdf_det = assign_source_tiles(gdf_det, gdf_bounds)
        tile_metrics = compute_per_tile_tp_fp_fn(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=HEADLINE_BUFFER_M
        )
        # Align this pass's per-tile counts into the fixed tile order.
        for _, row in tile_metrics.iterrows():
            idx = tile_index.get(row["tile_name"])
            if idx is None:
                continue
            tp_sum[idx] += float(row["tp"])
            fp_sum[idx] += float(row["fp"])
            fn_sum[idx] += float(row["fn"])

    n_passes = len(pass_files)
    return tp_sum / n_passes, fp_sum / n_passes, fn_sum / n_passes, n_passes


def permutation_test_float(
    tp_a: np.ndarray,
    fp_a: np.ndarray,
    fn_a: np.ndarray,
    tp_b: np.ndarray,
    fp_b: np.ndarray,
    fn_b: np.ndarray,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict:
    """Float tile-swap paired permutation test on pass-averaged per-tile counts.

    Mirrors ``pairwise_permutation_test.run_permutation_test`` exactly — the
    micro-average F1 statistic, the probability-0.5 per-tile label swap, the
    ``numpy.random.default_rng(seed)`` stream, and the two-sided p-value — but
    operates on float (pass-mean) per-tile arrays rather than integer single-
    pass counts. The arrays are vectorised across the permutation batch for
    speed (153 pairs x 10k perms).

    Args:
        tp_a, fp_a, fn_a: Condition A pass-averaged per-tile counts (float).
        tp_b, fp_b, fn_b: Condition B pass-averaged per-tile counts (float).
        n_permutations: Number of permutation iterations.
        seed: Random seed for reproducibility.

    Returns:
        Dict with ``f1_a``, ``f1_b``, ``observed_diff``, ``p_value``,
        ``n_tiles``, and null-distribution summary statistics.
    """
    f1_a = micro_f1(tp_a.sum(), fp_a.sum(), fn_a.sum())
    f1_b = micro_f1(tp_b.sum(), fp_b.sum(), fn_b.sum())
    observed_diff = f1_a - f1_b

    n_tiles = len(tp_a)
    rng = np.random.default_rng(seed)
    # Vectorised tile-swap: (n_permutations x n_tiles) boolean swap mask.
    swap = rng.random((n_permutations, n_tiles)) < 0.5

    # Per-permutation aggregate sums after swapping each tile's A/B counts.
    def _swapped_sums(arr_a: np.ndarray, arr_b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Return (sum_a, sum_b) per permutation under the swap mask."""
        perm_a = np.where(swap, arr_b, arr_a)  # condition A after swap
        perm_b = np.where(swap, arr_a, arr_b)  # condition B after swap
        return perm_a.sum(axis=1), perm_b.sum(axis=1)

    tp_a_sum, tp_b_sum = _swapped_sums(tp_a, tp_b)
    fp_a_sum, fp_b_sum = _swapped_sums(fp_a, fp_b)
    fn_a_sum, fn_b_sum = _swapped_sums(fn_a, fn_b)

    # Vectorised micro-F1 with safe division (matches micro_f1 edge cases).
    def _micro_f1_vec(tp: np.ndarray, fp: np.ndarray, fn: np.ndarray) -> np.ndarray:
        denom_p = tp + fp
        denom_r = tp + fn
        precision = np.divide(tp, denom_p, out=np.zeros_like(tp), where=denom_p > 0)
        recall = np.divide(tp, denom_r, out=np.zeros_like(tp), where=denom_r > 0)
        denom_f = precision + recall
        f1 = np.divide(
            2 * precision * recall, denom_f, out=np.zeros_like(tp), where=denom_f > 0
        )
        f1[tp == 0] = 0.0  # explicit tp==0 -> 0.0, as in micro_f1
        return f1

    null_diffs = _micro_f1_vec(tp_a_sum, fp_a_sum, fn_a_sum) - _micro_f1_vec(
        tp_b_sum, fp_b_sum, fn_b_sum
    )
    p_value = float(np.mean(np.abs(null_diffs) >= abs(observed_diff)))

    return {
        "f1_a": round(f1_a, 6),
        "f1_b": round(f1_b, 6),
        "observed_diff": round(observed_diff, 6),
        "p_value": round(p_value, 4),
        "n_permutations": n_permutations,
        "n_tiles": n_tiles,
        "null_mean": round(float(np.mean(null_diffs)), 6),
        "null_std": round(float(np.std(null_diffs)), 6),
    }


def greedy_clique_tiers(
    ordered_refs: list[str], significant: dict[frozenset, bool]
) -> list[list[str]]:
    """Group conditions into tiers by greedy clique (mirrors apply_fdr_and_tier).

    Conditions are processed in the given (board-F1-descending) order. Each
    joins the current tier iff it is statistically indistinguishable (NOT
    BH-significant) from ALL current tier members; otherwise a new tier opens.

    Args:
        ordered_refs: Condition refs sorted by board F1@20 m, descending.
        significant: Map from ``frozenset({ref_a, ref_b})`` to whether that
            pair is BH-significant.

    Returns:
        List of tiers, each a list of condition refs. ``tiers[0]`` is the
        leader's clique (the tie_set).
    """
    tiers: list[list[str]] = []
    current: list[str] = []
    for ref in ordered_refs:
        if not current:
            current = [ref]
            continue
        indistinguishable = all(
            not significant.get(frozenset({ref, member}), False) for member in current
        )
        if indistinguishable:
            current.append(ref)
        else:
            tiers.append(current)
            current = [ref]
    if current:
        tiers.append(current)
    return tiers


def main() -> int:
    """CLI entry point: run the round-robin, tier, and write results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--conditions", type=Path, default=DEFAULT_CONDITIONS)
    parser.add_argument("--analyses", type=Path, default=DEFAULT_ANALYSES)
    parser.add_argument("--ground-truth", type=Path, default=DEFAULT_GT)
    parser.add_argument("--bounds", type=Path, default=DEFAULT_BOUNDS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--n-permutations", type=int, default=N_PERMUTATIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument(
        "--limit-cells",
        type=int,
        default=None,
        help="Dev-only: restrict to the first N cells for a quick dry-run.",
    )
    args = parser.parse_args()

    print("Loading references and bounds ...", flush=True)
    gdf_ref = gpd.read_file(args.ground_truth).to_crs(TARGET_CRS)
    gdf_bounds = gpd.read_file(args.bounds).to_crs(TARGET_CRS)
    tile_order = list(gdf_bounds["tile_name"].unique())
    print(f"  {len(tile_order)} evaluation tiles", flush=True)

    cells = load_baseline_cells(args.conditions, args.analyses)
    if args.limit_cells is not None:
        cells = cells[: args.limit_cells]
    print(f"Loaded {len(cells)} baseline cells", flush=True)

    # --- Per-cell pass-averaged per-tile statistics + board F1 cross-check ---
    for cell in cells:
        tp, fp, fn, n_passes = pass_averaged_per_tile(
            Path(cell["detections"]), gdf_ref, gdf_bounds, tile_order
        )
        cell["tp"], cell["fp"], cell["fn"] = tp, fp, fn
        cell["n_passes"] = n_passes
        cell["observed_micro_f1"] = round(micro_f1(tp.sum(), fp.sum(), fn.sum()), 6)
        cell["board_f1"] = round(board_f1_at_20m(BASE_DIR / cell["eval_path"]), 6)
        cell["f1_gap"] = round(cell["observed_micro_f1"] - cell["board_f1"], 6)
        print(
            f"  {cell['label']:42s} passes={n_passes:2d} "
            f"micro-F1-of-mean={cell['observed_micro_f1']:.4f} "
            f"board-F1={cell['board_f1']:.4f} gap={cell['f1_gap']:+.4f}",
            flush=True,
        )

    # --- Round-robin C(N, 2) float tile-swap permutation tests ---
    pairs = list(combinations(range(len(cells)), 2))
    print(f"Running {len(pairs)} pairwise permutation tests "
          f"({args.n_permutations} perms each) ...", flush=True)
    pairwise: list[dict] = []
    for a, b in pairs:
        ca, cb = cells[a], cells[b]
        res = permutation_test_float(
            ca["tp"], ca["fp"], ca["fn"], cb["tp"], cb["fp"], cb["fn"],
            n_permutations=args.n_permutations, seed=args.seed,
        )
        pairwise.append({"ref_a": ca["ref"], "ref_b": cb["ref"], **res})

    # --- BH-FDR correction (q = 0.05) ---
    raw_p = [r["p_value"] for r in pairwise]
    adjusted = apply_bh_correction(raw_p, q=FDR_Q)
    significant: dict[frozenset, bool] = {}
    for r, adj in zip(pairwise, adjusted):
        r["bh_adjusted_p"] = round(adj, 6)
        r["significant"] = bool(adj < FDR_Q)
        significant[frozenset({r["ref_a"], r["ref_b"]})] = r["significant"]

    # --- Sort by board F1 (the ranked headline metric) and tier ---
    ordered = sorted(cells, key=lambda c: c["board_f1"], reverse=True)
    ordered_refs = [c["ref"] for c in ordered]
    tiers = greedy_clique_tiers(ordered_refs, significant)
    tie_set = tiers[0]

    n_sig = sum(1 for r in pairwise if r["significant"])
    print(
        f"FDR: {n_sig}/{len(pairwise)} pairs significant at q={FDR_Q} "
        f"-> {len(tiers)} tiers; tie_set (Tier 1) = {len(tie_set)} condition(s)",
        flush=True,
    )

    # --- Write result JSON + Markdown ---
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "analysis_id": "n1-baseline-matrix-384",
        "metric": "f1",
        "buffer_metres": HEADLINE_BUFFER_M,
        "n_permutations": args.n_permutations,
        "seed": args.seed,
        "fdr_q": FDR_Q,
        "replicate_handling": "pass-averaged per-tile (expected single-pass micro-F1)",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "ranking": [
            {
                "rank": i + 1,
                "ref": c["ref"],
                "label": c["label"],
                "n_passes": c["n_passes"],
                "board_f1": c["board_f1"],
                "observed_micro_f1": c["observed_micro_f1"],
                "f1_gap": c["f1_gap"],
                "tier": next(t for t, members in enumerate(tiers, 1) if c["ref"] in members),
            }
            for i, c in enumerate(ordered)
        ],
        "tiers": [{"tier": i + 1, "members": members} for i, members in enumerate(tiers)],
        "tie_set": tie_set,
        "pairwise": pairwise,
    }
    json_path = args.output_dir / "tiering_20m.json"
    json_path.write_text(json.dumps(result, indent=2))
    print(f"Wrote {json_path}", flush=True)

    md_lines = [
        "# N=1 baseline leaderboard — statistical tiering (20 m)",
        "",
        f"- **Metric**: micro-average F1 @ {HEADLINE_BUFFER_M} m "
        "(pass-averaged per-tile; expected single-pass)",
        f"- **Permutations**: {args.n_permutations:,} per pair, seed {args.seed}, "
        f"two-sided; **BH-FDR** q = {FDR_Q}",
        f"- **Pairs**: {len(pairwise)} ({n_sig} significant) -> **{len(tiers)} tiers**",
        f"- **Tie set (Tier 1)**: {', '.join(tie_set)}",
        "",
        "| rank | condition | passes | board F1@20m | micro-F1-of-mean | gap | tier |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for i, c in enumerate(ordered, 1):
        tier = next(t for t, members in enumerate(tiers, 1) if c["ref"] in members)
        md_lines.append(
            f"| {i} | `{c['label']}` | {c['n_passes']} | {c['board_f1']:.3f} | "
            f"{c['observed_micro_f1']:.3f} | {c['f1_gap']:+.3f} | {tier} |"
        )
    md_path = args.output_dir / "tiering_20m.md"
    md_path.write_text("\n".join(md_lines) + "\n")
    print(f"Wrote {md_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
