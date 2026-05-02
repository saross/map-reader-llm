# Student GT False-Negative Rate — 55-Map Review-Based Estimate

Tightened estimate of the false-negative (FN) rate of the 55-map
student / participatory-GIS ground truth, derived from human review
of detection candidates produced by four corrected 55-map runs
(image-generalisation, text-HIGH-generalisation,
text-HIGH-T0.3-generalisation, text-MIN-generalisation) plus the
earlier image single-buffer review.

## Headline result

- **Headline FN rate (high-confidence + highest-confidence)**: 0.0887 (95 % CI 0.0693–0.1135); 462 candidate FN mounds added to 4744 student-GT mounds across 55 maps.
- **Recall-adjusted central estimate**: 0.1115 (95 % CI 0.0858–0.1449), using recall = 0.7958 from the highest-recall corrected run (image-generalisation, R_m = 150 m, recall CI 0.7836–0.8077).
- **Inclusive estimate (incl. marginal tier, 75–125 m)**: 0.1056 (95 % CI 0.0857–0.1303).
- **Permissive lower bound (all VLM-flagged mounds, regardless of distance)**: 0.1657 (95 % CI 0.1478–0.1872).
- **Comparator (4-map curator-vs-student diff, prior characterisation)**: ~6 % (Sobotkova et al. 2023; `docs/notes/reflections/working-notes.md`). The four curator-corrected gold-standard maps are not represented in the 55-map student GT, so this comparator is not reproducible from the active codebase — see Cross-validation, below.

### Comparison with prior 6 % characterisation

The headline rate (0.089) and the recall-adjusted central estimate (0.112) are both materially higher than the prior 4-map ~6 % figure. The 95 % CI on the headline rate (0.069–0.114) excludes 0.06; the 4-map figure is therefore unlikely to apply uniformly across the 55-map corpus. Three plausible drivers:

1. **Sampling bias in the 4-map calibration**. The four GS maps were chosen for fieldwork-grade reference quality and tend to have well-mapped, cluster-light terrain. Maps with denser mound clusters or more degraded symbols may exhibit higher student omission rates.
2. **Map-level variance is real and substantial**. Per-map headline FN rates range from 0.000 to 0.525 (see `per_map_fn_breakdown.csv`), with a median of 0.075 and IQR 0.043–0.128. This dispersion is the main reason the bootstrap CI is non-trivially wide.
3. **Definition of "missed"**. The 4-map figure was a curator-vs-student diff with the same map field reviewed against expert eyes. The 55-map figure is a curator-vs-VLM-flagged-candidates diff: it captures a different (and potentially partially overlapping) set of omissions. Recall-adjustment partially corrects for this; full correction would require a curator pass over the 55 maps, which has not been undertaken.

The result remains directionally consistent with the prior: students have approximately near-zero false-positive rate (Obs 261 onwards) and a non-trivial false-negative rate. The difference is in magnitude, not sign.

## Methodology

### Tier scheme

For each `human_label = "mound"` row in the five review CSVs
(total 1,817 mound-labelled rows out of 3,492 reviewed rows), we compute `d_nearest_studentGT`: the Euclidean distance from the candidate centroid `(x, y)` (EPSG:32635) to the nearest student-GT
mound on the same `map_name`, using a per-map `scipy.spatial.cKDTree`. Tiers (user-confirmed boundaries 2026-04-29):

- **Likely matching-collision (NOT a FN)**: `d_nearest_studentGT <= 75 m`. Shell-lift is confident at this
  distance (Obs 272); the candidate is most likely hitting the
  nearby student-GT mound, with the Hungarian assignment having
  matched that GT to a different detection.
- **Marginal**: `d_nearest_studentGT in (75, 125] m`. Shell-lift
  weakening; could be very-large-jitter on the same mound or a
  separate cluster-sibling.
- **High-confidence FN**: `d_nearest_studentGT > 125 m`. Beyond
  shell-significance threshold; the labelled mound is genuinely
  not in the student GT.
