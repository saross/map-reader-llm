# Phase 2 Analysis Summary

**Generated**: 2026-02-09T15:51:29.119254+00:00
**Study Directory**: `outputs/phase2c/track1-image-exploratory`
**Bootstrap Iterations**: 1000
**FDR q-value**: 0.05

## Per-Condition Metrics

| Condition | F1 | 95% CI | Precision | Recall |
|-----------|---:|:------:|----------:|-------:|
| pure-positive-canon | 0.6027 | [0.490, 0.695] | 0.5297 | 0.6990 |
| pure-positive-2hp | 0.5714 | [0.468, 0.675] | 0.4925 | 0.6804 |
| pure-positive-4hp | 0.5502 | [0.434, 0.647] | 0.4773 | 0.6495 |

## Pairwise Comparisons

| Comparison | ΔF1 | 95% CI | Initial Sig | FDR Sig |
|------------|----:|:------:|:-----------:|:-------:|
| pure-positive-canon vs pure-positive-2hp | +0.0209 | [-0.033, +0.073] |  |  |
| pure-positive-canon vs pure-positive-4hp | +0.0485 | [-0.018, +0.112] |  |  |
| pure-positive-2hp vs pure-positive-4hp | +0.0275 | [-0.038, +0.097] |  |  |

## Summary Statistics

- **Total comparisons**: 3
- **Initially significant**: 0
- **FDR significant**: 0

## Recommendation

Optimal condition: pure-positive-canon (mean F1 = 0.5983)
No pairwise differences significant after FDR correction (q=0.05).
