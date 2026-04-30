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
- [x] `--resume` Track 2 when current 63 jobs complete (27 remaining) — completed 90/90 (2026-02-15)
- [ ] `--resume` Track 1 when current 22 jobs complete (68 remaining) — in progress (34 completed + 41 pending, governance active)
- [x] Consensus analysis on MINIMAL-thinking results — Track 2 complete (2026-02-15); Track 1 pending (awaiting 90/90)
- [ ] Comparative analysis: HIGH vs MINIMAL thinking level effect — preliminary comparison in Obs 140; formal paired test pending
- [ ] Run T × thinking-level factorial within consensus framework — test whether
  temperature and thinking level are additive or substitutable diversity sources
  (motivated by Obs 140: both axes increase stochasticity through independent
  mechanisms, but may saturate the same diversity ceiling)
- [ ] Apply paired permutation test to Phase 2b retroactive analysis
- [ ] Fix Phase 3a YAML fixture rename in test_phase2_configs.py
- [ ] Consider adding `sys.stdout.reconfigure(line_buffering=True)` to
  `batch-monitor.py` for intrinsic unbuffered output
- [ ] Evaluate whether 280 additional tiles can expand validation set

---

## Session 39 — 2026-02-16 (File governance deployment, consensus comparison, diversity dividend)

**Instance boundary note**: This session is a continuation from a
compacted summary. The commit/push and initial background task setup
are reconstructed; the consensus analyses, comparative write-up, and
reflections are genuine first-person experience.

### Overview

Deployed the file storage governance code (committed in Session 38.5
as two logical commits), monitored background batch processing for
both tracks, ran consensus analyses on three completed tracks
(Track 2 MINIMAL, Track 1 Image HIGH, Track 2 Text HIGH), and
discovered that HIGH thinking dramatically outperforms MINIMAL for
consensus voting — the diversity dividend (Obs 140).

### Accomplishments

1. **Committed and pushed file storage governance** in two logical
   commits:
   - `edc798d` — library layer: `cleanup_batch_files()`,
     `audit_file_storage()`, `sweep_stale_files()`, modified
     `submit_batch_unit()` return type
   - `d3d6e1b` — pipeline integration: checkpoint tracking of
     `uploaded_file_name`, completion cleanup, retry-with-sweep,
     plus 15 new tests (77/77 passing)
2. **Track 2 MINIMAL completed**: 90/90 units, 0 failures. File
   governance confirmed working — input files deleted successfully,
   output file deletion fails universally due to bug #1759 (file ID
   > 40 chars), auto-expires in 48h
3. **Ran three consensus analyses** in parallel:
   - Track 2 Text MINIMAL: best F1=0.6832 (T1.0 N=30 x=22)
   - Track 1 Image HIGH: best F1=0.6444 (T0.3 N=30 x=25)
   - Track 2 Text HIGH: best F1=0.7513 (T0.7 N=30 x=22)
4. **Discovered the diversity dividend** (Obs 140): HIGH thinking
   generates 3–4× more detection clusters than MINIMAL, giving
   consensus voting richer signal to filter. HIGH consensus
   outperforms MINIMAL by +6.8 pp F1 on Track 2
5. **Wrote Observation 140** documenting the finding, the pilot
   blind spot, and the bias-variance trade-off mechanism
6. **Added to-do** for T × thinking-level factorial experiment

### Key Results

| Track | Thinking | Best Config | Best F1 | Baseline | Delta |
|-------|----------|-------------|---------|----------|-------|
| Track 2 Text | MINIMAL | T1.0 N=30 x=22 | 0.6832 | 0.660 | +0.023 |
| Track 2 Text | HIGH | T0.7 N=30 x=22 | 0.7513 | 0.660 | +0.091 |
| Track 1 Image | HIGH | T0.3 N=30 x=25 | 0.6444 | 0.609 | +0.035 |
| Track 1 Image | MINIMAL | *(34/90)* | — | 0.609 | — |

### Commits

- `edc798d` — `feat(batch-api): add file storage governance functions`
- `d3d6e1b` — `feat(pipeline): integrate file cleanup and quota retry`

### Issues

1. **Bug #1759 confirmed universal**: All batch output file IDs exceed
   40-char limit for `files.delete()`. Input file deletion works
   correctly (1 per unit). Output files auto-expire in 48h — acceptable
   fallback
2. **Track 1 MINIMAL still in progress**: 34 completed + 41 pending
   as of session end. Will need additional `--resume` cycle(s)

### Pending Work

- [x] Track 1 MINIMAL: complete remaining ~56 units via `--resume` — completed 90/90 (2026-02-16)
- [x] Re-run Track 1 MINIMAL consensus analysis once 90/90 complete — completed (2026-02-16): best F1=0.6497 (T0.7 N=10 x=6)
- [ ] Paired permutation test: HIGH vs MINIMAL (Track 2) for formal
  statistical comparison
- [x] Full 2×2 comparison (Image/Text × HIGH/MINIMAL) — completed (2026-02-16): academic draft in `results/phase3a-consensus/phase3a-thinking-level-comparison.md`
- [ ] Run T × thinking-level factorial within consensus framework
- [ ] Apply paired permutation test to Phase 2b retroactive analysis
- [ ] Fix Phase 3a YAML fixture rename in test_phase2_configs.py

---

## Session 40 — 2026-02-16 (Academic draft: 2×2 thinking-level comparison)

**Instance boundary note**: Continuation from compacted context. The
Track 1 MINIMAL completion and 2×2 comparison analysis occurred before
compaction. The academic document writing is genuine first-person
experience.

### Overview

Created a formal academic-style draft document capturing the full 2×2
(modality × thinking level) Phase 3a consensus analysis, suitable for
inclusion in the paper. The document covers H3 confirmation, the
modality-specific diversity dividend, and mechanistic interpretation.

### Accomplishments

1. **Completed Track 1 Image MINIMAL analysis**: 90/90 units completed,
   consensus sweep run. Best F1=0.6497 (T0.7 N=10 x=6, +0.041 vs
   baseline 0.609)
2. **Ran full 2×2 comparison** across all four conditions, identifying
   the modality-specific interaction: Track 2 Text shows +6.8 pp
   advantage for HIGH thinking; Track 1 Image shows negligible difference
3. **Wrote academic draft document**: 6 sections plus appendices at
   `results/phase3a-consensus/phase3a-thinking-level-comparison.md`:
   - Section 3: Five data tables (global optima, interaction summary,
     per-temperature optima, cluster diversity, precision-recall)
   - Section 4: Discussion of H3 confirmation, modality-specific
     diversity dividend, calibration methodology implications,
     temperature-thinking interaction, and cross-modality gap
   - Section 5: Limitations (power, single model, post-hoc status)
4. **Markdown lint**: Document passes clean

### Key Results

Complete 2×2 comparison:

| Track | Thinking | Best Config | Best F1 | Baseline | Delta |
|-------|----------|-------------|---------|----------|-------|
| Track 1 Image | MINIMAL | T0.7 N=10 x=6 | 0.6497 | 0.609 | +0.041 |
| Track 1 Image | HIGH | T0.3 N=30 x=25 | 0.6444 | 0.609 | +0.035 |
| Track 2 Text | MINIMAL | T1.0 N=30 x=22 | 0.6832 | 0.660 | +0.023 |
| Track 2 Text | HIGH | T0.7 N=30 x=22 | 0.7513 | 0.660 | +0.091 |

### Commits

*(No commits this session — document creation only)*

### Issues

None.

### Pending Work

- [ ] Paired permutation test: HIGH vs MINIMAL (Track 2) for formal
  statistical comparison
- [ ] Paired permutation test: HIGH vs MINIMAL (Track 1) to confirm
  null effect on image modality
- [ ] Run T × thinking-level factorial within consensus framework
- [ ] Apply paired permutation test to Phase 2b retroactive analysis
- [ ] Fix Phase 3a YAML fixture rename in test_phase2_configs.py
- [ ] Commit academic draft document and session reflections

## Session 41 — 2026-02-16: Spatial tolerance sensitivity and comprehensive report

### Overview

Fresh instance after Session 40 crashed with context length error.
Resumed Phase 3a spatial tolerance analysis from on-disk artefacts.
All 16 analyses (4 conditions × 4 tolerances) were already complete;
this session focused on extraction, synthesis, and documentation.

### Work Completed

1. **Verified completeness**: Confirmed all 16 consensus analysis
   report JSON files exist with valid data
2. **Created spatial tolerance sensitivity document**:
   `results/phase3a-consensus/phase3a-spatial-tolerance-sensitivity.md`
   — analyses how F1 changes as evaluation buffer widens from 20→50 m
3. **Created comprehensive results report**:
   `results/phase3a-consensus/phase3a-comprehensive-results-report.md`
   — consolidates all three analytical dimensions (temperature ×
   thinking level × spatial tolerance) with quotable results for
   paper drafting
4. **Updated working notes**: Added Observations 142–145 covering
   image-track spatial imprecision, configuration stability as
   robustness diagnostic, thinking-level persistence across
   tolerances, and image-track convergence at 50 m
5. **Checked next experiment readiness**: Phase 3c (H9 Diversity) is
   next; prompt variants are designed (V1–V5 in prompts/README.md)
   but instruction files not yet created
6. **Updated reflections**: Session reflection, LLM observations,
   session log

### Key Results

Full 4×4 matrix (condition × tolerance):

| Condition | 20 m | 30 m | 40 m | 50 m |
|-----------|------|------|------|------|
| T1 Img MIN | 0.650 | 0.734 | 0.785 | 0.794 |
| T1 Img HIGH | 0.644 | 0.726 | 0.775 | 0.794 |
| T2 Txt MIN | 0.683 | 0.753 | 0.782 | 0.782 |
| T2 Txt HIGH | 0.751 | 0.804 | 0.821 | 0.831 |

Key findings:
- Image tracks gain 14–15 pp from 20→50 m (spatial imprecision)
- Text tracks gain 8–10 pp (better localisation)
- Thinking-level interaction robust across all tolerances
- Text MINIMAL plateaus at 40 m; image conditions converge at 50 m

### Commits

*(No commits this session — document creation only)*

### Issues

- Subagent Task tool summarised instead of returning raw data
  (twice) — required fallback to direct Bash execution

### Pending Work

- [ ] Create H9 prompt variant instruction files (V1–V5)
- [ ] Scaffold Phase 3c study configs and submit batch job
- [ ] Commit spatial tolerance and comprehensive report documents
- [ ] Paired permutation tests (carried forward from Session 40)
- [ ] Fix Phase 3a YAML fixture rename in test_phase2_configs.py

## Session 42 — 2026-03-08: Phase 3c diversity analysis, batch throttling, and variance stabilisation

### Overview

Full-cycle Phase 3c session: infrastructure improvement (batch throttling),
data collection monitoring, analysis script development, execution on
both tracks, comprehensive results write-up, and formal variance testing.
The primary H9 hypothesis (diversity improves consensus F1) was null, but
a significant secondary finding — variance stabilisation via image
diversity — changed the carry-forward decision.

**Instance note**: Reflection written by continuation instance from
compacted summary.

### Work Completed

1. **Batch API concurrency throttling**: Replaced sequential submit-all /
   poll-all pattern in `run_phase2.py` with interleaved submit+poll loop.
   Added `--max-batch-jobs` CLI flag (default 50, hard cap 95). Preserves
   all checkpoint, error handling, and resume semantics
2. **Built `analyse_diversity.py`**: ~700-line analysis script for Phase 3c
   consensus diversity evaluation. Reuses clustering/evaluation primitives
   from `merge_passes.py` and `lib_advanced_metrics.py`. Includes paired
   permutation test, bootstrap CIs, and configurable vote threshold sweep
3. **Retried 4 failed Track 2 tiles**: All Elenovo sheet tiles that failed
   via Batch API were successfully re-run via real-time API and patched
   into the output directory
4. **Monitored Track 1 completion**: Set up cron-based monitoring (30-min
   interval) that auto-triggered analysis when 125/125 units completed
5. **Ran diversity analysis on both tracks**: Track 1 (5 conditions ×
   5 replications) and Track 2 (4 conditions × 5 replications, C omitted
   as degenerate for text-only)
6. **Wrote comprehensive results report**:
   `results/phase3c-diversity/phase3c-comprehensive-results-report.md`
   — 10 sections matching Phase 3a report format
7. **Formal variance testing**: Added multiple variance tests (F-test,
   Bartlett's, Levene's, permutation) to assess Condition C's SD reduction.
   Permutation test p=0.032 confirmed statistical significance
8. **Updated carry-forward decision**: Condition C adopted for image track
   (variance stabilisation); identical passes for text-only track

### Key Results

**Primary (H9 — mean F1)**:

| Track | Baseline F1 | Best Diversity F1 | ΔF1 | p-value | Significant? |
|-------|-------------|-------------------|-----|---------|:------------:|
| Track 1 Image (A vs D) | 0.644 | 0.658 | +0.014 | 0.626 | No |
| Track 2 Text (A vs B) | 0.703 | 0.668 | −0.035 | 0.121 | No |

H9 not supported on either track. All 9 pairwise comparisons non-significant.

**Secondary (variance stabilisation)**:

| Condition | SD (Track 1) | Variance test p |
|-----------|-------------|-----------------|
| A (baseline) | 0.041 | — |
| C (HN rotation) | 0.008 | 0.032 (permutation) |

23× variance reduction, statistically significant at α=0.05.

### Commits

- `d3d6e1b feat(pipeline): integrate file cleanup and quota retry`
- `edc798d feat(batch-api): add file storage governance functions`

### Issues

- 1 JSON parse error in Track 1 (h9-C-img4/run_3, tile K-35-052-4) —
  handled gracefully, unit completed with 60 tiles
