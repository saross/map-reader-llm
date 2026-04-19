#!/usr/bin/env python3
"""Streamlit app for manually reviewing student-GT duplicate clusters.

Identifies pairs/clusters of student-annotated burial-mound points
that are closer than a user-specified threshold (default 50 m) and
presents them for human classification. Students sometimes
double-mark a single physical mound; the spacing analysis on the
55-map student GT found 56 mounds (1.2 %) with nearest-neighbour
<50 m and a minimum spacing of 1.7 m, consistent with rare but real
double-marking errors. Reviewing and cleaning these improves the
validity of tight-buffer F1 evaluation by removing match-zone
overlap artefacts.

Companion script: same entry point with ``--apply`` runs
post-processing only (no Streamlit), consuming the decisions CSV to
produce a cleaned ``*-reviewed.geojson`` sidecar file + a diff
report.

Usage (interactive review)::

    streamlit run scripts/review_gt_duplicates.py -- \\
        --ground-truth inputs/vectors/references/student-mounds-55maps.geojson \\
        --rasters-dir inputs/rasters/Russian1981_32635 \\
        --threshold-m 50

Usage (apply decisions)::

    python scripts/review_gt_duplicates.py --apply \\
        --ground-truth inputs/vectors/references/student-mounds-55maps.geojson \\
        --decisions results/gt-duplicate-review/gt-duplicate-decisions.csv

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import random
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

if TYPE_CHECKING:
    from PIL.Image import Image as PILImage

# ---------------------------------------------------------------------------
# Path setup — allow imports from scripts/ siblings
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from lib_consensus import ensure_utm_crs  # noqa: E402

# =========================================================================
# Constants
# =========================================================================

_TARGET_CRS = "EPSG:32635"
_DEFAULT_THRESHOLD_M = 50.0
_DEFAULT_CONTEXT_M = 300.0
_DEFAULT_GT = "inputs/vectors/references/student-mounds-55maps.geojson"
_DEFAULT_RASTERS = "inputs/rasters/Russian1981_32635"
_DEFAULT_OUTPUT = "results/gt-duplicate-review/gt-duplicate-decisions.csv"
_DEFAULT_CLEAN_GT = (
    "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
)
_DEFAULT_DIFF = "results/gt-duplicate-review/gt-duplicate-diff.md"

# Mound subtypes used when merging (matches review_candidates.py vocabulary).
# Keys are the canonical subtype IDs saved to the decisions CSV; values are
# (display label, keyboard shortcut).
SUBTYPE_OPTIONS: dict[str, tuple[str, str]] = {
    "burial_mound": ("Burial mound", "f"),
    "bench_mark_on_mound": ("Bench mark on mound", "d"),
    "trig_point_on_mound": ("Trig point on mound", "s"),
    "settlement_mound": ("Settlement mound", "a"),
    "other": ("Other / uncertain subtype", "o"),
}

# Map the student GT's MapSymbol vocabulary to canonical subtypes. Used to
# suggest the default merge subtype (consensus of cluster members).
MAPSYMBOL_TO_SUBTYPE: dict[str, str] = {
    "Hairy brown circle": "burial_mound",
    "Hairy black diamond with a dot inside": "bench_mark_on_mound",
    "Hairy black triangle with a dot inside": "trig_point_on_mound",
    "Hairy black square with a dot inside": "settlement_mound",
    "Hairy brown circle (has black diamond on top)": "bench_mark_on_mound",
    "Other (describe in annotation) (hairy black circle)": "other",
}

# Decision codes written to the CSV
DECISION_KEEP_ALL = "keep_all"
DECISION_MERGE = "merge"
DECISION_KEEP_ONLY = "keep_only"
DECISION_UNCERTAIN = "uncertain"

_MARKER_COLOURS = [
    (220, 20, 20),    # red
    (20, 60, 220),    # blue
    (20, 180, 40),    # green
    (230, 130, 20),   # orange
    (180, 20, 180),   # magenta
    (20, 180, 180),   # cyan
    (200, 200, 20),   # yellow
    (120, 60, 20),    # brown
    (120, 120, 120),  # grey
]


# =========================================================================
# Data classes
# =========================================================================


@dataclass
class Cluster:
    """A group of GT points whose pairwise NN graph is connected at threshold."""

    cluster_id: str
    map_id: str
    point_ids: list[int]
    coords: list[tuple[float, float]]
    feature_types: list[str]
    map_symbols: list[str]
    pairwise_distances_m: list[float]
    centroid: tuple[float, float]

    @property
    def n_points(self) -> int:
        return len(self.point_ids)

    def suggest_subtype(self) -> str:
        """Consensus subtype across members; ties broken deterministically.

        The tie-break RNG is seeded with ``cluster_id`` so the suggestion is
        reproducible. Returns one of the keys from ``SUBTYPE_OPTIONS``.
        """
        mapped = [
            MAPSYMBOL_TO_SUBTYPE.get(s, "other") for s in self.map_symbols
        ]
        counts = Counter(mapped)
        top_n = counts.most_common()
        if len(top_n) == 1 or top_n[0][1] > top_n[1][1]:
            return top_n[0][0]
        tied = [subtype for subtype, n in top_n if n == top_n[0][1]]
        rng = random.Random(self.cluster_id)
        return rng.choice(sorted(tied))


# =========================================================================
# Data loading + clustering
# =========================================================================


def load_gt(path: Path) -> gpd.GeoDataFrame:
    """Load student GT, reproject to target UTM, attach stable row id.

    The returned frame carries an integer ``_gt_row_id`` column used as the
    canonical identifier throughout the review pipeline (so decisions remain
    valid even if the input ordering changes).
    """
    gdf = gpd.read_file(path)
    gdf = ensure_utm_crs(gdf, target_crs=_TARGET_CRS)
    gdf = gdf.reset_index(drop=True)
    gdf["_gt_row_id"] = gdf.index.astype(int)
    return gdf


def build_clusters(
    gdf: gpd.GeoDataFrame,
    threshold_m: float,
) -> list[Cluster]:
    """Group GT points into connected components at the NN threshold.

    Clustering is per-map (two points on different maps never join even if
    they share coordinates, which shouldn't occur under the 55-map
    partitioning but is guarded against for safety). Isolated points (no
    neighbour within threshold) are excluded from the returned list — only
    multi-point clusters need human review.

    Args:
        gdf: GT loaded via ``load_gt``; must be in a metric CRS and carry
            ``_gt_row_id`` + ``source_map`` columns.
        threshold_m: Pairwise distance threshold.

    Returns:
        Clusters sorted deterministically by ``(map_id, min(point_ids))``.
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    from scipy.spatial import cKDTree

    # Warn loudly if any rows have no source_map — groupby(dropna=True)
    # would silently skip them, leaving those points unreviewed.
    n_missing = int(gdf["source_map"].isna().sum())
    if n_missing:
        print(
            f"Warning: {n_missing} GT rows have no source_map; they will "
            f"be excluded from clustering.",
            file=sys.stderr,
        )

    clusters: list[Cluster] = []
    for map_id, group in gdf.groupby("source_map", sort=True, dropna=True):
        group = group.reset_index(drop=True)
        n = len(group)
        if n < 2:
            continue
        coords = np.array(
            [(geom.x, geom.y) for geom in group.geometry],
            dtype=np.float64,
        )
        tree = cKDTree(coords)
        pairs = tree.query_pairs(r=threshold_m, output_type="set")
        if not pairs:
            continue
        # Build sparse undirected adjacency for connected-components
        rows = [p[0] for p in pairs] + [p[1] for p in pairs]
        cols = [p[1] for p in pairs] + [p[0] for p in pairs]
        data = [1] * len(rows)
        adj = coo_matrix((data, (rows, cols)), shape=(n, n))
        n_comp, labels = connected_components(adj, directed=False)
        for comp_id in range(n_comp):
            idxs = np.where(labels == comp_id)[0]
            if len(idxs) < 2:
                continue
            idxs = sorted(int(i) for i in idxs)  # stable ordering
            member_rows = [int(group.iloc[i]["_gt_row_id"]) for i in idxs]
            member_coords = [
                (float(coords[i][0]), float(coords[i][1])) for i in idxs
            ]
            member_fts = [str(group.iloc[i]["FeatureType"]) for i in idxs]
            member_symbols = [
                str(group.iloc[i].get("MapSymbol", "")) for i in idxs
            ]
            pd_m: list[float] = []
            for a in range(len(idxs)):
                for b in range(a + 1, len(idxs)):
                    dx = coords[idxs[a]][0] - coords[idxs[b]][0]
                    dy = coords[idxs[a]][1] - coords[idxs[b]][1]
                    pd_m.append(round(float(np.hypot(dx, dy)), 2))
            cx = float(np.mean([c[0] for c in member_coords]))
            cy = float(np.mean([c[1] for c in member_coords]))
            cid = f"{map_id}_c{min(member_rows):05d}"
            clusters.append(
                Cluster(
                    cluster_id=cid,
                    map_id=str(map_id),
                    point_ids=member_rows,
                    coords=member_coords,
                    feature_types=member_fts,
                    map_symbols=member_symbols,
                    pairwise_distances_m=pd_m,
                    centroid=(cx, cy),
                )
            )
    clusters.sort(key=lambda c: (c.map_id, c.point_ids[0]))
    return clusters


