# Tile-join Wave 1 — dry run, census, and worklist (W1.0)

> **Last revised**: 2026-11-19 (seam counts corrected after Astra's review; W1.0 steps 3–8 completed after the stop; **the wave remains STOPPED on the 55-map seam ruling**). See [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), Wave 1 census agent (work item W1.0). Driven from
  amd-tower on branch `tile-join-wave-1-w10` (from `main` at
  `e92d1c5d7`); computation on zbook (reference environment, Python
  3.13.3), reading the gitignored tiles read-only from zbook's main checkout.
- **Specification**: `planning/tile-join-wave-1-spec-2026-11-01.md`, W1.0
  and § 5 (stop list).
- Every path, count, and number below was read from a file or produced by
  a command in this task.

## 0. Status: STOPPED on the 55-map seam ruling; W1.0's read-only steps completed

The 55-map sheet check (§ 2) found **32 point–tile contacts, from 26
references, where a reference recorded on one sheet lies on the map
content of another sheet's tile**, in `inputs/vectors/references/best-available-gt-55maps-r2.geojson`
(the reference of smoke cell 2), with no reference on the contacted sheet
nearby; in the crops inspected, the point lies on a printed mound symbol
on the neighbouring sheet (the other contacts are candidates, not
adjudicated). That is a specification § 5 stop. The main
session verified it, notified the PI, and recorded the stop in
`reports/tile-join-wave-1/stop-2026-11-18-55map-seams.md`. **The wave is
stopped on the seam ruling.** By the main session's decision (stop
record § 3), the read-only W1.0 steps that do not depend on the ruling
continued, together with a measurement for the ruling (§ 2.2). Nothing
here consumes a seam ruling, and no corrected (sheet-specific) score was
computed for any cell.

| W1.0 step | State |
|---|---|
| 1. The 3.7 eligibility table | **Done**: `withheld-37.md` (24 rows, all eligible subject to criterion 3, none unresolved; note A flagged, pending the PI) |
| 2. 55-map sheet check | **Done; it raised the stop** (§ 2); measurement for the ruling added (§ 2.2) |
| 3. Field schema | **Done** (§ 3) |
| 4. Census and worklist | **Done** (§ 4; `worklist.json`, 2,829 entries; every paper-cited file resolved) |
| 5. Smoke cells 3–5 | **Pinned** (§ 5) |
| 6. Recipe and input identity | **Done** for all eight (§ 6) |
| 7. Determinism replays | **Done**: all eight reproduce under their recorded rules (§ 7) |
| 8. Timings | **Recorded** (§ 8); the Wave 2 projection is the main session's and is paused with Wave 2 |

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
files yield fewer crop files than contacts because their `uuid` values
are written as rounded numbers, so file names collide; their contacts are
all in the committed `.txt`).

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

**Why it matters, and a pointer for the ruling** (revised 2026-11-19
after Astra's review, to keep apart what was measured, what was seen, and
what is not adjudicated). *Measured:* in r2 no cross-sheet pair lies
within 200 m, and no contacted-sheet reference lies within 50 m of any
non-padding contact (§ 2.2); that shows no local annotation on the
contacted sheet, not what is printed there, since the pixel test detects
map content, not mound symbols, and the seams are misregistered. *Seen:*
the crops above show a printed mound symbol at the point. *Not
adjudicated:* the other map-content contacts and the ambiguous ones.
Where a contact is a second printed copy, the effects differ by level.
At symbol level, a correct detection of that copy, attributed by D50 to
the sheet whose tile showed it, has no reference on its sheet and can be
scored a false positive. At tile level, a tile changes only if it holds
none of its own sheet's references: 11 of r2's 26 contacted tiles for
the map-content scope (§ 2.2). The canonical r50 reference differs: it
carries 415 `phantom:*` references (`layer` `phantom_canonical`,
`position_source` `detection_centroid`, `provenance`
`canonical_review_r50`), and 24 of its cross-sheet pairs lie within
50 m, each a `student` reference on one sheet beside a `phantom` on the
neighbouring sheet. That is a lead that review added the second copy;
it does not confirm each feature's identity.

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

### 2.2 Is the second copy already digitised, and what each option would move (for the seam ruling)

Measured after the stop, at the main session's request (stop record
§ 4, item 1), by `reports/tile-join-wave-1/scripts/seam_second_copy.py`
(standard library; no scorer code, no model output). It reads the
contacts and pixel verdicts from `scripts/out/sheet_check_55map_summary.json`
and writes `scripts/out/seam_second_copy.txt` and `.json` (zbook,
2026-11-18, at `6cda42d68`). The
baseline is plain sheet-specific containment: a tile is
reference-positive if a reference recorded on its own sheet lies inside
it. The options are those of the stop record § 4: (a) add the second copy
as a reference on the contacted sheet, at the contact point, wherever no
contacted-sheet reference lies within 50 m; (b) a seam exception, under
which the contacted tile is also positive; (c) frame-wide containment;
(d) remove the contacted tile and the reference's own-sheet tiles from
classification. Counts only.

