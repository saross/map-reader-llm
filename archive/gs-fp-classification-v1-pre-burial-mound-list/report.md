# GS FP-class classification (Obs 302 follow-up)

_Generated 2026-04-29 08:04 UTC_

Closes the comparator gap flagged in `results/55maps-fp-classification/report.md` Caveats - the 55-map driver tested Shawn's hypothesis (Obs 296) on one corpus but lacked the GS-side measurement to make a clean cross-corpus claim. This run applies the same Soviet-1980s closed-list classifier to all 371 detections in the GS verified-v1 full-scope set (`outputs/h11/gold-standard-v2/verified-v1/verified_detections_full-scope.geojson`), partitioning into TP-side (<= 50 m from a curator GT mound) and FP-side (> 50 m) post-classification. Plan reference: `archive/planning-completed-session-81-82/gs-fp-classification-plan-2026-04-29.md` (commit `edd2ecce`).

## Methodology - different mechanisms, comparable rigour

The 55-map sibling driver derives its FP set from human reviewer overrides (`human_label == "not_mound"`) on noisy student GT (`student-mounds-55maps-reviewed.geojson`, ~25 m positional jitter). The GS pipeline has no equivalent per-detection review step, but the GS curator GT (`inputs/vectors/references/mounds-reference.geojson`, 569 mounds) was triple-checked and manually re-centred to within ~1 px of each mound's true centre during Sobotkova 2022 + this project's reverify pass - sub-metre positional precision. Distance-from-curator-GT is therefore not a proxy on the GS corpus; it is a high-precision geometric filter. See plan section 2 for the full framing.

## Method

1. Loaded all 371 detections from the verified-v1 GeoJSON and 569 curator GT mounds (MultiPoint -> Point exploded). Both files are EPSG:32635, no reprojection.
2. Computed Euclidean planar distance from each detection to its nearest reference Point via `scipy.spatial.cKDTree` (precedent: `scripts/analyse_attractor_pull_gs.py`).
3. Rendered 150 x 150 m crops on-the-fly from the four GS GeoTIFFs at `inputs/rasters/` (K-35-052-4, K-35-053-3, K-35-062-2, K-35-078-1) using the live-raster pipeline mirrored from `scripts/review_candidates.py`.
4. Classified each crop via Gemini 3 Flash (flex tier, thinking_level=minimal, temperature=0.0). Closed-list categories (verbatim from the 55-map driver): number, benchmark, water-feature, contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid, none, other.
5. Partitioned results post-hoc into TP-side (<= 50 m) and FP-side (> threshold) buckets at thresholds [25, 50, 75, 100, 125] m. The classification pass is a single census; the threshold sweep is a post-classification aggregation. See plan section 6 for the rationale for classifying TP-side detections as well (reliability sanity check).
6. Cross-corpus chi-square test against the 55-map text-track aggregate (`results/55maps-fp-classification/category_distribution.json`).

Total classified: 371 / 371 (failed/skipped: 0). Wall-clock: 291.7 s (4.9 m). Estimated API cost: $0.1687 USD (flex tier).

## Distribution by distance-from-curator-GT stratum

The TP-side and FP-side rows below are partitioned at each sensitivity-sweep threshold so the user can see how the FP-class distribution shifts as the threshold tightens or relaxes. The primary threshold is 50 m (plan section 5.2).

| Category | TP (<=50 m) | FP (>25 m) | FP (>50 m) | FP (>75 m) | FP (>100 m) | FP (>125 m) |
|---|---:|---:|---:|---:|---:|---:|
| number | 54 (15.2 %) | 8 (36.4 %) | 4 (25.0 %) | 2 (14.3 %) | 2 (14.3 %) | 2 (14.3 %) |
| benchmark | 30 (8.5 %) | 4 (18.2 %) | 4 (25.0 %) | 4 (28.6 %) | 4 (28.6 %) | 4 (28.6 %) |
| water-feature | 2 (0.6 %) | 2 (9.1 %) | 2 (12.5 %) | 2 (14.3 %) | 2 (14.3 %) | 2 (14.3 %) |
| contour-ring | 213 (60.0 %) | 2 (9.1 %) | 2 (12.5 %) | 2 (14.3 %) | 2 (14.3 %) | 2 (14.3 %) |
| vegetation | 32 (9.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) |
| settlement | 21 (5.9 %) | 2 (9.1 %) | 2 (12.5 %) | 2 (14.3 %) | 2 (14.3 %) | 2 (14.3 %) |
| road-or-track | 0 (0.0 %) | 1 (4.5 %) | 1 (6.2 %) | 1 (7.1 %) | 1 (7.1 %) | 1 (7.1 %) |
| scale-bar-or-grid | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) |
| none | 0 (0.0 %) | 1 (4.5 %) | 1 (6.2 %) | 1 (7.1 %) | 1 (7.1 %) | 1 (7.1 %) |
| other | 3 (0.8 %) | 2 (9.1 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) |
| **N** | **355** | **22** | **16** | **14** | **14** | **14** |

