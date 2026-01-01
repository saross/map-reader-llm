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
Phase 1: Library Construction ──────────────────────────────┐
    │                                                       │
    ▼                                                       │
Phase 2: Core Factorial (H1, H5, H7, H9) ◄──────────────────┤
    │                                                       │
    ├───────────────┬───────────────┬───────────────┐       │
    ▼               ▼               ▼               ▼       │
Phase 3a:       Phase 3b:       Phase 3c:       Phase 3d:   │
H4 Voting       H6 Diversity    H3 Two-Stage    H2 Elaboration
    │               │               │               │       │
    └───────────────┴───────────────┴───────────────┘       │
                    │                                       │
                    ▼                                       │
            Phase 4: H8 Flash→Pro Transfer ◄────────────────┘
                    │
                    ▼
            Phase 5: Exploratory (H10-H15, E7)
```

---

## Phase 0: Preparation (Before Any API Calls)

**Duration**: 1-2 days
**Cost**: $0

### Checklist

- [ ] **Prompts**: Finalise all instruction files
  - [ ] `detect_image-only.md` (baseline)
  - [ ] `detect_image-only-hardneg.md` (H7)
  - [ ] `detect_text-image.md` and `-hardneg` variant
  - [ ] `detect_text-only.md` and `-hardneg` variant
  - [ ] H6 text variants (5 semantically equivalent instructions)
  - [ ] `propose_image-only.md` and `verify_image-only.md` (H3)

- [ ] **Configs**: Create all JSON config files
  - [ ] H5 ordering variants (canonical-first, canonical-last, random ×3)
  - [ ] H9 temperature variants (T=0.0, 0.3, 0.7, 1.0)
  - [ ] H6 diversity configs

- [ ] **Scripts**: Verify/create analysis code
  - [ ] Batch detection script handles all config variants
  - [ ] F1 evaluation with Hungarian matching
  - [ ] Voting aggregation at multiple thresholds
  - [ ] Results collation and statistical tests

- [ ] **Data management**:
  - [ ] Create output directory structure (see below)
  - [ ] Set up results tracking spreadsheet
  - [ ] Document API pricing at experiment start

### Output Directory Structure

```text
outputs/
├── phase1-library/
│   ├── baseline-runs/
│   └── hard-example-analysis/
├── phase2-factorial/
│   ├── raw-responses/
│   └── aggregated/
├── phase3-followup/
│   ├── h4-voting/
│   ├── h6-diversity/
│   ├── h3-twostage/
│   └── h2-elaboration/
├── phase4-transfer/
│   └── pro-replication/
└── phase5-exploratory/
```

---

## Phase 1: Library Construction

**Duration**: 0.5 days
**Estimated cost**: ~$1-2 (Flash)
**Prerequisite for**: All subsequent phases

### Purpose

Run baseline detection on training tiles to identify hard examples for the few-shot library.

### Procedure

1. **Run baseline** (image-only, 4 canonical + 3 null, no hard examples)
   - 5 passes × 20 training tiles = 100 API calls
   - Use T=1.0 (vendor recommended)

2. **Analyse results**
   - Identify False Negatives: ground truth mounds missed in ≥3/5 passes
   - Identify False Positives: detections in ≥3/5 passes with no matching ground truth
   - Rank by frequency

3. **Select hard examples**
   - Hard positives: Top 4 FNs by frequency
   - Hard negatives: Top 3 FPs by frequency
   - Document selection with crops and rationale

4. **Outputs**
   - [ ] `inputs/few-shot-library/hard-positives/` (4 images)
   - [ ] `inputs/few-shot-library/hard-negatives/` (3 images)
   - [ ] `inputs/few-shot-library/library-manifest.json` (metadata)
   - [ ] Upload library to OSF before Phase 2

### Decision Point

If <4 distinct FNs or <3 distinct FPs are found:
- Option A: Proceed with smaller hard example set (document)
- Option B: Expand training pool (requires re-randomisation)

---

## Phase 2: Core Factorial (H1, H5, H7, H9)

**Duration**: 1-2 days
**Estimated cost**: ~$6-10 (Flash)
**Prerequisites**: Phase 1 complete, library uploaded to OSF

### Design

Full 2×3×2×4 factorial on Gemini 3 Flash:

| Factor | Levels | Values |
|--------|--------|--------|
| Modality (M) | 2 | image-only, text+image |
| Ordering (O) | 3 | canonical-first, canonical-last, random |
| Hard negatives (H) | 2 | without, with |
| Temperature (T) | 4 | 0.0, 0.3, 0.7, 1.0 |

**Total**: 48 conditions × 5 passes × 20 holdout tiles = 4,800 API calls

### Execution Order

Run conditions in randomised order to distribute any temporal effects (API performance variation, rate limiting).

```python
# Pseudocode for execution
conditions = generate_all_48_conditions()
random.seed(20251231)  # Document seed
random.shuffle(conditions)

