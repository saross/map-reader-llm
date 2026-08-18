#!/usr/bin/env python3
"""
Measure the two scoring-path sensitivities in ``evaluate_detections.py``.

Session 136 surfaced two independent properties of the single-file
scoring path. Neither invalidates a committed result, but both need
measuring rather than estimating before the paper can say anything
about them. This script measures both on real committed artefacts and
emits a machine-readable record.

**Sensitivity 1 — no within-pass deduplication (``--mode dedup``).**
``scripts/evaluate_detections.py`` has no deduplication step. When it is
pointed at a RAW per-pass detection GeoJSON, a mound that the detector
emitted from two overlapping tiles appears twice, and the second copy
scores as a false positive under Hungarian matching. The preregistered
within-pass 20 m deduplication (§ 8.5 Step 1) lives in
``scripts/merge_passes.py`` (:func:`deduplicate_within_pass`), which is
reached by the multi-pass consensus and WBF paths but NOT by a
proposer-verifier cell whose proposer pool is a single raw pass —
``scripts/extract_candidates.py`` crops one candidate per input feature
without clustering, so duplicates survive verification. Exposure is
therefore a property of the artefact, not of its architecture label,
and is best established by measuring the artefact directly. This mode
scores each cell twice — once as committed, once after applying the
preregistered deduplication — and reports the movement.

**Sensitivity 2 — order-dependent tile assignment (``--mode tiebreak``).**
When a detection GeoJSON carries no ``source_tile`` property (true of
every aggregated artefact, whose features carry ``source_tiles`` plural
instead), ``evaluate_detections.py:1433-1443`` derives one with
``gpd.sjoin(..., predicate="intersects")`` followed by
``~joined.index.duplicated(keep="first")`` — i.e. the FIRST intersecting
bounds tile in GeoDataFrame row order. Because tiles overlap, a border
detection intersects two or more tiles, and the winner depends on row
order rather than on geometry. The alternative principled rule —
nearest tile centroid — is what
``lib_advanced_metrics._assign_refs_to_primary_tiles`` (lines 746-801)
already applies to REFERENCES. Since
``lib_advanced_metrics.calculate_f1_internal`` scopes detections per map
sheet through ``source_tile`` (line 1159) and runs Hungarian matching
per map, a reassignment that crosses a map-sheet boundary changes the
matching problem. This mode scores each cell under both rules and
reports the movement plus the reassignment counts.

Usage::

    # Both modes, driven by a spec file
    python scripts/scoring_sensitivity_probe.py \\
        --spec reports/data/scoring-sensitivity-spec.json \\
        --output results/scoring-sensitivity-2026-08-18/probe.json

Spec file format (JSON)::

    {
      "dedup_cells": [
        {"name": "label",
         "detections": ["outputs/.../detections_x_run01.geojson", ...],
         "bounds": "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
         "buffers": [20, 30]}
      ],
      "tiebreak_cells": [
        {"name": "label",
         "detections": "outputs/.../consensus_t9.geojson",
         "bounds": "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
         "buffers": [30]}
      ]
    }

Each ``dedup_cells`` entry may list several per-pass files; they are
scored independently and the per-cell result reports both the per-pass
numbers and their mean, which is how the conditions manifest aggregates
multi-run single-pass conditions.

Notes:
    - Point estimates only. ``evaluate_single_run`` takes its ``f1``
      straight from :func:`calculate_f1_internal`, so the point
      estimates here are bit-identical to the committed ones; the
      bootstrap is skipped because it costs minutes and answers a
      different question.
    - Zero API spend. Reads committed artefacts only.

Created: 2026-08-18 (Session 136)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_advanced_metrics import (  # noqa: E402
    calculate_f1_internal,
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

#: Default ground truth used by ``evaluate_detections.py``.
DEFAULT_GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"


# ── Tile-assignment rules ─────────────────────────────────────────────

def assign_first_intersecting(
    gdf_det: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> gpd.GeoSeries:
    """Reproduce the committed rule in ``evaluate_detections.py``.

    Mirrors ``evaluate_detections.py:1433-1443`` exactly: spatial join on
    ``intersects``, then keep the first row per detection index. The
    "first" is whichever bounds row the join emitted first, which is
    driven by ``gdf_bounds`` row order, not by geometry.

    Args:
        gdf_det: Detections, in the evaluation CRS.
        gdf_bounds: Tile bounds with a ``tile_name`` column, same CRS.

    Returns:
        Series of tile names indexed like ``gdf_det`` (NaN where the
        detection intersects no tile).
    """
    joined = gpd.sjoin(
        gdf_det, gdf_bounds[["tile_name", "geometry"]],
        how="left", predicate="intersects",
    )
    joined = joined[~joined.index.duplicated(keep="first")]
    return joined["tile_name"]


def assign_nearest_centroid(
    gdf_det: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> gpd.GeoSeries:
    """Assign each detection to the intersecting tile with nearest centroid.

    The rule ``lib_advanced_metrics._assign_refs_to_primary_tiles``
    (lines 746-801) already uses for references, applied here to
    detections. Unlike the committed rule it is a pure function of
    geometry, so it is invariant under row reordering of either frame.

    Args:
        gdf_det: Detections, in the evaluation CRS.
        gdf_bounds: Tile bounds with a ``tile_name`` column, same CRS.

    Returns:
        Series of tile names indexed like ``gdf_det`` (NaN where the
        detection intersects no tile).
    """
    joined = gpd.sjoin(
        gdf_det, gdf_bounds[["tile_name", "geometry"]],
        how="left", predicate="intersects",
    )
    centroids = {
        row["tile_name"]: row.geometry.centroid
        for _, row in gdf_bounds.iterrows()
    }

    out: dict[Any, Any] = {}
    for idx, group in joined.groupby(level=0):
        names = [n for n in group["tile_name"].tolist() if isinstance(n, str)]
        if not names:
            out[idx] = None
        elif len(names) == 1:
            out[idx] = names[0]
        else:
            geom = gdf_det.loc[idx].geometry
            # ``gdf_det.loc[idx]`` can return a frame if the index is not
            # unique; the probe only ever reads unique-index frames.
            out[idx] = min(names, key=lambda t: geom.distance(centroids[t]))

    return gpd.pd.Series(out).reindex(gdf_det.index)


# ── Deduplication ─────────────────────────────────────────────────────

def dedup_geodataframe(
    path: Path,
    distance_thresh: float = DISTANCE_THRESHOLD_METRES,
) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
    """Apply the preregistered within-pass deduplication to a raw pass.

    Reads the raw GeoJSON as plain JSON (the form
    :func:`deduplicate_within_pass` expects), clusters at
    ``distance_thresh``, and rebuilds a scorable point GeoDataFrame.

    Cluster ``source_tile`` is taken as the first (lexicographically
    sorted) contributing tile. Because rasters are tiled per map sheet,
    every tile contributing to a cluster belongs to the same sheet, so
    this choice cannot move a cluster between sheets — the function
    verifies that invariant and records any violation in the stats.

    CRS note: committed detection artefacts are stored in a mixture of
    UTM 35N (an explicit ``crs`` member naming EPSG:32635) and WGS84
    degrees (no ``crs`` member — the RFC 7946 default). The 20 m
    threshold is metric, so the file is loaded through
    :func:`evaluate_detections.load_geojson`, which reprojects to the
    evaluation CRS exactly as the scorer does, before clustering.

    Args:
        path: Detection GeoJSON in any CRS the scorer accepts.
        distance_thresh: Clustering radius in metres (default 20 m,
            preregistration § 8.5 Step 1).

    Returns:
        Tuple of (deduplicated point GeoDataFrame, statistics dict).
    """
    gdf_in = load_geojson(Path(path))
    features = [
        {
            "geometry": {"type": "Point",
                         "coordinates": [g.centroid.x, g.centroid.y]},
            "properties": {
                "subtype": row.get("subtype") or row.get("label") or "mound",
                "source_tile": row.get("source_tile") or "unknown",
            },
        }
        for (_, row), g in zip(gdf_in.iterrows(), gdf_in.geometry)
    ]
    clusters = deduplicate_within_pass(features, distance_thresh=distance_thresh)

    multi_sheet = 0
    tiles: list[str] = []
    for c in clusters:
        sheets = {get_map_name(t) for t in c["source_tiles"]}
        if len(sheets) > 1:
            multi_sheet += 1
        tiles.append(c["source_tiles"][0])

    gdf = gpd.GeoDataFrame(
        {
            "source_tile": tiles,
            "label": [c["label"] for c in clusters],
            "subtype": [c["label"] for c in clusters],
            "cluster_size": [c["cluster_size"] for c in clusters],
        },
        geometry=[Point(c["centroid"]) for c in clusters],
        crs=EVALUATION_CRS,
    )

    sizes = Counter(c["cluster_size"] for c in clusters)
    stats = {
        "n_raw": len(features),
        "n_dedup": len(clusters),
        "n_removed": len(features) - len(clusters),
        "removed_fraction": (
            (len(features) - len(clusters)) / len(features) if features else 0.0
        ),
        "cluster_size_histogram": {str(k): v for k, v in sorted(sizes.items())},
        "clusters_spanning_multiple_map_sheets": multi_sheet,
    }
    return gdf, stats


# ── Scoring ───────────────────────────────────────────────────────────

def score(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffers: list[int],
) -> dict[str, dict[str, float]]:
    """Score one detection set at several buffers.

    Args:
        gdf_det: Detections with a ``source_tile`` column.
        gdf_ref: Ground-truth references.
        gdf_bounds: Evaluation tile bounds.
        buffers: Buffer distances in metres.

    Returns:
        Mapping of ``str(buffer)`` to precision/recall/F1 and n.
    """
    out = {}
    for b in buffers:
        p, r, f1 = calculate_f1_internal(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=b,
        )
        out[str(b)] = {
            "precision": round(p, 6),
            "recall": round(r, 6),
            "f1": round(f1, 6),
            "n_detections": int(len(gdf_det)),
        }
    return out


def run_dedup_cell(
    cell: dict[str, Any],
    gdf_ref: gpd.GeoDataFrame,
) -> dict[str, Any]:
    """Score one cell as committed and after deduplication.

    Args:
        cell: Spec entry with ``name``, ``detections`` (list of paths),
            ``bounds``, and ``buffers``.
        gdf_ref: Ground-truth references.

    Returns:
        Per-pass and mean results for both scoring paths.
    """
    bounds = load_geojson(Path(cell["bounds"]))
    buffers = cell.get("buffers", [20, 30])
    passes = []

    for det_path in cell["detections"]:
        p = Path(det_path)
        committed = load_geojson(p)
        if "source_tile" not in committed.columns:
            raise ValueError(
                f"{p} has no source_tile property — the scorer would "
                "re-derive one by spatial join, so this cell is tie-break "
                "exposed and belongs in tiebreak_cells."
            )
        deduped, stats = dedup_geodataframe(p)
        passes.append({
            "detections": str(p),
            "dedup_stats": stats,
            "as_committed": score(committed, gdf_ref, bounds, buffers),
            "deduplicated": score(deduped, gdf_ref, bounds, buffers),
        })

    means = {}
    for b in map(str, buffers):
        for key in ("as_committed", "deduplicated"):
            for metric in ("precision", "recall", "f1"):
                vals = [pa[key][b][metric] for pa in passes]
                means.setdefault(b, {}).setdefault(key, {})[metric] = round(
                    sum(vals) / len(vals), 6,
                )
        means[b]["delta_f1"] = round(
            means[b]["deduplicated"]["f1"] - means[b]["as_committed"]["f1"], 6,
        )

    return {
        "name": cell["name"],
        "bounds": cell["bounds"],
        "n_passes": len(passes),
        "passes": passes,
        "mean_over_passes": means,
    }


def run_tiebreak_cell(
    cell: dict[str, Any],
    gdf_ref: gpd.GeoDataFrame,
) -> dict[str, Any]:
    """Score one aggregated cell under both tile-assignment rules.

    Args:
        cell: Spec entry with ``name``, ``detections`` (single path),
            ``bounds``, and ``buffers``.
        gdf_ref: Ground-truth references.

    Returns:
        Results under both rules plus reassignment counts.
    """
    bounds = load_geojson(Path(cell["bounds"]))
    buffers = cell.get("buffers", [30])
    det = load_geojson(Path(cell["detections"]))

    if "source_tile" in det.columns:
        logger.warning(
            "%s already carries source_tile — the committed scorer would "
            "NOT have re-derived it, so this cell is not tie-break exposed.",
            cell["detections"],
        )

    first = assign_first_intersecting(det, bounds)
    nearest = assign_nearest_centroid(det, bounds)

    changed_tile = int((first.fillna("") != nearest.fillna("")).sum())
    changed_sheet = int(sum(
        1 for a, b in zip(first.fillna(""), nearest.fillna(""))
        if get_map_name(a) != get_map_name(b)
    ))
    n_multi = int(gpd.sjoin(
        det, bounds[["tile_name", "geometry"]], how="left",
        predicate="intersects",
    ).index.duplicated().sum())

    det_first = det.copy()
    det_first["source_tile"] = first
    det_near = det.copy()
    det_near["source_tile"] = nearest

    res_first = score(det_first, gdf_ref, bounds, buffers)
    res_near = score(det_near, gdf_ref, bounds, buffers)
    deltas = {
        b: round(res_near[b]["f1"] - res_first[b]["f1"], 6) for b in res_first
    }

    return {
        "name": cell["name"],
        "detections": cell["detections"],
        "bounds": cell["bounds"],
        "n_detections": int(len(det)),
        "n_detections_intersecting_multiple_tiles": n_multi,
        "n_changing_tile": changed_tile,
        "n_changing_map_sheet": changed_sheet,
        "first_intersecting_tile": res_first,
        "nearest_centroid_tile": res_near,
        "delta_f1_nearest_minus_first": deltas,
    }


def main() -> int:
    """Run the probe over a spec file and write the results.

    Returns:
        Process exit code (0 on success).
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", type=Path, required=True,
                    help="JSON spec listing the cells to probe.")
    ap.add_argument("--output", type=Path, required=True,
                    help="Destination JSON for the results.")
    ap.add_argument("--ground-truth", type=Path, default=DEFAULT_GROUND_TRUTH,
                    help="Ground truth GeoJSON.")
    ap.add_argument("--mode", choices=["both", "dedup", "tiebreak"],
                    default="both", help="Which sensitivity to measure.")
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text())
    gdf_ref = load_geojson(args.ground_truth)
    logger.info("Ground truth: %s (%d references)", args.ground_truth, len(gdf_ref))

    results: dict[str, Any] = {
        "generated_at_utc": None,
        "ground_truth": str(args.ground_truth),
        "dedup_metres": DISTANCE_THRESHOLD_METRES,
        "dedup_cells": [],
        "tiebreak_cells": [],
    }
    from datetime import datetime, timezone
    results["generated_at_utc"] = datetime.now(timezone.utc).isoformat()

    if args.mode in ("both", "dedup"):
        for cell in spec.get("dedup_cells", []):
            logger.info("dedup cell: %s", cell["name"])
            results["dedup_cells"].append(run_dedup_cell(cell, gdf_ref))

    if args.mode in ("both", "tiebreak"):
        for cell in spec.get("tiebreak_cells", []):
            logger.info("tiebreak cell: %s", cell["name"])
            results["tiebreak_cells"].append(run_tiebreak_cell(cell, gdf_ref))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2))
    logger.info("Wrote %s", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
