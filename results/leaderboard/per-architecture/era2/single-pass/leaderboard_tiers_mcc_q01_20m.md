# Leaderboard (MCC tiers) — 20m buffer

**Generated**: 2026-04-25T14:12:19.923256+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 6 in 4 tier(s)

## Tier 1 (MCC: 0.734–0.752)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h11-pvd-pro-medium-text-baseline | 1-pass | 2 | text | 1 | 1 | 0.752 | 0.763 | [0.713, 0.806] | 0.767 | 0.759 |
| 2 | h11-pvd-pro-medium-image-baseline | 1-pass | 2 | image | 1 | 1 | 0.734 | 0.606 | [0.556, 0.651] | 0.557 | 0.664 |

## Tier 2 (MCC: 0.597–0.597)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 3 | h11-n1-pro-image-medium-t07 | 1-pass | 2 | image | 1 | 1 | 0.597 | 0.452 | [0.401, 0.496] | 0.331 | 0.715 |

## Tier 3 (MCC: 0.309–0.311)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 4 | h11-pvd-image-baseline | 1-pass | 2 | image | 1 | 1 | 0.311 | 0.600 | [0.555, 0.637] | 0.474 | 0.814 |
| 5 | h11-n1-pro-text-medium-t07 | 1-pass | 2 | text | 1 | 1 | 0.309 | 0.416 | [0.359, 0.468] | 0.271 | 0.899 |

## Tier 4 (MCC: -0.001–-0.001)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 6 | h11-pvd-text-baseline | 1-pass | 2 | text | 1 | 1 | -0.001 | 0.520 | [0.462, 0.576] | 0.368 | 0.885 |
