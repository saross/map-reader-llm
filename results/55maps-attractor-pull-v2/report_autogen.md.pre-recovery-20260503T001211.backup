# Attractor-pull v2 — multi-run shell-wise null analysis

**Anchor**: Obs 272 (`docs/notes/reflections/working-notes.md`, 2026-04-21) established the attractor-pull cutoff at ~125 m using the image-generalisation review only. v2 re-runs the same shell-wise within-tile permutation null on each of the 4 corrected 55-map runs and synthesises a consensus cutoff.

## 1. Method

For each run, observed shell rates are taken directly from the reviewer's ``buffer_metres`` label (the band at which a real mound is visible inside the buffer; ``not_mound`` rows are mapped to the > 286 m shell). The null distribution is M = 1,000 within-tile permutations (seed 42) of student GT distances. Bias correction divides the null rate by the student-GT fraction of the real-mound universe to account for the reviewer-promoted phantoms absent from student GT. Per-shell significance is the one-sided permutation p-value against the bias-corrected null (P(null_corrected ≥ obs)), alpha = 0.05.

Student-GT reference set: 4744 mounds (4-corner of the corrected reviewed reference).
Shell edges (m): 50, 75, 100, 125, 150, 286. The (200, 286] shell corresponds to the >150-m / not_mound review label, with effective tolerance 286 m (200 × √2 + 5 display-pixels on the 400 m × 400 m crop).

## 2. Per-run shell tables

### T=0.3 text-HIGH — n=692, bias_correction=0.9231

|   R_inner_m |   R_outer_m |   obs_rate_in_shell |   null_mean_bias_corrected |   lift_ratio_bias_corrected |   signal_fraction_bias_corrected |   p_value_bias_corrected | significant   |
|------------:|------------:|--------------------:|---------------------------:|----------------------------:|---------------------------------:|-------------------------:|:--------------|
|           0 |          50 |              0.4451 |                     0.0031 |                      145.88 |                           0.9931 |                    0.001 | True          |
|          50 |          75 |              0.0347 |                     0.0038 |                        9.23 |                           0.8917 |                    0.001 | True          |
|          75 |         100 |              0.0202 |                     0.005  |                        4.03 |                           0.7521 |                    0.001 | True          |
|         100 |         125 |              0.0101 |                     0.0059 |                        1.71 |                           0.416  |                    0.093 | False         |
|         125 |         150 |              0.0145 |                     0.0069 |                        2.08 |                           0.5203 |                    0.013 | True          |
|         150 |         286 |              0.0462 |                     0.0552 |                        0.84 |                          -0.1931 |                    0.842 | False         |

**Per-run cutoff**: 100 m (deepest shell outer edge with bias-corrected p < 0.05)

### T=0.7 text-HIGH — n=630, bias_correction=0.9309

|   R_inner_m |   R_outer_m |   obs_rate_in_shell |   null_mean_bias_corrected |   lift_ratio_bias_corrected |   signal_fraction_bias_corrected |   p_value_bias_corrected | significant   |
|------------:|------------:|--------------------:|---------------------------:|----------------------------:|---------------------------------:|-------------------------:|:--------------|
|           0 |          50 |              0.4254 |                     0.0028 |                      153.25 |                           0.9935 |                    0.001 | True          |
|          50 |          75 |              0.0286 |                     0.0034 |                        8.48 |                           0.8821 |                    0.001 | True          |
|          75 |         100 |              0.0286 |                     0.0047 |                        6.04 |                           0.8344 |                    0.001 | True          |
|         100 |         125 |              0.0175 |                     0.0059 |                        2.96 |                           0.6617 |                    0.001 | True          |
|         125 |         150 |              0.0079 |                     0.0069 |                        1.15 |                           0.1278 |                    0.37  | False         |
|         150 |         286 |              0.0508 |                     0.0545 |                        0.93 |                          -0.0721 |                    0.659 | False         |

**Per-run cutoff**: 125 m (deepest shell outer edge with bias-corrected p < 0.05)

### image (T=0.7) — n=1029, bias_correction=0.8641

