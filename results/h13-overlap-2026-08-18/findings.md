# H13 — tile overlap: F1, cost-efficiency, and edge detection

> **Last revised**: 2026-10-13 (the post-hoc Tier-0 aggregation sweep
> regenerated on the origin route, PI ruling D62 (1): 18 of its 27 points
> rise; no number in this document's body changes). 2026-10-12: the sweep's
> F1 intervals regenerated on the fixed bootstrap adapter, PI ruling D61
> (1); no point estimate and no number in this document's body changes.
> 2026-10-05: p-values from the paired permutation test, PI ruling D42; no
> verdict changes. 2026-08-19: bootstrap standardised to B = 10,000 per
> erratum E82; the three per-arm evaluations re-scored at that count. See
> [§ Changelog](#changelog) for revision history.

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

| Contrast | ΔF1 | **B = 10,000, CI95 (primary)** | B = 1,000, CI95 (superseded) | Excludes 0 |
|---|---:|---|---|---|
| A − B | +0.0380 | **[+0.0015, +0.0741], p = 0.0385** | [+0.0009, +0.0708], p = 0.0385 | yes, both |
| A − C | +0.1554 | **[+0.1204, +0.1890], p < 0.0001** | [+0.1214, +0.1889], p < 0.0001 | yes, both |
| B − C | +0.1174 | **[+0.0919, +0.1422], p < 0.0001** | [+0.0922, +0.1437], p < 0.0001 | yes, both |

B = 10,000 is primary from 2026-08-19 (erratum E82); the 1,000-iteration
column is retained because it is what Decision 10 pre-specified. Point
estimates are identical under both, and no verdict changes. The p-values
are the paired tile-swap permutation test's (PI ruling D42, 2026-10-05),
which does not depend on the bootstrap count, so both columns carry the
same p.

The A − B interval is the narrow one: its lower bound sits at +0.0015,
i.e. the 12.5 %-vs-25 % step clears zero but only just. A − C and B − C
are unambiguous. Read the A − B step as "directionally consistent,
marginally resolved", not as a firm effect. The extra resampling effort
resolved it slightly more comfortably than the registered count did
(bootstrap p 0.0500 → 0.0416), a gain in Monte Carlo precision, not
evidence; the permutation test now gives p = 0.0385.

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
  percentile CI95, **B = 10,000 primary**; p-values from the paired
  tile-swap permutation test (10,000 permutations, seed 42; PI ruling
  D42 retired the bootstrap p = max(2 · min tail, 1/B)) (erratum E82, 2026-08-19), with the B = 1,000 count
  Decision 10 pre-specified retained alongside. This resampler is the
  analysis script's own and was never on the D15 defective path, so the
  change is Monte Carlo precision only.
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
3. **The A − B step is marginal** (CI lower bound +0.0015 at B = 10,000;
   +0.0009 at the superseded B = 1,000). The monotone ordering rests on
   A − C and B − C.
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
- `tier0-aggregation/` — the post-hoc Tier-0 aggregation sweep
  (corroboration × consensus, 27 cells; E41-class, outside the
  registered H13 row; `scripts/h13_aggregation_sweep.py`). Its F1
  intervals were regenerated on 2026-10-12, and its points on 2026-10-13
  on the origin route (§ Changelog).
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

### 2026-10-13 — Tier-0 aggregation sweep: points regenerated on the origin route (PI ruling D62 (1))

**Refresh trigger**: PR #41 (merged as `602593ecb`) made the sweep's
aggregated clusters keep their contributing proposer tiles
(`origin_tiles`) and tiled each cluster on its own sheet
(`h13_aggregation_sweep.write_cell`). Until then they were tiled as bare
centroids by location alone, so D50's scorer fell back to the legacy
cross-sheet rule (`reports/s163-agent-records/origin-gap-h13-copies.md`
§ 1.4). PI ruling D62 (1) regenerates the sweep once, after that fix; it
was regenerated on PR #35's branch with `main` merged in (`9f8119e97`).

**Integrity**: two independent runs on sapphire (one in place, one into a
scratch directory) agree byte for byte on the Markdown and all 27 cell
files, and on the JSON apart from `generated_at_utc`; the kernel's
bad-page count stayed 0. All 27 cells equal the after-values PR #41's
record gives (n, F1, and both interval bounds at four decimal places).

**Before → after** (F1 with BCa CI95, B = 1,000, seed 42): 18 of 27 cells
rise, by +0.0050 to +0.0162. The nine `c = 3` cells, in which no cluster
changes sheet, do not move, and no cell's detection count changes.

| Arm | Best cell (c, k) | Before | After |
|---|---|---|---|
| A | (1, 3) | 0.6264 [0.5639, 0.6803] | 0.6426 [0.5858, 0.6938] |
| B | (1, 3) | 0.6331 [0.5756, 0.6874] | 0.6415 [0.5860, 0.6933] |
| C | (2, 3) | 0.7114 [0.6567, 0.7602] | 0.7191 [0.6673, 0.7659] |

Each arm's best cell keeps its (c, k). Arm A's best now edges arm B's
(0.6426 against 0.6415; before, B led by 0.0067). The sweep tests no
contrast between arms and the two intervals overlap almost entirely, so
this is a change of order inside noise, and "B ahead of A after
aggregation" should not be read from the sweep. The headline reading,
that overlap's ranking inverts under aggregation (arm C best), stands.
The full 27-row table is in PR #41's record, § 1.4.

**What did NOT change**: the registered H13 overlap analysis and every
number in this document's body (the per-pass sets the main analysis
scores already carried their tiles); the nine `c = 3` cells; each arm's
best (c, k). **Superseded**: the 2026-10-12 entry below says the Markdown
and the cell files were byte-identical after regeneration, so Obs 416
needed no change. That held for the interval regeneration alone. Now
`tier0_sweep.md` and all 27 cell files change (each cell file also
records `origin_tiles`), and Obs 416 quotes three moved values: 0.7114
(P 0.7347, R 0.6896), 0.6264, and 0.6331 become 0.7191 (P 0.7426,
R 0.6970), 0.6426, and 0.6415. Observations are not edited in place; a
correcting Observation is the PI's call (PR #41's record § 5, item 3).
Commit: the one landing this entry with the regenerated files.

