# Protocol Errata

**Purpose**: Record of corrections, clarifications, and deviations from the preregistered protocol identified during execution. This document is maintained for transparency and reproducibility.

**Associated preregistration**: `preregistration.md` v4.7 (2026-01-31)

**See also**: `osf/execution-checklist.md` for execution tracking

---

## Classification

- **Correction**: Fix to implementation that brings it into alignment with the preregistered protocol (no protocol change)
- **Clarification**: Interpretation of an ambiguous point in the preregistration
- **Deviation**: Substantive change from the preregistered protocol (requires justification)

---

## Entries

### E1: Stale version/date in OSF companion README

| Field | Value |
|-------|-------|
| Date | 2026-01-31 |
| Type | Correction |
| Commit | `a9ed78b` |
| Impact | None (cosmetic) |

**Description**: The `osf/README.md` file contained a stale date (`2026-01-14`) that did not match the current preregistration version (v4.7, 2026-01-31). Updated to `2026-01-31` along with version alignment across all three OSF companion documents (`f037a9d`).

**Protocol impact**: None. These are companion metadata files, not the preregistration document itself.

---

### E2: Missing execution fields in Phase 1 config

| Field | Value |
|-------|-------|
| Date | 2026-02-01 |
| Type | Correction |
| File | `prompts/configs/library_pure-positive-canon.json` |
| Impact | Would have prevented execution or produced non-preregistered results |

**Description**: The library config file used by Phase 1 (`run_phase1.py`) was missing five execution fields required by the batch detection script (`4_detect_mounds_batch.py`):

