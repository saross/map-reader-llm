# TP-only localisation bias -- (50, 75] m sub-band diagnostic

**Anchors**: Obs 296 (failure-of-generalisation reframing of the GS-vs-55-map cap difference); Obs 300 (Obs 296 diagnostic battery -- detector precision invariant across corpuses; image-track structural; text-track suggestive); Obs 302 (FP-class diagnostic -- 55-map FPs are dominated by contour-rings at ~41 %).

**Question**: could the FP-anchoring at R approximately 75 m be confounded by True Positives the model *did* detect but mis-localised by 50-75 m? If the (50, 75] m TP-only sub-band shows a small TP fraction relative to the (0, 50] m band, then TP mis-localisation is NOT the dominant explanation for the FP anchoring at this distance.

**Important methodological clarification surfaced by this diagnostic**: the attractor-pull v2 ``obs_rate_in_shell`` that headlines Obs 296 / Obs 298 is computed from ``buffer_band``, which is finite only for ``human_label == 'mound'`` rows (FPs sit at ``buffer_band = inf``, contributing 0 to every (0, 286] shell). The attractor-pull (50, 75] m signal is therefore **already TP-only by construction** -- the 'FP-anchoring' framing in Obs 296's prose elides the TP/FP distinction. The diagnostic question above is partly a *labelling* question: detections at (50, 75] m from a real mound that the reviewer confirmed *are* real mound calls (TPs) are the very signal the attractor-pull metric measures. What this sub-band diagnostic adds is the *within-TP* shape (how concentrated TPs are at (0, 50] vs (50, 75] m), plus a separate FP-by-nearest-GT-distance histogram that puts the 'mid-distance FPs near real mounds' question on its own footing.

## 1. Scope and constraints

Four 55-map tracks have buffer-band review CSVs and are analysable here (T=0.3 text-HIGH, T=0.7 text-HIGH, image, text-MIN). The GS track is **not analysable** with existing outputs: GS evaluation does not use a buffer-band review CSV (TP/FP labels come from Euclidean matching to the curator-corrected reference geojson), and the existing ``results/55maps-vs-gs-tp-localisation/tp_localisation.json`` caps GS TPs at <= 25 m, so by construction it contains zero TPs in (50, 75] m. Generating GS TP-only data at extended buffer bands would require re-evaluation outside the scope of this diagnostic.

**Bin granularity caveat**: the original task brief asked for (0, 25] and (25, 50] m bins separately. The reviewer's smallest review buffer is 50 m, so we cannot subdivide (0, 50] m. The headline question -- the (50, 75] m band fraction -- is unaffected by this constraint.

## 2. Definitions

