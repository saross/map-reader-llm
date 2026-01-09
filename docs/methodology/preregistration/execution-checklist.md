# Preregistration Execution Checklist

**Purpose**: Working checklist for tracking preregistration tasks. This file can be updated after the preregistration document is lodged.

**Associated preregistration**: `preregistration.md` v4.3.1

**Last updated**: 2026-01-09

---

## Pre-Registration Tasks

*Complete before lodging preregistration on OSF.*

- [x] Finalise hypothesis list and predictions (H1-H15 documented)
- [x] Specify exact test tile IDs (60 tiles in `inputs/tiles/holdout_manifest.json`)
- [x] Specify primary outcome: Overall F1 at 20m spatial tolerance
- [x] Specify success threshold: F1 ≥ 0.85 triggers H11 tile size testing
- [x] Document few-shot library composition (Section 8.4)
- [x] Document prompt text for all conditions (Appendix)
- [x] Document prompt variants for H9 (Section 8.3.2-8.3.3)
- [x] Specify random seeds for tile selection (documented in `inputs/tiles/tile_selection_metadata.json`)

---

## Pre-Evaluation Tasks

*Complete after lodging but before running any holdout evaluation.*

- [ ] Document hard negative examples (for H5)
  - Run FP analysis on training tiles
  - Select examples meeting ≥3/5 occurrence threshold
  - Record in library composition files
- [ ] Commit analysis code to repository
  - `scripts/run_study.py`
  - `scripts/lib_*.py` modules
  - Evaluation and metrics code
- [ ] Submit to OSF Registries
  - Upload `preregistration.md` and companion documents
  - Set embargo if needed
- [ ] Obtain timestamp confirmation
  - Record OSF registration URL
  - Record timestamp

---

## Registration Details

*Fill in after lodging.*

| Field | Value |
|-------|-------|
| OSF Registration URL | |
| Registration timestamp | |
| DOI (if assigned) | |
| Embargo end date (if any) | |

---

## Post-Registration Notes

*Document any deviations or clarifications needed during execution.*

| Date | Item | Note |
|------|------|------|
| | | |

---

## Execution Log

*Track when evaluation phases are run.*

| Phase | Start Date | End Date | Notes |
|-------|------------|----------|-------|
| Phase 1: Library + Text | | | |
| Phase 2a: Strand 1 | | | |
| Phase 2b: H5 Confirmatory | | | |
| Phase 2c: Strand 2 | | | |
| Phase 2d: Strand 3 (if triggered) | | | |
| Phase 3a: H3 N=30 Extension | | | |
| Phase 3b: H4 Ordering | | | |
| Phase 3c: H9 Diversity | | | |
| Phase 3d: H2 Two-Stage | | | |
| Phase 4: H6 Pro Transfer | | | |
| Phase 5: Exploratory | | | |

---

*This checklist is a working document separate from the frozen preregistration.*
