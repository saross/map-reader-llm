# Archive Manifest & Traceability Log

This document maps historical result files to the specific prompt versions used to generate them. Use this for paper reproducibility and historical analysis.

## V3: Visual Prompting Era (Dec 2025 - Present)
**System Instruction**: `prompts/text/v3.0_system_instruction.md` (Stable since Dec 15, 2025)

| Result File | Prompt / Config | Notes |
| :--- | :--- | :--- |
| `archive/results/detections-2025-12-11-3-pro.geojson` | Early V3 Prototype | Run before V3 prompt was committed. Logic identical to V3.0. |
| `archive/results/detections-calibration-stratified_v1.geojson` | V3.0 Baseline | The first major calibration run using V3. |
| `archive/results/detections-rakovski-full-v3-robust.geojson` | V3.0 Baseline | Full tiled run of Rakovski map. |
| `archive/detections-v3.2_experimental-gemini3pro-2025-12-17-PARTIAL.geojson` | V3.2 Experimental | Early test of V3.2 logic. |

## V2: Text-Based Prompting Era (Nov 2025)
**Prompts Location**: `archive/prompts/`

| Result File | Prompt File | Notes |
| :--- | :--- | :--- |
| `archive/results/detections-v2.4-retest.geojson` | `V2.4_mound_detection_prompt.md` | Testing "Label Confusion" fix. |
| `archive/results/test_v2.5_*.geojson` | `V2.5_mound_detection_prompt.md` | Testing "Geometric Regularity". |
| `archive/results/test_v2.0_*.geojson` | `V2_mound_detection_prompt.md` | Initial baseline. |

## V1: Initial Experiments
| Result File | Prompt File | Notes |
| :--- | :--- | :--- |
| `archive/results/calibration_manifest_v1.json` | `V1_mound_detection_prompt.md` | Early experimentation. |
