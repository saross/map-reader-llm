# Evaluation: consensus_t6

**Generated**: 2026-06-05T06:53:45.899543+00:00  
**Detections**: 433  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.164 | [0.156, 0.170] | 0.164 | [0.156, 0.171] | 0.163 | [0.155, 0.171] | 0.646 | [0.630, 0.659] | 0.812 | 0.833 |
| 10m | 0.433 | [0.421, 0.444] | 0.434 | [0.422, 0.445] | 0.432 | [0.421, 0.446] | 0.646 | [0.630, 0.659] | 0.812 | 0.833 |
| 15m | 0.641 | [0.630, 0.651] | 0.642 | [0.631, 0.653] | 0.639 | [0.628, 0.652] | 0.646 | [0.630, 0.659] | 0.812 | 0.833 |
| 20m | 0.735 | N/A * | 0.737 | N/A * | 0.733 | N/A * | 0.646 | N/A * | 0.812 | 0.833 |
| 25m | 0.767 | N/A * | 0.769 | N/A * | 0.765 | N/A * | 0.646 | N/A * | 0.812 | 0.833 |
| 30m | 0.788 | N/A * | 0.790 | N/A * | 0.786 | N/A * | 0.646 | N/A * | 0.812 | 0.833 |
| 35m | 0.795 | N/A * | 0.797 | N/A * | 0.793 | N/A * | 0.646 | N/A * | 0.812 | 0.833 |
| 40m | 0.804 | N/A * | 0.806 | N/A * | 0.802 | N/A * | 0.646 | N/A * | 0.812 | 0.833 |
| 45m | 0.809 | N/A * | 0.811 | N/A * | 0.807 | N/A * | 0.646 | N/A * | 0.812 | 0.833 |
| 50m | 0.818 | N/A * | 0.820 | N/A * | 0.816 | N/A * | 0.646 | N/A * | 0.812 | 0.833 |
| 75m | 0.827 | N/A * | 0.829 | N/A * | 0.825 | N/A * | 0.646 | N/A * | 0.812 | 0.833 |
| 100m | 0.830 | N/A * | 0.831 | N/A * | 0.828 | N/A * | 0.646 | N/A * | 0.812 | 0.833 |
| 125m | 0.830 | N/A * | 0.831 | N/A * | 0.828 | N/A * | 0.646 | N/A * | 0.812 | 0.833 |
| 150m | 0.830 | N/A * | 0.831 | N/A * | 0.828 | N/A * | 0.646 | N/A * | 0.812 | 0.833 |

\* Bootstrap CI suppressed for sparse-coverage buffers (50.1%, 50.1%, 50.1%, 50.1%, 50.1%, 50.1%, 50.1%, 50.1%, 50.1%, 50.1%, 50.1% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

