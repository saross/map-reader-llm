"""
Shared pytest fixtures for VLM burial mound detection tests.

Provides common test data and utilities used across test modules.
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import INPUTS_DIR, TILES_DIR, VECTORS_DIR


# =============================================================================
# Path Fixtures
# =============================================================================

@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def inputs_dir() -> Path:
    """Return the inputs directory path."""
    return INPUTS_DIR


@pytest.fixture
def vectors_dir() -> Path:
    """Return the vectors directory path."""
    return VECTORS_DIR


@pytest.fixture
def tiles_dir() -> Path:
    """Return the tiles directory path."""
    return TILES_DIR


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the test fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def configs_dir() -> Path:
    """Return the prompt configs directory path."""
    return PROJECT_ROOT / "prompts" / "configs"


# =============================================================================
# Ground Truth Fixtures
# =============================================================================

@pytest.fixture
def reference_files(vectors_dir: Path) -> list[Path]:
    """Return list of reference GeoJSON files."""
    return list((vectors_dir / "references").glob("reference_*.geojson"))


@pytest.fixture
def tile_selection_metadata(tiles_dir: Path) -> dict:
    """Load tile selection metadata JSON."""
    metadata_path = tiles_dir / "tile_selection_metadata.json"
    with open(metadata_path) as f:
        return json.load(f)


@pytest.fixture
def calibration_tiles(tile_selection_metadata: dict) -> list[dict]:
    """Return calibration tiles from metadata."""
    return tile_selection_metadata.get("calibration", {}).get("tiles", [])


# =============================================================================
# Test Data Fixtures (for integration tests)
# =============================================================================

@pytest.fixture
def empty_gdf() -> gpd.GeoDataFrame:
    """Return an empty GeoDataFrame with expected CRS."""
    return gpd.GeoDataFrame(geometry=[], crs="EPSG:32635")
