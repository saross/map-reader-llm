# Staging report — 2023 participatory-GIS baseline

> **Last revised**: 2026-09-01 (initial staging of the 2017/2018 volunteer
> digitisation corpus into anonymised, analysis-ready layers).
> Refer to [§ Changelog](#changelog) for revision history.

This document records how the raw 2023 participatory-GIS deposit was turned
into the anonymised layers in this directory, every transformation applied,
and the verification results that came out of the process.

**Anonymity contract.** Nothing in this directory contains a volunteer's
personal name. Digitisers are identified only by the paper's own codes —
`A`–`E` (2017 season), `F`–`I` (2018 season), and `TESTER-1` for the single
staff account. The de-anonymisation key lives at
`inputs/student-baseline-2023/raw/code-mapping.json`, inside the gitignored
`raw/` directory, and must never be copied out of it. The check that enforces
this is described in [§ 9](#9-name-leak-check).

---

## 1. Provenance

All source material was pulled read-only from the project's Google Drive into
`inputs/student-baseline-2023/raw/` and is documented, file by file with Drive
identifiers and byte-size verification, in `raw/MANIFEST.md`. That directory is
gitignored and is the only place volunteer names are permitted to exist.

Inputs consumed by this staging run:

| Raw input | Role here |
|---|---|
| `Student-coding-sheet__student-data.csv` | authoritative code -> person key |
| `Student-coding-sheet__2017.csv`, `__2018.csv` | per-season digitisation statistics, used to validate counts |
| `MapMounds17_18withnas.csv` | master point export (10,827 rows) |
| `MapMounds17_18allgood.csv`, `__NEgood.csv` | filtered variants, used for the membership flags |
| `Analysis-areas-by-student.shp` | audit-area polygons (8) |
| `Analysis-areas.shp` | the four audited map tiles |
| `Mound-count-by-student.shp`, `Error-count-by-student.shp` | per-polygon roll-ups, used as cross-checks |
| `QA-errors-SAR.shp` | 49 quality-assurance error points |
| `MapDigitisation__Sheet1.csv` | 2017 per-batch assignment log |
| `RecordingProgress__*.csv` | session and volunteer summaries, used for name-form reconciliation |
| `QA-time-on-task__*.csv` | staff quality-assurance workbook |
| `rawdata/Entity-*.csv`, `rawdata/MapDig_ALLfixedNE.csv` | device-level exports, used for name-form reconciliation and timestamp checks |

Two repository resources outside `raw/` were also used:

- `inputs/rasters/Russian1981_32635/*.tif` (55 sheets) — only for their
  georeferenced extents, to validate the sheet graticule and to recover
  settlement aliases for sheet numbers.
- `inputs/vectors/bounds/gs-4maps-sheet-bounds.geojson` — the four
  gold-standard sheet footprints.

The pipeline itself is in `inputs/student-baseline-2023/scripts/`
(`stage_01_mapping.py` ... `stage_09_leakcheck.py`, plus `sheetgrid.py`), run
under `.venv/bin/python`. Stages are independent and idempotent; stage 1 writes
into `raw/`, every other stage writes only into `staged/`.

---

## 2. Code mapping (stage 1)

`Student-coding-sheet__student-data.csv` is the authoritative key: it pairs each
of the paper's nine volunteer codes with a person and a season. The staged
layers use the bare letter (`A` ... `I`) rather than the paper's `Student A`
phrasing, so that the value is a clean categorical.

Reconciliation across the deposit found the same nine people written in several
different ways — full name, given name only, a shortened given name, initials,
and a spreadsheet key that concatenates the full name with a feature count. A
normalising matcher (NFKD, casefold, whitespace collapse, then exact full-name,
declared-nickname, surname, given-name, and single-character-substitution
passes) resolved **54 distinct normalised name forms across 15 source files
with zero unmatched forms**.

Ambiguities encountered and how they were resolved:

- **Two spelling variants between the coding sheet and the point data**, both in
  the 2018 cohort: one given name differs by a single letter, and one surname
  differs only in an internal capital. Both were bridged by the
  single-character-substitution pass and both are unambiguous (each cohort
  surname is unique). Feature counts confirm the identification: the resolved
  codes reproduce the published Table 2 counts exactly.
- **Shortened given names** in the 2017 assignment log (four of them) and
  **initials** in the session-hours tabs. These were declared explicitly in the
  matcher rather than inferred, because one of them is not a prefix of the
  registered given name.
- **Two staff-tester rows, one staff person.** The coding sheet lists a tester
  row in the 2017 tab (11 features) and another in the 2018 tab (21 features).
  The point data shows a single staff account behind both, totalling the 32
  staff features the paper reports. One code, `TESTER-1`, is therefore used for
  both seasons; `season` is recorded as `0` for that record.
- **Non-name cells in name columns.** The Drive-to-CSV conversion left markdown
  table separators and roll-up labels ("Cumulative", "Overall", block
  sub-headers) inside the same columns as names. These are filtered before
  matching and are not treated as unmatched forms.

Output: `raw/code-mapping.json` (10 codes; per-code canonical name, surname,
given name, season, role, and every observed variant form; plus a normalised
lookup table with 54 entries). **This file stays in `raw/`.**

---

## 3. Master point layer (stage 2)

**Output**: `mounds-attributed.geojson` — 10,827 features, EPSG:4326.

Source: `MapMounds17_18withnas.csv`, confirmed in `raw/MANIFEST.md` as the
export that corresponds to the local `inputs/gis-map-mounds/MapMounds4326.shp`
(shapefile identifiers are a strict subset; the CSV carries two extra rows).

### 3.1 Schema

| Column | Type | Derivation |
|---|---|---|
| `identifier` | int | source `identifier`, unique across all 10,827 rows |
| `student_code` | string | source `createdBy` mapped through the code key |
| `created_at_gmt` | string | source `createdAtGMT`, ISO 8601 with trailing `Z` |
| `modified_at_gmt` | string | source `modifiedAtGMT`, ISO 8601 with trailing `Z` |
| `feature_type` | string | source `FeatureType`, verbatim |
| `map_symbol` | string | source `MapSymbol`, verbatim |
| `year` | int | calendar year of `createdAtGMT` (2017 or 2018) |
| `in_allgood` | bool | `identifier` present in `MapMounds17_18allgood.csv` |
| `in_negood` | bool | `identifier` present in `MapMounds17_18NEgood.csv` |
| `geometry` | Point / null | `Longitude`, `Latitude` as EPSG:4326 |

### 3.2 Transformations and drops

- **Name-bearing columns dropped**: `createdBy`, `modifiedBy`, `FeatureAuthor`.
  These are the only three columns in the export that carry personal names; the
  free-text columns (`Note`, `Description`, `OtherDescription`,
  `Classification`) were scanned token by token against the full name set and
  contain none.
- Also dropped, as not requested and not needed downstream: `uuid`, `ID`,
  `FeatureTimestamp`, `Latitude`, `Longitude`, `Northing`, `Easting`,
  `Accuracy`, `Source`, `Note`, `GC`, `DateCompleted`, `Description`,
  `Classification`, `OtherDescription`, `Picture`, `geospatialcolumn`.
  (`Accuracy`, `Classification`, `OtherDescription`, `Picture` and
  `Description` are empty in every row; `Source` and `GC` are constant.)
- **Null geometry, not (0, 0)**: 205 rows have no latitude/longitude. These are
  the paper's recoverable form-completion omissions, not detection failures.
  They are retained with a null geometry so the layer still totals 10,827.
- `in_allgood` is true for 10,622 rows and `in_negood` for 10,632, matching the
  row counts of the two filtered variants exactly.
- **Attribution cross-check**: `createdBy` and `FeatureAuthor` resolve to the
  same code in all 10,827 rows (zero disagreements).

### 3.3 Counts per code per year

| Code | 2017 | 2018 | Total | Null geometry |
|---|---:|---:|---:|---:|
| A | 2,302 | 0 | 2,302 | 0 |
| B | 1,799 | 0 | 1,799 | 36 |
| C | 1,615 | 0 | 1,615 | 2 |
| D | 1,526 | 0 | 1,526 | 136 |
| E | 1,090 | 0 | 1,090 | 18 |
| F | 0 | 1,305 | 1,305 | 3 |
| G | 0 | 810 | 810 | 10 |
| H | 0 | 335 | 335 | 0 |
| I | 0 | 13 | 13 | 0 |
| TESTER-1 | 11 | 21 | 32 | 0 |
| **Total** | **8,343** | **2,484** | **10,827** | **205** |

Every cell reproduces the published Tables 1 and 2 exactly, including the
per-student latitude/longitude omission counts (2017 total 192, 2018 total 13).
This is an independent confirmation that the code mapping is correct.

### 3.4 The FeatureTimestamp question — no local-time quirk observed

`FeatureTimestamp` was checked against `createdAtGMT` in the master export and
in all four device-level exports under `raw/rawdata/`. **No offset of hours was
found anywhere.** Rounded to the nearest hour, the difference is zero for all
10,827 master rows and for all 2,484 rows of the three per-device exports.

The residual offset is sub-minute and always positive (`createdAtGMT` later
than `FeatureTimestamp`): minimum 3.7 s, median 10.9 s, mean 11.3 s, maximum
42.7 s. That is the interval between the app capturing the position and the
record being written, not a time-zone problem. Bulgaria was on UTC+3 during
both September field seasons, so a local-time quirk would have shown as a clean
three-hour offset; it does not appear. `FeatureTimestamp` was nonetheless
dropped from the staged layer, since `created_at_gmt` carries the same
information with better precision.

---

## 4. Assignment-area polygons (stage 3)

**Output**: `assignment-areas.geojson` — 8 polygons, EPSG:4326.

Columns: `id` (source identifier), `student_code`, `area_role`, `sheet_id`,
`share_of_polygon_in_sheet`, `area_km2`, `geometry`.

### 4.1 Why there are eight polygons and only four codes

`Analysis-areas-by-student.shp` is **not a per-student assignment layer for the
nine-person cohort**. It is the quality-assurance geometry for the four-sheet
audit reported as the paper's Table 3. The 9-versus-8 discrepancy in the task
framing dissolves once the layer's real content is examined: five of the eight
polygons are audit areas belonging to four codes, and the remaining three are
sub-polygons delimiting contiguous sections one student failed to digitise.

| `id` | Code | Role | Sheet | Area (sq km) |
|---:|---|---|---|---:|
| 1 | B | audit area | K-35-052-4_32635 | 380.493 |
| 3 | C | audit area | K-35-062-2_Rakovski | 381.644 |
| 4 | D | audit area | K-35-078-1_Lesovo | 383.528 |
| 10 | C | audit area | K-35-053-3_Elenovo | 95.893 |
| 11 | A | audit area | K-35-053-3_Elenovo | 283.743 |
| 100 | C | missed swath | K-35-062-2_Rakovski | 16.527 |
| 101 | C | missed swath | K-35-062-2_Rakovski | 9.582 |
| 102 | C | missed swath | K-35-062-2_Rakovski | 6.778 |

Codes `E`, `F`, `G`, `H`, `I` and `TESTER-1` have no polygon because they were
never audited. Code `C` has two audit polygons because C worked on two of the
four audited sheets. The three missed-swath polygons total 32.887 sq km, 8.6 %
of the Rakovski sheet, and sit entirely inside C's Rakovski audit area — they
are the sub-tile coverage holes behind that student's error rate.

**Cross-check against the roll-up layers.** `Mound-count-by-student.shp` gives
per-polygon feature counts of 227 (A), 203 (B), 244 + 61 = 305 (C) and 64 (D);
`Error-count-by-student.shp` gives 3, 6, 33 + 2 = 35 and 5. Both reproduce the
published Table 3 rows exactly, which independently confirms the code mapping
for the four audited students.

### 4.2 Inside-fraction cross-check

Because these are audit areas rather than assignments, the meaningful test is
not "what fraction of a student's points fall inside their polygon" (each
student worked eight to eleven sheets, of which at most two were audited) but
"how pure is each polygon". Both are reported.

| Code | Polygon area (sq km) | Own points (with geometry) | Own points inside | Fraction inside | All points inside | Purity |
|---|---:|---:|---:|---:|---:|---:|
| A | 283.7 | 2,302 | 227 | 9.86 % | 227 | 100 % |
| B | 380.5 | 1,763 | 203 | 11.51 % | 203 | 100 % |
| C | 477.5 | 1,613 | 305 | 18.91 % | 305 | 100 % |
| D | 383.5 | 1,390 | 47 | 3.38 % | 47 | 100 % |

**Every audit polygon is 100 % pure**: not one feature inside any of the five
audit polygons was created by a code other than the polygon's own. The low
fraction-inside values are expected and correct — they are the share of each
student's whole season that fell within the audited sheets.

D's 47 rather than 64 is the null-geometry effect: the Lesovo batch
(identifiers 205826–205889) contains exactly 64 records attributed to D, of
which 17 have no coordinates. The staff audit counted records (64, as published);
a spatial count can only reach 47.

---

## 5. Quality-assurance error layer (stage 3)

**Output**: `qa-errors.geojson` — 49 points, EPSG:4326.

### 5.1 CRS decision

`QA-errors-SAR.shp` arrives with no `.prj` sibling and geopandas reports
`CRS: None`. Coordinate ranges are x 24.75202 to 26.73117 and y 41.84858 to
42.48736 — decimal degrees squarely inside the Bulgarian envelope. The same
ground in EPSG:32635 would read roughly 380,000–480,000 easting and
4,650,000–4,770,000 northing, six and seven digits respectively. **CRS assigned:
EPSG:4326**; no reprojection was needed, and the points land on the correct
audit polygons, which is an independent confirmation.

### 5.2 Staged schema

| Column | Type | Notes |
|---|---|---|
| `error_id` | int | source `AUTO`; values 1–23, 25–49, 101 |
| `symbol` | string | source `Symbol`, verbatim (capitalisation is inconsistent in the source) |
| `error_type` | string | source `ErrorType`: false negative, double-marked, false positive |
| `student_code` | string | preferred attribution: spatial where available, otherwise the recorded one |
| `student_code_recorder` | string | source `Recorder` mapped through the code key |
| `student_code_spatial` | string | code of the audit polygon the point falls inside |
| `sheet_id` | string | source `Map`, normalised to the four canonical sheet identifiers |
| `map_label_corrected` | bool | true where the source `Map` string needed correcting |
| `year_recorded_raw` | int | source `Year`, verbatim, uncorrected |
| `note` | string | source `Note`, verbatim |
| `geometry` | Point | EPSG:4326 |

### 5.3 Error distribution

| Error type | K-35-052-4 | Elenovo | Rakovski | Lesovo | Total |
|---|---:|---:|---:|---:|---:|
| False negative | 6 | 5 | 27 | 4 | 42 |
| Double-marked | 0 | 0 | 6 | 0 | 6 |
| False positive | 0 | 0 | 0 | 1 | 1 |
| **Total** | **6** | **5** | **33** | **5** | **49** |

### 5.4 Source-data defects found and how they are handled

- **The `Recorder` attribute mis-attributes two errors.** On the Elenovo sheet
  the recorded attribution gives A 1 and C 4; the spatial attribution against
  the audit polygons gives A 3 and C 2. The spatial reading is the correct one:
  it reproduces `Error-count-by-student.shp` (A 3, C 2) and the published
  Table 3 (A 3, C 35 combined) exactly, whereas the recorded attribution does
  not. Both are kept in the staged layer, with `student_code` defaulting to the
  spatial value. On the other three sheets the two agree completely.
- **Two `Map` labels were wrong.** One row carries a leading `N-` where the
  sheet number begins `K-`, and one carries the sheet number of the Elenovo
  sheet with a different settlement name appended. Both are corrected in
  `sheet_id` and flagged by `map_label_corrected`.
- **The `Year` attribute is unreliable.** All six K-35-052-4 rows carry a 2018
  season value (one of them mistyped as 2108), but every feature on that sheet
  was created in September 2017 according to the point layer and the assignment
  log. The field is staged verbatim as `year_recorded_raw` and should not be
  used; the point layer's `year` is authoritative.

---

## 6. Sheet-to-student verification (stages 3 and 4)

### 6.1 The sheet graticule — a correction worth recording

An initial pass assigned points to sheets by spatial join against the local
GeoTIFF footprints. **That is wrong and produced badly inflated multi-student
counts.** Every raster in `inputs/rasters/Russian1981_32635/` is an axis-aligned
bounding box in EPSG:32635, so neighbouring sheet footprints overlap: 162
overlapping pairs totalling 3,295.9 sq km. Edge features were being assigned
arbitrarily, which manufactured apparent sheet sharing between students who in
fact worked adjacent sheets.

The staged analysis instead uses a true, exactly tessellating 1:50,000 Soviet
nomenclature graticule built in `scripts/sheetgrid.py`:

```text
1:1M sheet K-35   : row K = 40-44 N, column 35 = 24-30 E
1:100k sheet -NNN : 12 x 12 inside it, 30' longitude x 20' latitude,
                    numbered left to right then top to bottom
1:50k quarter -q  : 1 NW, 2 NE, 3 SW, 4 SE; 15' longitude x 10' latitude
```

The graticule was validated against all 55 local rasters: every raster's
footprint contains at least 99 % of its corresponding graticule cell, with zero
mismatches. Every one of the 10,622 geometried points falls inside exactly one
cell.

### 6.2 Sheets per student code, from the 2017 assignment log

`MapDigitisation__Sheet1.csv` holds **54 batch rows plus one totals row**. Each
row records a sheet, a digitiser given name, and an identifier range. Batch
identifier ranges span 202000–211206 and resolve entirely to the 2017 season;
**the log contains no 2018 rows at all.**

| Code | Log rows | Distinct sheet labels | Distinct graticule cells | Logged points |
|---|---:|---:|---:|---:|
| A | 14 | 11 | 11 | 2,289 |
| B | 11 | 9 | 10 | 1,761 |
| C | 11 | 8 | 9 | 1,684 |
| D | 11 | 8 | 8 | 1,540 |
| E | 7 | 6 | 6 | 1,091 |

The log's 42 distinct sheet labels resolve to 42 distinct graticule cells, but
not one-for-one: two labels are each used for two different cells (one
settlement name is applied to two adjacent sheets, and a second settlement name
is applied to one sheet that a different label also names). Consequently two
cells appear under two codes in the log purely because of the mislabelling —
these are label slips, not shared sheets.

Cross-checked against the point layer, the log's identifier ranges agree with
`createdBy` for **8,068 of the 8,339 covered points (96.75 %)**. The 271
disagreements are all block-boundary effects: a batch's identifier range was
allocated to one digitiser but partly consumed by another working concurrently
on the same device. The largest single case is 61 records inside one logged
batch that were created by a different student, which is exactly the Elenovo
sheet-sharing described below.

### 6.3 The four audited sheets — verdict

The task asked whether A↔Elenovo, B↔K-35-052-4, C↔Rakovski and D↔Lesovo hold.
Four independent lines of evidence were used: the audit polygons, the point
layer's own attribution, the quality-assurance workbook's per-tile table, and
the assignment log.

| Assumed alignment | Verdict | Evidence |
|---|---|---|
| B ↔ K-35-052-4 | **Confirmed** | 205 of 208 features on the sheet are B's; the audit polygon holds exactly 203 B features (Table 3's B row); all 6 errors attributed to B; the log gives the sheet to B alone |
| C ↔ Rakovski | **Confirmed** | 244 C features in the audit polygon; all 33 errors C's; all three missed swaths on this sheet; the log gives the sheet to C alone |
| D ↔ Lesovo | **Confirmed** | audit polygon holds 47 D features (64 records, 17 without coordinates); all 5 errors D's; the log gives the sheet to D alone |
| A ↔ Elenovo | **Confirmed but incomplete** | the sheet was digitised by **two** students, A and C |

**The Elenovo finding.** Sheet K-35-053-3 carries 291 features inside its
footprint: 228 from A and 63 from C (229/60 on the graticule cell). The audit
layer splits it into two adjacent polygons — 283.7 sq km assigned to A holding
227 features, and 95.9 sq km assigned to C holding 61 — which together partition
the sheet. The quality-assurance workbook records this explicitly: its per-tile
row for Elenovo reports 288 features identified and 5 errors (1.71 %), and its
per-student block splits that into A 227 / 3 errors and a separate C row
labelled with the Elenovo sheet, 61 features / 2 errors.

The consequence for the published table is that **Table 3's C row (305
identified, 35 errors) is not a single sheet**: it is 244 features and 33 errors
on Rakovski plus 61 features and 2 errors on Elenovo. And **Table 3's A row is
not the whole Elenovo sheet**: A's 227 features are 79 % of it. Per-sheet and
per-student error rates are therefore not interchangeable for these two
students — the sheet-level Elenovo rate is 1.71 % while A's own rate is 1.30 %.

