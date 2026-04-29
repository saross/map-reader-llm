# 55-map FP-class classification — Obs 296 Diagnostic Test #2 (v2)

_Generated 2026-04-29 12:49 UTC_

Tests Shawn's hypothesis (Obs 296) that 55-map false positives concentrate on numbers / benchmarks (distractor-pull failure mode), while the gold-standard (GS) calibration corpus surfaces a different mode (spot-heights / water features). The original Test #2 was blocked by the review CSV's collapsed `symbol_type` column (Obs 300); this run substitutes a Vision Language Model (VLM) classification pass on rendered 150 m crops, asking Gemini 3 Flash to apply Soviet-1980s topographic-symbol categories directly.

## Methodology change (v2 vs v1)

v1 (archived at `archive/55maps-fp-classification-v1-pre-burial-mound-list/`) used a 10-category FP-only closed list: `number, benchmark, water-feature, contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid, none, other`. There was no `burial-mound` category. The 55-map analysis is FP-only by design — every input row carries `human_label == "not_mound"`, i.e., human-confirmed non-mound — so the v1 list was defensible for this corpus alone.

v2 mirrors the parallel gold-standard (GS) re-run of the same date by appending four Soviet 1980s burial-mound symbols: `burial-mound`, `benchmark-on-burial-mound`, `triangulation-point-on-burial-mound`, `settlement-mound`. Cross-corpus chi-square comparisons in the paper draw on identical category sets, so the 55-map list must mirror the GS list. Any 55-map FP that v2 reclassifies as a burial-mound category indicates a review-pass false-FP label (a real mound accidentally clicked "not_mound") and is itself a finding — see the v1-vs-v2 comparison section below.

## Method

1. Enumerated FPs from the four corrected 55-map review CSVs (`human_label == "not_mound"`).
2. Rendered 150x150 m crops on-the-fly from the source GeoTIFFs (`inputs/rasters/Russian1981_32635/`) using the live-raster pipeline mirrored from `scripts/review_candidates.py`.
3. Classified each crop via Gemini 3 Flash (flex tier, thinking_level=minimal, temperature=0.0). Closed-list categories (v2, 14 entries): number, benchmark, water-feature, contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid, burial-mound, benchmark-on-burial-mound, triangulation-point-on-burial-mound, settlement-mound, none, other.
4. Tabulated per-corpus distributions; ran a chi-square test on image vs text-track aggregate distribution.

Total classified: 1119 (failed/skipped: 0). Wall-clock: 229.8 s (3.8 m). Estimated API cost: $0.5803 USD (flex tier).

## Per-corpus distribution

| Category | T0.3 | T0.7 | image | text-MIN | aggregate |
|---|---:|---:|---:|---:|---:|
| number | 32 (10.8 %) | 22 (7.9 %) | 44 (15.5 %) | 24 (9.2 %) | 122 (10.9 %) |
| benchmark | 6 (2.0 %) | 4 (1.4 %) | 2 (0.7 %) | 2 (0.8 %) | 14 (1.3 %) |
| water-feature | 25 (8.4 %) | 28 (10.1 %) | 29 (10.2 %) | 49 (18.8 %) | 131 (11.7 %) |
| contour-ring | 112 (37.7 %) | 107 (38.5 %) | 94 (33.2 %) | 69 (26.4 %) | 382 (34.1 %) |
| vegetation | 28 (9.4 %) | 24 (8.6 %) | 25 (8.8 %) | 23 (8.8 %) | 100 (8.9 %) |
| settlement | 35 (11.8 %) | 44 (15.8 %) | 33 (11.7 %) | 34 (13.0 %) | 146 (13.0 %) |
| road-or-track | 6 (2.0 %) | 2 (0.7 %) | 5 (1.8 %) | 4 (1.5 %) | 17 (1.5 %) |
| scale-bar-or-grid | 3 (1.0 %) | 1 (0.4 %) | 0 (0.0 %) | 1 (0.4 %) | 5 (0.4 %) |
| burial-mound | 8 (2.7 %) | 6 (2.2 %) | 3 (1.1 %) | 6 (2.3 %) | 23 (2.1 %) |
| benchmark-on-burial-mound | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) |
| triangulation-point-on-burial-mound | 9 (3.0 %) | 5 (1.8 %) | 11 (3.9 %) | 12 (4.6 %) | 37 (3.3 %) |
| settlement-mound | 31 (10.4 %) | 33 (11.9 %) | 25 (8.8 %) | 28 (10.7 %) | 117 (10.5 %) |
| none | 1 (0.3 %) | 0 (0.0 %) | 10 (3.5 %) | 4 (1.5 %) | 15 (1.3 %) |
| other | 1 (0.3 %) | 2 (0.7 %) | 2 (0.7 %) | 5 (1.9 %) | 10 (0.9 %) |
| **N (FPs)** | **297** | **278** | **283** | **261** | **1119** |

