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

*End of errata. New entries should be appended above this line.*
