# CC Instructions: Tile Size Pilot Experiment

## Purpose

Run a pre-registration calibration experiment to determine optimal tile size before committing to the main factorial. This pilot uses fresh tiles that will be discarded afterward — no contamination of training or holdout sets.

## Overview

Test three tile sizes (384×384, 512×512, 1024×1024) using a canonical-only library to determine which size balances detection accuracy with API efficiency.

---

## Phase 1: Tile Selection

### 1.1 Select Pilot Tiles

**Source**: Reserve set (281 tiles from the 361-tile corpus, excluding the 20 training + 60 holdout already selected)

**Count**: 15 tiles

**Stratification target**:
- 5 empty (0 mounds)
- 5 sparse (1-2 mounds)
- 5 dense (3+ mounds)

Adjust if reserve set density distribution doesn't allow exact 5/5/5 split.

**Selection method**:
1. Generate a random seed based on current timestamp (document the seed)
2. Filter reserve tiles by density category
3. Randomly sample from each category
4. Document selected tile IDs

**Output**: 
- `inputs/pilot_tile_manifest.json` — list of 15 tile IDs with density categories
- `inputs/pilot_selection_metadata.json` — seed, selection date, stratification counts

### 1.2 Exclusion Record

Create a record that these 15 tiles are permanently excluded from all future use:

```json
{
  "purpose": "tile_size_pilot",
  "selection_date": "YYYY-MM-DD",
  "random_seed": <seed>,
  "tiles": ["tile_id_1", "tile_id_2", ...],
  "status": "excluded_after_pilot"
}
```

Save to: `inputs/excluded_tiles.json`

---

## Phase 2: Tile Generation

### 2.1 Generate Tiles at Three Sizes

For each of the 15 pilot tiles, generate versions at three sizes from the source map images.

| Size | Stride (12.5% overlap) | Output Directory |
|------|------------------------|------------------|
| 384×384 | 336px | `inputs/pilot_tiles/384/` |
| 512×512 | 448px | `inputs/pilot_tiles/512/` |
| 1024×1024 | 896px | `inputs/pilot_tiles/1024/` |

**Important**: Each tile size covers the same geographic region. For 384 and 1024, the tile must be centered on (or maximally overlap with) the corresponding 512×512 tile's coverage area.

**Edge cases**: If a 1024×1024 tile would extend beyond map boundaries, shift the tile center to keep it within bounds. Document any such adjustments.

### 2.2 Regenerate Ground Truth

For each tile size, regenerate ground truth based on which mound symbols fall within the new tile boundaries.

**Process**:
1. Load master ground truth (all mound locations for the 4 maps)
2. For each pilot tile at each size, compute which mounds fall within tile boundaries
3. Output ground truth files per size

**Output**:
- `inputs/pilot_tiles/384/ground_truth.json`
- `inputs/pilot_tiles/512/ground_truth.json`
- `inputs/pilot_tiles/1024/ground_truth.json`

Each ground truth file should map tile_id → list of mound coordinates (in pixel coordinates for that tile size).

---

## Phase 3: Prepare Detection Configuration

### 3.1 Create Pilot Configuration File

Create a configuration specifically for the pilot:

**File**: `prompts/configs/pilot_tilesize.json`

```json
{
  "version": "pilot_tilesize",
  "description": "Tile size calibration pilot. Canonical library only.",
  "purpose": "pre-registration_calibration",
  "model": "gemini-3-flash",
  "instruction_file": "detect_brief-text-image.md",
  "temperature": 1.0,
  "max_output_tokens": 8192,
  "examples": [
    {"path": "examples/canonical_burial_mound.png", "label": "Positive: Burial Mound (Kurgan)", "category": "canonical_positive"},
    {"path": "examples/canonical_settlement_mound.png", "label": "Positive: Settlement Mound", "category": "canonical_positive"},
    {"path": "examples/canonical_triangulation_mound.png", "label": "Positive: Triangulation Point ON Mound", "category": "canonical_positive"},
    {"path": "examples/canonical_benchmark_mound.png", "label": "Positive: Benchmark ON Mound", "category": "canonical_positive"},
    {"path": "examples/canonical_standalone_triangulation.png", "label": "Negative: Triangulation Point ALONE (no mound)", "category": "canonical_negative"},
    {"path": "examples/canonical_standalone_benchmark.png", "label": "Negative: Benchmark ALONE (no mound)", "category": "canonical_negative"},
    {"path": "examples/null_tile_01.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
    {"path": "examples/null_tile_02.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
    {"path": "examples/null_tile_03.png", "label": "Negative: Empty tile (no mounds)", "category": "null"}
  ],
  "library_composition": {
    "canon_positive": 4,
    "canon_negative": 2,
    "hard_positive": 0,
    "empirical_hard_negative": 0,
    "null": 3,
    "total": 9
  }
}
```

**Note**: Verify the actual paths to canonical example images match what exists in the repository.

---

## Phase 4: Run Detection

### 4.1 Execute Detection Passes

For each tile size, run K=5 independent detection passes on all 15 tiles.

**Parameters**:
- Config: `pilot_tilesize.json`
- Temperature: 1.0
- Passes: 5
- Model: gemini-3-flash

**Execution order** (to interleave and avoid systematic effects):

Option A (by pass):
```
Pass 1: all 15 tiles at 384, then 512, then 1024
Pass 2: all 15 tiles at 384, then 512, then 1024
... (repeat for passes 3-5)
```

Option B (by tile):
```
Tile 1: 5 passes at 384, then 5 passes at 512, then 5 passes at 1024
Tile 2: ...
```

Either approach is acceptable. Document which was used.

**API calls**: 15 tiles × 5 passes × 3 sizes = **225 calls**

