# Priority Backfill Plan — 2026-04-22 Revision

**Revision**: supersedes `results/documentation-audit/priority-backfill.md`
(dated 2026-04-18). Several Tier 1 items from that plan have since been
closed by work that landed between 2026-04-19 and 2026-04-21, and the
CI-metadata registry plus errata E54 close a substantial infrastructure
gap that was not explicitly tracked in the prior plan.

**Constraint** (unchanged): no re-runs; all backfill uses existing
artefacts.

> **Post-recovery annotation (2026-05-03)** — the
> `55maps-text-high-generalisation` recovery (proposer recovery commit
> `731466d8`; full propagation through `e07dae37`) closed a previously
> unsurfaced backlog: 160 originally-failed tile-passes were 100 %
> recovered; downstream consensus / verifier cleanup / cost-manifest /
> evaluation / D-S / corrected-F1 / MCC / paired-permutation /
> attractor-pull all rebuilt against the post-recovery candidate set.
> Three new bugs surfaced and were fixed during the recovery (parser
> realtime-vs-batch asymmetry at `e3aef6fa`; D-S row-position at
> `a9e280a3`; `cost_manifest` cleanup-overwrites-meta at `7f05f529`).
> The parser fix in turn surfaced **3 outstanding recoveries** that
> are now backfill targets (none yet actioned as of 2026-05-03):
>
> - `outputs/55maps-image-generalisation/` (image HIGH)
> - `outputs/55maps-text-min-generalisation/` (text MIN)
> - `outputs/h11/gold-standard-v2/` (GS-v2)
>
> Per the parser-fix audit, these three runs collectively lost 163
> tiles to JSON-parse failures that the 3-tier repair would now
> recover. Tracked in `planning/paper-writeup-continuity.md` under
> "Pending before paper outline" (Session 83 closure).

---

## Status of prior Tier 1 items

| Prior item | Status | Closed by |
|---|---|---|
| Add pre-launch audit to the 2026-04-10 text run | Still open (retrospective run; retrospective post-run report exists at `configs/run-configs/55maps_text_generalisation_retrospective_post_run_report.md` but no retrospective pre-launch audit is yet filed) | — |
| Text-high cost harmonisation with min / image cohorts | **Closed** | 2026-04-19 re-run at `outputs/55maps-text-high-generalisation/` produced `cost_manifest.json` with `totals.cost_usd` = 69.60 (commit range `4e5c5e5a..`) |
| h11 paired proposer-vs-verifier test + post-run narrative | Still open (no statistical comparison computed; no unified narrative) | — |

---

## Status of prior Tier 2 items

| Prior item | Status |
|---|---|
| h8-v2 multi-buffer curves (30/40/50 m) | Still open |
| h10 multi-buffer curves + post-run narrative | Still open |
| h12-v2 multi-buffer curves + re-run of three-way null across buffers | Still open |

These are confirmatory; none is publication-blocking.

---

## Status of prior Tier 3 items

| Prior item | Status |
|---|---|
| Archive the `outputs/h11/*UNINTENDED-T1.0` runs | Still open |
| Mining-run READMEs under h10 / h11 | Still open |
| Phase 3c diversity study relevance decision | Still open |

---

## New items surfaced since 2026-04-18

These are items that the prior audit did not anticipate because the
work that raised them postdates 2026-04-18:

### N1. Dawid-Skene caveat on the image-run posterior

**Item**: the paper should cite the image-run D-S corrected F1 of 0.795
together with the Obs 273 caveat (structural inadequacy on the VLM-only
slice at any prior).

**Current state**: Obs 273 (`docs/notes/reflections/working-notes.md:12840`)
and the D-S v1 and v2 cross-tab artefacts are in place. The
`dawid-skene-results.json` file still records 0.7954 without a caveat
pointer. **Action**: add a caveat section to
`results/55maps-image-generalisation/dawid-skene/dawid-skene-results.md`
pointing to Obs 273 and the human-review corrected F1 as the preferred
lower-bound narrative. One paragraph; zero re-computation.

**Effort**: 15 minutes.

### N2. Paper methods wording for E54

**Item**: the paper's methods section needs the suggested E54 wording
embedded. The errata entry at
`docs/methodology/preregistration/protocol-errata.md:1695-1697` already
includes the recommended text: "Confidence intervals on primary F1,
precision, and recall are derived from 1 000-iteration tile-level
bootstrap resampling (preregistered Section 3.5, percentile method
2.5th / 97.5th). Post-hoc analyses — human-reviewed corrected F1
(single- and multi-buffer), subtype classification, and review-UI
calibration cross-tabs — use 10 000 iterations to tighten CIs on
narrow effect sizes; the resampling unit and percentile method are
unchanged."

