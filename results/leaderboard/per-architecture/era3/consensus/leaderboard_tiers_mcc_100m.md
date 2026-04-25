# Leaderboard (MCC tiers) — 100m buffer

**Generated**: 2026-04-25T14:40:51.876253+00:00
**Tiering metric**: MCC
**FDR q**: 0.05
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 14 in 2 tier(s)

## Tier 1 (MCC: 0.680–0.772)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h8v2-scale-4 | greedy | 3 | image | 5 | 4 | 0.772 | 0.823 | [0.782, 0.863] | 0.922 | 0.743 |
| 2 | h8v2-scale-8 | greedy | 3 | image | 5 | 3 | 0.739 | 0.827 | [0.789, 0.863] | 0.830 | 0.825 |
| 3 | h12v2-r3-hp-heavy | greedy | 3 | image | 5 | 3 | 0.733 | 0.834 | [0.798, 0.871] | 0.825 | 0.843 |
| 4 | h8v2-plus-hp | greedy | 3 | image | 5 | 4 | 0.732 | 0.796 | [0.753, 0.838] | 0.898 | 0.715 |
| 5 | h8v2-scale-16 | greedy | 3 | image | 5 | 3 | 0.726 | 0.819 | [0.772, 0.857] | 0.802 | 0.837 |
| 6 | h12v2-r1-hn-heavy | greedy | 3 | image | 5 | 3 | 0.725 | 0.842 | [0.808, 0.874] | 0.832 | 0.853 |
| 7 | h8v2-scale-32 | greedy | 3 | image | 5 | 4 | 0.718 | 0.763 | [0.714, 0.808] | 0.884 | 0.671 |
| 8 | h10v2-pool_160_hp4hn4 | greedy | 3 | image | 5 | 4 | 0.718 | 0.793 | [0.746, 0.835] | 0.932 | 0.690 |
| 9 | h12v2-r2-balanced | greedy | 3 | image | 5 | 4 | 0.718 | 0.793 | [0.746, 0.835] | 0.932 | 0.690 |
| 10 | h10v2-pool_080_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.691 | 0.809 | [0.765, 0.851] | 0.783 | 0.837 |
| 11 | h10v2-pool_020_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.686 | 0.811 | [0.770, 0.851] | 0.782 | 0.843 |
| 12 | h8v2-canonical | greedy | 3 | image | 5 | 4 | 0.680 | 0.780 | [0.727, 0.831] | 0.872 | 0.705 |

## Tier 2 (MCC: 0.599–0.640)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 13 | h10v2-pool_040_hp4hn4 | greedy | 3 | image | 5 | 3 | 0.640 | 0.799 | [0.762, 0.836] | 0.770 | 0.831 |
| 14 | h8v2-pure-positive-canon | greedy | 3 | image | 5 | 3 | 0.599 | 0.798 | [0.753, 0.837] | 0.743 | 0.862 |
