#!/usr/bin/env python3
"""
Prepare the H13 overlap-arm detection sets for uniform, comparable scoring.

H13 (preregistration §§ 1014-1048) contrasts three 512-pixel tiling
overlaps over the same four-sheet Era-1 footprint:

===  ==========  =========  ===========  =====
Arm  Overlap     Stride     Tiles/pass   Runs
===  ==========  =========  ===========  =====
A    64 px (12.5 %)  448 px  340         3
B    128 px (25 %)   384 px  430         3
C    256 px (50 %)   256 px  999         3
===  ==========  =========  ===========  =====

Two scoring hazards sit between the raw detections and a defensible
"F1 as a function of overlap" curve. This script neutralises both.

**Hazard 1 — cross-tile duplicates (caught at the S135 phase gate).**
``scripts/evaluate_detections.py`` has no deduplication step, so a mound
visible in two overlapping tiles is emitted twice and the second copy
becomes a false positive under Hungarian matching. Denser tilings
duplicate more, so naive scoring would manufacture a spurious
"overlap hurts precision" result. Every arm is therefore passed through
the preregistered within-pass 20 m deduplication
(``merge_passes.deduplicate_within_pass``, § 8.5 Step 1) before scoring
— arm A included, which is why the committed arm-A F1 values are NOT
comparable with the numbers produced here.

**Hazard 2 — divergent evaluation footprints (caught this session).**
The three arms' footprint-majority tile manifests do not cover identical
ground: arm A's union is 1751 km², arm B's 1695 km², arm C's 1847 km².
Ground truth in scope therefore differs by arm (539 / 563 / 565 mounds),
which would confound the overlap contrast with a tile-inclusion artefact.
This script emits two scopes:

``common``
    The intersection of all three arms' tile unions (1638 km²),
    represented as the arm-A tile grid clipped to that intersection.
    Detections are clipped to the same geometry and reassigned to the
    common grid, so every arm is scored on identical ground with an
    identical bootstrap resampling unit — this is the comparable,
    primary scope, and the only one supporting paired per-tile deltas.

``native``
    Each arm scored against its own tile bounds. Retained for
    transparency: it uses every detection the arm produced, but its
    across-arm F1 differences are not attributable to overlap alone.

Detections are assigned to a scoring tile by the same rule the evaluator
uses for references (:func:`lib_advanced_metrics._assign_refs_to_primary_tiles`):
among the tiles a detection intersects, the one whose centroid is nearest.
This keeps detection and reference tile assignment consistent for the
per-tile TP/FP/FN table that drives the bootstrap.

Usage::

    python scripts/prepare_h13_scoring.py \\
        --output-dir outputs/h13/scoring

    # Bounds only (skip the per-pass dedup work)
    python scripts/prepare_h13_scoring.py --bounds-only

Inputs:
    - Arm A passes: outputs/retest/phase2a/brief-text/run_{1,2,3}/
    - Arm B passes: outputs/h13/armB/run_{1,2,3}/ (+ run_1_recovery)
    - Arm C passes: outputs/h13/armC/run_{1,2,3}/
    - Arm A bounds: inputs/vectors/bounds/full_evaluation_bounds.geojson
    - Arm B/C tile manifests + per-map metadata under inputs/tiles_512_ov{128,256}/

Outputs (under ``--output-dir``):
    - bounds/h13_arm{A,B,C}_bounds.geojson  - native per-arm tile bounds
    - bounds/h13_common_bounds.geojson      - common (A n B n C) scope
    - {scope}/arm{A,B,C}/run_N/detections_dedup.geojson
    - dedup_summary.json                    - per-pass dedup + clip statistics

Created: 2026-08-18 (Session 136)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely.geometry import Point, mapping

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.merge_passes import (  # noqa: E402
    DISTANCE_THRESHOLD_METRES,
    deduplicate_within_pass,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: Coordinate reference system for all project vectors (UTM zone 35N).
CRS_URN = "urn:ogc:def:crs:EPSG::32635"
CRS_EPSG = 32635

#: Minimum area (m²) a clipped tile polygon must retain to stay in the
#: common-scope bounds. Guards against slivers produced by floating-point
#: noise along shared tile edges, which would otherwise add resampling
#: units that can hold no detection.
MIN_CLIPPED_TILE_AREA_M2 = 1.0

#: The three arms: label -> (overlap px, stride px, tiles dir, manifest).
#: Arm A predates the H13 tile trees; its bounds ship in inputs/vectors.
ARMS: dict[str, dict[str, Any]] = {
    "armA": {
        "overlap_px": 64,
        "stride_px": 448,
        "overlap_frac": 0.125,
        "tiles_dir": None,
        "manifest": None,
        "bounds": PROJECT_ROOT / "inputs/vectors/bounds/full_evaluation_bounds.geojson",
        "runs": {
            "run_1": [PROJECT_ROOT / "outputs/retest/phase2a/brief-text/run_1/detections_brief-text_run01.geojson"],
            "run_2": [PROJECT_ROOT / "outputs/retest/phase2a/brief-text/run_2/detections_brief-text_run02.geojson"],
            "run_3": [PROJECT_ROOT / "outputs/retest/phase2a/brief-text/run_3/detections_brief-text_run03.geojson"],
        },
    },
    "armB": {
        "overlap_px": 128,
        "stride_px": 384,
        "overlap_frac": 0.25,
        "tiles_dir": PROJECT_ROOT / "inputs/tiles_512_ov128",
        "manifest": PROJECT_ROOT / "inputs/tiles_512_ov128/h13_armB_manifest.json",
        "bounds": None,
        "runs": {
            # run_1 is completed by its additive single-tile recovery pass;
            # both files are concatenated before deduplication so the pass
            # covers the full 430-tile manifest.
            "run_1": [
                PROJECT_ROOT / "outputs/h13/armB/run_1/detections-detect_brief-text-3-flash-2026-08-17.geojson",
                PROJECT_ROOT / "outputs/h13/armB/run_1_recovery/detections-detect_brief-text-3-flash-2026-08-17.geojson",
            ],
            "run_2": [PROJECT_ROOT / "outputs/h13/armB/run_2/detections-detect_brief-text-3-flash-2026-08-17.geojson"],
            "run_3": [PROJECT_ROOT / "outputs/h13/armB/run_3/detections-detect_brief-text-3-flash-2026-08-17.geojson"],
        },
    },
    "armC": {
        "overlap_px": 256,
        "stride_px": 256,
        "overlap_frac": 0.50,
        "tiles_dir": PROJECT_ROOT / "inputs/tiles_512_ov256",
        "manifest": PROJECT_ROOT / "inputs/tiles_512_ov256/h13_armC_manifest.json",
        "bounds": None,
        "runs": {
            "run_1": [PROJECT_ROOT / "outputs/h13/armC/run_1/detections-detect_brief-text-3-flash-2026-08-17.geojson"],
            "run_2": [PROJECT_ROOT / "outputs/h13/armC/run_2/detections-detect_brief-text-3-flash-2026-08-17.geojson"],
            "run_3": [PROJECT_ROOT / "outputs/h13/armC/run_3/detections-detect_brief-text-3-flash-2026-08-17.geojson"],
        },
    },
}


def load_pass(paths: list[Path]) -> tuple[list[dict], set[str]]:
    """Load and concatenate one logical pass from one or more GeoJSON files.

    A pass is normally a single file. Arm B run_1 is split across a main
    file and an additive recovery file covering the one tile whose JSON
    response failed to parse; concatenating them reconstructs the complete
    pass without mutating either committed artefact.

    Args:
        paths: Detection GeoJSON paths making up the pass, in merge order.

    Returns:
        Tuple of (features, processed_tiles) where ``processed_tiles`` is
        the union of the files' top-level coverage records.

    Raises:
        FileNotFoundError: If any path does not exist.
    """
    features: list[dict] = []
    processed: set[str] = set()
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f"Detection GeoJSON missing: {p}")
        data = json.loads(p.read_text())
        features.extend(data.get("features", []))
        processed.update(data.get("processed_tiles") or [])
    return features, processed


def build_native_bounds(output_dir: Path) -> dict[str, Path]:
    """Materialise each arm's own tile-bounds GeoJSON.

    Arm A's bounds are the committed 340-tile evaluation bounds. Arms B
    and C are generated from their tile manifests via
    ``scripts/generate_tile_bounds.py`` so the polygons derive from the
    same tile metadata the detection run consumed.

    Args:
        output_dir: Root output directory; bounds land in ``output_dir/bounds``.

    Returns:
        Mapping of arm label to the written bounds path.

    Raises:
        RuntimeError: If a bounds generation subprocess fails.
    """
    bounds_dir = output_dir / "bounds"
    bounds_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    for arm, spec in ARMS.items():
        target = bounds_dir / f"h13_{arm}_bounds.geojson"
        if spec["bounds"] is not None:
            # Arm A: copy the committed bounds verbatim so the scoring
            # scope is byte-identical to the one used across the study.
            target.write_text(Path(spec["bounds"]).read_text())
        else:
            cmd = [
                sys.executable, str(PROJECT_ROOT / "scripts/generate_tile_bounds.py"),
                "--manifest", str(spec["manifest"]),
                "--name", f"h13_{arm}",
                "--tiles-dir", str(spec["tiles_dir"]),
                "--tile-size", "512",
                "--output-dir", str(bounds_dir),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(
                    f"generate_tile_bounds.py failed for {arm}:\n{result.stderr}"
                )
        n = len(json.loads(target.read_text())["features"])
        logger.info("%s native bounds: %d tiles -> %s", arm, n, target.name)
        written[arm] = target

    return written


def build_common_bounds(
    native: dict[str, Path], output_dir: Path,
) -> tuple[Path, Any]:
    """Build the common-scope bounds: the arm-A grid clipped to A n B n C.

    The arm-A grid is used as the carrier because it is the registered
    Era-1 evaluation grid and the coarsest of the three, giving the
    smallest set of resampling units that still covers the whole
    intersection. Clipping (rather than selecting whole tiles) keeps the
    scored ground exactly equal to the intersection, so no arm is scored
    over ground another arm never saw.

    Args:
        native: Mapping of arm label to native bounds path.
        output_dir: Root output directory.

    Returns:
        Tuple of (path to the written common bounds, the common footprint
        geometry as a shapely object).
    """
    unions = {}
    for arm, path in native.items():
        unions[arm] = gpd.read_file(path).geometry.union_all()

    common = unions["armA"].intersection(unions["armB"]).intersection(unions["armC"])

    grid = gpd.read_file(native["armA"]).copy()
    grid["geometry"] = grid.geometry.intersection(common)
    grid = grid[grid.geometry.notna() & ~grid.geometry.is_empty].copy()
    grid = grid[grid.geometry.area > MIN_CLIPPED_TILE_AREA_M2].copy()

    target = output_dir / "bounds" / "h13_common_bounds.geojson"
    grid.to_file(target, driver="GeoJSON")

    logger.info(
        "common scope: %.3f km² (A %.3f / B %.3f / C %.3f), %d carrier tiles",
        common.area / 1e6, unions["armA"].area / 1e6,
        unions["armB"].area / 1e6, unions["armC"].area / 1e6, len(grid),
    )
    return target, common


def assign_primary_tiles(
    gdf_det: gpd.GeoDataFrame, gdf_bounds: gpd.GeoDataFrame,
) -> list[str | None]:
    """Assign each detection to exactly one scoring tile.

    Mirrors the evaluator's reference-assignment rule: among the tiles a
    detection intersects, take the one whose centroid is nearest. Keeping
    detection and reference assignment consistent matters because the
    bootstrap resamples the per-tile TP/FP/FN table, where TPs and FPs are
    booked to the detection's tile and FNs to the reference's tile.

    Args:
        gdf_det: Detections (point geometries) in the project CRS.
        gdf_bounds: Scoring tile bounds with a ``tile_name`` column.

    Returns:
        List of tile names aligned with ``gdf_det``'s row order; ``None``
        for a detection intersecting no tile (only possible in the native
        scope, where detections are not clipped).
    """
    if gdf_det.empty:
        return []

    joined = gpd.sjoin(
        gdf_det, gdf_bounds[["tile_name", "geometry"]],
        how="inner", predicate="intersects",
    )
    centroids = {
        row["tile_name"]: row.geometry.centroid
        for _, row in gdf_bounds.iterrows()
    }

    candidates: dict[Any, list[str]] = defaultdict(list)
    for idx, tile_name in zip(joined.index, joined["tile_name"]):
        candidates[idx].append(tile_name)

    assigned: list[str | None] = []
    for idx, geom in zip(gdf_det.index, gdf_det.geometry):
        names = candidates.get(idx)
        if not names:
            assigned.append(None)
        elif len(names) == 1:
            assigned.append(names[0])
        else:
            assigned.append(min(names, key=lambda t: geom.distance(centroids[t])))
    return assigned


def write_dedup_geojson(
    deduped: list[dict],
    gdf_bounds: gpd.GeoDataFrame,
    processed_tiles: list[str],
    target: Path,
    clip_geom: Any | None,
) -> dict[str, int]:
    """Write one deduplicated pass as a scorable point GeoJSON.

    Deduplicated detections are cluster mean centroids. Points are the
    correct representation because the evaluator's Hungarian matcher
    reduces every geometry to its centroid anyway
    (:func:`lib_advanced_metrics.match_detections_to_references`), so
    nothing is lost, and point-in-polygon clipping is then exact.

    Args:
        deduped: Cluster dicts from :func:`deduplicate_within_pass`.
        gdf_bounds: Scoring tile bounds for tile assignment.
        processed_tiles: Coverage record to stamp on the output, so the
            evaluator's E72 partial-coverage guard counts rather than
            infers.
        target: Output path.
        clip_geom: Footprint to clip detections to, or ``None`` to keep all.

    Returns:
        Dict with ``n_in``, ``n_clipped``, ``n_out`` and ``n_unassigned``.
    """
    n_in = len(deduped)
    geoms = [Point(d["centroid"]) for d in deduped]
    gdf = gpd.GeoDataFrame(
        {
            "label": [d["label"] for d in deduped],
            "cluster_size": [d["cluster_size"] for d in deduped],
            "origin_tiles": [";".join(d["source_tiles"]) for d in deduped],
        },
        geometry=geoms,
        crs=f"EPSG:{CRS_EPSG}",
    )

    n_clipped = 0
    if clip_geom is not None:
        keep = gdf.geometry.within(clip_geom)
        n_clipped = int((~keep).sum())
        gdf = gdf[keep].copy()

    gdf["source_tile"] = assign_primary_tiles(gdf, gdf_bounds)
    n_unassigned = int(gdf["source_tile"].isna().sum())

    features = [
        {
            "type": "Feature",
            "geometry": mapping(row.geometry),
            "properties": {
                "source_tile": row["source_tile"],
                "label": row["label"],
                "subtype": row["label"],
                "cluster_size": int(row["cluster_size"]),
                "origin_tiles": row["origin_tiles"],
            },
        }
        for _, row in gdf.iterrows()
    ]

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": CRS_URN}},
        "processed_tiles": sorted(processed_tiles),
        "features": features,
    }))

    return {
        "n_in": n_in,
        "n_clipped": n_clipped,
        "n_out": len(features),
        "n_unassigned": n_unassigned,
    }


def main() -> int:
    """Run the preparation stage and write the dedup summary.

    Returns:
        Process exit status (0 on success).
    """
    parser = argparse.ArgumentParser(
        description="Prepare H13 overlap arms for uniform, comparable scoring.",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=PROJECT_ROOT / "outputs/h13/scoring",
        help="Root output directory (default: outputs/h13/scoring)",
    )
    parser.add_argument(
        "--bounds-only", action="store_true",
        help="Generate bounds files only; skip per-pass deduplication.",
    )
    parser.add_argument(
        "--dedup-metres", type=float, default=DISTANCE_THRESHOLD_METRES,
        help=f"Within-pass dedup radius (default: {DISTANCE_THRESHOLD_METRES} m)",
    )
    args = parser.parse_args()

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    native = build_native_bounds(out)
    common_path, common_geom = build_common_bounds(native, out)

    if args.bounds_only:
        logger.info("Bounds only — stopping before deduplication.")
        return 0

    bounds_gdfs = {arm: gpd.read_file(p) for arm, p in native.items()}
    common_gdf = gpd.read_file(common_path)
    common_tiles = sorted(common_gdf["tile_name"].tolist())

    summary: dict[str, Any] = {
        "dedup_metres": args.dedup_metres,
        "common_scope_km2": common_geom.area / 1e6,
        "common_carrier_tiles": len(common_gdf),
        "passes": [],
    }

    for arm, spec in ARMS.items():
        for run, paths in spec["runs"].items():
            raw, processed = load_pass(paths)
            deduped = deduplicate_within_pass(raw, distance_thresh=args.dedup_metres)

            native_stats = write_dedup_geojson(
                deduped, bounds_gdfs[arm], sorted(processed),
                out / "native" / arm / run / "detections_dedup.geojson",
                clip_geom=None,
            )
            # In the common scope the arm genuinely processed every carrier
            # tile (each arm's tiling fully covers the intersection), so the
            # coverage record is the carrier grid, not the arm's own tiling.
            common_stats = write_dedup_geojson(
                deduped, common_gdf, common_tiles,
                out / "common" / arm / run / "detections_dedup.geojson",
                clip_geom=common_geom,
            )

            summary["passes"].append({
                "arm": arm,
                "run": run,
                "overlap_frac": spec["overlap_frac"],
                "tiles": len(processed),
                "n_raw": len(raw),
                "n_dedup": len(deduped),
                "n_removed": len(raw) - len(deduped),
                "removed_frac": (len(raw) - len(deduped)) / len(raw) if raw else 0.0,
                "native": native_stats,
                "common": common_stats,
            })
            logger.info(
                "%s %s: raw %d -> dedup %d (-%d, %.1f%%); common %d "
                "(clipped %d, unassigned %d)",
                arm, run, len(raw), len(deduped), len(raw) - len(deduped),
                100 * (len(raw) - len(deduped)) / len(raw) if raw else 0.0,
                common_stats["n_out"], common_stats["n_clipped"],
                common_stats["n_unassigned"],
            )

    (out / "dedup_summary.json").write_text(json.dumps(summary, indent=2))
    logger.info("Wrote %s", out / "dedup_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