**Action**: paste into paper methods section when revising.

**Effort**: 5 minutes; paper-side only.

### N3. Retrospective text-run pre-launch audit (still open)

**Item**: the 2026-04-10 text run has a retrospective post-run report
but no retrospective pre-launch audit. For symmetry with the other
three runs, a retrospective pre-launch audit would record the
configuration decisions that were made ad-hoc at the time.

**Action**: author a short retrospective pre-launch audit at
`configs/run-configs/55maps_text_generalisation_retrospective_pre_launch_audit.md`
mirroring the structure of the text-min / text-high / image audits;
flag all cells as "retrospective reconstruction" where appropriate.

**Effort**: 1-2 hours.

### N4. UNINTENDED h11 runs — formal exclusion

**Item**: `outputs/h11/consensus-384-UNINTENDED-T1.0/` and
`outputs/h11/single-pass-384-UNINTENDED-T1.0/` remain in the active
tree. Under the project's "archive, never delete" policy, these should
either be archived with an explanation or explicitly flagged in a
nearby README.

**Recommendation**: move to `archive/unintended-t1.0/` with an
accompanying README note referencing the decision context.

**Effort**: 30 minutes.

### N5. h11 proposer-vs-verifier paired test

**Item**: 12 sub-runs under `outputs/h11/` share a two-stage design but
no proposer-vs-verifier paired statistical test has been computed.

**Action**: run `scripts/pairwise_permutation_test.py` against the
`outputs/h11/proposer-verifier-384/` proposer and verified detection
files; write result to `results/h11-384-pv-diagnostic/proposer_vs_verifier.json`;
draft a short post-run narrative integrating the twelve sub-runs.

**Effort**: 4-6 hours.

---

## New items from the 2026-04-20/21 human-review day

These were generated during the work that closed the text-high cost
gap and produced the corrected-F1 analyses. None is a documentation
gap per se; they are operational notes for future sessions.

### O1. Subtype classification verification

**Artefact**: `results/gold-standard-subtype-classification/`
— headline weighted-F1 0.8873 at 50 m buffer (Obs 270).

**Status**: all deliverables present — `report.md`, confusion matrices
at 4×4 and 5×5, per-map confusion, per-class F1, kappa/MCC, consensus
threshold sweep, buffer sensitivity, bootstrap CIs (10 000 iterations
per E54), `run_manifest.json`. No backfill needed.

### O2. Human-review workflow artefacts

**Artefact**: `results/55maps-image-generalisation/human-review-multi-buffer.csv`
(557 rows; second review day) plus `human-review.csv` (first review
day). Both files are committed and referenced by the corrected-F1
and multi-buffer analyses.

**Status**: both present. If the paper cites the rate of review-UI
flips (Obs 268), cite the JSON at
`results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.json`.

---

## Ongoing standards (post-backfill)

Unchanged from the prior plan, restated with corrected citations:

For every future run:

1. Pre-launch audit at `configs/run-configs/{run}_pre_launch_audit.md`.
2. Post-run report at both `outputs/{run}/post_run_report.md` and
   `configs/run-configs/{run}_post_run_report.md` (publishable-launcher
   convention).
3. `cost_manifest.json` with `totals.cost_usd`, `totals.cache_hit_rate`,
   and per-stage breakdown.
4. `evaluation/evaluation.json` with F1/P/R at 20/30/40/50 m with
   bootstrap CIs (1 000 iterations, seed 42, tile-level resampling per
   protocol E54). The CI-metadata sidecar at
   `evaluation.metadata.json` is now a hard requirement per the
   `results/ci-metadata-registry.md` registry.
5. Paired permutation test for every planned comparator (10 000
   permutations for narrow-effect analyses; 1 000 for primary).
6. Dawid-Skene latent-truth correction **plus** Obs 273 caveat
   discussion when two-annotator identifiability applies.
7. Working-notes Observation when a finding merits the log.

---

## Schedule (suggested, not committed)

| Item | Dependency | Effort | Priority |
|---|---|---|---|
| N1 D-S caveat paragraph | none | 15 min | High (paper-adjacent) |
| N2 Paper methods E54 wording | paper revision session | 5 min | High (paper-adjacent) |
| N3 Retrospective pre-launch audit | none | 1-2 h | Medium |
| N4 UNINTENDED archive | none | 30 min | Medium (cleanup) |
| N5 h11 paired test + narrative | N4 | 4-6 h | Medium |
| T2 prior items (h8 / h10 / h12 multi-buffer curves) | none | 8-11 h | Low (confirmatory) |

**Cumulative estimated effort**: ~15-20 hours once N1, N2 are off the
pile.
