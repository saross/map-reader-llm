---
priority: 5
scope: always
title: "Session Log"
audience: "researchers and future instances"
---

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

- [x] **Failure analysis**: Review the 18 FPs and 28 FNs to select hard examples for the library *(completed Session 6)*
- [x] **Hard example crops**: Extract context crops *(completed Session 7 — revised to 128×128 from full GeoTIFFs, see E8)*
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

- [x] **Failure analysis**: Review the 18 FPs and 28 FNs to select hard examples for the library *(completed Session 6)*
- [x] **Hard example crops**: Extract context crops *(completed Session 7 — revised to 128×128 from full GeoTIFFs, see E8)*
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

## Session 7 — 2026-02-02 (Boundary-effect scoping fix, hard positive replacement)

### Overview

Fixed the boundary-effect evaluation reference scoping bug (E7) identified in Session 6: replaced `union_all()` with per-tile `gpd.sjoin()` at three sites in the evaluation pipeline, added 7 new integration tests, and documented the fix in protocol errata. Phase 1 metrics were unchanged (non-adjacent calibration tiles make union equivalent to per-tile scoping), confirming the fix is preventive for Phase 2. Replaced three out-of-scope hard positive examples with genuine recognition failures, prioritising recognition failures over localisation failures based on domain judgement. Determined crop size (128×128) and extraction method (centred from full map GeoTIFFs, not detection tiles — see errata E8). Documented documentation heuristic for decisions-log vs errata vs working-notes vs session-log.

### Accomplishments

1. **Fixed evaluation reference scoping (E7)** — extracted `scope_references_to_tiles()` helper using `gpd.sjoin()`, replacing `union_all()` at three sites: `calculate_f1_internal()`, `error_taxonomy()`, and `validate_file()`
2. **Added 7 boundary-effect tests** — `TestReferenceScoping` class covering: reference inside tile, reference in gap excluded, reference outside excluded, boundary in scope, empty inputs, and F1 impact
3. **Updated `spatial_tolerance_curve()` defaults** — added 40m to buffer list: `[10, 20, 30, 40, 50]`
4. **Documented E7 in protocol errata** — correction type, no impact on Phase 1 results
5. **Diagnosed out-of-scope hard positives** — fids 354, 249, 556 are entirely outside all calibration tile polygons; never contributed to FN count
6. **Replaced hard positives 05-07** with genuine recognition failures:
   - example_05: fid 399 (Rakovski, recognition failure 5/5)
   - example_06: fid 99 (Elenovo, recognition failure 4/5)
   - example_07: fid 15 (Rakovski, recognition failure 4/5)
7. **Established ~5px edge clearance rule** — symbols need minimum ~5px from tile edge to be fully visible (fid 161 excluded: ~2/3 truncated at west edge)
8. **Recorded Observations 78-80** — crop size as empirical question (future OFAT experiment), human-AI division of labour in hard example curation, crop extraction decisions
9. **Determined crop size and extraction method** — 128×128 crops centred from full map GeoTIFFs (option c), documented in Decision 4 and errata E8
10. **Established documentation heuristic** — decisions-log for formal choices, errata for deviations, working-notes for observations, session-log for summaries

### Issues

- **Metrics unchanged after E7 fix**: Phase 1's 5 scattered tiles per sheet are non-adjacent, making `union_all()` geometrically equivalent to per-tile scoping. Fix is preventive for Phase 2 (60 tiles, likely adjacent).
- **Hard positive crop size**: Resolved — 128×128 crops extracted from full map GeoTIFFs. See errata E8.
- **One-per-sheet constraint broken**: Rakovski and Elenovo each have 2 hard positives because Lesovo and K-35-052-4 had no recognition failures.

### Tests

| Suite | Result |
|-------|--------|
| Full test suite | 274 passed (267 existing + 7 new) |
| New scoping tests | 7/7 passed |
| Regressions | None |

### Commits

Changes not yet committed at session end. Modified files:

- `scripts/lib_advanced_metrics.py` — `scope_references_to_tiles()`, fixed `calculate_f1_internal()`, `error_taxonomy()`, updated `spatial_tolerance_curve()`
- `scripts/6_accuracy_report.py` — fixed `validate_file()`, added import
- `tests/test_integration_pipeline_contracts.py` — 7 new boundary-effect tests
- `docs/methodology/preregistration/protocol-errata.md` — E7 entry
- `docs/notes/working_notes.md` — Observations 78, 79
- `inputs/examples/hard-positive/` — replaced example_05, 06, 07
- `inputs/examples/neutral-naming/` — updated symlinks

### Pending Work

- [ ] **Commit Session 7 changes** — E7 fix, tests, errata, hard example replacements, reflections, crop extraction
- [x] **Determine crop size** — 128×128 from full GeoTIFFs (errata E8, Decision 4)
- [x] **Update MANIFEST.md** — new hard positive provenance (fids 399, 99, 15)
- [x] **Update Decision 4** — revised selection rationale (recognition-failure prioritisation, broken one-per-sheet, crop extraction)
- [x] **Update FP/FN register** — reflect revised hard positive selection
- [ ] **Pending decision: prompt centring text** — whether to add "target symbols are centred" to text prompt variants (see Observation 80)
- [ ] **Text description updates**: Add hard example descriptions to instruction files (`detect_brief-text.md`, `detect_verbose-text.md`)
- [ ] **Upload to OSF**: Library construction results before holdout evaluation

---

## Session 8 — 2026-02-02 (Session archiving, hard negative re-extraction, file preservation)

### Overview

Archived two unarchived Claude Code sessions with metadata, re-extracted hard negative crops as 128×128 from full map GeoTIFFs (replacing the 512×512 detection-tile crops), and established the archive-not-delete file preservation principle. A short, focused session centred on consistency and housekeeping rather than new analysis.

### Accomplishments

1. **Archived CC sessions** — da3d0331 (Sessions 4-6) and abe6f808 (Session 7) archived with gzip compression, metadata populated with titles, purposes, tags, three_ps, relationships, and artifact descriptions. Backfilled `continuedBy` link in predecessor session f5e8cd4f.
2. **Re-extracted hard negative crops** — 4 crops (examples 11-14) re-extracted as 128×128 from full map GeoTIFFs centred on FP detection coordinates, consistent with the hard positive extraction method from Session 7. Extended errata E8 to cover hard negatives.
3. **Archived superseded crops** — recovered old 512×512 HP and HN crops from git commit `12898e9` and placed in `archive/preliminary-work/references/prompt_example_images/superseded-hard-{positives,negatives}-512x512/` with explanatory READMEs.
4. **Established file preservation principle** — added "Archive, never delete" section to project CLAUDE.md: superseded files must be browsable in the working tree, not just recoverable from git history.
5. **Updated MANIFEST.md** — hard negative section updated with GeoTIFF extraction method, hallucination-prioritisation selection criteria.
6. **Updated protocol errata E8** — expanded from "Hard positive crops" to "Hard example crops" covering both HPs and HNs with unified rationale.
7. **Recorded Observations 81-82** — recognition-vs-localisation distinction transfers to FPs; recoverability vs discoverability in research archives.

### Issues

- **python vs python3**: System `python` not found; needed `python3` throughout.
- **rasterio in venv**: Required `.venv` activation for rasterio-dependent crop extraction.
- **JSONL parsing**: Session archives use `"type": "user"` not `"type": "human"`; piping through zcat failed — resolved via temp file.
- **Files overwritten without archiving**: Replaced old HN crops in place, initially relying on git history. User corrected: archive to working tree for discoverability. Fixed by recovering from git and archiving.

### Commits

No commits made this session. All changes are staged/unstaged modifications spanning Sessions 7-8.

### Pending Work

- [ ] **Commit Sessions 7-8 changes** — E7 fix, tests, hard example replacements/re-extractions, errata, reflections, archive, CLAUDE.md
- [ ] **Text description updates**: Add hard example descriptions to instruction files (`detect_brief-text.md`, `detect_verbose-text.md`)
- [ ] **Pending decision: prompt centring text** — whether to add "target symbols are centred" to text prompt variants (recommended for HPs, not for HNs)
- [ ] **Config updates**: Add hard example paths to Scale-16 and Scale-32 library configs
- [ ] **SDK migration**: `scripts/5_verify_crops.py` still uses deprecated `google-generativeai` SDK
- [ ] **Upload to OSF**: Library construction results before holdout evaluation

---

## Session 9 — 2026-02-02 (Continuation: collaboration scaffolding and SHAWN.md)

### Overview

Short continuation session focused on collaboration meta-work rather than pipeline development. Completed remaining Session 8 reflections (abductive-reasoning-investigation.md and session-log.md), then created SHAWN.md — a counterpart to CLAUDE.md containing suggestions from the AI to the human. Reviewed all four reflection documents to identify additional patterns, expanding SHAWN.md from 3 to 6 suggestions. Elaborated on the four-element correction pattern (negation, grounding, redirection, stakes) at the user's request.

### Accomplishments

1. **Completed Session 8 reflections** — updated abductive-reasoning-investigation.md (Session 8 note on default assumptions as abduction blockers) and session-log.md (Session 8 entry)
2. **Created SHAWN.md** — 6 suggestions for the human collaborator based on patterns from reflection documents:
   - State expectations before results arrive
   - Ask "what assumptions are you making?" at action points
   - Flag when a "setup" task is actually a research task
   - Ask "have you looked at it?" for spatial/visual outputs
   - Ask for options rather than accepting a default
   - Your correction style works — keep the "why" even when rushed
3. **Recorded Observations 83-84** — bidirectional collaboration scaffolding; parallel default-following in human and AI collaborators
4. **Updated all reflection documents** — llm-observations.md (Session 9 section), session-reflection-investigation.md (Entry 5), working_notes.md (Observations 83-84)

### Issues

None. No code or data work this session.

### Commits

No commits made. Pending work unchanged from Session 8 plus SHAWN.md and new reflection content.

### Pending Work

- [ ] **Commit Sessions 7-9 changes** — E7 fix, tests, hard example replacements/re-extractions, errata, reflections, archive, CLAUDE.md, SHAWN.md
- [ ] **Text description updates**: Add hard example descriptions to instruction files (`detect_brief-text.md`, `detect_verbose-text.md`)
- [ ] **Pending decision: prompt centring text** — whether to add "target symbols are centred" to text prompt variants (recommended for HPs, not for HNs)
- [ ] **Config updates**: Add hard example paths to Scale-16 and Scale-32 library configs
- [ ] **SDK migration**: `scripts/5_verify_crops.py` still uses deprecated `google-generativeai` SDK
- [ ] **Upload to OSF**: Library construction results before holdout evaluation

---

## Session 10 — 2026-02-02 (H9 pool correction, centre-pointing language, errata, and commit backlog)

### Overview

Continuation session implementing decisions from the Opus strategic review (`planning/hard-example-library-decisions.md`). Revised centre-pointing language across all 11 detection prompt files, wrote 5 new protocol errata entries (E9-E13), corrected a fundamental error in H9 diversity rotation pool sizing (4 HN crops → 16 via 12 new extractions), and pushed the accumulated commit backlog from Sessions 7-10 as 9 logical commits. The H9 pool size error — where 4 HN crops filling 4 slots per pass yields zero diversity — was the session's most consequential correction, identified by Opus via the user.

### Accomplishments

1. **Revised centre-pointing language (E9)** — replaced "centred on the relevant feature" with "centred on the feature being labelled — the target symbol for Positive examples, the confusable feature for Negative examples" across all 11 `detect_*.md` files. Applied uniformly including image-only condition to preserve H5 factor orthogonality.
2. **Wrote protocol errata E9-E13** — E9 (centre-pointing language, clarification), E10 (50m threshold activation, clarification), E11 (Scale-16/32 capping, clarification), E12 (H9 frozen HP, clarification), E13 (H12 deferral, deviation).
3. **Corrected H9 HN pool size** — identified that 4 HN crops in 4 slots = C(4,4) = 1 combination = zero diversity. Extracted 12 new HN crops (examples 18-29) from FP GeoJSON using the preregistered two-dimensional ranking (vote count desc, distance desc, >50m filter). Total pool now 16 HN crops.
4. **Created neutral-naming symlinks** for examples 18-29.
5. **Updated MANIFEST.md** — added "Expanded Hard Negative Pool (Examples 18-29)" section with full provenance table, pool composition summaries, H9 diversity rotation documentation.
6. **Committed and pushed Sessions 7-10 changes** — 9 logical commits covering: pipeline fixes, hard example data, expanded HN pool, prompt revisions, config/planning updates, preregistration decisions and errata, outputs/session log, observation notes, and session archives.

### Issues

