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

- **Closed-list design dependency.** The 14-category vocabulary is pre-specified for the VLM; symbols absent from the list cannot be detected and will instead be coerced into `other` or the closest visual proxy. Soviet 1980s 1:50,000 sheets carry many cartographic symbols (railway crossings, ruins, springs, cliffs, dolines) that the closed list does not enumerate; the FP profile reported here is therefore conditional on the four-corpus-relevant categories chosen at design time, not a complete cartographic inventory. The v1 → v2 expansion (adding four burial-mound categories) demonstrates the dependency in action: 15.8 % of FPs reclassified once a previously-absent category was made available. Adding further categories could shift mass again.
- **15.8 % v2 burial-mound reclassification — three competing interpretations.** The `Finding interpretation` section above lists (1) review-pass mislabelling, (2) v2 prompt bias, and (3) vocabulary-expansion redistribution. The three are not separable from the classification table alone. A 30-crop manual spot-check is planned (see Obs 308 + the bet-test app planning artefact at `archive/planning-completed-session-81-82/v2-burial-mound-bet-test-app-plan-2026-04-29.md`); pending that, the 15.8 % rate is a flagged-but-unresolved upper bound on the review-error contribution. User's prior digitisation experience suggests the true review-error component is probably 1-3 %, with the bulk falling to (2) + (3) — but this remains a prior, not a measurement.
- **Calibration-noise threshold (~1 %).** Single-pass classification at T = 0.0 with thinking_level=minimal carries an implicit noise floor of approximately 1 % on per-category percentages — below this threshold, observed differences are indistinguishable from classifier-internal stochasticity (residual non-determinism in Gemini 3 Flash decoding even at T = 0). Per-category shifts smaller than ~1 percentage point should not be over-interpreted; the headline findings (contour-ring 34.1 %, distractor-pull 10.8 %, burial-mound-categories 15.8 %) are well outside this floor.
- **Single classifier, no ensemble.** Each FP is classified by one model (Gemini 3 Flash) at one set of decoding parameters. There is no cross-model consensus (e.g. Flash + Pro + a third VLM), no temperature ensemble (multi-K at non-zero T), and no human spot-check sample to anchor classifier accuracy on this task. A consensus pass at non-zero temperature would tighten the burial-mound rate estimate; a cross-model ensemble would bound the model-specific bias contribution to the reported distribution.
- **Single-pass classification, no consensus.** Each FP is classified once at temperature 0.0, thinking_level=minimal. Gemini 3 Flash class assignment may be noisy in ambiguous centres (e.g. crops with multiple plausible features near centre). The confidence-weighted distribution in `category_distribution.json` provides a sensitivity check; results should be read as a coarse first-pass profile, not a precise per-class accounting.
- **GS comparator now exists (Obs 307).** The original v1 caveat noted no GS-side comparator. As of 2026-04-29 (commit `9fa6db4e`), `results/gs-fp-classification/report.md` provides the GS-side analogue under the same v2 closed list. Cross-corpus chi-square (Monte Carlo): p = 0.0028 at the >125 m stratum and p = 0.0012 at >50 m. The headline cross-corpus claim (different failure modes by corpus) is now empirically supported, though see Obs 307 caveats — n = 14 at >125 m on GS is small, and Pearson residuals are interpretable only at |r| > 2.
- **Number = spot-height confound.** Soviet 1:50,000 maps render spot-heights as numeric elevation labels — the same `number` category that captures the distractor-pull arm of Shawn's 55-map hypothesis. The two arms are not separable by this classification alone; the cross-corpus picture (55-map number-prevalence as label distractor-pull vs GS number-prevalence as spot-height ambiguity) is a paper interpretation, not a measurement.
- **Crop-centre ambiguity.** Some FPs sit in dense map regions where multiple categories are plausible near the 150 m crop centre. The model is asked to pick the strongest burial-mound-confusable feature; the resulting category may differ from a strict "closest-to-centre" reading.
- **Prompt vocabulary anchor.** The prompt names Soviet 1980s topographic categories explicitly. This is a deliberate departure from the detection-prompt convention (visual-feature naming without cartographic vocabulary); for FP classification we WANT the model to apply its cartographic knowledge. Generic vs Soviet category mismatch was guarded against by including a Cyrillic example ("БМ") in the prompt.
- **v2 burial-mound assignment confidence.** The model assigned burial-mound categories with high mean confidence (0.94-0.95 across the four categories), but this should not be taken as evidence that 15.8 % of the FPs are misclassified by the human reviewer — Gemini 3 Flash's single-pass confidence calibration is loose, and the prompt-bias issue noted in the "Finding interpretation" section above is plausible. A consensus pass (multiple K runs at non-zero temperature) would tighten the burial-mound rate estimate.
- **Cross-corpus consistency note.** v2 categories now mirror the parallel GS re-run, supporting like-with-like chi-square comparisons across corpora. The image vs text-track chi-square moved from p = 0.1474 (v1, n.s.) to p = 0.0047 (v2, significant), but per-cell Pearson residuals show this is driven by `number` (image obs +2.37) and `none` (image obs +3.19) — both image-track elevations relative to text-track. Neither residual reflects the burial-mound category expansion directly; the v1 list already contained both implicated categories.

