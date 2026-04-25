# Permutation Tiers — image track, 50 m buffer

**Generated**: 2026-04-25T06:30:49.745596+00:00
**Git commit**: f8d75579
**N permutations**: 10,000, seed 42
**Bootstrap CI**: 10,000 iterations, seed 42
**FDR**: Benjamini-Hochberg step-up at q = 0.05
**Family size**: 21 pairs

## Tiers

### Tier 1 — F1 range 0.8873–0.8950

| # | variant | F1 | 95% CI | Precision | Recall | TP | FP | FN | N |
|--:|---------|---:|:------:|----------:|-------:|---:|---:|---:|---:|
| 1 | `adversarial` | 0.8950 | [0.8686, 0.9199] | 0.8981 | 0.8920 | 388 | 44 | 47 | 432 |
| 2 | `comparative` | 0.8940 | [0.8670, 0.9189] | 0.8961 | 0.8920 | 388 | 45 | 47 | 433 |
| 3 | `brief` | 0.8922 | [0.8646, 0.9174] | 0.8902 | 0.8943 | 389 | 48 | 46 | 437 |
| 4 | `checklist` | 0.8909 | [0.8642, 0.9158] | 0.8899 | 0.8920 | 388 | 48 | 47 | 436 |
| 5 | `checklist-text` | 0.8873 | [0.8600, 0.9124] | 0.8967 | 0.8782 | 382 | 44 | 53 | 426 |

### Tier 2 — F1 range 0.8636–0.8697

| # | variant | F1 | 95% CI | Precision | Recall | TP | FP | FN | N |
|--:|---------|---:|:------:|----------:|-------:|---:|---:|---:|---:|
| 1 | `adversarial-text` (canonical) | 0.8697 | [0.8405, 0.8965] | 0.8973 | 0.8437 | 367 | 42 | 68 | 409 |
| 2 | `brief-text` | 0.8636 | [0.8296, 0.8945] | 0.9002 | 0.8299 | 361 | 40 | 74 | 401 |

## Canonical `adversarial-text` vs each alternative

| alternative | F1 canonical | F1 alt | Δ F1 (alt − canonical) | raw p | BH-adj p | significant @ FDR q=0.05 | same tier? |
|-------------|-------------:|-------:|----------------------:|------:|---------:|:---------------:|:----------:|
| `adversarial` | 0.8697 | 0.8950 | +0.0254 | 0.0006 | 0.0037 | YES | no |
| `brief` | 0.8697 | 0.8922 | +0.0225 | 0.0027 | 0.0076 | YES | no |
| `brief-text` | 0.8697 | 0.8636 | -0.0060 | 0.5575 | 0.6887 | no | YES |
| `checklist` | 0.8697 | 0.8909 | +0.0213 | 0.0029 | 0.0076 | YES | no |
| `checklist-text` | 0.8697 | 0.8873 | +0.0177 | 0.0180 | 0.0378 | YES | no |
| `comparative` | 0.8697 | 0.8940 | +0.0243 | 0.0016 | 0.0063 | YES | no |

## All pairwise permutation tests

| variant A | variant B | F1 A | F1 B | Δ F1 | raw p | BH-adj p | sig? |
|-----------|-----------|-----:|-----:|-----:|------:|---------:|:----:|
| `adversarial` | `adversarial-text` | 0.8950 | 0.8697 | +0.0254 | 0.0006 | 0.0037 | YES |
| `adversarial` | `brief` | 0.8950 | 0.8922 | +0.0028 | 0.6142 | 0.7166 | no |
| `adversarial` | `brief-text` | 0.8950 | 0.8636 | +0.0314 | 0.0003 | 0.0032 | YES |
| `adversarial` | `checklist` | 0.8950 | 0.8909 | +0.0041 | 0.3958 | 0.5541 | no |
| `adversarial` | `checklist-text` | 0.8950 | 0.8873 | +0.0077 | 0.0824 | 0.1573 | no |
| `adversarial` | `comparative` | 0.8950 | 0.8940 | +0.0010 | 0.9136 | 0.9136 | no |
| `adversarial-text` | `brief` | 0.8697 | 0.8922 | -0.0225 | 0.0027 | 0.0076 | YES |
| `adversarial-text` | `brief-text` | 0.8697 | 0.8636 | +0.0060 | 0.5575 | 0.6887 | no |
| `adversarial-text` | `checklist` | 0.8697 | 0.8909 | -0.0213 | 0.0029 | 0.0076 | YES |
| `adversarial-text` | `checklist-text` | 0.8697 | 0.8873 | -0.0177 | 0.0180 | 0.0378 | YES |
| `adversarial-text` | `comparative` | 0.8697 | 0.8940 | -0.0243 | 0.0016 | 0.0063 | YES |
| `brief` | `brief-text` | 0.8922 | 0.8636 | +0.0286 | 0.0007 | 0.0037 | YES |
| `brief` | `checklist` | 0.8922 | 0.8909 | +0.0013 | 0.7782 | 0.8171 | no |
| `brief` | `checklist-text` | 0.8922 | 0.8873 | +0.0049 | 0.3008 | 0.4859 | no |
| `brief` | `comparative` | 0.8922 | 0.8940 | -0.0018 | 0.7181 | 0.7937 | no |
| `brief-text` | `checklist` | 0.8636 | 0.8909 | -0.0273 | 0.0018 | 0.0063 | YES |
| `brief-text` | `checklist-text` | 0.8636 | 0.8873 | -0.0237 | 0.0081 | 0.0189 | YES |
| `brief-text` | `comparative` | 0.8636 | 0.8940 | -0.0304 | 0.0003 | 0.0032 | YES |
| `checklist` | `checklist-text` | 0.8909 | 0.8873 | +0.0036 | 0.3886 | 0.5541 | no |
| `checklist` | `comparative` | 0.8909 | 0.8940 | -0.0031 | 0.4769 | 0.6259 | no |
| `checklist-text` | `comparative` | 0.8873 | 0.8940 | -0.0067 | 0.1617 | 0.2830 | no |

## Method

- **Detection source**: each variant's geojson materialised at the 20 m-buffer optimum (vote_t, prob_t) pair. For 13 of 14 cells the per-buffer optima at 20/30/40/50 m are identical to the 20 m optimum; for `text-adversarial` at 50 m the 50 m-optimum differs by F1 = 0.0002 (negligible).
- **Test statistic**: micro-average F1 difference (observed F1 A − F1 B) at the target buffer, computed from tile-level TP/FP/FN counts with per-map Hungarian matching at tolerance = buffer_m.
- **Permutation test**: paired tile-swap — for each permutation, independently swap per-tile (TP, FP, FN) counts between the two variants with probability 0.5, re-aggregate micro-average F1, compute the new difference. The p-value is the two-sided tail proportion |null diff| >= |observed diff|.
- **Permutations**: 10,000 iterations, seed 42.
- **FDR correction**: Benjamini-Hochberg step-up procedure applied WITHIN each (track, buffer) family of 21 pairs at q = 0.05.
- **Tiering**: greedy clique. Rank variants by F1 descending; a variant joins the current tier iff its paired test against every existing tier member is non-significant after FDR. Otherwise open a new tier.
