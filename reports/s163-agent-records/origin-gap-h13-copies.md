# D62 (1): the origin gap in the H13 chain and the consensus library copies

> **Last revised**: 2026-10-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), an overnight subagent of the main Session 163
  session (workstream `origin-gap-h13-copies`). Every number below was
  read from the run outputs on sapphire by the workstream agent on
  2026-10-13 before it was written here.
- **Date**: 2026-10-13 (UTC).
- **Repository**: `map-reader-llm`, branch `origin-gap-h13-copies` from
  `main` at `e8a7f4363`, with `main` at `04575a51a` merged in (`5cd9a5606`;
  the merged PRs touch none of the files or code paths measured here). Fixes: `7ab2caa9f` (H13 chain), `6ccf097d0`
  (its real-data test), `25943b776` (library copies).
- **Ruling**: PI ruling D62 (1) (`planning/pi-decisions-2026-09-20.md`):
  "the route is fixed in all four chains and in the other copies
  (`scripts/analyse_diversity.py`'s own `consensus_to_gdf`,
  `generate_consensus_gdf`, `build_pv_gdf`, and W2.7's `cluster_subset`)
  [...] the affected boards are re-scored on sapphire, and how they move
  is reported before any document or signature changes". This record
  covers the H13 chain and the three library copies. W2.7's
  `cluster_subset` is reported separately, on the stacked branch
  `origin-gap-w27`. The grid, plateau, and Image-B chains belong to
  another agent and are not touched here.
- **Finding being fixed**: `reports/s163-agent-records/scorer-restatement-inventory.md`
  §§ 3, 4, and 9 (PR #39), and the D60 (3) fix of
  `analyse_consensus_sweep.consensus_to_gdf` (PR #37,
  `reports/s163-agent-records/d60-3-consensus-route.md`).
- **Where the runs are**: `~/scratch/origin-gap-h13-copies-2026-10-13/` on
  sapphire: `out/{old,new1,new2}/` (the H13 chain), `copies/{old,new1,new2}/`
  (the library copies), `diffs/` (comparisons and summaries), `logs/`,
  `pids/`, `bin/` (drivers), `trees/` (disposable `git archive` copies).
  The drivers and the summaries are committed beside this record in
  `origin-gap-h13-copies-scripts/`.
- **Guarantees**: no model Application Programming Interface (API) call;
  nothing merged; no committed result, document, or register row was
  changed (every regenerated output lives in scratch); at most four
  processes on sapphire at a time; the shared checkout on sapphire was not
  touched. The kernel's "bad page" count read 0 before and after every run.

**Conventions.** "Committed" is the file on `main`. "OLD" is `main`'s code
(a `git archive` of `e8a7f4363`) run today; "NEW" is this branch. NEW was
run twice: "NEW1" in the branch clone, "NEW2" in a `git archive` of the fix
commit, in new processes. Every NEW number below is identical in both runs
(§ 4). F1 is at 20 m unless stated.

## Bottom line

1. **H13's registered analysis (signed `h13-overlap-2026-08-18`, arms A, B,
   and C) does not move with the fix.** Its per-pass sets already record
   their origins (`origin_tiles`), and the fixed code reproduces today's
   `h13_overlap_analysis.json` and `per_tile_counts.json` exactly. **No H13
   verdict changes.** The movement D50 itself causes there (arm F1 A 0.5578
   → 0.5733, B 0.5198 → 0.5301, C 0.4025 → 0.4116; A − B ΔF1 0.0380 →
   0.0432, CI95 [+0.0009, +0.0708] → [+0.0055, +0.0775], p 0.0385 → 0.0237)
   was first measured inside the memory-fault window (D57 (4) Phase 3);
   both runs here reproduce it exactly.
2. **The post-hoc sub-analyses move, all upwards.** The tier-0 aggregation
   sweep: 18 of 27 cells, by +0.0050 to +0.0162 F1, relative to PR #35's
   regenerated `tier0_sweep.json` (which today's pre-fix code reproduces
   exactly). Arm C's best cell stays best (0.7114 → 0.7191), but **arm A's
   best cell now edges arm B's** (0.6426 against 0.6415, where it was
   0.6264 against 0.6331). The K-sensitivity diagnostic moves 50 of 75 cells
   per pool (up to +0.0155) with every K's best cell and the
   interior-or-edge pattern unchanged; the tile-size grid moves 38 of 57
   cells (up to +0.0237) with its ordering unchanged. None of these is
   registered; Obs 416 quotes the tier-0 best cells and would need a dated
   note.
