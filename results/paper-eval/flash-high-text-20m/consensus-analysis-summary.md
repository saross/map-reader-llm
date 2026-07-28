# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:37:28.843912+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: text-t0.7 N=30 x=26 achieves F1=0.8141 (+0.2567 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| text-t0.7 | 30 | 26 | 0.8141 | [0.778, 0.846] | 0.8337 | 0.7954 | 415 | +0.2567 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| text-t0.7 | 5 | 1 | 0.1961 | [0.163, 0.230] | 0.1095 | 0.9402 | 3736 |
| text-t0.7 | 5 | 2 | 0.4362 | [0.382, 0.486] | 0.2871 | 0.9080 | 1376 |
| text-t0.7 | 5 | 3 | 0.6000 | [0.546, 0.648] | 0.4526 | 0.8897 | 855 |
| text-t0.7 | 5 | 4 | 0.7203 | [0.672, 0.762] | 0.6284 | 0.8437 | 584 |
| text-t0.7 | 5 | 5 | 0.7788 | [0.739, 0.817] | 0.7976 | 0.7609 | 415 |
| text-t0.7 | 10 | 1 | 0.1311 | [0.108, 0.155] | 0.0704 | 0.9494 | 5866 |
| text-t0.7 | 10 | 2 | 0.3087 | [0.265, 0.353] | 0.1847 | 0.9402 | 2215 |
| text-t0.7 | 10 | 3 | 0.4180 | [0.365, 0.467] | 0.2699 | 0.9264 | 1493 |
| text-t0.7 | 10 | 4 | 0.5133 | [0.458, 0.563] | 0.3578 | 0.9080 | 1104 |
| text-t0.7 | 10 | 5 | 0.5951 | [0.538, 0.642] | 0.4448 | 0.8989 | 879 |
| text-t0.7 | 10 | 6 | 0.6661 | [0.616, 0.709] | 0.5323 | 0.8897 | 727 |
| text-t0.7 | 10 | 7 | 0.7259 | [0.680, 0.765] | 0.6305 | 0.8552 | 590 |
| text-t0.7 | 10 | 8 | 0.7674 | [0.725, 0.804] | 0.7104 | 0.8345 | 511 |
| text-t0.7 | 10 | 9 | 0.7968 | [0.757, 0.830] | 0.8005 | 0.7931 | 431 |
| text-t0.7 | 10 | 10 | 0.7821 | [0.740, 0.822] | 0.8841 | 0.7011 | 345 |
| text-t0.7 | 30 | 1 | 0.0685 | [0.056, 0.082] | 0.0355 | 0.9609 | 11771 |
| text-t0.7 | 30 | 2 | 0.1663 | [0.139, 0.195] | 0.0911 | 0.9517 | 4543 |
| text-t0.7 | 30 | 3 | 0.2350 | [0.199, 0.271] | 0.1341 | 0.9471 | 3072 |
| text-t0.7 | 30 | 4 | 0.2938 | [0.251, 0.336] | 0.1739 | 0.9448 | 2363 |
| text-t0.7 | 30 | 5 | 0.3380 | [0.292, 0.383] | 0.2059 | 0.9425 | 1991 |
| text-t0.7 | 30 | 6 | 0.3799 | [0.331, 0.427] | 0.2382 | 0.9379 | 1713 |
| text-t0.7 | 30 | 7 | 0.4110 | [0.359, 0.460] | 0.2637 | 0.9310 | 1536 |
| text-t0.7 | 30 | 8 | 0.4446 | [0.390, 0.495] | 0.2920 | 0.9310 | 1387 |
| text-t0.7 | 30 | 9 | 0.4748 | [0.420, 0.523] | 0.3186 | 0.9310 | 1271 |
| text-t0.7 | 30 | 10 | 0.5050 | [0.448, 0.553] | 0.3471 | 0.9264 | 1161 |
| text-t0.7 | 30 | 11 | 0.5355 | [0.479, 0.584] | 0.3766 | 0.9264 | 1070 |
| text-t0.7 | 30 | 12 | 0.5660 | [0.509, 0.613] | 0.4092 | 0.9172 | 975 |
| text-t0.7 | 30 | 13 | 0.5931 | [0.538, 0.639] | 0.4388 | 0.9149 | 907 |
| text-t0.7 | 30 | 14 | 0.6179 | [0.563, 0.665] | 0.4671 | 0.9126 | 850 |
| text-t0.7 | 30 | 15 | 0.6471 | [0.595, 0.691] | 0.5019 | 0.9103 | 789 |
| text-t0.7 | 30 | 16 | 0.6753 | [0.626, 0.719] | 0.5391 | 0.9034 | 729 |
| text-t0.7 | 30 | 17 | 0.7001 | [0.650, 0.740] | 0.5733 | 0.8989 | 682 |
| text-t0.7 | 30 | 18 | 0.7127 | [0.665, 0.752] | 0.5997 | 0.8782 | 637 |
| text-t0.7 | 30 | 19 | 0.7274 | [0.681, 0.766] | 0.6244 | 0.8713 | 607 |
| text-t0.7 | 30 | 20 | 0.7416 | [0.697, 0.779] | 0.6532 | 0.8575 | 571 |
| text-t0.7 | 30 | 21 | 0.7580 | [0.715, 0.793] | 0.6866 | 0.8460 | 536 |
| text-t0.7 | 30 | 22 | 0.7746 | [0.734, 0.810] | 0.7176 | 0.8414 | 510 |
| text-t0.7 | 30 | 23 | 0.7797 | [0.740, 0.814] | 0.7352 | 0.8299 | 491 |
| text-t0.7 | 30 | 24 | 0.7876 | [0.749, 0.820] | 0.7591 | 0.8184 | 469 |
| text-t0.7 | 30 | 25 | 0.8014 | [0.766, 0.835] | 0.7959 | 0.8069 | 441 |
| text-t0.7 | 30 | 26 | 0.8141 | [0.778, 0.846] | 0.8337 | 0.7954 | 415 |
| text-t0.7 | 30 | 27 | 0.8048 | [0.768, 0.839] | 0.8513 | 0.7632 | 390 |
| text-t0.7 | 30 | 28 | 0.8015 | [0.765, 0.839] | 0.8837 | 0.7333 | 361 |
| text-t0.7 | 30 | 29 | 0.7874 | [0.747, 0.827] | 0.9174 | 0.6897 | 327 |
| text-t0.7 | 30 | 30 | 0.6946 | [0.640, 0.745] | 0.9375 | 0.5517 | 256 |

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
