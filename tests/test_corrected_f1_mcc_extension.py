"""
Tests for the additive ``--compute-mcc`` extension to
``compute_corrected_f1_multi_buffer`` (Session 105, Track-2 canonical-GT scoring).

Tier 1 unit tests covering two guarantees:

1. **Additivity** — with MCC off, the F1 path and serialised output are
   byte-identical to the legacy behaviour (no ``tile_classification`` block, no
   MCC columns). With MCC on, the F1 counts are unchanged and an MCC block is
   appended.
2. **Correct wiring** — ``compute_at_buffer(..., compute_mcc=True)`` computes the
   tile MCC against the SAME per-buffer gated extended GT used for the corrected
   F1, matching a direct ``calculate_tile_classification`` call.
"""

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, box

from scripts.compute_corrected_f1_multi_buffer import (
    BufferResult,
    _result_to_dict,
    build_extended_gt,
    build_phantom_gdf,
    compute_at_buffer,
    write_csv,
)
from scripts.lib_advanced_metrics import calculate_tile_classification

CRS = "EPSG:32635"
ORIGIN_X, ORIGIN_Y, TILE = 500_000.0, 4_700_000.0, 100.0


def _review(rows: list[dict]) -> pd.DataFrame:
    """Minimal review DataFrame with the columns the gating helper needs."""
    cols = ["candidate_id", "human_label", "buffer_metres", "x", "y", "map_name"]
    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows, columns=cols)


