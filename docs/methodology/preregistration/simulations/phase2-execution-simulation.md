# Phase 2 Execution Simulation

**Purpose**: Detailed walkthrough of Phase 2 (Sequential Confirmatory Factorial Testing) to identify operational requirements and scaffolding needs.

**Status**: Simulation only — not actual execution

**Prerequisites**: Phase 1 complete, hard example library constructed

---

## Phase 2 Overview

Phase 2 executes the confirmatory factorial testing using a sequential One-Factor-At-a-Time (OFAT) design. Each sub-phase tests one hypothesis while carrying optimal parameters forward from previous sub-phases.

**Goal**: Determine optimal configuration for Modality/Elaboration, Temperature, Library Composition, Negative Text Treatment, and Example Ordering.

**Inputs required**:

- 60 validation tiles (from `validation_manifest.json`)
- Ground truth annotations
- Phase 1 outputs (hard example library: examples 05-08, 11-14)
- All detection configs
- All system instruction files

**Outputs**:

- Detection results: K=10 runs × N=5 passes × 60 tiles per cell
- Statistical analyses (pairwise bootstrap comparisons per sub-phase)
- Optimal configuration for subsequent phases
- Aggregated results in CSV format

---

## Phase 2 Structure

| Sub-phase | Hypothesis | Factor | Cells | API Calls | Est. Cost |
|-----------|------------|--------|-------|-----------|-----------|
| 2a | H1 | Modality/Elaboration (5 levels) | 5 | 15,000 | ~$55 |
| 2b | H7 | Temperature (5 levels) | 5 | 15,000 | ~$55 |
| 2c | H8 | Library Composition (7 conditions) | 7 | 21,000 | ~$77 |
| 2d | H5 | Negative Text (3 M/E × 3 H5, 6 net new) | 6 | 18,000 | ~$66 |
| 2e | H4 | Ordering (3 conditions) | 3 | 9,000 | ~$33 |
| **Total** | | | **26** | **78,000** | **~$286** |

**Evaluation protocol**: K=10 independent runs with N=5 consensus voting per run.

- Per-cell calls: 10 runs × 5 passes × 60 tiles = 3,000 API calls
- Holdout tiles: 60 tiles containing 79 mound symbols

---

## Pre-Flight Checklist

### Phase 1 Prerequisites

- [ ] Phase 1 complete: `outputs/phase1-library/` contains merged detections
- [ ] Hard positive library: `inputs/examples/neutral-naming/example_05-08.png` exist
- [ ] Hard negative library: `inputs/examples/neutral-naming/example_11-14.png` exist
- [ ] Library manifest updated: `inputs/examples/neutral-naming/MANIFEST.md` documents provenance
- [ ] Phase 1 baseline metrics recorded in `docs/methodology/preregistration/decisions-log.md`

### Data Resources

- [ ] Validation manifest exists: `inputs/tiles/validation_manifest.json`
- [ ] Ground truth exists: `inputs/vectors/references/mounds-reference.geojson`
- [ ] Validation bounds exist: `inputs/vectors/bounds/validation_bounds.geojson`
- [ ] All 60 validation tiles present in tile directories

### Configuration Files

#### Phase 2a: H1 Modality/Elaboration (5 configs)

- [x] `prompts/configs/detect_image-only.json`
- [x] `prompts/configs/detect_brief-text.json`
- [x] `prompts/configs/detect_brief-text-image.json`
- [x] `prompts/configs/detect_verbose-text.json`
- [x] `prompts/configs/detect_verbose-text-image.json`

#### Phase 2b: H7 Temperature

Temperature is a config parameter, not separate files:

- [x] Detection script supports `--temperature` CLI override
- Note: Added in v4.3.0 of `4_detect_mounds_batch.py`

#### Phase 2c: H8 Library Composition (7 configs)

