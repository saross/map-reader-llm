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
# Tiering ranks F1 at the headline buffer (``--buffer``, default the
# preregistered 20 m; a 55-map board's headline is 50 m). MCC (buffer-agnostic
# tile-level discrimination, ``summary.tile_classification.mcc.point``) is
# carried as a reported column per the standing report-MCC-with-F1 preference.
#
# Since 2026-09-12, ``--permute-mcc`` ALSO makes MCC a permutation statistic:
# each cell's per-tile one-hot (TP, TN, FP, FN) classification is rebuilt
# through ``lib_advanced_metrics.compute_per_tile_classification`` (the house
# definition), hard-gated against the cell's committed
# ``tile_classification.confusion`` and MCC point estimate, and swapped by
# ``pairwise_permutation_test.permutation_test_mcc_arrays`` — the MCC sibling of
# ``permutation_test_float``. Both kernels draw one
# ``rng.random(n_tiles) < 0.5`` mask per iteration from
# ``default_rng(seed)``, so with one seed and one tile order the F1 and MCC
# tests see BYTE-IDENTICAL swap masks: two statistics of one permutation, with
# a separate BH-FDR family each. MCC needs one detection SET per cell, so a
# replicate-mean cell (``detections_dir``) raises rather than being silently
# collapsed.
#
# Since 2026-09-13 (PI ruling, S153 ruling 7), ``--permute-mcc`` also emits an
# MCC TIERING — the same ``greedy_clique_tiers`` instrument, over cells ordered
# by tile-MCC and cliqued on the MCC family's own BH verdicts — under
# ``mcc_permutation.ranking`` / ``.tiers`` / ``.tie_set``. It is REPORTED
# BESIDE the F1 tiering and does not replace it: the board's ranked headline
# stays the preregistered F1, and ``tiers`` / ``tie_set`` at the top level are
# always the F1 ones.
#
# Since 2026-09-13 (PI ruling), a cell the tile-join invariant REFUSES has its
# MCC withheld instead of aborting the board: the ``ConfusionGateError`` is
# caught per cell, the cell keeps its F1 rank with ``mcc: null``, it is left
# out of the MCC BH family, and it is listed under
# ``mcc_permutation.withheld`` with the refusal reason. Before this, one
# refused cell killed the whole run — which is why the Era-2 board could not
# admit the three Gemini 3.7 gold-standard text rungs at all.
#
# A cell the invariant refuses on the F1 ARM has no per-tile table on this
# frame at all, so it is withheld from BOTH families and listed under the
# top-level ``withheld_cells``. Each such record carries ruling 6's full
# disclosure: the whole-frame F1 point estimate that survives, the statement
# that its interval is WITHDRAWN (the bootstrap resamples tiles, so the refused
# table is the interval's input too), the interval being withdrawn where the
# committed artefact still carries one, the shortfall counts, and BOTH tile
# vocabularies — from ``lib_advanced_metrics.describe_tile_join_refusal``, the
# same describer ``evaluate_detections.py`` writes into a refused cell's own
# artefact.
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
from lib_advanced_metrics import (  # noqa: E402
    TILE_JOIN_DEFAULT,
    TILE_JOIN_REASON_DETECTION_SHORTFALL,
    TILE_JOIN_REASON_NO_SOURCE_TILE,
    TILE_JOIN_REASON_REFERENCE_SHORTFALL,
    calculate_tile_classification,
    compute_per_tile_classification,
    compute_per_tile_tp_fp_fn,
    describe_tile_join_refusal,
)
from lib_detection_paths import resolve_pool_passes  # noqa: E402
from pairwise_permutation_test import (  # noqa: E402
    assign_source_tiles,
    compute_mcc_or_none,
    permutation_test_mcc_arrays,
)

#: Recorded MCC is rounded to 4 dp by evaluate_detections.py, so the gate
#: cannot be tighter than half a unit in the last place.
MCC_GATE_TOL = 5e-5

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



class ConfusionGateError(RuntimeError):
    """A cell's rebuilt tile confusion disagrees with its committed evaluation."""


def read_tile_confusion(eval_path: Path) -> dict | None:
    """Read a cell's committed per-tile confusion cells, if it recorded them.

    Args:
        eval_path: Path to the cell's evaluation.json.

    Returns:
        A ``{tp, tn, fp, fn}`` dict of ints, or ``None`` when the evaluation
        carries no ``tile_classification.confusion`` block.
    """
    summary = json.loads(eval_path.read_text())["summary"]
    conf = (summary.get("tile_classification") or {}).get("confusion")
    if not isinstance(conf, dict):
        return None
    return {k: int(conf[k]) for k in ("tp", "tn", "fp", "fn") if k in conf}


