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
    python scripts/4_detect_mounds_batch.py --config <config> \
        --manifest <manifest> --output-dir <dir>
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
import random
import time
import argparse
import traceback
from pathlib import Path
from tqdm import tqdm
from google import genai
from google.genai import types
import geojson
from shapely.geometry import box, mapping
import rasterio
import sys
from PIL import Image as PILImage
from datetime import datetime, timezone
import concurrent.futures
import threading

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    GOOGLE_API_KEY, TILES_DIR, RESULTS_DIR, TILE_SIZE,
    TEST_LIMIT, BASE_DIR, EXAMPLES_DIR,
)

# Import comprehensive metadata tracking
from scripts.lib_llm_metadata import (
    LLMMetadataTracker,
    extract_gemini_metadata,
    create_error_metadata,
    estimate_cost,
    LLMProvider
)

# Import proactive token-bucket rate limiter (replaced reactive
# TPMGovernor — see lib_token_bucket.py for design rationale)
from scripts.lib_token_bucket import TokenBucketGovernor


# Script Version
__version__ = "6.0.0"  # TPM governor, jittered backoff, tile manifests, early warnings

# Maximum backoff wait time in seconds (5 minutes) to prevent multi-hour waits
# when exponential backoff grows beyond useful delays.
MAX_BACKOFF_SECONDS = 300

# Consecutive failure counts that trigger progress bar warnings.
# Uses specific thresholds instead of every-iteration warnings to avoid
# flooding the output during sustained outages.
CONSECUTIVE_FAILURE_THRESHOLDS = (5, 10, 20, 30)


