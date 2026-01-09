# Execution Plan: VLM Burial Mound Detection Study

**Companion document to**: `preregistration.md`
**Purpose**: Operational sequencing for executing the preregistered experiments
**Status**: Ready for Registration

---

## Dependency Graph

```text
Phase 0: Preparation
    │
    ▼
Phase 1: Library + Text Construction ───────────────────────┐
    │                                                       │
    ▼                                                       │
Phase 2a: Strand 1 (Verbosity × Partial H5) ◄───────────────┤
    │    26 cells × K=10 runs                               │
    ▼                                                       │
Phase 2b: H5 Confirmatory (Full 3-level at Optimal M/E)     │
    │    4 cells × K=10 runs                                │
    ▼                                                       │
Phase 2c: Strand 2 (Library Size H8) ───────────────────────┤
    │    24 cells × K=10 runs                               │
    ▼                                                       │
Phase 2d: Strand 3 (Interaction, conditional)               │
    │    ~10 cells × K=10 runs                              │
    │                                                       │
    ├───────────────┬───────────────┬───────────────┐       │
    ▼               ▼               ▼               ▼       │
Phase 3a:       Phase 3b:       Phase 3c:       Phase 3d:   │
H3 Voting       H4 Ordering     H9 Diversity    H2 Two-Stage│
(N=30 extend)   (partial cross) (exploratory)   (exploratory)
    │               │               │               │       │
    └───────────────┴───────────────┴───────────────┘       │
                    │                                       │
                    ▼                                       │
            Phase 4: H6 Flash→Pro Transfer (OFAT) ◄─────────┘
                    │                                       (exploratory)
                    ▼
            Phase 5: Exploratory (H10-H14, H16, H17)
```

**Note**: The stranded design separates text elaboration (Strand 1) from library content (Strand 2). H9 is exploratory; H2 and H6 remain confirmatory.

---

## Phase 0: Preparation (Before Any API Calls)

**Duration**: 1-2 days
**Cost**: $0

### Checklist

- [x] **Prompts**: Finalise all instruction files (2026-01-01)
  - [x] `detect_image-only.md` and `detect_image-only_hardneg.md`
  - [x] `detect_brief-text.md` (no hardneg variant — text-only tested at H5=None only)
  - [x] `detect_brief-text-image.md` and `detect_brief-text-image_hardneg.md`
  - [x] `detect_verbose-text.md` (no hardneg variant — text-only tested at H5=None only)
  - [x] `detect_verbose-text-image.md` and `detect_verbose-text-image_hardneg.md`
  - [ ] H9 text variants (5 semantically equivalent instructions, constructed after Phase 2)
  - [x] `propose_image-only.md` and `verify_image-only.md` (H2)

- [x] **Configs**: Create all JSON config files (2026-01-01)
  - [x] 16 main factorial configs: 5 M/E × 3 H5 (minus 4 invalid text-only × image-H5 combos)
  - [x] Naming pattern: `detect_{modality}_{hardneg}.json`
  - [ ] H4 ordering variants (6 configs: 2 orderings × 3 M/E levels)
  - [ ] H7 temperature: runtime parameter, no separate configs needed
  - [ ] H9 diversity configs: constructed after Phase 2 optimal determined

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
│   ├── h3-voting/
│   ├── h4-ordering/
│   ├── h9-diversity/
│   └── h2-twostage/
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
**Estimated cost**: ~$1 (Flash at $0.003/call)
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

**Note on exclusion guidance**: Exclusion guidance for hard negatives (FPs) is NOT part of either brief or verbose text. Exclusion guidance is controlled by the H5 factor via `_hardneg.md` instruction variants:

- H5 = None or Images-only: No exclusion text
- H5 = Text+Images: Exclusion text added

This separation ensures H2 (text elaboration) and H5 (hard negatives) remain orthogonal factors.

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

## Phase 2: Stranded Factorial Design (H1, H2, H5, H7, H8)

**Duration**: 3-4 days
**Estimated cost**: ~$111 (Flash at $0.003/call)
**Prerequisites**: Phase 1 complete, library and text uploaded to OSF

The stranded design separates text elaboration (Strand 1) from library content (Strand 2), avoiding a full factorial cross that would conflate these factors.

---

### Phase 2a: Strand 1 — Verbosity × Partial H5 Cross

**Purpose**: Determine optimal text elaboration and hard negative settings.

**Design**: 5 M/E levels × partial H5 cross × 4 temperatures:

