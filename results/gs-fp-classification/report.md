# GS FP-class classification (Obs 302 follow-up, v2)

_Generated 2026-04-29 12:52 UTC_

Closes the comparator gap flagged in `results/55maps-fp-classification/report.md` Caveats - the 55-map driver tested Shawn's hypothesis (Obs 296) on one corpus but lacked the GS-side measurement to make a clean cross-corpus claim. This run applies a Soviet-1980s closed-list classifier to all 371 detections in the GS verified-v1 full-scope set (`outputs/h11/gold-standard-v2/verified-v1/verified_detections_full-scope.geojson`), partitioning into TP-side (<= 50 m from a curator GT mound) and FP-side (> 50 m) post-classification. Plan reference: `planning/gs-fp-classification-plan-2026-04-29.md` (commit `edd2ecce`). v2 expands the closed list to include four burial-mound categories (see the Methodology change section below); v1 outputs are archived at `archive/gs-fp-classification-v1-pre-burial-mound-list/`.

## Methodology change vs v1 (closed-list expansion)

v1 (commits `6037b390` + `ee4f18cb`, 2026-04-29) inherited the 55-map sibling driver's FP-only closed list verbatim: `number, benchmark, water-feature, contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid, none, other`. When v1 was repurposed to classify all 371 GS detections (TP-side included, per plan section 6.5's reliability sanity check), real mounds had no proper category to map onto and fell back to visual proxies (v1 TP-side: `contour-ring` 60.0 %, `number` 15.2 %; the script's > 10 % vocabulary-leakage warning fired). Soviet 1:50,000 legends do contain burial-mound symbols (oval brown ring, sometimes with a marker glyph); the v1 omission was a script-design issue, not a classifier hallucination.

v2 adds four burial-mound categories so the closed list correctly covers the TP-side: `burial-mound` (ordinary mound glyph), `benchmark-on-burial-mound` (mound with a benchmark marker on top), `triangulation-point-on-burial-mound` (mound with a triangulation marker on top), and `settlement-mound` (tell or large mound associated with archaeological settlement remains). The non-mound categories from `number` through `other` retain their v1 names and ordering for direct comparability with the v1 archived tables. v1 outputs are preserved at `archive/gs-fp-classification-v1-pre-burial-mound-list/` with an `ARCHIVE-NOTE.md` explaining the supersession.

## Methodology - different mechanisms, comparable rigour

The 55-map sibling driver derives its FP set from human reviewer overrides (`human_label == "not_mound"`) on noisy student GT (`student-mounds-55maps-reviewed.geojson`, ~25 m positional jitter). The GS pipeline has no equivalent per-detection review step, but the GS curator GT (`inputs/vectors/references/mounds-reference.geojson`, 569 mounds) was triple-checked and manually re-centred to within ~1 px of each mound's true centre during Sobotkova 2022 + this project's reverify pass - sub-metre positional precision. Distance-from-curator-GT is therefore not a proxy on the GS corpus; it is a high-precision geometric filter. See plan section 2 for the full framing.

## Method

1. Loaded all 371 detections from the verified-v1 GeoJSON and 569 curator GT mounds (MultiPoint -> Point exploded). Both files are EPSG:32635, no reprojection.
2. Computed Euclidean planar distance from each detection to its nearest reference Point via `scipy.spatial.cKDTree` (precedent: `scripts/analyse_attractor_pull_gs.py`).
3. Rendered 150 x 150 m crops on-the-fly from the four GS GeoTIFFs at `inputs/rasters/` (K-35-052-4, K-35-053-3, K-35-062-2, K-35-078-1) using the live-raster pipeline mirrored from `scripts/review_candidates.py`.
4. Classified each crop via Gemini 3 Flash (flex tier, thinking_level=minimal, temperature=0.0). Closed-list categories (v2 — burial-mound classes added at the front; see Methodology change above): burial-mound, benchmark-on-burial-mound, triangulation-point-on-burial-mound, settlement-mound, number, benchmark, water-feature, contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid, none, other.
5. Partitioned results post-hoc into TP-side (<= 50 m) and FP-side (> threshold) buckets at thresholds [25, 50, 75, 100, 125] m. The classification pass is a single census; the threshold sweep is a post-classification aggregation. See plan section 6 for the rationale for classifying TP-side detections as well (reliability sanity check).
6. Cross-corpus chi-square test against the 55-map text-track aggregate (`results/55maps-fp-classification/category_distribution.json`).

Total classified: 371 / 371 (failed/skipped: 0). Wall-clock: 310.3 s (5.2 m). Estimated API cost: $0.1950 USD (flex tier).

## Distribution by distance-from-curator-GT stratum

The TP-side and FP-side rows below are partitioned at each sensitivity-sweep threshold so the user can see how the FP-class distribution shifts as the threshold tightens or relaxes. The primary threshold is 50 m (plan section 5.2).

| Category | TP (<=50 m) | FP (>25 m) | FP (>50 m) | FP (>75 m) | FP (>100 m) | FP (>125 m) |
|---|---:|---:|---:|---:|---:|---:|
| burial-mound | 124 (34.9 %) | 5 (22.7 %) | 4 (25.0 %) | 3 (21.4 %) | 3 (21.4 %) | 3 (21.4 %) |
| benchmark-on-burial-mound | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) |
| triangulation-point-on-burial-mound | 70 (19.7 %) | 4 (18.2 %) | 3 (18.8 %) | 3 (21.4 %) | 3 (21.4 %) | 3 (21.4 %) |
| settlement-mound | 8 (2.3 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) |
| number | 24 (6.8 %) | 3 (13.6 %) | 2 (12.5 %) | 1 (7.1 %) | 1 (7.1 %) | 1 (7.1 %) |
| benchmark | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) |
| water-feature | 8 (2.3 %) | 2 (9.1 %) | 2 (12.5 %) | 2 (14.3 %) | 2 (14.3 %) | 2 (14.3 %) |
| contour-ring | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) |
| vegetation | 45 (12.7 %) | 1 (4.5 %) | 1 (6.2 %) | 1 (7.1 %) | 1 (7.1 %) | 1 (7.1 %) |
| settlement | 7 (2.0 %) | 2 (9.1 %) | 2 (12.5 %) | 2 (14.3 %) | 2 (14.3 %) | 2 (14.3 %) |
| road-or-track | 0 (0.0 %) | 1 (4.5 %) | 1 (6.2 %) | 1 (7.1 %) | 1 (7.1 %) | 1 (7.1 %) |
| scale-bar-or-grid | 1 (0.3 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) |
| none | 0 (0.0 %) | 1 (4.5 %) | 1 (6.2 %) | 1 (7.1 %) | 1 (7.1 %) | 1 (7.1 %) |
| other | 68 (19.2 %) | 3 (13.6 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) |
| **N** | **355** | **22** | **16** | **14** | **14** | **14** |

