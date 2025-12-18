
import geopandas as gpd
import pandas as pd
import numpy as np
import json
from pathlib import Path
from shapely.geometry import box
import sys

# Constants for project structure
INPUTS_DIR = Path("inputs")

def load_data(detection_file, bounds_file, inputs_dir=INPUTS_DIR):
    try:
        gdf_det = gpd.read_file(detection_file)
        gdf_bounds = gpd.read_file(bounds_file)
        
        # Load references
        ref_files = list((inputs_dir / "vectors").glob("reference_*.geojson"))
        ref_gdfs = []
        for rf in ref_files:
            gdf = gpd.read_file(rf)
            gdf['Map'] = rf.stem.replace("reference_", "")
            ref_gdfs.append(gdf)
        
        if not ref_gdfs:
            print("Warning: No reference vectors found.")
            return None, None, None

        gdf_ref = pd.concat(ref_gdfs, ignore_index=True)
        
        # CRS Standardization
        target_crs = "EPSG:32635"
        if gdf_det.crs != target_crs: 
            if gdf_det.crs is None: gdf_det.set_crs(target_crs, inplace=True)
            else: gdf_det = gdf_det.to_crs(target_crs)
            
        if gdf_bounds.crs != target_crs: 
            if gdf_bounds.crs is None: gdf_bounds.set_crs(target_crs, inplace=True)
            else: gdf_bounds = gdf_bounds.to_crs(target_crs)

        if gdf_ref.crs != target_crs: 
            if gdf_ref.crs is None: gdf_ref.set_crs(target_crs, inplace=True)
            else: gdf_ref = gdf_ref.to_crs(target_crs)
        
        return gdf_det, gdf_bounds, gdf_ref
    except Exception as e:
        print(f"Error loading metrics data: {e}")
        return None, None, None

def get_map_name(tile_name):
    matches = ["K-35-062-2_Rakovski", "K-35-052-4_32635", "K-35-053-3_Elenovo", "K-35-078-1_Lesovo"]
    for m in matches:
        if tile_name.startswith(m): return m
    return "Unknown"

def normalize_ref_class(symbol):
    s = "{0}".format(symbol).lower() # Handle None/NaN safety
    if "bench mark" in s: return "benchmark_mound"
    if "triangulation" in s: return "triangulation_mound"
    if "burial mound" in s or "kurgan" in s: return "burial_mound"
    if "settlement" in s: return "settlement_mound"
    return "unknown"

def calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds, buffer_meters=20):
    """
    Internal helper to calc global F1 for a given set of dataframes.
    Assumes geodataframes are already filtered/prepared if needed.
    """
    tp = 0
    fp = 0
    fn = 0
    
    # 1. Scope
    processed_maps = set([get_map_name(n) for n in gdf_bounds['tile_name'].unique()])
    
    for map_name in processed_maps:
        if map_name == "Unknown": continue
        
        map_bounds = gdf_bounds[gdf_bounds['tile_name'].str.startswith(map_name)]
        search_area = map_bounds.geometry.union_all()
        
        ref_scope = gdf_ref[gdf_ref['Map'] == map_name]
        if not ref_scope.empty:
            ref_scope = ref_scope[ref_scope.intersects(search_area)].copy()
        
        det_scope = gdf_det[gdf_det['source_tile'].str.startswith(map_name)]
        
        # Buffer Refs
        ref_buffered = ref_scope.copy()
        ref_buffered['geometry'] = ref_buffered.geometry.buffer(buffer_meters)
        
        if det_scope.empty and ref_buffered.empty: continue
        
        if det_scope.empty:
            fn += len(ref_buffered)
        elif ref_buffered.empty:
            fp += len(det_scope)
        else:
             join_tp = gpd.sjoin(ref_buffered, det_scope, how='inner', predicate='intersects')
             tp += len(join_tp.index.unique())
             fn += len(ref_buffered) - len(join_tp.index.unique())
             
             join_fp = gpd.sjoin(det_scope, ref_buffered, how='left', predicate='intersects')
             fp += len(join_fp[join_fp.index_right.isna()])

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return precision, recall, f1

