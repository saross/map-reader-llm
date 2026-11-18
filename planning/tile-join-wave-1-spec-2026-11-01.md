# Tile-join Wave 1 — specification (code, tests, erratum draft, dry-run, smoke test)

> **Last revised**: 2026-11-18 (gate R round 2: Astra's focused changes
> applied). See [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), session S168 on amd-tower. Every path, count, line
  number, and confusion matrix below was read from the files named beside
  it, on `main` at `4b7411c9e` (first draft) or `73f74e9af` (this
  revision). Nothing was run on amd-tower beyond reading JSON and the
  standard-library evidence script of the parent record's § 2.6 (D70: its
  venv is not matched to the reference environment).
- **Parent**: `planning/tile-join-resolution-2026-11-01.md` (the decision
  record; this document specifies its § 4 and the Wave 1 row of its § 5).
  Rulings: D72 and D73 in `planning/pi-decisions-2026-09-20.md`.
- **Status**: **DRAFT, revised after gate R rounds 1 and 2.** Astra's
  reviews
  (`~/agent-mail/codex/outbox/claude/20261101T225231Z-astra-tile-join-record-and-wave1-review.md`,
  `…/20261118T050438Z-astra-tile-join-round-2-review.md`) are answered in
  § 10; the PI approved this revision on 2026-11-18. **Gate R is closed.
  Blocked only on the PI's approval to launch (P2).**
- **Target**: all data and results settled, and the write-up begun, by
  **Sunday 2026-11-29** (PI, 2026-11-18; first set to 2026-11-22, moved
  the same day).
- **Runs on**: zbook, **unattended from launch to M1, stopping only on a
  problem** (D73 (7); § 5). **Zero API calls.**

## 0. What Wave 1 does, in one paragraph

Wave 1 makes the D72 and D73 rulings the scorer's behaviour without
re-scoring the corpus. Tile classification defaults to containment within
each sheet, and the per-tile count tables to the nearest-centre tile of
each detection's scoped sheet. Both are new, named joins. The three
frame-wide joins (`id`, `geometric-primary`, `geometric-contains`) stay
available for replaying historical artefacts. A permanent perfect-detector
test, extended with seam and edge cases, checks the new rules. A smoke test
then re-scores eight evaluations in a scratch copy: five representative
cells and the three withheld Gemini 3.7 cells. The wave also drafts erratum
E93 and its OSF record, and dry-runs the Wave 2 corpus driver, measuring
the cost of the corpus re-score before anyone commits to it.

## 1. Preconditions (launch is blocked until all hold)

| # | Precondition | How it is checked |
|---|---|---|
| P1 | Gate R closed: Astra's round-2 review delivered, the PI has ruled on it, this document revised accordingly | **met 2026-11-18** (§ 10, § Changelog) |
| P2 | The PI approves this specification for launch | stated in conversation; recorded in § Changelog |
| P3 | zbook's `.venv` still matches the reference environment | `uv pip freeze` equals `requirements-lock.txt`; tier 1 passes at the reference count before any change (`docs/agent-guidance.md`, "Reference environment") |
| P4 | zbook's checkout is on `origin/main`, clean, 0 behind | `git fetch && git status -sb` |

Nothing on sapphire is needed. The board's per-cell frame-wide contains
readings are committed: 150 gates under `mcc_permutation.gates` in
`results/tile-join-audit/era2-board-mcc-tiering-2026-10-30/mcc-family-geometric-contains.json`
(Astra, S4).

## 2. What the gap analysis found

The first draft's read-only gap analysis found five things; Astra's review
corrected one of them and added three. As they stand:

1. **The downstream drivers read "not the default" as "sensitivity".**
   `era1_leaderboard_tiering.py`, `k_ladder_mcb.py`,
   `k_ladder_mcc_test.py`, and `selection_aware_intervals.py` branch on
   `tile_join != TILE_JOIN_DEFAULT`; `mcc_tiering_55map.py`,
   `k_ladder_clipped_cells.py`, and `evaluate_detections.py` take the
   default as an argument. Changing one constant would silently invert
   every one of these meanings. (Astra: supported.)
2. **Their committed-record gates would fail between Waves 1 and 3** on
   every evaluation not yet re-scored, as the comment above
   `TILE_JOIN_DEFAULT` predicts (`scripts/lib_advanced_metrics.py:133–148`).
   (Astra: supported.)
