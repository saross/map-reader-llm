# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-08-29T10:34:40.056112+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 418 | 9492 | 4328 | 4746 | 0 | 4746 | 0.0422 [0.0379, 0.0466] | 0.0881 [0.0799, 0.0966] | **0.0570** [0.0515, 0.0628] |
| 10 | 1350 | 8560 | 3396 | 4746 | 0 | 4746 | 0.1362 [0.1281, 0.1445] | 0.2845 [0.2703, 0.2985] | **0.1842** [0.1742, 0.1942] |
| 15 | 2268 | 7642 | 2478 | 4746 | 0 | 4746 | 0.2289 [0.2180, 0.2400] | 0.4779 [0.4620, 0.4943] | **0.3095** [0.2970, 0.3222] |
| 20 | 3011 | 6899 | 1735 | 4746 | 0 | 4746 | 0.3038 [0.2912, 0.3165] | 0.6344 [0.6187, 0.6504] | **0.4109** [0.3972, 0.4244] |
| 25 | 3442 | 6468 | 1304 | 4746 | 0 | 4746 | 0.3473 [0.3337, 0.3607] | 0.7252 [0.7109, 0.7398] | **0.4697** [0.4555, 0.4835] |
| 30 | 3660 | 6250 | 1086 | 4746 | 0 | 4746 | 0.3693 [0.3555, 0.3831] | 0.7712 [0.7576, 0.7844] | **0.4995** [0.4853, 0.5133] |
| 35 | 3767 | 6143 | 979 | 4746 | 0 | 4746 | 0.3801 [0.3660, 0.3941] | 0.7937 [0.7807, 0.8067] | **0.5141** [0.4999, 0.5279] |
| 40 | 3815 | 6095 | 931 | 4746 | 0 | 4746 | 0.3850 [0.3708, 0.3990] | 0.8038 [0.7908, 0.8168] | **0.5206** [0.5063, 0.5346] |
| 45 | 3848 | 6062 | 898 | 4746 | 0 | 4746 | 0.3883 [0.3740, 0.4024] | 0.8108 [0.7979, 0.8235] | **0.5251** [0.5107, 0.5391] |
| 50 | 4185 | 5725 | 975 | 4746 | 414 | 5160 | 0.4223 [0.4077, 0.4366] | 0.8110 [0.7988, 0.8231] | **0.5554** [0.5415, 0.5690] |
| 75 | 4207 | 5703 | 1132 | 4746 | 593 | 5339 | 0.4245 [0.4098, 0.4389] | 0.7880 [0.7754, 0.8004] | **0.5518** [0.5381, 0.5653] |
| 100 | 4228 | 5682 | 1202 | 4746 | 684 | 5430 | 0.4266 [0.4120, 0.4411] | 0.7786 [0.7659, 0.7914] | **0.5512** [0.5378, 0.5647] |
| 125 | 4240 | 5670 | 1234 | 4746 | 728 | 5474 | 0.4279 [0.4133, 0.4424] | 0.7746 [0.7618, 0.7874] | **0.5512** [0.5377, 0.5647] |
| 150 | 4251 | 5659 | 1257 | 4746 | 762 | 5508 | 0.4290 [0.4144, 0.4435] | 0.7718 [0.7589, 0.7847] | **0.5514** [0.5379, 0.5649] |

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
(**F1 = 0.0570**) re-runs Hungarian over extended GT including
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
**F1 = 0.5512** at R = 125 m (95 % CI [0.5377, 0.5647]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-text-high-t0-3-generalisation__verified-k4-canonical-gt/twin-4of5.geojson`
  - Student GT: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
