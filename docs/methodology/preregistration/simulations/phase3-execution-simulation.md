# Phase 3 Execution Simulation

> **NOT PART OF THE OSF LODGEMENT.** The registration comprises exactly three
> documents, all in `osf/` (`osf/README.md:3,9-11`); this file is not one of
> them. It is a working document: pre-lodgement content here fed into writing
> the registration but does not license a "the preregistration says" claim,
> and post-lodgement content is operational, not registered. Cite
> `osf/preregistration.md` for registered content. Banner added 2026-07-28
> (D17 audit, structural fix).

**Purpose**: Detailed walkthrough of Phase 3 (Follow-up Experiments) to identify operational requirements and scaffolding needs.

**Status**: Simulation only — not actual execution

**Prerequisites**: Phase 2 complete, optimal configuration determined

---

## Phase 3 Overview

Phase 3 executes follow-up experiments that extend the confirmatory findings from Phase 2. It consists of three active sub-phases that can run in parallel after Phase 2 completes.

**Goal**: Test voting extension (H3), diversity mechanisms (H9), and two-stage pipeline (H2).

**Inputs required**:

- Phase 2 optimal configuration (M/E, T, library, H5, ordering)
- 60 validation tiles (from `validation_manifest.json`)
- Ground truth annotations
- Phase 2 detection results (for voting extension)

**Outputs**:

- H3: Threshold sweep curves for N=5, 10, 30
- H9: Effect sizes for text and image diversity mechanisms
- H2: F1 comparison between single-stage and two-stage pipeline

---

## Phase 3 Structure

| Sub-phase | Hypothesis | Description | Trigger | API Calls | Est. Cost |
|-----------|------------|-------------|---------|-----------|-----------|
| 3a | H3 | Voting extension to N=30 | Always run | ~1,200 | ~$4 |
| 3b | — | *(Absorbed into Phase 2e)* | — | — | — |
| 3c | H9 | Diversity mechanisms (text/image) | If H3 shows voting helps | ~6,000 | ~$22 |
| 3d | H2 | Two-stage pipeline (proposer→verifier) | Always run | ~600-1,200 | ~$4 |
| **Total** | | | | **~8,400** | **~$30** |

**Note on Phase 3b**: H4 ordering testing was originally planned for Phase 3b but has been absorbed into Phase 2e. See `execution-plan.md` lines 515-524 for rationale.

---

## Pre-Flight Checklist

### Phase 2 Prerequisites

- [ ] Phase 2 complete: All sub-phases 2a-2e executed
- [ ] Optimal M/E determined from Phase 2a (H1)
- [ ] Optimal temperature determined from Phase 2b (H7)
- [ ] Optimal library determined from Phase 2c (H8)
- [ ] Optimal H5 treatment determined from Phase 2d
- [ ] Optimal ordering determined from Phase 2e (H4)
- [ ] Phase 2 results documented in decisions log

### Data Resources

- [ ] Validation manifest exists: `inputs/tiles/validation_manifest.json`
- [ ] Ground truth exists: `inputs/vectors/references/mounds-reference.geojson`
- [ ] Validation bounds exist: `inputs/vectors/bounds/validation_bounds.geojson`
- [ ] All 60 validation tiles present in tile directories

### Configuration Files

#### Phase 3a: H3 Voting Extension

- [x] Optimal detection config from Phase 2 (determined after 2e)
- [ ] Config updated with Phase 2 optimal parameters

#### Phase 3c: H9 Diversity Testing (4 configs)

- [ ] `prompts/configs/diversity_baseline.json` — Fixed text, fixed images
- [ ] `prompts/configs/diversity_text-varied.json` — 5 text variants, fixed images
- [ ] `prompts/configs/diversity_images-varied.json` — Fixed text, resampled images
- [ ] `prompts/configs/diversity_both-varied.json` — 5 text variants, resampled images

#### Phase 3d: H2 Two-Stage Pipeline

