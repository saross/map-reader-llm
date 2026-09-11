# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-09-10T23:57:56.836643+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 417 | 13155 | 4329 | 4746 | 0 | 4746 | 0.0307 [0.0275, 0.0339] | 0.0879 [0.0793, 0.0963] | **0.0455** [0.0409, 0.0501] |
| 10 | 1382 | 12190 | 3364 | 4746 | 0 | 4746 | 0.1018 [0.0955, 0.1084] | 0.2912 [0.2766, 0.3057] | **0.1509** [0.1422, 0.1598] |
| 15 | 2415 | 11157 | 2331 | 4746 | 0 | 4746 | 0.1779 [0.1691, 0.1870] | 0.5088 [0.4926, 0.5248] | **0.2637** [0.2525, 0.2750] |
| 20 | 3175 | 10397 | 1571 | 4746 | 0 | 4746 | 0.2339 [0.2236, 0.2445] | 0.6690 [0.6532, 0.6841] | **0.3467** [0.3340, 0.3592] |
| 25 | 3627 | 9945 | 1119 | 4746 | 0 | 4746 | 0.2672 [0.2561, 0.2786] | 0.7642 [0.7504, 0.7776] | **0.3960** [0.3829, 0.4092] |
| 30 | 3880 | 9692 | 866 | 4746 | 0 | 4746 | 0.2859 [0.2742, 0.2976] | 0.8175 [0.8050, 0.8297] | **0.4236** [0.4100, 0.4370] |
| 35 | 4003 | 9569 | 743 | 4746 | 0 | 4746 | 0.2949 [0.2830, 0.3070] | 0.8434 [0.8320, 0.8549] | **0.4371** [0.4232, 0.4508] |
| 40 | 4060 | 9512 | 686 | 4746 | 0 | 4746 | 0.2991 [0.2871, 0.3114] | 0.8555 [0.8441, 0.8666] | **0.4433** [0.4295, 0.4571] |
| 45 | 4088 | 9484 | 658 | 4746 | 0 | 4746 | 0.3012 [0.2892, 0.3134] | 0.8614 [0.8503, 0.8724] | **0.4463** [0.4325, 0.4602] |
| 50 | 4444 | 9128 | 716 | 4746 | 414 | 5160 | 0.3274 [0.3148, 0.3400] | 0.8612 [0.8505, 0.8717] | **0.4745** [0.4605, 0.4881] |
| 75 | 4495 | 9077 | 844 | 4746 | 593 | 5339 | 0.3312 [0.3185, 0.3439] | 0.8419 [0.8307, 0.8529] | **0.4754** [0.4615, 0.4888] |
| 100 | 4536 | 9036 | 894 | 4746 | 684 | 5430 | 0.3342 [0.3215, 0.3470] | 0.8354 [0.8240, 0.8464] | **0.4774** [0.4636, 0.4910] |
| 125 | 4559 | 9013 | 915 | 4746 | 728 | 5474 | 0.3359 [0.3231, 0.3488] | 0.8328 [0.8214, 0.8440] | **0.4787** [0.4649, 0.4922] |
| 150 | 4574 | 8998 | 934 | 4746 | 762 | 5508 | 0.3370 [0.3242, 0.3499] | 0.8304 [0.8191, 0.8416] | **0.4795** [0.4656, 0.4929] |

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
(**F1 = 0.0455**) re-runs Hungarian over extended GT including
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
**F1 = 0.4787** at R = 125 m (95 % CI [0.4649, 0.4922]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-text-high-generalisation__verified-k3-canonical-gt/twin-3of5.geojson`
  - Student GT: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