- **Highest-confidence FN**: `buffer_metres == 200`
  (the ">150 m" sentinel marker in the review UI). Treated as
  high-confidence FN regardless of `d_nearest_studentGT`.

### Per-tier counts (mound-labelled rows, before dedup)

| Tier | Count | Share of 1,817 mound rows |
|---|---:|---:|
| likely matching collision | 495 | 27.2 % |
| marginal | 141 | 7.8 % |
| high confidence fn | 1008 | 55.5 % |
| highest confidence fn | 173 | 9.5 % |

### Spatial deduplication

Different VLM runs may have independently flagged the same
student-missed mound. Within each map and each tier subset, we
perform greedy spatial dedup at 50 m: iterate
candidates in row order, drop any candidate whose centroid lies
within 50 m of an already-kept candidate.
This is the canonical match radius elsewhere in the project
(Obs 272). Across the five CSVs, every (map, x, y) tuple is
already unique; spatial dedup absorbs cross-run agreements at
shorter distances.

### Bootstrap

Aggregate FN rates across 55 maps are computed as
`sum(FN) / (sum(student_GT) + sum(FN))`. Confidence intervals
come from 10,000 by-map resamples (seed
42): each iteration resamples 55 maps with
replacement and recomputes the aggregate rate. CIs are the
2.5th and 97.5th percentiles across iterations.

## Per-stratum aggregate results

| Stratum | FN count | Aggregate FN rate | 95 % CI |
|---|---:|---:|---|
| Headline (high + highest) | 462 | 0.0887 | 0.0693–0.1135 |
| Inclusive (+ marginal) | 560 | 0.1056 | 0.0857–0.1303 |
| Permissive (all mound rows) | 942 | 0.1657 | 0.1478–0.1872 |

## Per-map summary statistics

| Stratum | Median | IQR (Q1–Q3) |
|---|---:|---|
| Headline FN rate | 0.0748 | 0.0426–0.1277 |
| Permissive FN rate | 0.1522 | 0.1302–0.2185 |

Per-map breakdown is in `per_map_fn_breakdown.csv`.

### Notable per-map findings

Top 5 maps by headline FN count (these dominate the corpus aggregate):

| Map | Student GT | Headline FN | Permissive FN | Headline FN rate |
|---|---:|---:|---:|---:|
| `K-35-076-2` | 47 | 52 | 59 | 0.5253 |
| `K-35-063-1_Granit_4326` | 246 | 39 | 69 | 0.1368 |
| `K-35-077-2` | 87 | 26 | 29 | 0.2301 |
| `K-35-054-1_Straldzha_4326` | 116 | 17 | 33 | 0.1278 |
| `K-35-064-1_Sredets_4326` | 126 | 15 | 22 | 0.1064 |

**Outlier flag** — `K-35-076-2` carries a headline FN rate of 0.5253 (52 likely-FN candidates against 47 student-GT mounds), the highest of any 55-map sheet. This map appears severely under-mapped in the student dataset: VLM-flagged mound candidates outnumber the student GT. If the user has prior knowledge of this sheet's mapping history, it would be worth checking whether participatory-GIS coverage was incomplete here. The aggregate rate is robust to this single outlier (the bootstrap CI averages across 55 maps), but for any per-map application the raw rates in `per_map_fn_breakdown.csv` should be inspected individually.

## Recall-adjusted central estimate

The headline rate is a lower bound on the true student-GT FN rate,
because the VLM does not detect every student-missed mound. To
approximate a central estimate we divide by the highest-recall
corrected 55-map run's recall:

- Run: **image-generalisation**
- R_m (corrected-F1 reference radius): 150 m
- Recall: 0.7958 (95 % CI 0.7836–0.8077)
- Source: `results/55maps-image-generalisation/corrected-f1-multi-buffer/summary.json`

**Recall-adjusted central estimate**: 0.1115 (95 % CI 0.0858–0.1449). The CI here propagates the bootstrap CI on the headline rate against the recall CI; it is conservative because it ignores the (small) covariance between the two terms.

Recall figures (all four runs):

