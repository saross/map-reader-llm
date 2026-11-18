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
# Since 2026-10-30, ``--tile-join`` names the rule the MCC arm books points to
# tiles with (``lib_advanced_metrics.TILE_JOINS``), for the tile-join
# sensitivity reading of the MCC family (``planning/paper-writeup-continuity.md``,
# the MCC robustness job, part (b)). The default is ``TILE_JOIN_DEFAULT``
# (``id``, the published convention, S153 ruling 6) and with it every byte of
# behaviour and output is as before. A geometric join changes ONLY the MCC
# arm: the F1 arm, its per-tile counts, its tiering and its withheld cells are
# untouched, because the per-tile F1 table keeps the published join. Under a
# geometric join no committed record exists to gate the rebuilt confusion
# against, so the gate compares the per-tile labels with the scorer's own
# aggregate confusion under that join (plus the geometric arm, which holds by
# construction), the MCC family ranks on that join's MCC at the committed four
# decimals, and the outputs are written as ``tiering_<buffer>m_<join>.json``
# and ``.md`` so they can never overwrite a board's published tiering.
#
# Since 2026-11-18 (tile-join Wave 1, PI rulings D72 and D73), the harness
# takes TWO separate options, and the paragraph above is superseded:
#   * ``--tile-join`` is the CLASSIFICATION join of the MCC arm (default
#     ``sheet-contains``, containment within each sheet);
#   * ``--count-table-join`` is the COUNT-TABLE join of the F1 arm's per-tile
#     TP/FP/FN (default ``sheet-primary``), which every committed tiering
#     built under the legacy ``id`` rule.
# ``TILE_JOIN_DEFAULT`` is retired, so "not the default" no longer means
# "sensitivity". Each cell runs TWO computations, in order:
#   1. VALIDATE the committed evaluation under the rules IT recorded
#      (``lib_advanced_metrics.recorded_tile_joins``: a missing record means
#      the legacy ``id``; contradictory provenance, or a Wave-1 evaluation
#      without provenance, is rejected). With ``--permute-mcc`` the rebuilt
#      confusion under the recorded classification join must equal the
#      committed one (or reproduce its recorded refusal) — the old gate,
#      unweakened;
#   2. COMPUTE every analysed value — per-tile arrays, MCC, ranks — under the
#      REQUESTED rules. No output carries an old committed MCC beside newly
#      computed arrays: where the requested classification join is not the
#      recorded one, a cell's ``mcc`` is the newly computed value (with
#      ``--permute-mcc``) or ``null`` with ``mcc_status`` saying why.
# Outputs under the two defaults are written as ``tiering_<buffer>m.json``;
# any other choice is stamped into the name (``_<join>`` for a classification
# join, ``_ct-<join>`` for a count-table join; :func:`tiering_stem`), so a
# replay such as ``--tile-join id --count-table-join id`` never overwrites a
# corrected tiering. Every output records both rules (``tile_joins``).
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
import re
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

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
    TILE_JOIN_CLASSIFICATION_DEFAULT,
    TILE_JOIN_COUNT_TABLE_DEFAULT,
    TILE_JOIN_LEGACY_CLASSIFICATION,
    TILE_JOIN_LEGACY_COUNT_TABLE,
    TILE_JOIN_REASON_DETECTION_SHORTFALL,
    TILE_JOIN_REASON_NO_SOURCE_TILE,
    TILE_JOIN_REASON_REFERENCE_SHORTFALL,
    TILE_JOIN_REASON_UNATTRIBUTED_DETECTION,
    TILE_JOIN_REASON_UNATTRIBUTED_REFERENCE,
    TILE_JOINS_CLASSIFICATION,
    TILE_JOINS_COUNT_TABLE,
    calculate_f1_internal,
    calculate_tile_classification,
    check_tile_joins,
    compute_per_tile_classification,
    compute_per_tile_tp_fp_fn,
    describe_tile_join_refusal,
    recorded_tile_joins,
    tile_join_provenance,
)
from lib_content_anchor import git_blob_hash  # noqa: E402
from lib_detection_paths import resolve_pool_passes  # noqa: E402
from pairwise_permutation_test import (  # noqa: E402
    assign_source_tiles,
    compute_mcc_or_none,
    permutation_test_mcc_arrays,
)

#: Recorded MCC is rounded to 4 dp by evaluate_detections.py, so the gate
#: cannot be tighter than half a unit in the last place.
MCC_GATE_TOL = 5e-5

#: Decimals a non-default tile join's MCC is ranked at. The published MCC
#: family ranks the committed evaluations' four-decimal values, so a
#: sensitivity reading under another join ranks at the same precision — the
#: value ``evaluate_detections.py`` would have written had the cell been
#: scored under that join — and ties resolve exactly as they would there.
MCC_PUBLISHED_DECIMALS = 4


def recorded_output_joins(data: dict) -> tuple[str, str]:
    """The (classification, count-table) rules an existing tiering JSON records.

    Wave 1 tierings record ``tile_joins``; a 2026-10-30 sensitivity tiering
    records only ``mcc_permutation.tile_join``; anything older was built
    under the legacy ``id`` on both arms.

    Args:
        data: A parsed tiering JSON.

    Returns:
        ``(classification, count_table)``.

    Raises:
        ValueError: If two records of one rule disagree (re-audit Low;
            mirrors ``k_ladder_mcb.tiering_joins`` after audit A-L7), rather
            than resolving them by whichever field is read first.
    """
    block = data.get("tile_joins") or {}
    mcc = data.get("mcc_permutation") or {}
    records = {
        "classification": (block.get("classification"), mcc.get("tile_join")),
        "count_table": (block.get("count_table"), data.get("count_table_join")),
    }
    legacy = {"classification": TILE_JOIN_LEGACY_CLASSIFICATION,
              "count_table": TILE_JOIN_LEGACY_COUNT_TABLE}
    out: dict[str, str] = {}
    for purpose, values in records.items():
        seen = {v for v in values if v}
        if len(seen) > 1:
            raise ValueError(
                f"tiering records contradictory {purpose} joins {sorted(seen)}")
        out[purpose] = seen.pop() if seen else legacy[purpose]
    return out["classification"], out["count_table"]


def refuse_overwrite_of_other_joins(path: Path, tile_join: str,
                                    count_table_join: str, allow: bool) -> None:
    """Refuse to overwrite an existing tiering built under other rules.

    Audit A-L5: the two defaults write the plain name, which every committed
    tiering (built under ``id``) also carries, so a default run would replace
    a committed ``id`` tiering in place. That is Wave 3's deliberate act, not
    a side effect: it needs ``--overwrite-other-joins``.

    Args:
        path: The output JSON about to be written.
        tile_join: The classification join requested.
        count_table_join: The count-table join requested.
        allow: ``--overwrite-other-joins``.

    Raises:
        SystemExit: If the file exists, records other rules, and ``allow``
            is not set.
    """
    if allow or not path.exists():
        return
    recorded = recorded_output_joins(json.loads(path.read_text()))
    if recorded != (tile_join, count_table_join):
        raise SystemExit(
            f"{path} exists and records joins {recorded}, not the requested "
            f"({tile_join!r}, {count_table_join!r}); refusing to overwrite it. "
            f"Pass --overwrite-other-joins to replace it deliberately.")


def tiering_stem(buffer_metres: int,
                 tile_join: str = TILE_JOIN_CLASSIFICATION_DEFAULT,
                 count_table_join: str = TILE_JOIN_COUNT_TABLE_DEFAULT) -> str:
    """The file stem a tiering is written under, by the rules it was built with.

    The two defaults keep the plain name; any other choice is stamped in, a
    classification join as ``_<join>`` and a count-table join as
    ``_ct-<join>``, so a replay or sensitivity reading can never overwrite
    or be mistaken for the corrected tiering it sits beside.

    Args:
        buffer_metres: The F1 statistic's buffer.
        tile_join: The classification join (MCC arm).
        count_table_join: The count-table join (F1 arm).

    Returns:
        E.g. ``tiering_20m`` or ``tiering_20m_id_ct-id``.

    Example:
        >>> tiering_stem(20, "id", "id")
        'tiering_20m_id_ct-id'
    """
    stem = f"tiering_{buffer_metres}m"
    if tile_join != TILE_JOIN_CLASSIFICATION_DEFAULT:
        stem += f"_{tile_join}"
    if count_table_join != TILE_JOIN_COUNT_TABLE_DEFAULT:
        stem += f"_ct-{count_table_join}"
    return stem

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
    count_table_join: str = TILE_JOIN_COUNT_TABLE_DEFAULT,
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
        buffer_metres: Match radius.
        count_table_join: The count-table join (``--count-table-join``).

    Returns:
        Tuple ``(tp, fp, fn)`` of float arrays, length ``len(tile_order)``.
    """
    tile_metrics = compute_per_tile_tp_fp_fn(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
        tile_join=count_table_join,
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
    count_table_join: str = TILE_JOIN_COUNT_TABLE_DEFAULT,
    per_pass: list[dict] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """Reproduce a cell's per-tile TP/FP/FN, its inputs exactly as its eval scored them.

    The detections, references, bounds and buffer are the eval's own; the
    count-table join is ``count_table_join`` (the eval's own was ``id``
    unless it records another; pass that to replay it).

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
        buffer_metres: Match radius.
        count_table_join: The count-table join the counts are booked under.
        per_pass: Optional sink. When given, one ``{"file", "tp", "fp",
            "fn"}`` record of whole-frame totals is appended per replicate
            pass, so a caller can rebuild each pass's own F1 (Astra R2-3:
            a replicate-mean cell's committed F1 is the mean of per-pass
            F1s, which the pass-averaged table does not give).

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
                                       buffer_metres, count_table_join)
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
                gdf_det, gdf_ref, gdf_bounds, tile_order, buffer_metres,
                count_table_join,
            )
            tp_sum += tp_i
            fp_sum += fp_i
            fn_sum += fn_i
            if per_pass is not None:
                per_pass.append({"file": str(pass_file), "tp": float(tp_i.sum()),
                                 "fp": float(fp_i.sum()), "fn": float(fn_i.sum())})
        n = len(pass_files)
        return tp_sum / n, fp_sum / n, fn_sum / n, n

    raise ValueError(
        "cli_args declare neither 'detections' nor 'detections_dir' — "
        "cannot reproduce this cell's per-tile counts"
    )



