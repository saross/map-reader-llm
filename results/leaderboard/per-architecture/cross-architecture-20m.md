# Cross-architecture comparison — 20 m buffer

**Generated**: 2026-05-06T00:25:57.124978+00:00

Each row shows the best-F1 condition within a (era, architecture) stratum at the 20 m buffer. The tier assignments come from the per-stratum BH-FDR tiering (i.e., tier 1 = statistically indistinguishable from the in-stratum top), NOT from a cross-stratum pairwise comparison. Era 1 vs. Era 2/3 is NOT tile-paired here — the tile grids differ (512 px vs 384 px).

## Era 1 — 512 px / 340 tiles

**Era leader**: `h3-high-track2-text-T1.0` (Consensus (no PV), track=text) — F1 = 0.775 [0.750, 0.798].

| Architecture | Top condition | Track | K | Vote t | Verifier | Prob t | F1 | 95% CI | P | R | MCC |
|:-------------|:--------------|:-----:|--:|:-----:|:--------:|:-----:|---:|:------:|---:|---:|---:|
| Single-pass (raw) | `h4-canonical-last` | image | 1 | 1 | — | — | 0.631 | [0.609, 0.657] | 0.532 | 0.775 | 0.214 |
| Consensus (no PV) | `h3-high-track2-text-T1.0` | text | 30 | 23 | — | — | 0.775 | [0.750, 0.798] | 0.860 | 0.705 | 0.641 |
| Single-pass + PV | — | — | — | — | — | — | — | — | — | — | — |
| Consensus + PV | — | — | — | — | — | — | — | — | — | — | — |

## Era 2 — 384 px / 487 tiles

**Era leader**: `pv-flash-high-text-16of30` (Consensus + PV, track=text) — F1 = 0.890 [0.874, 0.910].

| Architecture | Top condition | Track | K | Vote t | Verifier | Prob t | F1 | 95% CI | P | R | MCC |
|:-------------|:--------------|:-----:|--:|:-----:|:--------:|:-----:|---:|:------:|---:|---:|---:|
| Single-pass (raw) | `h11-pvd-pro-medium-text-baseline` | text | 1 | 1 | — | — | 0.763 | [0.732, 0.797] | 0.767 | 0.759 | 0.752 |
| Consensus (no PV) | `h11-pvd-pro-high-text-n5` | text | 10 | 6 | — | — | 0.836 | [0.810, 0.859] | 0.927 | 0.761 | 0.727 |
| Single-pass + PV | `pv-checklist-image` | image | 1 | 1 | checklist-image | — | 0.531 | [0.473, 0.580] | 0.620 | 0.464 | 0.031 |
| Consensus + PV | `pv-flash-high-text-16of30` | text | 30 | 16 | v1 (adversarial-text canonical) | 0.20 | 0.890 | [0.874, 0.910] | 0.915 | 0.867 | 0.789 |

## Era 3 — 384 px / 327 tiles

**Era leader**: `h8v2-scale-4` (Consensus (no PV), track=image) — F1 = 0.733 [0.699, 0.760].

| Architecture | Top condition | Track | K | Vote t | Verifier | Prob t | F1 | 95% CI | P | R | MCC |
|:-------------|:--------------|:-----:|--:|:-----:|:--------:|:-----:|---:|:------:|---:|---:|---:|
| Single-pass (raw) | — | — | — | — | — | — | — | — | — | — | — |
| Consensus (no PV) | `h8v2-scale-4` | image | 5 | 4 | — | — | 0.733 | [0.699, 0.760] | 0.821 | 0.661 | 0.772 |
| Single-pass + PV | — | — | — | — | — | — | — | — | — | — | — |
| Consensus + PV | — | — | — | — | — | — | — | — | — | — | — |

---

Tiering methodology: within each (era, architecture) stratum, conditions are ranked by point-estimate F1 at 20 m and grouped into tiers via greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. CIs are stratified bootstrap (1,000 iterations). The top row in each stratum is always Tier 1 rank 1.
