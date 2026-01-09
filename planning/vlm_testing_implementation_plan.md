# VLM Burial Mound Detection: Testing Implementation Plan

**Document Purpose**: Implementation specification for pytest-based testing framework  
**Target Audience**: Claude Code (implementation), Shawn Ross (review/approval)  
**Created**: 2025-01-02  
**Status**: Ready for review

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

**Purpose**: Validate entire pipeline from config to F1 score using real data

**Implementation**:

```python
# tests/test_integration_regression.py

def test_full_pipeline_empty_tile():
    """
    Integration test: empty tile through full pipeline
    Uses recorded API response fixture
    """
    # Load recorded API response
    response = load_fixture("fixtures/tile_empty_response.json")
    
    # Load ground truth
    ground_truth = load_ground_truth("tile_empty")
    
    # Run through pipeline
    detections = parse_detection_response(response)
    matches = match_detections_to_references(detections, ground_truth)
    f1 = calculate_f1_internal(matches)
    
    # Assert against expected value (recorded when fixture created)
    expected_f1 = load_fixture("fixtures/tile_empty_expected_f1.json")
    assert abs(f1 - expected_f1) < 0.01, f"F1 changed: {f1} vs {expected_f1}"

def test_full_pipeline_sparse_tile():
    """Integration test: sparse tile (1-2 mounds)"""
    # Similar structure to empty tile test

def test_full_pipeline_dense_tile():
    """Integration test: dense tile (4+ mounds)"""
    # Similar structure to empty tile test
```

**Fixture Creation** (one-time script):

```python
# scripts/create_test_fixtures.py

def create_regression_fixtures():
    """
    Run ONCE to create regression test fixtures
    
    Selects 3 training tiles, runs detection, saves responses
    """
    test_tiles = {
        'empty': 'K-35-052-4_32635_x3136_y3584.png',  # 0 mounds
        'sparse': 'K-35-052-4_32635_x1792_y3136.png',  # 1 mound
        'dense': 'K-35-053-3_Elenovo_x1792_y1792.png'  # 3 mounds
    }
    
    for name, tile_path in test_tiles.items():
        # Run detection with baseline config
        response = run_detection(tile_path, config='baseline')
        
        # Save raw response
        save_json(f"tests/fixtures/tile_{name}_response.json", response)
        
        # Calculate and save expected F1
        ground_truth = load_ground_truth(tile_path)
        detections = parse_detection_response(response)
        f1 = calculate_f1_from_detections(detections, ground_truth)
        save_json(f"tests/fixtures/tile_{name}_expected_f1.json", f1)
        
        print(f"{name}: {len(detections)} detections, F1={f1:.3f}")
```

**Deliverables**:
- `tests/test_integration_regression.py`: 3 integration tests
- `tests/fixtures/`: 3 response JSON files + 3 expected F1 files
- `scripts/create_test_fixtures.py`: One-time fixture generation script

### 1.2 Preregistration Compliance Tests

**File**: `tests/test_preregistration_compliance.py`

**Purpose**: Enforce methodology parameters committed in preregistration

**Implementation**:

Create constants file first:
```python
# scripts/preregistration_params.py
"""
Preregistered methodology parameters
DO NOT MODIFY without amending preregistration
"""

# Section 2.2: Selection Methodology
RANDOM_SEED = 1766464625
TILE_SIZE_PIXELS = 448
SAMPLES_PER_MAP = 5

# Section 4.1: Evaluation Methodology
SPATIAL_TOLERANCE_METERS = 20.0
MATCHING_ALGORITHM = "hungarian"
CRS_EPSG = 32635

# Section 4.2: Statistical Methods
BOOTSTRAP_ITERATIONS = 1000
FDR_ALPHA = 0.05
```

