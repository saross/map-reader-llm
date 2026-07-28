# Execution Plan: VLM Burial Mound Detection Study

> **NOT PART OF THE OSF LODGEMENT.** The registration comprises exactly three
> documents, all in `osf/` (`osf/README.md:3,9-11`); this file is not one of
> them. It is a working document: pre-lodgement content here fed into writing
> the registration but does not license a "the preregistration says" claim,
> and post-lodgement content is operational, not registered. Cite
> `osf/preregistration.md` for registered content. Banner added 2026-07-28
> (D17 audit, structural fix).

**Companion document to**: `preregistration.md`
**Purpose**: Operational sequencing for executing the preregistered experiments
**Status**: Ready for Registration
**Publication status**: Internal operational document (not published with preregistration)

> **Note**: This document contains detailed cost estimates, budget limits, and operational
> triggers that are kept internal for planning purposes. The public preregistration
> (`preregistration.md`) includes only summary cost information.

---

## Dependency Graph

```text
Phase 0: Preparation
    │
    ▼
Phase 1: Library + Text Construction
    │
    ▼
Phase 2a: H1 M/E Level (5 cells)
    │    ↓ optimal M/E
    ▼
Phase 2b: H7 Temperature (5 cells)
    │    ↓ optimal T
    ▼
Phase 2c: H8 Library Composition (7 cells)
    │    ↓ optimal library
    ▼
Phase 2d: H5 Negative Text Treatment (6 cells)
    │    ↓ optimal text treatment
    ▼
Phase 2e: H4 Ordering (3 cells)
    │    ↓ if significant
    └── [H4b: HP/HN ordering - 2 cells, triggered exploratory]
    │
    ├───────────────┬───────────────┬───────────────┐
    ▼               ▼               ▼               ▼
Phase 3a:       Phase 3b:       Phase 3c:       Phase 3d:
H3 Voting       H9 Diversity    H2 Two-Stage    Triggered
(N=30 extend)   (exploratory)   (exploratory)   Exploratory
    │               │               │               │
    └───────────────┴───────────────┴───────────────┘
                    │
                    ▼
            Phase 4: H6 Flash→Pro Transfer (OFAT)
                    │                           (exploratory)
                    ▼
            Phase 5: Exploratory (H10-H15)
```

**Note**: The sequential OFAT design tests one factor at a time, carrying optimal parameters forward. This reduces budget from ~54 cells to 26 cells while ensuring each hypothesis runs at truly optimal parameters.

---

## Phase 0: Preparation (Before Any API Calls)

**Duration**: 1-2 days
**Cost**: $0

### Checklist

- [x] **Prompts**: Finalise all instruction files (2026-01-01)
  - [x] `detect_image-only.md` (base M/E)
  - [x] `detect_brief-text.md` (text-only)
  - [x] `detect_brief-text-image.md` (text+image)
  - [x] `detect_verbose-text.md` (text-only)
  - [x] `detect_verbose-text-image.md` (base for H5)
  - [x] H5 variants (_terse, _verbose) at 3 image-using M/E levels (2026-01-14):
    - [x] `detect_image-only_{terse,verbose}.md` (2 files)
    - [x] `detect_brief-text-image_{terse,verbose}.md` (2 files)
    - [x] `detect_verbose-text-image_{terse,verbose}.md` (2 files)
  - [ ] H9 text variants (5 semantically equivalent instructions, constructed after Phase 2)
  - [x] `propose_brief.md` and `verify_brief.md` (H2)

- [x] **Configs**: Create all JSON config files (2026-01-01)
  - [x] 5 M/E configs: `detect_{modality}.json`
  - [x] 6 H5 variant configs (_terse, _verbose) at 3 image-using M/E levels: `detect_{modality}_{terse,verbose}.json` (2026-01-14)
  - [ ] 7 H8 library configs: `library_{composition}.json`
  - [ ] H4 ordering variants: 2 additional orderings at optimal M/E
  - [ ] H7 temperature: runtime parameter, no separate configs needed
  - [ ] H9 diversity configs: constructed after Phase 2 optimal determined

- [x] **Scripts**: Verify/create analysis code (2026-01-02)
  - [x] Batch detection script handles all config variants
  - [x] Comprehensive metadata tracking (`lib_llm_metadata.py`)
  - [ ] F1 evaluation with Hungarian matching
  - [ ] Voting aggregation at multiple thresholds
  - [ ] Results collation and statistical tests

