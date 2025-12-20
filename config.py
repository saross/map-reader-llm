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
REFERENCES_DIR = INPUTS_DIR / "references"

OUTPUTS_DIR = BASE_DIR / "outputs"

# Ensure directories exist
OUTPUTS_DIR.mkdir(exist_ok=True)
RESULTS_DIR = OUTPUTS_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Tiling settings
TILE_SIZE = 512
OVERLAP = 64  # Overlap in pixels. 20-30px mounds -> 64px is safe.

# Grid Settings (v4.7)
GRID_METERS = 100
PIXEL_RESOLUTION = 5.02 # Meters per pixel
GRID_SPACING_PX = int(GRID_METERS / PIXEL_RESOLUTION) # ~20 px
GRID_COLOR = (0, 255, 255, 128) # Cyan, 50% Alpha

# Gemini Settings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-3-pro-preview" # STRICT REQUIREMENT: Gemini 3 Pro ONLY
TEST_LIMIT = 0 # 0 = Process ALL tiles (Full Run)
