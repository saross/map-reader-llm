# Tile-join Wave 1 — dry run, census, and worklist (W1.0)

> **Last revised**: 2026-11-18 (original publication; **INCOMPLETE — the wave is STOPPED at W1.0 step 2**, the 55-map sheet check). See [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), Wave 1 census agent (work item W1.0). Driven from
  amd-tower on branch `tile-join-wave-1-w10` (from `main` at
  `e92d1c5d7`); computation on zbook (reference environment, Python
  3.13.3), reading the gitignored tiles read-only from zbook's main checkout.
- **Specification**: `planning/tile-join-wave-1-spec-2026-11-01.md`, W1.0
  and § 5 (stop list).
- Every path, count, and number below was read from a file or produced by
  a command in this task.

## 0. Status: STOPPED (spec § 5, "the 55-map GS check finding a cross-sheet contact on map content")

The 55-map sheet check (§ 2) found **32 point–tile contacts, from 26
references, where a reference recorded on one sheet lies on the map
content of another sheet's tile**, in `inputs/vectors/references/best-available-gt-55maps-r2.geojson`
(the reference of smoke cell 2). The pixels were measured, not judged, and
three crops were then viewed: in two of them the point sits on a printed
burial-mound symbol on the *other* sheet. This is the case the
specification feared: adjacent sheets print the same mound, only one copy
is digitised, and sheet-specific scoring would score a correct detection of
the other sheet's printed copy as a false positive. The specification
stops the wave on it; this agent stopped its line of work and makes no
ruling.

| W1.0 step | State |
|---|---|
| 1. The 3.7 eligibility table | **Done**: `reports/tile-join-wave-1/withheld-37.md` (24 rows, all eligible subject to criterion 3, none unresolved; one flagged judgement, note A) |
| 2. 55-map sheet check | **Done, and it triggers the stop** (§ 2) |
| 3. Field schema | **Partial**: what was read before the stop is in § 3; not complete |
| 4. Census and worklist | **Not started** (`worklist.json` not written) |
| 5. Smoke cells 3–5 | **Not started** |
| 6. Recipe and input identity | **Not started** |
| 7. Determinism replays | **Not started** (no replay launched) |
| 8. Timings | **Not started** |

## 1. The 3.7 eligibility table

See `withheld-37.md`. Eight families, 24 (cell, family) rows; every
committed exclusion record names only `tile_join_detection_shortfall`;
criterion 3 awaits W1.5. Frame-wide geometric tile-MCC for these cells has
been on record since 2026-09-12
(`reports/tile-mcc-geometric-join-2026-09-12.md:247–249`), so the rule is
fixed before their sheet-specific scores exist, not before any geometric
score was seen; no score enters any verdict.

## 2. The 55-map sheet check (the stop)