3. **Join provenance is recorded inconsistently, not absent** (corrected;
   Astra, S3). Newer evaluations record the classification join in both
   `summary.tile_classification.tile_join` and `_metadata.cli_args.tile_join`
   (for example
   `results/55map-final-board-r2-2026-09-06/cells/ARM1-N1-carried/evaluation.json`,
   both `id`; written at `evaluate_detections.py:1461`). Older ones, such as
   `results/k-ladder-2026-09-12/phase2/cells/pv-diag-384__pv-high-image-t0_3-n1-opmax/evaluation.json`,
   record neither. **No evaluation records the count-table rule**, because
   the old classification option never controlled the F1 count arm.
4. **The count-table change reaches the coverage flags.** Each
   `summary.buffers[]` entry's `coverage` block, `coverage_status`,
   `sparse_coverage`, `ci_unreliable`, `ci_excludes_point`, and
   `ci_flag_basis`, and the summary's roll-ups, derive from the per-tile
   table (`TILE_JOIN_WITHHELD_QUANTITIES`, `lib_advanced_metrics.py:178–189`).
   So do the precision and recall intervals, bootstrap means, and methods
   (`bootstrap_ci`, from `:3489`; Astra, R4). (Astra: supported.)
5. **Legacy replay must precede replacement** (Astra: the principle is
   good). E81's guard 1 (the recomputed confusion must equal the committed
   one) cannot be reused as written, because the new rule changes the
   confusion by design. Replay uses **each artefact's own recorded rule**,
   handles known refusals explicitly, and only then computes under the new
   rules.
6. **F1 replay has no count-table option** (Astra, S2). `bootstrap_ci`
   takes no join (`lib_advanced_metrics.py:3489–3498`), and its callers pass
   none (`evaluate_detections.py:1234–1240`; `era1_leaderboard_tiering.py:316–318`
   calls `compute_per_tile_tp_fp_fn` on its default). After the change, a
   classification-only `--tile-join id` could not reproduce old F1
   intervals or families.
7. **One branch would mislabel indicators** (Astra, S2). The default branch
   of `selection_aware_intervals.py` (`:896–899`, `build_board_tile_counts`)
   derives its MCC indicators from the F1 count arm. Those indicators must
   never be presented as classification-join MCC.
8. **The existing geometric routines reach across sheets** (Astra, R2;
   parent record § 2.6). They book detections and assign references against
   every frame tile (`lib_advanced_metrics.py:2960–2975`, `:3005–3011`,
   `:5010–5013`), so the K-35-052-4 edge tiles become positive for Elenovo
   mounds lying in their black no-data padding.

## 3. Work items

### W1.0 Dry run, census, and worklist (first, before code)

Read-only. Output: `reports/tile-join-wave-1/dry-run.md` and
`reports/tile-join-wave-1/worklist.json`.

- **Field schema.** Every `evaluation.json` field the classification join
  or the count table determines is the *target set*, everything else the
  *non-target set*, in `summary`, each `per_run[]` entry, summary
  roll-ups, legacy aliases (`f1` beside `f1_point`, and so on), and the
  `.md` and `.csv` siblings. Start from § 2 items 3 and 4, then search
  `evaluate_detections.py` for every consumer of the per-tile table rather
  than trusting this list. The schema must be complete before Wave 2.
- **Census** (Astra, S5). There are 2,817 tracked files named exactly
  `evaluation.json`, plus 12 `results/retest/*-evaluation.json` files
  (2,829 in all, by suffix). Of the 2,817, 2,646 contain
  `tile_classification`, and 33 of those are under `archive/`. Classify
  every file by:
  - frame;
  - construction route (merged or unmerged, taken from how the file was
    built, not from whether `source_tiles` is present: older materialisers
    discarded that list; unknowns labelled as such);
  - single or replicated;
  - recorded classification join (or none);
  - paper-cited or not (cited by a signed register row or `docs/paper/`).
- **Worklist.** One entry per file, with a status and a reason:
  `already-migrated`, `reproducible-legacy`, `known-withheld`,
  `unresolved-recipe`, `historical-only` (`archive/` and frozen artefacts,
  which get labelled corrected counterparts, not overwrites; D73 (5)).
  Every paper-cited file must have a status other than `unresolved-recipe`
  before Wave 2 can claim completeness.
