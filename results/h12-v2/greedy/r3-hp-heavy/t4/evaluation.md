# Evaluation: r3-hp-heavy-greedy-t4

**Generated**: 2026-04-30T06:52:45.727053+00:00  
**Detections**: 254  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.569 | N/A * | 0.772 | N/A * | 0.451 | N/A * |
| 30m | 0.621 | N/A * | 0.843 | N/A * | 0.492 | N/A * |
| 40m | 0.636 | N/A * | 0.862 | N/A * | 0.503 | N/A * |
| 50m | 0.644 | N/A * | 0.874 | N/A * | 0.510 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (56.5%, 56.5%, 56.7%, 56.7% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

