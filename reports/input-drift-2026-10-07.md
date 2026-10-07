# Input drift behind the frames check's reproduction failures, 2026-10-07

> **Last revised**: 2026-10-07 (original publication). See [§ Changelog](#changelog) for revision history.

**Status: FOR THE PI.** Read-only provenance trace of the 54 cells that the frames
blast-radius measurement could not reproduce because their detection inputs had
changed (`reports/frames-blast-radius-2026-10-07.md` § 3.1, lines 146–150; § 7, lines
541–542). No API call was made, and no detection or evaluation file was written, moved
or deleted. Git work ran locally; every re-score ran on sapphire. The scripts and their
outputs are beside this file in `input-drift-2026-10-07-scripts/` (outputs under
`out/`).

Abbreviations, first use: PI is the principal investigator; GS is the four-sheet gold
standard; F1 is the point-matched F1 score, and P and R are precision and recall; MCC is
the tile-level Matthews correlation coefficient; OFF is the project's scorer unchanged,
as the frames report uses the term; WBF is weighted boxes fusion. E*n* names an erratum
in `docs/methodology/preregistration/protocol-errata.md`, and D*n* a defect in
`reports/defect-register-2026-08-18.md`. A **pinned** evaluation is one that the E82
corpus re-emission scored against a frozen older commit of its inputs, recorded in
`_metadata.e82_input_vintage`. The **scored vintage** is the commit of an input that a
committed evaluation actually scored.

## 1. Headline

1. **Nothing was overwritten by a different run.** Every one of the 54 rows (42 live, 12
   archived) traces to a committed, documented campaign that rewrote a tracked detection
   file after the evaluation's scored vintage. For four archived 55-map rows the 55-map
   reference changed instead. There are five campaigns (§ 3). The largest is the E71
   dead-tile rerun of 2026-07-30 (`99ae28ec4`, `d01ea4412`) and the consensus sets
   rebuilt from its recovered passes (`f6116cba0`, `77bb342b4`, `185681674`,
   `e01b8617a`, `e7ebc1695`). It accounts for 40 of the 54 rows and 38 of the 42 live
   ones.
2. **Why the evaluations disagree with today's files.** All 42 live evaluations were
   last written by the E82 re-emission (`generated_at_utc` 2026-08-20T13:11Z to
   2026-08-22T13:36Z; committed in `43ea31b26`). For 29 of them the inputs had already
   been recovered, so E82's input-vintage rule pinned the pre-recovery commit, as its
   contract requires (`planning/e82-corpus-reemission-2026-08-20.md:93`, D40). The
   other 13 read the consensus sets that were current on 2026-08-20/21, and those sets
   were rebuilt on 2026-09-08. The frames classifier compared each committed count with
   today's file. It did not read the pins (`classify_reproduction.py` checks
   `blob_hashes` and counts only).
3. **Verified, not inferred.** Each cell's inputs were rebuilt at the scored vintage
   from git, and the frames OFF scorer was re-run on them (`rescore_scored_vintage.py`).
   **53 of 54 reproduce** the committed F1, P, R and MCC to 1e-4 at every committed
   buffer. The 54th is the archived "as read" copy of the Gemini 3.7 K = 3 rung. Its F1,
   P and R reproduce; its committed MCC 0.1337 predates the tile-join invariant and is
   refused today, the frames report's "MCC now refused" class.
4. **The frames fix moves none of the 42 live committed numbers.** On the scored vintage
   every live cell has **0 out-of-frame detections**, as on today's files. The only scored
   vintage that has any is the archived K = 3 copy: 27, the defect the frames report
   measures on the live rung.
5. **Registered conditions: nine, as the frames report says.** They are the six
   `n1-outstanding-384` Pro HIGH T 0 single passes, their two three-run baselines, and
   `e47-propose-brief::single-pass-run_4`. Each is a pinned record that PI ruling 3a
   (2026-09-07) keeps on purpose. Each carries an `input_vintage` stamp in
   `results/run-conditions.json` and has a `-post-e71` twin scored on the recovered
   file. **Today's file re-scores equal the twins to 1e-4** at F1@20, F1@50 and MCC
   (§ 5.1). Re-pointing would move F1@20 by −0.0079 to +0.0225 and MCC by +0.0054 to
   +0.0435. Those moves are already on the register, beside the pinned rows, and
   disclosed in the E71 rider of 2026-09-07 (`protocol-errata.md:3338–3360`).
   **Correction to the frames report's wording**: the drift in these nine is E71's, not
   E57's. E57 concerns their model of record: these "Pro" pools were dispatched as Flash
   (`run-conditions.json:317`, `:323`).
6. **Recommendation.** Withdraw the frames § 3.1 "surprising" flag for these cells. The
   state is the disclosed E71/D40 one, and this report verifies it to reproduce. Keep the
   committed numbers as the historical record, which is what ruling 3a says. The paper
   should rely on the post-recovery numbers, which are already registered (§ 4, § 5).
   For any claim about a Pro model, it should rely on `n1-pro-rerun-384` (E57). Make the
   next corpus-wide reproduction gate vintage-aware, or these cells will be raised
   again (§ 7).

## 2. Method

- **`trace_input_drift.py`** (sapphire; output `out/trace.json`, `repo_head`
  `886f60031`). For each of the 54 rows of
  `frames-blast-radius-2026-10-07-scripts/out/summary/reproduction_failures.csv` in the
  categories `input-drift-count`, `input-drift-blob` and `input-newer-than-eval`, it
  takes the detection files **verbatim from the frames re-score row** (`detections` in
  `evaluations.jsonl` / `evaluations_rerun.jsonl` on sapphire). The resolution of
  directory-recorded multi-run cells is therefore exactly the one
  `rescore_evaluations.py` used. For each file it records `git ls-files`,
  `git check-ignore`, size, modification time, the feature count on disk, whether the
  working tree matches `HEAD`, and the full `git log --follow` with the feature count at
  every commit. For each evaluation it records its `git log --follow`,
  `generated_at_utc`, the E82 pins, and every register row that names it.