class ConfusionGateError(RuntimeError):
    """A cell's rebuilt tile confusion disagrees with its committed evaluation."""


class ReproductionDriftError(RuntimeError):
    """Step 1 of the two computations could not reproduce a committed record.

    Raised by :func:`validate_recorded_classification` when a committed tile
    record, replayed under the join it recorded, comes out different (a
    different confusion or MCC, a refusal where a confusion was recorded, a
    confusion where a refusal was recorded, or a different refusal). The
    Wave 1 specification's § 5 makes a legacy replay mismatch a STOP, so this
    is deliberately not a :class:`ConfusionGateError`: :func:`load_cells`
    does not catch it and withhold the cell, it ends the run (audit A-L6).
    """


class ReplayRouteUnsupportedError(ReproductionDriftError):
    """A committed record this replay cannot reconstruct, held for its own route.

    Astra R2-3: a replicate-mean record that ``evaluate_detections.py`` did
    not write (a native adapter's output), or that keeps no ``per_run``
    block, has no per-pass statistic this replay can rebuild. It is held,
    never reported as validated; as a :class:`ReproductionDriftError` it
    ends the run rather than being withheld.
    """


#: The writer whose replicate-mean records this replay reconstructs.
EVALUATOR_SCRIPT_NAME = "evaluate_detections.py"

#: Per-pass F1 tolerance: each pass's committed F1 is rounded to 4 dp.
F1_RECORD_TOL = 5e-5

#: Mean F1 tolerance: the committed mean is ``round(mean(round(f1_i, 4)), 4)``
#: (``evaluate_multi_run_mean``), so it carries two roundings.
F1_MEAN_TOL = 1e-4 + 1e-9


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
    tile_join: str = TILE_JOIN_CLASSIFICATION_DEFAULT,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict]:
    """Per-tile one-hot (TP, TN, FP, FN) classification aligned to ``tile_order``.

    Wraps ``lib_advanced_metrics.compute_per_tile_classification`` — the house
    definition, a thin per-tile view over ``calculate_tile_classification`` — so
    the labels cannot drift from the ones ``evaluate_detections.py`` published.
    Buffer-free by construction: a tile is positive if the join books any
    reference mound to it, predicted positive if it books any detection to it.

    Args:
        gdf_det: One detection set in ``TARGET_CRS`` with ``source_tile``.
        gdf_ref: Ground-truth references in ``TARGET_CRS``.
        gdf_bounds: Evaluation tile boundaries in ``TARGET_CRS``.
        tile_order: Fixed list of ``tile_name`` values defining array positions.
        tile_join: One of ``lib_advanced_metrics.TILE_JOINS_CLASSIFICATION``,
            passed to both library calls so the aggregate the diagnostics
            come from and the per-tile labels are built by one rule.
            Defaults to ``TILE_JOIN_CLASSIFICATION_DEFAULT``
            (``sheet-contains``); pass a cell's recorded join to replay it.

    Returns:
        Tuple ``(tp, tn, fp, fn, diagnostics)`` — four integer arrays of
        length ``len(tile_order)``, plus the tile-join assignment
        diagnostics the confusion gate's geometric arm checks against.

    Raises:
        ConfusionGateError: if the tile join is refused for this frame, so
            that a mislabelled per-tile table never reaches the
            permutation harness.
    """
    tile_class = calculate_tile_classification(
        gdf_det, gdf_ref, gdf_bounds, tile_join=tile_join,
    )
    if "error" in tile_class:
        raise ConfusionGateError(
            f"tile join refused ({tile_class.get('reason')}): "
            f"{tile_class['error']}"
        )
    diagnostics = tile_class.get("tile_join_diagnostics") or {}
    per_tile = compute_per_tile_classification(
        gdf_det, gdf_ref, gdf_bounds, tile_join=tile_join,
    )
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
    # RA-C1: compare the UNROUNDED rebuilt MCC with the recorded 4-dp value.
    # Rounding the rebuilt value first (to 6 dp, as the callers once did)
    # adds a second rounding error, and a true reproduction can then miss
    # the half-unit tolerance: 0.5206504316 -> 0.520650 is 5.0000000000105e-05
    # from the recorded 0.5207 (retest-phase3a-high::text-high-t0.3-n5-4of5).
    if mcc_recorded is not None and mcc_rebuilt is not None \
            and abs(float(mcc_rebuilt) - float(mcc_recorded)) > MCC_GATE_TOL:
        raise ConfusionGateError(
            f"{label}: rebuilt MCC {mcc_rebuilt:.6f} != recorded "
            f"{mcc_recorded:.6f}"
        )
    if mcc_rebuilt is not None:
        mcc_rebuilt = round(float(mcc_rebuilt), 6)  # the record keeps 6 dp
    return {"confusion": rebuilt, "mcc_rebuilt": mcc_rebuilt,
            "mcc_recorded": mcc_recorded, "geometry": geometry_record,
            "passed": True}


def join_sensitivity_gate(
    label: str,
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    rebuilt: dict,
    mcc_rebuilt: float | None,
    join_diagnostics: dict,
    tile_join: str,
) -> tuple[dict, float | None]:
    """Gate a cell's per-tile labels under a join its evaluation did NOT record.

    Step 2 of the two computations (Wave 1). Step 1,
    :func:`validate_recorded_classification`, has already reproduced the
    committed record under the join it recorded; under the requested join
    there is no committed record to compare with. What can still be checked,
    and is:

    * the **geometric arm** of :func:`check_confusion_gate` — every point inside
      the frame's tile union was booked to some tile. Under both geometric
      joins this holds by construction, so it is a guard on the library, not a
      finding;
    * the **per-tile labels against the scorer's own aggregate** — the
      ``tile_order``-aligned one-hot arrays must sum to the confusion
      ``calculate_tile_classification`` reports under the same join, and their
      MCC to its MCC at the published four decimals. This catches a tile
      dropped by the alignment (a tile name absent from ``tile_order``), which
      would silently shrink the confusion the permutation swaps.

    Neither arm is an appeal to an independent record; the record of what this
    gate does and does not establish travels with the output (``reference``).

    Args:
        label: Cell label, for the error message.
        gdf_det: The cell's detections, as the per-tile labels were built from.
        gdf_ref: Reference mounds in ``TARGET_CRS``.
        gdf_bounds: The frame's tile polygons in ``TARGET_CRS``.
        rebuilt: ``{tp, tn, fp, fn}`` summed from the per-tile arrays.
        mcc_rebuilt: MCC of ``rebuilt`` (``None`` when undefined).
        join_diagnostics: The ``tile_join_diagnostics`` block of the build.
        tile_join: The requested join in force.

    Returns:
        ``(gate_record, mcc_join)`` — the gate record for the output JSON, and
        the join's MCC rounded to :data:`MCC_PUBLISHED_DECIMALS` (``None`` when
        undefined), which the MCC family ranks on.

    Raises:
        ConfusionGateError: on a geometric shortfall, or when the per-tile
            labels disagree with the scorer's aggregate under the same join.
    """
    aggregate = calculate_tile_classification(
        gdf_det, gdf_ref, gdf_bounds, tile_join=tile_join,
    )
    if "error" in aggregate:
        raise ConfusionGateError(
            f"{label}: tile join '{tile_join}' refused "
            f"({aggregate.get('reason')}): {aggregate['error']}"
        )
    recorded = {k: int(aggregate[k]) for k in ("tp", "tn", "fp", "fn")}
    mcc_aggregate = aggregate.get("mcc")
    mcc_join = (None if mcc_aggregate is None
                else round(float(mcc_aggregate), MCC_PUBLISHED_DECIMALS))
    gate = check_confusion_gate(
        label, rebuilt, recorded,
        mcc_rebuilt,
        mcc_join,
        geometry_check=join_diagnostics,
    )
    gate.update({
        "tile_join": tile_join,
        "reference": (
            f"calculate_tile_classification under '{tile_join}' on the same "
            f"detections: the evaluation records another join, so this gate "
            f"checks the per-tile alignment and the booking invariant; the "
            f"committed record was reproduced under its own join first "
            f"(validation)"
        ),
    })
    return gate, mcc_join