| Field | Missing default | Preregistered value |
|-------|----------------|---------------------|
| `model` | `None` (crash) | `gemini-3-flash` |
| `temperature` | `0.1` (wrong) | `1.0` |
| `instruction_file` | `v3.0_system_instruction.md` (doesn't exist) | `detect_image-only.md` |
| `thinking_level` | omitted | `minimal` |
| `max_output_tokens` | `8192` | `8192` |

**Root cause**: The library config files (`library_*.json`) were designed as examples-only compositions for use with `run_study.py`, which supplies execution parameters from its own `defaults` section. However, `run_phase1.py` passes the config directly to the batch script, requiring it to be self-contained.

**Fix**: Added the five fields to `library_pure-positive-canon.json`, matching the values specified in the preregistration (Section 8.9) and the pattern established in other detection configs (e.g., `detect_image-only.json`).

**Protocol impact**: None. The preregistered parameters are unchanged; this corrects the implementation to match them. Without the fix, either the script would crash (`model=None`, missing instruction file) or silently use wrong parameters (`temperature=0.1` instead of `1.0`).

---

### E3: SDK migration for Gemini ThinkingConfig support

| Field | Value |
|-------|-------|
| Date | 2026-02-01 |
| Type | Correction |
| File | `scripts/4_detect_mounds_batch.py` |
| Impact | Would have prevented all detections (100% failure rate) |

**Description**: The batch detection script used the deprecated `google-generativeai` SDK (v0.8.6) which does not support `ThinkingConfig`. All API calls failed with `Unknown field for GenerationConfig: thinkingLevel`. Migrated to the `google-genai` SDK (v1.56.0) which supports `types.ThinkingConfig` natively.

Additionally, the preregistered model name `gemini-3-flash` does not exist as an API endpoint — the current API name is `gemini-3-flash-preview`. Added model name resolution logic to map the preregistered name to the API-available variant.

**Protocol impact**: None. The model is the same (Gemini 3 Flash); the `-preview` suffix is Google's API naming convention for models not yet promoted to stable. All preregistered parameters (temperature, thinking level, instruction file) are unchanged.

---

### E4: Tile bounds generation Y-axis inversion

| Field | Value |
|-------|-------|
| Date | 2026-02-01 |
| Type | Correction |
| Files | `scripts/generate_tile_bounds.py`, `inputs/vectors/bounds/calibration_bounds.geojson` |
| Impact | Evaluation reported near-zero F1 due to misscoped references |

**Description**: The tile metadata format is `[minX, minY, pixel_size_x, pixel_size_y]` but the bounds generation script treated `metadata[1]` as `maxY`, computing `min_y = maxY - height`. This shifted all tile bounds one tile height south (~2565m), causing the F1 evaluation to scope ground truth references to incorrect spatial areas.

Additionally, the property names in the generated GeoJSON used `tile` and `map` instead of `tile_name` and `map_name` as expected by the evaluation pipeline.

**Fix**: Corrected the metadata interpretation (`metadata[1]` is `minY`), fixed property names, and regenerated `calibration_bounds.geojson` from the current calibration manifest.

**Protocol impact**: None. The preregistered evaluation methodology (20m spatial tolerance, Hungarian matching) is unchanged. This corrects the implementation infrastructure.

---

### E5: Evaluation pipeline reference path and column name bugs

| Field | Value |
|-------|-------|
| Date | 2026-02-01 |
| Type | Correction |
| Files | `scripts/lib_advanced_metrics.py`, `scripts/6_accuracy_report.py`, `scripts/analyse_study_effects.py` |
| Impact | Evaluation silently returned no references, reporting near-zero metrics |

**Description**: Three bugs in the evaluation pipeline:

1. Reference file loading looked in `inputs/vectors/` but files are in `inputs/vectors/references/`
2. Merged consensus GeoJSON uses `source_tiles` (list) but evaluation expected `source_tile` (string)
3. Same path issue in `analyse_study_effects.py`

**Protocol impact**: None. These are implementation bugs in evaluation infrastructure; the preregistered evaluation methodology is unchanged.

---

### E6: Pipeline contract validation (post-Phase 1 hardening)

| Field | Value |
|-------|-------|
| Date | 2026-02-01 |
| Type | Correction |
| Files | `scripts/lib_advanced_metrics.py`, `scripts/6_accuracy_report.py`, `scripts/generate_tile_bounds.py`, `tests/test_integration_pipeline_contracts.py` |
| Impact | Prevents recurrence of E4-E5 silent failures in Phase 2+ |

**Description**: Phase 1 execution exposed five cascading silent failures (E3-E5) where pipeline stages accepted bad input and produced valid-looking but incorrect output. Each bug was individually minor but chained together to produce misleading near-zero F1 scores. To prevent recurrence in Phase 2 (~15,000 API calls per sub-phase, ~$286 total), three categories of contract validation were added:

1. **Reference loading assertion** (`lib_advanced_metrics.py`, `6_accuracy_report.py`): `load_data()` now validates that the reference directory exists before attempting glob, logs directory contents on failure (elevated from `warning` to `error` level), and the accuracy report script fails loudly with a clear message when references are `None` or empty. Previously, a wrong reference path silently returned `None`, and evaluation reported near-zero metrics without error.

2. **Bounds metadata validation** (`generate_tile_bounds.py`): Added `validate_bounds()` function that spot-checks generated tile polygons against source metadata after generation. Verifies that polygon minY equals `metadata[1]` (catching Y-axis inversions like E4), and that polygon dimensions equal `TILE_SIZE * pixel_size`. Script exits with error if validation fails.

3. **Pipeline contract integration tests** (`tests/test_integration_pipeline_contracts.py`): Seven new pytest tests exercising stage-boundary contracts:
   - `source_tiles` list → `source_tile` string normalisation (E5b regression)
   - Reference loading fails loudly on missing/empty directory (E5a regression)
   - Bounds metadata correctly interprets `metadata[1]` as minY (E4 regression)
   - End-to-end merge → evaluate produces non-zero F1 on synthetic data
   - Vote counts and threshold filtering work correctly through the full path

**Protocol impact**: None. These are infrastructure hardening measures that do not change the preregistered methodology. The evaluation algorithms, spatial tolerance (20m), Hungarian matching, and statistical analysis are unchanged. The additions ensure that the same pipeline code will fail loudly rather than silently if similar interface bugs are introduced.

---

### E7: Evaluation reference scoping hardened against boundary effects

| Field | Value |
|-------|-------|
| Date | 2026-02-01 |
| Type | Correction |
| Files | `scripts/lib_advanced_metrics.py`, `scripts/6_accuracy_report.py`, `tests/test_integration_pipeline_contracts.py` |
| Impact | Preventive — no change to Phase 1 calibration metrics; prevents latent bug from manifesting in denser tile configurations (Phase 2+) |

**Description**: The evaluation pipeline scoped ground truth references against tile bounds using `union_all()` — merging all tile polygons into a single geometry and testing `intersects()`. This is semantically incorrect: references should be in scope only if they fall within at least one *individual* tile polygon, not within the union. With non-adjacent tiles, `union_all()` produces a MultiPolygon equivalent to per-tile checking, so the Phase 1 calibration results (5 scattered tiles per sheet) are unaffected. However, with denser tile configurations — such as the 60-tile validation set in Phase 2, which may include adjacent or overlapping tiles — the union could merge adjacent tile polygons and include references falling in inter-tile gaps.

A secondary issue in `6_accuracy_report.py` compounded the risk: references were buffered by 20m *before* the scoping check, meaning a reference 15m outside a tile boundary would have its 20m-radius buffer circle overlap the tile polygon, passing the scope check even though the reference point itself is outside.

Three locations were affected:

1. `lib_advanced_metrics.py:calculate_f1_internal()` — per-map `union_all()` for F1/precision/recall
2. `lib_advanced_metrics.py:error_taxonomy()` — global `union_all()` for FP/FN categorisation
3. `6_accuracy_report.py:validate_file()` — global `union_all()` on buffered references for FP/FN GeoJSON generation

**Fix**: Extracted a shared helper function `scope_references_to_tiles()` using `gpd.sjoin()` with `predicate='intersects'` against individual tile polygons, replacing all three `union_all()` sites. In `6_accuracy_report.py`, references are now scoped *unbuffered* against individual tiles, then only in-scope references are buffered for matching. Added 7 new integration tests covering: reference inside tile (in scope), reference in gap between tiles (excluded), reference outside all tiles (excluded), reference on tile boundary (in scope), empty inputs, and an end-to-end F1 test verifying that boundary-effect references don't inflate FN counts.

Additionally, the `spatial_tolerance_curve()` default buffer list was updated from `[10, 20, 30, 50]` to `[10, 20, 30, 40, 50]` to include the 40m tolerance level used in the two-dimensional failure ranking framework.

**Verification**: All 274 tests pass (267 existing + 7 new). Phase 1 calibration metrics are identical before and after the fix, confirming that the non-adjacent calibration tiles were unaffected by the union-based scoping.

**Protocol impact**: None. The preregistered evaluation methodology (20m spatial tolerance, Hungarian matching) is unchanged. The fix corrects a latent scoping bug that could produce inflated FN counts with denser tile configurations. Phase 1 results stand as reported.

---

### E8: Hard example crops extracted from full map GeoTIFFs

| Field | Value |
|-------|-------|
| Date | 2026-02-02 |
| Type | Clarification |
| Files | `inputs/examples/hard-positive/example_05-08_*.png`, `inputs/examples/hard-negative/example_11-14_*.png` |
| Impact | Crops may include map content from outside the detection tile boundary |

**Description**: The preregistration (§8.4.2) specifies hard example selection criteria but does not prescribe how example crops are spatially extracted. The implicit assumption is that crops come from the detection tiles shown to the model. Instead, all hard example crops (both hard positives and hard negatives) were extracted as 128×128 pixel regions from the full map GeoTIFFs (`inputs/rasters/*.tif`), not from the 512×512 detection tiles.

- **Hard positives**: Centred on the reference mound coordinate (the ground truth location of the missed symbol)
- **Hard negatives**: Centred on the FP detection coordinate (the location where the model placed its hallucinated detection)

Three options were evaluated (during hard positive extraction; the same rationale applies to hard negatives):

1. **Tile-bounded crops**: Crop from the detection tile, clamping to tile boundaries. When the reference point is near a tile edge, the target symbol is off-centre — in 2 of 4 cases, the symbol was within 60 pixels of a tile corner, producing asymmetric crops that could teach the VLM to associate mounds with image edges.
2. **Centred with padding**: Centre on the reference point, fill beyond-tile regions with black. Rejected because detection tiles already use black padding at map edges (`fill_value=0` in `preprocess_tiling.py`), so padding could be confused with genuine map features.
3. **Centred from full map** (selected): Crop directly from the source GeoTIFF, always centred on the target coordinate with full real map context. The relevant feature is at or near the crop centre, surrounded by real terrain in all directions.

**Rationale**: For hard positives, centring the target symbol disambiguates when multiple features appear in the same crop (observed in 2 of 4 hard positive examples). For hard negatives, centring on the hallucination location shows the model the map context that produced its false positive, focusing attention on the confusing feature. In both cases, the cross-tile-boundary content is from the same continuous map sheet and represents realistic context the model would see in adjacent tiles (which overlap by 64 pixels).

**Crop size** (128×128): Selected based on VLM few-shot reference sizing research. At ~5m/px, a 15–20px mound symbol occupies ~1–2.5% of a 128×128 crop — sufficient context without drowning the feature. VLM minimum input size recommendations (typically ≥300px) apply to analysis targets, not reference exemplars which are internally upscaled. The canonical positive legend crops are ~64px; hard examples need more context to show difficult real-world conditions. Crop size is flagged as a future exploratory variable (64, 128, 256, 512px OFAT experiment).

**Protocol impact**: Minor. Hard examples may show a few pixels of map content from outside the detection tile boundary. This is a conservative choice: it ensures the relevant feature is always centred and surrounded by realistic context, which better serves the reference exemplar's didactic purpose. The detection methodology (tile generation, model inference, evaluation) is unchanged.

---

### E9: Centre-pointing language added to detection prompts

| Field | Value |
|-------|-------|
| Date | 2026-02-02 |
| Type | Clarification |
| Files | All 11 `prompts/system-instructions/detect_*.md` files |
| Impact | Adds instructional text not specified in preregistration |

**Description**: A centre-pointing sentence was added to all detection prompt preambles:

> Each reference image is centred on the feature being labelled — the target symbol for Positive examples, the confusable feature for Negative examples.

This addresses an ambiguity in 128×128 hard example crops: when a crop centred on a confusable feature also contains a real mound at the periphery, the model needs to know which feature the label applies to. Without this, the model could interpret a "Negative" label as applying to a visible mound rather than the confusable non-mound at the centre.

The sentence is applied uniformly across all H5 conditions (Minimal, Terse, Verbose) to preserve factor orthogonality — centre-pointing is spatial orientation, distinct from H5's diagnostic text treatment.

**Protocol impact**: Minor. The preregistration specifies prompt structure and content at the section level but does not prescribe individual sentence-level phrasing. This adds a spatial orientation instruction that is consistent with the Stage 2 verifier's existing "candidate symbol in the centre" language. See Decision 12 in decisions-log.md.

---

### E10: 50m recognition/localisation threshold determined

| Field | Value |
|-------|-------|
| Date | 2026-02-02 |
| Type | Clarification |
| Files | `outputs/phase1-library/fp-fn-register.md`, `docs/methodology/preregistration/decisions-log.md` (Decision 11) |
| Impact | Determines which FNs qualify as hard positive candidates |

**Description**: The preregistration (§8.4.2) specifies that hard positive examples are drawn from recognition failures — false negatives where the model failed to detect a mound — rather than localisation errors where the model detected the mound but placed it inaccurately. The specific distance threshold separating these categories was left to empirical determination.

Analysis of the Phase 1 FN distance distribution revealed a distributional cliff between 30m and 50m: below 30m, FNs cluster tightly (clear localisation errors); above 50m, FNs are sparse and widely dispersed (clear recognition failures). The 30–50m range is ambiguous. A 50m threshold was selected as the boundary, yielding 9 recognition failures and 15 localisation failures from 24 total FNs.

**Protocol impact**: None. This is an empirical determination within the latitude granted by the preregistration. The threshold is documented with distributional evidence in Decision 11.

---

### E11: Scale-16 and Scale-32 library conditions capped

| Field | Value |
|-------|-------|
| Date | 2026-02-02 |
| Type | Clarification |
| Files | `prompts/configs/library_scale-16.json`, `prompts/configs/library_scale-32.json`, `docs/methodology/preregistration/hypothesis-tracking.md` |
| Impact | H8 conditions 6–7 deferred; scaling contrasts S2 and S3 deferred to post-H10 |

**Description**: The HP pool is structurally exhausted at 4 recognition failures (>50m threshold). Of 9 total recognition failures, 4 are selected for Scale-8, 3 are out-of-scope boundary artefacts, 1 is a newly discovered out-of-scope candidate (fid 489, outside all calibration tiles), and 1 is edge-truncated (fid 161). Zero recognition failures remain for library expansion.

Scale-16 requires 8 HP and Scale-32 requires 16 HP. Under the preregistered 1:1 HP:HN constraint, both conditions collapse to Scale-8. This activates the contingency anticipated at preregistration line 815: "If fewer than 16 distinct HPs or HNs are available, Scale-32 (and possibly Scale-16) will be capped at the maximum available while preserving 1:1 ratio."

Both config files are marked `"status": "deferred"` with empty example arrays. H8 contrasts C1–C3, S1, and B1 remain fully testable. Scaling contrasts S2 and S3 are deferred to post-H10 (calibration tile expansion).

**Protocol impact**: None. This is activation of a preregistered contingency path, not a deviation. See Decision 11 in decisions-log.md.

---

### E12: H9 image diversity runs as HN-diversity-only (HP frozen)

| Field | Value |
|-------|-------|
| Date | 2026-02-02 |
| Type | Clarification |
| Files | `docs/methodology/preregistration/hypothesis-tracking.md` |
| Impact | H9-C tests HN rotation only; HP diversity is untestable |

**Description**: H9 (diversity mechanisms) tests whether varying prompt components across voting passes improves consensus performance. For H9-C (image diversity), the preregistration envisions rotating both HP and HN examples across passes.

Due to HP pool exhaustion (E11), the HP channel is frozen: 4 slots, 4 examples, every HP appears in every pass. Only HN examples rotate across passes. HP diversity is untestable with the current pool. HN rotation is the more informative diversity dimension given the ~23:1 FP-to-FN asymmetry observed at baseline.

**Protocol impact**: Minor. H9-C tests a subset of the intended image diversity factor. The HP-diversity component is deferred to post-H10 when calibration tile expansion may yield additional recognition failures. See Decision 11 in decisions-log.md.

---

### E13: H12 (HP:HN ratio) deferred to post-H10

| Field | Value |
|-------|-------|
| Date | 2026-02-02 |
| Type | Deviation |
| Files | `docs/methodology/preregistration/hypothesis-tracking.md` |
| Impact | Exploratory hypothesis H12 postponed |

**Description**: H12 tests the effect of varying the HP:HN ratio within hard example libraries. With HP capped at 4, the only testable ratios are HP-constant with varying HN counts (e.g., 4:4, 4:8, 4:12), which confounds ratio with total library size. Reducing HP below 4 discards known-useful information.

The full symmetric ratio design (e.g., 4:8 vs 8:4) requires a larger HP pool, which may become available after H10 (training pool expansion via calibration tile expansion using reserve tiles).

**Justification**: Running a confounded version of H12 now would produce ambiguous results — any observed effect could be attributed to either ratio or total count. Deferring to post-H10 preserves the possibility of an informative, symmetric test. See Decision 11 in decisions-log.md and `planning/hard-example-library-decisions.md` §5.

**Protocol impact**: Moderate. H12 is a Tier B exploratory hypothesis, not confirmatory. Its trigger condition ("H8 shows library matters") may or may not be met. Deferral does not affect confirmatory hypotheses H1–H8.

---

### E14: Verbose instruction word count exceeds preregistered range

| Field | Value |
|-------|-------|
| Date | 2026-02-04 |
| Type | Clarification |
| Files | `prompts/system-instructions/detect_verbose-text-image.md`, `detect_verbose-text.md`, and their terse/verbose exclusion variants |
| Impact | Minor — verbose M/E level ~80 words above target |

**Description**: Iterative prompt refinement across Sessions 12–14 (decision procedure restructuring, centre-pointing language, exclusion criteria updates) has grown the verbose-level instruction text to 779 words. The brief-to-verbose ratio is now approximately 1:3.7 (213:779), which exceeds the preregistered range by ~80 words.

The additional content consists of structural improvements (two-phase decision procedure per E14 commit `52d54e9`), spatial orientation language (E9), and refined exclusion criteria — all documented in prior errata. No new substantive content was added beyond what is recorded in E9 and the prompt review commits.

**Protocol impact**: Minor. The overshoot may marginally increase the information gap between brief and verbose conditions, potentially amplifying the H1 M/E effect. This works in favour of detecting a difference if one exists, so it is a conservative deviation. The word count is noted here for transparency and will be reported in the methods section.

---

### E15: Inconsistent pass count references in preregistration appendix

| Field | Value |
|-------|-------|
| Date | 2026-02-04 |
| Type | Correction |
| File | `docs/methodology/preregistration/osf/preregistration-appendix-prompts.md` |
| Impact | None (internal inconsistency in submitted preregistration; execution used the correct value) |

**Description**: The preregistration appendix contains inconsistent pass count references for the Phase 1 baseline calibration run. The operative procedure (lines 98–99) specifies "5 passes" with a "≥3/5 passes" threshold, consistent with the execution simulation and the v2.1 changelog ("aligned Phase 1 baseline with preregistration (5 passes, ≥3/5 threshold)"). However, two other locations retain stale values from an earlier draft:

| Location | Text | Intended |
|----------|------|----------|
| Line 115 (HP selection) | "≥3/10 passes missed" | ≥3/5 |
| Line 1694 (HN TBD table) | "≥3/10 runs" | ≥3/5 |

The main preregistration (§8.4.2) does not specify a pass count, deferring to the appendix procedure.

**Root cause**: The appendix v2.1 update aligned the HN procedure (lines 98–99) and HP TBD table (line 1695) to K=5 but missed the HP description (line 115) and HN TBD table (line 1694).

**Protocol impact**: None. Phase 1 was executed with K=5 passes as specified by the operative procedure. The stale "≥3/10" references are residual from an earlier draft and do not reflect intended methodology. The threshold is moot in any case: all 24 FNs were complete misses (0/5) and all selected FPs occurred at 5/5 or ≥3/5 votes. Decisions-log Decision 4 has been corrected to reference K=5.

---

### E16: Prompt text shifted from cartographic naming to visual descriptions

| Field | Value |
|-------|-------|
| Date | 2026-02-03 |
| Type | Clarification |
| Commit | `2d46311` |
| Files | All 10 `prompts/system-instructions/detect_*.md` files |
| Impact | Changes wording of preregistered prompt text without altering prompt structure or factor design |

**Description**: The preregistered prompt text (appendix v2.17) describes non-mound map features using cartographic identity names: "Contour Line Artefacts", "Infrastructure Markers", "Quarry and Pit Symbols", "Roads (black/red lines), contour lines (brown), grid lines (blue)". During hard example review (Session 11), these were systematically revised to use visual appearance descriptions: "Closed Curved Line Patterns", "Dots on Linear Features", "Inward-Pointing Marks", "Lines in various colours (black, red, brown, blue)". Interpretive glosses such as "(inward = excavation, outward = elevation)" were removed.

**Rationale**: The VLM may not map cartographic feature names to the correct visual patterns. Visual descriptions (colours, shapes, spatial relationships) are robust because they describe what the model actually sees. This matches the register already used for the target symbol ("sunburst with outward-radiating rays"). See Decision 14 in decisions-log.md.

**Scope of changes**: Section headings, exclusion category titles, and feature descriptions were reworded. The prompt structure (preamble, decision procedure, exclusion categories), factor design (H5 levels, M/E levels), and example library are unchanged. The changes were applied uniformly across all H5 conditions.

**Protocol impact**: Minor. The wording of exclusion criteria and occlusion guidance changed, but the set of features being described and the diagnostic logic (ray presence/absence, direction of marks) are preserved. The changes are conservative: visual descriptions are a subset of what the cartographic names conveyed, avoiding assumptions about VLM cartographic knowledge.

---

### E17: Execution plan and Phase 2 YAMLs contained erroneous N=5 passes multiplier

| Field | Value |
|-------|-------|
| Date | 2026-02-05 |
| Type | Correction |
| Files | `docs/methodology/preregistration/execution-plan.md`, `studies/phase2a-h1-modality.yaml`, `studies/phase2b-h7-temperature.yaml`, `studies/phase2c-h8-library.yaml`, `studies/phase2d-h5-negtext.yaml`, `studies/phase2e-h4-ordering.yaml` |
| Impact | Would have run 5× more API calls than preregistered, at 5× the cost |

**Description**: The execution plan cost formula (line 271) and all five Phase 2 YAML files contained `passes: 5` and formulas like `5 × K=10 × 60 tiles × N=5 = 15,000 API calls`. The `× N=5` multiplier adds within-run consensus passes that **conflict** with the preregistration §3.8, which explicitly specifies "K=10 independent **single-pass** runs" and explains the rationale: "without assuming voting (which is itself under test in H3)."

Under the preregistered protocol, voting analysis (H3) is performed post-hoc by re-pooling the same K=10 single-pass runs (N=5 from runs 1–5, N=10 from all runs) without additional API calls.

**Fix**: Removed the `passes` field from all five Phase 2 YAML files. Corrected all cost formulas in the execution plan to use the single-pass formula (e.g., `5 × K=10 × 60 = 3,000` for Phase 2a). Corrected the evaluation protocol section to describe single-pass runs rather than N=5 consensus voting per run. Updated output path patterns from `run_{run}/pass_{pass}/` to `run_{run}/`.

**Protocol impact**: None. The preregistered protocol (§3.8) is authoritative and specifies single-pass runs. This corrects the implementation artefacts to match the preregistration.

---

### E18: Config naming convention clarification (§8.7.4 _minimal suffix)

| Field | Value |
|-------|-------|
| Date | 2026-02-05 |
| Type | Clarification |
| Files | `prompts/configs/detect_*.json` |
| Impact | None (naming simplification only) |

**Description**: The preregistration §8.7.4 references config files as `detect_image-only_minimal.json` (with an H5 suffix for the Minimal/default negative text treatment level). The actual implementation uses `detect_image-only.json` (no suffix) for the H5=Minimal variant, since Minimal is the default treatment. Configs for non-default H5 levels use explicit suffixes: `_terse` and `_verbose`.

This is a naming simplification: the unsuffixed config IS the H5=Minimal variant. The convention is consistent across all five M/E levels and is documented in each config's `description` field (e.g., "H1 baseline. M/E=Image-only, H5=Minimal").

**Protocol impact**: None. The config contents are identical to what the preregistration describes; only the filename omits the redundant `_minimal` suffix.

---

### E19: Validation bounds generated from wrong manifest

| Field | Value |
|-------|-------|
| Date | 2026-02-05 |
| Type | Correction |
| Files | `inputs/vectors/bounds/validation_bounds.geojson` |
| Impact | Evaluation reported F1 ~0.1 instead of ~0.4 for sanity check runs |

**Description**: The `validation_bounds.geojson` file contained 20 tile bounds generated from the calibration tile set (via `generate_tile_bounds.py` which reads `holdout_manifest.json`), not the 60-tile validation set. Only 7 of those 20 tiles overlapped spatially with the 60 validation tiles, so 53 of 60 tiles had no bounds for scoping ground truth references. This caused massive false positive inflation — predictions from unbounded tiles were compared against all ground truth rather than just references within the tile footprint.

**Root cause**: A naming convention mismatch. The tile selection metadata uses "holdout" as the key for the 60-tile set, but the manifest file is named `validation_manifest.json` (not `holdout_manifest.json`). The original `validation_bounds.geojson` (dated 2025-12-21) predates the manifest renaming and was never regenerated.

**Verification**: Calibration and validation tile sets confirmed to be **completely disjoint** (zero overlap). The sets were correctly partitioned at creation time — only the bounds file pointed to the wrong set.

**Fix**: Regenerated `validation_bounds.geojson` from `validation_manifest.json` using the `create_bounds_geojson()` function, producing 60 tile features matching the validation manifest. Bounds validated against tile metadata (5-tile spot check passed).

**Corrected metrics** (image-only condition, 3 sanity check runs at 20m tolerance):

| Run | Old F1 | Corrected F1 |
|-----|--------|-------------|
| 1 | 0.111 | 0.435 |
| 2 | 0.083 | 0.388 |
| 3 | 0.083 | 0.360 |

**Protocol impact**: None. The evaluation methodology (20m spatial tolerance, Hungarian matching) is unchanged. This corrects an infrastructure artefact.

---

### E20: Standardised "holdout" → "validation" naming across codebase

| Field | Value |
|-------|-------|
| Date | 2026-02-05 |
| Type | Clarification |
| Files | `inputs/tiles/tile_selection_metadata.json`, `scripts/generate_tile_bounds.py`, `scripts/select_tiles_phase4.py`, `scripts/analyse_phase2_results.py`, tests |
| Impact | None (internal naming only) |

**Description**: The codebase used inconsistent naming for the 60-tile evaluation set:

- Preregistration uses "holdout tiles" (§2.1)
- Manifest file was `validation_manifest.json`
- Bounds file was `validation_bounds.geojson`
- But metadata JSON used `"holdout"` as the key
- Scripts referenced `holdout_manifest.json` which never existed

This mismatch caused E19 (bounds generated from wrong manifest). Standardised to "validation" throughout:

1. Changed `tile_selection_metadata.json` key from `"holdout"` to `"validation"`
2. Changed `"holdout_samples_per_map"` to `"validation_samples_per_map"`
3. Updated `generate_tile_bounds.py` to read `validation_manifest.json` and output `validation_bounds.geojson`
4. Updated `select_tiles_phase4.py` to read from `validation_*` files
5. Updated `analyse_phase2_results.py` default bounds path
6. Updated test fixtures and docstrings

**Rationale**: "Validation" is the conventional ML term for the evaluation set used during development. "Holdout" in ML typically refers to a completely withheld test set (our 281-tile reserve). The preregistration's use of "holdout" for the 60-tile set was a terminological choice; the implementation uses "validation" for clarity. The 281-tile reserve remains unnamed/untouched.

**Protocol impact**: None. The tile sets are unchanged; only internal naming is standardised.

---

### E21: Stale `passes` parameter in analysis script

| Field | Value |
|-------|-------|
| Date | 2026-02-05 |
| Type | Correction |
| File | `scripts/analyse_phase2_results.py` |
| Impact | Would have caused analysis to look for non-existent pass subdirectories |

**Description**: The `load_condition_results()` function in the analysis script retained a `passes: int = 5` parameter from an earlier design that predated E17 (removal of per-run consensus passes from Phase 2 YAMLs). The function attempted to iterate `run_X/pass_Y/` subdirectories, but the actual output structure from `run_phase2.py` is flat `run_K/` directories with no pass level.

Additionally, the function globbed for `*.geojson` files, but the batch detection script produces detection files without the `.geojson` extension (e.g., `detections_image-only_run01` not `detections_image-only_run01.geojson`).

**Fix**: Removed `passes` parameter. Rewrote file discovery to iterate `run_*` directories directly and glob `detections_*` files with explicit exclusion of `.meta.json`, `_fp.*`, and `_fn.*` files. Function now returns `list[tuple[int, GeoDataFrame]]` (per-run results) instead of a single merged GeoDataFrame — see E22.

**Protocol impact**: None. This corrects the implementation to match the output structure already produced by the runner.

---

### E22: Per-run evaluation architecture (was merged, now per-run)

| Field | Value |
|-------|-------|
| Date | 2026-02-05 |
| Type | Correction |
| Files | `scripts/analyse_phase2_results.py`, `scripts/lib_advanced_metrics.py` |
| Impact | Previous merged approach would have produced nonsensical precision values |

**Description**: The analysis script's `analyse_phase_results()` function merged all K=10 runs' detections into a single GeoDataFrame before computing F1. With K=10 runs, this yields 10× the detection count per tile, making precision nonsensical — every run's detections are evaluated against the same ground truth, so 10 correct detections of the same reference mound count as 1 TP + 9 FPs.

**Fix**: Rewrote evaluation to compute F1 per run independently:

1. `load_condition_results()` returns per-run GeoDataFrames
2. F1, precision, and recall are computed per run using `calculate_f1_internal()`
3. Intermediate results saved to `per_run_metrics.csv`
4. Two new bootstrap functions added to `lib_advanced_metrics.py`:
   - `bootstrap_multi_run_ci()`: Resamples tiles (n=60 with replacement), computes F1 per run on the same tile sample, averages across runs. CI = 2.5th/97.5th percentiles.
   - `bootstrap_multi_run_effect_size_ci()`: Same tile resampling for paired condition comparison.

This preserves the tile as the resampling unit (per preregistration §3.5) while correctly handling the K=10 repeated-measures structure.

**Validation**: Run against 3 existing image-only runs. Per-run F1 values: 0.435, 0.388, 0.360 — matching the expected ~0.36–0.44 range observed during sanity checks.

**Protocol impact**: None. The preregistered statistical method (bootstrap with tile-level resampling) is unchanged. This corrects an implementation error that would have conflated runs.

---

### E23: Enhanced API metadata capture (citation, prompt block reason, prompt safety)

| Field | Value |
|-------|-------|
| Date | 2026-02-05 |
| Type | Correction |
| File | `scripts/lib_llm_metadata.py` |
| Impact | Three Gemini API fields were silently discarded; now captured |

**Description**: The Gemini API provides three metadata fields that the metadata extraction function silently discarded:

| Field | Where in API | Previous status | Fix |
|-------|-------------|----------------|-----|
| Citation metadata | `response.candidates[0].citation_metadata` | Not captured | Added `citation_metadata: dict` to dataclass |
| Prompt block reason | `response.prompt_feedback.block_reason` | Existence checked but value discarded | Capture actual enum value as string |
| Prompt-level safety ratings | `response.prompt_feedback.safety_ratings` | Not captured | Added `prompt_safety_ratings: list` to dataclass |

All three fields default gracefully (None/empty list) when not present in the API response. The existing `LLMResponseMetadata` dataclass is serialised via `asdict()`, so the new fields flow through to `.meta.json` files without changes to the batch detection script.

**Note**: The 3 existing image-only runs (completed before this fix) lack these fields. This is unavoidable as the data cannot be recovered retroactively. All subsequent runs capture them.

**Protocol impact**: None. This captures additional API-provided metadata for transparency. The detection methodology is unchanged.

---

### E24: Dry-run checkpoint corruption bug in run_phase2.py

| Field | Value |
|-------|-------|
| Date | 2026-02-05 |
| Type | Correction |
| File | `scripts/run_phase2.py` |
| Impact | Dry runs corrupted checkpoint state, preventing correct resume |

**Description**: The `run_phase2.py` runner unconditionally appended execution units to `checkpoint["completed"]` and saved the checkpoint file, regardless of whether the run was a dry run. This meant that `--dry-run` would mark all units as "completed" in the checkpoint, corrupting the resume state.

**Discovery**: During pre-flight validation (Step 1 of Phase 2a execution), a `--dry-run` command corrupted the checkpoint from 3 completed units to 50 completed units. The checkpoint had to be manually restored.

**Fix**: Wrapped checkpoint updates in an `if not dry_run:` guard so that dry runs never modify the persistent checkpoint state.

**Protocol impact**: None. This is a runner infrastructure bug that does not affect detection methodology or results. The 3 existing runs were unaffected (their results were on disk and the checkpoint was restored before data collection resumed).

---

### E25: Modality manipulation not implemented — text-only conditions received images

| Field | Value |
|-------|-------|
| Date | 2026-02-06 |
| Type | Correction |
| Files | `scripts/4_detect_mounds_batch.py`, `prompts/configs/detect_brief-text.json`, `prompts/configs/detect_verbose-text.json` |
| Impact | 20 runs (brief-text × 10, verbose-text × 10) tested wrong modality; must be re-run |

**Description**: The preregistration (Section 4.1.1, lines 412–418) specifies that the H1 modality/elaboration factor has 5 levels:

| Level | Text | Images |
|-------|------|--------|
| Image-only | Minimal | Yes |
| Brief-text | Brief | **No** |
| Brief-text+image | Brief | Yes |
| Verbose-text | Verbose | **No** |
| Verbose-text+image | Verbose | Yes |

The batch detection script (`4_detect_mounds_batch.py`) unconditionally loaded and sent all 17 example images from the config's `examples` array to the API, regardless of condition. No conditional logic existed to skip images for text-only conditions. All 5 conditions received identical image content.

**Discovery**: During post-collection QA, the user noted that F1 outcomes were "surprisingly clustered" across conditions (range: 0.42–0.46). Based on prior experience where adding images made a noticeable difference, this triggered investigation. Cross-referencing the preregistration table revealed the implementation gap.

**Cost**: 20 runs × 60 tiles = 1,200 API calls (~$2.60) executed with incorrect modality. The data has secondary value (tests text elaboration within image+text modality) but is invalid for the preregistered H1 modality question.

**Fix**:

1. Added `include_example_images` config field (default: `true` for backward compatibility)
2. Added conditional logic to batch script: when `include_example_images: false`, skip the example image loading loop entirely
3. Updated `detect_brief-text.json` and `detect_verbose-text.json` to set `include_example_images: false`

**Re-run scope**: Only brief-text and verbose-text conditions (20 runs) require re-execution. The other 3 conditions (image-only, brief-text-image, verbose-text-image) correctly received images and are valid.

**Protocol impact**: None. The preregistered design is unchanged. This corrects the implementation to match it. The affected runs will be re-executed with the corrected configs.

**Lesson**: After creating experimental configs, explicitly verify each manipulated dimension with the question: "how does the code know to vary this?" Design-to-implementation gaps are not caught by unit tests that verify component correctness.

---

### E26: Bootstrap CI bias from reference de-duplication on resampled tiles

| Field | Value |
|-------|-------|
| Date | 2026-02-06 |
| Type | Correction |
| Files | `scripts/lib_advanced_metrics.py`, `tests/test_analyse_phase2.py` |
| Impact | Bootstrap CIs were systematically deflated; point estimates unaffected |

**Description**: All bootstrap confidence interval functions in `lib_advanced_metrics.py` produced CIs that did not contain the point estimates. For example, image-only had point estimate F1=0.4252 but bootstrap CI=[0.254, 0.373] — a ~34% precision deflation.

**Root cause**: When tiles are resampled with replacement, detections are correctly duplicated (the inner loop appends per tile), but references are de-duplicated by `scope_references_to_tiles()` via `gdf_ref.index.isin()`. Because `isin()` returns unique index matches, duplicate tiles in the bootstrap sample do not produce duplicate reference entries. Extra detections for duplicated tiles therefore become unmatched false positives, systematically deflating precision.

A secondary instance of the same bug affected `bootstrap_tile_classification_ci()` and `bootstrap_tile_effect_size_ci()`, where `gdf_bounds['tile_name'].isin(sample_tiles)` de-duplicated the bootstrap sample, converting bootstrap resampling into subsampling without replacement.

**Fix**: Refactored all 7 bootstrap functions to use a per-tile pre-computation strategy:

1. Added `compute_per_tile_tp_fp_fn()`: performs spatial matching once per tile and returns a DataFrame of [tile_name, tp, fp, fn]
2. Added `aggregate_tile_metrics()`: looks up TP/FP/FN for each tile in the bootstrap sample (handling duplicates correctly) and computes precision, recall, F1 from the sums
3. Refactored `bootstrap_ci()`, `bootstrap_effect_size_ci()`, `bootstrap_multi_run_ci()`, `bootstrap_multi_run_effect_size_ci()`, and `bootstrap_interaction_ci()` to pre-compute per-tile metrics once, then use `aggregate_tile_metrics()` in the inner loop
4. Refactored `bootstrap_tile_classification_ci()` and `bootstrap_tile_effect_size_ci()` to pre-compute per-tile classifications and count them with duplicates

**Approximation**: The fix uses per-tile matching rather than per-map matching (as `calculate_f1_internal()` does). Cross-tile matches within the 20 m buffer are negligible given tile sizes (hundreds of metres). For the synthetic test data with 100 m tiles spaced 100 m apart, per-tile and per-map matching produce identical results.

**What was NOT affected**: Per-run F1 point estimates (in `per_run_metrics.csv`) were always correct — they use `calculate_f1_internal()` which does not resample tiles. Only the bootstrap CIs were biased.

**Regression tests added**:

- `test_bootstrap_mean_approximates_point_estimate`: Verifies bootstrap mean F1 is within 0.02 of the point estimate
- `test_per_tile_metrics_sum_matches_global`: Verifies per-tile TP/FP/FN sums match `calculate_f1_internal()` output
- `test_aggregate_with_duplicate_tiles`: Verifies a tile sampled 3× contributes 3× its TP/FP/FN
- `test_bootstrap_ci_contains_point_estimate`: Verifies the 95% CI contains the point estimate

**Protocol impact**: None. The preregistered statistical method (bootstrap with tile-level resampling, §3.5) is unchanged. This corrects an implementation bug in how resampled tiles were passed to the matching functions. The `analysis_report.json` was also regenerated from the current (valid) data after the fix.

### E27: Dual-track carry-forward from Phase 2a (OFAT deviation)

| Field | Value |
|-------|-------|
| Date | 2026-02-06 |
| Type | Deviation |
| Decision | Decision 16 |
| Impact | Phases 2b–2e carry two M/E levels instead of one; text-only track skips 2c, defers 2d/2e |

**Description**: The preregistered OFAT design (§8.3.1a) specifies selecting a single optimal M/E level from Phase 2a and carrying it forward through all subsequent phases. Phase 2a produced a counter-intuitive result: text-only `brief-text` achieved the highest mean F1 (0.5425), exceeding the best image-using condition `brief-text-image` (F1=0.4617) by +0.08. However, no pairwise comparisons survived FDR correction (q=0.05).

The single-winner carry-forward is structurally incompatible with a text-only winner: Phase 2d (H5) explicitly excludes text-only M/E levels, Phase 2c (H8) tests image library composition, and Phase 2e (H4) tests example image ordering.

**Deviation**: Two M/E levels are carried forward:

1. **brief-text-image** (Track 1): follows the full preregistered OFAT sequence (2b→2c→2d→2e)
2. **brief-text** (Track 2): receives targeted tests — Phase 2b temperature testing; Phase 2c skipped; Phases 2d and 2e deferred pending results

Each track maintains independent optimal parameters (e.g., different optimal temperatures carried forward separately).

**Justification**: Carrying only brief-text would abandon the image-based pipeline despite non-significant H1 differences. Carrying only brief-text-image would ignore the best-performing condition. The dual-track approach preserves both optimisation paths at modest additional cost (~$55 for 5 extra temperature cells).

**Protocol impact**: Adds ~5 cells to Phase 2b. Does not affect the image-using OFAT chain. Text-only results from deferred phases (if pursued) will be reported as exploratory.

---

### E28: H5 instruction text adapted for Phase 2d (HN image references removed, OFAT simplification)

| Field | Value |
|-------|-------|
| Date | 2026-02-11 |
| Type | Deviation |
| Decision | Decision 17 |
| Files | `prompts/system-instructions/detect_brief-text-image_terse.md`, `detect_brief-text-image_verbose.md`, `detect_brief-text_terse.md` (new), `detect_brief-text_verbose.md` (new) |
| Impact | Changes wording of preregistered instruction text; simplifies Phase 2d design |

**Description**: Three changes to the Phase 2d (H5 negative text treatment) design:

1. **Instruction text adaptation**: Guideline 3 in terse and verbose instruction files was trimmed from two sentences to one, removing "Each reference image is centred on the feature being labelled — the target symbol for Positive examples, the confusable feature for Negative examples." This sentence described HN (hard negative) reference image content, but HN images were excluded from the library after Phase 2c determined plus-hp (no HN) as optimal. The verbose exclusion intro was also trimmed: "Study any negative reference images carefully." removed for the same reason.

   The minimal instruction (`detect_brief-text-image.md`, `detect_brief-text.md`) is **not** modified — it serves as the Phase 2c/2b baseline and the cost of re-running 1,200 API calls to fix a conditional sentence the model mostly ignores outweighs the minor confound.

2. **OFAT simplification**: The preregistered 3×3 factorial (3 M/E levels × 3 H5 levels) is replaced by single-factor OFAT testing H5 at the carried-forward optimal M/E level per track. Since Phase 2a determined brief-text-image as optimal image-using M/E, the factorial collapses to 3 H5 levels × 1 M/E = 3 cells (1 reused, 2 new) per track.

3. **Dual-track execution**: Track 2 (text-only brief-text) was deferred for Phase 2d in Decision 16 but is now activated. Precision is the bottleneck for both tracks (~52–56% for text-only at T=0.0), so testing whether exclusion guidance text reduces false positives is justified in both modalities.

**Cross-references**: Decision 17, E27 (dual-track carry-forward).

**Protocol impact**: Moderate. The instruction text changes are conservative (removing references to non-existent images rather than adding new content). The OFAT simplification reduces statistical power for detecting M/E × H5 interactions but is consistent with the sequential OFAT design used throughout Phase 2. Dual-track addition is exploratory for the text-only track.

---

### E29: `reorder_examples()` canonical-first was a no-op

| Field | Value |
|-------|-------|
| Date | 2026-02-12 |
| Type | Correction |
| File | `scripts/4_detect_mounds_batch.py` |
| Impact | All prior phases used config-file order unknowingly; no results affected |

**Description**: The `reorder_examples()` function's `canonical-first` ordering was a no-op — it returned examples in config-file order `[C+, HP, C−, null]` rather than true canonical-first `[C+, C−, HP, null]`. The config-file order already places canonical positives first, so the function appeared to work, but the interleaving of hard positives before canonical negatives was not the intended grouping.

**Discovery**: During Phase 2e (H4 ordering) design review, comparison of the intended canonical-first grouping `[C+, C−, HP, null]` against the function output revealed the ordering was unchanged from config-file order.

**Fix**: Split the single `canonical-first` ordering into two distinct conditions:

1. **`config-default`**: Explicit no-op returning examples in JSON config-file order (the ordering all prior phases actually used)
2. **`canonical-first`**: True grouped ordering `[C+, C−, HP, null]` with category-based sorting and safety assertions against example loss

Additionally, `canonical-last` and `random` orderings were implemented with exhaustive category filtering using three filter conditions (`startswith('canonical')`, `startswith('hard')`, `== 'null'`) and a defensive assertion to catch any future miscategorised examples.

**Protocol impact**: None. All prior phases (2a–2d) used the default ordering from the config file, which is what they were intended to use — the `canonical-first` flag was never explicitly set in those phases. The fix enables Phase 2e to properly test the ordering hypothesis (H4) by providing distinct orderings to compare.

**Cross-references**: E30, Decision 18.

---

### E30: Phase 2e tests 4 ordering conditions instead of preregistered 3

| Field | Value |
|-------|-------|
| Date | 2026-02-12 |
| Type | Deviation |
| Decision | Decision 18 |
| Files | `studies/phase2e-h4-ordering.yaml` |
| Impact | Adds 1 condition (10 runs, 600 API calls) to Phase 2e |

**Description**: The execution plan (§Phase 2e) specifies 3 ordering conditions: canonical-first, canonical-last, and random. Phase 2e now tests 4 conditions by adding `config-default` as an explicit baseline distinct from `canonical-first`.

The 4 conditions are:

| Condition | Order | Source |
|-----------|-------|--------|
| config-default | `[C+, HP, C−, null]` | JSON config-file order (no-op) |
| canonical-first | `[C+, C−, HP, null]` | True canonical grouping |
| canonical-last | `[HP, null, C+, C−]` | Canonical examples last |
| random | Seeded shuffle per run | Randomised ordering |

**Rationale**: The bug documented in E29 revealed that the baseline ordering all prior phases used (`config-default`) was never truly `canonical-first`. Both orderings are scientifically informative: `config-default` preserves continuity with prior phases, while `canonical-first` tests the intended grouping. The `config-default` baseline is reused from Phase 2c plus-hp outputs via symlinks, adding no additional API cost for those 10 runs.

**Cost impact**: Net new API calls increase from 1,800 (3 × 10 × 60) to 1,800 (only 3 new conditions run; config-default reused). Total Phase 2e units increase from 30 to 40, but the 10 config-default units are pre-checkpointed.

**Protocol impact**: Minor. Adds one condition that reuses existing data. The additional condition strengthens the design by providing an explicit baseline that matches all prior phases, enabling direct comparison between the ordering all prior phases used and the intended canonical-first grouping.

**Cross-references**: E29, Decision 18.

---

### E31: Deterministic runs at T=0.0 copied instead of re-executed

- **Date**: 2026-02-12
- **Phase**: 2e (H4 — Ordering)
- **Type**: Deviation
- **Severity**: Low

**Issue**: The preregistered design specifies K=10 replicate runs per condition. At T=0.0 (deterministic decoding), fixed-ordering conditions (canonical-first, canonical-last) produce identical outputs across all K=10 runs — empirically confirmed in Phase 2d where every replicate was byte-identical. Running all 10 replicates for these conditions wastes API calls without generating any statistical information.

**Resolution**: For 4 remaining deterministic units (canonical-first/run\_1, canonical-last/run\_3, canonical-last/run\_6, canonical-last/run\_8), detection outputs were copied from an existing completed run in the same condition rather than re-executing against the API. File contents are identical to what the API would have produced. The 5 remaining random-ordering units (which use per-run seeds and therefore produce genuinely different outputs) were executed normally.

**Justification**: At T=0.0, the Gemini 3 Flash API is perfectly deterministic — identical prompts produce identical outputs. This was empirically confirmed in Phase 2d (Session 32: terse=134, verbose=128 detections in every replicate). For fixed-ordering conditions where the prompt does not vary across runs, all K=10 runs are guaranteed to be identical. Copying existing outputs is equivalent to re-execution and avoids ~$1 of redundant API calls and several hours of execution time under heavy API rate limiting.

**Impact on analysis**: None. The copied runs are identical to what re-execution would produce. Bootstrap CIs for deterministic conditions will show zero within-condition variance regardless of whether runs were executed or copied. The random condition (K=10 genuinely different runs) is unaffected.

**Files**: `outputs/phase2e/checkpoint.json`, `outputs/phase2e/canonical-first/run_1/`, `outputs/phase2e/canonical-last/run_{3,6,8}/`.

**Cross-references**: Observation 128 (working notes — determinism implications for replication design).

---

### E32: Phase 3a uses T=0.3/T=0.7 instead of carry-forward T=0.0

- **Date**: 2026-02-12
- **Phase**: 3a (H3 — Consensus Voting Validation)
- **Type**: Deviation
- **Severity**: Low

**Issue**: The preregistered design (Section 8.3.1a) carries forward the optimal temperature from Phase 2b through subsequent phases. For both tracks, T=0.0 was optimal. However, consensus voting requires run-to-run variation to function — at T=0.0, the plus-hp library configuration produces near-deterministic output (empirically confirmed in Phases 2d–2e, where every replicate was byte-identical for fixed-ordering conditions). Applying consensus voting to identical runs is meaningless: all vote thresholds x=1..N produce the same result as a single run.

**Resolution**: Phase 3a tests consensus voting at T=0.3 and T=0.7 instead of the carry-forward T=0.0. These temperatures introduce sufficient stochasticity for consensus voting to operate while remaining in the low-to-moderate variance range. The key question shifts from "does consensus at T=0.0 help?" to "does consensus at T>0 beat the T=0.0 single-run ceiling?"

**Justification**: Phase 2b retroactive consensus analysis (canonical library) showed that consensus voting at T=0.3 with N=10, x=8 achieved F1=0.642, exceeding the T=0.0 single-run F1=0.557. This suggests consensus can recover or exceed deterministic performance by filtering false positives through vote thresholds. Phase 3a validates this finding on the actual carry-forward configurations (plus-hp for image track, brief-text for text-only track).

**Baselines**: Track 1 (image) F1=0.609, Track 2 (text-only) F1=0.660 — both T=0.0 single-run means from Phase 2.

**Impact on analysis**: The consensus voting comparison is against the T=0.0 single-run baseline, not against single-run performance at the same temperature. This is the scientifically relevant comparison: consensus voting must justify its additional API cost by exceeding the cheapest achievable performance (one run at T=0.0).

**Cross-references**: E27 (dual-track carry-forward), E31 (deterministic run shortcuts confirming T=0.0 reproducibility).

---

### E33: Verifier crop extraction reads from tiles instead of source rasters

| Field | Value |
|-------|-------|
| Date | 2026-03-12 |
| Type | Correction |
| Files | `scripts/extract_candidates.py`, `scripts/5_verify_crops.py` |
| Impact | Mounds near tile edges receive asymmetrically truncated crops, potentially biasing verifier decisions |

**Description**: Both `extract_candidates.py` and `5_verify_crops.py` extracted crops from tile PNG images rather than the underlying GeoTIFF source rasters. When a detection centroid fell within `padding` pixels of a tile edge, the crop was clamped to tile boundaries (via `max(0, ...)` / `min(src.width, ...)` guards), producing a smaller-than-requested, asymmetric image. The intended behaviour was to crop from the full-resolution source raster, which has no edge constraints at detection locations.

**Fix**: Modified both scripts to resolve each detection's `source_tile` to its parent GeoTIFF raster (in `inputs/rasters/`), then extract the crop with `boundless=True`. Rasterio pads beyond-raster-edge pixels with fill_value=0 (black), guaranteeing crops are always exactly `padding*2 × padding*2` pixels regardless of detection position. Falls back to tile PNGs if source rasters are not available, with a warning.

**Affected results**: All Phase 3d proposer-verifier results that used `extract_candidates.py`:

- Phase 3d pilot (Session 43): Track 1 and Track 2, verifiers B/C/D
- Phase 3d pilot extensions (Session 44): P-R curves, cross-modal overlap
- Phase 3d verifier experiments A–D (Sessions 46–47)
- Phase 3d HIGH-thinking verifier test (Session 45)
- Cross-modal union experiment (Session 45)

**Not affected**: Single-pass detection (conditions a, b) — these don't use crop extraction.

**Remediation**: All affected verifier experiments to be re-run with corrected crop extraction. Original results archived to `archive/phase3d-pre-e33/` for comparison.

---

### E34: Thinking-level not propagated through batch/subprocess execution units

| Field | Value |
|-------|-------|
| Date | 2026-03-15 |
| Type | Correction |
| Files | `scripts/run_phase2.py` |
| Impact | `--thinking-level` CLI override silently dropped when running via `run_phase2.py` |

**Description**: The `generate_execution_units()` function in `run_phase2.py`
copied `temperature`, `ordering`, and `ordering_seed` from condition dicts to
execution unit dicts, but not `thinking_level`. This meant that when a study
YAML defined `thinking_level` as a factor (or set it in the `fixed` section),
the value was parsed correctly at the condition level but never reached the
subprocess command (real-time mode) or the batch unit dict (batch mode).

**Fix**: Added `"thinking_level": condition.get("thinking_level")` to the unit
dict in `generate_execution_units()`. Also added `--thinking-level` CLI flag to
`4_detect_mounds_batch.py` and thinking_level override support in
`lib_batch_api.py`'s `prepare_batch_unit()`.

**Affected results**: The `phase3a-replication.yaml` study was the first to use
`thinking_level` as a factor. The initial dry run (before the fix) showed
`--thinking-level` was absent from the subprocess commands. The fix was applied
before any replication data was collected, so no results are affected.

**Related**: The historical Phase 3a metadata-recording bug (Obs 141) is a
separate issue — the metadata captured the config file's default value rather
than the actual API parameter. That bug existed in the metadata *writer*, not
in the parameter *propagation* fixed here.

### E35: Bootstrap per-tile matching caused recall bias from reference double-counting

| Field | Value |
|-------|-------|
| Date | 2026-03-15 |
| Type | Correction |
| Files | `scripts/lib_advanced_metrics.py` |
| Impact | Bootstrap CIs for all prior phases had a small recall bias (bootstrap mean ~7 pp below point estimate at 340 tiles) |

**Description**: The `compute_per_tile_tp_fp_fn()` function performed
Hungarian-algorithm matching **per tile**, while `calculate_f1_internal()`
matched **per map**. With 64-pixel tile overlap, references near tile
borders intersected multiple tile geometries, causing two biases:

1. **Reference double-counting**: A reference in the overlap zone was
   independently matched (or not) in each overlapping tile, inflating
   both TP and FN counts.
2. **Border-detection misses**: A detection in tile A near the border
   could not match a reference in tile B's overlap zone, inflating FP.

At 60 tiles the effect was small (few tile boundaries). At 340 tiles
(production run), the divergence between point estimate and bootstrap
mean became visible: recall point estimate 0.802 vs bootstrap mean
0.731 (divergence 0.071).

**Fix**: Rewrote `compute_per_tile_tp_fp_fn()` to match **per map**
(identical to `calculate_f1_internal`), then distribute TP/FP/FN to
tiles: TPs and FPs assigned to the detection's `source_tile`,
unmatched FNs assigned to the reference's primary tile (nearest
centroid via `_assign_refs_to_primary_tiles()`).

