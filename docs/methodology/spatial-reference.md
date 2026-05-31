# Spatial reference (CRS / projection) — canonical record

> **Last revised**: 2026-05-31 (created after the missing-`crs` F1=0 bug). See
> [§ Changelog](#changelog).

**Purpose**: make the project's coordinate reference systems (CRS) and projections
**explicit and machine-discoverable**, so no consumer — human or script — has to
infer them. Every CRS number below is verified against the actual files (not
inferred). Study area: **burial mounds, Bulgaria.**

## The two CRS, and which artefacts use each

| EPSG | Name | Units | Used by |
|---|---|---|---|
| **32635** | WGS 84 / **UTM Zone 35N** | **metres** | rasters/tiles, evaluation **bounds**, **ground-truth** mounds, and the **evaluation/matching** CRS the scorer reprojects everything to |
| **4326** | **WGS 84** (geographic) | **degrees** | **detection output geojsons** (the model/pipeline outputs; RFC 7946 GeoJSON convention) |

**Verified 2026-05-31** (`gpd.read_file(...).crs` / `rasterio`):

| Artefact | Example path | CRS |
|---|---|---|
| Source rasters | `inputs/rasters/K-35-052-4_32635.tif` (CRS is in the filename) | EPSG:32635 |
| Evaluation bounds (all eras + 55-map) | `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` | EPSG:32635 |
| Ground truth — curator | `inputs/vectors/references/mounds-reference.geojson` | EPSG:32635 |
| Ground truth — 55-map student | `inputs/vectors/references/student-mounds-55maps-reviewed.geojson` | EPSG:32635 |
| Detection outputs | `outputs/gs/gold-standard-v2/consensus/consensus-4of5.geojson` | EPSG:4326 |

## The evaluation pipeline reprojects to a single metric CRS

`scripts/evaluate_detections.py` → `scripts/lib_advanced_metrics.py` defines
`DEFAULT_CRS = "EPSG:32635"` (UTM 35N). `load_geojson()` reprojects **every** input
(detections, GT, bounds) to that CRS before matching, so all detection-to-mound
distances and buffer radii are in **metres**. As of **`metadata_version` 1.2**
(2026-05-31), every `evaluation.json` records this explicitly in a `spatial` block:

```json
"spatial": {
  "evaluation_crs": "EPSG:32635",
  "evaluation_crs_name": "UTM Zone 35N (Bulgaria)",
  "geojson_storage_crs": "EPSG:4326",
  "geojson_storage_note": "GeoJSON is WGS84 (RFC 7946) unless a file declares its own crs member; the scorer reprojects to evaluation_crs before matching."
}
```

## The gotcha that motivated this doc (erratum-class)

A GeoJSON written in **UTM metres (EPSG:32635) with NO `crs` member** is silently
read as WGS84 degrees by GeoPandas (and by `load_geojson`), then mis-reprojected far
off the tile grid → the detections match no mound at any buffer → **F1 = 0 at every
radius** (with faint tile-MCC signal). On 2026-05-31 this was found in several h11
runs (`proposer-verifier-384`/`-512` verified outputs, `e47/flash-high-text-1of5`,
and — as a hard *crash* rather than F1=0 — `consensus-384-UNINTENDED-T1.0`'s voting
outputs). All were **repaired** by reprojecting 32635 → 4326 to match the storage
convention; originals are archived under `archive/data-repairs/<run>-missing-crs/`.
A corpus scan confirmed the defect was **contained to those h11 runs**, not
campaign-wide.

The trap: a missing `crs` member is *correct* for the WGS84 detection geojsons
(RFC 7946 default), so it cannot simply be rejected — the scorer must trust it. The
signal that distinguishes the hazard is **coordinate magnitude**: a first
coordinate with `|x| > 180` cannot be a longitude in degrees.

## Guards now in place

1. **Eval metadata** records `evaluation_crs` + the storage convention (above) —
   `metadata_version` 1.2.
2. **Verifier flag** (`scripts/verify_run_conditions.py`): a condition whose
   detections are projected metres (`|x| > 180`) with no `crs` member raises
   **`crs-missing-utm`** (WARN); an eval that is F1=0 at every buffer raises
   **`f1-all-zero`** (WARN). Both surface for human adjudication.
3. **Storage convention**: detection geojsons are EPSG:4326. A geojson that *must*
   store projected coordinates should declare an explicit `crs` member (e.g.
   `e47/text-baseline` correctly carries `EPSG::32635`, so the scorer reprojects it
   right — the verifier does **not** flag a declared-CRS file).

## How to check a file's CRS

```bash
python -c "import geopandas as gpd; print(gpd.read_file('PATH.geojson').crs)"
python -c "import rasterio; print(rasterio.open('PATH.tif').crs)"
```

A quick magnitude smell-test (no GeoPandas): if the first coordinate's `|x| > 180`
the file is **not** lon/lat degrees — it must declare its CRS.

## Changelog

### 2026-05-31 — Original publication

Created after the missing-`crs` F1=0 bug (and the `consensus-384-t1-0` crash) to make
the project's CRS explicit and well-documented. Records the verified per-artefact CRS,
the evaluation reprojection to EPSG:32635, the new `spatial` eval-metadata block
(`metadata_version` 1.2), and the `crs-missing-utm` / `f1-all-zero` verifier flags.
