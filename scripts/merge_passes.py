#!/usr/bin/env python3
"""
Merge Detection Passes with Consensus Voting
=============================================

Implements the voting algorithm from preregistration Section 8.5:

1. Within-pass deduplication (20 m tolerance) -- handles overlapping tiles
2. Cross-pass clustering (20 m tolerance)
3. Count votes per cluster (distinct passes contributing)
4. Apply vote threshold
5. Output: centroid, majority label, confidence (votes/N), source passes

Supports K=10 to N=5 conversion by splitting runs 1-5 and 6-10 into
separate pools (preregistration Section 3.8).

Usage:
    # Merge all passes in directory with threshold 3
    python scripts/merge_passes.py \\
        --input-dir outputs/phase1-library \\
        --output outputs/phase1-library/merged_t3.geojson \\
        --threshold 3

    # Split K=10 into two N=5 pools
    python scripts/merge_passes.py \\
        --input-dir outputs/experiment \\
        --output outputs/experiment/pool_a.geojson \\
        --passes 1,2,3,4,5 \\
        --threshold 3

    # Generate multiple threshold outputs
    python scripts/merge_passes.py \\
        --input-dir outputs/experiment \\
        --output-dir outputs/experiment/voting \\
        --sweep

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import logging
import math
import sys
from collections import Counter
from pathlib import Path

import geojson
from geojson import Feature, FeatureCollection, Point
from pyproj import Transformer
from shapely.geometry import shape

logger = logging.getLogger(__name__)

# Script version
__version__ = "1.1.0"

# CRS constants — internal coordinates are EPSG:32635 (UTM Zone 35N);
# GeoJSON spec (RFC 7946) mandates EPSG:4326 for output.
_SOURCE_CRS = "EPSG:32635"
_GEOJSON_CRS = "EPSG:4326"
_TO_4326 = Transformer.from_crs(
    _SOURCE_CRS, _GEOJSON_CRS, always_xy=True
)
_TO_UTM = Transformer.from_crs(
    _GEOJSON_CRS, _SOURCE_CRS, always_xy=True
)

# Constants aligned with preregistration Section 8.5
DISTANCE_THRESHOLD_METRES = 20.0  # Matches F1 evaluation tolerance


def geojson_coords_to_utm(lon: float, lat: float) -> tuple[float, float]:
    """Convert EPSG:4326 (lon, lat) to EPSG:32635 (easting, northing).

    Convenience wrapper for downstream code that needs UTM coordinates
    from GeoJSON features (e.g., raster crop extraction).

    Args:
        lon: Longitude in degrees.
        lat: Latitude in degrees.

    Returns:
        Tuple of (easting, northing) in EPSG:32635 metres.
    """
    return _TO_UTM.transform(lon, lat)


def coords_are_geographic(x: float, y: float) -> bool:
    """Detect whether coordinates are geographic (EPSG:4326) or projected.

    Uses a simple magnitude heuristic: UTM easting/northing values are
    typically > 100,000, while lon/lat are bounded by ±180/±90.

    Args:
        x: X coordinate (easting or longitude).
        y: Y coordinate (northing or latitude).

    Returns:
        True if coordinates appear to be geographic (EPSG:4326).
    """
    return abs(x) <= 180 and abs(y) <= 90


def centroid_from_geometry(geom_dict: dict) -> tuple[float, float]:
    """
    Extract centroid coordinates from a GeoJSON geometry.

    Uses Shapely for robust centroid computation, with a fallback for
    malformed geometries that cannot be parsed.

    Args:
        geom_dict: GeoJSON (Geographic JavaScript Object Notation) geometry
            dictionary.

    Returns:
        Tuple of (x, y) centroid coordinates.
    """
    try:
        geom = shape(geom_dict)
        centroid = geom.centroid
        return (centroid.x, centroid.y)
    except Exception:
        # Fallback for malformed geometries
        if geom_dict.get("type") == "Point":
            coords = geom_dict.get("coordinates", [0, 0])
            return (coords[0], coords[1])
        return (0, 0)


def euclidean_distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Calculate Euclidean distance between two projected coordinate points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def deduplicate_within_pass(
    features: list[dict],
    distance_thresh: float = DISTANCE_THRESHOLD_METRES,
) -> list[dict]:
    """
    Deduplicate detections within a single pass using 20 m tolerance.

    Implements preregistration Section 8.5 Step 1: "Within-pass deduplication".
    Prevents overlapping tiles from contributing multiple votes for the same
    physical location within a single pass.

    Uses greedy clustering: each unvisited detection seeds a new cluster,
    absorbing all remaining detections within the distance threshold.

    Args:
        features: List of GeoJSON features from a single pass.
        distance_thresh: Maximum distance (metres) for considering detections
            as duplicates.

    Returns:
        List of deduplicated detection dicts, each containing centroid
        coordinates, majority label, source tiles, and cluster size.
    """
    if not features:
        return []

    # Extract centroids and metadata
    detections = []
    for f in features:
        centroid = centroid_from_geometry(f.get("geometry", {}))
        props = f.get("properties", {})
        detections.append({
            "centroid": centroid,
            "label": props.get("subtype", "mound"),
            "source_tile": props.get("source_tile") or props.get("tile_id", "unknown"),
            "original": f,
        })

    # Greedy clustering
    clusters: list[list[dict]] = []
    used: set[int] = set()

    for i, det in enumerate(detections):
        if i in used:
            continue

        cluster = [det]
        used.add(i)

        for j, candidate in enumerate(detections):
            if j in used:
                continue

            dist = euclidean_distance(det["centroid"], candidate["centroid"])
            if dist <= distance_thresh:
                cluster.append(candidate)
                used.add(j)

        clusters.append(cluster)

    # Create deduplicated features (cluster centroids)
    deduped = []
    for cluster in clusters:
        # Compute mean centroid
        xs = [d["centroid"][0] for d in cluster]
        ys = [d["centroid"][1] for d in cluster]
        mean_centroid = (sum(xs) / len(xs), sum(ys) / len(ys))

        # Majority label
        labels = [d["label"] for d in cluster]
        majority_label = Counter(labels).most_common(1)[0][0]

        # Source tiles (for provenance)
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
    Cluster detections across passes using 20 m tolerance.

    Implements preregistration Section 8.5 Steps 2-5:

    - Pool deduplicated detections from all passes
    - Cluster using distance threshold (greedy star clustering)
    - Count votes (distinct passes per cluster)

    Note: Uses greedy star clustering (seed-based), not agglomerative.
    Cluster composition is order-dependent: different input orderings can
    produce different clusters for detections near the threshold boundary.
    This is a deliberate design choice for performance; the effect is
    minimal at the 20 m tolerance used in this project.

    Args:
        pass_detections: Dict mapping pass_id to list of deduplicated
            detections.
        distance_thresh: Maximum distance (metres) for clustering.

    Returns:
        List of cluster dicts, each containing centroid, majority label,
        vote count, contributing passes, source tiles, and cluster size.
    """
    # Pool all detections with pass identifiers
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

    # Greedy clustering
    clusters: list[list[dict]] = []
    used: set[int] = set()

    for i, det in enumerate(pool):
        if i in used:
            continue

        cluster = [det]
        used.add(i)

        for j, candidate in enumerate(pool):
            if j in used:
                continue

            dist = euclidean_distance(det["centroid"], candidate["centroid"])
            if dist <= distance_thresh:
                cluster.append(candidate)
                used.add(j)

        clusters.append(cluster)

    # Compute cluster statistics
    result = []
    for cluster in clusters:
        # Mean centroid (Step 7)
        xs = [d["centroid"][0] for d in cluster]
        ys = [d["centroid"][1] for d in cluster]
        mean_centroid = (sum(xs) / len(xs), sum(ys) / len(ys))

        # Distinct passes contributing (Step 5)
        contributing_passes = sorted(set(d["pass_id"] for d in cluster))
        vote_count = len(contributing_passes)

        # Majority label
        labels = [d["label"] for d in cluster]
        majority_label = Counter(labels).most_common(1)[0][0]

        # Source tiles (provenance)
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


