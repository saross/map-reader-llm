
import json
import geopandas as gpd
from pathlib import Path
import sys
import time
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import BASE_DIR, TILES_DIR
import importlib.util

def load_v3_module():
    spec = importlib.util.spec_from_file_location("detect_mounds_visual", str(BASE_DIR / "scripts/3_detect_mounds_visual.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules["detect_mounds_visual"] = module
    spec.loader.exec_module(module)
    return module

def run_missing():
    # 1. Load Calibration Manifest
    manifest_path = Path("inputs/calibration_manifest.json")
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    target_paths = [Path(p) for p in manifest]
    
    # 2. Load Existing Results
    existing_path = Path("outputs/results/detections-calibration-gemini3-pro.geojson")
    if existing_path.exists():
        existing_gdf = gpd.read_file(existing_path)
        done_names = set(existing_gdf['source_tile'].unique())
    else:
        done_names = set()
        existing_gdf = None

    # 3. Identify Missing
    missing_paths = []
    print("Checking for missing tiles...")
    for p in target_paths:
        if p.name not in done_names:
            # Check if file exists on disk (using the manifest path directly)
            if p.exists():
                missing_paths.append(p)
            else:
                found = list(TILES_DIR.rglob(p.name))
                if found:
                    if "Rakovski" in found[0].name: # Redundant check but safe
                        continue
                    missing_paths.append(found[0])
                else:
                    print(f"Critical: Tile {p.name} not found anywhere.")

    print(f"\nMissing Target Tiles (excluding Rakovski): {len(missing_paths)}")
    for p in missing_paths:
        print(f" - {p.name}")
        
    if not missing_paths:
        print("No tiles to process.")
        return

    # 4. Run Detection
    temp_output = "outputs/results/detections_calibration_missing.geojson"
    # Remove temp if exists to avoid appending dupes
    if Path(temp_output).exists():
        Path(temp_output).unlink()
        
    v3 = load_v3_module()
    print(f"\nStarting detection on {len(missing_paths)} tiles...")
    
    try:
        v3.detect_mounds_visual(tile_list=missing_paths, output_name=temp_output, export_bounds=False)
    except Exception as e:
        print(f"Run failed: {e}")
        
    # 5. Merge
    print("\nMerging results...")
    if Path(temp_output).exists():
        new_gdf = gpd.read_file(temp_output)
        if existing_gdf is not None:
            combined_gdf = pd.concat([existing_gdf, new_gdf], ignore_index=True)
        else:
            combined_gdf = new_gdf
            
        combined_gdf.to_file(existing_path, driver="GeoJSON")
        print(f"Merged {len(new_gdf)} new detections. Total: {len(combined_gdf)}")
    else:
        print("No new results generated.")

if __name__ == "__main__":
    run_missing()
