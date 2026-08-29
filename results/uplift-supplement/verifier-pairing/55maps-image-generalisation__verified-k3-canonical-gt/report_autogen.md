# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-08-29T10:09:30.443311+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 272 | 7606 | 4474 | 4746 | 0 | 4746 | 0.0345 [0.0303, 0.0388] | 0.0573 [0.0506, 0.0643] | **0.0431** [0.0380, 0.0484] |
| 10 | 973 | 6905 | 3773 | 4746 | 0 | 4746 | 0.1235 [0.1156, 0.1314] | 0.2050 [0.1927, 0.2174] | **0.1542** [0.1447, 0.1634] |
| 15 | 1792 | 6086 | 2954 | 4746 | 0 | 4746 | 0.2275 [0.2167, 0.2380] | 0.3776 [0.3625, 0.3922] | **0.2839** [0.2719, 0.2955] |
| 20 | 2543 | 5335 | 2203 | 4746 | 0 | 4746 | 0.3228 [0.3106, 0.3353] | 0.5358 [0.5203, 0.5513] | **0.4029** [0.3901, 0.4157] |
| 25 | 3103 | 4775 | 1643 | 4746 | 0 | 4746 | 0.3939 [0.3806, 0.4073] | 0.6538 [0.6388, 0.6689] | **0.4916** [0.4786, 0.5048] |
| 30 | 3439 | 4439 | 1307 | 4746 | 0 | 4746 | 0.4365 [0.4226, 0.4503] | 0.7246 [0.7103, 0.7384] | **0.5448** [0.5318, 0.5577] |
| 35 | 3638 | 4240 | 1108 | 4746 | 0 | 4746 | 0.4618 [0.4477, 0.4759] | 0.7665 [0.7532, 0.7797] | **0.5764** [0.5635, 0.5891] |
| 40 | 3757 | 4121 | 989 | 4746 | 0 | 4746 | 0.4769 [0.4629, 0.4910] | 0.7916 [0.7787, 0.8043] | **0.5952** [0.5826, 0.6077] |
| 45 | 3826 | 4052 | 920 | 4746 | 0 | 4746 | 0.4857 [0.4715, 0.4996] | 0.8062 [0.7936, 0.8186] | **0.6061** [0.5937, 0.6184] |
| 50 | 4160 | 3718 | 1000 | 4746 | 414 | 5160 | 0.5281 [0.5139, 0.5420] | 0.8062 [0.7939, 0.8181] | **0.6381** [0.6261, 0.6498] |
| 75 | 4333 | 3545 | 1006 | 4746 | 593 | 5339 | 0.5500 [0.5356, 0.5640] | 0.8116 [0.7994, 0.8233] | **0.6557** [0.6440, 0.6671] |
| 100 | 4388 | 3490 | 1042 | 4746 | 684 | 5430 | 0.5570 [0.5425, 0.5711] | 0.8081 [0.7958, 0.8200] | **0.6595** [0.6479, 0.6707] |
| 125 | 4414 | 3464 | 1060 | 4746 | 728 | 5474 | 0.5603 [0.5457, 0.5743] | 0.8064 [0.7940, 0.8183] | **0.6612** [0.6496, 0.6725] |
| 150 | 4432 | 3446 | 1076 | 4746 | 762 | 5508 | 0.5626 [0.5480, 0.5767] | 0.8046 [0.7922, 0.8165] | **0.6622** [0.6507, 0.6735] |

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
(**F1 = 0.0431**) re-runs Hungarian over extended GT including
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
**F1 = 0.6612** at R = 125 m (95 % CI [0.6496, 0.6725]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-image-generalisation__verified-k3-canonical-gt/twin-3of5.geojson`
  - Student GT: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
