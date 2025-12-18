# Archive Scripts Renaming Plan

**Goal**: Rationalize naming in `archive/scripts/` to be consistent with the Era-based structure of `archive/results/`.

## Proposed Renaming Scheme

We will prefix scripts with their Era (`v3.0`, `v2`, `v2.5`) or `util` for generic helpers.

### V3 Era (Visual Prompting)
| Original | New |
| :--- | :--- |
| `run_rakovski_full.py` | `v3.0_run_rakovski-full.py` |
| `run_robust.py` | `v3.0_run_robust-checks.py` |
| `test_v3_fixed_set.py` | `v3.0_test_fixed-set.py` |
| `test_v3_random5.py` | `v3.0_test_random5.py` |
| `run_random_extraction.py` | `v3.0_run_random-extraction.py` |

### V2 Era (Text-Based)
| Original | New |
| :--- | :--- |
| `2_detect_mounds.py` | `v2_runner_generic.py` |
| `2_detect_mounds_v2.5_baseline.py` | `v2.5_runner_baseline.py` |
| `test_detection_v2.py` | `v2_test_detection.py` |
| `retest_validation_tiles.py` | `v2_test_validation-tiles.py` |

### Utilities / Early Experiments
| Original | New |
| :--- | :--- |
| `analyze_legend.py` | `util_analyze_legend.py` |
| `convert_to_geojson.py` | `util_convert_txt-to-geojson.py` |
| `debug_detection.py` | `util_debug_detection.py` |
| `debug_gemini3.py` | `util_debug_gemini-connection.py` |
| `generate_adhoc_bboxes.py` | `util_generate_adhoc_bboxes.py` |
| `generate_missing_bounds.py` | `util_generate_missing_bounds.py` |
| `list_models_test.py` | `util_test_model-list.py` |

## Execution
1.  Apply renames using `mv`.
2.  Update `archive/ARCHIVE_MANIFEST.md` to include a Scripts table.

## 5. Manifest Update (Scripts)
We will add a "Scripts" section to `ARCHIVE_MANIFEST.md` to map these.

## 6. Update Input Paths

**Goal**: Align codebase with new `inputs/rasters` and `inputs/vectors` structure.

### Configuration
*   Modify `config.py` to define:
    *   `INPUTS_DIR = BASE_DIR / "inputs"` (Keep generic)
    *   `RASTERS_DIR = INPUTS_DIR / "rasters"` (New)
    *   `VECTORS_DIR = INPUTS_DIR / "vectors"` (New)

### Script Updates
*   **`scripts/preprocess_tiling.py`**: Update `tiling_pipeline()` to look for .tif files in `RASTERS_DIR` instead of `INPUTS_DIR`.
*   **`inputs/README.md`**: Update documentation to reflect the new hierarchy.

### Verification
*   Dry run `preprocess_tiling.py` (or check path resolution) to ensure it finds the rasters.

## 7. Renaming Calibration Inputs

**Goal**: Rename `inputs/calibration-run/` to `inputs/prompt_examples/` and give its contents descriptive filenames.

### Directory Structure
*   `inputs/calibration-run/` -> `inputs/prompt_examples/`

### File Renaming
*   `false-positives/Screenshot from 2025-12...png` -> `fp_blob_intersecting_contour_{n}.png` (Descriptive)
*   `false-negatives/Screenshot...` -> `fn_obscured_mound_{n}.png`

### Configuration Updates
*   Check `prompts/versions/*.json` for any hardcoded paths to these files. (Already checked: 'calibration-run' not found in config text, confirming they might only be used manually or in future work).
*   If they are **unused** in code, this is purely a file organization task.

## 8. Archiving Prompt Examples

**Goal**: Move the unused specific benchmark images to the archive.

### Operations
1.  Move `inputs/prompt_examples/` -> `archive/prompt_examples/`.
2.  Update `inputs/README.md` to remove the reference.
3.  Create `archive/prompt_examples/README.md`.
4.  Update `ARCHIVE_MANIFEST.md` to include this new section.


## 9. Standardize Target Manifest (Phase 2)

**Goal**: Establish a standard sets of tiles for benchmarking (`target_tiles_manifest.json`) and ensure it's tracked in metadata.

### 1. Rename Concept
*   `calibration_manifest.json` -> `target_tiles_manifest.json` (General purpose)

### 2. Update `scripts/4_detect_mounds_batch.py`
*   Current args: `--config` (required)
*   **New arg**: `--manifest` (optional) -> Path to a JSON list of tile filenames (e.g., `["tile1.png", "tile2.png"]`).
*   **Logic**:
    *   If `--manifest` is provided: Only process tiles present in that list.
    *   If NOT provided: Process all tiles in `TILES_DIR`.
*   **Metadata**:
    *   Add `target_manifest` field to `.meta.json`.
    *   Store the *filename* of the manifest (if used) and key characteristics (length, hash).

### 3. Generate Manifest
*   Create `inputs/target_tiles_manifest.json` from the verified V3 Baseline (20 stratified tiles).

## 10. Refactor Input Directory Structure

**Goal**: Centralize all analysis inputs (tiles, references, rasters, vectors) into the `inputs/` directory.

### Steps
1.  **Move Tiles**: `mv outputs/tiles/ inputs/tiles/`
2.  **Move References**: `mv references/ inputs/references/`
3.  **Update Config (`config.py`)**:
    *   `TILES_DIR = INPUTS_DIR / "tiles"`
    *   `REFERENCES_DIR = INPUTS_DIR / "references"`
4.  **Update Script (`scripts/4_detect_mounds_batch.py`)**:
    *   Update `refs_dir` variable to use `config.REFERENCES_DIR`.
