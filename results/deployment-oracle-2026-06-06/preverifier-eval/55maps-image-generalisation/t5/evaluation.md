# Evaluation: consensus_t5

**Generated**: 2026-06-06T01:37:03.975779+00:00  
**Detections**: 2834  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.041 | N/A * | 0.055 | N/A * | 0.033 | N/A * | 0.457 | N/A * | 0.477 | 0.920 |
| 10m | 0.149 | N/A * | 0.199 | N/A * | 0.119 | N/A * | 0.457 | N/A * | 0.477 | 0.920 |
| 15m | 0.270 | N/A * | 0.361 | N/A * | 0.215 | N/A * | 0.457 | N/A * | 0.477 | 0.920 |
| 20m | 0.378 | N/A * | 0.505 | N/A * | 0.302 | N/A * | 0.457 | N/A * | 0.477 | 0.920 |
| 25m | 0.447 | N/A * | 0.597 | N/A * | 0.357 | N/A * | 0.457 | N/A * | 0.477 | 0.920 |
| 30m | 0.489 | N/A * | 0.654 | N/A * | 0.391 | N/A * | 0.457 | N/A * | 0.477 | 0.920 |
| 35m | 0.509 | N/A * | 0.681 | N/A * | 0.407 | N/A * | 0.457 | N/A * | 0.477 | 0.920 |
| 40m | 0.518 | N/A * | 0.693 | N/A * | 0.414 | N/A * | 0.457 | N/A * | 0.477 | 0.920 |
| 45m | 0.525 | N/A * | 0.702 | N/A * | 0.419 | N/A * | 0.457 | N/A * | 0.477 | 0.920 |
| 50m | 0.529 | N/A * | 0.707 | N/A * | 0.422 | N/A * | 0.457 | N/A * | 0.477 | 0.920 |
| 75m | 0.533 | N/A * | 0.713 | N/A * | 0.426 | N/A * | 0.457 | N/A * | 0.477 | 0.920 |
| 100m | 0.534 | N/A * | 0.715 | N/A * | 0.427 | N/A * | 0.457 | N/A * | 0.477 | 0.920 |
| 125m | 0.535 | N/A * | 0.715 | N/A * | 0.427 | N/A * | 0.457 | N/A * | 0.477 | 0.920 |
| 150m | 0.536 | N/A * | 0.716 | N/A * | 0.428 | N/A * | 0.457 | N/A * | 0.477 | 0.920 |

\* Bootstrap CI suppressed for sparse-coverage buffers (62.2%, 62.6%, 62.9%, 63.2%, 63.4%, 63.5%, 63.6%, 63.6%, 63.6%, 63.7%, 63.7%, 63.7%, 63.7%, 63.7% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

