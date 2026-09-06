# Reference revision r2: fold the PI audits into the best-available ground truth and re-run the comparisons

> **Last revised**: 2026-09-06 (close — r2 built; register rows in;
> pre-run review written; clean-context audit returned 4 blockers, chain
> NO-GO until adjudicated next session). See [§ Changelog](#changelog).

**The PI's direction (2026-09-06, Session 148, verbatim in substance)**:
build a reference revision, establish it as the best-available ground
truth, re-run the statistics, comparisons, and leaderboards against it,
update the estimates of remaining false positives (FPs) and false
negatives (FNs), and add an estimated "corrected" F1 / P / R as an
additional column that takes into account what the audits revealed about
double-misses and ground-truth errors.

**Why now.** Two PI audits closed on 2026-09-06 (card
`planning/student-baseline-2026-08-31.md` § 5, § 5b, § 5c; Obs 446, 449,
450, and the census Obs): a complete cluster census (478 tiles, 719 of
the reference's 5,010 mounds) and a 10 % random sample of the empty
tiles (470 of 4,676). Together they enumerate, for the first time, both
directions of reference error with page-anchored provenance:

| Audit finding | Count | Effect on the reference |
|---|---:|---|
| GT points flagged as not a mound (census) | 6 distinct | remove |
| Mounds the model found that the GT lacks (census "detected") | 6 | add (model FPs that are real) |
| True double-misses in clusters (census) | 2 | add |
| Proposed-but-filtered mound (census, k=5 vote-gate kill) | 1 | add |
| True double-misses in the empty stratum (Phase 2 sample) | 5 | add |
| Residual near-duplicate pair in the reference (extension:40 / student:01034, 10.3 m) | 1 pair | the flag already removes extension:40 |

Fourteen additions and six removals against a 5,010-point reference:
small in count, but they are the first measured corrections since
Ruling 21 (`planning/ruling21-application-spec.md`), and they carry the
rates needed for an estimated correction of the unaudited remainder.

## 1. What r2 is, and is not

- **r2 = the Ruling-21 standardised reference + the audit instruction
  set.** It is emitted as NEW artefacts
  (`inputs/vectors/references/best-available-gt-55maps-r2.{geojson,csv}`),
  never by mutating the r1 files or the campaign layers, following the
  Ruling-21 materialisation pattern (its § Materialisation plan, item
  1). r1 (`best-available-gt-55maps.geojson`, 4,731 + 279) stays in the
  tree as the instrument every figure to date was scored on.
- **Still a best-possible reference, not a gold standard** (ruling
  21b). r2 changes the header's honesty statement from "joint
  student+model false negatives unrecovered" to "joint false negatives
  MEASURED at 1.06 % of empty tiles and 0.28 % of clustered mounds, and
  recovered only where the audit sampled". The remainder is what the
  estimated-correction column is for (§ 2).
- **Per-record provenance for every audit change**: layer
  `audit_reviewed`, `position_source = reviewer_mark` (the app's
  ±2.5 m nudge precision), `confidence_grade = directly_reviewed`,
  `provenance = pi_audit_2026-09_<census|empty>_<class>`, and for
  removals a `removed_by = pi_audit_2026-09` row in the provenance table
  (the point leaves the geojson, stays in the table).
- **Deterministic build**: a new
  `scripts/derive_audit_revision_instructions.py` reads the two
  adjudication files (`results/cluster-audit/adjudication.json`,
  `results/empty-tile-audit/adjudication.json`) and emits
  `audit-revision-instructions.csv` (one row per change: action,
  source, class, x, y, matched gt_id, tile, position); a `--vintage r2`
  path in `scripts/materialise_best_available_gt.py` applies it. Re-runs
  are byte-identical.

## 2. The estimated-correction column

The existing "corrected F1" (Obs 220, 267; `compute_corrected_f1_multi_buffer.py`,
Approach B) corrects against a REVIEWED extended GT: it removes the
error the reviewers saw. The new column estimates the error they did not
see, from the rates the audits measured, and carries the uncertainty.
Three rates, each with a Clopper–Pearson 95 % interval:

| Rate | Measured | Where it applies |
|---|---|---|
| p_dm(empty): double-misses per empty tile | 5 / 470 = 1.06 % (0.35–2.47 %) | the 4,676-tile empty frame → ≈ 50 missed mounds (16–115) |
| p_dm(cluster): double-misses per clustered mound | 2 / 719 = 0.28 % (0.03–1.00 %) | the 719 clustered mounds (census complete: no extrapolation) |
| p_err: GT points that are not mounds | 6 / 719 = 0.83 % (0.31–1.81 %) | the 4,291 non-clustered, non-audited mounds → ≈ 36 (13–78) |
| p_om: GT omissions the model already found | 6 / 719 = 0.83 % (0.31–1.81 %) | the same 4,291 → ≈ 36 (13–78) model "FPs" that are real |

For a condition with counts TP, FP, FN against r2 at radius R, the
estimated true state adds residual missed mounds M = p_dm(empty)·4,676
(these are counted in neither TP nor FN today), converts an expected
E_om = p_om·(non-audited mounds) of the FPs to TPs where a detection is
present, and removes an expected E_err of GT errors that today count as
FN (if undetected) or TP (if a detection sits on the wrong point). The
column reports P̂, R̂, F1̂ with an interval from Monte Carlo propagation
of the three Clopper–Pearson intervals (10,000 draws, seed 42), beside
the r2 point estimate, not in place of it. **Two assumptions to state
plainly**: (i) p_err and p_om outside clusters are taken from the
cluster census — clustered mounds may carry MORE errors (duplicates
concentrate there, Obs 396) or FEWER (they were reviewed harder), so the
extrapolation is a stated assumption with its interval, and (ii) the
per-condition split of E_om between conditions is not measured — the
column is a corpus-level correction applied uniformly, which is why it
cannot re-order a board and is presented as a column, not a re-tiering.

## 2b. The student baseline, re-estimated (PI request, 2026-09-06)

The novice baseline was measured directly only on the four Gold
Standard (GS) sheets against the curator GT (Obs 316, 443: P 1.000 /
R 0.9473 / F1 0.9729 at 50 m; FN 5.27 %, CI 2.9–8.8 %), where the
students made no false positives. On the 55-map corpus the student
layer IS the reference's backbone, so student precision was
unmeasurable there — until the census flagged 5 of the 686 clustered
student points as not mounds. The audits therefore support a
corpus-level re-estimate: precision from the flagged share of student
points; recall from the mounds the students missed — the 279
reviewer-confirmed extension mounds, the 14 audit additions, the
estimated unrecovered double-misses in the empty frame, and the
estimated 3.7-found omissions outside the clusters — with the same
Monte Carlo propagation as § 2. It reports beside the GS direct figure,
not in place of it: the two estimate different things (a 4-sheet direct
measurement on a curated GT versus a 55-sheet model-assisted
reconstruction), and their agreement or disagreement is itself a
result for D.7 (Obs 443's person-driven variance).

**Preliminary figure (2026-09-06, on r1 sizes and the audit rates;
to be recomputed on r2 after the five-tile re-review).** Inputs:
4,731 student records; 686 of them in clusters, 5 flagged (0.73 %);
missed by students = 279 extension + 14 audit additions + p_dm(empty)
× 4,676 (≈ 56) + p_om × 4,291 unaudited points (≈ 40); Beta posteriors
with a flat prior, 10,000 draws, seed 42:

| | P | R | F1 | Basis |
|---|---:|---:|---:|---|
| 55-map corpus-level (this estimate) | 0.992 (0.983–0.997) | 0.923 (0.911–0.931) | 0.956 (0.949–0.962) | r1 + audit rates, two extrapolated terms |
| — without the extrapolated terms | 0.992 | 0.941 | 0.966 | directly reviewed misses only (279 + 14) |
| GS-4 direct (Obs 316/443) | 1.000 | 0.947 (FN 5.27 %, CI 2.9–8.8 %) | 0.973 | 4 sheets, curator GT, 50 m |

Reading: the students' corpus-wide false-positive count is small (≈ 39,
15–81, i.e. under 1 %) but not zero as the GS sheets suggested; their
recall sits 2–3 points below the GS-4 figure once the model-found and
estimated unrecovered misses are counted, consistent with the
55-map-implied F1 of 0.934 in Obs 443 lying below the GS-4 0.973. The
two extrapolated terms account for 0.018 of recall — that is the part
the estimator, not the review, supplies.

## 3. Decisions for the PI (rule / reason / what to check)

**Rulings 2026-09-06 (PI):** (1) re-review the 5 empty-stratum
double-misses first — YES, run as a final-check pass
(`final_check_manifest.py --marks-class true-double-miss`); (2) the
estimator in § 2 — ACCEPTED; (3) standardised chain only — ACCEPTED,
with the paper framing: the standardised chain is the chain the paper
discusses; the older canonical chain is mentioned in Methods and
invoked in Results/Discussion only to draw comparisons and note
corrections; (4) sequencing behind the 3.7 register rows and the
membership ruling — AGREED. Item 2 (non-Mound points) was already
moot. The student re-estimate (§ 2b) joins the queue as item 9.

1. **The change set.** Rule: adopt the 14 additions and 6 removals as
   listed. Reason: every one is a directly reviewed mark with a final
   check on the edge cases. Check: the 5 empty-stratum double-misses are
   OUTSIDE any cluster and were reviewed once, not twice — accept on the
   Phase 2 review alone, or re-view them on their farthest-from-edge
   tiles first (13-tile pattern, ~10 min).
2. **The § 4c non-Mound points — ALREADY RESOLVED in r1, no ruling
   needed.** Checked 2026-09-06: r1's `symbol_type` holds only
   `burial_mound` 4,833, `bench_mark_on_mound` 111, `trig_point_on_mound`
   46, and `settlement_mound` 20; the canonical file's 16 "Surface
   feature", 5 "Other", and 2 "NA" records do not survive Ruling 21's
   standardisation. § 4c of the student-baseline card can be closed as
   "moot on the standardised instrument" (the canonical chain, where
   they remain, is historical).
3. **Additions for mounds the model found ("detected", 6).** Rule:
   add them to the reference (they are real mounds); the model's
   detections there become TPs. Reason: that is what a reference is
   for; it is also the direction Obs 220/267 already took. Check DONE
   2026-09-06: after the 6 removals, the nearest surviving r1 point to
   any of the 14 additions is 68.4 m (then 93.3, 96.7, 108.8 m, the
   rest > 300 m), and no two additions lie within 50 m of each other —
   r2 would hold 5,018 points with no new near-duplicate.
4. **The estimator in § 2.** Rule: accept the three-rate design and the
   uniform corpus-level application, or ask for a per-map or per-tier
   variant. Reason: the measured rates are corpus-level; anything finer
   is unmeasured. Check: the MDE appendix's 55-map MDE80 (0.013) against
   the column's interval width — if the interval is wider than the
   board's tiers, the column says so.
5. **Scope of the re-run.** Rule: the standardised chain only (the
   instrument Ruling 21 fixed; the canonical chain stays historical).
   Reason: Obs 444 § (b). Check: § 4's queue.
6. **The 3.7 (and 3.8) cells.** Rule: the pending register-row
   proposal (`planning/gemini37-register-rows-proposal-2026-09-03.md`)
   and the board-membership ruling come FIRST, so the r2 re-score covers
   the final membership once. Reason: sequencing register → membership
   → rebuild (55-map card § 6). Check: the 3.7 cells' standardised
   evaluations exist for the three carried cells only.

## 3a. Register-row and membership rulings (PI, 2026-09-06)

On the 3.7 register-row proposal's eight decisions: (1) `post-hoc`
throughout — agreed; (2) image row carries H1 — agreed; (3) both chains
per 55-map cell plus the canonical B N = 5 companion — agreed, with the
explanation recorded below; (4) **rungs WANTED** (the across-N story and
the economical-extraction options), which reverses the proposal's
recommendation — they need materialised detections and evaluations, so
they are folded into the r2 recompute chain (steps 3–4) and registered
there rather than scored twice; (5) image-GS cells register; (6) schema
pool convention; (7) register both vintages; (8) H14/H15 unchanged,
cross-vendor comparisons deferred to a later paper. **Membership**: all
four 3.7 cells and the 3.8 cell on their appropriate boards — the 55-map
final board gains arm 1, arm 2, and the fourth cell (carried + oracle
rows, and the N = 1 / N = 3 rungs once materialised) beside the
incumbent B; the GS board gains the four GS 3.7 cells (text carried-vf,
text swap, image carried-vf, image swap) and the 3.8 Arm V cell; the
K = 10 text cell and the fourth cell's GS leg are registered conditions
whose board membership the PI can add.

*Why a canonical B N = 5 companion row when everything moves to the
standardised chain*: the register records what was actually scored.
The 3.7 campaign's committed comparisons — D1's dead heat (arm 1 0.8494
vs 0.8502) and the 2×2 five-test family (Obs 444) — ran on the
canonical chain against a canonical B N = 5 value (0.843775) that lives
only inside `results/stride55-2026-08-27/ladder.json`; an analysis row
must point its `conditions_compared` at registered conditions, so
without that row the comparison as executed cannot be registered
faithfully. The standardised (and, after the chain, r2) rows are the
paper's instrument going forward; the canonical rows stay as the record
of what was done, which is also what lets the paper "note corrections"
across chains (ruling 3 of § 3).

## 3b. Step 1 DONE (2026-09-06): r2 materialised

`scripts/derive_audit_revision_instructions.py` →
`results/reference-revision-r2/audit-revision-instructions.csv` (6
removals, 14 additions; summary JSON carries the adjudication files'
SHA-256). `scripts/materialise_best_available_gt.py --vintage r2` →
`inputs/vectors/references/best-available-gt-55maps-r2.{geojson,csv}`
(**5,018 records**: 4,726 `student_standardised`, 278
`extension_standardised`, 14 `audit_reviewed`; symbol types burial_mound
4,840, bench_mark_on_mound 112, trig_point_on_mound 46,
settlement_mound 20) and `…-r2-removed.csv` (the six removed records
with `removed_by`). Gates: gt_id unique; no pair within 15 m; the
campaign gates stay 8/8 green (campaign layers untouched); tier-1 tests
`tests/test_reference_revision_r2.py` reconcile the instruction set with
the adjudications and r2 with r1 ± the changes. Deterministic re-run.

**Two things to disclose with r2.** (a) The empty-stratum re-review:
the PI reported "no errors" on all five double-misses; the app verdicts
saved were `n` (the pass had no known points to confirm against), read
as "the mark stands" and written into the instruction `note` column.
(b) **r2 overrides one Ruling-21 adjudication**: the campaign gates
report "promoted_phantom:40 marked distinct with unreviewed student
no. 1036 at 10.3 m" — the Session-130/131 walk kept the pair as two mounds;
the PI's census inspection of the symbol (tile 98) found one mound, and
r2 removes `extension:40`. A ruling corrected by direct inspection, to
be stated as such in the erratum.

## 4. The recompute queue ($0, no API; sapphire)

Nothing here runs until § 3 is ruled and a pre-run review has walked
the block (it spans more than one session and more than five chained
items).

1. Derive the instruction set; materialise r2; header + provenance
   table; `marking_campaign_gates.py` must stay 8/8 green (campaign
   layers untouched).
2. **Engine gate**: re-score IM-k4 against r1 through the same driver
   and reproduce its committed `evaluation.json` @ 50 m exactly (final
   board card § 5 gate 1); then score it against r2 and record the
   delta as the first data point of the band.
3. Standardised re-score against r2 of every board cell: the 16
   final-board cells (`results/55map-final-board-2026-08-27/cells/`),
   the 3.7 cells per the membership ruling, at 14 buffers with MCC and
   tile-level bootstrap (the IM-k4 template).
4. Rebuild the boards on r2 through the unbroken chain
   (`build_55map_leaderboard.py`, `final_board_build.py`,
   `final_board_sweeps.py`, `final_board_n3_carried.py`): F1 and MCC
   boards, round-robin tile-swap permutation + BH + tiers. **Band
   gate**: r1→r2 deltas within the incumbent band (|Δ| ≲ 0.005 at
   50 m); larger drift halts for diagnosis. **Regression gate**: the
   r1 board reproduces before the r2 board is trusted.
5. Re-measure the reference-dependent analyses in the register:
   `55map-standardised-leaderboard-50m`, `-mcc-50m`,
   `obs280-shared-reference`, `tile-level-f1`; the uplift-supplement
   pairing sets; the sensitivity/MDE appendix's 55-map rows.
6. Add the estimated-correction column (§ 2) to the r2 boards and to
   the paper's results table; regenerate the register rows (new
   analysis rows, `preregistered: post-hoc`, PI-signed) and the
   hypothesis-outcome table where a 55-map figure moves.
7. Re-run the two audit adjudications against r2 (their classes should
   collapse: the added mounds become known-in-GT, the removed points
   vanish) as the closure check.
8. Disclosure: an erratum entry (the reference changed after the
   registered analyses), Methods § M.x reference paragraph, D.8
   limitations (the estimated column's assumptions), and an Obs.
9. **Student baseline re-estimate** (§ 2b): a small script over r2 and
   the audit rates → corpus-level student P / R / F1 with intervals,
   tabulated beside the GS-4 direct figures; feeds D.7 and the
   student-baseline card § 4.

Expected wall-clock: the re-score and board chain took ~1 day of
sapphire time at the final-board build (Session 143); the estimator is
minutes. Expected effect: the change set moves 20 of 5,010 points
(0.4 %; r2 = 5,018), so r1→r2 board deltas should sit inside the 0.005
band; the estimated column will be wider than the tiers. Both are
expectations to test, not assume.

## 4a. Pre-run review (2026-09-06, `/pre-run-review`; grounded in the scripts named)

The PI's additions before the review: author the canonical B N = 5
companion once scored; materialise the N = 1 / N = 3 rungs; full 3.7/3.8
coverage on both boards, the K = 10 text cell and the fourth cell's GS
leg included.

**§ 1 Artefact inventory (per step; paths verified from the emitting
code).** (2) Engine gate: `scripts/evaluate_detections.py` on IM-k4 →
a scratch `evaluation.json` compared to
`results/55maps-standardised-ref-2026-08-14/IM-k4/evaluation.json`;
nothing committed. (3) r2 re-score: one `evaluation.json` per cell
(14 buffers, MCC, BCa 10,000/42) under a NEW home
`results/55maps-r2-ref-2026-09-06/<cell>/` — 16 final-board cells
(`results/55map-final-board-2026-08-27/cells/*/detections.geojson`), the
three 3.7 carried cells and their oracles, the 3.7 N = 1 / N = 3 rungs
(materialised by the first-N derivation of `final_board_sweeps.py`, new
`cells/` entries), and the canonical B N = 5 companion via
`stride55_score.py --cell g384_ov192_55map --verify-dir verify
--union-n <ladder.json runs.g384_ov192_55map.N.5.union_n> --prob-t 0.15
--min-votes 5 --compute-mcc` (canonical chain, tile MCC on). (4) Boards:
`results/55map-final-board-r2-2026-09-06/` (`final_board_50m.json`,
`final-board-50m.md`, `sweeps.json`, `cells/`, the significance figure)
and `results/55map-leaderboard/55map-leaderboard-50m-r2.md` + MCC
sibling via `build_55map_leaderboard.py --reference r2`; the GS Era-2
boards under `results/leaderboard/era2/` rebuilt by
`build_tiered_leaderboard.py` with the seven 3.7/3.8 cells added to the
inventory (text and image tracks; the 3.8 cell and the K = 10 text cell
and fourth-cell GS leg included). (5) Re-measured analyses: new rows
`55map-r2-leaderboard-50m`, `-mcc-50m`, `obs280-shared-reference-r2`,
`tile-level-f1-r2`; uplift-supplement pairing outputs under a `-r2`
suffix; the MDE appendix's 55-map rows. (6) The estimated-correction
column: new `scripts/estimated_correction.py` →
`results/55map-final-board-r2-2026-09-06/estimated-correction.{json,md}`,
and the paper results table. (7) Register: `-r2-gt` condition rows for
every re-scored cell (new suffix beside `-canonical-gt` /
`-standardised-gt`), the rung rows, the companion row, the r2 analysis
rows; manifests regenerated. (8) Disclosure: erratum entry, Methods
§ M.x paragraph, D.8 bullet, an Obs. (9) `scripts/student_baseline_reestimate.py`
→ `results/student-baseline-2026-09-01/reestimate-r2.{json,md}`, card
§ 4 table.

**§ 2 Finished states (countable).** (2) |Δ F1@50| = 0 to 4 dp against the
committed IM-k4 evaluation on r1, and the r2 delta recorded. (3) every
cell in the membership list has an `evaluation.json` on r2 with
`tile_classification.confusion` populated: 16 + 3 + 3 + 6 rungs + 1
companion (canonical) = 29 files; the r2 → r1 drift table has one row per
cell. (4) both 55-map boards tier all 22 cells (16 + 3 carried + 3
oracle) with BH q = 0.05 over all pairs; the r1 board reproduces
first (regression gate); the Era-2 GS text board carries the 3.7 text
K = 5, K = 10, swap, fourth-cell GS leg, and the 3.8 cell; the image
board carries image arms 1 and 2; the image-b anchor 0.8961 reproduces.
(5) each named analysis has an r2 row whose `conditions_compared` are
all `-r2-gt` ids. (6) every board cell carries P̂ / R̂ / F1̂ with an
interval; the column's inputs (three rates, intervals, draw count,
seed) are printed in the JSON. (7) schema-valid manifests; `verify_run_conditions.py`
green; tier-1 suite green. (8) the erratum id exists and is cited from
the Methods paragraph and D.8. (9) the table has three rows (55-map
corpus-level, without extrapolated terms, GS-4 direct). Block finished =
all nine, plus the PI's signature on the register rows and the board.

**§ 3 Stop states.** Spend: any API call → stop (the chain is $0; a
missing verified set must be reported, never re-verified). Invariant
gates red → stop before building on top: the 5 m duplicate audit in
`standardised_gt()` (expected drops 0 on r2 too), the campaign gates
8/8, the G4 sweep-scorer gate (0.003 bound), the family identity gates,
the engine gate, the regression gate. Surprising results → verify the
pipeline, then escalate: any r1 → r2 delta |Δ F1@50| > 0.005 on a
board cell; any tier change on the 55-map board between r1 and r2; any
rank change on the GS boards (the GS reference does not change, so a GS
rank change means a mechanism error); a 3.7 rung out of monotone order
with its N = 5 cell; a companion-row canonical F1 that misses the
ladder's 0.843775 by > 1e-6. Missing or ambiguous inputs → stop, never
substitute (the 3.7 rungs' first-N derivation must use the committed
K = 5 pass order; the companion must use the `verify` (Gemini 3)
probabilities, not `verify_37`). Sequencing: step 4 never starts before
step 3's count is 29/29; step 6 never before step 4's boards exist.
Environment: sapphire only for steps 3–4 (the board chain took ~1 day at
S143); the local machine only for the $0 minute-scale steps 6, 7, 9.

**§ 4 Dependency structure.** Hard: 1 → 2 → 3 → 4 → {5, 6} → 7 → 8;
9 depends on 1 only (it needs r2's layer sizes and the audit rates) and
is simultaneous-safe with 2–8. Coherence orderings: (i) the manifests —
step 7 is the ONLY writer of `results/*-manifest.json` in this block
(steps 3–6 write results homes only), so rows land once; (ii) the
student-baseline card § 4 table — written by step 9 only; (iii) the
r2 board home — written by step 4 only, never by step 3; (iv) the
r1 board and r1 evaluation homes are read-only throughout (the
regression gate needs them intact). Simultaneous-safe: step 9 with
anything; within step 3, cells are independent (workers).

**§ 5 Partial completion.** Every step is deterministic from committed
inputs and resumable: a cell with an existing `evaluation.json` is
skipped, so a halted step 3 resumes; boards are rebuilt whole, so a
halted step 4 leaves no partial board (the JSON is written last).
Visibility: partial state shows as a missing file against the 29-file
count, not as a silent number. Mixed-vintage risk: a board built from a
mix of r1 and r2 evaluations — gated by step 4 reading ONLY from the r2
home and by the 29/29 count; and a prose document straddling chains —
one-commit rule: a results `.md` and its changelog entry move together,
and `results-draft.md` / the paper table move in one commit per document
with the erratum id in the message.

**§ 6 Verification stack.** Layer 0: every board number traces to an
`evaluation.json`; the estimated column's inputs print with the output;
the register rows point at files. Layer 1: ruff, the tier-1 suite, the
schema validations, `verify_run_conditions.py`. Layer 2: a fresh-context
Opus verifier after step 6 re-derives, cold, the winner on each 55-map
board and each GS board from the evaluation files, the r1 → r2 drift
table, and the estimated column for three cells from the printed inputs;
it reports its denominator (files opened, claims re-derived) and its
corrections are claims — a disagreement triggers a third derivation or
PI adjudication, never "verifier wins". Layer 3: a citation-site sweep
for every 55-map number that moves (results-draft, methods-draft,
discussion-outline, the register .md), plus the drift check. Layer 4:
PI signature on the register rows and both boards; the erratum text.

**Hardenings recorded (H1–H9).** H1: r2 enters the board chain through
`standardised_gt()` extended with a `reference` switch that loads the
r2 layers (student, extension, audit) via the same `build_extended_gt`
path, keeping the 5 m duplicate-audit gate — never by bypassing the
engine with the merged geojson. H2: new results homes for every r2
artefact (`55maps-r2-ref-2026-09-06`, `55map-final-board-r2-2026-09-06`,
`-r2` leaderboard files); r1 homes read-only. H3:
`build_55map_leaderboard.py --reference` gains `r2`;
`lib_uplift_supplement.py`'s reference map gains the r2 file;
`register_standardised_gt_conditions.py` gains an r2 mode with the
`-r2-gt` suffix. H4: the companion row is scored on the canonical chain
with `stride55_score.py --compute-mcc` and gated on the ladder's F1 to
1e-6 before authoring. H5: the 3.7 rungs are materialised by the
committed first-N derivation with inherited K = 5 verification and their
oracle points swept on r2 (the board convention), then evaluated; no
rung is registered from sweep numbers alone. H6: step 7 is the only
manifest writer; one regeneration at the end. H7: the clean-context
agent pass runs after this review's amendments are committed and before
step 3 starts, against the card and the scripts it names, with the
naive-reviewer stance and a denominator. H8: the GS boards are rebuilt
with the r1 anchor gate (image-b 0.8961) and must show no rank change
among pre-existing cells. H9: the estimated column is presented beside
the r2 point estimate and never used to re-tier.

## 5. Ties

- `planning/ruling21-application-spec.md` — the pattern this follows.
- `planning/55map-final-board-2026-08-27.md` — the board chain and its
  three gates.
- `planning/student-baseline-2026-08-31.md` § 4c, § 5b, § 5c — the
  audits and the non-Mound question.
- `results/cluster-audit/adjudication.json`,
  `results/empty-tile-audit/adjudication.json` — the change set's
  source of truth (marks with world coordinates, classes, matched
  points).
- Obs 220, 267 (corrected F1 lineage), 396 (residual duplicates), 444
  § (b) (instrument), 446, 449, 450, and the census Obs.

## Changelog

### 2026-09-06 (close) — Clean-context audit received: NO-GO until adjudicated

`reports/r2-chain-pre-run-audit-2026-09-06.md` (fresh-context Opus,
18 scripts and 8 data files opened, 21 claims, 6 probes): **4 blockers,
5 majors, 6 minors**. Blockers: (1) step 3's count is 36 cells, not 29
(the r1 board tiers 23; the 29/29 gate would pass a mixed-vintage
board); (2) `build_55map_leaderboard.py` reads cells by label from
`run-conditions.json`, so the boards depend on the register rows —
step 7 must precede step 4; (3) the companion command as written cannot
run (`stride55_score.py` has no `--compute-mcc`, MCC is unconditional;
its count gate assumes the K = 10 union; no first-N path exists there);
(4) the r1 regression gates (G3 at 1e-9, G4 at 0.003) halt any r2 run
by design, so the gates need an r2 mode rather than a "red → stop"
rule. Majors: H1 contradicts the IM-k4 template (the merged geojson IS
the scorer's input; no r2 layer files exist); r1 homes are written by
module constants with no override; the 3.7 rungs' derivation lives only
in the two `gemini37_*_ladder.py` scripts (canonical chain, ladder.json
only); the Era-2 GS boards do not exist as artefacts and a rank change
after adding cells is legitimate under BH, so H8's tripwire is wrong;
`lib_uplift_supplement` resolves an r2 file to "unresolved" silently.
Clean: the r2 build and the instruction set regenerate byte-identical;
the stride55 `summary.json` DOES carry a tile matrix and MCC, so the
companion row's "no matrix" deferral no longer holds. **Disposition
deferred to the next session** (context budget): every finding is to be
adjudicated fix / accept / dispute and the contract amended before
step 2 runs. The PI had said "looks good" to the review text but had
not yet given the formal go; the chain is NO-GO as written.

### 2026-09-06 (later still) — Register rows landed; pre-run review written

The 3.7/3.8 register rows are in (`f4db3f4fd`, regeneration
`99d13ca1b`: 3 runs, 13 conditions, 6 analyses; canonical B N = 5
companion deferred for want of a tile matrix). The PI added: author the
companion once scored, materialise the N = 1 / N = 3 rungs, and put every
recent 3.7/3.8 cell on its board (K = 10 text and the fourth cell's GS
leg included). § 4a records the six-section pre-run review grounded in
`final_board_sweeps.py`, `final_board_build.py`,
`build_55map_leaderboard.py`, `stride55_score.py`,
`register_standardised_gt_conditions.py`, `lib_uplift_supplement.py`,
and `build_tiered_leaderboard.py`, with hardenings H1–H9. Awaiting the
PI's go/no-go and the stop conditions stated back.

### 2026-09-06 (later) — PI confirmations; GO for the sequence

The PI confirmed that the five `n` verdicts in the empty-stratum
re-review mean "the mark stands" (so all five double-misses enter r2 as
built), agreed the sequencing (3.7 register rows and the membership
ruling first, then the pre-run review, then the recompute chain), and
said go. The paper crops of the seven double-misses and the seven
model-found omissions were cut at verifier geometry
(`results/double-miss-crops-2026-09-06/`, `65e9bdc23`, caption fix
`df8746abc`). § 3b's disclosure (a) is now a confirmed reading, not an
inference.

### 2026-09-06 — Original publication

Scoped in Session 148 at the PI's direction after both audits closed.
Records the change set (14 additions, 6 removals), the r2 artefact
design following the Ruling-21 materialisation pattern, the
three-rate estimated-correction column with its two stated assumptions,
six decisions for the PI, and the eight-step recompute queue with its
gates. Nothing has been run.
