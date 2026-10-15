# Fault-window re-checks by exact reproduction

> **Last revised**: 2026-10-15 (rows W2-3, W2-4, W2-7, and W2-8 added,
> PI ruling D67 (2)). See [§ Changelog](#changelog) for revision history.

- **Prepared by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), a background agent of the main Session 164 (S164)
  session, with five Opus 5.5 sub-agents, one per row group. 2026-10-14,
  00:31 to 04:19 UTC. Rows W2-3, W2-4, W2-7, and W2-8 were added on
  2026-10-15, 10:07 to 12:39 UTC, by a second background agent of S164
  (same model lane), with two Opus 5.5 sub-agents for W2-3, on branch
  `fault-window-rechecks-2`, cut from `origin/main` at `718d0ee08`.
- **Repository**: `map-reader-llm`, branch `fault-window-rechecks`, cut
  from `origin/main` at `90294a283`. Every re-run was on sapphire.
- **Task**: PI ruling D65, item D62 (7) "as recommended"
  (`planning/pi-decisions-2026-09-20.md`). Re-check the claim-bearing rows
  of `reports/s163-agent-records/fault-window-recheck-list.md` in its
  suggested order: W2-1 and W2-2; W1-1 to W1-4; the `--check` items W1-13
  and W2-13; the inputs W1-8 and W2-11 through the provenance and rebuild
  tools. Each must reproduce the committed file exactly. W1-5 and W2-9
  are to be marked done on PR #38's and PR #35's evidence. Report only.
  Then PI ruling D67 (2) (2026-10-15, "yes re-check"): rows W2-3 (the
  K-ladder Phase 2), W2-4 (the tile-MCC re-sweeps), W2-7 (the
  modality-audit recomputation), and W2-8 (the E70 interval registry),
  which the main session had dropped from its walkthrough summary, by the
  same method. Report only.
- **Guarantees**: no model Application Programming Interface (API) call
  was made. Every replay ran in a disposable git worktree, or in scratch
  copies, outside the live checkout. No committed result, output,
  document, or register row was changed. The branch adds this record and
  its scripts directory, plus a dated changelog entry (with verdict
  marks) in the fault-window list.
- **Drivers, logs, and comparisons**:
  `reports/s164-agent-records/fault-window-rechecks-scripts/<row>/`.
  Regenerated bulk outputs stay on sapphire under
  `~/scratch/s164-fw-recheck-2026-10-14/*-out/` (not committed); those of
  2026-10-15 under `~/scratch/s164-fw-recheck2-2026-10-15/*-out/`.

## Bottom line

Every re-checked row reproduces exactly. There is **no unexplained
difference** in any fault-window file checked, so no claim, signature, or
ruling needs to change on fault-window grounds.

- **W2-1 and W2-2** (the Gemini 3.7 image test family behind D53, and
  the r2 boards behind the headline): every file reproduces at its
  generating commit, byte for byte. Two replicate `tests.json` files have
  key order that follows the hash seed. They match field for field, and
  byte for byte under a recovered seed. D53's P3 (0.919904 against 0.884825,
  +0.035079, BH p < 0.0001) and the board's 0.8871, 0.8848, and 0.8827
  are confirmed from the regenerated files.
- **W1-1 to W1-4** (the D42 p values, in W1): all 39 files reproduce. 36
  match byte for byte, or after setting aside timestamps and machine
  paths. The other 3 also differ in run timings, worker count, and
  completion order. No numeric value differs.
- **W1-13 and W2-13** (register projections and smaller items): the four
  manifests and the 2026-10-08 union sweep reproduce, and so do all six
  W2-13 commits.
- **W1-8 and W2-11** (inputs): every input that can be rebuilt without
  API spend reproduces. For W1-8 that is 100 of Run B's 331 non-log
  files. For W2-11 it is the r2 materialisations (55 of 55), the union
  and consensus rebuilds, and 33 image-campaign files. The rest are raw
  API outputs: NOT CHECKABLE without spend, and none was spent.
- **W1-5 and W2-9** are marked done on PR #38's and PR #35's evidence, as
  D65 directs.

The kernel's "Bad page state" count on sapphire was 0 before the first
re-run (2026-10-14T00:31Z) and 0 after the last (2026-10-14T04:19Z), on
the boot that began 2026-10-10T05:09:43Z with the memory at JEDEC
4,800 MT/s (D59).

**Added 2026-10-15 (D67 (2)): rows W2-3, W2-4, W2-7, and W2-8.** Every
file in them that can be regenerated without API spend reproduces at its
generating commit. Again there is **no unexplained difference**.

- **W2-3** (the signed K-ladder): of 920 files last written in W2 by the
  K-ladder's commits, 512 reproduce byte for byte or field for field,
  324 are cell evaluations the census already verifies, 66 are real-time
  verifier outputs (NOT CHECKABLE), and 18 are prose or code. That
  includes the two registered cells of W2-14 whose intervals and tile MCC
  the census could not reproduce: re-scored at their own commit, every
  number reproduces. The MCB sets reproduce exactly, so the list's "within
  4.958e-05 (a tolerance, not exact)" caveat can be dropped. The four tier E cells and the other S9
  movers reproduce their pre-D50 values at their generating commits, so
  their later moves are D50's scorer, not the fault window.
