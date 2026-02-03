# Preregistration Execution Checklist

**Purpose**: Working checklist for tracking preregistration tasks. This file can be updated after the preregistration document is lodged.

**Associated preregistration**: `preregistration.md` v4.7

**Last updated**: 2026-02-04

---

## Pre-Registration Tasks

*Complete before lodging preregistration on OSF.*

- [x] Finalise hypothesis list and predictions (H1-H15 documented)
- [x] Specify exact test tile IDs (60 tiles in `inputs/tiles/validation_manifest.json`)
- [x] Specify primary outcome: Overall F1 at 20m spatial tolerance
- [x] Specify success threshold: F1 ≥ 0.85 triggers H11 tile size testing
- [x] Document few-shot library composition (Section 8.4)
- [x] Document prompt text for all conditions (Appendix)
- [x] Document prompt variants for H9 (Section 8.3.2-8.3.3)
- [x] Specify random seeds for tile selection (documented in `inputs/tiles/tile_selection_metadata.json`)

---

## Pre-Evaluation Tasks

*Complete after lodging but before running any holdout evaluation.*

- [x] Calibrate `thinking_level` parameter (2026-01-15)
  - Pilot tested minimal, low, high across 20 tiles × K=10
  - Result: minimal achieves equivalent F1 to high at 1/3 latency
  - All Gemini configs updated to `thinking_level: minimal`
  - See preregistration.md §8.9 for full results

- [x] Document hard negative examples (for H5) (2026-02-01)
  - FP/FN analysis in `outputs/phase1-library/fp-fn-register.md`
  - 4 hard positives + 4 hard negatives selected (Decision 4 in decisions-log)
  - Recorded in library composition files and MANIFEST.md
- [x] Commit analysis code to repository (2026-01-31)
  - `scripts/run_study.py`
  - `scripts/lib_*.py` modules
  - Evaluation and metrics code
- [x] Submit to OSF Registries (2026-01-31)
  - Uploaded `preregistration.md` and companion documents
  - No embargo set
- [x] Obtain timestamp confirmation (2026-01-31)
  - OSF registration URL: <https://osf.io/tybgq/overview>
  - Timestamp: 2026-01-31 23:54 UTC

---

## Registration Details

*Fill in after lodging.*

| Field | Value |
|-------|-------|
| OSF Registration URL | <https://osf.io/tybgq/overview> |
| OSF Project URL | <https://osf.io/h9x4g> |
| Registration timestamp | 2026-01-31 23:54 UTC |
| DOI (if assigned) | |
| Embargo end date (if any) | None |

---

## Post-Registration Notes

*Document any deviations or clarifications needed during execution.*
*Detailed entries in `../protocol-errata.md`.*

| Date | Item | Note |
|------|------|------|
| 2026-01-31 | E1: Stale date in OSF README | Correction — cosmetic, no protocol impact |
| 2026-02-01 | E2: Missing execution fields in Phase 1 config | Correction — added model/temperature/instruction fields to `library_pure-positive-canon.json` |
| 2026-02-01 | E3: SDK migration for ThinkingConfig | Correction — deprecated SDK didn't support ThinkingConfig; migrated to google-genai SDK |
| 2026-02-01 | E4: Tile bounds Y-axis inversion | Correction — bounds generation misinterpreted metadata, shifted bounds ~2565m south |
| 2026-02-01 | E5: Evaluation pipeline reference path bugs | Correction — wrong reference directory, column name mismatch in merged GeoJSON |
| 2026-02-01 | E6: Pipeline contract validation | Correction — added assertions, bounds validation, and 7 integration tests to prevent E4-E5 recurrence |

---

## Execution Log

*Track when evaluation phases are run.*

| Phase | Start Date | End Date | Notes |
|-------|------------|----------|-------|
| Phase 1: Library + Text | 2026-02-01 | 2026-02-03 | Detection passes complete (F1=0.489 baseline); hard examples selected (4 HP + 4 HN); two-stage prompts reviewed and updated |
| Phase 2a: H1 M/E Level | | | |
| Phase 2b: H7 Temperature | | | |
| Phase 2c: H8 Library Composition | | | |
| Phase 2d: H5 Negative Text | | | |
| Phase 2e: H4 Ordering | | | |
| Phase 3a: H3 N=30 Extension | | | |
| Phase 3b: H9 Diversity | | | |
| Phase 3c: H2 Two-Stage | | | |
| Phase 3d: Triggered Exploratory (H4b, M/E-sensitivity, HN-only) | | | |
| Phase 4: H6 Pro Transfer | | | |
| Phase 5: Exploratory (H10-H15) | | | |

---

*This checklist is a working document separate from the frozen preregistration.*
