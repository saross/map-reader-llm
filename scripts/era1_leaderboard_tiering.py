#!/usr/bin/env python3
# ============================================================================
# era1_leaderboard_tiering.py
# ----------------------------------------------------------------------------
# A GENERIC statistically-tiered leaderboard over an arbitrary set of decomposed
# conditions, using the project-canonical round-robin tile-swap micro-F1
# permutation + Benjamini-Hochberg False Discovery Rate (FDR) + greedy-clique
# tiering at the preregistered 20 m headline buffer.
#
# WHY THIS EXISTS
# ---------------
# The Gold-Standard 4-map runs (Era 1, 512 px, 340 tiles, curator ground truth)
# need two tiered boards on their own terms (see
# ``planning/era1-leaderboard-plan-2026-06-08.md``):
#   * Stage A -- the Era-1 SINGLE-PASS baseline board (the 36 phase2a-e cells),
#     the Era-1 analogue of ``n1-baseline-matrix-384``;
#   * Stage B -- the DEFINITIVE Era-1 leaderboard (36 single-pass + 42 consensus
#     cells), the Era-1 analogue of ``diversity-dividend-384``.
# Both are the SAME computation over a different cell set, so this one harness
# produces both: it reads the board membership from a named analysis's
# ``conditions_compared`` list (the single source of truth) and tiers it.
#
# RELATIONSHIP TO THE EXISTING TWO SCRIPTS
# ----------------------------------------
# This module imports the canonical statistical machinery VERBATIM from
# ``n1_baseline_leaderboard_tiering`` -- ``permutation_test_float`` (the float
# tile-swap micro-F1 test), ``greedy_clique_tiers``, ``micro_f1``,
# ``board_f1_at_20m``, ``git_commit`` and the project-standard constants -- so
# the test is byte-for-byte identical to the one the 384 px single-pass board
# and the diversity-dividend board already passed. The ONLY thing this script
# adds is a UNIFIED per-tile loader that handles all three Era-1 cell shapes
# from one code path (see ``cell_per_tile`` below). It supersedes neither
# existing script; it generalises them so a board need not be hand-curated into
# "champions vs baseline" with bespoke named contrasts.
#
# THE UNIFIED PER-TILE LOADER (the one new piece)
# -----------------------------------------------
# Every Era-1 condition records, in its own ``evaluation.json`` under
# ``_metadata.cli_args``, EXACTLY how it was scored. This harness re-reads that
# record and reproduces it, so a board cell's per-tile TP/FP/FN are computed the
# same way ``evaluate_detections.py`` computed the published metric:
#   * ``detections`` set (a single aggregated geojson, or a list unioned into
#     one set) -> INTEGER per-tile counts of that one set. This is a consensus
#     single-set cell (phase3a / -high / -replication) or the PV cell.
#   * ``detections_dir`` + ``glob`` -> the per-tile MEAN over the matched files
#     (float). This is a replicate-mean cell: a single-pass baseline (K runs,
#     resolved through ``lib_detection_paths`` so BOTH per-pass naming
#     conventions are expanded) or a phase3c diversity pool (5 replications,
#     ``replication_*/consensus_t{vote}.geojson``, replayed verbatim).
# Both yield float arrays on one fixed tile order, so they drop unchanged into
# the shared ``permutation_test_float``. A single-pass board cell is an
# EXPECTATION over replicate passes (pass-averaged per-tile); a consensus
# single-set cell is ONE set (integer per-tile); a phase3c cell is a
# replicate-mean of consensus sets -- all three are "the F1 the leaderboard
# ranks", so the comparison is like-for-like on the quantity each cell is.
#
# METRIC
# ------
# Tiering ranks F1 @ 20 m (the preregistered headline). MCC (buffer-agnostic
# tile-level discrimination, ``summary.tile_classification.mcc.point``) is
# carried as a reported column per the standing report-MCC-with-F1 preference;
# it is NOT the permutation statistic.
#
# COMPUTE LOCATION
# ----------------
# A round-robin permutation sweep -- "computationally intensive" per the project
# CLAUDE.md. Run on zbook or sapphire, NEVER on amd-tower.
#
# Usage (Stage A -- single-pass board):
#     python scripts/era1_leaderboard_tiering.py \
#         --analysis-id era1-single-pass-baseline-matrix \
#         --output-dir results/paper-eval/n1/512px-14buf-mcc/tiering
#
# Usage (Stage B -- definitive board):
#     python scripts/era1_leaderboard_tiering.py \
#         --analysis-id era1-leaderboard \
#         --output-dir results/era1-leaderboard
#
# Author: Shawn Ross & Claude (Anthropic)
# Created: 2026-06-08
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
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

