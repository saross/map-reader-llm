# TP-only localisation precision — Obs 296 diagnostic #1

**Anchor**: Obs 296 (`docs/notes/reflections/working-notes.md`, 2026-04-28) reframed Obs 295's GS 25 m attractor-pull cap as 'post-calibration precision on the calibration corpus' rather than 'fundamental detector spatial precision', and the 55-map 100/125 m caps (Obs 298) as 'native unfamiliar-map precision'. This diagnostic separates detector spatial precision (TP localisation) from FP-anchoring failure modes, by computing TP-to-GT distance distributions across the five corpus conditions at a uniform 25 m matching scope.

Reference sets: GS curator-corrected n=569; 55-map post-review n=4744. TP filter: nearest-GT distance ≤ 25 m, applied uniformly across all five conditions (no per-corpus cap difference).

## 1. Per-condition TP distance descriptors

| condition               |   n_detections |   n_tp_at_25m |   tp_rate |   mean_m |   median_m |   p75_m |   p90_m |   p95_m |
|:------------------------|---------------:|--------------:|----------:|---------:|-----------:|--------:|--------:|--------:|
| GS text-HIGH-T0.7 (K=5) |            392 |           365 |     0.931 |    7.186 |      6.36  |   9.406 |  12.856 |  15.495 |
| 55-map T=0.3 text-HIGH  |            692 |            30 |     0.043 |   14.888 |     14.429 |  21.859 |  23.216 |  24.046 |
| 55-map T=0.7 text-HIGH  |            630 |            20 |     0.032 |   13.765 |     12.832 |  19.363 |  24.14  |  24.277 |
| 55-map image (T=0.7)    |           1029 |            52 |     0.051 |   17.51  |     18.379 |  23.031 |  24.286 |  24.591 |
| 55-map text-MIN         |            585 |            24 |     0.041 |   13.333 |     14.408 |  19.556 |  20.952 |  22.053 |

## 2. Histogram counts (5 m bins)

| condition               |   (0, 5] |   (5, 10] |   (10, 15] |   (15, 20] |   (20, 25] |
|:------------------------|---------:|----------:|-----------:|-----------:|-----------:|
| GS text-HIGH-T0.7 (K=5) |      126 |       163 |         53 |         17 |          6 |
| 55-map T=0.3 text-HIGH  |        2 |         8 |          5 |          5 |         10 |
| 55-map T=0.7 text-HIGH  |        1 |         6 |          7 |          1 |          5 |
| 55-map image (T=0.7)    |        2 |         7 |          6 |         16 |         21 |
| 55-map text-MIN         |        5 |         3 |          5 |          5 |          6 |

## 3. Pairwise Kolmogorov–Smirnov tests (GS vs each 55-map)

| pair                                |   gs_n |   other_n |   ks_statistic |   p_value | significant_alpha_0.05   | significant_bonferroni_4pairs   |
|:------------------------------------|-------:|----------:|---------------:|----------:|:-------------------------|:--------------------------------|
| gs-text-high-t0.7 vs 55map-t0.3     |    365 |        30 |         0.5237 |   0       | True                     | True                            |
| gs-text-high-t0.7 vs 55map-t0.7     |    365 |        20 |         0.5233 |   2.4e-05 | True                     | True                            |
| gs-text-high-t0.7 vs 55map-image    |    365 |        52 |         0.7173 |   0       | True                     | True                            |
| gs-text-high-t0.7 vs 55map-text-min |    365 |        24 |         0.5291 |   2e-06   | True                     | True                            |

## 4. Interpretation

**Verdict — mixed; majority FP-driven with one 55-map run partly loose.** GS median TP distance (6.36 m) is tight; 3 of 4 55-map medians sit inside the 5–15 m 'tight overlap' band. The remaining run(s) sit above 15 m (max 55-map median 18.38 m) but well below the 30 m 'real spatial-precision difference' threshold defined in the Obs 296 brief. After accounting for the ~25 m student-GT positional jitter (Obs 260, expected median floor ≈ 12 m), the residual cross-corpus precision gap on the loosest 55-map run is 5.9 m. The cap difference between GS and 55-map is therefore primarily FP-anchoring driven, with a modest modality-specific looseness on the looser run(s) contributing a smaller secondary effect. Obs 296's failure-of-generalisation framing is broadly supported.

**GT-jitter caveat**: the 55-map student GT carries ~25 m positional jitter (Obs 260). With unbiased 25 m jitter, a perfectly-localised detector yields median nearest-GT distance ≈ 12–13 m (Rayleigh-like floor). 55-map medians near 13 m are therefore consistent with a near-perfect detector + GT jitter; only medians materially above ~15 m indicate genuine detector looseness on top of the jitter floor. The GS curator-corrected reference has no comparable jitter, so the GS median (6.36 m here) reflects detector precision more directly.

## 5. Reproducibility

Script: `scripts/analyse_tp_localisation_55maps_vs_gs.py` (ruff-clean). KDTree query only — no permutations, no random seed required. Rerun with `python scripts/analyse_tp_localisation_55maps_vs_gs.py` from the repo root.

