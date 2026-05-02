# Deduplication plan: raw gold-standard (GS) student-review data

> **⚠️ SUPERSEDED 2026-05-01.** This planning document is preserved
> for historical reference. The work it describes was executed in
> Session 82 (commits `a0ee28c6..6f15b8c9`); see Obs 316
> (trapezoidal-graticule active-area correction → Sobotkova 2023
> 5.0 % FN / 0.1 % FP vindicated) and Obs 317 (per-map breakdown +
> inter-student-skill variance reframing) in
> `docs/notes/reflections/working-notes.md`, plus
> `planning/paper-writeup-continuity.md` §"Session 82 closure
> (2026-05-01)" for the current state. The full §8 open-questions
> list is closed inline in that continuity-doc section.
> Do not act on items in this file as if they are pending.

**Date**: 2026-04-30.
**Author**: Claude Code (Opus 4.7) for Shawn Ross.
**Status**: PLAN ONLY — needs user approval before any execution.
**Specification source**: User instruction 2026-04-30 (Obs 312-related GS-FP audit
follow-up); prior 55-map dedup workflow at `scripts/review_gt_duplicates.py`
(commit `dea1155f`).

## 1. Executive summary

The user requested a dedup pass on the raw GS student-review data — 822 raw
"Mound" features (560 Hairy / Russian 1:50k symbology, 262 non-Hairy) inside
the four GS map sheets — under the hypothesis that the apparent ~38.7 % FP
rate against curator GT is largely duplicates ("there were a lot of
duplicates" per user recall). The smoke test contradicts that hypothesis.

Key smoke-test findings (read-only, no modification):

1. **The prior dedup script exists** at `scripts/review_gt_duplicates.py`
   (Streamlit-based human review at 50 m primary, with optional 75 m widening
   pass) and produced `student-mounds-55maps-reviewed.geojson` via commit
   `dea1155f`. Methodology is well-documented: per-map connected-components
   clustering, four decision codes (`keep_all`, `merge`, `keep_only`,
   `uncertain`), centroid-merge geometry. The 55-map review accepted merge
   on 26 of 96 candidate clusters (27 % accept rate).
2. **At 50 m radius the GS-region Hairy data has only 4 candidate clusters
   (8 points, 0.7 % of 560).** All four are within-student (same student
   marking the same point twice; specifically Lachlan Hanley on K-35-062-2,
   Hairy brown circle in every case). At 25 m: 3 clusters / 6 points
   (0.5 %). At 10 m: 1 cluster / 2 points (0.2 %).
3. **The 38.7 % apparent FP rate is NOT primarily a duplicates story.** The
   correct decomposition: of 822 raw GS-region Mound features, 543 of 560
   Hairy match curator GT within 50 m (97 % match rate, consistent with
   Sobotkova 2023's 99.9 % accuracy); only 7 of 262 non-Hairy match
   (3 % match rate). The 38.7 % unmatched fraction collapses to 3 % once
   the data is filtered to the same Hairy-only criterion the 55-map
   reference applies, **without any deduplication**.
4. **The 262 non-Hairy points are an unexplained provenance question.**
   `MpSymbl` values like "Black diamond with a dot inside" (no "Hairy"
   prefix) are present in the raw data but absent from the 55-map
   reference. The `Source` field uniformly says "TopomapRU 1:50k" for
   all 822 features, but the symbol vocabulary is heterogeneous. A
   spatial check shows non-Hairy points are spatially disjoint from
   Hairy points (median distance 1.2 km; 0 % co-location at any
   reasonable dedup radius), so they are NOT re-symbolisations of the
   same features. Most likely they are markings made on a different
   underlying map series (e.g. Bulgarian 1:50k vs Russian 1:50k) or
   under an earlier protocol revision; the 55-map reviewers correctly
   excluded them. **This needs user confirmation before the dedup
   pass produces an authoritative GS-side student GT.**

The plan therefore recommends: (a) run the same Streamlit-based dedup as
the 55-map workflow, (b) apply the same Hairy-only filter as the 55-map
reference, and (c) flag the 262 non-Hairy points as a provenance question
for separate handling. Smoke-test result implies the dedup itself will
remove **0–4 features** (depending on user's keep_all/merge decisions), not
the "halve the unmatched count" the original framing predicted.

## 2. Prior dedup script — found

### 2.1 Location and provenance

- **Script**: `scripts/review_gt_duplicates.py` (1,617 lines).
- **Introducing commit**: `dea1155f` ("data(gt-review): cleaned GT +
  cleaned-GT F1 re-evaluation + Obs 261", 2026-04-19).
- **Output it produced**: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  (4,744 features; Δ = −26 from the 4,770-feature original at
  `inputs/vectors/references/student-mounds-55maps.geojson`).
- **Decisions CSV**: `results/gt-duplicate-review/gt-duplicate-decisions.csv`
  (96 reviewed clusters; 26 merges, 70 keep_all).
- **Diff report**: `results/gt-duplicate-review/gt-duplicate-diff.md`.

### 2.2 Methodology (read in full from the script)

1. **Load** the input GeoJSON, ensure UTM CRS (EPSG:32635 default), assign a
   stable `_gt_row_id`.
2. **Cluster per-map** at the user-specified radius using a `cKDTree`
   pairwise query → sparse-graph connected components. Two points on
   different `source_map` values never join even if their geometries are
   identical (per-map containment is enforced).
3. **Present each cluster** in a Streamlit UI with a 300 m raster context
   crop (best-coverage raster auto-selected, falling back to the
   declared `source_map`). Numbered markers identify each member point.
4. **Reviewer decision** is one of:
   - `keep_all`: every member is a distinct mound; no rows removed.
   - `merge`: every member is the same physical mound; all rows replaced
     by a single new row at the cluster centroid, with a chosen subtype
     from the closed list `{burial_mound, bench_mark_on_mound,
     trig_point_on_mound, settlement_mound, other}`.
   - `keep_only N`: keep only point #N from the cluster, drop the rest.
   - `uncertain`: flagged for later but pass through unchanged.
5. **Multi-threshold workflow**: decisions persist across threshold
   widenings. A tight 50 m pass can be followed by a 75 m pass; subsumed
   decisions are auto-removed when a wider cluster is decided.
6. **`--apply` post-processing** runs the decisions CSV against the
   original GT, drops merged rows, appends merged centroids carrying
   `_merged=True` and `_reviewed_subtype=...` columns, writes the
   cleaned GeoJSON + a markdown diff report.

### 2.3 Defaults and CLI shape (verbatim from the script)

```bash
streamlit run scripts/review_gt_duplicates.py -- \
    --ground-truth inputs/vectors/references/student-mounds-55maps.geojson \
    --rasters-dir inputs/rasters/Russian1981_32635 \
    --threshold-m 50

python scripts/review_gt_duplicates.py --apply \
    --ground-truth inputs/vectors/references/student-mounds-55maps.geojson \
    --decisions results/gt-duplicate-review/gt-duplicate-decisions.csv
```

- `_DEFAULT_THRESHOLD_M = 50.0` (line 99).
- `_DEFAULT_CONTEXT_M = 300.0` (line 100).
- `_DEFAULT_GT = "inputs/vectors/references/student-mounds-55maps.geojson"`
  (line 101).
- `_DEFAULT_RASTERS = "inputs/rasters/Russian1981_32635"` (line 102).
- `_DEFAULT_OUTPUT = "results/gt-duplicate-review/gt-duplicate-decisions.csv"`
  (line 103).
- `_DEFAULT_CLEAN_GT = "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"`
  (line 104–106).

The 55-map review chose 50 m as the primary threshold based on the
spacing analysis of the curator-corrected 4-map GT (minimum nearest-
neighbour spacing 68.1 m; zero mounds below 50 m). Below that floor any
cluster is operationally a double-mark; above, it is plausibly two
adjacent real mounds. Per the commit message: 93 % merge below 50 m,
0 % merge above 50 m. **This 50 m floor argument carries over directly
to the GS data** (same corpus, same survey region, same physical mound
spacing).

## 3. Raw GS student data — structure, count, provenance

### 3.1 Source

- **Directory**: `inputs/raw-student-review-production-maps/Mapmounds/`
  (untracked in git as of 2026-04-30; the user will need to commit
  before/after the dedup pass per the project "commit API outputs"
  policy and the per-project archive rule).
- **Shapefiles**:
  - `Mounds32635.shp` (EPSG:32635, 10,825 features) — primary input.
  - `MapMounds4326.shp` (EPSG:4326, same 10,825 features).
- **README**: `inputs/raw-student-review-production-maps/README.md`
  (3 lines of context; cites the upstream `MapMoundLoad.R` script at
  <https://github.com/adivea/MapMoundsDigitized.git>).
- **Feature count**: 10,825 raw points (per `len(gpd.read_file(...))`).
  Of these, 822 lie within the four GS map-sheet rectangular bounds —
  208 on K-35-052-4, 291 on K-35-053-3, 254 on K-35-062-2, 69 on
  K-35-078-1.

### 3.2 Schema (Mounds32635.shp)

25 columns: `uuid`, `identfr`, `cretdBy`, `crtAGMT`, `modfdBy`, `mdfAGMT`,
`ID`, `FtrAthr`, `FtrTmst`, `Latitud`, `Longitd`, `Accurcy`, `FetrTyp`,
`MpSymbl`, `Source`, `Note`, `GC`, `DtCmplt`, `Dscrptn`, `Clssfct`,
`OthrDsc`, `Picture`, `gsptlcl`, `year`, `geometry`.

Relevant attributes for the dedup pass:

- `FtrAthr` — student name (per-feature attribution; lets us decompose
  within-student vs across-student dedup).
- `FtrTmst` / `DtCmplt` — feature creation timestamp / completion date
  (lets us choose "earliest-timestamp" tie-breaks if needed; the prior
  script does not use these — it merges to the centroid).
- `FetrTyp` — top-level type. Values across the full 10,825-row file:
  `Mound` (10,744), `Surface feature` (58), `Other` (17). Within the
  four GS sheets: 822 / 822 are `Mound`. **The non-mound types are
  effectively absent from the GS region.**
- `MpSymbl` — symbol-vocabulary classification. Within GS: 11 distinct
  values across the 822 features (table below).
- `Source` — uniform "TopomapRU 1:50k" for all 822 GS-region features.
- `Note` — free-text reviewer note (rare; e.g. "settlement mound -
  atypically large symbol").

### 3.3 Symbol distribution within the four GS sheets

| `MpSymbl` value                                        |  Count | Hairy? |
|--------------------------------------------------------|-------:|:------:|
| Hairy brown circle                                     |    460 | yes    |
| Black diamond with a dot inside                        |    226 |  no    |
| Hairy black diamond with a dot inside                  |     58 | yes    |
| Hairy black triangle with a dot inside                 |     41 | yes    |
| Black triangle with a dot inside                       |     30 |  no    |
| Other (describe in annotation)                         |      6 |  no    |
| (Hairy + non-Hairy totals)                             |    822 |        |

Hairy-total: 559 (`460 + 58 + 41 = 559`; one row had a less common Hairy
variant counted in the 560 figure earlier — a single "Other (describe in
annotation) (hairy black circle)" record). Non-Hairy total: 262.

### 3.4 Provenance comparison vs the 55-map reference

The 55-map reference at `inputs/vectors/references/student-mounds-55maps.geojson`
filters the same upstream raw data to **only six "Hairy" `MapSymbol`
values** (verified by `set(ref['MapSymbol']) == {'Hairy brown circle',
'Hairy black diamond ...', 'Hairy black square ...', 'Hairy black
triangle ...', 'Hairy brown circle (has black diamond on top)', 'Other
(describe in annotation) (hairy black circle)'}`). Every one of the
4,770 reference features has a "Hairy" symbol; zero non-Hairy entries
survive. **The raw → 55-map filter pipeline drops the non-Hairy points
upstream of the dedup pass.**

### 3.5 Discrepancy with prior audit's 848 figure

The user's request states "848 raw student features across the 4 GS
maps". My re-count is **822** features (`gs.geometry.within(unary_union
(four GS sheet bounds))`, all `FetrTyp == 'Mound'`). The 26-feature
gap may reflect (a) a different bounds-vs-intersection rule (e.g.
counting features that touch an extended buffer around each sheet),
(b) inclusion of `Surface feature` / `Other` rows (not present within
the strict GS bounds in my re-count), or (c) an earlier audit-time
count I cannot reproduce without the audit script. **Flag for user
confirmation in §8.**

### 3.6 Same students, same campaign

Within the GS sheets, contributing students are: Lachlan Hanley (307),
Stephanie Black (238), Samuel Riley (206), Briana Barton (70), Isaac
Roberts (1). All five also appear in the 55-map reference's contributor
list, with overlapping date ranges (17 Sep 2017 – 28 Sep 2017 across
the GS subset). **Provenance is consistent with the 55-map review
campaign.**

## 4. Adaptation design — five decisions

### 4.1 Dedup radius — recommend 50 m primary, sweep at 25/50/75/100 m

Rationale (independent of the smoke-test result):

- The 55-map review's 50 m primary was anchored to the spacing analysis
  showing zero curator-GT mounds <50 m apart in this corpus (Stara
  Zagora region). That floor argument applies to the GS data
  unchanged — same survey region, same physical reality.
- 25 m as a tight sensitivity bound checks whether the very-close
  doubles ("clearly the same point") are caught at a stricter
  threshold; the 55-map review found 93 % merge rate below 50 m, so
  25 m and 50 m should produce similar merge counts.
- 75 m is the 55-map widening pass's threshold; preserving symmetry
  here lets us cross-check whether GS shows the same bimodal signal
  (high merge below 50 m, zero merge above).
- 100 m is a final upper bound for sensitivity (the 55-map review
  found 0 of the 70 keep_all decisions sat at 50–75 m gave a merge
  verdict; 75 m is functionally an asymptote on this corpus).

The smoke test (§5) shows merge counts will be small at every radius;
the sweep mainly serves to **demonstrate threshold stability** rather
than to discover hidden duplicates.

### 4.2 Which-dot-to-keep criterion — centroid (matches prior script)

The prior script's `merge` decision replaces the cluster's rows with a
single new row at the **mean of the member coordinates** and assigns
a user-chosen subtype from the closed-list vocabulary. No other
criterion (earliest timestamp, longest annotation, highest-resolution
position) is used.

**Recommend keeping centroid.** Two reasons:

1. Symmetry with the 55-map reference (any analysis comparing the two
   corpora benefits from identical merge geometry).
2. Centroid is unbiased w.r.t. which student happened to mark the
   feature first. The student timestamps in the raw data are when the
   reviewer clicked the dot, not when the mound was first observed —
   so "earliest" carries no archaeological meaning here.

### 4.3 Per-student vs across-student dedup — preserve both, decompose by source

The smoke test at 50 m (Hairy-only) found 4 candidate clusters, all
within-student: Lachlan Hanley double-marked the same Hairy brown
circle four separate times on K-35-062-2. **Across-student dedup
clusters are zero at 50 m on this data.**

This pattern matches the project's working-notes Obs 261: most
duplicates are "double-marks-below-50 m" within a single reviewer's
session, not two separate reviewers independently marking the same
mound. The dedup pass therefore is essentially a **within-reviewer
double-click cleanup**.

The plan recommends:

- Run the dedup at 50 m primary as for the 55-map review.
- In the diff report, decompose merges by `within-student` vs
  `across-student` per the prior `FtrAthr` field.
- **Do NOT change the script** — the existing decision UI does not
  need modification; this decomposition is a post-processing analysis
  that reads the decisions CSV.

### 4.4 Feature-type filter — Hairy-only, before the dedup pass

This is the largest design decision and the one where the smoke test
diverges sharply from the user's prior framing.

**Recommended pipeline**:

1. **Spatial subset** to the four GS sheets (rectangular bounds union,
   strict `within`).
2. **Type filter**: `FetrTyp == 'Mound'` (eliminates 0 features in
   practice within the GS bounds; preserves the convention).
3. **Symbol filter**: `MpSymbl` contains "Hairy" (case-insensitive) —
   **matches the 55-map reference exactly**. Drops 262 non-Hairy
   features.
4. **Dedup pass** on the resulting 560-feature Hairy-only set at
   50 m primary.

The 262 non-Hairy points are flagged for the user as an open question
(§8). They should NOT be in the dedup input until the user confirms
their provenance.

**Why this order matters**: running dedup first then filtering would
risk merging a Hairy point with a co-located non-Hairy point — but
the smoke test confirms zero such co-locations exist (median NN
distance from a non-Hairy to the nearest Hairy point is 1.2 km).
Order doesn't affect the count, but Hairy-first matches the 55-map
pipeline order and is conceptually cleaner.

### 4.5 Output naming — match the 55-map convention

Recommended path:
`inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson`

Sibling to `student-mounds-55maps-reviewed.geojson`. The "gs-4maps"
prefix follows the project's `gs-fp-classification` /
`results/gold-standard-*/` convention.

Decisions CSV: `results/gs-gt-duplicate-review/gs-gt-duplicate-decisions.csv`.
Diff report: `results/gs-gt-duplicate-review/gs-gt-duplicate-diff.md`.

The script's CLI accepts arbitrary paths via `--ground-truth`,
`--output`, `--clean-output`, `--diff-output`, so **no script
modification is needed for the output paths.** The Hairy-only filter,
however, will need a small change to the script (or a one-shot
sidecar that pre-filters the raw shapefile to a working GeoJSON,
which is the lower-risk path — see §6).

## 5. Smoke-test results

All numbers below come from a read-only Python session
(`.venv/bin/python` with geopandas, scipy.spatial.cKDTree,
shapely.box / unary_union). No file was created, modified, or
written during the smoke test.

### 5.1 Cluster counts by radius — Hairy-only (n = 560)

| Radius | Clusters | Pts in clusters | Removed if all-merge | % removed |
|-------:|---------:|----------------:|---------------------:|----------:|
|    5 m |        0 |               0 |                    0 |     0.0 % |
|   10 m |        1 |               2 |                    1 |     0.2 % |
|   25 m |        3 |               6 |                    3 |     0.5 % |
|   50 m |        4 |               8 |                    4 |     0.7 % |
|   75 m |        8 |              16 |                    8 |     1.4 % |
|  100 m |       23 |              59 |                   36 |     6.4 % |

The 100 m row crosses the spacing-analysis floor for genuinely-
adjacent real mounds (the 55-map review found ~50 m as the
operational boundary). Above ~50 m, clusters are increasingly
likely to be two distinct mounds rather than duplicates.

### 5.2 Cluster counts by radius — all Mound (n = 822)

| Radius | Clusters | Pts in clusters | Removed if all-merge | % removed |
|-------:|---------:|----------------:|---------------------:|----------:|
|    5 m |        0 |               0 |                    0 |     0.0 % |
|   10 m |        1 |               2 |                    1 |     0.1 % |
|   25 m |        4 |               8 |                    4 |     0.5 % |
|   50 m |        6 |              12 |                    6 |     0.7 % |
|   75 m |       10 |              20 |                   10 |     1.2 % |
|  100 m |       26 |              66 |                   40 |     4.9 % |

Including non-Hairy adds two candidate clusters at 50 m (one cluster
per sheet on K-35-053-3 and K-35-062-2). Both are between two
non-Hairy points; neither involves a Hairy ↔ non-Hairy join.

### 5.3 Within-student vs across-student decomposition (Hairy, 25 m)

- Within-student clusters: 3 (6 points, 100 % of clusters).
- Across-student clusters: 0.

Lachlan Hanley accounts for all 4 candidate clusters at 50 m on the
Hairy-only set, all on K-35-062-2, all involving "Hairy brown
circle" symbols. **The duplicate signal in the GS data is
within-student double-marking, just as the 55-map analysis found.**

### 5.4 Match rate against curator GT — the headline finding

| Filter                     | n   | Matched @25m | Unmatched @25m | Unmatched @50m |
|----------------------------|----:|-------------:|---------------:|---------------:|
| All raw within GS bounds   | 822 |          520 |    302 (36.7%) |    272 (33.1%) |
| `FetrTyp == Mound`         | 822 |          520 |    302 (36.7%) |    272 (33.1%) |
| **Hairy-only Mound**       | 560 |          515 |     45 (8.0 %) |     17 (3.0 %) |

Curator GT contains 569 mounds across the four sheets (verified at
`inputs/vectors/references/mounds-reference.geojson`, 569 multipoints
exploded to 569 single points; CRS EPSG:32635). The "match rate"
above is `student → nearest curator GT within R metres`.

**The Hairy-only filter alone collapses the unmatched rate from
33.1 % to 3.0 % at 50 m**, without any deduplication. The dedup pass
on top of that filter further reduces the unmatched count by at
most 4 features (0.7 % of 560), depending on the user's keep_all /
merge decisions.

### 5.5 Where do the unmatched non-Hairy points come from?

| `MpSymbl` value                  | Total in GS | Matched ≤50 m | Unmatched >50 m |
|----------------------------------|------------:|--------------:|----------------:|
| Black diamond with a dot inside  |         226 |             1 |             225 |
| Black triangle with a dot inside |          30 |             1 |              29 |
| Other (describe in annotation)   |           6 |             5 |               1 |

The 262 non-Hairy points are essentially a **separate dataset that
does not overlap the curator GT spatially** — only 7 of 262 land
within 50 m of a curator mound (2.7 % match rate; consistent with
chance background overlap). They are not duplicates of Hairy points;
they are mostly different features at different locations, marked
under different symbol vocabulary.

This is an unexplained provenance question that **must be resolved
before the GS-side student GT is cited as authoritative.** See §8.

## 6. Recommended execution plan

The recommended workflow runs the existing 55-map dedup script
unmodified, with a small pre-filter sidecar that produces the
Hairy-only working GeoJSON. **No changes to `scripts/review_gt_duplicates.py`.**

### 6.1 Pre-filter step — produce the Hairy-only working GeoJSON

A new script (~40 lines, sibling to `review_gt_duplicates.py`) reads the
raw shapefile, applies the spatial + type + symbol filters, assigns the
`source_map` column expected by the dedup clusterer, and writes
`inputs/vectors/references/student-mounds-gs-4maps.geojson` (sibling
to the 55-map original). This pre-filter is the **only new code**;
once it produces the working GeoJSON, the existing dedup script
operates on it unchanged.

Suggested name: `scripts/prepare_gs_student_input.py`. Suggested CLI:

```bash
python scripts/prepare_gs_student_input.py \
    --raw-input inputs/raw-student-review-production-maps/Mapmounds/Mounds32635.shp \
    --rasters-dir inputs/rasters \
    --output inputs/vectors/references/student-mounds-gs-4maps.geojson \
    --hairy-only
```

The script would:

1. Load the raw shapefile (10,825 features, EPSG:32635).
2. Build the union of the four GS-sheet rectangular bounds from
   `inputs/rasters/{K-35-052-4_32635, K-35-053-3_Elenovo, K-35-062-2_Rakovski,
   K-35-078-1_Lesovo}.tif`.
3. Filter: `geometry.within(union)` AND `FetrTyp == 'Mound'` AND
   (`--hairy-only` ⇒ `MpSymbl` contains "Hairy", case-insensitive).
4. Assign `source_map` column by checking which sheet each point
   is `within`.
5. Rename columns to match the 55-map schema:
   `MpSymbl → MapSymbol`, `FetrTyp → FeatureType`, `Latitud → Latitude`,
   `Longitd → Longitude`. Drop irrelevant columns.
6. Write the filtered GeoJSON, ensure WGS84 + UTM round-tripping.

### 6.2 Dedup review — Streamlit UI, 50 m primary

```bash
streamlit run scripts/review_gt_duplicates.py -- \
    --ground-truth inputs/vectors/references/student-mounds-gs-4maps.geojson \
    --rasters-dir inputs/rasters \
    --threshold-m 50 \
    --output results/gs-gt-duplicate-review/gs-gt-duplicate-decisions.csv
```

Note the `--rasters-dir inputs/rasters` (top-level, not the 55-map
`Russian1981_32635/` subdir; matches the convention used elsewhere
in the project for GS-specific runs).

Expected scope per the smoke test: **4 candidate clusters at 50 m**.
Wall-clock estimate at the prior 55-map pace (a few seconds per
cluster, mostly raster-rendering): under 1 minute of UI time.

**Optional widening pass at 75 m** afterwards — adds 4 more
candidate clusters per the smoke test (8 total at 75 m vs 4 at
50 m). The script auto-handles the threshold-widening case
without re-reviewing decisions already saved at 50 m.

### 6.3 Apply step — produce the cleaned GeoJSON

```bash
python scripts/review_gt_duplicates.py --apply \
    --ground-truth inputs/vectors/references/student-mounds-gs-4maps.geojson \
    --decisions results/gs-gt-duplicate-review/gs-gt-duplicate-decisions.csv \
    --clean-output inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson \
    --diff-output results/gs-gt-duplicate-review/gs-gt-duplicate-diff.md
```

The `--apply` step produces:

- `inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson`
  — the cleaned GS-side student GT, schema-symmetric with the
  55-map reviewed sidecar (`_merged`, `_reviewed_subtype` columns).
- `results/gs-gt-duplicate-review/gs-gt-duplicate-diff.md` — per-cluster
  decision record with merge / keep_all breakdown.

### 6.4 Verification queries (post-execution)

Run these to confirm the dedup behaved as the smoke test predicted:

1. **Feature count**: `len(reviewed) == len(input) - merges_accepted`.
   Expected:`560 - {0..4} = 556..560` depending on the user's
   keep_all/merge decisions.
2. **Match rate against curator GT** at 25 m / 50 m: should match
   the smoke-test §5.4 numbers within rounding (the dedup pass
   removes at most 4 of the 17 unmatched-at-50 m features and at
   most 4 of the 45 unmatched-at-25 m features, all of which are
   already inside the matched bucket per §5.5 — so the unmatched
   count should not change at all unless `keep_only` is used).
3. **Within-student vs across-student decomposition** of the
   accepted merges: should be 100 % within-student per §5.3.
4. **Per-map count**: K-35-052-4 = 135, K-35-053-3 = 213,
   K-35-062-2 = 191 - merges, K-35-078-1 = 21. (Lachlan Hanley's
   four candidate clusters all sit on K-35-062-2, so any merges
   reduce the K-35-062-2 count.)

### 6.5 What this enables for the paper

After the dedup pass and the curator-GT match-rate analysis, the
GS-side student-FP narrative for the paper is:

- Student review on the GS sheets achieves **~97 % match rate**
  against the curator-corrected sub-metre GT at 50 m tolerance,
  consistent with Sobotkova 2023.
- Of the 17 unmatched Hairy points at 50 m, 4 are within-student
  duplicates (Lachlan Hanley, K-35-062-2, all "Hairy brown
  circle") removed by the dedup pass; the residual 13 are
  candidates for a per-feature inspection (the "true student FP"
  set, ~2.3 % of 560).
- The 262 non-Hairy points are excluded as a different feature
  class (provenance pending §8.1) — they would inflate the
  apparent student-FP rate from 2.3 % to 33 % if naively
  included, which is what the user's prior framing was about.

## 7. Pre-execution checklist

Tick each item with the user before running anything that writes a
file. Items 1–4 are user-confirmation; items 5–6 are operational.

1. **PENDING (user)**: Confirm the 822 vs 848 feature-count gap
   (§3.5) is acceptable as a count-discrepancy note (i.e. the
   audit's 848 figure was approximate, or used a different bounds
   rule). If 848 is authoritative, the smoke test must be redone
   with whichever bounds-rule yields 848.
2. **PENDING (user)**: Confirm the Hairy-only filter (§4.4) as the
   pre-dedup symbol filter, OR specify an alternative. The 55-map
   reference uses Hairy-only; departing from this here would create
   a cross-corpus inconsistency that would need explicit
   methodological justification.
3. **PENDING (user)**: Approve the recommended dedup radius sweep
   (50 m primary; 25 m and 75 m sensitivity). The smoke test
   suggests dedup is essentially a 4-cluster cleanup at any
   reasonable threshold; sensitivity sweep is mostly demonstration.
4. **PENDING (user)**: Approve the output paths (§4.5):
   `inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson`
   and `results/gs-gt-duplicate-review/`.
5. **OPERATIONAL**: The raw-data directory
   `inputs/raw-student-review-production-maps/` is currently
   untracked in git. Per the project policy "All API-run outputs
   must be committed", the raw shapefiles should be either (a)
   committed as part of this work, or (b) explicitly archived
   (with a justification for not committing — e.g. shapefile
   licensing or size). Recommend: commit, since they are small
   (<27 MB total) and the project already commits comparable
   reference data.
6. **OPERATIONAL**: The dedup pass requires a Streamlit UI session
   (interactive review); the user must run it locally on a machine
   with raster access. The 4 candidate clusters at 50 m can be
   reviewed in well under a minute.

## 8. Open questions for the user

These are blockers — please respond before any execution.

### 8.1 Provenance of the 262 non-Hairy "Mound" features

What were the non-Hairy `MpSymbl` values intended to mark? The five
hypotheses considered:

- **(a) Different map series**: students reviewed both the Russian
  1:50k topo sheet AND a different sheet for these areas (e.g.
  Bulgarian topo); the non-Hairy symbology may be from the second
  series. The `Source` field uniformly says "TopomapRU 1:50k", which
  contradicts (a) unless the field was set automatically and
  inaccurately.
- **(b) Earlier protocol revision**: the digitisation campaign may
  have changed its symbol vocabulary mid-stream; the non-Hairy
  variants may be from before the "Hairy" prefix was standardised.
  Date ranges per student show overlap (same students contributed
  both Hairy and non-Hairy on the same dates), so this would be a
  same-day protocol switch.
- **(c) Different feature class**: the non-Hairy diamonds /
  triangles may mark non-mound features that students misclassified
  as `Mound` (e.g. benchmarks not on a mound, triangulation
  stations not on a mound). The 55-map reviewers may have caught
  this and excluded them.
- **(d) Test data / training data**: the non-Hairy points may have
  been calibration runs or training-week data that was later
  excluded from the production set.
- **(e) Combined**: multiple causes, not all 262 from the same
  source.

The smoke test's spatial signature (median 1.2 km separation from
nearest Hairy; 0 % co-location at any reasonable radius) rules out
the "they're duplicates of Hairy points" explanation but is
consistent with all five hypotheses above.

### 8.2 Is the `inputs/raw-student-review-production-maps/` directory the right source?

The directory was added in commit context that the user described as
"the audit found the raw GS student data here". The smoke test
results assume this is the canonical raw source. **Should I treat the
upstream `MapMoundLoad.R` repository (linked in the README) as more
authoritative if there is any drift?** The R script's URL is
<https://github.com/adivea/MapMoundsDigitized.git>; if the user
prefers re-running from the original processing chain, the dedup
input would change.

### 8.3 Should the dedup also run on the 262 non-Hairy points (separate pass)?

If §8.1 resolves to the non-Hairy points being legitimate mounds that
the 55-map reviewers wrongly excluded, a separate dedup pass would be
needed on the non-Hairy subset before re-incorporating them. The
smoke test for the all-Mound (n = 822) variant in §5.2 found 6
candidate clusters at 50 m (vs 4 for Hairy-only) — a small
incremental scope. If the user wants both, the plan is trivially
extensible: run the dedup on a `--no-hairy-only` variant of the
prepared input and merge the two reviewed outputs.

### 8.4 Should the GS dedup widen to 75 m and 100 m as well?

The 55-map review went to 75 m and stopped (per the
`gt-duplicate-decisions.csv` post-condition: "26 merges (all under
50 m), 70 keep_all (all at 50–75 m)"). 100 m was not reviewed. The
smoke test on GS at 100 m shows 23 candidate clusters (16 % of 75 m
clusters) — much larger than the 75 m result. **My recommendation
is to stop at 75 m** to maintain symmetry with the 55-map workflow,
but the user may want to extend further if the 50–75 m bimodal
signal does not hold on GS data.

### 8.5 Apparent FP rate framing — does the smoke-test answer suffice?

The original framing was: "the 38.7 % apparent FP rate is almost
certainly mostly duplicates; a 25–50 m dedup radius would likely
halve the unmatched feature count". The smoke test contradicts this
strongly: dedup removes at most 4 of 560 Hairy features (0.7 %),
not 50 %. The actual story is the Hairy-vs-non-Hairy filter, not
the dedup. **Should I write the GS-FP narrative for the paper
around this revised understanding (the paper context being §6.5
above), or does the user want a deeper investigation of the 17
residual unmatched Hairy points before concluding?** The 17
residuals could be reviewed individually (Streamlit-style) to
classify each as "true student FP / detector mis-localisation /
GT undercount / borderline".

## 9. Verdict

**READY TO EXECUTE — pending resolution of the open questions in §8.**

The plan is concrete, smoke-tested, and the dedup script and methodology
exist verbatim from the 55-map workflow. No new code is required for the
dedup pass itself; one small pre-filter sidecar (~40 lines) is the only
new artefact. Estimated wall-clock for the full pipeline:

- Pre-filter sidecar implementation + unit-level smoke test: 30 minutes.
- Streamlit dedup review at 50 m: under 1 minute.
- `--apply` step + verification queries: 5 minutes.
- Total: about 40 minutes of operator time, no API spend.

The smoke test result reframes the headline question. Before executing
this plan, the user should be aware that the 38.7 % FP rate is **not**
primarily a duplicates problem — it is a symbol-vocabulary problem,
which the dedup pass alone cannot fix. The Hairy-only filter resolves
it cleanly to a ~3 % residual, of which ~0.7 % can be attributed to
within-student double-marking (the dedup target) and ~2.3 % to
genuinely-unmatched points that would warrant separate per-feature
inspection if the user wants a fully-characterised student-FP rate.

## 10. References

- **Prior dedup script**: `scripts/review_gt_duplicates.py` (1,617
  lines), introducing commit `dea1155f`.
- **Prior cleaned reference**:
  `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  (4,744 features, Δ = −26 from the 4,770-feature original).
- **Prior decisions CSV**: `results/gt-duplicate-review/gt-duplicate-decisions.csv`.
- **Prior diff report**: `results/gt-duplicate-review/gt-duplicate-diff.md`.
- **Raw GS student data**:
  `inputs/raw-student-review-production-maps/Mapmounds/Mounds32635.shp`
  (10,825 features; 822 within the four GS sheets; untracked in git as
  of 2026-04-30).
- **Raw README**: `inputs/raw-student-review-production-maps/README.md`
  (cites upstream `MapMoundLoad.R`).
- **Curator GT**: `inputs/vectors/references/mounds-reference.geojson`
  (569 multipoints in EPSG:32635, exploded to 569 single points).
- **GS rasters**: `inputs/rasters/{K-35-052-4_32635, K-35-053-3_Elenovo,
  K-35-062-2_Rakovski, K-35-078-1_Lesovo}.tif`.
- **Working notes context**: Obs 261 (50 m bimodal merge signal in
  55-map review) at `docs/notes/reflections/working-notes.md`,
  introduced in commit `dea1155f`.
- **Paper-writeup continuity**: `planning/paper-writeup-continuity.md`
  for the broader paper context the GS-side student-FP narrative
  feeds into.
- **Sister plan (FP classification)**:
  `archive/planning-completed-session-81-82/gs-fp-classification-plan-2026-04-29.md` for the
  detection-side FP analysis that this dedup pass should integrate
  with cleanly.
