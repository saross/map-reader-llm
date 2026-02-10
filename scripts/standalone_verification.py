#!/usr/bin/env python3
"""
Standalone verification of Phase 2c detection pipeline results.

This script independently reimplements prompt construction, API calls,
coordinate transforms, and detection scoring — sharing NO code with the
existing pipeline. It validates whether the directional pattern
(plus-hp > pure-positive-canon > pure-positive-4hp) holds when every
component is written from scratch.

Key independence guarantees:
  - Prompt assembly: built from raw config JSON + image files, not
    from 4_detect_mounds_batch.py
  - Coordinate transform: rasterio affine only, not shared logic
  - GeoJSON loading: json.load() + shapely, not geopandas
  - Spatial scoping: shapely point.within(polygon), not spatial join
  - Detection matching: greedy nearest-neighbour, not Hungarian algorithm
  - F1 computation: inline arithmetic, not lib_advanced_metrics.py

Usage:
    .venv/bin/python3 scripts/standalone_verification.py

Requires:
    google-genai, rasterio, shapely (all in project .venv)
    GOOGLE_API_KEY environment variable set

Output:
    Console: comparison table
    outputs/standalone-verification/results.json: raw results
"""

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. CONFIGURATION — hardcoded paths, tile list, condition list
# ---------------------------------------------------------------------------

# All paths relative to the repository root
REPO_ROOT = Path(__file__).resolve().parent.parent

TILES_DIR = REPO_ROOT / "inputs" / "tiles"
EXAMPLES_DIR = REPO_ROOT / "inputs" / "examples"
CONFIGS_DIR = REPO_ROOT / "prompts" / "configs"
SYSTEM_INSTRUCTION_PATH = (
    REPO_ROOT / "prompts" / "system-instructions" / "detect_brief-text-image.md"
)
REFERENCES_PATH = (
    REPO_ROOT / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
)
BOUNDS_PATH = (
    REPO_ROOT / "inputs" / "vectors" / "bounds" / "validation_bounds.geojson"
)
OUTPUT_DIR_DEFAULT = REPO_ROOT / "outputs" / "standalone-verification"

# Tile size in pixels (all tiles are 512×512)
TILE_PX = 512

# Buffer distance for matching detections to references (metres)
MATCH_BUFFER_M = 20.0

# Default tiles — used when no --tiles JSON is provided
DEFAULT_TILES = [
    # (map_dir, tile_filename, expected_mound_count)
    ("K-35-052-4_32635", "K-35-052-4_32635_x0_y2240.png", 13),
    ("K-35-052-4_32635", "K-35-052-4_32635_x3136_y2240.png", 3),
    ("K-35-053-3_Elenovo", "K-35-053-3_Elenovo_x448_y2688.png", 4),
    ("K-35-053-3_Elenovo", "K-35-053-3_Elenovo_x896_y2240.png", 1),
    ("K-35-053-3_Elenovo", "K-35-053-3_Elenovo_x1792_y448.png", 2),
    ("K-35-062-2_Rakovski", "K-35-062-2_Rakovski_x1792_y0.png", 5),
    ("K-35-062-2_Rakovski", "K-35-062-2_Rakovski_x2688_y1344.png", 5),
    ("K-35-062-2_Rakovski", "K-35-062-2_Rakovski_x3136_y3136.png", 2),
    ("K-35-078-1_Lesovo", "K-35-078-1_Lesovo_x0_y3136.png", 3),
    ("K-35-078-1_Lesovo", "K-35-078-1_Lesovo_x3584_y0.png", 2),
]

# Three conditions to compare
CONDITIONS = [
    "library_pure-positive-canon",
    "library_pure-positive-4hp",
    "library_plus-hp",
]

# Short display labels for conditions
CONDITION_LABELS = {
    "library_pure-positive-canon": "pp-canon",
    "library_pure-positive-4hp": "pp-4hp",
    "library_plus-hp": "plus-hp",
}