- **Recipe and input identity.** For each smoke cell, recover detections,
  references, bounds, buffers, and bootstrap settings through the D22
  fallback chain (`rescore_tile_mcc_e81.recover_recipe`). Pin input file
  hashes, run order, seed, iteration count, and environment. A matching
  aggregate confusion is a tripwire, not proof of input identity.
- **Determinism.** Re-running the bootstrap under each cell's recorded
  rules, with its recorded `seed` and `n_iterations` (seed 42 and 10,000
  BCa draws in smoke cell 1), reproduces the committed intervals. A cell
  that does not reproduce has drifted for some other reason (as in E72):
  it is ledgered and left alone, never overwritten.
- **The 55-map GS sheet check** (parent record § 2.6, owed). Run the
  equivalent of `sheet_boundary_check.py` on the 55-map references and
  frame. If adjacent sheets there genuinely print the same mound and only
  one copy was digitised, sheet-specific scoring would score a correct
  detection on the other sheet as a false positive. Report every
  cross-sheet pair within 500 m and every cross-sheet tile contact, with
  pixel positions. **If any contact lies on map content rather than
  padding, stop and report** (§ 5).
- **Cost.** Time every smoke evaluation, legacy replay and new joins both,
  all intervals, and the repeatability check. Then project Wave 2's total
  CPU-hours and its wall-clock at a worker count that zbook's memory
  allows. The 55-map cell (8,541 tiles) is timed separately.
- **Smoke paths.** Select and pin cells 3–5 (§ 6) before the smoke launch,
  recording why each qualifies.
- **The 3.7 eligibility table** (Astra, round 2). Before any corrected
  result exists, record one row per (cell, family) pair for the three W1.4
  cells. Each row cites the family's existing inclusion criteria and the
  committed exclusion evidence, and gives the verdict the W1.4 rule
  produces. A missing or ambiguous exclusion record makes the row
  **unresolved**, which stops the wave (§ 5); it is never resolved by
  looking at the new score. Output: `reports/tile-join-wave-1/withheld-37.md`.

### W1.1 Two sheet-specific joins, two defaults, and replay

In `scripts/lib_advanced_metrics.py`:

- **New joins under new names**, so historical provenance stays
  unambiguous (the names below are proposed; Astra's round 2 may amend
  them):
  - `sheet-contains`, for classification: a tile is reference-positive if
    a reference recorded on the tile's sheet lies in it, and detected if a
    detection scoped to the tile's sheet lies in it;
  - `sheet-primary`, for count tables: each matched or unmatched detection
    is booked once, and each unmatched reference once. The candidates are
    the tiles **of the point's own sheet that the point intersects**,
    using the shared scope's `intersects` predicate, so a point on a shared
    edge is a candidate for both neighbours. Among them the nearest
    centroid wins, and an exact tie goes to the lexicographically smallest
    `tile_name`, so the result does not depend on input order (Astra,
    S2.3). This is the existing `geometric-primary` construction
    (`lib_advanced_metrics.py:2960–2975`) restricted to one sheet;
    historical tie behaviour is left untouched for replay.
- **A reference's sheet is read through the existing resolver,**
  `reference_map_column` (`lib_advanced_metrics.py:2405–2427`): `Map` in
  the GS, `source_map` in the 55-map ground truth (Astra, S2.2). Tile
  sheets come from the same catalogue the per-sheet symbol matching uses
  (`_attribute_rows`, from `:1936`; the per-sheet loop, from `:2440`).
  Nothing re-derives a sheet from an alphabetical member or a separate
  name parser.
- **A detection's sheet is the one `DetectionScope` already chose for
  matching** (D50; `lib_advanced_metrics.py:2051`), taken from its
  `detections` and `sheets`, not from the legacy `retained` collection.
  Do not substitute `assign_primary_tiles_on_origin_sheet` (`:2678`)
  blindly: its choice among several origins must agree with the scope.
- **An in-frame detection with no attributable sheet** (Astra, S2.1). Today
  the classification path scopes with `require_attribution=False` and
  books `scope.retained` across the whole frame (`:4991–5013`), so a
  non-empty input without origin columns has frame-wide occupancy and no
  scoped sheet. Under a sheet join this case gets a **named refusal**
  (`tile_join_unattributed_detection`), reported with its count and
  diagnostics, never a silent drop and never a frame-wide booking:
  - a detection with no `source_tiles` list but a valid `source_tile`
    keeps D50's existing attribution, and is not refused;
  - legitimate D50 exclusions and parent-frame exclusions stay distinct,
    each diagnosed under its own name, and are not counted as missing
    attribution;
  - the historical joins keep their historical behaviour, and symbol
    matching is not changed to make any test pass;
  - any input needing a different policy is an uncovered decision, which
    stops the wave (§ 5).
