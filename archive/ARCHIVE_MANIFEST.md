# Archive Manifest & Traceability Log

This document maps historical result files to the specific prompt versions used to generate them. Use this for paper reproducibility and historical analysis.

## V3: Visual Prompting Era (Dec 2025 - Present)
**System Instruction**: `prompts/text/v3.0_system_instruction.md` (Stable since Dec 15, 2025)
**Location**: `archive/results/v3_visual_prototypes/`

### Baseline Results
| Result File | Description |
| :--- | :--- |
| `v3.0_baseline_detections_calibration-stratified-20.geojson` | **Major Baseline**: The stratified 20-tile calibration set. |
| `v3.0_baseline_bounds_calibration-stratified-20.geojson` | Bounds for the calibration set. |
| `v3.0_baseline_detections_rakovski-full_robust.geojson` | **Full Map Run**: Complete tiled run of Rakovski using robust settings. |
| `v3.0_baseline_detections_rakovski-random5.geojson` | Snapshot: Random 5 tiles from Rakovski. |
| `v3.0_baseline_detections_rakovski-random5_retry.geojson` | Retry of the random 5 sample. |

### Prototypes & Experiments
| Result File | Description |
| :--- | :--- |
| `v3.0_prototype_detections_rakovski-full.geojson` | Early prototype run (Dec 11). |
| `v3.0_prototype_mounds_rakovski-full.geojson` | Post-processed output of the prototype. |
| `v3.2_experimental_detections_partial_run.geojson` | V3.2 Early Test (Partial). |

### Debug & Analysis
| Result File | Description |
| :--- | :--- |
| `v3.0_analysis_errors_fn.geojson` | False Negatives analysis file. |
| `v3.0_analysis_errors_fp.geojson` | False Positives analysis file. |
| `v3.0_analysis_tile-index.geojson` | Geospatial index of used tiles. |
| `v3.0_debug_detections_single-tile.geojson` | Single tile debug output. |
| `v3.x_debug_detections_rakovski-random1.geojson` | Debug: 1 random tile. |
| `v3.x_debug_detections_verification-green.geojson` | Debug: Verification of "green tile" issue. |

## V2: Text-Based Prompting Era (Nov 2025)
**Prompts Location**: `archive/prompts/`
**Results Location**: `archive/results/v2_text_based/`

| Result File | Prompt File | Notes |
| :--- | :--- | :--- |
| `v2.4_label-fix_detections_retest.geojson` | `V2.4_mound_detection_prompt.md` | Testing "Label Confusion". |
| `v2.6_debug_detections_single-tile.geojson` | `V2.6_mound_detection_prompt.md` | Debug run for V2.6. |
| `v2.5_geometric_detections_tile_*.geojson` | `V2.5_mound_detection_prompt.md` | Testing "Geometric Regularity". |
| `v2.0_baseline_detections_tile_*.geojson` | `V2_mound_detection_prompt.md` | Initial baseline tiles. |

## V1: Initial Experiments
**Results Location**: `archive/results/v1_initial_experiments/`

| Result File | Prompt File | Notes |
| :--- | :--- | :--- |
| `v1.0_manifest_calibration.json` | `V1_mound_detection_prompt.md` | Early experimentation file list. |
| `v1.x_results_gemini25-flash_experimental/` | `V1_mound_detection_prompt.md` | Experimental run using Gemini Flash 2.5 with V1 logic. |

## Legacy Scripts
**Location**: `archive/scripts/`

### V3 Era (Visual)
*   `v3.0_run_rakovski-full.py`: Full tiled run script for Rakovski map.
*   `v3.0_run_robust-checks.py`: Robustness testing script (re-tries).
*   `v3.0_test_fixed-set.py`: Testing on a fixed set of tiles.
*   `v3.0_test_random5.py`: Testing on a random 5 tiles.
*   `v3.0_run_random-extraction.py`: Random extraction logic.

### V2 Era (Text-Based)
*   `v2_runner_generic.py`: Generic runner for V2 prompts.
*   `v2.5_runner_baseline.py`: Baseline runner for V2.5.
*   `v2_test_detection.py`: Detection test script.
*   `v2_test_validation-tiles.py`: Validation script.

### Utilities
*   `util_*.py`: Various helper scripts (legend analysis, geojson conversion, debugging).

## Prompt Development Assets
**Location**: `archive/prompt_example_images/`

Collection of screenshots and crops used for tuning the V3 prompt (False Positives, False Negatives, Benchmarks).


