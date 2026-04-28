# Pairwise paired-permutation tests — 55-map corrected detection sets

**Timestamp**: 2026-04-28T01:00:54.886256+00:00
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

- **T=0.3 vs T=0.7** at R = 50 m: ΔF1 = +0.0177 [+0.0102, +0.0254]; raw p = <0.001, BH-FDR p = <0.001 (significant at q = 0.05 within pair).
- **T=0.3 vs image** at R = 50 m: ΔF1 = +0.0119 [+0.0026, +0.0211]; raw p = 0.012, BH-FDR p = 0.017 (significant at q = 0.05 within pair).
- **T=0.7 vs image** at R = 50 m: ΔF1 = -0.0057 [-0.0154, +0.0039]; raw p = 0.239, BH-FDR p = 0.239 (ns at q = 0.05 within pair).
- **T=0.3 vs T=MIN** at R = 50 m: ΔF1 = +0.0473 [+0.0379, +0.0568]; raw p = <0.001, BH-FDR p = <0.001 (significant at q = 0.05 within pair).
- **T=0.7 vs T=MIN** at R = 50 m: ΔF1 = +0.0296 [+0.0200, +0.0392]; raw p = <0.001, BH-FDR p = <0.001 (significant at q = 0.05 within pair).
- **image vs T=MIN** at R = 50 m: ΔF1 = +0.0353 [+0.0245, +0.0464]; raw p = <0.001, BH-FDR p = <0.001 (significant at q = 0.05 within pair).

## Buffers surviving BH-FDR correction (q = 0.05) within pair

- **T=0.3 vs T=0.7**: significant after BH-FDR (q = 0.05) at R ∈ {25 m, 35 m, 40 m, 45 m, 50 m, 75 m, 100 m, 125 m}.
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
|   20 | 0.6247 | 0.6199 | +0.0049 [-0.0073, +0.0174] | 0.448 | 0.448 | ns | 497/463/7581 |
|   25 | 0.7091 | 0.6922 | +0.0170 [+0.0054, +0.0287] | 0.003 | 0.004 | **\*** | 531/434/7576 |
|   30 | 0.7555 | 0.7296 | +0.0259 [+0.0149, +0.0369] | <0.001 | <0.001 | **\*** | 534/392/7615 |
|   35 | 0.7760 | 0.7486 | +0.0273 [+0.0170, +0.0378] | <0.001 | <0.001 | **\*** | 533/370/7638 |
|   40 | 0.7852 | 0.7561 | +0.0291 [+0.0187, +0.0396] | <0.001 | <0.001 | **\*** | 535/361/7645 |
|   45 | 0.7888 | 0.7598 | +0.0290 [+0.0187, +0.0393] | <0.001 | <0.001 | **\*** | 531/359/7651 |
|   50 | 0.8260 | 0.7964 | +0.0296 [+0.0200, +0.0392] | <0.001 | <0.001 | **\*** | 545/355/7641 |
|   75 | 0.8285 | 0.7991 | +0.0294 [+0.0199, +0.0389] | <0.001 | <0.001 | **\*** | 540/352/7649 |
|  100 | 0.8308 | 0.8003 | +0.0305 [+0.0211, +0.0399] | <0.001 | <0.001 | **\*** | 547/348/7646 |
|  125 | 0.8322 | 0.8007 | +0.0315 [+0.0221, +0.0409] | <0.001 | <0.001 | **\*** | 551/345/7645 |

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

## F1 tier rankings (greedy clique, BH-FDR within-buffer family)

### Methodology note

Tiers built via greedy clique on BH-FDR-corrected paired-permutation tests within the 6-pair family at each buffer (matrix-tier convention from `results/leaderboard/per-architecture/README.md`). Each run is added to the current tier if it is BH-adjusted indistinguishable (q ≥ threshold) from ALL current tier members; otherwise it starts a new tier. q=0.05 is the base threshold; q=0.01 is the sensitivity pass.

Source: per-pair JSONs in `paired-{t0.3-vs-t0.7,t0.3-vs-image,t0.7-vs-image,t0.3-vs-tmin,t0.7-vs-tmin,image-vs-tmin}/permutation-R{50,100}m.json`. F1 + 95 % CI from `results/<run>/corrected-f1-multi-buffer/summary.json`.

### R = 50 m (canonical operating point)

F1 ranking: T=0.3 > image > T=0.7 > T=MIN

#### Pairwise BH-FDR-adjusted p-values (6-pair family at R = 50 m)

| Pair | ΔF1 | BH-adj p | Sig at q=0.05 | Sig at q=0.01 |
|---|---:|---:|:--:|:--:|
| T=0.3 vs T=0.7 | +0.018 | <0.001 | ✓ | ✓ |
| T=0.3 vs image | +0.012 | 0.014 | ✓ | ✗ |
| T=0.7 vs image | −0.006 | 0.239 | ✗ | ✗ |
| T=0.3 vs T=MIN | +0.047 | <0.001 | ✓ | ✓ |
| T=0.7 vs T=MIN | +0.030 | <0.001 | ✓ | ✓ |
| image vs T=MIN | +0.035 | <0.001 | ✓ | ✓ |

