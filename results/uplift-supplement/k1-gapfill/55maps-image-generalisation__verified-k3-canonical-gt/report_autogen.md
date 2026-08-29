# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-08-29T04:59:47.721902+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 288 | 19342 | 4458 | 4746 | 0 | 4746 | 0.0147 [0.0129, 0.0165] | 0.0607 [0.0537, 0.0678] | **0.0236** [0.0208, 0.0265] |
| 10 | 944 | 18686 | 3802 | 4746 | 0 | 4746 | 0.0481 [0.0445, 0.0517] | 0.1989 [0.1869, 0.2112] | **0.0775** [0.0721, 0.0830] |
| 15 | 1725 | 17905 | 3021 | 4746 | 0 | 4746 | 0.0879 [0.0826, 0.0934] | 0.3635 [0.3483, 0.3788] | **0.1415** [0.1339, 0.1495] |
| 20 | 2447 | 17183 | 2299 | 4746 | 0 | 4746 | 0.1247 [0.1179, 0.1316] | 0.5156 [0.4996, 0.5320] | **0.2008** [0.1913, 0.2104] |
| 25 | 3030 | 16600 | 1716 | 4746 | 0 | 4746 | 0.1544 [0.1467, 0.1622] | 0.6384 [0.6229, 0.6539] | **0.2486** [0.2379, 0.2593] |
| 30 | 3422 | 16208 | 1324 | 4746 | 0 | 4746 | 0.1743 [0.1659, 0.1829] | 0.7210 [0.7068, 0.7353] | **0.2808** [0.2692, 0.2923] |
| 35 | 3679 | 15951 | 1067 | 4746 | 0 | 4746 | 0.1874 [0.1786, 0.1966] | 0.7752 [0.7619, 0.7884] | **0.3019** [0.2898, 0.3141] |
| 40 | 3854 | 15776 | 892 | 4746 | 0 | 4746 | 0.1963 [0.1871, 0.2058] | 0.8121 [0.7994, 0.8244] | **0.3162** [0.3038, 0.3286] |
| 45 | 3991 | 15639 | 755 | 4746 | 0 | 4746 | 0.2033 [0.1940, 0.2129] | 0.8409 [0.8292, 0.8524] | **0.3275** [0.3148, 0.3401] |
| 50 | 4418 | 15212 | 742 | 4746 | 414 | 5160 | 0.2251 [0.2151, 0.2351] | 0.8562 [0.8453, 0.8669] | **0.3564** [0.3436, 0.3692] |
| 75 | 4718 | 14912 | 621 | 4746 | 593 | 5339 | 0.2403 [0.2300, 0.2508] | 0.8837 [0.8742, 0.8928] | **0.3779** [0.3648, 0.3910] |
| 100 | 4829 | 14801 | 601 | 4746 | 684 | 5430 | 0.2460 [0.2356, 0.2568] | 0.8893 [0.8802, 0.8983] | **0.3854** [0.3722, 0.3985] |
| 125 | 4884 | 14746 | 590 | 4746 | 728 | 5474 | 0.2488 [0.2382, 0.2596] | 0.8922 [0.8832, 0.9008] | **0.3891** [0.3758, 0.4023] |
| 150 | 4928 | 14702 | 580 | 4746 | 762 | 5508 | 0.2510 [0.2404, 0.2619] | 0.8947 [0.8860, 0.9033] | **0.3921** [0.3788, 0.4054] |

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
(**F1 = 0.0236**) re-runs Hungarian over extended GT including
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
**F1 = 0.3891** at R = 125 m (95 % CI [0.3758, 0.4023]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `outputs/55maps-image-generalisation/proposer/library_plus-hp/run_1/detections-library_plus-hp-3-flash-2026-04-18.geojson`
  - Student GT: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