- **H9 pool size miscalculation**: The most significant error. Passed through CC analysis, Explore agent verification, and planning document review without being caught. Identified by Opus (web chatbot) via the user. Root cause: treating "enough for the library" as equivalent to "enough for the experiment."
- **MultiPoint geometry in reference GeoJSON**: The extraction script initially failed because `mounds-reference.geojson` contains MultiPoint geometries. Fixed by handling both Point and MultiPoint types in the distance computation.
- **Edit tool sequencing**: Attempted to edit 10 of 11 prompt files before reading them. Required reading all files first, then editing in parallel.

### Commits

9 logical commits pushed covering Sessions 7-10 (exact hashes available in `git log`):

| Scope | Description |
|-------|-------------|
| `fix(pipeline)` | Harden evaluation reference scoping and contracts |
| `data(library)` | Re-extract hard examples as 128×128 GeoTIFF crops |
| `data(library)` | Add expanded HN pool for H9 diversity rotation |
| `feat(prompts)` | Add centre-pointing language for label disambiguation |
| `chore(configs)` | Mark Scale-16/32 deferred, add planning synopsis |
| `docs(preregistration)` | Record Decisions 11-12 and errata E9-E13 |
| `docs(outputs)` | Update FP-FN register and session log |
| `docs(notes)` | Add Sessions 7-8 observations and reflections |
| `chore(archive)` | Add Sessions 6-7 archives |

### Pending Work

- [ ] **Text description updates**: Add hard example descriptions to `detect_brief-text.md` and `detect_verbose-text.md`
- [ ] **Config updates**: Wire expanded HN pool into H9 rotation configs
- [ ] **H9 assignment algorithm**: Implement the HN rotation assignment satisfying frequency constraints (each HN in ≥1 and ≤3 of 5 passes)
- [ ] **SDK migration**: `scripts/5_verify_crops.py` still uses deprecated `google-generativeai` SDK
- [ ] **Upload to OSF**: Library construction results before holdout evaluation
- [ ] **Remaining Phase 2 readiness items** (item d from strategic review)

---

## Session 11 — 2026-02-03 (Prompt text refinement from hard example library)

### Overview

Reviewed and iteratively refined prompt text derived from the hard example library (HP 05-08, HN 11-14). Established two governing principles: (1) describe visual appearance, not map symbology identity; (2) use only diagnostics reliable at VLM exemplar resolution (128×128px). Produced four categories of text changes across brief/terse/verbose prompt levels, a diagnostic reliability table (Decision 13), and a synopsis document for external Opus review. The session was characterised by complementary human-AI contributions: the user provided domain-grounded corrections from manual map review, while CC contributed VLM-perspective analysis identifying which diagnostics survive resolution reduction.

### Key Results

#### Governing Principles Established

1. **Descriptive principle**: Prompt text describes what the VLM will see (colours, shapes, spatial relationships), not what map features are (grid lines, buildings, canals). Matches the register used for the target symbol itself ("sunburst with outward-radiating rays").

2. **VLM-calibrated diagnostics**: Only diagnostics reliable at 128×128px exemplar resolution are used. Fine detail visible to humans (solid fill, hollow centre, precise outlines, half-coloured patterns) is excluded. Resolution-robust diagnostics (ray presence/absence, direction, colour composition) are retained. See Decision 13 for the full reliability table.

#### Four Change Categories

| Change | Source | Scope | Summary |
|--------|--------|-------|---------|
| 1: Occlusion guidance | HP 07 | Brief (Guideline 2) + Verbose (3 edits) | Replaced interpretive feature names with colour/shape descriptions; added interference range and reconstruction guidance |
| 2A: Inward-pointing marks | HN 13 | Terse (bullet) + Verbose (subsection) | Rewrote quarry/pit exclusion with descriptive language; added colour note |
| 2B: Cyrillic text | HN 13 | Terse (bullet) + Verbose (subsection) | New exclusion for 'могила'/'кург.' text without accompanying sunburst |
| 3: Non-mound round shapes | HN 11, HN 14 | Terse (bullet) + Verbose (subsection) | Catch-all for confusable round shapes using VLM-calibrated diagnostics |
| 4A: Enhanced clustering | HP 05, HP 06, HP 08 | Verbose only | "If you find one, look nearby" guidance addressing VLM satisficing |
| 4B: Dense features | HP 05, HP 06 | Verbose only | Apply ray diagnostic regardless of surrounding visual complexity |

### Accomplishments

1. **Iteratively refined 4 categories of prompt text changes** across brief/terse/verbose levels following both governing principles
2. **Produced VLM diagnostic reliability table** — systematic comparison of human vs VLM perception at 128px, documenting which diagnostics are resolution-robust (Decision 13)
3. **Recorded Observation 87** — human-VLM complementary perception finding and crop-size interaction implications
4. **Wrote synopsis for Opus review** — `planning/prompt-text-review-synopsis.md` covering principles, changes, open items
5. **Identified and applied descriptive principle** retroactively to pre-existing interpretive text ("grid lines (blue)" → descriptive language)
6. **Consolidated redundant subsections** after Opus flagged overlap between two Change 1 verbose edits

### Issues

- **Interpretive overreach in initial drafts**: All initial prompt text used interpretive language ("grid lines," "buildings," "quarry/pit symbols") rather than descriptive language. Required systematic correction after the user established the descriptive principle.
- **Human-VLM perception mismatch**: User's manual crop review identified fine detail (solid fill, black outline, two black dots, half-coloured patterns) that CC could not resolve at 128px. Required recalibrating all diagnostics to VLM-resolution-robust alternatives.
- **Context exhaustion**: Session ran out of context during end-of-session reflections. Continuation session completed the reflections.

### Open Items

- **Marks vs rays terminology**: Intentional lexical distinction ("rays" for outward, "marks" for inward) under review. User checking whether "inward-pointing rays or other marks" better covers the range.
- **Opus review pending**: User will share `planning/prompt-text-review-synopsis.md` with Opus at claude.ai for external assessment.

### Commits

No commits this session. All prompt text changes exist as proposed text in the conversation, pending:
1. User's manual review completion
2. Opus review feedback
3. Implementation across 10 prompt files

### Pending Work

- [ ] **Implement prompt text changes** across 10 `detect_*.md` files (after user + Opus review)
- [ ] **Resolve marks vs rays terminology** (user's manual map review)
- [ ] **Incorporate Opus review feedback** from synopsis review
- [ ] **Config updates**: Wire expanded HN pool into H9 rotation configs
- [ ] **H9 assignment algorithm**: Implement HN rotation assignment
- [ ] **SDK migration**: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] **Upload to OSF**: Library construction results before holdout evaluation

---

## Session 12 — 2026-02-03 (Prompt text implementation + status review)

### Overview

Implemented the prompt text changes designed in Session 11 and refined via Opus review. Applied Changes 1–4 plus Opus Priorities 1–5 across 12 of 13 prompt files and 2 two-stage prompts, following the detailed plan in `planning/parsed-questing-pancake.md`. Archived superseded planning documents. Produced a project status briefing confirming Phase 2a readiness (pending only `GOOGLE_API_KEY`).

### Accomplishments

1. **Implemented prompt text changes across 12 files** — 6 editing passes: verbose shared content (4 files), terse exclusion (3 files), verbose exclusion (3 files), brief guidelines (4 files), two-stage prompts (2 files), no-change verification (1 file)
2. **Verified all consistency constraints** — diff checks on file pairs (all passed), terminology audit (no "inward rays" or interpretive feature names), Guideline 2 consistency across 5 files, word count ratio 1:3.6 (target ~1:3)
3. **Archived 3 superseded planning files** to `archive/planning/hard-example-review/`: `combined-prompt-review-feedback.md`, `prompt-text-review-synopsis.md`, `hard-example-library-decisions.md`
4. **Produced Phase 2 status briefing** — Phase 1 complete, infrastructure ready, Phase 2a can begin when API key is configured
5. **End-of-session reflections** — Entry 10 in session-reflection-investigation.md, Session 12 in llm-observations.md, Observation 88 in working_notes.md

### Issues

- **Untracked file archiving**: `combined-prompt-review-feedback.md` was never committed, so `git mv` failed. Used plain `mv` + `git add` instead.
- **107 pre-existing markdownlint errors**: Found across all prompt files. Not fixed per CLAUDE.md policy (keep content changes reviewable; fix lint when touching files substantively).
- **Context exhaustion**: Original instance ran out of context during reflections. Continuation session completed them. See llm-observations.md Session 12 entry for methodological implications.

### Commits

1. `2d46311` — `feat(prompts): Apply hard-example prompt text changes 1–4`
2. `5e7601d` — `feat(prompts): Update two-stage prompts per Opus review`
3. `b7d7238` — `chore(planning): Archive superseded hard-example review docs`

### Pending Work

- [x] ~~Implement prompt text changes~~ (this session)
- [x] ~~Incorporate Opus review feedback~~ (this session)
- [x] ~~Resolve marks vs rays terminology~~ (resolved in plan: "rays" outward, "marks" inward)
- [ ] **Config updates**: Wire expanded HN pool into H9 rotation configs
- [ ] **H9 assignment algorithm**: Implement HN rotation assignment
- [ ] **SDK migration**: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] **Upload to OSF**: Library construction results before holdout evaluation
- [ ] **Set `GOOGLE_API_KEY`**: Required for Phase 2a execution
- [ ] **Fix markdownlint errors**: 107 pre-existing formatting issues across prompt files

---

## Session 13 — 2026-02-03 (Reflection skill creation + CLAUDE.md streamlining)

### Overview

Short session continuing from Session 12's context exhaustion. Completed Session 12 reflections, discussed Claude Code features for context management (hooks, `/compact`, `/context`), created the `/reflect` skill to encapsulate the end-of-session reflection protocol, and streamlined CLAUDE.md by replacing the detailed protocol section with a skill pointer. First test of the `/reflect` skill on this session.

### Accomplishments

1. **Completed Session 12 reflections** — Entry 10 in session-reflection-investigation.md, Session 12 in llm-observations.md, Observation 88 in working_notes.md (from continuation instance)
2. **Researched CC context management features** — hooks (PreCompact, SessionStart), `/compact`, `/context` commands; concluded hooks don't solve the core initiation friction problem
3. **Created `/reflect` skill** — `.claude/skills/reflect/SKILL.md` encapsulating the full reflection protocol (5 documents, 6 prompts, priority ordering, format requirements, instance boundary guidance)
4. **Streamlined CLAUDE.md** — Replaced 25-line reflection protocol section with 3-line pointer to the skill
5. **First `/reflect` test** — This session's reflections produced via the skill invocation

### Issues

- **YAML validator rejected `>-` fold indicator** as "angle bracket" — required switching to quoted string format in SKILL.md frontmatter
- **Short session provided thin material for reflections** — but serves as a useful baseline test of the skill on a low-content session

### Commits

1. `4f2800c` — `docs(notes): Add Session 12 reflections across four documents`
2. `8bebf51` — `feat: Add /reflect skill and streamline CLAUDE.md`

### Pending Work

- [ ] **Config updates**: Wire expanded HN pool into H9 rotation configs
- [ ] **H9 assignment algorithm**: Implement HN rotation assignment
- [ ] **SDK migration**: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] **Upload to OSF**: Library construction results before holdout evaluation
- [ ] **Set `GOOGLE_API_KEY`**: Required for Phase 2a execution
- [ ] **Fix markdownlint errors**: 107 pre-existing formatting issues across prompt files
- [ ] **Iterate on `/reflect` skill** based on test results and future usage

---

## Session 14 — 2026-02-04 (Pre-Phase 2 bookkeeping and prompt restructuring)

### Overview

Final housekeeping session before Phase 2a execution. Recovered a compact pre-Phase 2 task list from the session transcript after accidental `/clear`, completed all four items: updated execution checklist (Phase 1 complete), ticked pre-Phase 2 prerequisites, confirmed API key availability, and restructured the Decision Procedure in verbose instruction files per Opus review feedback. Added E14 erratum noting verbose word count overshoot. Ran word count pass across all instruction files.

### Accomplishments

1. **Recovered pre-Phase 2 task list** from session transcript JSONL after accidental `/clear` — the compact 4-item status briefing from the previous portion of the session
2. **Updated execution checklist** (`execution-checklist.md`) — Phase 1 end date set to 2026-02-03, notes updated to reflect hard example selection and two-stage prompt review
3. **Ticked pre-Phase 2 prerequisites** (`phase2-remaining-tasks.md`) — all four items marked ☑ Done with dates and resolution notes; status updated to "Phase 1 complete; prerequisites resolved"
4. **Confirmed `GOOGLE_API_KEY`** present in `.env` and properly loaded via `config.py` → `load_dotenv()` across all active scripts (`4_detect_mounds_batch.py`, `5_verify_crops.py`, `preflight_check.py`)
5. **Restructured Decision Procedure** in 4 verbose instruction files per Opus review — reordered into Phase 1 (identify sunburst: rays, direction, occlusion, degradation) then Phase 2 (classify subtype: shape, colour)
6. **Ran word count pass** across all 11 instruction files — M/E scaling ratios consistent (image-only 91 → brief 213 → verbose 779 words)
7. **Added E14 erratum** noting verbose instruction word count exceeds target by ~80 words (ratio 1:3.7 vs preregistered ~1:3); documented as conservative deviation