**(i) Is a reference on the contacted sheet already within 20 m / 50 m?**

| Reference file | Map-content contacts | … with a contacted-sheet reference ≤ 20 m (phantom) | ≤ 50 m (phantom) | Ambiguous contacts | … ≤ 20 m | ≤ 50 m |
|---|---:|---:|---:|---:|---:|---:|
| `best-available-gt-55maps-r2` | 32 | 0 | 0 | 18 | 0 | 0 |
| `best-available-gt-55maps` | 32 | 0 | 0 | 18 | 0 | 0 |
| `canonical-gt-55maps-r50` | 33 | **22 (22)** | **29 (29)** | 20 | 1 (0) | 1 (0) |
| `student-mounds-55maps-reviewed` | 33 | 0 | 0 | 16 | 0 | 0 |
| `student-mounds-55maps` | 35 | 0 | 0 | 15 | 0 | 0 |

Every second copy found is a `phantom:*` reference (layer
`phantom_canonical`, provenance `canonical_review_r50`). The four
canonical map-content contacts without one (`student:02195`,
`student:02396`, `student:02508`, `student:02793`) have their nearest
contacted-sheet reference 835.8–1,213.3 m away. Per-contact ids, layers,
and distances are in the committed `.txt` and `.json`.

**(ii) and (iii) Tiles moved, relative to sheet-specific containment.**
Corrected 2026-11-19 after Astra's review (see below): option (a) now
adds one reference per **(source feature, recipient sheet)**, the source
feature identified by its index in its file, however many overlapping
tiles of that sheet the point reaches. Contacts are kept beside them,
labelled as contacts. Baseline positive tiles (of 8,541): r2 3,196;
best-available 3,191; canonical 3,200; student-reviewed 3,056; student
3,055. No two references of any file share a sheet and identical
coordinates, so the feature keys are unambiguous.

| Reference file | Scope | Contacts | (feature, recipient sheet) pairs | Distinct contacted tiles | (a) contacts without a second copy / **references added** / tiles turning positive | (b) tiles turning positive | (d) tiles removed (positive / negative) |
|---|---|---:|---:|---:|---|---:|---|
| r2 | map content | 32 | 26 | 26 | 32 / **26** / 11 | 11 | 52 (41 / 11) |
| r2 | + ambiguous | 50 | 40 | 41 | 50 / **40** / 17 | 17 | 85 (68 / 17) |
| best-available | map content | 32 | 26 | 26 | 32 / **26** / 11 | 11 | 52 (41 / 11) |
| best-available | + ambiguous | 50 | 40 | 41 | 50 / **40** / 17 | 17 | 85 (68 / 17) |
| canonical r50 | map content | 33 | 27 | 27 | 4 / **4** / 0 | 0 | 53 (53 / 0) |
| canonical r50 | + ambiguous | 53 | 44 | 41 | 23 / **20** / 4 | 4 | 82 (78 / 4) |
| student-reviewed | map content | 33 | 27 | 27 | 33 / **27** / 11 | 11 | 53 (42 / 11) |
| student-reviewed | + ambiguous | 49 | 40 | 39 | 49 / **40** / 15 | 15 | 79 (64 / 15) |
| student | map content | 35 | 29 | 27 | 35 / **29** / 11 | 11 | 53 (42 / 11) |
| student | + ambiguous | 50 | 41 | 39 | 50 / **41** / 15 | 15 | 79 (64 / 15) |

On r2 the six references whose point reaches two tiles of the same
recipient sheet are `student:01876` (Tatarevo), `student:02191` and
`student:02195` (Sredets), `student:02387` and `student:02388`
(K-35-075-1), and `student:02393` (Dimitrovgrad), exactly as Astra
reported. The tile counts did not change: they were always counted as
sets of tiles.

**Option (c), frame-wide containment, split into disjoint categories.**
Each tile that turns positive is assigned by the pixel verdicts of the
contacts inside it, in priority order: any map-content contact; else any
ambiguous contact; else, if every contact is padding, confirmed padding;
else remainder. Verdicts come from the sheet check's full output
(`~/scratch/wave1/w10/sheet-check/sheet_check_55map.json`), padding
contacts included.

| Reference file | Tiles turning positive | Map-content contacted | Ambiguous contacted | Confirmed padding | Remainder | Tiles with mixed verdicts |
|---|---:|---:|---:|---:|---:|---:|
| r2 | 333 | 11 | 6 | 316 | 0 | 8 |
| best-available | 333 | 11 | 6 | 316 | 0 | 8 |
| canonical r50 | 324 | 0 | 4 | 320 | 0 | 2 |
| student-reviewed | 325 | 11 | 4 | 310 | 0 | 7 |
| student | 325 | 11 | 4 | 310 | 0 | 7 |