**Image-using modalities (3 levels)**:

| M/E | H5=None | H5=Text+Images |
|-----|---------|----------------|
| Image-only | ✓ | ✓ |
| Brief+image | ✓ | ✓ |
| Verbose+image | ✓ | ✓ |

**Text-only modalities (2 levels)**:

| M/E | H5=None | Notes |
|-----|---------|-------|
| Brief-text | ✓ | T=1.0 only (no example images) |
| Verbose-text | ✓ | T=1.0 only (no example images) |

**Note**: Text-only modalities are tested at H5=None only (they cannot use H5=Images-only or H5=Text+Images since they have no example images) and T=1.0 only (budget efficiency).

**Strand 1 totals**:

- (3 image M/E × 2 H5 × 4 T) + (2 text M/E × 1 H5 × 1 T) = 24 + 2 = **26 cells**
- 26 × K=10 × 60 tiles = **15,600 API calls** (~$47)

**Fixed parameters**: All conditions use Library A (13 examples: 4 Canon+, 2 Canon-, 2 HP, 2 HN, 3 nulls). Canonical-first ordering.

**Analysis**:

1. 2-way ANOVA: M/E × H5 (aggregating over T)
2. 1-way ANOVA on T (at optimal M/E × H5)
3. Identify optimal M/E and optimal H5 for next stage

---

### Phase 2b: H5 Confirmatory — Full 3-Level at Optimal M/E

**Purpose**: Test all 3 H5 levels at the optimal modality from Strand 1.

**Design**: Full 3-level H5 design at optimal M/E:

| H5 Level | Exclusion Text | HN Images |
|----------|----------------|-----------|
| None | No | No |
| Images-only | No | Yes (minimal labels) |
| Text+Images | Yes | Yes (detailed labels) |

**H5 Confirmatory totals**:

- 3 H5 × 4 T = **12 cells**
- 12 × K=10 × 60 = **7,200 API calls** (~$22)

**Note**: H5=None and H5=Text+Images are already tested in Strand 1 at optimal M/E. This adds H5=Images-only condition, yielding complete 3-level data.

**Expansion trigger**: Run H5 middle level (Images-only) at second-best M/E if:

- M/E × H5 interaction (p < 0.10) in Strand 1, OR
- H5 main effect > 0.08 F1 in Strand 1

**Expansion cost (if triggered)**: 1 H5 × 4 T × K=10 × 60 = **2,400 calls** (~$7)

---

### Phase 2c: Strand 2 — Library Size (H8)

**Purpose**: Determine optimal hard example library size.

**Prerequisite**: Optimal M/E and H5 from Strands 1 and 2b.

**Design**: 6 library conditions at optimal M/E and H5:

| Condition | Canon+ | Canon- | HP | HN | Nulls | Total | Hard Examples |
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
- **HN**: Empirically-derived hard negatives (FPs from Phase 1)

**H5 constraint**: Pure and Canonical run at H5=None (no empirical HNs available). Conditions A-D run at optimal H5 from Strand 1.

**Strand 2 totals**:

- 6 conditions × 4 T = **24 cells**
- 24 × K=10 × 60 = **14,400 API calls** (~$43)

**Planned contrasts**:

1. Pure → Canonical: Do legend-derived negatives help?
2. Canonical → A: Do empirical hard examples help? (confounded with H5 if optimal ≠ None)
3. A → B → C → D: Diminishing returns curve

**Confound note**: The Canonical → A contrast is confounded if Strand 1 optimal H5 ≠ None, because Canonical runs at H5=None while A runs at optimal H5. Document adjustment option in analysis.

---

### Phase 2d: Strand 3 — Interaction Check (Conditional)

**Purpose**: Check whether optimal verbosity depends on library size.

**Trigger**: Run if BOTH:

1. Strand 1 shows significant M/E effect (p < 0.05), AND
2. Strand 2 shows significant library size effect (p < 0.05)

**Design**: Test second-best M/E at 2 library sizes (optimal and one adjacent):

- 2 M/E × 2 Library × 4 T = **16 cells** (8 new cells; 8 overlap with Strands 1-2)
- ~8 new cells × K=10 × 60 = **4,800 API calls** (~$14)

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
| 1 | M/E × H5 partial ANOVA | Optimal M/E, preliminary H5 |
| 2b | H5 3-level ANOVA | Optimal H5 (confirmed) |
| 2c | Library size ANOVA + contrasts | Optimal library size |
| 3 | M/E × Library interaction | Interaction present? |