- [x] **Calibration pilots** (2026-01-15):
  - [x] Thinking level calibration complete — minimal achieves equivalent F1 to high at 1/3 latency (see §8.9)
  - [x] All Gemini configs set to `thinking_level: minimal`

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

See `docs/pipelines.md` for full schema documentation.

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
- Hard negatives: Top M FPs (target M=4)

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

**Note on exclusion guidance**: Exclusion guidance for hard negatives (FPs) is NOT part of either brief or verbose text in H1. Exclusion guidance is controlled by the H5 factor via separate instruction variants:

- H5=Minimal: Hard negative images with "Negative" label only (no exclusion text)
- H5=Terse: Hard negative images with brief exclusion guidance (1-2 sentences)
- H5=Verbose: Hard negative images with detailed exclusion explanations

This separation ensures H1 (M/E level, positive guidance) and H5 (negative text treatment) remain orthogonal factors.

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

## Phase 2: Sequential Hypothesis Testing (H1, H7, H8, H5, H4)

**Duration**: 2-3 days
**Estimated cost**: ~$57 confirmatory (26 cells at ~$2.20/cell)
**Prerequisites**: Phase 1 complete, library and text uploaded to OSF

The sequential OFAT design tests one factor at a time, carrying optimal parameters forward. This reduces budget from ~54 cells to 26 cells while ensuring each hypothesis runs at truly optimal parameters.

---

### Phase 2a: H1 — Modality/Elaboration Level

**Purpose**: Determine optimal text modality and elaboration level.

**Design**: 5 M/E levels at T=1.0 (default), Scale-8 library, canonical-first ordering:

| M/E Level | Description |
| --------- | ----------- |
| Image-only | No text guidance |
| Brief-text+image | Concise text + images |
| Verbose-text+image | Detailed text + images |
| Brief-text-only | Text-only (no images) |
| Verbose-text-only | Detailed text (no images) |

**Phase 2a totals**:

- 5 M/E levels = **5 cells**
- 5 × K=10 × 60 tiles = **3,000 API calls** (~$11)

**Fixed parameters**: T=1.0, Scale-8 library (17 examples), canonical-first ordering.

**Analysis**: Pairwise bootstrap comparisons across 5 M/E levels (95% CIs, FDR-corrected). Identify optimal M/E for subsequent phases.

---

### Phase 2b: H7 — Temperature

**Purpose**: Determine optimal temperature setting.

**Prerequisite**: Optimal M/E from Phase 2a.

**Design**: 5 temperature levels at optimal M/E:

| Temperature | Rationale |
| ----------- | --------- |
| 0.0 | Minimum (deterministic) |
| 0.3 | Low variance (evidence for visual detection) |
| 0.7 | Moderate variance |
| 1.0 | Vendor default |
| 1.3 | Above default |

**Phase 2b totals**:

- 5 T levels = **5 cells**
- 5 × K=10 × 60 = **3,000 API calls** (~$11)

**Fixed parameters**: Optimal M/E from Phase 2a, Scale-8 library, canonical-first ordering.

**Analysis**: Pairwise bootstrap comparisons across 5 T levels (95% CIs, FDR-corrected). Planned contrasts: T=1.0 vs each other level.

---

### Phase 2c: H8 — Library Composition and Scaling

**Purpose**: Determine optimal library composition and size.

**Prerequisite**: Optimal M/E and T from Phases 2a-2b.

**Design**: 7 library conditions:

| ID | Condition | Canon+ | Canon- | HP | HN | Nulls | Total |
| -- | --------- | ------ | ------ | -- | -- | ----- | ----- |
| 1 | Pure Positive Canon | 4 | 0 | 0 | 0 | 3 | 7 |
| 2 | Canonical | 4 | 2 | 0 | 0 | 3 | 9 |
| 3 | +HP | 4 | 2 | 4 | 0 | 3 | 13 |
| 4 | Scale-4 | 4 | 2 | 2 | 2 | 3 | 13 |
| 5 | Scale-8 | 4 | 2 | 4 | 4 | 3 | 17 |
| 6 | Scale-16 | 4 | 2 | 8 | 8 | 3 | 25 |
| 7 | Scale-32 | 4 | 2 | 16 | 16 | 3 | 41 |

**Phase 2c totals**:

