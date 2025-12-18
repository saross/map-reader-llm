
import geopandas as gpd
import pandas as pd
import numpy as np
import json
import argparse
from pathlib import Path
from shapely.geometry import box
import sys


# Hardcoded inputs for this specific ad-hoc request
RESULTS_DIR = Path("outputs/results/v3.2_experimental")
DETECTION_FILE = RESULTS_DIR / "benchmark_v3.2_experimental.geojson"
BOUNDS_FILE = RESULTS_DIR / "benchmark_v3.2_experimental_bounds.geojson"
MANIFEST_FILE = Path("inputs/target_tiles_manifest.json")
INPUTS_DIR = Path("inputs")

def load_data():
    print("Loading data...")
    try:
        gdf_det = gpd.read_file(DETECTION_FILE)
        gdf_bounds = gpd.read_file(BOUNDS_FILE)
        
        # Load references
        ref_files = list((INPUTS_DIR / "vectors").glob("reference_*.geojson"))
        ref_gdfs = []
        for rf in ref_files:
            gdf = gpd.read_file(rf)
            gdf['Map'] = rf.stem.replace("reference_", "")
            ref_gdfs.append(gdf)
        gdf_ref = pd.concat(ref_gdfs, ignore_index=True)
        
        # CRS Standardization
        target_crs = "EPSG:32635"
        if gdf_det.crs != target_crs: gdf_det = gdf_det.to_crs(target_crs)
        if gdf_bounds.crs != target_crs: gdf_bounds = gdf_bounds.to_crs(target_crs)
        if gdf_ref.crs != target_crs: gdf_ref = gdf_ref.to_crs(target_crs)
        
        return gdf_det, gdf_bounds, gdf_ref
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

def get_map_name(tile_name):
    matches = ["K-35-062-2_Rakovski", "K-35-052-4_32635", "K-35-053-3_Elenovo", "K-35-078-1_Lesovo"]
    for m in matches:
        if tile_name.startswith(m): return m
    return "Unknown"

def calculate_f1(gdf_det, gdf_ref, gdf_bounds, buffer_meters=20):
    # This is a simplified in-memory calculation for bootstrapping
    # 1. Scope
    processed_maps = set([get_map_name(n) for n in gdf_bounds['tile_name'].unique()])
    
    tp = 0
    fp = 0
    fn = 0
    
    for map_name in processed_maps:
        if map_name == "Unknown": continue
        
        # Filter to Map
        map_bounds = gdf_bounds[gdf_bounds['tile_name'].str.startswith(map_name)]
        search_area = map_bounds.geometry.union_all()
        
        ref_scope = gdf_ref[gdf_ref['Map'] == map_name]
        if not ref_scope.empty:
            ref_scope = ref_scope[ref_scope.intersects(search_area)].copy()
        
        det_scope = gdf_det[gdf_det['source_tile'].str.startswith(map_name)]
        if not det_scope.empty:
            # Important: Bootstrap resamples TILES, so we need to filter detections to ONLY the current sample's tiles?
            # Actually, standard bootstrap resamples the *units of analysis*.
            # If we resample tiles, we need to rebuild the detection set for that sample.
            pass 
        
        # Hit Logic
        ref_buffered = ref_scope.copy()
        ref_buffered['geometry'] = ref_buffered.geometry.buffer(buffer_meters)
        
        # Spatial Join
        if not det_scope.empty and not ref_buffered.empty:
            # TP = Refs hit by Dets
            join_tp = gpd.sjoin(ref_buffered, det_scope, how='inner', predicate='intersects')
            tp += len(join_tp.index.unique())
            
            # FN = Refs NOT hit
            fn += len(ref_buffered) - len(join_tp.index.unique())
            
            # FP = Dets NOT hitting Refs
            # Reverse join
            join_fp = gpd.sjoin(det_scope, ref_buffered, how='left', predicate='intersects')
            fp += len(join_fp[join_fp.index_right.isna()])
            
        elif det_scope.empty:
            fn += len(ref_buffered)
        elif ref_buffered.empty:
            fp += len(det_scope)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return precision, recall, f1

