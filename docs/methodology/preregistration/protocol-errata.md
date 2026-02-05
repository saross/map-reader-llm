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

*End of errata. New entries should be appended above this line.*
