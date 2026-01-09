
import argparse
import sys
import os
from pathlib import Path

# Add parent to path to import scripts
sys.path.append(os.getcwd())
from scripts.run_v3_1_benchmark import evaluate_performance, generate_bounds

# Hardcoded paths based on the known output
RESULTS_DIR = Path("outputs/results/v3.2_experimental")
DETECTION_FILE = RESULTS_DIR / "detections-v3.2_experimental-3-flash-2025-12-18.geojson"
OUTPUT_PREFIX = str(RESULTS_DIR / "final_verification_v3.2")

def main():
    if not DETECTION_FILE.exists():
        print(f"Error: Detection file {DETECTION_FILE} not found.")
        return

    print(f"Scoring Results: {DETECTION_FILE}")
    
    # Generate bounds if needed (using manifest)
    bounds_file = RESULTS_DIR / "final_verification_bounds.geojson"
    manifest_path = "inputs/target_tiles_manifest.json"
    
    if not bounds_file.exists():
        generate_bounds(manifest_path, bounds_file)
        
    evaluate_performance(DETECTION_FILE, bounds_file, OUTPUT_PREFIX)

if __name__ == "__main__":
    main()
