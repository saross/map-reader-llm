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


# ------------------------------------------------ Session 149 (Fable) ---
# Pass pins (MINOR 14), the build's r2 tolerances, the MCC board's engine
# shape, and the single r2 registrar.

import json  # noqa: E402

from scripts import final_board_build as fbb  # noqa: E402
from scripts import final_board_sweeps as fbs  # noqa: E402
from scripts import pin_pass_provenance as pin  # noqa: E402
from scripts import register_r2_conditions as r2reg  # noqa: E402
from scripts.mcc_tiering_55map import _load_cell_inputs  # noqa: E402


def _fake_cell(tmp_path: Path, k: int = 2) -> Path:
    """A minimal pass tree: run_1..run_k each with one detections file + meta."""
    cell = tmp_path / "cell"
    for i in range(1, k + 1):
        d = cell / f"run_{i}"
        d.mkdir(parents=True)
        (d / "detections-x.geojson").write_text(json.dumps(
            {"type": "FeatureCollection", "features": [], "run": i}))
        (d / "detections-x.meta.json").write_text(json.dumps(
            {"run_id": f"id-{i}", "timestamp": {"start": f"2026-01-0{i}T00:00", "end": ""}}))
    return cell


def _spec(cell: Path, tmp_path: Path, k: int = 2) -> dict:
    return {"cell_dir": cell, "k": k, "pin": tmp_path / "pin.json"}


@pytest.mark.tier1
def test_pass_pin_round_trips_and_gates(tmp_path, monkeypatch):
    """MINOR 14: a matching tree passes; a swapped, edited or extra pass fails."""
    monkeypatch.setattr(pin, "PROJECT_ROOT", tmp_path)
    cell = _fake_cell(tmp_path)
    spec = _spec(cell, tmp_path)
    p = pin.build_pin("t", spec)
    assert [e["run_id"] for e in p["passes"]] == ["id-1", "id-2"]
    assert p["start_times_monotone"] is True
    spec["pin"].write_text(json.dumps(p))
    pin.verify_pin("t", spec)  # matches

    # Swap the two passes' contents: union unchanged, rungs would differ.
    a, b = cell / "run_1/detections-x.geojson", cell / "run_2/detections-x.geojson"
    ta, tb = a.read_text(), b.read_text()
    a.write_text(tb)
    b.write_text(ta)
    with pytest.raises(pin.PassPinError, match="sha256"):
        pin.verify_pin("t", spec)
    a.write_text(ta)
    b.write_text(tb)

    # A stray pass beyond K is flagged even though the loaders ignore it.
    (cell / "run_3").mkdir()
    (cell / "run_3/detections-x.geojson").write_text("{}")
    with pytest.raises(pin.PassPinError, match="beyond K"):
        pin.verify_pin("t", spec)


@pytest.mark.tier1
def test_pass_pin_missing_is_a_hard_stop(tmp_path, monkeypatch):
    """Deriving a rung without a committed pin must refuse, not proceed."""
    monkeypatch.setattr(pin, "PROJECT_ROOT", tmp_path)
    cell = _fake_cell(tmp_path)
    with pytest.raises(pin.PassPinError, match="no pass pin"):
        pin.verify_pin("t", _spec(cell, tmp_path))


@pytest.mark.tier1
def test_committed_pins_match_the_tree():
    """The three committed pins verify against the current pass trees."""
    for tag, spec in pin.PINNED_CELLS.items():
        if not spec["cell_dir"].exists():
            pytest.skip(f"{tag}: pass tree not on this machine")
        pin.verify_pin(tag, spec, check_hashes=False)


@pytest.mark.tier1
def test_build_tolerates_unaudited_3_7_costs():
    """family_of must not KeyError on a 3.7 label; cost renders as a dash."""
    assert fbb.family_of("ARM1-N3-oracle") == "ARM1-N3"
    assert fbb.cost_of("FOURTH-N10-carried") is None
    assert fbb.fmt_cost(None) == "—"
    assert fbb.fmt_cost(97.22) == "$97"


