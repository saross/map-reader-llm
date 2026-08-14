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


def _extension_gdf_at(
    tmp_path, x: float, y: float, nearest: float,
) -> gpd.GeoDataFrame:
    """One-mound extension layer at (x, y), built through the REAL loader
    so every behaviour test also exercises the loader's output schema."""
    path = _extension_csv(tmp_path, [
        f"7,{x},{y},K-1,burial_mound,directly_reviewed,"
        f"own_mark,model_detection,{nearest}\n",
    ])
    return load_standardised_extension(path, crs=CRS)


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
def test_extension_enters_at_every_buffer(tmp_path):
    """The extension phantom set is constant across R — no per-buffer gate.

    Legacy ring gating would exclude the phantom below its ring; in
    standardised mode ``n_reviewer_promoted`` is identical at R = 5 and
    R = 150.
    """
    det, student, bounds = _scene()
    ext = _extension_gdf_at(
        tmp_path, ORIGIN_X + 1.5 * TILE, ORIGIN_Y + TILE / 2, 100.0,
    )
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
def test_sub50_detection_of_extension_mound_is_credited(tmp_path):
    """The Obs 371 cure: at R = 5 m a detection ON an extension mound is a
    TP (legacy ring gating booked it FP below the mound's 50 m ring)."""
    det, student, bounds = _scene()
    ext = _extension_gdf_at(
        tmp_path, ORIGIN_X + 1.5 * TILE, ORIGIN_Y + TILE / 2, 100.0,
    )
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
def test_dedup_still_drops_extension_twin_of_student_point(tmp_path):
    """An extension record within 5 m of a same-map student point is still
    dropped by build_extended_gt's channel-duplicate audit (expected count
    on the real standardised layers: 0, min nearest_student_m 10.32 m)."""
    det, student, bounds = _scene()
    centre_a = (ORIGIN_X + TILE / 2, ORIGIN_Y + TILE / 2)
    ext = _extension_gdf_at(tmp_path, centre_a[0] + 1.0, centre_a[1], 1.0)
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
def test_compute_at_buffer_rejects_mixed_modes(tmp_path):
    """Extension GDF plus review DataFrames must raise, never mix."""
    det, student, bounds = _scene()
    ext = _extension_gdf_at(
        tmp_path, ORIGIN_X + 1.5 * TILE, ORIGIN_Y + TILE / 2, 100.0,
    )
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
def test_run_rejects_invalid_mode_combinations(tmp_path):
    """run() must refuse every invalid phantom-source combination.

    Neither source; both complete sources; and — the audit-found hole —
    a LONE review CSV alongside the extension CSV (either side), which
    the original XOR check accepted silently.
    """
    common = {
        "verified_detections": tmp_path / "det.geojson",
        "student_gt": tmp_path / "gt.geojson",
        "bounds": tmp_path / "bounds.geojson",
        "output_dir": tmp_path / "out",
        "buffers": [50], "n_bootstrap": 10, "seed": 42,
    }
    with pytest.raises(ValueError, match="supply either"):
        run(**common)  # neither
    with pytest.raises(ValueError, match="mutually exclusive"):
        run(
            **common,
            review_yesterday=tmp_path / "y.csv",
            review_today=tmp_path / "t.csv",
            extension_csv=tmp_path / "ext.csv",
        )  # both complete
    with pytest.raises(ValueError, match="mutually exclusive"):
        run(
            **common,
            review_yesterday=tmp_path / "y.csv",
            extension_csv=tmp_path / "ext.csv",
        )  # lone yesterday + extension
    with pytest.raises(ValueError, match="mutually exclusive"):
        run(
            **common,
            review_today=tmp_path / "t.csv",
            extension_csv=tmp_path / "ext.csv",
        )  # lone today + extension
    with pytest.raises(ValueError, match="lone review CSV"):
        run(**common, review_yesterday=tmp_path / "y.csv")  # half a pair


# --------------------------------------------------------------------------- #
# De-duplication tolerance override (A0 reproduction support)
# --------------------------------------------------------------------------- #

@pytest.mark.tier1
def test_dedup_tolerance_zero_reproduces_prefix_behaviour(tmp_path):
    """dedup_tolerance_m=0 keeps a 1 m twin (pre-W6-E9 reproduction);
    the default 5 m tolerance drops it."""
    det, student, bounds = _scene()
    centre_a = (ORIGIN_X + TILE / 2, ORIGIN_Y + TILE / 2)
    ext = _extension_gdf_at(tmp_path, centre_a[0] + 1.0, centre_a[1], 1.0)
    res_off = compute_at_buffer(
        gdf_det=det, gdf_student=student, gdf_bounds=bounds,
        review_yesterday=None, review_today=None,
        buffer_r=50, n_bootstrap=10, seed=42,
        extension_gdf=ext, dedup_tolerance_m=0.0,
    )
    assert res_off.n_phantom_duplicates_dropped == 0
    assert res_off.n_reviewer_promoted == 1
    res_on = compute_at_buffer(
        gdf_det=det, gdf_student=student, gdf_bounds=bounds,
        review_yesterday=None, review_today=None,
        buffer_r=50, n_bootstrap=10, seed=42,
        extension_gdf=ext,
    )
    assert res_on.n_phantom_duplicates_dropped == 1


