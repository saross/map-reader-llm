# Tile-join Wave 1 — specification (code, tests, erratum draft, dry-run, smoke test)

> **Last revised**: 2026-11-01 (original publication, S168). See
> [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), session S168 on amd-tower. Every path, count, and
  confusion matrix below was read from the files named beside it, on
  `main` at `4b7411c9e`. No code was run on amd-tower beyond reading JSON
  (D70: its venv is not matched to the reference environment).
- **Parent**: `planning/tile-join-resolution-2026-11-01.md` (the decision
  record; this document specifies its § 4 and the Wave 1 row of its § 5).
  Ruling: D72 in `planning/pi-decisions-2026-09-20.md`.
- **Status**: **DRAFT. Blocked on gate R.** Astra's review of the parent
  record was requested by agent mail on 2026-11-01
  (`~/agent-mail/claude/outbox/codex/20261101T115954.630788Z-claude-tile-join-resolution-review-request.md`).
  This specification is revised for any PI ruling on that review. It then
  goes to the PI for approval to launch.
- **Runs on**: zbook. **Zero API calls.** Ends at milestone **M1**.

## 0. What Wave 1 does, in one paragraph

Wave 1 makes the D72 rulings the scorer's behaviour without re-scoring
the corpus. Tile classification defaults to `geometric-contains` and the
per-tile count tables to `geometric-primary`. `id` stays available as a
named legacy join. A permanent perfect-detector test proves the result:
a flawless pipeline must score 1.0 in every output shape. It then re-scores
five representative evaluations in a scratch copy, as a smoke test, and
checks them against values already committed. The wave also drafts
erratum E93, scores the three withheld Gemini 3.7 cells for the PI's
decision, and dry-runs the Wave 2 corpus driver. The dry run measures the
cost of the corpus re-score before anyone commits to it.

## 1. Preconditions (launch is blocked until all hold)

| # | Precondition | How it is checked |
|---|---|---|
| P1 | Gate R closed: Astra's review delivered, the PI has ruled on its findings, this document revised accordingly | the review's path and the PI's ruling recorded in § Changelog |
| P2 | The PI approves this specification for launch | stated in conversation; recorded in § Changelog |
| P3 | zbook's `.venv` still matches the reference environment | `uv pip freeze` equals `requirements-lock.txt`; tier-1 passes at the reference count before any change (`docs/agent-guidance.md`, "Reference environment") |
| P4 | zbook's checkout is on `origin/main`, clean, 0 behind | `git fetch && git status -sb` |

**Not a precondition.** The S166 board run's per-cell contains readings
were never committed. They remain only in
`~/scratch/mcc-join-tiering-2026-10-30/` on sapphire
(`reports/s166-agent-records/mcc-join-tiering.md` § 6), and sapphire was
unreachable from amd-tower on 2026-11-01 (`No route to host`). The smoke
test does not need them: the two smoke cells with contains references take
them from the committed K-ladder run (§ 6). If sapphire is reachable, copy
that run's `results/` directory into
`reports/s166-agent-records/mcc-join-tiering-results/` and commit it, so
that Wave 2's gate G2 can check the board against committed values.

## 2. Findings of this specification's own gap analysis

A dry-run reading of the code at `4b7411c9e`, done before writing this
document, found five things the parent record's § 4 does not yet cover.
Each is designed for below.

1. **The downstream drivers read "not the default" as "sensitivity".**
   `era1_leaderboard_tiering.py`, `k_ladder_mcb.py`,
   `k_ladder_mcc_test.py`, and `selection_aware_intervals.py` all branch
   on `tile_join != TILE_JOIN_DEFAULT`. On that branch the run touches only
   the MCC arm, refuses to run on the F1 arm, and labels its output "not
   the published join". `mcc_tiering_55map.py`, `k_ladder_clipped_cells.py`,
   and `evaluate_detections.py` take the default as an argument. Flipping
   one constant would silently invert every one of these meanings.
