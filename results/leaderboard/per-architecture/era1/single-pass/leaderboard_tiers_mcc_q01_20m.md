# Leaderboard (MCC tiers) — 20m buffer

**Generated**: 2026-05-06T02:55:40.159195+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 21 in 2 tier(s)

## Tier 1 (MCC: 0.149–0.282)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h5-track1-image-verbose | 1-pass | 1 | image | 1 | 1 | 0.282 | 0.603 | [0.573, 0.630] | 0.520 | 0.716 |
| 2 | h5-track1-image-terse | 1-pass | 1 | image | 1 | 1 | 0.224 | 0.605 | [0.581, 0.631] | 0.514 | 0.737 |
| 3 | h4-config-default | 1-pass | 1 | image | 1 | 1 | 0.216 | 0.606 | [0.576, 0.628] | 0.520 | 0.725 |
| 4 | h4-canonical-last | 1-pass | 1 | image | 1 | 1 | 0.214 | 0.631 | [0.609, 0.657] | 0.532 | 0.775 |
| 5 | h8-track1-image-exploratory-pure-positive-4hp | 1-pass | 1 | image | 1 | 1 | 0.164 | 0.599 | [0.574, 0.625] | 0.508 | 0.727 |
| 6 | h8-track1-image-scale-8 | 1-pass | 1 | image | 1 | 1 | 0.149 | 0.587 | [0.562, 0.612] | 0.499 | 0.712 |

## Tier 2 (MCC: 0.000–0.134)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 7 | h8-track1-image-scale-4 | 1-pass | 1 | image | 1 | 1 | 0.134 | 0.584 | [0.554, 0.609] | 0.486 | 0.731 |
| 8 | h4-canonical-first | 1-pass | 1 | image | 1 | 1 | 0.093 | 0.599 | [0.572, 0.627] | 0.508 | 0.727 |
| 9 | h8-track1-image-plus-hp | 1-pass | 1 | image | 1 | 1 | 0.093 | 0.599 | [0.572, 0.627] | 0.508 | 0.727 |
| 10 | h8-track1-image-canonical | 1-pass | 1 | image | 1 | 1 | 0.092 | 0.581 | [0.555, 0.610] | 0.508 | 0.679 |
| 11 | h8-track1-image-exploratory-pure-positive-canon | 1-pass | 1 | image | 1 | 1 | 0.091 | 0.570 | [0.541, 0.601] | 0.496 | 0.670 |
| 12 | h8-track1-image-pure-positive-canon | 1-pass | 1 | image | 1 | 1 | 0.091 | 0.568 | [0.542, 0.599] | 0.492 | 0.672 |
| 13 | h4-random | 1-pass | 1 | image | 1 | 1 | 0.065 | 0.571 | [0.539, 0.601] | 0.473 | 0.720 |
| 14 | h5-track2-text-verbose | 1-pass | 1 | text | 1 | 1 | 0.062 | 0.583 | [0.549, 0.616] | 0.489 | 0.724 |
| 15 | h5-track2-text-terse | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.598 | [0.570, 0.634] | 0.485 | 0.781 |
| 16 | h8-track1-image-exploratory-pure-positive-2hp | 1-pass | 1 | image | 1 | 1 | 0.000 | 0.571 | [0.543, 0.603] | 0.473 | 0.722 |
| 17 | h8-track2-text-canonical | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.605 | [0.569, 0.633] | 0.484 | 0.805 |
| 18 | h8-track2-text-plus-hp | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.597 | [0.565, 0.630] | 0.480 | 0.788 |
| 19 | h8-track2-text-pure-positive-canon | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.605 | [0.572, 0.636] | 0.486 | 0.800 |
| 20 | h8-track2-text-scale-4 | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.609 | [0.577, 0.641] | 0.491 | 0.803 |
| 21 | h8-track2-text-scale-8 | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.607 | [0.574, 0.638] | 0.489 | 0.800 |
