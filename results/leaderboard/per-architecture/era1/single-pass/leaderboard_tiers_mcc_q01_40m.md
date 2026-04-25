# Leaderboard (MCC tiers) — 40m buffer

**Generated**: 2026-04-25T13:29:49.629494+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 21 in 2 tier(s)

## Tier 1 (MCC: 0.147–0.281)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h5-track1-image-verbose | 1-pass | 1 | image | 1 | 1 | 0.281 | 0.710 | [0.669, 0.746] | 0.613 | 0.844 |
| 2 | h5-track1-image-terse | 1-pass | 1 | image | 1 | 1 | 0.223 | 0.695 | [0.654, 0.729] | 0.590 | 0.846 |
| 3 | h4-config-default | 1-pass | 1 | image | 1 | 1 | 0.214 | 0.713 | [0.674, 0.747] | 0.612 | 0.853 |
| 4 | h4-canonical-last | 1-pass | 1 | image | 1 | 1 | 0.212 | 0.718 | [0.676, 0.753] | 0.605 | 0.881 |
| 5 | h8-track1-image-exploratory-pure-positive-4hp | 1-pass | 1 | image | 1 | 1 | 0.162 | 0.699 | [0.654, 0.738] | 0.594 | 0.850 |
| 6 | h8-track1-image-scale-8 | 1-pass | 1 | image | 1 | 1 | 0.147 | 0.688 | [0.646, 0.722] | 0.584 | 0.835 |

## Tier 2 (MCC: 0.000–0.133)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 7 | h8-track1-image-scale-4 | 1-pass | 1 | image | 1 | 1 | 0.133 | 0.670 | [0.617, 0.718] | 0.557 | 0.839 |
| 8 | h4-canonical-first | 1-pass | 1 | image | 1 | 1 | 0.098 | 0.715 | [0.674, 0.749] | 0.607 | 0.868 |
| 9 | h8-track1-image-plus-hp | 1-pass | 1 | image | 1 | 1 | 0.098 | 0.715 | [0.674, 0.749] | 0.607 | 0.868 |
| 10 | h8-track1-image-canonical | 1-pass | 1 | image | 1 | 1 | 0.098 | 0.680 | [0.635, 0.719] | 0.594 | 0.794 |
| 11 | h8-track1-image-exploratory-pure-positive-canon | 1-pass | 1 | image | 1 | 1 | 0.097 | 0.680 | [0.637, 0.718] | 0.592 | 0.800 |
| 12 | h8-track1-image-pure-positive-canon | 1-pass | 1 | image | 1 | 1 | 0.097 | 0.676 | [0.631, 0.714] | 0.586 | 0.800 |
| 13 | h4-random | 1-pass | 1 | image | 1 | 1 | 0.084 | 0.673 | [0.626, 0.714] | 0.558 | 0.850 |
| 14 | h5-track2-text-verbose | 1-pass | 1 | text | 1 | 1 | 0.081 | 0.655 | [0.600, 0.704] | 0.549 | 0.813 |
| 15 | h5-track2-text-terse | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.644 | [0.585, 0.698] | 0.522 | 0.840 |
| 16 | h8-track1-image-exploratory-pure-positive-2hp | 1-pass | 1 | image | 1 | 1 | 0.000 | 0.665 | [0.613, 0.710] | 0.550 | 0.840 |
| 17 | h8-track2-text-canonical | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.646 | [0.587, 0.698] | 0.517 | 0.861 |
| 18 | h8-track2-text-plus-hp | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.649 | [0.595, 0.698] | 0.522 | 0.857 |
| 19 | h8-track2-text-pure-positive-canon | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.651 | [0.596, 0.701] | 0.523 | 0.861 |
| 20 | h8-track2-text-scale-4 | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.649 | [0.594, 0.698] | 0.523 | 0.855 |
| 21 | h8-track2-text-scale-8 | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.652 | [0.596, 0.701] | 0.525 | 0.859 |