def bootstrap_ci(gdf_det, gdf_ref, gdf_bounds, n_iterations=1000):
    print(f"\nRunning Bootstrap CI ({n_iterations} iterations)...")
    
    # 1. Identify Sampling Units (Tiles)
    tiles = gdf_bounds['tile_name'].unique()
    n_tiles = len(tiles)
    
    f1_scores = []
    
    for i in range(n_iterations):
        if i % 100 == 0: print(f"Iteration {i}...")
        
        # Resample tiles with replacement
        sample_tiles = np.random.choice(tiles, n_tiles, replace=True)
        
        # Reconstruct "Sampled Run"
        # We need to create a "Sampled Detections" DF that mimics this run
        # If Tile A is sampled 2x, its detections appear 2x? Yes.
        
        sample_dets = []
        sample_bounds = []
        
        for t in sample_tiles:
            # Get dets for this tile
            d = gdf_det[gdf_det['source_tile'] == t].copy()
            sample_dets.append(d)
            
            # Get bounds for this tile
            b = gdf_bounds[gdf_bounds['tile_name'] == t].copy()
            sample_bounds.append(b)
            
        if not sample_dets:
            # Bad luck sample (all empty tiles), skip or count as 0?
            # If truly all empty, F1 is undefined (0/0) or 0.
            f1_scores.append(0) 
            continue
            
        gdf_sample_det = pd.concat(sample_dets, ignore_index=True)
        gdf_sample_bounds = pd.concat(sample_bounds, ignore_index=True)
        
        # Calculate F1 for this sample
        try:
             _, _, f1 = calculate_f1(gdf_sample_det, gdf_ref, gdf_sample_bounds)
             f1_scores.append(f1)
        except:
             f1_scores.append(0)
             
    # Calculate Percentiles
    lower = np.percentile(f1_scores, 2.5)
    upper = np.percentile(f1_scores, 97.5)
    mean = np.mean(f1_scores)
    
    print(f"Bootstrap F1 Mean: {mean:.4f}")
    print(f"95% CI: [{lower:.4f}, {upper:.4f}]")
    return mean, lower, upper

def spatial_tolerance_curve(gdf_det, gdf_ref, gdf_bounds):
    print("\nGenerating Spatial Tolerance Curve...")
    buffers = [10, 20, 30, 40, 50]
    results = []
    
    for b in buffers:
        p, r, f1 = calculate_f1(gdf_det, gdf_ref, gdf_bounds, buffer_meters=b)
        print(f"Buffer {b}m: P={p:.3f}, R={r:.3f}, F1={f1:.3f}")
        results.append({"buffer": b, "precision": p, "recall": r, "f1": f1})
        
    return results


def normalize_ref_class(symbol):
    s = symbol.lower()
    if "bench mark" in s: return "benchmark_mound"
    if "triangulation" in s: return "triangulation_mound"
    if "burial mound" in s or "kurgan" in s: return "burial_mound"
    if "settlement" in s: return "settlement_mound"
    return "unknown"