After fix, divergence between point estimate and bootstrap mean
collapsed to <0.002 across all metrics (F1: 0.6050 vs 0.6034,
recall: 0.8015 vs 0.8005).

**Affected results**: All bootstrap CIs computed in Phases 2–3 on the
60-tile validation set have a small recall bias. The effect was modest
at 60 tiles (fewer overlap boundaries) but systematically present.
Pairwise effect size CIs were less affected because the bias applies
equally to both conditions, partially cancelling in the difference.
Production-run results use the corrected implementation.

**Context**: This correction is outside the formally preregistered
analysis protocol. The preregistration specifies bootstrap resampling
at the tile level (Section 3.5) but does not specify the spatial
matching granularity (per-tile vs per-map) within each bootstrap
iteration. The correction aligns the bootstrap matching with the
point-estimate matching method, which is the methodologically
consistent choice.

---

### E36: 340-tile production retest replaces 60-tile holdout evaluation

| Field | Value |
|-------|-------|
| Date | 2026-03-17 |
| Type | Deviation |
| Commit | `f06afb7` |
| Files | `studies/retest/*.yaml`, `inputs/vectors/bounds/full_evaluation_bounds.geojson` |
| Impact | All Phase 2–3 results re-evaluated on larger corpus; statistical power substantially increased |

