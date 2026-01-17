"""
Batch Mound Detection Script
============================
Description:
    The core inference engine. Orchestrates the loading of map tiles, construction of 
    multimodal prompts (visual + text), and interaction with the Google Gemini API.
    Designed for reproducibility, it uses a versioned configuration system and tracks 
    comprehensive metadata (prompt hashes, model versions) for every run.

Usage:
    python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_image-only.json

Inputs:
    - Tiles from `outputs/tiles/`
    - Prompt Config from `prompts/configs/*.json`
    - System Instructions from `prompts/system-instructions/*.md`

Outputs:
    - Raw GeoJSON detections in `outputs/results/vX.X/`
    - Processing Metadata (.meta.json)

Author: Shawn Ross, Adela Sobotkova
License: Apache 2.0
"""

import json
import time
import argparse
from pathlib import Path
from tqdm import tqdm
import google.generativeai as genai
from PIL import Image
import geojson
from shapely.geometry import box, mapping
import rasterio
import sys
from datetime import datetime, timezone
import concurrent.futures
import threading

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import GOOGLE_API_KEY, TILES_DIR, RESULTS_DIR, TILE_SIZE, TEST_LIMIT, BASE_DIR, EXAMPLES_DIR

# Import comprehensive metadata tracking
from scripts.lib_llm_metadata import (
    LLMMetadataTracker,
    extract_gemini_metadata,
    create_error_metadata,
    estimate_cost,
    LLMProvider
)


# Script Version
__version__ = "4.2.0"  # Comprehensive metadata tracking