- [x] `prompts/configs/library_pure-positive-canon.json` — Pure Positive Canon (7 examples)
- [x] `prompts/configs/library_canonical.json` — Canonical (9 examples)
- [x] `prompts/configs/library_plus-hp.json` — +HP (13 examples)
- [x] `prompts/configs/library_scale-4.json` — Scale-4 (13 examples)
- [x] `prompts/configs/library_scale-8.json` — Scale-8 (17 examples)
- [x] `prompts/configs/library_scale-16.json` — Scale-16 (25 examples)
- [x] `prompts/configs/library_scale-32.json` — Scale-32 (41 examples)

#### Phase 2d: H5 Negative Text (6 net new configs)

Baseline (H5=Minimal) reuses H1 configs. Terse and Verbose variants:

- [x] `prompts/configs/detect_image-only_terse.json`
- [x] `prompts/configs/detect_image-only_verbose.json`
- [x] `prompts/configs/detect_brief-text-image_terse.json`
- [x] `prompts/configs/detect_brief-text-image_verbose.json`
- [x] `prompts/configs/detect_verbose-text-image_terse.json`
- [x] `prompts/configs/detect_verbose-text-image_verbose.json`

#### Phase 2e: H4 Ordering (2 new configs needed)

Current configs use "canonical-first" ordering. Need:

- [x] Canonical-first: Existing configs
- [ ] `prompts/configs/detect_*_canonical-last.json` — Canonical examples at end
- [ ] `prompts/configs/detect_*_random.json` — Shuffled ordering

### System Instruction Files

#### H1 Base Instructions (5 files)

- [x] `prompts/system-instructions/detect_image-only.md`
- [x] `prompts/system-instructions/detect_brief-text.md`
- [x] `prompts/system-instructions/detect_brief-text-image.md`
- [x] `prompts/system-instructions/detect_verbose-text.md`
- [x] `prompts/system-instructions/detect_verbose-text-image.md`

#### H5 Variant Instructions (6 files)

- [x] `prompts/system-instructions/detect_image-only_terse.md`
- [x] `prompts/system-instructions/detect_image-only_verbose.md`
- [x] `prompts/system-instructions/detect_brief-text-image_terse.md`
- [x] `prompts/system-instructions/detect_brief-text-image_verbose.md`
- [x] `prompts/system-instructions/detect_verbose-text-image_terse.md`
- [x] `prompts/system-instructions/detect_verbose-text-image_verbose.md`

### Scripts

- [x] Detection: `scripts/4_detect_mounds_batch.py` (v4.3.0 with `--temperature`, `--ordering` flags)
- [x] Pass merger: `scripts/merge_passes.py`
- [x] Accuracy report: `scripts/6_accuracy_report.py`
- [x] Consensus analysis: `scripts/7_analyse_consensus.py`
- [x] Effect size analysis: `scripts/analyse_study_effects.py`
- [x] Advanced metrics: `scripts/lib_advanced_metrics.py`
- [x] Preflight check: `scripts/preflight_check.py`
- [x] Phase 2 orchestration: Use existing `scripts/run_study.py` (no new script needed)
- [x] Multi-condition analysis: `scripts/analyse_phase2_results.py` (bootstrapped CIs + FDR)
- [ ] Results collation: Aggregated CSV generation — **MISSING** (low priority)

### Study Configuration

- [x] Phase 1 YAML: `studies/phase1-library.yaml`
- [x] Phase 2a YAML: `studies/phase2a-h1-modality.yaml`
- [x] Phase 2b YAML: `studies/phase2b-h7-temperature.yaml`
- [x] Phase 2c YAML: `studies/phase2c-h8-library.yaml`
- [x] Phase 2d YAML: `studies/phase2d-h5-negtext.yaml`
- [x] Phase 2e YAML: `studies/phase2e-h4-ordering.yaml`

---

## Sub-Phase Execution Walkthroughs

### Phase 2a: H1 — Modality/Elaboration Level

**Purpose**: Determine optimal text modality and elaboration level.

**Design**: 5 M/E levels at T=1.0, Scale-8 library, canonical-first ordering.

