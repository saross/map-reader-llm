
import geopandas as gpd
import pandas as pd
from pathlib import Path
import json
import numpy as np

# Import metrics logic (copied simplified version to be standalone/reliable)
def calculate_metrics(pred_gdf, ref_gdf, bounds_gdf):
    if pred_gdf.empty:
        return 0, 0, 0
    
    # Spatial Join with Tolerance
    # Buffer refs by 20m
    ref_buf = ref_gdf.copy()
    ref_buf['geometry'] = ref_buf.geometry.buffer(20)
    
    # Check hits
    # Preds that hit a Ref
    hits = gpd.sjoin(pred_gdf, ref_buf, how='inner', predicate='intersects')
    tp = len(hits.index.unique())
    fp = len(pred_gdf) - tp
    
    # Check misses (Refs in bounds not hit)
    # Filter refs to bounds
    search_area = bounds_gdf.geometry.union_all()
    refs_in_scope = ref_gdf[ref_gdf.intersects(search_area)]
    
    # We need to use the HITs to determine how many refs were found.
    # Group hits by index_right (ref index)
    found_refs = len(hits['index_right'].unique())
    fn = len(refs_in_scope) - found_refs
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = found_refs / (found_refs + fn) if (found_refs + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return precision, recall, f1

def main():
    base_dir = Path("outputs/results/v4.6_opt")
    run_files = list(base_dir.glob("verified_run_01_v4_9_lowtemp_run_*.geojson"))
    print(f"Found {len(run_files)} run files.")
    
    if not run_files:
        print("No files found.")
        return

    # Load All
    gdfs = []
    for f in run_files:
        try:
            gdf = gpd.read_file(f)
            if not gdf.empty:
                # Add run ID
                gdf['run_id'] = f.stem
                gdfs.append(gdf)
        except Exception as e:
            print(f"Skipping empty or error file {f}: {e}")
            
    if not gdfs:
        print("No valid data loaded.")
        return
        
    all_preds = pd.concat(gdfs, ignore_index=True)
    print(f"Total detections across all runs: {len(all_preds)}")
    
    # Clustering (Deduplicate)
    # We assume detections of the same mound overlap significantly.
    # WBF usually averages boxes. Here we just want to count VOTES.
    # Simple strategy: Spatially cluster.
    
    # Buffer slightly to merge near-duplicates
    # Actually, since they come from the SAME candidate source (Stage 1), 
    # they should have IDENTICAL geometry/tile_id if they are the same candidate.
    # Let's check if 'tile_id' and 'geometry' are preserved.
    # Yes, 5_verify_crops passes through the feature.
    # So we can group by 'candidate_id' or just simple geometry string representation?
    # Better: Use the input candidate index/ID if available.
    # The input candidates likely have an ID or we can generate one from geometry centroid.
    
    all_preds['geom_wkt'] = all_preds.geometry.to_wkt()
    
    # Group by unique geometry
    grouped = all_preds.groupby('geom_wkt').agg({
        'run_id': 'count', # Number of runs detecting this
        'geometry': 'first',
        'verifier_avg_score': 'mean' # Avg confidence
    }).rename(columns={'run_id': 'votes'})
    
    unique_candidates = gpd.GeoDataFrame(grouped, geometry='geometry', crs=all_preds.crs)
    print(f"Unique candidates identified: {len(unique_candidates)}")
    print(unique_candidates['votes'].value_counts().sort_index())
    
    # Load Refs and Bounds for Scoring
    ref_path = Path("inputs/references/kurgans_gt.geojson") # Hardcoded or find
    # Actually use config paths, but for now assumption is ok or pass arg
    # I'll try to load from the verify script arg if possible, but hardcoding for the analysis task is faster.
    # Search for GT
    ref_files = list(Path("inputs/references").glob("*.geojson"))
    gt_file = next((f for f in ref_files if "gt" in f.name), None)
    
    # Load Bounds (from run_01)
    bounds_path = Path("outputs/results/v4.2_temp_0_7_train/run_01_bounds.geojson")
    
    if not gt_file or not bounds_path.exists():
        print("Missing GT or Bounds file.")
        return
        
    gdf_ref = gpd.read_file(gt_file)
    if gdf_ref.crs != unique_candidates.crs:
        gdf_ref = gdf_ref.to_crs(unique_candidates.crs)
        
    gdf_bounds = gpd.read_file(bounds_path)
    if gdf_bounds.crs != unique_candidates.crs:
        gdf_bounds = gdf_bounds.to_crs(unique_candidates.crs)

    # Calculate Metrics for N=1 to 5
    print("\n--- Consensus Results ---")
    print(f"{'N':<5} {'Count':<10} {'Precision':<10} {'Recall':<10} {'F1':<10}")
    
    results = []
    
    for n in range(1, 6):
        subset = unique_candidates[unique_candidates['votes'] >= n]
        if subset.empty:
            p, r, f1 = 0, 0, 0
            count = 0
        else:
            p, r, f1 = calculate_metrics(subset, gdf_ref, gdf_bounds)
            count = len(subset)
            
        print(f"{n:<5} {count:<10} {p:<10.4f} {r:<10.4f} {f1:<10.4f}")
        results.append({"n": n, "f1": f1})

if __name__ == "__main__":
    main()
