# Phase 1 Remaining Tasks

**Created**: 2026-01-23
**Status**: Ready to execute

This document tracks the readiness status for Phase 1 (Library Construction).

---

## Completed Scaffolding

All scaffolding for Phase 1 has been completed:

| Item | File | Tests | Notes |
|------|------|-------|-------|
| Phase 1 runner script | `scripts/run_phase1.py` | 18 tests | Checkpoint/resume support |
| Pass merging script | `scripts/merge_passes.py` | 18 tests | Spatial clustering with vote counts |
| Pre-flight check script | `scripts/preflight_check.py` | — | All 15 checks pass |
| Study YAML | `studies/phase1-library.yaml` | — | Documents pipeline steps |
| Execution simulation | `docs/methodology/preregistration/phase1-execution-simulation.md` | — | Step-by-step walkthrough |

**Total tests**: 36 (all passing)

---

## Gap Analysis Resolution

The gap analysis from 2026-01-20 (`reports/phase1-simulation-gaps.md`) identified several issues. All have been resolved:

| Issue | Status | Resolution |
|-------|--------|------------|
| Path mismatch (`neutral/` vs `neutral-naming/`) | ✅ Resolved | Configs updated to use `neutral-naming/` |
| Missing `merge_passes.py` | ✅ Resolved | Script created with tests |
| Missing `preflight_check.py` | ✅ Resolved | Script created |
| Missing `phase1-library.yaml` | ✅ Resolved | YAML created |
| Missing `run_phase1.py` | ✅ Resolved | Script created with tests |

---

## Pre-Execution Checklist

Run before Phase 1 execution:

- [x] `scripts/run_phase1.py` exists and tested
- [x] `scripts/merge_passes.py` exists and tested
- [x] `scripts/preflight_check.py` exists
- [x] `studies/phase1-library.yaml` exists
- [x] All configs use `neutral-naming/` path
- [x] `python scripts/preflight_check.py --phase 1` passes (15/15)
- [x] `pytest tests/test_run_phase1.py tests/test_merge_passes.py` passes (36 tests)
- [ ] Verify API quota/budget sufficient (~100 calls, ~$0.30)

---

## Execution Command

```bash
# Dry run first
python scripts/run_phase1.py --dry-run

# Actual execution
python scripts/run_phase1.py

# Resume if interrupted
python scripts/run_phase1.py --resume
```

---

## Post-Execution Tasks

After Phase 1 completes:

| Task | Description | Status |
|------|-------------|--------|
| Review merged detections | Inspect `outputs/phase1-library/merged_detections.geojson` | ☐ Pending |
| Verify hard positive selection | Check `outputs/phase1-library/hard-positives/` | ☐ Pending |
| Verify hard negative selection | Check `outputs/phase1-library/hard-negatives/` | ☐ Pending |
| Create example symlinks | Link HP/HN crops to `inputs/examples/neutral-naming/example_05-14.png` | ☐ Pending |
| Update MANIFEST.md | Document provenance of new examples | ☐ Pending |
| Document in decisions-log.md | Record baseline metrics and selection rationale | ☐ Pending |
| Verify library configs load | Test `library_scale-8.json` etc. with new examples | ☐ Pending |

---

## Cost and Time Estimates

| Item | Estimate |
|------|----------|
| API calls | 100 (20 tiles × 5 passes) |
| Cost | ~$0.30 (Flash @ ~$0.003/call) |
| Time | ~15-20 minutes |

---

## Dependencies

Phase 1 has no dependencies on other phases — it can run immediately.

Phase 1 outputs (hard example library) are required by:
- Phase 2a-2e (all use library configs)
- Phase 3a, 3c, 3d (all use library configs)
- Phase 4 (uses optimal library from Phase 2c)

---

## Related Documents

- `phase1-execution-simulation.md` — Detailed step-by-step walkthrough
- `reports/phase1-simulation-gaps.md` — Historical gap analysis (all resolved)
- `studies/phase1-library.yaml` — Study definition
- `execution-plan.md` — Overall study execution plan