#: Explicit schema translations for :func:`compare_present` (Astra R2-1).
#: A field the RECORD holds must be present in the replay; the only escape
#: is an entry here, keyed by the record's dotted path and naming the
#: replay's field (dotted, from the replay block's root) that carries the
#: same quantity under a later schema. Empty on purpose: a survey of the
#: 2,763 ``evaluation.json`` files under ``results/``, ``outputs/`` and
#: ``reports/`` in zbook's main checkout (2026-11-19) found
#: every recorded ``tile_join_diagnostics``, ``detection_scope`` and
#: ``tile_join_withheld`` field the single-set replay compares also in the
#: replay's schema (``detection_scope.n_passes`` exists only in multi-pass
#: rollups, which this replay does not cover). Add an entry only with a
#: written rationale beside it.
REPLAY_SCHEMA_TRANSLATIONS: dict[str, str] = {}


def _lookup(block: Any, dotted: str) -> tuple[bool, Any]:
    """Follow a dotted path through nested dicts: ``(found, value)``."""
    node = block
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return False, None
        node = node[part]
    return True, node


def compare_present(recorded: Any, replay: Any, where: str = "",
                    _root: Any = None) -> tuple[list[str], list[str], list[str]]:
    """Compare every field the RECORD holds with the replay's.

    Astra W1-C4: a recorded refusal (or diagnostic block) is reproduced only
    when every count it records reproduces, not merely its reason. Astra
    R2-1: the comparison is one-sided in the record's favour, never the
    replay's —

    * a field the record holds with a value is compared, and a field (or a
      whole block) the record holds but the replay LACKS is a mismatch,
      unless :data:`REPLAY_SCHEMA_TRANSLATIONS` names the replay field that
      carries it, which is then compared in its place;
    * a field the record holds as ``null`` (an old record that did not
      measure it) is NOT comparable, and is listed as such, never counted
      as compared;
    * a field only the replay has is not invented into the record (it is
      what a newer schema added);
    * list values (descriptive samples, not counts) must be present, but
      are not compared.

    Args:
        recorded: The committed block (dict, list or scalar).
        replay: The replay's block of the same shape.
        where: The dotted path, for messages.
        _root: The replay's root block, for translations (internal).

    Returns:
        ``(compared, mismatches, not_comparable)``: dotted paths compared,
        one message per field that differs or is missing from the replay,
        and the dotted paths the record holds as ``null``.
    """
    root = replay if _root is None else _root
    compared: list[str] = []
    mismatches: list[str] = []
    not_comparable: list[str] = []
    if isinstance(recorded, dict):
        if not isinstance(replay, dict):
            return compared, [f"{where or '.'}: the replay has no block here"], []
        for key, value in recorded.items():
            path = f"{where}.{key}" if where else key
            if value is None:
                not_comparable.append(path)
                continue
            if key in replay:
                counterpart = replay[key]
            elif path in REPLAY_SCHEMA_TRANSLATIONS:
                found, counterpart = _lookup(root, REPLAY_SCHEMA_TRANSLATIONS[path])
                if not found:
                    mismatches.append(
                        f"{path}: recorded {value!r}, and the replay lacks both "
                        f"it and its translation {REPLAY_SCHEMA_TRANSLATIONS[path]}")
                    continue
            else:
                mismatches.append(f"{path}: recorded {value!r}, the replay lacks "
                                  f"this field")
                continue
            c, m, n = compare_present(value, counterpart, path, root)
            compared += c
            mismatches += m
            not_comparable += n
        return compared, mismatches, not_comparable
    if isinstance(recorded, (list, tuple)) or isinstance(replay, (list, tuple)):
        return compared, mismatches, not_comparable  # descriptive, not counts
    if isinstance(recorded, bool) or isinstance(recorded, (int, float, str)):
        compared.append(where)
        if recorded != replay:
            mismatches.append(f"{where}: recorded {recorded!r}, replay {replay!r}")
    return compared, mismatches, not_comparable


def validate_detection_scope(label: str, gdf_det: gpd.GeoDataFrame,
                             gdf_bounds: gpd.GeoDataFrame, evaluation: dict) -> dict:
    """Reproduce the committed ``detection_scope`` counts (Astra W1-C4).

    Args:
        label: Cell label.
        gdf_det: The cell's detections.
        gdf_bounds: The frame.
        evaluation: The committed evaluation.

    Returns:
        ``{"compared": [...]}``, or ``{"status": "not recorded"}``.

    Raises:
        ReproductionDriftError: If a recorded count does not reproduce.
    """
    recorded = (evaluation.get("summary") or {}).get("detection_scope")
    if not isinstance(recorded, dict):
        return {"status": "not recorded"}
    try:  # imported as scripts.<module> (tests) or run as a script
        from scripts.evaluate_detections import describe_detection_scope  # noqa: PLC0415
    except ImportError:
        from evaluate_detections import describe_detection_scope  # noqa: PLC0415

    compared, mismatches, not_comparable = compare_present(
        recorded, describe_detection_scope(gdf_det, gdf_bounds), "detection_scope")
    if mismatches:
        raise ReproductionDriftError(f"{label}: " + "; ".join(mismatches))
    return {"compared": compared, "not_comparable": not_comparable}


def validate_recorded_classification(
    label: str,
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    evaluation: dict,
    recorded_join: str,
    expected_refusal: str | None = None,
) -> dict:
    """Step 1 of the two computations: reproduce a committed tile record.

    The committed ``tile_classification`` is rebuilt under the classification
    join the evaluation RECORDED (:func:`recorded_tile_joins`), never under the
    requested one, and must reproduce exactly:

    * a committed confusion and MCC: through :func:`check_confusion_gate`,
      geometric arm included — the gate a default run always applied;
    * a committed WITHHELD block (a recorded refusal): the replay must refuse
      with the same reason. A refusal is reproduced, never bypassed to
      manufacture a confusion (the specification's W1.4);
    * a committed confusion that predates the tile-join invariant, which
      the replay now refuses: accepted only when the caller passes that
      refusal as ``expected_refusal`` (an explicit, verified input, such as
      a committed tiering's ``withheld_cells``; Astra's W1-C2 and W1-C3).

    Every other outcome — a different confusion or MCC, an unexpected
    refusal, or no historical block at all — is a reproduction failure and
    raises :class:`ReproductionDriftError`, which no withholding handler
    catches (audit A-L6; Astra W1-C3).

    Args:
        label: Cell label, for messages.
        gdf_det: The cell's detections.
        gdf_ref: References.
        gdf_bounds: The frame.
        evaluation: The parsed committed ``evaluation.json``.
        recorded_join: The classification join the evaluation recorded.
        expected_refusal: A refusal reason the caller has verified this cell's
            replay should end in, or ``None``.

    Returns:
        A validation record (``recorded_join``, ``passed``, and either the
        gate record or ``expected_refusal``).

    Raises:
        ReproductionDriftError: If the replay does not reproduce the record,
            or there is no historical block (a stop, never a withholding).
    """
    block = (evaluation.get("summary") or {}).get("tile_classification")
    if not isinstance(block, dict):
        raise ReproductionDriftError(
            f"{label}: evaluation records no tile_classification block, so its "
            f"record cannot be validated before a new join is computed"
        )
    replay = calculate_tile_classification(
        gdf_det, gdf_ref, gdf_bounds, tile_join=recorded_join,
    )
    if block.get("withheld"):
        expected = block.get("withheld_reason")
        if "error" in replay and replay.get("reason") == expected:
            # W1-C4: the reason alone is not a reproduction; every count the
            # committed refusal records must reproduce too, and a count the
            # record holds that the replay no longer emits is a failure, not
            # a skip (R2-1). A record with no diagnostics at all (an old
            # one) has nothing comparable, and says so.
            recorded_diag = block.get("tile_join_diagnostics")
            if recorded_diag is None:
                compared, mismatches = [], []
                not_comparable = ["tile_join_diagnostics"]
            else:
                compared, mismatches, not_comparable = compare_present(
                    recorded_diag, replay.get("tile_join_diagnostics"),
                    "tile_join_diagnostics")
            if mismatches:
                raise ReproductionDriftError(
                    f"{label}: the recorded refusal ({expected}) reproduces in "
                    f"reason but not in its counts: " + "; ".join(mismatches))
            return {"recorded_join": recorded_join, "passed": True,
                    "expected_refusal": expected, "compared": compared,
                    "not_comparable": not_comparable}
        raise ReproductionDriftError(
            f"{label}: the committed record is a refusal ({expected}) under "
            f"'{recorded_join}', but the replay gave "
            f"{replay.get('reason') if 'error' in replay else 'a confusion'}"
        )
    if "error" in replay and expected_refusal is not None \
            and replay.get("reason") == expected_refusal:
        return {"recorded_join": recorded_join, "passed": True,
                "expected_refusal": expected_refusal,
                "expected_refusal_source": "caller (verified input)"}
    if "error" in replay:
        raise ReproductionDriftError(
            f"{label}: replay under the recorded join '{recorded_join}' refused "
            f"({replay.get('reason')}) where the committed record has a confusion"
        )
    rebuilt = {k: int(replay[k]) for k in ("tp", "tn", "fp", "fn")}
    mcc = replay.get("mcc")
    recorded_mcc = block.get("mcc")
    if isinstance(recorded_mcc, dict):
        recorded_mcc = recorded_mcc.get("point")
    conf = block.get("confusion")
    recorded = ({k: int(conf[k]) for k in ("tp", "tn", "fp", "fn") if k in conf}
                if isinstance(conf, dict) else None)
    if recorded is None:
        raise ReproductionDriftError(
            f"{label}: evaluation records no tile_classification.confusion, so "
            f"its record cannot be validated")
    try:
        gate = check_confusion_gate(
            label, rebuilt, recorded,
            None if mcc is None else float(mcc), recorded_mcc,
            geometry_check=replay.get("tile_join_diagnostics"),
        )
    except ConfusionGateError as error:
        raise ReproductionDriftError(f"reproduction drift: {error}") from error
    return {"recorded_join": recorded_join, **gate}


