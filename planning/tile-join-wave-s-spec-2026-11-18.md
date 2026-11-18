# Tile-join wave S — specification (spatial-block resampling check)

> **Last revised**: 2026-11-18 (original draft, for Astra's review). See
> [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), drafting for session S169 on amd-tower, in the
  worktree `~/worktrees/map-reader-llm/claude-wave-s-spec` (branch
  `wave-s-spec`). Every path, line number, and count below was read from the
  files named beside it, on `main` at `fe9d433d7`. The block counts and the
  occupancy correlogram were computed for this document by two
  standard-library scripts that read only bounds and reference files
  (§ 3.4, § 3.3; D70: amd-tower's environment is not the reference one).
  No block statistic, permutation, or bootstrap has been run by anyone.
- **Parent**: `planning/tile-join-resolution-2026-11-01.md` (the decision
  record; this document specifies the wave S row of its § 5). Rulings: D72
  and D73 in `planning/pi-decisions-2026-09-20.md`, in particular D73 (3).
  Sibling: `planning/tile-join-wave-1-spec-2026-11-01.md` (the joins this
  wave inherits).
- **Status**: **DRAFT, for Astra's review; not approved.** Nothing in it is
  a ruling. Where the record does not settle a choice, the document
  recommends one and lists it in § 11.
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
counts as the tile-level analysis that Wave 3 regenerates. Only the unit
changes. A claim that holds under the primary block size and every
sensitivity design is reported as robust to the specified design. A claim
that holds only under some is qualified, and a claim that fails under the
primary design, with enough blocks to decide, is withdrawn as a
significance claim (§ 3.6). This document fixes all of that before any
block result exists.

## 1. Preconditions (launch is blocked until all hold)

| # | Precondition | How it is checked |
|---|---|---|
| P1 | Astra has reviewed this specification, the PI has ruled on the review, and the document is revised accordingly | review delivered by agent mail or a committed file; § Changelog |
| P2 | The PI approves this specification for launch | stated in conversation; recorded in § Changelog |
| P3 | **The design lock is committed** (S.0): block maps, eligibility manifest, and parameters, with their SHA-256 hashes, in a commit that precedes every commit holding a wave S statistic | `git log` order; the driver refuses to run if the lock's hashes do not match the files (§ 5) |
| P4 | Wave 3 has passed G3: the tile-level families, tierings, MCB sets, and intervals are regenerated under the new joins and committed | the record's § 5, Wave 3 row; Wave 3's flip report exists |
| P5 | zbook's `.venv` matches the reference environment, and its checkout is clean and 0 behind `origin/main` | as Wave 1 spec § 1, P3 and P4 |

**Recommended, not required** (§ 11, PI question 1): approve this
specification and commit the design lock **before Wave 2 produces its
first corrected result**, so that even the corrected tile-level results are
unseen when the block design is frozen. The hard requirement (P3) is only
that the lock precede every block statistic.

## 2. What wave S inherits

Wave S adds a unit, not a method. Each piece below is reused unchanged, run
on block-aggregated arrays instead of tile arrays (§ 3.5). Line numbers are
at `fe9d433d7`.

| Piece | Where | What wave S keeps |
|---|---|---|
| Paired tile-swap permutation, F1, precision, recall | `scripts/lib_permutation.py:241` (`paired_permutation_test`); swap masks `:199`; constants `N_PERMUTATIONS = 10_000`, `SEED = 42` at `:68–69`; p-value `mean(\|null\| >= \|observed\|)` at `:306`, which may be exactly 0 (module docstring, D42 default (d)) | the kernel, the shared mask for all three metrics, the run-block swap for multi-run arms (`_as_runs`, `:147`) |
| The boards' F1 kernel | `scripts/n1_baseline_leaderboard_tiering.py:312` (`permutation_test_float`); `FDR_Q = 0.05` at `:101`; `greedy_clique_tiers` at `:391` | the kernel, BH at q = 0.05, the greedy-clique tiers |
| The MCC permutation kernel | `scripts/pairwise_permutation_test.py:580` (`permutation_test_mcc_arrays`): one `default_rng(seed)` mask per permutation, so F1 and MCC see byte-identical masks for one seed, unit count, and order; a degenerate permuted MCC is scored 0.0 inside the null only (`_compute_mcc`, `:514`), never published (E81; `compute_mcc_or_none`, `:547`) | the kernel and both conventions |
| Board harness | `scripts/era1_leaderboard_tiering.py`: per-tile loaders `cell_per_tile` (`:334`) and `cell_per_tile_classification` (`:494`); F1 pairs `:1309`, BH `:1317`, MCC pairs `:1347`, BH `:1353`, tiers `:1373`; `--permute-mcc` shares the swap masks (header, lines 64–76) | the loaders (with the explicit Wave 1 joins), the round-robin families |
| 55-map MCC tiering | `scripts/mcc_tiering_55map.py`: `N_PERMUTATIONS`, `SEED` at `:92–93`; round robin and BH at `:521–523` | the family and the instrument |
| Per-cell intervals | `scripts/lib_advanced_metrics.py:3489` (`bootstrap_ci`, F1, precision, recall) and `:5107` (`bootstrap_tile_classification_ci`, MCC, sensitivity, specificity, dropping undefined resamples per E81); BCa through `scipy.stats.bootstrap` with a percentile fallback (`_bca_ci_from_indices`, `:547`; `BOOTSTRAP_METHOD = "BCa"`, `:73`) | the estimator, the fallback, and E81's handling |
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
   wave S's code must reproduce Wave 3's committed tile-level p-values,
   intervals, tiers, and admissible sets exactly (gate GS2, § 6).
3. **One inherited convention needs a decision.** The D42 p-value can be
   exactly 0. That matters more with blocks, where the exact null has at
   most 2^d sign patterns over d informative blocks (§ 3.6 (c); § 11, Astra
   question 2).

## 3. The frozen design

Each subsection answers one of the five freeze items in the record's § 5
wave S row; § 12 maps them back.

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
value enters wave S.

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
block sums.

### 3.2 Freeze item (ii): block construction and the tile-to-block map

**Blocks are squares on the ground, laid on each sheet's own raster grid.**

- **Sheet restriction.** A block never spans two sheets. A tile's sheet is
  the one the scorer's tile-sheet catalogue gives it (`frame_tile_sheets`,
  `lib_advanced_metrics.py:1497`), the same catalogue the sheet joins and
  symbol matching use (Wave 1 spec, W1.1). It is cross-checked against the
  bounds file's `map_name`; any disagreement stops the wave (§ 7).
- **Origin.** The north-west corner of the sheet's pixel (0, 0), located in
  EPSG:32635 (UTM zone 35N) metres.
- **Orientation.** Along the sheet raster's columns and rows, which are UTM
  easting and southing. Every tile polygon in all eight frames is an
  axis-parallel rectangle in EPSG:32635 (`block_census.txt`, "every polygon
  axis-parallel: True").
- **Side.** A whole number of sheet pixels: 1,344 px for the primary design,
  672 px and 2,016 px for the sensitivity designs (§ 3.3). On the ground a
  sheet pixel measures 4.9952–5.0640 m on the 55-map frame and
  5.0100–5.0315 m on the GS frames, so 1,344 px is 6.71–6.81 km.
- **Membership.** A tile belongs to the block containing the **centre of its
  nominal pixel window**, `(x + T/2, y + T/2)`, where `x` and `y` are the
  pixel offsets in its name and `T` its tile size. Block column and row are
  `floor((x + T/2) / side)` and `floor((y + T/2) / side)`, with half-open
  intervals. A clipped frame polygon (the grid frame has tiles whose west
  edge is clipped by about 560 m) therefore does not move its tile. Because
  1,344 px is the least common multiple of the three strides in use (224,
  336, and 448 px), every primary block is a whole group of tiles: 6 × 6 at
  256 px, 4 × 4 at 384 px, and 3 × 3 at 512 px.
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
  the pure-function property. Their sizes are reported (§ 3.4).
- **Holes.** Tiles missing from a frame leave smaller blocks or none. A
  block with no tile in the frame does not exist in that frame. Holes are
  not filled and blocks are not merged across them.
- **Two routes, one answer.** The implementation computes membership twice:
  once from the tile's nominal centre in metres through the sheet's origin
  and pixel size, and once from the pixel offsets in its name. The census
  script does exactly this; the two routes agree on every tile of every
  frame, for every candidate side (`block_census.txt`, "routes disagree on
  0 tiles"). In the wave, any disagreement stops it (§ 7).
- **Deterministic order.** Blocks enter every kernel sorted by block
  identity. Tile order inside a block is irrelevant, because only sums enter
  a kernel.
- **Sheet blocks** (55-map only): the block is the sheet; the identity is
  `<sheet>|sheet`.

The maps are written to `reports/tile-join-wave-s/block-maps/<frame>.json`
(tile name to block identity, for each design) and hashed into the design
lock (S.0).

### 3.3 Freeze item (iii): primary and sensitivity sizes, and why

| Design | Side | Role |
|---|---|---|
| **P** | **1,344 px (6.71–6.81 km)** | primary |
| S− | 672 px (3.36–3.40 km) | sensitivity, smaller |
| S+ | 2,016 px (10.07–10.21 km) | sensitivity, larger |
| Sheet | the sheet (about 22 × 20 km) | sensitivity, 55-map only |

These sizes were chosen from the geometry, the matching distances, and where
the reference mounds lie. No significance or interval width was consulted,
and none exists yet: no block statistic has been computed, and the corrected
tile-level results of Waves 2 and 3 do not exist at the time of writing.

**Tile overlap.** At 384 px, neighbouring tiles share a 48 px strip (about
240 m), one eighth of a tile; the 512 px and 256 px tilings overlap by 64
and 32 px, also one eighth (`block_census.txt`). Within a block, overlap
does not matter. Across a block boundary, two tiles share at most that
strip, which is 48 / 1,344 ≈ 3.6 % of a primary block's width. A mound in
that strip can count in two blocks, but no wider ground can.

**Matching distance.** 20 m on the GS frames and 50 m on the 55-map frame,
about 4 and 10 sheet pixels. Astra's R3 mechanism (a matched target booked
at its detection's tile in one condition and at its reference's tile in
another) can move an outcome between blocks only when a block boundary
passes between the two points. For primary blocks that requires the target
to lie within 10 px of a 1,344 px boundary, against within 10 px of a
336 px stride for tiles, so blocks reduce the exposure about fourfold
without removing it.

**Plausible spatial dependence.** The dependence that matters is in the
paired difference between two conditions' per-tile outcomes, and that cannot
be measured before the design is frozen. The nearest observable proxy is
where the reference mounds lie. `occupancy_correlogram.txt` reports the
correlation of reference occupancy between tiles of the same sheet, by lag
in strides (one stride, 336 px, is about 1.7 km):

| Lag (strides) | Era-2, pooled | Era-2, within sheet | 55-map, pooled | 55-map, within sheet |
|---:|---:|---:|---:|---:|
| 1 (tiles overlap) | 0.361 | 0.188 | 0.251 | 0.165 |
| 2 | 0.262 | 0.048 | 0.155 | 0.057 |
| 3 | 0.273 | 0.072 | 0.124 | 0.024 |
| 4 | 0.216 | 0.012 | 0.107 | 0.005 |
| 6 | 0.140 | −0.057 | 0.079 | −0.023 |
| 8 | 0.102 | −0.052 | 0.053 | −0.047 |

Two kinds of dependence show:

- **Short-range, within a sheet.** Once each sheet's mean is removed, the
  correlation falls from about 0.17–0.19 at lag 1, where tiles share
  ground, to 0.05–0.07 at lags 2–3 and about 0.01 at lag 4. Mound clustering
  therefore reaches about one to three strides (roughly 2–5 km). A 4-stride
  block is wider than that range, so most of its tiles are further from any
  other block's tiles than the dependence reaches.
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
about 130 times the 55-map matching distance. It is wider than the
within-sheet dependence range the correlogram shows. And it leaves 48 blocks
on every GS frame and 660 on the 55-map frame, enough for bootstrap
intervals and for permutation p-values far below any BH threshold the
families need (§ 3.6). The block count is a validity constraint on the
resampling, not the reason for the size: 1,008 px (74 GS blocks) would give
more blocks but does not group whole tiles at 512 px or 256 px, and 2,688 px,
the next whole-tile side, leaves 16 GS blocks, too few for intervals. D73 (3)
anticipated "roughly 30 to 50 blocks on the 487-tile frame"; the primary
design gives 48.

**Why the sensitivity sizes.** S− halves the side: 2 × 2 tiles at 384 px,
the smallest block with more than one tile in each direction. It sits at the
edge of the short-range dependence (within-sheet occupancy correlation
0.048–0.057 at its 2-stride spacing), so it brackets that dependence from
below. S+ is half as large again: of the candidate sides in
`block_census.txt`, the largest that keeps at least 20 blocks on every GS
frame (24). The sheet design probes the sheet-level dependence that no
within-sheet block can. The sizes are a bracket around the primary, not a
search for the best: no claim may rest on whichever design favours it
(§ 3.6).

On the 512 px frames, S− (1.5 strides) and S+ (4.5 strides) do not group
whole tiles. Membership is still deterministic by the centre rule, but the
blocks are uneven; § 3.4 reports them.

### 3.4 Block counts and sizes per frame (design information)

Computed by
`planning/tile-join-wave-s-spec-2026-11-18-scripts/block_census.py`
(output `block_census.txt`), which reads only the bounds files. "Overlap
another block" counts tiles whose footprint overlaps, with positive area, a
tile assigned to a different block, in the same sheet or in another sheet.

| Frame | Tiles (sheets; tile/stride px) | S− 672 px: blocks (tiles per block min/median/max) | **P 1,344 px**: blocks (min/median/max; under 4 tiles) | S+ 2,016 px: blocks (min/median/max) | Sheet blocks |
|---|---|---|---|---|---|
| `inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson` | 487 (4; 384/336) | 155 (1/4/4) | **48 (1/12/16; 1)**, 12 per sheet | 24 (3/21/36) | 4, not used |
| `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` | 487 (4; 384/336) | 155 (1/4/4) | **48 (1/12/16; 1)** | 24 (3/21/36) | 4, not used |
| `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson` | 487 (4; 384/336) | 155 (1/4/4) | **48 (1/12/16; 1)** | 24 (3/21/36) | 4, not used |
| `inputs/vectors/bounds/384/h10_test_bounds.geojson` | 327 (4; 384/336) | 148 (1/2/4) | **48 (1/8/15; 14)** | 24 (2/14.5/27) | 4, not used |
| `inputs/vectors/bounds/full_evaluation_bounds.geojson` | 340 (4; 512/448) | 165 (1/2/4) | **48 (3/8.5/9; 12)** | 24 (4/15.5/25) | 4, not used |
| `outputs/h13/scoring/bounds/h13_common_bounds.geojson` | 340 (4; 512/448) | 165 (1/2/4) | **48 (3/8.5/9; 12)** | 24 (4/15.5/25) | 4, not used |
| `inputs/vectors/bounds/256/full_evaluation_bounds.geojson` | 1,032 (4; 256/224) | 152 (1/8/9) | **48 (1/25.5/36; 2)** | 24 (4/50.5/81) | 4, not used |
| `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` | 8,541 (55; 384/336) | 2,310 (1/4/4) | **660 (3/16/16; 3)**, 12 per sheet | 330 (5/36/36) | **55** (143/156/156) |

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
apart (record § 2.4); no within-sheet block, and not even the sheet design,
removes that dependence (§ 10).

These numbers become a regression check: wave S's own block maps must
reproduce this table exactly (gate GS4).

### 3.5 Freeze item (iv): units, draws, intervals, seeds, selection, and multiplicity

**Permutation unit.** The block. Under the null hypothesis, within each
block the two arms' labels are exchangeable. Each permutation swaps a whole
block's counts between arms with probability 0.5, and for multi-run arms
the block's whole run stack swaps together. Implementation: sum each arm's
per-tile arrays within blocks (per run where there are runs), then call the
unchanged kernel (§ 2) on the block arrays.

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

**Stratification.** None in the primary analysis. The tile-level bootstrap
and permutation are unstratified, so the block analysis is too: only the
unit changes. Sheet-stratified resampling is not run (§ 11, Astra question
3). On the 55-map corpus, sheet blocks probe the sheet level directly.

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

**Draw counts.** 10,000 permutations per test and 10,000 bootstrap
resamples per interval or MCB family, as at tile level. One extension,
applied mechanically: a test whose verdict would change between the two
p-value estimators of § 3.6 (c) is re-run at 100,000 permutations, same
seed, whatever its direction.

**Interval method.** Each instrument's own: BCa with the percentile
fallback for per-cell and paired intervals; percentiles and the bootstrap
critical values of both MCB forms for MCB and selection-aware intervals.
Degenerate MCC resamples are dropped, as E81 requires, and counted.

**Selection.** Where the tile-level instrument repeats a selection inside
each resample (the argmax in MCB and selection-aware intervals), the block
analysis repeats it inside each block resample. Where the tile-level
instrument treats a choice as fixed (the operating point of an `oracle`,
`opmax`, or `carried` cell in a pairwise test), wave S treats it as fixed
too. Wave S adds no selection correction and removes none (§ 10; § 11, Astra
question 6).

**Multiplicity.** Benjamini–Hochberg (BH) at q = 0.05 within each family,
exactly as Wave 3 constitutes it (same members, the D73 (4) cells
included), applied to the block p-values. Tiers are rebuilt by the same
greedy clique from the block verdicts. The four designs (P, S−, S+, Sheet)
are not extra hypotheses, so there is no correction across them: no design
is chosen for its result, and the decision rule requires agreement rather
than taking the best (§ 3.6).

### 3.6 Freeze item (v): decision rules

These rules are fixed before any claim's block result is known, and apply to
every eligible claim alike.

**(a) The verdict a claim carries.** Each eligible claim has a *tile-level
verdict* from Wave 3 (significant or not after BH; in a tier or not; in an
admissible set or not; an interval that excludes a value or not). Wave S
computes the same verdict under each applicable design: P, S−, S+, and, on
the 55-map frame, Sheet.

**(b) Categories.**

| Category | When | What the paper says |
|---|---|---|
| **Supported** | the verdict under P equals the tile-level verdict, and so does every applicable sensitivity design that can resolve it | the claim stands, with a sentence that it is robust to the specified block design |
| **Qualified** | the verdict under P equals the tile-level verdict, but a resolvable sensitivity design disagrees; **or** P cannot resolve it (rule (c)); **or** a P interval or test is flagged unreliable (rule (d)) | the claim stands with the qualification stated, naming the design that disagrees or cannot resolve it |
| **Withdrawn** (as a significance claim) | the verdict under P differs from the tile-level verdict, and P can resolve it | the significance, tier, or admissibility claim is withdrawn; the point estimate stays, described as a difference not established under spatial-block resampling |

**Direction.** The categories apply to a significant tile-level verdict that
loses significance. A non-significant tile-level verdict that becomes
significant under blocks is not turned into a new positive claim: wave S
creates no claims. It is reported as a surprising conflict (the project's
research-finding calibration) and the original claim is **qualified**.

Tier and set claims are judged member by member. A claim that X is in the
top tier, or cannot be ruled out as best, is supported if X's membership
holds under P, and so on through the table. A claim about the whole
partition ("the board has N tiers") is qualified whenever the partition
changes under P.

An interval that a claim quotes but does not reason from (for example
"F1 0.90, 95 % CI …") is not categorised. The block interval is reported
beside it, and the registered tile interval stays the reported one
(Decision 10's unit).

**(c) Too few informative blocks, and attainable resolution.**

- An **informative block** for a paired test is one where the two arms'
  block sums differ in any input to the statistic. Let d be their number.
  Swapping all d blocks negates the observed difference, so the exact
  two-sided permutation p-value can be no smaller than p_floor = 2^(1 − d).
  If p_floor > 0.05 (d ≤ 5), the test **cannot resolve** a significant
  verdict at any BH rank. A tile-level significant claim in that position is
  **qualified**, not withdrawn, because the design lacks the resolution to
  confirm or refute it. Every test reports d and p_floor.
- The **sheet design on the GS frames** has d ≤ 4, so p_floor ≥ 0.125. It
  cannot resolve anything, and is not run there.
- **Monte Carlo resolution.** The house estimator, `c / N` with c the
  number of null draws at least as extreme as the observed difference, can
  be exactly 0. The standard valid estimator is `(c + 1) / (N + 1)`. Every
  block test reports both. The verdict uses **the house estimator**, so the
  block and tile verdicts differ only in their unit (recommendation; § 11,
  Astra question 2). A test whose BH verdict differs between the two
  estimators is re-run at N = 100,000 with both; if they still differ, its
  claim is qualified.
- **Intervals.** A block interval supports a claim only if at least 20
  blocks contribute to the statistic: for F1, precision, and recall, blocks
  with any TP, FP, or FN in that cell; for MCC, sensitivity, and
  specificity, all blocks. Otherwise the interval is reported and flagged,
  and a claim reading it is qualified. P has 48 blocks on every GS frame and
  660 on the 55-map frame; S+ has 24 on the GS frames (§ 3.4).

**(d) Degenerate MCC.**

- An MCC that is undefined on the full data stays undefined (E81). The cell
  makes no MCC claim, as at tile level.
- In a bootstrap, undefined resamples are dropped and their share is
  reported. If more than 1 % of resamples are undefined, the interval is
  flagged unreliable, and a claim reading it is qualified.
- In a permutation null, the kernel scores an undefined permuted MCC as 0.0
  (`pairwise_permutation_test.py:514`). Their share is reported. If more
  than 1 % of null draws are undefined, the test is flagged unreliable, and
  its claim is qualified.

**(e) Conflicting designs.** P decides. A resolvable disagreement from S−,
S+, or Sheet qualifies a claim but never withdraws it, and never rescues a
claim that P withdraws. If S− disagrees while S+ and Sheet agree, the
pattern is unexpected, since smaller blocks are usually the less
conservative design. It is reported as surprising and the claim is
qualified.

**(f) What is never a reason.** A claim is never re-categorised because of
its importance to the paper, its effect size, or a preference among
designs. No design, block size, seed, or draw count may change after the
design lock, except the mechanical N = 100,000 rerun in (c).

### 3.7 What wave S does not change

- point estimates of every metric;
- the registered resampling unit (Decision 10: the tile) for the reported
  intervals and tests; wave S is a robustness check beside them;
- family membership, estimands, joins, buffers, frames, and seeds;
- any committed `evaluation.json`, tiering, or MCB artefact (wave S writes
  only under `reports/tile-join-wave-s/`).

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
counts, and tile order. These are the targets of the singleton-block
sentinel (GS2).

**Recommendation for Waves 2 and 3** (§ 11, PI question 4): export these
tables once, as a committed cache with a manifest, rather than have wave S
rebuild them. If they are not exported, wave S rebuilds them through the
same loaders Wave 3 uses (`cell_per_tile`, `cell_per_tile_classification`)
with the joins named explicitly, and gates each one against Wave 3's
committed aggregates.

## 5. Work items

### S.0 Enumeration, block maps, and the design lock (first; before any statistic)

Read-only on results. Outputs under `reports/tile-join-wave-s/`.

- **Eligibility manifest** (`eligibility.json` and `.md`). Apply § 3.1 to
  the signed register rows, `docs/paper/`, and the Wave 4 claim sources.
  Write one row per claim: the claim text or pointer, family, instrument,
  frame, buffer, joins, estimand, the Wave 3 artefact holding its
  tile-level verdict, and the applicable designs. Families from § 3.1's
  table that are absent are listed, with the reason.
- **Block maps** (`block-maps/<frame>.json`). One per frame named in the
  manifest, for P, S−, S+, and (55-map) Sheet, built by
  `scripts/lib_spatial_blocks.py` (new) by both routes of § 3.2. A frame
  whose stride does not divide 1,344 px, or whose tiles are not
  axis-parallel, is an uncovered decision and stops the wave (§ 7).
- **Design lock** (`design-lock.json`). SHA-256 of this specification, the
  manifest, every block map, and the parameter set (designs, seeds, N, B,
  q, thresholds). Commit it. The driver verifies these hashes before every
  run and refuses on a mismatch.
- **Cost.** Time one family per design on zbook (for example the Era-2
  board's MCC family under P) and project the total: the number of tests is
  known now (about 11,628 board pairs × 2 statistics × 3 designs on the
  Era-2 board, 595 × 2 × 4 on the 55-map board, plus ladders, MCB, and
  per-cell intervals), but their run time is not. The MCC kernel loops in
  Python over permutations (`pairwise_permutation_test.py:580` onwards), so
  it dominates. Record CPU-hours and the worker count zbook's memory allows.

### S.1 Code and tests (tier 1)

- `scripts/lib_spatial_blocks.py`: block identity, block maps by both
  routes, block aggregation of per-tile arrays (per run), and expansion of
  block draws to tile weights.
- `scripts/wave_s_block_check.py`: the driver; reads the lock, the
  manifest, and the inputs of § 4, runs every design, and writes the
  ledger.
- `selection_aware_intervals.run`: a block-map parameter, defaulting to
  singleton blocks.
- If S.0 shows the MCC loop kernel too slow, a vectorised block MCC kernel,
  gated against `permutation_test_mcc_arrays` for identical p-values on
  singleton blocks.
- `tests/test_spatial_blocks.py`, tier 1:
  - block maps: the two routes agree; one block per tile; no block spans
    sheets; a tile name has one identity in every frame; a clipped polygon
    does not move its tile; the counts of § 3.4 reproduced exactly;
  - **singleton blocks** reproduce the tile kernels bit for bit: F1 and MCC
    permutation, BCa intervals, `run`;
  - **block equivalence**: block aggregation followed by a kernel equals a
    slow reference path that swaps or draws every tile of a block together;
  - **perfect detector** (`docs/agent-guidance.md`, perfect-detector test):
    ground truth fed back as the prediction, merged and unmerged, single and
    replicated, under each design. F1 and MCC are 1, the interval collapses
    to [1, 1] (the percentile fallback, recorded), and a pair of identical
    arms gives p = 1 with d = 0;
  - **resolution**: p_floor = 2^(1 − d), checked against exact enumeration
    for small d;
  - **antisymmetry**: exchanging the arms leaves the two-sided p unchanged;
  - **refusals**: a block map that spans sheets, differs between arms, or
    disagrees with the lock is refused.
- **Red sentinel**: in a real-file copy of `scripts/` and `tests/`, never
  symlinked, break the sheet restriction, then separately the shared map.
  Confirm the tests turn red for each, and that the copy diffs equal once
  restored (Wave 1 spec, W1.2).

### S.2 Singleton-block reproduction

Run the driver with every tile its own block on every eligible family.
Every p-value, BH decision, tier, MCB set, and interval must equal Wave 3's
committed value to its recorded precision (GS2). This proves the block
layer changes nothing but the unit.

### S.3 Block runs

P, S−, S+, and (55-map) Sheet, over every eligible family, in one run from
the manifest, with a status per claim. Then the N = 100,000 reruns of
§ 3.6 (c). The run is idempotent: a second run over the same inputs gives
identical outputs.

### S.4 Verdict ledger

`verdicts.json` and `verdicts.md`: per claim, the tile-level verdict, the
verdict under each design, d and p_floor, both p estimators, degenerate
shares, interval block counts, and the category with the rule that
produced it. A summary table counts the claims in each category, by corpus
and family.

## 6. Gate GS (all must hold before M3)

1. **The lock held.** Its commit precedes every commit holding a block
   statistic, and every run verified its hashes.
2. **Singleton reproduction** (S.2) exact for every eligible family.
3. **Tier 1 green** on zbook, including `tests/test_spatial_blocks.py` and
   its perfect-detector and red-sentinel cases; `ruff check` and
   `npx markdownlint-cli2` clean on touched files.
4. **Block maps reproduce § 3.4**, the two routes agree, and no block spans
   sheets.
5. **Every eligible claim has a category** with its evidence; no claim is
   missing, and none was added after the lock without being logged (a
   claim found later by Wave 4 is run under the same frozen design and
   logged as late-eligible).
6. **Input invariants** of § 4 hold for every table used.
7. **Idempotent** rerun.
8. **A fresh-context `/audit`** of the wave S code has run, and each finding
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
- the two block routes disagreeing, a tile without exactly one block, a
  block spanning sheets, or a tile-sheet catalogue disagreeing with
  `map_name`;
- a frame whose stride does not divide 1,344 px, or whose tiles are not
  axis-parallel;
- an input table failing an invariant of § 4, or a family whose membership
  differs from Wave 3's;
- a write outside the scratch copy, the wave S branch, or
  `reports/tile-join-wave-s/`;
- a tier-1 failure that is not a pre-existing skip;
- any decision this specification does not cover.

**Never a problem**: any statistical outcome. A claim that is qualified or
withdrawn is a result, and the wave runs on. No stop condition may depend on
which claims survive.

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
  - `eligibility.json`, `eligibility.md`, `block-maps/`, and
    `design-lock.json` (S.0, committed before any statistic);
  - `cost.md` (S.0's timing and projection);
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
- every surprising pattern flagged under § 3.6 (direction and (e));
- the resolution and degeneracy diagnostics;
- the PR link.

The PI decides:

1. **Accept the categories**, so that Wave 4 restates claims from them.
2. **Wording** for qualified and withdrawn claims, and where the robustness
   sentence goes in the paper.
3. **Merge** the wave S PR.

## 10. Stated limits

- **Neighbouring blocks still share dependence.** Most tiles of a block lie
  on its edge (62.4 % of Era-2 tiles and 64.2 % of 55-map tiles overlap a
  tile of another block under P), and mound clustering does not stop at a
  block boundary. Blocks reduce the dependence between resampling units;
  they do not remove it.
- **Adjoining sheets may portray the same ground.** On the 55-map frame,
  33.0 % of tiles overlap a tile of another sheet, at seams where the same
  ground can appear about 170 m apart. No within-sheet block, and not the
  sheet design, makes those units independent.
- **The GS corpus cannot test sheet-level dependence.** Four sheets give a
  p_floor of at least 0.125. The occupancy correlogram shows strong
  between-sheet differences on both corpora, so on the GS frames this is a
  real gap, not a formality.
- **The dependence proxy is the reference, not the contrast.** The block
  sizes are related to where mounds are. The dependence that matters is in
  paired differences between conditions, which may be longer or shorter in
  range.
- **Inherited choices stay inherited.** Operating points fixed at tile
  level stay fixed; the tile-swap test still compares two outputs, not two
  configurations (tracker W2.7; `lib_permutation.py` module docstring).
- **A favourable check shows robustness to the specified design**, not that
  every inferential assumption holds.

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
   § 4 as a committed cache (recommended), or should wave S rebuild them?
5. **Withdrawal wording.** Is "withdrawn as a significance claim, point
   estimate kept, described as not established under spatial-block
   resampling" the right treatment (§ 3.6 (b))?
6. **Archaeological plausibility.** Does a primary block of about 6.7 km,
   with clustering measured out to roughly 2–5 km within sheets and strong
   differences between sheets, match your sense of how barrow groups and
   map-sheet character vary in these landscapes?
7. **Timeline.** Wave S adds a compute stage after Wave 3, whose length
   S.0 measures. Is the 2026-11-29 target to absorb it, or should claims
   that wave S has not reached by then be qualified pending the check?
8. **Review of the results.** D73 (3) requires review of this specification
   before it runs. Should Astra also spot-check the verdict ledger before
   M3 (recommended for any withdrawn claim)?

### For Astra

1. **Sizes and their rationale.** Is 1,344 px (about 6.7 km) right as the
   primary, with 672 px and 2,016 px as the sensitivity bracket and sheets
   as a 55-map extra? Is the reference-occupancy correlogram (§ 3.3) an
   acceptable proxy for plausible dependence, given that the dependence of
   paired differences cannot be consulted?
2. **The p-value estimator.** The verdict uses the house estimator `c / N`,
   which can be 0, so that block and tile verdicts differ only in their
   unit; `(c + 1) / (N + 1)` is reported beside it, and a disagreement
   triggers a rerun at N = 100,000. Or should `(c + 1) / (N + 1)` decide?
3. **Stratification.** Is an unstratified block bootstrap right, matching
   the tile design, or should resampling be stratified by sheet?
4. **Intervals with few blocks.** Is BCa with a leave-one-block-out
   jackknife acceptable at 24–48 blocks, with 20 contributing blocks as the
   minimum for an interval to support a claim, or should the percentile
   method be used for the block designs?
5. **Partial blocks.** Kept as they fall, so that block identity is a pure
   function of the tile (§ 3.2), rather than merged into a neighbour. Is
   that acceptable?
6. **Operating-point selection.** Pairwise tests treat an `oracle` or
   `opmax` operating point as fixed, as at tile level. Should wave S replay
   that selection inside each resample, or is it rightly out of scope here?
7. **Thresholds.** Are the 1 % degenerate-share limits (§ 3.6 (d)) and the
   p_floor > 0.05 resolution rule (§ 3.6 (c)) sensible as frozen?
8. **Seams.** Is stating the 55-map seam overlap as a limit enough, or is a
   further design needed, such as blocks that join each seam's two sides?

## 12. Freeze items: where each is answered

| Record § 5, wave S row | Here |
|---|---|
| (i) eligible cells, comparisons, families, buffers, frames, joins, estimands; pooled or run-averaged | § 3.1 |
| (ii) block construction in physical coordinates; deterministic shared tile-to-block map | § 3.2; counts § 3.4 |
| (iii) primary and sensitivity sizes, not chosen by significance or interval width; related to overlap, matching distance, dependence | § 3.3 |
| (iv) randomisation and bootstrap units, stratification, shared draws, interval method, seeds, draw counts, selection, multiplicity | § 3.5 |
| (v) too few informative blocks, degenerate MCC, attainable resolution, conflicting sensitivity results; when a claim is qualified or withdrawn | § 3.6 |
| actual block counts and sizes per frame | § 3.4 |
| stated limits | § 10 |
| aggregate runtime and memory-limited concurrency (Astra, round 2) | S.0 (measured, not estimated here) |

## Changelog

### 2026-11-18 — Original publication

Drafted for S169 on amd-tower, in the worktree branch `wave-s-spec` from
`fe9d433d7`, as the specification the record's § 5 requires before wave S
runs. It answers the five freeze items of Astra's round-2 review, and adds
two standard-library design scripts with their outputs
(`planning/tile-join-wave-s-spec-2026-11-18-scripts/`: `block_census.py`
and `occupancy_correlogram.py`), which read only bounds and reference
files. Status: draft for Astra's review; not approved. No block statistic
has been computed.
