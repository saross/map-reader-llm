import logging
import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# HTTP REQUEST LOG REDACTION
# =============================================================================
#
# httpx logs every request at INFO ('HTTP Request: GET <url> "HTTP/1.1 200
# OK"'), and most scripts set the root logger to INFO, so every request URL
# lands in run logs that are committed to this public repository. Gemini
# URLs carry pagination cursors (pageToken) and resumable-upload session IDs
# (upload_id) in their query strings. On 2026-10-07 and 2026-10-08 a
# secret scanner flagged the cursors, and an endpoint sent the key as ?key=
# would publish it. The filter below keeps each request line (method, path,
# and status) and replaces only the query string.
#
# Why not raise httpx to WARNING: while a batch job is polled, these lines
# (about one every 30 s) are the only writes to its log, and
# scripts/wait_for_run.py treats an hour without a write as a hang
# (reports/s163-agent-records/run-b-stage2-audit.md). Silencing them would
# make every long batch leg look hung.
#
# The filter sits on the "httpx" logger, so it applies to that logger's
# records wherever the root logger is configured. It is installed on import
# because every script that calls the Gemini API imports this module,
# directly or through scripts/lib_batch_api.py. Committed logs written
# before 2026-10-10 keep their query strings.
# =============================================================================

# A URL's query string: from "?" up to whitespace, a quote, or a fragment.
_URL_QUERY = re.compile(r"(https?://[^\s\"'?#]+)\?[^\s\"'#]*")


class RedactUrlQueryFilter(logging.Filter):
    """Replace the query string of every URL in a log record with ``?<redacted>``.

    The record is formatted first, so this works whatever position the URL
    takes in the record's arguments. A record without a URL query is passed
    through untouched; no record is dropped.

    Example:
        After ``install_http_log_redaction()``, the httpx line
        ``GET https://host/v1/files?pageToken=abc "HTTP/1.1 200 OK"`` is
        logged as ``GET https://host/v1/files?<redacted> "HTTP/1.1 200 OK"``.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Redact URL query strings in ``record`` in place; always keep it."""
        try:
            message = record.getMessage()
        except Exception:  # a malformed record: leave it for logging to report
            return True
        redacted = _URL_QUERY.sub(r"\1?<redacted>", message)
        if redacted != message:
            # The message is now final text, so drop the arguments: with
            # args None, getMessage() returns msg without %-formatting.
            record.msg, record.args = redacted, None
        return True


def install_http_log_redaction(logger_names: tuple[str, ...] = ("httpx",)) -> None:
    """Attach one ``RedactUrlQueryFilter`` to each named logger (idempotent).

    Args:
        logger_names: Loggers whose records carry request URLs. httpx is the
            one that logs at INFO; httpcore and urllib3 log URLs only at
            DEBUG and are not covered by default.
    """
    for name in logger_names:
        logger = logging.getLogger(name)
        if not any(isinstance(f, RedactUrlQueryFilter) for f in logger.filters):
            logger.addFilter(RedactUrlQueryFilter())


install_http_log_redaction()

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
