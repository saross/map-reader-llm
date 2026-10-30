# K-ladder tile-MCC under the geometric tile joins

> **Last revised**: 2026-10-30 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Agent / model lane**: Claude (Claude Code), Opus 5.5 (`claude-opus-5-5`),
  overnight sub-agent job of Session 166
- **Date**: 2026-10-30
- **Repository**: `saross/map-reader-llm`
- **Branch**: `kladder-mcc-join-2026-10-30`, from `origin/s166-merge-check`
  at `284179a05` (now `main`); pushed, no pull request
- **Commits**: `58d2ba7d0` (the two `--tile-join` options and their tests),
  `463257349` (the run scripts and the historical Phase 2 inventory; **every
  result below was computed at this commit**), `75895f06e` (keeps the default
  calls argument for argument; changes no output, § 1.4), and the commit that
  adds this record and `results/k-ladder-2026-09-12/mcc-join-2026-10-30/`
- **Cost**: US$0. No model application programming interface (API) call was
  made.

## 0. Status and headline

**Done, gate passed.** The K-ladder tile-level Matthews correlation
coefficient (tile-MCC) permutation tests and Hsu multiple-comparisons-with-
the-best (MCB) admissible sets were re-run for all 22 ladders they cover
(eight Phase 1, thirteen Phase 2, tier E), for the seven ladders on PI ruling
D51's clipped basis, and for § 8.6's consensus-only side, under the
published name join (`id`) and under `geometric-primary` and
`geometric-contains`. Under `id` every run reproduces its committed artefacts
(§ 2). No findings document, register, `docs/paper/`, `docs/notes/` or
`planning/` file was edited.

**The four answers, flagged as surprises where they contradict a claim (§ 4):**

1. **"Tile-MCC does not follow F1" is a clear majority only under `id`.** From
   K = 1 to the best F1 rung, tile-MCC falls on 16 of 21 verified ladders
   under `id`, but on 9 of 21 under `geometric-primary` and 11 of 21 under
   `geometric-contains`. **"No significant rise" fails under
   `geometric-primary`**: both 55-map stride B ladders rise significantly
   (+0.0111, Benjamini–Hochberg (BH) p 0.0075; +0.0110, p 0.0093). The four
   significant falls become two (primary) and three (contains). HIGH image
   T 1.0's significant fall (−0.0637) disappears under both. The counts are
   the same on D51's clipped basis.
2. **R3-12's tile-MCC half does not hold under either geometric join.** K = 1
   is MCC-admissible on 22 of 22 ladders under `id`, 17 of 22 (primary) and
   16 of 22 (contains). It holds the highest tile-MCC on 13 of 22, 5 of 22 and
   6 of 22.
3. **§ 8.6's sign reversal survives under both joins, as evaluated and
   clipped.** Consensus-only K = 1 → 10 tile-MCC rises (+0.0444 `id`, +0.0380
   primary, +0.0610 contains). Verified, it falls on every reading, and no
   verified change separates (BH p 0.37 to 1.00).
4. **The mechanism diagnostic.** Pooled over the 22 as-evaluated ladders'
   rungs, 67.3 % of `id` false-negative (FN) tiles hold one of the rung's own
   detections. The **share** does not move consistently with K. The
   **counts** do, on the gold-standard frame: from K = 1 to the top rung, `id`
   FN tiles rise on 15 of 15 ladders while the detection count falls on 14.
   The geometric joins' MCC gain over `id` is larger at the top rung on 13
   (primary) and 15 (contains) of 15.

Figures below are read from
`results/k-ladder-2026-09-12/mcc-join-2026-10-30/summary.json`, rendered as
`summary.md` in the same directory, unless another file is named.

## 1. What was done

### 1.1 Code (`58d2ba7d0`, `75895f06e`)

- **`scripts/k_ladder_mcc_test.py`** gains `--tile-join` (`id`,
  `geometric-primary`, `geometric-contains`; default `id`). The default
  invokes the tiering harness exactly as before and writes no new key. A
  geometric join is passed to `era1_leaderboard_tiering.py --tile-join`,
  whose F1 arm (and so the committed-board F1 gate) is unchanged. The
  join-stamped `tiering_<buffer>m_<join>.json` is read. Each pair's rung MCC
  values come from that tiering's MCC ranking, with the published join's
  board-frame values beside them, so a reported `low` and `high` are the same
  statistic as the delta. The join and the harness's withheld counts are
  recorded.
