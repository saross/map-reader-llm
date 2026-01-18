# VLM Burial Mound Detection: Testing Implementation Plan

**Document Purpose**: Implementation specification for pytest-based testing framework
**Target Audience**: Claude Code (implementation), Shawn Ross (review/approval)
**Created**: 2025-01-02
**Updated**: 2026-01-17
**Status**: Revised based on review

---

## Executive Summary

This testing plan supports a research project with:
- Hundreds of upcoming config-driven experimental runs
- Multiple collaborators modifying code
- History of silent bugs affecting metric calculations
- Budget constraints requiring accurate cost estimation
- Preregistered methodology requiring compliance verification

**Testing Philosophy**: Research code needs different testing than production software. Focus on **reproducibility**, **integration correctness**, and **methodology compliance** rather than exhaustive unit test coverage.

**Implementation Strategy**: Phased approach starting with critical path tests (Tier 1), expanding to high-value tests if time permits (Tier 2), with optional coverage (Tier 3).

**2026-01-17 Revision #1**: Voting aggregation promoted to Tier 1. Config uniqueness test redesigned. Ground truth and provider metadata tests added.

**2026-01-17 Revision #2**: Feasibility spike revealed significant mismatches between plan assumptions and actual code (function signatures, missing constants, schema differences). Plan simplified to **integration-focused approach** — testing pipeline outputs rather than internal function behaviour. This is more maintainable and better suited to research code.

---

## Context and Requirements

### Actual Pain Points (from user)
1. ✅ **Bugs**: Metric calculation bugs requiring reruns, config loading failures
2. ✅ **Reproducibility**: Need deterministic results across runs
3. ✅ **Confidence**: Hundreds of factorial experiment runs upcoming
4. ✅ **Collaboration**: Two co-authors may modify code

### What We're NOT Building
- ❌ Comprehensive unit test coverage (wrong priority for research code)
- ❌ Mocked LLM API calls (too fragile, wrong abstraction)
- ❌ Synthetic test data (less valuable than small real data regression tests)
- ❌ Production-grade CI/CD pipeline (overkill for research timeline)

### What We ARE Building
- ✅ Critical path integration tests with real data
- ✅ Preregistration methodology compliance tests
- ✅ Config behavioral verification
- ✅ Core metric calculation correctness tests
- ✅ Reproducibility/determinism validation

---

## Testing Approach: Key Decisions

### 1. Use Real Training Tiles for Regression Tests

**Decision**: Use 3 tiles from existing 20 training tiles (already contaminated)

**Rationale**:
- Training set already excluded from experimentation
- Ground truth available and documented
- Represents diverse conditions (empty, sparse, dense)
- No additional data consumption from 361-tile corpus

**Selected Tiles**:
- **Empty tile**: 0 mounds (tests True Negative handling)
- **Sparse tile**: 1-2 mounds (tests basic TP/FP discrimination)
- **Dense tile**: 4+ mounds (tests crowding, multiple detections)

### 2. Record-Replay Real API Responses (Not Mocking)

**Decision**: Run detection ONCE on test tiles, save raw JSON responses as fixtures

**Rationale**:
- Tests parsing/aggregation logic against real API output format
- No complex mocking infrastructure needed
- Catches real-world edge cases in API responses
- Simple to understand and maintain

**Process**:
1. Run detection on 3 test tiles with baseline config
2. Save raw JSON responses to `tests/fixtures/`
3. Save expected F1 scores for each tile
4. Tests replay these responses through pipeline

**Note**: Won't catch future API changes, but those will be obvious in real experimental runs anyway.

### 3. Integration Tests Are Primary

**Decision**: Integration tests validate end-to-end pipeline, not isolated functions

**Rationale**:
- Real risk is pipeline integration errors, not unit-level bugs
- One integration test catches more issues than 10 unit tests
- Matches research workflow (config → tiles → metrics)
- Efficient for limited testing time budget

---

## Implementation Plan

## TIER 1: Critical Path Tests (IMPLEMENT FIRST)

**Priority**: Essential for upcoming factorial experiments  
**Time Estimate**: 6-8 hours (includes pytest learning curve)  
**Stop here if time-constrained** - covers 80% of actual risks

### 1.1 Integration Regression Tests

**File**: `tests/test_integration_regression.py`

**Purpose**: Validate that F1 calculation produces consistent results when given the same inputs

**Approach**: Tests work at the GeoDataFrame level, matching how the actual scripts work. We don't test internal function behaviour; we test that known inputs produce expected outputs.

**Implementation**:

