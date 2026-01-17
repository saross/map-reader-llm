
import sys
import argparse
import geopandas as gpd
from pathlib import Path

# Setup Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

try:
    from scripts.lib_advanced_metrics import calculate_f1_internal, load_data
except ImportError:
    print("Error importing scripts.lib_advanced_metrics.")
    sys.exit(1)

def analyse_proposer(union_path, bounds_path, template_path):
    print(f"Analysing Proposer Consensus: {union_path}")
    
    # 1. Load Ground Truth
    try:
        _, gdf_bounds, gdf_ref = load_data(template_path, bounds_path)
    except Exception as e:
        print(f"Error loading ground truth: {e}")
        return

    # 2. Load Union
    try:
        gdf_pred = gpd.read_file(union_path)
        # Ensure CRS
        if not gdf_pred.empty:
            gdf_pred.set_crs("EPSG:32635", allow_override=True, inplace=True)
            if gdf_pred.crs != gdf_ref.crs: gdf_pred = gdf_pred.to_crs(gdf_ref.crs)
            
            # Filter NaNs in source_tile
            valid_mask = gdf_pred['source_tile'].notna()
            gdf_pred = gdf_pred[valid_mask].copy()
            
    except Exception as e:
        print(f"Error loading union: {e}")
        return
        
    print(f"Total Candidates: {len(gdf_pred)}")
    
    print(f"\n{'Votes':<10} | {'Recall':<10} | {'Precision':<10} | {'F1 Score':<10} | {'Count':<10}")
    print("-" * 60)
    
    best = {"f1": 0, "desc": ""}
    
    for v in range(1, 6):
        subset = gdf_pred[gdf_pred['proposer_votes'] >= v].copy()
        count = len(subset)
        
        if count == 0:
            print(f"{v:<10} | 0.0000     | 0.0000     | 0.0000     | 0")
            continue
            
        p, r, f1 = calculate_f1_internal(subset, gdf_ref, gdf_bounds)
        
        if f1 > best["f1"]:
            best = {"f1": f1, "desc": f"{v} Votes", "metrics": (p,r,f1)}
            
        best_mark = "🏆" if f1 > 0.7 else ""
        print(f"{v:<10} | {r:.4f}     | {p:.4f}     | {f1:.4f} {best_mark}   | {count}")
        
    print("-" * 60)
    if best['f1'] > 0:
        p, r, f1 = best['metrics']
        print(f"Best: {best['desc']} -> F1 {f1:.4f} (P {p:.4f}, R {r:.4f})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--union", required=True)
    parser.add_argument("--bounds", required=True)
    parser.add_argument("--template", required=True)
    args = parser.parse_args()
    
    analyse_proposer(args.union, args.bounds, args.template)