- **`rescore_scored_vintage.py`** (sapphire; output `out/scored_vintage.json`,
  `repo_head` `d93678303`). Rebuilds every input at its scored vintage with `git show`
  into scratch outside the checkout. The vintage is the E82 pin where one exists. If
  not, detections take the newest commit whose count equals the committed count, and
  references and bounds take the last commit at or before `generated_at_utc`. The script
  then re-runs `blast_lib.score_point` at every committed buffer and
  `blast_lib.geometric_detection_scope` on the scored vintage.
- **`summarise_drift.py`** (local) renders §§ 4–5 from the two outputs, so no number
  in those tables is transcribed by hand.
- **Checkout drift.** Sapphire's `HEAD` moved during the work because another session
  is committing. `git diff --stat 7ce21497d 9f19110b0` over every path read here (the
  three registers, `outputs/h11`, `outputs/h12-v2`, the 55-map outputs, the evaluation
  trees, the three archive trees, `inputs/vectors`) is empty, so no input differs
  between the checkouts used.
- **What the inputs are.** All 33 distinct detection files are git-tracked, none is
  ignored, and all 33 match `HEAD` on sapphire (`out/trace.json` → `files[].tracked`,
  `ignored`, `matches_head`). Their modification times on sapphire (2026-04-27T01:17Z to
  2026-09-13T09:26Z) are checkout times and add nothing to the git history. The
  GS reference (`cfc10c133`) and the bounds files have not changed since before any of
  these evaluations. The detection file is the only input that changed in groups A, B,
  C and E.

## 3. Groups by cause

| Group | Rows live / archived | What rewrote the input | Scored vintage | Register treatment | What the paper should rely on | Scored input recoverable from |
|---|---|---|---|---|---|---|
| **A. E71 dead-tile rerun, single passes** | 13 / 2 | `99ae28ec4` (2026-07-30 15:25 +1000, "E71 dead-tile rerun executed — 255/288 recovered") and deep sweeps `d01ea4412` (18:27 the same day). Detections were added on recovered tiles, so counts rose. | `c3852ebad` (per pass), `1f443fd69` (directory pin; the files there are the `c3852ebad` content), `52b0215a6` (e47 `run_4`) | 9 registered pinned records with `input_vintage` (`run-conditions.json:237, :656, :690, :724, :758, :792, :826, :920, :966`), 4 waived (`_ignored_evals`), 2 archived (2026-05-31, `d18b963d1`) | The `-post-e71` twins (`results/rescore-2026-09-07/`, `26cc430ad`), which equal today's file (§ 5.1). The pinned rows stay as the record of what signed analyses consumed (ruling 3a). | git, plus byte-identical copies in `archive/pre-recovery-2026-07-30/` (7 files checked) |
| **B. E71 downstream consensus rebuilds** | 25 / 0 | pv-diag t0.0: `f6116cba0`, `77bb342b4` (2026-07-30). n1-outstanding: `185681674`; e47: `e01b8617a`; h12-v2: `e7ebc1695` (all 2026-09-08). Counts rose, except e47's: they fell because the April sweep had double-read `run_5` (D6 class). | pv-diag: `2e8cc6481` / `09fe46a7f` (pinned); n1 and e47: `1f443fd69`; h12-v2: `2e84d4a65` (unpinned, read before the rebuild) | 11 pre-recovery records behind re-pointed rows (`_pre_recovery_eval_path`, `run-conditions.json:119–175, :464–534`); 12 waived; **2 listed nowhere** (§ 6.2) | The re-pointed rows under `results/recovery-reeval-2026-07-30/` and `-2026-09-08/`, all 14 of which equal today's file (§ 5.2). The e47 committed numbers also carry a D6-class double read of `run_5` (4,491 vs 4,146 clusters, `run-conditions.json:120`), so they are not a usable baseline even historically. For h12-v2, the registered greedy t = 4 and WBF vote ≥ 4 sets are feature-identical before and after (`e7ebc1695`; `reports/recovery-consistency-audit-2026-09-08.md:257`, not re-checked here). Only the waived greedy t = 1 and WBF all-candidate cells drift. | git, plus byte-identical copies in `archive/pre-recovery-2026-07-30/consensus__*` (6) and `archive/pre-recovery-2026-09-08/` (13) |
| **C. E57/Obs 338 Pro-medium `run_1` recovery** | 4 / 2 | `c07c57766` (2026-06-03, "recover pv-diag medium-t-0-0 run_1 failures -> complete (E57/Obs338)"); 25 and 23 failed tiles were merged into `run_1` in place | `3d22184d6` (pinned) | 4 waived (`pv-diag-384`), 2 archived (2026-06-02, `ea76bf4fc`, the day before the recovery) | The registered three-run siblings `pv-diag-384::baseline-pro-{image,text}-medium-t-0-0`, whose committed per-run counts (587/544/544 and 446/454/456) already read the recovered `run_1` | git only (`3d22184d6`); no working-tree copy |
| **D. 55-map verified-set rebuilds and reference edits** | 0 / 7 | Verified sets rebuilt in the 2026-05-02/03 recovery commits (`8965d2365`, `8699f456b`, `d7f85978d`, `c1ea6df3c`). `student-mounds-55maps-reviewed.geojson` gained two mounds (`baf1497a7`, `2e075eb99`, 2026-05-03). The four `input-newer-than-eval` rows are reference-only. | Detections at `4c147af65`, `4e5c5e5a3`, `f0f7158e7`, `8699f456b`, `d7f85978d`, `c1ea6df3c`, `548604d95`; reference at `dea1155fa` or `baf1497a7` | Archived 2026-06-07 (`da2cf355f`); unreferenced by any register (`archive/55maps-superseded-gt-evals/README.md:19`) | Neither: superseded by the Track 1 / Track 2 references | git only |
| **E. Recovery-fragment-drop fix, 3.7 K = 3** | 0 / 1 | `987534c03` (2026-09-13) installed the rebuilt K = 3 set: 494 → 495 | `326181bcd` (494) | Archived "as read" predecessor of the live cell | The live cell (0.8860 committed; `conditions-manifest.json` now 0.886 / 495). Under the frames fix it becomes 0.9135, pending the PI's ruling. | `archive/superseded-consensus-2026-09-13/recovery-fragment-drop/materialised-as-read-2026-09-13/` (blob `dc0c0b5d8…` = `326181bcd` = the evaluation's recorded `blob_hashes`) |

