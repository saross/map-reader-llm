
import json
import time
import os
from pathlib import Path
from tqdm import tqdm
import google.generativeai as genai
from PIL import Image
import geojson
from shapely.geometry import box, mapping
import rasterio

# Adjust python path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import GOOGLE_API_KEY, MODEL_NAME, TILES_DIR, OUTPUTS_DIR, TILE_SIZE, TEST_LIMIT

def detect_mounds():
    # Configure Gemini
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found.")
        return

    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Model Configuration
    generation_config = {
        "temperature": 0.1,
        "response_mime_type": "application/json",
    }
    
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=generation_config,
        system_instruction="""
        You are an expert analyst of Soviet 1:50,000 Topographic Maps.
        Your goal is to identify archaeological "Burial Mound" (Tumulus) symbols.
        
        Target Symbols:
        1. "Burial Mound": "sunburst"; "An orange-brown, sun-like or gear-shaped symbol consisting of a central circle/ring with short, radiating spikes extending outward."
        
        Negative Constraints:
        - DISTINCTLY IGNORE brown contour lines that do not form a distinct sunburst or circle-dot.
        - IGNORE black elevation points (simple dots) unless surrounded by a mound circle.
        - IGNORE blue wells (circles with blue filling).
        - IGNORE vegetation patterns.
        
        Output format: return a JSON object with detections using normalized coordinates (0-1000).
        """
    )

    # Output file (GeoJSON)
    output_file = OUTPUTS_DIR / "all_detections.geojson"
    
    # Load existing results if any to resume
    features = []
    processed_tiles = set()
    
    if output_file.exists():
        try:
            with open(output_file, 'r') as f:
                data = geojson.load(f)
                features = data.get("features", [])
                for feat in features:
                    if "source_tile" in feat["properties"]:
                        processed_tiles.add(feat["properties"]["source_tile"])
        except Exception:
            print("Could not read existing GeoJSON, starting fresh.")
            features = []

    # Gather all tiles
    # We rely on spatial metadata in the files now, so we just look for PNGs
    all_tiles = []
    for map_dir in TILES_DIR.iterdir():
        if map_dir.is_dir():
            all_tiles.extend(list(map_dir.glob("*.png")))
    
    all_tiles = sorted(all_tiles)
    print(f"Found {len(all_tiles)} tiles total.")
    
    # Filter out already processed tiles
    tiles_to_process = [t for t in all_tiles if t.name not in processed_tiles]
    
    # Cost Control: Limit processing
    if TEST_LIMIT and TEST_LIMIT > 0:
        print(f"Applying TEST_LIMIT: Only processing {TEST_LIMIT} tiles.")
        tiles_to_process = tiles_to_process[:TEST_LIMIT]

    print(f"Processing {len(tiles_to_process)} new tiles...")

    prompt = """
    Look at this Soviet map tile. 
    Identify the bounding boxes of all 'Burial Mound' symbols.
    
    Return a JSON object in this format (use normalized coordinates 0-1000):
    {
        "detections": [
            {
                "box_2d": [ymin, xmin, ymax, xmax], 
                "label": "mound", 
                "reasoning": "Brief explanation"
            }
        ]
    }
    """

    save_frequency = 5 
    
    for i, tile_path in enumerate(tqdm(tiles_to_process)):
        filename = tile_path.name
        
        try:
            img = Image.open(tile_path)
            
            # API Call
            try:
                response = model.generate_content([prompt, img])
            except Exception as e:
                print(f"API Error for {filename}: {e}")
                time.sleep(20) # Backoff
                continue

            # Parse Response
            detections = []
            try:
                json_response = json.loads(response.text)
                detections = json_response.get("detections", [])
            except Exception as e:
                print(f"Failed to parse response for {filename}: {e}")
                continue

            # Geotransform using Rasterio
            with rasterio.open(tile_path) as src:
                transform = src.transform
                crs = src.crs
            
            # Convert to GeoJSON Features
            for det in detections:
                ymin_n, xmin_n, ymax_n, xmax_n = det["box_2d"]
                
                # Convert Normalized (0-1000) to Pixel Coords
                # Note: TILE_SIZE is used, assuming tile is TILE_SIZE x TILE_SIZE
                # We can also get width/height from 'src' if we wanted to be perfectly safe,
                # but TILE_SIZE is constant.
                
                px_min_x = (xmin_n / 1000.0) * TILE_SIZE
                px_max_x = (xmax_n / 1000.0) * TILE_SIZE
                px_min_y = (ymin_n / 1000.0) * TILE_SIZE
                px_max_y = (ymax_n / 1000.0) * TILE_SIZE
                
                # Convert Pixel to Geo using Affine Transform
                # transform * (col, row) -> (x, y)
                # Box corners:
                # Top-Left Pixel (min_x, min_y) -> Geo (min_gx, max_gy) usually?
                # Let's just transform all 4 corners or min/max.
                
                geo_x1, geo_y1 = transform * (px_min_x, px_min_y)
                geo_x2, geo_y2 = transform * (px_max_x, px_max_y)
                
                # Since Y axis is inverted in pixels vs geo usually:
                min_geo_x = min(geo_x1, geo_x2)
                max_geo_x = max(geo_x1, geo_x2)
                min_geo_y = min(geo_y1, geo_y2)
                max_geo_y = max(geo_y1, geo_y2)
                
                geom = box(min_geo_x, min_geo_y, max_geo_x, max_geo_y)
                
                feature = geojson.Feature(
                    geometry=mapping(geom),
                    properties={
                        "source_tile": filename,
                        "label": det.get("label", "mound"),
                        "reasoning": det.get("reasoning", ""),
                        "confidence": "high"
                    }
                )
                features.append(feature)

            # Rate Limit Sleep
            time.sleep(10)
            
            # Periodically save
            if (i + 1) % save_frequency == 0:
                collection = geojson.FeatureCollection(features)
                if crs:
                    collection["crs"] = {
                        "type": "name",
                        "properties": {
                            "name": f"urn:ogc:def:crs:EPSG::{crs.to_epsg()}"
                        }
                    }
                with open(output_file, "w") as f:
                    geojson.dump(collection, f)

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            time.sleep(20)

    # Final Save
    collection = geojson.FeatureCollection(features)
    # Use last valid CRS? Or default
    collection["crs"] = {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:EPSG::32635" 
        }
    }
    with open(output_file, "w") as f:
        geojson.dump(collection, f)
        
    print(f"Finished. Saved {len(features)} detections to {output_file}")

if __name__ == "__main__":
    detect_mounds()
