# H13 — tile overlap: F1, cost-efficiency, and edge detection

> **Last revised**: 2026-08-18 (cost figures corrected to the billed
> basis). See [§ Changelog](#changelog) for revision history.

**What this is.** The registered three-arm H13 overlap contrast
(`docs/methodology/preregistration/osf/preregistration.md:1014-1048`),
executed at last. Arms B and C ran on 2026-08-17/18 (erratum E75
disclosed the contrast as silently dropped; the S134 walk ruled it back
in); this document reports the three registered analyses — F1 as a
function of overlap, cost-efficiency per additional API dollar, and
edge detection — over all three arms under one uniform scoring rule.

**What this is not.** A claim about the study's headline pipeline. Every
number here is for the single carried configuration (`brief-text`,
`gemini-3-flash-preview`, T = 1.0, MINIMAL thinking, 512 px, single
pass, no consensus and no verifier). The registration frames H13 as a
within-configuration contrast, and the Era-1 board never resolved a
single-pass optimum (a 20-cell Tier-1 tie), so the result is stated
"for the carried configuration" under the project's no-peak-picking
plateau rule.

## The headline

**More overlap buys recall and loses more precision. F1 falls
monotonically as overlap rises**, and every pairwise difference is
significant under the registered instrument.

| Arm | Overlap | Stride | Tiles/pass | Precision | Recall | **F1** |
|---|---|---|---:|---:|---:|---:|
| **A** | 12.5 % | 448 px | 340 | 0.4484 | 0.7379 | **0.5578** |
| **B** | 25 % | 384 px | 430 | 0.3887 | 0.7844 | **0.5198** |
| **C** | 50 % | 256 px | 999 | 0.2616 | 0.8717 | **0.4025** |

Common scope, 20 m buffer, mean of three passes per arm, uniform 20 m
within-pass deduplication. Pooled counts: A 397.0 TP / 488.3 FP /
141.0 FN; B 422.0 / 663.7 / 116.0; C 469.0 / 1323.7 / 69.0.

### Paired tile-bootstrap contrasts

| Contrast | ΔF1 | Registered B = 1,000, CI95 | E54 sensitivity B = 10,000, CI95 | Excludes 0 |
|---|---:|---|---|---|
| A − B | +0.0380 | [+0.0009, +0.0708], p = 0.0500 | [+0.0015, +0.0741], p = 0.0416 | yes, both |
| A − C | +0.1554 | [+0.1214, +0.1889], p = 0.0010 (floor) | [+0.1204, +0.1890], p = 0.0001 (floor) | yes, both |
| B − C | +0.1174 | [+0.0922, +0.1437], p = 0.0010 (floor) | [+0.0919, +0.1422], p = 0.0001 (floor) | yes, both |

The A − B interval is the narrow one: its lower bound sits at +0.0009
at B = 1,000, i.e. the 12.5 %-vs-25 % step clears zero but only just.
A − C and B − C are unambiguous. Read the A − B step as "directionally
consistent, marginally resolved", not as a firm effect.

## Analysis 2 — cost-efficiency per additional API dollar

All figures are the amount **actually billed**. Gemini real-time flex
carries the same 50 % discount as the async Batch API, which the run
metadata did not apply — see the basis note below.

| Arm | Calls (3 passes) | Spend | $/call | F1 | F1 per $ |
|---|---:|---:|---:|---:|---:|
| A | 1,020 | $0.6854 *(imputed)* | $0.000672 | 0.5578 | 0.8138 |
| B | 1,290 | $0.8736 | $0.000677 | 0.5198 | 0.5950 |
| C | 2,997 | $1.9983 | $0.000667 | 0.4025 | 0.2014 |

| Step | ΔF1 | Δ$ | F1 per additional $ |
|---|---:|---:|---:|
| A → B | −0.0380 | +$0.1882 | −0.2019 |
| B → C | −0.1173 | +$1.1247 | −0.1043 |
| A → C | −0.1553 | +$1.3129 | −0.1183 |

**Every additional dollar of overlap buys negative F1.** The registered
analysis asked what F1 an additional API dollar purchases; for this
configuration the answer is that it purchases none, and the money is
better left unspent. The three arms' measured per-call rates agree to
within 1.5 %, so the ranking is not a pricing artefact.

*Imputation disclosure*: arm A's three passes ran free-tier in March
2026 and carry `total_cost_usd = 0.0` in their metadata. Arm A is
priced here at $0.000672/call, the mean of the measured arm-B and
arm-C billed rates, so the three arms sit on one basis. Arms B and C are
audited spend, summed from the committed per-pass `cost_estimate`
blocks (arm B includes its single-tile recovery pass) and then halved
to the billed basis. Total H13 arms-B+C spend, including the smoke
test: **$2.8744 billed** ($5.7488 at list price).

*Cost-basis note (added 2026-08-18)*: this section originally quoted
list price throughout, because the run metadata recorded it. Gemini
real-time flex carries the same 50 % discount as the async Batch API,
so the recorded figures were about twice the actual bill. Every dollar
figure above has been halved. **No ratio, ranking or conclusion
changed** — all three arms sat on one basis, so the relative
cost-efficiency argument was unaffected; only the absolute amounts were
wrong. The writer now records the billed amount with list price beside
it (`cost_basis` field), so the ambiguity cannot recur.

## Analysis 3 — edge detection

This is the registered mechanism question, and the one place where
overlap does exactly what it was supposed to do.

For each ground-truth mound and each arm, `best_margin` is the largest
distance to a tile edge that the mound ever enjoyed, taken over the
arm's own tiles that contain it. It measures the most central look the
arm ever gave that mound. Denser tiling should raise it, and does:

| Arm | min | p10 | median | max | share < 100 m |
|---|---:|---:|---:|---:|---:|
| A | 9.2 m | 217.2 m | 498.0 m | 1219.1 m | 1.9 % |
| B | 95.5 m | 351.0 m | 597.7 m | 1270.4 m | 0.2 % |
| C | 116.1 m | 657.1 m | 824.5 m | 1272.1 m | 0.0 % |

Under arm A, ten of the 538 in-scope mounds are marooned within 100 m
of the nearest tile edge in every tile that contains them — one of them
9.2 m from an edge. No arm-C mound is closer than 116 m to an edge.

**Recall on that marooned subgroup is where the overlap gain lives:**

| Subgroup | n | Recall A | Recall B | Recall C |
|---|---:|---:|---:|---:|
| Arm-A best margin < 100 m | 10 | **0.2667** | **0.7667** | **0.9333** |
| Arm-A best margin ≥ 100 m | 528 | 0.7468 | 0.7847 | 0.8706 |

Recall binned on arm A's margin (a fixed x-axis, so each mound stays in
one bin across arms and bin-wise differences are arm effects):

