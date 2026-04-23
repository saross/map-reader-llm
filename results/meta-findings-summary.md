# Meta-findings summary — synthesis of Observations 262–273

**Created**: 2026-04-23
**Purpose**: Paper-Discussion-shaped synthesis of the 2026-04-20/21
human-review day's cross-cutting findings, framed for direct use during
manuscript drafting. Supersedes scattered cross-references across
`docs/notes/reflections/working-notes.md` Obs 262–273 and the eight
rendered per-analysis reports listed in §2 as the canonical narrative
surface for the paper's Discussion and portions of the Results.
**Scope**: the 1,028-candidate VLM-only slice of the 55-map image
generalisation run (`outputs/55maps-image-generalisation/` +
`results/55maps-image-generalisation/`) and the 4-map gold-standard
subtype analysis (`results/gold-standard-subtype-classification/`). UK /
Australian English throughout; no archive/ citations; E47 distinguished
whenever referenced.

## 1. Executive summary

The human-review day's findings decompose into five themes, each mapping
to one or more paper Discussion paragraphs:

- **T1 — Human-review calibration and the corrected-F1 lower bound.** The
  pipeline's 55-map image-generalisation measured F1 = 0.771 at 50 m rises
  to **F1 ≥ 0.830** under per-item human review of 1,028 VLM-only
  candidates (95 % bootstrap CI on review-label variability [0.826,
  0.833]; 472 / 1,028 = 45.9 % reviewer-promoted to true positive). The
  calibrated-tolerance review UI shifts 21.4 % of in-sample judgements
  one-directionally toward the conservative label (Obs 268), confirming
  that 0.830 is a defensible lower bound, not a point estimate.

- **T2 — Failure-mode taxonomies at production scale.** Three mechanistically
  distinct failure families dominate the 556 confirmed false positives:
  **centroid-pull** toward salient non-target text and features (Obs 264),
  **contour-ring / closed-summit confounds** (Obs 265), and
  **subtype-boundary failures** where detection is correct but subtype
  assignment crosses a class boundary (Obs 266). All three are
  high-verifier-confidence failures, not low-signal noise.

- **T3 — Verifier miscalibration.** The pipeline verifier's probability
  output has **ECE = 0.269** and **AUC = 0.655** against human-review
  labels — poorly calibrated at the high end (empirical P(mound) ≈ 0.55
  at the p = 1.00 bin) and heavily quantised (13 distinct probability
  values across 1,028 candidates). The verifier cannot filter the T2
  failure modes because its probability is saturated where those failures
  live.

- **T4 — Subtype classification: strong aggregate, sharp asymmetric
  failure.** On the 4-map gold-standard subset, conditional on a correct
  detection, subtype weighted-F1 is **0.887 [0.849, 0.922]** with Level-1
  accuracy = 1.000. However, the Level-2 error is dominated by a single
  asymmetric cell: **benchmark_mound → triangulation_mound at 27 / 47
  matched benchmarks (57 %)**, with the reverse cell empty. Five
  independent passes agree confidently on the wrong label — this is
  systematic, not noise.

- **T5 — Attractor-pull spatial scale and Dawid-Skene aggregate
  inadequacy.** The attractor-pull that drives the corrected-F1 lower
  bound is statistically distinguishable from within-tile random
  placement out to **~125 m** (shell-wise permutation test; p = 0.381 at
  the (125, 150] m shell with bias correction). Dawid-Skene aggregate
  estimation of the VLM-only rate is **prior-invariant at AUC = 0.500**
  — 2-annotator identifiability collapses every item onto the same
  posterior — so human adjudication, not D-S, is the only working
  per-item signal on this slice.

Read in the order T1 → T2 → T3 → T4 → T5 for the Discussion; T1 and T5
bracket the main headline, T2–T4 sit between them as failure-mode
drill-downs.

## 2. Scope and data

### 2.1 Candidate populations

