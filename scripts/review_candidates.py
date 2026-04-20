#!/usr/bin/env python3
"""Streamlit app for human review of VLM detection candidates.

Presents crop images of measured false positives (candidates accepted
by the pipeline but unmatched to student ground truth) for human
classification by symbol type. Provides running corrected precision
and F1 estimates.

Usage:
    streamlit run scripts/review_candidates.py -- \\
        --crops-dir outputs/55maps-generalisation/crops \\
        --probabilities outputs/55maps-generalisation/verified/probabilities.json \\
        --ground-truth inputs/vectors/references/student-mounds-55maps.geojson \\
        --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \\
        --output results/55maps-generalisation/human-review.csv

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
# at the ~5 m/px native resolution. 300 m × 300 m matches the GT
# deduplication app convention (see ``scripts/review_gt_duplicates.py``)
# and puts the 50 m tolerance circle at roughly 1/3 of the display
# width — a comfortable visual scale for "is this symbol close to
# centre?" decisions.
_DEFAULT_CONTEXT_M = 300.0
_DISPLAY_PX = 600

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


@st.cache_data
def render_candidate_context_crop(
    centroid_x: float,
    centroid_y: float,
    rasters_dir: str,
    context_m: float = _DEFAULT_CONTEXT_M,
    buffer_m: int = _DEFAULT_BUFFER,
    display_px: int = _DISPLAY_PX,
) -> Image.Image:
    """Render a ``context_m``-wide crop with magenta tolerance circle.

    Reads the source raster on demand (via ``rasterio`` with
    ``boundless=True`` so edge-of-sheet candidates still produce a
    correctly-sized image) and upscales to ``display_px`` via LANCZOS
    for legible map symbols at the ~5 m/px native resolution.

    The magenta tolerance circle has radius ``buffer_m / context_m *
    display_px`` display-pixels — a symbol inside is within buffer of
    the proposer centroid (centre cross); outside is not.

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

    # Tolerance circle + centre cross, magenta (rarely appears in
    # Soviet 1:50k topographic sheets, so high contrast with map).
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx = display_px // 2
    cy = display_px // 2
    r_display = int(round(buffer_m / context_m * display_px))
    draw.ellipse(
        [(cx - r_display, cy - r_display),
         (cx + r_display, cy + r_display)],
        outline=(255, 0, 255, 255),
        width=3,
    )
    cross_half = max(6, display_px // 100)
    draw.line([(cx - cross_half, cy), (cx + cross_half, cy)],
              fill=(255, 0, 255, 255), width=2)
    draw.line([(cx, cy - cross_half), (cx, cy + cross_half)],
              fill=(255, 0, 255, 255), width=2)
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
) -> tuple[list[dict], int, int, int]:
    """Load and match candidates, returning the FP subset.

    Returns:
        Tuple of (fp_candidates, n_accepted, n_tp, n_ref) where:
        - fp_candidates: list of dicts sorted by descending probability
        - n_accepted: total candidates above threshold
        - n_tp: number of true positives (matched to GT)
        - n_ref: total reference mounds in scope (for recall)
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
        return [], 0, 0, 0

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
    tp_count = 0
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

        _, _, unmatched_det, _ = match_detections_to_references(
            det_geoms, ref_geoms, buffer_metres,
        )

        matched_count = len(det_geoms) - len(unmatched_det)
        tp_count += matched_count

        for d_idx in unmatched_det:
            fp_indices.add(det_scope.index[d_idx])

    # Build FP candidate list sorted by descending probability
    fp_candidates = [
        accepted[i] for i in sorted(fp_indices)
    ]
    fp_candidates.sort(
        key=lambda c: c["mound_probability"], reverse=True,
    )

    return fp_candidates, n_accepted, tp_count, ref_count


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
        default="results/55maps-generalisation/human-review.csv",
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
        fp_candidates, n_accepted, n_tp, n_ref = load_candidates(
            args.crops_dir, args.probabilities,
            args.ground_truth, args.bounds,
            args.threshold, args.buffer,
        )

    if not fp_candidates:
        st.warning("No FP candidates found.")
        return

    n_fp = len(fp_candidates)

    # Initialise session state
    if "reviews" not in st.session_state:
        st.session_state.reviews = load_existing_reviews(output_path)
    reviews = st.session_state.reviews
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
    for i, c in enumerate(fp_candidates):
        if c["candidate_id"] not in reviews:
            current_idx = i
            break
    else:
        current_idx = len(fp_candidates)  # All reviewed

    # ---------------------------------------------------------------
    # Header and progress
    # ---------------------------------------------------------------
    reviewed_count = sum(
        1 for c in fp_candidates if c["candidate_id"] in reviews
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
    if current_idx >= len(fp_candidates):
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
                file_name="human-review.csv",
                mime="text/csv",
            )
        return

    candidate = fp_candidates[current_idx]
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

    # Crop image — tight context crop rendered live from the source
    # raster, with a magenta tolerance circle at centre. A symbol
    # inside the circle is within the matching buffer of the proposer
    # centroid (centre cross); outside is not. Context width is
    # configurable via --context-m (default 300 m) — smaller values
    # zoom in; larger values show more of the surrounding landscape.
    try:
        overlaid = render_candidate_context_crop(
            centroid_x=float(candidate["centroid_x"]),
            centroid_y=float(candidate["centroid_y"]),
            rasters_dir=str(rasters_dir),
            context_m=args.context_m,
            buffer_m=args.buffer,
        )
        st.image(overlaid, width=_DISPLAY_PX)
        st.caption(
            f"Magenta circle = {args.buffer} m matching tolerance "
            f"inside a {args.context_m:.0f} m × {args.context_m:.0f} m "
            f"context crop. Symbol inside = within tolerance; outside "
            f"= not counted by pipeline. Cross marks the proposer "
            f"centroid (crop centre)."
        )
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to render candidate {cid}: {exc}")

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
        reviews[cid] = {
            "symbol_type": button_pressed,
            "human_label": human_label,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "buffer_metres": args.buffer,
        }
        # Dedupe history so Undo is always a single-press undo, even
        # when the user re-reviews the same candidate.
        if cid in st.session_state.history:
            st.session_state.history.remove(cid)
        st.session_state.history.append(cid)

        # Save incrementally
        save_reviews(reviews, fp_candidates, output_path, args.buffer)
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
            save_reviews(reviews, fp_candidates, output_path, args.buffer)
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