3. **The library copies are fixed, and no committed output they feed would
   move.** `generate_consensus_gdf` and `build_pv_gdf` (242 arms behind the
   pairwise effect sizes and the Phase 3a HIGH sweep): no row's attribution
   changes. `analyse_diversity.consensus_to_gdf` (the 225 Phase 3c
   diversity arms): 885 rows in 124 arms are now matched on their origin
   sheet, but no arm's precision, recall, or F1 changes, and the per-tile
   tables the intervals resample are identical (§ 3.3).
4. **Two items for the PI** (§ 5): `h13_k_sensitivity.py`'s decomposition
   hard-codes the pre-fix shared-scope value 0.6463, which the fix moves to
   0.6687, so the "footprint effect" it logs (−0.0224) is an artefact; and
   rewriting the H13 prepared sets on today's code (a D50 consequence, not
   this fix) would move the A − B p from 0.0237 to 0.0231.

## 1. The H13 chain

### 1.1 The gap and the fix

`prepare_h13_scoring.assign_primary_tiles` delegates to
`lib_advanced_metrics.assign_primary_tiles_on_origin_sheet`, which keeps
the nearest-centroid tile but restricts it to the detection's origin sheet,
read from `origin=` or from the rows' origin columns. A row with no origin
keeps the legacy rule, the nearest tile among ALL frame tiles. Two H13
paths reached it with bare centroids:

- `h13_k_sensitivity.cluster_votes` returns centroids and votes only, and
  `score()` tiled them with no origin;
- `h13_aggregation_sweep.write_cell` built its frame from
  `cluster_across_passes` clusters but kept only centroid, label, and
  votes, dropping each cluster's `source_tiles`. The tile-size grid
  (`h13_tilesize_overlap_grid.py`) inherits `write_cell`.

The per-pass path of the registered analysis is not affected:
`prepare_h13_scoring.write_dedup_geojson` writes `origin_tiles` and tiles
each row through it, and the scorer reads the column.

The fix (`7ab2caa9f`):

- `h13_k_sensitivity.cluster_votes_with_origins` is `cluster_votes`, step
  for step, also returning each cluster's sorted union of member tiles.
  `cluster_votes` itself is unchanged, because the grid, plateau, stride,
  Image-B, W2.7, and Gemini 3.7 ladder chains import it with its two-value
  contract. `score(..., origins=)` tiles each cluster on its own sheet and
  carries the list as `source_tiles`.
- `write_cell` passes each cluster's tiles to `assign_primary_tiles` as its
  origin and records them as `origin_tiles` (the `;`-joined convention
  `write_dedup_geojson` uses) in the frame and in the cell file, so the
  in-memory cell and its file are attributed alike.

**Tests.** `tests/test_h13_origin_route.py` (9 tier-1) builds two sheets
whose tiles overlap by 100 m, with a cluster seen on sheet A but nearer
sheet B's tile centre. It checks that `cluster_votes_with_origins` clusters
exactly as `cluster_votes`, that `score` and `write_cell` score the cluster
on A, and that a cluster lying on no tile of its own sheet is out of frame.
`tests/test_h13_origin_route_real.py` (1 tier-2) rebuilds the tier-0 arm A
cell at `c ≥ 1`, `k ≥ 3` from the committed passes: F1 0.642599 on the
origin route, the same from its written file, and 0.626354 with its
centroids tiled without origins (9 clusters change sheet). **Red
sentinel**, in real copies (`git archive` plus `cp`): on `main`'s code the
tier-1 module fails to import and the tier-2 test fails; each of four
single mutations (score ignoring the origins, empty origins, `write_cell`
tiling without them, the file losing `origin_tiles`) turns one to three
tests red; the fixed code passes all ten.

### 1.2 What was run

Four jobs per tree, all on sapphire: the tier-0 sweep
(`h13_aggregation_sweep.py`, B = 1,000), the K-sensitivity diagnostic
(`h13_k_sensitivity.py`), the tile-size grid (`h13_tilesize_overlap_grid.py`),
and the overlap analysis (`h13_overlap_analysis.py`, B = 1,000 and 10,000,
10,000 permutations) on the committed prepared sets. NEW1 and NEW2 also
rewrote the 18 prepared sets on today's code (`reprep.py`, the
deduplicate-and-write stage of `prepare_h13_scoring.py` with the committed
bounds; the arm B and C tile metadata that its bounds stage needs is not in
the repository) and re-ran the overlap analysis on them.

