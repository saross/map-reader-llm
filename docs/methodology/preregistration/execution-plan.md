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
Phase 1: Library + Text Construction ───────────────────────┐
    │                                                       │
    ▼                                                       │
Phase 2a: Strand 1 (Verbosity × Partial H7) ◄───────────────┤
    │    50 cells × K=10 runs                               │
    ▼                                                       │
Phase 2b: H7 Confirmatory (Full 2×2 at Optimal M/E)         │
    │    20 cells × K=10 runs                               │
    ▼                                                       │
Phase 2c: Strand 2 (Library Size H15) ──────────────────────┤
    │    30 cells × K=10 runs                               │
    ▼                                                       │
Phase 2d: Strand 3 (Interaction, conditional)               │
    │    ~10 cells × K=10 runs                              │
    │                                                       │
    ├───────────────┬───────────────┬───────────────┐       │
    ▼               ▼               ▼               ▼       │
Phase 3a:       Phase 3b:       Phase 3c:       Phase 3d:   │
H4 Voting       H5 Ordering     H6 Diversity    H3 Two-Stage│
(N=30 extend)   (partial cross) (exploratory)   (exploratory)
    │               │               │               │       │
    └───────────────┴───────────────┴───────────────┘       │
                    │                                       │
                    ▼                                       │
            Phase 4: H8 Flash→Pro Transfer (OFAT) ◄─────────┘
                    │                                       (exploratory)
                    ▼
            Phase 5: Exploratory (H10-H14, H16, H17)