| Config | M/E Level | Description |
|--------|-----------|-------------|
| `detect_image-only.json` | Image-only | No text guidance |
| `detect_brief-text.json` | Brief-text | Text-only (concise) |
| `detect_brief-text-image.json` | Brief-text+image | Concise text + images |
| `detect_verbose-text.json` | Verbose-text | Text-only (detailed) |
| `detect_verbose-text-image.json` | Verbose-text+image | Detailed text + images |

**Command pattern** (for each config × 10 runs × 5 passes):

```bash
# Outer loop: K=10 runs
for run in {1..10}; do
    # Inner loop: N=5 passes per run
    for pass in {1..5}; do
        python scripts/4_detect_mounds_batch.py \
            --config prompts/configs/detect_image-only.json \
            --manifest inputs/tiles/validation_manifest.json \
            --output-dir outputs/phase2a/h1_image-only/run_${run}/pass_${pass} \
            --workers 1
    done
done
```

**Expected outputs**:

- `outputs/phase2a/h1_{condition}/run_{N}/pass_{M}/*.geojson`
- `outputs/phase2a/h1_{condition}/run_{N}/pass_{M}/*.meta.json`

**Analysis**:

- Pairwise bootstrap comparisons across 5 M/E levels (95% CIs, FDR-corrected)
- Outcome: Optimal M/E → carried forward to Phase 2b

**Gaps to fill before execution**:

1. Validation manifest file (verify existence/create)
2. Phase 2a study YAML
3. Orchestration script to manage K×N loop
4. Bootstrap analysis script

---

### Phase 2b: H7 — Temperature

**Purpose**: Determine optimal temperature setting.

**Prerequisite**: Optimal M/E from Phase 2a.

**Design**: 5 temperature levels at optimal M/E.

| Temperature | Description |
|-------------|-------------|
| 0.0 | Minimum (deterministic) |
| 0.3 | Low variance |
| 0.7 | Moderate variance |
| 1.0 | Vendor default |
| 1.3 | Above default |

**Implementation options**:

A. **CLI override** (preferred): Add `--temperature` flag to detection script

```bash
python scripts/4_detect_mounds_batch.py \
    --config prompts/configs/detect_{optimal_me}.json \
    --manifest inputs/tiles/validation_manifest.json \
    --output-dir outputs/phase2b/h7_T0.3/run_${run}/pass_${pass} \
    --temperature 0.3 \
    --workers 1
```

B. **Config duplication**: Create 5 copies of optimal config with different temperature values

```text
prompts/configs/detect_{optimal_me}_T0.0.json
prompts/configs/detect_{optimal_me}_T0.3.json
prompts/configs/detect_{optimal_me}_T0.7.json
prompts/configs/detect_{optimal_me}_T1.0.json
prompts/configs/detect_{optimal_me}_T1.3.json
```

**Recommendation**: Option A (CLI override) is more maintainable and avoids config proliferation.

**Expected outputs**:

- `outputs/phase2b/h7_T{value}/run_{N}/pass_{M}/*.geojson`

**Analysis**:

- Pairwise bootstrap comparisons across 5 temperature levels (95% CIs, FDR-corrected)
- Planned contrasts: T=1.0 vs each other level
- Outcome: Optimal T → carried forward to Phase 2c

**Gaps to fill before execution**:

1. Modify `4_detect_mounds_batch.py` to accept `--temperature` CLI override
2. Phase 2b study YAML
3. Bootstrap analysis script

---

### Phase 2c: H8 — Library Composition and Scaling

**Purpose**: Determine optimal library composition and size.

**Prerequisites**: Optimal M/E and T from Phases 2a-2b.

**Design**: 7 library conditions.