## TP-side reliability check (plan section 6.5)

A well-calibrated classifier should assign mostly `none` / `other` to TP-side detections - the Soviet 1980s topographic vocabulary has no "burial mound" category, so a real mound centred under the crop has nothing in the closed list to map onto. A TP bucket dominated by a vocabulary category (e.g. `contour-ring` > 10 %) would indicate the classifier is hallucinating Soviet-vocabulary categories onto correct detections, which would change how the FP-side categories are interpreted.

- TP-side n: 355
- `none` + `other` share on TP-side: 0.8 % (0 + 3 / 355)
- WARNING: vocabulary-category leakage on TP-side > 10 %: number (15.2 %); contour-ring (60.0 %). The FP-side categorical interpretation should be tempered accordingly (plan section 13.7).

## Distractor-pull share (number + benchmark)

Shawn's 55-map hypothesis predicted high `number + benchmark` share (Soviet 1980s spot-elevation labels and survey markers); the 55-map result was instead `contour-ring`-dominant (Obs 302). On the GS side, Shawn's intuition was that water-features and spot-heights (= `number` in this vocabulary) would dominate. The table below tests both arms by threshold.

| Bucket | number + benchmark | share | water-feature | share | n |
|---|---:|---:|---:|---:|---:|
| TP (<=50 m) | 84 | 23.7 % | 2 | 0.6 % | 355 |
| FP (>25 m) | 12 | 54.5 % | 2 | 9.1 % | 22 |
| FP (>50 m) | 8 | 50.0 % | 2 | 12.5 % | 16 |
| FP (>75 m) | 6 | 42.9 % | 2 | 14.3 % | 14 |
| FP (>100 m) | 6 | 42.9 % | 2 | 14.3 % | 14 |
| FP (>125 m) | 6 | 42.9 % | 2 | 14.3 % | 14 |

## Cross-corpus comparison vs 55-map text-track aggregate

Headline cross-corpus contrast: GS FP at the primary threshold (> 50 m, n=16) versus the 55-map text-track aggregate (sum of T0.3, T0.7, text-MIN runs from `results/55maps-fp-classification/category_distribution.json`).

| Category | GS FP (>50 m) | GS share | 55-map text-track | 55-map share |
|---|---:|---:|---:|---:|
| number | 4 | 25.0 % | 149 | 17.8 % |
| benchmark | 4 | 25.0 % | 41 | 4.9 % |
| water-feature | 2 | 12.5 % | 105 | 12.6 % |
| contour-ring | 2 | 12.5 % | 346 | 41.4 % |
| vegetation | 0 | 0.0 % | 51 | 6.1 % |
| settlement | 2 | 12.5 % | 120 | 14.4 % |
| road-or-track | 1 | 6.2 % | 10 | 1.2 % |
| scale-bar-or-grid | 0 | 0.0 % | 2 | 0.2 % |
| none | 1 | 6.2 % | 2 | 0.2 % |
| other | 0 | 0.0 % | 10 | 1.2 % |
| **N** | **16** | | **836** | |

### Chi-square test - GS FP at primary threshold vs 55-map text-track

- chi-squared statistic: 36.120
- degrees of freedom: 9
- p-value: 3.775e-05
- n (gs): 16
- n (fifty_five): 836
- categories retained (non-zero across both rows): number, benchmark, water-feature, contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid, none, other
- low-expected-count fraction (< 5): 0.55
- Monte Carlo p-value (10000 resamples): 0.0107 (small-N robustness check; per plan §13.3 the asymptotic p-value is unreliable when many cells have expected counts < 5)

### Per-category Pearson residuals

Pearson residuals (observed - expected) / sqrt(expected) indicate which categories drive the difference. |residual| > 2 is the conventional threshold for a meaningful per-cell effect.

| Category | gs obs | gs exp | gs residual | fifty_five obs | fifty_five exp | fifty_five residual |
|---|---:|---:|---:|---:|---:|---:|
| number | 4 | 2.9 | +0.67 | 149 | 150.1 | -0.09 |
| benchmark | 4 | 0.8 | +3.43 | 41 | 44.2 | -0.47 |
| water-feature | 2 | 2.0 | -0.01 | 105 | 105.0 | +0.00 |
| contour-ring | 2 | 6.5 | -1.77 | 346 | 341.5 | +0.24 |
| vegetation | 0 | 1.0 | -0.98 | 51 | 50.0 | +0.14 |
| settlement | 2 | 2.3 | -0.19 | 120 | 119.7 | +0.03 |
| road-or-track | 1 | 0.2 | +1.75 | 10 | 10.8 | -0.24 |
| scale-bar-or-grid | 0 | 0.0 | -0.19 | 2 | 2.0 | +0.03 |
| none | 1 | 0.1 | +3.98 | 2 | 2.9 | -0.55 |
| other | 0 | 0.2 | -0.43 | 10 | 9.8 | +0.06 |

