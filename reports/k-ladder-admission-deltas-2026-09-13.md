# K-ladder admission: claims with anchors

> **Last revised**: 2026-09-13 (original publication — the closing report of the
> K-ladder admission job, which executed the PI's rulings of 2026-09-13 on the
> close-out's morning list). Controlling card:
> `planning/k-ladder-review-2026-09-11.md` § 9. Predecessor:
> `reports/k-ladder-closeout-deltas-2026-09-12.md` § 10 (questions 1, 2, 5 and 8
> are now marked RULED and DONE there; 3, 4, 6 and 7 stay open).
> See [§ Changelog](#changelog).

## 1. The headline

Four items were ruled and **all four landed**, at **zero API cost**. Two things
the rulings did not anticipate were found by measuring, and both are recorded
rather than smoothed.

| # | Ruling | Outcome |
|---:|---|---|
| 1 | Board admission of the 46 Phase 2 rungs and the tier E cells — route (a) | **LANDED.** 103 → **153 cells admitted**, of which **150 tiered** and **3 withheld**; **Tier 1 and its five members unchanged** |
| 2 | The five renamed ids in the signed `uplift-supplement-flatten` row — confirmed | **LANDED.** Confirmation recorded; 441 ids; every signature field untouched; the FK guard and its tier-1 test pass |
| 3 | Stride B K = 5 under the 3.7 verifier — finish and register, do NOT re-tier | **LANDED.** F1@50 **0.8758**, tile-MCC **0.7326**; the 55-map board untouched |
| 4 | The verifier-stage reversal of tile-MCC's response to K — add as a claim | **LANDED.** `findings.md` **§ 8.6**, four numbers re-read at source |

**The one line a reader wants first — the board, before → after:**

| quantity | before (2026-09-12) | after (2026-09-13) |
|---|---:|---:|
| Cells **admitted** | 103 | **153** |
| Cells **tiered** | 103 | **150** |
| Cells **withheld** | 0 | **3** |
| — admitted by builder source | 60 `-era2b` + 43 `-opmax` | **60 `-era2b` + 50 K-ladder + 43 `-opmax`** |
| Pairs significant at BH q = 0.05 | 3,651 / 5,253 | **7,961 / 11,175** |
| Tiers (count) | 12 | **14** |
| Tier 1 (greedy clique) | the five 3.7 / 3.8 cells | **the same five, same order, same F1** |
| Tie set | 5 | **5** |
| Top cell | `g37-image-k5-verified-swap37-p0.90-k5` 0.9233 | **the same cell, 0.9233** |
| Hsu MCB admissible set | 49 of 103 (w_upper 0.0736) | **65 of 150 (w_upper 0.0749)** |
| Two-sided MCB band | 55 | **70** |
| Gates | G2 0 / G3 0 / G4 60 + 43 | **G2 0 / G3 0 / G4 110 / 110** |
| G6 max abs frame delta | 0.0078 | **0.0078** |

Anchors: `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/` —
`provenance.json`, `tiering_20m.json`, `gates.json`, `membership.json`,
`k-ladder/membership.json`, `mcb/gs-era2-verified-board-2026-09-10_b20_m1.json`.
The before column is the 2026-09-12 entry of that directory's `README.md` and the
`re_sign_pending.signed_outcome` / `proposed_outcome` pair its `provenance.json`
carried before this job.

## 2. Item 1: how the 50 cells were admitted, and what it cost the board

### 2.1 The mechanism — route (a), and nothing else relaxed

`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/k-ladder/membership.json`
names **50 condition ids** — **46 Phase 2** (43 `pv-diag-384`, 3
`gemini37-screen-2026-08-28`) and **4 tier E** (`grid-2026-08-18`) — each with a
one-line reason and, in `provenance`, the card, the close-out report and the
ruling text. It is derived rather than transcribed, by
`scripts/author_k_ladder_board_membership.py`: every verified registered
condition whose committed `eval_path` lies under `results/k-ladder-2026-09-12/`
and whose `scope_override.test_set_id` is `era2-b-487`, with each evaluation
opened and its `cli_args.bounds` checked against the board frame before it is
written. **0 refused.**

`scripts/build_gs_era2_board.py` `derive_membership()` defers to that file **by
condition id, before** its two refusal rules — the frame rule ("committed
evaluation on … neither the Era-2 frame nor grid-common") and the
`scope_override` rule. **Both rules are kept for every other row**: the 60 minted `-era2b` rows
are still excluded by the frame rule, and the exclusion list still records 160
refusals with their reasons (60 frame, 43 opmax-owned, 27 non-B geometry, 23
55-map, 4 `h10_test_bounds`, 2 `px256-1032` scope override, 1 unreadable
evaluation).

Three consequences, all deliberate and all visible in the artefacts:

- **Nothing was re-scored.** Each of the 50 committed evaluations already carries
  the board frame, `inputs/vectors/references/mounds-reference.geojson`, 14
  buffers, a 10,000-draw bootstrap, seed 42 and `--mcc`. `score-commands.sh` now
  reads "120 jobs for 60 re-scored members; 50 K-ladder members need none".
- **No `-era2b` row was minted for them.** That suffix records a *second*
  scoring, and there is none here; two register rows must not claim one
  evaluation file. So the cohort joins under its own condition ids, and
  `build_board_tiering_input.py` names them without the suffix.
  `register --write` added **0 rows and 0 G2 waivers** and left both register
  files byte-identical.
- **G2 is an identity and G6's delta is 0.0000 by construction** for these
  cells, not by measurement. G3 is still read off each file, because "the
  committed evaluation names the board frame" is the premise the deferral rests
  on. Gates: G2 0 failures, G3 0 failures, G4 110 / 110, 0 missing.

### 2.2 The discovery: the tile-join invariant refuses the F1 arm, not only MCC

**This is the one claim of the close-out report that was wrong, and it changes
what three cells can publish.** § 8 of that report expected the three Gemini 3.7
gold-standard text rungs to abort the tiering through an uncaught
`ConfusionGateError` on the MCC arm, so that catching it would leave their F1
intact with tile-MCC withheld. Measured:

- They abort in `lib_advanced_metrics.compute_per_tile_tp_fp_fn` — the **F1**
  arm, reached from `era1_leaderboard_tiering.cell_per_tile` — with a plain
  `ValueError` stamped `tile_join_detection_shortfall`.
- The cause is `pairwise_permutation_test.assign_source_tiles`, which returns
  early when `source_tile` is present and non-null, so a stale vocabulary is
  preserved rather than re-joined to the frame.
- So their whole **per-tile table** is unavailable on this frame. Their
  whole-frame F1 is unaffected (F1 is scored map-scoped, not tile-scoped), but
  nothing that needs a per-tile decomposition can be computed: no permutation
  test, no BH family, no admissible set.

| cell | in-frame detections | credited to a tile | F1@20 (whole frame, sound) | committed tile-MCC (NOT published) |
|---|---:|---:|---:|---:|
| `g37-text-k1-verified-carried-p0.10-k1` | 526 | **22** | 0.8338 | 0.1422 |
| `g37-text-k1-verified-opmax` | 475 | **21** | 0.8495 | 0.1337 |
| `g37-text-k3-verified-opmax` | 467 | **20** | 0.8870 | 0.1337 |

**The exposure was measured across all 50 admitted cells, not assumed.** Exactly
these three refuse. The **four tier E cells carry no `source_tile` column at
all**, so `assign_source_tiles` joins them geometrically from the frame and they
pass; the **43 `pv-diag-384` cells** already speak the frame's vocabulary. For
the three that fail, the frame shares 11–12 tile names with a vocabulary of
305–351.

**So they are admitted and withheld**: on the board by the PI's ruling, ranked
nowhere, in no BH family, in no admissible set, listed under
`tiering_20m.json` → `withheld_cells` and in the board README with their sound
whole-frame F1 and an explicit statement that their committed tile-MCC is the
pre-invariant value and is not published. That is where close-out **question 4**
— the corpus-wide tile-join decision, still open — already left them; it is now
blocking their whole statistics rather than only their MCC.

### 2.3 What the code now does, and the two blockers fixed

- `era1_leaderboard_tiering.load_cells()` takes an optional `withheld` sink.
  With one, a tile-join refusal is recorded and the cell skipped; without one the
  old fail-loud behaviour stands, which is what the function's two other callers
  want. `is_tile_join_refusal()` tells a refusal apart from every other
  `ValueError` **by the stamped reason code**, so a missing detections set or an
  un-scoreable cell still fails loud. `--strict-tile-join` restores aborting.
- The MCC arm's `ConfusionGateError` is caught per cell too: such a cell keeps
  its F1 rank with `mcc: null` and leaves the MCC BH family (`mcc_family()`).
  **No cell took this path on this board** — the three refusals happened earlier.
- `selection_aware_intervals.build_board_tile_counts()` withholds the same cells,
  so the admissible set is computed over the cells the tiering ranked (65 of
  **150**, not of 153).
- `finalise()` now carries **`signature_history`** forward beside `signed_at`,
  `signed_by` and `gates.G1.pi_ruling`, and nests a *resolved* `re_sign_pending`
  inside the fresh PENDING one rather than dropping it. The close-out found that
  a rebuild would otherwise have destroyed the array recording the board's
  original 2026-09-10 signature. Verified in the run's own output: "carried
  forward from the previous provenance.json: signed_at, signature_history,
  re_sign_pending (resolved, nested as previous_resolved), gates.G1.pi_ruling".
- `finalise()` also now reports the cells it could **not** tier — the outcome
  opens "150 of 153 admitted cells tiered; 3 WITHHELD …" — because a board that
  silently said "150 cells" would have hidden the other three.

**No signature field was written anywhere.** The board's analysis row is
PI-signed, so the tiering and the MCB read their membership from
`tiering-input/run-analyses.json` (153 ids, one substituted field) and
`finalise --no-analysis-row` recorded the proposed outcome under
`provenance.json` → `re_sign_pending` for the PI.

## 3. Item 2: the five renamed ids — confirmed

Re-read at source before recording the confirmation: the signed
`uplift-supplement-flatten` row holds **441** `conditions_compared`; all five
`consensus-384-t1-0::consensus-{1..5}of5` ids are present and **no `of30` id
remains**; `manually_verified_at` is still `2026-09-10T22:55:40Z`; `outcome` and
`_signature_note` are untouched. The single edit is `_conditions_note`, which now
records the PI's confirmation and its date in place of "flagged to the PI for
confirmation". The foreign-key guard passes — `build_manifests` returns
`warnings == []` — and so does its tier-1 test
(`tests/test_generate_post_run_report.py::test_manifest_envelopes_valid`, with
the ten manifest tests passing).

## 4. Item 3: the stride-B K = 5 rung under the 3.7 verifier

### 4.1 What was built

`scripts/final_board_sweeps.py --reference r2` re-ran in full on sapphire (20
workers, **64 minutes**), with the generator fix that derives each family's rungs
from its own `k_max` instead of the literal `for n in (1, 3)`. Every gate passed:
G4 on 13 committed cells at d ±0.0000; the 8 + 3 identity gates exact; the 5 + 3
mechanism gates' integer (TP, FP, FN) triples exact; the 2 + 3 geometry gates at
max nearest-neighbour 0.0000 m; all four pass pins verified.

**The strongest evidence that it disturbed nothing is the diff**: of the 22
committed sweep CSVs and the 31 committed cell detection files in
`results/55map-final-board-r2-2026-09-06/`, **none changed**. The run is
byte-identical wherever it overlaps the committed board.

Scored by the r2 chain's one engine
(`scripts/r2_score_cells.py --stage board`: 32 cells in the derived set, **31
resumed, exactly 1 run**) against reference r2, 14 buffers, tile-level BCa
10,000 / seed 42, `--mcc`:

| rung | operating point | F1@50 | BCa 95 % CI | tile-MCC | detections |
|---|---|---:|---|---:|---:|
| `FOURTH-N5-oracle` | (0.96, k5) | **0.8758** | 0.8679 – 0.8832 | **0.7326** | **4,434** |

Registered through the generated-manifest flow:
`scripts/register_r2_conditions.py --write` added **exactly one** row,
`stride-55map-2026-08-25::g384-ov192-55map-n5-verified37-oracle-p0.96-k5-r2-gt`
(37 present, 3 coincident and skipped by design);
`scripts/verify_run_conditions.py` passes that run and reports **0 fail** across
41 runs; the manifests regenerate **ALL VALID** at 41 runs, 593 conditions, 1,317
passes and 67 analyses.

### 4.2 The § 3.3 row, and what it says

`results/k-ladder-2026-09-12/findings.md` § 3.3 now reads K = 1 / 3 / 5 / 10 at
F1@50 **0.8352 / 0.8747 / 0.8758 / 0.8813** with tile-MCC **0.7471 / 0.7376 /
0.7326 / 0.7359**. The sub-table keeps its R1-non-compliant flag and its "not
supplied" verifier cost cell, and the carried column stays "—".

- **Saturation, as everywhere else in the corpus.** K = 3 → 5 buys **+0.0011**
  F1@50 against the **+0.0395** of K = 1 → 3.
- **Tile-MCC does not fall monotonically here.** 0.7326 at K = 5 is the *lowest*
  of the four rungs, below K = 10's 0.7359 — so this family breaks the monotone
  pattern tier E's ladder shows, while still putting every rung above K = 1 below
  K = 1's 0.7471, which is § 4's direction. Neither step is separation-tested:
  this sub-table is outside the review's instrument.
- **No carried figure is claimed.** This family's rungs have no carried cells:
  the carried column is "—" at K = 1 and K = 3 too, and the only post-hoc carried
  nominations on this board are Runs A and B at N = 3 (PI direction 2026-08-28,
  `scripts/final_board_n3_carried.py`). For a reader who wants the transferred
  point anyway, `sweep_FOURTH-N5.csv` scores (0.98, k5) — the K = 10 rung's
  committed point with k scaled to the rung — at micro-F1@50 **0.8754** over
  4,431 detections against the oracle's micro-F1@50 0.8758. That is a light-
  scorer sweep row, not a registered cell, and it is **not** a claim.

### 4.3 A second discovery: regenerating the sweep dropped two board cells

`final_board_sweeps.py` wrote `cells_manifest.json` from stage 1 alone, but two
of the board's cells come from a **later** step — the emergent post-hoc
`A-N3-carried` and `B-N3-carried` of `scripts/final_board_n3_carried.py` (PI
direction 2026-08-28). So any regeneration silently removed them from the
manifest, which is what `final_board_build.py --reference r2` and
`r2_score_cells.py --stage board` read: the board would have shrunk by two cells
on the next rebuild. The generator now carries forward every post-hoc cell it
does not itself produce, matched on label. **Nothing published was affected** —
the defect was caught in the diff before anything was committed, the committed
manifest's 35 rows are byte-for-byte unchanged, and `FOURTH-N5-oracle` is the
36th.

### 4.4 What was NOT re-tiered

`results/55map-final-board-r2-2026-09-06/final_board_50m.json`, its tiering and
its 595-pair BH family are untouched, and `scripts/final_board_build.py` was not
run — per the ruling on close-out question 5. `findings.md` § 4.1's gate against
that board's committed pairwise p-values therefore still holds.

## 5. Item 4: the reversal claim, and its four anchors

`findings.md` **§ 8.6** states as a claim what § 8.3 and § 8.4 each measured half
of. Every number was re-read at source before the section was written; none
moved.

| number | value | source re-read this session |
|---|---:|---|
| consensus-only ΔF1, K = 1 → 10 | **+0.0572** | `results/grid-2026-08-18/sweep.csv`, cell `g384_ov192`, best F1@20 per K over the (corroboration, vote) grid: **0.6633** at K = 1 (c ≥ 3, k ≥ 1) → **0.7205** at K = 10 (c ≥ 2, k ≥ 10) |
| consensus-only Δtile-MCC | **+0.0444** | the same two rows of the same file: **0.4465** → **0.4909** |
| verified ΔF1, K = 1 → 10 | **+0.0340** | `results/k-ladder-2026-09-12/tier-e/ladder.json` `rungs`, confirmed against each rung's own evaluation: `…/tier-e/cells/grid-2026-08-18__g384-ov192-k1-verified-opmax/evaluation.json` F1@20 **0.8546** (482 detections) → `…__g384-ov192-k10-verified-p0_15-k10-boardframe/evaluation.json` F1@20 **0.8886** (400 detections) |
| verified Δtile-MCC | **−0.0308** | the same two evaluations, `summary.tile_classification.mcc.point`: **0.8211** → **0.7903** |

Derived and stated for the first time: the verifier **absorbs 40.6 %** of K's F1
return (1 − 0.0340 / 0.0572) and the tile-MCC swing between stages is
**0.0752**. The mechanism is given in two sentences and cross-referenced to § 4
and § 4.3, whose 16-of-21 falling tile-MCC this explains as a property of the
pipeline *stage* rather than of K. The limits are stated with the claim: one
geometry, one thinking level, one temperature, one modality, one corpus, and the
ladder's own ΔMCC steps are **not** individually significant (tile-MCC separates
on none of the ladder's six pairs), so the claim is about the sign and size of
the shift between stages. The same claim is added to the `k-ladder-2026-09-12`
analysis row's `outcome`, which is **UNSIGNED** (`manually_verified_at` is null,
asserted before the edit).

## 6. What did NOT change

- **No committed evaluation was rewritten**, and no measured value moved. The
  only new measured value in the whole job is the K = 5 rung's.
- **No signature field**, anywhere: `manually_verified_at`, `_signature_note`,
  `signed_at`, `signed_by`, `signature_history` and `gates.G1.pi_ruling` are
  untouched, and the board's signed analysis row was not amended.
- **The Era-2 board's Tier 1**: the same five 3.7 / 3.8 cells, in the same order,
  at the same F1, with the same top cell at 0.9233 and the same tie set of 5.
  Every gate keeps its verdict and G6 its maximum frame delta of 0.0078.
- **The 55-map final board** (§ 4.4), and `findings.md` § 4.1's gate against it.
- **The tile-join rule.** `TILE_JOIN_DEFAULT` is still `id`; no geometric join
  was adopted. Close-out question 4 is still open, and is now the only thing
  between the three withheld cells and a full row on the board.
- **The Era-2 board's instrument.** The MCC permutation family was deliberately
  **not** added: the board's committed 2026-09-12 tiering was run without
  `--permute-mcc`, and adding a statistic family to a signed board is a change
  the PI did not rule. Offered to the PI as an option, not taken.
- **Tier E's K = 10 rung** (close-out question 3), the **h10 `consensus_t3/t4/t5`
  files** (question 6), the **analysis row's signature** (question 7), the
  registered `pass-budget-pareto-v2` efficient set, the E83 MCB ruling, and the
  stride ladders' registered outcomes.

## 7. Verification

| # | Check | Result | Anchor |
|---:|---|---|---|
| 1 | The K-ladder membership derives the ruled cohort exactly | **50 members, 46 Phase 2 + 4 tier E, 0 refused** | `k-ladder/membership.json`, `n_by_cohort` |
| 2 | The deferral does not relax the rules for anything else | 160 exclusions still recorded with reasons, 60 of them the frame rule on the `-era2b` rows | `membership.json`, `excluded` |
| 3 | Nothing was re-scored and no row minted | `register --write`: 0 new condition rows, 0 G2 waivers; both register files byte-identical | the run's own output; `git status` |
| 4 | Board gates over the enlarged membership | **G2 0, G3 0, G4 110 / 110, 0 missing** | `gates.json` |
| 5 | Which cells the invariant refuses, measured on all 50 | **exactly 3**; the 4 tier E cells have no `source_tile` and join geometrically; 43 `pv-diag-384` match the frame | § 2.2 |
| 6 | `signature_history` survives a rebuild | carried forward, with the resolved `re_sign_pending` nested as `previous_resolved` | `provenance.json`; the run's "carried forward" line |
| 7 | Tier 1 after the admission | **unchanged** — same five cells, same order, same F1, same top cell, tie set 5 | `tiering_20m.json` `tie_set`; § 1's table |
| 8 | The r2 sweep disturbed no committed artefact | **0 of 22 sweep CSVs and 0 of 31 cell detection files changed** | § 4.1; `git status` on the r2 board directory |
| 9 | The K = 5 rung's registration | 1 row added; `verify_run_conditions.py` 0 fail across 41 runs; manifests ALL VALID (593 conditions, 67 analyses) | § 4.1 |
| 10 | The reversal claim's four numbers | all four re-read at source; none moved | § 5 |
| 11 | Lint | `ruff check` clean on every Python file touched; `markdownlint-cli2` clean on every Markdown file touched | — |
| 12 | Tier-1 tests | **2,462 passed, 1 skipped, 3 xfailed, 0 failed** in 183 s on sapphire (`python -m pytest -m tier1 -q`). The close-out's baseline was 2,447, so the suite grew by exactly the 15 tests this job added and nothing regressed | `tests/test_k_ladder_board_admission.py` and the suite |

## 8. Tier-1 tests

The suite runs **2,462 passed, 1 skipped, 3 xfailed, 0 failed** in 183 s on
sapphire. The close-out's baseline was 2,447, so it grew by exactly the 15 tests
added here.

`tests/test_k_ladder_board_admission.py` is new, with **15 tier-1 tests** over
synthetic registers and temporary board directories — no committed artefact is
read and nothing is written outside `tmp_path`. They pin, in order: that both
refusal rules still refuse the cohort with no membership file; that the deferral
admits a named cell and flags it; that it does **not** relax the rules for an
unnamed cell; that a named cell with no detections file is refused rather than
admitted; that K-ladder members get no scoring jobs and mint no `-era2b` row;
that `build_board_tiering_input` names them by their own id; that
`finalise` carries `signature_history` forward and nests a resolved
`re_sign_pending`; that `finalise --no-analysis-row` leaves the signed row
byte-identical; that a tile-join refusal is told apart from every other
`ValueError`; that `mcc_family` splits testable from withheld cells; and that
both withholding arms reach provenance, the README and the proposed outcome.

## Changelog

### 2026-09-13 — Original publication

The closing report of the K-ladder admission job, written from artefacts the job
produced and re-read in the same session:
`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/`
(`k-ladder/membership.json`, `membership.json`, `membership.txt`, `gates.json`,
`frame-deltas.md`, `score-commands.sh`, `tiering-input/run-analyses.json`,
`tiering_20m.json`, `mcb/gs-era2-verified-board-2026-09-10_b20_m1.json`,
`provenance.json`, `README.md`);
`results/55map-final-board-r2-2026-09-06/` (`sweeps.json`, `cells_manifest.json`,
`sweep_FOURTH-N5.csv`, `cells/FOURTH-N5-oracle/`);
`results/run-conditions.json`, `results/run-analyses.json` and the four
regenerated manifests; `results/grid-2026-08-18/sweep.csv` and
`results/k-ladder-2026-09-12/tier-e/ladder.json` with the two rung evaluations,
read directly for § 5; and `scripts/build_gs_era2_board.py`,
`scripts/era1_leaderboard_tiering.py`, `scripts/selection_aware_intervals.py`,
`scripts/build_board_tiering_input.py`, `scripts/final_board_sweeps.py`,
`scripts/final_board_n3_carried.py`, `scripts/r2_score_cells.py` and
`scripts/register_r2_conditions.py` for the mechanisms §§ 2–4 name.

Landed on branch `worktree-agent-a771172bf2954c784`, not merged to `main`.
