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

*New session entries should be appended above this line.*
