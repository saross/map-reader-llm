"""
Tests for the additive standardised-extension mode of
``compute_corrected_f1_multi_buffer`` (Session 132, queue items 2–3).

Tier 1 unit tests covering three guarantees:

1. **Loader validation** — ``load_standardised_extension`` builds the
   phantom GDF from the ruling-21 extension schema, and refuses missing
   columns or an empty layer rather than guessing.
2. **Gating semantics** — in extension mode the phantom set enters the
   extended GT WHOLE at every buffer radius (marked centres are exactly
   localised, so the legacy ``buffer_metres <= R`` localisation gate does
   not apply). A detection sitting on an extension mound is credited even
   at sub-50 m radii — the Obs 371 sub-50 m collapse is cured.
3. **Mode exclusivity** — extension and review inputs are mutually
   exclusive at both the ``compute_at_buffer`` and ``run`` layers, so a
   mixed-reference invocation cannot happen silently.
"""

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, box

from scripts.compute_corrected_f1_multi_buffer import (
    compute_at_buffer,
    load_standardised_extension,
    run,
)

CRS = "EPSG:32635"
ORIGIN_X, ORIGIN_Y, TILE = 500_000.0, 4_700_000.0, 100.0

EXTENSION_HEADER = (
    "candidate_id,x,y,map_name,symbol_type,confidence_grade,"
    "position_source,provenance,nearest_student_m\n"
)


def _extension_csv(tmp_path, rows: list[str]):
    """Write a minimal standardised-extension CSV and return its path."""
    path = tmp_path / "extension-mounds-standardised.csv"
    path.write_text(EXTENSION_HEADER + "".join(rows))
    return path


