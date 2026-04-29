# 55-map FP-class classification — Obs 296 Diagnostic Test #2

_Generated 2026-04-28 13:33 UTC_

Tests Shawn's hypothesis (Obs 296) that 55-map false positives concentrate on numbers / benchmarks (distractor-pull failure mode), while the gold-standard (GS) calibration corpus surfaces a different mode (spot-heights / water features). The original Test #2 was blocked by the review CSV's collapsed `symbol_type` column (Obs 300); this run substitutes a Vision Language Model (VLM) classification pass on rendered 150 m crops, asking Gemini 3 Flash to apply Soviet-1980s topographic-symbol categories directly.

## Method

1. Enumerated FPs from the four corrected 55-map review CSVs (`human_label == "not_mound"`).
2. Rendered 150x150 m crops on-the-fly from the source GeoTIFFs (`inputs/rasters/Russian1981_32635/`) using the live-raster pipeline mirrored from `scripts/review_candidates.py`.
3. Classified each crop via Gemini 3 Flash (flex tier, thinking_level=minimal, temperature=0.0). Closed-list categories: number, benchmark, water-feature, contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid, none, other.
4. Tabulated per-corpus distributions; ran a chi-square test on image vs text-track aggregate distribution.

Total classified: 1119 (failed/skipped: 0). Wall-clock: 653.6 s (10.9 m). Estimated API cost: $0.5071 USD (flex tier).

## Per-corpus distribution

| Category | T0.3 | T0.7 | image | text-MIN | aggregate |
|---|---:|---:|---:|---:|---:|
| number | 53 (17.8 %) | 49 (17.6 %) | 65 (23.0 %) | 47 (18.0 %) | 214 (19.1 %) |
| benchmark | 17 (5.7 %) | 11 (4.0 %) | 13 (4.6 %) | 13 (5.0 %) | 54 (4.8 %) |
| water-feature | 31 (10.4 %) | 30 (10.8 %) | 31 (11.0 %) | 44 (16.9 %) | 136 (12.2 %) |
| contour-ring | 129 (43.4 %) | 121 (43.5 %) | 112 (39.6 %) | 96 (36.8 %) | 458 (40.9 %) |
| vegetation | 18 (6.1 %) | 18 (6.5 %) | 13 (4.6 %) | 15 (5.7 %) | 64 (5.7 %) |
| settlement | 40 (13.5 %) | 44 (15.8 %) | 37 (13.1 %) | 36 (13.8 %) | 157 (14.0 %) |
| road-or-track | 6 (2.0 %) | 1 (0.4 %) | 3 (1.1 %) | 3 (1.1 %) | 13 (1.2 %) |
| scale-bar-or-grid | 0 (0.0 %) | 1 (0.4 %) | 0 (0.0 %) | 1 (0.4 %) | 2 (0.2 %) |
| none | 0 (0.0 %) | 0 (0.0 %) | 5 (1.8 %) | 2 (0.8 %) | 7 (0.6 %) |
| other | 3 (1.0 %) | 3 (1.1 %) | 4 (1.4 %) | 4 (1.5 %) | 14 (1.3 %) |
| **N (FPs)** | **297** | **278** | **283** | **261** | **1119** |

## Distractor-pull share (number + benchmark)

Shawn's hypothesis predicts 55-map FPs concentrate on **number + benchmark** (Soviet 1980s spot-elevation labels and survey markers).

| Run | number + benchmark | share | n_FPs |
|---|---:|---:|---:|
| T0.3 | 70 | 23.6 % | 297 |
| T0.7 | 60 | 21.6 % | 278 |
| image | 78 | 27.6 % | 283 |
| text-MIN | 60 | 23.0 % | 261 |
| **text-track aggregate** | **190** | **22.7 %** | **836** |
| **image** | **78** | **27.6 %** | **283** |

## GS-failure-mode share (water-feature)

Shawn's hypothesis predicts the GS calibration corpus would have produced FPs on **spot-heights and water features**. Note that on Soviet maps a spot-height usually presents as a numeric label (sometimes plus a benchmark) — the closed list categorises elevation digits as `number` rather than as a separate spot-height bucket. This row therefore reports only the second arm of the GS prediction (water-feature). The first arm (numbers as spot-heights) is folded into the distractor-pull row above; under Shawn's hypothesis, 55-map number-prevalence reflects label distractor-pull, while GS would-be number-prevalence reflects spot-height ambiguity. The diagnostic alone cannot tell those apart without GS data — flagged as a methodological caveat.

