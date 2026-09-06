"""Tier-1 tests for the r2 recompute chain's hardenings H1-H3.

These cover the code landed in Session 149 when the clean-context audit
(`reports/r2-chain-pre-run-audit-2026-09-06.md`) was adjudicated. Each test
names the finding it guards, because the value of these tests is that they
fail if a future refactor quietly reopens one of them:

* **H1 / MAJOR 5** — r2 enters the chain as ONE merged file, gated on its own
  census and on the 5 m channel-duplicate invariant.
* **H2 / MAJOR 6** — an r2 run cannot write into the r1 homes that the G3
  regression gate reads.
* **H3 / MAJOR 9** — r2 resolves to a reference term everywhere, and an
  unknown vintage raises instead of degrading to "unresolved".
* **BLOCKER 4** — the regression gates stay pinned to r1 during an r2 build.
"""

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
from scipy.spatial import cKDTree
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import build_55map_leaderboard as bl  # noqa: E402
from scripts import lib_uplift_supplement as lus  # noqa: E402
from scripts import register_standardised_gt_conditions as reg  # noqa: E402
from scripts.final_board_build import REF_DIR_BY_VINTAGE, retarget  # noqa: E402
from scripts.materialise_best_available_gt import (  # noqa: E402
    DEDUP_TOLERANCE_M,
    _assert_no_channel_duplicates,
)

ROOT = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------- H1 / M5 ---

@pytest.mark.tier1
def test_r2_reference_loads_and_matches_its_published_census():
    """H1: r2 enters through one gated loader, not by a bare read_file."""
    gdf = bl.r2_gt()
    assert len(gdf) == bl.R2_EXPECTED_N == 5018
    assert gdf["layer"].value_counts().to_dict() == bl.R2_EXPECTED_LAYERS
    assert gdf.crs.to_epsg() == 32635
    # The census must be the sum of its parts — a layer table that does not
    # add up means the merge dropped or duplicated records.
    assert sum(bl.R2_EXPECTED_LAYERS.values()) == bl.R2_EXPECTED_N


@pytest.mark.tier1
def test_r2_reference_has_no_channel_duplicates():
    """H1: the invariant build_extended_gt would have enforced holds on r2."""
    gdf = bl.r2_gt()
    xy = np.c_[gdf.geometry.x, gdf.geometry.y]
    dist, _ = cKDTree(xy).query(xy, k=2)
    assert dist[:, 1].min() > DEDUP_TOLERANCE_M


@pytest.mark.tier1
def test_dedup_gate_catches_a_planted_duplicate():
    """The 16th finding: apply_audit_revision had NO spatial dedup at all.

    A gate that never fires is indistinguishable from a missing gate, so plant
    a duplicate and prove it is caught.
    """
    pts = [Point(0, 0), Point(1000, 0), Point(1000 + DEDUP_TOLERANCE_M / 2, 0)]
    gdf = gpd.GeoDataFrame(
        {"gt_id": ["a", "b", "c"]}, geometry=pts, crs="EPSG:32635")
    with pytest.raises(RuntimeError, match="channel duplicates"):
        _assert_no_channel_duplicates(gdf)


# ------------------------------------------------------- H2 / M6 / BLOCKER 4 ---

@pytest.mark.tier1
def test_board_homes_are_distinct_per_vintage():
    """H2: r2 artefacts land in their own home; r1 is never the r2 target."""
    r1, r2 = bl.board_home("standardised"), bl.board_home("r2")
    assert r1 != r2
    assert r1.name == "55map-final-board-2026-08-27"
    assert r2.name == "55map-final-board-r2-2026-09-06"


@pytest.mark.tier1
def test_unknown_board_vintage_exits_rather_than_defaulting_to_r1():
    """H2: a typo must not silently resolve to the committed r1 board."""
    with pytest.raises(SystemExit):
        bl.board_home("r3")


@pytest.mark.tier1
def test_register_homes_are_distinct_per_vintage():
    """H2: adapt_one writes inside one vintage's home only."""
    assert reg.vintage_home("standardised") != reg.vintage_home("r2")
    assert reg.vintage_home("r2").name == "55maps-r2-ref-2026-09-06"