## TP-side reliability check (plan section 6.5, v2)

Under the v2 closed list (which includes the four burial-mound categories), a well-calibrated classifier should assign mostly `burial-mound` (or one of the other three burial-mound classes) to TP-side detections - real mounds centred under their crops now have a correct category to map onto. v2 reverses the v1 expectation: under v1's closed list there was no mound category, so the v1 reliability check looked for `none` + `other` dominance and flagged any vocabulary category > 10 % as leakage. Under v2 the expectation is that the four burial-mound categories together dominate the TP-side; non-mound categories (number, benchmark, contour-ring, etc.) on the TP-side are now the leakage signal of interest.

- TP-side n: 355
- `burial-mound` + `benchmark-on-burial-mound` + `triangulation-point-on-burial-mound` + `settlement-mound` share on TP-side: 56.9 % (202 / 355)
- `none` + `other` share on TP-side: 19.2 % (0 + 68 / 355)

TP-side per-category counts (v2 closed list):

| Category | n | share |
|---|---:|---:|
| `burial-mound` | 124 | 34.9 % |
| `benchmark-on-burial-mound` | 0 | 0.0 % |
| `triangulation-point-on-burial-mound` | 70 | 19.7 % |
| `settlement-mound` | 8 | 2.3 % |
| `number` | 24 | 6.8 % |
| `benchmark` | 0 | 0.0 % |
| `water-feature` | 8 | 2.3 % |
| `contour-ring` | 0 | 0.0 % |
| `vegetation` | 45 | 12.7 % |
| `settlement` | 7 | 2.0 % |
| `road-or-track` | 0 | 0.0 % |
| `scale-bar-or-grid` | 1 | 0.3 % |
| `none` | 0 | 0.0 % |
| `other` | 68 | 19.2 % |
| **N** | **355** | |

