# Era-2 board: tile-MCC tiering under three tile joins

> **Last revised**: 2026-10-30 (original publication). See [§ Changelog](#changelog) for revision history.

A **sensitivity reading** of the gold-standard (GS) Era-2 verified board's tile-level Matthews Correlation Coefficient (MCC) family (`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/`). The board publishes its MCC permutation family and its MCC Multiple Comparisons with the Best (MCB) admissible set under the name-based `id` tile join, the published convention (S153 ruling 6). Here both are rebuilt under that join (the reproduction gate) and under the two geometric joins of `reports/tile-mcc-geometric-join-2026-09-12.md` § 2. Only the MCC arm changes: the F1 tiering, its tiers and its three withheld cells are the board's own in all three runs. Nothing in the board, the register or any findings document was written.

Instruments: `scripts/era1_leaderboard_tiering.py --permute-mcc [--tile-join JOIN]` (10,000 tile-swap draws, seed 42, BH q = 0.05 per family, greedy clique) and `scripts/selection_aware_intervals.py --board --metric mcc [--tile-join JOIN] --bootstrap 10000 --m-frac 1.0` (admissible set: hsu_not_ruled_out, Hsu's constrained one-sided form). Membership: `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering-input/run-analyses.json` (150 tiered cells, 487 tiles). Computed at commit `792d459ea` on sapphire. Machine-readable record: `summary.json`; each geometric join's MCC family: `mcc-family-<join>.json`; its MCC MCB: `mcb/`.

## 1. Reproduction gate (`id` join)

| Quantity | Committed | This run | Equal |
|---|---:|---:|:---:|
| F1 pairs significant | 8075 of 11175 | 8075 of 11175 | yes |
| F1 tiers | 14 | 14 | yes |
| F1 Tier 1 (the same five cells, same order) | 5 | 5 | yes |
| MCC pairs significant | 3001 of 11175 | 3001 of 11175 | yes |
| MCC tiers | 6 | 6 | yes |
| MCC Tier 1 | 34 | 34 | yes |
| whole `mcc_permutation` block | — | — | yes |
| tiering JSON keys differing beyond `generated_at_utc`, `git_commit` | — | 0 | yes |
| F1 MCB admissible set | 52 | 52 | yes |
| MCC MCB admissible set | 60 | 60 | yes |
| F1 MCB artefact byte-identical | — | — | yes |
| MCC MCB artefact byte-identical | — | — | yes |
| join-aware MCB builder under `id` = default derivation | — | — | yes |

**Gate: PASSED.**

## 2. Per-join MCC family

| | `id` | `geometric-primary` | `geometric-contains` |
|---|---:|---:|---:|
| MCC pairs significant (BH q 0.05, of 11,175) | 3001 | 2013 | 1856 |
| MCC tiers | 6 | 5 | 5 |
| MCC Tier 1 (tie set) size | 34 | 64 | 42 |
| MCC MCB admissible (Hsu), of 150 | 60 | 125 | 115 |
| top MCC cell | `verified-adv-image-baseline-pro-vf-era2b` | `g37-image-k5-verified-swap37-p0.90-k5-era2b` | `g37-image-k5-verified-swap37-p0.90-k5-era2b` |
| — its tile-MCC | 0.8887 | 0.9617 | 0.9423 |
| — its track; F1 tier | image; 9 | image; 1 | image; 1 |
| Spearman of MCC vs `id`, 150 cells | 1.0000 | 0.7896 | 0.7231 |
| Spearman of MCC vs `id`, the 103 `cells/` cells | 1.0000 | 0.8396 | 0.7666 |
| mean ΔMCC vs `id` (min … max) | +0.0000 (+0.0000 … +0.0000) | +0.1067 (+0.0478 … +0.1472) | +0.0763 (-0.0011 … +0.1190) |
| cells higher / lower than under `id` | 0 / 0 | 150 / 0 | 149 / 1 |
| MCC MCB argmax stability (distinct winners) | 0.4192 (39) | 0.5227 (70) | 0.6189 (48) |

The 2026-09-12 audit's own Spearman figures, recomputed from `results/tile-join-audit/board-era2-2026-09-12.json` (103 cells, before the S164 restatement): `geometric-primary` 0.8467, `geometric-contains` 0.7736.

## 3. Claim checks

| Claim | `id` | `geometric-primary` | `geometric-contains` |
|---|---:|---:|---:|
| (i) top F1 cell in MCC Tier 1 | yes | yes | yes |
| — its MCC rank / MCC tier | 21 / 1 | 1 / 1 | 1 / 1 |
| — MCC-admissible | yes | yes | yes |
| (ii) F1 Tier-1 cells in MCC Tier 1, of 5 | 1 | 4 | 4 |
| — their MCC ranks | 21, 62, 46, 37, 102 | 1, 27, 6, 3, 94 | 1, 15, 5, 4, 93 |
| (iii) F1-admissible ∩ MCC-admissible | 9 of 52 and 60 | 50 of 52 and 125 | 45 of 52 and 115 |
| — union / F1-only / MCC-only | 103 / 43 / 51 | 127 / 2 / 75 | 122 / 7 / 70 |
| — top MCC cell F1-admissible | no | yes | yes |
| (iv) top MCC cell's track | image | image | image |
| — image cells in the MCC top 10 | 10 | 6 | 5 |
| — MCC Tier 1 image / text | 31 / 3 | 37 / 27 | 28 / 14 |
| — MCC-admissible image / text | 46 / 14 | 55 / 70 | 55 / 60 |
| — median MCC rank, image / text | 33 / 100 | 51 / 95 | 47 / 97 |
| (v) register's MCC leader is the top MCC cell | yes | no | no |
| — its MCC, rank, MCC tier | 0.8887, 1, 1 | 0.9365, 10, 1 | 0.8942, 30, 1 |
| — in MCC Tier 1 / MCC-admissible | yes / yes | yes / yes | yes / yes |

The top F1 cell is `g37-image-k5-verified-swap37-p0.90-k5-era2b`; the register's MCC leader (row `gs-era2-verified-board-2026-09-10`, `outcome`) is `verified-adv-image-baseline-pro-vf-era2b`. Board composition by proposer track: 59 image, 91 text (derivation in `summary.json` → `track_derivation`).

## 4. MCC Tier 1 under each join

**`id`** (34 cells): `verified-adv-image-baseline-pro-vf-era2b`, `verified-adv-image-baseline-medium-vf-era2b`, `verified-adv-image-baseline-era2b`, `pv-scale4-optimal-n1-opmax`, `pv-high-image-t1.0-n1-opmax`, `pv-high-image-t1.0-n1-carried-p0.15-k1`, `pv-scale4-optimal-n1-carried-p0.15-k1`, `verified-adv-pro-image-pro-vf-3of5-era2b`, `pv-min-image-t0.3-n1-carried-p0.15-k1`, `verified-adv-image-min-3of5-era2b`, `pv-min-image-t0.3-n1-opmax`, `pv-scale4-optimal-n3-opmax`, `pv-min-image-t0.7-n1-opmax`, `pv-high-image-t0.7-n1-opmax`, `pv-high-image-t0.7-n3-opmax`, `pv-min-image-t0.3-n5-opmax`, `pv-n1-image-t0-n3-opmax`, `pv-min-image-t0.7-n5-opmax`, `pv-min-image-t0.7-n3-opmax`, `pv-min-image-t0.3-n10-opmax`, `g37-image-k5-verified-swap37-p0.90-k5-era2b`, `verified-adv-text-baseline-medium-vf-era2b`, `pv-min-image-t1.0-n1-opmax`, `pv-high-image-t0.7-n5-opmax`, `verified-adv-pro-image-baseline-medium-vf-era2b`, `verified-adv-pro-image-baseline-pro-vf-era2b`, `verified-adv-text-baseline-era2b`, `verified-adv-text-baseline-pro-vf-era2b`, `session-78-image-adversarial-opmax`, `session-78-image-comparative-opmax`, `pv-scale4-optimal-n5-opmax`, `session-78-image-brief-opmax`, `pv-high-image-t1.0-n3-opmax`, `pv-high-image-t0.3-n10-opmax`.

**`geometric-primary`** (64 cells): `g37-image-k5-verified-swap37-p0.90-k5-era2b`, `verified-adv-pro-image-pro-vf-3of5-era2b`, `g37-image-k5-verified-carried-p0.10-k5-era2b`, `pv-min-image-t0.7-n5-opmax`, `g384-ov192-k10-verified37-p0.98-k10-era2b`, `g37-text-k5-verified-swap38-p0.88-k5-era2b`, `pv-high-text-t1.0-n3-opmax`, `pv-high-image-t0.7-n5-opmax`, `g384-ov192-k3-verified-opmax`, `verified-adv-image-baseline-pro-vf-era2b`, `pv-min-image-t0.7-n3-opmax`, `verified-adv-image-min-3of5-era2b`, `session-78-image-adversarial-opmax`, `verified-adv-image-baseline-era2b`, `verified-adv-image-baseline-medium-vf-era2b`, `g384-ov192-k1-verified-opmax`, `pv-high-image-t0.3-n10-opmax`, `g384-ov192-k5-verified-opmax`, `pv-n1-image-t0-n3-opmax`, `verified-384-16of30-t0-3-n5-opmax-era2b`, `pv-high-image-t0.7-n3-opmax`, `pv-min-image-t0.3-n1-opmax`, `pv-scale4-optimal-n1-opmax`, `verified-adv-text-baseline-medium-vf-era2b`, `verified-adv-text-baseline-pro-vf-era2b`, `session-78-image-brief-opmax`, `g37-text-k5-verified-swap37-p0.80-k5-era2b`, `verified-adv-image-3of5-era2b`, `pv-high-text-t0.3-n5-opmax`, `pv-min-image-t1.0-n10-opmax`, `pv-min-image-t0.7-n1-opmax`, `pv-high-text-t0.7-n3-opmax`, `pv-high-text-t1.0-n10-opmax`, `session-78-image-checklist-text-opmax`, `session-78-text-comparative-opmax`, `verified-adv-text-6of10-era2b`, `pv-scale4-optimal-n3-opmax`, `pv-min-text-t1.0-n10-opmax`, `session-78-image-comparative-opmax`, `g384-ov192-image-min-k10-verified-p0.15-k9-era2b`, `verified-adv-image-min-6of10-era2b`, `pv-min-text-t1.0-n3-opmax`, `session-78-image-brief-text-opmax`, `pv-scale4-optimal-n10-opmax`, `pv-min-image-t0.3-n1-carried-p0.15-k1`, `g384-ov192-k1-verified-p0.15-k1`, `pv-min-image-t1.0-n1-opmax`, `pv-high-text-t1.0-n5-opmax`, `verified-adv-text-pro-vf-4of5-era2b`, `pv-min-text-t0.3-n10-opmax`, `g384-ov192-image-high-k10-verified-p0.20-k8-era2b`, `verified-adv-text-consensus-16of30-era2b`, `pv-min-text-t0.3-n1-opmax`, `pv-min-text-t0.3-n3-opmax`, `session-78-text-adversarial-opmax`, `pv-high-text-t0.3-n10-opmax`, `pv-scale4-optimal-n5-opmax`, `pv-high-image-t0.7-n1-opmax`, `pv-high-image-t0.3-n3-opmax`, `pv-scale4-optimal-n1-carried-p0.15-k1`, `pv-high-text-t0.3-n3-opmax`, `pv-min-image-t0.7-n3-carried-p0.15-k3`, `session-78-image-checklist-opmax`, `pv-high-image-t0.7-n10-opmax`.

**`geometric-contains`** (42 cells): `g37-image-k5-verified-swap37-p0.90-k5-era2b`, `verified-adv-pro-image-pro-vf-3of5-era2b`, `g384-ov192-k10-verified37-p0.98-k10-era2b`, `g37-image-k5-verified-carried-p0.10-k5-era2b`, `g37-text-k5-verified-swap38-p0.88-k5-era2b`, `verified-adv-text-pro-vf-4of5-era2b`, `pv-high-image-t0.7-n5-opmax`, `session-78-text-adversarial-opmax`, `g384-ov192-image-min-k10-verified-p0.15-k9-era2b`, `g384-ov192-k3-verified-opmax`, `pv-scale4-optimal-n1-opmax`, `pv-high-text-t0.7-n3-opmax`, `pv-high-text-t0.3-n3-opmax`, `session-78-text-comparative-opmax`, `g37-text-k5-verified-swap37-p0.80-k5-era2b`, `pv-min-image-t0.3-n10-opmax`, `session-78-image-adversarial-opmax`, `verified-384-ge3of5-t0-7-high-n5-era2b`, `session-78-image-brief-text-opmax`, `pv-high-image-t0.3-n10-opmax`, `verified-adv-image-min-3of5-era2b`, `pv-high-text-t0.3-n10-opmax`, `pv-high-image-t0.7-n10-opmax`, `session-78-image-checklist-text-opmax`, `session-78-image-brief-opmax`, `pv-min-image-t0.7-n5-opmax`, `session-78-image-comparative-opmax`, `verified-384-ge3of5-t0-3-high-n5-era2b`, `pv-min-image-t0.3-n1-carried-p0.15-k1`, `verified-adv-image-baseline-pro-vf-era2b`, `pv-min-image-t0.3-n1-opmax`, `g384-ov192-k1-verified-opmax`, `pv-min-image-t0.7-n3-opmax`, `pv-min-image-t0.3-n5-opmax`, `g384-ov192-k5-verified-opmax`, `verified-adv-image-3of5-era2b`, `verified-adv-pro-image-baseline-medium-vf-era2b`, `verified-adv-pro-image-baseline-pro-vf-era2b`, `pv-high-image-t0.7-n3-opmax`, `pv-scale4-optimal-n3-opmax`, `verified-adv-image-baseline-medium-vf-era2b`, `pv-min-image-t0.7-n1-opmax`.

## 5. Cross-checks

| Check | Result |
|---|---|
| `geometric-primary`: F1 side identical to the `id` run; MCC gates passed; MCC withheld; MCB candidate set equal | yes; 150 of 150; 0; yes |
| `geometric-contains`: F1 side identical to the `id` run; MCC gates passed; MCC withheld; MCB candidate set equal | yes; 150 of 150; 0; yes |
| confusions against `results/tile-join-audit/board-era2-2026-09-12.json` (103 board cells matched) | `id` 93 equal, 10 differ (10 re-scored since); `geometric-primary` 93 equal, 10 differ (10 re-scored since); `geometric-contains` 93 equal, 10 differ (10 re-scored since) |
| confusions against `results/tile-join-audit/k-ladder-phase2-cells-2026-09-12.json` (43 board cells matched) | `id` 43 equal, 0 differ; `geometric-primary` 43 equal, 0 differ; `geometric-contains` 43 equal, 0 differ |
| reference-positive tiles (TP + FN), one value per join across all cells | `id` [229]; `geometric-primary` [199]; `geometric-contains` [229] |

**The three withheld cells** stay withheld in every run: the per-tile F1 table refuses their vocabulary under the published join, which the F1 arm keeps. Their MCC under each join, computed for disclosure only and entered into no family:

| cell | F1@20 | `id` | `geometric-primary` | `geometric-contains` |
|---|---:|---:|---:|---:|
| `g37-text-k1-verified-carried-p0.10-k1` | 0.8616 | refused | 0.9059 | 0.8761 |
| `g37-text-k1-verified-opmax` | 0.8747 | refused | 0.9535 | 0.9262 |
| `g37-text-k3-verified-opmax` | 0.9135 | refused | 0.9121 | 0.8903 |

**Track (claim iv).** A cell's track is its proposer's transmitted modality: the board membership's `track` field (E88) for 107 cells; the track of a member sharing the same `proposer_pool` for 41 -opmax rows (every pool in the membership maps to one track, checked); the pool's name for 2.

**Diagnostic files** (used by no table above; written by `id_join_mechanism.py` and `mechanism_summary.py` in `reports/s166-agent-records/mcc-join-tiering-scripts/`): `id-join-mechanism.json` counts, per cell, the false-negative tiles under `id` that geometrically contain one of the cell's detections, and `id-join-mechanism-summary.json` aggregates them.

## Changelog

### 2026-10-30 — Original publication

First publication, by the S166 MCC robustness job, part (b), on branch `mcc-join-tiering-2026-10-30`. The record, with the reading of these tables, is `reports/s166-agent-records/mcc-join-tiering.md`.
