#!/usr/bin/env python3
"""
Create test fixtures for VLM burial mound detection tests.

This script generates synthetic GeoJSON fixtures for integration testing.
The fixtures have known, predictable F1 scores to enable regression testing.

Fixtures created:
- empty: No references, no detections -> F1=0.0
- sparse: 3 references, 2 detections (1 TP, 1 FP) -> F1=0.5
- dense: 5 references, 4 detections (3 TP, 1 FP) -> known F1

Run once to generate fixtures, then commit them to version control.

Usage:
    python scripts/create_test_fixtures.py
"""

import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import geopandas as gpd
from shapely.geometry import Point, box

FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"
CRS = "EPSG:32635"

# Base coordinates (in UTM metres) for synthetic tiles
# These are arbitrary but consistent with Bulgarian UTM Zone 35N
BASE_X = 400000
BASE_Y = 4700000
TILE_SIZE_M = 2500  # Approximate tile size in metres


def create_bounds_gdf(tile_name: str, map_name: str, x_offset: float = 0) -> gpd.GeoDataFrame:
    """Create a bounds GeoDataFrame for a synthetic tile."""
    minx = BASE_X + x_offset
    miny = BASE_Y
    maxx = minx + TILE_SIZE_M
    maxy = miny + TILE_SIZE_M

    geometry = box(minx, miny, maxx, maxy)
    gdf = gpd.GeoDataFrame(
        {"tile_name": [tile_name], "map_name": [map_name]},
        geometry=[geometry],
        crs=CRS,
    )
    return gdf


def create_detection_gdf(
    detections: list[tuple[float, float]],
    source_tile: str,
) -> gpd.GeoDataFrame:
    """Create a detection GeoDataFrame from coordinate tuples."""
    if not detections:
        return gpd.GeoDataFrame(
            {"source_tile": [], "confidence": [], "subtype": []},
            geometry=[],
            crs=CRS,
        )

    geometries = [Point(x, y) for x, y in detections]
    gdf = gpd.GeoDataFrame(
        {
            "source_tile": [source_tile] * len(detections),
            "confidence": [0.9] * len(detections),
            "subtype": ["burial_mound"] * len(detections),
        },
        geometry=geometries,
        crs=CRS,
    )
    return gdf


def create_reference_gdf(
    references: list[tuple[float, float]],
    map_name: str,
) -> gpd.GeoDataFrame:
    """Create a reference GeoDataFrame from coordinate tuples."""
    if not references:
        return gpd.GeoDataFrame(
            {"fid": [], "Map": [], "Symbol": []},
            geometry=[],
            crs=CRS,
        )

    geometries = [Point(x, y) for x, y in references]
    gdf = gpd.GeoDataFrame(
        {
            "fid": list(range(1, len(references) + 1)),
            "Map": [map_name] * len(references),
            "Symbol": ["Burial mound"] * len(references),
        },
        geometry=geometries,
        crs=CRS,
    )
    return gdf


def calculate_expected_metrics(
    det_coords: list[tuple[float, float]],
    ref_coords: list[tuple[float, float]],
    tolerance: float = 20,
) -> dict:
    """Calculate expected P/R/F1 for given detection and reference coordinates."""
    from scripts.lib_advanced_metrics import match_detections_to_references

    if not det_coords and not ref_coords:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "tp": 0, "fp": 0, "fn": 0}

    det_geoms = [Point(x, y) for x, y in det_coords] if det_coords else []
    ref_geoms = [Point(x, y) for x, y in ref_coords] if ref_coords else []

    matched_det, matched_ref, unmatched_det, unmatched_ref = match_detections_to_references(
        det_geoms, ref_geoms, tolerance
    )

    tp = len(matched_det)
    fp = len(unmatched_det)
    fn = len(unmatched_ref)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }


def create_empty_fixtures() -> None:
    """Create fixtures for an empty tile (no mounds)."""
    tile_name = "TestMap_x0_y0.png"
    map_name = "TestMap"

    # Bounds
    bounds = create_bounds_gdf(tile_name, map_name, x_offset=0)
    bounds.to_file(FIXTURES_DIR / "bounds_empty.geojson", driver="GeoJSON")

    # Empty detections
    detections = create_detection_gdf([], tile_name)
    detections.to_file(FIXTURES_DIR / "detections_empty.geojson", driver="GeoJSON")

    # Empty references (within bounds area)
    references = create_reference_gdf([], map_name)
    references.to_file(FIXTURES_DIR / "references_empty.geojson", driver="GeoJSON")

    print("Created empty fixtures (F1=0.0)")