- WARNING: non-mound vocabulary leakage on TP-side > 10 %: vegetation (12.7 %). Some real mounds were labelled as a non-mound feature - inspect the per-detection rationale strings in `fp_classifications.json` for borderline cases (plan section 13.7).

### v1 vs v2 TP-side comparison

Side-by-side TP-side category share for v1 (no burial-mound categories in the closed list) and v2 (this run). v2 is expected to consolidate v1's `contour-ring` and `number` leakage onto the burial-mound categories; the non-mound categories should drop sharply on the TP-side.

| Category | v1 share (n=355) | v2 share | v2 n |
|---|---:|---:|---:|
| `burial-mound` | — | 34.9 % | 124 |
| `benchmark-on-burial-mound` | — | 0.0 % | 0 |
| `triangulation-point-on-burial-mound` | — | 19.7 % | 70 |
| `settlement-mound` | — | 2.3 % | 8 |
| `number` | 15.2 % | 6.8 % | 24 |
| `benchmark` | 8.5 % | 0.0 % | 0 |
| `water-feature` | 0.6 % | 2.3 % | 8 |
| `contour-ring` | 60.0 % | 0.0 % | 0 |
| `vegetation` | 9.0 % | 12.7 % | 45 |
| `settlement` | 5.9 % | 2.0 % | 7 |
| `road-or-track` | 0.0 % | 0.0 % | 0 |
| `scale-bar-or-grid` | 0.0 % | 0.3 % | 1 |
| `none` | 0.0 % | 0.0 % | 0 |
| `other` | 0.8 % | 19.2 % | 68 |
| **N** | **355** | | **355** |

## Distractor-pull share (number + benchmark)

Shawn's 55-map hypothesis predicted high `number + benchmark` share (Soviet 1980s spot-elevation labels and survey markers); the 55-map result was instead `contour-ring`-dominant (Obs 302). On the GS side, Shawn's intuition was that water-features and spot-heights (= `number` in this vocabulary) would dominate. The table below tests both arms by threshold.

| Bucket | number + benchmark | share | water-feature | share | n |
|---|---:|---:|---:|---:|---:|
| TP (<=50 m) | 24 | 6.8 % | 8 | 2.3 % | 355 |
| FP (>25 m) | 3 | 13.6 % | 2 | 9.1 % | 22 |
| FP (>50 m) | 2 | 12.5 % | 2 | 12.5 % | 16 |
| FP (>75 m) | 1 | 7.1 % | 2 | 14.3 % | 14 |
| FP (>100 m) | 1 | 7.1 % | 2 | 14.3 % | 14 |
| FP (>125 m) | 1 | 7.1 % | 2 | 14.3 % | 14 |

## Cross-corpus comparison vs 55-map text-track aggregate

Headline cross-corpus contrast: GS FP at the primary threshold (> 50 m, n=16) versus the 55-map text-track aggregate (sum of T0.3, T0.7, text-MIN runs from `results/55maps-fp-classification/category_distribution.json`).

