# Results Documentation Audit — Executive Summary

**Audit Date**: 2026-04-22
**Draft status**: awaiting verifier pass (see
`results/documentation-audit/draft/README.md`)
**Supersedes**: `results/documentation-audit/audit-summary.md` (dated
2026-04-18), which contained hallucinated cost figures, a conflation of
two distinct text-high runs, and a blanket "Obs 255" attribution.

> **Post-recovery annotation (2026-05-03)** — the
> `55maps-text-high-generalisation` row in the anchor table below cites
> the pre-recovery 2026-04-19 launch state (cost $69.60; F1 @50m
> 0.788; D-S 0.813; cache-hit 0.0 %). On 2026-05-02/03 the run was
> recovered: 160 of 160 originally-failed tile-passes recovered;
> verified detections 4,143 → 4,164; F1 raw @50m 0.7896 → 0.7920;
> F1 corrected @50m 0.8260 → 0.8273; D-S F1 0.8129 → 0.8142; total
> cost $69.60 → $126.81 (recovery overrun $57.10 + verifier cleanup
> $0.10 + FP-classify share $0.01). Cache-hit remains 0.0 %. The
> total measured-cost figure of $495.09 in §"What this means for the
> paper" should be read as $552.30 post-recovery ($364.70 image +
> $60.79 text-MIN + $126.81 text-HIGH). See
> `configs/run-configs/55maps_text_high_generalisation_post_run_report.md`
> "Recovery 2026-05-02/03" subsection for the propagation chain
> (commits `731466d8` recovery → `e07dae37` final D-S re-runs).

---

## Headline

The project has a stark two-era documentation pattern:

- **Era 1** (h8–h12, retest phases, 2025-11 through 2026-03): rigorous
  statistical analyses (bootstrap CIs, paired permutation tests,
  threshold sweeps) with narrative synthesis concentrated in
  `docs/notes/reflections/working-notes.md` rather than in per-run
  post-run reports. No cost manifests, no formal pre-launch audits, no
  Dawid-Skene (D-S) corrections.
- **Era 2** (55-map generalisation, 2026-04-10 onwards): return to
  best-practice deliverables — cost manifest, pre-launch audit, post-
  run report, multi-buffer F1 with bootstrap CIs, paired permutation
  tests, and D-S posterior correction. Four runs fit this era; three
  were produced by the publishable `scripts/run_generalisation.py`
  launcher and one (the 2026-04-10 text run) is documented
  retrospectively because it predates the launcher.

The 2026-04-20/21 human-review day added a large cohort of post-hoc
analyses on top of the 55-map image run — multi-buffer corrected F1,
D-S v1/v2 cross-tabs, subtype classification, buffer-band lift,
verifier calibration, and a CI-metadata registry covering 48 files.
Those are summarised as "post-matrix analytical work" below.

## Four 55-map generalisation runs — anchor values

All values cited here are independently verifiable in the listed source
files; matching JSON key paths appear in
`results-audit-2026-04-21.md`.

| Run | Cost (USD) | F1 @ 50 m measured | F1 @ 50 m D-S posterior | Cache-hit rate | Observation |
|---|---:|---:|---:|---:|:---|
| `55maps-image-generalisation` | 364.70 | 0.771 | 0.795 | 91.0 % | Obs 256 / 257 / 262–269 / 272–273 |
| `55maps-generalisation` (retrospective text HIGH, 2026-04-10) | ~75 (estimate; no cost manifest) | 0.790 | 0.814 | not recorded | referenced by Obs 258 |
| `55maps-text-min-generalisation` | 60.79 | 0.759 | 0.783 | 0.0 % | Obs 258 / 259 |
| `55maps-text-high-generalisation` (2026-04-19 re-run) | 69.60 | 0.788 | 0.813 | 0.0 % | Obs 258 / 259 / 260 |

**Notes**:

- The D-S posterior F1 at 50 m for the image run is **0.7954** in
  `results/55maps-image-generalisation/dawid-skene/dawid-skene-results.json`
  under `dawid_skene.corrected_metrics.f1`; this rounds to 0.795.
  **Caveat from Obs 273** (line 12840): the preregistered student-FN
  prior of 0.05 is mis-specified on this cohort; the posterior is
  degenerate (every VLM-only candidate receives the same posterior of
  0.1862) and the headline 0.795 should be cited with the qualification
  that human adjudication, not D-S, is the only working per-item
  signal on the VLM-only slice. The measured F1 of 0.771 is unchanged.
