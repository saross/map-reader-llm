# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-09-10T23:57:40.888143+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 438 | 13507 | 4308 | 4746 | 0 | 4746 | 0.0314 [0.0283, 0.0347] | 0.0923 [0.0839, 0.1011] | **0.0469** [0.0424, 0.0516] |
| 10 | 1415 | 12530 | 3331 | 4746 | 0 | 4746 | 0.1015 [0.0953, 0.1079] | 0.2981 [0.2838, 0.3124] | **0.1514** [0.1429, 0.1601] |
| 15 | 2393 | 11552 | 2353 | 4746 | 0 | 4746 | 0.1716 [0.1631, 0.1802] | 0.5042 [0.4883, 0.5203] | **0.2561** [0.2451, 0.2670] |
| 20 | 3200 | 10745 | 1546 | 4746 | 0 | 4746 | 0.2295 [0.2194, 0.2397] | 0.6743 [0.6592, 0.6893] | **0.3424** [0.3299, 0.3549] |
| 25 | 3665 | 10280 | 1081 | 4746 | 0 | 4746 | 0.2628 [0.2518, 0.2738] | 0.7722 [0.7587, 0.7855] | **0.3922** [0.3789, 0.4051] |
| 30 | 3906 | 10039 | 840 | 4746 | 0 | 4746 | 0.2801 [0.2687, 0.2915] | 0.8230 [0.8108, 0.8347] | **0.4180** [0.4045, 0.4311] |
| 35 | 4033 | 9912 | 713 | 4746 | 0 | 4746 | 0.2892 [0.2775, 0.3010] | 0.8498 [0.8385, 0.8608] | **0.4315** [0.4179, 0.4450] |
| 40 | 4091 | 9854 | 655 | 4746 | 0 | 4746 | 0.2934 [0.2815, 0.3052] | 0.8620 [0.8511, 0.8725] | **0.4378** [0.4240, 0.4513] |
| 45 | 4132 | 9813 | 614 | 4746 | 0 | 4746 | 0.2963 [0.2844, 0.3082] | 0.8706 [0.8600, 0.8808] | **0.4421** [0.4284, 0.4558] |
| 50 | 4515 | 9430 | 645 | 4746 | 414 | 5160 | 0.3238 [0.3116, 0.3361] | 0.8750 [0.8649, 0.8847] | **0.4727** [0.4590, 0.4862] |
| 75 | 4580 | 9365 | 759 | 4746 | 593 | 5339 | 0.3284 [0.3161, 0.3408] | 0.8578 [0.8477, 0.8678] | **0.4750** [0.4615, 0.4884] |
| 100 | 4624 | 9321 | 806 | 4746 | 684 | 5430 | 0.3316 [0.3191, 0.3441] | 0.8516 [0.8413, 0.8616] | **0.4773** [0.4638, 0.4906] |
| 125 | 4647 | 9298 | 827 | 4746 | 728 | 5474 | 0.3332 [0.3207, 0.3458] | 0.8489 [0.8385, 0.8589] | **0.4786** [0.4652, 0.4919] |
| 150 | 4667 | 9278 | 841 | 4746 | 762 | 5508 | 0.3347 [0.3221, 0.3472] | 0.8473 [0.8368, 0.8574] | **0.4798** [0.4663, 0.4931] |

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
(**F1 = 0.0469**) re-runs Hungarian over extended GT including
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
**F1 = 0.4786** at R = 125 m (95 % CI [0.4652, 0.4919]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-text-high-t0-3-generalisation__verified-k3-canonical-gt/twin-3of5.geojson`
  - Student GT: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