# --------------------------------------------------------------------------- #
# End-to-end run() — the wiring, not just the functions
# --------------------------------------------------------------------------- #

def _scene_on_disk(tmp_path):
    """Write the synthetic scene to disk for end-to-end run() tests."""
    det, student, bounds = _scene()
    paths = {
        "det": tmp_path / "det.geojson",
        "student": tmp_path / "student.geojson",
        "bounds": tmp_path / "bounds.geojson",
    }
    det.to_file(paths["det"], driver="GeoJSON")
    student.to_file(paths["student"], driver="GeoJSON")
    bounds.to_file(paths["bounds"], driver="GeoJSON")
    return paths


@pytest.mark.tier1
def test_run_end_to_end_extension_mode(tmp_path):
    """run() in extension mode: real CSV in, correct artefacts out.

    Pins the wiring the unit tests cannot see: the loaded layer reaches
    the scoring (n_reviewer_promoted_at_R), the summary carries the
    standardised exclusions block and input_paths (extension_csv present,
    review keys absent), and the report table is written.
    """
    import json as json_mod

    paths = _scene_on_disk(tmp_path)
    # TWO extension records (vs ONE student mound) so a transposition of
    # the n_ref_student / n_extension report columns is detectable.
    ext_csv = _extension_csv(tmp_path, [
        f"7,{ORIGIN_X + 1.5 * TILE},{ORIGIN_Y + TILE / 2},K-1,burial_mound,"
        "directly_reviewed,own_mark,model_detection,100.0\n",
        f"8,{ORIGIN_X + 1.75 * TILE},{ORIGIN_Y + TILE / 2},K-1,burial_mound,"
        "directly_reviewed,own_mark,model_detection,125.0\n",
    ])
    out_dir = tmp_path / "out"
    run(
        verified_detections=paths["det"], student_gt=paths["student"],
        bounds=paths["bounds"], extension_csv=ext_csv,
        output_dir=out_dir, buffers=[5, 50], n_bootstrap=10, seed=42,
        compute_mcc=True,
    )
    with open(out_dir / "summary.json", encoding="utf-8") as fh:
        summary = json_mod.load(fh)
    # The extension layer reached the scoring, whole, at BOTH buffers.
    for row in summary["results"]:
        assert row["n_reviewer_promoted_at_R"] == 2
        assert row["n_phantom_duplicates_dropped"] == 0
    # MCC present and buffer-invariant.
    mccs = {row["tile_classification"]["mcc"] for row in summary["results"]}
    assert len(mccs) == 1
    # Standardised exclusions block, not the ring-review one.
    assert summary["exclusions"]["sentinel_buffer_metres"] is None
    assert "standardised" in summary["methodology"].lower()
    # Provenance: extension_csv recorded, review keys absent.
    ip = summary["metadata"]["input_paths"]
    assert "extension_csv" in ip
    assert "review_yesterday" not in ip and "review_today" not in ip
    # Report written with the standardised header, and the data row keeps
    # the n_ref_student (1) / n_extension (2) column ORDER.
    report = (out_dir / "report_autogen.md").read_text()
    assert "standardised reference" in report
    assert "n_ref_student | n_extension | n_ref_extended" in report
    # n_ref_student=1, n_extension=2, n_ref_extended=3 in exactly this
    # order; a transposed row would read "| 2 | 1 | 3 |".
    assert "| 1 | 2 | 3 |" in report
    assert (out_dir / "corrected-f1.csv").exists()


@pytest.mark.tier1
def test_run_end_to_end_legacy_mode_shape(tmp_path):
    """run() in legacy review mode: the exclusions block, methodology
    string, and input_paths keys keep their historical shape (the
    byte-identity contract's checkable core)."""
    import json as json_mod

    paths = _scene_on_disk(tmp_path)
    empty = tmp_path / "empty.csv"
    empty.write_text("candidate_id,human_label,buffer_metres,x,y,map_name\n")
    out_dir = tmp_path / "out-legacy"
    run(
        verified_detections=paths["det"], student_gt=paths["student"],
        bounds=paths["bounds"], review_yesterday=empty, review_today=empty,
        output_dir=out_dir, buffers=[50], n_bootstrap=10, seed=42,
    )
    with open(out_dir / "summary.json", encoding="utf-8") as fh:
        summary = json_mod.load(fh)
    assert summary["methodology"] == (
        "Approach B — extended-GT-at-R Hungarian matching"
    )
    assert summary["exclusions"]["sentinel_buffer_metres"] == 200
    ip = summary["metadata"]["input_paths"]
    assert list(ip.keys()) == [
        "detections", "student_gt", "bounds",
        "review_yesterday", "review_today",
    ]
    report = (out_dir / "report_autogen.md").read_text()
    assert "buffer-stratified" in report