# Canonical machinery, imported VERBATIM so the test matches the 384 px boards.
from n1_baseline_leaderboard_tiering import (  # noqa: E402
    FDR_Q,
    HEADLINE_BUFFER_M,
    N_PERMUTATIONS,
    SEED,
    TARGET_CRS,
    board_f1_at_20m,
    git_commit,
    greedy_clique_tiers,
    micro_f1,
    permutation_test_float,
)

from apply_fdr_correction import apply_bh_correction  # noqa: E402
from lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402
from lib_detection_paths import resolve_pool_passes  # noqa: E402
from pairwise_permutation_test import assign_source_tiles  # noqa: E402

DEFAULT_CONDITIONS = BASE_DIR / "results" / "run-conditions.json"
DEFAULT_ANALYSES = BASE_DIR / "results" / "run-analyses.json"


def read_tile_mcc(eval_path: Path) -> float | None:
    """Read a cell's buffer-agnostic tile-level MCC point estimate.

    The MCC lives in ``summary.tile_classification.mcc.point`` (NOT in the
    per-buffer block, where ``mcc`` is always null). This is the same field the
    n1 and diversity-dividend boards report as their secondary metric.

    Args:
        eval_path: Path to the cell's evaluation.json.

    Returns:
        The tile-level MCC point estimate, or ``None`` if absent.
    """
    summary = json.loads(eval_path.read_text())["summary"]
    # `tile_classification.mcc` has TWO committed shapes. evaluate_detections.py
    # writes a block ({point, mean, ci_lower, ci_upper, ...}); the Track-2
    # adapters write a bare float. Reading only the block shape raises on every
    # adapter-written cell, which is one of the reasons the 55-map boards were
    # unloadable. Both are accepted here; a null stays null (erratum E81).
    mcc = summary.get("tile_classification", {}).get("mcc")
    if isinstance(mcc, dict):
        return mcc.get("point")
    return mcc


def load_board_refs(analyses_path: Path, analysis_id: str) -> list[str]:
    """Return the ``conditions_compared`` refs for the named analysis.

    Board membership is the single source of truth in run-analyses.json: edits
    to the board take effect with no change to this script.

    Args:
        analyses_path: Path to results/run-analyses.json.
        analysis_id: The analysis whose conditions_compared defines the board.

    Returns:
        The list of ``<run>::<label>`` refs, in authored order.

    Raises:
        StopIteration: if the analysis_id is absent (fail loud, not silent).
    """
    analyses = json.loads(analyses_path.read_text())["analyses"]
    board = next(a for a in analyses if a["analysis_id"] == analysis_id)
    return list(board["conditions_compared"])


def resolve_condition(conditions_path: Path, ref: str) -> dict:
    """Resolve a ``<run>::<label>`` ref to its decomposed condition dict.

    Args:
        conditions_path: Path to results/run-conditions.json.
        ref: A ``<run>::<label>`` board reference.

    Returns:
        The condition dict (with ``detections``, ``eval_path``, ``architecture``).

    Raises:
        StopIteration: if the ref does not resolve (a board/sidecar
            inconsistency that should fail loudly rather than drop a cell).
    """
    decomposition = json.loads(conditions_path.read_text())["decomposition"]
    run, label = ref.split("::", 1)
    cond = next(c for c in decomposition[run]["conditions"] if c["label"] == label)
    return cond