#### Tier table at q = 0.05 (base)

| Tier | Run | F1 [95 % CI] |
|:---:|:---|:---|
| **1** | T=0.3 (text-HIGH) | **0.8437** [0.8344, 0.8524] |
| **2** | image | 0.8317 [0.8225, 0.8407] |
| **2** | T=0.7 (text-HIGH) | 0.8260 [0.8159, 0.8357] |
| **3** | T=MIN | 0.7964 [0.7851, 0.8072] |

T=0.3 alone in Tier 1 — significantly above image, T=0.7 and T=MIN. image and T=0.7 indistinguishable at q=0.05 (BH-adj p=0.239). T=MIN significantly below all three.

#### Tier table at q = 0.01 (sensitivity)

| Tier | Run | F1 [95 % CI] |
|:---:|:---|:---|
| **1** | T=0.3 (text-HIGH) | **0.8437** [0.8344, 0.8524] |
| **1** | image | 0.8317 [0.8225, 0.8407] |
| **2** | T=0.7 (text-HIGH) | 0.8260 [0.8159, 0.8357] |
| **3** | T=MIN | 0.7964 [0.7851, 0.8072] |

At the stricter q=0.01, the T=0.3-vs-image distinction collapses (BH-adj p=0.014 > 0.01) — image moves up to Tier 1. T=0.7 now alone in Tier 2.

### R = 100 m

F1 ranking: image > T=0.3 > T=0.7 > T=MIN — rank reversal at the top vs R=50 m.

#### Pairwise BH-FDR-adjusted p-values (6-pair family at R = 100 m)

| Pair | ΔF1 | BH-adj p | Sig at q=0.05 | Sig at q=0.01 |
|---|---:|---:|:--:|:--:|
| T=0.3 vs T=0.7 | +0.018 | <0.001 | ✓ | ✓ |
| T=0.3 vs image | −0.004 | 0.423 | ✗ | ✗ |
| T=0.7 vs image | −0.021 | <0.001 | ✓ | ✓ |
| T=0.3 vs T=MIN | +0.048 | <0.001 | ✓ | ✓ |
| T=0.7 vs T=MIN | +0.030 | <0.001 | ✓ | ✓ |
| image vs T=MIN | +0.052 | <0.001 | ✓ | ✓ |

#### Tier table at q = 0.05 (and q = 0.01 — identical)

| Tier | Run | F1 [95 % CI] |
|:---:|:---|:---|
| **1** | image | **0.8521** [0.8434, 0.8602] |
| **1** | T=0.3 (text-HIGH) | 0.8485 [0.8394, 0.8571] |
| **2** | T=0.7 (text-HIGH) | 0.8308 [0.8209, 0.8404] |
| **3** | T=MIN | 0.8003 [0.7892, 0.8110] |

image and T=0.3 indistinguishable at R=100 m (BH-adj p=0.423). T=0.7 significantly below both. T=MIN significantly below T=0.7. Tier structure stable across q=0.05 and q=0.01 — the only marginal pair at R=50 m has fully collapsed at R=100 m.

### Tier mobility between R = 50 m and R = 100 m

| Run | R=50 m tier (q=0.05) | R=100 m tier | Δ |
|---|:---:|:---:|---|
| **image** | 2 | **1** | promoted |
| T=0.3 | 1 | 1 | unchanged |
| T=0.7 | 2 | 2 | unchanged |
| T=MIN | 3 | 3 | unchanged |

The buffer-rank-reversal documented in **Obs 291** and **Obs 292** (text wins at tight buffer; image overtakes at wider buffer) shows up directly in the tier structure: image rises from Tier 2 to Tier 1 between R=50 m and R=100 m. T=0.3 holds the top throughout (joint at R=100 m); T=0.7 sits at Tier 2 throughout; T=MIN is bottom throughout.

### Paper-relevant summary

- **R=50 m operating point (q=0.05)**: T=0.3 is the unambiguous winner, alone in Tier 1.
- **R=100 m practitioner-broader buffer**: image catches up to T=0.3; they share Tier 1.
- **T=0.7 sits in Tier 2 at every buffer** — never the leader, never the bottom, statistically distinguishable from both extremes at canonical R ≥ 50 m.
- **T=MIN is always Tier 3** — significantly below everything else at every buffer; the in-corpus confirmation that HIGH thinking earns its tokens (see Obs 297).

## Reproducibility

- Driver: `scripts/paired_permutation_corrected_55maps.py`
- Summary builder: `scripts/build_pairwise_perm_v2_summary.py`
- Per-pair JSON outputs in `paired-<a>-vs-<b>/permutation-R<R>m.json`
- Per-pair summary in `paired-<a>-vs-<b>/summary.json`
- Detection inputs are unchanged from each run's
  `outputs/<run>/verified/verified_detections.geojson`; the corrected
  ground truth is rebuilt at each R from the run's review CSVs.
