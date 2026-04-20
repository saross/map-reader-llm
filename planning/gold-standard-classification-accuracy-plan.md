# Subtype-classification accuracy on the 4-map gold-standard: analysis plan

**Date**: 2026-04-20
**Author**: Claude (planning agent), reviewed by Shawn
**Status**: READY TO EXECUTE — decisions resolved 2026-04-20; see
`gold-standard-classification-metrics-decisions.md` for the decision record.
**Related**: Obs 266 in `docs/notes/reflections/working-notes.md`;
corrected detection F1 at `results/55maps-image-generalisation/human-reviewed-corrected/`

## 1. Preamble: data availability

### 1.1 What we found (Step 1)

The 4-map Era 2 calibration subset has **per-feature subtype labels on both
sides of the comparison**. No pivot to the 55-map human-review CSV is needed.

**Ground truth**: `inputs/vectors/references/reference_{MAP}.geojson`, four
files, one per calibration map. Each feature carries a `Symbol` property with
values drawn from:

- `Burial mound`
- `Bench mark on burial mound`
- `Triangulation point on burial mound`
- `Settlement mound`

(One stray `Burial Mound` with a capitalised `M` appears in Rakovski and must
be case-normalised during load.)

**VLM output**: `outputs/h11/gold-standard-v2/consensus/consensus-4of5.geojson`.
Each feature carries a `subtype` property with values drawn from:

- `burial_mound`
- `benchmark_mound`
- `triangulation_mound`
- `settlement_mound`

The vocabulary mapping is deterministic:

| GT Symbol                              | VLM subtype          |
|----------------------------------------|----------------------|
| Burial mound                           | burial_mound         |
| Bench mark on burial mound             | benchmark_mound      |
| Triangulation point on burial mound    | triangulation_mound  |
| Settlement mound                       | settlement_mound     |

### 1.2 Per-class support on the 4-map subset

**Ground truth (all 4 maps combined):**

| Class                | Count |
|----------------------|------:|
| Burial mound         | 455   |
| Bench mark           |  65   |
| Triangulation point  |  43   |
| Settlement mound     |   5   |
| **Total GT**         | **569** |

(Rakovski contributes the 1× `Burial Mound` case-variant; rolled into
`Burial mound`.)

**VLM consensus-4of5 output:**

| Subtype              | Count |
|----------------------|------:|
| burial_mound         | 462   |
| benchmark_mound      |  67   |
| triangulation_mound  |  74   |
| settlement_mound     |   4   |
| **Total detections** | **607** |

**Per-map GT breakdown:**

| Map                    | Burial | Benchmark | Trig | Settlement | Total |
|------------------------|-------:|----------:|-----:|-----------:|------:|
| K-35-052-4 (Elhovo NW) |  103   |  13       |  16  |  4         | 136   |
| K-35-053-3 Elenovo     |  187   |  18       |  11  |  1         | 217   |
| K-35-062-2 Rakovski    |  150   |  31       |  15  |  0         | 196   |
| K-35-078-1 Lesovo      |   16   |   3       |   1  |  0         |  20   |

Headline sparsity points:

- **settlement_mound n=5 total, scattered across 2 of 4 maps.** Bootstrap
  CIs will be very wide; the raw confusion cell is the right thing to report.
- **Lesovo has n=20 total**, so per-map stratification will show Lesovo
  with very noisy per-class ratios — but the confusion-cell counts are
  still informative if reported raw.

### 1.3 Obs 266 → predicted confusion-matrix signatures

From the working-notes Obs 266 failure taxonomy, we should expect the
confusion matrix to show these off-diagonal cells populated:

- **GT=Settlement → Predicted=Burial** (Obs 266 sub-pattern 3,
  "settlement-class under-assignment")
- **Predicted=Triangulation or Benchmark where GT has no match** (Obs 266
  sub-pattern 1, "compound-boundary over-assignment") — this falls into
  the "unmatched detection" bucket.