- 7 conditions = **7 cells**
- 7 × K=10 × 60 = **4,200 API calls** (~$15)

**Fixed parameters**: Optimal M/E and T, canonical-first ordering.

**Planned contrasts**:

- Sequential addition: C1 (Canon-), C2 (HP), C3 (HN)
- Scaling: S1 (4→8), S2 (8→16), S3 (16→32)
- Bonus: B1 (+HP vs Scale-4)

**Key question answered**: "Do negatives help?" is answered by contrast C3 (+HP → Scale-8).

---

### Phase 2d: H5 — Negative Text Treatment

**Purpose**: Determine optimal text treatment for negative examples across all image-using M/E levels.

**Prerequisite**: Optimal T and library composition from Phases 2a-2c.

**Design**: 3 H5 levels × 3 image-using M/E levels (factorial):

| H5 Level | Exclusion Text | Description |
| -------- | -------------- | ----------- |
| Minimal | "Negative" label only | Images speak for themselves |
| Terse | Brief guidance | 1-2 sentences: "Do not detect triangulation points..." |
| Verbose | Detailed guidance | Full explanation of why each is not a mound |

| M/E Level | Description |
| --------- | ----------- |
| Image-only | No text guidance |
| Brief-text+image | Concise text + images |
| Verbose-text+image | Detailed text + images |

**Phase 2d totals**:

- 3 M/E × 3 H5 = **9 cells** total
- 3 cells overlap with H1 baseline (each M/E at H5=Minimal)
- Net new: **6 cells**
- 6 × K=10 × 60 = **3,600 API calls** (~$13)

**Fixed parameters**: Optimal T and library from previous phases.

**Analysis**: Bootstrap interaction test (3 M/E × 3 H5, difference-of-differences with 95% CI). Test H5 main effect and M/E × H5 interaction. Planned contrasts: Minimal vs Terse; Terse vs Verbose (pooled across M/E levels).

---

### Phase 2e: H4 — Example Ordering

**Purpose**: Determine optimal example ordering.

**Prerequisite**: All optimal parameters from Phases 2a-2d.

**Design**: 4 ordering conditions at optimal M/E only (see Decision 18, E29, E30):

| Condition | Example Order | Notes |
| --------- | ------------- | ----- |
| Config-default | `[C+, HP, C−, null]` | JSON config-file order; baseline reused from Phase 2c via symlinks |
| Canonical-first | `[C+, C−, HP, null]` | True canonical grouping (E29 fix) |
| Canonical-last | `[HP, null, C+, C−]` | Canonical examples in final positions |
| Random | Seeded shuffle per run | Per-run seed from `random_seed_base` |

**Phase 2e totals**:

- 4 orderings = **4 cells** (1 reused, 3 new)
- Net new: 3 × K=10 × 60 = **1,800 API calls** (~$7)
- Total units: 4 × K=10 = 40 (10 config-default pre-checkpointed)

**Fixed parameters**: Optimal M/E (brief-text-image), T (0.0), library (plus-hp), and H5 (minimal) from previous phases. Image-using track only — text-only track cannot test ordering (no in-context examples sent).

**Analysis**: Pairwise bootstrap comparisons across 4 orderings (95% CIs, FDR-corrected). Planned contrasts: Canonical-first vs Canonical-last; Config-default vs Canonical-first.

**Triggered exploratory (H4b)**: If H4 significant (p < 0.05), test HP-first vs HN-first ordering within the hard block (+2 cells).

---

### Evaluation Protocol (All Phases)

Each condition is evaluated using K=10 independent single-pass runs (see preregistration Section 3.8):

- Each run makes 1 API call per tile (single-pass; voting is itself under test in H3)
- Single-pass F1 is the primary output per run
- Results characterised statistically (mean F1 across 10 runs, SD, 95% CI)
- Post-hoc voting computed from the same runs (N=5 from runs 1-5 or 6-10; N=10 from all runs) without additional API calls
- No within-run consensus voting during main effect testing

### Execution Order

Run conditions in randomised order within each phase to distribute temporal effects. Between phases, analyse results to determine optimal parameters before proceeding.