| ID | Config | Composition | Total |
|----|--------|-------------|-------|
| 1 | `library_pure-positive-canon.json` | Canon+ (4), null (3) | 7 |
| 2 | `library_canonical.json` | Canon+ (4), Canon- (2), null (3) | 9 |
| 3 | `library_plus-hp.json` | Canon+ (4), HP (4), Canon- (2), null (3) | 13 |
| 4 | `library_scale-4.json` | Canon+ (4), HP (2), Canon- (2), HN (2), null (3) | 13 |
| 5 | `library_scale-8.json` | Canon+ (4), HP (4), Canon- (2), HN (4), null (3) | 17 |
| 6 | `library_scale-16.json` | Canon+ (4), HP (8), Canon- (2), HN (8), null (3) | 25 |
| 7 | `library_scale-32.json` | Canon+ (4), HP (16), Canon- (2), HN (16), null (3) | 41 |

**Note**: Library configs define example composition but need pairing with optimal M/E instruction file from Phase 2a. May need to verify how library configs interact with M/E configs.

**Command pattern**:

```bash
# Use optimal M/E instruction with each library composition
python scripts/4_detect_mounds_batch.py \
    --config prompts/configs/library_scale-8.json \
    --manifest inputs/tiles/validation_manifest.json \
    --output-dir outputs/phase2c/h8_scale-8/run_${run}/pass_${pass} \
    --temperature ${optimal_T} \
    --workers 1
```

**Expected outputs**:

- `outputs/phase2c/h8_{condition}/run_{N}/pass_{M}/*.geojson`

**Analysis**:

- Pairwise bootstrap comparisons across 7 library conditions (95% CIs, FDR-corrected)
- Planned contrasts: Sequential addition (C1-C3) and scaling (S1-S3)
- Outcome: Optimal library → carried forward to Phase 2d

**Gaps to fill before execution**:

1. Verify library configs use correct instruction file (may need `instruction_file` field update)
2. Phase 2c study YAML
3. Ensure Scale-16 and Scale-32 have sufficient hard examples (may require extended HP/HN pools)

---

### Phase 2d: H5 — Negative Text Treatment

**Purpose**: Determine optimal text treatment for negative examples.

**Prerequisites**: Optimal T and library from Phases 2b-2c.

**Design**: 3 H5 levels × 3 image-using M/E levels (9 total cells, 3 overlap with H1 baseline, 6 net new).

| H5 Level | Description | Configs |
|----------|-------------|---------|
| Minimal | "Negative" label only | `detect_image-only.json`, `detect_brief-text-image.json`, `detect_verbose-text-image.json` |
| Terse | Brief exclusion guidance | `detect_image-only_terse.json`, `detect_brief-text-image_terse.json`, `detect_verbose-text-image_terse.json` |
| Verbose | Detailed exclusion guidance | `detect_image-only_verbose.json`, `detect_brief-text-image_verbose.json`, `detect_verbose-text-image_verbose.json` |

**Note**: H5=Minimal at each M/E level is already tested in Phase 2a, so Phase 2d only needs to run Terse and Verbose variants (6 new cells).

**Command pattern**:

```bash
# Terse variant at image-only M/E
python scripts/4_detect_mounds_batch.py \
    --config prompts/configs/detect_image-only_terse.json \
    --manifest inputs/tiles/validation_manifest.json \
    --output-dir outputs/phase2d/h5_image-only_terse/run_${run}/pass_${pass} \
    --temperature ${optimal_T} \
    --workers 1
```

**Expected outputs**:

- `outputs/phase2d/h5_{me}_{level}/run_{N}/pass_{M}/*.geojson`

**Analysis**:

- Bootstrap interaction test (3 M/E × 3 H5, difference-of-differences with 95% CI)
- Test H5 main effect and M/E × H5 interaction
- Planned contrasts: Minimal vs Terse, Terse vs Verbose
- Outcome: Optimal H5 treatment → carried forward to Phase 2e

**Gaps to fill before execution**:

1. Update H5 variant configs to use optimal library from Phase 2c
2. Phase 2d study YAML
3. Bootstrap interaction analysis capability

---

### Phase 2e: H4 — Example Ordering

**Purpose**: Determine optimal example ordering.

**Prerequisites**: All optimal parameters from Phases 2a-2d.

**Design**: 3 ordering conditions at optimal M/E only.

