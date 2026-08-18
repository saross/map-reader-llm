#!/usr/bin/env python3
# ============================================================================
# dedup_metric_impact.py
# ----------------------------------------------------------------------------
# Measure the movement in BOTH headline metrics — micro-average F1 and
# tile-level Matthews Correlation Coefficient (MCC) — when the preregistered
# within-pass deduplication (preregistration § 8.5 Step 1, 20 m) is applied to
# a committed detection artefact that never received it.
#
# WHY THIS EXISTS
# ---------------
# ``reports/scoring-sensitivity-review-2026-08-18.md`` measured the F1 movement
# on 48 cells but explicitly did not measure MCC anywhere (its § 5 gap 4). MCC
# is NOT automatically invariant under deduplication: it classifies each tile as
# populated-or-not by ``gdf_det['source_tile'] == tile_name``
# (``lib_advanced_metrics.calculate_tile_classification``), so collapsing a
# cross-tile duplicate pair into one cluster can empty a tile and flip its
# predicted class. Whether that helps or hurts depends on whether the emptied
# tile held a reference mound, so the sign is an empirical question.
#
# THE ATTRIBUTION PROBLEM (the reason this script reports three MCC rules)
# -----------------------------------------------------------------------
# Deduplication returns a CLUSTER, not a detection, and a cluster spanning two
# overlapping tiles has no single source tile. ``merge_passes`` records the full
# ``source_tiles`` list; a scorer has to pick one. F1 is nearly insensitive to
# the pick (matching is scoped per MAP SHEET, and every tile contributing to a
# 20 m cluster belongs to the same sheet — verified per cell below). MCC is
# maximally sensitive to it. So this script reports the deduplicated MCC under
# three attribution rules:
#
#   ``first_source_tile``  the lexicographically first contributing tile — the
#                          rule ``scoring_sensitivity_probe.dedup_geodataframe``
#                          already uses, so ΔF1 here is comparable to the
#                          prior review's numbers cell for cell;
#   ``nearest_centroid``   the intersecting tile whose centroid is nearest the
#                          cluster centroid — the geometric rule
#                          ``lib_advanced_metrics._assign_refs_to_primary_tiles``
#                          already applies to REFERENCES;
#   ``union_contributing`` every contributing tile counts as predicted-populated
#                          — the membership-preserving rule, under which the
#                          tile-level question ("did the model detect anything
#                          in this tile?") is answered from the raw pass and is
#                          therefore invariant to deduplication by construction.
#
# The third rule is the interpretive anchor: any ΔMCC observed under the first
# two is an artefact of collapsing cluster provenance, not of removing false
# positives. Reporting all three separates the two effects.
#
# GATES
# -----
# 1. ``tile_confusion`` is checked against ``calculate_tile_classification``
#    (the committed scorer's own function) on the as-committed arm of the first
#    cell, so the fast set-based path is pinned to the slow authoritative loop.
# 2. Where a cell declares ``eval_path``, the as-committed F1 and MCC are
#    checked against that ``evaluation.json``; a mismatch is reported in the
#    output rather than silently tolerated.
#
# COST: US$0.00. Reads committed artefacts only; no API calls.
# COMPUTE: run on sapphire (project CLAUDE.md "Compute Location — CRITICAL").
#
# Usage:
#     python scripts/dedup_metric_impact.py \
#         --spec results/dedup-metric-impact-2026-08-18/spec-gs-384.json \
#         --output results/dedup-metric-impact-2026-08-18/impact-gs-384.json
#
# Author: Shawn Ross & Claude (Anthropic)
# Created: 2026-08-18 (Session 136)
# Licence: Apache 2.0
# ============================================================================

from __future__ import annotations