**Description**: The preregistered Phase 3 evaluation used a 60-tile holdout set. Bootstrap CIs on this set were wide (~0.20) and only 1 of 10 Phase 2a pairwise comparisons survived FDR correction (Obs 155). The evaluation corpus was expanded to 340 tiles (569 ground truth mounds across 4 map sheets) to achieve adequate statistical power. All Phase 2a–3a conditions were re-run from scratch on the full corpus. K was reduced from 10 to 1–3 for single-pass conditions (340 tiles provide sufficient power) and retained at K=30 for consensus voting.

**Protocol impact**: Results from the 340-tile corpus supersede the 60-tile holdout results for all conditions. The 60-tile results remain documented in `results/phase3d-*.md` as historical reference. Hypothesis tests now have adequate power to detect the observed effect sizes.

---

### E37: Proposer-Verifier (PV) pipeline introduced as post-hoc extension

| Field | Value |
|-------|-------|
| Date | 2026-03-15 |
| Type | Deviation |
| Commit | `f9d40e0` (library), `5d72593` (orchestrator) |
| Files | `scripts/lib_verifier.py`, `scripts/run_pv.py`, `scripts/evaluate_pv_results.py` |
| Impact | New two-stage detection architecture; achieves F1=0.831, surpassing all preregistered approaches |