# Model configuration — matches library config files
MODEL_NAME = "gemini-3-flash"
API_VERSION = "v1alpha"

# Retry settings for API calls
MAX_RETRIES = 3
RETRY_BASE_DELAY_S = 5.0


def resolve_model_name(client, model_name: str) -> str:
    """
    Resolve a model name, trying '-preview' suffix if exact name unavailable.

    The library configs use marketing names (e.g., 'gemini-3-flash') but the
    API may require a '-preview' suffix until the model is promoted to stable.

    Args:
        client: google.genai.Client instance.
        model_name: Model name from config.

    Returns:
        Resolved model name string.
    """
    try:
        available = {
            m.name.removeprefix("models/") for m in client.models.list()
        }
    except Exception as e:
        print(f"Warning: could not list models ({e}), using '{model_name}' as-is.")
        return model_name

    if model_name in available:
        return model_name

    preview_name = f"{model_name}-preview"
    if preview_name in available:
        print(f"  Resolved '{model_name}' → '{preview_name}'")
        return preview_name

    # Fall back to original name
    print(f"  Warning: '{model_name}' not found in available models, trying anyway.")
    return model_name


def load_system_instruction() -> str:
    """Read system instruction text from the markdown file."""
    with open(SYSTEM_INSTRUCTION_PATH, "r", encoding="utf-8") as f:
        return f.read()


def load_library_config(condition_name: str) -> dict:
    """Read a library configuration JSON file."""
    config_path = CONFIGS_DIR / f"{condition_name}.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# 2. PROMPT CONSTRUCTION — from scratch, no shared code
# ---------------------------------------------------------------------------

def build_content_parts(config: dict, tile_path: Path) -> list:
    """
    Build the content parts list for a Gemini API call.

    Structure:
      1. Preamble text
      2. For each example: label text + image bytes
      3. Transition text
      4. Target tile image bytes

    Args:
        config: Library configuration dict with 'examples' list.
        tile_path: Path to the target tile image.

    Returns:
        List of google.genai.types.Part objects.
    """
    from google.genai import types

    parts = []

    # Preamble
    parts.append(
        types.Part.from_text(
            text="Here are the Reference Symbols you must find:"
        )
    )

    # Example images with labels
    for example in config.get("examples", []):
        label = example.get("label", "Example")
        rel_path = example.get("path", "")
        img_path = EXAMPLES_DIR / rel_path

        if not img_path.exists():
            print(f"  Warning: example image not found: {img_path}")
            continue

        # Label text
        parts.append(types.Part.from_text(text=label))

        # Image bytes
        with open(img_path, "rb") as f:
            image_bytes = f.read()
        parts.append(
            types.Part.from_bytes(data=image_bytes, mime_type="image/png")
        )

    # Transition text
    parts.append(
        types.Part.from_text(
            text=(
                "Now, find detection instances that visually match ANY of "
                "the above Reference Examples in the Target Map Tile below:"
            )
        )
    )

    # Target tile
    with open(tile_path, "rb") as f:
        tile_bytes = f.read()
    parts.append(
        types.Part.from_bytes(data=tile_bytes, mime_type="image/png")
    )

    return parts


