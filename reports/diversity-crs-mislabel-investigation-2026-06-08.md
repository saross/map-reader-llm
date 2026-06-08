# Diversity-analysis CRS mislabel: investigation and proposed fix

> **Status**: Report-for-review — **no code change applied**. The proposed
> fix could NOT be proven numerically inert against the published results,
> so per the task brief the code is left untouched and the findings are
> documented here for human review. See [§ Recommendation](#recommendation).

**Date**: 2026-06-08
**Author**: Claude Code (Opus 4.8, 1M context), amd-tower
**Branch**: `fix/diversity-crs-mislabel`
**Scope**: `scripts/analyse_diversity.py` (`consensus_to_gdf`,
`load_replication_passes`), `scripts/merge_passes.py` (`apply_threshold`),
and the published artefacts under `results/phase3c-diversity/track2-text/`.

---

## TL;DR

1. The CRS mislabel in `consensus_to_gdf` is **a live bug today**, not a
   cosmetic label. Re-running `analyse_diversity.py` against the current
   on-disk run data produces **F1 = 0** for every cell, because the
   consensus points (genuinely EPSG:4326) are mislabelled EPSG:32635 and
   therefore fail to intersect the UTM tile bounds — every detection is
   tagged `source_tile = "unknown"`, which collapses the per-map F1 scoring.

2. The mislabel was **numerically inert when the script was written**
   (2026-03-08): at that time `apply_threshold` emitted UTM points, so
   labelling them EPSG:32635 was correct. Commit `8c8e101fc`
   ("fix(crs): reproject consensus GeoJSON to EPSG:4326 at write time",
   2026-04-11) changed `apply_threshold` to emit EPSG:4326 and **silently
   broke** the unguarded label — but `analyse_diversity.py` was never
   re-run afterwards, so the published CSVs predate the breakage.

3. The 20 m dedup/cluster tolerance operates in **true UTM metres** and is
   **correct** in all eras. The bug is confined to the post-clustering
   `source_tile` spatial join in `consensus_to_gdf`.

4. **I cannot prove any fix is numerically inert against the published
   CSV**, because the published F1 numbers cannot be reproduced from the
   data currently on disk by *any* CRS handling (old or new) or scorer
   version. The consensus **geometry** reproduces exactly
   (n_detections 100/100), but the **F1** does not — the published F1 was
   computed on a data/scorer state that has since drifted. Two candidate
   fixes (4326→UTM round-trip vs exact-UTM) also disagree by up to
   **0.011 F1**, so the fix choice is *not* itself inert.

Because inertness is unprovable and the fix has measurable (small)
numerical consequences, this is the explicit "write a report, change no
code" branch of the task.

---

## 1. The actual CRS data flow (verified at source, 2026-06-08)

Traced end to end on `outputs/retest/phase3c/track2-text` (the directory
the published `diversity-analysis-report.json` records as its `study_dir`).

| Stage | Function | Coordinate space | Notes |
|-------|----------|------------------|-------|
| Source run GeoJSON on disk | — | **EPSG:32635 (UTM)** | Embedded `crs` member `urn:ogc:def:crs:EPSG::32635`; coords ~(397541, 4705060); geometries are **Polygons**. |
| Load + CRS guard | `load_replication_passes` | EPSG:32635 | `target_gdf.crs == TARGET_CRS` is already true, so `to_crs(TARGET_CRS)` is a **no-op**. |
| GeoJSON conversion | `gdf_to_features` | EPSG:32635 | Polygons in UTM. |
| Within-pass dedup | `deduplicate_within_pass` | EPSG:32635 | Centroids + 20 m Euclidean tolerance in **true metres**. ✅ |
| Cross-pass cluster | `cluster_across_passes` | EPSG:32635 | Same; 20 m tolerance in metres. ✅ |
| Threshold + output | `apply_threshold` | **EPSG:4326 (lon/lat)** | Reprojects UTM→4326 via `_TO_4326.transform` (added by `8c8e101fc`). Sample output: `[25.753222, 42.491127]`. |
| Consensus → GDF | `consensus_to_gdf` | labelled **EPSG:32635**, actually **4326** | **THE MISLABEL.** Builds `GeoDataFrame(..., crs=TARGET_CRS)` from 4326 points without reprojecting, then `sjoin(intersects)` against `gdf_bounds` (genuine UTM). |

### Where the 20 m tolerance operates — the crux

The task asked specifically whether the 20 m dedup/cluster tolerance might
be silently applied in degrees. **It is not.** `merge_passes` does the
distance work in `euclidean_distance` on the raw centroid coordinates, and
those centroids are UTM eastings/northings (~397 000, ~4 705 000) the whole
way through dedup and clustering. `apply_threshold` only reprojects to 4326
*after* clustering, at output time. The tolerance is therefore genuine
metres in every era of the code. This part of the pipeline is correct and
not at issue.

### The mislabel, demonstrated

```text
consensus points total_bounds (labelled 32635, actually 4326):
    [24.748984  41.833602  26.747751  42.49911 ]   # lon/lat
gdf_bounds total_bounds (genuine 32635 / UTM metres):
    [316259.71  4631497.60  478962.78  4706006.13]
sjoin(intersects): 771 consensus points → 0 matched, 771 'unknown'
```

With every `source_tile == "unknown"`, `calculate_f1_internal`'s per-map
scoping (`gdf_det[gdf_det['source_tile'].str.startswith(map_name)]`)
selects nothing, so all references become false negatives and **F1 = 0**.

---

## 2. Is the mislabel cosmetic or numerical? — Both, depending on era

| Era | `apply_threshold` output | `consensus_to_gdf` label | Result |
|-----|--------------------------|--------------------------|--------|
| Written (2026-03-08, `2d7a26538`) | `Point(cluster["centroid"])` — **UTM** | EPSG:32635 | **Correct.** Label matches reality; join works. |
| Now (post-`8c8e101fc`, 2026-04-11) | UTM→4326 reproject | EPSG:32635 | **Broken.** 4326 points mislabelled UTM; join finds nothing; F1 = 0. |

So the BACKGROUND framing (4326 source, `to_crs` is the explanation,
numbers are correct) is **inverted**: the source is UTM, `to_crs` is a
no-op, and the mislabel is now a *live, output-destroying bug* — it is only
"safe" in the published artefacts because those were produced before the
breaking commit and have not been regenerated since.

### Timeline (git-verified)

| Date | Commit | Event |
|------|--------|-------|
| 2026-03-08 | `2d7a26538` / `650fe9019` | `analyse_diversity.py` written; first CSVs committed. `apply_threshold` emits UTM. Mislabel inert. |
| 2026-03-25 | (report timestamp) | Published `diversity-analysis-report.json` generated (`study_dir = outputs/retest/phase3c/track2-text`, buffer 20). |
| 2026-03-26 | `a371376c1` | CSVs regenerated (200 lines changed, track2). Still UTM-era code. **This is the last real regeneration of the published CSV.** |
| 2026-04-11 | `8c8e101fc` | `apply_threshold` switched to emit EPSG:4326. **`analyse_diversity.py` silently broken from here**, but never re-run. |
| 2026-06-05 | `d4930b0fe` | Docs-only edit under `results/phase3c-diversity/` (thinking-level provenance). CSVs untouched. |

`git diff a371376c1 HEAD -- .../track2-text/diversity-sweep-results.csv`
is empty: **the published CSV has been byte-identical since 2026-03-26.**

---

## 3. Why inertness is unprovable

The task's inertness recipe assumed a label-only change yields
coordinate-identical geometries reproducing the published F1. Three
independent findings break that assumption:

### (a) The published F1 cannot be reproduced from on-disk data

Recomputing condition A (and B, D, E), buffer 20, against the current run
data:

| Path tested | n_detections vs published | F1 vs published |
|-------------|---------------------------|-----------------|
| Current broken code | 100/100 exact | all 0 (bug) |
| Old UTM-direct code (no reproject) | 100/100 exact | 25/25 mismatch (cond A) |
| Exact-UTM (no round-trip) + **current** scorer | 100/100 exact | 22/100 differ |
| Exact-UTM + **period-correct** scorer (`9d3fcbb02`) | 100/100 exact | **100/100 mismatch** |

The consensus **geometry** is byte-stable (n_detections matches in every
cell, every path), confirming the load→dedup→cluster→threshold pipeline is
unchanged. But the published **F1** is unreachable even with the
period-correct scorer. The most likely cause: the run data on disk was
re-materialised / re-scored after publication (commit log:
`fca7f888b` "N=5/10 + diversity-pool consensus + 14-buf+MCC re-score",
`bfdcf512f` "consensus regen + materialise"). The published CSV reflects a
data state that no longer exists on disk in reproducible form.

Without a reproducible baseline, **there is no published number to prove
the fix preserves.**

### (b) The fix choice is not numerically inert

Two honest fixes exist, and they disagree:

* **Fix 1 — reproject 4326→UTM**: load `apply_threshold`'s 4326 output at
  `_GEOJSON_CRS`, `to_crs(TARGET_CRS)` before the join. Minimal, but
  incurs a lossy UTM→4326→UTM round-trip.
* **Fix 2 — exact UTM (no round-trip)**: rebuild `consensus_to_gdf` (and
  its caller) to consume the UTM cluster centroids directly, never touching
  4326. Geometrically exact.

Measured difference between them across 100 cells (4 conds × 5 reps ×
5 thresholds), buffer 20: **max |ΔF1| = 0.011**, with 22 cells differing by
≥ 1e-4. The round-trip drift (sub-metre) flips a handful of detections
across the 20 m matching boundary. A fix that changes F1 by up to 0.011 is
**not** numerically inert by any reasonable definition.

### (c) The "geometrically correct" answer favours the more invasive fix

Fix 2 (exact UTM) is strictly better — it removes the lossy round-trip
entirely. But it requires changing the `consensus_to_gdf` signature and its
caller in `evaluate_condition_replication`, which is more than a label
tweak and warrants the regeneration described below.

---

## Recommendation

Because (a) the published numbers are unreproducible, (b) the candidate
fixes are not mutually inert, and (c) the best fix is non-trivial, **do not
silently patch the label.** Instead:

1. **Confirm the bug is real** (this report demonstrates F1 = 0 on a live
   re-run — that alone proves the current script is broken and must not be
   re-run as-is for any new analysis).

2. **Decide the canonical run data.** Establish which run data the Phase 3c
   diversity results *should* be computed from (the current
   `outputs/retest/phase3c/track2-text` HIGH-thinking data, or an archived
   MINIMAL set), since the published CSV no longer reproduces from disk.

3. **Apply Fix 2 (exact UTM, no round-trip)** as the geometrically correct
   implementation, then **regenerate** the diversity CSVs/reports on
   **sapphire** (bootstrap + permutation tests are forbidden on amd-tower)
   and refresh `results/phase3c-diversity/**` and downstream
   `results/retest/phase3a-consensus/**` per the Document Revision Policy
   (banner + changelog with before→after tables).

4. **Re-check tier rankings and significance.** The mislabel does not
   affect which detections survive (geometry is stable), and the
   round-trip drift is ≤ 0.011 F1, so qualitative conclusions (H9: does
   diversity beat the identical-pass baseline?) are very unlikely to move —
   but this should be confirmed against the regenerated permutation-test
   p-values, not assumed.

5. **Add the regression test** (below) once the fix lands, to pin the CRS
   contract so this cannot silently regress again.

### Proposed Fix 1 patch (minimal, for reference — NOT applied)

If a minimal, low-risk patch is preferred over Fix 2 despite the ≤ 0.011 F1
round-trip drift, the change to `scripts/analyse_diversity.py` is:

```python
# import block
from merge_passes import (
    _GEOJSON_CRS,        # NEW: the CRS apply_threshold actually emits
    apply_threshold,
    cluster_across_passes,
    deduplicate_within_pass,
)

# inside consensus_to_gdf, replace the GeoDataFrame construction:
#   gdf = gpd.GeoDataFrame(props_list, geometry=points, crs=TARGET_CRS)
# with:
    gdf = gpd.GeoDataFrame(props_list, geometry=points, crs=_GEOJSON_CRS)
    if gdf.crs != TARGET_CRS:
        gdf = gdf.to_crs(TARGET_CRS)
```

This makes the label honest (the points *are* `_GEOJSON_CRS` / EPSG:4326)
and reprojects them into the analysis CRS before the join, restoring a
working `source_tile` assignment. It does **not** eliminate the round-trip
precision loss — Fix 2 is preferred for correctness.

### Proposed regression test (for either fix, once landed)

A tier1 test under `tests/test_analyse_diversity_crs.py` that:

* feeds a synthetic UTM cluster through `apply_threshold` →
  `consensus_to_gdf` and asserts the returned GDF is in `TARGET_CRS`
  (EPSG:32635) with UTM-magnitude coordinates (easting > 100 000);
* asserts a detection placed inside a known tile polygon is assigned that
  tile's `source_tile` (not `"unknown"`) — i.e. the spatial join actually
  matches, which is the invariant the mislabel violated;
* pins `apply_threshold`'s output CRS contract (coords in lon/lat range,
  Bulgaria bbox) so a future change there is caught against this consumer.

---

## Reproduction notes

All checks above were run **locally on amd-tower** and are lightweight
(single-buffer F1, geometry diffs, no bootstrap — each well under 30 s),
in compliance with the compute-location policy. Any regeneration of the
diversity CSVs/reports (which involves 1000-iteration BCa bootstraps and
10 000-permutation tests per condition) **must be run on sapphire**, not
here.

Source data inspected: `outputs/retest/phase3c/track2-text/**`
(committed run GeoJSONs). Reference:
`inputs/vectors/references/mounds-reference.geojson`. Bounds:
`inputs/vectors/bounds/validation_bounds.geojson`.

---

## Changelog

### 2026-06-08 — Original publication

First investigation of the `consensus_to_gdf` CRS mislabel flagged for
Session-107 review. Established (via git archaeology + live re-runs) that
the mislabel is a post-`8c8e101fc` live bug producing F1 = 0, that the
published CSVs predate the breaking commit, that the published F1 is
unreproducible from on-disk data, and that the two candidate fixes differ
by up to 0.011 F1. Concluded: report-only, no code change; recommend Fix 2
(exact UTM) plus a regeneration on sapphire and a regression test.
Landed on branch `fix/diversity-crs-mislabel`.