**Description**: The preregistration did not include a two-stage Proposer-Verifier pipeline. The PV approach was developed after observing that single-stage detection produced many false positives that a second-stage verifier could filter. The verifier receives candidate crop images and classifies them as mound/not-mound using an adversarial prompt framing. The PV pipeline was first piloted on the 60-tile holdout (F1=0.796, Obs 150) and then validated and optimised on the 340-tile corpus.

The PV pipeline supports both Batch API and real-time API execution modes. The published software offers both modes to end users. Verifier optimisation (Phase 1) tested crop size (40–300px), consensus (N=1 vs N=5), and verifier strategy (adversarial, checklist, brief) — all parameters were found to be insensitive (Obs 166, 167, 169).

**Protocol impact**: The PV pipeline is an extension beyond the preregistered design, not a replacement. All preregistered analyses (H1–H9) are evaluated independently of PV. The PV results are reported as an additional finding demonstrating that two-stage architectures can substantially improve VLM detection accuracy.

---

### E38: Dual-mode API architecture (batch and real-time)

| Field | Value |
|-------|-------|
| Date | 2026-03-20 |
| Type | Clarification |
| Commit | `5d72593` |
| Files | `scripts/run_pv.py`, `scripts/lib_verifier.py` |
| Impact | Technical implementation choice; no effect on results |

**Description**: The PV pipeline was implemented with shared prompt construction via an intermediate representation (IR) that supports both Gemini Batch API and real-time API execution. Both modes produce identical prompts and results — the mode affects only execution speed, cost (Batch API is 50% cheaper), and quota management. The published software defaults to real-time mode but allows `--mode batch` for large-scale runs.

**Protocol impact**: None — this is a technical implementation decision that does not affect the experimental design or results.

---

### E39: Verifier strategy equivalence confirmed at production scale

| Field | Value |
|-------|-------|
| Date | 2026-03-21 |
| Type | Clarification |
| Commit | `9a1b9e1` |
| Files | `results/pv/phase1/*/threshold_sweep.json` |
| Impact | Adversarial verifier selected as default; all three strategies produce equivalent F1 |

**Description**: The 60-tile pilot selected the adversarial verifier strategy based on F1=0.796 (vs checklist 0.782, brief 0.768). At 340-tile scale, all three strategies produce statistically indistinguishable F1 (adversarial 0.770, checklist 0.769, brief 0.752 — all CIs overlap, Obs 169). The adversarial strategy was retained as the default for consistency with the pilot and because its adversarial framing provides the most interpretable rejection reasoning.

**Protocol impact**: The choice of verifier strategy is not load-bearing for the PV results. Any of the three strategies would produce equivalent F1. This is documented as a robustness finding.

---

### E40: Gemini 3.1 Pro requires MEDIUM thinking — deviation from §8.2/§8.9

| Field | Value |
|-------|-------|
| Date | 2026-03-24 |
| Type | Deviation |
| Commit | pending |
| Files | `studies/h11-384-pro-pilot-*.yaml`, `scripts/run_phase2.py`, `scripts/run_pv.py` |
| Impact | Pro results use MEDIUM or HIGH thinking instead of preregistered MINIMAL |

**Description**: The preregistration (§8.2) specifies `thinking_level=minimal` for both Gemini 3 Flash and Gemini 3 Pro. Gemini 3.1 Pro (the current Pro model, API name `gemini-3.1-pro-preview`) does not support MINIMAL thinking — the lowest available level is MEDIUM. Attempts to use MINIMAL result in silent batch failures where all tiles return empty detections with no error message (only a `partial_failure_N_tiles` checkpoint status reveals the problem). Single-pass Pro experiments use MEDIUM thinking; consensus Pro experiments use HIGH thinking (motivated by the post-registration finding that HIGH thinking benefits consensus voting at strict thresholds, Obs 183).

**Protocol impact**: Pro results are not directly comparable to Flash at a matched thinking level. The comparison confounds model capability with thinking budget. This is an inherent constraint of the model (not a design choice) and is documented as such. The `--thinking-level` CLI override was added to both `run_phase2.py` and `run_pv.py verify` to support explicit thinking level specification for cross-model experiments.

---

### E41: 384px tile size and full evaluation set used for Pro comparison

| Field | Value |
|-------|-------|
| Date | 2026-03-24 |
| Type | Deviation |
| Commit | pending |
| Files | `studies/h11-384-pro-*.yaml` |
| Impact | More statistical power but different evaluation scope than preregistered H6 |

**Description**: The preregistered H6 (Flash→Pro transfer, §3.6) specifies a 20-tile stratified holdout subset at 512px tile size. Our Pro comparison uses 487 tiles at 384px — the optimal tile size identified by the H11 diagnostic (Obs 181). This provides substantially more statistical power (487 vs 20 tiles) and evaluates at the pipeline's optimal operating point, but departs from the preregistered H6 scope and tile size.

**Protocol impact**: The Pro comparison is best characterised as an exploratory extension rather than a strict implementation of H6. The larger evaluation set and optimal tile size strengthen the comparison's statistical validity but make it a different experiment than preregistered. H6 Phase 1 (20-tile holdout at 512px) remains available for future execution if a strict preregistration-compliant comparison is needed.

---

### E42: Metadata bug — `configuration.model` in meta.json reports config default, not resolved model

| Field | Value |
|-------|-------|
| Date | 2026-03-25 (initial); 2026-03-25 (corrected) |
| Type | Correction |
| Commit | pending |
| Files | `scripts/lib_llm_metadata.py`, `scripts/lib_batch_api.py`, `scripts/run_pv.py` |
| Impact | meta.json `configuration.model` field was unreliable when `--model` CLI override was used; led to incorrect E42 initial diagnosis |

**Description**: `LLMMetadataTracker.finalise()` wrote
`configuration.model` from `self.config.get("model")`, which reads the
static prompt config JSON. When the `--model` CLI override was used
(e.g., `--model gemini-3.1-pro`), the override was applied to the API
call but NOT reflected in the metadata. The `cost_estimate.pricing_used.model`
field and GeoJSON detection properties did record the correct model.

**Initial incorrect diagnosis**: Based on meta.json alone, all "Pro"
runs appeared to use `gemini-3-flash`. Directories were renamed from
`pro-*` to `flash-*-b` and `flash-medium-*`. This was WRONG.

**Corrected diagnosis**: Three independent sources confirm Pro was
actually used for the "Pro" proposer runs:

1. GeoJSON detection feature properties: `"model": "gemini-3.1-pro-preview"`
2. Log files: `"Model override: gemini-3.1-pro"` → `"resolved to 'gemini-3.1-pro-preview'"`
3. `cost_estimate.pricing_used.model`: `"gemini-3.1-pro-preview"`

**Pro proposer runs confirmed** (gemini-3.1-pro-preview):

- `pro-high-text-n5` (5 runs) — Pro HIGH text
- `pro-high-image-n5` (5 runs) — Pro HIGH image
- `pro-medium-text-baseline` (1 run) — Pro MEDIUM text
- `pro-medium-image-baseline` (1 run) — Pro MEDIUM image

**Verifier runs**: All verifier runs used `gemini-3-flash` (confirmed).
The "pro-verifier" label indicated Flash with medium thinking, not Pro
model. These have been renamed to `*-medium-verifier` (verifier side)
and `pro-*-minimal-verifier` / `pro-*-medium-verifier` (proposer side)
to reflect: Pro proposer + Flash verifier at minimal or medium thinking.

**Fix applied** (Session 57): Added `model_override` parameter to
`LLMMetadataTracker.__init__()`. Callers (`lib_batch_api.py`,
`run_pv.py`) now pass the resolved model name. Future meta.json files
will correctly reflect the actual model used.

**Directories renamed back** to original Pro labels (Session 57):

| Incorrect rename | Restored name | Actual model |
|-----------------|---------------|--------------|
| `flash-high-text-n5-b` | `pro-high-text-n5` | gemini-3.1-pro-preview |
| `flash-high-image-n5-b` | `pro-high-image-n5` | gemini-3.1-pro-preview |
| `flash-medium-text-baseline` | `pro-medium-text-baseline` | gemini-3.1-pro-preview |
| `flash-medium-image-baseline` | `pro-medium-image-baseline` | gemini-3.1-pro-preview |

**Lesson**: Never trust a single metadata field for audit purposes.
Cross-reference multiple independent sources (meta.json, GeoJSON
properties, log files, cost estimates) before concluding a run used the
wrong model. The audit prompt has been updated to check
`cost_estimate.pricing_used.model` as a secondary verification source.

---

### E43: consensus-384 executed at T=1.0 instead of T=0.7

| Field | Value |
|-------|-------|
| Date | 2026-03-25 (discovered during configuration audit) |
| Type | Deviation |
| Files | `outputs/h11/consensus-384-UNINTENDED-T1.0/` (renamed from `consensus-384/`) |
| Impact | 30 runs × 487 tiles executed at wrong temperature; corrected baseline produced separately |

**Description**: The H11 consensus-384 study was intended as a Flash MINIMAL
T=0.7 consensus baseline (30 runs, 384px). The study YAML specified
`fixed.temperature: 0.7` and `carried_forward.optimal_temperature: 0.7`,
but the prompt config `detect_brief-text.json` has `"temperature": 1.0`
hardcoded. The `run_phase2.py` orchestrator used the config's embedded
temperature rather than the YAML-specified value, resulting in all 30 runs
executing at T=1.0.

**Root cause**: Same config propagation failure as E44. The `temperature`
field in the prompt config JSON was treated as the default when the
`--temperature` CLI flag was not explicitly passed by `run_phase2.py`.

**Data disposition**: The T=1.0 data is preserved and used in the T=0.7 vs
T=1.0 temperature sensitivity analysis (Obs 190: dF1 ~+0.15, p<0.0001 at
all pool sizes — T=0.7 dramatically outperforms T=1.0). Directory renamed
to `consensus-384-UNINTENDED-T1.0` with explanatory README.

**Corrected baseline**: `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/`
(30 runs, 487 tiles, T=0.7, Flash MINIMAL, produced Session 56).

---

### E44: single-pass-384 executed at T=1.0 instead of T=0.0

| Field | Value |
|-------|-------|
| Date | 2026-03-25 (discovered during configuration audit) |
| Type | Deviation |
| Files | `archive/h11-unintended-t1.0/single-pass-384-UNINTENDED-T1.0/` (renamed from `single-pass-384/`; archived from `outputs/h11/` on 2026-05-29, H11 reorganisation) |
| Impact | 10 runs × 240 tiles executed at wrong temperature; corrected rerun in progress |

**Description**: The H11 single-pass-384 study was intended as a deterministic
T=0.0 single-pass baseline (10 runs, 240 tiles, Flash MINIMAL). Same config
propagation failure as E43: the YAML specified `fixed.temperature: 0.0` and
`carried_forward.optimal_temperature: 0.0`, but `detect_brief-text.json` has
`"temperature": 1.0` hardcoded and the CLI override was not applied.

**Data disposition**: Directory renamed to `single-pass-384-UNINTENDED-T1.0`
with explanatory README. Not used in any published analysis. Archived to
`archive/h11-unintended-t1.0/` on 2026-05-29 (H11 reorganisation; preserved,
not deleted — it is unused deviation data, so it leaves the active output
tree while the canonical deviation record stays here in this erratum).

