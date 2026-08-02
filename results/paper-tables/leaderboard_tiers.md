# Leaderboard Tier Clustering (30m buffer, FDR-corrected)

> **⚠ Superseded figures (2026-08-02, E72)**: the rows `FM text T=1.0 5/5`
> (Tier 8), `FM text T=1.0 22/30` and `FM text T=1.0 9/10` (Tier 9) derive from
> `outputs/h11/consensus-384-UNINTENDED-T1.0`, a 240-tile study scored against
> 487-tile bounds (coverage confound — see protocol-errata E43 correction block
> and E72), and understate that arm by ~0.17–0.19 F1. With those three cells
> dropped the board has 22 conditions, 231 pairwise tests, 181 significant
> after BH, and **8 tiers**; Tier 9 disappears and no retained condition
> changes tier. The companion `leaderboard_tiers.csv` carries the same
> superseded rows. Regenerated board: `results/e43-board-regen/`.
> Matched-scope analysis: `results/e43-matched-temperature/`. Dated snapshot;
> body unchanged; do not cite the affected rows.

Conditions within the same tier are statistically indistinguishable
(all pairwise adjusted p-values ≥ 0.05).

**Scope unification note (2026-04-24)**: this document uses phase3a
condition labels and is not a mirror of
`results/leaderboard/era2/leaderboard_tiers_30m.md`, which uses the
h11-series cell naming. The Session 78 gold-standard-v2 scope-unified
cell at Era 2 (487-tile) scope reports F1=0.871 at 30 m
(`results/leaderboard/cells/gold-standard-v2-greedy-v1-487tile.json`).
It would sit in Tier 2 here on F1 but is not inserted as a distinct row
because the tier discussion focuses on phase3a matrix conditions with
matched pairwise permutation statistics. The Era 3 (327-tile) scope-pair
sibling (`gold-standard-v2-greedy-v1-327tile.json`) is intentionally
preserved for comparability with the Era 3 h8-v2 / h10-v2 / h12-v2
library-design artefacts.

## Tier 1 (F1: 0.885–0.904)

| Condition | F1 |
|-----------|------|
| FH text 16/30 + PV | 0.904 |
| FH text 4/5 + PV | 0.891 |
| FH text 4/5 + med vf | 0.885 |

## Tier 2 (F1: 0.851–0.869)

| Condition | F1 |
|-----------|------|
| FH text 9/10 + PV | 0.869 |
| Pro text 3/5 + PV | 0.865 |
| Pro text 3/5 | 0.855 |
| FH image 3/5 + PV | 0.851 |

## Tier 3 (F1: 0.799–0.832)

| Condition | F1 |
|-----------|------|
| Text base + PV | 0.832 |
| FH text 26/30 | 0.826 |
| Pro image 3/5 | 0.821 |
| FH image 6/10 | 0.812 |
| FH text 9/10 | 0.811 |
| FH image 3/5 | 0.799 |

## Tier 4 (F1: 0.782–0.788)

| Condition | F1 |
|-----------|------|
| FH text 5/5 | 0.788 |
| Image base + PV | 0.782 |

## Tier 5 (F1: 0.724–0.733)

| Condition | F1 |
|-----------|------|
| FM image 6/10 | 0.733 |
| FM image 4/5 | 0.724 |

## Tier 6 (F1: 0.647–0.669)

| Condition | F1 |
|-----------|------|
| FM text T=0.7 29/30 | 0.669 |
| FM text T=0.7 5/5 | 0.647 |

## Tier 7 (F1: 0.641)

| Condition | F1 |
|-----------|------|
| FM text T=0.7 10/10 | 0.641 |

## Tier 8 (F1: 0.479–0.563)

| Condition | F1 |
|-----------|------|
| Single-pass 10/10 | 0.563 |
| Single-pass 5/5 | 0.554 |
| FM text T=1.0 5/5 | 0.479 |

## Tier 9 (F1: 0.469–0.477)

| Condition | F1 |
|-----------|------|
| FM text T=1.0 22/30 | 0.477 |
| FM text T=1.0 9/10 | 0.469 |