This also explains the 61-record disagreement between the assignment log and
`createdBy` noted above: the log allocates identifiers 202534–202783 to A as
one Elenovo batch, but 61 of those 248 records were in fact created by C.

### 6.4 Reconciling 58 against 59 sheets

Counting distinct graticule cells occupied by the point layer:

| Threshold | Distinct sheets |
|---:|---:|
| >= 1 feature | 65 |
| >= 2 features | 62 |
| >= 3 features | 59 |
| >= 10 features | 59 |
| >= 20 features | 59 |
| >= 50 features | 58 |

Six cells hold one or two features each. These are edge bleed — features whose
recorded position falls just over a sheet boundary — not additional worked
sheets. Above that floor the count is stable at **59** all the way to a
threshold of 20 features per sheet.

Split by season, and using a 10-feature floor:

- **2017: 42 sheets.** This matches the published figure exactly, and matches
  the 42 distinct cells the assignment log resolves to.
- **2018: 17 sheets.** The published figure, and the project's own tally in the
  `RecordingProgress` workbook, is 16.
- **The two seasons are disjoint** at this threshold, so the union is 59.

**Answer: both numbers are right about different things.** The point data
contains 59 distinct sheets carrying substantive digitisation. The discrepancy
is entirely in the 2018 season, and the most likely 17th sheet is `K-35-077-4`,
which holds 59 features from one digitiser whose convex hull covers only 34 %
of the sheet. Every other 2018 sheet holds 91 to 284 features with 84–96 %
areal coverage. `K-35-077-4` reads as a partially worked sheet that the
project's own count did not treat as a completed map. The 58 in the paper is
"sheets completed"; the 59 the principal investigator recalls is "sheets
touched".

