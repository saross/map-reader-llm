
"""
Advanced metrics library for mound detection evaluation.

Provides F1, precision, recall calculations with one-to-one matching
using the Hungarian algorithm for optimal detection-to-reference assignment.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import json
from pathlib import Path
from shapely.geometry import box
from scipy.optimize import linear_sum_assignment
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
    """Normalise reference symbol class names to standard categories."""
    s = "{0}".format(symbol).lower()  # Handle None/NaN safety
    if "bench mark" in s:
        return "benchmark_mound"
    if "triangulation" in s:
        return "triangulation_mound"
    if "burial mound" in s or "kurgan" in s:
        return "burial_mound"
    if "settlement" in s:
        return "settlement_mound"
    return "unknown"


def match_detections_to_references(det_geoms, ref_geoms, max_distance):
    """
    Perform one-to-one matching between detections and references using
    the Hungarian algorithm.

    Each detection can match at most one reference, and vice versa.
    Matches are only valid if within max_distance metres.

    Args:
        det_geoms: List/array of detection geometries (points or centroids)
        ref_geoms: List/array of reference geometries (points or centroids)
        max_distance: Maximum distance in metres for a valid match

    Returns:
        tuple: (matched_det_indices, matched_ref_indices, unmatched_det_indices,
                unmatched_ref_indices)
    """
    n_det = len(det_geoms)
    n_ref = len(ref_geoms)

    if n_det == 0 or n_ref == 0:
        return ([], [], list(range(n_det)), list(range(n_ref)))

    # Build distance matrix
    # Use a large value for "no match possible" to ensure Hungarian algorithm
    # doesn't assign pairs beyond max_distance
    inf_cost = max_distance * 1000  # Effectively infinite

    cost_matrix = np.full((n_det, n_ref), inf_cost)

    for i, det_geom in enumerate(det_geoms):
        det_point = det_geom.centroid if det_geom.geom_type != 'Point' else det_geom
        for j, ref_geom in enumerate(ref_geoms):
            ref_point = ref_geom.centroid if ref_geom.geom_type != 'Point' else ref_geom
            dist = det_point.distance(ref_point)
            if dist <= max_distance:
                cost_matrix[i, j] = dist

    # Hungarian algorithm finds optimal assignment minimising total cost
    det_indices, ref_indices = linear_sum_assignment(cost_matrix)

    # Filter out assignments that exceed max_distance
    matched_det = []
    matched_ref = []
    for d_idx, r_idx in zip(det_indices, ref_indices):
        if cost_matrix[d_idx, r_idx] <= max_distance:
            matched_det.append(d_idx)
            matched_ref.append(r_idx)

    unmatched_det = [i for i in range(n_det) if i not in matched_det]
    unmatched_ref = [i for i in range(n_ref) if i not in matched_ref]

    return (matched_det, matched_ref, unmatched_det, unmatched_ref)

def calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds, buffer_meters=20):
    """
    Calculate global F1 using one-to-one matching via Hungarian algorithm.

    Each detection can match at most one reference, and vice versa.
    This ensures accurate mound counts: if one detection covers two mounds,
    it counts as 1 TP + 1 FN.

    Args:
        gdf_det: GeoDataFrame of detections
        gdf_ref: GeoDataFrame of ground truth references
        gdf_bounds: GeoDataFrame of tile boundaries (defines evaluation scope)
        buffer_meters: Maximum distance for a valid match (default 20m)

    Returns:
        tuple: (precision, recall, f1)
    """
    tp = 0
    fp = 0
    fn = 0

    # Scope by processed maps
    processed_maps = set([get_map_name(n) for n in gdf_bounds['tile_name'].unique()])

    for map_name in processed_maps:
        if map_name == "Unknown":
            continue

        map_bounds = gdf_bounds[gdf_bounds['tile_name'].str.startswith(map_name)]
        search_area = map_bounds.geometry.union_all()

        ref_scope = gdf_ref[gdf_ref['Map'] == map_name]
        if not ref_scope.empty:
            ref_scope = ref_scope[ref_scope.intersects(search_area)].copy()

        det_scope = gdf_det[gdf_det['source_tile'].str.startswith(map_name)]

        if det_scope.empty and ref_scope.empty:
            continue

        if det_scope.empty:
            fn += len(ref_scope)
        elif ref_scope.empty:
            fp += len(det_scope)
        else:
            # One-to-one matching using Hungarian algorithm
            det_geoms = list(det_scope.geometry)
            ref_geoms = list(ref_scope.geometry)

            matched_det, matched_ref, unmatched_det, unmatched_ref = \
                match_detections_to_references(det_geoms, ref_geoms, buffer_meters)

            tp += len(matched_det)
            fp += len(unmatched_det)
            fn += len(unmatched_ref)

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

def error_taxonomy(gdf_det, gdf_ref, gdf_bounds, buffer_meters=20):
    """
    Categorise false positives and false negatives by symbol type.

    Uses one-to-one matching to ensure consistent error attribution.

    Args:
        gdf_det: GeoDataFrame of detections
        gdf_ref: GeoDataFrame of ground truth references
        gdf_bounds: GeoDataFrame of tile boundaries
        buffer_meters: Maximum distance for a valid match (default 20m)

    Returns:
        dict: {'false_positives': {subtype: count}, 'false_negatives': {class: count}}
    """
    taxonomy = {"false_positives": {}, "false_negatives": {}}

    # Scope references to processed area
    processed_geometry = gdf_bounds.geometry.union_all()
    refs_in_scope = gdf_ref[gdf_ref.intersects(processed_geometry)].copy()

    if gdf_det.empty and refs_in_scope.empty:
        return taxonomy

    # Perform one-to-one matching
    det_geoms = list(gdf_det.geometry) if not gdf_det.empty else []
    ref_geoms = list(refs_in_scope.geometry) if not refs_in_scope.empty else []

    matched_det, matched_ref, unmatched_det, unmatched_ref = \
        match_detections_to_references(det_geoms, ref_geoms, buffer_meters)

    # Categorise false positives by detection subtype
    if unmatched_det and not gdf_det.empty:
        fp_detections = gdf_det.iloc[unmatched_det]
        if 'subtype' in fp_detections.columns:
            taxonomy["false_positives"] = fp_detections['subtype'].value_counts().to_dict()

    # Categorise false negatives by reference class
    if unmatched_ref and not refs_in_scope.empty:
        fn_refs = refs_in_scope.iloc[unmatched_ref].copy()
        fn_refs['normalized_class'] = fn_refs['Symbol'].apply(normalize_ref_class)
        taxonomy["false_negatives"] = fn_refs['normalized_class'].value_counts().to_dict()

    return taxonomy

def generate_report(detection_path, bounds_path, output_path=None, bootstrap_iterations=1000):
    print("Generating Advanced Metrics Report...")
    gdf_det, gdf_bounds, gdf_ref = load_data(detection_path, bounds_path)

    if gdf_det is None: return {}

    report = {}

    # 1. Global metrics (at standard 20m buffer)
    p, r, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds, buffer_meters=20)
    report["global_metrics"] = {
        "precision": round(p, 4),
        "recall": round(r, 4),
        "f1": round(f1, 4)
    }

    # 2. Bootstrap
    report["bootstrap_ci"] = bootstrap_ci(gdf_det, gdf_ref, gdf_bounds, n_iterations=bootstrap_iterations)

    # 3. Spatial
    report["spatial_tolerance"] = spatial_tolerance_curve(gdf_det, gdf_ref, gdf_bounds)

    # 4. Per Class
    report["per_class_performance"] = calculate_per_class_f1(gdf_det, gdf_ref, gdf_bounds)

    # 5. Taxonomy
    report["error_taxonomy"] = error_taxonomy(gdf_det, gdf_ref, gdf_bounds)

    if output_path:
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Advanced metrics saved to {output_path}")

    return report


def print_report_summary(report, title="Metrics Summary"):
    """
    Prints a formatted summary of the metrics report to console.

    Args:
        report (dict): The report dictionary from generate_report().
        title (str): Header title for the summary.
    """
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

    # Global metrics
    gm = report.get("global_metrics", {})
    print(f"\n[Global Performance @ 20m buffer]")
    print(f"  F1:        {gm.get('f1', 0):.4f}")
    print(f"  Precision: {gm.get('precision', 0):.4f}")
    print(f"  Recall:    {gm.get('recall', 0):.4f}")

    # Bootstrap CI
    ci = report.get("bootstrap_ci", {})
    if ci:
        print(f"\n[Bootstrap Confidence Interval (N={ci.get('n_iterations', 0)})]")
        print(f"  Mean F1:   {ci.get('mean', 0):.4f}")
        print(f"  95% CI:    [{ci.get('ci_lower', 0):.4f}, {ci.get('ci_upper', 0):.4f}]")

    # Per-class performance
    pcp = report.get("per_class_performance", [])
    if pcp:
        print(f"\n[Per-Class Performance]")
        print(f"  {'Class':<22} {'F1':>8} {'Prec':>8} {'Rec':>8}")
        print(f"  {'-'*22} {'-'*8} {'-'*8} {'-'*8}")
        for cls in pcp:
            print(f"  {cls['class']:<22} {cls['f1']:>8.4f} {cls['precision']:>8.4f} {cls['recall']:>8.4f}")

    # Spatial tolerance
    st = report.get("spatial_tolerance", [])
    if st:
        print(f"\n[Spatial Tolerance Curve]")
        print(f"  {'Buffer (m)':<12} {'F1':>8} {'Prec':>8} {'Rec':>8}")
        print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8}")
        for row in st:
            print(f"  {row['buffer']:<12} {row['f1']:>8.4f} {row['precision']:>8.4f} {row['recall']:>8.4f}")

    # Error taxonomy
    et = report.get("error_taxonomy", {})
    fps = et.get("false_positives", {})
    fns = et.get("false_negatives", {})
    if fps or fns:
        print(f"\n[Error Taxonomy]")
        if fps:
            print(f"  False Positives: {dict(fps)}")
        if fns:
            print(f"  False Negatives: {dict(fns)}")

    print(f"\n{'='*60}\n")