### 2026-10-12 — Tier-0 aggregation sweep: F1 intervals regenerated (PI ruling D61 (1))

**Refresh trigger**: the post-hoc Tier-0 aggregation sweep
(`tier0-aggregation/tier0_sweep.json`; generator
`scripts/h13_aggregation_sweep.py`; E41-class, outside the registered H13
row) was committed on 2026-08-18 (`dccee3362`), the evening before the
bias-corrected and accelerated (BCa) bootstrap adapter fix `122104b8a`
(2026-08-19, defect D15: the adapter transposed scipy's resample batch,
so each interval was read off the wrong distribution). The sweep was never
regenerated, and the D57 (4) Phase 3 re-score found that its 27 points
reproduce while its 54 F1 interval bounds do not
(`reports/s163-agent-records/d57-4-rescore-s3-deltas.md` § Stopped lines).
PI ruling D61 (1) (`planning/pi-decisions-2026-09-20.md`): regenerate the
JSON on today's code, and test the attribution to `122104b8a` by replay
rather than by dates.

**Replay evidence** (sapphire, 2026-10-12): the sweep was run in
disposable `git archive` copies of `122104b8a^` (`19d58ccd9`) and of
`122104b8a`, and on this branch, all with today's virtual environment.
The inputs (`outputs/h13/scoring/`, last changed in `faff43dd4`, and
`inputs/vectors/references/mounds-reference.geojson`) and the sweep
script itself are byte-identical in all three trees; between the parent
and the fix, only `scripts/lib_advanced_metrics.py` differs.