| Arm-A margin | n | Recall A | Recall B | Recall C |
|---|---:|---:|---:|---:|
| 0–50 m | 4 | 0.000 | 0.750 | 1.000 |
| 50–100 m | 6 | 0.444 | 0.778 | 0.889 |
| 100–200 m | 36 | 0.722 | 0.787 | 0.889 |
| 200–400 m | 161 | 0.679 | 0.768 | 0.841 |
| 400–800 m | 228 | 0.776 | 0.810 | 0.890 |
| 800–1300 m | 103 | 0.796 | 0.754 | 0.867 |

Arm A misses every one of the four most edge-marooned mounds in all
three of its passes. Arm C finds all four. The edge effect the
registration hypothesised is real, and it is sharply localised — it
concentrates in under 2 % of mounds, which is why fixing it cannot pay
for the precision the denser tiling costs elsewhere.

## Why F1 falls: it is not a deduplication artefact

The S135 phase gate caught that `evaluate_detections.py` has no
deduplication step, so a mound seen in two overlapping tiles is emitted
twice and the copy scores as a false positive. Left unfixed, that alone
would have manufactured "overlap hurts precision". All three arms are
therefore scored after the preregistered within-pass 20 m
deduplication (§ 8.5 Step 1) — arm A included, which is why **the
committed arm-A F1 values are superseded and not comparable with the
numbers here**.

Deduplication removes exactly what the geometry predicts:

| Arm | Overlap | Raw dets/pass | Deduplicated | Removed |
|---|---|---:|---:|---:|
| A | 12.5 % | 973 / 931 / 927 | 916 / 869 / 871 | 5.9 % / 6.7 % / 6.0 % |
| B | 25 % | 1,361 / 1,361 / 1,380 | 1,124 / 1,118 / 1,163 | 17.4 % / 17.9 % / 15.7 % |
| C | 50 % | 3,034 / 3,130 / 3,125 | 1,844 / 1,877 / 1,887 | 39.2 % / 40.0 % / 39.6 % |

After removing every duplicate, arm C still carries 1,323.7 false
positives per pass against arm A's 488.3 — a 2.7× increase in
*distinct* spurious locations for a 2.9× increase in tiles. The
precision collapse is therefore a genuine property of looking at the
same ground more times, not a scoring artefact: each additional look is
an independent opportunity to hallucinate a mound somewhere new, and
those new false positives are not duplicates of anything, so no
deduplication rule can remove them.

## The evaluation-footprint hazard (caught this session)

The plan's scoring chain specified uniform deduplication but assumed the
three arms cover the same ground. They do not. Each arm's
footprint-majority manifest selects a different tile set, and the tile
unions diverge:

