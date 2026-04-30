#!/usr/bin/env python3
"""Build the pre-dedup Hairy-filtered student-mound GT for the 4 GS map sheets.

Pipeline overview
-----------------

1. Read the raw 59-sheet student-digitisation shapefile
   (``inputs/raw-student-review-production-maps/Mapmounds/Mounds32635.shp``,
   10,825 features, EPSG:32635).
2. Apply the canonical "Hairy" filter:

   - ``FetrTyp == 'Mound'`` (excludes 'Surface feature' and 'Other').
   - ``MpSymbl`` contains the case-insensitive substring ``"Hairy"``
     (i.e. the student-vocabulary subset of map symbols that
     represents above-ground burial-mound markers).

3. Build a four-row bounds GeoDataFrame from the four GS rasters in
   ``inputs/rasters/`` and persist it to
   ``inputs/vectors/bounds/gs-4maps-sheet-bounds.geojson`` for downstream
   reuse (per-sheet evaluation, raster context lookup).
4. Spatial-join the Hairy-filtered features against the four-bounds
   frame, attaching ``source_map`` = raster filename stem (e.g.
   ``K-35-052-4_32635``) so the existing review script's
   ``_resolve_raster`` glob (``{map_id}.tif`` under ``inputs/rasters/``)
   matches without code changes.
5. Write the result to
   ``inputs/vectors/references/student-mounds-gs-4maps.geojson`` with the
   same 7-column schema as
   ``inputs/vectors/references/student-mounds-55maps.geojson``
   (pre-review variant — no ``_merged`` / ``_reviewed_subtype`` columns;
   those are added by the manual-review pipeline).

**No deduplication is performed.** The output is the input to the
human-review Streamlit app (see ``scripts/review_gt_duplicates.py`` and
``scripts/launch_gs4maps_gt_dedup_review.sh``).

Schema-matching note
--------------------

The 55-map artefact stores ``source_map`` as a bare sheet ID
(``K-35-042-3``) because its rasters under
``inputs/rasters/Russian1981_32635/`` are named with bare-ID stems
(``K-35-042-3.tif``). The four GS rasters under ``inputs/rasters/`` have
suffixed filenames (``K-35-052-4_32635.tif``,
``K-35-053-3_Elenovo.tif`` etc.), so we deliberately store the **stem**
(``K-35-052-4_32635``) as ``source_map`` to keep raster lookup working
under the existing review script. Downstream analyses that need the
canonical sheet ID can derive it by stripping the suffix at the first
underscore-following-the-third-dash.

Usage
-----

::

    .venv/bin/python scripts/build_student_mounds_gs4.py

Sanity-check counts are printed to stdout.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from shapely.geometry import box

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TARGET_CRS = "EPSG:32635"

_DEFAULT_RAW_SHP = Path(
    "inputs/raw-student-review-production-maps/Mapmounds/Mounds32635.shp"
)
_DEFAULT_RASTERS_DIR = Path("inputs/rasters")
_DEFAULT_BOUNDS_OUT = Path(
    "inputs/vectors/bounds/gs-4maps-sheet-bounds.geojson"
)
_DEFAULT_GT_OUT = Path(
    "inputs/vectors/references/student-mounds-gs-4maps.geojson"
)

# The four GS raster filenames (stems become the ``source_map`` values).
_GS_RASTER_FILENAMES: tuple[str, ...] = (
    "K-35-052-4_32635.tif",
    "K-35-053-3_Elenovo.tif",
    "K-35-062-2_Rakovski.tif",
    "K-35-078-1_Lesovo.tif",
)

# Output column order — must exactly match
# ``inputs/vectors/references/student-mounds-55maps.geojson``.
_OUTPUT_COLUMNS: tuple[str, ...] = (
    "uuid",
    "MapSymbol",
    "FeatureType",
    "source_map",
    "Latitude",
    "Longitude",
    "geometry",
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def build_gs_bounds(
    rasters_dir: Path,
    raster_filenames: tuple[str, ...] = _GS_RASTER_FILENAMES,
    target_crs: str = _TARGET_CRS,
) -> gpd.GeoDataFrame:
    """Build a four-row GS-bounds GeoDataFrame from raster bounding boxes.

    Args:
        rasters_dir: Directory containing the four GS GeoTIFF files.
        raster_filenames: Filenames (relative to ``rasters_dir``) for the
            four GS sheets.
        target_crs: EPSG code that the returned frame must be in. If a
            raster is in a different CRS, its bounds polygon is
            reprojected (but this should not happen — all four are
            authored in EPSG:32635).

    Returns:
        GeoDataFrame with columns ``sheet_id`` (raster filename stem) and
        ``geometry`` (rectangular bounds polygon).
    """
    records: list[dict[str, object]] = []
    for fname in raster_filenames:
        path = rasters_dir / fname
        with rasterio.open(path) as src:
            bounds = src.bounds
            crs = src.crs
        bbox = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
        # One-row mini-GDF so we can reproject cleanly if needed.
        mini = gpd.GeoDataFrame(
            {"sheet_id": [path.stem]},
            geometry=[bbox],
            crs=crs,
        )
        if str(mini.crs) != target_crs:
            mini = mini.to_crs(target_crs)
        records.append(
            {"sheet_id": path.stem, "geometry": mini.geometry.iloc[0]}
        )
    return gpd.GeoDataFrame(records, crs=target_crs)


def apply_hairy_filter(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Apply the canonical Hairy filter to the raw mounds shapefile.

    Selects rows where ``FetrTyp == 'Mound'`` and ``MpSymbl`` contains
    the case-insensitive substring ``"Hairy"``. NaN ``MpSymbl`` values
    are excluded.

    Args:
        gdf: Raw shapefile GeoDataFrame.

    Returns:
        Filtered copy (reset index).
    """
    is_mound = gdf["FetrTyp"].astype(str) == "Mound"
    is_hairy = (
        gdf["MpSymbl"].astype(str).str.contains("Hairy", case=False, na=False)
    )
    return gdf.loc[is_mound & is_hairy].reset_index(drop=True).copy()


