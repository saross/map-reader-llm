#!/usr/bin/env python3
"""
Thinking Level Calibration Pilot: Detection Script
===================================================

Description:
    Runs the detection task for the thinking level pilot experiment.
    Tests 3 thinking levels (minimal, low, high) × 10 replications = 30 runs.
    Uses parallel API calls for efficiency with adaptive rate limiting.

    Uses the new google-genai SDK with ThinkingConfig support.

Usage:
    python scripts/run_thinking_pilot_detection.py
    python scripts/run_thinking_pilot_detection.py --dry-run
    python scripts/run_thinking_pilot_detection.py --workers 5
    python scripts/run_thinking_pilot_detection.py --level high --runs 3

Output:
    outputs/results/pilot_thinking-{level}/
        pilot_thinking-{level}_run{01-10}.geojson
        pilot_thinking-{level}_run{01-10}.meta.json

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import sys
import json
import os
import time
import argparse
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, NamedTuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup Project Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

try:
    from google import genai
    from google.genai import types
    from PIL import Image
    from dotenv import load_dotenv
    from tqdm import tqdm
    import rasterio
    import geojson
    from shapely.geometry import box, mapping
except ImportError as e:
    print(f"Error: Missing required package - {e}")
    print("Install with: pip install google-genai pillow python-dotenv tqdm rasterio geojson shapely")
    sys.exit(1)

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

from config import EXAMPLES_DIR, TILE_SIZE

# Configuration
CONFIGS_DIR = BASE_DIR / "prompts" / "configs"
MANIFEST_PATH = BASE_DIR / "inputs" / "tiles" / "calibration_manifest.json"
TILES_DIR = BASE_DIR / "inputs" / "tiles"
OUTPUT_DIR = BASE_DIR / "outputs" / "results"

# Thinking levels to test
THINKING_LEVELS = ["minimal", "low", "high"]
K_RUNS = 10  # Replications per condition

# API settings
MAX_RETRIES = 3
BASE_WAIT = 2.0
RATE_LIMIT_WAIT = 60.0

# Parallelisation settings
DEFAULT_WORKERS = 5
DEFAULT_RPM = 300

# Script version
__version__ = "1.1.0"  # Fixed coordinate conversion to match 4_detect_mounds_batch.py


class RunSpec(NamedTuple):
    """Specification for a single detection run."""

    thinking_level: str
    run_number: int
    output_name: str
    config: Dict


class AdaptiveRateLimiter:
    """
    Thread-safe rate limiter with adaptive backoff.

    Automatically slows down when hitting rate limits.
    """

    def __init__(self, initial_rpm: int = 300, min_rpm: int = 30):
        """
        Initialise adaptive rate limiter.

        Args:
            initial_rpm: Starting requests per minute (default 300 for safety)
            min_rpm: Minimum RPM floor during backoff
        """
        self.current_rpm = initial_rpm
        self.initial_rpm = initial_rpm
        self.min_rpm = min_rpm
        self.min_interval = 60.0 / initial_rpm
        self.last_request_time = 0.0
        self.lock = threading.Lock()
        self.consecutive_successes = 0
        self.backoff_until = 0.0

    def wait(self):
        """Wait if necessary to respect rate limit."""
        with self.lock:
            # Check if we're in backoff period
            now = time.time()
            if now < self.backoff_until:
                sleep_time = self.backoff_until - now
                print(f"  [Rate limiter] Backoff: waiting {sleep_time:.1f}s...")
                time.sleep(sleep_time)
                now = time.time()

            elapsed = now - self.last_request_time
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            self.last_request_time = time.time()

    def report_success(self):
        """Report a successful request - may speed up if stable."""
        with self.lock:
            self.consecutive_successes += 1
            # Gradually recover after 20 consecutive successes
            if self.consecutive_successes >= 20 and self.current_rpm < self.initial_rpm:
                self.current_rpm = min(self.current_rpm * 1.2, self.initial_rpm)
                self.min_interval = 60.0 / self.current_rpm
                self.consecutive_successes = 0
                print(f"  [Rate limiter] Recovering: {self.current_rpm:.0f} RPM")

    def report_rate_limit(self, wait_seconds: float = 60.0):
        """Report a rate limit hit - backs off significantly."""
        with self.lock:
            self.consecutive_successes = 0
            # Reduce RPM by 50%, but not below minimum
            self.current_rpm = max(self.current_rpm * 0.5, self.min_rpm)
            self.min_interval = 60.0 / self.current_rpm
            self.backoff_until = time.time() + wait_seconds
            print(
                f"  [Rate limiter] Backing off: {self.current_rpm:.0f} RPM, "
                f"waiting {wait_seconds}s"
            )

    def report_error(self):
        """Report a non-rate-limit error - minor slowdown."""
        with self.lock:
            self.consecutive_successes = 0
            # Minor reduction for other errors
            self.current_rpm = max(self.current_rpm * 0.9, self.min_rpm)
            self.min_interval = 60.0 / self.current_rpm


def load_config(thinking_level: str) -> Dict:
    """Load the pilot configuration for a specific thinking level."""
    config_path = CONFIGS_DIR / f"pilot_thinking-{thinking_level}.json"
    with open(config_path, "r") as f:
        return json.load(f)


def load_instruction(config: Dict) -> str:
    """Load the system instruction file specified in config."""
    instruction_path = (
        BASE_DIR / "prompts" / "system-instructions" / config["instruction_file"]
    )
    with open(instruction_path, "r") as f:
        return f.read()


def load_manifest() -> List[Dict]:
    """Load the calibration manifest."""
    with open(MANIFEST_PATH, "r") as f:
        return json.load(f)


def build_reference_parts(config: Dict) -> List[types.Part]:
    """
    Build the reference content (examples) as Part objects for the new SDK.

    Returns:
        List of Part objects (alternating text labels and image parts).
    """
    parts = []

    for example in config["examples"]:
        path = EXAMPLES_DIR / example["path"]
        if path.exists():
            # Add text label
            parts.append(types.Part.from_text(text=example["label"]))

            # Add image as bytes
            with open(path, "rb") as f:
                image_bytes = f.read()

            # Determine mime type from extension
            suffix = path.suffix.lower()
            mime_type = "image/png" if suffix == ".png" else "image/jpeg"

            parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
        else:
            print(f"Warning: Example image not found: {path}")

    return parts


def parse_response(response_text: str) -> List[Dict]:
    """
    Parse the model response to extract detections.

    Returns:
        List of detection dictionaries.
    """
    try:
        # Clean up response text
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        result = json.loads(text)

        # Handle both {"detections": [...]} and direct array
        if isinstance(result, dict):
            return result.get("detections", [])
        elif isinstance(result, list):
            return result
        else:
            return []

    except json.JSONDecodeError:
        return []


def convert_detection_to_geo(
    det: Dict,
    transform: rasterio.Affine,
    tile_name: str,
    thinking_level: str,
    run_name: str,
    config_version: str,
    model_name: str,
) -> Dict:
    """
    Convert a raw detection dict to a GeoJSON-ready feature dict.

    Uses the standardised approach from 4_detect_mounds_batch.py:
    - Extracts box_2d [ymin, xmin, ymax, xmax] in normalised 0-1000 coords
    - Converts to pixel coords, then to geospatial coords via rasterio transform
    - Creates bounding box polygon (lower-left corner + size)

    Args:
        det: Raw detection dict from model (with box_2d key)
        transform: Rasterio affine transform for the tile
        tile_name: Source tile filename
        thinking_level: Thinking level used for this detection
        run_name: Run identifier
        config_version: Config version string
        model_name: Model name string

    Returns:
        GeoJSON feature dict with Polygon geometry and properties
    """
    if "box_2d" not in det:
        return None

    # Extract normalised coordinates [ymin, xmin, ymax, xmax] in 0-1000 range
    ymin_n, xmin_n, ymax_n, xmax_n = det["box_2d"]

    # Convert normalised coords to pixel coords
    px_min_x = (xmin_n / 1000.0) * TILE_SIZE
    px_max_x = (xmax_n / 1000.0) * TILE_SIZE
    px_min_y = (ymin_n / 1000.0) * TILE_SIZE
    px_max_y = (ymax_n / 1000.0) * TILE_SIZE

    # Convert pixel coords to geospatial coords using rasterio transform
    geo_x1, geo_y1 = transform * (px_min_x, px_min_y)
    geo_x2, geo_y2 = transform * (px_max_x, px_max_y)

    # Ensure min/max are correct (transform may flip axes)
    min_geo_x = min(geo_x1, geo_x2)
    max_geo_x = max(geo_x1, geo_x2)
    min_geo_y = min(geo_y1, geo_y2)
    max_geo_y = max(geo_y1, geo_y2)

    # Create bounding box polygon (lower-left corner + upper-right corner)
    geom = box(min_geo_x, min_geo_y, max_geo_x, max_geo_y)

    # Build GeoJSON feature
    feature = {
        "type": "Feature",
        "geometry": mapping(geom),
        "properties": {
            "source_tile": tile_name,
            "label": det.get("label", "mound"),
            "subtype": det.get("subtype", "unknown"),
            "confidence": "high",
            "thinking_level": thinking_level,
            "run": run_name,
            "method": config_version,
            "model": model_name,
        },
    }

    return feature


def process_tile(
    tile_path: Path,
    client: genai.Client,
    model_name: str,
    reference_parts: List[types.Part],
    instruction: str,
    thinking_level: str,
    rate_limiter: AdaptiveRateLimiter,
    config: Dict,
    run_name: str,
) -> Tuple[str, List[Dict], Dict]:
    """
    Process a single tile and return detections as GeoJSON features.

    Args:
        tile_path: Path to the tile image.
        client: The genai Client instance.
        model_name: Name of the model to use.
        reference_parts: Pre-built reference example parts.
        instruction: System instruction text.
        thinking_level: Thinking level (minimal, low, high).
        rate_limiter: Rate limiter instance.
        config: Full config dict for parameters.
        run_name: Run identifier for output properties.

    Returns:
        Tuple of (raw_response_text, geojson_features_list, metadata_dict)
    """
    tile_name = tile_path.name
    request_start = datetime.now(timezone.utc)

    # Read rasterio transform for coordinate conversion
    with rasterio.open(tile_path) as src:
        transform = src.transform

    # Read tile image as bytes
    with open(tile_path, "rb") as f:
        tile_bytes = f.read()

    # Build content parts
    parts = []

    # Add instruction
    parts.append(types.Part.from_text(text=instruction))

    # Add reference section header
    parts.append(types.Part.from_text(text="\n## Reference Examples\n"))

    # Add reference examples
    parts.extend(reference_parts)

    # Add target section
    parts.append(types.Part.from_text(text="\n## Target Image\n"))
    parts.append(types.Part.from_text(text="Find all mound symbols in this image:"))

    # Add target tile
    target_part = types.Part.from_bytes(data=tile_bytes, mime_type="image/png")
    parts.append(target_part)

    # Build content object
    content = types.Content(parts=parts)

    # Build generation config with thinking level
    gen_config = types.GenerateContentConfig(
        temperature=config.get("temperature", 1.0),
        max_output_tokens=config.get("max_output_tokens", 8192),
        thinking_config=types.ThinkingConfig(thinking_level=thinking_level),
    )

    for attempt in range(MAX_RETRIES):
        try:
            # Respect rate limit
            rate_limiter.wait()

            response = client.models.generate_content(
                model=model_name, contents=content, config=gen_config
            )

            request_end = datetime.now(timezone.utc)
            response_text = response.text

            # Parse raw detections from model response
            raw_detections = parse_response(response_text)

            # Convert raw detections to GeoJSON features with proper coordinates
            config_version = config.get("version", "pilot_thinking")
            features = []
            for det in raw_detections:
                feature = convert_detection_to_geo(
                    det=det,
                    transform=transform,
                    tile_name=tile_name,
                    thinking_level=thinking_level,
                    run_name=run_name,
                    config_version=config_version,
                    model_name=model_name,
                )
                if feature is not None:
                    features.append(feature)

            # Report success to rate limiter
            rate_limiter.report_success()

            # Build metadata
            metadata = {
                "tile": tile_name,
                "thinking_level": thinking_level,
                "request_start": request_start.isoformat(),
                "request_end": request_end.isoformat(),
                "latency_ms": (request_end - request_start).total_seconds() * 1000,
                "attempt": attempt + 1,
                "success": True,
                "detection_count": len(features),
                "raw_detection_count": len(raw_detections),
            }

            # Add token usage if available
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                metadata["tokens"] = {
                    "prompt": getattr(
                        response.usage_metadata, "prompt_token_count", 0
                    ),
                    "completion": getattr(
                        response.usage_metadata, "candidates_token_count", 0
                    ),
                    "total": getattr(response.usage_metadata, "total_token_count", 0),
                }

                # Enhanced token tracking for latency/cost analysis
                # Note: Gemini uses "thoughts_token_count" (not "thinking_token_count")
                thoughts_tokens = getattr(
                    response.usage_metadata, "thoughts_token_count", None
                )
                if thoughts_tokens is not None:
                    metadata["tokens"]["thoughts"] = thoughts_tokens

                cached_tokens = getattr(
                    response.usage_metadata, "cached_content_token_count", None
                )
                if cached_tokens is not None:
                    metadata["tokens"]["cached"] = cached_tokens

                # Tool use tokens (if using function calling)
                tool_tokens = getattr(
                    response.usage_metadata, "tool_use_prompt_token_count", None
                )
                if tool_tokens is not None:
                    metadata["tokens"]["tool_use"] = tool_tokens

                # Modality breakdown for research analysis
                # Shows token distribution across TEXT, IMAGE, AUDIO, VIDEO, DOCUMENT
                prompt_details = getattr(
                    response.usage_metadata, "prompt_tokens_details", None
                )
                if prompt_details:
                    metadata["tokens"]["prompt_by_modality"] = [
                        {"modality": str(m.modality), "count": m.token_count}
                        for m in prompt_details
                        if hasattr(m, "modality") and hasattr(m, "token_count")
                    ]

                candidates_details = getattr(
                    response.usage_metadata, "candidates_tokens_details", None
                )
                if candidates_details:
                    metadata["tokens"]["completion_by_modality"] = [
                        {"modality": str(m.modality), "count": m.token_count}
                        for m in candidates_details
                        if hasattr(m, "modality") and hasattr(m, "token_count")
                    ]

                cache_details = getattr(
                    response.usage_metadata, "cache_tokens_details", None
                )
                if cache_details:
                    metadata["tokens"]["cached_by_modality"] = [
                        {"modality": str(m.modality), "count": m.token_count}
                        for m in cache_details
                        if hasattr(m, "modality") and hasattr(m, "token_count")
                    ]

            # Add finish reason for completeness analysis
            if hasattr(response, "candidates") and response.candidates:
                finish_reason = response.candidates[0].finish_reason
                metadata["finish_reason"] = str(finish_reason)

            # Add traffic type if available (ON_DEMAND vs PROVISIONED_THROUGHPUT)
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                traffic_type = getattr(
                    response.usage_metadata, "traffic_type", None
                )
                if traffic_type is not None:
                    metadata["traffic_type"] = str(traffic_type)

            return response_text, features, metadata

        except Exception as e:
            error_msg = str(e)

            if (
                "429" in error_msg
                or "quota" in error_msg.lower()
                or "resource" in error_msg.lower()
            ):
                # Rate limit or quota exceeded - back off significantly
                rate_limiter.report_rate_limit(RATE_LIMIT_WAIT)
            else:
                # Other error - minor slowdown and retry
                rate_limiter.report_error()
                wait_time = BASE_WAIT * (2**attempt)
                time.sleep(wait_time)

    # All retries failed
    return (
        "",
        [],
        {
            "tile": tile_name,
            "thinking_level": thinking_level,
            "request_start": request_start.isoformat(),
            "success": False,
            "error": "Max retries exceeded",
        },
    )


def process_tile_wrapper(args: Tuple) -> Tuple[Path, str, List[Dict], Dict]:
    """
    Wrapper for process_tile to use with ThreadPoolExecutor.

    Returns:
        Tuple of (tile_path, raw_response_text, geojson_features_list, metadata_dict)
    """
    (
        tile_path,
        client,
        model_name,
        reference_parts,
        instruction,
        thinking_level,
        rate_limiter,
        config,
        run_name,
    ) = args
    raw_text, features, metadata = process_tile(
        tile_path,
        client,
        model_name,
        reference_parts,
        instruction,
        thinking_level,
        rate_limiter,
        config,
        run_name,
    )
    return tile_path, raw_text, features, metadata


def run_single_detection_run(
    tiles: List[Path],
    client: genai.Client,
    model_name: str,
    reference_parts: List[types.Part],
    instruction: str,
    spec: RunSpec,
    rate_limiter: AdaptiveRateLimiter,
    max_workers: int,
) -> Dict:
    """
    Run a single detection run (all tiles, one thinking level, one replication).

    Returns:
        Dictionary with run results including all detections.
    """
    run_start = datetime.now(timezone.utc)

    results = {
        "run": spec.output_name,
        "thinking_level": spec.thinking_level,
        "run_number": spec.run_number,
        "tiles_processed": 0,
        "tiles_successful": 0,
        "total_detections": 0,
        "detections_by_tile": {},
        "metadata_by_tile": {},
    }

    # Prepare arguments for each tile
    task_args = [
        (
            tile_path,
            client,
            model_name,
            reference_parts,
            instruction,
            spec.thinking_level,
            rate_limiter,
            spec.config,
            spec.output_name,  # run_name for GeoJSON feature properties
        )
        for tile_path in tiles
    ]

    # Process tiles in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_tile_wrapper, args): args[0] for args in task_args
        }

        with tqdm(
            total=len(tiles), desc=f"{spec.output_name}", leave=False
        ) as pbar:
            for future in as_completed(futures):
                tile_path, raw_text, detections, metadata = future.result()
                tile_name = tile_path.stem

                results["tiles_processed"] += 1
                if metadata.get("success", False):
                    results["tiles_successful"] += 1
                    results["total_detections"] += len(detections)

                results["detections_by_tile"][tile_name] = detections
                results["metadata_by_tile"][tile_name] = metadata

                pbar.update(1)

    run_end = datetime.now(timezone.utc)
    results["run_start"] = run_start.isoformat()
    results["run_end"] = run_end.isoformat()
    results["duration_seconds"] = (run_end - run_start).total_seconds()

    return results


def save_run_results(results: Dict, output_dir: Path) -> Tuple[Path, Path]:
    """
    Save run results as GeoJSON and metadata files.

    Features are already GeoJSON-ready (converted in process_tile using the
    standardised approach from 4_detect_mounds_batch.py with proper coordinate
    conversion via rasterio transform).

    Returns:
        Tuple of (geojson_path, meta_path)
    """
    run_name = results["run"]
    thinking_level = results["thinking_level"]

    # Create output directory
    run_output_dir = output_dir / f"pilot_thinking-{thinking_level}"
    run_output_dir.mkdir(parents=True, exist_ok=True)

    # Collect pre-converted GeoJSON features from all tiles
    features = []
    for tile_name, tile_features in results["detections_by_tile"].items():
        features.extend(tile_features)

    # Build GeoJSON FeatureCollection with CRS
    geojson_output = geojson.FeatureCollection(features)
    geojson_output["crs"] = {
        "type": "name",
        "properties": {"name": "urn:ogc:def:crs:EPSG::32635"},
    }

    # Save GeoJSON
    geojson_path = run_output_dir / f"{run_name}.geojson"
    with open(geojson_path, "w") as f:
        geojson.dump(geojson_output, f, indent=2)

    # Aggregate token counts across all tiles for cost estimation
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_thoughts_tokens = 0
    total_cached_tokens = 0
    total_tool_tokens = 0
    for tile_meta in results["metadata_by_tile"].values():
        if "tokens" in tile_meta:
            total_prompt_tokens += tile_meta["tokens"].get("prompt", 0)
            total_completion_tokens += tile_meta["tokens"].get("completion", 0)
            total_thoughts_tokens += tile_meta["tokens"].get("thoughts", 0)
            total_cached_tokens += tile_meta["tokens"].get("cached", 0)
            total_tool_tokens += tile_meta["tokens"].get("tool_use", 0)

    # Estimate cost using Gemini Flash pricing (as of 2026-01)
    # Flash: $0.50/1M input, $3.00/1M output (thoughts tokens billed as output)
    flash_input_rate = 0.50  # USD per 1M tokens
    flash_output_rate = 3.00  # USD per 1M tokens

    input_cost = (total_prompt_tokens / 1_000_000) * flash_input_rate
    output_cost = ((total_completion_tokens + total_thoughts_tokens) / 1_000_000) * flash_output_rate
    total_cost = input_cost + output_cost

    # Build metadata
    meta = {
        "run": run_name,
        "thinking_level": thinking_level,
        "run_number": results["run_number"],
        "run_start": results["run_start"],
        "run_end": results["run_end"],
        "duration_seconds": results["duration_seconds"],
        "tiles_processed": results["tiles_processed"],
        "tiles_successful": results["tiles_successful"],
        "total_detections": results["total_detections"],
        "tokens_aggregated": {
            "prompt": total_prompt_tokens,
            "completion": total_completion_tokens,
            "thoughts": total_thoughts_tokens,
            "cached": total_cached_tokens,
            "tool_use": total_tool_tokens,
            "total": total_prompt_tokens + total_completion_tokens + total_thoughts_tokens,
        },
        "cost_estimate_usd": {
            "input": round(input_cost, 6),
            "output": round(output_cost, 6),
            "total": round(total_cost, 6),
            "pricing_note": "Gemini Flash: $0.50/1M input, $3.00/1M output (thoughts billed as output)",
        },
        "tile_metadata": results["metadata_by_tile"],
    }

    # Save metadata
    meta_path = run_output_dir / f"{run_name}.meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    return geojson_path, meta_path


def load_checkpoint(checkpoint_path: Path) -> set:
    """Load set of completed run names from checkpoint."""
    if checkpoint_path.exists():
        with open(checkpoint_path, "r") as f:
            data = json.load(f)
            return set(data.get("completed", []))
    return set()


def save_checkpoint(
    checkpoint_path: Path, completed: set, failed: List[Dict]
) -> None:
    """Save checkpoint to file."""
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "completed": sorted(completed),
        "failed": failed,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    with open(checkpoint_path, "w") as f:
        json.dump(checkpoint, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Run thinking level pilot detection"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan without executing",
    )
    parser.add_argument(
        "--level",
        type=str,
        default=None,
        choices=THINKING_LEVELS,
        help="Only run for specific thinking level",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=K_RUNS,
        help=f"Number of runs per level (default: {K_RUNS})",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Number of parallel workers (default: {DEFAULT_WORKERS})",
    )
    parser.add_argument(
        "--rpm",
        type=int,
        default=DEFAULT_RPM,
        help=f"Requests per minute limit (default: {DEFAULT_RPM})",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from checkpoint, skipping completed runs",
    )
    args = parser.parse_args()

    print(f"Thinking Level Pilot Detection v{__version__}")
    print("=" * 60)

    # Determine levels to run
    levels = [args.level] if args.level else THINKING_LEVELS

    # Load manifest and discover tiles
    print("Loading calibration manifest...")
    manifest = load_manifest()
    # Manifest is a simple list of filenames
    # Tiles are organised in map subdirectories, extract map name from filename
    # e.g., "K-35-052-4_32635_x1344_y1344.png" -> "K-35-052-4_32635"
    tiles = []
    for filename in manifest:
        # Map name is everything before "_x"
        map_name = filename.rsplit("_x", 1)[0]
        tiles.append(TILES_DIR / map_name / filename)
    print(f"Found {len(tiles)} calibration tiles")

    # Verify tiles exist
    missing = [t for t in tiles if not t.exists()]
    if missing:
        print(f"Error: {len(missing)} tiles not found")
        for m in missing[:5]:
            print(f"  - {m}")
        sys.exit(1)

    # Generate run specifications
    specs = []
    for level in levels:
        config = load_config(level)
        for run_num in range(1, args.runs + 1):
            output_name = f"pilot_thinking-{level}_run{run_num:02d}"
            specs.append(
                RunSpec(
                    thinking_level=level,
                    run_number=run_num,
                    output_name=output_name,
                    config=config,
                )
            )

    print(f"Conditions: {len(levels)} thinking level(s)")
    print(f"Runs per condition: {args.runs}")
    print(f"Total runs: {len(specs)}")
    print(f"API calls per run: {len(tiles)}")
    print(f"Total API calls: {len(specs) * len(tiles)}")
    print(f"Parallel workers: {args.workers}")
    print(f"Rate limit: {args.rpm} RPM")

    if args.dry_run:
        print("\nDry run - run specifications:")
        for spec in specs:
            print(f"  {spec.output_name} (level={spec.thinking_level})")
        print("\nExiting without making API calls")
        return

    # Handle resume
    checkpoint_path = OUTPUT_DIR / "pilot_thinking_checkpoint.json"
    completed = set()
    failed = []

    if args.resume:
        completed = load_checkpoint(checkpoint_path)
        if completed:
            print(f"\nResuming: {len(completed)} runs already completed")

    pending_specs = [s for s in specs if s.output_name not in completed]

    if not pending_specs:
        print("\nAll runs already completed!")
        return

    print(f"Pending runs: {len(pending_specs)}")

    # Confirm before proceeding
    print("\nThis will make API calls. Press Ctrl+C to cancel.")
    time.sleep(3)

    # Configure API
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        sys.exit(1)

    # Create client with v1alpha API for ThinkingConfig support
    client = genai.Client(api_key=api_key, http_options={"api_version": "v1alpha"})

    # Get model name from first config
    model_name = pending_specs[0].config.get("model", "gemini-3-flash-preview")
    print(f"\nModel: {model_name}")
    print("Using v1alpha API for ThinkingConfig support")

    # Create rate limiter
    rate_limiter = AdaptiveRateLimiter(initial_rpm=args.rpm)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Run each spec
    print("\n" + "=" * 60)
    pilot_start = datetime.now(timezone.utc)

    for i, spec in enumerate(pending_specs, 1):
        print(f"\n[{i}/{len(pending_specs)}] Running {spec.output_name}...")

        # Load fresh reference parts for this level (in case config differs)
        reference_parts = build_reference_parts(spec.config)
        instruction = load_instruction(spec.config)

        # Run detection
        results = run_single_detection_run(
            tiles,
            client,
            model_name,
            reference_parts,
            instruction,
            spec,
            rate_limiter,
            args.workers,
        )

        # Save results
        geojson_path, meta_path = save_run_results(results, OUTPUT_DIR)
        print(f"  Saved: {geojson_path.name}")
        print(
            f"  Detections: {results['total_detections']} "
            f"({results['tiles_successful']}/{results['tiles_processed']} tiles)"
        )

        # Update checkpoint
        completed.add(spec.output_name)
        save_checkpoint(checkpoint_path, completed, failed)

    pilot_end = datetime.now(timezone.utc)

    # Summary
    print("\n" + "=" * 60)
    print("Pilot Detection Complete")
    print("=" * 60)
    print(f"Duration: {(pilot_end - pilot_start).total_seconds():.1f}s")
    print(f"Completed: {len(completed)}")
    print(f"Results saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