```

**Note**: The stranded design separates text elaboration (Strand 1) from library content (Strand 2). H3, H6, and H8 are now exploratory hypotheses.

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

**Step 4: Construct Brief Text**

Build brief text with terse descriptions:

| Component | Source | Content |
| --------- | ------ | ------- |
| Canonical descriptions | Legend | Terse descriptions of 4 canonical mound types |
| HP edge case guidance | Hard positive images | Terse mention of edge case types ("symbols may be partially occluded") |

Word count: ~200-300 words.

**Step 5: Construct Verbose Text**

Expand brief text with detailed guidance:

| Component | Source | Content |
| --------- | ------ | ------- |
| Canonical descriptions | Legend | Detailed descriptions of 4 canonical types (size, colour, ray count, context) |
| HP edge case guidance | Hard positive images | Detailed guidance on occlusion types, degradation patterns, clustering |

Word count: ~500-700 words.

**Brief vs Verbose distinction**: Both include the same content categories (canonical symbols + HP edge cases). The difference is detail level, not content coverage.

**Note on exclusion guidance**: Exclusion guidance for hard negatives (FPs) is NOT part of either brief or verbose text. Exclusion guidance is controlled by the H7 factor via `_hardneg.md` instruction variants:

- H7 = None or Images-only: No exclusion text
- H7 = Text-only or Text+Images: Exclusion text added

This separation ensures H2 (text elaboration) and H7 (hard negatives) remain orthogonal factors.

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

## Phase 2: Stranded Factorial Design (H1, H2, H7, H9, H15)

**Duration**: 3-4 days
**Estimated cost**: ~$99 (Flash)
**Prerequisites**: Phase 1 complete, library and text uploaded to OSF

The stranded design separates text elaboration (Strand 1) from library content (Strand 2), avoiding a full factorial cross that would conflate these factors.

---

### Phase 2a: Strand 1 — Verbosity × Partial H7 Cross

**Purpose**: Determine optimal text elaboration and hard negative settings.

**Design**: 5 M/E levels × partial H7 cross × 5 temperatures:

**Image-using modalities (3 levels)**:

| M/E | H7=None | H7=Text+Images |
|-----|---------|----------------|
| Image-only | ✓ | ✓ |
| Brief+image | ✓ | ✓ |
| Verbose+image | ✓ | ✓ |

**Text-only modalities (2 levels)**:

| M/E | H7=None | H7=Text-only |
|-----|---------|--------------|
| Brief-text | ✓ | ✓ |
| Verbose-text | ✓ | ✓ |

**Strand 1 totals**:

- (3 image M/E × 2 H7 × 5 T) + (2 text M/E × 2 H7 × 5 T) = 30 + 20 = **50 cells**
- 50 × K=10 × 60 tiles = **30,000 API calls** (~$45)

**Fixed parameters**: All conditions use Library A (13 examples: 4 Canon+, 2 Canon-, 2 HP, 2 Emp-HN, 3 nulls). Canonical-first ordering.

**Analysis**:

1. 2-way ANOVA: M/E × H7 (aggregating over T)
2. 1-way ANOVA on T (at optimal M/E × H7)
3. Identify optimal M/E and optimal H7 for next stage

---

### Phase 2b: H7 Confirmatory — Full 2×2 at Optimal M/E

**Purpose**: Test all 4 H7 levels at the optimal modality from Strand 1.

**Design**: Full 2×2 H7 factorial at optimal M/E:

| H7 Level | Exclusion Text | HN Images |
|----------|----------------|-----------|
| None | No | No |
| Text-only | Yes | No |
| Images-only | No | Yes (minimal labels) |
| Text+Images | Yes | Yes (detailed labels) |

**H7 Confirmatory totals**:

- 4 H7 × 5 T = **20 cells**
- 20 × K=10 × 60 = **12,000 API calls** (~$18)

**Note**: H7=None and H7=Text+Images are already tested in Strand 1 at optimal M/E. This adds H7=Text-only and H7=Images-only conditions, yielding complete 2×2 data.

**Expansion trigger**: Run H7 middle levels (Text-only, Images-only) at second-best M/E if:

- M/E × H7 interaction (p < 0.10) in Strand 1, OR
- H7 main effect > 0.08 F1 in Strand 1

**Expansion cost (if triggered)**: 2 H7 × 5 T × K=10 × 60 = **6,000 calls** (~$9)

---

### Phase 2c: Strand 2 — Library Size (H15)

**Purpose**: Determine optimal hard example library size.

**Prerequisite**: Optimal M/E and H7 from Strands 1 and 2b.

**Design**: 6 library conditions at optimal M/E and H7:

| Condition | Canon+ | Canon- | HP | Emp-HN | Nulls | Total | Hard Examples |
|-----------|--------|--------|-----|--------|-------|-------|---------------|
| Pure | 4 | 0 | 0 | 0 | 3 | 7 | 0 |
| Canonical | 4 | 2 | 0 | 0 | 3 | 9 | 0 |
| A | 4 | 2 | 2 | 2 | 3 | 13 | 4 |
| B | 4 | 2 | 4 | 4 | 3 | 17 | 8 |
| C | 4 | 2 | 8 | 8 | 3 | 25 | 16 |
| D | 4 | 2 | 16 | 16 | 3 | 41 | 32 |

**Terminology**:

- **Canon+**: Legend-derived positives (burial mound, settlement mound, trig on mound, bench mark on mound)
- **Canon-**: Legend-derived negatives (standalone trig point, standalone bench mark)
- **HP**: Empirically-derived hard positives (FNs from Phase 1)
- **Emp-HN**: Empirically-derived hard negatives (FPs from Phase 1)

**H7 constraint**: Pure and Canonical run at H7=None (no empirical HNs available). Conditions A-D run at optimal H7 from Strand 1.

**Strand 2 totals**:

- 6 conditions × 5 T = **30 cells**
- 30 × K=10 × 60 = **18,000 API calls** (~$27)

**Planned contrasts**:

1. Pure → Canonical: Do legend-derived negatives help?
2. Canonical → A: Do empirical hard examples help? (confounded with H7 if optimal ≠ None)
3. A → B → C → D: Diminishing returns curve

**Confound note**: The Canonical → A contrast is confounded if Strand 1 optimal H7 ≠ None, because Canonical runs at H7=None while A runs at optimal H7. Document adjustment option in analysis.

---

### Phase 2d: Strand 3 — Interaction Check (Conditional)

**Purpose**: Check whether optimal verbosity depends on library size.

**Trigger**: Run if BOTH:

1. Strand 1 shows significant M/E effect (p < 0.05), AND
2. Strand 2 shows significant library size effect (p < 0.05)

**Design**: Test second-best M/E at 2 library sizes (optimal and one adjacent):

- 2 M/E × 2 Library × 5 T = **20 cells** (10 new cells; 10 overlap with Strands 1-2)
- ~10 new cells × K=10 × 60 = **6,000 API calls** (~$9)

**Analysis**: Test M/E × Library interaction. If significant (p < 0.10), optimal configuration depends on library size.

---

### Evaluation Protocol (All Strands)

Each condition is evaluated using K=10 independent single-pass runs (see preregistration Section 3.8):

- Results characterised statistically (mean F1, SD, 95% CI)
- Post-hoc voting computed from runs (N=5 from runs 1-5 or 6-10; N=10 from all runs)
- No circular application of voting when testing main effects

### Execution Order

Run conditions in randomised order within each strand to distribute temporal effects.

```python
# Pseudocode for strand execution
def run_strand(strand_conditions, seed):
    random.seed(seed)
    random.shuffle(strand_conditions)
    for condition in strand_conditions:
        for tile in holdout_tiles:
            for run_num in range(10):  # K=10 independent runs
                run_detection(condition, tile, run_num)
                save_response()
        save_checkpoint(condition)

# Execute strands sequentially
run_strand(strand1_conditions, seed=20260104)
analyse_strand1()  # Determine optimal M/E, H7
run_strand(h7_confirmatory_conditions, seed=20260105)
analyse_h7()  # Complete H7 picture
run_strand(strand2_conditions, seed=20260106)
analyse_strand2()  # Determine optimal library size
if interaction_triggered():
    run_strand(strand3_conditions, seed=20260107)
