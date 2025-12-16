
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
    
    # Model Configuration - Optimal for Research Extraction
    generation_config = {
        "temperature": 0.1,             # Low creativity for factual extraction
        "top_p": 0.95,                  # Standard nucleus sampling
        "top_k": 40,                    # Standard top-k
        "max_output_tokens": 8192,      # Ensure large JSONs aren't truncated
        "response_mime_type": "application/json",
    }
    
    # Safety Settings: Block NONE to prevent scientific data censorship
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
    # Load V3 Prompt Text
    prompt_path = Path(BASE_DIR) / "prompts" / "V3_visual_mound_detection.md"
    try:
        with open(prompt_path, "r") as f:
            v3_prompt_text = f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {prompt_path}")
        return

    # Load Reference Images & Build Few-Shot Prompt Context
    refs_dir = BASE_DIR / "references"
    reference_content = []
    
    # Helper to add ref if exists
    def add_ref(path, label):
        if path.exists():
            reference_content.append(label)
            reference_content.append(Image.open(path))
        else:
            print(f"Warning: Reference image {path.name} not found.")

    # 1. Burial Mounds
    reference_content.append("--- Class 1: Burial Mounds (Kurgan) ---")
    add_ref(refs_dir / "burial_mound.png", "Example 1A: Standard Legend Symbol (Sunburst)")
    add_ref(refs_dir / "ref_variant_2.png", "Example 1B: Real Map Variant (Simpler/Degraded)")

    # 2. Settlement Mounds
    reference_content.append("--- Class 2: Settlement Mounds ---")
    add_ref(refs_dir / "settlement_mound.png", "Example 2A: Standard Legend Symbol (Irregular/Ticks)")

    # 3. Triangulation/Benchmark Mounds
    reference_content.append("--- Class 3: Triangulation/Benchmark on Mound ---")
    add_ref(refs_dir / "triangulation_mound.png", "Example 3A: Triangulation Point (Triangle + Spikes)")
    add_ref(refs_dir / "benchmark_mound.png", "Example 3B: Benchmark (Square + Spikes)")
    add_ref(refs_dir / "ref_variant_1.png", "Example 3C: Real Map Variant (Benchmark)")

    # 4. Negative Examples (False Positives)
    reference_content.append("--- NEGATIVE EXAMPLES (DO NOT DETECT) ---")
    reference_content.append("The following images are confirmed False Positives (noise/labels). Absolute rule: If a symbol detects as a visual match to these, IGNORE IT.")
    add_ref(refs_dir / "ref_negative_1.png", "Negative Example 1: Degraded Label/Noise")
    
    # Initialize Model with Safety Settings
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=generation_config,
        system_instruction=v3_prompt_text,
        safety_settings=safety_settings
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

    save_frequency = 1 
    tile_features = []
    
    for i, tile_path in enumerate(tqdm(tiles_to_process)):
        tile_filename = tile_path.name
        
        try:
            img = Image.open(tile_path)
            
            # Construct Multimodal Prompt
            # Interleave text and images
            content_parts = [
                "Here are the Reference Symbols you must find:",
            ]
            content_parts.extend(reference_content)
            
            content_parts.append("Now, find detection instances that visually match ANY of the above Reference Examples in the Target Map Tile below:")
            content_parts.append(img)
            # Robust API Call with Retries
            # User Requirement: speed is not crucial, robustness is key.
            # User Requirement: DO NOT fallback. 
            max_retries = 5
            base_wait = 30 # seconds
            
            response = None
            for attempt in range(max_retries):
                try:
                    # Explicit timeout of 900s (15 mins) for complex high-res reasoning
                    response = model.generate_content(
                        content_parts,
                        request_options={'timeout': 900} 
                    )
                    break # Success
                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "ResourceExhausted" in error_str:
                        wait = base_wait * (2 ** attempt) # Exponential backoff: 30, 60, 120...
                        print(f"\n[Warning] Rate Limit (429) hit for {tile_filename}. Waiting {wait}s before retry {attempt+1}/{max_retries}...")
                        time.sleep(wait)
                    elif "503" in error_str or "ServiceUnavailable" in error_str:
                        print(f"\n[Warning] Service Unavailable (503) for {tile_filename}. Waiting 30s...")
                        time.sleep(30)
                    elif "DeadlineExceeded" in error_str:
                        print(f"\n[Warning] Timeout (DeadlineExceeded) for {tile_filename}. Retrying...")
                        time.sleep(30)
                    elif "404" in error_str and "models/" in error_str:
                         # Strict Requirement: Report failure if model not found, DO NOT FALLBACK.
                         print(f"\n[CRITICAL] Model '{MODEL_NAME}' not found or not available. Terminating.")
                         return
                    else:
                        print(f"\n[Error] Unexpected API Error for {tile_filename}: {e}")
                        # For unhandled errors, we might want to skip the tile or retry?
                        # Given "robustness", we'll retry once or twice then skip.
                        if attempt < 2: 
                            time.sleep(20)
                        else:
                            print(f"Skipping tile {tile_filename} after repeated errors.")
                            break
            
            if not response:
                print(f"Failed to get response for {tile_filename} after retries.")
                continue

            # Parse Response
            detections = []
            try:
                json_response = json.loads(response.text)
                detections = json_response.get("detections", [])
            except Exception as e:
                print(f"Failed to parse response for {tile_filename}: {e}")
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
                        properties={"tile_name": tile_filename, "type": "processed_tile_bbox"}
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
                        "source_tile": tile_filename,
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
            print(f"Error processing {tile_filename}: {e}")
            time.sleep(20)

    # Final Save
    collection = geojson.FeatureCollection(features)
    collection["crs"] = {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::32635"}}
    with open(output_file, "w") as f:
        geojson.dump(collection, f)
        
    print(f"Finished. Saved {len(features)} detections to {output_file}")
    
    # Export bounds if requested
    if export_bounds:
        bounds_filename = Path(filename).stem + "_bounds.geojson"
        bounds_file = RESULTS_DIR / bounds_filename
        
        bounds_collection = geojson.FeatureCollection(tile_features)
        bounds_collection["crs"] = {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:EPSG::32635" 
            }
        }
        with open(bounds_file, "w") as f:
            geojson.dump(bounds_collection, f)
        print(f"Saved {len(tile_features)} tile bounding boxes to {bounds_file}")

if __name__ == "__main__":
    detect_mounds_visual()