Archive byte-identity was checked as
`git hash-object <archive copy>` = `git rev-parse <scored commit>:<path>`. That covers
the 6 `n1-outstanding` passes and e47 `run_4` against `c3852ebad` / `52b0215a6`, the 6
pv-diag t0.0 consensus sets against `2e8cc6481` / `09fe46a7f`, the 11 n1 and e47
consensus sets against `1f443fd69`, and the 2 h12-v2 sets against `2e84d4a65`.

## 4. Every row

Generated by `summarise_drift.py` from `out/trace.json` and `out/scored_vintage.json`.
*Register* is how `results/run-conditions.json` treats the evaluation: a registered
condition's source, waived (listed in `_ignored_evals`), a pre-recovery record (named by
a re-pointed row's `_pre_recovery_eval_path`), archived, or none of these. *Features* are
per run for multi-run cells. *Scored vintage* is the commit `rescore_scored_vintage.py`
reproduced against, with the reference commit where it differs from today's. *Rewritten
by* lists every later commit in the file's history. *F1 committed → today* is at 20 m,
or at the cell's only committed buffer. "Today" is the frames OFF re-score of the
current file.

### A. E71 dead-tile rerun rewrote single passes (2026-07-30): 15 rows

| Evaluation | Register | Features committed → today | Scored vintage | Rewritten by | F1 committed → today | Reproduces on scored vintage | Out of frame (scored vintage) |
|---|---|---|---|---|---|---|---:|
| `archive/superseded-evals/n1-outstanding-384/paper-eval-384px-outstanding/pro-image-high-t-0-0/evaluation.json` | archived | 692/681/677 → 750/744/741 | `c3852ebad` | `99ae28ec4` | 30 m: 0.5902 → 0.6209 | yes | 0 |
| `archive/superseded-evals/n1-outstanding-384/paper-eval-384px-outstanding/pro-text-high-t-0-0/evaluation.json` | archived | 1026/1028/1004 → 1090/1112/1060 | `c3852ebad` | `99ae28ec4`, `d01ea4412` | 30 m: 0.5148 → 0.5111 | yes | 0 |
| `results/paper-eval/mcc/384px/pro-image-high-t-0-0/evaluation.json` | waived (`_ignored_evals`, n1-outstanding-384) | 692/681/677 → 750/744/741 | `1f443fd69` | `99ae28ec4` | 30 m: 0.5902 → 0.6209 | yes | 0 |
| `results/paper-eval/mcc/384px/pro-text-high-t-0-0/evaluation.json` | waived (`_ignored_evals`, n1-outstanding-384) | 1026/1028/1004 → 1090/1112/1060 | `1f443fd69` | `99ae28ec4`, `d01ea4412` | 30 m: 0.5148 → 0.5111 | yes | 0 |
| `results/paper-eval/n1/384px-14buf-mcc/pro-image-high-t-0-0/evaluation.json` | registered: `n1-outstanding-384::baseline-pro-image-high-t-0-0` | 692/681/677 → 750/744/741 | `1f443fd69` | `99ae28ec4` | 20 m: 0.5276 → 0.5446 | yes | 0 |
| `results/paper-eval/n1/384px-14buf-mcc/pro-text-high-t-0-0/evaluation.json` | registered: `n1-outstanding-384::baseline-pro-text-high-t-0-0` | 1026/1028/1004 → 1090/1112/1060 | `1f443fd69` | `99ae28ec4`, `d01ea4412` | 20 m: 0.4942 → 0.4919 | yes | 0 |
| `results/paper-eval/n1/384px-all-buffers/pro-image-high-t-0-0/evaluation.json` | waived (`_ignored_evals`, n1-outstanding-384) | 692/681/677 → 750/744/741 | `1f443fd69` | `99ae28ec4` | 20 m: 0.5276 → 0.5446 | yes | 0 |
| `results/paper-eval/n1/384px-all-buffers/pro-text-high-t-0-0/evaluation.json` | waived (`_ignored_evals`, n1-outstanding-384) | 1026/1028/1004 → 1090/1112/1060 | `1f443fd69` | `99ae28ec4`, `d01ea4412` | 20 m: 0.4942 → 0.4919 | yes | 0 |
| `results/rescore-2026-05-31/e47-propose-brief/flash-high-text-n5/propose_brief-text/run_4/evaluation.json` | registered: `e47-propose-brief::single-pass-run_4` | 1619 → 1641 | `52b0215a6` | `99ae28ec4` | 20 m: 0.3544 → 0.3613 | yes | 0 |
| `results/rescore-2026-05-31/n1-outstanding-384/pro-image-high-t0/run_1/evaluation.json` | registered: `n1-outstanding-384::pro-image-high-t0-single-pass-run_1` | 692 → 750 | `c3852ebad` | `99ae28ec4` | 20 m: 0.5288 → 0.5401 | yes | 0 |
| `results/rescore-2026-05-31/n1-outstanding-384/pro-image-high-t0/run_2/evaluation.json` | registered: `n1-outstanding-384::pro-image-high-t0-single-pass-run_2` | 681 → 744 | `c3852ebad` | `99ae28ec4` | 20 m: 0.5305 → 0.5479 | yes | 0 |
| `results/rescore-2026-05-31/n1-outstanding-384/pro-image-high-t0/run_3/evaluation.json` | registered: `n1-outstanding-384::pro-image-high-t0-single-pass-run_3` | 677 → 741 | `c3852ebad` | `99ae28ec4`, `d01ea4412` | 20 m: 0.5234 → 0.5459 | yes | 0 |
| `results/rescore-2026-05-31/n1-outstanding-384/pro-text-high-t0/run_1/evaluation.json` | registered: `n1-outstanding-384::pro-text-high-t0-single-pass-run_1` | 1026 → 1090 | `c3852ebad` | `99ae28ec4`, `d01ea4412` | 20 m: 0.501 → 0.4931 | yes | 0 |
| `results/rescore-2026-05-31/n1-outstanding-384/pro-text-high-t0/run_2/evaluation.json` | registered: `n1-outstanding-384::pro-text-high-t0-single-pass-run_2` | 1028 → 1112 | `c3852ebad` | `99ae28ec4` | 20 m: 0.4867 → 0.4848 | yes | 0 |
| `results/rescore-2026-05-31/n1-outstanding-384/pro-text-high-t0/run_3/evaluation.json` | registered: `n1-outstanding-384::pro-text-high-t0-single-pass-run_3` | 1004 → 1060 | `c3852ebad` | `99ae28ec4` | 20 m: 0.4948 → 0.4977 | yes | 0 |