- **Predicted=Settlement where GT has no match or is building-like**
  (Obs 266 sub-pattern 2, "built-environment → settlement_mound"). Also
  predominantly in the "unmatched detection" bucket.

The VLM produces **only 4 predicted settlements** vs **5 GT settlements**,
so sub-pattern 3 (under-assignment) is expected to dominate on this subset.
Sub-patterns 1 and 2 will manifest in the unmatched-detection row if the
analysis uses a 5×5 confusion matrix.

The fact that VLM consensus produces **74 triangulation_mounds vs 43 GT
triangulations** (+31, +72%) is strong prima facie evidence that
sub-pattern 1 is present on this subset.

## 2. Objectives and scope

**Primary question**: conditional on a correctly-detected mound, how often
does the VLM assign the correct subtype?

**Secondary question**: what are the specific off-diagonal confusion cells
that drive subtype error, and how do they map to the Obs 266 taxonomy?

**Out of scope**: pixel-level or cartographic-symbol-level classification;
joint detection-and-classification training; per-prompt sensitivity.

## 3. Recommended metric set

### 3.1 Shortlist (report these — updated per decision record 2026-04-20)

1. **4×4 confusion matrix (matched pairs only)** — one row per GT class,
   one column per predicted class, counts in cells. The single most
   informative artefact for an Obs 266 discussion. Report as **both
   row-normalised (P(predicted | GT), recall perspective) and
   column-normalised (P(GT | predicted), precision perspective)** heat
   maps per **D4**.

2. **5×5 confusion matrix (adds `no_match` row and column)** — captures
   the spurious-detection and missed-detection streams. Row `no_match` =
   "GT had no match" = a detection that got FP at the buffer tolerance.
   Column `no_match` = "prediction had no match" = a FN.

3. **Per-class precision / recall / F1 with 95% bootstrap CIs**, accompanied
   by **per-class support counts**. Bootstrap **at the matched-pair level,
   stratified by map, over 10,000 iterations, seed 42** (per D6 and D7).
   For the sparse settlement_mound (n=5), report raw numerator/denominator
   not ratios (per §5).

4. **Weighted-F1 (HEADLINE)** and **Macro-F1 (companion)** per D9. Plan
   to lead the paper text with weighted-F1 because macro-F1 is dominated
   by settlement's n=5 noise. Both reported; micro-F1 omitted (redundant
   with overall accuracy for single-label multiclass).

5. **Linearly-weighted Cohen's kappa** on the 4×4 matched-pairs table
   (per D8), using the hierarchical weighting from D1: Level-1 errors
   (mound-family ↔ settlement) get weight 1.0; Level-2 errors (within
   mound-family, plain ↔ +benchmark ↔ +trig) get weight 0.5. Also
   report **unweighted Cohen's kappa** for comparability with the broader
   ML literature.

6. **Multi-class MCC** on the 4×4 matched-pairs table — a more
   imbalance-robust summary than macro-F1. Use sklearn's
   `matthews_corrcoef` multi-class formulation.

7. **Hierarchical decomposition** (per D1, extended):
   - **Detection layer**: `P(match | ref)` = detection recall;
     `P(match | det)` = detection precision. Already reported in paper.
   - **Level-1 classification** (on matched pairs): mound-family
     (burial / benchmark / trig, all compound burial-type) vs settlement.
     2×2 confusion table with precision/recall/F1 per class.
   - **Level-2 classification** (on matched pairs classified as
     mound-family at Level 1): plain burial / + benchmark / + trig.
     3×3 confusion table with precision/recall/F1 per class.
   - **Global**: `P(correct_subtype | matched)` = flat 4-class accuracy.
   - Report Level 1 and Level 2 separately — they correspond directly to
     Obs 266's sub-pattern 3 (Level-1 error: settlement misassignment)
     and sub-patterns 1–2 (Level-2 errors: compound-boundary and
     built-environment confusion). The hierarchical framing is the
     primary narrative for the Obs 266 discussion.