| Condition | Canonical Position | Hard Position |
|-----------|-------------------|---------------|
| Canonical-first | Positions 1-6 | Final positions |
| Canonical-last | Final positions | Positions 1-N |
| Random | Shuffled | Shuffled |

**Implementation**:

Ordering is controlled by the `examples` array order in config files. Need:

1. **Canonical-first**: Existing configs (current state)
2. **Canonical-last**: Create variant with Canon+ and Canon- at end of examples array
3. **Random**: Either runtime shuffling or pre-shuffled config

**Recommended approach**:

- Add `--ordering` CLI flag with options: `canonical-first`, `canonical-last`, `random`
- Script reorders examples array before sending to API

**Command pattern**:

```bash
python scripts/4_detect_mounds_batch.py \
    --config prompts/configs/detect_{optimal_config}.json \
    --manifest inputs/tiles/validation_manifest.json \
    --output-dir outputs/phase2e/h4_canonical-last/run_${run}/pass_${pass} \
    --temperature ${optimal_T} \
    --ordering canonical-last \
    --workers 1
```

**Triggered exploratory (H4b)**: If H4 significant (p < 0.05), test HP-first vs HN-first ordering within the hard block (+2 cells).

**Expected outputs**:

- `outputs/phase2e/h4_{ordering}/run_{N}/pass_{M}/*.geojson`

**Analysis**:

- Pairwise bootstrap comparisons across 3 orderings (95% CIs, FDR-corrected)
- Planned contrasts: Canonical-first vs Canonical-last
- Outcome: Optimal ordering → final optimal configuration

**Gaps to fill before execution**:

1. Add `--ordering` CLI flag to detection script OR create ordering-specific configs
2. Phase 2e study YAML
3. Document triggered exploratory (H4b) conditions

---

## Gap Analysis Summary

### Missing Configs (0 items — RESOLVED)

| Gap | Priority | Solution | Status |
|-----|----------|----------|--------|
| H4 canonical-last ordering | High | `--ordering canonical-last` CLI flag | ✓ RESOLVED |
| H4 random ordering | High | `--ordering random` CLI flag | ✓ RESOLVED |
| Temperature variants | Medium | `--temperature` CLI flag | ✓ RESOLVED |

### Missing System Instruction Files (0 items)

All required instruction files exist.

### Missing Scripts/Features (1 item)

| Gap | Priority | Complexity | Description | Status |
|-----|----------|------------|-------------|--------|
| `run_phase2.py` orchestration | High | Medium | Use existing `run_study.py` | ✓ RESOLVED |
| `--temperature` CLI flag | High | Low | Override config temperature at runtime | ✓ RESOLVED |
| `--ordering` CLI flag | High | Low | Reorder examples array before API call | ✓ RESOLVED |
| Multi-condition analysis | High | Medium | `analyse_phase2_results.py` with FDR | ✓ RESOLVED |
| Results collation script | Medium | Low | Aggregate per-condition results to CSV | PENDING |

### Missing Study YAMLs (0 items — RESOLVED)

| Gap | Priority | Template basis | Status |
|-----|----------|----------------|--------|
| `phase2a-h1-modality.yaml` | High | `phase1-library.yaml` | ✓ RESOLVED |
| `phase2b-h7-temperature.yaml` | High | Phase 2a output | ✓ RESOLVED |
| `phase2c-h8-library.yaml` | High | Phase 2b output | ✓ RESOLVED |
| `phase2d-h5-negtext.yaml` | High | Phase 2c output | ✓ RESOLVED |
| `phase2e-h4-ordering.yaml` | High | Phase 2d output | ✓ RESOLVED |

### Missing Input Files (verify existence)

| Item | Path | Action |
|------|------|--------|
| Validation manifest | `inputs/tiles/validation_manifest.json` | Verify or create |
| Validation bounds | `inputs/vectors/bounds/validation_bounds.geojson` | Verify or create |
| Scale-16/32 hard examples | `inputs/examples/neutral-naming/example_18-41.png` | May need extended pool |

### Operational Knowledge Gaps (3 items)

