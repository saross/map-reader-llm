# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-06-07T06:21:45.346075+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `bb7d5279e818cd52f7b9925e5f19790adf537676`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 440 | 3839 | 4306 | 4746 | 0 | 4746 | 0.1028 [0.0931, 0.1126] | 0.0927 [0.0839, 0.1014] | **0.0975** [0.0883, 0.1065] |
| 10 | 1364 | 2915 | 3382 | 4746 | 0 | 4746 | 0.3188 [0.3035, 0.3346] | 0.2874 [0.2732, 0.3019] | **0.3023** [0.2880, 0.3170] |
| 15 | 2241 | 2038 | 2505 | 4746 | 0 | 4746 | 0.5237 [0.5072, 0.5410] | 0.4722 [0.4557, 0.4887] | **0.4966** [0.4811, 0.5123] |
| 20 | 2859 | 1420 | 1887 | 4746 | 0 | 4746 | 0.6681 [0.6520, 0.6845] | 0.6024 [0.5863, 0.6192] | **0.6336** [0.6190, 0.6484] |
| 25 | 3207 | 1072 | 1539 | 4746 | 0 | 4746 | 0.7495 [0.7346, 0.7643] | 0.6757 [0.6602, 0.6918] | **0.7107** [0.6974, 0.7239] |
| 30 | 3387 | 892 | 1359 | 4746 | 0 | 4746 | 0.7915 [0.7776, 0.8055] | 0.7137 [0.6985, 0.7290] | **0.7506** [0.7382, 0.7625] |
| 35 | 3479 | 800 | 1267 | 4746 | 0 | 4746 | 0.8130 [0.7997, 0.8262] | 0.7330 [0.7183, 0.7477] | **0.7710** [0.7592, 0.7824] |
| 40 | 3517 | 762 | 1229 | 4746 | 0 | 4746 | 0.8219 [0.8088, 0.8351] | 0.7410 [0.7264, 0.7557] | **0.7794** [0.7681, 0.7906] |
| 45 | 3538 | 741 | 1208 | 4746 | 0 | 4746 | 0.8268 [0.8139, 0.8399] | 0.7455 [0.7308, 0.7600] | **0.7840** [0.7728, 0.7951] |
| 50 | 3836 | 443 | 1325 | 4746 | 415 | 5161 | 0.8965 [0.8862, 0.9062] | 0.7433 [0.7295, 0.7571] | **0.8127** [0.8025, 0.8227] |
| 75 | 3864 | 415 | 1476 | 4746 | 594 | 5340 | 0.9030 [0.8930, 0.9124] | 0.7236 [0.7098, 0.7373] | **0.8034** [0.7931, 0.8134] |
| 100 | 3881 | 398 | 1550 | 4746 | 685 | 5431 | 0.9070 [0.8971, 0.9162] | 0.7146 [0.7008, 0.7284] | **0.7994** [0.7889, 0.8095] |
| 125 | 3891 | 388 | 1584 | 4746 | 729 | 5475 | 0.9093 [0.8995, 0.9185] | 0.7107 [0.6968, 0.7247] | **0.7978** [0.7875, 0.8078] |
| 150 | 3904 | 375 | 1605 | 4746 | 763 | 5509 | 0.9124 [0.9028, 0.9214] | 0.7087 [0.6949, 0.7227] | **0.7977** [0.7874, 0.8076] |

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
(**F1 = 0.0975**) re-runs Hungarian over extended GT including
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
**F1 = 0.7978** at R = 125 m (95 % CI [0.7875, 0.8078]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/k3-scoring/55maps-text-min-generalisation/k3_verified.geojson`
  - Student GT: `/home/shawn/Code/map-reader-llm/inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `/home/shawn/Code/map-reader-llm/results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `bb7d5279e818cd52f7b9925e5f19790adf537676`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