for condition in conditions:
    for tile in holdout_tiles:
        for pass_num in range(5):
            run_detection(condition, tile, pass_num)
            save_response()
    # Checkpoint after each condition
    save_checkpoint(condition)
```

### Checkpoints

- After every 10 conditions (~1,000 calls): Spot-check parsing success rate
- If parsing failure rate >5%: Pause and investigate
- If API errors >10%: Pause and check rate limits

### Outputs

- [ ] Raw JSON responses: `outputs/phase2-factorial/raw-responses/{condition_id}/{tile_id}_pass{n}.json`
- [ ] Aggregated results: `outputs/phase2-factorial/aggregated/factorial-results.csv`
- [ ] Preliminary ANOVA: `outputs/phase2-factorial/factorial-anova.md`

### Analysis (Immediate)

1. Compute F1 for each condition (2-of-5 voting as default threshold)
2. Run 4-way ANOVA: M × O × H × T
3. Identify significant main effects and interactions
4. **Decision**: Which factors show significant effects? These inform Phase 3 priorities.

---

## Phase 3: Follow-up Experiments (Parallel)

These can run in parallel after Phase 2, depending on results.

### Phase 3a: H4 Voting Grid Search

**Duration**: 2-3 days
**Estimated cost**: ~$25-40 (Flash)
**Trigger**: Always run (Tier 1 priority)

#### Design

Using best config from Phase 2 (or baseline if no clear winner):

| Pool size (N) | Thresholds tested | Passes needed |
|---------------|-------------------|---------------|
| 5 | 1, 2, 3, 4, 5 | 5 × 20 = 100 |
| 10 | 1, 2, ..., 10 | 10 × 20 = 200 |
| 30 | 1, 2, ..., 30 | 30 × 20 = 600 |

**Note**: N=5 data already exists from Phase 2 for the best config. Only need N=10 and N=30 fresh runs.

**New API calls**: (10 + 30) × 20 tiles = 800 tile-evaluations = 800 × avg_passes = ~16,000 calls

#### Execution

1. Run N=10: 10 passes × 20 tiles = 200 API calls per tile... wait, that's 10 passes total, evaluated at all 10 thresholds
   - Actually: 10 passes × 20 tiles = 200 API calls
   - Then aggregate at T=1,2,...,10 (no additional calls)

2. Run N=30: 30 passes × 20 tiles = 600 API calls

**Total new calls**: 200 + 600 = 800 API calls (much less than I initially calculated!)

#### Outputs

- [ ] Threshold sweep curves (F1, precision, recall vs T for each N)
- [ ] Optimal (N, T) recommendation
- [ ] Cost-efficiency analysis (F1 per dollar)

---

### Phase 3b: H6 Diversity Testing

**Duration**: 1 day
**Estimated cost**: ~$5-8 (Flash)
**Trigger**: Run if H4 shows voting helps (expected)

#### Design

2×2 factorial:

| Condition | Text | Images | Description |
|-----------|------|--------|-------------|
| A | Fixed | Fixed | Baseline (run 5× with different seeds, average) |
| B | Varied | Fixed | 5 prompt variants, same images |
| C | Fixed | Varied | Same prompt, resampled hard examples per pass |
| D | Varied | Varied | Both mechanisms |

**API calls**:
- Condition A: 5 runs × 5 passes × 20 tiles = 500 calls
- Conditions B, C, D: 1 run × 5 passes × 20 tiles × 3 = 300 calls
- **Total**: 800 calls

#### Outputs

- [ ] 2×2 ANOVA results
- [ ] Effect sizes for text diversity, image diversity, interaction

---

### Phase 3c: H3 Two-Stage Pipeline

**Duration**: 1 day
**Estimated cost**: ~$3-5 (Flash)
**Trigger**: Always run (confirms preliminary finding)

#### Design

Compare:
- Condition A: Single-stage detection (baseline from Phase 2)
- Condition B: Proposer → Verifier pipeline

**API calls**:
- Proposer: 5 passes × 20 tiles = 100 calls
- Verifier: ~X candidates × 20 tiles (depends on proposer output)
- Estimate: ~300-500 total calls

#### Outputs

- [ ] F1 comparison (single-stage vs two-stage)
- [ ] Error analysis: What does two-stage miss that single-stage catches?

---

### Phase 3d: H2 Text Elaboration

**Duration**: 0.5 days
**Estimated cost**: ~$2-3 (Flash)
**Trigger**: Run if Phase 2 shows modality matters (M main effect significant)

#### Design

Compare within text+image modality:
- Condition A: Minimal text ("Detect burial mound symbols")
- Condition B: Elaborate text (detailed criteria, explicit rules)

**API calls**: 2 × 5 passes × 20 tiles = 200 calls

#### Outputs

- [ ] F1 comparison
- [ ] Qualitative analysis of error patterns

---

## Phase 4: H8 Flash→Pro Transfer

**Duration**: 2-3 days
**Estimated cost**: ~$50-100 (Pro is ~10× Flash cost)
**Prerequisites**: Phase 2 and Phase 3a complete

### Design

Replicate key findings on Gemini 3 Pro using adaptive testing framework (see preregistration Section H8).

#### Primary Analysis (~14 conditions)

| Hypothesis | Conditions on Pro |
|------------|-------------------|
| H4 (voting) | Single-pass, Flash-optimal, Unanimity |
| H5 (ordering) | All 3 conditions |
| H6 (diversity) | Full 2×2 |
| H7 (hard negatives) | Full 2×2 |

**API calls**: ~14 conditions × 5 passes × 20 tiles = 1,400 calls
**Estimated cost**: ~$40-70

#### Trigger Conditions

Monitor for:
- Effect reversal (sign change)
- Significant interaction (p < 0.10)
- Large attenuation (Cohen's d ratio < 0.50)
- Rank reversal

If triggered → Secondary analysis (bracketing, expanded testing)

### Outputs

- [ ] Transfer success rate (% effects replicating)
- [ ] Model-specific recommendations (if needed)

---

## Phase 5: Exploratory Hypotheses

**Duration**: Variable
**Estimated cost**: ~$20-50 (budget permitting)
**Prerequisites**: Phases 2-4 complete

### Priority Order

1. **H12 (cross-model consistency)**: Most important for generalisability
   - Replicate H4, H5, H7 on Claude 4.5 Sonnet and GPT-5.2
   - ~$30-50

2. **H13 (cross-model voting)**: Novel contribution
   - 6-pass voting: 6×Flash vs 6×Sonnet vs 6×GPT vs 2×each
   - ~$15-25

3. **H10 (fine-to-coarse)**: Novel architecture
   - Context-expanded re-query for uncertain detections
   - ~$5-10

4. **H11, H14, H15, E7**: Lower priority, if budget allows

---

## Budget Summary

| Phase | API Calls | Estimated Cost |
|-------|-----------|----------------|
| Phase 1: Library | ~100 | $1-2 |
| Phase 2: Factorial | ~4,800 | $6-10 |
| Phase 3a: H4 Voting | ~800 | $3-5 |
| Phase 3b: H6 Diversity | ~800 | $5-8 |
| Phase 3c: H3 Two-Stage | ~400 | $3-5 |
| Phase 3d: H2 Elaboration | ~200 | $2-3 |
| Phase 4: H8 Transfer | ~1,400 | $40-70 |
| **Confirmatory Total** | **~8,500** | **$60-103** |
| Phase 5: Exploratory | ~2,000-5,000 | $20-50 |
| **Grand Total** | **~10,500-13,500** | **$80-153** |

**Contingency**: 20% buffer → **Budget ceiling: ~$185**

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
- [ ] Aggregated results in CSV format
- [ ] Analysis scripts committed to repository
- [ ] Few-shot library uploaded to OSF
- [ ] Statistical analysis complete with FDR correction
- [ ] Effect sizes and confidence intervals computed
- [ ] Figures: threshold curves, factorial interaction plots
- [ ] Deviations from preregistration documented

---

*Document version: 1.0*
*Created: 2025-12-31*
