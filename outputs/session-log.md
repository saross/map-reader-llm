# Execution Session Log

Working notebook recording session summaries from the VLM burial mound detection study. Each entry captures accomplishments, results, issues encountered, and next steps — serving as both a handoff document between sessions and an audit trail of execution decisions.

**Convention**: Sessions are numbered sequentially. Each session includes an overview, key results (if any), issues found, and pending work. Earlier sessions (pre-log) are reconstructed from commit history and archived transcripts.

---

## Session 4 — 2026-02-01 (Phase 1 planning and pre-execution fixes)

### Overview

Preregistration was submitted to OSF in the previous session. This session reviewed the execution plan and preregistration documents, identified pre-execution issues, and prepared the pipeline for Phase 1 (Library Construction). Created the protocol errata tracking system.

### Accomplishments

1. **Reviewed preregistration and execution plan** — identified that Phase 1 is 100 API calls (20 tiles x 5 passes, ~$0.30), well within rate limits
2. **Found and fixed missing config fields** (E2) — `library_pure-positive-canon.json` lacked 5 fields required by the batch script (`model`, `temperature`, `instruction_file`, `thinking_level`, `max_output_tokens`)
3. **Created protocol errata document** — `docs/methodology/preregistration/protocol-errata.md` with entries E1 (stale date) and E2 (missing config fields)
4. **Updated execution checklist** with cross-references to errata
5. **Ran preflight check and dry run** — all 18 checks passed

### Issues

- Config incompleteness (E2) would have crashed the script or produced non-preregistered results (temperature 0.1 instead of 1.0)
- Venv Python required (system Python lacks dotenv)

### Pending Work

- Execute Phase 1 (5 detection passes)
- Sanity check outputs
- Migrate `scripts/5_verify_crops.py` to new SDK

---

## Session 5 — 2026-02-01 (Phase 1 execution and pipeline bug fixing)

### Overview

Executed Phase 1 Library Construction: 5 detection passes on 20 calibration tiles using Gemini 3 Flash with the image-only baseline configuration. The initial run failed completely due to the deprecated SDK lacking ThinkingConfig support. After migrating the SDK, all 5 passes completed successfully but the evaluation pipeline had multiple pre-existing bugs that produced misleading near-zero F1 scores. After fixing all bugs, the true baseline F1 was 0.489 at vote threshold 3 — consistent with expectations for a minimal image-only baseline.

### Phase 1 Results

| Metric | Value |
|--------|-------|
| Passes completed | 5/5 |
| Tiles per pass | 20 |
| API calls | 100 |
| Total cost | $0.096 |
| Detections per pass | 50-62 |
| Merged detections | 128 (all votes) |

#### F1 by Vote Threshold

| Threshold | Detections | TP | FP | FN | Precision | Recall | F1 |
|-----------|-----------|----|----|----|----|--------|-----|
| 1 | 128 | 30 | 98 | 20 | 0.234 | 0.600 | 0.337 |
| 2 | 62 | 26 | 36 | 24 | 0.419 | 0.520 | 0.464 |
| **3** | **40** | **22** | **18** | **28** | **0.550** | **0.440** | **0.489** |
| 4 | 25 | 16 | 9 | 34 | 0.640 | 0.320 | 0.427 |
| 5 | 17 | 11 | 6 | 39 | 0.647 | 0.220 | 0.328 |

**Interpretation**: The F1 of 0.489 at threshold 3 is expected for the minimal image-only baseline (canonical positives + null tiles only, no hard examples or text guidance). The pilot study that achieved F1 ~0.80-0.86 used richer prompt configurations. The systematic failures identified here (18 FPs, 28 FNs at threshold 3) are exactly what Phase 1 needs for hard example selection.

#### Spatial Tolerance Sensitivity (Vote Threshold 3)

| Tolerance | TP | FP | FN | Precision | Recall | F1 | ΔF1 from 20m |
|-----------|----|----|----|----|--------|-----|------|
| 10m | 10 | 30 | 40 | 0.250 | 0.200 | 0.222 | −0.267 |
| **20m** | **22** | **18** | **28** | **0.550** | **0.440** | **0.489** | **—** |
| 30m | 26 | 14 | 24 | 0.650 | 0.520 | 0.578 | +0.089 |
| 40m | 30 | 10 | 20 | 0.750 | 0.600 | 0.667 | +0.178 |
| 50m | 30 | 10 | 20 | 0.750 | 0.600 | 0.667 | +0.178 |

**Key finding**: Loosening from 20m to 50m reclassifies 8 FPs as TPs and resolves 8 FNs, raising F1 from 0.489 to 0.667. The 40m and 50m rows are identical, confirming all localisation failures cluster within 40m. Of the 28 FNs at 20m tolerance, 8 (29%) are localisation failures rather than recognition failures — the model detected something nearby but placed it too imprecisely to match. See `fp-fn-register.md` and Observation 76 in working notes for the full two-dimensional ranking framework.

