# Phase 4 Remaining Tasks

> **NOT PART OF THE OSF LODGEMENT.** The registration comprises exactly three
> documents, all in `osf/` (`osf/README.md:3,9-11`); this file is not one of
> them. It is a working document: pre-lodgement content here fed into writing
> the registration but does not license a "the preregistration says" claim,
> and post-lodgement content is operational, not registered. Cite
> `osf/preregistration.md` for registered content. Banner added 2026-07-28
> (D17 audit, structural fix).

**Created**: 2026-01-23
**Status**: Scaffolding complete — awaiting Phase 2-3 results

This document tracks remaining tasks, dependencies, and decisions required for Phase 4 (H6: Flash→Pro Transfer Testing) execution.

---

## Completed Scaffolding (2026-01-23)

These items were built in advance and are ready for use:

| Item | File | Notes |
|------|------|-------|
| Execution simulation document | `docs/methodology/preregistration/phase4-execution-simulation.md` | Comprehensive walkthrough following Phase 1-3 template |
| Stratified tile selection script | `scripts/select_tiles_phase4.py` | Selects 20-tile subset from 60 holdout, preserves density distribution |
| Tile selection tests | `tests/test_select_tiles_phase4.py` | 13 unit tests |
| Transfer decision logic | `scripts/lib_phase4_transfer.py` | Baseline, factor sensitivity, voting threshold evaluation |
| Transfer decision tests | `tests/test_analyse_phase4_transfer.py` | 25 unit tests |
| Phase 4 study YAML | `studies/phase4-transfer.yaml` | Template with PLACEHOLDER markers |
| Integration tests | `tests/test_integration_phase4.py` | 13 integration tests covering end-to-end workflow |

**Total new tests**: 51

---

## Deferred Tasks (Require Phase 2-3 Results)

### High Priority — Blocking Phase 4 Execution

| Task | Depends On | Files to Create/Update | Status |
|------|------------|------------------------|--------|
| Generate Phase 4 validation manifest | Holdout manifest exists | `inputs/tiles/phase4_validation_manifest.json` | ☐ Pending |
| Generate Phase 4 validation bounds | Holdout bounds exists | `inputs/vectors/bounds/phase4_validation_bounds.geojson` | ☐ Pending |
| Update Phase 4 YAML with optimal params | Phase 2a-2e, 3a | `studies/phase4-transfer.yaml` | ☐ Pending |
| Create `analyse_phase4_transfer.py` | Output structure known | `scripts/analyse_phase4_transfer.py` | ☐ Pending |

### Medium Priority — Required for OFAT Testing (Phase 4b)

| Task | Depends On | Description | Status |
|------|------------|-------------|--------|
| Identify OFAT alternative levels for M/E | Phase 2a optimal | 1-2 adjacent M/E levels to test | ☐ Pending |
| Identify OFAT alternative levels for H5 | Phase 2d optimal | 1-2 adjacent H5 levels to test | ☐ Pending |
| Identify OFAT alternative temperatures | Phase 2b optimal | ±0.3 from optimal temperature | ☐ Pending |
| Identify OFAT alternative orderings | Phase 2e optimal | 1-2 alternative orderings to test | ☐ Pending |

---

## Phase 2-3 Parameters to Carry Forward

After Phase 2-3 completes, these values must be extracted and applied to Phase 4:

| Parameter | Source | YAML Field |
|-----------|--------|------------|
| `optimal_me_config` | Phase 2a analysis | `carried_forward.optimal_me_config` |
| `optimal_me_instruction` | Phase 2a analysis | `carried_forward.optimal_me_instruction` |
| `optimal_temperature` | Phase 2b analysis | `carried_forward.optimal_temperature` |
| `optimal_library` | Phase 2c analysis | `carried_forward.optimal_library` |
| `optimal_h5_level` | Phase 2d analysis | `carried_forward.optimal_h5_level` |
| `optimal_ordering` | Phase 2e analysis | `carried_forward.optimal_ordering` |
| `flash_optimal_n` | Phase 3a analysis | `carried_forward.flash_optimal_n` |
| `flash_optimal_threshold` | Phase 3a analysis | `carried_forward.flash_optimal_threshold` |

---

## Decision Thresholds (mixed provenance — see note)

