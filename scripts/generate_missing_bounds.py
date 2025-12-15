
import sys
from pathlib import Path
import geojson
from shapely.geometry import box, mapping
import rasterio

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import TILES_DIR, RESULTS_DIR

def generate_missing_bounds():
    tile_names = [
        "K-35-062-2_Rakovski_x1792_y1792.png",
        "K-35-062-2_Rakovski_x2240_y1344.png",
        "K-35-062-2_Rakovski_x0_y2240.png",
        "K-35-062-2_Rakovski_x3584_y3584.png",
        "K-35-062-2_Rakovski_x3136_y2240.png"
    ]
    
    map_dir = TILES_DIR / "K-35-062-2_Rakovski"
    selected_tiles = [map_dir / t for t in tile_names]
    
    output_name = "detections-rakovski-v3-random5-retry_bounds.geojson"
    output_file = RESULTS_DIR / output_name
    
    tile_features = []
    print(f"Generating bounds for {len(selected_tiles)} tiles...")
    
    for tile_path in selected_tiles:
        if not tile_path.exists():
            print(f"Warning: {tile_path} does not exist")
            continue
            
        with rasterio.open(tile_path) as src:
            bounds = src.bounds
            geom = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
            tile_feat = geojson.Feature(
                geometry=mapping(geom),
                properties={"tile_name": tile_path.name, "type": "processed_tile_bbox"}
            )
            tile_features.append(tile_feat)

    bounds_collection = geojson.FeatureCollection(tile_features)
    bounds_collection["crs"] = {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:EPSG::32635" 
        }
    }
    
    with open(output_file, "w") as f:
        geojson.dump(bounds_collection, f)
    
    print(f"Saved {len(tile_features)} tile bounding boxes to {output_file}")

if __name__ == "__main__":
    generate_missing_bounds()