### Cross-corpus chi-square at every sweep threshold

Re-running the same chi-square contingency at each threshold in the sensitivity sweep. The >125 m row is the strictest FP filter (no detection within 125 m of any curator GT mound) and serves as the apples-to-apples comparator alongside the 50 m primary.

| Threshold (m) | n_gs | chi2 | dof | asymp p | Monte Carlo p | low_exp_frac |
|---:|---:|---:|---:|---:|---:|---:|
| 25 | 22 | 41.561 | 9 | 3.953e-06 | 0.0041 | 0.55 |
| 50 | 16 | 36.120 | 9 | 3.775e-05 | 0.0107 | 0.55 |
| 75 | 14 | 40.580 | 9 | 5.964e-06 | 0.008899 | 0.55 |
| 100 | 14 | 40.580 | 9 | 5.964e-06 | 0.007199 | 0.55 |
| 125 | 14 | 40.580 | 9 | 5.964e-06 | 0.007299 | 0.55 |

## Verdict on Shawn's GS-side hypothesis

- Dominant GS FP-side category at >50 m: `number` (4 / 16 = 25.0 %)
- water-feature share on GS FP-side at >50 m: 12.5 %
- number + benchmark (spot-height proxy) share on GS FP-side at >50 m: 50.0 %
- Cross-corpus chi-square (Monte Carlo) p-value: 0.0107

The GS FP-side distribution differs significantly from the 55-map text-track aggregate at the primary threshold. Inspect the per-category Pearson residuals above to see which categories drive the divergence.

## Threshold sensitivity

| Threshold (m) | n_fp | dominant category | dominant share |
|---:|---:|---|---:|
| 25 | 22 | `number` | 36.4 % |
| 50 | 16 | `number` | 25.0 % |
| 75 | 14 | `benchmark` | 28.6 % |
| 100 | 14 | `benchmark` | 28.6 % |
| 125 | 14 | `benchmark` | 28.6 % |

Dominant-category share is threshold-stable across the sweep (range < 15 percentage points).

## Caveats and methodological notes

- **Single-pass classification, no consensus.** Each detection is classified once at temperature 0.0, thinking_level=minimal. Gemini 3 Flash class assignment may be noisy in ambiguous centres. The confidence-weighted distribution in `category_distribution.json` provides a sensitivity check; results should be read as a coarse first-pass profile, not a precise per-class accounting.
- **Different mechanisms, comparable rigour.** The 55-map FP set comes from human reviewers overriding noisy student-GT geometric labels at the per-detection step. The GS FP set comes from geometric filtering against a triple-checked sub-metre curator GT, with the human work done upstream during GT centring. Both sides defensibly produce a curator-grade FP set; framing the GS filter as a "shortcut" or "proxy" misreads the upstream investment in GT precision (plan section 2).
- **Number = spot-height confound.** Soviet 1:50,000 maps render spot-heights as numeric elevation labels - the same `number` category that captures the distractor-pull arm of Shawn's 55-map hypothesis. Cross-corpus, identical `number` share on GS vs 55-map text-track does not by itself discriminate label distractor-pull from spot-height ambiguity; rationale-string review is required for that disambiguation.
- **Crop-centre ambiguity.** Some detections sit in dense map regions where multiple categories are plausible near the 150 m crop centre. The model is asked to pick the strongest burial-mound-confusable feature; the resulting category may differ from a strict "closest-to-centre" reading.
- **Per-map analysis is not powered.** The Lesovo sheet (K-35-078-1) carries only ~11 detections in the verified-v1 set, leaving < 2 FPs at any threshold. Per-corpus reporting is the only meaningful unit; per-map breakdowns are not reported (plan section 6.4).
- **Small N on GS FP-side.** At the primary threshold the GS FP bucket has n=16. Chi-square expected counts fall below 5 in some cells; the report uses a Monte Carlo p-value as a robustness check when this happens (plan section 13.3). Per-category Pearson residuals should be interpreted with the small-N caveat in mind.

## Findable later

Search terms: GS FP-class classification, Obs 302 follow-up, cross-corpus comparator, distance-from-curator-GT primary 50 m, sensitivity sweep 25 50 75 100 125 m, Soviet 1980s topographic categories closed list, Gemini 3 Flash 150 m crop classification, TP-side reliability check, water-feature spot-height GS failure mode, sub-metre curator GT precision.