> **Correction (2026-07-28, D17 audit U3)**: an earlier heading here read
> "(From Preregistration)". Only three of the five thresholds are registered —
> ≥0.03 F1 (`osf/preregistration.md:677`, *without* the CI condition, which was
> added at implementation), >10 % relative (`:683`), and >20 % (`:689`). The
> 0.05 transfer-success and 0.10 investigate thresholds are operational
> additions with no registered source.

These thresholds are already implemented in `lib_phase4_transfer.py`:

| Sub-phase | Threshold | Constant | Interpretation |
|-----------|-----------|----------|----------------|
| 4a Baseline | \|Δ F1\| ≤ 0.05 | `BASELINE_TRANSFER_THRESHOLD` | Transfer success, proceed |
| 4a Baseline | \|Δ F1\| > 0.10 | `BASELINE_INVESTIGATE_THRESHOLD` | Large degradation, investigate |
| 4b OFAT | Δ F1 ≥ 0.03 AND CI excludes 0 | `FACTOR_ADJUSTMENT_THRESHOLD` | Flag factor for adjustment |
| 4c Voting | >10% relative difference | `VOTING_THRESHOLD_DIFFERENCE` | Flag threshold difference |
| 4c Voting | >20% relative difference | `VOTING_EXTENDED_TEST_THRESHOLD` | Run extended N=30 test |

---

## Pre-Execution Checklist

Run before Phase 4 execution:

- [ ] Phase 2 complete (all sub-phases 2a-2e)
- [ ] Phase 3a complete (optimal N, T for Flash)
- [ ] Phase 2-3 optimal parameters documented in `decisions-log.md`
- [ ] All PLACEHOLDER values in Phase 4 YAML replaced
- [ ] Phase 4 validation manifest generated (`select_tiles_phase4.py`)
- [ ] OFAT alternative levels identified for each factor
- [ ] `analyse_phase4_transfer.py` script created
- [ ] `python scripts/preflight_check.py` passes
- [ ] `pytest tests/ -m tier1` passes

---

## Workflow After Phase 2-3

1. **Extract optimal parameters** from Phase 2-3 analysis reports
2. **Generate validation manifest** — run `python scripts/select_tiles_phase4.py --seed <SEED>`
3. **Update Phase 4 YAML** — replace PLACEHOLDER markers with actual values
4. **Identify OFAT alternatives** — determine which levels to test for each factor
5. **Create analysis script** — `analyse_phase4_transfer.py` for results processing
6. **Run Phase 4a** — baseline comparison (Pro at Flash-optimal)
7. **Decision gate**: If \|Δ F1\| > 0.10, investigate before continuing
8. **Run Phase 4b** — OFAT sensitivity testing for each factor
9. **Run Phase 4c** — voting threshold analysis (uses 4a/4b data)
10. **Run Phase 4d** — refinement if needed (conditional)
11. **Classify transfer outcome** — Full, Partial, or Poor transfer
12. **Document results** in decisions-log.md

---

## Transfer Outcome Classification

| Classification | Criteria | Action |
|----------------|----------|--------|
| Full transfer | 0 factors flagged | Report unified Flash/Pro recommendation |
| Partial transfer | 1-2 factors flagged | Report Flash-optimal with Pro adjustments |
| Poor transfer | ≥3 factors flagged | Note in limitations (Pro-specific optimisation out of scope) |

---

## Cost Estimates

| Sub-phase | API Calls | Est. Cost (Pro @ $0.03/call) |
|-----------|-----------|------------------------------|
| 4a (Baseline) | 200 | ~$6 |
| 4b (OFAT) | ~1,200 | ~$36 |
| 4c (Voting) | 0 | $0 |
| 4d (Refinement) | 0-200 | $0-6 |
| **Total** | **~1,400-1,600** | **~$42-48** |

---

## Related Documents

- `phase4-execution-simulation.md` — Detailed execution simulation and gap analysis
- `phase3-remaining-tasks.md` — Phase 3 task tracking
- `phase2-remaining-tasks.md` — Phase 2 task tracking
- `decisions-log.md` — Methodological decisions and optimal parameter choices
- `execution-plan.md` — Overall study execution plan (Phase 4 at lines 600-700)
