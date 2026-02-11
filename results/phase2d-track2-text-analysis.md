# Phase 2 Analysis Summary

**Generated**: 2026-02-11T07:13:49.556896+00:00
**Study Directory**: `outputs/phase2d/track2-text`
**Bootstrap Iterations**: 1000
**FDR q-value**: 0.05

## Per-Condition Metrics

| Condition | F1 | 95% CI | Precision | Recall |
|-----------|---:|:------:|----------:|-------:|
| minimal | 0.6602 | [0.533, 0.759] | 0.5585 | 0.8072 |
| terse | 0.6018 | [0.450, 0.729] | 0.5060 | 0.7423 |
| verbose | 0.5479 | [0.431, 0.646] | 0.4795 | 0.6392 |

## Pairwise Comparisons

| Comparison | ΔF1 | 95% CI | Initial Sig | FDR Sig |
|------------|----:|:------:|:-----------:|:-------:|
| minimal vs terse | +0.0648 | [-0.011, +0.147] |  |  |
| minimal vs verbose | +0.1140 | [+0.048, +0.174] | ✓ | ✓ |
| terse vs verbose | +0.0492 | [-0.041, +0.130] |  |  |

## Summary Statistics

- **Total comparisons**: 3
- **Initially significant**: 1
- **FDR significant**: 1

## Recommendation

Optimal condition: minimal (mean F1 = 0.6621)
1/3 pairwise differences significant after FDR correction.
