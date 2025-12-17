
import json
import argparse
from pathlib import Path
from shapely.geometry import shape, box, Point
from shapely.ops import unary_union
import geopandas as gpd
import pandas as pd
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import RESULTS_DIR, INPUTS_DIR

def evaluate(detection_file, reference_file, buffer_meters=20):
    print(f"--- Automated Evaluation ---")
    print(f"Detections: {detection_file}")
    print(f"Ground Truth: {reference_file}")
    print(f"Buffer: {buffer_meters}m")

    # Load Detections
    try:
        gdf_det = gpd.read_file(detection_file)
        print(f"Loaded {len(gdf_det)} detections.")
    except Exception as e:
        print(f"Error loading detections: {e}")
        return

    # Load Ground Truth
    try:
        gdf_ref = gpd.read_file(reference_file)
        print(f"Loaded {len(gdf_ref)} reference mounds.")
    except Exception as e:
        print(f"Error loading reference: {e}")
        return

    # Ensure CRS matches (EPSG:32635)
    target_crs = "EPSG:32635"
    if gdf_det.crs != target_crs:
        print(f"Reprojecting detections to {target_crs}...")
        gdf_det = gdf_det.to_crs(target_crs)
    if gdf_ref.crs != target_crs:
        print(f"Reprojecting reference to {target_crs}...")
        gdf_ref = gdf_ref.to_crs(target_crs)

    # Buffer Ground Truth Points to create "Hit Zones"
    # User Goal: 20m buffer around centroid
    gdf_ref['geometry'] = gdf_ref.geometry.buffer(buffer_meters)

    # Spatial Join: Which detections intersect with buffered reference?
    # predicate='intersects'
    join_left = gpd.sjoin(gdf_det, gdf_ref, how='left', predicate='intersects')
    join_right = gpd.sjoin(gdf_det, gdf_ref, how='right', predicate='intersects')

    # True Positives (TP): Detections that matched a Reference
    # We count UNIQUE reference IDs that were hit.
    # Note: Multiple detections might hit one reference (e.g. duplicates), 
    # and one detection might hit multiple references (rare if buffer small).
    # Strict definition: Count the number of Reference Features that were "found".
    tp_features = join_right[join_right.index_left.notnull()]
    tp_count = len(tp_features['index_left'].unique()) # How many Det IDs matched?
    # Actually, for Recall, we verify how many Ref items were hit.
    matched_ref_indices = join_right[join_right.index_left.notnull()].index.unique()
    tp = len(matched_ref_indices) 

    # False Negatives (FN): Reference mounds that were NOT hit
    fn = len(gdf_ref) - tp

    # False Positives (FP): Detections that hit NOTHING
    # Identify detection indices that are NOT in the join_left where index_right is present
    matched_det_indices = join_left[join_left.index_right.notnull()].index.unique()
    fp = len(gdf_det) - len(matched_det_indices)

    # Metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print("\n--- Results ---")
    print(f"True Positives (Guessed Correctly): {tp}")
    print(f"False Negatives (Missed): {fn}")
    print(f"False Positives (Hallucinations): {fp}")
    print(f"----------------")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

    # Optional: Save FP/FN for visualization
    # ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--detections", type=str, required=True, help="Path to detection GeoJSON")
    parser.add_argument("--reference", type=str, required=True, help="Path to reference GeoJSON")
    args = parser.parse_args()
    
    evaluate(args.detections, args.reference)
