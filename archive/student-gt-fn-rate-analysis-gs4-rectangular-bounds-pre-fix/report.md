# Student GT False-Negative Rate — 4 GS Maps Direct Curator-vs-Student

Direct confusion-matrix analysis (TP / FP / FN) of the cleaned student
ground truth against the curator-corrected reference, on the four
gold-standard (GS) map sheets. This is the proper analogue to
Sobotkova et al. (2023)'s 4-map curator-vs-student diff (5.0 % FN,
0.1 % FP) and a complement to the 55-map review-based estimate at
`results/student-gt-fn-rate-analysis/` (~9.7 % headline FN).

## Headline result

At a 50 m Hungarian match radius (project canonical, Obs 272):

- **Aggregate FN rate** (curator mounds the students missed): 0.0527 (95 % CI 0.0292–0.0880, bootstrap-by-sheet, 10,000 iterations); 30 unmatched curator features against 569 curator mounds across 4 sheets.
- **Aggregate FP rate** (student mounds with no curator analogue): 0.0306 (95 % CI 0.0129–0.0529); 17 unmatched student features against 556 student mounds across 4 sheets.
- **TP / FP / FN** (corpus aggregate at 50 m): TP = 539, FP = 17, FN = 30.
- **Student precision** (against curator truth): 0.9694.
- **Student recall** (against curator truth): 0.9473.
- **Student F1**: 0.9582.

### Comparison with prior estimates

| Estimate | FN rate | FP rate | Source |
|---|---:|---:|---|
| **This analysis (4 GS, direct)** | 0.0527 | 0.0306 | `results/student-gt-fn-rate-analysis-gs4/` |
| Sobotkova et al. 2023 (4 maps, direct) | 0.0500 | 0.0010 | published participatory-GIS comparison |
| 55-map VLM-mediated review (headline) | 0.0887 | n/a | `results/student-gt-fn-rate-analysis/` |
| 55-map recall-adjusted central | 0.1115 | n/a | `results/student-gt-fn-rate-analysis/` |

**Verdict — FN rate**. The 4-GS direct FN rate (5.27 %) is consistent with Sobotkova 2023 (delta +0.3 pp); it diverges from the 55-map estimate by -4.4 percentage points.
 The direction of the difference is informative: the 4 GS maps were selected as fieldwork-grade reference quality and may be among the best-mapped sheets in the wider corpus, so a lower-than-corpus FN rate is consistent with the 55-map analysis's earlier hypothesis that the original 4-map calibration is downward-biased relative to the wider corpus (see `results/student-gt-fn-rate-analysis/report.md` §Comparison).

**Verdict — FP rate**. The 4-GS direct FP rate (3.06 %) is **substantially higher** than Sobotkova 2023's 0.1 % FP (delta +3.0 pp). **This is a flag-worthy result**: a 30× inflation of FP relative to Sobotkova 2023's published 0.1 %. Three plausible explanations, in order of prior probability:

1. **Definitional drift**. Sobotkova 2023's 0.1 % may have counted only egregious duplicates / non-features, whereas the present analysis counts every unmatched student feature as FP regardless of cause — including curator features that were re-classified (e.g., not-mound after curator review) but are still genuine topographic anomalies the students reasonably flagged.
2. **Cleaning round difference**. The student GT used here is the '_reviewed' version (`student-mounds-gs-4maps-reviewed.geojson`). If Sobotkova 2023's analysis used a more aggressively cleaned student dataset that already removed obvious FPs, the residual FP rate would be lower.
3. **Genuine FP**. The students did flag 17 mounds that the curator did not. These would be worth a per-feature audit (location, FeatureType, MapSymbol) to see whether they are systematic (e.g., one symbol style) or scattered.

Either way, the 0.1 % comparator should be treated with caution until reconciliation with Sobotkova 2023's exact protocol is documented.

## Per-sheet breakdown

At the 50 m headline match radius:

