#!/usr/bin/env python3
"""
Consensus-building and PV data loading utilities.
==================================================

Shared library for spatial clustering, consensus GeoDataFrame construction,
and Proposer-Verifier (PV) result loading. Extracted from standalone analysis
scripts to eliminate code duplication and ensure algorithmic consistency.

Functions:
    centroid_from_geometry   — Extract centroid from GeoJSON geometry dict
    deduplicate_within_pass  — Cluster detections within a single VLM pass
    cluster_across_passes    — Cluster detections across multiple VLM passes
    load_run_detections      — Load GeoJSON features from a run directory
    generate_consensus_gdf   — Build consensus GeoDataFrame from run dirs
    build_pv_gdf             — Build GeoDataFrame from PV-filtered results
    load_geojson_gdf         — Load detection GeoJSON with CRS correction
    load_shared_data         — Load reference and bounds GeoDataFrames

All spatial operations use EPSG:32635 (UTM Zone 35N) and a 20 m distance
threshold, consistent with the preregistered study design.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import json
import logging
from collections import Counter
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry import shape

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TARGET_CRS = "EPSG:32635"
DISTANCE_THRESHOLD_METRES = 20.0
BUFFER_METRES = 20


# ===================================================================
# Geometry utilities
# ===================================================================

def centroid_from_geometry(geom_dict: dict) -> tuple[float, float]:
    """
    Extract centroid coordinates from a GeoJSON geometry dictionary.

    Attempts to parse the geometry via Shapely. Falls back to raw
    coordinate extraction for Point geometries. Raises ``ValueError``
    if the geometry cannot be interpreted, rather than silently
    returning a phantom coordinate.

    Args:
        geom_dict: GeoJSON geometry dictionary with 'type' and
            'coordinates' keys.

    Returns:
        Tuple of (x, y) centroid coordinates.
    """
    try:
        geom = shape(geom_dict)
        centroid = geom.centroid
        return (centroid.x, centroid.y)
    except Exception:
        if geom_dict.get("type") == "Point":
            coords = geom_dict.get("coordinates")
            if coords and len(coords) >= 2:
                return (coords[0], coords[1])
        logger.warning(
            "Could not extract centroid from geometry: %s",
            geom_dict.get("type", "unknown"),
        )
        raise ValueError(
            f"Uninterpretable geometry (type={geom_dict.get('type', 'unknown')})"
        )


# ===================================================================
# Spatial clustering
# ===================================================================

def deduplicate_within_pass(
    features: list[dict],
    distance_thresh: float = DISTANCE_THRESHOLD_METRES,
) -> list[dict]:
    """
    Deduplicate detections within a single VLM pass using spatial clustering.

    Groups nearby detections (within ``distance_thresh`` metres) into
    clusters using a cKDTree for efficient neighbour lookup. Each cluster
    is reduced to a single detection with the mean centroid, majority
    label, and merged source tile list.

    Args:
        features: List of GeoJSON feature dictionaries, each with
            'geometry' and 'properties' keys.
        distance_thresh: Maximum distance (metres) to merge detections.
            Defaults to 20 m.

    Returns:
        List of deduplicated detection dicts, each with keys:
        'centroid', 'label', 'source_tiles', 'cluster_size'.
    """
    if not features:
        return []

    detections = []
    for f in features:
        centroid = centroid_from_geometry(f.get("geometry", {}))
        props = f.get("properties", {})
        detections.append({
            "centroid": centroid,
            "label": props.get("subtype", "mound"),
            "source_tile": (
                props.get("source_tile") or props.get("tile_id", "unknown")
            ),
            "original": f,
        })

    # Use cKDTree for efficient spatial clustering
    coords = np.array([d["centroid"] for d in detections])
    tree = cKDTree(coords)
    clusters: list[list[int]] = []
    used: set[int] = set()

    for i in range(len(detections)):
        if i in used:
            continue
        # Find all points within distance_thresh of point i
        neighbours = tree.query_ball_point(coords[i], distance_thresh)
        cluster_indices = [j for j in neighbours if j not in used]
        for j in cluster_indices:
            used.add(j)
        clusters.append(cluster_indices)

    deduped = []
    for cluster_indices in clusters:
        cluster = [detections[i] for i in cluster_indices]
        xs = [d["centroid"][0] for d in cluster]
        ys = [d["centroid"][1] for d in cluster]
        mean_centroid = (sum(xs) / len(xs), sum(ys) / len(ys))
        labels = [d["label"] for d in cluster]
        majority_label = Counter(labels).most_common(1)[0][0]
        source_tiles = sorted(set(d["source_tile"] for d in cluster))

        deduped.append({
            "centroid": mean_centroid,
            "label": majority_label,
            "source_tiles": source_tiles,
            "cluster_size": len(cluster),
        })

    return deduped


def cluster_across_passes(
    pass_detections: dict[str, list[dict]],
    distance_thresh: float = DISTANCE_THRESHOLD_METRES,
) -> list[dict]:
    """
    Cluster detections across multiple VLM passes using spatial indexing.

    Pools all per-pass deduplicated detections, then groups nearby
    detections (within ``distance_thresh`` metres) using cKDTree. Each
    resulting cluster records the number of distinct contributing passes
    (the "vote count") used for consensus thresholding.

    Args:
        pass_detections: Mapping from pass identifier to list of
            deduplicated detection dicts (as returned by
            ``deduplicate_within_pass``).
        distance_thresh: Maximum distance (metres) to merge detections.
            Defaults to 20 m.

    Returns:
        List of cluster dicts, each with keys: 'centroid', 'label',
        'vote_count', 'contributing_passes', 'source_tiles',
        'cluster_size'.
    """
    pool: list[dict] = []
    for pass_id, detections in pass_detections.items():
        for det in detections:
            pool.append({
                "centroid": det["centroid"],
                "label": det["label"],
                "pass_id": pass_id,
                "source_tiles": det.get("source_tiles", []),
            })

    if not pool:
        return []

    # Use cKDTree for efficient clustering
    coords = np.array([d["centroid"] for d in pool])
    tree = cKDTree(coords)
    clusters: list[list[int]] = []
    used: set[int] = set()

    for i in range(len(pool)):
        if i in used:
            continue
        neighbours = tree.query_ball_point(coords[i], distance_thresh)
        cluster_indices = [j for j in neighbours if j not in used]
        for j in cluster_indices:
            used.add(j)
        clusters.append(cluster_indices)

    result = []
    for cluster_indices in clusters:
        cluster = [pool[i] for i in cluster_indices]
        xs = [d["centroid"][0] for d in cluster]
        ys = [d["centroid"][1] for d in cluster]
        mean_centroid = (sum(xs) / len(xs), sum(ys) / len(ys))
        contributing_passes = sorted(set(d["pass_id"] for d in cluster))
        vote_count = len(contributing_passes)
        labels = [d["label"] for d in cluster]
        majority_label = Counter(labels).most_common(1)[0][0]
        all_tiles: list[str] = []
        for d in cluster:
            all_tiles.extend(d.get("source_tiles", []))
        source_tiles = sorted(set(all_tiles))

        result.append({
            "centroid": mean_centroid,
            "label": majority_label,
            "vote_count": vote_count,
            "contributing_passes": contributing_passes,
            "source_tiles": source_tiles,
            "cluster_size": len(cluster),
        })

    return result


# ===================================================================
# Data loading
# ===================================================================

def load_run_detections(run_dir: Path) -> list[dict]:
    """
    Load all GeoJSON detection features from a run directory.

    Args:
        run_dir: Path to a run directory containing
            ``detections_*.geojson`` files.

    Returns:
        List of GeoJSON feature dictionaries.
    """
    features: list[dict] = []
    for geojson_file in sorted(run_dir.glob("detections_*.geojson")):
        with open(geojson_file, encoding="utf-8") as f:
            data = json.load(f)
            features.extend(data.get("features", []))
    return features


def generate_consensus_gdf(
    run_dirs: list[Path],
    threshold: int,
) -> gpd.GeoDataFrame:
    """
    Generate a consensus GeoDataFrame from N run directories.

    Loads all detection GeoJSONs from each run, deduplicates within
    each run, clusters across runs, applies the vote threshold, and
    returns a GeoDataFrame suitable for bootstrap comparisons.

    Args:
        run_dirs: List of paths to run directories (e.g., run_1/, run_2/).
        threshold: Minimum vote count to retain a cluster.

    Returns:
        GeoDataFrame with 'source_tile' column and Point geometries,
        CRS explicitly set to EPSG:32635.
    """
    total_passes = len(run_dirs)

    # Load and deduplicate each run.
    # Use parent/name as key to handle the case where multiple
    # sub-conditions share the same run_N directory name
    # (e.g., Phase 3c diversity: h9-A-p1/run_1, h9-A-p2/run_1).
    pass_detections: dict[str, list[dict]] = {}
    for run_dir in run_dirs:
        run_key = f"{run_dir.parent.name}/{run_dir.name}"
        features = load_run_detections(run_dir)
        if features:
            deduped = deduplicate_within_pass(features)
            pass_detections[run_key] = deduped

    if not pass_detections:
        return gpd.GeoDataFrame(
            columns=["geometry", "source_tile", "subtype"],
            crs=TARGET_CRS,
        )

    # Cluster across passes
    clusters = cluster_across_passes(pass_detections)

    # Apply threshold and build GeoDataFrame
    rows = []
    for cluster in clusters:
        if cluster["vote_count"] >= threshold:
            source_tile = (
                cluster["source_tiles"][0]
                if cluster["source_tiles"]
                else "unknown"
            )
            rows.append({
                "geometry": ShapelyPoint(cluster["centroid"]),
                "source_tile": source_tile,
                "subtype": cluster["label"],
                "vote_count": cluster["vote_count"],
                "total_passes": total_passes,
            })

    if not rows:
        return gpd.GeoDataFrame(
            columns=["geometry", "source_tile", "subtype"],
            crs=TARGET_CRS,
        )

    return gpd.GeoDataFrame(rows, crs=TARGET_CRS)


def build_pv_gdf(
    pv_results_dir: Path,
    manifest_dir: Path,
    sweep_dir: Path,
) -> gpd.GeoDataFrame:
    """
    Build a GeoDataFrame from PV-filtered results at the optimal threshold.

    Loads probabilities.json (and consensus.json if present), reads the
    optimal threshold from threshold_sweep.json, filters candidates at that
    threshold, and builds Point geometries from manifest centroids.

    Args:
        pv_results_dir: Directory containing probabilities.json.
        manifest_dir: Directory containing candidate_manifest.json.
        sweep_dir: Directory containing threshold_sweep.json.

    Returns:
        GeoDataFrame with 'source_tile' column and Point geometries.
    """
    # Load optimal threshold
    sweep_file = sweep_dir / "threshold_sweep.json"
    with open(sweep_file, encoding="utf-8") as f:
        sweep = json.load(f)
    threshold = sweep["optimal"]["threshold"]

    # Load probabilities
    prob_file = pv_results_dir / "probabilities.json"
    with open(prob_file, encoding="utf-8") as f:
        prob_data = json.load(f)

    # Extract per-candidate probabilities from the results dict
    results = prob_data.get("results", {})

    # If consensus.json exists, use it to override/supplement probabilities
    consensus_file = pv_results_dir / "consensus.json"
    if consensus_file.exists():
        with open(consensus_file, encoding="utf-8") as f:
            consensus_data = json.load(f)
        # Key is "consensus", matching what run_pv.py produces
        consensus_results = consensus_data.get("consensus", {})
        # Merge: consensus takes precedence for computing final probability
        for cand_id, cand_data in consensus_results.items():
            if cand_id in results:
                # Use consensus probability if available
                results[cand_id] = cand_data

    # Load candidate manifest
    manifest_file = manifest_dir / "candidate_manifest.json"
    with open(manifest_file, encoding="utf-8") as f:
        manifest = json.load(f)

    # Build lookup from candidate ID to manifest entry
    # The manifest has a 'candidates' list of candidate dicts
    candidates = manifest.get("candidates", [])
    candidate_lookup: dict[str, dict] = {}
    for cand in candidates:
        # Candidate IDs in manifest are integers; in probabilities they are
        # strings like "candidate_00000"
        cand_id = f"candidate_{cand['candidate_id']:05d}"
        candidate_lookup[cand_id] = cand

    # Filter candidates at optimal threshold and build GeoDataFrame rows
    rows = []
    for cand_id, cand_data in results.items():
        prob = cand_data.get("mound_probability", 0)
        if prob >= threshold:
            manifest_entry = candidate_lookup.get(cand_id)
            if manifest_entry is None:
                logger.warning(
                    "Candidate %s not found in manifest, skipping", cand_id,
                )
                continue
            rows.append({
                "geometry": ShapelyPoint(
                    manifest_entry["centroid_x"],
                    manifest_entry["centroid_y"],
                ),
                "source_tile": manifest_entry["source_tile"],
                "mound_probability": prob,
            })

    if not rows:
        return gpd.GeoDataFrame(
            columns=["geometry", "source_tile", "mound_probability"],
            crs=TARGET_CRS,
        )

    return gpd.GeoDataFrame(rows, crs=TARGET_CRS)


def load_geojson_gdf(geojson_path: Path) -> gpd.GeoDataFrame:
    """
    Load a detection GeoJSON as a GeoDataFrame with CRS correction.

    Ensures 'source_tile' column exists and CRS is correct. Handles the
    case where GeoJSON files declare CRS as EPSG:4326 but actually contain
    UTM coordinates (common in consensus-proposer files produced by the
    merge pipeline). Detected by checking whether coordinate magnitudes
    exceed plausible lat/lon bounds.

    Args:
        geojson_path: Path to the detection GeoJSON file.

    Returns:
        GeoDataFrame with 'source_tile' column and correct CRS.
    """
    gdf = gpd.read_file(geojson_path)

    if gdf.crs is None:
        gdf.set_crs(TARGET_CRS, inplace=True)
    elif str(gdf.crs) != TARGET_CRS:
        # Check if coordinates are already in projected CRS despite metadata
        # saying otherwise (e.g., EPSG:4326 header with UTM coordinates).
        # UTM easting/northing values are typically > 100000; lat/lon <= 180.
        if not gdf.empty:
            sample_geom = gdf.geometry.iloc[0]
            sample_x = (
                sample_geom.centroid.x
                if sample_geom is not None
                else 0
            )
            if abs(sample_x) > 1000:
                # Coordinates are projected (UTM-scale), not geographic
                logger.info(
                    "Overriding declared CRS %s → %s for %s "
                    "(coordinates are already projected, x=%.0f)",
                    gdf.crs, TARGET_CRS, geojson_path.name, sample_x,
                )
                gdf.set_crs(TARGET_CRS, allow_override=True, inplace=True)
            else:
                gdf = gdf.to_crs(TARGET_CRS)
        else:
            gdf = gdf.to_crs(TARGET_CRS)

    if "source_tile" not in gdf.columns:
        # Try to extract from properties
        if "tile_id" in gdf.columns:
            gdf["source_tile"] = gdf["tile_id"]
        else:
            logger.warning(
                "No source_tile column in %s, using 'unknown'", geojson_path,
            )
            gdf["source_tile"] = "unknown"

    return gdf


def load_shared_data(
    data_dir: Path,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Load reference and bounds GeoDataFrames (shared across all comparisons).

    Reads all ``reference_*.geojson`` files from the ``references/``
    subdirectory and the ``full_evaluation_bounds.geojson`` from the
    ``bounds/`` subdirectory. Ensures both are in the target CRS.

    Args:
        data_dir: Base data directory containing ``references/`` and
            ``bounds/`` subdirectories.

    Returns:
        Tuple of (gdf_ref, gdf_bounds).

    Raises:
        ValueError: If no reference GeoJSON files are found.
    """
    ref_dir = data_dir / "references"
    ref_files = sorted(ref_dir.glob("reference_*.geojson"))

    if not ref_files:
        raise ValueError(
            f"No reference_*.geojson files found in {ref_dir}"
        )

    ref_gdfs = []
    for rf in ref_files:
        gdf = gpd.read_file(rf)
        gdf["Map"] = rf.stem.replace("reference_", "")
        ref_gdfs.append(gdf)

    gdf_ref = pd.concat(ref_gdfs, ignore_index=True)
    if gdf_ref.crs is None:
        gdf_ref.set_crs(TARGET_CRS, inplace=True)
    elif str(gdf_ref.crs) != TARGET_CRS:
        gdf_ref = gdf_ref.to_crs(TARGET_CRS)

    bounds_file = data_dir / "bounds" / "full_evaluation_bounds.geojson"
    gdf_bounds = gpd.read_file(bounds_file)
    if gdf_bounds.crs is None:
        gdf_bounds.set_crs(TARGET_CRS, inplace=True)
    elif str(gdf_bounds.crs) != TARGET_CRS:
        gdf_bounds = gdf_bounds.to_crs(TARGET_CRS)

    return gdf_ref, gdf_bounds
