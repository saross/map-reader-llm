# 55-map FP-class classification — Obs 296 Diagnostic Test #2 (v2)

_Generated 2026-05-03 00:56 UTC_

Tests Shawn's hypothesis (Obs 296) that 55-map false positives concentrate on numbers / benchmarks (distractor-pull failure mode), while the gold-standard (GS) calibration corpus surfaces a different mode (spot-heights / water features). The original Test #2 was blocked by the review CSV's collapsed `symbol_type` column (Obs 300); this run substitutes a Vision Language Model (VLM) classification pass on rendered 150 m crops, asking Gemini 3 Flash to apply Soviet-1980s topographic-symbol categories directly.

## Methodology change (v2 vs v1)

v1 (archived at `archive/55maps-fp-classification-v1-pre-burial-mound-list/`) used a 10-category FP-only closed list: `number, benchmark, water-feature, contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid, none, other`. There was no `burial-mound` category. The 55-map analysis is FP-only by design — every input row carries `human_label == "not_mound"`, i.e., human-confirmed non-mound — so the v1 list was defensible for this corpus alone.

v2 mirrors the parallel gold-standard (GS) re-run of the same date by appending four Soviet 1980s burial-mound symbols: `burial-mound`, `benchmark-on-burial-mound`, `triangulation-point-on-burial-mound`, `settlement-mound`. Cross-corpus chi-square comparisons in the paper draw on identical category sets, so the 55-map list must mirror the GS list. Any 55-map FP that v2 reclassifies as a burial-mound category indicates a review-pass false-FP label (a real mound accidentally clicked "not_mound") and is itself a finding — see the v1-vs-v2 comparison section below.

## Method

1. Enumerated FPs from the four corrected 55-map review CSVs (`human_label == "not_mound"`).
2. Rendered 150x150 m crops on-the-fly from the source GeoTIFFs (`inputs/rasters/Russian1981_32635/`) using the live-raster pipeline mirrored from `scripts/review_candidates.py`.
3. Classified each crop via Gemini 3 Flash (flex tier, thinking_level=minimal, temperature=0.0). Closed-list categories (v2, 14 entries): number, benchmark, water-feature, contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid, burial-mound, benchmark-on-burial-mound, triangulation-point-on-burial-mound, settlement-mound, none, other.
4. Tabulated per-corpus distributions; ran a chi-square test on image vs text-track aggregate distribution.

Total classified: 1122 (failed/skipped: 0). Wall-clock: 160.7 s (2.7 m). Estimated API cost: $0.5821 USD (flex tier).

## Per-corpus distribution

| Category | T0.3 | T0.7 | image | text-MIN | aggregate |
|---|---:|---:|---:|---:|---:|
| number | 31 (10.4 %) | 25 (8.9 %) | 46 (16.3 %) | 26 (10.0 %) | 128 (11.4 %) |
| benchmark | 6 (2.0 %) | 4 (1.4 %) | 2 (0.7 %) | 2 (0.8 %) | 14 (1.2 %) |
| water-feature | 25 (8.4 %) | 28 (10.0 %) | 29 (10.2 %) | 48 (18.4 %) | 130 (11.6 %) |
| contour-ring | 110 (37.0 %) | 106 (37.7 %) | 89 (31.4 %) | 68 (26.1 %) | 373 (33.2 %) |
| vegetation | 29 (9.8 %) | 23 (8.2 %) | 24 (8.5 %) | 24 (9.2 %) | 100 (8.9 %) |
| settlement | 35 (11.8 %) | 46 (16.4 %) | 35 (12.4 %) | 33 (12.6 %) | 149 (13.3 %) |
| road-or-track | 6 (2.0 %) | 2 (0.7 %) | 6 (2.1 %) | 4 (1.5 %) | 18 (1.6 %) |
| scale-bar-or-grid | 3 (1.0 %) | 1 (0.4 %) | 0 (0.0 %) | 1 (0.4 %) | 5 (0.4 %) |
| burial-mound | 8 (2.7 %) | 6 (2.1 %) | 3 (1.1 %) | 6 (2.3 %) | 23 (2.0 %) |
| benchmark-on-burial-mound | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) |
| triangulation-point-on-burial-mound | 9 (3.0 %) | 5 (1.8 %) | 11 (3.9 %) | 12 (4.6 %) | 37 (3.3 %) |
| settlement-mound | 33 (11.1 %) | 33 (11.7 %) | 25 (8.8 %) | 28 (10.7 %) | 119 (10.6 %) |
| none | 1 (0.3 %) | 0 (0.0 %) | 11 (3.9 %) | 4 (1.5 %) | 16 (1.4 %) |
| other | 1 (0.3 %) | 2 (0.7 %) | 2 (0.7 %) | 5 (1.9 %) | 10 (0.9 %) |
| **N (FPs)** | **297** | **281** | **283** | **261** | **1122** |