| Category | GS FP (>50 m) | GS share | 55-map text-track | 55-map share |
|---|---:|---:|---:|---:|
| burial-mound | 4 | 25.0 % | 20 | 2.4 % |
| benchmark-on-burial-mound | 0 | 0.0 % | 0 | 0.0 % |
| triangulation-point-on-burial-mound | 3 | 18.8 % | 26 | 3.1 % |
| settlement-mound | 0 | 0.0 % | 92 | 11.0 % |
| number | 2 | 12.5 % | 78 | 9.3 % |
| benchmark | 0 | 0.0 % | 12 | 1.4 % |
| water-feature | 2 | 12.5 % | 102 | 12.2 % |
| contour-ring | 0 | 0.0 % | 288 | 34.4 % |
| vegetation | 1 | 6.2 % | 75 | 9.0 % |
| settlement | 2 | 12.5 % | 113 | 13.5 % |
| road-or-track | 1 | 6.2 % | 12 | 1.4 % |
| scale-bar-or-grid | 0 | 0.0 % | 5 | 0.6 % |
| none | 1 | 6.2 % | 5 | 0.6 % |
| other | 0 | 0.0 % | 8 | 1.0 % |
| **N** | **16** | | **836** | |

### Chi-square test - GS FP at primary threshold vs 55-map text-track

- chi-squared statistic: 57.337
- degrees of freedom: 12
- p-value: 6.87e-08
- n (gs): 16
- n (fifty_five): 836
- categories retained (non-zero across both rows): burial-mound, triangulation-point-on-burial-mound, settlement-mound, number, benchmark, water-feature, contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid, none, other
- low-expected-count fraction (< 5): 0.50
- Monte Carlo p-value (10000 resamples): 0.0012 (small-N robustness check; per plan §13.3 the asymptotic p-value is unreliable when many cells have expected counts < 5)

### Per-category Pearson residuals

Pearson residuals (observed - expected) / sqrt(expected) indicate which categories drive the difference. |residual| > 2 is the conventional threshold for a meaningful per-cell effect.

| Category | gs obs | gs exp | gs residual | fifty_five obs | fifty_five exp | fifty_five residual |
|---|---:|---:|---:|---:|---:|---:|
| burial-mound | 4 | 0.5 | +5.29 | 20 | 23.5 | -0.73 |
| triangulation-point-on-burial-mound | 3 | 0.5 | +3.33 | 26 | 28.5 | -0.46 |
| settlement-mound | 0 | 1.7 | -1.31 | 92 | 90.3 | +0.18 |
| number | 2 | 1.5 | +0.41 | 78 | 78.5 | -0.06 |
| benchmark | 0 | 0.2 | -0.47 | 12 | 11.8 | +0.07 |
| water-feature | 2 | 2.0 | +0.03 | 102 | 102.0 | -0.01 |
| contour-ring | 0 | 5.4 | -2.33 | 288 | 282.6 | +0.32 |
| vegetation | 1 | 1.4 | -0.36 | 75 | 74.6 | +0.05 |
| settlement | 2 | 2.2 | -0.11 | 113 | 112.8 | +0.01 |
| road-or-track | 1 | 0.2 | +1.53 | 12 | 12.8 | -0.21 |
| scale-bar-or-grid | 0 | 0.1 | -0.31 | 5 | 4.9 | +0.04 |
| none | 1 | 0.1 | +2.64 | 5 | 5.9 | -0.37 |
| other | 0 | 0.1 | -0.39 | 8 | 7.8 | +0.05 |

### Headline FP-side at the deepest stratum (>125 m)

The strictest FP filter in the sensitivity sweep (>125 m). No detection within 125 m of any curator GT mound contaminates the FP bucket - the cleanest apples-to-apples comparator with the 55-map text-track aggregate (which is itself bounded by per-detection human review rather than by geometric distance).