- The retrospective text run at `outputs/55maps-generalisation/` has
  no `cost_manifest.json`; the retrospective post-run report at
  `configs/run-configs/55maps_text_generalisation_retrospective_post_run_report.md`
  (lines 115–117) states "**~$75** (v1-only)" as a scaling estimate
  and flags proposer cost as unrecoverable from the original meta
  artefacts.
- The 2026-04-19 text-HIGH re-run (`outputs/55maps-text-high-generalisation/`)
  is distinct from the retrospective text HIGH run. The prior audit
  conflated the two.

## Deliverable coverage (the eight-column framework, unchanged)

Each 55-map production run is assessed against eight deliverables. The
table below covers the four runs in the anchor table; the
run-by-run table in `results-audit-2026-04-21.md` extends this to
Era 1 runs.

| Deliverable | image | retrospective text | text-min | text-high |
|---|:-:|:-:|:-:|:-:|
| F1 / P / R at 20/30/40/50 m | yes | yes | yes | yes |
| Bootstrap 95 % CIs (1 000 iter, seed 42) | yes | yes (1 000 iter per retrospective report line 37) | yes | yes |
| Paired permutation test vs a comparator | yes | no (no planned comparator in original design) | yes (vs text-high) | yes (vs text-min, 4 buffers) |
| Dawid-Skene latent-truth correction | yes (with Obs 273 caveat) | yes (retrospective) | yes | yes |
| Cost manifest | yes ($364.70) | no (~$75 estimate) | yes ($60.79) | yes ($69.60) |
| Pre-launch audit | yes | no (retrospective run) | yes | yes |
| Post-run report | yes | yes (retrospective) | yes | yes (filed under `configs/run-configs/`) |
| Working-notes observation | Obs 256+ | Obs 258 | Obs 258/259 | Obs 258/259/260 |

## Era 1 status (h-series, retest)

The prior audit's era analysis holds up on re-inspection. Key points
that carry over, restated here without the prior audit's numeric
errors:

- **h8-v2 library composition**: bootstrap CIs and paired permutation
  tests present for the greedy cohort; multi-buffer curve missing;
  narrative in `results/h8-v2/` + working-notes Obs 238 (line in file
  captured in the full audit table).
- **h10 calibration pool**: bootstrap CIs, ICC diagnostics, verifier-
  independence probe (`results/h10/verifier_independence_probe.md`)
  present; multi-buffer curve missing; narrative only in working-notes.
- **h11 two-stage**: fragmented across multiple sub-run directories;
  proposer-vs-verifier paired test never formally computed; two
  "UNINTENDED-T1.0" runs exist (`outputs/h11/single-pass-384-UNINTENDED-T1.0/`
  and `outputs/h11/consensus-384-UNINTENDED-T1.0/`) and have not been
  formally excluded or archived.
- **h12-v2 HP:HN ratio**: `results/h12-v2/analysis_summary.md` is a
  strong single-file narrative including threshold sweeps, three-way
  permutation tests with Benjamini-Hochberg FDR correction, and
  operational notes. Cost accounting is informal.
- **retest (phase 2 + 3)**: `results/retest/retest-production-summary.md`
  and `results/retest/pairwise-bootstrap-comparisons.json` make this
  one of the better-documented Era 1 runs.

## Post-matrix analytical work (2026-04-20 onwards)

These are analyses that landed after the prior audit and are therefore
not in it. All are scoped under `results/55maps-image-generalisation/`
(except subtype-classification, which is on the 4-map gold-standard)
and all cite to a working-notes Observation in the 262–273 range.

- **Review-UI effect cross-tab** (Obs 268, line 12490) —
  `results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.json`
  — 21 % one-directional reviewer flip rate after the tolerance-circle
  UI was added.
- **Verifier calibration cross-tab** (Obs 269, line 12550) —
  `results/55maps-image-generalisation/verifier-calibration-crosstab/calibration.json`
  — expected calibration error (ECE) 0.269, area under the receiver
  operating characteristic curve (AUC) 0.655, pronounced quantisation
  at the high end of the output range.
- **Human-reviewed corrected F1** (Obs 267, line 12394) —
  `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.json`
  — corrected F1 at 50 m buffer = 0.8295 (rounds to 0.830) under the
  extended-ground-truth counting rule, 2.5× more phantom TPs than D-S
  estimated.
- **Multi-buffer corrected F1** —
  `results/55maps-image-generalisation/corrected-f1-multi-buffer/summary.json`
  — F1 at R = 50/75/100/125/150 m = 0.832 / 0.848 / 0.852 / 0.854 /
  0.855 (rounded from the source JSON's 0.8317 / 0.8477 / 0.8521 /
  0.8538 / 0.8551).