### B. E71 downstream consensus rebuilds (2026-07-30 and 2026-09-08): 25 rows

| Evaluation | Register | Features committed → today | Scored vintage | Rewritten by | F1 committed → today | Reproduces on scored vintage | Out of frame (scored vintage) |
|---|---|---|---|---|---|---|---:|
| `results/h12-v2/greedy/r3-hp-heavy/t1/evaluation.json` | waived (`_ignored_evals`, h12-v2) | 1518 → 1521 | `2e84d4a65` | `e7ebc1695` | 20 m: 0.2683 → 0.2679 | yes | 0 |
| `results/h12-v2/wbf/r3-hp-heavy/evaluation.json` | waived (`_ignored_evals`, h12-v2) | 1097 → 1099 | `2e84d4a65` | `e7ebc1695` | 20 m: 0.3055 → 0.3051 | yes | 0 |
| `results/phase3a-image-matrix/high-t0.0/n10/high-t0-0-1of10/evaluation.json` | waived (`_ignored_evals`, pv-diag-384) | 802 → 889 | `2e8cc6481` | `f6116cba0`, `77bb342b4` | 20 m: 0.4883 → 0.4970 | yes | 0 |
| `results/phase3a-image-matrix/high-t0.0/n10/high-t0-0-2of10/evaluation.json` | waived (`_ignored_evals`, pv-diag-384) | 736 → 816 | `2e8cc6481` | `f6116cba0`, `77bb342b4` | 20 m: 0.4594 → 0.5084 | yes | 0 |
| `results/phase3a-image-matrix/high-t0.0/n10/high-t0-0-3of10/evaluation.json` | waived (`_ignored_evals`, pv-diag-384) | 718 → 782 | `2e8cc6481` | `f6116cba0`, `77bb342b4` | 20 m: 0.4666 → 0.5127 | yes | 0 |
| `results/phase3a-text-matrix/high-t0.0/n3/high-t0-0-1of3/evaluation.json` | waived (`_ignored_evals`, pv-diag-384) | 1256 → 1319 | `09fe46a7f` | `f6116cba0`, `77bb342b4` | 20 m: 0.4364 → 0.4424 | yes | 0 |
| `results/phase3a-text-matrix/high-t0.0/n3/high-t0-0-2of3/evaluation.json` | waived (`_ignored_evals`, pv-diag-384) | 985 → 1032 | `09fe46a7f` | `f6116cba0`, `77bb342b4` | 20 m: 0.5099 → 0.5194 | yes | 0 |
| `results/phase3a-text-matrix/high-t0.0/n3/high-t0-0-3of3/evaluation.json` | waived (`_ignored_evals`, pv-diag-384) | 745 → 796 | `09fe46a7f` | `f6116cba0`, `77bb342b4` | 20 m: 0.6051 → 0.6109 | yes | 0 |
| `results/rescore-2026-05-31/e47-propose-brief/flash-high-text-n5/propose_brief-text/consensus/consensus_t1/evaluation.json` | pre-recovery record (`_pre_recovery_eval_path`) | 4491 → 4149 | `1f443fd69` | `e01b8617a` | 20 m: 0.1669 → 0.1798 | yes | 0 |
| `results/rescore-2026-05-31/e47-propose-brief/flash-high-text-n5/propose_brief-text/consensus/consensus_t2/evaluation.json` | pre-recovery record (`_pre_recovery_eval_path`) | 1659 → 1537 | `1f443fd69` | `e01b8617a` | 20 m: 0.3868 → 0.4128 | yes | 0 |
| `results/rescore-2026-05-31/e47-propose-brief/flash-high-text-n5/propose_brief-text/consensus/consensus_t3/evaluation.json` | pre-recovery record (`_pre_recovery_eval_path`) | 1080 → 998 | `1f443fd69` | `e01b8617a` | 20 m: 0.5188 → 0.5471 | yes | 0 |
| `results/rescore-2026-05-31/e47-propose-brief/flash-high-text-n5/propose_brief-text/consensus/consensus_t4/evaluation.json` | pre-recovery record (`_pre_recovery_eval_path`) | 738 → 699 | `1f443fd69` | `e01b8617a` | 20 m: 0.6394 → 0.6543 | yes | 0 |
| `results/rescore-2026-05-31/e47-propose-brief/flash-high-text-n5/propose_brief-text/consensus/consensus_t5/evaluation.json` | pre-recovery record (`_pre_recovery_eval_path`) | 461 → 455 | `1f443fd69` | `e01b8617a` | 20 m: 0.7143 → 0.7326 | yes | 0 |
| `results/rescore-2026-05-31/n1-outstanding-384/pro-image-high-t0/consensus/consensus_t1/evaluation.json` | pre-recovery record (`_pre_recovery_eval_path`) | 665 → 730 | `1f443fd69` | `185681674` | 20 m: 0.5509 → 0.5614 | yes | 0 |
| `results/rescore-2026-05-31/n1-outstanding-384/pro-image-high-t0/consensus/consensus_t2/evaluation.json` | pre-recovery record (`_pre_recovery_eval_path`) | 627 → 690 | `1f443fd69` | `185681674` | 20 m: 0.5499 → 0.5760 | yes | 0 |
| `results/rescore-2026-05-31/n1-outstanding-384/pro-image-high-t0/consensus/consensus_t3/evaluation.json` | pre-recovery record (`_pre_recovery_eval_path`) | 604 → 648 | `1f443fd69` | `185681674` | 20 m: 0.5525 → 0.5854 | yes | 0 |
| `results/rescore-2026-05-31/n1-outstanding-384/pro-text-high-t0/consensus/consensus_t1/evaluation.json` | pre-recovery record (`_pre_recovery_eval_path`) | 1118 → 1192 | `1f443fd69` | `185681674` | 20 m: 0.4726 → 0.4634 | yes | 0 |
| `results/rescore-2026-05-31/n1-outstanding-384/pro-text-high-t0/consensus/consensus_t2/evaluation.json` | pre-recovery record (`_pre_recovery_eval_path`) | 946 → 991 | `1f443fd69` | `185681674` | 20 m: 0.5199 → 0.5203 | yes | 0 |
| `results/rescore-2026-05-31/n1-outstanding-384/pro-text-high-t0/consensus/consensus_t3/evaluation.json` | pre-recovery record (`_pre_recovery_eval_path`) | 783 → 842 | `1f443fd69` | `185681674` | 20 m: 0.5665 → 0.5748 | yes | 0 |
| `results/rescore-2026-06-05/pv-diag-384/consensus-sweep/flash-high-image-n5__image-t0.0__consensus__t1/evaluation.json` | none (not registered, waived or pointed to) | 802 → 889 | `2e8cc6481` | `f6116cba0`, `77bb342b4` | 20 m: 0.4883 → 0.4970 | yes | 0 |
| `results/rescore-2026-06-05/pv-diag-384/consensus-sweep/flash-high-image-n5__image-t0.0__consensus__t2/evaluation.json` | waived (`_ignored_evals`, pv-diag-384) | 736 → 816 | `2e8cc6481` | `f6116cba0`, `77bb342b4` | 20 m: 0.4594 → 0.5084 | yes | 0 |
| `results/rescore-2026-06-05/pv-diag-384/consensus-sweep/flash-high-image-n5__image-t0.0__consensus__t3/evaluation.json` | waived (`_ignored_evals`, pv-diag-384) | 718 → 782 | `2e8cc6481` | `f6116cba0`, `77bb342b4` | 20 m: 0.4666 → 0.5127 | yes | 0 |
| `results/rescore-2026-06-05/pv-diag-384/consensus-sweep/flash-high-text-n5__text-t0.0__consensus__t1/evaluation.json` | waived (`_ignored_evals`, pv-diag-384) | 1256 → 1319 | `09fe46a7f` | `f6116cba0`, `77bb342b4` | 20 m: 0.4364 → 0.4424 | yes | 0 |
| `results/rescore-2026-06-05/pv-diag-384/consensus-sweep/flash-high-text-n5__text-t0.0__consensus__t2/evaluation.json` | waived (`_ignored_evals`, pv-diag-384) | 985 → 1032 | `09fe46a7f` | `f6116cba0`, `77bb342b4` | 20 m: 0.5099 → 0.5194 | yes | 0 |
| `results/rescore-2026-06-05/pv-diag-384/consensus-sweep/flash-high-text-n5__text-t0.0__consensus__t3/evaluation.json` | none (not registered, waived or pointed to) | 745 → 796 | `09fe46a7f` | `f6116cba0`, `77bb342b4` | 20 m: 0.6051 → 0.6109 | yes | 0 |