| Run | water-feature | share |
|---|---:|---:|
| T0.3 | 31 | 10.4 % |
| T0.7 | 30 | 10.8 % |
| image | 31 | 11.0 % |
| text-MIN | 44 | 16.9 % |

## Chi-square test — image vs text-track

- chi-squared statistic: 13.350
- degrees of freedom: 9
- p-value: 0.1474
- n (image): 283
- n (text-track aggregate): 836
- categories used: number, benchmark, water-feature, contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid, none, other


### Per-category Pearson residuals

Pearson residuals (observed − expected) / √expected indicate which categories drive the difference. |residual| > 2 is the conventional threshold for a meaningful per-cell effect.

| Category | image obs | image exp | image residual | text obs | text exp | text residual |
|---|---:|---:|---:|---:|---:|---:|
| number | 65 | 54.1 | +1.48 | 149 | 159.9 | -0.86 |
| benchmark | 13 | 13.7 | -0.18 | 41 | 40.3 | +0.10 |
| water-feature | 31 | 34.4 | -0.58 | 105 | 101.6 | +0.34 |
| contour-ring | 112 | 115.8 | -0.36 | 346 | 342.2 | +0.21 |
| vegetation | 13 | 16.2 | -0.79 | 51 | 47.8 | +0.46 |
| settlement | 37 | 39.7 | -0.43 | 120 | 117.3 | +0.25 |
| road-or-track | 3 | 3.3 | -0.16 | 10 | 9.7 | +0.09 |
| scale-bar-or-grid | 0 | 0.5 | -0.71 | 2 | 1.5 | +0.41 |
| none | 5 | 1.8 | +2.43 | 2 | 5.2 | -1.41 |
| other | 4 | 3.5 | +0.24 | 10 | 10.5 | -0.14 |

## Verdict on Shawn's hypothesis

**NOT SUPPORTED** — text-track distractor-pull share is below 30 %, and image-vs-text-track chi-square is non-significant. Shawn's predicted asymmetric-failure-mode pattern is not visible in this classification pass.

- Text-track aggregate (number + benchmark) share: 22.7 %
- Image-track (number + benchmark) share: 27.6 %
- Chi-square p-value (image vs text-track): 0.1474

## Caveats and methodological notes

- **Single-pass classification, no consensus.** Each FP is classified once at temperature 0.0, thinking_level=minimal. Gemini 3 Flash class assignment may be noisy in ambiguous centres (e.g. crops with multiple plausible features near centre). The confidence-weighted distribution in `category_distribution.json` provides a sensitivity check; results should be read as a coarse first-pass profile, not a precise per-class accounting.
- **No GS comparator.** The diagnostic compares the four 55-map runs against each other, not against the GS corpus. The headline hypothesis (55-map vs GS asymmetric failure modes) is tested only on the 55-map side; the GS half is inferred from Shawn's prior manual review (Obs 296). A direct GS-side classification is the natural follow-up.
- **Number = spot-height confound.** Soviet 1:50,000 maps render spot-heights as numeric elevation labels — the same `number` category that captures the distractor-pull arm of Shawn's 55-map hypothesis. The two arms are not separable by this classification alone; the cross-corpus picture (55-map number-prevalence as label distractor-pull vs GS number-prevalence as spot-height ambiguity) is a paper interpretation, not a measurement.
- **Crop-centre ambiguity.** Some FPs sit in dense map regions where multiple categories are plausible near the 150 m crop centre. The model is asked to pick the strongest burial-mound-confusable feature; the resulting category may differ from a strict "closest-to-centre" reading.
- **Prompt vocabulary anchor.** The prompt names Soviet 1980s topographic categories explicitly. This is a deliberate departure from the detection-prompt convention (visual-feature naming without cartographic vocabulary); for FP classification we WANT the model to apply its cartographic knowledge. Generic vs Soviet category mismatch was guarded against by including a Cyrillic example ("БМ") in the prompt.

## Findable later

Search terms: 55-map FP-class classification, Obs 296 Test #2, cartographic-naming approach, Gemini 3 Flash 150 m crop classification, distractor-pull text-track number benchmark, chi-square image vs text-track, water-feature spot-height GS failure mode, Soviet 1980s topographic categories closed list, rendered crop in-memory base64, flex tier classification single-pass, confidence-weighted distribution sensitivity.