- File cleanup errors for 2 batch output files ("File ID cannot be more
  than 40 characters") — non-blocking, files auto-expire after 48h
- 4 Track 2 tile failures required real-time API retry — all patched
  successfully but meta.json files overwritten with single-tile metadata

### Pending Work

- [ ] Commit Phase 3c results and analysis script
- [ ] Commit batch throttling changes to run_phase2.py
- [ ] Commit reflection updates
- [ ] Phase 3d preparation (next experimental phase)
- [ ] Paired permutation tests from Session 40 (carried forward)
- [ ] Fix Phase 3a YAML fixture rename in test_phase2_configs.py

## Session 43 — 2026-03-09 (H2 two-stage pilot recovery and evaluation, Phase 2e documentation)

**Focus**: Recovering overnight pilot that hung, evaluating two-stage
pipeline results, writing up Phase 2e carry-forward and pilot results
**Duration**: ~2 hours (continuation from Session 42)
**Instance**: Continuation instance (context compaction mid-session)

**Instance boundary note**: Pilot was designed and launched by the
previous instance. This instance diagnosed the hung process, recovered
track 1 results, restarted track 2, evaluated all results, and wrote
both the Phase 2e carry-forward and Phase 3d pilot results reports.

### Accomplishments

1. **Diagnosed and recovered hung pilot**: Process alive 12+ hours after
   launch due to stdout buffering + API stall. Discovered track 1 had
   completed successfully (3 verifier probability files saved). Killed
   process, restarted track 2 with `PYTHONUNBUFFERED=1`
2. **Evaluated track 1 results**: All three verifier strategies beat
   baseline by +0.086 to +0.091 F1. Standard and checklist identical at
   optimal threshold (F1=0.706); adversarial slightly better (F1=0.711)
3. **Completed track 2**: 420 API calls completed in ~28 minutes. Even
   larger improvements (+0.110 to +0.138 F1). Adversarial best (F1=0.796)
4. **Wrote Phase 3d pilot results report**:
   `results/phase3d-pilot-results.md` — full write-up with threshold
   sensitivity, cross-track comparison, strategy analysis, go/no-go
5. **Wrote Phase 2e carry-forward document** (retrospective):
   `results/phase2e-carry-forward-parameters.md` — fills documentation
   gap from Session 33 (25 days overdue)
6. **Added Observation 150**: User's surprise at two-stage efficacy,
   pattern of confounded expectations across the project
7. **Completed reflections**: All five reflection documents updated

### Key Results

**H2 Two-Stage Pilot — Track 1 (Image)**:

| Condition | F1 | ΔF1 | Precision | Recall |
|---|---|---|---|---|
| A (baseline) | 0.620 | — | 0.538 | 0.732 |
| B (standard) | 0.706 | +0.086 | 0.683 | 0.732 |
| C (adversarial) | 0.711 | +0.091 | 0.711 | 0.711 |
| D (checklist) | 0.706 | +0.086 | 0.683 | 0.732 |

**H2 Two-Stage Pilot — Track 2 (Text-only)**:

| Condition | F1 | ΔF1 | Precision | Recall |
|---|---|---|---|---|
| A (baseline) | 0.658 | — | 0.557 | 0.804 |
| B (standard) | 0.768 | +0.110 | 0.785 | 0.753 |
| C (adversarial) | 0.796 | +0.138 | 0.809 | 0.784 |
| D (checklist) | 0.782 | +0.124 | 0.770 | 0.794 |

**Go/no-go**: GO — all conditions exceed ≥0.05 ΔF1 stopping criterion
by wide margin.

### Commits

*(No commits this session — pending user review of results)*

### Issues

- **Pilot hung overnight**: stdout buffering hid progress; API stall
  on track 2 transition. Fixed with `PYTHONUNBUFFERED=1`. Track 1
  results recovered from output files despite silent console
- **Monitoring gap**: `/loop` cron was for Phase 3c, not the pilot.
  No automated monitoring caught the stall

### Pending Work

- [ ] Commit new files (verifier instructions, pilot script, results,
  Phase 2e carry-forward, reflections)
- [ ] Design full Phase 3d experiment based on pilot findings
- [ ] User has extension ideas for the two-stage experiment
- [ ] Fix Phase 3a YAML fixture rename in test_phase2_configs.py
  (carried forward)

---

## Session 44 — 2026-03-10 (Extended pilot analyses, cross-modal union planning)

**Instance note**: Continuation instance; reconstructed from summary.

### Focus

Three zero-cost analyses on existing Phase 3d pilot data, followed by
design discussion and experiment planning for the cross-modal union
proposer + adversarial verifier pipeline.

### Key Outcomes

1. **P-R curve analysis**: Fine-grained threshold sweep (0.01 steps)
   confirmed adversarial verifier optimal at t=0.21 (image) and t=0.16
   (text). Standard/checklist verifiers produce step-function curves
   (bimodal probability distributions). AUC-PR values are low due to
   narrow recall range, not poor classification.

2. **Cross-modal overlap analysis**: Union of image + text proposer
   tracks achieves 0.866 recall (84/97 mounds) vs 0.804 text-only or
   0.732 image-only. False positives are largely independent (20/62
   co-occur). Post-verification, union recall stays at 0.866 while
   Jaccard drops (0.774→0.655), meaning verification amplifies
   complementarity.

3. **Multi-verifier ensemble**: Standard and checklist verifiers are
   100% identical on image track, 93.6% on text. Best ensemble adds
   only +0.007 F1 over adversarial alone. Not worth pursuing.

4. **Union experiment plan**: Designed and saved to
   `~/.claude/plans/eager-watching-plum.md`. Four-stage pipeline using
   existing infrastructure: cluster→extract→verify→evaluate. Expected
   ~187 candidates, ~$2 cost.

### New Files

- `scripts/analyse_h2_pilot_extensions.py` — analysis script (3 analyses)
- `tests/test_analyse_h2_pilot_extensions.py` — 30 tier-1 unit tests
- `results/phase3d-pilot-extensions.md` — detailed write-up
- `results/phase3d-pilot-extensions.json` — machine-readable results
- `results/phase3d-pr-curves.csv` — threshold sweep data
- `results/figures/phase3d-pr-curves.png` — P-R curve figure
- `results/figures/phase3d-cross-modal-venn.png` — Venn diagram

### Modified Files

- `planning/to-do.md` — three free analyses marked complete, findings noted

### Key Metrics

**Cross-Modal Union (Pre-Verification)**:

| Metric | Image | Text | Union |
|---|---|---|---|
| Recall | 0.732 | 0.804 | **0.866** |
| TPs | 71/97 | 78/97 | 84/97 |
| Unique discoveries | 6 | 13 | — |
| Jaccard index | — | — | 0.774 |

**Multi-Verifier Ensemble vs Best Single**:

| Track | Best single (adversarial) | Best ensemble | Δ F1 |
|---|---|---|---|
| Image | 0.711 | 0.718 (union) | +0.007 |
| Text | 0.796 | 0.794 (average) | −0.002 |

### Commits

*(No commits this session — pending user review of results and plan)*

### Issues

- Script's `generate_report()` function overwrites hand-written detailed
  interpretation in `phase3d-pilot-extensions.md` when run end-to-end;
  hand-written version was restored manually. Future pattern: separate
  machine-generated tables from hand-written interpretation.

### Pending Work

- [ ] Execute cross-modal union experiment (plan at
  `~/.claude/plans/eager-watching-plum.md`)
- [ ] Commit Session 44 outputs (analysis script, tests, results,
  reflections)
- [ ] Pilot high-recall text proposer (~$7)
- [ ] HIGH-thinking verifier test (~$7)
- [ ] Fix Phase 3a YAML fixture rename in test_phase2_configs.py
  (carried forward from Session 43)

---

## Session 48 — 2026-03-10: Experiment E ablation series

### Focus

Implement and execute Experiment E (high-recall text proposer), then
systematically diagnose the negative result via one-at-a-time ablation.

### Accomplishments

1. **Implemented Experiment E infrastructure** — 4 deliverables:
   - `prompts/system-instructions/detect_brief-text_high-recall.md`
     (recall-biased proposer prompt)
   - `prompts/configs/detect_brief-text_high-recall.json` (all-levers
     config)
   - `scripts/run_experiment_e.py` (3-stage evaluation pipeline)
   - `tests/test_experiment_e.py` (12 tier1 tests, all passing)

2. **Executed initial combined run (E1)** — all levers simultaneously:
   recall-bias prompt, T=0.7, HIGH thinking, reduced examples (10, no
   nulls or HN). Result: F1=0.640 (ΔF1=−0.156 vs baseline 0.796).
   Surprising negative result.

3. **Ran 3 ablation experiments** — restored parameters one at a time:
   - **E2 (+nulls)**: F1=0.690 (+0.050, 32% of gap recovered)
   - **E3 (+minimal thinking)**: F1=0.711 (+0.021, 13%)
   - **E4 (+T=0.0)**: F1=0.779 (+0.068, 44%)

4. **Documented results thoroughly** —
   `results/phase3d-experiment-e-results.md` with full ablation tables,
   5 findings, success criteria, timing, and implications.

5. **Added 4 working-notes observations** (Obs 156–159): null examples
   as structural constraints, temperature as noise, recall ceiling is
   perceptual, capability frontier established.

6. **Updated project memory** — Experiment E status, expanded diversity
   taxonomy with 3 new entries.

### Key Findings

| Lever | ΔF1 attribution | % of total |
|---|---|---|
| T=0.7 → 0.0 | +0.068 | 44% |
| Null removal → restored | +0.050 | 32% |
| HIGH → minimal thinking | +0.021 | 13% |
| Recall-bias prompt + no HN | +0.017 | 11% |

**Both proposer-side and verifier-side optimisation now exhausted.**
F1=0.796 is the practical ceiling for Gemini Flash on this task.

### New Files

- `prompts/system-instructions/detect_brief-text_high-recall.md`
- `prompts/configs/detect_brief-text_high-recall.json`
- `prompts/configs/detect_brief-text_high-recall_nulls.json`
- `prompts/configs/detect_brief-text_high-recall_nulls-minimal.json`
- `prompts/configs/detect_brief-text_high-recall_nulls-minimal-t0.json`
- `scripts/run_experiment_e.py`
- `tests/test_experiment_e.py`
- `results/phase3d-experiment-e-results.md`
- `outputs/phase3d-experiment-e/` (candidates, probabilities, results)
- `outputs/results/detect_brief-text_high-recall*/` (4 proposer runs)

### Key Metrics

| Variant | Detections | Raw TP | Raw Recall | Verified F1 |
|---|---|---|---|---|
| Baseline | 140 | ~78 | 0.804 | **0.796** |
| E1 (all levers) | 212 | 66 | 0.680 | 0.640 |
| E2 (+nulls) | 183 | 71 | 0.740 | 0.690 |
| E3 (+minimal) | 184 | 73 | 0.753 | 0.711 |
| E4 (+T=0.0) | 151 | 76 | 0.784 | 0.779 |

Total experiment cost: ~$3.06 (4 proposer runs + 4 verifier runs).

### Commits

*(Pending user review)*

### Pending Work

- [ ] Commit Session 48 outputs
- [ ] Discuss "what next" — path to F1>0.80 or paper write-up focus
- [ ] Fix Phase 3a YAML fixture rename (carried forward)

## Session 50 — 2026-03-15: H11 384 proposer-verifier factorial and cascade experiments

**Focus**: Run the 384 proposer-verifier pipeline, expand to full 3×2
factorial, and test cascaded verification

**Duration**: ~2 hours
**Instance**: Direct experience (no compaction boundary)

### What Was Done

1. **Ran 384 proposer-verifier pipeline on zbook** (remote via SSH) —
   proposer reused prior 238/240 tiles, retried 2 remaining (1 succeeded,
   1 persistent parse failure). 572 detections from 239 tiles.

2. **Updated N=30 consensus findings** in results doc — N=30 at 384 does
   not improve over N=5 (F1=0.643 vs 0.664). Recall saturation (Obs 160).

3. **Created verifier configs** — `verify_adversarial.json`,
   `verify_adversarial-text.json`, `verify_brief-text.json`,
   `verify_checklist.json`, `verify_checklist-text.json`. Updated
   `verify_brief.json` from template (T=1.0) to Phase 3d params (T=0.0).

4. **Ran full 3×2 verifier factorial** — 3 strategies × 2 tracks on 572
   candidates. 3,672 API calls, $2.49 total, ~20 min sequential on zbook.

5. **Ran cascade experiments** — adversarial → checklist (removed 2 FPs)
   and checklist → adversarial (identical to single-pass). Confirmed
   near-perfect error correlation between strategies.

6. **Wrote up all results** — Section 5 of `results/h11-tile-size-results.md`
   expanded to cover full factorial (5.4), text-only gap collapse (5.7),
   strategy ranking (5.8), cascades (5.9).

7. **Added Obs 161** (384 PV factorial, text-only gap collapse) and
   **Obs 162** (text-only vs image as VLM capability insight).

### Key Findings

| Strategy | Image F1 | Text F1 | 512 text (ref) |
|:---------|:--------:|:-------:|:--------------:|
| Adversarial | **0.684** | 0.679 | 0.796 |
| Checklist | 0.672 | 0.661 | 0.782 |
| Brief | 0.661 | 0.675 | 0.768 |

- All 6 configs within 2.3 pp — candidate pool quality is the binding
  constraint, not verifier strategy
- Text-only vs image gap collapsed from +6–9 pp at 512 to ±1.5 pp at 384
- Cascade experiments show near-perfect error correlation between strategies
- 512 PV text-only (F1=0.796) remains project best

### New Files

- `prompts/configs/verify_adversarial.json`
- `prompts/configs/verify_adversarial-text.json`
- `prompts/configs/verify_brief-text.json`
- `prompts/configs/verify_checklist.json`
- `prompts/configs/verify_checklist-text.json`
- Outputs on zbook: `outputs/h11/proposer-verifier-384/verified-{strategy}-{track}.geojson`

### Commits

- `021ac42` — 384 PV results and N=30 consensus findings (adversarial only)
- `e9923cd` — Full 3×2 verifier factorial

### Pending Work

- [ ] Commit reflection entries and Obs 162
- [ ] 384 tile-size pathway is closed; focus shifts to paper write-up

---

## Session 51 — 2026-03-15: Config audit, model drift, Flash-Lite pilot, documentation rationalisation

**Focus**: 512 PV re-run after E33 crop fix; config audit and correction;
Phase 3a replication; Flash-Lite transfer pilot; documentation
**Duration**: ~4 hours
**Instance**: Direct experience (no compaction boundary)

### What Was Done

1. Planned and executed 512 PV re-run on zbook (E33-corrected crops)
2. Discovered F1 decline (0.796 → 0.729); ran identical-crop analysis
   (34% vs 35% flip rate → model drift, not crop fix)
3. Found verifier config mismatch vs Phase 3d baseline — 3 categories
   of non-target drift. Added `text_only_labels` and `crop_label`
   support to `5_verify_crops.py`
4. Audited all 384 configs; fixed 5 configs + study YAML reference
5. Re-ran corrected 512 PV (F1=0.732) and 384 factorial (5/6 complete,
   checklist-image rate-limited)
6. Investigated Phase 3a thinking-level metadata bug — corrected my
   initial analysis after user pointed to Obs 141
7. Added `--thinking-level` CLI override, fixed batch mode ordering
   gap, added `fixed` parameter support in study YAMLs
8. Ran Phase 3a replication via Batch API (30 minimal + 30 HIGH).
   Result: HIGH F1=0.735 vs minimal F1=0.699 (+3.6 pp)
9. Ran Flash-Lite pilot — catastrophic failure (F1=0.111 best). Three
   variants tested, all failed gate. Pathway abandoned (Decision 21)
10. Looked up MMMU Pro scores; saved leaderboard for cross-model planning
11. Updated hypothesis tracking (H2-H5, H9, H11 marked complete)
12. Created documentation index and maintenance protocol
13. Extracted 5 items from commits to formal docs (E34, D19-D21, Obs 165)
14. Completed full configuration audit (12 phases, ~350 checks). One
    critical finding (already resolved), no new issues

### Key Findings

| Result | Value |
|:-------|:------|
| 512 PV (corrected v2) | F1=0.732 (was 0.796 pre-correction) |
| 384 PV best (corrected v2) | F1=0.682 adversarial text |
| 512-384 gap | 5.0 pp (was 11.2 pp) |
| Phase 3a HIGH replication | F1=0.735 (+3.6 pp over minimal) |
| Flash-Lite best | F1=0.111 (gate failed) |
| Config audit | 1 critical (resolved), 0 new |

### Commits

`cad5d33`, `9b023ae`, `6159416`, `3419ce2`, `b9dbe80`, `7fb1d0b`,
`60cdffb`, `ead94aa`, `5d72603`, `eb423ef`, `0f67eba`, `9940972`,
`743cb5b`, `1ea2e43`, `59e7495`, `c0a6c8d`, `49e93c5`

### New Documents

- `docs/methodology/documentation-index.md`
- `docs/methodology/documentation-protocol.md`
- `docs/methodology/configuration-audit.md`
- `planning/mmmu-pro-leaderboard.md`
- `prompts/configs/detect_brief-text-high.json`
- `studies/phase3a-replication.yaml`

### Pending

- [ ] Checklist-image 384 verifier (rate-limited; retry when quota recovers)
- [ ] Cross-model comparison design (H14, using MMMU Pro leaderboard)
- [ ] Paper write-up integration of corrected results

## Session 52 — 2026-03-15/16

**Focus**: Production retest infrastructure and execution (340-tile
full corpus).

### Accomplished

1. Created 340-tile manifest and bounds GeoJSON (539 mounds in scope)
2. Config audit: 58 detection configs verified, PV text_only_labels
   confirmed correct
3. Generated 14 retest study YAMLs via `create_retest_studies.py`
4. Fixed `run_phase2.py` empty `fixed:` handling (NoneType bug)
5. Ran $0.17 smoke test — caught bootstrap recall bias (E35, 7 pp
   divergence from tile-overlap reference double-counting)
6. Rewrote `compute_per_tile_tp_fp_fn()` to match per-map then
   distribute to tiles — divergence collapsed to <0.002
7. **Stage 1 complete**: 66/66 units across 9 studies (Phases 2a–2e)
8. **Stage 2 partially complete**: 162/240 units (Track 1: 81/90,
   Track 2: 81/90, Replication: 18/60)
9. Built `BatchTokenLedger` for Batch API enqueued token management
   (3M Tier 1 quota)
10. Added `countTokens`-based estimation, safety margin, retry backoff,
    and submission spacing
11. Documented persona affordance design concept — craft entry, paper
    seed, memory, actionable plan
12. Web research on persona cultivation, context engineering, affordance
    theory applied to AI

### Key Finding

Per-tile bootstrap matching produces biased recall estimates at scale
due to reference double-counting in tile overlap zones. Fixed by
switching to per-map matching with tile-level distribution (E35).

### Infrastructure Created

- `inputs/tiles/full_evaluation_manifest.json` (340 tiles)
- `inputs/vectors/bounds/full_evaluation_bounds.geojson`
- `studies/retest/*.yaml` (14 files)
- `scripts/create_retest_studies.py`
- `scripts/evaluate_pilot.py`
- `BatchTokenLedger` class in `run_phase2.py`

### Commits

`f06afb7`, `3ad487f`, `5a57f58`, `aa099ad`, `195fa64`

### Pending

- [ ] Stage 2 remaining: Track 2 (9 units), Replication (42 units),
      Track 1 (9 units) — blocked on daily quota reset
- [ ] Stage 3: PV pipeline (proposer + verifier on 340 tiles)
- [ ] Stage 4: Diversity (deferred, decision after Stages 1–3)
- [ ] Persona affordance design: review proposed CLAUDE.md additions
- [ ] Push commits to origin

---

## Session 53 — 2026-03-17/19 (map-reader-llm)

### Production Runs Completed

- Phase 3a Track 2 (text, minimal): 8 remaining units → 90/90 complete
- Phase 3a Track 1 (image, minimal): 9 remaining units → 90/90 complete
  (reconciled T1.0/run_26 under new threshold)
- Phase 3a Replication (minimal + HIGH, T=0.7): 42 units → 60/60 complete
  (reconciled 26 units, patched 203 tiles via `--patch-tiles`)
- Phase 3a HIGH text track (T=0.3/0.7/1.0): 76/90 complete (in progress)
- Phase 3c Diversity text track: 41/100 complete (in progress)
- Phase 3a HIGH image track: queued (pending text completion)
- Phase 3c Diversity image track: queued (pending text completion)

### Evaluation Results

All OFAT phases (2a–2e) and Phase 3a evaluated with F1/P/R + bootstrap
95% CIs. Key results:

- Best single-pass: F1=0.631 (image, canonical-last, T=0.0)
- Best consensus (minimal): F1=0.691 (image T0.7 18-of-30)
- Best consensus (HIGH): F1=0.771 (text T0.7 21-of-30) — **best overall**
- HIGH thinking significantly worse single-pass (−0.139) but
  significantly better under consensus (+0.068)

Consensus sweep completed for both tracks + replication (N=5/10/30).

### Statistical Analysis

70 pairwise bootstrap comparisons with two-sided p-values completed.
24 significant at raw p < 0.05. FDR correction deferred until full
comparison family is available. `bootstrap_effect_size_ci()` extended
with `return_p_values` parameter for FDR support.

### Infrastructure Built

- `scripts/evaluate_retest_all.py` — comprehensive evaluation script
- `scripts/lib_batch_verifier.py` — batch verifier library for PV pipeline
- `MAX_SYNC_RETRIES` raised to 10; `MAX_ACCEPTABLE_TILE_FAILURES` to 10
- `--patch-tiles` mode for post-hoc tile recovery (two-tier: original
  params then safe-mode with reduced `max_output_tokens`)
- Failed tile report in `complete_batch_unit()` with `--patch-tiles` hint
- `max_output_tokens_override` parameter on `_retry_tile_sync()`
- Model name resolution in `patch_failed_tiles()`

### Documentation

- `docs/batch-api-throughput-and-errors.md` — processing times and error
  characterisation
- `docs/cost-effectiveness-analysis.md` — cost model with Pareto frontier
- `planning/pv-batch-pipeline.md` — approved PV implementation plan

### Study YAMLs Created

- `studies/retest/phase3a-h3-voting-track1-high.yaml`
- `studies/retest/phase3a-h3-voting-track2-high.yaml`
- `prompts/configs/library_plus-hp-high.json`

### Commits

`2176d46`, `d9361ea`, `3caae99`, `9d3fcbb`, `fc832df`, `3054136`,
`85edc74`, `f9d40e0`, `01a6a76`

### Pending

- [ ] HIGH text track: 14 remaining units (in progress)
- [ ] Diversity text track: 59 remaining units (in progress)
- [ ] HIGH image track: 90 units (queued)
- [ ] Diversity image track: 125 units (queued)
- [ ] PV pipeline: `run_pv_batch.py` orchestrator (step 2–6 of plan)
- [ ] PV pipeline: `evaluate_pv_results.py` threshold sweep (step 7)
- [ ] Phase 1 verifier optimisation (6 variants × 4 proposers)
- [ ] FDR-corrected analysis (after all production data available)

---

## Session 54 — 2026-03-20/21 (map-reader-llm): PV pipeline build, production experiments, documentation

### Overview

Built the complete dual-mode Proposer-Verifier pipeline from library through orchestrator, evaluator, and production experiments. Achieved new project best F1=0.831. Completed Phase 3a-HIGH text (90/90). Created `/phase-gate` skill. Full documentation suite.

### Accomplishments

1. **Refactored lib_verifier.py** — shared IR (TextItem/ImageItem), batch + real-time serialisers, verify_candidate_realtime() with retry
2. **Built run_pv.py** — dual-mode orchestrator with extract/verify subcommands, `--mode batch|realtime`
3. **Built evaluate_pv_results.py** — threshold sweep with bootstrap CIs, multi-variant comparison
4. **Audited all new code** — 18 issues found and fixed across 3 files (critical: dry-run guard, model resolution, safety-block handling; tests: 36 → 47 → 57)
5. **PV Phase 1 optimisation** — crop size (40–300px), consensus (N=1 vs N=5), verifier strategy (3 types). All parameters insensitive. Obs 166–169.
6. **PV Phase 2 production** — 25 experiments across N=1 runs, consensus unions, HIGH configs. PV improved F1 in 25/25. New best: F1=0.831 (text 5-of-10 + PV)
7. **54 pairwise bootstrap comparisons** — computed on sapphire. PV significantly beats all non-PV approaches.
8. **Phase 3a-HIGH text complete** (90/90) — consensus sweep (135 configs), 8 pairwise comparisons. Best: T=0.3 23-of-30 F1=0.779
9. **Created `/phase-gate` skill** — experimental phase boundary checkpoint (Obs 168)
10. **Full documentation** — retest summary, PV Phase 1 + 2 analyses, protocol errata E36–39, decisions D22–25, Obs 166–177
11. **Copied rasters** to amd-tower, fixed consensus GeoJSON CRS (EPSG:4326 → 32635)

### Key Results

| Configuration | F1 | 95% CI |
|---|---|---|
| PV: text 5-of-10 + verifier | **0.831** | [0.789, 0.870] |
| PV: text 3-of-10 + verifier | 0.823 | [0.784, 0.860] |
| PV: HIGH 20-of-30 + verifier | 0.819 | [0.776, 0.856] |
| Consensus: HIGH 23-of-30 (no PV) | 0.779 | [0.735, 0.822] |
| Previous best: HIGH 25-of-30 | 0.763 | [0.709, 0.802] |

### Issues

- Batch API jobs stuck in PENDING for 24+ hours (cancelled, resubmitted)
- Consensus GeoJSONs missing CRS declaration (fixed)
- Verifier strategy not validated at scale before Phase 2 (caught retroactively, led to /phase-gate skill)
- Ad hoc consensus thresholds used instead of preregistered N=5/10/30 convention (corrected)

### Pending

- [ ] Phase 3c diversity text: 60/100 complete (batch polling running)
- [ ] Phase 3a-HIGH image track: 90 units, not started (Task #1 prerequisite)
- [ ] Phase 3c diversity image track: 100 units, not started (Task #1)
- [ ] FDR correction across all pairwise comparisons (after all data)
- [ ] Update analysis summaries when pairwise/FDR results available

---

*New session entries should be appended above this line.*

## Session 57 — 2026-03-25 (map-reader-llm): Comprehensive analysis, configuration audit, E42 saga, 22 bug fixes

### Overview

Marathon session covering four major workstreams: (1) completed all
pending consensus sweeps and 16 pairwise comparisons, (2) ran PV
pipeline on two conditions, (3) discovered and investigated a metadata
bug (E42) that led to a misdiagnosis (Pro runs reported as Flash),
then corrected after deep dive confirmed Pro was genuine, (4) ran
comprehensive code audit finding 22 bugs (4 critical) and fixed all.

### Key results

- Flash HIGH text N=30 consensus F1=0.814 [0.763, 0.860] — best consensus-only
- Flash HIGH text 4-of-5 + Flash PV F1=0.864 [0.833, 0.893] — best overall
- Pro HIGH text 3-of-5 + Flash PV F1=0.850 [0.812, 0.883]
- T=0.7 >> T=1.0 at all pool sizes (dF1 ~+0.15, p<0.0001)
- Pool scaling: N=5→N=10 significant (p=0.025), N=10→N=30 ns (p=0.852)
- Flash medium verifier > minimal verifier on text (p=0.001)
- Pro vs Flash model: ns at tile level (p=0.874 text, p=0.018 image Flash better)

### Bugs found and fixed (22 total)

- **E42 metadata bug**: `configuration.model` reported config default, not
  resolved model. Fixed with `model_override` parameter in `LLMMetadataTracker`.
  Initially misdiagnosed as "Pro never used" (all meta.json said Flash); deep
  dive via GeoJSON features/cost_estimate/logs confirmed Pro was genuine.
- **E42 in 3 more callers**: `5_verify_crops.py`, `4_detect_mounds_batch.py`,
  `run_pv.py` estimate_cost — all fixed
- **source_tiles/source_tile mismatch**: merge_passes.py outputs list,
  extract_candidates.py expects string — added normalisation
- **Temperature propagation**: single-pass-384 T=1.0 bug newly discovered
- **15 additional medium/low bugs**: patch metadata, dropped tiles logging,
  bounds tracking, thinking_level display, stale path fallbacks, etc.

### Issues found

- E42 misdiagnosis: renamed Pro dirs to Flash, then had to rename back.
  Root cause was trusting `configuration.model` without cross-validation.
- All verifier runs used Flash — no Pro verifier data exists despite intent.
  Proposer × verifier model matrix is incomplete (4 of 6 cells filled).
- single-pass-384 ran at T=1.0 not T=0.0 (same root cause as consensus-384).
- Long-running diversity batch killed when CC session closed (not nohup'd).
  Restarted with nohup, 123/125 complete at session end.

### Pending (next session)

- Commit all Session 57 changes (massive)
- Audit correctives: rename T=1.0 dirs, re-run single-pass at T=0.0
- Complete PV baseline: 5 conditions with crops ready (~$1.23 Batch API)
- Buffer sensitivity analysis at 30, 40, 50 m
- Pro verifier matrix: 10 new verifier runs needed
- Systematic gap matrix for paper write-up

---

## Session 56 — 2026-03-23/24 (map-reader-llm): Gemini 3.1 Pro pilot, HIGH thinking consensus, temperature bug discovery

### Overview

First Gemini 3.1 Pro experiments on this project. Ran a full Flash × Pro comparison matrix (single-pass + PV, 8 conditions) and N=5 consensus comparisons with HIGH thinking. Key finding: HIGH thinking is the dominant factor for consensus performance (p<0.0001), not the model — Pro adds nothing beyond Flash HIGH (p=0.874). Discovered a temperature propagation bug affecting 30 runs of historical data and a silent batch failure mode in Gemini 3.1 Pro. Significant infrastructure work: `--model`, `--thinking-level`, and `--bounds` CLI overrides for cross-model experiments.

### Key results

- Pro MEDIUM single-pass underperforms Flash MINIMAL: text -0.039, image -0.096
- Pro HIGH text N=5 simple consensus F1=0.849 (approaching Flash N=10+PV champion 0.883)
- Flash HIGH text N=5 simple consensus F1=0.776 (+0.132 over MINIMAL)
- Pairwise: Flash HIGH vs MINIMAL text p<0.0001; Pro HIGH vs Flash HIGH p=0.874 (ns)
- Image N=10+PV: best 6-of-10 F1=0.789; text N=5+PV: best 2-of-5 F1=0.600

### Issues found

- Gemini 3.1 Pro rejects MINIMAL thinking silently in batch mode (E40)
- `extract_conditions()` dropped `thinking_level` for pre-enumerated conditions
- consensus-384 text runs used T=1.0 not T=0.7 (10-day-old bug in temperature propagation)
- `evaluate_pv_results.py` and `paired_permutation_consensus.py` hardcoded 512px bounds
- Bootstrap evaluations run on local machine during live presentation (sapphire policy)

### Pending (next session)

- Analyse completed batch runs (consensus sweeps, PV pipeline, pairwise comparisons)
- Flash HIGH text N=30 and Flash MINIMAL text N=30 T=0.7 (in flight)
- Phase 3c H9 diversity Track 1 completion + analysis
- T=0.7 vs T=1.0 comparison (unexpected data from temperature bug)
- Comprehensive run audit against preregistration
- 512px PV pipeline (low priority)

---

## Session 55 — 2026-03-21/23 (map-reader-llm): 384px tile-size breakthrough, 256px diagnostic, infrastructure hardening

### Overview

Extended session spanning three days. Managed in-flight batch runs (Phase 3c Tracks 1+2), discovered 384px tiles produce a new project-best F1=0.883 (+0.063 over 512px, p=0.002), confirmed with 256px diagnostic that 384px is optimal (inverted-U curve). Significant infrastructure work: code audit integration, file storage concurrency fix, polling resilience, and 306 accumulated failed tiles recovered.

### Accomplishments

1. **Batch API management** — swept 116 orphaned files (15.3 GB), resumed crashed processes, patched 306 failed tiles across all runs, increased max_poll_hours from 25 → 72
2. **Code audit integration** — reviewed 22-finding audit from parallel session, built on fixes (proactive sweep, polling resilience, catch-all exception handler)
3. **Concurrency-safe file registry** — `lib_file_registry.py` with `fcntl.flock` locking, atomic writes, 48h stale entry pruning. Replaced per-process sweep that caused 404 race conditions
4. **384px diagnostic** — 4 proposer configs (487 clean tiles), 17 PV verification runs, full threshold sweeps. New project best: text 6-of-10 + PV F1=0.883
5. **Fair paired comparison methodology** — spatial-join 512px detections to 384px tile polygons for truly paired bootstrap. All 6 comparisons significant (p ≤ 0.008)
6. **256px diagnostic** — 1,032 clean tiles, N=1 smoke test + N=5 consensus + PV. Best F1=0.844. Confirms inverted-U peaking at 384px
7. **Phase 3c Track 2 complete** (100/100) — diversity adds nothing (all p > 0.44), 9 pairwise comparisons
8. **Pairwise re-run** — 52 comparisons with corrected code (v2). Max change 0.0018 F1; no conclusions affected
9. **Phase 3c diversity pairwise** — 9 new comparisons confirming null result for H9
10. **Observations 178–182** — Batch API operations, 384px superiority, paired test methodology, 256px peak confirmation, audit impact assessment

### Key Results

| Configuration | F1 | Context |
|---|---|---|
| **384px text 6-of-10 + PV** | **0.883** | New project best |
| 384px text 5-of-10 + PV | 0.881 | |
| 256px text 5-of-5 + PV | 0.844 | Below 384px (p=0.816) |
| 512px text 5-of-10 + PV | 0.831 | Below 384px (p=0.002) |

### Issues Found

- Proactive sweep race condition (files deleted by concurrent processes) → fixed with shared registry
- 25-hour poll timeout misidentified as process crash → increased to 72h
- `box_2d` string coordinates from Gemini API → float cast added
- `generate_consensus_gdf` key collision with shared run names → parent/name key
- `calculate_f1_internal` return order (P, R, F1) misread as (F1, P, R) → caught by user

### Pending

- Phase 3c Track 1 image: 74/125 (will need 1 more --resume after 25h timeout)
- Phase 3c Track 1 analysis + pairwise comparisons
- FDR correction (blocked on Track 1)
- Phase 4 (H6 Flash→Pro transfer): not started

---

## Session 58 — 2026-03-25/26 (map-reader-llm): Final API runs, Pro verifier matrix, F1=0.890, methodology revision

### Overview

Two-day session completing all planned API work, running comprehensive
analyses, and discovering a methodological issue in the pairwise
permutation test that led to erratum E45. The project's best result
reached F1=0.890 (0.904 at 30m buffer). All experiments are now complete
— remaining work is statistical analysis and paper writing.

### Accomplishments

1. **All API runs complete** — 4 waves launched overnight:
   - Wave 1: Flash PV baseline (4 conditions, 21,247 candidates) via batch
   - Wave 2+4: Pro verifier matrix (10 conditions, 15,799 candidates) —
     batch stalled twice, switched to real-time for final 4 jobs
   - Wave 3: Single-pass T=0.0 rerun (10 runs × 487 tiles) via batch
   - 90 missing Pro verifier candidates recovered via real-time API
   - 1 candidate (03486) excluded — systematic parse failure at medium thinking

2. **Sapphire analyses** — all run on sapphire per project rules:
   - Buffer distance sensitivity: 15 consensus conditions × 3 buffers
   - Phase 3c diversity: Track 1 + Track 2 re-analysis (H9 null both tracks)
   - PV threshold sweeps: 50 new conditions (N=5/10/30 Flash, N=5 MINIMAL)
   - Pro verifier evaluation: 34 sweeps (4 baselines + 30 derived)
   - Detection-to-reference distance distributions (Obs 190)
   - Cross-modal complementarity check (+0.3% recall — not worthwhile)

3. **Documentation completed**:
   - Observations 190–195 in working notes
   - Protocol errata E43 (consensus-384 T=1.0), E44 (single-pass T=1.0),
     E45 (permutation test methodology)
   - Consolidated results report (`reports/results-summary-session-58.md`)
   - 81 per-condition PV sweep markdown summaries (new generator script)
   - Bootstrap CIs consolidated (81 conditions)
   - T=1.0 directories renamed with READMEs
   - 2 superseded pairwise files archived

4. **Code delivered**:
   - `analyse_pv_buffer_sensitivity.py` — standalone FAIR4RS buffer script
   - `pairwise_permutation_test.py` — generalised pairwise test (3 modes)
   - `generate_pv_sweep_summaries.py` — markdown summary generator
   - `consolidate_pv_bootstrap_cis.py` — bootstrap CI consolidation
   - Buffer-metres consolidation: `lib_advanced_metrics.py` (4 functions
     parameterised), `evaluate_pv_results.py` + 4 consumer scripts updated
   - 6 batch/overnight shell scripts

5. **13 commits pushed** — clearing Session 57–58 backlog. Resolved
   GitHub 100 MB limit by gitignoring verifier_requests.jsonl files.

### Key Results

| Configuration | F1@20m | F1@30m | Notes |
|---|---|---|---|
| **Flash HIGH text 16-of-30 + Flash min vf** | **0.890** | **0.904** | New project best |
| Flash HIGH text 4-of-5 + Pro vf | 0.879 | — | Pro verifier significant (p=0.019) |
| Flash HIGH text 6-of-10 + Flash min vf | 0.877 | 0.898 | |
| Flash MINIMAL T=0.7 4-of-5 + Flash min vf | 0.871 | 0.883 | Cheapest competitive config |
| Flash HIGH text 4-of-5 + Flash min vf | 0.864 | 0.891 | Previous best |
| Pro HIGH text 3-of-5 + Flash min vf | 0.850 | 0.865 | P=0.971 at 30m (precision leader) |

### Key Findings

- **F1 > 0.9 achieved** at 30m buffer (Obs 193)
- **Pro verifier significantly outperforms Flash** (p=0.019, E45 method)
- **Verifier thinking level**: minimal > medium > HIGH in aggregate,
  but HIGH wins more individual tiles (Obs 194)
- **Buffer sensitivity**: image tracks gain 0.09–0.15 F1 at 30–50m;
  text saturates at 30m (Obs 190)
- **Temperature**: T=0.7 >> T=1.0 by ~0.15 F1 at all pool sizes
- **Diversity (H9)**: null on both tracks; Obs 148 variance stabilisation
  did not replicate (Obs 192)
- **Cross-modal union**: +0.3% recall at N=30 — not worthwhile
- **Verifier model effect converges** with consensus quality (Obs 195)
- **Permutation test methodology**: macro-average sign-flip replaced by
  micro-average tile-swap (E45) for consistency with project F1 reporting

### Issues Found

- Batch API queue stalled repeatedly (2 Pro jobs, 1 Flash job stuck in
  PENDING for hours with no state change). Resolved by switching to
  real-time API.
- 90 candidates missing from flash-high-text-1of5 Pro verifier batch
  result — recovered via real-time API
- 1 candidate (03486) produces unparseable JSON at Flash medium thinking
  — excluded (3,735/3,736 coverage)
- Ad-hoc bootstrap pairwise test used different method than preregistered
  permutation test — caught during `/review-implementation`, corrected
  with E45
- Disk space critically low (638 MB) — freed 5 GB by deleting
  regenerable verifier JSONL files

### Pending

- ~~FDR correction across all pairwise families~~ → Session 60
- ~~Tile-level MCC (preregistered secondary outcome)~~ → Done Session 59
- ~~Re-run 17 existing pairwise comparisons with E45 method~~ → Session 60
- ~~Additional PV pairwise comparisons~~ → Session 60 (32 defined in YAML)
- ~~Gap matrix review~~ → Done Session 59 (comprehensive coverage)
- Commit Session 58+59 changes
- Paper writing

## Session 59 — 2026-03-27/28 (map-reader-llm): Multi-buffer evaluation, N=1 baselines, MCC, Pro 2×2 matrix

### Overview

Marathon two-day session completing all single-condition analyses for
the paper. Chose 30m spatial tolerance (E46), evaluated everything at
multiple buffers, computed tile-level MCC across 63 conditions, completed
the Pro temperature × thinking matrix, implemented context caching, and
defined 32 pairwise comparisons for the next session.

### Accomplishments

1. **Tile patching and bug fixes** — patched 13 failed tiles in
   single-pass-384 T=0.0. Fixed 3 bugs: tiles_dir not threaded to
   patch function, trailing comma in LLM JSON output, tile_size None
   from meta.json.

2. **Multi-buffer evaluation** — all consensus + PV conditions at
   20/30/40/50m on full 487-tile bounds. Created `sapphire-paper-eval.sh`,
   `consolidate_paper_metrics.py`, `configs/pv-paper-conditions.yaml`.
   Ran on sapphire (~16 min).

3. **Spatial tolerance decision** — chose 30m as primary buffer (E46).
   Text plateaus at 30m, image at 50m. Both plateau well within symbol
   diameter. Centroid-to-centroid matching methodology documented
   (Obs 198).

4. **N=1 single-pass evaluation** — created `evaluate_detections.py`
   with `--batch` and `--mcc` modes. Evaluated 16 conditions at 384px
   and 33 conditions at 512px (Phase 2), all at 30m with bootstrap CIs.

5. **Pro 2×2 matrix** — completed MEDIUM/HIGH × T=0.0/T=0.7 for text
   and image. Discovered strong temperature × thinking interaction
   (Obs 200). Ran Pro MEDIUM T=0.7 (the final missing cell) and found
   it dramatically underperforms (F1=0.428 text).

6. **Context caching** — implemented `--use-cache` in
   `4_detect_mounds_batch.py` and `run_phase2.py`. Works for image
   configs (14,549 tokens cached, 90% input discount). Text configs
   below 1,024 token minimum, fall back gracefully.

7. **Pricing fix** — updated PRICING table in `lib_llm_metadata.py`
   with verified Google pricing. Old table had Flash-Lite prices for
   Flash model.

8. **Tile-level MCC** — created `evaluate_tile_mcc.py` for consensus
   and PV conditions. Evaluated 63 total conditions (18 N=1 at 384px,
   33 N=1 at 512px, 12 consensus/PV). Key finding: Flash MCC ≈ 0
   (detects everywhere), Pro MCC ≈ 0.85 (genuine discrimination),
   pipeline MCC = 0.79 (compensates for Flash limitation).

9. **Pairwise comparison spec** — 32 comparisons across 7 groups
   defined in `configs/pairwise-comparisons.yaml`. YAML-driven for
   reproducibility.

10. **Disk cleanup** — freed 173 GB by deleting 319 completed
    batch_working directories.

11. **Documentation** — Observations 196–202 in working notes. Erratum
    E46 (spatial tolerance). Archived 11 superseded planning files.
    New master to-do list.

### Key findings

- **Obs 196**: Text-image gap is largely a localisation artefact — gap
  narrows and inverts at wider buffers
- **Obs 197**: Text plateaus at 30m (6 px), image at 50m (10 px)
- **Obs 198**: Centroid-to-centroid Hungarian matching methodology
- **Obs 199**: ~$1,000 potentially wasted by not using context caching
- **Obs 200**: Pro temperature × thinking interaction — mismatched
  configurations fail
- **Obs 201**: Flash cannot discriminate empty tiles (MCC ≈ 0)
- **Obs 202**: Pipeline compensates for fundamental model limitations
  that prompt engineering cannot fix

### Scripts created

- `scripts/evaluate_detections.py` — general-purpose detection
  evaluation with `--batch` and `--mcc` modes
- `scripts/evaluate_tile_mcc.py` — tile-level MCC for consensus/PV
- `scripts/consolidate_paper_metrics.py` — multi-buffer consolidation
- `scripts/sapphire-paper-eval.sh` — multi-buffer orchestration

### Pending (Session 60)

- Pairwise permutation tests (32 comparisons at 20m + 30m)
- FDR correction (26 confirmatory + 6 exploratory)
- Paper tables (leaderboard, pipeline progression, tolerance curve)
- API cost retrospective
- Commits (substantial accumulated changes)
- Spatial tolerance curve for plotting

See `planning/session-59-analysis-plan.md` for detailed carry-forward.

---

## Session 60 — 2026-03-28 (map-reader-llm)

**Focus**: Adversarial audit of F1 > 0.9 result; pairwise comparison
strategy.

### Accomplishments

1. **Prompt hardening** — applied `/improve-prompt` to the adversarial
   audit seed prompt (`planning/adversarial-audit-prompt-seed.md`).
   Produced hardened version at `planning/adversarial-audit-prompt.md`
   with 15 anti-satisficing techniques applied. Captured to grimoire.

2. **Full adversarial audit** — ran the hardened prompt across 8 pipeline
   layers and 9 inflation hypotheses using 5 parallel subagents. All 9
   hypotheses rejected. No pipeline errors, data leakage, or
   methodological flaws found. F1 = 0.9044 verified from raw counts
   (TP=383, FP=29, FN=52, scoped GT=435). Report at
   `reports/adversarial-audit-report.md`.

3. **Identified reporting concerns** — three issues flagged, all about
   reporting precision rather than pipeline correctness:
   - Tolerance dependency: F1 = 0.904 at 30m, 0.890 at 20m
   - CI lower bound = 0.878 (does not guarantee F1 > 0.9)
   - No pairwise test between top-2 PV conditions

4. **Documented pseudo-p-value FDR flaw** — detailed explanation of why
   the ad hoc formula in `analyse_phase2_results.py:199-210` is
   methodologically unsound, with recommendation to replace with real
   permutation test p-values from `pairwise_permutation_test.py`.

5. **Pairwise comparison proposal** — designed 32 structured comparisons
   across 7 hypothesis-driven groups (26 confirmatory + 6 exploratory)
   with BH FDR correction. Written to
   `planning/pairwise-comparison-proposal.md`.

6. **Symbol radius correction** — incorporated user's domain correction
   that 30m ≈ 1 symbol radius (not diameter), strengthening the
   tolerance justification (Obs 204).

### Key findings

- **Obs 203**: Adversarial audit as publication prerequisite — the audit
  trail is itself a publishable supplementary document
- **Obs 204**: 30m tolerance = approximate minimum symbol radius,
  providing geometric justification for the preregistration deviation

### Files created

- `planning/adversarial-audit-prompt.md` — hardened audit prompt
- `reports/adversarial-audit-report.md` — full audit report
- `planning/pairwise-comparison-proposal.md` — 32-comparison strategy
- `personal-assistant/notes/grimoire/adversarial-results-audit.md` —
  grimoire entry

### Session 60 continuation — Analysis phase (different CC instance)

7. **N=1 tolerance sweep** — evaluated all 51 N=1 conditions (18 at
   384px + 33 at 512px) at 20/30/40/50m buffers on sapphire.

8. **Pairwise permutation tests** — wrote `run_pairwise_tests.py`
   orchestrator and `apply_fdr_correction.py`. Ran 335 comparisons:
   - 32 hypothesis-driven (7 groups): 18/26 confirmatory significant,
     3/6 exploratory significant after BH FDR at 30m
   - 300 leaderboard round-robin (top-25): 243/300 significant,
     9 performance tiers identified
   - 20m sensitivity: directionally consistent (20/26 confirmatory)

9. **Paper tables** — produced 7 tables:
   - N=1 leaderboard (51 conditions × 4 buffers)
   - Pipeline progression (F1: 0.406 → 0.904)
   - Pairwise hypothesis table with 20m cross-check
   - Leaderboard tier clustering (top 3 indistinguishable)
   - Spatial tolerance curve (15 conditions × 4 buffers)
   - Pro 2×2 temperature × thinking matrix
   - Cost retrospective (~$195–203 total, $0.34/mound)

10. **MCC completeness** — 16 additional conditions (5 PV + 11
    consensus). Image baseline + PV achieved MCC=0.877 (highest).

11. **H9 diversity cross-track comparison** — null result on both
    tracks. Parametric diversity fails where structural diversity
    (PV pipeline) succeeds.

12. **Tile-size comparison** — `/review-implementation` identified
    McNemar + per-map F1 as the correct approach (tile-swap permutation
    invalid for cross-grid). Finding: 384px has higher recall (McNemar
    p≤0.017), 512px has higher F1 (better precision). Divergence
    explains why 384px suits the consensus+PV pipeline (Obs 203).

13. **Defensive model check** — `validate_model_consistency()` in
    run_phase2.py and run_pv.py. Checks CLI vs YAML vs output dir.

14. **Commits and cleanup** — 22 commits pushed, 171.7 GB freed on
    sapphire (319 batch_working dirs), all to-do items complete.

## Session 61 — 2026-03-29 to 2026-04-02 (map-reader-llm)

Transition from analysis to paper argumentation. 14 commits pushed.

1. **Housekeeping** — confirmed all analyses complete, marked to-do
   items done, archived 9 completed planning files to archive/planning/.

2. **Primary tolerance reverted to 20m** — new errata E47 reinstating
   preregistered 20m as headline tolerance (superseding E46's 30m).
   Updated script defaults, configs, condition registry. 30m retained
   for production recommendation via tolerance curve.

3. **20m leaderboard round-robin** — ran full C(25,2) = 300 pairwise
   permutation tests at 20m. Finding: best condition (FH text 16/30 +
   PV) separates as solitary Tier 1 at 20m (indistinguishable from
   top 3 at 30m). Greater discrimination at tighter tolerance.

4. **Condition registry completed** — added 20m-optimal threshold
   variants for FH image N=10 (7-of-10) and FM image N=10 (8-of-10).
   Re-ran round-robin: all 25 conditions, 248/300 significant.

5. **Pro N=10 expansion** — 5 additional Pro HIGH text Batch API runs
   (~$60). Consensus evaluation at all thresholds and 20/30/40/50m
   buffers. Result: Pro N=10 does NOT improve over N=5 (F1=0.837 vs
   0.843, well within CIs). Pool-size plateau confirmed for both
   models. PV stage skipped (consensus showed no improvement).

6. **Leaderboard expanded to 26 conditions** — added Pro N=10 6-of-10.
   Re-ran round-robin: 325 comparisons, 265/325 significant. Pro N=10
   slots into Tier 2 at #7, just below Pro N=5 at #6. Tier structure
   unchanged (9 tiers).

7. **Annotated leaderboard document** — comprehensive briefing document
   for co-authors with all 26 conditions, F1/P/R/MCC with CIs, tier
   assignments, pipeline progression, pairwise results, and what-works
   / what-doesn't summary. Updated three times as analysis progressed.

8. **Pareto frontier analysis** — identified only 3 cost-optimal
   configurations (all PV). Text baseline + PV at $0.25 outperforms
   all consensus-only conditions. FH text 4/5 + PV at $3 is the knee.
   Pro completely dominated by Flash + pipeline.

9. **Five-factor lever analysis** — 61 FDR-corrected pairwise
   permutation tests across 5 families:
   - Architecture: 11/12 significant (max ΔF1 +0.387)
   - Thinking: 5/6 significant (max ΔF1 +0.164)
   - Temperature: 5/6 significant (max ΔF1 +0.194)
   - Modality: 8/9 significant (max ΔF1 +0.149)
   - Prompt engineering: 0/28 significant (max ΔF1 +0.061)
   Created YAML config, ran 14 new tests (12 at 384px, 2 at 512px),
   merged with 18 reused + 28 prompt engineering results.

10. **Modality amplification** — text outperforms image in 5/6 matched
    architecture comparisons (ΔF1 +0.047 to +0.141). Gap amplifies
    through pipeline stages. Corrected earlier underestimate and ran
    2 missing permutation tests (Pro text vs image ***, baseline PV
    text vs image ***).

11. **Thinking-level crossover** — HIGH is worse at N=1 (ΔF1=-0.101)
    but better at consensus (+0.139). The diversity mechanism: HIGH's
    false positives are diverse and filterable; MINIMAL's are consistent
    and systematic. Single-pass benchmarks would select the wrong
    configuration.

12. **T=1.0 clarification** — corrected characterisation throughout.
    T=1.0 is a preregistered test condition (Phase 2b), not
    intrinsically a bug. The finding that T=1.0 performs poorly is
    legitimate. The bug (E43) was deploying T=1.0 when T=0.7 was
    intended — a separate incident.

13. **Paper framing** — two-stage presentation: absolute effect
    magnitude first (does the lever move the needle?), then direction
    and interactions for factors that matter. Identified three design
    decisions that cross over between N=1 and consensus (thinking,
    temperature, tile size).

14. **Experimental progression report** — three-act narrative for the
    methods section: preregistered exploration (60 tiles), scaled
    validation (340 tiles), production optimisation (487 tiles).
    Documents what was tested where and why the design evolved.

15. **Venue strategy** — ISPRS JPRS first (no word limit, IF~13,
    CAUL-covered), cascade to JAG via Elsevier transfer if desk-
    rejected. Four framing hooks: methodology not archaeology,
    text-only novelty, Pareto costs, preregistration credibility.

### Observations added

- Obs 204: Pool-size plateau (Pro N=10 confirms N=5 saturation)
- Obs 205: Cost-performance Pareto frontier
- Obs 206: Text modality amplification through pipeline stages
- Obs 207: Five-factor lever analysis (61 tests, 5 FDR families)
- Obs 208: Thinking-level crossover (N=1 vs consensus direction reversal)
- Obs 209: Paper framing and T=1.0 distinction

## Session 62 — 2026-04-08 (map-reader-llm)

Generalisation run preparation — dataset characterisation, QGIS sanity
check, prompt refinement (v2), erratum E47, code hardening, and 55-map
infrastructure.

### Dataset characterisation

1. **Student mound data loaded** — `MapMounds17_18LLgood.csv` (10,825
   records). Filtered to "hairy" symbols only (mounds): 5,306.
   Spatial join against 332 available rasters: 59 maps with student
   data, 55 after excluding the 4 gold-standard maps.

2. **Hairy-only filter validated** — 0.97 ratio against curated
   reference on the 4 overlap maps (552 student vs 569 curated).
   Confirms the filter captures the correct symbol types.

3. **Tile count**: 7,833 tiles at 384px (stride 336) across 55 maps.
   Revised to 8,541 after reprojection to EPSG:32635.

4. **Cost estimate**: ~$28 batch for FH text 4-of-5 + PV on 55 maps.

### QGIS sanity check

5. **Export script created** — `scripts/export_qgis_sanity_check.py`.
   Produces classified TP/FP/FN/rejected GeoJSON layers from N=1
   PV output (572 candidates from `proposer-verifier-384`).

6. **Spatial accuracy** (Obs 210): Median match distance 5.0m
   (exactly 1 pixel at 5.02 m/px). 88% within 10m. VLM precision
   exceeds human volunteer digitisation accuracy.

7. **FP taxonomy** (Obs 211): 82 FPs decomposed into three explained
   categories — spot heights (29), overlap duplicates (18), water
   features (3). Remainder are high-confidence detections near
   reference mounds (overlap boundary effects).

8. **Composite symbol offset**: "Bench mark on burial mound" (fid 445)
   detected at 23.2m — just outside 20m buffer. Systematic centroid
   pull from adjacent symbols on composite map features.

### Prompt refinement (v2)

9. **v2 prompts created** — `propose_brief_v2.md` and
   `verify_adversarial_v2.md`. Added size criterion for spot heights
   (~5–7px vs ≥12px mounds) and colour exclusion for water features
   (blue = never a mound).

10. **v2 verifier effect** (Obs 212): Re-verified 572 candidates.
    At threshold 0.15: ΔF1=+0.071, ΔP=+0.129, ΔR=+0.046. The
    "adversarial budget" mechanism — concrete rejection criteria
    make the verifier more confident about real mounds too.

11. **Scale-dependent FP populations** (Obs 213): Spot height FPs
    are specific to 384px tiles — at 512px the symbols are below
    the VLM's detection threshold. Calibration at 512px correctly
    addressed 512px FPs; the 384px FP population is a legitimate
    scale-dependent emergence.

### Erratum E47 and controlled testing

12. **E47: Proposer prompt substitution** — discovered that all PV
    experiments used `detect_brief-text.md` instead of preregistered
    `propose_brief.md`. Created on 2026-01-20, refined 2026-02-03,
    never used. The H2 pilot reused Phase 2d detection outputs to
    save cost, and the pattern persisted.

13. **2×2 prompt matrix** (Obs 214): Initial ad-hoc test showed
    +21pp F1 from proposer framing. Controlled test (identical
    17-example config, 569-mound evaluation) showed ΔF1=−0.013
    (null). The ad-hoc result was confounded by example set
    difference (9 vs 17 examples). **Retracted** the framing
    claim; v2 verifier finding (Obs 212) unaffected.

14. **`propose_brief-text.json` config created** — clones
    `detect_brief-text.json` changing only the instruction file.
    Isolates the E47 instruction change.

15. **E47 N=1 evaluation** — `propose_brief` proposer + v1 verifier:
    F1=0.800 [0.765–0.831] vs original detect F1=0.813
    [0.780–0.844]. CIs overlapping. No significant difference.

### Code hardening

16. **Tile-size validation** — `4_detect_mounds_batch.py` and
    `lib_batch_api.py` now check first tile dimensions against
    configured tile_size. Errors on mismatch with actionable
    message. Prevents the 512/384 coordinate corruption bug.

17. **Batch mode added** — `4_detect_mounds_batch.py` now supports
    `--mode batch` using `lib_batch_api.run_batch_unit()`. Full
    lifecycle: JSONL build → upload → submit → poll → retrieve →
    parse. Includes `--run N` for multi-pass consensus.

18. **Audit** — `/audit` on both modified scripts. 1 critical
    (test breakage from validation), 4 medium, 4 low. All critical
    and medium issues fixed. 97/97 batch API tests pass.

19. **Output directory standard** — spec document at
    `docs/methodology/output-directory-standard.md`. Defines
    artefact types, gitignore policy, naming conventions.

### 55-map production run preparation

20. **Rasters reprojected** — 55 maps from EPSG:4326 to EPSG:32635
    via gdalwarp. 65 seconds on zbook. Output: 2.4 GB in
    `inputs/rasters/Russian1981_32635/`.

21. **Tiles generated** — 8,541 tiles at 384px (stride 336).
    4 minutes 38 seconds on zbook. Output: 2.0 GB in
    `inputs/tiles_384_55maps/`.

22. **Ground truth built** — 4,770 hairy-only student mounds in
    EPSG:32635. Output: `inputs/vectors/references/student-mounds-55maps.geojson`.

23. **Manifest and bounds** — tile manifest (8,541 entries) and
    evaluation bounds GeoJSON (8,541 polygons) generated.

### E47 N=5 batch run

24. **5-pass consensus run launched** — `propose_brief-text` proposer,
    Flash HIGH, T=0.7, 384px, batch mode. Run 1 complete (1,614
    detections). Runs 2–5 initially failed (network outage),
    resubmitted. Consensus → verify → evaluate pipeline deferred
    to next session.

### Observations added

- Obs 210: VLM spatial accuracy exceeds human volunteers (median 1px)
- Obs 211: FP taxonomy and composite symbol localisation
- Obs 212: v2 verifier +7pp F1 (adversarial budget mechanism)
- Obs 213: Scale-dependent FP populations (384px vs 512px)
- Obs 214: Full 2×2 matrix + CORRECTION (proposer framing is null)
- Erratum E47: Proposer prompt substitution (conservative deviation)

### Key findings

- **Obs 203**: Tile size as pipeline optimisation — 384px provides
  better raw material (high recall) for consensus+PV
- Headline buffer: 20m per preregistration, tolerance curve prominent,
  30m argued as empirically grounded

### Status

All analysis for the paper is complete. Next phase: paper writing.

## Session 63 — 2026-04-08 to 2026-04-10 (map-reader-llm)

55-map generalisation run: overnight pipeline execution, E47 v1/v2
analysis, gold-standard v2 recreation, evaluation bug fix, code
hardening, and statistical correction framework.

### Infrastructure and pipeline execution

1. **Smoke test** — validated end-to-end on 50 tiles (tile naming,
   raster resolution, coordinate conversion, verifier, evaluation).
   Caught double-nested tile directory issue; flattened from
   `map/map/*.png` to `map/*.png`.

2. **Batch mode** — initial approach hit Google's 2 GB file upload
   limit (8,541 tiles × ~320 KB/line = 2.75 GB). Added chunking
   support (`--max-batch-tiles 4000`) to split into 3 batch jobs.

3. **Batch queue congestion** — jobs spent 5+ hours in PENDING.
   Discovered and adopted Google's new Flex API (same 50% discount,
   synchronous 1–15 min latency). Implemented `--service-tier flex`.

4. **Flex execution** — 5 proposer runs completed (~4 hrs each).
   Throughput: ~1 tile/sec at 60 workers, saturating Tier 3 governor
   (RPM=14,400, TPM=14.4M). Zero 429 errors.

5. **Straggler cleanup** — 3-pass iterative cleanup (standard,
   longer backoff, safe-mode). Recovery: 99.9%. Safe-mode not needed
   (0 tiles required it — all failures were transient 503s, not
   token exhaustion). Final coverage: 8,540/8,541 at 5/5, 1 at 4/5.

6. **Verifier** — v1 adversarial on 8,942 consensus candidates,
   8,916/8,942 (99.7%). 26 failures recovered via cleanup pass.
   v2 adversarial also run for comparison (8,939/8,942).

### Code changes (13 commits)

7. **Evaluation generalisation** — `get_map_name()` regex (was
   hardcoded 4-map list), `--ground-truth` flag for
   `evaluate_pv_results.py`, auto-detect reference column.

8. **Incremental verifier write** (Issue #10) — `_save_probabilities_
   incremental()` every 100 candidates + resume logic. Prevents the
   530/607 data loss that occurred during gold-standard v2 run.

9. **Cleanup subcommand** (Task #11) — `run_pv.py cleanup` with
   iterative retries, safe-mode escalation, audit trail, dry-run.
   6 unit tests.

10. **Failure threshold scaling** — `MAX_ACCEPTABLE_TILE_FAILURE_RATE
    = 0.20` (was hardcoded 10 tiles). `MAX_SYNC_RETRIES` 0 → 3
    (restored default).

11. **Test fixes** — 5 pre-existing test failures resolved
    (`missing_tiles` → `missing_sources`, xfail for bootstrap
    interaction zeros, updated non-georeferenced tile assertions).

12. **Gitignore overhaul** — principled rule: track anything that
    costs API money, ignore locally regenerable. Selective unignore
    for 55-map and gold-standard outputs.

### E47 v1 vs v2 verifier analysis

13. **Full grid sweep** — 5 consensus levels × 4 buffers × threshold
    sweeps for both v1 and v2 verifiers on the E47 `propose_brief`
    data. v2 wins 8/8 at every level (sign test p=0.004).

14. **Pairwise permutation** — at 4-of-5: ΔF1=+0.017, p=0.039.
    Suggestive but doesn't survive multiple-comparison correction.

15. **Gold-standard recreation** — 5-pass `detect_brief-text` +
    both verifiers on 4-map data. v2 F1=0.885 vs v1 0.873 (+0.012)
    at 50m. Confirms v2 improvement on the optimal pipeline.

16. **55-map v1 vs v2** — ΔF1=+0.001 at 50m. v2 effect diminishes
    on broader datasets (Obs 217).

### 55-map generalisation results

17. **Primary result** (50m, T=0.15 carry-forward):
    F1=0.790, P=0.858, R=0.732.

18. **Generalisation gap**: −0.101 from gold standard (F1=0.891).
    Primarily recall loss (−0.112).

19. **Carry-forward threshold validated**: T=0.15 tied with T=0.20
    as optimal. No re-optimisation needed.

20. **Buffer sensitivity**: 20m→30m F1 jump of +0.132 (vs +0.027 on
    gold standard) reveals student GT spatial imprecision. 50m is
    the most meaningful tolerance for this comparison.

21. **Correction for student errors** (Obs 220): Adjusting for
    documented 5% student FN rate, corrected F1 ∈ [0.790, 0.810].
    Generalisation gap narrows to 0.081–0.101.

### Observations added

- Obs 215: v2 on optimal pipeline (+0.012 F1)
- Obs 216: 55-map generalisation results
- Obs 217: v2 effect is data-dependent
- Obs 218: straggler cleanup — safe-mode not needed
- Obs 219: architecture dominates prompt refinement
- Obs 220: correcting for student GT errors
- Obs 221: CI on student QA sample
- Obs 222: evaluation script generalisation bug

### Plans externalised

- `planning/dawid-skene-latent-truth.md` — latent class model
- `planning/candidate-review-app.md` — Streamlit review app
- `planning/verifier-cleanup-subcommand.md` — implemented this session

### Status

55-map generalisation study complete. E47 v1-vs-v2 analysis complete.
Gold-standard v2 recreation complete. All code fixes resolved. Next:
candidate review app, D-S model, paper writing.

## Session 64 — 2026-04-11 to 2026-04-12 (map-reader-llm)

D-S latent truth model, CRS bug fix, test pollution fix, full
calibration pipeline, H10/H12 experiments with statistical analysis,
and candidate review app.

### D-S latent truth model

- Implemented `scripts/analyse_dawid_skene.py` — two-annotator EM
  model with fixed student parameters (sens=0.95, spec=1.0)
- 26 tier1 tests, audit-clean after 5 fixes (surplus redistribution,
  CRS handling, dedup, log message, unused constant)
- Results: measured F1=0.790, simple correction F1=0.808,
  D-S posterior F1=0.814 (expected counts)
- Key finding: 2-annotator D-S can only estimate aggregate
  fractions, not per-item classifications. All 578 VLM-only items
  get the same posterior (0.318). Used `ensure_utm_crs` on read.

### Consensus GeoJSON CRS bug

- Found during D-S implementation: coordinate reprojection produced
  `inf` values because `merge_passes.py` wrote EPSG:32635 into
  GeoJSON without CRS metadata (GeoJSON spec mandates EPSG:4326).
- 5 reader scripts had accumulated `set_crs(allow_override=True)`
  workarounds; `lib_consensus.load_geojson_gdf()` had a coordinate-
  magnitude heuristic.
- Fix: reproject UTM→4326 at write time in `merge_passes.py`;
  extracted `ensure_utm_crs()` as canonical helper in
  `lib_consensus.py`; `extract_candidates.py` reprojects 4326→UTM
  for raster cropping.
- 6 scripts fixed, 2 tests updated, no regressions.

### Test pollution fix

- 8 reverify mock tests failed in full suite but passed in
  isolation — classic test ordering issue.
- Root cause: `test_batch_api.py` imports `google.genai.types`,
  caching it in `sys.modules`. Reverify tests mocked
  `sys.modules["google.genai.types"]` but production code uses
  `from google.genai import types`, which bypasses the sys.modules
  patch via parent attribute lookup.
- Fix: mock the full module chain (`google.genai` +
  `google.genai.types`).
- Full tier1 suite: 589 passed, 0 failed (was 580 + 9 failed).

### Generalised calibration pipeline (main deliverable)

Built across 5 sprints, 84 tier1 tests, 6 audit passes:

1. **`scripts/lib_calibration.py`** — shared library with
   `enrich_bounds_with_mound_counts`, `categorise_density`,
   `stratified_sample` (3-level hierarchical), `nested_subsample`
   (for H10 nesting), `score_difficulty_hp/hn`. 32 tests.
2. **`scripts/select_calibration_tiles.py`** — generalised tile
   selector with nested pool generation. 13 tests. Dry run verified
   on real data: 160 cal + 327 test = 487 total, perfect geographic
   balance (40/map), density-proportional at every nesting level.
3. **`scripts/discover_hard_cases.py`** — hard-case discovery from
   K detection passes with per-map Hungarian matching, cross-pass
   FP clustering. 17 tests. Fixed `gpd.pd.concat` fragility,
   relative FP threshold, CRS validation warning, dead parameter.
4. **`scripts/build_example_pool.py`** — diversity-optimised
   selection with spatial (500m radius) and grid-based same-tile
   penalties. 15 tests. Fixed HP granularity issue (grid ID instead
   of map name), recursive raster glob.
5. **`scripts/generate_prompt_configs.py`** — automated config
   assembly preserving canonical examples. 9 tests. Fixed examples
   path resolution (inputs/examples, not prompts/examples).

Tile-size-agnostic, dataset-agnostic. Seed of the automated
"map reading service" concept.

### H10/H12 experiment execution

**Calibration discovery** (API gate 1, $0.80):
- K=5 detection passes on 160 calibration tiles
- 63 HP candidates (48 borderline + 15 consistent FN) — 16×
  expansion from the 20-tile Phase 2 calibration
- 151 HN candidates
- Unlocked all 3 deferred experiments (H8 Scale-16/32, H9-C)

**Example pools** (no API):
- Baseline: pool_160_hp4hn4 (H8 Scale-8)
- H12 HN-heavy: pool_160_hp2hn6 (1:3)
- H12 HP-heavy: pool_160_hp6hn2 (3:1)
- H8 Scale-16: pool_160_hp8hn8
- H8 Scale-32: pool_160_hp16hn16
- All 5 crop sets extracted successfully, 0 failures

**Proposer runs** (API gate 2, $22.32):
- K=10 per config × 327 test tiles = 16,350 calls
- 88 parse failures across 50 runs (0.5%)
- 3-round retry cleanup: 88 → 11 → 4 → 2 remaining (99.99% recovery)

**Verifier runs** (API gate 3, $10.69):
- Adversarial verifier (v1) on vote≥2 candidates = 7,766 calls
- Zero failures
- Per config: ~1,500-1,600 candidates, ~$2 each

**Full sweep evaluation** (no API):
- 9 vote thresholds × 9 probability thresholds × 5 configs
- 315 evaluation points at 20m buffer
- Best F1: 0.885 for baseline and Scale-32, 0.883 HN-heavy,
  0.882 Scale-16, 0.870 HP-heavy

**Statistical analysis** (no API, ran on laptop as one-time
exception to sapphire rule — user was travelling):
- K=5 replicate sweeps (runs 1-5 and runs 6-10 independently)
- Bootstrap 95% CIs at vote≥6, prob≥0.15
- Round-robin pairwise permutation tests (10k iterations each)
- Result: **zero significant differences** at α=0.05 across all
  10 pairs. HP6:HN2 (HP-heavy) vs baseline closest at p=0.061.

### Candidate review app

- `scripts/review_candidates.py` — Streamlit app for human review
  of measured FPs from 55-map generalisation data
- 6-way classification: burial mound / settlement mound / bench mark
  on mound / trig point on mound / not a mound / uncertain
- Keyboard shortcuts: `f/d/s/a` (left hand) for positive types by
  frequency, `j/k` (right hand) for negative/uncertain
- Resume from CSV, undo last, running corrected P and F1 (computed
  from matching results, not hardcoded)
- Audit-clean after 3 fixes (hardcoded recall, CSV column validation,
  measured baseline)
- Ready to use but not yet run against real data

### Symbol taxonomy investigation

- Student data uses "Hairy black diamond" and "Hairy black square"
  descriptively for what the legend calls "Bench mark on burial mound"
  (a single symbol that students described inconsistently)
- Cropped 6 examples of "Hairy black diamond" from source rasters
  to verify — all matched the bench-mark-on-mound legend symbol
- Settlement mounds (5 in gold standard) are distinct symbol but
  students likely classified them as "Hairy brown circle" (lumped
  with burial mounds) — no specific "settlement mound" option in
  student taxonomy
- Raw student data: 8,343 records; filtered (hairy only) 4,770
- `MapMounds17_18LLgood.csv` has 93 "Hairy black square" entries
  missing from the `Entity-*.csv` files — source of the student-
  mounds-55maps.geojson filtered file

### Key observations added to working notes

- Obs 223: D-S 2-annotator identifiability
- Obs 224: Consensus GeoJSON CRS bug
- Obs 225: Test pollution via Python module caching
- Obs 226: Calibration pool expansion unblocks deferred experiments
- Obs 227: H10/H12 null results — verifier dominates library composition

### Deferred to Session 65

- Leaderboard comparison: round-robin permutation tests against
  previous text-track and image-track configurations
- Assessment of whether F1=0.885 beats or matches previous best
- Paper integration of H10/H12 null results (implications for H8,
  H12 hypothesis discussion)

### Infrastructure additions

- `inputs/calibration/h10-384/` — permanent calibration/test split
  (160/327) with nested pools 20⊂40⊂80⊂160 at seed=42
- `outputs/h10/evaluation/` — K=10 proposer detections per config
- `outputs/h10/consensus/` — consensus at thresholds 1/2/4/5/6 of 10
- `outputs/h10/verifier-crops/` — 7,766 crops for verifier
- `outputs/h10/verified/` — verifier probabilities per config
- `results/h10/sweep_results.json` — 315-point grid evaluation
- `results/h10/k5_replicate_sweep.json` — independent K=5 replicates
- `results/h10/statistical_analysis.json` — bootstrap CIs + pairwise

### Total API spend

| Phase | Calls | Cost |
|-------|-------|------|
| Calibration discovery (K=5) | 800 | $0.80 |
| H10/H12 proposer (K=10 × 5) | 16,350 | $22.32 |
| Retry cleanup (3 rounds) | ~170 | ~$0.10 |
| Verifier (7,766 candidates) | 7,766 | $10.69 |
| **Total** | **~25,000** | **~$33.91** |

### Status

Calibration pipeline built and tested. H10/H12 experiments complete
with statistical analysis. Review app ready. Session 65 will tackle
the leaderboard comparison and paper integration.

---

## Session 65 — 2026-04-13 (map-reader-llm)

Consensus dedup audit (Obs 228), Weighted Boxes Fusion library
implementation, two WBF validation runs (hp4hn4 tie, production
run +0.08 on non-canonical baseline), buffer-sensitivity finding
(Obs 232), and Decision 26 committing to the methodology.

### Obs 228 — Consensus dedup radius audit

- Obs 227 verifier-independence probe turned up ~346 intra-config
  "collisions" at 20 m single-link cross-config clustering. Initially
  read as "single-link is the wrong algorithm"; Shawn pushed back with
  the cartographic constraint that mound symbols are ~75 m in diameter
  and never overlap, so centroids must be ≥75 m apart.
- Empirically verified: minimum GT–GT distance across all 569 reference
  mounds is **68.1 m**; p1 is 72.0 m; only 5 pairs within 75 m in the
  entire corpus. Shawn's claim confirmed to within 7 m.
- Magnitude diagnostic (`scripts/diagnose_consensus_dedup_radius.py`):
  ~11 % of GT mounds (per config) have ≥2 final candidates within the
  attribution-safe 40 m radius → the upstream greedy-ball dedup at
  20 m leaks same-mound duplicates because centroid drift can exceed
  20 m. Drift distribution: p50 = 7 m, p90 = 23 m, p99 = 37 m.
- Visual verification (`scripts/export_dedup_visual_check.py` + QGIS)
  on a 6-mound cemetery caught that a naive 60 m min-separation
  variant **lost a real mound** by over-merging adjacent cemetery
  mounds into a single super-cluster. The aggregate multi-GT metric
  was blind to this failure because both mounds fell within 40 m of
  the merged centroid, so both appeared "covered".

### WBF library + Variant C parameters

- Ran `/review-implementation` protocol on the dedup problem →
  Weighted Boxes Fusion (Solovyev et al. 2019) is the canonical
  modern approach for multi-pass ensemble aggregation. Widely cited,
  well-tested reference implementation.
- Built `scripts/lib_fusion.py` implementing WBF with a vote-aware
  minimum-separation post-step. 33 tier-1 tests covering IoU
  (including the 68 m cartographic-floor safety property), size
  filtering, WBF clustering (with and without merges), vote-aware
  anchoring, end-to-end pipeline.
- **Variant C finalised parameters** after visual iteration: IoU
  threshold 0.25, min-separation 30 m, vote-aware with anchor ≥
  vote_t (which equals 6 for 10-pass or 4 for 5-pass pipelines),
  box size filter [20, 200] m per dimension, area [400, 40000] m².

### Obs 230 — hp4hn4 WBF statistical equivalence

- Applied Variant C to `outputs/h10/evaluation/pool_160_hp4hn4/run_{1..10}/`
  (detect_brief-text, minimal, T=0.0, 10 passes)
- Extracted 1,467 verifier crops, ran v1 verifier (minimal adversarial)
  in Flex mode (~$5, 1 cleanup retry for a single failed candidate)
- Full (vote_t × prob_t) F1 sweep at 20 m buffer → best WBF F1 = 0.8800
  at vote=7, prob=0.15
- Bootstrap 1000-iter CI: greedy [0.8483, 0.9165], WBF [0.8452,
  0.9108] — overlap ~97 %
- Paired permutation test (n=10,000): **ΔF1 = 0.0053, p = 0.6019**,
  with 11 greedy wins, 11 WBF wins, 305 tied (exact symmetric split)
- Interpretation: statistical tie. Decision 26 written: retain
  greedy-ball as primary, WBF as methodological robustness check.
  Protocol classification: not a deviation (preregistration
  specifies Hungarian matching tolerance and consensus voting
  framework but not the clustering algorithm).

### Obs 231 — Production-run WBF comparison (⚠ NON-CANONICAL BASELINE)

- Applied Variant C with anchor=4 to
  `outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text/run_{1..5}/`
  — I assumed this was the 4-map gold-standard production run
- Extracted 3,890 verifier crops, ran both v1 and v2 verifiers in
  Flex mode (~$16 total, 1 cleanup retry on v1)
- Full (vote_t × prob_t × buffer_m) sweep across 5 buffers:
  - greedy v2 best F1 = 0.8273 at 50 m
  - WBF v2 best F1 = 0.9108 at 50 m
  - **ΔF1 = +0.083, paired permutation p = 0.0000** at every buffer
  - CIs do not overlap on either verifier at any buffer
  - Tile wins: ~25 greedy, ~61–72 WBF, ~390–400 ties per test
  - Effect is universal across all 4 maps (+0.057 to +0.196 ΔF1)
  - Precision-driven: WBF precision 0.90–0.99 vs greedy 0.52–0.82;
    recall flat or marginally lower under WBF
- **Correction discovered at session end**: the `e47-propose-brief/`
  directory contains a **7-file `propose_brief-text` one-off
  experiment**, not the canonical production run. The canonical run
  uses `detect_brief-text` (53+ files across many directories) and
  lives at `outputs/h11/gold-standard-v2/proposer/detect_brief-text/`.
  My WBF-vs-greedy comparison is measured against the wrong baseline.
  The +0.08 finding is real for that specific loose-consensus
  propose_brief-text pipeline but does not directly validate WBF for
  the paper headline. Correction note added to the top of Obs 231.
- **Priority 1 for Session 66**: run the corrected apples-to-apples
  comparison against `gold-standard-v2/detect_brief-text` + existing
  v1/v2 verifier probabilities, which will cost ~$6–10 Flex and
  reuse the local greedy baseline without re-running.

### Obs 232 — Leaderboard rankings are buffer-dependent

- Discovered while deciding the buffer for the top-20 round-robin
  pairwise permutation tests. Shawn asked whether 20 m rankings are
  stable across buffers.
- Analysed `results/paper-eval/pv/*/buffer_sensitivity.json` (8
  production configs at buffers {20, 30, 40, 50} m) and the existing
  `results/pairwise/leaderboard-{20,30}m/` data (9 rank flips between
  20 m and 30 m, all in one direction).
- Found 3 additional rank flips between 30 m and 40 m (none between
  40 m and 50 m — ranking stable beyond 40 m). Every flip is
  **image-track gaining at wider buffers**. Text-track F1 saturates
  at 30 m; image-track keeps climbing to 40 m.
- Most dramatic case: Flash HIGH image 3-of-5 climbs rank 7 at 20 m
  → rank 6 at 30 m → **rank 4 at 40/50 m**. A 3-rank gain across the
  buffer sweep.
- Mechanism hypothesis: image-track proposer centroids drift further
  from true mound centres (~40 m tail) than text-track centroids
  (~20 m tail), matching half the 75 m mound symbol diameter.
  Image-track may be fixating on a salient feature within the mound
  symbol (sunburst ray end, central dot) rather than the geometric
  centre. Testable via per-map mean offset vector diagnostic —
  deferred.
- **Implication for round-robin plan**: must run at 3 buffers
  {20 m, 30 m, 40 m}. Text-track top-3 is stable across buffers;
  image-track ranking requires 40 m. Cross-track comparison is
  buffer-dependent — pick a primary buffer per track.

### Medium-vf is not the paper's best config

- Investigated why the F1 = 0.885 headline is associated with the
  medium-thinking verifier when minimal-vf beats it at the same
  consensus level.
- Leaderboard data: `flash-high-text 4-of-5 + min-vf` F1 = 0.8908 at
  30 m beats `flash-high-text 4-of-5 + medium-vf` F1 = 0.8850.
  `flash-high-text 16-of-30 + min-vf` F1 = 0.9044 (leaderboard rank 1).
- The "F1 = 0.885 medium-vf" headline is likely a historical
  preregistered result that was later surpassed by minimal-vf but
  stuck around as the remembered number.
- Priority 2 (sapphire medium-vf comparison) downgraded accordingly
  — no longer the paper headline validator.

### Decision 26

Committed to `docs/methodology/preregistration/decisions-log.md`.
Retain greedy-ball at 20 m as primary consensus aggregation method
for all preregistered phases; adopt WBF as methodological robustness
check; recommend WBF as preferred default for future work. Not a
protocol deviation (preregistration doesn't specify the clustering
algorithm). Pending revision after Priority 1 canonical test.

### Commits + push

Session produced 10 commits:

1. `feat(wbf): add Weighted Boxes Fusion library` — lib_fusion.py +
   tests (33 tier-1)
2. `feat(wbf): add WBF runners, F1 sweep, and greedy comparison
   scripts` — 5 runner scripts
3. `feat(h10): add dedup audit + verifier independence probe
   scripts` — 4 scripts + tests
4. `feat(wbf): add Obs 228-231 result artefacts` — JSON results
5. `feat(wbf): add QGIS visual-check layers` — 10 GeoJSONs
6. `feat(wbf): add WBF candidate manifests, geojsons, and verifier
   probabilities` — 28 output files + `.gitignore` crop exclusion
7. `feat(wbf): add missed e47-propose-brief-n5 WBF candidates
   geojson`
8. `docs(wbf): Decision 26, Obs 228-232, and WBF continuity doc`
9. `chore(gitignore): ignore verifier cleanup backups and WBF HTTP
   logs`
10. `feat(h10): add H10/H12 raw proposer data (calibration +
    evaluation)` — 2.6 MB + 53 MB of Session 64 raw data committed
    for reproducibility

All pushed to `origin/main`. Working tree fully clean — every file
now either tracked or formally gitignored.

### Cost summary

| Stage | API calls | Cost |
|---|---|---|
| hp4hn4 verifier run (v1 only) | 1,467 | ~$5 |
| hp4hn4 verifier cleanup (1 retry) | 1 | ~$0.01 |
| e47-propose-brief v1 verifier | 3,890 | ~$8 |
| e47-propose-brief v2 verifier | 3,890 | ~$8 |
| Cleanup retries | 1 | ~$0.01 |
| **Total** | **~9,250** | **~$21** |

### Status

WBF library built, tested, and two validation variants run. Decision
26 committed. Obs 228–232 written. Full continuity document at
`planning/2026-04-13-wbf-investigation-continuity.md`. Priority 1
for Session 66: run the corrected canonical WBF comparison against
`gold-standard-v2/detect_brief-text` (~$6–10 Flex). Priority 2–7
queued in the continuity doc.

### Contextual assumptions

- The "production run" label was used throughout the session to
  refer to `outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text/`
  on the assumption it was the canonical 4-map gold-standard run.
  This assumption was wrong — the canonical run is
  `outputs/h11/gold-standard-v2/proposer/detect_brief-text/`. The
  correction is documented in the Obs 231 correction note and in
  the continuity doc.
- The "F1 = 0.885 headline" is associated with multiple configs
  depending on the source memo: MEMORY.md associates it with v2
  minimal-vf; `results/paper-eval/pv/` associates it with
  medium-vf. Both are valid results at different operating points;
  the "headline" label is a session-to-session accumulation rather
  than a single canonical number.
- The `gold-standard-v2/` directory naming is confusing: "v2"
  refers to the recreation script version
  (`scripts/11maps-gold-standard-v2.sh`, the second iteration),
  not the proposer version. The proposer inside is the standard
  `detect_brief-text`.

---

## Session 66 — 2026-04-13/14 (map-reader-llm): Canonical WBF Priority 1, H10/H12 retraction, and the three code-side fixes

**Overview**: Executed Priority 1 from the Session 65 continuity
doc (canonical WBF vs greedy on `gold-standard-v2/detect_brief-text`),
pivoted into a leaderboard rebuild, surfaced and retracted a major
scientific error (the H10/H12 pool sweep was run with a text-only
config, so the library was never transmitted), wrote a 600-line
failure retrospective, and implemented three code-side
infrastructure fixes that move the verification protocol from
memory into code. Session spans two days because of multiple
/exit + resume cycles, but the work was continuous. Six commits
pushed to `main`.

### Accomplishments

**Priority 1 — canonical WBF vs greedy (Obs 233)**. Added
`gold-standard-v2-detect` entry to `SPECIAL_CONFIGS` in
`fuse_detections_wbf.py`, ran WBF Variant C on the 5-pass canonical
detect_brief-text data, extracted 1,318 crops after filtering to
vote ≥ 2, ran v1 and v2 adversarial verifiers via Flex (~$5–6
spend, 0 failures), and executed a full (vote_t × prob_t × buffer_m)
sweep via a new `compare_wbf_vs_greedy_canonical.py`. Headline:
canonical WBF v1 at 50 m = F1 **0.9074** [CI 0.883, 0.930] vs
greedy-v1 F1 0.8734 (ΔF1 +0.034, p=0.001). Mechanism is
**recall-driven**, opposite of the precision-driven pattern from
Obs 231 on the non-canonical propose_brief-text pipeline. The
+0.034 F1 at 50 m ties the published leaderboard #1
(`flash-high-text 16-of-30 + min-vf` F1=0.9044) using K=5 instead
of K=30 — a 6× proposer-side compute reduction for matching
headline F1 conditional on swapping greedy for WBF.

**Leaderboard rebuild (partial) — 327-tile H10-clean subset**.
Built `inputs/vectors/bounds/384/h10_test_bounds.geojson` from H10's
`test_set` selection (327 tiles = 487 full-eval minus H10's own
160-tile calibration pool), wrote `scripts/score_leaderboard_cells.py`
as a universal scorer with detection pre-filtering, and scored the
canonical gold-standard-v2 configs (greedy v1/v2, WBF v1) plus all
five H10 pools at x-of-10 and x-of-5. Discovered that the H10
pools "beat" canonical by +0.07 F1 on the 327-tile universe,
drafted Obs 234 attributing this to a "library effect", and
recommended revising the paper headline. **This was wrong** — see
retraction below.

**H10/H12 retraction (Obs 235)**. Shawn asked, "if H10 was text-only,
what were the 'hard examples'?" A config-file check revealed
`detect_brief-text_pool_160_*` has `include_example_images: false`,
and a trace through `4_detect_mounds_batch.py:816` confirmed the
example loop is skipped entirely when the modality flag is false.
**The H10 library was never transmitted to the API**. The
+0.07 F1 "library effect" is impossible because the library is not
reaching the model. Obs 234 was retracted the same day; Obs 227
(from a prior session) was retroactively retracted for the same
reason; Obs 230 (hp4hn4 WBF equivalence) carries a partial
correction note (the WBF-vs-greedy comparison is valid, the "on
hp4hn4" framing is not). ~$33 of API spend was on a tautological
experiment. Full retrospective written to
`docs/notes/reflections/2026-04-14-h10-h12-config-intent-retrospective.md`.

**Three code-side infrastructure fixes**. After the retraction,
Shawn asked for structural prevention rather than discipline-based
rules. Implemented:

- **Fix #1 — Hypothesis-aware config generator**. New module
  `scripts/lib_hypothesis_requirements.py` (HYPOTHESIS_REQUIREMENTS
  table, NO_OP_RULES table, DIFFERS_FROM_BASE sentinel,
  validation/diff/report helpers). `generate_prompt_configs.py`
  modified to accept `--hypothesis`, run preflight validation
  before any file writes, raise `ConfigIntentMismatchError` on
  failure with a structured refusal report naming the misaligned
  field and suggesting a fix, write a new `base_config` field into
  the generated config for downstream diff tools. Refusal leaves
  zero partial artefacts on disk.

- **Fix #2 — Launch-time experiment_intent.md writer**. New module
  `scripts/lib_experiment_intent.py`. `write_experiment_intent()`
  records hypothesis, varied factor, base config, verified modality
  values (with pipeline defaults applied), a Transmission check
  section with a bold warning when no-op changes are detected, a
  diff table, and provenance. Handles rerun semantics: matches on
  key fields or warns on mismatch without overwriting.

- **Fix #3 — Pre-run config diff with interactive gate**.
  `run_launch_checks()` in the same module, wired into both the
  realtime (line 937) and batch (line 1307) dispatch paths of
  `4_detect_mounds_batch.py`. Diffs variant vs base, applies
  no-op rules, prompts `[y/N]` with reference to Obs 227/234/235.
  Dry-run downgrades to non-blocking warning. New
  `--skip-intent-check` CLI flag for automation.

- **70 new tests**: 32 in `test_lib_hypothesis_requirements.py`,
  15 in `test_lib_experiment_intent.py`, 12 additional in
  `test_generate_prompt_configs.py`, 2 tier-2 integration tests in
  a new `test_integration_intent_check.py`. All pass. Full tier-1
  regression: 782 passed, 74 deselected, 3 xfailed.

- **/audit pass**: ran the audit skill across all 4 new and 4
  modified files. Found three minor issues (mutable class
  attribute in `_EmptyRequirement`, bare `Exception` catch in
  frozen-dataclass tests, missing `ValidationFinding` immutability
  test); all fixed. Two agent-reported "critical" findings
  rejected with written justification as false positives.

**Sapphire lightweight sync**. Shawn confirmed access to sapphire
and asked for the lightweight pv-diag-384 artefacts. Pulled 5
targeted verifier directories (medium-vf historical headline,
leaderboard #1 16-of-30, leaderboard #2 4-of-5, 9-of-10 reference,
flash-high-image-3-of-5) and all 30 consensus geojsons via rsync
with `--exclude='crops/'`. Total ~19 MB (4 MB verified + 15 MB
consensus). Force-added under the bulk `outputs/h11/pv-diag-384/`
gitignore to avoid committing the 3 GB of PNG crops.

### Key results

- Canonical WBF v1 @ 50 m: **F1 = 0.9074** [0.883, 0.930] — ties
  published leaderboard #1 with K=5 instead of K=30
- Canonical WBF v1 @ 30 m: F1 = 0.8981, ΔF1 vs greedy-v1 = +0.027
  (p=0.008)
- Canonical WBF v2 @ 50 m: F1 = 0.9074 [0.885, 0.928], ΔF1 vs
  greedy-v2 = +0.022 (p=0.025)
- H10/H12 experimental arm: **retracted** (no preregistered
  conclusion supported by the data as run; ~$33 API wasted)
- 70 new tests added, all passing; 782 tier-1 regression clean
- 6 commits pushed to `main`

### Issues found

- The H10/H12 pool sweep was misconfigured (`include_example_images:
  false` inherited silently from the text-only base config) —
  documented in Obs 235 and the retrospective
- Two sessions in a row (65 and 66) produced the same failure shape:
  a finding written up with a ready mechanism, missing a config-
  level verification, caught by Shawn's factual question after the
  fact. The code-side fixes target the specific cause but the
  pattern is worth watching for on other axes
- CLAUDE.md's "verify on surprise" rule has a blind spot for
  non-surprising inherited findings, now patched by Rule 5 in
  `feedback_config_intent_verification.md`

### Pending work

- Build the leaderboard assembly script (task #14) using the new
  327-tile scorer + the just-pulled pv-diag-384 cells
- Tile-set consistency audit across all experiments (task #15)
- Decision 26 amendment or Decision 27 — depending on how the
  leaderboard rebuild resolves WBF's role in the paper
- Resume the leaderboard round-robin pairwise permutation tests
  (top-20 per buffer, per track) once the cells are assembled

### Commits pushed

1. `0dede119` feat(wbf): canonical detect_brief-text WBF vs greedy
   on gold-standard-v2
2. `92257c34` feat(leaderboard): 327-tile H10-clean subset scorer
   and canonical cells
3. `e82de0a9` docs(reflections): Obs 233-235, H10/H12 retraction,
   and config-intent retrospective
4. `54bfe8f4` feat(infra): hypothesis-aware config gate and
   launch-time experiment-intent check
5. `5b82e084` data(pv-diag-384): commit lightweight artefacts from
   sapphire

### Contextual assumptions

- The decision to retract H10/H12 rather than re-run it was based
  on the observation that text-only `detect_brief-text` numbers
  are already known from existing K=30 sweeps. If those K=30 runs
  were later found to be misconfigured in a similar way, this
  decision would need to be revisited.
- The `/audit` skill's two "critical" findings were rejected as
  false positives because the auditor misread the code order
  (directory creation via intent-md writer vs the explicit mkdir)
  and miscounted the post-build revalidation's file-write
  ordering. If the project's audit workflow later formalises
  around those findings, the justification for rejection should
  be reviewed.
- The ~$33 wasted on H10/H12 is a sunk cost, but roughly 2/3 of
  the experimental arm's output survives: the WBF Variant C
  parameter calibration, the WBF-vs-greedy aggregation comparison
  on K=10 data, the 327-tile evaluation universe, and most
  importantly the retrospective itself as a teaching artefact.
  The net accounting is "mostly productive, partially wasted".
- The code-side fixes deliberately do NOT enforce verification
  on the `hypothesis` field being present in the generated
  config — the hypothesis field is still human-authored metadata,
  not a machine-enforced contract. A future strengthening could
  make `--hypothesis` required for any config that uses a
  hypothesis-tagged base. Deferred as out-of-scope.

---

## Session 68 — 2026-04-15 (map-reader-llm): H8 v2 library-composition re-run, strong null, bug found at end of session

### Completed

1. **H8 v2 scaffolding** — seven condition configs, study YAML, errata E51
   (15 deviations from the original Phase 2c H8), audit-config audit
   (`reports/configuration-audit-2026-04-15-h8-v2.md`), Phase 0 archival of
   v1 pools and retracted configs to `archive/h10-v1-*/`.

2. **Infrastructure fixes uncovered during setup**:
   - **Edge-of-raster crop filter** added to `scripts/build_example_pool.py`
     (`--exclude-edge-crops`, default on). Found three off-size crops in
     `pool_160_hp16hn16` during the pre-launch audit; re-mined both
     `pool_160_hp8hn8` and `pool_160_hp16hn16` under the filter, preserving
     prefix nestedness (verified by byte-hash).
   - **Thread pool size fix** in `scripts/4_detect_mounds_batch.py`. The
     hardcoded `pool_size = 60 if governor else workers` was the binding
     constraint at Tier 2 (observed peak 4.12 M TPM = 60 workers × 60/17 s
     latency × 20 K tokens/req, matching derivation to three significant
     figures). Changed to `max(60, workers)` when governor is active.
     Backward-compatible; `--workers 250` now actually works.

3. **H8 v2 launch on sapphire** — 6 new conditions × K=5 passes (Scale-8
   was originally to be reused from H10 v2 `pool_160_hp4hn4`, then re-run
   mid-session per Shawn's unified-pipeline instruction). Total 9,810 API
   calls, 1 h 24 min wall time, zero 429s, 97.6 % peak cache hit rate
   (Scale-32), 72 % peak Tier 3 TPM utilisation (14.4 M / 20 M). Realtime
   + flex + cache throughout; `--workers 250`. Google-genai SDK on sapphire
   upgraded 1.68.0 → 1.71.0 pre-launch to restore flex-tier support (Obs 20
   regression resolved).

4. **Aggregation and evaluation** (local analysis pipeline on sapphire):
   - WBF Variant C for all 7 conditions via the existing
     `scripts/fuse_detections_wbf.py` (added 7 `SPECIAL_CONFIGS` entries
     for `h8v2-*`).
   - Greedy threshold sweep (t=1..5) for all 7 conditions via
     `scripts/merge_passes.py --sweep`.
   - 42 evaluations (7 WBF + 35 greedy) via `scripts/evaluate_detections.py`
     at 20 m buffer, 1000 bootstrap, on the 327-tile H10 test set.
   - **Bug fix**: `scripts/evaluate_detections.py` crashed on WBF output
     with "cannot reindex on an axis with duplicate labels" when a
     detection intersected multiple overlapping tile bounds (384 px tiles
     with 336 stride overlap by 48 px). Added `keep="first"` deduplication
     after the sjoin.

5. **Preregistered contrasts with BH-FDR** — 7 tile-level permutation tests
   (C1–C3, B1, S1–S3) via `scripts/pairwise_permutation_test.py --mode
   geojson`, 10,000 permutations each, seed 42, at greedy t=4. BH-FDR
   applied at q=0.05 across the 7 contrasts via the new
   `scripts/apply_fdr_h8v2.py`.

6. **Sanity check**: fresh H8 v2 Scale-8 vs existing H10 v2
   `pool_160_hp4hn4` at greedy t=4: F1 = 0.710 and 0.717 respectively,
   ΔF1 = 0.007, within sampling noise. The aggregation + evaluation
   pipeline is internally consistent.

7. **Post-launch observability bug found and fixed**: `items_failed: 1`
   appeared in two runs (canonical run_2, plus-hp run_4) despite
   `finish_reason_counts: {success: 327}`. Investigation showed the same
   tile was logged in BOTH `completed_items` AND `failed_items`. Root
   cause: `log_success()` was called at line 562 before JSON parse /
   rasterio / feature extraction, and `log_failure()` was called later
   via the inner or outer exception handler when those downstream steps
   threw. Fix (`6a7c3ed8`): move `log_success()` to just before
   `return features` so success is logged only after the full pipeline
   completes.

8. **Observation 238** written for `working-notes.md` — 213-line entry
   documenting the null result, the sanity check, the per-tile tie
   pattern (260–280 of 327 tiles tie on every contrast), the domain
   interpretation (library axis closed), and methodological caveats
   (proposer-only, B1 is the largest weak signal, cost estimator
   unreliable).

9. **Four memories** captured via `/remember`:
   - `gotcha` / cost-estimation: `lib_llm_metadata.py` `estimate_cost()`
     ignores flex, cache, and thinking-token billing.
   - `pattern` / parallelism: Tier 3 pool-size rule
     (`≥ target_rpm × avg_latency / 60`); use `--workers 250`.
   - `architecture` / pool mining: greedy diversity selection is
     prefix-preserving byte-identically with fixed seed.
   - `provenance` / SDK: google-genai ≥1.69.0 forwards
     `service_tier='flex'` correctly.

### Key results

- **Null across all 7 preregistered contrasts.** Smallest raw p =
  0.164 (B1, HP-only vs balanced at size 13), nowhere near significant
  even uncorrected. All BH-adjusted p-values ≥ 0.83.
- **Spread across 7 conditions at fixed greedy t=4: 0.040 F1.** Best:
  Scale-4 at 0.733 [0.680, 0.777]; worst: Scale-16 at 0.693. Every CI
  contains every other condition's point estimate.
- **Per-tile pattern**: 257–276 of 327 tiles tie on every contrast;
  the 51–70 tiles that differ split roughly 50:50 between conditions.
- **Combined with H10 v2 null (Obs 236)**, H8 v2 closes the library
  axis: pool size, composition, and scaling all null at the proposer
  stage.
- **Tier 3 parallelism unlocked**: `--workers 250` saturates 72 % TPM
  / 72 % RPM, 2 min 18 s wall time per 327-tile K=1 pass (vs ~25 min
  at the old 60-worker cap).

### Decisions

- **Scale-8 re-run rather than symlinked** from H10 v2. Shawn reversed
  the original reuse decision mid-session to produce a self-contained
  H8 v2 output tree. The re-run also served as the pipeline sanity
  check (two independent K=5 draws at identical settings converged to
  ΔF1 = 0.007).
- **Edge-exclusion default on** in `build_example_pool.py`. Resolves
  the Scale-32 dimensional-uniformity confound from the audit.
- **No verifier runs** on H8 v2 conditions. The library-axis null is
  as tight as this experimental design can make it; the verifier only
  compresses noise (cf. H10 v2 Obs 236), and Scale-8 already has its
  post-verifier number via the existing H10 v2 pool_160_hp4hn4 data.
- **H12 deferred** — given H8 null, H12 is very likely null too.
  Shawn proposed running only the two extremes (R1 = 2:6, R3 = 6:2)
  and reusing R2 (= Scale-8) for ~$34 meta-estimated, but deferred to
  a fresh session with clearer billing data.
- **`items_failed` renamed-in-spirit by the fix** — the counter now
  correctly reflects terminal failures rather than retries or
  downstream-exception-after-valid-response cases.

### Commits pushed

1. `85315cfa` archive(h10): move v1 H10/H12 pools, hard-cases, and
   retracted configs (91 files via `git mv`)
2. `f9efabfc` feat(detect): edge-of-raster exclusion + pool-size fix
   for governor mode
3. `e575a57d` feat(h8-v2): seven-condition library-composition re-run
   at 384 px (7 configs, study YAML, audit report, E51, 162 files)
4. `5a9db98d` feat(wbf): register H8 v2 conditions in SPECIAL_CONFIGS
5. `99ee2600` fix(eval): deduplicate spatial join when bounds tiles
   overlap
6. `23df1a44` feat(analysis): H8 v2 summariser + BH-FDR applier
7. `b57cf6c2` data(h8-v2): complete Phase 2.8 acquisition + analysis
   (376 files from sapphire — aggregation outputs, evaluations,
   permutation tests, FDR summary)
8. `88d9d9a0` docs(obs-238): H8 v2 library null — all 7 contrasts fail
   after BH-FDR
9. `6a7c3ed8` fix(detect): log tile success only after full processing
   succeeds (the end-of-session bug fix)

### Cost

- Meta-reported: ~$107.60 total across 9,810 H8 v2 calls + ~$16.93
  for the Scale-8 re-run (also counted in the 9,810). These figures
  are known to be unreliable — see memory
  `2026-04-15-ffa433f8e5f6` and Obs 238's methodological caveat
  section.
- Real billing: pending Google Cloud console refresh. Shawn's preview
  at end-of-session: "several hundred dollars today" across this and
  other work, implying the meta under-reports (probably via
  thinking-token billing at the output rate).

### Issues found

- **Thread pool hardcap** (`pool_size = 60` regardless of `--workers`)
  was leaving ~80 % of Tier 3 capacity on the table. Fixed in
  `f9efabfc`.
- **Edge-clipped crops** in `pool_160_hp16hn16` (3 of 32) created a
  Scale-32 dimensional confound. Fixed in `f9efabfc` + re-mine.
- **Spatial-join dedup** in `evaluate_detections.py` crashed on WBF
  output. Fixed in `99ee2600`.
- **`log_success()` ordering** caused double-logging of tiles that
  returned valid API responses but failed downstream processing.
  Fixed in `6a7c3ed8`. (This bug survived the Session 66 `/audit`
  pass — see the abductive-reasoning.md entry for why.)
- **`estimate_cost()` fundamentally incomplete** — no flex, no cache,
  no thinking-token accounting. Documented but not fixed this session.

### Pending work

- Real-billing reconciliation of the H8 v2 run once Google Cloud
  catches up.
- Patch `lib_llm_metadata.estimate_cost()` to apply flex + cache
  discounts and include thinking-token billing.
- Fresh `/audit` pass on code modified since Session 66 (Shawn will
  do this in a new session).
- Decision on running H12 (R1 + R3 extremes, reusing Scale-8 for R2)
  once real billing is known.
- Observation 238 is the primary scientific artefact; a paper-section
  draft for the library-axis closure (H10 + H8 v2, with H12 either as
  "deferred" or as a third null) is ready to be written whenever
  paper work resumes.

### Contextual assumptions

- **Cost figures are quoted from the meta-estimate throughout this
  log**, and the meta-estimate is known to be unreliable (details in
  Obs 238 and the gotcha memory). Future readers should treat the
  ~$107 and ~$34 figures as order-of-magnitude indicators, not
  accurate accounting. The real billing console is authoritative.
- **The "Scale-8 reuse" decision was reversed mid-session.** The API
  gate proposal (v1 and v2) originally planned to reuse H10 v2
  `pool_160_hp4hn4` as the Scale-8 condition (saving ~$17). Shawn
  reversed this during Phase 2.6 in the interest of a self-contained
  unified pipeline. The re-run value came partly from the
  cross-check it enabled (two independent K=5 draws agreeing to
  within 0.007 F1), which was not anticipated in the reversal
  rationale but turned out to be load-bearing for trusting the
  whole analysis.
- **All commits on sapphire used `git -c user.name=... -c
  user.email=...`** as an inline override because sapphire's git
  config did not have a user identity set and I did not want to
  modify the persistent config. The commit `b57cf6c2` is authored
  correctly as a result.
- **The pre-existing uncommitted files** in `git status` at the end
  of the session (`M docs/notes/user_observations.md`, two `??`
  `outputs/h10/evaluation-v2/pool_*_hp4hn4/crops/` directories) are
  from sessions before this one and were deliberately not touched.
- **The `items_failed` bug was in the production code during the
  H8 v2 run.** This means `run.meta.json` files for runs from this
  session (and from prior sessions using this script) may report
  `items_failed > 0` even when no tiles were actually lost. The
  correct count is always `len(per_item_metadata)` where
  `finish_reason in {"success", "STOP"}`, or equivalently
  `finish_reason_counts["success"]`. Going forward, the fix in
  `6a7c3ed8` will produce accurate counts for new runs, but
  historical run metadata should be interpreted with caution.

## Session 67 — 2026-04-14/15 (map-reader-llm): WBF closure, H10 production run, and the permutation test correction

### Completed

1. **WBF vs greedy-ball comparison** — scored consensus-only F1 across 18 leaderboard conditions on sapphire. Greedy slightly ahead (mean ΔF1 = −0.005). Then ran WBF through PV pipeline for N=5 and N=30: N=5 NS (p=0.392), N=30 significant (p=0.009, greedy wins). Greedy confirmed as the correct consensus method.

2. **H10 Training Pool Size experiment** — full cold-start pipeline:
   - Created 384px null examples, cold-start calibration config (9 examples, legend + nulls only)
   - K=5 calibration detections on 160 tiles with production config (T=0.7, HIGH, image-track), ~$5
   - Filtered detections to 020/040/080 tile subsets (new `filter_detections_to_pool.py`)
   - Hard-case discovery on all 4 pools, built 4:4 HP:HN libraries with 150px crops
   - K=5 evaluation on 327-tile holdout × 4 conditions, ~$66 (should have been ~$33 at flex)
   - Consensus scoring: pool_160 leads (+0.020 F1); WBF tested on all pools (greedy wins)
   - PV verification on pool_020 and pool_160: gap compresses to ΔF1=+0.005, p=0.845 (NS)
   - **Conclusion**: Pool size has no significant effect under PV. 20 tiles suffices.

3. **Permutation test bug found and fixed** — `compare_wbf_greedy_pv_permutation.py` used map-level permutation (4 maps, min p=0.125, structurally underpowered). Rewritten to use existing tile-swap infrastructure from `pairwise_permutation_test.py`. WBF N=30 flipped from NS (p=0.258) to significant (p=0.009).

4. **Infrastructure**:
   - 2,630 GeoJSON files tracked in git (previously gitignored in `h11/pv-diag-384/`, `retest/`, `pv/`, `pv-diag-256/`)
   - SDK upgraded: google-genai 1.67.0 → 1.73.1
   - Flex tier defaulted for all real-time API calls (`--service-tier flex`)
   - `service_tier=None` crash fixed in both `4_detect_mounds_batch.py` and `lib_verifier.py`
   - `/audit-config` skill created (grimoire entry + `~/.claude/skills/audit-config/SKILL.md`)
   - Errata E48-E50 recorded (HN count inconsistency, cold-start deviation, holdout expansion)

### Decisions

- **Greedy-ball confirmed** as consensus method for the paper (WBF N=30 significantly worse, N=5 equivalent)
- **H10 null result** — pool size doesn't matter under PV; 20-tile cold-start suffices
- **4:4 HP:HN ratio** adopted for H10 (preregistration Section 8.4.1 said M=3, but Scale-8 definition and composition table say 4:4; treated as drafting error, E48)
- **API gate is frozen** after approval — no silent parameter substitutions

### Commits

~17 commits across WBF analysis, H10 pipeline, infrastructure fixes, and documentation.

### Cost

- WBF verifier (N=5 + N=30): ~$3 (standard, SDK didn't support flex at the time)
- H10 calibration: ~$5 (standard, same reason)
- H10 evaluation: ~$66 (standard — should have been ~$33 at flex; SDK not upgraded until after)
- H10 verifier: ~$3
- **Total session**: ~$77, of which ~$35 was overspend from the flex-tier incident

### Contextual assumptions

The flex-tier overspend occurred because the google-genai SDK v1.67.0 didn't support `service_tier` as a `GenerateContentConfig` parameter. Rather than stopping to upgrade the SDK (a 30-second operation), runs were relaunched without flex. This was identified as a process failure and new rules were established: API gate approval is a frozen contract, and SDK incompatibilities must be fixed rather than worked around.

---

## Session 69 — 2026-04-15/16 (map-reader-llm): H12 v2 (last production run), library-axis closure, Scale-4 verifier sanity check, scope discovery, archiving, leaderboard planning

### H12 v2 execution (the last production hypothesis run)

1. **Planned and configured** H12 v2 (HP:HN ratio, 3 conditions: R1 2:6, R2 4:4 reused, R3 6:2). Errata E52 appended. `/audit-config` passed all technical checks.
2. **Launched overnight**: 10 detection runs (R1 × 5 + R3 × 5), 3,270 API calls, ~$34, 26 min wall time, 94.5% cache hit rate. Two transient JSON parse failures in R3 (1.3% loss).
3. **Full analysis pipeline**: greedy t=1..5 + WBF variant C → multi-buffer evaluation → tile-level paired permutation → BH-FDR.
4. **Result** (Obs 239): three-way null. F1 band 0.688–0.717 at greedy t=4. All CIs overlap. HP-heavy (R3) directionally worst — contradicts prereg prediction.

### Cross-hypothesis library-design closure

5. **45-pair cross-hypothesis matrix** (all H8 v2 + H12 v2 conditions) run on sapphire. Zero significant after BH-FDR; pooled adj-p ceiling 0.966 (Obs 240).
6. **WBF H12 pairwise**: also null under secondary aggregation.
7. Combined with H8 v2 null (Obs 238) and H10 v2 null (Obs 236): **library-design axis definitively closed**.

### Scale-4 vs Scale-8 post-verifier comparison

8. **Scale-4 advanced** for generalisation run on parsimony grounds.
9. **Greedy verifier** (Scale-4 $2.16 API): 1551 candidates verified, 0 failed. Initial 1D sweep gave artificially low F1 (0.525) because the t=1 union is too noisy for a single-threshold sweep.
10. **2D sweep** (vote_t × prob_t) recovered F1 to 0.737 (Scale-4) / 0.722 (Scale-8).
11. **WBF verifier** (Scale-4 $1.52 + Scale-8 $1.39): same story — WBF matches greedy within 0.0005 F1.
12. **Three-pipeline comparison** (Obs 241): Scale-4 leads by +0.015 in all three pipelines, none significant. Parsimony choice confirmed.

### Evaluation scope discovery

13. User questioned whether H1–H7 were re-run at 384 px. Investigation revealed: retest was at 512 px over 340 tiles (not 384 px), correcting my assumption.
14. **Three production test tile sets** identified and locked in: Era 1 (340 × 512), Era 2 (487 × 384), Era 3 (327 × 384). Fully nested, verified by spatial intersection.
15. Key finding: the 487-tile 384-px set already excludes the 512-px calibration footprint (zero overlap confirmed). The pool_160 exclusion for Era 3 is geographically separate.
16. Coverage quantified: 80.8% / 73.0% / 59.0%. Documented in `results/evaluation-scopes.md`. Decision (Obs 242): era-first leaderboards (primary) + consolidated via spatial re-tiling (secondary).

### Archiving

17. **~2.1 GB archived** across 5 categories: 60-tile validation results, 256-px data, pre-retest outputs, experimental pilots, intermediate calibration. Manifest at `archive/ARCHIVE-MANIFEST.md`.

### Leaderboard planning

18. Architecture grid: 2 × 2 (single-pass / consensus × no-PV / +PV) × 3 tracks.
19. Sweep convention locked: consensus threshold (1-of-K..K-of-K) × verifier probability (0.0–1.0) × spatial buffer (20/30/40/50 m).
20. **Condition inventory built**: 144 conditions (96 Era 1, 34 Era 2, 14 Era 3). 81 need consensus building; 67 already have pre-computed F1 data in aggregate bootstrap-CIs files.
21. Externalised to `planning/leaderboard-construction-plan.md`.

### Decisions and observations

- **Obs 239**: H12 v2 HP:HN ratio null (three-way)
- **Obs 240**: 45-pair cross-hypothesis library-design null (closure)
- **Obs 241**: Scale-4 vs Scale-8 three-pipeline verifier sanity check
- **Obs 242**: Leaderboard construction strategy (era-first + re-tiling)
- **Scale-4 confirmed** as generalisation-run library
- **Greedy** confirmed as primary aggregation (100% tile coverage)
- **v2 verifier quarantined** (data leakage from test pool)
- **Phase transition**: pure analysis mode entered

### Commits

- `4be2d68a` feat(h12-v2): H12 experiment setup + errata E52
- `9009a65b` feat(analysis): 7 new/modified analysis scripts
- `6d804934` data(analysis): H12 + cross-hypothesis + verifier results
- `b7460aae` docs(session-69): Obs 239–242 + leaderboard plan + inventory
- `276e4ca8` refactor(archive): ~2.1 GB non-production data pruned
- `2e84d4a6` data(h12-v2): detection data + verifier outputs

### API spend

~$39 total: H12 v2 detections ($34) + Scale-4/Scale-8 verifier runs ($5.07).

### Contextual assumptions

The 2D sweep (vote_t × prob_t) resolution of the "verifier looks broken" false alarm is important context. The 1D sweep on consensus_t1 (the union of all detections) produces artificially low F1 because the verifier cannot substitute for the proposer's vote-count filter. Any future PV pipeline that takes the consensus_t1 union as input MUST be evaluated with a 2D sweep, not a 1D verifier-probability sweep alone. This lesson is documented in Obs 241 and should prevent future confusion.


## Session 70–71 — 2026-04-17/18 (map-reader-llm): Two 55-map generalisation runs, paired permutation test split decision, publishable launcher infrastructure matured

### Work completed

**Image HIGH generalisation run** (2026-04-17 → 04-18):

- Designed and wrote the publishable launcher `scripts/run_generalisation.py` (~1,600 LOC) with YAML run-configs, launch_manifest, cost_manifest, pre/post-run audit copying, signal-handler subprocess tracking.
- Built YAML config + pre-launch audit for the image run.
- `/audit` on launcher code: found and fixed 5 Critical bugs (token-key mapping, cache-rate denominator, yaml.safe_dump Path crash, top-level service_tier dead key, git-dirty false positives on untracked outputs).
- `/audit-config`: 20/20 preregistration requirements matched. 1 blocker fixed: `include_example_images: true` made explicit in `library_plus-hp.json`.
- Dry-run + single-tile live smoke test ($0.05) on sapphire.
- Launched headless on sapphire 2026-04-17 00:15 UTC. Pass 1 ran at 60 workers; switched to 250 for passes 3-5 (workers can only be changed between passes).
- Operational issues mid-run: orphaned subprocess during worker switch (cleaned up manually); launcher's `failed_passes >= 3` safety gate aborted after all 5 passes succeeded because exit-code-2 is the proposer's normal "log and continue" signal (recovered with `--resume`). Three post-run launcher fixes applied and committed as `b80cfc30`: pass-skip check uses `*.meta.json`, SIGINT/SIGTERM handler propagates to subprocess, `failed_passes` gate removed.
- Final result: **F1 = 0.771 [0.760, 0.782] @ 50 m, cost $364.70** (within $355–385 budget). Runtime 4h 55m. Cache hit 91.0 %, tile failure 0.06 %.

**Post-run analysis on image run**:

- Dawid-Skene correction: F1 0.771 → **0.795** (ΔF1 = +0.024). 
- Per-map heterogeneity analysis: SD @ 50 m widens from 0.021 (4-map calibration) → 0.094 (55-map out-of-sample), ~4.4× wider. K-35-075-3 is a persistent low-outlier (F1 = 0.286 all buffers) — diagnosed as under-annotation (2 refs vs 58-142 adjacent), not pipeline failure. Excluding it tightens SD to 0.069.
- Obs 256 (image headline + D-S) and Obs 257 (heterogeneity + K-35-075-3 diagnostic) written to working-notes.md.
- Pre-launch audit, post-run report, and heterogeneity script `analyse_55maps_heterogeneity.py` all committed.

**Retrospective documentation pass** (2026-04-18 afternoon):

- Reconstructed pre/post-run docs for the 2026-04-10 text HIGH generalisation run using the image HIGH template. Honest labelling of what's measured vs estimated vs unrecoverable: proposer cost estimated (~$62) because the cleanup-retry loop overwrote per-pass meta.json totals; per-map cost attribution unrecoverable; cache hit rate N/A (text preamble below Flash's 1024-tok cache minimum).
- Files: `configs/run-configs/55maps_text_generalisation_retrospective.yaml` + `..._retrospective_post_run_report.md`.

**Text MIN comparison run** (2026-04-18 afternoon):

- Paired design against the 2026-04-10 text HIGH run: same config except `thinking_level: high → minimal` + `workers: 60 → 250` (orchestration-only).
- Full pipeline: YAML config + pre-launch audit → `/audit` (1 Medium: overstated "ONLY difference" claim — fixed) → `/audit-config` (13/13 prereg matches, 0 blockers) → dry-run on sapphire → commit before launch (`6b1d9192`) → launch.
- Runtime: 2h 6m (substantially faster than image — text payloads smaller at 250 workers, Flex less saturated).
- Result: **F1 = 0.759 [0.747, 0.771] @ 50 m, cost $60.79** (below $65–80 budget). Thinking tokens: 0 (confirms MIN forwarding to API). Cache hit 0.0 % (expected — text preamble below cache minimum). Tile failure 0.29 %.

**Paired permutation test text HIGH vs text MIN** (10,000 iter, seed 42):

| Buffer | ΔF1 (HIGH−MIN) | p-value | Verdict |
|:------:|:--------------:|:-------:|:-------:|
| 20 m | +0.0052 | 0.42 | **ns** |
| 30 m | +0.0278 | < 0.0001 | *** |
| 40 m | +0.0294 | < 0.0001 | *** |
| 50 m | +0.0306 | < 0.0001 | *** |

- Split decision: HIGH wins significantly at ≥30 m, indistinguishable at 20 m (the preregistered primary per §4.1.1, E47).
- P/R decomposition: HIGH's advantage is entirely recall-driven (+0.045 R at 50 m, P delta −0.009 trivial). Mechanistic interpretation: thinking helps *enumeration*, not *localisation*.
- Dawid-Skene correction on MIN: F1 0.759 → **0.783** (ΔF1 = +0.024, matching the other two runs exactly — constant correction magnitude across runs).

**GitHub issues filed for deferred code fixes** (5 issues #1-#5):

- #1: `_estimate_cost()` image-biased (manifest expected_cost_usd = $355 on text MIN run when actual was $61)
- #2: Theoretical Popen-assignment microsecond race in signal handler
- #3: Pass-skip check fragile to corrupt `.meta.json`
- #4: Heterogeneity script polish bundle
- #5: Record launcher SHA256 in launch_manifest (closes the stale-git-HEAD provenance caveat observed on sapphire)

**Environment sync**:

- Resolved divergent state on sapphire: 7 tracked-file modifications were mostly identical-to-main (rsync artefacts); one cosmetic diff in `run_generalisation.py`; one misfired-rsync content replacement in `scripts/README.md`. Reset sapphire to origin/main with user approval, then pulled. All three environments (amd-tower, sapphire, zbook) now at commit `ac4ba4e0`, later `6f2bdd9a` after plan commit.

**Plan for text HIGH re-run** (next session):

- Planning doc at `planning/55maps-text-high-rerun-plan.md` committed as `6f2bdd9a`.
- Hand-off prompt written for a new session to execute the re-run with full publishable-launcher documentation.

### Artefacts produced

- 3 pre-launch audits, 3 post-run reports (image HIGH, text HIGH retrospective, text MIN), 1 planning doc, 5 GitHub issues.
- 2 run YAML configs (image HIGH, text MIN), 1 retrospective YAML (text HIGH old run), 1 heterogeneity analysis script, 1 D-S CLI extension (`--consensus`, `--probs`, `--ground-truth`, `--bounds` flags added to `analyse_dawid_skene.py`).
- 4 new/updated memory files under the auto-memory system.

### Observations (working-notes.md)

- **Obs 256**: 55-map image generalisation F1 = 0.771 measured / 0.795 D-S-corrected.
- **Obs 257**: Generalisation widens F1 distribution ~4×; K-35-075-3 under-annotation diagnostic.
- **Obs 258**: HIGH thinking helps enumeration not localisation — paired permutation split decision.

### Commits (chronological, 15+)

Key commits: `b84925d2` (launcher publication), `4c147af6` (image run outputs), `b80cfc30` (launcher fixes), `3acba058` (followup tracking), `57f8bfe4` (heterogeneity analysis), `a10caa8d` (K-35-075-3 diagnostic), `a5f28fe9` (D-S on image), `15eb9383` (Obs 256-257), `badddf92` (text HIGH retrospective docs), `6b1d9192` (text MIN config), `f0f7158e` (text MIN run + analysis), `ac4ba4e0` (paired geojson), `6f2bdd9a` (text HIGH re-run plan).

### API spend

- Image HIGH run: $364.70 (Flex tier, measured via cost_manifest).
- Text MIN run: $60.79 (Flex tier, measured via cost_manifest).
- Incidental: single-tile smoke test ($0.05), D-S analyses on sapphire (local compute only), HIGH text retrospective evaluation on sapphire (local compute only).
- **Session total: ~$425.**

### Contextual assumptions

- Sapphire's git HEAD was stale (`b57cf6c2`, ~33 commits behind `origin/main`) at the time of the text MIN run launch. The actual launcher file that ran was the latest content (rsynced from amd-tower), but `launch_manifest.json` recorded `git.commit_sha: b57cf6c2`. This is a provenance gap filed as GH issue #5. Mitigation: replicators should reference the `resolved_config.yaml` in the output dir, which fully documents what was actually used.
- The `_estimate_cost()` helper is calibrated on the image proposer per-tile rate (~$0.0082/call) and reports 5.8× overestimates on text runs. Visible in `launch_manifest.json` and `experiment_intent.md` during dry-run. Does not affect the actual run cost tracking (cost_manifest.json is measured from per-run meta files). Filed as GH #1.
- The 2026-04-10 text HIGH run's `outputs/55maps-generalisation/verified/verified_detections_paired.geojson` was created this session by retrospectively filtering the original consensus + probabilities at the same (vote_t=4, prob_t=0.15) operating point the text MIN run used. Committed for downstream-tool reproducibility; derivation is deterministic from already-committed artefacts so it could also be regenerated.
- Claim in YAML/audit that "ONLY differences are thinking_level and run_name" was initially false (omitted workers: 60→250); `/audit` caught it, both files amended to document workers as orchestration-only. The scientific claim (paired permutation test measures thinking-level effect cleanly) is unaffected because workers is not a payload parameter.

---

## Session 72 — 2026-04-20 (map-reader-llm): Human-review completion, corrected F1 at 50 m, verifier calibration, subtype-accuracy plan

Single-day session, no compaction, 6 commits pushed (`ee2f0f4a` →
`6fc6df2a`). Work organised in three phases: morning infrastructure,
afternoon human review, evening analysis and planning.

### Morning — infrastructure

- **Planning item #3 resolved** (`55maps-image-generalisation-followups.md`):
  post-run artefacts were already committed at `4c147af6` / `15eb9383`;
  plan doc updated to reflect.
- **Crops recovered**: `outputs/55maps-image-generalisation/crops/crops/`
  was empty on amd-tower because the `outputs/**/crops/crops/` gitignore
  rule meant they never synced via git. 7,877 PNGs (~338 MB) rsynced
  from sapphire. Blocker cleared for the human-review session.
- **NAS migration plan drafted** via prior-art-scout agent (found DVC +
  Cloudflare R2 as the recommended modern approach) and Plan agent.
  Key decisions: NAS-primary with R2 off-site backup (Infrequent Access
  tier, ~$0.72/mo at 70 GB consolidated), DVC deferred to future
  project, MANIFEST-in-git as lightweight reproducibility alternative.
  Stage 0 (read-only verification) ran as background agent; surfaced
  two blockers (sapphire SSH key-auth broken, h11 canonical copy is on
  zbook not sapphire) that must be resolved before Stage 1.
- **Google Drive verified** as source copy of the Soviet 1981 rasters
  (`2023-MapDigitisation-ML/Maps/Russian1981_4326/`) — five-tier
  redundancy established for source material.

### Afternoon — human review of 1,028 VLM-only candidates

The headline work of the session. Shawn reviewed all 1,028 candidates
from the 55-map image generalisation VLM-only set in a single sitting
(~3 hours), classifying by symbol type.

- **Calibrated tolerance-circle UI built mid-review** — after ~100
  candidates Shawn raised the spatial-ambiguity problem explicitly
  ("~15% of cases are genuinely ambiguous — how far off-centre is too
  far?"). I added a 50 m magenta tolerance circle rendered live from
  the source raster with a 300 m context crop upscaled via LANCZOS to
  600 px, plus a `buffer_metres` CSV column for provenance. Shawn
  then restarted the review from scratch for defensibility; the
  original 327 uncalibrated reviews were archived at
  `archive/human-review-sessions/` for the later cross-tab analysis.
- **70 paper-figure screenshots captured during review**, organised
  into a taxonomy covering robustness (smudging, scan artefact, blur,
  colour shift, occlusion, extreme-distortion apex), centroid-bias
  failures (text-label pull, feature-clutter, contour-line, water-
  feature — three attractor categories with negative controls),
  FP confounds (nine sub-categories), subtype-classification errors,
  and reviewer-discipline boundary cases. Indexed with README.md
  capture log.
- **Observations 262–266 added** during the review as the patterns
  emerged — the failure-mode taxonomies for Obs 264/265/266 were
  built up screenshot-by-screenshot, gaining sub-categories as
  successive captures either reinforced or extended the pattern.
- **Final review counts**: 472 mounds (45.9%), 556 not_mound (54.1%),
  0 uncertain, all tagged `buffer_metres=50`. Subtype breakdown:
  burial 338, benchmark_on_mound 92, trig_on_mound 29, settlement 13.

### Evening — analysis, planning, reflection

- **Corrected F1 at 50 m** computed on sapphire: F1 = 0.8295 (up from
  measured 0.7710), P = 0.8808, R = 0.7839. Bootstrap 95% CIs (over
  human-review label resampling): F1 [0.826, 0.833]. Output at
  `results/55maps-image-generalisation/human-reviewed-corrected/`.
  Obs 267 written to capture the headline finding and the 2.5× gap
  vs the Dawid-Skene aggregate estimate (~186 posterior-true mounds
  vs 472 reviewer-confirmed).
- **Three background agents dispatched in parallel** at session end
  while Shawn was AFK:
  1. Uncalibrated-vs-calibrated cross-tab → Obs 268 (21.4% flip rate,
     one-directional mound→not_mound, revised Obs 263's low-p framing).
  2. Verifier probability vs human-label cross-tab → Obs 269 (over-
     confidence, AUC 0.65, low-p-under-confidence hypothesis
     falsified).
  3. Classification-accuracy plan for 4-map gold-standard → plan
     drafted with data-availability step, metric shortlist.
- **`/review-implementation` pass on the classification plan**
  surfaced 9 metric decisions; Shawn accepted all default
  recommendations. Decision record at
  `planning/gold-standard-classification-metrics-decisions.md`; plan
  updated to flip status to READY TO EXECUTE.

### Artefacts produced

- Code: `scripts/review_candidates.py` (enhanced),
  `scripts/compute_corrected_f1_human_reviewed.py`,
  `scripts/crosstab_uncalibrated_vs_calibrated.py`,
  `scripts/crosstab_verifier_vs_human.py`.
- Data: `results/55maps-image-generalisation/human-review.csv` (1,028
  rows), `human-reviewed-corrected/`, `uncalibrated-vs-calibrated-
  crosstab/`, `verifier-calibration-crosstab/` (with reliability
  diagram + ROC + PR curves as PNGs).
- Archives: `archive/human-review-sessions/human-review-55maps-image-
  uncalibrated-2026-04-20.csv` (327 rows, preserved for cross-tab).
- Paper figures: `docs/paper/figures/review-app-examples/` (70 PNGs
  + README).
- Observations 262–269 in working-notes.md; Obs 263 revised.
- Plans: `nas-migration-plan.md` + `gold-standard-classification-
  accuracy-plan.md` + decision records.

### Session outcomes

- Paper headline number: corrected F1 ≥ 0.830 at 50 m.
- Paper methodology figure: 21.4% reviewer flip rate under
  calibrated UI.
- Paper failure-taxonomy figure source: 70 indexed screenshots.
- Paper error-taxonomy: Obs 264 (centroid bias, three attractor
  categories), Obs 265 (visual confounds, nine sub-categories), Obs
  266 (subtype classification boundary failures), Obs 269 (verifier
  miscalibration — the architectural complement to the above).
- Next-action readiness: classification-accuracy analysis plan is
  READY TO EXECUTE, script not yet written.

### Contextual assumptions

- The 1,028 VLM-only candidate set is relative to the student GT at
  50 m buffer. Tighter-buffer corrections are NOT derivable from this
  review — reviewers judged against the 50 m tolerance circle and
  did not pinpoint symbol positions within the circle. Corrected F1
  is 50 m-only.
- The reviewer's conservative-bias asymmetric decision policy
  ("if in doubt, reject") is empirically confirmed by the one-
  directional nature of the 70 flips between uncalibrated and
  calibrated review. This means corrected F1 at 50 m is a *lower
  bound*, not a point estimate. The D-S aggregate F1 (0.795) is
  the complementary upper-ambient estimate; the honest interval is
  [0.795, 0.830+].
- The verifier's heavy quantisation (only 13 distinct probability
  values across 1,028 candidates, 370 at p=1.00) means threshold-
  based filtering has limited headroom. Any paper recommendation
  about "tune the verifier threshold" should acknowledge that the
  signal is coarse.
- Obs 263's low-p-ambiguity prediction was retracted in-session
  based on the cross-tab evidence. The revised framing is "spatial-
  tolerance-driven ambiguity across all confidence levels." Future
  discussion of the ambiguity band should reference the revised
  version, not the original.
- The 70 paper-figure screenshots are named by descriptor + candidate
  ID + date; this naming is stable and can be cited verbatim in the
  paper. If any are re-captured in future sessions, match the
  existing naming convention per `README.md` in the figures dir.

---

## Session 73 — 2026-04-21 (map-reader-llm): Analysis freeze reached via multi-buffer F1 + D-S double-negative + v2 quarantine + documentation audit

Single-day session, no compaction, **ten commits pushed** (`edfc27f5`
→ `0fc26427`). Ten background agents orchestrated across the day,
with up to four in flight simultaneously. Ended the day at clean
analysis freeze with paper write-up continuity handed off.

### Morning — subtype-classification F1 execution

- **`scripts/analyse_subtype_classification.py` executed on sapphire**
  (via background agent per Session 72's "READY TO EXECUTE" plan).
  Output: `results/gold-standard-subtype-classification/` with 15
  files. Weighted-F1 = **0.887** [0.849, 0.922] at 50 m / 4-of-5
  consensus; Level-1 accuracy = 1.000 (mound-family vs settlement on
  matched pairs); Level-2 accuracy = 0.904. Obs 270 captures headline;
  Obs 271 captures benchmark → triangulation 57 % asymmetric confusion
  as a new sub-pattern not in Obs 266's original taxonomy.
- Audit step caught a `settlement_trace` bug (Hungarian matcher
  returns pairs in detection-index order, not GT file-order; fids
  were mis-assigned in the qualitative trace). Fixed; headline metrics
  unaffected (they came from the raw pair-list, not the fid-labelled
  rows).
- Surfaced the "paper detection F1 = 0.904" anchor on the 487-tile
  matrix (K=30 text-HIGH + PV). The 4-map GS extended-buffer report's
  0.826 is a K=5 companion on a different corpus; not the headline.

### Midday — buffer-band lift analysis (Obs 272)

- **GT-clustering + Hungarian pair-drift diagnostics on the 55-map
  set** (`scripts/diagnose_100m_buffer.py`, ran on sapphire): 83.2 %
  of GT are isolated at 100 m; pair-drift at 100 m is 4 of 4,108
  = 0.097 %. Hungarian matching is safe to use at 100 m without a
  greedy-nearest bracket.
- **Multi-buffer re-review app built** (`scripts/review_candidates.py`
  extended): five concentric tolerance rings at 50/75/100/125/150 m
  + sidebar toggle for re-verifying yesterday's mounds + buffer-band
  selector keyed 1-6 + auto-reset. Default queue excludes candidates
  already resolved as mound@50 m.
- **557-candidate re-review** completed by Shawn: 274 mounds found
  across wider bands (2 at 50, 121 at 75, 47 at 100, 19 at 125, 11 at
  150, 74 at >150), 283 confirmed FPs.
- **Buffer-band lift analysis** (`scripts/analyse_buffer_band_lift.py`,
  sapphire): permutation null + Ripley's cross-L with 1,000
  within-tile permutations, seed 42. Shell lift is 102× / 21× / 5.9×
  / 1.9× across (0,50] / (50,75] / (75,100] / (100,125]; p = 0.381
  at (125,150] and p = 0.433 at (150,286] — **pull effect ends at
  ~125 m**. Obs 272 captures.

### Afternoon — analyses consolidation

- **Multi-buffer corrected F1** (`scripts/compute_corrected_f1_
  multi_buffer.py`, sapphire, 10 000 bootstrap iterations, seed 42):
  F1 curve 0.832 → 0.848 → 0.852 → 0.854 → **0.855** across
  50 / 75 / 100 / 125 / 150 m. Plateau reached at 125 m consistent
  with Obs 272's null-crossing. Agent caught a 12-hour → 3-minute
  performance issue in the bootstrap inner loop (Python vs vectorised
  `np.bincount`); library patch deferred as post-freeze work.
- **D-S × human review cross-tab v1**
  (`scripts/analyse_ds_vs_human_review.py`): posterior degenerate at
  0.186; AUC = 0.500; ECE = 0.539. Worse calibration than the
  verifier (Obs 269).
- **D-S data-driven prior re-run** (`scripts/analyse_dawid_skene_v2.
  py`): prior sweep + 80/20 held-out control. Feeding the empirical
  rate (0.7247) produces posterior = 1.000 (degenerate collapse
  above prior ~0.22). The prior that yields cohort-rate-matching is
  0.17 — about half the empirical rate. AUC prior-invariant at 0.500
  regardless. Obs 273 captures: D-S is **structurally inadequate
  on this slice at any prior**.

### Late afternoon — v2 verifier quarantine

Shawn flagged that the v2 verifier prompt was written by analysing
GS FPs (calibration-on-test); v2-on-GS evaluations are therefore
invalid.

- **100 files moved** to `archive/v2-verifier-contamination/` via
  `git mv` (quarantine agent). Primary mover: agent confirmed via
  `run.meta.json` that the paper-headline F1 = 0.904 uses verifier v1
  (instruction hash `2518d529…`, run date 2026-03-25, before v2
  existed). Headline is clean.
- MANIFEST + README + `docs/methodology/v2-verifier-contamination-
  policy.md` + `planning/condition-inventory.json` annotations land.
  Six `pv-*-v2` entries flagged for manual review — the `-v2` suffix
  there may denote a second verification pass rather than the v2
  prompt (agent inspected `run.meta.json` and found v1 instruction
  files; left in place, flagged).
- **Leaderboard rebuild check** (background agent): all paper-table
  aggregates predate the v2 cell creation date (2026-04-14) or are
  era-scoped to non-v2 conditions. No rebuild required.

### Evening — CI metadata + paper-tables + documentation audit

- **CI metadata infrastructure**: registry at `results/ci-metadata-
  registry.md`; 48 sidecar `.metadata.json` files (41 per-file + 7
  directory-level); `evaluate_detections.py` patched to embed
  `_metadata` in future `evaluation.json` outputs (+205/−3 lines,
  15 tier1 tests passing); E54 Clarification errata entry
  documenting the preregistered 1,000-iter primary-F1 bootstrap vs
  the 10,000-iter post-hoc analyses (corrected F1, subtype, review-
  UI crosstabs).
- **Paper-tables consolidation**: `results/paper-tables/gold-
  standard-spatial-tolerance.{md,csv}` (GS extended-buffer curve
  5/10/15/25/35/45 m, plateau at 25 m) and `subtype-classification.
  {md,csv}` (weighted-F1 = 0.887 headline + per-class table + Obs 270
  / 271 pointers + Suggested paper text block).
- **Documentation audit re-run**: two-agent workflow per `planning/
  doc-audit-rerun-plan.md`. Primary produced 4-file draft at
  `results/documentation-audit/draft/`; verifier in fresh context
  checked 85 claims (82 PASS, 2 FAIL, 0 DEAD, 0 silently-wrong
  uncited figures). Both failures one-line fixes (paper-tables file
  count 28 → 26; E47 mis-attribution as Obs 246). Draft promoted to
  top-level `results/documentation-audit/`; old flawed audit (commit
  `8747d726` from 2026-04-19) archived to `archive/flawed-audit-
  2026-04-19/` with NOTE.md.

### Paper write-up continuity prepared

- `planning/paper-writeup-continuity.md` — single-file handoff for
  a fresh session. Contains: current state, interim-docs-first
  strategy (user-confirmed), exemplar nomination (gold-standard-
  subtype-classification report), canonical numbers table with
  source citations, six-step fresh-session plan, five guardrails
  (including the two-E47 disambiguation), and context budget
  estimates.
- Meta-findings consolidation doc flagged as Step 3 of the next
  session: synthesise Obs 262 / 263 / 268 (review-UI calibration) +
  Obs 264 / 265 / 266 (failure taxonomies) + Obs 269 (verifier
  miscalibration) + Obs 271 (benchmark → trig asymmetric) + Obs 272
  (attractor-pull scale) + Obs 273 (D-S inadequacy) into a paper-
  Discussion-shaped spine. ~2 hours work for the next session.
- Deferred fact-check agent for the paper draft: modelled on the
  documentation-audit verifier pattern, to run when the paper is
  near complete. Not a next-session task.

### Observations added

- **Obs 270** — Subtype-classification weighted-F1 = 0.887 on 4-map
  GS (headline).
- **Obs 271** — benchmark → triangulation asymmetric confusion
  (27 / 47, reverse cell empty; new sub-pattern).
- **Obs 272** — attractor-pull effect ends at ~125 m on VLM-only
  candidates (shell lift + Ripley's cross-L).
- **Obs 273** — D-S aggregate is structurally inadequate on the
  VLM-only slice at any prior (2-annotator identifiability
  degeneracy).
- **Errata E54** — Clarification on the 1 000 vs 10 000 bootstrap
  iteration split (preregistered primary vs post-hoc analyses).

### Issues

- Git-staging interaction between agent `git mv` operations and
  my own `git add` commits resulted in the Obs 273 commit pulling
  in 100 quarantine renames (amended message to reflect both). Not
  a bug; a coordination consequence. Noted in session-reflection as
  a "hardest to reconstruct in 6 months" item.
- Two-E47 identifier collision between `docs/methodology/
  preregistration/protocol-errata.md` line 1233 and `docs/notes/
  reflections/working-notes.md` line 6553. Caught by the audit's
  verifier (in the 82/85-PASS pass); flagged explicitly in the
  continuity file's guardrails. A future-session trap.
- Quarantine agent's six `pv-*-v2` flagged entries remain unresolved
  (may be mis-labelled; `run.meta.json` shows v1 instruction files).
  Low priority; worth a look before citing any of the v1/v2 inventory.

### Pending work (for the fresh paper-write-up session)

- **Step 1**: Read `planning/paper-writeup-continuity.md` to re-orient.
- **Step 2**: Interim-doc review pass — score each per-analysis
  `report.md` against the exemplar's 17-section structure; produce
  `planning/interim-docs-review.md`.
- **Step 3**: Write `results/meta-findings-summary.md` at exemplar
  quality, synthesising Obs 262-273.
- **Step 4**: Fill identified gaps (era-scoped hypothesis summaries
  where lacking, 55-map cross-track comparison doc, limitations
  consolidation).
- **Step 5**: Mark superseded planning / pre-launch-audit docs as
  `SUPERSEDED`.
- **Step 6**: Hand to paper outline phase.

### Contextual assumptions

- **Analysis freeze is real but not absolute**: Shawn anticipates
  paper-write-up-driven recalculations may arise ("high probability I
  think"). The freeze is a working stance, not a hard stop. If a
  recalculation is needed, follow the same commit-pattern discipline
  as this session: one focused commit, cited outputs, no batching.
- **No more LLM extraction runs planned**: API spend is frozen. The
  `evaluate_detections.py` patch is prospective; existing
  `evaluation.json` files are preserved as-is with sidecars providing
  the retrospective metadata.
- **v2 verifier is preserved in archive for future out-of-sample
  evaluation**: `outputs/55maps-generalisation/verified-v2/` is
  deliberately kept in place (NOT archived) because the 55-map text-
  HIGH corpus is disjoint from the 4 GS maps that contaminated v2's
  prompt-design. An evaluation of v2 against the 55-map student GT
  is valid future work.
- **The 6 `pv-*-v2` flagged entries**: if a future session needs to
  cite v1 vs v2 performance on a 487-tile pipeline, verify the
  instruction-file hash in each run's `run.meta.json` before citing.
  Hash `2518d529…` is v1; anything else needs investigation.
- **The user's "three-turn corrections" on the 4-map GS F1 (0.64 →
  0.826 → 0.904)**: caught a real mis-attribution (I had been
  conflating corpora). If a future session quotes numbers from
  prior-session context, cross-check against `metrics_master.json`
  for paper-headline anchors (F1 = 0.904 K=30 matrix; F1 = 0.891 K=5
  matrix companion; F1 = 0.826 K=5 extended-buffer on GS; F1 = 0.887
  subtype classification conditional on match).

## Session 74 — 2026-04-23 (map-reader-llm): Step 2 + Step 3 of the paper write-up, CRS bugfix, Obs 274 MCC finding, phase2b archive pass

### Objectives (from Session 73 handoff)

- Step 2: Interim-doc review pass → `planning/interim-docs-review.md`.
- Step 3: Meta-findings consolidation → `results/meta-findings-summary.md`.
- Steps 4–6 queued.

### Accomplishments

**Step 2 — Interim-doc scorecard (`planning/interim-docs-review.md`,
1,281 lines, markdownlint-clean)**. 21 reports reviewed against the
17-section exemplar (`results/gold-standard-subtype-classification/report.md`).
Final tier breakdown: 0 ✓ / 13 ~ partial / 2 ✗ stub / 4 ✗ missing;
9 directory groups in §10 "known out-of-scope". Discovered during
re-inventory passes that the original scope (continuity doc's "Have"
list) was a strict subset — added 6 rows post-inventory (uncalibrated-
vs-calibrated-crosstab, phase3a-image-matrix, secondary-effects,
factor-analysis, retest-production-summary, evaluation-scopes) and
one row for Phase 2b retest at `outputs/retest/phase2b/` (no
dedicated analysis_summary.md; narrative embedded in
`retest-production-summary.md` §Phase 2b).

**Step 3 — Meta-findings synthesis (`results/meta-findings-summary.md`,
1,158 lines, markdownlint-clean)**. Obs 262–273 synthesised into five
themes (T1 human-review calibration / T2 failure taxonomies / T3
verifier miscalibration / T4 subtype asymmetry / T5 attractor-pull +
D-S inadequacy), each with a "Suggested paper text" block and full
Trace. All 9 headline canonical numbers spot-checked present. No
archive citations; E47 disambiguated; UK/AU English throughout.

**CRS bugfix (`scripts/analyse_consensus_sweep.py`)**. Discovered
during the Phase 2b tile-level MCC compute on sapphire: commit
8c8e101f (2026-04-11) switched `apply_threshold` consensus emission
to EPSG:4326, but `consensus_to_gdf` continued to stamp 32635
without reprojection. Patched to construct the GeoDataFrame in 4326
then `to_crs(TARGET_CRS)`. Contamination scope verified narrow:
Phase 2b MCC was the only post-2026-04-11 consumer of the buggy path;
all other tile-level MCC artefacts either pre-date the bug or use a
different code path (`evaluate_detections.py::load_geojson`, which
relies on GeoPandas' default 4326 auto-assignment for CRS-less
GeoJSON). Three contamination investigation agents confirmed scope.

**Phase 2b tile-level MCC (`results/paper-eval/mcc/phase2b/`)**.
10 conditions × 3 runs × 340 tiles computed on sapphire with the
patched pipeline. Batch summary + 10 per-condition `mcc.json` +
`compute.log`.

**New observation**: Obs 274 in `working-notes.md` — Phase 2b
tile-level MCC increases monotonically with temperature (opposite
to Obs 116 F1 finding). Mechanism verified: flat sensitivity +
climbing specificity; empty-tile correct-rejection climbs
16.9 % → 47.8 % across T=0.0 → T=1.3 (image track).

**UNINTENDED-T1.0 disposition settled**. Updated README banners in
both `outputs/h11/{consensus,single-pass}-384-UNINTENDED-T1.0/`
directories to state the dual role: origin = E43 deviation;
retention = serendipitous Era 2 / 487-tile-scope T=1.0 coverage for
the 157 downstream references. Directory names keep the
`-UNINTENDED-` label as a permanent origin signal.

**Option A pre-retest phase2b archive pass**. Six orphan 60-tile K=10
pilot docs archived from `results/` to
`archive/outputs-pre-retest-60-tile/phase2b/`.
`phase2b-carry-forward-parameters.md` retained with a retention
banner because `phase2c-carry-forward-parameters.md:126` depends on
it. **Option B residual** (create retest-era carry-forward doc;
repoint phase2c citation; archive pre-retest carry-forward) tracked
in four places to survive Step 4 handoff: banner in the file,
scorecard §3.15 bullet, scorecard §3.15 level-up notes sub-task,
scorecard §6 sequencing item 3.

**Machine sync**. amd-tower pushed 10 commits (`eb2cf23c` through
`0fccf455`); zbook was 28 commits behind origin and is now fully
synced. Both at HEAD = `0fccf455`, clean working trees, main-only,
no stray branches.

### Decisions / corrections

- **Step 3 scope confirmed unchanged** (synthesise Obs 262–273 only).
  Era 1 Phase 2a–3d + retest coverage deferred to Step 4. §10 "known
  out-of-scope" section transparent about scorecard coverage limits.
- **Step 4 sequencing**: Shawn prefers comprehensive pass (all 10
  items) over minimum-viable (4 items). Scorecard §6 order accepted.
- **UNINTENDED-T1.0**: archive-with-note via README strengthening,
  not filesystem move. 157 downstream references preserved.
- **Option A / B split for phase2b orphans**: A done now (safe);
  B deferred to Step 4 when Phase 2b consolidation happens anyway.
- **Sub-agent verdict reversals**: Phase 2b tile count (agent said
  15, actually 340); Phase 3a contamination (agent said yes, actually
  clean); subtype-MCC contamination (agent flagged, actually uses
  `ensure_utm_crs` helper which is immune). All three caught by
  direct filesystem verification triggered by user challenge or my
  own numerical-plausibility check.

### Observations added (working-notes.md)

- **Obs 274** — Phase 2b tile-level MCC sweep is monotonically
  increasing in temperature (image 0.089 → 0.368, text 0.064 →
  0.221), opposite to Obs 116 F1 ordering. Mechanism: flat
  sensitivity + climbing specificity; empty-tile correct-rejection
  rises from 16.9 % to 47.8 % at T=1.3 image. Reconciles (does not
  contradict) Obs 116 / 177 / 209. Cross-referenced to the CRS
  bugfix provenance (patched before compute).

### Issues

- **Sub-agent verdict reliability**: three of seven background
  Explore agents returned wrong or mis-calibrated verdicts this
  session (see Session 74 llm-observations and abductive-reasoning
  entries for the pattern analysis). Verification cost was
  manageable because the filesystem was accessible; in environments
  where verification would require another agent, the calculus would
  invert.
- **Scorecard initial scope was narrow**: relied on continuity doc's
  "Have" list rather than direct `results/` inventory. Re-inventory
  passes caught the gap before Step 3 but after Step 2's first
  "complete" marker. A Step 2 that started from a direct
  directory-walk would have been more robust.
- **Phase 3a "0 thinking tokens" anomaly** (scorecard row 14 note)
  remains unresolved — likely a logging/parsing artefact in
  `secondary_effects.md` §13 HIGH-T0.7. Low priority, pre-publication
  cleanup.
- **Factor-analysis data-completeness bug** (scorecard row 19): blank
  F1 cells on lines 42–43 of `factor-analysis/factor_analysis_results.md`
  flagged during the re-inventory. Paper-critical; Step 4 level-up
  dependency.

### Pending work (for Step 4)

Per `planning/interim-docs-review.md` §6 Step 4 sequencing
(~11–15 hours comprehensive):

1. Synthesise `results/h8-v2/analysis_summary.md` (L, ~90 min).
2. Synthesise `results/h10/analysis_summary.md` (L, ~90 min).
3. Synthesise `results/retest/phase2b/analysis_summary.md` (L,
   ~90 min) **with Option B residual MANDATORY sub-task**: create
   retest-era carry-forward doc, repoint phase2c citation, archive
   pre-retest carry-forward.
4. Consolidate `results/h11/analysis_summary.md` (M, 60–75 min).
5. Write `results/55maps-image-generalisation/buffer-100m-diagnostics/report.md`
   (M, 45–60 min).
6. Write `results/paper-eval/mcc/report.md` (M, 45–60 min).
7. Level-up `results/factor-analysis/factor_analysis_results.md`
   (M, ~45–60 min; fix blank Temperature rows 42–43).
8. Level-up `uncalibrated-vs-calibrated-crosstab/crosstab.md`
   (S, 25–35 min).
9. Level-up `results/evaluation-scopes.md` (S, 20–30 min).
10. Batch-level-up the eight partial per-analysis reports
    (~3.5–4.5 hours at S/M each).

### Contextual assumptions

- **Scorecard is Step 2's canonical output**; it supersedes any
  earlier "coverage inventory" implied by the continuity doc. Step 4
  sequencing should be read from `planning/interim-docs-review.md`
  §6, not from the continuity doc's "Need" list.
- **Meta-findings synthesis scope is Obs 262–273 only** (Discussion
  spine). Results-section material (Era 1 hypothesis closures,
  55-map cross-track comparison, Limitations consolidation) is
  Step 4 or Step 6 work, not Step 3 extension material.
- **CRS patch is prophylactic going forward**; no active artefacts
  required re-computation. `consensus_to_gdf` is now safe for
  post-2026-04-11 consensus inputs. A further hardening (use
  `lib_consensus.ensure_utm_crs` helper for coordinate-magnitude
  detection) is deferred to Step 4.
- **Sub-agent outputs should be treated as drafts**: the pattern
  this session (3 of 7 wrong verdicts) suggests any load-bearing
  claim from a background agent warrants a direct-evidence check
  before it informs a decision. See Session 74 llm-observations for
  the full framing.
- **Shawn's "are you sure X" question pattern** consistently
  retrieves project-wide shape-of-data memory faster than my
  in-session file reads. When this pattern appears, default to a
  fresh filesystem check rather than defending the current claim.

---

## Session 75 — 2026-04-24 (map-reader-llm): Step 4 items 1–7 + close-out hardening + continuity handoff

**Commits**: 16 on `main`, `f6d1cdb4` → `55c5c82c`, all pushed to
`origin/main`. Working tree clean at session close.

### Step 4 deliverables (items 1–7 per scorecard §6)

| Item | Target | Effort | Commit(s) |
|------|--------|--------|-----------|
| 1 | `results/h8-v2/analysis_summary.md` | L | `f6d1cdb4` + `ce075d5a` |
| 2 | `results/h10/analysis_summary.md` + retracted-probe archive | L | `52404476` + `4b20b427` |
| 3 | `results/retest/phase2b/analysis_summary.md` + Option B | L | `e8c46809` |
| 4 | `results/h11/analysis_summary.md` | M | `bb156aab` |
| 5 | `buffer-100m-diagnostics/report.md` | M | `334c6cb4` |
| 6 | `results/paper-eval/mcc/report.md` | M | `9df2f169` |
| 7 | `factor-analysis/factor_analysis_results.md` level-up | M | `a5c4c325` + `043fca18` + `6cf99660` + `9f9f98c3` |

### Close-out hardening

- `71033ff6` — Step 6 polish-pass backlog entry logged (later resolved).
- `9f9f98c3` — `collect-factor-analysis.py` (8 /audit items + autogen-MD path split).
- `23ddfdf6` — `evaluate_pv_results.py` (raise on missing consensus.json).
- `9f7bfe0f` — `consolidate_pv_bootstrap_cis.py` (debug→warning + metadata provenance).
- `f623652d` — `consolidate_paper_metrics.py` (schema validation + provenance).
- `783f37c2` — Doc hygiene (h11 model line + 50m TP reconciliation notes).
- `8949dc00` — Continuity: S6.1 RESOLVED + metrics_master drift logged.
- `55c5c82c` — Continuity: Session 75 handoff block for Session 76 entry.

### Parallel-agent close-out sweeps

| Pass | Scope | Findings |
|------|-------|----------|
| Agent A | results/factor-analysis, phase3a-*, paper-eval, pairwise/ | Only the already-known factor-analysis bug |
| Agent B | results/h{8,10,11,12}, retest/ | 3 narrative consistency issues (all fixed in `6cf99660`) |
| Agent C | results/55maps-*, gold-standard-*, paper-tables/ | Zero Priority-1 findings |
| Agent D | scripts/ aggregator scripts | 1 confirmed bug (pre-fixed) + 3 risk patterns (all hardened) |
| /audit | scripts/collect-factor-analysis.py | 4 medium + 4 low items (all in `9f9f98c3`) |

### Key decisions

- **Option A over Option B** for the factor-analysis blanks (source
  correction instead of README-only documentation). Option A
  uncovered a schema-mismatch + mislabelling bug that
  document-only would have missed.
- **Split auto-MD path** for `collect-factor-analysis.py` after the
  dry-run overwrote the hand-authored narrative. Auto target is now
  `factor_analysis_results_autogen.md`; the hand-authored
  `factor_analysis_results.md` is protected.
- **No output regeneration in close-out**. Plan's non-goal explicitly
  deferred deliberate regeneration of `metrics_master.csv/json` and
  `bootstrap-cis-384px.json` to paper finalisation. Script patches
  committed with outputs reverted to HEAD.
- **Agent B's h10 sign-convention flag was wrong**; headline table
  at line 36 was correct. Main-thread verification fixed the actual
  bug at narrative line 97 instead.

### Issues encountered

- **Dry-run of `collect-factor-analysis.py` overwrote hand-authored
  narrative** at `factor_analysis_results.md`. Recovered via git
  checkout; mitigated by splitting the auto-write path.
- **`metrics_master.csv` has 4 stale rows vs `metrics_master.json`**
  (pro-high-text pool_size=10). Pre-existing; logged for Step 6.
- **Obs 235 retracted-probe data still in the active working tree
  seven months after retraction prose**. Fixed in `52404476` with
  physical move to `archive/h10-h12-v1-retracted-probe/`. Obs 275
  added to working-notes.

### Results summary

- Step 4 progress: 7 of 14 items DONE; 7 remaining (items 8–14).
- Paper-citation layer complete for h8-v2, h10, Phase 2b retest,
  h11, buffer-100m, paper-eval/mcc, factor-analysis.
- Archive state: `archive/h10-h12-v1-retracted-probe/` added (7,988
  files); ARCHIVE-MANIFEST updated.
- Script state: 4 aggregator scripts emit provenance metadata and
  fail loudly on schema mismatch.
- Documentation state: scorecard §3.11 superseded; Step 6 backlog
  updated; continuity doc has Session-75 handoff block for
  Session 76.

### Next session entry

**Step 4 item 8** per scorecard §6: level-up
`results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.md`
(S effort, 25–35 min). Theme T1 anchor (Obs 268 flip-rate).

### Contextual assumptions

- The user's Session 73 approval of the comprehensive Step 4 pass
  (not minimum-viable) held through Session 75, including scope
  expansions during items 2 (retracted-probe archive) and 7
  (Option A recovery).
- Verifier agent + main-thread propose pattern was established in
  Session 74 and re-validated throughout Session 75. Not optional
  for future Step 4 items.
- `planning/paper-writeup-continuity.md` is the single entry point
  for Session 76. The "⚡ Start here" block and §"Session 75 status"
  together carry the load-bearing context.

## 2026-04-24 — Session 77 (map-reader-llm)

Autonomous-then-collaborative session covering: Batch A sapphire
compute (Session 77 data-gen follow-ups), Batch B1 mark-superseded
archive reorganisation (17 files + 6 new themed subdirs), Batch B2
reflections (Session 76 entries), Batch C meta-findings refresh,
corpus-disjointness documentation (5 docs), audit fallout from a
chat confabulation (3 verifier agents + blast-radius audit),
four-cell correction pass after MCC backfill surfaced wrong
detection-source paths, 250-feature scope-filter forensic
investigation, Streamlit wrapper for text-HIGH review, and Session
78 handover. 33 commits pushed to `origin/main`
(`8f213c67..a0f629e9`).

### What was produced

- Batch A (data-gen, 3 commits `dfbf88a5..eaf6c8ba`): 8 paired
  permutation tests (image vs text-HIGH + image vs text-MIN at
  20/30/40/50 m), extended-buffer evaluations for text-HIGH and
  text-MIN at 75/100/125 m, and the cross-track-comparison doc
  updated to incorporate both.
- Batch B1 (archive reorg, 2 commits `34074873` + `b33a818a`): 17
  superseded planning / pre-launch-audit files moved to 6 new
  themed `archive/` subdirs (completed-analysis-plans,
  session-continuity, post-run-followups, infrastructure-planning,
  issue-tracking, superseded-audits), each with a README. All 17
  files got SUPERSEDED banners identifying the replacement doc.
- Batch B2 (reflections, `80025eaf`): Session 76 entries appended
  to session-reflection.md and llm-observations.md.
- Batch C (meta-findings refresh, `ad93c806`): T1 §3.4 (cross-
  modality paired significance + student-GT position noise +
  corrected-F1 track availability), T3 §5.4 (cross-track verifier
  scope), T5 §7.4 (D-S prior-invariance confirmation), and 6 new
  canonical-numbers rows.
- Corpus disjointness documentation (`267134b2`): new §11 in
  evaluation-scopes.md documenting the 55-map generalisation scope
  as disjoint from the 4-map gold-standard Era 1/2/3 scopes; 4
  cross-reference notes in downstream docs.
- Audit-fallout artefacts: three fact-check verifier agents
  disproved my modality attribution claim; a blast-radius audit
  confirmed zero propagation into committed docs. No code changes
  needed.
- Option A MCC backfill (`743e59a8`): 16 cells across
  h8-v2 / h10 / h12-v2 / phase3a-text-matrix / phase3a-image-
  matrix; parallel 8-way on sapphire; 14 clean, 3 flagged as
  suspect with anomaly notes in the commit message.
- Correction pass (in the same `743e59a8` commit): Cells 2/3/4
  corrected with verified detection sources producing the expected
  F1 values (0.750 image, 0.814 text — matches documented cells).
  Cell 1 handover-queued (see Q1 in continuity doc §"Session 78
  entry-point queue").
- Streamlit wrapper (`06cb6247`): `scripts/launch_55maps_text_high_review.sh`
  with `--prev-review ""` to disable the image-track pre-population
  default for a fresh text-HIGH multi-buffer review.
- Session 78 handover (`a0f629e9`): Q1–Q4 entry-point queue with
  exact commands; carry-over context for three memory saves, the
  audit-fallout lesson, the disjointness finding, and the script-
  hygiene + investigation follow-ups.

### Observations + decisions recorded

- Verifier-agent pattern scoped up from committed-artefacts-only
  to also catching chat-turn errors (my modality misattribution).
  Worth retaining in Session 78+.
- 250-feature gold-standard-extended-buffer-sweep
  verified_detections is bounds-filtered intentionally (to Era 3
  / 327 tiles) to match the canonical leaderboard cell. Not a
  bug; a scope choice superseded by the user's later "prefer
  487-tile Era 2" preference. Session 78 Q1 produces the Era 2
  companion artefact; existing Era 3 artefact preserved.
- Three new memories saved (precondition habits): MCC-with-F1,
  384px-Era-2 scope preference, feature-count cross-check before
  evaluator re-runs.
- Text-HIGH human review is a user-facing task (~10–12
  reviewer-hours); downstream compute support queued for when
  the review CSV lands (Session 78 Q3).

### Contextual assumptions

- Sapphire remained reachable throughout the session; all compute
  used the transient-branch pattern (`s77-sapphire-compute`,
  pushed to origin for sapphire to pull, deleted after rsync).
  Origin/main was only pushed at the very end once the user
  explicitly requested it.
- Context budget reached ~80 % by end-of-session but stayed under
  the user's 85 % ceiling. The user's mid-session directive "you're
  only at 60 %, please continue" (earlier in Session 77 chat)
  calibrated my context estimates — I had been over-reporting usage
  by ~20 pp; the corrected self-estimate was informed by explicit
  user calibration.
- The text-HIGH review will be performed by the user, not by me.
  The image-track review (Session 73 era) was performed by the
  user; the text-HIGH review replicates that workflow on a new
  track. Shawn's willingness to review both tracks (rather than
  just "which was supposed to be reviewed") is the positive-
  externality outcome of the chat confabulation.

## Session 78 — 2026-04-24/25 (map-reader-llm): verifier calibration matrix (7 prompts × 2 pools), CRS-bug recurrence + fix, Obs 277 paper-ready finding, Session 79 handoff

**Commits**: 17 on `main`, `6b57364c` → `484538a6`, all pushed to
`origin/main`. Working tree clean at session close.

### Work arc

Continuous overnight-plus-morning session. Started as "fill Step 6 backlog items" but pivoted to a verifier calibration matrix when the user asked whether non-adversarial verifiers might rescue the image-track miscalibration documented in Obs 269. The matrix became the session: ~$36 API spend (flex tier), ~6 hours of compute, 17 commits, and one paper-ready observation (Obs 277).

### Phase-by-phase

| Phase | Artefact | Duration | Commit(s) |
|------|----------|---------|-----------|
| Preparation | `verify_comparative.json` config; lat/lon → UTM reprojection; session-78-matrix shared-crops (2,017 image, 3,736 text) | 15 min | `ca42f557`, `b89dd2f3` |
| Overnight pipeline script | `scripts/session-78-matrix-overnight.sh` | 5 min drafting | `9ebe7346` |
| Phase A (matrix API) | 12 verifier runs × flex tier; 6 novel variants × 2 pools | ~1 hr wall-clock | (artefacts only) |
| Phase B (sweep cells) | 12 × `score_leaderboard_cells.py` | ~10 min | (cell JSONs) |
| Phase C original | 12 × `evaluate_detections.py` at 10k bootstrap + MCC | failed with F1=0 | (caught at inspection) |
| CRS bug diagnosis + fix | `materialise_pv_geojson.py` auto-detect + reproject | 15 min | `6b57364c` |
| Tile recovery | 738 of 740 transient-503 gaps closed via `run_pv.py cleanup` | 17 min | (via agent a24ab205daa5b0cd5) |
| Phase C re-run (`/tmp/phasec_final_v2.py`) | 12 re-materialisations + re-evaluations | ~25 min | (artefacts only) |
| Canonical baseline add | Canonical `verify_adversarial-text` scored + evaluated on both pools for comparison | ~5 min | (within 6d1cad27) |
| Matrix data commit | Cell JSONs + evaluation.jsons + materialised geojsons + shell script | — | `6d1cad27` |
| Calibration crosstab | AUC/Brier/ECE for 14 cells + summary markdown | ~10 min | `88d6b55b` |
| Obs 277 draft + adversarial verification | Working-notes observation draft with 14-cell table + verifier agent round-trip | ~30 min | `303d4f21` |
| Step 6 backlog expansion | 5 new to-do items added | — | `cf192345` |
| Session 79 entry-point queue | Handoff message at top of continuity doc | — | `484538a6` |

### Other commits in the session's 17-commit block (Session 77 carryover into Session 78 early, pre-matrix)

| Commit | Type | Purpose |
|--------|------|---------|
| `e1ef2190`, `b514ecb6` | fix/refactor | First CRS fix (emit EPSG:32635 header; later found insufficient — see Phase C) |
| `aa36b638` | data | GS text-HIGH Era 2 companion + 487-tile leaderboard cell |
| `7ab7d7fa` | docs | Scope-pair narrative edits + leaderboard unification |
| `7b8e5ed7` | docs | Retract 0.722/0.736 forensic-audit prediction; log Obs 276 script-hygiene |
| `4cc95e80` | data | 55-map text-HIGH corrected-F1 + verifier calibration crosstab |
| `1b7143c5` | docs | Session 78 Q3 cross-track comparison edits |
| `27c56057` | docs | Fold tile-level MCC into 55-map cross-track report |
| `651b8ab4` | data | Image-track PV anchor on Era 2 (4 image conditions scored) |
| `46f7a652`, `e917ff91`, `8e8d85d5` | docs | Three Step 6 backlog additions (unevaluated geojsons, per-arch leaderboards, pairwise permutations) |

### Headline result

Obs 277 (working-notes.md:13215): canonical `verify_adversarial-text` is Pareto-dominant on both candidate pools across 7 prompt variants. Best ECE on both pools (image 0.188, text 0.067); best AUC on image (0.863). No novel prompt variant materially improves image-track calibration — all stay in the miscalibrated regime (ECE 0.19–0.27). Text track is well-calibrated across all variants. Falsifies the prompt-specificity hypothesis for Obs 269's image-track miscalibration; confirms the input-distribution hypothesis. **Re-derived 2026-04-25**: prior values were image (AUC=0.863, ECE=0.188) and text (AUC=0.959, ECE=0.067); re-run on crop-parity shared-crops gives image (AUC=0.857, ECE=0.179) and text (AUC=0.956, ECE=0.071) — within original bootstrap CIs. See `docs/methodology/data-reproduction-2026-04-25.md`.

Secondary observation awaiting pairwise-permutation significance testing (Step 6 backlog item 4): on text, four with-images variants (comparative, adversarial, checklist, brief) achieve higher F1 at optimum than canonical by 0.014–0.021 F1, but calibration worsens in exchange. Statistical significance of the F1 deltas not yet established.

### Matrix artefacts

- Cell JSONs: `results/leaderboard/cells/session-78-<pool>-<variant>-487tile.json` (14 files)
- Deep evaluations: `results/verifier-calibration-matrix/<pool>-<variant>/evaluation.json` (F1/P/R/MCC + 10k-bootstrap CIs, 14 files)
- Calibration crosstabs: `results/verifier-calibration-matrix/<pool>-<variant>/calibration.json` (AUC/Brier/ECE, 14 files)
- Materialised PV geojsons: `results/verifier-calibration-matrix/<pool>-<variant>-opt-20m.geojson` (14 files; UTM coords after the CRS fix)
- Two summary docs: `planning/session-78-verifier-calibration-matrix-summary.md` + `planning/session-78-matrix-calibration-summary.md`

### Step 6 backlog net additions this session

6 new items logged (net), bringing the backlog to 9:

1. Unevaluated-consensus-geojsons audit (`46f7a652`)
2. Build per-architecture leaderboards (`e917ff91`)
3. Run pairwise permutation tests across the verifier matrix (`8e8d85d5`)
4. Re-run canonical on session-78 shared-crops for crop-parity (`cf192345`)
5. Investigate `cand_01563` parser bug (`cf192345`)
6. Scope-version the `results/verifier-calibration-matrix/` directory (`cf192345`)
7. Clean up exact-duplicate files in `archive/pre-session-78-pull-2026-04-24/` on sapphire (`cf192345`)
8. Configure GitHub identity on sapphire (`cf192345`)

### Key decisions

- **Flex tier for the matrix API spend** (~$36, default in run_pv.py `--service-tier flex`). 50 % cost discount; trade-off is ~14 % transient 503 rate at overnight launch. `run_pv.py cleanup` recovered 738 of 740 gaps in a follow-up pass.
- **7 prompts × 2 pools** rather than image-only (which would have been cheaper but wouldn't falsify prompt-specificity with the same strength). Defensible under the falsification framing, not under the informational framing.
- **Re-materialise with fixed `materialise_pv_geojson.py`** rather than just rewriting the CRS header in-place on the 12 overnight-produced geojsons. Ensures any tile-recovered candidates are picked up, and the resulting UTM coords match project convention.
- **Adversarially verify Obs 277 before commit** after the user flagged context-contamination concerns. The verification agent caught one correction (the "2 of 5,753 unverified" claim was imprecise — actual is 100% union coverage with per-cell gaps); applied and committed.

### Contextual assumptions

- The canonical `verify_adversarial-text` probabilities used for comparison come from `outputs/h11/pv-diag-384/flash-high-<pool>-n5/<pool>-t0.7/verified-v1-n5/probabilities.json` — produced in prior sessions on a different crop set than the session-78-matrix shared-crops. Crop-for-crop parity is therefore not strictly established; logged as Step 6 backlog item 5 for a follow-up re-run.
- Two candidates (cand_00744 in image-brief-text, cand_01563 in image-checklist) are persistently un-verifiable: one persistent 503, one deterministic parser bug in `run_pv.py` response handling. Union coverage across the 7 variants is 100% — every candidate was verified by at least one prompt — so cross-variant comparability is intact.
- Sapphire has no git identity configured, so Phase E commits from the overnight script failed; all artefacts rsync'd back to amd-tower before commit. Backlog item 9 logged.

## Session 79 — 2026-04-25/27 (map-reader-llm): data-loss recovery, full per-arch + combined leaderboard rebuild, T=0.3 generalisation re-run

**Commits**: ~26 on `main`, `dcd36515` → `d6c0f08a`, all pushed to `origin/main`. Working tree clean at session close.

**API spend**: ~$131.60 total. Matrix Phase A re-run $63.77 (flex Flash) + T=0.3 55-map generalisation $67.79 + T=0.3 recovery $0.034. All within pre-approved gates.

### Work arc

Continuous from Session 78 close through end-of-day Session 79 wind-down. Started as "fill gaps in intermediate report.md docs" per focus slot; immediately pivoted to investigating an Explore-agent-confabulated data deletion that had cost ~$80 of API data, which cascaded into a full reproduction + analytical-infrastructure-build session.

Phases (numbered for cross-reference; each landed before the next started):

1. **Data-loss investigation and reproduction** ($63.77 API, ~80 min on sapphire). Re-ran Session 78 verifier-calibration matrix Phase A: 14 probabilities files at crop-parity. Downstream Phase B/C/D refreshed; Obs 277 numbers updated within-CI; tier-flip caveat added.
2. **Sapphire ↔ GitHub SSH key configured** mid-session in response to data loss. Sapphire can now `git push` directly (closes a previously-painful sync gap; backlog item from Session 78 closed).
3. **Per-architecture leaderboard tree** (~$0 API, ~1.8 hr CPU on sapphire). 12 strata (3 Era × 4 Architecture), F1 + MCC parallel tier tables × 5 buffers × q=0.05 + q=0.01. Era 2 single-pass+PV F1=0 evaluator bug fixed; 2 missing-extension files renamed; condition inventory extended to 204 conditions with S78 cells.
4. **Per-buffer F1 re-tiering** (~$0 API, ~50 min CPU on sapphire). Patched tier-builder with `--threshold-buffer` and per-buffer F1 cache key. 56 reruns; uncovered era1/single-pass tier-1 collapse (21→1 between 30 m and 40 m matching tolerance) and era3/consensus non-monotonic oscillation.
5. **Cross-architecture combined leaderboards** (~$0 API, ~77 min CPU on sapphire). Pooled all conditions across 4 architectures within each Era; greedy-clique BH-FDR tiering. Headline finding: **Era 2 Tier 1 = 100% PV** (8/8 F1, 20/20 MCC).
6. **Per-arch MD overwrite bug fix** (~$0 API, ~25 min). Tier-builder script overwrote non-primary-buffer MD files with later passes. Regenerated 140 MD files retroactively (commit `27d1793f`); patched script to prevent recurrence (commit `bea135af`).
7. **55-map T=0.3 generalisation re-run** ($67.79 API, ~7.8 hr wall-clock on sapphire). Pre-launch audit READY-TO-LAUNCH; user explicitly re-confirmed API spend after launch_manifest cost-estimator output a 5× overstatement ($355 vs empirical $70).
8. **Post-run recovery + MCC patch** ($0.034 API, ~50 min). Recovery agent recovered 18/18 proposer + 1 truly-missing verifier candidate to zero residual; MCC agent added MCC=0.654 tile-level. Recovery investigation surfaced two upstream script bugs (workarounds applied; underlying fixes logged for next session).
9. **Extended-buffer evaluation + Session 80 handoff**. T=0.3 F1 at 50/75/100/125/150 m; F1@125m=0.8072 raw (T=0.7 at same buffer = 0.7949; Δ +0.012). Session 80 entry-point queue at top of `paper-writeup-continuity.md` with 10-item carry-over backlog.

### Major artefacts produced

- `results/leaderboard/per-architecture/` — 12-stratum tier tree (3 Era × 4 Architecture); F1+MCC parallel tables × 5 buffers × 2 q-levels; tier-stability with Spearman rho; MC-precision flags (6,652 flagged tests)
- `results/leaderboard/combined/` — cross-architecture combined tier tables per Era × buffer × metric × q-level
- `results/leaderboard/per-architecture/headlines{,_50m,_100m}.md` — top-3 per stratum at 20 m primary + parallel buffers
- `outputs/55maps-text-high-t0.3-generalisation/` — full T=0.3 generalisation run; cost_manifest.json, launch_manifest.json (provenance), evaluation/ + extended-buffer-eval/, verified/, proposer/, consensus/, crops/
- `docs/notes/reflections/working-notes.md` Obs 277 (refreshed crop-parity numbers + tier-flip + underestimate caveats), 278 (PV scope), 279 (per-buffer tier stability), 280 (F1/MCC tier-leader divergence), 281 (temperature failure-rate hypothesis NOT supported)
- `planning/paper-writeup-continuity.md` — Session 80 entry-point queue with 10-item carry-over backlog
- New scripts (committed): `summarise_per_arch_headlines_at_buffer.py`, `regenerate_per_arch_md_from_json.py`, `materialise_session78_geojsons.py`, `enrich_per_arch_markdown.py`, `verify_per_arch_leaderboard.py`, `build_cross_arch_comparison.py`, `summarise_combined_headlines.py`, `merge_recovery_meta.py`, `55maps-t0.3-extract-new-candidates.py`, `55maps-t0.3-rebuild-verified-geojson.py`, `55maps-t0.3-recovery.sh`
- New feedback memories (in project-memory): `feedback_no_credentials_in_chat`, `feedback_verify_git_tracked_before_delete`, `feedback_commit_api_outputs`

### Headline numerical findings

- T=0.3 raw F1 @ 50 m = **0.8024** [0.791, 0.813] (T=0.7 reference: 0.7883 — Δ +0.014)
- T=0.3 raw F1 @ 125 m = **0.8072** (T=0.7: 0.7949 — Δ +0.012; flat plateau past 50 m)
- T=0.3 tile-level MCC = **0.654** [0.639, 0.670]
- Estimated T=0.3 corrected F1 @ 50 m = **~0.840** (using text-HIGH correction delta +0.038; pre-launch audit estimate was 0.847 ± 0.018)
- Era 2 PV combined Tier 1: 8/8 PV cells (100% PV); F1 leader `pv-flash-high-text-16of30` at 0.890 @ 20 m
- Era 1 consensus combined Tier 1: 4/4 consensus cells (no PV cells in inventory); F1 leader `h3-high-track2-text-T1.0` at 0.775 @ 20 m
- Per-buffer F1 Spearman rho (median across populated strata × non-primary buffers) = +0.956 — combined and per-arch tiers buffer-robust
- Era 1/single-pass tier-1 collapse: 21 conditions in tier 1 at 20–30 m matching tolerance; only 1 condition (`h4-canonical-last`) survives at 40 m+ — paper-relevant methodological story

### Contextual assumptions

- Opus 4.7 was newly released at session start; the user had observed elevated confabulation rates relative to Opus 4.6. Session discipline (anti-confabulation rules, source-of-truth verification) was a session-long theme.
- Sapphire git push was configured mid-session (response to data-loss event). Future sapphire runs commit + push directly without rsync-back; this changes the workflow envelope materially.
- Cost-estimator in `launch_manifest.json` is a consistent 5× overstatement (T=0.7 estimate $355 → actual $69.60; T=0.3 estimate $355 → actual $67.79). Carry-over fix item.
- The 55-map T=0.3 run is on disk with full reproducibility metadata (launch_manifest with input SHA256s + git commit, cost_manifest with per-stage breakdown, per-pass run.meta.json, evaluation.json + extended-buffer-eval/). Paper-grade provenance is intact.
- Step 6 paper outline remains the next-session deliverable; all required analytical infrastructure is now in place.

## Session 80 — 2026-04-27/28 (map-reader-llm): Wave 1–4 secondary analyses, four corrected 55-map runs cross-analysed, agent-design infrastructure externalised, 22 new Obs (282–303)

**Commits**: ~60 on `main`, `468565f9` → `70026553`, all pushed to `origin/main`. Working tree clean at session close.

**API spend**: ~$2.30 total. Stage A verifier-T pilot $1.71 (3 verifier runs at T=0.0/0.5/1.0, reused existing T=0.0 baseline) + Stage B re-eval $0 (analysis-only, no new API) + FP-class diagnostic $0.51 (1,119 candidates × Gemini 3 Flash flex). Well under standing $5 spend cap.

**Sapphire compute**: ~6 hr total. Wave 2 phase3a MCC re-eval (252 cells, 15:17 wall at -j 8); overnight bootstrap-CI standardisation (361 cells, ~6 hr wall at -j 16 including timed-out fat-cell retries); diagnostic batch (TP-only localisation 1.8 s, per-map variance 1.4 s, FP-class ~11 min, attractor-pull 4-run 2 s, GS attractor-pull 1.3 s); v2 K-consensus SD shrinkage 50.9 min.

### Work arc

Two-day continuous session opening with the Step 6 paper-outline entry-point and consistently deferring it for "one more analytical wave". Each wave was justified by a specific deliverable; the cumulative effect was that Step 6 was deferred to next session, but with substantially stronger analytical infrastructure than at the start.

Phases (numbered for cross-reference; each landed before the next started):

1. **Wave 1 — secondary-analysis gap closure + four backlog code fixes** (~2 hr CPU, $0 API). Five secondary-analysis Plan agents + four Implement agents in parallel covering the gaps identified at start-of-session. Backlog code fixes: #2 mode-aware cost estimator (`run_generalisation.py`), #3 MCC rendering in `evaluate_detections.py` .md/.csv (the BLOCKER for Wave 2), #4 resume-mode `*.meta.json` merge (`lib_llm_metadata.py` shared utility), #5 idempotent `aggregate-cost`. Secondary analyses: SD narrowing v1 (Obs 285), Cohen's kappa inter-pass agreement (Obs 282), per-condition token efficiency (Obs 284), proposer vote-fraction-as-confidence proxy (Obs 283). Detector-confidence followup planning docs landed.

2. **Verifier-T pilot Stage A + Stage B** ($1.71 API). Stage A: 4-map gold-standard 4-of-5 consensus candidate set (607 candidates), T=0.0 reused + T=0.5 + T=1.0 fresh. Result: T=0.0 has 1.65 % deterministic verifier failures vs 0.00 % at T>0 (Obs 286). Stage B: re-evaluate T=0.5/T=1.0 against gold-standard at canonical threshold sweep + buffers + MCC. Result: F1/MCC NOT degraded; T=0.5 dominates T=1.0; recommend T=0.5 as production default (Obs 287).

3. **Wave 2 — phase3a MCC re-eval** (~2.5 hr sapphire compute, $0 API). 252 conditions across phase3a-text-matrix (156) + phase3a-image-matrix (96) re-evaluated with `--mcc --bootstrap 1000 --seed 42`. Smoke-test on `with-mcc/high-t0.7-n30-t26` (the canonical reference cell) verified backlog #3 fix renders MCC into .md/.csv. Cross-check of the 2 with-mcc reference cells against the new matrix outputs surfaced **Obs 288**: the with-mcc cells were off-matrix one-offs evaluated against the wrong consensus sources (image high-T0.7 K=10 t=7: corrected MCC 0.3831 → 0.6765 = +0.29 absolute). Archived to `archive/with-mcc-pre-2026-04-27-off-matrix/` per the project's archive-don't-delete policy.

4. **Wave 3 — staleness audit** (~30 min, $0). 8 candidate stale themes audited against post-Wave-2 / post-Phase-C source data. **0 substantive corrections** required: all narratives were already canonical-aligned. New artefact: 5m-granularity buffer-elasticity table from Phase C (commit `2a928cf7`). Recorded as Obs 290.

5. **Wave 4 — text-MIN extension to 4-run analysis grid** (~1.5 hr sapphire). User completed manual review of text-MIN candidates; corrected F1@50m = 0.7964 (lowest of four). Four parallel agents: attractor-pull 4-run, pairwise-permutation 6-pair, MCC for text-MIN, D-S aggregation + crosstab for text-MIN. Headline finding: T=0.7 vs T=MIN paired Δ +0.0296 BH p<0.001 → HIGH thinking earns its tokens out-of-sample on 55-map (Obs 297). Plus Obs 298 (4-run cap clarification: 100 m most-permissive, 125 m majority), Obs 299 (D-S calibration converges across text-track configs; image isolated as modality-specific), Obs 280-pattern reproduces on corrected runs (Obs 292), buffer-rank-reversal text-vs-image (Obs 291). Obs 293 received a brief forward-pointer update.

6. **Cross-corpus diagnostic battery** (~5 min compute total, $0.51 API for FP-class). Three diagnostics from Obs 296: TP-only localisation (Obs 296 #1; commit `682fca2d`), per-map (50,75]m rate variance (Obs 296 #3; commit `0cbae1f6`), FP-class categorical classification (Obs 296 #2; commit `e552ad46`). Plus the GS-side attractor-pull cap via geometric KDTree (Obs 295). Findings: cross-corpus cap difference is FP-anchoring driven, not detector-precision driven (Obs 300); per-map FP-anchoring rates are heavily right-skewed on text-track (median 0 %; Obs 301); contour-rings dominate at ~41 % across all four runs (Obs 302 — overturns the manual-review distractor-pull hypothesis); cap-precision framing in Obs 295 should be retired in favour of "post-calibration precision on calibration corpus" per Obs 296 + Obs 300 confirmation. Three new Obs entries (300, 301, 302) capture the diagnostic results.

7. **Bootstrap-CI standardisation to N=10K** (~6 hr sapphire wall, $0 API). Pre-flight scan of 540 evaluation.json files; 14 already at N=10K, 276 at N=1K with `_metadata.cli_args`, 250 unknown (legacy format). Implementing agent inferred 85 of the 250 (61 h8-v2/h12-v2 cells via path naming + 24 verifier-t-pilot cells via driver script modification with new `--bootstrap` CLI flag), deferred 165 per `feedback_feature_count_crosscheck.md` (paper-eval, pairwise, 55maps-cleaned-gt, gold-standard-extended-buffer-sweep). Final queue: 337 main + 24 t-pilot = 361 cells. Four 55-map MCC fat-cells (8541 tiles) timed out at -j 16 contention; orchestrator retried serially with 3 hr timeout. **Critical agent catch**: spot-check found CI width ratios 0.96–1.02 between N=1K and N=10K — bootstrap-N controls Monte Carlo noise, not CI width. My √10 expectation in the agent prompt was wrong; agent corrected the framing and continued. Recorded as Obs 303. **Orchestrator stalled at the rebase+push step** (sapphire's branch had diverged from origin via the FP-class commits landing during the sweep); needed manual rescue in the morning. Tag `pre-bootstrap-10k-2026-04-28` → `5040f5b4` pushed.

8. **Agent-design infrastructure externalised** (~25 min, $0). User noted obs-writing was a recurring pattern across projects; externalised as `~/personal-assistant/agents/obs-writer.md` (auto-detect format; collision check; commit + push; anti-confabulation rule baked in) + `~/personal-assistant/commands/observe.md` (slash command with three invocation modes). Symlinked into `~/.claude/{agents,commands}/`. First invocation (Obs 300) fell back to `general-purpose` because Claude Code's agent registry was loaded at session start; the contract was followed correctly. Subsequent Obs entries (301, 303) used the same fallback pattern.

9. **Daylight follow-up sweep spec'd** (~10 min). 165-cell completion of bootstrap-N=10K standardisation spec'd in `paper-writeup-continuity.md`. Post-hoc Explore audit confirmed all 165 are recoverable with HIGH confidence via heterogeneous metadata mechanisms (parent `.metadata.json`, source scripts, per-cell sidecars, report.md inference). Spec includes pre-flight checklist, compute estimate (30–60 min wall), Plan-first workflow per yesterday's lesson, and three explicit lessons-to-apply from the overnight run.

10. **Outstanding to-dos audit + Step 6 starting-state finalisation** (~15 min). Explore agent surveyed planning + reflection + backlog docs for outstanding items not in the continuity doc; writer agent landed 9 items in 3 priority bands (3 HIGH, 2 MEDIUM, 4 LOW/optional) into a new "Outstanding to-dos for next session" section.

### Major artefacts produced

- `docs/notes/reflections/working-notes.md` Obs 282–303 (22 new entries; closing roll-up section indexes them by topical cluster)
- `results/55maps-pairwise-permutation-v2/` — 6-pair paired permutation + tier-ranking summary tables
- `results/55maps-mcc-v2-summary/report.md` — 4-run MCC cross-run summary (extended from 3-run during Wave 4)
- `results/55maps-ds-summary-v2/report.md` — 4-run D-S cross-run summary (extended from 3-run during Wave 4)
- `results/55maps-attractor-pull-v2/` — 4-run attractor-pull v2 with text-MIN added; backup-cap = 100 m most-permissive
- `results/gold-standard-attractor-pull/` — GS-corpus attractor-pull via geometric KDTree (Obs 295)
- `results/55maps-vs-gs-tp-localisation/` — TP-only localisation diagnostic (Obs 296 #1 → Obs 300)
- `results/55maps-per-map-shell-variance/` — per-map (50,75]m rate variance bootstrap (Obs 296 #3 → Obs 300/301)
- `results/55maps-fp-classification/` — VLM-based FP-class diagnostic (Obs 296 #2 → Obs 302)
- `results/secondary-effects-token-efficiency/`, `results/secondary-effects-consensus-sd/`, `results/inter-pass-agreement/`, `results/proposer-vote-fraction/` — Wave 1 secondary-analysis outputs
- `results/verifier-t-pilot/{stage-a-report.md,stage-b-report.md}` — verifier-T production-default recommendation (T=0.5)
- `results/phase3a-{text,image}-matrix/<cell>/evaluation.{json,md,csv}` — 252 cells with canonical post-Wave-2 MCC
- `archive/with-mcc-pre-2026-04-27-off-matrix/` — archived off-matrix one-off cells (Obs 288 housekeeping)
- `archive/MIGRATION-pre-session-78-pull-2026-04-24.md` — sapphire archive cleanup migration record (carry-over backlog item #8)
- `~/personal-assistant/agents/obs-writer.md` + `~/personal-assistant/commands/observe.md` — cross-project agent + slash command for working-notes Obs production
- `planning/paper-writeup-continuity.md` — Session 80 closure section + Step 6 starting-state Obs reading list + daylight follow-up sweep spec + outstanding to-dos for next session
- `planning/detector-confidence-{calibration-pilot,flag-scoping}.md` — scoping docs for the H-a follow-up (calibration pilot zero-cost; flag opt-in deferred)
- New scripts: `scripts/launch_55maps_text_high_t0.3_review.sh`, `scripts/launch_55maps_text_min_review.sh`, `scripts/analyse_consensus_sd_shrinkage.py` + `_v2.py`, `scripts/analyse_inter_pass_agreement.py`, `scripts/analyse_proposer_vote_fraction.py`, `scripts/analyse_token_efficiency.py`, `scripts/analyse_attractor_pull_v2.py` (+ `_gs.py` sibling), `scripts/analyse_tp_localisation_55maps_vs_gs.py`, `scripts/analyse_55maps_per_map_shell_variance.py`, `scripts/analyse_verifier_t_pilot.py`, `scripts/run_bootstrap_10k.py`, `scripts/55maps-fp-classify.py`, `scripts/paired_permutation_corrected_55maps.py`
- New tests: `tests/test_evaluate_detections_mcc_rendering.py`, `tests/test_aggregate_cost_idempotency.py`, `tests/test_merge_meta.py`, `tests/test_analyse_attractor_pull_gs.py`, `tests/test_analyse_55maps_per_map_shell_variance.py`
- New feedback memory: `feedback_commit_push_before_review.md` (commit + push before requesting review)
- Tag: `pre-bootstrap-10k-2026-04-28` → `5040f5b4`

### Headline numerical findings

- **T=0.3 corrected F1 @ 50 m** = **0.8437** [0.8344, 0.8524] (10K bootstrap; matches pre-launch estimate ~0.840)
- **T=0.7 vs T=MIN paired Δ F1 @ 50 m** = **+0.0296** [+0.020, +0.039], BH p < 0.001 — HIGH thinking earns its tokens at 55-map scope (Obs 297)
- **T=0.3 paired-significant over T=0.7** at canonical R=50m: ΔF1 = +0.018, BH p < 0.001 (Obs 291)
- **Image overtakes T=0.3 on F1 by R=75 m** — buffer-rank-reversal stable across q=0.05 and q=0.01 (Obs 292)
- **4-run MCC ranking**: image (0.691) > T=0.3 (0.654) > T=0.7 (0.647) > text-MIN (0.625) — Obs 280 F1/MCC tier-leader divergence reproduces (Obs 292)
- **D-S calibration gap monotonic across all 4 runs**: text-MIN (1.88×) ≈ T=0.7 (1.90×) < T=0.3 (2.53×) < image (3.89×); image isolated as modality-specific (Obs 299)
- **Verifier T=0.0 has 1.65 % deterministic failures vs 0.00 % at T>0** on 4-map gold-standard 4-of-5 candidate set; T=0.5 production-default recommendation (Obs 286/287)
- **GS attractor-pull cap = 25 m** (geometric KDTree; Obs 295) vs **55-map cap = 100 m most-permissive / 125 m majority** (Obs 294/298) — 5-fold gap is FP-anchoring driven, not detector-precision driven (Obs 300)
- **FP-class category distribution**: contour-rings dominate at ~41 % across all four 55-map runs; numbers + benchmarks ~25 %; image vs text indistinguishable (chi² p=0.147) (Obs 302)
- **Per-map (50,75] m rate**: text-track median 0 % (heavy right-skew); image median 15.4 % (centred) — corpus rate is misleading on text-track (Obs 301)
- **Bootstrap N=10K vs N=1K**: CI width ratios 0.96–1.02 — bootstrap N controls Monte Carlo noise, not CI width (Obs 303)
- **Wave 3 staleness audit**: 0 substantive corrections from Phase C / Wave 2 source updates; 8/9 themes canonical-aligned (Obs 290)

### Contextual assumptions

- Continuation from Session 79 close — same anti-confabulation discipline carried forward; the new `feedback_commit_push_before_review.md` rule was added mid-session in response to user's "commit + push before review" directive.
- The `obs-writer` agent + `/observe` slash command were introduced mid-session and used (via `general-purpose` fallback) for Obs 300, 301, 303 and the brief Obs 293 update. Native invocation (`subagent_type=obs-writer`) failed because Claude Code's agent registry was loaded at session start; will be available natively from next session restart. This affects how next session should reference obs-writer.
- The overnight bootstrap-N=10K orchestrator stalled at the rebase+push step; manual rescue this morning rebased 11 commits onto `origin/main` (no conflicts; FP-class commits landing during the sweep didn't overlap with bootstrap-CI changes). Future overnight orchestrators should explicitly handle push divergence with retry-on-conflict.
- 165 cells currently at N=1K bootstrap remain to be upgraded; spec for daylight follow-up sweep is in `paper-writeup-continuity.md` lines 1372+. Recovery confidence is HIGH per the post-hoc Explore audit.
- The cost-estimator overstatement bug (5× on text-mode) is now fixed (mode-aware via backlog #2; commit `c738c60e`). All future API-spend estimates should use the fixed estimator.
- Step 6 paper outline remains the next-session deliverable; all required analytical infrastructure is now in place. The Step 6 starting-state Obs reading list in `paper-writeup-continuity.md` is the suggested entry point.
- Manual-review intuition vs categorical-classification trade-off: the FP-class diagnostic (Obs 302) overturned a hypothesis built from human visual review. Future analyses that depend on "what kind of feature is this" should default to uniform categorical classification across the population, not extension via more visual review.

## Session 81 — 2026-04-29/30 (map-reader-llm): cleanup + bet-test inspection + failure-mode taxonomy + GS student-data audit

### Major activities

1. **Mit-3 + BCa code change**: `scripts/lib_advanced_metrics.py` switched percentile bootstrap → BCa across all six bootstrap functions; added Mit-3 sparse-coverage flag (50 % zero-tile threshold). Schema bumped 1.0 → 1.1; `bootstrap.method = "BCa"`; `point` deterministic-statistic fields on F1/P/R/MCC; `coverage_status` rollup. Commit `2026999a`. 24 new tier-1 tests; all 839 + 43 integration tests passed; ruff clean. Rollback tag `pre-bca-mit3-2026-04-29`.
2. **Daylight sweep close-out**: 4 per-group commits `b774238b..6b611174` upgrading 162 of 165 cells from N=1K to N=10K; 2 timed-out cells re-run in commit `cbad41fd`. §7 verification: 163 N=10K presence, 4/5 F1-stability pass (one outlier `pro-text-high-t-0-7` traced to N=5 → N=10 input expansion). §7.5 verifier patched to use `mcc.point` (commit `3822645a`).
3. **Pro-n10 evaluation.json recovery**: 10 consensus levels at N=10K + `--mcc` flag (commit `f1cf5086`). Closes daylight-sweep §12 question 1.
4. **BCa re-run-all-cells migration**: 526 cells regenerated on sapphire (~10 min wall, 16-way parallel). Scaffolding `66272391` + 8 per-group data commits `014d62488..4eea8768d`. §7.7 point-estimate stability vs pre-BCa: 526/526 (Δ=0). 114/526 (21.7 %) flagged `coverage_status = "sparse_cross_grid"`.
5. **Citation audits**: ZERO surviving off-matrix `with-mcc/` citations; ZERO MCC-citation divergences from matrix-canonical (6 spot-checked). Niculiță / Guyot misattributions confirmed at lines 45 / 68 of methodology research docs; added to to-do as items #10 + #11 (commit `dd0693c4`).
6. **FN-rate analysis**: `scripts/analyse_student_gt_fn_rate.py` (760 LOC). Three-tier verdict scheme on 5 review CSVs. Bootstrap-resample by map (10K iter, seed 42). Headline: 8.87 % [6.93, 11.35] lower-bound; 11.15 % recall-adjusted central. Output `results/student-gt-fn-rate-analysis/`; commit `508e498f`.
7. **Bet-test app + inspection**: Streamlit at `scripts/v2_burial_mound_bet_test_app.py` (867 LOC) + launcher; 197-crop queue (177 reclassifications + 20 calibration). Plan committed `8d2f7f47`. User inspection: **0/177 verdicts as `real_mound_my_error`**; bet won; Obs 308 provisional status closed.
8. **Settlement-mound re-inspection app + inspection**: `scripts/v2_settlement_mound_mode2_app.py` (786 LOC), commit `d75a483e`. 117-crop queue. Result: 87 / 117 (74.4 %) `not_orange_brown` + 29 (24.8 %) `closed_topo_line_no_hachures` + 1 + 0.
9. **Failure-mode taxonomy** (Obs 312-315): three-category bet-test result + two-mechanism unification. Mechanism A = colour-veto failure (~75 %); Mechanism B = central-glyph anchor (~25 %); Mechanism C = source-domain ambiguity (mud-geyser crater item 285).
10. **Symbol-identification thread** (closed with negative result): two SovietTopoSymbols.pdf agents searched for Cat 2; first identified Items 472 + 473 (1:10k, wrong scale); second searched ≤425 (1:50k-relevant) and came up empty. Resolution: paper-Discussion uses mechanism-level framing, not symbol-identity-level. Plus Obs 314's agent context-biasing methodological note.
11. **GS student-data audit + dedup plan**: 822 features within 4 GS sheets; dedup smoke-test 0.7 % on Hairy-only at 50 m. Major reframing: 560 Hairy (97 % match curator GT) + 262 non-Hairy (3 % match, spatially disjoint median 1.2 km). Plan-doc `planning/dedupe-raw-gs-student-data-plan-2026-04-30.md` (commit `d5dc0e87`). 4-map FN re-derivation: 9.1 % cumulative (per-map 3.55 / 3.56 / 9.09 / 15.88 %); converges with 55-map estimate.
12. **Continuity-doc updates**: Session 81 closure roll-up (commit `3a8d3cf8`) + Session 82 entry-point queue with GS student-maps review thread (commit `8066599d`). Audit verdict: EXCELLENT COVERAGE.

### Major artefacts produced

- `docs/notes/reflections/working-notes.md` Obs 305-315 (11 new entries; commits `73b21b6b`, `4eb3914d`, `1a56f35b`, `c4432978`, `0d80ebcd`)
- `scripts/lib_advanced_metrics.py` — BCa + Mit-3 (commit `2026999a`)
- `scripts/evaluate_detections.py` — schema 1.1; aggregator-runs propagation patch (commit `ad4ba1bf`)
- `scripts/v2_burial_mound_bet_test_app.py` + launcher — Streamlit re-review (commits `eae884ed`, `9a99ac68`, `d318c50c`, `3107d476`)
- `scripts/v2_settlement_mound_mode2_app.py` + launcher — Streamlit Mode 2 confirmation (commit `d75a483e`)
- `scripts/analyse_student_gt_fn_rate.py` — three-tier FN analysis (commit `508e498f`)
- `scripts/build_bootstrap_10k_queue_followup.py` + `scripts/verify_bootstrap_10k_followup.py` — daylight sweep infrastructure (commits `89a5ad67`, `3822645a`)
- `results/student-gt-fn-rate-analysis/{report.md, per_map_fn_breakdown.csv, bootstrap_summary.json, figures/}`
- `results/55maps-fp-classification/v2-burial-mound-bet-test/verdicts.csv` (197 rows, all v2_overclaim)
- `results/55maps-fp-classification/v2-burial-mound-bet-test/settlement-mound-mode2-verdicts.csv` (117 rows)
- `results/gs-fp-classification/{report.md, ...}` (v2 with burial-mound categories; commit `9fa6db4e`)
- `results/55maps-fp-classification/{report.md, ...}` (v2 with burial-mound categories; commit `ec21c8ef`)
- `results/paper-eval/pro-n10/consensus-t[1-10]/evaluation.{json,csv,md}` — 10 evaluation files at N=10K
- `archive/gs-fp-classification-v1-pre-burial-mound-list/` (FP-classification v1 archive)
- `archive/55maps-fp-classification-v1-pre-burial-mound-list/` (55-map v1 archive)
- 7 new planning + status docs in `planning/` (daylight-followup-sweep-plan, gs-fp-classification-plan, pairwise-bootstrap-ci-fix-plan, daylight-sweep-status, input-expansion-audit, v2-burial-mound-bet-test-app-plan, dedupe-raw-gs-student-data-plan)
- `planning/paper-writeup-continuity.md` — Session 81 closure roll-up + Session 82 entry-point queue + GS student-maps review thread
- Tags: `pre-bca-mit3-2026-04-29`, `pre-bca-migration-2026-04-29`, `pre-bootstrap-10k-followup-2026-04-29`

### Headline numerical findings

- **Bet-test result: 0 / 177 verdicts as `real_mound_my_error`** — review-pass error rate empirically zero on v2-burial-mound reclassifications; Obs 312
- **Settlement-mound re-inspection: 87 / 117 (74.4 %) not-orange-brown** + 29 (24.8 %) closed-topo-line + 1 + 0; dominant ~75 % colour-veto-failure family
- **Failure-mode taxonomy at mechanism level**: A (colour-veto failure) ~75 %; B (central-glyph anchor) ~25 %; C (source-domain ambiguity) small but real
- **55-map student-GT FN rate: 8.87 % [6.93, 11.35]** lower-bound; **11.15 %** recall-adjusted central; per-map IQR 4.3-12.8 %, K-35-076-2 outlier at 52.5 %
- **4-map FN re-derivation: 9.1 % cumulative** (per-map 3.55 / 3.56 / 9.09 / 15.88 %); 4-map and 55-map converge at 9-11 %; Sobotkova 2023's published 5.0 % conceded as calculation issue
- **Cross-corpus chi-square (v2 closed list)**: >125 m stratum chi² = 50.231, Monte Carlo p = 0.0028; >50 m p = 0.0012; significant divergence; Obs 307
- **TP-side calibration validation (v2)**: 56.9 % TPs as burial-mound categories (vs v1's 0 %); v1's 60 % `contour-ring` collapses entirely; closed-list-design issue confirmed
- **Daylight sweep N=10K**: 165/165 cells now at N=10K; closes Obs 303 forward-pointer
- **BCa migration**: 526 cells regenerated; ZERO point-estimate drift; 114/526 (21.7 %) flagged sparse_cross_grid (Obs 311)
- **Pairwise CI bug closed**: example `512px-image-t0` @ 30 m: F1 = 0.5132, percentile CI = [0.139, 0.422] → BCa CI = [0.262, 0.324] (point inside)
- **Raw GS student data**: 822 features; 560 Hairy / 262 non-Hairy; dedup smoke-test 0.7 % at 50 m
- **Soviet topo legend confirmation**: items 62 + 81-83 (≤425) include all four burial-mound subtypes named in the proposer prompt; proposer vocabulary is canonical, not invented

### Contextual assumptions

- The user (Shawn) was the original curator of the 4 GS maps for Sobotkova 2022, and re-checked them once before this project; curator GT (`mounds-reference.geojson`, 569 mounds) is sub-metre-precise per his manual centring pass. He is the authoritative source on actual on-map rendering colours.
- TM 30-548 (US Army 1958 Soviet Topographic Map Symbols guide) is reliable for symbol structure / identity / numbering / labels but partial-reliability for colour in B&W-print sections. Trust shape + hachure direction + central glyph + item number + names; cross-check colour against user's domain expertise.
- The premature-completion pattern in agents that orchestrate parallel background work (4 instances this session) is well-documented in Obs 310 + Session 81 entry in `llm-observations.md`. External orchestration (manual commits or watch-loops via Bash `run_in_background`) is the workaround.
- The non-Hairy 262 student points are an unresolved population question — Session 82 priority #1.
- The agent context-biasing pattern (Item 472 misidentification) is a non-confabulation reasoning failure mode; mitigation in future agent prompts via the "identify based on visual properties / objective evidence ONLY" template clause (Obs 314).
- The bet-test inspection's 0/177 result validates the user's review-pass labels as a clean ground truth; the FN-rate analysis (Obs 305) is therefore unbiased by review-pass mislabelling.
- Step 6 paper outline still pending — but the failure-mode catalogue is mechanism-level paper-Discussion-ready, and the FN-rate framing is paper-Methods-ready (4-map / 55-map convergence at 9-11 %; Sobotkova correction note).
- Session 82 has a focused 1-2 hour pickup before returning to Step 6: non-Hairy provenance (~30 min), K-35-062-2 outlier investigation (~20 min), Obs 305 amendment with cross-validation finding (~15 min).