- **The booking invariant counts the sheet-scoped population,** with
  exclusions reported beside it. Comparing it with the old frame-wide
  union count would wrongly reject the intended removal of cross-sheet
  contacts.
- **Defaults:** `TILE_JOIN_CLASSIFICATION_DEFAULT = "sheet-contains"` and
  `TILE_JOIN_COUNT_TABLE_DEFAULT = "sheet-primary"`.
  **`TILE_JOIN_DEFAULT` is retired** (D73 (6)): every importer fails until
  it chooses one explicitly.
- **Refusals:** `compute_per_tile_tp_fp_fn` refuses `sheet-contains` and
  `geometric-contains`, naming D72 (2), because containment books one
  detection to several tiles and would double-count.
- **Legacy replay:** `id`, `geometric-primary`, and `geometric-contains`
  remain selectable, for both purposes where they applied historically.
- **Count-table rule threaded through** `bootstrap_ci` and every wrapper
  that reaches a count table: `evaluate_detections.py`,
  `era1_leaderboard_tiering.py`, `selection_aware_intervals.py`,
  `k_ladder_mcb.py`, `k_ladder_mcc_test.py`, `mcc_tiering_55map.py`, and
  `k_ladder_clipped_cells.py`. Each gets separate classification and
  count-table options, with their meanings recorded in its header.
- **Two computations, in order** (Astra, S2):
  1. validate a historical input under the rules it recorded (a missing
     classification record means `id`; a missing count-table record means
     the legacy name rule);
  2. compute *every* analysed value — arrays, scores, ranks, and
     metadata — under the explicitly requested rules.

  No output may carry an old committed MCC beside newly computed arrays.
  Contradictory provenance is rejected. The missing-provenance fallbacks
  apply to historical inputs only: every new output records its rules.
- **Provenance written:** every emitted `tile_classification` block records
  `tile_join`; every block whose intervals or coverage come from a count
  table records `count_table_join`; `_metadata` records both, with a
  pointer to D72 and D73.

### W1.2 The perfect-detector test, permanent (tier 1), and the edge cases

New module `tests/test_perfect_detector.py`, tier 1, per the standing rule
in `docs/agent-guidance.md`: feed the ground truth back as the prediction,
in every shape the pipeline produces.

- **Frames:** the real Era-2 frame
  (`inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson`) with
  the GS references, as two **separately named fixtures** (Astra, round
  2):
  - `historical_alphabetical`, the S167 construction, where a merged point
    is named for the alphabetically first containing tile; it picks a
    different sheet for 15 references, so it proves the classification
    defect but is not a valid fixture under D50 (Astra, S1);
  - `sheet_preserving`, where each reference keeps its own sheet. Astra's
    independent probe expects 224 reference-positive and 263
    reference-negative tiles under sheet-specific containment, and MCC 1.

  Also synthetic overlapping frames with a seam between two sheets and
  padding beyond one sheet's edge, each built twice: once with references
  recording their sheet in `Map`, once in `source_map` (Astra, S2.2).
- **Merged** (one point per mound): tile-MCC, sensitivity, specificity,
  and symbol F1, precision, and recall are all 1.0 under the new defaults.
- **Unmerged** (one point per mound and containing tile): tile
  classification is perfect. Symbol scores are 1.0 only after the points
  pass through the real within-run deduplication path. Without it, the
  test asserts the expected false-positive penalty: one reference and two
  identical predictions give TP 1, FP 1, FN 0, precision 0.5, F1 2/3
  (Astra, S1).
- **Replicated** identical runs: each pass reproduces, and the declared
  aggregation preserves them. Per-run means, pooled counts, and a summary
  confusion taken from `run_1` (`confusion_source`,
  `evaluate_detections.py:395`) are distinct quantities, and each is
  tested.
- **Count tables:** `sheet-primary` sums to the symbol-level totals
  overall and **per sheet**, against `per_sheet_confusion`.
