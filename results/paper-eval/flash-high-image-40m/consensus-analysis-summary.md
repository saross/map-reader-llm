# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:42:06.230712+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=10 x=6 achieves F1=0.8294 (+0.2720 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 10 | 6 | 0.8294 | [0.795, 0.859] | 0.8052 | 0.8552 | 462 | +0.2720 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.3401 | [0.299, 0.377] | 0.2067 | 0.9586 | 2017 |
| image-t0.7 | 5 | 2 | 0.6956 | [0.655, 0.730] | 0.5520 | 0.9402 | 741 |
| image-t0.7 | 5 | 3 | 0.8183 | [0.783, 0.849] | 0.7609 | 0.8851 | 506 |
| image-t0.7 | 5 | 4 | 0.7922 | [0.754, 0.827] | 0.8402 | 0.7494 | 388 |
| image-t0.7 | 5 | 5 | 0.7085 | [0.659, 0.753] | 0.9007 | 0.5839 | 282 |
| image-t0.7 | 10 | 1 | 0.2320 | [0.202, 0.261] | 0.1317 | 0.9724 | 3211 |
| image-t0.7 | 10 | 2 | 0.5365 | [0.495, 0.575] | 0.3732 | 0.9540 | 1112 |
| image-t0.7 | 10 | 3 | 0.6976 | [0.658, 0.733] | 0.5505 | 0.9517 | 752 |
| image-t0.7 | 10 | 4 | 0.7701 | [0.729, 0.804] | 0.6601 | 0.9241 | 609 |
| image-t0.7 | 10 | 5 | 0.8134 | [0.778, 0.842] | 0.7476 | 0.8920 | 519 |
| image-t0.7 | 10 | 6 | 0.8294 | [0.795, 0.859] | 0.8052 | 0.8552 | 462 |
| image-t0.7 | 10 | 7 | 0.8238 | [0.788, 0.857] | 0.8543 | 0.7954 | 405 |
| image-t0.7 | 10 | 8 | 0.7882 | [0.750, 0.825] | 0.8924 | 0.7057 | 344 |
| image-t0.7 | 10 | 9 | 0.7235 | [0.676, 0.767] | 0.9217 | 0.5954 | 281 |
| image-t0.7 | 10 | 10 | 0.6053 | [0.552, 0.661] | 0.9417 | 0.4460 | 206 |

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
