# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-14T08:41:17.624662+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 570 | 4216 | 4440 | 4731 | 279 | 5010 | 0.1191 [0.1092, 0.1288] | 0.1138 [0.1042, 0.1232] | **0.1164** [0.1066, 0.1258] | 0.6796 [0.6657, 0.6933] |
| 10 | 1645 | 3141 | 3365 | 4731 | 279 | 5010 | 0.3437 [0.3291, 0.3585] | 0.3283 [0.3136, 0.3431] | **0.3359** [0.3216, 0.3502] | 0.6796 [0.6657, 0.6933] |
| 15 | 2623 | 2163 | 2387 | 4731 | 279 | 5010 | 0.5481 [0.5328, 0.5634] | 0.5236 [0.5079, 0.5391] | **0.5355** [0.5209, 0.5500] | 0.6796 [0.6657, 0.6933] |
| 20 | 3294 | 1492 | 1716 | 4731 | 279 | 5010 | 0.6883 [0.6738, 0.7026] | 0.6575 [0.6421, 0.6723] | **0.6725** [0.6591, 0.6855] | 0.6796 [0.6657, 0.6933] |
| 25 | 3684 | 1102 | 1326 | 4731 | 279 | 5010 | 0.7697 [0.7570, 0.7823] | 0.7353 [0.7215, 0.7490] | **0.7521** [0.7406, 0.7632] | 0.6796 [0.6657, 0.6933] |
| 30 | 3920 | 866 | 1090 | 4731 | 279 | 5010 | 0.8191 [0.8072, 0.8308] | 0.7824 [0.7696, 0.7953] | **0.8003** [0.7899, 0.8103] | 0.6796 [0.6657, 0.6933] |
| 35 | 4034 | 752 | 976 | 4731 | 279 | 5010 | 0.8429 [0.8317, 0.8538] | 0.8052 [0.7927, 0.8174] | **0.8236** [0.8141, 0.8330] | 0.6796 [0.6657, 0.6933] |
| 40 | 4075 | 711 | 935 | 4731 | 279 | 5010 | 0.8514 [0.8406, 0.8624] | 0.8134 [0.8012, 0.8254] | **0.8320** [0.8228, 0.8411] | 0.6796 [0.6657, 0.6933] |
| 45 | 4097 | 689 | 913 | 4731 | 279 | 5010 | 0.8560 [0.8454, 0.8667] | 0.8178 [0.8057, 0.8297] | **0.8365** [0.8273, 0.8454] | 0.6796 [0.6657, 0.6933] |
| 50 | 4108 | 678 | 902 | 4731 | 279 | 5010 | 0.8583 [0.8477, 0.8690] | 0.8200 [0.8078, 0.8319] | **0.8387** [0.8297, 0.8475] | 0.6796 [0.6657, 0.6933] |
| 75 | 4121 | 665 | 889 | 4731 | 279 | 5010 | 0.8611 [0.8504, 0.8717] | 0.8226 [0.8105, 0.8344] | **0.8414** [0.8324, 0.8501] | 0.6796 [0.6657, 0.6933] |
| 100 | 4133 | 653 | 877 | 4731 | 279 | 5010 | 0.8636 [0.8530, 0.8741] | 0.8250 [0.8129, 0.8368] | **0.8438** [0.8349, 0.8525] | 0.6796 [0.6657, 0.6933] |
| 125 | 4144 | 642 | 866 | 4731 | 279 | 5010 | 0.8659 [0.8553, 0.8763] | 0.8271 [0.8151, 0.8389] | **0.8461** [0.8372, 0.8547] | 0.6796 [0.6657, 0.6933] |
| 150 | 4148 | 638 | 862 | 4731 | 279 | 5010 | 0.8667 [0.8561, 0.8772] | 0.8279 [0.8159, 0.8398] | **0.8469** [0.8381, 0.8554] | 0.6796 [0.6657, 0.6933] |

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
  - Detections: `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/k3-scoring/55maps-text-high-generalisation/k3_verified.geojson`
  - Student GT (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