def build_generation_config(
    config: dict, system_instruction_text: str
):
    """
    Build the GenerateContentConfig from library config values.

    Args:
        config: Library configuration dict.
        system_instruction_text: System instruction markdown text.

    Returns:
        A GenerateContentConfig instance.
    """
    from google.genai import types

    thinking_config = None
    thinking_level = config.get("thinking_level")
    if thinking_level:
        thinking_config = types.ThinkingConfig(thinking_level=thinking_level)

    return types.GenerateContentConfig(
        temperature=config.get("temperature", 0.0),
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


# ---------------------------------------------------------------------------
# 3. API CALLS — sequential, simple retry
# ---------------------------------------------------------------------------

def call_gemini(client, model_name: str, content_parts: list,
                gen_config) -> str | None:
    """
    Call the Gemini API with retry logic for transient errors.

    Args:
        client: google.genai.Client instance.
        model_name: Model identifier string.
        content_parts: List of Part objects.
        gen_config: GenerateContentConfig instance.

    Returns:
        Raw response text, or None on failure.
    """
    from google.genai import types

    content = types.Content(parts=content_parts)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=content,
                config=gen_config,
            )
            # Extract text from the response
            if response.candidates and response.candidates[0].content:
                text_parts = [
                    p.text
                    for p in response.candidates[0].content.parts
                    if hasattr(p, "text") and p.text
                ]
                return "".join(text_parts) if text_parts else None
            return None

        except Exception as e:
            err_str = str(e)
            # Retry on rate limits and server errors
            if "429" in err_str or "500" in err_str or "503" in err_str:
                delay = RETRY_BASE_DELAY_S * (2 ** (attempt - 1))
                print(f"    Retry {attempt}/{MAX_RETRIES} after {delay}s: {err_str[:80]}")
                time.sleep(delay)
            else:
                print(f"    API error (non-retryable): {err_str[:120]}")
                return None

    print(f"    Exhausted {MAX_RETRIES} retries.")
    return None


# ---------------------------------------------------------------------------
# 4. RESPONSE PARSING — from scratch
# ---------------------------------------------------------------------------

def parse_detections(raw_text: str | None) -> list[dict]:
    """
    Parse model response JSON into a list of detection dicts.

    Handles multiple response formats:
      - {"detections": [...]}
      - [{"detections": [...]}]
      - [{"box_2d": [...], ...}, ...]

    Each returned dict has at minimum a 'box_2d' key with
    [ymin, xmin, ymax, xmax] in normalised 0-1000 coordinates.

    Args:
        raw_text: Raw JSON text from the API response.

    Returns:
        List of detection dicts, possibly empty.
    """
    if not raw_text:
        return []

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        print(f"    Failed to parse JSON: {raw_text[:100]}")
        return []

    # Unwrap outer list if present: [{"detections": [...]}]
    if isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict):
        if "detections" in data[0]:
            data = data[0]

    # Extract detections list
    if isinstance(data, dict) and "detections" in data:
        detections = data["detections"]
    elif isinstance(data, list):
        detections = data
    else:
        print(f"    Unexpected response structure: {str(data)[:100]}")
        return []

    # Validate each detection has box_2d
    valid = []
    for det in detections:
        if isinstance(det, dict) and "box_2d" in det:
            box = det["box_2d"]
            if isinstance(box, list) and len(box) == 4:
                valid.append(det)
    return valid


# ---------------------------------------------------------------------------
# 5. COORDINATE CONVERSION — from scratch using rasterio
# ---------------------------------------------------------------------------

def normalised_to_geographic(
    detections: list[dict], tile_path: Path
) -> list[tuple[float, float]]:
    """
    Convert normalised 0-1000 bounding boxes to EPSG:32635 centroids.

    Steps:
      1. Normalised (0-1000) → pixel coordinates (0-TILE_PX)
      2. Pixel → geographic via rasterio affine transform
      3. Compute centroid as midpoint of transformed bounding box

    Args:
        detections: List of dicts with 'box_2d' [ymin, xmin, ymax, xmax].
        tile_path: Path to the georeferenced tile image.

    Returns:
        List of (easting, northing) tuples in EPSG:32635.
    """
    import rasterio

    with rasterio.open(tile_path) as src:
        transform = src.transform

    centroids = []
    for det in detections:
        ymin_n, xmin_n, ymax_n, xmax_n = det["box_2d"]

        # Step 1: normalised → pixel
        px_xmin = (xmin_n / 1000.0) * TILE_PX
        px_xmax = (xmax_n / 1000.0) * TILE_PX
        px_ymin = (ymin_n / 1000.0) * TILE_PX
        px_ymax = (ymax_n / 1000.0) * TILE_PX

        # Step 2: pixel → geographic (rasterio affine: transform * (col, row))
        geo_x1, geo_y1 = transform * (px_xmin, px_ymin)
        geo_x2, geo_y2 = transform * (px_xmax, px_ymax)

        # Step 3: centroid
        cx = (geo_x1 + geo_x2) / 2.0
        cy = (geo_y1 + geo_y2) / 2.0
        centroids.append((cx, cy))

    return centroids