**Output**: Raw API responses saved to:
- `outputs/pilot/384/responses/`
- `outputs/pilot/512/responses/`
- `outputs/pilot/1024/responses/`

### 4.2 Parse Responses

Parse all API responses to extract detections:
- `outputs/pilot/384/detections.json`
- `outputs/pilot/512/detections.json`
- `outputs/pilot/1024/detections.json`

Each file maps: tile_id → pass_number → list of detections

---

## Phase 5: Analysis

### 5.1 Compute Voting Results

For each tile size, compute voted detections at all thresholds:

| Threshold | Meaning |
|-----------|---------|
| 1/5 | Detection in ≥1 pass |
| 2/5 | Detection in ≥2 passes |
| 3/5 | Detection in ≥3 passes (majority) |
| 4/5 | Detection in ≥4 passes |
| 5/5 | Detection in all 5 passes |

Use 20m spatial clustering for vote aggregation (consistent with main experiment).

### 5.2 Compute Metrics

For each (tile_size, threshold) combination, compute:
- Precision
- Recall
- F1
- True Positives, False Positives, False Negatives

**Output**: `outputs/pilot/pilot_results.json`

```json
{
  "pilot_date": "YYYY-MM-DD",
  "tiles_tested": 15,
  "passes_per_tile": 5,
  "results": {
    "384": {
      "1_of_5": {"precision": X, "recall": X, "f1": X, "tp": N, "fp": N, "fn": N},
      "2_of_5": {"precision": X, "recall": X, "f1": X, "tp": N, "fp": N, "fn": N},
      "3_of_5": {...},
      "4_of_5": {...},
      "5_of_5": {...}
    },
    "512": {...},
    "1024": {...}
  }
}
```

### 5.3 Generate Summary Table

Create a markdown summary:

**File**: `outputs/pilot/pilot_summary.md`

```markdown
# Tile Size Pilot Results

**Date**: YYYY-MM-DD
**Tiles**: 15 (5 empty, 5 sparse, 5 dense)
**Passes**: K=5
**Library**: Canonical (9 examples)

## F1 by Tile Size and Voting Threshold

| Tile Size | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | Best |
|-----------|-----|-----|-----|-----|-----|------|
| 384×384   |     |     |     |     |     |      |
| 512×512   |     |     |     |     |     |      |
| 1024×1024 |     |     |     |     |     |      |

## Precision/Recall at 2/5 Threshold

| Tile Size | Precision | Recall | F1 |
|-----------|-----------|--------|-----|
| 384×384   |           |        |     |
| 512×512   |           |        |     |
| 1024×1024 |           |        |     |

## Decision

[To be filled after analysis]

Based on decision rules:
- 384 vs 512: [outcome]
- 1024 vs 512: [outcome]

**Selected tile size for main experiment**: XXX
```

---

## Phase 6: Decision Application

### 6.1 Apply Decision Rules

| Comparison | Condition | Action |
|------------|-----------|--------|
| 384 vs 512 | 384px F1 ≥ 0.05 better at 2/5 | **Switch to 384px** |
| 384 vs 512 | Within 0.03 | Stay at 512px |
| 384 vs 512 | 384px 0.03-0.05 better | Judgment call — document reasoning |
| 1024 vs 512 | 1024px F1 ≥ 0.10 worse | Confirms literature; deprioritize H11 |
| 1024 vs 512 | Within 0.05 | Investigate — context may help this task |

### 6.2 Document Outcome

Update `outputs/pilot/pilot_summary.md` with:
1. Which decision rule was triggered
2. Selected tile size for main experiment
3. Any surprising findings or notes

### 6.3 If Tile Size Changes

If switching from 512×512 to a different size:

1. **Regenerate training tiles** at new size (20 tiles)
2. **Regenerate holdout tiles** at new size (60 tiles)
3. **Update ground truth** for new tile boundaries
4. **Update preregistration** to reflect the new tile size as a fixed parameter
5. **Update canonical example images** if they need to match tile size (probably not — they're symbol crops, not full tiles)

---

## Verification Checklist

Before starting:
- [ ] Reserve set (281 tiles) is accessible
- [ ] Canonical example images exist at expected paths
- [ ] Ground truth master file is available
- [ ] Detection scripts support variable tile sizes

After Phase 1 (Selection):
- [ ] 15 tiles selected with documented seed
- [ ] Stratification documented (empty/sparse/dense counts)
- [ ] Tiles added to exclusion list

After Phase 2 (Generation):
- [ ] Tiles generated at all 3 sizes
- [ ] Ground truth regenerated for each size
- [ ] Edge cases documented

After Phase 4 (Detection):
- [ ] 225 API calls completed
- [ ] All responses saved and parsed

After Phase 5 (Analysis):
- [ ] Metrics computed for all (size, threshold) combinations
- [ ] Summary table generated

After Phase 6 (Decision):
- [ ] Decision rule applied and documented
- [ ] Tile size for main experiment confirmed
- [ ] If changed: regeneration tasks completed

---

## File Outputs Summary

| File | Purpose |
|------|---------|
| `inputs/pilot_tile_manifest.json` | Selected tile IDs |
| `inputs/pilot_selection_metadata.json` | Seed, date, stratification |
| `inputs/excluded_tiles.json` | Permanent exclusion record |
| `inputs/pilot_tiles/{384,512,1024}/` | Generated tiles |
| `inputs/pilot_tiles/{384,512,1024}/ground_truth.json` | Per-size ground truth |
| `prompts/configs/pilot_tilesize.json` | Detection configuration |
| `outputs/pilot/{384,512,1024}/responses/` | Raw API responses |
| `outputs/pilot/{384,512,1024}/detections.json` | Parsed detections |
| `outputs/pilot/pilot_results.json` | Computed metrics |
| `outputs/pilot/pilot_summary.md` | Human-readable summary |
