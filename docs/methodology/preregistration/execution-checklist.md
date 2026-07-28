# Preregistration Execution Checklist

> **NOT PART OF THE OSF LODGEMENT.** The registration comprises exactly three
> documents, all in `osf/` (`osf/README.md:3,9-11`); this file is not one of
> them. It is a working document: pre-lodgement content here fed into writing
> the registration but does not license a "the preregistration says" claim,
> and post-lodgement content is operational, not registered. Cite
> `osf/preregistration.md` for registered content. Banner added 2026-07-28
> (D17 audit, structural fix).

**Purpose**: Working checklist for tracking preregistration tasks. This file can be updated after the preregistration document is lodged.

**Associated preregistration**: `preregistration.md` v4.7

**Last updated**: 2026-03-12

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
  - Timestamp: 2026-01-31 12:54:09 UTC (23:54 AEDT; an earlier entry here
    mislabelled the local time as UTC — corrected 2026-07-28 against the OSF
    API `date_registered` field)

---

## Registration Details

*Fill in after lodging.*

| Field | Value |
|-------|-------|
| OSF Registration URL | <https://osf.io/tybgq/overview> |
| OSF Project URL | <https://osf.io/h9x4g> |
| Registration timestamp | 2026-01-31 12:54:09 UTC (23:54 AEDT; corrected 2026-07-28 — see above) |
| DOI (if assigned) | |
| Embargo end date (if any) | OSF API records `embargo_end_date: 2026-06-30` (now public); an earlier entry here said "None" — PI to confirm which is right |

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
| 2026-02-05 | E17: Passes multiplier correction | Correction — execution plan and all Phase 2 YAMLs contained erroneous N=5 passes; corrected to single-pass per §3.8 |
| 2026-02-05 | E18: Config naming clarification | Clarification — unsuffixed configs are H5=Minimal variant; `_minimal` suffix omitted by convention |
| 2026-02-05 | D15: run_phase2.py replaces run_study.py | New OFAT runner for Phase 2; run_study.py archived to archive/deprecated-scripts/ |
| 2026-02-05 | E19: Validation bounds from wrong manifest | Correction — bounds generated from calibration (20 tiles) instead of validation (60 tiles) |
| 2026-02-05 | E20: Standardised "holdout" → "validation" | Clarification — internal naming standardised to "validation" throughout |
| 2026-02-05 | E21: Stale passes parameter in analysis | Correction — removed pre-E17 remnant; fixed file discovery for extensionless detection files |
| 2026-02-05 | E22: Per-run evaluation architecture | Correction — was merging all runs (10× inflation); now computes F1 per run independently |
| 2026-02-05 | E23: Enhanced API metadata capture | Correction — citation metadata, prompt block reason, prompt safety ratings now captured |
| 2026-02-05 | E24: Dry-run checkpoint corruption | Correction — dry runs were writing to checkpoint; fixed with dry-run guard |

---

## Execution Log

*Track when evaluation phases are run.*

| Phase | Start Date | End Date | Notes |
|-------|------------|----------|-------|
| Phase 1: Library + Text | 2026-02-01 | 2026-02-03 | Detection passes complete (F1=0.489 baseline); hard examples selected (4 HP + 4 HN); two-stage prompts reviewed and updated |
| Phase 2a: H1 M/E Level | 2026-02-05 | 2026-02-06 | Infrastructure built; sanity checks passed (3 runs, F1 0.36–0.44); analysis script fixed (E21–E22); metadata capture enhanced (E23); dry-run bug fixed (E24); K=10 runs complete; surprising result — text-only brief-text (F1=0.5425) outperformed all image-using conditions; dual-track carry-forward established (Decision 16) |
| Phase 2b: H7 Temperature | 2026-02-07 | 2026-02-08 | Dual-track: Track 1 (brief-text-image), Track 2 (brief-text); 5 temperatures × K=10 per track; T=0.0 optimal both tracks |
| Phase 2c: H8 Library Composition | 2026-02-08 | 2026-02-09 | Track 1 only (library composition is visual; text-only conditions collapse to identical prompts); plus-hp library optimal (F1=0.609) |
| Phase 2d: H5 Negative Text | 2026-02-09 | 2026-02-12 | Dual-track OFAT (Decision 17, E28): Track 1 brief-text-image + plus-hp, Track 2 brief-text text-only; H5=minimal optimal both tracks |
| Phase 2e: H4 Ordering | 2026-02-12 | 2026-02-12 | Single-track (image-using only; text-only has nothing to reorder); 4 conditions × K=10; no significant effect after FDR correction; retrospective carry-forward 2026-03-09 |
| Phase 3a: H3 N=30 Extension | 2026-02-12 | 2026-03-07 | 2×2×4 full analysis (dual-track, two thinking levels, four spatial tolerances); consensus voting improves F1 across all conditions |
| Phase 3b: H9 Diversity | 2026-03-07 | 2026-03-08 | Implicit testing via Phase 3a parameter variation; confirmed null result — prompt/parameter diversity does not improve consensus |
| Phase 3c: H2 Two-Stage | 2026-03-08 | 2026-03-09 | Pilot: adversarial verifier improves F1 by +0.086 to +0.138 vs single-stage baseline; GO for full experiment |
| Phase 3d: Triggered Exploratory | 2026-03-09 | 2026-03-11 | Pilot extensions (cross-modal union recall=0.835); verifier experiments A–D (max ΔF1=+0.011, perceptual limit); HIGH-thinking verifier (negative); Experiment E text proposer ablation (negative — baseline at capability frontier) |
| Phase 4: H6 Pro Transfer | | | |
| Phase 5: Exploratory (H10-H15) | | | |

---

*This checklist is a working document separate from the frozen preregistration.*
