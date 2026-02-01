"""
Batch Mound Detection Script
============================
Description:
    The core inference engine. Orchestrates the loading of map tiles, construction of
    multimodal prompts (visual + text), and interaction with the Google Gemini API.
    Designed for reproducibility, it uses a versioned configuration system and tracks
    comprehensive metadata (prompt hashes, model versions) for every run.

    Uses the google-genai SDK with ThinkingConfig support for Gemini 3 models.

Usage:
    python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_image-only.json
    python scripts/4_detect_mounds_batch.py --config <config> --manifest <manifest> --output-dir <dir>
    python scripts/4_detect_mounds_batch.py --config <config> --dry-run
    python scripts/4_detect_mounds_batch.py --config <config> --limit 10

Inputs:
    - Tiles from `outputs/tiles/`
    - Prompt Config from `prompts/configs/*.json`
    - System Instructions from `prompts/system-instructions/*.md`

Outputs:
    - Raw GeoJSON detections in `outputs/results/vX.X/`
    - Processing Metadata (.meta.json)

Author: Shawn Ross, Adela Sobotkova
Licence: Apache 2.0
"""

import json
import time
import argparse
from pathlib import Path
from tqdm import tqdm
from google import genai
from google.genai import types
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
__version__ = "5.0.1"  # Add model name resolution for preview-suffix models


def _resolve_model_name(client: genai.Client, model_name: str) -> str | None:
    """
    Resolve a model name to its API-available form.

    Configs use marketing names (e.g., 'gemini-3-flash') matching the preregistration,
    but the API may require a '-preview' suffix until Google promotes the model to
    stable. This function checks availability and falls back to the '-preview' variant.

    Args:
        client: Initialised google-genai Client.
        model_name: Model name from config (e.g., 'gemini-3-flash').

    Returns:
        Resolved model name string, or None if the model cannot be found.
    """
    # Build set of available model names (strip 'models/' prefix for comparison)
    try:
        available = {
            m.name.removeprefix("models/") for m in client.models.list()
        }
    except Exception as e:
        print(f"[Warning] Could not list models: {e}")
        print(f"  Proceeding with '{model_name}' as-is.")
        return model_name

    # Exact match — model name is valid as-is
    if model_name in available:
        return model_name

    # Try with '-preview' suffix
    preview_name = f"{model_name}-preview"
    if preview_name in available:
        print(f"  Model '{model_name}' not found; resolved to '{preview_name}'")
        return preview_name

    # Neither found
    print(f"[CRITICAL] Model '{model_name}' not found in API (also tried '{preview_name}').")
    print("  Available flash/pro models:")
    for m in sorted(available):
        if "flash" in m or "pro" in m:
            print(f"    {m}")
    return None