```

### Checkpoints

- After every 10 conditions (~6,000 calls): Spot-check parsing success rate
- If parsing failure rate >5%: Pause and investigate
- If API errors >10%: Pause and check rate limits

### Outputs

- [ ] Raw JSON responses: `outputs/phase2-factorial/raw-responses/{strand}/{condition_id}/{tile_id}_run{n}.json`
- [ ] Aggregated results: `outputs/phase2-factorial/aggregated/strand{n}-results.csv`
- [ ] Strand analyses: `outputs/phase2-factorial/strand{n}-anova.md`
- [ ] Final optimal configuration: `outputs/phase2-factorial/optimal-config.json`

### Analysis Summary

| Strand | Primary Analysis | Key Output |
|--------|------------------|------------|
| 1 | M/E × H7 partial ANOVA | Optimal M/E, preliminary H7 |
| 2b | H7 2×2 ANOVA | Optimal H7 (confirmed) |
| 2c | Library size ANOVA + contrasts | Optimal library size |
| 3 | M/E × Library interaction | Interaction present? |

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
**Estimated cost**: ~$40-60 (budget permitting)
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

4. **H17 (HP:HN ratio)**: Ratio exploration
   - At optimal library size from H15 (A-D only), compare HP:HN ratios at fixed total count
   - 3 ratios: 1:3 (HN-heavy), 1:1 (baseline), 3:1 (HP-heavy)
   - Trigger: Run if H15 shows library size matters AND budget permits
   - ~$9 incremental (R2 already tested in H15)

5. **H11, H14, H16**: Lower priority, if budget allows

---

## Budget Summary

| Phase | API Calls | Estimated Cost |
|-------|-----------|----------------|
| Phase 1: Library + Text | ~100 | ~$1-2 |
| Phase 2a: Strand 1 (Verbosity × partial H7) | ~30,000 | ~$45 |
| Phase 2b: H7 Confirmatory (full 2×2) | ~12,000 | ~$18 |
| Phase 2c: Strand 2 — H15 (6 library conditions) | ~18,000 | ~$27 |
| Phase 2d: Strand 3 (conditional interaction) | ~6,000 | ~$9 |
| Phase 3a: H4 N=30 Extension | ~1,200 | ~$2 |
| Phase 3b: H5 Ordering | ~3,600 | ~$5 |
| Phase 3c: H6 Diversity (exploratory) | ~6,000 | ~$9 |
| Phase 3d: H3 Two-Stage (exploratory) | ~1,200 | ~$2 |
| H7 Expansion (if triggered) | ~6,000 | ~$9 |
| **Flash Subtotal** | **~78,100-90,100** | **~$117-135** |
| Phase 4: H8 Pro Transfer (exploratory) | ~1,400-1,600 | ~$105-120 |
| **Confirmatory Total** | **~79,500-91,700** | **~$222-255** |
| Phase 5: Exploratory (H10-H14, H16, H17) | ~7,000-12,000 | ~$40-60 |
| **Grand Total** | **~86,500-103,700** | **~$262-315** |

**Contingency**: 20% buffer → **Budget ceiling: ~$380**

**Notes**:

- Phase 2d (Strand 3) only runs if Strands 1 and 2 both show significant effects
- H7 Expansion only runs if interaction or large H7 effect detected
- H3, H6, and H8 are now exploratory (moved from confirmatory)
- The majority of cost comes from Pro model testing (Phase 4) at ~10× Flash pricing
- Flash-only confirmatory testing would cost ~$117-135

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

*Document version: 2.3*
*Created: 2025-12-31*
*Updated: 2026-01-06*

**Changelog:**

- v2.3: Stranded factorial restructure — separates text elaboration (Strand 1) from library content (Strand 2); Phase 2 now has 4 sub-phases (2a-2d); H15 promoted to confirmatory with 6 library conditions (Pure, Canonical, A-D) using 1:1 HP:Emp-HN ratio; H3, H6, H8 moved to exploratory; H17 added to Phase 5 (HP:HN ratio exploration); budget updated (~$117-135 Flash, ~$222-255 total confirmatory)
- v2.2: Final review fixes — H2/H7 orthogonality in Phase 1 (exclusion guidance controlled by H7 only); corrected Pro cost estimates (~$105-120, not ~$21-24); fixed budget summary totals; updated file naming to match 10-instruction structure; fixed H5 condition count (6 new, not 9); removed stale h2-elaboration directory; corrected H12 description
- v2.1: Fixed stale E7 reference → H16 in dependency graph and Phase 5 priority list
- v2.0: Major design update — revised to 100-condition factorial (5 M/E × 4 H7 × 5 T); K=10 independent runs protocol; Phase 1 now includes verbose text construction with text-image alignment; H2 integrated into main factorial (removed Phase 3d); H5 partial cross design; H8 OFAT approach on 20-tile subset; revised budget summary (~$150-183 vs ~$187-326)
- v1.2: Added metadata tracking documentation
- v1.1: Added H6 diversity configs, H9 temperature parameter
- v1.0: Initial execution plan