- **Buffer-band lift** (Obs 272, line 12770) —
  `results/55maps-image-generalisation/buffer-band-lift/summary.json`
  — attractor-pull effect statistically significant through 125 m;
  shells beyond 125 m are indistinguishable from within-tile random
  placement.
- **Buffer-100 m diagnostics** —
  `results/55maps-image-generalisation/buffer-100m-diagnostics/summary.json`
  — ground-truth clustering + pair-drift contributions to the 50 m →
  100 m recall gain.
- **D-S v1 cross-tab vs human review** (Obs 273, line 12840) —
  `results/55maps-image-generalisation/ds-human-crosstab/summary.json`
  — D-S posteriors collapse to a single value (0.1862) on every
  VLM-only candidate; ECE 0.539, AUC 0.500. Prior-invariant AUC
  establishes structural inadequacy.
- **D-S v2 data-driven prior sweep** (Obs 273) —
  `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/dawid-skene-results-v2.json`
  — confirms the pathology at every informative prior including
  held-out 80/20 control.
- **Subtype classification** (Obs 270/271, lines 12649 / 12711) —
  `results/gold-standard-subtype-classification/macro_weighted_summary.json`
  — weighted-F1 0.8873 (rounds to 0.887) at 50 m buffer on the 4-map
  gold-standard set; 57 % benchmark_mound → triangulation_mound
  asymmetric confusion.
- **Human re-review multi-buffer CSV** —
  `results/55maps-image-generalisation/human-review-multi-buffer.csv`
  (557 rows re-reviewing yesterday's not-mound candidates at five
  tolerance bands).
- **Paper-tables consolidation** — `results/paper-tables/` contains 26
  files including `gold-standard-spatial-tolerance.{md,csv}` and
  `subtype-classification.{md,csv}` plus cross-hypothesis metrics
  master tables with CI-metadata sidecars.

## CI-metadata registry + protocol errata E54

The CI-metadata registry at `results/ci-metadata-registry.md` enumerates
48 sidecar files (41 per-file `*.metadata.json` + 7 directory-level
entries) across `outputs/`, `results/`, and `results/leaderboard/`.
Every bootstrap CI in the project now has an accompanying sidecar that
records iteration count, seed, resampling unit, library entry point,
and the commit of the generating script.

Protocol errata entry **E54** (committed in `ad023fc3`;
`docs/methodology/preregistration/protocol-errata.md:1670`) documents
the split between 1 000-iteration (preregistered) and 10 000-iteration
(post-hoc) bootstrap analyses, with the explicit list of scripts in
each category.

## What this means for the paper

1. The paper headline of F1 = 0.904 was produced before the v2
   verifier existed and uses verifier v1 (policy document
   `docs/methodology/v2-verifier-contamination-policy.md`); the
   quarantine of 100 contaminated files on 2026-04-21 does not
   touch the headline.
2. The image-run D-S posterior of 0.795 should be cited with the
   Obs 273 caveat; human-review corrected F1 of 0.830 at 50 m is the
   preferred lower-bound narrative.
3. The text-high versus text-min paired test at 50 m returns
   ΔF1 = 0.029163 with p = 0.0 across 10 000 permutations
   (`results/55maps-text-high-generalisation/paired-vs-min-50m/pairwise_permutation_result.json`).
4. Cost accounting is complete across the three publishable-launcher
   runs; the retrospective text run is flagged as estimate-only. Total
   production-run API spend for the four 55-map runs is at least
   $495.09 measured ($364.70 + $60.79 + $69.60) plus ~$75 estimated for
   the retrospective text run.

## Known gaps remaining

After the post-matrix work, the notable remaining gaps are:

- Era 1 multi-buffer curves for h8, h10, h12-v2 (only 20 m reported).
- h11 proposer-vs-verifier paired test never computed; two UNINTENDED
  runs not formally excluded.
- No formal cost manifest for h-series or retest (pre-launcher era).

These are methodological-support gaps, not publication blockers, since
the paper headline rests on runs that do have full coverage.

## Cross-references

- `docs/methodology/preregistration/protocol-errata.md` — full errata
  log (E47 primary buffer, E52 H12 re-run, E54 bootstrap iterations).
- `docs/methodology/v2-verifier-contamination-policy.md` — the
  2026-04-21 quarantine policy.
- `docs/notes/reflections/working-notes.md` — Observation log; all
  post-matrix observations are in the 262–273 range.
- `planning/doc-audit-rerun-plan.md` — the plan document that drove
  this re-audit.
