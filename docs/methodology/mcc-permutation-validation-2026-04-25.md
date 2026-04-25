# MCC permutation null validation

**Date**: 2026-04-25 (Session 79, Stage 1b)
**Author**: Claude Code
**Purpose**: prove the per-tile (TP, TN, FP, FN) classification swap produces a valid (symmetric, zero-centred) null distribution for delta-MCC before launching Stage 2 with `--metric mcc`.

## Test setup

- **Stratum**: Era 3 consensus, 14 cells
- **Pair tested**: `h10v2-pool_020_hp4hn4` vs `h10v2-pool_040_hp4hn4`
- **Tiles**: 327 (327-tile h10_test bounds)
- **Permutations**: 10,000
- **Seed**: 42

## Observed

| Quantity | Value |
|:---|---:|
| MCC(A) | +0.229562 |
| MCC(B) | +0.254591 |
| Delta MCC (observed) | -0.025029 |
| Two-sided p-value | 0.6017 |

## Null distribution

| Statistic | Value |
|:---|---:|
| Mean | +0.000643 |
| Std | 0.046693 |
| 2.5%ile | -0.087652 |
| 97.5%ile | +0.087652 |

## Symmetry verdict

Two diagnostic checks were applied:

1. **Mean approximately zero** (|mean| < 0.005): PASS (observed |mean|=0.000643)
2. **Quantile symmetry** (|q2.5 + q97.5| < 0.01): PASS (observed |q2.5 + q97.5|=0.000000)

**Overall**: PASS - proceed with Stage 2

## Methodology

Under the null hypothesis that condition labels are exchangeable within each tile, swapping each tile's full classification 4-tuple (one-hot encoding of TP/TN/FP/FN) between conditions A and B with probability 0.5 should produce a symmetric distribution of delta-MCC centred at 0 (since each tile's contribution to A-minus-B is independently inverted with prob 0.5). This is the same logical structure as the F1 test (per-tile (TP, FP, FN) swap) but with TN added; the only difference is that MCC includes the TN cell, which contributes to the denominator.

## Implication for Stage 2

If both checks pass, Stage 2 can run all populated strata with `--metric mcc` alongside the F1 build, producing parallel tier tables. If either fails, Stage 2 must skip MCC and report an F1-only table.

## Reproducibility

```bash
# Re-run from /tmp/validate_mcc_null.py
ssh sapphire 'cd /home/shawn/Code/map-reader-llm/ && \
  .venv/bin/python /tmp/validate_mcc_null.py'
```
