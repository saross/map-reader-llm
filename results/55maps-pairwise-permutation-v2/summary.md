# Pairwise paired-permutation tests — 55-map corrected detection sets

**Timestamp**: 2026-04-27T11:37:53.161659+00:00
**Pairs**: T=0.3 vs T=0.7, T=0.3 vs image, T=0.7 vs image
**Buffers**: 20, 25, 30, 35, 40, 45, 50, 75, 100, 125 m
**Permutations**: 10 000 per cell, seed = 42, two-sided
**Bootstrap CI**: 10 000 tile-level paired iterations, seed = 42
**FDR correction**: Benjamini-Hochberg within each pair, q = 0.05
**Methodology**: Approach B — extended-GT-at-R Hungarian matching; per-side
extended GT identical to each run's `corrected-f1-multi-buffer/summary.json`.
**Test statistic**: aggregate (micro-average) F1 difference; tile-swap
permutations preserve pairing across the 8 541 evaluation tiles.

## Headline at canonical R = 50 m

- **T=0.3 vs T=0.7** at R = 50 m: ΔF1 = +0.0177 [+0.0102, +0.0254]; raw p = <0.001, BH-FDR p = <0.001 (significant at q = 0.05 within pair).
- **T=0.3 vs image** at R = 50 m: ΔF1 = +0.0119 [+0.0026, +0.0211]; raw p = 0.012, BH-FDR p = 0.017 (significant at q = 0.05 within pair).
- **T=0.7 vs image** at R = 50 m: ΔF1 = -0.0057 [-0.0154, +0.0039]; raw p = 0.239, BH-FDR p = 0.239 (ns at q = 0.05 within pair).

## Buffers surviving BH-FDR correction (q = 0.05) within pair

- **T=0.3 vs T=0.7**: significant after BH-FDR (q = 0.05) at R ∈ {25 m, 35 m, 40 m, 45 m, 50 m, 75 m, 100 m, 125 m}.
- **T=0.3 vs image**: significant after BH-FDR (q = 0.05) at R ∈ {20 m, 25 m, 30 m, 35 m, 40 m, 45 m, 50 m}.
- **T=0.7 vs image**: significant after BH-FDR (q = 0.05) at R ∈ {20 m, 25 m, 30 m, 35 m, 40 m, 45 m, 75 m, 100 m, 125 m}.

## T=0.3 vs T=0.7

Detection sets:

- A (T=0.3): `outputs/55maps-text-high-t0.3-generalisation/verified/verified_detections.geojson`
- B (T=0.7): `outputs/55maps-text-high-generalisation/verified/verified_detections.geojson`

| R (m) | F1 A | F1 B | ΔF1 (A−B) [95 % CI] | p (raw) | p (BH) | sig (q=0.05) | W/L/T |
|------:|-----:|-----:|--------------------:|--------:|-------:|:------------:|------:|
|   20 | 0.6305 | 0.6247 | +0.0058 [-0.0044, +0.0159] | 0.259 | 0.259 | ns | 390/360/7791 |
|   25 | 0.7187 | 0.7091 | +0.0096 [+0.0008, +0.0186] | 0.037 | 0.047 | **\*** | 384/331/7826 |
|   30 | 0.7640 | 0.7555 | +0.0085 [+0.0002, +0.0170] | 0.054 | 0.061 | ns | 365/312/7864 |
|   35 | 0.7867 | 0.7760 | +0.0107 [+0.0025, +0.0191] | 0.014 | 0.020 | **\*** | 365/301/7875 |
|   40 | 0.7961 | 0.7852 | +0.0109 [+0.0030, +0.0192] | 0.009 | 0.015 | **\*** | 360/297/7884 |
|   45 | 0.8027 | 0.7888 | +0.0139 [+0.0059, +0.0221] | 0.001 | 0.002 | **\*** | 366/294/7881 |
|   50 | 0.8437 | 0.8260 | +0.0177 [+0.0102, +0.0254] | <0.001 | <0.001 | **\*** | 383/281/7877 |
|   75 | 0.8468 | 0.8285 | +0.0183 [+0.0108, +0.0260] | <0.001 | <0.001 | **\*** | 382/271/7888 |
|  100 | 0.8485 | 0.8308 | +0.0177 [+0.0104, +0.0252] | <0.001 | <0.001 | **\*** | 381/269/7891 |
|  125 | 0.8500 | 0.8322 | +0.0178 [+0.0104, +0.0254] | <0.001 | <0.001 | **\*** | 384/272/7885 |

Notes — wins / losses / ties are tile-level comparisons (per-tile F1_A vs F1_B); ΔF1 is the aggregate micro-average difference; CI is a 10 000-iteration tile-level paired bootstrap.

## T=0.3 vs image

Detection sets:

- A (T=0.3): `outputs/55maps-text-high-t0.3-generalisation/verified/verified_detections.geojson`
- B (image): `outputs/55maps-image-generalisation/verified/verified_detections.geojson`

