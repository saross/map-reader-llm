# Permutation Tiers — text track, 20 m buffer

**Generated**: 2026-04-25T06:30:52.228983+00:00
**Git commit**: f8d75579
**N permutations**: 10,000, seed 42
**Bootstrap CI**: 10,000 iterations, seed 42
**FDR**: Benjamini-Hochberg step-up at q = 0.05
**Family size**: 21 pairs

## Tiers

### Tier 1 — F1 range 0.8783–0.8846

| # | variant | F1 | 95% CI | Precision | Recall | TP | FP | FN | N |
|--:|---------|---:|:------:|----------:|-------:|---:|---:|---:|---:|
| 1 | `comparative` | 0.8846 | [0.8546, 0.9120] | 0.9270 | 0.8460 | 368 | 29 | 67 | 397 |
| 2 | `adversarial` | 0.8833 | [0.8539, 0.9106] | 0.9268 | 0.8437 | 367 | 29 | 68 | 396 |
| 3 | `checklist` | 0.8783 | [0.8481, 0.9061] | 0.9132 | 0.8460 | 368 | 35 | 67 | 403 |

### Tier 2 — F1 range 0.8762–0.8762

| # | variant | F1 | 95% CI | Precision | Recall | TP | FP | FN | N |
|--:|---------|---:|:------:|----------:|-------:|---:|---:|---:|---:|
| 1 | `brief` | 0.8762 | [0.8455, 0.9041] | 0.9086 | 0.8460 | 368 | 37 | 67 | 405 |

### Tier 3 — F1 range 0.8456–0.8599

| # | variant | F1 | 95% CI | Precision | Recall | TP | FP | FN | N |
|--:|---------|---:|:------:|----------:|-------:|---:|---:|---:|---:|
| 1 | `checklist-text` | 0.8599 | [0.8286, 0.8889] | 0.8894 | 0.8322 | 362 | 45 | 73 | 407 |
| 2 | `adversarial-text` (canonical) | 0.8575 | [0.8241, 0.8884] | 0.9119 | 0.8092 | 352 | 34 | 83 | 386 |
| 3 | `brief-text` | 0.8456 | [0.8127, 0.8765] | 0.9055 | 0.7931 | 345 | 36 | 90 | 381 |

## Canonical `adversarial-text` vs each alternative

| alternative | F1 canonical | F1 alt | Δ F1 (alt − canonical) | raw p | BH-adj p | significant @ FDR q=0.05 | same tier? |
|-------------|-------------:|-------:|----------------------:|------:|---------:|:---------------:|:----------:|
| `adversarial` | 0.8575 | 0.8833 | +0.0258 | 0.0000 | 0.0000 | YES | no |
| `brief` | 0.8575 | 0.8762 | +0.0187 | 0.0055 | 0.0105 | YES | no |
| `brief-text` | 0.8575 | 0.8456 | -0.0119 | 0.1831 | 0.2136 | no | YES |
| `checklist` | 0.8575 | 0.8783 | +0.0208 | 0.0006 | 0.0014 | YES | no |
| `checklist-text` | 0.8575 | 0.8599 | +0.0024 | 0.8037 | 0.8037 | no | YES |
| `comparative` | 0.8575 | 0.8846 | +0.0271 | 0.0000 | 0.0000 | YES | no |

## All pairwise permutation tests

| variant A | variant B | F1 A | F1 B | Δ F1 | raw p | BH-adj p | sig? |
|-----------|-----------|-----:|-----:|-----:|------:|---------:|:----:|
| `adversarial` | `adversarial-text` | 0.8833 | 0.8575 | +0.0258 | 0.0000 | 0.0000 | YES |
| `adversarial` | `brief` | 0.8833 | 0.8762 | +0.0071 | 0.0929 | 0.1219 | no |
| `adversarial` | `brief-text` | 0.8833 | 0.8456 | +0.0377 | 0.0000 | 0.0000 | YES |
| `adversarial` | `checklist` | 0.8833 | 0.8783 | +0.0050 | 0.1742 | 0.2136 | no |
| `adversarial` | `checklist-text` | 0.8833 | 0.8599 | +0.0234 | 0.0002 | 0.0005 | YES |
| `adversarial` | `comparative` | 0.8833 | 0.8846 | -0.0013 | 0.7620 | 0.8037 | no |
| `adversarial-text` | `brief` | 0.8575 | 0.8762 | -0.0187 | 0.0055 | 0.0105 | YES |
| `adversarial-text` | `brief-text` | 0.8575 | 0.8456 | +0.0119 | 0.1831 | 0.2136 | no |
| `adversarial-text` | `checklist` | 0.8575 | 0.8783 | -0.0208 | 0.0006 | 0.0014 | YES |
| `adversarial-text` | `checklist-text` | 0.8575 | 0.8599 | -0.0024 | 0.8037 | 0.8037 | no |
| `adversarial-text` | `comparative` | 0.8575 | 0.8846 | -0.0271 | 0.0000 | 0.0000 | YES |
| `brief` | `brief-text` | 0.8762 | 0.8456 | +0.0306 | 0.0000 | 0.0000 | YES |
| `brief` | `checklist` | 0.8762 | 0.8783 | -0.0021 | 0.7790 | 0.8037 | no |
| `brief` | `checklist-text` | 0.8762 | 0.8599 | +0.0163 | 0.0114 | 0.0199 | YES |
| `brief` | `comparative` | 0.8762 | 0.8846 | -0.0084 | 0.0209 | 0.0338 | YES |
| `brief-text` | `checklist` | 0.8456 | 0.8783 | -0.0327 | 0.0001 | 0.0003 | YES |
| `brief-text` | `checklist-text` | 0.8456 | 0.8599 | -0.0143 | 0.0724 | 0.1014 | no |
| `brief-text` | `comparative` | 0.8456 | 0.8846 | -0.0390 | 0.0000 | 0.0000 | YES |
| `checklist` | `checklist-text` | 0.8783 | 0.8599 | +0.0184 | 0.0017 | 0.0036 | YES |
| `checklist` | `comparative` | 0.8783 | 0.8846 | -0.0063 | 0.0687 | 0.1014 | no |
| `checklist-text` | `comparative` | 0.8599 | 0.8846 | -0.0248 | 0.0001 | 0.0003 | YES |

## Method

- **Detection source**: each variant's geojson materialised at the 20 m-buffer optimum (vote_t, prob_t) pair. For 13 of 14 cells the per-buffer optima at 20/30/40/50 m are identical to the 20 m optimum; for `text-adversarial` at 50 m the 50 m-optimum differs by F1 = 0.0002 (negligible).
- **Test statistic**: micro-average F1 difference (observed F1 A − F1 B) at the target buffer, computed from tile-level TP/FP/FN counts with per-map Hungarian matching at tolerance = buffer_m.
- **Permutation test**: paired tile-swap — for each permutation, independently swap per-tile (TP, FP, FN) counts between the two variants with probability 0.5, re-aggregate micro-average F1, compute the new difference. The p-value is the two-sided tail proportion |null diff| >= |observed diff|.
- **Permutations**: 10,000 iterations, seed 42.
- **FDR correction**: Benjamini-Hochberg step-up procedure applied WITHIN each (track, buffer) family of 21 pairs at q = 0.05.
- **Tiering**: greedy clique. Rank variants by F1 descending; a variant joins the current tier iff its paired test against every existing tier member is non-significant after FDR. Otherwise open a new tier.
