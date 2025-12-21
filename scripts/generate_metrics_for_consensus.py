import json
import argparse
from pathlib import Path
import geopandas as gpd
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.getcwd())
from scripts.lib_advanced_metrics import load_data, calculate_f1_internal, calculate_per_class_f1

def generate_metrics(run_dir, bounds_path, output_dir=None):
    run_dir = Path(run_dir)
    if output_dir is None:
        output_dir = run_dir
    print(f"Scanning runs in {run_dir}...")
    
    # Find all run_* files (excluding .meta.json, _metrics.json, etc)
    all_files = sorted(run_dir.glob("run_*"))
    run_files = []
    for f in all_files:
        if f.suffix in ['.json'] and 'meta' in f.name: continue
        if '_metrics' in f.name: continue
        if '_advanced_metrics' in f.name: continue
        if f.is_dir(): continue # Skip directories if any
        run_files.append(f)
    
    for run_file in run_files:
        run_name = run_file.stem # run_1
        print(f"Processing {run_name}...")
        
        try:
            # Load Data
            gdf_det, gdf_bounds, gdf_ref = load_data(run_file, bounds_path)
            
            if gdf_det is None or gdf_det.empty:
                print(f"Skipping {run_name}: No detections or load error.")
                continue

            # Calculate Metrics
            p, r, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds)
            
            # Calculate Per Class
            per_class_res = calculate_per_class_f1(gdf_det, gdf_ref, gdf_bounds)
            
            # Construct Metrics Dictionary (matching structure expected by benchmark_variability.py)
            metrics = {
                "precision": round(p, 4),
                "recall": round(r, 4),
                "f1": round(f1, 4),
                "tiles_processed": len(gdf_bounds['tile_name'].unique()) if gdf_bounds is not None else 0
            }
            
            # Advanced metrics (for per-class)
            advanced_metrics = {
                "per_class_performance": per_class_res
            }
            
            # Save metrics.json
            metrics_path = output_dir / f"{run_name}_metrics.json"
            with open(metrics_path, "w") as f:
                json.dump(metrics, f, indent=2)
                
            # Save advanced_metrics.json
            adv_metrics_path = output_dir / f"{run_name}_advanced_metrics.json"
            with open(adv_metrics_path, "w") as f:
                json.dump(advanced_metrics, f, indent=2)
                
            print(f"Saved metrics for {run_name}")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error processing {run_name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_dir", required=True, help="Directory containing run GeoJSONs")
    parser.add_argument("--bounds", required=True, help="Path to bounds GeoJSON")
    args = parser.parse_args()
    
    generate_metrics(args.run_dir, args.bounds)