### Bugs Found and Fixed (E3-E5)

Five distinct infrastructure bugs were exposed during execution, each individually minor but chaining together to produce misleading results:

1. **E3 — SDK migration** (`4_detect_mounds_batch.py`): The deprecated `google-generativeai` SDK (v0.8.6) doesn't support `ThinkingConfig`. All 100 API calls failed silently with `Unknown field for GenerationConfig: thinkingLevel`. Migrated to `google-genai` SDK (v1.56.0). Also added model name resolution (`gemini-3-flash` → `gemini-3-flash-preview`).

2. **E4 — Tile bounds Y-axis inversion** (`generate_tile_bounds.py`): Metadata format is `[minX, minY, ...]` but the script treated `metadata[1]` as `maxY`. This shifted all tile bounds ~2565m south, causing the evaluation to scope references to entirely wrong spatial areas.

3. **E5a — Reference path** (`lib_advanced_metrics.py`, `analyse_study_effects.py`): `load_data()` looked for references in `inputs/vectors/` but they are in `inputs/vectors/references/`. Silently returned `None` instead of failing loudly.

4. **E5b — Column name mismatch** (`6_accuracy_report.py`): Merged GeoJSON uses `source_tiles` (list) but evaluation expected `source_tile` (string).

5. **Orchestrator args** (`run_phase1.py`): Passed `--tolerance 20.0` and `--passes 5` to `merge_passes.py`, but neither argument exists (tolerance is hardcoded; `--passes` expects comma-separated numbers).

**Propagation pattern**: Each stage quietly accepted bad input — the deprecated SDK reported "0 detections" (not an error), wrong bounds scoped wrong references, missing references returned `None` silently. Only the column name crash was loud. See Observation 66 in working notes.

### Commits

| Hash | Description |
|------|-------------|
| `e168410` | `refactor(detection)`: Migrate batch script to google-genai SDK |
| `b2f693c` | `fix(orchestrator)`: Remove invalid merge script arguments |
| `49184be` | `fix(bounds)`: Correct Y-axis inversion in tile bounds generation |
| `67e4b92` | `fix(evaluation)`: Correct reference path and source_tile handling |
| `92d3a95` | `data(phase1)`: Add Phase 1 detection results |
| `85dc0d2` | `docs(preregistration)`: Record E3-E5 errata |
| `1bd757f` | `docs(notes)`: Add Observation 66 on silent pipeline failures |

### Pending Work

- [ ] **Failure analysis**: Review the 18 FPs and 28 FNs to select hard examples for the library
- [ ] **Hard example crops**: Extract 512x512 context crops using `analyse_fp_crops.py`
- [ ] **Text description updates**: Add hard example descriptions to instruction files (`detect_brief-text.md`, `detect_verbose-text.md`)
- [ ] **Config updates**: Add hard example paths to Scale-8+ library configs
- [ ] **SDK migration**: `scripts/5_verify_crops.py` still uses the deprecated `google-generativeai` SDK
- [ ] **Upload to OSF**: Library construction results should be uploaded before holdout evaluation

---

## Session 5b — 2026-02-01 (Reflection, contract validation, and protocol)

### Overview

Continuation of Session 5 after context compaction. Completed the end-of-session reflection that Session 5 ran out of context to finish, then implemented pipeline contract validation to prevent recurrence of the E3-E5 bugs before Phase 2. Codified the end-of-session reflection protocol in CLAUDE.md.

### Accomplishments

1. **Completed Session 5 reflections** — added observations to `llm-observations.md` (Session 5 section with 6 observations), `session-reflection-investigation.md` (second entry), and `abductive-reasoning-investigation.md` (debugging cycles as new abductive reasoning data)
2. **Implemented pipeline contract validation (E6)** — three categories of hardening:
   - Reference loading assertion in `lib_advanced_metrics.py` and `6_accuracy_report.py`
   - Bounds metadata validation in `generate_tile_bounds.py`
   - 7 new integration tests in `test_integration_pipeline_contracts.py`
3. **Updated protocol errata** — E6 entry documenting the contract validation additions
4. **Codified end-of-session protocol** — added reflection protocol to project CLAUDE.md pointing at the four reflection/observation documents

### Tests

| Suite | Result |
|-------|--------|
| Full test suite | 267 passed (260 existing + 7 new) |
| New contract tests | 7/7 passed in 0.17s |
| Regressions | None |

### Pending Work

- [ ] **Failure analysis**: Review the 18 FPs and 28 FNs to select hard examples for the library
- [ ] **Hard example crops**: Extract 512x512 context crops using `analyse_fp_crops.py`
- [ ] **Text description updates**: Add hard example descriptions to instruction files (`detect_brief-text.md`, `detect_verbose-text.md`)
- [ ] **Config updates**: Add hard example paths to Scale-8+ library configs
- [ ] **SDK migration**: `scripts/5_verify_crops.py` still uses the deprecated `google-generativeai` SDK
- [ ] **Upload to OSF**: Library construction results should be uploaded before holdout evaluation