def refusal_code(error: Exception | str) -> str | None:
    """The tile-join refusal code a message carries, or ``None``."""
    text = str(error)
    return next((c for c in TILE_JOIN_REFUSAL_CODES if c in text), None)


#: The rules every pre-Wave-1 record was scored under; an expected refusal
#: licenses a replay under these rules only (RA-M5).
LEGACY_JOINS = (TILE_JOIN_LEGACY_CLASSIFICATION, TILE_JOIN_LEGACY_COUNT_TABLE)


def expected_refusals_from(path: Path, analysis_id: str) -> dict[str, str]:
    """Read verified expected refusals, with their provenance checked (RA-M5).

    An expected refusal licenses a cell's replay under its RECORDED rules to
    refuse. It is accepted only from a source that says which board and
    which rules it describes, and they must be this board and the legacy
    rules every pre-Wave-1 record was scored under:

    * a committed tiering: its ``analysis_id`` must be ``analysis_id``, its
      recorded rules (:func:`recorded_output_joins`; a tiering older than
      the provenance block is the legacy pair) must be the legacy pair, and
      a withheld cell that records its ``count_table_join`` must record the
      legacy one;
    * an explicit file ``{"analysis_id", "tile_joins": {"classification",
      "count_table"}, "expected_refusals": {ref: code}}``: the same checks,
      with ``tile_joins`` required. A bare ``{ref: code}`` mapping carries no
      provenance and is refused.

    Args:
        path: The JSON file.
        analysis_id: The board being replayed.

    Returns:
        Condition ref to refusal code.

    Raises:
        ValueError: On missing or mismatched provenance, or a reason that
            carries no recognised refusal code.
    """
    data = json.loads(path.read_text())
    if "withheld_cells" in data:
        cells = [(c.get("ref"), c.get("reason", ""), c.get("count_table_join"))
                 for c in data["withheld_cells"]]
        joins = recorded_output_joins(data)
    elif isinstance(data.get("expected_refusals"), dict):
        if not isinstance(data.get("tile_joins"), dict):
            raise ValueError(f"{path}: an expected-refusals file must record the "
                             f"tile_joins its refusals were observed under")
        cells = [(ref, code, None) for ref, code in data["expected_refusals"].items()]
        joins = (data["tile_joins"].get("classification"),
                 data["tile_joins"].get("count_table"))
    else:
        raise ValueError(f"{path}: neither a tiering's withheld_cells nor an "
                         f"expected_refusals block with provenance; a bare "
                         f"{{ref: code}} mapping is not accepted")
    if data.get("analysis_id") != analysis_id:
        raise ValueError(f"{path}: describes analysis {data.get('analysis_id')!r}, "
                         f"not {analysis_id!r}")
    if tuple(joins) != LEGACY_JOINS:
        raise ValueError(f"{path}: its refusals were observed under {tuple(joins)}, "
                         f"not the legacy rules {LEGACY_JOINS} the records were "
                         f"scored under")
    out: dict[str, str] = {}
    for ref, reason, ct in cells:
        if ct is not None and ct != TILE_JOIN_LEGACY_COUNT_TABLE:
            raise ValueError(f"{path}: withheld cell {ref} was refused under the "
                             f"count table {ct!r}, not the legacy one")
        code = refusal_code(str(reason))
        if code is None:
            raise ValueError(f"{path}: withheld cell {ref} has no "
                             f"refusal code in its reason")
        out[str(ref)] = code
    return out


def recorded_refusal(evaluation: dict) -> str | None:
    """The refusal code an evaluation itself records, or ``None``."""
    summary = evaluation.get("summary") or {}
    withheld = summary.get("tile_join_withheld") or {}
    if withheld.get("reason"):
        return str(withheld["reason"])
    block = summary.get("tile_classification") or {}
    if isinstance(block, dict) and block.get("withheld_reason"):
        return str(block["withheld_reason"])
    return None


def verify_input_identity(label: str, evaluation: dict, cli: dict,
                          overridden: set[str]) -> dict:
    """Check the inputs a cell will read are the bytes its evaluation scored.

    Evaluations from ``metadata_version`` 1.4 record a git blob hash per
    input (``_metadata.input_git_state.blob_hashes``). Each recorded input
    this harness will read (detections, and the reference and bounds unless
    overridden on the command line) must still hash the same; a mismatch is
    reproduction drift, fatal. An evaluation that records no hashes is
    historical and cannot be checked; the record says so.

    Args:
        label: Cell label, for messages.
        evaluation: The parsed committed ``evaluation.json``.
        cli: The cell's recipe (``cli_args``).
        overridden: ``{"ground_truth", "bounds"}`` members overridden here.

    Re-audit (Low, absent-as-agreement): ``verified`` now means the files
    the replay READS were checked. A single-set cell's detections must be
    covered by a recorded hash, under their own path or as the tail of a
    snapshot path the evaluation hashed (``.../blobs/<commit>/<path>``),
    and the file read must hash to it; hashes that name only other files
    are drift. A record whose every hash is null checked nothing, and says
    ``not recorded`` rather than ``verified``.

    Returns:
        ``{"status": "verified" | "not recorded", "n_files": ...}``.

    Raises:
        ReproductionDriftError: On a hash mismatch, or recorded hashes that
            do not cover the detections this replay reads.
    """
    hashes = (((evaluation.get("_metadata") or {}).get("input_git_state") or {})
              .get("blob_hashes") or {})
    if not hashes:
        return {"status": "not recorded", "n_files": 0}
    skip = {str(cli.get(key)) for key in overridden if cli.get(key)}
    checked = 0
    for rel, recorded in hashes.items():
        if recorded is None or rel in skip:
            continue
        current = git_blob_hash(BASE_DIR / rel)
        if current != recorded:
            raise ReproductionDriftError(
                f"{label}: input {rel} hashes {current}, the evaluation recorded "
                f"{recorded}; the cell's inputs are not the ones it scored")
        checked += 1
    if checked == 0:
        return {"status": "not recorded", "n_files": 0,
                "note": "every recorded hash is null"}
    det = cli.get("detections")
    reads = [str(d) for d in (det if isinstance(det, list) else [det] if det else [])]
    for rel in reads:
        key = rel if rel in hashes else next(
            (k for k in hashes if str(k).endswith("/" + rel.lstrip("/"))), None)
        if key is None or hashes[key] is None:
            raise ReproductionDriftError(
                f"{label}: the evaluation's recorded hashes do not cover the "
                f"detections this replay reads ({rel})")
        current = git_blob_hash(BASE_DIR / rel)
        if current != hashes[key]:
            raise ReproductionDriftError(
                f"{label}: detections {rel} hash {current}, the evaluation "
                f"recorded {hashes[key]} for {key}")
    return {"status": "verified", "n_files": checked,
            "detections_covered": len(reads)}


