# Evaluation: detections_random_run01

**Generated**: 2026-08-21T13:44:27.460771+00:00  
**Detections**: 821  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.140 | N/A * | 0.116 | N/A * | 0.176 | N/A * | 0.067 | N/A * | 1.000 | 0.007 |
| 10m | 0.335 | N/A * | 0.278 | N/A * | 0.423 | N/A * | 0.067 | N/A * | 1.000 | 0.007 |
| 15m | 0.482 | N/A * | 0.400 | N/A * | 0.609 | N/A * | 0.067 | N/A * | 1.000 | 0.007 |
| 20m | 0.571 | N/A * | 0.473 | N/A * | 0.720 | N/A * | 0.067 | N/A * | 1.000 | 0.007 |
| 25m | 0.612 | N/A * | 0.507 | N/A * | 0.772 | N/A * | 0.067 | N/A * | 1.000 | 0.007 |
| 30m | 0.644 | N/A * | 0.533 | N/A * | 0.813 | N/A * | 0.067 | N/A * | 1.000 | 0.007 |
| 35m | 0.665 | N/A * | 0.550 | N/A * | 0.839 | N/A * | 0.067 | N/A * | 1.000 | 0.007 |
| 40m | 0.673 | N/A * | 0.558 | N/A * | 0.850 | N/A * | 0.067 | N/A * | 1.000 | 0.007 |
| 45m | 0.687 | N/A * | 0.569 | N/A * | 0.866 | N/A * | 0.067 | N/A * | 1.000 | 0.007 |
| 50m | 0.697 | N/A * | 0.577 | N/A * | 0.879 | N/A * | 0.067 | N/A * | 1.000 | 0.007 |
| 75m | 0.710 | N/A * | 0.588 | N/A * | 0.896 | N/A * | 0.067 | N/A * | 1.000 | 0.007 |
| 100m | 0.713 | N/A * | 0.591 | N/A * | 0.900 | N/A * | 0.067 | N/A * | 1.000 | 0.007 |
| 125m | 0.718 | N/A * | 0.594 | N/A * | 0.905 | N/A * | 0.067 | N/A * | 1.000 | 0.007 |
| 150m | 0.718 | N/A * | 0.594 | N/A * | 0.905 | N/A * | 0.067 | N/A * | 1.000 | 0.007 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

