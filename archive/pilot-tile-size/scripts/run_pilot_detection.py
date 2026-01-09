#!/usr/bin/env python3
"""
Tile Size Pilot: Detection Script
=================================

Description:
    Runs the detection task for the tile size pilot experiment.
    Executes 5 passes over all tiles, interleaved by pass to avoid
    systematic effects. Uses parallel API calls for efficiency.

    Uses the new google-genai SDK with media_resolution support.
    For 1024px tiles, uses MEDIA_RESOLUTION_HIGH to prevent internal tiling.

Usage:
    python scripts/run_pilot_detection.py [--passes N] [--dry-run] [--workers N]

Output:
    outputs/pilot/
    ├── 256/
    │   ├── responses/     (raw API responses)
    │   └── detections.json
    ├── 512/
    │   └── ...
    └── 1024/
        └── ...

Author: Shawn Ross, Adela Sobotkova
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
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Setup Project Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

try:
    from google import genai
    from google.genai import types
    from PIL import Image
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Missing required package - {e}")
    print("Install with: pip install google-genai pillow python-dotenv")
    sys.exit(1)

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

from config import EXAMPLES_DIR

# Configuration
PILOT_TILES_DIR = BASE_DIR / "inputs" / "pilot_tiles"
OUTPUT_DIR = BASE_DIR / "outputs" / "pilot"
CONFIG_PATH = BASE_DIR / "prompts" / "configs" / "pilot_tilesize.json"
INSTRUCTION_PATH = BASE_DIR / "prompts" / "system-instructions" / "detect_brief-text-image.md"

# API settings
MAX_RETRIES = 3
BASE_WAIT = 2.0
RATE_LIMIT_WAIT = 60.0

# Parallelisation settings (conservative to avoid TPM limits)
DEFAULT_WORKERS = 5
DEFAULT_RPM = 300  # Conservative: 5 RPS instead of 16

# Script version
__version__ = "2.0.0"  # Updated to use google-genai SDK with media_resolution


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
            print(f"  [Rate limiter] Backing off: {self.current_rpm:.0f} RPM, "
                  f"waiting {wait_seconds}s")

    def report_error(self):
        """Report a non-rate-limit error - minor slowdown."""
        with self.lock:
            self.consecutive_successes = 0
            # Minor reduction for other errors
            self.current_rpm = max(self.current_rpm * 0.9, self.min_rpm)
            self.min_interval = 60.0 / self.current_rpm


def load_config() -> Dict:
    """Load the pilot configuration."""
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)


def load_instruction() -> str:
    """Load the system instruction."""
    with open(INSTRUCTION_PATH, 'r') as f:
        return f.read()


def build_reference_parts(config: Dict) -> List[types.Part]:
    """
    Build the reference content (examples) as Part objects for the new SDK.

    Returns:
        List of Part objects (alternating text labels and image parts).
    """
    parts = []

    for example in config['examples']:
        path = EXAMPLES_DIR / example['path']
        if path.exists():
            # Add text label
            parts.append(types.Part.from_text(text=example['label']))

            # Add image as bytes
            with open(path, 'rb') as f:
                image_bytes = f.read()

            # Determine mime type from extension
            suffix = path.suffix.lower()
            mime_type = 'image/png' if suffix == '.png' else 'image/jpeg'

            parts.append(types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            ))
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
            return result.get('detections', [])
        elif isinstance(result, list):
            return result
        else:
            return []

    except json.JSONDecodeError:
        return []


def process_tile(
    tile_path: Path,
    client: genai.Client,
    model_name: str,
    reference_parts: List[types.Part],
    instruction: str,
    tile_size: int,
    rate_limiter: AdaptiveRateLimiter
) -> Tuple[str, List[Dict], Dict]:
    """
    Process a single tile and return detections.

    Args:
        tile_path: Path to the tile image.
        client: The genai Client instance.
        model_name: Name of the model to use.
        reference_parts: Pre-built reference example parts.
        instruction: System instruction text.
        tile_size: Size of tile in pixels (used to set media_resolution).
        rate_limiter: Rate limiter instance.

    Returns:
        Tuple of (raw_response_text, detections_list, metadata_dict)
    """
    tile_name = tile_path.name
    request_start = datetime.now(timezone.utc)

    # Read tile image as bytes
    with open(tile_path, 'rb') as f:
        tile_bytes = f.read()

    # Build content parts
    parts = []

    # Add instruction
    parts.append(types.Part.from_text(text=instruction))

    # Add reference section header
    parts.append(types.Part.from_text(text="\n## Reference Examples\n"))

    # Add reference examples (without media_resolution - they're small legend images)
    parts.extend(reference_parts)

    # Add target section
    parts.append(types.Part.from_text(text="\n## Target Image\n"))
    parts.append(types.Part.from_text(text="Find all mound symbols in this image:"))

    # Add target tile with media_resolution for 1024px tiles
    if tile_size >= 1024:
        # Use MEDIA_RESOLUTION_HIGH to prevent internal tiling
        target_part = types.Part.from_bytes(
            data=tile_bytes,
            mime_type='image/png',
            media_resolution=types.MediaResolution.MEDIA_RESOLUTION_HIGH
        )
    else:
        # Default resolution for smaller tiles
        target_part = types.Part.from_bytes(
            data=tile_bytes,
            mime_type='image/png'
        )

    parts.append(target_part)

    # Build content object
    content = types.Content(parts=parts)

    for attempt in range(MAX_RETRIES):
        try:
            # Respect rate limit
            rate_limiter.wait()

            response = client.models.generate_content(
                model=model_name,
                contents=content,
                config=types.GenerateContentConfig(
                    temperature=1.0,
                    max_output_tokens=8192
                )
            )

            request_end = datetime.now(timezone.utc)
            response_text = response.text

            # Parse detections
            detections = parse_response(response_text)

            # Report success to rate limiter
            rate_limiter.report_success()

            # Build metadata
            metadata = {
                'tile': tile_name,
                'request_start': request_start.isoformat(),
                'request_end': request_end.isoformat(),
                'latency_ms': (request_end - request_start).total_seconds() * 1000,
                'attempt': attempt + 1,
                'success': True,
                'detection_count': len(detections),
                'media_resolution': 'high' if tile_size >= 1024 else 'default'
            }

            # Add token usage if available
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                metadata['tokens'] = {
                    'prompt': getattr(response.usage_metadata, 'prompt_token_count', 0),
                    'completion': getattr(response.usage_metadata, 'candidates_token_count', 0),
                    'total': getattr(response.usage_metadata, 'total_token_count', 0)
                }

            return response_text, detections, metadata

        except Exception as e:
            error_msg = str(e)

            if "429" in error_msg or "quota" in error_msg.lower() or "resource" in error_msg.lower():
                # Rate limit or quota exceeded - back off significantly
                rate_limiter.report_rate_limit(RATE_LIMIT_WAIT)
            else:
                # Other error - minor slowdown and retry
                rate_limiter.report_error()
                wait_time = BASE_WAIT * (2 ** attempt)
                time.sleep(wait_time)

    # All retries failed
    return "", [], {
        'tile': tile_name,
        'request_start': request_start.isoformat(),
        'success': False,
        'error': 'Max retries exceeded'
    }


def process_tile_wrapper(args: Tuple) -> Tuple[Path, str, List[Dict], Dict]:
    """
    Wrapper for process_tile to use with ThreadPoolExecutor.

    Returns:
        Tuple of (tile_path, raw_response_text, detections_list, metadata_dict)
    """
    tile_path, client, model_name, reference_parts, instruction, tile_size, rate_limiter = args
    raw_text, detections, metadata = process_tile(
        tile_path, client, model_name, reference_parts, instruction, tile_size, rate_limiter
    )
    return tile_path, raw_text, detections, metadata


def run_detection_pass_parallel(
    tiles: List[Path],
    client: genai.Client,
    model_name: str,
    reference_parts: List[types.Part],
    instruction: str,
    pass_num: int,
    tile_size: int,
    output_dir: Path,
    rate_limiter: AdaptiveRateLimiter,
    max_workers: int
) -> Dict:
    """
    Run a single detection pass over all tiles using parallel workers.

    Returns:
        Dictionary with pass results.
    """
    responses_dir = output_dir / str(tile_size) / "responses"
    responses_dir.mkdir(parents=True, exist_ok=True)

    pass_results = {
        'pass': pass_num,
        'tile_size': tile_size,
        'tiles_processed': 0,
        'tiles_successful': 0,
        'total_detections': 0,
        'detections': {}
    }

    # Prepare arguments for each tile
    task_args = [
        (tile_path, client, model_name, reference_parts, instruction, tile_size, rate_limiter)
        for tile_path in tiles
    ]

    # Process tiles in parallel with progress bar
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_tile_wrapper, args): args[0]
            for args in task_args
        }

        with tqdm(total=len(tiles), desc=f"Pass {pass_num}, {tile_size}px") as pbar:
            for future in as_completed(futures):
                tile_path, raw_text, detections, metadata = future.result()
                tile_name = tile_path.stem

                # Save raw response
                response_file = responses_dir / f"{tile_name}_pass{pass_num}.json"
                with open(response_file, 'w') as f:
                    json.dump({
                        'raw_response': raw_text,
                        'detections': detections,
                        'metadata': metadata
                    }, f, indent=2)

                pass_results['tiles_processed'] += 1
                if metadata.get('success', False):
                    pass_results['tiles_successful'] += 1
                    pass_results['total_detections'] += len(detections)

                pass_results['detections'][tile_name] = {
                    'pass': pass_num,
                    'detections': detections,
                    'metadata': metadata
                }

                pbar.update(1)

    return pass_results


def main():
    parser = argparse.ArgumentParser(
        description="Run tile size pilot detection"
    )
    parser.add_argument(
        '--passes', type=int, default=5,
        help="Number of passes (default: 5)"
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help="Print plan without executing"
    )
    parser.add_argument(
        '--size', type=int, default=None,
        help="Only run for specific tile size (256, 512, or 1024)"
    )
    parser.add_argument(
        '--workers', type=int, default=DEFAULT_WORKERS,
        help=f"Number of parallel workers (default: {DEFAULT_WORKERS})"
    )
    parser.add_argument(
        '--rpm', type=int, default=DEFAULT_RPM,
        help=f"Requests per minute limit (default: {DEFAULT_RPM})"
    )
    args = parser.parse_args()

    print(f"Tile Size Pilot Detection v{__version__}")
    print("=" * 50)

    # Load configuration
    print("Loading configuration...")
    config = load_config()
    instruction = load_instruction()

    # Configure API
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        sys.exit(1)

    # Create client with v1alpha API for media_resolution support
    client = genai.Client(
        api_key=api_key,
        http_options={'api_version': 'v1alpha'}
    )
    model_name = config.get('model', 'gemini-3-flash-preview')
    print(f"Model: {model_name}")
    print("Using v1alpha API for media_resolution support")

    # Build reference content as Part objects
    print("Loading reference examples...")
    reference_parts = build_reference_parts(config)
    print(f"Loaded {len(reference_parts) // 2} examples")

    # Discover tiles
    tile_sizes = [256, 512, 1024] if args.size is None else [args.size]
    tiles_by_size = {}

    for size in tile_sizes:
        size_dir = PILOT_TILES_DIR / str(size)
        tiles = sorted(size_dir.glob("*.png"))
        tiles_by_size[size] = tiles
        print(f"Found {len(tiles)} tiles at {size}px")

    # Calculate total API calls
    total_calls = sum(len(t) for t in tiles_by_size.values()) * args.passes
    print(f"\nTotal API calls: {total_calls}")
    print(f"Parallel workers: {args.workers}")
    print(f"Rate limit: {args.rpm} RPM")

    estimated_time = total_calls / (args.rpm / 60)
    print(f"Estimated time: {estimated_time / 60:.1f} minutes")

    if args.dry_run:
        print("\nDry run - exiting without making API calls")
        return

    # Confirm before proceeding
    print("\nThis will make API calls. Press Ctrl+C to cancel.")
    time.sleep(3)

    # Create rate limiter (client already created above)
    rate_limiter = AdaptiveRateLimiter(initial_rpm=args.rpm)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Run passes
    all_results = {}
    run_start = datetime.now(timezone.utc)

    for pass_num in range(1, args.passes + 1):
        print(f"\n{'=' * 50}")
        print(f"Pass {pass_num} of {args.passes}")
        print(f"{'=' * 50}")

        pass_results_by_size = {}

        for size in tile_sizes:
            tiles = tiles_by_size[size]
            resolution_note = " (media_resolution=HIGH)" if size >= 1024 else ""
            print(f"\nProcessing {len(tiles)} tiles at {size}px{resolution_note}...")

            pass_results = run_detection_pass_parallel(
                tiles, client, model_name, reference_parts, instruction,
                pass_num, size, OUTPUT_DIR, rate_limiter, args.workers
            )
            pass_results_by_size[size] = pass_results

        all_results[f"pass_{pass_num}"] = pass_results_by_size

    run_end = datetime.now(timezone.utc)

    # Save aggregated results per size
    print("\nSaving aggregated results...")
    for size in tile_sizes:
        size_results = {
            'tile_size': size,
            'passes': args.passes,
            'run_start': run_start.isoformat(),
            'run_end': run_end.isoformat(),
            'model': model_name,
            'config_version': config.get('version', 'unknown'),
            'tiles': {}
        }

        # Aggregate across passes
        for pass_num in range(1, args.passes + 1):
            pass_data = all_results[f"pass_{pass_num}"][size]
            for tile_name, tile_data in pass_data['detections'].items():
                if tile_name not in size_results['tiles']:
                    size_results['tiles'][tile_name] = {'passes': {}}
                size_results['tiles'][tile_name]['passes'][pass_num] = tile_data

        # Save
        output_path = OUTPUT_DIR / str(size) / "detections.json"
        with open(output_path, 'w') as f:
            json.dump(size_results, f, indent=2)
        print(f"  Saved {output_path}")

    # Print summary
    print("\n" + "=" * 50)
    print("Detection Complete")
    print("=" * 50)
    print(f"Duration: {(run_end - run_start).total_seconds():.1f}s")

    for size in tile_sizes:
        total_detections = 0
        for pass_num in range(1, args.passes + 1):
            total_detections += all_results[f"pass_{pass_num}"][size]['total_detections']
        print(f"  {size}px: {total_detections} total detections across {args.passes} passes")


if __name__ == "__main__":
    main()