- **Edge cases** (Astra, S6):
  - exact tile-label alignment;
  - permuted input order and tied distances;
  - differing tile vocabularies;
  - missing origins and cross-sheet origins;
  - reduced and parent frames;
  - a withheld-to-valid transition;
  - an empty detection set (`evaluate_detections.py:1423` skips the
    classification block when `n_det` is 0);
  - degenerate MCC (TN + FN = 0);
  - and, as a real-data regression, the K-35-052-4 `x4032` edge tiles,
    which must not become positive for Elenovo mounds.
- **Unattributed detections** (W1.1; Astra, S2.1), each with its expected
  outcome stated in the test: no origin columns at all (named refusal
  under a sheet join; historical behaviour under the historical joins); a
  missing `source_tiles` list with a valid `source_tile` (scored by D50's
  attribution, no refusal); a D50 exclusion and a parent-frame exclusion
  (each diagnosed under its own name, neither a refusal).
- **Tie-break and boundary** (W1.1; Astra, S2.3): a point equidistant from
  two candidate centroids goes to the smaller `tile_name` whatever the
  input order; a point on a shared edge is a candidate for both tiles; a
  sheet tile that the point does not intersect is never a candidate, even
  if its centroid is nearer.
- **Replay and provenance regressions** (Astra, round 2): default calls;
  explicit historical calls; mixed old and new input files; contradictory
  metadata (rejected); a new output missing provenance (rejected); and the
  `selection_aware_intervals.py:891–899` branch, whose default path derives
  MCC indicators from the F1 count arm and must never be labelled as
  classification-join MCC.
- **Legacy sentinel:** the merged Era-2 input under `id` gives tile-MCC
  0.8711 (TP 196, FP 0, FN 33, TN 258; `perfect_detector.txt`), pinned so
  that the defect stays documented. Astra found the same legacy confusion
  on both fixtures, because the 15 renamed references do not change it;
  the test asserts that on both.
- **Red sentinel:** in a real-file copy of `scripts/` and `tests/` (copied,
  never symlinked), set the classification default back to `id`, then
  separately remove the sheet restriction. Confirm the new tests turn red
  for each, and that the copy's sources diff equal once restored.

### W1.3 Erratum E93 and the OSF record, drafts

E93 is the next free number (the highest erratum in
`docs/methodology/preregistration/protocol-errata.md` at `73f74e9af` is
E92). Reserve it with an entry marked **DRAFT** on the Wave 1 branch,
framed per D73 (1):

- the original § 4.2 text preserved;
- `id` shown invalid for merged output (the perfect-detector evidence);
- sheet-specific containment presented as a clarification made after
  results were known, stating when, and which results were known then;
- a placeholder before/after table, which Wave 2 fills and Wave 4
  finalises.

Draft the matching OSF transparent-changes record beside it, in
`reports/tile-join-wave-1/osf-transparent-changes-draft.md`. **Posting it
to OSF is an external action: the PI approves the exact text, and Wave 1
only drafts it.**

### W1.4 The three withheld Gemini 3.7 cells, by the D73 (4) rule

The board's tiering (`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json`,
`withheld_cells`) lists three cells withheld under `id`:

| Cell | Committed F1 |
|---|---:|
| `gemini37-screen-2026-08-28::g37-text-k1-verified-carried-p0.10-k1` | 0.8616 |
| `gemini37-screen-2026-08-28::g37-text-k1-verified-opmax` | 0.8747 |
| `gemini37-screen-2026-08-28::g37-text-k3-verified-opmax` | 0.9135 |

**The eligibility rule, fixed here before any new inference is seen.** A
cell re-enters every family it otherwise qualifies for if, and only if:

- its *only* recorded reason for exclusion was the tile-join refusal
  (`tile_join_detection_shortfall` or `tile_join_reference_shortfall`);
- no other technical refusal or frame problem stands (absence of a
  vocabulary shortfall alone is insufficient; Astra, R5);
- it scores successfully under the new defaults.

Its scores, favourable or not, play no part. Wave 1 applies the rule and
reports the outcome; Wave 3 recomputes each affected family and admissible
set whole, and shows the fixed-old-family comparison beside it. In the
smoke run, each cell's legacy replay must end in its **expected, recorded
refusal**, with unaffected point estimates and input identity verified. It
must then score successfully under the new rules. Never bypass a refusal to
manufacture a legacy confusion.

### W1.5 Smoke test

