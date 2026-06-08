# Spatial reference (CRS / projection) — canonical record

> **Last revised**: 2026-06-08 (added the consensus-path CRS contract +
> `apply_threshold`→`consensus_to_gdf` mislabel record; Stage-0 fix). See
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

## The consensus voting path — an *in-memory* CRS contract (2026-06-08)

The gotcha above is about CRS on **disk** (a stored GeoJSON with the wrong/missing
`crs`). A second, distinct hazard lives **in memory**, at the boundary *between*
functions, and it bit the consensus path:

- `scripts/merge_passes.py` clusters in the **analysis CRS (EPSG:32635, metres)** —
  it *assumes* its input geometries are already UTM (it computes the 20 m
  dedup/cluster tolerance as a plain Euclidean distance on raw coordinates; the
  vestigial `coords_are_geographic`/`geojson_coords_to_utm` helpers are **not**
  wired into the production path). `apply_threshold()` then **reprojects the cluster
  centroids to EPSG:4326** before returning them (commit `8c8e101fc`, 2026-04-11,
  for RFC 7946 storage compliance).
- `scripts/analyse_diversity.py:consensus_to_gdf()` **consumes** `apply_threshold`'s
  in-memory output and must reproject it **back to the analysis CRS (32635)** before
  the metric spatial join against the UTM tile bounds.

**The incident**: `consensus_to_gdf` was written (2026-03-08) when `apply_threshold`
still returned UTM, so it labelled the output `EPSG:32635` *without reprojecting* —
correct at the time. The `8c8e101fc` change to `apply_threshold` (a month later)
**silently broke** it: the now-4326 points, mislabelled as 32635, landed ~5×10⁵ m off
the grid → the intersects-join matched no tile → `source_tile = "unknown"` for every
detection → **F1 = 0 on any live re-run**. It went undetected because the **published
Phase 3c diversity CSVs predate the break** (2026-03-26) and the script was never
re-run; the `results/phase3c-diversity/**` numbers are correct and were
independently confirmed via the standard scorer (`evaluate_detections.py`, which
handles CRS correctly) to ~0.001 F1. Full archaeology:
`reports/diversity-crs-mislabel-investigation-2026-06-08.md`.

**Stage-0 fix** (2026-06-08): `consensus_to_gdf` now declares the points
`EPSG:4326` (honestly, what `apply_threshold` emits) and `.to_crs(TARGET_CRS)`
before the join. Pinned by `tests/test_analyse_diversity_crs.py` (asserts both
`apply_threshold`'s 4326 output contract and `consensus_to_gdf`'s reproject-and-join
contract), so a future change like `8c8e101fc` fails a test instead of corrupting
results. The published CSVs are **authoritative as-is** and were **not** regenerated.

**The principle (carry CRS with the geometry).** The root cause was CRS tracked
*out-of-band* — geometries flowing as bare dicts/tuples with no CRS metadata, so a
producer's CRS change could not be caught by the consumer. The durable contract:

1. **Geometry carries its CRS** (GeoDataFrames with a populated `.crs`); reprojection
   is always explicit (`.to_crs`), never a relabel.
2. **One analysis CRS, resolved once and threaded** — never assumed. Today that is
   the hard-coded `EPSG:32635` (Bulgaria, UTM 35N) in ~89 scripts; for a *generalised*
   pipeline it must be **derived** from the data (UTM-zone auto-select) or passed
   explicitly, because the metric tolerance (20 m) is only meaningful in the right
   metric CRS.
3. **Separate storage egress (→4326, RFC 7946) from analysis (stay in the analysis
   CRS)** — analysis should not round-trip through 4326.
4. **Respect the declared CRS; never guess** from coordinate magnitude.

Stages 1–2 of this principle (a shared `lib_crs`, retiring the 89-script hard-code,
deriving the CRS from data) are scoped in
[`planning/generalised-pipeline-roadmap.md`](../../planning/generalised-pipeline-roadmap.md)
as a prerequisite workstream for the "bring-your-own-maps" pipeline.

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

### 2026-06-08 — Consensus-path CRS contract + mislabel fix

**Trigger**: a CRS investigation (Session 106) found `analyse_diversity.consensus_to_gdf`
mislabelled `apply_threshold`'s output, silently broken since the `8c8e101fc`
(2026-04-11) change made `apply_threshold` emit EPSG:4326. Re-running the diversity
analysis today produced F1=0 (all detections tagged `source_tile = "unknown"`).

**What changed**: added the "consensus voting path — in-memory CRS contract" section
(the producer/consumer boundary, the incident, the principle of carrying CRS with the
geometry). Landed the Stage-0 fix in `consensus_to_gdf` (declare 4326 + reproject to
the analysis CRS) with a regression test `tests/test_analyse_diversity_crs.py`.

**What did NOT change**: the per-artefact CRS table, the evaluation-CRS reprojection,
and the on-disk missing-`crs` guards are unchanged. The **published Phase 3c diversity
CSVs are authoritative as-is and were NOT regenerated** — they predate the break and
were independently confirmed correct via `evaluate_detections.py` (~0.001 F1). The
fix only restores the legacy script's runnability.

**Commit**: landed on branch `fix/diversity-crs-mislabel` (PR #10).

### 2026-05-31 — Original publication

Created after the missing-`crs` F1=0 bug (and the `consensus-384-t1-0` crash) to make
the project's CRS explicit and well-documented. Records the verified per-artefact CRS,
the evaluation reprojection to EPSG:32635, the new `spatial` eval-metadata block
(`metadata_version` 1.2), and the `crs-missing-utm` / `f1-all-zero` verifier flags.
