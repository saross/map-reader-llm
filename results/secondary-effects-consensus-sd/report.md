# Consensus SD Shrinkage Analysis (Phase 3a Text + Image)

**Generated**: 2026-04-27T04:48:11.938763+00:00
**Bootstrap iterations**: 1000 (seed = 42)
**Theoretical i.i.d. log-log slope**: beta_1 = -0.5
**Slower-than-i.i.d. flag**: beta_1 > -0.3 (asterisked rows below)

## Per-stratum log-log slope and SD shrinkage

| Track | Thinking | T | SD@K=1 | SD@K=5 | SD@K=10 | SD@K=N_max | beta_1 [95% CI] | CI-width ratio (K=N_max / K=1) |
|-------|----------|--:|------:|------:|------:|------:|:--------------:|:-----:|
| image | HIGH | 0.3 | 0.0089 | 0.0039 | 0.0027 | 0.0027 (K=10) | -0.52 [-0.58, -0.48] | — |
| image | HIGH | 0.7 | 0.0177 | 0.0078 | 0.0052 | 0.0052 (K=10) | -0.53 [-0.58, -0.47] | 0.34 |
| image | HIGH | 1.0 | 0.0224 | 0.0094 | 0.0068 | 0.0068 (K=10) | -0.52 [-0.58, -0.47] | — |
| image | MINIMAL | 0.3 | 0.0068 | 0.0028 | 0.0021 | 0.0021 (K=10) | -0.52 [-0.59, -0.47] | — |
| image | MINIMAL | 0.7 | 0.0137 | 0.0057 | 0.0040 | 0.0040 (K=10) | -0.53 [-0.59, -0.47] | — |
| image | MINIMAL | 1.0 | 0.0072 | 0.0030 | 0.0022 | 0.0022 (K=10) | -0.51 [-0.58, -0.47] | — |
| image | SCALE4 | 0.7 | 0.0229 | 0.0095 | 0.0068 | 0.0068 (K=10) | -0.53 [-0.59, -0.47] | — |
| text | HIGH | 0.3 | 0.0149 | 0.0063 | 0.0045 | 0.0045 (K=10) | -0.53 [-0.58, -0.47] | — |
| text | HIGH | 0.7 | 0.0122 | 0.0053 | 0.0038 | 0.0022 (K=30) | -0.50 [-0.55, -0.47] | 0.16 |
| text | HIGH | 1.0 | 0.0137 | 0.0058 | 0.0042 | 0.0042 (K=10) | -0.52 [-0.58, -0.47] | — |
| text | MINIMAL | 0.3 | 0.0078 | 0.0033 | 0.0024 | 0.0024 (K=10) | -0.52 [-0.58, -0.48] | — |
| text | MINIMAL | 0.7 | 0.0107 | 0.0047 | 0.0034 | 0.0019 (K=30) | -0.51 [-0.55, -0.47] | — |
| text | MINIMAL | 1.0 | 0.0067 | 0.0028 | 0.0020 | 0.0020 (K=10) | -0.53 [-0.58, -0.48] | — |

## Prose summary (~120 words)

Across the Phase 3a matrices, the empirical K-consensus F1 SD shrinks with K at a mean log-log slope of -0.52 for the text track and -0.52 for the image track, against the i.i.d. theoretical reference of -0.5. All strata cluster tightly around -0.5; no stratum departs detectably from i.i.d. shrinkage. The ceiling-K paired bootstrap CI-width ratio is 0.16x at K=30 for HIGH-T0.7 text and 0.34x at K=10 for HIGH-T0.7 image -- consistent with the expected ~sqrt(K) contraction. **Important caveat**: because we use the mean of K single-pass F1s as the K-consensus proxy, the analysis recovers the i.i.d. shrinkage law by construction; departures from -0.5 would require subsample rebuilding of the actual greedy-vote consensus from per-pass detection geometries, not available from existing per-K aggregate evaluation files. This analysis is orthogonal to the image-track cross-condition Levene heterogeneity (W = 3.192, p = 0.0040) reported in Section 4 of the secondary-effects sibling.

## Methodology footnote

The Phase 3a evaluation outputs (`{thinking}-t{T}/n{K}/{rolldir}/evaluation.json`) store **vote-threshold sweeps** (`1ofK` to `KofK`) for a single K-pass consensus build per cell -- they do **not** store independent K-roll subsamples. To obtain a per-K SD, we approximate the K-consensus F1 estimator by the mean of K single-pass F1 values drawn (with replacement) from the K_max-pass pool, using the per-condition single-pass F1 lists in `secondary_effects.json[run_variability]`. **This proxy assumes pass-level i.i.d. errors and therefore recovers the -0.5 shrinkage law by construction**; the analysis thus serves as a sanity check against the i.i.d. expectation rather than an independent test of departure from i.i.d. To detect genuine shared-mode signal (slope > -0.3) one would need to rebuild greedy-vote consensus from per-pass detection geometries on multiple K-subsamples drawn from the K_max pool, then re-evaluate -- a follow-up that requires per-pass GeoJSONs in `outputs/h11/pv-diag-384/` and ~5--10 minutes of compute per stratum on sapphire. SD CIs use 1,000 percentile bootstrap iterations (seed 42); slope CIs use 1,000 nested-bootstrap iterations over the per-pass F1 pool. Image-track T=0.0 cells (K_max = 3) have only three single-pass replicates and so support only K = {1, 3} subsamples; no slope is fitted for those strata.

## Caveats

- **Proxy bias toward -0.5**: the mean-of-K-passes proxy mathematically yields slope = -0.5 under any scenario in which the per-pass F1s are drawn from a stable distribution (because SD of mean of K i.i.d. samples = sigma / sqrt(K)). Slopes departing meaningfully from -0.5 in this analysis would only emerge if the per-pass F1 distribution itself were non-stationary across the K_max-pass pool -- a property that is not the intended target of an SD-shrinkage diagnostic. **Treat the resulting slopes as confirming the i.i.d. expectation, not as an independent test for shared-mode signal.**
- **Subsample independence**: K-subset rolls share underlying per-pass detections, so the reported SD-across-rolls is a **lower bound** on the SD of K independent K-pass runs.
- **K_max = 3 strata**: image-track T=0.0 cells have only three single-pass replicates and so support only K = {1, 3} subsamples; no slope is fitted (need >= 3 K-levels).
- **Orthogonal to Levene**: the image-track Levene W = 3.192, p = 0.0040 cross-condition variance heterogeneity finding from `results/secondary-effects/secondary_effects.md` Section 4 stands; the present analysis examines within-cell shrinkage as K rises, not between-cell variance comparison.
- **Where genuine shared-mode signal lives**: the per-condition K=1 SDs themselves are still informative (HIGH conditions show SD = 0.012-0.022 for image vs 0.005-0.022 for text at K_max). To detect shared-mode shrinkage failure, future work should rebuild greedy-vote consensus on K-subsamples (see Methodology footnote).

## Output files

- `sd_shrinkage.json` -- full numeric results.
- `sd_shrinkage.png` -- log-log SD vs K, faceted by track.
- `report.md` -- this file.

*Generated: 2026-04-27T04:48:11.946090+00:00*