- **`scripts/k_ladder_mcb.py`** gains `--tile-join` for `--metrics mcc` with
  `--registry`. The join reaches `selection_aware_intervals.py --tile-join`.
  The artefact carries the join in its name. The gate compares each rung's
  MCB statistic with the join's MCC in that join's own tiering, and refuses a
  tiering written under any other join. A geometric join with the F1 metric,
  or without a registry, is refused.

### 1.2 Tests and the red sentinel

`tests/test_k_ladder_tile_join_options.py` holds 17 tier-1 tests on
synthetic fixtures with the subprocess boundary monkeypatched. They pin the
default (no flag in either command, the published file names, the legacy key
sets, inventory rung values, default equal to explicit `id`, the MCB gate on
the ranking's `mcc`) and the join (the flag reaches the instrument, the
stamped file is read, rung values are the join's, the gate refuses another
join's tiering and a statistic equal to the published MCC, the refusals).

The red sentinel ran in a real-file copy of `scripts/`, the test module,
`conftest.py`, `config.py` and `pytest.ini` (0 symlinks, 603 files). One
break at a time:

1. `run_tiering` dropping the join flag: 1 failed;
2. the driver ignoring the join's rung values: 1 failed;
3. the default path always passing the flag: 1 failed;
4. the MCB gate reading the published MCC under a join: 2 failed.

Restored, 17 passed, and the copy's sources diffed equal to the worktree's.
The sentinel ran on the code of `58d2ba7d0`; `75895f06e` touches none of
the four broken sites.
`ruff check` is clean on every touched Python file.

### 1.3 The run

On sapphire, in `~/scratch/kladder-mcc-join-2026-10-30/`: `git fetch` in
sapphire's checkout (nothing else touched there), then whole-tree clones
(`git clone --no-checkout`, `checkout --detach 463257349`; 76,750 tracked
files, clean). `ladder_files.py` lists the 235 files the 29 ladders' rungs
name; all exist in the clone and none passes through a symlink (the clone's
75 symlinks are tracked links under `archive/`, `inputs/examples/` and one
`outputs/` directory).

`chain.sh` ran two waves, every job single-threaded, at most 12 at once:

- 12 tiering jobs (Phase 1, Phase 2, tier E and clipped, under each join);
- 6 MCB jobs, the consensus replay, and the mechanism diagnostic.

Every launch redirected all three descriptors, with `;` before `nohup` and
nothing after it. Each job wrote pid and rc files from inside itself.
Watchers read terminal state files and log age, never `pgrep -f`. All 20
jobs ended rc 0. Sapphire was idle at launch (load 0.04).

**Inputs, and two departures from the committed commands, both disclosed:**

- **Phase 2's inventory.** Today's `phase2/ladders-compat.json` holds only
  the 7 unclipped ladders (clipped rebuild `0fc2d6389`), so the as-evaluated
  Phase 2 tests ran on the 13-ladder inventory the committed test read,
  `git show 326181bcd:…/ladders-compat.json`, committed as
  `mcc-join-2026-10-30/inputs/phase2-ladders-compat-326181bcd.json`. Its
  rungs (K, condition id, F1, MCC) equal those of every later version up to
  `32d0c6445`.
- **The `id` MCB ran through `--registry`.** At today's head the default
  `k_ladder_mcb.py` registry cannot run: `label_to_k` reads the same 7-ladder
  inventory, so 24 rung labels have no K (a pre-existing defect, § 4 item 6).
  `make_registries.py` writes `id-registry.json`: the committed registry
  (the same analyses, conditions, bounds, buffers and committed tierings)
  plus each label's K and family name, read by the module's own functions
  pointed at the 13-ladder inventory. The geometric registries are the same
  entries with each `tiering` moved to the join's own tiering.

**Cell counts and clip status** (`summary.json` → `tiering_census`): 87
tierings (29 ladders × 3 joins), 113 cells per join. Phase 1 has 29 rungs
(3.7 arms and the 3.7-verifier stride B 3 each, the others 4), Phase 2 52,
tier E 4, clipped 28. Every clipped ladder's cells are all `-d51clip`
evaluations, and every other ladder's none (0 mixed). No cell was withheld
on either arm under any join.

### 1.4 The tier-1 suite, and the fix it forced

The full tier-1 suite at `463257349`, in a second clone, gave 4,519 passed,
2 failed, 5 skipped, 132 deselected and 3 xfailed. The two failures
(`test_k_ladder_clipped_cells.py::test_mcc_test_resolves_rungs_through_the_named_conditions`
and `::test_mcb_main_runs_the_registry_it_is_given`) were mine: their fakes
take the committed signatures of `run_tiering`, `committed_ranking` and
`run_mcb`, and the drivers passed `tile_join` on every call. `75895f06e`
makes the default path call them argument for argument and adds the keyword
only off the default. At `75895f06e`, in a fresh clone, the full tier-1 suite
gave **4,521 passed, 0 failed** (5 skipped, 132 deselected, 3 xfailed;
`logs/suite2.log`).

The fix cannot change an output, since the keyword's default is the
published join. To show it does not, `verify.sh` re-ran, at `75895f06e` in
another clone, the Phase 2, clipped and tier E jobs and the clipped MCB under
all three joins. All 221 JSON outputs equal the chain's at `463257349` once
the machine root of the absolute `*_override` paths is removed. The only raw
differences are those paths, timestamps and commit stamps
(`logs/verify/compare-normalised.txt`). The Phase 1 and main MCB jobs were
not re-run at `75895f06e`.

## 2. Gate: the `id` join reproduces the committed results

`summarise.py` compares every `id` artefact with its committed counterpart
key by key, in key order, value for value. Set aside, because they cannot
match by construction: run timestamps, commit stamps, the paths of this run's
outputs, the summaries' `source_inventory` (this job's inventory copy) and
`conditions` (a key the driver gained on 2026-10-30, after those summaries),
and absolute `*_override` paths (compared after their machine root is
removed).

