# Execution Plan: VLM Burial Mound Detection Study

**Companion document to**: `preregistration.md`
**Purpose**: Operational sequencing for executing the preregistered experiments
**Status**: Draft for review

---

## Dependency Graph

```text
Phase 0: Preparation
    │
    ▼
Phase 1: Library + Verbose Text Construction ───────────────┐
    │                                                       │
    ▼                                                       │
Phase 2: Core Factorial (H1, H2, H7, H9) ◄──────────────────┤
    │    100 conditions × K=10 runs                         │
    │                                                       │
    ├───────────────┬───────────────┬───────────────┐       │
    ▼               ▼               ▼               ▼       │
Phase 3a:       Phase 3b:       Phase 3c:       Phase 3d:   │
H4 Voting       H5 Ordering     H6 Diversity    H3 Two-Stage│
(N=30 extend)   (partial cross)                             │
    │               │               │               │       │
    └───────────────┴───────────────┴───────────────┘       │
                    │                                       │
                    ▼                                       │
            Phase 4: H8 Flash→Pro Transfer (OFAT) ◄─────────┘
                    │
                    ▼
            Phase 5: Exploratory (H10-H16)
```

**Note**: H2 (Text Elaboration) is now integrated into the main factorial as the M/E factor (5 levels). Phase 3d formerly tested H2 separately; this is no longer required.

---

## Phase 0: Preparation (Before Any API Calls)

**Duration**: 1-2 days
**Cost**: $0

### Checklist

- [x] **Prompts**: Finalise all instruction files (2026-01-01)
  - [x] `detect_image-only.md` and `detect_image-only_hardneg.md`
  - [x] `detect_brief-text.md` and `detect_brief-text_hardneg.md`
  - [x] `detect_brief-text-image.md` and `detect_brief-text-image_hardneg.md`
  - [x] `detect_verbose-text.md` and `detect_verbose-text_hardneg.md`
  - [x] `detect_verbose-text-image.md` and `detect_verbose-text-image_hardneg.md`
  - [ ] H6 text variants (5 semantically equivalent instructions, constructed after Phase 2)
  - [x] `propose_image-only.md` and `verify_image-only.md` (H3)

- [x] **Configs**: Create all JSON config files (2026-01-01)
  - [x] 16 main factorial configs: 5 M/E × 4 H7 (minus 4 invalid text-only × image-H7 combos)
  - [x] Naming pattern: `detect_{modality}_{hardneg}.json`
  - [ ] H5 ordering variants (6 configs: 2 orderings × 3 M/E levels)
  - [ ] H9 temperature: runtime parameter, no separate configs needed
  - [ ] H6 diversity configs: constructed after Phase 2 optimal determined

- [x] **Scripts**: Verify/create analysis code (2026-01-02)
  - [x] Batch detection script handles all config variants
  - [x] Comprehensive metadata tracking (`lib_llm_metadata.py`)
  - [ ] F1 evaluation with Hungarian matching
  - [ ] Voting aggregation at multiple thresholds
  - [ ] Results collation and statistical tests

- [ ] **Data management**:
  - [ ] Create output directory structure (see below)
  - [ ] Set up results tracking spreadsheet
  - [x] API pricing documented in `lib_llm_metadata.py` (2026-01-02)

### Output Directory Structure

```text
outputs/
├── phase1-library/
│   ├── baseline-runs/
│   │   ├── detections-*.geojson
│   │   └── detections-*.meta.json    # Run metadata
│   └── hard-example-analysis/
├── phase2-factorial/
│   ├── raw-responses/
│   │   ├── {condition_id}/
│   │   │   ├── detections.geojson
│   │   │   └── detections.meta.json  # Per-condition metadata
│   └── aggregated/
├── phase3-followup/
│   ├── h4-voting/
│   ├── h5-ordering/
│   ├── h6-diversity/
│   └── h3-twostage/
│       ├── candidates.geojson        # Proposer output
│       ├── candidates.meta.json
│       ├── verified.geojson          # Verifier output
│       └── verified.meta.json
├── phase4-transfer/
│   └── pro-replication/
└── phase5-exploratory/
```

### Metadata Output Format

Each script run produces a `.meta.json` file containing:

- **Run identification**: UUID, timestamps, git commit
- **Configuration snapshot**: Full config including prompt hash
- **Execution stats**: Items processed, retries, failures
- **Token usage**: Input/output/cached tokens by provider
- **Cost estimate**: Calculated from current pricing
- **Per-item metadata**: Detailed per-tile/per-candidate data

See `docs/PIPELINES.md` for full schema documentation.

