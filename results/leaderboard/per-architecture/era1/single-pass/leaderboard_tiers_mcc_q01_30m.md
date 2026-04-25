# Leaderboard (MCC tiers) — 30m buffer

**Generated**: 2026-04-25T13:29:49.629372+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 21 in 2 tier(s)

## Tier 1 (MCC: 0.147–0.281)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | h5-track1-image-verbose | 1-pass | 1 | image | 1 | 1 | 0.281 | 0.668 | [0.623, 0.711] | 0.577 | 0.794 |
| 2 | h5-track1-image-terse | 1-pass | 1 | image | 1 | 1 | 0.223 | 0.649 | [0.607, 0.691] | 0.551 | 0.790 |
| 3 | h4-config-default | 1-pass | 1 | image | 1 | 1 | 0.214 | 0.671 | [0.630, 0.709] | 0.576 | 0.803 |
| 4 | h4-canonical-last | 1-pass | 1 | image | 1 | 1 | 0.212 | 0.686 | [0.640, 0.725] | 0.578 | 0.842 |
| 5 | h8-track1-image-exploratory-pure-positive-4hp | 1-pass | 1 | image | 1 | 1 | 0.162 | 0.656 | [0.612, 0.699] | 0.558 | 0.798 |
| 6 | h8-track1-image-scale-8 | 1-pass | 1 | image | 1 | 1 | 0.147 | 0.655 | [0.613, 0.695] | 0.557 | 0.796 |

## Tier 2 (MCC: 0.000–0.133)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 7 | h8-track1-image-scale-4 | 1-pass | 1 | image | 1 | 1 | 0.133 | 0.637 | [0.585, 0.683] | 0.530 | 0.798 |
| 8 | h4-canonical-first | 1-pass | 1 | image | 1 | 1 | 0.098 | 0.664 | [0.617, 0.706] | 0.564 | 0.807 |
| 9 | h8-track1-image-plus-hp | 1-pass | 1 | image | 1 | 1 | 0.098 | 0.664 | [0.617, 0.706] | 0.564 | 0.807 |
| 10 | h8-track1-image-canonical | 1-pass | 1 | image | 1 | 1 | 0.098 | 0.653 | [0.609, 0.693] | 0.571 | 0.762 |
| 11 | h8-track1-image-exploratory-pure-positive-canon | 1-pass | 1 | image | 1 | 1 | 0.097 | 0.649 | [0.601, 0.689] | 0.565 | 0.762 |
| 12 | h8-track1-image-pure-positive-canon | 1-pass | 1 | image | 1 | 1 | 0.097 | 0.646 | [0.599, 0.687] | 0.560 | 0.764 |
| 13 | h4-random | 1-pass | 1 | image | 1 | 1 | 0.084 | 0.644 | [0.595, 0.688] | 0.533 | 0.813 |
| 14 | h5-track2-text-verbose | 1-pass | 1 | text | 1 | 1 | 0.081 | 0.630 | [0.573, 0.680] | 0.528 | 0.781 |
| 15 | h5-track2-text-terse | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.627 | [0.566, 0.680] | 0.508 | 0.818 |
| 16 | h8-track1-image-exploratory-pure-positive-2hp | 1-pass | 1 | image | 1 | 1 | 0.000 | 0.631 | [0.579, 0.676] | 0.522 | 0.798 |
| 17 | h8-track2-text-canonical | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.636 | [0.578, 0.688] | 0.509 | 0.848 |
| 18 | h8-track2-text-plus-hp | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.638 | [0.582, 0.686] | 0.513 | 0.842 |
| 19 | h8-track2-text-pure-positive-canon | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.641 | [0.587, 0.690] | 0.515 | 0.848 |
| 20 | h8-track2-text-scale-4 | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.640 | [0.586, 0.689] | 0.516 | 0.844 |
| 21 | h8-track2-text-scale-8 | 1-pass | 1 | text | 1 | 1 | 0.000 | 0.645 | [0.590, 0.694] | 0.520 | 0.850 |