2. **Their committed-record gates would fail between Waves 1 and 3.** The
   tiering drivers gate each cell by comparing their recomputed MCC with
   the MCC committed in its `evaluation.json`. Once the default changes,
   that comparison fails on every evaluation that Wave 2 has not yet
   re-scored. The comment above `TILE_JOIN_DEFAULT`
   (`scripts/lib_advanced_metrics.py:133–148`) predicts exactly this for
   the board's confusion gate.
3. **No evaluation records its join.** In
   `results/k-ladder-2026-09-12/phase2/cells/pv-diag-384__pv-high-image-t0_3-n1-opmax/evaluation.json`,
   neither `_metadata` nor `_metadata.cli_args` carries `tile_join`. During
   and after Wave 2, a re-scored file and an un-re-scored file would look
   alike.
4. **The count-table change reaches the coverage flags, not only the F1
   intervals.** Each `summary.buffers[]` entry carries `coverage`
   (`n_zero_count_tiles`, `zero_fraction`, `coverage_status`), and with it
   `coverage_status`, `sparse_coverage`, `ci_unreliable`,
   `ci_excludes_point`, and `ci_flag_basis`. The summary also carries
   `ci_unreliable_any_buffer` and `coverage_status`. All of these derive
   from the per-tile table, which is why `coverage_diagnostics` is listed
   in `TILE_JOIN_WITHHELD_QUANTITIES` (`lib_advanced_metrics.py:178–189`).
   Re-booking TP and FP from `id` to `geometric-primary` moves detections
   between tiles. That can change which tiles hold no outcomes, and so flip
   a cell's coverage status and its CI-reliability flag. The parent record's
   § 2.3 lists the intervals, p-values, tiers, and Hsu sets, but not these
   flags.
5. **E81's wrong-source guard cannot be reused as written.**
   `scripts/rescore_tile_mcc_e81.py` guard 1 requires the recomputed
   confusion to equal the committed one. Under the new join it changes by
   design. The guard becomes **reproduce, then replace**: re-score under
   `id` and require the committed numbers exactly (the wrong-source
   tripwire), and only then score under the new joins.

## 3. Work items

### W1.0 Gap analysis and Wave 2 driver dry-run (first, before code)

The project convention requires this before implementation. It is
read-only. Output: `reports/tile-join-wave-1/dry-run.md`.

- **Field inventory.** List every `evaluation.json` field that the tile
  join or the per-tile table determines. This is the *target set*; every
  other field is the *non-target set* and must stay byte-identical. Start
  from § 2 item 4 and from `TILE_JOIN_WITHHELD_QUANTITIES`, in `summary`,
  in each `per_run[]` entry, and in the `.md` and `.csv` siblings. Search
  `evaluate_detections.py` for every consumer of the per-tile table rather
  than trusting this list.
- **Recipe recovery.** For each smoke cell (§ 6), recover detections,
  references, bounds, buffers, and bootstrap settings through the D22
  fallback chain (`rescore_tile_mcc_e81.recover_recipe`). Record any cell
  whose recipe does not resolve.
- **Determinism.** Show that re-running the bootstrap under `id`, with the
  recorded `seed` and `n_iterations`
  (`_metadata.bootstrap`: `seed` 42, 10,000 BCa in the board cell),
  reproduces the committed intervals. A cell that does not reproduce has
  drifted for some other reason (as in E72). It is ledgered and
  left alone, never overwritten.
- **Census.** Recount the 2,646 tile-bearing evaluations
  (`git ls-files`; 2,829 `evaluation.json` files in all at `4b7411c9e`).
  Classify each by frame, merged or unmerged (whether `source_tiles` is
  present), single or replicated (`per_run`), and paper-cited or not
  (cited by a signed register row or `docs/paper/`).