```python
# tests/test_integration_regression.py
import geopandas as gpd
import pytest
from pathlib import Path

# Import the actual function as used in scripts
from scripts.lib_advanced_metrics import calculate_f1_internal, load_data


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


def test_f1_empty_tile(fixtures_dir):
    """
    Integration test: empty tile (no detections, no ground truth in tile).

    Verifies F1 calculation handles true negative case correctly.
    """
    # Load pre-saved GeoJSON fixtures (not API responses)
    gdf_det = gpd.read_file(fixtures_dir / "detections_empty.geojson")
    gdf_ref = gpd.read_file(fixtures_dir / "references_empty.geojson")
    gdf_bounds = gpd.read_file(fixtures_dir / "bounds_empty.geojson")

    precision, recall, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds)

    # Expected: empty input gives F1=0.0 (actual behaviour, not F1=1.0)
    expected_f1 = 0.0
    assert abs(f1 - expected_f1) < 0.01, f"F1 mismatch: {f1} vs {expected_f1}"


def test_f1_sparse_tile(fixtures_dir):
    """Integration test: sparse tile (1-2 mounds)."""
    gdf_det = gpd.read_file(fixtures_dir / "detections_sparse.geojson")
    gdf_ref = gpd.read_file(fixtures_dir / "references_sparse.geojson")
    gdf_bounds = gpd.read_file(fixtures_dir / "bounds_sparse.geojson")

    precision, recall, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds)

    # Load expected value recorded when fixture was created
    import json
    with open(fixtures_dir / "expected_f1_sparse.json") as fp:
        expected = json.load(fp)

    assert abs(f1 - expected["f1"]) < 0.01, f"F1 regression: {f1} vs {expected['f1']}"


def test_f1_dense_tile(fixtures_dir):
    """Integration test: dense tile (4+ mounds)."""
    gdf_det = gpd.read_file(fixtures_dir / "detections_dense.geojson")
    gdf_ref = gpd.read_file(fixtures_dir / "references_dense.geojson")
    gdf_bounds = gpd.read_file(fixtures_dir / "bounds_dense.geojson")

    precision, recall, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds)

    import json
    with open(fixtures_dir / "expected_f1_dense.json") as fp:
        expected = json.load(fp)

    assert abs(f1 - expected["f1"]) < 0.01, f"F1 regression: {f1} vs {expected['f1']}"
```

**Fixture Creation** (one-time script):

```python
# scripts/create_test_fixtures.py
"""
One-time script to create regression test fixtures.

Run this ONCE to generate GeoJSON fixtures from actual pipeline outputs.
Save the fixture files to tests/fixtures/ and commit them.
"""
import geopandas as gpd
import json
from pathlib import Path

from scripts.lib_advanced_metrics import calculate_f1_internal

FIXTURES_DIR = Path("tests/fixtures")


def create_fixtures_from_pipeline_output(
    name: str,
    detections_geojson: Path,
    references_geojson: Path,
    bounds_geojson: Path,
) -> None:
    """
    Create test fixtures from actual pipeline outputs.

    Args:
        name: Fixture name (e.g., 'sparse', 'dense', 'empty')
        detections_geojson: Path to detection GeoJSON from pipeline
        references_geojson: Path to ground truth GeoJSON
        bounds_geojson: Path to tile bounds GeoJSON
    """
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    # Load and save detection fixture
    gdf_det = gpd.read_file(detections_geojson)
    gdf_det.to_file(FIXTURES_DIR / f"detections_{name}.geojson", driver="GeoJSON")

    # Load and save reference fixture
    gdf_ref = gpd.read_file(references_geojson)
    gdf_ref.to_file(FIXTURES_DIR / f"references_{name}.geojson", driver="GeoJSON")

    # Load and save bounds fixture
    gdf_bounds = gpd.read_file(bounds_geojson)
    gdf_bounds.to_file(FIXTURES_DIR / f"bounds_{name}.geojson", driver="GeoJSON")

    # Calculate and save expected F1
    precision, recall, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds)

    with open(FIXTURES_DIR / f"expected_f1_{name}.json", "w") as fp:
        json.dump({"precision": precision, "recall": recall, "f1": f1}, fp, indent=2)

    print(f"Created fixtures for '{name}': P={precision:.3f}, R={recall:.3f}, F1={f1:.3f}")
```

**Deliverables**:
- `tests/test_integration_regression.py`: 3 integration tests
- `tests/fixtures/`: GeoJSON fixtures + expected F1 JSON files
- `scripts/create_test_fixtures.py`: One-time fixture generation script

### 1.2 Preregistration Compliance Tests

**File**: `tests/test_preregistration_compliance.py`

**Purpose**: Verify methodology parameters match preregistration

**Approach**: Test at file/metadata level rather than importing constants. This avoids coupling tests to internal module structure, which may change.

**Implementation**:

```python
# tests/test_preregistration_compliance.py
"""
Preregistration compliance tests.

These tests verify that methodology parameters match the preregistration.
They check files and metadata rather than importing internal constants,
making them resilient to refactoring.
"""
import json
from pathlib import Path

import geopandas as gpd
import pytest

# Preregistered values (from preregistration document)
PREREGISTERED = {
    "random_seed": 1766464625,          # Section 2.2
    "tile_size_pixels": 512,            # Section 2.2 (512px tiles, 448px stride)
    "stride_pixels": 448,               # Section 2.2
    "samples_per_map": 5,               # Section 2.2
    "spatial_tolerance_meters": 20.0,   # Section 4.1
    "crs_epsg": 32635,                  # Section 4.1
}


def test_tile_selection_seed_matches_preregistration():
    """
    Verify tile selection used preregistered seed (Section 2.2).

    Checks the metadata file created during tile selection.
    """
    metadata_path = Path("inputs/tiles/tile_selection_metadata.json")
    assert metadata_path.exists(), f"Tile selection metadata missing: {metadata_path}"

    with open(metadata_path) as fp:
        metadata = json.load(fp)

    actual_seed = metadata.get("random_seed") or metadata.get("seed")
    assert actual_seed == PREREGISTERED["random_seed"], (
        f"Seed mismatch: {actual_seed} != {PREREGISTERED['random_seed']}"
    )


def test_ground_truth_crs_matches_preregistration():
    """
    Verify ground truth uses preregistered CRS (Section 4.1).
    """
    # Find a ground truth file
    gt_files = list(Path("inputs/vectors/references").glob("*.geojson"))
    assert len(gt_files) > 0, "No ground truth files found"

    gdf = gpd.read_file(gt_files[0])
    actual_epsg = gdf.crs.to_epsg() if gdf.crs else None

    assert actual_epsg == PREREGISTERED["crs_epsg"], (
        f"CRS mismatch: EPSG:{actual_epsg} != EPSG:{PREREGISTERED['crs_epsg']}"
    )


def test_config_has_tile_size():
    """
    Verify config.py contains expected tile size (Section 2.2).
    """
    from scripts.config import TILE_SIZE, STRIDE

    assert TILE_SIZE == PREREGISTERED["tile_size_pixels"], (
        f"TILE_SIZE mismatch: {TILE_SIZE} != {PREREGISTERED['tile_size_pixels']}"
    )
    assert STRIDE == PREREGISTERED["stride_pixels"], (
        f"STRIDE mismatch: {STRIDE} != {PREREGISTERED['stride_pixels']}"
    )


def test_f1_uses_correct_spatial_tolerance():
    """
    Verify F1 calculation uses 20m tolerance (Section 4.1).

    Tests behaviour rather than inspecting constants.
    """
    from scripts.lib_advanced_metrics import calculate_f1_internal
    from shapely.geometry import Point

    # Create detection 15m from reference (should match at 20m tolerance)
    det_within = gpd.GeoDataFrame(
        {"geometry": [Point(0, 15)]}, crs="EPSG:32635"
    )
    # Create detection 25m from reference (should NOT match at 20m tolerance)
    det_outside = gpd.GeoDataFrame(
        {"geometry": [Point(0, 25)]}, crs="EPSG:32635"
    )
    ref = gpd.GeoDataFrame(
        {"geometry": [Point(0, 0)]}, crs="EPSG:32635"
    )
    bounds = gpd.GeoDataFrame(
        {"geometry": [Point(0, 0).buffer(100)]}, crs="EPSG:32635"
    )

    # 15m should match
    p1, r1, f1_within = calculate_f1_internal(det_within, ref, bounds, buffer_meters=20)
    assert f1_within > 0, "Detection 15m away should match at 20m tolerance"

    # 25m should NOT match
    p2, r2, f1_outside = calculate_f1_internal(det_outside, ref, bounds, buffer_meters=20)
    assert f1_outside == 0, "Detection 25m away should NOT match at 20m tolerance"
```

**Deliverables**:
- `tests/test_preregistration_compliance.py`: 4 compliance tests
- No new constants file needed (values defined in test file)

### 1.3 Config Structural Uniqueness Tests

**File**: `tests/test_config_uniqueness.py`

**Purpose**: Verify 16 experimental configs are structurally distinct and valid

**Rationale**: Config files must be:
- Loadable without errors
- Complete (all required fields present)
- Distinct (no duplicate parameter combinations)

**Note**: These tests validate config *structure*, not API *behaviour*. Behavioural differences are validated in experimental runs where actual API responses differ.

**Implementation**:

```python
# tests/test_config_uniqueness.py

def test_configs_load_without_error():
    """All 16 configs load successfully"""
    config_files = list_config_files()
    assert len(config_files) == 16

    for config_path in config_files:
        config = load_config(config_path)
        assert config is not None, f"Failed to load {config_path}"

def test_configs_have_required_fields():
    """All configs contain required fields"""
    required_fields = ['prompt_type', 'temperature', 'model', 'voting_threshold']

    for config_path in list_config_files():
        config = load_config(config_path)
        for field in required_fields:
            assert field in config, f"{config_path} missing field: {field}"

def test_configs_have_distinct_parameters():
    """
    Verify configs produce distinct parameter combinations.

    Note: This validates config structure, not API behaviour.
    Actual behavioural differences are validated in experimental runs.
    """
    signatures = {}
    for config_path in list_config_files():
        config = load_config(config_path)
        sig = (
            config.get('model'),
            config.get('temperature'),
            config.get('prompt_type'),
            config.get('voting_threshold'),
            # Add other distinguishing parameters as needed
        )
        signatures[config_path.stem] = sig

    # All 16 configs should have unique parameter combinations
    unique_sigs = set(signatures.values())
    assert len(unique_sigs) == len(signatures), \
        "Some configs have identical parameter combinations"
```

**Deliverables**:
- `tests/test_config_uniqueness.py`: 3 config verification tests

### 1.4 F1 Calculation Correctness Tests

**File**: `tests/test_f1_calculation.py`

**Purpose**: Validate F1 calculation produces correct results for known inputs

**Approach**: Test at the GeoDataFrame level using `calculate_f1_internal()` directly. Don't test internal matching functions — verify outputs, not implementation.

**Implementation**:

```python
# tests/test_f1_calculation.py
"""
F1 calculation correctness tests.

Tests the calculate_f1_internal function with synthetic GeoDataFrames
to verify correct precision/recall/F1 computation.
"""
import geopandas as gpd
import pytest
from shapely.geometry import Point

from scripts.lib_advanced_metrics import calculate_f1_internal


def make_gdf(points: list[tuple[float, float]], crs: str = "EPSG:32635") -> gpd.GeoDataFrame:
    """Helper to create GeoDataFrame from coordinate tuples."""
    if not points:
        return gpd.GeoDataFrame({"geometry": []}, crs=crs)
    return gpd.GeoDataFrame(
        {"geometry": [Point(x, y) for x, y in points]},
        crs=crs,
    )


def make_bounds(points: list[tuple[float, float]], buffer: float = 100) -> gpd.GeoDataFrame:
    """Create a bounds polygon covering all points."""
    from shapely.ops import unary_union
    if not points:
        # Default bounds if no points
        return gpd.GeoDataFrame(
            {"geometry": [Point(0, 0).buffer(buffer)]},
            crs="EPSG:32635",
        )
    geoms = [Point(x, y).buffer(buffer) for x, y in points]
    return gpd.GeoDataFrame(
        {"geometry": [unary_union(geoms)]},
        crs="EPSG:32635",
    )


def test_f1_perfect_match():
    """F1 = 1.0 when all detections match references perfectly."""
    coords = [(0, 0), (100, 100), (200, 200)]
    gdf_det = make_gdf(coords)
    gdf_ref = make_gdf(coords)
    gdf_bounds = make_bounds(coords)

    precision, recall, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds)

    assert f1 == 1.0, f"Expected F1=1.0 for perfect match, got {f1}"
    assert precision == 1.0
    assert recall == 1.0


def test_f1_no_matches():
    """F1 = 0.0 when no detections match references (too far apart)."""
    det_coords = [(0, 0), (100, 100)]
    ref_coords = [(1000, 1000), (2000, 2000)]  # Very far from detections
    gdf_det = make_gdf(det_coords)
    gdf_ref = make_gdf(ref_coords)
    gdf_bounds = make_bounds(det_coords + ref_coords)

    precision, recall, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds)

    assert f1 == 0.0, f"Expected F1=0.0 when no matches, got {f1}"


def test_f1_empty_inputs():
    """F1 = 0.0 when both detections and references are empty."""
    gdf_det = make_gdf([])
    gdf_ref = make_gdf([])
    gdf_bounds = make_bounds([])

    precision, recall, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds)

    # Actual behaviour: F1=0.0 for empty inputs (not 1.0)
    assert f1 == 0.0, f"Expected F1=0.0 for empty inputs, got {f1}"


def test_f1_partial_match():
    """Test known precision/recall case."""
    # 4 detections, 3 references, 2 should match
    det_coords = [(0, 0), (100, 100), (200, 200), (300, 300)]
    ref_coords = [(0, 0), (100, 100), (1000, 1000)]  # Third ref far from any det
    gdf_det = make_gdf(det_coords)
    gdf_ref = make_gdf(ref_coords)
    gdf_bounds = make_bounds(det_coords + ref_coords)

    precision, recall, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds)

    # Expected: 2 TP, 2 FP, 1 FN
    # Precision = 2/4 = 0.5
    # Recall = 2/3 = 0.667
    # F1 = 2 * 0.5 * 0.667 / (0.5 + 0.667) ≈ 0.571
    assert abs(precision - 0.5) < 0.01, f"Expected precision≈0.5, got {precision}"
    assert abs(recall - 0.667) < 0.01, f"Expected recall≈0.667, got {recall}"
    assert abs(f1 - 0.571) < 0.02, f"Expected F1≈0.571, got {f1}"
```

