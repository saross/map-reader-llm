# Permutation Tiers — image track, 20 m buffer

**Generated**: 2026-04-25T06:30:42.035611+00:00
**Git commit**: f8d75579
**N permutations**: 10,000, seed 42
**Bootstrap CI**: 10,000 iterations, seed 42
**FDR**: Benjamini-Hochberg step-up at q = 0.05
**Family size**: 21 pairs

## Tiers

### Tier 1 — F1 range 0.7679–0.7866

| # | variant | F1 | 95% CI | Precision | Recall | TP | FP | FN | N |
|--:|---------|---:|:------:|----------:|-------:|---:|---:|---:|---:|
| 1 | `adversarial` | 0.7866 | [0.7461, 0.8251] | 0.7894 | 0.7839 | 341 | 91 | 94 | 432 |
| 2 | `comparative` | 0.7857 | [0.7448, 0.8241] | 0.7875 | 0.7839 | 341 | 92 | 94 | 433 |
| 3 | `brief` | 0.7844 | [0.7435, 0.8230] | 0.7826 | 0.7862 | 342 | 95 | 93 | 437 |
| 4 | `checklist` | 0.7830 | [0.7423, 0.8208] | 0.7821 | 0.7839 | 341 | 95 | 94 | 436 |
| 5 | `checklist-text` | 0.7805 | [0.7398, 0.8195] | 0.7887 | 0.7724 | 336 | 90 | 99 | 426 |
| 6 | `adversarial-text` (canonical) | 0.7725 | [0.7306, 0.8123] | 0.7971 | 0.7494 | 326 | 83 | 109 | 409 |
| 7 | `brief-text` | 0.7679 | [0.7252, 0.8087] | 0.8005 | 0.7379 | 321 | 80 | 114 | 401 |

## Canonical `adversarial-text` vs each alternative

| alternative | F1 canonical | F1 alt | Δ F1 (alt − canonical) | raw p | BH-adj p | significant @ FDR q=0.05 | same tier? |
|-------------|-------------:|-------:|----------------------:|------:|---------:|:---------------:|:----------:|
| `adversarial` | 0.7725 | 0.7866 | +0.0141 | 0.0463 | 0.2683 | no | YES |
| `brief` | 0.7725 | 0.7844 | +0.0119 | 0.1134 | 0.2995 | no | YES |
| `brief-text` | 0.7725 | 0.7679 | -0.0046 | 0.6354 | 0.7413 | no | YES |
| `checklist` | 0.7725 | 0.7830 | +0.0105 | 0.1408 | 0.3024 | no | YES |
| `checklist-text` | 0.7725 | 0.7805 | +0.0080 | 0.2817 | 0.4688 | no | YES |
| `comparative` | 0.7725 | 0.7857 | +0.0132 | 0.0857 | 0.2995 | no | YES |

## All pairwise permutation tests

| variant A | variant B | F1 A | F1 B | Δ F1 | raw p | BH-adj p | sig? |
|-----------|-----------|-----:|-----:|-----:|------:|---------:|:----:|
| `adversarial` | `adversarial-text` | 0.7866 | 0.7725 | +0.0141 | 0.0463 | 0.2683 | no |
| `adversarial` | `brief` | 0.7866 | 0.7844 | +0.0022 | 0.6142 | 0.7413 | no |
| `adversarial` | `brief-text` | 0.7866 | 0.7679 | +0.0187 | 0.0276 | 0.2683 | no |
| `adversarial` | `checklist` | 0.7866 | 0.7830 | +0.0036 | 0.3958 | 0.5937 | no |
| `adversarial` | `checklist-text` | 0.7866 | 0.7805 | +0.0061 | 0.1141 | 0.2995 | no |
| `adversarial` | `comparative` | 0.7866 | 0.7857 | +0.0009 | 0.9136 | 0.9136 | no |
| `adversarial-text` | `brief` | 0.7725 | 0.7844 | -0.0119 | 0.1134 | 0.2995 | no |
| `adversarial-text` | `brief-text` | 0.7725 | 0.7679 | +0.0046 | 0.6354 | 0.7413 | no |
| `adversarial-text` | `checklist` | 0.7725 | 0.7830 | -0.0105 | 0.1408 | 0.3024 | no |
| `adversarial-text` | `checklist-text` | 0.7725 | 0.7805 | -0.0080 | 0.2817 | 0.4688 | no |
| `adversarial-text` | `comparative` | 0.7725 | 0.7857 | -0.0132 | 0.0857 | 0.2995 | no |
| `brief` | `brief-text` | 0.7844 | 0.7679 | +0.0165 | 0.0511 | 0.2683 | no |
| `brief` | `checklist` | 0.7844 | 0.7830 | +0.0014 | 0.7782 | 0.8171 | no |
| `brief` | `checklist-text` | 0.7844 | 0.7805 | +0.0039 | 0.2902 | 0.4688 | no |
| `brief` | `comparative` | 0.7844 | 0.7857 | -0.0013 | 0.7181 | 0.7937 | no |
| `brief-text` | `checklist` | 0.7679 | 0.7830 | -0.0151 | 0.0731 | 0.2995 | no |
| `brief-text` | `checklist-text` | 0.7679 | 0.7805 | -0.0125 | 0.1440 | 0.3024 | no |
| `brief-text` | `comparative` | 0.7679 | 0.7857 | -0.0178 | 0.0381 | 0.2683 | no |
| `checklist` | `checklist-text` | 0.7830 | 0.7805 | +0.0025 | 0.4468 | 0.6255 | no |
| `checklist` | `comparative` | 0.7830 | 0.7857 | -0.0027 | 0.4769 | 0.6259 | no |
| `checklist-text` | `comparative` | 0.7805 | 0.7857 | -0.0052 | 0.2124 | 0.4055 | no |

## Method

- **Detection source**: each variant's geojson materialised at the 20 m-buffer optimum (vote_t, prob_t) pair. For 13 of 14 cells the per-buffer optima at 20/30/40/50 m are identical to the 20 m optimum; for `text-adversarial` at 50 m the 50 m-optimum differs by F1 = 0.0002 (negligible).
- **Test statistic**: micro-average F1 difference (observed F1 A − F1 B) at the target buffer, computed from tile-level TP/FP/FN counts with per-map Hungarian matching at tolerance = buffer_m.
- **Permutation test**: paired tile-swap — for each permutation, independently swap per-tile (TP, FP, FN) counts between the two variants with probability 0.5, re-aggregate micro-average F1, compute the new difference. The p-value is the two-sided tail proportion |null diff| >= |observed diff|.
- **Permutations**: 10,000 iterations, seed 42.
- **FDR correction**: Benjamini-Hochberg step-up procedure applied WITHIN each (track, buffer) family of 21 pairs at q = 0.05.
- **Tiering**: greedy clique. Rank variants by F1 descending; a variant joins the current tier iff its paired test against every existing tier member is non-significant after FDR. Otherwise open a new tier.
