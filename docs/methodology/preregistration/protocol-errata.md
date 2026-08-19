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

### E10: 50m recognition/localisation threshold — post-hoc narrowing of the registered HP definition (reclassified 2026-07-28)

| Field | Value |
|-------|-------|
| Date | 2026-02-02 (original); **reclassified 2026-07-28** |
| Type | Deviation (originally recorded as Clarification) |
| Files | `outputs/phase1-library/fp-fn-register.md`, `docs/methodology/preregistration/decisions-log.md` (Decision 11) |
| Impact | Determines which FNs qualify as hard positive candidates |

**Description (corrected 2026-07-28, D17 audit FALSE-20)**: the preregistration draws hard positives from false negatives (`osf/preregistration.md:1450` "Ground truth mounds missed in ≥3/5 passes"; `:1510` "FN mining") **without distinguishing recognition failures from localisation errors** — under the registered definition, a mound detected but mislocalised beyond the tolerance is an FN and an eligible HP candidate. The recognition/localisation distinction and its threshold are post-hoc additions (the project's own notes agree: `working-notes.md:1471` calls it "a distinction the preregistration did not anticipate"). This entry originally described the distinction as registered; that description is withdrawn.

Analysis of the Phase 1 FN distance distribution revealed a distributional cliff between 30m and 50m: below 30m, FNs cluster tightly (clear localisation errors); above 50m, FNs are sparse and widely dispersed (clear recognition failures). The 30–50m range is ambiguous. A 50m threshold was selected as the boundary, yielding 9 recognition failures and 15 localisation failures from 24 total FNs.

**Protocol impact (corrected 2026-07-28)**: this deviation **narrows the registered HP pool** — restricting HP selection to recognition failures reduced the pool to 4, which cascaded into E11 (Scale-16/32 deferred), E12 (H9 image diversity reduced to HN-only), and E13 (H12 deferred). The narrowing is empirically motivated (distributional cliff, Decision 11) but unregistered. E51 later re-mined 108 HP under a v2 definition and re-enabled Scale-16/32, partly undoing the cascade.

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

### E16: Prompt text shifted from cartographic naming to visual descriptions (corrected 2026-07-30)

| Field | Value |
|-------|-------|
| Date | 2026-02-03 (original); **corrected 2026-07-30** — see Correction |
| Type | Clarification |
| Commit | `2d46311` |
| Files | All 10 `prompts/system-instructions/detect_*.md` files |
| Impact | Changes wording of preregistered prompt text without altering prompt structure or factor design |

**Correction (2026-07-30)**: this erratum's "Scope of changes" states that "The prompt
structure (preamble, decision procedure, exclusion categories), factor design (H5
levels, M/E levels), and example library are unchanged", and its Protocol impact states
that "the set of features being described and the diagnostic logic (ray
presence/absence, direction of marks) are preserved". **The "unchanged" and "preserved"
claims are inaccurate as they stand.** Commit `2d46311`, which this erratum records, did
not only reword existing material: it **added three new exclusion sections**, enumerated
in the commit's own message:

| Commit-message change | New section added |
|-----------------------|-------------------|
| "Change 2B — Cyrillic text: New exclusion items (terse bullet + verbose subsection) flagging Cyrillic characters as a confound." | `### Cyrillic Map Text` |
| "Change 3 — Round shapes: New catch-all exclusion for round/ovoid shapes in mound-like colours without outward-radiating rays." | `### Other Round Shapes in Mound-Like Colours` |
| "Change 4B — Dense features: New "Symbols Amid Dense Features" subsection in verbose files." | `### Symbols Amid Dense Features` |