**Deliverables**:
- `tests/test_f1_calculation.py`: 4 correctness tests

### 1.5 Ground Truth Loading Validation

**File**: `tests/test_ground_truth.py`

**Purpose**: Verify ground truth files exist and have expected schema

**Approach**: Test against actual file structure in `inputs/vectors/references/`.

**Implementation**:

```python
# tests/test_ground_truth.py
"""
Ground truth validation tests.

Verifies ground truth files are present and correctly formatted.
"""
from pathlib import Path

import geopandas as gpd
import pytest


REFERENCES_DIR = Path("inputs/vectors/references")


def test_ground_truth_files_exist():
    """Verify ground truth reference files exist."""
    gt_files = list(REFERENCES_DIR.glob("*.geojson"))
    assert len(gt_files) > 0, f"No ground truth files in {REFERENCES_DIR}"


def test_ground_truth_schema():
    """
    Verify ground truth files have expected schema.

    Actual schema: ['fid', 'Map', 'Symbol', 'Author', 'layer', 'path', 'geometry']
    """
    gt_files = list(REFERENCES_DIR.glob("*.geojson"))
    assert len(gt_files) > 0, "No ground truth files found"

    gdf = gpd.read_file(gt_files[0])

    # Required columns (based on actual schema)
    required = ["geometry", "fid"]
    for col in required:
        assert col in gdf.columns, f"Missing required column: {col}"

    # Geometries should be valid
    if len(gdf) > 0:
        assert gdf.geometry.is_valid.all(), "Invalid geometries in ground truth"


def test_ground_truth_crs():
    """Verify ground truth uses expected CRS (EPSG:32635)."""
    gt_files = list(REFERENCES_DIR.glob("*.geojson"))
    assert len(gt_files) > 0, "No ground truth files found"

    gdf = gpd.read_file(gt_files[0])
    actual_epsg = gdf.crs.to_epsg() if gdf.crs else None

    assert actual_epsg == 32635, f"Unexpected CRS: EPSG:{actual_epsg}"
```

**Deliverables**:
- `tests/test_ground_truth.py`: 3 ground truth validation tests

---

### Tier 1 Summary

**Files Created**:
- `tests/__init__.py`
- `tests/conftest.py` (pytest configuration)
- `tests/test_integration_regression.py` (3 tests)
- `tests/test_preregistration_compliance.py` (4 tests)
- `tests/test_config_uniqueness.py` (3 tests)
- `tests/test_f1_calculation.py` (4 tests)
- `tests/test_ground_truth.py` (3 tests)
- `scripts/create_test_fixtures.py` (one-time script)
- `tests/fixtures/*.geojson` (GeoJSON fixture files)
- `tests/fixtures/*.json` (expected value files)
- `pytest.ini` (pytest config)

**Total Tests**: 17 tests covering critical paths

**Run Command**: `pytest tests/ -v`

**Success Criteria**: All tests pass, providing confidence in:
- End-to-end pipeline correctness (integration regression)
- Methodology compliance with preregistration
- Config structural validity
- Core metric calculation accuracy
- Ground truth data integrity

**Removed from original plan** (feasibility spike findings):
- Voting aggregation tests — function doesn't exist; voting is pre-computed in GeoJSON
- Provider metadata extraction tests — requires response objects, too complex for value

---

## TIER 2: High-Value Tests (If Time Permits)

**Priority**: Valuable but not blocking
**Implement if**: Tier 1 complete and time available before factorial experiments

### 2.1 Cost Model Validation

**File**: `tests/test_cost_estimation.py` + one-time validation script

**Purpose**: Verify cost predictions match actual Google billing

**Implementation**:

```python
# scripts/validate_cost_model.py (one-time validation)

def validate_cost_model():
    """
    One-time validation of cost model against actual billing
    
    Run small workload, compare predicted vs actual costs
    """
    workload = {
        'tiles': 2,
        'configs': 1,
        'passes': 1
    }
    
    # Predict costs
    predicted_cost = estimate_cost(workload)
    
    # Run actual workload
    run_small_workload(workload)
    
    # Wait 20 minutes for Google billing to update
    print("Waiting 20 minutes for Google billing update...")
    time.sleep(1200)
    
    # Fetch actual cost from Google dashboard
    actual_cost = fetch_google_dashboard_cost(last_20_min=True)
    
    # Compare
    error_pct = abs(predicted_cost - actual_cost) / actual_cost * 100
    
    print(f"Predicted: ${predicted_cost:.4f}")
    print(f"Actual: ${actual_cost:.4f}")
    print(f"Error: {error_pct:.1f}%")
    
    assert error_pct < 10, f"Cost model error too high: {error_pct}%"
```

Then ongoing tests:
```python
# tests/test_cost_estimation.py

def test_cost_estimation_token_counting():
    """Verify token counts aggregated correctly"""
    # Test that token metadata is correctly summed

def test_cost_estimation_pricing_model():
    """Verify pricing model uses correct rates"""
    # Test against known pricing (update when pricing changes)
```

### 2.2 Reproducibility/Determinism Tests

**File**: `tests/test_reproducibility.py`

**Purpose**: Verify deterministic execution where expected

```python
def test_same_config_same_tile_identical_output():
    """
    Running same config on same tile twice gives identical results
    
    Tests reproducibility when random seed is set
    """
    config = load_config("baseline")
    tile = load_fixture("tile_sparse_response.json")
    
    result1 = run_pipeline(tile, config)
    result2 = run_pipeline(tile, config)
    
    assert result1 == result2

def test_random_seed_controls_sampling():
    """Verify random seed actually controls randomness"""
    # Test that setting seed produces deterministic sampling

def test_tile_selection_is_deterministic():
    """Verify tile selection uses preregistered seed"""
    # Test that tile selection is reproducible with seed
```

---

## TIER 3: Optional Coverage

**Priority**: Low - implement only if Tier 1 and 2 complete with time to spare  
**Time Estimate**: 4-6 hours

- Metadata aggregation edge cases
- Bootstrap CI calculation correctness
- GeoJSON output format validation
- Additional unit tests for utility functions

**Recommendation**: Skip unless you have specific known bugs in these areas

---

## Pytest Infrastructure Setup

### Directory Structure

```
project/
├── scripts/
│   ├── lib_advanced_metrics.py
│   ├── lib_llm_metadata.py
│   ├── 4_detect_mounds_batch.py
│   ├── 5_verify_crops.py
│   └── create_test_fixtures.py     # NEW
├── tests/
│   ├── __init__.py                 # NEW
│   ├── conftest.py                 # NEW
│   ├── fixtures/                   # NEW
│   │   ├── detections_empty.geojson
│   │   ├── detections_sparse.geojson
│   │   ├── detections_dense.geojson
│   │   ├── references_empty.geojson
│   │   ├── references_sparse.geojson
│   │   ├── references_dense.geojson
│   │   ├── bounds_empty.geojson
│   │   ├── bounds_sparse.geojson
│   │   ├── bounds_dense.geojson
│   │   ├── expected_f1_sparse.json
│   │   └── expected_f1_dense.json
│   ├── test_integration_regression.py
│   ├── test_preregistration_compliance.py
│   ├── test_config_uniqueness.py
│   ├── test_f1_calculation.py
│   └── test_ground_truth.py
└── pytest.ini                      # NEW
```

### pytest.ini Configuration

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers for organizing tests
markers =
    integration: Integration tests (full pipeline)
    compliance: Preregistration compliance tests
    unit: Unit tests for specific functions
    tier1: Critical path tests (must pass)
    tier2: High-value tests (should pass)
    tier3: Optional coverage

# Output configuration
addopts = 
    -v
    --tb=short
    --strict-markers

# Minimum Python version
minversion = 3.8
```

### conftest.py (Shared Fixtures)

```python
# tests/conftest.py

import pytest
import json
from pathlib import Path