def validate_recorded_count_table(
    label: str,
    cli: dict,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_order: list[str],
    buffer_metres: int,
    eval_path: Path,
    evaluation: dict,
    recorded_join: str,
    expected_refusal: str | None,
    recorded_classification: str = "id",
) -> dict:
    """Step 1 for the F1 arm: replay the committed per-tile table numerically.

    The per-tile table is rebuilt under the count-table rule the evaluation
    recorded (legacy ``id`` when it records none) BEFORE any table is built
    under the requested rule (Astra W1-C2). It must reproduce:

    * a recorded refusal (the evaluation's own, or ``expected_refusal``, a
      verified caller input): the replay must refuse with that code;
    * otherwise a table: the replay must not refuse, the evaluation must not
      record a refusal, and for a single-set cell the micro-F1 of the table
      must equal the committed F1 at ``buffer_metres`` to its four decimals.
      A replicate-mean cell's committed F1 is the mean of per-pass F1s,
      which the pass-averaged table's micro-F1 does not equal, so each pass
      is replayed and the record's per-pass F1s and their mean are compared
      (:func:`_validate_replicate_mean_f1`; Astra R2-3). A record whose
      ``per_run`` count differs from the replay's pass count is drift; a
      record this replay cannot reconstruct is held
      (:class:`ReplayRouteUnsupportedError`), never passed.

    On the expected-refusal route (W1-C4, W1.4) a single-set cell must also
    reproduce its unaffected point values (F1, precision and recall at
    ``buffer_metres``) and every count of its recorded refusal record
    (``summary.tile_join_withheld.shortfall``), replayed by the probe the
    evaluator used: the classification join when the count table is ``id``,
    as before Wave 1, else the count-table join.

    Args:
        label: Cell label.
        cli: The cell's recipe.
        gdf_ref: References.
        gdf_bounds: The frame.
        tile_order: Tile order.
        buffer_metres: The F1 buffer.
        eval_path: The committed evaluation's path.
        evaluation: The parsed evaluation.
        recorded_join: The count-table rule the evaluation recorded.
        expected_refusal: A verified expected refusal code, or ``None``.
        recorded_classification: The classification join the evaluation
            recorded (the historical probe's join for an ``id`` table).

    Returns:
        The validation record.

    Raises:
        ReproductionDriftError: On any failure to reproduce.
    """
    own = recorded_refusal(evaluation)
    expected = own or expected_refusal
    per_pass: list[dict] = []
    try:
        tp, fp, fn, n_passes = cell_per_tile(cli, gdf_ref, gdf_bounds, tile_order,
                                             buffer_metres, recorded_join,
                                             per_pass=per_pass)
    except (ValueError, ConfusionGateError) as error:
        code = refusal_code(error)
        if code is not None and code == expected:
            record = {"recorded_join": recorded_join, "passed": True,
                      "expected_refusal": code,
                      "expected_refusal_source": ("evaluation" if own else
                                                  "caller (verified input)")}
            record.update(_reproduce_refused_cell(
                label, cli, gdf_ref, gdf_bounds, buffer_metres, evaluation,
                recorded_join, recorded_classification))
            return record
        if code is not None:
            raise ReproductionDriftError(
                f"{label}: replay of the count table under the recorded rule "
                f"'{recorded_join}' refused ({code}); expected "
                f"{expected or 'a table'}") from error
        raise
    if own is not None:
        raise ReproductionDriftError(
            f"{label}: the evaluation records a refusal ({own}), but the count "
            f"table replays under '{recorded_join}'")
    record = {"recorded_join": recorded_join, "passed": True, "n_passes": n_passes}
    per_run = evaluation.get("per_run")
    if isinstance(per_run, list) and len(per_run) != n_passes:
        raise ReproductionDriftError(
            f"{label}: the evaluation averages {len(per_run)} passes, the "
            f"replay under '{recorded_join}' scores {n_passes}")
    if n_passes == 1:
        eval_f1 = board_f1_at_20m(eval_path, buffer_metres)
        replay_f1 = micro_f1(tp.sum(), fp.sum(), fn.sum())
        record.update(eval_f1=eval_f1, replay_f1=round(replay_f1, 6))
        if abs(replay_f1 - eval_f1) > 5e-5:
            raise ReproductionDriftError(
                f"{label}: the count table replayed under '{recorded_join}' gives "
                f"micro-F1 {replay_f1:.6f}, the evaluation records {eval_f1:.4f}")
    else:
        record.update(_validate_replicate_mean_f1(
            label, eval_path, evaluation, per_pass, buffer_metres, recorded_join))
    return record


def _validate_replicate_mean_f1(label: str, eval_path: Path, evaluation: dict,
                                per_pass: list[dict], buffer_metres: int,
                                recorded_join: str) -> dict:
    """Reconstruct a replicate-mean cell's committed F1 pass by pass (R2-3).

    ``evaluate_multi_run_mean`` publishes the arithmetic mean of the
    per-pass F1s (each rounded to 4 dp), NOT the micro-F1 of the
    pass-averaged count table, so the table cannot be compared with it.
    This rebuilds the statistic the record holds instead: each pass's
    whole-frame micro-F1 under the recorded count-table rule, matched to
    the record's ``per_run`` F1s, and their mean against the committed
    summary F1. Passes are matched as sorted values, since their labels
    (file stems) need not be unique; sorted pairing is the matching that
    minimises the largest difference, so no valid pairing is missed.

    Args:
        label: Cell label.
        eval_path: The committed evaluation's path.
        evaluation: The parsed evaluation.
        per_pass: Per-pass whole-frame totals from :func:`cell_per_tile`.
        buffer_metres: The F1 buffer.
        recorded_join: The recorded count-table rule (for messages).

    Returns:
        The F1 part of the validation record.

    Raises:
        ReplayRouteUnsupportedError: If the record was written by another
            writer (a native adapter) or keeps no ``per_run`` block.
        ReproductionDriftError: If a pass's F1 or the mean does not reproduce.
    """
    writer = (evaluation.get("_metadata") or {}).get("script_path")
    per_run = evaluation.get("per_run")
    if not writer or Path(str(writer)).name != EVALUATOR_SCRIPT_NAME:
        raise ReplayRouteUnsupportedError(
            f"{label}: a replicate-mean record written by {writer!r}, not "
            f"{EVALUATOR_SCRIPT_NAME}, cannot be reconstructed by this replay; "
            f"it is held for its own replay route, not passed")
    if not isinstance(per_run, list):
        raise ReplayRouteUnsupportedError(
            f"{label}: a replicate-mean record ({len(per_pass)} passes) with no "
            f"per_run block has no per-pass F1 to reconstruct; it is held for "
            f"its own replay route, not passed")
    try:
        recorded = sorted(
            float(next(b["f1"] for b in run["buffers"]
                       if b.get("buffer_metres") == buffer_metres))
            for run in per_run)
    except (StopIteration, KeyError, TypeError) as error:
        raise ReproductionDriftError(
            f"{label}: a per_run entry records no F1 at {buffer_metres} m") from error
    replay = sorted(micro_f1(p["tp"], p["fp"], p["fn"]) for p in per_pass)
    differing = [f"recorded {r:.4f}, replay {q:.6f}" for r, q in zip(recorded, replay)
                 if abs(q - r) > F1_RECORD_TOL]
    if differing:
        raise ReproductionDriftError(
            f"{label}: replayed under '{recorded_join}', {len(differing)} of "
            f"{len(per_pass)} passes' F1 do not reproduce: " + "; ".join(differing))
    eval_f1 = board_f1_at_20m(eval_path, buffer_metres)
    replay_mean = float(np.mean([round(q, 4) for q in replay]))
    if abs(replay_mean - eval_f1) > F1_MEAN_TOL:
        raise ReproductionDriftError(
            f"{label}: the mean of the replayed per-pass F1s is "
            f"{replay_mean:.6f}, the evaluation records {eval_f1:.4f}")
    return {"f1_check": "per-pass F1 and their mean (replicate-mean cell)",
            "eval_f1": eval_f1, "replay_mean_f1": round(replay_mean, 6),
            "per_pass_eval_f1": recorded,
            "per_pass_replay_f1": [round(q, 6) for q in replay]}