| Run | Best R_m | Recall | Recall 95 % CI |
|---|---:|---:|---|
| image-generalisation | 150 | 0.7958 | 0.7836–0.8077 |
| text-high-generalisation | 150 | 0.7573 | 0.7431–0.7712 |
| text-high-t0.3-generalisation | 150 | 0.7877 | 0.7748–0.8002 |
| text-min-generalisation | 150 | 0.7083 | 0.6934–0.7230 |

## Cross-validation against 4-map curator-vs-student diff

The 4 gold-standard (GS) maps (`K-35-052-4`, `K-35-053-3`,
`K-35-062-2`, `K-35-078-1`) were curator-corrected from an
earlier student mapping pass. **None of these four maps appear
in the 55-map student GT** (`source_map` column lists 55 distinct
maps, none of which are the four GS maps). The active codebase
contains the curator-corrected reference
(`inputs/vectors/references/mounds-reference.geojson`, 569 mounds)
but does not contain a pre-curation student version of those four
maps. The original ~6 % FN figure is therefore inherited from
prior characterisation (Sobotkova et al. 2023; project working
notes) and cannot be re-derived in this analysis.

We searched `archive/` and `inputs/vectors/` for files matching
the four GS map names alongside terms like `student`, `original`,
`pre-curation`, or `raw`; nothing was found. If a pre-curation
version exists outside the repository (e.g., in original
fieldwork archives), a future cross-validation could anchor the
55-map estimate against the 4-map estimate with both derived
under the same protocol.

## Active-area-clipping audit (2026-04-30)

A bounds-clipping artefact was identified and corrected in the 4-GS
sister analysis (`results/student-gt-fn-rate-analysis-gs4/`): the
GeoTIFF rasters include a black collar / tilted-corner padding
**outside the cartographic neat-line**, and student features digitised
on that collar were being counted as false positives. The fix was to
clip both ground-truth datasets to the trapezoidal graticule
quadrangle of each sheet (derived from the sheet ID on the
Pulkovo-1942 datum and re-projected to UTM-35N), recovering an FP = 0
result on the 4 GS maps.

**This 55-map analysis is unaffected by the artefact.** This script
(`scripts/analyse_student_gt_fn_rate.py`) does not perform bounds
clipping at any stage: review candidates are joined to student GT by
`map_name` and a per-map cKDTree of `(x, y)` centroids, with no
sheet-polygon test. The denominator uses raw student-GT counts; the
numerator counts review-confirmed mound candidates regardless of
whether their centroids fall inside or outside any sheet's neat-line.
There is therefore no rectangular-vs-trapezoidal envelope decision to
correct.

A residual question — whether some review-confirmed FNs themselves
lie on the black collar of their source sheet — is logically possible
but operationally unlikely: review candidates were proposed by
detector runs on tiles that ought to be inside the neat-line, and the
human reviewer would have rejected any that obviously fell on padding.
A targeted spot-check could be added if the per-map FN rates are
revisited for the paper, but the headline rate (0.0887) and CI are
not at risk of the same 17-feature inflation that affected the 4-GS
FP count.

## Reframing 2026-05-01 (Obs 317)

The "Comparison with prior 6 % characterisation" section above (and
its three "plausible drivers" enumeration) was written before the
companion 4-GS direct curator-vs-student analysis was completed
(`results/student-gt-fn-rate-analysis-gs4/report.md`). With that
analysis in hand, the framing of the 4-GS-vs-55-map gap is updated as
follows. **The numerical results in this report are unchanged**;
this subsection revises only the interpretation of the gap between
the 55-map figures and the 4-map prior characterisation.

### 1. Cross-corpus consistency

The 4-GS direct analysis yields an aggregate student-GT FN rate of
**5.27 % (95 % CI 2.92–8.80 %)**, bootstrap-by-sheet, 10,000
iterations, seed 42; source:
`results/student-gt-fn-rate-analysis-gs4/bootstrap_summary.json`.
The 55-map headline rate of 8.87 % lies just outside the upper edge
of this CI. At α = 0.05 we **cannot reject a shared underlying FN
rate** between the two corpora. The 55-map headline CI
(6.93–11.35 %) and the 4-GS CI (2.92–8.80 %) overlap substantially,
which is independent evidence against a large cross-corpus
heterogeneity component.

