# Phase 2 Analysis Summary

**Generated**: 2026-02-08T04:36:01.511332+00:00
**Study Directory**: `outputs/phase2b/track2-text`
**Bootstrap Iterations**: 1000
**FDR q-value**: 0.05

## Per-Condition Metrics

| Condition | F1 | 95% CI | Precision | Recall |
|-----------|---:|:------:|----------:|-------:|
| T0.0 | 0.6602 | [0.533, 0.759] | 0.5585 | 0.8072 |
| T0.3 | 0.6212 | [0.484, 0.731] | 0.5068 | 0.8031 |
| T0.7 | 0.5672 | [0.436, 0.685] | 0.4510 | 0.7660 |
| T1.0 | 0.5687 | [0.432, 0.677] | 0.4559 | 0.7567 |
| T1.3 | 0.5258 | [0.402, 0.633] | 0.4113 | 0.7299 |

## Pairwise Comparisons

| Comparison | ΔF1 | 95% CI | Initial Sig | FDR Sig |
|------------|----:|:------:|:-----------:|:-------:|
| T0.0 vs T0.3 | +0.0378 | [-0.001, +0.084] |  |  |
| T0.0 vs T0.7 | +0.0915 | [+0.044, +0.147] | ✓ | ✓ |
| T0.0 vs T1.0 | +0.0961 | [+0.053, +0.143] | ✓ | ✓ |
| T0.0 vs T1.3 | +0.1347 | [+0.086, +0.186] | ✓ | ✓ |
| T0.3 vs T0.7 | +0.0538 | [+0.006, +0.108] | ✓ |  |
| T0.3 vs T1.0 | +0.0584 | [+0.015, +0.105] | ✓ |  |
| T0.3 vs T1.3 | +0.0970 | [+0.052, +0.142] | ✓ | ✓ |
| T0.7 vs T1.0 | +0.0046 | [-0.036, +0.041] |  |  |
| T0.7 vs T1.3 | +0.0432 | [+0.004, +0.083] | ✓ |  |
| T1.0 vs T1.3 | +0.0386 | [+0.011, +0.068] | ✓ |  |

## Summary Statistics

- **Total comparisons**: 10
- **Initially significant**: 8
- **FDR significant**: 4

## Recommendation

Optimal condition: T0.0 (mean F1 = 0.6621)
4/10 pairwise differences significant after FDR correction.
