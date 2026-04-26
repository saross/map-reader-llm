# Leaderboard (MCC tiers) — 40m buffer

**Generated**: 2026-04-26T07:18:22.594782+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 14 in 2 tier(s)

## Tier 1 (MCC: 0.640–0.772)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h8v2-scale-4 | greedy | 3 | image | 5 | 4 | 0.772 | 0.812 | [0.770, 0.852] | 0.910 | 0.734 |
| 2 | h8v2-scale-8 | greedy | 3 | image | 5 | 3 | 0.739 | 0.808 | [0.769, 0.847] | 0.811 | 0.806 |
| 3 | h12v2-r3-hp-heavy | greedy | 3 | image | 5 | 3 | 0.733 | 0.809 | [0.771, 0.849] | 0.801 | 0.818 |
| 4 | h8v2-plus-hp | greedy | 3 | image | 5 | 4 | 0.732 | 0.785 | [0.740, 0.828] | 0.886 | 0.705 |
| 5 | h8v2-scale-16 | greedy | 3 | image | 5 | 3 | 0.726 | 0.794 | [0.750, 0.834] | 0.778 | 0.812 |
| 6 | h12v2-r1-hn-heavy | greedy | 3 | image | 5 | 3 | 0.725 | 0.824 | [0.785, 0.861] | 0.814 | 0.834 |
| 7 | h8v2-scale-32 | greedy | 3 | image | 5 | 4 | 0.718 | 0.752 | [0.702, 0.799] | 0.872 | 0.661 |
| 8 | h10v2-pool_160_hp4hn4 | greedy | 3 | image | 5 | 4 | 0.718 | 0.786 | [0.738, 0.830] | 0.924 | 0.683 |
| 9 | h12v2-r2-balanced | greedy | 3 | image | 5 | 4 | 0.718 | 0.786 | [0.738, 0.830] | 0.924 | 0.683 |
| 10 | h10v2-pool_080_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.691 | 0.779 | [0.730, 0.823] | 0.754 | 0.806 |
| 11 | h10v2-pool_020_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.686 | 0.781 | [0.738, 0.826] | 0.753 | 0.812 |
| 12 | h8v2-canonical | greedy | 3 | image | 5 | 4 | 0.680 | 0.776 | [0.725, 0.827] | 0.868 | 0.702 |
| 13 | h10v2-pool_040_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.640 | 0.781 | [0.738, 0.823] | 0.753 | 0.812 |

## Tier 2 (MCC: 0.599–0.599)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 14 | h8v2-pure-positive-canon | greedy | 3 | image | 5 | 3 | 0.599 | 0.784 | [0.738, 0.824] | 0.730 | 0.846 |