8. **Per-class-pair confusion rates** — the specific "A → B" conditional
   rates that are directly paper-quotable:
   - `P(predicted=B | GT=A, matched)` for A ≠ B.
   - Reported as counts not just ratios, because some cells are tiny.

9. **Consensus-threshold sweep** (per D3). Re-generate consensus GeoJSONs
   at 3/5 and 5/5 thresholds (alongside the default 4/5), and compute
   the full metric set at each threshold. Produces a small table:

   | Threshold | N detections | Weighted F1 | Level-1 acc | Level-2 acc |
   |-----------|-------------:|------------:|------------:|------------:|
   | 3/5       |        ?     |      ?      |      ?      |      ?      |
   | 4/5       |        ?     |      ?      |      ?      |      ?      |
   | 5/5       |        ?     |      ?      |      ?      |      ?      |

   Tests the hypothesis that higher consensus buys higher subtype
   accuracy (analogous to the verifier-calibration analysis in Obs 269).

### 3.2 Considered but deprioritised

| Metric              | Why deprioritised |
|---------------------|-------------------|
| Top-k accuracy      | VLM outputs a single label per detection, not a ranked list. |
| Brier score         | VLM consensus output carries `confidence` = vote share (5-pass), not per-class posterior probabilities. Calibration analysis is moot. |
| PR-curves per class | Requires rankable confidences per predicted class; not available. Deferrable to the parallel verifier-calibration work. |
| Balanced accuracy   | Captured by macro-F1 and multi-class MCC; marginal additional information. |
| Overall accuracy    | Redundant with micro-F1; misleading under imbalance. |
| F2 / F0.5 F-beta variants | Flagged briefly in the paper's discussion for the settlement sparse-class framing (D2), but not in the headline tables. |
| Custom archaeological cost-weighted kappa | Explicitly deferred (D5). Adds argument surface (cost-matrix choices can be contested) without changing the substantive findings. |

### 3.3 Why confusion matrix is the headline, not F1

Per-class F1 collapses the two directions of error (P errors and R errors)
into a single number. For Obs 266, the directionality is exactly what
matters: "settlement → burial" (under-assignment) is a different failure
mode from "non-mound → settlement" (over-assignment). Only the confusion
matrix exposes these separately. The paper should lead with the matrix,
use per-class F1 as a summary, and quote specific cells for the Obs 266
discussion.

## 4. Matching / pairing protocol

### 4.1 Matching algorithm

Reuse `scripts/lib_advanced_metrics.py::match_detections_to_references`
(Hungarian algorithm, one-to-one matching, buffer distance in metres).
This is the same function used for detection F1; consistency matters.

### 4.2 Buffer sweep

Run at **three buffer distances**: 20 m, 30 m, 50 m.

- **50 m**: consistency with the headline detection F1 the paper reports.
- **30 m**: intermediate; typical GT-spacing residual noise is ~10–15 m.
- **20 m**: tighter pairing; subtype accuracy is conditional on positional
  match, so a tighter buffer reduces false matches (a burial_mound
  prediction matched to a benchmark GT 40 m away is not really the same
  object).

Headline table uses 50 m for continuity with the paper. Sensitivity
table uses all three.

### 4.3 Handling unmatched detections

**Primary analysis**: matched-pairs-only 4×4 confusion matrix.

**Supplementary analysis**: 5×5 confusion matrix with an "unmatched"
pseudo-class for both dimensions.

- Unmatched detection → treated as `predicted = X, GT = no_match`.
- Unmatched GT → treated as `predicted = no_match, GT = Y`.

This second form is what directly exposes Obs 266's "compound-boundary
over-assignment" (most triangulation/benchmark FPs will appear as
`predicted = triangulation_mound, GT = no_match`).

Per-class F1 reported from the 4×4 matched-pairs table is the honest
"conditional on correct detection" number. Per-class F1 from the 5×5
table is dominated by detection errors and would be misleading to lead
with.

### 4.4 Vocabulary normalisation

Load-time transformations:

- `Burial Mound` → `Burial mound` (case).
- Map all four GT `Symbol` values to the VLM's snake_case vocabulary
  per §1.1 table.