### Issues

- **Glob tool missed `.env`**: Dotfile filtering meant `Glob("**/.env")` returned no results, though `ls` confirmed the file exists. Bash `grep -rl` found it.

### Commits

| Hash | Description |
|------|-------------|
| `e610b6f` | `chore(docs)`: Mark Phase 1 complete and tick pre-Phase 2 prerequisites |
| `52d54e9` | `feat(prompts)`: Reorder Decision Procedure for detect-before-classify |
| `7028e90` | `docs(errata)`: E14 — verbose instruction word count exceeds target |

### Pending Work

- [ ] **Compose OSF submission document**: Consolidate all errata (E1-E14), decisions, and protocol changes into a single paste-ready Markdown document for OSF open-ended registration update
- [ ] **Config updates**: Wire expanded HN pool into H9 rotation configs
- [ ] **H9 assignment algorithm**: Implement HN rotation assignment
- [ ] **SDK migration**: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] **Upload Phase 1 materials to OSF**: Library construction results
- [ ] **Fix markdownlint errors**: 107 pre-existing formatting issues across prompt files
- [ ] **Begin Phase 2a execution**: H1 M/E level testing

## Session 15 — 2026-02-04 (OSF preregistration update and errata consolidation)

### Overview

Produced a consolidated errata/decisions document for the OSF open-ended preregistration update. The user's critical reading of the draft revealed three issues requiring corrections: K=10 vs K=5 pass count inconsistency, over-generalised FN miss rate claim, and undocumented visual-description prompt principle. Added errata E15–E16 and Decision 14. Uploaded five supporting files to OSF. Archived OSF description and narrative summary locally.

### Accomplishments

1. **Produced consolidated OSF update document** (`osf/phase1-errata-and-decisions.md`) — condensed summaries of 16 errata and 5 post-preregistration decisions, with references to detailed source files
2. **Corrected K=10 → K=5 in Decision 4** — discovered internal inconsistency in preregistration appendix (stale "≥3/10" in lines 115 and 1694 vs operative "K=5" in lines 98–99); added E15 documenting the inconsistency
3. **Qualified "all 24 FNs were 0/5" claim** — narrowed to "all 9 recognition failures were complete misses"; localisation failures not individually verified per-pass
4. **Added concrete numbers to distributional cliff description** — 15 of 24 FNs in 20–50 m band, 9 scattered from 50–2450 m
5. **Added Decision 14** (visual appearance over cartographic identity) — distinct from Decision 13 (resolution-dependent diagnostic filtering); documents the conceptual register shift in prompt text
6. **Added E16** documenting the prompt text changes from cartographic naming to visual descriptions (commit `2d46311`)
7. **Recommended and user uploaded 5 files to OSF** — protocol-errata, decisions-log, fp-fn-register, hypothesis-tracking, prompt-text-review-synopsis
8. **Archived OSF description and narrative summary** as local markdown files; reflowed description from single-line paste

### Issues

- **K=10 propagation**: The decisions-log's incorrect K=10 claim would have been submitted to OSF if the user hadn't caught it from domain memory. Intermediate documents were treated as authoritative without source verification.
- **Over-generalisation risk in summarisation**: Three of five issues found were cases where consolidation flattened nuanced claims into simple assertions.

### Commits

| Hash | Description |
|------|-------------|
| `2b473d7` | `docs(prereg)`: Add OSF update doc, errata E15-E16, Decision 14 |
| `3420c5f` | `docs(prereg)`: Add OSF description and narrative summary to repo |

### Pending Work

- [x] ~~Compose OSF submission document~~ — completed and submitted
- [ ] **Config updates**: Wire expanded HN pool into H9 rotation configs
- [ ] **H9 assignment algorithm**: Implement HN rotation assignment
- [ ] **SDK migration**: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] **Upload Phase 1 materials to OSF**: Library construction results
- [ ] **Fix markdownlint errors**: 107 pre-existing formatting issues across prompt files
- [ ] **Begin Phase 2a execution**: H1 M/E level testing

## Session 16 — 2026-02-04 (Phase 2 readiness assessment and gate-keeping)

### Overview

Final verification session before Phase 2a execution. Archived 7 CC sessions (Feb 2–4), ran a comprehensive 10-area readiness assessment, verified pytest (258 tests pass), cross-referenced all 5 Phase 2 study YAML files against the preregistration and execution plan, and resolved three discrepancies. All readiness areas confirmed green.

### Accomplishments

1. **Archived 7 CC sessions** (Sessions 9–15, Feb 2–4) with gzip compression, human-readable directory names, and full v1.1 metadata (titles, tags, three_ps summaries); updated CATALOG.json
2. **Ran 10-area readiness assessment** — execution plan, preregistration, checklists, prompts (13 instructions + 18 configs), scripts, inputs (60 tiles + 14 hard examples), tests, infrastructure, errata/decisions, and working notes all confirmed ready
3. **Verified pytest** — 258 tier1 tests pass in `.venv/` (pytest 9.0.2)
4. **Cross-referenced study YAMLs** — all 5 Phase 2 YAMLs (2a–2e) verified against execution plan v3.0 and preregistration; factor levels, cell counts, fixed parameters, planned contrasts, and decision rules all consistent
5. **Fixed Scale-16/32 in Phase 2c YAML** — commented out deferred conditions with E11 reference; updated estimates from 7→5 cells (15,000 calls, ~$55); removed S2/S3 contrasts
6. **Annotated B1 ≡ C3** — the "bonus" contrast is the same pair as sequential addition C3 (+HP vs Scale-4); added inline comment rather than duplicating
7. **Updated studies/README.md** — replaced stale stranded-factorial filenames with current OFAT names; added hypothesis references and cell counts

### Issues

- **Propagation failures**: All three discrepancies were cases where a design document was updated but a dependent configuration or README file wasn't synchronised. Same class of error as Session 15's K=10 issue, but at the config-file level.

### Commits

| Hash | Description |
|------|-------------|
| `b389a46` | `docs(notes)`: Add Session 15 reflections across five documents |
| `5d45277` | `chore(archive)`: Archive 7 CC sessions (Feb 2–4) |

### Pending Work

- [x] ~~Compose OSF submission document~~ — completed and submitted (Session 15)
- [ ] **Begin Phase 2a execution**: H1 M/E level testing — READY
- [ ] **Config updates**: Wire expanded HN pool into H9 rotation configs
- [ ] **H9 assignment algorithm**: Implement HN rotation assignment
- [ ] **SDK migration**: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] **Upload Phase 1 materials to OSF**: Library construction results
- [ ] **Fix markdownlint errors**: 107 pre-existing formatting issues across prompt files

---

## Session 17 — 2026-02-05 (Phase 2a infrastructure, sanity checks, and naming standardisation)

### Overview

First execution session for Phase 2a. Built the run_phase2.py OFAT runner, fixed all 5 Phase 2 YAML files (erroneous `passes: 5`), corrected the execution plan cost tables, and ran graduated sanity checks (Levels 1–5). Level 4 revealed implausibly low F1 (~0.11), traced to `validation_bounds.geojson` containing calibration tiles instead of validation tiles due to a "holdout" vs "validation" naming mismatch. Confirmed zero calibration/validation overlap. Regenerated bounds (corrected F1: 0.36–0.44). Standardised naming across the codebase.

### Phase 2a Sanity Check Results (image-only, corrected)

| Run | Precision | Recall | F1 |
|-----|-----------|--------|------|
| 1 | 0.346 | 0.588 | 0.435 |
| 2 | 0.307 | 0.526 | 0.388 |
| 3 | 0.282 | 0.495 | 0.360 |

### Accomplishments

1. **Created `scripts/run_phase2.py`** — OFAT runner for Phases 2a–2e with YAML parsing, condition extraction, randomised execution order, checkpoint/resume, cost monitoring, and CLI overrides (--runs, --limit, --condition, --dry-run, --resume)
2. **Created `tests/test_run_phase2.py`** — 37 tier1 tests covering config loading, condition extraction, unit generation, checkpoint logic, and real YAML validation
3. **Fixed all 5 Phase 2 YAMLs** — removed erroneous `passes: 5`, corrected API call estimates and costs, updated output path patterns (E17)
4. **Corrected execution-plan.md** — removed ×N=5 multiplier from all cost formulas, updated Phase 2 total from $286→$57
5. **Archived `run_study.py`** to `archive/deprecated-scripts/` (D15)
6. **Ran graduated sanity checks Levels 1–5** — all passed (180 API calls, ~$0.37 total)
7. **Found and fixed cost tracking bug** — `read_meta_cost()` read wrong JSON path (`estimated_cost_usd` vs `cost_estimate.total_cost_usd`)
8. **Investigated low F1** — traced to `validation_bounds.geojson` containing 20 calibration tiles instead of 60 validation tiles (E19)
9. **Confirmed zero calibration/validation overlap** — tile sets are completely disjoint
10. **Regenerated `validation_bounds.geojson`** — 60 features matching validation manifest
11. **Standardised naming** — "holdout" → "validation" across metadata JSON, 3 scripts, 2 test files (E20)
12. **Updated documentation** — errata E17–E20, Decision 15, execution checklist

### Issues

- **Bounds file mismatch (E19)**: `validation_bounds.geojson` was generated from calibration manifest due to naming inconsistency between `tile_selection_metadata.json` ("holdout" key) and `validation_manifest.json`. Root cause: naming convention decision applied to manifest filename but not to metadata or scripts.
- **Cost tracking bug**: `read_meta_cost()` looked for top-level `estimated_cost_usd` but actual path is `cost_estimate.total_cost_usd`.
- **GeoJSON extension**: Batch detector outputs files without `.geojson` extension, requiring manual filename specification during evaluation.
- **Compact event**: Context compacted mid-investigation; post-compact instance completed resolution from conversation summary.

### Commits

| Hash | Description |
|------|-------------|
| `deed6f5` | `fix(studies)`: Correct erroneous N=5 passes in Phase 2 YAMLs and execution plan (E17) |
| `c64a7dc` | `feat(scripts)`: Add run_phase2.py OFAT runner, archive run_study.py (D15) |
| `4911170` | `fix(scripts)`: Read cost from correct meta.json path in run_phase2.py |
| `496dde2` | `fix(inputs)`: Regenerate validation_bounds.geojson from correct manifest (E19) |
| `ced77b4` | `refactor(naming)`: Standardise "holdout" → "validation" across codebase (E20) |

### Pending Work

- [ ] **Full Phase 2a execution**: 5 conditions × 10 runs × 60 tiles = 3,000 calls (~$11) — READY
- [ ] **Investigate zero tile-level specificity**: Model detects in all 24 empty tiles
- [ ] **Fix GeoJSON extension**: Batch detector output naming convention
- [ ] Config updates: Wire expanded HN pool into H9 rotation configs
- [ ] H9 assignment algorithm: Implement HN rotation assignment
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF
- [ ] Fix markdownlint errors: 107 pre-existing formatting issues

---

## Session 18 — 2026-02-05 (Continuation: reflections commit, collaboration discussion, RDM)

### Overview

Short continuation session following Session 17's compact event. Committed the Session 17 reflections, then had an extended conversation about human–AI collaboration dynamics, the user's RDA Interest Group for documentation standards, and why documenting AI collaboration requires capturing "the path not taken." Added Observations 99–101 to working notes.

### Accomplishments

1. **Committed Session 17 reflections** across 5 documents (`3f33d44`)
2. **Wrote Observation 99** — complementary expertise in staged execution (human calibration catches what automation misses)
3. **Wrote Observation 100** — why human–AI collaboration documentation differs from traditional RDM (5-dimension analysis: hypotheses eliminated, approaches rejected, moments of redirection, thinking traces as primary sources, contribution legibility asymmetry)
4. **Wrote Observation 101** — memory asymmetry as a documentation design constraint
5. **Committed Observations 99–100** (`f792b00`)
6. **Discussed RDA Interest Group** — user and colleague establishing an IG to develop documentation standards for human–AI interactions; this project's protocol is a proof-of-concept

### Issues

- None (no technical work in this session)

### Commits

| Hash | Description |
|------|-------------|
| `3f33d44` | `docs(notes)`: Add Session 17 reflections across five documents |
| `f792b00` | `docs(notes)`: Add Observations 99–100 on collaboration and RDM |

### Pending Work

- [ ] **Full Phase 2a execution**: 5 conditions × 10 runs × 60 tiles = 3,000 calls (~$11) — READY
- [ ] **Investigate zero tile-level specificity**: Model detects in all 24 empty tiles
- [ ] **Fix GeoJSON extension**: Batch detector output naming convention
- [ ] Config updates: Wire expanded HN pool into H9 rotation configs
- [ ] H9 assignment algorithm: Implement HN rotation assignment
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF
- [ ] Fix markdownlint errors: 107 pre-existing formatting issues

