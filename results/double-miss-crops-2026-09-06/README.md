# Double-miss crops — the seven mounds nobody recorded

> **Last revised**: 2026-09-06 (original publication). See [§ Changelog](#changelog) for revision history.

Verifier-sized crops, cut for the paper, of every **true double-miss** the
Principal Investigator's (PI) two 2026-09-06 audits found: burial mounds that
appear on the Soviet 1:50,000 sheets but were recorded neither by the student
digitisers who built the reference nor by any model run in this study.

There are seven — five from the sampled empty-tile stratum and two from the
complete cluster census. All seven carry the classic kurgan symbol, a hairy
brown circle, and all seven sit far from anything in the reference: the
nearest recorded point in any set (GT or union candidate) is 185–731 m away and the nearest GT point 571–1,518 m, so none is a near-miss
mis-registration.

## Contents

| File | What it is |
|---|---|
| `contact-sheet.png` | The seven crops in a labelled grid — the paper figure. |
| `<audit>_<position>_<tile-stem>.png` | One crop per point at the verifier's own geometry. |
| `<audit>_<position>_<tile-stem>_context.png` | The same centre at 3x the padding, so the surrounding map reads in print. |
| `manifest.csv` | One row per point: audit, position, sheet, symbol, coordinates, raster, window pixel bounds, crop filenames, and the verification-gate results. |
| `contact-sheet-omissions.png`, `manifest-omissions.csv` | Secondary set — see [§ Secondary set](#secondary-set-reference-omissions-the-model-found). |

`audit` is `empty` (the sampled empty stratum) or `census` (the cluster
census); `position` is the adjudication row's `order_index` plus one, so it
matches the reviewer's one-based review order.

## Geometry

The crop geometry is **not invented here**. It is read at run time from the
verifier crop manifests and the two are required to agree:

- `outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/crops/candidate_manifest.json`
- `outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/crops/candidate_manifest.json`

Both record `padding: 75` and `crop_dimensions: "150x150"`.

| Property | Verifier crop | Context crop |
|---|---|---|
| Padding | 75 px | 225 px (3x) |
| Dimensions | 150 x 150 px | 450 x 450 px |
| Ground sample distance | 5.00–5.05 m/px | same |
| Footprint on the ground | ~750–758 m square | ~2.25–2.27 km square |

Crops are read from the full-resolution sheet GeoTIFF with rasterio's
`boundless=True, fill_value=0`, so a point near a sheet edge still yields
exactly the nominal dimensions (black fill beyond the edge) rather than a
truncated image. They are cut by the project's own routine —
`scripts/extract_candidates.py::crop_region`, imported rather than
reimplemented — so a paper crop is pixel-for-pixel the same kind of image the
verifier stage was shown. (`scripts/5_verify_crops.py::crop_candidate` builds
an identical window for these parameters: it uses `context_px // 2` as the
offset with side `context_px`, which for 150 px is the same 75 px offset and
150 px side.)

Every raster was confirmed to be in EPSG:32635, the coordinate reference
system the adjudication points are recorded in, so no reprojection was needed;
the script aborts rather than transform implicitly.

## The seven

| Crop | Sheet | Review tile | Symbol | Nearest recorded point (GT or any union) |
|---|---|---|---|---|
| `empty #145` | K-35-077-2 | `K-35-077-2_x1680_y1008` | hairy brown circle | 346 m |
| `empty #147` | K-35-051-3 | `K-35-051-3_x1008_y1344` | hairy brown circle | 572 m |
| `empty #191` | K-35-067-4 | `K-35-067-4_x2352_y2688` | hairy brown circle | 731 m |
| `empty #350` | K-35-051-3 | `K-35-051-3_x1008_y3360` | hairy brown circle | 223 m |
| `empty #382` | K-35-055-2 | `K-35-055-2_x2688_y0` | hairy brown circle | 476 m |
| `census #46` | K-35-052-2 | `K-35-052-2_x1344_y336` | hairy brown circle | 315 m |
| `census #207` | K-35-063-1_Granit_4326 | `K-35-063-1_Granit_4326_x3024_y672` | hairy brown circle | 185 m |

## Verification gates

All three gates passed on the run that produced these files.

1. **Centre round-trip** — each crop's centre position, taken back through the
   raster affine transform, must land within 1 m of the source easting and
   northing. Worst residual: **0.000000 m**.
   Reported alongside, and *not* gated: the distance from each point to the
   centre of the raster pixel it falls in, at most **2.52 m** here. That is
   pixel quantisation inherent to a ~5 m ground sample distance, not a
   registration error — a crop cannot be centred more finely than one pixel.
2. **Manifest row count** — exactly 7 rows. Passed (7 in the secondary set too).
3. **Crop dimensions** — every primary Portable Network Graphics (PNG) file
   measures exactly the manifests' `crop_dimensions`. Passed, 7/7 at
   150 x 150 px.

## Secondary set: reference omissions the model found

`contact-sheet-omissions.png` and `manifest-omissions.csv` cover a different,
clearly separated question: the census marks that are missing from the
reference but that a model **did** record — six adjudicated `detected` and one
`proposed-but-filtered`. These are not double-misses; they are omissions in
the human reference that the pipeline caught. The nearest recorded point — a model detection — is 1–6 m, while the nearest reference point is 68–633 m
for all seven, which is the signature of a mound the reference records
slightly off rather than not at all in some cases; read the census
adjudication for the per-mark reasoning.

| Crop | Sheet | Review tile | Symbol | Nearest recorded point (GT or any union) |
|---|---|---|---|---|
| `census #77` | K-35-053-2 | `K-35-053-2_x3360_y2352` | hairy brown circle | 2 m |
| `census #127` | K-35-054-4_Voynika | `K-35-054-4_Voynika_x672_y336` | hairy brown circle | 4 m |
| `census #252` | K-35-063-4_Skobelevo_4326 | `K-35-063-4_Skobelevo_4326_x1680_y2016` | hairy black square with a dot inside | 1 m |
| `census #380` | K-35-067-4 | `K-35-067-4_x2688_y1344` | hairy brown circle | 6 m |
| `census #426` | K-35-076-1 | `K-35-076-1_x1344_y0` | hairy brown circle | 3 m |
| `census #458` | K-35-077-2 | `K-35-077-2_x1008_y2688` | hairy brown circle | 5 m |
| `census #462` | K-35-077-2 | `K-35-077-2_x2016_y3360` | hairy brown circle | 3 m |

## Provenance

| Source | Path / commit |
|---|---|
| Empty-stratum adjudication (5 marks) | `results/empty-tile-audit/adjudication.json` |
| Cluster-census adjudication (2 marks) | `results/cluster-audit/adjudication.json` |
| Adjudication protocol | `planning/student-baseline-2026-08-31.md` § 5b |
| Reference used for the nearest-neighbour classing | `inputs/vectors/references/best-available-gt-55maps.geojson` |
| Sheet GeoTIFFs | `inputs/rasters/Russian1981_32635/<sheet>.tif` |
| Empty-tile adjudication landed | `dba5b1bcf` — *feat(audit): adjudicate the empty-tile marks; Phase 2 closed at 500 tiles* |
| Census mode landed | `130ec28c8` — *feat(audit): census mode — additional sightings, flags, edge-safety list* |
| PI re-review of the five confirmed | `2eca853a7` — *results(empty-tile-audit): re-review of the five double-misses — all confirmed* |

## Reproducing

```bash
python scripts/cut_double_miss_crops.py
```

Regenerates every file in this directory and re-runs the three gates, exiting
non-zero if any fails. No Application Programming Interface (API) calls and no
network access; it reads the two adjudication files, the two crop manifests,
and six sheet GeoTIFFs. Pass `--no-omissions` for the primary set alone.

## Changelog

### 2026-09-06 — Original publication

Created by `scripts/cut_double_miss_crops.py` v1.0.0 on the local workstation
(amd-tower); all 55 sheet GeoTIFFs were already present under
`inputs/rasters/Russian1981_32635/`, so no work was offloaded to sapphire and
no raster was copied into the repository.

Initial state: 7 verifier-geometry crops, 7 context crops, `manifest.csv`,
`contact-sheet.png`, plus the secondary set (7 + 7 crops,
`manifest-omissions.csv`, `contact-sheet-omissions.png`). All three
verification gates passed.

One departure from the commissioning brief is worth recording. The brief named
`scripts/5_verify_crops.py::crop_candidate` as the routine to reuse, but the
`padding` and `crop_dimensions` fields recorded in the crop manifests are
written by `scripts/extract_candidates.py`, and it is that script's
`crop_region` which actually cut the verifier's crops. `crop_region` is
therefore what this script imports. The two functions build the same window at
these parameters, so the choice does not change a pixel; it changes which
function the provenance chain honestly points at.