# =========================================================================
# Raster rendering (lazy imports — not needed for clustering or apply paths)
# =========================================================================


def render_cluster_image(
    cluster: Cluster,
    rasters_dir: Path,
    context_m: float,
    display_px: int = 600,
) -> "PILImage":
    """Render a context crop around the cluster with numbered markers.

    Reads from the full-resolution GeoTIFF with ``boundless=True`` so the
    crop is always exactly the requested size even if the cluster sits near
    a raster edge, then upscales to ``display_px`` square via LANCZOS so
    markers and the underlying map symbols are both legibly sized for
    manual review. Overlays a numbered circle for each cluster member.

    Falls back to a grey placeholder with relative-coordinate markers if the
    raster cannot be located — keeps the review flow unblocked.
    """
    from PIL import Image, ImageDraw
    import rasterio
    from rasterio.windows import Window

    # Prefer the raster whose extent covers the cluster centroid with
    # the most margin — this automatically picks the neighbouring sheet
    # when the cluster sits near the edge of its declared source_map,
    # avoiding the boundless-read black fill that makes edge clusters
    # hard to review. Fall back to the source_map raster if no other
    # coverage exists (cluster is at a truly-unique spot).
    cx_centroid, cy_centroid = cluster.centroid
    raster_path = _best_raster_for_point(
        rasters_dir, cx_centroid, cy_centroid,
    )
    if raster_path is None:
        raster_path = _resolve_raster(rasters_dir, cluster.map_id)
    if raster_path is None:
        return _placeholder_image(cluster, size=display_px)

    with rasterio.open(raster_path) as src:
        cx_m, cy_m = cluster.centroid
        row_f, col_f = src.index(cx_m, cy_m)
        # rasterio's index() can return floats in newer versions; coerce
        # so Window arithmetic below stays integer.
        row_c = int(round(float(row_f)))
        col_c = int(round(float(col_f)))
        res_m_per_px = abs(src.transform.a)
        half_px = max(1, int(round(context_m / 2 / res_m_per_px)))
        window = Window(
            col_c - half_px, row_c - half_px, half_px * 2, half_px * 2,
        )
        arr = src.read(window=window, boundless=True, fill_value=0)
        n_bands = arr.shape[0]
        if n_bands >= 3:
            img_data = arr[:3].transpose(1, 2, 0)
        elif n_bands == 1:
            g = arr[0]
            img_data = np.stack([g, g, g], axis=-1)
        elif n_bands == 2:
            # Two-band (e.g. grey + alpha): replicate grey for RGB.
            g = arr[0]
            img_data = np.stack([g, g, g], axis=-1)
        else:
            # 0-band shouldn't happen; fall through to placeholder
            return _placeholder_image(cluster)
        raw_img = Image.fromarray(img_data.astype(np.uint8)).convert("RGB")
        # Upscale to a display-friendly size before drawing markers. This
        # keeps the map symbols legible at the ~5 m/px raster resolution
        # (a 300 m crop is only ~60 raw pixels).
        scale = display_px / raw_img.size[0] if raw_img.size[0] > 0 else 1.0
        img = raw_img.resize((display_px, display_px), Image.LANCZOS)

        draw = ImageDraw.Draw(img)
        marker_r = max(10, int(display_px * 0.025))
        for i, (px_m, py_m) in enumerate(cluster.coords):
            pt_row_f, pt_col_f = src.index(px_m, py_m)
            pt_row = float(pt_row_f)
            pt_col = float(pt_col_f)
            lx = int(round((pt_col - (col_c - half_px)) * scale))
            ly = int(round((pt_row - (row_c - half_px)) * scale))
            colour = _MARKER_COLOURS[i % len(_MARKER_COLOURS)]
            draw.ellipse(
                [lx - marker_r, ly - marker_r, lx + marker_r, ly + marker_r],
                outline=colour, width=3,
            )
            draw.text(
                (lx + marker_r + 3, ly - marker_r - 3),
                str(i + 1),
                fill=colour,
            )
        return img


