
import json
import rasterio
import geojson
from pathlib import Path
from shapely.geometry import box, mapping
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import TILES_DIR, RESULTS_DIR

def reconstruct_bounds():
    # 1. List of Confirmed V2 Successes (Step 943)
    v2_tiles = [
        "K-35-062-2_Rakovski_x1792_y1792.png",
        "K-35-062-2_Rakovski_x2240_y1344.png",
        "K-35-062-2_Rakovski_x0_y2240.png",
        "K-35-062-2_Rakovski_x3584_y3584.png",
        "K-35-062-2_Rakovski_x3136_y2240.png",
        "K-35-052-4_32635_x1344_y448.png",
        "K-35-052-4_32635_x896_y3584.png",
        "K-35-052-4_32635_x3136_y1344.png",
        "K-35-052-4_32635_x2240_y896.png",
        "K-35-052-4_32635_x1792_y2688.png",
        "K-35-053-3_Elenovo_x1344_y1792.png",
        "K-35-053-3_Elenovo_x2688_y448.png",
        "K-35-053-3_Elenovo_x1792_y3136.png",
        "K-35-053-3_Elenovo_x448_y3136.png",
        "K-35-053-3_Elenovo_x3136_y2240.png",
        "K-35-078-1_Lesovo_x2240_y0.png",
        "K-35-078-1_Lesovo_x1792_y3584.png"
    ]
    
    # 2. List of Supplement Tiles (Step 998)
    supp_tiles = [
        "K-35-078-1_Lesovo_x448_y1344.png",
        "K-35-078-1_Lesovo_x2240_y3136.png",
        "K-35-078-1_Lesovo_x0_y2240.png"
    ]
    
    all_tiles = v2_tiles + supp_tiles
    print(f"Reconstructing bounds for {len(all_tiles)} tiles...")
    
    features = []
    
    for tile_name in all_tiles:
        # Determine map folder from tile name
        if "Rakovski" in tile_name: map_dir = "K-35-062-2_Rakovski"
        elif "32635" in tile_name: map_dir = "K-35-052-4_32635"
        elif "Elenovo" in tile_name: map_dir = "K-35-053-3_Elenovo"
        elif "Lesovo" in tile_name: map_dir = "K-35-078-1_Lesovo"
        else:
            print(f"Unknown map for {tile_name}")
            continue
            
        tile_path = TILES_DIR / map_dir / tile_name
        
        try:
            with rasterio.open(tile_path) as src:
                bbox = src.bounds
                geom = box(bbox.left, bbox.bottom, bbox.right, bbox.top)
                
                feature = geojson.Feature(
                    geometry=mapping(geom),
                    properties={
                        "tile_name": tile_name,
                        "type": "processed_tile_bbox" # Matching expectation of eval script
                    }
                )
                features.append(feature)
        except Exception as e:
            print(f"Error processing {tile_name}: {e}")

    output_path = RESULTS_DIR / "detections-calibration-stratified_bounds.geojson"
    
    collection = geojson.FeatureCollection(features)
    collection["crs"] = {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::32635"}}
    
    with open(output_path, "w") as f:
        geojson.dump(collection, f)
        
    print(f"Saved {len(features)} bounds to {output_path}")

if __name__ == "__main__":
    reconstruct_bounds()
