# D62 (1): W2.7's subset frames carry contributing tiles

> **Last revised**: 2026-10-13 (later: the regeneration § 6 called for
> is done, on PR #38's branch, and moved what § 3 predicted). See
> [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), an overnight subagent of the main Session 163
  session (workstream `origin-gap-h13-copies`, step 3). Every number below
  was read from the run outputs on sapphire by the workstream agent on
  2026-10-13 before it was written here.
- **Date**: 2026-10-13 (UTC).
- **Repository**: `map-reader-llm`, branch `origin-gap-w27` from
  `d60-w27-fastscorer` (PR #38's head, `3448e1e9b`), stacked on PR #38.
  Commits: `34855d6fe` (a cherry-pick of the H13 fix `7ab2caa9f` from PR
  #41, for `h13_k_sensitivity.cluster_votes_with_origins`; identical
  content, so merging both is clean) and `36bf9472d` (the W2.7 fix).
- **Ruling**: PI ruling D62 (1) (`planning/pi-decisions-2026-09-20.md`)
  names "W2.7's `cluster_subset`" among the copies whose clusters must carry
  their contributing tiles into scoring; #38's floors merge only after this,
  so they are regenerated once. The brief adds "and the board's own rung
  builder, if it builds frames the same way" (§ 4).
- **Where the runs are**: `~/scratch/origin-gap-h13-copies-2026-10-13/w27/`
  on sapphire: `r1/` and `r2/` (two independent runs, each with its own
  empty pass cache: `w27/` § 6, `gate/` the scorer gate, `out55/` § 6b,
  `results/` the floors analysis), `probe-p*.json` (§ 4), `logs/`, `pids/`.
  The drivers are committed beside this record in `origin-gap-w27-scripts/`.
- **Guarantees**: no model Application Programming Interface (API) call;
  nothing merged; nothing pushed to PR #38's branch; no committed result or
  document changed (W2.7's report and `floors-v2/results/` are untouched);
  at most four worker processes on sapphire; the clone's untracked
  `crops_k5/` copy left in place.

## Bottom line

1. **§ 6 does not move.** Both runs reproduce PR #38's committed
   `subset_cells.json`, `subset_pairs.csv`, `gates.json`, and
   `verifier_provenance.json` byte for byte, and PR #38's per-tile arrays
   (`subset_cells.npz`) member for member: no cell, pair, p value, or
   table entry changes.
2. **The rebuilt `FastScorer` gate passes** under the fix: exact against
   the live library, tile by tile, on all 1,466 cells; the pre-D50 red
   sentinel still fails on exactly PR #38's four § 6 cells.
3. **§ 6b moves 132 of 16,260 cells, all back to their pre-D50 values.**
   Every one is a family B subset of three to five passes holding pass 8,
   at k ≤ 3, and gains one false positive (F1 −0.000087 to −0.000053):
   a cluster that D50 dropped as out of frame is seen on two sheets, so
   with its tiles carried it is scored on the sheet whose tiles hold it.
   Of the 362 cells D50 moved (PR #38), 230 stay moved. The simulated
   cells and the gold-standard slices are unchanged.
4. **No floor, fit, ratio, or verdict quoted moves at its quoted
   precision.** 18 rows of `floors55_all.csv` move (family B, K = 3 to 5,
   k ≤ 3), by at most 0.0000072; `tables.md`, `rescreen.csv`, and the
   rescreen log are byte-identical to PR #38's. The quoted B N3 carried
   floor returns from 0.005058 to its pre-D50 0.005063 (0.0051 either way);
   B N1 oracle 0.007957 and R7.2-32a's upper bound 0.0093 are unchanged.
5. **The board's own rung builder** (`stride55_ladder.cluster_first_n` and
   its 3.7 copy) builds frames the same way but is a shared helper feeding
   signed boards, so it was not changed (§ 4). Measured: carrying the tiles
   there would re-attribute at most two rows per rung, only at N = 9 and
   N = 10, each with verifier probability ≤ 0.05, so no board operating
   point would move.

## 1. The fix (`36bf9472d`)

- `w27_55map_subset_replicates.cluster_subset` (W2.7's restatement of the
  board's `stride55_ladder.cluster_first_n`) gave each rung cluster one
  standard-grid `source_tile`, from the nearest pooled detection's first
  member tile, and nothing else. It now also carries `source_tiles`, the
  sorted union of its members' proposer tiles, from a module-level hook,
  `cluster_votes_origins` (by default `h13_k_sensitivity.cluster_votes_with_origins`:
  the same clustering, so centroids, votes, and `source_tile` are
  unchanged).
- `load_upl_frame` keeps each union candidate's `properties.source_tiles`
  (4 of UPL's 16,482 candidates were seen on two sheets).
- `floors2_lib.cluster_votes_fast_origins` is the KD-tree restatement of
  `cluster_votes_with_origins`, keeping the pass bitmasks the
  vote-propensity model reads. `cluster_votes_fast` itself is unchanged,
  so the gold-standard slices, which use it, are unaffected.
  `floors2_55map.py` (gate 1) and `floors2_scorer_gate.py` now require the
  fast function to equal the committed one (centroids, votes, and tiles)
  before installing it as `cluster_subset`'s clustering;
  `floors2_intcost_check.py` installs it too.

**Tests.** `tests/test_w27_origin_route.py` (4 tier-1): the fast function
equals the committed one on seeded frames that straddle a sheet line;
`cluster_subset` carries the members' tiles, with `source_tile` unchanged,
and the shared scorer then matches a cluster seen on both sheets on the one
whose tile holds it; the floors-v2 hook reaches the frame; `load_upl_frame`
keeps the tiles. **Red sentinel** (real copies): on PR #38's head the module
fails to import; three single mutations (the frame losing the column, the
fast clustering returning no tiles, the UPL frame losing its tiles) each
turn one or two tests red.

## 2. What was run

Each run, in the W2.7 clone at `36bf9472d` (`scripts/lib_advanced_metrics.py`
blob `c6e6198b0`, as in PR #38), with its own empty pass cache so the
passes were re-deduplicated from the raw files (`run_w27.sh`):

1. § 6: `w27_55map_subset_replicates.py` (466 cells, 865 disjoint pairs);
2. the gate: `floors-v2/floors2_scorer_gate.py`, the rebuilt `FastScorer`
   against the live library, tile by tile, on all 466 § 6 cells and the
   same seeded 1,000 of the other § 6b cells as PR #38 (seed 20261012),
   with that run's § 6 cells as `--w27-cells`;
3. § 6b: `floors-v2/floors2_55map.py --sims 200` against that run's gate
   (16,260 subset cells and the vote-propensity simulations);
4. the floors analysis (`run-w27-analysis.sh`, PR #38's chain):
   `floors2_analyse.py`, `floors2_rescreen.py`, and `floors2_tables.py`, with
   PR #38's gold-standard slice cells (unaffected: `floors2_gs.py` does not
   call `cluster_subset`, and `cluster_votes_fast` is unchanged).

Three, then four, worker processes (§ 6 at three while other jobs ran;
the gates and § 6b at two each, side by side). "Before" is PR #38's
committed file on `d60-w27-fastscorer`.

## 3. Results

**§ 6.** Identical to PR #38 in both runs (bottom line 1). The probe (§ 4)
explains why: in the four § 6 frames where a row is re-attributed, the row's
inherited probability is 0.05 or below, under every § 6 threshold.

**The gate** (`scorer_gate.json`, `scorer_gate_cells.csv`). Pass; the new
scorer is exact on all 466 § 6 cells and the 1,000 sampled § 6b cells; the
red sentinel fails on `B (8,)` and `B (8, 9)` at k1, both thresholds, as in
PR #38; the § 6 cross-check against each run's `subset_cells.json` passes.
Against PR #38's committed gate, five sampled § 6b cells differ, each by one
false positive, and they are the five sampled cells where the library now
agrees with the pre-D50 scorer again (the sentinel's sample mismatches fall
from 22 to 17): `B (1, 3, 5, 6, 8)` at (0.2, k1), `B (2, 3, 4, 6, 8)` at
(0.2, k2), `B (2, 3, 5, 6, 8)` at (0.2, k1), and `B (3, 4, 6, 8)` at
(0.15, k1) and (0.2, k2). The JSON also differs in `floors2_lib.py`'s blob
hash (this branch changes the file) and the run time.

**§ 6b** (`subset_cells_all.csv`). 132 of 16,260 cells move, every one in
family B:

| K | Cells moved | k |
|---:|---:|---|
| 3 | 6 | 1, 2, 3 (2 each) |
| 4 | 36 | 1, 2, 3 (12 each) |
| 5 | 90 | 1, 2, 3 (30 each) |

Each gains exactly one false positive, with detections and true positives
unchanged (F1 −0.000087 to −0.000053); every moved subset holds pass 8; and
all 132 now equal `main`'s pre-D50 `subset_cells_all.csv` (`a4b5734cb`,
2026-10-07). PR #38 recorded 362 cells D50 moved, each by one false
positive fewer (family B subsets holding pass 8, k ≤ 3): the fix returns
132 of them and leaves 230. The mechanism is D50's own switch rule: the
pass-8 detection that D50 put out of frame lies outside the tiles of the
sheet its `source_tile` names; in a larger subset it clusters with another
pass's detection seen on the neighbouring sheet, so with the tiles carried
the cluster is "seen on two sheets" and is scored on the one whose tiles
hold it, where it is a false positive, as the pre-D50 scorer booked it. The
57,576 simulated cells (`sim_cells.csv`) equal PR #38's byte for byte, and
the gates file differs only in the new origins gate and the scorer blob.

**Floors analysis.** Against PR #38's committed `floors-v2/results/`:

| File | Rows that differ |
|---|---:|
| `floors55_all.csv` | 18 (B, K = 3, 4, 5 at k ≤ 3, prob_t 0.15 and 0.20) |
| `cell_sds.csv` | 6 |
| `extrapolation55.csv` | 8 |
| `nested_rung55.csv` | 8 |
| `nested_threshold55.csv` | 2 |
| `propensity55.csv` | 8 |
| `results.json` | the same values |
| `tables.md`, `rescreen.csv` (and the rescreen log), `gs_*.csv` | none |

The largest floor change is 0.0000072 (B, K = 5, (0.15, k1): 0.023894 →
0.023886). The figures W2.7's report and `floors-v2.md` quote do not move
at their quoted precision: B N3 carried (0.15, k3) 0.005058 → 0.005063
(0.0051), B N1 oracle 0.007957 (K = 1 does not move), R7.2-32a's upper bound
0.0093 (the rescreen is identical); `tables.md` is byte-identical.

## 4. The board's own rung builder

`stride55_ladder.cluster_first_n` and its copy
`gemini37_arm_ladder.cluster_first_n` build their rung frames exactly as
`cluster_subset` does, so the brief's condition holds. **They were not
changed**, and this is left to the PI: `stride55_ladder.cluster_first_n` is
a shared helper imported by six other scripts that feed signed boards
(`final_board_sweeps.py`, `final_board_n3_carried.py`,
`gemini37_fourth_cell_ladder.py`, `gemini37_grid_board.py`,
`materialise_first_n_ladder_twin.py`, `stride55_a5_vs_b5.py`), two of which
write their frames to GeoJSON with `to_file` (`final_board_sweeps.py:993`,
`final_board_n3_carried.py:125`), where a list-valued column would need a
serialisation decision; the brief's rule for a shared helper is to stop and
report.

**What it would move, measured instead** (`probe_w27_scope.py`, two runs,
byte-identical): every first-N rung on the board families' pass sets (N = 1
to 10 for A, B, and FOURTH; N = 1 to 5 for the Gemini 3.7 arms and the two
image pools), every § 6 subset frame, and UPL's verified union (16,482
candidates, which holds both halves' rows) were scored by the library's
scope with and without `source_tiles`, raw and after inheritance:

| Frame (inherited) | Rows | Re-attributed | Vote count, probability |
|---|---:|---:|---|
| A, first 9 | 37,276 | 1 | 2, 0.00 |
| A, first 10 (top rung) | 38,713 | 1 | 2, 0.05 |
| B and FOURTH, first 9 | 55,068 | 2 | 3 and 2; B 0.05 and 0.05, FOURTH 0.00 and 0.01 |
| B and FOURTH, first 10 (top rung) | 57,482 | 1 | 4; B 0.05, FOURTH 0.00 |
| § 6 subsets A (5–9), A (8, 9), B and FOURTH (6–8) | 29,689; 22,400; 36,101 | 1 each | 2; A 0.05, B 0.05, FOURTH 0.01 |

(B and FOURTH share the same passes, so their frames are the same rows
with each family's own inherited probabilities; the raw B and FOURTH
(3–5) frame also has one re-attributed row, which inheritance drops.)
Every first-N rung at N = 1 to 8, every rung of the arms and the image
pools, every other § 6 frame, and UPL re-attribute nothing.

Every re-attributed row is a cluster seen on two sheets whose
`source_tile` (from the nearest pooled detection's first member) names the
sheet whose tiles do not hold it: without the list it is out of frame and
not scored; with it, it is switched to the sheet that holds it. Each has an
inherited verifier probability of 0.00 to 0.05, and its nearest r2
reference on that sheet is 664 m to 1,939 m away. So it can only add one
false positive, and only in a cell whose probability threshold is 0.05 or
lower. The board's published operating points for these families are 0.15
or higher (W2.7's `PROBS`: A and B 0.15 and 0.20, FOURTH 0.96 and 0.98), so
**carrying the tiles in the board's builder would move no board operating
point**; only sweep rows at a threshold of 0.05 or below on the N = 9 and
N = 10 rungs could gain one false positive.

## 5. Integrity

Two runs, r1 and r2, in new processes, each re-deduplicating the passes
from the raw files into its own empty cache. Every output agrees byte for
byte: § 6's four files (and the per-tile arrays member for member), the
gate's cells CSV (its JSON differs only in `wall_seconds` and the path of the
§ 6 file it read), § 6b's `subset_cells_all.csv`, `sim_cells.csv`, and
`gates.json`, every file of the floors analysis, and the rescreen log. The
probe and the row listing (§ 4) also ran twice (on each run's cache) with
byte-identical outputs. The kernel's "bad page" count read 0 before the
first run (04:32 UTC) and after the last (07:15 UTC).

## 6. Not done, and for the PI

- **Nothing was regenerated in the repository.** W2.7's report,
  `floors-v2/results/`, and `floors-v2.md` still carry PR #38's figures;
  when #38's floors are regenerated (D62 (1): once, after this), the 132
  § 6b cells, the 18 floor rows, and the other rows listed in § 3 move as
  shown, with no quoted figure changing at its precision. PR #38's own
  record of "362 cells moved by D50" would read 230 net of this fix.
  (Done later on 2026-10-13, with PR #33's library: see the Changelog.)
- **The board's own rung builder** (§ 4): whether to carry the tiles in
  `stride55_ladder.cluster_first_n` and `gemini37_arm_ladder.cluster_first_n`
  too, and how the two GeoJSON writers should serialise the list, is the
  PI's call. Measured effect: none at any board operating point.
- PR #33 (`d50-review-fixes`) merged into `main` (`7a8a081e1`) while these
  runs were under way; PR #38 and this branch do not carry it yet. When #38
  takes `main`, the gate and these runs must be repeated with #33's library
  (PR #38's own probe found #33 moved no W2.7 cell without the tiles; with
  them it is untested here). On the H13 chain and the library copies (PR
  #41), #33 changed nothing. (Repeated later on 2026-10-13 with the tiles:
  #33 moved no W2.7 output; see the Changelog.)

## Changelog

### 2026-10-13 (later) — The regeneration done

The regeneration § 6 called for was done on PR #38's branch
(`d60-w27-fastscorer`), after `main` (`4974c3c2b`, carrying PR #33's
library) was merged in (`cc8f277c6`): every W2.7 floors-v2 output was
regenerated twice, independently, on sapphire, at `533e62605`, and the two
runs agree byte for byte. The movements are exactly those of § 3 (§ 6
unchanged; the gate exact on all 1,466 cells with the sentinel failing on
the same four § 6 cells; 132 § 6b cells; 18 floor rows by at most
0.0000072; `tables.md` and the rescreen unchanged), and #33's library moved
nothing. Results: `bdb4de89b`; account: the 2026-10-13 changelog entries
of W2.7's report (`reports/w27-replicate-floors-2026-10-06.md`) and of
`floors-v2.md`. Commit: see git log for this entry.

### 2026-10-13 — Original publication

First publication, by the overnight `origin-gap-h13-copies` subagent
(step 3). No earlier version exists.