---

## Phase 1: Library + Verbose Text Construction

**Duration**: 0.5 days
**Estimated cost**: ~$1-2 (Flash)
**Prerequisite for**: All subsequent phases

### Purpose

Run baseline detection on training tiles to:

1. Identify hard examples for the few-shot library
2. Derive verbose text additions from the same failures (text-image alignment)

### Procedure

**Step 1: Image-Only Baseline**

- Prompt: Image-only (4 canonical positives + 3 null tiles, minimal text instruction)
- Passes: 5 × 20 training tiles = 100 API calls
- Temperature: T=1.0

**Step 2: Failure Analysis**

- Identify False Negatives (FNs): Ground truth mounds missed in ≥3/5 passes
- Identify False Positives (FPs): Detections in ≥3/5 passes with no matching ground truth
- Rank by frequency and categorise by failure type

**Step 3: Construct Hard Example Library**

Select hard examples based on frequency ranking:

- Hard positives: Top K FNs (target K=4)
- Hard negatives: Top M FPs (target M=3)

Document for each selected example:

- Source tile
- Frequency (passes where failure occurred)
- Failure category (e.g., "occluded mound", "benchmark confusion")

**Step 4: Construct Verbose Text**

Build verbose text by adding edge case guidance for hard positives:

| Component | Source | Content |
|-----------|--------|---------|
| Base | Legend descriptions | Brief text describing canonical mound types |
| Edge case guidance | Hard positive images | Text describing why each FN IS a mound (e.g., occluded symbols, degraded examples) |

**Note on exclusion guidance**: Text describing hard negatives (FPs) is NOT part of verbose text. Exclusion guidance is controlled by the H7 factor:
- H7 = None or Images-only: No exclusion text
- H7 = Text-only or Text+Images: Exclusion text added via `_hardneg.md` instruction variants

This separation ensures H2 (elaboration) and H7 (hard negatives) remain orthogonal factors.

**Alignment requirement**: Each hard positive image must have corresponding edge case text in verbose prompts.

**Step 5: Construct Brief vs Verbose Text**

| Text Version | Content |
|--------------|---------|
| Brief text | Legend-based descriptions of canonical mound types only (~200-400 words) |
| Verbose text | Brief text + edge case guidance for hard positives (~400-700 words) |

**Note**: Exclusion guidance for hard negatives is added separately via H7 `_hardneg.md` variants, not via the brief/verbose distinction.

**Text-modality consistency**: Identical text is used across modalities:

- Text-only brief = Text+image brief (same text)
- Text-only verbose = Text+image verbose (same text)

**Step 6: Document and Upload**

Before any holdout evaluation, upload to OSF:

- [ ] `inputs/few-shot-library/hard-positives/` (4 images)
- [ ] `inputs/few-shot-library/hard-negatives/` (3 images)
- [ ] `inputs/few-shot-library/library-manifest.json`
- [ ] `prompts/brief-text.md` (identical for text-only and text+image)
- [ ] `prompts/verbose-text.md` (identical for text-only and text+image)
- [ ] `prompts/text-image-alignment.md` (mapping of hard examples to text)

### Decision Point

If <4 distinct FNs or <3 distinct FPs are found:

- Option A: Proceed with smaller hard example set (document)
- Option B: Lower frequency threshold (≥2/5 instead of ≥3/5)
- Document decision and rationale

---

## Phase 2: Core Factorial (H1, H2, H7, H9)

**Duration**: 2-3 days
**Estimated cost**: ~$90 (Flash)
**Prerequisites**: Phase 1 complete, library and text uploaded to OSF

### Design

Full 5×4×5 factorial on Gemini 3 Flash:

| Factor | Levels | Values |
|--------|--------|--------|
| Modality/Elaboration (M/E) | 5 | Image-only, Brief-text, Brief-text+image, Verbose-text, Verbose-text+image |
| Hard negatives (H7) | 4 | None, Text-only, Images-only, Text+Images |
| Temperature (T) | 5 | 0.0, 0.3, 0.7, 1.0, 1.3 |

**Note**: Ordering (H5) is tested as a partial cross in Phase 3b, not in the main factorial. All main factorial conditions use canonical-first ordering.

**Total**: 100 conditions × K=10 runs × 60 holdout tiles = **60,000 API calls**

**Implementation note**: The 100 conditions are implemented using 16 config files × 5 temperature values (runtime parameter). Text-only modalities (Brief-text, Verbose-text) only have 2 valid H7 levels each (None, Text-only), yielding 16 rather than 20 configs.

### Evaluation Protocol