def assign_source_map(
    points: gpd.GeoDataFrame,
    bounds: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Spatial-join points against bounds; attach ``source_map`` from sheet_id.

    Points falling inside more than one (overlapping) sheet are
    duplicated by the join — but the four GS sheets do not overlap, so
    in practice each point gets at most one ``source_map`` value.
    Points outside all four sheets are dropped.

    Args:
        points: Hairy-filtered mound points (any CRS — will be aligned
            to ``bounds``).
        bounds: Output of :func:`build_gs_bounds`.

    Returns:
        Subset of ``points`` clipped to the four GS sheets, with
        ``source_map`` column added (= sheet_id).
    """
    if str(points.crs) != str(bounds.crs):
        points = points.to_crs(bounds.crs)
    joined = gpd.sjoin(
        points, bounds[["sheet_id", "geometry"]],
        how="inner", predicate="within",
    )
    joined = joined.drop(columns=["index_right"])
    joined = joined.rename(columns={"sheet_id": "source_map"})
    return joined.reset_index(drop=True)


def conform_to_55maps_schema(
    gdf: gpd.GeoDataFrame,
    columns: tuple[str, ...] = _OUTPUT_COLUMNS,
) -> gpd.GeoDataFrame:
    """Conform the joined frame to the 55-map pre-review schema.

    Renames the raw shapefile's truncated ``MpSymbl`` / ``FetrTyp`` /
    ``Latitud`` / ``Longitd`` columns to their full-name equivalents and
    selects only the canonical seven columns. Any pre-existing columns
    of the canonical names take precedence over their truncated
    counterparts.

    Args:
        gdf: GeoDataFrame post spatial-join (carries the raw shapefile's
            truncated column names plus ``source_map``).
        columns: Output column order.

    Returns:
        GeoDataFrame with exactly ``columns`` in order, EPSG:32635.
    """
    rename_map = {
        "MpSymbl": "MapSymbol",
        "FetrTyp": "FeatureType",
        "Latitud": "Latitude",
        "Longitd": "Longitude",
    }
    out = gdf.copy()
    for src_col, dst_col in rename_map.items():
        if dst_col not in out.columns and src_col in out.columns:
            out = out.rename(columns={src_col: dst_col})
    # uuid in the raw shapefile is float64 (e.g. 1.000050e+18). The
    # 55-map pre-review file stores it as a string. Normalise here so
    # downstream cluster IDs and CSV row keys are stable.
    if "uuid" in out.columns:
        out["uuid"] = out["uuid"].apply(_uuid_to_str)
    missing = [c for c in columns if c not in out.columns]
    if missing:
        raise ValueError(
            f"Missing expected columns after rename: {missing}. "
            f"Have: {list(out.columns)}"
        )
    return out[list(columns)].copy()


def _uuid_to_str(val: object) -> str:
    """Coerce a uuid value to a stable string representation.

    Float uuids that lost precision in the shapefile are rendered as
    fixed-point integers (no scientific notation, no trailing
    ``.0``). Strings pass through unchanged. NaN / None becomes the
    empty string.
    """
    if val is None:
        return ""
    if isinstance(val, float):
        if np.isnan(val):
            return ""
        return f"{int(val)}"
    return str(val)


def count_clusters_at_threshold(
    gdf: gpd.GeoDataFrame,
    threshold_m: float = 50.0,
) -> int:
    """Preview how many duplicate clusters the review app will surface.

    Uses the same per-map cKDTree connected-components predicate as
    ``review_gt_duplicates.build_clusters`` (>= 2 members within
    ``threshold_m``).

    Args:
        gdf: Pre-review GT (must carry ``source_map`` and metric CRS).
        threshold_m: Pairwise distance threshold (default 50 m).

    Returns:
        Number of multi-point clusters across all sheets.
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    from scipy.spatial import cKDTree

    n_clusters = 0
    for _map_id, group in gdf.groupby("source_map", sort=True, dropna=True):
        group = group.reset_index(drop=True)
        n = len(group)
        if n < 2:
            continue
        coords = np.array(
            [(geom.x, geom.y) for geom in group.geometry], dtype=np.float64,
        )
        tree = cKDTree(coords)
        pairs = tree.query_pairs(r=threshold_m, output_type="set")
        if not pairs:
            continue
        rows = [p[0] for p in pairs] + [p[1] for p in pairs]
        cols = [p[1] for p in pairs] + [p[0] for p in pairs]
        adj = coo_matrix(([1] * len(rows), (rows, cols)), shape=(n, n))
        n_comp, labels = connected_components(adj, directed=False)
        for comp_id in range(n_comp):
            idxs = np.where(labels == comp_id)[0]
            if len(idxs) >= 2:
                n_clusters += 1
    return n_clusters


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Run the full build pipeline and emit sanity-check counts.

    Returns:
        0 on success.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw-shp", type=Path, default=_DEFAULT_RAW_SHP,
        help="Path to the raw 59-sheet Mounds32635 shapefile.",
    )
    parser.add_argument(
        "--rasters-dir", type=Path, default=_DEFAULT_RASTERS_DIR,
        help="Directory containing the four GS GeoTIFF files.",
    )
    parser.add_argument(
        "--bounds-out", type=Path, default=_DEFAULT_BOUNDS_OUT,
        help="Output path for the 4-GS sheet-bounds GeoJSON.",
    )
    parser.add_argument(
        "--gt-out", type=Path, default=_DEFAULT_GT_OUT,
        help="Output path for the pre-review Hairy-filtered GT GeoJSON.",
    )
    parser.add_argument(
        "--threshold-m", type=float, default=50.0,
        help="Cluster-preview threshold in metres (default 50 m).",
    )
    args = parser.parse_args(argv)

    print(f"[1/5] Reading raw shapefile: {args.raw_shp}")
    raw = gpd.read_file(args.raw_shp)
    if str(raw.crs) != _TARGET_CRS:
        raw = raw.to_crs(_TARGET_CRS)
    print(f"      Raw feature count: {len(raw):,}")

    print("[2/5] Applying Hairy filter (FetrTyp=='Mound' & MpSymbl~'Hairy')")
    hairy = apply_hairy_filter(raw)
    print(f"      Post-Hairy feature count: {len(hairy):,}")

    print(f"[3/5] Building 4-GS bounds from {args.rasters_dir}")
    bounds = build_gs_bounds(args.rasters_dir)
    args.bounds_out.parent.mkdir(parents=True, exist_ok=True)
    bounds.to_file(args.bounds_out, driver="GeoJSON")
    print(f"      Wrote {args.bounds_out} ({len(bounds)} rows)")

    print("[4/5] Spatial-joining Hairy-filtered features to 4 GS sheets")
    joined = assign_source_map(hairy, bounds)
    print(f"      Post-join feature count: {len(joined):,}")
    per_sheet = (
        joined.groupby("source_map", dropna=False)
        .size().sort_values(ascending=False)
    )
    print("      Per-sheet breakdown:")
    for sheet, n in per_sheet.items():
        print(f"        {sheet:30s} {n:>5,}")

    print("[5/5] Conforming to 55-map pre-review schema and writing GT")
    out_gt = conform_to_55maps_schema(joined)
    args.gt_out.parent.mkdir(parents=True, exist_ok=True)
    out_gt.to_file(args.gt_out, driver="GeoJSON")
    print(f"      Wrote {args.gt_out} ({len(out_gt):,} features)")

    n_clusters = count_clusters_at_threshold(out_gt, args.threshold_m)
    flag = " [FLAG: > 20 clusters]" if n_clusters > 20 else ""
    print(
        f"\nDuplicate-cluster preview at {args.threshold_m:.0f} m: "
        f"{n_clusters} multi-point cluster(s){flag}"
    )
    print(
        "(This is just a preview of what Shawn will see in the Streamlit "
        "app; no dedup is performed here.)"
    )

    # Light schema cross-check vs the 55-map pre-review file.
    fiftyfive = Path(
        "inputs/vectors/references/student-mounds-55maps.geojson"
    )
    if fiftyfive.exists():
        ref = gpd.read_file(fiftyfive)
        if list(ref.columns) != list(out_gt.columns):
            print(
                f"\nWARNING: column order differs from 55-map pre-review.\n"
                f"  55-map: {list(ref.columns)}\n"
                f"  GS-4 :  {list(out_gt.columns)}"
            )
        else:
            print("\nSchema cross-check vs 55-map pre-review: OK")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