One further wrinkle: exactly one cell (`K-35-076-1`) carries features from both
seasons — two 2017 features and 213 from 2018. The two 2017 features are edge
bleed from an adjacent 2017 sheet, so this is not a genuine cross-season
re-survey.

---

## 7. Overlap census (stage 4)

This is the section that matters for a double-marking or consensus analysis.
Three independent measurements were made.

### 7.1 Pairwise polygon intersection

All 28 pairs of the eight audit polygons were intersected.

| Pair | Codes | Intersection (sq km) | Reading |
|---|---|---:|---|
| 3 ∩ 100 | C, C | 16.527 | missed swath nested inside C's Rakovski area |
| 3 ∩ 101 | C, C | 9.582 | as above |
| 3 ∩ 102 | C, C | 6.778 | as above |
| 10 ∩ 11 | C, A | 0.0002 | shared boundary sliver on Elenovo |
| 1 ∩ 10 | B, C | 0.0000 | shared corner, zero area |

**There is no cross-student polygon overlap.** The only two cross-student pairs
that intersect at all share a boundary: the total cross-student intersection
area is 0.0002 sq km, i.e. about 200 square metres of topological sliver along
the Elenovo partition line. The Elenovo split between A and C is a **partition,
not an overlap** — the two students worked adjacent halves of one sheet, not
the same ground.

