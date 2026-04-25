# Leaderboard (MCC tiers) — 100m buffer

**Generated**: 2026-04-25T14:12:19.923621+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 6 in 4 tier(s)

## Tier 1 (MCC: 0.734–0.752)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h11-pvd-pro-medium-text-baseline | 1-pass | 2 | text | 1 | 1 | 0.752 | 0.807 | [0.765, 0.845] | 0.812 | 0.802 |
| 2 | h11-pvd-pro-medium-image-baseline | 1-pass | 2 | image | 1 | 1 | 0.734 | 0.794 | [0.755, 0.829] | 0.730 | 0.871 |

## Tier 2 (MCC: 0.597–0.597)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 3 | h11-n1-pro-image-medium-t07 | 1-pass | 2 | image | 1 | 1 | 0.597 | 0.593 | [0.533, 0.639] | 0.434 | 0.938 |

## Tier 3 (MCC: 0.309–0.311)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 4 | h11-pvd-image-baseline | 1-pass | 2 | image | 1 | 1 | 0.311 | 0.689 | [0.644, 0.722] | 0.546 | 0.936 |
| 5 | h11-n1-pro-text-medium-t07 | 1-pass | 2 | text | 1 | 1 | 0.309 | 0.432 | [0.374, 0.485] | 0.281 | 0.933 |

## Tier 4 (MCC: -0.001–-0.001)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 6 | h11-pvd-text-baseline | 1-pass | 2 | text | 1 | 1 | -0.001 | 0.538 | [0.478, 0.597] | 0.381 | 0.917 |