- **Cost.** Time each smoke evaluation and report the Wave 2 aggregate:
  total CPU-hours, then wall-clock at the worker count zbook's cores allow.
  The 55-map cell (8,541 tiles) is the worst case and should be timed
  separately.

### W1.1 Two defaults, one per purpose

In `scripts/lib_advanced_metrics.py`:

- `TILE_JOIN_CLASSIFICATION_DEFAULT = TILE_JOIN_GEOMETRIC_CONTAINS` for
  tile-MCC, tile-F1, sensitivity, and specificity (D72 (1));
- `TILE_JOIN_COUNT_TABLE_DEFAULT = TILE_JOIN_GEOMETRIC_PRIMARY` for
  `compute_per_tile_tp_fp_fn` and everything built on it (D72 (2));
- `compute_per_tile_tp_fp_fn` **refuses** `geometric-contains`, naming
  D72 (2): its `_book` credits a detection to every tile it lies in, so
  under contains a count table double-counts;
- `id` stays selectable as a named legacy join, for reproducing historical
  artefacts.

**Retire the single `TILE_JOIN_DEFAULT` name** (recommended). Every
importer then fails at import and has to choose a purpose explicitly, which
turns § 2 item 1's silent inversion into a loud failure. The alternative,
aliasing it to one of the two new names, keeps imports working but leaves
each caller's meaning unaudited. Then audit all seven drivers in § 2
item 1. In each, re-express "published" and "sensitivity" against the new
defaults, and note the change in its header comment.

**Provenance.** Every emitted `tile_classification` block records
`tile_join`. Every buffer block whose intervals or coverage come from a
count table records `count_table_join`. `_metadata` records both, with a
pointer to D72.

**Gates read provenance.** A committed-record gate compares like with
like: it recomputes under the join the artefact records, and treats an
artefact with no record as `id`. The tiering drivers then work on the
corpus both before and after Wave 2, so Wave 3 can regenerate without a
flag day. Wave 1 changes the gate logic only; it regenerates nothing.

### W1.2 The perfect-detector test, permanent (tier 1)

New module `tests/test_perfect_detector.py`, marked tier 1. This follows
the standing rule in `docs/agent-guidance.md` ("Perfect-detector test"):
feed the ground truth back as the prediction, in every shape the pipeline
produces.

- **Frames:** the real Era-2 frame
  (`inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson`) with
  the GS references, as in
  `planning/tile-join-resolution-2026-11-01-scripts/perfect_detector.py`;
  and a synthetic overlapping frame. The four-tile fixture in
  `tests/test_board_mcc_tile_join.py` (100 m tiles on an 80 m stride) is a
  candidate for reuse.
- **Shapes:** merged (one point per mound); unmerged (one point per mound
  and containing tile); single run; replicated (several identical runs,
  through the `per_run` mean path).
- **Assertions:** with the new defaults, tile-MCC, sensitivity, and
  specificity are 1.0, and symbol-level F1, precision, and recall are 1.0.
  The `geometric-primary` count table sums to the symbol-level totals
  (FP 0, FN 0, TP equal to the matched references). A count table under
  `geometric-contains` is refused.
- **Legacy sentinel:** the same merged input under `id` gives tile-MCC
  0.8711 on the Era-2 frame (TP 196, FN 33; `perfect_detector.txt`). The
  test pins that value, so the defect stays documented and reproducible.
- **Red sentinel:** in a real-file copy of `scripts/` and `tests/` (copied,
  never symlinked), set the classification default back to `id`. Confirm
  the new tests turn red, then confirm the copy's sources diff equal once
  restored.

### W1.3 Erratum E93, draft

E93 is the next free number: the highest erratum in
`docs/methodology/preregistration/protocol-errata.md` at `4b7411c9e` is
E92. Reserve it with an entry marked **DRAFT**, so that no other change
takes the number. The entry states that `id` departed from OSF § 4.2 for
merged output, gives the perfect-detector evidence, and names the
correction. It carries a placeholder before/after table, which Wave 2
fills and Wave 4 finalises. Its framing (correction by erratum, or a
deviation needing a registration update) follows the PI's ruling on gate
R question 1.