---

## Session 19 — 2026-02-06 (Phase 2a execution complete, critical implementation bug discovered)

### Overview

Completed Phase 2a data collection: 50 units (5 conditions × 10 runs), 3,000 API calls, $6.54 total. Recovery from network failures required re-running 5 incomplete units. Bootstrap analysis computed per-run metrics. During QA, user flagged unexpectedly clustered F1 outcomes. Investigation revealed a critical implementation bug: all 5 conditions received identical example images. The modality factor (H1: image vs text-only) was not manipulated. Phase 2a data is invalid for the preregistered hypothesis.

### Phase 2a Results (invalid for H1)

| Condition | Mean F1 | StdDev | Note |
|-----------|---------|--------|------|
| brief-text-image | 0.4617 | ±0.0269 | All received images |
| brief-text | 0.4610 | ±0.0217 | Should have been text-only |
| verbose-text | 0.4528 | ±0.0321 | Should have been text-only |
| verbose-text-image | 0.4369 | ±0.0333 | All received images |
| image-only | 0.4252 | ±0.0342 | Correct |

### Accomplishments

1. **Completed Phase 2a data collection** — 50/50 units, $6.54 total cost
2. **Recovered from network failures** — 5 incomplete runs (low detection counts) re-run successfully
3. **Computed per-run metrics** — `outputs/phase2a/per_run_metrics.csv` with F1/precision/recall per run
4. **Investigated clustered F1 outcomes** — traced to missing modality manipulation
5. **Identified implementation gap** — `4_detect_mounds_batch.py` has no conditional logic to skip images for text-only conditions
6. **Verified against preregistration** — Table at lines 412-418 explicitly specifies Brief-text and Verbose-text should receive "No" images
7. **Documented Observation 102** — design-to-implementation translation failures as distinct failure class

### Critical Bug (E24)

**The batch script sends 17 example images to ALL conditions.** The preregistration specifies:

| Condition | Images |
|-----------|--------|
| image-only | Yes |
| brief-text | **No** |
| brief-text-image | Yes |
| verbose-text | **No** |
| verbose-text-image | Yes |

The config files have no `include_example_images` field. The batch script (lines 556-572) unconditionally loads and sends all example images. 3,000 API calls tested text elaboration within image+text modality, not the modality factor.

**Root cause**: Design specification in preregistration was not translated into code. No one asked: "how does the code know which conditions include images?"

### Issues

- **Invalid data for H1**: Modality factor not manipulated
- **Network instability**: Initial run had 5 incomplete units (1–97 features instead of ~140)
- **Bootstrap analysis**: Still running in background (task bbf60d6) but results moot for H1
- **Context compaction**: Session compacted during reflection; post-compact instance completed from summary

### Commits

None (no code changes committed in this session).

### Pending Work

- [ ] **Fix batch script** — Add `include_example_images` field to configs, add conditional logic to skip images
- [ ] **Re-run Phase 2a** — With corrected implementation (~$6.50 additional)
- [ ] **Document E24** — Log erratum for implementation gap
- [ ] **Assess secondary value** — Phase 2a data tests text elaboration within image+text; potentially useful even if not preregistered
- [ ] **Kill bootstrap task** — Task bbf60d6 still running; results invalid for H1
- [ ] Investigate zero tile-level specificity
- [ ] Config updates: Wire expanded HN pool into H9 rotation configs
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF

---

## Session 19b — 2026-02-06 (Phase 2a fix, text-only re-run, surprising H1 result)

### Overview

Continuation session after compaction. Implemented the modality manipulation fix (E25): added `include_example_images` config field and conditional logic in the batch script to skip images for text-only conditions. Archived invalid text-only runs, re-ran 20 text-only units with corrected code ($0.31 additional cost). Analysis revealed a surprising result: text-only conditions significantly outperform image conditions, contradicting H1 prediction.

### Phase 2a Results (corrected)

| Condition | Mean F1 | Precision | Recall | Detections |
|-----------|---------|-----------|--------|------------|
| **brief-text** | **0.5425** | 0.434 | 0.725 | 162–177 |
| verbose-text | 0.4710 | 0.364 | 0.666 | 165–175 |
| brief-text-image | 0.4617 | 0.393 | 0.559 | 130–150 |
| verbose-text-image | 0.4369 | 0.368 | 0.539 | 135–145 |
| image-only | 0.4252 | 0.349 | 0.545 | 130–145 |

**Key finding**: Text-only conditions outperform image conditions. Brief-text (F1=0.5425) is substantially better than image-only (F1=0.4252), a ~0.12 difference. This contradicts H1 prediction.

**Detection count divergence**: Text-only conditions produce 20–30% more detections than image conditions. Images appear to constrain rather than enrich detection behaviour.

### Accomplishments

1. **Implemented E25 fix** — Added `include_example_images: false` to `detect_brief-text.json` and `detect_verbose-text.json`; added conditional logic in `4_detect_mounds_batch.py` to skip image loading
2. **Archived invalid runs** — Moved invalid brief-text and verbose-text directories to `archive/phase2a-invalid-text-only-runs/`
3. **Re-ran text-only conditions** — 20 units (brief-text + verbose-text, 10 runs each), $0.31 additional cost
4. **Generated corrected analysis** — `outputs/phase2a/per_run_metrics.csv` with valid text-only data
5. **Documented E25** in `docs/methodology/preregistration/protocol-errata.md`
6. **Updated MEMORY.md** with Phase 2a corrected status
7. **Added Observation 103** — Text-only outperforming image as foundational assumption challenge

### Surprising Result Analysis

The H1 prediction was that image-based conditions would outperform text-only conditions. The data shows the opposite:

- Text-only conditions achieve higher recall (0.67–0.73) than image conditions (0.54–0.56)
- Text-only conditions detect more features overall (162–177 vs 130–150)
- The difference is consistent across all 10 runs per condition

Possible explanations:
1. Images anchor to specific visual patterns that don't generalise well
2. Negative examples (hard negatives) make the model too conservative
3. Text descriptions allow more flexible matching
4. Gemini's architecture may favour text grounding for this task

### Issues

- **Bootstrap CIs may have bug** — Reported CIs don't contain means for some conditions; needs investigation
- **Result contradicts project trajectory** — Visual few-shot was developed as an improvement over text-only (Observations 9–10); Phase 2a suggests that trajectory was wrong

### Commits

None yet — reflection documents completed but not committed.

### Pending Work

- [x] Fix batch script for modality manipulation (E25)
- [x] Re-run text-only conditions with corrected code
- [x] Generate corrected per-run metrics
- [x] **Investigate bootstrap CI calculation** — CIs don't appear to contain means (fixed in Session 20, E26)
- [ ] **Discuss H1 decision rule implications** — brief-text wins by decision rule but contradicts prior experience
- [ ] Commit reflection documents and E25 changes
- [ ] Config updates: Wire expanded HN pool into H9 rotation configs
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF

---

## Session 20 (2026-02-06)

**Focus**: Bootstrap CI bias diagnosis and fix (E26)

### Summary

Single-focus session dedicated to diagnosing and fixing a systematic
bias in the bootstrap confidence interval functions in
`lib_advanced_metrics.py`. The AI flagged in the previous session that
CIs didn't contain point estimates (e.g., image-only F1=0.4252,
CI=[0.254, 0.373]).

Root cause: `scope_references_to_tiles()` uses `gdf_ref.index.isin()`
which silently de-duplicates references when tiles are resampled with
replacement. Extra detections against de-duplicated references = false
positive inflation = precision deflation = downward-biased F1 CIs.

Fix: Pre-compute TP/FP/FN per tile once, aggregate in bootstrap loop
with proper duplicate handling. Added `compute_per_tile_tp_fp_fn()` and
`aggregate_tile_metrics()` helpers. Refactored all 7 bootstrap functions
+ 2 tile classification bootstrap functions.

### Key Results

Corrected Phase 2a CIs (all now properly contain point estimates):

| Condition | F1 | 95% CI |
|-----------|----|--------|
| brief-text | 0.5425 | [0.424, 0.650] |
| verbose-text | 0.4710 | [0.355, 0.569] |
| brief-text-image | 0.4617 | [0.371, 0.541] |
| image-only | 0.4252 | [0.340, 0.500] |
| verbose-text-image | 0.4369 | [0.358, 0.507] |

0 FDR-significant pairwise comparisons at q=0.05 (unchanged from
before fix). 3 initially significant comparisons (image-only vs
brief-text, brief-text vs verbose-text, brief-text vs verbose-text-image).

### Issues

- **Corrected CIs are wider than biased ones** — honest results less
  dramatic than biased ones; the bias was flattering to the findings
- **Per-tile approximation** — new approach does per-tile matching
  rather than per-map; cross-tile effects within 20m buffer are
  negligible for these tile sizes

### Commits

None yet — changes to be committed.

### Pending Work

- [ ] Commit bootstrap CI fix (lib_advanced_metrics.py, tests, E26)
- [ ] Commit regenerated analysis outputs
- [ ] Commit reflection documents (Session 20)
- [ ] **Discuss H1 decision rule implications** — brief-text wins by decision rule but contradicts prior experience
- [ ] Config updates: Wire expanded HN pool into H9 rotation configs
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF

---

## Session 21 (2026-02-06)

**Focus**: Systematic verification of Phase 2a text-only outperformance finding

### Overview

Dedicated verification session to rule out pipeline artefacts before accepting the counter-intuitive Phase 2a result that text-only conditions outperform image-inclusive conditions. Four-track verification: (A) statistical pipeline recomputation, (B) image pipeline metadata/token verification, (C) fresh one-off tile assessments, and (D) system instruction content analysis.

### Accomplishments

1. **Wrote `scripts/verify_phase2a_metrics.py`** — standalone verification script covering Parts A+B (F1 recomputation, per-tile decomposition, spatial overlap, metadata/token analysis, detection distributions, instruction comparison)
2. **Independently recomputed all 50 F1 values** — all match `per_run_metrics.csv` exactly; no pipeline bugs
3. **Per-tile F1 decomposition** — brief-text wins 15 tiles, image-only wins 10, advantage distributed across 3/4 maps
4. **Spatial overlap analysis** — only 29.8% shared detections; brief-text-only detections are 2x more likely to be TPs (27.7% vs 14.3%)
5. **Input token analysis** — 10.70x ratio (113K vs 1.21M); zero variance; no image leakage possible
6. **Selected 5 verification tiles** — 2 high density, 2 low density, 1 empty; created `inputs/tiles/verification_manifest.json`
7. **Ran fresh API calls** — 10 calls (~$0.012); brief-text F1=0.7600 vs image-only F1=0.5714 (+0.19 diff) on fresh data
8. **Wrote verification report** — `results/phase2-factorial/phase2a-verification-report.md` documenting all findings for write-up preparation

### Key Results

All red flag criteria cleared:

| Check | Outcome |
|-------|---------|
| F1 values match CSV | GREEN — all 50 exact |
| Advantage broadly distributed | GREEN — 3/4 maps, 15 tiles |
| brief-text finds true mounds | GREEN — 23 additional TPs |
| Input tokens differ dramatically | GREEN — 10.70x ratio |
| Fresh runs reproduce pattern | GREEN — +0.19 F1 diff |
| Instructions identical within level | GREEN — byte-identical |

Within-elaboration-level comparisons (strongest evidence):

- brief-text vs brief-text-image: +0.08 F1 (identical text, only images differ)
- verbose-text vs verbose-text-image: +0.03 F1 (identical text, only images differ)

### Issues

- None — all verification checks passed

### Commits

None yet — verification script, manifest, report, and reflection documents to be committed.

### Pending Work

- [ ] Commit verification script, manifest, report, and reflection documents
- [ ] **Discuss H1 decision rule implications** — brief-text wins by decision rule but contradicts prior experience
- [ ] Config updates: Wire expanded HN pool into H9 rotation configs
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF

---

## Session 22 — 2026-02-06 (Dual-track carry-forward decision and Phase 2b setup)

### Overview

Strategic planning session following the Phase 2a verification. Investigated whether text-only prompts were fully exercised across experimental conditions (they were not — by design). Collaboratively designed a dual-track carry-forward strategy to resolve the structural incompatibility between a text-only H1 winner and downstream phases designed for image-using conditions. Documented the decision (Decision 16, Erratum E27), configured two Phase 2b YAMLs for dual-track temperature testing, validated both with dry runs, committed and pushed.

### Accomplishments