5.  **Update Documentation**:
    *   `scripts/preprocess_tiling.py` (docstrings)
    *   `scripts/README.md`
    *   `README.md` (Setup instructions)

## 11. Refactor Outputs Directory

**Goal**: Clean up `outputs/` to remove legacy "phase" folders and ensure a strictly versioned structure in `outputs/results/`.

### 1. Analysis of `outputs/`
*   Found `outputs/phase12_gemini3pro_errors/` (Legacy V3 analysis).
    *   Files: `errors_fn.geojson`, `errors_fp.geojson`.
    *   Action: Move to `archive/results/v3_visual_prototypes/` with clearer names.

### 2. Execution Steps
*   `mv outputs/phase12_gemini3pro_errors/errors_fn.geojson archive/results/v3_visual_prototypes/v3.0_analysis_error-analysis_initial_fn.geojson`
*   `mv outputs/phase12_gemini3pro_errors/errors_fp.geojson archive/results/v3_visual_prototypes/v3.0_analysis_error-analysis_initial_fp.geojson`
*   `rmdir outputs/phase12_gemini3pro_errors`
*   Verify `outputs/results/` only contains version-stamped folders (e.g., `v3.1_baseline`).

## 12. Refactor Scripts Directory

**Goal**: Consolidate `scripts/archive/` into `archive/scripts/` and migrate loose, non-core scripts to `archive/scripts/` with `util_` or versioned prefixes.

### 1. Source Analysis
*   `scripts/archive/`: Contains `2_detect_mounds_v.2.0.py` etc. -> Move to `archive/scripts/` (V2 era).
*   `scripts/`: Contains loose utilities like `debug_edge_exclusion.py`, `retest_green_tile.py`. -> Move to `archive/scripts/` with `v3.x_debug_` prefix.

### 2. Core Scripts (To Keep in `scripts/`)
*   `preprocess_tiling.py` (Pipeline Step 1)
*   `4_detect_mounds_batch.py` (Pipeline Step 2 - Inference)
*   `3_georeference_and_visualize.py` (Pipeline Step 3 - Post-processing)
*   `run_v3.1_benchmark.py` (Phase 2 Runner - Maybe keep?)

### 3. Migration Plan (Detailed)

#### From `scripts/archive/` to `archive/scripts/`
*   `3_detect_mounds_visual.py` -> `v3.0_prototype_detect_mounds_visual.py`
*   `3_detect_mounds_visual_v3_gemini3pro_failed.py` -> `v3.0_prototype_detect_mounds_broken.py`
*   `benchmark_calibration_v3.py` -> `v3.0_benchmark_calibration.py`
*   `supplement_lesovo.py` -> `v3.0_adhoc_supplement_lesovo.py`
*   **Action**: Remove `scripts/archive/` after move.

#### From `scripts/` to `archive/scripts/`
*   `analyze_partial_results.py` -> `util_analyze_partial.py`
*   `debug_edge_exclusion.py` -> `util_debug_edge_exclusion.py`
*   `debug_model_selection.py` -> `util_debug_model_selection.py`
*   `evaluate_full_run.py` -> `util_evaluate_full_run.py`
*   `evaluate_results.py` -> `util_evaluate_results.py`
*   `evaluate_single_tile_verification.py` -> `util_evaluate_single_tile.py`
*   `evaluate_stratified.py` -> `util_evaluate_stratified.py`
*   `extract_calibration_from_full.py` -> `util_extract_calibration.py`
*   `extract_errors.py` -> `util_extract_errors.py`
*   `extract_references.py` -> `util_extract_references.py`
*   `generate_tile_index.py` -> `util_generate_tile_index.py`
*   `reconstruct_bounds.py` -> `util_reconstruct_bounds.py`
*   `retest_green_tile.py` -> `v3.x_debug_retest_green_tile.py`
*   `run_calibration.py` -> `v3.0_run_calibration_legacy.py`
*   `run_missing_calibration.py` -> `v3.0_run_missing_calibration.py`
*   `select_calibration_tiles.py` -> `util_select_calibration_tiles.py`
*   `split_references.py` -> `util_split_references.py`
*   `visualize_fp_crops.py` -> `util_visualize_fp_crops.py`

#### Files Remaining in `scripts/` (The Core)
1.  `preprocess_tiling.py`
2.  `4_detect_mounds_batch.py`
3.  `3_georeference_and_visualize.py`
4.  `run_v3.1_benchmark.py` (Active Phase 2 Tool)

### 4. Updates
*   Update `ARCHIVE_MANIFEST.md`.

## 13. Implement Methodological Records

**Goal**: Preserve AI interaction logs (`conversations/*.pb`) and artifacts (`brain/**/*.md`) for open science transparency.

### 1. Structure
*   `methodology/logs/`: Destination directory.
    *   `methodology/logs/conversations/*.pb`: Raw chat logs.
    *   `methodology/logs/artifacts/<UUID>/*.md`: Plan and Task artifacts.

### 2. Script: `scripts/archive_methodology.py`
*   Input: `~/.gemini/antigravity` (auto-detected).
*   Logic:
    *   Find all `.pb` files in `conversations/`.
    *   Copy to `methodology/logs/conversations/`.
    *   Find corresponding `brain/<UUID>/` folders.
    *   Copy contents to `methodology/logs/artifacts/<UUID>/`.
*   Safety: Do not overwrite existing unless changed? Or simple timestamped sync? (Start with rsync-like copy).

### 3. Execution
*   Develop script.
*   Run script once to populate.
*   Update README with instructions on how to use it.





