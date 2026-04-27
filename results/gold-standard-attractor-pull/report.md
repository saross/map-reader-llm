# Attractor-pull GS — geometric KDTree shell-wise null analysis

**Anchor**: Obs 294 (`docs/notes/reflections/working-notes.md`, 2026-04-28) established the 55-map attractor-pull cutoff at 125 m, using reviewer-mediated buffer-band labels because the student GT carries ~25 m positional jitter (Obs 260). The 4-map gold-standard corpus has a curator-corrected reference with no positional jitter, so we replace the reviewer-label-based observed-rate construction with a direct geometric KDTree query of detection centroid against reference centroid. Companion finding to Obs 294.

## 1. Method

For each condition, observed shell rates are computed by building a `scipy.spatial.cKDTree` on the curator-corrected reference centroids (EPSG:32635), querying nearest-reference distance for each detection centroid, and binning into shells (0, 25] / (25, 50] / (50, 75] / (75, 100] / (100, 125] / (125, 150] / (150, 286] m. The null distribution is M = 1000 within-tile permutations (seed 42) of the same KDTree query. Per-shell significance is the one-sided permutation p-value `(1 + #{null ≥ obs}) / (1 + M)`, alpha = 0.05. No bias correction is applied (the reference is precise; the null and observed rates are computed against the same universe).

Reference set: 569 mounds (curator-corrected 4-map gold-standard reference).
Shell edges (m): 25, 50, 75, 100, 125, 150, 286. The (150, 286] shell is preserved as a single bucket for cross-corpus comparability with the 55-map analysis (Obs 294 §5 — splitting at 200 m flagged a reviewer-labelling artefact on the 55-map corpus). Detections with d > 286 m fall outside all shells (analogous to ``not_mound`` rows in Obs 272 / 294).

## 2. Per-condition shell tables

### text-HIGH-T0.7 (K=5) — n=392, within-286m=376 (95.9 %)

|   R_inner_m |   R_outer_m |   obs_rate_in_shell |   null_mean_in_shell |   lift_ratio |   signal_fraction |   p_value | significant   |
|------------:|------------:|--------------------:|---------------------:|-------------:|------------------:|----------:|:--------------|
|           0 |          25 |              0.9311 |               0.002  |       466.75 |            0.9979 |    0.001  | True          |
|          25 |          50 |              0.0128 |               0.006  |         2.14 |            0.5322 |    0.0909 | False         |
|          50 |          75 |              0.0051 |               0.0094 |         0.54 |           -0.846  |    0.8841 | False         |
|          75 |         100 |              0.0026 |               0.0125 |         0.2  |           -3.888  |    0.992  | False         |
|         100 |         125 |              0      |               0.0157 |         0    |            0      |    1      | False         |
|         125 |         150 |              0      |               0.0184 |         0    |            0      |    1      | False         |
|         150 |         286 |              0.0077 |               0.1364 |         0.06 |          -16.8257 |    1      | False         |

**Per-condition cutoff**: 25 m (deepest shell outer edge with permutation p < 0.05)

### image-HIGH-T0.7 (K=5) — n=414, within-286m=406 (98.1 %)

|   R_inner_m |   R_outer_m |   obs_rate_in_shell |   null_mean_in_shell |   lift_ratio |   signal_fraction |   p_value | significant   |
|------------:|------------:|--------------------:|---------------------:|-------------:|------------------:|----------:|:--------------|
|           0 |          25 |              0.8647 |               0.002  |       436.05 |            0.9977 |    0.001  | True          |
|          25 |          50 |              0.0725 |               0.0057 |        12.76 |            0.9216 |    0.001  | True          |
|          50 |          75 |              0.0121 |               0.0089 |         1.36 |            0.2642 |    0.3247 | False         |
|          75 |         100 |              0.0048 |               0.0124 |         0.39 |           -1.567  |    0.959  | False         |
|         100 |         125 |              0.0048 |               0.0152 |         0.32 |           -2.1365 |    0.982  | False         |
|         125 |         150 |              0      |               0.0178 |         0    |            0      |    1      | False         |
|         150 |         286 |              0.0217 |               0.1332 |         0.16 |           -5.125  |    1      | False         |

**Per-condition cutoff**: 50 m (deepest shell outer edge with permutation p < 0.05)

### SCALE4-optimal (image, K=10) — n=411, within-286m=403 (98.1 %)

|   R_inner_m |   R_outer_m |   obs_rate_in_shell |   null_mean_in_shell |   lift_ratio |   signal_fraction |   p_value | significant   |
|------------:|------------:|--------------------:|---------------------:|-------------:|------------------:|----------:|:--------------|
|           0 |          25 |              0.8394 |               0.0019 |       448.63 |            0.9978 |    0.001  | True          |
|          25 |          50 |              0.0925 |               0.0058 |        15.83 |            0.9368 |    0.001  | True          |
|          50 |          75 |              0.017  |               0.0089 |         1.92 |            0.478  |    0.0759 | False         |
|          75 |         100 |              0.0024 |               0.0121 |         0.2  |           -3.991  |    0.992  | False         |
|         100 |         125 |              0.0049 |               0.0153 |         0.32 |           -2.148  |    0.993  | False         |
|         125 |         150 |              0      |               0.0181 |         0    |            0      |    1      | False         |
|         150 |         286 |              0.0243 |               0.133  |         0.18 |           -4.467  |    1      | False         |

**Per-condition cutoff**: 50 m (deepest shell outer edge with permutation p < 0.05)

## 3. Cross-condition consensus

|   R_outer_m | text-high-t0.7   | image-high-t0.7   | scale4-optimal   |   n_sig | all_sig   |
|------------:|:-----------------|:------------------|:-----------------|--------:|:----------|
|          25 | sig              | sig               | sig              |       3 | yes       |
|          50 | —                | sig               | sig              |       2 | no        |
|          75 | —                | —                 | —                |       0 | no        |
|         100 | —                | —                 | —                |       0 | no        |
|         125 | —                | —                 | —                |       0 | no        |
|         150 | —                | —                 | —                |       0 | no        |
|         286 | —                | —                 | —                |       0 | no        |

**Most-permissive consensus cutoff**: 25 m (largest shell outer edge significant in all three conditions).
**Majority-loses breakpoint**: 75 m (first shell where < 2/3 conditions are significant).

### Per-condition cutoff summary

| condition                    |   n_detections |   cutoff_m |
|:-----------------------------|---------------:|-----------:|
| text-HIGH-T0.7 (K=5)         |            392 |         25 |
| image-HIGH-T0.7 (K=5)        |            414 |         50 |
| SCALE4-optimal (image, K=10) |            411 |         50 |

## 4. Cross-reference to Obs 294 (55-map cap = 125 m)

**Verdict**: the GS cap (25 m) is tighter than the 55-map cap (125 m), as predicted by the F1-plateau evidence (GS plateau at R = 25 m vs 55-map > 50 m; GS ~2× denser in mounds-per-tile, so within-tile null saturates sooner).

### Cross-condition disagreement (range 25–50 m)

Per-condition cutoffs differ by 25 m. Inspect the per-condition shell tables in §2 to see which shells flip significance between conditions.

## 5. Reproducibility

Script: `scripts/analyse_attractor_pull_gs.py` (ruff-clean). Seed 42, M = 1000 permutations per condition. Rerun with `python scripts/analyse_attractor_pull_gs.py` from the repo root.
