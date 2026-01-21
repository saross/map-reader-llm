import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
INPUTS_DIR = BASE_DIR / "inputs"
RASTERS_DIR = INPUTS_DIR / "rasters"
VECTORS_DIR = INPUTS_DIR / "vectors"
TILES_DIR = INPUTS_DIR / "tiles"

# =============================================================================
# EXAMPLE IMAGES CONFIGURATION
# =============================================================================
#
# Example images for few-shot prompts. Supports two naming modes:
#   - "neutral": Uses neutral-naming/ with example_01.png, example_02.png, etc.
#                Prevents semantic leakage in image-only experiments.
#   - "descriptive": Uses legend-positive/, legend-negative/, null-tiles/
#                    with descriptive names like burial_mound.png
#
# The naming mode affects which subdirectory is used when resolving paths
# from config JSON files. Config paths like "neutral-naming/example_01.png" or
# "legend-positive/burial_mound.png" are resolved relative to EXAMPLES_DIR.
# =============================================================================

EXAMPLES_DIR = INPUTS_DIR / "examples"

# Backwards compatibility alias (deprecated - use EXAMPLES_DIR)
REFERENCES_DIR = EXAMPLES_DIR

OUTPUTS_DIR = BASE_DIR / "outputs"

# Ensure directories exist
OUTPUTS_DIR.mkdir(exist_ok=True)
RESULTS_DIR = OUTPUTS_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# =============================================================================
# TILE CONFIGURATION
# =============================================================================
#
# Tile Generation (preprocess_tiling.py):
#   - Source: High-resolution GeoTIFF maps (~5.02 m/pixel)
#   - Output: TILE_SIZE × TILE_SIZE PNG tiles with OVERLAP pixels of overlap
#   - Naming: {map_name}_x{origin_x}_y{origin_y}.png
#   - Coordinates: Pixel coordinates of tile origin (top-left corner)
#
# Key Relationships:
#   - TILE_SIZE: Actual tile dimensions (default 512px)
#   - OVERLAP: Overlap ensures features at edges aren't clipped (default 64px)
#   - STRIDE: Distance between tile origins = TILE_SIZE - OVERLAP (default 448px)
#   - Tile origin coordinates are always multiples of STRIDE (0, 448, 896, ...)
#
# Spatial Calculations:
#   - Grid position: tile_coords // STRIDE (not TILE_SIZE!)
#   - Geographic extent: tile_coords + TILE_SIZE (actual dimensions)
#
# These parameters are configurable to support experiments with different
# tile sizes and overlap configurations.
# =============================================================================

# Core tiling parameters
TILE_SIZE = 512  # Actual tile dimensions in pixels (512×512)
OVERLAP = 64     # Overlap in pixels. 20-30px mounds -> 64px is safe.
STRIDE = TILE_SIZE - OVERLAP  # Distance between tile origins (448px)

# Tile selection parameters
MAX_BACKGROUND_PERCENT = 0.75  # Tiles must have ≤75% background (black) pixels
ADJACENCY_DISTANCE = 1         # Spatial separation in grid units (Manhattan distance)

# Crop extraction parameters
CONTEXT_SIZE = 512  # Pixel dimensions for context window crops

# Grid Settings (v4.7)
GRID_METERS = 100
PIXEL_RESOLUTION = 5.02 # Meters per pixel
GRID_SPACING_PX = int(GRID_METERS / PIXEL_RESOLUTION) # ~20 px
GRID_COLOR = (0, 255, 255, 128) # Cyan, 50% Alpha

# Gemini Settings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-3-pro-preview" # STRICT REQUIREMENT: Gemini 3 Pro ONLY
TEST_LIMIT = 0 # 0 = Process ALL tiles (Full Run)