def _resolve_raster(rasters_dir: Path, map_id: str) -> Path | None:
    """Find ``{map_id}.tif`` directly under ``rasters_dir`` or recursively."""
    direct = rasters_dir / f"{map_id}.tif"
    if direct.is_file():
        return direct
    found = list(rasters_dir.rglob(f"{map_id}.tif"))
    return found[0] if found else None


# Cache of (raster_path, bounds) for a given rasters_dir. First call per
# dir reads metadata from every TIF; subsequent calls are O(1).
_RASTER_BOUNDS_CACHE: dict[str, list[tuple[Path, tuple[float, ...]]]] = {}


def _collect_raster_bounds(
    rasters_dir: Path,
) -> list[tuple[Path, tuple[float, float, float, float]]]:
    """Gather (path, (left, bottom, right, top)) for every TIF in dir.

    Cached on the resolved path string so repeat calls within a
    session are effectively free. The rasterio read is ~1 ms per file
    on SSD so even 55-sheet scans take <100 ms uncached.
    """
    import rasterio

    key = str(rasters_dir.resolve())
    if key in _RASTER_BOUNDS_CACHE:
        return _RASTER_BOUNDS_CACHE[key]
    out: list[tuple[Path, tuple[float, float, float, float]]] = []
    for p in sorted(rasters_dir.glob("*.tif")):
        try:
            with rasterio.open(p) as src:
                b = src.bounds
                out.append((p, (float(b.left), float(b.bottom),
                                float(b.right), float(b.top))))
        except Exception:  # noqa: BLE001 — skip unreadable rasters
            continue
    _RASTER_BOUNDS_CACHE[key] = out
    return out


def _best_raster_for_point(
    rasters_dir: Path,
    x: float,
    y: float,
    sample_px: int = 40,
) -> Path | None:
    """Return the raster whose pixels at (x, y) contain the most real content.

    Filtering by the rectangular bounds is not enough: georeferenced
    1:25k map sheets are trapezoids inside rectangular rasters, and
    the pixels outside the trapezoid (still within the rectangular
    extent) are pre-filled with black. A cluster that sits inside the
    rectangular bounds of sheet X may still fall outside X's actual
    mapped area.

    Algorithm:
    1. Filter rasters whose rectangular bounds cover (x, y).
    2. For each candidate, read a small ``sample_px`` × ``sample_px``
       window centred on (x, y) and measure the non-black fraction.
    3. Pick the raster with the most real content. Ties broken by
       largest min-distance to the rectangular edge (deepest inside
       the sheet).

    Returns None if no raster covers the point at all, so callers can
    fall back to the cluster's declared ``source_map``.
    """
    import rasterio
    from rasterio.windows import Window

    bounds_list = _collect_raster_bounds(rasters_dir)
    best: tuple[Path, float, float] | None = None  # (path, real_frac, min_edge)
    for path, (left, bottom, right, top) in bounds_list:
        if not (left <= x <= right and bottom <= y <= top):
            continue
        try:
            with rasterio.open(path) as src:
                row_f, col_f = src.index(x, y)
                row = int(round(float(row_f)))
                col = int(round(float(col_f)))
                window = Window(
                    col - sample_px // 2,
                    row - sample_px // 2,
                    sample_px, sample_px,
                )
                arr = src.read(window=window, boundless=True, fill_value=0)
                if arr.shape[0] == 0:
                    continue
                bands = arr[:3] if arr.shape[0] >= 3 else arr[:1]
                near_black = np.all(bands <= 8, axis=0)
                real_frac = 1.0 - float(near_black.mean())
        except Exception:  # noqa: BLE001 — skip unreadable
            continue
        min_edge = min(x - left, right - x, y - bottom, top - y)
        candidate = (path, real_frac, min_edge)
        if best is None:
            best = candidate
            continue
        # Prefer higher real-content fraction. When ties are close
        # (within 1 %), fall back to larger min-edge so the cluster
        # sits deepest inside the chosen sheet.
        if real_frac - best[1] > 0.01:
            best = candidate
        elif abs(real_frac - best[1]) <= 0.01 and min_edge > best[2]:
            best = candidate
    return best[0] if best else None