- [x] `prompts/configs/propose_brief.json` — Proposer config (template)
- [x] `prompts/configs/verify_brief.json` — Verifier config (template)
- [ ] Both configs updated with Phase 2 optimal parameters

### System Instruction Files

#### H9 Text Variants (5 files needed)

- [ ] `prompts/system-instructions/detect_optimal_v1.md` — Base text
- [ ] `prompts/system-instructions/detect_optimal_v2.md` — Semantically equivalent variant
- [ ] `prompts/system-instructions/detect_optimal_v3.md` — Semantically equivalent variant
- [ ] `prompts/system-instructions/detect_optimal_v4.md` — Semantically equivalent variant
- [ ] `prompts/system-instructions/detect_optimal_v5.md` — Semantically equivalent variant

#### H2 Two-Stage Instructions

- [x] `prompts/system-instructions/propose_brief.md` — Proposer instructions
- [x] `prompts/system-instructions/verify_brief.md` — Verifier instructions

### Scripts

- [x] Detection: `scripts/4_detect_mounds_batch.py`
- [x] Consensus analysis: `scripts/7_analyse_consensus.py`
- [x] Accuracy report: `scripts/6_accuracy_report.py`
- [x] Pass merger: `scripts/merge_passes.py`
- [ ] H3 threshold sweep: Extends `7_analyse_consensus.py` for N=5,10,30 sweep — **MISSING**
- [ ] H9 image resampling: Per-pass hard example resampling — **MISSING**
- [ ] H2 candidate extraction: Crop proposer detections for verifier — **MISSING**
- [ ] H2 pipeline orchestration: Proposer → extraction → verifier flow — **MISSING**

### Study Configuration

- [ ] Phase 3a YAML: `studies/phase3a-h3-voting.yaml` — **MISSING**
- [ ] Phase 3c YAML: `studies/phase3c-h9-diversity.yaml` — **MISSING**
- [ ] Phase 3d YAML: `studies/phase3d-h2-twostage.yaml` — **MISSING**

---

## Sub-Phase Execution Walkthroughs

### Phase 3a: H3 — Voting Extension to N=30

**Purpose**: Extend voting pool from N=5/10 to N=30 to determine optimal voting threshold.

**Prerequisite**: Optimal configuration from Phase 2.

**Design**:

Phase 2 already provides K=10 runs × N=5 passes = 50 passes at optimal config. From these:
- N=5 voting: Use 5 passes per run (existing)
- N=10 voting: Combine 2 runs of 5 passes each (free computation)
- N=30 voting: Requires 20 additional passes

**Data sources**:

| Source | Passes | New API Calls |
|--------|--------|---------------|
| Phase 2 optimal cell | 50 (K=10 × N=5) | 0 |
| Additional Phase 3a runs | 20 | 1,200 |
| **Total** | 70 | 1,200 |

**Command pattern** (for additional 20 passes):

```bash
# Run 20 additional passes at optimal config
for pass in {1..20}; do
    python scripts/4_detect_mounds_batch.py \
        --config prompts/configs/detect_{optimal_config}.json \
        --manifest inputs/tiles/validation_manifest.json \
        --output-dir outputs/phase3a/h3_voting/pass_${pass} \
        --temperature ${optimal_T} \
        --ordering ${optimal_ordering} \
        --workers 1
done
```

**Analysis**:

1. Merge all 70 passes into pooled detection set
2. Sweep voting thresholds T = 1, 2, 3, ..., 30
3. For each T, compute F1, precision, recall
4. Identify optimal (N, T) combination
5. Compute cost-efficiency (F1 per dollar)

**Outputs**:

- `outputs/phase3a/threshold_sweep.json` — F1, P, R at each threshold
- `outputs/phase3a/threshold_curves.png` — Visualisation
- `outputs/phase3a/cost_efficiency.json` — F1/$ at each N

**Gaps to fill before execution**:

1. Threshold sweep analysis script (extend `7_analyse_consensus.py`)
2. Phase 3a study YAML
3. Cost-efficiency calculation

---

### Phase 3c: H9 — Diversity Testing

**Purpose**: Test whether introducing diversity in prompts or examples improves consensus voting.

**Trigger**: Run if H3 shows voting helps (expected).

**Design**: 2×2 factorial at optimal configuration.

| Condition | Text | Images | Description |
|-----------|------|--------|-------------|
| A (baseline) | Fixed | Fixed | Identical prompt and examples across all 5 passes |
| B (text-varied) | Varied | Fixed | 5 semantically equivalent text variants, same images |
| C (images-varied) | Fixed | Varied | Same prompt, resampled hard examples per pass |
| D (both-varied) | Varied | Varied | Both mechanisms combined |

**Text variation strategy**:

Create 5 semantically equivalent instruction files that convey the same detection task but with different wording. For example:
- v1: "Identify burial mounds marked with specific symbols..."
- v2: "Detect circular mound features indicated by..."
- v3: "Locate mound symbols represented as..."
- etc.

**Image resampling strategy**:

For each pass, randomly resample hard examples from the extended pool while:
- Maintaining category balance (same number of HP, HN per pass)
- Using frequency caps (no example appears in >60% of passes)
- Using seeded randomness for reproducibility

**Command pattern** (condition B: text-varied):

```bash
# Run 5 passes with different text variants
for pass in {1..5}; do
    python scripts/4_detect_mounds_batch.py \
        --config prompts/configs/diversity_text-varied.json \
        --instruction-variant v${pass} \
        --manifest inputs/tiles/validation_manifest.json \
        --output-dir outputs/phase3c/h9_text-varied/run_${run}/pass_${pass} \
        --temperature ${optimal_T} \
        --workers 1
done
```

**Command pattern** (condition C: images-varied):

```bash
# Run 5 passes with resampled hard examples
for pass in {1..5}; do
    python scripts/4_detect_mounds_batch.py \
        --config prompts/configs/diversity_images-varied.json \
        --resample-examples --resample-seed $((pass + run * 100)) \
        --manifest inputs/tiles/validation_manifest.json \
        --output-dir outputs/phase3c/h9_images-varied/run_${run}/pass_${pass} \
        --temperature ${optimal_T} \
        --workers 1
done
```

**API calls**:

- Each condition: K=5 runs × N=5 passes × 60 tiles = 1,500 calls
- 4 conditions × 1,500 = **6,000 calls**

**Analysis**:

Using bootstrapped CIs with planned contrasts (consistent with Phase 2):

1. **Text effect**: Compare (B+D) vs (A+C) — does text variation help?
2. **Image effect**: Compare (C+D) vs (A+B) — does image variation help?
3. **Interaction**: Test if D-(B+C-A) differs from zero — synergy or redundancy?

Report effect sizes with 95% bootstrapped CIs.

**Outputs**:

- `outputs/phase3c/h9_results.json` — Per-condition F1 with CIs
- `outputs/phase3c/h9_analysis.md` — Effect sizes and interpretation

**Gaps to fill before execution**:

1. 5 semantically equivalent instruction files
2. Image resampling logic in detection script (or wrapper)
3. `--instruction-variant` or `--resample-examples` CLI flags
4. H9 diversity configs
5. Phase 3c study YAML

---

### Phase 3d: H2 — Two-Stage Pipeline

**Purpose**: Compare single-stage detection vs proposer→verifier pipeline.

**Trigger**: Always run (confirms preliminary finding).

**Prerequisites**: All optimal parameters from Phase 2.

**Design**:

| Condition | Description |
|-----------|-------------|
| A (single-stage) | Standard detection at optimal config (reuse Phase 2 results) |
| B (two-stage) | Proposer → candidate extraction → verifier pipeline |

**Two-stage protocol**:

