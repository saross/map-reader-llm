#!/usr/bin/env python3
"""
Streamlit reviewer for student-vs-curator GT false-positive candidates
on the four gold-standard (GS) map sheets.

Background
----------
``scripts/analyse_student_gt_fn_rate_gs4.py`` runs a Hungarian one-to-
one match between the cleaned student GT
(``inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson``,
556 features) and the curator-corrected reference
(``inputs/vectors/references/mounds-reference.geojson``, 569 features
restricted to the four GS sheets) at a 50 m radius. The aggregate
result is TP = 539, FN = 30, FP = 17.

The 17 FPs are *unmatched* student features. Shawn's prior expert
review of the GS sheets recalls only ~1 genuinely-non-mound student
feature, so the value 17 deserves a per-feature audit before being
reported as a 3 % student FP rate. There are four plausible
explanations to disambiguate manually with the raster in front of us:

1. **Genuine FP** — the student marked a non-mound symbol or empty
   space.
2. **Hungarian-matching artefact** — there *is* a curator mound within
   50 m, but Hungarian assigned that curator mound to a different
   (closer) student feature, leaving this one orphaned.
3. **Curator-GT miss** — the student caught a real mound that is not
   in the curator GT (Shawn believes near-zero on the GS sheets).
4. **Near-miss outside 50 m** — the closest curator mound is between
   50 m and 200 m away, suggesting digitisation imprecision rather
   than a true FP.

Usage
-----

Build the FP-candidate CSV only (no Streamlit, headless-safe)::

    .venv/bin/python scripts/review_student_fp_candidates.py --build-only

Launch the interactive reviewer (auto-builds the candidate CSV if it
is missing or stale)::

    .venv/bin/streamlit run scripts/review_student_fp_candidates.py

The wrapper script ``scripts/launch_gs4maps_fp_review.sh`` invokes the
reviewer with the canonical paths.

Outputs
-------

- ``results/student-gt-fp-review-gs4/fp-candidates.csv`` — one row per
  FP, sorted by ``source_map`` then nearest-curator distance ascending.
- ``results/student-gt-fp-review-gs4/fp-decisions.csv`` — one row per
  reviewed FP, written incrementally after each click.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

import geopandas as gpd
import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from PIL.Image import Image as PILImage

# --------------------------------------------------------------------------
# Path setup — let us import sibling helpers from scripts/.
# --------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

# Re-use raster helpers from the dedup reviewer (Approach A in the brief).
from review_gt_duplicates import (  # noqa: E402
    _MARKER_COLOURS,
    _best_raster_for_point,
    _resolve_raster,
)
from lib_advanced_metrics import match_detections_to_references  # noqa: E402

# =========================================================================
# Constants
# =========================================================================

REPO_ROOT = _SCRIPT_DIR.parent

# Inputs (mirror analyse_student_gt_fn_rate_gs4.py).
STUDENT_GT_PATH = (
    REPO_ROOT / "inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson"
)
CURATOR_GT_PATH = REPO_ROOT / "inputs/vectors/references/mounds-reference.geojson"
GS4_BOUNDS_PATH = REPO_ROOT / "inputs/vectors/bounds/gs-4maps-sheet-bounds.geojson"
RASTERS_DIR = REPO_ROOT / "inputs/rasters"

# Match radius (must mirror the source analysis to recover the same 17 FPs).
MATCH_RADIUS_M = 50.0
# Search radius when collecting "nearby" curator features for raster overlay
# and for the candidate CSV's nearest-curator-within-N columns.
NEIGHBOUR_RADIUS_M = 200.0
# Display window around the student feature, in metres.
DISPLAY_CONTEXT_M = 300.0
DISPLAY_PX = 600

# Outputs.
RESULTS_DIR = REPO_ROOT / "results/student-gt-fp-review-gs4"
CANDIDATES_CSV = RESULTS_DIR / "fp-candidates.csv"
DECISIONS_CSV = RESULTS_DIR / "fp-decisions.csv"

# Decision codes.
DECISION_GENUINE_FP = "genuine_fp"
DECISION_HUNGARIAN_ARTEFACT = "hungarian_artefact"
DECISION_CURATOR_MISSED = "curator_missed"
DECISION_NEAR_MISS_50_200M = "near_miss_50_200m"
DECISION_UNCERTAIN = "uncertain"

DECISION_OPTIONS: tuple[tuple[str, str], ...] = (
    (DECISION_GENUINE_FP, "Genuine FP (non-mound / empty space)"),
    (DECISION_HUNGARIAN_ARTEFACT, "Hungarian artefact (curator mound <50 m, "
                                  "stolen by another student)"),
    (DECISION_CURATOR_MISSED, "Curator missed a real mound"),
    (DECISION_NEAR_MISS_50_200M, "Near-miss (closest curator 50–200 m)"),
    (DECISION_UNCERTAIN, "Uncertain — can't tell from raster"),
)

_DECISION_CSV_COLUMNS = (
    "fp_index",
    "student_row_id",
    "source_map",
    "decision",
    "notes",
    "timestamp",
)


# =========================================================================
# Data classes
# =========================================================================


@dataclass(frozen=True)
class FPCandidate:
    """One unmatched student feature with its nearest-curator context."""

    fp_index: int  # 1-based, stable across runs (sorted by sheet, distance).
    student_row_id: int  # 0-based row index into the student GeoJSON.
    student_uuid: str
    map_symbol: str
    feature_type: str
    source_map: str
    student_x_m: float
    student_y_m: float
    student_lat: float
    student_lon: float
    nearest_curator_fid: int  # global curator nearest, regardless of distance
    nearest_curator_distance_m: float
    nearest_within_200_fid: int  # -1 if none within NEIGHBOUR_RADIUS_M
    nearest_within_200_distance_m: float  # NaN if none within NEIGHBOUR_RADIUS_M
    second_within_200_fid: int  # -1 if no second neighbour within 200 m
    second_within_200_distance_m: float

    @property
    def is_hungarian_artefact_candidate(self) -> bool:
        """True iff a curator mound exists within MATCH_RADIUS_M.

        Hungarian one-to-one assignment was given the chance to match this
        student, but did not — so if a curator mound is geometrically
        within 50 m, it must have been claimed by a different (closer)
        student feature. That's the diagnostic flavour of explanation 2.
        """
        return (
            np.isfinite(self.nearest_curator_distance_m)
            and self.nearest_curator_distance_m < MATCH_RADIUS_M
        )


# =========================================================================
# Candidate-CSV builder
# =========================================================================


def load_inputs() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Load student GT, curator GT, and 4-GS sheet bounds (all EPSG:32635)."""
    student = gpd.read_file(STUDENT_GT_PATH)
    curator = gpd.read_file(CURATOR_GT_PATH)
    bounds = gpd.read_file(GS4_BOUNDS_PATH)
    for name, gdf in [("student", student), ("curator", curator), ("bounds", bounds)]:
        if gdf.crs is None or gdf.crs.to_epsg() != 32635:
            raise ValueError(f"{name} CRS is {gdf.crs}, expected EPSG:32635")
    # Stable per-row ids — preserve original ordering of the GeoJSONs so the
    # ids round-trip via re-reads of the same file.
    student = student.reset_index(drop=True)
    student["_student_row_id"] = student.index.astype(int)
    curator = curator.reset_index(drop=True)
    curator["_curator_row_id"] = curator.index.astype(int)
    return student, curator, bounds