| Arm | Tiles | Union area | Ground truth in scope |
|---|---:|---:|---:|
| A | 340 | 1751.2 km² | 539 |
| B | 430 | 1694.8 km² | 563 |
| C | 999 | 1847.0 km² | 565 |

Arm C's footprint is a strict superset of arm A's; arm B's is neither.
Scored natively, each arm would face a different ground-truth
denominator over different terrain — a tile-inclusion artefact
confounded with the overlap factor under test.

**Resolution.** Every arm is scored on a **common footprint**, the
intersection A ∩ B ∩ C (1637.5 km², 538 mounds), carried on the arm-A
tile grid clipped to that intersection. Detections are clipped to the
same geometry and reassigned to the carrier grid, so all three arms are
scored over identical ground on an identical resampling unit — which is
also what makes the bootstrap deltas genuinely *paired*. The clip costs
arm A nothing (0 of its detections; the 113.7 km² of arm A outside arm B
is blank sheet margin holding one mound and no detections), arm B 43–53
detections per pass, and arm C 74–78.

**How much did it matter?** Little, as it turns out — but that is a
finding, not an assumption:

| Arm | F1 common scope | F1 native scope | Δ |
|---|---:|---:|---:|
| A | 0.5578 | 0.5576 | 0.0002 |
| B | 0.5198 | 0.5222 | −0.0024 |
| C | 0.4025 | 0.4067 | −0.0042 |

Both scopes are committed (`common/` and `native/` under this
directory). Tile-level MCC, by contrast, is *not* robust to the choice —
arm B reads MCC 0.258 on the common carrier grid and 0.012 on its own
430-tile grid — because MCC's tile-classification units are the bounds
tiles themselves. Only the common scope compares MCC like for like, and
even there all three arms sit in a low band (A 0.106, B 0.258,
C 0.059) driven by very low specificity on a grid where most tiles hold
at least one mound. **MCC is reported here for completeness and should
not carry an overlap claim.**

## Method

- **Scoring set**: `outputs/h13/scoring/{common,native}/arm{A,B,C}/run_N/detections_dedup.geojson`,
  built by `scripts/prepare_h13_scoring.py`. Within-pass 20 m greedy
  deduplication (`merge_passes.deduplicate_within_pass`, § 8.5 Step 1);
  cluster mean centroids as points, which is loss-free because the
  evaluator's Hungarian matcher reduces every geometry to its centroid.
- **Evaluation**: `scripts/evaluate_detections.py` at 20 m with `--mcc`,
  three passes per arm, per-arm outputs under `common/` and `native/`.
- **Contrasts**: `scripts/h13_overlap_analysis.py`. Per-tile TP/FP/FN
  averaged over the arm's three passes, then a paired tile bootstrap —
  one resampled index set applied to both arms of a contrast, seed 42,
  percentile CI95, two-sided p = max(2 · min tail, 1/B), B = 1,000
  registered primary (Decision 10) and B = 10,000 E54 sensitivity.
  The registered quantity is the CI and the CI-excludes-zero reading;
  the p-value is carried for comparability with the family-FDR
  convention only.
- **Arm B run_1** is the concatenation of its main pass (429 tiles) and
  its additive single-tile recovery pass, reconstructing the full
  430-tile pass without mutating either committed artefact.

## Qualifications

1. **Vintage asymmetry (disclosed at audit).** Arm A's passes are March
   2026 pipeline vintage; arms B and C are August. Configuration and
   instruction file are identical (system-instruction hash
   `e169b7237b85…` on all three arms), and temperature was corrected to
   T = 1.0 at audit precisely to match arm A. The residual is E66-class
   orchestration evolution. The model string also differs in form —
   arm A records `gemini-3-flash`, arms B and C `gemini-3-flash-preview`
   — a labelling difference in how the alias was resolved, not a
   knowingly different model.
2. **One configuration, not the pipeline.** No consensus, no verifier.
   The overlap effect under a consensus or proposer-verifier stage is
   untested; there is a plausible argument that consensus voting would
   suppress the very false positives that sink arm C, and this analysis
   cannot settle it.
3. **The A − B step is marginal** (CI lower bound +0.0009 at B = 1,000).
   The monotone ordering rests on A − C and B − C.
4. **Arm A's cost is imputed**, not audited (see § Analysis 2).
5. **Ten mounds** carry the edge finding's headline subgroup. The
   direction is stark and consistent across bins, but the subgroup is
   small; treat the 0.267 → 0.933 figure as an illustration of the
   mechanism, not a precise effect size.
