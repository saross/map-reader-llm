# Leaderboard (MCC tiers) — 50m buffer

**Generated**: 2026-04-25T13:29:49.629608+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 21 in 2 tier(s)

## Tier 1 (MCC: 0.147–0.281)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h5-track1-image-verbose | 1-pass | 1 | image | 1 | 1 | 0.281 | 0.726 | [0.686, 0.761] | 0.627 | 0.863 |
| 2 | h5-track1-image-terse | 1-pass | 1 | image | 1 | 1 | 0.223 | 0.717 | [0.675, 0.750] | 0.608 | 0.872 |
| 3 | h4-config-default | 1-pass | 1 | image | 1 | 1 | 0.214 | 0.734 | [0.695, 0.769] | 0.630 | 0.879 |
| 4 | h4-canonical-last | 1-pass | 1 | image | 1 | 1 | 0.212 | 0.724 | [0.681, 0.757] | 0.610 | 0.889 |
| 5 | h8-track1-image-exploratory-pure-positive-4hp | 1-pass | 1 | image | 1 | 1 | 0.162 | 0.724 | [0.680, 0.760] | 0.615 | 0.879 |
| 6 | h8-track1-image-scale-8 | 1-pass | 1 | image | 1 | 1 | 0.147 | 0.704 | [0.663, 0.741] | 0.599 | 0.855 |

## Tier 2 (MCC: 0.000–0.133)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 7 | h8-track1-image-scale-4 | 1-pass | 1 | image | 1 | 1 | 0.133 | 0.690 | [0.636, 0.738] | 0.575 | 0.865 |
| 8 | h4-canonical-first | 1-pass | 1 | image | 1 | 1 | 0.098 | 0.730 | [0.687, 0.765] | 0.620 | 0.887 |
| 9 | h8-track1-image-plus-hp | 1-pass | 1 | image | 1 | 1 | 0.098 | 0.730 | [0.687, 0.765] | 0.620 | 0.887 |
| 10 | h8-track1-image-canonical | 1-pass | 1 | image | 1 | 1 | 0.098 | 0.689 | [0.645, 0.727] | 0.603 | 0.805 |
| 11 | h8-track1-image-exploratory-pure-positive-canon | 1-pass | 1 | image | 1 | 1 | 0.097 | 0.699 | [0.656, 0.737] | 0.609 | 0.822 |
| 12 | h8-track1-image-pure-positive-canon | 1-pass | 1 | image | 1 | 1 | 0.097 | 0.695 | [0.649, 0.734] | 0.602 | 0.822 |
| 13 | h4-random | 1-pass | 1 | image | 1 | 1 | 0.084 | 0.697 | [0.649, 0.738] | 0.577 | 0.879 |
| 14 | h5-track2-text-verbose | 1-pass | 1 | text | 1 | 1 | 0.081 | 0.667 | [0.614, 0.715] | 0.559 | 0.828 |
| 15 | h5-track2-text-terse | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.654 | [0.599, 0.708] | 0.530 | 0.853 |
| 16 | h8-track1-image-exploratory-pure-positive-2hp | 1-pass | 1 | image | 1 | 1 | 0.000 | 0.678 | [0.627, 0.723] | 0.561 | 0.857 |
| 17 | h8-track2-text-canonical | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.650 | [0.590, 0.700] | 0.521 | 0.866 |
| 18 | h8-track2-text-plus-hp | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.654 | [0.600, 0.702] | 0.527 | 0.865 |
| 19 | h8-track2-text-pure-positive-canon | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.655 | [0.599, 0.705] | 0.526 | 0.866 |
| 20 | h8-track2-text-scale-4 | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.654 | [0.599, 0.703] | 0.527 | 0.863 |
| 21 | h8-track2-text-scale-8 | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.658 | [0.601, 0.706] | 0.530 | 0.866 |