@pytest.mark.tier1
def test_coincident_points_are_the_committed_identity_points():
    """The coincidence gate's r1 points must be the sweep's identity points."""
    for cell, fam in (("TH7-oracle", "TH7"), ("IM-oracle", "IM"), ("UPL-oracle", "UPL")):
        assert fbb.COINCIDENT_POINTS[cell] == fbs.IDENTITY[fam][0]
    assert r2reg.COINCIDENT_POINTS == fbb.COINCIDENT_POINTS


@pytest.mark.tier1
def test_g37_identity_counts_match_the_committed_primaries():
    """The 3.7 identity gates are the committed primaries' own feature counts."""
    for label, det, _f1 in fbs.G37_COMMITTED:
        fam = label.removesuffix("-carried")
        n = len(json.loads((ROOT / det).read_text())["features"])
        assert n == fbs.G37_IDENTITY[fam][1], (fam, n)


@pytest.mark.tier1
def test_mcc_board_reads_the_engine_evaluation_shape(tmp_path):
    """r2 cells carry evaluate_detections' nested tile block, not summary.json."""
    cell = tmp_path / "X-k4"
    cell.mkdir()
    det = tmp_path / "det.geojson"
    gpd.GeoDataFrame({"a": [1]}, geometry=[Point(25.0, 42.0)], crs="EPSG:4326").to_file(
        det, driver="GeoJSON")
    ev = {"_metadata": {"input_files": {"detections": [str(det.relative_to(tmp_path))]}},
          "summary": {"tile_classification": {
              "confusion": {"tp": 1, "tn": 2, "fp": 3, "fn": 4},
              "mcc": {"point": 0.5, "ci_lower": 0.4, "ci_upper": 0.6},
              "sensitivity": {"point": 0.2}, "specificity": {"point": 0.9}}}}
    (cell / "evaluation.json").write_text(json.dumps(ev))
    import scripts.mcc_tiering_55map as m
    old = m.BASE_DIR
    m.BASE_DIR = tmp_path
    try:
        gdf, tile = _load_cell_inputs(cell)
    finally:
        m.BASE_DIR = old
    assert len(gdf) == 1 and gdf.crs.to_epsg() == 32635
    assert tile == {"tp": 1, "tn": 2, "fp": 3, "fn": 4, "mcc": 0.5,
                    "mcc_CI": [0.4, 0.6], "sensitivity": 0.2, "specificity": 0.9}


@pytest.mark.tier1
def test_r2_registrar_clones_scoring_rows_and_retargets_eval_paths():
    """7a-i: every r1 scoring-home row gains an -r2-gt twin in the r2 home."""
    dec = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]
    plan = r2reg.clone_scoring_rows(dec)
    assert plan, "no scoring-home rows found to clone"
    for run_id, row, status in plan:
        assert row["label"].endswith("-r2-gt")
        assert row["eval_path"].startswith(r2reg.R2_SCORING)
        assert status in ("add", "skip")
        src = next(c for c in dec[run_id]["conditions"]
                   if c["label"] == row["label"].replace("-r2-gt", "-standardised-gt"))
        assert row["detections"] == src["detections"]  # detections never move
    assert {Path(r["eval_path"]).parent.name for _, r, _ in plan} >= {
        "IM-k4", "TH7-k4", "T03-k4", "TM-k4", "TM-n10-k5"}