@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory"""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def load_fixture(fixtures_dir):
    """Fixture factory for loading JSON fixtures"""
    def _load(filename):
        path = fixtures_dir / filename
        with open(path) as f:
            return json.load(f)
    return _load

@pytest.fixture
def empty_tile_response(load_fixture):
    """Load empty tile API response fixture"""
    return load_fixture("tile_empty_response.json")

@pytest.fixture
def sparse_tile_response(load_fixture):
    """Load sparse tile API response fixture"""
    return load_fixture("tile_sparse_response.json")

@pytest.fixture
def dense_tile_response(load_fixture):
    """Load dense tile API response fixture"""
    return load_fixture("tile_dense_response.json")

# Add more shared fixtures as needed
```

---

## Running Tests

### Basic Usage

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_integration_regression.py

# Run specific test
pytest tests/test_f1_calculation.py::test_f1_perfect_match

# Run only Tier 1 tests
pytest -m tier1

# Run only integration tests
pytest -m integration

# Run with coverage report (optional)
pytest --cov=scripts --cov-report=term
```

### Expected Output

```
tests/test_integration_regression.py::test_f1_empty_tile PASSED
tests/test_integration_regression.py::test_f1_sparse_tile PASSED
tests/test_integration_regression.py::test_f1_dense_tile PASSED
tests/test_preregistration_compliance.py::test_tile_selection_seed_matches_preregistration PASSED
tests/test_preregistration_compliance.py::test_ground_truth_crs_matches_preregistration PASSED
tests/test_preregistration_compliance.py::test_config_has_tile_size PASSED
tests/test_preregistration_compliance.py::test_f1_uses_correct_spatial_tolerance PASSED
tests/test_config_uniqueness.py::test_configs_load_without_error PASSED
tests/test_config_uniqueness.py::test_configs_have_required_fields PASSED
tests/test_config_uniqueness.py::test_configs_have_distinct_parameters PASSED
tests/test_f1_calculation.py::test_f1_perfect_match PASSED
tests/test_f1_calculation.py::test_f1_no_matches PASSED
tests/test_f1_calculation.py::test_f1_empty_inputs PASSED
tests/test_f1_calculation.py::test_f1_partial_match PASSED
tests/test_ground_truth.py::test_ground_truth_files_exist PASSED
tests/test_ground_truth.py::test_ground_truth_schema PASSED
tests/test_ground_truth.py::test_ground_truth_crs PASSED

======================= 17 passed in 4.23s =======================
```

---

## Implementation Workflow

### Step 1: Setup (30-60 min)

1. Create directory structure
2. Install pytest: `pip install pytest pytest-cov`
3. Create `pytest.ini` and `conftest.py`
4. Create `tests/__init__.py`

### Step 2: Create Test Fixtures (60-90 min)

1. Write `scripts/create_test_fixtures.py`
2. Select 3 training tiles (empty, sparse, dense)
3. Run fixture creation script
4. Verify fixtures created in `tests/fixtures/`
5. Document which tiles were used and their expected F1 scores

### Step 3: Preregistration Compliance (60 min)

1. Write compliance tests in `tests/test_preregistration_compliance.py`
2. Preregistered values are defined in the test file itself (no separate constants file)
3. Run tests: `pytest tests/test_preregistration_compliance.py -v`

### Step 4: Integration Tests (120-180 min)

1. Write `tests/test_integration_regression.py`
2. Test with each fixture (empty, sparse, dense)
3. Debug any failures
4. Document expected vs actual F1 scores

### Step 5: Config, F1, and Ground Truth Tests (90-120 min)

1. Write `tests/test_config_uniqueness.py`
2. Write `tests/test_f1_calculation.py`
3. Write `tests/test_ground_truth.py`
4. Run full Tier 1 test suite

### Step 6: Validation (30 min)

1. Run all tests: `pytest -v`
2. Fix any failures
3. Document test coverage
4. Update README with testing instructions

---

## Red Flags and Debugging

### Common Issues

**Tests fail due to path issues**:
- Check that imports work from `tests/` directory
- May need to add `scripts/` to Python path
- Use `conftest.py` to set up paths if needed

**Integration tests fail with "fixture not found"**:
- Verify `create_test_fixtures.py` ran successfully
- Check `tests/fixtures/` directory exists and contains JSON files
- Verify fixture filenames match test code

**Preregistration compliance tests fail**:
- This is GOOD - means test caught a methodology violation
- Check if code was modified without updating preregistration
- Update either code or preregistration documentation

**Config uniqueness test fails**:
- Some config redundancy may be intentional
- Adjust threshold (e.g., require 10/16 unique instead of 12/16)
- Document which configs are intentionally similar

**F1 calculation tests fail**:
- May indicate actual bug in metric calculation
- Check spatial tolerance, matching algorithm
- Verify edge case handling (empty tiles, etc.)

### When Tests Should Fail (Good Failures)

- ✅ Preregistration compliance test catches accidental parameter change
- ✅ Integration test catches regression after code refactor
- ✅ Config test catches config file parsing error
- ✅ F1 test catches metric calculation bug

### When Tests Shouldn't Fail (Bad Test Design)

- ❌ Tests fail randomly (flaky tests)
- ❌ Tests fail when code is correct (false positives)
- ❌ Tests pass when code is broken (false negatives)
- ❌ Tests are too tightly coupled to implementation details

---

## Maintenance and Updates

### When to Update Tests

**Update fixtures when**:
- API response format changes significantly
- You improve the baseline model/prompt
- Ground truth annotations are corrected

**Update compliance tests when**:
- Preregistration is formally amended
- New methodology parameters are added

**Update integration tests when**:
- Pipeline structure changes (new stages, different ordering)
- Expected F1 scores change due to methodology improvements

### Test Maintenance Cost

**Low maintenance** (rarely need updates):
- Preregistration compliance tests
- F1 calculation unit tests
- Config loading tests

**Medium maintenance** (occasional updates):
- Integration regression tests (when pipeline changes)
- Config uniqueness tests (when adding new configs)

**High maintenance** (avoid):
- Mocked API tests (would break with every API change)
- Overly specific unit tests (break with minor refactors)

---

## Success Metrics

### Tier 1 Complete When:

- ✅ All 17 Tier 1 tests pass
- ✅ Tests run in <10 seconds (GeoDataFrame operations may be slower)
- ✅ No false positives (tests don't fail when code is correct)
- ✅ README updated with testing instructions
- ✅ Collaborators can run tests with single command

### Quality Indicators:

- Integration tests catch at least one real bug during implementation
- Preregistration compliance tests prevent accidental parameter changes
- Config tests reveal any redundant/broken configs
- Team has confidence to refactor code knowing tests will catch regressions

### Red Flags:

- ⚠️ Tests take >30 seconds to run (too slow, will be ignored)
- ⚠️ Tests fail intermittently (flaky, will be ignored)
- ⚠️ Tests require complex setup (too fragile)
- ⚠️ Team avoids running tests (too annoying/slow/brittle)

---

## Documentation Requirements

### README Addition

Add section to main README:

```markdown
## Testing

This project uses pytest for testing critical pipeline components and methodology compliance.

### Running Tests

# All tests
pytest

# Tier 1 only (critical path)
pytest -m tier1

# Specific test file
pytest tests/test_integration_regression.py

### Test Organization

- **Tier 1** (critical): Integration, preregistration compliance, config verification, F1 correctness
- **Tier 2** (high-value): Voting aggregation, cost estimation, reproducibility
- **Tier 3** (optional): Additional edge case coverage

### Test Fixtures

Regression tests use 3 training tiles with recorded API responses:
- `tile_empty`: 0 mounds (True Negative test)
- `tile_sparse`: 1-2 mounds (basic detection test)
- `tile_dense`: 4+ mounds (crowding test)

Fixtures created: 2025-01-02 with baseline config

### Regenerating Fixtures

python scripts/create_test_fixtures.py

⚠️ Only regenerate if API format changes or ground truth is corrected

### Preregistration Compliance

Tests enforce methodology parameters from preregistration:
- Spatial tolerance: 20m
- Matching: Hungarian algorithm
- Tile size: 448×448 pixels
- Random seed: 1766464625

Compliance test failures indicate methodology violations.
```

---

## Handoff Checklist for Claude Code

Before implementation, verify:

- [ ] Access to existing codebase (`scripts/lib_advanced_metrics.py`, etc.)
- [ ] Access to training tiles and ground truth annotations
- [ ] Understanding of preregistration parameters (Section 2.2, 4.1)
- [ ] pytest installation capability
- [ ] Ability to run one-time API calls for fixture creation

During implementation:

- [ ] Create directory structure first
- [ ] Set up pytest.ini and conftest.py before writing tests
- [ ] Run `create_test_fixtures.py` before integration tests
- [ ] Test each tier independently before moving to next
- [ ] Document any deviations from this plan

After implementation:

- [ ] All Tier 1 tests pass
- [ ] Tests run in <5 seconds
- [ ] README updated with testing instructions
- [ ] Fixture creation process documented
- [ ] Known issues/limitations documented

---

## Questions for Reviewer (Shawn)

Before implementation, please confirm:

1. **Tile selection for fixtures**: Approve empty/sparse/dense tile choices from training set?
2. **F1 tolerance**: Is ±0.01 acceptable tolerance for regression tests, or should it be tighter?
3. ~~**Ground truth schema**: Confirm required columns for `test_ground_truth.py`~~ — **RESOLVED**: Schema is `['fid', 'Map', 'Symbol', 'Author', 'layer', 'path', 'geometry']`
4. **Tier 2 priority**: Should we implement Tier 2, or stop after Tier 1?

---

## Revision History

| Date | Changes |
|------|---------|
| 2025-01-02 | Initial version |
| 2026-01-17 | Revision #1: Moved voting to Tier 1, redesigned config test, added ground truth and metadata tests |
| 2026-01-17 | Revision #2: Feasibility spike revealed plan-vs-code mismatches. Simplified to integration-focused approach. Removed voting aggregation tests (function doesn't exist), removed metadata extraction tests (too complex), updated all tests to use GeoDataFrame-level APIs, fixed ground truth schema |

---

**Document End**

*Ready for implementation*
