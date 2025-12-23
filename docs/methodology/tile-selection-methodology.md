# Tile Selection Methodology (Phase 2)

**Created**: 2025-12-23
**Purpose**: Documented procedure for selecting training and holdout tile sets with provenance tracking

---

## Overview

This methodology establishes a clean separation between training and holdout tile sets for VLM-based burial mound detection experiments. All selections are random with documented seeds for reproducibility.

## Data Sources

- **Maps**: 4 Soviet 1:50,000 topographic maps (Bulgaria)
  - K-35-052-4_32635
  - K-35-053-3_Elenovo
  - K-35-062-2_Rakovski
  - K-35-078-1_Lesovo

- **Tiles**: 448×448 pixel tiles at native resolution
  - ~90 tiles per map
  - ~360 tiles total

- **Ground Truth**: `inputs/vectors/mounds-reference.geojson`
  - 569 annotated mound symbols across all maps
  - Annotated by primary researcher (Shawn Ross) and student collaborators

## Selection Criteria

### Content Threshold

Tiles must have **≤75% background pixels** (black [0,0,0]) to be eligible.

**Rationale**: Excludes edge tiles that are predominantly empty while retaining tiles with significant map content.

### Sample Size

- **Training set**: 20 tiles (5 per map)
- **Holdout set**: 20 tiles (5 per map)

### Stratification

**Training Set**:

1. Filter tiles by content threshold
2. Calculate mound count per tile from ground truth
3. Stratify by density category:
   - Empty (0 mounds)
   - Sparse (1-2 mounds)
   - Dense (3+ mounds)
4. Within each map, sample proportionally from density strata
5. If insufficient tiles in a stratum, sample from adjacent strata

**Holdout Set**:

1. Exclude all training tiles
2. Filter by content threshold
3. Apply **spatial separation**: exclude tiles adjacent to training tiles (Manhattan distance ≤ 1 tile = 448 pixels)
4. Match training set density distribution as closely as possible
5. If spatial separation over-constrains, relax adjacency requirement and document

## Randomisation

- **Random seed**: Documented in output manifest
- **Seed selection**: Based on current timestamp at script execution
- **Reproducibility**: Re-running with same seed produces identical selection

## Output Artefacts

### Manifests

- `inputs/training_manifest.json` — list of training tile filenames
- `inputs/holdout_manifest.json` — list of holdout tile filenames
- `inputs/null_tiles_manifest.json` — null tiles for few-shot library
- `inputs/tile_selection_metadata.json` — full metadata including:
  - Random seed used
  - Per-tile mound counts
  - Density strata assignments
  - Spatial separation details
  - Selection timestamp

### Bounds GeoJSON

- `outputs/results/training_bounds.geojson` — spatial extent of training tiles
- `outputs/results/holdout_bounds.geojson` — spatial extent of holdout tiles

## Few-Shot Example Rules

### Positive Examples (Legend Only)

From `inputs/references/`:

- `burial_mound.png` — standard burial mound symbol
- `settlement_mound.png` — settlement mound symbol
- `triangulation_mound.png` — triangulation point on mound
- `benchmark_mound.png` — benchmark on mound

### Negative Examples (Legend Only)

From `inputs/references/`:

- `ref_neg_benchmark.png` — benchmark symbol (no mound)
- `ref_neg_triangulation.png` — triangulation point (no mound)

### Null Tiles (From Training Tiles)

Full empty tiles included in few-shot library to calibrate model expectations and reduce hallucinations. These demonstrate "some tiles contain no mounds."

**Selection methodology**:

1. Pool: All training tiles with `density: empty` (mound_count = 0)
2. Filter: Must meet content threshold (≤75% background)
3. Stratification: One tile required from Lesovo (distinct terrain), remainder from other maps
4. Selection: Stratified random (one per map until target reached)
5. Random seed: 20251223 (date-based for reproducibility)

**Selected null tiles**:

| Tile                                  | Map               | Background % |
| ------------------------------------- | ----------------- | ------------ |
| `K-35-078-1_Lesovo_x2240_y2688.png`   | Lesovo (required) | 0.1%         |
| `K-35-053-3_Elenovo_x3584_y1344.png`  | Elenovo           | 0.3%         |
| `K-35-052-4_32635_x896_y1792.png`     | 32635             | 0.1%         |

**Manifest**: `inputs/null_tiles_manifest.json`

## Constraints

1. **No holdout contamination**: Few-shot examples may only come from legend or training tiles
2. **Documented provenance**: Every example must trace to a specific source
3. **No iterative refinement on holdout**: Holdout tiles are for final evaluation only

---

## Implementation

Script: `scripts/select_tiles_phase2.py`

```bash
# Generate new tile selections
python scripts/select_tiles_phase2.py

# Output:
#   inputs/training_manifest.json
#   inputs/holdout_manifest.json
#   inputs/tile_selection_metadata.json
```

## Verification Checklist

Executed: 2025-12-23 | Seed: 1766464625

- [x] Training and holdout sets are mutually exclusive (verified: 0 overlap)
- [x] All selected tiles meet content threshold (≤75% background)
- [x] Spatial separation applied to holdout tiles (not relaxed)
- [x] Density distribution approximately matched (training: 8 empty, 7 sparse, 5 dense; holdout: identical)
- [x] Random seed documented (1766464625)
- [x] All file paths verified (40/40 tiles exist)
