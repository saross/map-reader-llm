# Tile-join wave S — specification (spatial-block resampling check)

> **Last revised**: 2026-11-19 (revised after Astra's round-2 review). See
> [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), drafting for session S169 on amd-tower, in the
  worktree `~/worktrees/map-reader-llm/claude-wave-s-spec` (branch
  `wave-s-spec`). The first draft read every path, line number, and count
  from the files named beside it, on `main` at `fe9d433d7`; the line
  numbers in § 2 are still at that commit. The revision was made on the
  same branch, fast-forwarded to `main` at `92064b134`. The block counts,
  the geometry check, and the occupancy correlogram come from two
  standard-library scripts that read only bounds files, tracked tile
  rasters' world files and headers, and reference files (§ 3.2, § 3.3,
  § 3.4; D70: amd-tower's environment is not the reference one). No block
  statistic, permutation, or bootstrap has been run by anyone.
- **Parent**: `planning/tile-join-resolution-2026-11-01.md` (the decision
  record; this document specifies the wave S row of its § 5). Rulings: D72
  and D73 in `planning/pi-decisions-2026-09-20.md`, in particular D73 (3).
  Sibling: `planning/tile-join-wave-1-spec-2026-11-01.md` (the joins this
  wave inherits).
- **Review**: Astra (GPT, OpenAI Codex, Astra lane), round 1, 2026-11-18,
  at `a588b96f1`: "changes requested before launch"
  (`~/agent-mail/codex/outbox/claude/20261118T124335Z-astra-wave-s-spec-review.md`;
  evidence in `~/agent-mail/codex/reviews/wave-s-spec-2026-11-18/`). Every
  finding was checked against the files and held; § 13 records the
  dispositions. Round 2, 2026-11-18, at `0a1b4dadd`: two arithmetic
  corrections before the design lock (S6, S7) and a recommendation to the
  PI on estimator changes
  (`~/agent-mail/codex/outbox/claude/20261118T133113Z-astra-wave-s-round2-review.md`;
  evidence in `~/agent-mail/codex/reviews/wave-s-round2-2026-11-18/`); both
  corrections verified and applied (§ 13).
- **Status**: **DRAFT, revised after Astra's rounds 1 and 2; not approved
  by the PI.** Nothing in it is a ruling. Where the record does not settle a
  choice, the document recommends one and lists it in § 11.
- **Target**: all data and results settled, and the write-up begun, by
  **Sunday 2026-11-29** (PI, 2026-11-18; parent record, header).
- **Runs on**: zbook, after Wave 3's gate G3 (§ 1). **Zero application
  programming interface (API) calls.**

## 0. What wave S does, in one paragraph

Every significance test and interval in this study resamples **tiles**: the
paired tile-swap permutation test of D42, the bias-corrected and accelerated
(BCa) bootstrap, and the bootstrap behind the Hsu multiple comparisons with
the best (MCB) admissible sets. Those methods treat tiles as exchangeable
units. Tiles overlap by 48 px at 384 px, mounds cluster, and map sheets
differ, so they are not independent, and Astra showed that reassigning
outcomes to tiles can make the tests anti-conservative, not merely noisier
(round 1, R3). Wave S repeats every affected significance claim with
**blocks of contiguous tiles inside one sheet** as the resampling unit, on
both corpora, using the same estimands, families, kernels, seeds, and draw
budget as the tile-level analysis that Wave 3 regenerates. Its decisions
use a **valid permutation p-value**, `(c + 1)/(N + 1)` for sampled swaps or
the exact proportion under full enumeration, computed for the tile unit
(singleton blocks) and for every block design alike, so the ledger
separates the change of estimator from the change of unit (§ 3.6). A claim
whose verdict holds under the primary block size and every applicable
sensitivity design, each able to resolve it, is reported as robust to the
specified design. A claim that holds only under some, or that some cannot
resolve, is qualified, and a claim that fails under the primary design,
with the resolution to decide, is withdrawn as a significance claim. On the
55-map corpus, the inferential scope stays qualified until a seam-aware
design is frozen after the PI's seam ruling (§ 3.8). This document fixes all
of that before any block result exists.

## 1. Preconditions (launch is blocked until all hold)

| # | Precondition | How it is checked |
|---|---|---|
| P1 | Astra has reviewed this specification, the PI has ruled on the review, and the document is revised accordingly | round 1 delivered 2026-11-18 and answered by this revision (§ 13); the PI's ruling on § 13 and § 11 recorded in § Changelog; a further round if the PI asks for one |
| P2 | The PI approves this specification for launch | stated in conversation; recorded in § Changelog |
| P3 | **The design lock is committed** (S.0): block maps, eligibility manifest, and parameters, with their SHA-256 hashes, in a commit that precedes every commit holding a wave S statistic | `git log` order; the driver refuses to run if the lock's hashes do not match the files (§ 5) |
| P4 | Wave 3 has passed G3: the tile-level families, tierings, MCB sets, and intervals are regenerated under the new joins and committed | the record's § 5, Wave 3 row; Wave 3's flip report exists |
| P5 | zbook's `.venv` matches the reference environment, and its checkout is clean and 0 behind `origin/main` | as Wave 1 spec § 1, P3 and P4 |
| P6 | **The synthetic timing benchmark** (S.0, cost) has run and `cost.md` is committed, before any real block statistic | `git log` order; the driver refuses a real statistic without it |
| P7 | **For 55-map families only**: the PI has ruled on the 55-map seams, and either a seam-aware design is frozen in the lock or the lock records that the 55-map scope is qualified (§ 3.8) | the lock's `seam_disposition` field |

**Recommended, not required** (§ 11, PI question 1): approve this
specification and commit the design lock **before Wave 2 produces its
first corrected result**, so that even the corrected tile-level results are
unseen when the block design is frozen. The hard requirement (P3) is only
that the lock precede every block statistic.

## 2. What wave S inherits

Wave S adds a unit, not a method. Each piece below is reused unchanged, run
on block-aggregated arrays instead of tile arrays (§ 3.5), with one change
of decision rule: the p-value estimator (§ 3.6 (c)). Line numbers are at
`fe9d433d7`.

| Piece | Where | What wave S keeps |
|---|---|---|
| Paired tile-swap permutation, F1, precision, recall | `scripts/lib_permutation.py:241` (`paired_permutation_test`); swap masks `:199`; constants `N_PERMUTATIONS = 10_000`, `SEED = 42` at `:68–69`; p-value `mean(\|null\| >= \|observed\|)` at `:306`, which may be exactly 0 (module docstring, D42 default (d)) | the kernel's draws, the shared mask for all three metrics, the run-block swap for multi-run arms (`_as_runs`, `:147`); the exceedance count c behind `:306` feeds both estimators of § 3.6 (c) |
| The boards' F1 kernel | `scripts/n1_baseline_leaderboard_tiering.py:312` (`permutation_test_float`); `FDR_Q = 0.05` at `:101`; `greedy_clique_tiers` at `:391` | the kernel, BH at q = 0.05, the greedy-clique tiers |
| The MCC permutation kernel | `scripts/pairwise_permutation_test.py:580` (`permutation_test_mcc_arrays`): one `default_rng(seed)` mask per permutation, so F1 and MCC see byte-identical masks for one seed, unit count, and order; a degenerate permuted MCC is scored 0.0 inside the null only (`_compute_mcc`, `:514`), never published (E81; `compute_mcc_or_none`, `:547`) | the kernel and both conventions; wave S also counts the draws with an undefined arm and reports lower and upper bounds that do not depend on the 0.0 convention (§ 3.6 (d)) |
| Board harness | `scripts/era1_leaderboard_tiering.py`: per-tile loaders `cell_per_tile` (`:334`) and `cell_per_tile_classification` (`:494`); F1 pairs `:1309`, BH `:1317`, MCC pairs `:1347`, BH `:1353`, tiers `:1373`; `--permute-mcc` shares the swap masks (header, lines 64–76) | the loaders (with the explicit Wave 1 joins), the round-robin families |
| 55-map MCC tiering | `scripts/mcc_tiering_55map.py`: `N_PERMUTATIONS`, `SEED` at `:92–93`; round robin and BH at `:521–523` | the family and the instrument |
| Per-cell intervals | `scripts/lib_advanced_metrics.py:3489` (`bootstrap_ci`, F1, precision, recall) and `:5107` (`bootstrap_tile_classification_ci`, MCC, sensitivity, specificity, dropping undefined resamples per E81); BCa through `scipy.stats.bootstrap` with a percentile fallback on a degenerate distribution (`_bca_ci_from_indices`, `:547`, whose `method` field records `BCa`, `percentile_fallback`, or `undefined`, and `n_valid` the usable resamples; `BOOTSTRAP_METHOD = "BCa"`, `:73`) | the estimator, the fallback, and E81's handling; wave S adds the fallback's reason and the jackknife diagnostics to the ledger (§ 3.5) |
| Paired and multi-run intervals | `bootstrap_effect_size_ci` (`:3745`; paired draw of the same tiles for both arms, `:3833–3834`), `bootstrap_multi_run_ci` (`:3957`), and `_multi_run_permutation` (`:4203`) | the pairing and each estimand |
| Selection-aware intervals and MCB | `scripts/selection_aware_intervals.py`: `run` (`:244`) redraws the argmax inside every resample (`:339–345`); MCB critical values at `:389–396`; resample weights from `resample_weights` (`:239`) | the replay of selection inside each resample, both MCB forms, the optimism correction |
| K-ladder drivers | `scripts/k_ladder_mcb.py` (10,000 resamples, seed 42, m-out-of-n fraction 1.0; header, lines 20–24; `BOOTSTRAP` and `SEED` at `:141–143`) and `scripts/k_ladder_mcc_test.py` (K = 1 versus the best rung and every adjacent pair, BH within each ladder; header, lines 17–51) | the pair sets, families, and gates |
| Precedent for sheet units | `scripts/stride55_sweep_oracle.py:243` and `:283`: a per-map paired sign-swap over the 55 sheets (10,000, seed 42), whose p-value is floored at `1/N` | the idea only; wave S uses the D42 kernels so its sheet design differs from the tile designs in the unit alone |

Three consequences:

1. **Every statistic is a function of summed counts.** Micro-F1, precision,
   and recall read summed TP, FP, and FN. MCC reads summed tile labels (TP,
   TN, FP, FN). So swapping every tile of a block together is the same as
   swapping the block's sums, and drawing a block in a bootstrap is the same
   as drawing its sums. No new statistical kernel is needed (§ 3.5).
2. **The singleton block is a free sentinel.** With every tile its own block,
   in the instrument's recorded tile order and in **legacy reproduction
   mode** (the `c / N` estimator), wave S's code must reproduce Wave 3's
   committed tile-level p-values, intervals, tiers, and admissible sets
   exactly (gate GS2, § 6).
3. **One inherited convention is not used for decisions.** The D42 p-value,
   `c / N`, can be exactly 0 and is not a valid permutation p-value. Wave S
   keeps it only to reproduce history, and decides every test, at the tile
   unit and at the block unit alike, with a valid estimator (§ 3.6 (c);
   Astra, round 1, S1).

## 3. The frozen design

Each subsection answers one of the five freeze items in the record's § 5
wave S row; § 12 maps them back. § 3.8 adds the scope of the inference.

### 3.1 Freeze item (i): eligible claims, comparisons, families, frames, buffers, joins, and estimands

**Eligibility rule.** A claim is eligible if, and only if, all four hold:

1. it is **inferential**: a significance verdict, a "no significant
   difference" statement, a tier or tie-set membership, an MCB admissible
   set, an interval that the claim reads (one that excludes, includes, or
   bounds a value), or a selection-aware (optimism-corrected) interval;
2. its instrument **resamples or permutes tiles**, reading a per-tile count
   table (F1, precision, recall) or a per-tile classification (tile-MCC,
   sensitivity, specificity);
3. it is **paper-relevant**: cited by a signed row of `results/run-analyses.json`
   (45 of its 71 rows carry `signature.status` `signed` at `fe9d433d7`), by
   `docs/paper/`, or by the claim records Wave 4 searches (the record's § 5,
   Wave 4 row);
4. its frame belongs to **either corpus**: the gold-standard (GS) frames or
   the 55-map frame (§ 3.4 lists all eight frames behind the signed tile-MCC
   rows).

A claim's tile-level p-value, interval, or direction plays no part in its
eligibility. A claim that was not significant at tile level is eligible on
the same terms as one that was.

**Known families** (the enumeration in S.0 must find at least these, or
explain the absence):

| Corpus | Family | Instrument | Committed tile-level artefact (before Wave 3) |
|---|---|---|---|
| GS, Era-2 frame | board F1 round robin, BH, tiers | `era1_leaderboard_tiering.py` | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json` (150 ranked cells, 3 withheld, 11,175 pairs) |
| GS, Era-2 frame | board MCC round robin, BH, tiers | same, `--permute-mcc` | same file, `mcc_permutation` (150 cells, 11,175 pairs) |
| GS, Era-2 frame | board MCB, F1 and MCC | `selection_aware_intervals.py --board` | `…/mcb/gs-era2-verified-board-2026-09-10_b20_m1.json`, `…_mcc_b20_m1.json` |
| GS, Era-2 frame | selection-aware headline intervals | `selection_aware_intervals.py` | `…/optimism/` |
| GS and 55-map | K-ladder pair tests, F1 and MCC | `k_ladder_mcc_test.py` | `results/k-ladder-2026-09-12/mcc-test/` (one file per ladder, `summary.json`) |
| GS and 55-map | K-ladder MCB | `k_ladder_mcb.py` | `results/k-ladder-2026-09-12/mcb/` |
| 55-map | final board F1 round robin, BH, tiers | the GS chain at 50 m | `results/55map-final-board-r2-2026-09-06/final_board_50m.json` (35 cells, 595 pairs) |
| 55-map | MCC tiering | `mcc_tiering_55map.py` or the board harness | the regenerated MCC family of Wave 3 |
| both | per-cell intervals that a claim reads | `bootstrap_ci`, `bootstrap_tile_classification_ci` | each cell's `evaluation.json` |
| both | paired hypothesis contrasts (H-series and named contrasts) that resample tiles | `bootstrap_effect_size_ci`, `bootstrap_multi_run_ci`, the D42 kernels | as cited by the register |

With the three Gemini 3.7 cells admitted under D73 (4), the Era-2 board
family would hold 153 cells and 11,628 pairs. Wave S takes each family's
membership from Wave 3, never recomputes it.

**Comparisons.** Exactly the pairs, contrasts, and candidate sets each
family's tile-level instrument tests after Wave 3: the full round robin for
boards, the K = 1-versus-best and adjacent-rung pairs for ladders, and the
candidate set for MCB and selection-aware intervals. Wave S adds no
comparison and drops none.

**Frames.** Each claim's own recorded frame (`_metadata.cli_args.bounds` of
its evaluations). Common-tile comparisons use the common tiles, each keeping
its block identity (§ 3.2 makes that identity independent of the frame).

**Buffers.** Each family's headline buffer: 20 m on the GS frames
(`HEADLINE_BUFFER_M`, `n1_baseline_leaderboard_tiering.py:98`), 50 m on the
55-map frame (`final_board_50m.json`, `buffer_m`). A claim made at another
buffer is checked at that buffer only.

**Joins.** Under the Wave 1 names: `sheet-contains` for classification
(MCC, sensitivity, specificity) and `sheet-primary` for count tables (F1,
precision, recall), as Wave 2 records them (`tile_join` and
`count_table_join`; Wave 1 spec, W1.1). No frame-wide join and no `id`
value enters wave S. On the 55-map corpus, the joins and references are
whatever the PI's seam ruling leaves them (§ 3.8).

**Estimands.** Unchanged from each family's tile-level instrument and copied
into the eligibility manifest per claim, so a reviewer can check them:

- **Single-set cells** (one aggregated detection set): micro-F1 of the
  summed integer per-tile counts, and tile-MCC of the summed tile labels.
- **Replicate-mean cells on the boards** (single-pass K runs, phase 3c
  replications): micro-F1 of **pass-averaged** per-tile counts, which are
  floats (`tiering_20m.json`, `replicate_handling`). They have no MCC arm:
  the harness refuses to collapse runs into one set for MCC
  (`era1_leaderboard_tiering.py` header, lines 74–76).
- **Multi-run contrasts with equal run counts**: the **mean over runs** of
  each run's micro metric, with each unit's whole run block swapping
  together (`_multi_run_permutation`, `lib_advanced_metrics.py:4203`); with
  unequal run counts, the micro metric of pass-averaged counts.
- **MCB and selection-aware**: Hsu's θ_i = F1_i − max_{j≠i} F1_j (or the
  MCC analogue) and the Efron–Gong optimism, as `run` computes them.

Because each estimand is a function of sums, block aggregation preserves it
exactly: the block sum of pass-averaged counts equals the pass average of
block sums. Pooled estimands **sum counts** across blocks; no block-level F1
or MCC is ever averaged.

### 3.2 Freeze item (ii): block construction and the tile-to-block map

**Blocks are squares on the ground, laid on each sheet's own raster grid.**

- **Sheet restriction.** A block never spans two sheets. A tile's sheet is
  the one the scorer's tile-sheet catalogue gives it (`frame_tile_sheets`,
  `lib_advanced_metrics.py:1497`), the same catalogue the sheet joins and
  symbol matching use (Wave 1 spec, W1.1). It is cross-checked against the
  bounds file's `map_name` and against the raster directory the tile's
  world file sits in; any disagreement stops the wave (§ 7).
- **Origin.** The north-west corner of the sheet's pixel (0, 0), located in
  EPSG:32635 (UTM zone 35N) metres.
- **Orientation.** Along the sheet raster's columns and rows, which are UTM
  easting and southing. Every tile polygon in all eight frames is an
  axis-parallel rectangle in EPSG:32635 (`block_census.txt`, "every polygon
  axis-parallel: True"), and every tile raster the geometry check below
  reads has no rotation terms in its world file.
- **Side.** A whole number of sheet pixels: 1,344 px for the primary design,
  672 px and 2,016 px for the sensitivity designs (§ 3.3). On the ground a
  sheet pixel measures 4.9952–5.0640 m on the 55-map frame and
  5.0100–5.0315 m on the GS frames, so 1,344 px is 6.71–6.81 km.
- **Membership.** A tile belongs to the block containing the **centre of its
  nominal pixel window**, `(x + T/2, y + T/2)`, where `x` and `y` are the
  pixel offsets in its name and `T` its tile size. Block column and row are
  `floor((x + T/2) / side)` and `floor((y + T/2) / side)`, with half-open
  intervals. Because 1,344 px is the least common multiple of the three
  strides in use (224, 336, and 448 px), every primary block is a whole
  group of tiles: 6 × 6 at 256 px, 4 × 4 at 384 px, and 3 × 3 at 512 px.
- **Clipping.** Some frame polygons are clipped: the census finds 32 on the
  Era-2 frame (south edge), 49 on the grid frame (south, east, north, or
  west edges, some on two), and 62 on the H13 frame (south or east edges, a few on both),
  and none on the other three tracked GS frames (`block_census.txt`,
  "independent geometry check"). Membership uses the **nominal** centre,
  never a clipped polygon's centroid. On these frames the clipped centroid
  would have moved no tile to another primary block, and one grid tile's
  nominal centre lies outside its clipped polygon; the rule is the same
  whatever those counts are.
- **Block identity.** The string `<sheet>|s<side>|c<column>r<row>`, for
  example `K-35-052-4_32635|s1344|c0r0`. It is a **pure function of the
  tile's sheet, name, tile size, and the side**. It does not depend on the
  frame, the condition, or which other tiles are present. So the map is
  automatically shared by every condition in a comparison, and a tile that
  appears in several frames has one identity in all of them.
- **Partial blocks.** The east and south edges of a sheet leave narrower
  blocks (13 columns of 384 px tiles give four primary columns, the last
  one tile wide). They are **kept as blocks**, not merged. Merging would make
  a block's identity depend on which tiles a frame holds, which would break
  the pure-function property. A small edge block is one draw unit, but it is
  not given the interpretation of a full block: its size and its share of
  each statistic's counts are reported (§ 3.4; § 3.5, "Partial blocks").
- **Holes.** Tiles missing from a frame leave smaller blocks or none. A
  block with no tile in the frame does not exist in that frame. Holes are
  not filled and blocks are not merged across them.
- **An arithmetic consistency check, and an independent geometry check.**
  The census also computes each tile's block from the name's offsets mapped
  into metres through the sheet's origin and pixel size. The origin and
  pixel size cancel algebraically, so that second route reduces to the
  first, and its agreement ("arithmetic routes disagree on 0 tiles") checks
  only the floating-point arithmetic of the block rule. It cannot detect a
  footprint that disagrees with its name (Astra, round 1, S2). The
  **independent geometry and name check** reads each tile's nominal
  footprint from its own raster: the `.pgw` world file beside the tracked
  PNG, and the PNG's size, neither of which comes from the bounds file or
  the name. It requires that (a) the sheet origin implied by every tile's
  raster and name offsets is one point per sheet, and the tile lies in its
  `map_name`'s raster directory; (b) an unclipped bounds polygon equals the
  nominal footprint, and a clipped one lies inside it and keeps at least
  two of its edges; (c) the block from the raster's nominal centre, and
  from an unclipped polygon's own centre, equals the block from the name.
  On the six GS frames whose rasters are tracked (`inputs/tiles_384/`,
  `inputs/tiles/`), every tile passes, unclipped polygons match their
  footprints to 9.3 × 10⁻¹⁰ m, and the red sentinel (one unclipped
  footprint moved one stride, and again 10 m, east with its name unchanged;
  one tile's `map_name` changed to another sheet) turns the check red each
  time, while the arithmetic check passes the displaced footprint
  (`block_census.txt`). The 256 px and 55-map frames' rasters are not
  tracked (`.gitignore` ignores `inputs/tiles_256/*/` and
  `inputs/tiles_384_55maps/`), so S.0 runs the same check on them where
  they are kept (§ 5). A polygon shrunk inside its footprint is
  indistinguishable from a clip; S.0 lists the clip classes so they can be
  reviewed.
- **Deterministic order.** In the block designs, blocks enter every kernel
  sorted by block identity. Tile order inside a block is irrelevant, because
  only sums enter a kernel. The **singleton legacy reproduction** keeps
  each instrument's recorded tile order instead: sorting singleton block
  identities would change which mask column meets which tile, and so the
  random-number mapping (Astra, round 1, S5).
- **Sheet blocks** (55-map only): the block is the sheet; the identity is
  `<sheet>|sheet`.

The maps are written to `reports/tile-join-wave-s/block-maps/<frame>.json`
(tile name to block identity, for each design) and hashed into the design
lock (S.0).

### 3.3 Freeze item (iii): primary and sensitivity sizes, and why

| Design | Side | Role | Applies to |
|---|---|---|---|
| **P** | **1,344 px (6.71–6.81 km)** | primary | every test and interval |
| S− | 672 px (3.36–3.40 km) | sensitivity, smaller | every test and interval |
| S+ | 2,016 px (10.07–10.21 km) | sensitivity, larger | every test and interval |
| Pst | 1,344 px, blocks drawn within each sheet | sensitivity, sheet-stratified bootstrap (§ 3.5) | bootstrap intervals, MCB, and selection-aware intervals |
| Sheet | the sheet (about 22 × 20 km) | sensitivity, 55-map only | every test and interval on the 55-map frame |
| Seam | after the PI's seam ruling (§ 3.8) | sensitivity, 55-map only, if frozen | as frozen |

These sizes were chosen from the geometry, the matching distances, and where
the reference mounds lie. No significance or interval width was consulted,
and none exists yet: no block statistic has been computed, and the corrected
tile-level results of Waves 2 and 3 do not exist at the time of writing.
They are a **frozen, pragmatic bracket**, which Astra accepts as such
(round 1, S3). They are not a demonstrated solution to within-sheet or
between-sheet dependence, and the claim wording must keep that distinction
(§ 3.6 (b); § 10).

**Tile overlap.** At 384 px, neighbouring tiles share a 48 px strip (about
240 m), one eighth of a tile; the 512 px and 256 px tilings overlap by 64
and 32 px, also one eighth (`block_census.txt`). Within a block, overlap
does not matter. Across a block boundary, two tiles share at most that
strip, which is 48 / 1,344 ≈ 3.6 % of a primary block's width. A mound in
that strip can count in two blocks, but no wider ground can.

**Matching distance and the booking regions.** The matching distance is
20 m on the GS frames and 50 m on the 55-map frame, about 4 and 10 sheet
pixels. Astra's R3 mechanism (a matched target booked at its detection's
tile in one condition and at its reference's tile in another) moves an
outcome between blocks only when the two points **book into different
blocks**. Booking has two stages: `sheet-primary` books a point to the
nearest-centroid tile among the tiles of its own sheet that it intersects,
with ties to the smallest `tile_name` (Wave 1 spec, W1.1), and that tile's
block is fixed by the centre rule above. On a regular, unclipped grid the
tile booking regions are therefore one stride wide, bounded midway between
neighbouring tile centres, and a block's booking region is the union of its
tiles' regions. **Its boundary is not the block square's edge.** On the
384/336 px grid, block column 0 ends where its last tile (start 1,008 px,
centre 1,200 px) meets the next block's first tile (start 1,344 px, centre
1,536 px), at 1,368 px. In general the boundary lies at
k × 1,344 px + half the overlap: 1,368, 1,376, and 1,360 px for k = 1 on
the 384, 512, and 256 px tilings. So points at 1,367 and 1,369 px book into
different blocks although both are more than 10 px from the square's edge
at 1,344 px (Astra's probe, `wave-s-design-probe.json`). These block booking
boundaries recur every 1,344 px along each axis, against every stride (336,
448, or 224 px) for tiles. For a pair of points a given distance apart
along one axis, the set of positions at which a boundary falls between
them is therefore a quarter as large for primary blocks as for tiles on the
384 px tilings, a third on the 512 px tilings, and a sixth on the 256 px
tiling. That is geometry on the regular grid, **not a measured rate**:
whether matched pairs lie uniformly with respect to the grid is unknown,
and near clipped polygons and holes the boundaries move, because
`sheet-primary` uses the frame's own polygon centroids. S.0 reports, per
frame and design, how many references lie within the matching distance of
a block booking boundary computed from the frame's own polygons
(descriptive only; § 5).

**Plausible spatial dependence.** The dependence that matters is in the
paired difference between two conditions' per-tile outcomes, and that cannot
be measured before the design is frozen. The nearest observable proxy is
where the reference mounds lie. `occupancy_correlogram.txt` describes it by
**Chebyshev lag** in strides (one stride, 336 px, is about 1.7 km). A
Chebyshev lag L takes the pairs of tiles of one sheet with
`max(|di|, |dj|) = L`, so it pools axial pairs (centres L strides apart)
with diagonal ones (up to L√2). Two of its statistics are below. The
**pooled** column is the Pearson correlation of occupancy over the list of
pairs. The **within-sheet** column is not a Pearson correlation: it is the
mean, over the lag's pairs, of the product of the two tiles' occupancies
centred on their sheet's mean, divided by the whole-frame within-sheet
variance (`occupancy_correlogram.py`, the line computing `within`; Astra,
round 1, S3). It is called the *within-sheet cross-product* below.

| Chebyshev lag (strides) | Era-2, pooled r | Era-2, within-sheet cross-product | 55-map, pooled r | 55-map, within-sheet cross-product |
|---:|---:|---:|---:|---:|
| 1 (tiles overlap) | 0.361 | 0.188 | 0.251 | 0.165 |
| 2 | 0.262 | 0.048 | 0.155 | 0.057 |
| 3 | 0.273 | 0.072 | 0.124 | 0.024 |
| 4 | 0.216 | 0.012 | 0.107 | 0.005 |
| 6 | 0.140 | −0.057 | 0.079 | −0.023 |
| 8 | 0.102 | −0.052 | 0.053 | −0.047 |

This is **descriptive design evidence**, not an estimate of the dependence
range of model contrasts. Two patterns show:

- **Short-range, within a sheet.** Once each sheet's mean is removed, the
  within-sheet cross-product falls from 0.165–0.188 at Chebyshev lag 1,
  where tiles share ground, to 0.024–0.072 at lags 2–3 and 0.012 or less at
  lag 4. Small values at a pooled lag do not show that dependence ends
  there. Nor do 4-stride blocks place their tiles beyond that range from
  other blocks: in a complete interior 4 × 4 block, twelve tiles have a
  centre one stride from a tile of a neighbouring block and four have one
  two strides away, and none is farther (Astra's probe). Wider blocks
  reduce the share of short-range tile pairs that straddle a unit boundary,
  and so the dependence between aggregate units; they do not establish
  independence.
- **Sheet-level.** The pooled correlation stays positive out to lag 8
  because sheets differ greatly in mound density: the share of
  reference-occupied tiles ranges from 0.099 to 0.619 across the four Era-2
  sheets, and from 0.038 to 0.686 across the 55 sheets. Differences in map
  style, print, and scan between sheets are also plausible. No within-sheet
  block captures this. On the 55-map corpus sheet blocks test it directly;
  on the GS corpus four sheets are too few (§ 3.6 (c)), which is stated as a
  limit (§ 10).

**Why 1,344 px is primary.** It is the smallest side that groups whole
tiles on every tiling in the corpus. It is 28 times the 384 px overlap and
about 130 times the 55-map matching distance. It is larger than the
Chebyshev lags (1–3) at which the reference-occupancy cross-product is
visibly positive, which is descriptive evidence only. And it leaves 48
blocks on every GS frame and 660 on the 55-map frame. With d informative
blocks the finite swap-group floor is 2^(1−d), below even the first-rank
BH threshold of the 153-cell board (about 4.30 × 10⁻⁶) once d ≥ 19; the
binding limits are then the Monte Carlo floor and the multiplicity
procedure (§ 3.6 (c)), and no block count by itself guarantees interval
coverage. The block count is a validity constraint on the resampling, not
the reason for the size: 1,008 px (74 GS blocks) would give more blocks but
does not group whole tiles at 512 px or 256 px, and 2,688 px, the next
whole-tile side, leaves 16 GS blocks, too few for intervals. D73 (3)
anticipated "roughly 30 to 50 blocks on the 487-tile frame"; the primary
design gives 48.

**Why the sensitivity sizes.** S− halves the side: 2 × 2 tiles at 384 px,
the smallest block with more than one tile in each direction. Its spacing,
Chebyshev lag 2, is where the within-sheet cross-product has fallen to
0.048–0.057, so it brackets the short-range pattern from below. S+ is half
as large again: of the candidate sides in `block_census.txt`, the largest
that keeps at least 20 blocks on every GS frame (24). Pst keeps the primary
blocks and changes only the bootstrap's sampling scheme (§ 3.5). The sheet
design probes the sheet-level dependence that no within-sheet block can.
The sizes are a bracket around the primary, not a search for the best: no
claim may rest on whichever design favours it (§ 3.6).

On the 512 px frames, S− (1.5 strides) and S+ (4.5 strides) do not group
whole tiles. Membership is still deterministic by the centre rule, but the
blocks are uneven; § 3.4 reports them.

### 3.4 Block counts and sizes per frame (design information)

Computed by
`planning/tile-join-wave-s-spec-2026-11-18-scripts/block_census.py`
(output `block_census.txt`), which reads the bounds files and, for the
independent geometry check, the tracked tile rasters' world files and PNG
headers. "Overlap another block" counts tiles whose footprint overlaps,
with positive area, a tile assigned to a different block, in the same sheet
or in another sheet.

| Frame | Tiles (sheets; tile/stride px) | S− 672 px: blocks (tiles per block min/median/max) | **P 1,344 px**: blocks (min/median/max; under 4 tiles) | S+ 2,016 px: blocks (min/median/max) | Sheet blocks | Independent geometry check |
|---|---|---|---|---|---|---|
| `inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson` | 487 (4; 384/336) | 155 (1/4/4) | **48 (1/12/16; 1)**, 12 per sheet | 24 (3/21/36) | 4, not used | 487 pass (32 clipped) |
| `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` | 487 (4; 384/336) | 155 (1/4/4) | **48 (1/12/16; 1)** | 24 (3/21/36) | 4, not used | 487 pass |
| `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson` | 487 (4; 384/336) | 155 (1/4/4) | **48 (1/12/16; 1)** | 24 (3/21/36) | 4, not used | 487 pass (49 clipped) |
| `inputs/vectors/bounds/384/h10_test_bounds.geojson` | 327 (4; 384/336) | 148 (1/2/4) | **48 (1/8/15; 14)** | 24 (2/14.5/27) | 4, not used | 327 pass |
| `inputs/vectors/bounds/full_evaluation_bounds.geojson` | 340 (4; 512/448) | 165 (1/2/4) | **48 (3/8.5/9; 12)** | 24 (4/15.5/25) | 4, not used | 340 pass |
| `outputs/h13/scoring/bounds/h13_common_bounds.geojson` | 340 (4; 512/448) | 165 (1/2/4) | **48 (3/8.5/9; 12)** | 24 (4/15.5/25) | 4, not used | 340 pass (62 clipped) |
| `inputs/vectors/bounds/256/full_evaluation_bounds.geojson` | 1,032 (4; 256/224) | 152 (1/8/9) | **48 (1/25.5/36; 2)** | 24 (4/50.5/81) | 4, not used | not tracked; S.0 |
| `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` | 8,541 (55; 384/336) | 2,310 (1/4/4) | **660 (3/16/16; 3)**, 12 per sheet | 330 (5/36/36) | **55** (143/156/156) | not tracked; S.0 |

Dependence that blocks leave in place, under the primary design:

| Frame | Tiles overlapping a tile of another block, same sheet | Tiles overlapping a tile of another sheet |
|---|---:|---:|
| Era-2 (487) | 304 (62.4 %) | 24 (4.9 %) |
| 55-map (8,541) | 5,482 (64.2 %) | 2,816 (33.0 %) |

Most tiles of a 4 × 4 block lie on its edge, so most tiles touch another
block; what they share is the 48 px strip. The cross-sheet column is
independent of block size. On the Era-2 frame those contacts are the
no-data padding of the record's § 2.6. On the 55-map frame they are seams
where neighbouring sheets overlap and can show the same ground about 170 m
apart (record § 2.4). Wave 1's 55-map sheet check has since found that 32
reference–tile contacts (26 references) lie on another sheet's map
content, at nine seams involving the reprojected `_4326` sheets (§ 3.8). No
within-sheet block, and not even the sheet design, removes that
dependence (§ 10).

These numbers become a regression check: wave S's own block maps must
reproduce this table exactly (gate GS4).

### 3.5 Freeze item (iv): units, draws, intervals, seeds, selection, and multiplicity

**Permutation unit.** The block. Under the null hypothesis, within each
block the two arms' labels are exchangeable. Each permutation swaps a whole
block's counts between arms with probability 0.5, and for multi-run arms
the block's whole run stack swaps together. Implementation: sum each arm's
per-tile arrays within blocks (per run where there are runs), then call the
unchanged kernel (§ 2) on the block arrays. The validity of the test rests
on that exchangeability under the allowed swaps (stated as an assumption,
§ 3.8); the arithmetic of the estimator cannot repair a failure of it.

**Exact enumeration.** When the number d of informative blocks (§ 3.6 (c))
satisfies 2^d ≤ N, that is d ≤ 13 at N = 10,000, the test enumerates the
whole swap group of the d informative blocks instead of sampling, and its
p-value is the exact proportion (§ 3.6 (c)). Swapping a non-informative
block changes no input, so the group over all blocks gives the same
proportion. The singleton (tile) design enumerates under the same rule.

**Bootstrap unit.** The block, drawn with replacement, as many draws as
there are blocks (n out of n; m-out-of-n fraction 1.0 for MCB, as
committed). A drawn block contributes all its tiles' counts. Per-cell and
paired intervals call `_bca_ci_from_indices` on block indices whose
statistic sums block arrays, so BCa's jackknife acceleration becomes a
leave-one-block-out jackknife automatically. MCB and selection-aware
intervals call `run` with tile weights set to the multiplicity of each
tile's block in the draw. That needs one small change to `run` (it draws its
own weights today, `selection_aware_intervals.py:340`): a block map
parameter, defaulting to singleton blocks so the committed behaviour is
unchanged.

**Stratification, and the inferential target.** The primary block bootstrap
is **unstratified**, matching the tile-level bootstrap, so that P differs
from the tile analysis in its unit alone. It treats the frame's blocks as
draws from one population of blocks, with the sheet mix varying between
resamples. **Pst**, a declared sensitivity design, is the **sheet-stratified
block bootstrap**: each resample draws, within every sheet, as many primary
blocks as that sheet has, with replacement, so every sheet keeps its
representation. Its target is inference **conditional on these particular
sheets**. Neither design is evidence about arbitrary new sheets; on the
55-map frame the sheet design comes nearest to that, with 55 sheet units,
and on the GS frames no design does (§ 3.8; Astra, round 1, answers table).
Pst applies to bootstrap intervals, MCB, and selection-aware intervals
only: a permutation test already conditions on the observed blocks, so it
has no stratified form. Its interval method is fixed in advance as the
**percentile** method, because neither BCa path supports stratified draws
with a block jackknife as committed; this is the design's declared method,
not a fallback. So that the Pst comparison changes one thing, the ledger
also reports the P percentile interval from P's own draws beside it.
`run` takes stratified weights through the same block-map parameter. Whether
Pst should be primary instead is a question for the PI (§ 11).

**Shared draws.** As at tile level:

- one swap-mask stream, `default_rng(42)`, re-seeded for every pair, so
  every pair of a family with the same block count sees the same masks;
- F1, precision, recall, and MCC of one pair share one mask sequence (same
  seed, same block order);
- in a paired interval, both arms take the same block draws;
- in an MCB or selection-aware family, every candidate takes the same block
  draws, and the argmax is redrawn inside each resample;
- each per-cell interval is seeded 42, as `evaluate_detections.py` runs it
  (`_metadata.cli_args.seed` 42, `bootstrap` 10000, for example in
  `results/55map-final-board-r2-2026-09-06/cells/A-N1-oracle/evaluation.json`).

**Draw budget: fixed and predeclared.** Proposed: 10,000 permutations per
sampled test and 10,000 bootstrap resamples per interval or MCB family, for
every design, the singleton included, as at tile level. **Lock order**: the
budget is fixed in the design lock only after the synthetic timing
benchmark (S.0; P6) has run and the PI has made the cost and precision
choice (§ 11, question 11), and it applies to every test alike. There is
**no data-dependent extension**: no test is re-run with more draws because
of its result, and the budget is never raised selectively after real
results are seen. Extending selected tests and treating the resulting
fractions as fixed-budget p-values would not be justified (Astra, round 1,
S1). A test whose verdict the fixed budget cannot settle is recorded as
**Monte Carlo-unresolved** (§ 3.6 (c)). The exact-enumeration rule
(2^d ≤ N) follows the locked budget.

**Ties.** For the valid and exact estimators, a null draw counts as at least
as extreme when `|T_null| >= |T_obs| − ε`, with ε = 10⁻¹² × max(1, |T_obs|),
frozen in the lock. The observed assignment and its complete reversal are
then both counted as at least as extreme even when floating-point summation
order differs by a unit in the last place. The legacy reproduction keeps
the kernel's exact comparison, so that it reproduces Wave 3. Both counts
come from the same draws, and the ledger flags any test where they differ.

**Interval method and its reporting.** Each instrument's own: BCa with the
inherited percentile fallback on a degenerate distribution for per-cell and
paired intervals; percentiles and the bootstrap critical values of both MCB
forms for MCB and selection-aware intervals; percentiles for Pst. **Nothing
switches method automatically because blocks are few**, and no count
threshold selects a method. For every interval the ledger records the
method actually used, the **reason** for any fallback (a constant bootstrap
distribution, or a jackknife acceleration that cannot be computed), the
**usable resample count** (`n_valid`), and the **jackknife diagnostics**:
the number of leave-one-block-out values that are undefined or that equal
the full-data statistic. Degenerate MCC resamples are dropped, as E81
requires, and counted.

**Partial blocks, and contribution imbalance.** For every test and interval
the ledger reports the number of contributing blocks, each block's share of
the statistic's total counts (TP + FP + FN for F1, precision, and recall;
tiles for MCC, sensitivity, and specificity), the largest block's share,
the partial blocks' combined share, and the effective number of blocks
(Σw)² / Σw², with w a block's count contribution. These are reported, not
rules; they let a reader see when a few blocks carry a result.

**Selection.** Where the tile-level instrument repeats a selection inside
each resample (the argmax in MCB and selection-aware intervals), the block
analysis repeats it inside each block resample. Where the tile-level
instrument treats a choice as fixed (the operating point of an `oracle`,
`opmax`, or `carried` cell in a pairwise test), wave S treats it as fixed
too, and adds or removes no selection correction. The scope this implies is
stated in § 3.8.

**Multiplicity.** Benjamini–Hochberg (BH) at q = 0.05 within each family,
exactly as Wave 3 constitutes it (same members, the D73 (4) cells
included), applied to the valid block p-values, and separately to the valid
singleton p-values. Tiers are rebuilt by the same greedy clique from each
set of verdicts. The designs (P, S−, S+, Pst, Sheet, and Seam if frozen)
are not extra hypotheses, so there is no correction across them: no design
is chosen for its result, and the decision rule requires agreement rather
than taking the best (§ 3.6). Resolution is judged against this BH
procedure, not against a fixed 0.05 (§ 3.6 (c)).

### 3.6 Freeze item (v): decision rules

These rules are fixed before any claim's block result is known, and apply to
every eligible claim alike.

**(a) The verdicts a claim carries.** Each eligible claim has three kinds of
verdict (significant or not after BH; in a tier or not; in an admissible
set or not; an interval that excludes a value or not):

- the **legacy tile verdict**: Wave 3's committed verdict, from `c / N`;
- the **valid tile verdict**: the same tests at the singleton unit, decided
  with the valid estimator of rule (c), from the same draws;
- the **valid block verdict** under each applicable design: P, S−, S+, Pst
  (bootstrap claims), and, on the 55-map frame, Sheet and Seam if frozen.

The **estimator change** is the legacy tile verdict against the valid tile
verdict. The **unit change**, which is wave S's question, is the valid tile
verdict against the valid block verdict. Intervals, MCB sets, and
selection-aware intervals carry no p-value, so for them the two tile
verdicts coincide.

**(b) Categories.** **PROVISIONAL for estimator changes, pending the
PI's ruling on § 11, question 9.** Until that ruling, nothing below settles
how a claim with an estimator change is worded, and the "stands" wording
in the Qualified row does not apply to it (see "Estimator changes", below).

| Category | When | What the paper says |
|---|---|---|
| **Supported** | no estimator change; the valid P verdict equals the valid tile verdict, and P is resolved and reliable; and every applicable sensitivity design gives the same verdict, resolved and reliable | the claim stands, with a sentence that it is robust to the specified block designs, naming them; on the 55-map frame the sentence also states the seam scope of § 3.8 |
| **Qualified** | anything short of Supported that is not Withdrawn: an estimator change; a resolved sensitivity design that disagrees; any applicable sensitivity design that cannot resolve the claim, is Monte Carlo-unresolved, or is unreliable; P unable to resolve it, Monte Carlo-unresolved, or unreliable (rules (c) and (d)); or a newly significant block result (Direction, below) | for a unit-change or sensitivity reason: the claim stands with the qualification stated, naming each design and the reason; the resolved checks are reported separately. For an estimator change: **provisional**, pending § 11, question 9; the wording must not be read as settled that the claim stands |
| **Withdrawn** (as a significance claim) | no estimator change; the valid tile verdict is significant, and the valid P verdict is not, with P resolved (it could have rejected, rule (c)), Monte Carlo-resolved, and reliable | the significance, tier, or admissibility claim is withdrawn; the point estimate stays, described as a difference not established under spatial-block resampling, never as evidence of no difference |

**Direction.** The categories apply to a significant tile-level verdict that
loses significance. A non-significant tile-level verdict that becomes
significant under blocks is not turned into a new positive claim: wave S
creates no claims, and none may be selected after the results are seen. It
is reported as a disclosed conflict (the project's research-finding
calibration) and the original claim is **qualified**. A non-significant
verdict that stays non-significant is Supported as a statement about
significance only; it is never reported as equivalence or as the absence of
an effect.

**Estimator changes (PROVISIONAL, pending the PI's ruling).** A claim
whose legacy and valid tile verdicts differ rests on the invalid estimator.
For bookkeeping it is placed in **Qualified** and listed for the PI
whatever its block verdicts, with its block verdicts reported beside it,
and the estimator and unit effects kept separate. How such a claim is
worded, and whether its significance assertion is withdrawn, is the PI's
decision (§ 11, question 9, which records Astra's recommendation); this
specification does not rule on it, and no text here should be read as
saying such a claim stands.

Tier and set claims are judged member by member. A claim that X is in the
top tier, or cannot be ruled out as best, is supported if X's membership
holds under P, and so on through the table. A claim about the whole
partition ("the board has N tiers") is qualified whenever the partition
changes under P.

An interval that a claim quotes but does not reason from (for example
"F1 0.90, 95 % CI …") is not categorised. The block interval is reported
beside it, and the tile-level interval stays the reported one: its tile
resampling unit was pre-specified in Decision 10
(`docs/methodology/preregistration/decisions-log.md:345`) before
lodgement, not registered. The lodged registration asks only for 95 %
bootstrapped intervals
(`docs/methodology/preregistration/osf/preregistration.md:293`) and names
no unit
(E54, attribution corrected 2026-07-28; E82 records that the method became
BCa).

**(c) Estimators, resolution, and power.** Three different limits are kept
apart (Astra, round 1, S1).

- **The decision estimator.** With N sampled swap patterns and c of them at
  least as extreme as the observed one (ties as in § 3.5), the p-value is
  `(c + 1) / (N + 1)`, the valid Monte Carlo p-value that counts the
  observed assignment (Phipson and Smyth; Hemerik and Goeman, as cited by
  Astra). Under exact enumeration (§ 3.5) it is the exact proportion of the
  2^d patterns at least as extreme, which counts the observed assignment and
  its complete reversal. **`c / N` is used only in the legacy reproduction
  mode** (S.2), never for a wave S decision. Every test reports c, N, both
  estimators, and whether it was enumerated.
- **Finite swap-group resolution.** An **informative block** for a paired
  test is one where the two arms' block sums differ in any input to the
  statistic; let d be their number. If d = 0 the arms are identical in
  every block, every pattern gives the observed statistic, and **p = 1**
  under every estimator. If d ≥ 1, the observed assignment and its complete
  reversal are distinct and equally extreme, so the exact p-value is at
  least 2^(1 − d). That is a **lower bound**, not a value a given contrast
  attains: ties among other patterns raise it. Under enumeration the
  ledger records the exact attainable minimum (the share of patterns that
  reach the largest |T|). Every test reports d and its floor.
- **Monte Carlo resolution.** A sampled test's estimator cannot go below
  1/(N + 1), about 1.0 × 10⁻⁴ at N = 10,000. For the 153-cell Era-2 board
  (11,628 pairs), the first-rank BH threshold is 0.05 / 11,628 ≈ 4.30 ×
  10⁻⁶, which neither 10,000 nor 100,000 draws can reach (Astra's probe:
  at least 232,559 draws would be needed). This does not prohibit
  rejections at later ranks: a p-value at the 10,000-draw floor can be
  rejected once the BH rank reaches 24 on that family, or 2 on the 595-pair
  55-map board. The first draft's statement that 48 blocks give "p-values
  far below any BH threshold the families need" was wrong and is
  withdrawn. A sampled test is **Monte Carlo-unresolved** if replacing its
  p-value by either end of the 99 % Clopper–Pearson interval for its
  exceedance probability (from c of N), holding the rest of its family
  fixed, changes its BH verdict. **"Monte Carlo-resolved" means only that
  this per-test check passed.** It is not a statement that the BH family's
  rejections are jointly stable: with two p-values of 0.051 and 0.052 at
  q = 0.05, lowering either alone to 0.049 rejects neither, while lowering
  both rejects both (Astra, round 2). The joint Monte Carlo error of a
  family is not bounded, which is a stated limit (§ 10). Monte Carlo
  precision, the validity of the randomised p-value, and exchangeability
  are separate questions.
- **Two different floors (Astra, round 2, S7).** They concern different
  quantities and are never substituted for each other:
  - the **exact-group lower bound** 2^(1 − d) (d ≥ 1) bounds the exact
    proportion over the whole swap group. It is a **diagnostic**, reported
    for every test. It does not bound a sampled estimate: random sampling
    can miss the extreme patterns, so the valid sampled p-value can fall
    below it. At d = 14, the first d sampled under the enumeration rule,
    the exact-group bound is 1/8,192 while a 10,000-draw estimate can be
    1/10,001; even if the exact tail probability were 1/8,192, 10,000 draws
    with replacement would find no extreme pattern with probability about
    0.295. The ledger flags any sampled p-value below its exact-group bound;
  - the **estimator's own attainable minimum**: 1/(N + 1) for a sampled
    test, and, under enumeration, the exact attainable minimum (the share
    of patterns that reach the largest |T|).

  **The valid sampled p-value is never clamped** to 2^(1 − d) or to any
  other estimator's value, and every BH decision uses it as computed.
- **Resolution against the multiplicity procedure, and which floor
  controls the category.** The claim category is controlled by the
  **resolution floor** r, defined once and frozen in the lock:
  - under enumeration, r is the exact attainable minimum;
  - for a sampled test, r = max(1/(N + 1), 2^(1 − d)). This is an
    explicitly **conservative policy for interpreting a non-rejection**,
    not a claim that a sampled test cannot reject below 2^(1 − d) (it can,
    and such a rejection stands as computed). It ensures that a claim is
    never withdrawn on a test whose exact swap group could not have
    rejected it.

  A test **can resolve** a significant verdict only if, with its p-value
  replaced by r and the rest of its family held fixed, BH would reject it;
  r enters only this counterfactual check, never the test's own decision.
  A test whose r exceeds q = 0.05, the largest threshold BH can use, cannot
  reject at any rank; that coarse check covers every d ≤ 5
  (2^(1 − 5) = 0.0625), all of which are enumerated. A tile-level
  significant claim whose valid P verdict is non-significant but which P
  cannot resolve is **qualified**, not withdrawn. No other interpretation
  of resolution may be substituted in the implementation.
- **Power.** None of this measures power, the chance of rejecting under a
  given alternative, which wave S does not estimate. A resolved
  non-rejection is a difference not established, not evidence of
  equivalence or of no effect.
- **The sheet design on the GS frames** has d ≤ 4, so its floor is at
  least 0.125. It cannot resolve anything, and is not run there.
- **Interval flags.** A block interval that a claim reads is flagged, and
  the claim qualified, if fewer than 20 blocks contribute to the statistic
  (for F1, precision, and recall, blocks with any TP, FP, or FN in that
  cell; for MCC, sensitivity, and specificity, all blocks), if it came from
  a numerical fallback, or if rule (d) flags it. These are predeclared
  reporting flags. Passing them does not establish that the interval covers
  at its nominal rate, and **a numerical fallback never yields an
  unqualified supporting interval**. P has 48 blocks on every GS frame and
  660 on the 55-map frame; S+ has 24 on the GS frames (§ 3.4).

**(d) Degenerate MCC.**

- An MCC that is undefined on the full data stays undefined (E81). The cell
  makes no MCC claim, as at tile level.
- In a bootstrap, undefined resamples are **dropped and counted**, never
  scored as 1 or 0, and their share is reported. If more than 1 % of
  resamples are undefined, the interval is flagged unreliable, and a claim
  reading it is qualified.
- In a permutation null, the inherited kernel scores an undefined permuted
  MCC as 0.0 (`pairwise_permutation_test.py:514`). Zero imputation has no
  defined MCC to be compared with, and it can itself make the difference
  between the arms extreme. Wave S therefore separates three counts over
  the same draws (or, under enumeration, the same M = 2^d patterns):
  - u, the draws in which **either arm's** MCC is undefined, each counted
    **once** however many arms are undefined;
  - c_defined, the draws at least as extreme as the observed one **with
    both arms defined**;
  - c_inherited, the draws at least as extreme under the inherited 0.0
    convention (c_defined ≤ c_inherited ≤ c_defined + u).

  It reports the **union bounds**: the upper count is c_defined + u (every
  undefined draw counted as extreme, but only once, since an undefined draw
  may already be extreme under the 0.0 convention), giving
  `(c_defined + u + 1) / (N + 1)` when sampled and `(c_defined + u) / M`
  under full enumeration; the lower count is c_defined, giving
  `(c_defined + 1) / (N + 1)` and `c_defined / M`. The upper bound never
  exceeds 1. The **inherited-convention estimate**,
  `(c_inherited + 1) / (N + 1)` or `c_inherited / M`, is kept separately,
  and is the one BH uses, for comparability with Wave 3. The test is
  flagged unreliable, and its claim qualified, if more than 1 % of draws
  have an undefined arm, or if its BH verdict (the rest of its family held
  fixed) differs between the lower and upper bounds. Astra's synthetic
  example (reference `[1, 0, 1, 0]`, arms `[1, 0, 0, 0]` and
  `[0, 0, 1, 0]`, M = 4) has c_inherited = 4, u = 2, and c_defined = 2:
  the round-1 formula gave 7/5, the union bounds give 2/4 and 4/4.

**(e) Conflicting designs.** P decides. A resolvable disagreement from S−,
S+, Pst, Sheet, or Seam qualifies a claim but never withdraws it, and never
rescues a claim that P withdraws. If S− disagrees while S+ and Sheet agree,
the pattern is unexpected, since smaller blocks are usually the less
conservative design. It is reported as surprising and the claim is
qualified.

**(f) What is never a reason.** A claim is never re-categorised because of
its importance to the paper, its effect size, or a preference among
designs. No design, block size, seed, draw budget, estimator, tolerance, or
threshold may change after the design lock. The one addition the lock
provides for in advance is the seam design of § 3.8, frozen before any
55-map block statistic.

### 3.7 What wave S does not change

- point estimates of every metric;
- the reported intervals and tests: the tile-level intervals, whose tile
  resampling unit was pre-specified in Decision 10 before lodgement (the
  registration names bootstrapped intervals, not their unit; E54), and the
  tile-swap tests of D42; wave S is a robustness check beside them. Its
  valid tile verdicts are a diagnostic of the estimator, not a replacement
  for Wave 3's (§ 11 asks the PI whether Wave 3 should adopt the valid
  estimator);
- family membership, estimands, joins, buffers, frames, and seeds;
- any committed `evaluation.json`, tiering, or MCB artefact (wave S writes
  only under `reports/tile-join-wave-s/`).

### 3.8 Scope of the inference, and the 55-map seams

**What the intervals and tests are about.** Every wave S interval and test
describes the variability of **fixed, realised outputs** at their recorded
operating points, over the frame's blocks. They are not uncertainty for the
whole tuning procedure: the choice of operating point, prompt, or
configuration is not resampled, except where the inherited instrument
already replays a selection (MCB and selection-aware intervals), which wave
S keeps. The tile-swap test still compares two outputs, not two
configurations (tracker W2.7; `lib_permutation.py` module docstring).

**Exchangeability.** The block permutation test assumes that, under the
null, the joint distribution of the outputs is unchanged by swapping the
arms in any set of blocks. Independent block swaps need that argument in
their own right; it is plausible for comparisons of outputs from identical
requests and is assumed, not shown, for others.

**Stratification.** The unstratified bootstrap (P) and the sheet-stratified
one (Pst) answer different questions (§ 3.5); the paper names which one an
interval comes from, and neither is described as evidence about new sheets.

**The 55-map seams.** Wave 1 stopped on 2026-11-18 because, on the r2
reference behind smoke cell 2 (`best-available-gt-55maps-r2.geojson`), 32
point–tile contacts (26 references) lie on map content of a neighbouring
sheet's tile, all at nine seams involving the reprojected `_4326` sheets;
the PI is asked how sheet-specific scoring treats a mound printed on both
sides of a seam but digitised once
(`reports/tile-join-wave-1/stop-2026-11-18-55map-seams.md` on branch
`tile-join-wave-1-w10`, § 1 and § 4). The designs above do not test
shared-ground dependence across sheets, and a favourable within-sheet or
sheet-block result cannot validate that omitted dependence. So:

- **Until the PI's seam ruling,** wave S's 55-map scope is explicitly
  qualified, and no 55-map block statistic runs (P7). The ruling may also
  change the 55-map references or joins themselves, which reach wave S
  through Waves 2 and 3.
- **After the ruling,** a **seam-aware sensitivity design** is specified
  (for example, joining into one unit the blocks on both sides of each seam
  where a reference lies on the other sheet's map content), reviewed by
  Astra, and frozen in the design lock before any 55-map block statistic.
  It is then an applicable sensitivity design under § 3.6.
- **If no seam-aware design is frozen,** the lock records that choice, and
  every 55-map claim's category carries the scope statement that
  cross-sheet shared ground at seams is untested.

## 4. Inputs from Waves 2 and 3

Wave S needs Wave 2's re-scored per-tile tables under the new joins and
Wave 3's regenerated families. Waves 2 and 3 are specified after Wave 1;
this section is the contract their specifications must meet for wave S.

**Per-tile count table** (from `sheet-primary`), one row per (claim cell,
run, tile, buffer):

| Field | Meaning |
|---|---|
| `cell_id` | the register's `run::label` |
| `run` | pass index, or `null` for a single set |
| `tile_name` | a tile of the claim's frame |
| `buffer_m` | the matching distance |
| `tp`, `fp`, `fn` | integer counts, or pass-averaged floats for replicate-mean board cells |

**Per-tile classification** (from `sheet-contains`), one row per (claim
cell, tile): `cell_id`, `tile_name`, `ref_positive`, `detected`, and the
one-hot label (TP, TN, FP, or FN).

**Provenance** for each table: `count_table_join` or `tile_join`; the
bounds, reference, and detection files with their SHA-256 hashes; the
estimand and replicate handling; and the cell's family memberships, with its
D73 (4) admission status.

**Invariants** wave S re-checks before use, stopping on failure: every
count table sums to the symbol-level totals, overall and per sheet (Wave 1
G1 item 5); the tile vocabulary equals the frame's; each table reproduces
the cell's committed aggregate confusion or counts under the new joins.

**Tile-level results** from Wave 3, for every eligible family: raw and BH
p-values, tiers, MCB sets, and intervals, with their kernels, seeds, draw
counts, and **tile order**, and, for every test, its exceedance count c or
a p-value and N from which c follows exactly. These are the targets of the
singleton-block sentinel (GS2).

**Recommendation for Waves 2 and 3** (§ 11, PI question 4): export these
tables once, as a committed cache with a manifest, rather than have wave S
rebuild them. If they are not exported, wave S rebuilds them through the
same loaders Wave 3 uses (`cell_per_tile`, `cell_per_tile_classification`)
with the joins named explicitly, and gates each one against Wave 3's
committed aggregates.

## 5. Work items

### S.0 Enumeration, block maps, the geometry check, the benchmark, and the design lock (first; before any statistic)

Read-only on results. Outputs under `reports/tile-join-wave-s/`.

- **Eligibility manifest** (`eligibility.json` and `.md`). Apply § 3.1 to
  the signed register rows, `docs/paper/`, and the Wave 4 claim sources.
  Write one row per claim: the claim text or pointer, family, instrument,
  frame, buffer, joins, estimand, the Wave 3 artefact holding its
  tile-level verdict, and the applicable designs. Families from § 3.1's
  table that are absent are listed, with the reason.
- **Block maps** (`block-maps/<frame>.json`). One per frame named in the
  manifest, for P, S−, S+, Pst (the P map with its sheet strata), and
  (55-map) Sheet, built by `scripts/lib_spatial_blocks.py` (new) with the
  arithmetic consistency check of § 3.2. A frame whose stride does not
  divide 1,344 px, or whose tiles are not axis-parallel, is an uncovered
  decision and stops the wave (§ 7).
- **Geometry and name validation** (`geometry-check.json` and `.md`). For
  every frame in the manifest, the independent check of § 3.2, reading each
  tile's world file and raster size where the rasters are kept: the tracked
  `inputs/tiles_384/` and `inputs/tiles/` for six GS frames, and on zbook
  the untracked `inputs/tiles_256/` and `inputs/tiles_384_55maps/` trees
  for the 256 px and 55-map frames. If a frame's rasters cannot be read, the
  frame stops the wave rather than falling back to the arithmetic check. The
  output lists the clip classes per frame, the clipped tiles whose nominal
  centre lies outside their polygon, and the tiles whose clipped centroid
  would fall in another block.
- **Booking-boundary exposure** (`booking-exposure.md`, descriptive). Per
  frame and design, the number of references within the matching distance
  of a block booking boundary, with the boundaries computed from the
  frame's own polygons as `sheet-primary` uses them (§ 3.3). It reads only
  bounds and reference files.
- **Seam disposition** (55-map). After the PI's ruling, either the
  seam-aware design's specification, its block map, and Astra's review, or
  the recorded choice to qualify the scope (§ 3.8). Required in the lock
  before any 55-map block statistic.
- **Cost: planning arithmetic.** Astra's arithmetic, checked here: the two
  board schedules alone hold 11,628 pairs × 2 statistics × 3 designs on the
  Era-2 board and 595 × 2 × 4 on the 55-map board, that is **74,528
  tests**, and at the fixed budget of 10,000 draws **745,280,000
  permutation draws** (7,452,800,000 at 100,000). The singleton
  reproduction re-runs the boards' tile-level tests once more: 24,446
  tests, or 244,460,000 draws at 10,000. Ladders, per-cell and paired
  intervals, MCB, selection-aware intervals, Pst, and any seam design come
  on top. These are counts, not measured runtime. API calls and paid-model
  fees for this resampling are **zero**; CPU-hours, wall time, and any host
  cost are unknown until measured. Each draw's cost scales with the unit
  count, which blocks reduce (48 against 487 units on the Era-2 frame, 660
  against 8,541 on the 55-map frame, under P).
- **Cost: a fixed synthetic timing benchmark** (`scripts/wave_s_benchmark.py`,
  new; `cost.md`). Synthetic per-tile arrays from `default_rng(42)`, with
  no project data, at the unit counts of each design on the Era-2 and
  55-map frames (singleton 487 and 8,541; P 48 and 660; S− 155 and 2,310;
  S+ 24 and 330; Sheet 55). It times the F1 permutation kernel, the MCC
  permutation kernel, one BCa interval, and `run`, at 1,000 draws, three
  repeats each, on zbook at the worker count its memory allows, and
  projects the totals from the census above. It runs, and `cost.md` is
  committed, **before any real block statistic** (P6). The MCC kernel loops
  in Python over permutations (`pairwise_permutation_test.py:580` onwards),
  so it is expected to dominate.
- **Design lock** (`design-lock.json`). SHA-256 of this specification, the
  manifest, every block map, the geometry check, and the parameter set:
  designs, seeds, the draw budget (fixed only after the benchmark and the
  PI's cost and precision choice), the estimators and their tie tolerance,
  the resolution floor r and its policy, the undefined-MCC union bounds,
  the enumeration rule, the Monte Carlo resolution rule (99 %
  Clopper–Pearson), q, the interval flags, the degeneracy thresholds, and
  `seam_disposition`. Commit it. The driver verifies these hashes before
  every run and refuses on a mismatch.

### S.1 Code and tests (tier 1)

- `scripts/lib_spatial_blocks.py`: block identity, block maps, the
  arithmetic consistency check, the independent geometry check, block
  aggregation of per-tile arrays (per run), stratified and unstratified
  block draws expanded to tile weights, the valid, exact, and legacy
  estimators, and the resolution checks of § 3.6 (c).
- `scripts/wave_s_block_check.py`: the driver; reads the lock, the
  manifest, and the inputs of § 4, runs every design, and writes the
  ledger. It has an explicit `--legacy-reproduction` mode, the only path
  that decides with `c / N`.
- `selection_aware_intervals.run`: a block-map parameter, defaulting to
  singleton blocks, that also carries sheet strata for Pst.
- If the benchmark shows the MCC loop kernel too slow, a vectorised block
  MCC kernel, gated against `permutation_test_mcc_arrays` for identical
  exceedance counts on singleton blocks.
- `tests/test_spatial_blocks.py`, tier 1:
  - block maps: the arithmetic check agrees; one block per tile; no block
    spans sheets; a tile name has one identity in every frame; a clipped
    polygon does not move its tile; the counts of § 3.4 reproduced exactly;
  - **geometry check**: a displaced unclipped footprint, a footprint moved
    by less than a block, a relabelled sheet, a rotated world file, and a
    polygon reaching outside its footprint each fail; a clip keeping two or
    three edges passes;
  - **singleton blocks** reproduce the tile kernels bit for bit in legacy
    mode, **in the instrument's recorded tile order**: F1 and MCC
    permutation, BCa intervals, `run`;
  - **block equivalence**: block aggregation followed by a kernel equals a
    slow reference path that swaps or draws every tile of a block together;
  - **perfect detector** (`docs/agent-guidance.md`, perfect-detector test),
    under each design, single and replicated:
    - the **merged exact-reference fixture** (one point per reference, each
      keeping its own sheet, Wave 1's `sheet_preserving` construction):
      F1, precision, recall, tile-MCC, sensitivity, and specificity are all
      1;
    - the **unmerged per-tile fixture** (one point per reference and
      containing tile): tile classification is perfect (MCC, sensitivity,
      and specificity 1); its symbol counts are the duplicate-sensitive
      ones Wave 1's W1.2 asserts, and block aggregation reproduces their
      sums exactly, without asserting F1 = 1;
    - in a bootstrap of either fixture, undefined MCC resamples are dropped
      and counted, never scored 1 or 0, and the defined ones collapse to
      [1, 1], with the method, fallback reason, and usable count recorded;
    - a pair of identical arms gives d = 0 and p = 1 under the exact, valid,
      and legacy estimators;
  - **estimators**: `(c + 1) / (N + 1)` from a known c; the exact proportion
    under enumeration matches brute force for small d; the complete
    reversal is counted as at least as extreme under the tie tolerance;
    the floor is 1 at d = 0 and a lower bound at d ≥ 1 (a constructed
    contrast whose exact p exceeds 2^(1 − d));
  - **undefined MCC**: Astra's four-unit example gives c_inherited = 4,
    u = 2, c_defined = 2, and union bounds 2/4 and 4/4; a draw with both
    arms undefined counts once in u; no reported bound exceeds 1;
  - **floors**: at d = 14 the exact-group bound is reported as a diagnostic
    and a sampled p-value of 1/(N + 1) is kept as computed, never clamped;
    r follows the frozen policy;
  - **resolution**: the resolution-floor BH check and the Monte Carlo
    resolution check on constructed families, including a test that is
    resolved at rank 1 and one that is not;
  - **antisymmetry**: exchanging the arms leaves the two-sided p unchanged;
  - **stratification**: Pst draws never move a block across sheets, and
    each sheet keeps its block count in every resample;
  - **refusals**: a block map that spans sheets, differs between arms, or
    disagrees with the lock is refused; a real statistic before `cost.md`
    is committed is refused; a 55-map statistic without a seam disposition
    in the lock is refused.
- **Red sentinel**: in a real-file copy of `scripts/` and `tests/`, never
  symlinked, break the sheet restriction; then separately the shared map;
  then **displace one unclipped footprint without changing its name**.
  Confirm the tests turn red for each, and that the copy diffs equal once
  restored (Wave 1 spec, W1.2).

### S.2 Singleton-block reproduction

Run the driver with every tile its own block, **in legacy reproduction mode
and in each instrument's recorded tile order**, on every eligible family.
Every p-value, BH decision, tier, MCB set, and interval must equal Wave 3's
committed value to its recorded precision (GS2). This proves the block
layer changes nothing but the unit. From the same draws, the run also
counts exceedances under the tie tolerance and computes the **valid tile
verdicts** (§ 3.6 (a)), enumerating exactly where d ≤ 13; no further draws
are needed.

### S.3 Block runs

P, S−, S+, Pst, (55-map) Sheet, and the seam design if frozen, over every
eligible family, in one run from the manifest, with a status per claim, at
the fixed budget. No test is re-run with more draws. The run is idempotent:
a second run over the same inputs gives identical outputs.

### S.4 Verdict ledger

`verdicts.json` and `verdicts.md`, per claim and per test:

- the legacy tile verdict, the valid tile verdict, and the valid verdict
  under each design, with the estimator change and the unit change marked;
- c, N, both counts of c (exact and with the tie tolerance), the legacy,
  valid, and exact p-values, d, the exact-group bound, the estimator's
  attainable minimum, the resolution floor r, and, for MCC, u, c_defined,
  c_inherited, and the lower, upper, and inherited p-values, and whether
  the test was enumerated;
- the resolution checks: the coarse floor check, the resolution-floor BH
  check, and the Monte Carlo resolution check;
- for intervals: method, fallback reason, usable resample count, jackknife
  diagnostics, undefined shares, and contributing blocks;
- block contribution: contributing blocks, largest and partial-block
  shares, and the effective number of blocks;
- the category, the rule that produced it, and, on the 55-map frame, the
  seam scope.

A summary table counts the claims in each category, by corpus and family,
and lists separately every estimator change, every Monte Carlo-unresolved
test, and every disclosed conflict.

## 6. Gate GS (all must hold before M3)

1. **The lock held.** Its commit precedes every commit holding a block
   statistic, and every run verified its hashes.
2. **Singleton reproduction** (S.2) exact for every eligible family, in
   legacy mode and recorded tile order.
3. **Tier 1 green** on zbook, including `tests/test_spatial_blocks.py` and
   its perfect-detector and red-sentinel cases; `ruff check` and
   `npx markdownlint-cli2` clean on touched files.
4. **Block maps reproduce § 3.4**, the arithmetic check agrees, the
   independent geometry check passes on every frame, and no block spans
   sheets.
5. **Every eligible claim has a category** with its evidence; no claim is
   missing, and none was added after the lock without being logged (a
   claim found later by Wave 4 is run under the same frozen design and
   logged as late-eligible).
6. **Input invariants** of § 4 hold for every table used.
7. **Idempotent** rerun.
8. **The benchmark preceded** every real block statistic (`git log` order of
   `cost.md`), and the 55-map seam disposition preceded every 55-map block
   statistic.
9. **A fresh-context `/audit`** of the wave S code has run, and each finding
   is resolved or carries a written disposition explaining why it is not
   blocking.

## 7. Running, and what stops it

**Recommended** (§ 11, PI question 2): like Wave 1 (D73 (7)), wave S runs
**unattended from launch to M3, stopping only on a problem**. A problem
stops the wave; the session sends the PI a push notification and writes up
the stop. Problems:

- the failure of any GS item;
- a design-lock hash mismatch, or any change to a design parameter after the
  lock;
- the arithmetic check or the independent geometry check failing, a frame
  whose rasters cannot be read for the geometry check, a tile without
  exactly one block, a block spanning sheets, or a tile-sheet catalogue
  disagreeing with `map_name`;
- a frame whose stride does not divide 1,344 px, or whose tiles are not
  axis-parallel;
- an input table failing an invariant of § 4, or a family whose membership
  differs from Wave 3's;
- a real block statistic requested before `cost.md` is committed, or a
  55-map one before the seam disposition is in the lock;
- a write outside the scratch copy, the wave S branch, or
  `reports/tile-join-wave-s/`;
- a tier-1 failure that is not a pre-existing skip;
- any decision this specification does not cover.

**Never a problem**: any statistical outcome. A claim that is qualified or
withdrawn, a Monte Carlo-unresolved test, or an estimator change is a
result, and the wave runs on. No stop condition may depend on which claims
survive.

Launch discipline as the Wave 1 specification's § 5: all three file
descriptors redirected; nothing after the launch on the same line; setup
separated by `;`; a pid file; watchers on terminal state
(`scripts/wait_for_run.py`) and log staleness, never `pgrep -f`; failure
filters matched case-insensitively (`docs/agent-guidance.md`, "Compute
Location").

## 8. Outputs (committed)

- Code and tests on branch **`tile-join-wave-s`**, with a pull request,
  merged only after the PI approves at M3.
- `reports/tile-join-wave-s/`, every Markdown file following the document
  revision policy (banner and changelog):
  - `eligibility.json`, `eligibility.md`, `block-maps/`,
    `geometry-check.json`, `geometry-check.md`, `booking-exposure.md`, the
    seam disposition, and `design-lock.json` (S.0, committed before any
    statistic);
  - `cost.md` and the benchmark's raw timings (S.0, committed before any
    real block statistic);
  - `singleton-reproduction.json` (S.2);
  - `verdicts.json`, `verdicts.md`, and the run ledger (S.3, S.4).
- The design-evidence scripts and outputs beside this document
  (`planning/tile-join-wave-s-spec-2026-11-18-scripts/`).

## 9. Milestone M3: what the PI receives, and decides

Wave S reports at M3, beside Wave 3's flip report (record § 5). No affected
significance claim is finalised before it has.

The PI receives:

- the GS checklist, with the evidence for each item;
- the verdict summary: claims supported, qualified, and withdrawn, by corpus
  and family, and every qualified or withdrawn claim with its rule and
  numbers;
- the estimator changes, listed apart from the unit changes;
- the Monte Carlo-unresolved tests, and the tests that could not resolve;
- every surprising pattern and disclosed conflict flagged under § 3.6
  (Direction and (e));
- the interval, resolution, contribution, and degeneracy diagnostics;
- the 55-map seam scope as frozen;
- the PR link.

The PI decides:

1. **Accept the categories**, so that Wave 4 restates claims from them.
2. **Wording** for qualified and withdrawn claims, and where the robustness
   sentence goes in the paper.
3. **Estimator changes**: whether those claims stay qualified or are
   withdrawn (§ 11).
4. **Merge** the wave S PR.

## 10. Stated limits

- **Neighbouring blocks still share dependence.** Most tiles of a block lie
  on its edge (62.4 % of Era-2 tiles and 64.2 % of 55-map tiles overlap a
  tile of another block under P), every tile of a complete interior 4 × 4
  block is within two strides of another block, and mound clustering does not stop at a block
  boundary. Blocks reduce the dependence between resampling units; they do
  not remove it, and the sizes are a pragmatic bracket, not a demonstrated
  solution.
- **Adjoining sheets may portray the same ground.** On the 55-map frame,
  33.0 % of tiles overlap a tile of another sheet, at seams where the same
  ground can appear about 170 m apart, and Wave 1 has found reference
  mounds on another sheet's map content at nine seams. No within-sheet
  block, and not the sheet design, makes those units independent; until a
  seam-aware design is frozen, the 55-map scope is qualified (§ 3.8).
- **The GS corpus cannot test sheet-level dependence.** Four sheets give a
  floor of at least 0.125. The occupancy correlogram shows strong
  between-sheet differences on both corpora, so on the GS frames this is a
  real gap, not a formality. Pst conditions on the four sheets rather than
  testing it.
- **The dependence proxy is the reference, not the contrast.** The block
  sizes are related to where mounds are, described by a within-sheet
  cross-product that is not a correlation and by Chebyshev lags that pool
  distances. The dependence that matters is in paired differences between
  conditions, which may be longer or shorter in range.
- **Monte Carlo error is controlled per test, not per family.** The
  resolution check of § 3.6 (c) holds the rest of a BH family fixed; the
  joint Monte Carlo error of a family's rejections is not bounded, and
  "Monte Carlo-resolved" never means that a family's rejections are jointly
  stable.
- **Exchangeability is assumed.** The block permutation test's validity
  rests on exchangeability of arm labels under block swaps (§ 3.8).
- **Inherited choices stay inherited.** Operating points fixed at tile
  level stay fixed, and the intervals describe fixed outputs, not the
  tuning procedure (§ 3.8).
- **A favourable check shows robustness to the specified designs**, not that
  every inferential assumption holds, and a non-rejection is never evidence
  of equivalence.

## 11. Open questions

### For the PI

1. **When to lock.** Approve this specification and commit the design lock
   before Wave 2 produces its first corrected result (recommended), so that
   no corrected result of any kind is known when the block design is fixed?
   Or only before wave S's own statistics (the hard minimum, P3)?
2. **Running mode.** Should wave S run unattended from launch to M3,
   stopping only on a problem, as D73 (7) set for Wave 1 (recommended)?
3. **Scope of "both corpora".** The eligibility rule (§ 3.1) reaches every
   GS frame behind a signed tile-MCC row, including the 512 px, 256 px,
   grid, H10, and H13 frames, not only the Era-2 frame. Is that the
   intended reach of D73 (3) (recommended), or should wave S stop at the
   Era-2 and 55-map frames and qualify the rest?
4. **Per-tile export.** Should Waves 2 and 3 export the per-tile tables of
   § 4, with each test's exceedance count and tile order, as a committed
   cache (recommended), or should wave S rebuild them?
5. **Withdrawal wording.** Is "withdrawn as a significance claim, point
   estimate kept, described as not established under spatial-block
   resampling" the right treatment (§ 3.6 (b))?
6. **Archaeological plausibility.** Does a primary block of about 6.7 km
   match your sense of how barrow groups and map-sheet character vary in
   these landscapes? The reference-occupancy cross-product is visibly
   positive only at Chebyshev lags 1–3 (roughly 2–5 km) within sheets, and
   sheets differ strongly; both are descriptive, not a measured range for
   model contrasts.
7. **Timeline.** Wave S adds a compute stage after Wave 3, whose length
   the synthetic benchmark measures. Is the 2026-11-29 target to absorb it,
   or should claims that wave S has not reached by then be qualified
   pending the check?
8. **Review of the results.** D73 (3) requires review of this specification
   before it runs. Should Astra also spot-check the verdict ledger before
   M3 (recommended for any withdrawn claim)?
9. **Estimator changes (new).** A tile-level claim whose verdict differs
   between Wave 3's `c / N` and the valid `(c + 1) / (N + 1)` is qualified
   and listed (§ 3.6 (b)). Should such claims be withdrawn instead? And
   should Wave 3 itself adopt the valid estimator for the paper's
   tile-level p-values, so that its own verdicts are valid, rather than
   leave that to wave S's diagnostic? § 3.6 (b) is provisional until you
   rule. **Astra's recommendation** (round 2, verbatim): "My recommendation
   is to use the valid estimator for Wave 3's scientific decisions,
   retaining the old estimator only for historical reproduction and a
   clearly labelled before/after ledger. If significance disappears under
   the valid singleton analysis, withdraw the old *significance
   assertion*, while keeping the point estimate and attributing the change
   to the estimator. A category name may remain Qualified for bookkeeping,
   but its prose must not preserve an unsupported positive assertion. Keep
   estimator and spatial-unit effects separate."
10. **Stratification (new).** The sheet-stratified block bootstrap (Pst) is
    a declared sensitivity design for inference conditional on these
    sheets, and the unstratified one stays primary so that only the unit
    changes (recommended). Should Pst be primary instead?
11. **Draw budget (new).** The budget is proposed at 10,000 for every test,
    singleton included (recommended: the valid tile verdicts then come from
    the same draws as the legacy reproduction). At 10,000, a p-value at
    the floor can be rejected on the 11,628-pair board only from BH rank 24;
    100,000 would lower that to rank 3 at ten times the draws
    (7,452,800,000 for the board schedules). Keep 10,000, or raise it for
    every test alike? The budget is locked only after the synthetic
    benchmark has measured the cost, and after this choice.
12. **The 55-map seams (new).** After your seam ruling, should a
    seam-aware sensitivity design be specified, reviewed, and frozen
    (recommended), or should the 55-map scope be qualified instead (§ 3.8)?
    The design would be specified only after the ruling, since the ruling
    may change the references and joins it rests on.

### For Astra

Round 1 settled the eight questions of the first draft (sizes, estimator,
stratification, intervals with few blocks, partial blocks, operating-point
selection, thresholds, and seams); § 13 records each answer and what
changed. The revision is open to a further round if the PI asks for one.

## 12. Freeze items: where each is answered

| Record § 5, wave S row | Here |
|---|---|
| (i) eligible cells, comparisons, families, buffers, frames, joins, estimands; pooled or run-averaged | § 3.1 |
| (ii) block construction in physical coordinates; deterministic shared tile-to-block map | § 3.2; counts § 3.4 |
| (iii) primary and sensitivity sizes, not chosen by significance or interval width; related to overlap, matching distance, dependence | § 3.3 |
| (iv) randomisation and bootstrap units, stratification, shared draws, interval method, seeds, draw counts, selection, multiplicity | § 3.5 |
| (v) too few informative blocks, degenerate MCC, attainable resolution, conflicting sensitivity results; when a claim is qualified or withdrawn | § 3.6 |
| actual block counts and sizes per frame | § 3.4 |
| scope of the inference; seams | § 3.8 |
| stated limits | § 10 |
| aggregate runtime and memory-limited concurrency (Astra, round 2) | S.0: planning arithmetic, then the synthetic benchmark (measured, not estimated here) |

## 13. Gate R-S round 1: Astra's findings and their dispositions

Astra's round-1 review (2026-11-18, at `a588b96f1`; mail and evidence named
in the header) requested changes before launch. Each finding was checked
against the source before it was accepted. Astra's counterexamples and
planning arithmetic were recomputed independently (standard-library
arithmetic) and agree with `wave-s-design-probe.json`: 11,628 pairs; a
first-rank BH threshold of 4.30 × 10⁻⁶; floors of 1/10,001 and 1/100,001;
twelve tiles at one stride and four at two in a 4 × 4 block; a booking
boundary at 1,368 px; 74,528 tests. The S2 cancellation was confirmed in
`block_census.py` (the first draft's `block_by_metres`), and the S3
statistic at `occupancy_correlogram.py:140` in the first draft. Every
finding holds; none is disputed.

| Finding | Disposition | Sections changed |
|---|---|---|
| **S1** Valid permutation p-values for decisions | **Accepted.** Decisions use `(c + 1)/(N + 1)` for sampled swaps and the exact proportion under full enumeration (d ≤ 13 at N = 10,000); `c / N` survives only in an explicit legacy reproduction mode. Singleton and block verdicts are both computed with the valid estimator from the same draws, so the ledger separates the estimator change from the unit change. The disagreement-triggered rerun is removed in favour of a fixed, predeclared budget; a test the budget cannot settle is recorded as Monte Carlo-unresolved, not forced. The false claim that 48 blocks resolve every BH threshold is withdrawn; finite swap-group resolution, Monte Carlo resolution, and power are kept apart, and resolution is judged against BH. d = 0 gives p = 1; 2^(1 − d) is stated as a lower bound. Ties are handled with a frozen tolerance so the reversal counts | § 0; § 2 (table, consequences 2–3); § 3.3; § 3.5 (exact enumeration, draw budget, ties, multiplicity); § 3.6 (a), (b), (c), (f); § 3.7; S.1–S.4; § 9; § 10; § 11 (PI 9, 11) |
| **S2** Make the geometry check independent | **Accepted.** The metres route cancels to the name route; it is relabelled as an arithmetic consistency check. A genuinely independent check now reads each tile's nominal footprint from its own world file and PNG size, checks the name against the raster (one sheet origin per sheet), the bounds geometry against the footprint with clipping treated explicitly (equal, or inside and keeping at least two edges; never a clipped centroid for membership), and the block by three routes. Tracked rasters cover six GS frames, all of which pass; the 256 px and 55-map rasters are untracked, so S.0 runs the check where they are kept and stops if it cannot. The red sentinel displaces one unclipped footprint (by a stride and by 10 m) with its name unchanged, and relabels a sheet; each turns the check red, while the arithmetic check passes the displacement. `block_census.py` was changed and re-run; its block counts are unchanged | § 3.2 (sheet restriction, orientation, clipping, the checks); § 3.4; S.0 (geometry and name validation); S.1 (tests, red sentinel); § 6 (4); § 7; § 8; `block_census.py` and `.txt` |
| **S3** Correct the block-size rationale | **Accepted.** The claim that most tiles of a 4 × 4 block lie farther from other blocks than the dependence reaches is withdrawn (twelve are one stride and four two strides from another block). The matching-distance exposure is derived from the regions `sheet-primary` booking induces (boundaries at k × 1,344 px plus half the overlap), as geometry on the regular grid, not a measured rate, with S.0 counting exposure from the frames' own polygons. The correlogram's within-sheet column is relabelled as a mean-centred cross-product normalised by the whole-frame within-sheet variance, and its lag as Chebyshev, pooling axial and diagonal pairs; the script header and output labels now say so, and the reference occupancy is kept as descriptive design evidence only. The sizes are kept as a frozen, pragmatic bracket, not a solution to dependence. The first draft's "0.05–0.07 at lags 2–3" also misquoted its own table (55-map lag 3 is 0.024); corrected to 0.024–0.072 | § 3.3 (whole subsection); § 3.4; § 10; § 11 (PI 6); `occupancy_correlogram.py` and `.txt` |
| **S4** Unresolved sensitivity checks are not support | **Accepted.** Supported now requires every applicable sensitivity design to agree, resolved, Monte Carlo-resolved, and reliable; any applicable design that cannot resolve or is unreliable qualifies the claim, with the resolved checks reported separately. Resolution limits are reported against the actual BH procedure (the resolution-floor BH check; corrected in round 2, S7), with the absolute floor kept as a coarse check. Intervals report method, fallback reason, usable resample count, and jackknife diagnostics; a numerical fallback never yields an unqualified supporting interval; 20 blocks and 1 % are reporting flags, not coverage guarantees. A newly significant block result stays a disclosed conflict, not a new claim | § 3.5 (interval method and reporting); § 3.6 (b), (c), (d); S.4; § 9 |
| **S5** Repair the permanent sentinel's estimand | **Accepted.** The merged exact-reference fixture must give F1 = MCC = 1 (and precision, recall, sensitivity, specificity); the unmerged per-tile fixture must give perfect tile classification and keeps its duplicate-sensitive symbol counts, as Wave 1's W1.2 already distinguishes. Undefined MCC resamples are dropped and counted, never scored 1 or 0; in a permutation null the inherited 0.0 convention is kept for comparability with Wave 3, but the draws with an undefined arm are counted and union bounds reported (corrected in round 2, S6). The legacy singleton sentinel keeps each instrument's recorded tile order | § 2 (consequence 2); § 3.2 (deterministic order); § 3.6 (d); S.1 (perfect detector); S.2; § 6 (2) |
| Answers: stratification | **Accepted.** A sheet-stratified block bootstrap (Pst) is a declared sensitivity design, with its inferential target (conditional on these sheets) stated beside the unstratified primary's; neither is evidence about new sheets; the block swap's own exchangeability argument is stated. Whether Pst should be primary is put to the PI | § 3.3; § 3.5 (stratification); § 3.6 (a), (e); § 3.8; § 11 (PI 10) |
| Answers: BCa versus percentile | **Accepted.** No automatic switch for few blocks; the inherited degeneracy fallback is kept but recorded with its reason and flags the interval; the method actually used and its diagnostics are reported | § 3.5 (interval method); § 3.6 (c) |
| Answers: partial blocks | **Accepted.** Deterministic identities kept; block sizes and count-contribution imbalance (largest and partial shares, effective number of blocks) reported; counts are summed for pooled estimands, never averaged block metrics | § 3.1 (estimands); § 3.2 (partial blocks); § 3.5; S.4 |
| Answers: operating-point selection | **Accepted.** Scope stated: intervals and tests describe fixed realised outputs, not the tuning procedure; selection replay kept wherever the inherited instrument performs it | § 3.5 (selection); § 3.8; § 10 |
| Answers: seams | **Accepted.** The 55-map scope is explicitly qualified until the seam ruling; after it, a seam-aware sensitivity design is frozen in the lock before any 55-map block statistic, or the scope stays qualified on every 55-map claim. Context added from the Wave 1 stop report | § 0; § 1 (P7); § 3.3; § 3.4; § 3.6 (b); § 3.8; S.0; § 6 (8); § 7; § 10; § 11 (PI 12) |
| Bookkeeping: Decision 10 attribution | **Accepted.** "Registered resampling unit" and "registered tile interval" replaced: the tile unit was pre-specified in Decision 10 (`decisions-log.md:345`) before lodgement; the registration asks for bootstrapped intervals and names no unit (`osf/preregistration.md:293`; E54 as corrected 2026-07-28); the tile-swap tests come from D42 | § 3.6 (b); § 3.7 |
| Cost: planning arithmetic and benchmark | **Accepted.** Astra's 74,528 tests and 745,280,000 draws (7,452,800,000 at 100,000) checked and recorded, with the singleton reproduction's 24,446 tests and 244,460,000 draws added; zero API calls and paid fees; runtime unmeasured. A fixed synthetic timing benchmark runs and is committed before any real block statistic | § 1 (P6); S.0 (cost); S.1 (refusals); § 6 (8); § 7; § 8 |

**Reply.** No finding is disputed. Two points went slightly beyond the
review: a bound for undefined MCC null draws (§ 3.6 (d)), and the misquoted
lag-3 range noted in the S3 row, which the review did not raise. The first
was added in round 1 on a wrong premise, that scoring an undefined MCC as
0.0 can only make a permutation p-value smaller. There is no defined MCC to
compare the 0.0 with, and zero imputation can itself make the difference
between the arms extreme; the round-1 formula also double-counted draws.
Round 2's S6 replaced both the premise and the formula with union bounds.

### Round 2

Astra's round-2 review (2026-11-18, at `0a1b4dadd`; mail and evidence named
in the header) accepted the round-1 answers and requested two arithmetic
corrections before the design lock, plus a recommendation to the PI. Both
corrections were verified first by an independent standard-library
enumeration of Astra's synthetic example, which agrees with
`wave-s-round2-probe.json`: c = 4, u = 2, c_defined = 2 over M = 4
patterns, so the round-1 formula gives 1.4 and the union upper bound 1.0;
at d = 14, 2^(1 − 14) = 1/8,192 exceeds 1/10,001, and (1 − 1/8,192)^10,000
≈ 0.295. Astra's BH example (0.051 and 0.052 at q = 0.05) was checked by
hand.

| Finding | Disposition | Sections changed |
|---|---|---|
| **S6** The undefined-MCC bound double-counts draws | **Accepted.** `(c + u + 1)/(N + 1)` replaced by union bounds: a draw with either arm undefined is counted once in u; upper count c_defined + u, giving `(c_defined + u + 1)/(N + 1)` sampled and `(c_defined + u)/M` enumerated; lower count c_defined. The inherited-convention estimate is kept separately, and BH uses it; the unreliable flag compares the BH verdicts at the two bounds. § 13's false premise corrected | § 2 (MCC kernel row); § 3.6 (d); S.0 (lock); S.1 (tests); S.4; § 13 (Reply, S5 row) |
| **S7** An exact-group floor is not the sampled estimator's floor | **Accepted.** The exact-group bound 2^(1 − d) is a diagnostic only; the sampled estimator's own minimum is 1/(N + 1), and the exact attainable minimum applies under enumeration. The category is controlled by one frozen resolution floor r: the exact attainable minimum when enumerated, and max(1/(N + 1), 2^(1 − d)) when sampled, declared as a conservative policy for interpreting a non-rejection, used only in the counterfactual BH check. The valid sampled p-value is never clamped. Astra's d = 14 example recorded | § 3.6 (c); S.0 (lock); S.1 (tests); S.4; § 13 (S4 row) |
| Estimator changes and claim wording (recommendation to the PI) | **Referred to the PI, not ruled on.** Astra's recommendation added verbatim under § 11, question 9. § 3.6 (b) and its "Estimator changes" paragraph marked PROVISIONAL, so that nothing reads as settled that such a claim "stands"; the Qualified placement is bookkeeping only | § 3.6 (b); § 11 (PI 9) |
| Monte Carlo resolution (accepted with the stated limit) | **Accepted.** "Monte Carlo-resolved" defined as a per-test check only, never joint stability of the BH family, with Astra's two-p-value example; precision, validity, and exchangeability stated as separate questions. Lock order recorded: the draw budget is fixed after the synthetic benchmark and the PI's cost and precision choice, never raised selectively | § 3.5 (draw budget); § 3.6 (c); § 10; § 11 (PI 11); S.0 (lock) |

## Changelog

### 2026-11-19 — Revised after Astra's round 2 (S169, amd-tower)

Trigger: Astra's round-2 review of `0a1b4dadd`
(`~/agent-mail/codex/outbox/claude/20261118T133113Z-astra-wave-s-round2-review.md`):
two arithmetic corrections before the design lock (S6, S7), a
recommendation to the PI on estimator changes, and a wording limit on
Monte Carlo resolution. Both corrections were verified against Astra's
synthetic example before being applied; § 13, "Round 2", records the
dispositions. The branch was first fast-forwarded to `main` at
`7d6e1e881`. Status: draft, revised after Astra's rounds 1 and 2; not
approved by the PI.

| Item | Before | After |
|---|---|---|
| Undefined-MCC bound | `(c + u + 1)/(N + 1)` (double-counts; can exceed 1) | union bounds: lower `(c_defined + 1)/(N + 1)`, upper `(c_defined + u + 1)/(N + 1)`; `/M` forms under enumeration; inherited estimate kept separately |
| Resolution floor | "attainable floor", max(2^(1 − d), 1/(N + 1)) for a sampled test, read as the test's floor | exact-group bound a diagnostic; sampled minimum 1/(N + 1); one frozen resolution floor r controls the category, declared a conservative policy; p-values never clamped |
| Estimator-change wording | "the claim stands with the qualification stated" | PROVISIONAL pending the PI's ruling; Astra's recommendation recorded verbatim in § 11, question 9 |
| "Monte Carlo-resolved" | per-test check, with a stated family limit | the same, defined explicitly as never meaning joint stability of a BH family |
| Draw budget | fixed at 10,000 | proposed 10,000; locked only after the benchmark and the PI's cost and precision choice |

What did not change: the designs, block rule, block counts, correlogram
values, seeds, eligibility, and the design scripts. Commit: the one adding
this entry.

### 2026-11-18 — Revised after Astra's round 1 (S169, amd-tower)

Trigger: Astra's round-1 review of the first draft at `a588b96f1`
("changes requested before launch";
`~/agent-mail/codex/outbox/claude/20261118T124335Z-astra-wave-s-spec-review.md`).
Every finding (S1–S5, the five design answers, bookkeeping, and cost) was
verified against the source and accepted; § 13 records each disposition.
The branch was fast-forwarded to `main` at `92064b134` first. Status:
draft, revised after Astra's round 1; not approved by the PI.

| Item | Before | After |
|---|---|---|
| Decision estimator | `c / N`, with `(c + 1)/(N + 1)` reported beside it | `(c + 1)/(N + 1)` sampled, exact proportion enumerated (d ≤ 13); `c / N` in legacy reproduction only |
| Tile verdict used for categories | Wave 3's committed (`c / N`) | the valid singleton verdict; the estimator change listed separately |
| Draw budget | 10,000, re-run at 100,000 when the estimators disagree | 10,000 fixed for every test; Monte Carlo-unresolved recorded, never re-run |
| Resolution | p_floor = 2^(1 − d) > 0.05 | d = 0 → p = 1; 2^(1 − d) a lower bound; checked against BH with the attainable floor; Monte Carlo resolution separate |
| Second block route | "two routes, one answer" | an arithmetic consistency check, plus an independent geometry check from tracked world files (six GS frames pass; 256 px and 55-map run in S.0) |
| Booking-boundary exposure | "about fourfold" from the block-square edge | derived from `sheet-primary`'s booking regions (boundary at 1,368 px for 384/336); no measured rate claimed |
| Correlogram, within-sheet column | "correlation" | within-sheet cross-product (not a correlation), Chebyshev lags |
| Designs | P, S−, S+, Sheet | adds Pst (sheet-stratified bootstrap) and a seam design after the seam ruling |
| Supported | P and every sensitivity design that can resolve agree | every applicable design agrees, resolved and reliable; anything unresolved qualifies |
| Perfect-detector sentinel | F1 and MCC 1 for merged and unmerged | merged: all 1; unmerged: tile classification 1, duplicate-sensitive symbol counts kept |
| Preconditions | P1–P5 | adds P6 (benchmark first) and P7 (55-map seam disposition) |
| Gate GS | eight items | nine (benchmark and seam ordering) |
| Open questions | PI 1–8, Astra 1–8 | PI 1–12 (9–12 new); Astra's settled, § 13 |

What did not change: the eligibility rule, the families, the block rule and
sides, every block count in § 3.4, every correlogram value, the seeds, and
the 10,000 draws per test. The design scripts were changed: `block_census.py`
(route relabelled; geometry check and red sentinel added; output re-run, its
block counts unchanged) and `occupancy_correlogram.py` (header and output
labels; values unchanged). Commit: the one adding this entry.

### 2026-11-18 — Original publication

Drafted for S169 on amd-tower, in the worktree branch `wave-s-spec` from
`fe9d433d7`, as the specification the record's § 5 requires before wave S
runs. It answers the five freeze items of Astra's round-2 review, and adds
two standard-library design scripts with their outputs
(`planning/tile-join-wave-s-spec-2026-11-18-scripts/`: `block_census.py`
and `occupancy_correlogram.py`), which read only bounds and reference
files. Status: draft for Astra's review; not approved. No block statistic
has been computed.