All three headings are verifiable as additions in `git show 2d46311 --
prompts/system-instructions`. The same commit also inserted a new diagnostic principle
("Opus P3b — Insert visual-diagnostic-principle in Core Diagnostic: 'Base all detections
on the visual sunburst diagnostic only.'").

**The correct characterisation** is therefore: the *exclusion categories were extended*,
not held constant, and *the set of features being described was enlarged* — Cyrillic map
text, round/ovoid shapes without rays, and dense-feature contexts were not described in
the lodged appendix text at all. What genuinely is unchanged is the **factor design**
(H5 levels, M/E levels) and the **example library**; and the core diagnostic logic (ray
presence/absence, outward versus inward direction) is genuinely preserved — the
additions sharpen and extend it rather than replacing it. The change remains conservative
in effect, and the changes were still applied uniformly across all H5 conditions, so no
condition contrast is confounded.

**Why this matters**: E16 is the register entry a reader consults to learn how far the
executed prompts diverge from the lodged appendix. An "unchanged" claim in that entry
understates the divergence. Identified by the Phase 1 verification campaign
(`reports/verification/phase1-gate-package.md` § 2 finding 4;
`reports/verification/apparatus/defence-pass-adjudication-2026-07-29.md` F4), whose
broader ruling was a **major downgrade** of the prompt-divergence concern: the lodged
appendix was byte-accurate at lodgement, all drift is post-lodgement across five commits
(2026-02-02 to 2026-02-11), four of them erratum'd within 24 hours, and the restructure
is licensed by E14. This correction and the `5e7601d77` entry (E65) are the residue.

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

### E20: Standardised "holdout" → "validation" naming across codebase (corrected 2026-07-30)

| Field | Value |
|-------|-------|
| Date | 2026-02-05 (original); **corrected 2026-07-30** — see Correction |
| Type | Clarification |
| Files | `inputs/tiles/tile_selection_metadata.json`, `scripts/generate_tile_bounds.py`, `scripts/select_tiles_phase4.py`, `scripts/analyse_phase2_results.py`, tests |
| Impact | None (internal naming only) |

**Correction (2026-07-30)**: this erratum's Rationale closes with "The 281-tile reserve
remains unnamed/untouched." **That statement was falsified 40 days later and was never
amended.** E20 is dated 2026-02-05; E36 is dated 2026-03-17 and records the expansion of
the evaluation corpus to 340 tiles — which is the full 360-tile physical corpus minus the
20 calibration tiles, and therefore absorbs the *entire* reserve. From 2026-03-17 the
reserve was neither unnamed (it is enumerated in
`inputs/tiles/full_evaluation_manifest.json`, 340 entries) nor untouched (every Phase 2a–3a
condition was re-run across it). E36's own numbers disclose the absorption; what was
missing was an amendment here, at the entry that asserts the opposite.

**Secondary correction**: the reserve's size. E20 says "281-tile"; the physical corpus is
**360** tiles (`find inputs/tiles -name "*.png"` → 360), of which 20 are calibration and
60 validation, leaving a reserve of **280**. The 281 figure inherits the off-by-one in
§ 2.1's "**Total**: 361 tiles" — see E64 sub-item (ii), which adopts § 8.6's "~360" as
the operative corpus count.

**What does not change**: the naming standardisation itself, which is what E20 exists to
record, and its "Protocol impact: None" assessment for that naming change. Identified by
the Phase 1 verification campaign
(`reports/verification/apparatus/defence-pass-adjudication-2026-07-29.md` F7, where the
defence raised it against its own interest).

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

This preserves the tile as the resampling unit (fixed pre-lodgement in Decision 10, `decisions-log.md:337`; the registered §3.5 specifies only "95% bootstrapped CIs" — attribution corrected 2026-07-28, D17 audit U1) while correctly handling the K=10 repeated-measures structure.

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

**Protocol impact**: None. The statistical method (bootstrap CIs, registered §3.5; tile-level resampling unit fixed pre-lodgement in Decision 10 — attribution corrected 2026-07-28, D17 audit U1) is unchanged. This corrects an implementation bug in how resampled tiles were passed to the matching functions. The `analysis_report.json` was also regenerated from the current (valid) data after the fix.

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
analysis protocol. The preregistration specifies 95% bootstrapped CIs
(Section 3.5); the tile-level resampling unit was fixed pre-lodgement in
Decision 10 (attribution corrected 2026-07-28, D17 audit U1). Neither
specifies the spatial
matching granularity (per-tile vs per-map) within each bootstrap
iteration. The correction aligns the bootstrap matching with the
point-estimate matching method, which is the methodologically
consistent choice.

---

### E36: 340-tile production retest replaces 60-tile holdout evaluation (corrected 2026-07-30)

| Field | Value |
|-------|-------|
| Date | 2026-03-17 (original); **corrected 2026-07-30** — see Correction |
| Type | Deviation |
| Commit | `f06afb7` |
| Files | `studies/retest/*.yaml`, `inputs/vectors/bounds/full_evaluation_bounds.geojson` |
| Impact | All Phase 2–3 results re-evaluated on larger corpus; statistical power substantially increased |

**Correction (2026-07-30)**: this erratum's Description states that on the 60-tile
holdout "only 1 of 10 Phase 2a pairwise comparisons survived FDR correction (Obs 155)".
**The correct figure is zero.** `results/phase2a-analysis-report.json` — the artefact
this claim summarises, generated 2026-02-06 and committed 2026-02-08 (`57ec68c25`) —
records `n_comparisons: 10`, `n_initially_significant: 3`, and **`n_fdr_significant: 0`**,
with a `recommendation` field that says so in words: "No pairwise differences
significant after FDR correction (q=0.05)." Every committed version of that artefact
records 0; no version has ever recorded 1. The defence pass independently re-ran the
Benjamini–Hochberg routine and reproduced 0.

**Severity context, stated because it cuts against the reflex to minimise**:

1. **The error is self-adverse.** Zero surviving comparisons is a *stronger* rationale
   for the corpus expansion this erratum records than one surviving comparison. The
   mistake understated the case for the decision it justifies.
2. **It was inherited, and the source is worse than a mis-transcription.** The claim is
   attributed to Obs 155. **Obs 155 contains no FDR result at all.** Observation 155
   (`docs/notes/working-notes.md:2754`) is "Extended reasoning as liberaliser — more
   thinking, worse precision (2026-03-10)", an analysis of 44 verifier candidates under
   HIGH versus minimal thinking; a full-text scan of the entry returns zero occurrences
   of "FDR", "bootstrap", "holdout", or "pairwise". The citation does not merely
   mis-report a number in Obs 155; it points at an observation that never made the claim.
3. **It propagated to four documents.** This entry;
   `reports/experimental-progression.md:83` ("only 1 of 10 Phase 2a pairwise
   comparisons survived FDR correction"); `reports/gs-tile-pool-mapping-2026-05-28.md:45`
   (quoting "only 1 of 10 / Phase 2a comparisons" surviving FDR correction);
   `docs/notes/working-notes.md:3397`, in the "Transition to Production Runs (Session 52)"
   block ("Only 1 of 10 Phase 2a comparisons / survived"). All four require the same
   correction to 0; the two reports are corrected in place with changelogs, and the
   working-notes site receives an append-only Obs rider (never an edit).
4. **It escaped the 2026-07-28 preregistration-integrity sweep** and was caught only by
   the Phase 1 execution census the following day.

**What does not change**: the corpus expansion decision, the 340-tile scope, the power
rationale, and every downstream result. The corrected figure strengthens the rationale
rather than undermining it. Identified by the Phase 1 verification campaign
(`reports/verification/phase1-gate-package.md` § 2 finding 5;
`reports/verification/apparatus/defence-pass-adjudication-2026-07-29.md` F5); handling
ruled by the PI 2026-07-30
(`reports/verification/phase2-rulings-2026-07-30.md` § 1d).

**Description**: The preregistered Phase 3 evaluation used a 60-tile holdout set. Bootstrap CIs on this set were wide (~0.20) and only 1 of 10 Phase 2a pairwise comparisons survived FDR correction (Obs 155). The evaluation corpus was expanded to 340 tiles (569 ground truth mounds across 4 map sheets) to achieve adequate statistical power. All Phase 2a–3a conditions were re-run from scratch on the full corpus. K was reduced from 10 to 1–3 for single-pass conditions (340 tiles provide sufficient power) and retained at K=30 for consensus voting.

**Protocol impact**: Results from the 340-tile corpus supersede the 60-tile holdout results for all conditions. The 60-tile results remain documented in `results/phase3d-*.md` as historical reference. Hypothesis tests now have adequate power to detect the observed effect sizes.

---

### E37: Proposer-Verifier (PV) pipeline — production implementation of registered H2 Condition B (corrected 2026-07-28)

| Field | Value |
|-------|-------|
| Date | 2026-03-15 (original); **corrected 2026-07-28** — see Withdrawal |
| Type | Correction (originally recorded as Deviation) |
| Commit | `f9d40e0` (library), `5d72593` (orchestrator) |
| Files | `scripts/lib_verifier.py`, `scripts/run_pv.py`, `scripts/evaluate_pv_results.py` |
| Impact | Reclassifies the headline PV result from "unregistered post-hoc extension" to **confirmatory H2 outcome: the registered null prediction is falsified and the registered stopping rule fired** |

**Withdrawal (2026-07-28)**: this erratum's original Description opened with
"The preregistration did not include a two-stage Proposer-Verifier pipeline."
**That sentence is withdrawn as false.** The preregistration registers the
coarse-to-fine proposer-verifier architecture as H2 Condition B
(`osf/preregistration.md:457`, `:466-476`, including "Stage 1: Detection with
lower confidence threshold / Stage 2: Crop candidate regions, verify with
focused prompt"); the verifier prompt is lodged in the registered appendix
(§1.6.2 `verify_brief.md`, `preregistration-appendix-prompts.md:1088-1128`)
with its JSON config (`:1622-1640`) and the H2 execution protocol (`:1584`).
The original Impact line ("surpassing all preregistered approaches") and the
original Protocol-impact claim ("an extension beyond the preregistered
design") are withdrawn on the same basis. Identified by the 2026-07-27/28
preregistration-integrity audit
(`reports/d17-inventory/e37-pv-preregistration-audit.md`; attribution sweep
FALSE-8); the repo copy of the registration was verified byte-identical to
the OSF-posted artefact on 2026-07-28.

**Corrected description**: The registered H2 prediction was a null — "Neither
two-stage architecture will improve F1 over single-stage detection with
voting" (`osf:461`). **That prediction is falsified.** PV's improvement
exceeded the registered stopping rule — "Two-stage architectures will only be
pursued further if either demonstrates F1 at least 0.05 higher than
single-stage" (`osf:491`) — whose firing is what licensed further pursuit,
and it activated the registered optimisation contingency in the coverage
document (`preregistration-coverage.md:187`: pipeline optimisation "only if
this threshold is met"). The production PV programme is that registered
contingency, exercised.

What this erratum correctly records is a set of **implementation elaborations
beyond the registered Condition-B specification**:

1. **Consensus proposer pool** — the registered Stage 1 is a single liberal
   detection pass; production feeds the verifier from a consensus union of
   passes. Registered-contingent (Condition A's consensus baseline), but not
   what Condition B literally specified.
2. **Binary application of the verifier verdict** in the headline pipeline
   (`prob_threshold = null`, E56) versus the registered direct use of raw
   `mound_probability` scores (`preregistration-appendix-prompts.md:1584`).
   The deviation is in the *handling*: the production adversarial prompt
   still elicits raw probabilities.
3. **Adversarial prompt framing** — the registered verifier prompt is a
   neutral classifier; E39 establishes strategy choice is not load-bearing.
4. **Crop geometry** — the registration is silent on crop extraction (E8).
5. **Verifier consensus size** — the registration is silent; N=1 vs N=5 was
   tested and found insensitive (Obs 166, 167, 169).

The PV approach was operationalised after observing that single-stage
detection produced many false positives that a second-stage verifier could
filter. The PV pipeline was first piloted on the 60-tile holdout (F1=0.796,
Obs 150) and then validated and optimised on the 340-tile corpus. It
supports both Batch API and real-time API execution modes; the published
software offers both modes to end users. Verifier optimisation (Phase 1)
tested crop size (40–300px), consensus (N=1 vs N=5), and verifier strategy
(adversarial, checklist, brief) — all parameters were found to be
insensitive (Obs 166, 167, 169).

**Protocol impact (corrected)**: the headline PV result is a confirmatory H2
outcome — registered null falsified, registered stopping rule fired — with
the five elaborations above recorded as implementation-level deviations from
the registered Condition-B specification. All other preregistered analyses
(H1–H9) remain evaluated independently of PV. Cross-references: E38, E39,
E56, E58 (the registered proposer prompt was never used).

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

### E40: Gemini 3.1 Pro requires MEDIUM thinking — deviation from §8.2/§8.9 (clarified 2026-07-30)

| Field | Value |
|-------|-------|
| Date | 2026-03-24 (original); **clarified 2026-07-30** — see Clarification |
| Type | Deviation |
| Commit | pending |
| Files | `studies/h11-384-pro-pilot-*.yaml`, `scripts/run_phase2.py`, `scripts/run_pv.py` |
| Impact | Pro results use MEDIUM or HIGH thinking instead of preregistered MINIMAL |

**Clarification (2026-07-30)**: this entry's licence extends to Gemini 3.1 Pro used
**as a verifier**, not only as a detector. The Phase 1 execution census
(`reports/verification/c2-census/licence-census.json`,
`verifier_thinking_level=medium`) found seven proposer-verifier conditions in
`pv-diag-384` whose verifier is `gemini-3.1-pro-preview` at MEDIUM thinking
(`verified-adv-pro-text-pro-vf-3of5`, `verified-adv-text-pro-vf-4of5`,
`verified-adv-image-baseline-pro-vf`, `verified-adv-text-baseline-pro-vf`,
`verified-adv-pro-image-pro-vf-3of5`, `verified-adv-pro-text-baseline-pro-vf`,
`verified-adv-pro-image-baseline-pro-vf`) and flagged them as a near-miss: this
entry's text names single-pass and consensus Pro *experiments*, not the verifier
role. The Principal Investigator ruled on 2026-07-30 that the endpoint constraint
this entry records — the Pro endpoint cannot run MINIMAL; MEDIUM is its floor —
applies identically wherever the Pro model is invoked, so those seven sites are
licensed by this entry ("For Pro we had no choice, that's an existing erratum" —
`reports/verification/phase2-rulings-2026-07-30.md` § 1a). The deliberate
Flash-verifier thinking exploration the same census surfaced is a separate matter
and is disclosed in **E69**, not here.

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

**Correction (2026-08-02)**: this erratum's Impact row says "30 runs ×
487 tiles"; the study executed **240 tiles** (all 30 runs: 240/240
completed, 0 failed — `*.tiles.json` sidecars, `run.meta.json`
`items_processed`, and the union of `processed_tiles` across all 30
GeoJSONs agree; `results/passes-manifest.json` records the honest 240
throughout). 240 was the *designed* scope
(`studies/h11-384-consensus.yaml:69,106-112` — the H11 tile-size
comparison, planned before the 487-tile 384 px bounds existed). The
Data-disposition paragraph's temperature claim ("Obs 190: dF1 ~+0.15,
p<0.0001 at all pool sizes — T=0.7 dramatically outperforms T=1.0") is
a **coverage artefact and does not survive matched-scope comparison**:
the cited tests scored this study's 240-tile detections against
487-tile bounds, counting 193 of 435 ground-truth mounds (44.4 %) as
automatic false negatives (recall ceiling 242/435 = 0.556 — the E71
artificial-false-negative mechanism at ~247 tiles). At matched
487-tile scope (the 10-run `text-t1.0` arm, identical
system-instruction and library hashes) ΔF1 = −0.021 (N=5, p=0.335) /
−0.034 (N=10, p=0.082) at 20 m, similar at 30 m — sign reversed,
nothing significant; at matched 240-tile scope (archived 2026-03-24
evaluations) the matched-N deltas span −0.007 to +0.039 with all CIs
overlapping; the preregistered Phase 2b evidence (text +0.072, FDR
p=0.004; image +0.014, ns) is the citable temperature result, as
working-notes already directs. See E72 for the full disposition,
`results/e43-matched-temperature/` for the matched analysis, and
`reports/e43-coverage-confound-remediation-2026-08-02.md` for the
investigation. Identified by the C4 verification sweep (wave-4 blind
triage, Session 125); matched figures re-derived from committed
artefacts by two independent investigation passes.

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

### E45: Unregistered inference method — tile-swap permutation testing (corrected 2026-07-28; originally "test statistic changed from macro-average to micro-average")

| Field | Value |
|-------|-------|
| Date | 2026-03-26 (original); **corrected 2026-07-28** — see Correction |
| Type | Deviation (unregistered inference method adopted) |
| Preregistration ref | None — no permutation test is registered. The registered method is bootstrap CIs (§3.5, `osf/preregistration.md:293`) with BH-FDR (§3.1, `:270`) |
| Files | `scripts/pairwise_permutation_test.py` (new, replaces `scripts/paired_permutation_consensus.py`) |
| Impact | **High.** Permutation-based inference underlies every leaderboard, tiering, and pairwise-significance claim in the project; it is an unregistered substitution for the registered method, not an amendment to a registered one |

**Correction (2026-07-28)**: this erratum originally opened "The
preregistered pairwise permutation test (Section 3.5) specifies tile-level
resampling with a sign-flip permutation…". **There was never a preregistered
permutation test to deviate from.** `permutation` appears zero times in the
lodged registration (normalised whole-file scan; the lodged appendix's three
hits all concern H4 example-order shuffling), and §3.5 is a five-bullet
reporting section specifying effect sizes with 95 % bootstrapped CIs. The
sign-flip macro-average test this entry described as "preregistered" was
itself an unregistered post-registration implementation
(`paired_permutation_consensus.py`). Both it and its replacement are
unregistered inference methods. The registered analysis for confirmatory
hypotheses is bootstrap CIs + BH-FDR, and must be reported alongside
permutation results wherever confirmatory claims are made. Identified by the
2026-07-27/28 audit (attribution sweep FALSE-9; independently reached at
`docs/paper/results-outline.md:486-493`).

**Description (original, premise corrected above)**: The earlier sign-flip
test computed tile-level resampling with a sign-flip permutation on per-tile
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
| Crop size | 128px (implementation choice, E8 — not registered) | 150px (aligned with verifier standard) |

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

**Description**: The Phase 3a image-track study YAML
(`studies/retest/phase3a-h3-voting-track1-high.yaml`) — which implements
registered H3 extended voting (`osf/preregistration.md:512`) with an
unregistered HIGH-thinking factor (attribution corrected 2026-07-28, D17
audit U6; a study YAML is not the preregistration) — defined K = 30
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

**Correction (2026-08-19) — the iteration-count claim below is superseded by E82.**
This entry states that the scripts evaluating preregistered conditions "use 1 000
iterations, matching the preregistration", and frames 10 000 iterations as a
selective post-hoc choice. A census of the committed artefacts contradicts that
split: of 1 749 git-tracked `evaluation.json` files, **1 583 declare B = 10 000
against 114 at B = 1 000**. The Principal Investigator ruled 2026-08-19 to
standardise on 10 000 rather than revert, and to disclose the deviation. E54 is
left standing rather than rewritten so the earlier reading remains legible; read
it with E82. E82 additionally discloses that the *method* named below — percentile
(2.5th/97.5th) — was replaced by BCa in commit `2026999ad` (2026-04-30) without
disclosure, so the "percentile method" wording here describes Decision 10 rather
than the code that produced the artefacts.

**Description** (attribution corrected 2026-07-28, D17 audit U1): the registered text specifies 95% bootstrapped CIs (Section 3.5); the **1 000-iteration** count, percentile method (2.5th / 97.5th), and tile-level resampling unit were fixed pre-lodgement in **Decision 10** (`decisions-log.md:337`) and do not appear in the lodged registration. They are pre-specified analysis parameters, not registered ones. All scripts that evaluate preregistered conditions — `evaluate_detections.py`, `compute-pairwise-effect-sizes.py`, `evaluate_pv_results.py`, `compare_wbf_vs_greedy.py`, `analyse_secondary_effects_text.py`, and the shared `lib_advanced_metrics.bootstrap_ci` default — use 1 000 iterations, matching the preregistration.

Several **post-hoc** analyses (not specified in the preregistration) use **10 000 iterations** instead. These analyses are characterised by narrow effect sizes where CI precision at 2-3 decimal places is material for narrative clarity:

- `compute_corrected_f1_human_reviewed.py` — human-reviewed corrected F1 lower bound (effect size ~0.06 above measured F1; CI half-width would be ~±0.01-0.02 at 1 000 iter, ~±0.003-0.006 at 10 000)
- `compute_corrected_f1_multi_buffer.py` — multi-buffer extension of the same analysis (same rationale)
- `analyse_subtype_classification.py` — per-class subtype F1 with CIs (several per-class F1s sit in a 0.02-0.05 window; tighter CIs improve separability)
- `crosstab_uncalibrated_vs_calibrated.py` — review-UI disagreement-rate CI (disagreement ~21 %; narrow effect size)
- `analyse_buffer_band_lift.py` — within-tile permutation test, M = 1 000 matches the preregistered convention for permutation-derived null envelopes (noted here for completeness — this one follows the 1 000 default)

**Rationale for the split**:

1. **Decision 10 fixed 1 000 for primary evaluation pre-lodgement** — the setting remains untouched for preregistered conditions; because the count is pre-specified rather than registered, changing it for post-hoc analyses is a clarification, not a deviation.
2. **10 000 is selectively applied to post-hoc analyses where CI precision determines narrative clarity** — the preregistration does not constrain methodology for analyses it did not specify.
3. **Runtime is not a binding constraint for post-hoc analyses**: they run once on a single corpus, not across the hundreds-of-conditions leaderboard matrix. The 10× cost is absorbable for a one-off authoring run.

**Paper methods wording (suggested)**:

> Confidence intervals on primary F1, precision, and recall are derived from 1 000-iteration tile-level bootstrap resampling (95% bootstrapped CIs per registered §3.5; 1 000 iterations, percentile method 2.5th / 97.5th, and tile-level unit pre-specified in Decision 10 before lodgement). Post-hoc analyses — human-reviewed corrected F1 (single- and multi-buffer), subtype classification, and review-UI calibration cross-tabs — use 10 000 iterations to tighten CIs on narrow effect sizes; the resampling unit and percentile method are unchanged.

**Reference artefacts**:

- Registered §3.5 (95% bootstrapped CIs): `osf/preregistration.md:293`; parameter source Decision 10: `docs/methodology/preregistration/decisions-log.md:337` (this line previously mislabelled the decisions log as "Preregistration Section 3.5" — corrected 2026-07-28)
- Primary bootstrap defaults: `scripts/evaluate_detections.py` (`DEFAULT_BOOTSTRAP = 1000`); `scripts/lib_advanced_metrics.py::bootstrap_ci` default `n_iterations = 1000`
- Post-hoc 10 000-iteration scripts: enumerated above
- CI-metadata registry (per-file iteration count): `results/ci-metadata-registry.md`

---

### E55: Verifier-t-pilot T0.5/T1.0 metadata under-recorded the swept temperature (corrected 2026-07-30)

| Field | Value |
|-------|-------|
| Date | 2026-05-30 (original); **corrected 2026-07-30** — see Correction |
| Type | Metadata correction (non-destructive) |
| Commit | TBD |
| Impact | Low — exploratory pilot (H2); corrected at source and in the manifest |

**Correction (2026-07-30)**: remediation item 3 below promises that "The manifest
generator records the true temperature for these verifier passes, with
`provenance.source_files` listing both `run.meta.json` and `run.log`". **The
provenance half of that promise was never implemented.** Verified 2026-07-30: no row
in `results/runs-manifest.json` lists `run.log` among its `provenance.source_files`,
and `scripts/generate_post_run_report.py` mentions `run.log` only in a code comment
describing it as "the deeper source if neither is present — not" implemented. The
temperature values themselves ARE correct in the manifest — they flow through the
additive `configuration.temperature_effective` field written by remediation item 2 —
so the manifest's *content* honours this erratum; only the promised provenance
listing is missing. The Principal Investigator ruled 2026-07-30 ("Correction block +
fix" — `reports/verification/phase2-rulings-2026-07-30.md` § 2.3): this block records
the unfulfilled promise, and the generator is amended in the same landing wave to
list `run.log` in `provenance.source_files` for the two affected verifier passes.
Caught by the Phase 2 (C3) provenance re-derivation campaign.

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

**Description**: The headline proposer-verifier pipeline (gold-standard-v2) applies the verifier as a **binary accept/reject verdict** — its `verified` condition records `prob_threshold = null`, so no probability cutoff is tuned. The consensus vote threshold was calibrated on the 20 held-out Phase 1 calibration tiles (≥3/5). (Attribution corrected 2026-07-28, D17 audit: the registered ≥3/5 threshold, `osf/preregistration.md:1450-1451`, governs hard-example mining in §8.4.1 Step 2 — which FNs/FPs qualify as HP/HN candidates — not consensus vote-threshold calibration; the calibrate-then-test split for the vote threshold is an execution-time practice, not a registered one.)

The verifier's continuous `mound_probability` is explored only in the **diagnostic** runs (pv-diag-384 / the Session 78 verifier-calibration matrix). There the per-cell operating point `(vote_t, prob_t)` is selected by sweeping the grid and taking the F1-optimum at the 20 m buffer — and that selection is performed **on the 487-tile evaluation scope, which is the test set** (`scripts/score_leaderboard_cells.py`; `results/verifier-calibration-matrix/README.md` Phase B). There is **no calibration-tile verifier data** to select on: the verifier never ran on the 20 calibration tiles (excluded from the 487-tile scope; pv-diag ∩ calibration = 0). So any single `prob_t`-thresholded F1 quoted for these diagnostics is an **in-sample, test-set-optimised** number, not a calibrated one.

**Verification**: gs-v2 `verified-v1` carries `prob_threshold: null` (`results/run-conditions.json`); the 487-tile `full_evaluation_bounds` has zero overlap with the 20-tile `inputs/tiles/calibration_manifest.json`; the pv-diag text pool (471 covered tiles) contains none of the 20. The 2026-06-02 sweep (`results/rescore-2026-05-31/pv-diag-384/sweep/`) shows the F1@20 curve is **flat in the operating range** — single-run-PV ≈0.74 across prob_t 0.25–0.40, consensus-PV ≈0.86 across 0.15–0.20 — so a fixed reference threshold (0.20: 0.718 / 0.861) and the in-sample optimum (0.25: 0.740 / 0.15: 0.864) differ by ≤0.022 F1.

**Blast radius**: every `prob_t`-thresholded operating point in the verifier-probability diagnostics — the 14 `*-opt-20m.geojson` Session 78 cells, the h10 / h8-v2 / verifier-t-pilot `detections_vt*_pt*` materialisations, and the pv-diag-384 PV quadrants. The **headline** proposer-verifier results (binary verdict) and **all consensus-vote-threshold** results (preregistered, calibration-selected) are NOT affected.

**Reporting rule (resolution)**:

1. Report the headline proposer-verifier result at the **binary verdict** (`prob_t = null`), per gs-v2 and the preregistered design.
2. Present the verifier-probability diagnostics as **threshold-sensitivity curves**, not single F1 maxima. Where one operating point is quoted, state explicitly that it is the **20 m test-set F1-optimum (in-sample)** and give the fixed-reference value beside it; the curve's flatness (≤0.022 F1 across the plateau) makes the two interchangeable for the well-calibrated text track.
3. State plainly, in the paper and all supporting materials, **when and how each threshold was set**: vote threshold → preregistered, calibrated on the 20 held-out tiles; verifier binary verdict → no tuning; verifier `prob_t` operating points → in-sample on the 487-tile test set (diagnostic only).
4. The text-track verifier is well-calibrated (AUC 0.956, ECE 0.071); the image track is not (AUC 0.86, ECE 0.18; Obs 269, 277) — so a fixed threshold transfers on text but not image. Cite this for any image-track operating point.

**Reference artefacts**: `results/verifier-calibration-matrix/README.md` (Phase B); `results/run-conditions.json` (gs-v2 `prob_threshold: null`); `inputs/tiles/calibration_manifest.json`; `results/rescore-2026-05-31/pv-diag-384/sweep/`; working-notes Obs 269 + 277; `planning/session-78-matrix-calibration-summary.md`.

**Update (2026-06-06 — scope clarification, H3 consensus characterisation).** This erratum governs the **verifier probability-threshold** diagnostics only. It does **not** make the **H3 consensus-voting characterisation** (the Phase 3a / pv-diag-384 vote-threshold sweep, realised as the `diversity-dividend-384` finding) an "in-sample" limitation. The preregistered H3 analysis plan (`osf/preregistration.md:519-521` — "Compare single-pass mean F1 vs voted F1 at each (N, threshold) combination", "Generate threshold sweep curves", "Identify optimal (N, threshold)"; citation corrected 2026-07-28, D17 audit U4 — the original cited `analysis-summary.md`, which is not a lodged document) — so reporting each configuration's best (N, threshold) operating point against the test-tile ground truth is the **preregistered method**, and the deliverable of a study whose stated purpose is to characterise how well VLM symbol extraction localises mounds against known ground truth. Three operating-point provenances must be kept distinct and **not** conflated under one "in-sample" label:

1. **Phase-1 baseline consensus** — vote threshold ≥3/5, calibration-selected on the 20 held-out calibration tiles, used to build the hard-case example library. Calibrated.
2. **H3 consensus characterisation** (Phase 3a / pv-diag-384; `diversity-dividend-384`) — best (N, threshold) swept against the test tiles. **Preregistered method, not a hedge** — the test tiles are the measurement instrument, and best-achievable performance is the result.
3. **Verifier `prob_t` diagnostics** (this erratum) — selected on the 487-tile test set with no held-out verifier data. In-sample; report as sensitivity curves.

The calibrate → test → produce logic (and any "in-sample vs deployable" framing) belongs to the **55-map generalisation** deployment, where the carried-forward configuration is reported against corrected student ground truth alongside the oracle-best on the 55-map set (the carry-forward − best delta). It does not apply to the GS test-tile characterisation, which is the whole point of the test tiles. No preregistration amendment is required: H3's swept-optimal reporting was preregistered (`osf/preregistration.md:519-521`; citation corrected 2026-07-28 — see above).

---

### E57: H11 384px Pro/baseline detection metadata — model template default and output_dir overrides

| Field | Value |
|-------|-------|
| Date | 2026-06-02 (original); **revised 2026-06-03** — see Update below |
| Type | Metadata correction (non-destructive) + **billing reconciliation (finding-affecting)** |
| Commit | `e1f20da4` (model-of-record + re-run), `59727c8a` (re-tier), `c06aceee` (finding rewrite) |
| Impact | **Revised to Medium–High.** The original assessment ("Low — provenance only") was wrong: the 2026-06-03 billing reconciliation found four of the "Pro" pools were dispatched as **Flash**, which CHANGED the N=1 leaderboard finding (tie_set and the H6 narrative). See the Update. |

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

---

#### Update (2026-06-03): billing reconciliation — four "Pro" cells were Flash; genuine-Pro re-run; finding changed

The original entry (above) assumed `config.model = flash` was an unreliable *template default* on **all** the "Pro" pools and that those pools were genuinely Gemini 3 Pro. A triple-checked billing reconciliation on 2026-06-03 found this is only half right, and the half it got wrong is finding-affecting.

**The split (airtight):**

- The four **`n1-outstanding-384`** anti-diagonal "Pro" cells — `pro-text-high-t0`, `pro-image-high-t0`, `pro-text-medium-t07`, `pro-image-medium-t07` — were **dispatched and billed as `gemini-3-flash-preview`**, NOT Pro. Confirmed by `per_item_metadata.model_version = gemini-3-flash-preview` on every one of their ~3,896 responses (sourced from `response.model_version` at `scripts/lib_llm_metadata.py:635`), and corroborated by Flash pricing rates and Flash-range performance. The runner never threaded the per-study `--model` Pro override, so the base-config Flash ran. For these four, `config.model = flash` was therefore *correct*, not a misleading template default.
- The four **`pv-diag-384`** "Pro" cells (`pro-medium-text-baseline`, `pro-medium-image-baseline`, `pro-high-text-n5`, `pro-high-image-n5`) ARE genuinely Pro: `pricing_used.model = gemini-3.1-pro-preview` at $2/$12 rates — the `--model` override took there.

**The authoritative field for *what ran* is `per_item_metadata.model_version` / `pricing_used.model` — NEVER `config.model`** (a Flash template-default on BOTH groups) **and never the directory slug or the study YAML** (which record *intent*, not dispatch).

**Genuine-Pro re-run.** To complete the genuine Pro 2×2 × modality, the four mis-dispatched corners were re-dispatched as genuine Pro (run `n1-pro-rerun-384`, realtime+flex, byte-audited configs; `outputs/h11/n1-pro-rerun-384/`, committed `1cdf9438`). All 8 passes verify `model_version = gemini-3.1-pro-preview`. Scored at the 14-buffer + MCC standard (`results/paper-eval/n1/384px-14buf-mcc/pro-rerun/`).

**Model-of-record corrections** (`results/run-conditions.json`, non-destructive — directories and slugs unchanged):

| Pool (corner) | Was (study intent) | Now (model-of-record) |
|---|---|---|
| `n1-outstanding-384` pro-{text,image}-{high-t0, medium-t07} ×4 | `gemini-3.1-pro` | **`gemini-3-flash-preview`** |
| `n1-pro-rerun-384` pro-{text,image}-{high-t0, medium-t07} ×4 | — (new run) | **`gemini-3.1-pro-preview`** |

**Finding change (the reason this is no longer "Low impact").** The pre-E57 N=1 leaderboard ranked the four mis-dispatched Flash cells as "weak Pro" (F1 0.42–0.53) and reported a two-member Tier-1 tie (`pro-text-medium-t-0-0` 0.763 + `pro-text-high-t-0-7` 0.745). Replacing them with the genuine-Pro re-run cells (which score 0.59–0.80 at the same corners):

| Corner | Flash (mis-dispatch) F1@20 m | Genuine Pro F1@20 m |
|---|---:|---:|
| Pro text HIGH T=0.0 | 0.494 | **0.804** |
| Pro text MEDIUM T=0.7 | 0.416 | 0.755 |
| Pro image HIGH T=0.0 | 0.528 | 0.666 |
| Pro image MEDIUM T=0.7 | 0.452 | 0.595 |

(genuine-Pro column shown at the final n=3; the medium-thinking corners moved
0.764→0.755 / 0.593→0.595 between the n=1 re-run and the n=3 top-up.)

- The earlier "Flash image-MINIMAL beats weak Pro" reading was an **artefact of the mis-dispatch**: genuine Pro beats the best Flash cell (0.600) at every text corner and dominates MCC at every image corner. H6 (Pro ≥ Flash) now holds uniformly at the top (top six cells all genuine Pro).
- The Tier-1 `tie_set` is **two genuine-Pro text cells at T=0.0** — `pro-text-high-t-0-0` (0.804) + `pro-text-medium-t-0-0` (0.792) — clear of the two Pro-text T=0.7 cells (Tier 2), a clean T=0.0 > T=0.7 ordering (H7). 129/153 pairs significant → 7 tiers.

The leaderboard's `n1-baseline-matrix-384` board membership (`results/run-analyses.json` `conditions_compared`) was updated to name the genuine-Pro re-run cells, **replacing** the Flash cells; `tie_set`, `outcome`, and `predicted_outcome` were rewritten. The four Flash cells are preserved (documented, not deleted) under `n1-outstanding-384` with the corrected model-of-record; they remain available as genuine Flash data at otherwise-untested thinking/temperature corners.

**Completeness addendum (n=3 top-up).** Finalising the board, all four medium-thinking Pro cells were brought to n=3. This surfaced a *separate* data-quality issue isolated to the two **pv-diag medium-t-0-0** cells: their `run_1` batch passes had ~5 % unretried tile failures (25/23 of 487), which had depressed their scores (`pro-text-medium-t-0-0` 0.763, `pro-image-medium-t-0-0` 0.606). Recovered to 487/487 via the standard resume-merge path (genuine Pro, single round each), they score 0.792 / 0.655. The intermediate "sole leader" reading recorded above the addendum line was an artefact of the incomplete `run_1`; with coverage fixed, `pro-text-medium-t-0-0` ties the leader. Commits: `c06aceee` (initial E57 rewrite), `309e08de`/`c07c5776`/`28c8438a`/`0f32ec00`/`e857c7b5` (top-up, recovery, union glob, re-score, re-tier).

**Verification**: `per_item_metadata.model_version` re-read at source across all affected pools; `results/passes-manifest.json` shows the 8 `n1-outstanding-384` pro-* passes as `gemini-3-flash-preview` and the `n1-pro-rerun-384` passes as `gemini-3.1-pro-preview`. Cross-references: Obs 336 (leaderboard finding), Obs 337 (billing reconciliation), Obs 338 (genuine-Pro re-run), Obs 339 (n=3 top-up + recovery), `docs/methodology/n1-baseline-matrix.md`.

---

### E58: Registered H2 proposer prompt (`propose_brief`) never used — `detect_brief-text` substituted in all PV experiments

| Field | Value |
|-------|-------|
| Date | 2026-04-08 (deviation identified and analysed); **registered here 2026-07-28** |
| Type | Deviation |
| Commit | `5e7601d7` (prompt refinement, never invoked); analysis in `docs/notes/working-notes.md:6556-6790` |
| Files | `prompts/system-instructions/propose_brief.md` (registered, unused); `scripts/run_h2_pilot.py:12` |
| Impact | Medium — every PV experiment used a non-registered proposer prompt; measured comparison shows the substitution was conservative under N=1 but superior under production consensus |

**Register-integrity note**: this deviation was analysed in full on
2026-04-08 under the heading "Erratum E47" in `docs/notes/working-notes.md`
(`:6556`), a number that collides with the canonical register's E47 (20 m
buffer reversion) and was never entered here. It is promoted to **E58**
(2026-07-28, D17 audit); the working-notes analysis remains the reference
artefact.

**Description**: the registration's Config Files table
(`osf/preregistration.md:2015`) specifies `propose_*.json` + `verify_*.json`
for H2, and the proposer prompt is lodged in full in the registered appendix
(`preregistration-appendix-prompts.md:1042-1086`, §1.6.1, including "This is
Stage 1 of a two-stage pipeline; a verifier will filter false positives.").
The `propose_brief.md` prompt was written 2026-01-20 and refined 2026-02-03
— and **never invoked in any experiment**. All PV experiments from Phase 3d
through H11 production reused `detect_brief-text` outputs as proposer input,
a pragmatic cost-saving reuse of existing Phase 2d detections
(`run_h2_pilot.py:12`) that then persisted.

The two prompts differ by two lines (title, and the candidate/verifier
framing sentence). A 2026-04-08 N=1 comparison found the registered proposer
substantially better in the single-pass pipeline (F1 0.716 vs 0.573,
recall +35 pp — consistent with the framing effect; comparison partly
confounded with v2 exclusions). Under production **consensus**, however, the
relationship reverses: `detect_brief-text` with 4-of-5 consensus proved
superior, and the final assessment (`working-notes.md:6786`) is that the
substitution "was accidentally the right design choice".

**Protocol impact**: PV results implement registered H2 Condition B (see
corrected E37) with a non-registered proposer prompt. The paper must not
describe the production proposer as the registered one. Reference artefacts:
`docs/notes/working-notes.md:6556-6790`;
`results/documentation-audit/results-audit-2026-04-21.md:430`.

---

### E59: H2 Condition C (fine-to-coarse) — registered confirmatory condition never executed, never formally dropped

| Field | Value |
|-------|-------|
| Date | 2026-07-28 (omission spans 2026-02 → present) |
| Type | Deviation |
| Commit | — (records an omission, not a change) |
| Files | `osf/preregistration.md:469`, `:478-482`; `preregistration-appendix-prompts.md:1129-1160` (registered verification prompt, §1.7.1) |
| Impact | Medium-high — one of three registered H2 conditions has no result and no decision trail |

**Description**: the registration specifies H2 Condition C — standard
detection on 512 px tiles with 5-pass voting; candidates at 2/5–3/5
agreement re-queried at ~1024 px with a verification prompt
(`osf/preregistration.md:478-482`). It was never executed. The forensic
reconstruction (`reports/d17-inventory/step0-fine-to-coarse-archaeology.md`)
found: (1) the operational execution plan listed only Conditions A and B
from 2026-01-01, a week *before* the registration's A/B/C table
(2026-01-08) — a drafting mismatch never reconciled; (2) the PI was asked
twice on 2026-03-07 to confirm C stays dropped and answered other topics
(verified against the full raw session archive, 4,201 records, 2026-07-28);
(3) a 2026-03-15 note claiming C was deprioritised because "the
coarse-to-fine results were strong enough" is invalid under the registered
design — the registered prediction was a null for *both* architectures, so
a strong Condition-B result is the registered trigger to pursue two-stage
architectures further, not a licence to stop (that note is corrected in
`hypothesis-tracking.md`).

**Protocol impact**: H2's registered test is two-thirds executed. Condition
B's result stands as a confirmatory falsification of the registered null
(corrected E37); Condition C's contribution is unknowable without running
it. Running it now is feasible (~1–1.5 days; Stage 1 exists in
`outputs/retest/phase3a/`; `extract_candidates.py --padding 512` produces
the crops; two open PI decisions — corpus and crop size, the spec giving
both 1024 px at `osf:482` and 896 px at appendix `:1144`). Whether to run
it or disclose it as unexecuted is an open PI decision
(`planning/audit-and-completion-plan.md` § 8).

**Update (2026-08-17 — residual disclosure facts, S134 reconciliation).**
Five facts supplement the original entry. (1) The registered
implementation artefacts were never created: the configuration mapping
(`osf/preregistration.md:2015`) requires `detect_*.json` + `expand_*.json`
for fine-to-coarse; no `expand_*` config or system instruction exists in
`prompts/`, and `git log --all --diff-filter=A` shows neither was ever
added — the drafted verification prompt survives only as prose at
`preregistration-appendix-prompts.md:1136-1160`. (2) Condition C's absence
makes the registered one-tailed test (`osf:486-489`), the ≥0.05 stopping
rule (`osf:491`), and the advance criterion (`osf:493`) unevaluable for
that architecture, so H2 conclusions must be phrased over coarse-to-fine,
never over "two-stage architectures" generally. (3) A fine-to-coarse
*approximation* did run — "Strategy 10" in the archived multi-scale pilot
(`archive/pilot-tile-size/scripts/analyze_multiscale_voting.py`, 7
configurations, best F1 0.533) — using fixed grid tiles and a detection
prompt rather than candidate-centred crops with a verification prompt; it
does not discharge Condition C and must not be mistaken for it. (4) The
pilot premise in the registration ("37% recall at 1024 px", `osf:484`) is
stale under model drift, so it cannot serve as a reason C would be
uninformative without re-measurement — an argument for running C, and a
caveat on any "we did not need it" framing. (5) The omission dates
precisely: the last moment C was treated as live is the 2026-01-17
"correctly TBD" ruling on the missing verification prompt. The open
disposition decision this entry records is scheduled for closure at the
S134 unexecuted-set adjudication
(`planning/s134-d17-reconciliation-block-2026-08-17.md`).

---

### E60: H7 escalation trigger — fired as written on the expanded corpus; escalation judged uninformative and not run

| Field | Value |
|-------|-------|
| Date | 2026-07-28 (decision 2026-07-28; trigger events 2026-02 / 2026-03) |
| Type | Deviation (registered conditional evaluated; escalation not conducted) |
| Commit | — |
| Files | `osf/preregistration.md:731`; `results/retest/pairwise-bootstrap-comparisons.json`; `archive/outputs-pre-retest-60-tile/phase2b/carry-forward-parameters.md` |
| Impact | Low-medium — two registered exploratory cells (T=1.6, T=2.0) not run; the scientific question they target is already answered |

**Description**: the registration (`osf/preregistration.md:731`) commits:
"If T=1.3 yields higher F1 than T=1.0 (point estimate, same M/E and H5
condition), exploratory testing at T=1.6 and T=2.0 will be conducted at the
optimal configuration to characterise the upper bound of the
temperature-performance curve."

**On the corpus the registration specified** (60-tile K=10 holdout), the
trigger **never fired**: T=1.0 exceeds T=1.3 on both tracks (image 0.4578 >
0.4387; text 0.5687 > 0.5258;
`archive/outputs-pre-retest-60-tile/phase2b/carry-forward-parameters.md`).
The trigger fired only on the E36-expanded 340-tile retest, and only on the
text track (T=1.3 0.544 > T=1.0 0.533, point estimate). E36 records why the
corpus changed: the 60-tile set lacked the power to separate conditions —
a sound methodological choice, but it means the firing occurred on an
unregistered corpus.

**Why escalation was judged uninformative**: the triggering difference is
statistically indistinguishable from noise (ΔF1 −0.0357, 95 % CI
[−0.0908, +0.0137], p = 0.204); the direction **reverses** on the image
track (+0.0210, p = 0.290); the two levels compared are the worst two of
five on the text track; and the full five-level curve is monotone declining,
with T=0.3 significantly better than both T=1.0 and T=1.3. Characterising
the "upper bound" of a curve already known to decline, on a trigger that is
noise on an unregistered corpus and absent on the registered one, answers no
open question: the benefit-above-vendor-default question is decisively
negative.

**Resolution**: T=1.6 / T=2.0 escalation is **not run** (decision recorded
at `planning/audit-and-completion-plan.md` § 6.1, 2026-07-28). This erratum
discloses the registered conditional, both evaluations of its firing
condition, and the disposition.

**Blast radius**: none on reported results (no existing number changes);
the deviations table in the paper gains one disclosure row.

**Reference artefacts**: `planning/audit-and-completion-plan.md` § 6.1;
`results/phase2b-carry-forward-parameters.md:35-70` (retest curve);
`reports/d17-inventory/unexecuted-register.md` § 4 (T-01).

---

### E61: H4b trigger wording clarified — "main effect" designates the registered directional contrast; H4b to run as unregistered exploratory on the full GS corpus

| Field | Value |
|-------|-------|
| Date | 2026-07-28 (PI decision, Session 119) |
| Type | Clarification |
| Commit | — |
| Files | `osf/preregistration.md:1100` (trigger), `:546` (directional hypothesis), `:570-574` (planned contrasts); `results/phase2e-carry-forward-parameters.md` |
| Impact | Settles whether H4b is an owed registered experiment (it is not), and fixes H4's primary test ahead of the family-level BH-FDR analysis |

**The ambiguity**: the registered H4b trigger reads "H4 main effect is
significant (FDR-corrected p < 0.05)" — but H4's registered analysis contains
no omnibus "main effect" test. "Main effect" is analysis-of-variance
vocabulary surviving from the pre-v4.7 draft; the v4.7 statistical
reconciliation replaced per-hypothesis ANOVA with pairwise bootstrap
comparisons and two named planned contrasts (canonical-first vs
canonical-last; optimal vs random) without updating the trigger's wording.
Two readings were defensible: (1) the registered *directional* contrast
(H1: canonical-last > canonical-first, `osf:546`); (2) "any ordering effect"
(supported by the Simplification rationale's parenthetical "does ordering
matter?", `osf:560`).

**PI decision (2026-07-28)**: **reading (1) is adopted.** Rationale: it is
the only test H4 formally hypothesises (the H0/H1 statement); H4b's own
Background ("If canonical placement matters (H4)…") points at the
canonical-position contrast; and "main effect" is demonstrably a drafting
residue. Reading (2) rests on a parenthetical in a cost-justification
paragraph.

**Consequence under the adopted reading**: Phase 2e's directional contrast
is null (canonical-last 0.609 vs canonical-first 0.579; 0/6 comparisons
FDR-significant) — **the H4b trigger never fired and H4b is not an owed
registered experiment**. This clarification is recorded *before* the
family-level BH-FDR analysis runs, so the designation of H4's primary test
(the directional contrast) is not conditioned on seeing which contrast
survives the seven-member family correction.

**Disposition (also PI, 2026-07-28)**: H4b's two cells (HP-first vs
HN-first within the hard block) will nevertheless be run as **unregistered
exploratory**, buying off the interpretive ambiguity entirely at small cost
— and over the **full gold-standard corpus rather than the registered
60-tile holdout**, because the 60-tile set lacks the power to separate
conditions (the E36 lesson). Instrument choice (Era-1 512 px/340-tile vs
Era-2 384 px/487-tile) and cost are settled at run-authoring time; per
§ 6.4 of `planning/audit-and-completion-plan.md`, the registry entry,
conditions, and `predicted_outcome` must be authored and committed with
`status: planned` **before** the run executes.

**Reference artefacts**: `planning/audit-and-completion-plan.md` § 6.3;
`reports/d17-inventory/fable-adversarial-review-2026-07-28.md`.

---

### E62: Three unregistered proposer-verifier extension studies (`flash35-pv-2x2`, `pv-diag-256`, `verifier-robustness`) and four unregistered verifier-parameter levels — additional exploratory extensions of the registered PV contingency

| Field | Value |
|-------|-------|
| Date | 2026-07-30 (disclosure; executions 2026-04 to 2026-06) |
| Type | Deviation (unregistered exploratory extensions; no registered study altered) |
| Commit | — |
| Files | `results/runs-manifest.json`; `results/run-conditions.json`; `reports/verification/c2-census/licence-census.json`; `outputs/flash35-pv-2x2/`, `outputs/h11/pv-diag-256/`, `outputs/verifier-robustness/` |
| Impact | Low. No registered hypothesis test is conditioned on these runs; no reported registered result changes. Together with E69 and E40's 2026-07-30 clarification, the disclosure closes the last thirteen unlicensed factor=level pairs in the execution→errata inverse census |

**Framing (PI, 2026-07-29)**: E37 establishes that the proposer-verifier (PV)
architecture is *registered* — H2 Condition B — and that the production PV programme
is "that registered contingency, exercised" (E37), the contingency being the coverage
document's "exhaustive optimisation only if this threshold is met"
(`osf/preregistration-coverage.md:187`) fired by the registered stopping rule at
`osf/preregistration.md:491`. The three families recorded here are **additional,
unregistered, serendipitous extensions of that same programme** — exploratory
additions built on top of a registered architecture. They are **not** deviations from
any registered study: none replaces, alters, or re-specifies a registered condition,
and no registered analysis draws on them. This erratum discloses them for
completeness, not because a registered commitment was departed from.

**How they surfaced**: the Phase 1 verification campaign's execution→errata inverse
census triaged all 213 observed factor=level pairs against the 702-obligation
commitment ledger and all 61 existing errata. 200 pairs were licensed (43 by the
registration, 14 by an erratum, 143 by both); 13 were UNLICENSED
(`reports/verification/c2-census/licence-census.json`, `summary`). Those 13 reduce to
three study families, five verifier-parameter levels, and five derivative
`proposer_pool` slugs that are licensed at run level and carry no independent content.
Disposition of the five levels (PI ruling 2026-07-30,
`reports/verification/phase2-rulings-2026-07-30.md` § 1a): four are disclosed in this
entry; the fifth (`verifier_thinking_level=medium`, 13 sites) splits — its seven
Pro-verifier sites are licensed by E40's endpoint-constraint rationale (dated
clarification block at E40), and its six Flash-verifier sites, plus the one
`pv-diag-384` Flash HIGH-verifier site, are the deliberate exploration disclosed in
**E69**.

**The three families**:

| Family | Purpose (source) | Architectures executed | Scope |
|--------|------------------|------------------------|-------|
| `flash35-pv-2x2` | `runs-manifest.json`: "Model-role 2x2x2: is Flash 3.5 a better bare proposer, PV proposer, or verifier than Flash 3 at the minimal operating point? (The S110 parking note: bare proposer was the only angle a stronger model might win.)" | 1 × `consensus`, 3 × `proposer-verifier` (4 citable conditions) | era-2-487 (487 tiles, 384 px, 4-map gold standard, curator ground truth) |
| `pv-diag-256` | `runs-manifest.json` `purpose` was **`null`** at census time; populated in this landing wave per the PI ruling of 2026-07-30 (§ 1b). `run-conditions.json` `_note`: "256px H11 tile-size diagnostic (px256-1032 scope, 1032 tiles, curator GT) … 256px is the small-tile anchor for the tile-size comparison: F1@20m orders 256 < 512 < 384 (0.46 / 0.69 / 0.79)." | 1 × `single-pass`, 1 × `consensus`, 1 × `proposer-verifier` (3 citable conditions) | px256-1032 (1 032 tiles, 256 px, 4-map gold standard, curator ground truth) |
| `verifier-robustness` | `runs-manifest.json`: "Verifier-robustness programme: determinism (n=1 vindicated), proposer-input band, temperature/thinking matrix, model roles, compute allocation, operational maximum, pass-budget Pareto. Meta-rule: on a within-noise tie, take the cheaper config." | 8 × `proposer-verifier` (8 citable conditions) | era-2-487, with one condition scope-overridden to px256-1032 |

Architectures are as recorded in `results/run-conditions.json`, `decomposition.<family>.
conditions[].architecture`. Every condition in all three families is either a PV
condition or a proposer-side baseline built to be compared against one — which is the
factual basis for the "extension of the PV programme" framing rather than "new
unregistered studies".

**Why each is an extension rather than a registered study**:

1. **`flash35-pv-2x2`** asks a model-role question the registration does not pose. The
   lodged model set is closed at four values — "| Model | gemini-3-flash, gemini-3-pro,
   claude-4.5-sonnet, gpt-5.2-thinking | H6, H14 | Overrides config file value |"
   (CMT-0591) and "**Primary**: Gemini 3 Flash, Gemini 3 Pro" (CMT-0377) — and admits no
   3.5-generation model. E3's model-name resolution licence
   (`gemini-3-flash` → `gemini-3-flash-preview`) resolves a registered name to an API
   endpoint; it does not admit a later model generation. Executed 2026-06-10.
   The result is against the extension's own interest and is reported as such: Flash 3.5
   wins in no role (`runs-manifest.json` `headline_rationale`, verbatim: "Deliberately
   none — a model comparison, not a champion search: Flash 3.5 wins in NO role
   (bare-proposer numerical tie 0.6196 vs 0.6204; PV proposer -0.0355, p=0.035 targeted
   tile-swap — the one resolved role gap; verifier -0.012..-0.015, within-noise ties, at
   3x the price). The all-Flash-3 production stack stands").
2. **`pv-diag-256`** runs the registered H11 tile-size question at a third level.
   Registered H11 has exactly two conditions — "| A | 512×512 | 1× (baseline) | 1× |
   Lower |" (CMT-0310) and "| B | 384×384 | 0.56× | ~1.8× | Higher |" (CMT-0311). The
   registration discusses 256 px only as *prior pilot context*, not as a condition:
   "Pilot testing at 256px confirmed high recall (0.90) but very low precision (0.10) at
   2/5 consensus voting threshold, suggesting smaller tiles may over-detect"
   (`osf/preregistration.md:963`). The 256 px diagnostic re-runs that pilot question on
   the production corpus and anchors the low end of the tile-size curve. Its proposer
   passes were **not** materialised as `run_*` directories (only consensus outputs and
   crops survive), so no per-pass metadata exists; the six consensus GeoJSONs were first
   committed 2026-04-15 (`3d22184d6`), and the PV verification condition was executed
   2026-06-08 (`outputs/era1-pv-stage-d/256-consensus-text-5of5/`).
3. **`verifier-robustness`** sweeps verifier parameters the registration fixes at a
   single value. The lodged two-stage configs are templates pinned to one downstream
   optimum — "**Template status**: These configs are templates that will be finalised
   after earlier phases complete. Temperature will use the H7-optimal value from Phase
   2b. Library composition will use the H8-optimal from Phase 2c." (CMT-0583) — and the
   lodged verifier config fixes thinking at minimal: "| `thinking_level` | `minimal` |
   Calibrated via pilot; minimal achieves equivalent F1 to high at 1/3 latency (see
   §8.9) |" (CMT-0605). Executed 2026-06-09/10. Again the headline is deliberately
   negative (`runs-manifest.json`, verbatim): "Deliberately none — NO new champion. The
   carry-forward headline pv-diag-384::verified-adv-text-consensus-16of30 (0.890) stands:
   the operational maximum here (verified-384-16of30-t0-3-n5-opmax, 0.8951) is NOT
   significant over it (paired tile-swap permutation p=0.363, …), so per the cost
   meta-rule (Obs 357) it is a numerical high only."

**The four verifier-parameter levels disclosed here**:

| Level | Observed sites | Carrying family/families | Nearest licence, and why it does not reach |
|-------|----------------|--------------------------|--------------------------------------------|
| `verifier_model=gemini-3.5-flash` | 2 | `flash35-pv-2x2` | E3 resolves a registered model *name* to its API endpoint; it does not admit a new model generation |
| `verifier_temperature=0.3` | 4 | `verifier-robustness` | CMT-0590 registers 0.3 as a runtime temperature level, but hooked to **H7 detection** temperature; no commitment extends the H7 sweep to the verifier stage |
| `verifier_temperature=0.7` | 2 | `verifier-robustness` | as above; E55 licenses a verifier-temperature sweep only at 0.5/1.0, in `verifier-t-pilot` |
| `verifier_thinking_level=high` | 3 (2 disclosed here, in `verifier-robustness`; the 1 `pv-diag-384` site is disclosed in E69) | `verifier-robustness` | E40 licenses HIGH only for `gemini-3.1-pro-preview` consensus runs; these sites run `gemini-3-flash-preview` |

The five derivative `proposer_pool` slugs (`f3-min-text-1of10`,
`flash35-min-text-1of10`, `text`, `text-1of5`, `text-consensus-5of5`) are per-study
pool identifiers with no independent experimental content; they are licensed at run
level and are disclosed here only so the census's thirteen are fully accounted for.

**Post-facto acknowledgement**: this disclosure is written with results in hand, in
July 2026, for runs executed between April and June 2026. It was produced by a
systematic census rather than at execution time, and the fact that these families were
not erratum'd contemporaneously is itself part of what the census found.

**Protocol impact**: none on registered results. All three families are exploratory
extensions of the registered H2 Condition-B architecture; none is cited as evidence for
a registered hypothesis; two of the three report deliberately null headlines, and the
third (`pv-diag-256`) contributes only the low anchor of a tile-size curve whose two
registered levels (512 px, 384 px) are unaffected. Reporting requirement: the paper's
deviations table gains one row, and any use of these families in the text must be
labelled unregistered exploratory. Cross-references: E37 (PV as registered contingency
exercised), E39 (verifier strategy not load-bearing), E40 (Pro thinking levels, incl.
the 2026-07-30 Pro-as-verifier clarification), E41 (384 px / 487-tile evaluation
scope), E55 (verifier-temperature pilot), E56 (in-sample verifier operating points),
E58 (registered proposer prompt never used), E69 (the Flash-verifier thinking
exploration split from this entry).

---

### E63: `retest-phase3c` (H9 diversity) executed at HIGH thinking level — unregistered departure from the §8.9 `minimal` decision, configuration-verified but not token-corroborated

| Field | Value |
|-------|-------|
| Date | 2026-07-30 (disclosure; execution 2026-03-18 to 2026-03-25) |
| Type | Deviation (unregistered thinking level on an exploratory hypothesis) |
| Commit | — |
| Files | `studies/phase3c-h9-diversity-track1.yaml`, `studies/phase3c-h9-diversity-track2.yaml`; `prompts/configs/phase3c-t{1,2}-*.json` (22 configs); `outputs/retest/phase3c/**/*.meta.json` (225 files) |
| Impact | Medium-low on level, potentially higher on direction. The setting is constant across every compared H9 condition, so within-H9 contrasts are not confounded by it; but Obs 140 identifies HIGH thinking as itself a diversity mechanism, and H9 is a test *of* diversity mechanisms, so the setting may bias the H9 null's direction and not merely its level |

**The registered commitment**: §8.9 calibrates thinking level on a 20-tile, K=10 pilot
and concludes, verbatim, "**Decision:** Use `thinking_level=minimal` for main
experiment." (`osf/preregistration.md:2135`), with the appendix runtime table fixing
"| `thinking_level` | `minimal` | Calibrated via pilot; minimal achieves equivalent F1
to high at 1/3 latency (see §8.9) |" (CMT-0605). No erratum names `phase3c`.

**What was executed**: all 22 `phase3c` prompt configs and both study YAMLs set HIGH
thinking. Both YAMLs state, verbatim and identically, "All conditions use HIGH thinking
level. Temperature is fixed at T=0.7" (`studies/phase3c-h9-diversity-track1.yaml:40`;
`studies/phase3c-h9-diversity-track2.yaml:37`), and both carry
`optimal_thinking: "high"` in their `carried_forward` block (`:50` and `:47`
respectively). Configs and YAMLs were committed together on **2026-03-07**
(`ec00c2ae0`, "feat(phase3c): scaffold H9 diversity testing for both tracks"); the first
`phase3c` API execution timestamp is **2026-03-18** — the declaration therefore
pre-dates execution by 11 days and cannot be a post-hoc reconstruction. Execution ran
2026-03-18 to 2026-03-25 across 225 passes.

**Verification caveat (recorded at the PI's explicit mis-recording warning)**: all 225
`phase3c` meta files record `configuration.thinking_level: "high"` — a mechanical count,
225/225, zero exceptions. **But the retest-era pipeline left `usage_stats` wholesale
unpopulated**, so token-level corroboration is unavailable. Every one of the 225 metas
carries `usage_stats` with `total_tokens: 0`, `total_thoughts_tokens: 0`, and every
other counter at zero; the sibling `retest/phase3a` (180 metas, all `minimal`) and
`retest/phase3a-high` (90 metas, all `high`) directories are identically empty. The
distinction that matters: elsewhere in the project, **known-HIGH runs show millions of
thoughts tokens** (e.g. `outputs/55maps-text-high-generalisation/` passes record
45.7–46.4 M `total_thoughts_tokens`; `outputs/gs/` passes record 1.3–2.7 M) and
**known-minimal runs show zero thoughts tokens against a non-zero total** (e.g.
`outputs/gs/**/run.meta.json`: `total_thoughts_tokens: 0`, `total_tokens: 21633`).
`phase3c` shows **nothing** — not zero-thinking. The absence is an absence of accounting,
not evidence of minimal thinking. The wording of this erratum therefore rests on
configuration plus the pre-committed YAML declarations, and says so.

**What can be established structurally** (defence search, charter rule 13). Three
independent facts narrow the gap without closing it:

1. **No CLI override was in play.** `thinking_level` is set in the 22 config JSONs
   themselves (22/22 `"high"`), not passed as a runtime flag. E42's failure mode — meta
   recording the config default while a `--model`-style override changed the actual API
   call — structurally cannot arise where no override exists.
2. **The request builder and the metadata writer read the same key.**
   `scripts/lib_llm_metadata.py:531` writes `"thinking_level": self.config.get(
   "thinking_level")`, and the batch request builder at `scripts/lib_batch_api.py:509-513`
   constructs `generation_config["thinking_config"]` from the same
   `config.get("thinking_level")`. Within a single execution the two cannot diverge.
3. **The propagation bug was already fixed.** E34's fix — `"thinking_level":
   condition.get("thinking_level")` added to `generate_execution_units()` in
   `run_phase2.py` — landed 2026-03-15 (`5d7260335`), three days before `phase3c`
   execution began; and Decision 20 (2026-03-15) had just established the mitigation
   pattern `phase3c` uses, namely "separate config files … that differ only in the
   `thinking_level` field".

None of these is a runtime observation of thinking tokens. The honest statement is:
the configuration is verified, the declaration is pre-committed, the propagation path
is repaired and structurally coupled — and the response-side accounting that would close
the loop was not written to disk in this era.

**Aggravator, recorded against interest (Obs 140)**: HIGH thinking is not a neutral
efficiency setting in this project. Obs 140 (`docs/notes/working-notes.md:2239`)
established that HIGH thinking is itself an **unregistered diversity mechanism**:
"HIGH thinking consensus outperforms MINIMAL thinking consensus by +6.8 percentage
points on F1", by a mechanism Obs 140 names explicitly — "At N=30, HIGH thinking
produces 3–4× more detection clusters than MINIMAL" — and concludes "Thinking level
interacts with temperature and pool size in ways that make it an experimental factor
for consensus voting workflows, not merely an efficiency setting." H9 is the hypothesis
that tests whether *added* diversity across consensus passes improves detection. Running
every H9 condition — including the H9-A identical-passes baseline — at a thinking level
that is itself a diversity mechanism means the baseline already carries substantial
pass-to-pass diversity. If that raises the floor, the H9 contrasts have less headroom to
show a diversity effect, and the H9 null may be biased toward acceptance. **This
concerns the null's direction, not only its level**, and it should be stated in the
paper wherever the H9 result is reported.

**Mitigating scope**: the setting is **constant across every compared condition** within
H9 — both tracks, all five track-1 conditions (h9-A through h9-E) and all four track-2
conditions (h9-A, h9-B, h9-D, h9-E; h9-C image diversity is degenerate for the text-only
track), across all 225 passes. No H9 contrast is between a HIGH condition and a minimal
one. Separately, the
verification campaign's finding 9 records that of the 41 configs originally flagged for
unlicensed HIGH thinking, **17 were already licensed by name** (E49, E51, E52, E53,
Decision 20); the residue this erratum addresses is the **22 `phase3c` configs**.

**Post-facto acknowledgement**: this disclosure is written in July 2026 about a March
2026 execution, with the H9 result in hand. The thinking level was disclosed on the
study YAMLs at the time and was visible to anyone reading them; what was missing was an
erratum recognising that it departed from §8.9's registered `minimal` decision.

**Protocol impact**: H9 is exploratory (Tier A), so no confirmatory claim is affected.
The H9 result must be reported with two riders: (a) the runs were executed at HIGH
thinking, not the registered `minimal`; (b) HIGH thinking is itself a diversity
mechanism (Obs 140), so the H9 baseline is not a low-diversity baseline and the null
should be read accordingly. Cross-references: E34 (thinking-level propagation),
E42 (metadata field reliability; "Never trust a single metadata field for audit
purposes"), E53 (Phase 3a-HIGH track), Decision 20 (controlled thinking-level
replication), Obs 140 and Obs 141.

---

### E64: Five internal contradictions in the lodged registration — operative readings adopted, reasoning stated, post-facto status acknowledged

| Field | Value |
|-------|-------|
| Date | 2026-07-30 (PI policy decision, GATE 1) |
| Type | Clarification (five reconciliations; no registered procedure altered) |
| Commit | — |
| Files | `osf/preregistration.md` (`:78`, `:269`, `:300`, `:442`, `:815`, `:936-938`, `:968`, `:1443`, `:1450-1451`, `:1882`, `:1892`, `:1898-1901`, `:1921`); `osf/preregistration-coverage.md:237` |
| Impact | None on executed procedure — in every case the execution followed one of the lodged readings. Impact is on interpretation and on the paper's Methods: five parameters are specified two or three ways in the lodged text, and this entry fixes which reading governs |

**Why one entry**: the Phase 1 verification campaign's meta-finding is that the single
most recurrent root cause across its twelve headline findings is **internal
inconsistency within the lodged registration itself** — the same parameter specified two
or three ways, with execution following one of them (findings 1, 2, 6, 7, 8, 11;
`reports/verification/apparatus/defence-pass-adjudication-2026-07-29.md` § "Meta-finding").
Filing five separate errata would obscure the pattern. This is a finding about
preregistration authoring, not misconduct, and it belongs in the paper's Discussion.

**Standing acknowledgement, applying to all five**: each operative reading below was
adopted in **July 2026, with the results in hand**. In every case the execution had
already committed to one reading long before the contradiction was catalogued; what is
post facto is the *recognition and justification*, not the choice of procedure. Where an
operative reading happens to be the conservative one, that is noted; where it is not,
that is noted too.

**Summary**:

| # | Parameter | Lodged reading A | Lodged reading B | Operative reading adopted |
|---|-----------|------------------|------------------|---------------------------|
| i | Hard-example mining K and filter | `:815` — K=10 baseline runs, any-run candidacy | `:1443` — 5 passes; `:1450-1451` — ≥3/5 filter | **The executed procedure**: K=5 passes, any-run HP candidacy (reading A's rule), ≥3-of-5 HN filter (reading B's rule) |
| ii | Corpus size and reserve | § 2.1 `:78` — 361 total, `:76` — 281 reserve | § 8.6 `:1921` — "~360 total"; coverage § 9 `:237` — "321 available" | **The 360 physical tiles** (§ 8.6) |
| iii | Voting cluster membership | § 8.5 step 4 `:1882` — cluster on distance **and matching label** | § 8.5 `:1892` — label is a post-hoc majority vote; § 4.1.2 — evaluation is label-blind | **Spatial clustering, then post-hoc majority label** |
| iv | Tile overlap at 384 px | H11 `:968` — "64px overlap" | H11 `:959` — "~1.8×" API-call multiplier | **Constant overlap fraction** — 48 px overlap, stride 336 at 384 px |
| v | Test tailedness | § 3.1 `:269` — one-tailed for directional predictions | H1 `:442` — two-tailed for modality; § 3.6 `:300` — power computed two-tailed | **Two-sided throughout** |

---

#### (i) Hard-example mining: K and the candidacy filter

**Reading A** (`osf/preregistration.md:815`, § H8 "Availability constraint"), verbatim:

> "The training set contains 36 mounds across 20 tiles. Hard examples are drawn from
> failures across K=10 baseline runs (a mound missed in any run is a candidate HP; any
> false detection is a candidate HN)."

**Reading B** (`osf/preregistration.md:1443`, § 8.4.1 Step 1), verbatim:

> "- Passes: 5 × 20 training tiles = 100 API calls"

and (`osf/preregistration.md:1450-1451`, § 8.4.1 Step 2), verbatim:

> "- **False Negatives (FNs)**: Ground truth mounds missed in ≥3/5 passes"
>
> "- **False Positives (FPs)**: Detections in ≥3/5 passes with no matching ground truth"

The two passages contradict each other twice over: K=10 versus five passes, and
*any-run* candidacy versus a *≥3-of-5* majority filter. Both are lodged.

**Operative reading**: the executed procedure — **K=5 passes; hard positives by the
any-run rule of reading A; hard negatives by the ≥3-of-5 filter of reading B.** This is
verifiable in the artefact: `outputs/h10/hard-cases-v2/pool_160/hard_cases_register.json`
records `k_passes: 5`, and its summary block reconciles exactly —
`borderline_tp: 82` (missed in at least one of five passes) + `consistent_fn: 26`
(missed in all five) = `hp_candidates: 108`, the any-run count; while
`consistent_fp: 57` = `hn_candidates: 57`, the majority-filtered count, out of
`total_fp_clusters: 720`.

**Reasoning**: the hybrid is not opportunistic. The pass count is settled by § 8.4.1,
which is the *operative procedure section* — the registration's own step-by-step
construction protocol — against a parenthetical inside an availability-constraint
paragraph in the H8 hypothesis section. The HP rule follows reading A because the
campaign's binding constraint was hard-positive scarcity, documented at the same line
815 ("If fewer than 16 distinct HPs or HNs are available, Scale-32 (and possibly
Scale-16) will be capped at the maximum available") and exercised in E11 and Decision 11;
a ≥3-of-5 filter on FNs would have deepened an exhaustion the registration already
anticipated. The HN rule follows reading B because false-positive clusters were
abundant (720 candidates), so the stricter filter costs nothing and buys quality. The
spirit of the campaign — build the strongest available hard-example library under a
1:1 ratio constraint — selects each rule on the side where it binds.

**Prior treatment and residue**: E15 already corrects the *appendix's* stale "≥3/10"
references to ≥3/5 and records "Phase 1 was executed with K=5 passes as specified by the
operative procedure". **No erratum has ever named line 815.** This sub-item is that
naming. E15, E49, and E51 license the K=5 substance downstream.

**Post facto**: adopted July 2026. The library built under this hybrid has been in
production since Phase 1; the reconciliation is a justification of a settled fact.

---

#### (ii) Corpus size and the reserve set

**Reading A** (`osf/preregistration.md:76,78`, § 2.1 Map Tile Corpus), verbatim:

> "| Reserve set | 281 | Confirmatory testing | **Untouched** |"

and, two lines later:

> "**Total**: 361 tiles from 4 annotated Soviet topographic map sheets. Maps were
> hand-annotated by students with comprehensive expert review."

**Reading B** (`osf/preregistration.md:1921`, § 8.6 Tile Selection Methodology),
verbatim:

> "- **Tiles**: 512×512 pixel tiles at native resolution (~90 tiles per map, ~360 total)"

**Reading C** (`osf/preregistration-coverage.md:237`, § 9 Stage 2 Design Principles),
verbatim:

> "2. Use **80-160 reserve tiles** (from 321 available)"

Three figures for one corpus: 361 total with a 281-tile reserve; ~360 total; and a
321-tile reserve.

**Operative reading**: **the 360 physical tiles.** `find inputs/tiles -name "*.png"`
returns **360**; `inputs/tiles/full_evaluation_manifest.json` contains **340** entries
(= 360 − 20 calibration tiles); `inputs/tiles/calibration_manifest.json` contains 20 and
`inputs/tiles/validation_manifest.json` contains 60. The reserve is therefore
360 − 20 − 60 = **280**, not 281 and not 321. § 8.6's "~360" is the accurate statement;
§ 2.1's 361 is off by one and its 281 inherits that off-by-one; coverage § 9's 321 is
reconcilable with neither and appears to be a residue of an earlier tile-selection draft.

**Reasoning**: § 8.6 is the methodology section that generated the tiles, and it is the
only one of the three that matches the artefacts on disk. The 361st tile never existed —
repository history contains no deletion of a tile file. Adopting the physical count is
not a choice between defensible alternatives; it is the correction of an arithmetic
slip in the lodged text, and it is adopted because every downstream artefact already
embodies it.

**Consequence, disclosed**: the reserve's status. § 2.1 marks the reserve
"**Untouched**"; E36 (2026-03-17) expanded the evaluation corpus to 340 tiles, which
absorbs the entire reserve. E36's own numbers disclose this; a dated correction block
attached to **E20** (2026-07-30) records that E20's "The 281-tile reserve remains
unnamed/untouched" was falsified by that expansion.

**Post facto**: adopted July 2026. The 340-tile corpus has been the production
evaluation set since March 2026.

---

#### (iii) The voting step-4 label clause

**Reading A** (`osf/preregistration.md:1882`, § 8.5 Spatial Clustering Algorithm,
step 4), verbatim:

> "   - Greedy clustering: for each unclustered detection, find all others within 20m
> and matching label; group as cluster"

**Reading B** (`osf/preregistration.md:1892`, § 8.5 Consensus Detection Output),
verbatim:

> "- **Label**: Majority vote among constituent detection subtypes"

together with § 8.5's own alignment clause (`osf/preregistration.md:1898-1901`),
verbatim:

> "The 20m clustering threshold deliberately matches the spatial tolerance used in F1
> calculation (Section 4.1.1). This ensures that:
>
> - Detections considered "the same" during voting are also treated as matching the same
> reference during evaluation
> - No artificial precision loss from threshold misalignment"

and § 4.1.2's matching algorithm, which is purely spatial — steps 1–7 at
`osf/preregistration.md:362-368` compute pairwise centroid distances, threshold them at
20 m, and run the Hungarian assignment, with **no reference to labels or subtypes
anywhere**.

**Operative reading**: **spatial clustering, then a post-hoc majority label** — that is,
reading A's label gate is not applied.

**Reasoning**: reading A is self-defeating on the registration's own terms. If cluster
membership already requires matching labels, then every cluster is label-homogeneous by
construction and reading B's "Majority vote among constituent detection subtypes" is
vacuous — the registration would be specifying a majority vote over a set that can only
ever hold one value. Reading A also breaks the registration's own alignment clause:
evaluation (§ 4.1.2) matches on distance alone, so a label-gated voting step would split
into two clusters what evaluation will treat as one location, which is exactly the
"artificial precision loss from threshold misalignment" that § 8.5 says the design
exists to prevent. Only the spatial-only reading leaves both of § 8.5's other provisions
with work to do. This is a case where the registered text contains a clause that cannot
be executed without nullifying two neighbouring clauses in the same section.

**Materiality, computed (PI ruling 2026-07-30, "Compute true figure now")**: the two
readings diverge only where detections within 20 m carry different subtypes, so the
governing quantity is cluster-level label heterogeneity, not the overall subtype mix.
Computed on sapphire from committed detection pools, replicating the executed
clustering exactly (`scripts/analyse_cluster_label_heterogeneity.py`;
`reports/verification/apparatus/cluster-label-heterogeneity-2026-07-30.md` + `.json`):
**2.21 % of 153,102 spatial clusters are label-heterogeneous** (47 pools — all 45
Era-1 phase3c H9 pools plus the Era-2 flash-high-text pool at N=30 and N=5; Era 1
2.17 %, Era 2 2.61 %). The label gate's bite is threshold-dependent: at the operative
vote thresholds it would remove **1.6–2.4 %** of spatially-passing clusters (t=3 of 5
across both eras; t=16 of 30 at the headline operating point), rising to ~10 % at
unanimous 5-of-5 and at 26-of-30, and ~17 % at 30-of-30 — a heterogeneous cluster can
pass a strict threshold on combined votes while no single label reaches it. Earlier
subtype-share proxies are superseded as materiality bounds: the re-verified 17.2 %
(phase3c track-1 H9-A run-1 pool, 4 954 detections: 82.8 % `burial_mound`, 10.1 %
`benchmark_mound`, 6.4 % `triangulation_mound`, 0.7 % `settlement_mound`) stands as a
descriptive subtype mix only, and the defence pass's "~21 %" carried no recorded pool
or denominator and could not be re-verified.

**Post facto**: adopted July 2026. The spatial-only implementation has been in the
voting code since the pipeline was built.

---

#### (iv) Tile overlap at 384 px

**Reading A** (`osf/preregistration.md:968`, § H11 Implementation), verbatim:

> "- Tiles generated from source maps with 64px overlap"

**Reading B** (`osf/preregistration.md:959`, § H11 condition table), verbatim:

> "| B | 384×384 | 0.56× | ~1.8× | Higher |"

**Operative reading**: **constant overlap fraction — 48 px overlap, stride 336, at
384 px.**

**Reasoning**: the registration's own cost arithmetic requires it. At the 512 px
baseline (§ 8.6 `:1921`), a 64 px overlap gives stride 448. Preserving that overlap
*fraction* (64/512 = 12.5 %) at 384 px gives overlap 48 and stride 336, and the tile
count scales as (448/336)² = **1.78× — the "~1.8×" the registration states**. Carrying
the 64 px overlap across *literally* gives stride 320 and (448/320)² = **1.96×**, which
the registration does not state. Reading A and reading B cannot both hold; reading B is
the one the registration used to justify the condition's cost, and it is the one that
matches the 0.56× area multiplier in the same row. Execution followed reading B: stride
336 is disclosed in E51's parameter table ("| Stride | 448 px | 336 px |") and carried
into E52 ("| Stride | 448 px | 336 px (E51) |"), and it is hard-coded in the analysis
pipeline (`scripts/evaluate_detections.py:1330`, "stride=336 overlaps neighbours by
48 px"; `scripts/build_example_pool.py:243`). (The gate package's citation of Obs 211
for the stride disclosure was found incorrect at drafting — Obs 211 contains only a
passing mention of the 48 px overlap zone — and is not carried here.)

**Residue, stated plainly**: E51 and E52 disclose the executed stride as a parameter of
their re-runs. **Neither addresses `osf/preregistration.md:968` on its own terms** — that
is, neither says "the registered 64 px overlap clause was not followed, and here is
why". This sub-item is that statement.

**Post facto**: adopted July 2026. The 384 px corpus was generated at stride 336 in
early 2026 and every 384 px result in the project rests on it.

---

#### (v) Test tailedness

**Reading A** (`osf/preregistration.md:269`, § 3.1 Significance Testing), verbatim:

> "- **Direction**: One-tailed for directional predictions; two-tailed for equivalence
> tests (H1)"

**Reading B**, two lodged instances that contradict reading A. § H1 Analysis
(`osf/preregistration.md:442-443`), verbatim:

> "- Two-tailed tests for modality comparisons"
>
> "- One-tailed for elaboration: H0: verbose ≤ brief; H1: verbose > brief"

— i.e. H1 is *not* uniformly an equivalence test as § 3.1 asserts; it is split, with
directional elaboration contrasts run one-tailed and modality contrasts two-tailed. And
§ 3.6 Power Considerations (`osf/preregistration.md:300`), verbatim:

> "With 60 holdout tiles containing 79 mound symbols, statistical power is adequate for
> detecting moderate effects. Approximate detectable effect sizes (80% power, α = 0.05,
> two-tailed):"

— i.e. the registration's own power calculation, which underwrites the whole design, was
computed **two-tailed**, including for the directional hypotheses § 3.1 would run
one-tailed.

**Operative reading**: **two-sided tests throughout.**

**Reasoning**: two-sided is **strictly conservative** for a directional prediction — it
demands a larger effect to reach the same α, so no claim is strengthened by the choice
and any surviving claim would also have survived the one-tailed rule. It is also the
reading consistent with the registration's own power arithmetic (§ 3.6), so the design's
stated detectable effect sizes remain valid rather than being optimistic by construction.
The scope of the contradiction is narrow: the one-tailed rule bites H2, H3, H4, and one
H1 elaboration contrast only. It should be stated plainly that **no tailedness licence
exists anywhere in the errata**: the executed two-sided practice was never erratum'd
before now.

**Post facto**: adopted July 2026, with results in hand. Mitigating the post-facto
concern: because two-sided is the conservative direction, adopting it after seeing
results cannot have manufactured a significant finding — it can only have suppressed
one. Any hypothesis that would have been significant one-tailed but is not two-sided
should nonetheless be reported as such in the paper, so the reader can apply the
registered rule if they prefer it.

---

**Protocol impact (E64 as a whole)**: none on executed procedure. In all five cases
execution followed one of the lodged readings; nothing is being changed, only
adjudicated. Reporting requirements: (a) the paper's Methods states the operative
reading for each of the five parameters; (b) the Discussion carries the meta-finding —
that a registration can be internally inconsistent in five distinct places without any
single inconsistency being visible at authoring time, and that this is a hazard of long,
multiply-revised preregistrations rather than of this project in particular; (c) each
operative reading is flagged as adopted post facto. Cross-references: E11 and Decision 11
(HP pool exhaustion), E15 (appendix pass-count corrections), E20 and E36 (corpus and
reserve), E45 (unregistered inference method — the tailedness question compounds it),
E49/E51/E52 (K=5 substance and stride disclosure), E53.

---

### E65: Registered verifier prompt `verify_brief.md` edited post-lodgement (commit `5e7601d77`) — the one prompt-divergence commit with no contemporaneous erratum

| Field | Value |
|-------|-------|
| Date | 2026-07-30 (disclosure; commit 2026-02-03) |
| Type | Deviation (lodged prompt text altered post-lodgement; lodged appendix never amended) |
| Commit | `5e7601d77` |
| Files | `prompts/system-instructions/verify_brief.md`, `prompts/system-instructions/propose_brief.md`; lodged text at `osf/preregistration-appendix-prompts.md:1088-1128` |
| Impact | Low-medium. Affects the `verify_brief` verifier strategy arm only; E39 establishes verifier strategy is not load-bearing, and the production pipeline uses `verify_adversarial.md` |

**Description**: the Phase 1 verification campaign established that the lodged prompt
appendix was byte-accurate at lodgement and that all subsequent divergence occurred in
five post-lodgement commits between 2026-02-02 and 2026-02-11, **four of which were
erratum'd within 24 hours**. Commit `5e7601d77` (2026-02-03, "feat(prompts): Update
two-stage prompts per Opus review") is the fifth, and carries no contemporaneous
erratum. This entry supplies it.

**What changed in `verify_brief.md`** — the registered H2 Stage-2 verifier prompt, lodged
verbatim at `osf/preregistration-appendix-prompts.md:1088-1128` (§ 1.6.2, "**Used by**:
H2 (Stage 2)"). The commit:

1. **Rewrote key test 2.** Lodged: "2. Do rays point OUTWARD (mound) or INWARD
   (quarry/pit)? Inward → not a mound." Executed: "2. Do rays point OUTWARD (mound) or
   are there marks pointing INWARD (not a mound)? Inward marks may appear in orange-brown,
   the same colour family as mound symbols."
2. **Added key test 5** (not present in the lodged text): "5. Is the shape round or ovoid
   in mound-like colours but without outward-radiating rays? Dark marks within the shape
   rather than extending outward → not a mound."
3. **Added key test 6** (not present in the lodged text): "6. Does nearby Cyrillic text
   (e.g., "могила", "кург.") appear to confirm the candidate? Text does not confirm or
   deny — the ray pattern is the sole criterion."
4. **Extended the reference-example sentence.** Lodged: "If reference examples are
   provided, compare the candidate against them." Executed: the same sentence plus "Each
   reference image is centred on the feature being labelled."

The same commit made two smaller edits to `propose_brief.md` (occlusion language,
centre-pointing sentence); E58 already records that `propose_brief` was **never used** in
any PV experiment, and cites this commit as "prompt refinement, never invoked" (E58).
The `verify_brief.md` half is different: `verify_brief.md`
**was** executed, as the "brief" arm of the verifier-strategy comparison
(`prompts/configs/verify_brief.json`, `verify_brief-text.json`;
`studies/phase3d-h2-twostage.yaml:68`; outputs under
`outputs/h11/proposer-verifier-384/verified-brief-*`).

**Rationale for the edits** (from the commit message): they apply the same hard-example
review outcomes recorded in E16 — Change 2A (marks/rays distinction), Change 3 (round
shapes), Change 2B (Cyrillic text) — to the two-stage prompts, "which were still in their
pre-hard-example state". The intent was consistency across the prompt suite, not a
change to the verifier's decision rule; the diagnostic criterion (outward-radiating rays)
is unchanged and the added tests operationalise exclusions already present elsewhere.

**Protocol impact**: the `verify_brief` verifier arm was executed against a prompt that
differs from the lodged appendix text in the four respects above; the lodged appendix was
never amended. Blast radius is bounded by E39, which found all three verifier strategies
statistically indistinguishable at 340-tile scale (adversarial 0.770, checklist 0.769,
brief 0.752, all CIs overlapping), and by the fact that the production pipeline uses
`verify_adversarial.md`, not `verify_brief.md`. Cross-references: E14, E16 (and its
2026-07-30 correction block), E39, E58.

---

### E66: `run_study.py` → `run_phase1.py` / `run_phase2.py` orchestration substitution — formalising Decision 15

| Field | Value |
|-------|-------|
| Date | 2026-07-30 (disclosure; substitution 2026-02-05) |
| Type | Clarification (orchestration layer substituted; batch engine unchanged) |
| Commit | `c64a7dceb` (adds `run_phase2.py`, archives `run_study.py`) |
| Files | `scripts/run_phase1.py`, `scripts/run_phase2.py`, `archive/deprecated-scripts/run_study.py`, `scripts/4_detect_mounds_batch.py`; lodged mapping at `osf/preregistration.md:2027-2032` |
| Impact | None on results. The script that issues API calls and records metadata is the one the registration names and is unchanged |

**Description**: § 8.7.3 of the registration maps hypotheses to scripts, naming
`run_study.py` in five of six rows — for example "| H1, H4, H5, H7 | `run_study.py`,
`4_detect_mounds_batch.py` | `lib_advanced_metrics.py` |"
(`osf/preregistration.md:2027`) and "| H9 | `run_study.py` (extended for diversity) |
`lib_advanced_metrics.py` |" (`:2032`). Execution did not use `run_study.py`. Phase 1
used `run_phase1.py`; Phases 2a–2e and the retest phases used `run_phase2.py`;
`run_study.py` was archived to `archive/deprecated-scripts/`.

**Decision and documentation**: the substitution is Decision 15 in
`docs/methodology/preregistration/decisions-log.md:671` ("Replace run_study.py with
run_phase2.py for Phase 2 Execution", dated 2026-02-05), which records four structural
incompatibilities between `run_study.py` and the one-factor-at-a-time (OFAT) YAML
structure: hard-coded factorial factor names, a `defaults` versus `fixed` schema
mismatch, no runs loop, and no `{condition}/run_{K}/` output hierarchy. It is also logged
in the execution-checklist deviation table
(`docs/methodology/preregistration/execution-checklist.md:92`: "| 2026-02-05 | D15:
run_phase2.py replaces run_study.py | New OFAT runner for Phase 2; run_study.py archived
to archive/deprecated-scripts/ |"). What was missing was an erratum. This entry supplies
it, formalising Decision 15 as a protocol deviation record.

**Precision on what is and is not post-lodgement**:

- `scripts/run_phase1.py` was **first committed 2026-01-21** (`fa5d53ede`) — ten days
  **before** lodgement (2026-01-31). It is not a post-lodgement substitution; the
  registration simply did not name it. E2 already refers to it by name.
- `scripts/run_phase2.py` was first committed **2026-02-05** (`c64a7dceb`), the same
  commit that archived `run_study.py`. This is the genuinely post-lodgement limb.
- `scripts/4_detect_mounds_batch.py` — the **batch engine named in the same lodged
  rows** — was first committed 2025-12-18 (`88545c84a`) and was not replaced. It remains
  the component that constructs prompts, issues API calls, and writes detection
  metadata.

**Protocol impact**: none on results. The substitution replaced an orchestration wrapper
— condition enumeration, run looping, checkpointing, output-directory layout — while
leaving the execution engine the registration names in place. No prompt, model,
temperature, thinking level, library, or evaluation parameter changed as a consequence.
The disclosure is owed because the registration names a specific script and that script
was not the one used. Cross-references: E2 (`run_phase1.py` config self-containment),
E34 (`run_phase2.py` thinking-level propagation), Decision 15.

---

### E67: Stale version header in the lodged preregistration — "Document version: 4.6" against a v4.7 changelog

| Field | Value |
|-------|-------|
| Date | 2026-07-30 |
| Type | Correction (documentation metadata; no protocol content affected) |
| Commit | — |
| Files | `osf/preregistration.md:2388` |
| Impact | None on protocol. Cosmetic, but it is the version string a reader of the lodged document sees |

**Description**: the lodged preregistration's footer reads, verbatim
(`osf/preregistration.md:2388-2390`):

> *Document version: 4.6*
> *Created: 2025-12-22*
> *Updated: 2026-01-31*

while the changelog immediately below it opens with a **v4.7** entry
(`osf/preregistration.md:2394`): "- v4.7: Statistical methodology reconciliation — All
per-hypothesis ANOVA references updated to bootstrap CI + FDR, aligning Sections 5–6
with the statistical analysis plan (Section 3) and Decision 10 … no change to
hypotheses, predictions, or experimental design". The v4.7 revision was applied to the
document body — §§ 5–6 do specify pairwise bootstrap comparisons — but the version
string in the footer was not incremented with it. The `Updated:` date (2026-01-31) is
correct and matches the lodgement date.

**Corroboration that v4.7 is the operative version**: the errata document's own header
states "**Associated preregistration**: `preregistration.md` v4.7 (2026-01-31)"
(`protocol-errata.md:5`), and E61 relies on the v4.7 reconciliation as the explanation
for a surviving drafting residue ("'Main effect' is analysis-of-variance vocabulary
surviving from the pre-v4.7 draft; the v4.7 statistical reconciliation replaced
per-hypothesis ANOVA with pairwise bootstrap comparisons").

**Protocol impact**: none. The document content is v4.7; only the footer string is stale.
Because the repository copy has been verified byte-identical to the OSF-posted artefact
(verification recorded in E37's 2026-07-28 withdrawal block), **the stale string is
present in the lodged artefact and cannot be silently repaired** — it is disclosed here
rather than edited. Any paper text or companion document citing the preregistration
should cite **v4.7 (2026-01-31)**. Cross-references: E1 (the same class of
version/date drift in the OSF companion README), E61.

---

### E68: "Academic baseline" designation for text-only conditions retired — falsified by the registration's own H1 test; the deployment pipeline is text-prompted

| Field | Value |
|-------|-------|
| Date | 2026-07-30 (rider; designation lodged 2026-01-31) |
| Type | Clarification (registered interpretive designation superseded by registered results) |
| Commit | — |
| Files | `osf/preregistration.md:52`, `:445`, `:1350`, `:1432`; `results/retest/pairwise-bootstrap-comparisons.json`; `docs/pipelines.md:54` |
| Impact | Reporting only. No procedure or result changes; the paper may not describe text-only conditions as "academic baselines", and the deployment headline's reliance on a text-prompted condition must be disclosed against the registered designation |

**The registered designation**: the lodged registration designates the text-only
conditions as academic baselines at four sites. The H1 site (CMT-0109,
`osf/preregistration.md:445`), verbatim:

> "**Text-only note**: Text-only conditions serve primarily as academic baselines to
> characterise VLM capability without visual examples. The operationally-relevant
> comparisons are among image-using conditions."

with parallel statements at `:52` ("The primary optimisation target is image-based
discovery, as an optimal deployment will almost certainly include visual examples"),
`:1350`, and `:1432`. (The gate package's finding 10 counted "three sites"; a fresh
sweep at drafting finds four — the count is corrected here, artefact over summary.)

**What the registered results showed**: the registration's own H1 prediction 3
(`osf/preregistration.md:407`), verbatim — "Image-based conditions will outperform
text-only conditions" — was **falsified by the registered test**: brief-text beats
image-only by ΔF1 +0.088 (p = 0.004, two-sided, Era-1 340-tile bootstrap,
`results/retest/pairwise-bootstrap-comparisons.json` `comparisons[1]`), and adding
example images to the text prompt does not measurably help (brief-text vs
brief-text-image, ΔF1 +0.022 in favour of text-only, p = 0.38, `comparisons[0]`).
On the registered secondary outcome the completed image track leads (tile-MCC 0.7104,
sole Tier 1 on the 55-map canonical MCC board,
`results/metric-leaderboards/55map-mcc-tiering.md`) — the designation's *substance*
(images matter operationally) survives in MCC terms even as its *role assignment*
(text = academic-only) fails.

**Why the selection of a text condition was nonetheless rule-following**: § 8.4.7's
operative one-factor-at-a-time carry-forward clause contains no modality restriction —
selecting `brief-text` as the production carry-forward followed the registration's own
selection rule applied to the registered results. The deployment headline and the
55-map generalisation runs are built on the text-prompted `detect_brief-text`
configuration (`include_example_images: false`). Two nuances must be carried into the
paper: (a) "text-only" refers to the *example* modality — the deployment remains a
vision pipeline reading map tiles; text conditions drop example *images*, not images;
(b) E27's promise that exploratory extensions are reported as exploratory still
applies to any post-carry-forward text-condition claims.

**Retirement**: the designation is retired as a description of the executed study.
Residue fixed in the same landing wave: `docs/pipelines.md:54` ("Purpose: Academic
baseline to measure image contribution") updated to describe the condition's actual
role. Approved by the PI 2026-07-30
(`reports/verification/phase2-rulings-2026-07-30.md` § 1e), implementing the GATE 1
package § 3 item 6 recommendation (finding 10). Cross-references: E27, CMT-0109,
`reports/verification/phase1-gate-package.md` § 2 finding 10.

---

### E69: Unregistered Flash-verifier thinking levels in `pv-diag-384` (MEDIUM on six conditions, HIGH on one) — a deliberate exploratory verifier-variant matrix

| Field | Value |
|-------|-------|
| Date | 2026-07-30 (disclosure; executions 2026-03-23 to 2026-05-06) |
| Type | Deviation (unregistered parameter levels inside an otherwise-licensed family) |
| Commit | — |
| Files | `outputs/h11/pv-diag-384/verified/*medium*`, `.../verified/flash-high-text-1of5-flash-high-verifier`; `results/run-conditions.json` (`decomposition.pv-diag-384`); `reports/verification/c2-census/licence-census.json` |
| Impact | Low. All seven conditions are exploratory diagnostics; the production carry-forward verifier is `gemini-3-flash` at MINIMAL thinking, vindicated independently by the verifier-robustness programme. No registered result draws on these cells |

**The sites**: seven `pv-diag-384` proposer-verifier conditions run a
`gemini-3-flash-preview` verifier at a thinking level the registration does not
license — MEDIUM on `verified-adv-text-medium-vf-4of5`,
`verified-adv-image-baseline-medium-vf`, `verified-adv-text-baseline-medium-vf`,
`verified-adv-pro-text-medium-vf-3of5`, `verified-adv-pro-text-baseline-medium-vf`,
and `verified-adv-pro-image-baseline-medium-vf`; HIGH on
`verified-adv-text-high-vf-4of5` (verifier configurations as recorded in
`results/run-conditions.json`). The seven sibling conditions whose verifier is
`gemini-3.1-pro-preview` at MEDIUM are licensed by E40's endpoint-constraint rationale
(E40's 2026-07-30 clarification block); this entry covers only the Flash sites, where
nothing forced the level — Flash supports MINIMAL.

**The registered commitment**: the lodged registration fixes verifier thinking at
minimal (CMT-0605; §8.9's "**Decision:** Use `thinking_level=minimal` for main
experiment.", `osf/preregistration.md:2135`). Notably, §8.9's own description of the
parameter enumerates its values as "(`minimal`, `low`, `high`)"
(`osf/preregistration.md:2110`) — **`medium` is absent from the registration's
vocabulary for this parameter**; the §8.9 pilot compared minimal, low, and high, and
never tested medium.

**Provenance — configuration, API accounting, and behaviour all corroborate**:

1. `run.meta.json` `configuration.thinking_level` records `medium`/`high` at every
   site (e.g. `outputs/h11/pv-diag-384/verified/
   flash-high-text-1of5-flash-medium-verifier/run.meta.json`).
2. The API's own token accounting confirms non-minimal thinking: the medium-verifier
   metas record **non-zero `total_thoughts_tokens`** (1,933 on the Flash-medium union
   segment), where known-minimal runs record zero thoughts tokens against a non-zero
   total. (Caveat: the union run's meta is segment-scoped — 1 item recorded against
   3,736 candidates in `probabilities.json` — so token corroboration is per-segment;
   see E71 for the segment-bookkeeping defect.)
3. The behavioural record is decisive: Obs 187 ("Verifier Thinking Level — Flash
   Medium Helps", `docs/notes/working-notes.md:4204`, Session 57, 2026-03-25) reports
   a statistically significant matched comparison between the minimal and medium
   verifier variants — ΔF1 = +0.010, p = 0.001 on text; image ΔF1 = +0.009, p = 0.166 —
   which could not arise from a mislabelled configuration.

**Intent — deliberate, contemporaneously documented, never erratum'd**: the variants
were built as a verifier thinking-level matrix during the Session 57 (2026-03-25)
proposer × verifier diagnostics, partly to compare Flash and Pro verifiers at a
matched thinking level (Pro's floor being MEDIUM, per E40). The finding was recorded
as Obs 187 the same day, and `flash-high-text 4-of-5 + medium-vf` (F1 = 0.885) was
briefly the project's working headline before the minimal-verifier replication
superseded it. The HIGH site is the on-disk verifier prior scored at zero cost during
the verifier-robustness programme's thinking axis (S110). The exploration was visible
in the working notes throughout; what was missing was an erratum recognising that it
departed from the registered `minimal` decision. PI ruling 2026-07-30, verbatim: "For
Flash it was an unlicensed exploratory run that needs a new erratum"
(`reports/verification/phase2-rulings-2026-07-30.md` § 1a).

**Post-facto acknowledgement**: this disclosure is written in July 2026 for executions
of March–May 2026, with the results in hand and after a systematic census surfaced the
licence gap.

**Protocol impact**: none on registered results. All seven conditions are exploratory
verifier diagnostics; the production carry-forward verifier (`gemini-3-flash`, T=0.0,
MINIMAL, n=1) was selected independently and vindicated by the verifier-robustness
programme (E62's third family). Any paper use of these cells must be labelled
unregistered exploratory, and Obs 187's medium-helps finding must be reported with
this licence status. Cross-references: E40 (and its 2026-07-30 clarification), E62,
Obs 185, Obs 187.

---

### E70: March 2026 out-of-band tile-recovery campaign (`--patch-tiles`) — 127 passes / 350 tiles recovered; sidecars updated, per-item meta lists left stale

| Field | Value |
|-------|-------|
| Date | 2026-07-30 (disclosure; campaign ~2026-03-17 onwards) |
| Type | Clarification (recovery mechanism disclosed; no experimental parameter changed) |
| Commit | — |
| Files | `scripts/lib_batch_api.py` (`patch_failed_tiles()`, `:2016`); `outputs/retest/**/*.tiles.json`, `outputs/retest/**/*.meta.json`; `reports/verification/c3-rederivation/c3-triage-tiles.json` |
| Impact | None on results — recovered detections are genuine API outputs and the manifests' tile counts are correct. The stale per-item lists produced 127 apparent mismatches in the Phase 2 (C3) provenance re-derivation, all vindicated |

**The mechanism**: batch-API tiles that exhausted the 10-retry ladder (output
truncation being the sole failure mode of the era) were re-run out of band by
`patch_failed_tiles()` (`scripts/lib_batch_api.py:2016`) at a reduced
`max_output_tokens` safe mode. The patcher of that era updated the `.tiles.json`
sidecar (`completed`/`failed`/`patched`/`patch_timestamp`) and the meta's **scalar**
counters (`execution_stats.items_processed` / `items_failed`), but left the meta's
`completed_items[]` / `failed_items[]` **lists** at their pre-patch state — these metas
predate the `merge_meta` recovery path now wired at `scripts/lib_batch_api.py:2343`
and carry no `recovery_history` key.

**Contemporaneous attestation**: working notes, Session 53 ("Tile failure
characterisation", `docs/notes/working-notes.md:3466-3470`), verbatim: "Output
truncation is the sole failure mode. … The 10-retry loop resolves 99%+ of failures;
`--patch-tiles` handles the remainder via reduced `max_output_tokens`." The campaign
was visible in the notes and in every `.tiles.json` it touched; it was never recorded
in the decisions log, the execution-checklist deviation table, or this register. This
entry supplies the missing disclosure (PI ruling 2026-07-30,
`reports/verification/phase2-rulings-2026-07-30.md` § 2.1).

**Scale, from the committed triage artefact**: 127 passes across the retest-era pools,
350 tiles recovered (sum of manifest-minus-derived over the 127 vindicated rows in
`reports/verification/c3-rederivation/c3-triage-tiles.json`; the Session-120 beacon's
"126 passes / 349 tiles" undercounted by the one pass whose second failed tile stayed
permanently unrecovered — `retest-phase3c::track2-text-h9-e-p1::run3`, 339/340
coverage, `.tiles.json`: completed 339, failed 1, patched 1).

**How it surfaced**: the Phase 2 (C3) provenance re-derivation preferred
`len(union(completed_items))` over `execution_stats.items_processed`
(`scripts/rederive_manifest_fields.py:188`) and therefore under-counted every patched
pass by exactly its patched-tile count. All 127 mismatches were triaged
MANIFEST_CORRECT: the manifest generator's era-1 branch reads the post-patch scalar,
which the independent `.tiles.json` and detection GeoJSONs confirm. The decisive
counter-check: the manifest tracks the *recovered* count, not a nominal corpus size —
the one partially-recovered pass reads 339, not 340.

**Protocol impact**: none. Recovered tiles are genuine model outputs under the same
configuration as their parent pass (reduced output budget only); no detection content
was altered. The disclosure is owed because a recovery campaign that touched 127
passes is part of the execution record, and because the stale per-item lists remain
on disk (append-only outputs policy) and will trip any future list-based re-derivation
— as they tripped C3. Cross-references: E57 (a later recovery, resume-merge era), E71
(the dispatched-vs-completed semantics defect the same triage exposed), Obs in
`docs/notes/working-notes.md:3466`.

---

### E71: `n_tiles_processed` manifest column carries two semantics (dispatched vs completed) plus a verifier-row placeholder (GAP-8) — 15 passes with genuine coverage shortfalls, two live conditions carrying dead tiles as artificial false negatives

| Field | Value |
|-------|-------|
| Date | 2026-07-30 (disclosure) |
| Type | Correction (manifest bookkeeping defect + coverage shortfall disclosure) |
| Commit | — |
| Files | `scripts/generate_post_run_report.py` (`:368`, `:398`, `:487-504`); `results/passes-manifest.json`; `reports/verification/c3-rederivation/c3-triage-tiles.json` |
| Impact | Medium-low. Two evaluated `pv-diag-384` conditions score 19–34 dead tiles as zero-detection tiles (artificial false negatives, deflating their F1); six quarantined `n1-outstanding-384` Pro passes carry 15–29-tile shortfalls (not on the current board, E57); the manifest column is not comparable across rows until regenerated |

**Defect 1 — two semantics in one column**: the manifest generator has two branches
for `n_tiles_processed`. When `per_item_metadata` is present it reports
`len(per_item_metadata)` (`scripts/generate_post_run_report.py:368`) — tiles
**dispatched**; when absent it reports `execution_stats.items_processed` (`:398`) —
tiles **completed**. The same column therefore carries different quantities depending
on the meta era, and rows are not comparable. The two diverge exactly where tiles
genuinely produced no output (per-item `finish_reason = max_tokens` after 15 attempts;
`failed_items[].reason = "Retries Exhausted / Invalid Finish Reason"`).

**Defect 2 — GAP-8 verifier placeholder**: for verifier passes the generator reports
`usage_stats.by_provider.google_gemini.request_count` (`:504`), self-flagged in the
code comment at `:487` as a carry-forward — request counts are per-candidate-crop and
retry-inflated, not tile counts (surfaced by the
`55maps-text-min-n10-uplift::verified-3of10` row: 16,484 requests vs 16,482 crops
verified, `retries_total: 2`). The defect silently shapes every verifier row,
including the ones that happen to match.

**Defect 3 — segment-scoped metas**: the resume-merge path leaves `per_item_metadata`
(and the overwritten `.tiles.json`) holding only the **final recovery segment's**
items. Two `n1-pro-rerun-384` passes report 26 dispatched for full-corpus (487-tile)
coverage — there the re-derivation, not the manifest, is right; and one pass
(`pv-diag-384::flash-high-image-n5-image-t0.0::run1`) has **both** values wrong: the
segment meta (33 attempted / 17 recovered) overwrote the original, while the pass's
actual coverage is 471 tiles, recorded only in the cumulative GeoJSON's
`processed_tiles`.

**The genuine coverage shortfalls** (Phase 2 C3 triage, 15 rows): six
`n1-outstanding-384` `pro-*-high-t0` passes short 15–29 tiles each — **not** on the
current `n1-baseline-matrix-384` board (E57 replaced those cells with
`n1-pro-rerun-384`, all 487/487; the preserved rows in `results/conditions-manifest.json`
do score the dead tiles); five `pv-diag-384` flash-high t0.0 passes — image pool
run_2/run_3 short 34 each (run_1's true coverage 471, 16 short), text pool
run_1/run_2/run_3 short 19/20/20; and four single-tile shortfalls
(`e47-propose-brief::propose_brief-text::run4`, `h12-v2::r3-hp-heavy::run3` and
`::run5`, `flash35-pv-2x2::flash35-min-text-1of10::run3`).

**Live impact**: two evaluated conditions consume the shortfall pools —
`pv-diag-384::flash-high-image-n5-image-t0.0-consensus-1of3` and
`pv-diag-384::flash-high-text-n5-text-t0.0-consensus-3of3` — and their evaluations
score the full 487-tile bounds (`evaluation.json` `coverage.n_tiles = 487`), so the
dead tiles enter as **artificial zero-detection tiles**: any ground-truth mound on
them is an artificial false negative, deflating recall and F1 for those two cells.
The working-notes claim that unretried tile failures were "isolated to those two
cells" (`docs/notes/working-notes.md:17339`, about the E57 pv-diag medium-t-0-0
cells) also gains a counterexample from the same triage: current board cell
`pv-diag-384::baseline-flash-image-minimal-t-0-0` is 483/487 — recorded as an
append-only Obs rider, never an edit.

**Remediation (PI ruling 2026-07-30, verbatim: "Erratum + fixes + rerun to sweep up
failed tiles (through usual API-gate process including dry-run, approval, etc.)" —
`reports/verification/phase2-rulings-2026-07-30.md` § 2.2)**:

1. this disclosure;
2. the generator is fixed in the same landing wave to a single completed-tiles
   semantics (with dispatched counts preserved under a distinct field where
   available), the GAP-8 placeholder resolved, and E55's promised `run.log`
   provenance implemented; manifests regenerated;
3. a recovery rerun to sweep up the dead tiles is registered under execution rule 10
   (`status: planned` before any API call) and gated by dry-run, configuration audit,
   and per-batch PI cost approval before any spend.

Cross-references: E55 (and its 2026-07-30 correction block), E57, E70, GAP-8
(`scripts/generate_post_run_report.py:487`).

**Rider (2026-08-02)**: the registered recovery rerun executed
2026-07-30 (commit `99ae28ec4`, 255/288 tiles recovered, ~2.5 h after
this entry landed). Post-recovery coverage for the six affected
passes: image run_1/2/3 → 484/483/485, text run_1/2/3 → 485/486/486
(shortfalls 1–4, from 16–34). The Live-impact paragraph above
describes the pre-recovery state; residual F1 deflation is now bounded
by 1–4 tiles per pass, not 19–34.

---

### E72: Temperature comparison (group_4/group_12) scored a 240-tile arm against 487-tile bounds — coverage confound in an unregistered exploratory analysis

| Field | Value |
|-------|-------|
| Date | 2026-08-02 (identified by C4 verification sweep, Session 125) |
| Type | Analysis defect (exploratory; no registered hypothesis affected) |
| Files | `results/pairwise/{20m,30m}/group_4_temperature/`, `results/pairwise/factor-analysis-20m/group_12/`, `results/paper-eval/flash-min-text-t10-*/`, 9 paper tables (inventory: `reports/e43-coverage-confound-remediation-2026-08-02.md` § 4) |
| Impact | ΔF1 +0.168…+0.194 "temperature effect" is a coverage artefact; matched scope gives −0.034…+0.039, nothing significant; ~530 clean tests' BH q-values were computed against confounded p-values |

**Description**: The 2026-03-26 bounds standardisation re-scored all
paper evaluations against `full_evaluation_bounds.geojson` (487
tiles). Seven of eight studies in that pass had full coverage; the E43
study covers 240 tiles by design, and no coverage check ran (the
sparse-coverage guard reads zero-detection fractions, which
mound-bearing unprocessed tiles evade — zero_fraction 0.4641 vs the
0.5 threshold). The 2026-03-28 temperature comparison then paired this
arm against 487-tile T=0.7 arms under the unexpected-data policy —
defensible at the time (the only 384 px T=1.0 data then in existence)
but never revisited after the matched 10-run 487-tile `text-t1.0` arm
landed on 2026-04-17. One uncontrolled variable is documented in the
matched analysis (`results/e43-matched-temperature/findings.md`
§ 8.3): the arms took different execution paths (async Batch API vs
governed realtime, 24 days apart) with identical system-instruction
and library hashes.

**Remediation (PI commissioning and approval, 2026-08-02)**:

1. this disclosure + the E43 correction block;
2. matched-scope re-analysis at N=5/10 (both buffers, 10,000
   permutations, first-N verified from `contributing_passes`):
   `results/e43-matched-temperature/` (commit `6176b985e`) — no
   significant matched-scope difference at any pool size or buffer;
3. the matched cells filed as their own first-class analysis
   (14-buffer + MCC, manifest-registered) rather than spliced into
   the March board; the March 26-condition round-robin regenerated as
   a 23-condition board (confounded cells dropped; BH q-values
   recomputed over the retained pairs); superseded-figures banners on
   the affected dated snapshots;
4. instrument hardening: the 240-tile pool registered in
   `results/evaluation-scopes.md`; the coverage guard counts
   unprocessed tiles directly from `processed_tiles`;
   conditions-manifest coverage caveats set for the derived
   conditions; the verifier-pass `n_tiles_processed` defect fixed.

Cross-references: E43 (+ its 2026-08-02 correction block), E44 (scope
expansion "for consistency" — the comparability cost), E71 (the same
mechanism at 15–34 tiles), Obs 190 (superseded; correction Obs
follows the register landing). The paper's citable temperature
evidence is the preregistered Phase 2b sweep (text +0.072, FDR
p=0.004; image +0.014, ns) — "T=1.0 is a poor default" is supported;
a universal T=0.7 superiority is not.

---

### E73: Preregistration pointer and manifest-name integrity defects (documentation; lodged text immutable)

| Field | Value |
|-------|-------|
| Date | 2026-08-02 (identified by C4 wave-4 blind verification, Session 125) |
| Type | Documentation integrity |
| Files | `docs/methodology/preregistration/osf/preregistration.md` (§ 8.6 pointer, artefact list), `scripts/select_tiles_phase2.py` |
| Impact | Three stale references between the lodged registration and the live repo; one reproducibility defect on a prereg-cited script |

**Description**: (1) `preregistration.md:1915` cites
`docs/methodology/tile-selection-methodology.md` as the methodology of
record; the file moved to `docs/methodology/reports/` on 2026-01-08
(`e4a871dfd`), so the lodged pointer is a dead path. (2)
`preregistration.md:1951` names `inputs/tiles/holdout_manifest.json`,
renamed to `validation_manifest.json` on 2026-01-21 (`640caa0c3`).
(3) `scripts/select_tiles_phase2.py:570,577` still *writes*
`holdout_manifest.json` (and `holdout_samples_per_map` at `:526`),
whereas the live pipeline reads `validation_manifest.json`
(`generate_tile_bounds.py:457`, `preflight_check.py:355`) — re-running
the documented selection command would not regenerate the file the
pipeline consumes.

**Disposition**: the lodged text cannot change; this entry is the
durable cross-walk. The script's output filename and field name are
aligned to the live pipeline in the same landing wave (a rename-only
behavioural fix, PI-approved 2026-08-02; the selection logic and seeds
are untouched). The methodology doc itself was corrected the same day
(holdout figures 20/5 → 60/15 — see its Revised note and
`reports/verification/c4-triage/mismatch-triage-2026-08-02-wave4.json`).

---

### E74: H6 (Flash→Pro transfer, Phase 4) — registered confirmatory hypothesis never executed; deferral never ratified

| Field | Value |
|-------|-------|
| Date | 2026-08-17 (omission spans 2026-03 → present) |
| Type | Deviation (records an omission, not a change) |
| Commit | — (records an omission, not a change) |
| Files | `osf/preregistration.md:651-701`; `studies/phase4-transfer.yaml` |
| Impact | High — the only registered confirmatory hypothesis with no result; excluded (and disclosed as excluded) from the family BH-FDR, which ran over m=7 |

**Description**: the registration specifies H6 as a four-phase
transfer protocol (`osf/preregistration.md:651-701`): Phase 1
baseline (K=10 runs on a 20-tile stratified holdout at 512 px),
Phase 2 one-factor-at-a-time (OFAT) sensitivity over four named
factors (M/E, H5, T, ordering), Phase 3 voting-threshold comparison
("no additional API calls"), and Phase 4 conditional refinement,
closing with a three-way transfer verdict (full / partial / poor,
`:695-699`). None of it was executed. The concrete evidence:
`studies/phase4-transfer.yaml` still carries 13 literal
`PLACEHOLDER` strings (lines 28, 31, 32, 35, 38, 41, 44, 47, 48,
103–106); `inputs/tiles/phase4_validation_manifest.json` and
`inputs/vectors/bounds/phase4_validation_bounds.geojson` were never
created (`git log --all` shows zero commits for either); the
analysis driver was never written; and the execution checklist's
Phase 4 row (`execution-checklist.md:118`) is blank. Of the four
registered OFAT factors, only temperature was ever varied on Pro
(T=0.0 vs T=0.7, and at the substitute 487-tile/384 px scope rather
than the registered holdout — E41); M/E was varied only as
text-vs-image, not as two adjacent levels of the registered
five-level ladder; H5 and ordering were never varied on Pro at all.
The registered analyses were never computed, including three that
cost nothing: the ≥0.03 F1 decision rule (`:677`), the Phase 3
voting-threshold comparison (`:679-683`), and the cost-effectiveness
scope gate (`:691`). The registered advance criterion (`:701`) is
therefore unevaluable, and no "transfer" claim may be made. The
decision trail is a single dated deferral (2026-03-11, for a
competing paper deadline) that was never revisited; no decision to
abandon H6 exists in any committed artefact.

**Protocol impact**: the Pro work that exists is an exploratory
extension, not H6 (E41), and its results were corrected under E57;
any faithful re-run would still inherit the E40 thinking-level
confound (Gemini 3.1 Pro cannot run `thinking_level=minimal`, so the
registered "matched configuration" baseline is unattainable). The
family BH-FDR (2026-07-30) ran with H6 excluded and disclosed as
never run. The scaffolding (selection script, decision-logic
library, tests) is intact and re-execution remains available at the
registered maximum of ~US$48 (`studies/phase4-transfer.yaml:161-165`),
subject to the E40 caveat. Whether to execute the registered protocol
or formally close H6 as not-executed is scheduled for the S134
unexecuted-set adjudication
(`planning/s134-d17-reconciliation-block-2026-08-17.md`).

---

### E75: H13 (overlap/stride) — registered in-scope exploratory contrast silently dropped; arms B and C never executed

| Field | Value |
|-------|-------|
| Date | 2026-08-17 (omission spans 2026-02 → present) |
| Type | Deviation (records an omission, not a change) |
| Commit | — (records an omission, not a change) |
| Files | `osf/preregistration.md:1014-1048`; `config.py:66-68` |
| Impact | Medium — a registered three-arm contrast has no result and no decision trail; tile overlap was a fixed parameter throughout, never a manipulated factor |

**Description**: the registration specifies H13 as a three-arm
overlap contrast (`osf/preregistration.md:1024-1028`: A = 64 px /
stride 448 / 12.5 %, B = 128 px / 384 / 25 %, C = 256 px / 256 /
50 %) with three registered analyses (`:1042-1046`: F1 as a function
of overlap; cost-efficiency per additional API dollar; edge-detection
analysis) and a disjunctive trigger (`:1048`). Only the study's fixed
baseline tiling ever ran; arms B and C were never executed. Nor can
the study claim "arm A ran": every registered H13 analysis is
comparative and needs at least two arms, and arm A is specified in
pixels, so only the 512 px corpus coincides with it — the 384 px and
256 px corpora run 48 px and 32 px overlap (the 12.5 % ratio
preserved) and match neither arm A's overlap nor its stride. The
defensible statement is that overlap was a fixed parameter (12.5 % at
every tile size, `config.py:66-68`), not a manipulated factor. No
edge-effect assessment exists anywhere in `results/`. The trigger's
two clauses had different fates: clause 1 (edge-effect errors in the
Stage 2 holdout evaluation) was never evaluated — Stage 2 as
registered never happened; clause 2 (disappointing F1 warranting
multiple perspectives on the same location) was arguably satisfied
(single-stage baseline F1 0.660) and was answered by different
mechanisms (H3 consensus voting, H2 proposer-verifier), not by
overlap. Provenance note: clause 2 was added on 2026-01-09
(`ce17da492`) with no changelog entry, three weeks before lodgement —
it is nonetheless part of the registered trigger. No dated,
attributed decision to defer or drop H13 exists in any committed
artefact; the status assertions that do exist are undated,
unattributed, and mutually inconsistent, and the two recorded
reasons are undercut by the drafters' own ~$6 costing
(pre-lodgement estimate) and by the three independently generated
tile trees already in the repository.

**Disposition (2026-08-18, Sessions 135–136 — REMEDIATED)**: the
omission has been closed by execution, not by disclosure alone. The
S134 walk (Group E) ruled the arms back in behind a re-pricing gate;
the S135 phase gate re-priced them and caught two load-bearing errors
before any spend (arm C needs **2.99×** the tiles, not the registered
"~2×"; and `evaluate_detections.py` has no deduplication step, so
naive scoring would have manufactured an "overlap hurts precision"
artefact — **that second finding is H13-scoped here and is generalised
to the whole result set in E80**, which measures it at 155 of 333
conditions). Arms B and C ran on 2026-08-17/18 —
`gemini-3-flash-preview`, brief-text, T = 1.0, MINIMAL, 512 px, three
passes each, 6 passes plus a one-tile recovery, **US$5.7488 actual
against a $4.37 gate estimate (+31 %, flagged to the PI, not
absorbed)**. All three registered analyses are reported in
`results/h13-overlap-2026-08-18/findings.md`, with every arm scored
under one uniform rule (preregistered within-pass 20 m
deduplication; a common A ∩ B ∩ C evaluation footprint, since the
three arms' tile manifests turned out not to cover identical ground).
Arm A was re-scored from its committed Phase 2a `brief-text`
detections rather than re-run, so **the committed arm-A F1 values are
superseded and not comparable with the H13 numbers**.

**What the paper may now say.** The prohibition in the Protocol impact
paragraph above is lifted to this extent: overlap/stride effects may
be characterised **for the carried `brief-text` configuration on the
Era-1 four-sheet corpus**, and only there. F1 falls monotonically as
overlap rises (0.5578 / 0.5198 / 0.4025 at 12.5 % / 25 % / 50 %); all
three paired contrasts exclude zero; the registered edge-detection
mechanism is confirmed but sharply localised (the ten mounds arm A
could only ever see within 100 m of a tile edge go from recall 0.2667
to 0.9333 across the arms, against 0.7468 → 0.8706 for the other 528);
and every additional API dollar spent on overlap buys negative F1. The
statement that "overlap was a fixed parameter throughout" remains
correct **for every other result in the study** — H13 is the sole
place where overlap is manipulated, and nothing outside H13 may be
read as evidence about it.

**Residual deviations, all disclosed**: the arms ran out of sequence,
after the study's other phases; the registered "optimal configuration
from Stages 1-2" could not be identified (the Era-1 single-pass board
is a 20-cell Tier-1 tie), so a carried configuration is held constant
across arms and the result is stated for that configuration under the
plateau rule; arm A is reused rather than re-run, and its passes are
March pipeline vintage against August for arms B and C (E66-class);
arm A's dollar cost is imputed, not audited, because those passes ran
free-tier. Register: `h13-overlap-2026-08-18`
(PROPOSED `registered-exploratory`, PI ratification queued; the S135
plan had proposed `post-hoc` — the disagreement is recorded in the
row). The prior `h13-overlap-stride` disposition row is marked
superseded and awaits the PI's ruling on whether to retire it.

**Protocol impact**: H13 does not shelter under the Tier C
"registered as deferred" framing that covers H14/H15 — it was
registered fully in scope and dropped silently. The paper must
disclose it as unexecuted and must not characterise overlap/stride
effects. E64 sub-item (iv) fixes the operative overlap reading for
H11's tiling (constant 12.5 % fraction) without addressing the
missing H13 contrast; the two disclosures are complementary, not
redundant. Re-execution is feasible (three tile trees exist; spatial
deduplication machinery exists) at an indicative ~$6-8, but that
figure is a pre-lodgement drafting estimate and must be re-priced
before it is relied on. Disposition is scheduled for the S134
unexecuted-set adjudication.

**Cross-reference (added 2026-08-18)**: the missing-deduplication
mechanism named in the Disposition paragraph above is disclosed in
general form as **E80**. This entry retains only the H13-scoped
statement, because deduplication is what makes the three arms
comparable; the study-wide exposure (155 of 333 conditions, ΔF1@20 up
to +0.058), the compliance reading that it is a comparability confound
rather than a registered-protocol breach, and the paper's obligations
all belong to E80. E80 is also the reason the H13 arms are the only
conditions in the manifest scored on explicitly deduplicated inputs.

---

### E76: H14 (cross-model consistency) — registered as deferred and honoured; three qualifications recorded

| Field | Value |
|-------|-------|
| Date | 2026-08-17 |
| Type | Clarification (registered deferral honoured; qualifications recorded) |
| Commit | — (records qualifications, not a change) |
| Files | `osf/preregistration.md:1052-1070`; `docs/methodology/preregistration/execution-plan.md:691`; `osf/preregistration-coverage.md:163` |
| Impact | Low-medium — no omission to remedy; constrains every generalisation claim to Gemini |

**Description**: H14 (cross-model consistency across Claude and GPT)
was registered as Tier C, deferred to future work, with its reasons
stated in the registration itself (`osf/preregistration.md:1064-1068`)
— the honest case, needing no remedy. Non-execution is positively
verified: of 1,132 pass records, the 1,131 model-labelled ones are
all Gemini (784 `gemini-3-flash`, 305 `gemini-3-flash-preview`, 30
`gemini-3.1-pro-preview`, 12 `gemini-3.5-flash`); the strings
`claude`/`gpt`/`anthropic`/`openai` occur zero times across the six
results manifests; and no Anthropic or OpenAI client appears in any
dependency file. Three qualifications are recorded so the deferral is
not overstated. (A) The deferral is not original to the hypothesis:
it was introduced during the v4.0 restructure (2026-01-07/08) —
pre-v4.0 the same hypothesis (then numbered H12) was "Exploratory but
important for generalisability claims" with a four-phase protocol —
and the deferral target changed from "Paper 2" to "future work" in
`ce17da492` (2026-01-09) without a changelog note. The paper should
not imply the hypothesis was always out of scope. (B) The operational
execution plan still lists H14 as the first Phase 5 priority at
~$40-60 (`execution-plan.md:691`), contradicting the registered
deferral; the preregistration governs. (C) The coverage companion
document counts Claude and GPT as realised levels of the model-tier
factor (`osf/preregistration-coverage.md:163`); only Flash and Pro
were realised — that line must be corrected before the document is
published as a supplement.

**Protocol impact**: every generalisation claim in the paper is
scoped to Gemini. The within-Google comparisons (H6-adjacent Pro
work; `flash35-model-roles`) speak to model capability, not to
architecture- or provider-independence, and must never be cited as
H14 evidence.

---

### E77: H15 (cross-model consensus voting) — registered as deferred; gated on H14, which never ran

| Field | Value |
|-------|-------|
| Date | 2026-08-17 |
| Type | Clarification (registered deferral honoured; gated precondition) |
| Commit | — (records qualifications, not a change) |
| Files | `osf/preregistration.md:1074-1088`; `docs/methodology/preregistration/execution-plan.md:696` |
| Impact | Low — no omission to remedy; blocks any cross-architecture ensemble claim |

**Description**: H15 (consensus voting across heterogeneous models)
was registered as Tier C, deferred, with three numbered grounds, the
first being a dependency on H14 results
(`osf/preregistration.md:1082-1086`). H14 never ran (E76), so the
registered precondition was never satisfied: H15 was gated, not
skipped. Non-execution is positively verified: no scored condition
aggregates votes across models — the 322 conditions span 123
distinct proposer pools, all single-model by name, and a model-level
join over the 1,132 pass records yields 265 distinct
`(run_id, proposer_pool)` pairs of which exactly one spans two
models. What exists instead is cross-model *cascading*: four
`flash35-pv-2x2` conditions and seven `pv-diag-384` conditions pair
a single-model proposer pool with a different-model verifier,
including the `unswept-pools-completeness` result (Pro verifier over
the Flash-HIGH union, +0.015, raw p=0.019, post-hoc, not
multiplicity-controlled). These test cross-model verification, not
the heterogeneous-vote averaging H15 specifies, and must not be
cited as H15. One mixed-model pool exists unaggregated
(`pv-diag-384::pro-high-text-n5-text-t0.7`: `config.model` records
Flash for runs 1–5 and Pro for runs 6–10); the fields E57 designates
authoritative for model attribution are absent from its batch
metadata while E57 separately asserts the pool is genuinely Pro —
that provenance must be settled before any analysis of the pool is
published, and no reported number in the study is the output of a
cross-model vote either way. The execution plan lists H15 as a
Phase 5 priority at ~$15-25 (`execution-plan.md:696`), contradicting
the registered deferral; the preregistration governs. Search hazard:
before the v4.0 renumbering, "H15" designated the few-shot library
hypothesis (now H8), so the changelog line "H15 promoted to
confirmatory" (`osf/preregistration.md:2403`) is not evidence about
cross-model voting.

**Protocol impact**: no claim about cross-architecture ensemble
diversity may be made. A within-Gemini voting analogue over the
mixed pool would cost $0 in API terms but is provenance-gated as
above. Disposition (with H14's) is recorded as disclose-only unless
the S134 unexecuted-set adjudication rules otherwise.

---

### E78: Section 8.9 post-experiment thinking-level verification — registered confirmatory comparison never executed

| Field | Value |
|-------|-------|
| Date | 2026-08-17 (surfaced by the S134 blind verification pass) |
| Type | Deviation (records an omission, not a change) |
| Commit | — (records an omission, not a change) |
| Files | `osf/preregistration.md:2139-2145` |
| Impact | Low-medium — a registered verification of the minimal-thinking decision has no result; the latency limb has no coverage at all |

**Description**: the registration's § 8.9 closes its thinking-level
pilot with a registered commitment (`osf/preregistration.md:2139-2145`):
"A confirmatory analysis with full Hungarian matching at the optimal
configuration will compare: Detection accuracy (F1, precision,
recall); Latency per tile; Token usage and API costs", verifying the
§ 8.9 decision to run the main experiment at
`thinking_level=minimal` (`osf:2135`). It carries no hypothesis
number, so it fell outside every per-hypothesis reconciliation until
the S134 blind verification pass surfaced it. It was never executed
as registered. The closest coverage is the post-hoc analysis
`min-vs-high-thinking-pv`, which compares F1 and cost at the optimal
proposer-verifier configuration and finds MINIMAL at statistical
parity with HIGH on the gold-standard instrument — the direction
§ 8.9 anticipated — but it does not report latency per tile, is not
the registered full-Hungarian construction, and its scope note
records that the parity REVERSED at 55-map deployment.

**Protocol impact**: the practical claim § 8.9 licenses ("minimal is
truly equivalent at 1/3 the latency") may not be asserted; the paper
may cite the post-hoc F1/cost parity with its scope caveat, and must
not cite a latency result, which does not exist. The obligation is
recorded in the analyses register as a named-programme disposition
row (`s8-9-post-experiment-verification`, `not-executed`). Whether
to execute the registered comparison (a $0 recomputation for
F1/tokens over committed outputs; latency would need timing metadata
already recorded in run sidecars, or a small re-measurement) is a PI
decision not yet taken.

---

### E79: Order-dependent tile assignment in `evaluate_detections.py` — a scoring sensitivity of ~0.01 F1 on the 123 conditions whose detection artefact carries no `source_tile`

| Field | Value |
|-------|-------|
| Date | 2026-08-18 (surfaced while building the H13 overlap scoring chain, Session 136) |
| Type | Clarification (records a scoring-path sensitivity; no committed result changes) |
| Commit | — (documents a property of the scoring path; no code change) |
| Files | `scripts/evaluate_detections.py:1431-1444`; `scripts/lib_advanced_metrics.py:746-801` and `:1106-1184`; `scripts/prepare_h13_scoring.py:287-334`; measurements in `results/scoring-sensitivity-2026-08-18/` (`probe-batch1.json`, `probe-batch4.json`, `exposure-survey.json`) |
| Impact | Low — no committed number is wrong and no within-analysis ranking is affected, but the two scoring chains in the repository differ by ~0.01 F1 on affected cells, and the committed rule is not invariant under row reordering |

**Description**: Hungarian matching in
`lib_advanced_metrics.calculate_f1_internal` (`:1106-1184`) runs **per
map sheet**, not globally: the function loops over the sheets present in
the evaluation bounds (`:1149`) and scopes detections to a sheet by
string-matching the detection's `source_tile`
(`:1159`, `gdf_det['source_tile'].str.startswith(map_name)`). Which
sheet a detection is booked to therefore determines which reference
subset it can match against.

Most detection artefacts carry a `source_tile` written by the detector
itself. Aggregated artefacts do not: `merge_passes.py` writes
`source_tiles` (plural, a list of contributing tiles), so the
consensus GeoJSONs arrive at the scorer without the singular key. For
those, `evaluate_detections.py` derives one
(`:1431-1444`):

```python
joined = gpd.sjoin(
    gdf_det, gdf_bounds[["tile_name", "geometry"]],
    how="left", predicate="intersects",
)
joined = joined[~joined.index.duplicated(keep="first")]
gdf_det["source_tile"] = joined["tile_name"]
```

Because the study tiles at 12.5 % overlap, a detection in an overlap
band intersects two or more bounds tiles, and `keep="first"` resolves
the ambiguity by **GeoDataFrame row order** — a property of how the
bounds file happens to be serialised, not of the detection's geometry.
Between 29 % and 39 % of detections in the measured cells intersect more
than one tile, so the tie-break is exercised constantly.

The repository already contains the principled alternative and applies
it to the other side of the same matching problem: references are booked
to the tile whose **centroid is nearest**
(`lib_advanced_metrics._assign_refs_to_primary_tiles`, `:746-801`),
and the H13 overlap chain uses that same rule for detections
(`prepare_h13_scoring.assign_primary_tiles`, `:287-334`). Detections and
references are therefore assigned by two different rules in the
committed scorer, and by one uniform rule in the H13 chain.

**Measurement**: ten committed consensus cells were scored under both
rules from the same detection and bounds files, with everything else
held fixed (`scripts/scoring_sensitivity_probe.py --mode tiebreak`;
outputs in `results/scoring-sensitivity-2026-08-18/probe-batch1.json`).
The `first_intersecting_tile` column reproduces the committed
`evaluation.json` value exactly in every cell, which validates the
harness.

| Condition | n | intersect >1 tile | change tile | change **sheet** | F1@20 first | F1@20 nearest | ΔF1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `pv-diag-384::flash-minimal-text-n30-t07-text-t1.0-consensus-9of10` | 549 | 195 | 90 | 10 | 0.6667 | 0.6565 | −0.0102 |
| `pv-diag-384::flash-high-text-n5-text-t0.7-consensus-26of30` | 415 | 150 | 63 | 7 | 0.8141 | 0.8047 | −0.0094 |
| `pv-diag-384::flash-high-text-n5-text-t0.7-consensus-n10-9of10` | 431 | 153 | 59 | 6 | 0.7968 | 0.7875 | −0.0092 |
| `pv-diag-384::flash-high-text-n5-text-t0.3-consensus-10of10` | 409 | 142 | 56 | 6 | 0.7891 | 0.7773 | −0.0118 |
| `pv-diag-384::flash-high-image-n5-image-t0.7-consensus-7of10` | 405 | 156 | 63 | 7 | 0.7500 | 0.7405 | −0.0095 |
| `retest-phase3a-high::text-high-t0.7-n30-22of30` | 478 | 143 | 67 | 7 | 0.7729 | 0.7591 | −0.0138 |
| `retest-phase3a-high::text-high-t1.0-n30-23of30` | 442 | 127 | 61 | 6 | 0.7747 | 0.7625 | −0.0122 |
| `retest-phase3a-replication::text-high-t0.7-n30-21of30` | 520 | 158 | 72 | 7 | 0.7705 | 0.7573 | −0.0132 |
| `retest-phase3a::image-t0.7-n30-18of30` | 535 | 170 | 77 | 9 | 0.6909 | 0.6834 | −0.0074 |
| `gold-standard-v2::consensus-5of5` | 420 | 152 | 62 | 8 | 0.7649 | 0.7556 | −0.0094 |

Four further consensus cells at low vote thresholds
(`probe-batch4.json`) fall in the same band: −0.0028 to −0.0096 at 30 m.

Three features of the measurement matter. First, the **magnitude is
small and tightly bounded**: ΔF1 spans −0.0028 to −0.0138 across
fourteen cells, with the ten primary cells clustered at −0.0074 to
−0.0138. Second, only a handful of reassignments actually bite: of the
56–90 detections per cell that change tile, only **6–10 change map
sheet**, and only those can change the matching problem — a
within-sheet reassignment moves the per-tile bootstrap unit but not the
point estimate. Third, the **direction is systematic, not noisy**: the
nearest-centroid rule scores lower than the committed rule in all
fourteen cells, so the committed figures sit at the optimistic end of
the interval spanned by the two defensible rules.

**Exposure**: exactly the conditions whose scored artefact carries no
`source_tile`. `scripts/scoring_sensitivity_survey.py` establishes this
by reading every artefact behind every condition in
`results/conditions-manifest.json`: **123 of 333 conditions**, all of
architecture `consensus` (register:
`results/scoring-sensitivity-2026-08-18/exposure-survey.json`,
`summary.n_tiebreak_exposed`). The 125 single-pass conditions and all
83 proposer-verifier conditions carry a `source_tile` written upstream,
so the scorer never reaches the tie-break for them and their committed
values are exactly reproducible.

**Why this is a sensitivity and not an error**: neither rule is
prescribed by the registration, which specifies the matching algorithm
in full (§ 4.1.2, `osf/preregistration.md:358-372`: one-to-one Hungarian
assignment over a cost matrix truncated at the spatial tolerance) but
never states that matching is partitioned by map sheet, and says nothing
about how a detection lying in a tile-overlap band is booked to a
sheet. Both rules are defensible; the
committed rule is merely arbitrary rather than wrong. Every committed
comparison applies one rule uniformly across all of its arms, so
**within-analysis validity is preserved** — no leaderboard ordering,
tier assignment, or hypothesis outcome computed inside a single chain is
affected by the choice. What the arbitrariness costs is:

1. **Cross-chain comparability.** The H13 overlap chain
   (`results/h13-overlap-2026-08-18/`) assigns detections by nearest
   centroid; every other committed evaluation assigns them by first
   intersection. Numbers from the two chains are offset by roughly
   0.01 F1 and must not be placed in the same table without a note.
   This is the "F1 agrees to within 0.0012" residual already recorded in
   `results/h13-overlap-2026-08-18/findings.md` § validation and
   decomposed in `k-sensitivity/k_sensitivity.json`.
2. **Reproducibility under row reordering.** Regenerating a bounds file
   with a different feature order, or upgrading a library whose spatial
   index emits joins in a different order, would move the affected
   figures by up to ~0.014 F1 without any change to data or method. The
   committed numbers are reproducible from the committed inputs, but
   they are not reproducible *in principle* from a re-derived bounds
   file.

**Protocol impact**: none on any registered outcome. No committed value
is withdrawn or revised. Three obligations follow for the paper:

- Report the tile-assignment rule in Methods as part of the evaluation
  specification, rather than leaving it implicit — "a detection lying in
  a tile-overlap band is assigned to the first intersecting tile in
  bounds-file order" — and cite this erratum for the measured
  sensitivity.
- State the ~0.01 F1 sensitivity once, with the fourteen-cell range,
  wherever consensus F1 values are compared across the H13 chain and the
  main chain. Do not restate it per number.
- Do not report a difference smaller than ~0.014 F1 between two
  consensus cells as meaningful on the strength of the point estimate
  alone; the confidence intervals already committed are wider than this,
  so no published interval is invalidated, but a bare point-estimate
  ordering inside that band is not robust to the tie-break.

Making the rule uniform (nearest centroid for detections as well as
references) is a one-line change to `evaluate_detections.py` that would
require re-scoring 123 conditions at $0 API cost. Whether to do so is a
PI decision; the argument against is that it would move committed
numbers by ~0.01 for no gain in validity, and the argument for is that
it removes a latent reproducibility hazard and makes the two chains
commensurable. This erratum records the sensitivity so that the decision
can be deferred without the information being lost.

Cross-references: E72 (coverage confound in an unregistered exploratory
analysis — the same family of "scoring-path property that looks like a
result"), E75 (H13 execution, whose scoring chain adopted the uniform
rule), and the S136 review at
`reports/scoring-sensitivity-review-2026-08-18.md`, which also treats
the second, larger scoring-path finding of the same session (the
missing within-pass deduplication).

---

### E80: No within-pass deduplication in the scoring path — a comparability confound on 155 of 333 conditions, preregistration-compliant but asymmetric across architectures

| Field | Value |
|-------|-------|
| Date | 2026-08-18 (mechanism caught by the S135 H13 phase gate; exposure, effect, and compliance reading established in Session 136) |
| Type | Clarification (records a scoring-path asymmetry; no registered requirement was breached, no committed value is withdrawn) |
| Commit | — (documents a property of the scoring path; the only change landed with this entry is the correction of a false statement in `docs/troubleshooting.md`) |
| Files | `scripts/evaluate_detections.py:430-432`; `scripts/merge_passes.py:71` and `:137-219`; `scripts/extract_candidates.py:272-284` and `:315-324`; `osf/preregistration.md:1861-1901`, `:358-375`, `:313-329`, and `:1036-1040`; `config.py:66-68`; `docs/troubleshooting.md:121` (corrected); measurements in `results/scoring-sensitivity-2026-08-18/`; compliance reading in `reports/dedup-gap-compliance-2026-08-18.md` |
| Impact | Medium — no committed number is wrong and no registered outcome changes, but two scoring paths coexist in the result set, and any comparison spanning them carries an F1 offset of up to ~0.058 that scales with detection density |

**Description**: `scripts/evaluate_detections.py` applies no spatial
deduplication to detections anywhere in its scoring path. Its per-buffer point
estimate comes straight from `lib_advanced_metrics.calculate_f1_internal`
(`:430-432`), which Hungarian-matches whatever features it is handed. (The one
`# Deduplicate` comment in that file, at `:1437-1442`, deduplicates the *tile
list* for a detection and is the separate E79 tie-break, not a spatial merge.)

The preregistered within-pass 20 m deduplication lives elsewhere, in
`merge_passes.deduplicate_within_pass` (`scripts/merge_passes.py:137-219`,
greedy star clustering at `DISTANCE_THRESHOLD_METRES = 20.0`, `:71`). Whether a
scored artefact has been through it is therefore a property of the **path the
artefact took**, not of its architecture label:

- **Multi-pass consensus and weighted-box-fusion cells reach it** — they are
  deduplicated by construction, because `merge_passes` is how they are built.
- **Single-pass cells do not.** A raw pass is scored exactly as emitted.
- **Proposer-verifier cells whose proposer pool was a single raw pass do not
  either.** `scripts/extract_candidates.py` crops one candidate per input
  feature with no clustering (`:315-324`); its only concession to the issue is
  normalising `source_tiles` → `source_tile` (`:272-284`). Duplicate proposals
  become duplicate crops, are verified independently, and — where both copies
  clear the probability threshold — land in the scored accepted set as two
  detections.

The study tiles at 12.5 % overlap in both axes at every tile size
(`config.py:66-68`: `TILE_SIZE = 512`, `OVERLAP = 64`,
`STRIDE = TILE_SIZE - OVERLAP`). A mound in an overlap band is therefore seen
and emitted twice, and under § 4.1.2's one-to-one matching the second copy
scores as a false positive.

**Why this is a comparability confound and not a protocol violation**: the
registered text scopes within-pass deduplication to the consensus/voting
pipeline. Section 8.5 is headed "Voting Implementation"
(`osf/preregistration.md:1861`) and opens "Consensus voting aggregates
detections from multiple passes into a single prediction set" (`:1863`); the
requirement itself reads "**Within-pass deduplication**: *Before voting*,
detections from overlapping tiles within the same pass are deduplicated using
the 20m spatial tolerance. This prevents a single pass from contributing
multiple votes for the same physical location detected in adjacent tiles"
(`:1869`, emphasis added). Its stated purpose is vote-count integrity, and it
is step 1 of a seven-step Spatial Clustering Algorithm (`:1875-1885`) whose
remaining six steps — pool, distance, cluster, count votes, threshold, output
centroid — presuppose N > 1 passes.

The registered **evaluation** protocol contains no such step and instead
specifies what becomes of a second copy: § 4.1.2 (`:358-375`) prescribes
one-to-one Hungarian assignment in full, defines "**False Positive**: Each
unmatched detection (not assigned to any reference)" (`:368`), and claims as a
property that "a single detection cannot satisfy multiple references"
(`:375`). Section 3.8 "Evaluation Protocol" (`:313-329`) is silent on
overlap-band duplicates. The scorer's behaviour is therefore what the
registered algorithm says it should be.

The one place the registration prescribes deduplication outside the voting
pipeline is H13's own Implementation block — "Spatial deduplication applied to
handle redundant detections" (`:1039`) — which is precisely the hypothesis
where overlap is the manipulated factor, and it **was** honoured (see E75
disposition; `results/h13-overlap-2026-08-18/findings.md:127-134`). That H13
had to say it separately is itself evidence that § 8.5 Step 1 does not bind
general evaluation. The 26 exposed proposer-verifier conditions are covered by
nothing at all: PV is "a post-hoc extension to the preregistered single-stage
detection approach" (`decisions-log.md:1070`, Decision 22).

Full reading, with every quotation anchored:
`reports/dedup-gap-compliance-2026-08-18.md`.

**What is nevertheless wrong** is an asymmetry the registration did not
anticipate: § 8.5 Step 1 makes multi-pass artefacts deduplicated by
construction while single-pass and single-proposer-pass artefacts are not, so
**two scoring paths coexist in the same result set**. A comparison that places
an exposed cell against an unexposed one — the shape of the
consensus-versus-single-pass and diversity-dividend claims — measures the
scoring-path difference in addition to the effect it names.

**Exposure**: established by measurement, not by reading `architecture`.
`scripts/scoring_sensitivity_survey.py` resolves the scored detection files
behind every condition in `results/conditions-manifest.json` and counts the
features lying within 20 m of another feature in the same artefact
(`:155-185`). Register:
`results/scoring-sensitivity-2026-08-18/exposure-survey.json`.

| Architecture | conditions | exposed (>1 %) | median pair involvement, exposed | max |
|---|--:|--:|--:|--:|
| single-pass | 125 | 123 | 0.129 | 0.229 |
| proposer-verifier | 83 | 26 | 0.190 | 0.250 |
| consensus | 125 | 6 | 0.037 | 0.069 |
| **total** | **333** | **155** | — | — |

All 333 conditions resolved; none was unreadable. 289,065 features sit in the
exposed set. Two caveats on the table. First, "pair involvement" counts every
feature having at least one neighbour within 20 m and is roughly twice the
fraction deduplication actually removes; the removal fractions are 0.0–12.7 %
across the 48 probed cells. Second, the 123 single-pass figure includes
`h13::arm-c-overlap-50`, which *was* deduplicated but retains a 3.20 % residual
because greedy star clustering is not quite idempotent at 50 % overlap; the
genuinely un-deduplicated single-pass set is 122. The 6 consensus conditions
are all low-vote-threshold cells at 1.6–6.9 % and are the same non-idempotency
residual, an implementation-fidelity matter inside a registered step rather
than a gap.

**Effect, measured on 48 cells at US$0.00**:
`scripts/scoring_sensitivity_probe.py --mode dedup` scores each cell twice from
the same bounds and ground truth — once exactly as committed, once after
applying `deduplicate_within_pass`. The as-committed column reproduces the
committed `evaluation.json` F1 to four decimal places in all 48 cells, which
validates the harness.

**Every one of the 48 deltas is non-negative.** ΔF1@20 spans **+0.0000 to
+0.0578** and ΔF1@30 spans **+0.0000 to +0.0589**; the three near-zero cells
are `h13::arm-a-overlap-12-5` (already deduplicated, +0.0000),
`55maps-image-generalisation::verified` (+0.0004), and `h13::arm-c-overlap-50`
(+0.0044), with the remaining 45 spanning +0.0090 to +0.0578 at 20 m. Recall is
bit-identical before and after in every proposer-verifier cell and unchanged in
33 of the 68 single-pass cell–buffer pairs; precision does all the work
(0.8060 → 0.9235 at 30 m on the most exposed cell). That signature — precision
rises, recall does not move — is the strongest evidence that the removed
features are duplicates rather than detections.

The magnitude scales with detection density, so **paired contrasts do not
cancel**. For geometric calibration: raw removal at 12.5 % overlap is 5.9–6.7 %
per pass, at 25 % it is 15.7–17.9 %, and at 50 % it is 39.2–40.0 %
(`results/h13-overlap-2026-08-18/findings.md:138-142`).

**Which committed claims this reaches.** Both study headlines are safe: the
gold-standard headline `pv-diag-384::verified-adv-text-consensus-16of30` has
pair involvement 0.0000, and the 55-map deployment cell moves +0.0004 F1@20.
Two paper-cited claims are materially at risk, both because they compare an
exposed cell against an unexposed one:

- the `diversity-dividend-384` Tier-1 three-member tie
  (`results/diversity-dividend-384/tiering-champions/tiering_20m.json`,
  `tie_set`), where the consensus champion `consensus-flash-high-text-26of30`
  (F1@20 0.8141, unexposed to deduplication) is currently at the top of a tie
  containing two exposed Pro single-pass baselines —
  `n1-pro-rerun-384::baseline-pro-text-high-t-0-0` (0.8045 → **0.8545**) and
  `pv-diag-384::baseline-pro-text-medium-t-0-0` (0.7921 → **0.8211**). On
  deduplicated point estimates the "cheap Flash consensus reaches the expensive
  Pro single-pass tier" framing reverses direction; and
- the § R5 zero-diversity anchor `pv-diag-384::verified-adv-text-baseline`,
  the single most exposed condition in the study (pair involvement 0.2500),
  F1@30 0.8320 → **0.8905**, which moves it from 29th to 13th of the 39 rows on
  `gs-era2-pv-family-30m` and shrinks the measured diversity dividend
  substantially.

Neither movement has been tested. Every figure above is a **point estimate**;
no bootstrap interval or permutation tiering was re-run, so whether the Tier-1
tie survives is unknown. One further approximation must be stated plainly:
deduplicating an *accepted* proposer-verifier set post hoc is not identical to
what deduplicating before crop extraction would have produced — the verifier
would have seen ~405 crops rather than 464, and the accepted set could differ
in composition as well as count. Full assessment, including the claims verified
unexposed: `reports/scoring-sensitivity-review-2026-08-18.md` § 3.

**Relationship to E75 and E79.** E75 (H13) records the mechanism in passing, in
the narrow form in which the S135 phase gate met it: "`evaluate_detections.py`
has no deduplication step, so naive scoring would have manufactured an 'overlap
hurts precision' artefact". That statement is correct and remains in place
because it is load-bearing for H13's disposition, but it is scoped to three
conditions. **E80 is now the general disclosure**; E75 cross-references it.

E79 (order-dependent tile assignment) is the *other* scoring-path finding of
the same session, and the two must be kept separate in the paper. They are
near-disjoint (155 versus 123 conditions, 6 in common), they run in opposite
directions (deduplication raises F1, the nearest-centroid tile rule lowers it),
and they differ in magnitude by roughly fivefold. E79 is a genuine sensitivity
between two equally defensible rules; E80 is an asymmetry between two paths
only one of which the registration contemplated. Bundling them into one
"scoring caveats" note would make the deltas unattributable — and, if both were
fixed in one commit, unmeasurable.

**A contributing cause worth recording.** `docs/troubleshooting.md:121`, under
the heading "Duplicate Detections", stated from `211a1bce4` (2026-01-18,
thirteen days before lodgement) that "The evaluation script handles
deduplication using 20m clustering." This is false, and it is the entry an
operator who noticed duplicate detections would have consulted. The false
reassurance plausibly explains why the gap survived to Session 135, and it is
corrected in the commit landing this erratum.

**Protocol impact**: none on any registered outcome. No committed value is
withdrawn or revised, and no deviation from the registered evaluation algorithm
is disclosed — § 4.1.2 was followed. Four obligations follow for the paper:

- **Describe both scoring paths in Methods.** The Methods draft currently
  mentions deduplication nowhere. It must state that multi-pass aggregation
  applies § 8.5 Step 1 within-pass deduplication at 20 m, that single-pass and
  single-proposer-pass conditions are scored as emitted, and that overlap-band
  duplicates therefore score as false positives in the latter per § 4.1.2.
- **Do not present a cross-path comparison without re-scoring it.** Any table
  or claim placing an exposed cell against an unexposed one needs both sides on
  the same path, with confidence intervals, before it can be published as an
  effect.
- **Re-score selectively, not blanketly.** The targeted campaign in
  `reports/scoring-sensitivity-review-2026-08-18.md` § 6 — the
  `diversity-dividend-384` tiering, the twelve `*-baseline*` rows of
  `gs-era2-pv-family-30m` with the § R5 anchor, the two single-pass baseline
  matrices, and the H1 pooled-modality bootstrap — covers the exposure that
  reaches a reader. 108 of the 155 exposed conditions are per-pass lineage rows
  cited nowhere; re-scoring them would move numbers no reader sees at the cost
  of invalidating every cross-reference into the conditions manifest.
- **Report tile-level MCC movement as unquantified where it applies.** MCC is
  not automatically invariant to deduplication — collapsing two copies emitted
  from two overlapping tiles into one centroid can empty one of those tiles and
  flip its predicted class — and no MCC movement was measured anywhere. The
  55-map MCC boards carry only 1.05 % exposure, so the risk concentrates in the
  gold-standard single-pass boards.

Whether to add deduplication to `evaluate_detections.py` is a PI decision and
is deliberately not taken here. The safer pattern is a `--deduplicate` flag
defaulting off, with the targeted campaign run explicitly under it, since
changing the default would silently move 155 committed conditions. Unifying the
tile-assignment rule (E79) is a separate one-line change with its own ~0.01 F1
cost; the two must not be bundled.

Cross-references: E79 (order-dependent tile assignment — the companion
scoring-path finding of the same session), E75 (H13 execution, whose
disposition first recorded this mechanism in H13-scoped form), E72 (coverage
confound — the same family of "scoring-path property mistaken for a result"),
Decision 22 in `decisions-log.md:1066-1088` (PV as a post-hoc extension), and
the two Session 136 reports:
`reports/scoring-sensitivity-review-2026-08-18.md` (measurement) and
`reports/dedup-gap-compliance-2026-08-18.md` (compliance reading).

---

### E81: Undefined tile-level MCC published as `0.0` — nine conditions reported at the value the scale calls "random" where the metric is not computable, four more depressed by averaging an undefined pass into a mean

| Field | Value |
|-------|-------|
| Date | 2026-08-18 (mechanism first flagged in § 2.6 of the Session 136 deduplication-impact campaign; the defined-versus-undefined split, the corpus-wide exposure, the consumer sweep, and the registered-text reading established independently for this entry) |
| Type | Correction (reporting defect — 13 committed tile-MCC values are withdrawn as published; not a protocol violation, because § 4.2 prescribes no handling for a degenerate confusion matrix) |
| Commit | — (documents the defect and withdraws the values; no code change lands with this entry, because the fix is a PI decision — see **Protocol impact**) |
| Files | `scripts/evaluate_detections.py:533-535` (`_safe_round`) and `:752-788` (multi-run averaging; confusion carried from run 1 at `:787`); `scripts/lib_advanced_metrics.py:1980-1982` (`mcc = None`), `:2034-2036` (docstring) against `:2087-2091` (code), and `:1069-1073` (the divergence already documented on `score_detection_set`); `docs/methodology/preregistration/osf/preregistration.md:390-392` (§ 4.2 scale legend and rationale); `results/conditions-manifest.json` and `.md` (13 of 333 conditions); source evaluations under `results/paper-eval/phase2/512px-14buf-mcc/` and the duplicate root `results/paper-eval/mcc/512px/`; consumers at `docs/paper/results-draft.md:134-135`, `results/analyses-manifest.json` (`era1-single-pass-baseline-matrix.outcome`), and `results/leaderboard/combined/era1/leaderboard_tiers_mcc.md:125-135`; first flag in `results/dedup-metric-impact-2026-08-18/findings.md` § 2.6 |
| Impact | Medium — no F1, precision, recall, or registered hypothesis outcome is touched, but nine conditions publish a value the metric does not have, four more publish an arithmetic blend of measurements and placeholders, one load-bearing sentence of the Results draft rests on the imputed zeros, and an entire published tier of an MCC-tiered leaderboard exists only because of them |

**Description**: the tile-level Matthews Correlation Coefficient (MCC) is
undefined when the 2 × 2 tile confusion matrix is degenerate — when any row or
column marginal is zero, the denominator `√((TP+FP)(TP+FN)(TN+FP)(TN+FN))`
vanishes. `lib_advanced_metrics.calculate_tile_classification` handles this
correctly and returns `None` (`:1980-1982`, "Edge case: MCC undefined when any
row/column sum is zero"). `evaluate_detections.py` then discards the
distinction: the nested helper `_safe_round` (`:533-535`) is documented as
"Round a value, returning 0.0 for None (undefined MCC)" and coerces the `None`
to `0.0` on its way into the published `tile_classification` block.

`0.0` is not a neutral placeholder here. It is a value with a stated meaning on
this scale, and the registration supplies the legend: § 4.2 says MCC "ranges
from -1 (perfect inverse classification) through **0 (random)** to +1 (perfect
classification)"
(`docs/methodology/preregistration/osf/preregistration.md:390`). A reader taking
the published boards at face value therefore reads nine conditions as
*performing at chance* on tile-level discrimination. What the data support is
that the question was not answerable for those conditions. Which of those two
statements flatters the model depends entirely on the surrounding argument —
which is exactly why the substitution cannot be left standing.

**The degenerate case, and which marginal vanishes.** Across all 1,990 per-pass
tile confusion blocks in the committed result set, exactly **35 are
degenerate**, and in **every one of the 35** the vanishing marginal is the same:
**TN + FN = 0**. Every tile in the 340-tile Era-1 scope was predicted populated
— the model emitted at least one detection in all 340 — so the
predicted-negative column of the matrix is empty. This corrects the first flag:
`results/dedup-metric-impact-2026-08-18/findings.md` § 2.6 attributes the
degeneracy to "TN + FP = 0". TN + FP is the count of reference-empty tiles, 136
on this scope, and is never zero anywhere in the committed corpus. Sensitivity
and specificity are consequently always defined — `_safe_round` wraps those too
but never fires on them — so this entry concerns MCC alone.

**The split, verified condition by condition.** Nine conditions in
`results/conditions-manifest.json` publish a tile MCC of exactly `0.0`. All nine
carry the identical confusion matrix TP = 204, TN = 0, FP = 136, FN = 0. **All
nine are the undefined case; not one is a genuine zero.** There is no mixed
population to disentangle:

| Condition | Degenerate passes | TP / TN / FP / FN | Published | Truthful value |
|---|---|---|---|---|
| `retest-phase2b::text-t0.0` | 3 of 3 | 204 / 0 / 136 / 0 | 0.0 | undefined |
| `retest-phase2b::text-t0.7` | 3 of 3 | 204 / 0 / 136 / 0 | 0.0 | undefined |
| `retest-phase2c::image-exploratory-pure-positive-2hp` | 1 of 1 | 204 / 0 / 136 / 0 | 0.0 | undefined |
| `retest-phase2c::text-canonical` | 1 of 1 | 204 / 0 / 136 / 0 | 0.0 | undefined |
| `retest-phase2c::text-plus-hp` | 1 of 1 | 204 / 0 / 136 / 0 | 0.0 | undefined |
| `retest-phase2c::text-pure-positive-canon` | 1 of 1 | 204 / 0 / 136 / 0 | 0.0 | undefined |
| `retest-phase2c::text-scale-4` | 1 of 1 | 204 / 0 / 136 / 0 | 0.0 | undefined |
| `retest-phase2c::text-scale-8` | 1 of 1 | 204 / 0 / 136 / 0 | 0.0 | undefined |
| `retest-phase2d::text-terse` | 1 of 1 | 204 / 0 / 136 / 0 | 0.0 | undefined |

**The averaging effect, which is the less defensible half.**
`evaluate_multi_run_mean` (`:752-788`) averages the per-run MCC blocks
arithmetically with no guard for the coerced zeros — by the time it sees them
they are indistinguishable from measurements. A condition with two computable
passes and one degenerate pass therefore publishes a mean pulled toward zero by
a number that was never a measurement. Four further conditions are affected:

| Condition | Degenerate passes | Published | Mean over defined passes |
|---|---|---|---|
| `retest-phase2a::brief-text` | 1 of 3 | 0.0443 | 0.0665 |
| `retest-phase2a::verbose-text` | 1 of 3 | 0.0443 | 0.0665 |
| `retest-phase2b::text-t0.3` | 1 of 3 | 0.0443 | 0.0665 |
| `retest-phase2b::text-t1.0` | 2 of 3 | 0.0222 | 0.0665 |

Total exposure: **13 of 333 conditions** (3.9 %), all of them 512 px Era-1
phase-2 cells — 13 of the 38 conditions across `retest-phase2a` … `phase2e`.
Every condition outside phase 2, including all 55-map, 384 px, and Era-2
boards, is clean. A second nuance in the same aggregation block: for multi-run
cells the published confusion matrix is **run 1's**, not a sum or a mean
(`:787`, `avg_mcc["confusion"] = mcc_results[0].get("confusion", {})`), which is
why the four rows above show a non-degenerate matrix (TN = 1) beside a mean that
a degenerate pass contaminated. That is a pre-existing schema property rather
than a new defect, but it is what makes the contamination invisible on the face
of the record.

**The bootstrap block has the same defect, and a docstring that denies it.**
`bootstrap_tile_classification_ci` documents its handling of degenerate
resamples as "the score is treated as `NaN` and skipped when computing the CI
bounds" (`:2034-2036`). The code does the opposite: `_mcc_from_idx` returns
`0.0` for any degenerate resample, commented "MCC undefined — return 0.0 so
scipy can compute bounds" (`:2087-2091`). The bootstrap mean and both CI bounds
are therefore mixtures of MCC values and zeros. This is visible in the committed
data: a pass with TN = 1 has a deterministic point of 0.0665 but a bootstrap
mean of 0.0514 and a CI lower bound of exactly 0.0000, because resamples that
happen to omit the single true-negative tile are degenerate and are counted as
zero rather than dropped. Any tile-MCC CI whose lower bound is exactly 0.0000 on
these cells is that substitution surfacing, not a percentile.

**The registered text anticipated this case and got it wrong.** § 4.2's
rationale for preferring MCC reads: "A method that simply predicts 'mounds
present' for every tile would achieve 50 % accuracy but **MCC ≈ 0**" (`:392`).
That is precisely the observed configuration, and the claim is false: the MCC of
an all-positive predictor is not approximately zero, it is undefined, because
the predictor never emits a negative and the predicted-negative marginal is
empty. The `0.0` in the published boards is thus a faithful implementation of
the registration's own stated expectation — and the registration's expectation
is a mathematical error. Both halves need saying: the code is not freelancing,
and the registered rationale cannot be leaned on to defend the published value.

**What the metric is actually measuring on these cells.** On the Era-1 scope,
with TP = 204 and FN = 0 fixed across the whole phase-2 text family, tile MCC
collapses to a step function of a single integer — how many of the 136
reference-empty tiles the model left alone: 0 → undefined, 1 → 0.0665, 2 →
0.0942, 3 → 0.1156. Every published tile-MCC value in that family is one of
those steps, and the gap between a "0.0" condition and a "0.0665" condition is
one tile out of 136. This does not excuse the defect, but it bounds its
scientific consequence: the substantive reading — that phase-2 text-only
conditions have essentially no tile-level discrimination while image conditions
have a little — survives any correction contemplated here, and the confirmatory
proposer-verifier cells of the same phase (`verified-adv-text-t0.0` at 0.7895,
`verified-adv-image-t0.0` at 0.8894) sit an order of magnitude away, untouched.

**The codebase already knew.** `score_detection_set`, the in-process point
scorer added for grid and sweep analyses, documents the divergence explicitly
(`scripts/lib_advanced_metrics.py:1069-1073`): "the one deliberate difference is
that an *undefined* MCC (degenerate tile confusion matrix) is returned here as
`None` rather than coerced to `0.0` as the CLI's `_safe_round` does — `None` is
the more honest 'undefined', and callers should rank/aggregate on F1 (or guard
`None`) rather than treat a missing MCC as zero discrimination." That note
identifies both the defect and the remedy. What it never did was propagate the
remedy back into the command-line interface that writes the committed boards.

**Where this reaches a reader.** A sweep of `docs/paper/`,
`results/metric-leaderboards/`, `results/analyses-manifest.json`,
`results/hypothesis-outcome-table/`, `results/leaderboard/`, and
`results/paper-tables/` found the exposure to be qualitative in the paper and
structural in the leaderboards. No paper file quotes `0.0`, `0.0443`, or
`0.0222` as an MCC.

- **Paper prose — one sentence, load-bearing.** `docs/paper/results-draft.md:134-135`
  reads "a metric trade-off recurs in which text cells reach F1 ≈ 0.60 at
  near-zero MCC while image cells trade F1 for far better tile discrimination".
  "Near-zero MCC" *is* the imputation. Its source is verbatim in the
  `era1-single-pass-baseline-matrix` outcome text of
  `results/analyses-manifest.json` ("text cells reach F1 ~0.60-0.61 at MCC ~0.0
  while image cells trail on F1 but carry higher tile-discrimination MCC"), and
  `docs/paper/results-outline.md:200-201` designates this the home of the D3
  thread and marks the surrounding item **load-bearing**. The claim's
  *direction* survives — image cells at 0.09–0.28 genuinely exceed text cells —
  but its *magnitude* is built on values that do not exist, and the honest text
  cells sit at 0.0665, not at zero.
- **MCC-tiered leaderboards — a tier that exists only as an artefact.**
  `results/leaderboard/combined/era1/leaderboard_tiers_mcc.md:125` opens
  `## Tier 7 (MCC: 0.000–0.000)`, and ranks 87–93 (`:129-135`) are exactly and
  only seven of the nine degenerate conditions. In the per-architecture
  single-pass boards
  (`results/leaderboard/per-architecture/era1/single-pass/leaderboard_tiers_mcc_20m.md`,
  `**Tiering metric**: MCC` at `:4`) the same seven occupy ranks 15–21
  (`:32-38`) and the tier's own lower bound is the imputed value
  (`## Tier 2 (MCC: 0.000–0.164)` at `:18`) — replicated across the 20/30/40/50/100 m
  and `q01` variants and both `tier_stability_mcc` tables, plus the `.json`
  counterparts. Two of the nine (`text-t0.0`, `text-t0.7`) do not reach these
  boards: that stratum carries their K = 3 consensus rows instead, whose MCC is
  defined. The four averaged means do not appear on these boards at all.
- **Not affected.** `results/metric-leaderboards/` — zero occurrences of any of
  the 13 across the directory; its MCC-tiered boards cover 55-map and Era-2 PV
  cells only. The `era1-single-pass-baseline-matrix` **tie set** is safe: it is
  tiered by round-robin tile-swap **micro-F1** permutation (10 k perms, seed 42,
  BH-FDR q = 0.05) at 20 m, with MCC a display column, so the nine affected
  conditions sitting inside that tie set are there on F1.
  `results/hypothesis-outcome-table/` carries no MCC dependence for any of the
  13 — its only MCC references are the two 55-map boards, a different corpus.
  `results/paper-tables/metrics_master.csv` has no MCC column.
- **Other republishers**, none paper-facing: `results/conditions-manifest.md`,
  `results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.{md,json}`,
  `results/era1-leaderboard/tiering_20m.{md,json}`, the per-cell
  `evaluation.{json,md,csv}` under `results/paper-eval/phase2/512px-14buf-mcc/`
  and its duplicate roots, and `reports/d17-inventory/d17-inventory-h5-h8.md:559-563`.
  `results/dedup-metric-impact-2026-08-18/impact-era1-single-pass-board.json` is
  the one artefact that preserves the honest signal, recording the as-committed
  tile MCC as `null`.

**Protocol impact**: this is a **reporting defect, not a protocol violation**.
§ 4.2 registers tile-level MCC as a secondary outcome and fixes the
classification matrix; it prescribes no handling for a degenerate matrix, so no
registered requirement was breached — and, as recorded above, the registration's
own rationale asserts the very value the code publishes. No F1, precision,
recall, or confidence interval anywhere in the study is affected; no registered
hypothesis verdict changes; no tie set moves. What is withdrawn is the
publication status of 13 numbers.

Four obligations follow for the paper:

- **Never print `0.0` for the nine.** Wherever a tile MCC is reported for a
  condition whose tile confusion matrix is degenerate, print "undefined" (or
  "n/a — every tile predicted populated") with a footnote giving the reason, and
  **exclude the cell from any MCC ranking, tier, mean, or tie set** rather than
  seating it at the bottom. A condition for which the metric is not computable
  has no rank on that metric. Tier 7 of
  `results/leaderboard/combined/era1/leaderboard_tiers_mcc.md` should cease to
  exist rather than be renumbered.
- **Restate the four averaged means, or drop them.** `0.0443`, `0.0443`,
  `0.0443`, and `0.0222` are blends of measurements and placeholders and
  correspond to no defensible estimator. Either publish the mean over the
  defined passes — 0.0665 in all four cases, with the pass count stated — or
  report the cell as undefined. Note that the first option collapses four
  apparently distinct values into a seven-way tie at 0.0665 with
  `retest-phase2b::text-t1.3`, `retest-phase2d::text-verbose`, and
  `retest-phase2e::random`, which is the honest picture: all seven differ by at
  most one correctly-identified empty tile.
- **Rewrite the D3 sentence to say what happened.** `results-draft.md:134-135`
  should not say text cells reach "near-zero MCC". It should say that for the
  text-only single-pass cells the model fired on **every** tile in the 340-tile
  scope, so tile MCC is undefined rather than low, and that this is a stronger
  form of the same finding: the metric cannot separate a text cell from chance
  because the text cell never declines to detect. Read that way the D3 thread
  gains rather than loses; what it must not do is quote a number.
- **Do not quote a tile-MCC confidence interval whose lower bound is exactly
  0.0000 on an affected cell.**

**Recommended fix, offered as a recommendation and deliberately not taken
here.** The minimal change is three-part and should land as one commit with a
re-extraction — not a re-run — of the affected cells:

1. Let `None` survive into the JSON: replace the `_safe_round` coercion for the
   `mcc` block with a null-preserving round, so `tile_classification.mcc.point`
   is `null` on a degenerate matrix, and add a sibling boolean `mcc_defined` so
   consumers need not infer undefinedness from a null.
2. Aggregate over defined passes only: in `evaluate_multi_run_mean`, filter
   nulls before averaging, record `n_passes_mcc_defined` beside the mean, and
   emit `null` when no pass is defined.
3. Bring `_mcc_from_idx` into line with its own docstring — return `np.nan` for
   degenerate resamples and use `nan`-aware mean and percentile paths — or, if
   that materially moves the surviving bounds, correct the docstring instead and
   state plainly in Methods that the MCC bootstrap substitutes zero for
   degenerate resamples.

Whether to re-extract or re-run, and whether to accept item 3's effect on
published CIs, are PI decisions. None of this should be bundled with the E79
tile-assignment change or the E80 deduplication decision: all three touch the
scoring path, all three are separable, and bundling them would make their deltas
unattributable.

Cross-references: E80 (deduplication gap — the campaign whose § 2.6 first
flagged this, and whose fourth paper obligation warns that tile MCC is not
invariant to deduplication), E79 (order-dependent tile assignment — the other
scoring-path finding of the same session), E64 (ii) (corpus size — § 4.2's
"30 empty tiles, 30 non-empty tiles" balance is not the executed 136/204
split), and `reports/scoring-audit-notes-2026-08-18.md` (the two suspicions
from the same audit that cleared and therefore have no erratum).

---

#### E81 changelog

##### 2026-08-18 — Fix landed and values re-emitted (Session 136)

The "recommended fix, deliberately not taken here" above **has now been
taken**, in three commits on `main`: `69061a2db` (code and tests),
`6afc393b5` (the 13 re-emitted cells and their manifest/paper consumers), and
`22dc99578` (the two F1-tiered display boards). The withdrawn values are
replaced rather than merely withdrawn, so the `Commit | —` row of the header
table is superseded by this entry.

**What was changed in the code.**

1. `_safe_round` (`scripts/evaluate_detections.py`) preserves `None` instead of
   returning `0.0`. A *genuine* zero — the specificity of a condition that
   false-positives on every reference-empty tile — still returns `0.0`; the
   test suite pins both halves.
2. The per-pass block builder and the multi-run averager were lifted to
   module level as `build_tile_classification_block` and
   `aggregate_tile_classification`, so there is exactly one place that
   decides what an undefined metric looks like. The aggregate averages over
   **defined passes only** and records `n_runs` and `n_runs_defined`; it
   returns `null` when no pass is defined. It also records
   `confusion_source: "run_1"`, making explicit the schema property this
   erratum identified as what "made the contamination invisible on the face
   of the record".
3. `_bca_ci_from_indices` gained `skip_undefined`. `_mcc_from_idx` now returns
   `np.nan` for a degenerate resample, as its own docstring always claimed,
   and the nan-aware mean and percentile paths drop those resamples rather
   than counting them as zeros; `method` becomes `"undefined"` and the bounds
   `null` when every resample is degenerate. `n_valid_mcc` /
   `n_valid_sensitivity` / `n_valid_specificity` stop being hard-coded to
   `n_iterations` and report the true count.
4. Renderers: CSV writes an empty cell, Markdown and the console write the
   word `undefined`, and `evaluation.md` gains a footnote naming the
   degenerate matrix and citing this erratum. Roughly two dozen downstream
   consumers were swept for `None`-handling gaps; the ranking keys that read
   `float(x or 0.0)` were the dangerous ones, because they would have
   reinstated the defect one layer down.

**Deviation from the recommendation, recorded deliberately.** Item 1 above
suggested a sibling boolean `mcc_defined`. That was not added. For a
single-pass cell `mcc.method == "undefined"` is an explicit, non-inferential
marker beside the `null`; for an aggregated cell `n_runs_defined` carries
strictly more information than a boolean. Adding a third redundant flag would
have given consumers three things to keep consistent.

**What moved.** All 13 conditions were re-emitted **surgically** — only the
`tile_classification` block was recomputed and spliced into the committed
`evaluation.json`, with every F1, precision, recall, confidence-interval, and
coverage field carried through untouched. This was a deliberate choice over
a full replay: replaying `evaluate_detections.py` against the recorded
`cli_args` reproduces F1 bit-for-bit, but it also imports every unrelated
change made to the scorer since the cell was written — most visibly the E72
partial-coverage machinery, which flips `coverage_status` to
`partial_coverage` on cells whose detection set does not cover every tile.
Folding that into an MCC-reporting fix would have made both corrections
unattributable, which is the same failure mode this erratum warns about in
its own closing paragraph.

| Condition | Published | Re-emitted | Basis |
|---|---|---|---|
| `retest-phase2a::brief-text` | 0.0443 | **0.0665** | mean over 2 defined of 3 passes |
| `retest-phase2a::verbose-text` | 0.0443 | **0.0665** | 2 of 3 |
| `retest-phase2b::text-t0.3` | 0.0443 | **0.0665** | 2 of 3 |
| `retest-phase2b::text-t1.0` | 0.0222 | **0.0665** | 1 of 3 |
| `retest-phase2b::text-t0.0` | 0.0 | **`null`** | 0 of 3 defined |
| `retest-phase2b::text-t0.7` | 0.0 | **`null`** | 0 of 3 |
| `retest-phase2c::image-exploratory-pure-positive-2hp` | 0.0 | **`null`** | 0 of 1 |
| `retest-phase2c::text-canonical` | 0.0 | **`null`** | 0 of 1 |
| `retest-phase2c::text-plus-hp` | 0.0 | **`null`** | 0 of 1 |
| `retest-phase2c::text-pure-positive-canon` | 0.0 | **`null`** | 0 of 1 |
| `retest-phase2c::text-scale-4` | 0.0 | **`null`** | 0 of 1 |
| `retest-phase2c::text-scale-8` | 0.0 | **`null`** | 0 of 1 |
| `retest-phase2d::text-terse` | 0.0 | **`null`** | 0 of 1 |

The predicted seven-way tie **materialised and was verified, not assumed**:
with the four blended means corrected, exactly seven phase-2 cells now sit at
a tile-MCC point estimate of 0.0665 — `brief-text`, `verbose-text`,
`text-t0.3`, `text-t1.0` (the four corrected) plus `text-t1.3`,
`text-verbose`, and `random`, which were already there. Every one is the same
arithmetic: 204 true positives, one of 136 reference-empty tiles left alone.

The tile-MCC confidence intervals moved on the four corrected cells, as this
erratum predicted they would: `brief-text`'s bound of exactly `0.0000` was the
substitution surfacing, and the honest interval is `[0.0605, 0.1281]` with a
bootstrap mean of 0.081 rather than 0.0343.

**What did not move.** Verified mechanically against `git show HEAD:` for all
25 re-emitted evaluations (13 in `results/paper-eval/phase2/512px-14buf-mcc/`
plus 12 in the duplicate single-buffer root `results/paper-eval/mcc/512px/`,
which lacks the exploratory-2hp cell): **every** field outside
`tile_classification` is byte-identical. No F1, precision, recall, buffer CI,
coverage status, or `n_detections` changed anywhere. A corpus-wide sweep of
`results/` confirms the fix is complete and the diagnosis exact: of **2,103**
committed `tile_classification` blocks, **39** are degenerate, in **all 39**
the vanishing marginal is TN + FN, and **none** now publishes a number.

**Two things moved that were not predicted, and both are reported here rather
than absorbed.**

- *Specificity confidence intervals widened on four cells.* Point estimates
  and bootstrap means are unchanged everywhere (`0.0074` / `0.0073`), but on
  the passes with TN = 1 the interval goes from `[0.0040, 0.0095]` to
  `[0.0000, 0.0236]`. Cause: making the empty-denominator case undefined
  routes those cells off scipy's BCa path — whose jackknife is degenerate
  here — and onto the percentile path, whose resampling is correct. The wider
  interval is the right one: a resample that draws none of the single
  reference-empty-and-correctly-empty tile genuinely has specificity 0.
- *The sensitivity `method` label flips* from `"BCa"` to
  `"percentile_fallback"` on the nine fully-degenerate cells. All four numeric
  fields are unchanged (`1.0`); only the label moves, and it moves toward the
  honest description, since the underlying distribution is constant at 1.0 and
  BCa acceleration is undefined on a constant.

**Consumers corrected.**

- `docs/paper/results-draft.md` § R2 no longer says text cells reach "near-zero
  MCC". It now states that tile MCC is undefined on eight of the fourteen
  phase-2 text-only cells and 0.0665 on the remaining six, against
  0.094–0.291 over the seventeen computable image-bearing cells, carrying a
  `[REVISED 2026-08-18]` marker and a changelog entry. (The four phase-2e
  ordering variants sit in neither group: they are image-track by
  registration but vary example order rather than modality, and one of them,
  `random`, is itself at 0.0665.)
  The **direction** of the D3 metric-trade-off thread survives intact; its
  magnitude did not exist.
- `results/analyses-manifest.{json,md}` — the
  `era1-single-pass-baseline-matrix` outcome text, which was the verbatim
  source of the paper sentence.
- `results/conditions-manifest.{json,md}` — all 13 rows, with
  `mcc_undefined_reason`, `mcc_n_runs`, and `mcc_n_runs_defined` added. The
  Markdown was verified byte-identical to what the (also corrected) generator
  in `scripts/generate_post_run_report.py` now produces, so it cannot drift on
  the next regeneration.
- `results/leaderboard/combined/era1/leaderboard_tiers_mcc.{md,json}` and the
  `_q01` variant, plus `tier_stability_mcc.{md,json}` — see below.
- `results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.{md,json}` and
  `results/era1-leaderboard/tiering_20m.{md,json}` — both tier on micro-F1
  with MCC as a display column, so no rank, tier, p-value, or tie set depends
  on the withdrawn values; only the 13 displayed MCCs changed, and both boards
  gained a legend entry explaining `undefined`.

**The MCC-tiered leaderboard: `## Tier 7 (MCC: 0.000–0.000)` is gone.** The
board was regenerated by a **reproduce-then-correct** procedure. Its
`.cache/` is gitignored and absent from a checkout, but both expensive stages
are recoverable from committed artefacts — the evaluation sweep from
`leaderboard_all_evaluations.json`, the 4,278 permutation tests from the
board's own `pairwise_tests` — so
`scripts/rebuild_leaderboard_cache_from_committed.py` reconstitutes the cache
and the documented driver invocation runs unchanged. Rebuilding from the
*unpatched* cache reproduced the committed board **byte-for-byte** (93
conditions, 7 tiers, identical tier structure), which is what licenses
attributing every subsequent difference to E81 alone.

Rebuilt from the corrected cache, the board carries **86 conditions in 6
tiers**, and the seven undefined conditions appear in a new, explicitly
labelled `## MCC undefined (not ranked)` section that states why they cannot
be ranked. Verified against the committed board: **zero** conditions changed
F1@20 m, best threshold, or MCC; **zero** raw permutation p-values changed;
Tier 1 remains the same 21 conditions spanning 0.638–0.714.

Two conditions did change tier — `h9-track2-text-h9-B-v1` and
`h1-verbose-text-image`, both from Tier 4 to Tier 3 — and the mechanism is
worth stating because it is a real methodological consequence rather than an
artefact. Dropping seven unrankable conditions removes 623 pairwise
comparisons from the Benjamini–Hochberg family (4,278 → 3,655). The raw
p-values of the 3,655 surviving pairs are untouched, but 2,110 of their
BH-adjusted p-values change and nine flip significance, which regroups the
Tier 3 / Tier 4 boundary (Tier 3: 20 → 22 conditions; Tier 4: 9 → 7). This is
the correct outcome: those 623 comparisons were testing a coefficient that
does not exist, and they should never have been carrying multiple-testing
weight. `tier_stability_mcc.{md,json}` was rebuilt from the corrected board
(93 → 86 conditions; Spearman rho remains 1.0 by construction).

**Residuals, deliberately left.**

1. `results/paper-eval/mcc/512px/batch_summary.{json,csv,md}` still carries the
   withdrawn zeros in its JSON rows. It is a 2026-03-27 roll-up that predates
   the Session 102 re-score of the cells beneath it, so regenerating it moves
   **all 33 rows' F1** — five months of unrelated drift that must not land
   under an MCC-reporting fix. `scripts/rescore_tile_mcc_e81.py
   --rebuild-batch-summary` will refresh it whenever the PI wants that drift
   accepted as a separate, attributable change.
2. The per-architecture MCC boards under
   `results/leaderboard/per-architecture/era1/single-pass/` were not rebuilt.
   They carry the same seven conditions at ranks 15–21 across the
   20/30/40/50/100 m and `q01` variants, and their tier-2 lower bound is the
   imputed value. The same reproduce-then-correct procedure applies; it is
   deferred because it multiplies across twelve board files and their
   `tier_stability_mcc` siblings, and because none of them is paper-facing.
3. `_compute_mcc` in `scripts/pairwise_permutation_test.py` still returns
   `0.0` for a degenerate matrix, **by design**: it is the kernel of
   `run_permutation_test_mcc`'s null-resampling loop, called ~10,000 times per
   pair, where a `None` would break the null distribution rather than
   describe it. A companion `compute_mcc_or_none` was added beside it for
   reporting and gating, and the kernel is now documented as
   kernel-only. The residual is that `run_permutation_test_mcc` publishes its
   *observed* `mcc_a` / `mcc_b` / `observed_mcc_diff` through the kernel, so a
   degenerate observed arm would still report `0.0` there. Deciding what a
   ΔMCC against an undefined arm even means is a methodological question, not
   a rendering one, so it is left open. It does not touch the corrected board:
   the seven undefined conditions are excluded before pairwise testing, and
   none of the 3,655 surviving pairs has a degenerate arm.

**Separate finding, not fixed here, flagged for a PI decision.** While pinning
the bootstrap behaviour, the vectorised wrapper inside `_bca_ci_from_indices`
was found to iterate the **wrong axis** of scipy's resample matrix.
`scipy.stats.bootstrap` passes an `(n_resamples, n_observations)` index array
with `axis=-1`, but the wrapper applies `np.moveaxis(idx_array, axis, 0)` and
iterates the result, so the statistic is evaluated once per *observation*
over a vector of `n_resamples` draws rather than once per *resample* over a
vector of `n_observations` draws. On the Era-1 scope this yields a
"bootstrap distribution" of 340 values each computed from 10,000 draws
instead of 10,000 values each computed from 340 draws, and the BCa jackknife
becomes column-wise nonsense (each leave-one-out "sample" contains only two
distinct tile indices — which is precisely why the specificity and
sensitivity labels move above). The consequence is that **every BCa-path
confidence interval in the study is too narrow**, by roughly
`sqrt(n_resamples / n_tiles)` ≈ 5.4× at 10,000 iterations on 340 tiles. The
`percentile_fallback` path resamples correctly and is unaffected. This is
**not** an E81 defect, it is not fixed here, and it should not be bundled
with E81 for exactly the reason this erratum gives for keeping E79, E80, and
E81 separate: fixing it would move essentially every published confidence
interval, and that delta must be attributable on its own. It needs its own
erratum and its own PI decision.

---

### E82: Bootstrap confidence intervals depart from Decision 10 on both method and iteration count — BCa replaced the registered percentile method undisclosed, its vectorised adapter transposed its axes until 2026-08-19, and the corpus runs at 10 000 iterations where E54 records 1 000

| Field | Value |
|-------|-------|
| Date | 2026-08-19 |
| Type | Deviation (undisclosed method substitution) + Correction (implementation defect, fixed) + Correction (supersedes a factual claim in E54) |
| Commit | `122104b8a` (the axis fix and its five regression tests); this entry lands separately and re-emits nothing |
| Files | `scripts/lib_advanced_metrics.py` — `_bca_ci_from_indices` (:299, the transposing wrapper), `bootstrap_ci` (:1278), `bootstrap_tile_classification_ci` (:2107), `_compute_bca_ci` (:521, the unaffected hand-rolled helper); `scripts/evaluate_detections.py:214` and `:710-730` (the `f1_ci_method` / `p_ci_method` / `r_ci_method` and `tile_classification.<metric>.method` write sites), `:539` (`_metadata.bootstrap.method`, a hard-coded literal); `docs/methodology/preregistration/decisions-log.md:345` (Decision 10); the BCa migration `2026999ad` (2026-04-30); this register's E54 (:1901) |
| Impact | Medium. **No point estimate and no published significance verdict changes** — Decision 10's rule is defined on *difference* CIs, and no difference CI in this study reaches the defective wrapper. What changes is the width of single-condition intervals, in both directions, across essentially the whole corpus; and the study's stated statistical method no longer matches the one it ran |

**Description**: Decision 10 fixes the confidence-interval procedure as
"Bootstrap resampling (tile-level) | 1000 iterations, percentile method
(2.5th/97.5th)" (`decisions-log.md:345`). The study as executed matches neither
half of that specification, and the implementation of the substituted method was
defective for sixteen weeks. Three separate disclosures follow. They are grouped
here because a reader auditing any one of them needs the other two to interpret
it, and because the corrective ruling is common to all three.

#### Disclosure 1 — BCa is an unregistered method substitution

On 2026-04-30, commit `2026999ad` ("replace percentile method with BCa") moved
every interval-producing function in `lib_advanced_metrics` from the percentile
method to bias-corrected and accelerated (BCa) bootstrap, via
`scipy.stats.bootstrap(method='BCa')`. The change was made for a defensible
statistical reason, recorded in the commit body: on evaluation scopes where
roughly 80 % of tiles carry zero true positives, false positives, and false
negatives, the percentile interval systematically excluded the all-data point
estimate. The migration was planned
(`planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md`), tagged for rollback
(`pre-bca-mit3-2026-04-29`), and tested.

It was never disclosed. The string `BCa` occurs **zero** times in
`decisions-log.md` and **zero** times in the lodged registration
(`osf/preregistration.md`), and until this entry it occurred in this register
only inside E81's flag of the defect below, never as a disclosure of the method
itself. A reader following Decision 10 to the artefacts would expect percentile
intervals and find, in 1 691 of 1 749 git-tracked `evaluation.json` files, 76 404
intervals labelled `BCa`.

The corpus is in fact mixed-method, which the disclosure has to state plainly.
Alongside the BCa intervals sit 224 intervals labelled `percentile`, in 16 files
under `results/55maps-extended-gt-2026-06-07/` and
`results/55maps-standardised-ref-2026-08-14/`. These are not a pre-migration
residue: they are adapter-written Track-2 corrected-F1 cells whose statistics come
from `compute_corrected_f1_multi_buffer.py`, which does its own percentile
resampling and never enters the BCa path. A further 166 intervals record
`percentile_fallback` (BCa attempted, jackknife degenerate, correct percentile
resampler used instead) and 35 record `undefined`.

#### Disclosure 2 — the vectorised BCa adapter transposed its axes (D15)

`_bca_ci_from_indices` adapts a per-tile statistic to
`scipy.stats.bootstrap(vectorized=True)`. scipy's contract is that the statistic is
computed *along* the passed axis, which is then consumed, so every remaining axis
enumerates independent resamples. The wrapper applied `np.moveaxis(idx_array, axis,
0)` and iterated the result, which walks the observation axis instead. On a
340-tile scope at 10 000 iterations the "bootstrap distribution" was therefore 340
statistics of 10 000 draws each, where it should have been 10 000 statistics of 340
draws each.

A statistic's spread falls as the inverse square root of its sample size, so the
interval width was rescaled by `sqrt(n / B)`. **The error changes sign at `B = n`**,
and both regimes occur in this study: of the BCa intervals whose `n` and `B` can
both be read from the artefact, 69 663 sit at `B > n` and are **too narrow**, while
840 sit at `B < n` and are **too wide**, chiefly the 55-map cells at n = 8 541
evaluated at B = 1 000, where the interval is roughly 2.9 times wider than it should
be. A further 5 901 could not be classified because one or both quantities are
absent from the file. Measured on real committed per-tile counts (n = 340, seed 42),
the defective-to-corrected width ratio is 0.592 at B = 1 000 and 0.182 at B = 10 000,
against `sqrt(n/B)` values of 0.583 and 0.184.

Two consequences bound the damage. Point estimates are untouched: `f1`, `precision`,
and `recall` are written from `calculate_f1_internal`, which does no resampling.
And **no published significance verdict changes**. The registered rule is that a
95 % CI *for a difference* excludes zero, every difference interval in the library
is produced by the hand-rolled `_compute_bca_ci` over a distribution the caller
resampled itself, and that helper never touches scipy's vectorised path. The
defective wrapper is reachable only from single-condition intervals, which the
registered rule does not adjudicate.

The fix landed in `122104b8a` with five tier-1 regression tests, validated to
floating-point equality against `scipy.stats.bootstrap(vectorized=False)`. No
committed interval has been re-emitted. Full working, refutation attempts, and the
verified scope census are in `reports/bca-axis-defect-2026-08-18.md`.

#### Disclosure 3 — E54's factual claim about the iteration count does not hold

E54 (:1901) states that the scripts evaluating preregistered conditions "use 1 000
iterations, matching the preregistration", and frames 10 000 iterations as a
selective post-hoc choice confined to five named narrow-effect analyses. A census
of the committed artefacts contradicts this. Across the 1 749 git-tracked
`evaluation.json` files, **1 583 declare B = 10 000 and 114 declare B = 1 000**,
with 52 declaring no iteration count. The 10 000-iteration setting is not the
exception in this corpus. It is the rule, and E54's split has been inverted since
well before it was written. The library default remains 1 000, so the divergence
was introduced at the call sites rather than by a change of default.

#### The ruling (Principal Investigator, 2026-08-19)

Standardise on 10 000 iterations rather than reverting to the pre-specified 1 000,
re-run what needs re-running at that count, and disclose the deviation here. This
supersedes E54's post-hoc-only framing, which is corrected by reference rather than
rewritten, so that the earlier reading stays legible.

The practical consequence is uniform and worth stating in advance: at B = 10 000
against evaluation scopes of 340 to 487 tiles, `B > n` throughout, so **every
re-emitted interval widens** relative to the committed value. Re-running is a
correction towards conservatism, not towards stronger claims.

**Protocol impact**: the deviation is a methodological one and does not touch any
registered hypothesis outcome. Reported intervals are wider than published for the
dominant regime and narrower for the 55-map B = 1 000 cells, and the statistical
method reported in any paper text must read BCa at 10 000 tile-level iterations,
with the percentile-method cells identified where they occur.

**Remediation** (items 1 and 2 executed 2026-08-19; see the completion note below):

1. The axis fix is landed (`122104b8a`). The `evaluate_detections.py` path now
   produces correct BCa intervals at whatever `B` it is given.
2. Re-emission of committed intervals proceeds by campaign rather than in bulk, so
   that each wave's delta stays attributable, by the same reasoning that kept E79,
   E80, E81, and this entry separate. Tile-MCC needs no separate wave: E81's landed
   re-emission already delivers the corrected intervals for that metric family as a
   by-product, because the defective wrapper made the tile-MCC jackknife undefined
   and diverted those calls to the correct percentile fallback.
3. Paper-facing text must not quote a committed interval width until the cell
   behind it has been re-emitted at B = 10 000 under the fixed wrapper.

**Completion note (2026-08-19)**: the standardisation is executed for everything
the register carries. All 49 evaluations backing
`results/conditions-manifest.json` that ran below 10 000 iterations were replayed
from their own `_metadata.cli_args` with only the iteration count changed
(`scripts/rerun_evals_at_10k.py`; report at
`results/bootstrap-10k-restandardisation.json`). Because these ran under the
pre-`122104b8a` wrapper, one pass delivered both the axis correction and the
standardisation. **All 337 registered conditions now declare `n_iter = 10 000`**,
321 on the BCa path and 16 on the percentile path. Point estimates were gated at
1e-9 and **none moved**.

Interval widths moved as the mechanism predicts, in both directions: 46 of 49
widened and 3 narrowed, with the ratio tracking `sqrt(B_old / n)`. The narrowing
cells are the n = 1 032 scopes, where `B < n` had made the defective interval too
wide (0.96x), and the largest widening is on n = 340 scopes (1.79x against a
predicted `sqrt(1000/340)` = 1.71).

The 16 percentile cells needed no re-run: they had always run at 10 000, but
recorded it as `metadata.bootstrap_n` in their source `summary.json`, a key the
manifest extractor does not read. Their two adapters now restate it in the shape
every other evaluation uses, so the register can see a value that was already
true. `archive/` evaluations and pre-2026-04-30 artefacts that predate the BCa
migration were deliberately left alone: neither backs a live claim, and both are
covered as history by this entry.

**Reference artefacts**:

- Registered specification: `docs/methodology/preregistration/decisions-log.md:345`
- Restandardisation report and script: `results/bootstrap-10k-restandardisation.json`;
  `scripts/rerun_evals_at_10k.py`
- Migration to BCa: commit `2026999ad` (2026-04-30), plan
  `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md`, rollback tag
  `pre-bca-mit3-2026-04-29`
- Defect analysis, refutation attempts, and fix: `reports/bca-axis-defect-2026-08-18.md`;
  fix commit `122104b8a`
- Defect register entries D15 (the axis defect) and D16 (the grid register row it
  blocked): `reports/defect-register-2026-08-18.md`
- Superseded framing: E54 (:1901), corrected by reference
- Method-label evidence lives in `f1_ci_method` / `p_ci_method` / `r_ci_method`
  (`scripts/evaluate_detections.py:214`) and `tile_classification.<metric>.method`
  (`:710-730`). `_metadata.bootstrap.method` (`:539`) is written unconditionally as a
  literal and is not evidence of the path taken

---

### E83: Tier-1 membership was decided by an order-dependent sequential rule, not by the clique its docstring promised — eight boards' tie sets revised to Hsu MCB, including one that published a sole leader it does not have

| Field | Value |
|-------|-------|
| Date | 2026-08-19 |
| Type | Correction (inferential instrument replaced; published tie-set membership changes in both directions) |
| Commit | — (this entry lands with the register revision; the superseded tiering code is retained, see **Protocol impact**) |
| Files | `scripts/n1_baseline_leaderboard_tiering.py:383` (`greedy_clique_tiers`); `results/era1-leaderboard/tiering_20m.json` and two `results/dedup-metric-impact-2026-08-18/tiering-era1-leaderboard-*.json`; eight `tie_set` fields in `results/run-analyses.json`; instruments in `scripts/selection_aware_intervals.py`; audit in `scripts/audit_tier1_cliques.py`; findings in `results/selection-aware/findings.md`; policy in `docs/methodology/inference-instrument-policy.md` |
| Impact | Medium-to-high on claim wording, nil on measurement. No point estimate, F1, MCC, or pairwise p-value changes. What changes is which conditions are published as statistically indistinguishable from the best, on eight of fourteen boards, in both directions — and one board's headline claim of a **sole** leader does not survive |

**Description**: leaderboard tiers are built by `greedy_clique_tiers`, which walks
conditions in F1-descending order and closes the current tier at the **first**
condition that is Benjamini-Hochberg-significant against any current member. Its
docstring states that `tiers[0]` is "the leader's clique (the tie_set)". That is
not what the function computes. Because it closes on first failure, a marginally
significant condition immediately below the leader shuts tier 1 before any
lower-ranked condition is considered, however clearly non-separable that
condition may be.

**The failure is visible on the study's own headline board.** On
`era1-leaderboard` the rank-2 condition is significant at **BH-adjusted
p = 0.048**, and closes tier 1 at a single member. Five lower-ranked conditions
are non-significant against the leader, and — checked pairwise — mutually
non-significant: **all 15 pairs within the leader plus those five are
non-significant**. The leader's actual clique therefore has **six** members,
verified with zero violating pairs. The register published `tie_set` = 1 and an
outcome reading "proposer-verifier is the single best Era-1 architecture ... clear
of the HIGH-consensus cluster (Tier 2)". Neither clause is supported by the
artefact's own pairwise tests.

**The deeper problem, which is why the fix is not a patch.** Tiers built from
pairwise non-significance are not a well-defined object, because non-significance
is not transitive: A indistinguishable from B and B from C does not make A
indistinguishable from C. Every tiering scheme inherits this, clique-based or
sequential, and the order-dependence above is a symptom rather than the disease.
Measured across the boards, the sequential rule is **not biased in one
direction** — against the replacement instrument it runs too narrow on two
boards, too wide on three, identical on one, and on `min-vs-high-thinking-pv`
produces a set that is neither a subset nor a superset (adding one condition
while dropping two). No uniform adjustment can repair that.

**Resolution**: `tie_set` is now the **Hsu multiple-comparisons-with-the-best
(MCB) admissible set** at simultaneous 95 % confidence — the conditions that
cannot be ruled out as *the* best. MCB is the canonical instrument for that
question, is simultaneous by construction rather than by correction, and does not
condition on the empirical winner, which is itself a noisy draw. The critical
value is obtained by tile-level bootstrap rather than from Dunnett's table,
because Dunnett assumes normal homoscedastic means and the statistics here are
micro-F1 and tile-MCC over correlated tiles.

| Board | Metric | Candidates | Published `tie_set` | Revised (Hsu MCB) |
|---|---|---:|---:|---:|
| `era1-leaderboard` | F1 | 82 | **1** | **10** |
| `era1-single-pass-baseline-matrix` | F1 | 36 | 20 | 15 |
| `h12-v2-hp-hn-ratio` | F1 | 6 | 3 | 6 |
| `pass-budget-pareto` | F1 | 5 | 5 | 3 |
| `pass-budget-pareto-v2` | F1 | 7 | 7 | 6 |
| `min-vs-high-thinking-pv` | F1 | 7 | 6 | 5 |
| `flash35-model-roles` | F1 | 5 | 2 | 3 |
| `verifier-robustness-matrix` | F1 | 6 | 5 | 5 |

| `n1-baseline-matrix-384` | F1 | 18 | 2 | 4 |
| `diversity-dividend-384` | F1 | 22 | 3 | 3 |

**All fourteen boards are now on the MCB instrument: ten revised, four confirmed
unchanged.** The first attempt could revise only eight.
`n1-baseline-matrix-384` and `diversity-dividend-384` failed because 18 of their
cells were scored through `--batch`, where `cli_args` records the batch-level
invocation and leaves `detections` and `detections_dir` null while the per-cell
input sits in `_metadata.input_files.detections`. That was a loader gap, not a
data loss (defect D22): an additive fallback recovers all 18, each reproducing
its committed evaluation F1 to within 0.0005, and both boards are now revised.

The last four are the 55-map boards (`55map-canonical-leaderboard-50m`, `55map-standardised-leaderboard-50m`
and their MCC siblings). Their ground truth was a composite of an adjudication
CSV and a reviewed GeoJSON rather than a single loadable reference, so
`evaluate_detections.py --ground-truth`, which takes one path, could not score
them at all.

**That blocker is now removed**, though the boards are not yet re-tiered.
`scripts/materialise_best_available_gt.py` merges the two standardised layers
into one artefact — `inputs/vectors/references/best-available-gt-55maps.{geojson,csv}`,
**5,010 records** (4,731 standardised student + 279 confirmed extension), in
EPSG:32635, with per-record `layer`, `confidence_grade`, `position_source` and
`provenance` retained. It is buffer-invariant, because the standardised layers
are marked centres with no ring gate, which is what makes a single static
reference possible where the earlier per-buffer-gated extended GT did not.

It remains a **best-possible reference, not a gold standard** (ruling 21b): mounds
that both the students and every model missed are absent, and the two-directional
biases documented in the source README apply unchanged.

**Those four are now re-tiered.** Each was scored at its own 50 m buffer against
the matching materialised reference, every cell reproducing its committed F1 to
0.0000, and **all four return a tie set identical to the published one** (2, 1, 2
and 1 members respectively). The sequential rule and MCB agree here, so no 55-map
claim changes — including the two MCC boards' *sole* Tier-1 cell, which survives
the simultaneous procedure where `era1-leaderboard`'s sole-leader claim did not.

Reaching them required three further fixes, each a loader gap rather than a data
problem: adapter-written evaluations carry no `cli_args` at all (they were not
produced by `evaluate_detections.py`); `tile_classification.mcc` has two committed
shapes, a block from the scorer and a bare float from the adapters; and the
reproduction gate read a fixed 20 m buffer, which on a 50 m board compared the
recomputation against a different quantity and turned the gate into noise. All
three are fixed and the buffer is now an explicit parameter.

**Tiers below the first are retained**, on the Principal Investigator's direction
(2026-08-19), because showing what did not work is part of the result. They are
relabelled **descriptive rank bands**: orderings by point estimate that carry no
claim of statistical separation. Only the first group changes status, from an
inferential tier to the MCB admissible set.

**Tile-level MCC** was computed alongside F1 wherever the inputs support it. The
derivation reproduces a committed `tile_classification` block exactly — confusion
counts and MCC alike — before being used, and drops the thirteen conditions whose
MCC is undefined rather than reading them as `0.0` (erratum E81).

**Protocol impact**: no registered hypothesis outcome changes, because no
hypothesis is stated in terms of tier membership. Decision 10's significance rule
is untouched: it is defined on a difference interval, and the pairwise tests
underlying every board are unchanged. What must change is paper wording anywhere
a sole leader, a tier boundary, or an architecture ranking is asserted; those
sentences are flagged in `docs/paper/results-draft.md` for revision rather than
rewritten here, since the Results prose is still gated on the Discussion outline.
The superseded `greedy_clique_tiers` is retained rather than deleted so the
published boards remain reproducible as published.

**Reference artefacts**:

- Defect record: `reports/defect-register-2026-08-18.md` D20
- Instruments and measured comparison: `results/selection-aware/findings.md`;
  `scripts/selection_aware_intervals.py`
- Clique audit across every tiering artefact: `scripts/audit_tier1_cliques.py`;
  `results/selection-aware/tier1-clique-audit.json`
- Reporting policy: `docs/methodology/inference-instrument-policy.md`
- Method: Hsu (1984), *Annals of Statistics* 12(3); Edwards & Hsu (1983)

---
