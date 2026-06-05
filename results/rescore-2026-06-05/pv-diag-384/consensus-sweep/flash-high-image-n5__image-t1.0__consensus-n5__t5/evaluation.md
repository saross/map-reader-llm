# Evaluation: consensus_t5

**Generated**: 2026-06-05T06:53:25.456575+00:00  
**Detections**: 248  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.164 | N/A * | 0.226 | N/A * | 0.129 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 10m | 0.404 | N/A * | 0.556 | N/A * | 0.317 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 15m | 0.559 | N/A * | 0.770 | N/A * | 0.439 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 20m | 0.612 | N/A * | 0.843 | N/A * | 0.480 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 25m | 0.630 | N/A * | 0.867 | N/A * | 0.494 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 30m | 0.644 | N/A * | 0.887 | N/A * | 0.506 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 35m | 0.650 | N/A * | 0.895 | N/A * | 0.510 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 40m | 0.650 | N/A * | 0.895 | N/A * | 0.510 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 45m | 0.653 | N/A * | 0.899 | N/A * | 0.513 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 50m | 0.656 | N/A * | 0.903 | N/A * | 0.515 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 75m | 0.659 | N/A * | 0.907 | N/A * | 0.517 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 100m | 0.659 | N/A * | 0.907 | N/A * | 0.517 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 125m | 0.659 | N/A * | 0.907 | N/A * | 0.517 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 150m | 0.659 | N/A * | 0.907 | N/A * | 0.517 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |

\* Bootstrap CI suppressed for sparse-coverage buffers (55.6%, 55.9%, 56.1%, 56.3%, 56.3%, 56.3%, 56.3%, 56.3%, 56.3%, 56.3%, 56.3%, 56.3%, 56.3%, 56.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

