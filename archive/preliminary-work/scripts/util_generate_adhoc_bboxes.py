import sys
import geojson
import rasterio
from pathlib import Path
from shapely.geometry import box, mapping

# Adjust path
sys.path.append(str(Path(__file__).parent.parent))
from config import TILES_DIR, RESULTS_DIR

def generate_adhoc_bboxes():
    # Input: The robust results we just generated
    input_geojson = RESULTS_DIR / "detections-K-35-062-2_Rakovski-robust-random5.geojson"
    output_geojson = RESULTS_DIR / "tile_bboxes-rakovski-random5.geojson"
    
    if not input_geojson.exists():
        print(f"Error: {input_geojson} not found.")
        return

    print(f"Reading {input_geojson}...")
    with open(input_geojson, 'r') as f:
        data = geojson.load(f)
        
    # Extract unique source tiles
    processed_tiles = set()
    features = data.get("features", [])
    for feat in features:
        if "source_tile" in feat["properties"]:
            processed_tiles.add(feat["properties"]["source_tile"])
            
    print(f"Found {len(processed_tiles)} unique tiles in results.")
    
    # Generate BBox Features
    bbox_features = []
    
    # We need to find these tiles in TILES_DIR
    # We know the map name is K-35-062-2_Rakovski from the filename or context, 
    # but let's just search for them in the known directory to be safe.
    map_dir = TILES_DIR / "K-35-062-2_Rakovski"
    
    for tile_name in processed_tiles:
        tile_path = map_dir / tile_name
        if not tile_path.exists():
            print(f"Warning: Tile {tile_name} not found in {map_dir}")
            continue
            
        try:
            with rasterio.open(tile_path) as src:
                bounds = src.bounds # (left, bottom, right, top)
                crs = src.crs
                
                geom = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
                
                feature = geojson.Feature(
                    geometry=mapping(geom),
                    properties={
                        "tile_name": tile_name,
                        "type": "processed_tile_bbox"
                    }
                )
                bbox_features.append(feature)
        except Exception as e:
            print(f"Error reading {tile_name}: {e}")

    # Save
    collection = geojson.FeatureCollection(bbox_features)
    # Assume CRS is uniform (32635) or take from last
    collection["crs"] = {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:EPSG::32635" 
        }
    }
    
    with open(output_geojson, "w") as f:
        geojson.dump(collection, f)
        
    print(f"Saved {len(bbox_features)} tile bounding boxes to {output_geojson}")

if __name__ == "__main__":
    generate_adhoc_bboxes()