Re-score the five cells of § 6 and the three of W1.4 with the Wave 1 code,
in a scratch copy on zbook (a detached clone; the S166 pattern). Nothing
is written into the repository except the ledger and reports. Each run is
replayed under its recorded rules, then computed under the new ones, then
re-run once to confirm the result is idempotent.

## 4. Gate G1 (all must hold before M1)

1. **F1, precision, and recall point estimates byte-identical** in every
   buffer of every smoke cell.
2. **Legacy replay reproduces** each pass's committed confusion **and
   committed intervals** exactly, under its recorded rules, then the
   declared aggregation. A W1.4 cell's expected refusal counts as a
   reproduction; any other refusal or drift is fatal. New intervals may
   change and are ledgered.
3. **Against the historical contains readings** (cells 1 and 2):
   `sheet-contains` differs from the frame-wide reading only on tiles that
   another sheet's evidence reaches, and every such tile is listed and
   explained.
4. **Reference-positive tiles** equal the count of tiles holding at least
   one of their own sheet's references, recomputed independently of the
   scorer.
5. **Count tables sum** to the symbol-level totals, overall and per sheet,
   for every buffer and every pass.
6. **Non-target fields byte-identical** (W1.0 schema). Target-field changes
   are ledgered per field, coverage flags included.
7. **Idempotent:** a second run over the same inputs gives identical
   outputs.
8. **Tier 1 green** on zbook at the reference count plus the new tests;
   `ruff check` and `npx markdownlint-cli2` clean on touched files.
9. **A fresh-context `/audit`** of the code change has run, and each of
   its findings is resolved or carries a written disposition explaining
   why it is resolved or not blocking. Recording a known blocker is not a
   pass.

## 5. Running unattended, and what stops it

The PI ruled that Wave 1 runs **unattended from launch to M1, unless there
is a problem** (D73 (7)). It proceeds through W1.0–W1.5 without
consultation. Any of the following is a problem: it **stops the wave**,
and the session sends the PI a push notification and writes up the stop.

- **the failure of any G1 item** (§ 4), including non-target drift, a
  failed independent reference count, a failed repeatability check, a
  lint failure, or an unresolved blocking audit finding;
- a point F1, precision, or recall change;
- a legacy replay mismatch, or an unexpected refusal;
- an in-frame detection without an attributable sheet in any smoke cell
  (the named refusal of W1.1);
- an unresolved row in the 3.7 eligibility table (W1.0);
- a sheet-specific difference from the historical reading on a tile that
  no other sheet's evidence reaches;
- a count-table sum mismatch, overall or per sheet;
- the 55-map GS check finding a cross-sheet contact on map content;
- a write outside the scratch copy, the Wave 1 branch, or
  `reports/tile-join-wave-1/`;
- a tier-1 failure that is not a pre-existing skip;
- any decision this specification does not cover.

Launch discipline for the smoke run: all three file descriptors
redirected; nothing after the launch on the same line; setup separated by
`;`; a pid file; watchers on terminal state (`scripts/wait_for_run.py`)
and log staleness, never `pgrep -f`; failure filters matched
case-insensitively (`docs/agent-guidance.md`, "Compute Location").

## 6. Smoke cells

Paths were resolved through `results/run-conditions.json`
(`decomposition[run].conditions[].eval_path`) at `4b7411c9e`. The
historical contains readings are frame-wide, so they are comparison values
for gate G1 item 3, not targets.