class ResultsTracker:
    """
    Lightweight thread-safe tracker for detection results.

    Works alongside LLMMetadataTracker to aggregate task-specific results.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.total_detections = 0
        self.class_counts = {}

    def update(self, detections):
        """Update results with new detections."""
        with self._lock:
            self.total_detections += len(detections)
            for det in detections:
                subtype = det.get("subtype", "unknown")
                self.class_counts[subtype] = self.class_counts.get(subtype, 0) + 1

    def get_summary(self):
        """Return results summary dict."""
        with self._lock:
            return {
                "total_detections": self.total_detections,
                "class_counts": dict(self.class_counts)
            }

def process_single_tile(
    tile_path,
    model,
    metadata_tracker,
    results_tracker,
    reference_content,
    base_wait,
    max_retries,
    config_version,
    model_name_cfg
):
    """
    Worker function to process a single tile with comprehensive metadata capture.

    Args:
        tile_path: Path to the tile image
        model: The Gemini model instance
        metadata_tracker: LLMMetadataTracker for API metadata
        results_tracker: ResultsTracker for detection counts
        reference_content: List of reference images and labels
        base_wait: Base wait time for rate limit retries
        max_retries: Maximum retry attempts
        config_version: Version string from config
        model_name_cfg: Model name from config

    Returns:
        List of GeoJSON features for detected mounds
    """
    tile_filename = tile_path.name
    features = []

    try:
        img = Image.open(tile_path)

        content_parts = [
            "Here are the Reference Symbols you must find:",
        ]
        content_parts.extend(reference_content)
        content_parts.append(
            "Now, find detection instances that visually match ANY of the "
            "above Reference Examples in the Target Map Tile below:"
        )
        content_parts.append(img)

        response = None
        response_metadata = None

        for attempt in range(max_retries):
            request_start = datetime.now(timezone.utc)

            try:
                response = model.generate_content(
                    content_parts,
                    request_options={'timeout': 900}
                )

                # Extract comprehensive metadata from response
                response_metadata = extract_gemini_metadata(
                    response=response,
                    request_start=request_start,
                    model_requested=model_name_cfg,
                    item_id=tile_filename,
                    attempt=attempt + 1
                )

                # Check Finish Reason
                if hasattr(response, 'candidates') and response.candidates:
                    reason = response.candidates[0].finish_reason
                    if reason == 2:  # MAX_TOKENS
                        metadata_tracker.log_retry(
                            tile_filename,
                            attempt + 1,
                            "MAX_TOKENS (Finish Reason 2)",
                            error_type="other"
                        )
                        time.sleep(5)
                        continue
                    elif reason != 1:  # Not STOP (Success)
                        pass  # Log but continue

                # Check content validity
                if response.candidates and response.candidates[0].content.parts:
                    break  # Success
                else:
                    if attempt < max_retries - 1:
                        time.sleep(5)
                        continue

            except Exception as e:
                error_str = str(e)

                # Create error metadata
                response_metadata = create_error_metadata(
                    error=e,
                    request_start=request_start,
                    provider=LLMProvider.GEMINI.value,
                    model_requested=model_name_cfg,
                    item_id=tile_filename,
                    attempt=attempt + 1
                )

                # Categorise and log retry
                if "429" in error_str or "ResourceExhausted" in error_str:
                    metadata_tracker.log_retry(
                        tile_filename, attempt + 1, error_str, error_type="rate_limit"
                    )
                    wait = base_wait * (2 ** attempt) + (attempt * 2)
                    time.sleep(wait)
                elif "503" in error_str or "InternalServerError" in error_str:
                    metadata_tracker.log_retry(
                        tile_filename, attempt + 1, error_str, error_type="server_error"
                    )
                    time.sleep(30)
                elif "DeadlineExceeded" in error_str:
                    metadata_tracker.log_retry(
                        tile_filename, attempt + 1, error_str, error_type="timeout"
                    )
                    time.sleep(30)
                elif "404" in error_str and "models/" in error_str:
                    print(f"\n[CRITICAL] Model '{model_name_cfg}' not found. Terminating.")
                    return []  # Fatal
                else:
                    metadata_tracker.log_retry(
                        tile_filename, attempt + 1, error_str, error_type="other"
                    )
                    print(f"\n[Error] {tile_filename}: {e}")
                    if attempt < 2:
                        time.sleep(20)
                    else:
                        break

        # Check for valid response
        valid_response = (
            response and
            hasattr(response, 'candidates') and
            response.candidates and
            response.candidates[0].finish_reason == 1
        )

        if not valid_response:
            if response_metadata:
                response_metadata.parse_success = False
            metadata_tracker.log_failure(tile_filename, "Retries Exhausted / Invalid Finish Reason")
            if response_metadata:
                metadata_tracker.log_response(tile_filename, response_metadata)
            return []

        # Log successful response metadata
        if response_metadata:
            metadata_tracker.log_response(tile_filename, response_metadata)

        metadata_tracker.log_success(tile_filename)

        # Parse detections
        detections = []
        try:
            json_response = json.loads(response.text)
            if isinstance(json_response, list):
                # Handle case where model returns [ { "detections": [...] } ]
                if (
                    len(json_response) > 0 and
                    isinstance(json_response[0], dict) and
                    "detections" in json_response[0]
                ):
                    detections = json_response[0]["detections"]
                else:
                    detections = json_response
            else:
                detections = json_response.get("detections", [])
            results_tracker.update(detections)
        except Exception as e:
            print(f"Failed to parse response for {tile_filename}: {e}")
            metadata_tracker.log_failure(tile_filename, f"JSON Parse Error: {e}")
            return []

        with rasterio.open(tile_path) as src:
            transform = src.transform
            crs = src.crs

        for det in detections:
            if "box_2d" not in det:
                continue
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
                    "confidence": "high",
                    "method": config_version,
                    "model": model_name_cfg
                }
            )
            features.append(feature)
            
        return features

    except Exception as e:
        print(f"Error processing {tile_filename}: {e}")
        tracker.log_failure(tile_filename, str(e))
        return []

def detect_mounds_versioned(config_path, manifest_path=None, tile_list=None, output_name=None, export_bounds=False, model_override=None, workers=1):
    """
    Executes the detection pipeline using a specific versioned configuration.

    Args:
        config_path (str): Path to the JSON configuration file defining the experiment properties.
        manifest_path (str, optional): Path to a JSON list of filenames to process (Target Set).
        tile_list (list, optional): List of specific Path objects to process (Manual override).
        output_name (str, optional): Custom filename for the output GeoJSON.
        export_bounds (bool, optional): If True, exports the bounding boxes of processed tiles (debug feature).
        model_override (str, optional): Overrides the model defined in the JSON config.
        workers (int, optional): Number of parallel workers. Defaults to 1.
    """
    # Load Config
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    # Add manifest to config for tracking
    if manifest_path:
        config["manifest_path"] = str(manifest_path)

    # Apply Model Override
    if model_override:
        print(f"Overriding Config Model ({config.get('model')}) with CLI Argument: {model_override}")
        config["model"] = model_override
        # Note: MetadataTracker uses 'config' object, so this change will be automatically recorded in metadata.

    print(f"Loaded Version: {config.get('version', 'unknown')}")
    print(f"Model: {config.get('model', 'unknown')}")
    print(f"Workers: {workers}")

    model_name_cfg = config.get("model")
    
    # Configure Gemini
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found.")
        return

    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Load Prompt Text
    instruction_file = config.get("instruction_file", "v3.0_system_instruction.md")
    prompt_path = Path(BASE_DIR) / "prompts" / "system-instructions" / instruction_file
    
    print(f"System Instruction: {instruction_file}") # Feedback to user

    try:
        with open(prompt_path, "r") as f:
            v3_prompt_text = f.read()
    except FileNotFoundError:
        print(f"Error: Prompt text not found at {prompt_path}")
        return

    # Initialise metadata tracker for comprehensive API logging
    metadata_tracker = LLMMetadataTracker(
        config=config,
        system_instruction=v3_prompt_text,
        script_name="4_detect_mounds_batch.py",
        script_version=__version__
    )

    # Initialise results tracker for detection counts
    results_tracker = ResultsTracker()

    # Build Few-Shot Context from Config
    examples_dir = EXAMPLES_DIR
    reference_content = []

    examples = config.get("examples", [])
    for ex in examples:
        label = ex.get("label", "Example")
        path_str = ex.get("path", "")
        img_path = examples_dir / path_str
        
        if img_path.exists():
            reference_content.append(label)
            reference_content.append(Image.open(img_path))
        else:
            print(f"Warning: Reference image {path_str} not found.")

    # Initialize Model Configuration (Shared)
    generation_config = {
        "temperature": config.get("temperature", 0.1),
        "top_p": config.get("top_p", 0.95),
        "top_k": config.get("top_k", 40),
        "max_output_tokens": config.get("max_output_tokens", 8192),
        "response_mime_type": "application/json",
    }

    # Add thinking_level if specified (Gemini 3 reasoning depth control)
    # Note: API uses camelCase 'thinkingLevel' in GenerationConfig
    if "thinking_level" in config:
        generation_config["thinkingLevel"] = config["thinking_level"]
    
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    try:
        model = genai.GenerativeModel(
            model_name=model_name_cfg,
            generation_config=generation_config,
            system_instruction=v3_prompt_text,
            safety_settings=safety_settings
        )
    except Exception as e:
        print(f"Error initializing model {model_name_cfg}: {e}")
        return

    # Output file setup
    if output_name:
        filename = output_name
    else:
        current_date = datetime.now().strftime("%Y-%m-%d")
        version_tag = config.get("version", "vX")
        sanitized_model = model_name_cfg.replace("models/", "").replace("gemini-", "").replace("preview", "").strip("-")
        filename = f"detections-{version_tag}-{sanitized_model}-{current_date}.geojson"
    
    # Versioned Output Directory
    version_out_dir = RESULTS_DIR / config.get("version", "unknown")
    version_out_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = version_out_dir / filename
    meta_file = output_file.with_suffix('.meta.json')
    print(f"Output: {output_file}")
    print(f"Metadata: {meta_file}")
    
    # Load existing results (Resume capability)
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
            features = []

    # Gather tiles
    tiles_to_process = []
    
    # Priority 1: Manual List (e.g. from code call)
    if tile_list:
        tiles_to_process = [t for t in tile_list if t.name not in processed_tiles]
        print(f"Using provided tile list. {len(tiles_to_process)} remaining.")
        
    # Priority 2: Manifest File (Target Set)
    elif manifest_path:
        print(f"Using Manifest: {manifest_path}")
        try:
            with open(manifest_path, 'r') as f:
                target_filenames = json.load(f)
                all_tiles_map = {}
                for map_dir in TILES_DIR.iterdir():
                    if map_dir.is_dir():
                        for t in map_dir.glob("*.png"):
                            all_tiles_map[t.name] = t
                            
                found_count = 0
                for fname in target_filenames:
                    if fname in all_tiles_map and fname not in processed_tiles:
                        tiles_to_process.append(all_tiles_map[fname])
                        found_count += 1
                        
                print(f"Manifest loaded. Found {found_count} of {len(target_filenames)} tiles ({len(tiles_to_process)} remaining to process).")
                
        except Exception as e:
            print(f"Error reading manifest: {e}")
            return
            
    # Priority 3: Scan All (Default)
    else:
        all_tiles = []
        for map_dir in TILES_DIR.iterdir():
            if map_dir.is_dir():
                all_tiles.extend(list(map_dir.glob("*.png")))
        all_tiles = sorted(all_tiles)
        tiles_to_process = [t for t in all_tiles if t.name not in processed_tiles]
        print(f"Scanning all tiles. {len(tiles_to_process)} remaining.")
        
        if TEST_LIMIT and TEST_LIMIT > 0:
            print(f"Applying TEST_LIMIT: {TEST_LIMIT}")
            tiles_to_process = tiles_to_process[:TEST_LIMIT]

    print(f"Processing {len(tiles_to_process)} new tiles...")
    
    if len(tiles_to_process) == 0:
        print("No tiles to process.")
        return

    # --- PARALLEL EXECUTION ---
    # Prepare Arguments
    max_retries = 5
    base_wait = 30
    config_version = config.get("version", "vX")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(
                process_single_tile,
                tile,
                model,
                metadata_tracker,
                results_tracker,
                reference_content,
                base_wait,
                max_retries,
                config_version,
                model_name_cfg
            ): tile.name for tile in tiles_to_process
        }
        
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(tiles_to_process)):
            tile_name = futures[future]
            try:
                new_features = future.result()
                features.extend(new_features)
            except Exception as e:
                print(f"Exception in worker for {tile_name}: {e}")

    # Final Save
    collection = geojson.FeatureCollection(features)
    collection["crs"] = {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::32635"}}
    with open(output_file, "w") as f:
        geojson.dump(collection, f)

    # Add results summary to metadata tracker
    metadata_tracker.update_results_summary(results_tracker.get_summary())

    # Estimate costs
    cost_estimate = estimate_cost(
        usage=metadata_tracker.usage,
        provider=LLMProvider.GEMINI.value,
        model=model_name_cfg
    )

    # Finalise and save metadata
    meta = metadata_tracker.finalise(include_per_item=True)
    meta["cost_estimate"] = cost_estimate

    with open(meta_file, "w") as f:
        json.dump(meta, f, indent=2)

    # Print summary
    print(f"\nFinished. Saved to {output_file}")
    print(f"Metadata saved to {meta_file}")
    print(f"Tiles processed: {meta['execution_stats']['items_processed']}")
    print(f"Total detections: {results_tracker.get_summary()['total_detections']}")
    print(f"Tokens used: {meta['usage_stats']['total_tokens']:,}")
    print(f"Estimated cost: ${cost_estimate['total_cost_usd']:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to JSON prompt config")
    parser.add_argument("--manifest", required=False, help="Path to JSON manifest of target tiles")
    parser.add_argument("--output", required=False, help="Custom output filename (without extension)")
    parser.add_argument("--model", required=False, help="Override model name (e.g. gemini-1.5-flash)")
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel workers")
    args = parser.parse_args()
    
    detect_mounds_versioned(args.config, manifest_path=args.manifest, output_name=args.output, model_override=args.model, workers=args.workers)
