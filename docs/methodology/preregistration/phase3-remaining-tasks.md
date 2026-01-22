# Phase 3 Remaining Tasks

**Created**: 2026-01-22
**Status**: Scaffolding complete — awaiting Phase 2 results

This document tracks remaining tasks, dependencies, and decisions required for Phase 3 execution.

---

## Completed Scaffolding (2026-01-22)

These items were built in advance and are ready for use:

| Item | File | Notes |
|------|------|-------|
| H3 threshold sweep function | `scripts/7_analyse_consensus.py` | `analyse_threshold_sweep()` with `--threshold-sweep` CLI |
| H3 threshold sweep tests | `tests/test_threshold_sweep.py` | 17 unit tests |
| H2 candidate extraction | `scripts/extract_candidates.py` | Crops proposer detections for verifier |
| H2 extraction tests | `tests/test_extract_candidates.py` | 17 unit tests |
| Phase 3a study YAML | `studies/phase3a-h3-voting.yaml` | Template with PLACEHOLDER markers |
| Phase 3c study YAML | `studies/phase3c-h9-diversity.yaml` | Template with PLACEHOLDER markers |
| Phase 3d study YAML | `studies/phase3d-h2-twostage.yaml` | Template with PLACEHOLDER markers |
| Phase 3 YAML validation tests | `tests/test_phase2_configs.py` | 8 new tests for Phase 3 YAMLs |
| Statistical methods documentation | `docs/methodology/preregistration/decisions-log.md` | Decision 10: pseudo-p-values |

---

## Deferred Tasks (Require Phase 2 Results)

### High Priority — Blocking Phase 3 Execution

| Task | Depends On | Files to Create/Update | Status |
|------|------------|------------------------|--------|
| Update Phase 3a YAML with optimal params | Phase 2a-2e | `studies/phase3a-h3-voting.yaml` | ☐ Pending |
| Update Phase 3c YAML with optimal params | Phase 2a-2e | `studies/phase3c-h9-diversity.yaml` | ☐ Pending |
| Update Phase 3d YAML with optimal params | Phase 2a-2e | `studies/phase3d-h2-twostage.yaml` | ☐ Pending |
| Update `propose_brief.json` with optimal params | Phase 2a-2c | `prompts/configs/propose_brief.json` | ☐ Pending |
| Update `verify_brief.json` with optimal params | Phase 2a-2c | `prompts/configs/verify_brief.json` | ☐ Pending |

### Medium Priority — Required for H9 (Phase 3c)

| Task | Depends On | Files to Create | Status |
|------|------------|-----------------|--------|
| Create H9 text variant instruction v1 | Phase 2a (optimal M/E) | `prompts/system-instructions/detect_*_v1.md` | ☐ Pending |
| Create H9 text variant instruction v2 | Phase 2a (optimal M/E) | `prompts/system-instructions/detect_*_v2.md` | ☐ Pending |
| Create H9 text variant instruction v3 | Phase 2a (optimal M/E) | `prompts/system-instructions/detect_*_v3.md` | ☐ Pending |
| Create H9 text variant instruction v4 | Phase 2a (optimal M/E) | `prompts/system-instructions/detect_*_v4.md` | ☐ Pending |
| Create H9 text variant instruction v5 | Phase 2a (optimal M/E) | `prompts/system-instructions/detect_*_v5.md` | ☐ Pending |
| Create H9 diversity configs (4 configs) | Phase 2a-2c + text variants | `prompts/configs/detect_*_diverse_*.json` | ☐ Pending |

**Note**: The `*` in filenames depends on which M/E level is optimal from Phase 2a (e.g., `detect_brief-text-image_v1.md`).

---

## Phase 2 Parameters to Carry Forward

After Phase 2 completes, these values must be extracted and applied to Phase 3:

| Parameter | Source | Needed By |
|-----------|--------|-----------|
| `optimal_me_config` | Phase 2a analysis | 3a, 3c, 3d |
| `optimal_temperature` | Phase 2b analysis | 3a, 3c, 3d |
| `optimal_library` | Phase 2c analysis | 3a, 3c, 3d |
| `optimal_h5_treatment` | Phase 2d analysis | 3c, 3d |
| `optimal_ordering` | Phase 2e analysis | 3c |
| `optimal_n` | Phase 3a analysis | 3c, 3d |
| `optimal_threshold` | Phase 3a analysis | 3c, 3d |

---

## Pre-Execution Checklist

Run before Phase 3 execution:

- [ ] Phase 2 complete (all sub-phases 2a-2e)
- [ ] Phase 2 optimal parameters documented in `decisions-log.md`
- [ ] All PLACEHOLDER values in Phase 3 YAMLs replaced
- [ ] `propose_brief.json` updated with optimal parameters
- [ ] `verify_brief.json` updated with optimal parameters
- [ ] For Phase 3c: H9 text variant files created
- [ ] `python scripts/preflight_check.py` passes
- [ ] `pytest tests/ -m tier1` passes (186+ tests)

---

## Workflow After Phase 2

1. **Extract optimal parameters** from Phase 2 analysis reports
2. **Update Phase 3 YAMLs** — replace PLACEHOLDER markers with actual values
3. **Create H9 text variants** (if running Phase 3c)
4. **Run Phase 3a first** — determines optimal N, T for other phases
5. **Run Phase 3c, 3d in parallel** (both depend on Phase 3a results for N, T)
6. **Document results** in decisions-log.md

---

## Related Documents

- `phase3-execution-simulation.md` — Detailed execution simulation and gap analysis
- `phase2-remaining-tasks.md` — Phase 2 task tracking (complete when Phase 3 starts)
- `decisions-log.md` — Methodological decisions and optimal parameter choices
- `execution-plan.md` — Overall study execution plan