### W1.4 The three withheld Gemini 3.7 cells

The board's tiering (`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json`,
`withheld_cells`) lists three cells withheld under `id` for a vocabulary
shortfall:

| Cell | Committed F1 |
|---|---:|
| `gemini37-screen-2026-08-28::g37-text-k1-verified-carried-p0.10-k1` | 0.8616 |
| `gemini37-screen-2026-08-28::g37-text-k1-verified-opmax` | 0.8747 |
| `gemini37-screen-2026-08-28::g37-text-k3-verified-opmax` | 0.9135 |

Score all three under the new defaults in the smoke run's scratch copy, and
confirm that the shortfall invariant no longer refuses them. Report their
tile-MCC and F1 intervals. **Do not enter them into any family**: that
decision is the PI's, at M1 (parent § 4 item 3). The highest of the three
would sit near the top of the board on F1, so admitting it changes
families in a way that is visible.

### W1.5 Smoke test

Re-score five evaluations with the Wave 1 code, in a scratch copy on
zbook. The copy must not be the tree the run reads; follow the S166
pattern of a detached clone. Nothing is written into the repository except
the ledger.

## 4. Gate G1 (all must hold before M1)

1. **F1, precision, and recall point estimates byte-identical** in every
   buffer of every smoke cell.
2. **Reproduce first:** under `id`, each recomputed confusion equals the
   committed one exactly.
3. **Contains matches the committed reading** where one exists (§ 6,
   cells 1 and 2), count for count.
4. **Reference-positive tiles conserved:** TP + FN is the same under `id`
   and contains (229 and 229 for cell 1, 3,529 and 3,529 for cell 2 in the
   committed values).
5. **Count tables sum** to the symbol-level totals under
   `geometric-primary`, for every buffer.
6. **Non-target fields byte-identical** (W1.0 inventory). Target-field
   changes are ledgered per field, coverage flags included.
7. **Tier 1 green** on zbook at the reference count plus the new tests;
   `ruff check` and `npx markdownlint-cli2` clean on touched files.
8. **A fresh-context `/audit`** of the code change has run and its
   findings are resolved or listed.

**Stops (any one halts the wave and goes to the PI):** a point F1, P, or R
change; an `id` reproduction mismatch; a contains mismatch against a
committed reading; a count-table sum mismatch; a write outside the scratch
copy; a tier-1 failure that is not a pre-existing skip.

## 5. Outputs (committed)

- Code and tests on branch **`tile-join-wave-1`**, with a pull request
  (PR). A change to the scorer's default is the kind of change the git
  rules route through a PR. It merges after the PI approves at M1.
- `reports/tile-join-wave-1/`: `dry-run.md` (W1.0), `smoke-ledger.md` and
  `smoke-ledger.json` (before and after for every target field of every
  smoke cell, plus timings), and `withheld-37.md` (W1.4). These follow the
  document revision policy (banner and changelog).
- The E93 draft entry, on the same branch.

## 6. Smoke cells

Paths were resolved through `results/run-conditions.json`
(`decomposition[run].conditions[].eval_path`) at `4b7411c9e`.

