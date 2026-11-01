# Tile-join resolution — decision record and execution plan

> **Last revised**: 2026-11-01 (original publication, S167). See
> [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), main session S167 on zbook, with the principal
  investigator (PI). Every figure below was re-read from the files named
  beside it, on `main` at `c33c1463d`, before it was written here.
- **Status**: rulings **D72 (1)–(4)** taken
  (`planning/pi-decisions-2026-09-20.md`). **Waiting on Astra's review of
  this document (gate R, § 6) before Wave 1 launches.** Nothing has been
  re-scored, and no committed result has changed.
- **Target**: all data and results settled, and the write-up begun, by
  **2026-11-08**.

## 0. The decision in one paragraph

The published tile join (`id`, S153 ruling 6) gives a **perfect** detector
a tile-level Matthews correlation coefficient (tile-MCC) of **0.8711**
instead of 1.0, whenever the detector merges duplicates, as every consensus
and verified cell does. Here is why. A merged point's `source_tile` is the
alphabetically first of the tiles it was seen on, while a reference mound
counts in every tile it lies in. On our overlapping frames, every mound
seen on two tiles therefore leaves a false-negative tile that the pipeline
did not cause. This makes the rule invalid as a measurement, not merely
one defensible choice among several, so no workaround that keeps `id`
values in the reported numbers or in the robustness set is acceptable. The
PI ruled:

- **(1)** tile-level classification (tile-MCC, tile-F1, sensitivity,
  specificity) moves to `geometric-contains`, which is the registered
  definition (OSF § 4.2) read literally;
- **(2)** the per-tile count tables behind F1's bootstrap intervals and
  tile-swap permutation tests book true and false positives by
  `geometric-primary`, as false negatives already are;
- **(3)** the paper-cited artefacts are re-scored first, but a run does
  not stop at that subset if it can carry on;
- **(4)** Astra reviews this record before compute is spent, from
  amd-tower.

Symbol-level F1, precision and recall, the registered primary outcome, are
not touched by any of this (§ 2).

## 1. The defect, stated once

| Step | Code | What it does |
|---|---|---|
| A merged point gets one name | `scripts/lib_consensus.py:307–309`, `:394–395` | "`source_tile` is still the alphabetically first" of the tiles the cluster's members were seen on. The full list is kept in `source_tiles` (since D62 (1)) |
| Tile classification under `id` | `scripts/lib_advanced_metrics.py`, `calculate_tile_classification` | detections are booked by name, references by containment ("`id` keeps the legacy asymmetric pairing … purely so that published numbers reproduce") |
| Per-tile F1 counts under `id` | same file, `compute_per_tile_tp_fp_fn` (`:2889–2890`) | "TPs and FPs to the detection's `source_tile`, unmatched FNs to the reference's primary tile (nearest centroid)" |
| The default | same file, `:149` | `TILE_JOIN_DEFAULT: str = TILE_JOIN_ID` |

Every frame tiles its maps with overlap, so the asymmetry bites
everywhere. A mound seen on tiles T1 and T2 is credited by name to T1
only. Its reference counts in both, so T2 becomes a false negative, even
though the model reported the mound there.

## 2. Evidence

### 2.1 The perfect-detector test

`tile-join-resolution-2026-11-01-scripts/perfect_detector.py` scores the
GS reference mounds *as* the detections, on the Era-2 frame
(`inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson`), for two
perfect pipelines. Output: `perfect_detector.txt`. Of the 435 mounds in
the frame, 117 (26.9 %) lie in two or more tiles.

| Perfect pipeline | `id` | `geometric-primary` | `geometric-contains` |
|---|---|---|---|
| merged: one point per mound, named for the alphabetically first containing tile | **0.8711** (TP 196, FN 33) | 1.0000 | 1.0000 |
| per-tile: one point per (mound, containing tile) | 1.0000 | 1.0000 | 1.0000 |