### 7.2 Per-sheet feature counts by student

Full table: `sheet-student-census.csv` (one row per sheet, one column per code,
plus `total`, `n_codes`, `n_codes_ge5`, `n_codes_ge20`).

- Sheets touched by two or more codes, counting a single feature: **31**.
- Sheets where two or more codes each contributed at least 5 features: **6**.
- Sheets where two or more codes each contributed at least 20 features: **4**.

The gap between 31 and 6 is the point: most apparent sheet sharing is one or
two features bleeding across a boundary from an adjacent sheet.

The four genuinely multi-student sheets:

| Sheet | Alias | Codes and counts | Total |
|---|---|---|---:|
| K-35-053-3 | Elenovo | A 229, C 60 | 289 |
| K-35-075-2 | — | F 264, G 20 | 284 |
| K-35-076-4 | — | F 148, TESTER-1 21, H 2, G 1 | 172 |
| K-35-076-2 | — | F 97, H 35 | 132 |

Two more sheets clear the 5-feature bar: `K-35-055-1` (A 205, TESTER-1 10, B 2)
and `K-35-074-4` (G 128, I 13, F 3). The staff-tester contributions are
demonstration or training records, not independent survey.

### 7.3 Cross-student proximity — the double-marking question

Every point pair from different codes within 50 m was enumerated in EPSG:32635.
Full table: `cross-student-proximity-pairs.csv`.