1. **Investigated text-only prompt coverage** — confirmed text-only prompts were tested only in Phase 2a at a single fixed parameter combination (T=1.0, Scale-8, canonical-first, H5=Minimal), and were explicitly excluded from Phases 2c–2e
2. **Designed dual-track carry-forward** — Track 1 (brief-text-image) follows full preregistered OFAT; Track 2 (brief-text) receives targeted tests where applicable
3. **Wrote Decision 16** in decisions log — full rationale, track specifications, budget implications, convergence plan at Phase 3
4. **Wrote Erratum E27** in protocol errata — formal deviation record for dual-track vs preregistered single-winner carry-forward
5. **Updated Phase 2b YAML** (`studies/phase2b-h7-temperature.yaml`) — replaced placeholders with brief-text-image config, updated output directory to `outputs/phase2b/track1-image/`
6. **Created Phase 2b text-only YAML** (`studies/phase2b-h7-temperature-text-only.yaml`) — brief-text config, output to `outputs/phase2b/track2-text/`, documented as exploratory track
7. **Validated both YAMLs** — dry runs confirm correct condition extraction, config paths, temperature overrides, and output directories
8. **Decided to rerun T=1.0** rather than reuse Phase 2a data — replication check worth the ~$4.40 cost

### Issues

- None (no technical issues in this session)

### Commits

| Hash | Description |
|------|-------------|
| `143e8a5` | `feat(studies)`: Set up Phase 2b dual-track temperature testing |

### Pending Work

- [ ] **Run Phase 2b Track 1** — `python3 scripts/run_phase2.py studies/phase2b-h7-temperature.yaml` (50 units, ~$11)
- [ ] **Run Phase 2b Track 2** — `python3 scripts/run_phase2.py studies/phase2b-h7-temperature-text-only.yaml` (50 units, ~$11)
- [ ] **Phase 2b analysis** — update analysis script for dual-track output directories; consider cross-track temperature comparison
- [ ] **Resolve pooling question** — whether Phase 2a T=1.0 data should be pooled with Phase 2b T=1.0 runs in analysis
- [ ] **Resolve FDR scope** — whether FDR correction spans both tracks or applies within each
- [ ] Config updates: Wire expanded HN pool into H9 rotation configs
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF

---

## Session 23 — 2026-02-07 (Phase 2b pipeline hardening and checkpoint repair)

### Overview

Recovery session after the Phase 2b rate-limiting incident. Both tracks had been launched simultaneously at workers=60, overwhelming the 1M TPM limit when the API responded quickly (~6s/tile). 82 of 100 runs were damaged (13 healthy in track1-image, 2 in track2-text). Checkpoint files incorrectly marked all 100 as "completed." The user arrived with a detailed 11-step engineering plan. Session implemented the plan across 6 files (3 new, 3 modified), all 345 tests passing.

### Accomplishments

1. **Created TPM-aware adaptive concurrency governor** (`scripts/lib_tpm_governor.py`) — semaphore + sliding-window token ledger that scales workers down when the API is fast and up when it's slow
2. **Hardened batch detection script** (`scripts/4_detect_mounds_batch.py`) — governor integration, jittered exponential backoff, 15 retries (CLI-configurable), `None` failure sentinel, early warning system, tile completion manifests, exit codes, `--max-retries` and `--base-wait` CLI args
3. **Added completed_items tracking** to `ExecutionStats` in `scripts/lib_llm_metadata.py`
4. **Added meta.json validation** in `scripts/run_phase2.py` — `read_meta_failures()` helper catches partial failures even when exit code is 0
5. **Created checkpoint repair script** (`scripts/repair-phase2b-checkpoint.py`) — scans runs, classifies healthy vs damaged, backs up and rewrites checkpoints
6. **Wrote 13 tier1 unit tests** for TPM governor covering semaphore behaviour, sliding window, concurrency adaptation, and thread safety
7. **Added Google API quota reset note** to project CLAUDE.md — midnight PT = 7 PM AEDT

### Issues

- Resume logic gap: damaged output files remain on disk; `--resume` may load partial features from existing GeoJSON rather than starting fresh. Needs resolution before re-run.

### Commits

| Hash | Description |
|------|-------------|
| `140ed78` | `feat(scripts)`: Add TPM-aware adaptive concurrency governor |
| `d9782a6` | `fix(scripts)`: Harden batch detection against rate limiting |
| `64b72f3` | `fix(scripts)`: Track completed tiles in metadata |
| `7485766` | `fix(scripts)`: Validate tile completeness in run_phase2.py |
| `29c114e` | `chore(scripts)`: Add Phase 2b checkpoint repair script |

### Pending Work

- [ ] **Resolve resume logic gap** — damaged output files may need deletion before re-run, or batch script needs option to start fresh
- [ ] **Run checkpoint repair** — `python scripts/repair-phase2b-checkpoint.py`
- [ ] **Re-run Phase 2b Track 1** — `scripts/run_phase2.py studies/phase2b-h7-temperature.yaml --workers 30 --resume`
- [ ] **Re-run Phase 2b Track 2** — `scripts/run_phase2.py studies/phase2b-h7-temperature-text-only.yaml --workers 30 --resume`
- [ ] **Phase 2b analysis** — update analysis script for dual-track output directories
- [ ] Config updates: Wire expanded HN pool into H9 rotation configs
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF

---

## Session 24 — 2026-02-08 (Phase 2b Track 1 completion)

### Overview

Operational session focused on completing Phase 2b Track 1 data collection
using the multi-unit parallelisation feature implemented in Session 23.
Started with 37/50 units completed, 12 failed, and 1 not attempted.
Reached 50/50 through five iterative run attempts, overcoming environment
issues, API slowness, and a misdiagnosis of the failure mode.

### Accomplishments

1. **Completed Phase 2b Track 1** — all 50 execution units (5 temperatures
   x 10 runs x 60 tiles = 3,000 tile evaluations) now finished
2. **Verified both tracks** — Track 1: 50/50 with 7,108 detections;
   Track 2: 50/50 with 7,932 detections; 6,000 total tile evaluations
   confirmed
3. **Resolved zero-detection tile ambiguity** — 12 Track 1 units at
   T1.0/T1.3 had fewer than 60 features in GeoJSON; confirmed via
   tiles.json metadata that all tiles were evaluated with zero detections
   (valid experimental result, not missing data)
4. **Identified opposite-intervention failure modes** — user corrected
   misdiagnosis: slow API responses required *increasing* parallelism
   (poor API performance), not decreasing it (rate limiting). API
   dashboard showed 25/1K RPM, 365K/1M TPM — abundant headroom
5. **Wrote end-of-session reflections** in session-reflection-investigation
   (Entry 23), llm-observations (Session 24), working_notes (Obs 111-113),
   and abductive-reasoning-investigation (Session 24 Assessment)

### Issues

- **Wrong Python interpreter**: First run used system `/usr/bin/python3`
  instead of `.venv/bin/python3`, causing `ModuleNotFoundError: No module
  named 'tqdm'` across all 13 units
- **API timeout too short**: Initial 600s timeout insufficient for slow
  API; increased to 1800s
- **Misdiagnosed failure mode**: Reduced parallelism when API was slow,
  which was the opposite of the correct intervention. User provided API
  dashboard showing abundant quota headroom.
- **stdout buffering**: Background task stdout was block-buffered without
  TTY, making `_execute_units_parallel` print output invisible. Worked
  around by reading per-unit log files and checkpoint.json directly

### Commits

No commits this session — all changes were to data outputs and
reflection documents (untracked/gitignored).

### Pending Work

- [x] Complete Phase 2b Track 1 data collection (50/50)
- [x] Verify all tiles evaluated across both tracks
- [x] End-of-session reflection
- [ ] **Phase 2b analysis** — run statistical analysis on completed data
- [ ] **Governor review** — TPM governor needs to distinguish "slow API"
  (increase parallelism) from "rate limited" (decrease parallelism);
  user flagged for future work
- [ ] Config updates: Wire expanded HN pool into H9 rotation configs
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF

---

## Session 25 — 2026-02-08 (TPM governor rate-limit awareness)

### Overview

Engineering session implementing the Rate-Limit-Aware TPM Governor plan.
Extended the governor with rate-limit tracking, latency-informed scaling,
and a priority-based state machine. Restructured the batch script's retry
loop to release governor slots before backoff sleep. Followed by a
comprehensive line-by-line code audit that found and fixed three issues.
Continued from compacted context (Session 24).

### Accomplishments

1. **Implemented rate-limit-aware governor** — added `LatencyRecord`
   dataclass, rate-limit event tracking, latency ledger, cooldown timer,
   and priority-based state machine in `lib_tpm_governor.py`
2. **Restructured batch retry loop** — governor slot released before
   backoff sleep in `4_detect_mounds_batch.py` so 429 signals propagate
   immediately; added `was_rate_limited` and `latency_seconds` kwargs
3. **Added 15 new tests** across 5 test classes in `test_tpm_governor.py`:
   rate-limit response, latency-based ramp-up, cold start, backward
   compatibility, and mixed scenarios
4. **Fixed 4 initial test failures** — resolved TPM ledger contamination
   in tests that needed low TPM for under-threshold paths; injected
   `LatencyRecord` objects directly instead of through `release()`
5. **Comprehensive code audit** found and fixed 3 issues:
   - `continue` paths in retry loop lost backoff sleep (restored direct
     `time.sleep(5)` before `continue`)
   - `cooldown_seconds` default (60.0) == `window_seconds` made cooldown
     path unreachable (changed to 90.0)
   - `test_holds_at_sustainable` passed via wrong code path (rewritten
     with direct state injection)
6. **All tests passing** — 33/33 governor tests, 372/372 full suite,
   ruff lint clean

### Issues

- **TPM ledger contamination in tests**: Releasing high-token-count
  values through `release()` simultaneously populates TPM ledger and
  latency records. High TPM triggers `over_target` (priority 2) instead
  of `under_threshold_ramp` (priority 3b). Fixed by injecting latency
  records directly into the deque.
- **Python `continue`/`finally` interaction**: `continue` inside `try`
  runs `finally` then jumps to next iteration, skipping post-finally
  deferred sleep code. Not a bug in either construct — a compositional
  interaction that breaks the deferred-sleep pattern.
- **Cooldown path unreachable with defaults**: Mathematical
  inconsistency in plan — `cooldown_seconds == window_seconds` means
  rate-limit events age out of both simultaneously, creating a
  zero-width cautious recovery window.

### Commits

| Hash | Message |
|------|---------|
| `d19560a` | `feat(governor)`: Add rate-limit awareness and latency-informed scaling |

### Pending Work

- [x] Implement rate-limit-aware governor (all 3 files)
- [x] Pass all tests and lint
- [x] Comprehensive code audit
- [x] Commit and push
- [x] End-of-session reflections
- [ ] **Production validation** — verify governor behaviour during next
  Phase 2b run (sustainable formula, step sizing, cooldown recovery)
- [ ] **Phase 2b analysis** — run statistical analysis on completed data
- [ ] Config updates: Wire expanded HN pool into H9 rotation configs
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF

## Session 26: Memory system exploration and Phase 2b temperature analysis (2026-02-08)

### Overview

Split session covering two domains: (1) exploration and critique of the
personal-assistant memory system at `~/personal-assistant/`, with
recommendations on project filtering and GTD category exclusion; (2)
first statistical analysis of Phase 2b temperature results across both
tracks, including a file-loading bug fix.

### Accomplishments

1. **Explored personal-assistant memory system** — mapped architecture
   (JSONL store, PostgreSQL derived layer, hooks, retrieval). Identified
   two scope issues: no project-based filtering on retrieval, and GTD
   categories duplicating the accountability hook banner
2. **Analysed memory/reflection complementarity** — articulated how the
   memory system (atomic facts) and reflection system (structured
   narratives) serve different continuity functions with different
   failure modes
3. **Ran Phase 2b Track 1 (image) analysis** — 5 temperatures × 10 runs,
   bootstrapped CIs, FDR correction. T0.0 optimal (F1=0.5574), 6/10
   FDR-significant pairwise comparisons
4. **Ran Phase 2b Track 2 (text) analysis** — same design. T0.0 optimal
   (F1=0.6602), 4/10 FDR-significant pairwise comparisons
5. **Fixed `.tiles.json` file-loading bug** in `analyse_phase2_results.py`
   — `.tiles.json` files were passing exclusion filters and being picked
   up as detection results, causing T1.0 and T1.3 to load only 7-8 runs.
   Added `.tiles.json` to exclusion filter on line 120
6. **Reran both analyses with fix** — all conditions now load 10/10 runs;
   results stable with corrected data
7. **End-of-session reflections** — updated all 5 reflection documents
   (post-compaction, flagged per protocol)

### Issues

- **`python` not found in background tasks**: Background commands don't
  inherit the venv. Must use `.venv/bin/python3` explicitly
- **`.tiles.json` file matching**: Phase 2b introduced tile-tracking
  metadata files that the Phase 2a-era analysis script didn't exclude.
  Root cause: exclusion-based rather than inclusion-based file filtering
- **Context compaction**: Session was broad enough (infrastructure +
  analysis + bug fix) to trigger compaction before reflections. Future
  sessions should trigger /reflect earlier

### Commits

No commits this session (analysis outputs and reflection documents are
uncommitted working changes).

