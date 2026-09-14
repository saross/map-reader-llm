# Evaluation: retest-phase2c__image-exploratory-pure-positive-canon

**Generated**: 2026-09-13T14:01:57.109668+00:00  
**Detections**: 664  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.123 | N/A * | 0.107 | N/A * | 0.144 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 10m | 0.316 | N/A * | 0.276 | N/A * | 0.371 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 15m | 0.477 | N/A * | 0.416 | N/A * | 0.560 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 20m | 0.555 | N/A * | 0.483 | N/A * | 0.651 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 25m | 0.607 | N/A * | 0.529 | N/A * | 0.712 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 30m | 0.638 | N/A * | 0.556 | N/A * | 0.749 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 35m | 0.659 | N/A * | 0.574 | N/A * | 0.773 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 40m | 0.671 | N/A * | 0.584 | N/A * | 0.787 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 45m | 0.678 | N/A * | 0.590 | N/A * | 0.795 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 50m | 0.690 | N/A * | 0.601 | N/A * | 0.809 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 75m | 0.704 | N/A * | 0.613 | N/A * | 0.826 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 100m | 0.709 | N/A * | 0.618 | N/A * | 0.832 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 125m | 0.711 | N/A * | 0.619 | N/A * | 0.834 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 150m | 0.714 | N/A * | 0.622 | N/A * | 0.838 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/315 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

