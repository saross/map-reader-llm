# Pairwise paired-permutation tests — 55-map corrected detection sets

**Timestamp**: 2026-05-03T04:27:23.164943+00:00
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
- **T=0.3 vs image** at R = 50 m: ΔF1 = +0.0102 [+0.0009, +0.0193]; raw p = 0.031, BH-FDR p = 0.045 (significant at q = 0.05 within pair).
- **T=0.7 vs image** at R = 50 m: ΔF1 = -0.0060 [-0.0156, +0.0035]; raw p = 0.215, BH-FDR p = 0.215 (ns at q = 0.05 within pair).
- **T=0.3 vs T=MIN** at R = 50 m: ΔF1 = +0.0467 [+0.0374, +0.0562]; raw p = <0.001, BH-FDR p = <0.001 (significant at q = 0.05 within pair).
- **T=0.7 vs T=MIN** at R = 50 m: ΔF1 = +0.0305 [+0.0210, +0.0400]; raw p = <0.001, BH-FDR p = <0.001 (significant at q = 0.05 within pair).
- **image vs T=MIN** at R = 50 m: ΔF1 = +0.0365 [+0.0256, +0.0476]; raw p = <0.001, BH-FDR p = <0.001 (significant at q = 0.05 within pair).

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
|   20 | 0.6307 | 0.5080 | +0.1227 [+0.1084, +0.1367] | <0.001 | <0.001 | **\*** | 804/398/7339 |
|   25 | 0.7189 | 0.6209 | +0.0980 [+0.0847, +0.1107] | <0.001 | <0.001 | **\*** | 752/425/7364 |
|   30 | 0.7642 | 0.6886 | +0.0756 [+0.0638, +0.0873] | <0.001 | <0.001 | **\*** | 679/429/7433 |
|   35 | 0.7868 | 0.7276 | +0.0592 [+0.0480, +0.0702] | <0.001 | <0.001 | **\*** | 641/442/7458 |
|   40 | 0.7963 | 0.7518 | +0.0444 [+0.0336, +0.0552] | <0.001 | <0.001 | **\*** | 592/465/7484 |
|   45 | 0.8029 | 0.7660 | +0.0368 [+0.0264, +0.0470] | <0.001 | <0.001 | **\*** | 569/469/7503 |
|   50 | 0.8436 | 0.8333 | +0.0102 [+0.0009, +0.0193] | 0.031 | 0.045 | **\*** | 487/530/7524 |
|   75 | 0.8467 | 0.8492 | -0.0025 [-0.0114, +0.0061] | 0.570 | 0.570 | ns | 450/556/7535 |
|  100 | 0.8484 | 0.8536 | -0.0052 [-0.0139, +0.0034] | 0.242 | 0.269 | ns | 435/566/7540 |
|  125 | 0.8499 | 0.8554 | -0.0054 [-0.0141, +0.0030] | 0.216 | 0.269 | ns | 434/569/7538 |

Notes — wins / losses / ties are tile-level comparisons (per-tile F1_A vs F1_B); ΔF1 is the aggregate micro-average difference; CI is a 10 000-iteration tile-level paired bootstrap.

## T=0.7 vs image

Detection sets:

- A (T=0.7): `outputs/55maps-text-high-generalisation/verified/verified_detections.geojson`
- B (image): `outputs/55maps-image-generalisation/verified/verified_detections.geojson`

| R (m) | F1 A | F1 B | ΔF1 (A−B) [95 % CI] | p (raw) | p (BH) | sig (q=0.05) | W/L/T |
|------:|-----:|-----:|--------------------:|--------:|-------:|:------------:|------:|
|   20 | 0.6259 | 0.5080 | +0.1179 [+0.1039, +0.1316] | <0.001 | <0.001 | **\*** | 791/414/7336 |
|   25 | 0.7101 | 0.6209 | +0.0892 [+0.0763, +0.1023] | <0.001 | <0.001 | **\*** | 736/454/7351 |
|   30 | 0.7568 | 0.6886 | +0.0682 [+0.0560, +0.0805] | <0.001 | <0.001 | **\*** | 661/463/7417 |
|   35 | 0.7776 | 0.7276 | +0.0500 [+0.0387, +0.0615] | <0.001 | <0.001 | **\*** | 614/489/7438 |
|   40 | 0.7866 | 0.7518 | +0.0348 [+0.0240, +0.0461] | <0.001 | <0.001 | **\*** | 568/511/7462 |
|   45 | 0.7902 | 0.7660 | +0.0242 [+0.0136, +0.0348] | <0.001 | <0.001 | **\*** | 532/521/7488 |
|   50 | 0.8273 | 0.8333 | -0.0060 [-0.0156, +0.0035] | 0.215 | 0.215 | ns | 434/598/7509 |
|   75 | 0.8300 | 0.8492 | -0.0193 [-0.0284, -0.0101] | <0.001 | <0.001 | **\*** | 400/631/7510 |
|  100 | 0.8324 | 0.8536 | -0.0212 [-0.0302, -0.0121] | <0.001 | <0.001 | **\*** | 389/640/7512 |
|  125 | 0.8338 | 0.8554 | -0.0216 [-0.0304, -0.0126] | <0.001 | <0.001 | **\*** | 388/642/7511 |