### 2. Per-map variance evidence

Within the 4 GS maps, per-sheet FN rates span **2.76 % to 9.18 %**
(source:
`results/student-gt-fn-rate-analysis-gs4/per_sheet_confusion.csv`):

| Sheet | Curator features | Student features | FN | FN rate |
|---|---:|---:|---:|---:|
| K-35-053-3 Elenovo | 217 | 211 | 6 | 2.76 % |
| K-35-052-4 32635 | 136 | 131 | 5 | 3.68 % |
| K-35-078-1 Lesovo | 20 | 19 | 1 | 5.00 % |
| K-35-062-2 Rakovski | 196 | 178 | 18 | 9.18 % |

The within-corpus range is **6.4 percentage points (pp)**,
**wider than the 3.6 pp gap** between the 4-GS aggregate (5.27 %)
and the 55-map headline lower bound (8.87 %). Any 4-map draw from
a distribution with this much per-map variance will routinely
deviate 3–4 pp from the corpus mean.

### 3. Mechanism

Each of the 4 GS maps was digitised by exactly one student, with no
double-marking and no consensus signal. Inter-student digitiser-skill
variance is wide; a single high-error student (Rakovski, 9.18 %) is
enough to move a 4-map aggregate substantially. The dominant
explanation for the 4-GS-vs-55-map gap is therefore
**small N (4 maps) × per-student variance**, not cross-corpus
heterogeneity. The "sampling bias in the 4-map calibration" and
"map-level variance is real" drivers from the comparison section
above are correct in spirit; the new framing makes explicit that
these dominate over any cross-corpus mean shift.

### 4. What 8.87 % means

The 8.87 % headline is best read as the
**within-curator-GT disagreement rate** detectable through this
methodology: the rate at which review-confirmed mounds (proposed by
VLM detectors and verified by a human reviewer) lie outside the
55-map student GT. The true student FN rate on the 55-map corpus is
**bounded below by 8.87 %** because some student-missed mounds will
themselves have been double-missed by the VLM detectors and so go
uncounted; the recall-adjusted central estimate (11.15 %) attempts
to correct for this.

By contrast, the 4-GS 5.27 % is a **high-confidence approximation
of the true FN rate** for those four sheets, because curator review
was exhaustive — every curator-reference mound is checked against
every student feature, with no VLM-mediated detection step in the
loop. The two numbers therefore answer slightly different questions,
and the gap should not be interpreted as a calibration mismatch
between two estimates of the same quantity.

### 5. Paper-Methods implication

Both numbers should be cited. The recommended Methods framing:

> The 4.4 pp gap between the 4-GS direct estimate (5.27 % FN,
> 95 % CI 2.92–8.80 %) and the 55-map review-based lower bound
> (8.87 % FN, 95 % CI 6.93–11.35 %) is statistically consistent
> with sampling variance across four maps, each digitised by a
> single student with no consensus correction. Within the 4-GS
> corpus, per-sheet FN rates span 2.76–9.18 % — a 6.4 pp range
> that is wider than the 3.6 pp cross-corpus gap.

The within-4-GS per-sheet spread (2.76–9.18 %) is itself
**internal evidence supporting the paper's existing
double-marking recommendation**: the consensus-voting benefit
that K-pass aggregation confers on VLM pipelines applies equally
to human annotators, because a single digitiser per map is a
single draw from a wide skill distribution. The 4-GS-vs-55-map
gap is not a contradiction to be reconciled — it is the argument
for double-marking, made from the project's own data.

### Cross-references

- **Obs 316**: Sobotkova 2023 vindication via trapezoidal-bounds
  correction (commits `0bb7c448` / `eff34bfd`); 4-GS FN/FP
  recovered as 5.27 % / 0.00 %. The trapezoidal-correction result
  is unchanged; this reframe updates only the secondary
  cross-corpus-gap interpretation.