def _reproduce_refused_cell(label: str, cli: dict, gdf_ref: gpd.GeoDataFrame,
                            gdf_bounds: gpd.GeoDataFrame, buffer_metres: int,
                            evaluation: dict, recorded_join: str,
                            recorded_classification: str) -> dict:
    """Point values and refusal counts of a refused single-set cell (W1-C4).

    Args:
        label: Cell label.
        cli: The recipe.
        gdf_ref: References.
        gdf_bounds: The frame.
        buffer_metres: The buffer whose point values are checked.
        evaluation: The committed evaluation.
        recorded_join: The recorded count-table rule.
        recorded_classification: The recorded classification join.

    Returns:
        What was compared (or why nothing could be).

    Raises:
        ReproductionDriftError: If a point value or a recorded count differs.
    """
    if not cli.get("detections"):
        return {"point_check": "not applicable: replicate-mean cell"}
    gdf_det = cell_detections(cli, gdf_bounds)
    out: dict = {}
    row = next((b for b in (evaluation.get("summary") or {}).get("buffers") or []
                if b.get("buffer_metres") == buffer_metres), None)
    if row is not None:
        p, r, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds,
                                         buffer_metres=buffer_metres)
        replay = {"f1": round(f1, 4), "precision": round(p, 4), "recall": round(r, 4)}
        compared, mismatches, not_comparable = compare_present(
            {k: row.get(k) for k in replay}, replay, "point")
        if mismatches:
            raise ReproductionDriftError(f"{label}: " + "; ".join(mismatches))
        out["point_compared"] = compared
        out["point_not_comparable"] = not_comparable
    else:
        # Re-audit Low: an absent row is said, never an empty record.
        out["point_check"] = (f"not comparable: the evaluation records no "
                              f"buffer row at {buffer_metres} m")
    withheld = (evaluation.get("summary") or {}).get("tile_join_withheld") or {}
    if not withheld:
        out["refusal_check"] = ("not comparable: the evaluation records no "
                                "tile_join_withheld block (a pre-invariant "
                                "record; the refusal is the caller's verified "
                                "expected refusal)")
    if withheld:
        probe_join = recorded_classification if recorded_join == "id" else recorded_join
        replay = describe_tile_join_refusal(gdf_det, gdf_ref, gdf_bounds, probe_join) or {}
        compared, mismatches, not_comparable = compare_present(
            {"reason": withheld.get("reason"), "shortfall": withheld.get("shortfall")},
            {"reason": replay.get("reason"), "shortfall": replay.get("shortfall")},
            "tile_join_withheld")
        if mismatches:
            raise ReproductionDriftError(
                f"{label}: the recorded refusal does not reproduce: "
                + "; ".join(mismatches))
        out["refusal_compared"] = compared
        out["refusal_not_comparable"] = not_comparable
    return out


#: Reason codes the tile-join invariant stamps into its refusal messages. A
#: ``ValueError`` carrying one of these is a REFUSAL — the cell's per-tile table
#: does not describe this frame — and is distinguishable from every other
#: ``ValueError`` the per-tile path can raise (an un-scoreable cell, a missing
#: file), which must still fail loud.
TILE_JOIN_REFUSAL_CODES = (
    TILE_JOIN_REASON_DETECTION_SHORTFALL,
    TILE_JOIN_REASON_REFERENCE_SHORTFALL,
    TILE_JOIN_REASON_NO_SOURCE_TILE,
    TILE_JOIN_REASON_UNATTRIBUTED_DETECTION,
    # RA-M1: the in-frame reference with no recorded sheet (Wave 1) is a
    # refusal too; without it a board raised instead of withholding.
    TILE_JOIN_REASON_UNATTRIBUTED_REFERENCE,
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
    count_table_join: str = TILE_JOIN_COUNT_TABLE_DEFAULT,
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
        count_table_join: The F1 arm's count-table join, the rule whose
            refusal this describes (Wave 1: the record names the purpose and
            rule of the computation it guards, never another one).

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
            gdf_det, gdf_ref, gdf_bounds, count_table_join
        )
    except (ValueError, KeyError):
        return None


