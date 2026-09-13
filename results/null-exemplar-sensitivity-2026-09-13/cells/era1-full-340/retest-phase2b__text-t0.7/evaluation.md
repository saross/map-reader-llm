# Evaluation: retest-phase2b__text-t0.7

**Generated**: 2026-09-13T14:01:31.001315+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.213 | [0.175, 0.256] | 0.169 | [0.135, 0.207] | 0.291 | [0.240, 0.343] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.437 | [0.380, 0.495] | 0.346 | [0.289, 0.404] | 0.596 | [0.532, 0.655] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.538 | [0.476, 0.597] | 0.425 | [0.360, 0.488] | 0.733 | [0.671, 0.784] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.577 | [0.513, 0.635] | 0.456 | [0.389, 0.520] | 0.786 | [0.727, 0.834] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.596 | [0.533, 0.654] | 0.471 | [0.403, 0.537] | 0.812 | [0.755, 0.857] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.609 | [0.545, 0.665] | 0.481 | [0.412, 0.547] | 0.829 | [0.776, 0.870] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.618 | [0.554, 0.674] | 0.488 | [0.418, 0.554] | 0.841 | [0.789, 0.880] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.621 | [0.558, 0.677] | 0.491 | [0.421, 0.557] | 0.846 | [0.796, 0.884] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.625 | [0.562, 0.681] | 0.494 | [0.424, 0.561] | 0.852 | [0.803, 0.889] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.629 | [0.566, 0.685] | 0.497 | [0.427, 0.564] | 0.857 | [0.810, 0.893] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.633 | [0.570, 0.690] | 0.500 | [0.430, 0.567] | 0.863 | [0.817, 0.898] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.635 | [0.572, 0.691] | 0.502 | [0.431, 0.569] | 0.866 | [0.821, 0.900] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.636 | [0.573, 0.692] | 0.503 | [0.432, 0.570] | 0.867 | [0.822, 0.902] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.637 | [0.574, 0.693] | 0.503 | [0.432, 0.570] | 0.868 | [0.823, 0.902] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here (defined on 0 of 3 passes): the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=193, TN=0, FP=122, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

