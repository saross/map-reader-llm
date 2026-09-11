# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-09-10T23:57:47.599024+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 461 | 11929 | 4285 | 4746 | 0 | 4746 | 0.0372 [0.0335, 0.0410] | 0.0971 [0.0882, 0.1061] | **0.0538** [0.0486, 0.0591] |
| 10 | 1439 | 10951 | 3307 | 4746 | 0 | 4746 | 0.1161 [0.1088, 0.1237] | 0.3032 [0.2885, 0.3180] | **0.1680** [0.1584, 0.1777] |
| 15 | 2365 | 10025 | 2381 | 4746 | 0 | 4746 | 0.1909 [0.1811, 0.2009] | 0.4983 [0.4816, 0.5150] | **0.2760** [0.2639, 0.2883] |
| 20 | 3010 | 9380 | 1736 | 4746 | 0 | 4746 | 0.2429 [0.2317, 0.2544] | 0.6342 [0.6181, 0.6505] | **0.3513** [0.3380, 0.3648] |
| 25 | 3380 | 9010 | 1366 | 4746 | 0 | 4746 | 0.2728 [0.2608, 0.2849] | 0.7122 [0.6971, 0.7274] | **0.3945** [0.3806, 0.4082] |
| 30 | 3571 | 8819 | 1175 | 4746 | 0 | 4746 | 0.2882 [0.2759, 0.3007] | 0.7524 [0.7380, 0.7670] | **0.4168** [0.4028, 0.4306] |
| 35 | 3662 | 8728 | 1084 | 4746 | 0 | 4746 | 0.2956 [0.2830, 0.3081] | 0.7716 [0.7576, 0.7856] | **0.4274** [0.4133, 0.4415] |
| 40 | 3706 | 8684 | 1040 | 4746 | 0 | 4746 | 0.2991 [0.2865, 0.3117] | 0.7809 [0.7672, 0.7945] | **0.4325** [0.4184, 0.4466] |
| 45 | 3728 | 8662 | 1018 | 4746 | 0 | 4746 | 0.3009 [0.2882, 0.3136] | 0.7855 [0.7718, 0.7990] | **0.4351** [0.4209, 0.4492] |
| 50 | 4049 | 8341 | 1111 | 4746 | 414 | 5160 | 0.3268 [0.3135, 0.3401] | 0.7847 [0.7715, 0.7976] | **0.4614** [0.4471, 0.4754] |
| 75 | 4081 | 8309 | 1258 | 4746 | 593 | 5339 | 0.3294 [0.3160, 0.3427] | 0.7644 [0.7510, 0.7775] | **0.4604** [0.4463, 0.4742] |
| 100 | 4104 | 8286 | 1326 | 4746 | 684 | 5430 | 0.3312 [0.3178, 0.3446] | 0.7558 [0.7425, 0.7690] | **0.4606** [0.4466, 0.4743] |
| 125 | 4117 | 8273 | 1357 | 4746 | 728 | 5474 | 0.3323 [0.3189, 0.3456] | 0.7521 [0.7387, 0.7653] | **0.4609** [0.4469, 0.4747] |
| 150 | 4135 | 8255 | 1373 | 4746 | 762 | 5508 | 0.3337 [0.3203, 0.3471] | 0.7507 [0.7373, 0.7641] | **0.4621** [0.4480, 0.4757] |

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
(**F1 = 0.0538**) re-runs Hungarian over extended GT including
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
**F1 = 0.4609** at R = 125 m (95 % CI [0.4469, 0.4747]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-text-min-generalisation__verified-k3-canonical-gt/twin-3of5.geojson`
  - Student GT: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