def _save_geojson(
    features: list,
    output_file: Path,
    processed_tiles: set | None = None,
) -> None:
    """
    Write features to a GeoJSON FeatureCollection.

    Called incrementally after each tile so that partial results survive
    if the process is killed (e.g. by a SIGKILL timeout). The resume
    logic in detect_mounds_versioned() reads this file on restart and
    skips already-processed tiles.

    Args:
        features: List of GeoJSON Feature dicts.
        output_file: Path to write the FeatureCollection.
        processed_tiles: Optional set of tile filenames that have been
            successfully processed (including those with zero detections).
            Stored as a top-level property so resume can skip them even
            when no features were generated.
    """
    collection = geojson.FeatureCollection(features)
    collection["crs"] = {
        "type": "name",
        "properties": {"name": "urn:ogc:def:crs:EPSG::32635"},
    }
    if processed_tiles is not None:
        collection["processed_tiles"] = sorted(processed_tiles)
    with open(output_file, "w") as f:
        geojson.dump(collection, f)


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
        ordering: Ordering strategy — one of:
            'config-default': Return examples in their JSON config order (no-op).
            'canonical-first': Group all canonical examples first, then hard, then null.
            'canonical-last': Group all canonical examples last, after hard and null.
            'random': Reproducibly shuffle all examples using the given seed.
        seed: Random seed for reproducible ordering when using 'random'.

    Returns:
        Reordered list of examples.

    Example categories expected:
        - canonical_positive, canonical_negative (canonical examples)
        - hard_positive, hard_negative (hard examples)
        - null (null tiles)
    """
    import random as rand_module

    if ordering == "config-default":
        # Return examples in their JSON config file order (no reordering).
        # This is the ordering used in all phases prior to Phase 2e.
        return examples

    elif ordering == "canonical-first":
        # Group all canonical examples first, then hard examples, then null.
        # Within each group, preserve the original config order.
        canonical = [
            e for e in examples
            if e.get("category", "").startswith("canonical")
        ]
        hard = [
            e for e in examples
            if e.get("category", "").startswith("hard")
        ]
        null = [
            e for e in examples
            if e.get("category") == "null"
        ]
        result = canonical + hard + null
        if len(result) != len(examples):
            dropped = len(examples) - len(result)
            raise ValueError(
                f"canonical-first ordering lost {dropped} example(s). "
                f"Check that all examples have a recognised category "
                f"(canonical_*, hard_*, or null)."
            )
        return result

    elif ordering == "canonical-last":
        # Move all canonical examples to the end, after hard and null.
        # Within each group, preserve the original config order.
        canonical = [
            e for e in examples
            if e.get("category", "").startswith("canonical")
        ]
        non_canonical = [
            e for e in examples
            if not e.get("category", "").startswith("canonical")
        ]
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
    governor=None,
    tile_size=TILE_SIZE,
    cache_name=None,
):
    """
    Worker function to process a single tile with comprehensive metadata capture.

    Uses the google-genai SDK for API calls. When a TPMGovernor is provided,
    each API attempt is gated through acquire/release to stay within TPM limits.

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
        governor: Optional TPMGovernor for adaptive concurrency control
        tile_size: Tile dimension in pixels for normalised→pixel coordinate
            conversion (default: TILE_SIZE from config).

    Returns:
        List of GeoJSON features for detected mounds, or None if all
        retries were exhausted (distinguishes failure from zero detections).
    """
    tile_filename = tile_path.name
    features = []

    try:
        # Read tile image as bytes for the new SDK
        with open(tile_path, "rb") as f:
            tile_bytes = f.read()

        # Build content parts using types.Part objects.
        # When a context cache is active, the preamble and examples
        # are already in the cache — only send the transition text
        # and the tile image.
        if cache_name:
            content_parts = [
                types.Part.from_text(
                    text="Now, find detection instances that visually "
                    "match ANY of the above Reference Examples in "
                    "the Target Map Tile below:"
                ),
                types.Part.from_bytes(
                    data=tile_bytes, mime_type="image/png",
                ),
            ]
        else:
            content_parts = [
                types.Part.from_text(
                    text="Here are the Reference Symbols you must find:"
                ),
            ]
            content_parts.extend(reference_parts)
            content_parts.append(
                types.Part.from_text(
                    text="Now, find detection instances that visually "
                    "match ANY of the above Reference Examples in "
                    "the Target Map Tile below:"
                )
            )
            content_parts.append(
                types.Part.from_bytes(
                    data=tile_bytes, mime_type="image/png",
                )
            )

        # Build content object
        content = types.Content(parts=content_parts)

        response = None
        response_metadata = None

        for attempt in range(max_retries):
            request_start = datetime.now(timezone.utc)
            api_start = time.monotonic()
            actual_tokens = 0  # Default for governor release on error
            got_rate_limited = False
            api_latency = None
            # Backoff state — set inside try/except, executed after
            # governor release so 429 signals reach the governor
            # immediately rather than after a 30–300s delay.
            backoff_seconds = 0.0
            is_fatal = False
            should_break = False

            # Gate through TPM governor if available
            if governor:
                governor.acquire()

            try:
                # When using context cache, pass cache_name in config
                # and omit system_instruction (it's in the cache).
                if cache_name:
                    call_config = types.GenerateContentConfig(
                        cached_content=cache_name,
                        temperature=gen_config.temperature,
                        max_output_tokens=gen_config.max_output_tokens,
                        response_mime_type=gen_config.response_mime_type,
                        thinking_config=gen_config.thinking_config,
                        safety_settings=gen_config.safety_settings,
                    )
                else:
                    call_config = gen_config

                response = client.models.generate_content(
                    model=model_name_cfg,
                    contents=content,
                    config=call_config,
                )

                api_latency = time.monotonic() - api_start

                # Report actual tokens to governor
                actual_tokens = getattr(
                    getattr(response, 'usage_metadata', None),
                    'total_token_count', 0
                ) or 0

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
                        # Sleep before continue — the deferred sleep
                        # pattern doesn't work with continue (finally
                        # runs but post-finally code is skipped). This
                        # isn't a 429, so holding the governor slot
                        # during 5s is harmless.
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
                        # Sleep before continue — same rationale as
                        # the MAX_TOKENS case above.
                        time.sleep(5)
                        continue

            except Exception as e:
                # Report zero tokens on error
                actual_tokens = 0
                api_latency = time.monotonic() - api_start

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

                # Categorise and log retry — backoff sleeps are
                # deferred to after governor release
                if "429" in error_str or "ResourceExhausted" in error_str:
                    got_rate_limited = True
                    metadata_tracker.log_retry(
                        tile_filename, attempt + 1, error_str,
                        error_type="rate_limit"
                    )
                    jittered_wait = (
                        base_wait * (2 ** attempt)
                        + random.uniform(0, base_wait)
                    )
                    backoff_seconds = min(
                        jittered_wait, MAX_BACKOFF_SECONDS
                    )
                elif "503" in error_str or "InternalServerError" in error_str:
                    metadata_tracker.log_retry(
                        tile_filename, attempt + 1, error_str,
                        error_type="server_error"
                    )
                    backoff_seconds = 30 + random.uniform(0, 10)
                elif "DeadlineExceeded" in error_str:
                    metadata_tracker.log_retry(
                        tile_filename, attempt + 1, error_str,
                        error_type="timeout"
                    )
                    backoff_seconds = 30 + random.uniform(0, 10)
                elif "404" in error_str and "models/" in error_str:
                    print(
                        f"\n[CRITICAL] Model '{model_name_cfg}' "
                        f"not found. Terminating."
                    )
                    is_fatal = True
                else:
                    metadata_tracker.log_retry(
                        tile_filename, attempt + 1, error_str,
                        error_type="other"
                    )
                    print(f"\n[Error] {tile_filename}: {e}")
                    if attempt < 2:
                        backoff_seconds = 20 + random.uniform(0, 10)
                    else:
                        should_break = True

            finally:
                # Release governor slot BEFORE backoff sleep so the
                # rate-limit signal reaches the governor immediately.
                # Only pass latency for successful requests (non-429,
                # tokens > 0) to avoid polluting the average.
                if governor:
                    governor.release(
                        actual_tokens,
                        was_rate_limited=got_rate_limited,
                        latency_seconds=(
                            api_latency
                            if actual_tokens > 0
                            and not got_rate_limited
                            else None
                        ),
                    )

            # Handle fatal errors and breaks after governor release
            if is_fatal:
                return None
            if should_break:
                break

            # Backoff sleep AFTER governor release — the worker
            # re-acquires at the top of the next iteration. If the
            # governor halved concurrency in response to a 429,
            # the worker may block at acquire(), which is desirable.
            if backoff_seconds > 0:
                time.sleep(backoff_seconds)

        # Check for valid response
        # New SDK uses string finish reasons (e.g., 'STOP')
        valid_response = False
        if response and hasattr(response, 'candidates') and response.candidates:
            reason_str = str(response.candidates[0].finish_reason).upper()
            valid_response = "STOP" in reason_str

        if not valid_response:
            if response_metadata:
                response_metadata.parse_success = False
            metadata_tracker.log_failure(
                tile_filename,
                "Retries Exhausted / Invalid Finish Reason"
            )
            if response_metadata:
                metadata_tracker.log_response(tile_filename, response_metadata)
            return None

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
            metadata_tracker.log_failure(
                tile_filename, f"JSON Parse Error: {e}"
            )
            return None

        with rasterio.open(tile_path) as src:
            transform = src.transform
            _crs = src.crs  # Extracted for potential future use (e.g., multi-CRS support)

        for det in detections:
            if "box_2d" not in det:
                continue
            box_coords = det["box_2d"]
            if not isinstance(box_coords, (list, tuple)) or len(box_coords) != 4:
                print(
                    f"  Skipping detection with malformed box_2d "
                    f"(length={len(box_coords) if isinstance(box_coords, (list, tuple)) else 'N/A'})"
                    f" in {tile_filename}"
                )
                continue
            ymin_n, xmin_n, ymax_n, xmax_n = box_coords
            px_min_x = (xmin_n / 1000.0) * tile_size
            px_max_x = (xmax_n / 1000.0) * tile_size
            px_min_y = (ymin_n / 1000.0) * tile_size
            px_max_y = (ymax_n / 1000.0) * tile_size

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
        traceback.print_exc()
        metadata_tracker.log_failure(tile_filename, str(e))
        return None

def detect_mounds_versioned(
    config_path,
    manifest_path=None,
    tile_list=None,
    output_name=None,
    output_dir=None,
    export_bounds=False,
    model_override=None,
    temperature_override=None,
    thinking_level_override=None,
    ordering_override=None,
    ordering_seed=None,
    workers=1,
    dry_run=False,
    limit=None,
    max_retries=15,
    base_wait=30,
    tile_size=None,
    tiles_dir_override=None,
    use_cache=False,
    service_tier=None,
    skip_intent_check=False,
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
        max_retries (int, optional): Maximum retry attempts per tile. Defaults to 15.
        base_wait (int, optional): Base wait time in seconds for exponential backoff.
            Defaults to 30.
        tile_size (int, optional): Override tile dimension in pixels for normalised→pixel
            coordinate conversion. Defaults to TILE_SIZE from config.
        tiles_dir_override (str, optional): Override tiles directory path. Defaults to
            TILES_DIR from config.

    Returns:
        Dict with items_processed and items_failed counts, or None if
        setup failed before processing could begin.
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

    # Apply Thinking Level Override
    if thinking_level_override is not None:
        print(
            f"Overriding Config Thinking Level "
            f"({config.get('thinking_level', 'not set')}) "
            f"with CLI Argument: {thinking_level_override}"
        )
        config["thinking_level"] = thinking_level_override

    # Resolve effective tile size — CLI override > default from config import
    effective_tile_size = tile_size if tile_size is not None else TILE_SIZE

    # Resolve effective tiles directory — CLI override > default from config import
    effective_tiles_dir = Path(tiles_dir_override) if tiles_dir_override else TILES_DIR

    print(f"Loaded Version: {config.get('version', 'unknown')}")
    print(f"Model: {config.get('model', 'unknown')}")
    print(f"Workers: {workers}")
    if effective_tile_size != TILE_SIZE:
        print(f"Tile size: {effective_tile_size} (overriding config default {TILE_SIZE})")
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
        script_version=__version__,
        model_override=model_name_cfg,
    )

    # Initialise results tracker for detection counts
    results_tracker = ResultsTracker()

    # Build Few-Shot Context from Config using types.Part objects
    examples_dir = EXAMPLES_DIR
    reference_parts = []

    examples = config.get("examples", [])

    # Check whether to include example images (default: True for backward compatibility)
    # Text-only conditions (H1: brief-text, verbose-text) set this to False
    include_example_images = config.get("include_example_images", True)

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

    # Skip example images for text-only conditions
    if not include_example_images:
        print("Text-only modality: skipping example images")
        example_count = 0
    else:
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

    # Log service tier if specified
    if service_tier:
        print(f"Service tier: {service_tier}")

    gen_config_kwargs = {
        "temperature": config.get("temperature", 0.1),
        "max_output_tokens": config.get("max_output_tokens", 8192),
        "response_mime_type": "application/json",
        "thinking_config": thinking_config,
        "system_instruction": system_instruction_text,
        "safety_settings": [
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
    }
    if service_tier is not None:
        gen_config_kwargs["service_tier"] = service_tier
    gen_config = types.GenerateContentConfig(**gen_config_kwargs)

    # ── Context caching (opt-in) ─────────────────────────────────
    # Cache the shared prompt prefix (system instruction + examples)
    # so each tile only sends its unique image. Reduces input costs
    # by ~50-90% depending on example count.
    cache_name = None
    if use_cache:
        cache_parts = [
            types.Part.from_text(
                text="Here are the Reference Symbols you must find:"
            ),
        ]
        cache_parts.extend(reference_parts)

        try:
            config_version_tag = config.get("version", "detect")
            cached_content = client.caches.create(
                model=model_name_cfg,
                config=types.CreateCachedContentConfig(
                    system_instruction=system_instruction_text,
                    contents=[
                        types.Content(parts=cache_parts, role="user"),
                    ],
                    display_name=f"detect-{config_version_tag}",
                    ttl="3600s",
                ),
            )
            cache_name = cached_content.name
            cache_tokens = getattr(
                cached_content, "usage_metadata", None,
            )
            token_count = (
                getattr(cache_tokens, "total_token_count", 0)
                if cache_tokens else 0
            )
            print(
                f"Context cache created: {cache_name} "
                f"({token_count} tokens, TTL=1h)"
            )
        except Exception as e:
            print(f"WARNING: Cache creation failed ({e}), proceeding without cache")
            cache_name = None

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

    # Launch-time experiment-intent guard (Fix #2 + #3 from 2026-04-14
    # Obs 235 retrospective). Writes experiment_intent.md and diffs the
    # variant config against its base, prompting the user to confirm if
    # changed fields are flagged as no-ops under the current modality.
    from lib_experiment_intent import run_launch_checks
    proceed = run_launch_checks(
        config=config,
        config_path=Path(config_path),
        experiment_root=version_out_dir,
        dry_run=dry_run,
        skip_intent_check=skip_intent_check,
    )
    if not proceed:
        print("Aborted by user at launch-time intent check.")
        return None

    output_file = version_out_dir / filename
    meta_file = output_file.with_suffix('.meta.json')
    print(f"Output: {output_file}")
    print(f"Metadata: {meta_file}")

    # Load existing results (Resume capability)
    # Reads any incrementally-saved geojson from a prior (possibly killed)
    # run.  The processed_tiles set tracks ALL successfully-processed tiles
    # including those with zero detections, so they aren't re-queried.
    features = []
    processed_tiles = set()
    if output_file.exists():
        try:
            with open(output_file, 'r') as f:
                data = geojson.load(f)
                features = data.get("features", [])
                # Primary source: explicit list (handles zero-detection tiles)
                if "processed_tiles" in data:
                    processed_tiles = set(data["processed_tiles"])
                # Fallback: scan features (for older output files)
                else:
                    for feat in features:
                        if "source_tile" in feat["properties"]:
                            processed_tiles.add(
                                feat["properties"]["source_tile"]
                            )
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
                for map_dir in effective_tiles_dir.iterdir():
                    if map_dir.is_dir():
                        for t in map_dir.rglob("*.png"):
                            all_tiles_map[t.name] = t

                found_count = 0
                for fname in target_filenames:
                    if fname in all_tiles_map:
                        found_count += 1
                        if fname not in processed_tiles:
                            tiles_to_process.append(all_tiles_map[fname])

                print(
                    f"Manifest loaded. Found {found_count} of "
                    f"{len(target_filenames)} tiles "
                    f"({len(tiles_to_process)} remaining to process)."
                )
                if processed_tiles:
                    print(
                        f"  Resuming: {len(processed_tiles)} tiles "
                        f"already processed."
                    )

        except Exception as e:
            print(f"Error reading manifest: {e}")
            return

    # Priority 3: Scan All (Default)
    else:
        all_tiles = []
        for map_dir in effective_tiles_dir.iterdir():
            if map_dir.is_dir():
                all_tiles.extend(list(map_dir.rglob("*.png")))
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

    # ── Tile-size validation ────────────────────────────────────
    # Verify that the first tile's actual dimensions match the configured
    # tile_size. A mismatch silently corrupts coordinate conversion
    # (e.g., using 512 on 384px tiles produces 300–500m offsets).
    if tiles_to_process:
        _sample = PILImage.open(tiles_to_process[0])
        _actual_w, _actual_h = _sample.size
        _sample.close()
        if _actual_w != effective_tile_size or _actual_h != effective_tile_size:
            print(
                f"\nERROR: Tile dimensions ({_actual_w}×{_actual_h}) do not "
                f"match tile_size ({effective_tile_size}). "
                f"Pass --tile-size {_actual_w} to fix coordinate conversion."
            )
            return None

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
    config_version = config.get("version", "vX")

    # Create token-bucket rate limiter for multi-worker runs.
    # Proactive capacity gating: only dispatches when both RPM and TPM
    # budgets allow. No adaptive concurrency — the bucket IS the throttle.
    include_images = config.get("include_example_images", True)
    tokens_per_request = 20_000 if include_images else 1_500
    governor = None
    if workers > 1:
        governor = TokenBucketGovernor(
            tokens_per_request=tokens_per_request,
        )
        stats = governor.get_stats()
        print(
            f"Token Bucket: target_rpm={stats['target_rpm']}, "
            f"target_tpm={stats['target_tpm']:,}, "
            f"tokens_per_request={tokens_per_request}"
        )

    # Thread pool ceiling matches governor max; the governor semaphore
    # is the actual throttle, not the pool size.
    pool_size = 60 if governor else workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=pool_size) as executor:
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
                governor,
                effective_tile_size,
                cache_name,
            ): tile.name for tile in tiles_to_process
        }

        # Early warning system — track failures during execution
        failure_count = 0
        consecutive_failures = 0

        for future in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(tiles_to_process),
        ):
            tile_name = futures[future]
            try:
                new_features = future.result()
                if new_features is None:
                    # Tile failed (distinct from zero detections)
                    failure_count += 1
                    consecutive_failures += 1
                else:
                    consecutive_failures = 0
                    features.extend(new_features)
                    processed_tiles.add(tile_name)

                    # Incremental save — ensures partial results survive
                    # if the process is killed by a timeout (SIGKILL).
                    _save_geojson(features, output_file, processed_tiles)
            except Exception as e:
                print(f"Exception in worker for {tile_name}: {e}")
                failure_count += 1
                consecutive_failures += 1

            # Early warnings (use tqdm.write to avoid corrupting bar)
            if failure_count == 3:
                tqdm.write(
                    "\nWARNING: 3 tiles have failed. Check API status."
                )
            if failure_count == 10:
                tqdm.write(
                    "\nWARNING: 10 tiles failed. "
                    "Consider stopping (Ctrl+C)."
                )
            if consecutive_failures in CONSECUTIVE_FAILURE_THRESHOLDS:
                tqdm.write(
                    f"\nWARNING: {consecutive_failures} consecutive failures!"
                )

    # Final save (also written incrementally above, but ensures
    # the file reflects the complete run including any late arrivals).
    _save_geojson(features, output_file, processed_tiles)

    # Write tile completion manifest
    manifest_path = output_file.with_suffix('.tiles.json')
    tile_manifest = {
        "total_tiles": len(tiles_to_process),
        "completed": list(metadata_tracker.stats.completed_items),
        "failed": [
            fi["item_id"] for fi in metadata_tracker.stats.failed_items
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(manifest_path, "w") as f:
        json.dump(tile_manifest, f, indent=2)

    # Add results summary to metadata tracker
    metadata_tracker.update_results_summary(results_tracker.get_summary())

    # ── Clean up context cache ─────────────────────────────────
    if cache_name:
        try:
            client.caches.delete(name=cache_name)
            print(f"Context cache deleted: {cache_name}")
        except Exception as e:
            print(f"Cache cleanup failed (will expire via TTL): {e}")

    # Estimate costs
    cost_estimate = estimate_cost(
        usage=metadata_tracker.usage,
        provider=LLMProvider.GEMINI.value,
        model=model_name_cfg
    )

    # Finalise and save metadata — include governor stats if used
    meta = metadata_tracker.finalise(include_per_item=True)
    meta["cost_estimate"] = cost_estimate
    if governor:
        meta["tpm_governor"] = governor.get_stats()

    with open(meta_file, "w") as f:
        json.dump(meta, f, indent=2)

    # Print summary
    print(f"\nFinished. Saved to {output_file}")
    print(f"Tile manifest: {manifest_path}")
    print(f"Metadata saved to {meta_file}")
    print(f"Tiles processed: {meta['execution_stats']['items_processed']}")
    print(f"Tiles failed: {meta['execution_stats']['items_failed']}")
    print(f"Total detections: {results_tracker.get_summary()['total_detections']}")
    print(f"Tokens used: {meta['usage_stats']['total_tokens']:,}")
    print(f"Estimated cost: ${cost_estimate['total_cost_usd']:.4f}")

    return {
        "items_processed": metadata_tracker.stats.items_processed,
        "items_failed": metadata_tracker.stats.items_failed,
    }

def _detect_mounds_batch(args: argparse.Namespace) -> dict | None:
    """
    Run detection via Gemini Batch API (50% cost discount).

    Delegates to ``lib_batch_api.run_batch_unit()`` which handles the
    full lifecycle: JSONL build → upload → submit → poll → retrieve →
    parse → write GeoJSON/meta/tiles outputs.

    The output format (.geojson, .tiles.json, .meta.json) is identical
    to the real-time path, enabling seamless downstream consumption by
    the PV pipeline and evaluation scripts.

    Args:
        args: Parsed CLI arguments (same as real-time mode).

    Returns:
        Dict with items_processed and items_failed counts, or None if
        setup failed before processing could begin.
    """
    from scripts.lib_batch_api import run_batch_unit

    # Load config
    try:
        with open(args.config, "r") as f:
            config_json = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

    # Apply CLI overrides
    if args.temperature is not None:
        config_json["temperature"] = args.temperature
    thinking_level = getattr(args, "thinking_level", None)
    if thinking_level is not None:
        config_json["thinking_level"] = thinking_level
    if args.model:
        config_json["model"] = args.model

    # Resolve effective tile size and tiles directory
    effective_tile_size = (
        args.tile_size if args.tile_size is not None else TILE_SIZE
    )
    effective_tiles_dir = (
        Path(args.tiles_dir) if args.tiles_dir is not None else TILES_DIR
    )

    # Resolve manifest path — use effective_tiles_dir for the default
    # so that --tiles-dir inputs/tiles_384 loads the 384px manifest
    manifest_path = args.manifest or str(
        effective_tiles_dir / "full_evaluation_manifest.json"
    )
    try:
        with open(manifest_path) as f:
            json.load(f)  # Validate manifest is readable
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading manifest {manifest_path}: {e}")
        return None

    # Load system instruction
    instruction_file = config_json.get(
        "instruction_file", "detect_image-only.md"
    )
    prompt_path = (
        Path(BASE_DIR) / "prompts" / "system-instructions" / instruction_file
    )
    try:
        with open(prompt_path, "r") as f:
            system_instruction = f.read()
    except FileNotFoundError:
        print(f"Error: System instruction not found at {prompt_path}")
        return None

    # Resolve model name
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found.")
        return None

    client = genai.Client(
        api_key=GOOGLE_API_KEY,
        http_options={"api_version": "v1alpha"},
    )
    model_name = _resolve_model_name(client, config_json.get("model"))
    if model_name is None:
        return None

    # Resolve output directory
    if getattr(args, "output_dir", None):
        output_dir = Path(args.output_dir)
    else:
        output_dir = RESULTS_DIR / config_json.get("version", "unknown")

    # Launch-time experiment-intent guard (Fix #2 + #3 from 2026-04-14
    # Obs 235 retrospective). Same helper as the realtime path, called
    # once per batch launch before any jobs are submitted.
    output_dir.mkdir(parents=True, exist_ok=True)
    from lib_experiment_intent import run_launch_checks
    proceed = run_launch_checks(
        config=config_json,
        config_path=Path(args.config),
        experiment_root=output_dir,
        dry_run=getattr(args, "dry_run", False),
        skip_intent_check=getattr(args, "skip_intent_check", False),
    )
    if not proceed:
        print("Aborted by user at launch-time intent check.")
        return None

    config_version = config_json.get("version", "unknown")
    examples = config_json.get("examples", [])

    print("Mode: BATCH API (50% cost discount)")
    print(f"Config: {config_version}")
    print(f"Model: {model_name}")
    print(f"System instruction: {instruction_file}")
    print(f"Tile size: {effective_tile_size}")
    print(f"Tiles dir: {effective_tiles_dir}")
    print(f"Manifest: {manifest_path}")
    print(f"Output: {output_dir}")
    if args.dry_run:
        print("Mode: DRY RUN (JSONL built but not submitted)")

    # Construct unit and config dicts for run_batch_unit()
    run_number = getattr(args, "run", 1)
    unit = {
        "condition_name": config_version,
        "run": run_number,
        "config": str(args.config),
        "temperature": config_json.get("temperature"),
        "thinking_level": config_json.get("thinking_level"),
    }
    batch_config = {
        "inputs": {
            "manifest": str(manifest_path),
            "tile_size": effective_tile_size,
            "tiles_dir": str(effective_tiles_dir),
        },
        "_project_root": str(BASE_DIR),
    }

    # Determine tile count for chunking. The Batch API has a 2 GB file
    # upload limit; each tile adds ~320 KB to the JSONL (base64 image +
    # prompt). At 4,000 tiles per chunk the JSONL is ~1.3 GB, safely
    # under the limit.
    from scripts.lib_batch_api import _resolve_tile_paths

    max_batch_tiles = getattr(args, "max_batch_tiles", 4000) or 4000
    all_tile_paths = _resolve_tile_paths(
        Path(manifest_path), tiles_dir=effective_tiles_dir,
    )
    if args.limit and args.limit > 0:
        total_tiles = min(args.limit, len(all_tile_paths))
    else:
        total_tiles = len(all_tile_paths)

    num_chunks = max(1, (total_tiles + max_batch_tiles - 1) // max_batch_tiles)
    needs_chunking = num_chunks > 1

    if needs_chunking:
        print(
            f"Chunking: {total_tiles} tiles into {num_chunks} batch jobs "
            f"(max {max_batch_tiles} per job)"
        )

    # Run batch lifecycle — chunked if needed, single job otherwise
    run_dir = output_dir / config_version / f"run_{run_number}"
    total_cost = 0.0
    total_processed = 0
    total_failed = 0
    chunk_failed = False

    for chunk_idx in range(num_chunks):
        chunk_offset = chunk_idx * max_batch_tiles
        chunk_limit = min(max_batch_tiles, total_tiles - chunk_offset)
        suffix = f"_chunk{chunk_idx}" if needs_chunking else ""

        # Skip chunks whose output already exists (resume support)
        chunk_geojson = run_dir / (
            f"detections_{config_version}_run{run_number:02d}"
            f"{suffix}.geojson"
        )
        if chunk_geojson.exists():
            print(
                f"\n--- Chunk {chunk_idx + 1}/{num_chunks}: "
                f"SKIPPING (output exists: {chunk_geojson.name}) ---"
            )
            # Count existing tiles for summary
            chunk_tiles = chunk_geojson.with_suffix(".tiles.json")
            if chunk_tiles.exists():
                with open(chunk_tiles) as f:
                    td = json.load(f)
                total_processed += len(td.get("completed", []))
                total_failed += len(td.get("failed", []))
            continue

        if needs_chunking:
            print(
                f"\n--- Chunk {chunk_idx + 1}/{num_chunks} "
                f"(tiles {chunk_offset + 1}–{chunk_offset + chunk_limit}) ---"
            )

        success, message, cost_usd = run_batch_unit(
            unit=unit,
            config=batch_config,
            output_dir=output_dir,
            client=client,
            model_name=model_name,
            system_instruction=system_instruction,
            examples=examples,
            config_version=config_version,
            limit=chunk_limit,
            offset=chunk_offset,
            dry_run=args.dry_run,
            tile_size=effective_tile_size,
            tiles_dir=effective_tiles_dir,
            output_name_suffix=suffix,
        )

        total_cost += cost_usd

        if not success:
            print(f"\nBatch chunk {chunk_idx} failed: {message}")
            chunk_failed = True
            continue

        # Count tiles from this chunk's .tiles.json
        chunk_tiles_files = list(run_dir.glob(f"*{suffix}.tiles.json"))
        for tf in chunk_tiles_files:
            with open(tf) as f:
                td = json.load(f)
            total_processed += len(td.get("completed", []))
            total_failed += len(td.get("failed", []))

    # Merge chunk GeoJSONs into a single output if chunked
    if needs_chunking and not args.dry_run:
        chunk_geojsons = sorted(run_dir.glob("*_chunk*.geojson"))
        if chunk_geojsons:
            merged_features = []
            merged_processed = []
            crs_obj = None
            for gj_path in chunk_geojsons:
                with open(gj_path) as f:
                    gj_data = json.load(f)
                merged_features.extend(gj_data.get("features", []))
                merged_processed.extend(
                    gj_data.get("processed_tiles", [])
                )
                if crs_obj is None:
                    crs_obj = gj_data.get("crs")

            merged_output = run_dir / (
                f"detections_{config_version}_run{run_number:02d}.geojson"
            )
            merged_data = {
                "type": "FeatureCollection",
                "features": merged_features,
                "processed_tiles": sorted(set(merged_processed)),
            }
            if crs_obj:
                merged_data["crs"] = crs_obj
            with open(merged_output, "w") as f:
                json.dump(merged_data, f)

            print(
                f"\nMerged {len(chunk_geojsons)} chunks → "
                f"{merged_output.name}: "
                f"{len(merged_features)} features, "
                f"{len(merged_data['processed_tiles'])} tiles"
            )

    if chunk_failed:
        print("\nBatch partially failed (some chunks errored)")
        return {"items_processed": total_processed, "items_failed": total_failed}

    print(f"\nBatch complete. Estimated cost: ${total_cost:.4f}")
    print(f"Tiles processed: {total_processed}")
    if total_failed:
        print(f"Tiles failed: {total_failed}")

    return {"items_processed": total_processed, "items_failed": total_failed}


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
        "--thinking-level", required=False,
        choices=["minimal", "low", "medium", "high"],
        help="Override thinking level from config",
    )
    parser.add_argument(
        "--ordering", required=False,
        choices=["config-default", "canonical-first", "canonical-last", "random"],
        help="Override example ordering (config-default, canonical-first, canonical-last, random)",
    )
    parser.add_argument(
        "--ordering-seed", type=int, required=False,
        help="Random seed for reproducible ordering when using --ordering random",
    )
    parser.add_argument(
        "--workers", type=int, default=12,
        help="Enable rate-limited parallel execution (default: 12). "
        "Values > 1 activate the token-bucket governor, which paces "
        "requests within RPM/TPM API limits. The pool ceiling is 60 "
        "threads; the capacity budget is the actual throttle."
    )
    parser.add_argument(
        "--max-retries", type=int, default=15,
        help="Maximum retry attempts per tile (default: 15)",
    )
    parser.add_argument(
        "--base-wait", type=int, default=30,
        help="Base wait time in seconds for exponential backoff (default: 30)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Validate config without making API calls",
    )
    parser.add_argument("--limit", type=int, help="Process only first N tiles")
    parser.add_argument(
        "--use-cache", action="store_true",
        help=(
            "Enable Gemini context caching. Caches the shared prompt "
            "prefix (system instruction + examples) to reduce input "
            "costs by ~50-90%%. Real-time API only."
        ),
    )
    parser.add_argument(
        "--tile-size", type=int, default=None,
        help=f"Override tile size for coordinate conversion (default: {TILE_SIZE} from config). "
        "Must match the actual tile dimensions being processed.",
    )
    parser.add_argument(
        "--tiles-dir", type=str, default=None,
        help="Override tiles directory (default: from config.py). "
        "Use when processing tiles at a non-standard size (e.g., inputs/tiles_384).",
    )
    parser.add_argument(
        "--mode", choices=["realtime", "batch"], default="realtime",
        help="Execution mode. 'batch' uses Gemini Batch API "
        "(50%% discount, asynchronous). Default: realtime.",
    )
    parser.add_argument(
        "--run", type=int, default=1,
        help="Run number for batch mode (used in output path: "
        "{output-dir}/{version}/run_{N}/). Default: 1.",
    )
    parser.add_argument(
        "--max-batch-tiles", type=int, default=4000,
        dest="max_batch_tiles",
        help="Maximum tiles per batch job. The Batch API has a 2 GB "
        "file upload limit; each tile adds ~320 KB to the JSONL. "
        "When the total tile count exceeds this, the work is "
        "automatically split into multiple batch jobs and merged. "
        "Default: 4000 (~1.3 GB per job).",
    )
    parser.add_argument(
        "--service-tier",
        choices=["standard", "flex"],
        default="flex",
        dest="service_tier",
        help="Service tier for real-time API calls. 'flex' gives 50%% "
        "discount with 1-15 min latency (uses off-peak capacity). "
        "Ignored in batch mode. Default: flex.",
    )
    parser.add_argument(
        "--skip-intent-check",
        action="store_true",
        help=(
            "Bypass the launch-time experiment-intent confirmation "
            "prompt. Use in automation. Not recommended for "
            "interactive runs; see "
            "scripts/lib_experiment_intent.py and Obs 235 retrospective "
            "for context."
        ),
    )
    args = parser.parse_args()

    if args.mode == "batch":
        result = _detect_mounds_batch(args)
    else:
        result = detect_mounds_versioned(
            args.config,
            manifest_path=args.manifest,
            output_name=args.output,
            output_dir=getattr(args, 'output_dir', None),
            model_override=args.model,
            temperature_override=args.temperature,
            thinking_level_override=getattr(args, 'thinking_level', None),
            ordering_override=args.ordering,
            ordering_seed=getattr(args, 'ordering_seed', None),
            workers=args.workers,
            dry_run=args.dry_run,
            limit=args.limit,
            max_retries=args.max_retries,
            base_wait=args.base_wait,
            tile_size=args.tile_size,
            tiles_dir_override=args.tiles_dir,
            use_cache=args.use_cache,
            service_tier=args.service_tier,
            skip_intent_check=args.skip_intent_check,
        )

    # Exit code: 0 = success, 1 = setup error, 2 = partial failure
    if result is None:
        sys.exit(1)
    elif result["items_failed"] > 0:
        sys.exit(2)
    else:
        sys.exit(0)
