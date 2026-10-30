# MCC tiering of the Era-2 board under the geometric tile joins

> **Last revised**: 2026-10-30 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Agent / model lane**: Claude (Claude Code), Opus 5.5 (`claude-opus-5-5`),
  overnight job, one of three parallel lanes
- **Date**: 2026-10-30 (Session 166)
- **Repository**: `saross/map-reader-llm`
- **Branch**: `mcc-join-tiering-2026-10-30` (from `origin/main` at
  `3cbe6867e`; pushed, no pull request)
- **Commits**: `792d459ea` (the option and its tests; every run below was
  computed at this commit), `e88d00b69` (a log line only), and the commit
  that adds this record and `results/tile-join-audit/era2-board-mcc-tiering-2026-10-30/`
- **Task**: the MCC robustness job, part (b), in
  `planning/paper-writeup-continuity.md` ("Planned: one $0 MCC robustness
  job after PR #52 merges"). $0: no model application programming
  interface (API) call was made.

## 0. Status and headline

**Done, gate passed.** The gold-standard (GS) Era-2 verified board's
tile-level Matthews correlation coefficient (MCC) permutation family and
its MCC Multiple Comparisons with the Best (MCB) admissible set were
rebuilt under the published name join (`id`) — reproducing the committed
board exactly — and then under `geometric-primary` and
`geometric-contains`. Nothing in the board, the register, any findings
document, `docs/paper/`, `docs/notes/` or `planning/` was edited.

**The board-grain disagreement between F1 and tile-MCC holds under the
`id` join only (flagged, § 4).** Under both geometric joins the top F1
cell is also the top MCC cell, four of the five F1 Tier-1 cells are in MCC
Tier 1, and 50 (primary) or 45 (contains) of the 52 F1-admissible cells
are MCC-admissible. Under `id` those figures are MCC rank 21, one of five,
and 9 of 52. Obs 482's headline, Obs 513's "near-oppositely below it",
and R6-18's board-grain sentence rest on the `id` reading. A diagnostic
(§ 4.2) finds that, under `id`, 59.6 % of all false-negative tiles on the
board contain one of the same cell's own detections, booked by name to an
overlapping neighbour tile.

All figures below are read from
`results/tile-join-audit/era2-board-mcc-tiering-2026-10-30/summary.json`
(rendered as that directory's `README.md`) unless another file is named.

## 1. What was done

**Code** (commit `792d459ea`; `e88d00b69` changes one log line):

- `scripts/era1_leaderboard_tiering.py` gains `--tile-join` (`id`,
  `geometric-primary`, `geometric-contains`; default `id`). It reaches
  `cell_per_tile_classification` and `load_cells`, which pass it to
  `lib_advanced_metrics.calculate_tile_classification` and
  `compute_per_tile_classification`. With the default, the library calls,
  the committed-record gate, the output names and the output keys are what
  they were. A geometric join changes only the MCC arm. Each cell's
  per-tile labels follow the join. The gate (`join_sensitivity_gate`)
  compares them with the scorer's aggregate under the same join, plus the
  geometric booking arm, because no committed record exists under a
  geometric join. The family ranks on the join's MCC at the committed four
  decimals. The outputs are `tiering_20m_<join>.json` and `.md`, which
  carry `mcc_permutation.tile_join` and each ranking row's published-join
  MCC beside the join's. A geometric join without `--permute-mcc` is
  refused.
- `scripts/selection_aware_intervals.py` gains `--tile-join` for `--board
  --metric mcc` (default `id`: the legacy derivation of the indicators from
  the F1 arm's per-tile true positives (TP) plus false positives (FP), and
  references by intersection). A geometric join reads the indicators off
  each cell's gated one-hot arrays (`build_board_tile_classification`), and
  `run()` takes them as `has_det`. The output is
  `<board>_mcc_<join>_b20_m1.json`. A geometric join with `--metric f1`, or
  outside `--board`, is refused.

**Tests.** `tests/test_board_mcc_tile_join.py` holds 19 tier-1 tests on a
four-tile overlapping fixture (100 m tiles on an 80 m stride). The fixture
is built so that the three joins give three different confusions and
three different MCCs (+0.5774, −1.0000, −0.3333). Seven tests pin the
default path:

- the option's default is the library's default, `id`;
- the default call equals the explicit `id` call;
- the default `load_cells` gates against the committed record, adds no
  key, and still withholds a disagreeing record;
- `mcc_point` is unchanged without `mcc_join`;
- the MCB's default indicators serialise identically to the legacy
  derivation;
- the join-aware MCB builder under `id` equals the default path on a
  two-cell board.

The rest pin the change:

- each join's labels match the scorer's;
- a geometric `load_cells` gates on its own aggregate and ranks on its own
  MCC, and leaves the F1 arm untouched;
- the MCB builder reads the join's indicators;
- both command lines refuse a join where it would change nothing.

**Red sentinel.** The tests were broken on purpose in a real-file copy of
`scripts/` and `tests/` (checked to hold no symlinks), one break at a time:

1. per-tile labels that ignore the join turned 5 tests red;
2. the default gate branch inverted turned 5 red;
3. MCB indicators taken from the F1 counts turned 1 red.

Restored, all 19 were green, and the copy's sources diffed equal to the
worktree's.

**Suite.** The full tier-1 suite ran on sapphire at `792d459ea`, in a second
checkout so no test could touch the tree the runs read: 4,454 passed,
5 skipped, 132 deselected, 3 xfailed, 0 failed (369 s). `ruff check` is
clean on every touched Python file.

**Run.** On sapphire, in `~/scratch/mcc-join-tiering-2026-10-30/wt`: a
whole-tree clone of sapphire's checkout (read only), then
`checkout --detach 792d459ea`, so every tracked file is present.
`reports/s164-agent-records/restatement-pass-scripts/board_files.py` lists
310 files that the board's 153 cells name; all 310 exist and are tracked,
so nothing gitignored was copied. `mcc-join-tiering-scripts/chain.sh` ran
eight single-threaded jobs in parallel, with commands mirroring the S164
board chain:

- the tiering under each of the three joins;
- the F1 MCB;
- the MCC MCB under each join;
- a builder check.

Every launch redirected all three descriptors. Each job wrote pid and rc
files from inside itself. Liveness was checked with `kill -0` on the pid
and by the rc file, never with `pgrep -f`. Sapphire was idle at launch.
This job used at most eight processes.

## 2. Gate (the `id` join reproduces the committed board)

| Quantity | Committed | This run |
|---|---:|---:|
| F1 pairs significant (Benjamini–Hochberg (BH) q 0.05) | 8,075 of 11,175 | 8,075 of 11,175 |
| F1 tiers | 14 | 14 |
| F1 Tier 1 | the five cells | the same five, same order |
| MCC pairs significant | 3,001 of 11,175 | 3,001 of 11,175 |
| MCC tiers | 6 | 6 |
| MCC Tier 1 | 34 cells | the same 34 |
| F1 MCB admissible (Hsu) | 52 | 52, same members |
| MCC MCB admissible (Hsu) | 60 | 60, same members |

These are not just matching counts:

- The whole `mcc_permutation` block is equal to the committed one.
- No key of `tiering_20m.json` differs beyond `generated_at_utc` and
  `git_commit`.
- Both MCB artefacts are byte-identical to the committed files (SHA-256
  `5f8926c1…` and `49cf614a…`).
- The join-aware MCB builder, run under `id` on the real board, returns the
  default path's indicators exactly (150 cells, 229 reference-positive
  tiles; `builder-id-check.json` on sapphire).

**Gate: passed.**

**Checks on the geometric runs.** In both geometric runs the F1 side
(ranking, tiers, Tier 1, all 11,175 pairwise records, the withheld cells)
is identical to the `id` run's. 150 of 150 MCC gates passed, no cell's MCC
was withheld, and the MCB candidate set equals the default's.

The **independent cross-check** compared each run's rebuilt confusion with
the 2026-09-12 audit (`scripts/audit_tile_join_variants.py`, a separate
code path), cell by cell and join by join:

- on `results/tile-join-audit/board-era2-2026-09-12.json`, 93 of 103 cells
  are equal under all three joins, and the ten that differ are exactly the
  ten that the S164 restatement re-scored after the audit;
- on `k-ladder-phase2-cells-2026-09-12.json`, 43 of 43 matched cells are
  equal under all three joins.

There are 229 reference-positive tiles under `id` and `geometric-contains`
and 199 under `geometric-primary`, the same on every cell. Primary books
each mound to one tile.

## 3. Per-join table

| | `id` | `geometric-primary` | `geometric-contains` |
|---|---:|---:|---:|
| MCC pairs significant (BH q 0.05, of 11,175) | 3,001 | 2,013 | 1,856 |
| MCC tiers | 6 | 5 | 5 |
| MCC Tier 1 (tie set) | 34 | 64 | 42 |
| MCC MCB admissible (Hsu), of 150 | 60 | 125 | 115 |
| top MCC cell | `verified-adv-image-baseline-pro-vf-era2b` | `g37-image-k5-verified-swap37-p0.90-k5-era2b` | `g37-image-k5-verified-swap37-p0.90-k5-era2b` |
| — its tile-MCC; F1 tier | 0.8887; 9 | 0.9617; 1 | 0.9423; 1 |
| Spearman of MCC against `id`, 150 cells | 1 | 0.7896 | 0.7231 |
| — over the 103 cells in `cells/` | 1 | 0.8396 | 0.7666 |
| mean ΔMCC against `id` (min … max) | — | +0.1067 (+0.0478 … +0.1472) | +0.0763 (−0.0011 … +0.1190) |
| cells higher / lower than under `id` | — | 150 / 0 | 149 / 1 |
| MCC MCB argmax stability (distinct winners) | 0.4192 (39) | 0.5227 (70) | 0.6189 (48) |

The MCC Tier 1 members of each join are listed in the results `README.md`
§ 4, and the admissible sets in `summary.json` → `per_join.<join>.mcb_admissible`.
Under `id`, MCC Tier 1 draws on F1 tiers 1 and 6–12. Under both geometric
joins it draws on F1 tiers 1–11 (primary) and 1–12 (contains).

## 4. Claim checks

| Claim | `id` | `geometric-primary` | `geometric-contains` |
|---|---|---|---|
| (i) top F1 cell in MCC Tier 1? (its MCC rank) | yes (21) | yes (1) | yes (1) |
| (ii) F1 Tier-1 cells in MCC Tier 1 (their MCC ranks) | 1 of 5 (21, 62, 46, 37, 102) | 4 of 5 (1, 27, 6, 3, 94) | 4 of 5 (1, 15, 5, 4, 93) |
| (iii) F1-admissible ∩ MCC-admissible | 9 of 52 and 60 | 50 of 52 and 125 | 45 of 52 and 115 |
| — union / F1-only / MCC-only | 103 / 43 / 51 | 127 / 2 / 75 | 122 / 7 / 70 |
| — top MCC cell F1-admissible? | no | yes | yes |
| (iv) top MCC cell's track | image | image | image |
| — image cells in the MCC top 10 | 10 | 6 | 5 |
| — MCC Tier 1, image / text | 31 / 3 | 37 / 27 | 28 / 14 |
| — MCC-admissible, image / text | 46 / 14 | 55 / 70 | 55 / 60 |
| — median MCC rank, image / text | 33 / 100 | 51 / 95 | 47 / 97 |
| (v) register's MCC leader still the top MCC cell? | yes | no | no |
| — its MCC, rank, MCC tier | 0.8887, 1, 1 | 0.9365, 10, 1 | 0.8942, 30, 1 |

Reading of each check, without interpretation beyond the figures:

1. **(i)** The top F1 cell is the all-3.7 image K = 5 cell. It is in MCC
   Tier 1 under every join. Under both geometric joins it is the MCC leader
   (0.9617 and 0.9423, against 0.8376 under `id`).
2. **(ii)** Under both geometric joins the fifth F1 Tier-1 cell,
   `g37-text-k10-verified-carried-p0.10-k10-era2b`, is the one left out of
   MCC Tier 1 (MCC rank 94 and 93).
3. **(iii)** The overlap moves from 9 to 50 and 45. It does so partly
   because the MCC instrument resolves less at the top under the geometric
   joins: 2,013 and 1,856 significant pairs against 3,001, and 125 and 115
   admissible cells of 150 against 60. The sharper statement is (ii), on
   the 42-cell `geometric-contains` Tier 1, which is close to `id`'s 34 in
   size.
4. **(iv)** "Image leads tile-MCC" (Obs 482) holds in the narrow sense that
   the top MCC cell is an image cell under every join. It is not the same
   cell, though: under the geometric joins it is the top F1 cell, a K = 5
   verified consensus cell, not a single-pass image proposer-verifier
   baseline. The image dominance of the MCC head does not survive the
   joins: image cells fill 10 of the top 10 under `id` but 6 and 5 under
   the geometric joins, and MCC Tier 1 goes from 31 / 3 to 37 / 27 and
   28 / 14. Image cells still rank higher at the median (51 and 47 against
   95 and 97), and they are 59 of the board's 150 cells. The track is the
   proposer's transmitted modality. For 107 cells it is the membership
   `track` field (E88). For 41 `-opmax` rows it is inferred from a member
   with the same `proposer_pool` (every pool maps to one track, checked).
   For 2 cells it is read from the pool's name.
5. **(v)** The register row's named MCC leader,
   `verified-adv-image-baseline-pro-vf-era2b` (row
   `gs-era2-verified-board-2026-09-10`, `outcome`: "MCC Tier 1 = 34
   cell(s) (verified-adv-image-baseline-pro-vf-era2b MCC 0.8887; …"),
   stays in MCC Tier 1 and the MCC admissible set under every join. It
   drops to MCC rank 10 (primary) and 30 (contains).

### 4.1 Surprises (flagged, not explained away)

1. **The F1-against-MCC board-grain disagreement is a property of the
   `id` reading.** Under `id`, F1 and tile-MCC pick largely different
   configurations: only the top F1 cell is in both Tier 1s, and the
   admissible sets share 9 members. Under either geometric join the two
   heads largely coincide (§ 4, (i)–(iii)). This contradicts the board-grain
   reading of Obs 482 and Obs 513 (the "near-opposite" ordering) and R6-18's
   board sentence, all of which rest on the `id` reading. Obs 513's caveat
   anticipated that "this observation's counts may move". They do, and the
   direction of the conclusion moves with them. The pipeline was checked
   before this was written up (§ 2). The F1 side is identical in all three
   runs. The geometric confusions agree with an independent code path on
   the 136 cells whose inputs are unchanged since 2026-09-12. The
   join-aware MCB builder reproduces the default under `id`.
2. **The 150-cell rank agreement is lower than the anchor quoted for this
   job.** The anchor, Spearman 0.85 and 0.77, is over the 103 `cells/`
   cells and reproduces from the 2026-09-12 audit as 0.8467 and 0.7736.
   Over the same 103 cells at today's restated head it is 0.8396 and
   0.7666. Over all 150 tiered cells it is 0.7896 and 0.7231: the 47
   K-ladder and `-opmax` cells reorder more.
3. **A withheld cell would sit at the MCC top under a geometric join.**
   The three cells withheld on the F1 arm stay withheld in all three runs,
   because the F1 arm keeps `id`. If admitted, `g37-text-k1-verified-opmax`
   would rank 2 under primary (0.9535) and 4 under contains (0.9262). The
   other two would rank 91 and 78 (primary) and 84 and 44 (contains).
   Results `README.md` § 5 gives their values. Disclosure only. No family
   includes them.

### 4.2 A diagnostic of where the `id` join's tile errors sit

`mcc-join-tiering-scripts/id_join_mechanism.py` makes one pass over the 150
cells. For each cell it counts the false-negative (FN) tiles under `id` that
geometrically contain one of the cell's own detections, that is, a detection
booked by its `source_tile` name to an overlapping neighbour.
`mechanism_summary.py` aggregates the counts. The outputs are
`id-join-mechanism.json` and `id-join-mechanism-summary.json` in the
results directory. This is descriptive. It is not a decomposition of
ΔMCC, and no table above uses it.

| Figure | Value |
|---|---:|
| FN tiles under `id`, all 150 cells | 6,697 |
| — of which contain one of the cell's own detections | 3,993 (59.6 %) |
| Spearman, that count against ΔMCC (primary / contains) | 0.7536 / 0.8668 |
| Spearman, that count against F1@20 | 0.5182 |
| top F1 cell: FN tiles under `id`, of which contain a detection | 37, 29 (433 detections) |
| register's MCC leader: the same | 14, 7 (509 detections) |
| median ΔMCC (primary), F1 tiers 1–3 / 4–8 / 9–14 | +0.1243 / +0.1143 / +0.0821 |

On the overlapping frame (384 px tiles on a 336 px stride), the `id` join
books a reference to every tile it touches but a detection to the one tile
its name gives. A cell's FN tiles under `id` are therefore often tiles its
detections occupy. The count grows with F1 and tracks the gain a cell
makes under the geometric joins. These figures are consistent with that
asymmetry penalising detection sets that keep one point per mound more
than sets that keep a point per tile the mound was seen on. That is a
hypothesis. It was not tested here: duplicates per mound were not
counted. Nor was it checked how a merged consensus or verified point's
`source_tile` is chosen, which bears on S153 ruling 6's rationale for `id`
("the per-tile decision the model actually made").

## 5. What is not done, and the open decisions

**Not done**:

- part (a) of the MCC robustness job (the clipped D51 evaluations), which
  is outside this brief;
- any edit to the board, the register (`results/run-analyses.json`),
  findings documents, `docs/paper/`, `docs/notes/` or `planning/` (by
  instruction);
- a pull request, which was not opened.

**Not measured**:

- the per-tile F1 under a geometric join, because the F1 arm keeps `id`
  (by the 2026-09-12 report § 4.3, `geometric-primary` leaves the per-tile
  F1 totals unchanged and `geometric-contains` moves them);
- duplicates per mound;
- the tile-exchangeability question that the overlap raises for every
  tile-swap test (`reports/tile-mcc-geometric-join-2026-09-12.md` § 6
  item 4), which applies to all three joins alike.

**Choices made and disclosed, each reversible.** None of the choices below
changes the `id` gate. The first is the one most likely to matter:

- the three withheld cells stay out of the geometric families, so that the
  comparison stays on one set of 150 cells (§ 4.1, 3);
- a geometric join's MCC is ranked at four decimals, as the committed
  evaluations are;
- the gate under a geometric join is the scorer's own aggregate plus the
  geometric arm, backed by the independent audit cross-check (§ 2);
- "image-bearing" means the proposer's track (§ 4, (iv)).

**For the PI: how the paper words MCC-ranking claims.** Options, not
chosen here:

- **A.** Keep the `id` claims (MCC Tier 1, the MCC crown, 4.11's MCC
  leader, 4.15's "image leads tile-MCC", R6-18's board sentence). Add the
  sensitivity statement that the board-grain F1-against-MCC disagreement,
  and the image baselines' MCC lead, hold under the published join and not
  under either geometric join.
- **B.** Narrow the board-grain claims to what holds under all three joins:
  the top F1 cell is in MCC Tier 1; image cells rank higher at the median;
  the register's leader is in MCC Tier 1 throughout. Report the `id`-only
  readings as join-dependent.
- **C.** Revisit the published join itself (the 2026-09-12 report § 6). The
  § 4.2 diagnostic is the evidence that bears on whether `id` measures what
  ruling 6 says it does for merged detection sets.

R6-18's ladder-grain claim (K = 1 admissible on tile-MCC on 22 of 22
ladders) was not re-tested here. It uses the K-ladder instruments, not
this board.

**Observation candidate** (for the PI's verdict; nothing written to
`docs/notes/`): the tile-MCC ranking's head depends on the tile join. Under
`id`, F1 and tile-MCC disagree at board grain (9 of 52 and 60 admissible
cells shared). Under either geometric join they largely agree (50 and 45
of 52), and 59.6 % of `id`'s FN tiles contain one of the cell's own
detections. It is a correction candidate to Obs 482 and Obs 513.

## 6. Reproduce

All on sapphire, $0, from `792d459ea`. Scripts are in
`reports/s166-agent-records/mcc-join-tiering-scripts/`: `chain.sh`,
`builder_id_check.py`, `summarise.py`, `id_join_mechanism.py`,
`mechanism_summary.py`.

```bash
S=$HOME/scratch/mcc-join-tiering-2026-10-30; T=<scripts dir>
git clone --no-checkout "$HOME/Code/map-reader-llm" "$S/wt"
git -C "$S/wt" checkout --detach 792d459ea
mkdir -p "$S/logs"; cd "$S"
nohup "$T/chain.sh" "$S/wt" "$S/out" "$S/logs" > logs/chain.log 2>&1 < /dev/null &
# once logs/chain.state reads DONE:
python "$T/summarise.py" "$S/wt" "$S/out" "$S/results"
python "$T/id_join_mechanism.py" "$S/wt" "$S/out" "$S/out/id-join-mechanism.json"
python "$T/mechanism_summary.py" "$S/out/id-join-mechanism.json" \
  "$S/results/summary.json" \
  "$S/wt/results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json" \
  "$S/results/id-join-mechanism-summary.json"
```

Wall-clock on sapphire: each tiering run took about 53 minutes,
single-threaded (11,175 pairs, two families, 10,000 draws); the MCB jobs
and the builder check took 1 to 3 minutes each. The full outputs,
including the geometric runs' Markdown renderings, remain in
`~/scratch/mcc-join-tiering-2026-10-30/out/` on sapphire. The results
directory carries each geometric join's `mcc_permutation` block, not the
F1 side, which is identical to the board's.

## Changelog

### 2026-10-30 — Original publication

Written by the S166 MCC robustness job, part (b), on branch
`mcc-join-tiering-2026-10-30`. It records the gate (passed), the per-join
table, the five claim checks, the surprises of § 4.1, the diagnostic of
§ 4.2, and the open decisions of § 5.
