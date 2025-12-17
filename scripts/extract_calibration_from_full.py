
import json
import geopandas as gpd
from pathlib import Path

def extract_calibration():
    # 1. Load Calibration Manifest
    manifest_path = Path("inputs/calibration_manifest.json")
    if not manifest_path.exists():
        print("Manifest missing.")
        return
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    # Get names of 20 tiles
    # Manifest is list of full paths. Extract names.
    target_tiles = [Path(p).name for p in manifest]
    print(f"Targeting {len(target_tiles)} calibration tiles.")
    
    # 2. Load Full Run Results
    full_path = Path("outputs/results/detections-visual-2025-12-17-3-pro.geojson")
    if not full_path.exists():
        print("Full run results missing.")
        return
        
    print("Loading full run data...")
    full_gdf = gpd.read_file(full_path)
    
    # 3. Filter
    calibration_gdf = full_gdf[full_gdf['source_tile'].isin(target_tiles)].copy()
    
    print(f"Found matches for {calibration_gdf['source_tile'].nunique()} of {len(target_tiles)} tiles.")
    print(f"Total Detections Extracted: {len(calibration_gdf)}")
    
    missing = set(target_tiles) - set(calibration_gdf['source_tile'].unique())
    if missing:
        print(f"Missing Tiles: {list(missing)[:5]}...")
        
    # 4. Save
    output_path = Path("outputs/results/detections-calibration-gemini3-pro.geojson")
    calibration_gdf.to_file(output_path, driver="GeoJSON")
    print(f"Saved extracted results to {output_path}")

if __name__ == "__main__":
    extract_calibration()
