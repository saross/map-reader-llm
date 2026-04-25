# Leaderboard (MCC tiers) — 30m buffer

**Generated**: 2026-04-25T14:12:19.513320+00:00
**Tiering metric**: MCC
**FDR q**: 0.05
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 6 in 4 tier(s)

## Tier 1 (MCC: 0.734–0.752)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h11-pvd-pro-medium-text-baseline | 1-pass | 2 | text | 1 | 1 | 0.752 | 0.784 | [0.736, 0.827] | 0.788 | 0.779 |
| 2 | h11-pvd-pro-medium-image-baseline | 1-pass | 2 | image | 1 | 1 | 0.734 | 0.734 | [0.692, 0.772] | 0.674 | 0.805 |

## Tier 2 (MCC: 0.597–0.597)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 3 | h11-n1-pro-image-medium-t07 | 1-pass | 2 | image | 1 | 1 | 0.597 | 0.538 | [0.481, 0.581] | 0.393 | 0.851 |

## Tier 3 (MCC: 0.309–0.311)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 4 | h11-pvd-image-baseline | 1-pass | 2 | image | 1 | 1 | 0.311 | 0.655 | [0.612, 0.689] | 0.519 | 0.890 |
| 5 | h11-n1-pro-text-medium-t07 | 1-pass | 2 | text | 1 | 1 | 0.309 | 0.428 | [0.370, 0.480] | 0.278 | 0.924 |

## Tier 4 (MCC: -0.001–-0.001)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 6 | h11-pvd-text-baseline | 1-pass | 2 | text | 1 | 1 | -0.001 | 0.530 | [0.471, 0.587] | 0.375 | 0.903 |
