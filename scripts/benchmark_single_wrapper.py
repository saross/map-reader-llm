
import argparse
import sys
import os
import json
from pathlib import Path

# Extend path to import sibling scripts
sys.path.append(os.getcwd())
from scripts.run_v3_1_benchmark import run_benchmark
from scripts.lib_advanced_metrics import generate_report, print_report_summary

def main():
    parser = argparse.ArgumentParser(description="Standardized Benchmark Wrapper (Single Run)")
    parser.add_argument("--config", required=True, help="Path to config JSON (e.g., prompts/configs/detect_image-only.json)")
    parser.add_argument("--model", required=False, help="Override model (e.g., gemini-3-flash-preview)")
    parser.add_argument("--bootstrap", type=int, default=1000, help="Number of bootstrap iterations for CI (default: 1000)")
    
    args = parser.parse_args()
    
    # 1. Run Standard Benchmark
    # This runs detection + basic eval + generates _metrics.json and _advanced_metrics.json (default settings)
    print(f"--- Starting Single Benchmark Wrapper ---")
    run_benchmark(config_path=args.config, model_override=args.model)
    
    # 2. Verify Advanced Metrics were generated
    # We need to construct the path to check.
    # run_benchmark derives path from config['version']
    with open(args.config) as f:
        cfg = json.load(f)
        version = cfg.get("version", "vX")
        
    results_dir = Path("outputs/results") / version
    output_name = f"benchmark_{version}.geojson"
    adv_metrics_path = results_dir / f"benchmark_{version}_advanced_metrics.json"
    
    # 2. Generate/Update Advanced Metrics
    # We always regenerate this to ensure 'bootstrap_iterations' matches the CLI argument
    results_dir = Path("outputs/results") / version
    output_name = f"benchmark_{version}.geojson"
    adv_metrics_path = results_dir / f"benchmark_{version}_advanced_metrics.json"
    det_file = results_dir / output_name
    bound_file = results_dir / f"benchmark_{version}_bounds.geojson"

    if det_file.exists() and bound_file.exists():
        generate_report(det_file, bound_file, output_path=adv_metrics_path, bootstrap_iterations=args.bootstrap)
    
    # 3. Print Summary
    if adv_metrics_path.exists():
        with open(adv_metrics_path) as f:
            report = json.load(f)
        print_report_summary(report, title=f"Benchmark: {version}")

if __name__ == "__main__":
    main()
