# Phase 4 Execution Simulation

**Purpose**: Detailed walkthrough of Phase 4 (H6: Flash→Pro Transfer Testing) to identify operational requirements and scaffolding needs.

**Status**: Simulation only — not actual execution

**Prerequisites**: Phase 2-3 complete, optimal Flash configuration determined

---

## Phase 4 Overview

Phase 4 validates that optimisations developed on Gemini 3 Flash (cost-efficient) transfer to Gemini 3 Pro (more capable) without requiring complete re-optimisation. This uses a One-Factor-At-a-Time (OFAT) sensitivity approach on a 20-tile stratified subset.

**Goal**: Confirm Flash→Pro transfer and document any Pro-specific adjustments needed.

**Inputs required**:

- 20-tile stratified subset (from `phase4_validation_manifest.json`)
- Flash-optimal configuration from Phase 2-3 (M/E, T, library, H5, ordering)
- Ground truth annotations
- Phase 3a voting threshold results

**Outputs**:

- H6: Transfer success rate (% of factors transferring)
- Pro baseline performance metrics (F1, precision, recall)
- Pro-specific recommendations (if any adjustments needed)
- Voting threshold comparison (Flash vs Pro)

---

## Phase 4 Structure

| Sub-phase | Hypothesis | Description | Trigger | API Calls | Est. Cost |
|-----------|------------|-------------|---------|-----------|-----------|
| 4a | H6 | Baseline comparison at Flash-optimal config | Always run | 200 | ~$6 |
| 4b | H6 | OFAT sensitivity testing (~4 factors × 2 alternatives) | Always run | ~1,200 | ~$36 |
| 4c | H6 | Voting threshold analysis | Always run (no new API calls) | 0 | $0 |
| 4d | H6 | Refinement (conditional) | If 4b flags adjustments | 0-200 | $0-6 |
| **Total** | | | | **~1,400-1,600** | **~$42-48** |

**Cost basis**: Gemini 3 Pro at ~$0.03/call (verify at execution time — approximately 10× Flash pricing).

---

## Pre-Flight Checklist

### Phase 2-3 Prerequisites

- [ ] Phase 2 complete: All sub-phases 2a-2e executed
- [ ] Optimal M/E determined from Phase 2a (H1)
- [ ] Optimal temperature determined from Phase 2b (H7)
- [ ] Optimal library determined from Phase 2c (H8)
- [ ] Optimal H5 treatment determined from Phase 2d
- [ ] Optimal ordering determined from Phase 2e (H4)
- [ ] Phase 3a voting analysis complete: Optimal (N, T) for Flash determined
- [ ] All results documented in decisions log

### Data Resources

- [ ] Phase 4 validation manifest exists: `inputs/tiles/phase4_validation_manifest.json`
- [ ] Phase 4 validation bounds exist: `inputs/vectors/bounds/phase4_validation_bounds.geojson`
- [ ] Ground truth exists: `inputs/vectors/references/mounds-reference.geojson`
- [ ] All 20 validation tiles present in tile directories
- [ ] Density distribution preserved in 20-tile subset (empty/sparse/dense ratio)

### Configuration Files

#### Phase 4a-4d: All Configs from Phase 2

- [ ] Optimal M/E config identified (from Phase 2a winner)
- [ ] Optimal library config identified (from Phase 2c winner)
- [ ] `--model gemini-3-pro` runtime parameter available

**Note**: No new config files required — model selection is a runtime parameter, not config-encoded.

### Scripts

- [x] Detection: `scripts/4_detect_mounds_batch.py` (supports `--model` flag)
- [x] Consensus analysis: `scripts/7_analyse_consensus.py`
- [x] Accuracy report: `scripts/6_accuracy_report.py`
- [x] Pass merger: `scripts/merge_passes.py`
- [x] Threshold sweep: `scripts/7_analyse_consensus.py` (with `--threshold-sweep`)
- [ ] Stratified subset selection: `scripts/select_tiles_phase4.py` — **MISSING**
- [ ] Transfer analysis: `scripts/analyse_phase4_transfer.py` — **MISSING**

