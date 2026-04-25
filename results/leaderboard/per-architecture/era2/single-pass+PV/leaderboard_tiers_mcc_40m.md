# Leaderboard (MCC tiers) — 40m buffer

**Generated**: 2026-04-25T14:31:11.206768+00:00
**Tiering metric**: MCC
**FDR q**: 0.05
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 8 in 2 tier(s)

## Tier 1 (MCC: 0.388–0.432)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | pv-cascade-adversarial-checklist | 1-pass+PV | 2 | text | 1 | 1 | 0.432 | 0.518 | [0.434, 0.586] | 0.686 | 0.416 |
| 2 | pv-adversarial-text | 1-pass+PV | 2 | text | 1 | 1 | 0.431 | 0.480 | [0.396, 0.556] | 0.726 | 0.359 |
| 3 | pv-adversarial-image | 1-pass+PV | 2 | image | 1 | 1 | 0.416 | 0.509 | [0.426, 0.577] | 0.678 | 0.407 |
| 4 | pv-cascade-checklist-adversarial | 1-pass+PV | 2 | text | 1 | 1 | 0.412 | 0.509 | [0.426, 0.578] | 0.681 | 0.407 |
| 5 | pv-brief-text | 1-pass+PV | 2 | text | 1 | 1 | 0.396 | 0.526 | [0.444, 0.593] | 0.688 | 0.425 |
| 6 | pv-checklist-image | 1-pass+PV | 2 | image | 1 | 1 | 0.388 | 0.544 | [0.458, 0.609] | 0.635 | 0.476 |

## Tier 2 (MCC: 0.315–0.340)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 7 | pv-brief-image | 1-pass+PV | 2 | image | 1 | 1 | 0.340 | 0.533 | [0.450, 0.602] | 0.623 | 0.467 |
| 8 | pv-checklist-text | 1-pass+PV | 2 | text | 1 | 1 | 0.315 | 0.534 | [0.450, 0.600] | 0.613 | 0.474 |