def mcc_point(cell: dict) -> float | None:
    """A cell's tile-MCC point estimate, from its evaluation or its arrays.

    ``cell["mcc"]`` is the committed, gate-checked number and is what the board
    publishes. A cell whose evaluation records no ``tile_classification`` still
    has one-hot arrays here (that is what the gate rebuilt), so the fallback
    recomputes the point rather than dropping the cell out of the MCC ordering.

    Since Wave 1, ``cell["mcc"]`` is always the MCC under the REQUESTED
    classification join: the committed number when the cell recorded that
    join (and passed the gate), the newly computed one otherwise
    (:func:`load_cells`). The ``mcc_join`` key of the 2026-10-30 sensitivity
    readings is gone, and with it any committed MCC beside new arrays.

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
    tile_join: str = TILE_JOIN_CLASSIFICATION_DEFAULT,
    count_table_join: str = TILE_JOIN_COUNT_TABLE_DEFAULT,
    expected_refusals: dict[str, str] | None = None,
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
        tile_join: The CLASSIFICATION join the MCC arm (``want_mcc``) books
            points to tiles with; one of
            ``lib_advanced_metrics.TILE_JOINS_CLASSIFICATION``. Two
            computations, in order (Wave 1): each cell's committed record is
            first validated under the join IT recorded
            (:func:`recorded_tile_joins`; a cell recording the requested join
            is gated against its committed confusion exactly as before; any
            other is reproduced by :func:`validate_recorded_classification`),
            and only then are its arrays and MCC computed under ``tile_join``
            (gated by :func:`join_sensitivity_gate`), the new MCC, at the
            committed four decimals, replacing the committed one in
            ``cell["mcc"]``. Without ``want_mcc`` a cell whose recorded join
            differs carries ``mcc: None`` and ``mcc_status``.
        count_table_join: The COUNT-TABLE join of the F1 arm's per-tile
            TP/FP/FN; one of ``lib_advanced_metrics.TILE_JOINS_COUNT_TABLE``.
        expected_refusals: Condition ref to the refusal code its replay under
            the recorded rules is verified to end in (a committed tiering's
            ``withheld_cells``, via :func:`expected_refusals_from`). Needed
            for cells whose evaluation predates the tile-join invariant and so
            records no refusal of its own.

    Order (Astra W1-C2, W1-C3): for every cell, BEFORE anything is built
    under the requested rules, (1) the inputs' recorded blob hashes are
    verified (:func:`verify_input_identity`); (2) where the evaluation
    recorded another count-table rule, its table is replayed under that
    rule (:func:`validate_recorded_count_table`); (3) with ``want_mcc`` and
    another recorded classification join, its tile record is replayed
    (:func:`validate_recorded_classification`). Any failure there raises
    :class:`ReproductionDriftError` and ends the run; it is never routed
    through the handlers that withhold a refused cell under the requested
    rules. Where the recorded rule IS the requested one, the one computation
    validates and computes at once, with the historical behaviour.

    Returns:
        ``(cells, gdf_ref, gdf_bounds, tile_order)``.

    Raises:
        ValueError: if the cells disagree on ground truth / bounds and no
            override is supplied (a silent-scope-mix guard); or if a cell's
            per-tile table cannot be built for any reason other than a
            tile-join refusal, or for that reason with no ``withheld`` sink;
            or if either join is named for the wrong purpose.
        TileJoinProvenanceError: if a cell's evaluation records
            contradictory tile-join provenance, or is a Wave-1 output without
            it (a ``ValueError`` subclass, raised regardless of ``withheld``).
    """
    check_tile_joins(tile_join, count_table_join)
    refs = load_board_refs(analyses_path, analysis_id)

    # First pass: resolve every cell's eval, collect (gt, bounds) declarations.
    resolved: list[dict] = []
    gts: set[str] = set()
    boundss: set[str] = set()
    for ref in refs:
        cond = resolve_condition(conditions_path, ref)
        eval_path = BASE_DIR / cond["eval_path"]
        evaluation = json.loads(eval_path.read_text())
        meta = evaluation["_metadata"]
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
        resolved.append({"ref": ref, "cond": cond, "eval_path": eval_path, "cli": cli,
                         "evaluation": evaluation,
                         # Step 1's input: the rules this evaluation recorded.
                         # Contradictory or missing-on-new provenance raises
                         # here, before any cell is scored.
                         "recorded": recorded_tile_joins(evaluation)})

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
    overridden = {name for name, value in (("ground_truth", gt_override),
                                           ("bounds", bounds_override))
                  if value is not None}
    for r in resolved:
        cond, eval_path, cli = r["cond"], r["eval_path"], r["cli"]
        recorded_join = r["recorded"]["classification"]
        recorded_ct = r["recorded"]["count_table"]
        same_join = recorded_join == tile_join
        expected = (expected_refusals or {}).get(r["ref"])
        if expected is not None and (recorded_join, recorded_ct) != LEGACY_JOINS:
            # RA-M5: an expected refusal licenses a replay under the legacy
            # rules only; a record under other rules carries its own refusal.
            raise ReproductionDriftError(
                f"{cond['label']}: an expected refusal was supplied, but the "
                f"evaluation records the rules ({recorded_join}, {recorded_ct})")
        # ── Step 1: validate the historical record, outside every handler
        # that withholds a cell under the requested rules (W1-C2, W1-C3).
        validation: dict = {"identity": verify_input_identity(
            cond["label"], r["evaluation"], cli, overridden)}
        # RA-M3 (with R2-2): every recorded arm is validated whenever EITHER
        # rule changes. A classification-only change used to skip the F1
        # arm, so a record whose F1 does not reproduce passed silently.
        rules_change = recorded_ct != count_table_join or not same_join
        if rules_change:
            validation["count_table"] = validate_recorded_count_table(
                cond["label"], cli, gdf_ref, gdf_bounds, tile_order,
                buffer_metres, eval_path, r["evaluation"], recorded_ct, expected,
                recorded_join)
        gdf_det_mcc = None
        if cli.get("detections") and rules_change:
            # The recorded scope counts reproduce too (W1-C4); single-set
            # cells only, whose one detection set the evaluation scoped.
            gdf_det_mcc = cell_detections(cli, gdf_bounds)
            validation["detection_scope"] = validate_detection_scope(
                cond["label"], gdf_det_mcc, gdf_bounds, r["evaluation"])
        # R2-2: the classification record is validated whenever EITHER rule
        # changes, not only the classification join. With the join unchanged
        # and only the count table new, the step-2 gate below sits inside the
        # handler that withholds, so a historical confusion mismatch would
        # otherwise surface as an ordinary withholding after the new count
        # table was computed, instead of stopping the run before it.
        if want_mcc and rules_change:
            if gdf_det_mcc is None:
                gdf_det_mcc = cell_detections(cli, gdf_bounds)
            validation["classification"] = validate_recorded_classification(
                cond["label"], gdf_det_mcc, gdf_ref, gdf_bounds,
                r["evaluation"], recorded_join, expected_refusal=expected)
        # ── Step 2: the analysed values, under the requested rules.
        # The tile-join invariant can refuse the F1 arm as well as the MCC arm:
        # a cell whose source_tile vocabulary is not this frame's has no
        # per-tile decomposition on it, only a sound whole-frame F1. When the
        # caller supplies a ``withheld`` sink, such a cell is WITHHELD from the
        # statistics and listed rather than aborting the board (PI ruling
        # 2026-09-13); without a sink the old fail-loud behaviour stands, which
        # is what every other caller of this function still wants.
        try:
            tp, fp, fn, n_passes = cell_per_tile(cli, gdf_ref, gdf_bounds,
                                                 tile_order, buffer_metres,
                                                 count_table_join)
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
                "disclosure": refusal_disclosure(cli, gdf_ref, gdf_bounds,
                                                 count_table_join),
                "count_table_join": count_table_join,
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
        # The committed MCC is the recorded join's. It may stand as the
        # cell's analysed MCC only when that is the requested join (and, with
        # want_mcc, only once the gate below has reproduced it).
        committed_mcc = (lambda m: round(float(m), 6) if m is not None else None)(
            read_tile_mcc(eval_path))
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
                "mcc": committed_mcc if same_join else None,
                "validation": validation,
            }
        )
        if not same_join and not want_mcc:
            cells[-1]["mcc_status"] = (
                f"not reported: the evaluation records the classification "
                f"join '{recorded_join}', the requested one is '{tile_join}', "
                f"and the MCC arm (--permute-mcc) was not run to recompute it"
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
                gdf_det = (gdf_det_mcc if gdf_det_mcc is not None
                           else cell_detections(cli, gdf_bounds))
                # Step 2: the analysed arrays, under the REQUESTED join (the
                # record was validated in step 1, above this handler).
                tp_c, tn_c, fp_c, fn_c, join_diagnostics = (
                    cell_per_tile_classification(
                        gdf_det, gdf_ref, gdf_bounds, tile_order,
                        tile_join=tile_join,
                    )
                )
                rebuilt = {"tp": int(tp_c.sum()), "tn": int(tn_c.sum()),
                           "fp": int(fp_c.sum()), "fn": int(fn_c.sum())}
                mcc_rebuilt = compute_mcc_or_none(**rebuilt)
                if same_join:
                    # The recorded join: one computation validates and
                    # computes at once — the committed-record gate, unchanged.
                    gate = check_confusion_gate(
                        cond["label"], rebuilt, read_tile_confusion(eval_path),
                        mcc_rebuilt,
                        cells[-1]["mcc"],
                        geometry_check=join_diagnostics,
                    )
                    if "classification" in validation:
                        gate["validation"] = validation["classification"]
                else:
                    gate, mcc_join = join_sensitivity_gate(
                        cond["label"], gdf_det, gdf_ref, gdf_bounds, rebuilt,
                        mcc_rebuilt, join_diagnostics, tile_join,
                    )
                    gate["validation"] = validation.get("classification")
                    cells[-1]["mcc"] = mcc_join
                gate["recorded_tile_joins"] = {
                    "classification": recorded_join,
                    "count_table": recorded_ct,
                }
            except ConfusionGateError as error:
                cells[-1].update({
                    "mcc_withheld": {
                        "recorded_mcc": committed_mcc,
                        "recorded_join": recorded_join,
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
        join_note = f" [{tile_join}]"
        print(
            f"  {kind:12s} {cond['label']:34s} passes={n_passes:2d} "
            f"eval-F1={cells[-1]['eval_f1']:.4f} "
            f"micro-F1-of-mean={cells[-1]['observed_micro_f1']:.4f} "
            f"gap={cells[-1]['f1_gap']:+.4f} MCC={cells[-1]['mcc']}{join_note}",
            flush=True,
        )
    return cells, gdf_ref, gdf_bounds, tile_order


def main() -> int:
    """CLI entry point: load the board, round-robin, tier, and write results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-id", type=str, default=None,
                        help="run-analyses.json analysis whose conditions_compared "
                             "defines the board membership. Required except for "
                             "--render-md / --check, which read a committed "
                             "tiering JSON instead of rebuilding a board.")
    parser.add_argument("--conditions", type=Path, default=DEFAULT_CONDITIONS)
    parser.add_argument("--analyses", type=Path, default=DEFAULT_ANALYSES)
    parser.add_argument("--ground-truth", type=Path, default=None,
                        help="Optional override; else derived from the cells' evals.")
    parser.add_argument("--bounds", type=Path, default=None,
                        help="Optional override; else derived from the cells' evals.")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Where the tiering JSON and Markdown are written. "
                             "Required except for --render-md / --check, which "
                             "take the board directory as their own argument.")
    parser.add_argument(
        "--render-md", type=Path, default=None, metavar="BOARD_DIR",
        help="Re-render tiering_<buffer>m.md from the COMMITTED "
             "tiering_<buffer>m.json in BOARD_DIR and exit. Recomputes "
             "nothing — no permutation, no evaluation, no detection file read "
             "— because the Markdown is a pure projection of that JSON.",
    )
    parser.add_argument(
        "--check", type=Path, default=None, metavar="BOARD_DIR",
        help="Drift guard: re-render tiering_<buffer>m.md from the committed "
             "JSON in memory and compare with the committed document, with the "
             "rendered-at-commit stamp neutralised. Exit 1 on drift.",
    )
    parser.add_argument("--n-permutations", type=int, default=N_PERMUTATIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument(
        "--buffer", type=int, default=HEADLINE_BUFFER_M,
        help="Buffer in metres the F1 statistic is computed at (default: "
             f"{HEADLINE_BUFFER_M}, the preregistered headline). A 55-map "
             "board's headline is 50.",
    )
    parser.add_argument(
        "--expected-refusals", type=Path, default=None,
        help="JSON of verified expected refusals: {ref: reason_code}, or a "
             "committed tiering whose withheld_cells list them. A cell whose "
             "replay under its recorded rules refuses is accepted only when "
             "its evaluation, or this file, records that refusal.",
    )
    parser.add_argument(
        "--overwrite-other-joins", action="store_true",
        help="Allow replacing an existing tiering JSON that records other "
             "tile-join rules (audit A-L5). Without it such a file is refused.",
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
    parser.add_argument(
        "--tile-join", choices=TILE_JOINS_CLASSIFICATION,
        default=TILE_JOIN_CLASSIFICATION_DEFAULT,
        help="CLASSIFICATION join of the MCC arm. Default "
             f"{TILE_JOIN_CLASSIFICATION_DEFAULT!r} (D72, D73). Each cell is "
             "first validated under the join its evaluation recorded, then "
             "computed under this one. Any other join than the default needs "
             "--permute-mcc and is stamped into the output name; pass 'id' "
             "(with --count-table-join id) to replay a committed tiering.",
    )
    parser.add_argument(
        "--count-table-join", choices=TILE_JOINS_COUNT_TABLE,
        default=TILE_JOIN_COUNT_TABLE_DEFAULT,
        help="COUNT-TABLE join of the F1 arm's per-tile TP/FP/FN. Default "
             f"{TILE_JOIN_COUNT_TABLE_DEFAULT!r} (D72 (2), D73 (2)). Every "
             "tiering before Wave 1 was built under 'id'. A non-default join "
             "is stamped into the output name as _ct-<join>.",
    )
    args = parser.parse_args()

    if args.check is not None:
        return check_rendering(args.check, args.buffer)
    if args.render_md is not None:
        path = write_markdown_from_json(args.render_md, args.buffer)
        print(f"rendered {path}", flush=True)
        return 0
    for name in ("analysis_id", "output_dir"):
        if getattr(args, name) is None:
            parser.error(f"--{name.replace('_', '-')} is required unless "
                         f"--render-md or --check is given")
    # The classification join only changes the MCC arm, so a non-default one
    # without that arm would write an F1 tiering under a name that claims
    # otherwise.
    if args.tile_join != TILE_JOIN_CLASSIFICATION_DEFAULT and not args.permute_mcc:
        parser.error("--tile-join other than the default changes only the MCC "
                     "arm; pass --permute-mcc with it")
    print(f"TILE JOINS: classification {args.tile_join!r} (MCC arm), count "
          f"table {args.count_table_join!r} (F1 arm)", flush=True)
    # Checked before any computation, so a refused run costs nothing.
    planned = tiering_stem(args.buffer, args.tile_join, args.count_table_join)
    refuse_overwrite_of_other_joins(
        args.output_dir / f"{planned}.json",
        args.tile_join, args.count_table_join, args.overwrite_other_joins)

    withheld_cells: list[dict] = []
    cells, _gdf_ref, _gdf_bounds, tile_order = load_cells(
        args.conditions, args.analyses, args.analysis_id,
        args.bounds, args.ground_truth, buffer_metres=args.buffer,
        want_mcc=args.permute_mcc,
        withheld=None if args.strict_tile_join else withheld_cells,
        tile_join=args.tile_join,
        count_table_join=args.count_table_join,
        expected_refusals=(expected_refusals_from(args.expected_refusals,
                                                  args.analysis_id)
                           if args.expected_refusals else None),
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
        # Wave 1 provenance: both rules, and the count-table rule the F1 arm
        # (and so ``pairwise`` and ``tiers``) was built under.
        "tile_joins": tile_join_provenance(args.tile_join, args.count_table_join),
        "count_table_join": args.count_table_join,
        # Step 1's record per cell: input identity, and each recorded arm
        # replayed under its own rule before the requested one was computed.
        "validation": {c["ref"]: c["validation"] for c in cells},
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
                **({"mcc_status": c["mcc_status"]} if "mcc_status" in c else {}),
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
        # Wave 1: always recorded, since no join is "the published one" by
        # omission any more. No committed MCC of another join is carried
        # beside the arrays computed here.
        block = result["mcc_permutation"]
        block["tile_join"] = args.tile_join
        block["tile_join_note"] = (
            f"The MCC arm books points to tiles under '{args.tile_join}'"
            + (" (the default, D72 and D73)"
               if args.tile_join == TILE_JOIN_CLASSIFICATION_DEFAULT
               else " (a replay or sensitivity reading, not the default)")
            + ". Each cell's committed record was validated under the join "
              "it recorded before its arrays were computed under this one "
              "(gates[ref].recorded_tile_joins)."
        )
    stem = tiering_stem(args.buffer, args.tile_join, args.count_table_join)
    json_path = args.output_dir / f"{stem}.json"
    json_path.write_text(json.dumps(result, indent=2))
    print(f"Wrote {json_path}", flush=True)

    md_path = args.output_dir / f"{stem}.md"
    md_path.write_text(render_markdown(result), encoding="utf-8")
    print(f"Wrote {md_path}", flush=True)
    return 0


#: Neutralises the render-time stamp for drift comparison: re-rendering at a
#: new commit must not read as drift when the projection is unchanged. The
#: *computed-at* commit is taken from the JSON and is deliberately NOT
#: neutralised — a board recomputed at a different commit IS a different board.
_RENDER_STAMP_RE = re.compile(r"rendered at commit `[^`]+`")


def tiering_paths(board_dir: Path, buffer_metres: int) -> tuple[Path, Path]:
    """Return the (JSON, Markdown) tiering paths for a board directory.

    Args:
        board_dir: Directory holding ``tiering_<buffer>m.json``.
        buffer_metres: The buffer the board's headline is computed at.

    Returns:
        Tuple of (JSON path, Markdown path).
    """
    return (board_dir / f"tiering_{buffer_metres}m.json",
            board_dir / f"tiering_{buffer_metres}m.md")


def write_markdown_from_json(board_dir: Path, buffer_metres: int) -> Path:
    """Re-render a board's tiering Markdown from its committed JSON.

    Args:
        board_dir: Directory holding the committed tiering JSON.
        buffer_metres: Buffer selecting the pair of files.

    Returns:
        The Markdown path written.

    Raises:
        SystemExit: If the JSON is absent.
    """
    json_path, md_path = tiering_paths(board_dir, buffer_metres)
    if not json_path.exists():
        raise SystemExit(f"no committed tiering JSON at {json_path}")
    result = json.loads(json_path.read_text(encoding="utf-8"))
    md_path.write_text(render_markdown(result), encoding="utf-8")
    return md_path


def check_rendering(board_dir: Path, buffer_metres: int) -> int:
    """Drift guard for a board's tiering Markdown.

    Args:
        board_dir: Directory holding the committed pair of files.
        buffer_metres: Buffer selecting the pair.

    Returns:
        Process exit code: 0 when the committed Markdown equals a
        rendering of the committed JSON (render stamp neutralised), 1 on
        drift or a missing file.
    """
    json_path, md_path = tiering_paths(board_dir, buffer_metres)
    for path in (json_path, md_path):
        if not path.exists():
            print(f"MISSING: {path}", file=sys.stderr)
            return 1
    result = json.loads(json_path.read_text(encoding="utf-8"))
    fresh = render_markdown(result)
    committed = md_path.read_text(encoding="utf-8")
    if _RENDER_STAMP_RE.sub("", committed) != _RENDER_STAMP_RE.sub("", fresh):
        print(f"DRIFT: {md_path} differs from a rendering of {json_path.name}",
              file=sys.stderr)
        print("Re-render with --render-md (the Markdown is a pure projection; "
              "no permutation is re-run).", file=sys.stderr)
        return 1
    print(f"{md_path.name} current: {len(result['ranking'])} ranked cell(s), "
          f"{len(result['tiers'])} tiers (render stamp neutralised)")
    return 0


def render_markdown(result: dict, source_commit: str | None = None) -> str:
    """Render the human-readable tiering Markdown from the tiering result.

    A pure projection of ``result`` — the same object written to
    ``tiering_<buffer>m.json`` — which is what lets ``--check`` verify the
    committed document without re-running a 10,000-permutation test. The
    rank table is read from ``result["ranking"]``, whose rows carry their
    own tier, so no ordering decision is made here.

    Args:
        result: The tiering result object (as written, or as committed).
        source_commit: Short hash to stamp as the render commit; defaults
            to HEAD. The commit the board was *computed* at comes from
            ``result["git_commit"]``.

    Returns:
        The full Markdown document, newline-terminated.
    """
    ordered = result["ranking"]
    n_sp = sum(1 for c in ordered if c["kind"] == "single-pass")
    n_con = sum(1 for c in ordered if c["kind"] == "consensus")
    n_pv = sum(1 for c in ordered if c["kind"] == "verified-PV")
    n_sig = sum(1 for r in result["pairwise"] if r["significant"])
    pv_frag = f" + {n_pv} verified-PV" if n_pv else ""
    json_name = f"tiering_{result['buffer_metres']}m.json"
    lines = [
        f"# Era-1 leaderboard — statistical tiering "
        f"({result['buffer_metres']} m) — `{result['analysis_id']}`",
        "",
        f"> **GENERATED FILE — do not hand-edit.** Rendered from `{json_name}` "
        f"by `scripts/era1_leaderboard_tiering.py`, computed at commit "
        f"`{result.get('git_commit', 'unknown')}` and rendered at commit "
        f"`{source_commit or git_commit()}`. Per the PI ruling of 2026-09-11 "
        f"(`docs/methodology/output-directory-standard.md` § \"Documents in "
        f"Revision Policy Scope\") this projection carries provenance instead "
        f"of a hand changelog: \"is this current?\" is answered by "
        f"`--check <board dir>` and its tier-1 test, and `--render-md <board "
        f"dir>` re-renders it from the committed JSON without re-running the "
        f"permutation.",
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
            f"{c['f1_gap']:+.3f} | {mcc} | {c['tier']} |"
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
        if mcc_block.get("tile_join"):
            # Absent from tierings written before Wave 1 under the then
            # default join, so a committed board re-renders exactly as
            # before; every Wave 1 tiering records it.
            lines += [f"- **Tile join**: `{mcc_block['tile_join']}` — "
                      f"{mcc_block['tile_join_note']}"]
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
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