**OLD reproduces the committed files.** The tier-0 sweep equals PR #35's
regenerated `tier0_sweep.json` (branch `d61-regenerations`, `75abef2ab`)
leaf for leaf, ignoring only `generated_at_utc`, and its Markdown and 27
cell files equal `main`'s byte for byte. The K-sensitivity and tile-size
JSONs equal `main`'s (ignoring `generated_at_utc`), and so do the tile-size
cells and bounds. So every "before" value below is the committed (or
PR #35's) value, and NEW − before is the fix alone.

### 1.3 The registered overlap analysis: unchanged by the fix

NEW's `h13_overlap_analysis.json` equals OLD's leaf for leaf (ignoring
`generated_at_utc`) and its `per_tile_counts.json` byte for byte. Against
the committed file, both differ by D50's attribution (the scorer restores
each per-pass row to the sheet its `origin_tiles` name), not by this fix:

| Quantity | Committed | Today (OLD = NEW) |
|---|---:|---:|
| Arm A micro-F1 (P, R) | 0.5578 (0.4484, 0.7379) | 0.5733 (0.4608, 0.7584) |
| Arm B micro-F1 (P, R) | 0.5198 (0.3887, 0.7844) | 0.5301 (0.3964, 0.7999) |
| Arm C micro-F1 (P, R) | 0.4025 (0.2616, 0.8717) | 0.4116 (0.2676, 0.8916) |
| A − B ΔF1, CI95 (B = 1,000), p | +0.0380 [+0.0009, +0.0708], 0.0385 | +0.0432 [+0.0055, +0.0775], 0.0237 |
| A − B, CI95 (B = 10,000) | [+0.0015, +0.0741] | [+0.0060, +0.0795] |
| A − C ΔF1, CI95 (B = 1,000) | +0.1554 [+0.1214, +0.1889] | +0.1617 [+0.1270, +0.1943] |
| B − C ΔF1, CI95 (B = 1,000) | +0.1174 [+0.0922, +0.1437] | +0.1185 [+0.0926, +0.1451] |
| Low-margin subgroup recall (A, B, C) | 0.2667, 0.7667, 0.9333 | unchanged |
| High-margin subgroup recall (A, B, C) | 0.7468, 0.7847, 0.8706 | 0.7677, 0.8005, 0.8908 |

**Verdicts**: all three contrasts still exclude zero, the ordering is still
monotone, and the edge reading stands (the ten low-margin mounds' recalls
are unchanged; recall elsewhere rises in all three arms). These are the D57 (4) Phase 3
"NEW" values (`reports/s163-agent-records/d57-4-rescore-s3-deltas.md`
§ Per test, item 1), which were computed on 2026-10-09 inside the
memory-fault window and are listed for recheck as W1-14 in
`reports/s163-agent-records/fault-window-recheck-list.md`; two independent
runs reproduce them here.

**Rewritten prepared sets (a D50 consequence, not this fix).** The
committed prepared sets were tiled on 2026-08-18 under the legacy rule. The
scorer restores each row's sheet for matching, but the per-tile table books
a row's TP or FP to its recorded `source_tile`, which for a re-keyed row is
the neighbouring sheet's tile. Rewritten on today's code, the 18 sets keep
every detection, coordinate, order, and property except `source_tile`,
which changes on 12 to 22 rows per common-scope pass (5 to 20 per
native-scope pass), every one a change of sheet. On those sets no F1,
precision, or recall moves, but the per-tile tables do: A − B CI95
(B = 1,000) [+0.0055, +0.0775] → [+0.0054, +0.0781], p 0.0237 → 0.0231
(B = 10,000: [+0.0060, +0.0795] → [+0.0061, +0.0797]); A − C and B − C move
in the fourth decimal of their bounds. No verdict changes. Whether the
re-signing should use rewritten sets is for the PI (§ 5).

### 1.4 The tier-0 aggregation sweep (post-hoc, E41-class)

Before = PR #35's regenerated file (today's pre-fix code; points also equal
`main`'s); after = NEW. F1 with BCa CI95, B = 1,000, seed 42. "Sheet"
counts the clusters whose `source_tile` moves to another sheet. No cell's
detection count changes, and no cluster is left without a tile.

