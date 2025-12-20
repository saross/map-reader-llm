
import sys
import os
import argparse
import json
import geopandas as gpd
from pathlib import Path
import pandas as pd
import numpy as np

# Setup Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

try:
    from scripts.lib_advanced_metrics import calculate_f1_internal, load_data
except ImportError:
    print("Error importing scripts.lib_advanced_metrics.")
    sys.exit(1)

def analyze_consensus(pred_path, bounds_path, template_path, iterations=5):
    print(f"Analyzing Consensus: {pred_path}")
    
    # 1. Load Ground Truth
    try:
        _, gdf_bounds, gdf_ref = load_data(template_path, bounds_path)
    except Exception as e:
        print(f"Error loading ground truth: {e}")
        return

    # 2. Load Consensus Predictions
    try:
        gdf_pred = gpd.read_file(pred_path)
        # Ensure CRS
        if not gdf_pred.empty:
            gdf_pred.set_crs("EPSG:32635", allow_override=True, inplace=True)
            if gdf_pred.crs != gdf_ref.crs: gdf_pred = gdf_pred.to_crs(gdf_ref.crs)
    except Exception as e:
        print(f"Error loading predictions: {e}")
        return
        
    print(f"Total Union Candidates: {len(gdf_pred)}")
    
    # 3. Simulate Vote Thresholds (2D Grid)
    # Proposer Threshold (1-5) x Verifier Threshold (1-5)
    
    print(f"\n{'Prop Votes':<10} | {'Verif Votes':<10} | {'Recall':<10} | {'Precision':<10} | {'F1 Score':<10} | {'Count':<10}")
    print("-" * 80)
    
    best_overall = {"f1": 0, "desc": ""}
    
    for p_thresh in range(1, 6):
        # Filter Proposer Consensus first
        # Note: 'proposer_votes' is in properties
        subset_p = gdf_pred[gdf_pred['proposer_votes'] >= p_thresh].copy()
        
        if subset_p.empty: continue
            
        for v_thresh in range(1, iterations + 1):
            # Filter Verifier Consensus
            subset_pv = subset_p[subset_p['verifier_votes'] >= v_thresh].copy()
            count = len(subset_pv)
            
            label = f"P>={p_thresh} V>={v_thresh}"
            
            p, r, f1 = 0.0, 0.0, 0.0
            if count > 0:
                p, r, f1 = calculate_f1_internal(subset_pv, gdf_ref, gdf_bounds)
            
            if f1 > best_overall["f1"]:
                best_overall = {"f1": f1, "desc": label, "p_thresh": p_thresh, "v_thresh": v_thresh, "metrics": (p,r,f1)}
                
            # Print compelling rows (F1 > 0.7 or specific interest)
            if f1 > 0.7:
                best_mark = "🏆" if f1 == best_overall["f1"] else ""
                print(f"{p_thresh:<10} | {v_thresh:<10} | {r:.4f}     | {p:.4f}     | {f1:.4f} {best_mark}   | {count}")

    print("-" * 80)
    print("Optimization Result:")
    print(f"Global Best: {best_overall['desc']} -> F1 {best_overall['f1']:.4f}")
    if best_overall['f1'] > 0:
        p, r, f1 = best_overall['metrics']
        print(f"Precision: {p:.4f}")
        print(f"Recall:    {r:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred", required=True)
    parser.add_argument("--bounds", required=True)
    parser.add_argument("--template", required=True)
    parser.add_argument("--iterations", type=int, default=5)
    args = parser.parse_args()
    
    analyze_consensus(args.pred, args.bounds, args.template, args.iterations)
