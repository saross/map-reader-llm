# Leaderboard (MCC tiers) — 20m buffer

**Generated**: 2026-05-06T09:33:40.953335+00:00
**Tiering metric**: MCC
**FDR q**: 0.05
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 8 in 2 tier(s)

## Tier 1 (MCC: 0.388–0.432)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | pv-cascade-adversarial-checklist | 1-pass+PV | 2 | text | 1 | 1 | 0.432 | 0.504 | [0.446, 0.549] | 0.667 | 0.405 |
| 2 | pv-adversarial-text | 1-pass+PV | 2 | text | 1 | 1 | 0.432 | 0.471 | [0.408, 0.517] | 0.712 | 0.352 |
| 3 | pv-adversarial-image | 1-pass+PV | 2 | image | 1 | 1 | 0.416 | 0.494 | [0.434, 0.539] | 0.659 | 0.395 |
| 4 | pv-cascade-checklist-adversarial | 1-pass+PV | 2 | text | 1 | 1 | 0.413 | 0.495 | [0.435, 0.540] | 0.661 | 0.395 |
| 5 | pv-brief-text | 1-pass+PV | 2 | text | 1 | 1 | 0.397 | 0.514 | [0.456, 0.560] | 0.673 | 0.416 |
| 6 | pv-checklist-image | 1-pass+PV | 2 | image | 1 | 1 | 0.388 | 0.531 | [0.473, 0.580] | 0.620 | 0.464 |

## Tier 2 (MCC: 0.315–0.341)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 7 | pv-brief-image | 1-pass+PV | 2 | image | 1 | 1 | 0.341 | 0.520 | [0.463, 0.569] | 0.607 | 0.455 |
| 8 | pv-checklist-text | 1-pass+PV | 2 | text | 1 | 1 | 0.315 | 0.521 | [0.463, 0.569] | 0.598 | 0.462 |
