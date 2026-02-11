# Phase 2 Analysis Summary

**Generated**: 2026-02-11T10:40:28.187195+00:00
**Study Directory**: `outputs/phase2d/track1-image`
**Bootstrap Iterations**: 1000
**FDR q-value**: 0.05

## Per-Condition Metrics

| Condition | F1 | 95% CI | Precision | Recall |
|-----------|---:|:------:|----------:|-------:|
| minimal | 0.6087 | [0.485, 0.701] | 0.5244 | 0.7258 |
| terse | 0.5714 | [0.484, 0.658] | 0.4925 | 0.6804 |
| verbose | 0.5778 | [0.443, 0.669] | 0.5078 | 0.6701 |

## Pairwise Comparisons

| Comparison | ΔF1 | 95% CI | Initial Sig | FDR Sig |
|------------|----:|:------:|:-----------:|:-------:|
| minimal vs terse | +0.0252 | [-0.036, +0.083] |  |  |
| minimal vs verbose | +0.0376 | [-0.010, +0.097] |  |  |
| terse vs verbose | +0.0124 | [-0.042, +0.073] |  |  |

## Summary Statistics

- **Total comparisons**: 3
- **Initially significant**: 0
- **FDR significant**: 0

## Recommendation

Optimal condition: minimal (mean F1 = 0.6034)
No pairwise differences significant after FDR correction (q=0.05).