| Sheet | Curator | Student | TP | FN | FP | FN rate | FP rate | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `K-35-052-4_32635` | 136 | 135 | 131 | 5 | 4 | 0.0368 | 0.0296 | 0.9668 |
| `K-35-053-3_Elenovo` | 217 | 213 | 211 | 6 | 2 | 0.0276 | 0.0094 | 0.9814 |
| `K-35-062-2_Rakovski` | 196 | 187 | 178 | 18 | 9 | 0.0918 | 0.0481 | 0.9295 |
| `K-35-078-1_Lesovo` | 20 | 21 | 19 | 1 | 2 | 0.0500 | 0.0952 | 0.9268 |

**Sheet flagged (highest FN rate)**: `K-35-062-2_Rakovski` carries an FN rate of 0.0918 (18 of 196 curator mounds unmatched at 50 m), the highest of the four GS sheets.

**Comparison with Session 81 audit**: `K-35-062-2_Rakovski` was previously flagged as a 15.88 % FN outlier in Session 81. The present analysis at 50 m yields 9.18 % (-6.70 pp delta). This is a material reduction from the Session 81 figure. Possible drivers: (a) the reviewed-and-cleaned student GT landed at commit `a8b576d5` added Rakovski mounds that were missing from the prior version (Rakovski student count = 187, curator count = 196 — near-parity); (b) the Session 81 analysis may have used a different match radius or matching protocol; (c) Hungarian matching may have resolved cluster collisions differently than the prior protocol. Worth re-reading Session 81's notes to reconcile the protocols.

## Match-radius sensitivity sweep

Aggregate confusion-matrix counts at four match radii. The 50 m row
is the headline; 75 / 100 / 150 m mirror the 55-map analysis's tier
boundaries (likely-collision / marginal / outer-shell) so the two
analyses can be compared at matched radii.

| Radius (m) | TP | FN | FP | FN rate | FP rate | Precision | Recall | F1 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 50 | 539 | 30 | 17 | 0.0527 | 0.0306 | 0.9694 | 0.9473 | 0.9582 |
| 75 | 539 | 30 | 17 | 0.0527 | 0.0306 | 0.9694 | 0.9473 | 0.9582 |
| 100 | 539 | 30 | 17 | 0.0527 | 0.0306 | 0.9694 | 0.9473 | 0.9582 |
| 150 | 539 | 30 | 17 | 0.0527 | 0.0306 | 0.9694 | 0.9473 | 0.9582 |

**Important sweep finding**: TP / FN / FP are *identical* at all four radii. There are no near-miss pairs in the 50–150 m band:
 every student–curator pair that can match within 150 m already matches within 50 m. This means the headline FN and FP counts are not artefacts of jitter or Hungarian-blocking — the 30 unmatched curator features and 17 unmatched student features are genuinely without a counterpart at any reasonable radius. By contrast, the 55-map review-based analysis observed a non-trivial 'marginal' tier (75–125 m) of 141 candidates, suggesting the cleaner cluster-resolution behaviour of the 4-GS curator-cleaned reference is what produces this sharp result here.

Per-sheet sweep is in `match_radius_sweep.csv`.

## Methodology

### Inputs

- **Student GT (4 GS, cleaned and reviewed)**: `inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson`, 556 features in EPSG:32635, landed at commit `a8b576d5`. Per-sheet counts: Elenovo 213, Rakovski 187, K-35-052-4 135, Lesovo 21.
- **Curator GT**: `inputs/vectors/references/mounds-reference.geojson`, 569 features across the 4 GS sheets in EPSG:32635. The full curator file is already restricted to the 4 GS sheets by `Map` column; the 4-GS sheet bounds at `inputs/vectors/bounds/gs-4maps-sheet-bounds.geojson` were used to verify there is no leakage outside the 4 sheet polygons.

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

- **Selection bias of the 4 GS sheets**. These sheets were chosen for fieldwork-grade reference quality. Their FN rate is therefore plausibly an under-estimate of the corpus-wide rate; the 55-map analysis (which spans more diverse sheets) is the better corpus-
 level estimate.
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
