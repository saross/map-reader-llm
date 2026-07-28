# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:42:49.207537+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=5 x=3 achieves F1=0.6998 (+0.1424 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 5 | 3 | 0.6998 | [0.653, 0.741] | 0.6730 | 0.7287 | 471 | +0.1424 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.5611 | [0.522, 0.599] | 0.4257 | 0.8230 | 841 |
| image-t0.7 | 5 | 2 | 0.6621 | [0.620, 0.703] | 0.5780 | 0.7747 | 583 |
| image-t0.7 | 5 | 3 | 0.6998 | [0.653, 0.741] | 0.6730 | 0.7287 | 471 |
| image-t0.7 | 5 | 4 | 0.6925 | [0.645, 0.734] | 0.7315 | 0.6575 | 391 |
| image-t0.7 | 5 | 5 | 0.6448 | [0.594, 0.690] | 0.7946 | 0.5425 | 297 |

## Methodology

For each (temperature, pool_size, threshold) combination:

1. Detection GeoDataFrames are converted to GeoJSON features
2. Within-run deduplication (20 m tolerance) removes overlapping-tile duplicates
3. Cross-run clustering (20 m tolerance) groups detections and counts votes
4. Vote threshold filters clusters by minimum agreement
5. Consensus centroids are spatially joined to tile boundaries for F1 evaluation
6. F1 evaluation uses 20 m spatial matching tolerance
7. Bootstrapped 95% CIs use tile-level resampling (K=1000 iterations)

Pool selection uses the first-N convention: N=5 uses runs 1-5, N=10 uses runs 1-10, and larger N take the first N runs. The preregistration (§3.8) specifies first-N pooling for N=5 and N=10 within a K=10 design and additionally specifies a second N=5 pool (runs 6-10) for an independent estimate; sub-pooling of larger run pools, and the omission of the second N=5 pool, are unregistered extensions (D17 audit U2).