- **W2-4** (D6a's tile-MCC record): all 52 files reproduce byte for byte at
  their own commits: the 23 tile-MCC re-sweep CSVs (2,048 points),
  `sweeps.json` as each of the three commits that rewrote it left it, the
  27 post-hoc cells' detection sets, and `cells_manifest.json` as each of
  the four commits that rewrote it left it.
  Every family's tile-MCC argmax sits at the lowest vote count its sweep
  offers, as D6a says.
- **W2-7** (R2-06): all ten files reproduce, eight byte for byte and two
  after `generated_at_utc`. The image-bearing tile MCC range 0.0665 to
  0.2907 is confirmed.
- **W2-8** (the interval registry): both stores are byte for byte the
  committed file once the 85 re-run entries' `recomputed_at` and
  `elapsed_seconds` are copied in.

Kernel "Bad page state" count: 0 at 2026-10-15T10:07:58Z, before the
first replay, and 0 at 2026-10-15T12:38:40Z, after the last, on the same
boot.

## 1. Method

1. **The machine.** Sapphire on its current boot (since
   2026-10-10T05:09:43Z), with the memory fixed and the 467-replay soak
   passed (D59). The numerical libraries in the project's virtual
   environment (Python 3.13.3; numpy 2.4.3, scipy 1.17.1, pandas 3.0.1,
   shapely 2.1.2, geopandas 1.1.3, pyproj 3.7.2) were installed on
   2026-03-25 and have not changed since. So every replay used the same
   library versions as the September and October runs, and there is no
   library-version caveat.
2. **Replay at the generating commit.** Each file was regenerated with the
   code of the commit that produced it, in a disposable
   `git worktree add --detach` tree (real copies, never symlinks), and not
   with today's code. Later deliberate changes would otherwise show up as
   differences: D50's per-sheet scoring, D62 (1)'s origin route, D63's
   sorted bootstrap order, and the `_repaired` verifier legs. Where an
   original run read inputs that were committed slightly later, or patched
   a hard-coded root, the section says so.
3. **Comparison.** Each regeneration was compared byte for byte with
   `git show <generating commit>:<path>`. Where bytes differed, it was
   compared field by field, setting aside only the fields named in the
   section (timestamps, machine paths, run timings). For every file the
   check also asks whether today's committed file (at `90294a283`) is
   that version. If later commits changed it, a structured diff shows
   those changes to be the documented non-computational edits.
4. **Hash seed (D63).** No bootstrap interval differed anywhere, so no
   hash-seed explanation was needed. One cosmetic case (key order only) is
   in W2-1 note (c).
5. **Limits.** At most 8 worker processes (two other agents shared the 24
   cores). Long jobs were launched detached with all three descriptors
   redirected and a pid file. Liveness was checked with `kill -0` and log
   staleness, never `pgrep -f`.
6. **Second runs.** The brief asks for a second independent run of
   anything that DIFFERS. Nothing did. Some files were nonetheless
   produced more than once. W2-1's test family ran under two hash seeds
   and gave the same bytes both times. The 3.7 inheritance sweeps and
   cells came out byte-identical at three successive commits (`62b13e6fd`,
   `58500a739`, `2ba1914b6`).
7. **Lint after the runs.** Eleven Python scripts were reformatted after
   they had run: long lines wrapped to the 100-column limit, and three
   one-line `a; b` statements split. Nine are comparison or search
   helpers. Two produced regenerated files (`w1-2_annotate.py` and
   `w1-3_feb_compare.py`). `lint_ast_check.py` shows that each edited
   file has the same docstring-free syntax tree as before, so each is the
   same program (`lint-ast-check.txt`, with a red sentinel).

## 2. Verdicts

| Row | What | Generating commit(s) | Verdict |
|---|---|---|---|
| W2-1 | Gemini 3.7 image 55-map statistics: test family, sweeps, materialised cells, K = 5 replicates, inheritance (both rows) | `e0f9a4d03`, `392a06933`, `8d800f2d6`, `0569b0d2f`, `7351bcce8`, `62b13e6fd`, `58500a739`, `3fc3f0751`, `2ba1914b6`, `a14d218ee` (and arm 1's `82020b941`, `d1134a707`, `321dd4549`) | **VERIFIED** (byte for byte; two replicate `tests.json` field for field, byte for byte under a recovered hash seed) |
| W2-2 | 55-map r2 boards: final board, 50 m leaderboard, MCC tiering (+ `.md`, figure) | `22353e660`; addendum `de009ed5d`, `892633660`; cost `b044c486e` | **VERIFIED** (byte for byte) |
| W1-1 | D42 p values: `grid_analysis`, `verifier_analysis`, `incumbents_common_footprint`, `stride_verifier_analysis` | `5986316b5` (code `7aef6d2ff`) | **VERIFIED** (byte for byte after `generated_at_utc`) |
| W1-2 | Retest phase annotations (9 files, 61 rows) and the annotation summary | `5f02cfbc2` | **VERIFIED** (byte for byte) |
| W1-3 | February 60-tile re-test (8 phase files, `comparison.json`) | `35f9814d7` | **VERIFIED** (byte for byte after timestamp and study path) |
| W1-4 | D42 class B: 7 annotated files, 9 re-run records | `e7b32de0b` (re-run at `7121c969f`) | **VERIFIED** (annotated files byte for byte; records field for field) |
| W1-5 | W2.7 / W7.6 floors | PR #38, merged `446171b97` | **DONE** (D65), on PR #38's evidence; residue noted |
| W1-13 | Register projections and the union sweep | `0a08eedc9`, `c117cd012`, `e5f702d2c`, `20e0be0d3`, `69df3b5d4`, `da86896c4` | **VERIFIED** (manifests byte for byte; sweep field for field); the authored inputs validated |
| W2-9 | h6 A-06 and A-09 | PR #35, merged `3a5e5c453` | **DONE** (D65), on PR #35's evidence |
| W2-13 | Tile-join audit, June pool grid, union-staleness retrospective, frontier, tile-presence costs, register regeneration | `3d6b47e33`, `4ac321a79`, `30609d5c8`, `61870d9e7`, `6fc63546e`, `7c9499846` | **VERIFIED** |
| W1-8 | Run B inputs, `outputs/modality-bridge-2026-10-07/` | `92b151058`, `2718be084`, `60aceebdd`, `987718a66`, `2b6edde9a`, `a3ea389c2`, `94be8b01a`, `69eb32132`, `2cff16c91` | **VERIFIED** for all 100 checkable files (90 byte for byte, 10 metas field for field); 212 raw API outputs **NOT CHECKABLE** |
| W2-11 | Inputs written on sapphire in W2 | `7894b5b5a`, `e9d1db0d0`, `185681674`, `e01b8617a`, `e7ebc1695`, `c053f5a41`, `43516df9a`, `f8e0eb600`, image campaigns | **VERIFIED** for every checkable file; raw API outputs **NOT CHECKABLE** |
| W2-3 (2026-10-15) | K-ladder: Phase 2 unions, verifier stages, materialisations, carried points, recovery fix, tier E, MCC test, MCB, tiering | `e3232d65b`, `19e56ed80`, `eb6d797e0`, `326181bcd`, `9457b2689`, `d10137595`, `d900ed1d5`, `b7e2821ba`, `98e54baf6`, `5167b9a5c`, `741a4eaff`, `f31e7470e`, `3d9c64807`, recovery fix `20c0a053f` to `a8c03bb9e`, small items | **VERIFIED** for every checkable file (512); 66 real-time verifier outputs **NOT CHECKABLE**; 324 evaluations census-verified |
| W2-4 (2026-10-15) | r2 board tile-MCC re-sweeps of 23 families; carried-analogue and MCC-oracle cells; carried-k record; relabel | `a1c4bf2c3`, `03b8496ed`, `cca6ccda5`, `1ed3e54cb`, `539372938`, `681b4e246`, `1bbba2e21` | **VERIFIED** (all 52 byte for byte) |
| W2-7 (2026-10-15) | Modality-track audit recomputation | `d5eaeb1ee`, `aa1d9bd5b` | **VERIFIED** (8 files byte for byte, 2 after `generated_at_utc`) |
| W2-8 (2026-10-15) | E70 bootstrap-interval re-run, both stores; the registry's figures | `8c89ccebb` | **VERIFIED** (byte for byte after `recomputed_at` and `elapsed_seconds`) |

## 3. Per-row detail

### W2-1 — Gemini 3.7 image 55-map statistics

Sub-agent, drivers and comparisons in `fault-window-rechecks-scripts/w2-1/`
(`run-01…09*.sh`, `run-inherit.sh`, logs, `compare_files.py`,
`check_sweeps_json.py`, `later_edits_diff.py`, `hashseed_search.py`,
`cmp-*.json`, `chk-sweeps-json-*.json`, `diff-*-later-edits.json`,
`patch-*.diff`). Paths below are under
`results/gemini37-image-55map-2026-09-13/` unless stated. The driver is
`scripts/gemini37_image_55map_r2.py` with `--workers 2`; the evaluations
were not re-scored (census-verified).

| Files | Generating commit → replayed at | Stage | Result |
|---|---|---|---|
| Four K1/K3 sweep CSVs, `sweeps.json` and `cells_manifest.json` as of `e0f9a4d03`, 12 K1/K3 `detections.geojson` (18) | `e0f9a4d03` → `b9d4032bb` (note a) | `sweep`, `materialise` | 18 of 18 byte-identical |
| `tests_IMG-ARM2-K3-carried.json`, the five-test family | `392a06933` → `b9d4032bb` | `tests`, under hash seeds 0 and 12345 | byte-identical both times (sha256 `bf3b02b7…`, which I re-hashed against the git blob); today's file is this blob |
| Two K5 sweep CSVs, 6 K5 detections, the K5 merge into `sweeps.json` and `cells_manifest.json` | `8d800f2d6` → `8d800f2d6` | `sweep --rungs 5`, `materialise --rungs 5` | 10 of 10 byte-identical |
| Arm 2 K = 5 replicate: `agreement.json`, `sweeps.json`, `cells_manifest.json`, sweep CSV, 2 detections | `0569b0d2f` → `0569b0d2f` (note b) | `replicate_k5_arm2.py --stage agree`, `materialise` | 6 of 6 byte-identical; today's files are these blobs |
| Arm 2 replicate `tests.json` | `7351bcce8` (run on amd-tower) → `7351bcce8` | `--stage tests` | field for field with nothing ignored under seeds 0 and 12345; byte-identical under seed 202 (note c) |
| 3.7 inheritance: `ladder.json`, 4 sweep CSVs, 4 detections, `cells_manifest.json` | `62b13e6fd` → `62b13e6fd`, then `58500a739` and `2ba1914b6` for the later `ladder.json` versions | `inheritance_ladder.py --stage ladder` (and `separation` at `2ba1914b6`) | byte-identical at every step; today's `ladder.json` and `union_separation.json` equal the `2ba1914b6` regeneration |
| 3.7 inheritance `tests.json` | `3fc3f0751` → `3fc3f0751` | `--stage tests` | byte-identical; today's file is this blob |
| Gemini 3 inheritance row (`results/gemini3-image-55map-2026-09-16/inheritance-2026-09-20/`): `ladder.json`, `union_separation.json`, 4 CSVs, 4 detections, `cells_manifest.json` | `2ba1914b6` → `2ba1914b6` | `--stage ladder --campaign g3`, `--stage separation --campaign g3` | 12 of 12 byte-identical (note d) |
| Gemini 3 inheritance `tests.json` | `a14d218ee` → `a14d218ee` | `--stage tests --campaign g3` | byte-identical |
| Arm 1 K = 5 replicate (not named in the row; same family): `agreement.json` at `82020b941` and `321dd4549`, `sweeps.json`, `cells_manifest.json`, CSV, 2 detections, `tests.json` at `d1134a707` | each at its commit | `replicate_k5_arm1.py --arm arm1` | byte-identical; `tests.json` field for field under seeds 0 and 12345, byte-identical under seed 124 |

Today's `sweeps.json` and `cells_manifest.json` carry later edits, each
checked by structured diff. In `sweeps.json`, `4a8d157cb` added the
`mcc_argmax_unconstrained` blocks (78 leaves) and moved IMG-ARM2-K3's MCC
row, and `1bbba2e21` is exactly the key rename `mcc_oracle` →
`mcc_argmax_at_carried_k`. In every committed version, each block equals,
leaf for leaf, the row of the verified sweep CSV that the version's
documented selection rule picks. In `cells_manifest.json`, `2645e499c`
re-pointed IMG-ARM2-K3-mcc-oracle from (0.96, k2) to (0.90, k3) and kept
the old cell as `-unconstrained`, `67e7b8a12` added `rescored_in_place`
text, and `1bbba2e21` changed `basis` and `presentation` text on seven
cells. The re-pointed MCC-oracle detections are byte-identical to the
reproduced IMG-ARM2-K3-f1-oracle file (the same point), and the
`-unconstrained` detections to `e0f9a4d03`'s original MCC-oracle file.

**D53 reproduced exactly.** In the regenerated family, IMG-ARM2-K3-carried
scores 0.919904 against ARM2-N3-oracle 0.884825, +0.035079, p 0.0 and BH
p 0.0 over 10,000 permutations on 8,541 tiles (I read these from the
committed file, which the regeneration equals byte for byte). The arm 2
carried ladder from the reproduced sweeps: 0.8719, 0.9199, 0.9270.

Notes:

- (a) `e0f9a4d03` ran while its K1/K3 verifier inputs were on disk but
  untracked; they were committed 35 minutes later in `b9d4032bb`. The
  driver blob and every input the stages read are unchanged between the
  two commits, so the replay used `b9d4032bb`, and the byte-identical
  outputs confirm those committed inputs are the ones used.
- (b) The replicate and inheritance drivers hard-code
  `PROJECT_ROOT = Path("/home/shawn/Code/map-reader-llm")`. Run unchanged
  they would have read and written sapphire's shared checkout, so that one
  line was changed to resolve from the script's own path (what `55ff8a02e`
  later did); each change is in `patch-*.diff`.
- (c) The replicate drivers fill a cache by iterating a Python set of cell
  labels, so the key ORDER of `n_detections` and `tile_confusion` in the
  two replicate `tests.json` files follows `PYTHONHASHSEED`; no value does.
  Seeds that reproduce the committed order were found by search
  (`hashseed_search.py`) and confirmed by real driver runs. This is
  cosmetic and is not the D63 bootstrap effect (these files hold
  permutation tests only). The sub-agent disclosed and corrected one bug
  in its first search tool (it spawned interpreters with `-I`, which
  ignores `PYTHONHASHSEED`; one apparent match was by chance, and that run
  was redone).
- (d) The Gemini 3 crop manifests these stages read
  (`outputs/gemini3-image-55map-2026-09-16/verifier/g384_ov192_55map_g3img/crops_k{1,3,5}/candidate_manifest.json`)
  were never committed. Read-only copies were taken from sapphire's main
  checkout, where they sit untracked with modification times
  2026-09-19T00:26 to 00:37Z (in W2). The byte-identical outputs show they
  are the files used, but they are uncommitted inputs written in W2 (§ 4).

### W2-2 — the 55-map r2 boards

Sub-agent, drivers and comparisons in `fault-window-rechecks-scripts/w2-2/`
(`replay.sh`, `replay_addendum.sh`, `replay_cost.sh`, `crossread.py`,
`jsondiff.py`, `mdtables.py`, logs, `summary.json`).

- **Rebuilt at `22353e660`**, the step 4e commit, in a disposable tree:
  `scripts/final_board_build.py --reference r2` (00:40–01:07Z, round-robin
  tile-swap of 10,000 permutations, seed 42, BH q = 0.05 over 595 pairs),
  `scripts/build_55map_leaderboard.py --reference r2`, and
  `scripts/mcc_tiering_55map.py --reference r2`. All seven outputs are
  byte-identical to `git show 22353e660:<path>`: `final_board_50m.json`,
  `final-board-50m.md`, `significance-groups.png`,
  `55map_leaderboard_50m_r2.json` and its `.md`, and
  `55map-mcc-tiering-r2.json` and its `.md`. I re-hashed the three JSONs
  against the git blobs myself (sha256 prefixes `441978aad9860380`,
  `f864e33a594fe356`, `33d179560984ea62`). The builder's own gates passed
  on the way: G3 reproduced the 8-cell r1 board (F1, 28 p values, 5 tiers),
  and the TH7, IM, and UPL coincidence gates matched (0.8380, 0.8008,
  0.8274).
- **Headline, read from the regenerated board**: ARM2-N5-oracle 0.8871
  (group a) and ARM2-N3-oracle 0.8848 (ab), ARM2-N5-carried 0.8827 (bc);
  12 tiers; 595 pairwise rows.
- **Later commits.** The addendum writer
  (`scripts/final_board_addendum_render.py`) replayed at `de009ed5d` and at
  `892633660`, each from its parent's board, and the cost refresh
  (`scripts/final_board_cost_refresh.py --write`) replayed at `b044c486e`,
  give byte-identical JSON. Their `.md` differences are the hand-written
  banner and changelog lines the commit bodies describe. Against today's
  `final_board_50m.json`, the regeneration differs in 74 leaves, all under
  six keys the later commits own: `addendum`, `addendum_cells`, each cell's
  `cost_usd` and `cost_basis`, `cost_axis`, and `efficiency_frontiers`.
  Ignoring only those keys, 0 leaves differ: tiers, groups, every cell value
  and all 595 pairwise blocks are as regenerated. The leaderboard and MCC
  tiering JSONs are still the `22353e660` blobs; the leaderboard `.md`
  gained only a two-line generated-file banner (`80e897049`).
- **Cross-read (a).** Every board cell (35 tiered, 8 and 8 on the two
  leaderboards, and today's 7 addendum rows) equals the census-verified
  `evaluation.json` it cites on F1, interval, precision, recall, MCC, and n
  (MCC board: MCC, interval, sensitivity, specificity, confusion matrix).
- Not replayed: the writers of `cc6d9537f` and `1bbba2e21` (the addendum
  rows they left were cross-read exactly instead).

### W1-1 to W1-4 — the D42 permutation-test regenerations

Sub-agent, drivers and comparisons in `fault-window-rechecks-scripts/w1-1-to-4/`
(`w1-1_regen.sh`, `w1-1_splice.py`, `w1-2_regen.sh`, `w1-2_annotate.py`,
`w1-3_feb.sh`, `w1-3_feb_compare.py`, `w1-4_classb.sh`, `w1_compare.py`,
`w1-4_conform_check.py`, `netguard/sitecustomize.py`, results and
`run-logs.txt`). The order of the original steps was read from the
Session 161 transcript in the session archive
(`~/cc-archives/map-reader-llm/2026-10-05T05-59_d2c550e4/`), and replayed
in that order. The original drivers wrote into the live checkout and
`/tmp`; adapted copies wrote only to scratch. Every replayed process loaded
a network guard that refuses Internet connections.

- **W1-1** (`5986316b5`): `grid_analysis.py --bootstrap 10000`,
  `grid_incumbent_rescore.py`, `grid_verifier_analysis.py`, and
  `stride_verifier_analysis.py` at `7aef6d2ff`, then the two hand splices
  the transcript records (`verifier_analysis.json`'s `conditions`,
  `grid_analysis.json`'s `verifier_costing`, both carried from the
  pre-existing committed files, as originally). All four files are
  byte-identical to `5986316b5`'s after substituting `generated_at_utc`, the
  only differing leaf in each (`w1-1_bytecheck.txt`). Every p field behind
  the signed rows `grid-tilesize-overlap-2026-08-18` and
  `grid-postverifier-2026-08-18` and the stride findings is exact. The
  hash seed was unpinned, as originally, and the files still match.
- **W1-2** (`5f02cfbc2`): `evaluate_retest_all.py --phase <key>` for the
  nine phases at `7aef6d2ff`, then the annotator reading the pre-annotation
  committed files. All nine `results/retest/phase2*-evaluation.json` and
  `results/d42-retest-2026-10-05/retest-annotation-summary.json` are byte
  for byte identical, the note's embedded hash `7aef6d2ff` included. The
  annotator's printout matches the original: 61 rows, 4 verdict changes,
  maximum F1 drift 0.0059. I re-hashed `phase2a-evaluation.json` against
  the git blob myself (`a338ad61…`).
- **W1-3** (`35f9814d7`): the February step on a fresh copy of the tracked
  archive, including the mid-run repair the transcript records (100 Phase
  2b files renamed and the Phase 2e links re-pointed at 07:04:47Z, then
  four analyses re-run). The eight phase files are byte-identical after
  substituting `analysis_timestamp` and `study_dir`
  (`w1-3_bytecheck.txt`); `comparison.json` is byte-identical. The four
  contrasts significant after BH are reproduced (2b text T0.3/T1.0 and
  T1.0/T1.3; 2e config-default/random and canonical-last/random). The
  intervals match too, with the hash seed unpinned as originally.
- **W1-4** (`e7b32de0b`): the class B runner (`run_classb.sh`, adapted,
  `PYTHONHASHSEED=0` as originally) at `7121c969f` (sapphire's HEAD at the
  original launch), then the annotator `annotate_classb_permutation.py
  --write` (which had run on amd-tower). The seven annotated files
  (`fair-384-vs-512.json`, `pairwise-384px.json`, the two
  `pro-proposer-verifier-thinking-*/comparison.json`, both
  `pairwise-effect-sizes*.json`, `phase3a-high-text-pairwise.json`) are byte
  for byte identical; I re-hashed `fair-384-vs-512.json` against the git
  blob myself (`e31da98d…`). Of the nine re-run records under
  `results/d42-retest-2026-10-05/class-b/`, two are byte-identical and
  seven equal field for field once machine paths (`dir`,
  `probabilities_file`, `manifest_file`), per-comparison `elapsed_seconds`
  and `metadata.total_elapsed_seconds`, `metadata.workers` (8 then, 2
  now), and completion-order list or key order are set aside
  (`w1-4_conform.txt`); no numeric value differs. The D43 and D44
  quantities reproduce: B-17 p 0.0047 and the re-sweep's 0.0067, I4 p
  0.007, E39 F1 0.7701 at p 0.0111, the 0.0527 raw-alpha flip, B-18
  0.1626. The untracked class B input `~/cc-scratch/bootstrap-cis` passes
  `md5sum -c` on all 570 entries of the archived inventory.
- Counts, for the list: W1-4's "16 JSON" are 9 under `class-b/` plus the 7
  annotated files; W1-3's "11" are the 8 phase files, `comparison.json`,
  and the annotation summary (under W1-2), the rest being scripts and a
  timing log. In all, 39 files were compared (4 + 10 + 9 + 16; the
  sub-agent's report said 44, a miscount I corrected from its comparison
  files): 36 match after setting aside only timestamps or machine paths,
  and 3 (the two pairwise-effect-size records and the Phase 3a pairwise
  record) also after setting aside run timings, the worker count, and
  completion order. Today's version of every one of the 39 equals its
  generating commit's.

### W1-5 — W2.7 / W7.6 floors: done (D65)

Marked done on PR #38's evidence, as D65 directs. PR #38 merged as
`446171b97`. Its 2026-10-13 regeneration (`reports/w27-replicate-floors-2026-10-06.md`
§ Changelog, entry "2026-10-13 — §§ 6 and 6b regenerated with cluster
origins"; drivers and comparisons in
`reports/w27-replicate-floors-2026-10-06-scripts/floors-v2/regen-2026-10-13/`)
ran § 6, the scorer gate, § 6b, the gold-standard slices, and the floors
analysis twice on the fixed boot at `533e62605`. The two runs agree byte
for byte on every output (`r1-vs-r2.json`), a third process set recomputed
a seeded 10 % of § 6b with 0 mismatches, and the kernel count was 0 before
and after (`kernel-bad-page.txt`). Its run 1 also equals, byte for byte,
W1-era files that are still committed: § 6's `gates.json` (`c84cfa378`)
and the gold-standard slice files from `a4b5734cb` (`gs_k10_check.csv`,
`gs_k10_summary.csv`, `gs_validation.csv`, `gs_validation_summary.csv`;
`r1-vs-pr38-committed.json`).

Residue, recorded but not acted on: five files in the W1-5 group were not
part of that regeneration and remain as written in W1. They are the § 3
gold-standard consensus floors from `c84cfa378` (`gs_consensus_cells.csv`,
`gs_consensus_pairs.csv`, `gs_gates.json`), and `vdate-results.json` and
`vdate-results-extra.json` (`3a1ce64eb`). The list's overnight evidence
says § 3's 486 coincident cells reproduce. `runA/runA_results.json`
(`b56300cdc`) belongs to W1-6, outside this ruling's scope.

### W2-9 — h6 A-06 and A-09: done (D65)

Marked done on PR #35's evidence, as D65 directs. PR #35 merged as
`3a5e5c453`. `results/h6-registered-analyses/a06_decision_rule.json` was
regenerated by `046d5efc1` and `a09_cost_gate.json` by `e177d4b97`
(both 2026-10-12, on the fixed boot), each produced twice, byte-identical
apart from timestamps (the list's overnight evidence). Today's files are
those commits' blobs (`04d2c4bbb593`, `3fd003f516f0`; the later merges did
not change them). The W2 versions of `cd8dc5591` are superseded. Both rows are re-sign-pending for the PI
(D62 (3), (4)).

### W1-13 — register projections and the union sweep

Driver and logs: `fault-window-rechecks-scripts/w1-13/` (`run_manifests.sh`,
`manifests.log`, `manifests-sha256.txt`, `run_union_sweep.sh`,
`union-sweep-run1.log`, `compare_union_sweep.py`,
`union-sweep-compare-run1.txt`).

- **Manifests.** `scripts/generate_post_run_report.py --all --write` in a
  disposable tree at `90294a283` rebuilt every row from its inputs (44 runs,
  658 conditions, 1,455 passes, 71 analyses; ALL VALID). The generator
  carries `generated_at` and `last_extracted_at` forward only when a row's
  content is otherwise equal (`_stabilise_timestamps`), so a byte-identical
  file means the content reproduced field for field. `runs-manifest.json`
  (last written in W1 by `0a08eedc9` on sapphire), `passes-manifest.json`
  (`e5f702d2c`), `analyses-manifest.json` (the W1 version of `c117cd012`,
  since superseded by `2bba84ab5` on the fixed boot), and, unlisted,
  `conditions-manifest.json` all came out with the committed sha256. The
  five `.md` renderings differ only in the source-commit stamp
  (`d064e9d57` → `90294a283`), and `--check-renderings` passed before the
  rebuild.
- **Authored inputs.** `results/run-conditions.json` and
  `results/manipulation-gate-bindings.json` (`20e0be0d3`) and
  `results/run-analyses.json` (`69df3b5d4`, since `d064e9d57`) are
  hand-authored register inputs by their own `_README`s, committed from
  amd-tower, so there is no computation to reproduce. They validate: the
  generator's schema check passes, and `scripts/check_manipulation.py
  --all` ends in its documented steady state (exit 3: 47 PASS, 5 refusals
  all documented, 19 unverifiable).
- **Union sweep.** `scripts/check_union_provenance.py --all --workers 1`
  with the code of `da86896c4` (checker v1.1.0) in a disposable tree at that
  commit reproduced
  `reports/stale-register-notes-2026-10-07-union-sweep-2026-10-08.json`
  on all 106 unions with 0 differing leaves, ignoring only each union's
  `seconds` (wall time). Counts: 50 REPRODUCES, 29 STALE, 27
  SUBPOOL-CONSISTENT, as committed. Today's file is the `da86896c4` blob.

### W2-13 — smaller sapphire items

Sub-agent, drivers and comparisons in `fault-window-rechecks-scripts/w2-13/`
(`replay_*.sh`, `compare.py`, `job-*.log`, `cmp-*/`). Every run used one
worker with BLAS threads pinned to 1.

| Commit | Files | Replayed at, and command | Result |
|---|---|---|---|
| `61870d9e7` (frontier, "rebuilt on sapphire") | `pareto_v2.json` and `.png` (R6-01); K-ladder `ladders.json`, `phase2/{ladders,ladders-compat}.json`, `phase2/ladder-tables.md`, two figures | `61ab7a446` (the source commit stamped in `ladder-tables.md`; `scripts/` identical to `61870d9e7`'s): `build_pareto_v2.py`, `build_k_ladder_tables.py`, `build_k_ladder_phase2_tables.py` | `pareto_v2.json` and the three PNGs byte-identical; the other four equal after ignoring only `generated_at_utc` (JSON) and the banner's generation timestamp line. I re-hashed `pareto_v2.json` against the git blob myself (`762833e4…`); today's file is that blob |
| `2e0c2941d`, `32d0c6445` (today's Phase 2 files, later W2 rewrites on sapphire) | `phase2/{ladders,ladders-compat}.json`, `ladder-tables.md`, phase 2 figure | `5eaa8cb9f` and `9cab57ad9`, as stamped | PNGs byte-identical; the rest equal after the same timestamp ignores |
| `3d6b47e33` (tile-join audit; PI ruling 6) | `results/tile-join-audit/*-2026-09-12.{json,md}` (6) | `3d6b47e33`, `audit_tile_join_variants.py` with the three globs reconstructed from the committed rows (the commit body does not record them) | all 6 byte-identical; I re-hashed the board JSON myself (`b5279bdb…`) |
| `4ac321a79` (June image pool grid) | `sweep_IM-5pass.csv`, `grid.json`, `cells_manifest.json`, 4 `detections.geojson` | `4ac321a79`: `im_june_pool_grid.py --stage gate`, `sweep --workers 1`, `materialise` | all 7 byte-identical; today's `grid.json` and `cells_manifest.json` were later relabelled on amd-tower (`26cb1650d`, `e24b2d1a0`: a key rename and a note, values untouched) |
| `30609d5c8` (union-staleness retrospective) | `results/union-staleness-retrospective-2026-09-12.json` (106 rows) | `30609d5c8` (pre-`75d7c8d4c` merger): `check_union_provenance.py --all --workers 1` | equal on every field except the per-union `seconds`; counts 64 REPRODUCES, 36 SUBPOOL-CONSISTENT, 5 STALE, 1 UNRESOLVED |
| `6fc63546e` (tile-presence costs) | `verifier-costs.json`, `leaderboard.json`, `leaderboard.md` | `6fc63546e`: `build_tile_presence_board.py --stage all --check` (exit 0), then a real write of `costs` and `leaderboard` | all 3 byte-identical |
| `7c9499846` (register regeneration) | `rederivation-report.json`; the four manifest JSONs; register `.md` views; 39 post-run reports; the generated-file registry | `7c9499846`: `rederive_manifest_fields.py`, `generate_post_run_report.py --check-renderings` and `--all --write`, `generate_run_reports.py --all --check`, `build_generated_file_registry.py --check` | `rederivation-report.json` and the four manifests byte-identical; `.md` views differ only in the source-commit stamp; all three guards exit 0 |

Not re-checked here: the board part of `61870d9e7` (refreshed on amd-tower;
W2-2 covers today's board), the June grid's four evaluations (census
reproduces them), later prose edits to the retrospective, and the
superseded first WP4b regeneration `0f484491c`.

### W1-8 — Run B inputs, `outputs/modality-bridge-2026-10-07/`

Sub-agent, drivers and comparisons in `fault-window-rechecks-scripts/w1-8-w2-11/`
(`runb_*.sh`, `runb_spec.py`, `reparse_verifier_leg.py`,
`remerge_chunks.py`, `compare_files.py`, `summarise_runb_audits.py`,
`later_change_diff.py`, `w1-8-*.json`, `w1-8-*.txt`, `integrity.txt`,
`logs/`). Every job ran with the API keys blanked and the HTTP(S) proxies
pointed at a dead port. No file under `scripts/`, `config.py`, `prompts/`,
`data/`, or `inputs/` changes across Run B's generating commits
(`2cff16c91`..`69eb32132`), but each step was still replayed at the commit
its record names.

| Group | Replay | Result |
|---|---|---|
| 7 unions and their 7 `.build.json` | `modality_bridge_union.py --layout batch … --write` at each build's recorded `git_head` | 14 byte-identical |
| 7 crop manifests | `run_pv.py extract` (offline stage) with real copies of the rasters | 7 byte-identical |
| 7 coverage, 7 metas, and 7 provenance check records | the gates-only union run, `modality_bridge_stage2_checks.py metas`, and `check_union_provenance.py --manifest` at the records' commits | 21 byte-identical |
| `anchor-gate.json` | `modality_bridge_anchors.py` at `2b6edde9a` | byte-identical (6 cells, 3 gaps) |
| `validate-chain.json` | `--validate-originals` at `2cff16c91` | equal field for field, ignoring only 8 scratch-path leaves of 361 |
| 10 legs' `probabilities.json` | re-derived offline from each leg's committed `batch_results.jsonl` (an offline driver importing only `validate_batch_results` and `parse_verifier_results`) at each meta's `git_commit` | 10 byte-identical |
| 10 legs' `run.meta.json` | the same driver (`aggregate_batch_usage`, `estimate_cost`) | usage, batch usage, items, cost estimate, and billing equal; run ids and timestamps cannot be re-derived |
| 7 repaired copies (3 files each) | `modality_bridge_stage2_checks.py repair` at the adding commit | 21 byte-identical |
| 5 merged g37-image passes (3 files each) | re-merged from the 15 committed chunk triples at `987718a66` | 15 byte-identical |
| Cost audits | `audit_proposer_cost.py` and `audit_verifier_cost.py --tier batch` | the seven Stage 1 arms (8.39, 19.52, 8.64, 18.93, 12.33, 4.26, 9.76; total US$81.8348), the four Gemini 3 legs, and the Stage 2 total US$12.692042 match the findings at their quoted precision |

Coverage, of the 331 non-log files: 100 verified (90 byte for byte, 10
metas field for field). 212 are NOT CHECKABLE without spend: 120 Stage 1
passes, 45 chunk files, 27 recovery fragments, and 20 raw batch result
and job files. 10 `rehearse-*.json` records were not run, because
regenerating them needs `run_pv.py verify --dry-run`, which the no-API
rule bars. 9 are prose. Today's files equal their generating versions,
except the 7 repaired `probabilities.json`. Those were changed on purpose
by D62 (1)'s re-verification (`f2256f7c7`): 35, 12, 12, 10, 10, 8, and 8
rows, each named in that leg's re-verify record, plus a new
`reverify_wrong_sheet` key. As a bonus, the 45 deduplicated passes that
sit untracked in sapphire's main checkout (written 2026-10-07, in W1)
were regenerated byte for byte by the union step.

### W2-11 — inputs written on sapphire in W2

Same sub-agent and directory (`w2_11_*.sh`, `w2_11_spec.py`,
`check_*.py`, `r2_*.py`, `count_image_w2.py`, `w2-11-*.json`). I
completed one check myself (`fault-window-rechecks-scripts/w2-11-vote4/`).

| Producing commit | Replay | Result |
|---|---|---|
| `7894b5b5a`, r2 sweep materialisations (31 cells, `cells_manifest.json`, 22 CSVs, `sweeps.json`) | at `7894b5b5a^`: `final_board_sweeps.py --reference r2` (all gates passed), then `final_board_n3_carried.py --reference r2` | **55 of 55 byte-identical**. 24 of them changed later (`f407d4f5d`, `a1c4bf2c3`, `03b8496ed`, `681b4e246`, `1ed3e54cb`, `cca6ccda5`, `539372938`, `1bbba2e21`); a structured diff shows those commits only added tile-MCC columns, `sweeps.json` leaves, and 28 manifest entries, keeping every original value |
| `e9d1db0d0`, union rebuilds (12) | the three recorded `merge_passes.py --sweep --passes …` commands at the parent | 12 byte-identical; `check_union_provenance.py --union` at `e9d1db0d0`: all 9 SUBPOOL-CONSISTENT |
| `185681674`, `e01b8617a`, `e7ebc1695` (the 2026-09-08 consensus rebuilds) | `merge_passes.py --sweep` over the pool `rebuild_recovered_consensus.pool_dir_for` resolves; WBF by `fuse_detections_wbf.py` at the parameters `wbf_diagnostics.json` records | 8 + 6 + 6 consensus files and 3 WBF files byte-identical; 26 of 26 archive copies equal their source blobs. The sub-agent's replay did not produce `wbf_vote4.geojson` (the commit made it with a separate vote ≥ 4 filter). I ran `e7ebc1695`'s `scripts/filter_detections_by_vote.py --min-votes 4` on the regenerated candidates: byte-identical, 328 of 1,099 features (`w2-11-vote4/run_vote4.log`) |
| `c053f5a41` (a hand correction, no script) | the documented rule re-applied to the parent's meta | the parsed meta is equal; the bytes differ only in the final newline; the tiles sidecar's completed list equals the GeoJSON's 326 tiles |
| `43516df9a`, recovery verifier stages (12) | extract and `sweep_f1_greedy_pv.py` at `43516df9a` | 3 `sweep_2d.json` byte-identical; 3 crop manifests equal field for field apart from `rasters_dir` and `tiles_dir` (machine paths); 6 `probabilities.json` and `run.meta.json` are real-time output with no raw responses kept: NOT CHECKABLE |
| `f8e0eb600`, extended stages (20) | extract; the carry harness (`63f4cac1c`) and its 6 sweeps | 3 carry records, the K = 5 probabilities, and 6 sweeps byte-identical; 3 manifests equal apart from `rasters_dir` and `tiles_dir` (committed absolute, regenerated relative); the carried rows equal (K = 1 639 of 639, K = 3 756 of 756); the 1 + 3 newly called rows and 2 metas are API output: NOT CHECKABLE |
| Image campaigns (224 files last changed in W2 by the sub-agent's count; the list said 227) | runs 4 and 5 re-merged from the `21d1b497d` chunks; unions and pass-provenance sidecars at `b9d4032bb`, `bd5de9f80`, `7d61f1ff9`; the 3.7 crop manifests; 6 batch legs re-parsed at their meta commits | 33 checked, all exact: 6 merged files and 12 unions and sidecars byte-identical; 3 crop manifests equal apart from `rasters_dir` and in agreement with their unions; 6 `probabilities.json` byte-identical and 6 metas equal field for field. NOT CHECKABLE: 42 chunk files, 57 proposer passes, 23 real-time legs and earlier sidecars, 11 raw batch results and job records. Not attempted: 12 (recovery worklists, `all_tiles_manifest.json`, the probe's sampled manifest). Logs and prose: 46 |

The sub-agent stopped its first r2 sweep (one worker, 50 minutes in, at
the start of the sweep proper) and relaunched it on six workers once the
other rows had finished. It first confirmed from the script that worker
count cannot change the output: `Pool.map` keeps task order, and rows are
sorted before writing. The stopped run's log is kept
(`logs/w2-11-r2-stopped-1worker.log`).

### W2-3 — the K-ladder (Phase 2, tier E, MCC test, MCB)

Two sub-agents, drivers and comparisons in
`fault-window-rechecks-scripts/w2-3/w2-3a/` (the Phase 2 pipeline) and
`w2-3/w2-3b/` (the statistics), each with a `coverage-tally.json` that
accounts for every file in its list. The scope is every tracked file
whose last change (at `718d0ee08`) was a W2 commit that also wrote under
`results/k-ladder-2026-09-12/` or `outputs/k-ladder-2026-09-12/`, plus the
K-ladder reports and the board's K-ladder membership file, less seven
files that belong to other rows (four uplift-supplement files of
`741a4eaff`, W2-5; `pareto_v2.{json,png}`, W2-13; one census-verified r2
board evaluation of `c2060da40`): 920 files. The list's "547" counted
differently. My first split of the scope missed 57 of the 920, the five
tier E tiering files and 52 union files of `e3232d65b`; a completeness
check caught them, and both groups were then replayed (below).

Coverage: 512 VERIFIED (6 of them already by the first batch, under
W2-13), 324 cell evaluations census-verified, 66 NOT CHECKABLE, and 18
prose or code.

| Group | Generating commit → replayed at | Result |
|---|---|---|
| The 28 Phase 2 first-N unions | `e3232d65b` and `19e56ed80`, each at itself (`build_k_ladder_phase2_unions.py`); `unions.json` at `eb6d797e0` | 56 consensus GeoJSONs and 28 `voting_summary.json` byte for byte at both commits; 28 `experiment_intent.md` line for line apart from their two date lines; `unions.json` field for field after `generated_at_utc`. `check_union_provenance.py` at `19e56ed80`: 28 SUBPOOL-CONSISTENT, as committed. The 52 `consensus_t*.geojson` last changed by `e3232d65b` (outside my enumeration) reproduce too |
| Phase 2 run, offline stages | `326181bcd` → `326181bcd` (`/tmp/final_downstream.sh`, recovered from the transcript: `--recompute-ledger`, `score … prepare --fresh`, `collect --strict`, the carried and 3.7 opmax derivations, `check_tile_vocabulary_match.py`, `run_pv.py extract` for 28 rungs) | 173 files compared: 166 byte for byte, 7 field for field after `generated_at_utc` / `updated_at_utc`. That includes 60 sweeps, 46 materialised detection sets, the job lists, and `tile-vocabulary-match.json`. The 28 crop manifests equal byte for byte once the one `rasters_dir` path is substituted, and all 35,844 re-extracted crops are byte-identical to the September crops still on sapphire, so the images the verifier was sent are exactly reproducible |
| Phase 2 verifier outputs | `326181bcd` | 28 `probabilities.json` and 28 `run.meta.json`: real-time flex output, no raw responses kept, **NOT CHECKABLE**. Offline consistency holds on all 28: keys equal manifest ids equal union features (35,844), 0 failures, `gemini-3-flash-preview` at T 0.0, MINIMAL thinking, and each meta's tokens give its ledger entry (US$24.8065 in all) |
| The 2026-09-13 recovery fix | `20c0a053f`, `63f4cac1c`, `5166ddeda`, `987534c03` (harness at `63f4cac1c`, `fix_op_points.py` at `5166ddeda`, K = 3 re-score at `987534c03`) | 4 materialised sets byte for byte; 3 `f1-only` records after one machine path; both `operating-points.json` versions; the K = 3 detection set byte for byte at two commits. The `reproduced-k5-evaluation` summary reproduces exactly at its generating code |
| Small items | `b949d5644`, `3013171cd`, `f4a1011a8`; smoke `9a934eaef` | all field for field after `generated_at_utc` (tables line for line after their "Generated" line); smoke union byte for byte; its 2 API outputs NOT CHECKABLE |
| MCC test | `d10137595` → itself; sign-swap `d900ed1d5` → itself | 32 files: 15 byte for byte, 17 after `generated_at_utc` and the tiering `git_commit` stamp; sign-swap 2 of 2 byte for byte. GS ΔMCC +0.0134 at BH p 0.7678 reproduced |
| Phase 2 MCC test | `326181bcd` → `3c5de3f23` (note a) | 53 files: 26 byte for byte, 27 after `generated_at_utc` and `git_commit` |
| MCB sets | `b7e2821ba` → `cebae7868` (where it ran; `b7e2821ba` changes only a table builder the driver does not import) | 46 of 46 exact: 44 byte for byte after substituting the run root, `table.md` byte for byte, `summary.json` after `generated_at_utc`. 10,000 resamples, seed 42 (note b) |
| Tier E unions, smoke, outputs | `98e54baf6` → itself; `5167b9a5c` → itself | unions, voting summaries, sweeps, the h10 rebuild, 4 materialised sets and `score-jobs.txt` byte for byte; crop manifests after `rasters_dir`; tension, `operating-points.json`, `scores.json` after `generated_at_utc`; `smoke.json` and `spend-ledger.json` re-derived offline from the committed metas, byte for byte (US$4.9595 flex); 8 API outputs NOT CHECKABLE |
| Tier E tiering (the enumeration slip) | `741a4eaff` → itself (`tier_e_ladder_tiering.py`, as last run at 14:28:43Z in the original worktree; 10,000 permutations, seed 42) | both tiering inputs and `tiering_20m.md` byte for byte; `ladder.json` after `generated_at_utc`; `tiering_20m.json` after `generated_at_utc` and the `git_commit` stamp. The pre-D50 values reproduce (K = 1 F1@20 0.854586) |
| Carried points | `9457b2689` → itself | 52 materialised sets and the job list byte for byte |
| Board frame | `f31e7470e`, `3d9c64807` (both written on amd-tower) | byte for byte after the build timestamp |
| Ladder tables and figures | `61870d9e7`, `32d0c6445`, `2e0c2941d`, `0f484491c` | already VERIFIED by the first batch (row W2-13) |
| The two 3.7 K = 1 cells the census could not fully reproduce | `326181bcd` → itself: their two `evaluate_detections.py` lines of `phase2/score-jobs.txt` (`replay_withheld_cells.sh`) | 6 files: both `evaluation.csv` byte for byte; both `evaluation.json` after `generated_at_utc`, `timestamp`, `output_dir`, and the git-state stamps (7 of 498 leaves); both `.md` after their "Generated" line. The intervals and tile MCC reproduce (0.1337, interval 0.0552 to 0.1884; 0.1422, 0.0679 to 0.198) (note f) |
| Cell evaluations | various | 324 files census-verified, each checked against the census table (`census_cells.csv`): 315 `replay` reproducing, 9 `verified-bytediff`; not re-scored |

Notes:

- (a) The Phase 2 MCC test ran as stage 12 of `/tmp/final_downstream.sh`
  in sapphire's live checkout (HEAD `f724b7a10`, the branch's scripts
  copied in) and resolved its rungs through `results/run-conditions.json`
  as stage 8 had just written it. Those 46 rows were committed only in
  `3c5de3f23`, the child of `326181bcd`, which changes nothing but the
  register, the manifests, and the uplift files; at `326181bcd` itself
  the rungs do not resolve.
- (b) The list's MCB caveat ("gated against the committed ranking within
  4.958e-05, a tolerance, not exact") describes the MCB's own internal
  gate. Its largest delta is on the MCC arm against a committed ranking
  rounded to four places (0.71275 against 0.7127); the F1 arm's largest
  is 5e-07. The 46 MCB files themselves reproduce exactly, so the caveat
  can be dropped.
- (c) The originals did not run at commits. They ran in sapphire's live
  checkout or in agent worktrees, with scripts rsynced or copied in and,
  for the recovery fix, with inputs committed minutes later. Each replay
  ran at the committing commit (or the commit named above), after
  `git diff --stat` showed no difference in the scripts and inputs used;
  the byte identity confirms it. For the same reason the `git_commit`
  stamps inside several outputs (`f724b7a10`, `156bddf36`, `5167b9a5c`)
  do not identify the code that ran.
- (d) S9's eight D50 movers reproduce their committed, pre-D50 values at
  their generating commits: the four tier E cells (K = 1 / 3 / 5 F1@20
  0.8546 / 0.884 / 0.8905, unrounded K = 1 0.854586, and the K = 1
  carried cell's 0.854), the recovery-fix K = 5 evaluation's whole
  summary, the two 3.7 K = 1 cells re-scored in full (note f), and the
  3.7 K = 3 cell's detection set (its evaluation census-verified). Their
  later moves are D50's scorer, not fault-window damage.
- (e) No patch was needed: no script these replays load hard-codes the
  live checkout's root. Five unrelated scripts in the tree do
  (`scripts/ab_plus/tail/*.py` and `scripts/run_bootstrap_10k.py`); none
  ran.
- (f) The sub-agents first filed these two cells under the census. A
  cross-check of every census-attributed file against the census table
  found their rows marked `W-tile-join-withheld`: the census re-scored them
  with code that has the tile-join invariant (`7ba47b63b`), which
  withholds the name-based tile MCC they were scored with, so only their
  points could reproduce there. Neither `326181bcd` nor the original HEAD
  `f724b7a10` has that invariant, and the re-score at `326181bcd`
  reproduces every number. These are the two registered K-ladder cells of
  row W2-14, which is otherwise not re-checked.

### W2-4 — the r2 board's tile-MCC re-sweeps and post-hoc cells

Driver and comparisons in `fault-window-rechecks-scripts/w2-4/`
(`replay_cells.sh`, `replay_sweep.sh`, `compare_steps.py`, `cap_guard.sh`,
`cmp-*.json`, logs). The 52 files are those whose last change was one of
the seven commits below; each step ran at sapphire's HEAD when the
original ran (reflog of the live checkout), with the command from the
session archive (2026-09-19T07-27). Every step started from a fresh tree,
and every file it wrote was compared with the generating commit's blob.

| Generating commit | Replayed at, and command | Files | Result |
|---|---|---|---|
| `cca6ccda5` (the seven carried-analogue cells) | `3ced9749c`: `final_board_posthoc_cells.py --set carried-analogue` | 7 detections + `cells_manifest.json` | 8 of 8 byte for byte |
| `a1c4bf2c3` (tile-MCC re-sweep, ten families) | `835c2f3a0`: `final_board_sweeps.py --reference r2 --families ARM1-N1 … FOURTH-N10` | 10 sweep CSVs + `sweeps.json` | 11 of 11 byte for byte (926 points) |
| `1ed3e54cb` (the ten MCC-oracle cells) | `a1c4bf2c3`: `final_board_posthoc_cells.py --set mcc-oracle` | 10 detections + `cells_manifest.json` | 11 of 11 byte for byte |
| `03b8496ed` (tile-MCC re-sweep, the other 13 families) | `c9131e757` (committed on sapphire as `a9e4279cc`, rebased before the push): `final_board_sweeps.py --reference r2 --families TH7 … B-N5` | 13 sweep CSVs + `sweeps.json` | 14 of 14 byte for byte (1,122 points) |
| `539372938` (the carried-k MCC record) | `d7e0c741d`: `final_board_sweeps.py --reference r2 --record-carried-k` | `sweeps.json` | byte for byte |
| `681b4e246` (the ten carried-k MCC-oracle cells) | `4a8d157cb`: `final_board_posthoc_cells.py --set mcc-oracle-at-carried-k --reference r2` | 10 detections + `cells_manifest.json` | 11 of 11 byte for byte |
| `1bbba2e21` (the relabel) | `182a414f2`: `build_tile_presence_board.py --stage relabel` | `cells_manifest.json` (and the campaign files it also writes) | 5 of 5 byte for byte: the r2 manifest and the four Gemini 3 and 3.7 campaign manifests and sweep records the stage also relabels. The commit's two board documents come from a separate renderer (W2-2's files) and were not replayed |

- **D6a reproduced.** Every one of the 23 families puts its tile-MCC
  argmax at the lowest vote count its sweep space offers: 18 at k1 and
  the five incumbents (TH7, T03, TM, IM, UPL), which never sweep below
  k3, at k3. The ten 3.7 families' MCC oracles and their micro-F1 equal
  the commit body of `a1c4bf2c3` (for example ARM2-N5 0.7487 at (0.96, k1),
  micro 0.8055).
- **Today's files.** All 52 are their generating commits' blobs, and
  today's `sweeps.json` is the `539372938` version, whose replay read the
  CSVs and the `03b8496ed` record that the sweep replays had reproduced.
  So every tile-MCC column and argmax block on the board's record is
  verified.
- **Worker count.** The originals used 20 workers, the replays 3 and 4.
  `Pool.map` with a fixed chunk size returns rows in task order and rows
  are sorted before writing, so the count cannot change the output; the
  byte identity confirms it. The gates (G4 12 cells, identity counts,
  mechanism triples, geometry, and pass pins) passed on the way in both
  runs.
- **Rebased commit.** `03b8496ed` was committed on sapphire as `a9e4279cc`
  at 03:23:42Z and rebased onto `f1b9b48ff` before the push; the replay
  ran at the HEAD of the launch (`c9131e757`, pulled at 02:31:14Z).
- No step touched sapphire's live checkout: a canary on its
  `git status` stayed unchanged from start to end
  (`../kernel-bad-page-2026-10-15.txt`).

### W2-8 — the E70 bootstrap-interval re-run

Driver and comparisons in `fault-window-rechecks-scripts/w2-8/`
(`replay.sh`, `run1.log`, `compare-run1.jsonl`, `crosscheck.py`,
`crosscheck-run1.json`); the comparison helper is
`fault-window-rechecks-scripts/compare_json.py`.

- **Replayed at `c50bd5f19`**, the parent of `8c89ccebb` and sapphire's
  HEAD when the original ran (reflog, 2026-09-12T05:15:40Z). The original
  command, from the session archive (2026-09-11T04-35, 2026-09-12T05:16:03Z),
  was `scripts/repair_bootstrap_cis.py rerun --workers 16
  results/all-bootstrap-cis.json results/pv/all-bootstrap-cis.json`; the
  replay used 2 workers. The script's `ProcessPoolExecutor.map` keeps job
  order and seeds every entry with 42, so the worker count cannot change
  the output. Its gate ran first, as originally: 5 of 5 already-matching
  entries reproduce at |Δ| = 0.
- **Both stores** (`results/all-bootstrap-cis.json` and
  `results/pv/all-bootstrap-cis.json`): of 7,549 leaves, 170 differ, all of
  them the 85 re-run entries' `recomputed_at` and `elapsed_seconds`; key
  order is equal. With those two fields copied from the committed file and
  the store serialised as `write_store` does, the regeneration is byte for
  byte the `8c89ccebb` blob (`crosscheck-run1.json`). The two regenerated
  stores are byte-identical to each other, as committed. Today's files are
  the `8c89ccebb` blob.
- **The registry's figures** (`results/ci-metadata-registry.md`, last
  changed by `8c89ccebb`; hand-written prose) re-derived from the
  regeneration: 85 entries re-run across 16 run families, the largest
  `phase3a/track1-image` (44); median |ΔF1 mean| 0.000583; maximum 0.027611
  (`single:phase3c/track2-text/h9-E-p2/run_5`, 1,114 → 1,233 detections,
  +119); 81 of 85 below 0.005; 59 fell and 26 rose (commit body).
  `check_bootstrap_cis.py --check` reports 472 resolved, 472 match,
  0 mismatch, and 24 known unresolved `consensus:` entries, as the commit
  body says (its exit code is 1 because of the 24 annotated entries; the
  registry names `--allow-annotated` as the drift gate).

### W2-7 — the modality-track audit recomputation

Driver and comparisons in `fault-window-rechecks-scripts/w2-7/`
(`replay.sh`, `run1.log`, `compare-run1.jsonl`).

- **Step 1, `d5eaeb1ee`**, replayed at its parent `c1b151bce`, which the
  original worktree had just pulled. The five commands are the ones the
  session archive records (2026-09-13T23:46:10Z and 23:46:18Z):
  `characterise_gs_plateau.py` and `tile_size_sweep.py`, each with and
  without `--legacy-modality`, into `recomputed/`, then
  `compare_modality_recomputation.py`. The replay tree had no
  `recomputed/` directory and no `recomputation.*` before the run, so every
  file compared was written by the replay. Of the ten files, eight are byte
  for byte the `d5eaeb1ee` blobs (both plateau tabulations and their `.md`,
  both sweep `.md`, `recomputation.json`, and `recomputation.md` as first
  committed); the two `tile_size_sweep.json` differ only in
  `generated_at_utc`.
- **Step 2, `aa1d9bd5b`** ("re-render recomputation.md with blanks
  collapsed"), replayed at its parent `6dfe7cbeb`:
  `compare_modality_recomputation.py` gives `recomputation.md` byte for
  byte the `aa1d9bd5b` blob and `recomputation.json` byte for byte the
  `d5eaeb1ee` blob. Today's files are those blobs.
- **R2-06 confirmed**: the regenerated recomputation gives the phase-2
  text group 14 cells, 6 with a defined tile MCC, all 0.0665, and the
  image group 22 cells, 21 defined, 0.0665 to 0.2907; two of fifteen
  tile-size legs move, and the three isolation views are identical.

## 4. Surprises and things worth knowing

None of these is a difference in a committed number. They are provenance
and procedure findings met on the way: items 1 to 9 in the rows of
2026-10-14, items 10 to 17 in those of 2026-10-15.

1. **Three Gemini 3 crop manifests were never committed** (W2-1 note d).
   The Gemini 3 inheritance row reads
   `outputs/gemini3-image-55map-2026-09-16/verifier/g384_ov192_55map_g3img/crops_k{1,3,5}/candidate_manifest.json`.
   They sit untracked in sapphire's main checkout (written
   2026-09-19T00:26 to 00:37Z, in W2; 8.3, 13.3, and 16.7 MB). The
   inheritance outputs reproduce byte for byte from them, so they are the
   files that were used, and nothing in them looks corrupted. But a signed
   input that exists only on one disk is a provenance gap of the kind
   W2-11 lists, and nothing else records their hashes.
2. **An output's key order depends on the hash seed** (W2-1 note c). The
   two K = 5 replicate drivers build a cache by iterating a Python set of
   cell labels, so the key order of `n_detections` and `tile_confusion` in
   their `tests.json` follows `PYTHONHASHSEED`. No value changes. D63's
   sweep looked for set order feeding numbers, so this cosmetic case was
   out of its scope. It does make the files byte-reproducible only under a
   recovered seed (202 for arm 2, 124 for arm 1).
3. **`e0f9a4d03` ran on inputs committed 35 minutes later** (W2-1 note a).
   The K1/K3 verifier outputs it read were untracked when it ran and were
   committed in `b9d4032bb`. The replay at `b9d4032bb` reproduces its
   outputs byte for byte, which settles that the committed inputs are the
   ones used.
4. **Two blocks in W1-1's files were spliced by hand, not computed**
   (`verifier_analysis.json`'s `conditions`, `grid_analysis.json`'s
   `verifier_costing`). Both were carried from the files committed before
   W1, as the Session 161 transcript records. The replay repeats the splice
   and matches, but those two blocks are verified only as copies of
   clean-boot content.
5. **Hard-coded roots.** The replicate and inheritance drivers under
   `results/gemini37-image-55map-2026-09-13/` hard-code the live checkout's
   path at their generating commits. Run unchanged in a replay tree, they
   read and write sapphire's shared checkout, not the tree. `55ff8a02e`
   fixed this in all three drivers on 2026-10-09; anyone replaying an
   older commit needs the same one-line patch (`w2-1/patch-*.diff`).
6. **A launch pattern that blocks.** This line backgrounds the whole
   `cd && nohup` list as a subshell:

   ```bash
   ssh host 'cd TREE && nohup cmd > log 2>&1 < /dev/null &'
   ```

   That subshell keeps the ssh session's descriptors open, so
   the local call does not return until the job ends. The project rule
   ("redirect all three descriptors, nothing after the `&`") is met by the
   letter and still blocks. Putting the `cd` inside `bash -c`, or using
   `setsid nohup`, avoids it. The W2-2 sub-agent hit this and lost no
   work, and no job ran twice. This is a candidate one-line addition to
   `docs/agent-guidance.md` § Compute Location, for the PI to decide.
7. **Count corrections for the list.** W1-4's "16 JSON under `class-b/`"
   are 9 there plus 7 annotated files elsewhere. W1-3's "(11)" are 8 phase
   files, `comparison.json`, and the annotation summary (checked under
   W1-2), the rest being scripts and a timing log.

8. **A rounding slip in prose.** Run B's findings § 9 says "In all,
   US$94.52". The audited components reproduce exactly (Stage 1
   US$81.8348, Stage 2 US$12.692042), but their sum is US$94.526842, which
   rounds to US$94.53. The slip came from adding the two rounded
   subtotals. It is not a computational difference, and the subtotals as
   quoted are right.
9. **Other untracked W1 intermediates.** The 45 deduplicated Stage 1
   passes under `outputs/modality-bridge-2026-10-07/*/scoring/common/` sit
   untracked in sapphire's main checkout (written 2026-10-07, in W1). The
   union step regenerated all 45 byte for byte, so they are sound. They
   are regenerable intermediates, not inputs that exist nowhere else.

10. **An orphan detection set.**
    `results/k-ladder-2026-09-12/phase2/materialised/pv-min-text-t0.7-n1-carried-p0.15-k1.geojson`
    was committed in `326181bcd` but not written by the final run. No cell
    or operating point refers to it. It is left over from a trial at
    06:29Z, before the driver gained its carried-equals-opmax rule, and it
    is the same blob as the regenerated `pv-min-text-t0.7-n1-opmax.geojson`
    (sha256 `582c9d1d…`), so it is harmless.
11. **Tier E `smoke.json` says `probabilities_returned: 6`.** The true count
    is 5; 6 is the envelope's key count, the driver defect `5b2f2c05d`
    fixed. Today's file still carries the 6, and the replay reproduces it
    exactly with the pre-fix expression.
12. **Today's union checker calls two of the 28 Phase 2 unions STALE** as
    they stood at `326181bcd`: the Gemini 3.7 K = 1 and K = 3 unions. This
    is the documented recovery-fragment drop, repaired on 2026-09-13
    (`e9d1db0d0`, verified under W2-11), not fault-window damage. All 28
    crop manifests agree with their unions (`--manifest` mode).
13. **A slip in `eb6d797e0`'s body.** It says the rewritten intent files
    changed "only their dates"; the 3.7 K = 3 intent would also change its
    count line (757 to 759). The intents were not committed, so no file is
    affected.
14. **An input-state dependency in the tension analyses.** The committed
    `tension/grid-overlap.json` has `tier_e_verified_b_geometry: null`
    because `tier-e/scores.json` did not yet exist when it ran (13:59Z). A
    replay at `5167b9a5c` with that file present fills the block, so it was
    held aside for that step.
15. **`check_bootstrap_cis.py --check` exits 1** on the regenerated store,
    with 472 resolved, 472 match, and 0 mismatch: the 24 annotated
    `consensus:` entries count as unresolved. The registry names
    `--check --allow-annotated` as the drift gate, so this is expected.
16. **My own scoping slip.** My first split of the K-ladder files dropped
    `741a4eaff` whole, because four of its files belong to W2-5, and with
    it five tier E tiering files; the 52 union files of `e3232d65b` were
    also outside the split. A completeness check against every W2 commit
    that wrote under the K-ladder directories caught both, and both were
    replayed (§ 3, W2-3).
17. **The worker cap needed a guard.** With two sweep replays on 3 and 4
    workers and the short W2-4 steps on one process, a small guard
    (`w2-4/cap_guard.sh`) was ready to pause the short steps with SIGSTOP
    whenever the total would pass 8; it logged no pause. A first sweep
    launch on 2 workers was stopped during its gates when the W2-3
    sub-agents finished, and relaunched on 3; its log is kept
    (`sweep-run1-stopped-2workers.log`), and nothing it wrote was used.

## 5. Not done, and why

- **Rows outside D65's limit.** W1-6, W1-7, W1-9 to W1-12, W1-14, W2-3 to
  W2-8, W2-10, W2-12, W2-14, and the W3 boot were not re-checked. D62 (7)
  limited this pass to the rows above. Several of the others are
  claim-bearing: W2-3 (the signed K-ladder), W2-4 (D6a), W2-7 (R2-06), and
  W2-8 (the interval registry) are in the list's suggested-order item 3.
  Those four were re-checked on 2026-10-15 under D67 (2) (§ 3). Still not
  re-checked: W1-6, W1-7, W1-9 to W1-12, W1-14, W2-5, W2-6, W2-10, W2-12,
  W2-14 (but for its two K-ladder cells, § 3 W2-3 note f), and W3.
- **W1-5 residue.** Five W1-era files in W1-5's group were outside PR
  #38's regeneration (§ 3, W1-5).
- **Cell evaluations were not re-scored.** The census already verifies
  them, and the brief excluded the BCa engine runs. The exception is the
  two W2-3 cells whose census rows could not reproduce their intervals
  and tile MCC (§ 3, W2-3 note f): they were re-scored at their own
  commit on 2026-10-15.
- **Raw API responses** (Stage 1 passes, verifier responses) cannot be
  re-obtained without spend, and none was spent. In W1-8 that is 212 of Run B's 331 non-log files. In W2-11 it is 133 image-campaign files, the 6 real-time verifier outputs of `43516df9a`, and the newly called rows and 2 metas of `f8e0eb600`. The 10 Run B `rehearse-*.json` records were not run, because they need `run_pv.py verify --dry-run`, which the no-API rule bars. In W2-11, 12 image-campaign files (worklists, `all_tiles_manifest.json`, the probe's sampled manifest) were not attempted.
- **No second run of a DIFFERS file**, because nothing differed.

## 6. For the PI

1. **Nothing to restate.** Every claim-bearing file in the D62 (7) rows
   reproduces exactly on the fixed machine. That includes D53's P3
   (0.9199 against 0.8848, +0.0351, BH p < 0.0001), the K = 1 / 3 / 5
   ladder (0.8719 / 0.9199 / 0.9270), the r2 headline (0.8871, 0.8848,
   0.8827), and every D42 p value on the signed grid, stride, retest, and
   class B rows. No signature needs to lapse on fault-window grounds.
2. **Decide on the three untracked Gemini 3 crop manifests** (§ 4 item
   1). Commit them (about 38 MB), or record their sha256 in the campaign's
   provenance. The first closes the gap; the second documents it.
3. **Optional:** sort the replicate drivers' set iteration (§ 4 item 2),
   and add the launch-pattern line to the agent guidance (§ 4 item 6).
4. **Next re-checks, if wanted.** W2-3, W2-4, W2-7, and W2-8 were done on
   2026-10-15 (D67 (2)) and need nothing restated: the signed K-ladder,
   D6a's tile-MCC record, R2-06's range, and the interval registry all
   reproduce. The list's W2-3 caveat on the MCB tolerance can be dropped
   (§ 3, W2-3 note b). Of the W1 rows left, the list calls W1-11 and W1-12
   superseded, and W1-6, W1-7, W1-9, and W1-10 are re-parses or re-scores
   of minutes each; W2-5, W2-6, W2-10, W2-12, and W2-14 are minutes each
   too.
5. **Housekeeping.** The re-checks no longer need the working trees in
   `~/scratch/d57-4-rescore-2026-10-09/` (`old/`, `new/`, `phase3-*/`, and
   `rerun-check/`, most of its 77 GB) or the `q4-*` directories, which
   D62 (8) kept until the re-checks finished. Two cautions. The
   `phase3-new/` worktree holds nine uncommitted Phase 3 NEW outputs (the
   h6 A-06, A-07, and A-09 files, four null-exemplar files, and two
   voting summaries), the only copies of the W1 values W1-14 lists; W1-14's
   re-check compares against the S3 and S4 records' quoted values, so they
   are not strictly needed. And a few small files there are
   evidence that both re-check records and the fault-window list cite,
   and they are not committed anywhere: the census table
   `census-old/out/census_cells.csv` (1.7 MB, with `census_summary.json`
   and `compare.csv`), which is what "census-verified" rests on; Phase 3's
   `phase3-out/diffs/` (232 KB); Q4's `q4-repaired-readers-2026-10-09/q4/compare-*.json`
   (and `q4/before/`, 62 MB); and the Q4 drivers in `q4-tools/` (52 KB),
   which are not in the repository. Commit or archive those before the
   directories go. The regenerated outputs under
   `~/scratch/s164-fw-recheck-2026-10-14/*-out/` and
   `~/scratch/s164-fw-recheck2-2026-10-15/*-out/` can go once this record
   is accepted.

## Changelog

### 2026-10-15 — D67 (2): rows W2-3, W2-4, W2-7, and W2-8

Refresh trigger: PI ruling D67 (2) ("yes re-check"), for the four
claim-bearing rows the main session had dropped from its walkthrough
summary. Each was re-run on the fixed sapphire at its generating commits
and compared exactly, with no API call; branch `fault-window-rechecks-2`
from `718d0ee08`, drivers in `fault-window-rechecks-scripts/{w2-3,w2-4,w2-7,w2-8}/`.

| Row | Before | After |
|---|---|---|
| W2-3 | not re-checked (cells census-verified; MCB within a tolerance) | VERIFIED for 512 files; 66 NOT CHECKABLE; 324 census; MCB exact |
| W2-4 | not re-checked (cells census-verified; sweeps no) | VERIFIED (52 files byte for byte) |
| W2-7 | not re-checked | VERIFIED (10 files) |
| W2-8 | not re-checked | VERIFIED (both stores) |

What did not change: every verdict of 2026-10-14; no committed result,
output, document, or register row; no claim, signature, or ruling. The
additions are the header bullets, a paragraph in the bottom line, the
four rows' entries in § 2 and § 3, § 4 items 10 to 17, and the refreshed
§ 5 and § 6 items 4 and 5. Kernel "Bad page state" count 0 before and
after. Commits: `ed21afc21` and later commits on the branch.

### 2026-10-14 — Original publication

The re-check record for PI ruling D65, item D62 (7): rows W2-1, W2-2,
W1-1 to W1-4, W1-13, W2-13, W1-8, and W2-11 re-run on the fixed sapphire
and compared exactly; W1-5 and W2-9 marked done on PR #38's and PR #35's
evidence. Branch `fault-window-rechecks` from `90294a283`; drivers in
`ba450d4d1` and later commits on the branch.