**Method.** `reports/tile-join-wave-1/scripts/sheet_check_55map.py`
(modelled on `planning/tile-join-resolution-2026-11-01-scripts/sheet_boundary_check.py`;
geometry standard-library only, no scorer import). Frame:
`inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`, 8,541 tiles,
55 sheets (each tile's sheet by the scorer's `_x<n>_y<n>` rule; it equals
the tile's `map_name` on all 8,541). References: all five tracked 55-map
files, sheet from `source_map` (every file's 55 sheets are frame sheets).
For each contact the tile PNG was read and measured: near-black (every
channel ≤ 20, or transparent) fraction of a 17 × 17 px window around the
point, the extent of non-black content along the point's row and column,
and the colour at the point. Verdict rule: `padding` if the window is at
least 95 % near-black **and** the point lies outside its row's or column's
content span; `map-content` if the window is under 50 % near-black and the
point lies inside both spans; otherwise `ambiguous`. Run on zbook,
2026-11-18, at `c1a7a23fd`; outputs committed as
`reports/tile-join-wave-1/scripts/out/sheet_check_55map.txt` (full) and
`…/out/sheet_check_55map_summary.json` (counts and every non-padding
contact). Crops of every contact (96 × 96 px around the point, enlarged
3 ×, point circled in red) are in zbook scratch,
`~/scratch/wave1/w10/sheet-check/crops/<reference-file-stem>/<ref-id>__<tile-stem>.png`
(814 for r2, 814, 873, 534, and 544 for the others: the two student
files yield fewer crop files than contacts because their \`uuid\` values
are written as rounded numbers, so file names collide; their contacts are
all in the committed \`.txt\`).

**Results.**

| Reference file | Points | Cross-sheet pairs ≤ 50 / 100 / 200 / 500 / 1,000 m | Closest cross-sheet pair | Contacts (references) | Padding | Ambiguous | **Map content** (references) | Tracked evaluations naming it (text match) |
|---|---:|---|---|---:|---:|---:|---:|---:|
| `best-available-gt-55maps-r2.geojson` | 5,018 | 0 / 0 / 0 / 35 / 155 | 200.7 m | 814 (648) | 764 | 18 | **32 (26)** | 196 |
| `best-available-gt-55maps.geojson` | 5,010 | 0 / 0 / 0 / 34 / 153 | 200.7 m | 814 (648) | 764 | 18 | **32 (26)** | 67 |
| `canonical-gt-55maps-r50.geojson` | 5,161 | 24 / 24 / 32 / 69 / 221 | 3.1 m | 873 (697) | 820 | 20 | **33 (27)** | 8 |
| `student-mounds-55maps-reviewed.geojson` | 4,746 | 0 / 0 / 1 / 33 / — | 188.7 m | 757 (608) | 708 | 16 | **33 (17)** | 58 |
| `student-mounds-55maps.geojson` | 4,770 | 0 / 0 / 1 / 33 / — | 188.7 m | 767 (614) | 717 | 15 | **35 (19)** | 2 |

(The last column counts tracked `*evaluation.json` files whose text
contains `"ground_truth": "inputs/vectors/references/<file>"`; it is
indicative, not a census.) The full 1,000 m counts for the two student
files and every pair within 500 m are in the committed `.txt`.

**Where.** In r2 every map-content contact involves one of nine sheet
pairs, all at the seams of the reprojected `_4326` sheets:
Granit/Chirpan, Granit/Tatarevo, Chirpan/Sredets, Tatarevo/K-35-075-1,
Skobelevo/Dimitrovgrad, Skobelevo/K-35-075-2, Dimitrovgrad/Galabovo,
Dimitrovgrad/K-35-076-1, Glavan/K-35-077-1 (reference sheet / tile sheet).
This is the misregistered overlap the parent record noted ("the same
ground appears on neighbouring sheets about 170 m apart", § 2.4).

**Viewed, after measurement** (crops fetched to amd-tower and read as
images):

- r2 `student:01862` (Granit) in `K-35-063-2_Chirpan_4326_x0_y672.png`
  at col 164.6, row 280.7: the point lies on a printed burial-mound symbol
  with its label on the Chirpan sheet.
- r2 `student:02387` (Tatarevo) in `K-35-075-1_x1344_y0.png` at col
  364.1, row 52.6: the point lies on a printed mound symbol labelled "2" on
  K-35-075-1, just inside its map face.
- r2 `student:02782` (Dimitrovgrad) in `K-35-076-1_x1344_y0.png` at col
  262.4, row 89.1: the point lies on a symbol beside a printed mound symbol
  and "2" label (map content in any case).
- r2 `student:01575` (`ambiguous`, window 0.533) in
  `K-35-054-4_Voynika_x4032_y672.png`: the point is on the black map edge
  itself, between content and padding.

**Why it matters, and a pointer for the ruling.** In r2 no cross-sheet
pair lies within 200 m, so for these mounds only one sheet's copy is a
reference. Under sheet-specific scoring a correct detection of the other
sheet's printed copy, attributed (by D50) to the sheet whose tile showed
it, has no reference on its sheet and scores as a false positive, while
the frame-wide join would match it. The canonical r50 reference differs:
it carries 415 `phantom:*` references (`layer` `phantom_canonical`,
`position_source` `detection_centroid`, `provenance`
`canonical_review_r50`), and 24 of its cross-sheet pairs lie within
50 m, every listed one a `student` reference on one sheet beside a
`phantom` on the neighbouring sheet. That looks like a second copy of the
same mound added on the other sheet by review; this agent did not verify
that reading.

### 2.1 Every non-padding contact in r2 (the smoke-cell-2 reference)

| # | Reference (sheet, id) | Tile it lies in | Pixel (col, row) | Window near-black | RGB at point | Row content span | Column content span | Measured |
|---:|---|---|---|---:|---|---|---|---|
| 1 | `K-35-054-1_Straldzha_4326` `student:00962` | `K-35-053-2_x4032_y1344.png` | 91.0, 240.1 | 0.765 | (0, 0, 0) | (0, 86) | — | ambiguous |
| 2 | `K-35-054-3_Yambol` `student:01202` | `K-35-066-1_x1680_y0.png` | 227.8, 2.6 | 0.914 | (0, 0, 0) | — | (11, 383) | ambiguous |
| 3 | `K-35-055-1` `student:01447` | `K-35-054-2_Atolov_4326_x4032_y2688.png` | 89.8, 342.6 | 0.824 | (0, 0, 0) | (0, 83) | — | ambiguous |
| 4 | `K-35-055-1` `student:01447` | `K-35-054-2_Atolov_4326_x4032_y3024.png` | 89.8, 6.6 | 0.824 | (0, 0, 0) | (0, 83) | — | ambiguous |
| 5 | `K-35-055-3` `student:01561` | `K-35-055-1_x1344_y3360.png` | 139.9, 357.1 | 0.882 | (0, 0, 0) | — | (0, 350) | ambiguous |
| 6 | `K-35-055-3` `student:01561` | `K-35-055-1_x1344_y3696.png` | 139.9, 21.1 | 0.882 | (0, 0, 0) | — | (0, 14) | ambiguous |
| 7 | `K-35-055-3` `student:01575` | `K-35-054-4_Voynika_x4032_y672.png` | 79.7, 87.8 | 0.533 | (135, 143, 147) | (0, 79) | (0, 383) | ambiguous |
| 8 | `K-35-062-4_Asenovgrad_4326` `student:01822` | `K-35-063-1_Granit_4326_x0_y3360.png` | 83.7, 296.8 | 0.886 | (0, 0, 0) | (90, 383) | — | ambiguous |
| 9 | `K-35-063-1_Granit_4326` `student:01862` | `K-35-063-2_Chirpan_4326_x0_y672.png` | 164.6, 280.7 | 0.000 | (166, 195, 141) | (135, 383) | (0, 383) | map-content |
| 10 | `K-35-063-1_Granit_4326` `student:01863` | `K-35-063-2_Chirpan_4326_x0_y672.png` | 192.8, 321.7 | 0.000 | (187, 169, 131) | (134, 383) | (0, 383) | map-content |
| 11 | `K-35-063-1_Granit_4326` `student:01876` | `K-35-063-3_Tatarevo_4326_x2352_y0.png` | 360.5, 165.2 | 0.000 | (223, 226, 212) | (0, 383) | (149, 383) | map-content |
| 12 | `K-35-063-1_Granit_4326` `student:01876` | `K-35-063-3_Tatarevo_4326_x2688_y0.png` | 24.5, 165.2 | 0.000 | (223, 226, 212) | (0, 383) | (149, 383) | map-content |
| 13 | `K-35-063-1_Granit_4326` `student:01878` | `K-35-063-3_Tatarevo_4326_x2688_y0.png` | 327.1, 201.7 | 0.000 | (124, 132, 139) | (0, 383) | (155, 383) | map-content |
| 14 | `K-35-063-1_Granit_4326` `student:01879` | `K-35-063-3_Tatarevo_4326_x3360_y0.png` | 220.4, 177.4 | 0.000 | (243, 245, 240) | (0, 383) | (167, 383) | map-content |
| 15 | `K-35-063-1_Granit_4326` `student:01882` | `K-35-063-3_Tatarevo_4326_x3696_y0.png` | 130.1, 238.2 | 0.000 | (231, 234, 237) | (0, 383) | (171, 383) | map-content |
| 16 | `K-35-063-1_Granit_4326` `student:02069` | `K-35-063-3_Tatarevo_4326_x2352_y0.png` | 348.2, 140.4 | 0.920 | (0, 0, 0) | (29, 36) | (148, 383) | ambiguous |
| 17 | `K-35-063-1_Granit_4326` `student:02069` | `K-35-063-3_Tatarevo_4326_x2688_y0.png` | 12.2, 140.4 | 0.920 | (0, 0, 0) | — | (148, 383) | ambiguous |
| 18 | `K-35-063-2_Chirpan_4326` `student:02190` | `K-35-064-1_Sredets_4326_x0_y0.png` | 182.1, 101.9 | 0.000 | (155, 96, 53) | (129, 383) | (68, 383) | map-content |
| 19 | `K-35-063-2_Chirpan_4326` `student:02191` | `K-35-064-1_Sredets_4326_x0_y0.png` | 141.1, 367.8 | 0.080 | (137, 116, 104) | (126, 383) | (68, 383) | map-content |
| 20 | `K-35-063-2_Chirpan_4326` `student:02191` | `K-35-064-1_Sredets_4326_x0_y336.png` | 141.1, 31.8 | 0.080 | (137, 116, 104) | (126, 383) | (0, 383) | map-content |
| 21 | `K-35-063-2_Chirpan_4326` `student:02194` | `K-35-064-1_Sredets_4326_x0_y1008.png` | 114.0, 300.3 | 0.201 | (147, 151, 162) | (109, 383) | (0, 383) | map-content |
| 22 | `K-35-063-2_Chirpan_4326` `student:02195` | `K-35-064-1_Sredets_4326_x0_y1008.png` | 128.4, 365.1 | 0.000 | (244, 245, 247) | (108, 383) | (0, 383) | map-content |
| 23 | `K-35-063-2_Chirpan_4326` `student:02195` | `K-35-064-1_Sredets_4326_x0_y1344.png` | 128.4, 29.1 | 0.000 | (244, 245, 247) | (108, 383) | (0, 383) | map-content |
| 24 | `K-35-063-2_Chirpan_4326` `student:02196` | `K-35-064-1_Sredets_4326_x0_y1344.png` | 132.6, 132.5 | 0.000 | (210, 214, 215) | (105, 383) | (0, 383) | map-content |
| 25 | `K-35-063-3_Tatarevo_4326` `student:02387` | `K-35-075-1_x1344_y0.png` | 364.1, 52.6 | 0.052 | (53, 52, 48) | (0, 383) | (37, 383) | map-content |
| 26 | `K-35-063-3_Tatarevo_4326` `student:02387` | `K-35-075-1_x1680_y0.png` | 28.1, 52.6 | 0.052 | (53, 52, 48) | (0, 383) | (37, 383) | map-content |
| 27 | `K-35-063-3_Tatarevo_4326` `student:02388` | `K-35-075-1_x2016_y0.png` | 374.2, 107.2 | 0.000 | (227, 228, 227) | (0, 383) | (52, 383) | map-content |
| 28 | `K-35-063-3_Tatarevo_4326` `student:02388` | `K-35-075-1_x2352_y0.png` | 38.2, 107.2 | 0.000 | (227, 228, 227) | (0, 383) | (52, 383) | map-content |
| 29 | `K-35-063-3_Tatarevo_4326` `student:02389` | `K-35-075-1_x3024_y0.png` | 223.7, 101.4 | 0.048 | (125, 132, 132) | (0, 383) | (70, 383) | map-content |
| 30 | `K-35-063-3_Tatarevo_4326` `student:02390` | `K-35-075-1_x3360_y0.png` | 334.6, 87.7 | 0.218 | (104, 99, 72) | (0, 383) | (82, 383) | map-content |
| 31 | `K-35-063-4_Skobelevo_4326` `student:02391` | `K-35-075-2_x2016_y0.png` | 211.2, 65.9 | 0.000 | (186, 203, 170) | (0, 383) | (42, 383) | map-content |
| 32 | `K-35-063-4_Skobelevo_4326` `student:02392` | `K-35-075-2_x3024_y0.png` | 200.6, 125.8 | 0.000 | (97, 88, 83) | (0, 383) | (61, 383) | map-content |
| 33 | `K-35-063-4_Skobelevo_4326` `student:02393` | `K-35-064-3_Dimitrovgrad_4326_x0_y1680.png` | 108.7, 368.8 | 0.010 | (169, 174, 177) | (95, 383) | (0, 383) | map-content |
| 34 | `K-35-063-4_Skobelevo_4326` `student:02393` | `K-35-064-3_Dimitrovgrad_4326_x0_y2016.png` | 108.7, 32.8 | 0.010 | (169, 174, 177) | (95, 383) | (0, 383) | map-content |
| 35 | `K-35-063-4_Skobelevo_4326` `student:02394` | `K-35-064-3_Dimitrovgrad_4326_x0_y2016.png` | 108.6, 57.6 | 0.007 | (230, 234, 234) | (94, 383) | (0, 383) | map-content |
| 36 | `K-35-063-4_Skobelevo_4326` `student:02445` | `K-35-064-3_Dimitrovgrad_4326_x0_y1344.png` | 102.3, 119.0 | 0.647 | (0, 0, 0) | (105, 383) | (270, 383) | ambiguous |
| 37 | `K-35-063-4_Skobelevo_4326` `student:02465` | `K-35-064-3_Dimitrovgrad_4326_x0_y1680.png` | 92.2, 111.1 | 0.882 | (0, 0, 0) | (99, 383) | — | ambiguous |
| 38 | `K-35-064-3_Dimitrovgrad_4326` `student:02686` | `K-35-064-4_Galabovo_4326_x0_y1008.png` | 101.9, 297.0 | 0.000 | (231, 227, 218) | (91, 383) | (0, 383) | map-content |
| 39 | `K-35-064-3_Dimitrovgrad_4326` `student:02687` | `K-35-064-4_Galabovo_4326_x0_y3360.png` | 105.9, 231.6 | 0.000 | (189, 203, 131) | (56, 383) | (0, 362) | map-content |
| 40 | `K-35-064-3_Dimitrovgrad_4326` `student:02781` | `K-35-076-1_x336_y0.png` | 98.7, 39.0 | 0.004 | (162, 193, 136) | (0, 383) | (7, 383) | map-content |
| 41 | `K-35-064-3_Dimitrovgrad_4326` `student:02782` | `K-35-076-1_x1344_y0.png` | 262.4, 89.1 | 0.000 | (231, 231, 230) | (0, 383) | (26, 383) | map-content |
| 42 | `K-35-064-3_Dimitrovgrad_4326` `student:02783` | `K-35-076-1_x2016_y0.png` | 283.4, 80.9 | 0.000 | (224, 223, 217) | (0, 383) | (37, 383) | map-content |
| 43 | `K-35-064-3_Dimitrovgrad_4326` `student:02784` | `K-35-076-1_x3360_y0.png` | 102.7, 90.0 | 0.000 | (191, 181, 150) | (0, 383) | (55, 383) | map-content |
| 44 | `K-35-065-3_Glavan_4326` `student:03135` | `K-35-077-1_x3360_y0.png` | 323.1, 68.4 | 0.000 | (199, 203, 205) | (0, 383) | (38, 383) | map-content |
| 45 | `K-35-075-1` `student:03969` | `K-35-074-2_x4032_y672.png` | 166.2, 121.4 | 0.741 | (0, 0, 0) | (0, 161) | — | ambiguous |
| 46 | `K-35-076-1` `student:04282` | `K-35-076-2_x0_y2352.png` | 13.6, 345.6 | 0.543 | (0, 0, 0) | (14, 383) | — | ambiguous |
| 47 | `K-35-076-1` `student:04282` | `K-35-076-2_x0_y2688.png` | 13.6, 9.6 | 0.543 | (0, 0, 0) | (14, 383) | (63, 383) | ambiguous |
| 48 | `K-35-076-2` `student:04378` | `K-35-076-4_x3696_y0.png` | 246.1, 44.2 | 0.886 | (0, 0, 0) | — | (51, 383) | ambiguous |
| 49 | `K-35-077-3` `student:04646` | `K-35-077-1_x0_y3360.png` | 20.9, 324.6 | 0.882 | (0, 0, 0) | — | (0, 317) | ambiguous |
| 50 | `K-35-066-1` `extension:408` | `K-35-066-3_x3360_y0.png` | 326.3, 14.3 | 0.647 | (0, 0, 0) | — | (17, 383) | ambiguous |

## 3. Field schema (partial; stopped before completion)

Read before the stop, from `scripts/evaluate_detections.py` and
`scripts/lib_advanced_metrics.py` at `e92d1c5d7`. Not yet complete:
the other consumers below were located but not traced, and the other
drivers' outputs were not read.

**Target set (determined by the classification join or the count table):**

- `summary.tile_classification` (and each `per_run[].tile_classification`):
  `confusion`, `mcc` / `sensitivity` / `specificity` {`point`, `mean`,
  `ci_lower`, `ci_upper`, `method`}, `tile_join`, and the withheld form
  (`withheld`, `withheld_reason`, `withheld_detail`,
  `withheld_quantities`, `tile_join_diagnostics`); aggregated cells add
  `n_runs`, `n_runs_defined`, `n_runs_withheld`, `confusion_source`
  (`evaluate_detections.py:238–396`, `:1423–1461`).
- Each `buffers[]` row: `f1_ci_lower`, `f1_ci_upper`, `f1_ci_method`,
  `p_ci_*`, `r_ci_*`, `coverage` {`n_zero_count_tiles`, `zero_fraction`,
  `coverage_status`; `n_tiles`, `threshold`, `coverage_source`,
  `n_processed_tiles`, `n_unprocessed_tiles`, `coverage_detail` do not
  depend on the table except through its presence}, `coverage_status`,
  `ci_unreliable`, `ci_excludes_point`, `sparse_coverage`,
  `ci_flag_basis`, and the withheld form `ci_withheld`,
  `ci_withheld_reason`, `ci_withheld_detail` (`:947–1023`,
  `:1232–1352`; `bootstrap_ci`, `lib_advanced_metrics.py:3489–3655`;
  `_compute_coverage`, `:411–537`).
- Aggregated rows add `ci_zero_fraction`, `ci_n_tiles`,
  `ci_withheld_n_passes` (`:1569–1673`).
- Summary roll-ups: `ci_unreliable_any_buffer`, `coverage_status`
  (`:1390–1404`, `:1697–1711`); `tile_join_withheld` (present or absent,
  with `n_passes_withheld` on aggregates; `:1419–1420`, `:1724–1733`).
- `_metadata.bootstrap.method` and `methods_measured` (measured from the
  per-metric methods, which a new table can move between `BCa` and
  `percentile_fallback`; `:1803–1844`); `_metadata.cli_args.tile_join`
  and the provenance W1.1 adds (`count_table_join`).
- Siblings: `evaluation.csv` columns `f1_ci_*`, `p_ci_*`, `r_ci_*`,
  `mcc*`, `sensitivity`, `specificity`, `*_boot_mean`,
  `coverage_status`, `ci_unreliable`, `ci_zero_fraction`, `ci_n_tiles`
  (`:1926–2009`); `evaluation.md` CI cells, MCC columns, and the
  withheld, partial, sparse, and undefined-MCC footnotes (`:2011–2269`);
  batch-mode `batch_summary.csv` and `.json` rows (`:2343–2523`).

**Non-target set (so far):** `buffer_metres`, `f1`/`f1_point`,
`precision`/`p_point`, `recall`/`r_point` (the point estimates and
their aliases), `label`, `n_detections`, `n_runs`, `detection_scope`,
`version`, and `_metadata` apart from the fields above. **Volatile on
every run** (to be excluded from any byte comparison, not non-target
drift): `timestamp`, `_metadata.generated_at_utc`,
`_metadata.script_git_commit` / `script_git_status` /
`input_git_state.head`, and the `.md` "Generated" line.

**Other per-tile-table consumers located, not yet traced:** in
`lib_advanced_metrics.py`, `compute_per_tile_tp_fp_fn` is called by
`bootstrap_ci` (`:3563`), `bootstrap_effect_size_ci` (`:3819`,
`:3823`), `bootstrap_multi_run_ci` (`:4004`),
`bootstrap_multi_run_effect_size_ci` (`:4117`, `:4124`), and
`bootstrap_interaction_ci` (`:4339`); `calculate_tile_classification`
by `compute_per_tile_classification` (`:3170`), `score_detection_set`
(`:3305`), `bootstrap_tile_classification_ci` (`:5172`), and
`bootstrap_tile_effect_size_ci` (`:5351`, `:5355`). In
`evaluate_detections.py` the pre-flight `describe_tile_join_refusal`
(`:1183–1187`) decides, under the classification join, whether the F1
intervals are computed at all, so the join reaches the interval fields
through the refusal as well as through the table.

## 4. Census, worklist, smoke cells, recipes, determinism, timings

Not started: the wave stopped at § 2. Nothing was launched on zbook beyond
the sheet check.

## 5. Stop-list items checked

| § 5 item | Checked | Result |
|---|---|---|
| Unresolved row in the 3.7 eligibility table | yes | none (24 rows resolved) |
| The 55-map GS check finding a cross-sheet contact on map content | yes | **found: 32 contacts (26 references) in r2; the stop** |
| A write outside the scratch copy, the Wave 1 branch, or `reports/tile-join-wave-1/` | yes | none: writes were this worktree's `reports/tile-join-wave-1/`, zbook `~/scratch/wave1/w10/`, and the zbook worktree by fast-forward |
| Any decision this specification does not cover | yes | note A of `withheld-37.md` is a judgement, flagged; not treated as a stop |
| All others (G1 items, replay, refusals, count sums, tier 1) | no | belong to W1.1–W1.5, not reached |

## Changelog

### 2026-11-18 — Original publication

Written by the Wave 1 census agent at the stop. W1.0 steps 1 and 2 done;
step 3 partial; steps 4–8 not started. The 55-map sheet check found
cross-sheet contacts on map content (§ 2), a § 5 stop.