**Corrected rerun**: `outputs/retest/h11-single-pass-384-t0/` (10 runs,
487 tiles — expanded to full evaluation area for consistency with consensus
analyses, T=0.0, Flash MINIMAL, Batch API). Submitted 2026-03-25.

---

### E45: Pairwise permutation test statistic changed from macro-average to micro-average F1

| Field | Value |
|-------|-------|
| Date | 2026-03-26 |
| Type | Deviation |
| Preregistration ref | Section 3.5 |
| Files | `scripts/pairwise_permutation_test.py` (new, replaces `scripts/paired_permutation_consensus.py`) |
| Impact | Different test statistic produces different ΔF1 and p-values for the same comparison |

**Description**: The preregistered pairwise permutation test (Section 3.5)
specifies tile-level resampling with a sign-flip permutation on per-tile
F1 differences. This computes the **macro-average** F1 difference — each
tile receives equal weight regardless of how many detections or references
it contains.

The generalised replacement script (`pairwise_permutation_test.py`) uses a
**tile-swap permutation** with **micro-average** F1 as the test statistic.
For each permutation, per-tile TP/FP/FN assignments are independently
swapped between conditions with probability 0.5, then TP/FP/FN are
aggregated across tiles to compute F1 for each permuted condition.

**Rationale for the change**:

1. **Consistency with reported F1**: All F1 values throughout the project
   (threshold sweeps, leaderboard, working notes) are micro-averages
   computed by `calculate_f1_internal()`. The macro-average test statistic
   produced a different ΔF1 from the reported ΔF1 for the same comparison
   (e.g., +0.007 macro vs +0.015 micro for the Pro verifier comparison).
   This inconsistency would be confusing in the paper.

2. **Standard practice in detection evaluation**: PASCAL VOC, COCO, and
   the remote sensing detection literature use micro-average F1 for method
   comparisons. Macro-average is unusual for object detection tasks.

3. **Information weighting**: With 487 evaluation tiles, ~347 contain zero
   reference mounds. In the macro-average, these tiles contribute noise
   (undefined or trivial F1 values). In the micro-average, they contribute
   zero TP/FP/FN — effectively receiving appropriate weight.

4. **Statistical power**: The macro-average dilutes the signal with ~347
   uninformative tiles, reducing power. The micro-average concentrates on
   tiles that contain detectable objects.

**The change preserves**:

- Tile-level exchangeability as the null hypothesis
- Permutation-based inference (exact Type I error under the null)
- Paired design (same tiles compared across conditions)

**What changes**:

- Test statistic: micro-average F1 difference (aggregate TP/FP/FN, then
  compute F1) instead of macro-average (per-tile F1, then average)
- Output key renamed: `observed_f1_diff` (was `observed_mean_diff`)
- The ΔF1 reported by the permutation test now matches the ΔF1 computed
  from the project's standard F1 reporting pipeline

**Validation**: The Pro verifier comparison (Flash HIGH text 4-of-5)
produces ΔF1=+0.015, p=0.019 with the micro-average test, compared to
ΔF1=+0.007, p=0.081 with the macro-average. The micro-average result
is consistent with the F1 values reported in the threshold sweep results
(0.879 − 0.864 = 0.015).

---

### E46: Primary spatial matching buffer changed from 20 m to 30 m

| Field | Value |
|-------|-------|
| Date | 2026-03-27 |
| Type | Deviation |
| Preregistration ref | Section 3.5 |
| Files | All evaluation scripts (`analyse_consensus_sweep.py`, `evaluate_pv_results.py`, `analyse_pv_buffer_sensitivity.py`) |
| Impact | Absolute F1/P/R values increase slightly; condition rankings unchanged |

**Description**: The preregistered evaluation buffer of 20 m is replaced
by 30 m as the primary spatial matching tolerance. 20 m results are
retained as a secondary strict-localisation analysis.

The spatial matching algorithm uses **centroid-to-centroid distance**:
each detection bounding box is reduced to its centroid, and the distance
to the hand-placed reference point (verified at ~1-2 px accuracy by the
first author) must fall within the buffer to count as a True Positive.
At 384 px tiles (~5 m/px), 30 m = 6 px — requiring the detection box
centre to fall within ~40% of the symbol diameter (~15 px) from the
true centre.

**Rationale for the change**:

1. **Symbol-scale analysis**: Burial mound symbols are ~15 px in
   diameter (~75 m on the ground). A 20 m buffer (4 px) requires the
   detection centroid to fall within ~1/4 of the symbol diameter. This
   threshold measures localisation precision as much as detection
   quality, penalising correctly-detected symbols whose bounding boxes
   are slightly off-centre.

2. **Modality-specific localisation plateaus**: Comprehensive buffer
   sensitivity analysis (Obs 196-197) showed that text-based detections
   plateau at 30 m (zero further F1 gain at 40, 50, 75, or 100 m) while
   image-based detections plateau at 50 m. At 20 m, the evaluation
   disproportionately penalises image detections for localisation error
   rather than detection quality. At 30 m, text detections fully express
   their detection quality while image detections recover the majority
   of their spatial error.

3. **Practical relevance**: The task is to flag map locations containing
   burial mound symbols for human verification. A 30 m offset (6 px on
   the map, ~30 m in the field) produces no ambiguity about which
   feature was detected — mound symbols in these maps are typically
   >100 m apart in clusters.

4. **Ranking stability**: Condition rankings are identical at all buffer
   distances from 20 m to 100 m. No comparative conclusion changes. The
   only effect is that absolute metrics rise slightly and the text-image
   performance gap narrows.

**The change preserves**:

- Centroid-to-centroid matching (not edge-to-point)
- Hungarian algorithm for globally optimal one-to-one assignment
- Per-map-sheet matching to prevent boundary effects
- All 20 m results available as secondary analysis

**What changes**:

- Primary F1/P/R values reported in the paper use 30 m buffer
- 20 m results reported as sensitivity analysis
- The text-vs-image modality gap is smaller at 30 m (reflects detection
  quality rather than localisation precision)

**Evidence**: Full multi-buffer evaluation at 20, 30, 40, 50 m for 16
conditions (8 consensus, 8 PV) on 487 tiles with 435 reference mounds.
Extended to 75 m and 100 m for image conditions to confirm plateau.
See `results/paper-tables/spatial_tolerance_comparison.md` and
Observations 196-198 in working notes.

---

### E47: Primary spatial matching buffer reverted to preregistered 20 m

| Field | Value |
|-------|-------|
| Date | 2026-03-29 |
| Type | Reversion (restores preregistered value) |
| Preregistration ref | Section 3.5 |
| Supersedes | E46 |
| Files | `scripts/run_pairwise_tests.py`, `scripts/evaluate_detections.py`, `scripts/compare_tile_sizes.py`, `configs/mcc-eval-384px.yaml`, `configs/tile-size-comparison.yaml`, `configs/condition-registry.yaml` |
| Impact | Absolute F1/P/R values decrease slightly; greater discrimination between conditions; condition rankings unchanged |

**Description**: The primary spatial matching tolerance is reverted from
30 m (E46) to the preregistered 20 m. The 30 m analysis remains
available and is recommended for production deployment, but 20 m is
used as the paper's headline tolerance.

**Rationale for the reversion**:

1. **Preregistration alignment**: The preregistered primary tolerance is
   20 m (Section 3.5). E46 changed this during analysis — reverting
   restores alignment with the registered protocol and avoids the
   appearance of post-hoc tolerance selection.

2. **Greater statistical discrimination**: At 20 m, the leaderboard
   round-robin (253 pairwise comparisons, FDR-corrected) produces a
   solitary Tier 1 (best condition alone), whereas at 30 m the top 3
   conditions are statistically indistinguishable. The tighter tolerance
   better separates conditions for comparative purposes.

3. **Conservative reporting**: 20 m is the more demanding evaluation.
   Reporting the harder metric as the headline and showing improvement
   at 30 m via the tolerance curve is more credible than the reverse.

**The paper will present**:

- 20 m as the primary (preregistered) evaluation tolerance
- A spatial tolerance curve from 20–50 m showing sensitivity
- An argument that 30 m (generalised to: minimum typical radius of
  the target symbol) is better suited for production workflows where
  the goal is flagging locations for human review, not measuring
  sub-symbol localisation precision

**The E46 rationale remains valid**: 30 m is a physically meaningful
threshold (~1 symbol radius) and the text-track plateau begins there.
The two tolerances answer different questions: 20 m measures detection
quality under strict localisation; 30 m measures practical detection
utility. Both are reported.

**Changes to defaults**: Script defaults and config files updated from
30 m to 20 m. The condition registry now includes threshold variants
for both 20 m and 30 m optimal consensus thresholds (two N=10
conditions have different optima at the two tolerances).

---

### E48: Section 8.4.1 HN target M=3 inconsistent with Scale-8 definition

| Field | Value |
|-------|-------|
| Date | 2026-04-15 |
| Type | Correction |
| Sections | §8.4.1 (line 1460), §8.4.2 (line 1514, table line 769) |
| Impact | None (internal inconsistency in preregistration text) |

**Description**: Section 8.4.1 specifies "Top M FPs (target M=3)" for hard
negative selection. However, the Scale-8 library composition table (§8.4.2,
line 769) defines Scale-8 as `HP=4, HN=4, Total hard=8`, and the category
ratio (line 1514) is explicitly stated as `4:2:4:4:3 = 17 examples`. The M=3
target is a stale draft value that was not updated when the library design
settled on Scale-8 (4+4). All H8 contrasts, the Scale-8 naming convention,
and the 1:1 HP:HN ratio specification (line 813) are built around HN=4.

**Resolution**: Use HN=4 (consistent with Scale-8 and the composition table).
The M=3 value in §8.4.1 is treated as a drafting error.

---

### E49: H10 calibration uses cold-start production config instead of preregistered image-only baseline

| Field | Value |
|-------|-------|
| Date | 2026-04-15 |
| Type | Deviation |
| Sections | §8.4.1 Step 1, H10 |
| Impact | Changes which examples are identified as "hard" |

**Description**: The preregistration specifies calibration runs using an
image-only baseline at T=1.0 with K=5 passes. The H10 v2 implementation
instead uses a cold-start production config with the following changes:

| Parameter | Preregistered | H10 v2 |
|-----------|---------------|--------|
| Temperature | T=1.0 | T=0.7 |
| Thinking level | (unspecified, implied minimal) | HIGH |
| Instruction file | image-only | detect_brief-text-image (text+image) |
| Examples | Full baseline library (17) | Cold-start: legend + nulls only (9) |
| Crop size | 128px | 150px (aligned with verifier standard) |

**Rationale**: The cold-start config better simulates a realistic deployment
scenario — a user approaching new maps with only legend reference images. The
production-quality settings (T=0.7, HIGH thinking) discover hard cases that
are genuinely hard for the configuration that will use them, avoiding the
confound of mining hard cases under an inferior config. The 150px crop size
aligns with the verifier crop standard (75px padding × 2).

---

### E50: H10 holdout expanded from 60 to 327 tiles

| Field | Value |
|-------|-------|
| Date | 2026-04-15 |
| Type | Deviation |
| Sections | H10 (lines 914-919) |
| Impact | Increased statistical power |

**Description**: The preregistration specifies a 60-tile holdout for H10
evaluation. The actual holdout is 327 tiles — the remainder after removing
160 calibration tiles from 487 total. This expansion results from the move
to 384px tiles (E36/H11), which increased the total tile count from 361
(at 512px) to 487 (at 384px). The calibration pool sizes (20, 40, 80, 160)
remain as preregistered; only the holdout expanded.

**Rationale**: The original 60-tile holdout was found to have insufficient
statistical power for detecting pool-size effects. The 327-tile holdout
provides substantially more power while maintaining the preregistered
calibration/holdout disjointness constraint.

---

### E51: H8 library composition re-run under production carry-forward (384 px / v2 pipeline)

| Field | Value |
|-------|-------|
| Date | 2026-04-15 |
| Type | Deviation |
| Sections | §8.3.4 H8, Phase 2c |
| Impact | Changes the evaluation pipeline on which H8 results are reported; re-enables Scale-16/Scale-32 |

**Description**: The original H8 (Phase 2c, completed 2026-02-09) ran at 512 px
tiles with prereg carry-forward parameters (T=0.0 from H7, minimal thinking per
Decision 2, canonical-first ordering) and deferred Scale-16 and Scale-32 due to
HP pool exhaustion (E11 — only 4 hard positives available under the v1 mining
definition). The v2 re-run (Phase h8-v2, launched 2026-04-15) instead uses:

| Parameter | Original H8 (Phase 2c) | H8 v2 |
|-----------|------------------------|-------|
| Tile size | 512 px | 384 px |
| Stride | 448 px | 336 px |
| Temperature | T=0.0 (H7 optimum) | T=0.7 (production carry-forward) |
| Thinking level | Minimal | HIGH |
| Instruction file | detect_brief-text-image.md | detect_brief-text-image.md (unchanged) |
| K (passes) | 10 | 5 (production n=5 consensus) |
| Service tier | standard | **flex** (50 % off-peak discount) |
| Context caching | none | **enabled** (reduces input cost 50–90 %) |
| Hard-example crop size | 128 px (v1) | 150 px (v2, verifier-aligned) |
| Hard-case register | v1 (pool_160, 63 HP / 151 HN) | v2 (pool_160, 108 HP / 57 HN) |
| Scale-16 | DEFERRED (HP pool exhausted) | **RE-ENABLED** (pool_160_hp8hn8) |
| Scale-32 | DEFERRED (HP pool exhausted) | **RE-ENABLED** (pool_160_hp16hn16) |
| Evaluation manifest | `inputs/tiles/validation_manifest.json` (60 tiles @ 512 px) | `inputs/calibration/h10-384/test_manifest.json` (327 tiles @ 384 px) |

The v2 re-run also reuses the existing H10 v2 `pool_160_hp4hn4` run as the
Scale-8 condition. Prefix nestedness of greedy example selection was verified
on 2026-04-15 by byte-hash of the first 4 HP/HN crops across hp4hn4, hp8hn8,
and hp16hn16 pools — all identical. Model, temperature, thinking, instruction,
K, manifest, and tile size are identical between H10 v2 `pool_160_hp4hn4` and
H8 v2 `scale-8`, so the existing `outputs/h10/evaluation-v2/pool_160_hp4hn4/`
run_1..run_5 directories are referenced directly in H8-v2 analysis rather than
re-launched.