| R (m) | F1 A | F1 B | ΔF1 (A−B) [95 % CI] | p (raw) | p (BH) | sig (q=0.05) | W/L/T |
|------:|-----:|-----:|--------------------:|--------:|-------:|:------------:|------:|
|   20 | 0.6305 | 0.5070 | +0.1236 [+0.1094, +0.1377] | <0.001 | <0.001 | **\*** | 808/397/7336 |
|   25 | 0.7187 | 0.6196 | +0.0991 [+0.0859, +0.1119] | <0.001 | <0.001 | **\*** | 757/424/7360 |
|   30 | 0.7640 | 0.6872 | +0.0768 [+0.0651, +0.0886] | <0.001 | <0.001 | **\*** | 685/427/7429 |
|   35 | 0.7867 | 0.7261 | +0.0606 [+0.0495, +0.0716] | <0.001 | <0.001 | **\*** | 648/441/7452 |
|   40 | 0.7961 | 0.7501 | +0.0460 [+0.0351, +0.0567] | <0.001 | <0.001 | **\*** | 600/464/7477 |
|   45 | 0.8027 | 0.7644 | +0.0384 [+0.0279, +0.0485] | <0.001 | <0.001 | **\*** | 577/468/7496 |
|   50 | 0.8437 | 0.8317 | +0.0119 [+0.0026, +0.0211] | 0.012 | 0.017 | **\*** | 495/529/7517 |
|   75 | 0.8468 | 0.8477 | -0.0009 [-0.0097, +0.0078] | 0.848 | 0.848 | ns | 458/555/7528 |
|  100 | 0.8485 | 0.8521 | -0.0035 [-0.0122, +0.0050] | 0.423 | 0.470 | ns | 443/565/7533 |
|  125 | 0.8500 | 0.8538 | -0.0038 [-0.0125, +0.0046] | 0.386 | 0.470 | ns | 442/568/7531 |

Notes — wins / losses / ties are tile-level comparisons (per-tile F1_A vs F1_B); ΔF1 is the aggregate micro-average difference; CI is a 10 000-iteration tile-level paired bootstrap.

## T=0.7 vs image

Detection sets:

- A (T=0.7): `outputs/55maps-text-high-generalisation/verified/verified_detections.geojson`
- B (image): `outputs/55maps-image-generalisation/verified/verified_detections.geojson`

| R (m) | F1 A | F1 B | ΔF1 (A−B) [95 % CI] | p (raw) | p (BH) | sig (q=0.05) | W/L/T |
|------:|-----:|-----:|--------------------:|--------:|-------:|:------------:|------:|
|   20 | 0.6247 | 0.5070 | +0.1178 [+0.1037, +0.1317] | <0.001 | <0.001 | **\*** | 794/415/7332 |
|   25 | 0.7091 | 0.6196 | +0.0895 [+0.0764, +0.1027] | <0.001 | <0.001 | **\*** | 739/455/7347 |
|   30 | 0.7555 | 0.6872 | +0.0683 [+0.0560, +0.0806] | <0.001 | <0.001 | **\*** | 666/465/7410 |
|   35 | 0.7760 | 0.7261 | +0.0499 [+0.0384, +0.0614] | <0.001 | <0.001 | **\*** | 619/492/7430 |
|   40 | 0.7852 | 0.7501 | +0.0351 [+0.0242, +0.0462] | <0.001 | <0.001 | **\*** | 571/515/7455 |
|   45 | 0.7888 | 0.7644 | +0.0244 [+0.0138, +0.0349] | <0.001 | <0.001 | **\*** | 535/526/7480 |
|   50 | 0.8260 | 0.8317 | -0.0057 [-0.0154, +0.0039] | 0.239 | 0.239 | ns | 439/602/7500 |
|   75 | 0.8285 | 0.8477 | -0.0191 [-0.0283, -0.0099] | <0.001 | <0.001 | **\*** | 405/635/7501 |
|  100 | 0.8308 | 0.8521 | -0.0212 [-0.0304, -0.0121] | <0.001 | <0.001 | **\*** | 394/645/7502 |
|  125 | 0.8322 | 0.8538 | -0.0216 [-0.0307, -0.0126] | <0.001 | <0.001 | **\*** | 393/647/7501 |

Notes — wins / losses / ties are tile-level comparisons (per-tile F1_A vs F1_B); ΔF1 is the aggregate micro-average difference; CI is a 10 000-iteration tile-level paired bootstrap.

## Reproducibility

- Driver: `scripts/paired_permutation_corrected_55maps.py`
- Summary builder: `scripts/build_pairwise_perm_v2_summary.py`
- Per-pair JSON outputs in `paired-<a>-vs-<b>/permutation-R<R>m.json`
- Per-pair summary in `paired-<a>-vs-<b>/summary.json`
- Detection inputs are unchanged from each run's
  `outputs/<run>/verified/verified_detections.geojson`; the corrected
  ground truth is rebuilt at each R from the run's review CSVs.
