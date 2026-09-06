# Reference revision r2: fold the PI audits into the best-available ground truth and re-run the comparisons

> **Last revised**: 2026-09-06 (original publication — SCOPED, not
> approved to run; decisions for the PI listed in § 3). See
> [§ Changelog](#changelog).

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
#1036 at 10.3 m" — the Session-130/131 walk kept the pair as two mounds;
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

### 2026-09-06 — Original publication

Scoped in Session 148 at the PI's direction after both audits closed.
Records the change set (14 additions, 6 removals), the r2 artefact
design following the Ruling-21 materialisation pattern, the
three-rate estimated-correction column with its two stated assumptions,
six decisions for the PI, and the eight-step recompute queue with its
gates. Nothing has been run.
