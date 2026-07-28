# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:44:25.139774+00:00  
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
| text-t0.7 | 5 | 1 | 0.4004 | [0.342, 0.457] | 0.2549 | 0.9333 | 1593 |
| text-t0.7 | 5 | 2 | 0.5172 | [0.459, 0.572] | 0.3605 | 0.9149 | 1104 |
| text-t0.7 | 5 | 3 | 0.5675 | [0.510, 0.623] | 0.4137 | 0.9034 | 950 |
| text-t0.7 | 5 | 4 | 0.6103 | [0.550, 0.666] | 0.4696 | 0.8713 | 807 |
| text-t0.7 | 5 | 5 | 0.6471 | [0.592, 0.697] | 0.5391 | 0.8092 | 653 |
| text-t0.7 | 10 | 1 | 0.3400 | [0.286, 0.392] | 0.2079 | 0.9333 | 1953 |
| text-t0.7 | 10 | 2 | 0.4556 | [0.395, 0.513] | 0.3021 | 0.9264 | 1334 |
| text-t0.7 | 10 | 3 | 0.5038 | [0.445, 0.559] | 0.3466 | 0.9218 | 1157 |
| text-t0.7 | 10 | 4 | 0.5360 | [0.477, 0.591] | 0.3790 | 0.9149 | 1050 |
| text-t0.7 | 10 | 5 | 0.5589 | [0.499, 0.614] | 0.4041 | 0.9057 | 975 |
| text-t0.7 | 10 | 6 | 0.5778 | [0.519, 0.632] | 0.4273 | 0.8920 | 908 |
| text-t0.7 | 10 | 7 | 0.6002 | [0.541, 0.654] | 0.4558 | 0.8782 | 838 |
| text-t0.7 | 10 | 8 | 0.6199 | [0.566, 0.671] | 0.4869 | 0.8529 | 762 |
| text-t0.7 | 10 | 9 | 0.6393 | [0.586, 0.690] | 0.5226 | 0.8230 | 685 |
| text-t0.7 | 10 | 10 | 0.6412 | [0.591, 0.689] | 0.5696 | 0.7333 | 560 |
| text-t0.7 | 30 | 1 | 0.2549 | [0.209, 0.300] | 0.1473 | 0.9448 | 2790 |
| text-t0.7 | 30 | 2 | 0.3510 | [0.297, 0.403] | 0.2159 | 0.9379 | 1890 |
| text-t0.7 | 30 | 3 | 0.3998 | [0.343, 0.456] | 0.2547 | 0.9287 | 1586 |
| text-t0.7 | 30 | 4 | 0.4365 | [0.378, 0.493] | 0.2853 | 0.9287 | 1416 |
| text-t0.7 | 30 | 5 | 0.4582 | [0.399, 0.515] | 0.3044 | 0.9264 | 1324 |
| text-t0.7 | 30 | 6 | 0.4755 | [0.416, 0.532] | 0.3201 | 0.9241 | 1256 |
| text-t0.7 | 30 | 7 | 0.4917 | [0.432, 0.548] | 0.3350 | 0.9241 | 1200 |
| text-t0.7 | 30 | 8 | 0.5076 | [0.447, 0.564] | 0.3499 | 0.9241 | 1149 |
| text-t0.7 | 30 | 9 | 0.5208 | [0.461, 0.576] | 0.3633 | 0.9195 | 1101 |
| text-t0.7 | 30 | 10 | 0.5351 | [0.475, 0.590] | 0.3774 | 0.9195 | 1060 |
| text-t0.7 | 30 | 11 | 0.5468 | [0.486, 0.602] | 0.3891 | 0.9195 | 1028 |
| text-t0.7 | 30 | 12 | 0.5512 | [0.492, 0.607] | 0.3944 | 0.9149 | 1009 |
| text-t0.7 | 30 | 13 | 0.5556 | [0.495, 0.611] | 0.4002 | 0.9080 | 987 |
| text-t0.7 | 30 | 14 | 0.5630 | [0.503, 0.619] | 0.4089 | 0.9034 | 961 |
| text-t0.7 | 30 | 15 | 0.5712 | [0.512, 0.626] | 0.4176 | 0.9034 | 941 |
| text-t0.7 | 30 | 16 | 0.5784 | [0.520, 0.634] | 0.4264 | 0.8989 | 917 |
| text-t0.7 | 30 | 17 | 0.5834 | [0.526, 0.639] | 0.4324 | 0.8966 | 902 |
| text-t0.7 | 30 | 18 | 0.5889 | [0.530, 0.645] | 0.4406 | 0.8874 | 876 |
| text-t0.7 | 30 | 19 | 0.5938 | [0.536, 0.650] | 0.4480 | 0.8805 | 855 |
| text-t0.7 | 30 | 20 | 0.6041 | [0.547, 0.660] | 0.4598 | 0.8805 | 833 |
| text-t0.7 | 30 | 21 | 0.6139 | [0.558, 0.669] | 0.4732 | 0.8736 | 803 |
| text-t0.7 | 30 | 22 | 0.6168 | [0.561, 0.671] | 0.4802 | 0.8621 | 781 |
| text-t0.7 | 30 | 23 | 0.6263 | [0.571, 0.679] | 0.4940 | 0.8552 | 753 |
| text-t0.7 | 30 | 24 | 0.6318 | [0.577, 0.683] | 0.5041 | 0.8460 | 730 |
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
6. F1 evaluation uses 30 m spatial matching tolerance
7. Bootstrapped 95% CIs use tile-level resampling (K=1000 iterations)

Pool selection uses the first-N convention: N=5 uses runs 1-5, N=10 uses runs 1-10, and larger N take the first N runs. The preregistration (§3.8) specifies first-N pooling for N=5 and N=10 within a K=10 design and additionally specifies a second N=5 pool (runs 6-10) for an independent estimate; sub-pooling of larger run pools, and the omission of the second N=5 pool, are unregistered extensions (D17 audit U2).
