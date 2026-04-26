# Leaderboard (MCC tiers) — 50m buffer

**Generated**: 2026-04-26T07:18:22.544947+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 8 in 2 tier(s)

## Tier 1 (MCC: 0.388–0.432)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | pv-cascade-adversarial-checklist | 1-pass+PV | 2 | text | 1 | 1 | 0.432 | 0.521 | [0.438, 0.589] | 0.689 | 0.418 |
| 2 | pv-adversarial-text | 1-pass+PV | 2 | text | 1 | 1 | 0.431 | 0.483 | [0.399, 0.558] | 0.730 | 0.361 |
| 3 | pv-adversarial-image | 1-pass+PV | 2 | image | 1 | 1 | 0.416 | 0.511 | [0.428, 0.580] | 0.682 | 0.409 |
| 4 | pv-cascade-checklist-adversarial | 1-pass+PV | 2 | text | 1 | 1 | 0.412 | 0.512 | [0.430, 0.580] | 0.685 | 0.409 |
| 5 | pv-brief-text | 1-pass+PV | 2 | text | 1 | 1 | 0.396 | 0.528 | [0.448, 0.596] | 0.691 | 0.428 |
| 6 | pv-checklist-image | 1-pass+PV | 2 | image | 1 | 1 | 0.388 | 0.547 | [0.460, 0.612] | 0.638 | 0.478 |

## Tier 2 (MCC: 0.315–0.340)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 7 | pv-brief-image | 1-pass+PV | 2 | image | 1 | 1 | 0.340 | 0.536 | [0.454, 0.605] | 0.626 | 0.469 |
| 8 | pv-checklist-text | 1-pass+PV | 2 | text | 1 | 1 | 0.315 | 0.537 | [0.453, 0.602] | 0.616 | 0.476 |