def _scene() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Deterministic two-tile scene.

    Tile A ("K-1_x0_y0") holds one student mound AND one detection (→ a TP tile
    and a Hungarian TP); tile B ("K-1_x100_y0") is empty with no detection (→ a
    TN tile). With empty reviews the extended GT equals the student GT, so MCC
    is 1.0 (tp=1, tn=1, fp=0, fn=0) and corrected F1 is 1.0.
    """
    bounds = gpd.GeoDataFrame(
        {"tile_name": ["K-1_x0_y0", "K-1_x100_y0"]},
        geometry=[
            box(ORIGIN_X, ORIGIN_Y, ORIGIN_X + TILE, ORIGIN_Y + TILE),
            box(ORIGIN_X + TILE, ORIGIN_Y, ORIGIN_X + 2 * TILE, ORIGIN_Y + TILE),
        ],
        crs=CRS,
    )
    centre_a = (ORIGIN_X + TILE / 2, ORIGIN_Y + TILE / 2)
    student = gpd.GeoDataFrame(
        {"source_map": ["K-1"]}, geometry=[Point(*centre_a)], crs=CRS,
    )
    det = gpd.GeoDataFrame(
        {"source_tile": ["K-1_x0_y0"]}, geometry=[Point(*centre_a)], crs=CRS,
    )
    return det, student, bounds


# --------------------------------------------------------------------------- #
# Serialisation additivity (fast — no geodata)
# --------------------------------------------------------------------------- #

def _f1_only_result() -> BufferResult:
    return BufferResult(
        buffer_metres=50, tp=1, fp=1, fn=1, n_ref_student_only=1,
        n_reviewer_promoted=0, n_ref_extended=1,
        precision=0.5, precision_ci=(0.4, 0.6),
        recall=0.5, recall_ci=(0.4, 0.6), f1=0.5, f1_ci=(0.4, 0.6),
    )


@pytest.mark.tier1
def test_result_dict_omits_mcc_block_when_absent():
    """Legacy F1-only result must not gain a tile_classification block."""
    assert "tile_classification" not in _result_to_dict(_f1_only_result())


@pytest.mark.tier1
def test_result_dict_includes_mcc_block_when_present():
    """An MCC-populated result serialises the block with the expected value."""
    r = BufferResult(
        buffer_metres=50, tp=1, fp=1, fn=1, n_ref_student_only=1,
        n_reviewer_promoted=0, n_ref_extended=1,
        precision=0.5, precision_ci=(0.4, 0.6),
        recall=0.5, recall_ci=(0.4, 0.6), f1=0.5, f1_ci=(0.4, 0.6),
        mcc=0.71, mcc_ci=(0.6, 0.8), tile_tp=10, tile_tn=20,
        tile_fp=2, tile_fn=3, sensitivity=0.77, specificity=0.9,
    )
    block = _result_to_dict(r)["tile_classification"]
    assert block["mcc"] == 0.71
    assert block["tp"] == 10 and block["tn"] == 20
    assert block["mcc_CI"] == [0.6, 0.8]


@pytest.mark.tier1
def test_write_csv_omits_mcc_columns_when_absent(tmp_path):
    """F1-only CSV must not carry MCC columns (byte-identical legacy schema)."""
    out = tmp_path / "f1.csv"
    write_csv([_f1_only_result()], out)
    header = out.read_text().splitlines()[0]
    assert "MCC" not in header and "tile_TP" not in header


@pytest.mark.tier1
def test_write_csv_includes_mcc_columns_when_present(tmp_path):
    """An MCC run appends the MCC columns."""
    r = _f1_only_result()
    r_mcc = BufferResult(
        **{**{k: getattr(r, k) for k in (
            "buffer_metres", "tp", "fp", "fn", "n_ref_student_only",
            "n_reviewer_promoted", "n_ref_extended", "precision",
            "precision_ci", "recall", "recall_ci", "f1", "f1_ci")},
           "mcc": 0.7, "mcc_ci": (0.6, 0.8), "tile_tp": 1, "tile_tn": 1,
           "tile_fp": 0, "tile_fn": 0, "sensitivity": 1.0, "specificity": 1.0},
    )
    out = tmp_path / "mcc.csv"
    write_csv([r_mcc], out)
    header = out.read_text().splitlines()[0]
    assert "MCC" in header and "tile_TP" in header


# --------------------------------------------------------------------------- #
# compute_at_buffer wiring (synthetic geodata)
# --------------------------------------------------------------------------- #

@pytest.mark.tier1
def test_compute_at_buffer_mcc_matches_direct_call():
    """MCC from compute_at_buffer equals a direct calculate_tile_classification
    on the same gated extended GT — and the clean scene gives MCC = 1.0."""
    det, student, bounds = _scene()
    empty = _review([])
    res = compute_at_buffer(
        gdf_det=det, gdf_student=student, gdf_bounds=bounds,
        review_yesterday=empty, review_today=empty, buffer_r=50,
        n_bootstrap=50, seed=42, compute_mcc=True,
    )
    # Reconstruct the same gated extended GT and classify directly.
    phantoms = build_phantom_gdf(empty, empty, 50, crs=str(det.crs))
    ext_gt = build_extended_gt(student, phantoms)
    direct = calculate_tile_classification(det, ext_gt, bounds)

    assert res.mcc == pytest.approx(direct["mcc"])
    assert res.mcc == pytest.approx(1.0)
    assert (res.tile_tp, res.tile_tn, res.tile_fp, res.tile_fn) == (1, 1, 0, 0)


@pytest.mark.tier1
def test_mcc_flag_is_purely_additive():
    """Toggling compute_mcc must not change the F1 counts; off ⇒ MCC None."""
    det, student, bounds = _scene()
    empty = _review([])
    common = dict(
        gdf_det=det, gdf_student=student, gdf_bounds=bounds,
        review_yesterday=empty, review_today=empty, buffer_r=50,
        n_bootstrap=50, seed=42,
    )
    off = compute_at_buffer(**common, compute_mcc=False)
    on = compute_at_buffer(**common, compute_mcc=True)

    assert off.mcc is None and off.tile_tp is None
    assert on.mcc is not None
    # F1 path identical regardless of the MCC flag.
    assert (off.tp, off.fp, off.fn, off.f1) == (on.tp, on.fp, on.fn, on.f1)
    assert off.f1 == pytest.approx(1.0)
