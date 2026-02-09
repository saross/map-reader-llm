# Phase 2 Analysis Summary

**Generated**: 2026-02-09T02:08:47.966952+00:00
**Study Directory**: `outputs/phase2c/track1-image`
**Bootstrap Iterations**: 1000
**FDR q-value**: 0.05

## Per-Condition Metrics

| Condition | F1 | 95% CI | Precision | Recall |
|-----------|---:|:------:|----------:|-------:|
| canonical | 0.5281 | [0.403, 0.628] | 0.4741 | 0.5959 |
| scale-4 | 0.5635 | [0.446, 0.658] | 0.4794 | 0.6835 |
| scale-8 | 0.5698 | [0.460, 0.663] | 0.4896 | 0.6814 |
| plus-hp | 0.6087 | [0.485, 0.701] | 0.5244 | 0.7258 |
| pure-positive-canon | 0.6027 | [0.490, 0.695] | 0.5297 | 0.6990 |

## Pairwise Comparisons

| Comparison | ΔF1 | 95% CI | Initial Sig | FDR Sig |
|------------|----:|:------:|:-----------:|:-------:|
| canonical vs scale-4 | -0.0429 | [-0.139, +0.059] |  |  |
| canonical vs scale-8 | -0.0516 | [-0.125, +0.029] |  |  |
| canonical vs plus-hp | -0.0837 | [-0.169, +0.001] |  |  |
| canonical vs pure-positive-canon | -0.0787 | [-0.149, -0.011] | ✓ |  |
| scale-4 vs scale-8 | -0.0087 | [-0.066, +0.051] |  |  |
| scale-4 vs plus-hp | -0.0408 | [-0.114, +0.026] |  |  |
| scale-4 vs pure-positive-canon | -0.0357 | [-0.105, +0.031] |  |  |
| scale-8 vs plus-hp | -0.0321 | [-0.093, +0.022] |  |  |
| scale-8 vs pure-positive-canon | -0.0271 | [-0.080, +0.027] |  |  |
| plus-hp vs pure-positive-canon | +0.0051 | [-0.062, +0.067] |  |  |

## Summary Statistics

- **Total comparisons**: 10
- **Initially significant**: 1
- **FDR significant**: 0

## Recommendation

Optimal condition: plus-hp (mean F1 = 0.6034)
No pairwise differences significant after FDR correction (q=0.05).