Then test file:
```python
# tests/test_preregistration_compliance.py

from scripts.preregistration_params import (
    RANDOM_SEED, TILE_SIZE_PIXELS, SPATIAL_TOLERANCE_METERS,
    MATCHING_ALGORITHM, CRS_EPSG
)

def test_spatial_tolerance_matches_preregistration():
    """
    Verify 20m tolerance per preregistration Section 4.1
    
    CRITICAL: Changing this invalidates preregistration
    """
    from scripts.lib_advanced_metrics import SPATIAL_TOLERANCE
    assert SPATIAL_TOLERANCE == SPATIAL_TOLERANCE_METERS, \
        f"Spatial tolerance mismatch: {SPATIAL_TOLERANCE} != {SPATIAL_TOLERANCE_METERS}"

def test_hungarian_matching_is_used():
    """
    Verify Hungarian algorithm per preregistration Section 4.1
    
    Tests that matching uses Hungarian (optimal assignment),
    not greedy nearest-neighbor
    """
    from scripts.lib_advanced_metrics import match_detections_to_references
    
    # Create test case where Hungarian and greedy give different results
    detections = [(0, 0), (10, 0)]  # Two detections
    references = [(0, 5), (10, 5)]  # Two references
    
    matches = match_detections_to_references(detections, references)
    
    # Hungarian should match (0,0)→(0,5) and (10,0)→(10,5)
    # Greedy might match differently
    # Verify optimal total distance
    total_distance = sum(dist for _, _, dist in matches)
    optimal_distance = 10.0  # 2 * 5m
    
    assert abs(total_distance - optimal_distance) < 0.01, \
        "Matching does not use Hungarian algorithm"

def test_tile_size_matches_preregistration():
    """Verify 448x448 per preregistration Section 2.2"""
    from scripts.config import TILE_SIZE
    assert TILE_SIZE == (TILE_SIZE_PIXELS, TILE_SIZE_PIXELS)

def test_random_seed_matches_preregistration():
    """Verify seed 1766464625 per preregistration Section 2.2"""
    from scripts.config import SEED
    assert SEED == RANDOM_SEED

def test_crs_matches_preregistration():
    """Verify EPSG:32635 per preregistration Section 4.1"""
    from scripts.lib_advanced_metrics import CRS
    assert CRS == f"EPSG:{CRS_EPSG}"
```

**Deliverables**:
- `scripts/preregistration_params.py`: Canonical parameter source
- `tests/test_preregistration_compliance.py`: 5 compliance tests
- Refactor existing scripts to import from `preregistration_params.py`

### 1.3 Config Behavioral Uniqueness Tests

**File**: `tests/test_config_uniqueness.py`

**Purpose**: Verify 16 experimental configs produce distinct behaviors

**Rationale**: Config files might look different but execute identically due to:
- Temperature parameters being ignored by model
- Prompt variants producing identical outputs
- Config parsing errors causing fallback to defaults

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

def test_configs_produce_distinct_outputs():
    """
    Verify configs don't collapse to identical behavior
    
    Runs simple detection on same tile with each config,
    verifies sufficient output diversity
    """
    # Use one of our regression test tiles
    test_tile_response = load_fixture("fixtures/tile_sparse_response.json")
    
    outputs = {}
    for config_path in list_config_files():
        config = load_config(config_path)
        # Parse detection with this config's parameters
        detections = parse_detection_response(test_tile_response, config)
        # Create hashable representation
        output_signature = (
            len(detections),
            tuple(sorted((d.x, d.y) for d in detections))
        )
        outputs[config_path.stem] = output_signature
    
    # Assert we get at least 12 distinct outputs (allow some duplication)
    unique_outputs = len(set(outputs.values()))
    assert unique_outputs >= 12, \
        f"Only {unique_outputs}/16 unique outputs - configs may be redundant"
    
    # Report any duplicate configs
    from collections import Counter
    duplicates = [sig for sig, count in Counter(outputs.values()).items() 
                  if count > 1]
    if duplicates:
        print(f"Warning: {len(duplicates)} duplicate output signatures")