# ---------------------------------------------------------------------------
# 6. GROUND TRUTH LOADING — from scratch, no geopandas
# ---------------------------------------------------------------------------

def load_reference_mounds() -> list[dict]:
    """
    Load reference mounds from GeoJSON as plain dicts.

    Returns:
        List of feature dicts from the GeoJSON FeatureCollection.
    """
    with open(REFERENCES_PATH, "r", encoding="utf-8") as f:
        geojson = json.load(f)
    return geojson.get("features", [])


def load_validation_bounds() -> list[dict]:
    """
    Load validation tile bounds from GeoJSON as plain dicts.

    Returns:
        List of feature dicts from the GeoJSON FeatureCollection.
    """
    with open(BOUNDS_PATH, "r", encoding="utf-8") as f:
        geojson = json.load(f)
    return geojson.get("features", [])


def get_tile_bounds_polygon(tile_name: str, bounds_features: list[dict]):
    """
    Find the bounds polygon for a specific tile.

    Args:
        tile_name: Tile filename (e.g., 'K-35-052-4_32635_x0_y2240.png').
        bounds_features: List of bounds GeoJSON features.

    Returns:
        A shapely Polygon, or None if not found.
    """
    from shapely.geometry import shape

    for feat in bounds_features:
        props = feat.get("properties", {})
        if props.get("tile_name") == tile_name:
            return shape(feat["geometry"])
    return None


def get_references_in_tile(
    tile_name: str,
    all_references: list[dict],
    bounds_features: list[dict],
) -> list[tuple[float, float]]:
    """
    Get reference mound coordinates that fall within a tile's bounds.

    Uses shapely point-in-polygon test (no geopandas spatial join).

    Args:
        tile_name: Tile filename.
        all_references: All reference mound features.
        bounds_features: All bounds features.

    Returns:
        List of (easting, northing) tuples for references in this tile.
    """
    from shapely.geometry import Point

    bounds_poly = get_tile_bounds_polygon(tile_name, bounds_features)
    if bounds_poly is None:
        print(f"  Warning: no bounds polygon found for {tile_name}")
        return []

    refs_in_tile = []
    for feat in all_references:
        geom = feat.get("geometry", {})
        coords = geom.get("coordinates", [])
        geom_type = geom.get("type", "")

        if geom_type == "MultiPoint":
            # Each coordinate pair in the MultiPoint
            for coord in coords:
                if len(coord) >= 2:
                    pt = Point(coord[0], coord[1])
                    if bounds_poly.contains(pt):
                        refs_in_tile.append((coord[0], coord[1]))
        elif geom_type == "Point":
            if len(coords) >= 2:
                pt = Point(coords[0], coords[1])
                if bounds_poly.contains(pt):
                    refs_in_tile.append((coords[0], coords[1]))

    return refs_in_tile


# ---------------------------------------------------------------------------
# 7. SCORING — greedy nearest-neighbour matching (NOT Hungarian)
# ---------------------------------------------------------------------------