| Arm | c | k | n | Sheet | Before (PR #35) | After | ΔF1 |
|---|---:|---:|---:|---:|---|---|---:|
| A | 1 | 1 | 1,284 | 23 | 0.4753 [0.4086, 0.5314] | 0.4896 [0.4316, 0.5462] | +0.0143 |
| A | 1 | 2 | 798 | 12 | 0.6183 [0.5570, 0.6733] | 0.6332 [0.5778, 0.6843] | +0.0150 |
| A | 1 | 3 | 570 | 9 | 0.6264 [0.5639, 0.6803] | 0.6426 [0.5858, 0.6938] | +0.0162 |
| A | 2 | 1 | 73 | 2 | 0.1768 [0.1360, 0.2262] | 0.1833 [0.1419, 0.2342] | +0.0065 |
| A | 2 | 2 | 58 | 2 | 0.1544 [0.1153, 0.2010] | 0.1611 [0.1208, 0.2092] | +0.0067 |
| A | 2 | 3 | 35 | 2 | 0.0977 [0.0656, 0.1417] | 0.1047 [0.0718, 0.1500] | +0.0070 |
| A | 3 | 1 | 3 | 0 | 0.0111 [0.0033, 0.0275] | unchanged | 0 |
| A | 3 | 2 | 3 | 0 | 0.0111 [0.0033, 0.0275] | unchanged | 0 |
| A | 3 | 3 | 2 | 0 | 0.0074 [0.0000, 0.0222] | unchanged | 0 |
| B | 1 | 1 | 1,648 | 26 | 0.4190 [0.3595, 0.4728] | 0.4291 [0.3717, 0.4802] | +0.0101 |
| B | 1 | 2 | 930 | 9 | 0.5872 [0.5277, 0.6434] | 0.5981 [0.5386, 0.6503] | +0.0109 |
| B | 1 | 3 | 653 | 6 | 0.6331 [0.5756, 0.6874] | 0.6415 [0.5860, 0.6933] | +0.0084 |
| B | 2 | 1 | 256 | 2 | 0.4433 [0.3860, 0.4939] | 0.4484 [0.3922, 0.5005] | +0.0050 |
| B | 2 | 2 | 181 | 2 | 0.3978 [0.3373, 0.4561] | 0.4033 [0.3430, 0.4614] | +0.0056 |
| B | 2 | 3 | 129 | 2 | 0.3238 [0.2682, 0.3811] | 0.3298 [0.2734, 0.3880] | +0.0060 |
| B | 3 | 1 | 34 | 0 | 0.0979 [0.0676, 0.1423] | unchanged | 0 |
| B | 3 | 2 | 26 | 0 | 0.0851 [0.0539, 0.1266] | unchanged | 0 |
| B | 3 | 3 | 18 | 0 | 0.0576 [0.0325, 0.0944] | unchanged | 0 |
| C | 1 | 1 | 2,752 | 36 | 0.2948 [0.2487, 0.3441] | 0.3021 [0.2538, 0.3487] | +0.0073 |
| C | 1 | 2 | 1,476 | 17 | 0.4717 [0.4129, 0.5299] | 0.4826 [0.4231, 0.5378] | +0.0109 |
| C | 1 | 3 | 988 | 7 | 0.5872 [0.5270, 0.6481] | 0.5963 [0.5352, 0.6547] | +0.0092 |
| C | 2 | 1 | 831 | 8 | 0.6340 [0.5703, 0.6915] | 0.6457 [0.5826, 0.7005] | +0.0117 |
| C | 2 | 2 | 626 | 6 | 0.7079 [0.6534, 0.7552] | 0.7182 [0.6700, 0.7663] | +0.0103 |
| C | 2 | 3 | 505 | 4 | 0.7114 [0.6567, 0.7602] | 0.7191 [0.6673, 0.7659] | +0.0077 |
| C | 3 | 1 | 445 | 0 | 0.6714 [0.6115, 0.7216] | unchanged | 0 |
| C | 3 | 2 | 346 | 0 | 0.6584 [0.6004, 0.7116] | unchanged | 0 |
| C | 3 | 3 | 266 | 0 | 0.6144 [0.5573, 0.6730] | unchanged | 0 |

**Reading.**

- Each arm's best cell keeps its (c, k): A (1, 3) 0.6264 → 0.6426, B (1, 3)
  0.6331 → 0.6415, C (2, 3) 0.7114 → 0.7191 (P 0.7347 → 0.7426, R 0.6896 →
  0.6970, n 505).
- **Surprise, flagged**: arm A's best cell now edges arm B's (0.6426
  against 0.6415, a 0.0011 gap; before, B led by 0.0067). The sweep tests
  no contrast between arms, and the two intervals overlap almost entirely,
  so this is a change of order inside noise, not a finding. It does mean
  "B ahead of A after aggregation" should not be read from this sweep.
- The headline reading, that overlap's ranking inverts under aggregation
  (arm C best), stands, and by more than before only at c ≥ 2.
- The nine unmoved cells are the `c ≥ 3` cells, in which no cluster
  changes sheet.
- Obs 416 (`docs/notes/working-notes.md`) quotes 0.7114 (P 0.7347, R
  0.6896, n = 505), 0.6264, and 0.6331, and cites `tier0_sweep.md`; those
  three values become 0.7191 (P 0.7426, R 0.6970), 0.6426, and 0.6415 under
  the fix. Its "0.4025 → 0.7114 for the arm itself" also uses the
  pre-D50 single-pass 0.4025 (0.4116 today).

### 1.5 The K-sensitivity diagnostic (post-hoc)

Both 384 px pools (`minimal-t1.0`, `minimal-t0.7`), K ∈ {3, 5, 7, 10},
c ∈ {1, 2, 3}, every k: 75 cells per pool.

- **50 of 75 cells move in each pool**, all upwards: +0.0036 to +0.0122
  (T 1.0) and +0.0036 to +0.0155 (T 0.7). No detection count changes, and
  the corroboration profiles are identical.
- **Every K's best cell keeps its (c, k)**, so the interior-or-edge reading
  is unchanged (T 1.0: interior only at K = 10, k = 9; T 0.7: at the edge
  at every K):

| Pool | K | Best (c, k) | Before | After |
|---|---:|---|---:|---:|
| T 1.0 | 3 | (1, 3) | 0.6236 | 0.6332 |
| T 1.0 | 5 | (1, 5) | 0.6525 | 0.6631 |
| T 1.0 | 7 | (1, 7) | 0.6555 | 0.6667 |
| T 1.0 | 10 | (1, 9) | 0.6565 | 0.6687 |
| T 0.7 | 3 | (1, 3) | 0.6007 | 0.6143 |
| T 0.7 | 5 | (1, 5) | 0.6268 | 0.6415 |
| T 0.7 | 7 | (1, 7) | 0.6267 | 0.6422 |
| T 0.7 | 10 | (1, 10) | 0.6231 | 0.6352 |

- **The decomposition (diagnostic A) moves**: the 9-of-10 native-scope F1
  0.6565 → 0.6687 (P 0.5883 → 0.5993, R 0.7425 → 0.7563; 549 detections).
  Its recorded story ("10 detections change map sheet and move F1 by
  0.0102", residual to the committed 0.6667) was the legacy tie-break this
  fix removes: on the origin route the chain now reads 0.0020 ABOVE the
  committed consensus cell. See § 5 for the hard-coded constant.
- The committed protocol erratum
  (`docs/methodology/preregistration/protocol-errata.md`, the paragraph
  citing `k-sensitivity/k_sensitivity.json`) describes the H13 chain's
  nearest-centroid assignment as offsetting it from other chains by about
  0.01 F1; under D50 and this fix that offset is the origin rule's, which
  the PI may want noted there.

### 1.6 The tile-size × overlap grid (post-hoc)

57 cells on the 384 px ∩ 512 px common scope (unchanged: 332 carrier tiles).

- **38 of 57 cells move**, all upwards, +0.0036 to +0.0237 (the largest at
  384 px, K = 10, c ≥ 1, k ≥ 10, where 12 clusters change sheet). No
  detection count changes; no cluster is left without a tile.
- Best cell per (configuration, K) keeps its (c, k):

| Configuration | K | Best (c, k) | Before | After |
|---|---:|---|---:|---:|
| 384 px, 12.5 % | 10 | (1, 9) | 0.6463 | 0.6687 |
| 384 px, 12.5 % | 3 | (1, 3) | 0.6139 | 0.6332 |
| 512 px, 12.5 % | 3 | (1, 3) | 0.6309 | 0.6506 |
| 512 px, 50 % | 3 | (2, 3) | 0.7247 | 0.7341 |

- The ordering at matched K = 3 (512 px 50 % > 512 px 12.5 % > 384 px
  12.5 %) is unchanged. The 384 px K = 10 best cell now equals the
  K-sensitivity decomposition's native-scope value exactly (0.6687, 549
  detections both), so the "footprint effect" between the two scopes (the
  shared-scope F1 minus the native-scope F1, which the diagnostic logged as
  −0.0102 from the values in `k_sensitivity.json`) is 0.0000 on the origin
  route.

## 2. The library copies

### 2.1 The fixes (`25943b776`)

Carried from PR #37's fix of `analyse_consensus_sweep.consensus_to_gdf` and
`evaluate_pv_results.build_candidate_gdf`:

- `lib_consensus.generate_consensus_gdf` wrote the alphabetically first
  member into `source_tile` and dropped the member list. It now keeps
  `source_tiles` (one list per row, parsed by `parse_tile_list`);
  `source_tile` is unchanged.
- `lib_consensus.build_pv_gdf` dropped each candidate's
  `properties.source_tiles`; it now keeps them (an empty list where none is
  recorded, which the scorer treats as before).
- `analyse_diversity.consensus_to_gdf`, a copy of the D60 (3) function,
  chose `source_tile` by location and dropped the list; it now keeps it,
  exactly as PR #37 does.

Two other functions named `build_pv_gdf` exist: `evaluate_tile_mcc.py`'s
delegates to `build_candidate_gdf` (fixed by PR #37), and
`compare-384-vs-512.py`'s private copy also drops
`properties.source_tiles` but is not in the ruling's list. It reads 4-map
manifests only, and PR #37 found no 4-map candidate seen on two sheets in
any of the 271 committed candidate manifests, so it is left as it is and
recorded here.

**Tests.** `tests/test_library_copies_origins.py` (7 tier-1, synthetic
two-sheet fixtures): the cluster seen on two sheets and lying on the
second's tile only is switched to that sheet and matched, where the
pre-fix frame dropped it as out of frame; the PV candidate likewise; the
diversity frame keeps the list and a cluster seen on B only is matched on
B. All 7 fail on `main`; single mutations emptying each builder's list turn
1 or 2 red.

### 2.2 What each copy feeds, and how it was measured

Nothing was regenerated. Each committed output's arms were rebuilt with the
script's own builders and scored with the shared library at the output's
buffer, twice with the fixed code (NEW1, NEW2) and once with `main`'s
(OLD). The fix adds one column and changes nothing else, so for each arm
the fixed frame with `source_tiles` dropped is the pre-fix frame; OLD's
frames equal those, arm by arm, on every scope counter and on precision,
recall, and F1 (0 failures in 467 scored arms). An arm "moves" when the
scorer's scope (which rows are kept, and on which sheet each is matched)
differs with and without the list.

| Copy | Script | Committed outputs | Arms rebuilt | Rows re-attributed | Would move |
|---|---|---|---:|---:|---|
| `generate_consensus_gdf`, `build_pv_gdf` | `compute-pairwise-effect-sizes.py` (v1 inputs as `run_classb.sh` ran them; v2 March layout remapped as `regen_pes_v2.py` remaps it) | `results/pv/pairwise-effects/pairwise-effect-sizes{,-v2}.json`; `results/d42-retest-2026-10-05/class-b/pairwise-effect-sizes-{v2,v1-inputs}.json` | 60 (28 PV and 2 N = 30 consensus conditions per variant; 26 GeoJSON conditions per variant use an unchanged loader) | 0 | nothing |
| `generate_consensus_gdf`, `build_pv_gdf` | `consensus-sweep-phase3a-high-text.py` | `results/retest/phase3a-high-text/phase3a-high-text-{consensus-sweep,pairwise}.json`; `results/d42-retest-2026-10-05/class-b/phase3a-high-text-pairwise.json` | 182 (135 HIGH and 45 minimal consensus arms, 2 PV arms) | 0 | nothing |
| `analyse_diversity.consensus_to_gdf` | `analyse_diversity.py` | `results/phase3c-diversity/track1-image/` and `track2-text/` (`diversity-analysis-report.json`, `diversity-sweep-results.csv`, `diversity-analysis-summary.md`), and the two Markdown roll-ups above them | 225 (125 image, 100 text) | 885 (451 image, 434 text), in 124 arms | nothing (§ 2.3) |

In the first two rows every arm reads 0 rows restored, 0 switched, 0 out of
frame, and 0 unattributed, with and without the list: the first member's
sheet always holds the point.

### 2.3 The diversity arms

In 63 of the 125 image arms and 61 of the 100 text arms, the location rule
(first intersecting tile) had named a sheet none of the cluster's members
was seen on; with the list, the scorer restores those rows to their origin
sheet (1 to 34 rows per arm, the most at vote threshold 1). **No arm's
precision, recall, or F1 changes** (exactly, at full precision), because
no restored row changes outcome. The per-tile tables that `bootstrap_ci`
resamples were then compared directly for all 124 arms
(`pertile_diversity.py`): every table is identical, tile by tile, with and
without the list (a restored row keeps its outcome and its booking tile,
`source_tile`, which the fix does not change). So the committed point
estimates, intervals, optima, and replicate permutation tests would not
move.

Context, not caused by the fix: today's pre-fix code reproduces the
committed four-decimal F1 in 113 of the 125 image arms and 87 of the 100
text arms (the outputs date from 2026-03-25 and predate D50 and later input
changes), so `results/phase3c-diversity/` would move on regeneration for
other reasons.

## 3. Integrity

Sapphire has no error-correcting memory, so every number above comes from
two independent runs that agree:

- **H13**: NEW1 against NEW2, 116 files: 111 byte-identical; 5 identical
  after dropping keys named exactly `generated_at_utc` (the four analysis
  JSONs and the rewritten-sets analysis). No path is recorded in any output.
  The before-after summaries computed from each run are byte-identical.
- **Library copies**: NEW1 against NEW2, all four section files
  byte-identical; the per-tile check, run with each tree's code, wrote
  byte-identical outputs (124 of 124 tables equal in both).
- OLD values are checked against the committed files (§ 1.2), which serve as
  their second witness.
- The H13 runs did not pin `PYTHONHASHSEED` (the library-copy runs pinned
  0), so NEW1, NEW2, and OLD ran under different hash seeds and still
  agree; none of the outputs here goes through the set-ordered paired
  bootstraps recorded on `main` on 2026-10-13
  (`planning/paper-writeup-continuity.md`, the D62 entry).
- The kernel's "bad page" count (`journalctl -k -b | grep -c -i "bad page"`)
  read 0 at 03:59, 04:09, 04:11, 04:20, 04:32, and 04:47 UTC (the last
  after every run reported here).

## 4. Not done

- No committed result, Markdown, cell file, register row, or signature was
  changed. The regenerations (tier-0 sweep, K-sensitivity, tile-size grid)
  and any re-signing wait for the PI.
- `scripts/phase0_3_tilesize_common_footprint.py` (a dedup arm rebuilding
  a geometry-only frame, inventory § 3) and `scripts/selection_aware_intervals.py`
  (through the grid chain's `as_gdf`) are neither in this workstream's brief
  nor fixed here.
- W2.7's `cluster_subset`: on branch `origin-gap-w27`, its own record.

## 5. For the PI

1. **The K-sensitivity decomposition's constants.** `h13_k_sensitivity.py`
   writes `committed_f1: 0.6667` and `shared_scope_deduped_f1: 0.6463` as
   literals, with a note attributing the residual to "10 detections that
   change map sheet". Under the fix the shared-scope value is 0.6687 (§ 1.6)
   and the residual is −0.0020, so the logged "footprint effect" (0.6463
   minus 0.6687 = −0.0224) is an artefact of the stale literal. The note
   and the literal should be restated before `k_sensitivity.json` is
   regenerated; this is a wording decision, so it was not made here.
2. **Rewritten prepared sets for the H13 re-signing.** Re-running the
   preparation on today's code changes only `source_tile` on 12 to 22 rows
   per pass and moves A − B's p 0.0237 → 0.0231 (§ 1.3). Whether D50's
   re-signing should use rewritten sets, and how the arm B and C bounds
   would be regenerated without their tile metadata, is open.
3. **Obs 416 and the tier-0 Markdown** quote the moved best cells (§ 1.4).

## Changelog

### 2026-10-13 — Original publication

First publication, by the overnight `origin-gap-h13-copies` subagent. It
records the H13 chain fix and its re-score (twice), the three library
copies' fixes and the arm-by-arm measurement of what they would move
(twice), and the decisions left for the PI. No earlier version exists.