def reorder_examples(examples: list, ordering: str, seed: int = None) -> list:
    """
    Reorder examples array based on ordering strategy.

    Args:
        examples: List of example dictionaries with 'category' field.
        ordering: Ordering strategy - 'canonical-first', 'canonical-last', or 'random'.
        seed: Random seed for reproducible ordering when using 'random'.

    Returns:
        Reordered list of examples.

    Example categories expected:
        - canonical_positive, canonical_negative (canonical examples)
        - hard_positive, hard_negative (hard examples)
        - null (null tiles)
    """
    import random as rand_module

    if ordering == "canonical-first":
        # Default ordering: canonical examples first, then hard, then null
        # Already the default in most configs, so return as-is
        return examples

    elif ordering == "canonical-last":
        # Move canonical examples to the end
        canonical = [e for e in examples if e.get("category", "").startswith("canonical")]
        non_canonical = [e for e in examples if not e.get("category", "").startswith("canonical")]
        return non_canonical + canonical

    elif ordering == "random":
        # Randomly shuffle all examples
        if seed is not None:
            rand_module.seed(seed)
        shuffled = examples.copy()
        rand_module.shuffle(shuffled)
        return shuffled

    else:
        # Unknown ordering, return unchanged with warning
        print(f"Warning: Unknown ordering '{ordering}', using original order")
        return examples


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
    client,
    model_name_cfg,
    gen_config,
    metadata_tracker,
    results_tracker,
    reference_parts,
    base_wait,
    max_retries,
    config_version,
):
    """
    Worker function to process a single tile with comprehensive metadata capture.

    Uses the google-genai SDK for API calls.

    Args:
        tile_path: Path to the tile image
        client: The genai.Client instance
        model_name_cfg: Model name string (e.g., 'gemini-3-flash')
        gen_config: types.GenerateContentConfig for generation parameters
        metadata_tracker: LLMMetadataTracker for API metadata
        results_tracker: ResultsTracker for detection counts
        reference_parts: List of types.Part objects for reference examples
        base_wait: Base wait time for rate limit retries
        max_retries: Maximum retry attempts
        config_version: Version string from config

    Returns:
        List of GeoJSON features for detected mounds
    """
    tile_filename = tile_path.name
    features = []

    try:
        # Read tile image as bytes for the new SDK
        with open(tile_path, "rb") as f:
            tile_bytes = f.read()

        # Build content parts using types.Part objects
        content_parts = [
            types.Part.from_text(
                text="Here are the Reference Symbols you must find:"
            ),
        ]
        content_parts.extend(reference_parts)
        content_parts.append(
            types.Part.from_text(
                text="Now, find detection instances that visually match ANY of the "
                "above Reference Examples in the Target Map Tile below:"
            )
        )
        content_parts.append(
            types.Part.from_bytes(data=tile_bytes, mime_type="image/png")
        )

        # Build content object
        content = types.Content(parts=content_parts)

        response = None
        response_metadata = None

        for attempt in range(max_retries):
            request_start = datetime.now(timezone.utc)

            try:
                response = client.models.generate_content(
                    model=model_name_cfg,
                    contents=content,
                    config=gen_config,
                )

                # Extract comprehensive metadata from response
                # The new SDK response object has compatible attributes
                response_metadata = extract_gemini_metadata(
                    response=response,
                    request_start=request_start,
                    model_requested=model_name_cfg,
                    item_id=tile_filename,
                    attempt=attempt + 1
                )

                # Check Finish Reason
                # New SDK uses string enum values (e.g., 'STOP', 'MAX_TOKENS')
                if hasattr(response, 'candidates') and response.candidates:
                    reason = response.candidates[0].finish_reason
                    reason_str = str(reason).upper()
                    if "MAX" in reason_str or "TOKEN" in reason_str:
                        metadata_tracker.log_retry(
                            tile_filename,
                            attempt + 1,
                            f"MAX_TOKENS (Finish Reason: {reason})",
                            error_type="other"
                        )
                        time.sleep(5)
                        continue
                    elif "STOP" not in reason_str:
                        pass  # Log but continue

                # Check content validity
                if (
                    response.candidates
                    and response.candidates[0].content
                    and response.candidates[0].content.parts
                ):
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
        # New SDK uses string finish reasons (e.g., 'STOP')
        valid_response = False
        if response and hasattr(response, 'candidates') and response.candidates:
            reason_str = str(response.candidates[0].finish_reason).upper()
            valid_response = "STOP" in reason_str

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
            _crs = src.crs  # Extracted for potential future use (e.g., multi-CRS support)

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
        metadata_tracker.log_failure(tile_filename, str(e))
        return []