def bootstrap_ci(gdf_det, gdf_ref, gdf_bounds, n_iterations=1000):
    tiles = gdf_bounds['tile_name'].unique()
    n_tiles = len(tiles)
    if n_tiles == 0: return {}
    
    f1_scores = []
    
    for i in range(n_iterations):
        sample_tiles = np.random.choice(tiles, n_tiles, replace=True)
        
        sample_dets = []
        sample_bounds = []
        
        for t in sample_tiles:
            d = gdf_det[gdf_det['source_tile'] == t].copy()
            sample_dets.append(d)
            b = gdf_bounds[gdf_bounds['tile_name'] == t].copy()
            sample_bounds.append(b)
            
        if not sample_dets:
            f1_scores.append(0)
            continue
            
        gdf_sample_det = pd.concat(sample_dets, ignore_index=True)
        gdf_sample_bounds = pd.concat(sample_bounds, ignore_index=True)
        
        try:
             _, _, f1 = calculate_f1_internal(gdf_sample_det, gdf_ref, gdf_sample_bounds)
             f1_scores.append(f1)
        except:
             f1_scores.append(0)
             
    lower = float(np.percentile(f1_scores, 2.5))
    upper = float(np.percentile(f1_scores, 97.5))
    mean = float(np.mean(f1_scores))
    
    return {
        "mean": mean,
        "ci_lower": lower,
        "ci_upper": upper,
        "n_iterations": n_iterations
    }

def spatial_tolerance_curve(gdf_det, gdf_ref, gdf_bounds, buffers=[10, 20, 30, 50]):
    results = []
    for b in buffers:
        p, r, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds, buffer_meters=b)
        results.append({
            "buffer": b,
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f1, 4)
        })
    return results

def calculate_per_class_f1(gdf_det, gdf_ref, gdf_bounds, buffer_meters=20):
    gdf_ref['normalized_class'] = gdf_ref['Symbol'].apply(normalize_ref_class)
    classes = ["burial_mound", "benchmark_mound", "triangulation_mound"]
    
    results = []
    for cls in classes:
        det_cls = gdf_det[gdf_det['subtype'] == cls].copy()
        ref_cls = gdf_ref[gdf_ref['normalized_class'] == cls].copy()
        
        p, r, f1 = calculate_f1_internal(det_cls, ref_cls, gdf_bounds, buffer_meters)
        results.append({
            "class": cls,
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f1, 4)
        })
    return results

def error_taxonomy(gdf_det, gdf_ref, gdf_bounds):
    taxonomy = {"false_positives": {}, "false_negatives": {}}
    
    gdf_ref_buf = gdf_ref.copy()
    gdf_ref_buf['geometry'] = gdf_ref_buf.geometry.buffer(20)
    
    # FPs
    join_fp = gpd.sjoin(gdf_det, gdf_ref_buf, how='left', predicate='intersects')
    fps = join_fp[join_fp.index_right.isna()]
    if not fps.empty:
        taxonomy["false_positives"] = fps['subtype'].value_counts().to_dict()
    
    # FNs
    processed_geometry = gdf_bounds.geometry.union_all()
    refs_in_scope = gdf_ref_buf[gdf_ref_buf.intersects(processed_geometry)].copy()
    
    join_fn = gpd.sjoin(refs_in_scope, gdf_det, how='left', predicate='intersects')
    fns = join_fn[join_fn.index_right.isna()].copy()
    if not fns.empty:
        fns['normalized_class'] = fns['Symbol'].apply(normalize_ref_class)
        taxonomy["false_negatives"] = fns['normalized_class'].value_counts().to_dict()
        
    return taxonomy

def generate_report(detection_path, bounds_path, output_path=None, bootstrap_iterations=1000):
    print("Generating Advanced Metrics Report...")
    gdf_det, gdf_bounds, gdf_ref = load_data(detection_path, bounds_path)
    
    if gdf_det is None: return {}
    
    report = {}
    
    # 1. Bootstrap
    report["bootstrap_ci"] = bootstrap_ci(gdf_det, gdf_ref, gdf_bounds, n_iterations=bootstrap_iterations)
    
    # 2. Spatial
    report["spatial_tolerance"] = spatial_tolerance_curve(gdf_det, gdf_ref, gdf_bounds)
    
    # 3. Per Class
    report["per_class_performance"] = calculate_per_class_f1(gdf_det, gdf_ref, gdf_bounds)
    
    # 4. Taxonomy
    report["error_taxonomy"] = error_taxonomy(gdf_det, gdf_ref, gdf_bounds)
    
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Advanced metrics saved to {output_path}")
        
    return report
