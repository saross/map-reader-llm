# Evaluation: detections_scale-8_run01

**Generated**: 2026-08-18T13:03:44.952833+00:00  
**Detections**: 881  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.266 | [0.258, 0.274] | 0.214 | [0.207, 0.221] | 0.351 | [0.341, 0.361] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.480 | [0.469, 0.491] | 0.387 | [0.377, 0.397] | 0.633 | [0.621, 0.644] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.568 | [0.557, 0.578] | 0.457 | [0.446, 0.468] | 0.748 | [0.738, 0.757] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.607 | [0.597, 0.617] | 0.489 | [0.477, 0.500] | 0.800 | [0.790, 0.807] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.628 | [0.618, 0.638] | 0.506 | [0.494, 0.517] | 0.828 | [0.819, 0.835] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.645 | [0.635, 0.654] | 0.520 | [0.508, 0.530] | 0.850 | [0.842, 0.856] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.649 | [0.639, 0.658] | 0.523 | [0.511, 0.534] | 0.855 | [0.848, 0.862] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.652 | [0.642, 0.661] | 0.525 | [0.514, 0.536] | 0.859 | [0.852, 0.865] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.656 | [0.646, 0.665] | 0.529 | [0.517, 0.540] | 0.865 | [0.858, 0.871] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.658 | [0.648, 0.667] | 0.530 | [0.518, 0.541] | 0.866 | [0.859, 0.872] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.661 | [0.650, 0.670] | 0.532 | [0.521, 0.543] | 0.870 | [0.863, 0.876] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.662 | [0.652, 0.671] | 0.533 | [0.522, 0.545] | 0.872 | [0.865, 0.878] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.662 | [0.652, 0.671] | 0.533 | [0.522, 0.545] | 0.872 | [0.865, 0.878] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.663 | [0.653, 0.672] | 0.535 | [0.523, 0.546] | 0.874 | [0.867, 0.880] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