### C. E57/Obs 338 Pro-medium run_1 recovery (2026-06-03): 6 rows

| Evaluation | Register | Features committed → today | Scored vintage | Rewritten by | F1 committed → today | Reproduces on scored vintage | Out of frame (scored vintage) |
|---|---|---|---|---|---|---|---:|
| `archive/superseded-evals/n1-baseline-384px-30m-only/pro-image-medium-t-0-0/evaluation.json` | archived | 519 → 587 | `3d22184d6` | `c07c57766` | 30 m: 0.7338 → 0.7495 | yes | 0 |
| `archive/superseded-evals/n1-baseline-384px-30m-only/pro-text-medium-t-0-0/evaluation.json` | archived | 430 → 446 | `3d22184d6` | `c07c57766` | 30 m: 0.7838 → 0.7968 | yes | 0 |
| `results/paper-eval/mcc/384px/pro-image-medium-t-0-0/evaluation.json` | waived (`_ignored_evals`, pv-diag-384) | 519 → 587 | `3d22184d6` | `c07c57766` | 30 m: 0.7338 → 0.7495 | yes | 0 |
| `results/paper-eval/mcc/384px/pro-text-medium-t-0-0/evaluation.json` | waived (`_ignored_evals`, pv-diag-384) | 430 → 446 | `3d22184d6` | `c07c57766` | 30 m: 0.7838 → 0.7968 | yes | 0 |
| `results/paper-eval/n1/384px-all-buffers/pro-image-medium-t-0-0/evaluation.json` | waived (`_ignored_evals`, pv-diag-384) | 519 → 587 | `3d22184d6` | `c07c57766` | 20 m: 0.6059 → 0.6243 | yes | 0 |
| `results/paper-eval/n1/384px-all-buffers/pro-text-medium-t-0-0/evaluation.json` | waived (`_ignored_evals`, pv-diag-384) | 430 → 446 | `3d22184d6` | `c07c57766` | 20 m: 0.763 → 0.7764 | yes | 0 |

### D. 55-map verified-set recovery rebuilds and reference edits (2026-05): 7 rows

| Evaluation | Register | Features committed → today | Scored vintage | Rewritten by | F1 committed → today | Reproduces on scored vintage | Out of frame (scored vintage) |
|---|---|---|---|---|---|---|---:|
| `archive/55maps-superseded-gt-evals/55maps-cleaned-gt-evaluation/image/evaluation.json` | archived | 4665 → 4680 | `4c147af65`; reference `dea1155fa` | `8965d2365`, `8699f456b` | 20 m: 0.507 → 0.5082 | yes | 0 |
| `archive/55maps-superseded-gt-evals/55maps-cleaned-gt-evaluation/text-high/evaluation.json` | archived | 4143 → 4164 | `4e5c5e5a3`; reference `dea1155fa` | `d7f85978d` | 20 m: 0.6247 → 0.6260 | yes | 0 |
| `archive/55maps-superseded-gt-evals/55maps-cleaned-gt-evaluation/text-min/evaluation.json` | archived | 3861 → 3865 | `f0f7158e7`; reference `dea1155fa` | `c1ea6df3c` | 20 m: 0.6199 → 0.6201 | yes | 0 |
| `archive/55maps-superseded-gt-evals/per-run/55maps-image-generalisation/mcc/evaluation.json` | archived | 4680 → 4680 | `8699f456b`; reference `baf1497a7` | none (only the reference changed) | 50 m: 0.7745 → 0.7747 | yes | 0 |
| `archive/55maps-superseded-gt-evals/per-run/55maps-text-high-generalisation/mcc/evaluation.json` | archived | 4164 → 4164 | `d7f85978d`; reference `dea1155fa` | none (only the reference changed) | 50 m: 0.7919 → 0.7921 | yes | 0 |
| `archive/55maps-superseded-gt-evals/per-run/55maps-text-high-t0.3-generalisation/mcc/evaluation.json` | archived | 4350 → 4350 | `548604d95`; reference `dea1155fa` | none (only the reference changed) | 50 m: 0.8045 → 0.8047 | yes | 0 |
| `archive/55maps-superseded-gt-evals/per-run/55maps-text-min-generalisation/mcc/evaluation.json` | archived | 3865 → 3865 | `c1ea6df3c`; reference `baf1497a7` | none (only the reference changed) | 50 m: 0.7619 → 0.7618 | yes | 0 |

