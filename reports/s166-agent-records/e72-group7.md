# E72's Group 7 on the restated inputs: the board regenerated (D69 Q15)

> **Last revised**: 2026-10-30 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Agent**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), an overnight sub-agent of the Session 166 main session.
  2026-10-30, on zbook.
- **Repository**: `map-reader-llm` (`saross/map-reader-llm`), worktree
  `~/worktrees/map-reader-llm/claude-e72-regen`, branch
  `e72-regen-2026-10-30`, branched from `origin/main` at `3cbe6867e`.
- **Commits reported here**: `27454299f` (the adapted
  `scripts/regen_e43_board.py` and its tests) and `fac61ebfe` (the
  regenerated `results/e43-board-regen/`). This record is the next commit on
  the branch. Nothing is merged, and no pull request is open.
- **Brief**: the Principal Investigator's (PI's) ruling D69 Q15 ("yes, queue
  as follow-up"; `planning/pi-decisions-2026-09-20.md` D69;
  `planning/paper-writeup-continuity.md`, "To do after PR #52 … D69 Q15").
  Cost: no application programming interface (API) calls and no permutation
  tests. The regeneration takes about 2 s wall-clock (7 s of CPU) on zbook,
  below the project's 30 s threshold for moving work to sapphire.

## 1. The answer

**E72's flip of Group 7 reverses.** On the restated inputs, the 20 m
`N=30 vs N=10 (HIGH text)` row is significant in E72's 23-member family.