Notes — wins / losses / ties are tile-level comparisons (per-tile F1_A vs F1_B); ΔF1 is the aggregate micro-average difference; CI is a 10 000-iteration tile-level paired bootstrap.

## T=0.3 vs T=MIN

Detection sets:

- A (T=0.3): `outputs/55maps-text-high-t0.3-generalisation/verified/verified_detections.geojson`
- B (T=MIN): `outputs/55maps-text-min-generalisation/verified/verified_detections.geojson`

| R (m) | F1 A | F1 B | ΔF1 (A−B) [95 % CI] | p (raw) | p (BH) | sig (q=0.05) | W/L/T |
|------:|-----:|-----:|--------------------:|--------:|-------:|:------------:|------:|
|   20 | 0.6307 | 0.6202 | +0.0105 [-0.0019, +0.0230] | 0.093 | 0.093 | ns | 539/460/7542 |
|   25 | 0.7189 | 0.6925 | +0.0264 [+0.0147, +0.0379] | <0.001 | <0.001 | **\*** | 563/418/7560 |
|   30 | 0.7642 | 0.7298 | +0.0343 [+0.0233, +0.0453] | <0.001 | <0.001 | **\*** | 573/388/7580 |
|   35 | 0.7868 | 0.7489 | +0.0379 [+0.0273, +0.0484] | <0.001 | <0.001 | **\*** | 574/368/7599 |
|   40 | 0.7963 | 0.7563 | +0.0399 [+0.0299, +0.0500] | <0.001 | <0.001 | **\*** | 577/359/7605 |
|   45 | 0.8029 | 0.7600 | +0.0428 [+0.0327, +0.0528] | <0.001 | <0.001 | **\*** | 580/350/7611 |
|   50 | 0.8436 | 0.7968 | +0.0467 [+0.0374, +0.0562] | <0.001 | <0.001 | **\*** | 599/326/7616 |
|   75 | 0.8467 | 0.7993 | +0.0474 [+0.0382, +0.0567] | <0.001 | <0.001 | **\*** | 602/316/7623 |
|  100 | 0.8484 | 0.8005 | +0.0479 [+0.0388, +0.0572] | <0.001 | <0.001 | **\*** | 605/311/7625 |
|  125 | 0.8499 | 0.8009 | +0.0490 [+0.0398, +0.0581] | <0.001 | <0.001 | **\*** | 611/310/7620 |

Notes — wins / losses / ties are tile-level comparisons (per-tile F1_A vs F1_B); ΔF1 is the aggregate micro-average difference; CI is a 10 000-iteration tile-level paired bootstrap.

## T=0.7 vs T=MIN

Detection sets:

- A (T=0.7): `outputs/55maps-text-high-generalisation/verified/verified_detections.geojson`
- B (T=MIN): `outputs/55maps-text-min-generalisation/verified/verified_detections.geojson`