**Result: 17 pairs, involving 34 distinct features, all on one sheet, all from
one pair of students.**

| Threshold | Cross-student pairs |
|---:|---:|
| <= 25 m | 12 |
| <= 50 m | 17 |
| <= 100 m | 17 |
| <= 200 m | 20 |
| <= 500 m | 73 |
| <= 1000 m | 326 |

All 17 sub-50 m pairs are code F against code G on sheet `K-35-075-2` (2018
season). Separations run from 3.3 m to 37.1 m, median 17.9 m. **All 17 pairs
carry identical `map_symbol` values** — the two digitisers agreed on the symbol
class in every case.

The mechanism is visible in the identifiers and timestamps:

- G recorded two isolated features on this sheet on 12 September 2018, far from
  anything else (nearest counterpart 649 m and 976 m).
- G then recorded a contiguous run of 18 features, identifiers 212232–212249,
  on 25 September 2018 between 05:19 and 05:53 UTC — a 34-minute stint.
- F digitised the entire sheet (264 features, identifiers 213105–213369) the
  same day, 09:02 to 14:22 UTC, about three and a half hours later.
- 17 of G's 18-feature run have an F counterpart within 50 m. The pairing is
  one-to-one and order-preserving: G's 212232…212249 map onto F's 213105…213131
  in sequence.