| Gap | Resolution |
|-----|------------|
| Config + library interaction | Verify how library configs pair with M/E instruction files |
| Cross-phase parameter handoff | Document mechanism for passing optimal params between sub-phases |
| Checkpoint/resume strategy | Design checkpointing for long-running K×N execution |

---

## Resource Planning

### API Calls per Sub-Phase

| Sub-phase | Cells | Calls/Cell | Total Calls | Est. Cost |
|-----------|-------|------------|-------------|-----------|
| 2a (H1) | 5 | 3,000 | 15,000 | ~$55 |
| 2b (H7) | 5 | 3,000 | 15,000 | ~$55 |
| 2c (H8) | 7 | 3,000 | 21,000 | ~$77 |
| 2d (H5) | 6 | 3,000 | 18,000 | ~$66 |
| 2e (H4) | 3 | 3,000 | 9,000 | ~$33 |
| **Total** | **26** | — | **78,000** | **~$286** |

**Calls/cell formula**: K=10 runs × N=5 passes × 60 tiles = 3,000 calls

**Cost basis**: Gemini 3 Flash at ~$0.003/call

### Time Estimates

| Sub-phase | Est. Duration | Notes |
|-----------|---------------|-------|
| Phase 2a | 4-6 hours | 5 cells × ~1 hour/cell |
| Phase 2b | 4-6 hours | 5 cells |
| Phase 2c | 6-8 hours | 7 cells |
| Phase 2d | 5-7 hours | 6 cells |
| Phase 2e | 3-4 hours | 3 cells |
| Analysis | 2-3 hours | Per sub-phase |
| **Total** | **24-34 hours** | Plus analysis time |

**Rate limiting**: With `workers=1` and typical Gemini rate limits, expect ~50-100 calls/minute → ~30-60 min per 3,000 call cell.

### Quality Checkpoints

After each sub-phase:

1. **Parsing check**: ≥95% responses successfully parsed
2. **Sanity check**: F1 within expected range (±0.05 of Phase 1 baseline)
3. **Cost check**: Actual vs estimated ≤120%
4. **Checkpoint save**: Export intermediate results before proceeding

---

## Scaffolding Recommendations

### High Priority (Required Before Execution) — RESOLVED

1. **Phase 2 orchestration** ✓
   - Use existing `run_study.py` with Phase 2 YAML files
   - K=10 × N=5 execution loop handled by study runner
   - Checkpointing built into study framework

2. **Detection script enhancements** ✓
   - `--temperature` CLI flag added (v4.3.0)
   - `--ordering` CLI flag added with `canonical-first`, `canonical-last`, `random` options
   - `--ordering-seed` for reproducible random ordering

3. **Multi-condition analysis script** ✓
   - `scripts/analyse_phase2_results.py` created
   - Bootstrapped 95% CIs for all metrics
   - Benjamini-Hochberg FDR correction at q=0.05
   - Effect size reporting with CIs
   - JSON and Markdown output formats

4. **Study YAML templates** ✓
   - All 5 Phase 2 YAML files created
   - Parameter handoff via `carried_forward` sections

### Medium Priority (Helpful but Not Blocking)

5. **Results collation script**
   - Aggregate per-condition metrics to CSV
   - Support for threshold sweep analysis

6. **Input validation**
   - Verify holdout manifest and bounds exist
   - Validate hard example symlinks

### Future Considerations

7. **Extended hard example pool** (for Scale-16, Scale-32)
   - May require additional HP/HN extraction if Phase 1 yields <16 candidates

8. **Parallelisation strategy**
   - Multi-worker execution for faster completion
   - Rate limit management

---

## Verification Checklist

After completing Phase 2 simulation:

- [x] All 5 sub-phases documented with execution steps
- [x] All config/instruction files checked for existence
- [x] Gap analysis categorised (scripts, configs, docs, knowledge)
- [x] Resource estimates provided (API calls, cost, time)
- [x] Scaffolding recommendations prioritised
- [x] Document follows Phase 1 template structure

---

*Simulation created: 2026-01-20*
