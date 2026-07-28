# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:42:37.044341+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: text-t0.7 N=5 x=3 achieves F1=0.8579 (+0.3005 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| text-t0.7 | 5 | 3 | 0.8579 | [0.822, 0.890] | 0.9373 | 0.7908 | 367 | +0.3005 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| text-t0.7 | 5 | 1 | 0.7923 | [0.752, 0.832] | 0.7381 | 0.8552 | 504 |
| text-t0.7 | 5 | 2 | 0.8483 | [0.815, 0.880] | 0.8753 | 0.8230 | 409 |
| text-t0.7 | 5 | 3 | 0.8579 | [0.822, 0.890] | 0.9373 | 0.7908 | 367 |
| text-t0.7 | 5 | 4 | 0.8394 | [0.796, 0.874] | 0.9614 | 0.7448 | 337 |
| text-t0.7 | 5 | 5 | 0.8124 | [0.770, 0.851] | 0.9837 | 0.6920 | 306 |

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
