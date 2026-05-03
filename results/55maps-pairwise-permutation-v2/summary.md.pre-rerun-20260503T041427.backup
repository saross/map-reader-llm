# Pairwise paired-permutation tests — 55-map corrected detection sets

**Timestamp**: 2026-05-03T00:51:27.322209+00:00
**Pairs**: T=0.3 vs T=0.7, T=0.3 vs image, T=0.7 vs image, T=0.3 vs T=MIN, T=0.7 vs T=MIN, image vs T=MIN
**Buffers**: 20, 25, 30, 35, 40, 45, 50, 75, 100, 125 m
**Permutations**: 10 000 per cell, seed = 42, two-sided
**Bootstrap CI**: 10 000 tile-level paired iterations, seed = 42
**FDR correction**: Benjamini-Hochberg within each pair, q = 0.05
**Methodology**: Approach B — extended-GT-at-R Hungarian matching; per-side
extended GT identical to each run's `corrected-f1-multi-buffer/summary.json`.
**Test statistic**: aggregate (micro-average) F1 difference; tile-swap
permutations preserve pairing across the 8 541 evaluation tiles.

## Headline at canonical R = 50 m

- **T=0.3 vs T=0.7** at R = 50 m: ΔF1 = +0.0162 [+0.0089, +0.0238]; raw p = <0.001, BH-FDR p = <0.001 (significant at q = 0.05 within pair).
- **T=0.3 vs image** at R = 50 m: ΔF1 = +0.0119 [+0.0026, +0.0211]; raw p = 0.012, BH-FDR p = 0.017 (significant at q = 0.05 within pair).
- **T=0.7 vs image** at R = 50 m: ΔF1 = -0.0043 [-0.0139, +0.0052]; raw p = 0.373, BH-FDR p = 0.373 (ns at q = 0.05 within pair).
- **T=0.3 vs T=MIN** at R = 50 m: ΔF1 = +0.0473 [+0.0379, +0.0568]; raw p = <0.001, BH-FDR p = <0.001 (significant at q = 0.05 within pair).
- **T=0.7 vs T=MIN** at R = 50 m: ΔF1 = +0.0308 [+0.0214, +0.0403]; raw p = <0.001, BH-FDR p = <0.001 (significant at q = 0.05 within pair).
- **image vs T=MIN** at R = 50 m: ΔF1 = +0.0353 [+0.0245, +0.0464]; raw p = <0.001, BH-FDR p = <0.001 (significant at q = 0.05 within pair).

## Buffers surviving BH-FDR correction (q = 0.05) within pair

- **T=0.3 vs T=0.7**: significant after BH-FDR (q = 0.05) at R ∈ {35 m, 40 m, 45 m, 50 m, 75 m, 100 m, 125 m}.
- **T=0.3 vs image**: significant after BH-FDR (q = 0.05) at R ∈ {20 m, 25 m, 30 m, 35 m, 40 m, 45 m, 50 m}.
- **T=0.7 vs image**: significant after BH-FDR (q = 0.05) at R ∈ {20 m, 25 m, 30 m, 35 m, 40 m, 45 m, 75 m, 100 m, 125 m}.
- **T=0.3 vs T=MIN**: significant after BH-FDR (q = 0.05) at R ∈ {25 m, 30 m, 35 m, 40 m, 45 m, 50 m, 75 m, 100 m, 125 m}.
- **T=0.7 vs T=MIN**: significant after BH-FDR (q = 0.05) at R ∈ {25 m, 30 m, 35 m, 40 m, 45 m, 50 m, 75 m, 100 m, 125 m}.
- **image vs T=MIN**: significant after BH-FDR (q = 0.05) at R ∈ {20 m, 25 m, 30 m, 35 m, 50 m, 75 m, 100 m, 125 m}.

## T=0.3 vs T=0.7

Detection sets:

- A (T=0.3): `outputs/55maps-text-high-t0.3-generalisation/verified/verified_detections.geojson`
- B (T=0.7): `outputs/55maps-text-high-generalisation/verified/verified_detections.geojson`

