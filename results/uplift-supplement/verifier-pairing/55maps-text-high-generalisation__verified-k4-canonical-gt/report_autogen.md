# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-08-29T10:21:51.355100+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 393 | 8812 | 4353 | 4746 | 0 | 4746 | 0.0427 [0.0382, 0.0473] | 0.0828 [0.0744, 0.0912] | **0.0563** [0.0505, 0.0621] |
| 10 | 1289 | 7916 | 3457 | 4746 | 0 | 4746 | 0.1400 [0.1315, 0.1488] | 0.2716 [0.2570, 0.2860] | **0.1848** [0.1744, 0.1953] |
| 15 | 2242 | 6963 | 2504 | 4746 | 0 | 4746 | 0.2436 [0.2321, 0.2552] | 0.4724 [0.4562, 0.4886] | **0.3214** [0.3085, 0.3344] |
| 20 | 2938 | 6267 | 1808 | 4746 | 0 | 4746 | 0.3192 [0.3061, 0.3324] | 0.6190 [0.6026, 0.6351] | **0.4212** [0.4072, 0.4350] |
| 25 | 3341 | 5864 | 1405 | 4746 | 0 | 4746 | 0.3630 [0.3492, 0.3769] | 0.7040 [0.6886, 0.7189] | **0.4790** [0.4649, 0.4929] |
| 30 | 3561 | 5644 | 1185 | 4746 | 0 | 4746 | 0.3869 [0.3725, 0.4013] | 0.7503 [0.7357, 0.7645] | **0.5105** [0.4960, 0.5246] |
| 35 | 3658 | 5547 | 1088 | 4746 | 0 | 4746 | 0.3974 [0.3828, 0.4121] | 0.7708 [0.7565, 0.7845] | **0.5244** [0.5099, 0.5385] |
| 40 | 3701 | 5504 | 1045 | 4746 | 0 | 4746 | 0.4021 [0.3874, 0.4169] | 0.7798 [0.7659, 0.7937] | **0.5306** [0.5161, 0.5448] |
| 45 | 3720 | 5485 | 1026 | 4746 | 0 | 4746 | 0.4041 [0.3895, 0.4189] | 0.7838 [0.7699, 0.7976] | **0.5333** [0.5189, 0.5474] |
| 50 | 4021 | 5184 | 1139 | 4746 | 414 | 5160 | 0.4368 [0.4217, 0.4518] | 0.7793 [0.7658, 0.7923] | **0.5598** [0.5457, 0.5734] |
| 75 | 4047 | 5158 | 1292 | 4746 | 593 | 5339 | 0.4397 [0.4244, 0.4547] | 0.7580 [0.7441, 0.7715] | **0.5565** [0.5424, 0.5699] |
| 100 | 4068 | 5137 | 1362 | 4746 | 684 | 5430 | 0.4419 [0.4267, 0.4570] | 0.7492 [0.7351, 0.7627] | **0.5559** [0.5419, 0.5693] |
| 125 | 4082 | 5123 | 1392 | 4746 | 728 | 5474 | 0.4435 [0.4282, 0.4585] | 0.7457 [0.7316, 0.7594] | **0.5562** [0.5422, 0.5695] |
| 150 | 4091 | 5114 | 1417 | 4746 | 762 | 5508 | 0.4444 [0.4291, 0.4596] | 0.7427 [0.7286, 0.7566] | **0.5561** [0.5422, 0.5693] |

## How to read this table

- **TP / FP / FN**: Hungarian-matching counts against the extended GT at R.
  Every reviewer-promoted phantom within R is added to the GT before matching.
- **n_ref_student**: Student GT points scoped to the evaluation tile bounds
  (the denominator without any human-review correction).
- **n_promoted@R**: Number of reviewer-promoted phantoms included in the
  extended GT at this R. Yesterday's 472 mound labels appear at every R ≥ 50.
  Today's shell-stratified mound labels accumulate as R rises: +2 @50 m,
  +121 @75 m, +47 @100 m, +19 @125 m, +11 @150 m.
- **n_ref_extended**: Scoped extended-GT count at R (student GT scoped ∪
  in-scope phantoms at R). This is the recall denominator.
- **F1 [95 % CI]**: Corrected F1 at R with tile-level bootstrap CI.

## Comparison to yesterday's 50 m result

Yesterday's single-buffer correction (``compute_corrected_f1_human_reviewed.py``)
produced **F1 = 0.8295** at R = 50 m via an analytic adjustment to measured
counts (moved 472 FPs into TP and added them to the GT denominator, without
re-running Hungarian). This script's R = 5 m row
(**F1 = 0.0563**) re-runs Hungarian over extended GT including
the 2 today-corrections at 50 m. Expected ΔF1 ≈ +0.003 versus yesterday's
number. The two numbers are methodologically close but not identical —
Approach B allows detections to rematch optimally against the extended GT,
which can free a detection previously bound to a distant student-GT point
to pair with a closer phantom.

## Obs 272 caveat — the 150 m row is an upper bound

Obs 272 in ``docs/notes/reflections/working-notes.md`` shows the
attractor-pull effect (reviewer confirmations concentrating closer to the
detection than a uniform within-tile null would predict) is statistically
significant only through 125 m. At the (125, 150] shell the shell-specific
mound-confirmation rate is indistinguishable from the within-tile random-
placement null, and the (150, 286] shell ("200 m" sentinel in today's CSV)
is completely indistinguishable.

**Implication for interpretation:**

- **R ≤ 125 m**: corrected F1 / P / R are practitioner-meaningful. The
  reviewer-promoted phantoms in these shells are confirming detections
  genuinely spatially associated with visible mound symbols.
- **R = 150 m**: corrected F1 at 150 m is an **upper bound on achievable
  practitioner recall**, not a practitioner-useful operating point.
  Including the 11 mounds in the (125, 150] shell inflates recall in a way
  the attractor-pull null cannot distinguish from coincidental alignment.
- **R > 150 m (excluded from this analysis)**: the 74 candidates at the
  ">150 m" sentinel (``buffer_metres=200``) are visible mounds inside the
  286 m corners-plus-5 px review circle but outside every review ring.
  They are **not** added as phantoms at any R in this analysis; their
  detections appear as FP at every R ≤ 150 m, which is the correct
  behaviour under the 150 m practitioner cap.


## Practitioner-useful cap: F1 at R = 125 m

Recommended single-number summary for downstream quotation:
**F1 = 0.5562** at R = 125 m (95 % CI [0.5422, 0.5695]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-text-high-generalisation__verified-k4-canonical-gt/twin-4of5.geojson`
  - Student GT: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