- The remaining feature of the run (identifier 212243) has **no** F feature
  within 1.29 km. It is either a genuine omission by F or a positional error by
  G, and is worth eyeballing on the raster.

Everywhere else in the corpus, cross-student proximity is negligible: only
three further pairs exist between 100 m and 200 m, and no other code pair
produces a single sub-50 m pair.

### 7.4 Genuinely double-surveyed zones

Each code's coverage footprint on each sheet was modelled as the union of 250 m
buffers around its features, and footprints of different codes on the same
sheet were intersected. Full table: `double-surveyed-zones.csv`.

| Code pair | Sheets | Total zone (sq km) | Features in zone |
|---|---:|---:|---:|
| F–G | 3 | 3.212 | 36 |
| D–E | 2 | 0.146 | 2 |
| B–D | 1 | 0.130 | 2 |
| A–B | 1 | 0.095 | 2 |
| A–C | 1 | 0.074 | 0 |
| B–C | 1 | 0.059 | 0 |
| A–TESTER-1 | 1 | 0.006 | 0 |
| **Total** | | **3.722** | **42** |

**The entire double-surveyed estate in this corpus is 3.7 sq km, of which
3.1 sq km is the single F–G zone on `K-35-075-2` holding 36 features (19 F,
17 G).** Everything else is a handful of stray features straddling a sheet
boundary.