### E. Recovery-fragment-drop fix re-materialised the 3.7 K = 3 set (2026-09-13): 1 row

| Evaluation | Register | Features committed → today | Scored vintage | Rewritten by | F1 committed → today | Reproduces on scored vintage | Out of frame (scored vintage) |
|---|---|---|---|---|---|---|---:|
| `archive/superseded-consensus-2026-09-13/recovery-fragment-drop/evaluations-as-read-2026-09-13/gemini37-screen-2026-08-28__g37-text-k3-verified-opmax/evaluation.json` | archived | 494 → 495 | `326181bcd` | `987534c03` | 20 m: 0.887 → 0.8860 | F1/P/R yes; MCC no (mcc: committed 0.1337 vintage None) | 27 |

## 5. Registered numbers and the claims that lean on them

### 5.1 The nine pinned conditions

Registered (pinned) value, the frames OFF re-score of today's file, and the registered
`-post-e71` twin, from `results/conditions-manifest.json` and `out/trace.json`
(`summarise_drift.py`). Δ is today minus registered.

| Registered condition | Metric | Registered (pinned) | Today's file (OFF) | Δ | `-post-e71` twin | Twin equals today (±1e-4) |
|---|---|---:|---:|---:|---:|---|
| `n1-outstanding-384::baseline-pro-image-high-t-0-0` | F1@20 | 0.5276 | 0.5446 | +0.0170 | 0.5446 | yes |
| `n1-outstanding-384::baseline-pro-image-high-t-0-0` | F1@50 | 0.6337 | 0.6655 | +0.0318 | 0.6656 | yes |
| `n1-outstanding-384::baseline-pro-image-high-t-0-0` | MCC | 0.6062 | 0.6481 | +0.0419 | 0.6481 | yes |
| `n1-outstanding-384::baseline-pro-text-high-t-0-0` | F1@20 | 0.4942 | 0.4919 | -0.0023 | 0.4919 | yes |
| `n1-outstanding-384::baseline-pro-text-high-t-0-0` | F1@50 | 0.5249 | 0.5208 | -0.0041 | 0.5208 | yes |
| `n1-outstanding-384::baseline-pro-text-high-t-0-0` | MCC | 0.3808 | 0.3992 | +0.0184 | 0.3992 | yes |
| `e47-propose-brief::single-pass-run_4` | F1@20 | 0.3544 | 0.3613 | +0.0069 | 0.3613 | yes |
| `e47-propose-brief::single-pass-run_4` | F1@50 | 0.3856 | 0.3921 | +0.0065 | 0.3921 | yes |
| `e47-propose-brief::single-pass-run_4` | MCC | 0.2287 | 0.2560 | +0.0273 | 0.2560 | yes |
| `n1-outstanding-384::pro-image-high-t0-single-pass-run_3` | F1@20 | 0.5234 | 0.5459 | +0.0225 | 0.5459 | yes |
| `n1-outstanding-384::pro-image-high-t0-single-pass-run_3` | F1@50 | 0.6295 | 0.6650 | +0.0355 | 0.6650 | yes |
| `n1-outstanding-384::pro-image-high-t0-single-pass-run_3` | MCC | 0.6021 | 0.6428 | +0.0407 | 0.6428 | yes |
| `n1-outstanding-384::pro-image-high-t0-single-pass-run_2` | F1@20 | 0.5305 | 0.5479 | +0.0174 | 0.5479 | yes |
| `n1-outstanding-384::pro-image-high-t0-single-pass-run_2` | F1@50 | 0.6344 | 0.6667 | +0.0323 | 0.6667 | yes |
| `n1-outstanding-384::pro-image-high-t0-single-pass-run_2` | MCC | 0.6073 | 0.6508 | +0.0435 | 0.6508 | yes |
| `n1-outstanding-384::pro-image-high-t0-single-pass-run_1` | F1@20 | 0.5288 | 0.5401 | +0.0113 | 0.5401 | yes |
| `n1-outstanding-384::pro-image-high-t0-single-pass-run_1` | F1@50 | 0.6371 | 0.6650 | +0.0279 | 0.6650 | yes |
| `n1-outstanding-384::pro-image-high-t0-single-pass-run_1` | MCC | 0.6093 | 0.6508 | +0.0415 | 0.6508 | yes |
| `n1-outstanding-384::pro-text-high-t0-single-pass-run_3` | F1@20 | 0.4948 | 0.4977 | +0.0029 | 0.4977 | yes |
| `n1-outstanding-384::pro-text-high-t0-single-pass-run_3` | F1@50 | 0.5254 | 0.5271 | +0.0017 | 0.5271 | yes |
| `n1-outstanding-384::pro-text-high-t0-single-pass-run_3` | MCC | 0.3805 | 0.4083 | +0.0278 | 0.4083 | yes |
| `n1-outstanding-384::pro-text-high-t0-single-pass-run_2` | F1@20 | 0.4867 | 0.4848 | -0.0019 | 0.4848 | yes |
| `n1-outstanding-384::pro-text-high-t0-single-pass-run_2` | F1@50 | 0.5195 | 0.5145 | -0.0050 | 0.5145 | yes |
| `n1-outstanding-384::pro-text-high-t0-single-pass-run_2` | MCC | 0.3704 | 0.3922 | +0.0218 | 0.3922 | yes |
| `n1-outstanding-384::pro-text-high-t0-single-pass-run_1` | F1@20 | 0.5010 | 0.4931 | -0.0079 | 0.4931 | yes |
| `n1-outstanding-384::pro-text-high-t0-single-pass-run_1` | F1@50 | 0.5298 | 0.5207 | -0.0091 | 0.5207 | yes |
| `n1-outstanding-384::pro-text-high-t0-single-pass-run_1` | MCC | 0.3916 | 0.3970 | +0.0054 | 0.3970 | yes |

