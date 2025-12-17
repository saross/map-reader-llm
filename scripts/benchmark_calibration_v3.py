
import json
import sys
from pathlib import Path
import geopandas as gpd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import BASE_DIR, TILES_DIR


# Dynamic Import Wrapper
import importlib.util
def load_v3_module():
    spec = importlib.util.spec_from_file_location("detect_mounds_visual", str(BASE_DIR / "scripts/3_detect_mounds_visual.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules["detect_mounds_visual"] = module
    spec.loader.exec_module(module)
    return module

def run_benchmark():
    # 1. Load Calibration Manifest
    manifest_path = BASE_DIR / "inputs/calibration_manifest.json"
    if not manifest_path.exists():
        print("Manifest not found!")
        return
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    # Extract tile names
    # Format: {"tiles": ["tile1.png", ...]} or just list?
    # Let's check format dynamically or assume list of dicts/strings
    # If list of dicts: [ {"tile_name": "..."} ]
    
    tile_names = []
    if isinstance(manifest, list):
         # Check first item
         if isinstance(manifest[0], str):
             tile_names = manifest
         elif isinstance(manifest[0], dict):
             tile_names = [t.get('tile_name') for t in manifest]
    elif isinstance(manifest, dict):
        # Maybe {"stratified_tiles": [...]}
        keys = list(manifest.keys())
        if "stratified_tiles" in keys:
            tile_names = manifest["stratified_tiles"]
        # Handle dict format if different
    
    if not tile_names:
        print("Could not parse manifest.")
        return

    print(f"Loaded {len(tile_names)} tiles from manifest.")
    
    # 2. Resolve Paths
    print("Resolving paths from manifest...")
    tile_paths = []
    
    for tpath_str in tile_names:
        p = Path(tpath_str)
        if p.exists():
            tile_paths.append(p)
        else:
            print(f"Warning: Tile {tpath_str} not found on disk.")
            
    print(f"Found {len(tile_paths)} valid tile paths.")
    
    if len(tile_paths) == 0:
        print("Aborting: No tiles found.")
        return
    
    # 3. Run Detection
    v3_module = load_v3_module()
    output_name = "detections-calibration-flash-rollback.geojson"
    
    print(f"Starting Flash Rollback Benchmark on {len(tile_paths)} tiles...")
    v3_module.detect_mounds_visual(tile_list=tile_paths, output_name=output_name, export_bounds=True)

if __name__ == "__main__":
    run_benchmark()