For scale: the corpus covers 58–59 sheets of roughly 384 sq km each, about
22,500 sq km. The double-surveyed fraction is **0.017 %**.

### 7.5 Within-student duplicates, for comparison

The same proximity computation was run within codes, as a pipeline validation.
Full table: `within-student-proximity-pairs.csv`. There are 47 within-student
pairs under 50 m across the whole corpus (A 18, C 13, E 8, B 3, D 3, F 1, G 1).

On the audited Rakovski sheet, code C has **exactly 6** within-student pairs
under 50 m — reproducing the 6 double-marked features the published Table 3
attributes to that student on that sheet. The paper's "double-marked" category
is therefore a *within*-student phenomenon (one digitiser marking one symbol
twice), structurally different from the cross-student overlap measured in
§ 7.3.

---

## 8. Quality-assurance workbook (stage 5)

**Outputs**: `qa-time-on-task.csv` and `qa-time-on-task-activity-log.csv`.

`QA-time-on-task__Results.csv` stacks five different presentations of the same
four-sheet audit in one tab. They are staged as one tidy table with a `block`
column distinguishing them, all names replaced by codes, and the two composite
row labels preserved in a `qualifier` column:

| `block` | Rows | Content |
|---|---:|---|
| `by_tile` | 5 | per audited sheet, with the sheet's principal digitiser |
| `by_student_split` | 6 | per student, with C's two sheets kept apart |
| `by_student_combined` | 5 | per student, with C's two sheets summed |
| `excluding_student_c` | 4 | the counterfactual quoted in the paper |
| `published_table_3` | 5 | the table as published |

Metric columns are `features_identified`, `false_positive`, `double_marked`,
`false_negative`, `classification_error`, `total_errors`, `true_positives`,
`true_feature_count`, and the four corresponding rates. Roll-up rows carry
`student_code = CUMULATIVE`.

`QA-time-on-task__ToT.csv` is the staff quality-assurance session log. It
contains no personal names. Its seven activity rows are staged verbatim as
`qa-time-on-task-activity-log.csv` (activity, date, start, minutes,
errors found, notes): 180 minutes logged across the sessions, 26 errors found
in-session. The surrounding free-text commentary in that tab (a second attempt
after a data loss, 240 minutes; two hours of collation; a nine-hour total
including the lost attempt) was not staged, as it is prose rather than tabular
data; it remains in `raw/`.

---

## 9. Name-leak check

`scripts/stage_09_leakcheck.py` builds the personal-name token set from
`raw/code-mapping.json` — canonical names, surnames, given names, and every
observed variant form, split into individual word tokens — and runs two passes
over every file in this directory.

**Pass 1, raw text.** Case-insensitive, word-boundary search of every byte of
every staged file for every token.

**Pass 2, field-level adjudication.** Every hit is traced to the column and
value it occupies, and every attribution column is asserted closed over the
code vocabulary `{A ... I, TESTER-1, CUMULATIVE}`.

Two classes of token are excluded from the sweep, both deliberately and both
documented in the script:

1. **Structural words** that appear only inside composite source labels
   ("Student A", "Staff Tester", and the missed-swath polygon labels): *student,
   staff, tester, missed, partial, row, rows, combined, cumulative, overall,
   volunteer*, and one settlement name. The script asserts that none of these is
   a substring of any real name before dropping it.
2. **One two-character initialism**, which is also an ordinary English word and
   therefore yields only false positives. Its absence is instead guaranteed by
   the closed-vocabulary assertion on the attribution columns, which is the
   stronger check.

### Result

