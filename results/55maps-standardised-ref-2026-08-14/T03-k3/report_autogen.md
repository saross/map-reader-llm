# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-14T08:41:20.868308+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 598 | 4307 | 4412 | 4731 | 279 | 5010 | 0.1219 [0.1125, 0.1315] | 0.1194 [0.1099, 0.1289] | **0.1206** [0.1113, 0.1301] | 0.6888 [0.6749, 0.7022] |
| 10 | 1657 | 3248 | 3353 | 4731 | 279 | 5010 | 0.3378 [0.3236, 0.3517] | 0.3307 [0.3165, 0.3450] | **0.3342** [0.3206, 0.3479] | 0.6888 [0.6749, 0.7022] |
| 15 | 2608 | 2297 | 2402 | 4731 | 279 | 5010 | 0.5317 [0.5167, 0.5466] | 0.5206 [0.5053, 0.5360] | **0.5261** [0.5119, 0.5404] | 0.6888 [0.6749, 0.7022] |
| 20 | 3331 | 1574 | 1679 | 4731 | 279 | 5010 | 0.6791 [0.6652, 0.6929] | 0.6649 [0.6503, 0.6796] | **0.6719** [0.6590, 0.6848] | 0.6888 [0.6749, 0.7022] |
| 25 | 3732 | 1173 | 1278 | 4731 | 279 | 5010 | 0.7609 [0.7479, 0.7735] | 0.7449 [0.7314, 0.7582] | **0.7528** [0.7413, 0.7640] | 0.6888 [0.6749, 0.7022] |
| 30 | 3945 | 960 | 1065 | 4731 | 279 | 5010 | 0.8043 [0.7923, 0.8160] | 0.7874 [0.7746, 0.7998] | **0.7958** [0.7854, 0.8057] | 0.6888 [0.6749, 0.7022] |
| 35 | 4057 | 848 | 953 | 4731 | 279 | 5010 | 0.8271 [0.8156, 0.8383] | 0.8098 [0.7976, 0.8215] | **0.8184** [0.8088, 0.8275] | 0.6888 [0.6749, 0.7022] |
| 40 | 4109 | 796 | 901 | 4731 | 279 | 5010 | 0.8377 [0.8265, 0.8487] | 0.8202 [0.8084, 0.8317] | **0.8288** [0.8196, 0.8376] | 0.6888 [0.6749, 0.7022] |
| 45 | 4141 | 764 | 869 | 4731 | 279 | 5010 | 0.8442 [0.8332, 0.8550] | 0.8265 [0.8148, 0.8379] | **0.8353** [0.8262, 0.8440] | 0.6888 [0.6749, 0.7022] |
| 50 | 4161 | 744 | 849 | 4731 | 279 | 5010 | 0.8483 [0.8374, 0.8591] | 0.8305 [0.8189, 0.8419] | **0.8393** [0.8304, 0.8479] | 0.6888 [0.6749, 0.7022] |
| 75 | 4182 | 723 | 828 | 4731 | 279 | 5010 | 0.8526 [0.8417, 0.8632] | 0.8347 [0.8232, 0.8458] | **0.8436** [0.8349, 0.8520] | 0.6888 [0.6749, 0.7022] |
| 100 | 4194 | 711 | 816 | 4731 | 279 | 5010 | 0.8550 [0.8442, 0.8656] | 0.8371 [0.8258, 0.8481] | **0.8460** [0.8374, 0.8544] | 0.6888 [0.6749, 0.7022] |
| 125 | 4203 | 702 | 807 | 4731 | 279 | 5010 | 0.8569 [0.8459, 0.8674] | 0.8389 [0.8277, 0.8498] | **0.8478** [0.8392, 0.8560] | 0.6888 [0.6749, 0.7022] |
| 150 | 4212 | 693 | 798 | 4731 | 279 | 5010 | 0.8587 [0.8478, 0.8692] | 0.8407 [0.8295, 0.8515] | **0.8496** [0.8411, 0.8578] | 0.6888 [0.6749, 0.7022] |

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
  - Detections: `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/k3-scoring/55maps-text-high-t0.3-generalisation/k3_verified.geojson`
  - Student GT (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