| # | Role | Cell | `evaluation.json` | Committed `id` confusion (TP, TN, FP, FN; MCC) | Committed contains reading |
|---|---|---|---|---|---|
| 1 | Era-2 `pv-diag-384`, merged, 487 tiles (the K = 1 rung of the HIGH image T 0.3 ladder) | `pv-diag-384::pv-high-image-t0.3-n1-opmax` | `results/k-ladder-2026-09-12/phase2/cells/pv-diag-384__pv-high-image-t0_3-n1-opmax/` | 204, 241, 17, 25; 0.827 | 221, 233, 25, 8; 0.866671 (`results/k-ladder-2026-09-12/mcc-join-2026-10-30/geometric-contains/phase2-mcc-test/tiering/phase2-flash-high-image-n5-image-t0-3/tiering_20m_geometric-contains.json`, `mcc_permutation.gates`) |
| 2 | K-ladder 55-map rung, 8,541 tiles, 50 m buffer | `stride-55map-2026-08-25::g384-ov128-55map-n1-oracle-p0.20-k1-r2-gt` | `results/55map-final-board-r2-2026-09-06/cells/A-N1-oracle/` | 2424, 4847, 165, 1105; 0.7006 | 3138, 4765, 247, 391; 0.845541 (`…/geometric-contains/mcc-test/tiering/55map-stride-a-r2/tiering_50m_geometric-contains.json`, `mcc_permutation.gates`) |
| 3 | Era-1 512 px | chosen in W1.0: paper-cited, on a 512 px frame | — | — | none committed |
| 4 | Grid | candidate `grid-2026-08-18::g512-ov064-k10-c1-k8` (`results/grid-2026-08-18/conditions/g512_ov064/eval/`); W1.0 confirms it is paper-cited, or substitutes one that is | — | — | none committed |
| 5 | Replicate-mean | chosen in W1.0: paper-cited, `per_run` ≥ 3 | — | — | none committed |

Across the five, at least one cell must be **unmerged**. `id` scored
unmerged output correctly in the perfect-detector test, so its shift there
should be small, and the ledger should show that it is. The committed
`outputs/era1-pv-stage-d/512-single-image-t0.0/eval_t0.1/evaluation.json`
(`per_run` 3) is one candidate for cells 3 and 5, if W1.0 confirms it is
paper-cited.

## 7. How Wave 1 runs

- **Who:** a main Claude session on zbook does W1.1 and W1.2. This code is
  subtle and should not be delegated. W1.0's census can run in parallel as
  a read-only subagent on the `opus` alias. W1.3 and W1.4 follow W1.1, and
  W1.5 follows W1.1 and W1.2.
- **Launch discipline** for the smoke run: all three file descriptors
  redirected, nothing after the launch on the same line, setup separated
  by `;`, a pid file, and watchers on terminal state
  (`scripts/wait_for_run.py`) and log staleness, never `pgrep -f`
  (`docs/agent-guidance.md`, "Compute Location").
- **Expected size:** hours, not days. Code, tests, and five evaluations.
  The 55-map cell's 10,000-draw bootstrap is the longest item. W1.0
  measures it.

## 8. Milestone M1: what the PI receives, and decides

The PI receives:

- the G1 checklist, with the evidence for each item;
- the smoke ledger, showing ΔMCC and every target field that moved,
  including any coverage-status or CI-reliability flip;
- the three withheld 3.7 cells' readings;
- W1.0's census and the measured Wave 2 cost (CPU-hours and wall-clock);
- the PR link.

The PI decides:

1. **Merge** the Wave 1 PR.
2. **The 3.7 cells:** whether they enter their families.
3. **Coverage flips:** if the smoke test shows any, whether a flipped
   `ci_unreliable` or `coverage_status` is published as the new value
   (the default, since it describes the corrected table) or held for
   review.
4. **Launch Wave 2**, with its specification (written during Wave 1 from
   W1.0's findings) and the measured cost.

## 9. Not in Wave 1

No corpus re-score; no regeneration of tierings, boards, leaderboards,
manifests, or register renderings; no edits to signed register rows,
findings, `docs/paper/`, or observations; no API calls.

## Changelog

### 2026-11-01 — Original publication

Drafted at S168 on amd-tower while Astra reviewed the parent record (gate
R). It specifies Wave 1 from the parent record's § 4 and adds five design
points from a read-only gap analysis (§ 2): downstream "sensitivity"
semantics, gates that read provenance, join provenance in artefacts,
coverage flags derived from the count table, and reproduce-then-replace in
place of E81's guard 1. Not yet approved for launch.
