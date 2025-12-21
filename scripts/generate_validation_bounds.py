
import json
import argparse
from pathlib import Path
import rasterio
from shapely.geometry import box, mapping
import geojson
import sys
import os

# Add parent directory to path
sys.path.append(os.getcwd())
from config import TILES_DIR, OUTPUTS_DIR

def generate_bounds(manifest_path, output_path):
    print(f"Reading manifest: {manifest_path}")
    with open(manifest_path, 'r') as f:
        target_filenames = json.load(f)
    
    features = []
    
    # Scan tiles dir
    all_tiles_map = {}
    for map_dir in TILES_DIR.iterdir():
        if map_dir.is_dir():
            for t in map_dir.glob("*.png"):
                all_tiles_map[t.name] = t
                
    found_count = 0
    for fname in target_filenames:
        if fname in all_tiles_map:
            tile_path = all_tiles_map[fname]
            found_count += 1
            
            try:
                with rasterio.open(tile_path) as src:
                    bounds = src.bounds
                    geom = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
                    
                    feature = geojson.Feature(
                        geometry=mapping(geom),
                        properties={
                            "tile_name": fname,
                            "map_name": tile_path.parent.name
                        }
                    )
                    features.append(feature)
            except Exception as e:
                print(f"Error reading {fname}: {e}")
                
    print(f"Found {found_count} of {len(target_filenames)} tiles.")
    
    collection = geojson.FeatureCollection(features)
    collection["crs"] = {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::32635"}}
    
    with open(output_path, "w") as f:
        geojson.dump(collection, f)
        
    print(f"Saved bounds to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    generate_bounds(args.manifest, args.output)
