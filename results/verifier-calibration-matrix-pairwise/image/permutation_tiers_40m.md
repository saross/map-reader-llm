# Permutation Tiers — image track, 40 m buffer

**Generated**: 2026-04-25T06:30:47.161188+00:00
**Git commit**: f8d75579
**N permutations**: 10,000, seed 42
**Bootstrap CI**: 10,000 iterations, seed 42
**FDR**: Benjamini-Hochberg step-up at q = 0.05
**Family size**: 21 pairs

## Tiers

### Tier 1 — F1 range 0.8780–0.8858

| # | variant | F1 | 95% CI | Precision | Recall | TP | FP | FN | N |
|--:|---------|---:|:------:|----------:|-------:|---:|---:|---:|---:|
| 1 | `adversarial` | 0.8858 | [0.8568, 0.9121] | 0.8889 | 0.8828 | 384 | 48 | 51 | 432 |
| 2 | `comparative` | 0.8848 | [0.8549, 0.9115] | 0.8868 | 0.8828 | 384 | 49 | 51 | 433 |
| 3 | `brief` | 0.8830 | [0.8530, 0.9100] | 0.8810 | 0.8851 | 385 | 52 | 50 | 437 |
| 4 | `checklist` | 0.8817 | [0.8522, 0.9087] | 0.8807 | 0.8828 | 384 | 52 | 51 | 436 |
| 5 | `checklist-text` | 0.8780 | [0.8483, 0.9053] | 0.8873 | 0.8690 | 378 | 48 | 57 | 426 |

### Tier 2 — F1 range 0.8565–0.8649

| # | variant | F1 | 95% CI | Precision | Recall | TP | FP | FN | N |
|--:|---------|---:|:------:|----------:|-------:|---:|---:|---:|---:|
| 1 | `adversarial-text` (canonical) | 0.8649 | [0.8339, 0.8931] | 0.8924 | 0.8391 | 365 | 44 | 70 | 409 |
| 2 | `brief-text` | 0.8565 | [0.8206, 0.8884] | 0.8928 | 0.8230 | 358 | 43 | 77 | 401 |

## Canonical `adversarial-text` vs each alternative

| alternative | F1 canonical | F1 alt | Δ F1 (alt − canonical) | raw p | BH-adj p | significant @ FDR q=0.05 | same tier? |
|-------------|-------------:|-------:|----------------------:|------:|---------:|:---------------:|:----------:|
| `adversarial` | 0.8649 | 0.8858 | +0.0209 | 0.0042 | 0.0197 | YES | no |
| `brief` | 0.8649 | 0.8830 | +0.0181 | 0.0127 | 0.0381 | YES | no |
| `brief-text` | 0.8649 | 0.8565 | -0.0085 | 0.4023 | 0.5280 | no | YES |
| `checklist` | 0.8649 | 0.8817 | +0.0168 | 0.0159 | 0.0390 | YES | no |
| `checklist-text` | 0.8649 | 0.8780 | +0.0131 | 0.0758 | 0.1447 | no | no |
| `comparative` | 0.8649 | 0.8848 | +0.0199 | 0.0089 | 0.0312 | YES | no |

## All pairwise permutation tests

| variant A | variant B | F1 A | F1 B | Δ F1 | raw p | BH-adj p | sig? |
|-----------|-----------|-----:|-----:|-----:|------:|---------:|:----:|
| `adversarial` | `adversarial-text` | 0.8858 | 0.8649 | +0.0209 | 0.0042 | 0.0197 | YES |
| `adversarial` | `brief` | 0.8858 | 0.8830 | +0.0028 | 0.6142 | 0.7166 | no |
| `adversarial` | `brief-text` | 0.8858 | 0.8565 | +0.0294 | 0.0007 | 0.0147 | YES |
| `adversarial` | `checklist` | 0.8858 | 0.8817 | +0.0041 | 0.3958 | 0.5280 | no |
| `adversarial` | `checklist-text` | 0.8858 | 0.8780 | +0.0078 | 0.0745 | 0.1447 | no |
| `adversarial` | `comparative` | 0.8858 | 0.8848 | +0.0010 | 0.9136 | 0.9136 | no |
| `adversarial-text` | `brief` | 0.8649 | 0.8830 | -0.0181 | 0.0127 | 0.0381 | YES |
| `adversarial-text` | `brief-text` | 0.8649 | 0.8565 | +0.0085 | 0.4023 | 0.5280 | no |
| `adversarial-text` | `checklist` | 0.8649 | 0.8817 | -0.0168 | 0.0159 | 0.0390 | YES |
| `adversarial-text` | `checklist-text` | 0.8649 | 0.8780 | -0.0131 | 0.0758 | 0.1447 | no |
| `adversarial-text` | `comparative` | 0.8649 | 0.8848 | -0.0199 | 0.0089 | 0.0312 | YES |
| `brief` | `brief-text` | 0.8830 | 0.8565 | +0.0266 | 0.0032 | 0.0197 | YES |
| `brief` | `checklist` | 0.8830 | 0.8817 | +0.0013 | 0.7782 | 0.8171 | no |
| `brief` | `checklist-text` | 0.8830 | 0.8780 | +0.0050 | 0.2239 | 0.3617 | no |
| `brief` | `comparative` | 0.8830 | 0.8848 | -0.0018 | 0.7181 | 0.7937 | no |
| `brief-text` | `checklist` | 0.8565 | 0.8817 | -0.0253 | 0.0047 | 0.0197 | YES |
| `brief-text` | `checklist-text` | 0.8565 | 0.8780 | -0.0216 | 0.0167 | 0.0390 | YES |
| `brief-text` | `comparative` | 0.8565 | 0.8848 | -0.0283 | 0.0017 | 0.0179 | YES |
| `checklist` | `checklist-text` | 0.8817 | 0.8780 | +0.0037 | 0.3434 | 0.5151 | no |
| `checklist` | `comparative` | 0.8817 | 0.8848 | -0.0030 | 0.4769 | 0.5891 | no |
| `checklist-text` | `comparative` | 0.8780 | 0.8848 | -0.0067 | 0.1382 | 0.2419 | no |

## Method

- **Detection source**: each variant's geojson materialised at the 20 m-buffer optimum (vote_t, prob_t) pair. For 13 of 14 cells the per-buffer optima at 20/30/40/50 m are identical to the 20 m optimum; for `text-adversarial` at 50 m the 50 m-optimum differs by F1 = 0.0002 (negligible).
- **Test statistic**: micro-average F1 difference (observed F1 A − F1 B) at the target buffer, computed from tile-level TP/FP/FN counts with per-map Hungarian matching at tolerance = buffer_m.
- **Permutation test**: paired tile-swap — for each permutation, independently swap per-tile (TP, FP, FN) counts between the two variants with probability 0.5, re-aggregate micro-average F1, compute the new difference. The p-value is the two-sided tail proportion |null diff| >= |observed diff|.
- **Permutations**: 10,000 iterations, seed 42.
- **FDR correction**: Benjamini-Hochberg step-up procedure applied WITHIN each (track, buffer) family of 21 pairs at q = 0.05.
- **Tiering**: greedy clique. Rank variants by F1 descending; a variant joins the current tier iff its paired test against every existing tier member is non-significant after FDR. Otherwise open a new tier.