| Row: `results/pairwise/20m`, family `confirmatory`, group 7, `N=30 vs N=10 (HIGH text)` (Flash HIGH text 26-of-30 against 9-of-10) | 2026-08-02 board (`2f3ef020a`) | 2026-10-30 board (`fac61ebfe`) |
|---|--:|--:|
| Raw permutation p | 0.0375 | 0.0357 |
| Benjamini–Hochberg (BH) q, full 26-member family (the run's own) | 0.04875 | 0.04641 |
| BH q, E72's 23-member family (three group 4 members dropped) | 0.050735 | **0.0483** |
| Verdict in the 23-member family (q < 0.05) | not significant | **significant** |
| Did dropping the E72 members change the verdict? | yes (the "flip") | no |

Source: `results/e43-board-regen/bh-families/families_recomputed.csv`
line 22 at each commit. The sub-agent's figure of 0.0483
(`reports/s164-agent-records/restatement-pass.md` § 5 item 13) is confirmed
by the generator itself. In both revisions the 26-member family finds the
row significant, so its false discovery rate (FDR) verdict does not move.

The per-test file
(`results/pairwise/20m/group_7_poolsize/n-30-vs-n-10-high-text-flash-high-text-26-of-30-vs-flash-high-text-9-of-10.json`)
was regenerated in place by the S164 pass; it is not one of the dated
records. Both arms' F1 rose by about 0.0023: N=30 0.814118 → 0.816471, and
N=10 0.796767 → 0.799076. ΔF1 went from 0.017351 to 0.017394 and p from
0.0375 to 0.0357. The detection counts (415, 431) and the tile
wins/losses/ties (10/8/469) are unchanged. At 30 m the same row stays not
significant (p 0.0671 → 0.0668, q 0.090782 → 0.096025).

## 2. Every verdict that changes

The comparison is between the committed 2026-08-02 board and the
regenerated one, row for row. It covers the 253 and 231 retained board pairs
and every member of the three affected families. Five verdicts change. The
generator lists them in `results/e43-board-regen/summary.md` § Changelog,
and they were re-read from that file at `fac61ebfe`.

| Artefact | Condition A | Condition B | p (raw) | q | Verdict |
|---|---|---|---|---|---|
| `leaderboard-20m` | image-baseline--flash-min-vf (t=0.2) | flash-min-text-t07 N=30 N=30, 29-of-30 | 0.0383 → 0.0469 | 0.048693 → 0.059033 | significant → ns |
| `leaderboard-30m` | flash-high-image-3-of-5--flash-min-vf (t=0.15) | flash-high-text N=10 N=10, 9-of-10 | 0.0371 → 0.0506 | 0.047349 → 0.063525 | significant → ns |
| `leaderboard-30m` | pro-high-text-3-of-5--flash-min-vf (t=0.15) | flash-high-text N=30 N=30, 26-of-30 | 0.0315 → 0.0410 | 0.041110 → 0.052911 | significant → ns |
| `leaderboard-30m` | text-baseline--flash-min-vf (t=0.15) | flash-high-text N=5 N=5, 5-of-5 | 0.0371 → 0.0465 | 0.047349 → 0.059019 | significant → ns |
| `results/pairwise/20m` `confirmatory`, group 7 | Flash HIGH text 26-of-30 | Flash HIGH text 9-of-10 | 0.0375 → 0.0357 | 0.050735 → 0.048300 | ns → significant |

Counts (same source):

| Figure | 2026-08-02 | 2026-10-30 |
|---|--:|--:|
| `leaderboard-20m` regenerated board, BH-significant | 199 of 253 | 198 of 253 |
| `leaderboard-30m` regenerated board, BH-significant | 181 of 231 | 178 of 231 |
| Tiers (both boards) | 8 and 8 | 8 and 8 |
| `results/pairwise/20m` `confirmatory`, significant (23 retained) | 16 | 17 |
| `results/pairwise/30m` `confirmatory`, significant (23 retained) | 15 | 15 |
| Factor analysis `temperature`, significant (2 retained) | 1 | 1 |

No retained condition changes tier on either board; the tier memberships in
`tiers.csv` are identical at the two commits. Thirteen retained conditions'
F1 values move at each buffer. This agrees with the S164 record's sixteen
moved rows at 20 m once the three dropped `flash-min-text-t10` cells are
taken out. Each board's `leaderboard.md` changelog lists the moves.

**Where the four board flips come from.** None of them is new to this
regeneration. Each is a flip in the restated full run that carries into the
retained set. The comparison is the full runs' own BH artefacts,
`fdr/pairwise_results_fdr.json` at `bc45133b4` against today's:

- at 20 m the full run has two opposite flips (the S164 record's "two pairs
  flip in opposite directions"). One is the 20 m pair above (q 0.04715 →
  0.056875). The other, `flash-min-text-t10 N=30` against
  `single-pass-t0 N=5` (q 0.050949 → 0.049547, ns → significant), involves
  a cell E72 drops.
- at 30 m the full run's three flips (243 → 240) are exactly the three
  30 m pairs above.
- the 26-member families at 20 m and 30 m have no flips.

**Unchanged.** The E72 drop still flips one pair within each revision, and
it is the same pair in both: #1 against #2 at 20 m
(`flash-high-text-16-of-30--flash-min-vf (t=0.2)` against
`flash-high-text-4-of-5--flash-min-vf (t=0.15)`, raw p 0.0398). It goes from
significant to not significant as the family shrinks: q 0.0488 → 0.0503 in
March, and 0.0490 → 0.0506 today (`summary.md` § 3, line 45 at each commit).

## 3. The gates

### 3.1 What "reproduce" means, and the result

The committed E72 board was built at `bc45133b4` (the commit its manifests
and summary record). The reproduce gate builds those inputs in a scratch
tree: `results/pairwise/` and
`results/factor-analysis/factor_analysis_results.json` from `git archive
bc45133b4`. It adds today's `scripts/` as real-file copies and runs the
adapted script with `--revision 2026-08-02`. It then compares every output
file with the files committed in `2f3ef020a`. The comparison blanks only
the JSON `timestamp` and `git_commit` values and the commit hash in
`summary.md`'s "Produced" line. Every other byte must match. Harness:
`e72-group7-scripts/reproduce-march.sh` with
`compare_board_outputs.py`.

**Result: 16 of 16 files identical**, with no file missing or extra. The
2026-08-02 script gives the same result on the same inputs, so the
comparison itself was checked first. On these inputs the adapted gates also
pass: Gate B reads 265 and 243 from the March runs' own artefacts and
confirms nine tiers, and the new family p-value check passes.

### 3.2 On the restated inputs (`fac61ebfe`)

- **Dated records**: 100 March records are each read through today's run
  beside them under `results/rescore-2026-10-15/pairwise/`: 49 in
  `leaderboard-20m/group_8/`, 47 in `leaderboard-30m/group_8/`, and two each
  in `20m/` and `30m/` `group_1_architecture/`. This matches the README
  there. Each record names the same test as the run beside it and is the
  older of the two, and no beside file is an orphan. Another 45, 36, 8 and 8
  per-pair files carry March timestamps but have no run beside them. These
  are the pairs that did not move, and they are read in place as current;
  the script identifies a record by its beside run, never by its timestamp.
- **Gate A**: both boards' per-pair files equal their committed
  `run_manifest.json` (pair set, raw p, ΔF1). Every family's raw p equals
  its per-test file's.
- **Gate B**: the full boards reproduce their own runs' BH artefacts. That
  is 265 of 325 significant at 20 m and 240 of 300 at 30 m, with every
  pair's adjusted value within 1e-6, and nine tiers each.
- **Gate C**: every condition's F1, precision, recall and detection count
  agree across today's runs.
- **Gate D**: replaying the published 20 m rank order reproduces the
  published tier sizes (1, 6, 3, 2, 4, 4, 1, 3, 2).

## 4. What changed in the script (`27454299f`)

The PI's specification, as implemented:

- **Gates A and C accept the dated March records beside today's runs.** The
  loader (`resolve_group_files`) reads the beside run in place of each dated
  record, after `check_dated_record` confirms the two are the same test
  (labels in order, group, question, family, buffer, permutations, seed) and
  the record is the older. A beside file with no record next to it is
  refused. Both gates then see one vintage.
- **Gate B takes the count from today's run.** `check_full_board_gate` reads
  each board's own `fdr/pairwise_results_fdr.json`. It requires the same
  significance count (240 at 30 m today; the March run gives 243) and every
  pair's adjusted value. The tier count stays pinned at the published 9.
  Reading the count from the run, rather than pinning 240, lets the same
  code pass on both vintages, which the reproduce gate needs.
- **The renderers keep the revision banner.** A `REVISIONS` registry drives
  every banner and changelog. The 2026-10-30 revision's documents carry a
  new banner naming their predecessor, and a `## Changelog` whose newest
  entry gives the before → after figures. Those figures are computed against
  the 2026-08-02 outputs, read with `git show 2f3ef020a`. The
  original-publication stub follows. `--revision 2026-08-02` renders the
  original revision verbatim. Each revision declares the input layout it
  expects, and the script refuses a mismatch.

Beyond the specification, each change needed to keep a regenerated document
true:

- **§ 3.1's quoted figures are now computed.** The 2026-08-02 renderer held
  four literals: F1 0.778, "the 0.814 clique", F1 0.797, and q = 0.046.
  Three are stale on the restated inputs, which give 0.814–0.816, 0.799 and
  0.044. The script now computes them and asserts the paragraph's structure.
  On the March inputs the computed paragraph is the old one, byte for byte.
- **The MCC sentence no longer asserts the March column.** The 2026-08-02
  `leaderboard.md` said the dated snapshot's tile-level Matthews correlation
  coefficient (MCC) column "remains valid for these rows". After the
  restatement, the retained rows' mound-level metrics differ from that
  snapshot's, and nothing here establishes whether tile MCC moved with them.
  The 2026-10-30 text says the column predates the restatement and is not
  asserted current.
- **Families' p-values are cross-checked.** Each family artefact's raw p must
  equal the per-test file's (today's run where a record is dated). This
  guards the very p that settles Group 7.