So on r2, 316 of the 333 tiles that a frame-wide join would make
positive are confirmed padding (every contact inside them measured as
padding), 11 are map-content contacts, and 6 hold only ambiguous
contacts. This replaces the earlier wording, which treated everything
except the 11 map-content tiles as padding without showing it.

Reading the table: (a) and (b) move the same tiles here, because a tile
the contact reaches either already holds one of its own sheet's
references or does not; they differ in what else they change ((a) adds
references, and so recall's denominator; (b) changes matching). On r2,
15 of the 26 contacted tiles are already positive from their own sheet's
references, so 11 tiles move.

**Astra's independent audit** (`~/agent-mail/codex/outbox/claude/20261118T130529Z-astra-seam-measurement-counting-finding.md`,
reviewing `seam_second_copy.py` at `6bd4a3e03`): all 50 of r2's
non-padding contacts reproduced, measurements and verdicts both, with no
discrepancies; every supplied world file has zero rotation. Under a
nearest-pixel-centre sensitivity, the two ambiguous contacts of
`student:04282` (sheet K-35-076-1) change, so they **stay unresolved for
manual judgement**: `student:04282` in `K-35-076-2_x0_y2352.png` (col
13.6, row 345.6) and in `K-35-076-2_x0_y2688.png` (col 13.6, row 9.6),
rows 46 and 47 of § 2.1 (Astra's evidence-manifest indices 46 and 47).

**The canonical r50 lead, checked.** All **24** of canonical r50's
student–phantom cross-sheet pairs within 50 m are map-content contacts:
in each, the student reference on one sheet lies on the map content of a
tile of the phantom's sheet (distances 3.1–39.5 m, listed in the `.txt`).
So the r50 review appears to have digitised the neighbouring sheet's copy
for 29 of its 33 map-content contacts, option (a) in effect (a lead from
proximity, not a check of each feature's identity); r2, the
best-available file, and the student files carry no `phantom` layer (r2's
layers are `student` 4,726, `extension` 278, `audit` 14 by `gt_id`
prefix).

## 3. Field schema

Read from `scripts/evaluate_detections.py` and
`scripts/lib_advanced_metrics.py` at `e92d1c5d7` (line numbers are
there). The scorer writes `evaluation.json` (keys `version`, `timestamp`,
`summary`, `_metadata`, and `per_run` for replicated cells;
`write_outputs`, `:1847–1894`), `evaluation.csv`, and `evaluation.md`;
batch mode adds `batch_summary.csv` and `.json`.

### 3.1 How the per-tile table and the classification join reach the file

| Route | Where | What it determines |
|---|---|---|
| Pre-flight refusal probe, `describe_tile_join_refusal`, under the **classification** join | `evaluate_detections.py:1183–1187`; library `:4795` (`assign_points_to_tiles`, `check_tile_join_invariant`, `:4869–4873`) | whether every interval, coverage block, and the tile block are computed at all, or the cell is written in the withheld form (`_withheld_buffer_row`, `:947–1023`) |
| F1/precision/recall bootstrap, `bootstrap_ci` → `compute_per_tile_tp_fp_fn` on its **default** join (no join argument today; spec § 2 item 6) | `:1232–1240`; library `:3489–3655`, `:3563` | `f1_ci_*`, `p_ci_*`, `r_ci_*` and their methods; the `coverage` block via `_compute_coverage` (`:411–537`) |
| Tile classification, `calculate_tile_classification` and `bootstrap_tile_classification_ci`, under the **classification** join | `:1423–1461`; library `:4916`, `:5107` | the whole `tile_classification` block |
| Measured method census, `with_measured_bootstrap_method` | `:1803–1844`, called at `:1873` | `_metadata.bootstrap.method`, `methods_measured` |
| Writers | `:1896–2269` (CSV, Markdown), `write_batch_summary` (`:2343–2523`) | the sibling files |

No other function in `evaluate_detections.py` reads the per-tile table
or the join (search for `compute_per_tile`, `bootstrap_ci`,
`calculate_tile_classification`, `bootstrap_tile_classification_ci`,
`describe_tile_join_refusal`, `tile_join`, `processed_tiles`). In the
library, the other users of the table are `bootstrap_effect_size_ci`
(`:3819`, `:3823`), `bootstrap_multi_run_ci` (`:4004`),
`bootstrap_multi_run_effect_size_ci` (`:4117`, `:4124`),
`bootstrap_interaction_ci` (`:4339`), `compute_per_tile_classification`
(`:3170`), `score_detection_set` (`:3305`), and
`bootstrap_tile_effect_size_ci` (`:5351`, `:5355`). None of them writes
`evaluation.json`; they feed other artefacts (pairwise effect sizes,
tiering, permutation tests, the Pareto and leaderboard builders), which
are Wave 3's, not this schema's. `compute_per_tile_tp_fp_fn` alone is
called from 28 other scripts and `calculate_tile_classification` from 16,
`evaluate_detections.py` included (a `grep` of `scripts/*.py`); that list is the downstream reach.

### 3.2 Target set (determined by the classification join or the count table)

In `summary` and in each `per_run[]` entry:

- `tile_classification`, whole: `confusion` {`tp`, `tn`, `fp`, `fn`};
  `mcc`, `sensitivity`, `specificity`, each {`point`, `mean`,
  `ci_lower`, `ci_upper`, `method`}; `tile_join`; on aggregates also
  `n_runs`, `n_runs_defined` per metric, `confusion_source`; in the
  withheld form `withheld`, `withheld_reason`, `withheld_detail`,
  `withheld_quantities`, `tile_join_diagnostics`, and on aggregates
  `n_runs_withheld` (`:238–396`, `:1439–1461`).
- `tile_join_withheld`, present or absent, whole (and
  `n_passes_withheld`, `n_passes` on aggregates; `:1419–1420`,
  `:1724–1733`).
- Each `buffers[]` row: `f1_ci_lower`, `f1_ci_upper`, `f1_ci_method`,
  `p_ci_lower`, `p_ci_upper`, `p_ci_method`, `r_ci_lower`, `r_ci_upper`,
  `r_ci_method`; `coverage` {`n_zero_count_tiles`, `zero_fraction`,
  `coverage_status`; and, only through the block's presence or absence,
  `n_tiles`, `threshold`, `coverage_source`, `n_processed_tiles`,
  `n_unprocessed_tiles`, `coverage_detail`}; `coverage_status`,
  `ci_unreliable`, `ci_excludes_point`, `sparse_coverage`,
  `ci_flag_basis`; the withheld form's `ci_withheld`,
  `ci_withheld_reason`, `ci_withheld_detail` (`:947–1023`,
  `:1321–1352`).
- Aggregated rows also: `ci_zero_fraction`, `ci_n_tiles`,
  `ci_withheld_n_passes` (`:1569–1673`).
- Roll-ups: `ci_unreliable_any_buffer`, `coverage_status`
  (`:1390–1404`, `:1697–1711`).
- `_metadata.bootstrap.method`, `_metadata.bootstrap.methods_measured`;
  `_metadata.cli_args.tile_join`; and the provenance W1.1 adds
  (`count_table_join`, and the D72/D73 pointer).
- Siblings: in `evaluation.csv` the columns `f1_ci_lower`,
  `f1_ci_upper`, `p_ci_lower`, `p_ci_upper`, `r_ci_lower`, `r_ci_upper`,
  `mcc`, `mcc_ci_lower`, `mcc_ci_upper`, `sensitivity`, `specificity`,
  `mcc_boot_mean`, `sensitivity_boot_mean`, `specificity_boot_mean`,
  `coverage_status`, `ci_unreliable`, `ci_zero_fraction`, `ci_n_tiles`
  (and the MCC column group's presence; `:1926–2009`); in
  `evaluation.md` every CI cell, the MCC, MCC CI, Sens, and Spec cells,
  and the withheld, partial-coverage, sparse-coverage, and undefined-MCC
  footnotes (`:2011–2269`); in `batch_summary.csv` and `.json` the same
  interval and MCC columns.

### 3.3 Non-target set

`version`; `summary.label`, `n_detections`, `n_runs`,
`detection_scope` (D50's scope, computed before any join); in each
buffer row `buffer_metres` and the point estimates and their legacy
aliases `f1`/`f1_point`, `precision`/`p_point`, `recall`/`r_point`; in
`coverage`, `n_tiles`, `threshold`, `coverage_source`,
`n_processed_tiles`, `n_unprocessed_tiles`, `coverage_detail` whenever
the block exists (they come from the frame and the processed-tile record,
not the table); in `_metadata`, everything except the fields in § 3.2;
in the CSV the `label`, `buffer_metres`, `f1`, `precision`, `recall`,
`coverage_source`, `n_unprocessed_tiles` columns; in the Markdown the
header lines and the F1, P, R cells.

**Changing on every run, excluded from byte comparisons** (not drift):
`timestamp`; `_metadata.generated_at_utc`, `script_git_commit`,
`script_git_status`, `input_git_state` (head and states depend on the
checkout), `cli_args.output_dir`; the Markdown "Generated" line.

### 3.4 Writers other than the scorer

Of the 2,829 files, 2,769 record `scripts/evaluate_detections.py` as
their writer, 5 record `scripts/compute_corrected_f1_multi_buffer.py`
(all under `results/stride55-2026-08-27/`), and 55 record no writer (24
under `results/verifier-t-pilot/`, 12 `results/retest/`, 8 each under
`results/55maps-extended-gt-2026-06-07/` and
`results/55maps-standardised-ref-2026-08-14/`, 2 under
`results/gemini37-55map-2026-08-31/`, 1 under
`results/gemini37-fourth-cell/`). Their schema was not traced field by
field; Wave 2 must check each writer's output shape before re-scoring
it.

## 4. Census and worklist

**Scripts** (zbook, 2026-11-18; read-only; the data root
`~/Code/map-reader-llm` at `e92d1c5d7` supplies gitignored inputs):
`scripts/census_extract.py` (facts of each file),
`scripts/census_detections.py` (opens each recorded detection input,
resolving directories with the scorer's own `resolve_pool_passes`), and
`scripts/build_worklist.py` (rules in its header; output
`reports/tile-join-wave-1/worklist.json`, 2,829 entries).

### 4.1 Recount against the specification

| Count | Specification (W1.0) | Recounted (`git ls-files` at `e92d1c5d7`) | Match |
|---|---:|---:|---|
| Files named exactly `evaluation.json` | 2,817 | 2,817 | yes |
| `results/retest/*-evaluation.json` | 12 | 12 | yes |
| All, by suffix | 2,829 | 2,829 | yes |
| … containing `tile_classification` | 2,646 | 2,646 by text match; **2,641** with a `summary.tile_classification` block | see note |
| … of those under `archive/` | 33 | 33 | yes |
| Files under `archive/` in all | — | 54 | — |

Note: the 5 files that mention `tile_classification` but carry no block
are `results/pairwise/tile-size-30m/{512px-image-t0, 512px-image-t07,
512px-text-t0, 512px-text-t07, eval-512-on-384-image-t0}/evaluation.json`.
They were scored without `--mcc` and name `tile_classification` only in
`summary.tile_join_withheld.withheld_quantities`: they are withheld cells
(§ 4.3).

### 4.2 Classification

| Facet | Counts (2,829 files) |
|---|---|
| Frame (`bounds`, D22 chain) | 384 px full 1,107; 512 px full 739; 55-map 331 (+1 recorded as an absolute path, `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`); Era-2 B intersection 254; null-exemplar reduced Era-2 153 and Era-1 82; grid common 64; H10 test 40; 256 px full 16; H13 common 3 and arms A/B/C 1 each; **unrecorded 36** |
| Construction route | merged 2,170; unmerged 433; unknown 226 |
| Replication | single 2,618; replicated (`per_run` ≥ 2) 211 |
| Recorded classification join | `id` 1,144 (1,049 in both the tile block and `cli_args`, 95 in `cli_args` only); none 1,685; no sheet-specific join anywhere |
| Recorded count-table join | none in any file (as § 2 item 3 of the specification says) |
| Paper-cited | 761: 624 by signed register rows, 322 under directories `docs/paper/` names (overlapping) |

**Route basis** (`build_worklist.py` header): a merge field in the
detection input (`vote_count`, `cluster_size`, `source_tiles`,
`origin_tiles`) → merged; exactly the raw detector schema, or an Era-1
stage-D `-single-` pass → unmerged; no merge field but a path naming a
merging product → merged, recorded as such; otherwise unknown. Unknowns:
96 whose input could not be opened, 54 materialisations carrying only
`source_tile` (older materialisers dropped the lists; spec W1.0) whose
paths do not name a merging product, 47 Era-1 proposer-verifier accepted
files (`majority_vote_fraction`, `verifier_votes`), 26 null-exemplar
cells whose recorded source is one of the latter, and 3 others. Of the
paper-cited files: merged 547, unmerged 135, unknown 79 (54 `source_tile`
only, 25 proposer-verifier accepted).

**Paper citation** was determined as follows. The register is
`results/run-analyses.json` (71 rows; 45 with `signature.status`
`signed`). Each signed row's `conditions_compared` was resolved to
`eval_path` through `results/run-conditions.json` (all resolved; 624
distinct tracked files). `docs/paper/*.md` names 14 existing
directories; files under 5 of them are evaluations
(`results/leaderboard/era2/gs-era2-verified-board-2026-09-10` 210,
`results/55map-final-board-r2-2026-09-06` 59,
`results/paper-eval/phase2/512px-14buf-mcc` 36,
`results/55maps-standardised-ref-2026-08-14` 9,
`results/stride-2026-08-25` 8). No `docs/paper/` file names an
`evaluation.json` directly.

### 4.3 Worklist status totals

| Status | All | Paper-cited |
|---|---:|---:|
| `already-migrated` | 0 | 0 |
| `reproducible-legacy` | 2,445 | 758 |
| `known-withheld` | 49 | 3 |
| `unresolved-recipe` | 281 | **0** |
| `historical-only` (`archive/`) | 54 | 0 |

**Every paper-cited file has a status other than `unresolved-recipe`.**
The three paper-cited withheld files are the W1.4 cells.

The 49 `known-withheld` files: the three 3.7 cells, their three
null-exemplar counterparts, the five `tile-size-30m` cells above, and 38
under `results/uplift-supplement/` (36 in `k1-gapfill/`, 2 in
`verifier-pairing/`), all with reason `tile_join_detection_shortfall`
under `id` where recorded. Only the three 3.7 cells are in W1.4; **the
other 46 are withheld cells the specification does not mention**
(open question 5).

The 281 `unresolved-recipe` files: 232 null-exemplar sensitivity cells
(their detection files are gitignored derivatives, absent on zbook, and
regenerable from `detections_manifest.json`; regeneration not tried), 24
`results/verifier-t-pilot/` and 12 `results/retest/` (no recipe at all;
the retest files carry no `_metadata`), 12
`results/deployment-oracle-2026-06-06/preverifier-eval/` and 1
`results/rescore-2026-05-31/` (detection input absent on zbook). None is
paper-cited.

"Frozen" was taken as `archive/` only. No evaluation file lies under the
S166 historical-comparison directories (`results/tile-join-audit/`,
`results/k-ladder-2026-09-12/mcc-join-2026-10-30/`); whether any other
live directory should count as frozen under D73 (5) is open question 6.

## 5. Smoke cells 3–5, pinned

| # | Cell (evaluation file) | Why it qualifies |
|---|---|---|
| 3 | `results/paper-eval/phase2/512px-14buf-mcc/p2c-image-canonical/evaluation.json` | Era-1 512 px frame (`inputs/vectors/bounds/full_evaluation_bounds.geojson`); paper-cited both ways (signed rows `uplift-supplement-flatten`, `null-exemplar-sensitivity-2026-09-13`; directory named in `docs/paper/`); **unmerged** by route (raw detector schema); single; has a tile block and intervals; `reproducible-legacy` |
| 4 | `results/grid-2026-08-18/conditions/g512_ov064/eval/evaluation.json` (the spec's candidate, `grid-2026-08-18::g512-ov064-k10-c1-k8`, confirmed through `results/run-conditions.json`) | Grid common frame; paper-cited (signed rows `grid-tilesize-overlap-2026-08-18`, `uplift-supplement-flatten`); merged (merge fields present); single; records `id`; one buffer (20 m) |
| 5 | `results/paper-eval/n1/384px-14buf-mcc/pro-rerun/pro-image-high-t-0-0/evaluation.json` | Replicate-mean, `per_run` 3; paper-cited (signed rows `h6-a06-decision-rule`, `h6-a09-cost-gate`, `uplift-supplement-flatten`); **unmerged** by route; 384 px Era-1 frame, a frame no other smoke cell uses |

The specification's other candidate,
`outputs/era1-pv-stage-d/512-single-image-t0.0/eval_t0.1/evaluation.json`,
is not paper-cited by the rule above (no signed row names it and no
`docs/paper/` directory contains it), so it was not used. Across cells
1–5, cells 3 and 5 are unmerged by construction route, as required.

## 6. Recipe and input identity (all eight smoke cells)

Recovered with the existing `scripts.rescore_tile_mcc_e81.recover_recipe`
(D22) and `evaluate_detections.find_detection_files`, by
`scripts/replay_smoke.py`. Record: `scripts/out/smoke_replay.json` (full
SHA-256 and git blob of every input; argv; run order). Every cell: seed
42, 10,000 BCa draws, `scipy.stats.bootstrap`.

| # | Recorded join | Buffers | Detection input(s), run order | Generating commit | Input identity |
|---|---|---|---|---|---|
| 1 | none (→ `id`) | 14 | `results/k-ladder-2026-09-12/phase2/materialised/pv-high-image-t0.3-n1-opmax.geojson` | `f724b7a10` | all 3 git blobs equal the recorded `blob_hashes` |
| 2 | none (→ `id`) | 14 | `results/55map-final-board-r2-2026-09-06/cells/A-N1-oracle/detections.geojson` | `7894b5b5a` | no hashes recorded; all 3 blobs equal the blobs at `7894b5b5a` |
| 3 | none (→ `id`) | 14 | `outputs/retest/phase2c/track1-image/canonical/run_1/detections_canonical_run01.geojson` (glob `*/detections_*.geojson`) | `349cdd1b6` | none recorded; all 3 equal the blobs at `349cdd1b6` |
| 4 | `id` | 20 m | `results/grid-2026-08-18/conditions/g512_ov064/detections.geojson` | `unknown` | all 3 equal the recorded `blob_hashes` |
| 5 | none (→ `id`) | 14 | `outputs/h11/n1-pro-rerun-384/pro-image-high-t0/run_{1,2,3}/detections-library_plus-hp-3.1-pro-2026-06-03.geojson`, in that order | `349cdd1b6` | none recorded; all 5 equal the blobs at `349cdd1b6` |
| 6–8 | `id` | 14 | `results/k-ladder-2026-09-12/phase2/materialised/g37-text-{k1-verified-carried-p0.10-k1, k1-verified-opmax, k3-verified-opmax}.geojson` | `8654d741f` | all equal the recorded `blob_hashes` and the blobs at `8654d741f` |

Environment: zbook, Python 3.13.3, NumPy 2.4.3, SciPy 1.17.1, scorer at
`e92d1c5d7` (the data root's checkout; `scripts/` and `tests/` identical
to `fe9d433d7`). D50 scope in every replay: no out-of-frame and no
unattributed in-frame detection (cells 1–5); cells 2, 3, and 5 carry no
origin columns and are attributed by `source_tile`.

## 7. Determinism: legacy replays under the recorded rules

Each cell was re-scored by the unchanged scorer under its recorded rules
(join as recorded, `id` where none is recorded), into
`~/scratch/wave1/w10/replay/cell<N>/`, and compared field by field with
the committed file, excluding only the fields that change on every run
(§ 3.3).

| # | Outcome | Committed intervals and tile block | Differences |
|---|---|---|---|
| 1 | **reproduces** | every interval, method, coverage flag, and the tile confusion (TP 204, TN 241, FP 17, FN 25; MCC 0.827) equal | 2, both keys the current scorer adds and the committed file predates: `summary.detection_scope`, `summary.tile_classification.tile_join` |
| 2 | **reproduces** | equal (TP 2,424, TN 4,847, FP 165, FN 1,105; MCC 0.7006) | the same 2 added keys |
| 3 | **reproduces** | equal | the same 2 added keys |
| 4 | **reproduces** | equal | 0 |
| 5 | **reproduces** | equal, in all three passes and the aggregate | 7: the same added keys in `summary` and each of the 3 `per_run` entries |
| 6 | **reproduces: the recorded refusal** | `tile_join_detection_shortfall` under `id`, 22 of 526 booked; point estimates equal | 0 |
| 7 | **reproduces: the recorded refusal** | the same refusal, 21 of 475 | 0 |
| 8 | **reproduces: the recorded refusal** | the same refusal, 20 of 467 | 0 |

No interval differs in any cell, and `_metadata.bootstrap` (method and
measured methods) is equal in all eight. **No cell has drifted.** The
added keys are schema additions (D50's scope block and the tile block's
join field), not value changes; Wave 2's comparison must treat a
key absent from an older committed file as "not recorded", not as drift.
No corrected (sheet-specific) score was computed for any cell.

## 8. Timings for the cost model

Measured on zbook, all eight replays at once (8 of 32 cores busy), each
the scorer's full recorded recipe (all buffers, 10,000 draws, tile
block). Per-cell CPU and peak memory from `os.wait4` on the child.

| # | Tiles (frame) | Passes | Buffers | Wall (s) | CPU (s) | Peak RSS (MB) |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 487 | 1 | 14 | 19.24 | 20.51 | 295 |
| **2 (55-map)** | **8,541** | 1 | 14 | **131.33** | **133.86** | **2,095** |
| 3 | 340 | 1 | 14 | 26.84 | 28.46 | 271 |
| 4 | 487 | 1 | 1 | 2.68 | 4.19 | 292 |
| 5 | 487 | 3 | 14 | 56.33 | 57.86 | 296 |
| 6 | 487 | 1 | 14 (refusal) | 6.56 | 8.64 | 221 |
| 7 | 487 | 1 | 14 (refusal) | 6.03 | 7.33 | 220 |
| 8 | 487 | 1 | 14 (refusal) | 6.26 | 9.16 | 224 |
| all | | | | 131.88 | 270.03 | |

(Frame tile counts are from the parent record § 2.4 for 487, 340, and
8,541; cell 3's frame is the 512 px full frame of 340 tiles.) These are
legacy replays with the existing code; the new joins' costs are not yet
measurable. For the main session's projection: the scorer is
single-threaded per cell (CPU ≈ wall), a 55-map cell needs about 2.1 GB,
so 14 concurrent 55-map cells would need about 29 GB of zbook's 31 GB.
Wave 2 per file will be at least a legacy replay plus a new-rules run
plus an idempotence rerun.

## 9. Stop-list items checked

| § 5 item | Checked | Result |
|---|---|---|
| Unresolved row in the 3.7 eligibility table | yes | none (24 rows resolved) |
| The 55-map GS check finding a cross-sheet contact on map content | yes | **found; the stop** (§ 2; stop record) |
| A legacy replay mismatch, or an unexpected refusal | yes, for the eight smoke cells | none: all reproduce; the three refusals are the recorded ones |
| An in-frame detection without an attributable sheet in any smoke cell | yes, from the replays' D50 scope | none (`n_unattributed_in_frame` 0 in all five non-refused cells and the three 3.7 cells) |
| A write outside the scratch copy, the Wave 1 branch, or `reports/tile-join-wave-1/` | yes | none to files. The replays ran the data root's scorer with `PYTHONDONTWRITEBYTECODE=1` and wrote only to `~/scratch/wave1/w10/`; `git status` of the data root stayed clean. One `git fetch` was run in the data root's checkout, which updates the object store that its worktrees (including this branch's) share |
| Any decision this specification does not cover | yes | note A of `withheld-37.md` (flagged); the 46 withheld cells outside W1.4 and "frozen" outside `archive/` (open questions 5 and 6) are reported, not decided |
| G1 items, count sums, tier 1 | no | belong to W1.1–W1.5 |

## 10. Open questions

1. The seam ruling (stop record § 4, item 1).
2. Note A in `withheld-37.md`.
3. The 18 ambiguous contacts on r2.
4. Route `unknown` for 79 paper-cited files (54 `source_tile`-only
   materialisations, 25 Era-1 proposer-verifier accepted sets): their
   builders should be checked before Wave 2 relies on the route.
5. 46 `known-withheld` files outside W1.4 (`results/uplift-supplement/`
   38, `results/pairwise/tile-size-30m/` 5, null-exemplar counterparts
   3): does the D73 (4) rule apply to them, or do they simply re-score?
6. Whether any live directory besides `archive/` counts as frozen under
   D73 (5).
7. One evaluation records its bounds as an absolute path.

## Changelog

### 2026-11-19 — Seam counts corrected; claims made precise

Trigger: Astra's reviews (`~/agent-mail/codex/outbox/claude/20261118T130529Z-astra-seam-measurement-counting-finding.md`,
`…/20261118T130721Z-astra-e93-seam-paragraph-review.md`), verified by
this agent (26 distinct pairs among r2's 32 map-content contacts, and the
six duplicated references, recomputed from the committed summary).
`seam_second_copy.py` fixed and re-run on zbook (`57a4ac33a`).

| Item (§ 2.2) | Before | After |
|---|---|---|
| (a) "references added", r2 map content / + ambiguous | 32 / 50 (contacts) | **26 / 40** references; 32 / 50 contacts kept beside them |
| the same, canonical r50 | 4 / 23 | 4 / **20** |
| the same, student-reviewed | 33 / 49 | **27 / 40** |
| the same, student | 35 / 50 | **29 / 41** |
| (c) on r2 | 333 tiles; 11 map content; the rest called padding | 333 = 11 map content + 6 ambiguous + 316 confirmed padding + 0 remainder |

Also: Astra's pixel audit recorded (all 50 r2 contacts reproduced; zero
rotation; `student:04282`'s two contacts unresolved under the
nearest-pixel-centre sensitivity); §§ 0 and 2 reworded to separate the
measured proximity fact, the inspected examples, and the unadjudicated
candidates, and the symbol-level from the tile-level effect. Unchanged:
every tile count, the stop, and §§ 3–10.

### 2026-11-18 — Steps 3–8 completed after the stop; seam measurement added

Trigger: the main session's instruction to resume the read-only W1.0
steps while the wave stays stopped on the seam ruling (stop record § 3).
Added § 2.2 (second-copy counts for options (a)–(d)); completed § 3
(schema); added §§ 4–10 (census and recount, worklist, smoke cells 3–5,
recipes, determinism, timings, stop list, open questions); rewrote § 0.

| Item | Before | After |
|---|---|---|
| Status | stopped at step 2; steps 3–8 not started | stopped on the seam ruling; steps 3–8 done |
| Census | not started | 2,829 files, matching the specification's 2,817 + 12; 2,646 text matches for `tile_classification` (2,641 blocks) |
| Worklist | not written | `worklist.json`: 2,445 reproducible-legacy, 49 known-withheld, 281 unresolved-recipe (none paper-cited), 54 historical-only |
| Determinism | not run | all eight smoke cells reproduce their committed intervals and confusions, or their recorded refusal |

Unchanged: the stop, § 2's sheet-check results, and the eligibility
table.

### 2026-11-18 — Original publication

Written by the Wave 1 census agent at the stop. W1.0 steps 1 and 2 done;
step 3 partial; steps 4–8 not started. The 55-map sheet check found
cross-sheet contacts on map content (§ 2), a § 5 stop.