- Store the mapping in a small dict at the top of the analysis script
  so reviewers can audit it.

### 4.5 Per-map stratification

Run the analysis both pooled (all 4 maps) and stratified by map.
Per-map tables will have tiny supports (Lesovo n=20), so report raw
cells only — no bootstrap CIs per-map. The pooled 4-map analysis is
the primary; per-map is diagnostic only.

## 5. Sparse-class handling policy

**Settlement_mound** has n=5 GT on the 4-map subset. Explicit policy:

1. Always show the raw confusion-matrix cells for settlement. A single
   misclassification moves the ratio by 20 percentage points; do not
   smooth or suppress.
2. Do **not** bootstrap F1 for settlement_mound on the 4-map set. The
   CI width would be wider than the [0,1] interval allows. Report
   precision and recall as fractions with explicit numerator/denominator
   (e.g., "recall: 2/5 = 0.4"), not as bootstrap CIs.
3. Flag the support count visibly in every table row ("n=5").
4. In the Obs 266 discussion, quote the specific GT rows. With n=5 we
   can individually inspect each settlement_mound's fate in the VLM
   output and describe it qualitatively.
5. **Triangulation_mound** (n=43 GT) and **Benchmark_mound** (n=65 GT)
   are borderline; bootstrap CIs on these will be wide (expect ±0.1–0.15
   on F1) but not uninterpretable. Report with bootstrap CIs and
   transparent support.
6. **Burial_mound** (n=455 GT) is well-supported; CIs will be narrow.

## 6. Decision points — RESOLVED 2026-04-20

All original decision points resolved. See
`planning/gold-standard-classification-metrics-decisions.md` for the
full decision record with rationale.

| # | Original decision | Resolution |
|---|---|---|
| 1 | 5×5 vs 4×4 as primary | 4×4 headline + 5×5 supplementary (accepted default) |
| 2 | Buffer choice | 50 m headline + 20/30/50 m sensitivity table (accepted default) |
| 3 | Per-map stratification depth | Pooled headline + per-map 4×4 cell tables as supplementary (accepted default) |
| 4 | Additional data source | Gold-standard-only for this paper (accepted default) |
| 5 | 55-map human-review CSV corroboration | Included as short sensitivity-analysis appendix (accepted default) |
| 6 | Capitalisation normalisation | Fold `Burial Mound` → `Burial mound` (accepted default) |
| 7 | Bootstrap iteration count | 10,000 throughout (per decision-record D7; was 1,000 / 10,000 split in original draft) |

Further decisions from the `/review-implementation` capability scan
(2026-04-20) are also resolved and captured in the decision record:

| # | Review decision | Resolution |
|---|---|---|
| D1 | Hierarchical 2-level analysis alongside 4-class | YES (alongside) |
| D2 | F-beta variants | F1 headline only; F2 framing in discussion for settlement |
| D3 | Consensus-threshold sweep (3/5, 4/5, 5/5) | YES |
| D4 | Both row- and column-normalised heat maps | YES |
| D5 | Cost-weighted archaeological kappa | NO (deferred) |
| D6 | Classification bootstrap resample unit | Matched-pair-level, map-stratified |
| D7 | Bootstrap iteration count | 10,000 throughout |
| D8 | Kappa variant | Linearly-weighted (primary) + unweighted (companion) |
| D9 | Lead summary metric | Weighted-F1 (macro-F1 as companion) |

## 7. Implementation notes

### 7.1 Scripts to write

Single new script: `scripts/analyse_subtype_classification.py`.

Inputs (CLI args):

- `--gt-dir inputs/vectors/references/`
  (loads all `reference_*.geojson`, ignores `mounds-reference.geojson`
  master and `student-mounds-*` student files)
- `--detections outputs/h11/gold-standard-v2/consensus/consensus-4of5.geojson`
- `--bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson`
- `--buffers 20 30 50`
- `--output-dir results/gold-standard-subtype-classification/`
- `--bootstrap-n 10000`
- `--seed 42`