def _to_point(geom):
    """Curator features are MULTIPOINT; coerce to centroid Point."""
    return geom if geom.geom_type == "Point" else geom.centroid


def build_fp_candidates(
    student: gpd.GeoDataFrame,
    curator: gpd.GeoDataFrame,
    bounds: gpd.GeoDataFrame,
    radius_m: float = MATCH_RADIUS_M,
    neighbour_radius_m: float = NEIGHBOUR_RADIUS_M,
) -> list[FPCandidate]:
    """
    Reproduce the Hungarian one-to-one match per sheet and return one
    ``FPCandidate`` per unmatched student feature.

    For each unmatched student, computes:

    - The nearest curator feature *anywhere* on the same sheet (distance
      may exceed ``neighbour_radius_m``).
    - The 1st- and 2nd-nearest curator features whose distance is
      ≤ ``neighbour_radius_m`` (NaN/-1 if none).

    The 1st-nearest-anywhere column is the simplest diagnostic for the
    "Hungarian artefact" hypothesis: if that distance is < 50 m, the
    Hungarian assignment must have given the matching curator to a
    different student, since otherwise this pair would itself have
    matched. The 200 m fields support the "near-miss outside 50 m"
    category.

    Args:
        student: Student GT with ``_student_row_id`` column.
        curator: Curator GT with ``_curator_row_id`` column and ``Map``
            column for sheet attribution.
        bounds: 4-GS sheet-bounds frame with ``sheet_id`` column.
        radius_m: Hungarian match radius. Must be the same value as the
            source analysis (50 m) for the recovered FP set to match.
        neighbour_radius_m: Search radius for the within-N-m neighbour
            columns.

    Returns:
        Sorted list of FPCandidate, one per unmatched student feature,
        ordered by (source_map, nearest_curator_distance_m).
    """
    sheet_ids = sorted(bounds["sheet_id"].tolist())
    candidates: list[FPCandidate] = []

    for sheet_id in sheet_ids:
        cur_sub = curator[curator["Map"] == sheet_id].reset_index(drop=True)
        stu_sub = student[student["source_map"] == sheet_id].reset_index(drop=True)
        if len(stu_sub) == 0:
            continue

        cur_geoms = [_to_point(g) for g in cur_sub.geometry]
        stu_geoms = [_to_point(g) for g in stu_sub.geometry]

        _, _, unmatched_det, _ = match_detections_to_references(
            stu_geoms, cur_geoms, radius_m,
        )

        if not unmatched_det:
            continue

        # Pre-compute all curator coords on this sheet for distance lookups.
        if cur_geoms:
            cur_xy = np.array([(g.x, g.y) for g in cur_geoms], dtype=np.float64)
        else:
            cur_xy = np.empty((0, 2), dtype=np.float64)

        for det_idx in unmatched_det:
            stu_row = stu_sub.iloc[det_idx]
            stu_geom = stu_geoms[det_idx]
            sx = float(stu_geom.x)
            sy = float(stu_geom.y)

            # Distances to every curator on this sheet.
            if cur_xy.size == 0:
                near_fid = -1
                near_dist = float("nan")
                first200_fid = -1
                first200_dist = float("nan")
                second200_fid = -1
                second200_dist = float("nan")
            else:
                dists = np.hypot(cur_xy[:, 0] - sx, cur_xy[:, 1] - sy)
                order = np.argsort(dists, kind="stable")
                # Nearest overall (regardless of distance).
                near_local = int(order[0])
                near_fid = int(cur_sub.iloc[near_local]["fid"])
                near_dist = float(dists[near_local])
                # Within-200 m neighbours (1st and 2nd).
                in_band = [int(i) for i in order if dists[i] <= neighbour_radius_m]
                if not in_band:
                    first200_fid = -1
                    first200_dist = float("nan")
                    second200_fid = -1
                    second200_dist = float("nan")
                else:
                    first200_fid = int(cur_sub.iloc[in_band[0]]["fid"])
                    first200_dist = float(dists[in_band[0]])
                    if len(in_band) >= 2:
                        second200_fid = int(cur_sub.iloc[in_band[1]]["fid"])
                        second200_dist = float(dists[in_band[1]])
                    else:
                        second200_fid = -1
                        second200_dist = float("nan")

            candidates.append(
                FPCandidate(
                    fp_index=0,  # filled in after global sort
                    student_row_id=int(stu_row["_student_row_id"]),
                    student_uuid=str(stu_row.get("uuid", "")),
                    map_symbol=str(stu_row.get("MapSymbol", "")),
                    feature_type=str(stu_row.get("FeatureType", "")),
                    source_map=str(stu_row["source_map"]),
                    student_x_m=sx,
                    student_y_m=sy,
                    student_lat=float(stu_row.get("Latitude", float("nan"))),
                    student_lon=float(stu_row.get("Longitude", float("nan"))),
                    nearest_curator_fid=near_fid,
                    nearest_curator_distance_m=near_dist,
                    nearest_within_200_fid=first200_fid,
                    nearest_within_200_distance_m=first200_dist,
                    second_within_200_fid=second200_fid,
                    second_within_200_distance_m=second200_dist,
                )
            )

    # Sort and assign 1-based fp_index for stable display ordering.
    candidates.sort(
        key=lambda c: (c.source_map, c.nearest_curator_distance_m, c.student_row_id)
    )
    return [
        FPCandidate(**{**c.__dict__, "fp_index": i + 1})
        for i, c in enumerate(candidates)
    ]