**PASS.** Across 54 name tokens and 10 staged files:

- **Zero** personal-name tokens in any attribution, label, note, column name,
  free-text, or prose position.
- All 11 attribution columns verified closed over the code vocabulary.
- 6,519 hits are accounted for by a **single controlled-vocabulary collision**:
  one 2017 surname is also a colour adjective used throughout the Soviet
  map-symbol descriptions (`map_symbol` in the point layer, `symbol` in the
  error layer, `symbol_a`/`symbol_b` in the proximity table). Every one of those
  6,519 occurrences is inside one of the 12 exact vocabulary strings. Those
  strings appear across every digitiser's records and in both seasons — the
  colliding term occurs on 6,499 of the 10,827 features — so they carry no
  attribution signal whatever. Removing the term would destroy the symbol
  vocabulary, which is essential analytical content; it is therefore retained
  and documented here rather than suppressed.

---

## 10. Files in this directory

| File | Rows / features | CRS | Description |
|---|---:|---|---|
| `mounds-attributed.geojson` | 10,827 | EPSG:4326 | master point layer, anonymised |
| `assignment-areas.geojson` | 8 | EPSG:4326 | audit areas and missed swaths |
| `qa-errors.geojson` | 49 | EPSG:4326 | quality-assurance error points |
| `sheet-student-census.csv` | 65 | — | features per sheet per code |
| `cross-student-proximity-pairs.csv` | 17 | — | cross-code point pairs within 50 m |
| `within-student-proximity-pairs.csv` | 47 | — | within-code point pairs within 50 m |
| `double-surveyed-zones.csv` | 10 | — | overlapping coverage footprints |
| `qa-time-on-task.csv` | 25 | — | audit error tables, coded |
| `qa-time-on-task-activity-log.csv` | 7 | — | staff session log |
| `STAGING.md` | — | — | this document |

---

## 11. Open items and cautions

- **The double-marking corpus is small.** Seventeen independently duplicated
  features on one sheet from one pair of digitisers is enough for a case study
  or a worked illustration, not for a powered inter-rater agreement estimate.
  If a consensus analysis is the goal, the four-sheet staff audit (834 true
  features, 49 errors, fully localised) is the substantive second reading in
  this deposit, not the accidental overlaps.
- **The `Recorder` attribute in the error layer should not be used** without the
  spatial cross-check; it mis-attributes two of the 49 errors.
- **The `Year` attribute in the error layer should not be used at all**; six of
  49 rows carry a season inconsistent with the point layer.
- **Per-sheet and per-student error rates are not interchangeable** for codes A
  and C, because those two share the Elenovo sheet.
- **The assignment-log labels contain two settlement-name slips**, so label
  identity is not a safe join key; the graticule cell derived from the point
  geometry is.
- **Sheet counts depend on a feature-count floor.** Any count of "sheets
  digitised" should state its threshold; the corpus is stable at 59 sheets for
  any floor between 3 and 20 features.
- **All 59 sheets do have a local raster**, but in two places: 55 under
  `inputs/rasters/Russian1981_32635/` and the four gold-standard sheets at the
  top level of `inputs/rasters/`. Any code that globs only the former will
  silently miss the four audited sheets.

---

## Changelog

### 2026-09-01 — Original publication

Initial staging of the 2023 participatory-GIS deposit. Created
`mounds-attributed.geojson` (10,827 features), `assignment-areas.geojson` (8),
`qa-errors.geojson` (49), `sheet-student-census.csv`,
`cross-student-proximity-pairs.csv`, `within-student-proximity-pairs.csv`,
`double-surveyed-zones.csv`, `qa-time-on-task.csv` and
`qa-time-on-task-activity-log.csv` from the raw Drive deposit documented in
`raw/MANIFEST.md`.

Substantive findings established at this revision, each recorded above with its
evidence: the audit-area layer is a four-sheet quality-assurance geometry rather
than a nine-person assignment layer; the Elenovo sheet was partitioned between
two students, which makes the published Table 3's A and C rows non-comparable
with per-sheet rates; the corpus contains 59 distinct sheets against the
published 58, the difference being one partially worked 2018 sheet; and
cross-student double-marking is confined to 17 feature pairs on a single sheet,
totalling 3.1 sq km of doubly surveyed ground.

One methodological correction was made during the run and is retained here as a
caution: sheet assignment must not use the local GeoTIFF footprints, which are
axis-aligned bounding boxes overlapping their neighbours by 3,295.9 sq km in
total, and which manufacture spurious multi-student sheets. The staged analysis
uses an exactly tessellating Soviet-nomenclature graticule instead.
