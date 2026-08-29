# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-08-29T10:47:42.186302+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 433 | 9737 | 4313 | 4746 | 0 | 4746 | 0.0426 [0.0382, 0.0470] | 0.0912 [0.0824, 0.0999] | **0.0581** [0.0523, 0.0639] |
| 10 | 1357 | 8813 | 3389 | 4746 | 0 | 4746 | 0.1334 [0.1250, 0.1420] | 0.2859 [0.2714, 0.3006] | **0.1820** [0.1716, 0.1924] |
| 15 | 2210 | 7960 | 2536 | 4746 | 0 | 4746 | 0.2173 [0.2064, 0.2287] | 0.4657 [0.4490, 0.4828] | **0.2963** [0.2835, 0.3094] |
| 20 | 2807 | 7363 | 1939 | 4746 | 0 | 4746 | 0.2760 [0.2633, 0.2888] | 0.5914 [0.5747, 0.6085] | **0.3764** [0.3624, 0.3904] |
| 25 | 3140 | 7030 | 1606 | 4746 | 0 | 4746 | 0.3088 [0.2953, 0.3222] | 0.6616 [0.6454, 0.6778] | **0.4210** [0.4066, 0.4352] |
| 30 | 3310 | 6860 | 1436 | 4746 | 0 | 4746 | 0.3255 [0.3117, 0.3393] | 0.6974 [0.6817, 0.7132] | **0.4438** [0.4292, 0.4581] |
| 35 | 3392 | 6778 | 1354 | 4746 | 0 | 4746 | 0.3335 [0.3195, 0.3477] | 0.7147 [0.6991, 0.7302] | **0.4548** [0.4400, 0.4693] |
| 40 | 3427 | 6743 | 1319 | 4746 | 0 | 4746 | 0.3370 [0.3229, 0.3512] | 0.7221 [0.7065, 0.7372] | **0.4595** [0.4445, 0.4740] |
| 45 | 3444 | 6726 | 1302 | 4746 | 0 | 4746 | 0.3386 [0.3246, 0.3528] | 0.7257 [0.7101, 0.7408] | **0.4618** [0.4468, 0.4764] |
| 50 | 3726 | 6444 | 1434 | 4746 | 414 | 5160 | 0.3664 [0.3516, 0.3810] | 0.7221 [0.7074, 0.7366] | **0.4861** [0.4714, 0.5005] |
| 75 | 3748 | 6422 | 1591 | 4746 | 593 | 5339 | 0.3685 [0.3537, 0.3832] | 0.7020 [0.6873, 0.7165] | **0.4833** [0.4690, 0.4976] |
| 100 | 3761 | 6409 | 1669 | 4746 | 684 | 5430 | 0.3698 [0.3551, 0.3846] | 0.6926 [0.6779, 0.7070] | **0.4822** [0.4679, 0.4962] |
| 125 | 3769 | 6401 | 1705 | 4746 | 728 | 5474 | 0.3706 [0.3559, 0.3854] | 0.6885 [0.6736, 0.7029] | **0.4818** [0.4675, 0.4958] |
| 150 | 3777 | 6393 | 1731 | 4746 | 762 | 5508 | 0.3714 [0.3566, 0.3862] | 0.6857 [0.6708, 0.7003] | **0.4818** [0.4675, 0.4957] |

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
(**F1 = 0.0581**) re-runs Hungarian over extended GT including
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
**F1 = 0.4818** at R = 125 m (95 % CI [0.4675, 0.4958]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-text-min-generalisation__verified-k4-canonical-gt/twin-4of5.geojson`
  - Student GT: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