```

**Deliverables**:
- `tests/test_config_uniqueness.py`: 3 config verification tests

### 1.4 F1 Calculation Correctness Tests

**File**: `tests/test_f1_calculation.py`

**Purpose**: Validate core metric calculation logic with known test cases

**Implementation**:

```python
# tests/test_f1_calculation.py

def test_f1_perfect_match():
    """F1 = 1.0 when all detections match references perfectly"""
    detections = [(0, 0), (10, 10), (20, 20)]
    references = [(0, 0), (10, 10), (20, 20)]
    
    matches = match_detections_to_references(detections, references)
    f1 = calculate_f1_internal(matches)
    
    assert f1 == 1.0

def test_f1_no_matches():
    """F1 = 0.0 when no detections match references"""
    detections = [(0, 0), (10, 10)]
    references = [(100, 100), (200, 200)]  # Far from detections
    
    matches = match_detections_to_references(detections, references)
    f1 = calculate_f1_internal(matches)
    
    assert f1 == 0.0

def test_f1_partial_precision_recall():
    """Test known precision/recall case"""
    detections = [(0, 0), (10, 10), (20, 20), (30, 30)]  # 4 detections
    references = [(0, 0), (10, 10), (100, 100)]  # 3 references, 2 match
    
    # Expected: 2 TP, 2 FP, 1 FN
    # Precision = 2/4 = 0.5
    # Recall = 2/3 = 0.667
    # F1 = 2 * 0.5 * 0.667 / (0.5 + 0.667) = 0.571
    
    matches = match_detections_to_references(detections, references)
    f1 = calculate_f1_internal(matches)
    
    assert abs(f1 - 0.571) < 0.01

def test_f1_empty_tile():
    """F1 when both detections and references are empty"""
    detections = []
    references = []
    
    matches = match_detections_to_references(detections, references)
    f1 = calculate_f1_internal(matches)
    
    # Convention: F1 = 1.0 for true negative (nothing to detect, nothing detected)
    assert f1 == 1.0

def test_hungarian_gives_optimal_assignment():
    """
    Verify Hungarian matching minimizes total distance
    
    Test case where greedy would give suboptimal assignment
    """
    detections = [(0, 0), (10, 0)]
    references = [(1, 10), (9, 10)]
    
    # Optimal: (0,0)→(1,10) and (10,0)→(9,10) = sqrt(101) + sqrt(101) ≈ 20.1
    # Greedy might: (0,0)→(9,10) and (10,0)→(1,10) = sqrt(181) + sqrt(181) ≈ 26.9
    
    matches = match_detections_to_references(detections, references)
    total_distance = sum(dist for _, _, dist in matches)
    
    optimal_distance = 2 * (1**2 + 10**2)**0.5
    assert abs(total_distance - optimal_distance) < 0.01

def test_spatial_tolerance_applied():
    """Verify 20m tolerance correctly filters matches"""
    detections = [(0, 0), (0, 25)]  # Second is >20m from nearest reference
    references = [(0, 0), (0, 50)]
    
    matches = match_detections_to_references(
        detections, references, 
        tolerance_meters=20.0
    )
    
    # Should match (0,0)→(0,0), but (0,25) too far from (0,50)
    assert len(matches) == 1
    assert matches[0][2] == 0.0  # Perfect match for first pair