def calculate_per_class_f1(gdf_det, gdf_ref, gdf_bounds, buffer_meters=20):
    print("\nCalculated Per-Class F1 (One-vs-All)...")
    
    # Pre-process Ref Classes
    gdf_ref['normalized_class'] = gdf_ref['Symbol'].apply(normalize_ref_class)
    classes = ["burial_mound", "benchmark_mound", "triangulation_mound"]
    
    results = []
    
    for cls in classes:
        # Filter Dets and Refs to JUST this class
        # Note: This is "Strict" matching. 
        # If model predicts "burial_mound" for a "benchmark_mound", it is a FP for burial and FN for benchmark.
        
        det_cls = gdf_det[gdf_det['subtype'] == cls].copy()
        ref_cls = gdf_ref[gdf_ref['normalized_class'] == cls].copy()
        
        # We need to run the spatial join logic just for this subset
        # Reuse simple logic from global calc but filtered
        
        tp = 0
        fp = 0
        fn = 0
        
        ref_buffered = ref_cls.copy()
        ref_buffered['geometry'] = ref_buffered.geometry.buffer(buffer_meters)
        
        # We must limit scope to the processed tiles
        processed_maps = set([get_map_name(n) for n in gdf_bounds['tile_name'].unique()])
        
        for map_name in processed_maps:
             if map_name == "Unknown": continue
             
             # Bounds of processed area
             map_bounds = gdf_bounds[gdf_bounds['tile_name'].str.startswith(map_name)]
             search_area = map_bounds.geometry.union_all()
             
             # Filter Ref to Map & Bounds
             r = ref_buffered[ref_buffered['Map'] == map_name]
             if not r.empty: r = r[r.intersects(search_area)]
             
             # Filter Det to Map
             d = det_cls[det_cls['source_tile'].str.startswith(map_name)]
             
             if d.empty and r.empty: continue
             
             if d.empty:
                 fn += len(r)
                 continue
             if r.empty:
                 fp += len(d)
                 continue
                 
             # Join
             join_tp = gpd.sjoin(r, d, how='inner', predicate='intersects')
             current_tp = len(join_tp.index.unique())
             tp += current_tp
             fn += len(r) - current_tp
             
             join_fp = gpd.sjoin(d, r, how='left', predicate='intersects')
             fp += len(join_fp[join_fp.index_right.isna()])
        
        p = tp / (tp + fp) if (tp + fp) > 0 else 0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (p * r) / (p + r) if (p + r) > 0 else 0
        
        print(f"Class '{cls}': P={p:.2f}, R={r:.2f}, F1={f1:.2f} (TP={tp}, FP={fp}, FN={fn})")
        results.append({"class": cls, "precision": p, "recall": r, "f1": f1})

def error_taxonomy(gdf_det, gdf_ref, gdf_bounds):
    print("\nGenerating Error Taxonomy...")
    
    # Buffer refs
    gdf_ref_buf = gdf_ref.copy()
    gdf_ref_buf['geometry'] = gdf_ref_buf.geometry.buffer(20)
    
    # 1. False Positives
    # Filter to bounds
    # (Simplified: assuming all Dets are within bounds by definition of the run)
    join_fp = gpd.sjoin(gdf_det, gdf_ref_buf, how='left', predicate='intersects')
    fps = join_fp[join_fp.index_right.isna()].copy()
    
    print(f"\nTotal False Positives: {len(fps)}")
    if not fps.empty:
        print(fps['subtype'].value_counts())

    # 2. False Negatives
    # We need to filter Refs to strictly those inside the Bounds
    processed_geometry = gdf_bounds.geometry.union_all()
    refs_in_scope = gdf_ref_buf[gdf_ref_buf.intersects(processed_geometry)].copy()
    
    join_fn = gpd.sjoin(refs_in_scope, gdf_det, how='left', predicate='intersects')
    fns = join_fn[join_fn.index_right.isna()].copy()
    
    print(f"\nTotal False Negatives: {len(fns)}")
    if not fns.empty:
        # Use Normalized Class for taxonomy
        fns['normalized_class'] = fns['Symbol'].apply(normalize_ref_class)
        print(fns['normalized_class'].value_counts())

def main():
    gdf_det, gdf_bounds, gdf_ref = load_data()
    
    # 1. CI
    bootstrap_ci(gdf_det, gdf_ref, gdf_bounds, n_iterations=1000)
    
    # 2. Per-Class F1
    calculate_per_class_f1(gdf_det, gdf_ref, gdf_bounds)
    
    # 3. Spatial Curve
    spatial_tolerance_curve(gdf_det, gdf_ref, gdf_bounds)
    
    # 4. Taxonomy
    error_taxonomy(gdf_det, gdf_ref, gdf_bounds)


if __name__ == "__main__":
    main()