| artefact set (committed) | files | result |
|---|---:|---|
| Phase 1 tests, `mcc-test/` (8 ladders, summary, 8 tierings) | 17 | pass |
| Phase 2 tests, `phase2/mcc-test/` (13 ladders, summary, 13 tierings) | 27 | pass |
| clipped tests, `clipped-mcc-2026-10-30/mcc-test/` | 15 | pass, exact |
| MCB, `mcb/` (summary and 44 artefacts, 22 ladders × 2 metrics) | 45 | pass, exact |
| clipped MCB, `clipped-mcc-2026-10-30/mcb/` | 15 | pass, exact |
| tier E, `tier-e/tiering/tiering_20m.json` | 1 | pass, exact |
| consensus sweep, `sweep.csv` cell `g384_ov192` and `tension/grid-overlap.json` | 57 rows, 4 rungs | pass, exact |

**One qualification, stated rather than absorbed.** 40 committed files (the
seven 55-map ladders' per-ladder JSONs and tierings, and all 13 Phase 2
ladders') were written on 2026-09-12 between 06:11 and 08:52 UTC (their
tierings stamp harness commits `156bddf36` and `f724b7a10`). That was before
the harness gained 14 keys: the gate
record's geometry arm (`24e6ae696`, 13:00 UTC that day), the withheld-cell
lists (`670f6ee76`) and the MCC family's tiers and ranking (`30a27f361`, both
2026-09-13). Today's harness writes those keys. In those 40 files every
committed key and value is reproduced. The only additions are those 14 key
paths, and the gate tolerates them only in a file dated before `24e6ae696`.
The GS stride A files and the Phase 1 `summary.json` (2026-10-15) match
exactly, as does everything else in the table. So the committed numbers
reproduce, but those 40 files are not byte-identical to a run at today's
harness.

The MCB gate inside each run also passed under every join
(`gate_all_passed`), as did each tiering's per-cell confusion gates and the
committed-board F1 gate of the 55-map ladders (unchanged under the joins,
because the F1 arm keeps `id`).

