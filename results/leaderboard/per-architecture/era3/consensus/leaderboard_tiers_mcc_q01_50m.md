# Leaderboard (MCC tiers) — 50m buffer

**Generated**: 2026-04-25T14:40:52.302368+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 14 in 2 tier(s)

## Tier 1 (MCC: 0.640–0.772)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h8v2-scale-4 | greedy | 3 | image | 5 | 4 | 0.772 | 0.816 | [0.773, 0.856] | 0.914 | 0.737 |
| 2 | h8v2-scale-8 | greedy | 3 | image | 5 | 3 | 0.739 | 0.815 | [0.777, 0.850] | 0.817 | 0.812 |
| 3 | h12v2-r3-hp-heavy | greedy | 3 | image | 5 | 3 | 0.733 | 0.819 | [0.779, 0.857] | 0.810 | 0.828 |
| 4 | h8v2-plus-hp | greedy | 3 | image | 5 | 4 | 0.732 | 0.789 | [0.745, 0.831] | 0.890 | 0.709 |
| 5 | h8v2-scale-16 | greedy | 3 | image | 5 | 3 | 0.726 | 0.807 | [0.763, 0.846] | 0.790 | 0.825 |
| 6 | h12v2-r1-hn-heavy | greedy | 3 | image | 5 | 3 | 0.725 | 0.833 | [0.799, 0.866] | 0.823 | 0.843 |
| 7 | h8v2-scale-32 | greedy | 3 | image | 5 | 4 | 0.718 | 0.759 | [0.712, 0.804] | 0.880 | 0.668 |
| 8 | h10v2-pool_160_hp4hn4 | greedy | 3 | image | 5 | 4 | 0.718 | 0.786 | [0.738, 0.830] | 0.924 | 0.683 |
| 9 | h12v2-r2-balanced | greedy | 3 | image | 5 | 4 | 0.718 | 0.786 | [0.738, 0.830] | 0.924 | 0.683 |
| 10 | h10v2-pool_080_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.691 | 0.794 | [0.747, 0.839] | 0.768 | 0.821 |
| 11 | h10v2-pool_020_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.686 | 0.796 | [0.756, 0.839] | 0.767 | 0.828 |
| 12 | h8v2-canonical | greedy | 3 | image | 5 | 4 | 0.680 | 0.780 | [0.727, 0.831] | 0.872 | 0.705 |
| 13 | h10v2-pool_040_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.640 | 0.793 | [0.754, 0.830] | 0.764 | 0.825 |

## Tier 2 (MCC: 0.599–0.599)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 14 | h8v2-pure-positive-canon | greedy | 3 | image | 5 | 3 | 0.599 | 0.787 | [0.740, 0.827] | 0.732 | 0.850 |