| Tree | 27 points (n, P, R, F1) | 54 F1 interval bounds |
|---|---|---|
| `122104b8a^`, the parent | identical to the committed file | identical to the committed file (54 of 54) |
| `122104b8a`, the fix | identical | none identical; all 27 intervals wider |
| this branch (today's code) | identical | identical to the fix's (54 of 54) |

The stale bounds are therefore the defective adapter's, and nothing
between the fix and today, D50's sheet scoping included, moves the sweep.
`tier0_sweep.md` (points only) and the 27 `cells/*.geojson` files are
byte-identical after regeneration, so Obs 416, which cites the Markdown,
needs no change.

**Before → after** (F1 CI95, BCa, B = 1,000, seed 42; points unchanged):

| Arm | c | k | F1 | Before | After | Width ratio |
|---|---:|---:|---:|---|---|---:|
| A | 1 | 1 | 0.4753 | [0.4348, 0.5092] | [0.4086, 0.5314] | 1.65 |
| A | 1 | 2 | 0.6183 | [0.5855, 0.6518] | [0.5570, 0.6733] | 1.75 |
| A | 1 | 3 | 0.6264 | [0.5930, 0.6581] | [0.5639, 0.6803] | 1.79 |
| A | 2 | 1 | 0.1768 | [0.1507, 0.2005] | [0.1360, 0.2262] | 1.81 |
| A | 2 | 2 | 0.1544 | [0.1293, 0.1770] | [0.1153, 0.2010] | 1.79 |
| A | 2 | 3 | 0.0977 | [0.0746, 0.1177] | [0.0656, 0.1417] | 1.77 |
| A | 3 | 1 | 0.0111 | [0.0038, 0.0180] | [0.0033, 0.0275] | 1.71 |
| A | 3 | 2 | 0.0111 | [0.0038, 0.0180] | [0.0033, 0.0275] | 1.71 |
| A | 3 | 3 | 0.0074 | [0.0012, 0.0133] | [0.0000, 0.0222] | 1.84 |
| B | 1 | 1 | 0.4190 | [0.3845, 0.4524] | [0.3595, 0.4728] | 1.67 |
| B | 1 | 2 | 0.5872 | [0.5560, 0.6201] | [0.5277, 0.6434] | 1.81 |
| B | 1 | 3 | 0.6331 | [0.6037, 0.6637] | [0.5756, 0.6874] | 1.86 |
| B | 2 | 1 | 0.4433 | [0.4138, 0.4743] | [0.3860, 0.4939] | 1.78 |
| B | 2 | 2 | 0.3978 | [0.3660, 0.4300] | [0.3373, 0.4561] | 1.85 |
| B | 2 | 3 | 0.3238 | [0.2952, 0.3580] | [0.2682, 0.3811] | 1.80 |
| B | 3 | 1 | 0.0979 | [0.0729, 0.1191] | [0.0676, 0.1423] | 1.62 |
| B | 3 | 2 | 0.0851 | [0.0596, 0.1022] | [0.0539, 0.1266] | 1.71 |
| B | 3 | 3 | 0.0576 | [0.0407, 0.0725] | [0.0325, 0.0944] | 1.94 |
| C | 1 | 1 | 0.2948 | [0.2678, 0.3248] | [0.2487, 0.3441] | 1.67 |
| C | 1 | 2 | 0.4717 | [0.4370, 0.5052] | [0.4129, 0.5299] | 1.72 |
| C | 1 | 3 | 0.5872 | [0.5507, 0.6155] | [0.5270, 0.6481] | 1.87 |
| C | 2 | 1 | 0.6340 | [0.5996, 0.6677] | [0.5703, 0.6915] | 1.78 |
| C | 2 | 2 | 0.7079 | [0.6756, 0.7355] | [0.6534, 0.7552] | 1.70 |
| C | 2 | 3 | 0.7114 | [0.6793, 0.7398] | [0.6567, 0.7602] | 1.71 |
| C | 3 | 1 | 0.6714 | [0.6380, 0.7034] | [0.6115, 0.7216] | 1.69 |
| C | 3 | 2 | 0.6584 | [0.6263, 0.6889] | [0.6004, 0.7116] | 1.78 |
| C | 3 | 3 | 0.6144 | [0.5789, 0.6459] | [0.5573, 0.6730] | 1.73 |

The widths grow by 1.62 to 1.94 times, around the `sqrt(1000/340)` = 1.71
that the 2026-08-19 entry below gives for the defect on this 340-tile
scope (the sweep's `carrier_tiles`). One
reading moves with them: each arm's best cell had a single-condition
interval disjoint from the others' (arm C, `c ≥ 2`, `k ≥ 3`, against arm
B, `c ≥ 1`, `k ≥ 3`), and the two now overlap. The sweep runs no paired
contrast between arms, so it never tested that separation, and no
committed claim rests on it (Obs 416 cites points).

**What did NOT change**: all 27 points, each arm's best cell (A 0.6264,
B 0.6331, C 0.7114), the Markdown, the cell files, and every number in
this document's body. The registered row `h13-overlap-2026-08-18` does
not cite the sweep; it is still `signed` on `main`, and its re-signing,
which D50 already requires, is a separate step not taken here. Commit:
the one landing this entry with the regenerated JSON.