def _estimate_black_fraction(img: "PILImage") -> float:
    """Return the fraction of near-black pixels in the rendered crop.

    Used to detect edge-of-raster crops: ``rasterio.read(boundless=True,
    fill_value=0)`` pads out-of-raster pixels with RGB (0, 0, 0), so a
    high black fraction means the cluster sits near the map edge.

    Threshold is generous (RGB values ≤ 8 each) to account for slight
    LANCZOS interpolation of the boundary with genuine map pixels.
    Counts only fully-black pixels — will underestimate if the raster
    itself contains genuinely-black symbols, but those are a small
    fraction of 1:25k topographic rasters so the heuristic is
    conservative-enough for an advisory warning.
    """
    arr = np.asarray(img)
    if arr.ndim != 3 or arr.shape[2] < 3:
        return 0.0
    rgb = arr[:, :, :3]
    near_black = (rgb[:, :, 0] <= 8) & (rgb[:, :, 1] <= 8) & (rgb[:, :, 2] <= 8)
    return float(near_black.mean())


def _placeholder_image(cluster: Cluster, size: int = 600) -> "PILImage":
    """Fall back to a grey canvas with relative-coordinate markers."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (size, size), (200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.text(
        (10, 10),
        f"[raster missing]\nmap: {cluster.map_id}\n"
        f"n_points: {cluster.n_points}",
        fill=(40, 40, 40),
    )
    xs = [c[0] for c in cluster.coords]
    ys = [c[1] for c in cluster.coords]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 10.0)
    pad = 40
    for i, (px_m, py_m) in enumerate(cluster.coords):
        lx = int((px_m - min(xs)) / span * (size - 2 * pad) + pad)
        ly = size - int((py_m - min(ys)) / span * (size - 2 * pad) + pad)
        colour = _MARKER_COLOURS[i % len(_MARKER_COLOURS)]
        draw.ellipse([lx - 12, ly - 12, lx + 12, ly + 12],
                     outline=colour, width=3)
        draw.text((lx + 14, ly - 14), str(i + 1), fill=colour)
    return img


# =========================================================================
# Decisions CSV I/O
# =========================================================================

_DECISION_COLUMNS = [
    "cluster_id",
    "map_id",
    "n_points",
    "point_ids_in",
    "pairwise_distances_m",
    "decision",
    "point_ids_kept",
    "merged_subtype",
    "merged_centroid_x",
    "merged_centroid_y",
    "timestamp",
]


def load_decisions(csv_path: Path) -> dict[str, dict]:
    """Load an existing decisions CSV (if any). Keyed by cluster_id.

    An empty or header-only file yields an empty dict, not an error — this
    is the expected state when starting a fresh review. A CSV whose
    structure is malformed (mismatched columns) raises a clear error
    rather than silently returning partial data.
    """
    if not csv_path.is_file() or csv_path.stat().st_size == 0:
        return {}
    try:
        df = pd.read_csv(csv_path, dtype=str).fillna("")
    except pd.errors.EmptyDataError:
        return {}
    except pd.errors.ParserError as exc:
        raise ValueError(
            f"Malformed decisions CSV at {csv_path}: {exc}. "
            f"Inspect and repair the file before retrying."
        ) from exc
    if "cluster_id" not in df.columns:
        return {}
    if df["cluster_id"].duplicated().any():
        dupes = df.loc[df["cluster_id"].duplicated(), "cluster_id"].tolist()
        print(
            f"Warning: {len(dupes)} duplicate cluster_id rows in "
            f"{csv_path} — last occurrence wins. Duplicates: "
            f"{sorted(set(dupes))[:5]}...",
            file=sys.stderr,
        )
    out: dict[str, dict] = {}
    for _, row in df.iterrows():
        out[row["cluster_id"]] = row.to_dict()
    return out


def save_decisions(decisions: dict[str, dict], csv_path: Path) -> None:
    """Atomically write decisions to CSV (tmp-then-rename)."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [decisions[k] for k in sorted(decisions)]
    df = pd.DataFrame(rows, columns=_DECISION_COLUMNS)
    tmp = csv_path.with_suffix(csv_path.suffix + ".tmp")
    df.to_csv(tmp, index=False)
    tmp.replace(csv_path)