def apply_threshold(
    clusters: list[dict],
    threshold: int,
    total_passes: int,
) -> FeatureCollection:
    """
    Apply vote threshold and create output GeoJSON.

    Implements preregistration Section 8.5 Step 6: retain only clusters
    whose vote count meets or exceeds the specified threshold.

    Args:
        clusters: List of cluster dictionaries from cluster_across_passes().
        threshold: Minimum vote count to retain a cluster.
        total_passes: Total number of passes (for confidence calculation).

    Returns:
        GeoJSON FeatureCollection of consensus detections.
    """
    features = []

    for cluster in clusters:
        if cluster["vote_count"] >= threshold:
            # Reproject centroid from EPSG:32635 → EPSG:4326 for
            # GeoJSON spec compliance (RFC 7946 mandates WGS 84)
            utm_x, utm_y = cluster["centroid"]
            lon, lat = _TO_4326.transform(utm_x, utm_y)
            geom = Point((lon, lat))

            # Properties per preregistration Section 8.5 "Consensus Detection Output"
            props = {
                "subtype": cluster["label"],
                "confidence": cluster["vote_count"] / total_passes,
                "vote_count": cluster["vote_count"],
                "total_passes": total_passes,
                "contributing_passes": cluster["contributing_passes"],
                "source_tiles": cluster["source_tiles"],
                "cluster_size": cluster["cluster_size"],
            }

            features.append(Feature(geometry=geom, properties=props))

    return FeatureCollection(features)


