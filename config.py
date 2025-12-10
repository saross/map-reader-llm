import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
INPUTS_DIR = BASE_DIR / "inputs"
OUTPUTS_DIR = BASE_DIR / "outputs"
TILES_DIR = OUTPUTS_DIR / "tiles"

# Ensure directories exist
OUTPUTS_DIR.mkdir(exist_ok=True)
TILES_DIR.mkdir(exist_ok=True)

# Tiling settings
TILE_SIZE = 512
OVERLAP = 64  # Overlap in pixels. 20-30px mounds -> 64px is safe.

# Gemini Settings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-1.5-flash" # Cost effective for high volume