**Independent check** (`checks/independent-joins.json`):
`independent_check.py` books points to tiles with its own code (one spatial
join per point set, the § 2 rules of
`reports/tile-mcc-geometric-join-2026-09-12.md` written out again) and
computes each confusion and MCC itself. Over all 113 rungs and three joins,
339 comparisons, it agrees with the MCC each tiering ranked on to four
decimals: **0 mismatches**. The mechanism diagnostic's `id` MCC also matches
every `id` tiering (0 mismatches).

**Gate: passed.**

## 3. The four answers, per join beside `id`

Every delta is (higher K) − (lower K). Each BH p is adjusted within the
ladder's own round-robin; bold marks significance at q = 0.05. Full tables,
including every rung, are in `summary.md`.

### 3.1 Tile-MCC from K = 1 to the best F1 rung

| ladder | pair | `id` | primary | contains |
|---|---|---:|---:|---:|
| 3.7 arm 1 | K1 → K5 | **−0.0099 (0.0168)** | −0.0068 (0.1280) | **−0.0096 (0.0240)** |
| 3.7 arm 2 | K1 → K5 | **−0.0275 (<0.0001)** | **−0.0319 (<0.0001)** | **−0.0339 (<0.0001)** |
| 55-map stride A, r2 | K1 → K10 | −0.0052 (0.1984) | −0.0076 (0.0622) | −0.0066 (0.1226) |
| 55-map stride A, standardised | K1 → K10 | −0.0052 (0.1984) | −0.0076 (0.0622) | −0.0066 (0.1226) |
| GS stride A (board frame) | K1 → K10 | +0.0130 (0.7633) | +0.0214 (0.2166) | +0.0214 (0.2460) |
| 55-map stride B, r2 | K1 → K10 | +0.0031 (0.5592) | **+0.0111 (0.0075)** | +0.0079 (0.0816) |
| 55-map stride B, 3.7 verifier | K1 → K10 | **−0.0112 (<0.0001)** | **−0.0110 (<0.0001)** | **−0.0112 (<0.0001)** |
| 55-map stride B, standardised | K1 → K10 | +0.0031 (0.5832) | **+0.0110 (0.0093)** | +0.0079 (0.0885) |
| MINIMAL text T 0.3 | K1 → K5 | −0.0251 (0.6044) | −0.0253 (0.2854) | −0.0318 (0.2034) |
| MINIMAL text T 0.7 | K1 → K5 | +0.0077 (0.8125) | +0.0000 (1.0000) | +0.0369 (0.1308) |
| MINIMAL text T 1.0 | K1 → K10 | −0.0214 (0.5760) | +0.0170 (0.8772) | −0.0168 (0.6724) |
| HIGH text T 0.3 | K1 → K5 | −0.0263 (0.5689) | +0.0156 (1.0000) | +0.0306 (0.1466) |
| HIGH text T 0.7 | K1 → K10 | −0.0096 (0.8387) | +0.0276 (0.4699) | +0.0300 (0.2984) |
| HIGH text T 1.0 | K1 → K10 | −0.0252 (0.8065) | +0.0164 (0.7116) | −0.0168 (0.6040) |
| MINIMAL image T 0.3 | K1 → K10 | −0.0065 (0.9954) | −0.0132 (0.5155) | +0.0079 (0.8803) |
| MINIMAL image T 0.7 | K1 → K10 | −0.0214 (0.9768) | −0.0096 (0.6636) | −0.0098 (0.9981) |
| MINIMAL image T 1.0 | K1 → K10 | −0.0282 (0.6072) | +0.0079 (0.9779) | +0.0108 (0.8690) |
| HIGH image T 0.3 | K1 → K10 | +0.0024 (0.9886) | +0.0370 (0.1068) | +0.0315 (0.3357) |
| HIGH image T 0.7 | K1 → K5 | −0.0076 (0.8746) | +0.0235 (0.7068) | +0.0380 (0.1890) |
| HIGH image T 1.0 | K1 → K10 | **−0.0637 (0.0420)** | +0.0029 (1.0000) | −0.0236 (0.6214) |
| scale-4-optimal 487 | K1 → K10 | −0.0572 (0.0762) | −0.0048 (0.8991) | −0.0293 (0.6078) |
| tier E, as evaluated | K1 → K5 | −0.0071 (1.0000) | −0.0006 (0.8837) | −0.0003 (1.0000) |
| tier E, D51 clipped | K1 → K5 | −0.0071 (1.0000) | −0.0005 (0.8837) | −0.0002 (1.0000) |

