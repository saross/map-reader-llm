# Student GT False-Negative Rate — 4 GS Maps Direct Curator-vs-Student

> **Last revised**: 2026-09-01 (selection framing corrected per
> Obs 442 — the four sheets were randomly selected, not
> quality-selected). See [§ Changelog](#changelog) for revision
> history.

Direct confusion-matrix analysis (TP / FP / FN) of the cleaned student
ground truth against the curator-corrected reference, on the four
gold-standard (GS) map sheets. This is the proper analogue to
Sobotkova et al. (2023)'s 4-map curator-vs-student diff (5.0 % FN,
0.1 % FP) and a complement to the 55-map review-based estimate at
`results/student-gt-fn-rate-analysis/` (~9.7 % headline FN).

## Headline result

At a 50 m Hungarian match radius (project canonical, Obs 272):

- **Aggregate FN rate** (curator mounds the students missed): 0.0527 (95 % CI 0.0292–0.0880, bootstrap-by-sheet, 10,000 iterations); 30 unmatched curator features against 569 curator mounds across 4 sheets.
- **Aggregate FP rate** (student mounds with no curator analogue): 0.0000 (95 % CI 0.0000–0.0000); 0 unmatched student features against 539 student mounds across 4 sheets.
- **TP / FP / FN** (corpus aggregate at 50 m): TP = 539, FP = 0, FN = 30.
- **Student precision** (against curator truth): 1.0000.
- **Student recall** (against curator truth): 0.9473.
- **Student F1**: 0.9729.

### Comparison with prior estimates

| Estimate | FN rate | FP rate | Source |
|---|---:|---:|---|
| **This analysis (4 GS, direct)** | 0.0527 | 0.0000 | `results/student-gt-fn-rate-analysis-gs4/` |
| Sobotkova et al. 2023 (4 maps, direct) | 0.0500 | 0.0010 | published participatory-GIS comparison |
| 55-map VLM-mediated review (headline) | 0.0887 | n/a | `results/student-gt-fn-rate-analysis/` |
| 55-map recall-adjusted central | 0.1115 | n/a | `results/student-gt-fn-rate-analysis/` |

**Verdict — FN rate**. The 4-GS direct FN rate (5.27 %) is consistent with Sobotkova 2023 (delta +0.3 pp); it diverges from the 55-map estimate by -4.4 percentage points.
 The four sheets were **randomly selected** from the complete corpus (Sobotkova et al. 2023 § 3.5.2 "four randomly selected maps"; PI confirmation 2026-08-31; Obs 442 — an earlier "selected for fieldwork-grade reference quality" framing here is retracted), so the divergence is not a selection artefact. The plausible drivers are n = 4 sampling variance (the bootstrap CI below nearly reaches the 55-map headline), genuine corpus/era variation (all four audited sheets are 2017 digitisations), and the two estimates' different instruments — the 55-map figure is a VLM-mediated lower bound whose recall adjustment is itself optimistic under miss-correlation (Obs 361).

