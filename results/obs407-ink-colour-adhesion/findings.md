# Obs 407 ink-colour adhesion test — the model adheres to black-element symbols; students do not

> **Last revised**: 2026-08-15 (blind-verification corrections applied
> — three minor prose-precision fixes, no number or conclusion moved).
> See [§ Changelog](#changelog) for revision history.

**Question** (Obs 407, from the PI's ruling-21 walk item #4635): do
displaced marks adhere to attractors of matching ink colour? Testable
form used here: does displacement magnitude sort by the marked mound's
symbol colour class?

**Design**: pre-specified in `planning/s133-analysis-block-2026-08-15.md`
(hardenings 1–3, commit `22227508a`) before the formal tests ran; a
transparency note on what the data-semantics gate exposed first is at
§ 4. Script `scripts/analyse_ink_colour_adhesion.py` (seed 42, 10,000
label permutations, two-sided); results
`results/obs407-ink-colour-adhesion/adhesion-results.json` (run on
sapphire, commit `8466f16a8`). Input:
`results/deployment-oracle-2026-06-06/canonical-gt/marked-centres.csv`;
census 1,271 records retained after the a-priori exclusions
(not_a_mound, extra_point, skipped, displacement-free), 1,271 in
cohorts.

**Colour classes** (from `symbol_type`): **black-element** =
{bench_mark_on_mound, trig_point_on_mound} — the mound carries a black
geodetic overprint and printed elevation numeral at the true centre;
**plain** = {burial_mound, settlement_mound} — orange-brown relief ink
only.

## 1. Headline

| Cohort | n (black / plain) | median black | median plain | Δ median | p (median) | p (mean) |
|---|---|---:|---:|---:|---:|---:|
| **model** (promoted phantoms) | 152 / 580 | **13.71 m** | **44.89 m** | **−31.18 m** | **0.0001** | 0.0049 |
| student_hard (condition-selected) | 52 / 387 | 8.96 m | 8.25 m | +0.71 m | 0.495 | 0.647 |
| student_random (jitter sample) | 25 / 75 | 8.34 m | 8.85 m | −0.50 m | 0.718 | 0.418 |

(All figures: `adhesion-results.json`; the median p for the model
cohort is the add-one floor at 10,000 permutations.)

**Model detections sit 3× closer to the true centre (on the median;
1.3× on the mean) on black-element mounds than on plain mounds; human
placement shows no colour-class effect at all.** Both student cohorts — the unbiased random jitter
sample and the condition-selected hard cases — put marks a median
~8–9 m from the true centre regardless of symbol class.

## 2. Why the student null matters (the confound control)

The named confound (block plan hardening 2) was that black-element
mounds are surveyed geodetic points — plausibly larger and better
mapped — so smaller displacements could reflect mapping quality, not
ink colour. If that were the mechanism it should compress *human*
placement error on black-element mounds too. It does not (median
deltas +0.7 m / −0.5 m; all four student tests p ≥ 0.418). The
effect is specific to the model pipeline.

## 3. Interpretation — consistent-with, not proof-of

The result is **consistent with colour-matched adhesion**: the black
geodetic symbol coincides with the true centre on black-element
mounds, and model detections bind to it; on plain mounds the nearest
black ink is off-mound and detections land far more diffusely (median
44.9 m).

Two mechanisms remain confounded at this grain:

1. **Ink-colour adhesion proper** — the detection binds to black ink
   wherever it sits (the PI's #4635 rationale).
2. **Labelled-point locatability** — trig points and benchmarks carry
   printed elevation numerals; a text-mode pipeline may simply
   transcribe labelled points more precisely, regardless of colour.

Both predict the observed contrast, because on black-element mounds
the black attractor *is* the target. Separating them needs the
displacement **bearings** on plain mounds: colour adhesion predicts
vectors pointing toward the nearest black feature; locatability
predicts no directional structure. That is the **vector-extension
project** (extract black-feature locations from the sheets), noted as
parked in the block plan (PI, 2026-08-15).

A distributional note supporting the adhesion reading: the model's
black-element class is strongly bimodal — an "adhered" mode (Q1
6.15 m, median 13.71 m) plus a far tail (P90 101.79 m; mean 35.01 m ≫
median). Roughly half the black-element phantoms pin near the symbol;
the rest behave like plain-mound phantoms. The plain class is not
bimodal in this way (median 44.89 ≈ mean 44.24).

## 4. Transparency notes

- **What was seen before the tests ran**: the block plan's
  data-semantics gate (hardening 3) profiled per-class descriptive
  medians while establishing `item_type` semantics, so the direction
  of the model contrast was visible before the permutation tests
  executed. The contrasts, statistics (10,000 permutations, seed 42),
  and exclusions were fixed in the committed plan (`22227508a`,
  hardenings 1 and 3) *before* that profiling. One refinement was
  made *at* the gate and is disclosed here: the plan specified
  per-source-layer tests with the jitter sample reported as a noise
  floor; the executed design instead splits `corrected_student` into
  the random (jitter) and condition-selected cohorts and tests all
  three — a finer grain of the same contrast, adopted for the
  selection-bias reason in the next bullet, not on any outcome. Of
  the four a-priori exclusion filters, only two bind on this file
  (`skipped` matches zero rows; every displacement-free row is
  already `not_a_mound`), so the census is 1,317 − 45 − 1 = 1,271.
- **Cohort semantics**: the jitter sample is random and
  conflation-free by construction
  (`planning/point-marking-app-spec.md`); student_hard rows were
  queued *because* they are difficult (conflations, pairs, merge
  sites), so their agreement with the random sample (medians 8.25–8.96
  vs 8.34–8.85) is itself reassuring about human placement stability.
- **Status**: exploratory, $0, not preregistered; extends the
  attractor-mechanism series (Obs 396's subsidy caveat; Obs 398, 404,
  407).

## Changelog

### 2026-08-15 (later) — Blind-verification corrections

Fresh-context verifier (denominator: 70 claims identified / 69
re-derived or source-checked / 66 confirmed / 3 corrections, all
minor; verdict pass-with-corrections). Every headline statistic,
census figure, commit hash, and external attribution reproduced
exactly from the raw CSV. Corrections applied: (1) "p ≥ 0.42" →
"p ≥ 0.418" (the minimum student p is 0.41776 at the pinned seed;
triple-derived); (2) the headline "3× closer" qualified as a median
ratio (3.27×; the mean ratio is 1.26×); (3) the § 4 pre-specification
claim narrowed — the three-cohort split was a disclosed refinement at
the data-semantics gate, not fixed in the plan text (the plan
specified per-source-layer tests with the jitter sample as a noise
floor). Two verifier-suggested strengtheners also applied: the
only-two-filters-bind census note and Obs 396's "subsidy caveat"
qualifier. No number, direction, or conclusion moved.

### 2026-08-15 — Original publication

First analysis of Obs 407's hypothesis. Design pre-specified in the
S133 block plan (commit `22227508a`); results produced on sapphire
(commit `8466f16a8`); blind fresh-context verification to follow in
the same session.