def format_decision(
    cluster: Cluster,
    decision: str,
    kept_row_ids: list[int] | None = None,
    merged_subtype: str | None = None,
) -> dict:
    """Build a CSV-ready row dict for a cluster decision."""
    if decision == DECISION_MERGE:
        cx, cy = cluster.centroid
        merged_cx: str = f"{cx:.4f}"
        merged_cy: str = f"{cy:.4f}"
        kept_list = ""
    elif decision == DECISION_KEEP_ONLY:
        merged_cx = merged_cy = ""
        kept_list = ";".join(str(i) for i in (kept_row_ids or []))
    elif decision == DECISION_KEEP_ALL:
        merged_cx = merged_cy = ""
        kept_list = ";".join(str(i) for i in cluster.point_ids)
    else:  # uncertain
        merged_cx = merged_cy = ""
        kept_list = ";".join(str(i) for i in cluster.point_ids)
    return {
        "cluster_id": cluster.cluster_id,
        "map_id": cluster.map_id,
        "n_points": str(cluster.n_points),
        "point_ids_in": ";".join(str(i) for i in cluster.point_ids),
        "pairwise_distances_m": ";".join(
            f"{d:.2f}" for d in cluster.pairwise_distances_m
        ),
        "decision": decision,
        "point_ids_kept": kept_list,
        "merged_subtype": merged_subtype or "",
        "merged_centroid_x": merged_cx,
        "merged_centroid_y": merged_cy,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# =========================================================================
# Apply decisions → cleaned GT
# =========================================================================


def apply_decisions(
    gt: gpd.GeoDataFrame,
    decisions: dict[str, dict],
) -> tuple[gpd.GeoDataFrame, dict[str, int]]:
    """Produce a cleaned GT by applying the decision set.

    - ``keep_all`` / ``uncertain``: no change to the cluster's rows.
    - ``merge``: delete all cluster rows, append a single merged point at
      the cluster centroid carrying the user's ``merged_subtype``.
    - ``keep_only``: retain only the listed row ids from the cluster.

    Deterministic. Data-idempotent: re-applying to the same GT with the
    same decisions set produces the same geometry/subtype/row-count output.
    (The ``timestamp`` column in the decisions CSV is regenerated on each
    save, so the CSV itself is not byte-identical across saves, but the
    cleaned GT is.)

    Raises:
        ValueError: if a decision row has an unrecognised ``decision``
            code, or a ``merge`` row lacks valid centroid coordinates, or
            a ``keep_only`` row lists no kept points. These signal a
            malformed or stale CSV that should be corrected before the
            cleaned GT is produced — silent pass-through would corrupt
            the output.
    """
    clean = gt.copy()
    clean["_merged"] = False
    clean["_reviewed_subtype"] = None
    drop_ids: set[int] = set()
    new_rows: list[dict] = []
    counts = {"keep_all": 0, "merge": 0, "keep_only": 0, "uncertain": 0}

    valid_subtypes = set(SUBTYPE_OPTIONS.keys())

    for cid, d in decisions.items():
        decision = d.get("decision", "")
        in_ids = _parse_id_list(d.get("point_ids_in", ""))

        if decision == DECISION_KEEP_ALL:
            counts["keep_all"] += 1
            continue
        if decision == DECISION_UNCERTAIN:
            counts["uncertain"] += 1
            continue
        if decision == DECISION_KEEP_ONLY:
            kept = _parse_id_list(d.get("point_ids_kept", ""))
            if not kept:
                raise ValueError(
                    f"Decision for cluster {cid!r} is keep_only but "
                    f"point_ids_kept is empty."
                )
            stranger = [k for k in kept if k not in in_ids]
            if stranger:
                raise ValueError(
                    f"Decision for cluster {cid!r} keeps rows "
                    f"{stranger} that are not in the cluster's "
                    f"point_ids_in list."
                )
            counts["keep_only"] += 1
            kept_set = set(kept)
            drop_ids.update(i for i in in_ids if i not in kept_set)
            continue
        if decision == DECISION_MERGE:
            cx = _safe_float(d.get("merged_centroid_x", ""))
            cy = _safe_float(d.get("merged_centroid_y", ""))
            if not (np.isfinite(cx) and np.isfinite(cy)):
                raise ValueError(
                    f"Decision for cluster {cid!r} is merge but has "
                    f"non-finite centroid: ({cx}, {cy})."
                )
            subtype = d.get("merged_subtype", "") or "other"
            if subtype not in valid_subtypes:
                # Unknown subtype strings are coerced to 'other' rather
                # than raising — a human-entered typo shouldn't block the
                # whole pipeline — but a warning is logged.
                print(
                    f"Warning: cluster {cid!r} has unknown subtype "
                    f"{subtype!r}; coerced to 'other'.",
                    file=sys.stderr,
                )
                subtype = "other"
            counts["merge"] += 1
            drop_ids.update(in_ids)
            template: dict = {}
            if in_ids:
                match_rows = gt.loc[gt["_gt_row_id"] == in_ids[0]]
                if not match_rows.empty:
                    template = match_rows.iloc[0].to_dict()
            if "source_map" not in template:
                # Fall back to map_id stored in the decision row so the
                # merged point isn't stranded without a source_map
                # attribution (stale in_ids corner case).
                template["source_map"] = d.get("map_id", "")
            new_rows.append({
                **{k: v for k, v in template.items()
                   if k not in ("geometry", "_gt_row_id")},
                "geometry": Point(cx, cy),
                "_gt_row_id": -1,
                "_merged": True,
                "_reviewed_subtype": subtype,
                "uuid": f"merged-{cid}",
            })
            continue

        # Unknown decision code — fail loudly rather than silently skip.
        raise ValueError(
            f"Decision for cluster {cid!r} has unrecognised code "
            f"{decision!r} (expected one of: keep_all, merge, keep_only, "
            f"uncertain)."
        )

    if drop_ids:
        clean = clean.loc[~clean["_gt_row_id"].isin(drop_ids)].copy()
    if new_rows:
        new_gdf = gpd.GeoDataFrame(new_rows, geometry="geometry",
                                   crs=clean.crs)
        clean = gpd.GeoDataFrame(
            pd.concat([clean, new_gdf], ignore_index=True),
            geometry="geometry", crs=clean.crs,
        )
    # Stable row order after apply
    clean = clean.sort_values(
        by=["source_map", "_gt_row_id"], kind="stable",
    ).reset_index(drop=True)
    return clean, counts


def _parse_id_list(raw: str) -> list[int]:
    """Parse a ``;``-joined integer list stored in the CSV."""
    if not raw:
        return []
    return [int(x) for x in raw.split(";") if x.strip()]


def _safe_float(raw: str) -> float:
    try:
        return float(raw)
    except (TypeError, ValueError):
        return float("nan")


def write_diff_report(
    original: gpd.GeoDataFrame,
    cleaned: gpd.GeoDataFrame,
    decisions: dict[str, dict],
    counts: dict[str, int],
    output_path: Path,
) -> None:
    """Write a human-readable diff summary."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_orig = len(original)
    n_clean = len(cleaned)
    lines: list[str] = []
    lines.append("# GT duplicate-review diff")
    lines.append("")
    lines.append(
        f"Generated: {datetime.now(timezone.utc).isoformat()}"
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Original points: **{n_orig}**")
    lines.append(f"- Cleaned points: **{n_clean}** (Δ = {n_clean - n_orig:+d})")
    lines.append(f"- Decisions applied: **{len(decisions)}**")
    lines.append(f"  - keep_all: {counts['keep_all']}")
    lines.append(f"  - merge: {counts['merge']}")
    lines.append(f"  - keep_only: {counts['keep_only']}")
    lines.append(f"  - uncertain (passthrough): {counts['uncertain']}")
    lines.append("")
    lines.append("## Per-cluster decisions")
    lines.append("")
    lines.append(
        "| Cluster | Map | n | Decision | Subtype | Kept | Δ rows |"
    )
    lines.append("|---|---|--:|---|---|---|--:|")
    for cid in sorted(decisions):
        d = decisions[cid]
        n = int(d.get("n_points", "0") or 0)
        dec = d.get("decision", "")
        sub = d.get("merged_subtype", "") or ""
        kept = d.get("point_ids_kept", "")
        if dec == DECISION_MERGE:
            delta = -(n - 1)
        elif dec == DECISION_KEEP_ONLY:
            delta = len(_parse_id_list(kept)) - n
        else:
            delta = 0
        lines.append(
            f"| {cid} | {d.get('map_id', '')} | {n} | {dec} | "
            f"{sub} | {kept} | {delta:+d} |"
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# =========================================================================
# Streamlit UI (imported lazily — only when running the review app)
# =========================================================================


def run_streamlit(args: argparse.Namespace) -> None:
    """Launch the interactive review UI. Imports Streamlit lazily."""
    import streamlit as st

    st.set_page_config(page_title="GT Duplicate Review", layout="centered")
    st.title("GT Duplicate Review")

    gt_path = Path(args.ground_truth)
    rasters_dir = Path(args.rasters_dir)
    output_path = Path(args.output)
    threshold_m = float(args.threshold_m)
    context_m = float(args.context_m)

    @st.cache_data
    def _load_and_cluster(gt_str: str, threshold: float) -> list[Cluster]:
        gdf = load_gt(Path(gt_str))
        return build_clusters(gdf, threshold)

    clusters = _load_and_cluster(str(gt_path), threshold_m)
    if not clusters:
        st.success(
            f"No clusters found at threshold {threshold_m} m. Nothing to review."
        )
        return

    decisions = st.session_state.setdefault(
        "decisions", load_decisions(output_path),
    )
    # Seed history from previously-saved decisions so the Back button can
    # undo decisions from earlier sessions, not just this-session work.
    if "history" not in st.session_state:
        st.session_state["history"] = [
            cid for cid in sorted(decisions) if cid
        ]
    history: list[str] = st.session_state["history"]
    # Skipped clusters are session-state only — never persisted to the
    # CSV, so they reappear on next launch. This is the correct
    # semantic for "defer until I've checked the adjacent map sheet".
    skipped: set[str] = st.session_state.setdefault("skipped", set())

    # Find next cluster not yet decided AND not skipped this session.
    idx = 0
    for i, c in enumerate(clusters):
        if c.cluster_id in decisions or c.cluster_id in skipped:
            continue
        idx = i
        break
    else:
        idx = len(clusters)

    done = sum(1 for c in clusters if c.cluster_id in decisions)
    total = len(clusters)
    progress_text = f"Progress: {done} / {total} clusters reviewed"
    if skipped:
        progress_text += f" ({len(skipped)} skipped this session)"
    st.progress(done / total if total else 1.0, text=progress_text)

    if idx >= total:
        if skipped:
            st.info(
                f"First pass complete: {done} decided, {len(skipped)} "
                f"skipped. Click *Revisit skipped* to go through the "
                f"skipped clusters now, or close the app and relaunch "
                f"later — skipped clusters are session-only and will "
                f"reappear automatically next time."
            )
            if st.button("Revisit skipped"):
                st.session_state["skipped"] = set()
                st.rerun()
            _render_summary(decisions)
            return
        st.success("All clusters reviewed. Run with --apply to generate the "
                   "cleaned GT and diff report.")
        _render_summary(decisions)
        return

    cluster = clusters[idx]
    st.markdown(
        f"### Cluster `{cluster.cluster_id}`  \n"
        f"Map: `{cluster.map_id}`  •  Points: **{cluster.n_points}**  •  "
        f"Pairwise distances (m): "
        f"{', '.join(f'{d:.1f}' for d in cluster.pairwise_distances_m)}"
    )

    with st.spinner("Rendering context crop..."):
        img = render_cluster_image(cluster, rasters_dir, context_m)
    st.image(img, width="stretch")

    # Tell the user which raster the crop actually came from. When the
    # best-coverage raster differs from the cluster's declared
    # source_map, an auto-switch has happened and flagging it is
    # important for review transparency.
    cx_centroid, cy_centroid = cluster.centroid
    actual_raster = _best_raster_for_point(
        rasters_dir, cx_centroid, cy_centroid,
    )
    if actual_raster is not None:
        actual_map = actual_raster.stem
        if actual_map != cluster.map_id:
            st.caption(
                f"Rendered from **{actual_map}** (auto-selected for "
                f"best context around the cluster; cluster's declared "
                f"source_map is {cluster.map_id})."
            )

    # Edge-of-raster heuristic: even after preferring the best-coverage
    # raster, some clusters sit at the corner/edge of the full raster
    # set and still end up with significant no-data black fill.
    black_frac = _estimate_black_fraction(img)
    if black_frac > 0.25:
        st.warning(
            f"⚠️ Edge of raster detected "
            f"({black_frac * 100:.0f}% of the crop is no-data black "
            f"fill). Consider pressing **n: Skip** and checking the "
            f"adjacent map sheet before deciding."
        )

    # Per-member metadata
    with st.expander("Member points"):
        for i, (rid, ft, sym, (px, py)) in enumerate(zip(
            cluster.point_ids, cluster.feature_types, cluster.map_symbols,
            cluster.coords, strict=True,
        )):
            st.write(
                f"**{i+1}.** id=`{rid}`  •  FeatureType: {ft}  •  "
                f"MapSymbol: {sym}  •  ({px:.2f}, {py:.2f})"
            )

    # --- Decision buttons -------------------------------------------------
    st.markdown("#### Decision")
    st.markdown(
        "**`k`** Keep all distinct &nbsp;&nbsp; "
        "**`m`** Merge (select subtype) &nbsp;&nbsp; "
        "**`1`..`9`** Keep only point N &nbsp;&nbsp; "
        "**`u`** Uncertain (flagged) &nbsp;&nbsp; "
        "**`n`** Skip (revisit later) &nbsp;&nbsp; "
        "**`b`** Back (undo)"
    )

    pending_merge = st.session_state.get("pending_merge")
    col_main = st.columns([1, 1, 1, 1, 1])
    if col_main[0].button("k: Keep all", key=f"keep_all_{cluster.cluster_id}",
                          use_container_width=True):
        _save_decision(
            cluster, DECISION_KEEP_ALL, decisions, history, output_path,
        )
        st.rerun()
    if col_main[1].button("m: Merge",
                          key=f"merge_{cluster.cluster_id}",
                          use_container_width=True):
        st.session_state["pending_merge"] = cluster.cluster_id
        st.rerun()
    if col_main[2].button("u: Uncertain",
                          key=f"unc_{cluster.cluster_id}",
                          use_container_width=True):
        _save_decision(
            cluster, DECISION_UNCERTAIN, decisions, history, output_path,
        )
        st.rerun()
    if col_main[3].button("n: Skip",
                          key=f"skip_{cluster.cluster_id}",
                          use_container_width=True):
        skipped.add(cluster.cluster_id)
        st.session_state.pop("pending_merge", None)
        st.rerun()
    # Back button. Semantics:
    #   - If a merge is pending (user clicked Merge but hasn't picked a
    #     subtype yet), Back cancels the pending merge without popping
    #     history.
    #   - Otherwise, Back pops the most-recently-saved decision from
    #     history and removes it from the decisions dict + CSV.
    back_label = (
        "b: Cancel merge" if pending_merge == cluster.cluster_id
        else "b: Back"
    )
    back_enabled = (
        pending_merge == cluster.cluster_id or bool(history)
    )
    if back_enabled and col_main[4].button(
        back_label, key="back_btn", use_container_width=True,
    ):
        if pending_merge == cluster.cluster_id:
            st.session_state.pop("pending_merge", None)
        else:
            last = history.pop()
            decisions.pop(last, None)
            save_decisions(decisions, output_path)
        st.rerun()

    # Keep-only N buttons (one per point)
    st.write("")
    kept_cols = st.columns(min(cluster.n_points, 9))
    for i in range(min(cluster.n_points, 9)):
        if kept_cols[i].button(
            f"{i+1}: keep only #{i+1}",
            key=f"keep_{i}_{cluster.cluster_id}",
            use_container_width=True,
        ):
            _save_decision(
                cluster, DECISION_KEEP_ONLY, decisions, history,
                output_path, kept_row_ids=[cluster.point_ids[i]],
            )
            st.rerun()
    if cluster.n_points > 9:
        st.warning(
            "Cluster has more than 9 points; use the command line --apply "
            "with a manually-edited decisions CSV for keep_only on points "
            "above #9."
        )

    # Merge-subtype selector (appears after pressing m)
    if pending_merge == cluster.cluster_id:
        st.markdown("##### Select merged-point subtype")
        default_subtype = cluster.suggest_subtype()
        st.caption(
            f"Suggested (consensus of cluster members): "
            f"**{SUBTYPE_OPTIONS[default_subtype][0]}**"
        )
        sub_cols = st.columns(len(SUBTYPE_OPTIONS))
        for i, (key, (label, shortcut)) in enumerate(SUBTYPE_OPTIONS.items()):
            marker = "★ " if key == default_subtype else ""
            if sub_cols[i].button(
                f"{shortcut}: {marker}{label}",
                key=f"sub_{key}_{cluster.cluster_id}",
                use_container_width=True,
            ):
                _save_decision(
                    cluster, DECISION_MERGE, decisions, history,
                    output_path, merged_subtype=key,
                )
                st.session_state.pop("pending_merge", None)
                st.rerun()

    # Keyboard shortcuts
    _inject_keyboard_shortcuts(cluster.n_points, pending_merge is not None)


def _save_decision(
    cluster: Cluster,
    decision: str,
    decisions: dict[str, dict],
    history: list[str],
    output_path: Path,
    kept_row_ids: list[int] | None = None,
    merged_subtype: str | None = None,
) -> None:
    """Record a decision, update history, persist atomically."""
    decisions[cluster.cluster_id] = format_decision(
        cluster, decision, kept_row_ids=kept_row_ids,
        merged_subtype=merged_subtype,
    )
    history.append(cluster.cluster_id)
    save_decisions(decisions, output_path)


def _inject_keyboard_shortcuts(n_points: int, merge_pending: bool) -> None:
    """Bind single-key shortcuts to the button rows via inline JS.

    Streamlit's ``components.v1.html`` renders inside an iframe, so a
    naive ``document.addEventListener`` only catches keystrokes that
    happen *inside that iframe* — which is empty and zero-height, so
    it's never focused. The fix is to attach the listener to
    ``window.parent.document`` (same-origin, allowed). A reference is
    cached on the parent document so repeated Streamlit reruns don't
    stack duplicate listeners.

    The JS scans buttons by visible text prefix ``"{key}:"`` and clicks
    the first match. Labels produced by the Python code (``"k: Keep
    all"``, ``"1: keep only #1"``, etc.) are constructed to match this
    convention.
    """
    import streamlit as st

    # n_points and merge_pending are accepted for future server-side
    # routing; the JS handler reads the current buttons directly from
    # the DOM each keystroke so it stays in sync without a re-render.
    _ = (n_points, merge_pending)

    js = """
    <script>
    (function() {
        // Walk up frames until we find the top Streamlit document.
        let doc = null;
        try {
            doc = window.parent.document;
        } catch (e) {
            doc = document;  // fallback; likely non-functional
        }
        // Remove any previous listener (Streamlit reruns inject a fresh
        // iframe on every pass; without this guard, listeners stack).
        if (doc.__gtReviewKeyHandler) {
            doc.removeEventListener('keydown', doc.__gtReviewKeyHandler);
        }

        // Click a Streamlit-rendered button. Streamlit's React tree
        // doesn't always process a plain .click() as a user-initiated
        // event, so we dispatch a full MouseEvent sequence (pointerdown,
        // mousedown, mouseup, click) which matches a trusted click more
        // closely. Also blurs any currently-focused element first so
        // Streamlit's state machine sees a fresh interaction.
        const simulateClick = function(btn) {
            if (!btn) return;
            btn.scrollIntoView({block: 'nearest', behavior: 'instant'});
            const active = doc.activeElement;
            if (active && active.blur) active.blur();
            const opts = {bubbles: true, cancelable: true, view: window};
            btn.dispatchEvent(new MouseEvent('mousedown', opts));
            btn.dispatchEvent(new MouseEvent('mouseup', opts));
            btn.dispatchEvent(new MouseEvent('click', opts));
        };

        const handler = function(e) {
            if (e.ctrlKey || e.altKey || e.metaKey) return;
            const active = doc.activeElement;
            if (active && (active.tagName === 'INPUT' ||
                           active.tagName === 'TEXTAREA' ||
                           active.isContentEditable)) return;
            const key = (e.key || '').toLowerCase();
            if (!key) return;
            const buttons = doc.querySelectorAll('button');
            const matches = [];
            for (const btn of buttons) {
                const text = (btn.textContent || '').trim().toLowerCase();
                if (text.startsWith(key + ':')) matches.push(btn);
            }
            if (matches.length === 0) {
                console.debug('[gt-review] key', key,
                              '— no matching button');
                return;
            }
            if (matches.length > 1) {
                console.debug('[gt-review] key', key,
                              '— multiple matches, clicking last (most '
                              + 'recently rendered):',
                              matches.map(b => b.textContent.trim()));
            }
            // When multiple buttons share a prefix, prefer the LAST one
            // in document order — Streamlit renders new widget groups
            // after old ones, so the bottom-most match is almost always
            // the one currently visible to the user.
            const btn = matches[matches.length - 1];
            simulateClick(btn);
            e.preventDefault();
            e.stopPropagation();
        };
        doc.addEventListener('keydown', handler);
        doc.__gtReviewKeyHandler = handler;
    })();
    </script>
    """
    st.components.v1.html(js, height=0)


def _render_summary(decisions: dict[str, dict]) -> None:
    """Show a quick classification breakdown at end-of-review."""
    import streamlit as st

    counts = Counter(d.get("decision", "") for d in decisions.values())
    st.markdown("#### Decision breakdown")
    for dec, n in sorted(counts.items(), key=lambda x: -x[1]):
        st.write(f"- {dec}: {n}")


# =========================================================================
# --apply post-processing
# =========================================================================


def run_apply(args: argparse.Namespace) -> int:
    """Apply decisions CSV to produce the cleaned GT + diff report."""
    gt_path = Path(args.ground_truth)
    decisions_path = Path(args.decisions)
    clean_path = Path(args.clean_output)
    diff_path = Path(args.diff_output)

    if not gt_path.is_file():
        print(f"GT not found: {gt_path}", file=sys.stderr)
        return 2

    gt = load_gt(gt_path)
    decisions = load_decisions(decisions_path)
    cleaned, counts = apply_decisions(gt, decisions)

    # Drop internal helper columns before writing
    out = cleaned.drop(columns=["_gt_row_id"], errors="ignore")
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    # GeoPackage-safe: convert bool columns that pandas keeps as object
    for col in ("_merged",):
        if col in out.columns:
            out[col] = out[col].astype(bool)
    out.to_file(clean_path, driver="GeoJSON")

    write_diff_report(gt, cleaned, decisions, counts, diff_path)

    print(
        f"Applied {len(decisions)} decisions "
        f"(merge={counts['merge']}, keep_only={counts['keep_only']}, "
        f"keep_all={counts['keep_all']}, uncertain={counts['uncertain']}). "
        f"Original: {len(gt)}  →  Cleaned: {len(cleaned)} "
        f"(Δ = {len(cleaned) - len(gt):+d})"
    )
    print(f"Cleaned GT: {clean_path}")
    print(f"Diff report: {diff_path}")
    return 0


# =========================================================================
# CLI entry
# =========================================================================


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI parser (shared between Streamlit and --apply)."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ground-truth", type=str, default=_DEFAULT_GT)
    p.add_argument("--rasters-dir", type=str, default=_DEFAULT_RASTERS)
    p.add_argument("--threshold-m", type=float,
                   default=_DEFAULT_THRESHOLD_M)
    p.add_argument("--context-m", type=float, default=_DEFAULT_CONTEXT_M)
    p.add_argument("--output", type=str, default=_DEFAULT_OUTPUT,
                   help="Decisions CSV (input+output).")
    p.add_argument("--apply", action="store_true",
                   help="Post-process: apply decisions CSV to produce "
                        "cleaned GT + diff report. No Streamlit.")
    p.add_argument("--decisions", type=str, default=_DEFAULT_OUTPUT,
                   help="Decisions CSV to read under --apply.")
    p.add_argument("--clean-output", type=str, default=_DEFAULT_CLEAN_GT,
                   help="Cleaned GT path written under --apply.")
    p.add_argument("--diff-output", type=str, default=_DEFAULT_DIFF,
                   help="Diff report written under --apply.")
    return p


def main() -> int:
    """Dispatch to --apply or Streamlit UI based on flags."""
    parser = build_parser()
    try:
        args = parser.parse_args(sys.argv[1:])
    except SystemExit as exc:
        # Preserve argparse's exit code convention: 0 for --help, 2 for
        # parse error. Otherwise SystemExit('foo') → return 2.
        code = exc.code
        if isinstance(code, int):
            return code
        return 2

    if args.apply:
        return run_apply(args)

    # Streamlit path. When invoked via ``streamlit run ...`` Streamlit's own
    # entrypoint calls ``main()`` in a context where st is already alive.
    run_streamlit(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