### 2026-10-05 — p-values from the permutation test (PI ruling D42)

**Refresh trigger**: PI ruling D42 (`planning/pi-decisions-2026-09-20.md`).
`h13_overlap_analysis.paired_bootstrap` keeps its CI and takes p from the
paired tile-swap permutation test; `h13_overlap_analysis.json` regenerated
on sapphire (`5986316b5`).

| Contrast | Before (B = 10,000 / 1,000) | After |
|---|---|---:|
| A − B | 0.0416 / 0.0500 | 0.0385 |
| A − C | 0.0001 / 0.0010 (floors) | < 0.0001 |
| B − C | 0.0001 / 0.0010 (floors) | < 0.0001 |

**What did NOT change**: every ΔF1, CI and verdict.

### 2026-08-19 — Bootstrap standardised to B = 10,000

**Trigger**: the 2026-08-19 PI ruling (erratum E82) standardises the study on
10,000 bootstrap iterations rather than the 1,000 Decision 10 pre-specified.

**Contrast CIs**: the B = 10,000 column, previously carried as an E54
sensitivity, is now primary. Nothing about the analysis changed: this
resampler is `h13_overlap_analysis.py`'s own and was never on the D15
defective path.

| Contrast | ΔF1 | B = 1,000 (superseded) | B = 10,000 (primary) |
|---|---:|---|---|
| A − B | +0.0380 | [+0.0009, +0.0708], p = 0.0500 | [+0.0015, +0.0741], p = 0.0416 |
| A − C | +0.1554 | [+0.1214, +0.1889] | [+0.1204, +0.1890] |
| B − C | +0.1174 | [+0.0922, +0.1437] | [+0.0919, +0.1422] |

**Per-arm evaluations re-scored**: the three `common/arm{A,B,C}/evaluation.json`
ran at B = 1,000 under the pre-`122104b8a` BCa wrapper, so their single-condition
intervals carried the D15 distortion. Re-scored at 10,000 under the fixed
wrapper, their 20 m F1 interval widths move 0.0724 → 0.1226 (A), 0.0657 → 0.1158
(B), and 0.0654 → 0.1106 (C) — about 1.7×, matching `sqrt(1000/340)` = 1.71 on
this 340-tile scope.

**What did NOT change**: every point estimate (F1, precision, recall) reproduced
to within 1e-9 and was gated on that; the monotone ordering; every
CI-excludes-zero verdict; the edge-mechanism and cost-efficiency analyses. The
A − B step remains marginal, resolved slightly more comfortably at the higher
count, which is Monte Carlo precision rather than evidence.

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