- The JSON manifests of later revisions gain `provenance.revision`. It lists
  every dated record and the run read in its place, and `version` becomes
  1.1.0. The original revision's schema is unchanged.

## 5. Tests and the red sentinel

`tests/test_regen_e43_board_restated_layout.py` adds 19 tier-1 tests. They
use synthetic trees of real files under `tmp_path`, with the module's
`BASE_DIR` monkeypatched. The 17 existing tests in
`tests/test_regen_e43_board.py` are untouched and pass. `ruff check` is
clean on the touched Python.

Harness: `e72-group7-scripts/red-sentinel.sh`, which copies everything as
real files and checks that the copy holds no links.

| Script under test | Result |
|---|---|
| 2026-08-02 (`git show 2f3ef020a:scripts/regen_e43_board.py`) | 18 failed, 18 passed: 18 of the 19 new tests fail; all 17 old tests pass |
| adapted (`27454299f`) | 36 passed |
| adapted, mutated to read the in-place record instead of the beside run | 3 failed |
| adapted, mutated to always write the 2026-08-02 banner | 1 failed |

The old script fails on behaviour, for each gate's own reason:

- Gate A: "p-value mismatch for ['s', 'x']: 0.0001 vs 0.0002".
- Gate C: "inconsistent f1 for 'x': 0.8 vs 0.81".
- Gate B: "recomputed 36 significant, published snapshot says 243".
- The record checks and the family p check: "DID NOT RAISE".
- The banner: it renders "2026-08-02 (original publication".

