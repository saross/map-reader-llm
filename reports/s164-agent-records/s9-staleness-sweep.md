# D65 (2): the S9 staleness sweep of evaluations scored before D50 (report only)

> **Last revised**: 2026-10-14 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), a background subagent of the main Session 164
  session (workstream `s9-staleness-sweep`). Every number below was read
  from the run outputs on sapphire, or from the committed files at
  `origin/main` `90294a283`, by the workstream agent on 2026-10-14 before
  it was written here.
- **Date**: 2026-10-14 (UTC).
- **Repository**: `map-reader-llm`, branch `s9-staleness-sweep` from
  `origin/main` at `90294a283`; this branch adds only this record and its
  scripts and records. `origin/main` advanced 16 commits during the sweep
  (to `9664f1094`); none changes a scorer file or any `evaluation.json`
  (they add raw passes and regenerate A-07), and `origin/main` is merged
  into this branch.
- **Ruling**: principal investigator (PI) ruling D65 (2)
  (`planning/pi-decisions-2026-09-20.md`): the restatements are published
  as one pass "after a sweep for S9-type staleness (every evaluation scored
  before D50 that feeds a signed analysis or claim, the K-ladder Phase 2
  cells first), so nothing is restated twice". The finding that prompted
  it is surprise S9 of the S164 re-score
  (`origin/rescore-repaired-gs:reports/s164-agent-records/rescore-repaired-gs.md`
  § 5).
- **Where the runs are**: `~/scratch/s164-s9-sweep-2026-10-14/` on
  sapphire: `wt/` (this branch's worktree), `inventory/`, `runs/` (each
  run's replayed cells, sidecars, logs and progress log), `codes/`
  (`scripts/` of four earlier commits, for attribution), `records/`. The
  drivers and the extracted numbers are committed beside this record in
  [`s9-staleness-sweep-scripts/`](s9-staleness-sweep-scripts/).
- **Guarantees**: no model Application Programming Interface (API) call;
  no committed file under `results/`, `outputs/` or `docs/`, and no
  register row, was changed; nothing restated, re-signed or merged.
  Sapphire's shared checkout was read only: 71 gitignored input
  directories (raw passes the replayed cells score) were copied out of it
  into this branch's worktree, where they stay ignored, after checking each
  cell's per-run detection counts against its committed evaluation. At
  most eight of this workstream's processes ran at a time.

**Conventions.** COMMITTED is the file at `origin/main` `90294a283`. TODAY
is a replay on this branch's code (identical to `origin/main`) with
`MAP_READER_VERIFY_DIRS=fixed`, so verifier legs are read by fixed name and
the re-verified rows of PR #46 play no part. "Pre-D50" means the
evaluation carries no `summary.detection_scope` block, which only the D50
scorer writes; D50's scorer reached `main` with PR #26 (`fefb73f2b`,
2026-10-08) and the re-scored data with PR #29 (`b9b42c79b`, 2026-10-10).
A value **moves** when it is present on both sides and differs; a file
**reproduces** when every compared value is equal, and differences that
are only the `tile_join` label the current scorer records, or keys an
older file format lacks (`f1_point` aliases), are counted as reproducing
and listed as such. F1 is at 20 m unless stated; MCC is tile-level
Matthews correlation coefficient. Paths written `records/…` are under
[`s9-staleness-sweep-scripts/records/`](s9-staleness-sweep-scripts/records/).

## Bottom line

1. **Inventory.** 2,746 committed `evaluation.json` files live outside
   `archive/`; 1,984 were scored before D50 (the latest committed
   2026-10-05), and 1,680 of those feed a signed analysis or a claim row.
   Of those 1,680, **1,480 were recomputed on today's code** and 200 could
   not be (§ 9). In all, 1,255 evaluations were replayed in full (bootstrap
   as recorded), 2,268 for their points (1,556 pre-D50 and the 712
   D50-scored ones), the 24 55-map adapter cells through their corrected-F1
   engine, and seven drifted cells on their inputs as scored.
2. **The K-ladder and Era-2 board cells first.** All 110 K-ladder
   evaluations and all 153 Era-2 board members were replayed in full, twice.
   **Eight move, every one in `results/k-ladder-2026-09-12/`, all by D50**;
   the other 102 K-ladder cells and all 103 board-frame cells reproduce every
   number. Tier E's K = 1, K = 1 carried, K = 3 and K = 5 rungs (and the
   recovery-fix copy of K = 5) rise **+0.0133 to +0.0141 F1**: six or seven
   detections are restored to their origin sheet, giving six more true
   positives and six fewer false positives each; tile MCC is unchanged. The
   Gemini 3.7 GS text ladder's K = 1, K = 1 carried and K = 3 rungs rise
   **+0.0252 to +0.0278 F1**: 27 to 32 detections outside the frame, counted
   as false positives before, are dropped; recall is unchanged. § 3.
