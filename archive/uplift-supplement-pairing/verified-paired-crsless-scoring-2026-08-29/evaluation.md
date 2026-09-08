# Evaluation: 55maps-generalisation__verified-paired-unverified

**Generated**: 2026-08-29T10:00:06.717624+00:00  
**Detections**: 8942  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | undefined | undefined | 0.000 | 1.000 |
| 10m | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | undefined | undefined | 0.000 | 1.000 |
| 15m | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | undefined | undefined | 0.000 | 1.000 |
| 20m | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | undefined | undefined | 0.000 | 1.000 |
| 25m | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | undefined | undefined | 0.000 | 1.000 |
| 30m | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | undefined | undefined | 0.000 | 1.000 |
| 35m | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | undefined | undefined | 0.000 | 1.000 |
| 40m | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | undefined | undefined | 0.000 | 1.000 |
| 45m | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | undefined | undefined | 0.000 | 1.000 |
| 50m | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | undefined | undefined | 0.000 | 1.000 |
| 75m | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | undefined | undefined | 0.000 | 1.000 |
| 100m | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | undefined | undefined | 0.000 | 1.000 |
| 125m | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | undefined | undefined | 0.000 | 1.000 |
| 150m | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | 0.000 | [0.000, 0.000] | undefined | undefined | 0.000 | 1.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=0, TN=5160, FP=0, FN=3381). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