**Verdict — FP rate**. The 4-GS direct FP rate is 0.00 % (delta -0.10 pp from Sobotkova 2023's 0.1 %). After clipping student GT to the trapezoidal active area (see §Active-area clipping), all 17 features previously counted as FPs are excluded as black-collar artefacts. The remaining FP count is 0, which is consistent with — and slightly cleaner than — Sobotkova 2023's published comparator. The pre-fix analysis (rectangular raster envelope, no neat-line clipping) reported 17 FPs and a 3.06 % rate; that analysis is preserved at `archive/student-gt-fn-rate-analysis-gs4-rectangular-bounds-pre-fix/` for transparency.

## Per-sheet breakdown

At the 50 m headline match radius:

| Sheet | Curator | Student | TP | FN | FP | FN rate | FP rate | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `K-35-052-4_32635` | 136 | 131 | 131 | 5 | 0 | 0.0368 | 0.0000 | 0.9813 |
| `K-35-053-3_Elenovo` | 217 | 211 | 211 | 6 | 0 | 0.0276 | 0.0000 | 0.9860 |
| `K-35-062-2_Rakovski` | 196 | 178 | 178 | 18 | 0 | 0.0918 | 0.0000 | 0.9519 |
| `K-35-078-1_Lesovo` | 20 | 19 | 19 | 1 | 0 | 0.0500 | 0.0000 | 0.9744 |

**Sheet flagged (highest FN rate)**: `K-35-062-2_Rakovski` carries an FN rate of 0.0918 (18 of 196 curator mounds unmatched at 50 m), the highest of the four GS sheets.

**Comparison with Session 81 audit**: `K-35-062-2_Rakovski` was previously flagged as a 15.88 % FN outlier in Session 81. The present analysis at 50 m yields 9.18 % (-6.70 pp delta). This is a material reduction from the Session 81 figure. Possible drivers: (a) the reviewed-and-cleaned student GT landed at commit `a8b576d5` added Rakovski mounds that were missing from the prior version (Rakovski student count = 178, curator count = 196 — near-parity); (b) the Session 81 analysis may have used a different match radius or matching protocol; (c) Hungarian matching may have resolved cluster collisions differently than the prior protocol. Worth re-reading Session 81's notes to reconcile the protocols.

## Match-radius sensitivity sweep

Aggregate confusion-matrix counts at four match radii. The 50 m row
is the headline; 75 / 100 / 150 m mirror the 55-map analysis's tier
boundaries (likely-collision / marginal / outer-shell) so the two
analyses can be compared at matched radii.

| Radius (m) | TP | FN | FP | FN rate | FP rate | Precision | Recall | F1 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 50 | 539 | 30 | 0 | 0.0527 | 0.0000 | 1.0000 | 0.9473 | 0.9729 |
| 75 | 539 | 30 | 0 | 0.0527 | 0.0000 | 1.0000 | 0.9473 | 0.9729 |
| 100 | 539 | 30 | 0 | 0.0527 | 0.0000 | 1.0000 | 0.9473 | 0.9729 |
| 150 | 539 | 30 | 0 | 0.0527 | 0.0000 | 1.0000 | 0.9473 | 0.9729 |

**Important sweep finding**: TP / FN / FP are *identical* at all four radii. There are no near-miss pairs in the 50–150 m band:
 every student–curator pair that can match within 150 m already matches within 50 m. This means the headline FN and FP counts are not artefacts of jitter or Hungarian-blocking — the 30 unmatched curator features and 0 unmatched student features are genuinely without a counterpart at any reasonable radius. By contrast, the 55-map review-based analysis observed a non-trivial 'marginal' tier (75–125 m) of 141 candidates, suggesting the cleaner cluster-resolution behaviour of the 4-GS curator-cleaned reference is what produces this sharp result here.

Per-sheet sweep is in `match_radius_sweep.csv`.

## Methodology

### Inputs

- **Student GT (4 GS, cleaned and reviewed)**: `inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson`, 556 features in EPSG:32635, landed at commit `a8b576d5`. Per-sheet rectangular-envelope counts: Elenovo 213, Rakovski 187, K-35-052-4 135, Lesovo 21. After clipping to the trapezoidal active area (see §Active-area clipping below): **539 features retained** (17 dropped on the black collar outside the cartographic neat-line).
- **Curator GT**: `inputs/vectors/references/mounds-reference.geojson`, 569 features across the 4 GS sheets in EPSG:32635. The full curator file is already restricted to the 4 GS sheets by `Map` column. All 569 curator features lie inside the trapezoidal active area (0 dropped on clipping), confirming the curator dataset is a canonical truth defined inside the neat-line.

### Active-area clipping

Both student and curator GT are clipped to the **trapezoidal graticule quadrangle** of each sheet (1:50,000 sheet, 10' lat × 15' lon, derived deterministically from the sheet ID on the Pulkovo-1942 / S-42 datum and re-projected to UTM-35N). Bounds file: `inputs/vectors/bounds/gs-4maps-active-area-bounds.geojson`, produced by `scripts/generate_gs4maps_active_area_bounds.py`.

Why trapezoidal, not rectangular: the GeoTIFF rasters include a black collar / tilted-corner padding outside the cartographic neat-line. A pre-fix version of this analysis used the rectangular raster envelope (`inputs/vectors/bounds/gs-4maps-sheet-bounds.geojson`) for sanity-checking only, and reported 17 student false positives. Visual review of all 17 in the Streamlit reviewer found that every one fell on the black collar, not on cartographic content — i.e., they were artefacts of digitising over the padding, not legitimate misidentifications. Switching to the trapezoidal active area drops these 17 features and produces a clean FP = 0 result. Pre-fix outputs are preserved at `archive/student-gt-fn-rate-analysis-gs4-rectangular-bounds-pre-fix/`.

### Matching

One-to-one Hungarian assignment via
`scripts.lib_advanced_metrics.match_detections_to_references` — the same matcher used for the project's main F1 evaluation. Curator features are treated as the reference; student features as
 detections. Pairs with separation > radius are dropped from the assignment (cost = `radius * 1000` for those entries).

Counts:

- TP: matched curator–student pairs.
- FN: unmatched curator features (the students missed these).
- FP: unmatched student features (extra student mounds with no
  curator analogue at this radius).

**Headline match radius**: 50 m. This is the project canonical match radius (Obs 272) and the spatial-dedup distance used in the 55-map review-based analysis. The sweep at
 75 / 100 / 150 m provides comparability with the 55-map tier
 boundaries.

### FN-rate denominator (differs from the 55-map analysis)

We use the standard confusion-matrix convention:

- FN rate = FN / curator_count (Sobotkova 2023 convention)
- FP rate = FP / student_count

The 55-map review-based analysis used `FN / (student_GT + FN)` because the curator GT did not exist for those 55 sheets — VLM-
flagged candidates were the only signal of student-missed mounds, and the denominator was student-anchored. Here the curator IS the canonical truth, so the denominator is curator_count alone. The two denominators differ slightly when FN is non-trivial: 0.0887 (55-map) implies 0.0973 under the 4-GS convention
 (FN / curator = FN / (student_GT + FN) when student_GT ≈ TP + genuine_FN; the 9.7 % figure reported in the project as the '~9.7 % estimate' is the converted value).

### Bootstrap

Bootstrap-by-sheet, 10,000 iterations, seed 42. Each iteration resamples 4 sheets with replacement and recomputes the aggregate rate as `sum(numerator) / sum(denominator)`. **Caveat**: with N = 4, the bootstrap CI is wide and dominated by
 between-sheet variance; the smallest sheet (Lesovo, 20 curator mounds) carries low weight per draw but a single draw containing
 four copies of one extreme sheet is non-trivial. The CI here is best read as 'how stable is the aggregate to the choice of which 4 sheets we happen to have' rather than as a population-level CI.

## Caveats

- **Sampling of the 4 GS sheets**. The sheets were randomly selected
 from the complete corpus (Obs 442, correcting this report's original
 selection-bias caveat), so the estimate is unbiased — but n = 4
 leaves wide sampling variance (see § Bootstrap), and the draw is
 all-2017 by chance (hypergeometric P ≈ 0.26; the 2018 cohort was
 never audited), so era coverage is a scope limit.
- **Single human cleaning pass**. The student GT used here was
 cleaned and reviewed in a single human pass landed at commit
 `a8b576d5`. Reviewer-induced systematic errors (e.g., missing a
 specific symbol style) would propagate into both the FN and FP
 counts.
- **No matching-radius optimisation**. We report at fixed radii
 (50 / 75 / 100 / 150 m) rather than picking the F1-maximising
 radius. This is deliberate: the comparison with Sobotkova 2023
 and the 55-map estimate requires fixed, project-canonical radii.
- **Hungarian-collision residual is empty here**. Unlike the 55-map analysis, the 50 / 75 / 100 / 150 m sweep produces *identical* TP / FN / FP counts. There are no near-miss pairs; the headline counts are not artefacts of jitter or Hungarian blocking. This is a stronger result than the 55-map analysis could deliver, because the curator-cleaned reference does not have the cluster-resolution ambiguities that fed the 55-map 'marginal' tier.
- **No recall adjustment**. Unlike the 55-map analysis, we do not
 divide by VLM recall — the curator IS the canonical truth here,
 not a VLM detection set, so no recall adjustment applies.

## Reproducibility

- Script: `scripts/analyse_student_gt_fn_rate_gs4.py`
- Bootstrap: 10,000 iterations, seed 42
- Headline radius: 50 m
- Sweep radii: 50, 75, 100, 150 m
- Outputs: `results/student-gt-fn-rate-analysis-gs4/`
  - `report.md` (this file)
  - `per_sheet_confusion.csv`
  - `match_radius_sweep.csv`
  - `bootstrap_summary.json`
  - `figures/fn_rate_by_sheet.png`

## Changelog

### 2026-09-01 — Selection framing corrected (Obs 442)

The two claims that the four sheets were "selected/chosen for
fieldwork-grade reference quality" (§ Comparison verdict, § Caveats)
are corrected in place: the sheets were randomly selected from the
complete corpus (Sobotkova et al. 2023 § 3.5.2; PI confirmation
2026-08-31; register history in Obs 317/442 — the register recorded
the random selection one day after Obs 316 but it never propagated
here). Numerical results unchanged; the FN-divergence explanation now
rests on n = 4 variance, era/corpus variation, and instrument
differences rather than selection bias. Banner added; this changelog
initiated. Commit: see `git log` for this entry.

### 2026-04-30 — Original publication

Direct curator-vs-student confusion-matrix analysis on the four GS
sheets with trapezoidal active-area clipping (Obs 316): FN 5.27 %
(CI 2.92–8.80 %), FP 0.00 %, student F1 0.9729 at 50 m,
radius-insensitive 50–150 m; pre-fix rectangular-bounds outputs
archived.
