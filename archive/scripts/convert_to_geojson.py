
import json
from pathlib import Path
import geojson
from shapely.geometry import box, mapping
# Adjust python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import OUTPUTS_DIR, TILES_DIR, TILE_SIZE

def convert_to_geojson():
    input_file = OUTPUTS_DIR / "test_detections.json"
    if not input_file.exists():
        print(f"File not found: {input_file}")
        return

    with open(input_file) as f:
        detections_data = json.load(f)

    features = []
    
    # We need to find the metadata.json files. 
    # Since detections key is filename "K-35..._x...y...png", we can deduce the map name directory.
    # But simpler: search for the file in the tiles dir to find its parent.
    
    # Cache metadata to avoid repetitive loads
    metadata_cache = {}

    for filename, result in detections_data.items():
        if "error" in result:
            continue
            
        detections = result.get("detections", [])
        if not detections:
            continue

        # Find the map name from the filename
        # Assumption: Filename is mapname_x..._y...png
        # We can try to match the file path
        found_path = list(TILES_DIR.rglob(filename))
        if not found_path:
            print(f"Could not locate tile file {filename} in {TILES_DIR}")
            continue
        
        tile_path = found_path[0]
        map_dir = tile_path.parent
        metadata_path = map_dir / "metadata.json"
        
        if str(metadata_path) not in metadata_cache:
            if metadata_path.exists():
                with open(metadata_path) as f:
                    metadata_cache[str(metadata_path)] = json.load(f)
            else:
                print(f"Metadata not found for {filename} at {metadata_path}")
                continue

        # Get metadata for this specific tile
        tile_meta = metadata_cache[str(metadata_path)].get(filename)
        if not tile_meta:
            print(f"No metadata entry for {filename}")
            continue
            
        # Unpack [LowerLeftX, LowerLeftY, ResX, ResY]
        ll_x, ll_y, res_x, res_y = tile_meta
        
        for det in detections:
            # Gemini returns [ymin, xmin, ymax, xmax] in 0-1000 scale
            box_2d = det["box_2d"]
            ymin_n, xmin_n, ymax_n, xmax_n = box_2d
            
            # Convert to Pixel Coordinates (0-512)
            # 0 is Top, 512 is Bottom for Y in pixels
            # 0 is Left, 512 is Right for X in pixels
            
            px_min_y = (ymin_n / 1000) * TILE_SIZE
            px_max_y = (ymax_n / 1000) * TILE_SIZE
            px_min_x = (xmin_n / 1000) * TILE_SIZE
            px_max_x = (xmax_n / 1000) * TILE_SIZE
            
            # Convert to Geospatial Coordinates
            # GeoX = LowerLeftX + (PixelX * ResX)
            # GeoY = LowerLeftY + ((TILE_SIZE - PixelY) * ResY)
            
            # Since GeoY increases upwards (North), and PixelY increases downwards (South),
            # The "Top" pixel (min_y) corresponds to the Higher GeoY.
            # The "Bottom" pixel (max_y) corresponds to the Lower GeoY.
            
            geo_min_x = ll_x + (px_min_x * res_x)
            geo_max_x = ll_x + (px_max_x * res_x)
            
            # Note the flip for Y:
            # Pixel Min Y -> corresponds to Max Geo Y
            geo_max_y = ll_y + ((TILE_SIZE - px_min_y) * res_y)
            geo_min_y = ll_y + ((TILE_SIZE - px_max_y) * res_y)
            
            # Create Geometry (Shapely Box)
            # box(minx, miny, maxx, maxy)
            geom = box(geo_min_x, geo_min_y, geo_max_x, geo_max_y)
            
            # Create GeoJSON Feature
            feature = geojson.Feature(
                geometry=mapping(geom),
                properties={
                    "source_tile": filename,
                    "confidence": "test_run",
                    "label": det.get("label", "mound")
                }
            )
            features.append(feature)

    feature_collection = geojson.FeatureCollection(features)
    
    output_path = OUTPUTS_DIR / "test_detections.geojson"
    with open(output_path, "w") as f:
        geojson.dump(feature_collection, f)
        
    print(f"Saved {len(features)} features to {output_path}")

if __name__ == "__main__":
    convert_to_geojson()
