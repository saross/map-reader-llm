# Leaderboard (MCC tiers) — 100m buffer

**Generated**: 2026-04-25T13:29:49.629718+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 21 in 2 tier(s)

## Tier 1 (MCC: 0.147–0.281)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h5-track1-image-verbose | 1-pass | 1 | image | 1 | 1 | 0.281 | 0.742 | [0.701, 0.775] | 0.640 | 0.881 |
| 2 | h5-track1-image-terse | 1-pass | 1 | image | 1 | 1 | 0.223 | 0.738 | [0.697, 0.772] | 0.626 | 0.898 |
| 3 | h4-config-default | 1-pass | 1 | image | 1 | 1 | 0.214 | 0.753 | [0.715, 0.785] | 0.646 | 0.902 |
| 4 | h4-canonical-last | 1-pass | 1 | image | 1 | 1 | 0.212 | 0.730 | [0.688, 0.762] | 0.615 | 0.896 |
| 5 | h8-track1-image-exploratory-pure-positive-4hp | 1-pass | 1 | image | 1 | 1 | 0.162 | 0.741 | [0.700, 0.774] | 0.629 | 0.900 |
| 6 | h8-track1-image-scale-8 | 1-pass | 1 | image | 1 | 1 | 0.147 | 0.727 | [0.686, 0.761] | 0.618 | 0.883 |

## Tier 2 (MCC: 0.000–0.133)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 7 | h8-track1-image-scale-4 | 1-pass | 1 | image | 1 | 1 | 0.133 | 0.705 | [0.650, 0.753] | 0.587 | 0.883 |
| 8 | h4-canonical-first | 1-pass | 1 | image | 1 | 1 | 0.098 | 0.739 | [0.698, 0.773] | 0.628 | 0.898 |
| 9 | h8-track1-image-plus-hp | 1-pass | 1 | image | 1 | 1 | 0.098 | 0.739 | [0.698, 0.773] | 0.628 | 0.898 |
| 10 | h8-track1-image-canonical | 1-pass | 1 | image | 1 | 1 | 0.098 | 0.709 | [0.664, 0.746] | 0.619 | 0.828 |
| 11 | h8-track1-image-exploratory-pure-positive-canon | 1-pass | 1 | image | 1 | 1 | 0.097 | 0.718 | [0.674, 0.754] | 0.625 | 0.844 |
| 12 | h8-track1-image-pure-positive-canon | 1-pass | 1 | image | 1 | 1 | 0.097 | 0.714 | [0.668, 0.750] | 0.618 | 0.844 |
| 13 | h4-random | 1-pass | 1 | image | 1 | 1 | 0.084 | 0.713 | [0.663, 0.752] | 0.591 | 0.900 |
| 14 | h5-track2-text-verbose | 1-pass | 1 | text | 1 | 1 | 0.081 | 0.681 | [0.628, 0.727] | 0.570 | 0.844 |
| 15 | h5-track2-text-terse | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.664 | [0.607, 0.716] | 0.538 | 0.866 |
| 16 | h8-track1-image-exploratory-pure-positive-2hp | 1-pass | 1 | image | 1 | 1 | 0.000 | 0.696 | [0.643, 0.739] | 0.576 | 0.879 |
| 17 | h8-track2-text-canonical | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.655 | [0.595, 0.705] | 0.524 | 0.872 |
| 18 | h8-track2-text-plus-hp | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.659 | [0.602, 0.707] | 0.530 | 0.870 |
| 19 | h8-track2-text-pure-positive-canon | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.659 | [0.604, 0.708] | 0.530 | 0.872 |
| 20 | h8-track2-text-scale-4 | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.661 | [0.607, 0.711] | 0.533 | 0.872 |
| 21 | h8-track2-text-scale-8 | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.662 | [0.606, 0.711] | 0.533 | 0.872 |