def cell_detections(cli_args: dict, gdf_bounds: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Rebuild ONE detection set for a cell, with source tiles assigned.

    The MCC statistic is a per-tile binary classification of one detection SET,
    so unlike :func:`cell_per_tile` it has no replicate-mean form: a
    pass-averaged per-tile *count* has no one-hot classification. Replicate-mean
    cells therefore raise rather than being silently collapsed.

    Args:
        cli_args: The cell's ``evaluation.json[_metadata][cli_args]``.
        gdf_bounds: Evaluation tile boundaries in ``TARGET_CRS``.

    Returns:
        The cell's detections in ``TARGET_CRS`` with a ``source_tile`` column.

    Raises:
        ValueError: if the cell is a replicate-mean (``detections_dir``) cell.
        FileNotFoundError: if a declared detection file is missing.
    """
    det = cli_args.get("detections")
    if not det:
        raise ValueError(
            "MCC permutation needs a single detection SET; this cell declares "
            "detections_dir (a replicate-mean cell), for which a per-tile "
            "one-hot classification is undefined"
        )
    files = det if isinstance(det, list) else [det]
    paths = [BASE_DIR / f for f in files]
    missing = [q for q in paths if not q.exists()]
    if missing:
        raise FileNotFoundError(f"detections set file(s) not found: {missing}")
    parts = [_read_detections_gdf(q) for q in paths]
    gdf_det = (
        parts[0] if len(parts) == 1
        else gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=TARGET_CRS)
    )
    return assign_source_tiles(gdf_det, gdf_bounds)


def cell_per_tile_classification(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_order: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict]:
    """Per-tile one-hot (TP, TN, FP, FN) classification aligned to ``tile_order``.

    Wraps ``lib_advanced_metrics.compute_per_tile_classification`` — the house
    definition, a thin per-tile view over ``calculate_tile_classification`` — so
    the labels cannot drift from the ones ``evaluate_detections.py`` published.
    Buffer-free by construction: a tile is positive if it intersects any
    reference mound, predicted positive if the set assigned any detection to it.

    Args:
        gdf_det: One detection set in ``TARGET_CRS`` with ``source_tile``.
        gdf_ref: Ground-truth references in ``TARGET_CRS``.
        gdf_bounds: Evaluation tile boundaries in ``TARGET_CRS``.
        tile_order: Fixed list of ``tile_name`` values defining array positions.

    Returns:
        Tuple ``(tp, tn, fp, fn, diagnostics)`` — four integer arrays of
        length ``len(tile_order)``, plus the tile-join assignment
        diagnostics the confusion gate's geometric arm checks against.

    Raises:
        ConfusionGateError: if the tile join is refused for this frame, so
            that a mislabelled per-tile table never reaches the
            permutation harness.
    """
    tile_class = calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds)
    if "error" in tile_class:
        raise ConfusionGateError(
            f"tile join refused ({tile_class.get('reason')}): "
            f"{tile_class['error']}"
        )
    diagnostics = tile_class.get("tile_join_diagnostics") or {}
    per_tile = compute_per_tile_classification(gdf_det, gdf_ref, gdf_bounds)
    tile_index = {name: i for i, name in enumerate(tile_order)}
    n_tiles = len(tile_order)
    arrays = {k: np.zeros(n_tiles, dtype=int) for k in ("tp", "tn", "fp", "fn")}
    for _, row in per_tile.iterrows():
        idx = tile_index.get(row["tile_name"])
        if idx is None:
            continue
        for k in arrays:
            arrays[k][idx] = int(row[k])
    return (arrays["tp"], arrays["tn"], arrays["fp"], arrays["fn"],
            diagnostics)


def check_confusion_gate(label: str, rebuilt: dict, recorded: dict | None,
                         mcc_rebuilt: float | None, mcc_recorded: float | None,
                         geometry_check: dict | None = None,
                         ) -> dict:
    """Hard-gate a rebuilt tile confusion against geometry AND its own record.

    The MCC permutation is only trustworthy if the per-tile labels it swaps
    aggregate to the confusion matrix and MCC the published evaluation reported.
    A disagreement means the harness is not reproducing the scored cell, so it
    raises rather than reporting a number.

    **Reproduction alone is not enough, and that is what let the 2026-09-12
    tile-join defect through.** This gate rebuilds the confusion by calling
    the same ``calculate_tile_classification`` that produced the committed
    number, so where that function was wrong the gate reproduced the same
    wrong confusion and passed it. Three Gemini 3.7 rungs went through it
    with 21 of 475 in-frame detections booked and an MCC of 0.1337.

    The fix is a check against something other than itself: ``geometry_check``
    carries the tile-join assignment diagnostics, and every point lying
    inside the frame's tile union must have been booked to some tile. That
    is an appeal to the frame's polygons, not to a prior computation, so a
    join that does not describe the frame fails here even when the rebuild
    agrees with the record perfectly.

    Args:
        label: Cell label, for the error message.
        rebuilt: ``{tp, tn, fp, fn}`` recomputed here.
        recorded: ``{tp, tn, fp, fn}`` from the evaluation, or None if absent.
        mcc_rebuilt: MCC recomputed from ``rebuilt`` (None when undefined).
        mcc_recorded: ``tile_classification.mcc.point`` from the evaluation.
        geometry_check: ``tile_join_diagnostics``-shaped dict with
            ``detections`` and ``references`` sub-dicts carrying
            ``n_assigned`` and ``n_inside_union``. ``None`` skips the
            geometric arm, which should only happen for a cell whose
            detections could not be loaded.

    Returns:
        A gate-record dict for the output JSON, including the geometric
        arm's counts so a reader can see it actually ran.

    Raises:
        ConfusionGateError: on a geometric shortfall, on any cell-count
            disagreement, or on an MCC disagreement beyond the recorded
            4-dp rounding.
    """
    geometry_record: dict | None = None
    if geometry_check is not None:
        geometry_record = {}
        for noun in ("detections", "references"):
            side = geometry_check.get(noun) or {}
            assigned = side.get("n_assigned")
            inside = side.get("n_inside_union")
            geometry_record[noun] = {
                "n_assigned": assigned,
                "n_inside_union": inside,
                "n_outside_union": side.get("n_outside_union"),
            }
            if assigned is None or inside is None:
                continue
            if assigned < inside:
                raise ConfusionGateError(
                    f"{label}: tile join lost {inside - assigned} of "
                    f"{inside} in-frame {noun} — the confusion does not "
                    f"describe this frame's geometry, whether or not it "
                    f"reproduces the committed record"
                )

    if recorded is None:
        raise ConfusionGateError(
            f"{label}: evaluation records no tile_classification.confusion, so "
            f"the MCC permutation cannot be gated"
        )
    if rebuilt != recorded:
        raise ConfusionGateError(
            f"{label}: rebuilt tile confusion {rebuilt} != recorded {recorded}"
        )
    if mcc_recorded is not None and mcc_rebuilt is not None \
            and abs(mcc_rebuilt - mcc_recorded) > MCC_GATE_TOL:
        raise ConfusionGateError(
            f"{label}: rebuilt MCC {mcc_rebuilt:.6f} != recorded "
            f"{mcc_recorded:.6f}"
        )
    return {"confusion": rebuilt, "mcc_rebuilt": mcc_rebuilt,
            "mcc_recorded": mcc_recorded, "geometry": geometry_record,
            "passed": True}


#: Reason codes the tile-join invariant stamps into its refusal messages. A
#: ``ValueError`` carrying one of these is a REFUSAL — the cell's per-tile table
#: does not describe this frame — and is distinguishable from every other
#: ``ValueError`` the per-tile path can raise (an un-scoreable cell, a missing
#: file), which must still fail loud.
TILE_JOIN_REFUSAL_CODES = (
    TILE_JOIN_REASON_DETECTION_SHORTFALL,
    TILE_JOIN_REASON_REFERENCE_SHORTFALL,
    TILE_JOIN_REASON_NO_SOURCE_TILE,
)


def is_tile_join_refusal(error: Exception) -> bool:
    """Whether an exception is the tile-join invariant refusing a cell.

    The invariant raises a plain ``ValueError`` from
    ``lib_advanced_metrics.compute_per_tile_tp_fp_fn`` (the F1 arm) and a
    :class:`ConfusionGateError` from the tile-classification arm, so the F1
    arm's refusal has to be told apart from every other ``ValueError`` by its
    stamped reason code rather than by type.

    Args:
        error: The exception raised while building a cell's per-tile table.

    Returns:
        True when the message carries one of :data:`TILE_JOIN_REFUSAL_CODES`.
    """
    if isinstance(error, ConfusionGateError):
        return True
    return any(code in str(error) for code in TILE_JOIN_REFUSAL_CODES)


def mcc_family(cells: list[dict]) -> tuple[list[int], list[dict]]:
    """Split a loaded board into the MCC-testable cells and the withheld ones.

    A cell whose tile join the invariant refused carries no per-tile
    classification arrays, so it cannot enter the MCC permutation family. It is
    NOT dropped from the board: it keeps its F1 rank and is listed here so the
    board can publish what is not known about it (PI ruling 2026-09-13).

    Args:
        cells: Loaded cells from :func:`load_cells`, each optionally carrying
            ``tp_c`` (the per-tile classification survived) or
            ``mcc_withheld`` (the invariant refused it).

    Returns:
        ``(indices, withheld)`` — positions in ``cells`` that can be MCC-tested,
        and one record per withheld cell carrying its ``ref``, ``label``,
        ``recorded_mcc`` and ``reason``.
    """
    indices = [i for i, c in enumerate(cells) if "tp_c" in c]
    withheld = [{"ref": c["ref"], "label": c["label"], **c["mcc_withheld"]}
                for c in cells if "mcc_withheld" in c]
    return indices, withheld


#: What a withheld cell's confidence interval is, and why. A refused cell's
#: interval is not replaced by a better one: ``bootstrap_ci`` resamples TILES
#: (Decision 10; every artefact's ``_metadata.bootstrap.resampling_unit`` says
#: so), so the per-tile table the invariant refuses is the interval's input
#: too. The cell therefore has a point and no interval on this frame, and any
#: interval it used to carry is WITHDRAWN rather than superseded.
INTERVAL_WITHDRAWN: str = "interval withdrawn (tile-resampled bootstrap)"
INTERVAL_WITHDRAWN_DETAIL: str = (
    "the F1 bootstrap resamples tiles, so its input is the same per-tile table "
    "the tile-join invariant refuses; the cell has a whole-frame point estimate "
    "and no interval on this frame, and any interval it previously carried is "
    "withdrawn rather than superseded"
)


def committed_interval_f1(eval_path: Path, buffer_metres: int
                          ) -> list[float] | None:
    """The interval a withheld cell's committed evaluation still carries, if any.

    Two of the Era-2 board's three withheld cells were scored BEFORE the
    tile-join invariant existed, so their committed evaluations still hold a
    BCa interval on F1 — one resampled from a per-tile table the invariant now
    refuses. Naming that interval in the board's disclosure is the difference
    between "withdrawn" and "was never there": a reader who has the old
    artefact in hand must be able to see which number the board is retracting.

    Args:
        eval_path: Path to the cell's ``evaluation.json``.
        buffer_metres: Buffer whose interval to read.

    Returns:
        ``[lower, upper]`` when the committed artefact carries both bounds at
        that buffer, else ``None`` (a re-scored cell writes nulls there).
    """
    try:
        summary = json.loads(eval_path.read_text())["summary"]
    except (OSError, ValueError, KeyError):
        return None
    for block in summary.get("buffers", []):
        if block.get("buffer_metres") != buffer_metres:
            continue
        lower, upper = block.get("f1_ci_lower"), block.get("f1_ci_upper")
        if lower is None or upper is None:
            return None
        return [float(lower), float(upper)]
    return None


def refusal_disclosure(
    cli_args: dict,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> dict | None:
    """The shortfall counts and both tile vocabularies behind one refusal.

    PI ruling 2026-09-13 (S153 ruling 6) is that the name-based ``id`` tile
    join is the published convention and that a refused cell is disclosed
    rather than quietly dropped. A disclosure a reader can act on has to name
    the two vocabularies the refusal is a disagreement between, not just the
    count that went missing — so this reuses
    :func:`lib_advanced_metrics.describe_tile_join_refusal`, the same
    describer ``evaluate_detections.py`` writes into a refused cell's own
    artefact, rather than re-deriving a second dialect of the same facts.

    Args:
        cli_args: The cell's ``evaluation.json[_metadata][cli_args]``.
        gdf_ref: Reference mounds in ``TARGET_CRS``.
        gdf_bounds: The board frame's tile polygons in ``TARGET_CRS``.

    Returns:
        The refusal record (``shortfall``, ``vocabularies``, ``tile_join``,
        ``reference_join``, ``ruling``, …), or ``None`` when the detections
        cannot be rebuilt at all — a replicate-mean cell, say — in which case
        the refusal message remains the whole of what is known.
    """
    try:
        gdf_det = cell_detections(cli_args, gdf_bounds)
    except (ValueError, FileNotFoundError, OSError):
        return None
    try:
        return describe_tile_join_refusal(
            gdf_det, gdf_ref, gdf_bounds, TILE_JOIN_DEFAULT
        )
    except (ValueError, KeyError):
        return None


def mcc_point(cell: dict) -> float | None:
    """A cell's tile-MCC point estimate, from its evaluation or its arrays.

    ``cell["mcc"]`` is the committed, gate-checked number and is what the board
    publishes. A cell whose evaluation records no ``tile_classification`` still
    has one-hot arrays here (that is what the gate rebuilt), so the fallback
    recomputes the point rather than dropping the cell out of the MCC ordering.

    Args:
        cell: A loaded cell from :func:`load_cells`.

    Returns:
        The MCC point estimate, or ``None`` when neither source has one.
    """
    if cell.get("mcc") is not None:
        return float(cell["mcc"])
    if "tp_c" not in cell:
        return None
    value = compute_mcc_or_none(
        tp=int(cell["tp_c"].sum()), tn=int(cell["tn_c"].sum()),
        fp=int(cell["fp_c"].sum()), fn=int(cell["fn_c"].sum()),
    )
    return None if value is None else float(value)


def mcc_tiering(
    cells: list[dict],
    have_mcc: list[int],
    pairwise_mcc: list[dict],
) -> tuple[list[dict], list[list[str]]]:
    """Tier the MCC family by the same greedy clique the F1 tiering uses.

    PI ruling 2026-09-13 (S153 ruling 7): the tile-MCC permutation family is
    reported BESIDE the preregistered F1 tiering and does not replace it. So
    this produces a second ranking and a second tier assignment over the same
    cells — ordered by tile-MCC descending, cliqued on the MCC family's own
    BH verdicts — and the caller keeps both. The instrument is identical
    (``greedy_clique_tiers``, imported verbatim from the canonical chain); only
    the statistic and the BH family differ, which is the whole point of
    reporting them side by side.

    Args:
        cells: Loaded cells from :func:`load_cells`.
        have_mcc: Positions in ``cells`` that entered the MCC family.
        pairwise_mcc: The MCC family's pairwise records, each carrying
            ``ref_a``, ``ref_b`` and a BH ``significant`` verdict.

    Returns:
        ``(ranking, tiers)`` — one ranking row per MCC-tested cell (rank, ref,
        label, mcc, and the F1 tier for side-by-side reading, which the caller
        fills in), and the tiers as lists of refs with ``tiers[0]`` the MCC
        tie set.
    """
    significant = {
        frozenset({r["ref_a"], r["ref_b"]}): bool(r["significant"])
        for r in pairwise_mcc
    }
    scored = [(mcc_point(cells[i]), cells[i]) for i in have_mcc]
    # A cell with no MCC at all cannot be ordered against one that has one;
    # it is already outside the family, so it is outside the ranking too.
    ordered = sorted(
        (pair for pair in scored if pair[0] is not None),
        key=lambda pair: pair[0], reverse=True,
    )
    tiers = greedy_clique_tiers([c["ref"] for _, c in ordered], significant)
    tier_of = {ref: t for t, members in enumerate(tiers, 1) for ref in members}
    ranking = [
        {
            "rank": i + 1,
            "ref": cell["ref"],
            "label": cell["label"],
            "mcc": round(point, 6),
            "eval_f1": cell["eval_f1"],
            "mcc_tier": tier_of[cell["ref"]],
        }
        for i, (point, cell) in enumerate(ordered)
    ]
    return ranking, tiers


def load_cells(
    conditions_path: Path,
    analyses_path: Path,
    analysis_id: str,
    bounds_override: Path | None,
    gt_override: Path | None,
    buffer_metres: int = HEADLINE_BUFFER_M,
    want_mcc: bool = False,
    withheld: list[dict] | None = None,
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
        buffer_metres: Buffer the F1 statistic is computed at.
        want_mcc: Also rebuild each cell's per-tile one-hot tile classification
            (and gate it against the committed confusion), so the MCC
            permutation can run on the same tile order as the F1 one.
        withheld: Optional sink for cells the tile-join invariant REFUSES. When
            a list is supplied, such a cell is appended to it (ref, label, its
            committed F1, the recorded MCC, and the refusal reason) and left out
            of the returned cells rather than raising — the board is then tiered
            over the cells that do have a per-tile table on this frame, and the
            withheld ones are published as withheld (PI ruling 2026-09-13).
            ``None`` keeps the fail-loud behaviour, which is what a caller
            without a place to publish a withholding wants.

    Returns:
        ``(cells, gdf_ref, gdf_bounds, tile_order)``.

    Raises:
        ValueError: if the cells disagree on ground truth / bounds and no
            override is supplied (a silent-scope-mix guard); or if a cell's
            per-tile table cannot be built for any reason other than a
            tile-join refusal, or for that reason with no ``withheld`` sink.
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
        # The tile-join invariant can refuse the F1 arm as well as the MCC arm:
        # a cell whose source_tile vocabulary is not this frame's has no
        # per-tile decomposition on it, only a sound whole-frame F1. When the
        # caller supplies a ``withheld`` sink, such a cell is WITHHELD from the
        # statistics and listed rather than aborting the board (PI ruling
        # 2026-09-13); without a sink the old fail-loud behaviour stands, which
        # is what every other caller of this function still wants.
        try:
            tp, fp, fn, n_passes = cell_per_tile(cli, gdf_ref, gdf_bounds,
                                                 tile_order, buffer_metres)
        except (ValueError, ConfusionGateError) as error:
            if withheld is None or not is_tile_join_refusal(error):
                raise
            withheld.append({
                "ref": r["ref"], "label": cond["label"],
                "eval_f1": round(float(board_f1_at_20m(eval_path, buffer_metres)), 6),
                "recorded_mcc": read_tile_mcc(eval_path),
                "arm": "per-tile F1 (and therefore MCC)",
                "reason": str(error),
                "ruling": ("PI ruling 2026-09-13: withhold and list, never "
                           "abort the board"),
                # Ruling 6's disclosure, carried as data so the board's README
                # can publish the shortfall counts and both tile vocabularies
                # instead of only the one-line refusal message.
                "interval_status": INTERVAL_WITHDRAWN,
                "interval_detail": INTERVAL_WITHDRAWN_DETAIL,
                "withdrawn_interval_f1": committed_interval_f1(
                    eval_path, buffer_metres),
                "disclosure": refusal_disclosure(cli, gdf_ref, gdf_bounds),
            })
            print(f"  WITHHELD {cond['label']}: {error}", flush=True)
            continue
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
        if want_mcc:
            # A cell the tile-join invariant refuses has its MCC WITHHELD and
            # is dropped from the MCC family — it does NOT abort the board.
            # PI ruling 2026-09-13: a board must not be destroyed by one cell
            # whose vocabulary the frame cannot join, and withholding is the
            # honest record of what is not known (the alternative, publishing
            # the committed pre-invariant number, is the defect the gate was
            # written to catch). The F1 side is unaffected: it is computed
            # from the buffered per-tile counts, not from the tile join.
            try:
                gdf_det = cell_detections(cli, gdf_bounds)
                tp_c, tn_c, fp_c, fn_c, join_diagnostics = (
                    cell_per_tile_classification(
                        gdf_det, gdf_ref, gdf_bounds, tile_order
                    )
                )
                rebuilt = {"tp": int(tp_c.sum()), "tn": int(tn_c.sum()),
                           "fp": int(fp_c.sum()), "fn": int(fn_c.sum())}
                mcc_rebuilt = compute_mcc_or_none(**rebuilt)
                gate = check_confusion_gate(
                    cond["label"], rebuilt, read_tile_confusion(eval_path),
                    None if mcc_rebuilt is None else round(float(mcc_rebuilt), 6),
                    cells[-1]["mcc"],
                    geometry_check=join_diagnostics,
                )
            except ConfusionGateError as error:
                cells[-1].update({
                    "mcc_withheld": {
                        "recorded_mcc": cells[-1]["mcc"],
                        "reason": str(error),
                        "ruling": ("PI ruling 2026-09-13: withhold and list, "
                                   "never abort the board"),
                    },
                    "mcc_gate": {"passed": False, "withheld": True,
                                 "reason": str(error)},
                })
                cells[-1]["mcc"] = None
                print(f"    MCC WITHHELD for {cond['label']}: {error}",
                      flush=True)
            else:
                cells[-1].update({"tp_c": tp_c, "tn_c": tn_c, "fp_c": fp_c,
                                  "fn_c": fn_c, "mcc_gate": gate,
                                  "n_detections": int(len(gdf_det))})
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
    parser.add_argument(
        "--buffer", type=int, default=HEADLINE_BUFFER_M,
        help="Buffer in metres the F1 statistic is computed at (default: "
             f"{HEADLINE_BUFFER_M}, the preregistered headline). A 55-map "
             "board's headline is 50.",
    )
    parser.add_argument(
        "--strict-tile-join", action="store_true",
        help="Abort on the FIRST cell the tile-join invariant refuses, instead "
             "of withholding it and tiering the rest. The default (withhold "
             "and list) is the PI ruling of 2026-09-13: a board must not be "
             "destroyed by one cell whose vocabulary its frame cannot join. "
             "Pass this when you want the refusal to be fatal — auditing a "
             "board that is supposed to have no refused cell, for instance.",
    )
    parser.add_argument(
        "--permute-mcc", action="store_true",
        help="Also run the tile-swap permutation on tile-level MCC, through "
             "the same per-tile swap masks as the F1 test (same seed, same "
             "tile order), with its own BH-FDR family. Every cell must be a "
             "single detection SET and must carry a committed "
             "tile_classification.confusion to gate against.",
    )
    args = parser.parse_args()

    withheld_cells: list[dict] = []
    cells, _gdf_ref, _gdf_bounds, tile_order = load_cells(
        args.conditions, args.analyses, args.analysis_id,
        args.bounds, args.ground_truth, buffer_metres=args.buffer,
        want_mcc=args.permute_mcc,
        withheld=None if args.strict_tile_join else withheld_cells,
    )
    if withheld_cells:
        print(f"WITHHELD {len(withheld_cells)} cell(s) the tile-join invariant "
              f"refused; they are listed in the output and are NOT tiered: "
              + ", ".join(w["label"] for w in withheld_cells), flush=True)
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

    # --- Optional MCC round-robin, on the SAME swap masks -----------------
    # Same kernel family, same seed, same tile order: the MCC test sees the
    # identical per-tile swap mask the F1 test saw, so a ΔF1 and a ΔMCC on one
    # pair are two statistics of one permutation, not two separate experiments.
    pairwise_mcc: list[dict] = []
    withheld_mcc: list[dict] = []
    mcc_ranking: list[dict] = []
    mcc_tiers: list[list[str]] = []
    if args.permute_mcc:
        # Cells whose tile join the invariant refused carry no per-tile
        # classification arrays, so they cannot enter the MCC family. The BH
        # family is therefore the pairs among the cells that DO have one, and
        # the withheld cells are listed rather than silently dropped.
        have_mcc, withheld_mcc = mcc_family(cells)
        mcc_pairs = list(combinations(have_mcc, 2))
        if withheld_mcc:
            print(f"MCC withheld for {len(withheld_mcc)} of {len(cells)} cells; "
                  f"the MCC family is {len(mcc_pairs)} pairs of "
                  f"{len(pairs)}", flush=True)
        print(f"Running {len(mcc_pairs)} pairwise MCC permutation tests "
              f"({args.n_permutations} perms, seed {args.seed}) ...", flush=True)
        for a, b in mcc_pairs:
            ca, cb = cells[a], cells[b]
            res = permutation_test_mcc_arrays(
                ca["tp_c"], ca["tn_c"], ca["fp_c"], ca["fn_c"],
                cb["tp_c"], cb["tn_c"], cb["fp_c"], cb["fn_c"],
                n_permutations=args.n_permutations, seed=args.seed,
            )
            pairwise_mcc.append({"ref_a": ca["ref"], "ref_b": cb["ref"], **res})
        adjusted_mcc = apply_bh_correction(
            [r["p_value"] for r in pairwise_mcc], q=FDR_Q
        )
        for r, adj in zip(pairwise_mcc, adjusted_mcc):
            r["bh_adjusted_p"] = round(adj, 6)
            r["significant"] = bool(adj < FDR_Q)
        n_sig_mcc = sum(1 for r in pairwise_mcc if r["significant"])
        print(f"MCC FDR: {n_sig_mcc}/{len(pairwise_mcc)} pairs significant "
              f"at q={FDR_Q}", flush=True)
        # Ruling 7's "reported beside the F1 tiering": the MCC family gets its
        # own greedy-clique tiers, over its own BH verdicts. The board's
        # tiering stays the preregistered F1 one — this is a second reading of
        # the same cells, not a replacement ranking.
        mcc_ranking, mcc_tiers = mcc_tiering(cells, have_mcc, pairwise_mcc)
        print(f"MCC tiering: {len(mcc_tiers)} tiers; MCC tie set = "
              f"{len(mcc_tiers[0]) if mcc_tiers else 0} cell(s)", flush=True)

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
        "buffer_metres": args.buffer,
        "n_permutations": args.n_permutations,
        "seed": args.seed,
        "fdr_q": FDR_Q,
        "n_tiles": len(tile_order),
        "n_cells": len(cells),
        "n_cells_withheld": len(withheld_cells),
        "withheld_cells": withheld_cells,
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
    if args.permute_mcc:
        result["mcc_permutation"] = {
            "statistic": "tile-level MCC (buffer-invariant: tile truth is "
                         "intersection with any reference, tile prediction is "
                         "any detection assigned to the tile)",
            "kernel": "pairwise_permutation_test.permutation_test_mcc_arrays",
            "swap_mask": "identical to the F1 test's (same seed, same tile "
                         "order, same rng.random(n_tiles) < 0.5 stream)",
            "fdr_q": FDR_Q,
            "n_cells_with_mcc": sum(1 for c in cells if "tp_c" in c),
            "n_cells_withheld": len(withheld_mcc),
            "withheld": withheld_mcc,
            "n_pairs": len(pairwise_mcc),
            "n_significant": sum(1 for r in pairwise_mcc if r["significant"]),
            "reported_not_tiering": (
                "PI ruling 2026-09-13 (S153 ruling 7): the MCC family is "
                "reported BESIDE the preregistered F1 tiering and does not "
                "replace it. The board's tiering is the F1 one."
            ),
            "n_tiers": len(mcc_tiers),
            "tie_set": mcc_tiers[0] if mcc_tiers else [],
            "tiers": [{"tier": i + 1, "members": m}
                      for i, m in enumerate(mcc_tiers)],
            "ranking": [
                {**row, "f1_tier": tier_of.get(row["ref"])}
                for row in mcc_ranking
            ],
            "gates": {c["ref"]: c.get("mcc_gate") for c in cells},
            "pairwise": pairwise_mcc,
        }
    json_path = args.output_dir / f"tiering_{args.buffer}m.json"
    json_path.write_text(json.dumps(result, indent=2))
    print(f"Wrote {json_path}", flush=True)

    md_path = args.output_dir / f"tiering_{args.buffer}m.md"
    _write_markdown(md_path, result, ordered, tier_of)
    print(f"Wrote {md_path}", flush=True)
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
        f"# Era-1 leaderboard — statistical tiering "
        f"({result['buffer_metres']} m) — `{result['analysis_id']}`",
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
    ]
    if result.get("withheld_cells"):
        lines += [
            f"- **{len(result['withheld_cells'])} cell(s) WITHHELD** — the "
            f"tile-join invariant refuses their per-tile table on this frame, "
            f"so they are neither ranked nor tested here. Their whole-frame F1 "
            f"is unaffected and is quoted for reference:",
            "",
        ]
        lines += [f"  - `{w['label']}` (F1@{result['buffer_metres']} m "
                  f"{w['eval_f1']:.4f}) — {w['reason']}"
                  for w in result["withheld_cells"]]
        lines += [""]
    lines += [
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
    if result.get("mcc_permutation"):
        mcc_block = result["mcc_permutation"]
        lines += [
            "",
            "## Tile-level MCC — the same permutation, a second statistic",
            "",
            f"- **Test**: tile-swap permutation on tile-level MCC, "
            f"{result['n_permutations']:,} perms, seed {result['seed']}, "
            f"two-sided; **BH-FDR** q = {mcc_block['fdr_q']} within this "
            f"board; swap masks identical to the F1 test's",
            f"- **Pairs**: {len(mcc_block['pairwise'])} "
            f"({mcc_block['n_significant']} significant)",
        ]
        if mcc_block.get("withheld"):
            lines += [
                f"- **MCC WITHHELD** for {len(mcc_block['withheld'])} cell(s) "
                f"the tile-join invariant refused; they are ranked on F1 and "
                f"excluded from this BH family:",
                "",
            ]
            lines += [f"  - `{w['label']}` — {w['reason']}"
                      for w in mcc_block["withheld"]]
        if mcc_block.get("ranking"):
            lines += [
                "",
                f"- **MCC tiers**: {mcc_block['n_tiers']}; MCC tie set "
                f"{len(mcc_block['tie_set'])} cell(s). Reported beside the F1 "
                f"tiering, which remains the board's tiering (ruling 7).",
                "",
                "| MCC rank | condition | tile-MCC | MCC tier | F1 tier | F1@20m |",
                "|---:|---|---:|---:|---:|---:|",
            ]
            for row in mcc_block["ranking"]:
                f1_tier = row.get("f1_tier")
                lines.append(
                    f"| {row['rank']} | `{row['label']}` | {row['mcc']:.4f} | "
                    f"{row['mcc_tier']} | "
                    f"{f1_tier if f1_tier is not None else '—'} | "
                    f"{row['eval_f1']:.4f} |"
                )
        lines += [
            "",
            "| a | b | MCC a | MCC b | ΔMCC | raw p | BH p | significant |",
            "|---|---|---:|---:|---:|---:|---:|:--:|",
        ]
        for r in mcc_block["pairwise"]:
            lines.append(
                f"| `{r['ref_a']}` | `{r['ref_b']}` | {r['mcc_a']:.4f} | "
                f"{r['mcc_b']:.4f} | {r['observed_mcc_diff']:+.4f} | "
                f"{r['p_value']:.4f} | {r['bh_adjusted_p']:.4f} | "
                f"{'yes' if r['significant'] else 'no'} |"
            )
    md_path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