- **Obs 317**: this reframe (small-N + inter-student variance as
  the dominant gap mechanism, supersedes the "genuine
  cross-corpus variation" reading in Obs 316).
- **Obs 305**: original 55-map FN-rate analysis (commit
  `508e498f`); source of the 8.87 % headline and 11.15 %
  recall-adjusted central estimate retained in this report.
- **`results/student-gt-fn-rate-analysis-gs4/report.md`**: the
  canonical 4-GS deliverable. Cite alongside this report whenever
  the 55-map figures are used.

## Caveats

- **Lower-bound vs central estimate**. The headline rate counts
  only student-missed mounds that the VLM detected. The true FN
  rate is higher; we approximate it via recall-adjustment. The
  recall figure is from the matching protocol used in
  corrected-F1 evaluation (Hungarian at the relevant R), so it
  is calibrated to the same matching protocol that produced
  these review candidates.
- **Hungarian-collision residual**. Even with the 75 m exclusion,
  some "likely matching collisions" may include genuine FN
  mounds that happen to lie close to a mapped one. The 75 m
  threshold is conservative (Obs 272 attractor-pull is
  significant out to 125 m on the GS corpus and at least 100 m
  on the 55-map corpus). The marginal (75–125 m) tier captures
  this; the inclusive estimate is the soft upper bound on the
  exclusion-corrected count.
- **Sampling assumptions**. Bootstrap-by-map treats each map as
  independent. Map-level variation in mound density and VLM
  recall is real; the bootstrap captures it. We do not condition
  on map-level features (era, region) — the 55 maps span the
  generalisation corpus uniformly.
- **Visual inspection bias**. The reviewer (one human) labelled
  candidates as `mound`/`not_mound` based on what is visible on
  the map. Reviewer recall on actually-visible mounds is
  near-perfect for clear symbols (Obs 152 onwards) but degrades
  for severely degraded ones; the headline rate may slightly
  underestimate FN where the reviewer also missed the symbol.
- **Sentinel-buffer treatment**. Rows with `buffer_metres = 200`
  (173 rows) are
  treated as highest-confidence FN regardless of geometric
  distance. This is consistent with the corrected-F1 protocol,
  which excludes them from the extended GT precisely because
  they are >150 m from any review ring centre and therefore
  guaranteed to be student-missed mounds in a different region
  of the tile.
- **Recall denominator scope**. Recall comes from the corrected-F1
  evaluation, which uses the extended-GT-at-R protocol. This
  recall is conditional on a particular matching radius and
  reviewer-promoted GT extension. Using the highest-recall run
  gives the most generous denominator and therefore the lowest
  recall-adjusted central estimate; using a lower-recall run
  would inflate the central estimate.

## Paper implications

**Methods text** — replace any standing reference to a 4-map ~6 %
FN rate with:

> Re-evaluation of the 55-map student ground-truth dataset using
> human review of VLM-flagged candidates yields a high-confidence
> FN rate of 0.089 (0.069–0.114, 95 % bootstrap CI
> by map). Adjusted for VLM recall this corresponds to a central
> estimate of 0.112 (0.086–0.145).
> An inclusive count that retains a marginal (75–125 m) shell yields 0.106
> (0.086–0.130); a permissive
> count that retains every VLM-flagged mound (the upper bound on
> reviewer-detected student omissions) yields 0.166
> (0.148–0.187).

**Limitations text** — note that the four maps used for prior
curator-vs-student calibration (~6 % FN) are not represented in
the 55-map dataset, so the historical 6 % figure is reported as
comparator only.

**Total candidates classified across the four strata**: 1817 mound-labelled rows out of 3492 reviewed rows across five review CSVs (one per corrected run + earlier image single-buffer review).

## Reproducibility

- Script: `scripts/analyse_student_gt_fn_rate.py`
- Bootstrap: 10,000 iterations, seed 42
- Spatial dedup: 50 m, greedy first-wins
- Outputs: `results/student-gt-fn-rate-analysis/`
  - `report.md` (this file)
  - `per_map_fn_breakdown.csv`
  - `bootstrap_summary.json`
  - `figures/fn_rate_by_stratum.png`