## v1-vs-v2 aggregate comparison

How did the four added burial-mound categories shift the 55-map FP profile? Each row shows the v1 aggregate count and share alongside the v2 aggregate. Burial-mound categories were not in v1 — any v2 mass on those rows reflects FPs that v1 had to assign to the closest non-burial-mound category (typically `contour-ring` for the round mound symbol or `settlement` for the angular tell symbol).

| Category | v1 n | v1 % | v2 n | v2 % | Δ (v2 − v1) pp |
|---|---:|---:|---:|---:|---:|
| number | 214 | 19.1 % | 122 | 10.9 % | -8.2 |
| benchmark | 54 | 4.8 % | 14 | 1.3 % | -3.6 |
| water-feature | 136 | 12.2 % | 131 | 11.7 % | -0.4 |
| contour-ring | 458 | 40.9 % | 382 | 34.1 % | -6.8 |
| vegetation | 64 | 5.7 % | 100 | 8.9 % | +3.2 |
| settlement | 157 | 14.0 % | 146 | 13.0 % | -1.0 |
| road-or-track | 13 | 1.2 % | 17 | 1.5 % | +0.4 |
| scale-bar-or-grid | 2 | 0.2 % | 5 | 0.4 % | +0.3 |
| **burial-mound** | — | — | 23 | 2.1 % | +2.1 (new) |
| **benchmark-on-burial-mound** | — | — | 0 | 0.0 % | +0.0 (new) |
| **triangulation-point-on-burial-mound** | — | — | 37 | 3.3 % | +3.3 (new) |
| **settlement-mound** | — | — | 117 | 10.5 % | +10.5 (new) |
| none | 7 | 0.6 % | 15 | 1.3 % | +0.7 |
| other | 14 | 1.3 % | 10 | 0.9 % | -0.4 |
| **N (FPs)** | **1119** | — | **1119** | — | — |

**Total v2 mass on the four burial-mound categories: 177 / 1119 FPs (15.8 %).**

**FINDING:** 177 FPs (15.8 %) reclassify as burial-mound categories under v2. This exceeds the < 1 % calibration-noise threshold and indicates a non-trivial rate of review-pass false-FP labels (real mounds accidentally clicked "not_mound" by the reviewer). Per-FP records are in `fp_classifications.json` (filter on `category in {burial-mound, benchmark-on-burial-mound, triangulation-point-on-burial-mound, settlement-mound}`); manual review of these crops is the natural follow-up.

### Finding interpretation — flag for human calibration

The 15.8 % burial-mound reclassification rate is **larger than expected** and merits flagging. Three competing interpretations:

1. **Review-pass mislabelling.** A genuine 15.8 % rate of human reviewer error would be high but not implausible — manual review of ~1,100 candidates is fatiguing, and the reviewer may have under-applied the "mound" label in dense / ambiguous map regions. Manual re-review of the 177 v2-burial-mound crops is the natural follow-up.
2. **Prompt-bias / vocabulary-leakage.** The prompt tells the model the centre was "identified as a possible burial mound symbol" and instructs "when in doubt, prefer the more specific category over 'other'" — both nudge toward burial-mound categories now that they are in the list. The mean confidence on burial-mound assignments is high (0.94-0.95), but Gemini 3 Flash is known to anchor on confidence calibration in single-pass minimal-thinking runs. The dominant new category is `settlement-mound` (117 / 1,119 = 10.5 %), which describes a black hairy/angular square-shaped symbol that may be a noisy fit for unrelated dense-feature crops.
3. **Vocabulary expansion redistributes mass without changing underlying judgement.** Note that the cumulative shift away from `number` (-92), `benchmark` (-40), and `contour-ring` (-76) sums to -208, while the four burial-mound categories pick up +177; the net mass shifted is closer to 16 % of the corpus. v1 classifications of these FPs as `contour-ring` or `number` may have been the model's best non-mound option for crops that genuinely contain mound symbols; v2 simply lets the model name them correctly.