```

**Deliverables**:
- `tests/test_f1_calculation.py`: 6 correctness tests

---

### Tier 1 Summary

**Total Estimated Time**: 6-8 hours (including pytest learning)

**Files Created**:
- `tests/__init__.py`
- `tests/conftest.py` (pytest configuration)
- `tests/test_integration_regression.py` (3 tests)
- `tests/test_preregistration_compliance.py` (5 tests)
- `tests/test_config_uniqueness.py` (3 tests)
- `tests/test_f1_calculation.py` (6 tests)
- `scripts/preregistration_params.py` (constants)
- `scripts/create_test_fixtures.py` (one-time script)
- `tests/fixtures/*.json` (6 fixture files)
- `pytest.ini` (pytest config)

**Total Tests**: ~17 tests covering critical paths

**Run Command**: `pytest tests/ -v`

**Success Criteria**: All tests pass, providing confidence in:
- End-to-end pipeline correctness
- Methodology compliance with preregistration
- Config behavioral diversity
- Core metric calculation accuracy

---

## TIER 2: High-Value Tests (If Time Permits)

**Priority**: Valuable but not blocking  
**Time Estimate**: 3-4 hours  
**Implement if**: Tier 1 complete and time available before factorial experiments

### 2.1 Voting Aggregation Correctness

**File**: `tests/test_voting_aggregation.py`

**Purpose**: Validate consensus voting logic

```python
def test_voting_threshold_3_of_5():
    """Test 3/5 consensus threshold"""
    # 5 passes detect at slightly different coordinates
    pass_detections = [
        [(10, 10)],  # Pass 1
        [(10.5, 10.2)],  # Pass 2 (within spatial tolerance)
        [(10.3, 9.8)],  # Pass 3
        [(50, 50)],  # Pass 4 (different location)
        [(10.1, 10.1)]  # Pass 5
    ]
    
    consensus = aggregate_voting(pass_detections, threshold=3, tolerance_m=5.0)
    
    # Should find 1 consensus detection at ~(10, 10) with 4/5 votes
    assert len(consensus) == 1
    assert consensus[0].vote_count == 4

def test_voting_spatial_matching():
    """Detections within tolerance are matched correctly"""
    # Similar test for spatial matching across passes

def test_voting_edge_case_exactly_at_threshold():
    """Detection appearing in exactly k of N passes"""
    # Test tie-breaking behavior
```

### 2.2 Cost Model Validation

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

### 2.3 Reproducibility/Determinism Tests

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
│   ├── preregistration_params.py  # NEW
│   └── create_test_fixtures.py     # NEW
├── tests/
│   ├── __init__.py                 # NEW
│   ├── conftest.py                 # NEW
│   ├── fixtures/                   # NEW
│   │   ├── tile_empty_response.json
│   │   ├── tile_empty_expected_f1.json
│   │   ├── tile_sparse_response.json
│   │   ├── tile_sparse_expected_f1.json
│   │   ├── tile_dense_response.json
│   │   └── tile_dense_expected_f1.json
│   ├── test_integration_regression.py
│   ├── test_preregistration_compliance.py
│   ├── test_config_uniqueness.py
│   └── test_f1_calculation.py
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
tests/test_integration_regression.py::test_full_pipeline_empty_tile PASSED
tests/test_integration_regression.py::test_full_pipeline_sparse_tile PASSED
tests/test_integration_regression.py::test_full_pipeline_dense_tile PASSED
tests/test_preregistration_compliance.py::test_spatial_tolerance_matches_preregistration PASSED
tests/test_preregistration_compliance.py::test_hungarian_matching_is_used PASSED
...

======================= 17 passed in 2.34s =======================
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

1. Create `scripts/preregistration_params.py`
2. Refactor existing code to import from this file
3. Write compliance tests in `tests/test_preregistration_compliance.py`
4. Run tests: `pytest tests/test_preregistration_compliance.py -v`

### Step 4: Integration Tests (120-180 min)

1. Write `tests/test_integration_regression.py`
2. Test with each fixture (empty, sparse, dense)
3. Debug any failures
4. Document expected vs actual F1 scores

### Step 5: Config and F1 Tests (90-120 min)

1. Write `tests/test_config_uniqueness.py`
2. Write `tests/test_f1_calculation.py`
3. Run full Tier 1 test suite

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
- ✅ Tests run in <5 seconds
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
3. **Config uniqueness threshold**: Currently 12/16 unique outputs - adjust if needed?
4. **Time budget**: Confirm 6-8 hours acceptable for Tier 1 implementation?
5. **Tier 2 priority**: Should we implement Tier 2, or stop after Tier 1?

---

**Document End**

*Ready for review and handoff to Claude Code for implementation*