---

## Session 6 — 2026-02-01 (Failure analysis, hard example selection, and boundary-effect discovery)

### Overview

Completed Phase 1 failure analysis: built a comprehensive FP/FN register with a two-dimensional ranking framework (frequency × localisation accuracy), computed spatial tolerance sensitivity curves, selected hard examples, and extracted 512×512 context crops. During visual inspection of the hard positive crops, discovered that 3 of 4 selected FN reference points fall outside all calibration tiles — a boundary-effect artefact in the evaluation scoping, not genuine recognition failures. Hard negative selection (FPs) is confirmed good; hard positive selection needs revision next session after fixing the evaluation scoping.

### Key Results

#### Spatial Tolerance Sensitivity (Vote Threshold 3)

| Tolerance | TP | FP | FN | Precision | Recall | F1 |
|-----------|----|----|----|----|--------|-----|
| 20m | 22 | 18 | 28 | 0.550 | 0.440 | 0.489 |
| 40m | 30 | 10 | 20 | 0.750 | 0.600 | 0.667 |
| 50m | 30 | 10 | 20 | 0.750 | 0.600 | 0.667 |

At 5.01 m/px: 20m = 4 pixels, 40m = 8 pixels, 50m = 10 pixels. The 40m and 50m rows are identical, confirming all localisation failures cluster within 40m.

#### Two-Dimensional Failure Ranking

FNs split into recognition failures (9, >50m from any detection) and localisation failures (15, 20-50m). FPs classified as hallucinations (>500m from reference), moderate, marginal, or near-misses. 63% of FNs are localisation failures rather than recognition failures. See Observation 76.

#### Hard Example Selection

**Hard negatives (confirmed good)**: 4 vote-5/5 hallucinations, one per sheet:

| Example | Subtype | Map | Nearest Ref. |
|---------|---------|-----|-------------|
| 11 | burial_mound | Rakovski | 1896.0m |
| 12 | triangulation_mound | Lesovo | 1807.8m |
| 13 | burial_mound | K-35-052-4 | 872.9m |
| 14 | burial_mound | Elenovo | 725.0m |

**Hard positives (3 of 4 need replacement)**: Visual inspection revealed no mound symbols at the reference coordinates for examples 05-07. These FNs are boundary-effect artefacts — reference points that passed the evaluation scope check but fell outside all calibration tiles shown to the model. Example 08 (fid 105, Elenovo) is confirmed with a visible mound at the bottom-right edge.

### Boundary-Effect Issue (E7 — pending)

The evaluation pipeline scopes references using `intersects(union_of_tile_polygons)` per map sheet. With only 5 scattered calibration tiles per sheet (out of 90), there are large gaps. Reference mounds near tile edges can pass the union intersection test while falling outside every individual tile. The model never sees these mounds, so counting them as FNs inflates the FN count and deflates F1.

**Fix needed**: Scope references against individual tile polygons (containment), not the union. Recalculate F1 after excluding boundary-effect FNs.

### Accomplishments

1. **Built FP/FN register** (`outputs/phase1-library/fp-fn-register.md`) with two-dimensional ranking
2. **Computed spatial tolerance sensitivity** — F1 rises from 0.489 (20m) to 0.667 (40m/50m)
3. **Recorded Observation 76** on frequency × localisation ranking framework
4. **Extracted 8 hard example crops** (4 HP, 4 HN) with neutral-naming symlinks
5. **Updated Decision 4** in decisions-log with full selection rationale and provenance
6. **Marked hard example checklist item complete** in execution-checklist
7. **Verified library configs** — all 5 active configs (pure-positive-canon through scale-8) resolve correctly
8. **Discovered boundary-effect FN inflation** during visual inspection of hard positive crops

### Commits

| Hash | Description |
|------|-------------|
| `bc7ace1` | `data(phase1)`: Add FP/FN register with two-dimensional ranking |
| `64cf830` | `docs(notes)`: Add Observation 76 on frequency × localisation ranking |
| `6a12b1e` | `docs(outputs)`: Add spatial tolerance sensitivity to Phase 1 results |
| `12898e9` | `data(library)`: Add hard positive and hard negative examples |
| `6119298` | `docs(preregistration)`: Record hard example selection in Decision 4 |

### Pending Work

- [ ] **E7: Fix evaluation reference scoping** — scope against individual tiles, not union; recalculate F1
- [ ] **Replace hard positives 05-07** — visually confirm mound symbols before selection
- [ ] **Text description updates**: Add hard example descriptions to instruction files
- [ ] **Upload to OSF**: Library construction results before holdout evaluation

---

*New session entries should be appended above this line.*
