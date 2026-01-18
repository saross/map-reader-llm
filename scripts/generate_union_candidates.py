"""
Generate Union Candidates from Multiple Detection Runs
=======================================================

Clusters detections from multiple runs using distance-based matching (20m)
to align with F1 evaluation spatial tolerance. Used in the two-stage pipeline
to aggregate proposals from multiple runs before verification.

Usage:
    python scripts/generate_union_candidates.py \\
        --input outputs/proposer_runs \\
        --output outputs/union_candidates.geojson

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import math
from pathlib import Path
from shapely.geometry import shape
import numpy as np
import geojson
from geojson import FeatureCollection


def get_centroid(geom_bounds):
    """Get centroid coordinates from geometry bounds [minx, miny, maxx, maxy]."""
    minx, miny, maxx, maxy = geom_bounds
    return ((minx + maxx) / 2, (miny + maxy) / 2)


def centroid_distance(bounds_a, bounds_b):
    """
    Calculate Euclidean distance between centroids of two bounding boxes.

    Returns distance in coordinate units (metres for EPSG:32635).
    """
    cx_a, cy_a = get_centroid(bounds_a)
    cx_b, cy_b = get_centroid(bounds_b)
    return math.sqrt((cx_a - cx_b) ** 2 + (cy_a - cy_b) ** 2)


def cluster_detections(all_detections, distance_thresh=20.0):
    """
    Cluster detections using distance-based matching.

    Uses 20m centroid distance threshold to match F1 evaluation spatial tolerance,
    ensuring consistency between voting aggregation and metric calculation.

    Args:
        all_detections: Dict mapping run_id to list of GeoJSON features.
        distance_thresh: Maximum centroid distance (metres) for clustering. Default 20m.

    Returns:
        List of clusters, where each cluster is a list of detection dicts.
    """
    pool = []
    # Flatten
    for run_id, feats in all_detections.items():
        for f in feats:
            props = f.get("properties", {})
            try:
                g = shape(f["geometry"])
                geom_box = g.bounds  # minx, miny, maxx, maxy
                legacy_box = [geom_box[1], geom_box[0], geom_box[3], geom_box[2]]  # yx
            except:
                continue

            pool.append({
                "box": legacy_box,
                "geom_bounds": geom_box,
                "label": props.get("subtype", "mound"),
                "source_tile": props.get("source_tile") or props.get("tile_id"),
                "run_id": run_id,
                "original": f
            })

    # Greedy Clustering using distance-based matching
    clusters = []
    used_indices = set()

    for i, det in enumerate(pool):
        if i in used_indices:
            continue
        current_cluster = [det]
        used_indices.add(i)

        for j, candidate in enumerate(pool):
            if j in used_indices:
                continue
            if candidate["source_tile"] != det["source_tile"]:
                continue  # Must be same tile

            # Use centroid distance for consistency with F1 evaluation
            dist = centroid_distance(det["geom_bounds"], candidate["geom_bounds"])
            if dist <= distance_thresh:
                current_cluster.append(candidate)
                used_indices.add(j)
        clusters.append(current_cluster)
    return clusters

def generate_union(input_dir, output_path):
    input_path = Path(input_dir)
    run_files = list(input_path.glob("run_*.geojson"))
    print(f"Found {len(run_files)} runs in {input_dir}")
    
    all_dets = {}
    for rf in run_files:
        with open(rf) as f:
            fc = json.load(f)
            all_dets[rf.stem] = fc.get("features", [])
            
    clusters = cluster_detections(all_dets)
    print(f"Generated {len(clusters)} unique clusters from {sum(len(v) for v in all_dets.values())} detections.")
    
    # Create Union Features (Vote >= 1)
    union_features = []
    for cl in clusters:
        # Averaging Geometry
        boxes = np.array([c["box"] for c in cl])
        avg_box = np.mean(boxes, axis=0).tolist() # ymin, xmin, ymax, xmax
        
        # Convert to Geom (minx, miny, maxx, maxy)
        minx, miny, maxx, maxy = avg_box[1], avg_box[0], avg_box[3], avg_box[2]
        
        feat = {
            "type": "Feature",
            "properties": {
                "source_tile": cl[0]["source_tile"],
                "proposer_votes": len(set(c["run_id"] for c in cl)),
                "cluster_size": len(cl)
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [minx, miny],
                    [maxx, miny],
                    [maxx, maxy],
                    [minx, maxy],
                    [minx, miny]
                ]]
            }
        }
        union_features.append(feat)
        
    with open(output_path, 'w') as f:
        geojson.dump(FeatureCollection(union_features), f)
    print(f"Saved {len(union_features)} union candidates to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cluster detections from multiple runs into union candidates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate union candidates from proposer runs
    python scripts/generate_union_candidates.py \\
        --input outputs/proposer_runs \\
        --output outputs/union_candidates.geojson

Notes:
    - Input directory should contain run_*.geojson files
    - Uses 20m centroid distance threshold for clustering (matches F1 evaluation)
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