@pytest.mark.tier1
def test_r2_registrar_authors_every_board_family_and_skips_coincidence():
    """7a-ii: stride, incumbent, 3.7-arm and fourth-cell schemes; coincidence skipped."""
    dec = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]

    def cell(label, point, basis="oracle (r2-reference argmax)"):
        return {"label": label, "det": f"x/cells/{label}/detections.geojson",
                "basis": basis, "point": point, "committed_eval": False}

    manifest = [cell("B-N1-oracle", "(0.20, k1)"), cell("A-N3-carried", "(0.15, k3)", "carried (post-hoc)"),
                cell("TH7-oracle", "(0.15, k3)"), cell("T03-oracle", "(0.20, k3)"),
                cell("ARM2-N3-oracle", "(0.95, k3)"), cell("FOURTH-N10-carried", "(0.98, k10)", "carried"),
                {"label": "TH7-k4", "det": "d", "basis": "carried", "point": "(0.15, k4)", "committed_eval": True}]
    plan = author_board_rows = r2reg.author_board_rows(dec, manifest, None)
    by = {row["label"]: (run, status) for run, row, status in plan}
    assert by["TH7-oracle"] == (None, "coincident")  # argmax on the committed set
    assert by["g384-ov192-55map-n1-oracle-p0.20-k1-r2-gt"] == ("stride-55map-2026-08-25", "add")
    assert by["g384-ov128-55map-n3-carried-posthoc-p0.15-k3-r2-gt"][1] == "add"
    assert by["verified-oracle-p0.20-k3-r2-gt"] == ("55maps-text-high-t0-3-generalisation", "add")
    assert by["arm2-n3-oracle-p0.95-k3-r2-gt"] == ("gemini37-55map-2026-08-29", "add")
    assert by["g384-ov192-55map-n10-verified37-carried-p0.98-k10-r2-gt"][1] == "add"
    assert "TH7-k4" not in {r["label"] for _, r, _ in plan}  # committed_eval: cloned in 7a-i
    arm = next(r for _, r, _ in plan if r["label"].startswith("arm2-"))
    assert arm["verifier_config"]["model"].startswith("gemini-3.7"), arm["verifier_config"]
    assert author_board_rows is plan


# ------------------------------------------ audit-2 fixes (S149-b) ---
# r1 homes refused at tool level (MAJOR 4/5), and the scoring driver
# (MAJOR 7): its derived cell set, its recipe, and its refusal to run
# without the r2 board manifest.

from scripts import r2_score_cells as drv  # noqa: E402


@pytest.mark.tier1
def test_every_r1_writing_tool_refuses_without_force_r1():
    """H15: default invocations must not touch a committed r1 artefact."""
    import scripts.final_board_n3_carried as n3
    import scripts.mcc_tiering_55map as mcc
    import scripts.register_standardised_gt_conditions as reg
    with pytest.raises(SystemExit, match="read-only"):
        n3.main("standardised")
    with pytest.raises(SystemExit, match="regression-gate target"):
        bl.main(reference="standardised")
    with pytest.raises(SystemExit, match="committed r1 board"):
        mcc.main(reference="standardised")
    with pytest.raises(SystemExit, match="Refusing"):
        reg.main("standardised")
    with pytest.raises(SystemExit, match="read-only"):
        fbb.main("standardised")


@pytest.mark.tier1
def test_driver_derives_the_contract_s_nine_fixed_cells():
    """Step 3's set is NAMES ∪ COMMITTED_CARRIED and every input exists."""
    jobs = drv.fixed_jobs()
    assert {j.label for j in jobs} == drv.CONTRACT_FIXED
    assert len(jobs) == 9
    for j in jobs:
        assert j.detections.exists(), j.label
        assert j.out_dir.parent == drv.SCORING_HOME
        assert j.eval_label.endswith("-r2-gt")


@pytest.mark.tier1
def test_driver_command_is_the_im_k4_recipe_against_r2():
    """The engine invocation must match the committed template exactly."""
    job = drv.fixed_jobs()[0]
    cmd = drv.engine_command(job, workers=2, require_clean=True)
    s = " ".join(cmd)
    assert "--buffers 5 10 15 20 25 30 35 40 45 50 75 100 125 150" in s
    assert "--bootstrap 10000" in s and "--seed 42" in s and "--mcc" in s
    assert "best-available-gt-55maps-r2.geojson" in s
    assert "55maps_evaluation_bounds.geojson" in s
    assert "--require-clean-inputs" in s
    assert "--require-clean-inputs" not in " ".join(
        drv.engine_command(job, workers=2, require_clean=False))


@pytest.mark.tier1
def test_driver_board_stage_refuses_without_the_r2_manifest(monkeypatch, tmp_path):
    """4b cannot run before 4a/4c have written the r2 board manifest."""
    monkeypatch.setattr(drv, "BOARD_HOME", tmp_path / "no-such-board")
    with pytest.raises(SystemExit, match="does not exist"):
        drv.board_jobs()