def euclidean_distance(
    p1: tuple[float, float], p2: tuple[float, float]
) -> float:
    """Euclidean distance between two (x, y) points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def greedy_match(
    detections: list[tuple[float, float]],
    references: list[tuple[float, float]],
    buffer_m: float,
) -> dict:
    """
    Greedy nearest-neighbour matching between detections and references.

    Algorithm:
      1. Compute all pairwise distances
      2. Sort by distance (ascending)
      3. Assign closest unmatched pairs, up to buffer_m cutoff
      4. Count TP, FP, FN

    This is deliberately different from the Hungarian algorithm used in
    the main pipeline, to provide an independent verification.

    Args:
        detections: List of (easting, northing) detection centroids.
        references: List of (easting, northing) reference points.
        buffer_m: Maximum match distance in metres.

    Returns:
        Dict with keys 'tp', 'fp', 'fn', 'matched_distances'.
    """
    if not detections and not references:
        return {"tp": 0, "fp": 0, "fn": 0, "matched_distances": []}

    if not detections:
        return {"tp": 0, "fp": 0, "fn": len(references), "matched_distances": []}

    if not references:
        return {"tp": 0, "fp": len(detections), "fn": 0, "matched_distances": []}

    # Compute all pairwise distances
    pairs = []
    for d_idx, det in enumerate(detections):
        for r_idx, ref in enumerate(references):
            dist = euclidean_distance(det, ref)
            pairs.append((dist, d_idx, r_idx))

    # Sort by distance
    pairs.sort(key=lambda x: x[0])

    # Greedy assignment
    matched_det = set()
    matched_ref = set()
    matched_distances = []

    for dist, d_idx, r_idx in pairs:
        if dist > buffer_m:
            break  # All remaining pairs are beyond the buffer
        if d_idx in matched_det or r_idx in matched_ref:
            continue
        matched_det.add(d_idx)
        matched_ref.add(r_idx)
        matched_distances.append(dist)

    tp = len(matched_det)
    fp = len(detections) - tp
    fn = len(references) - len(matched_ref)

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "matched_distances": matched_distances,
    }


def compute_f1(tp: int, fp: int, fn: int) -> dict:
    """
    Compute precision, recall, and F1 from TP/FP/FN counts.

    Args:
        tp: True positives.
        fp: False positives.
        fn: False negatives.

    Returns:
        Dict with 'precision', 'recall', 'f1' (all floats, 0.0 if undefined).
    """
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    return {"precision": precision, "recall": recall, "f1": f1}


# ---------------------------------------------------------------------------
# 8. MAIN — orchestrate everything and output results
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Standalone verification of Phase 2c detection pipeline.",
    )
    parser.add_argument(
        "--tiles", type=Path, default=None,
        help=(
            "Path to a JSON file listing tiles to process. "
            "Format: [[map_dir, tile_filename], ...]. "
            "Reference counts are computed automatically via spatial scoping. "
            "If omitted, uses the built-in default tile list."
        ),
    )
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help=(
            "Directory for results.json output. "
            "Defaults to outputs/standalone-verification/."
        ),
    )
    return parser.parse_args()


def load_tile_list_from_json(
    json_path: Path,
    all_references: list[dict],
    bounds_features: list[dict],
) -> list[tuple[str, str, int]]:
    """
    Load tile list from a JSON file and compute reference counts.

    Args:
        json_path: Path to JSON file with [[map_dir, tile_name], ...].
        all_references: All reference mound features.
        bounds_features: All bounds features.

    Returns:
        List of (map_dir, tile_name, ref_count) tuples.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    tiles = []
    for entry in raw:
        if len(entry) < 2:
            print(f"  Warning: skipping malformed entry: {entry}")
            continue
        map_dir, tile_name = entry[0], entry[1]
        ref_count = len(
            get_references_in_tile(tile_name, all_references, bounds_features)
        )
        tiles.append((map_dir, tile_name, ref_count))

    return tiles


