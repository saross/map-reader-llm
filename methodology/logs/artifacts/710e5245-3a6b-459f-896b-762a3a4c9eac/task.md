# Task: Verify Mound Detection V2.5

- [x] Integrate V2.5 Prompt into `2_detect_mounds.py` <!-- id: 0 -->
- [x] Run detection on sample tiles <!-- id: 1 -->
- [x] Verify results against false positive/negative cases <!-- id: 2 -->
- [/] Refine prompt to V2.6 (Targeting Label Confusion) <!-- id: 3 -->
    - [x] Draft V2.6 Prompt <!-- id: 3.1 -->
    - [x] Update `2_detect_mounds.py` <!-- id: 3.2 -->
    - [x] Verify V2.6 on mislabeled examples (numbers) <!-- id: 3.3 -->
    - [x] FAIL: V2.6 increased detected numbers. Reverted to V2.5. <!-- id: 3.4 -->
- [ ] Finalize V2.5 as the current best standard <!-- id: 4 -->

# Phase 3: Visual Detection
- [ ] Extract reference symbols from `legend.tif` <!-- id: 5 -->
    - [x] Create `extract_references.py` <!-- id: 5.1 -->
    - [x] Run extraction and verify crops <!-- id: 5.2 -->
- [ ] Implement Visual Prompting <!-- id: 6 -->
    - [x] Create `prompts/V3_visual_mound_detection.md` <!-- id: 6.1 -->
    - [x] Create `3_detect_mounds_visual.py` (preserving V2.5) <!-- id: 6.2 -->
- [x] Verify V3 on Challenging Tile <!-- id: 7 -->
- [x] Document Visual Prompting results in `working_notes.md` <!-- id: 8 -->
- [x] Preserve V2.5 pipeline as `scripts/2_detect_mounds_v2.5_baseline.py` <!-- id: 9 -->
- [x] Run V3 on 5 random Rakovski tiles <!-- id: 10 -->

# Phase 4: Few-Shot Library
- [x] Add False Negative to `references/` <!-- id: 11 -->
- [x] Update `3_detect_mounds_visual.py` to support multiple variants <!-- id: 12 -->
- [x] Verify fix on the tile containing the FN <!-- id: 13 -->

# Phase 5: Negative Examples
- [x] Add Negative Example to `references/` <!-- id: 14 -->
- [x] Update `3_detect_mounds_visual.py` to support negative examples <!-- id: 15 -->
- [x] Document Few-Shot findings in `working_notes.md` <!-- id: 17 -->
- [x] Commit and Push Changes <!-- id: 18 -->
- [ ] Verify reduction in FP on relevant tile <!-- id: 16 -->

# Phase 6: Full Run (Robustness)
- [x] Implement robust API retries (Exponential Backoff) <!-- id: 19 -->
- [x] Execute Full Run on Rakovski Map <!-- id: 20 -->

# Phase 7: Automated Evaluation
- [x] Split reference GeoJSON by Map <!-- id: 21 -->
- [x] Create `evaluate_results.py` (Recall/Precision/F1) <!-- id: 22 -->
- [x] Run Evaluation on Rakovski Results <!-- id: 23 -->

# Phase 8: Multi-Map Calibration (Stratified)
- [x] Create Stratified Manifest (20 tiles) <!-- id: 24 -->
- [x] Run Calibration on Stratified Set <!-- id: 25 -->
- [x] Evaluate Calibration Set <!-- id: 26 -->
- [ ] Refine Few-Shot Library (Phase 10) <!-- id: 28 -->
    - [x] Select diverse FP/FN examples <!-- id: 29 -->
    - [x] Add examples to prompts/V3_visual_mound_detection.md <!-- id: 30 -->
- [x] Verify V3 on Challenging Tile <!-- id: 7 -->
- [x] Full Production Run (Phase 12) <!-- id: 31 -->
    - [x] Archive previous results <!-- id: 32 -->
    - [x] Run detection on ALL tiles (FAILED: Regression/RateLimit) <!-- id: 33 -->
    - [x] Evaluate full production results (Partial Analysis) <!-- id: 34 -->
- [x] **Infrastructure: Semantic Versioning** <!-- id: 39 -->
    - [x] Create directory structure (prompts/versions) <!-- id: 40 -->
    - [x] Create JSON Configs (V3.0, V3.1, V3.2) <!-- id: 41 -->
    - [x] Standardize Script (detect_mounds_v3.py) <!-- id: 42 -->
    - [x] Verify V3.1 Baseline works <!-- id: 43 -->
    - [x] Verify V3.2 Experimental works <!-- id: 44 -->
- [ ] **REQUIREMENT: Use Gemini 3 Pro ONLY** <!-- id: 35 -->
    - [ ] Restore config.py to gemini-3-pro-preview <!-- id: 36 -->
    - [ ] Restore 13-shot prompt (V3) <!-- id: 37 -->
    - [ ] Await Model Availability / Fix Rate Limits <!-- id: 38 -->
