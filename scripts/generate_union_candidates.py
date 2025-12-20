
import os
import sys
import json
import argparse
import logging
from pathlib import Path
from shapely.geometry import shape, box, mapping
import numpy as np
import geojson
from geojson import FeatureCollection

# Reuse IoU logic
def calculate_iou(boxA, boxB):
    b1 = box(boxA[1], boxA[0], boxA[3], boxA[2])
    b2 = box(boxB[1], boxB[0], boxB[3], boxB[2])
    if not b1.intersects(b2): return 0.0
    return b1.intersection(b2).area / b1.union(b2).area

def cluster_detections(all_detections, iou_thresh=0.5):
    pool = []
    # Flatten
    for run_id, feats in all_detections.items():
        for f in feats:
            props = f.get("properties", {})
            try:
                g = shape(f["geometry"])
                geom_box = g.bounds # minx, miny, maxx, maxy
                legacy_box = [geom_box[1], geom_box[0], geom_box[3], geom_box[2]] # yx
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
            
    # Greedy Clustering
    clusters = []
    used_indices = set()
    
    for i, det in enumerate(pool):
        if i in used_indices: continue
        current_cluster = [det]
        used_indices.add(i)
        
        for j, candidate in enumerate(pool):
            if j in used_indices: continue
            if candidate["source_tile"] != det["source_tile"]: continue # Must be same tile!
            
            if calculate_iou(det["box"], candidate["box"]) > iou_thresh:
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    generate_union(args.input, args.output)
