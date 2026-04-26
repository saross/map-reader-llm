# Leaderboard (MCC tiers) — 30m buffer

**Generated**: 2026-04-26T07:18:22.544311+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 8 in 2 tier(s)

## Tier 1 (MCC: 0.388–0.432)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | pv-cascade-adversarial-checklist | 1-pass+PV | 2 | text | 1 | 1 | 0.432 | 0.515 | [0.433, 0.583] | 0.682 | 0.414 |
| 2 | pv-adversarial-text | 1-pass+PV | 2 | text | 1 | 1 | 0.431 | 0.477 | [0.393, 0.553] | 0.721 | 0.356 |
| 3 | pv-adversarial-image | 1-pass+PV | 2 | image | 1 | 1 | 0.416 | 0.506 | [0.423, 0.574] | 0.674 | 0.405 |
| 4 | pv-cascade-checklist-adversarial | 1-pass+PV | 2 | text | 1 | 1 | 0.412 | 0.506 | [0.424, 0.575] | 0.677 | 0.405 |
| 5 | pv-brief-text | 1-pass+PV | 2 | text | 1 | 1 | 0.396 | 0.523 | [0.440, 0.590] | 0.684 | 0.423 |
| 6 | pv-checklist-image | 1-pass+PV | 2 | image | 1 | 1 | 0.388 | 0.541 | [0.455, 0.607] | 0.632 | 0.474 |

## Tier 2 (MCC: 0.315–0.340)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 7 | pv-brief-image | 1-pass+PV | 2 | image | 1 | 1 | 0.340 | 0.531 | [0.449, 0.599] | 0.620 | 0.464 |
| 8 | pv-checklist-text | 1-pass+PV | 2 | text | 1 | 1 | 0.315 | 0.532 | [0.447, 0.599] | 0.610 | 0.471 |