|   R_inner_m |   R_outer_m |   obs_rate_in_shell |   null_mean_bias_corrected |   lift_ratio_bias_corrected |   signal_fraction_bias_corrected |   p_value_bias_corrected | significant   |
|------------:|------------:|--------------------:|---------------------------:|----------------------------:|---------------------------------:|-------------------------:|:--------------|
|           0 |          50 |              0.4606 |                     0.0047 |                       97.78 |                           0.9898 |                    0.001 | True          |
|          50 |          75 |              0.1176 |                     0.0056 |                       21.1  |                           0.9526 |                    0.001 | True          |
|          75 |         100 |              0.0457 |                     0.0075 |                        6.07 |                           0.8352 |                    0.001 | True          |
|         100 |         125 |              0.0185 |                     0.0093 |                        1.99 |                           0.4973 |                    0.003 | True          |
|         125 |         150 |              0.0107 |                     0.0108 |                        0.99 |                          -0.0125 |                    0.502 | False         |
|         150 |         286 |              0.0719 |                     0.0814 |                        0.88 |                          -0.1322 |                    0.865 | False         |

**Per-run cutoff**: 125 m (deepest shell outer edge with bias-corrected p < 0.05)

### text-MIN — n=585, bias_correction=0.9361

|   R_inner_m |   R_outer_m |   obs_rate_in_shell |   null_mean_bias_corrected |   lift_ratio_bias_corrected |   signal_fraction_bias_corrected |   p_value_bias_corrected | significant   |
|------------:|------------:|--------------------:|---------------------------:|----------------------------:|---------------------------------:|-------------------------:|:--------------|
|           0 |          50 |              0.4274 |                     0.0028 |                      151.76 |                           0.9934 |                    0.001 | True          |
|          50 |          75 |              0.0342 |                     0.0034 |                       10.08 |                           0.9008 |                    0.001 | True          |
|          75 |         100 |              0.012  |                     0.0045 |                        2.68 |                           0.6262 |                    0.015 | True          |
|         100 |         125 |              0.0085 |                     0.0056 |                        1.54 |                           0.3486 |                    0.199 | False         |
|         125 |         150 |              0.012  |                     0.0068 |                        1.76 |                           0.433  |                    0.082 | False         |
|         150 |         286 |              0.0598 |                     0.0527 |                        1.14 |                           0.1193 |                    0.254 | False         |

**Per-run cutoff**: 100 m (deepest shell outer edge with bias-corrected p < 0.05)

## 3. Cross-run consensus

|   R_outer_m | t0.3   | t0.7   | image   | text-min   |   n_runs_significant | all_significant   |
|------------:|:-------|:-------|:--------|:-----------|---------------------:|:------------------|
|          50 | sig    | sig    | sig     | sig        |                    4 | yes               |
|          75 | sig    | sig    | sig     | sig        |                    4 | yes               |
|         100 | sig    | sig    | sig     | sig        |                    4 | yes               |
|         125 | —      | sig    | sig     | —          |                    2 | no                |
|         150 | sig    | —      | —       | —          |                    1 | no                |
|         286 | —      | —      | —       | —          |                    0 | no                |

**Most-permissive consensus cutoff**: 100 m (largest shell outer edge significant in all 4 runs).
**Majority-loses breakpoint**: 125 m (first shell where < 3/4 runs are significant).

### Per-run cutoff summary

| run             |   n_candidates |   cutoff_m |
|:----------------|---------------:|-----------:|
| T=0.3 text-HIGH |            692 |        100 |
| T=0.7 text-HIGH |            630 |        125 |
| image (T=0.7)   |           1029 |        125 |
| text-MIN        |            585 |        100 |

## 4. Cross-reference to Obs 272

Obs 272 reported a 125-m cutoff using only the image-generalisation review and a 1,000-permutation within-tile null. The v2 image-only cutoff is **125 m** — corroborates Obs 272 exactly.

The cross-run **consensus cutoff** (most permissive value significant in every run) is **100 m**.

**Verdict**: Obs 272's 125 m claim is revised downward by the multi-run consensus — at least one run shows the cutoff at a tighter radius.

### Cross-run disagreement (range 100–125 m)

Per-run cutoffs differ by 25 m. Inspect the per-run shell tables in §2 to see which shells flip significance between runs.

## 5. Reproducibility

Script: `scripts/analyse_attractor_pull_v2.py` (ruff-clean). Seed 42, M = 1000 permutations per run. Rerun with `python scripts/analyse_attractor_pull_v2.py` from the repo root.