Each condition is evaluated using K=10 independent single-pass runs (see preregistration Section 3.8):

- Results characterised statistically (mean F1, SD, 95% CI)
- Post-hoc voting computed from runs (N=5 from runs 1-5 or 6-10; N=10 from all runs)
- No circular application of voting when testing main effects

### Execution Order

Run conditions in randomised order to distribute any temporal effects (API performance variation, rate limiting).

```python
# Pseudocode for execution
conditions = generate_all_100_conditions()
random.seed(20260104)  # Document seed
random.shuffle(conditions)

for condition in conditions:
    for tile in holdout_tiles:
        for run_num in range(10):  # K=10 independent runs
            run_detection(condition, tile, run_num)
            save_response()
    # Checkpoint after each condition
    save_checkpoint(condition)
```

### Checkpoints

- After every 10 conditions (~6,000 calls): Spot-check parsing success rate
- If parsing failure rate >5%: Pause and investigate
- If API errors >10%: Pause and check rate limits

### Outputs

- [ ] Raw JSON responses: `outputs/phase2-factorial/raw-responses/{condition_id}/{tile_id}_run{n}.json`
- [ ] Aggregated results: `outputs/phase2-factorial/aggregated/factorial-results.csv`
- [ ] Preliminary ANOVA: `outputs/phase2-factorial/factorial-anova.md`

### Analysis (Immediate)

1. Compute mean F1 and SD for each condition across K=10 runs
2. Run 3-way ANOVA: M/E × H7 × T
3. Compute post-hoc voting performance at multiple thresholds
4. Identify significant main effects and interactions
5. **Decision**: Which factors show significant effects? These inform Phase 3 priorities.

---

## Phase 3: Follow-up Experiments (Parallel)

These can run in parallel after Phase 2, depending on results.

### Phase 3a: H4 Voting Extension (N=30)

**Duration**: 0.5 days
**Estimated cost**: ~$2 (Flash)
**Trigger**: Always run (Tier 1 priority)

#### Design

The K=10 runs from Phase 2 provide data for voting analysis at N=5 and N=10. Phase 3a extends to N=30 at the optimal configuration only.

**Data from Phase 2 (no additional calls)**:

| Pool size (N) | Source | Thresholds |
|---------------|--------|------------|
| 5 | Runs 1-5 or 6-10 | 1, 2, 3, 4, 5 |
| 10 | All runs 1-10 | 1, 2, ..., 10 |

**Additional runs for N=30**:

- 20 additional runs at optimal config (already have 10 from Phase 2)
- 20 runs × 60 tiles = **1,200 API calls**

#### Execution

1. Identify optimal configuration from Phase 2 results
2. Run 20 additional passes at that configuration
3. Combine with K=10 runs for N=30 voting pool
4. Analyse threshold sweep across N=5, 10, 30

#### Outputs

- [ ] Threshold sweep curves (F1, precision, recall vs T for each N)
- [ ] Optimal (N, T) recommendation
- [ ] Cost-efficiency analysis (F1 per dollar)

---

### Phase 3b: H5 Ordering (Partial Cross)

**Duration**: 0.5 days
**Estimated cost**: ~$5 (Flash)
**Trigger**: Always run

#### Design

Test 3 orderings × 3 M/E levels, but canonical-first is already in the main factorial. This adds **6 new conditions** (2 orderings × 3 M/E levels):

| Ordering | M/E Levels Tested |
|----------|-------------------|
| Canonical-first | (covered in main factorial) |
| Canonical-last | Image-only, Brief-text+image, Verbose-text+image |
| Random | Image-only, Brief-text+image, Verbose-text+image |

**Note**: Canonical-first is covered in the main factorial. This adds 6 new conditions (2 orderings × 3 M/E levels).

**API calls**: 6 conditions × K=10 runs × 60 tiles = **3,600 API calls**

**Fixed parameters**: All H5 conditions tested at optimal H7 and T from Phase 2 results.

#### Mitigation Trigger

If O × M/E interaction is detected (p < 0.10), extend to remaining 2 M/E levels (Brief-text and Verbose-text).

#### Outputs

- [ ] 3 × 3 ANOVA (ordering × M/E)
- [ ] Interaction test results
- [ ] Recommendation for operational ordering

---

### Phase 3c: H6 Diversity Testing

**Duration**: 1 day
**Estimated cost**: ~$9 (Flash)
**Trigger**: Run if H4 shows voting helps (expected)

#### Design

2×2 factorial at optimal configuration:

| Condition | Text | Images | Description |
|-----------|------|--------|-------------|
| A | Fixed | Fixed | Baseline: identical prompt and examples across all 5 passes |
| B | Varied | Fixed | 5 prompt variants, same images |
| C | Fixed | Varied | Same prompt, resampled hard examples per pass |
| D | Varied | Varied | Both mechanisms |

**API calls**:

- Each condition: 5 runs × 5 passes × 60 tiles = 1,500 calls
- 4 conditions × 1,500 = **6,000 calls**

#### Outputs

- [ ] 2×2 ANOVA results
- [ ] Effect sizes for text diversity, image diversity, interaction

---

### Phase 3d: H3 Two-Stage Pipeline

**Duration**: 1 day
**Estimated cost**: ~$2 (Flash)
**Trigger**: Always run (confirms preliminary finding)

#### Design

Compare:

- Condition A: Single-stage detection (optimal from Phase 2)
- Condition B: Proposer → Verifier pipeline

**API calls**:

- Proposer: K=10 runs × 60 tiles = 600 calls
- Verifier: ~X candidates × 60 tiles (depends on proposer output)
- Estimate: ~600-1,200 total calls

**Stopping rule**: Two-stage must exceed single-stage by ≥0.05 F1 to justify ~2× cost overhead (see preregistration H3).

#### Outputs

- [ ] F1 comparison (single-stage vs two-stage)
- [ ] Error analysis: What does two-stage miss that single-stage catches?

---

## Phase 4: H8 Flash→Pro Transfer (OFAT)

**Duration**: 2-3 days
**Estimated cost**: ~$60-90 (Pro is ~10× Flash cost)
**Prerequisites**: Phase 2 complete

### Design

Validate Flash-optimal configuration on Gemini 3 Pro using One-Factor-At-a-Time (OFAT) approach. Uses 20-tile stratified subset (preserving density distribution from the 60 holdout tiles).

### Phase 4a: Baseline Comparison

**Purpose**: Verify Pro performance at Flash-optimal configuration.

**API calls**: K=10 runs × 20 tiles = 200 calls

**Decision point**: If Pro F1 within 0.05 of Flash F1, proceed with OFAT. If large degradation (>0.10 F1), investigate before continuing.

### Phase 4b: OFAT Sensitivity Testing

**Purpose**: Test 1-2 alternatives per factor to check if optimal point differs.

| Factor | Flash Optimal | Alternatives to Test |
|--------|---------------|---------------------|
| M/E | (from Phase 2) | 1-2 adjacent levels |
| H7 | (from Phase 2) | 1-2 adjacent levels |
| T | (from Phase 2) | ±0.3 temperatures |

**API calls**: ~3 factors × 2 alternatives × K=10 runs × 20 tiles = ~1,200 calls

### Phase 4c: Voting Analysis

**Purpose**: Verify Flash voting threshold transfers.

**Data source**: Runs from Phase 4a-4b provide voting pools.

**Analysis**: Compute optimal threshold from Phase 4a-4b data; compare to Flash-optimal.

### Phase 4d: Refinement (Conditional)

**Trigger**: Only if Phase 4b shows optimum differs from Flash.

**Design**: Targeted follow-up at Pro-optimal configuration.

**API calls**: ~K=10 × 20 tiles = 200 calls (if triggered)

### Total Phase 4 API Calls

| Sub-phase | API Calls | Est. Cost |
|-----------|-----------|-----------|
| 4a: Baseline | 200 | ~$15 |
| 4b: OFAT | ~1,200 | ~$90 |
| 4c: Voting | (from 4a-4b) | — |
| 4d: Refinement | 0-200 | $0-15 |
| **Total** | **~1,400-1,600** | **~$105-120** |

**Note**: Pro pricing is ~10× Flash (~$0.075/call vs ~$0.0015/call). If Pro shows dramatic superiority warranting full optimisation, budget for extended Pro testing (~$50-80 additional).

### Outputs

- [ ] Transfer success rate (% factors transferring)
- [ ] Pro-specific recommendations (if any)
- [ ] Voting threshold comparison (Flash vs Pro)

---

## Phase 5: Exploratory Hypotheses

**Duration**: Variable
**Estimated cost**: ~$20-50 (budget permitting)
**Prerequisites**: Phases 2-4 complete

### Priority Order

1. **H12 (cross-model consistency)**: Most important for generalisability
   - Test Flash-optimal configuration on Claude 4.5 Sonnet and GPT-5.2 Thinking
   - OFAT sensitivity testing per factor (same protocol as H8)
   - ~$40-60 (depends on provider pricing)