## v1-vs-v2 aggregate comparison

How did the four added burial-mound categories shift the 55-map FP profile? Each row shows the v1 aggregate count and share alongside the v2 aggregate. Burial-mound categories were not in v1 — any v2 mass on those rows reflects FPs that v1 had to assign to the closest non-burial-mound category (typically `contour-ring` for the round mound symbol or `settlement` for the angular tell symbol).

| Category | v1 n | v1 % | v2 n | v2 % | Δ (v2 − v1) pp |
|---|---:|---:|---:|---:|---:|
| number | 214 | 19.1 % | 128 | 11.4 % | -7.7 |
| benchmark | 54 | 4.8 % | 14 | 1.2 % | -3.6 |
| water-feature | 136 | 12.2 % | 130 | 11.6 % | -0.6 |
| contour-ring | 458 | 40.9 % | 373 | 33.2 % | -7.7 |
| vegetation | 64 | 5.7 % | 100 | 8.9 % | +3.2 |
| settlement | 157 | 14.0 % | 149 | 13.3 % | -0.8 |
| road-or-track | 13 | 1.2 % | 18 | 1.6 % | +0.4 |
| scale-bar-or-grid | 2 | 0.2 % | 5 | 0.4 % | +0.3 |
| **burial-mound** | — | — | 23 | 2.0 % | +2.0 (new) |
| **benchmark-on-burial-mound** | — | — | 0 | 0.0 % | +0.0 (new) |
| **triangulation-point-on-burial-mound** | — | — | 37 | 3.3 % | +3.3 (new) |
| **settlement-mound** | — | — | 119 | 10.6 % | +10.6 (new) |
| none | 7 | 0.6 % | 16 | 1.4 % | +0.8 |
| other | 14 | 1.3 % | 10 | 0.9 % | -0.4 |
| **N (FPs)** | **1119** | — | **1122** | — | — |

**Total v2 mass on the four burial-mound categories: 179 / 1122 FPs (16.0 %).**

**FINDING:** 179 FPs (16.0 %) reclassify as burial-mound categories under v2. This exceeds the < 1 % calibration-noise threshold and indicates a non-trivial rate of review-pass false-FP labels (real mounds accidentally clicked "not_mound" by the reviewer). Per-FP records are in `fp_classifications.json` (filter on `category in {burial-mound, benchmark-on-burial-mound, triangulation-point-on-burial-mound, settlement-mound}`); manual review of these crops is the natural follow-up.

## Distractor-pull share (number + benchmark)

Shawn's hypothesis predicts 55-map FPs concentrate on **number + benchmark** (Soviet 1980s spot-elevation labels and survey markers).

| Run | number + benchmark | share | n_FPs |
|---|---:|---:|---:|
| T0.3 | 37 | 12.5 % | 297 |
| T0.7 | 29 | 10.3 % | 281 |
| image | 48 | 17.0 % | 283 |
| text-MIN | 28 | 10.7 % | 261 |
| **text-track aggregate** | **94** | **11.2 %** | **839** |
| **image** | **48** | **17.0 %** | **283** |

## GS-failure-mode share (water-feature)

Shawn's hypothesis predicts the GS calibration corpus would have produced FPs on **spot-heights and water features**. Note that on Soviet maps a spot-height usually presents as a numeric label (sometimes plus a benchmark) — the closed list categorises elevation digits as `number` rather than as a separate spot-height bucket. This row therefore reports only the second arm of the GS prediction (water-feature). The first arm (numbers as spot-heights) is folded into the distractor-pull row above; under Shawn's hypothesis, 55-map number-prevalence reflects label distractor-pull, while GS would-be number-prevalence reflects spot-height ambiguity. The diagnostic alone cannot tell those apart without GS data — flagged as a methodological caveat.

| Run | water-feature | share |
|---|---:|---:|
| T0.3 | 25 | 8.4 % |
| T0.7 | 28 | 10.0 % |
| image | 29 | 10.2 % |
| text-MIN | 48 | 18.4 % |

## Chi-square test — image vs text-track

- chi-squared statistic: 31.808
- degrees of freedom: 12
- p-value: 0.001482
- n (image): 283
- n (text-track aggregate): 839
- categories used: number, benchmark, water-feature, contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid, burial-mound, triangulation-point-on-burial-mound, settlement-mound, none, other

### Per-category Pearson residuals

Pearson residuals (observed − expected) / √expected indicate which categories drive the difference. |residual| > 2 is the conventional threshold for a meaningful per-cell effect.

