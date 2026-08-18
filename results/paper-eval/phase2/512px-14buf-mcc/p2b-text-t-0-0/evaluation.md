# Evaluation: T0.0

**Generated**: 2026-08-18T13:03:37.516036+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.269 | [0.261, 0.278] | 0.217 | [0.209, 0.224] | 0.356 | [0.345, 0.366] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.479 | [0.468, 0.490] | 0.385 | [0.374, 0.396] | 0.633 | [0.621, 0.644] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.565 | [0.555, 0.576] | 0.455 | [0.443, 0.466] | 0.746 | [0.736, 0.755] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.606 | [0.595, 0.616] | 0.487 | [0.475, 0.499] | 0.800 | [0.790, 0.808] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.627 | [0.617, 0.637] | 0.505 | [0.493, 0.516] | 0.829 | [0.820, 0.836] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.643 | [0.633, 0.653] | 0.518 | [0.506, 0.528] | 0.850 | [0.842, 0.856] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.648 | [0.638, 0.658] | 0.521 | [0.510, 0.533] | 0.856 | [0.848, 0.863] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.651 | [0.641, 0.661] | 0.524 | [0.512, 0.536] | 0.860 | [0.853, 0.866] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.655 | [0.644, 0.664] | 0.527 | [0.515, 0.538] | 0.865 | [0.857, 0.871] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.656 | [0.646, 0.666] | 0.528 | [0.516, 0.540] | 0.866 | [0.859, 0.873] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.658 | [0.648, 0.668] | 0.530 | [0.518, 0.541] | 0.870 | [0.862, 0.876] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.660 | [0.649, 0.669] | 0.531 | [0.519, 0.542] | 0.871 | [0.864, 0.878] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.660 | [0.649, 0.669] | 0.531 | [0.519, 0.542] | 0.871 | [0.864, 0.878] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.661 | [0.651, 0.671] | 0.532 | [0.520, 0.544] | 0.873 | [0.866, 0.879] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here (defined on 0 of 3 passes): the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