### Pending Work

- [x] Phase 2b statistical analysis (both tracks)
- [x] Fix `.tiles.json` file-loading bug
- [x] End-of-session reflections
- [ ] **Production validation** — verify governor behaviour during next
  Phase 2b run (sustainable formula, step sizing, cooldown recovery)
- [ ] Commit Phase 2b results and analysis script fix
- [ ] Config updates: Wire expanded HN pool into H9 rotation configs
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF

## Session 27 — 2026-02-09/10 (Phase 2c exploratory + script hardening)

**Duration**: Extended overnight session (API slowness)
**Phase**: 2c-exploratory

### Accomplishments

1. **Phase 2c exploratory study**: Designed, executed, and analysed
   pure-positive HP scaling (3 conditions x K=10). Created library
   configs (`library_pure-positive-2hp.json`, `library_pure-positive-4hp.json`),
   study YAML, copied existing pure-positive-canon data, ran 20 new units
2. **Script hardening**: Added incremental GeoJSON saves to
   `4_detect_mounds_batch.py` and graceful SIGTERM timeout to
   `run_phase2.py` after a single unit (`pure-positive-2hp/run_2`)
   failed 6 consecutive times due to API slowness + write-only-at-end
3. **Completed stubborn unit**: 7th attempt succeeded via incremental
   resume (6 tiles saved from attempt 6, 54 remaining processed in 34 min)
4. **Full 30/30 analysis**: Re-ran bootstrap analysis with complete dataset

### Key Results

Surprising: adding HP to pure-positive library monotonically degrades F1
(0.603 → 0.575 → 0.550). Contradicts expectation that HP would help in
negative-free context. plus-hp (F1=0.609, includes Canon-) remains optimal.

### Issues

- `pure-positive-2hp/run_2` timed out 6 times (API ~2 min/tile)
- Default 3600s timeout insufficient; even 7200s wasn't enough
- Root cause: output only written at end, so no resume possible
- Fix: incremental saves + graceful SIGTERM made retries cumulative

### Commits

- `fb1b636` feat(data): Phase 2c exploratory outputs and results (29/30)
- `6e59cd5` fix(scripts): Incremental saves and graceful timeout
- `cf65c34` feat(data): Complete run_2 and update analysis (30/30)

### Pending Work

- [x] Adversarial review of Phase 2c results *(completed Session 28)*
- [x] Verify each config actually loaded the right example images *(completed Session 28)*
- [x] Check detection outputs for anomalies across conditions *(completed Session 28)*

## Session 28 — 2026-02-10 (Adversarial review + metadata improvements)

**Phase**: 2c verification / infrastructure

### Accomplishments

1. **Adversarial review**: 8-step systematic verification of Phase 2c
   results. All steps passed — no pipeline bugs, configuration errors,
   or scoring anomalies found. Report: `reports/phase2c-adversarial-review.md`
2. **Key mechanistic finding**: plus-hp and pure-positive-4hp produce
   identical detection counts (132) but Canon- negatives redirect 8
   detections from FPs to TPs. Canon- improves placement, not volume.
3. **Verification test designed**: `studies/phase2c-verification-test.yaml`
   (5 tiles, 3 conditions, K=1, ~$0.05). Not yet executed.
4. **Metadata improvements** in `lib_llm_metadata.py`:
   - Renamed `prompt_hash` → `system_instruction_hash`
   - Added `library_hash`, `system_instruction_text`
   - Added `thinking_level`, `max_output_tokens`,
     `include_example_images`, `example_count`
5. **Documentation**: Prompt reconstruction instructions added to
   `docs/pipelines.md`

### Issues

- `prompt_hash` was misleadingly named (hashed system instruction only,
  identical across all 7 conditions). Renamed and augmented.
- Pre-existing test bug found: `test_ramp_up_stability` fails because
  token-aware clamping (added later) reduces initial_concurrency=4 to 3

### Pending Work (next session)

- [ ] Commit all changes (nothing committed this session)
- [ ] Discuss and potentially run verification test (needs
  `verification_bounds.geojson` generated first)
- [ ] Fix `test_tpm_governor.py::test_ramp_up_stability` — raise
  `tpm_limit` or set `tokens_per_request=1` in test fixture
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF

## Session 29 — 2026-02-10 (Standalone pipeline verification)

**Phase**: 2c verification (independent replication)

### Accomplishments

1. **Built standalone verification script**:
   `scripts/standalone_verification.py` (900 lines, zero project imports).
   Independent reimplementation of prompt assembly, coordinate transforms,
   spatial scoping, and detection matching (greedy NN instead of Hungarian).
2. **Ran 3 verification batches** (90 API calls total, ~$0.06):
   - Batch 1 (10 tiles, 40 refs): reversed pattern (pp-4hp > pp-canon > plus-hp)
   - Batch 2 (10 tiles, 39 refs): confirmed pattern (plus-hp > pp-canon > pp-4hp)
   - Batch 3 (10 tiles, 21 refs): partial (plus-hp > pp-4hp > pp-canon)
   - Aggregate: plus-hp (0.686) > pp-4hp (0.662) > pp-canon (0.658)
3. **Refactored script for reuse**: Added `--tiles` (JSON file) and
   `--output-dir` CLI arguments for running arbitrary tile batches.
4. **Discovered metadata divergence**: `mound_count` in validation bounds
   doesn't match independent spatial scoping for several tiles.

### Issues

- Batch 1 reversal initially alarming but resolved as small-sample noise
- Two planned tiles had zero references under independent scoping;
  replaced with alternatives from same maps
- Model resolved as `gemini-3-flash-preview` (may differ from Phase 2c
  model version)

### Pending Work (next session)

- [ ] Causal reasoning review: why does plus-hp outperform? What is the
  mechanism behind the Canon- negative effect?
- [ ] Results write-up for the plus-hp configuration being advanced
- [ ] Documentation of the full scrutiny chain (adversarial review →
  standalone verification → 3-batch replication)
- [ ] Investigate `mound_count` metadata vs spatial scoping divergence
- [ ] Fix `test_tpm_governor.py::test_ramp_up_stability` (carried forward)
- [ ] Commit standalone verification script and outputs

---

## Session 30 — 2026-02-10 (Causal reasoning review and P:N ratio analysis)

**Phase**: 2c analysis (post-verification)

### Accomplishments

1. **Collaborative causal reasoning review**: Reviewed three candidate
   mechanisms for the counterintuitive Phase 2c ordering (P:N ratio
   shift, informative vs uninformative negatives, discriminative
   sandwich). User corrected two framing errors that improved the
   analysis.
2. **Comprehensive P:N ratio analysis**: Produced
   `reports/phase2c-pn-ratio-analysis.md` documenting all 7 Phase 2c
   conditions with master data table (C+/HP/C-/HN/Null/P:N/F1/Det/
   TP/FP/FN), P:N ratio as poor predictor, 2x2 HP × Canon- crossover
   interaction tables, HN degradation effect, clear-vs-ambiguous
   quality asymmetry, and standalone verification cross-reference.
3. **Null tile investigation deferred**: Added Section 3.4 to
   `docs/planning/future-work.md` documenting null tiles as necessary
   infrastructure and proposing an OFAT probe (0, 1, 3, 5 nulls at
   plus-hp) for future exploration.
4. **Memory capture**: `/remember` for null tile decision (functionally
   necessary infrastructure, not a tuneable parameter).
5. **End-of-session reflections**: Updated all 5 reflection documents.
6. **Cross-track performance comparison**: Computed brief-text T=0.0
   (F1=0.660, P=0.559, R=0.807) vs plus-hp T=0.0 (F1=0.609, P=0.524,
   R=0.726). Text-only still leads on all metrics; gap narrowed from
   +0.08 (Phase 2a) to +0.05.
7. **Phase 2d dual-track decision**: Agreed to run negative text
   treatment for both Track 1 (image-using, plus-hp library) and
   Track 2 (text-only). Captured to memory system for handoff.
8. **Handoff prompt composed**: Prepared restart prompt for Phase 2d
   with all design questions externalised.

### Key Findings

- **P:N ratio is a poor predictor**: Negative composition (which types)
  matters more than count or ratio
- **Crossover interaction**: HP and Canon- each reverse their effect
  depending on the other's presence (neither inherently helpful nor
  harmful)
- **Clear vs ambiguous asymmetry**: Canon- (clear negatives) helps; HN
  (ambiguous negatives) hurts regardless of context
- **Null tiles are infrastructure**: Functionally necessary to prevent
  runaway detection; not a parameter to optimise
- **Text-only still leads**: brief-text T=0.0 outperforms plus-hp T=0.0
  by +0.05 F1. Precision is the bottleneck for both tracks (~52–56%).

### Issues

- Post-compaction instance wrote reflections from summary rather than
  direct experience (flagged per protocol)
- H5 design tension: preregistration assumed Scale-8 (with HN) as
  carry-forward; actual carry-forward is plus-hp (no HN). Exclusion
  text still applies but the question shifts slightly.

### Commits

| Hash | Description |
|------|-------------|
| `cef46c9` | `docs(reports)`: Phase 2c P:N ratio and negative composition analysis |
| `f11fda9` | `docs(reflections)`: Session 30 causal reasoning and P:N ratio analysis |

### Pending Work

- [x] Commit P:N ratio report and reflection documents
- [x] **Phase 2d setup and execution** — dual-track negative text
  treatment (completed Session 31; execution pending)
- [ ] Results write-up for plus-hp configuration
- [ ] Investigate `mound_count` metadata vs spatial scoping divergence
- [ ] Fix `test_tpm_governor.py::test_ramp_up_stability` (carried forward)
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF

## Session 31 — 2026-02-11 (Phase 2d dual-track setup)

### Overview

Implemented the Phase 2d dual-track H5 exclusion guidance design from
a detailed plan prepared in the prior session. This was a pure
implementation session — no design decisions were made, no unexpected
findings emerged. The plan specified every file to create/modify and
the implementation followed it exactly.

### Accomplishments

1. **Track 1 instruction files updated**: Trimmed Guideline 3 in
   `detect_brief-text-image_terse.md` and
   `detect_brief-text-image_verbose.md` to remove HN image references.
   Verbose intro sentence also trimmed.
2. **Track 2 instruction files created**: `detect_brief-text_terse.md`
   and `detect_brief-text_verbose.md` as copies of updated Track 1
   terse/verbose files.
3. **Track 1 config JSONs created**: `library_plus-hp_terse.json` and
   `library_plus-hp_verbose.json` (plus-hp library, T=0.0, H5-B/C).
4. **Track 2 config JSONs created**: `detect_brief-text_terse.json`
   and `detect_brief-text_verbose.json` (Scale-8 metadata, T=0.0,
   `include_example_images: false`, H5-B/C).
5. **Track 1 study YAML rewritten**: `phase2d-h5-negtext.yaml`
   converted from 3×3 factorial to single-factor OFAT.
6. **Track 2 study YAML created**: `phase2d-h5-negtext-text-only.yaml`
   following the Phase 2b text-only pattern.
7. **Documentation**: E28 (protocol errata), Decision 17 (decisions
   log), H5 section update (hypothesis tracking), Phase 2d row
   (execution checklist).
8. **Validation**: Both study YAMLs pass dry-run (20 execution units
   each, all OK). Documentation files pass markdownlint (0 errors).
9. **End-of-session reflections**: Updated all reflection documents.

### Key Details

- **New cells**: 4 (2 per track) × K=10 × 60 tiles = 2,400 API calls
- **Estimated cost**: ~$6.90 ($4.40 Track 1 + $2.50 Track 2)
- **Reused baselines**: Phase 2c plus-hp (Track 1 minimal), Phase 2b
  Track 2 T=0.0 (Track 2 minimal)

### Issues

- None. Implementation plan was complete and accurate.
- System instruction files have pre-existing markdownlint violations
  (blank lines around headings/lists in exclusion criteria sections).
  Legacy debt from original prompt creation — not addressed in this
  session as these are VLM prompts where formatting changes could
  affect model behaviour.

### Commits

| Hash | Description |
|------|-------------|
| `b0d7dd0` | `feat(phase2d)`: dual-track H5 exclusion guidance setup |
| `b6f4600` | `docs(preregistration)`: Decision 17 and Erratum E28 for Phase 2d design |

### Pending Work

- [x] Phase 2d setup and execution configs (this session)
- [ ] **Phase 2d execution** — run Track 2 first (cheaper), then Track 1
- [ ] Phase 2d analysis — scoring pipeline, compare P/R/F1 across H5 levels
- [ ] Results write-up for plus-hp configuration
- [ ] Investigate `mound_count` metadata vs spatial scoping divergence
- [ ] Fix `test_tpm_governor.py::test_ramp_up_stability` (carried forward)
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF

---

## Session 32 — 2026-02-11

**Focus**: Phase 2d Track 1 (image-using) execution and analysis
**Duration**: ~35 minutes
**Instance**: Single instance, no compaction

