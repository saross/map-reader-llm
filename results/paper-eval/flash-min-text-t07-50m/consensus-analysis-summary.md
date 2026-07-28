# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:45:42.370789+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: text-t0.7 N=30 x=29 achieves F1=0.6694 (+0.1120 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| text-t0.7 | 30 | 29 | 0.6694 | [0.621, 0.715] | 0.6094 | 0.7425 | 530 | +0.1120 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| text-t0.7 | 5 | 1 | 0.4034 | [0.344, 0.461] | 0.2567 | 0.9402 | 1593 |
| text-t0.7 | 5 | 2 | 0.5224 | [0.464, 0.578] | 0.3641 | 0.9241 | 1104 |
| text-t0.7 | 5 | 3 | 0.5733 | [0.514, 0.630] | 0.4179 | 0.9126 | 950 |
| text-t0.7 | 5 | 4 | 0.6135 | [0.555, 0.669] | 0.4721 | 0.8759 | 807 |
| text-t0.7 | 5 | 5 | 0.6471 | [0.592, 0.697] | 0.5391 | 0.8092 | 653 |
| text-t0.7 | 10 | 1 | 0.3434 | [0.290, 0.395] | 0.2099 | 0.9425 | 1953 |
| text-t0.7 | 10 | 2 | 0.4590 | [0.399, 0.515] | 0.3043 | 0.9333 | 1334 |
| text-t0.7 | 10 | 3 | 0.5075 | [0.448, 0.562] | 0.3492 | 0.9287 | 1157 |
| text-t0.7 | 10 | 4 | 0.5401 | [0.482, 0.594] | 0.3819 | 0.9218 | 1050 |
| text-t0.7 | 10 | 5 | 0.5631 | [0.504, 0.618] | 0.4072 | 0.9126 | 975 |
| text-t0.7 | 10 | 6 | 0.5793 | [0.520, 0.634] | 0.4284 | 0.8943 | 908 |
| text-t0.7 | 10 | 7 | 0.6002 | [0.541, 0.654] | 0.4558 | 0.8782 | 838 |
| text-t0.7 | 10 | 8 | 0.6199 | [0.566, 0.671] | 0.4869 | 0.8529 | 762 |
| text-t0.7 | 10 | 9 | 0.6393 | [0.586, 0.690] | 0.5226 | 0.8230 | 685 |
| text-t0.7 | 10 | 10 | 0.6412 | [0.591, 0.689] | 0.5696 | 0.7333 | 560 |
| text-t0.7 | 30 | 1 | 0.2567 | [0.212, 0.303] | 0.1484 | 0.9517 | 2790 |
| text-t0.7 | 30 | 2 | 0.3535 | [0.300, 0.406] | 0.2175 | 0.9448 | 1890 |
| text-t0.7 | 30 | 3 | 0.4038 | [0.346, 0.460] | 0.2573 | 0.9379 | 1586 |
| text-t0.7 | 30 | 4 | 0.4398 | [0.382, 0.496] | 0.2874 | 0.9356 | 1416 |
| text-t0.7 | 30 | 5 | 0.4616 | [0.404, 0.519] | 0.3066 | 0.9333 | 1324 |
| text-t0.7 | 30 | 6 | 0.4790 | [0.420, 0.535] | 0.3225 | 0.9310 | 1256 |
| text-t0.7 | 30 | 7 | 0.4954 | [0.435, 0.553] | 0.3375 | 0.9310 | 1200 |
| text-t0.7 | 30 | 8 | 0.5114 | [0.451, 0.568] | 0.3525 | 0.9310 | 1149 |
| text-t0.7 | 30 | 9 | 0.5247 | [0.466, 0.580] | 0.3660 | 0.9264 | 1101 |
| text-t0.7 | 30 | 10 | 0.5378 | [0.478, 0.593] | 0.3792 | 0.9241 | 1060 |
| text-t0.7 | 30 | 11 | 0.5496 | [0.489, 0.605] | 0.3911 | 0.9241 | 1028 |
| text-t0.7 | 30 | 12 | 0.5540 | [0.494, 0.610] | 0.3964 | 0.9195 | 1009 |
| text-t0.7 | 30 | 13 | 0.5584 | [0.499, 0.615] | 0.4022 | 0.9126 | 987 |
| text-t0.7 | 30 | 14 | 0.5659 | [0.507, 0.622] | 0.4110 | 0.9080 | 961 |
| text-t0.7 | 30 | 15 | 0.5741 | [0.516, 0.631] | 0.4198 | 0.9080 | 941 |
| text-t0.7 | 30 | 16 | 0.5814 | [0.523, 0.638] | 0.4286 | 0.9034 | 917 |
| text-t0.7 | 30 | 17 | 0.5864 | [0.528, 0.642] | 0.4346 | 0.9011 | 902 |
| text-t0.7 | 30 | 18 | 0.5904 | [0.531, 0.646] | 0.4418 | 0.8897 | 876 |
| text-t0.7 | 30 | 19 | 0.5953 | [0.537, 0.651] | 0.4491 | 0.8828 | 855 |
| text-t0.7 | 30 | 20 | 0.6057 | [0.548, 0.660] | 0.4610 | 0.8828 | 833 |
| text-t0.7 | 30 | 21 | 0.6155 | [0.559, 0.670] | 0.4745 | 0.8759 | 803 |
| text-t0.7 | 30 | 22 | 0.6184 | [0.563, 0.672] | 0.4814 | 0.8644 | 781 |
| text-t0.7 | 30 | 23 | 0.6279 | [0.573, 0.680] | 0.4954 | 0.8575 | 753 |
| text-t0.7 | 30 | 24 | 0.6335 | [0.579, 0.685] | 0.5055 | 0.8483 | 730 |
| text-t0.7 | 30 | 25 | 0.6385 | [0.583, 0.691] | 0.5171 | 0.8345 | 702 |
| text-t0.7 | 30 | 26 | 0.6445 | [0.590, 0.696] | 0.5296 | 0.8230 | 676 |
| text-t0.7 | 30 | 27 | 0.6542 | [0.604, 0.702] | 0.5502 | 0.8069 | 638 |
| text-t0.7 | 30 | 28 | 0.6596 | [0.609, 0.704] | 0.5705 | 0.7816 | 596 |
| text-t0.7 | 30 | 29 | 0.6694 | [0.621, 0.715] | 0.6094 | 0.7425 | 530 |
| text-t0.7 | 30 | 30 | 0.6652 | [0.618, 0.712] | 0.6505 | 0.6805 | 455 |

## Methodology

For each (temperature, pool_size, threshold) combination:

1. Detection GeoDataFrames are converted to GeoJSON features
2. Within-run deduplication (20 m tolerance) removes overlapping-tile duplicates
3. Cross-run clustering (20 m tolerance) groups detections and counts votes
4. Vote threshold filters clusters by minimum agreement
5. Consensus centroids are spatially joined to tile boundaries for F1 evaluation
6. F1 evaluation uses 50 m spatial matching tolerance
7. Bootstrapped 95% CIs use tile-level resampling (K=1000 iterations)

Pool selection uses the first-N convention: N=5 uses runs 1-5, N=10 uses runs 1-10, and larger N take the first N runs. The preregistration (§3.8) specifies first-N pooling for N=5 and N=10 within a K=10 design and additionally specifies a second N=5 pool (runs 6-10) for an independent estimate; sub-pooling of larger run pools, and the omission of the second N=5 pool, are unregistered extensions (D17 audit U2).