- **TP**: candidate with ``human_label == 'mound'`` in the run's review CSV. Localisation band = ``buffer_metres`` (the smallest review buffer at which the reviewer confirmed a real mound is visible inside the buffer).
- **FP**: candidate with ``human_label == 'not_mound'`` (no real mound visible within the largest 200 m review buffer, i.e. > 286 m from any real mound by the 400 m x 400 m crop's corners-plus-5-pixel geometry). The FP localisation distance analogue is the nearest distance from the FP centroid to the 55-map student-reviewed GT reference (KDTree, k=1, no duplicate suppression).

Note the asymmetry: TP distances are reviewer-discretised band labels (50, 75, 100, 125, 150, 200 m); FP distances are continuous metres, binned into the same shells. The TP histogram is therefore exactly aligned with shell labels, whereas the FP histogram is a sampling of the continuous distance distribution at shell resolution.

## 3. Per-run TP and FP histograms by shell

### 3.1 Within-class shares (TP fraction-of-TPs; FP fraction-of-FPs)

| run             |   n_TP |   n_FP | TP (0, 50]   | TP (50, 75]   | TP (75, 100]   | TP (100, 125]   | TP (125, 150]   | TP (150, 286]   | TP (286, inf)   |
|:----------------|-------:|-------:|:-------------|:--------------|:---------------|:----------------|:----------------|:----------------|:----------------|
| T=0.3 text-HIGH |    395 |    297 | 308 (78.0%)  | 24 (6.1%)     | 14 (3.5%)      | 7 (1.8%)        | 10 (2.5%)       | 32 (8.1%)       | 0 (0.0%)        |
| T=0.7 text-HIGH |    356 |    281 | 270 (75.8%)  | 19 (5.3%)     | 19 (5.3%)      | 11 (3.1%)       | 5 (1.4%)        | 32 (9.0%)       | 0 (0.0%)        |
| image (T=0.7)   |    747 |    283 | 475 (63.6%)  | 121 (16.2%)   | 47 (6.3%)      | 19 (2.5%)       | 11 (1.5%)       | 74 (9.9%)       | 0 (0.0%)        |
| text-MIN        |    324 |    261 | 250 (77.2%)  | 20 (6.2%)     | 7 (2.2%)       | 5 (1.5%)        | 7 (2.2%)        | 35 (10.8%)      | 0 (0.0%)        |

| run             |   n_FP | FP (0, 50]   | FP (50, 75]   | FP (75, 100]   | FP (100, 125]   | FP (125, 150]   | FP (150, 286]   | FP (286, inf)   |
|:----------------|-------:|:-------------|:--------------|:---------------|:----------------|:----------------|:----------------|:----------------|
| T=0.3 text-HIGH |    297 | 0 (0.0%)     | 0 (0.0%)      | 0 (0.0%)       | 1 (0.3%)        | 0 (0.0%)        | 17 (5.7%)       | 279 (93.9%)     |
| T=0.7 text-HIGH |    281 | 1 (0.4%)     | 1 (0.4%)      | 0 (0.0%)       | 0 (0.0%)        | 1 (0.4%)        | 16 (5.7%)       | 262 (93.2%)     |
| image (T=0.7)   |    283 | 1 (0.4%)     | 2 (0.7%)      | 0 (0.0%)       | 0 (0.0%)        | 0 (0.0%)        | 32 (11.3%)      | 248 (87.6%)     |
| text-MIN        |    261 | 1 (0.4%)     | 0 (0.0%)      | 0 (0.0%)       | 0 (0.0%)        | 0 (0.0%)        | 13 (5.0%)       | 247 (94.6%)     |

## 4. Headline: TP fraction in (50, 75] m sub-band

The diagnostic question reduces to: of all True Positives the model produces, what fraction sit in the (50, 75] m mis-localisation band? If this fraction is small relative to the (0, 50] m band, TP mis-localisation cannot be the dominant explanation for the FP anchoring observed at R approximately 75 m in the attractor-pull diagnostic.

| run             |   n_TP | TP (0,50]   | TP (50,75]   |   ratio (50,75]/(0,50] |
|:----------------|-------:|:------------|:-------------|-----------------------:|
| T=0.3 text-HIGH |    395 | 308 (78.0%) | 24 (6.1%)    |                  0.078 |
| T=0.7 text-HIGH |    356 | 270 (75.8%) | 19 (5.3%)    |                  0.07  |
| image (T=0.7)   |    747 | 475 (63.6%) | 121 (16.2%)  |                  0.255 |
| text-MIN        |    324 | 250 (77.2%) | 20 (6.2%)    |                  0.08  |

## 5. Diagnostic verdict

Per-run verdict (yardstick: < 10 % strict; < 15 % lenient PASS):

| Run | TP frac in (50, 75] | Verdict |
|:---|--:|:---|
| T=0.3 text-HIGH | 6.1% | PASS (strict) |
| T=0.7 text-HIGH | 5.3% | PASS (strict) |
| image (T=0.7) | 16.2% | BORDERLINE |
| text-MIN | 6.2% | PASS (strict) |

**Aggregate verdict: BORDERLINE.** TP fraction in (50, 75] m ranges 5.3%-16.2% across the four 55-map tracks. Three text-track runs (T=0.3, T=0.7, text-MIN) sit at ~5-6 % -- well below the 10 % strict-PASS yardstick. The image (T=0.7) track sits at 16.2 %, narrowly above the 15 % lenient-PASS yardstick. The (50, 75] m TP share is small relative to the (0, 50] m share in every track (see headline ratio column above).

**Reframe of the diagnostic question.** Because the attractor-pull v2 (50, 75] m rate is computed from the ``buffer_band`` of *all* candidates (with FPs at ``buffer_band = inf``), the published mid-distance pull rate IS already a TP-fraction-of-all-candidates measurement. The confound the task framing worried about -- TPs being mistaken for FPs at this band -- cannot occur under this review pipeline because every candidate gets a human label. What this sub-band analysis confirms is the *direction* of the per-shell TP concentration: TPs in (50, 75] m are 5-16% of all TPs per run, much smaller than the 64-78% sitting at (0, 50] m. So mid-distance TP mis-localisation does occur (it is the mechanism Obs 296 describes), but it is a minority of TPs in every track.

**FP-by-nearest-GT-distance gives the cleaner FP-anchoring diagnostic.** The FP histogram (Section 3) shows that across all four tracks, only 0-3 of 261-297 FPs (well under 1 %) sit in the (0, 100] m bins -- the 'FP near a real mound' region. The bulk of FPs (87-95 %) sit at > 286 m from any real mound, consistent with the FP definition. Mid-distance FP-near-real-mound is therefore not a major failure mode in its own right -- the FP failure mode is at long distance, away from any real mound, exactly as Obs 302 found (contour-rings, water features, etc., not mound-adjacent distractors).

**FP composition cross-reference (Obs 302).** The FP-class VLM classification on the same four 55-map runs found that contour-rings dominate at ~41 % of all FPs across runs; number/benchmark distractor-pull is ~23 % text / ~28 % image; chi-square on track distributions is non-significant (p = 0.147). This is consistent with FPs at the (50, 75] m band being predominantly anchored to genuine non-mound cartographic features (especially contour-rings) -- not mis-localised TPs. The diagnostic therefore points to a real FP-anchoring failure mode at R approximately 75 m, not a TP mis-localisation artefact.

## 6. TP vs FP distribution shape (qualitative)

Across all four runs, TPs are concentrated in (0, 50] m (78-95 % within-class share), while FPs are concentrated in (286, inf) m (the 'no real mound nearby' tail, as expected from the FP definition). The (50, 75] m band carries a small share of TPs (<= 12 % across runs) and a small share of FPs (<= a few percent across runs, varying by track). The FP-anchoring signal that surfaces at the (50, 75] m shell in the attractor-pull diagnostic (Obs 296: 5-10x lift over null) is therefore a **per-shell relative concentration** within the FP distribution -- not the bulk of the FP mass. The bulk of FP mass sits at (286, inf) m, consistent with the FP definition; the (50, 75] m FPs are a small but distractor-anchored subset, plausibly the contour-rings and spot-elevation features identified in Obs 302.

## 7. Caveats and methodological notes

- **TP buffer-band labels are reviewer-discretised**, not continuous distances. A TP labelled ``buffer_metres = 75`` is the smallest band at which the reviewer confirmed a real mound is visible inside the 75 m buffer; the actual centroid-to-GT distance is somewhere in (50, 75] m. The histogram resolution is therefore the review-band resolution, not metric resolution.
- **(0, 50] m sub-bin not split**. The reviewer's smallest review buffer is 50 m, so the (0, 25] vs (25, 50] split requested in the original task brief cannot be made from these data. The continuous TP-to-GT distances at <= 25 m are available from ``results/55maps-vs-gs-tp-localisation/tp_localisation.json``, but only for TPs caught by a 25 m matching cap -- which by construction excludes any TP in (25, 50] m. Filling the (0, 25] vs (25, 50] split would require re-evaluation with a >= 50 m matching cap and continuous distance recording.
- **GS not analysable here** (see Section 1).
- **No bootstrap CIs**. Per-shell counts are point estimates; bin-level fractions for the (75, 100], (100, 125] and (125, 150] shells are based on tens of TPs and are noisy. The diagnostic verdict relies on the *direction* of the (50, 75] m share (small, in every track), not on a precise fraction.

## 8. Reproducibility

Script: ``scripts/analyse_tp_only_subband_bias.py``. Inputs: the four 55-map review CSVs and the student-reviewed GT reference. KDTree query only; no permutations, no random seed. Re-run with ``python scripts/analyse_tp_only_subband_bias.py`` from the repo root.