| # | Role | Cell | `evaluation.json` directory | Committed `id` confusion (TP, TN, FP, FN; MCC) | Historical frame-wide contains reading |
|---|---|---|---|---|---|
| 1 | Era-2 GS, merged, 487 tiles, includes the K-35-052-4 edge tiles (the K = 1 rung of the HIGH image T 0.3 ladder) | `pv-diag-384::pv-high-image-t0.3-n1-opmax` | `results/k-ladder-2026-09-12/phase2/cells/pv-diag-384__pv-high-image-t0_3-n1-opmax/` | 204, 241, 17, 25; 0.827 | 221, 233, 25, 8; 0.866671, identical in the board's gates (`results/tile-join-audit/era2-board-mcc-tiering-2026-10-30/mcc-family-geometric-contains.json`) and the K-ladder's (`results/k-ladder-2026-09-12/mcc-join-2026-10-30/geometric-contains/phase2-mcc-test/tiering/phase2-flash-high-image-n5-image-t0-3/tiering_20m_geometric-contains.json`) |
| 2 | K-ladder 55-map rung, 8,541 tiles, 50 m buffer, sheet seams | `stride-55map-2026-08-25::g384-ov128-55map-n1-oracle-p0.20-k1-r2-gt` | `results/55map-final-board-r2-2026-09-06/cells/A-N1-oracle/` | 2424, 4847, 165, 1105; 0.7006 | 3138, 4765, 247, 391; 0.845541 (`…/geometric-contains/mcc-test/tiering/55map-stride-a-r2/tiering_50m_geometric-contains.json`, `mcc_permutation.gates`) |
| 3 | Era-1 512 px | pinned in W1.0: paper-cited, on a 512 px frame | — | — | none committed |
| 4 | Grid | candidate `grid-2026-08-18::g512-ov064-k10-c1-k8` (`results/grid-2026-08-18/conditions/g512_ov064/eval/`); W1.0 confirms it is paper-cited, or substitutes one that is | — | — | none committed |
| 5 | Replicate-mean | pinned in W1.0: paper-cited, `per_run` ≥ 3 | — | — | none committed |
| 6–8 | The three withheld 3.7 cells (W1.4) | see W1.4 | resolved in W1.0 | expected refusal | none |

Across cells 1–5, at least one must be **unmerged** by construction
route. `outputs/era1-pv-stage-d/512-single-image-t0.0/eval_t0.1/evaluation.json`
(`per_run` 3) is one candidate for cells 3 and 5, if W1.0 confirms it is
paper-cited.

## 7. Before Wave 2 may be specified as ready

Beyond G1 (Astra, S6):

- a complete target and non-target schema (W1.0);
- a small reference case checked independently of the scorer;
- an idempotent rerun (G1 item 7);
- a reconciled worklist and ledger: success, expected refusal, skip, and
  failure, each with a reason, and every paper-cited file resolved.

## 8. Outputs (committed)

- Code and tests on branch **`tile-join-wave-1`**, with a pull request
  (PR), merged only after the PI approves at M1.
- `reports/tile-join-wave-1/`, all following the document revision policy
  (banner and changelog):
  - `dry-run.md` and `worklist.json` (W1.0);
  - `smoke-ledger.md` and `smoke-ledger.json` (before and after for every
    target field of every smoke cell, legacy replay results, and timings);
  - `withheld-37.md` (W1.4, with the eligibility outcome);
  - `osf-transparent-changes-draft.md` (W1.3).
- The E93 draft entry, on the same branch.

## 9. Milestone M1: what the PI receives, and decides

The PI receives:

- the G1 checklist, with the evidence for each item;
- the smoke ledger: ΔMCC, and every target field that moved, including
  any coverage-status or interval-reliability flip;
- the 55-map GS sheet-check result;
- the W1.4 eligibility outcome for the three 3.7 cells;
- W1.0's census, worklist summary, and measured Wave 2 cost;
- the E93 and OSF drafts;
- the PR link.

The PI decides:

1. **Merge** the Wave 1 PR.
2. **Coverage flips:** if the smoke test shows any, whether a flipped
   `ci_unreliable` or `coverage_status` is published as the new value (the
   default, since it describes the corrected table) or held for review.