```python
# Pseudocode for sequential phase execution
def run_phase(phase_conditions, seed):
    random.seed(seed)
    random.shuffle(phase_conditions)
    for condition in phase_conditions:
        for tile in holdout_tiles:
            for run_num in range(10):  # K=10 independent runs
                run_detection(condition, tile, run_num)
                save_response()
        save_checkpoint(condition)

# Execute phases sequentially with analysis between each
run_phase(h1_conditions, seed=20260104)
optimal_me = analyse_h1()  # Determine optimal M/E

run_phase(h7_conditions, seed=20260105)
optimal_temp = analyse_h7()  # Determine optimal temperature

run_phase(h8_conditions, seed=20260106)
optimal_library = analyse_h8()  # Determine optimal library composition

run_phase(h5_conditions, seed=20260107)
optimal_text = analyse_h5()  # Determine optimal negative text treatment

run_phase(h4_conditions, seed=20260108)
optimal_ordering = analyse_h4()  # Determine optimal ordering

# Triggered exploratory
if h4_significant():
    run_phase(h4b_conditions, seed=20260109)  # HP/HN ordering
```

### Checkpoints

- After each phase (~600-4,200 calls): Spot-check parsing success rate
- If parsing failure rate >5%: Pause and investigate
- If API errors >10%: Pause and check rate limits

### Outputs

- [ ] Raw JSON responses: `outputs/phase2-sequential/raw-responses/{hypothesis}/{condition_id}/{tile_id}_run{n}.json`
- [ ] Aggregated results: `outputs/phase2-sequential/aggregated/{hypothesis}-results.csv`
- [ ] Phase analyses: `outputs/phase2-sequential/{hypothesis}-analysis.md`
- [ ] Final optimal configuration: `outputs/phase2-sequential/optimal-config.json`

### Analysis Summary

| Phase | Primary Analysis | Key Output |
|-------|------------------|------------|
| 2a (H1) | Bootstrap pairwise (5 M/E levels) | Optimal M/E |
| 2b (H7) | Bootstrap pairwise (5 temperatures) | Optimal temperature |
| 2c (H8) | Bootstrap pairwise + planned contrasts | Optimal library composition |
| 2d (H5) | Bootstrap interaction (3 M/E × 3 H5) | Optimal negative text treatment |
| 2e (H4) | Bootstrap pairwise (4 orderings) | Optimal ordering |

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

### Phase 3b: (Absorbed into Phase 2e)

**Note**: H4 ordering testing has been simplified and moved to Phase 2e. The original partial factorial design (3 orderings × 3 M/E levels = 9 cells) has been replaced with a single M/E level (optimal from H1, 3 cells). This change:

- Removes speculative O × M/E interaction testing (no strong prior support)
- Saves 6 cells (~$18)
- Focuses H4 on the primary question: does ordering matter?

If H4 shows a strong main effect and interaction is suspected, OFAT sensitivity testing at a contrasting M/E level can be conducted as exploratory follow-up (see H4b in preregistration).

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

- [ ] 2×2 bootstrap comparison results
- [ ] Effect sizes for text diversity, image diversity, interaction

---

### Phase 3d: H2 Two-Stage Pipeline

**Duration**: 1 day
**Estimated cost**: ~$4 (Flash at $0.003/call)
**Trigger**: Always run (confirms preliminary finding)

**Prerequisites**:

- Phase 2a (H1) complete → optimal M/E level known
- Phase 2b (H7) complete → optimal temperature known
- Phase 2c (H8) complete → optimal library composition known
- Phase 2d (H5) complete → optimal negative text treatment known

**Configuration**:

- Uses optimal M/E level from Phase 2a (H1)
- Uses optimal temperature from Phase 2b (H7)
- Uses optimal library from Phase 2c (H8)
- Uses optimal negative text from Phase 2d (H5)

**Config finalisation**: Before H2 testing begins (after Phase 2e completes):

1. Update both configs with H7-optimal temperature
2. Update both configs with H8-optimal library composition
3. Update both configs with H1-optimal M/E level instruction file
4. Commit finalised configs with version tag (e.g., `h2-final-20260125`)
5. Run H2 experiments with finalised configs

#### Design

Compare:

- Condition A: Single-stage detection (optimal from Phase 2)
- Condition B: Proposer → Verifier pipeline

**Protocol**: Each of the K=10 runs is independent (one proposer pass → one verifier pass). The verifier returns raw `mound_probability` scores used directly for evaluation — no binary thresholding or voting within the verification step.

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
   - At optimal library size from H8, compare HP:HN ratios at fixed total count
   - 3 ratios: 1:3 (HN-heavy), 1:1 (baseline), 3:1 (HP-heavy)
   - Trigger: Run if H8 shows library composition matters AND budget permits
   - ~$9 incremental (1:1 ratio already tested in H8 scaling conditions)