@pytest.mark.tier1
def test_regression_gate_reference_is_not_the_r2_reference():
    """BLOCKER 4: standardised_gt() stays r1 so G3/G4 stay live under r2.

    The gates call ``standardised_gt`` directly and the board build calls
    ``reference_gt``; if a refactor ever collapsed the two, the regression
    gate would compare r2 numbers to the r1 board and be switched off by its
    own failure.
    """
    assert len(bl.standardised_gt()) != len(bl.r2_gt())
    assert len(bl.reference_gt("r2")) == bl.R2_EXPECTED_N
    assert len(bl.reference_gt("standardised")) == len(bl.standardised_gt())


@pytest.mark.tier1
def test_retarget_moves_scoring_homes_but_not_detection_sources():
    """BLOCKER 1: carried cells must move to r2 with everything else."""
    ev = "results/55maps-standardised-ref-2026-08-14/TH7-k4/evaluation.json"
    assert retarget(ev, "r2").startswith(REF_DIR_BY_VINTAGE["r2"])
    assert retarget(ev, "standardised") == ev
    # Detections do not change between references — only the scoring of them.
    det = "outputs/55maps-text-high-generalisation/verified/verified_detections.geojson"
    assert retarget(det, "r2") == det


# --------------------------------------------------------------- H3 / M9 ---

@pytest.mark.tier1
def test_r2_names_mirror_the_canonical_board_cells():
    """H3: the r2 board resolves the same cells through -r2-gt rows."""
    assert len(bl.NAMES_R2) == len(bl.NAMES)
    assert all(label.endswith("-r2-gt") for _run, label in bl.NAMES_R2)
    assert set(bl.NAMES_R2.values()) == set(bl.NAMES.values())


@pytest.mark.tier1
def test_registration_labels_carry_the_r2_suffix():
    """H3: step 7a writes -r2-gt rows, which the board later resolves by."""
    for cell in reg.REGISTRATIONS:
        _run, src, new = reg.registration_for(cell, "r2")
        assert src.endswith("-canonical-gt")
        assert new.endswith("-r2-gt")
        # Every vintage clones the SAME canonical base, never the previous
        # vintage, so a defect cannot propagate down the chain.
        assert reg.registration_for(cell, "standardised")[1] == src


@pytest.mark.tier1
def test_uplift_supplement_resolves_r2_by_filename_and_by_label():
    """MAJOR 9: both resolution routes must know r2."""
    assert lus.REFERENCE_BY_FILENAME["best-available-gt-55maps-r2.geojson"] == "r2"
    assert lus.REFERENCE_PATH["r2"].endswith("best-available-gt-55maps-r2.geojson")


@pytest.mark.tier1
def test_uplift_supplement_r2_mound_count_matches_the_committed_file():
    """MAJOR 9: REFERENCE_N_MOUNDS is a literal and can drift from the file."""
    n = len(gpd.read_file(ROOT / lus.REFERENCE_PATH["r2"]))
    assert lus.REFERENCE_N_MOUNDS["r2"] == n == 5018


@pytest.mark.tier1
def test_r2_label_suffix_resolves_when_the_evaluation_metadata_is_absent():
    """MAJOR 9: the label-suffix fallback is the route the register rows take."""
    res = lus.resolve_reference(None, "verified-k4-r2-gt", None)
    assert res.term == "r2"
    assert res.basis == "label-suffix"
    assert res.path.endswith("best-available-gt-55maps-r2.geojson")


@pytest.mark.tier1
def test_r2_evaluation_metadata_resolves_by_filename():
    """MAJOR 9: the authoritative route — what the evaluation actually read."""
    meta = {"input_files": {"ground_truth": lus.REFERENCE_PATH["r2"]}}
    res = lus.resolve_reference(meta, "anything", None)
    assert res.term == "r2"
    assert res.basis == "eval-ground-truth"


@pytest.mark.tier1
def test_unknown_reference_vintage_raises_instead_of_resolving_unresolved():
    """MAJOR 9: a silent 'unresolved' drops the run from the reference column.

    An unrecognised member of the best-available family is a vintage nobody
    taught this module about — exactly the case that must be loud.
    """
    meta = {"input_files": {
        "ground_truth": "inputs/vectors/references/best-available-gt-55maps-r3.geojson"}}
    with pytest.raises(ValueError, match="unrecognised reference vintage"):
        lus.resolve_reference(meta, "verified-k4-r3-gt", None)


@pytest.mark.tier1
def test_a_reference_outside_the_family_still_resolves_unresolved():
    """The raise must be narrow: only the best-available family is gated."""
    meta = {"input_files": {"ground_truth": "inputs/vectors/references/something-else.geojson"}}
    res = lus.resolve_reference(meta, "some-label", None)
    assert res.basis == "unresolved"
