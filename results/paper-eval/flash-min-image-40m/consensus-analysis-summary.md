# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:48:09.437896+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=10 x=6 achieves F1=0.7510 (+0.1936 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 10 | 6 | 0.7510 | [0.711, 0.786] | 0.6586 | 0.8736 | 577 | +0.1936 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.5263 | [0.485, 0.567] | 0.3651 | 0.9425 | 1123 |
| image-t0.7 | 5 | 2 | 0.6627 | [0.622, 0.702] | 0.5225 | 0.9057 | 754 |
| image-t0.7 | 5 | 3 | 0.7281 | [0.689, 0.763] | 0.6207 | 0.8805 | 617 |
| image-t0.7 | 5 | 4 | 0.7432 | [0.701, 0.779] | 0.6807 | 0.8184 | 523 |
| image-t0.7 | 5 | 5 | 0.7169 | [0.677, 0.756] | 0.7237 | 0.7103 | 427 |
| image-t0.7 | 10 | 1 | 0.4350 | [0.394, 0.475] | 0.2828 | 0.9425 | 1450 |
| image-t0.7 | 10 | 2 | 0.5883 | [0.547, 0.628] | 0.4286 | 0.9379 | 952 |
| image-t0.7 | 10 | 3 | 0.6700 | [0.633, 0.706] | 0.5225 | 0.9333 | 777 |
| image-t0.7 | 10 | 4 | 0.7085 | [0.670, 0.742] | 0.5753 | 0.9218 | 697 |
| image-t0.7 | 10 | 5 | 0.7358 | [0.696, 0.771] | 0.6240 | 0.8966 | 625 |
| image-t0.7 | 10 | 6 | 0.7510 | [0.711, 0.786] | 0.6586 | 0.8736 | 577 |
| image-t0.7 | 10 | 7 | 0.7443 | [0.704, 0.779] | 0.6748 | 0.8299 | 535 |
| image-t0.7 | 10 | 8 | 0.7449 | [0.704, 0.782] | 0.7004 | 0.7954 | 494 |
| image-t0.7 | 10 | 9 | 0.7267 | [0.685, 0.765] | 0.7201 | 0.7333 | 443 |
| image-t0.7 | 10 | 10 | 0.6834 | [0.639, 0.723] | 0.7535 | 0.6253 | 361 |

## Methodology

For each (temperature, pool_size, threshold) combination:

1. Detection GeoDataFrames are converted to GeoJSON features
2. Within-run deduplication (20 m tolerance) removes overlapping-tile duplicates
3. Cross-run clustering (20 m tolerance) groups detections and counts votes
4. Vote threshold filters clusters by minimum agreement
5. Consensus centroids are spatially joined to tile boundaries for F1 evaluation
6. F1 evaluation uses 40 m spatial matching tolerance
7. Bootstrapped 95% CIs use tile-level resampling (K=1000 iterations)

Pool selection uses the first-N convention: N=5 uses runs 1-5, N=10 uses runs 1-10, and larger N take the first N runs. The preregistration (§3.8) specifies first-N pooling for N=5 and N=10 within a K=10 design and additionally specifies a second N=5 pool (runs 6-10) for an independent estimate; sub-pooling of larger run pools, and the omission of the second N=5 pool, are unregistered extensions (D17 audit U2).
