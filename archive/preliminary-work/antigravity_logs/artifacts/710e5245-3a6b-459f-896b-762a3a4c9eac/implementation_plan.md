# Implementation Plan - Phase 5: Negative Visual Library

## Goal
Eliminate "stubborn" False Positives (like the one reported) by explicitly showing them to the model as "Negative Examples" (What NOT to detect).

## Proposed Changes

### 1. Build Negative Library
- Add `uploaded_image_1765771272200.png` as `references/ref_negative_1.png`.

### 2. Update Detection Logic
#### [MODIFY] [3_detect_mounds_visual.py](file:///home/shawn/Code/map-reader-llm/scripts/3_detect_mounds_visual.py)
#### [NEW] [evaluate_full_run.py](file:///home/shawn/Code/map-reader-llm/scripts/evaluate_full_run.py)

## Semantic Versioning Strategy (Proposed)
To resolve versioning ambiguity, we will enforce the following structure:

### 1. Prompt Versions (The "Logic")
We will separate the Prompt Logic (System Text + Few-Shot Examples) into explicit folders `prompts/versions/`.
*   **V3.0 (Initial):** `prompts/versions/v3.0_legend_only.md` (Legend examples only).
*   **V3.1 (Baseline):** `prompts/versions/v3.1_balanced_6shot.md` (3 Pos / 3 Neg).
    *   *Provenance:* Phase 9. High Accuracy (F1 0.89).
*   **V3.2 (Experimental):** `prompts/versions/v3.2_refined_13shot.md` (13 Examples).
    *   *Provenance:* Phase 10/12. Current "Pro" logic.

*Note: Since images are dynamic, we may implement `scripts/prompt_config.py` to define the shot lists for each version, rather than hardcoding.*

### 2. Output Standard
All outputs (Results and Errors) must include the version tag:
*   `detections-v3.1-flash-...`
*   `detections-v3.2-pro-...`
*   `errors-v3.2-pro.geojson`

### 3. Repository Structure
```
repo/
├── prompts/
│   ├── active/ -> symlink to current version
│   ├── versions/
│   │   ├── v3.0_basic.json (Config for shots)
│   │   ├── v3.1_baseline.json
│   │   └── v3.2_experimental.json
│   └── text/
│       └── v3_system_instruction.md (Shared text)
├── scripts/
│   ├── detect_mounds.py (Main Runner, accepts --version arg)
│   └── ...
└── outputs/results/
    ├── v3.1_baseline/
    └── v3.2_experimental/
```

### 4. Metadata & Reproducibility (Scientific Logging)
To satisfy research standards, **every** execution will generate two files:
1.  `results/v3.1/.../detections.geojson` (The data)
2.  `results/v3.1/.../detections.meta.json` (The "Black Box" flight recorder)

**Metadata Schema:**
```json
{
  "run_id": "uuid-v4",
  "timestamp": {
    "start": "2025-12-18T09:00:00Z",
    "end": "2025-12-18T09:15:00Z",
    "duration_seconds": 900.5
  },
  "environment": {
    "git_commit": "abc1234",
    "script_version": "scripts/detect_mounds_v3.py"
  },
  "configuration": {
    "prompt_version": "v3.1_baseline",
    "model_name": "gemini-3-pro-preview",
    "parameters": {"temperature": 0.1, ...},
    "prompt_hash": "sha256_of_system_text"
  },
  "execution_stats": {
    "tiles_processed": 20,
    "tiles_failed": 0,
    "api_retries": 5
  },
  "usage_stats": {
    "total_input_tokens": 150000,
    "total_output_tokens": 5000
  },
  "results_summary": {
    "total_detections": 15,
    "class_counts": {"burial_mound": 12, "benchmark": 3}
  }
}
```

#### [MODIFY] [detect_mounds_v3.py](file:///home/shawn/Code/map-reader-llm/scripts/detect_mounds_v3.py)
- Integrate `RunMetadata` class to track stats.
- Capture `usage_metadata` from Gemini response.
- Save `.meta.json` on completion.:
- Add loading logic for `ref_negative_*.png`.
- Append a new section to the prompt:
    ```
    --- NEGATIVE EXAMPLES (DO NOT DETECT) ---
    The following images are NOT mounds. They are false positives (e.g. random noise, labels).
    IGNORE anything that looks like these.
    [Negative Image 1]
    ...
    ```

## Q&A: Bounding Boxes vs Crops?
- **Recommendation**: Use **Clean Crops** (like the ones you uploaded).
- **Reason**: We want the model to learn the *texture and shape* of the false positive object itself. Drawing a bounding box *on* the reference image introduces an artificial visual feature (the line of the box) that isn't present in the real map, which can confuse the matching process.

## User Review Required
> [!TIP]
> This completes the "Few-Shot" loop: Positive Examples for Recall, Negative Examples for Precision.