**Rationale**: Three independent motivations converge on the re-run.

1. **Pipeline alignment.** H11 closed the 384 px pathway (E41) and the
   production proposer is now 384-tile. The original 512 px H8 numbers are
   off-pipeline and cannot be directly compared with downstream work. Re-running
   at 384 px restores comparability with H10 v2 and the 55-maps generalisation
   study (F1=0.891 on gold standard, 2026-04-08).
2. **HP pool exhaustion resolved.** The v2 hard-case register (mined under
   production image-track settings from the 160-tile calibration pool)
   yields 108 HP / 57 HN, both sufficient for Scale-32 (16 HP + 16 HN) with
   comfortable diversity-selection headroom. Scale-16 and Scale-32 were
   preregistered and can now be executed as originally intended.
3. **Internal consistency with H10 v2.** H10 v2 used the production carry-
   forward settings (T=0.7, thinking=high) rather than the prereg H7 optimum
   (T=0.0, thinking=minimal). Running H8 v2 under the same settings keeps
   the library-composition story on a single pipeline: H10 asks whether
   calibration-pool size matters (null, 2026-04-14); H8 v2 asks whether
   library composition matters; H12 v2 will ask whether HP:HN ratio matters
   at the H8-selected optimum.

The K=5 reduction from the preregistered K=10 matches production n=5 consensus
voting (validated in the 55-maps study) and halves the API spend without
sacrificing the ability to detect library-composition effects larger than
prior-phase noise.

**Reference artefacts**:

- Study YAML: `studies/h8-v2-library.yaml`
- Per-condition configs: `prompts/configs/h8/v2/detect_h8_*_v2.json` (7 files)
- v2 pool mining provenance: `outputs/h10/example-pools-v2/pool_160_hp{4hn4,8hn8,16hn16}/pool_metadata.json`
- Retrospective informing the re-run: `docs/notes/reflections/2026-04-14-h10-h12-config-intent-retrospective.md`
- Formal retraction of the v1 H10/H12 pass: Obs 235 (2026-04-14)

**Runtime parallelism note (2026-04-15)**: The H8 v2 launch uses
`--workers 250` on Tier 3 API quota (20 M TPM / 20 K RPM), targeting ~72 %
TPM utilisation via the existing token-bucket governor
(`scripts/lib_token_bucket.py`). The detect script's hard-coded thread-pool
ceiling of 60 was the binding constraint at Tier 2 (observed peak 4.12 M TPM
= 20.6 % utilisation), bottlenecking on worker availability rather than on
rate limits. The ceiling has been changed to `max(60, workers)` when the
governor is active, preserving backward compatibility while allowing
runtime scaling via `--workers N`. Parallelism is an operational parameter
and does not affect the content of the API payload; it does not impact the
experimental validity of the results. Recorded here for reproducibility.

**Edge-of-raster exclusion fix (2026-04-15)**: During the pre-launch audit of
the H8 v2 configs, three crops in the initial `pool_160_hp16hn16` mining were
found to be clipped by the raster boundary (`hp_11.png` 95 × 150, `hn_11.png`
150 × 100, `hn_16.png` 150 × 149). This created a Scale-32-specific
dimensional-uniformity confound that would have muddied the interpretation of
the S3 (Scale-16 → Scale-32) contrast. Resolution: `scripts/build_example_pool.py`
was extended with an `--exclude-edge-crops` flag (default on) that pre-filters
candidates whose `crop_size` window would extend beyond the source raster's
pixel grid. Both `pool_160_hp8hn8` and `pool_160_hp16hn16` were re-mined with
the filter. `pool_160_hp8hn8` picks are byte-identical to the pre-filter
mining (none of the top 8 HP or HN candidates were edge cases, so the filter
was a no-op at this rung); `pool_160_hp16hn16` preserves picks 1–10 and
shifts picks 11–16. Prefix nestedness (pool_160_hp4hn4 ⊂ pool_160_hp8hn8 ⊂
pool_160_hp16hn16) is preserved for both HP and HN. Pre-filter pools archived
to `archive/h10-v2-prefilter-pools/`. Audit report:
`reports/configuration-audit-2026-04-15-h8-v2.md`.

### E52: H12 HP:HN ratio re-run under production carry-forward (384 px / v2 pipeline)

| Field | Value |
|-------|-------|
| Date | 2026-04-15 |
| Type | Deviation + deferral resolution |
| Sections | §H12 (preregistration lines 980–1011), Decision 11 (decisions-log.md) |
| Impact | Runs H12 at production carry-forward settings with R2 reused from H8 v2 Scale-8; resolves the Decision 11 deferral; relaxes the "H8 shows library size matters" trigger |

**Description**: The preregistered H12 (hard-positive to hard-negative ratio)
was formally deferred on 2026-02-02 in decisions-log entry 11 because the v1
hard-positive pool was structurally exhausted at 4 examples under the 50 m
recognition/localisation threshold. Under Decision 11, the only testable
ratios were HP-constant with varying HN (e.g., 4:4, 4:8), which confounds
ratio with total hard count. H12 was deferred until H10 had expanded the HP
pool via calibration tile expansion.

**Deferral resolved**: The v2 hard-case register mined on 2026-04-15 from
H10's pool_160 (`outputs/h10/hard-cases-v2/pool_160/hard_cases_register.json`)
yields **108 hard positives and 57 hard negatives** after the edge-of-raster
exclusion filter, well above the HP ≥ 6 required for the symmetric 3:1
HP-heavy extreme. The full preregistered H12 condition matrix is therefore
executable:

| Condition | HP | HN | Total Hard | Ratio |
|-----------|----|----|------------|-------|
| R1 | 2 | 6 | 8 | 1:3 (HN-heavy) |
| R2 | 4 | 4 | 8 | 1:1 (balanced) |
| R3 | 6 | 2 | 8 | 3:1 (HP-heavy) |

**Trigger deviation**: H12's preregistered trigger is "run if H8 shows library
size matters" (preregistration line 1010). H8 v2 (completed 2026-04-15,
Observation 238) returned a null result: all seven library-composition
contrasts (C1, C2, C3, B1, S1, S2, S3) null after Benjamini–Hochberg FDR
correction at q = 0.05, with an F1 spread of only 0.040 across all seven
conditions at greedy consensus threshold t = 4. Strictly read, the trigger is
not met.

H12 is being run anyway for two reasons:

1. **Orthogonal axis.** H8 tests library *size* and *composition* (the number
   of hard examples, and their canonical/empirical mix). H12 tests the
   *balance* between hard positives and hard negatives at fixed total. A null
   effect on size does not imply a null effect on balance, and the
   preregistered secondary analysis (precision vs. recall differential;
   preregistration line 1007) predicts a directional effect even in the
   absence of an overall F1 difference.
2. **Null results are publishable.** A null ratio result corroborates the H8
   v2 null: together they close the library-design story for the write-up
   with two independently-preregistered axes. Deferring H12 would leave that
   story incomplete.

**Parameter deviations** (applied to match H8 v2 and H10 v2, per E49/E50/E51):

| Parameter | Original H12 prereg (carried from H7/H8) | H12 v2 |
|-----------|------------------------------------------|--------|
| Tile size | 512 px | 384 px (E41/E51) |
| Stride | 448 px | 336 px (E51) |
| Temperature | T = 0.0 (H7 optimum) | T = 0.7 (production carry-forward, E49/E51) |
| Thinking level | Minimal (Decision 2) | **HIGH** (E49/E51) |
| Instruction file | detect_brief-text-image.md | detect_brief-text-image.md (unchanged) |
| K (passes) | 10 | **5** (production n = 5 consensus; E49/E51) |
| Service tier | standard | **flex** (50 % off-peak discount) |
| Context caching | none | **enabled** (reduces input cost 50–90 %) |
| Hard-example crop size | 128 px (v1) | **150 px** (v2, verifier-aligned) |
| Evaluation manifest | 60-tile validation holdout | **327-tile h10-384 test manifest** (E50) |

**R2 reuse**: R2 (4 HP + 4 HN) is byte-identical to H8 v2 Scale-8, which is
itself the existing H10 v2 `pool_160_hp4hn4` run. Prefix nestedness of
greedy-diversity example selection was verified on 2026-04-15 by
`sha256sum` across `pool_160_hp4hn4`, `pool_160_hp8hn8`, and
`pool_160_hp16hn16` for `hp_01..hp_04` and `hn_01..hn_04` — all hashes
identical. Model, temperature, thinking, instruction, K, manifest, and tile
size are identical between H10 v2 `pool_160_hp4hn4`, H8 v2 `scale-8`, and
H12 v2 `r2-balanced`, so R2 is NOT re-launched. Analysis references the
existing `outputs/h10/evaluation-v2/pool_160_hp4hn4/run_{1..5}/` directories
directly.

**No new example pools are built.** R1 (HP=2, HN=6) and R3 (HP=6, HN=2) both
reference the existing `inputs/examples/h10-v2/pool_160_hp8hn8/` crops
(`hp_01..hp_06.png` and `hn_01..hn_06.png`). Because prefix-nested greedy
selection with `seed=42` is deterministic, these bytes are identical to what
`build_example_pool.py --hp-count 2 --hn-count 6` or `--hp-count 6 --hn-count 2`
would produce as dedicated `pool_160_hp2hn6` / `pool_160_hp6hn2` directories.
This mirrors the H8 v2 Scale-16 pattern, which references `pool_160_hp8hn8`
directly rather than building a dedicated `pool_160_hp8hn8` alias.

**Analysis aggregation**: Greedy consensus at t = 4 is the primary / headline
aggregation method for H12 (user preference, 2026-04-15); WBF variant C
(Obs 228–230 parameters) is reported alongside as the secondary method so
H12 results remain directly comparable to H8 v2 and H10 v2 (both of which
were analysed under WBF variant C as the primary method). BH-FDR-corrected
pairwise contrasts (R1 vs R2, R2 vs R3, R1 vs R3) at q = 0.05 are computed on
the greedy primary metric.

**Reference artefacts**:

- Study YAML: `studies/h12-v2-ratio.yaml`
- Per-condition configs: `prompts/configs/h12/v2/detect_h12_{r1-hn-heavy,r2-balanced,r3-hp-heavy}_v2.json`
- Pre-launch audit (via `/audit-config`): 2026-04-15 session — all technical checks PASS
- Retrospective informing the v1 retraction: `docs/notes/reflections/2026-04-14-h10-h12-config-intent-retrospective.md`
- Formal retraction of the v1 H10/H12 pass: Obs 235 (2026-04-14)
- H8 v2 null-result source: Obs 238 (2026-04-15)
- Decision 11 (HP pool exhaustion, now resolved): `docs/methodology/preregistration/decisions-log.md` §11

**Runtime parallelism note (2026-04-15)**: H12 v2 uses `--workers 250` on
Tier 3 quota, matching H8 v2 (Session 68 observed ~72 % TPM utilisation with
zero 429 errors at that worker count). Parallelism is an operational
parameter; it does not affect the content of the API payload and does not
impact experimental validity.

---

### E53: Phase 3a-HIGH image track moved from 512 px (Era 1) to 384 px (Era 2)

| Field | Value |
|-------|-------|
| Date | 2026-04-16 |
| Type | Deviation |
| Sections | §H3 (preregistration lines 497–531), Phase 3a study YAML |
| Impact | H3 image-track consensus analysis reported on Era 2 scope (487 tiles, 384 px) rather than Era 1 (340 tiles, 512 px) |

**Description**: The preregistered Phase 3a study
(`studies/retest/phase3a-h3-voting-track1-high.yaml`) defined K = 30
consensus voting experiments for the image track at 512 px (Era 1, 340
tiles) with HIGH thinking at T = 0.3, T = 0.7, and T = 1.0. The study
manifest was generated (2026-03-18) and run directories created, but the
detection runs were never launched. The text-track counterpart completed
(90/90 runs). The image track was queued behind the text track and
deprioritised when the project moved to Phase 3c, H11, and the v2
hypothesis series.

Investigation during Session 70 (2026-04-16) revealed that:

1. **The same experiment already exists at 384 px.** The H11 PV-diag
   condition `flash-high-image-n5` (Flash, HIGH thinking, image track,
   plus-hp library, T = 0.7, K = 10) was run on the full 487-tile 384-px
   evaluation manifest. A matched MINIMAL-thinking condition (`image-n5`)
   also exists at T = 0.7 with K = 10.

2. **The archived 60-tile preliminary data was mislabelled.** The
   pre-retest `track1-image-high` directory (archived at
   `archive/outputs-pre-retest-60-tile/phase3a/track1-image-high/`) was
   labelled as HIGH thinking but the study notes confirm it "actually used
   minimal thinking" (study YAML `retest_notes` field).

3. **The library-design axis is null** (Obs 240). All 10 library-design
   conditions span F1 = 0.688–0.733 with zero significant pairwise
   differences after BH-FDR. Temperature and thinking-level findings from
   the plus-hp library transfer to the scale-4 generalisation library.

**Resolution**: The 512-px experiment is omitted. Instead, a complete
2 × 4 thinking × temperature matrix is run at 384 px (487 tiles) using
the existing H11 infrastructure:

| | T = 0.0 (K = 3) | T = 0.3 (K = 10) | T = 0.7 (K = 10) | T = 1.0 (K = 10) |
|---|---|---|---|---|
| **HIGH** | New | New | Exists | New |
| **MINIMAL** | Exists | New | Exists | New |

This design provides: (a) clean paired HIGH vs MINIMAL comparison at three
consensus-relevant temperatures; (b) T = 0.0 baselines for both thinking
levels; (c) N = 5 and N = 10 consensus threshold sweeps at each cell.

**Justification**:

1. **More informative than the original design.** The 512-px study tested
   only HIGH thinking at three temperatures. The 384-px matrix adds the
   MINIMAL comparison, enabling direct quantification of the thinking-level
   effect on consensus voting — the key scientific question.

2. **Consistent evaluation scope.** The 384-px data integrates cleanly with
   the Era 2+3 leaderboard (H8 v2, H10 v2, H11, H12 v2). H11 provides the
   tile-size bridge (384 px vs 512 px) for cross-era comparison.