Outputs:

- `confusion_matrix_4x4_buf50.csv`
- `confusion_matrix_5x5_buf50.csv`
- `per_class_f1_buf50.csv` (with bootstrap CIs)
- `macro_weighted_summary.json`
- `kappa_mcc.json`
- `hierarchical_decomposition.json`
- `buffer_sensitivity.csv`
- `per_map_confusion.csv`
- `analysis.log`

A matching report: `results/gold-standard-subtype-classification/report.md`,
templated to include all tables and an Obs-266-aligned narrative.

### 7.2 Implementation details

- Reuse `match_detections_to_references` from `lib_advanced_metrics.py`.
- Add a thin wrapper `build_pair_list(gdf_det, gdf_ref, bounds, buffer_m)`
  that returns a dataframe with columns `(map, det_subtype, gt_symbol,
  distance_m)` — one row per matched pair, plus `_match_type` =
  `{matched, unmatched_det, unmatched_ref}`.
- Build confusion matrices from the pair-list via pandas pivot.
- Bootstrap over tiles (same resampling unit as existing F1 bootstrap)
  for the confusion-matrix cells and per-class F1.

### 7.3 Compute placement

- Sapphire for the bootstrap-heavy phase (≥10k iterations × 3 buffers,
  pooled + 4 per-map) — ~30 minutes wall-clock.
- Local for the deterministic confusion-matrix build (seconds).
- No API calls needed.

### 7.4 Reproducibility

- Pin seed to 42 throughout.
- Record the vocabulary mapping dict in the output `analysis.log`.
- Record git commit hash of the repo state.
- Record inputs SHA256 of the GT and detections files.

## 8. Timeline estimate

| Phase                                     | Duration |
|-------------------------------------------|---------:|
| Finalise decisions (§6) with user         |    0.1 d |
| Draft `analyse_subtype_classification.py` |    0.5 d |
| Dry-run on single buffer, sanity-check    |    0.2 d |
| Sapphire bootstrap run (3 buffers × pool) |    0.3 d |
| Write report.md, iterate on tables        |    0.5 d |
| User review + paper-table extraction      |    0.4 d |
| **Total from "go" to results in hand**    | **~2 d** |

## 9. Risk register

- **Risk**: matching at 50 m may pair a detection with a subtype-mismatched
  GT that happens to be the nearest. **Mitigation**: report 20 m
  sensitivity — the tightest buffer in the sensitivity table is a lower
  bound on this form of coincidence pairing.
- **Risk**: settlement_mound n=5 means 1 error moves F1 by 0.2. **Mitigation**:
  the sparse-class policy (§5) reports raw cells, avoids bootstrapping
  settlement F1, and notes the sample size in every table row.
- **Risk**: the Rakovski case-variant (`Burial Mound`) is not a typo but a
  meaningful distinction missed by the GT-QA pass. **Mitigation**: flag
  for QA review as part of decision §6.6. If ambiguous, run the analysis
  both ways.
- **Risk**: VLM confidence is vote-share, not probability; miscommunicating
  this would be a paper-quality issue. **Mitigation**: explicitly deprioritise
  Brier score in §3.2 and call it out in the report.md methods section.

## 10. Appendix: example confusion-matrix template

Matched-pairs 4×4 (rows = GT, columns = predicted):

|                         | burial | benchmark | trig | settlement | row total |
|-------------------------|-------:|----------:|-----:|-----------:|----------:|
| Burial mound            |    ?   |     ?     |   ?  |     ?      |     455   |
| Bench mark              |    ?   |     ?     |   ?  |     ?      |      65   |
| Triangulation point     |    ?   |     ?     |   ?  |     ?      |      43   |
| Settlement mound        |    ?   |     ?     |   ?  |     ?      |       5   |
| **col total**           |    ?   |     ?     |   ?  |     ?      |    ≤568   |

(Col total ≤ GT total because some GT are unmatched; the 5×5 version
fills in the mismatch rows.)

---

END OF PLAN
