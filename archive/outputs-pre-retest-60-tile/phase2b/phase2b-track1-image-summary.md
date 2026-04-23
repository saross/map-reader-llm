# Phase 2 Analysis Summary

**Generated**: 2026-02-08T04:36:01.179183+00:00
**Study Directory**: `outputs/phase2b/track1-image`
**Bootstrap Iterations**: 1000
**FDR q-value**: 0.05

## Per-Condition Metrics

| Condition | F1 | 95% CI | Precision | Recall |
|-----------|---:|:------:|----------:|-------:|
| T0.0 | 0.5574 | [0.453, 0.643] | 0.4761 | 0.6722 |
| T0.3 | 0.5492 | [0.457, 0.631] | 0.4645 | 0.6722 |
| T0.7 | 0.4814 | [0.403, 0.557] | 0.4060 | 0.5918 |
| T1.0 | 0.4578 | [0.369, 0.532] | 0.3830 | 0.5691 |
| T1.3 | 0.4387 | [0.349, 0.506] | 0.3640 | 0.5526 |

## Pairwise Comparisons

| Comparison | ΔF1 | 95% CI | Initial Sig | FDR Sig |
|------------|----:|:------:|:-----------:|:-------:|
| T0.0 vs T0.3 | +0.0044 | [-0.033, +0.040] |  |  |
| T0.0 vs T0.7 | +0.0700 | [+0.032, +0.107] | ✓ | ✓ |
| T0.0 vs T1.0 | +0.0992 | [+0.060, +0.138] | ✓ | ✓ |
| T0.0 vs T1.3 | +0.1209 | [+0.075, +0.174] | ✓ | ✓ |
| T0.3 vs T0.7 | +0.0656 | [+0.045, +0.089] | ✓ | ✓ |
| T0.3 vs T1.0 | +0.0948 | [+0.054, +0.133] | ✓ | ✓ |
| T0.3 vs T1.3 | +0.1165 | [+0.075, +0.161] | ✓ | ✓ |
| T0.7 vs T1.0 | +0.0291 | [-0.007, +0.061] |  |  |
| T0.7 vs T1.3 | +0.0509 | [+0.013, +0.088] | ✓ |  |
| T1.0 vs T1.3 | +0.0218 | [-0.013, +0.055] |  |  |

## Summary Statistics

- **Total comparisons**: 10
- **Initially significant**: 7
- **FDR significant**: 6

## Recommendation

Optimal condition: T0.0 (mean F1 = 0.5549)
6/10 pairwise differences significant after FDR correction.