| Category | image obs | image exp | image residual | text obs | text exp | text residual |
|---|---:|---:|---:|---:|---:|---:|
| number | 46 | 32.3 | +2.41 | 82 | 95.7 | -1.40 |
| benchmark | 2 | 3.5 | -0.81 | 12 | 10.5 | +0.47 |
| water-feature | 29 | 32.8 | -0.66 | 101 | 97.2 | +0.38 |
| contour-ring | 89 | 94.1 | -0.52 | 284 | 278.9 | +0.30 |
| vegetation | 24 | 25.2 | -0.24 | 76 | 74.8 | +0.14 |
| settlement | 35 | 37.6 | -0.42 | 114 | 111.4 | +0.24 |
| road-or-track | 6 | 4.5 | +0.69 | 12 | 13.5 | -0.40 |
| scale-bar-or-grid | 0 | 1.3 | -1.12 | 5 | 3.7 | +0.65 |
| burial-mound | 3 | 5.8 | -1.16 | 20 | 17.2 | +0.68 |
| triangulation-point-on-burial-mound | 11 | 9.3 | +0.55 | 26 | 27.7 | -0.32 |
| settlement-mound | 25 | 30.0 | -0.92 | 94 | 89.0 | +0.53 |
| none | 11 | 4.0 | +3.47 | 5 | 12.0 | -2.01 |
| other | 2 | 2.5 | -0.33 | 8 | 7.5 | +0.19 |

## Verdict on Shawn's hypothesis

**MIXED** — image-vs-text distributions differ significantly, but text-track distractor-pull share does not exceed 30 %; the dominant 55-map FP class on text-track is something other than number/benchmark.

- Text-track aggregate (number + benchmark) share: 11.2 %
- Image-track (number + benchmark) share: 17.0 %
- Chi-square p-value (image vs text-track): 0.001482

### Comparison with v1 verdict

v1 verdict: **NOT SUPPORTED — text-track distractor-pull share is below 30 %, and image-vs-text-track chi-square is non-significant.**

- v1 text-track distractor-pull share: 22.7 % (v2: 11.2 %)
- v1 image-track distractor-pull share: 27.6 % (v2: 17.0 %)
- v1 chi-square p-value: 0.1474 (v2: 0.001482)

v1 and v2 verdicts agree on the headline question: Shawn's distractor-pull-on-text-track hypothesis is not supported under both closed lists. The closed-list expansion did not change the hypothesis-testing outcome.

## Caveats and methodological notes

- **Single-pass classification, no consensus.** Each FP is classified once at temperature 0.0, thinking_level=minimal. Gemini 3 Flash class assignment may be noisy in ambiguous centres (e.g. crops with multiple plausible features near centre). The confidence-weighted distribution in `category_distribution.json` provides a sensitivity check; results should be read as a coarse first-pass profile, not a precise per-class accounting.
- **No GS comparator.** The diagnostic compares the four 55-map runs against each other, not against the GS corpus. The headline hypothesis (55-map vs GS asymmetric failure modes) is tested only on the 55-map side; the GS half is inferred from Shawn's prior manual review (Obs 296). A direct GS-side classification is the natural follow-up.
- **Number = spot-height confound.** Soviet 1:50,000 maps render spot-heights as numeric elevation labels — the same `number` category that captures the distractor-pull arm of Shawn's 55-map hypothesis. The two arms are not separable by this classification alone; the cross-corpus picture (55-map number-prevalence as label distractor-pull vs GS number-prevalence as spot-height ambiguity) is a paper interpretation, not a measurement.
- **Crop-centre ambiguity.** Some FPs sit in dense map regions where multiple categories are plausible near the 150 m crop centre. The model is asked to pick the strongest burial-mound-confusable feature; the resulting category may differ from a strict "closest-to-centre" reading.
- **Prompt vocabulary anchor.** The prompt names Soviet 1980s topographic categories explicitly. This is a deliberate departure from the detection-prompt convention (visual-feature naming without cartographic vocabulary); for FP classification we WANT the model to apply its cartographic knowledge. Generic vs Soviet category mismatch was guarded against by including a Cyrillic example ("БМ") in the prompt.

## Findable later

Search terms: 55-map FP-class classification, Obs 296 Test #2, cartographic-naming approach, Gemini 3 Flash 150 m crop classification, distractor-pull text-track number benchmark, chi-square image vs text-track, water-feature spot-height GS failure mode, Soviet 1980s topographic categories closed list, rendered crop in-memory base64, flex tier classification single-pass, confidence-weighted distribution sensitivity, 55-map FP v2 burial-mound closed list, cross-corpus consistency with parallel GS re-run, review-pass false-FP labels.

