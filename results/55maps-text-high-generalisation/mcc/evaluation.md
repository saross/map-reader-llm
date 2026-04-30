# Evaluation: 55maps-text-high-generalisation

**Generated**: 2026-04-30T06:54:08.486048+00:00  
**Detections**: 4143  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 50m | 0.791 | N/A * | 0.848 | N/A * | 0.741 | N/A * | 0.647 | N/A * | 0.642 | 0.953 |
| 75m | 0.793 | N/A * | 0.850 | N/A * | 0.742 | N/A * | 0.647 | N/A * | 0.642 | 0.953 |
| 100m | 0.794 | N/A * | 0.851 | N/A * | 0.744 | N/A * | 0.647 | N/A * | 0.642 | 0.953 |
| 125m | 0.795 | N/A * | 0.853 | N/A * | 0.745 | N/A * | 0.647 | N/A * | 0.642 | 0.953 |
| 150m | 0.796 | N/A * | 0.854 | N/A * | 0.745 | N/A * | 0.647 | N/A * | 0.642 | 0.953 |

\* Bootstrap CI suppressed for sparse-coverage buffers (66.3%, 66.3%, 66.3%, 66.4%, 66.4% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