def create_sparse_fixtures() -> None:
    """Create fixtures for a sparse tile (few mounds, partial detection).

    Scenario: 3 references, 2 detections
    - Detection 1 matches Reference 1 (within 20m)
    - Detection 2 is a false positive (>20m from any reference)
    - References 2 and 3 are missed

    Expected: TP=1, FP=1, FN=2
    Precision = 1/2 = 0.5
    Recall = 1/3 = 0.333
    F1 = 2 * 0.5 * 0.333 / (0.5 + 0.333) = 0.4
    """
    tile_name = "TestMap_x448_y0.png"
    map_name = "TestMap"
    x_offset = 3000  # Offset from empty tile

    # Reference locations
    ref_coords = [
        (BASE_X + x_offset + 500, BASE_Y + 500),   # Ref 1
        (BASE_X + x_offset + 1000, BASE_Y + 1000), # Ref 2
        (BASE_X + x_offset + 1500, BASE_Y + 1500), # Ref 3
    ]

    # Detection locations
    det_coords = [
        (BASE_X + x_offset + 505, BASE_Y + 505),   # Det 1: 7m from Ref 1 (match)
        (BASE_X + x_offset + 2000, BASE_Y + 2000), # Det 2: FP (no nearby ref)
    ]

    # Bounds
    bounds = create_bounds_gdf(tile_name, map_name, x_offset=x_offset)
    bounds.to_file(FIXTURES_DIR / "bounds_sparse.geojson", driver="GeoJSON")

    # Detections
    detections = create_detection_gdf(det_coords, tile_name)
    detections.to_file(FIXTURES_DIR / "detections_sparse.geojson", driver="GeoJSON")

    # References
    references = create_reference_gdf(ref_coords, map_name)
    references.to_file(FIXTURES_DIR / "references_sparse.geojson", driver="GeoJSON")

    # Calculate and save expected metrics
    expected = calculate_expected_metrics(det_coords, ref_coords)
    with open(FIXTURES_DIR / "expected_f1_sparse.json", "w") as f:
        json.dump(expected, f, indent=2)

    print(f"Created sparse fixtures: P={expected['precision']}, R={expected['recall']}, F1={expected['f1']}")


def create_dense_fixtures() -> None:
    """Create fixtures for a dense tile (many mounds, good detection).

    Scenario: 5 references, 4 detections
    - Detections 1-3 match References 1-3 (within 20m)
    - Detection 4 is a false positive
    - References 4-5 are missed

    Expected: TP=3, FP=1, FN=2
    Precision = 3/4 = 0.75
    Recall = 3/5 = 0.6
    F1 = 2 * 0.75 * 0.6 / (0.75 + 0.6) = 0.667
    """
    tile_name = "TestMap_x896_y0.png"
    map_name = "TestMap"
    x_offset = 6000  # Offset from sparse tile

    # Reference locations
    ref_coords = [
        (BASE_X + x_offset + 200, BASE_Y + 200),   # Ref 1
        (BASE_X + x_offset + 400, BASE_Y + 400),   # Ref 2
        (BASE_X + x_offset + 600, BASE_Y + 600),   # Ref 3
        (BASE_X + x_offset + 800, BASE_Y + 800),   # Ref 4 (missed)
        (BASE_X + x_offset + 1000, BASE_Y + 1000), # Ref 5 (missed)
    ]

    # Detection locations
    det_coords = [
        (BASE_X + x_offset + 205, BASE_Y + 205),   # Det 1: ~7m from Ref 1 (match)
        (BASE_X + x_offset + 408, BASE_Y + 408),   # Det 2: ~11m from Ref 2 (match)
        (BASE_X + x_offset + 610, BASE_Y + 610),   # Det 3: ~14m from Ref 3 (match)
        (BASE_X + x_offset + 1500, BASE_Y + 1500), # Det 4: FP (no nearby ref)
    ]

    # Bounds
    bounds = create_bounds_gdf(tile_name, map_name, x_offset=x_offset)
    bounds.to_file(FIXTURES_DIR / "bounds_dense.geojson", driver="GeoJSON")

    # Detections
    detections = create_detection_gdf(det_coords, tile_name)
    detections.to_file(FIXTURES_DIR / "detections_dense.geojson", driver="GeoJSON")

    # References
    references = create_reference_gdf(ref_coords, map_name)
    references.to_file(FIXTURES_DIR / "references_dense.geojson", driver="GeoJSON")

    # Calculate and save expected metrics
    expected = calculate_expected_metrics(det_coords, ref_coords)
    with open(FIXTURES_DIR / "expected_f1_dense.json", "w") as f:
        json.dump(expected, f, indent=2)

    print(f"Created dense fixtures: P={expected['precision']}, R={expected['recall']}, F1={expected['f1']}")


def main() -> None:
    """Generate all test fixtures."""
    print(f"Creating test fixtures in {FIXTURES_DIR}")

    # Ensure fixtures directory exists
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    # Create each fixture set
    create_empty_fixtures()
    create_sparse_fixtures()
    create_dense_fixtures()

    print("\nAll fixtures created successfully.")
    print("You can now run: pytest tests/test_integration_regression.py -v")


if __name__ == "__main__":
    main()