| R (m) | F1 A | F1 B | ΔF1 (A−B) [95 % CI] | p (raw) | p (BH) | sig (q=0.05) | W/L/T |
|------:|-----:|-----:|--------------------:|--------:|-------:|:------------:|------:|
|   20 | 0.6259 | 0.6202 | +0.0057 [-0.0065, +0.0181] | 0.368 | 0.368 | ns | 499/459/7583 |
|   25 | 0.7101 | 0.6925 | +0.0176 [+0.0061, +0.0291] | 0.002 | 0.002 | **\*** | 531/430/7580 |
|   30 | 0.7568 | 0.7298 | +0.0269 [+0.0160, +0.0378] | <0.001 | <0.001 | **\*** | 533/388/7620 |
|   35 | 0.7776 | 0.7489 | +0.0287 [+0.0184, +0.0390] | <0.001 | <0.001 | **\*** | 533/366/7642 |
|   40 | 0.7866 | 0.7563 | +0.0303 [+0.0200, +0.0407] | <0.001 | <0.001 | **\*** | 535/357/7649 |
|   45 | 0.7902 | 0.7600 | +0.0302 [+0.0200, +0.0403] | <0.001 | <0.001 | **\*** | 531/356/7654 |
|   50 | 0.8273 | 0.7968 | +0.0305 [+0.0210, +0.0400] | <0.001 | <0.001 | **\*** | 545/354/7642 |
|   75 | 0.8300 | 0.7993 | +0.0306 [+0.0213, +0.0401] | <0.001 | <0.001 | **\*** | 541/350/7650 |
|  100 | 0.8324 | 0.8005 | +0.0319 [+0.0226, +0.0413] | <0.001 | <0.001 | **\*** | 549/346/7646 |
|  125 | 0.8338 | 0.8009 | +0.0328 [+0.0235, +0.0422] | <0.001 | <0.001 | **\*** | 553/343/7645 |

Notes — wins / losses / ties are tile-level comparisons (per-tile F1_A vs F1_B); ΔF1 is the aggregate micro-average difference; CI is a 10 000-iteration tile-level paired bootstrap.

## image vs T=MIN

Detection sets:

- A (image): `outputs/55maps-image-generalisation/verified/verified_detections.geojson`
- B (T=MIN): `outputs/55maps-text-min-generalisation/verified/verified_detections.geojson`

| R (m) | F1 A | F1 B | ΔF1 (A−B) [95 % CI] | p (raw) | p (BH) | sig (q=0.05) | W/L/T |
|------:|-----:|-----:|--------------------:|--------:|-------:|:------------:|------:|
|   20 | 0.5080 | 0.6202 | -0.1122 [-0.1280, -0.0961] | <0.001 | <0.001 | **\*** | 519/791/7231 |
|   25 | 0.6209 | 0.6925 | -0.0715 [-0.0864, -0.0568] | <0.001 | <0.001 | **\*** | 583/727/7231 |
|   30 | 0.6886 | 0.7298 | -0.0413 [-0.0549, -0.0274] | <0.001 | <0.001 | **\*** | 609/654/7278 |
|   35 | 0.7276 | 0.7489 | -0.0213 [-0.0341, -0.0085] | <0.001 | <0.001 | **\*** | 628/604/7309 |
|   40 | 0.7518 | 0.7563 | -0.0045 [-0.0171, +0.0078] | 0.463 | 0.463 | ns | 653/557/7331 |
|   45 | 0.7660 | 0.7600 | +0.0060 [-0.0060, +0.0182] | 0.320 | 0.356 | ns | 669/532/7340 |
|   50 | 0.8333 | 0.7968 | +0.0365 [+0.0256, +0.0476] | <0.001 | <0.001 | **\*** | 757/439/7345 |
|   75 | 0.8492 | 0.7993 | +0.0499 [+0.0394, +0.0606] | <0.001 | <0.001 | **\*** | 790/404/7347 |
|  100 | 0.8536 | 0.8005 | +0.0531 [+0.0427, +0.0637] | <0.001 | <0.001 | **\*** | 810/389/7342 |
|  125 | 0.8554 | 0.8009 | +0.0544 [+0.0440, +0.0650] | <0.001 | <0.001 | **\*** | 818/390/7333 |

Notes — wins / losses / ties are tile-level comparisons (per-tile F1_A vs F1_B); ΔF1 is the aggregate micro-average difference; CI is a 10 000-iteration tile-level paired bootstrap.

## Reproducibility

- Driver: `scripts/paired_permutation_corrected_55maps.py`
- Summary builder: `scripts/build_pairwise_perm_v2_summary.py`
- Per-pair JSON outputs in `paired-<a>-vs-<b>/permutation-R<R>m.json`
- Per-pair summary in `paired-<a>-vs-<b>/summary.json`
- Detection inputs are unchanged from each run's
  `outputs/<run>/verified/verified_detections.geojson`; the corrected
  ground truth is rebuilt at each R from the run's review CSVs.