| Category | GS FP (>125 m) | GS share | 55-map text-track | 55-map share |
|---|---:|---:|---:|---:|
| `burial-mound` | 3 | 21.4 % | 20 | 2.4 % |
| `benchmark-on-burial-mound` | 0 | 0.0 % | 0 | 0.0 % |
| `triangulation-point-on-burial-mound` | 3 | 21.4 % | 26 | 3.1 % |
| `settlement-mound` | 0 | 0.0 % | 92 | 11.0 % |
| `number` | 1 | 7.1 % | 78 | 9.3 % |
| `benchmark` | 0 | 0.0 % | 12 | 1.4 % |
| `water-feature` | 2 | 14.3 % | 102 | 12.2 % |
| `contour-ring` | 0 | 0.0 % | 288 | 34.4 % |
| `vegetation` | 1 | 7.1 % | 75 | 9.0 % |
| `settlement` | 2 | 14.3 % | 113 | 13.5 % |
| `road-or-track` | 1 | 7.1 % | 12 | 1.4 % |
| `scale-bar-or-grid` | 0 | 0.0 % | 5 | 0.6 % |
| `none` | 1 | 7.1 % | 5 | 0.6 % |
| `other` | 0 | 0.0 % | 8 | 1.0 % |
| **N** | **14** | | **836** | |

- chi-squared statistic: 50.231
- degrees of freedom: 12
- p-value: 1.272e-06
- n (gs): 14
- n (fifty_five): 836
- categories retained (non-zero across both rows): burial-mound, triangulation-point-on-burial-mound, settlement-mound, number, benchmark, water-feature, contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid, none, other
- low-expected-count fraction (< 5): 0.54
- Monte Carlo p-value (10000 resamples): 0.0028 (small-N robustness check; per plan §13.3 the asymptotic p-value is unreliable when many cells have expected counts < 5)

### Per-category Pearson residuals (>125 m stratum)

Pearson residuals (observed - expected) / sqrt(expected) indicate which categories drive the difference. |residual| > 2 is the conventional threshold for a meaningful per-cell effect.

| Category | gs obs | gs exp | gs residual | fifty_five obs | fifty_five exp | fifty_five residual |
|---|---:|---:|---:|---:|---:|---:|
| burial-mound | 3 | 0.4 | +4.26 | 20 | 22.6 | -0.55 |
| triangulation-point-on-burial-mound | 3 | 0.5 | +3.65 | 26 | 28.5 | -0.47 |
| settlement-mound | 0 | 1.5 | -1.23 | 92 | 90.5 | +0.16 |
| number | 1 | 1.3 | -0.26 | 78 | 77.7 | +0.03 |
| benchmark | 0 | 0.2 | -0.45 | 12 | 11.8 | +0.06 |
| water-feature | 2 | 1.7 | +0.22 | 102 | 102.3 | -0.03 |
| contour-ring | 0 | 4.7 | -2.18 | 288 | 283.3 | +0.28 |
| vegetation | 1 | 1.3 | -0.23 | 75 | 74.7 | +0.03 |
| settlement | 2 | 1.9 | +0.08 | 113 | 113.1 | -0.01 |
| road-or-track | 1 | 0.2 | +1.70 | 12 | 12.8 | -0.22 |
| scale-bar-or-grid | 0 | 0.1 | -0.29 | 5 | 4.9 | +0.04 |
| none | 1 | 0.1 | +2.87 | 5 | 5.9 | -0.37 |
| other | 0 | 0.1 | -0.36 | 8 | 7.9 | +0.05 |

### Cross-corpus chi-square at every sweep threshold

Re-running the same chi-square contingency at each threshold in the sensitivity sweep. The >125 m row is the strictest FP filter (no detection within 125 m of any curator GT mound) and serves as the apples-to-apples comparator alongside the 50 m primary.

| Threshold (m) | n_gs | chi2 | dof | asymp p | Monte Carlo p | low_exp_frac |
|---:|---:|---:|---:|---:|---:|---:|
| 25 | 22 | 89.199 | 12 | 7.054e-14 | 9.999e-05 | 0.50 |
| 50 | 16 | 57.337 | 12 | 6.87e-08 | 0.0012 | 0.50 |
| 75 | 14 | 50.231 | 12 | 1.272e-06 | 0.0036 | 0.54 |
| 100 | 14 | 50.231 | 12 | 1.272e-06 | 0.0036 | 0.54 |
| 125 | 14 | 50.231 | 12 | 1.272e-06 | 0.0028 | 0.54 |

