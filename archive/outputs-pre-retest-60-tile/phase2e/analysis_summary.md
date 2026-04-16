# Phase 2 Analysis Summary

**Generated**: 2026-02-12T00:10:39.966904+00:00
**Study Directory**: `outputs/phase2e`
**Bootstrap Iterations**: 1000
**FDR q-value**: 0.05

## Per-Condition Metrics

| Condition | F1 | 95% CI | Precision | Recall |
|-----------|---:|:------:|----------:|-------:|
| config-default | 0.6087 | [0.485, 0.701] | 0.5244 | 0.7258 |
| canonical-first | 0.5791 | [0.463, 0.671] | 0.4974 | 0.6928 |
| canonical-last | 0.6087 | [0.529, 0.722] | 0.5263 | 0.7216 |
| random | 0.5286 | [0.440, 0.616] | 0.4533 | 0.6340 |

## Pairwise Comparisons

| Comparison | ΔF1 | 95% CI | Initial Sig | FDR Sig |
|------------|----:|:------:|:-----------:|:-------:|
| config-default vs canonical-first | +0.0281 | [-0.042, +0.095] |  |  |
| config-default vs canonical-last | -0.0277 | [-0.114, +0.046] |  |  |
| config-default vs random | +0.0665 | [+0.008, +0.125] | ✓ |  |
| canonical-first vs canonical-last | -0.0559 | [-0.140, +0.010] |  |  |
| canonical-first vs random | +0.0384 | [-0.020, +0.099] |  |  |
| canonical-last vs random | +0.0942 | [+0.034, +0.166] | ✓ |  |

## Summary Statistics

- **Total comparisons**: 6
- **Initially significant**: 2
- **FDR significant**: 0

## Recommendation

Optimal condition: canonical-last (mean F1 = 0.6311)
No pairwise differences significant after FDR correction (q=0.05).
