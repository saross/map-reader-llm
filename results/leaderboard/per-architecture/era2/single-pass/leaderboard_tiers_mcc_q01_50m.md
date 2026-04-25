# Leaderboard (MCC tiers) — 50m buffer

**Generated**: 2026-04-25T14:12:19.923548+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 6 in 4 tier(s)

## Tier 1 (MCC: 0.734–0.752)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h11-pvd-pro-medium-text-baseline | 1-pass | 2 | text | 1 | 1 | 0.752 | 0.802 | [0.761, 0.841] | 0.807 | 0.798 |
| 2 | h11-pvd-pro-medium-image-baseline | 1-pass | 2 | image | 1 | 1 | 0.734 | 0.778 | [0.740, 0.812] | 0.715 | 0.853 |

## Tier 2 (MCC: 0.597–0.597)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 3 | h11-n1-pro-image-medium-t07 | 1-pass | 2 | image | 1 | 1 | 0.597 | 0.586 | [0.523, 0.631] | 0.428 | 0.926 |

## Tier 3 (MCC: 0.309–0.311)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 4 | h11-pvd-image-baseline | 1-pass | 2 | image | 1 | 1 | 0.311 | 0.681 | [0.636, 0.715] | 0.539 | 0.924 |
| 5 | h11-n1-pro-text-medium-t07 | 1-pass | 2 | text | 1 | 1 | 0.309 | 0.430 | [0.371, 0.484] | 0.280 | 0.929 |

## Tier 4 (MCC: -0.001–-0.001)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 6 | h11-pvd-text-baseline | 1-pass | 2 | text | 1 | 1 | -0.001 | 0.536 | [0.475, 0.594] | 0.379 | 0.913 |
