
import json
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Import project modules
sys.path.append(os.getcwd())
try:
    from scripts.run_v3_1_benchmark import evaluate_performance, generate_bounds, get_map_name
    from scripts.detect_mounds_batch import detect_mounds_versioned
    from scripts.config import RESULTS_DIR, INPUTS_DIR
except ImportError:
    # Handle dynamic import if needed, assuming running from root
    import importlib.util
    spec = importlib.util.spec_from_file_location("detect_mounds_batch", "scripts/4_detect_mounds_batch.py")
    dmb = importlib.util.module_from_spec(spec)
    sys.modules["detect_mounds_batch"] = dmb
    spec.loader.exec_module(dmb)
    from detect_mounds_batch import detect_mounds_versioned
    
    spec2 = importlib.util.spec_from_file_location("run_benchmark", "scripts/run_v3_1_benchmark.py")
    rb = importlib.util.module_from_spec(spec2)
    sys.modules["run_benchmark"] = rb
    spec2.loader.exec_module(rb)
    from run_benchmark import evaluate_performance, generate_bounds

# Fallback / Ensure definitions
if "RESULTS_DIR" not in globals():
    RESULTS_DIR = Path("outputs/results")
if "INPUTS_DIR" not in globals():
    INPUTS_DIR = Path("inputs")

def run_study(config_path, iterations, study_id, model_override=None):
    print(f"--- Starting Variability Study ---")
    print(f"Config: {config_path}")
    print(f"Model: {model_override if model_override else 'Default'}")
    print(f"Iterations: {iterations}")
    print(f"Study ID: {study_id}")
    
    # Setup Output Directory
    study_dir = RESULTS_DIR / study_id
    study_dir.mkdir(parents=True, exist_ok=True)
    
    manifest_path = INPUTS_DIR / "target_tiles_manifest.json"
    
    # Storage for metrics
    all_metrics = []
    
    for i in range(1, iterations + 1):
        print(f"\n[Iteration {i}/{iterations}]")
        
        # 1. Define Unique Output Name
        run_name = f"run_{i:02d}"
        output_geojson = f"{study_id}_{run_name}.geojson"
        
        # 2. Run Detection
        try:
            detect_mounds_versioned(
                config_path, 
                manifest_path=manifest_path, 
                output_name=output_geojson,
                export_bounds=True, # We need bounds for accurate FNs
                model_override=model_override
            )
        except Exception as e:
            print(f"Error in Iteration {i}: {e}")
            continue
            
        # 3. Paths
        with open(config_path, 'r') as f:
            v_tag = json.load(f).get("version", "unknown")
            
        # Reference in place
        res_dir = RESULTS_DIR / v_tag
        det_file = res_dir / output_geojson
        bounds_file = res_dir / (Path(output_geojson).stem + "_bounds.geojson")
        
        if not bounds_file.exists():
            generate_bounds(manifest_path, bounds_file)

        # 4. Evaluate
        output_prefix = str(study_dir / f"{run_name}")
        
        try:
            evaluate_performance(det_file, bounds_file, output_prefix)
            
            # 5. Read Metrics
            metrics_file = Path(output_prefix + "_metrics.json")
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    m = json.load(f)
                    m['iteration'] = i
                    all_metrics.append(m)
        except Exception as e:
             print(f"Evaluation Failed for {i}: {e}")

    # --- Analysis ---
    if not all_metrics:
        print("No successful runs to analyze.")
        return

    df = pd.DataFrame(all_metrics)
    
    # Calculate Stats
    stats = df[['precision', 'recall', 'f1']].describe()
    
    print("\n=== VARIABILITY STUDY RESULTS ===")
    print(stats)
    
    # Save Summary
    csv_path = study_dir / "summary_metrics.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nDetailed metrics saved to {csv_path}")
    
    stats_path = study_dir / "summary_stats.csv"
    stats.to_csv(stats_path)
    print(f"Summary stats saved to {stats_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="prompts/versions/v3.2_experimental.json", help="Config to test")
    parser.add_argument("--iterations", type=int, default=10, help="Number of runs")
    parser.add_argument("--study_id", required=True, help="Unique ID for this study output folder")
    parser.add_argument("--model", help="Model override (e.g., gemini-3-flash-preview)")
    
    args = parser.parse_args()
    
    run_study(args.config, args.iterations, args.study_id, args.model)