The remaining failures are tests of functions the old script lacks. The one
new test that passes on the old script is
`test_gate_b_refuses_a_count_the_run_does_not_hold`, which the old Gate B
also refuses, for its own reason.

## 6. Surprises, flagged

1. **The flip reverses.** Every committed statement that E72 turned Group 7
   non-significant is now stale (§ 7). The size of the move is small: raw p
   fell by 0.0018 and the q crossed 0.05 by 0.0017 (0.0483). The row sits at
   the 0.05 edge in both revisions.
2. **Four board pairs lose significance, all in the same direction, and none
   is in the brief.** Each one's raw p rose (by 0.0086 to 0.0135). One of
   them, at 30 m `flash-high-image-3-of-5--flash-min-vf (t=0.15)` against
   `flash-high-text N=10 N=10, 9-of-10`, now has raw p 0.0506, above 0.05
   before any correction. All four were already in the restated full runs
   (§ 2), but the committed E72 board still counted them as significant.
3. **The 2026-08-02 renderer would have printed stale numbers.** If its gates
   had let it run on the restated inputs, § 3.1 would have kept 0.814, 0.797
   and 0.046 (§ 4).
4. **A second inversion in the published 20 m order.** On the restated F1
   values, ranks 8 and 9 are also out of order:
   `text-baseline--flash-min-vf (t=0.15)` has F1 0.814 and
   `flash-high-text N=30 N=30, 26-of-30` has 0.816. The two share a tier
   under either order, and Gate D still passes. The generated § 3.1 now says
   so.
5. **The family's name.** The brief calls the 20 m Group 7 family
   exploratory, but its artefact names it `confirmatory`
   (`results/pairwise/20m/fdr/pairwise_results_fdr.json`, field `family`).
   Nothing was changed; the label is reported as the artefact gives it.

## 7. Documents that quote the moved figures (not edited)

The brief excludes these from this job. They are listed so the main session
can plan the document changes:

- `results/paper-tables/pairwise_hypothesis_table.md` lines 21 and 35 (the
  E72 banner: Group 7 "non-significant (q = 0.0507)").
- `results/paper-tables/leaderboard_tiers_20m.md` line 29 ("199
  significant") and `results/paper-tables/leaderboard_tiers.md` line 27
  ("181 significant"). The S164 banners there already say that
  `results/e43-board-regen/` was not regenerated.
- `results/paper-tables/leaderboard-20m-annotated.md` line 471 ("199/253").
- `docs/notes/working-notes.md`, Observation 387 (table row at line 25101:
  Group 7 q 0.0488 → 0.0507).
- `docs/methodology/preregistration/protocol-errata.md` § E72 cites the
  regeneration but quotes none of these figures. It needs no figure change.
  Whether it should note the reversal is for the PI.

## 8. Not done

- No document outside the generated board was changed: the errata, findings,
  `docs/paper/`, `docs/notes/`, `planning/` and `results/run-analyses.json`
  are untouched. No pull request is open, and nothing is merged.
- **Full tier-1 suite not run.** The only importers of
  `regen_e43_board.py` are its two test modules (`git grep`), and all 36 of
  their tests pass. The full suite's roughly three minutes of CPU would
  belong on sapphire under the project rule, and was judged not to buy
  anything here.
- **Tile-level MCC** for the retained rows after the restatement was not
  checked (§ 4). It may belong with the queued MCC robustness job.

## Changelog

### 2026-10-30 — Original publication

First version, written with commits `27454299f` and `fac61ebfe` on branch
`e72-regen-2026-10-30`.