---

## Phase 3: Follow-up Experiments (Parallel)

These can run in parallel after Phase 2, depending on results.

### Phase 3a: H3 Voting Extension (N=30)

**Duration**: 0.5 days
**Estimated cost**: ~$4 (Flash at $0.003/call)
**Trigger**: Always run (Tier 1 priority)

#### Design

The K=10 runs from Phase 2 provide data for voting analysis (H3) at N=5 and N=10. Phase 3a extends to N=30 at the optimal configuration only.

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

### Phase 3b: H4 Ordering (Partial Cross)

**Duration**: 0.5 days
**Estimated cost**: ~$11 (Flash at $0.003/call)
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

**Fixed parameters**: All H4 conditions tested at optimal H5 and T from Phase 2 results.

#### Mitigation Trigger

If O × M/E interaction is detected (p < 0.10), extend to remaining 2 M/E levels (Brief-text and Verbose-text).

#### Outputs

- [ ] 3 × 3 ANOVA (ordering × M/E)
- [ ] Interaction test results
- [ ] Recommendation for operational ordering

---

### Phase 3c: H9 Diversity Testing

**Duration**: 1 day
**Estimated cost**: ~$18 (Flash at $0.003/call)
**Trigger**: Run if H3 shows voting helps (expected)

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

### Phase 3d: H2 Two-Stage Pipeline

**Duration**: 1 day
**Estimated cost**: ~$4 (Flash at $0.003/call)
**Trigger**: Always run (confirms preliminary finding)

#### Design

Compare:

- Condition A: Single-stage detection (optimal from Phase 2)
- Condition B: Proposer → Verifier pipeline

**API calls**:

- Proposer: K=10 runs × 60 tiles = 600 calls
- Verifier: ~X candidates × 60 tiles (depends on proposer output)
- Estimate: ~600-1,200 total calls

**Stopping rule**: Two-stage must exceed single-stage by ≥0.05 F1 to justify ~2× cost overhead (see preregistration H2).

#### Outputs

- [ ] F1 comparison (single-stage vs two-stage)
- [ ] Error analysis: What does two-stage miss that single-stage catches?

---

## Phase 4: H6 Flash→Pro Transfer (OFAT)

**Duration**: 2-3 days
**Estimated cost**: ~$42-48 (Pro at ~$0.03/call, needs verification)
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
| H5 | (from Phase 2) | 1-2 adjacent levels |
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
| 4a: Baseline | 200 | ~$6 |
| 4b: OFAT | ~1,200 | ~$36 |
| 4c: Voting | (from 4a-4b) | — |
| 4d: Refinement | 0-200 | $0-6 |
| **Total** | **~1,400-1,600** | **~$42-48** |

**Note**: Pro pricing assumed ~10× Flash (~$0.03/call vs ~$0.003/call). Actual Pro pricing to be verified at experiment start. If Pro shows dramatic superiority warranting full optimisation, budget for extended Pro testing (~$50-80 additional).

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

1. **H14 (cross-model consistency)**: Most important for generalisability
   - Test Flash-optimal configuration on Claude 4.5 Sonnet and GPT-5.2 Thinking
   - OFAT sensitivity testing per factor (same protocol as H6)
   - ~$40-60 (depends on provider pricing)

2. **H15 (cross-model voting)**: Novel contribution
   - 6-pass voting: 6×Flash vs 6×Sonnet vs 6×GPT vs 2×each
   - ~$15-25

3. **H10 (training pool size)**: Library quality assessment
   - Test libraries constructed from larger training pools
   - ~$5-10

4. **H12 (HP:HN ratio)**: Ratio exploration
   - At optimal library size from H8 (A-D only), compare HP:HN ratios at fixed total count
   - 3 ratios: 1:3 (HN-heavy), 1:1 (baseline), 3:1 (HP-heavy)
   - Trigger: Run if H8 shows library size matters AND budget permits
   - ~$9 incremental (R2 already tested in H8)

5. **H11, H13**: Lower priority, if budget allows

---

## Budget Summary

**Pricing basis**: Gemini 3 Flash at $0.003/call ($0.50/1M input + $3/1M output for ~5K input + 200 output tokens). Pro estimated at ~10× Flash ($0.03/call; needs verification).