def write_fp_candidates_csv(candidates: list[FPCandidate], path: Path) -> None:
    """Persist FP candidates to CSV with stable column ordering."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "fp_index": c.fp_index,
            "student_row_id": c.student_row_id,
            "student_uuid": c.student_uuid,
            "MapSymbol": c.map_symbol,
            "FeatureType": c.feature_type,
            "source_map": c.source_map,
            "student_x_m": f"{c.student_x_m:.4f}",
            "student_y_m": f"{c.student_y_m:.4f}",
            "student_lat": f"{c.student_lat:.6f}",
            "student_lon": f"{c.student_lon:.6f}",
            "nearest_curator_fid": c.nearest_curator_fid,
            "nearest_curator_distance_m": f"{c.nearest_curator_distance_m:.2f}",
            "nearest_within_200_fid": c.nearest_within_200_fid,
            "nearest_within_200_distance_m": (
                f"{c.nearest_within_200_distance_m:.2f}"
                if np.isfinite(c.nearest_within_200_distance_m) else ""
            ),
            "second_within_200_fid": c.second_within_200_fid,
            "second_within_200_distance_m": (
                f"{c.second_within_200_distance_m:.2f}"
                if np.isfinite(c.second_within_200_distance_m) else ""
            ),
        }
        for c in candidates
    ]
    pd.DataFrame(rows).to_csv(path, index=False)


def load_fp_candidates_csv(path: Path) -> list[FPCandidate]:
    """Read a previously-built FP-candidate CSV into FPCandidate objects."""
    df = pd.read_csv(path)
    out: list[FPCandidate] = []
    for _, r in df.iterrows():
        n2_dist = r.get("nearest_within_200_distance_m", "")
        s2_dist = r.get("second_within_200_distance_m", "")
        out.append(
            FPCandidate(
                fp_index=int(r["fp_index"]),
                student_row_id=int(r["student_row_id"]),
                student_uuid=str(r.get("student_uuid", "")),
                map_symbol=str(r.get("MapSymbol", "")),
                feature_type=str(r.get("FeatureType", "")),
                source_map=str(r["source_map"]),
                student_x_m=float(r["student_x_m"]),
                student_y_m=float(r["student_y_m"]),
                student_lat=float(r.get("student_lat", float("nan"))),
                student_lon=float(r.get("student_lon", float("nan"))),
                nearest_curator_fid=int(r["nearest_curator_fid"]),
                nearest_curator_distance_m=float(r["nearest_curator_distance_m"]),
                nearest_within_200_fid=int(r["nearest_within_200_fid"]),
                nearest_within_200_distance_m=(
                    float(n2_dist) if str(n2_dist) not in ("", "nan") else float("nan")
                ),
                second_within_200_fid=int(r["second_within_200_fid"]),
                second_within_200_distance_m=(
                    float(s2_dist) if str(s2_dist) not in ("", "nan") else float("nan")
                ),
            )
        )
    return out


# =========================================================================
# Decisions CSV I/O (per-FP, simpler schema than the dedup reviewer)
# =========================================================================


def load_decisions(path: Path) -> dict[int, dict]:
    """Load existing decisions keyed by ``fp_index``. Empty dict if absent."""
    if not path.is_file() or path.stat().st_size == 0:
        return {}
    try:
        df = pd.read_csv(path, dtype=str).fillna("")
    except pd.errors.EmptyDataError:
        return {}
    if "fp_index" not in df.columns:
        return {}
    out: dict[int, dict] = {}
    for _, row in df.iterrows():
        try:
            key = int(row["fp_index"])
        except (TypeError, ValueError):
            continue
        out[key] = row.to_dict()
    return out


def save_decisions(decisions: dict[int, dict], path: Path) -> None:
    """Atomically write the decisions dict to CSV (tmp → rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [decisions[k] for k in sorted(decisions)]
    df = pd.DataFrame(rows, columns=list(_DECISION_CSV_COLUMNS))
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_csv(tmp, index=False)
    tmp.replace(path)


def format_decision(
    candidate: FPCandidate,
    decision: str,
    notes: str = "",
) -> dict:
    """Build a CSV-ready row dict for a single FP decision."""
    return {
        "fp_index": str(candidate.fp_index),
        "student_row_id": str(candidate.student_row_id),
        "source_map": candidate.source_map,
        "decision": decision,
        "notes": notes or "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# =========================================================================
# Raster rendering — student point + nearby curator markers.
# =========================================================================


def render_fp_image(
    candidate: FPCandidate,
    curator_neighbours: list[tuple[int, float, float, float]],
    rasters_dir: Path,
    context_m: float = DISPLAY_CONTEXT_M,
    display_px: int = DISPLAY_PX,
) -> "PILImage":
    """
    Render a context crop centred on the student feature.

    The student point is drawn in red with label ``S``; each supplied
    curator neighbour is drawn in blue with sequential labels ``C1``,
    ``C2``, ... in distance-ascending order. Falls back to a grey
    placeholder if the raster cannot be located, mirroring the dedup
    reviewer's behaviour for edge clusters.

    Args:
        candidate: The FP under review.
        curator_neighbours: List of ``(fid, x_m, y_m, distance_m)`` for
            curator features near the student point. Already sorted by
            ``distance_m`` ascending — the renderer respects that order
            when assigning labels.
        rasters_dir: Directory containing the GS sheet GeoTIFFs.
        context_m: Window size in metres (square, centred on student).
        display_px: Output image size in pixels (square).

    Returns:
        A PIL RGB image ``display_px`` × ``display_px`` in size.
    """
    from PIL import Image, ImageDraw
    import rasterio
    from rasterio.windows import Window

    sx, sy = candidate.student_x_m, candidate.student_y_m

    raster_path = _best_raster_for_point(rasters_dir, sx, sy)
    if raster_path is None:
        raster_path = _resolve_raster(rasters_dir, candidate.source_map)
    if raster_path is None:
        return _fp_placeholder_image(candidate, curator_neighbours, size=display_px)

    with rasterio.open(raster_path) as src:
        row_f, col_f = src.index(sx, sy)
        row_c = int(round(float(row_f)))
        col_c = int(round(float(col_f)))
        res_m_per_px = abs(src.transform.a)
        half_px = max(1, int(round(context_m / 2 / res_m_per_px)))
        window = Window(col_c - half_px, row_c - half_px, half_px * 2, half_px * 2)
        arr = src.read(window=window, boundless=True, fill_value=0)
        n_bands = arr.shape[0]
        if n_bands >= 3:
            img_data = arr[:3].transpose(1, 2, 0)
        elif n_bands == 1:
            g = arr[0]
            img_data = np.stack([g, g, g], axis=-1)
        elif n_bands == 2:
            g = arr[0]
            img_data = np.stack([g, g, g], axis=-1)
        else:
            return _fp_placeholder_image(candidate, curator_neighbours, size=display_px)

        raw_img = Image.fromarray(img_data.astype(np.uint8)).convert("RGB")
        scale = display_px / raw_img.size[0] if raw_img.size[0] > 0 else 1.0
        img = raw_img.resize((display_px, display_px), Image.LANCZOS)

        draw = ImageDraw.Draw(img)
        marker_r = max(10, int(display_px * 0.025))

        # Student marker: red circle with label "S".
        student_colour = (220, 20, 20)
        s_row_f, s_col_f = src.index(sx, sy)
        lx = int(round((float(s_col_f) - (col_c - half_px)) * scale))
        ly = int(round((float(s_row_f) - (row_c - half_px)) * scale))
        draw.ellipse(
            [lx - marker_r, ly - marker_r, lx + marker_r, ly + marker_r],
            outline=student_colour, width=4,
        )
        draw.text((lx + marker_r + 3, ly - marker_r - 3), "S", fill=student_colour)

        # Curator markers: blue circles with labels C1, C2, ... .
        curator_colour = (20, 60, 220)
        for i, (_fid, cx_m, cy_m, _dist) in enumerate(curator_neighbours):
            c_row_f, c_col_f = src.index(cx_m, cy_m)
            cxp = int(round((float(c_col_f) - (col_c - half_px)) * scale))
            cyp = int(round((float(c_row_f) - (row_c - half_px)) * scale))
            draw.ellipse(
                [cxp - marker_r, cyp - marker_r, cxp + marker_r, cyp + marker_r],
                outline=curator_colour, width=3,
            )
            draw.text(
                (cxp + marker_r + 3, cyp - marker_r - 3),
                f"C{i + 1}", fill=curator_colour,
            )
    return img


def _fp_placeholder_image(
    candidate: FPCandidate,
    curator_neighbours: list[tuple[int, float, float, float]],
    size: int = 600,
) -> "PILImage":
    """Grey-canvas fallback when no raster covers the student point."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (size, size), (200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.text(
        (10, 10),
        f"[raster missing]\nmap: {candidate.source_map}\n"
        f"FP {candidate.fp_index}",
        fill=(40, 40, 40),
    )
    sx, sy = candidate.student_x_m, candidate.student_y_m
    pts = [(sx, sy)] + [(cx, cy) for _, cx, cy, _ in curator_neighbours]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 10.0)
    pad = 40

    def _to_px(px_m: float, py_m: float) -> tuple[int, int]:
        lx = int((px_m - min(xs)) / span * (size - 2 * pad) + pad)
        ly = size - int((py_m - min(ys)) / span * (size - 2 * pad) + pad)
        return lx, ly

    student_colour = _MARKER_COLOURS[0]
    lx, ly = _to_px(sx, sy)
    draw.ellipse([lx - 12, ly - 12, lx + 12, ly + 12],
                 outline=student_colour, width=4)
    draw.text((lx + 14, ly - 14), "S", fill=student_colour)

    curator_colour = _MARKER_COLOURS[1]
    for i, (_fid, cx_m, cy_m, _d) in enumerate(curator_neighbours):
        cxp, cyp = _to_px(cx_m, cy_m)
        draw.ellipse([cxp - 12, cyp - 12, cxp + 12, cyp + 12],
                     outline=curator_colour, width=3)
        draw.text((cxp + 14, cyp - 14), f"C{i + 1}", fill=curator_colour)
    return img


# =========================================================================
# Streamlit UI
# =========================================================================


def _curator_neighbours_for_fp(
    candidate: FPCandidate,
    curator: gpd.GeoDataFrame,
    radius_m: float = 150.0,
) -> list[tuple[int, float, float, float]]:
    """
    Collect curator features within ``radius_m`` of the student point on
    the same sheet, sorted ascending by distance.

    Uses ``radius_m = 150`` by default — a touch under the
    ``DISPLAY_CONTEXT_M / 2`` window so all returned markers will fall
    inside the rendered crop.

    Returns:
        List of ``(curator_fid, curator_x_m, curator_y_m, distance_m)``.
    """
    cur_sub = curator[curator["Map"] == candidate.source_map]
    if cur_sub.empty:
        return []
    out: list[tuple[int, float, float, float]] = []
    for _, row in cur_sub.iterrows():
        g = row.geometry
        p = g if g.geom_type == "Point" else g.centroid
        d = float(np.hypot(p.x - candidate.student_x_m, p.y - candidate.student_y_m))
        if d <= radius_m:
            out.append((int(row["fid"]), float(p.x), float(p.y), d))
    out.sort(key=lambda t: t[3])
    return out


def run_streamlit(args: argparse.Namespace) -> None:
    """Launch the interactive FP-review UI. Imports Streamlit lazily."""
    import streamlit as st

    st.set_page_config(page_title="Student-GT FP Review (4 GS)", layout="centered")
    st.title("Student-GT False-Positive Review — 4 GS Maps")

    candidates_path = Path(args.candidates)
    decisions_path = Path(args.decisions)
    rasters_dir = Path(args.rasters_dir)

    # Auto-build the candidate CSV if missing or if --rebuild was passed.
    if args.rebuild or not candidates_path.is_file():
        with st.spinner("Building FP-candidate CSV (Hungarian match @ 50 m)…"):
            student, curator, bounds = load_inputs()
            candidates = build_fp_candidates(student, curator, bounds)
            write_fp_candidates_csv(candidates, candidates_path)
        st.success(
            f"Built {len(candidates)} FP candidates → "
            f"`{candidates_path.relative_to(REPO_ROOT)}`"
        )

    candidates = load_fp_candidates_csv(candidates_path)
    if not candidates:
        st.success("No FP candidates to review.")
        return

    # Always reload the curator GT so the on-screen neighbours are derived
    # straight from the canonical file rather than the cached CSV row.
    curator = gpd.read_file(CURATOR_GT_PATH)

    decisions = st.session_state.setdefault(
        "fp_decisions", load_decisions(decisions_path),
    )

    # Find the next un-decided FP. The user can also navigate freely via
    # the sidebar selectbox — useful when revisiting a specific decision.
    total = len(candidates)
    decided_n = sum(1 for c in candidates if c.fp_index in decisions)

    st.sidebar.markdown("### Navigation")
    options = [
        f"{c.fp_index:02d}  ({c.source_map}, "
        f"{c.nearest_curator_distance_m:.0f} m)"
        + ("  ✓" if c.fp_index in decisions else "")
        for c in candidates
    ]

    # Default selection: first un-decided FP.
    default_idx = 0
    for i, c in enumerate(candidates):
        if c.fp_index not in decisions:
            default_idx = i
            break

    chosen = st.sidebar.selectbox(
        "Jump to FP", options, index=default_idx,
    )
    idx = options.index(chosen)
    candidate = candidates[idx]

    st.progress(decided_n / total if total else 1.0,
                text=f"Decided {decided_n} / {total}")

    # Header.
    st.markdown(
        f"### FP {candidate.fp_index} of {total}  \n"
        f"**Map**: `{candidate.source_map}`  •  "
        f"**MapSymbol**: {candidate.map_symbol or '(blank)'}  •  "
        f"**FeatureType**: {candidate.feature_type}  \n"
        f"**Student row id**: `{candidate.student_row_id}`  •  "
        f"**Student uuid**: `{candidate.student_uuid}`  \n"
        f"**Student point**: ({candidate.student_x_m:.2f}, "
        f"{candidate.student_y_m:.2f}) EPSG:32635  •  "
        f"({candidate.student_lat:.5f}, {candidate.student_lon:.5f}) WGS84"
    )

    # Diagnostic flag for the Hungarian-artefact category.
    if candidate.is_hungarian_artefact_candidate:
        st.warning(
            f"⚠️ Nearest curator is "
            f"**{candidate.nearest_curator_distance_m:.1f} m** away — "
            f"that is *inside* the 50 m Hungarian match radius. The most "
            f"likely explanation is that another (closer) student feature "
            f"claimed this curator mound first; press "
            f"**Hungarian artefact** below if the raster confirms a "
            f"nearby mound."
        )

    # Render the crop with student + nearby curator markers.
    neighbours = _curator_neighbours_for_fp(candidate, curator)
    with st.spinner("Rendering raster crop…"):
        img = render_fp_image(candidate, neighbours, rasters_dir)
    st.image(img, width="stretch")

    actual_raster = _best_raster_for_point(
        rasters_dir, candidate.student_x_m, candidate.student_y_m,
    )
    if actual_raster is not None and actual_raster.stem != candidate.source_map:
        st.caption(
            f"Rendered from **{actual_raster.stem}** (auto-selected for "
            f"best context; declared source_map is "
            f"{candidate.source_map})."
        )

    # Distance summary table.
    rows: list[dict] = [{
        "rank": "Nearest (any distance)",
        "curator_fid": candidate.nearest_curator_fid,
        "distance_m": f"{candidate.nearest_curator_distance_m:.2f}",
    }]
    if candidate.nearest_within_200_fid >= 0:
        rows.append({
            "rank": "1st within 200 m",
            "curator_fid": candidate.nearest_within_200_fid,
            "distance_m": f"{candidate.nearest_within_200_distance_m:.2f}",
        })
    if candidate.second_within_200_fid >= 0:
        rows.append({
            "rank": "2nd within 200 m",
            "curator_fid": candidate.second_within_200_fid,
            "distance_m": f"{candidate.second_within_200_distance_m:.2f}",
        })
    st.markdown("#### Curator-neighbour distances")
    st.table(pd.DataFrame(rows))

    if neighbours:
        with st.expander("Curator features rendered on the crop"):
            for i, (fid, cx, cy, d) in enumerate(neighbours):
                st.write(
                    f"- **C{i + 1}** (fid=`{fid}`)  •  ({cx:.2f}, {cy:.2f})"
                    f"  •  {d:.2f} m from student"
                )
    else:
        st.info("No curator features within 150 m of the student point.")

    # Decision UI.
    existing = decisions.get(candidate.fp_index, {})
    existing_decision = existing.get("decision", "")
    existing_notes = existing.get("notes", "")

    st.markdown("#### Decision")
    if existing_decision:
        st.caption(
            f"Current decision: **{existing_decision}** "
            f"(saved {existing.get('timestamp', '')[:19]} UTC). "
            f"Re-clicking a button overwrites; you can also edit the "
            f"notes field below."
        )

    notes = st.text_area(
        "Notes (optional)",
        value=existing_notes,
        key=f"notes_{candidate.fp_index}",
        height=80,
    )

    cols = st.columns(len(DECISION_OPTIONS))
    for i, (code, label) in enumerate(DECISION_OPTIONS):
        is_current = code == existing_decision
        button_label = f"{'✅ ' if is_current else ''}{label}"
        if cols[i].button(
            button_label,
            key=f"dec_{code}_{candidate.fp_index}",
            use_container_width=True,
        ):
            decisions[candidate.fp_index] = format_decision(
                candidate, code, notes=notes,
            )
            save_decisions(decisions, decisions_path)
            st.rerun()

    # Save-notes-only button: updates the notes for the existing decision
    # without changing its code (or creates an "uncertain" placeholder
    # if the user is parking a thought before deciding).
    if st.button(
        "💾 Save notes (without changing decision)",
        key=f"save_notes_{candidate.fp_index}",
    ):
        if existing_decision:
            row = dict(decisions[candidate.fp_index])
            row["notes"] = notes
            row["timestamp"] = datetime.now(timezone.utc).isoformat()
            decisions[candidate.fp_index] = row
        else:
            decisions[candidate.fp_index] = format_decision(
                candidate, DECISION_UNCERTAIN, notes=notes,
            )
        save_decisions(decisions, decisions_path)
        st.rerun()

    # End-of-list summary.
    if decided_n == total:
        st.success(
            "All FPs reviewed. The decisions CSV is the final artefact "
            f"(`{decisions_path.relative_to(REPO_ROOT)}`). Re-run the "
            "analysis script's reporting layer to produce a per-category "
            "tally if desired."
        )


# =========================================================================
# CLI entry
# =========================================================================


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI parser."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--candidates", type=str, default=str(CANDIDATES_CSV),
        help="FP-candidate CSV (input + output of --build-only).",
    )
    p.add_argument(
        "--decisions", type=str, default=str(DECISIONS_CSV),
        help="Decisions CSV (input + output during the review).",
    )
    p.add_argument(
        "--rasters-dir", type=str, default=str(RASTERS_DIR),
        help="Directory containing the four GS sheet GeoTIFFs.",
    )
    p.add_argument(
        "--build-only", action="store_true",
        help="Build the FP-candidate CSV and exit (no Streamlit). "
             "Used by tests and by the launch wrapper's pre-flight step.",
    )
    p.add_argument(
        "--rebuild", action="store_true",
        help="Force rebuild of the FP-candidate CSV before launching the UI.",
    )
    return p


def main() -> int:
    """Dispatch to --build-only or the Streamlit UI based on flags."""
    parser = build_parser()
    try:
        args = parser.parse_args(sys.argv[1:])
    except SystemExit as exc:
        code = exc.code
        return code if isinstance(code, int) else 2

    if args.build_only:
        student, curator, bounds = load_inputs()
        candidates = build_fp_candidates(student, curator, bounds)
        write_fp_candidates_csv(candidates, Path(args.candidates))
        print(
            f"Built {len(candidates)} FP candidates → {args.candidates}"
        )
        # Surface the diagnostic Hungarian-artefact count immediately so
        # the operator sees it before launching the UI.
        n_hungarian = sum(1 for c in candidates if c.is_hungarian_artefact_candidate)
        print(
            f"  of which {n_hungarian} have a curator mound within "
            f"{MATCH_RADIUS_M:.0f} m (likely Hungarian artefacts)."
        )
        # Per-sheet breakdown.
        by_map: dict[str, int] = {}
        for c in candidates:
            by_map[c.source_map] = by_map.get(c.source_map, 0) + 1
        print("  by source_map:")
        for m in sorted(by_map):
            print(f"    {m}: {by_map[m]}")
        return 0

    run_streamlit(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
