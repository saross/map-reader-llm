# Results Documentation Audit Report

**Audit Date**: 2026-04-18  
**Scope**: All unarchived experimental runs (59 total)  
**Purpose**: Comprehensive assessment of statistical documentation, post-run reporting, and reproducibility artefacts across all research phases

---

## Deliverables

Three markdown files constitute the full audit:

### 1. [`results-audit-2026-04-18.md`](./results-audit-2026-04-18.md) — FULL AUDIT TABLE

**Content**: 
- Run-by-run breakdown table (59 runs across all eras)
- Detailed era-by-era analysis (Era 1 pilot/calibration vs Era 2 production)
- Per-run assessment of 8 deliverable types (F1+P+R, bootstrap CIs, paired tests, D-S, cost manifest, pre-launch audit, post-run report, working-notes observation)
- Cross-reference to working-notes observations
- Scope & applicability notes

**Length**: ~350 lines  
**Audience**: Replicators, statisticians, methodology reviewers

**Key Tables**:
- Main audit table (8 columns × 59 rows, color-coded ✅/❌/◐/—)
- Statistical completeness by axis (F1, CIs, paired tests, D-S, costs, audits, reports)
- Detailed run-by-run breakdown for major runs (h8–h12, retest, 55maps cohorts)
- Working-notes observation cross-reference

---

### 2. [`audit-summary.md`](./audit-summary.md) — EXECUTIVE SUMMARY

**Content**:
- Overview of two-era pattern (documentation cliff, then recovery)
- Coverage rates table (8 deliverables × 2 eras)
- Worst-documented runs list (5 runs with ≥3 gaps; with remediation path)
- Gold-standard examples (5 runs meeting/exceeding publication standards)
- Patterns in breakdown (by time period, research axis, deliverable type)
- Recommended backfill priority
- Historical lessons learned
- Stats at a glance (coverage gain, completeness rates)

**Length**: ~196 lines  
**Audience**: Project lead, paper authors, reviewers

**Key Insight**: Era 1 (late 2025) runs are statistically rigorous but narratively fragmented; Era 2 (April 2026) runs return to best practices with all deliverables.

---

### 3. [`priority-backfill.md`](./priority-backfill.md) — IMPLEMENTATION ROADMAP

**Content**:
- Three-tier backfill plan (publication-blocking, methodological support, archival decisions)
- Detailed action items for 9 runs requiring documentation work
- Implementation schedule (1–2 weeks, ~18–25 person-hours)
- Validation checklist
- Ongoing standards for future runs

**Length**: ~263 lines  
**Audience**: Implementers (data managers, analysts)

**Tier 1** (publication-blocking):
1. 55maps-generalisation: retroactive pre-launch audit
2. h11: integrated post-run narrative + proposer vs verifier test
3. 55maps-generalisation: cost harmonization

**Tier 2** (methodological support):
4–6. h8, h10, h12: multi-buffer curves + hypothesis retests

**Tier 3** (archival):
7–9. Archive decisions, mining-run documentation, exploratory flags

---

## How to Use This Audit

### For Paper Reviewers
Start with [`audit-summary.md`](./audit-summary.md):
- Skim "Overview" and "Coverage Rates by Deliverable Type"
- Review "Gold-Standard Examples" (runs meeting publication standards)
- Check "Patterns in Documentation Breakdown" for methodological concerns

Then review [`results-audit-2026-04-18.md`](./results-audit-2026-04-18.md):
- Look up runs cited in the manuscript in the main audit table
- Verify deliverables are marked ✅ (present) or note the gap
- Cross-reference to working-notes observations

### For Project Lead (Submission Timeline)
1. Read [`audit-summary.md`](./audit-summary.md) "Recommended Backfill Priority"
2. Review [`priority-backfill.md`](./priority-backfill.md) "Tier 1: Publication-Blocking"
3. Decide: which Tier 1 items are critical path? (suggest: all 3)
4. Track implementation schedule (Table, end of backfill document)

### For Replicators / Future Methods
Consult [`results-audit-2026-04-18.md`](./results-audit-2026-04-18.md):
- "Detailed Run-by-Run Analysis" section
- "Statistical Deliverable Coverage by Axis" (what was computed when)
- "Notes on Scope & Applicability" (edge cases, definitions)

### For Documentation Standards
See [`priority-backfill.md`](./priority-backfill.md) "Ongoing Standards (Post-Backfill)":
- Checklist of 5 requirements for all future runs
- Pre-launch audit template location
- Bootstrap CI protocol (1000 iterations, seed 42, tile-level resampling)

---

## Key Statistics

| Metric | Value |
|---|---|
| **Total runs audited** | 59 (44 Era 1, 4 Era 2 major, 11 validation) |
| **Runs with ≥7 deliverables** (gold-standard) | 5 (h10, h12, retest, 55maps-text-min, 55maps-image) |
| **Runs with complete F1+CIs+paired tests** | 5 |
| **Coverage improvement (Era 1 → Era 2)** | +85% median deliverables per run |
| **Worst-documented runs** | h11 (4–5 gaps), h8-v2 (4 gaps), h10 (3 gaps), 55maps-generalisation (3–4 gaps) |
| **Publication-ready runs** | 55maps-text-min, 55maps-image (8/8 deliverables each) |
| **Backfill effort** | ~18–25 person-hours over 1–2 weeks |

---

## Recommendations at a Glance

| Run | Action | Timeline | Effort |
|---|---|---|---|
| **55maps-generalisation** | Add pre-launch audit (retroactive) | By 2026-04-19 | 2–3h |
| **h11 two-stage** | Integrate + paired test | By 2026-04-21 | 4–6h |
| **h8-v2, h10, h12-v2** | Multi-buffer curves | By 2026-04-28 | 8–11h |
| **Archive cleanup** | Move UNINTENDED runs, flag mining runs | By 2026-04-30 | 1.5h |

**Blocking constraint**: None. All backfill uses existing artefacts (no re-runs required).

---

## Files Referenced

- Main project audit: **this directory** (`results/documentation-audit/`)
- Raw results: `results/`, `outputs/` (all subdirectories)
- Working notes: `docs/notes/reflections/working-notes.md`
- Preregistration: `docs/methodology/preregistration/analysis-summary.md`, `hypothesis-tracking.md`
- Run configs: `configs/run-configs/`

---

## Questions?

Refer to the full [`results-audit-2026-04-18.md`](./results-audit-2026-04-18.md) for:
- Detailed deliverable-by-deliverable assessment (sections: "Statistical Deliverable Coverage by Axis")
- Working-notes cross-reference table
- Scope clarifications (what counts as a "run", era definitions, archive policy)