The baseline image twin's F1@50 (0.6656 against 0.6655) differs only by the
four-decimal rounding of a three-run mean. The F1@20 deltas are the ones the E71 rider
quotes (`protocol-errata.md:3349–3353`): "+0.011 to +0.023 on the image passes",
"−0.008 to +0.003 on the text passes", and "+0.017 / −0.002 on the two aggregates, and
+0.007 on the e47 pass".

**Who reads the pinned nine** (`results/run-analyses.json` → `conditions_compared`,
`signature.status`):

- **`uplift-supplement-flatten`** (signed 2026-09-10T22:55:40Z; Appendix) flattens all
  441 registered conditions, so it carries all nine pinned rows **and** their nine twins
  (for example `results/uplift-supplement/conditions.csv` lines 87–88 and 114–115). It is a
  derivation with no verdict that rests on a pinned value. See § 6.3 for a disclosure
  gap in its `detections_path`.
- **No tier, ladder, hypothesis or cost analysis reads them.** `h6-a07-voting-thresholds`
  (signed 2026-09-10T06:56:15Z) and `h6-a09-cost-gate` (signed 2026-09-17T07:37:26Z)
  compare the re-pointed consensus rows and the `-post-e71` baselines. The
  `n1-baseline-matrix-384` and `diversity-dividend-384` tierings (unsigned) use the
  genuine-Pro `n1-pro-rerun-384` baselines
  (`results/paper-eval/n1/384px-14buf-mcc/tiering/tiering_20m.md:6`).
- **Documents** that quote the pinned values do so beside the twins:
  `results/working-precision/gs-plateau-characterisation.md:65–68, :139–154`, and the
  E71 rider. `results/conditions-manifest.md` is generated and lists both rows.

### 5.2 The re-pointed consensus conditions

Fourteen registered consensus rows (n1-outstanding, e47 and pv-diag t0.0) point at a
post-recovery re-score. Their predecessors are the group B rows above. The check below
asks whether each registered value equals the OFF re-score of today's file
(`summarise_drift.py`).

| Re-pointed registered condition | F1@20 registered / today | F1@50 registered / today | MCC registered / today | Equal (±1e-4) |
|---|---|---|---|---|
| `e47-propose-brief::consensus-1of5` | 0.1798 / 0.1798 | 0.1859 / 0.1859 | 0.0882 / 0.0882 | yes |
| `e47-propose-brief::consensus-2of5` | 0.4128 / 0.4128 | 0.4270 / 0.4270 | 0.1971 / 0.1971 | yes |
| `e47-propose-brief::consensus-3of5` | 0.5471 / 0.5471 | 0.5666 / 0.5666 | 0.3374 / 0.3374 | yes |
| `e47-propose-brief::consensus-4of5` | 0.6543 / 0.6543 | 0.6684 / 0.6684 | 0.4049 / 0.4049 | yes |
| `e47-propose-brief::consensus-5of5` | 0.7326 / 0.7326 | 0.7461 / 0.7461 | 0.5262 / 0.5262 | yes |
| `n1-outstanding-384::pro-image-high-t0-consensus-1of3` | 0.5614 / 0.5614 | 0.6747 / 0.6747 | 0.5577 / 0.5577 | yes |
| `n1-outstanding-384::pro-image-high-t0-consensus-2of3` | 0.5760 / 0.5760 | 0.6987 / 0.6987 | 0.5678 / 0.5678 | yes |
| `n1-outstanding-384::pro-image-high-t0-consensus-3of3` | 0.5854 / 0.5854 | 0.7073 / 0.7073 | 0.5921 / 0.5921 | yes |
| `n1-outstanding-384::pro-text-high-t0-consensus-1of3` | 0.4634 / 0.4634 | 0.4929 / 0.4929 | 0.2629 / 0.2629 | yes |
| `n1-outstanding-384::pro-text-high-t0-consensus-2of3` | 0.5203 / 0.5203 | 0.5526 / 0.5526 | 0.3333 / 0.3333 | yes |
| `n1-outstanding-384::pro-text-high-t0-consensus-3of3` | 0.5748 / 0.5748 | 0.6092 / 0.6092 | 0.3894 / 0.3894 | yes |
| `pv-diag-384::flash-high-image-n5-image-t0.0-consensus-1of3` | 0.4970 / 0.4970 | 0.5997 / 0.5997 | 0.4671 / 0.4671 | yes |
| `pv-diag-384::flash-high-image-n5-image-t0.0-consensus-3of3` | 0.5127 / 0.5127 | 0.6179 / 0.6179 | 0.4993 / 0.4993 | yes |
| `pv-diag-384::flash-high-text-n5-text-t0.0-consensus-3of3` | 0.6109 / 0.6109 | 0.6401 / 0.6401 | 0.4318 / 0.4318 | yes |

Re-pointed rows checked: 14; equal to today's file: 14

For these conditions the registered numbers are therefore the current-file numbers.

### 5.3 Waived, unlisted and archived rows

The other 31 rows (12 waived pv-diag t0.0 and h12-v2 cells, 8 waived `paper-eval`
duplicates, 2 unlisted pv-diag predecessors, 12 archived) source no registered
condition. No analysis in `results/run-analyses.json` compares a condition built from
them. Their committed numbers are historical records. None is a candidate for citation.

## 6. Flags

1. **The frames § 3.1 flag was a false alarm, raised by a vintage-blind check.**
   The nine registered "drifted" numbers are pinned on purpose (D40; the E82 contract's
   § 3, item 1; ruling 3a), stamped in the register, disclosed in the E71 rider, and paired with
   current-file twins. `classify_reproduction.py` looks at `blob_hashes` and feature
   counts. It does not look at `_metadata.e82_input_vintage`, the register's
   `input_vintage`, or `_pre_recovery_eval_path`. A corpus-wide re-score that does not
   look at them will raise these cells again every time. `verify_run_conditions.py`
   already treats the pins as "a reproduction gate, not a currency gate"
   (`protocol-errata.md:3358–3359`).