def main():
    """Run the standalone verification."""
    args = parse_args()

    print("=" * 70)
    print("STANDALONE PIPELINE VERIFICATION")
    print("=" * 70)
    print()

    # Load .env file if python-dotenv is available
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
            print(f"Loaded environment from {env_path}")
        except ImportError:
            print("Warning: python-dotenv not installed, relying on shell env.")

    # Check API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        sys.exit(1)

    # Late imports — only standard libs + google-genai, rasterio, shapely
    from google import genai

    # Initialise API client
    client = genai.Client(
        api_key=api_key,
        http_options={"api_version": API_VERSION},
    )

    # Load system instruction
    system_instruction_text = load_system_instruction()
    print(f"System instruction: {len(system_instruction_text)} chars")

    # Load ground truth data
    print("Loading ground truth...")
    all_references = load_reference_mounds()
    bounds_features = load_validation_bounds()
    print(f"  {len(all_references)} reference features loaded")
    print(f"  {len(bounds_features)} tile bounds loaded")

    # Resolve tile list — from JSON file or built-in defaults
    if args.tiles:
        print(f"\nLoading tile list from {args.tiles}...")
        verification_tiles = load_tile_list_from_json(
            args.tiles, all_references, bounds_features
        )
    else:
        verification_tiles = DEFAULT_TILES

    # Resolve output directory
    output_dir = args.output_dir or OUTPUT_DIR_DEFAULT

    # Verify tiles exist
    print("\nVerifying tile paths...")
    for map_dir, tile_name, expected in verification_tiles:
        tile_path = TILES_DIR / map_dir / tile_name
        if not tile_path.exists():
            print(f"  MISSING: {tile_path}")
            sys.exit(1)
        # Verify reference count
        refs = get_references_in_tile(tile_name, all_references, bounds_features)
        status = "OK" if len(refs) == expected else f"MISMATCH (got {len(refs)})"
        print(f"  {tile_name}: {len(refs)} refs ({status})")
    print()

    # Resolve model name (may need '-preview' suffix)
    resolved_model = resolve_model_name(client, MODEL_NAME)
    print(f"Model: {resolved_model}")
    print()

    # Pre-build generation configs for each condition
    configs = {}
    for condition in CONDITIONS:
        lib_config = load_library_config(condition)
        gen_config = build_generation_config(lib_config, system_instruction_text)
        configs[condition] = {
            "lib_config": lib_config,
            "gen_config": gen_config,
        }
        n_examples = len(lib_config.get("examples", []))
        print(f"Condition '{CONDITION_LABELS[condition]}': {n_examples} examples")

    print(f"\nTotal API calls: {len(verification_tiles) * len(CONDITIONS)}")
    print()

    # --------------- Run API calls and score -----------------

    # Results storage: condition → tile → {tp, fp, fn, n_detections, ...}
    results = {c: {} for c in CONDITIONS}

    call_count = 0
    total_calls = len(CONDITIONS) * len(verification_tiles)

    for condition in CONDITIONS:
        label = CONDITION_LABELS[condition]
        lib_config = configs[condition]["lib_config"]
        gen_config = configs[condition]["gen_config"]

        print(f"--- Condition: {label} ---")

        for map_dir, tile_name, _expected in verification_tiles:
            call_count += 1
            tile_path = TILES_DIR / map_dir / tile_name
            print(f"  [{call_count}/{total_calls}] {tile_name}...", end=" ")

            # Build prompt
            content_parts = build_content_parts(lib_config, tile_path)

            # Call API
            raw_response = call_gemini(
                client, resolved_model, content_parts, gen_config
            )

            # Parse response
            detections = parse_detections(raw_response)
            print(f"{len(detections)} detections", end="")

            # Convert to geographic coordinates
            det_centroids = normalised_to_geographic(detections, tile_path)

            # Get references for this tile
            ref_points = get_references_in_tile(
                tile_name, all_references, bounds_features
            )

            # Score with greedy matching
            match_result = greedy_match(det_centroids, ref_points, MATCH_BUFFER_M)
            tp = match_result["tp"]
            fp = match_result["fp"]
            fn = match_result["fn"]
            print(f" → TP={tp} FP={fp} FN={fn}")

            results[condition][tile_name] = {
                "n_detections": len(detections),
                "n_references": len(ref_points),
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "matched_distances": match_result["matched_distances"],
            }

        print()

    # --------------- Output results -----------------

    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()

    # Per-tile breakdown
    tile_names = [t[1] for t in verification_tiles]

    header = f"{'Tile':<20} "
    for condition in CONDITIONS:
        label = CONDITION_LABELS[condition]
        header += f"| {label:^22} "
    print(header)
    print("-" * len(header))

    for tile_name in tile_names:
        # Abbreviated tile name for display
        short = tile_name.replace(".png", "")
        if len(short) > 19:
            short = "..." + short[-16:]
        row = f"{short:<20} "
        for condition in CONDITIONS:
            r = results[condition][tile_name]
            cell = f"TP={r['tp']} FP={r['fp']} FN={r['fn']}"
            row += f"| {cell:^22} "
        print(row)

    print()

    # Per-condition summary
    print(f"{'Condition':<12} | {'TP':>4} {'FP':>4} {'FN':>4} | "
          f"{'Precision':>9} {'Recall':>7} {'F1':>6} | {'Detections':>10}")
    print("-" * 75)

    condition_summaries = {}
    for condition in CONDITIONS:
        label = CONDITION_LABELS[condition]
        total_tp = sum(r["tp"] for r in results[condition].values())
        total_fp = sum(r["fp"] for r in results[condition].values())
        total_fn = sum(r["fn"] for r in results[condition].values())
        total_det = sum(r["n_detections"] for r in results[condition].values())
        metrics = compute_f1(total_tp, total_fp, total_fn)

        condition_summaries[condition] = {
            "label": label,
            "tp": total_tp,
            "fp": total_fp,
            "fn": total_fn,
            "n_detections": total_det,
            **metrics,
        }

        print(
            f"{label:<12} | {total_tp:>4} {total_fp:>4} {total_fn:>4} | "
            f"{metrics['precision']:>9.3f} {metrics['recall']:>7.3f} "
            f"{metrics['f1']:>6.3f} | {total_det:>10}"
        )

    print()

    # Directional comparison
    print("DIRECTIONAL COMPARISON")
    print("-" * 40)

    f1_values = {
        c: condition_summaries[c]["f1"] for c in CONDITIONS
    }

    f1_plus_hp = f1_values["library_plus-hp"]
    f1_pp_canon = f1_values["library_pure-positive-canon"]
    f1_pp_4hp = f1_values["library_pure-positive-4hp"]

    print(f"  plus-hp F1:  {f1_plus_hp:.3f}")
    print(f"  pp-canon F1: {f1_pp_canon:.3f}")
    print(f"  pp-4hp F1:   {f1_pp_4hp:.3f}")
    print()

    pattern_holds = f1_plus_hp > f1_pp_canon > f1_pp_4hp
    if pattern_holds:
        print("  RESULT: Directional pattern CONFIRMED")
        print("  plus-hp > pp-canon > pp-4hp")
    else:
        print("  RESULT: Directional pattern NOT confirmed")
        # Show actual ranking
        ranked = sorted(f1_values.items(), key=lambda x: x[1], reverse=True)
        ranking = " > ".join(
            f"{CONDITION_LABELS[c]} ({v:.3f})" for c, v in ranked
        )
        print(f"  Actual ranking: {ranking}")

    print()

    # --------------- Save raw results -----------------

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "results.json"

    output_data = {
        "metadata": {
            "script": "standalone_verification.py",
            "model": resolved_model,
            "api_version": API_VERSION,
            "match_buffer_m": MATCH_BUFFER_M,
            "matching_algorithm": "greedy_nearest_neighbour",
            "tile_count": len(verification_tiles),
            "conditions": CONDITIONS,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        },
        "tiles": [
            {
                "map_dir": t[0],
                "tile_name": t[1],
                "expected_refs": t[2],
            }
            for t in verification_tiles
        ],
        "per_tile_results": {
            condition: {
                tile: {
                    k: v for k, v in data.items()
                    if k != "matched_distances"
                }
                for tile, data in tiles.items()
            }
            for condition, tiles in results.items()
        },
        "condition_summaries": condition_summaries,
        "directional_pattern_holds": pattern_holds,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    print(f"Raw results saved to: {output_path}")
    print()


if __name__ == "__main__":
    main()