def _scene() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Two-tile scene: tile A has a student mound + a detection on it; tile
    B holds a second detection 30 m from tile B's centre-left edge with NO
    student mound — the extension-mound test bed."""
    bounds = gpd.GeoDataFrame(
        {"tile_name": ["K-1_x0_y0", "K-1_x100_y0"]},
        geometry=[
            box(ORIGIN_X, ORIGIN_Y, ORIGIN_X + TILE, ORIGIN_Y + TILE),
            box(ORIGIN_X + TILE, ORIGIN_Y, ORIGIN_X + 2 * TILE, ORIGIN_Y + TILE),
        ],
        crs=CRS,
    )
    centre_a = (ORIGIN_X + TILE / 2, ORIGIN_Y + TILE / 2)
    centre_b = (ORIGIN_X + 1.5 * TILE, ORIGIN_Y + TILE / 2)
    student = gpd.GeoDataFrame(
        {"source_map": ["K-1"]}, geometry=[Point(*centre_a)], crs=CRS,
    )
    det = gpd.GeoDataFrame(
        {"source_tile": ["K-1_x0_y0", "K-1_x100_y0"]},
        geometry=[Point(*centre_a), Point(*centre_b)],
        crs=CRS,
    )
    return det, student, bounds


def _extension_gdf_at(x: float, y: float, nearest: float) -> gpd.GeoDataFrame:
    """One-mound extension layer at (x, y) via the real loader."""
    df = pd.DataFrame([{
        "candidate_id": "7", "x": x, "y": y, "map_name": "K-1",
        "symbol_type": "burial_mound", "confidence_grade": "directly_reviewed",
        "position_source": "own_mark", "provenance": "model_detection",
        "nearest_student_m": nearest,
    }])
    geometry = [Point(x, y)]
    return gpd.GeoDataFrame(
        df.rename(columns={"map_name": "source_map"})[
            ["candidate_id", "source_map", "nearest_student_m"]
        ],
        geometry=geometry, crs=CRS,
    )


# --------------------------------------------------------------------------- #
# Loader validation
# --------------------------------------------------------------------------- #

@pytest.mark.tier1
def test_loader_builds_phantom_gdf(tmp_path):
    """A valid extension CSV loads with source_map, geometry, and distance."""
    path = _extension_csv(tmp_path, [
        "0,500150.0,4700050.0,K-1,burial_mound,directly_reviewed,"
        "own_mark,model_detection,120.5\n",
    ])
    gdf = load_standardised_extension(path, crs=CRS)
    assert len(gdf) == 1
    assert gdf.iloc[0]["source_map"] == "K-1"
    assert gdf.iloc[0]["nearest_student_m"] == 120.5
    assert gdf.iloc[0].geometry.x == 500150.0


@pytest.mark.tier1
def test_loader_rejects_missing_columns(tmp_path):
    """A CSV without nearest_student_m must be refused, not guessed at."""
    path = tmp_path / "bad.csv"
    path.write_text("candidate_id,x,y,map_name\n0,1.0,2.0,K-1\n")
    with pytest.raises(ValueError, match="missing expected"):
        load_standardised_extension(path, crs=CRS)


@pytest.mark.tier1
def test_loader_rejects_empty_layer(tmp_path):
    """An empty extension layer is a data defect, not a valid reference."""
    path = _extension_csv(tmp_path, [])
    with pytest.raises(ValueError, match="empty"):
        load_standardised_extension(path, crs=CRS)


# --------------------------------------------------------------------------- #
# Gating semantics — the whole layer enters at every R
# --------------------------------------------------------------------------- #

@pytest.mark.tier1
def test_extension_enters_at_every_buffer():
    """The extension phantom set is constant across R — no per-buffer gate.

    Legacy ring gating would exclude the phantom below its ring; in
    standardised mode ``n_reviewer_promoted`` is identical at R = 5 and
    R = 150.
    """
    det, student, bounds = _scene()
    ext = _extension_gdf_at(ORIGIN_X + 1.5 * TILE, ORIGIN_Y + TILE / 2, 141.4)
    results = {}
    for r_m in (5, 150):
        results[r_m] = compute_at_buffer(
            gdf_det=det, gdf_student=student, gdf_bounds=bounds,
            review_yesterday=None, review_today=None,
            buffer_r=r_m, n_bootstrap=10, seed=42,
            extension_gdf=ext,
        )
    assert results[5].n_reviewer_promoted == 1
    assert results[150].n_reviewer_promoted == 1


@pytest.mark.tier1
def test_sub50_detection_of_extension_mound_is_credited():
    """The Obs 371 cure: at R = 5 m a detection ON an extension mound is a
    TP (legacy ring gating booked it FP below the mound's 50 m ring)."""
    det, student, bounds = _scene()
    ext = _extension_gdf_at(ORIGIN_X + 1.5 * TILE, ORIGIN_Y + TILE / 2, 141.4)
    res = compute_at_buffer(
        gdf_det=det, gdf_student=student, gdf_bounds=bounds,
        review_yesterday=None, review_today=None,
        buffer_r=5, n_bootstrap=10, seed=42,
        extension_gdf=ext,
    )
    # Both detections match: the student mound in tile A, the extension
    # mound in tile B. No FPs, no FNs.
    assert (res.tp, res.fp, res.fn) == (2, 0, 0)
    assert res.f1 == 1.0


@pytest.mark.tier1
def test_dedup_still_drops_extension_twin_of_student_point():
    """An extension record within 5 m of a same-map student point is still
    dropped by build_extended_gt's channel-duplicate audit (expected count
    on the real standardised layers: 0, min nearest_student_m 10.32 m)."""
    det, student, bounds = _scene()
    centre_a = (ORIGIN_X + TILE / 2, ORIGIN_Y + TILE / 2)
    ext = _extension_gdf_at(centre_a[0] + 1.0, centre_a[1], 1.0)
    res = compute_at_buffer(
        gdf_det=det, gdf_student=student, gdf_bounds=bounds,
        review_yesterday=None, review_today=None,
        buffer_r=50, n_bootstrap=10, seed=42,
        extension_gdf=ext,
    )
    assert res.n_phantom_duplicates_dropped == 1
    assert res.n_reviewer_promoted == 0


# --------------------------------------------------------------------------- #
# Mode exclusivity
# --------------------------------------------------------------------------- #

@pytest.mark.tier1
def test_compute_at_buffer_rejects_mixed_modes():
    """Extension GDF plus review DataFrames must raise, never mix."""
    det, student, bounds = _scene()
    ext = _extension_gdf_at(ORIGIN_X + 1.5 * TILE, ORIGIN_Y + TILE / 2, 141.4)
    empty_review = pd.DataFrame(
        columns=["candidate_id", "human_label", "buffer_metres",
                 "x", "y", "map_name"],
    )
    with pytest.raises(ValueError, match="mutually exclusive"):
        compute_at_buffer(
            gdf_det=det, gdf_student=student, gdf_bounds=bounds,
            review_yesterday=empty_review, review_today=empty_review,
            buffer_r=50, n_bootstrap=10, seed=42,
            extension_gdf=ext,
        )


@pytest.mark.tier1
def test_run_rejects_neither_and_both_modes(tmp_path):
    """run() must refuse a phantom-source-less or double-sourced call."""
    common = {
        "verified_detections": tmp_path / "det.geojson",
        "student_gt": tmp_path / "gt.geojson",
        "bounds": tmp_path / "bounds.geojson",
        "output_dir": tmp_path / "out",
        "buffers": [50], "n_bootstrap": 10, "seed": 42,
    }
    with pytest.raises(ValueError, match="supply either"):
        run(**common)  # neither
    with pytest.raises(ValueError, match="supply either"):
        run(
            **common,
            review_yesterday=tmp_path / "y.csv",
            review_today=tmp_path / "t.csv",
            extension_csv=tmp_path / "ext.csv",
        )  # both
