# Evaluation: detections_plus-hp_run01

**Generated**: 2026-08-18T13:03:42.474627+00:00  
**Detections**: 885  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.264 | [0.255, 0.272] | 0.212 | [0.205, 0.220] | 0.349 | [0.339, 0.359] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.468 | [0.457, 0.478] | 0.376 | [0.365, 0.386] | 0.618 | [0.606, 0.629] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.555 | [0.545, 0.564] | 0.446 | [0.435, 0.456] | 0.733 | [0.723, 0.742] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.597 | [0.587, 0.607] | 0.480 | [0.469, 0.491] | 0.788 | [0.778, 0.796] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.618 | [0.608, 0.627] | 0.497 | [0.486, 0.508] | 0.816 | [0.807, 0.824] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.638 | [0.627, 0.646] | 0.513 | [0.500, 0.523] | 0.842 | [0.835, 0.849] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.645 | [0.634, 0.654] | 0.519 | [0.505, 0.529] | 0.852 | [0.845, 0.858] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.649 | [0.638, 0.658] | 0.522 | [0.509, 0.532] | 0.857 | [0.850, 0.863] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.653 | [0.643, 0.662] | 0.525 | [0.513, 0.535] | 0.863 | [0.856, 0.869] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.654 | [0.644, 0.663] | 0.527 | [0.514, 0.536] | 0.865 | [0.858, 0.870] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.657 | [0.647, 0.666] | 0.529 | [0.516, 0.538] | 0.868 | [0.861, 0.875] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.659 | [0.648, 0.668] | 0.530 | [0.517, 0.540] | 0.870 | [0.864, 0.876] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.659 | [0.648, 0.668] | 0.530 | [0.517, 0.540] | 0.870 | [0.864, 0.876] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.661 | [0.651, 0.670] | 0.532 | [0.520, 0.542] | 0.874 | [0.867, 0.880] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