Each of K=10 runs is independent:
1. **Proposer pass**: Run proposer config on all 60 tiles
2. **Candidate extraction**: Crop regions around proposer detections
3. **Verifier pass**: Score each candidate with `mound_probability`
4. **Evaluation**: Use verifier scores directly (no binary thresholding)

**Config finalisation** (before execution):

Update both `propose_brief.json` and `verify_brief.json` with:
- Optimal temperature from Phase 2b
- Optimal library from Phase 2c
- Optimal M/E instruction file from Phase 2a

```bash
# Example finalisation (manual or scripted)
# 1. Update temperature in both configs
# 2. Update examples array with optimal library
# 3. Update instruction_file with optimal M/E instruction
# 4. Commit with version tag (e.g., h2-final-20260125)
```

**Command pattern** (proposer):

```bash
# K=10 runs, single pass each
for run in {1..10}; do
    python scripts/4_detect_mounds_batch.py \
        --config prompts/configs/propose_brief.json \
        --manifest inputs/tiles/validation_manifest.json \
        --output-dir outputs/phase3d/h2_proposer/run_${run} \
        --workers 1
done
```

**Candidate extraction**:

```bash
# Extract candidate regions from proposer output
python scripts/extract_candidates.py \
    --input outputs/phase3d/h2_proposer/run_${run}/*.geojson \
    --tiles-dir inputs/tiles/ \
    --output-dir outputs/phase3d/h2_candidates/run_${run} \
    --padding 50  # pixels around detection centroid
```

**Command pattern** (verifier):

```bash
# Verify extracted candidates
python scripts/4_detect_mounds_batch.py \
    --config prompts/configs/verify_brief.json \
    --manifest outputs/phase3d/h2_candidates/run_${run}/candidate_manifest.json \
    --output-dir outputs/phase3d/h2_verifier/run_${run} \
    --workers 1
```

**API calls**:

- Proposer: K=10 runs × 60 tiles = 600 calls
- Verifier: ~X candidates (depends on proposer FP rate)
- Estimate: ~600-1,200 total calls

**Stopping rule**: Two-stage must exceed single-stage by ≥0.05 F1 to justify ~2× cost overhead.

**Analysis**:

1. Aggregate F1, precision, recall for single-stage (from Phase 2)
2. Compute F1, precision, recall for two-stage pipeline
3. Bootstrap difference CI for F1_twostage - F1_single
4. Apply stopping rule

**Outputs**:

- `outputs/phase3d/h2_comparison.json` — Metrics for both conditions
- `outputs/phase3d/h2_analysis.md` — Effect size and decision

**Gaps to fill before execution**:

1. Candidate extraction script (`scripts/extract_candidates.py`)
2. Pipeline orchestration (proposer → extract → verifier)
3. Config finalisation with Phase 2 optimal params
4. Phase 3d study YAML

---

## Gap Analysis Summary

### What Exists

| Component | Path | Status |
|-----------|------|--------|
| Consensus analysis | `scripts/7_analyse_consensus.py` | Exists, needs extension for threshold sweep |
| Proposer config | `prompts/configs/propose_brief.json` | Template, needs Phase 2 params |
| Verifier config | `prompts/configs/verify_brief.json` | Template, needs Phase 2 params |
| Proposer instructions | `prompts/system-instructions/propose_brief.md` | Complete |
| Verifier instructions | `prompts/system-instructions/verify_brief.md` | Complete |

### Missing Scripts/Features

| Gap | Sub-phase | Priority | Complexity |
|-----|-----------|----------|------------|
| H3 threshold sweep extension | 3a | High | Low |
| H9 text variant selector | 3c | Medium | Low |
| H9 image resampling logic | 3c | Medium | Medium |
| H2 candidate extraction | 3d | High | Medium |
| H2 pipeline orchestration | 3d | High | Medium |

### Missing Configs

