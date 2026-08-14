# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-14T08:41:18.397787+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 656 | 3623 | 4354 | 4731 | 279 | 5010 | 0.1533 [0.1415, 0.1649] | 0.1309 [0.1204, 0.1409] | **0.1412** [0.1301, 0.1518] | 0.6569 [0.6435, 0.6710] |
| 10 | 1666 | 2613 | 3344 | 4731 | 279 | 5010 | 0.3893 [0.3735, 0.4055] | 0.3325 [0.3175, 0.3474] | **0.3587** [0.3438, 0.3736] | 0.6569 [0.6435, 0.6710] |
| 15 | 2535 | 1744 | 2475 | 4731 | 279 | 5010 | 0.5924 [0.5765, 0.6086] | 0.5060 [0.4898, 0.5220] | **0.5458** [0.5307, 0.5610] | 0.6569 [0.6435, 0.6710] |
| 20 | 3116 | 1163 | 1894 | 4731 | 279 | 5010 | 0.7282 [0.7133, 0.7432] | 0.6220 [0.6062, 0.6380] | **0.6709** [0.6567, 0.6848] | 0.6569 [0.6435, 0.6710] |
| 25 | 3438 | 841 | 1572 | 4731 | 279 | 5010 | 0.8035 [0.7902, 0.8165] | 0.6862 [0.6715, 0.7015] | **0.7402** [0.7275, 0.7526] | 0.6569 [0.6435, 0.6710] |
| 30 | 3601 | 678 | 1409 | 4731 | 279 | 5010 | 0.8416 [0.8296, 0.8534] | 0.7188 [0.7042, 0.7336] | **0.7753** [0.7637, 0.7867] | 0.6569 [0.6435, 0.6710] |
| 35 | 3701 | 578 | 1309 | 4731 | 279 | 5010 | 0.8649 [0.8538, 0.8758] | 0.7387 [0.7247, 0.7529] | **0.7969** [0.7861, 0.8074] | 0.6569 [0.6435, 0.6710] |
| 40 | 3735 | 544 | 1275 | 4731 | 279 | 5010 | 0.8729 [0.8619, 0.8836] | 0.7455 [0.7315, 0.7594] | **0.8042** [0.7937, 0.8145] | 0.6569 [0.6435, 0.6710] |
| 45 | 3754 | 525 | 1256 | 4731 | 279 | 5010 | 0.8773 [0.8665, 0.8877] | 0.7493 [0.7354, 0.7631] | **0.8083** [0.7980, 0.8184] | 0.6569 [0.6435, 0.6710] |
| 50 | 3766 | 513 | 1244 | 4731 | 279 | 5010 | 0.8801 [0.8694, 0.8905] | 0.7517 [0.7379, 0.7656] | **0.8109** [0.8006, 0.8210] | 0.6569 [0.6435, 0.6710] |
| 75 | 3777 | 502 | 1233 | 4731 | 279 | 5010 | 0.8827 [0.8720, 0.8929] | 0.7539 [0.7401, 0.7677] | **0.8132** [0.8031, 0.8233] | 0.6569 [0.6435, 0.6710] |
| 100 | 3786 | 493 | 1224 | 4731 | 279 | 5010 | 0.8848 [0.8742, 0.8950] | 0.7557 [0.7419, 0.7695] | **0.8152** [0.8051, 0.8251] | 0.6569 [0.6435, 0.6710] |
| 125 | 3790 | 489 | 1220 | 4731 | 279 | 5010 | 0.8857 [0.8752, 0.8959] | 0.7565 [0.7427, 0.7703] | **0.8160** [0.8060, 0.8259] | 0.6569 [0.6435, 0.6710] |
| 150 | 3797 | 482 | 1213 | 4731 | 279 | 5010 | 0.8874 [0.8769, 0.8975] | 0.7579 [0.7442, 0.7716] | **0.8175** [0.8075, 0.8274] | 0.6569 [0.6435, 0.6710] |

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
  - Detections: `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/k3-scoring/55maps-text-min-generalisation/k3_verified.geojson`
  - Student GT (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