`id` is correct for unmerged per-tile output, which is the case S153
ruling 6 reasoned about ("the pipeline's decision on the tile the model
saw"). It is wrong for merged output, which covers every consensus and
verified cell.

### 2.2 The registered definition

`docs/methodology/preregistration/osf/preregistration.md:379–390`
(§ 4.2) defines the unit as the tile and classifies it as "Has mounds" ×
"Detected ≥1 mound", for a holdout of 30 empty and 30 populated tiles.
For one tile's own model output, "detected in that tile" and "named for
that tile" coincide. On an overlapping frame with merged output, the
literal reading is containment on both axes, which is `geometric-contains`.
So `id` was itself an unrecognised departure from § 4.2, and the fix
restores the registered metric rather than introducing a new deviation.

### 2.3 Scope: what is and is not affected

| Result | Status | Basis |
|---|---|---|
| Symbol-level F1, precision and recall (primary outcome, every hypothesis decided on F1) | **untouched** | matched per map by Hungarian assignment on geometry, "before any tile is consulted" (`lib_advanced_metrics.py:2899`) |
| Tile-MCC, tile-F1, sensitivity, specificity (secondary outcome) | **wrong for every merged cell** | § 1 |
| F1 bootstrap intervals, tile-swap permutation p-values, tiers, F1 Hsu sets | **unknown** | point estimates exact (each object booked once); the spread of counts over tiles follows the name rule for TP/FP, so the null distributions may move |

### 2.4 Every frame overlaps

`frame_census.py` (output `frame_census.txt`) reads the frame each
evaluation was scored on, for the 21 signed register rows that quote
tile-MCC:

| Frame | Tiles | Summed area / union |
|---|---:|---:|
| `inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson` | 487 | 1.2783 |
| `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` | 487 | 1.2768 |
| `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson` | 487 | 1.2834 |
| `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` | 8,541 | 1.4527 |
| `inputs/vectors/bounds/full_evaluation_bounds.geojson` (512 px) | 340 | 1.2814 |
| `outputs/h13/scoring/bounds/h13_common_bounds.geojson` | 340 | 1.2918 |
| `inputs/vectors/bounds/384/h10_test_bounds.geojson` | 327 | 1.1743 |
| `inputs/vectors/bounds/256/full_evaluation_bounds.geojson` | 1,032 | 1.2853 |

The 55-map frame overlaps most: neighbouring sheets also overlap at their
seams, and some tiles have a near-duplicate from the next sheet about
170 m away. Only 5 of the 21 rows have any committed geometric-join
reading. That count is a text match, so it is indicative. In the 47 Era-2
board cells whose detection files record `source_tiles`, 19.4 % of
detections (3,698 of 19,017) were seen on two or more tiles; the other 56
cells' files carry no list.

### 2.5 What the S166 sensitivity runs showed

From `reports/s166-agent-records/mcc-join-tiering.md` and
`k-ladder-mcc-join.md`, under `id` / primary / contains:

- the board's top-F1 cell ranks 21st / 1st / 1st on MCC;
- F1-admissible cells that are also MCC-admissible: 9 / 50 / 45 of 52;
- tile-MCC falls from K = 1 to the best F1 rung on 16 / 9 / 11 of 21
  ladders;
- K = 1 is MCC-admissible on 22 / 17 / 16 of 22 ladders;
- 59.6 % (board) and 67.3 % (K-ladder) of `id`'s false-negative tiles
  contain one of the cell's own detections.

The claims that the "F1 and tile-MCC disagree" (Obs 482, Obs 513, R6-18)
and that "tile-MCC does not follow F1" (R3-12, R3-13) look like products of
the defect. Contains values are already computed for the board and the
K-ladder, and they become the published values (§ 5, gate G2).

## 3. The rulings, and what was rejected

- **Rejected: options A and B** of the S166 records (keep `id` and add a
  sensitivity sentence; or keep `id` and narrow claims to what holds under
  all three joins). Both keep an invalid rule, either in the reported
  numbers or in the robustness set. The PI's objection was that this would
  produce outcomes that are consistent but consistently incorrect.
- **Rejected for classification: `geometric-primary`.** It too scores the
  perfect detector at 1.0, but it redefines the unit as a tile's
  nearest-centre core, a new deviation from § 4.2. It stays the rule for
  count tables, where each object must be counted exactly once (D72 (2)).
- **Not built: a `source_tiles` join** (credit a merged point to every
  tile it was seen on). It is closest to ruling 6's intent, but it does
  not exist, 56 of the board's 103 detection files lack the list it
  needs, and it would measure exposure rather than the registered
  presence.
- **`id` stays in the code** as a named legacy join, so historical
  artefacts can still be reproduced. It stops being the default.

## 4. Design of the change (Wave 1)

1. **Two defaults, one per purpose**, in `scripts/lib_advanced_metrics.py`:
   - tile classification defaults to `geometric-contains`;
   - per-tile count tables default to `geometric-primary`.

   Name the two constants separately. Every caller that passes
   `tile_join` explicitly is audited, since some pass the old default by
   name. `geometric-contains` must never reach a count table (it would
   double-count): refuse that combination.
2. **The perfect-detector test, made permanent (tier 1).** On a real
   overlapping frame and on a synthetic one:
   - ground truth fed back as merged detections and as per-tile
     detections must give tile-MCC 1.0 and F1 1.0;
   - the per-tile count table must sum to the symbol-level totals.

   Its red sentinel: the same test under `id` gives 0.8711 on the Era-2
   frame.
3. **The tile-join invariant.** Under geometric joins, no vocabulary
   mismatch can arise. The three Gemini 3.7 GS text cells withheld since
   2026-09-13 therefore become scoreable. Whether they then enter their
   families changes family composition: put it to the PI at M1, not
   automatically.
4. **Erratum E93** (the next free number on `main` at the time of
   writing) in `docs/methodology/preregistration/protocol-errata.md`:
   `id` departed from § 4.2 and is corrected, with a before/after table
   produced by Wave 2.
5. **Gap analysis first** (project convention): a dry-run simulation of
   Wave 2's driver over a handful of evaluations, before any code is
   written for it.

## 5. Execution plan: waves and gates

Each wave is a specified, long-running job, multi-agent where the work
splits. Each ends at a milestone where the PI reviews and approves before
the next wave launches. Compute runs on zbook, which is about as capable as
sapphire and may run as long as needed. An approved overnight wave runs to
completion rather than stopping at its priority subset. Launch discipline
follows `docs/agent-guidance.md`: all three file descriptors redirected,
nothing after the launch on the same line, watchers on terminal state
(`scripts/wait_for_run.py`) and log staleness, never `pgrep -f`. Zero API
calls throughout.

| Wave | Work | Gate before the milestone | Milestone |
|---|---|---|---|
| **R** | Astra reviews this record (amd-tower) | review delivered by agent mail or a committed file | PI rules on the findings |
| **1** | § 4 code and tests; erratum draft; Wave 2 driver dry-run. **Smoke test:** re-score 3–5 representative evaluations (an Era-2 board cell, a K-ladder 55-map rung, an Era-1 512 px cell, a grid cell, a replicate-mean cell) | G1: F1/P/R byte-identical; tile-MCC equals the S166 contains reading where one exists; tier-1 green | **M1**: PI reviews the smoke results and the 3.7 question (§ 4 item 3) |
| **2** | Corpus re-score. 2,646 committed `evaluation.json` files carry tile tables (`git ls-files`, 2026-11-01). Paper-cited first (cited by the register's signed rows or `docs/paper/`), then the rest, in one run. Re-emit `tile_classification` **and** the per-tile-table-derived F1 intervals, surgically, on the `scripts/rescore_tile_mcc_e81.py` pattern | G2: every non-target field byte-identical (the E81 guards); point F1/P/R identical; contains values reproduce the S166 board and K-ladder readings; a per-file before/after ledger | **M2**: PI reviews the ledger summary (ΔMCC distribution, any interval or guard failure = stop) |
| **3** | Regenerate downstream: tierings (F1 permutation on primary-booked tables, MCC on contains), Hsu sets, boards, K-ladder tables, leaderboards, manifests, register renderings | G3: a flip report: every F1 significance, tier or admissible-set change, and every MCC claim's new reading | **M3**: PI reviews the flip report |
| **4** | Restate claims: the 21 signed MCC rows (`frame_census.txt`), Obs 482, Obs 513, R6-18, R3-12, R3-13, R3-14 / R6-17, the K-ladder findings §§ 4.1, 4.3, 7.2, 8.2, 8.4, 8.6, any F1 claim Wave 3 flips, and the D71 held items; erratum E93 finalised; the Obs 515 candidate decided | G4: drift checks green; markdownlint and tier-1 green | **M4**: PI re-signs rows; write-up starts |
| **S** (parallel, low priority) | Sensitivity: sheet-block bootstrap on the 55-map corpus (spatial dependence between tiles affects every tile-resampling method under any join) | — | reported at M3 |

## 6. Questions for the review (gate R)

1. Is `geometric-contains` the right literal reading of OSF § 4.2 for
   merged output on an overlapping frame? Is calling `id` an unrecognised
   departure, corrected by erratum, the right framing, or is it a new
   deviation that needs a registration update?
2. Is using two rules (contains for classification, primary for count
   tables) coherent, or should one rule serve both?
3. Can booking TP/FP by name instead of by nearest centre make the F1
   tile-swap permutation tests or BCa intervals anti-conservative, or only
   noisier? Is anything already published at risk before Wave 3 measures
   it?
4. Does anything in § 2.3's "untouched" row deserve a check we have not
   planned? For example, D50 frame scoping reads `source_tiles` to
   attribute a detection seen on two sheets.
5. Should the three withheld 3.7 cells enter their families once
   scoreable?
6. Are gates G1–G4 sufficient, and is anything missing from Wave 4's
   claim list?

## Changelog

### 2026-11-01 — Original publication

Written at S167 after the PI paused the tile-join walk-through ("a serious
problem that needs a robust solution"). Records the perfect-detector test,
the scope check, rulings D72 (1)–(4), and the wave plan. Evidence scripts
and their outputs are in `tile-join-resolution-2026-11-01-scripts/`.
