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
import pandas as pd
import streamlit as st
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
        reviews = {}
        for _, row in df.iterrows():
            reviews[int(row["candidate_id"])] = {
                "symbol_type": row["symbol_type"],
                "human_label": row["human_label"],
                "timestamp": row["timestamp"],
            }
        return reviews
    except Exception:
        return {}


def save_reviews(
    reviews: dict[int, dict],
    candidates: list[dict],
    csv_path: Path,
) -> None:
    """Save all reviews to CSV."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    # Build a lookup for candidate metadata
    cand_lookup = {c["candidate_id"]: c for c in candidates}
    for cid, review in sorted(reviews.items()):
        cand = cand_lookup.get(cid, {})
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
            "timestamp": review["timestamp"],
        })
    pd.DataFrame(rows).to_csv(csv_path, index=False)


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
    if "history" not in st.session_state:
        st.session_state.history = []

    reviews = st.session_state.reviews

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

    # Crop image — display large
    crop_path = Path(candidate["crop_file"])
    if crop_path.exists():
        st.image(str(crop_path), width=300)
    else:
        st.error(f"Crop not found: {crop_path}")

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

    # Keyboard shortcut listener
    shortcut_js = """
    <script>
    document.addEventListener('keydown', function(e) {
        const keyMap = {
            'f': 0, 'd': 1, 's': 2, 'a': 3, 'j': 4, 'k': 5
        };
        if (e.key in keyMap && !e.ctrlKey && !e.altKey && !e.metaKey) {
            // Don't fire if user is typing in an input
            if (document.activeElement.tagName === 'INPUT' ||
                document.activeElement.tagName === 'TEXTAREA') {
                return;
            }
            const buttons = parent.document.querySelectorAll(
                'button[kind="secondary"]'
            );
            // Find the button whose text starts with the key
            for (const btn of buttons) {
                if (btn.textContent.trim().startsWith(e.key + ':')) {
                    btn.click();
                    break;
                }
            }
        }
    });
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
        }
        st.session_state.history.append(cid)

        # Save incrementally
        save_reviews(reviews, fp_candidates, output_path)
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
            save_reviews(reviews, fp_candidates, output_path)
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