6. **One silent detection drop**, found in cross-checking: arm B run_2's
   metadata records 1,362 detections but its GeoJSON holds 1,361. The
   cause is `scripts/4_detect_mounds_batch.py:606-607`, where a parsed
   detection lacking a `box_2d` key is counted by the results tracker
   but skipped when features are built — and, unlike the
   malformed-length branch just below it, logs nothing. The GeoJSON is
   the authoritative artefact and all analyses use it; the affected
   quantity is one detection in 1,362 (0.07 %).

## Verification

`scripts/verify_h13_overlap.py` re-derives every load-bearing number
from the committed raw artefacts along a deliberately separate code
path — it imports none of `lib_advanced_metrics`, `merge_passes`,
`evaluate_detections`, or `h13_overlap_analysis`, and reimplements the
deduplication, the footprint intersection, the ground-truth scoping and
the Hungarian matching from primitives. **20/20 checks pass**: per-pass
raw and deduplicated counts (9 passes), common-footprint area,
ground-truth-in-scope count, per-arm precision/recall/F1, audited cost
for arms B and C, and the edge low-margin subgroup size and per-arm
recall. Per-arm F1 agrees to within 0.0012 (the verifier assigns a
detection to the first intersecting tile rather than the
nearest-centroid tile, which moves a handful of border detections
between map scopes).

Gate reproduced: validation V1's arm-A run_1 deduplication figure
(973 → 916, −57) is recovered exactly.

## Artefacts

- `h13_overlap_analysis.json` — all three analyses, machine-readable;
  the source for every number above.
- `per_tile_counts.json` — per-arm per-tile TP/FP/FN (bootstrap input).
- `common/arm{A,B,C}/evaluation.{json,csv,md}` — primary scope.
- `native/arm{A,B,C}/evaluation.{json,csv,md}` — secondary scope.
- `outputs/h13/scoring/` — deduplicated detection sets, per-arm and
  common bounds, `dedup_summary.json`.
- Register row: `h13-overlap-arms` in `results/analyses-manifest.json`
  (classification PROPOSED post-hoc per the discharge principle; PI
  ratification queued).

## See also

- **Preceding experiment(s)**: `planning/h13-arms-bc-plan-2026-08-17.md`
  — phase gate, validations V1–V4, audit outcome and run record for the
  arms-B+C execution this analysis scores.
- **Preceding experiment(s)**: `results/retest/retest-production-summary.md`
  — the Phase 2a `brief-text` passes reused as arm A.
- **Follow-up experiment(s)**: None. The registered H13 analyses are
  complete; any overlap-under-consensus follow-up is unregistered and
  unscheduled.
- **Run output directory**: `outputs/h13/` (arms B and C passes, the
  smoke test, and the derived scoring sets under `outputs/h13/scoring/`).
- **Working-notes Observations**: None yet — candidates raised at
  session close.
- **Decisions / Errata**: E75 — H13 registered but silently dropped;
  this analysis discharges it and its disposition is updated in
  `docs/methodology/preregistration/protocol-errata.md`. E54 — the
  10,000-iteration narrow-effect bootstrap convention. E66 — pipeline
  vintage drift between March and August passes. Decision 10 —
  tile-level resampling, percentile CI95, B = 1,000.

## Changelog

### 2026-08-18 (later) — Cost figures corrected to the billed basis

Trigger: Gemini real-time flex was found to carry the same 50 % discount
as the async Batch API, which the run metadata did not apply. § Analysis 2
therefore quoted list price as though it were spend.

| Quantity | Before (list) | After (billed) |
|---|---:|---:|
| Arm A spend (imputed) | $1.3708 | $0.6854 |
| Arm B spend | $1.7472 | $0.8736 |
| Arm C spend | $1.9983 × 2 = $3.9966 | $1.9983 |
| Total, incl. smoke | $5.7488 | $2.8744 |
| F1 per $ (A / B / C) | 0.4069 / 0.2975 / 0.1007 | 0.8138 / 0.5950 / 0.2014 |
| F1 per additional $ (A→C) | −0.0592 | −0.1183 |

**What did NOT change**: every F1, precision, recall and MCC value; the
arm ranking; the paired bootstrap contrasts; the edge-detection result;
and the conclusion that every additional API dollar spent on overlap buys
negative F1. All three arms shared one cost basis, so the relative
argument was never affected — only the absolute amounts.

Landed with the writer-side fix that records the billed amount alongside
list price and an explicit `cost_basis` field (defect D13).

### 2026-08-18 — Original publication

Session 136, executed on sapphire, $0 API. The $0 scoring chain
specified in `planning/h13-arms-bc-plan-2026-08-17.md` § 7, plus the
evaluation-footprint hazard caught in this session and resolved with a
common-scope design. F1 falls monotonically with overlap
(0.558 / 0.520 / 0.402); all three paired contrasts exclude zero; the
registered edge mechanism is confirmed and localised to ten
edge-marooned mounds. Independent verification 20/20.