3. **S9 is a deferred backlog, not new staleness.** The D50 measurement of
   2026-10-08 listed exactly these eight cells as moved, at the unrounded
   values found today. D57 (4) held them for a "Phase 6" (D57 (4): "ladder
   files wait for (3)", Astra's review), and no PR re-scored them after the
   review closed. No other recomputed pre-D50 evaluation moves by D50 or by
   any later scorer change (§ 5).
4. **Everything else reproduces, or moves for a known reason that is not
   the scorer.** Of the 1,480 recomputed lineage evaluations, **1,457
   reproduce every recomputed value**; 23 move: the eight above, seven pinned
   cells whose detection files changed after scoring (on their inputs as
   scored, today's scorer reproduces them; § 4.4), and **eight 55-map
   extended-reference cells** whose engine summaries predate the engine's
   coincidence de-duplication (W6-E9, `1de559119`, 2026-08-04): one
   reviewer-promoted phantom fewer at every R ≥ 50 m, F1 +0.00008 to
   +0.00009 at 50 m (§ 4.3). D50 moves neither group. Outside the lineage,
   and among the D50-scored cells, the only movers are input drift the D57
   (4) census and D60 (1) already record.
5. **What the eight feed.** Signed analyses `k-ladder-2026-09-12`, the
   Era-2 board (`gs-era2-verified-board-2026-09-10`; seven of the eight are
   members) and `null-exemplar-sensitivity-2026-09-13`. Claim rows R3-14 and
   R6-17 quote a moved value (tier E K = 1's 0.8546, and the 40.6 % and
   +0.0340 built on it); ten more rows name the K-ladder analysis and four
   the board (§ 3.2). The re-score of 2026-10-13 measured the effect on the
   board and the two GS ladders (its §§ 3.1–3.2); it did not reach the 3.7
   GS text ladder or the null-exemplar analysis.
6. **Integrity.** Two independent runs agree on every point and on every
   file apart from timestamps, run paths, and one disclosed artefact of
   method (§ 8). Run B repeated every recomputed cell except 57 staged GS
   cells replayed once in full, each of which reproduces its committed file
   exactly. Kernel bad-page count 0 before and after.

## 1. What was inventoried

`inventory.py` lists every tracked `evaluation.json` outside `archive/` at
`90294a283` and records, per file: the commit that last wrote it, the scorer
commit it records, whether it carries `summary.detection_scope`, whether its
`_metadata.cli_args` can be replayed, whether its detection inputs exist and
carry origin lists, its D57 (4) census disposition, and its lineage. Lineage
follows the register, as the earlier sweeps did: condition
`provenance.source_files` and `eval_path` → registered analyses through
`conditions_compared` (the Era-2 board's own tiering input lists 153 members
where the register row lists 103; the other 50 are K-ladder identity cells,
so the board is attached through its tiering input) → signature status in
`results/run-analyses.json` → claim rows of
`docs/paper/results-claims-inventory-2026-09-12.md` that name the analysis,
the condition, or the cell's path. Cells under an analysis's own
directory (its `output_path`, or that file's directory) are attached to it
as well and marked "by directory"; that is how, for example, the K-ladder's
52 committed-carried cells, which are not registered conditions, reach
`k-ladder-2026-09-12`.

| Class | Cells | In a signed or claim lineage | Recomputed |
|---|---:|---:|---|
| D50-scored (carry `detection_scope`) | 762 | 398 | points of 712; 50 have gitignored inputs (49 of them D57 (4)'s null-exemplar twins) |
| Pre-D50, recipe and inputs present | 1,534 | 1,349 | all (full, points, or both; § 2) |
| Pre-D50, recipe, inputs gitignored | 390 | 295 | 107 lineage cells after staging; not 186 null-exemplar cells, 2 drifted cells, 95 cells outside the lineage |
| Pre-D50, no recipe | 60 | 36 | the 24 55-map adapter cells through their engine; not 12 March `results/retest/` files, 24 pilot files |
| **All** | **2,746** | **2,078** | |

All 1,984 pre-D50 files were last committed by 2026-10-05; the earliest
D50-scored one on 2026-10-09.

## 2. How each group was recomputed

- **Full replay** (`run_sweep.py` driving the D57 (4) wrapper
  `reports/d57-4-rescore-2026-10-09-scripts/replay_cell.py`): the cell's
  recorded `cli_args` exactly (14 buffers, 10,000 BCa resamples, seed 42,
  MCC, tile join, workers), today's scorer, output to scratch; the whole
  `summary` and every `per_run` block compared leaf by leaf
  (`compare.py`). Run for the 213 priority cells (stage 1), the 1,034 GS
  cells of stage 2 in a lineage (927 with inputs present, and 85 + 22 whose
  gitignored raw-pass directories were staged from the shared checkout after
  their per-run detection counts matched the committed evaluation, using the
  scorer's own file resolver), and a sample of eight 55-map cells: 1,255 in
  all.
- **Points replay** (`points_cell.py`): the same scorer and recipe with the
  two interval routines stubbed (`evaluate_detections.bootstrap_ci` and
  `lib_advanced_metrics._bca_ci_from_indices`), so only F1, precision,
  recall, detection counts and the tile confusion and MCC point are
  computed and compared. Run for every replayable cell whose inputs were
  present at inventory time, 2,246 cells (1,534 pre-D50 and the 712
  D50-scored ones), and the 22 staged cells of stage 2 part 3. On the 55-map
  frame a full replay costs minutes per cell (the per-tile table behind
  every buffer's interval, and a BCa jackknife over 8,541 tiles), which is
  why the 209 55-map cells of stage 2 were replayed in full only as an
  eight-cell sample. The stub was checked on nine replays (three with a
  narrower first stub, six with the final one: 55-map cells, two K-ladder
  movers, a board cell); every unrounded point equals an unstubbed replay's
  (`records/stub-check.json`).
- **Engine replay** (`engine_replay.py`): the 24 55-map adapter cells
  carry no `cli_args`; each is a transform of a `summary.json` written by
  `scripts/compute_corrected_f1_multi_buffer.py`, which the D50 commit
  `f93935c18` changed and the D50 measurement left unscored
  ("diagnostics-only"). The engine was re-run from each summary's recorded
  inputs, mode, buffers and seed (50 resamples; points only).
- **Vintage replay** (`vintage_cells.py`, calling D57's Stage A
  `prepare` and `run_cell` unchanged): for the seven pinned pre-D50
  lineage cells whose detection files changed after scoring, the inputs
  as scored were recovered from git (their E82 pins) and scored under the
  pre-D50 tree (`b3c52591d`) and today's code.
- **Attribution** (`attrib_cells.py`): each mover's points replayed under
  the `scripts/` of `b3c52591d` (before D50), `8988f3f17` (D50, PRs #26
  and #27), `7a8a081e1` (PR #33) and `4974c3c2b` (just before the origin
  route), always on today's inputs.

## 3. The K-ladder Phase 2 cells and the Era-2 board members

All 110 K-ladder evaluations (46 `phase2/cells`, 52 `phase2/committed-carried`,
2 `phase2/g37-opmax`, 5 `tier-e/cells`, 4 `board-frame`, 1 `recovery-fix`)
and the 103 Era-2 board-frame cells were replayed in full, twice. With the
50 K-ladder cells the board also lists, that covers all 153 board members.

| Group | Cells | Reproduce every number | Move |
|---|---:|---:|---:|
| K-ladder `results/k-ladder-2026-09-12/` | 110 | 102 (101 differ only by the `tile_join` label) | 8 |
| Era-2 board-frame cells (`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/`) | 103 | 103 (all differ only by the label) | 0 |

### 3.1 The eight movers

F1, precision and recall at 20 m, COMMITTED → TODAY (identical in runs A
and B, full and points). Paths are under `results/k-ladder-2026-09-12/`.
"Restored" and "out of frame" are today's `detection_scope` counts; for
tier E the out-of-frame rows were outside the frame under the old rule as
well (both sides score 459, 469, 427 and 414 rows), so its move is the
restoration alone.

| Cell | Scored (scorer commit) | F1 | Precision | Recall | F1 at 50 m | Tile MCC | Today's scope |
|---|---|---|---|---|---|---|---|
| `tier-e/cells/grid-2026-08-18__g384-ov192-k1-verified-opmax` | 2026-09-12 (`98e54baf6`) | 0.8546 → **0.8680** | 0.8322 → 0.8453 | 0.8782 → 0.8920 | 0.8658 → 0.8792 | 0.8211, unchanged | 7 restored, 23 out of frame |
| `tier-e/cells/grid-2026-08-18__g384-ov192-k1-verified-p0_15-k1` | 2026-09-12 (`98e54baf6`) | 0.8540 → **0.8673** | 0.8230 → 0.8358 | 0.8874 → 0.9011 | 0.8650 → 0.8783 | 0.8079, unchanged | 7 restored, 24 out of frame |
| `tier-e/cells/grid-2026-08-18__g384-ov192-k3-verified-opmax` | 2026-09-12 (`98e54baf6`) | 0.8840 → **0.8979** | 0.8923 → 0.9063 | 0.8759 → 0.8897 | 0.8933 → 0.9072 | 0.8167, unchanged | 6 restored, 23 out of frame |
| `tier-e/cells/grid-2026-08-18__g384-ov192-k5-verified-opmax` | 2026-09-12 (`98e54baf6`) | 0.8905 → **0.9046** | 0.9130 → 0.9275 | 0.8690 → 0.8828 | 0.8999 → 0.9140 | 0.8139, unchanged | 7 restored, 21 out of frame |
| `recovery-fix-2026-09-13/reproduced-k5-evaluation` | 2026-09-13 (`5a56ad248`) | 0.8905 → **0.9046** | 0.9130 → 0.9275 | 0.8690 → 0.8828 | 0.8999 → 0.9140 | 0.8139, unchanged | 7 restored, 21 out of frame |
| `phase2/cells/gemini37-screen-2026-08-28__g37-text-k1-verified-carried-p0_10-k1` | 2026-09-12 (`f724b7a10`) | 0.8338 → **0.8616** | 0.7419 → 0.7871 | 0.9517, unchanged | 0.8520 → 0.8803 | 0.1422 → withheld | 32 out of frame |
| `phase2/cells/gemini37-screen-2026-08-28__g37-text-k1-verified-opmax` | 2026-09-12 (`f724b7a10`) | 0.8495 → **0.8747** | 0.7928 → 0.8379 | 0.9149, unchanged | 0.8709 → 0.8967 | 0.1337 → withheld | 27 out of frame |
| `phase2/cells/gemini37-screen-2026-08-28__g37-text-k3-verified-opmax` | 2026-09-13 (`987534c03`) | 0.8860 → **0.9135** | 0.8323 → 0.8822 | 0.9471, unchanged | 0.9011 → 0.9290 | none recorded, withheld | 28 out of frame |

The three Gemini 3.7 rungs' committed tile MCC (0.1422 and 0.1337; K = 3
recorded none) came from the name-based tile join that the tile-join
invariant (`7ba47b63b`, 2026-09-12) now refuses; today they are withheld
with their intervals, as the census found under the pre-D50 scorer too.
That change is not D50. Tier E's tile MCC does not move. The
recovery-fix `reproduced-k5-evaluation` scores the same detection set as
tier E's K = 5 and moves identically.

### 3.2 What they feed

| Analysis (signed) | Signed | Movers it reads | How |
|---|---|---|---|
| `k-ladder-2026-09-12` | 2026-09-13 | all eight | conditions (seven), directory (the recovery-fix copy) |
| `gs-era2-verified-board-2026-09-10` | re-signed 2026-09-16 | seven (not the recovery-fix copy) | tiering input; the three 3.7 rungs are withheld from its tiering by the tile-join invariant |
| `null-exemplar-sensitivity-2026-09-13` | 2026-09-16 | seven | conditions; its reduced-frame twins of these cells were regenerated under D50 in D57 (4) Phase 2, the full-frame ones not (the S3 record's flag 1) |

Claim rows: **R3-14** quotes tier E's K = 1 F1 (0.8546) and the "40.6 %"
built on it; **R6-17** quotes the 40.6 % and the +0.0340 (0.8886 − 0.8546).
The re-score of 2026-10-13 already restates both on today's code (60.3 %,
+0.0262 with the repaired rows; its § 3.2). Rows that name
`k-ladder-2026-09-12` without quoting a moved value: R1b-17, R3-10 to
R3-13, R3-15, R6-11, R6-14, R6-16, R6-18. Rows that name the board: R0-05,
R4-17, R4-18, R4-28. No row names the null-exemplar analysis. Committed
files that carry the eight cells' old unrounded F1 values
(`0.854586…`, `0.890459…`, `0.853982…`, `0.833836…`):
`results/k-ladder-2026-09-12/mcb/summary.json`,
`…/mcb/tier-e/k-ladder-tier-e-2026-09-12_b20_m1.json`,
`…/tier-e/ladder.json`, `…/tier-e/tiering/tiering_20m.json`, and the
board's `tiering_20m.json`; the K-ladder's `phase2/scores.json`,
`phase2/ladders.json`, `phase2/ladder-tables.md`, `tier-e/scores.json`,
`findings.md` and `recovery-fix-2026-09-13/` quote them at four decimals.

### 3.3 Why they were stale

- **2026-10-07**: the frames blast-radius measurement's replica rule
  predicted no move for tier E (its `cells.csv` gives off = on = 0.8546 for
  K = 1): the replica did not restore origins.
- **2026-10-08**: the D50 measurement with the real scorer (`8988f3f17`)
  listed all eight as moved, at the values this sweep finds
  (`reports/scorer-frames-d50-d51-2026-10-08-scripts/out/summary/moved_new.csv`,
  column `new_f1_20`: 0.868008… for tier E K = 1, 0.861602… for the 3.7
  K = 1 carried rung). D50's own ruling text names "tier E's and h13's six
  cells each to be re-scored under the rule" and "the 3.7 GS ladder's K = 1,
  K = 3 and carried rungs".
- **2026-10-09**: D57 (4) Phase 2 regenerated 737 moved cells and held
  "8 ladder (7 registered)" for Phase 6
  (`reports/d57-4-rescore-2026-10-09-scripts/d57_common.py`,
  `LADDER_PREFIXES`), pending D57 (3)'s second opinion.
- **2026-10-11 to 2026-10-13**: Astra accepted the D51 guard (PR #30 merged
  2026-10-13, code only); no PR re-scored the held cells, and no K-ladder or
  board result file has changed since 2026-10-08 apart from a pricing
  restamp (`8e343e6e7`).

Attribution (§ 5) confirms it: each of the eight first moves at
`8988f3f17` and is unchanged from there through PR #33 and the origin-route
PRs to today.

## 4. The rest of the corpus

### 4.1 Full replays of the GS cells in a signed or claim lineage

Stage 2 replayed in full the 1,034 other pre-D50 GS evaluations in a
lineage. Run A covered all of them; run B covered 408 (all 100 of part 1,
and in part 2 every third cell plus the four whose run A did not reproduce
and which the sample missed; § 8). **1,027 reproduce every number** (1,025
differ only by the `tile_join` label, 2 are identical). The seven that move
are the pinned drift cells of § 4.4. By directory: `results/rescore-2026-06-07/phase3`
495, `results/leaderboard/era2` (the board's opmax and G2 cells) 107,
`results/uplift-supplement/verifier-pairing` 68 and `k1-gapfill` 66,
`results/rescore-2026-06-07/phase3c` 45, `results/paper-eval/phase2` 36,
`results/verifier-robustness` 33, `results/rescore-2026-05-31` 80 in nine
directories, `results/paper-eval/n1` 20, `results/h8-v2` 14,
`results/rescore-2026-09-07` 9, the registered grid (8) and stride (8)
conditions, `results/rescore-2026-06-05` 8, `results/flash35-2x2` 7,
`results/era1-pv-stage-d` 6, `results/h12-v2` 6, `results/h10` 4, and 14 cells
of the Gemini 3.7 and 3.8 screens, Image-B, the 3.7 image arms, the fourth
cell's GS leg, H7 escalation, `rescore-2026-06-08` and the Era-2
extended-buffer sweep. The registered GS conditions downstream of the
wrong-sheet legs reproduce here because legs are read by fixed name; their
repaired-row moves are PR #46's.

### 4.2 Points of every replayable cell

The points scan replayed 2,268 cells twice. Among the 1,556 pre-D50 ones,
the only movers are the eight K-ladder cells, the seven pinned drift cells
(§ 4.4), and 13 drifted cells outside any lineage; the 209 55-map cells of
stage 2 all reproduce their points, and so do the eight of them replayed in
full, intervals included. Among the 712 D50-scored cells (re-scored by PR #29
at `494b5a7af`, or later), **687 reproduce every point on today's code** and
25 move: exactly the 25 drifted or pinned cells of D60 (1), whose Stage A
scored their inputs as scored and whose Stage B on today's inputs is pending.
So the scorer changes after `494b5a7af` (PR #33's sheet rule, reduced
frames and mixed cuts) move no committed point among the cells replayed;
the null-exemplar reduced-frame cells, which PR #33 could move, were not
replayed (§ 9).

### 4.3 The 55-map corrected-F1 engine cells

The engine was re-run for all 24 adapter cells (two runs). Sixteen
reproduce every point at every buffer: the eight standardised-reference
cells (`results/55maps-standardised-ref-2026-08-14/`), the three Gemini 3.7
55-map primaries (arm 1, arm 2, the fourth cell) and the five stride55
primaries, oracles and N = 5 companion. Eight move: the extended-reference
cells of `results/55maps-extended-gt-2026-06-07/` (IM-k3, T03-k3, T03-k4,
TH7-k3, TH7-k4, TM-k3, TM-k4, TM-n10-k5). Each has exactly one
reviewer-promoted phantom fewer at every R ≥ 50 m (415 → 414 at 50 m), so one
false negative fewer; every count at R ≤ 45 m and the tile confusion and MCC
reproduce.

| Cell (`results/55maps-extended-gt-2026-06-07/`) | Engine commit | FN at 50 m | F1 at 50 m, COMMITTED → TODAY |
|---|---|---|---|
| `IM-k3` | `bb7d5279e` | 1,231 → 1,230 | 0.798699 → 0.798780 |
| `T03-k3` | `bb7d5279e` | 895 → 894 | 0.847606 → 0.847690 |
| `T03-k4` | `bb7d5279e` | 1,186 → 1,185 | 0.835874 → 0.835962 |
| `TH7-k3` | `bb7d5279e` | 971 → 970 | 0.842465 → 0.842550 |
| `TH7-k4` | `bb7d5279e` | 1,360 → 1,359 | 0.815228 → 0.815315 |
| `TM-k3` | `bb7d5279e` | 1,325 → 1,324 | 0.812712 → 0.812798 |
| `TM-k4` | `bb7d5279e` | 1,627 → 1,626 | 0.783071 → 0.783158 |
| `TM-n10-k5` | `7aa28475b` | 1,214 → 1,213 | 0.829028 → 0.829115 |

**Cause: the engine's coincidence de-duplication, not D50.** Today's
engine with `--dedup-tolerance-m 0` reproduces IM-k3 exactly, and the
pre-D50 tree (`b3c52591d`) gives today's moved values; the eight share one
extended reference, so one cell stands for all. The summaries were written
at `bb7d5279e` and `7aa28475b` (June); the de-duplication arrived with
`1de559119` (2026-08-04, "coincidence de-dup in build_extended_gt — W6-E9
durable fix"). They feed the signed `tile-level-f1`,
`uplift-supplement-flatten` and `verifier-uplift-pairing` (the flatten's
`conditions.csv` and `conditions-by-buffer.csv`, and `verifier-uplift.csv`,
carry these cells' 50 m values, for example `0.79869…` for IM-k3). Claim
rows R0-04 and R4-15 reach them only by naming `tile-level-f1` and quote
none of their values.

### 4.4 Drifted inputs

Every other evaluation whose points move has a detection file (or a
reference) that changed after it was scored. All were known before this
sweep, and none moves because of the scorer:

- **Seven pinned pre-D50 cells in a signed lineage**, all feeding
  `uplift-supplement-flatten`: the e47 propose-brief `run_4` and the
  n1-outstanding Pro HIGH T 0 image and text `run_1` to `run_3`
  (`results/rescore-2026-05-31/`). Each carries an E82 input pin
  (`52b0215a6`, `c3852ebad`); today's detection files hold 22 to 84 more
  rows. On their inputs as scored, recovered from the pins, the pre-D50 tree
  reproduces all seven committed files and today's code gives the same F1 at
  every buffer and the same MCC (`records/vintage-A.json`). On today's
  inputs they move by up to 0.0368 F1, which is drift, not scorer.
- **The 25 drifted or pinned cells of D60 (1)** (D50-scored on their
  as-scored inputs as Stage A, PRs #29 and #36): on today's inputs they move,
  as D60 (1) expects; their Stage B on today's inputs is already ruled into
  Phase 5.
- **Nine unregistered `outputs/55maps-*-generalisation` evaluations** (no
  lineage): F1 ±0.0001 to 0.0002 and MCC +0.0003 to +0.0004 on an unchanged
  detection count; the census's vintage replays reproduce them, the drift
  being in the 55-map reviewed reference.
- **Four unregistered `results/paper-eval/{mcc,n1}` Pro medium T 0 cells**
  (no lineage): the census's input-drift class, not replayed on vintage
  inputs here.

Two lineage cells could not be recomputed at all for the same reason:
`results/paper-eval/n1/384px-14buf-mcc/pro-{image,text}-high-t-0-0`
(feeding the flatten) score raw-pass directories whose files changed and
which have no git history; the census records them as pinned drift.

## 5. Cause attribution

Points of each K-ladder mover under each tree, on today's inputs (F1 at
20 m; "=" where the tree reproduces the committed F1, P and R; scope
counts from that tree's `detection_scope`, which the pre-D50 tree does not
write). `records/attrib.json`.

| Cell | `b3c52591d` (before D50) | `8988f3f17` (D50) | `7a8a081e1` (PR #33) | `4974c3c2b` (before the origin route) | today |
|---|---|---|---|---|---|
| 3.7 text K = 1 carried | = (MCC withheld) | 0.8616, 32 out of frame | 0.8616 | 0.8616 | 0.8616 |
| 3.7 text K = 1 opmax | = (MCC withheld) | 0.8747, 27 out of frame | 0.8747 | 0.8747 | 0.8747 |
| 3.7 text K = 3 opmax | = | 0.9135, 28 out of frame | 0.9135 | 0.9135 | 0.9135 |
| tier E K = 1 opmax | = | 0.8680, 7 restored | 0.8680 | 0.8680 | 0.8680 |
| tier E K = 1 carried | = | 0.8673, 7 restored | 0.8673 | 0.8673 | 0.8673 |
| tier E K = 3 opmax | = | 0.8979, 6 restored | 0.8979 | 0.8979 | 0.8979 |
| tier E K = 5 opmax | = | 0.9046, 7 restored | 0.9046 | 0.9046 | 0.9046 |
| recovery-fix K = 5 | = | 0.9046, 7 restored | 0.9046 | 0.9046 | 0.9046 |

"MCC withheld": the pre-D50 tree already refuses the two rungs' tile join
(`7ba47b63b` precedes it), so it reproduces their F1, P and R but not their
recorded MCC; the census found the same. For the 55-map extended-reference
cells the attribution is § 4.3 (de-duplication, `1de559119`); for the drift
cells, § 4.4 (inputs).

## 6. What reproduces

Every live evaluation, by group (run A; run B agrees, § 8). "Reproduce"
means every recomputed value equals the committed one (label and format
differences aside). Per cell: `records/coverage.csv`; movers in full:
`records/movers.json`; counts: `records/counts.json`.

| Group | Cells | Recomputed by | Reproduce | Move | Why they move |
|---|---:|---|---:|---:|---|
| K-ladder evaluations | 110 | full ×2, points ×2 | 102 | 8 | D50 (§ 3) |
| Era-2 board-frame cells | 103 | full ×2, points ×2 | 103 | 0 | — |
| Other pre-D50 GS cells in a lineage | 1,034 | full (408 twice); points ×2 for 949 | 1,027 | 7 | input drift, pinned (§ 4.4) |
| Pre-D50 55-map cells in a lineage | 209 | points ×2; 8 also full ×2 | 209 | 0 | — |
| Pre-D50 55-map adapter cells in a lineage | 24 | engine ×2 | 16 | 8 | engine de-duplication, before D50 (§ 4.3) |
| Pre-D50 cells outside any lineage | 185 | points ×2 | 172 | 13 | input drift (census) |
| D50-scored cells | 712 | points ×2 | 687 | 25 | input drift (D60 (1)) |
| Not recomputed | 369 | — | — | — | § 9 (200 pre-D50 in a lineage, 119 outside, 50 D50-scored) |
| **All** | **2,746** | | | | |

In a lineage, then: 1,480 recomputed, 1,457 reproduce, 23 move (8 by D50,
8 by the pre-D50 engine fix, 7 by input drift).

## 7. Surprises

Flagged, not explained away.

- **T1. S9 was a known backlog, not an undetected class.** The eight
  movers are exactly the "ladder (8)" group the D50 measurement of
  2026-10-08 found and D57 (4) deferred to a Phase 6 that no later PR or
  ledger entry picked up. Nothing else among the 1,665 pre-D50 evaluations
  recomputed moves by D50 or a later scorer change. What failed was the tracking of a deferral, not the
  re-score's coverage.
- **T2. The Gemini 3.7 GS text ladder moves twice as far as tier E**, and
  S9 did not name it: +0.0252 to +0.0278 F1 against +0.0133 to +0.0141.
  These three rungs are withheld from the Era-2 board's tiering (the
  tile-join invariant), so the 2026-10-13 re-score saw no effect on the
  board, but they are rungs of `k-ladder-2026-09-12` and cells of the
  null-exemplar analysis. Their committed F1 (0.8338, 0.8495, 0.8860) is
  neither today's unclipped value (0.8616, 0.8747, 0.9135) nor D51's clipped
  reading (K = 1 0.8682, K = 3 0.9073; D51), so the ladder's committed tables
  carry a third set of numbers.
- **T3. Staleness older than D50 sits in signed lineage.** The eight
  55-map extended-reference engine summaries (June) predate the engine's
  de-duplication fix of 2026-08-04 and were never re-run; they move in the
  fifth decimal (one phantom). They feed `tile-level-f1`, the flatten and
  `verifier-uplift-pairing`. Small, but the same class as S9: a fix that
  landed after a committed file and never reached it.
- **T4. The frames blast-radius replica missed origin restoration.** Its
  `cells.csv` (2026-10-07) predicted no move for tier E (off = on = 0.8546);
  the real D50 scorer a day later did. Any reading that still relies on that
  replica's "unchanged" verdicts should be checked against `moved_new.csv`
  instead.

## 8. Integrity

Run A and run B are fresh processes writing to separate directories;
`cmp_runs.py` compares every file after removing only `timestamp`,
`_metadata.generated_at_utc`, the run's own root path and the Markdown
`**Generated**` line, and compares the unrounded sidecar points exactly
(`records/integrity-*.json`).

| Replay | Cells (A / B) | Files compared | Byte-identical | Identical after normalising | Differ | Sidecar points equal |
|---|---|---:|---:|---:|---:|---|
| Stage 1, full (K-ladder, board) | 213 / 213 | 639 | 213 | 426 | 0 | 213 of 213 |
| Stage 2 part 1, full | 100 / 100 | 300 | 100 | 200 | 0 | 100 of 100 |
| Stage 2 part 2, full | 912 / 308 | 924 | 308 | 616 | 0 | 308 of 308 |
| Stage 2 part 3, full | 22 / 1 | 3 | 1 | 2 | 0 | 1 of 1 |
| 55-map sample, full | 8 / 8 | 24 | 8 | 16 | 0 | 8 of 8 |
| Points scan | 2,246 / 2,246 | 6,738 | 2,243 | 4,486 | 9 | 2,246 of 2,246 |
| Part 3 points | 22 / 22 | 66 | 22 | 44 | 0 | 22 of 22 |
| Engine (summaries' `results`) | 24 / 24 | 24 | — | 24 equal | 0 | — |

- **The nine points-scan files that differ** are three 55-map cells
  (`results/55map-final-board-r2-2026-09-06/cells/ARM1-N3-oracle`,
  `ARM1-N3-mcc-oracle`, `ARM1-N3-mcc-oracle-k3`) that ran in the five
  minutes when the interval stub was being widened: run A had the narrower
  stub, run B the full one, so their stubbed interval fields differ by
  construction while every point is equal. The first 33 cells of both runs
  ran before any stub; their points equal the stubbed replays' too
  (`records/stub-check.json`).
- **Single-run replays.** 57 staged GS cells (30 `rescore-2026-06-07/phase3c`,
  24 `paper-eval/phase2`, 3 others) were replayed once, in full, outside the
  part-2 sample and before the points scan could reach them; all 57
  reproduce their committed files exactly. The vintage replays and the
  attribution ran once: the vintage OLD replays reproduce all seven committed files exactly, and
  an exact reproduction of a committed file cannot come from a memory fault
  (the D57 (4) census's argument); the attribution's D50-tree values equal
  the D50 measurement's of 2026-10-08 and today's two runs.
- **Kernel memory errors** (sapphire has no error-correcting memory):
  `journalctl -k -b | grep -c "Bad page state"` read 0 at 00:39:56 UTC
  before the first run and 0 at 05:48:09 UTC after the last; every run's
  own tripwire read 0 → 0 (`records/bad-page-*.txt`, each run's
  `progress.log`).
- **Part 2's run A ran as two processes** at the end (the second working
  through the last 28 cells from the back, `runs/s2p2-A2`, to use idle
  slots); 12 cells ran in both, and every cell is covered. Part 2's run B
  is every third cell (304) plus the four non-reproducing cells the sample
  missed. Part 3's run B was stopped after one cell, in favour of a points
  run B over all 22 (§ 2); its one full cell equals run A's.
- **Process cap.** At most eight of this workstream's processes ran at a
  time, except once: the attribution launched while eight were running (a
  wait that timed out before its condition held); it was stopped within
  about a minute, its partial output discarded, and it was re-run once a
  slot was free.

## 9. What was not done

- **No restatement.** No committed file, document, register row or
  signature was touched; every "today" value lives in scratch and in
  `s9-staleness-sweep-scripts/records/`.
- **200 pre-D50 lineage evaluations were not recomputed**, each for a
  stated reason: the 186 null-exemplar reduced-frame cells (inputs are
  gitignored filter outputs; that analysis's `--stage filter` rewrites a
  tracked manifest; D65 (5) re-runs the analysis in full after the board
  restatement, and PR #33's reduced-frame change makes movement there
  plausible); the 12 March `results/retest/phase*-evaluation.json` files
  (no recipe; claim rows R2-11 and R3-09; the D63 record documents why
  they do not reproduce); and the two drifted Pro HIGH T 0 n1 cells of
  § 4.4.
- **Not in any lineage, not recomputed**: 78 pre-D50 cells whose
  gitignored inputs were not staged, 13 with absent inputs, 4 with drifted
  directory inputs, 24 verifier-T-pilot files without a recipe, and 50
  D50-scored cells with gitignored inputs (49 of them null-exemplar twins
  D57 (4) regenerated).
- **55-map cells in full.** The 209 55-map cells of stage 2 were replayed
  for their points (twice) and eight of them in full (twice); their other
  intervals were not.
- **Run B of stage 2 part 2** covered every third cell plus every cell
  whose run A did not reproduce the committed file (§ 8); the points of
  every other cell were replayed twice, except 57 staged cells replayed
  once in full (each reproduces its committed file exactly).
- **Generator outputs.** Sweeps, ladder tables, MCB and tiering files,
  boards and the uplift CSVs were not regenerated; § 3.2 names the K-ladder
  and board files that carry the eight movers' old values. Whether any
  sweep's argmax moves (the S2 mechanism of the 2026-10-13 re-score) was
  not swept; that is a generator question, not an evaluation one.
- **Per-tile tables.** Only two are committed
  (`results/grid-2026-08-18/per_tile_counts.json`, inside PR #42's pending
  restatement; `results/h13-overlap-2026-08-18/per_tile_counts.json`, which
  PR #41 reproduced byte for byte). Every other per-tile table is rebuilt at
  tiering time from the detection files.

## 10. For the PI

1. **Add the eight K-ladder cells to the restatement pass.** They are the
   only scorer-stale evaluations found. Regenerating them moves
   `k-ladder-2026-09-12` (tier E's ladder, the 3.7 GS text ladder, the MCB
   sets), the Era-2 board's tiering (already measured on 2026-10-13), and
   the null-exemplar analysis (re-run last under D65 (5)), and it restates
   R3-14 and R6-17. One choice: whether the 3.7 GS text rungs' cells are
   restated unclipped (as their recipes give) or on D51's clipped basis,
   which PR #30 made the reported basis of the ladder tables (in code; the
   committed tables have not been regenerated since).
2. **The eight 55-map extended-reference cells** (§ 4.3): regenerate them
   with today's engine in the same pass (fifth-decimal moves in the flatten
   and the uplift pairing), or record that they keep the pre-W6-E9 engine.
3. **Drift** (§ 4.4) needs no new decision: D60 (1)'s Stage B covers the 25,
   and the seven pinned flatten inputs are scored on purpose on their E82
   vintages.

## Changelog

### 2026-10-14 — Original publication

First version: the inventory of 2,746 live evaluations; the full, points,
engine and vintage replays on sapphire of every pre-D50 evaluation in a
signed or claim lineage that could be replayed (1,480 of 1,680), most of them
twice; and the attribution of every mover. No committed output changed.
