#!/usr/bin/env python3
"""
Generate Union Candidates from Multiple Detection Runs
=======================================================

Description:
    Clusters detections from multiple runs using distance-based matching (20 m)
    to align with F1 evaluation spatial tolerance. Used in the two-stage pipeline
    to aggregate proposals from multiple runs before verification.

Usage:
    python scripts/generate_union_candidates.py \
        --input outputs/proposer_runs \
        --output outputs/union_candidates.geojson

Inputs:
    - Directory containing run_*.geojson detection files from proposer runs

Outputs:
    - Single GeoJSON FeatureCollection of union candidates with vote counts

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import math
from pathlib import Path

import geojson
import numpy as np
from geojson import FeatureCollection
from shapely.geometry import shape


def get_centroid(geom_bounds: tuple[float, ...]) -> tuple[float, float]:
    """Return centroid coordinates from geometry bounds (minx, miny, maxx, maxy)."""
    minx, miny, maxx, maxy = geom_bounds
    return ((minx + maxx) / 2, (miny + maxy) / 2)


def centroid_distance(
    bounds_a: tuple[float, ...],
    bounds_b: tuple[float, ...],
) -> float:
    """
    Calculate Euclidean distance between centroids of two bounding boxes.

    Returns distance in coordinate units (metres for European Petroleum Survey
    Group (EPSG):32635).
    """
    cx_a, cy_a = get_centroid(bounds_a)
    cx_b, cy_b = get_centroid(bounds_b)
    return math.sqrt((cx_a - cx_b) ** 2 + (cy_a - cy_b) ** 2)


def cluster_detections(
    all_detections: dict[str, list[dict]],
    distance_thresh: float = 20.0,
) -> list[list[dict]]:
    """
    Cluster detections using distance-based matching.

    Uses a 20 m centroid distance threshold to match F1 evaluation spatial
    tolerance, ensuring consistency between voting aggregation and metric
    calculation.

    Args:
        all_detections: Mapping of run_id to list of GeoJSON features.
        distance_thresh: Maximum centroid distance (metres) for clustering.
            Default 20 m.

    Returns:
        List of clusters, where each cluster is a list of detection dicts.
    """
    pool: list[dict] = []

    # Flatten all runs into a single pool of detections
    for run_id, feats in all_detections.items():
        for f in feats:
            props = f.get("properties", {})
            try:
                g = shape(f["geometry"])
                geom_box = g.bounds  # (minx, miny, maxx, maxy)
                # Legacy box format: (ymin, xmin, ymax, xmax)
                legacy_box = [
                    geom_box[1],
                    geom_box[0],
                    geom_box[3],
                    geom_box[2],
                ]
            except (KeyError, ValueError, TypeError):
                continue

            pool.append({
                "box": legacy_box,
                "geom_bounds": geom_box,
                "label": props.get("subtype", "mound"),
                "source_tile": (
                    props.get("source_tile") or props.get("tile_id")
                ),
                "run_id": run_id,
                "original": f,
            })

    # Greedy clustering using distance-based matching
    clusters: list[list[dict]] = []
    used_indices: set[int] = set()

    for i, det in enumerate(pool):
        if i in used_indices:
            continue
        current_cluster = [det]
        used_indices.add(i)

        for j, candidate in enumerate(pool):
            if j in used_indices:
                continue
            # Detections must share the same tile to cluster
            if candidate["source_tile"] != det["source_tile"]:
                continue

            # Centroid distance for consistency with F1 evaluation
            dist = centroid_distance(
                det["geom_bounds"],
                candidate["geom_bounds"],
            )
            if dist <= distance_thresh:
                current_cluster.append(candidate)
                used_indices.add(j)

        clusters.append(current_cluster)

    return clusters


def generate_union(input_dir: str, output_path: str) -> None:
    """
    Load proposer runs, cluster detections, and write union candidates.

    Args:
        input_dir: Directory containing run_*.geojson detection files.
        output_path: Output path for the union candidates GeoJSON file.
    """
    input_path = Path(input_dir)
    run_files = list(input_path.glob("run_*.geojson"))
    print(f"Found {len(run_files)} runs in {input_dir}")

    all_dets: dict[str, list] = {}
    for rf in run_files:
        with open(rf) as f:
            fc = json.load(f)
            all_dets[rf.stem] = fc.get("features", [])

    clusters = cluster_detections(all_dets)
    total_detections = sum(len(v) for v in all_dets.values())
    print(
        f"Generated {len(clusters)} unique clusters "
        f"from {total_detections} detections."
    )

    # Create union features (vote >= 1)
    union_features: list[dict] = []
    for cl in clusters:
        # Average geometry across cluster members
        boxes = np.array([c["box"] for c in cl])
        avg_box = np.mean(boxes, axis=0).tolist()  # ymin, xmin, ymax, xmax

        # Convert from legacy (ymin, xmin, ymax, xmax) to geom order
        minx, miny, maxx, maxy = (
            avg_box[1],
            avg_box[0],
            avg_box[3],
            avg_box[2],
        )

        feat = {
            "type": "Feature",
            "properties": {
                "source_tile": cl[0]["source_tile"],
                "proposer_votes": len(set(c["run_id"] for c in cl)),
                "cluster_size": len(cl),
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [minx, miny],
                    [maxx, miny],
                    [maxx, maxy],
                    [minx, maxy],
                    [minx, miny],
                ]],
            },
        }
        union_features.append(feat)

    with open(output_path, "w") as f:
        geojson.dump(FeatureCollection(union_features), f)
    print(f"Saved {len(union_features)} union candidates to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Cluster detections from multiple runs into union candidates"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate union candidates from proposer runs
    python scripts/generate_union_candidates.py \\
        --input outputs/proposer_runs \\
        --output outputs/union_candidates.geojson

Notes:
    - Input directory should contain run_*.geojson files
    - Uses 20 m centroid distance threshold for clustering (matches F1 evaluation)
    - Output includes vote counts and cluster sizes for each candidate
        """,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Directory containing run_*.geojson detection files",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for union candidates GeoJSON file",
    )
    args = parser.parse_args()
    generate_union(args.input, args.output)