3. **Library choice is orthogonal.** Obs 240 confirms that library
   composition does not interact with detection performance at the proposer
   stage. Findings about optimal T and thinking level on the plus-hp library
   will transfer to the scale-4 library used in the generalisation run.

**Parameter summary**:

| Parameter | Original Phase 3a-HIGH (512 px) | E53 replacement (384 px) |
|-----------|--------------------------------|--------------------------|
| Tile size | 512 px | 384 px |
| Tiles | 340 (Era 1) | 487 (Era 2 full evaluation) |
| K | 30 | 10 (K = 30 if needed after initial analysis) |
| Temperatures | T = 0.3, 0.7, 1.0 | T = 0.0, 0.3, 0.7, 1.0 |
| Thinking levels | HIGH only | **HIGH + MINIMAL** |
| Config | library_plus-hp-high.json | library_plus-hp.json + CLI override |
| Execution mode | Not specified | Realtime flex + context caching |
| Workers | Not specified | 250 (Tier 3 standard) |

**Reference artefacts**:

- Launcher script: `scripts/run_phase3a_image_matrix.sh`
- Config: `prompts/configs/library_plus-hp.json`
- Existing HIGH T = 0.7: `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/`
- Existing MINIMAL T = 0.7: `outputs/h11/pv-diag-384/image-n5/image-t0.7/`
- Pre-launch audit (via `/audit-config`): 2026-04-16 Session 70
- Library-design null: Obs 240 (2026-04-16)
- Mislabelling discovery: Session 70 investigation of empty `outputs/retest/phase3a-high/track1-image/`

---

### E54: Bootstrap iteration count — preregistered 1 000 for primary F1, post-hoc 10 000 for narrow-effect analyses

| Field | Value |
|-------|-------|
| Date | 2026-04-21 |
| Type | Clarification |
| Commit | TBD |
| Impact | None (preregistered methodology unchanged) |

**Description**: The preregistration (Section 3.5) specifies bootstrap resampling at **1 000 iterations** with the percentile method (2.5th / 97.5th) and tile-level resampling. All scripts that evaluate preregistered conditions — `evaluate_detections.py`, `compute-pairwise-effect-sizes.py`, `evaluate_pv_results.py`, `compare_wbf_vs_greedy.py`, `analyse_secondary_effects_text.py`, and the shared `lib_advanced_metrics.bootstrap_ci` default — use 1 000 iterations, matching the preregistration.

Several **post-hoc** analyses (not specified in the preregistration) use **10 000 iterations** instead. These analyses are characterised by narrow effect sizes where CI precision at 2-3 decimal places is material for narrative clarity:

- `compute_corrected_f1_human_reviewed.py` — human-reviewed corrected F1 lower bound (effect size ~0.06 above measured F1; CI half-width would be ~±0.01-0.02 at 1 000 iter, ~±0.003-0.006 at 10 000)
- `compute_corrected_f1_multi_buffer.py` — multi-buffer extension of the same analysis (same rationale)
- `analyse_subtype_classification.py` — per-class subtype F1 with CIs (several per-class F1s sit in a 0.02-0.05 window; tighter CIs improve separability)
- `crosstab_uncalibrated_vs_calibrated.py` — review-UI disagreement-rate CI (disagreement ~21 %; narrow effect size)
- `analyse_buffer_band_lift.py` — within-tile permutation test, M = 1 000 matches the preregistered convention for permutation-derived null envelopes (noted here for completeness — this one follows the 1 000 default)

**Rationale for the split**:

1. **The preregistration locks 1 000 for primary evaluation** — any deviation on preregistered conditions would require a deviation-class errata entry, not a clarification. The 1 000-iteration setting remains untouched for those.
2. **10 000 is selectively applied to post-hoc analyses where CI precision determines narrative clarity** — the preregistration does not constrain methodology for analyses it did not specify.
3. **Runtime is not a binding constraint for post-hoc analyses**: they run once on a single corpus, not across the hundreds-of-conditions leaderboard matrix. The 10× cost is absorbable for a one-off authoring run.

**Paper methods wording (suggested)**:

> Confidence intervals on primary F1, precision, and recall are derived from 1 000-iteration tile-level bootstrap resampling (preregistered Section 3.5, percentile method 2.5th / 97.5th). Post-hoc analyses — human-reviewed corrected F1 (single- and multi-buffer), subtype classification, and review-UI calibration cross-tabs — use 10 000 iterations to tighten CIs on narrow effect sizes; the resampling unit and percentile method are unchanged.

**Reference artefacts**:

- Preregistration Section 3.5: `docs/methodology/preregistration/decisions-log.md:337`
- Primary bootstrap defaults: `scripts/evaluate_detections.py` (`DEFAULT_BOOTSTRAP = 1000`); `scripts/lib_advanced_metrics.py::bootstrap_ci` default `n_iterations = 1000`
- Post-hoc 10 000-iteration scripts: enumerated above
- CI-metadata registry (per-file iteration count): `results/ci-metadata-registry.md`

---

### E55: Verifier-t-pilot T0.5/T1.0 metadata under-recorded the swept temperature

| Field | Value |
|-------|-------|
| Date | 2026-05-30 |
| Type | Metadata correction (non-destructive) |
| Commit | TBD |
| Impact | Low — exploratory pilot (H2); corrected at source and in the manifest |

**Description**: The verifier-temperature pilot `outputs/verifier-t-pilot/` swept the verifier temperature via a CLI `--temperature` override. For the two new executions (`T0.5`, `T1.0`), the override was applied to the API call and logged in `run.log` (`Temperature override: 0.50` / `1.00`), but it was **not written back into the serialised `run.meta.json`**, whose `configuration.temperature` (and `configuration.full_config_snapshot.temperature`) retained the base-config default of `0.0`. Reading the temperature from the meta alone would therefore mis-record the very parameter the pilot varies.

**Verification**: the override genuinely took effect — across the 607 shared candidates, 348 (57 %) of mound probabilities differ between `T0.5` and `T1.0` (`probabilities.json` → `results`). The `T0.0` arm has no `run.meta.json` (it reuses the existing T=0.0 baseline verifier).

**Blast radius**: a scan of every `run.log` under `outputs/` for `Temperature override:` returns **only these two files**. No other run swept temperature by CLI override; all other runs set temperature in their config/study YAML, where the meta records it faithfully. The class of error is confined to this pilot.

**Root cause**: the verifier runner applied the `--temperature` CLI override to the request but serialised the unmodified base-config object into `run.meta.json` (the override was not merged into the snapshot before writing).

**Resolution (option R2, non-destructive)**:

1. The original `configuration.temperature: 0.0` is **left untouched** (a faithful record of what the runner serialised).
2. An additive `configuration.temperature_effective` (0.5 / 1.0) and a `configuration._correction` block (true value, `run.log` source, this erratum, date) were added to each meta, so a direct reader of the raw file sees the execution truth.
3. The manifest generator records the true temperature for these verifier passes, with `provenance.source_files` listing both `run.meta.json` and `run.log`. The extractor gains a general rule: prefer a logged CLI override over the meta `configuration` field (GAP-10).

**Reference artefacts**:

- Affected metas: `outputs/verifier-t-pilot/{T0.5,T1.0}/run.meta.json` (`configuration.temperature_effective`, `configuration._correction`)
- Ground truth: `outputs/verifier-t-pilot/{T0.5,T1.0}/run.log` (`Temperature override:`)
- Manifest design / extractor rule: `planning/manifest-schema-design.md`; `planning/run-registry-draft-review.md` (GAP-10)

---

*End of errata. New entries should be appended above this line.*

---

### E56: Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated

| Field | Value |
|-------|-------|
| Date | 2026-06-02 |
| Type | Methodological clarification (threshold provenance) |
| Commit | TBD |
| Impact | Medium — governs how diagnostic operating points are reported; the headline pipeline is unaffected (binary verdict) |

**Description**: The headline proposer-verifier pipeline (gold-standard-v2) applies the verifier as a **binary accept/reject verdict** — its `verified` condition records `prob_threshold = null`, so no probability cutoff is tuned. The preregistered calibrate-then-test split governs the **consensus vote threshold** (Phase 1 baseline calibration on the 20 held-out calibration tiles, ≥3/5).

The verifier's continuous `mound_probability` is explored only in the **diagnostic** runs (pv-diag-384 / the Session 78 verifier-calibration matrix). There the per-cell operating point `(vote_t, prob_t)` is selected by sweeping the grid and taking the F1-optimum at the 20 m buffer — and that selection is performed **on the 487-tile evaluation scope, which is the test set** (`scripts/score_leaderboard_cells.py`; `results/verifier-calibration-matrix/README.md` Phase B). There is **no calibration-tile verifier data** to select on: the verifier never ran on the 20 calibration tiles (excluded from the 487-tile scope; pv-diag ∩ calibration = 0). So any single `prob_t`-thresholded F1 quoted for these diagnostics is an **in-sample, test-set-optimised** number, not a calibrated one.

**Verification**: gs-v2 `verified-v1` carries `prob_threshold: null` (`results/run-conditions.json`); the 487-tile `full_evaluation_bounds` has zero overlap with the 20-tile `inputs/tiles/calibration_manifest.json`; the pv-diag text pool (471 covered tiles) contains none of the 20. The 2026-06-02 sweep (`results/rescore-2026-05-31/pv-diag-384/sweep/`) shows the F1@20 curve is **flat in the operating range** — single-run-PV ≈0.74 across prob_t 0.25–0.40, consensus-PV ≈0.86 across 0.15–0.20 — so a fixed reference threshold (0.20: 0.718 / 0.861) and the in-sample optimum (0.25: 0.740 / 0.15: 0.864) differ by ≤0.022 F1.

**Blast radius**: every `prob_t`-thresholded operating point in the verifier-probability diagnostics — the 14 `*-opt-20m.geojson` Session 78 cells, the h10 / h8-v2 / verifier-t-pilot `detections_vt*_pt*` materialisations, and the pv-diag-384 PV quadrants. The **headline** proposer-verifier results (binary verdict) and **all consensus-vote-threshold** results (preregistered, calibration-selected) are NOT affected.

**Reporting rule (resolution)**:

1. Report the headline proposer-verifier result at the **binary verdict** (`prob_t = null`), per gs-v2 and the preregistered design.
2. Present the verifier-probability diagnostics as **threshold-sensitivity curves**, not single F1 maxima. Where one operating point is quoted, state explicitly that it is the **20 m test-set F1-optimum (in-sample)** and give the fixed-reference value beside it; the curve's flatness (≤0.022 F1 across the plateau) makes the two interchangeable for the well-calibrated text track.
3. State plainly, in the paper and all supporting materials, **when and how each threshold was set**: vote threshold → preregistered, calibrated on the 20 held-out tiles; verifier binary verdict → no tuning; verifier `prob_t` operating points → in-sample on the 487-tile test set (diagnostic only).
4. The text-track verifier is well-calibrated (AUC 0.956, ECE 0.071); the image track is not (AUC 0.86, ECE 0.18; Obs 269, 277) — so a fixed threshold transfers on text but not image. Cite this for any image-track operating point.

**Reference artefacts**: `results/verifier-calibration-matrix/README.md` (Phase B); `results/run-conditions.json` (gs-v2 `prob_threshold: null`); `inputs/tiles/calibration_manifest.json`; `results/rescore-2026-05-31/pv-diag-384/sweep/`; working-notes Obs 269 + 277; `planning/session-78-matrix-calibration-summary.md`.

---

### E57: H11 384px Pro/baseline detection metadata — model template default and output_dir overrides

| Field | Value |
|-------|-------|
| Date | 2026-06-02 |
| Type | Metadata correction (non-destructive) |
| Commit | TBD |
| Impact | Low — provenance legibility only; run/model identity recoverable from eval input_files + study manifests |

**Description**: Two metadata artefacts in the H11 384px single-pass baseline pools (the N=1 baseline matrix, `results/paper-eval/n1/384px-all-buffers/`, sourced from pv-diag-384 ×10, n1-outstanding-384 ×7, retest-h11-single-pass-384-t0 ×1):

1. **`config.model` template default** — the per-detection `.meta.json` `configuration.model` reads `gemini-3-flash` / `gemini-3-flash-preview` even for the four **Pro** pools (e.g. `pro-text-medium-t-0-0`, `pro-image-medium-t-0-0`), whose `study_manifest.json` describes a Gemini 3 Pro single-pass proposer. The field is an unreliable template default that does not reflect the model actually dispatched.
2. **Study `output_dir` overridden at runtime** — e.g. `studies/h11-384-pro-medium-text-baseline.yaml` declares `output_dir: outputs/h11/pv-diag-384/pro-pilot-text`, but the actual (eval-referenced) directory is `outputs/h11/pv-diag-384/pro-medium-text-baseline`; the declared `pro-pilot-*` dirs do not exist on disk.

**Verification**: traced by a background investigation (2026-06-02) over all 18 pool dirs via each eval's `_metadata.input_files.detections` + `configs/n1-eval-384px-all-buffers.yaml` + the per-study `studies/h11-384-*.yaml`. The eval `input_files` paths are internally consistent and are the ground truth for run identity.

**Blast radius**: the four Pro pools (model field) and the two `pro-*-baseline` study YAMLs (output_dir). Detection geometries and scores are unaffected — only the model-of-record and the declared output path are mis-stated in the raw artefacts.

**Root cause**: the proposer runner serialised the base-config `model` without merging the per-study Pro override; and the study `output_dir` was overridden by a runtime flag not written back into the YAML.

**Resolution (non-destructive)**:

1. Leave the raw `.meta.json` and study YAMLs untouched (faithful records of what was written).
2. Treat the eval `_metadata.input_files.detections` path + the `study_manifest.json` description as ground truth for run/model identity — NOT `config.model` or the YAML `output_dir`.
3. When the N=1 baseline pools are authored into the manifest (continuity Session 95 to-do #3), record the **model-of-record** as a derived field from the study manifest, with provenance noting the `config.model` template-default caveat.

**Reference artefacts**: `configs/n1-eval-384px-all-buffers.yaml`; `studies/h11-384-pro-medium-text-baseline.yaml`; `results/paper-eval/n1/384px-all-buffers/*/evaluation.json` (`_metadata.input_files`); run-registry entries for pv-diag-384 / n1-outstanding-384 / retest-h11-single-pass-384-t0.
