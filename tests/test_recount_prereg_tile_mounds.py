#!/usr/bin/env python3
"""
Tier-1 tests for ``scripts/recount_prereg_tile_mounds.py`` (E87 remediation 2).

The corrected counts are quoted in erratum E87 and in
``reports/null-exemplar-errata-2026-09-13.md``, so they are pinned here: a
change to the reference layer or to a tile's affine metadata must fail a test
rather than silently falsify published prose.

The heaviest thing these tests read is the 569-feature reference GeoJSON and
four small per-sheet affine metadata files, all well under a second, so the
module is tier-1 per ``tests/README.md``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import recount_prereg_tile_mounds as recount  # noqa: E402

pytestmark = pytest.mark.tier1

REPO_ROOT = Path(__file__).resolve().parent.parent
JSON_OUT = REPO_ROOT / f"{recount.OUT_STEM}.json"
MD_OUT = REPO_ROOT / f"{recount.OUT_STEM}.md"


@pytest.fixture(scope="module")
def payload() -> dict:
    """Build the recomputation once for the whole module."""
    return recount.build_payload(REPO_ROOT)


# ---------------------------------------------------------------------------
# Parsing the lodged tables
# ---------------------------------------------------------------------------


def test_published_counts_parse_to_the_registered_set_sizes() -> None:
    """Sections 2.3 and 2.4 yield exactly 20 and 60 per-tile rows."""
    published = recount.parse_published_counts(REPO_ROOT)
    assert len(published["calibration"]) == 20
    assert len(published["holdout"]) == 60


def test_published_totals_are_the_lodged_summaries() -> None:
    """The parsed rows sum to the "36 mounds" and "79 mounds" summary lines."""
    published = recount.parse_published_counts(REPO_ROOT)
    assert sum(published["calibration"].values()) == 36
    assert sum(published["holdout"].values()) == 79


def test_published_tile_ids_match_the_committed_manifests() -> None:
    """The lodged tables name exactly the tiles the manifests hold."""
    published = recount.parse_published_counts(REPO_ROOT)
    for label, manifest_path, _ in recount.SETS:
        tiles = set(json.loads(
            (REPO_ROOT / manifest_path).read_text(encoding="utf-8")))
        assert set(published[label]) == tiles


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------


def test_reference_layer_holds_569_symbols(payload: dict) -> None:
    """The design-time reference is the 569-symbol layer E87 counts against."""
    assert payload["reference_total"] == 569


def test_cores_partition_the_reference_layer(payload: dict) -> None:
    """The 448 px cores account for every reference exactly once.

    This is the check that validates the affine window arithmetic: cores tile
    each sheet without overlap, so any y-axis inversion or off-by-a-stride
    would break the identity. :func:`build_payload` asserts it internally and
    exits on failure; this test records what the assertion means.
    """
    assert "569 of 569 references exactly once" in \
        payload["geometry_self_check"]


def test_core_window_is_smaller_than_the_tile_window() -> None:
    """A 448 px core sits inside its 512 px tile, anchored at the same corner."""
    affines = recount.load_tile_affines(REPO_ROOT)
    tile = "K-35-078-1_Lesovo_x2240_y2688.png"
    left_t, right_t, lower_t, upper_t = recount.affine_window(
        tile, affines, recount.TILE_PX)
    left_c, right_c, lower_c, upper_c = recount.affine_window(
        tile, affines, recount.CORE_PX)
    assert left_c == left_t
    assert upper_c == upper_t
    assert right_c < right_t
    assert lower_c > lower_t


# ---------------------------------------------------------------------------
# The corrected counts E87 publishes
# ---------------------------------------------------------------------------


def test_calibration_corrected_totals(payload: dict) -> None:
    """The 20 calibration windows hold 50 distinct references, not 36."""
    totals = payload["sets"]["calibration"]["totals"]
    assert totals["published"] == 36
    assert totals["affine_512px_union"] == 50
    assert totals["affine_512px_sum"] == 52
    assert totals["affine_448px_core_union"] == 39


def test_holdout_corrected_totals(payload: dict) -> None:
    """The 60 holdout windows hold 97 distinct references, not 79."""
    totals = payload["sets"]["holdout"]["totals"]
    assert totals["published"] == 79
    assert totals["affine_512px_union"] == 97
    assert totals["affine_512px_sum"] == 106
    assert totals["affine_448px_core_union"] == 82


def test_the_overlap_band_is_why_sum_exceeds_union(payload: dict) -> None:
    """A sum over overlapping 512 px windows double-counts; cores do not."""
    for label in ("calibration", "holdout"):
        totals = payload["sets"][label]["totals"]
        assert totals["affine_512px_sum"] > totals["affine_512px_union"]
        assert totals["affine_448px_core_sum"] == \
            totals["affine_448px_core_union"]


# ---------------------------------------------------------------------------
# The mechanism
# ---------------------------------------------------------------------------


def test_the_approximation_reproduces_the_published_counts_best(
    payload: dict,
) -> None:
    """45 of 80 published rows reproduce under the approximation, 31 under the affine.

    This asymmetry is the evidence that the bounding-box approximation, not the
    raster affine, wrote the lodged tables.
    """
    agree_approx = sum(
        d["exact_row_agreement_with_published"]["approximation"]
        for d in payload["sets"].values()
    )
    agree_affine = sum(
        d["exact_row_agreement_with_published"]["affine_512px"]
        for d in payload["sets"].values()
    )
    assert agree_approx == 45
    assert agree_affine == 31
    assert agree_approx > agree_affine


def test_per_set_row_agreement(payload: dict) -> None:
    """The per-set split of the 45/31 agreement figures."""
    cal = payload["sets"]["calibration"]["exact_row_agreement_with_published"]
    hold = payload["sets"]["holdout"]["exact_row_agreement_with_published"]
    assert (cal["approximation"], cal["affine_512px"]) == (10, 7)
    assert (hold["approximation"], hold["affine_512px"]) == (35, 24)


# ---------------------------------------------------------------------------
# The committed outputs
# ---------------------------------------------------------------------------


def test_committed_outputs_exist() -> None:
    """Both the machine-readable and the human-readable table are committed."""
    assert JSON_OUT.is_file()
    assert MD_OUT.is_file()


def test_committed_json_matches_a_fresh_computation(payload: dict) -> None:
    """The committed JSON has not drifted from the inputs it was built from."""
    assert json.loads(JSON_OUT.read_text(encoding="utf-8")) == payload


def test_committed_markdown_matches_a_fresh_render(payload: dict) -> None:
    """The committed table is exactly what the generator renders today."""
    assert MD_OUT.read_text(encoding="utf-8") == recount.render_markdown(payload)


def test_markdown_is_labelled_a_post_hoc_correction() -> None:
    """The table must not read as a replacement for the lodged text."""
    text = MD_OUT.read_text(encoding="utf-8")
    assert "POST-HOC CORRECTION" in text
    assert "immutable" in text
    assert "E87" in text


def test_check_mode_passes_against_the_committed_outputs() -> None:
    """The documented drift guard is green on the committed tree."""
    assert recount.main(["--check", "--root", str(REPO_ROOT)]) == 0