def load_pass_detections(
    input_dir: Path,
    pass_filter: list[int] | None = None,
) -> dict[str, list[dict]]:
    """
    Load detection GeoJSON files from pass directories.

    Expected directory structure::

        input_dir/
            pass_01/*.geojson
            pass_02/*.geojson
            ...

    Also supports ``run_*`` directory naming as an alternative.

    Args:
        input_dir: Directory containing pass_XX subdirectories.
        pass_filter: Optional list of pass numbers to include (1-indexed).

    Returns:
        Dict mapping pass_id to list of GeoJSON features.
    """
    pass_dirs = sorted(input_dir.glob("pass_*"))

    if not pass_dirs:
        # Try alternative naming (run_*)
        pass_dirs = sorted(input_dir.glob("run_*"))

    if not pass_dirs:
        logger.warning("No pass_* or run_* directories found in %s", input_dir)
        return {}

    result: dict[str, list[dict]] = {}

    for pass_dir in pass_dirs:
        # Extract pass number from directory name
        pass_name = pass_dir.name
        try:
            if pass_name.startswith("pass_"):
                pass_num = int(pass_name.replace("pass_", ""))
            elif pass_name.startswith("run_"):
                pass_num = int(pass_name.replace("run_", ""))
            else:
                continue
        except ValueError:
            continue

        # Apply filter if specified
        if pass_filter and pass_num not in pass_filter:
            continue

        # Load all GeoJSON files in pass directory
        features: list[dict] = []
        for geojson_file in pass_dir.glob("*.geojson"):
            # Skip metadata files
            if ".meta" in geojson_file.name:
                continue

            try:
                with open(geojson_file) as f:
                    data = json.load(f)
                    feats = data.get("features", [])
                    features.extend(feats)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Could not load %s: %s", geojson_file, e)

        if features:
            result[pass_name] = features
            logger.info("  Loaded %d detections from %s", len(features), pass_name)

    return result


def merge_passes(
    input_dir: Path,
    output_path: Path,
    threshold: int,
    pass_filter: list[int] | None = None,
) -> dict:
    """
    Execute the full voting pipeline: load, deduplicate, cluster, threshold.

    This is the main merge function that orchestrates all steps of the
    preregistration Section 8.5 voting algorithm.

    Args:
        input_dir: Directory containing pass subdirectories.
        output_path: Path for output GeoJSON file.
        threshold: Minimum vote count to retain a detection.
        pass_filter: Optional list of pass numbers to include.

    Returns:
        Summary statistics dictionary with counts at each pipeline stage.
    """
    logger.info("Loading passes from %s...", input_dir)
    raw_passes = load_pass_detections(input_dir, pass_filter)

    if not raw_passes:
        logger.error("No passes loaded.")
        return {"error": "No passes loaded"}

    total_passes = len(raw_passes)
    total_raw_detections = sum(len(feats) for feats in raw_passes.values())

    logger.info("Step 1: Within-pass deduplication (20 m tolerance)...")
    deduped_passes: dict[str, list[dict]] = {}
    total_deduped = 0
    for pass_id, features in raw_passes.items():
        deduped = deduplicate_within_pass(features)
        deduped_passes[pass_id] = deduped
        total_deduped += len(deduped)
        logger.info("  %s: %d -> %d detections", pass_id, len(features), len(deduped))

    logger.info("Step 2-5: Cross-pass clustering and vote counting...")
    clusters = cluster_across_passes(deduped_passes)
    logger.info("  Generated %d unique clusters", len(clusters))

    # Vote distribution
    vote_counts = Counter(c["vote_count"] for c in clusters)
    logger.info("  Vote distribution: %s", dict(sorted(vote_counts.items())))

    logger.info("Step 6: Applying threshold T>=%d...", threshold)
    consensus = apply_threshold(clusters, threshold, total_passes)
    retained = len(consensus["features"])
    logger.info("  Retained %d/%d clusters", retained, len(clusters))

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output
    with open(output_path, "w") as f:
        geojson.dump(consensus, f, indent=2)
    logger.info("Saved consensus detections to %s", output_path)

    # Summary statistics
    stats = {
        "total_passes": total_passes,
        "pass_ids": sorted(raw_passes.keys()),
        "total_raw_detections": total_raw_detections,
        "total_deduped_detections": total_deduped,
        "total_clusters": len(clusters),
        "threshold": threshold,
        "retained_clusters": retained,
        "vote_distribution": dict(sorted(vote_counts.items())),
    }

    return stats


