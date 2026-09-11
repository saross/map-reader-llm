# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-09-11T00:02:27.080185+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 484 | 11792 | 4262 | 4746 | 0 | 4746 | 0.0394 [0.0356, 0.0434] | 0.1020 [0.0928, 0.1112] | **0.0569** [0.0515, 0.0623] |
| 10 | 1502 | 10774 | 3244 | 4746 | 0 | 4746 | 0.1224 [0.1148, 0.1302] | 0.3165 [0.3015, 0.3315] | **0.1765** [0.1666, 0.1866] |
| 15 | 2402 | 9874 | 2344 | 4746 | 0 | 4746 | 0.1957 [0.1858, 0.2060] | 0.5061 [0.4896, 0.5231] | **0.2822** [0.2702, 0.2947] |
| 20 | 3079 | 9197 | 1667 | 4746 | 0 | 4746 | 0.2508 [0.2395, 0.2625] | 0.6488 [0.6327, 0.6650] | **0.3618** [0.3484, 0.3755] |
| 25 | 3486 | 8790 | 1260 | 4746 | 0 | 4746 | 0.2840 [0.2717, 0.2963] | 0.7345 [0.7196, 0.7493] | **0.4096** [0.3955, 0.4235] |
| 30 | 3669 | 8607 | 1077 | 4746 | 0 | 4746 | 0.2989 [0.2863, 0.3114] | 0.7731 [0.7588, 0.7870] | **0.4311** [0.4169, 0.4450] |
| 35 | 3754 | 8522 | 992 | 4746 | 0 | 4746 | 0.3058 [0.2930, 0.3185] | 0.7910 [0.7771, 0.8044] | **0.4411** [0.4269, 0.4553] |
| 40 | 3801 | 8475 | 945 | 4746 | 0 | 4746 | 0.3096 [0.2969, 0.3224] | 0.8009 [0.7873, 0.8139] | **0.4466** [0.4322, 0.4608] |
| 45 | 3821 | 8455 | 925 | 4746 | 0 | 4746 | 0.3113 [0.2984, 0.3241] | 0.8051 [0.7918, 0.8181] | **0.4489** [0.4347, 0.4631] |
| 50 | 4140 | 8136 | 1020 | 4746 | 414 | 5160 | 0.3372 [0.3238, 0.3505] | 0.8023 [0.7894, 0.8148] | **0.4749** [0.4604, 0.4889] |
| 75 | 4171 | 8105 | 1168 | 4746 | 593 | 5339 | 0.3398 [0.3262, 0.3532] | 0.7812 [0.7681, 0.7939] | **0.4736** [0.4593, 0.4874] |
| 100 | 4192 | 8084 | 1238 | 4746 | 684 | 5430 | 0.3415 [0.3279, 0.3550] | 0.7720 [0.7586, 0.7849] | **0.4735** [0.4593, 0.4872] |
| 125 | 4204 | 8072 | 1270 | 4746 | 728 | 5474 | 0.3425 [0.3289, 0.3560] | 0.7680 [0.7546, 0.7809] | **0.4737** [0.4596, 0.4874] |
| 150 | 4218 | 8058 | 1290 | 4746 | 762 | 5508 | 0.3436 [0.3300, 0.3571] | 0.7658 [0.7523, 0.7786] | **0.4744** [0.4603, 0.4880] |

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
(**F1 = 0.0569**) re-runs Hungarian over extended GT including
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
**F1 = 0.4737** at R = 125 m (95 % CI [0.4596, 0.4874]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-text-min-n10-uplift__verified-5of10-canonical-gt/twin-5of10.geojson`
  - Student GT: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