## Paper implications

This classification underwrites three load-bearing moves in the paper's Discussion of cross-corpus generalisation behaviour.

1. **Cross-corpus FP-classification asymmetry as direct evidence for failure-of-generalisation (Obs 296, refined by Obs 307).** The Obs 296 reading was that the 5–10× higher 55-map mid-distance pull rate reflects a _generalisation gap_: the GS corpus was the calibration corpus, and prompt iteration progressively suppressed its native distractor-pull failure modes; the 55-map sample is closer to native unfamiliar-map behaviour. The cross-corpus chi-square (Monte Carlo p = 0.0028 at >125 m; p = 0.0012 at >50 m, see Obs 307) shows the two corpora produce _categorically different_ FP profiles — GS over-represents `burial-mound` and `triangulation-point-on-burial-mound` (Pearson residuals +5.29 and +3.33 at >50 m); GS under-represents `contour-ring` (residual −2.33 at >50 m / −2.18 at >125 m), with 55-map text-track aggregate `contour-ring` at 34.4 % vs GS 0 % (0 / 16) at the same stratum. This is the cleanest categorical evidence the project has produced for the failure-of-generalisation reading: the two corpora are not just at different points along the same failure-mode axis; they fail in qualitatively different ways.
2. **Refines but does not confirm Shawn's original distractor-pull-on-text-track hypothesis.** Number + benchmark text-track aggregate share is 10.8 % under v2 (down from 22.7 % under v1, with the burial-mound categories absorbing some of v1's number assignments). Both lie below the 30 % advance-specified threshold for hypothesis support. The paper Discussion should NOT cite this work as evidence for the spot-height-distractor-pull mechanism; it should cite it as evidence that the dominant 55-map FP class is contour-ring confusion (~34 %), with distractor-pull a secondary contributor.
3. **Strengthens the calibration-vs-native reading; does not bear on the architecture-comparison narrative.** The result is mechanism-level — it tells us _what kind of feature_ the detector falls prey to on each corpus, not which architecture is preferable. The paper's architecture-comparison sections (image vs text track; PV vs no-PV; verifier-T) draw on the F1 / MCC matrix and the paired-permutation grid, which this work does not touch. The contribution here is to the Discussion's failure-mode characterisation, not to the Results' architecture verdicts.

The framing change for the paper Discussion: replace any draft text claiming "55-map detector falls prey to numbers and benchmarks" with "55-map detector falls prey predominantly to closed-contour-ring features (~34 %), with numbers / benchmarks contributing a secondary ~11 % on text-track; the GS corpus surfaces a different mode (burial-mound-adjacent symbols, residuals +3 to +5)". This is paper-load-bearing — see Obs 302 and Obs 307 for full mechanism arguments.

## Reproducibility

- **Script**: `scripts/55maps-fp-classify.py` (driver) — commit `5040f5b4` introduced; commit `ec21c8ef` is the v2 re-run that produced this report.
- **Data commit at run time**: `ec21c8ef` (2026-04-29).
- **Closed list (v2)**: 14 categories, defined verbatim in `CATEGORIES` (script line 185).
- **Model and parameters**: Gemini 3 Flash, `service_tier="flex"`, `temperature=0.0`, `thinking_level=minimal`. Single-pass per FP; no consensus, no ensemble, no bootstrap (deterministic-aimed decoding, so no `--seed` flag is exposed; residual non-determinism is the calibration-noise floor in Caveats).
- **Inputs**: Four corrected 55-map review CSVs at `results/55maps-{text-high-t0.3,text-high,image,text-min}-generalisation/human-review-multi-buffer.csv`; rasters at `inputs/rasters/Russian1981_32635/K-35-*.tif` (EPSG:32635).
- **Wall-clock**: 229.8 s (3 m 50 s) at `--workers 20` on a residential broadband connection. Per-run breakdown in `cost_summary.json`.
- **API cost**: $0.5803 USD actual on flex tier (4-run total: T0.3 $0.154; T0.7 $0.144; image $0.147; text-MIN $0.135). Hard-cap of $5.00 set in driver.
- **N classified**: 1,119 FPs across four runs (T0.3: 297; T0.7: 278; image: 283; text-MIN: 261). Failed/skipped: 0.
- **Re-run command** (from repo root):

  ```bash
  python scripts/55maps-fp-classify.py \
      --workers 20 \
      --output-dir results/55maps-fp-classification
  ```