def threshold_sweep(
    input_dir: Path,
    output_dir: Path,
    pass_filter: list[int] | None = None,
) -> None:
    """
    Generate consensus outputs for every possible threshold value.

    Iterates from T=1 to T=total_passes, writing a separate GeoJSON file
    for each threshold along with a JSON summary of detection counts.

    Args:
        input_dir: Directory containing pass subdirectories.
        output_dir: Directory for output files.
        pass_filter: Optional list of pass numbers to include (1-indexed).
            When provided, only these passes are loaded and total_passes
            reflects the filtered count.
    """
    logger.info("Loading passes from %s...", input_dir)
    raw_passes = load_pass_detections(input_dir, pass_filter=pass_filter)

    if not raw_passes:
        logger.error("No passes loaded.")
        return

    total_passes = len(raw_passes)

    logger.info("Step 1: Within-pass deduplication...")
    deduped_passes: dict[str, list[dict]] = {}
    for pass_id, features in raw_passes.items():
        deduped_passes[pass_id] = deduplicate_within_pass(features)

    logger.info("Step 2-5: Cross-pass clustering...")
    clusters = cluster_across_passes(deduped_passes)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Generating outputs for thresholds 1 to %d...", total_passes)
    summary: dict = {"total_passes": total_passes, "thresholds": {}}

    for t in range(1, total_passes + 1):
        consensus = apply_threshold(clusters, t, total_passes)
        retained = len(consensus["features"])

        output_path = output_dir / f"consensus_t{t}.geojson"
        with open(output_path, "w") as f:
            geojson.dump(consensus, f, indent=2)

        summary["thresholds"][t] = retained
        logger.info("  T>=%d: %d detections -> %s", t, retained, output_path.name)

    # Write summary
    summary_path = output_dir / "voting_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info("Summary saved to %s", summary_path)


def main() -> None:
    """Command-line interface (CLI) for the merge-passes voting pipeline."""
    parser = argparse.ArgumentParser(
        description=(
            "Merge detection passes with consensus voting "
            "(preregistration Section 8.5)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Merge all passes with threshold 3
    python scripts/merge_passes.py \\
        --input-dir outputs/phase1-library \\
        --output outputs/phase1-library/merged_t3.geojson \\
        --threshold 3

    # Split K=10 into N=5 pool A (passes 1-5)
    python scripts/merge_passes.py \\
        --input-dir outputs/experiment \\
        --output outputs/experiment/pool_a_t3.geojson \\
        --passes 1,2,3,4,5 \\
        --threshold 3

    # Generate all threshold outputs
    python scripts/merge_passes.py \\
        --input-dir outputs/experiment \\
        --output-dir outputs/experiment/voting \\
        --sweep

Notes:
    - Implements preregistration Section 8.5 voting algorithm
    - Uses 20 m spatial tolerance (matches F1 evaluation)
    - Within-pass deduplication handles overlapping tiles
    - Output includes confidence (vote_count / total_passes)
        """,
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing pass_XX subdirectories with detection GeoJSONs",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for merged consensus GeoJSON (required unless --sweep)",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for threshold sweep (used with --sweep)",
    )

    parser.add_argument(
        "--threshold",
        "-t",
        type=int,
        default=1,
        help="Minimum vote count to retain detection (default: 1)",
    )

    parser.add_argument(
        "--passes",
        type=str,
        help=(
            "Comma-separated pass numbers to include "
            "(e.g., '1,2,3,4,5' for N=5 pool A)"
        ),
    )

    parser.add_argument(
        "--sweep",
        action="store_true",
        help="Generate outputs for all thresholds (requires --output-dir)",
    )

    args = parser.parse_args()

    # Parse pass filter
    pass_filter = None
    if args.passes:
        try:
            pass_filter = [int(p.strip()) for p in args.passes.split(",")]
        except ValueError:
            logger.error("--passes must be comma-separated integers")
            sys.exit(1)

    # Validate arguments and dispatch
    if args.sweep:
        if not args.output_dir:
            logger.error("--sweep requires --output-dir")
            sys.exit(1)
        threshold_sweep(args.input_dir, args.output_dir, pass_filter=pass_filter)
    else:
        if not args.output:
            logger.error("--output required (unless using --sweep)")
            sys.exit(1)
        merge_passes(args.input_dir, args.output, args.threshold, pass_filter)


if __name__ == "__main__":
    main()