On D51's clipped basis two of the six clipped Phase 2 ladders move
(`summary.md` § 2): HIGH text T 1.0 −0.0290 / +0.0121 / −0.0168 and
MINIMAL image T 0.7 −0.0253 / −0.0139 / −0.0140 (`id` / primary / contains);
the other four equal the table. No direction or significance call changes.

**The counts** (the 21 verified ladders, Phase 1 and Phase 2; identical on
D51's clipped basis):

| join | falls | rises | significant falls | significant rises |
|---|---:|---:|---|---|
| `id` | 16 of 21 | 5 | 4: 3.7 arm 1; 3.7 arm 2; stride B, 3.7 verifier; HIGH image T 1.0 | 0 |
| primary | 9 of 21 | 12 | 2: 3.7 arm 2; stride B, 3.7 verifier | 2: stride B r2; stride B standardised |
| contains | 11 of 21 | 10 | 3: 3.7 arm 1; 3.7 arm 2; stride B, 3.7 verifier | 0 |

Under `id` the 5 non-falls are GS stride A, both stride B ladders, MINIMAL
text T 0.7 and HIGH image T 0.3, as the findings state. One of primary's 12
"rises", MINIMAL text T 0.7, is +0.000019 (0.906370 → 0.906389), effectively
flat. Of the 13 Phase 2 ladders, tile-MCC falls on 11 under `id`, 4 under
primary and 6 under contains.

**The other significant tile-MCC pairs** (adjacent rungs):

- **`id`** (as findings § 4.1): 3.7 arm 1 K1 → K3 −0.0067 (0.0498) and
  K3 → K5 −0.0032 (0.0498); 3.7 arm 2 K1 → K3 −0.0258 (<0.0001); both stride
  A ladders K3 → K5 −0.0111 (0.0066) and K5 → K10 +0.0047 (0.0300); stride
  B, 3.7 verifier K1 → K3 −0.0095 (<0.0001). No Phase 2 pair.
- **primary**: 3.7 arm 2 K1 → K3 −0.0302 (<0.0001); both stride A ladders
  K3 → K5 −0.0160 (<0.0001) and K5 → K10 +0.0067 (0.0016); **both stride B
  ladders K1 → K3 +0.0114 (0.0072)**; stride B, 3.7 verifier K1 → K3 −0.0089
  (0.0006). No Phase 2 pair.
- **contains**: 3.7 arm 1 K3 → K5 −0.0055 (0.0045); 3.7 arm 2 K1 → K3
  −0.0288 (<0.0001) and K3 → K5 −0.0052 (0.0094); both stride A ladders
  K3 → K5 −0.0139 (<0.0001) and K5 → K10 +0.0049 (0.0232); stride B, 3.7
  verifier K1 → K3 −0.0094 (0.0001); **MINIMAL text T 0.3 K3 → K5 −0.0443
  (0.0108), HIGH text T 0.3 K1 → K3 +0.0516 (0.0483) and HIGH text T 0.7
  K1 → K3 +0.0632 (0.0054)**; the clipped MINIMAL text T 0.3 likewise.

The stride A pattern (a significant K3 → K5 fall then a significant K5 → K10
rise) holds under all three joins.

### 3.2 The tile-MCC MCB admissible sets

| join | ladders | K = 1 admissible | K = 1 highest | highest at K = 1 / 3 / 5 / 10 | whole ladder admissible | K = 10 excluded |
|---|---:|---:|---:|---|---:|---:|
| `id` | 22 | 22 | 13 | 13 / 6 / 1 / 2 | 13 | 6 |
| primary | 22 | 17 | 5 | 5 / 8 / 3 / 6 | 9 | 5 |
| contains | 22 | 16 | 6 | 6 / 7 / 4 / 5 | 10 | 4 |
| `id`, clipped | 7 | 7 | 6 | 6 / 1 / 0 / 0 | 6 | 0 |
| primary, clipped | 7 | 7 | 1 | 1 / 2 / 1 / 3 | 4 | 1 |
| contains, clipped | 7 | 7 | 1 | 1 / 3 / 2 / 1 | 6 | 0 |

K = 1 is ruled out as best on tile-MCC under **primary** on HIGH text T 0.7,
HIGH text T 1.0, HIGH image T 0.3 and both stride B ladders; under
**contains** on MINIMAL text T 0.7, HIGH text T 0.3, HIGH text T 0.7, HIGH
image T 0.7 and both stride B ladders. The `{K = 1}`-only sets of the stride
B 3.7-verifier ladder and 3.7 arm 2 hold under all three joins. Each ladder's
set and highest rung per join are in `summary.md` § 3. The F1 sets do not
depend on the join (the F1 arm keeps `id`) and reproduce the committed ones.

### 3.3 § 8.6: K = 1 → 10, consensus-only against verified

| join | consensus only | verified, as evaluated (BH p) | verified, D51 clipped (BH p) | swing, as evaluated / clipped | reversal |
|---|---:|---:|---:|---:|---|
| `id` | 0.4465 → 0.4909 (+0.0444) | 0.8211 → 0.7973 (−0.0238, 0.8094) | 0.8133 → 0.7973 (−0.0161, 1.0000) | 0.0682 / 0.0604 | yes / yes |
| primary | 0.5413 → 0.5793 (+0.0380) | 0.9330 → 0.9113 (−0.0216, 0.3682) | 0.9242 → 0.9113 (−0.0128, 0.8363) | 0.0597 / 0.0509 | yes / yes |
| contains | 0.4935 → 0.5544 (+0.0610) | 0.8935 → 0.8813 (−0.0122, 0.6490) | 0.8850 → 0.8813 (−0.0037, 1.0000) | 0.0732 / 0.0647 | yes / yes |

The consensus side is `consensus/grid-overlap-joins.json`: the grid sweep of
cell `g384_ov192` replayed with `scripts/grid_analysis.py`'s own functions
(57 detection sets), each scored under the three joins. F1 and the detection
count are identical across the joins, so each K's operating point (best F1)
is the same under all three. The verified side is the tier E tierings, as
evaluated and clipped. The sign reversal survives under both geometric joins
on both bases. Its size moves either way: the swing is 0.0597 / 0.0509
(primary) and 0.0732 / 0.0647 (contains), against 0.0682 / 0.0604 under
`id`. The contains clipped verified change is −0.0037. As under `id`, no
verified change separates, so the claim stays one about the shift between
stages.

### 3.4 The mechanism, descriptively

`mechanism/id-join-mechanism.json` counts, per rung under `id`, the FN tiles
and those that geometrically contain one of the rung's own detections. This
is descriptive. It is not a decomposition of any MCC change.

- **Pooled** over the 22 as-evaluated ladders' rungs: 19,671 of 29,227 FN
  tiles (67.3 %). The Era-2 board's figure was 59.6 %.
- **The share does not change consistently with K.** From K = 1 to the top
  rung it rises on 8 and falls on 7 of the 15 gold-standard-frame ladders,
  and rises on 1 and falls on 6 of the 7 deployment ladders. Per rung it lies
  between 0.5625 (GS stride A, K = 3) and 0.8182 (tier E, K = 3)
  (`summary.md` § 5).
- **The counts do, on the gold-standard frame (487 tiles).** From K = 1 to
  the top rung, on the 15 ladders (GS stride A, the 13 Phase 2 ladders, tier
  E):

| quantity, K = 1 → top rung | rises | falls |
|---|---:|---:|
| detections in the cell | 1 | 14 |
| FN tiles under `id` | 15 | 0 |
| FN tiles holding one of the rung's detections | 15 | 0 |
| geometric − `id` MCC gain larger at the top rung (primary / contains) | 13 / 15 | — |

On the 7 deployment ladders (8,541 tiles) the detection count falls on all 7,
but FN tiles rise on 4 and fall on 3, and the gain is larger at the top rung
on 4 (primary) and 3 (contains).

An example, from `checks/independent-joins.json`: HIGH image T 1.0's cells
hold 490, 418, 410 and 414 detections at K = 1, 3, 5, 10. Their `id` FN
tiles go 17, 32, 36, 42, and their `geometric-primary` FN tiles 6, 13, 12,
13.

## 4. Surprises, flagged and not explained away

1. **Most of the K-ladder tile-MCC decline is a property of the `id`
   reading.** Under `id`, tile-MCC falls on 16 of 21 ladders from K = 1 to
   the best rung. Under the geometric joins it falls on 9 and 11, and on the
   gold-standard Phase 2 ladders the majority direction reverses under
   primary (falls on 4 of 13, against 11 under `id`). This contradicts
   R3-13, findings § 4.3 ("the same direction § 4 reported on the eight, now
   on fourteen more ladders") and § 7.2 ("the direction holds") wherever
   the join is geometric. The pipeline was checked before
   this was written: the `id` runs reproduce every committed value (§ 2), the
   F1 arm is unchanged under the joins, every cell's geometric MCC was
   reproduced by independent code (339 of 339), and no cell was withheld.
2. **A significant tile-MCC rise appears under `geometric-primary`**, on
   both 55-map stride B ladders (K1 → K10 +0.0111 and +0.0110; K1 → K3
   +0.0114 on each). This contradicts "no ladder shows a significant
   tile-MCC rise" (R3-13, findings § 4.1 item 2) under that join. Under
   `geometric-contains` the same pair rises without separating (BH p 0.0816,
   0.0885), and the contains reading has two significant intermediate rises
   (HIGH text T 0.3 and T 0.7, K1 → K3).
3. **HIGH image T 1.0's significant fall (−0.0637), the one significant
   Phase 2 decline, does not survive either join** (+0.0029 primary, −0.0236
   contains, BH p 1.0000 and 0.6214). Findings § 7.2 reads its shape as
   "exactly the mechanism § 4 proposed". Under `id` this ladder's FN tiles
   rise from 17 to 42 while its detections fall from 490 to 414.
4. **The 3.7-verifier and 3.7-arm declines are robust.** Stride B under the
   3.7 verifier (about −0.011) and 3.7 arm 2 (about −0.03) fall significantly
   under all three joins, and their MCC-admissible set is {K = 1} under all
   three. 3.7 arm 1's fall separates under `id` and contains but not primary
   (BH p 0.1280).
5. **R3-12's "K = 1 admissible on tile-MCC on 22 of 22" is an `id`
   result** (17 and 16 under the joins), and "highest on 13" becomes 5 and
   6. Under the geometric joins the highest-MCC rung spreads across K = 1, 3,
   5 and 10.
6. **Pre-existing defects found on the way.**
   - **(a)** `k_ladder_mcb.py`'s default registry no longer runs at `main`:
     `label_to_k` and `display_names` read `phase2/ladders-compat.json`, which
     `0fc2d6389` cut to 7 ladders, 1 h 41 min after the committed
     `mcb/summary.json` was written. 24 rung labels have no K, so re-running
     the committed command would fail in `summarise`. Not fixed here: it
     touches the default path.
   - **(b)** The committed Phase 1 `mcc-test/summary.json` (2026-10-15) sits
     beside seven per-ladder files and tierings from 2026-09-12. Only the GS
     ladder was re-run at the restatement. Their numbers reproduce (§ 2).
   - **(c)** Also noted, unchanged: `k_ladder_mcb.py`'s `table.md` has no
     heading (MD041), as the clipped record found. The six such renderings
     were left out of the commit; their JSON is in.
7. **The diagnostic's share is higher on the ladders than on the board**
   (67.3 % against 59.6 %), but the share is flat in K. What moves with K on
   the gold-standard frame is the count: higher-K cells hold fewer points
   while matching more mounds, and under `id` they leave more
   reference-positive tiles unnamed. This is consistent with the board
   record's hypothesis (the `id` asymmetry penalises sets that keep fewer
   points per mound). It is still not a test of it: points per mound were
   not counted, and how a merged point's `source_tile` is chosen was not
   examined.

## 5. Not done, choices made, and options for the PI

**Not done:**

- no findings document, the register, `docs/paper/`, `docs/notes/` or
  `planning/` was edited (by instruction). No pull request was opened;
- the Gemini 3.7 gold-standard text ladder, the 23rd, stays withheld: its
  F1 arm is refused under `id`, which the geometric joins do not change, so it
  enters no family here;
- § 4.2's per-map sign-swap instrument (two stride ladders) was not re-run.
  `stride55_ladder.py` has no tile-join option;
- points per mound, and the tile-exchangeability question that overlapping
  tiles raise for every tile-swap test under any join
  (`reports/tile-mcc-geometric-join-2026-09-12.md` § 6 item 4).

**Choices made, disclosed, each reversible:**

- the 13-ladder Phase 2 inventory from `326181bcd`, and the `id` MCB through
  a registry equal to the committed one (§ 1.3);
- gating 40 committed 2026-09-12 files on reproduction of every committed
  key and value, tolerating only the 14 keys the harness gained afterwards
  (§ 2);
- K1 → best rung is by F1, as committed; "falls" and "rises" are by sign,
  so +0.000019 counts as a rise.

**For the PI: how the paper words the K-ladder MCC claims.** Options, not
chosen here (they parallel the board record's § 5):

- **A.** Keep the `id` claims (R3-12's tile-MCC half, R3-13, findings §§ 4.1,
  4.3, 7.2) and add that the majority decline, "no significant rise", HIGH
  image T 1.0's fall and K = 1's admissibility on 22 of 22 hold under the
  published join and not under the geometric joins.
- **B.** Narrow to what holds under all three joins. F1 rises with K. The 3.7
  verifier and 3.7 arm 2 lose tile-MCC significantly, and their
  MCC-admissible set is {K = 1}. Stride A falls from K3 to K5 and rises from
  K5 to K10 significantly. § 8.6's sign reversal holds (its size moves, from
  0.0509 to 0.0732), with no verified change separating.
- **C.** Revisit the published join itself. § 3.4 is the K-ladder evidence
  that bears on whether `id` measures "the per-tile decision the model
  actually made" (S153 ruling 6) for merged detection sets.

**Observation candidate** (for the PI's verdict; nothing written to
`docs/notes/`): the K-ladder's "tile-MCC does not follow F1" is largely a
property of the `id` reading. Under either geometric join the decline is a
minority or near-even direction, and under `geometric-primary` two ladders
rise significantly. On the gold-standard frame the `id` FN tiles rise with K
on every ladder as detection counts fall. The robust exceptions are the
Gemini 3.7 ladders. It is a correction candidate to R3-12's tile-MCC half,
R3-13 and findings §§ 4.1, 4.3 and 7.2; § 8.6 (R3-14) survives.

## 6. Reproduce

All on sapphire, US$0, from `463257349` (`75895f06e` gives the same outputs,
§ 1.4). Scripts are in `reports/s166-agent-records/k-ladder-mcc-join-scripts/`;
`logs/` holds the chain's job logs and the input listing.

```bash
S=$HOME/scratch/kladder-mcc-join-2026-10-30; T=reports/s166-agent-records/k-ladder-mcc-join-scripts
git clone --no-checkout "$HOME/Code/map-reader-llm" "$S/wt"
git -C "$S/wt" checkout --detach 463257349
cd "$S"; nohup bash "$S/wt/$T/chain.sh" "$S/wt" "$S/logs" > "$S/logs/chain.log" 2>&1 < /dev/null &
# once logs/chain.state reads DONE, from $S/wt:
python "$T/independent_check.py" . results/k-ladder-2026-09-12/mcc-join-2026-10-30/inputs/phase2-ladders-compat-326181bcd.json \
  results/k-ladder-2026-09-12/mcc-join-2026-10-30/checks/independent-joins.json
python "$T/summarise.py" .
python "$T/render.py" results/k-ladder-2026-09-12/mcc-join-2026-10-30/summary.json \
  results/k-ladder-2026-09-12/mcc-join-2026-10-30/summary.md 2026-10-30 463257349
```

Wall-clock (`logs/*.log`): the chain took about 10 minutes. In wave A the
tier E jobs took about 5 s, the clipped and Phase 2 jobs 30 s to 1 min, and
the Phase 1 jobs (8,541-tile 55-map cells) 3.5 to 4 min; in wave B the
longest job, the `id` MCB, took 6 min. The tier-1 suite took about 5 min.

## Changelog

### 2026-10-30 — Original publication

Written by the S166 K-ladder tile-join job on branch
`kladder-mcc-join-2026-10-30`. It records the gate (passed, with the 40-file
schema qualification), the per-join tables, the four answers, the surprises
of § 4 and the open decisions of § 5.