| Gap | Sub-phase | Priority |
|-----|-----------|----------|
| H9 diversity configs (4) | 3c | Medium |
| H2 configs finalisation | 3d | High (after Phase 2) |

### Missing Instruction Files

| Gap | Sub-phase | Priority |
|-----|-----------|----------|
| H9 text variants (5 files) | 3c | Medium |

### Missing Study YAMLs

| Gap | Priority |
|-----|----------|
| `phase3a-h3-voting.yaml` | High |
| `phase3c-h9-diversity.yaml` | Medium |
| `phase3d-h2-twostage.yaml` | High |

### Documentation Updates Required

The following `execution-plan.md` references have been updated to match Phase 2 implementation (v4.7):

| Issue | Location | Status |
|-------|----------|--------|
| "2×2 ANOVA" for H9 | Line ~551 | ✅ Updated to "2×2 bootstrap comparison results" |
| "One-way ANOVA" for Phase 2 | Lines 275, 302, etc. | ✅ Updated to "pairwise bootstrap comparisons" |

---

## Resource Planning

### API Calls per Sub-Phase

| Sub-phase | Cells | Calls/Cell | Total Calls | Est. Cost |
|-----------|-------|------------|-------------|-----------|
| 3a (H3) | 1 | 1,200 | 1,200 | ~$4 |
| 3c (H9) | 4 | 1,500 | 6,000 | ~$22 |
| 3d (H2) | 2 | ~600 | ~1,200 | ~$4 |
| **Total** | **7** | — | **~8,400** | **~$30** |

**Cost basis**: Gemini 3 Flash at ~$0.003/call

### Time Estimates

| Sub-phase | Est. Duration | Notes |
|-----------|---------------|-------|
| Phase 3a | 1-2 hours | 20 additional passes + analysis |
| Phase 3c | 4-6 hours | 4 conditions × ~1 hour/cell |
| Phase 3d | 2-3 hours | Proposer + candidate extraction + verifier |
| Analysis | 1-2 hours | Per sub-phase |
| **Total** | **8-13 hours** | Plus analysis time |

---

## Scaffolding Recommendations

### High Priority (Blocking)

1. **H3 threshold sweep extension**
   - Extend `7_analyse_consensus.py` to support multi-N sweep
   - Add cost-efficiency calculation
   - Generate threshold curve visualisations

2. **H2 config finalisation** (after Phase 2)
   - Update `propose_brief.json` and `verify_brief.json` with optimal params
   - Commit with version tag for reproducibility

3. **Phase 3 study YAMLs**
   - Create templates based on Phase 2 YAML structure
   - Include parameter dependencies on Phase 2 results

### Medium Priority (Helpful but Not Blocking)

4. **H9 text variant instruction files**
   - Create 5 semantically equivalent versions of optimal instruction
   - Maintain consistent structure, vary wording

5. **H9 image resampling logic**
   - Add `--resample-examples` flag or wrapper script
   - Implement frequency-capped random sampling

6. **H2 candidate extraction pipeline**
   - Script to crop regions around proposer detections
   - Generate candidate manifest for verifier input

### Low Priority (Can Defer)

1. **H9 diversity analysis**
   - Reuse Phase 2 bootstrap infrastructure
   - Add 2×2 contrast calculations

2. **Cost-efficiency reporting**
   - F1 per dollar metrics
   - Comparative visualisations

---

## Verification Checklist

After completing Phase 3 simulation:

- [x] All 3 active sub-phases documented with execution steps
- [x] Phase 3b absorption noted
- [x] Analysis methodology uses bootstrapped CIs (not ANOVA)
- [x] Gap analysis categorised (scripts, configs, docs)
- [x] Resource estimates provided (API calls, cost, time)
- [x] Scaffolding recommendations prioritised
- [x] Dependencies on Phase 2 clearly documented
- [x] ANOVA inconsistency in `execution-plan.md` flagged for update
- [x] Document follows Phase 1/2 template structure

---

*Simulation created: 2026-01-22*