2. **Two pre-recovery evaluations are listed nowhere.**
   `results/rescore-2026-06-05/pv-diag-384/consensus-sweep/flash-high-image-n5__image-t0.0__consensus__t1/`
   and `…/flash-high-text-n5__text-t0.0__consensus__t3/` are the predecessors of the two
   pv-diag cells re-pointed on 2026-07-30. They are neither registered nor waived, and
   no `_pre_recovery_eval_path` names them. The other ten pv-diag t0.0 evaluations of these
   files are waived, and the eleven 2026-09-08 predecessors are named by
   `_pre_recovery_eval_path`. Bookkeeping only; no number depends on it.
3. **The uplift supplement does not record the pin.** In
   `results/uplift-supplement/conditions.csv`, the nine pinned rows give
   `detections_path` as the working-tree path. That path now holds the recovered file,
   and no column names the scored commit. The rows' `notes` mention only the reference
   replay copy. A reader who follows `detections_path` gets detections that did not
   produce the row's numbers. The build report records that the `-post-e71` rows joined
   (`results/uplift-supplement/build-report.md:228–230`), but not the pin.
4. **`ladders.json` carries the archived K = 3 evaluation.** Its K = 3 rung
   (`results/k-ladder-2026-09-12/phase2/ladders.json:3208–3209`: 494 detections,
   F1@20 0.887, P 0.834, R 0.9471) is exactly the archived "as read" evaluation of
   group E. This corroborates the frames report's § 5.1 flag (lines 325–327) that the
   ladder file was not refreshed after `987534c03`. That scored vintage also has 27
   out-of-frame detections, so the stale rung carries the frames defect as well.
5. **Adjacent: a three-pass cell labelled N = 10.**
   `results/phase3a-image-matrix/high-t0.0/n10/high-t0-0-{1,2,3}of10/` score the
   pv-diag image t0.0 consensus. Its `voting_summary.json` reads `total_passes: 3` both
   at the scored vintage `2e8cc6481` and today, and the pool has three run directories.
   The matrix summary calls the cell "HIGH-T0.0 / N = 10" and quotes the pre-recovery
   0.488 (`results/phase3a-image-matrix/consensus-analysis-summary.md:26, :42`). The
   cells are waived, and the summary itself mentions "K = 3 at T = 0.0" at line 262.
   This report did not investigate further.
6. **Archive READMEs.** `archive/pre-recovery-2026-07-30/` and
   `archive/pre-recovery-2026-09-08/` hold no README. Their provenance lives in
   `reports/recovery-consistency-audit-2026-09-08.md` and the E71 riders. Minor.

## 7. Recommendations

1. **Frames report, § 3.1.** Re-word the input-drift bullet. The 42 live cells are
   pinned or pre-recovery records whose scored vintages reproduce (this report, § 4),
   with 0 out-of-frame detections on both vintages. The nine registered ones are E71
   pins with registered twins. "Superseded under E57" should read "pinned under E71
   ruling 3a; E57 governs their model of record". The 12 archived cells are likewise
   explained.
2. **Paper.** No registered number needs to change because of this drift. Cite the
   `-post-e71` twins and the `recovery-reeval-*` rows for any performance statement
   about these pools. Cite the pinned nine only as the historical record ruling 3a
   preserves. For any "Pro" wording, cite `n1-pro-rerun-384`. Do not cite the e47 April
   consensus numbers in any role, because of the D6-class double read.
3. **Tooling, before the next corpus-wide re-score** (including the scorer fix the
   frames report recommends). Make the reproduction gate vintage-aware, as
   `rescore_scored_vintage.py` is: honour `_metadata.e82_input_vintage`, the register's
   `input_vintage` and `_pre_recovery_eval_path`, and fall back to a count-matched
   commit. Then "input drift" shrinks to cells with no recorded or reconstructable
   explanation. Among these 54 there are none.
4. **Optional bookkeeping, for the PI to rule on.** List the two predecessors of § 6.2,
   add the scored commit to the nine pinned uplift rows (§ 6.3), refresh the
   `ladders.json` K = 3 rung (already open from the frames report), and add READMEs
   under `archive/pre-recovery-*`.
5. **Registry.** This report is a new hand-written `reports/**.md`, so
   `reports/verification/generated-file-registry.json` needs the rebuild that
   `d40a5d4a2` performed for the frames report. It was not done here, because this
   commit is restricted to this report's own files.

## 8. Not established

- **Other machines' copies.** Only sapphire's working tree and git history were read.
  Whether amd-tower, zbook or rpi-server hold different bytes at these paths was not
  checked. The brief placed this out of scope.
- **Intervals.** Only point estimates and MCC were re-scored on the scored vintages.
  Whether each committed bootstrap interval reproduces was not tested.
- **ON values on the scored vintages.** The frames diagnostic counted out-of-frame
  detections on every scored vintage. ON scores were not computed. Only the archived
  K = 3 copy (27) would differ, and it is not live.
- **The archived K = 3 MCC.** Its committed 0.1337 cannot be reproduced under today's
  tile-join invariant (`tile_join_detection_shortfall`). Whether it reproduces under the
  pre-invariant library was not tested.
- **Intent behind §§ 6.2–6.3.** Whether the two unlisted predecessors and the missing
  pin column in the uplift supplement are deliberate was not determined.
- **Early evaluation history.** `git log --follow` on some evaluations reaches commits
  that predate the evaluation's current path, through git's rename heuristic. Those
  early entries were not verified, and no claim here rests on them. When each live
  evaluation was written rests on `generated_at_utc` and the E82 commits.

## Changelog

### 2026-10-07 — Original publication

First publication: provenance trace of the 54 frames gate (i) input-drift rows (42
live, 12 archived). Five causes were identified, and every cell's scored vintage was
reconstructed from git and re-scored on sapphire. 53 of 54 cells reproduce exactly; the
54th reproduces its F1, P and R, and only its pre-invariant MCC is refused. None of the
42 live scored vintages has an out-of-frame detection. The nine registered cells are
the E71 ruling 3a pins, and their registered twins equal today's file. Scripts:
`trace_input_drift.py`, `rescore_scored_vintage.py`, `summarise_drift.py`; outputs
`out/trace.json`, `out/scored_vintage.json`.
