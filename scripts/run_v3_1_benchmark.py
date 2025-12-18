
import json
import logging
from pathlib import Path
import geojson
import sys
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
import warnings

# Suppress FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

# Add parent to path to import scripts
sys.path.append(os.getcwd())
import importlib.util

# Dynamic import for scripts starting with numbers
spec = importlib.util.spec_from_file_location("detect_mounds_batch", str(Path("scripts/4_detect_mounds_batch.py").absolute()))
detect_mounds_module = importlib.util.module_from_spec(spec)
sys.modules["detect_mounds_batch"] = detect_mounds_module
spec.loader.exec_module(detect_mounds_module)
from detect_mounds_batch import detect_mounds_versioned

from config import BASE_DIR, TILES_DIR, INPUTS_DIR, RESULTS_DIR
import rasterio
from shapely.geometry import box

def generate_bounds(manifest_path, output_path):
    print(f"Generating bounds from {manifest_path}...")
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    features = []
    crs = None
    
    for item in manifest:
        # Item is a string filename
        tile_path = Path(item)
        if (INPUTS_DIR / "tiles" / tile_path).exists():
             tile_path = INPUTS_DIR / "tiles" / tile_path
        else:
             # Search recursively
             found = list((INPUTS_DIR / "tiles").rglob(tile_path.name))
             if found:
                 tile_path = found[0]
             else:
                 print(f"Warning: Tile {tile_path} not found.")
                 continue

        try:
            with rasterio.open(tile_path) as src:
                b = src.bounds
                geom = box(b.left, b.bottom, b.right, b.top)
                features.append({
                    "geometry": geom,
                    "properties": {"tile_name": tile_path.name}
                })
                if crs is None:
                    crs = src.crs
        except Exception as e:
            print(f"Error reading {tile_path}: {e}")

    if not features:
        print("No bounds features generated.")
        return

    gdf = gpd.GeoDataFrame.from_features(features, crs=crs)
    gdf.to_file(output_path, driver="GeoJSON")
    print(f"Saved bounds to {output_path}")

def get_map_name(tile_filename):
    """Infers map name from tile filename."""
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