### What Happened

Executed the Phase 2d Track 1 experiment (image-using detection with
H5 exclusion guidance) from a pre-approved plan. 20 execution units
(terse × 10, verbose × 10), each processing 60 tiles with 13 in-context
example images. All units completed on first pass with zero failures.

Committed and pushed both Track 2 (text-only, from prior session) and
Track 1 (this session) outputs and analysis results.

### Key Results

- **Track 1 (image-using)**: minimal F1=0.609, terse F1=0.571, verbose
  F1=0.578. No pairwise differences significant after FDR correction.
- **Cross-track comparison**: Exclusion guidance hurts both tracks, but
  Track 2 drop (-0.112) is ~3.6× larger than Track 1 drop (-0.031).
  Image examples buffer the harmful effect of exclusion text.
- **Perfect determinism**: terse=134, verbose=128 detections in every
  replicate at T=0.0.
- **Cost**: $1.99 actual vs $4.40 estimated (55% overestimate).

### Issues Encountered

- None. Clean execution, no API failures, no pipeline errors.

### Commits

| Hash | Description |
|------|-------------|
| `d656199` | `feat(phase2d)`: Track 2 text-only execution and analysis |
| `36bd5f2` | `feat(phase2d)`: Track 1 image-using execution and analysis |

### Pending Work

- [x] Phase 2d setup and execution configs (Session 31)
- [x] **Phase 2d execution** — Track 2 (Session 31) and Track 1 (this session)
- [x] Phase 2d analysis — scoring pipeline, compare P/R/F1 across H5 levels
- [ ] Phase 2d cross-track write-up integrating both tracks' findings
- [ ] Results write-up for plus-hp configuration
- [ ] Investigate `mound_count` metadata vs spatial scoping divergence
- [ ] Fix `test_tpm_governor.py::test_ramp_up_stability` (carried forward)
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF

---

## Session 33 — 2026-02-12

**Focus**: Phase 2e (H4 — Example Ordering) execution and analysis
**Duration**: ~4 hours (mostly API wait time; split across two context windows)
**Instance**: Two instances (context compaction mid-session)

### What Happened

Completed the full Phase 2e lifecycle: governor improvement, test fixes,
experiment execution, analysis, and documentation. This was the final
OFAT phase before Phase 3 validation.

The session began with infrastructure work — fixing the TPM governor's
429 handling — then pivoted to experiment execution. Mid-execution, we
discovered that K=10 replication at T=0.0 produces identical outputs for
fixed-ordering conditions, allowing 4 of the remaining 10 units to be
satisfied by copying existing outputs (documented as E31). API rate
limiting (Gemini returning 429s at 88–95% rate despite 5% quota usage)
was the primary bottleneck; one unit (random/run_2) timed out and
required retry after API conditions improved.

### Key Results

**H4 Ordering — No significant effect after FDR correction:**

| Condition | Ordering | F1 | 95% CI |
|-----------|----------|---:|:------:|
| config-default | [C+, HP, C−, null] | 0.609 | [0.485, 0.701] |
| canonical-last | [HP, null, C+, C−] | 0.609 | [0.529, 0.722] |
| canonical-first | [C+, C−, HP, null] | 0.579 | [0.463, 0.671] |
| random | shuffled per-run | 0.529 | [0.440, 0.616] |

- Two comparisons initially significant at α=0.05 (config-default vs
  random ΔF1=+0.067; canonical-last vs random ΔF1=+0.094) but neither
  survives Benjamini-Hochberg FDR correction across 6 comparisons.
- Fixed orderings outperform random, but specific ordering among fixed
  strategies has minimal effect.
- **Carry-forward**: config-default ordering (no change from prior phases).

**Infrastructure:**

- Governor now distinguishes intermittent 429s (API degradation, hold
  steady) from sustained 429s (genuine rate limiting, reduce concurrency).
  Requires ≥25% 429 rate and n≥2 to classify as rate limiting.
- All 34 governor tests pass (8 fixed, 1 new test added).
- Deterministic run optimisation saved ~$1 and several hours of API time.

### Issues Encountered

- **Governor spiralling**: Pre-fix governor reduced concurrency to 1 on
  any single 429, even at 5% quota usage. Fixed by rate-based threshold.
- **Test suite deadlocks**: safe_initial clamping reduced semaphore
  capacity below what thread tests tried to acquire. Fixed by adding
  explicit `tokens_per_request` to avoid clamping.
- **random/run_2 timeout**: First attempt timed out at 27/60 tiles due
  to 88–95% 429 rate during peak API load. Retried successfully after
  API conditions improved (33 tiles in 40 seconds).
- **Bootstrap mean ≠ point estimate**: Analysis recommendation reported
  bootstrap mean F1=0.631 for canonical-last, but point estimate is
  0.609. Tile-level resampling on zero-variance data introduces upward
  bias. Minor reporting inconsistency to address in analysis script.

### Commits

| Hash | Description |
|------|-------------|
| `7a038b6` | `docs(phase2e)`: errata E29/E30, Decision 18, execution plan updates |
| `fa3043f` | `fix(governor)`: distinguish intermittent 429s from genuine rate limiting |
| `8c292af` | `docs(phase2e)`: E31 deterministic run shortcut, observations 128–129 |
| `de6ac2e` | `feat(phase2e)`: H4 ordering experiment execution (40/40 units) |
| `8f34ed4` | `feat(phase2e)`: H4 ordering analysis — no significant effect after FDR |

### Pending Work

- [x] Phase 2e setup (Session 32.5)
- [x] Governor fix for 429 handling
- [x] **Phase 2e execution** — 40/40 units complete
- [x] Phase 2e analysis — bootstrap CIs, pairwise comparisons
- [x] Fix `test_tpm_governor.py::test_ramp_up_stability` (carried forward, fixed)
- [ ] Phase 2d cross-track write-up integrating both tracks' findings
- [ ] Fix bootstrap mean vs point estimate discrepancy in analysis script
- [ ] Results write-up for plus-hp configuration
- [ ] Investigate `mound_count` metadata vs spatial scoping divergence
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF
- [ ] **Phase 3 validation** — next major milestone

---

## Session 34 — 2026-02-12 (Phase 2b retroactive consensus voting analysis)

**Focus**: Retrospective consensus voting sweep on Phase 2b temperature data
**Duration**: ~1 hour
**Instance**: Two instances (context compaction mid-session)

### What Happened

Built and ran a retroactive consensus voting analysis on Phase 2b
temperature sweep data (5 temperatures × 10 runs = 50 detection sets,
zero additional API calls). The hypothesis was that aggregating multiple
runs via majority voting at elevated temperature might outperform the
best single-run T=0.0 result (F1=0.557). Created a standalone analysis
script, ran a full sweep of 75 configurations (5 temps × 2 pool sizes ×
variable thresholds), and discovered that consensus voting beats the
single-run baseline at every temperature.

A critical caveat emerged during interpretation: T=0.0 consensus results
(F1=0.657, the best overall) exploit run-to-run variation that only
exists in the canonical library used for Phase 2b. Phase 2c/2d/2e showed
that the current plus-hp library produces near-perfect determinism at
T=0.0, making consensus voting ineffective at that temperature. The
actionable finding is therefore restricted to T≥0.3.

### Key Results

**Consensus voting improves over single-run baseline at all temperatures:**

| Temp | Best N | Best x | F1 | ΔF1 vs baseline |
|------|-------:|-------:|----:|----------------:|
| T0.0 | 5 | 4 | 0.657 | +0.099 |
| T0.3 | 10 | 8 | 0.642 | +0.085 |
| T0.7 | 10 | 6 | 0.619 | +0.061 |
| T1.0 | 10 | 6 | 0.605 | +0.048 |
| T1.3 | 10 | 5 | 0.586 | +0.029 |

**Actionable findings for Phase 3a** (excluding T=0.0):

- **T=0.3 is the optimal consensus temperature**: F1=0.642 at N=10 x=8,
  with optimal threshold x=8 indicating strong inter-run agreement
- **Pool size has diminishing returns**: T0.3 N=5 x=4 (F1=0.639) vs
  N=10 x=8 (F1=0.642) — only +0.003 from doubling the pool
- **Consensus primarily filters false positives**: detection counts drop
  from ~229 (x=1) to ~93 (x=8) at T=0.3, with precision rising from
  0.34 to 0.66 while recall drops from 0.79 to 0.63
- **Plus-hp single-run baseline (F1=0.609) is already close**: best
  Phase 2b consensus (0.642) exceeds it by only +0.033, suggesting
  modest but real headroom for consensus on plus-hp data

**Mechanism insight**: consensus voting works as a noise-reduction tool
(filtering inconsistent FPs) rather than a diversity exploiter (capturing
complementary TPs). Lower temperatures produce better consensus because
consistent high-confidence detections matter more than coverage of
diverse hypotheses.

### Accomplishments

1. **Created `scripts/analyse_consensus_sweep.py`** — standalone script
   combining functions from `merge_passes.py` (spatial clustering),
   `analyse_phase2_results.py` (data loading), and
   `lib_advanced_metrics.py` (F1 evaluation with bootstrap CIs).
   Parallelised evaluation across 75 configurations using
   ProcessPoolExecutor.
2. **Ran full analysis** — 75 configurations × 1000 bootstrap iterations
   in ~8 seconds. All results with 95% CIs.
3. **Generated output files** in `results/phase2b-consensus/`:
   - `consensus-sweep-results.csv` — full 75-row results table
   - `consensus-analysis-report.json` — structured results with metadata
   - `consensus-analysis-summary.md` — human-readable summary
4. **Added T=0.0 non-transferability caveat** — edited summary to
   document that T=0.0 consensus results depend on canonical library's
   run-to-run variation, which doesn't exist in plus-hp. Reframed the
   key finding to focus on T=0.3.
5. **Cross-library comparison** — compared Phase 2b consensus results
   against plus-hp single-run baseline (mean F1=0.609 from Phase
   2c/2d/2e), establishing the +0.033 headroom estimate.

### Issues

- **T=0.0 determinism artefact**: Initial results highlighted T=0.0 as
  the best consensus temperature. User correctly flagged that plus-hp
  achieves near-perfect determinism at T=0.0, making this result
  non-transferable. The improvement mechanism (filtering across 4 unique
  run patterns) doesn't exist in plus-hp (only 2 patterns, and those
  differ only due to minor API non-determinism).
- **Script re-run would overwrite caveat**: The `generate_summary_md()`
  function in the script still generates the original key finding text
  without the caveat. If re-run, the manually-added caveat would be
  lost. Not yet fixed programmatically.

**Spatial tolerance sensitivity analysis** (post-compaction):

After the consensus analysis, the user requested a tolerance sensitivity
check before committing to Phase 3a. Created
`scripts/analyse_tolerance_sensitivity.py` — iterates over all 33 Phase
2 conditions and computes F1/precision/recall at 10, 20, 30, 40, and
50m buffer sizes using the existing `spatial_tolerance_curve()` function.

Key findings:

| Tolerance | Plus-hp F1 | Text-only T0.0 F1 | Plus-hp rank |
|-----------|-----------|-------------------|--------------|
| 10m | 0.323 | 0.506 | ~15th |
| 20m | 0.620 | 0.658 | 3rd-5th |
| 30m | 0.716 | 0.700 | 1st-3rd |
| 40m | 0.751 | 0.709 | 1st-3rd |
| 50m | 0.769 | 0.726 | 1st-3rd |

The carry-forward configuration holds its ranking or improves across all
tolerances. At 50m (10 pixels, ~3-4 px from symbol edge given 14-16 px
mound symbols), F1=0.769 — competitive with traditional CV approaches.

The user noted that 20m is appropriate for internal optimisation but
30-40m is fair for paper reporting given the symbol geometry. At these
tolerances, single-run F1 is already 0.716-0.751, and consensus voting
could push beyond 0.80.

**Phase 3a planning** (in progress):

Drafted a Phase 3a plan: K=30 runs at T=0.3 and T=0.7 with plus-hp
configuration, deriving N=5, N=10, and N=30 from the same runs.
3,600 API calls, ~$6-8 estimated cost. Contingent T=1.0 if results
suggest higher temperature + larger N could help. Plan saved but not
yet approved — session ended for context clearing.

### Accomplishments (continued)

6. **Created `scripts/analyse_tolerance_sensitivity.py`** — spatial
   tolerance sweep across all 33 Phase 2 conditions at 5 buffer sizes
7. **Generated tolerance sensitivity outputs** in
   `results/tolerance-sensitivity/`:
   - `tolerance-sensitivity.csv` — 165-row results table
   - `tolerance-sensitivity.json` — structured results
8. **Drafted Phase 3a plan** — K=30 at T=0.3/T=0.7 with plus-hp,
   erratum E32 for temperature deviation, saved to plan file

### Commits

None yet — all new files are unstaged.

### Pending Work