def _read_detections_gdf(path: Path) -> gpd.GeoDataFrame:
    """Read one detection geojson, normalising its CRS to ``TARGET_CRS``.

    Mirrors the CRS handling of the existing harnesses: a file with no declared
    CRS is assumed WGS84 (EPSG:4326, RFC 7946), then everything is reprojected
    to the metric ``TARGET_CRS`` the scorer matches in. (See the Session-106
    CRS contract fix, Obs 350: ``apply_threshold`` already emits 4326, so the
    on-disk consensus geojsons declare 4326 and this reprojection reproduces the
    eval exactly.)

    Args:
        path: Absolute path to the detection geojson.

    Returns:
        The detections GeoDataFrame in ``TARGET_CRS``.
    """
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    return gdf.to_crs(TARGET_CRS)


def _per_tile_one_set(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_order: list[str],
    buffer_metres: int = HEADLINE_BUFFER_M,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per-tile TP/FP/FN for ONE detection set, aligned to ``tile_order``.

    Wraps the canonical ``compute_per_tile_tp_fp_fn`` (Hungarian matching per
    map at the headline buffer) and aligns its per-tile output into fixed-order
    float arrays.

    Args:
        gdf_det: One detection set, already in ``TARGET_CRS`` with source tiles
            assigned.
        gdf_ref: Ground-truth references in ``TARGET_CRS``.
        gdf_bounds: Evaluation tile boundaries in ``TARGET_CRS``.
        tile_order: Fixed list of ``tile_name`` values defining array positions.

    Returns:
        Tuple ``(tp, fp, fn)`` of float arrays, length ``len(tile_order)``.
    """
    tile_metrics = compute_per_tile_tp_fp_fn(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_metres
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


def cell_per_tile(
    cli_args: dict,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_order: list[str],
    buffer_metres: int = HEADLINE_BUFFER_M,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """Reproduce a cell's per-tile TP/FP/FN exactly as its eval scored it.

    Dispatches on the cell's recorded ``_metadata.cli_args``:

    * ``detections`` set (a single geojson, or a list unioned into one set) ->
      INTEGER per-tile counts of that one set (``n_passes = 1``). This is a
      consensus single-set cell (phase3a / -high / -replication) or the PV cell.
    * ``detections_dir`` + ``glob`` -> the per-tile MEAN over the matched files
      (float). This is a replicate-mean cell: a single-pass baseline (K runs) or
      a phase3c diversity pool (5 replications). ``n_passes`` = file count.
      A pass-file glob is resolved through
      :func:`scripts.lib_detection_paths.resolve_pool_passes` rather than
      replayed verbatim, because the recorded pattern matches only the
      batch-written convention and would drop any real-time pass (defect D6);
      a glob naming a non-pass artefact (a phase3c consensus set) is replayed
      as recorded.

    Args:
        cli_args: The cell's ``evaluation.json[_metadata][cli_args]``.
        gdf_ref: Ground-truth references in ``TARGET_CRS``.
        gdf_bounds: Evaluation tile boundaries in ``TARGET_CRS``.
        tile_order: Fixed list of ``tile_name`` values.

    Returns:
        Tuple ``(tp, fp, fn, n_passes)`` -- float arrays of length
        ``len(tile_order)`` plus the replicate count.

    Raises:
        FileNotFoundError: if no detection files resolve.
        ValueError: if the cli_args declare neither a detections set nor a
            detections_dir (an un-scoreable cell that must fail loud).
    """
    det = cli_args.get("detections")
    det_dir = cli_args.get("detections_dir")
    glob = cli_args.get("glob")

    if det:
        # Single aggregated set. A list is the evaluate_detections "union these
        # files into one set" form; in Era-1 it is always exactly one geojson.
        files = det if isinstance(det, list) else [det]
        paths = [BASE_DIR / f for f in files]
        missing = [p for p in paths if not p.exists()]
        if missing:
            raise FileNotFoundError(f"detections set file(s) not found: {missing}")
        gdf_parts = [_read_detections_gdf(p) for p in paths]
        gdf_det = (
            gdf_parts[0]
            if len(gdf_parts) == 1
            else gpd.GeoDataFrame(
                pd.concat(gdf_parts, ignore_index=True), crs=TARGET_CRS
            )
        )
        gdf_det = assign_source_tiles(gdf_det, gdf_bounds)
        tp, fp, fn = _per_tile_one_set(gdf_det, gdf_ref, gdf_bounds, tile_order,
                                       buffer_metres)
        return tp, fp, fn, 1

    if det_dir:
        # Replicate-mean over the matched files (single-pass K runs, or phase3c
        # 5 replications). Pass-averaged per-tile -- the expected per-tile count.
        pool_dir = BASE_DIR / det_dir
        if glob and "detections" not in glob:
            # Non-pass artefact (phase3c ``replication_*/consensus_t*``) —
            # replay the recorded pattern verbatim.
            pass_files = sorted(pool_dir.glob(glob))
        else:
            pass_files = resolve_pool_passes(pool_dir, allow_multiple=True)
        if not pass_files:
            raise FileNotFoundError(
                f"No replicate passes under {det_dir} matching glob {glob!r}"
            )
        n_tiles = len(tile_order)
        tp_sum = np.zeros(n_tiles, dtype=float)
        fp_sum = np.zeros(n_tiles, dtype=float)
        fn_sum = np.zeros(n_tiles, dtype=float)
        for pass_file in pass_files:
            gdf_det = assign_source_tiles(_read_detections_gdf(pass_file), gdf_bounds)
            tp_i, fp_i, fn_i = _per_tile_one_set(
                gdf_det, gdf_ref, gdf_bounds, tile_order, buffer_metres
            )
            tp_sum += tp_i
            fp_sum += fp_i
            fn_sum += fn_i
        n = len(pass_files)
        return tp_sum / n, fp_sum / n, fn_sum / n, n

    raise ValueError(
        "cli_args declare neither 'detections' nor 'detections_dir' — "
        "cannot reproduce this cell's per-tile counts"
    )


def load_cells(
    conditions_path: Path,
    analyses_path: Path,
    analysis_id: str,
    bounds_override: Path | None,
    gt_override: Path | None,
    buffer_metres: int = HEADLINE_BUFFER_M,
) -> tuple[list[dict], gpd.GeoDataFrame, gpd.GeoDataFrame, list[str]]:
    """Load every board cell with per-tile stats, F1 and MCC.

    Ground truth and bounds are derived from the cells' own evals (asserting
    every cell shares the same pair) unless overridden on the CLI. This keeps
    the analysis self-describing: the board carries its evaluation scope with
    it, and a board for a different era "just works" by pointing at a different
    analysis.

    Args:
        conditions_path: results/run-conditions.json.
        analyses_path: results/run-analyses.json.
        analysis_id: The analysis whose conditions_compared defines the board.
        bounds_override: Optional explicit bounds path (wins over the evals').
        gt_override: Optional explicit ground-truth path (wins over the evals').

    Returns:
        ``(cells, gdf_ref, gdf_bounds, tile_order)``.

    Raises:
        ValueError: if the cells disagree on ground truth / bounds and no
            override is supplied (a silent-scope-mix guard).
    """
    refs = load_board_refs(analyses_path, analysis_id)

    # First pass: resolve every cell's eval, collect (gt, bounds) declarations.
    resolved: list[dict] = []
    gts: set[str] = set()
    boundss: set[str] = set()
    for ref in refs:
        cond = resolve_condition(conditions_path, ref)
        eval_path = BASE_DIR / cond["eval_path"]
        meta = json.loads(eval_path.read_text())["_metadata"]
        # Adapter-written evaluations (the Track-2 55-map cells) carry no
        # `cli_args` at all — they were not produced by evaluate_detections.py —
        # but they do record `input_files`. Start from whatever exists and fill
        # the rest below, so an adapter cell is loadable given a --ground-truth
        # override naming a materialised reference.
        cli = dict(meta.get("cli_args") or {})
        inf = meta.get("input_files") or {}
        cli.setdefault("bounds", inf.get("bounds"))
        cli.setdefault("ground_truth", inf.get("ground_truth"))
        # Batch-mode fallback. `--batch` records the BATCH-level invocation in
        # cli_args, so `detections` and `detections_dir` are both null there and
        # the per-cell input lives in `_metadata.input_files.detections` instead.
        # Without this, every cell scored through a batch YAML is unreproducible
        # from the committed record — 18 cells across n1-baseline-matrix-384 and
        # diversity-dividend-384, which is why neither board could be re-tiered
        # under E83 on the first attempt. The fallback is additive: it fires only
        # where cell_per_tile would otherwise raise.
        if not (cli.get("detections") or cli.get("detections_dir")):
            fallback = (meta.get("input_files") or {}).get("detections")
            if isinstance(fallback, str):
                cli["detections_dir"] = fallback
            elif isinstance(fallback, list) and fallback:
                cli["detections"] = fallback
        gts.add(cli["ground_truth"])
        boundss.add(cli["bounds"])
        resolved.append({"ref": ref, "cond": cond, "eval_path": eval_path, "cli": cli})

    if gt_override is None and len(gts) != 1:
        raise ValueError(
            f"Board cells disagree on ground truth ({sorted(gts)}); pass "
            f"--ground-truth to override or fix the board membership."
        )
    if bounds_override is None and len(boundss) != 1:
        raise ValueError(
            f"Board cells disagree on bounds ({sorted(boundss)}); pass --bounds "
            f"to override or fix the board membership."
        )
    gt_path = gt_override or (BASE_DIR / next(iter(gts)))
    bounds_path = bounds_override or (BASE_DIR / next(iter(boundss)))

    print(f"Loading references {gt_path.name} and bounds {bounds_path.name} ...",
          flush=True)
    gdf_ref = gpd.read_file(gt_path).to_crs(TARGET_CRS)
    gdf_bounds = gpd.read_file(bounds_path).to_crs(TARGET_CRS)
    tile_order = list(gdf_bounds["tile_name"].unique())
    print(f"  {len(tile_order)} evaluation tiles", flush=True)

    cells: list[dict] = []
    for r in resolved:
        cond, eval_path, cli = r["cond"], r["eval_path"], r["cli"]
        tp, fp, fn, n_passes = cell_per_tile(cli, gdf_ref, gdf_bounds, tile_order,
                                             buffer_metres)
        # Kind label: distinguish the three Era-1 architectures so the board
        # does not mislabel proposer-verifier cells as single-pass.
        kind = {
            "consensus": "consensus",
            "proposer-verifier": "verified-PV",
        }.get(cond.get("architecture"), "single-pass")
        eval_f1 = board_f1_at_20m(eval_path, buffer_metres)
        observed = micro_f1(tp.sum(), fp.sum(), fn.sum())
        cells.append(
            {
                "ref": r["ref"],
                "label": cond["label"],
                "kind": kind,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "n_passes": n_passes,
                "eval_f1": round(float(eval_f1), 6),
                "observed_micro_f1": round(observed, 6),
                "f1_gap": round(observed - eval_f1, 6),
                "mcc": (lambda m: round(float(m), 6) if m is not None else None)(
                    read_tile_mcc(eval_path)
                ),
            }
        )
        print(
            f"  {kind:12s} {cond['label']:34s} passes={n_passes:2d} "
            f"eval-F1={cells[-1]['eval_f1']:.4f} "
            f"micro-F1-of-mean={cells[-1]['observed_micro_f1']:.4f} "
            f"gap={cells[-1]['f1_gap']:+.4f} MCC={cells[-1]['mcc']}",
            flush=True,
        )
    return cells, gdf_ref, gdf_bounds, tile_order


def main() -> int:
    """CLI entry point: load the board, round-robin, tier, and write results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-id", type=str, required=True,
                        help="run-analyses.json analysis whose conditions_compared "
                             "defines the board membership.")
    parser.add_argument("--conditions", type=Path, default=DEFAULT_CONDITIONS)
    parser.add_argument("--analyses", type=Path, default=DEFAULT_ANALYSES)
    parser.add_argument("--ground-truth", type=Path, default=None,
                        help="Optional override; else derived from the cells' evals.")
    parser.add_argument("--bounds", type=Path, default=None,
                        help="Optional override; else derived from the cells' evals.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--n-permutations", type=int, default=N_PERMUTATIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    cells, _gdf_ref, _gdf_bounds, tile_order = load_cells(
        args.conditions, args.analyses, args.analysis_id,
        args.bounds, args.ground_truth,
    )
    print(f"Loaded {len(cells)} cells "
          f"({sum(c['kind'] == 'single-pass' for c in cells)} single-pass + "
          f"{sum(c['kind'] == 'consensus' for c in cells)} consensus + "
          f"{sum(c['kind'] == 'verified-PV' for c in cells)} verified-PV)", flush=True)

    # --- Round-robin C(N, 2) float tile-swap permutation tests ---
    pairs = list(combinations(range(len(cells)), 2))
    print(f"Running {len(pairs)} pairwise permutation tests "
          f"({args.n_permutations} perms each, seed {args.seed}) ...", flush=True)
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

    # --- Sort by the eval-reported F1@20 m (the ranked headline) and tier ---
    ordered = sorted(cells, key=lambda c: c["eval_f1"], reverse=True)
    ordered_refs = [c["ref"] for c in ordered]
    tiers = greedy_clique_tiers(ordered_refs, significant)
    tie_set = tiers[0]
    tier_of = {ref: t for t, members in enumerate(tiers, 1) for ref in members}

    n_sig = sum(1 for r in pairwise if r["significant"])
    print(
        f"FDR: {n_sig}/{len(pairwise)} pairs significant at q={FDR_Q} "
        f"-> {len(tiers)} tiers; tie_set (Tier 1) = {len(tie_set)} cell(s)",
        flush=True,
    )

    # --- Write result JSON + Markdown ---
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "analysis_id": args.analysis_id,
        "metric": "f1",
        "buffer_metres": HEADLINE_BUFFER_M,
        "n_permutations": args.n_permutations,
        "seed": args.seed,
        "fdr_q": FDR_Q,
        "n_tiles": len(tile_order),
        "replicate_handling": (
            "single-set cells: integer per-tile of one aggregated set; "
            "replicate-mean cells (single-pass K runs, phase3c 5 replications): "
            "pass-averaged per-tile (float)"
        ),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "ranking": [
            {
                "rank": i + 1,
                "ref": c["ref"],
                "label": c["label"],
                "kind": c["kind"],
                "n_passes": c["n_passes"],
                "eval_f1": c["eval_f1"],
                "observed_micro_f1": c["observed_micro_f1"],
                "f1_gap": c["f1_gap"],
                "mcc": c["mcc"],
                "tier": tier_of[c["ref"]],
            }
            for i, c in enumerate(ordered)
        ],
        "tiers": [{"tier": i + 1, "members": m} for i, m in enumerate(tiers)],
        "tie_set": tie_set,
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
    n_sp = sum(1 for c in ordered if c["kind"] == "single-pass")
    n_con = sum(1 for c in ordered if c["kind"] == "consensus")
    n_pv = sum(1 for c in ordered if c["kind"] == "verified-PV")
    n_sig = sum(1 for r in result["pairwise"] if r["significant"])
    pv_frag = f" + {n_pv} verified-PV" if n_pv else ""
    lines = [
        f"# Era-1 leaderboard — statistical tiering (20 m) — `{result['analysis_id']}`",
        "",
        f"- **Cells**: {len(ordered)} ({n_sp} single-pass + {n_con} consensus{pv_frag}), "
        f"{result['n_tiles']} evaluation tiles",
        f"- **Metric**: micro-average F1 @ {result['buffer_metres']} m; "
        f"MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)",
        f"- **Test**: round-robin tile-swap permutation, "
        f"{result['n_permutations']:,} perms, seed {result['seed']}, two-sided; "
        f"**BH-FDR** q = {result['fdr_q']}",
        f"- **Pairs**: {len(result['pairwise'])} ({n_sig} significant) -> "
        f"**{len(result['tiers'])} tiers**",
        f"- **Tie set (Tier 1)**: {', '.join('`' + r + '`' for r in result['tie_set'])}",
        "",
        "| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for i, c in enumerate(ordered, 1):
        mcc = f"{c['mcc']:.3f}" if c["mcc"] is not None else "—"
        lines.append(
            f"| {i} | `{c['label']}` | {c['kind']} | {c['n_passes']} | "
            f"{c['eval_f1']:.3f} | {c['observed_micro_f1']:.3f} | "
            f"{c['f1_gap']:+.3f} | {mcc} | {tier_of[c['ref']]} |"
        )
    md_path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