def evaluate_performance(detection_file, bounds_file, output_prefix, buffer_meters=20):
    """
    Evaluates detections against ground truth within the searched bounds.
    Generates Metrics and FP/FN maps.
    """
    print(f"\n--- Starting Evaluation ---")
    print(f"Detections: {detection_file}")
    print(f"Bounds: {bounds_file}")

    target_crs = "EPSG:32635"

    # 1. Load Detections & Bounds
    try:
        gdf_det = gpd.read_file(detection_file)
        gdf_bounds = gpd.read_file(bounds_file)
        
        # CRS Check
        if gdf_det.crs != target_crs: 
            if gdf_det.crs is None:
                gdf_det.set_crs(target_crs, inplace=True) # Assume correct if missing
            else:
                gdf_det = gdf_det.to_crs(target_crs)
                
        if gdf_bounds.crs != target_crs:
            if gdf_bounds.crs is None:
                gdf_bounds.set_crs(target_crs, inplace=True)
            else:
                gdf_bounds = gdf_bounds.to_crs(target_crs)
                
    except Exception as e:
        print(f"Error loading evaluation files: {e}")
        return

    # 2. Load Ground Truth (References)
    ref_files = list((INPUTS_DIR / "vectors").glob("reference_*.geojson"))
    ref_gdfs = []
    print(f"Loading {len(ref_files)} reference maps...")
    for rf in ref_files:
        try:
            gdf = gpd.read_file(rf)
            if gdf.crs != target_crs: 
                if gdf.crs is None:
                    gdf.set_crs(target_crs, inplace=True)
                else:
                    gdf = gdf.to_crs(target_crs)
            
            # Label map name
            map_name = rf.stem.replace("reference_", "")
            gdf['Map'] = map_name 
            
            # Buffer References (The "Hit Zone")
            gdf['geometry'] = gdf.geometry.buffer(buffer_meters)
            
            ref_gdfs.append(gdf)
        except Exception as e:
            print(f"Skipping ref {rf}: {e}")

    if not ref_gdfs:
        print("No reference data found.")
        return

    gdf_ref_all = pd.concat(ref_gdfs, ignore_index=True)

    # 3. Filter Detections (Clean up)
    # Remove metadata features if present
    if 'label' in gdf_det.columns:
         gdf_det = gdf_det[gdf_det['label'] != 'processed_tile_bounds']
    
    # Infer map names
    gdf_det['Map'] = gdf_det['source_tile'].apply(get_map_name)

    # 4. Evaluation Logic
    all_fp = []
    all_fn = []
    
    # Analyze by Map to ensure we match Reference Scope
    # (Only look for errors on maps we actually processed)
    processed_maps = set([get_map_name(n) for n in gdf_bounds['tile_name'].unique()])
    
    tp_global = 0
    fn_global = 0
    fp_global = 0

    print(f"Evaluating on maps: {processed_maps}")

    for map_name in processed_maps:
        if map_name == "Unknown": continue
        
        # A. Define Search Area for this Map (Union of tile bounds)
        map_bounds = gdf_bounds[gdf_bounds['tile_name'].str.startswith(map_name)]
        if map_bounds.empty: continue
        
        searched_area = map_bounds.geometry.union_all()
        # Optional: slight edge exclusion? Let's keep strict for benchmark.
        
        # B. Filter References to Scope
        ref_on_map = gdf_ref_all[gdf_ref_all['Map'] == map_name]
        # Only check references that inside the tiles we processed
        if ref_on_map.empty:
            ref_in_scope = gpd.GeoDataFrame(columns=ref_on_map.columns, crs=target_crs)
        else:
            ref_in_scope = ref_on_map[ref_on_map.intersects(searched_area)].copy()

        # C. Filter Detections to Scope
        det_on_map = gdf_det[gdf_det['Map'] == map_name].copy()
        
        # D. Calculate Hits (TP)
        # Spatial Join: Detections intersecting Reference Hit Zones
        if det_on_map.empty and ref_in_scope.empty:
            continue
            
        if det_on_map.empty:
            # All Refs are FN
            fn_features = ref_in_scope.copy()
            fn_features['error_type'] = 'False Negative'
            all_fn.append(fn_features)
            fn_global += len(fn_features)
            continue

        if ref_in_scope.empty:
            # All Dets are FP
            fp_features = det_on_map.copy()
            fp_features['error_type'] = 'False Positive'
            all_fp.append(fp_features)
            fp_global += len(fp_features)
            continue

        # --- TP / FN / FP Logic ---
        
        # join_left: Det -> Ref (Find FPs)
        join_fp = gpd.sjoin(det_on_map, ref_in_scope, how='left', predicate='intersects')
        
        # FPs: Detections that hit NO reference
        fp_indices = join_fp[join_fp.index_right.isna()].index
        fp_features = det_on_map.loc[fp_indices].copy()
        fp_features['error_type'] = 'False Positive'
        all_fp.append(fp_features)
        fp_count = len(fp_features)
        
        # join_right: Ref -> Det (Find FNs)
        join_fn = gpd.sjoin(ref_in_scope, det_on_map, how='left', predicate='intersects')
        
        # FNs: References that were hit by NO detection
        fn_indices = join_fn[join_fn.index_right.isna()].index
        fn_features = ref_in_scope.loc[fn_indices].copy()
        fn_features['error_type'] = 'False Negative'
        all_fn.append(fn_features)
        fn_count = len(fn_features)
        
        # TPs: References that WERE hit (Count unique references found)
        # (Recall-oriented TP)
        tp_indices = join_fn[join_fn.index_right.notnull()].index.unique()
        tp_count = len(tp_indices)
        
        # Aggregation
        fp_global += fp_count
        fn_global += fn_count
        tp_global += tp_count
        
        print(f"[{map_name}] TP: {tp_count}, FP: {fp_count}, FN: {fn_count}")

    # 5. Global Metrics
    precision = tp_global / (tp_global + fp_global) if (tp_global + fp_global) > 0 else 0
    recall = tp_global / (tp_global + fn_global) if (tp_global + fn_global) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\n=== BENCHMARK RESULTS ===")
    print(f"True Positives:  {tp_global}")
    print(f"False Positives: {fp_global}")
    print(f"False Negatives: {fn_global}")
    print(f"-------------------------")
    print(f"Precision:       {precision:.4f}")
    print(f"Recall:          {recall:.4f}")
    print(f"F1 Score:        {f1:.4f}")
    print(f"=========================")
    
    # 6. Save Error Maps
    fp_path = Path(output_prefix + "_fp.geojson")
    fn_path = Path(output_prefix + "_fn.geojson")
    
    if all_fp:
        gdf_fp = pd.concat(all_fp, ignore_index=True)
        gdf_fp.to_file(fp_path, driver="GeoJSON")
        print(f"Saved False Positives to {fp_path}")
    else:
        # Save empty
        if not all_fp: gpd.GeoDataFrame(columns=['geometry'], crs=target_crs).to_file(fp_path, driver="GeoJSON")

    if all_fn:
        gdf_fn = pd.concat(all_fn, ignore_index=True)
        gdf_fn.to_file(fn_path, driver="GeoJSON")
        print(f"Saved False Negatives to {fn_path}")
    else:
        if not all_fn: gpd.GeoDataFrame(columns=['geometry'], crs=target_crs).to_file(fn_path, driver="GeoJSON")

    # 7. Save Metrics
    metrics_file = Path(output_prefix + "_metrics.json")
    metrics_data = {
        "tp": int(tp_global),
        "fp": int(fp_global),
        "fn": int(fn_global),
        "precision": precision,
        "recall": recall,
        "f1": f1
    }
    with open(metrics_file, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    print(f"Saved Metrics to {metrics_file}")

    # 8. Advanced Metrics (Added Dec 18)
    try:
        from scripts import lib_advanced_metrics
        adv_metrics_file = Path(output_prefix + "_advanced_metrics.json")
        lib_advanced_metrics.generate_report(detection_file, bounds_file, output_path=adv_metrics_file)
    except Exception as e:
        print(f"Warning: Failed to generate advanced metrics: {e}")


def run_benchmark(model_override=None, config_path=None):
    # 1. Config
    if not config_path:
        config_path = "prompts/versions/v3.1_baseline.json"
        
    manifest_path = INPUTS_DIR / "target_tiles_manifest.json"
    
    if not manifest_path.exists():
        print(f"Error: Manifest not found at {manifest_path}")
        return

    print(f"Starting Benchmark using Manifest: {manifest_path}")
    print(f"Config: {config_path}")
    if model_override:
        print(f"Model Override: {model_override}")
    
    # Load config to get version for naming
    try:
        with open(config_path, 'r') as f:
            cfg_data = json.load(f)
            version_tag = cfg_data.get("version", "vX")
    except Exception as e:
        print(f"Error reading config for version tag: {e}")
        return

    # 2. Run Detection (with Bounds Export)
    # Output name derived from version: benchmark_{version}.geojson
    output_name = f"benchmark_{version_tag}.geojson"
    
    # Note: detect_mounds_versioned returns None, but we know the paths
    detect_mounds_versioned(
        config_path, 
        manifest_path=manifest_path, 
        output_name=output_name,
        export_bounds=True, # Crucial forFN calculation
        model_override=model_override
    )
    
    # 3. Paths for Evaluation
    results_dir = RESULTS_DIR / version_tag # Batch script creates subdir based on config name
    detection_file = results_dir / output_name
    bounds_file = results_dir / (Path(output_name).stem + "_bounds.geojson")
    
    # Generate bounds if missing
    if not bounds_file.exists():
        generate_bounds(manifest_path, bounds_file)

    if not detection_file.exists():
        print("Error: Detection file creation failed. Aborting evaluation.")
        return
        
    # 4. Run Evaluation
    output_prefix = str(results_dir / f"benchmark_{version_tag}")
    evaluate_performance(detection_file, bounds_file, output_prefix)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=False, help="Path to JSON prompt config")
    parser.add_argument("--model", required=False, help="Override model name (e.g. gemini-1.5-flash)")
    args = parser.parse_args()
    
    run_benchmark(model_override=args.model, config_path=args.config)