The v1-vs-v2 distractor-pull share comparison (text-track 22.7 % → 10.8 %) is consistent with interpretation (3): the v1 `number` and `benchmark` categories absorbed mass that v2 redirects elsewhere. Whichever interpretation is correct, the headline distractor-pull-on-text-track hypothesis is unsupported under both closed lists.

**Recommended follow-up:** manual re-inspection of the 177 v2-burial-mound crops to disambiguate (1) from (2) + (3). If most are real mounds, the 55-map review pass needs a targeted second pass on ambiguous candidates. If most are false-mound assignments, the v1 distribution is the more conservative read of the FP profile.

## Distractor-pull share (number + benchmark)

Shawn's hypothesis predicts 55-map FPs concentrate on **number + benchmark** (Soviet 1980s spot-elevation labels and survey markers).

| Run | number + benchmark | share | n_FPs |
|---|---:|---:|---:|
| T0.3 | 38 | 12.8 % | 297 |
| T0.7 | 26 | 9.4 % | 278 |
| image | 46 | 16.3 % | 283 |
| text-MIN | 26 | 10.0 % | 261 |
| **text-track aggregate** | **90** | **10.8 %** | **836** |
| **image** | **46** | **16.3 %** | **283** |

## GS-failure-mode share (water-feature)

Shawn's hypothesis predicts the GS calibration corpus would have produced FPs on **spot-heights and water features**. Note that on Soviet maps a spot-height usually presents as a numeric label (sometimes plus a benchmark) — the closed list categorises elevation digits as `number` rather than as a separate spot-height bucket. This row therefore reports only the second arm of the GS prediction (water-feature). The first arm (numbers as spot-heights) is folded into the distractor-pull row above; under Shawn's hypothesis, 55-map number-prevalence reflects label distractor-pull, while GS would-be number-prevalence reflects spot-height ambiguity. The diagnostic alone cannot tell those apart without GS data — flagged as a methodological caveat.

| Run | water-feature | share |
|---|---:|---:|
| T0.3 | 25 | 8.4 % |
| T0.7 | 28 | 10.1 % |
| image | 29 | 10.2 % |
| text-MIN | 49 | 18.8 % |

## Chi-square test — image vs text-track

- chi-squared statistic: 28.490
- degrees of freedom: 12
- p-value: 0.004688
- n (image): 283
- n (text-track aggregate): 836
- categories used: number, benchmark, water-feature, contour-ring, vegetation, settlement, road-or-track, scale-bar-or-grid, burial-mound, triangulation-point-on-burial-mound, settlement-mound, none, other

### Per-category Pearson residuals

Pearson residuals (observed − expected) / √expected indicate which categories drive the difference. |residual| > 2 is the conventional threshold for a meaningful per-cell effect.

| Category | image obs | image exp | image residual | text obs | text exp | text residual |
|---|---:|---:|---:|---:|---:|---:|
| number | 44 | 30.9 | +2.37 | 78 | 91.1 | -1.38 |
| benchmark | 2 | 3.5 | -0.82 | 12 | 10.5 | +0.48 |
| water-feature | 29 | 33.1 | -0.72 | 102 | 97.9 | +0.42 |
| contour-ring | 94 | 96.6 | -0.27 | 288 | 285.4 | +0.15 |
| vegetation | 25 | 25.3 | -0.06 | 75 | 74.7 | +0.03 |
| settlement | 33 | 36.9 | -0.65 | 113 | 109.1 | +0.38 |
| road-or-track | 5 | 4.3 | +0.34 | 12 | 12.7 | -0.20 |
| scale-bar-or-grid | 0 | 1.3 | -1.12 | 5 | 3.7 | +0.65 |
| burial-mound | 3 | 5.8 | -1.17 | 20 | 17.2 | +0.68 |
| triangulation-point-on-burial-mound | 11 | 9.4 | +0.54 | 26 | 27.6 | -0.31 |
| settlement-mound | 25 | 29.6 | -0.84 | 92 | 87.4 | +0.49 |
| none | 10 | 3.8 | +3.19 | 5 | 11.2 | -1.85 |
| other | 2 | 2.5 | -0.33 | 8 | 7.5 | +0.19 |

