
import rasterio
import geojson
from pathlib import Path
import sys
# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from shapely.geometry import box, mapping
from tqdm import tqdm
from config import TILES_DIR, RESULTS_DIR

def generate_tile_index():
    print(f"Scanning tiles in {TILES_DIR}...")
    
    features = []
    
    # Iterate over all map content folders
    for map_dir in TILES_DIR.iterdir():
        if not map_dir.is_dir():
            continue
            
        map_name = map_dir.name
        print(f"Indexing {map_name}...")
        
        tiles = list(map_dir.glob("*.png"))
        
        for tile_path in tqdm(tiles):
            try:
                with rasterio.open(tile_path) as src:
                    bbox = src.bounds
                    geom = box(bbox.left, bbox.bottom, bbox.right, bbox.top)
                    
                    feature = geojson.Feature(
                        geometry=mapping(geom),
                        properties={
                            "tile_name": tile_path.name,
                            "map_name": map_name,
                            "path": str(tile_path)
                        }
                    )
                    features.append(feature)
            except Exception as e:
                print(f"Error reading {tile_path.name}: {e}")

    output_path = RESULTS_DIR / "all_tiles_index.geojson"
    
    collection = geojson.FeatureCollection(features)
    # create CRS 
    # Assuming all are 32635 as per project standard, but we can grab from last src if needed.
    # We'll just write the standard header.
    collection["crs"] = {
        "type": "name", 
        "properties": {
            "name": "urn:ogc:def:crs:EPSG::32635"
        }
    }
    
    with open(output_path, "w") as f:
        geojson.dump(collection, f)
        
    print(f"Index generated: {len(features)} tiles.")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    generate_tile_index()