### Study Configuration

- [ ] Phase 4 YAML: `studies/phase4-transfer.yaml` — **MISSING**

---

## Sub-Phase Execution Walkthroughs

### Phase 4a: Baseline Comparison

**Purpose**: Verify Pro performance at Flash-optimal configuration before sensitivity testing.

**Prerequisites**: All optimal parameters from Phase 2-3.

**Design**:

- **Model**: Gemini 3 Pro
- **Configuration**: Flash-optimal params (M/E, T, library, H5, ordering)
- **Tile subset**: 20 stratified tiles (preserving density distribution from 60 holdout)
- **Runs**: K=10 independent runs × N=1 pass each (simpler than Phase 2's K×N=50)

**Command pattern**:

```bash
# Run K=10 independent runs at Flash-optimal config with Pro model
for run in {1..10}; do
    python scripts/4_detect_mounds_batch.py \
        --config prompts/configs/detect_{optimal_me}.json \
        --manifest inputs/tiles/phase4_validation_manifest.json \
        --output-dir outputs/phase4a/baseline/run_${run} \
        --model gemini-3-pro \
        --temperature ${optimal_T} \
        --ordering ${optimal_ordering} \
        --workers 1
done
```

**API calls**: K=10 runs × 20 tiles = **200 calls**

**Estimated cost**: ~$6 (Pro at ~$0.03/call)

**Decision point**:

| Outcome | Δ F1 | Action |
|---------|------|--------|
| Transfer success | ≤0.05 | Proceed with OFAT (Phase 4b) |
| Marginal difference | 0.05-0.10 | Proceed with caution, document |
| Large degradation | >0.10 | Investigate before continuing |

**Outputs**:

- `outputs/phase4a/baseline/run_*/detections.geojson`
- `outputs/phase4a/pro_baseline_metrics.json` — F1, precision, recall with bootstrapped CIs
- `outputs/phase4a/transfer_baseline_comparison.json` — Δ F1 vs Flash baseline

**Gaps to fill before execution**:

1. Phase 4 validation manifest (20-tile stratified subset)
2. Transfer comparison analysis script

---

### Phase 4b: OFAT Sensitivity Testing

**Purpose**: Test whether Flash-optimal parameters are also optimal for Pro.

**Prerequisites**: Phase 4a baseline confirms reasonable transfer (Δ F1 ≤ 0.10).

**Design**: For each core factor, test 1-2 alternative levels while holding others at Flash-optimal.

| Factor | Flash-Optimal | Alternatives to Test | Rationale |
|--------|---------------|----------------------|-----------|
| **M/E** | (from Phase 2a) | 1-2 adjacent M/E levels | Does Pro prefer more/less text? |
| **H5** | (from Phase 2d) | 1-2 adjacent H5 levels | Does Pro need different negative treatment? |
| **T** | (from Phase 2b) | ±0.3 temperatures | Does Pro prefer different temperature? |
| **O** | (from Phase 2e) | 1-2 alternative orderings | Does ordering effect transfer? |

**Decision rule**: Flag factor if alternative outperforms Flash-optimal by ≥0.03 F1 AND 95% CI excludes zero.

**Execution pattern** (example for M/E factor):

```bash
# Test adjacent M/E level (e.g., if Flash-optimal is brief-text-image, test verbose-text-image)
for run in {1..10}; do
    python scripts/4_detect_mounds_batch.py \
        --config prompts/configs/detect_{alternative_me}.json \
        --manifest inputs/tiles/phase4_validation_manifest.json \
        --output-dir outputs/phase4b/ofat_me_alt1/run_${run} \
        --model gemini-3-pro \
        --temperature ${optimal_T} \
        --ordering ${optimal_ordering} \
        --workers 1
done
```

**API calls**: ~3-4 factors × 2 alternatives × K=10 runs × 20 tiles = **~1,200 calls**

**Estimated cost**: ~$36

**Analysis workflow**:

For each factor tested:

1. Compute F1 at alternative level (bootstrapped 95% CI)
2. Compare to Pro-at-Flash-optimal (from Phase 4a)
3. Report: Δ F1 = F1_alternative - F1_Flash_optimal with 95% CI
4. Decision: Δ F1 ≥ 0.03 AND CI excludes 0 → flag factor for adjustment

**Outputs**:

- `outputs/phase4b/ofat_{factor}_{level}/run_*/detections.geojson`
- `outputs/phase4b/ofat_sensitivity_results.json` — Per-factor comparison table

**Factor-by-factor output format**:

```json
{
  "factors": [
    {
      "factor": "M/E",
      "flash_optimal": "brief-text-image",
      "alternatives_tested": ["verbose-text-image", "image-only"],
      "results": [
        {"level": "brief-text-image", "f1": 0.82, "ci": [0.78, 0.86], "is_baseline": true},
        {"level": "verbose-text-image", "f1": 0.80, "ci": [0.76, 0.84], "delta": -0.02, "flagged": false},
        {"level": "image-only", "f1": 0.75, "ci": [0.71, 0.79], "delta": -0.07, "flagged": false}
      ],
      "recommendation": "Keep Flash-optimal (brief-text-image)"
    }
  ],
  "transfer_rate": 1.0,
  "classification": "full_transfer"
}
```

**Gaps to fill before execution**:

1. Determine which alternative levels to test (depends on Phase 2 results)
2. OFAT sensitivity analysis script

---

### Phase 4c: Voting Analysis

**Purpose**: Verify that Flash-optimal voting threshold transfers to Pro.

**Data source**: Runs from Phase 4a-4b (no additional API calls required).

**Analysis workflow**:

1. Pool all Phase 4a-4b runs into voting analysis
2. Compute voting curves at varying thresholds (T=1, 2, 3, ..., N)
3. Identify Pro-optimal threshold
4. Compare to Flash-optimal threshold from Phase 3a
5. Flag if difference >10% relative

**Command pattern**:

```bash
# Threshold sweep on Phase 4 pooled data
python scripts/7_analyse_consensus.py \
    --pred outputs/phase4_pooled/merged_detections.geojson \
    --bounds inputs/vectors/bounds/phase4_validation_bounds.geojson \
    --template inputs/vectors/references/mounds-reference.geojson \
    --threshold-sweep \
    --output outputs/phase4c/threshold_comparison.json
```

**Decision rule**:

| Outcome | Threshold Difference | Action |
|---------|---------------------|--------|
| Threshold transfers | ≤10% relative | Use Flash-optimal threshold |
| Minor difference | 10-20% relative | Document, consider Pro-adjusted |
| Large difference | >20% relative | Run Phase 4d refinement |

**Outputs**:

- `outputs/phase4c/threshold_comparison.json` — Pro vs Flash threshold analysis
- `outputs/phase4c/voting_curves.json` — Threshold sweep data

**Gaps to fill before execution**:

1. Threshold comparison logic in analysis script

---

### Phase 4d: Refinement (Conditional)

**Trigger**: Only if Phase 4b identifies factors needing adjustment OR Phase 4c shows >20% threshold difference.

**Design**: Targeted follow-up testing.

**Scenario A: Factor adjustment needed**

If Phase 4b flagged 1-2 factors:

- Test one additional level in the indicated direction
- Confirm the Pro-optimal level

**Scenario B: Voting threshold differs**

If Phase 4c shows >20% threshold difference:

- Run N=30 passes at Pro-adjusted config for stability verification
- Compare voting curves at extended pool size

**API calls**: 0-200 calls (conditional)

**Estimated cost**: $0-6 (conditional)

**Outputs**:

- `outputs/phase4d/refinement_results.json` — Pro-specific adjustments (if any)

---

## Statistical Methods (Phase 4-Specific)

### Comparison to Phase 2-3 Methods

| Aspect | Phase 2-3 | Phase 4 |
|--------|-----------|---------|
| Design | Multi-level factorial | OFAT sensitivity |
| Comparisons | Multiple pairwise (per factor) | Single pairwise (Pro vs Flash-optimal) |
| FDR correction | Benjamini-Hochberg (q=0.05) | Not needed (sequential single comparisons) |
| Bootstrap CIs | Yes (1000 iterations, tile resampling) | Yes (same methodology) |
| Decision threshold | Effect size + CI excludes zero | Specific thresholds (0.03 or 0.05 F1) |

### Why No FDR Correction

Phase 4 uses OFAT (One-Factor-At-a-Time) sensitivity testing, not a full factorial design:

- Each factor is tested independently against the baseline
- No multiple pairwise comparisons within a single factor
- Sequential decisions: if Factor A needs adjustment, test A first before B
- Benjamini-Hochberg is designed for simultaneous multiple comparisons, not sequential OFAT

### Decision Thresholds (from preregistration)

| Sub-phase | Threshold | Interpretation |
|-----------|-----------|----------------|
| 4a Baseline | \|Δ F1\| ≤ 0.05 | Transfer success, proceed |
| 4a Baseline | \|Δ F1\| > 0.10 | Large degradation, investigate |
| 4b OFAT | Δ F1 ≥ 0.03 AND CI excludes 0 | Flag factor for adjustment |
| 4c Voting | \|T_Pro - T_Flash\| > 10% relative | Flag threshold difference |

### Transfer Classification

| Outcome | Criteria | Interpretation |
|---------|----------|----------------|
| **Full transfer** | All factors within 0.03 F1 | Report unified Flash/Pro recommendation |
| **Partial transfer** | 1-2 factors differ by ≥0.03 F1 | Report Flash-optimal with Pro adjustments |
| **Poor transfer** | ≥3 factors differ by ≥0.03 F1 | Consider Pro-specific optimisation (out of scope) |

---

## Gap Analysis Summary

### What Exists

| Component | Path | Status |
|-----------|------|--------|
| Detection script | `scripts/4_detect_mounds_batch.py` | Has `--model` flag |
| Consensus analysis | `scripts/7_analyse_consensus.py` | Has threshold sweep |
| Bootstrap CIs | `scripts/lib_advanced_metrics.py` | `bootstrap_ci()` function |
| Effect size CIs | `scripts/lib_advanced_metrics.py` | `bootstrap_effect_size_ci()` function |

### Missing Scripts

| Gap | Priority | Complexity | Description |
|-----|----------|------------|-------------|
| `select_tiles_phase4.py` | High | Low | Select 20-tile stratified subset |
| `analyse_phase4_transfer.py` | High | Medium | Pro vs Flash comparison with decision logic |

### Missing Infrastructure

| Gap | Priority | Description |
|-----|----------|-------------|
| Phase 4 validation manifest | High | `inputs/tiles/phase4_validation_manifest.json` |
| Phase 4 validation bounds | High | `inputs/vectors/bounds/phase4_validation_bounds.geojson` |

### Missing Study YAML

| Gap | Priority | Template basis |
|-----|----------|----------------|
| `studies/phase4-transfer.yaml` | High | Phase 3a YAML structure |

### Missing Configs

None required — model (Flash vs Pro) is a runtime parameter.

---

## Resource Planning

### API Calls per Sub-Phase

| Sub-phase | Cells | Calls/Cell | Total Calls | Est. Cost |
|-----------|-------|------------|-------------|-----------|
| 4a (Baseline) | 1 | 200 | 200 | ~$6 |
| 4b (OFAT) | ~8 | ~150 | ~1,200 | ~$36 |
| 4c (Voting) | — | 0 | 0 | $0 |
| 4d (Refinement) | 0-1 | ~200 | 0-200 | $0-6 |
| **Total** | **~10** | — | **~1,400-1,600** | **~$42-48** |

**Cost basis**: Gemini 3 Pro at ~$0.03/call (verify pricing at execution time).

**Note**: If Pro shows dramatic superiority (≥20% higher F1 at comparable cost, OR comparable F1 at ≤50% cost), budget for extended Pro testing (~$50-80 additional).

### Time Estimates

| Sub-phase | Est. Duration | Notes |
|-----------|---------------|-------|
| Phase 4a | 1-2 hours | 10 runs, 20 tiles each |
| Phase 4b | 4-6 hours | ~8 cells × ~1 hour/cell |
| Phase 4c | 30 min | Analysis only |
| Phase 4d | 0-2 hours | Conditional |
| **Total** | **6-10 hours** | Plus analysis time |

---

## Scaffolding Recommendations

### Can Build NOW (Before Phase 2-3 Complete)

| Priority | Item | Rationale |
|----------|------|-----------|
| 1 | `select_tiles_phase4.py` | Stratified selection independent of Phase 2-3 results |
| 2 | `tests/test_select_tiles_phase4.py` | Unit tests for selection logic |
| 3 | Phase 4 study YAML template | Structure known; placeholders for params |
| 4 | Transfer decision logic functions | Pure logic, unit testable |
| 5 | `tests/test_analyse_phase4_transfer.py` | Decision logic tests |

### Must WAIT for Phase 2-3 Results

| Item | Dependency |
|------|------------|
| Actual Phase 4 execution | Flash-optimal config from Phase 2e |
| YAML `carried_forward` values | Phase 2-3 optimal M/E, T, library, H5, ordering |
| Voting threshold comparison baseline | Phase 3a optimal (N, T) for Flash |
| OFAT alternative level selection | Depends on which levels are adjacent to Phase 2 optimal |

---

## Testing Plan

### Tier 1 Tests (Unit Tests)

**`tests/test_select_tiles_phase4.py`**:

| Test | Purpose |
|------|---------|
| `test_preserves_density_distribution` | Subset maintains empty/sparse/dense ratio |
| `test_returns_20_tiles` | Exactly 20 tiles returned |
| `test_all_tiles_from_holdout` | All tiles in 60-tile holdout set |
| `test_reproducible_with_seed` | Same seed → identical selection |
| `test_different_seeds_differ` | Different seeds → different subsets |

**`tests/test_analyse_phase4_transfer.py`**:

| Test | Purpose |
|------|---------|
| `test_full_transfer_within_threshold` | Δ F1 ≤ 0.05 → transfer success |
| `test_degradation_flag_beyond_threshold` | Δ F1 > 0.10 → flag investigation |
| `test_partial_transfer_classification` | 1-2 factors adjusted → partial |
| `test_poor_transfer_classification` | ≥3 factors adjusted → poor transfer |
| `test_flag_factor_exceeds_threshold` | Δ F1 ≥ 0.03 → flag factor |
| `test_no_flag_below_threshold` | Δ F1 < 0.03 → no flag |
| `test_ci_excludes_zero_required` | CI must exclude zero to flag |
| `test_voting_threshold_difference` | Relative threshold comparison |

### Tier 2 Tests (Integration Tests)

**`tests/test_integration_phase4.py`**:

| Test | Purpose |
|------|---------|
| `test_study_yaml_loads` | Phase 4 YAML parses correctly |
| `test_subset_manifest_valid` | Generated manifest works with detection script |
| `test_transfer_workflow_end_to_end` | Full 4a→4b→4c flow with fixtures |

---

## Verification Checklist

After completing Phase 4 simulation scaffolding:

- [ ] `docs/methodology/preregistration/phase4-execution-simulation.md` follows Phase 1-3 template
- [ ] Statistical methods section documents OFAT vs factorial differences
- [ ] Decision thresholds (0.03, 0.05, 0.10) documented clearly
- [ ] Gap analysis categorised (scripts, YAML, infrastructure)
- [ ] Testing plan follows tier1/tier2 pattern
- [ ] Scaffolding recommendations prioritised (NOW vs LATER)
- [ ] Resource estimates account for 10x Pro pricing
- [ ] Dependencies on Phase 2-3 clearly documented
- [ ] `pytest tests/ -m tier1` passes (including new tests)
- [ ] Study YAML parses without error

---

*Simulation created: 2026-01-22*