| R (m) | F1 A | F1 B | ΔF1 (A−B) [95 % CI] | p (raw) | p (BH) | sig (q=0.05) | W/L/T |
|------:|-----:|-----:|--------------------:|--------:|-------:|:------------:|------:|
|   20 | 0.6307 | 0.6259 | +0.0048 [-0.0053, +0.0148] | 0.348 | 0.348 | ns | 387/363/7791 |
|   25 | 0.7189 | 0.7101 | +0.0088 [-0.0001, +0.0178] | 0.054 | 0.068 | ns | 379/333/7829 |
|   30 | 0.7642 | 0.7568 | +0.0074 [-0.0010, +0.0158] | 0.087 | 0.096 | ns | 360/313/7868 |
|   35 | 0.7868 | 0.7776 | +0.0092 [+0.0010, +0.0175] | 0.029 | 0.041 | **\*** | 360/303/7878 |
|   40 | 0.7963 | 0.7866 | +0.0096 [+0.0018, +0.0178] | 0.018 | 0.029 | **\*** | 355/299/7887 |
|   45 | 0.8029 | 0.7902 | +0.0126 [+0.0047, +0.0208] | 0.003 | 0.006 | **\*** | 361/296/7884 |
|   50 | 0.8436 | 0.8273 | +0.0162 [+0.0089, +0.0238] | <0.001 | <0.001 | **\*** | 378/284/7879 |
|   75 | 0.8467 | 0.8300 | +0.0168 [+0.0094, +0.0242] | <0.001 | <0.001 | **\*** | 378/273/7890 |
|  100 | 0.8484 | 0.8324 | +0.0161 [+0.0088, +0.0234] | <0.001 | <0.001 | **\*** | 377/272/7892 |
|  125 | 0.8499 | 0.8338 | +0.0161 [+0.0089, +0.0235] | <0.001 | <0.001 | **\*** | 380/275/7886 |

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
|   20 | 0.6259 | 0.5069 | +0.1190 [+0.1050, +0.1329] | <0.001 | <0.001 | **\*** | 795/411/7335 |
|   25 | 0.7101 | 0.6196 | +0.0905 [+0.0777, +0.1037] | <0.001 | <0.001 | **\*** | 740/451/7350 |
|   30 | 0.7568 | 0.6871 | +0.0696 [+0.0575, +0.0819] | <0.001 | <0.001 | **\*** | 666/460/7415 |
|   35 | 0.7776 | 0.7260 | +0.0516 [+0.0403, +0.0630] | <0.001 | <0.001 | **\*** | 620/487/7434 |
|   40 | 0.7866 | 0.7501 | +0.0366 [+0.0258, +0.0477] | <0.001 | <0.001 | **\*** | 574/509/7458 |
|   45 | 0.7902 | 0.7643 | +0.0259 [+0.0154, +0.0364] | <0.001 | <0.001 | **\*** | 538/519/7484 |
|   50 | 0.8273 | 0.8316 | -0.0043 [-0.0139, +0.0052] | 0.373 | 0.373 | ns | 441/596/7504 |
|   75 | 0.8300 | 0.8476 | -0.0176 [-0.0267, -0.0084] | <0.001 | <0.001 | **\*** | 407/629/7505 |
|  100 | 0.8324 | 0.8520 | -0.0196 [-0.0286, -0.0105] | <0.001 | <0.001 | **\*** | 396/638/7507 |
|  125 | 0.8338 | 0.8537 | -0.0200 [-0.0288, -0.0111] | <0.001 | <0.001 | **\*** | 395/640/7506 |

Notes — wins / losses / ties are tile-level comparisons (per-tile F1_A vs F1_B); ΔF1 is the aggregate micro-average difference; CI is a 10 000-iteration tile-level paired bootstrap.

## T=0.3 vs T=MIN

Detection sets:

- A (T=0.3): `outputs/55maps-text-high-t0.3-generalisation/verified/verified_detections.geojson`
- B (T=MIN): `outputs/55maps-text-min-generalisation/verified/verified_detections.geojson`

| R (m) | F1 A | F1 B | ΔF1 (A−B) [95 % CI] | p (raw) | p (BH) | sig (q=0.05) | W/L/T |
|------:|-----:|-----:|--------------------:|--------:|-------:|:------------:|------:|
|   20 | 0.6305 | 0.6199 | +0.0107 [-0.0017, +0.0232] | 0.090 | 0.090 | ns | 541/460/7540 |
|   25 | 0.7187 | 0.6922 | +0.0266 [+0.0148, +0.0381] | <0.001 | <0.001 | **\*** | 564/418/7559 |
|   30 | 0.7640 | 0.7296 | +0.0344 [+0.0234, +0.0454] | <0.001 | <0.001 | **\*** | 574/388/7579 |
|   35 | 0.7867 | 0.7486 | +0.0380 [+0.0274, +0.0485] | <0.001 | <0.001 | **\*** | 575/368/7598 |
|   40 | 0.7961 | 0.7561 | +0.0401 [+0.0300, +0.0502] | <0.001 | <0.001 | **\*** | 578/359/7604 |
|   45 | 0.8027 | 0.7598 | +0.0429 [+0.0328, +0.0529] | <0.001 | <0.001 | **\*** | 581/350/7610 |
|   50 | 0.8437 | 0.7964 | +0.0473 [+0.0379, +0.0568] | <0.001 | <0.001 | **\*** | 602/325/7614 |
|   75 | 0.8468 | 0.7991 | +0.0477 [+0.0385, +0.0570] | <0.001 | <0.001 | **\*** | 604/316/7621 |
|  100 | 0.8485 | 0.8003 | +0.0482 [+0.0391, +0.0575] | <0.001 | <0.001 | **\*** | 607/311/7623 |
|  125 | 0.8500 | 0.8007 | +0.0493 [+0.0401, +0.0585] | <0.001 | <0.001 | **\*** | 613/310/7618 |

Notes — wins / losses / ties are tile-level comparisons (per-tile F1_A vs F1_B); ΔF1 is the aggregate micro-average difference; CI is a 10 000-iteration tile-level paired bootstrap.

## T=0.7 vs T=MIN

Detection sets:

- A (T=0.7): `outputs/55maps-text-high-generalisation/verified/verified_detections.geojson`
- B (T=MIN): `outputs/55maps-text-min-generalisation/verified/verified_detections.geojson`

| R (m) | F1 A | F1 B | ΔF1 (A−B) [95 % CI] | p (raw) | p (BH) | sig (q=0.05) | W/L/T |
|------:|-----:|-----:|--------------------:|--------:|-------:|:------------:|------:|
|   20 | 0.6259 | 0.6200 | +0.0059 [-0.0063, +0.0182] | 0.355 | 0.355 | ns | 500/459/7582 |
|   25 | 0.7101 | 0.6923 | +0.0178 [+0.0063, +0.0293] | 0.002 | 0.002 | **\*** | 533/430/7578 |
|   30 | 0.7568 | 0.7297 | +0.0270 [+0.0161, +0.0380] | <0.001 | <0.001 | **\*** | 535/388/7618 |
|   35 | 0.7776 | 0.7488 | +0.0289 [+0.0185, +0.0392] | <0.001 | <0.001 | **\*** | 535/366/7640 |
|   40 | 0.7866 | 0.7562 | +0.0304 [+0.0200, +0.0408] | <0.001 | <0.001 | **\*** | 537/357/7647 |
|   45 | 0.7902 | 0.7599 | +0.0303 [+0.0201, +0.0404] | <0.001 | <0.001 | **\*** | 533/356/7652 |
|   50 | 0.8273 | 0.7965 | +0.0308 [+0.0214, +0.0403] | <0.001 | <0.001 | **\*** | 547/353/7641 |
|   75 | 0.8300 | 0.7990 | +0.0310 [+0.0216, +0.0404] | <0.001 | <0.001 | **\*** | 543/349/7649 |
|  100 | 0.8324 | 0.8002 | +0.0322 [+0.0229, +0.0417] | <0.001 | <0.001 | **\*** | 551/345/7645 |
|  125 | 0.8338 | 0.8006 | +0.0331 [+0.0238, +0.0426] | <0.001 | <0.001 | **\*** | 555/342/7644 |

Notes — wins / losses / ties are tile-level comparisons (per-tile F1_A vs F1_B); ΔF1 is the aggregate micro-average difference; CI is a 10 000-iteration tile-level paired bootstrap.

## image vs T=MIN

Detection sets:

- A (image): `outputs/55maps-image-generalisation/verified/verified_detections.geojson`
- B (T=MIN): `outputs/55maps-text-min-generalisation/verified/verified_detections.geojson`

| R (m) | F1 A | F1 B | ΔF1 (A−B) [95 % CI] | p (raw) | p (BH) | sig (q=0.05) | W/L/T |
|------:|-----:|-----:|--------------------:|--------:|-------:|:------------:|------:|
|   20 | 0.5070 | 0.6199 | -0.1129 [-0.1286, -0.0968] | <0.001 | <0.001 | **\*** | 516/795/7230 |
|   25 | 0.6196 | 0.6922 | -0.0725 [-0.0873, -0.0578] | <0.001 | <0.001 | **\*** | 580/731/7230 |
|   30 | 0.6872 | 0.7296 | -0.0424 [-0.0559, -0.0285] | <0.001 | <0.001 | **\*** | 606/659/7276 |
|   35 | 0.7261 | 0.7486 | -0.0225 [-0.0354, -0.0097] | <0.001 | <0.001 | **\*** | 626/610/7305 |
|   40 | 0.7501 | 0.7561 | -0.0059 [-0.0185, +0.0064] | 0.341 | 0.379 | ns | 653/564/7324 |
|   45 | 0.7644 | 0.7598 | +0.0046 [-0.0074, +0.0166] | 0.451 | 0.451 | ns | 670/538/7333 |
|   50 | 0.8317 | 0.7964 | +0.0353 [+0.0245, +0.0464] | <0.001 | <0.001 | **\*** | 756/446/7339 |
|   75 | 0.8477 | 0.7991 | +0.0486 [+0.0380, +0.0592] | <0.001 | <0.001 | **\*** | 789/411/7341 |
|  100 | 0.8521 | 0.8003 | +0.0518 [+0.0414, +0.0624] | <0.001 | <0.001 | **\*** | 809/396/7336 |
|  125 | 0.8538 | 0.8007 | +0.0531 [+0.0428, +0.0637] | <0.001 | <0.001 | **\*** | 817/397/7327 |

Notes — wins / losses / ties are tile-level comparisons (per-tile F1_A vs F1_B); ΔF1 is the aggregate micro-average difference; CI is a 10 000-iteration tile-level paired bootstrap.

## Reproducibility

- Driver: `scripts/paired_permutation_corrected_55maps.py`
- Summary builder: `scripts/build_pairwise_perm_v2_summary.py`
- Per-pair JSON outputs in `paired-<a>-vs-<b>/permutation-R<R>m.json`
- Per-pair summary in `paired-<a>-vs-<b>/summary.json`
- Detection inputs are unchanged from each run's
  `outputs/<run>/verified/verified_detections.geojson`; the corrected
  ground truth is rebuilt at each R from the run's review CSVs.
