# Phase 2 Analysis Summary

**Generated**: 2026-02-06T06:45:59.298055+00:00
**Study Directory**: `outputs/phase2a`
**Bootstrap Iterations**: 1000
**FDR q-value**: 0.05

## Per-Condition Metrics

| Condition | F1 | 95% CI | Precision | Recall |
|-----------|---:|:------:|----------:|-------:|
| image-only | 0.4252 | [0.340, 0.500] | 0.3492 | 0.5454 |
| brief-text | 0.5425 | [0.424, 0.650] | 0.4338 | 0.7247 |
| brief-text-image | 0.4617 | [0.371, 0.541] | 0.3934 | 0.5588 |
| verbose-text | 0.4710 | [0.355, 0.569] | 0.3644 | 0.6660 |
| verbose-text-image | 0.4369 | [0.358, 0.507] | 0.3675 | 0.5392 |

## Pairwise Comparisons

| Comparison | ΔF1 | 95% CI | Initial Sig | FDR Sig |
|------------|----:|:------:|:-----------:|:-------:|
| image-only vs brief-text | -0.1155 | [-0.195, -0.026] | ✓ |  |
| image-only vs brief-text-image | -0.0331 | [-0.071, +0.006] |  |  |
| image-only vs verbose-text | -0.0400 | [-0.112, +0.041] |  |  |
| image-only vs verbose-text-image | -0.0107 | [-0.062, +0.041] |  |  |
| brief-text vs brief-text-image | +0.0824 | [-0.010, +0.168] |  |  |
| brief-text vs verbose-text | +0.0755 | [+0.017, +0.134] | ✓ |  |
| brief-text vs verbose-text-image | +0.1048 | [+0.014, +0.182] | ✓ |  |
| brief-text-image vs verbose-text | -0.0068 | [-0.089, +0.081] |  |  |
| brief-text-image vs verbose-text-image | +0.0224 | [-0.023, +0.073] |  |  |
| verbose-text vs verbose-text-image | +0.0293 | [-0.054, +0.103] |  |  |

## Summary Statistics

- **Total comparisons**: 10
- **Initially significant**: 3
- **FDR significant**: 0

## Recommendation

Optimal condition: brief-text (mean F1 = 0.5416)
No pairwise differences significant after FDR correction (q=0.05).