import argparse
import glob
import json
import logging
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_advanced_metrics import (  # noqa: E402
    calculate_f1_internal,
    calculate_tile_classification,
    get_map_name,
)
from scripts.merge_passes import (  # noqa: E402
    DISTANCE_THRESHOLD_METRES,
    deduplicate_within_pass,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: Evaluation CRS for every project vector (UTM zone 35N, Bulgaria).
EVALUATION_CRS = "EPSG:32635"

#: Default gold-standard ground truth (the 4-map GS corpus).
DEFAULT_GROUND_TRUTH = (
    PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
)

#: The three tile-attribution rules applied to a deduplicated cluster set.
ATTRIBUTION_RULES = ("first_source_tile", "nearest_centroid", "union_contributing")

#: Default conditions manifest used to resolve ``condition_id``-only cells.
DEFAULT_MANIFEST = PROJECT_ROOT / "results/conditions-manifest.json"

#: Glob a batch evaluation records when it was not given an explicit one.
DEFAULT_PASS_GLOB = "*/detections_*.geojson"

#: Both pass-file naming conventions in use across the corpus. Identical to
#: ``n1_baseline_leaderboard_tiering.PASS_GLOBS``, restated here so this module
#: does not import the leaderboard machinery just for a constant.
PASS_GLOBS = ("*/detections_*.geojson", "*/detections-*.geojson")


# ── Spec resolution ───────────────────────────────────────────────────

def resolve_from_manifest(
    condition_id: str,
    manifest_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Resolve a condition's scored inputs from the conditions manifest.

    Reproduces ``scoring_sensitivity_survey.resolve_detection_paths`` — walk
    ``provenance.source_files``, read each ``evaluation.json``'s ``_metadata``,
    and expand directory-mode inputs with the recorded ``--glob`` — so this
    script scores exactly the files the committed evaluation scored. The
    evaluation's own ``input_files.bounds`` is carried through too, because
    board membership spans 256 px, 384 px and 512 px scopes.

    Args:
        condition_id: ``<run>::<label>`` identifier.
        manifest_index: Map of condition_id to manifest entry.

    Returns:
        Dict with ``detections`` (sorted list), ``bounds``, ``eval_path``.

    Raises:
        KeyError: If the condition is absent from the manifest.
        FileNotFoundError: If no detection artefact resolves.
    """
    cond = manifest_index[condition_id]
    detections: list[str] = []
    bounds: str | None = None
    eval_path: str | None = None
    n_runs_expected = 0

    for src in (cond.get("provenance") or {}).get("source_files") or []:
        if not os.path.exists(src):
            continue
        ev = json.loads(Path(src).read_text())
        meta = ev.get("_metadata") or {}
        cli = meta.get("cli_args") or {}
        inputs = meta.get("input_files") or {}
        eval_path = eval_path or src
        bounds = bounds or inputs.get("bounds") or cli.get("bounds")
        pattern = cli.get("glob") or DEFAULT_PASS_GLOB
        value = inputs.get("detections")
        if value is None:
            value = cli.get("detections") or cli.get("detections_dir")
        if isinstance(value, str):
            value = [value]
        for path in value or []:
            if os.path.isdir(path):
                # Expand with the recorded glob AND the hyphenated variant.
                # Pass files are named ``detections_<label>_runNN.geojson`` in
                # some runs and ``detections-<config>-<date>.geojson`` in
                # others, and a batch evaluation records only the CLI DEFAULT
                # glob, not the per-condition pattern from its YAML. Expanding
                # with one pattern alone silently drops the passes named the
                # other way — which is exactly how the Session 136 exposure
                # survey came to score
                # ``pv-diag-384::baseline-pro-text-medium-t-0-0`` on 1 of its 3
                # passes. ``n1_baseline_leaderboard_tiering.PASS_GLOBS`` already
                # unions both patterns; this matches it.
                patterns = {pattern, *PASS_GLOBS}
                hits = sorted(
                    {h for g in patterns for h in glob.glob(os.path.join(path, g))}
                )
                if not hits:
                    hits = sorted(
                        glob.glob(os.path.join(path, "*/detections*.geojson"))
                    )
                detections.extend(hits)
            elif os.path.isfile(path):
                detections.append(path)
            n_runs_expected += _n_runs(ev)

    if not detections:
        raise FileNotFoundError(
            f"{condition_id}: no detection artefact resolved from provenance"
        )
    return {
        "detections": sorted(set(detections)),
        "bounds": bounds,
        "eval_path": eval_path,
        "n_runs_expected": n_runs_expected,
    }


def _n_runs(ev: dict[str, Any]) -> int:
    """Number of replicate runs a committed evaluation record aggregated.

    ``evaluate_detections`` writes one ``per_run`` entry per scored artefact
    and reports ``summary.n_runs``; either is a sufficient statement of how
    many files the committed number averaged over.

    Args:
        ev: Parsed ``evaluation.json``.

    Returns:
        The recorded run count, or 0 when the record does not state one.
    """
    summary = ev.get("summary") or {}
    if isinstance(summary.get("n_runs"), int):
        return summary["n_runs"]
    return len(ev.get("per_run") or [])


def resolve_cell(
    cell: dict[str, Any],
    manifest_index: dict[str, dict[str, Any]],
    default_bounds: str | None,
) -> dict[str, Any]:
    """Fill a spec cell's missing input paths and choose its tile-source mode.

    A spec entry may give only ``name`` and ``condition_id``; everything else
    is resolved from the manifest. ``tile_source`` defaults to ``"property"``
    when the first detection artefact carries a ``source_tile`` column and to
    ``"derive"`` otherwise — the latter being the aggregated-artefact case,
    where the committed scorer derives a tile itself.

    Args:
        cell: Raw spec entry.
        manifest_index: Map of condition_id to manifest entry.
        default_bounds: Spec-level bounds fallback.

    Returns:
        The cell with ``detections``, ``bounds``, ``eval_path`` and
        ``tile_source`` populated.
    """
    resolved = dict(cell)
    if not resolved.get("detections") and resolved.get("condition_id"):
        found = resolve_from_manifest(resolved["condition_id"], manifest_index)
        resolved.setdefault("detections", found["detections"])
        if not resolved.get("bounds") and found["bounds"]:
            resolved["bounds"] = found["bounds"]
        resolved.setdefault("eval_path", found["eval_path"])
        resolved.setdefault("n_passes_expected", found["n_runs_expected"])
    if not resolved.get("bounds"):
        resolved["bounds"] = default_bounds
    if not resolved.get("tile_source"):
        first = load_geojson(Path(resolved["detections"][0]))
        resolved["tile_source"] = (
            "property"
            if "source_tile" in first.columns and first["source_tile"].notna().any()
            else "derive"
        )
    return resolved


# ── Tile-level classification ─────────────────────────────────────────

def populated_tiles(
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> tuple[list[str], set[str]]:
    """Return the bounds tile order and the set of reference-populated tiles.

    Vectorised equivalent of the ``refs_in_tile`` half of
    ``lib_advanced_metrics.calculate_tile_classification``: a tile counts as
    populated if ANY reference point intersects its geometry (so a point on a
    shared boundary populates every tile it touches). Computed once per
    (bounds, ground truth) pair because it does not depend on the detections.

    Args:
        gdf_ref: Reference points in the evaluation CRS.
        gdf_bounds: Tile bounds with a ``tile_name`` column, same CRS.

    Returns:
        Tuple ``(tile_order, populated)`` where ``tile_order`` preserves the
        bounds row order and ``populated`` is a set of tile names.
    """
    tile_order = list(gdf_bounds["tile_name"].unique())
    joined = gpd.sjoin(
        gdf_ref[["geometry"]],
        gdf_bounds[["tile_name", "geometry"]],
        how="inner",
        predicate="intersects",
    )
    return tile_order, set(joined["tile_name"].unique())


def tile_confusion(
    predicted: set[str],
    tile_order: list[str],
    populated: set[str],
) -> dict[str, Any]:
    """Tile-level confusion matrix and MCC from a predicted-populated tile set.

    Implements preregistration § 4.2 exactly as
    ``lib_advanced_metrics.calculate_tile_classification`` does, but from
    pre-computed sets rather than a per-tile loop over geometries. Pinned to
    that function by :func:`gate_tile_confusion`.

    Args:
        predicted: Tile names the detections attribute at least one detection
            to. Names outside ``tile_order`` are ignored.
        tile_order: All tile names in the evaluation bounds.
        populated: Tile names containing at least one reference mound.

    Returns:
        Dict with ``tp``/``tn``/``fp``/``fn`` counts, ``mcc`` (``None`` when
        the denominator degenerates, matching the committed function),
        ``sensitivity``, ``specificity``, ``n_tiles``.
    """
    tiles = set(tile_order)
    pred = predicted & tiles
    tp = len(pred & populated)
    fp = len(pred - populated)
    fn = len(populated - pred)
    tn = len(tiles) - tp - fp - fn

    denominator = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    mcc = None if denominator == 0 else (tp * tn - fp * fn) / math.sqrt(denominator)
    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "mcc": None if mcc is None else round(mcc, 6),
        "sensitivity": round(tp / (tp + fn), 6) if (tp + fn) else None,
        "specificity": round(tn / (tn + fp), 6) if (tn + fp) else None,
        "n_tiles": len(tiles),
    }


def gate_tile_confusion(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_order: list[str],
    populated: set[str],
) -> dict[str, Any]:
    """Check the fast confusion path against the committed scorer's own loop.

    Args:
        gdf_det: Detections carrying a ``source_tile`` column.
        gdf_ref: Reference points.
        gdf_bounds: Tile bounds.
        tile_order: Tile order from :func:`populated_tiles`.
        populated: Populated-tile set from :func:`populated_tiles`.

    Returns:
        Dict recording both confusion matrices and whether they agree.
    """
    fast = tile_confusion(set(gdf_det["source_tile"].dropna()), tile_order, populated)
    slow = calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds)
    keys = ("tp", "tn", "fp", "fn")
    agree = all(fast[k] == slow[k] for k in keys)
    return {
        "fast": {k: fast[k] for k in keys},
        "calculate_tile_classification": {k: slow[k] for k in keys},
        "agree": bool(agree),
        "mcc_fast": fast["mcc"],
        "mcc_committed_function": (
            None if slow["mcc"] is None else round(float(slow["mcc"]), 6)
        ),
    }


# ── Tile assignment for the as-committed arm ──────────────────────────

def assign_first_intersecting(
    gdf_det: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> gpd.GeoSeries:
    """Reproduce the committed scorer's derived tile rule.

    Mirrors ``evaluate_detections.py`` (the ``sjoin(..., "intersects")`` then
    ``~index.duplicated(keep="first")`` block that fires when a detection
    artefact carries no ``source_tile``). Used for aggregated artefacts —
    consensus outputs write ``source_tiles`` plural, so the scorer derives a
    singular one. Applying the SAME rule to both arms of a cell holds the
    tile-assignment mechanism (erratum E79) fixed, so the measured movement is
    attributable to deduplication alone.

    Args:
        gdf_det: Detections in the evaluation CRS.
        gdf_bounds: Tile bounds with ``tile_name``, same CRS.

    Returns:
        Series of tile names indexed like ``gdf_det``.
    """
    joined = gpd.sjoin(
        gdf_det,
        gdf_bounds[["tile_name", "geometry"]],
        how="left",
        predicate="intersects",
    )
    joined = joined[~joined.index.duplicated(keep="first")]
    return joined["tile_name"]


# ── Deduplication with full provenance ────────────────────────────────

def dedup_with_provenance(
    gdf_in: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    distance_thresh: float = DISTANCE_THRESHOLD_METRES,
) -> tuple[gpd.GeoDataFrame, list[list[str]], dict[str, Any]]:
    """Apply the preregistered within-pass deduplication, keeping provenance.

    Wraps ``merge_passes.deduplicate_within_pass`` (greedy star clustering at
    20 m) and rebuilds a scorable point GeoDataFrame whose ``source_tile``
    column follows the ``first_source_tile`` rule, while ALSO returning each
    cluster's full contributing-tile list so the other two attribution rules
    can be evaluated without re-clustering.

    Args:
        gdf_in: Detections in the evaluation CRS, carrying ``source_tile``.
        gdf_bounds: Tile bounds (used for the nearest-centroid rule).
        distance_thresh: Clustering radius in metres (default 20 m).

    Returns:
        Tuple ``(gdf_dedup, contributing_tiles, stats)``. ``gdf_dedup`` has one
        row per cluster with ``source_tile`` set by the first-source-tile rule
        and a ``source_tile_nearest`` column for the geometric rule;
        ``contributing_tiles[i]`` lists every tile that fed cluster ``i``.
    """
    features = [
        {
            "geometry": {
                "type": "Point",
                "coordinates": [geom.centroid.x, geom.centroid.y],
            },
            "properties": {
                "subtype": row.get("subtype") or row.get("label") or "mound",
                "source_tile": row.get("source_tile") or "unknown",
            },
        }
        for (_, row), geom in zip(gdf_in.iterrows(), gdf_in.geometry)
    ]
    clusters = deduplicate_within_pass(features, distance_thresh=distance_thresh)

    contributing = [list(c["source_tiles"]) for c in clusters]
    multi_sheet = sum(
        1 for tiles in contributing if len({get_map_name(t) for t in tiles}) > 1
    )
    multi_tile = sum(1 for tiles in contributing if len(tiles) > 1)

    gdf = gpd.GeoDataFrame(
        {
            "source_tile": [tiles[0] for tiles in contributing],
            "label": [c["label"] for c in clusters],
            "subtype": [c["label"] for c in clusters],
            "cluster_size": [c["cluster_size"] for c in clusters],
        },
        geometry=[Point(c["centroid"]) for c in clusters],
        crs=EVALUATION_CRS,
    )

    # Nearest-centroid attribution, restricted to each cluster's contributing
    # tiles: the geometric analogue of the reference-side rule.
    centroids = {
        row["tile_name"]: row.geometry.centroid for _, row in gdf_bounds.iterrows()
    }
    nearest = []
    for tiles, geom in zip(contributing, gdf.geometry):
        known = [t for t in tiles if t in centroids]
        if not known:
            nearest.append(tiles[0])
        else:
            nearest.append(min(known, key=lambda t: geom.distance(centroids[t])))
    gdf["source_tile_nearest"] = nearest

    stats = {
        "n_raw": len(features),
        "n_dedup": len(clusters),
        "n_removed": len(features) - len(clusters),
        "removed_fraction": round(
            (len(features) - len(clusters)) / len(features), 6
        ) if features else 0.0,
        "n_clusters_spanning_multiple_tiles": multi_tile,
        "n_clusters_spanning_multiple_map_sheets": multi_sheet,
    }
    return gdf, contributing, stats


# ── Scoring ───────────────────────────────────────────────────────────

def score_f1(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffers: list[int],
) -> dict[str, dict[str, float]]:
    """Score one detection set at several buffers with the committed matcher.

    Args:
        gdf_det: Detections with a ``source_tile`` column.
        gdf_ref: Reference points.
        gdf_bounds: Tile bounds.
        buffers: Buffer distances in metres.

    Returns:
        Mapping of ``str(buffer)`` to precision/recall/F1 and detection count.
    """
    out: dict[str, dict[str, float]] = {}
    for b in buffers:
        precision, recall, f1 = calculate_f1_internal(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=b
        )
        out[str(b)] = {
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "f1": round(f1, 6),
            "n_detections": int(len(gdf_det)),
        }
    return out


def run_pass(
    det_path: Path,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    tile_order: list[str],
    populated: set[str],
    buffers: list[int],
    tile_source: str,
    gate: bool,
) -> dict[str, Any]:
    """Score one detection file as committed and after deduplication.

    Args:
        det_path: Detection GeoJSON (per-pass file, or one aggregated set).
        gdf_ref: Reference points in the evaluation CRS.
        gdf_bounds: Tile bounds in the evaluation CRS.
        tile_order: Tile order from :func:`populated_tiles`.
        populated: Populated-tile set from :func:`populated_tiles`.
        buffers: Buffer distances in metres.
        tile_source: ``"property"`` to trust the file's own ``source_tile``,
            or ``"derive"`` to apply the committed first-intersecting rule to
            BOTH arms (required for aggregated artefacts, which carry none).
        gate: Whether to run the confusion-matrix gate on this pass.

    Returns:
        Per-pass result dict.

    Raises:
        ValueError: If ``tile_source`` is ``"property"`` but the file has no
            usable ``source_tile`` column.
    """
    committed = load_geojson(det_path)

    if tile_source == "derive":
        committed = committed.copy()
        committed["source_tile"] = assign_first_intersecting(committed, gdf_bounds)
    elif "source_tile" not in committed.columns:
        raise ValueError(
            f"{det_path} carries no source_tile; declare tile_source='derive' "
            "for this cell so both arms share the committed derivation rule."
        )

    deduped, contributing, stats = dedup_with_provenance(committed, gdf_bounds)

    result: dict[str, Any] = {
        "detections": str(det_path),
        "dedup_stats": stats,
        "as_committed": {
            "buffers": score_f1(committed, gdf_ref, gdf_bounds, buffers),
            "tile_classification": tile_confusion(
                set(committed["source_tile"].dropna()), tile_order, populated
            ),
        },
        "deduplicated": {
            "buffers": score_f1(deduped, gdf_ref, gdf_bounds, buffers),
            "tile_classification": {},
        },
    }

    predicted_by_rule = {
        "first_source_tile": set(deduped["source_tile"].dropna()),
        "nearest_centroid": set(deduped["source_tile_nearest"].dropna()),
        "union_contributing": {t for tiles in contributing for t in tiles},
    }
    for rule, predicted in predicted_by_rule.items():
        result["deduplicated"]["tile_classification"][rule] = tile_confusion(
            predicted, tile_order, populated
        )

    if gate:
        result["gate_tile_confusion"] = gate_tile_confusion(
            committed, gdf_ref, gdf_bounds, tile_order, populated
        )
    return result


def _mean(values: list[float]) -> float:
    """Arithmetic mean rounded to six decimals (empty list -> 0.0)."""
    return round(sum(values) / len(values), 6) if values else 0.0


def aggregate_passes(passes: list[dict[str, Any]], buffers: list[int]) -> dict[str, Any]:
    """Average per-pass results the way ``evaluate_detections`` aggregates runs.

    ``evaluate_detections.aggregate_runs`` averages the per-run F1/precision/
    recall per buffer and averages the per-run MCC ``point`` values, so a
    multi-pass cell's headline numbers are means over passes. This mirrors that
    so the as-committed column is directly comparable to ``evaluation.json``.

    Args:
        passes: Per-pass dicts from :func:`run_pass`.
        buffers: Buffer distances in metres.

    Returns:
        Dict of mean F1/precision/recall per buffer per arm, mean MCC per arm
        and rule, and the deltas.
    """
    means: dict[str, Any] = {"buffers": {}, "mcc": {}, "delta": {}}

    for b in map(str, buffers):
        block: dict[str, Any] = {}
        for arm in ("as_committed", "deduplicated"):
            block[arm] = {
                metric: _mean([p[arm]["buffers"][b][metric] for p in passes])
                for metric in ("precision", "recall", "f1")
            }
            block[arm]["n_detections"] = _mean(
                [p[arm]["buffers"][b]["n_detections"] for p in passes]
            )
        block["delta_f1"] = round(
            block["deduplicated"]["f1"] - block["as_committed"]["f1"], 6
        )
        block["delta_precision"] = round(
            block["deduplicated"]["precision"] - block["as_committed"]["precision"], 6
        )
        block["delta_recall"] = round(
            block["deduplicated"]["recall"] - block["as_committed"]["recall"], 6
        )
        means["buffers"][b] = block

    committed_mcc = [
        p["as_committed"]["tile_classification"]["mcc"]
        for p in passes
        if p["as_committed"]["tile_classification"]["mcc"] is not None
    ]
    means["mcc"]["as_committed"] = _mean(committed_mcc)
    for rule in ATTRIBUTION_RULES:
        values = [
            p["deduplicated"]["tile_classification"][rule]["mcc"]
            for p in passes
            if p["deduplicated"]["tile_classification"][rule]["mcc"] is not None
        ]
        means["mcc"][rule] = _mean(values)
        means["delta"][f"delta_mcc_{rule}"] = round(
            means["mcc"][rule] - means["mcc"]["as_committed"], 6
        )
    return means


def check_against_evaluation(
    eval_path: Path,
    means: dict[str, Any],
    buffers: list[int],
) -> dict[str, Any]:
    """Compare the as-committed arm against the cell's committed evaluation.

    Args:
        eval_path: Path to the cell's ``evaluation.json``.
        means: Output of :func:`aggregate_passes`.
        buffers: Buffer distances in metres.

    Returns:
        Dict of committed vs reproduced values and their agreement flags.
    """
    summary = json.loads(eval_path.read_text())["summary"]
    out: dict[str, Any] = {"eval_path": str(eval_path), "buffers": {}}
    for b in buffers:
        row = next(
            (r for r in summary.get("buffers", []) if r["buffer_metres"] == b), None
        )
        if row is None:
            continue
        reproduced = means["buffers"][str(b)]["as_committed"]["f1"]
        out["buffers"][str(b)] = {
            "committed_f1": row["f1"],
            "reproduced_f1": reproduced,
            "abs_diff": round(abs(row["f1"] - reproduced), 6),
            "agree_4dp": bool(round(row["f1"], 4) == round(reproduced, 4)),
        }
    committed_mcc = (
        summary.get("tile_classification", {}).get("mcc", {}).get("point")
    )
    if committed_mcc is not None:
        out["mcc"] = {
            "committed_mcc_point": committed_mcc,
            "reproduced_mcc": means["mcc"]["as_committed"],
            "abs_diff": round(abs(committed_mcc - means["mcc"]["as_committed"]), 6),
            "agree_3dp": bool(
                round(committed_mcc, 3) == round(means["mcc"]["as_committed"], 3)
            ),
        }
    return out


def run_cell(
    cell: dict[str, Any],
    gdf_ref: gpd.GeoDataFrame,
    bounds_cache: dict[str, tuple[gpd.GeoDataFrame, list[str], set[str]]],
    gate_first: bool,
) -> dict[str, Any]:
    """Measure one condition cell end to end.

    Args:
        cell: Spec entry (see the module docstring for the schema).
        gdf_ref: Reference points in the evaluation CRS.
        bounds_cache: Memo of loaded bounds keyed by path string.
        gate_first: Whether to run the confusion gate on this cell's first pass.

    Returns:
        Per-cell result dict.
    """
    bounds_key = cell["bounds"]
    if bounds_key not in bounds_cache:
        gdf_bounds = load_geojson(Path(bounds_key))
        order, populated = populated_tiles(gdf_ref, gdf_bounds)
        bounds_cache[bounds_key] = (gdf_bounds, order, populated)
    gdf_bounds, tile_order, populated = bounds_cache[bounds_key]

    buffers = cell.get("buffers", [20, 30])
    tile_source = cell.get("tile_source", "property")

    passes = []
    for i, det in enumerate(cell["detections"]):
        passes.append(
            run_pass(
                Path(det),
                gdf_ref,
                gdf_bounds,
                tile_order,
                populated,
                buffers,
                tile_source,
                gate=(gate_first and i == 0),
            )
        )

    means = aggregate_passes(passes, buffers)
    expected = cell.get("n_passes_expected")
    if expected and expected != len(passes):
        logger.warning(
            "%s: resolved %d pass file(s) but its evaluation.json aggregated %d "
            "— the committed value cannot be reproduced from this file set",
            cell["name"], len(passes), expected,
        )
    result: dict[str, Any] = {
        "name": cell["name"],
        "condition_id": cell.get("condition_id"),
        "board": cell.get("board"),
        "bounds": bounds_key,
        "tile_source": tile_source,
        "detections": [str(d) for d in cell["detections"]],
        "n_passes": len(passes),
        "n_passes_expected": expected,
        "pass_count_gate": (
            None if not expected else bool(expected == len(passes))
        ),
        "n_populated_tiles": len(populated),
        "n_tiles": len(tile_order),
        "mean_over_passes": means,
        "passes": passes,
    }
    if cell.get("eval_path"):
        result["committed_check"] = check_against_evaluation(
            Path(cell["eval_path"]), means, buffers
        )
    return result


def main() -> int:
    """CLI entry point: measure every cell in the spec and write the results.

    Returns:
        Process exit code (0 on success).
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True,
                        help="JSON spec listing the cells to measure.")
    parser.add_argument("--output", type=Path, required=True,
                        help="Destination JSON for the results.")
    parser.add_argument("--ground-truth", type=Path, default=None,
                        help="Ground truth GeoJSON (overrides the spec).")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST,
                        help="Conditions manifest used to resolve condition_ids.")
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text())
    gt_path = args.ground_truth or Path(
        spec.get("ground_truth", DEFAULT_GROUND_TRUTH)
    )
    gdf_ref = load_geojson(gt_path)
    logger.info("Ground truth: %s (%d references)", gt_path, len(gdf_ref))

    manifest_index = {
        c["condition_id"]: c
        for c in json.loads(args.manifest.read_text())["conditions"]
    }

    bounds_cache: dict[str, tuple[gpd.GeoDataFrame, list[str], set[str]]] = {}
    cells = []
    for i, raw_cell in enumerate(spec["cells"]):
        cell = resolve_cell(raw_cell, manifest_index, spec.get("bounds"))
        logger.info(
            "[%d/%d] %s (%d pass file(s), tile_source=%s)",
            i + 1, len(spec["cells"]), cell["name"],
            len(cell["detections"]), cell["tile_source"],
        )
        cells.append(run_cell(cell, gdf_ref, bounds_cache, gate_first=(i == 0)))

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "spec": str(args.spec),
        "ground_truth": str(gt_path),
        "dedup_metres": DISTANCE_THRESHOLD_METRES,
        "attribution_rules": list(ATTRIBUTION_RULES),
        "cells": cells,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    logger.info("Wrote %s", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
