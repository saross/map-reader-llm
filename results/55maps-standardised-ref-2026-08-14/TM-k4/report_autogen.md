# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-14T08:41:12.390414+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 620 | 3245 | 4390 | 4731 | 279 | 5010 | 0.1604 [0.1476, 0.1728] | 0.1238 [0.1135, 0.1336] | **0.1397** [0.1285, 0.1506] | 0.6401 [0.6265, 0.6539] |
| 10 | 1571 | 2294 | 3439 | 4731 | 279 | 5010 | 0.4065 [0.3893, 0.4235] | 0.3136 [0.2986, 0.3286] | **0.3540** [0.3387, 0.3694] | 0.6401 [0.6265, 0.6539] |
| 15 | 2370 | 1495 | 2640 | 4731 | 279 | 5010 | 0.6132 [0.5964, 0.6301] | 0.4731 [0.4570, 0.4896] | **0.5341** [0.5189, 0.5498] | 0.6401 [0.6265, 0.6539] |
| 20 | 2906 | 959 | 2104 | 4731 | 279 | 5010 | 0.7519 [0.7366, 0.7673] | 0.5800 [0.5637, 0.5966] | **0.6549** [0.6404, 0.6696] | 0.6401 [0.6265, 0.6539] |
| 25 | 3195 | 670 | 1815 | 4731 | 279 | 5010 | 0.8266 [0.8133, 0.8396] | 0.6377 [0.6221, 0.6537] | **0.7200** [0.7069, 0.7330] | 0.6401 [0.6265, 0.6539] |
| 30 | 3344 | 521 | 1666 | 4731 | 279 | 5010 | 0.8652 [0.8535, 0.8771] | 0.6675 [0.6519, 0.6829] | **0.7536** [0.7412, 0.7657] | 0.6401 [0.6265, 0.6539] |
| 35 | 3425 | 440 | 1585 | 4731 | 279 | 5010 | 0.8862 [0.8752, 0.8970] | 0.6836 [0.6685, 0.6987] | **0.7718** [0.7604, 0.7831] | 0.6401 [0.6265, 0.6539] |
| 40 | 3453 | 412 | 1557 | 4731 | 279 | 5010 | 0.8934 [0.8828, 0.9040] | 0.6892 [0.6742, 0.7043] | **0.7781** [0.7668, 0.7893] | 0.6401 [0.6265, 0.6539] |
| 45 | 3468 | 397 | 1542 | 4731 | 279 | 5010 | 0.8973 [0.8870, 0.9076] | 0.6922 [0.6773, 0.7072] | **0.7815** [0.7703, 0.7925] | 0.6401 [0.6265, 0.6539] |
| 50 | 3476 | 389 | 1534 | 4731 | 279 | 5010 | 0.8994 [0.8889, 0.9096] | 0.6938 [0.6789, 0.7087] | **0.7833** [0.7722, 0.7943] | 0.6401 [0.6265, 0.6539] |
| 75 | 3482 | 383 | 1528 | 4731 | 279 | 5010 | 0.9009 [0.8907, 0.9111] | 0.6950 [0.6800, 0.7100] | **0.7847** [0.7734, 0.7956] | 0.6401 [0.6265, 0.6539] |
| 100 | 3487 | 378 | 1523 | 4731 | 279 | 5010 | 0.9022 [0.8921, 0.9123] | 0.6960 [0.6810, 0.7108] | **0.7858** [0.7747, 0.7967] | 0.6401 [0.6265, 0.6539] |
| 125 | 3489 | 376 | 1521 | 4731 | 279 | 5010 | 0.9027 [0.8926, 0.9128] | 0.6964 [0.6815, 0.7112] | **0.7863** [0.7752, 0.7971] | 0.6401 [0.6265, 0.6539] |
| 150 | 3495 | 370 | 1515 | 4731 | 279 | 5010 | 0.9043 [0.8942, 0.9143] | 0.6976 [0.6826, 0.7124] | **0.7876** [0.7766, 0.7984] | 0.6401 [0.6265, 0.6539] |

## How to read this table

- **Reference**: the ruling-21 standardised layers — the standardised
  student ground truth plus the standardised extension layer (confirmed
  mounds the students missed, at marked centres ±2.5 m). Because marked
  centres are exactly localised, the extension layer enters the extended
  ground truth **whole at every R**: the legacy ring gate (Obs 371) is
  dissolved, `n_extension` is constant across rows, and only the Hungarian
  matching radius varies with R. Sub-50 m rows are therefore genuine
  Track-2 figures, not a collapse to the student layer.
- **n_ref_student**: standardised student records scoped to the evaluation
  tile bounds.
- **n_extension**: extension records admitted to the extended GT before
  tile scoping (0 dropped by the 5 m channel-duplicate audit —
  expected 0 on the standardised layers, whose minimum
  `nearest_student_m` is 10.32 m).
- **n_ref_extended**: scoped extended-GT count — the recall denominator.
- **Tile MCC** (when present) is computed against the SAME extended GT.
  Tile classification does not use the matching radius, and the extended
  GT no longer varies with R, so MCC is constant across rows by
  construction.
- **Known reference biases** (Obs 396, artefact README): residual
  long-range duplicates deflate F1 ≈ −0.03 at a balanced operating point;
  absent joint student+model misses inflate it ≈ +0.011–0.012; net at
  point estimates ≈ −0.017, rank-preserving to first order.

## Reproducibility

- **Inputs**:
  - Detections: `/home/shawn/Code/map-reader-llm/outputs/55maps-text-min-generalisation/verified/verified_detections.geojson`
  - Student GT (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