- **Outputs**: `fp_classifications.json` (per-FP record), `category_distribution.json` (per-corpus + aggregate counts; chi-square test), `cost_summary.json` (per-run + total spend), `figures/category_distribution.png` (stacked-bar chart), `report.md` (this document).
- **Caveat on exact reproducibility**: Gemini 3 Flash decoding at T = 0.0 with thinking_level=minimal is _aimed at_ determinism but not guaranteed bit-exact across reruns; expect per-category percentages to drift by ≤ 1 percentage point on a fresh run (the calibration-noise floor noted in Caveats).

## Related observations and artefacts

- **Obs 296** (failure-of-generalisation reinterpretation, distractor-pull hypothesis): the test target. This work refines Obs 296 — the FP-anchoring reading survives, but the dominant captor on the 55-map side is contour-rings (~34 %), not numbers / benchmarks. Together with Obs 307 it provides categorical cross-corpus evidence for the calibration-vs-native reading.
- **Obs 302** (FP-class diagnostic v1 verdict, pre-burial-mound-list): the predecessor. v1 ran on a 10-category closed list without burial-mound categories; this v2 run mirrors the parallel GS re-run for cross-corpus comparability. The v1 vs v2 distractor-pull share (text-track 22.7 % → 10.8 %) is consistent with vocabulary redistribution rather than mechanism change.
- **Obs 304** (high-pull tail does NOT share an identifiable cartographic feature): convergent evidence. Per-map FP category distributions are similar between high-pull and low-pull control maps; contour-rings dominate in both. What separates high-pull from low-pull is not the _kind_ of FPs raised but whether those FPs happen to fall within the (50, 75] m annulus of a reference point.
- **Obs 307** (cross-corpus chi-square Monte Carlo p = 0.0028 / 0.0012): the cross-corpus headline this work feeds into. Apples-to-apples chi-square at the >125 m and >50 m strata; categorical evidence that GS and 55-map produce different FP profiles.
- **Obs 308** (15.8 % v2 burial-mound reclassification, provisional): the bet-test framing for the manual spot-check that will partition the three competing explanations. Denominator 1,675 reviewed `not_mound` rows; bet threshold = 34 errors among 177 reclassifications (= 19 %).
- **GS analogue**: `results/gs-fp-classification/report.md` (commit `9fa6db4e`) — same v2 closed list applied to all 371 GS detections (verified-v1 full-scope), partitioned post-hoc into TP-side (≤50 m from curator GT) and FP-side (>50 m). Headline GS FP at >50 m: `burial-mound` 25.0 % (4 / 16); cross-corpus chi-square Monte Carlo p = 0.0012.
- **Bet-test plan**: `archive/planning-completed-session-81-82/v2-burial-mound-bet-test-app-plan-2026-04-29.md` (commit `8d2f7f47`) — Streamlit app for manual re-inspection of the 177 v2-burial-mound reclassifications.
- **Artefacts**: Driver `scripts/55maps-fp-classify.py`. Results `results/55maps-fp-classification/{fp_classifications.json, category_distribution.json, cost_summary.json, report.md, figures/category_distribution.png, v2-burial-mound-bet-test/}`. v1 archive `archive/55maps-fp-classification-v1-pre-burial-mound-list/`. Commits: `5040f5b4` (driver introduction), `e552ad46` (v1 data + report), `ec21c8ef` (v2 re-run with burial-mound categories).

## Findable later

Search terms: 55-map FP-class classification, Obs 296 Test #2, cartographic-naming approach, Gemini 3 Flash 150 m crop classification, distractor-pull text-track number benchmark, chi-square image vs text-track, water-feature spot-height GS failure mode, Soviet 1980s topographic categories closed list, rendered crop in-memory base64, flex tier classification single-pass, confidence-weighted distribution sensitivity, 55-map FP v2 burial-mound closed list, cross-corpus consistency with parallel GS re-run, review-pass false-FP labels, 15.8 percent burial-mound reclassification rate, settlement-mound vocabulary leakage, prompt-bias caveat, image-track number distractor-pull elevated.
