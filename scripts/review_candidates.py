#!/usr/bin/env python3
"""Streamlit app for human review of VLM detection candidates.

Presents context crops of detection candidates with five concentric
tolerance rings (50 / 75 / 100 / 125 / 150 m) so reviewers can flag
real mounds that are pulled beyond the primary 50 m tolerance by
attractor labels (numbers, letters, trig symbols). The reviewer picks
the tightest enclosing ring per mound (or marks the candidate as
not_mound / mound beyond 150 m).

By default the app presents the FP queue at 50 m as the primary
re-review target. Enable the sidebar toggle
"Include confirmed mounds (re-check yesterday's TPs)" to also cycle
through yesterday's accepted-TP candidates with their prior answers
pre-populated — useful for correcting errors from a prior review
session.

Usage (55-map image-generalisation multi-buffer re-review):

    streamlit run scripts/review_candidates.py -- \\
        --crops-dir outputs/55maps-image-generalisation/crops \\
        --probabilities \\
            outputs/55maps-image-generalisation/verified/probabilities.json \\
        --ground-truth \\
            inputs/vectors/references/student-mounds-55maps-reviewed.geojson \\
        --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \\
        --output \\
            results/55maps-image-generalisation/human-review-multi-buffer.csv \\
        --prev-review results/55maps-image-generalisation/human-review.csv

Output CSV schema matches the 2026-04-20 single-buffer review, with
``buffer_metres`` now taking values in ``{50, 75, 100, 125, 150, 200}``
where ``200`` is the sentinel for "mound visible beyond 150 m". For
not_mound / uncertain rows the ``buffer_metres`` cell is empty.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import streamlit as st
from PIL import Image, ImageDraw
from rasterio.windows import Window
from shapely.geometry import Point

# ---------------------------------------------------------------------------
# Path setup — allow imports from scripts/
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from lib_advanced_metrics import (  # noqa: E402
    get_map_name,
    match_detections_to_references,
    scope_references_to_tiles,
)
from lib_consensus import ensure_utm_crs  # noqa: E402

# =========================================================================
# Constants
# =========================================================================

_TARGET_CRS = "EPSG:32635"
_DEFAULT_THRESHOLD = 0.15
_DEFAULT_BUFFER = 50

# Context crop defaults. The render reads a ``context_m``-wide window
# from the source raster, centred on the candidate centroid, and
# upscales to ``_DISPLAY_PX`` via LANCZOS so map symbols remain legible
# at the ~5 m/px native resolution. 400 m × 400 m accommodates the
# five-ring multi-buffer display (rings at 50/75/100/125/150 m) with
# comfortable margin for the outermost ring's label; single-ring legacy
# reviews can override via ``--context-m 300`` for tighter framing.
_DEFAULT_CONTEXT_M = 400.0
_DISPLAY_PX = 600

# Concentric tolerance rings used in multi-buffer review mode. The 50 m
# ring is the reference tolerance from the 2026-04-20 review; outer
# rings let reviewers flag mounds pulled beyond 50 m by attractor
# labels (numbers, letters, trig symbols) without having to re-matched
# at a wider buffer mechanically.
_BUFFER_BANDS_DEFAULT: tuple[int, ...] = (50, 75, 100, 125, 150)
# Three anchor labels — inner reference, mid, outer. 75 and 125 m rings
# stay unlabelled to reduce visual clutter over map content; they are
# unambiguously "the ring between" two labelled neighbours.
_LABEL_BANDS: tuple[int, ...] = (50, 100, 150)
# Per-ring (stroke_width_px, opacity_0_255). Inner ring boldest and
# fully opaque (reference); outer rings taper to keep them visually
# subordinate.
_BAND_STYLES: dict[int, tuple[int, int]] = {
    50: (3, 255),
    75: (2, 230),
    100: (2, 210),
    125: (2, 190),
    150: (2, 170),
}
_MAGENTA = (255, 0, 255)
# Sentinel buffer value in the output CSV for mounds visible beyond the
# outermost 150 m ring. Kept numeric (not a string) so downstream
# analysis can filter via ``buffer_metres <= X`` without NaN handling
# for the mound-beyond-150 subset.
_BEYOND_150_SENTINEL = 200

# Symbol classification options
SYMBOL_TYPES = {
    "f": ("burial_mound", "Burial mound"),
    "d": ("bench_mark_on_mound", "Bench mark on mound"),
    "s": ("trig_point_on_mound", "Trig point on mound"),
    "a": ("settlement_mound", "Settlement mound"),
    "j": ("not_mound", "Not a mound"),
    "k": ("uncertain", "Uncertain"),
}

# Which symbol types count as "real mound" for precision correction
_MOUND_TYPES = {
    "burial_mound", "bench_mark_on_mound",
    "trig_point_on_mound", "settlement_mound",
}


# =========================================================================
# Live-raster context crop rendering
# =========================================================================
#
# The three helpers below (_collect_raster_bounds, _resolve_raster,
# _best_raster_for_point) are inlined copies of the private helpers
# in scripts/review_gt_duplicates.py. Extracted to a shared module if
# a third consumer ever appears; for now, two consumers justifies the
# duplication over a refactor.

# Cache of (raster_path, bounds) per rasters_dir — avoids rescanning on
# every Streamlit re-run.
_RASTER_BOUNDS_CACHE: dict[str, list[tuple[Path, tuple[float, ...]]]] = {}


def _collect_raster_bounds(
    rasters_dir: Path,
) -> list[tuple[Path, tuple[float, float, float, float]]]:
    """Gather (path, (left, bottom, right, top)) for every TIF in dir."""
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
        except Exception:  # noqa: BLE001
            continue
    _RASTER_BOUNDS_CACHE[key] = out
    return out


def _best_raster_for_point(
    rasters_dir: Path, x: float, y: float, sample_px: int = 40,
) -> Path | None:
    """Return the raster whose pixels at (x, y) have most real content.

    Trapezoidal sheets inside rectangular rasters leave black-fill
    outside the mapped area, so bounds filtering alone picks the wrong
    neighbouring sheet for points near the edge. Sample a small window
    at (x, y) and prefer the raster with the most non-black pixels.
    """
    bounds_list = _collect_raster_bounds(rasters_dir)
    best: tuple[Path, float, float] | None = None
    for path, (left, bottom, right, top) in bounds_list:
        if not (left <= x <= right and bottom <= y <= top):
            continue
        try:
            with rasterio.open(path) as src:
                row_f, col_f = src.index(x, y)
                row = int(round(float(row_f)))
                col = int(round(float(col_f)))
                window = Window(
                    col - sample_px // 2, row - sample_px // 2,
                    sample_px, sample_px,
                )
                arr = src.read(
                    window=window, boundless=True, fill_value=0,
                )
                if arr.shape[0] == 0:
                    continue
                bands = arr[:3] if arr.shape[0] >= 3 else arr[:1]
                near_black = np.all(bands <= 8, axis=0)
                real_frac = 1.0 - float(near_black.mean())
        except Exception:  # noqa: BLE001
            continue
        min_edge = min(x - left, right - x, y - bottom, top - y)
        candidate = (path, real_frac, min_edge)
        if best is None:
            best = candidate
            continue
        if real_frac - best[1] > 0.01:
            best = candidate
        elif abs(real_frac - best[1]) <= 0.01 and min_edge > best[2]:
            best = candidate
    return best[0] if best else None


def _placeholder_image(
    centroid_x: float, centroid_y: float, size: int = _DISPLAY_PX,
) -> Image.Image:
    """Grey fallback when no raster covers the candidate centroid."""
    img = Image.new("RGB", (size, size), (200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.text(
        (10, 10),
        f"[raster not found]\ncentroid (x, y):\n"
        f"{centroid_x:.1f}, {centroid_y:.1f}",
        fill=(40, 40, 40),
    )
    return img


def _draw_ring_label(
    draw: "ImageDraw.ImageDraw",
    text: str,
    cx: int,
    ring_top_y: int,
) -> None:
    """Draw a labelled magenta-on-dark text box just above a ring's top edge.

    The label sits centred on ``cx`` with its bottom 2 px above
    ``ring_top_y`` (the ring's 12 o'clock pixel row). A semi-opaque
    black rectangle behind the text gives legibility over busy map
    content. Falls back to a fixed-width estimate if the PIL
    ``textbbox`` API is unavailable.
    """
    try:
        bbox = draw.textbbox((0, 0), text)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except (AttributeError, TypeError):
        text_w = 6 * len(text)
        text_h = 11
    pad = 3
    box_w = text_w + 2 * pad
    box_h = text_h + 2 * pad
    box_left = cx - box_w // 2
    box_top = ring_top_y - box_h - 2
    draw.rectangle(
        [(box_left, box_top), (box_left + box_w, box_top + box_h)],
        fill=(0, 0, 0, 200),
    )
    draw.text(
        (box_left + pad, box_top + pad),
        text,
        fill=(255, 0, 255, 255),
    )


@st.cache_data
def render_candidate_context_crop(
    centroid_x: float,
    centroid_y: float,
    rasters_dir: str,
    context_m: float = _DEFAULT_CONTEXT_M,
    buffer_bands: tuple[int, ...] = _BUFFER_BANDS_DEFAULT,
    label_bands: tuple[int, ...] = _LABEL_BANDS,
    display_px: int = _DISPLAY_PX,
) -> Image.Image:
    """Render a ``context_m``-wide crop with concentric tolerance rings.

    Reads the source raster on demand (via ``rasterio`` with
    ``boundless=True`` so edge-of-sheet candidates still produce a
    correctly-sized image) and upscales to ``display_px`` via LANCZOS
    for legible map symbols at the ~5 m/px native resolution.

    Each ring in ``buffer_bands`` is drawn in magenta with a per-band
    stroke width and alpha (see ``_BAND_STYLES``): inner ring bold and
    fully opaque, outer rings progressively lighter. Rings in
    ``label_bands`` carry an anchor label ("<band> m") just above their
    12 o'clock edge so the reviewer can orient within the concentric
    stack without miscounting. The centre cross marks the proposer
    centroid (crop centre).

    Streamlit-cached on all arguments so re-renders are free when the
    reviewer hasn't changed candidate.
    """
    rasters_path = Path(rasters_dir)
    raster_path = _best_raster_for_point(
        rasters_path, centroid_x, centroid_y,
    )
    if raster_path is None:
        return _placeholder_image(
            centroid_x, centroid_y, size=display_px,
        )

    with rasterio.open(raster_path) as src:
        row_f, col_f = src.index(centroid_x, centroid_y)
        row_c = int(round(float(row_f)))
        col_c = int(round(float(col_f)))
        res_m_per_px = abs(src.transform.a)
        half_px = max(1, int(round(context_m / 2 / res_m_per_px)))
        window = Window(
            col_c - half_px, row_c - half_px,
            half_px * 2, half_px * 2,
        )
        arr = src.read(window=window, boundless=True, fill_value=0)
        n_bands = arr.shape[0]
        if n_bands >= 3:
            img_data = arr[:3].transpose(1, 2, 0)
        elif n_bands in (1, 2):
            g = arr[0]
            img_data = np.stack([g, g, g], axis=-1)
        else:
            return _placeholder_image(
                centroid_x, centroid_y, size=display_px,
            )
        raw_img = Image.fromarray(
            img_data.astype(np.uint8),
        ).convert("RGB")

    # Upscale to display size so markers and the tolerance circle
    # remain sharp. LANCZOS preserves edges better than bicubic for
    # line-art like topographic symbols.
    img = raw_img.resize(
        (display_px, display_px), Image.LANCZOS,
    ).convert("RGBA")

    # Concentric tolerance rings + centre cross, magenta (rarely
    # appears in Soviet 1:50k topographic sheets, so high contrast with
    # map content). Drawn outer-to-inner so the innermost reference
    # ring sits on top if rings overlap anti-aliased pixels.
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx = display_px // 2
    cy = display_px // 2
    for band_m in sorted(buffer_bands, reverse=True):
        r_display = int(round(band_m / context_m * display_px))
        width, alpha = _BAND_STYLES.get(band_m, (2, 200))
        colour = (_MAGENTA[0], _MAGENTA[1], _MAGENTA[2], alpha)
        draw.ellipse(
            [(cx - r_display, cy - r_display),
             (cx + r_display, cy + r_display)],
            outline=colour,
            width=width,
        )
    # Anchor labels — drawn after all rings so they sit on top. The
    # label box is positioned above each ring's top edge so it does
    # not obscure the ring stroke itself.
    for band_m in label_bands:
        r_display = int(round(band_m / context_m * display_px))
        ring_top_y = cy - r_display
        _draw_ring_label(draw, f"{band_m} m", cx, ring_top_y)
    # Centre cross.
    cross_half = max(6, display_px // 100)
    draw.line(
        [(cx - cross_half, cy), (cx + cross_half, cy)],
        fill=(255, 0, 255, 255), width=2,
    )
    draw.line(
        [(cx, cy - cross_half), (cx, cy + cross_half)],
        fill=(255, 0, 255, 255), width=2,
    )
    return Image.alpha_composite(img, overlay)


# =========================================================================
# Data loading
# =========================================================================


@st.cache_data
def load_candidates(
    crops_dir: str,
    probabilities_path: str,
    reference_path: str,
    bounds_path: str,
    threshold: float,
    buffer_metres: int,
) -> tuple[list[dict], list[dict], int, int, int]:
    """Load and match candidates, returning both FP and TP subsets.

    The FP subset is the primary review queue. The TP subset is emitted
    so that the multi-buffer review app can optionally cycle the
    reviewer through yesterday's accepted-TP calls for re-verification
    (see ``--include-confirmed-mounds`` / sidebar toggle).

    Returns:
        Tuple of (fp_candidates, tp_candidates, n_accepted, n_tp, n_ref):
        - fp_candidates: detections unmatched to GT at ``buffer_metres``,
          sorted by descending probability.
        - tp_candidates: detections matched to GT at ``buffer_metres``,
          sorted by descending probability.
        - n_accepted: total candidates above threshold.
        - n_tp: number of true positives (matched to GT).
        - n_ref: total reference mounds in scope (for recall).
    """
    crops_dir_path = Path(crops_dir)

    # Load manifest
    manifest_path = crops_dir_path / "candidate_manifest.json"
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    candidates = manifest["candidates"]

    # Load probabilities
    with open(probabilities_path, encoding="utf-8") as f:
        prob_data = json.load(f)
    probabilities = prob_data.get("results", {})

    # Filter by threshold and build GeoDataFrame
    accepted = []
    for c in candidates:
        cid = c["candidate_id"]
        key = f"candidate_{cid:05d}"
        prob_entry = probabilities.get(key, {})
        prob = prob_entry.get("mound_probability", 0.0)
        if prob >= threshold:
            accepted.append({
                "candidate_id": cid,
                "candidate_key": key,
                "mound_probability": prob,
                "source_tile": c.get("source_tile", "unknown"),
                "centroid_x": c["centroid_x"],
                "centroid_y": c["centroid_y"],
                "crop_file": str(
                    crops_dir_path / c["crop_file"]
                ),
                "subtype": c.get("properties", {}).get(
                    "subtype", "unknown"
                ),
                "vote_count": c.get("properties", {}).get(
                    "vote_count", 0
                ),
            })

    if not accepted:
        return [], [], 0, 0, 0

    n_accepted = len(accepted)

    # Build detection GeoDataFrame
    gdf_det = gpd.GeoDataFrame(
        accepted,
        geometry=[
            Point(a["centroid_x"], a["centroid_y"])
            for a in accepted
        ],
        crs=_TARGET_CRS,
    )

    # Load reference and bounds
    gdf_ref = gpd.read_file(reference_path)
    gdf_ref = ensure_utm_crs(gdf_ref, source_label=reference_path)

    gdf_bounds = gpd.read_file(bounds_path)
    gdf_bounds = ensure_utm_crs(gdf_bounds, source_label=bounds_path)

    # Per-map Hungarian matching (same logic as calculate_f1_internal)
    ref_map_col = (
        "source_map" if "source_map" in gdf_ref.columns else "Map"
    )
    processed_maps = {
        get_map_name(n) for n in gdf_bounds["tile_name"].unique()
    }
    processed_maps.discard("Unknown")

    fp_indices: set[int] = set()
    tp_indices: set[int] = set()
    ref_count = 0  # Total scoped reference mounds

    for map_name in sorted(processed_maps):
        map_bounds = gdf_bounds[
            gdf_bounds["tile_name"].str.startswith(map_name)
        ]
        ref_scope = gdf_ref[gdf_ref[ref_map_col] == map_name]
        if not ref_scope.empty:
            ref_scope = scope_references_to_tiles(
                ref_scope, map_bounds,
            )
        det_scope = gdf_det[
            gdf_det["source_tile"].str.startswith(map_name)
        ]

        ref_count += len(ref_scope)

        if det_scope.empty:
            continue
        if ref_scope.empty:
            fp_indices.update(det_scope.index)
            continue

        det_geoms = list(det_scope.geometry)
        ref_geoms = list(ref_scope.geometry)

        matched_det, _, unmatched_det, _ = match_detections_to_references(
            det_geoms, ref_geoms, buffer_metres,
        )

        for d_idx in matched_det:
            tp_indices.add(det_scope.index[d_idx])
        for d_idx in unmatched_det:
            fp_indices.add(det_scope.index[d_idx])

    # Build FP and TP candidate lists, each sorted by descending probability.
    fp_candidates = [accepted[i] for i in sorted(fp_indices)]
    fp_candidates.sort(
        key=lambda c: c["mound_probability"], reverse=True,
    )
    tp_candidates = [accepted[i] for i in sorted(tp_indices)]
    tp_candidates.sort(
        key=lambda c: c["mound_probability"], reverse=True,
    )

    return fp_candidates, tp_candidates, n_accepted, len(tp_indices), ref_count


# =========================================================================
# CSV I/O
# =========================================================================


def load_existing_reviews(csv_path: Path) -> dict[int, dict]:
    """Load previously saved reviews for resume support.

    If the CSV includes a ``buffer_metres`` column (added 2026-04-20),
    the per-row value is preserved so that a later save does not
    silently re-tag rows with the current ``--buffer`` argument. Rows
    without a recorded buffer (from older saves) are left untagged at
    load time; they will pick up the current buffer on first re-save.

    Returns:
        Dict mapping candidate_id → review dict.
    """
    if not csv_path.exists():
        return {}
    try:
        df = pd.read_csv(csv_path)
        required = {"candidate_id", "symbol_type", "human_label", "timestamp"}
        if not required.issubset(df.columns):
            return {}
        has_buffer = "buffer_metres" in df.columns
        reviews = {}
        for _, row in df.iterrows():
            entry = {
                "symbol_type": row["symbol_type"],
                "human_label": row["human_label"],
                "timestamp": row["timestamp"],
            }
            if has_buffer and pd.notna(row["buffer_metres"]):
                entry["buffer_metres"] = int(row["buffer_metres"])
            reviews[int(row["candidate_id"])] = entry
        return reviews
    except Exception:
        return {}


@st.cache_data
def load_previous_mound_labels(csv_path_str: str) -> dict[int, dict]:
    """Load yesterday's mound classifications for pre-population.

    Used when the confirmed-mounds sidebar toggle is active: the
    reviewer sees each of yesterday's accepted-TP calls pre-populated
    with its previous ``symbol_type`` and ``buffer_metres`` so they can
    one-keystroke-confirm or override without retyping.

    Cached across reruns on the string path so flipping the toggle
    mid-session does not re-read the CSV from disk repeatedly.

    Returns a dict keyed by ``candidate_id`` for rows whose
    ``human_label`` was ``'mound'``. Rows labelled ``'not_mound'`` or
    ``'uncertain'`` are excluded — those go through the normal re-review
    queue as FPs.
    """
    csv_path = Path(csv_path_str)
    if not csv_path.exists():
        return {}
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        return {}
    required = {"candidate_id", "symbol_type", "human_label"}
    if not required.issubset(df.columns):
        return {}
    df = df[df["human_label"] == "mound"]
    out: dict[int, dict] = {}
    for _, row in df.iterrows():
        entry = {
            "symbol_type": row["symbol_type"],
            "human_label": "mound",
            "timestamp": row.get("timestamp", ""),
        }
        # Default the pre-populated buffer to 50 m (yesterday's review
        # was done at a 50 m tolerance) unless a per-row value exists.
        if "buffer_metres" in df.columns and pd.notna(row["buffer_metres"]):
            entry["buffer_metres"] = int(row["buffer_metres"])
        else:
            entry["buffer_metres"] = 50
        out[int(row["candidate_id"])] = entry
    return out


def save_reviews(
    reviews: dict[int, dict],
    candidates: list[dict],
    csv_path: Path,
    buffer_m: int = _DEFAULT_BUFFER,
) -> None:
    """Save all reviews to CSV via atomic tmp-then-rename.

    The ``buffer_metres`` column records the matching-tolerance zone
    the reviewer was judging against. This review set is valid only
    for computing corrected F1/P/R at that buffer — it does NOT
    identify *where* inside the circle the real mound is, so corrected
    metrics at tighter buffers are not derivable from this output.

    Atomic write guards against a partial file on user-triggered
    crashes or Streamlit re-runs mid-save. Without this, an
    interrupted write would leave a truncated CSV and lose review
    history.
    """
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    # Build a lookup for candidate metadata
    cand_lookup = {c["candidate_id"]: c for c in candidates}
    for cid, review in sorted(reviews.items()):
        cand = cand_lookup.get(cid, {})
        # Preserve per-row buffer provenance: if the review was loaded
        # with a buffer_metres already recorded, keep it. Otherwise tag
        # with the current session buffer.
        row_buffer = review.get("buffer_metres", buffer_m)
        rows.append({
            "candidate_id": cid,
            "verifier_probability": cand.get("mound_probability", ""),
            "human_label": review["human_label"],
            "symbol_type": review["symbol_type"],
            "source_tile": cand.get("source_tile", ""),
            "map_name": get_map_name(
                cand.get("source_tile", "unknown")
            ),
            "x": cand.get("centroid_x", ""),
            "y": cand.get("centroid_y", ""),
            "buffer_metres": row_buffer,
            "timestamp": review["timestamp"],
        })
    tmp = csv_path.with_suffix(csv_path.suffix + ".tmp")
    pd.DataFrame(rows).to_csv(tmp, index=False)
    tmp.replace(csv_path)


# =========================================================================
# Streamlit UI
# =========================================================================


def main() -> None:
    """Streamlit app entry point."""
    st.set_page_config(
        page_title="Candidate Review",
        layout="centered",
    )

    # Parse CLI args (after Streamlit's own args via --)
    parser = argparse.ArgumentParser()
    parser.add_argument("--crops-dir", type=str, required=True)
    parser.add_argument("--probabilities", type=str, required=True)
    parser.add_argument("--ground-truth", type=str, required=True)
    parser.add_argument("--bounds", type=str, required=True)
    parser.add_argument(
        "--threshold", type=float, default=_DEFAULT_THRESHOLD,
    )
    parser.add_argument(
        "--buffer", type=int, default=_DEFAULT_BUFFER,
    )
    parser.add_argument(
        "--context-m", type=float, default=_DEFAULT_CONTEXT_M,
        help=(
            "Width/height of the context crop in metres. Default 300 m "
            "gives a ~1/3-of-display-width tolerance circle at 50 m "
            "buffer, suitable for symbol-proximity decisions."
        ),
    )
    parser.add_argument(
        "--rasters-dir", type=str, default=None,
        help=(
            "Directory containing the source GeoTIFFs to render crops "
            "from. If omitted, read from the candidate manifest's "
            "rasters_dir field."
        ),
    )
    parser.add_argument(
        "--output", type=str,
        default=(
            "results/55maps-image-generalisation/"
            "human-review-multi-buffer.csv"
        ),
        help=(
            "Output CSV path. Defaults to the multi-buffer re-review "
            "file; override for legacy single-buffer review runs."
        ),
    )
    parser.add_argument(
        "--prev-review", type=str,
        default="results/55maps-image-generalisation/human-review.csv",
        help=(
            "Path to a prior human-review CSV. Used by the "
            "confirmed-mounds sidebar toggle to pre-populate yesterday's "
            "mound classifications so the reviewer can one-keystroke "
            "confirm or override. Set to '' to disable."
        ),
    )
    try:
        args = parser.parse_args(sys.argv[1:])
    except SystemExit:
        st.error(
            "Missing required arguments. Run with: "
            "`streamlit run scripts/review_candidates.py -- "
            "--crops-dir ... --probabilities ... --ground-truth ... "
            "--bounds ...`"
        )
        return

    output_path = Path(args.output)

    # Resolve rasters directory: CLI arg overrides the manifest field.
    if args.rasters_dir:
        rasters_dir = Path(args.rasters_dir)
    else:
        manifest_path = (
            Path(args.crops_dir) / "candidate_manifest.json"
        )
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            rasters_dir = Path(manifest.get(
                "rasters_dir", "inputs/rasters/Russian1981_32635",
            ))
        except Exception:
            rasters_dir = Path("inputs/rasters/Russian1981_32635")
    if not rasters_dir.is_dir():
        st.error(
            f"Rasters directory not found: {rasters_dir}. "
            "Pass --rasters-dir or ensure the manifest's rasters_dir is "
            "a valid path relative to the current working directory."
        )
        return

    # Load data
    with st.spinner("Loading candidates and running matching..."):
        (
            fp_candidates,
            tp_candidates,
            n_accepted,
            n_tp,
            n_ref,
        ) = load_candidates(
            args.crops_dir, args.probabilities,
            args.ground_truth, args.bounds,
            args.threshold, args.buffer,
        )

    if not fp_candidates and not tp_candidates:
        st.warning("No candidates found.")
        return

    # --- Sidebar controls ---
    with st.sidebar:
        st.markdown("### Review mode")
        include_confirmed_mounds = st.toggle(
            "Include confirmed mounds (re-check yesterday's TPs)",
            value=False,
            help=(
                "When ON, yesterday's accepted-TP candidates are cycled "
                "through with their prior symbol_type and 50 m buffer "
                "pre-populated. Lets you one-keystroke confirm or "
                "override, giving you a chance to correct errors from "
                "yesterday's session."
            ),
        )
        st.markdown("---")
        st.caption(
            f"FP queue: {len(fp_candidates)} &nbsp; | &nbsp; "
            f"Confirmed-TP pool: {len(tp_candidates)}"
        )

    # Compose the review queue. FPs always come first; if the toggle is
    # on, append yesterday's confirmed-mound candidates so re-verification
    # happens after the FP pass.
    if include_confirmed_mounds:
        queue = fp_candidates + tp_candidates
    else:
        queue = fp_candidates

    n_fp = len(queue)

    # Initialise session state — reviews dict persists across reruns,
    # seeded from the on-disk CSV if one exists.
    if "reviews" not in st.session_state:
        st.session_state.reviews = load_existing_reviews(output_path)
    # Pre-populate with yesterday's mound labels whenever the
    # confirmed-mounds toggle is on. Idempotent — only inserts for
    # candidate_ids in the current TP queue that aren't yet reviewed,
    # so flipping the toggle mid-session is safe.
    if include_confirmed_mounds and args.prev_review:
        prev = load_previous_mound_labels(args.prev_review)
        queue_ids = {c["candidate_id"] for c in tp_candidates}
        for cid, entry in prev.items():
            if cid in queue_ids and cid not in st.session_state.reviews:
                st.session_state.reviews[cid] = dict(entry)
    reviews = st.session_state.reviews

    # Initialise the buffer-band selector. The band resets to 50 m
    # after every save (see Classification handler below) so a band
    # chosen for one candidate never silently carries into the next.
    if "current_band" not in st.session_state:
        st.session_state.current_band = 50
    # Seed history from previously-saved reviews so Undo can undo
    # prior-session work, not just this-session reviews. (Order is
    # deterministic — sorted by candidate_id — so the undo order is
    # predictable; it doesn't reflect the actual chronological order
    # of the original reviews, but that information isn't available
    # from the CSV anyway.)
    if "history" not in st.session_state:
        st.session_state.history = sorted(reviews.keys())
    # Reconcile history with the reviews dict in case the CSV was
    # externally edited between reruns — otherwise Undo would try to
    # pop candidate_ids that no longer exist.
    st.session_state.history[:] = [
        h for h in st.session_state.history if h in reviews
    ]

    # Find first unreviewed candidate
    current_idx = 0
    for i, c in enumerate(queue):
        if c["candidate_id"] not in reviews:
            current_idx = i
            break
    else:
        current_idx = len(queue)  # All reviewed

    # ---------------------------------------------------------------
    # Header and progress
    # ---------------------------------------------------------------
    reviewed_count = sum(
        1 for c in queue if c["candidate_id"] in reviews
    )

    st.title("Candidate Review")
    st.progress(
        reviewed_count / n_fp if n_fp > 0 else 1.0,
        text=f"Progress: {reviewed_count} / {n_fp} "
             f"({100 * reviewed_count / n_fp:.1f}%)",
    )

    # ---------------------------------------------------------------
    # Running statistics
    # ---------------------------------------------------------------
    mound_count = sum(
        1 for r in reviews.values()
        if r["symbol_type"] in _MOUND_TYPES
    )
    not_mound_count = sum(
        1 for r in reviews.values()
        if r["symbol_type"] == "not_mound"
    )
    uncertain_count = sum(
        1 for r in reviews.values()
        if r["symbol_type"] == "uncertain"
    )

    # Corrected metrics (extrapolate from reviewed sample)
    # Recall = TP / (TP + FN) where FN = n_ref - TP.
    # Reclassifying FPs as TPs doesn't change recall (same detections,
    # same GT) — recall is based on reference count, not detection count.
    measured_r = n_tp / n_ref if n_ref > 0 else 0.0

    reviewed_decisive = mound_count + not_mound_count
    if reviewed_decisive > 0:
        phantom_rate = mound_count / reviewed_decisive
        est_phantom_total = int(round(phantom_rate * n_fp))
        corrected_tp = n_tp + est_phantom_total
        corrected_p = (
            corrected_tp / n_accepted if n_accepted > 0 else 0.0
        )
        corrected_f1 = (
            2 * corrected_p * measured_r
            / (corrected_p + measured_r)
            if (corrected_p + measured_r) > 0 else 0.0
        )
    else:
        corrected_p = None
        corrected_f1 = None

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Mounds", mound_count)
    with col2:
        st.metric("Not mound", not_mound_count)
    with col3:
        st.metric("Uncertain", uncertain_count)

    if corrected_p is not None:
        measured_p = n_tp / n_accepted if n_accepted > 0 else 0.0
        measured_f1 = (
            2 * measured_p * measured_r / (measured_p + measured_r)
            if (measured_p + measured_r) > 0 else 0.0
        )
        col4, col5 = st.columns(2)
        with col4:
            st.metric(
                "Corrected P",
                f"{corrected_p:.3f}",
                delta=f"{corrected_p - measured_p:+.3f} from measured",
            )
        with col5:
            st.metric(
                "Corrected F1",
                f"{corrected_f1:.3f}",
                delta=(
                    f"{corrected_f1 - measured_f1:+.3f} from measured"
                ),
            )

    st.divider()

    # ---------------------------------------------------------------
    # Current candidate display
    # ---------------------------------------------------------------
    if current_idx >= len(queue):
        st.success(
            f"All {n_fp} candidates reviewed! "
            f"Mounds: {mound_count}, Not mound: {not_mound_count}, "
            f"Uncertain: {uncertain_count}"
        )
        # Download button
        if output_path.exists():
            csv_data = output_path.read_text()
            st.download_button(
                "Download CSV", csv_data,
                file_name=output_path.name,
                mime="text/csv",
            )
        return

    candidate = queue[current_idx]
    cid = candidate["candidate_id"]
    prob = candidate["mound_probability"]
    tile = candidate["source_tile"]
    map_name = get_map_name(tile)
    subtype = candidate["subtype"]
    vote = candidate["vote_count"]

    # Metadata line
    st.markdown(
        f"**candidate_{cid:05d}** &nbsp; | &nbsp; "
        f"p = {prob:.3f} &nbsp; | &nbsp; "
        f"{map_name} &nbsp; | &nbsp; "
        f"VLM: {subtype} &nbsp; | &nbsp; "
        f"votes: {vote}/5"
    )

    # Crop image — context crop rendered live from the source raster,
    # with five concentric magenta tolerance rings at 50 / 75 / 100 /
    # 125 / 150 m. Three of them (50, 100, 150) carry labels. The
    # reviewer picks the tightest ring that encloses a real mound (or
    # marks the candidate as not_mound / mound beyond 150 m).
    try:
        overlaid = render_candidate_context_crop(
            centroid_x=float(candidate["centroid_x"]),
            centroid_y=float(candidate["centroid_y"]),
            rasters_dir=str(rasters_dir),
            context_m=args.context_m,
        )
        st.image(overlaid, width=_DISPLAY_PX)
        st.caption(
            f"Concentric rings at 50 / 75 / 100 / 125 / 150 m inside a "
            f"{args.context_m:.0f} m × {args.context_m:.0f} m context "
            f"crop. Anchor labels at 50 / 100 / 150 m. A symbol inside "
            f"a ring is within that tolerance of the proposer centroid "
            f"(centre cross). Pick the tightest ring that encloses the "
            f"real mound, or `>150` if visible beyond all rings."
        )
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to render candidate {cid}: {exc}")

    # ---------------------------------------------------------------
    # Buffer-band selector
    # ---------------------------------------------------------------
    # The selected band is attached to the next mound classification
    # and auto-resets to 50 m after every save so it cannot silently
    # carry across candidates.
    band_specs: list[tuple[int, str, str]] = [
        (50, "1", "50 m"),
        (75, "2", "75 m"),
        (100, "3", "100 m"),
        (125, "4", "125 m"),
        (150, "5", "150 m"),
        (_BEYOND_150_SENTINEL, "6", ">150"),
    ]
    active_band = st.session_state.current_band
    active_label = next(
        (lbl for band, _k, lbl in band_specs if band == active_band),
        f"{active_band}",
    )
    st.markdown(
        f"**Buffer band** &nbsp; | &nbsp; current: **{active_label}** "
        "&nbsp; | &nbsp; keys `1`-`6` set 50 / 75 / 100 / 125 / 150 / >150. "
        "The band attaches to the next mound classification, then "
        "auto-resets to 50 m."
    )
    band_cols = st.columns(len(band_specs))
    for i, (band, key_char, lbl) in enumerate(band_specs):
        with band_cols[i]:
            is_active = band == active_band
            if st.button(
                f"{key_char}: {lbl}",
                key=f"band_btn_{key_char}_{cid}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.current_band = band
                st.rerun()

    # ---------------------------------------------------------------
    # Classification buttons
    # ---------------------------------------------------------------
    st.markdown(
        "**`f`** Burial mound &nbsp;&nbsp; "
        "**`d`** Bench mark on mound &nbsp;&nbsp; "
        "**`s`** Trig on mound &nbsp;&nbsp; "
        "**`a`** Settlement mound &nbsp;&nbsp; "
        "**`j`** Not a mound &nbsp;&nbsp; "
        "**`k`** Uncertain"
    )

    # Button row
    cols = st.columns(6)
    button_pressed = None
    for i, (key, (sym_type, label)) in enumerate(SYMBOL_TYPES.items()):
        with cols[i]:
            if st.button(
                f"{key}: {label}",
                key=f"btn_{key}_{cid}",
                use_container_width=True,
            ):
                button_pressed = sym_type

    # Keyboard shortcut listener. The naive approach — listening on
    # the component iframe's own ``document`` — doesn't work because
    # the iframe is zero-height and never has keyboard focus, so
    # keydown events fire on the parent Streamlit page and never reach
    # this listener. We attach in the CAPTURE phase to every
    # reachable document (parent, top, self) so the keystroke is
    # caught wherever focus happens to be. Simulated clicks use a
    # full MouseEvent sequence (mousedown + mouseup + click) plus a
    # native ``.click()`` fallback, wrapped in ``setTimeout(0)`` so
    # any pending React render from a prior keystroke flushes before
    # the next click fires — without this, Streamlit's React state
    # machine sometimes ignores the click as non-trusted.
    shortcut_js = """
    <script>
    (function() {
        const docs = [];
        try { docs.push(window.parent.document); } catch (e) {}
        try {
            if (window.top && window.top.document !== window.parent.document) {
                docs.push(window.top.document);
            }
        } catch (e) {}
        docs.push(document);

        const LOG = function() {
            console.log.apply(console, ['[candidate-review]'].concat(
                Array.prototype.slice.call(arguments)
            ));
        };

        const streamlitDoc = docs[0] || document;

        for (const d of docs) {
            if (d.__candidateReviewKeyHandler) {
                d.removeEventListener(
                    'keydown', d.__candidateReviewKeyHandler, true,
                );
            }
        }

        const simulateClick = function(btn, label) {
            if (!btn) return;
            btn.scrollIntoView({block: 'nearest', behavior: 'instant'});
            setTimeout(function() {
                const opts = {bubbles: true, cancelable: true, view: window};
                try {
                    btn.dispatchEvent(new MouseEvent('mousedown', opts));
                    btn.dispatchEvent(new MouseEvent('mouseup', opts));
                    btn.dispatchEvent(new MouseEvent('click', opts));
                    if (typeof btn.click === 'function') btn.click();
                    LOG('clicked', label || btn.textContent.trim());
                } catch (err) {
                    LOG('click failed', err);
                }
            }, 0);
        };

        const makeHandler = function(source) {
            return function(e) {
                if (e.ctrlKey || e.altKey || e.metaKey) return;
                if (e.__candidateReviewSeen) return;
                e.__candidateReviewSeen = true;

                const active = (streamlitDoc.activeElement || null);
                const activeTag = active ? active.tagName : '(none)';
                if (active && (active.tagName === 'INPUT' ||
                               active.tagName === 'TEXTAREA' ||
                               active.isContentEditable)) return;
                const key = (e.key || '').toLowerCase();
                if (!key) return;

                const buttons = streamlitDoc.querySelectorAll('button');
                const matches = [];
                for (const btn of buttons) {
                    const text = (btn.textContent || '').trim()
                                    .toLowerCase();
                    if (text.startsWith(key + ':')) matches.push(btn);
                }
                LOG('key', key, 'source', source, 'active', activeTag,
                    '→', matches.length, 'match(es)',
                    matches.map(function(b) {
                        return (b.textContent || '').trim().slice(0, 40);
                    }));
                if (matches.length === 0) return;
                const btn = matches[matches.length - 1];
                const focused = streamlitDoc.activeElement;
                if (focused && focused.blur) focused.blur();
                simulateClick(btn, (btn.textContent || '').trim());
                e.preventDefault();
                e.stopPropagation();
            };
        };

        for (let i = 0; i < docs.length; i++) {
            const label = i === 0 ? 'parent' :
                          (i === 1 && docs[i] !== document ? 'top' :
                           'iframe');
            const h = makeHandler(label);
            docs[i].addEventListener('keydown', h, true);
            docs[i].__candidateReviewKeyHandler = h;
        }
        LOG('handler attached to', docs.length, 'doc(s) at',
            new Date().toISOString());
    })();
    </script>
    """
    st.components.v1.html(shortcut_js, height=0)

    # Handle classification
    if button_pressed:
        human_label = (
            "mound" if button_pressed in _MOUND_TYPES
            else button_pressed
        )
        # Attach the active buffer band only when the classification
        # is a mound type. For not_mound / uncertain the band has no
        # meaning; we write None (empty CSV cell) so downstream
        # analysis does not accidentally read the session's sticky
        # band as a per-row measurement.
        if button_pressed in _MOUND_TYPES:
            row_buffer: int | None = int(st.session_state.current_band)
        else:
            row_buffer = None
        reviews[cid] = {
            "symbol_type": button_pressed,
            "human_label": human_label,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "buffer_metres": row_buffer,
        }
        # Dedupe history so Undo is always a single-press undo, even
        # when the user re-reviews the same candidate.
        if cid in st.session_state.history:
            st.session_state.history.remove(cid)
        st.session_state.history.append(cid)

        # Reset band to the 50 m default for the next candidate so a
        # chosen band never silently carries over.
        st.session_state.current_band = 50

        # Save incrementally
        save_reviews(
            reviews, fp_candidates + tp_candidates,
            output_path, args.buffer,
        )
        st.rerun()

    # ---------------------------------------------------------------
    # Undo button
    # ---------------------------------------------------------------
    st.divider()
    if st.session_state.history:
        if st.button("Undo last"):
            last_cid = st.session_state.history.pop()
            if last_cid in reviews:
                del reviews[last_cid]
            save_reviews(
            reviews, fp_candidates + tp_candidates,
            output_path, args.buffer,
        )
            st.rerun()

    # Symbol type breakdown
    if reviews:
        type_counts = {}
        for r in reviews.values():
            t = r["symbol_type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        with st.expander("Classification breakdown"):
            for sym_type, count in sorted(
                type_counts.items(), key=lambda x: -x[1]
            ):
                label = next(
                    (v[1] for v in SYMBOL_TYPES.values() if v[0] == sym_type),
                    sym_type,
                )
                st.write(f"  {label}: {count}")


if __name__ == "__main__":
    main()
