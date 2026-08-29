# Evaluation: retest-phase3a-replication__text-minimal-t0_7-n30-25of30-n1

**Generated**: 2026-08-29T07:29:37.293418+00:00  
**Detections**: 902  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.222 | [0.186, 0.263] | 0.177 | [0.145, 0.214] | 0.297 | [0.251, 0.347] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.457 | [0.401, 0.512] | 0.365 | [0.310, 0.421] | 0.610 | [0.549, 0.666] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.541 | [0.483, 0.596] | 0.432 | [0.372, 0.493] | 0.724 | [0.663, 0.773] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.582 | [0.522, 0.638] | 0.465 | [0.400, 0.527] | 0.777 | [0.717, 0.824] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.609 | [0.551, 0.664] | 0.487 | [0.422, 0.550] | 0.815 | [0.762, 0.857] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.623 | [0.564, 0.678] | 0.498 | [0.431, 0.561] | 0.833 | [0.783, 0.874] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.626 | [0.567, 0.680] | 0.500 | [0.434, 0.563] | 0.837 | [0.787, 0.877] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.634 | [0.575, 0.688] | 0.507 | [0.440, 0.570] | 0.848 | [0.800, 0.886] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.634 | [0.575, 0.688] | 0.507 | [0.440, 0.570] | 0.848 | [0.800, 0.886] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.638 | [0.580, 0.691] | 0.510 | [0.443, 0.572] | 0.853 | [0.806, 0.890] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.643 | [0.583, 0.696] | 0.513 | [0.445, 0.576] | 0.859 | [0.812, 0.896] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.645 | [0.586, 0.698] | 0.515 | [0.447, 0.578] | 0.863 | [0.818, 0.898] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.645 | [0.586, 0.698] | 0.515 | [0.447, 0.578] | 0.863 | [0.818, 0.898] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.647 | [0.588, 0.699] | 0.517 | [0.448, 0.579] | 0.865 | [0.820, 0.900] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

