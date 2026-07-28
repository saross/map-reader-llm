# Phase 2 Remaining Tasks

> **NOT PART OF THE OSF LODGEMENT.** The registration comprises exactly three
> documents, all in `osf/` (`osf/README.md:3,9-11`); this file is not one of
> them. It is a working document: pre-lodgement content here fed into writing
> the registration but does not license a "the preregistration says" claim,
> and post-lodgement content is operational, not registered. Cite
> `osf/preregistration.md` for registered content. Banner added 2026-07-28
> (D17 audit, structural fix).

**Created**: 2026-01-21
**Status**: Phase 1 complete; prerequisites resolved

This document tracks remaining tasks, dependencies, and decisions required for Phase 2 execution.

---

## Pre-Phase 2 Prerequisites

These tasks depend on Phase 1 completion.

| Task | Blocker | Status | Notes |
|------|---------|--------|-------|
| Complete Phase 1 library construction | None | ☑ Done (2026-02-01) | F1=0.489 baseline established |
| Create hard example symlinks (05-08 HP, 11-14 HN) | Phase 1 results | ☑ Done (2026-02-01) | Using neutral-naming paths in `inputs/examples/neutral-naming/` |
| Assess Scale-16/32 feasibility | Phase 1 HP/HN pool size | ☑ Done (2026-02-03) | Deferred — documented as E11 in protocol-errata |
| Update library configs with actual hard examples | Phase 1 extraction | ☑ Done (2026-02-01) | Configs reference actual files |

---

## Between Sub-Phase Decisions

After each sub-phase completes, update the YAML files for subsequent phases.

| After | Decision Required | Files to Update | Status |
|-------|-------------------|-----------------|--------|
| Phase 2a | Determine optimal M/E | `phase2b-2e` YAMLs: `carried_forward.optimal_me_config` | ☐ Pending |
| Phase 2b | Determine optimal temperature | `phase2c-2e` YAMLs: `carried_forward.optimal_temperature` | ☐ Pending |
| Phase 2c | Determine optimal library | `phase2d-2e` YAMLs: `carried_forward.optimal_library` | ☐ Pending |
| Phase 2d | Determine optimal H5 treatment | `phase2e` YAML: `carried_forward.optimal_h5_treatment` | ☐ Pending |
| Phase 2e | Document final optimal config | Phase 3 preparation | ☐ Pending |

### Decision Rules (operational, declared in the Phase 2 study YAMLs — NOT preregistered)

> **Correction (2026-07-28, D17 audit FALSE-7)**: an earlier heading here read
> "(from preregistration)". None of the five rules below appears in any lodged
> document — the preregistration specifies **no** carry-forward selection or
> tie-break rules. These are operational rules adopted at execution time in
> the study YAMLs. This heading was the upstream source that made the
> "preregistered decision rule" attributions in the Phase 2b–2e carry-forward
> documents look legitimate.

- **2a → 2b**: Select M/E with highest mean F1. If tied (overlapping 95% CIs), prefer simpler (image-only > brief > verbose).
- **2b → 2c**: Select temperature with highest mean F1. If T=1.0 within 0.02 F1 of best, prefer T=1.0.
- **2c → 2d**: Select library with highest mean F1. If tied, prefer smaller library.
- **2d → 2e**: If H5 main effect significant, select best H5 level. If M/E×H5 interaction, select best at optimal M/E. If neither, use Minimal.
- **2e → Phase 3**: Select ordering with highest F1. If canonical-first within 0.02 of best, prefer canonical-first.

---

## Scripts Not Yet Written

| Script | Priority | When Needed | Notes |
|--------|----------|-------------|-------|
| Results collation (CSV aggregation) | Medium | After first sub-phase | Aggregate per-condition metrics |
| H4b exploratory (HP-first vs HN-first) | Low | Only if H4 significant | Triggered analysis |

---

## Configs That Cannot Be Created Yet

| Config | Depends On | Notes |
|--------|------------|-------|
| H5 variant configs with optimal library | Phase 2c result | May need to update library reference |
| Scale-16/32 with full HP/HN pool | Phase 1 extraction | Need ≥16 hard examples of each type |

---

## Pre-Execution Checklist

Run before each sub-phase:

- [ ] `python scripts/preflight_check.py --phase 2` passes
- [ ] All config files referenced in YAML exist
- [ ] `carried_forward` values updated from prior phase
- [ ] Sufficient API budget available
- [ ] Previous phase results backed up

---

## Completed Infrastructure (for reference)

- [x] `--temperature` CLI flag (`4_detect_mounds_batch.py` v4.3.0)
- [x] `--ordering` CLI flag with `canonical-first`, `canonical-last`, `random`
- [x] `--ordering-seed` for reproducible random ordering
- [x] Phase 2a-2e study YAML templates
- [x] `analyse_phase2_results.py` with bootstrapped CIs + FDR correction
- [x] Unit tests for ordering and FDR functions

---

*Last updated: 2026-02-04*