## Verdict on Shawn's hypothesis

**MIXED** — image-vs-text distributions differ significantly, but text-track distractor-pull share does not exceed 30 %; the dominant 55-map FP class on text-track is something other than number/benchmark.

- Text-track aggregate (number + benchmark) share: 10.8 %
- Image-track (number + benchmark) share: 16.3 %
- Chi-square p-value (image vs text-track): 0.004688

### Comparison with v1 verdict

v1 verdict: **NOT SUPPORTED — text-track distractor-pull share is below 30 %, and image-vs-text-track chi-square is non-significant.**

- v1 text-track distractor-pull share: 22.7 % (v2: 10.8 %)
- v1 image-track distractor-pull share: 27.6 % (v2: 16.3 %)
- v1 chi-square p-value: 0.1474 (v2: 0.004688)

v1 and v2 verdicts agree on the headline question: Shawn's distractor-pull-on-text-track hypothesis is not supported under both closed lists. The closed-list expansion did not change the hypothesis-testing outcome.

## Caveats and methodological notes

- **Single-pass classification, no consensus.** Each FP is classified once at temperature 0.0, thinking_level=minimal. Gemini 3 Flash class assignment may be noisy in ambiguous centres (e.g. crops with multiple plausible features near centre). The confidence-weighted distribution in `category_distribution.json` provides a sensitivity check; results should be read as a coarse first-pass profile, not a precise per-class accounting.
- **No GS comparator.** The diagnostic compares the four 55-map runs against each other, not against the GS corpus. The headline hypothesis (55-map vs GS asymmetric failure modes) is tested only on the 55-map side; the GS half is inferred from Shawn's prior manual review (Obs 296). A direct GS-side classification is the natural follow-up.
- **Number = spot-height confound.** Soviet 1:50,000 maps render spot-heights as numeric elevation labels — the same `number` category that captures the distractor-pull arm of Shawn's 55-map hypothesis. The two arms are not separable by this classification alone; the cross-corpus picture (55-map number-prevalence as label distractor-pull vs GS number-prevalence as spot-height ambiguity) is a paper interpretation, not a measurement.
- **Crop-centre ambiguity.** Some FPs sit in dense map regions where multiple categories are plausible near the 150 m crop centre. The model is asked to pick the strongest burial-mound-confusable feature; the resulting category may differ from a strict "closest-to-centre" reading.
- **Prompt vocabulary anchor.** The prompt names Soviet 1980s topographic categories explicitly. This is a deliberate departure from the detection-prompt convention (visual-feature naming without cartographic vocabulary); for FP classification we WANT the model to apply its cartographic knowledge. Generic vs Soviet category mismatch was guarded against by including a Cyrillic example ("БМ") in the prompt.
- **v2 burial-mound assignment confidence.** The model assigned burial-mound categories with high mean confidence (0.94-0.95 across the four categories), but this should not be taken as evidence that 15.8 % of the FPs are misclassified by the human reviewer — Gemini 3 Flash's single-pass confidence calibration is loose, and the prompt-bias issue noted in the "Finding interpretation" section above is plausible. A consensus pass (multiple K runs at non-zero temperature) would tighten the burial-mound rate estimate.
- **Cross-corpus consistency note.** v2 categories now mirror the parallel GS re-run, supporting like-with-like chi-square comparisons across corpora. The image vs text-track chi-square moved from p = 0.1474 (v1, n.s.) to p = 0.0047 (v2, significant), but per-cell Pearson residuals show this is driven by `number` (image obs +2.37) and `none` (image obs +3.19) — both image-track elevations relative to text-track. Neither residual reflects the burial-mound category expansion directly; the v1 list already contained both implicated categories.

## Findable later

Search terms: 55-map FP-class classification, Obs 296 Test #2, cartographic-naming approach, Gemini 3 Flash 150 m crop classification, distractor-pull text-track number benchmark, chi-square image vs text-track, water-feature spot-height GS failure mode, Soviet 1980s topographic categories closed list, rendered crop in-memory base64, flex tier classification single-pass, confidence-weighted distribution sensitivity, 55-map FP v2 burial-mound closed list, cross-corpus consistency with parallel GS re-run, review-pass false-FP labels, 15.8 percent burial-mound reclassification rate, settlement-mound vocabulary leakage, prompt-bias caveat, image-track number distractor-pull elevated.
