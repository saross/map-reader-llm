
import json
import argparse
from pathlib import Path
import geopandas as gpd
import pandas as pd
import sys
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import INPUTS_DIR

def get_map_name(tile_filename):
    known_maps = [
        "K-35-062-2_Rakovski",
        "K-35-052-4_32635",
        "K-35-053-3_Elenovo",
        "K-35-078-1_Lesovo"
    ]
    for m in known_maps:
        if tile_filename.startswith(m):
            return m
    return "Unknown"

def extract_errors(detection_file, bounds_file, out_fp, out_fn, buffer_meters=20, edge_exclusion=0):
    print(f"--- Extracting Errors (FP/FN) ---")
    print(f"Detections: {detection_file}")
    print(f"Bounds: {bounds_file}")
    
    # 1. Load Data
    try:
        gdf_det = gpd.read_file(detection_file)
        gdf_bounds = gpd.read_file(bounds_file)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    # Infer Map name for detections
    gdf_det['Map'] = gdf_det['source_tile'].apply(get_map_name)
    
    # Target CRS
    target_crs = "EPSG:32635"
    if gdf_det.crs != target_crs: gdf_det = gdf_det.to_crs(target_crs)
    if gdf_bounds.crs != target_crs: gdf_bounds = gdf_bounds.to_crs(target_crs)

    # Load References
    ref_files = list(INPUTS_DIR.glob("reference_*.geojson"))
    ref_gdfs = []
    for rf in ref_files:
        gdf = gpd.read_file(rf)
        if gdf.crs != target_crs: gdf = gdf.to_crs(target_crs)
        map_name_from_file = rf.stem.replace("reference_", "")
        gdf['Map'] = map_name_from_file 
        # Apply Buffer to Reference Logic (same as eval script)
        gdf['geometry'] = gdf.geometry.buffer(buffer_meters)
        ref_gdfs.append(gdf)
        
    gdf_ref_all = pd.concat(ref_gdfs, ignore_index=True)
    
    # Identify tile bounds features (if merged in det file, separate them)
    # But here we require explicit bounds_file input for robustness
    tile_bounds_features = gdf_bounds

    # Filter detections to exclude valid bounds features if present in det file
    if 'label' in gdf_det.columns:
         gdf_det = gdf_det[gdf_det['label'] != 'processed_tile_bounds']

    all_fp = []
    all_fn = []
    
    maps = gdf_det['Map'].unique()
    # Also check bounds maps in case no detections
    maps = set(maps).union(set([get_map_name(n) for n in gdf_bounds['tile_name'].unique()]))

    for map_name in maps:
        if map_name == "Unknown": continue
        
        # Scope
        map_bounds = tile_bounds_features[tile_bounds_features['tile_name'].str.startswith(map_name)]
        if map_bounds.empty:
            print(f"[{map_name}] No bounds found. Skipping.")
            continue
            
        searched_area = map_bounds.geometry.union_all()

        # Apply Edge Exclusion if requested
        if edge_exclusion > 0:
            searched_area = searched_area.buffer(-edge_exclusion)
        
        # Filter Ref
        ref_on_map = gdf_ref_all[gdf_ref_all['Map'] == map_name]
        if ref_on_map.empty:
             print(f"[{map_name}] No references found.")
             continue
             
        # Ref in Scope (Intersects Searched Area)
        # Note: ref_on_map is already buffered.
        ref_in_scope = ref_on_map[ref_on_map.intersects(searched_area)]
        
        # Filter Det
        det_on_map = gdf_det[gdf_det['Map'] == map_name]
        
        # consistency check: Filter Detections to Searched Area (Eroded)
        if edge_exclusion > 0 and not det_on_map.empty:
             det_on_map = det_on_map[det_on_map.geometry.centroid.within(searched_area)]
        
        # FP Logic: Detection that does NOT intersect any Ref in Scope
        # Left join Det -> Ref
        join_fp = gpd.sjoin(det_on_map, ref_in_scope, how='left', predicate='intersects')
        # FPs are those where index_right is NaN
        fp_indices = join_fp[join_fp.index_right.isna()].index
        fp_features = det_on_map.loc[fp_indices].copy()
        fp_features['error_type'] = 'False Positive'
        all_fp.append(fp_features)
        
        # FN Logic: Ref in Scope that does NOT intersect any Detection
        # Left join Ref -> Det
        join_fn = gpd.sjoin(ref_in_scope, det_on_map, how='left', predicate='intersects')
        # FNs are those where index_right is NaN
        fn_indices = join_fn[join_fn.index_right.isna()].index
        fn_features = ref_in_scope.loc[fn_indices].copy()
        fn_features['error_type'] = 'False Negative'
        all_fn.append(fn_features)
        
        print(f"[{map_name}] Found {len(fp_features)} FPs and {len(fn_features)} FNs.")

    # Save outputs
    if all_fp:
        gdf_fp = pd.concat(all_fp, ignore_index=True)
        gdf_fp.to_file(out_fp, driver="GeoJSON")
        print(f"Saved {len(gdf_fp)} False Positives to {out_fp}")
    else:
        print("No False Positives found.")
        # Create empty
        gpd.GeoDataFrame(columns=['geometry'], crs=target_crs).to_file(out_fp, driver="GeoJSON")

    if all_fn:
        gdf_fn = pd.concat(all_fn, ignore_index=True)
        gdf_fn.to_file(out_fn, driver="GeoJSON")
        print(f"Saved {len(gdf_fn)} False Negatives to {out_fn}")
    else:
        print("No False Negatives found.")
        gpd.GeoDataFrame(columns=['geometry'], crs=target_crs).to_file(out_fn, driver="GeoJSON")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--detections", required=True)
    parser.add_argument("--bounds", required=True)
    parser.add_argument("--out_fp", required=True, help="Output path for False Positives")
    parser.add_argument("--out_fn", required=True, help="Output path for False Negatives")
    parser.add_argument("--buffer", type=int, default=20)
    parser.add_argument("--edge_exclusion", type=float, default=0, help="Margin in meters to exclude from search area edges")
    args = parser.parse_args()
    
    extract_errors(args.detections, args.bounds, args.out_fp, args.out_fn, args.buffer, args.edge_exclusion)
