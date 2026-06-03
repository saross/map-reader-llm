# N=1 baseline leaderboard — statistical tiering (20 m)

- **Metric**: micro-average F1 @ 20 m (pass-averaged per-tile; expected single-pass)
- **Permutations**: 10,000 per pair, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 153 (112 significant) -> **6 tiers**
- **Tie set (Tier 1)**: pv-diag-384::baseline-pro-text-medium-t-0-0, pv-diag-384::baseline-pro-text-high-t-0-7

| rank | condition | passes | board F1@20m | micro-F1-of-mean | gap | tier |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `baseline-pro-text-medium-t-0-0` | 1 | 0.763 | 0.763 | +0.000 | 1 |
| 2 | `baseline-pro-text-high-t-0-7` | 10 | 0.745 | 0.745 | +0.000 | 1 |
| 3 | `baseline-pro-image-medium-t-0-0` | 1 | 0.606 | 0.606 | -0.000 | 2 |
| 4 | `baseline-flash-image-minimal-t-0-0` | 1 | 0.600 | 0.599 | -0.000 | 2 |
| 5 | `baseline-flash-image-minimal-t-0-0-487-tiles` | 3 | 0.598 | 0.598 | -0.000 | 2 |
| 6 | `baseline-flash-image-minimal-t-0-3` | 3 | 0.593 | 0.593 | -0.000 | 2 |
| 7 | `baseline-pro-image-high-t-0-7` | 5 | 0.591 | 0.591 | +0.000 | 2 |
| 8 | `baseline-flash-image-minimal-t-0-7` | 10 | 0.553 | 0.553 | +0.000 | 3 |
| 9 | `baseline-pro-image-high-t-0-0` | 3 | 0.528 | 0.528 | -0.000 | 3 |
| 10 | `baseline-flash-text-minimal-t-0-0-pv-baseline` | 1 | 0.520 | 0.520 | -0.000 | 3 |
| 11 | `baseline-flash-text-minimal-t-0-0` | 10 | 0.503 | 0.503 | -0.000 | 4 |
| 12 | `baseline-flash-text-minimal-t-0-3` | 3 | 0.499 | 0.499 | +0.000 | 4 |
| 13 | `baseline-flash-image-high-t-0-7` | 10 | 0.499 | 0.498 | -0.000 | 4 |
| 14 | `baseline-pro-text-high-t-0-0` | 3 | 0.494 | 0.494 | -0.000 | 4 |
| 15 | `baseline-flash-text-minimal-t-0-7` | 30 | 0.488 | 0.488 | -0.000 | 4 |
| 16 | `baseline-pro-image-medium-t-0-7` | 1 | 0.452 | 0.452 | +0.000 | 5 |
| 17 | `baseline-pro-text-medium-t-0-7` | 1 | 0.416 | 0.416 | -0.000 | 5 |
| 18 | `baseline-flash-text-high-t-0-7` | 30 | 0.387 | 0.387 | -0.000 | 6 |
