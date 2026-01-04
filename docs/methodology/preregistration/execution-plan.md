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

- [x] **Prompts**: Finalise all instruction files (2026-01-01)
  - [x] `detect_image-only.md` (baseline, also used by hardneg configs)
  - [x] `detect_text-image.md` and `detect_text-image_hardneg.md`
  - [x] `detect_text-only.md` and `detect_text-only_hardneg.md`
  - [x] `detect_*_elaborate.md` and `detect_*_elaborate_hardneg.md` (H2)
  - [ ] H6 text variants (5 semantically equivalent instructions)
  - [x] `propose_image-only.md` and `verify_image-only.md` (H3)

- [x] **Configs**: Create all JSON config files (2026-01-01)
  - [x] H1/H5/H7 baseline and ordering variants (`detect_image-only*.json`, `detect_text-image*.json`)
  - [x] H2 elaboration variants (`detect_*_elaborate*.json`)
  - [ ] H9 temperature (runtime parameter, no separate configs needed)
  - [ ] H6 diversity configs

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
│   ├── h6-diversity/
│   ├── h3-twostage/
│   │   ├── candidates.geojson        # Proposer output
│   │   ├── candidates.meta.json
│   │   ├── verified.geojson          # Verifier output
│   │   └── verified.meta.json
│   └── h2-elaboration/
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
**Estimated cost**: ~$18-30 (Flash)
**Prerequisites**: Phase 1 complete, library uploaded to OSF

### Design

Full 2×3×2×4 factorial on Gemini 3 Flash:

| Factor | Levels | Values |
|--------|--------|--------|
| Modality (M) | 2 | image-only, text+image |
| Ordering (O) | 3 | canonical-first, canonical-last, random |
| Hard negatives (H) | 2 | without, with |
| Temperature (T) | 4 | 0.0, 0.3, 0.7, 1.0 |

**Total**: 48 conditions × 5 passes × 60 holdout tiles = 14,400 API calls

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
**Estimated cost**: ~$75-120 (Flash)
**Trigger**: Always run (Tier 1 priority)

#### Design

Using best config from Phase 2 (or baseline if no clear winner):

| Pool size (N) | Thresholds tested | Passes needed |
|---------------|-------------------|---------------|
| 5 | 1, 2, 3, 4, 5 | 5 × 60 = 300 |
| 10 | 1, 2, ..., 10 | 10 × 60 = 600 |
| 30 | 1, 2, ..., 30 | 30 × 60 = 1,800 |

**Note**: N=5 data already exists from Phase 2 for the best config. Only need N=10 and N=30 fresh runs.

**New API calls**: (10 + 30) × 60 tiles = 2,400 tile-evaluations

#### Execution

1. Run N=10: 10 passes × 60 tiles = 600 API calls
   - Then aggregate at T=1,2,...,10 (no additional calls)

2. Run N=30: 30 passes × 60 tiles = 1,800 API calls

**Total new calls**: 600 + 1,800 = 2,400 API calls

#### Outputs

- [ ] Threshold sweep curves (F1, precision, recall vs T for each N)
- [ ] Optimal (N, T) recommendation
- [ ] Cost-efficiency analysis (F1 per dollar)

---

### Phase 3b: H6 Diversity Testing

**Duration**: 1 day
**Estimated cost**: ~$15-24 (Flash)
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
- Condition A: 5 runs × 5 passes × 60 tiles = 1,500 calls
- Conditions B, C, D: 1 run × 5 passes × 60 tiles × 3 = 900 calls
- **Total**: 2,400 calls

#### Outputs

- [ ] 2×2 ANOVA results
- [ ] Effect sizes for text diversity, image diversity, interaction

---

### Phase 3c: H3 Two-Stage Pipeline

**Duration**: 1 day
**Estimated cost**: ~$9-15 (Flash)
**Trigger**: Always run (confirms preliminary finding)

#### Design

Compare:
- Condition A: Single-stage detection (baseline from Phase 2)
- Condition B: Proposer → Verifier pipeline

**API calls**:
- Proposer: 5 passes × 60 tiles = 300 calls
- Verifier: ~X candidates × 60 tiles (depends on proposer output)
- Estimate: ~900-1,500 total calls

#### Outputs

- [ ] F1 comparison (single-stage vs two-stage)
- [ ] Error analysis: What does two-stage miss that single-stage catches?

---

### Phase 3d: H2 Text Elaboration

**Duration**: 0.5-1 day
**Estimated cost**: ~$9-15 (Flash)
**Trigger**: Run if Phase 2 shows modality matters (M main effect significant)

#### Design

2×2×2 factorial within text-containing conditions:

| Factor | Levels |
|--------|--------|
| Modality | text-only, text+image |
| Elaboration | brief (~200-400 words), elaborate (~700-1400 words) |
| Hard negatives | baseline, hardneg |

**Configs**: 8 total (see `planning/h2-text-elaboration-comparison.md`)
- `detect_text-only.json`, `detect_text-only_hardneg.json`
- `detect_text-only_elaborate.json`, `detect_text-only_elaborate_hardneg.json`
- `detect_text-image.json`, `detect_text-image_hardneg.json`
- `detect_text-image_elaborate.json`, `detect_text-image_elaborate_hardneg.json`

**API calls**: 8 × 5 passes × 60 tiles = 2,400 calls

#### Outputs

- [ ] 2×2×2 ANOVA (modality × elaboration × hardneg)
- [ ] F1 comparison: brief vs elaborate within each modality
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
| Phase 2: Factorial | ~14,400 | $18-30 |
| Phase 3a: H4 Voting | ~2,400 | $75-120 |
| Phase 3b: H6 Diversity | ~2,400 | $15-24 |
| Phase 3c: H3 Two-Stage | ~1,200 | $9-15 |
| Phase 3d: H2 Elaboration | ~2,400 | $9-15 |
| Phase 4: H8 Transfer | ~1,400 | $40-70 |
| **Confirmatory Total** | **~24,300** | **$167-276** |
| Phase 5: Exploratory | ~2,000-5,000 | $20-50 |
| **Grand Total** | **~26,300-29,300** | **$187-326** |

**Contingency**: 20% buffer → **Budget ceiling: ~$390**

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

*Document version: 1.2*
*Created: 2025-12-31*
*Updated: 2026-01-02 (added metadata tracking documentation)*
