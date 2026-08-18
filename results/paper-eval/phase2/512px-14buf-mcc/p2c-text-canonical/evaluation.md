# Evaluation: detections_canonical_run01

**Generated**: 2026-08-18T13:03:41.652505+00:00  
**Detections**: 897  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.265 | [0.257, 0.273] | 0.212 | [0.204, 0.219] | 0.352 | [0.342, 0.363] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.476 | [0.465, 0.487] | 0.381 | [0.370, 0.392] | 0.634 | [0.623, 0.645] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.558 | [0.547, 0.569] | 0.447 | [0.434, 0.459] | 0.744 | [0.735, 0.754] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.605 | [0.594, 0.615] | 0.484 | [0.470, 0.496] | 0.805 | [0.796, 0.813] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.623 | [0.612, 0.633] | 0.498 | [0.485, 0.510] | 0.829 | [0.821, 0.837] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.636 | [0.625, 0.647] | 0.509 | [0.495, 0.521] | 0.848 | [0.840, 0.855] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.643 | [0.631, 0.653] | 0.515 | [0.501, 0.526] | 0.857 | [0.849, 0.864] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.646 | [0.634, 0.656] | 0.517 | [0.503, 0.528] | 0.861 | [0.854, 0.867] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.649 | [0.637, 0.658] | 0.519 | [0.505, 0.530] | 0.865 | [0.857, 0.871] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.650 | [0.638, 0.660] | 0.521 | [0.506, 0.531] | 0.866 | [0.859, 0.873] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.653 | [0.642, 0.663] | 0.523 | [0.509, 0.534] | 0.870 | [0.863, 0.876] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.655 | [0.643, 0.664] | 0.524 | [0.510, 0.535] | 0.872 | [0.865, 0.878] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.655 | [0.643, 0.664] | 0.524 | [0.510, 0.535] | 0.872 | [0.865, 0.878] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.656 | [0.644, 0.666] | 0.525 | [0.511, 0.536] | 0.874 | [0.867, 0.880] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

