# Permutation Tiers — image track, 30 m buffer

**Generated**: 2026-04-25T06:30:44.599178+00:00
**Git commit**: f8d75579
**N permutations**: 10,000, seed 42
**Bootstrap CI**: 10,000 iterations, seed 42
**FDR**: Benjamini-Hochberg step-up at q = 0.05
**Family size**: 21 pairs

## Tiers

### Tier 1 — F1 range 0.8571–0.8651

| # | variant | F1 | 95% CI | Precision | Recall | TP | FP | FN | N |
|--:|---------|---:|:------:|----------:|-------:|---:|---:|---:|---:|
| 1 | `adversarial` | 0.8651 | [0.8325, 0.8948] | 0.8681 | 0.8621 | 375 | 57 | 60 | 432 |
| 2 | `comparative` | 0.8641 | [0.8310, 0.8945] | 0.8661 | 0.8621 | 375 | 58 | 60 | 433 |
| 3 | `brief` | 0.8624 | [0.8292, 0.8927] | 0.8604 | 0.8644 | 376 | 61 | 59 | 437 |
| 4 | `checklist` | 0.8611 | [0.8286, 0.8912] | 0.8601 | 0.8621 | 375 | 61 | 60 | 436 |
| 5 | `checklist-text` | 0.8571 | [0.8237, 0.8883] | 0.8662 | 0.8483 | 369 | 57 | 66 | 426 |

### Tier 2 — F1 range 0.8397–0.8460

| # | variant | F1 | 95% CI | Precision | Recall | TP | FP | FN | N |
|--:|---------|---:|:------:|----------:|-------:|---:|---:|---:|---:|
| 1 | `adversarial-text` (canonical) | 0.8460 | [0.8120, 0.8771] | 0.8729 | 0.8207 | 357 | 52 | 78 | 409 |
| 2 | `brief-text` | 0.8397 | [0.8033, 0.8732] | 0.8753 | 0.8069 | 351 | 50 | 84 | 401 |

## Canonical `adversarial-text` vs each alternative

| alternative | F1 canonical | F1 alt | Δ F1 (alt − canonical) | raw p | BH-adj p | significant @ FDR q=0.05 | same tier? |
|-------------|-------------:|-------:|----------------------:|------:|---------:|:---------------:|:----------:|
| `adversarial` | 0.8460 | 0.8651 | +0.0191 | 0.0071 | 0.0373 | YES | no |
| `brief` | 0.8460 | 0.8624 | +0.0164 | 0.0235 | 0.0705 | no | no |
| `brief-text` | 0.8460 | 0.8397 | -0.0063 | 0.5060 | 0.6251 | no | YES |
| `checklist` | 0.8460 | 0.8611 | +0.0151 | 0.0305 | 0.0801 | no | no |
| `checklist-text` | 0.8460 | 0.8571 | +0.0112 | 0.1270 | 0.2425 | no | no |
| `comparative` | 0.8460 | 0.8641 | +0.0181 | 0.0154 | 0.0539 | no | no |

## All pairwise permutation tests

| variant A | variant B | F1 A | F1 B | Δ F1 | raw p | BH-adj p | sig? |
|-----------|-----------|-----:|-----:|-----:|------:|---------:|:----:|
| `adversarial` | `adversarial-text` | 0.8651 | 0.8460 | +0.0191 | 0.0071 | 0.0373 | YES |
| `adversarial` | `brief` | 0.8651 | 0.8624 | +0.0027 | 0.6142 | 0.7166 | no |
| `adversarial` | `brief-text` | 0.8651 | 0.8397 | +0.0253 | 0.0028 | 0.0326 | YES |
| `adversarial` | `checklist` | 0.8651 | 0.8611 | +0.0040 | 0.3958 | 0.5541 | no |
| `adversarial` | `checklist-text` | 0.8651 | 0.8571 | +0.0079 | 0.0730 | 0.1533 | no |
| `adversarial` | `comparative` | 0.8651 | 0.8641 | +0.0010 | 0.9136 | 0.9136 | no |
| `adversarial-text` | `brief` | 0.8460 | 0.8624 | -0.0164 | 0.0235 | 0.0705 | no |
| `adversarial-text` | `brief-text` | 0.8460 | 0.8397 | +0.0063 | 0.5060 | 0.6251 | no |
| `adversarial-text` | `checklist` | 0.8460 | 0.8611 | -0.0151 | 0.0305 | 0.0801 | no |
| `adversarial-text` | `checklist-text` | 0.8460 | 0.8571 | -0.0112 | 0.1270 | 0.2425 | no |
| `adversarial-text` | `comparative` | 0.8460 | 0.8641 | -0.0181 | 0.0154 | 0.0539 | no |
| `brief` | `brief-text` | 0.8624 | 0.8397 | +0.0227 | 0.0061 | 0.0373 | YES |
| `brief` | `checklist` | 0.8624 | 0.8611 | +0.0013 | 0.7782 | 0.8171 | no |
| `brief` | `checklist-text` | 0.8624 | 0.8571 | +0.0052 | 0.2265 | 0.3659 | no |
| `brief` | `comparative` | 0.8624 | 0.8641 | -0.0017 | 0.7181 | 0.7937 | no |
| `brief-text` | `checklist` | 0.8397 | 0.8611 | -0.0214 | 0.0095 | 0.0399 | YES |
| `brief-text` | `checklist-text` | 0.8397 | 0.8571 | -0.0174 | 0.0356 | 0.0831 | no |
| `brief-text` | `comparative` | 0.8397 | 0.8641 | -0.0243 | 0.0031 | 0.0326 | YES |
| `checklist` | `checklist-text` | 0.8611 | 0.8571 | +0.0039 | 0.3458 | 0.5187 | no |
| `checklist` | `comparative` | 0.8611 | 0.8641 | -0.0030 | 0.4769 | 0.6251 | no |
| `checklist-text` | `comparative` | 0.8571 | 0.8641 | -0.0069 | 0.1493 | 0.2613 | no |

## Method

- **Detection source**: each variant's geojson materialised at the 20 m-buffer optimum (vote_t, prob_t) pair. For 13 of 14 cells the per-buffer optima at 20/30/40/50 m are identical to the 20 m optimum; for `text-adversarial` at 50 m the 50 m-optimum differs by F1 = 0.0002 (negligible).
- **Test statistic**: micro-average F1 difference (observed F1 A − F1 B) at the target buffer, computed from tile-level TP/FP/FN counts with per-map Hungarian matching at tolerance = buffer_m.
- **Permutation test**: paired tile-swap — for each permutation, independently swap per-tile (TP, FP, FN) counts between the two variants with probability 0.5, re-aggregate micro-average F1, compute the new difference. The p-value is the two-sided tail proportion |null diff| >= |observed diff|.
- **Permutations**: 10,000 iterations, seed 42.
- **FDR correction**: Benjamini-Hochberg step-up procedure applied WITHIN each (track, buffer) family of 21 pairs at q = 0.05.
- **Tiering**: greedy clique. Rank variants by F1 descending; a variant joins the current tier iff its paired test against every existing tier member is non-significant after FDR. Otherwise open a new tier.