5. **H11, H13**: Lower priority, if budget allows

---

## Budget Summary

**Pricing basis**: Gemini 3 Flash at ~$0.003/call ($0.50/1M input + $3/1M output for ~5K input + 200 output tokens). Per-cell cost varies with library size: ~$2/cell for Scale-8 (17 examples), ~$4/cell for Scale-32 (41 examples). Pro estimated at ~10× Flash (~$0.03/call; needs verification).

| Phase | Cells | API Calls | Estimated Cost |
|-------|-------|-----------|----------------|
| Phase 1: Library + Text | — | ~100 | ~$1 |
| Phase 2a: H1 — M/E Level | 5 | 15,000 | ~$55 |
| Phase 2b: H7 — Temperature | 5 | 15,000 | ~$55 |
| Phase 2c: H8 — Library Composition | 7 | 21,000 | ~$77 |
| Phase 2d: H5 — Negative Text | 6 | 18,000 | ~$66 |
| Phase 2e: H4 — Ordering | 4 (1 reused) | 1,800 net new | ~$7 |
| **Phase 2 Confirmatory** | **26** | **78,000** | **~$286** |
| Phase 3a: H3 N=30 Extension | — | ~12,000 | ~$44 |
| Phase 3c: H9 Diversity (exploratory) | — | ~6,000 | ~$22 |
| Phase 3d: H2 Two-Stage (exploratory) | — | ~1,200 | ~$4 |
| **Flash Subtotal** | **26+** | **~97,300** | **~$357** |
| Phase 4: H6 Pro Transfer | — | ~1,400-1,600 | ~$42-48 |
| **Confirmatory Total** | — | **~99,000** | **~$399-405** |
| Phase 5: Exploratory (H10-H15) | — | ~7,000-12,000 | ~$40-60 |
| **Grand Total** | — | **~106,000-111,000** | **~$439-465** |

**Triggered exploratory** (not included in totals above):

| Hypothesis | Trigger | Cells | Calls | Cost |
|------------|---------|-------|-------|------|
| H4b (HP/HN ordering) | H4 significant (p < 0.05) | 2 | 1,200 | ~$4 |
| HN-only condition | β_hardneg > 2×β_hardpos | 1 | 600 | ~$2 |
| **Maximum triggered** | | **3** | **1,800** | **~$6** |

**Soft budget limit**: $500 (triggers review, not hard cap)
**Contingency**: 20% buffer → **Budget ceiling: ~$600**

**Notes**:

- Sequential design reduces confirmatory cells from ~54 to 26
- H5 now tests at all 3 image-using M/E levels (3 M/E × 3 H5 = 9 cells, 6 net new)
- H9 is exploratory; H2 and H6 remain confirmatory
- Flash-only confirmatory testing costs ~$286
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

*Document version: 3.0*
*Created: 2025-12-31*
*Updated: 2026-01-14*

**Changelog:**

- v3.0: Aligned with preregistration.md v4.6 — H5 scope expanded to test at all 3 image-using M/E levels (3 M/E × 3 H5 = 9 cells, 6 net new); total confirmatory cells updated from 23 to 26; cost estimates corrected (~$286 confirmatory); Phase 0 checklist updated to reflect all 9 H5 instruction files and configs now created; budget summary recalculated with revised per-cell costs
- v2.9: Major redesign aligned with preregistration.md v4.5 — replaced stranded factorial with sequential OFAT design; H5 now tests text treatment only (Minimal/Terse/Verbose) given negatives present; H8 expanded to 7 conditions with sequential addition (C1-C3) and scaling (S1-S3) contrasts; H4 simplified to optimal M/E only (3 cells); H7 adds T=0.3 (5 levels); added triggered exploratory (H4b, HN-only); revised budget (~$50 confirmatory vs ~$171); Phase 2 restructured to sequential phases 2a-2e; Phase 3b absorbed into Phase 2e
- v2.8: Aligned with preregistration.md v4.4 — renamed "Pure" to "Pure Positive Canon" in Strand 2 table; updated H8 library compositions to match preregistration; clarified distinction between H5=None (includes HP) and Pure Positive Canon (no HP); updated planned contrasts; corrected terminology (benchmark not "bench mark")
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