| Phase | API Calls | Estimated Cost |
|-------|-----------|----------------|
| Phase 1: Library + Text | ~100 | ~$1 |
| Phase 2a: Strand 1 (Verbosity × partial H5) | ~15,600 | ~$47 |
| Phase 2b: H5 Confirmatory (full 3-level) | ~7,200 | ~$22 |
| Phase 2c: Strand 2 — H8 (6 library conditions) | ~14,400 | ~$43 |
| Phase 2d: Strand 3 (conditional interaction) | ~4,800 | ~$14 |
| Phase 3a: H3 N=30 Extension | ~1,200 | ~$4 |
| Phase 3b: H4 Ordering | ~3,600 | ~$11 |
| Phase 3c: H9 Diversity (exploratory) | ~6,000 | ~$18 |
| Phase 3d: H2 Two-Stage (exploratory) | ~1,200 | ~$4 |
| H5 Expansion (if triggered) | ~2,400 | ~$7 |
| **Flash Subtotal** | **~56,500** | **~$171** |
| Phase 4: H6 Pro Transfer (exploratory) | ~1,400-1,600 | ~$42-48 |
| **Confirmatory Total** | **~58,100** | **~$213-219** |
| Phase 5: Exploratory (H10-H15) | ~7,000-12,000 | ~$40-60 |
| **Grand Total** | **~65,100-70,100** | **~$253-279** |

**Soft budget limit**: $250 (triggers review, not hard cap)
**Contingency**: 20% buffer → **Budget ceiling: ~$335**

**Notes**:

- Phase 2d (Strand 3) only runs if Strands 1 and 2 both show significant effects
- H5 Expansion only runs if interaction or large H5 effect detected
- H9 is exploratory; H2 and H6 remain confirmatory
- Flash-only confirmatory testing would cost ~$171
- Pro pricing needs verification at experiment start

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
| Budget reaches $250 | Pause, review and prioritise remaining experiments |
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

*Document version: 2.7*
*Created: 2025-12-31*
*Updated: 2026-01-09*

**Changelog:**

- v2.7: Updated pricing based on verified Gemini 3 Flash rates ($0.50/1M input, $3/1M output → $0.003/call); all Flash cost estimates doubled; Pro estimate revised to ~$0.03/call (needs verification); soft budget limit $250; budget ceiling ~$335
- v2.6: Fixed text-only modality constraints in Strand 1 — text-only tested at H5=None only and T=1.0 only per preregistration.md; corrected Strand 1 calculation from 40 cells to 26 cells (24 image + 2 text); fixed API call count from 24,000 to 15,600; updated prompts checklist to note text-only has no hardneg variants; corrected Strand 2 cell count in dependency graph from 30 to 24
- v2.5: Consistency fixes with preregistration.md v4.2 — corrected H8 label (was H15); fixed H2/H6 status (confirmatory, not exploratory); corrected cell counts (Strand 1: 26, H5 Confirmatory: 4); fixed H10 description (training pool size, not fine-to-coarse); recalculated budget totals
- v2.4: Synchronised hypothesis numbering with preregistration.md v4.2 — H5=hard negatives (3 levels), H7=temperature (4 levels), H4=ordering, H3=voting, H2=two-stage, H6=Flash→Pro, H8=library size, H9=diversity; updated factorial to 60 conditions (5 M/E × 3 H5 × 4 T); revised budget (~$94-101 Flash, ~$199-221 confirmatory); status updated to Ready for Registration
- v2.3: Stranded factorial restructure — separates text elaboration (Strand 1) from library content (Strand 2); Phase 2 now has 4 sub-phases (2a-2d); library size promoted to confirmatory with 6 library conditions (Pure, Canonical, A-D) using 1:1 HP:HN ratio; two-stage, diversity, and Flash→Pro moved to exploratory; HP:HN ratio added to Phase 5 exploration; budget updated
- v2.2: Final review fixes — H2/hard negatives orthogonality in Phase 1 (exclusion guidance controlled by hard negatives only); corrected Pro cost estimates (~$105-120); fixed budget summary totals; updated file naming to match 10-instruction structure; fixed ordering condition count (6 new, not 9); removed stale elaboration directory
- v2.1: Fixed stale reference in dependency graph and Phase 5 priority list
- v2.0: Major design update — revised to 100-condition factorial; K=10 independent runs protocol; Phase 1 now includes verbose text construction with text-image alignment; elaboration integrated into main factorial; ordering partial cross design; Flash→Pro OFAT approach on 20-tile subset; revised budget summary
- v1.2: Added metadata tracking documentation
- v1.1: Added diversity configs, temperature parameter
- v1.0: Initial execution plan
