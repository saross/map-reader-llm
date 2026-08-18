# Evaluation: detections_scale-4_run01

**Generated**: 2026-08-18T13:03:44.124758+00:00  
**Detections**: 882  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.266 | [0.256, 0.274] | 0.214 | [0.207, 0.222] | 0.351 | [0.340, 0.361] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.476 | [0.464, 0.486] | 0.383 | [0.371, 0.393] | 0.627 | [0.615, 0.638] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.566 | [0.555, 0.576] | 0.456 | [0.444, 0.467] | 0.746 | [0.736, 0.755] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.609 | [0.599, 0.619] | 0.491 | [0.479, 0.502] | 0.803 | [0.794, 0.811] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.625 | [0.615, 0.634] | 0.503 | [0.491, 0.514] | 0.824 | [0.815, 0.831] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.640 | [0.630, 0.650] | 0.516 | [0.503, 0.525] | 0.844 | [0.837, 0.851] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.646 | [0.635, 0.655] | 0.520 | [0.508, 0.530] | 0.852 | [0.844, 0.859] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.649 | [0.638, 0.658] | 0.523 | [0.510, 0.532] | 0.855 | [0.848, 0.862] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.653 | [0.643, 0.662] | 0.526 | [0.514, 0.536] | 0.861 | [0.854, 0.867] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.654 | [0.644, 0.663] | 0.527 | [0.515, 0.537] | 0.863 | [0.856, 0.869] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.659 | [0.649, 0.668] | 0.531 | [0.519, 0.541] | 0.868 | [0.861, 0.875] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.661 | [0.651, 0.670] | 0.533 | [0.521, 0.543] | 0.872 | [0.865, 0.878] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.661 | [0.651, 0.670] | 0.533 | [0.521, 0.543] | 0.872 | [0.865, 0.878] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.663 | [0.652, 0.671] | 0.534 | [0.522, 0.544] | 0.874 | [0.867, 0.880] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

