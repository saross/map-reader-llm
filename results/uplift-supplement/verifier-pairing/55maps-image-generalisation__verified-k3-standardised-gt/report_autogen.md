# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-29T10:12:05.093966+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 338 | 7540 | 4672 | 4731 | 279 | 5010 | 0.0429 [0.0382, 0.0476] | 0.0675 [0.0604, 0.0747] | **0.0525** [0.0469, 0.0581] | 0.4369 [0.4178, 0.4551] |
| 10 | 1161 | 6717 | 3849 | 4731 | 279 | 5010 | 0.1474 [0.1387, 0.1561] | 0.2317 [0.2190, 0.2443] | **0.1802** [0.1702, 0.1902] | 0.4369 [0.4178, 0.4551] |
| 15 | 2057 | 5821 | 2953 | 4731 | 279 | 5010 | 0.2611 [0.2499, 0.2722] | 0.4106 [0.3955, 0.4251] | **0.3192** [0.3070, 0.3310] | 0.4369 [0.4178, 0.4551] |
| 20 | 2802 | 5076 | 2208 | 4731 | 279 | 5010 | 0.3557 [0.3432, 0.3682] | 0.5593 [0.5438, 0.5741] | **0.4348** [0.4220, 0.4474] | 0.4369 [0.4178, 0.4551] |
| 25 | 3353 | 4525 | 1657 | 4731 | 279 | 5010 | 0.4256 [0.4123, 0.4390] | 0.6693 [0.6549, 0.6836] | **0.5203** [0.5073, 0.5331] | 0.4369 [0.4178, 0.4551] |
| 30 | 3683 | 4195 | 1327 | 4731 | 279 | 5010 | 0.4675 [0.4536, 0.4811] | 0.7351 [0.7214, 0.7483] | **0.5715** [0.5588, 0.5839] | 0.4369 [0.4178, 0.4551] |
| 35 | 3883 | 3995 | 1127 | 4731 | 279 | 5010 | 0.4929 [0.4788, 0.5067] | 0.7750 [0.7622, 0.7877] | **0.6026** [0.5900, 0.6147] | 0.4369 [0.4178, 0.4551] |
| 40 | 4000 | 3878 | 1010 | 4731 | 279 | 5010 | 0.5077 [0.4939, 0.5216] | 0.7984 [0.7861, 0.8104] | **0.6207** [0.6086, 0.6326] | 0.4369 [0.4178, 0.4551] |
| 45 | 4064 | 3814 | 946 | 4731 | 279 | 5010 | 0.5159 [0.5019, 0.5297] | 0.8112 [0.7989, 0.8230] | **0.6307** [0.6188, 0.6424] | 0.4369 [0.4178, 0.4551] |
| 50 | 4109 | 3769 | 901 | 4731 | 279 | 5010 | 0.5216 [0.5075, 0.5354] | 0.8202 [0.8081, 0.8318] | **0.6376** [0.6257, 0.6492] | 0.4369 [0.4178, 0.4551] |
| 75 | 4199 | 3679 | 811 | 4731 | 279 | 5010 | 0.5330 [0.5187, 0.5470] | 0.8381 [0.8263, 0.8494] | **0.6516** [0.6397, 0.6633] | 0.4369 [0.4178, 0.4551] |
| 100 | 4222 | 3656 | 788 | 4731 | 279 | 5010 | 0.5359 [0.5217, 0.5499] | 0.8427 [0.8312, 0.8538] | **0.6552** [0.6433, 0.6668] | 0.4369 [0.4178, 0.4551] |
| 125 | 4238 | 3640 | 772 | 4731 | 279 | 5010 | 0.5380 [0.5237, 0.5519] | 0.8459 [0.8343, 0.8569] | **0.6577** [0.6456, 0.6692] | 0.4369 [0.4178, 0.4551] |
| 150 | 4248 | 3630 | 762 | 4731 | 279 | 5010 | 0.5392 [0.5249, 0.5532] | 0.8479 [0.8365, 0.8589] | **0.6592** [0.6472, 0.6708] | 0.4369 [0.4178, 0.4551] |

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
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-image-generalisation__verified-k3-standardised-gt/twin-3of5.geojson`
  - Student GT (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
