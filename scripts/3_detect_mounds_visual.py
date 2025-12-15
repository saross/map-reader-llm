
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
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import GOOGLE_API_KEY, MODEL_NAME, TILES_DIR, OUTPUTS_DIR, RESULTS_DIR, TILE_SIZE, TEST_LIMIT, BASE_DIR

def detect_mounds_visual(tile_list=None, output_name=None, export_bounds=False):
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
    
    # Load V3 Prompt Text
    prompt_path = Path(BASE_DIR) / "prompts" / "V3_visual_mound_detection.md"
    try:
        with open(prompt_path, "r") as f:
            v3_prompt_text = f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {prompt_path}")
        return

    # Load Reference Images
    refs_dir = BASE_DIR / "references"
    ref_images = {}
    for ref_name in ["burial_mound", "settlement_mound", "triangulation_mound", "benchmark_mound"]:
        img_path = refs_dir / f"{ref_name}.png"
        if img_path.exists():
            ref_images[ref_name] = Image.open(img_path)
        else:
            print(f"Warning: Reference image {ref_name} not found.")

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=generation_config,
        system_instruction=v3_prompt_text
    )

    # Output file setup
    if output_name:
        filename = output_name
    else:
        current_date = datetime.now().strftime("%Y-%m-%d")
        sanitized_model = MODEL_NAME.replace("models/", "").replace("gemini-", "").replace("preview", "").strip("-")
        if not sanitized_model: sanitized_model = "model"
        filename = f"detections-visual-{current_date}-{sanitized_model}.geojson"
    
    output_file = RESULTS_DIR / filename
    print(f"Output will be saved to: {output_file}")
    
    # Load existing results
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

    # Gather tiles
    if tile_list:
        tiles_to_process = [t for t in tile_list if t.name not in processed_tiles]
        print(f"Using provided list of {len(tile_list)} tiles. {len(tiles_to_process)} remaining to process.")
    else:
        all_tiles = []
        for map_dir in TILES_DIR.iterdir():
            if map_dir.is_dir():
                all_tiles.extend(list(map_dir.glob("*.png")))
        all_tiles = sorted(all_tiles)
        print(f"Found {len(all_tiles)} tiles total.")
        tiles_to_process = [t for t in all_tiles if t.name not in processed_tiles]
        if TEST_LIMIT and TEST_LIMIT > 0:
            print(f"Applying TEST_LIMIT: Only processing {TEST_LIMIT} tiles.")
            tiles_to_process = tiles_to_process[:TEST_LIMIT]

    print(f"Processing {len(tiles_to_process)} new tiles...")

    save_frequency = 5 
    tile_features = []
    
    for i, tile_path in enumerate(tqdm(tiles_to_process)):
        filename = tile_path.name
        
        try:
            img = Image.open(tile_path)
            
            # Construct Multimodal Prompt
            # Interleave text and images
            content_parts = [
                "Here are the Reference Symbols you must find:",
            ]
            
            if "burial_mound" in ref_images:
                content_parts.append("Reference 1: Burial Mound (Kurgan)")
                content_parts.append(ref_images["burial_mound"])
            
            if "settlement_mound" in ref_images:
                content_parts.append("Reference 2: Settlement Mound")
                content_parts.append(ref_images["settlement_mound"])
                
            if "triangulation_mound" in ref_images:
                content_parts.append("Reference 3: Triangulation Point on Mound")
                content_parts.append(ref_images["triangulation_mound"])
            
            content_parts.append("Now, find these symbols in the Target Map Tile below:")
            content_parts.append(img)
            
            # API Call
            try:
                response = model.generate_content(
                    content_parts,
                    request_options={'timeout': 600}
                )
            except Exception as e:
                print(f"API Error for {filename}: {e}")
                time.sleep(20)
                continue

            # Parse Response
            detections = []
            try:
                json_response = json.loads(response.text)
                detections = json_response.get("detections", [])
            except Exception as e:
                print(f"Failed to parse response for {filename}: {e}")
                continue

            # Geotransform
            with rasterio.open(tile_path) as src:
                transform = src.transform
                crs = src.crs
                if export_bounds:
                    bounds = src.bounds
                    geom = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
                    tile_feat = geojson.Feature(
                        geometry=mapping(geom),
                        properties={"tile_name": filename, "type": "processed_tile_bbox"}
                    )
                    tile_features.append(tile_feat)
            
            # Convert to Features
            for det in detections:
                ymin_n, xmin_n, ymax_n, xmax_n = det["box_2d"]
                px_min_x = (xmin_n / 1000.0) * TILE_SIZE
                px_max_x = (xmax_n / 1000.0) * TILE_SIZE
                px_min_y = (ymin_n / 1000.0) * TILE_SIZE
                px_max_y = (ymax_n / 1000.0) * TILE_SIZE
                
                geo_x1, geo_y1 = transform * (px_min_x, px_min_y)
                geo_x2, geo_y2 = transform * (px_max_x, px_max_y)
                
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
                        "subtype": det.get("subtype", "unknown"),
                        "reasoning": det.get("reasoning", ""),
                        "confidence": "high",
                        "method": "visual_v3"
                    }
                )
                features.append(feature)

            time.sleep(10) # Rate limit
            
            if (i + 1) % save_frequency == 0:
                collection = geojson.FeatureCollection(features)
                if crs:
                    collection["crs"] = {"type": "name", "properties": {"name": f"urn:ogc:def:crs:EPSG::{crs.to_epsg()}"}}
                with open(output_file, "w") as f:
                    geojson.dump(collection, f)

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            time.sleep(20)

    # Final Save
    collection = geojson.FeatureCollection(features)
    collection["crs"] = {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::32635"}}
    with open(output_file, "w") as f:
        geojson.dump(collection, f)
        
    print(f"Finished. Saved {len(features)} detections to {output_file}")

if __name__ == "__main__":
    detect_mounds_visual()
