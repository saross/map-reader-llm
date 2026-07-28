# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:41:35.956372+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=10 x=7 achieves F1=0.7500 (+0.1926 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 10 | 7 | 0.7500 | [0.707, 0.790] | 0.7778 | 0.7241 | 405 | +0.1926 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.3116 | [0.273, 0.349] | 0.1894 | 0.8782 | 2017 |
| image-t0.7 | 5 | 2 | 0.6173 | [0.577, 0.654] | 0.4899 | 0.8345 | 741 |
| image-t0.7 | 5 | 3 | 0.7269 | [0.687, 0.765] | 0.6759 | 0.7862 | 506 |
| image-t0.7 | 5 | 4 | 0.7193 | [0.675, 0.764] | 0.7629 | 0.6805 | 388 |
| image-t0.7 | 5 | 5 | 0.6583 | [0.610, 0.709] | 0.8369 | 0.5425 | 282 |
| image-t0.7 | 10 | 1 | 0.2128 | [0.183, 0.242] | 0.1208 | 0.8920 | 3211 |
| image-t0.7 | 10 | 2 | 0.4874 | [0.446, 0.524] | 0.3390 | 0.8667 | 1112 |
| image-t0.7 | 10 | 3 | 0.6217 | [0.582, 0.659] | 0.4907 | 0.8483 | 752 |
| image-t0.7 | 10 | 4 | 0.6801 | [0.638, 0.719] | 0.5829 | 0.8161 | 609 |
| image-t0.7 | 10 | 5 | 0.7212 | [0.681, 0.757] | 0.6628 | 0.7908 | 519 |
| image-t0.7 | 10 | 6 | 0.7402 | [0.701, 0.777] | 0.7186 | 0.7632 | 462 |
| image-t0.7 | 10 | 7 | 0.7500 | [0.707, 0.790] | 0.7778 | 0.7241 | 405 |
| image-t0.7 | 10 | 8 | 0.7291 | [0.685, 0.772] | 0.8256 | 0.6529 | 344 |
| image-t0.7 | 10 | 9 | 0.6788 | [0.631, 0.724] | 0.8648 | 0.5586 | 281 |
| image-t0.7 | 10 | 10 | 0.5741 | [0.519, 0.633] | 0.8932 | 0.4230 | 206 |

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
