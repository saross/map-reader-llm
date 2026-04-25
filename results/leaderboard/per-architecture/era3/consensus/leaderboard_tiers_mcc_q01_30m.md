# Leaderboard (MCC tiers) — 30m buffer

**Generated**: 2026-04-25T14:40:52.302188+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 14 in 2 tier(s)

## Tier 1 (MCC: 0.640–0.772)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h8v2-scale-4 | greedy | 3 | image | 5 | 4 | 0.772 | 0.799 | [0.751, 0.842] | 0.895 | 0.721 |
| 2 | h8v2-scale-8 | greedy | 3 | image | 5 | 3 | 0.739 | 0.792 | [0.751, 0.831] | 0.795 | 0.790 |
| 3 | h12v2-r3-hp-heavy | greedy | 3 | image | 5 | 3 | 0.733 | 0.788 | [0.746, 0.828] | 0.779 | 0.796 |
| 4 | h8v2-plus-hp | greedy | 3 | image | 5 | 4 | 0.732 | 0.775 | [0.728, 0.822] | 0.874 | 0.696 |
| 5 | h8v2-scale-16 | greedy | 3 | image | 5 | 3 | 0.726 | 0.764 | [0.716, 0.810] | 0.748 | 0.781 |
| 6 | h12v2-r1-hn-heavy | greedy | 3 | image | 5 | 3 | 0.725 | 0.805 | [0.765, 0.845] | 0.795 | 0.815 |
| 7 | h8v2-scale-32 | greedy | 3 | image | 5 | 4 | 0.718 | 0.734 | [0.685, 0.781] | 0.851 | 0.646 |
| 8 | h10v2-pool_160_hp4hn4 | greedy | 3 | image | 5 | 4 | 0.718 | 0.760 | [0.711, 0.807] | 0.894 | 0.661 |
| 9 | h12v2-r2-balanced | greedy | 3 | image | 5 | 4 | 0.718 | 0.760 | [0.711, 0.807] | 0.894 | 0.661 |
| 10 | h10v2-pool_080_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.691 | 0.758 | [0.707, 0.805] | 0.733 | 0.784 |
| 11 | h10v2-pool_020_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.686 | 0.757 | [0.709, 0.807] | 0.730 | 0.787 |
| 12 | h8v2-canonical | greedy | 3 | image | 5 | 4 | 0.680 | 0.759 | [0.702, 0.815] | 0.849 | 0.686 |
| 13 | h10v2-pool_040_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.640 | 0.769 | [0.723, 0.810] | 0.741 | 0.799 |

## Tier 2 (MCC: 0.599–0.599)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 14 | h8v2-pure-positive-canon | greedy | 3 | image | 5 | 3 | 0.599 | 0.755 | [0.701, 0.800] | 0.703 | 0.815 |
