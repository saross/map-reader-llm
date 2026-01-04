
import sys
import os
import argparse
import json
import geopandas as gpd
from pathlib import Path

# Setup Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

try:
    from scripts.lib_advanced_metrics import (
        calculate_f1_internal,
        calculate_tile_classification,
        bootstrap_tile_classification_ci,
        load_data,
    )
except ImportError:
    print("Error importing scripts.lib_advanced_metrics.")
    sys.exit(1)

def validate_file(pred_path, bounds_path, template_det_path):
    print(f"Validating: {pred_path}")
    
    # 1. Load Ground Truth (using template)
    # load_data returns (gdf_det, gdf_bounds, gdf_ref) treating template_det as the detection
    # We only want gdf_bounds and gdf_ref
    #load_data
    try:
        det_dummy, gdf_bounds, gdf_ref = load_data(template_det_path, bounds_path)
        print(f"Loaded Ref: {len(gdf_ref)} features. Maps: {gdf_ref['Map'].unique()}")
        print(f"Loaded Bounds: {len(gdf_bounds)} tiles. Sample Tile: {gdf_bounds.iloc[0]['tile_name'] if not gdf_bounds.empty else 'None'}")
    except Exception as e:
        print(f"Error loading ground truth: {e}")
        return

    # 2. Load Predictions
    try:
        gdf_pred = gpd.read_file(pred_path)
        # Check source_tile
        if not gdf_pred.empty:
             # Logic fix: Force CRS to 32635 because coordinates are clearly UTM
             # defaulting to 4326 causes reprojection errors
             gdf_pred.set_crs("EPSG:32635", allow_override=True, inplace=True)
             
             print(f"Loaded Pred: {len(gdf_pred)} candidates. Sample Source: {gdf_pred.iloc[0].get('source_tile', 'Missing')}")
             print(f"Ref Bounds: {gdf_ref.total_bounds}")
             print(f"Pred Bounds: {gdf_pred.total_bounds}")
             print(f"Ref CRS: {gdf_ref.crs} | Pred CRS: {gdf_pred.crs}")
    except Exception as e:
        print(f"Error loading predictions: {e}")
        return
        
    print(f"Total Candidates: {len(gdf_pred)}")
    
    # 3. Filter for Verified
    if "verified" in gdf_pred.columns:
        # Verified is boolean or 0/1?
        # GeoJSON saves booleans as true/false.
        # Pandas might load as bool or object.
        gdf_verified = gdf_pred[gdf_pred["verified"] == True]
    else:
        print("Warning: 'verified' column not found. Assuming all are verified.")
        gdf_verified = gdf_pred
        
    print(f"Verified Candidates: {len(gdf_verified)}")
    
    if len(gdf_verified) == 0:
        print("No verified candidates found.")
        return

    # 4. Calculate F1
    # Ensure CRS match
    if gdf_verified.crs != gdf_ref.crs:
        gdf_verified = gdf_verified.to_crs(gdf_ref.crs)
        
    p, r, f1 = calculate_f1_internal(gdf_verified, gdf_ref, gdf_bounds)
    
    print("\n=== Validation Results (Symbol-Level) ===")
    print(f"Precision: {p:.4f}")
    print(f"Recall:    {r:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print("==========================================")

    # 5. Calculate Tile-Level MCC (Section 4.2)
    tile_results = calculate_tile_classification(gdf_verified, gdf_ref, gdf_bounds)
    tile_ci = bootstrap_tile_classification_ci(gdf_verified, gdf_ref, gdf_bounds)

    print("\n=== Tile-Level Classification (MCC) ===")
    mcc = tile_results.get('mcc')
    sens = tile_results.get('sensitivity')
    spec = tile_results.get('specificity')
    mcc_ci = tile_ci.get('mcc', {})

    if mcc is not None:
        ci_str = ""
        if mcc_ci.get('ci_lower') is not None:
            ci_str = f" (95% CI: {mcc_ci['ci_lower']:.4f}-{mcc_ci['ci_upper']:.4f})"
        print(f"MCC:         {mcc:.4f}{ci_str}")
    else:
        print(f"MCC:         undefined")

    print(f"Sensitivity: {sens:.4f}" if sens is not None else "Sensitivity: undefined")
    print(f"Specificity: {spec:.4f}" if spec is not None else "Specificity: undefined")
    print(f"Tiles: {tile_results['n_populated']} populated, {tile_results['n_empty']} empty")
    print("========================================")

    # Save FP and FN files for Mining
    print("\nGenerating FP/FN files...")
    # Buffer Refs for matching
    gdf_ref_buf = gdf_ref.copy()
    gdf_ref_buf['geometry'] = gdf_ref_buf.geometry.buffer(20)
    
    # Identify FPs (Verified candidates not hitting any Ref)
    join_fp = gpd.sjoin(gdf_verified, gdf_ref_buf, how='left', predicate='intersects')
    fps = join_fp[join_fp.index_right.isna()].copy()
    
    # Identify FNs (Refs not hit by any Verified candidate)
    # Filter refs to bounds first
    processed_geometry = gdf_bounds.geometry.union_all()
    refs_in_scope = gdf_ref_buf[gdf_ref_buf.intersects(processed_geometry)].copy()
    
    join_fn = gpd.sjoin(refs_in_scope, gdf_verified, how='left', predicate='intersects')
    fns = join_fn[join_fn.index_right.isna()].copy()
    # Recover original geometry (unbuffered) for FNs
    fns = fns.merge(gdf_ref[['geometry']], left_index=True, right_index=True, how='left', suffixes=('_buf', ''))
    fns.set_geometry('geometry', inplace=True)
    if 'geometry_buf' in fns.columns: fns.drop(columns=['geometry_buf'], inplace=True)

    base_name = Path(pred_path).stem
    parent_dir = Path(pred_path).parent
    
    fp_path = parent_dir / f"{base_name}_fp.geojson"
    fn_path = parent_dir / f"{base_name}_fn.geojson"
    
    if not fps.empty:
        # Drop columns that cause save errors
        for col in ['index_right', 'Map_left', 'Map_right']: 
            if col in fps.columns: fps.drop(columns=[col], inplace=True)
        fps.to_file(fp_path, driver='GeoJSON')
        print(f"Saved {len(fps)} False Positives to {fp_path}")
        
    if not fns.empty:
        # Drop columns
        for col in ['index_right', 'Map_left', 'Map_right']:
             if col in fns.columns: fns.drop(columns=[col], inplace=True)
        fns.to_file(fn_path, driver='GeoJSON')
        print(f"Saved {len(fns)} False Negatives to {fn_path}")

    # Compare with Unfiltered (Base)
    print("\n--- Comparison (Unfiltered Input) ---")
    gdf_all = gpd.read_file(pred_path) # Reload full
    if not gdf_all.empty: gdf_all.set_crs("EPSG:32635", allow_override=True, inplace=True)
    if gdf_all.crs != gdf_ref.crs: gdf_all = gdf_all.to_crs(gdf_ref.crs)
    p_base, r_base, f1_base = calculate_f1_internal(gdf_all, gdf_ref, gdf_bounds)
    print(f"Base Precision: {p_base:.4f}")
    print(f"Base Recall:    {r_base:.4f}")
    print(f"Base F1:        {f1_base:.4f}")
    
    # Delta
    print(f"\nDelta Precision: {p - p_base:+.4f}")
    print(f"Delta Recall:    {r - r_base:+.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred", required=True)
    parser.add_argument("--bounds", required=True)
    parser.add_argument("--template", required=True)
    args = parser.parse_args()
    
    validate_file(args.pred, args.bounds, args.template)
