# Leaderboard (MCC tiers) — 20m buffer

**Generated**: 2026-05-06T03:01:29.972502+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 14 in 2 tier(s)

## Tier 1 (MCC: 0.640–0.772)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h8v2-scale-4 | greedy | 3 | image | 5 | 4 | 0.772 | 0.733 | [0.699, 0.760] | 0.821 | 0.661 |
| 2 | h8v2-scale-8 | greedy | 3 | image | 5 | 3 | 0.739 | 0.730 | [0.703, 0.757] | 0.732 | 0.727 |
| 3 | h12v2-r3-hp-heavy | greedy | 3 | image | 5 | 3 | 0.733 | 0.701 | [0.673, 0.728] | 0.693 | 0.709 |
| 4 | h8v2-plus-hp | greedy | 3 | image | 5 | 4 | 0.732 | 0.705 | [0.668, 0.730] | 0.795 | 0.633 |
| 5 | h8v2-scale-16 | greedy | 3 | image | 5 | 3 | 0.726 | 0.712 | [0.680, 0.741] | 0.697 | 0.727 |
| 6 | h12v2-r1-hn-heavy | greedy | 3 | image | 5 | 3 | 0.725 | 0.731 | [0.700, 0.753] | 0.722 | 0.740 |
| 7 | h8v2-scale-32 | greedy | 3 | image | 5 | 4 | 0.718 | 0.713 | [0.680, 0.737] | 0.826 | 0.627 |
| 8 | h10v2-pool_160_hp4hn4 | greedy | 3 | image | 5 | 4 | 0.718 | 0.717 | [0.690, 0.750] | 0.843 | 0.624 |
| 9 | h12v2-r2-balanced | greedy | 3 | image | 5 | 4 | 0.718 | 0.717 | [0.690, 0.750] | 0.843 | 0.624 |
| 10 | h10v2-pool_080_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.691 | 0.688 | [0.656, 0.719] | 0.666 | 0.712 |
| 11 | h10v2-pool_020_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.686 | 0.697 | [0.666, 0.726] | 0.671 | 0.724 |
| 12 | h8v2-canonical | greedy | 3 | image | 5 | 4 | 0.681 | 0.707 | [0.675, 0.737] | 0.791 | 0.639 |
| 13 | h10v2-pool_040_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.640 | 0.694 | [0.658, 0.723] | 0.669 | 0.721 |

## Tier 2 (MCC: 0.599–0.599)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 14 | h8v2-pure-positive-canon | greedy | 3 | image | 5 | 3 | 0.599 | 0.705 | [0.675, 0.737] | 0.657 | 0.762 |