3. **The OSF text:** approve, amend, or hold.
4. **Launch Wave 2**, with its specification (written during Wave 1 from
   W1.0's findings) and the measured cost.

## 10. Gate R round 1: Astra's findings on this specification

| Finding | Disposition |
|---|---|
| Retire `TILE_JOIN_DEFAULT` rather than alias it | Agreed; ruled D73 (6). W1.1 |
| S1: the unmerged perfect detector cannot score symbol F1 1.0; the real-frame fixture must keep each reference's sheet | **Error in the first draft**, corrected. W1.2 |
| S2: validate under the recorded rule, then compute everything under the requested rule; thread the count-table rule through; guard `selection_aware_intervals.py` | Adopted. § 2 items 5–7, W1.1 |
| S3: provenance is inconsistent, not absent | **Error in the first draft**, corrected. § 2 item 3 |
| S4: the board's contains gates are committed | **Error in the first draft** (an output listing was cut short before reaching them), corrected. § 1, § 6 |
| S5: classify by construction route; worklist with statuses; preserve historical evidence; census definitions | Adopted; `archive/` split ruled D73 (5). W1.0 |
| S6: stronger tests, eight cell cases, expected refusals, per-pass replay, pre-Wave-2 requirements | Adopted. W1.2, W1.4, § 4, § 7 |
| R2 (record): sheet semantics | Sheet-specific, ruled D73 (2). W1.1, W1.2, § 4 item 3 |

**Round 2** (review at `dce74be05`:
`~/agent-mail/codex/outbox/claude/20261118T050438Z-astra-tile-join-round-2-review.md`).
Verdict: focused changes requested before unattended launch; the new join
names and the two-computation replay are sound; no redesign needed. The PI
approved the revision below on 2026-11-18.

| Finding | Disposition |
|---|---|
| S2.1 (P1): define the outcome for an in-frame detection with no attributable sheet | Named refusal under the sheet joins, historical behaviour kept, D50 and parent-frame exclusions kept distinct, expected-outcome tests; the booking invariant counts the sheet-scoped population. W1.1, W1.2, § 5 |
| S2.2 (P2): references carry their sheet in `Map` or `source_map` | Read through `reference_map_column` and the shared catalogue; fixtures built with each column. W1.1, W1.2 |
| S2.3 (P2): candidates must intersect the point; deterministic tie-break | Intersecting tiles of the point's own sheet, nearest centroid, smallest `tile_name` on a tie; historical tie behaviour untouched. W1.1, W1.2 |
| Eligibility made mechanical | A (cell, family) table recorded in W1.0 before corrected results; an unresolved row stops the wave |
| Replay regressions, including `selection_aware_intervals.py:891–899` | Explicit tests. W1.2 |
| Historical fallbacks must not license unrecorded new outputs | Stated. W1.1 |
| Name the historical and sheet-preserving fixtures separately | Done. W1.2 |
| Failure of any G1 item stops the wave; an audit disposition must explain itself | Added. § 4 item 9, § 5 |
| Legacy replay includes the committed intervals | Added. § 4 item 2 |

## Changelog

### 2026-11-18 — Gate R round 2 answered (S168, amd-tower)

Trigger: Astra's round-2 review (§ 10) and the PI's approval of this
revision. Contract clarifications only; the design and the rulings are
unchanged.

| Item | Before | After |
|---|---|---|
| Gate R (P1) | round 2 pending | met |
| Detections with no attributable sheet | unspecified ("missing origins" test) | named refusal under the sheet joins, with defined exceptions |
| Reference sheet | `Map` | `reference_map_column` (`Map` or `source_map`) |
| `sheet-primary` candidates | the sheet's tiles | the sheet's tiles the point intersects; tie to smallest `tile_name` |
| 3.7 eligibility | rule only | rule plus a (cell, family) table fixed in W1.0 |
| G1 item 2 | confusion | confusion and committed intervals |
| Stop list | eight conditions | adds any G1 failure, unattributed detections, unresolved eligibility rows |
| Target | not set | Sunday 2026-11-29 (first set to 2026-11-22, moved the same day) |

### 2026-11-18 — Revised after gate R round 1 (S168, amd-tower)

Trigger: Astra's review (§ 10) and the PI's rulings D73 (1)–(7).

| Item | Before | After |
|---|---|---|
| Classification default | `geometric-contains` (frame-wide) | `sheet-contains` (new) |
| Count-table default | `geometric-primary` (frame-wide) | `sheet-primary` (new) |
| `TILE_JOIN_DEFAULT` | retire recommended | retired (D73 (6)) |
| Gap findings | 5 | 8; item 3 corrected |
| Smoke cases | 5 | 8 (the three 3.7 cells added) |
| G1 items | 8 | 9, with item 3 now "differences only on cross-sheet tiles" |
| The 3.7 cells | a PI decision at M1 | the D73 (4) rule, fixed in W1.4 |
| Running mode | unspecified | unattended to M1, stopping on a problem (D73 (7)) |
| Sapphire | readings to recover if reachable | not needed (S4) |

Unchanged: the five representative smoke roles, the committed `id`
confusions of cells 1 and 2, and the zero-API-call constraint.

### 2026-11-01 — Original publication

Drafted at S168 on amd-tower while Astra reviewed the parent record (gate
R). It specified Wave 1 from the parent record's § 4 and added five design
points from a read-only gap analysis. It was not approved for launch. It
recorded the PI's ruling to retire `TILE_JOIN_DEFAULT` on 2026-11-02
(`73f74e9af`).