- [ ] Commit consensus voting analysis script and results
- [ ] Commit tolerance sensitivity script and results
- [ ] **Phase 3a execution** — approve plan and run (3,600 API calls)
- [ ] Phase 2d cross-track write-up integrating both tracks' findings
- [ ] Fix bootstrap mean vs point estimate discrepancy in analysis script
- [ ] Results write-up for plus-hp configuration
- [ ] Investigate `mound_count` metadata vs spatial scoping divergence
- [ ] SDK migration: `scripts/5_verify_crops.py` still uses deprecated SDK
- [ ] Upload Phase 1 materials to OSF

## Session 35 — 2026-02-14 (Write-ahead checkpoint for batch API)

**Focus**: Implementing the write-ahead checkpoint pattern for
crash-safe batch job recovery, plus archiving the superseded
TPMGovernor.

**Mode**: Infrastructure / fault tolerance. No API calls, no
experimental data.

### Accomplishments

1. **Implemented write-ahead checkpoint** in `lib_batch_api.py` — added
   `on_submit` callback and `resume_job_name` parameters to
   `run_batch_unit()` (~30 lines)
2. **Wired resume logic** in `run_phase2.py` — added `_make_on_submit()`
   factory function and pending job detection in `_execute_units_batch()`
   (~25 lines)
3. **Added 5 tests** for write-ahead checkpoint behaviour in
   `test_batch_api.py` — callback invocation, resume skips
   upload/submit, dry-run safety, poll timeout on resume
4. **Updated documentation** — crash recovery notes in `architecture.md`
   and `pipelines.md`
5. **Archived `TPMGovernor`** — moved `lib_tpm_governor.py` and
   `test_tpm_governor.py` to `archive/deprecated-scripts/`, eliminating
   5 failing tests + 2 fixture errors from tier1 suite

### Verification

- `ruff check` — all checks passed
- `pytest tests/test_batch_api.py` — 46/46 passed (41 existing + 5 new)
- `pytest tests/ -m tier1` — 432 passed, 5 failed + 2 errors
  (all pre-existing TPMGovernor/Phase3a YAML drift, resolved by
  archiving TPMGovernor)
- `markdownlint-cli2` — 0 errors on modified docs

### Commits

- `2a5ffbe` — `feat(batch): write-ahead checkpoint for crash-safe job recovery`
- `ef6f133` — `chore: archive superseded TPMGovernor and its tests`

### Issues

- **Dry-run test initially failed**: The test for "on_submit not called
  in dry run" omitted the `_resolve_tile_paths` mock, causing
  `run_batch_unit()` to return "no_tiles_found" before reaching the
  dry-run check. Fixed by adding the mock.

### Pending Work

- [ ] Fix Phase 3a YAML fixture rename in `test_phase2_configs.py`
  (references `phase3a-h3-voting.yaml` which was split into track1/track2)
- [ ] Commit remaining unstaged files: `lib_token_bucket.py`,
  `test_token_bucket.py`, `4_detect_mounds_batch.py`, `scripts/README.md`,
  `uv.lock`
- [ ] Phase 3a execution — approve plan and run (3,600 API calls)
- [ ] Phase 2d cross-track write-up integrating both tracks' findings

---

## Session 36 — 2026-02-14 (Track 1 consensus analysis, Track 2 batch launch, statistical power investigation)

**Focus**: Running the full Track 1 consensus sweep, launching Track 2
batch execution, and investigating statistical significance of
consensus improvements through power analysis and paired permutation
tests.

**Mode**: Analysis and execution. Gemini Batch API calls for Track 2,
statistical analysis for Track 1.

**Instance boundary note**: This session continued from a compacted
Session 35b. The Track 1 reconciliation and Track 2 batch setup were
completed in the pre-compaction portion; the analysis and reflection
work is from direct experience post-compaction.

### Accomplishments

1. **Ran Track 1 consensus sweep** — 135 configurations (3 temperatures
   × 3 pool sizes × 15 thresholds), all 90 runs confirmed via
   `--reconcile`. Best: T0.3 N=30 x=25 → F1=0.6444 (+0.035 over
   baseline 0.609)
2. **Tolerance sensitivity analysis** — evaluated top 5 at 20m, 30m,
   40m, 50m; T0.7 N=30 x=14 overtakes at wider tolerances (F1=0.792
   at 50m). Rankings are tolerance-robust overall
3. **Pool size comparison** — N=5 fails to beat baseline, N=10 barely
   beats it (+0.007), N=30 provides substantial gain (+0.035).
   Non-linear activation threshold around N=20–25
4. **Statistical significance assessment** — no individual improvements
   statistically significant under unpaired bootstrap (CIs ~0.20 wide)
5. **Power analysis** — ~400 tiles for just-significant, ~900 for 80%
   power at observed effect size. 280 additional ground-truthed tiles
   available but preregistration constraints may apply
6. **Paired permutation test** — T0.3 N=30 x=25 reaches p=0.055
   (borderline). T0.7 N=30 x=14 shows Simpson's paradox (p=0.363,
   losing on 20/60 tiles despite global improvement)
7. **Launched Track 2 batch run** — 70 units submitting via Gemini
   Batch API, overnight monitor configured
8. **Added Observation 134** to working-notes.md — Batch API discovery
   and reactive-vs-proactive framing insight (with CC perspective)

### Key Results

| Config | F1 (20m) | ΔF1 | Paired p | Wins:Losses |
|--------|----------|------|----------|-------------|
| T0.3 N=30 x=25 | 0.6444 | +0.035 | 0.055 | 25:18 |
| T0.3 N=30 x=22 | 0.6435 | +0.035 | 0.081 | — |
| T0.7 N=30 x=14 | 0.6377 | +0.029 | 0.363 | 16:20 |
| T0.3 N=10 x=8 | 0.6161 | +0.007 | — | — |
| T0.7 N=5 x=3 | 0.6047 | −0.004 | — | — |

### Commits

- None this session (analysis and execution only, uncommitted changes
  carried forward from Session 35)

### Issues

- **TypeError on tolerance analysis**: `load_condition_results()` takes
  `(study_dir, condition)` not `target_crs` kwarg. Fixed inline.
- **Track 2 first batch stuck in PENDING**: First unit
  (`batches/tl1yx9hwkhxkr1ow2mfkkx0cyfz7hd27ngi4`) polling for extended
  period. Monitor script checking hourly.

### Pending Work

- [ ] Track 2 batch completion and consensus analysis (monitor running)
- [ ] Commit run_phase2.py and lib_batch_api.py changes (from Session 35)
- [ ] Apply paired permutation test to Phase 2b retroactive analysis
- [ ] Apply paired permutation test to Track 2 results when available
- [ ] Commit lib_token_bucket.py, test_token_bucket.py, and other
  unstaged files
- [ ] Fix Phase 3a YAML fixture rename in test_phase2_configs.py
- [ ] Evaluate whether 280 additional tiles can expand validation set
  within preregistration constraints

## Session 37 — 2026-02-15 (Discovery vs exploitation pattern, /review-implementation skill)

### Overview

Meta-reflective session with no code execution or experiment runs. The user
arrived with a pattern observed across Sessions 35–36: the Batch API discovery
(AI-led, via capability scanning) and the concurrency optimisation (human-led,
via noticing serial execution). Together these illustrated two distinct
collaboration failure modes — discovery failure (not knowing a capability exists)
and exploitation failure (implementing a capability conservatively without using
the full envelope). The session produced three operationalised interventions.

### Accomplishments

1. **Observation 137 in working-notes.md** — documented the two-stage
   discovery/exploitation pattern with concrete examples (Batch API, paired
   permutation tests), CC perspective on why the exploitation failure occurred,
   and a proposed three-step protocol (capability scan → exploitation review →
   quantitative audit)
2. **Global CLAUDE.md "Implementation and Methodology Review" section** — four
   passive, always-on checks: compute aggregate implications, check capacity
   envelope, flag conservative defaults, survey solution space in non-expert
   domains
3. **`/review-implementation` skill** — structured four-phase protocol
   (capability scan → exploitation review → quantitative audit → recommendation)
   with domain-specific checklists for APIs, statistics, data pipelines, and
   experimental design. Located at `~/.claude/skills/review-implementation/`
4. **`~/personal-assistant/notes/llm-craft.md` entry** — human-facing prompting
   protocol documenting the two habits (capability scan before committing,
   exploitation review after implementing) with the statistical methodology
   generalisation
5. **Memory captured** — decision memory documenting the three-layer defence

### Key Results

- No quantitative results this session (meta-reflective work only)
- The generalisation from API usage to statistics (paired permutation tests)
  validated that the pattern applies across domains, not just to API integrations

### Commits

- None this session (changes to CLAUDE.md and skill are outside the repository;
  working-notes.md changes uncommitted)

### Issues

- None

### Pending Work

- [ ] Carry forward all pending items from Session 36
- [ ] Test whether the passive CLAUDE.md instruction changes CC behaviour in
  practice vs requiring explicit `/review-implementation` invocation
- [ ] Consider adding `/review-implementation` invocation to phase-boundary
  checklists in execution plan

## Session 38 — 2026-02-15 (Phase 3a re-run with MINIMAL thinking, operational failures)

**Instance boundary note**: This session continued from a compaction
summary. Content below covers the full session but earlier phases are
reconstructed from the summary.

### Overview

Continuation session to clean up uncommitted work from Sessions 35–37,
then re-run Phase 3a batch jobs with corrected `thinking_level=MINIMAL`
(fixing the protocol deviation discovered in Session 37 where all 180
jobs ran with HIGH thinking). The re-run hit a cascade of operational
failures: wrong Python environment, disk space exhaustion, and Batch API
quota limits.

### Accomplishments

1. **Committed and pushed 7 commits** spanning Sessions 35–38:
   - `cb3f0c1` — `--poll-interval` and `--max-poll-hours` CLI flags
   - `24abf81` — standalone `batch-monitor.py` script
   - `6081c36` — `thinking_config` fix in batch JSONL output
   - `57f631e` — TokenBucketGovernor replacing TPMGovernor
   - `0ef38d8` — gitignore `outputs/phase3a/` (2.5GB)
   - `d129ccc` — Phase 3a consensus results + `uv.lock`
   - `a7baa41` — Sessions 35–37 reflections and observations
2. **Preserved HIGH-thinking runs** by renaming output directories
   (`track1-image-high`, `track2-text-high`) before re-running
3. **Launched MINIMAL-thinking batch runs** for both tracks
4. **Track 2**: 63/90 batch jobs submitted, 13+ already completed,
   27 failed submission (quota exhausted), polling in progress
5. **Track 1**: 22/90 batch jobs submitted, 4 SUCCEEDED + 18 PENDING,
   14 failed submission (quota exhausted), polling in progress
6. **Set up hourly monitoring** with `batch-monitor.py --watch`
   (fixed stdout buffering with `PYTHONUNBUFFERED=1`)
7. **Processed pending `/remember`** for paired permutation test
   methodology insight

### Key Results

- No scientific results yet — batch jobs still running
- Both tracks partially submitted; `--resume` needed after current
  jobs complete to submit remaining 68 (Track 1) + 27 (Track 2) units

### Commits

- `57f631e` through `a7baa41` — 7 commits covering Sessions 35–38
  (see Accomplishments above for breakdown)

### Issues

1. **Disk space exhaustion**: 944GB disk was 95% full; image-track JSONL
   preparation (90 × 160MB = 14GB) pushed it to 100%. Fixed by user
   emptying trash (~100GB freed)
2. **Batch API quota**: Concurrent job limit (~80–90 active jobs) caused
   `429 RESOURCE_EXHAUSTED` after ~85 submissions across both tracks.
   Write-ahead checkpoint ensures safe recovery via `--resume`
3. **Python stdout buffering**: `batch-monitor.py` produced no output as
   background process. Fixed with `PYTHONUNBUFFERED=1` environment variable
4. **Wrong Python**: First attempt used system Python (missing
   `google-genai`); fixed by using `.venv/bin/python3`

### Pending Work

- [x] Commit and push all outstanding changes (7 commits)
- [x] Rename HIGH-thinking output directories for preservation
- [x] Launch MINIMAL-thinking batch runs
- [ ] `--resume` Track 1 when current 22 jobs complete (68 remaining)
- [ ] `--resume` Track 2 when current 63 jobs complete (27 remaining)
- [ ] Consensus analysis on MINIMAL-thinking results (both tracks)
- [ ] Comparative analysis: HIGH vs MINIMAL thinking level effect
- [ ] Apply paired permutation test to Phase 2b retroactive analysis
- [ ] Fix Phase 3a YAML fixture rename in test_phase2_configs.py
- [ ] Consider adding `sys.stdout.reconfigure(line_buffering=True)` to
  `batch-monitor.py` for intrinsic unbuffered output
- [ ] Evaluate whether 280 additional tiles can expand validation set

---

*New session entries should be appended above this line.*
