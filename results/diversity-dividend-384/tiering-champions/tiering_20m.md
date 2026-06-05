# Diversity dividend — consensus vs single-pass baseline (20 m)

- **Cells**: 4 consensus (champion) + 18 single-pass = 22
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Tiers**: 7; **Tier 1** = `consensus-flash-high-text-26of30`, `n1-pro-rerun-384::baseline-pro-text-high-t-0-0`, `pv-diag-384::baseline-pro-text-medium-t-0-0`

| rank | cell | kind | think | mod | vote | F1@20m | MCC | tier |
|---:|---|---|---|---|---|---:|---:|---:|
| 1 | `consensus-flash-high-text-26of30` | champion | high | text | 26-of-30 | 0.814 | 0.620 | 1 |
| 2 | `baseline-pro-text-high-t-0-0` | single-pass | — | — | — | 0.804 | 0.790 | 1 |
| 3 | `baseline-pro-text-medium-t-0-0` | single-pass | — | — | — | 0.792 | 0.790 | 1 |
| 4 | `baseline-pro-text-medium-t-0-7` | single-pass | — | — | — | 0.755 | 0.768 | 2 |
| 5 | `consensus-flash-high-image-7of10` | champion | high | image | 7-of-10 | 0.750 | 0.678 | 2 |
| 6 | `baseline-pro-text-high-t-0-7` | single-pass | — | — | — | 0.745 | 0.747 | 2 |
| 7 | `consensus-flash-minimal-image-8of10` | champion | minimal | image | 8-of-10 | 0.680 | 0.406 | 3 |
| 8 | `baseline-pro-image-high-t-0-0` | single-pass | — | — | — | 0.666 | 0.868 | 3 |
| 9 | `consensus-flash-minimal-text-29of30` | champion | minimal | text | 29-of-30 | 0.661 | 0.381 | 3 |
| 10 | `baseline-pro-image-medium-t-0-0` | single-pass | — | — | — | 0.655 | 0.868 | 3 |
| 11 | `baseline-flash-image-minimal-t-0-0` | single-pass | — | — | — | 0.600 | 0.312 | 4 |
| 12 | `baseline-flash-image-minimal-t-0-0-487-tiles` | single-pass | — | — | — | 0.598 | 0.314 | 4 |
| 13 | `baseline-pro-image-medium-t-0-7` | single-pass | — | — | — | 0.595 | 0.911 | 4 |
| 14 | `baseline-flash-image-minimal-t-0-3` | single-pass | — | — | — | 0.593 | 0.305 | 4 |
| 15 | `baseline-pro-image-high-t-0-7` | single-pass | — | — | — | 0.591 | 0.852 | 4 |
| 16 | `baseline-flash-image-minimal-t-0-7` | single-pass | — | — | — | 0.553 | 0.330 | 5 |
| 17 | `baseline-flash-text-minimal-t-0-0-pv-baseline` | single-pass | — | — | — | 0.520 | -0.004 | 5 |
| 18 | `baseline-flash-text-minimal-t-0-0` | single-pass | — | — | — | 0.503 | 0.046 | 6 |
| 19 | `baseline-flash-text-minimal-t-0-3` | single-pass | — | — | — | 0.499 | 0.039 | 6 |
| 20 | `baseline-flash-image-high-t-0-7` | single-pass | — | — | — | 0.499 | 0.602 | 6 |
| 21 | `baseline-flash-text-minimal-t-0-7` | single-pass | — | — | — | 0.488 | 0.078 | 6 |
| 22 | `baseline-flash-text-high-t-0-7` | single-pass | — | — | — | 0.387 | 0.331 | 7 |

## Headline contrasts

| claim | F1 a | F1 b | ΔF1 | p | BH-p | sig |
|---|---:|---:|---:|---:|---:|:--:|
| diversity-dividend (text): HIGH vs minimal consensus | 0.814 | 0.661 | +0.153 | 0.0000 | 0.0000 | **yes** |
| diversity-dividend (image): HIGH vs minimal consensus | 0.750 | 0.680 | +0.070 | 0.0001 | 0.0002 | **yes** |
| consensus vs matched single-pass (consensus-flash-high-text-26of30) | 0.814 | 0.387 | +0.427 | 0.0000 | 0.0000 | **yes** |
| consensus vs matched single-pass (consensus-flash-high-image-7of10) | 0.750 | 0.499 | +0.251 | 0.0000 | 0.0000 | **yes** |
| consensus vs matched single-pass (consensus-flash-minimal-image-8of10) | 0.680 | 0.553 | +0.127 | 0.0000 | 0.0000 | **yes** |
| consensus vs matched single-pass (consensus-flash-minimal-text-29of30) | 0.661 | 0.488 | +0.173 | 0.0000 | 0.0000 | **yes** |
| Flash text-HIGH consensus vs Pro single-pass leader | 0.814 | 0.804 | +0.010 | 0.6163 | 0.6622 | no |
