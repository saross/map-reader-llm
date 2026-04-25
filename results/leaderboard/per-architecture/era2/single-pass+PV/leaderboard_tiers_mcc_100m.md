# Leaderboard (MCC tiers) — 100m buffer

**Generated**: 2026-04-25T14:31:11.206943+00:00
**Tiering metric**: MCC
**FDR q**: 0.05
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 8 in 2 tier(s)

## Tier 1 (MCC: 0.388–0.432)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | pv-cascade-adversarial-checklist | 1-pass+PV | 2 | text | 1 | 1 | 0.432 | 0.526 | [0.447, 0.593] | 0.697 | 0.423 |
| 2 | pv-adversarial-text | 1-pass+PV | 2 | text | 1 | 1 | 0.431 | 0.486 | [0.405, 0.559] | 0.735 | 0.363 |
| 3 | pv-adversarial-image | 1-pass+PV | 2 | image | 1 | 1 | 0.416 | 0.517 | [0.439, 0.583] | 0.690 | 0.414 |
| 4 | pv-cascade-checklist-adversarial | 1-pass+PV | 2 | text | 1 | 1 | 0.412 | 0.518 | [0.440, 0.585] | 0.692 | 0.414 |
| 5 | pv-brief-text | 1-pass+PV | 2 | text | 1 | 1 | 0.396 | 0.534 | [0.455, 0.599] | 0.699 | 0.432 |
| 6 | pv-checklist-image | 1-pass+PV | 2 | image | 1 | 1 | 0.388 | 0.552 | [0.468, 0.617] | 0.644 | 0.483 |

## Tier 2 (MCC: 0.315–0.340)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 7 | pv-brief-image | 1-pass+PV | 2 | image | 1 | 1 | 0.340 | 0.541 | [0.462, 0.610] | 0.632 | 0.474 |
| 8 | pv-checklist-text | 1-pass+PV | 2 | text | 1 | 1 | 0.315 | 0.542 | [0.460, 0.606] | 0.622 | 0.480 |