def detect_mounds_versioned(
    config_path,
    manifest_path=None,
    tile_list=None,
    output_name=None,
    output_dir=None,
    export_bounds=False,
    model_override=None,
    temperature_override=None,
    ordering_override=None,
    ordering_seed=None,
    workers=1,
    dry_run=False,
    limit=None,
):
    """
    Executes the detection pipeline using a specific versioned configuration.

    Args:
        config_path (str): Path to the JSON configuration file defining the experiment properties.
        manifest_path (str, optional): Path to a JSON list of filenames to process (Target Set).
        tile_list (list, optional): List of specific Path objects to process (Manual override).
        output_name (str, optional): Custom filename for the output GeoJSON.
        output_dir (str, optional): Custom output directory (overrides default versioned directory).
        export_bounds (bool, optional): If True, exports the bounding boxes of processed tiles
            (debug feature).
        model_override (str, optional): Overrides the model defined in the JSON config.
        temperature_override (float, optional): Overrides the temperature defined in the JSON
            config.
        ordering_override (str, optional): Overrides example ordering. Options: 'canonical-first',
            'canonical-last', 'random'. Canonical-first is the default in most configs.
        ordering_seed (int, optional): Random seed for reproducible ordering when using 'random'.
        workers (int, optional): Number of parallel workers. Defaults to 1.
        dry_run (bool, optional): If True, validate config and show what would be processed
            without API calls.
        limit (int, optional): Process only the first N tiles.
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
        print(
            f"Overriding Config Model ({config.get('model')}) "
            f"with CLI Argument: {model_override}"
        )
        config["model"] = model_override

    # Apply Temperature Override
    if temperature_override is not None:
        print(
            f"Overriding Config Temperature ({config.get('temperature', 0.1)}) "
            f"with CLI Argument: {temperature_override}"
        )
        config["temperature"] = temperature_override

    print(f"Loaded Version: {config.get('version', 'unknown')}")
    print(f"Model: {config.get('model', 'unknown')}")
    print(f"Workers: {workers}")
    if dry_run:
        print("Mode: DRY RUN (no API calls)")
    if limit:
        print(f"Limit: {limit} tiles")

    model_name_cfg = config.get("model")

    # Configure Gemini client (new google-genai SDK)
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found.")
        return

    # Use v1alpha API version for ThinkingConfig support
    client = genai.Client(
        api_key=GOOGLE_API_KEY,
        http_options={"api_version": "v1alpha"},
    )

    # Resolve model name — configs use marketing names (e.g., 'gemini-3-flash')
    # but the API may require the '-preview' suffix until the model is promoted
    # to stable. Try the exact name first, then fall back to '-preview'.
    model_name_cfg = _resolve_model_name(client, model_name_cfg)
    if model_name_cfg is None:
        return

    # Load Prompt Text (system instruction)
    instruction_file = config.get("instruction_file", "detect_image-only.md")
    prompt_path = Path(BASE_DIR) / "prompts" / "system-instructions" / instruction_file

    print(f"System Instruction: {instruction_file}")

    try:
        with open(prompt_path, "r") as f:
            system_instruction_text = f.read()
    except FileNotFoundError:
        print(f"Error: Prompt text not found at {prompt_path}")
        return

    # Initialise metadata tracker for comprehensive API logging
    metadata_tracker = LLMMetadataTracker(
        config=config,
        system_instruction=system_instruction_text,
        script_name="4_detect_mounds_batch.py",
        script_version=__version__
    )

    # Initialise results tracker for detection counts
    results_tracker = ResultsTracker()

    # Build Few-Shot Context from Config using types.Part objects
    examples_dir = EXAMPLES_DIR
    reference_parts = []

    examples = config.get("examples", [])

    # Apply Ordering Override
    if ordering_override:
        _original_order = [e.get("path", "") for e in examples]
        examples = reorder_examples(examples, ordering_override, ordering_seed)
        _new_order = [e.get("path", "") for e in examples]
        print(f"Overriding example ordering with: {ordering_override}")
        if ordering_seed is not None:
            print(f"  Random seed: {ordering_seed}")
        # Update config to record the override in metadata
        config["ordering_override"] = ordering_override
        if ordering_seed is not None:
            config["ordering_seed"] = ordering_seed

    example_count = 0
    for ex in examples:
        label = ex.get("label", "Example")
        path_str = ex.get("path", "")
        img_path = examples_dir / path_str

        if img_path.exists():
            # Build Part objects for the new SDK
            reference_parts.append(types.Part.from_text(text=label))
            with open(img_path, "rb") as f:
                image_bytes = f.read()
            suffix = img_path.suffix.lower()
            mime_type = "image/png" if suffix == ".png" else "image/jpeg"
            reference_parts.append(
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            )
            example_count += 1
        else:
            print(f"Warning: Reference image {path_str} not found.")

    # Build generation config with ThinkingConfig support
    thinking_config = None
    if "thinking_level" in config:
        thinking_config = types.ThinkingConfig(
            thinking_level=config["thinking_level"]
        )
        print(f"Thinking level: {config['thinking_level']}")

    gen_config = types.GenerateContentConfig(
        temperature=config.get("temperature", 0.1),
        max_output_tokens=config.get("max_output_tokens", 8192),
        response_mime_type="application/json",
        thinking_config=thinking_config,
        system_instruction=system_instruction_text,
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT", threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
            ),
        ],
    )

    # Output file setup
    if output_name:
        filename = output_name
    else:
        current_date = datetime.now().strftime("%Y-%m-%d")
        version_tag = config.get("version", "vX")
        sanitized_model = (
            model_name_cfg.replace("models/", "")
            .replace("gemini-", "")
            .replace("preview", "")
            .strip("-")
        )
        filename = f"detections-{version_tag}-{sanitized_model}-{current_date}.geojson"

    # Output Directory: CLI override takes precedence
    if output_dir:
        version_out_dir = Path(output_dir)
    else:
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

                print(
                    f"Manifest loaded. Found {found_count} of "
                    f"{len(target_filenames)} tiles "
                    f"({len(tiles_to_process)} remaining to process)."
                )

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

    # Apply CLI limit (overrides TEST_LIMIT)
    if limit and limit > 0:
        print(f"Applying --limit: {limit}")
        tiles_to_process = tiles_to_process[:limit]

    print(f"Processing {len(tiles_to_process)} new tiles...")

    if len(tiles_to_process) == 0:
        print("No tiles to process.")
        return

    # Dry run: show what would be processed and exit
    if dry_run:
        print("\n--- DRY RUN SUMMARY ---")
        print(f"Config: {config_path}")
        print(f"Version: {config.get('version', 'unknown')}")
        print(f"Model: {model_name_cfg}")
        print(f"System instruction: {instruction_file}")
        print(f"Examples loaded: {example_count}")
        print(f"Output directory: {version_out_dir}")
        print(f"Output file: {output_file}")
        print(f"Tiles to process: {len(tiles_to_process)}")
        if len(tiles_to_process) <= 10:
            for t in tiles_to_process:
                print(f"  - {t.name}")
        else:
            for t in tiles_to_process[:5]:
                print(f"  - {t.name}")
            print(f"  ... and {len(tiles_to_process) - 5} more")
        print("\nValidation PASSED. Ready to run without --dry-run.")
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
                client,
                model_name_cfg,
                gen_config,
                metadata_tracker,
                results_tracker,
                reference_parts,
                base_wait,
                max_retries,
                config_version,
            ): tile.name for tile in tiles_to_process
        }

        for future in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(tiles_to_process),
        ):
            tile_name = futures[future]
            try:
                new_features = future.result()
                features.extend(new_features)
            except Exception as e:
                print(f"Exception in worker for {tile_name}: {e}")

    # Final Save
    collection = geojson.FeatureCollection(features)
    collection["crs"] = {
        "type": "name",
        "properties": {"name": "urn:ogc:def:crs:EPSG::32635"},
    }
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
    parser = argparse.ArgumentParser(
        description="Batch mound detection using VLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic detection with config
  python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_image-only.json

  # Detection with manifest and custom output directory
  python scripts/4_detect_mounds_batch.py \\
      --config prompts/configs/library_pure-positive-canon.json \\
      --manifest inputs/tiles/calibration_manifest.json \\
      --output-dir outputs/phase1-library/pass_01

  # Dry run to validate config without API calls
  python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_image-only.json --dry-run

  # Process only first 5 tiles for testing
  python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_image-only.json --limit 5
        """,
    )
    parser.add_argument("--config", required=True, help="Path to JSON prompt config")
    parser.add_argument(
        "--manifest", required=False, help="Path to JSON manifest of target tiles"
    )
    parser.add_argument(
        "--output", required=False,
        help="Custom output filename (without extension)",
    )
    parser.add_argument(
        "--output-dir", required=False,
        help="Custom output directory (overrides versioned dir)",
    )
    parser.add_argument(
        "--model", required=False,
        help="Override model name (e.g. gemini-3-flash)",
    )
    parser.add_argument(
        "--temperature", type=float, required=False,
        help="Override temperature from config (0.0-2.0)",
    )
    parser.add_argument(
        "--ordering", required=False,
        choices=["canonical-first", "canonical-last", "random"],
        help="Override example ordering (canonical-first, canonical-last, random)",
    )
    parser.add_argument(
        "--ordering-seed", type=int, required=False,
        help="Random seed for reproducible ordering when using --ordering random",
    )
    parser.add_argument(
        "--workers", type=int, default=1, help="Number of parallel workers"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Validate config without making API calls",
    )
    parser.add_argument("--limit", type=int, help="Process only first N tiles")
    args = parser.parse_args()

    detect_mounds_versioned(
        args.config,
        manifest_path=args.manifest,
        output_name=args.output,
        output_dir=getattr(args, 'output_dir', None),
        model_override=args.model,
        temperature_override=args.temperature,
        ordering_override=args.ordering,
        ordering_seed=getattr(args, 'ordering_seed', None),
        workers=args.workers,
        dry_run=args.dry_run,
        limit=args.limit,
    )