- **55-map image-generalisation VLM-only set** (T1, T2, T3, T5): 1,028
  candidates produced by the 5-pass gemini-3-flash image proposer + v1
  verifier pipeline on `outputs/55maps-image-generalisation/`; all
  human-reviewed twice (first pass 2026-04-19 uncalibrated; full
  calibrated pass 2026-04-20 with 50 m tolerance-circle UI). The 472
  reviewer-promoted true positives at 50 m + 274 additional reviewer
  promotions at R > 50 m (today's multi-buffer pass) give 746 total
  reviewer-promoted real mounds from this candidate set.
- **4-map gold-standard set** (T4 only): `outputs/h11/gold-standard-v2/`
  proposer consensus against the 569 expert-digitised features in
  `inputs/vectors/references/reference_*.geojson` (burial 456 /
  benchmark 65 / triangulation 43 / settlement 5).

### 2.2 Observation → theme mapping

| Theme | Obs | Role |
|---|---|---|
| T1 | 262 | Edge-case narrative — benchmark-on-burial-mound on a settlement mound; illustrates review-caught features no algorithm can infer |
| T1 | 263 | Crop-review ambiguity band; 21 % flip rate context and reviewer-conservative bias |
| T1 | 267 | Headline corrected-F1 lower bound (F1 ≥ 0.830 at 50 m) |
| T1 | 268 | Empirical confirmation of lower-bound claim via uncalibrated-vs-calibrated cross-tab |
| T2 | 264 | Centroid-pull toward salient text and features (figures 03836 / 04108 / 04275 / 04365 / 04245 negative control) |
| T2 | 265 | Contour-ring / closed-summit "typical confound" FP class |
| T2 | 266 | Subtype-boundary qualitative taxonomy (three sub-patterns) |
| T3 | 269 | Verifier calibration crosstab — ECE 0.269 / AUC 0.655 / 13-value quantisation |
| T4 | 270 | Subtype weighted-F1 0.887 headline + consensus-threshold null |
| T4 | 271 | Asymmetric benchmark → triangulation confusion (mechanistic drill-down) |
| T5 | 272 | Attractor-pull scale ~125 m (shell permutation null) |
| T5 | 273 | D-S aggregate structural inadequacy at any prior |

### 2.3 Canonical numbers used in this document

All numbers below are pulled directly from primary artefacts (paths in
the right-most column). No value in this document is re-derived; every
value is copied-and-cited. Where `paper-tables/metrics_master.json` has
an aggregated entry, that is the canonical citation; otherwise the
per-analysis JSON is primary.

| Claim | Value | Source |
|---|---|---|
| 55-map image measured F1 @ 50 m | 0.771 [0.760, 0.782] | `outputs/55maps-image-generalisation/evaluation/evaluation.json` → `summary.buffers[3]` |
| 55-map image corrected F1 @ 50 m (human-reviewed) | **0.830** [0.826, 0.833] | `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.json` |
| 55-map multi-buffer corrected F1 curve | 0.832 / 0.848 / 0.852 / 0.854 / 0.855 @ 50 / 75 / 100 / 125 / 150 m | `results/55maps-image-generalisation/corrected-f1-multi-buffer/summary.json` → `results[*].F1` |
| Practitioner-useful cap (attractor-truncated) | 0.854 @ R = 125 m | same as above |
| Review-set size | 1,028 VLM-only candidates | `results/55maps-image-generalisation/human-review.csv` + `.../human-review-multi-buffer.csv` |
| Phantom TPs at 50 m | 472 (45.9 %) | same + Obs 267 |
| Confirmed FPs | 556 (54.1 %) | same |
| Reviewer-promoted at R > 50 m | 274 additional | `human-review-multi-buffer.csv` + Obs 272 shell counts |
| Total reviewer-promoted real mounds | 746 (472 + 274) | as above |
| UI-flip rate (uncal → cal) | 21.4 % [17.1 %, 26.0 %], all one-directional | `results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.json` |
| Verifier ECE | 0.269 | `results/55maps-image-generalisation/verifier-calibration-crosstab/calibration.json` → `ece` |
| Verifier AUC | 0.655 [0.622, 0.687] | same → `auc.point`, `auc.ci_95` |
| Verifier distinct probability values | 13 | same → inspected from calibration table |
| P(mound \| p ≤ 0.25) | 0.174 [0.127, 0.224] | same → low-p tail |
| Attractor-pull shell (125, 150] p-value | **0.381** (bias-corrected) | `results/55maps-image-generalisation/buffer-band-lift/shell.csv` |
| Cumulative lift at R = 125 m | 24× observed vs corrected null | `results/55maps-image-generalisation/buffer-band-lift/summary.json` |
| Subtype weighted-F1 (4-map GS) | **0.887** [0.849, 0.922] | `results/gold-standard-subtype-classification/macro_weighted_summary.json` |
| Level-1 accuracy (mound-family vs settlement, matched pairs) | 1.000 | `results/gold-standard-subtype-classification/hierarchical_decomposition.json` |
| Benchmark → triangulation cell | 27 / 47 (57 %) | `results/gold-standard-subtype-classification/confusion_matrix_4x4_buf50.csv` |
| Reverse triangulation → benchmark | 0 / 33 (0 %) | same |
| D-S VLM-only posterior (v1, fixed prior 0.05) | 0.1862 (degenerate single value) | `results/55maps-image-generalisation/dawid-skene/dawid-skene-results.json` + Obs 273 |
| D-S AUC (any prior, VLM-only slice) | **0.500** (prior-invariant) | `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/summary.json` + Obs 273 |
| Empirical mound rate on VLM-only slice | 0.7247 (745 / 1,028) | `results/55maps-image-generalisation/ds-human-crosstab/summary.json` |
| 55-map text-HIGH raw F1 @ 50 m | 0.788 [0.777, 0.800] | `outputs/55maps-text-high-generalisation/evaluation/evaluation.json` |
| 55-map text-MIN raw F1 @ 50 m | 0.759 [0.747, 0.772] | `outputs/55maps-text-min-generalisation/evaluation/evaluation.json` |
| Paired text-HIGH vs image @ 50 m | ΔF1 = −0.018, p = 0.0008 (significant) | `results/55maps-cross-track-comparison/paired-image-vs-text-high-50m/pairwise_permutation_result.json` |
| Paired text-MIN vs image @ 50 m | ΔF1 = +0.012, p = 0.0543 (n.s. — marginal image advantage) | `results/55maps-cross-track-comparison/paired-image-vs-text-min-50m/pairwise_permutation_result.json` |
| Text-HIGH buffer plateau (50 → 125 m) | +0.007 F1 (0.788 → 0.795) | `outputs/55maps-text-high-generalisation/extended-buffer-eval/evaluation.json` |
| Text-MIN buffer plateau (50 → 125 m) | +0.007 F1 (0.759 → 0.766) | `outputs/55maps-text-min-generalisation/extended-buffer-eval/evaluation.json` |
| 55-map paper-headline F1 | **0.904** [0.878, 0.928] @ 50 m (487-tile matrix, text-HIGH + PV) | `results/paper-tables/metrics_master.json` (separate from the 55-map slice — see §8) |

## 3. Theme T1 — Human-review calibration and the corrected-F1 lower bound

### 3.1 Findings

The 1,028 VLM-only candidates are the set of 5-pass consensus detections
from the 55-map image-generalisation run that did NOT match any student
ground-truth mound at the 50 m buffer under Hungarian one-to-one
matching. Per-item human review with a calibrated 50 m tolerance-circle
UI re-classified **472** of them (45.9 %) as real mounds the students had
missed. Recomputing F1 at 50 m under an extended GT (student GT + 472
reviewer-promoted TPs) yields a corrected F1 of **0.8295** (rounds to
0.830) at the 50 m buffer — an absolute increase of +0.0585 over the
measured F1 of 0.771 on the same-corpus Hungarian accounting. Precision
rises from 0.780 to 0.881 (+0.101); recall rises only from 0.763 to 0.784
(+0.021) because the phantom TPs also extend the GT denominator.

An independent cross-tabulation of the 327 candidates reviewed under
both an uncalibrated UI (binary accept/reject on crop alone) and the
calibrated tolerance-circle UI shows that **21.4 %** (70 / 327; 95 % CI
[17.1 %, 26.0 %] over 10 000 bootstrap iterations) of labels flipped
between UIs, and **100 % of flips were one-directional** (Uncal = mound →
Cal = not_mound). The calibrated UI uniformly tightens reviewer
judgement. Combined with the reviewer's asymmetric decision policy on
ambiguous cases ("if in doubt, reject" — see Obs 263 candidate_02400
exemplar vs candidate_06479 self-calibration), this empirically
establishes 0.830 as a **defensible lower bound**, not a point estimate.

The multi-buffer extension of this correction — re-running the extended-
GT Hungarian matcher at R = 50, 75, 100, 125, 150 m with reviewer-
promoted phantoms at each R — yields a corrected F1 curve of
**0.832 / 0.848 / 0.852 / 0.854 / 0.855**. The 150 m endpoint is
qualified by T5's attractor-pull scale finding; the practitioner-useful
cap is R = 125 m at F1 = 0.854.

### 3.2 Mechanism

The per-item human reviewer operates with three advantages over any
automated corrector the project has considered:

1. **Context**: the reviewer sees the tolerance-circle-overlaid crop and
   can resolve "is this candidate close enough to a symbol?" as a
   geometric check rather than a fuzzy visual judgement (the UI
   tightening effect quantified by Obs 268).
2. **Class boundaries**: the reviewer can distinguish benchmark, triangulation,
   burial, settlement, and "not_mound" under the project's working
   symbol-convention catalogue, including edge cases like Obs 262's
   benchmark-on-mound-on-tell superposition that cannot be inferred from
   the symbol alone.
3. **Asymmetric conservatism**: when genuinely ambiguous, the reviewer
   defaults to not_mound. This biases the correction toward
   under-counting real mounds in the ambiguous band rather than
   over-counting, which is the honest direction for a lower bound.

Dawid-Skene aggregate estimation of the same quantity — "what fraction
of the VLM-only slice are real mounds?" — under-counts by a factor of
approximately 2.5 (D-S posterior ~18.1 % real vs human 45.9 %). T5 §7
documents why this is structural, not a tunable-prior issue: 2-annotator
D-S is rank-uninformative by design, and every tested prior yields
AUC = 0.500.

### 3.3 Evidence

- Headline numbers in §2.3 canonical table above.
- Per-item review CSVs: `human-review.csv` (1,028 rows @ 50 m) +
  `human-review-multi-buffer.csv` (557 rows re-reviewing not-mound
  candidates at R ∈ {50, 75, 100, 125, 150, > 150} m).
- Rendered reports: `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.md`
  (the 50 m correction); `results/55maps-image-generalisation/corrected-f1-multi-buffer/report.md`
  (the multi-buffer curve, including the Obs 272 cap at 125 m);
  `results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.md`
  (the 21 % flip-rate analysis).

### 3.4 Caveats

- **50 m-only validity (first correction)**: the Obs 267 50 m correction
  records binary in/out-of-circle judgements only; it does not locate
  symbol centres within the circle, so tighter-buffer F1 values cannot
  be derived from that output alone. The multi-buffer correction (Obs
  272's paired review) re-reviewed only candidates originally labelled
  not_mound at 50 m, stratified by R ∈ {75, 100, 125, 150, > 150} m.
- **CI incompatibility**: the measured 95 % CI on F1 bootstraps
  tile-level pipeline-matching variability; the corrected 95 % CI
  bootstraps reviewer-label variability. They quantify different
  uncertainty sources and should NOT be combined by intersection or
  union.
- **Reviewer noise floor**: roughly 10–15 % of per-item decisions in
  the ambiguous band carry reviewer-level noise (Obs 263 qualitative
  estimate; partly corroborated by the 21 % one-directional flip rate
  in Obs 268). The corrected F1 is a reviewer-consistent estimate, not a
  ground-truth correction.
- **Extended-GT denominator**: adding 472 phantom TPs to the GT
  denominator means recall ceilings are tighter than the measured
  recall would suggest. The +0.021 recall delta reflects this, not a
  genuine recall loss.
- **Image-track only**: the corrected-F1 ≥ 0.830 is specific to the
  image track. Text-HIGH and text-MIN tracks were not subjected to
  per-candidate human review (see
  `results/55maps-cross-track-comparison/report.md` §4), so their
  corrected F1 is not available. Equivalent review would likely lift
  their corrected F1 similarly — text-HIGH's raw F1 of 0.788 at 50 m
  plus an image-style +0.059 raw-to-corrected gap would place
  text-HIGH's corrected F1 in the 0.82–0.85 range — but this is an
  extrapolation, not a measurement.
- **Student-GT position noise quantified at ~25–35 m**: the
  extended-buffer F1 curve on the 4-map curator-annotated
  gold-standard (`gold-standard-extended-buffer-sweep/
  extended-buffer-report.md`) plateaus at 25 m (F1 = 0.822); the
  55-map student-GT F1 curve has not plateaued by 50 m (F1 = 0.788
  at 50 m). The ~25–35 m rightward shift is the empirical signature
  of student-annotator position jitter on the 55-map GT — 4–5 px
  (≈ 20–25 m at the 384-px tile scale) of centroid noise. This is
  additive to the 45.9 % phantom-TP rate from per-candidate review;
  both push the raw 0.771 figure below the corrected ≥ 0.830.
- **Cross-modality paired significance** (Session 77 2026-04-24):
  the paired permutation tests across the three tracks
  (`results/55maps-cross-track-comparison/paired-image-vs-text-*`;
  10,000 permutations, seed 42) establish that **text-HIGH
  significantly outperforms image at every buffer 20–50 m** (ΔF1 =
  −0.118 → −0.018; all p ≤ 0.001); **text-MIN beats image at tight
  buffers but converges with image at R ≥ 40 m** (p = 0.34 at 40 m;
  p = 0.054 at 50 m). Text-track extended-buffer evaluations show
  both text tracks plateau by 75 m (gain only +0.007 F1 from 50 →
  125 m; cf. image's corrected +0.022). Image-track buffer
  sensitivity is therefore a modality property (spatial imprecision
  of image-proposer outputs), not a GT-noise artefact; text tracks
  do not have the same buffer-dependency.

### 3.5 Suggested paper text

> The pipeline's measured F1 on the 55-map image-generalisation set is
> 0.771 at the 50 m tolerance buffer under Hungarian one-to-one matching
> against student ground truth. Per-item human review of the 1,028
> VLM-only candidates (detections that did not match any student-labelled
> mound at 50 m) — conducted under a calibrated 50 m tolerance-circle UI
> — reclassifies 472 of them (45.9 %) as real mounds the students had
> missed, raising corrected F1 at 50 m to F1 ≥ 0.830 (95 % review-label
> bootstrap CI [0.826, 0.833]). The correction is a lower bound: an
> independent cross-tabulation of the 327 candidates reviewed under both
> an uncalibrated and the calibrated UI shows that 21.4 % of labels
> flipped between UIs (95 % CI [17.1 %, 26.0 %]), with every flip in the
> direction Uncal = mound → Cal = not_mound, and the reviewer's policy
> on genuinely ambiguous cases was conservative ("if in doubt, reject").
> Extending the correction to wider buffers yields F1 = 0.832 / 0.848 /
> 0.852 / 0.854 / 0.855 at R = 50 / 75 / 100 / 125 / 150 m; the
> practitioner-useful cap is R = 125 m (§T5) at F1 = 0.854.

**Intended position**: Discussion, first numeric paragraph (sets the
corrected-F1 lower bound before any failure-mode or verifier analysis).

**Figure / table references**: Table of the multi-buffer corrected-F1
curve (from `corrected-f1-multi-buffer/summary.json`); reliability of
uncal-vs-cal flip-rate as inline statistic.

**Trace**:

- Obs anchors: `docs/notes/reflections/working-notes.md:§Obs 262`,
  `§Obs 263`, `§Obs 267`, `§Obs 268`.
- Artefacts: `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.json`,
  `results/55maps-image-generalisation/corrected-f1-multi-buffer/summary.json`,
  `results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.json`.
- Canonical number source: see §2.3 (measured F1 from
  `evaluation.json:summary.buffers[3]`; corrected F1 from
  `corrected-f1-human-reviewed.json`; flip rate from
  `crosstab.json:rates.disagreement_rate`).

## 4. Theme T2 — Failure-mode taxonomies at production scale

### 4.1 Findings

The 556 candidates that remained confirmed false positives after human
review fall into three mechanistically distinct failure families, all at
high verifier confidence (the majority sit in the p = 1.00 bin — see
T3). Each family was characterised during the human-review day on
**dozens of exemplars**; an atlas of roughly 70 exemplar figures under
`docs/paper/figures/review-app-examples/` covers the three families at
severity gradients from sub-threshold to severe.

**Family 1 — Centroid-pull attractors (Obs 264)**. The pipeline
correctly identifies that a mound is present but the reported centroid
is biased toward a nearby salient non-target feature — numeric or
Cyrillic text labels, contour intersections, water features, road
junctions, or clusters of mixed cartographic clutter. Under the 50 m
buffer the detection still matches; under tighter 20 m buffers it
misses. This produces the image track's documented buffer elasticity
(Obs 252: 8.6 – 21.5 % F1 swing across 20–50 m). Three attractor
sub-categories were mechanistically distinguished: text-label pull
(dominant; generalises across numerals, Cyrillic text, and compound
symbols — e.g. Cyrillic "0 КМ" on candidate_04365), feature-clutter
pull (e.g. candidate_04592, centroid between road + stream + contour),
and contour-line pull (e.g. candidates 04661 / 04809, with the real
mound symbol visible outside the tolerance circle and brown contour
lines inside it).

**Family 2 — Contour-ring / closed-summit confounds (Obs 265)**. The
pipeline produces high-confidence detections on features whose visual
signature approximates the mound symbol — ring-shaped contour closures,
small enclosures, or circular topographic markers — but that lack the
specific cartographic convention of the ringed-mound symbol. The confound
class is heterogeneous: eight documented sub-types include contour
intersections forming a mound-like vertex, printing artefacts, composite
number + slope-hatching cases, road-junction radiating-orange-line
patterns, compact cross / landmark symbols, letters within place-name
labels classified as mounds, right-shape-wrong-colour symbols, and dark
built-structure features classified as `settlement_mound`. No single
visual pattern dominates; the pipeline is responding to a broad
equivalence class of cartographic accidents that share *some* property
of the mound symbol.

**Family 3 — Subtype-boundary failures (Obs 266, quantified in T4)**.
Detection is robust (the pipeline agrees a mound is present) but the
subtype boundary is crossed: plain surveying markers classified as
compound-on-mound, built-environment features classified as
`settlement_mound`, or real tells classified as the simpler
`burial_mound`. Unlike Family 1 and Family 2, this family does not
inflate the FP count — the candidate still matches a nearby GT mound —
but it drives the Level-2 subtype errors quantified in T4.

### 4.2 Mechanism

Families 1 and 2 share a common mechanism that a narrow prompt fix
cannot address: VLM attention is weighted by visual saliency within the
crop, not anchored on the target symbol specifically. The decision
"where is the mound in this crop?" is coupled to every salient feature
present — labels, contour structures, adjacent text of any type, colour
signatures — and the centroid leaks toward whichever feature is most
visually dominant. Candidate_06937 (where the VLM correctly inferred a
mound exists in a distorted crop but reported the centroid on an adjacent
number) is the cleanest case for **detection / localisation dissociation**
in the current single-output formulation.

Family 3's three sub-patterns each have a distinct mechanism:
compound-boundary over-assignment (plain → compound-on-mound) reflects
the VLM treating a marker symbol as sufficient evidence for the
compound class; settlement-class over-assignment reflects `settlement_mound`
functioning as a catch-all for built-structure features; settlement-class
under-assignment (real tell → `burial_mound`) reflects the tell
signature collapsing to the more common class. The five-pass consensus
does not repair any of these — the same systematic attractor operates
across every pass.

### 4.3 Evidence

- Obs 264 figure atlas at `docs/paper/figures/review-app-examples/`
  (18 figures documenting the centroid-pull severity gradient and
  attractor sub-categories; negative control 04245 showing the bias is
  statistical not deterministic).
- Obs 265 sub-category table at `docs/notes/reflections/working-notes.md`
  §Obs 265 (heterogeneity across eight sub-types).
- Obs 266 qualitative table + Obs 270 quantitative confusion matrix at
  `results/gold-standard-subtype-classification/confusion_matrix_4x4_buf50.csv`
  (see T4 §6 for detail).
- Reviewer free-text notes on "dozens" of each failure family during the
  calibrated review (2026-04-20).

### 4.4 Caveats

- **Exemplar count is not a proportion.** The reviewer's atlas of ~70
  figures is not a random sample; it is a curated taxonomy of observed
  patterns. The absolute share of each family within the 556 confirmed
  FPs is not yet quantified from the review CSV's `symbol_type` column.
  A follow-up tally (Obs 265 §Follow-up) would quantify this but is not
  required for the paper's error-taxonomy discussion.
- **Architecture-level vs prompt-level**: Family 1 specifically argues
  against prompt-narrow fixes ("ignore numbers"). The generalisation to
  Cyrillic text and to non-text attractors (contour lines, road
  junctions) in the captured exemplars supports that diagnosis. But the
  Level-3 (strong future direction) proposal — decoupled
  detection/localisation architecture — is not attempted in this paper
  and belongs in future work.
- **Prompt-engineering sufficiency for Family 3**: Obs 266 proposes
  concrete prompt fixes for sub-patterns 1 and 2 (visual negatives for
  plain markers, attention to tell hatching). These are not implemented
  in this paper; the subtype-specific F1 in T4 reflects the current
  prompt.

### 4.5 Suggested paper text

> Among the 556 candidates confirmed as false positives under human
> review, we identify three mechanistically distinct failure families
> that together account for the full atlas of observed patterns and that
> are individually characterised on dozens of exemplars (`docs/paper/figures/review-app-examples/`).
> First, centroid-pull: the VLM correctly identifies a mound is present
> but reports a centroid biased toward a nearby salient non-target
> feature — numeric labels, Cyrillic text, contour-line intersections,
> water features, or feature clutter — producing the image track's
> buffer elasticity. The bias generalises across attractor types (our
> atlas includes numeric, Cyrillic, and non-text cases with and without
> colour match), arguing against a narrow prompt fix. Second, contour-ring
> and closed-summit confounds: high-confidence detections on features
> whose visual signature approximates the ringed-mound symbol but lack
> its specific cartographic convention — a heterogeneous class including
> contour intersections, printing artefacts, and built-structure
> features. Third, subtype-boundary failures: detection is correct but
> the subtype assignment crosses a class boundary (plain surveying
> markers upgraded to compound-on-mound; built environment mapped to
> `settlement_mound`; tells collapsed to `burial_mound`) — these are
> quantified separately on the 4-map gold-standard set (§T4). None of
> the three families is filtered by the verifier's probability output
> (§T3), because the verifier is saturated where these failures live.

**Intended position**: Discussion, error-taxonomy paragraph; one of the
Methods/Results tables citing the 70-figure atlas by directory, with
2–3 headline exemplars in the figure panel.

**Figure / table references**: Figure panel with centroid-pull severity
gradient (candidates 04245 negative control, 04275 sub-threshold, 03836
at-threshold, 04108 severe, 04365 Cyrillic text generalisation — five
panels in total for Family 1). Optional panel for Family 2 heterogeneity
showing 2–3 sub-types side by side.

**Trace**:

- Obs anchors: `docs/notes/reflections/working-notes.md:§Obs 264`,
  `§Obs 265`, `§Obs 266`.
- Artefacts: `docs/paper/figures/review-app-examples/*.png` (figure
  atlas); `results/gold-standard-subtype-classification/confusion_matrix_4x4_buf50.csv`
  (Family 3 quantification, cross-reference to T4).
- Canonical number source: confirmed-FP count 556 from Obs 267 headline
  counts (= 1,028 − 472); figure atlas size from Obs 264 and 265 inline
  descriptions.

## 5. Theme T3 — Verifier miscalibration

### 5.1 Findings

Cross-tabulating the 5-pass pipeline verifier's probability output
against the 1,028 human-review labels yields three findings that invert
in-session hypotheses on the verifier's behaviour:

1. **The verifier is over-confident, not under-confident.** Expected
   Calibration Error (ECE) = **0.269**. Every populated probability bin
   above p = 0.30 shows empirical P(mound) well below mean predicted p,
   and the gap widens with predicted confidence: (0.70, 0.90] bin gap
   −0.26, (0.90, 0.95] gap −0.33, (0.99, 1.00] gap −0.45. 370 candidates
   received p = 1.00 ("certain") but only 55 % were real mounds.
2. **Discriminative power is weak.** AUC = **0.6545** (95 % bootstrap
   CI [0.622, 0.687]) — barely better than chance as a binary
   "is-this-a-mound" classifier. In-session anecdotal impressions that
   the verifier was doing "honest work at low p" were artefacts of a
   4/4 small-sample spot-check; at scale the verifier correctly
   discriminates at the low end (P(mound | p ≤ 0.25) = **0.174** [0.127,
   0.224], well below the 0.459 overall prevalence) but fails at the
   high end where most candidates live.
3. **The output is heavily quantised.** Only **13 distinct probability
   values** across 1,028 candidates, with 370 exactly at p = 1.00 and
   180 exactly at p = 0.95. The (0.95, 0.99] bin is empty. This
   eliminates any threshold-triage strategy above p ≈ 0.95.

Per-class Brier score is dominated by the `not_mound` class (Brier 0.524)
— the verifier confidently mis-scores false positives (mean predicted
p = 0.625 for items that are all negatives). Mound-subclass Brier is
well-resolved (0.06–0.09) only because those items are all positives and
mean predicted p ≈ 0.85; the calibration reads "well" because the
reference labels happen to agree with high confidence, not because the
verifier discriminates within the class.

### 5.2 Mechanism

T3 compounds mechanistically with T2. Most confirmed-FP candidates sit
in the p ≥ 0.90 bins where the verifier cannot distinguish the T2
centroid-pulled, contour-ring-confounded, or subtype-boundary-failed
candidates from true positives. A tighter threshold from 0.15 to 0.70
improves within-set precision by +0.11 at the cost of dropping recall to
0.85 — because the verifier's distribution is too quantised to give a
strong sweet spot. The pipeline's precision ceiling is therefore
**architectural, not prompt-level**: the verifier probability cannot
carry the filtering load the pipeline design assigns to it.

### 5.3 Evidence

- Calibration table + reliability diagram + ROC + PR curves at
  `results/55maps-image-generalisation/verifier-calibration-crosstab/`
  (`calibration.json`, `calibration.md`, `reliability-diagram.png`,
  `roc-curve.png`, `pr-curve.png`).
- Bootstrap CIs (10 000 iterations, seed 42) in the JSON's `bootstrap`
  block; stratified threshold-sweep table in the same file.
- Cross-validated against Obs 269's in-session notes — see
  `docs/notes/reflections/working-notes.md:§Obs 269` for the hypothesis-
  reversal narrative (original prediction was under-confidence at low p).

### 5.4 Caveats

- **Ground truth is the human-review labels**, which are themselves
  conservative (T1 §3.4 caveats). The empirical P(mound) values may be
  slightly under-stated relative to an idealised ground truth, but the
  magnitude of the over-confidence gap (−0.26 to −0.45 across high-p
  bins) is far too large to be attributable to reviewer-conservatism
  alone.
- **Symbol-subclass Brier** reads well (0.06–0.09 for burial / benchmark
  / triangulation / settlement) but this reflects the subclass members
  being all positives at mean predicted p ≈ 0.85 — not that the verifier
  discriminates within the mound class. The `not_mound` class Brier
  (0.524) is the honest diagnostic.
- **Generalisation to other runs**: the verifier calibration analysis
  used here is specific to the verifier v1 prompt on the 55-map image
  pipeline. The v2 verifier work is quarantined (per
  `docs/methodology/v2-verifier-contamination-policy.md`) because its
  prompt was calibrated on gold-standard false positives — that run is
  not cited.
- **Cross-track verifier scope**: the text-HIGH and text-MIN tracks
  use the same `verify_adversarial v1` prompt as the image track.
  Verifier-calibration metrics (ECE, AUC, Brier) are NOT re-computed
  for the text tracks because per-candidate human review did not
  extend to them (see T1 §3.4). The T3 conclusions about verifier
  quantisation, over-confidence at the high end, and the modest
  discriminative AUC therefore generalise cleanly to the text tracks
  by inference (same verifier prompt, same verifier-stage quantisation)
  but are empirically anchored on the image-track review.

### 5.5 Suggested paper text

> The pipeline's probabilistic verifier is poorly calibrated on the
> 55-map image generalisation set. Cross-tabulating verifier probability
> against per-item human-review labels on the 1,028 VLM-only candidates
> yields ECE = 0.269 and AUC = 0.655 (95 % bootstrap CI [0.622, 0.687]).
> The distribution is quantised to 13 distinct probability values; 370
> candidates receive p = 1.00 but only 55 % of them are real mounds. The
> verifier discriminates correctly at the low end — P(mound | p ≤ 0.25)
> = 0.174, well below the 0.459 overall prevalence — but fails at the
> high end where most candidates live. Tightening the threshold from
> 0.15 to 0.70 improves within-set precision by +0.11 at the cost of
> a 0.15 recall loss, and the heavy quantisation means thresholds above
> 0.95 do not meaningfully exist. The verifier cannot filter the failure
> modes reported in §T2 because its probability output is saturated in
> exactly the bins where those failures dominate. The pipeline's
> precision ceiling is therefore architectural, not prompt-level: a
> finer-grained probability output (logprobs, multi-pass averaging, or a
> different verifier model) would be more informative than tuning the
> current threshold.

**Intended position**: Discussion, verifier-limits paragraph,
immediately after the T2 error-taxonomy paragraph (so the reader sees
why the failure modes are not filtered).

**Figure / table references**: Reliability diagram (`reliability-diagram.png`)
is the most publication-worthy single panel; ROC curve (`roc-curve.png`)
as a secondary or supplementary panel.

**Trace**:

- Obs anchors: `docs/notes/reflections/working-notes.md:§Obs 269`.
- Artefacts: `results/55maps-image-generalisation/verifier-calibration-crosstab/calibration.json`,
  `results/55maps-image-generalisation/verifier-calibration-crosstab/reliability-diagram.png`.
- Canonical number source: see §2.3.

## 6. Theme T4 — Subtype classification: strong aggregate, sharp asymmetric failure

### 6.1 Findings

On the 4-map gold-standard subset (569 expert-digitised features across
K-35-052-4, K-35-053-3 Elenovo, K-35-062-2 Rakovski, K-35-078-1 Lesovo),
the proposer-stage `consensus-4of5.geojson` (607 detections) achieves
**weighted-F1 = 0.887** [0.849, 0.922] conditional on a correct
detection, with Level-1 (mound-family vs settlement) accuracy = 1.000 on
matched pairs. Multi-class Matthews (MCC) = 0.744 [0.681, 0.807]; Cohen's
kappa (linear hierarchical) = 0.736 [0.664, 0.804]. Buffer sensitivity
is flat (weighted-F1 0.888 / 0.887 / 0.887 at 20 / 30 / 50 m) — subtype
errors are not an artefact of loose matching. Consensus threshold is
flat (weighted-F1 0.891 / 0.887 / 0.888 at 3/5, 4/5, 5/5) — vote-share is
a signal for **detection** correctness but **not** for subtype correctness.

However, the Level-2 error is dominated by a single asymmetric cell.
**Benchmark_mound → triangulation_mound at 27 / 47 matched benchmarks
(57 %)**; the reverse cell (triangulation_mound → benchmark_mound) is
**0 / 33**. Benchmark per-class recall collapses to 0.255; triangulation
per-class precision collapses to 0.542 because 27 of its 59 matched
predictions are actually benchmarks. This asymmetry was **not** predicted
by Obs 266's original taxonomy, which treated compound-boundary
over-assignment symmetrically.

A second sub-pattern: **settlement class fails via missed detection, not
misclassification**. Of 5 GT settlements, 2 are correctly classified (fid
6 on K-35-052-4 at 9.5 m; fid 26 on Elenovo at 3.5 m) and 3 are entirely
unmatched within 50 m (fids 1, 3, 4 on K-35-052-4). When matched,
settlement is classified correctly (2/2); the failure lives in the
`settlement → no_match` cell of the 5×5 matrix, not in the 4×4 matched-
pairs confusion cells.

### 6.2 Mechanism

Obs 271 identifies **symbol similarity + triangulation-as-default
attractor** as the most likely mechanism for the benchmark → triangulation
asymmetry. Both benchmark and triangulation marks are compound glyphs
superimposed on the burial-mound circle — a filled triangle for
triangulation, a cross / asterisk for benchmark. At the 384 px crop
resolution, the discriminative mark-shape sits close to the feature
resolution the VLM reliably attends to, and the model falls back on a
"mark on mound → triangulation" prior. The consensus-threshold flatness
(§6.1) confirms this is systematic: five independent passes agree
confidently on the wrong answer, ruling out vote-noise. Rakovski
contributes 15 / 27 (56 %) of the confusions, reflecting its dense
benchmark population (31 / 65 corpus benchmarks) rather than a single-map
artefact — the pattern is present on every map that carries benchmarks.

Settlement failure-via-missed-detection reflects a different mechanism:
the tell signature (hatching pattern inside an oval outline) differs
from the burial-mound ringed-circle signature, and the pipeline's
current prompt may not emphasise tell morphology strongly enough.
Obs 266 sub-pattern 3 proposes prompt-level remediation (more tell
positive examples at varied scales) but this is future work.

### 6.3 Evidence

- Full analysis report at `results/gold-standard-subtype-classification/report.md`
  (the nominated exemplar doc for structural quality, 17 sections).
- Confusion matrices: `confusion_matrix_4x4_buf50.csv` (raw /
  row-norm / col-norm) + `confusion_matrix_5x5_buf50.csv` (including
  no_match row/column).
- Per-class F1 + bootstrap CIs: `per_class_f1_buf50.csv`.
- Hierarchical decomposition: `hierarchical_decomposition.json`.
- Per-map diagnostic: `per_map_confusion.csv`, `per_map_summary.csv`.
- Settlement trace: `settlement_trace.csv` (per-feature fate for 5 GT
  settlements).

### 6.4 Caveats

- **Sparse settlement class (n = 5 GT)** — single-feature shifts of 20
  percentage points. We report raw cells and individual fates rather
  than smoothed or bootstrapped settlement F1. The 55-map human-review
  subset may deepen settlement evidence (the 1,028-candidate review
  found additional settlement-class candidates) but that analysis is
  out of scope for T4.
- **VLM confidence ≠ posterior probability in subtype**: the
  `confidence` field on subtype predictions is vote-share across the 5
  passes, not a per-class posterior. Brier scores and per-class PR
  curves are therefore not computed for subtype classification — see
  `results/gold-standard-subtype-classification/report.md` §12.4.
- **Level-1 accuracy = 1.000 on matched pairs** is not a claim that the
  pipeline never crosses the mound-family vs settlement boundary —
  it does, via missed detection (the 3 / 5 unmatched settlement fids).
  Accuracy only counts crossings within the matched-pair subset.
- **Subtype output should be reported as advisory** to the paper's
  practitioner audience — the subtype-specific F1 here is dominated by
  a single asymmetric cell and a sparse class, not a uniform
  classification quality story.

### 6.5 Suggested paper text

> On the 4-map gold-standard subset (569 expert-digitised features),
> the proposer-stage 4/5-consensus output achieves a subtype weighted-F1
> of 0.887 [0.849, 0.922] conditional on a correct detection, with
> perfect Level-1 accuracy (mound-family vs settlement) on matched pairs
> and multi-class MCC of 0.744 [0.681, 0.807]. The aggregate masks a
> single sharp asymmetric failure at the Level-2 (within-mound-family)
> axis: benchmark-on-burial-mound is labelled triangulation-on-burial-
> mound for 27 of 47 matched benchmarks (57 %), while the reverse
> confusion is empty (0 of 33). Benchmark per-class recall collapses to
> 0.255; triangulation per-class precision to 0.542. The asymmetry is
> systematic, not noise: five independent passes converge confidently on
> the wrong label and the consensus-threshold sweep (3/5 → 4/5 → 5/5)
> does not alter the pattern. We interpret this as symbol similarity at
> the 384 px crop resolution combined with a triangulation-as-default
> prior. Settlement-class failures are separately a missed-detection
> problem (3 of 5 GT settlements are entirely unmatched within 50 m)
> rather than a misclassification problem. Overall the VLM's subtype
> output should be read as advisory at the plain-vs-compound axis, and
> a dedicated prompt-engineering pass (visual negatives for plain
> surveying markers; side-by-side benchmark vs triangulation
> disambiguation) is indicated as future work.

**Intended position**: Discussion, subtype-accuracy paragraph (can stand
alone from T1–T3 or be grouped under "failure modes of the current
pipeline" with T2 and T3).

**Figure / table references**: Row-normalised 4×4 confusion heat map
(recall view) + column-normalised 4×4 (precision view) — both
perspectives needed, since the asymmetry is starker in the precision
view (triangulation precision collapse is less visible in recall alone).
Per-class F1 table from `per_class_f1_buf50.csv`.

**Trace**:

- Obs anchors: `docs/notes/reflections/working-notes.md:§Obs 266`,
  `§Obs 270`, `§Obs 271`.
- Artefacts: `results/gold-standard-subtype-classification/report.md`
  (exemplar-tier, 17 sections); `results/gold-standard-subtype-classification/macro_weighted_summary.json`;
  `results/gold-standard-subtype-classification/confusion_matrix_4x4_buf50.csv`;
  `results/gold-standard-subtype-classification/settlement_trace.csv`.
- Canonical number source: see §2.3 (weighted-F1 from
  `macro_weighted_summary.json`; 27/47 from
  `confusion_matrix_4x4_buf50.csv`).

## 7. Theme T5 — Attractor-pull spatial scale and Dawid-Skene aggregate inadequacy

### 7.1 Findings

The attractor-pull effect that drives T1's corrected-F1 lower bound is
statistically distinguishable from within-tile random placement only
out to **~125 m**. Shell-wise permutation testing (1 000 permutations,
seed 42) of the 1,029 reviewed VLM-only candidates against a student-GT
null (4,744 mounds) on the full 55-map corpus (31 818 km², 8 541 tiles),
with a 14 % bias correction for reviewer-promoted real mounds absent
from the null reference, gives:

| Shell (m) | Observed rate | Null (corrected) | Lift | Signal fraction | p |
|---|---:|---:|---:|---:|---:|
| (0, 50] | 46.1 % | 0.45 % | **102×** | 99 % | < 0.001 |
| (50, 75] | 11.8 % | 0.55 % | **21×** | 95 % | < 0.001 |
| (75, 100] | 4.6 % | 0.77 % | **5.9×** | 83 % | < 0.001 |
| (100, 125] | 1.9 % | 0.96 % | 1.9× | 48 % | 0.002 |
| (125, 150] | 1.1 % | 1.08 % | 0.99× | −1 % | **0.381** |
| (150, 286] | 7.2 % | 8.16 % | 0.88× | −13 % | **0.433** |

The attractor-pull effect ends cleanly at 125 m: the (125, 150] and
(150, 286] shells are **indistinguishable from within-tile random
placement**. The 11 mounds reviewers flagged in the (125, 150] shell and
the 74 mounds flagged at the "> 150 m" sentinel (effective tolerance
286 m) are essentially coincidental under this null — genuine mounds
that happen to be inside the review crop, not pulled to detection
attractors. A Ripley's cross-L(r) − r confirmation at r ∈ [10, 320] m
stays above the 95 % null envelope at every r, consistent with the
cumulative-lift view — but the honest scale-specific decomposition is
the shell analysis.

Second finding — **Dawid-Skene aggregate estimation is structurally
inadequate on this slice**. Two-annotator D-S with `fix_student_sens =
True` (the identifiability constraint the pipeline uses) collapses every
VLM-only candidate onto a **single** posterior value, regardless of
prior:

| Prior | Posterior (VLM-only) | ECE | Brier | AUC |
|---|---:|---:|---:|---:|
| 0.05 (preregistered v1) | 0.1862 | 0.539 | 0.490 | **0.500** |
| 0.17 (calibrated) | 0.7246 | 0.0001 | 0.200 | **0.500** |
| 0.7247 (empirical) | 1.000 | 0.275 | 0.275 | **0.500** |

AUC stays at 0.500 at **every** prior — prior-invariant. A data-driven
prior at the empirical rate (0.7247) snaps every posterior to 1.000
above a prior threshold of ~0.22; a grid search finds a "calibrated"
prior of 0.17 that yields a posterior matching the empirical rate, but
this is not a plug-in-the-truth recipe — it is a prior chosen to hit a
target. An 80 / 20 held-out sensitivity check (seed 42) confirms the
collapse is mechanical, not a circularity artefact. Structurally,
2-annotator D-S with the identifiability constraint **cannot rank items
on this slice**; three or more independent annotators would be required
to break the degeneracy.

### 7.2 Mechanism

The attractor-pull scale decay is consistent with the T2 failure-mode
mechanism: centroid-pull typically offsets real mounds by ≲ 50 m, with a
long tail to ~100–125 m for severe label-pull cases (Obs 264's "severe"
candidates like 04108). Beyond 125 m, reviewer-visible mounds inside the
400 m × 400 m context crop are not correlated with detection centroids
at rates above the within-tile null — the crop is large enough that
incidental mound presence is expected. The architectural pairing with
T3 is tight: the detections that are attractor-pulled in the 50–125 m
regime sit at saturated verifier confidence (T3's p = 1.00 bin), which
is why the verifier cannot filter them.

D-S aggregate inadequacy has a different mechanism: 2-annotator D-S
with `fix_student_sens = True` has a non-linear prior → posterior map
that passes through a degenerate collapse. Above prior ≈ 0.22 the
estimated prevalence snaps to 1.0 and every item's posterior snaps to
1.0; below that the posterior is identifiability-constrained to a
single value per response pattern. The VLM-only slice has only one
response pattern (student = 0, VLM = 1), so every item lands on the
same posterior. Human adjudication — which generates per-item labels
rather than aggregate rate estimates — is structurally the only
working per-item signal on this slice.

### 7.3 Evidence

- Attractor-pull: `results/55maps-image-generalisation/buffer-band-lift/`
  (`summary.json`, `cumulative.csv`, `shell.csv`, `ripley.csv`,
  `lift_curve.png`, `ripley_plot.png`).
- Dawid-Skene v1 (fixed 0.05 prior): `results/55maps-image-generalisation/ds-human-crosstab/`
  (`summary.json`, `report.md`, `reliability.csv`, `reliability_plot.png`,
  `buffer_scatter.png`).
- Dawid-Skene v2 (data-driven prior sweep + calibrated subvariant):
  `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/`
  (`report.md`, `summary.json`, `prior_sensitivity_sweep.csv`,
  `holdout.json`, `item-posteriors.csv`, `item-posteriors-calibrated.csv`,
  `ds-human-crosstab/`, `ds-human-crosstab-calibrated/`).
- Reviewer tally underlying the shell p-values: `human-review.csv`
  (472 mound@50 m) + `human-review-multi-buffer.csv` (274 additional
  mounds distributed across (50, 75] / (75, 100] / (100, 125] /
  (125, 150] / > 150 m shells).

### 7.4 Caveats

- **Null-reference scope**: the permutation null uses student GT only
  (4 744 mounds). The 746 reviewer-promoted real mounds are aliased to
  detection coordinates and cannot be used as null-space references
  without creating trivial self-matches. The 14 % bias-correction (×
  1/0.864) scales the null upward under the assumption that
  reviewer-promoted mounds share the tile-pool distribution of student
  GT. No significance conclusion changes between raw and corrected
  columns, but the assumption is noted in the paper's methods.
- **Hungarian one-to-one artefact**: 189 of the 1 029 "VLM-only FPs"
  (18.4 %) actually have student GT within 50 m — they are flagged as
  FPs because a closer detection claimed the GT first under the
  Hungarian matcher, not because no real mound is nearby. This is
  structural, not a bug, and does not affect the reviewer-label rates
  underlying the shell analysis.
- **D-S circularity (v2)**: the calibrated-prior 0.17 result is
  deliberately circular — the prior is fitted to the same labels used
  to evaluate the posterior. The 80 / 20 held-out control (ECE = 0.262
  on the test fold) confirms the collapse is mechanical rather than a
  circularity artefact, but this is a sensitivity check on the collapse
  mechanism, not on the calibrated prior's generalisability.
- **Generalisation of the D-S finding**: the AUC = 0.500 result is a
  structural consequence of 2-annotator D-S with the identifiability
  constraint on a single-response-pattern slice. It does not imply
  D-S is ineffective in general; it is ineffective on this slice with
  this configuration. **Prior-invariance empirically confirmed**
  (Session 76 level-up of
  `dawid-skene-v2-data-driven-prior/report.md`): across a grid of
  ~100 student-FN prior values in [0.01, 0.99]
  (see `dawid-skene-v2-data-driven-prior/prior_sensitivity_sweep.csv`)
  the VLM-only slice AUC remains 0.5000 for every value tested. The
  calibrated prior 0.17 recovers the aggregate rate (posterior 0.7246
  ≈ empirical 0.7247; ECE = 0.0001) but preserves the rank
  degeneracy. The 80 / 20 held-out sensitivity check (test-fold ECE
  = 0.262) confirms the aggregate-calibration result is not purely
  a circularity artefact, but it also confirms no prior choice
  restores per-item ranking on the 2-annotator structure.

### 7.5 Suggested paper text

> The attractor-pull effect that drives the human-reviewed corrected F1
> lower bound (§T1) is statistically distinguishable from within-tile
> random placement out to approximately 125 m. Shell-wise permutation
> testing of the 1,029 reviewed VLM-only candidates on the full 55-map
> corpus (31,818 km² / 8,541 tiles; 1,000 permutations, seed 42; bias
> correction for 14 % reviewer-promoted mounds absent from the
> student-GT null) gives lift ratios of 102× at (0, 50] m, 21× at (50,
> 75] m, 5.9× at (75, 100] m, 1.9× at (100, 125] m (p = 0.002), and
> 0.99× at (125, 150] m (p = 0.381). Mounds visible in the (125, 150]
> and (150, 286] shells are essentially coincidental under this null;
> the practitioner-useful tolerance cap is therefore 125 m, not 150 m or
> the 286 m corners-plus-5-pixel review tolerance. This defines the
> honest operating envelope for corrected-F1 quotation (§T1): F1 = 0.854
> at R = 125 m is the highest attractor-pull-tolerant number, with R =
> 150 m (F1 = 0.855) an upper bound that cannot be distinguished from
> chance.
>
> Dawid-Skene aggregate estimation of the same VLM-only rate is
> structurally inadequate: the 2-annotator D-S model with `fix_student_sens
> = True` identifiability constraint collapses every item onto a single
> posterior regardless of prior, and AUC = 0.500 is prior-invariant.
> A data-driven prior at the empirical rate snaps every posterior to
> 1.0; a grid-calibrated prior of 0.17 reproduces the cohort rate but
> still provides no item-level discrimination. Per-item human
> adjudication is therefore the only working per-item signal on this
> slice; the "D-S aggregate corrected F1 = 0.795" recorded in
> intermediate artefacts is an under-estimate artefact of the
> fixed-5 % prior and should not be cited alongside the human-reviewed
> corrected F1 of 0.830 as an independent corroboration.

**Intended position**: Discussion, closing paragraph of the failure-
modes section OR opening paragraph of a "methods limits" sub-section.

**Figure / table references**: Shell-wise lift table (directly
reproducible from `buffer-band-lift/shell.csv`); reliability diagram for
D-S posterior at the preregistered prior showing the single-value
degeneracy (`ds-human-crosstab/reliability_plot.png`).

**Trace**:

- Obs anchors: `docs/notes/reflections/working-notes.md:§Obs 272`,
  `§Obs 273`.
- Artefacts: `results/55maps-image-generalisation/buffer-band-lift/summary.json`,
  `results/55maps-image-generalisation/buffer-band-lift/shell.csv`,
  `results/55maps-image-generalisation/ds-human-crosstab/summary.json`,
  `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/dawid-skene-results-v2.json`.
- Canonical number source: see §2.3 (shell p-values from `shell.csv`;
  D-S AUC from `ds-human-crosstab/summary.json` and confirmed
  prior-invariant in `dawid-skene-v2-data-driven-prior/summary.json`).

## 8. Cross-theme integration — how T1–T5 interact

Read across the five themes, the paper's Discussion has a coherent
single story. Detection-stage performance on out-of-sample maps is
strong under per-item human adjudication (T1: F1 ≥ 0.830 at 50 m, rising
to 0.854 at the practitioner-useful 125 m cap). The gap to the measured
F1 of 0.771 is not reviewer noise — it is a structural under-count by
the student GT, quantified by the 472 reviewer-promoted true positives.
At the same time, the pipeline produces 556 confirmed false positives
that fall into three mechanistically distinct failure families (T2:
centroid-pull, contour-ring confounds, subtype-boundary failures), and
the verifier cannot filter them (T3: ECE 0.269, AUC 0.655, quantised
output saturated at the confidence level where the failures live). The
subtype-classification analysis on a separate 4-map gold-standard set
(T4) delivers strong aggregate performance (weighted-F1 0.887) but
reveals a sharp Level-2 asymmetry (benchmark → triangulation at 57 %)
that prompt-engineering disambiguation might address in future work.
Finally, the spatial envelope within which the detection signal operates
is bounded: attractor-pull is statistically distinguishable from
random placement only to ~125 m (T5), and Dawid-Skene aggregate
estimation is structurally unable to rank items on this slice at any
prior — human adjudication is the only working per-item signal.

Two cross-theme dependencies deserve explicit framing in the paper:

1. **T1 ↔ T3**: the corrected-F1 lower bound and the verifier-
   miscalibration finding are complementary. T1's 0.830 lower bound
   assumes the verifier's probability output is not load-bearing for
   precision; T3 documents why that assumption is correct. Together,
   they show that the pipeline's useful operating regime is
   "propose-and-adjudicate" rather than "propose-verify-and-trust" —
   the adjudication layer (human review) is doing the work the
   verifier's probability cannot.
2. **T2 ↔ T5**: the three failure families of T2 have different
   characteristic spatial scales (centroid-pull typically ≲ 50 m;
   contour-ring confounds typically at-centroid; subtype-boundary
   failures are pure classification with no spatial component). T5's
   125 m attractor-pull scale is therefore an **upper** bound on the
   centroid-pull extent, not a characterisation of all failure modes;
   the contour-ring and subtype-boundary failures contribute FPs
   regardless of spatial tolerance.

A single **scope boundary** spans every theme: all five are drawn from
the 55-map image-generalisation VLM-only slice + 4-map gold-standard
subset. The paper-headline F1 = 0.904 @ 50 m lives on the 487-tile
matrix (text-HIGH + PV at K = 30 consensus; `paper-tables/metrics_master.json`)
and is a **different** evaluation regime from the 55-map slice analysed
here. The paper should cite 0.904 as the headline detection result and
0.830 as the human-reviewed out-of-sample lower bound for the image
modality, flagging the modality and scope differences explicitly.

## 9. Methods notes

### 9.1 Provenance of the Obs 262–273 numbers

Every headline number in §§3–7 traces to a JSON / CSV / Markdown
artefact under `results/` produced by a versioned script with an explicit
seed. The provenance chain is:

- **Raw detections and consensus** → `outputs/55maps-image-generalisation/verified/`
  (55-map slice) and `outputs/h11/gold-standard-v2/consensus/` (4-map
  slice).
- **Matching and measured F1/P/R** → `outputs/55maps-image-generalisation/evaluation/evaluation.json`
  (Hungarian one-to-one at 20 / 30 / 40 / 50 m, 1 000 bootstrap
  iterations, seed 42); `results/gold-standard-subtype-classification/`
  (10 000 bootstrap iterations, seed 42, matched-pair stratified by map).
- **Human-review labels** → `results/55maps-image-generalisation/human-review.csv`
  (50 m, 1,028 rows) + `.../human-review-multi-buffer.csv` (wider-buffer
  re-review, 557 rows).
- **Corrected F1** → `scripts/compute_corrected_f1_human_reviewed.py`
  (50 m, analytic) and `scripts/compute_corrected_f1_multi_buffer.py`
  (multi-buffer, extended-GT Hungarian rerun); both seed 42, 10 000
  bootstrap iterations on reviewer-label variability.
- **Verifier calibration** → `scripts/crosstab_verifier_vs_human.py` on
  the same 1,028 labels; seed 42, 10 000 bootstrap iterations.
- **Attractor-pull lift** → `scripts/analyse_buffer_band_lift.py`
  (within-tile permutation null, 1 000 permutations, seed 42;
  bias-corrected for reviewer-promoted mounds absent from the student-GT
  null).
- **Dawid-Skene** → `scripts/analyse_ds_vs_human_review.py` (v1 fixed
  prior 0.05) + `scripts/analyse_dawid_skene_v2.py` (v2 prior sweep +
  held-out control, seed 42).
- **Subtype classification** → `scripts/analyse_subtype_classification.py`
  v1.0.0 at git commit `508f7698`; seed 42, 10 000 bootstrap iterations,
  matched-pair-level resampling stratified by map.

### 9.2 Bootstrap protocol

Every CI reported here uses percentile 2.5 / 97.5 bootstrap with seed 42.
Resampling unit varies by analysis: tile-level for measured F1 and the
attractor-pull permutation null; matched-pair-level (stratified by map)
for the subtype-classification CIs; reviewer-label-level for the
corrected-F1 CIs; verifier-label-pair-level for the verifier-calibration
CIs. This is documented per-analysis in the canonical sidecars and in
`results/ci-metadata-registry.md`, which enumerates the 48 bootstrap CI
sidecar files across the project.

### 9.3 Out-of-scope for this document

This synthesis deliberately scopes to the 1,028-candidate VLM-only slice
and the 4-map gold-standard set. The following adjacent analyses are
NOT synthesised here and belong in dedicated paper sections:

- Era 1 hypothesis closures (h8-v2 library composition, h10 calibration
  pool, h11 two-stage, h12-v2 HP:HN ratio, and the preregistered Phase
  2b H7 temperature sweep). These feed the paper's Results section, not
  the Discussion spine.
- The 55-map cross-track comparison (image vs text-HIGH vs text-MIN);
  paired-permutation tests exist at each track's `paired-vs-*`
  subdirectory; a cross-track consolidation doc is a Step 4 task per
  `planning/interim-docs-review.md`.
- The 487-tile paper-headline matrix (text-HIGH + PV at K = 30
  consensus, F1 = 0.904) — a different evaluation regime (§8).
- Phase 2b tile-level MCC temperature sweep (Obs 274, added 2026-04-23
  after the 262–273 window). That finding enters the paper as a
  complementary tile-level metric alongside the object-level F1
  headline; it does not substitute for any claim in T1–T5.

## 10. Reproducibility

- **Date of the numbers used here**: 2026-04-20 (the calibrated
  human-review day; Obs 262–269) and 2026-04-21 (wider-buffer re-review
  + attractor-pull + D-S + subtype analysis; Obs 270–273).
- **Files used**: every path cited above. The `results/` subdirectories
  listed in §§3–7 `Evidence` blocks constitute the complete provenance
  tree; §2.3 gives the canonical-numbers mapping.
- **Working-notes anchors**: `docs/notes/reflections/working-notes.md`
  §§ Obs 262–273 (lines 11780–12908 at the time of writing).
- **Re-run command**: **none required.** This document is a pure
  synthesis of existing artefacts; no computation re-runs were performed
  in producing it. If any underlying analysis is re-run (e.g. after a
  calibration-constant change or a re-review pass), every number in §2.3
  should be re-pulled from the regenerated source.
- **Cross-reference to protocol errata**: E47 is mentioned twice in this
  project — `docs/methodology/preregistration/protocol-errata.md:1233`
  (primary spatial matching buffer reverted to preregistered 20 m) and
  `docs/notes/reflections/working-notes.md:6553` (proposer prompt
  substitution). Whenever this document references E47, the intended
  entry is stated explicitly. Neither E47 entry is materially cited in
  the present themes; the buffer-revert (errata line 1233) is the
  framing context for the "why 50 m instead of 20 m" sentence in T1,
  but not a numeric source.

## 11. Caveats and risk register

The five-theme synthesis inherits all caveats of its underlying Obs; the
following are the most load-bearing for paper-text quotation:

1. **Corrected F1 is a lower bound** (T1 §3.4; Obs 263, 267, 268).
   Quote as "F1 ≥ 0.830 at 50 m" and not "F1 = 0.830 at 50 m".
2. **Multi-buffer corrected F1 at 150 m is an upper bound**, not a
   practitioner-useful number (T5 §7.1; Obs 272). Quote the
   practitioner-useful cap as F1 = 0.854 at R = 125 m.
3. **Reviewer noise floor** (T1 §3.4; Obs 263): approximately 10–15 %
   of per-item decisions in the ambiguous band carry reviewer-level
   noise. Framing should be "reviewer-consistent estimate with a
   conservative bias", not "ground truth".
4. **Verifier probability cannot filter T2 failures** (T3; Obs 269).
   Any text that claims the verifier provides precision control should
   be removed from the paper — T3's architectural framing is load-bearing.
5. **D-S aggregate is not a useful item-level signal** on this slice
   (T5 §7.1; Obs 273). The intermediate artefact's "D-S corrected F1 =
   0.795" is an under-estimate artefact of the fixed 5 % prior and
   should be reported only as methodological context for the structural
   inadequacy finding, not alongside the human-reviewed 0.830 as an
   independent estimate.
6. **Subtype output is advisory** (T4 §6.4; Obs 266, 270, 271). The
   0.887 weighted-F1 headline requires the 27 / 47 benchmark →
   triangulation cell and the triangulation-precision-0.542 collapse to
   be quoted alongside it.
7. **v2 verifier quarantine**: no figure or number in this document
   traces to the quarantined v2 verifier tree. The 55-map image-
   generalisation headline uses verifier v1, confirmed by the
   quarantine policy at `docs/methodology/v2-verifier-contamination-policy.md`.
8. **Untested under MINIMAL thinking + Pro**: the 55-map image run used
   gemini-3-flash HIGH thinking; the Pro + MINIMAL cell is not in the
   production envelope and should not be inferred from any number here.
9. **Student-GT positional noise** (Obs 260; ~25 m): affects the
   Hungarian matching's FN counts at tight buffers more than at 50 m.
   The corrected F1 at 50 m is relatively insensitive to this noise;
   buffer-elasticity claims need to cite Obs 260 explicitly.
10. **E47 disambiguation**: every mention of E47 in the manuscript must
    identify which entry — `protocol-errata.md:1233` (buffer revert) or
    `working-notes.md:6553` (proposer prompt substitution). This
    document does so (§10).

## 12. Paper implications — per-theme summary

- **T1 headline sentence**: "Per-item human adjudication yields
  corrected F1 ≥ 0.830 at 50 m on the 55-map out-of-sample set (95 %
  review-label bootstrap CI [0.826, 0.833]); the practitioner-useful
  attractor-pull-tolerant cap is F1 = 0.854 at R = 125 m." Discussion,
  first numeric paragraph.
- **T2 headline sentence**: "Three mechanistically distinct failure
  families dominate the confirmed false positives: centroid-pull,
  contour-ring confounds, and subtype-boundary failures — all at
  high verifier confidence, all addressable by architecture- rather
  than prompt-level remediation." Discussion, error-taxonomy paragraph,
  cites the 70-figure atlas by directory.
- **T3 headline sentence**: "The pipeline verifier is poorly calibrated
  on this corpus (ECE = 0.269; AUC = 0.655; 13 distinct probability
  values) and cannot filter the T2 failure modes." Discussion,
  verifier-limits paragraph.
- **T4 headline sentence**: "Subtype classification on the 4-map gold
  standard yields weighted-F1 = 0.887, but the Level-2 error is
  dominated by a single asymmetric benchmark → triangulation cell
  (27 / 47; the reverse cell is empty); the subtype output is
  advisory." Discussion, subtype paragraph.
- **T5 headline sentence**: "The attractor-pull effect ends at ~125 m
  (shell-wise permutation test; p = 0.381 at (125, 150] m), defining
  the practitioner-useful tolerance envelope; Dawid-Skene aggregate
  estimation is structurally inadequate on this slice at any prior
  (AUC = 0.500), so human adjudication is the only working per-item
  signal." Discussion, methods-limits paragraph OR closing paragraph
  of the failure-modes section.

**Figures and tables to cite** (cross-reference to `paper-tables/` where
consolidated):

- Multi-buffer corrected F1 curve table: `corrected-f1-multi-buffer/summary.json`.
- Attractor-pull shell table: `buffer-band-lift/shell.csv`.
- Verifier reliability diagram: `verifier-calibration-crosstab/reliability-diagram.png`.
- Subtype 4×4 confusion (row-norm + col-norm heat maps):
  `gold-standard-subtype-classification/confusion_matrix_4x4_buf50.csv`.
- Per-class F1 + CI table: `gold-standard-subtype-classification/per_class_f1_buf50.csv`.
- Error-taxonomy figure panel: 5 representative images from
  `docs/paper/figures/review-app-examples/`.
- Settlement-class trace (qualitative): `gold-standard-subtype-classification/settlement_trace.csv`.

**Future-work pointers** (capped at three for Discussion § future work):

1. Decoupled detection-vs-localisation architecture to eliminate
   centroid-pull (T2 Family 1).
2. Benchmark-vs-triangulation prompt disambiguation (T4 §6.5) + higher
   crop resolution test (384 px → native).
3. Continuous-confidence or spatial-pinpoint human-review UI (T1 §3.4;
   Obs 263) to quantify the 10–15 % ambiguous-band noise explicitly.

## 13. Files referenced (manifest, absolute paths)

### 13.1 Primary inputs (raw / measured)

- `/home/shawn/Code/map-reader-llm/outputs/55maps-image-generalisation/evaluation/evaluation.json`
- `/home/shawn/Code/map-reader-llm/outputs/55maps-image-generalisation/verified/verified_detections.geojson`
- `/home/shawn/Code/map-reader-llm/outputs/h11/gold-standard-v2/consensus/consensus-4of5.geojson`
- `/home/shawn/Code/map-reader-llm/inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
- `/home/shawn/Code/map-reader-llm/inputs/vectors/references/reference_*.geojson` (four files, 4-map gold-standard)
- `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
- `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/full_evaluation_bounds.geojson`
- `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/h10_test_bounds.geojson`

### 13.2 Human-review CSVs

- `/home/shawn/Code/map-reader-llm/results/55maps-image-generalisation/human-review.csv`
- `/home/shawn/Code/map-reader-llm/results/55maps-image-generalisation/human-review-multi-buffer.csv`

### 13.3 Rendered per-analysis reports

- `/home/shawn/Code/map-reader-llm/results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.md` (+ `.json`)
- `/home/shawn/Code/map-reader-llm/results/55maps-image-generalisation/corrected-f1-multi-buffer/report.md` (+ `summary.json`)
- `/home/shawn/Code/map-reader-llm/results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.md` (+ `crosstab.json`)
- `/home/shawn/Code/map-reader-llm/results/55maps-image-generalisation/verifier-calibration-crosstab/calibration.md` (+ `calibration.json`, `reliability-diagram.png`, `roc-curve.png`, `pr-curve.png`)
- `/home/shawn/Code/map-reader-llm/results/55maps-image-generalisation/buffer-band-lift/report.md` (+ `summary.json`, `shell.csv`, `cumulative.csv`, `ripley.csv`, `lift_curve.png`, `ripley_plot.png`)
- `/home/shawn/Code/map-reader-llm/results/55maps-image-generalisation/ds-human-crosstab/report.md` (+ `summary.json`, `reliability.csv`, `reliability_plot.png`, `buffer_scatter.png`)
- `/home/shawn/Code/map-reader-llm/results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/report.md` (+ `summary.json`, `dawid-skene-results-v2.json`, `prior_sensitivity_sweep.csv`, `holdout.json`)
- `/home/shawn/Code/map-reader-llm/results/55maps-image-generalisation/buffer-100m-diagnostics/summary.json` (+ `gt_clustering.csv`, `pair_drift.csv` — stub; report pending per Step 4)
- `/home/shawn/Code/map-reader-llm/results/gold-standard-subtype-classification/report.md` (the exemplar, 17 sections) (+ `macro_weighted_summary.json`, `kappa_mcc.json`, `hierarchical_decomposition.json`, `confusion_matrix_4x4_buf50.csv`, `confusion_matrix_5x5_buf50.csv`, `per_class_f1_buf50.csv`, `buffer_sensitivity.csv`, `consensus_threshold_sweep.csv`, `per_map_confusion.csv`, `per_map_summary.csv`, `settlement_trace.csv`, `run_manifest.json`)

### 13.4 Working-notes observation anchors

- `/home/shawn/Code/map-reader-llm/docs/notes/reflections/working-notes.md`
  §§ Obs 262 (line 11780), 263 (11877), 264 (12033), 265 (12242),
  266 (12291), 267 (12394), 268 (12490), 269 (12550), 270 (12649),
  271 (12711), 272 (12770), 273 (12840).

### 13.5 Cross-referenced policy + errata documents

- `/home/shawn/Code/map-reader-llm/docs/methodology/preregistration/protocol-errata.md`
  (E47 line 1233 — primary spatial matching buffer revert)
- `/home/shawn/Code/map-reader-llm/docs/methodology/v2-verifier-contamination-policy.md`
  (v2 quarantine; none of this document cites quarantined v2 artefacts)

### 13.6 Paper-tables consolidation references

- `/home/shawn/Code/map-reader-llm/results/paper-tables/metrics_master.json`
  (487-tile headline matrix, cross-referenced for F1 = 0.904 scope
  boundary — see §8)
- `/home/shawn/Code/map-reader-llm/results/ci-metadata-registry.md`
  (48 CI sidecar entries; bootstrap-protocol provenance)

### 13.7 Figure atlas

- `/home/shawn/Code/map-reader-llm/docs/paper/figures/review-app-examples/*.png`
  (approximately 70 exemplar figures for T2's centroid-pull, contour-
  ring confound, and subtype-boundary failure families)

---

**End of synthesis.** Proceed to paper outline (Step 6 of
`planning/paper-writeup-continuity.md`) only after Step 4 gap-fills and
Step 5 SUPERSEDED marking are complete, per the scorecard at
`planning/interim-docs-review.md` §6 Step 4 sequencing.