2. **H13 (cross-model voting)**: Novel contribution
   - 6-pass voting: 6×Flash vs 6×Sonnet vs 6×GPT vs 2×each
   - ~$15-25

3. **H10 (fine-to-coarse)**: Novel architecture
   - Context-expanded re-query for uncertain detections
   - ~$5-10

4. **H11, H14, H15, H16**: Lower priority, if budget allows

---

## Budget Summary

| Phase | API Calls | Estimated Cost |
|-------|-----------|----------------|
| Phase 1: Library + Text | ~100 | $1-2 |
| Phase 2: Factorial (100 × K=10) | ~60,000 | ~$90 |
| Phase 3a: H4 N=30 Extension | ~1,200 | ~$2 |
| Phase 3b: H5 Ordering | ~3,600 | ~$5 |
| Phase 3c: H6 Diversity | ~6,000 | ~$9 |
| Phase 3d: H3 Two-Stage | ~1,200 | ~$2 |
| **Flash Subtotal** | **~72,100** | **~$109** |
| Phase 4: H8 Pro Transfer | ~1,400-1,600 | ~$105-120 |
| **Confirmatory Total** | **~73,500-73,700** | **~$214-229** |
| Phase 5: Exploratory | ~2,000-5,000 | ~$30-60 |
| **Grand Total** | **~75,500-78,700** | **~$244-289** |

**Contingency**: 20% buffer → **Budget ceiling: ~$350**

**Note**: The majority of cost comes from Pro model testing (Phase 4) at ~10× Flash pricing. Flash-only confirmatory testing would cost ~$109.

---

## Quality Control Checkpoints

### After Each Phase

1. **Parsing check**: % responses successfully parsed as JSON
   - Acceptable: ≥95%
   - Action if <95%: Investigate malformed responses, adjust parsing

2. **Sanity check**: F1 on training tiles (should match Phase 1 baseline ±0.05)
   - Action if drift detected: Check for API changes, model updates

3. **Cost check**: Actual vs estimated spend
   - Action if >120% estimate: Pause, review before continuing

### Stopping Rules

| Condition | Action |
|-----------|--------|
| Budget reaches $200 | Pause, prioritise remaining experiments |
| API error rate >20% sustained | Pause, contact provider |
| Model deprecated mid-study | Document, switch to successor, note in limitations |
| Clear null result (p > 0.5, effect ~0) | Complete condition but deprioritise follow-up |

---

## Timeline (Estimated)

| Week | Activities |
|------|------------|
| Week 1 (Dec 30 - Jan 5) | Phase 0 preparation, Phase 1 library construction |
| Week 2 (Jan 6 - Jan 12) | Phase 2 factorial execution |
| Week 3 (Jan 13 - Jan 19) | Phase 2 analysis, Phase 3 parallel experiments |
| Week 4 (Jan 20 - Jan 26) | Phase 4 Pro transfer, begin Phase 5 |
| Week 5 (Jan 27 - Jan 31) | Complete Phase 5, final analysis, write-up |

---

## Outputs Checklist (Pre-Submission)

Before submitting results:

- [ ] All raw API responses archived
- [ ] All `.meta.json` metadata files archived
- [ ] Aggregated results in CSV format
- [ ] Analysis scripts committed to repository
- [ ] Few-shot library uploaded to OSF
- [ ] Statistical analysis complete with FDR correction
- [ ] Effect sizes and confidence intervals computed
- [ ] Figures: threshold curves, factorial interaction plots
- [ ] Cost summary from metadata files
- [ ] Deviations from preregistration documented

---

*Document version: 2.2*
*Created: 2025-12-31*
*Updated: 2026-01-04*

**Changelog:**

- v2.2: Final review fixes — H2/H7 orthogonality in Phase 1 (exclusion guidance controlled by H7 only); corrected Pro cost estimates (~$105-120, not ~$21-24); fixed budget summary totals; updated file naming to match 10-instruction structure; fixed H5 condition count (6 new, not 9); removed stale h2-elaboration directory; corrected H12 description
- v2.1: Fixed stale E7 reference → H16 in dependency graph and Phase 5 priority list
- v2.0: Major design update — revised to 100-condition factorial (5 M/E × 4 H7 × 5 T); K=10 independent runs protocol; Phase 1 now includes verbose text construction with text-image alignment; H2 integrated into main factorial (removed Phase 3d); H5 partial cross design; H8 OFAT approach on 20-tile subset; revised budget summary (~$150-183 vs ~$187-326)
- v1.2: Added metadata tracking documentation
- v1.1: Added H6 diversity configs, H9 temperature parameter
- v1.0: Initial execution plan