## Verdict on Shawn's GS-side hypothesis

- Dominant GS FP-side category at >50 m: `burial-mound` (4 / 16 = 25.0 %)
- water-feature share on GS FP-side at >50 m: 12.5 %
- number + benchmark (spot-height proxy) share on GS FP-side at >50 m: 12.5 %
- Cross-corpus chi-square (Monte Carlo) p-value at >50 m: 0.0012
- Dominant GS FP-side category at >125 m: `burial-mound` (3 / 14 = 21.4 %)
- Cross-corpus chi-square (Monte Carlo) p-value at >125 m: 0.0028

The GS FP-side distribution differs significantly from the 55-map text-track aggregate at the primary threshold. Inspect the per-category Pearson residuals above to see which categories drive the divergence.

## Threshold sensitivity

| Threshold (m) | n_fp | dominant category | dominant share |
|---:|---:|---|---:|
| 25 | 22 | `burial-mound` | 22.7 % |
| 50 | 16 | `burial-mound` | 25.0 % |
| 75 | 14 | `burial-mound` | 21.4 % |
| 100 | 14 | `burial-mound` | 21.4 % |
| 125 | 14 | `burial-mound` | 21.4 % |

Dominant-category share is threshold-stable across the sweep (range < 15 percentage points).

## Caveats and methodological notes

- **Single-pass classification, no consensus.** Each detection is classified once at temperature 0.0, thinking_level=minimal. Gemini 3 Flash class assignment may be noisy in ambiguous centres. The confidence-weighted distribution in `category_distribution.json` provides a sensitivity check; results should be read as a coarse first-pass profile, not a precise per-class accounting.
- **Different mechanisms, comparable rigour.** The 55-map FP set comes from human reviewers overriding noisy student-GT geometric labels at the per-detection step. The GS FP set comes from geometric filtering against a triple-checked sub-metre curator GT, with the human work done upstream during GT centring. Both sides defensibly produce a curator-grade FP set; framing the GS filter as a "shortcut" or "proxy" misreads the upstream investment in GT precision (plan section 2).
- **Number = spot-height confound.** Soviet 1:50,000 maps render spot-heights as numeric elevation labels - the same `number` category that captures the distractor-pull arm of Shawn's 55-map hypothesis. Cross-corpus, identical `number` share on GS vs 55-map text-track does not by itself discriminate label distractor-pull from spot-height ambiguity; rationale-string review is required for that disambiguation.
- **Crop-centre ambiguity.** Some detections sit in dense map regions where multiple categories are plausible near the 150 m crop centre. The model is asked to pick the strongest burial-mound-confusable feature; the resulting category may differ from a strict "closest-to-centre" reading.
- **Per-map analysis is not powered.** The Lesovo sheet (K-35-078-1) carries only ~11 detections in the verified-v1 set, leaving < 2 FPs at any threshold. Per-corpus reporting is the only meaningful unit; per-map breakdowns are not reported (plan section 6.4).
- **Small N on GS FP-side.** At the primary threshold the GS FP bucket has n=16. Chi-square expected counts fall below 5 in some cells; the report uses a Monte Carlo p-value as a robustness check when this happens (plan section 13.3). Per-category Pearson residuals should be interpreted with the small-N caveat in mind.

## Findable later

Search terms: GS FP-class classification, Obs 302 follow-up, v2 closed list, burial-mound categories added, benchmark-on-burial-mound, triangulation-point-on-burial-mound, settlement-mound, cross-corpus comparator, distance-from-curator-GT primary 50 m, deepest stratum 125 m, sensitivity sweep 25 50 75 100 125 m, Soviet 1980s topographic categories closed list, Gemini 3 Flash 150 m crop classification, TP-side reliability check (v2 — burial-mound dominance expected), water-feature spot-height GS failure mode, sub-metre curator GT precision, v1 vs v2 TP-side comparison.
