# Permutation Tiers — text track, 50 m buffer

**Generated**: 2026-04-25T06:30:59.686669+00:00
**Git commit**: f8d75579
**N permutations**: 10,000, seed 42
**Bootstrap CI**: 10,000 iterations, seed 42
**FDR**: Benjamini-Hochberg step-up at q = 0.05
**Family size**: 21 pairs

## Tiers

### Tier 1 — F1 range 0.9045–0.9111

| # | variant | F1 | 95% CI | Precision | Recall | TP | FP | FN | N |
|--:|---------|---:|:------:|----------:|-------:|---:|---:|---:|---:|
| 1 | `comparative` | 0.9111 | [0.8857, 0.9340] | 0.9547 | 0.8713 | 379 | 18 | 56 | 397 |
| 2 | `adversarial` | 0.9097 | [0.8845, 0.9325] | 0.9545 | 0.8690 | 378 | 18 | 57 | 396 |
| 3 | `checklist` | 0.9045 | [0.8782, 0.9279] | 0.9404 | 0.8713 | 379 | 24 | 56 | 403 |

### Tier 2 — F1 range 0.9024–0.9024

| # | variant | F1 | 95% CI | Precision | Recall | TP | FP | FN | N |
|--:|---------|---:|:------:|----------:|-------:|---:|---:|---:|---:|
| 1 | `brief` | 0.9024 | [0.8760, 0.9260] | 0.9358 | 0.8713 | 379 | 26 | 56 | 405 |

### Tier 3 — F1 range 0.8701–0.8860

| # | variant | F1 | 95% CI | Precision | Recall | TP | FP | FN | N |
|--:|---------|---:|:------:|----------:|-------:|---:|---:|---:|---:|
| 1 | `checklist-text` | 0.8860 | [0.8578, 0.9115] | 0.9165 | 0.8575 | 373 | 34 | 62 | 407 |
| 2 | `adversarial-text` (canonical) | 0.8843 | [0.8555, 0.9106] | 0.9404 | 0.8345 | 363 | 23 | 72 | 386 |
| 3 | `brief-text` | 0.8701 | [0.8398, 0.8978] | 0.9318 | 0.8161 | 355 | 26 | 80 | 381 |

## Canonical `adversarial-text` vs each alternative

| alternative | F1 canonical | F1 alt | Δ F1 (alt − canonical) | raw p | BH-adj p | significant @ FDR q=0.05 | same tier? |
|-------------|-------------:|-------:|----------------------:|------:|---------:|:---------------:|:----------:|
| `adversarial` | 0.8843 | 0.9097 | +0.0255 | 0.0000 | 0.0000 | YES | no |
| `brief` | 0.8843 | 0.9024 | +0.0181 | 0.0069 | 0.0132 | YES | no |
| `brief-text` | 0.8843 | 0.8701 | -0.0142 | 0.1004 | 0.1240 | no | YES |
| `checklist` | 0.8843 | 0.9045 | +0.0202 | 0.0009 | 0.0021 | YES | no |
| `checklist-text` | 0.8843 | 0.8860 | +0.0017 | 0.8251 | 0.8251 | no | YES |
| `comparative` | 0.8843 | 0.9111 | +0.0268 | 0.0000 | 0.0000 | YES | no |

## All pairwise permutation tests

| variant A | variant B | F1 A | F1 B | Δ F1 | raw p | BH-adj p | sig? |
|-----------|-----------|-----:|-----:|-----:|------:|---------:|:----:|
| `adversarial` | `adversarial-text` | 0.9097 | 0.8843 | +0.0255 | 0.0000 | 0.0000 | YES |
| `adversarial` | `brief` | 0.9097 | 0.9024 | +0.0074 | 0.0929 | 0.1219 | no |
| `adversarial` | `brief-text` | 0.9097 | 0.8701 | +0.0396 | 0.0000 | 0.0000 | YES |
| `adversarial` | `checklist` | 0.9097 | 0.9045 | +0.0052 | 0.1742 | 0.2032 | no |
| `adversarial` | `checklist-text` | 0.9097 | 0.8860 | +0.0238 | 0.0001 | 0.0003 | YES |
| `adversarial` | `comparative` | 0.9097 | 0.9111 | -0.0013 | 0.7620 | 0.8179 | no |
| `adversarial-text` | `brief` | 0.8843 | 0.9024 | -0.0181 | 0.0069 | 0.0132 | YES |
| `adversarial-text` | `brief-text` | 0.8843 | 0.8701 | +0.0142 | 0.1004 | 0.1240 | no |
| `adversarial-text` | `checklist` | 0.8843 | 0.9045 | -0.0202 | 0.0009 | 0.0021 | YES |
| `adversarial-text` | `checklist-text` | 0.8843 | 0.8860 | -0.0017 | 0.8251 | 0.8251 | no |
| `adversarial-text` | `comparative` | 0.8843 | 0.9111 | -0.0268 | 0.0000 | 0.0000 | YES |
| `brief` | `brief-text` | 0.9024 | 0.8701 | +0.0323 | 0.0000 | 0.0000 | YES |
| `brief` | `checklist` | 0.9024 | 0.9045 | -0.0022 | 0.7790 | 0.8179 | no |
| `brief` | `checklist-text` | 0.9024 | 0.8860 | +0.0164 | 0.0114 | 0.0199 | YES |
| `brief` | `comparative` | 0.9024 | 0.9111 | -0.0087 | 0.0209 | 0.0338 | YES |
| `brief-text` | `checklist` | 0.8701 | 0.9045 | -0.0344 | 0.0001 | 0.0003 | YES |
| `brief-text` | `checklist-text` | 0.8701 | 0.8860 | -0.0159 | 0.0468 | 0.0702 | no |
| `brief-text` | `comparative` | 0.8701 | 0.9111 | -0.0410 | 0.0000 | 0.0000 | YES |
| `checklist` | `checklist-text` | 0.9045 | 0.8860 | +0.0185 | 0.0021 | 0.0044 | YES |
| `checklist` | `comparative` | 0.9045 | 0.9111 | -0.0065 | 0.0687 | 0.0962 | no |
| `checklist-text` | `comparative` | 0.8860 | 0.9111 | -0.0251 | 0.0001 | 0.0003 | YES |

## Method

- **Detection source**: each variant's geojson materialised at the 20 m-buffer optimum (vote_t, prob_t) pair. For 13 of 14 cells the per-buffer optima at 20/30/40/50 m are identical to the 20 m optimum; for `text-adversarial` at 50 m the 50 m-optimum differs by F1 = 0.0002 (negligible).
- **Test statistic**: micro-average F1 difference (observed F1 A − F1 B) at the target buffer, computed from tile-level TP/FP/FN counts with per-map Hungarian matching at tolerance = buffer_m.
- **Permutation test**: paired tile-swap — for each permutation, independently swap per-tile (TP, FP, FN) counts between the two variants with probability 0.5, re-aggregate micro-average F1, compute the new difference. The p-value is the two-sided tail proportion |null diff| >= |observed diff|.
- **Permutations**: 10,000 iterations, seed 42.
- **FDR correction**: Benjamini-Hochberg step-up procedure applied WITHIN each (track, buffer) family of 21 pairs at q = 0.05.
- **Tiering**: greedy clique. Rank variants by F1 descending; a variant joins the current tier iff its paired test against every existing tier member is non-significant after FDR. Otherwise open a new tier.
