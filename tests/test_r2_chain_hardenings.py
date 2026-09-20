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
    # "add" before 7a-ii ran, "skip" once the rows are in the register: both
    # are the idempotent plan; the run assignment is what the test pins.
    ok = {"add", "skip"}
    assert by["g384-ov192-55map-n1-oracle-p0.20-k1-r2-gt"][0] == "stride-55map-2026-08-25"
    assert by["g384-ov128-55map-n3-carried-posthoc-p0.15-k3-r2-gt"][1] in ok
    assert by["verified-oracle-p0.20-k3-r2-gt"][0] == "55maps-text-high-t0-3-generalisation"
    assert by["arm2-n3-oracle-p0.95-k3-r2-gt"][0] == "gemini37-55map-2026-08-29"
    assert by["g384-ov192-55map-n10-verified37-carried-p0.98-k10-r2-gt"][1] in ok
    assert all(s in ok | {"coincident"} for _r, _row, s in plan)
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


# ------------------------------------------------ Session 150 (Fable) ---
# The corrected-F1 engine records its BASE layer (the student file) as
# ``ground_truth``; the reference it scored against is canonical. Ruling 2's
# re-adaptation (0ac49a736) attached that metadata to the stride canonical
# rows and they fell out of the ``canonical`` stratum into ``student``.


@pytest.mark.tier1
def test_student_base_layer_under_a_canonical_label_resolves_canonical():
    """A ``-canonical-gt`` row scored by the corrected-F1 engine stays canonical."""
    meta = {"input_files": {
        "ground_truth": "inputs/vectors/references/student-mounds-55maps-reviewed.geojson",
        "review_today": "results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv",
    }}
    res = lus.resolve_reference(meta, "g384-ov128-55map-verified-carried-p0.15-k8-canonical-gt", None)
    assert (res.term, res.basis) == ("canonical", "label-suffix")
    assert res.path.endswith("canonical-gt-55maps-r50.geojson")
    assert res.consumed_path.endswith("student-mounds-55maps-reviewed.geojson")


@pytest.mark.tier1
def test_student_base_layer_without_a_suffix_still_resolves_student():
    """The exception is narrow: no explicit suffix, the filename rule stands."""
    meta = {"input_files": {
        "ground_truth": "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"}}
    res = lus.resolve_reference(meta, "verified-k4", None)
    assert (res.term, res.basis) == ("student", "eval-ground-truth")


@pytest.mark.tier1
def test_a_real_reference_file_still_outranks_the_label_suffix():
    """Rule 1 keeps its authority when the file names a reference, not a base layer."""
    meta = {"input_files": {"ground_truth": lus.REFERENCE_PATH["r2"]}}
    res = lus.resolve_reference(meta, "verified-k4-canonical-gt", None)
    assert (res.term, res.basis) == ("r2", "eval-ground-truth")


# ---------------------------- D6: the carried-analogue addendum (r2) ---
# PI decision D6 (planning/pi-decisions-2026-09-20.md, ruled 2026-09-20):
# (a) register the seven carried-analogue addendum cells of the r2 board;
# hold the ten mcc-oracle cells, because the tile-MCC oracle is being
# redefined as the optimum over prob_t at the family's carried vote count.
# The trigger is reports/comparability-inventory-37-runs-2026-09-20.md
# section 3.2, which found the seven points swept on r2 but never
# materialised, leaving carried-against-carried with no cell below the top
# rung.

#: (run id, label, prob_threshold, vote_threshold, n_passes, board cell).
#: One row per addendum cell, in the inventory's section 3.2 order.
ADDENDUM_ROWS = [
    ("gemini37-55map-2026-08-29", "arm2-n1-carried-posthoc-p0.80-k1-r2-gt",
     0.8, 1, 1, "ARM2-N1-carried"),
    ("gemini37-55map-2026-08-29", "arm2-n3-carried-posthoc-p0.80-k3-r2-gt",
     0.8, 3, 3, "ARM2-N3-carried"),
    ("gemini37-55map-2026-08-29", "arm1-n1-carried-posthoc-p0.10-k1-r2-gt",
     0.1, 1, 1, "ARM1-N1-carried"),
    ("gemini37-55map-2026-08-29", "arm1-n3-carried-posthoc-p0.10-k3-r2-gt",
     0.1, 3, 3, "ARM1-N3-carried"),
    ("stride-55map-2026-08-25",
     "g384-ov192-55map-n1-verified37-carried-posthoc-p0.98-k1-r2-gt",
     0.98, 1, 1, "FOURTH-N1-carried"),
    ("stride-55map-2026-08-25",
     "g384-ov192-55map-n3-verified37-carried-posthoc-p0.98-k3-r2-gt",
     0.98, 3, 3, "FOURTH-N3-carried"),
    ("stride-55map-2026-08-25",
     "g384-ov192-55map-n5-verified37-carried-posthoc-p0.98-k5-r2-gt",
     0.98, 5, 5, "FOURTH-N5-carried"),
]

R2_BOARD_REL = "results/55map-final-board-r2-2026-09-06"


@pytest.mark.tier1
def test_the_seven_carried_analogue_cells_are_registered():
    """D6(a): all seven rows are present, in the right run, at the right point."""
    dec = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]
    for run_id, label, prob, votes, n_passes, cell in ADDENDUM_ROWS:
        rows = [c for c in dec[run_id]["conditions"] if c.get("label") == label]
        assert len(rows) == 1, f"{run_id}::{label}: expected exactly one row, got {len(rows)}"
        row = rows[0]
        assert row["prob_threshold"] == prob
        assert row["vote_threshold"] == votes
        assert row["n_passes"] == n_passes
        assert row["architecture"] == "proposer-verifier"
        assert row["aggregation"] == "verified"
        assert row["eval_path"] == f"{R2_BOARD_REL}/cells/{cell}/evaluation.json"
        assert row["detections"] == f"{R2_BOARD_REL}/cells/{cell}/detections.geojson"
        assert (ROOT / row["eval_path"]).exists(), row["eval_path"]


@pytest.mark.tier1
def test_the_addendum_notes_carry_their_basis_date_and_trigger():
    """A post-hoc row must say what it is and what asked for it, not just where."""
    dec = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]
    for run_id, label, _prob, _votes, _n, cell in ADDENDUM_ROWS:
        note = next(c for c in dec[run_id]["conditions"]
                    if c.get("label") == label)["_note"]
        assert cell in note
        assert "carried-analogue" in note and "post-hoc" in note
        assert r2reg.ADDENDUM_DATE in note
        assert "comparability-inventory-37-runs-2026-09-20.md" in note
        assert "section 3.2" in note
        # The board was not re-tiered for these, so the note must not claim it.
        assert "tier via final_board_50m.json" not in note


@pytest.mark.tier1
def test_the_addendum_rows_keep_their_runs_candidate_count_convention():
    """n_candidates follows the run, not the rung: 12,715 text, 57,482 fourth."""
    dec = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]
    expected = {"gemini37-55map-2026-08-29": 12715, "stride-55map-2026-08-25": 57482}
    for run_id, label, *_ in ADDENDUM_ROWS:
        row = next(c for c in dec[run_id]["conditions"] if c.get("label") == label)
        assert row["n_candidates"] == expected[run_id], label


@pytest.mark.tier1
def test_the_hold_mechanism_works_though_nothing_is_held_today():
    """A held basis plans as 'held' -- not an add, not a raise, not a drop.

    HELD_BASES emptied with the amended D6c (2026-09-21), which gave every
    cell on this board a home. The mechanism is what must survive: it is how
    the registrar carries "scored, but the PI has not said where this
    belongs" without either raising on the cell or dropping it silently, and
    that situation has now arisen twice in two days. Exercised here with a
    basis no manifest carries, so the test pins the behaviour rather than
    the current ruling.
    """
    dec = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]
    manifest = [{"label": "ARM1-N1-mcc-oracle", "det": "x/d.geojson",
                 "basis": "awaiting-a-ruling (post-hoc)",
                 "point": "(0.20, k1)", "committed_eval": False}]
    monkeyed = r2reg.HELD_BASES
    r2reg.HELD_BASES = ("awaiting-a-ruling",)
    try:
        plan = r2reg.author_board_rows(dec, manifest, None)
        assert [(r, row["label"], s) for r, row, s in plan] == [
            (None, "ARM1-N1-mcc-oracle", "held")]
        # apply() writes only "add" rows, so a held cell cannot reach the file.
        before = {rid: len(run["conditions"]) for rid, run in dec.items()}
        assert r2reg.apply(dec, plan) == 0
        assert {rid: len(run["conditions"]) for rid, run in dec.items()} == before
    finally:
        r2reg.HELD_BASES = monkeyed


@pytest.mark.tier1
def test_an_unknown_board_cell_label_still_raises():
    """The hold must be narrow: only HELD_BASES is exempt from the raise."""
    dec = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]
    manifest = [{"label": "WAT-N1-sideways", "det": "x/d.geojson",
                 "basis": "something new", "point": "(0.20, k1)",
                 "committed_eval": False}]
    with pytest.raises(ValueError, match="unrecognised board cell label"):
        r2reg.author_board_rows(dec, manifest, None)


@pytest.mark.tier1
def test_the_registrar_writes_in_the_registers_own_json_style(tmp_path,
                                                             monkeypatch):
    """780a49ae3's ASCII style must survive a write, or the diff is unreadable."""
    committed = (ROOT / "results/run-conditions.json").read_text()
    assert committed.isascii(), "the committed register is ASCII-escaped"

    doc = {"decomposition": {"r": {"conditions": [{"_note": "an em dash — here"}]}}}
    ascii_file = tmp_path / "ascii.json"
    ascii_file.write_text(json.dumps(doc, indent=1, ensure_ascii=True) + "\n")
    monkeypatch.setattr(r2reg, "RUN_CONDITIONS", ascii_file)
    r2reg.write_register(doc)
    assert ascii_file.read_text().isascii()
    assert ascii_file.read_text().endswith("\n")

    utf8_file = tmp_path / "utf8.json"
    utf8_file.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    monkeypatch.setattr(r2reg, "RUN_CONDITIONS", utf8_file)
    r2reg.write_register(doc)
    assert "—" in utf8_file.read_text()
    assert not utf8_file.read_text().endswith("\n")


# ------------------ D6/6c: the tile-MCC oracle at the carried k (r2) ---
# PI ruling 6c (planning/pi-decisions-2026-09-20.md, 2026-09-20): the
# board's tile-MCC oracle is the optimum over prob_t with min_votes PINNED
# to the family's carried vote count. The ten carried-k cells are
# registered; the ten unconstrained optima they supersede stay on disk,
# unregistered, as the evidence for the redefinition (Obs 492).

#: (run id, label, prob_threshold, vote_threshold, n_passes, board cell).
MCC_CARRIED_ROWS = [
    ("gemini37-55map-2026-08-29", "arm1-n1-mcc-oracle-posthoc-p0.20-k1-r2-gt",
     0.2, 1, 1, "ARM1-N1-mcc-oracle-k1"),
    ("gemini37-55map-2026-08-29", "arm1-n3-mcc-oracle-posthoc-p0.20-k3-r2-gt",
     0.2, 3, 3, "ARM1-N3-mcc-oracle-k3"),
    ("gemini37-55map-2026-08-29", "arm1-n5-mcc-oracle-posthoc-p0.20-k5-r2-gt",
     0.2, 5, 5, "ARM1-N5-mcc-oracle-k5"),
    ("gemini37-55map-2026-08-29", "arm2-n1-mcc-oracle-posthoc-p0.96-k1-r2-gt",
     0.96, 1, 1, "ARM2-N1-mcc-oracle-k1"),
    ("gemini37-55map-2026-08-29", "arm2-n3-mcc-oracle-posthoc-p0.96-k3-r2-gt",
     0.96, 3, 3, "ARM2-N3-mcc-oracle-k3"),
    ("gemini37-55map-2026-08-29", "arm2-n5-mcc-oracle-posthoc-p0.96-k5-r2-gt",
     0.96, 5, 5, "ARM2-N5-mcc-oracle-k5"),
    ("stride-55map-2026-08-25",
     "g384-ov192-55map-n1-verified37-mcc-oracle-posthoc-p0.96-k1-r2-gt",
     0.96, 1, 1, "FOURTH-N1-mcc-oracle-k1"),
    ("stride-55map-2026-08-25",
     "g384-ov192-55map-n3-verified37-mcc-oracle-posthoc-p0.96-k3-r2-gt",
     0.96, 3, 3, "FOURTH-N3-mcc-oracle-k3"),
    ("stride-55map-2026-08-25",
     "g384-ov192-55map-n5-verified37-mcc-oracle-posthoc-p0.96-k5-r2-gt",
     0.96, 5, 5, "FOURTH-N5-mcc-oracle-k5"),
    ("stride-55map-2026-08-25",
     "g384-ov192-55map-n10-verified37-mcc-oracle-posthoc-p0.96-k10-r2-gt",
     0.96, 10, 10, "FOURTH-N10-mcc-oracle-k10"),
]


@pytest.mark.tier1
def test_the_ten_carried_k_mcc_oracles_are_registered():
    """6c: all ten rows present, at the pinned k, against the carried-k cell."""
    dec = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]
    for run_id, label, prob, votes, n_passes, cell in MCC_CARRIED_ROWS:
        rows = [c for c in dec[run_id]["conditions"] if c.get("label") == label]
        assert len(rows) == 1, f"{run_id}::{label}: expected one row, got {len(rows)}"
        row = rows[0]
        assert row["prob_threshold"] == prob
        assert row["vote_threshold"] == votes
        assert row["n_passes"] == n_passes
        assert row["eval_path"] == f"{R2_BOARD_REL}/cells/{cell}/evaluation.json"
        assert (ROOT / row["eval_path"]).exists(), row["eval_path"]
        # The cell pins its k in its own name; the row must agree with it.
        assert cell.endswith(f"-k{votes}"), (cell, votes)
        note = row["_note"]
        assert "mcc-oracle at carried k" in note and "min_votes PINNED" in note
        assert "Observation 492" in note
        assert "unconstrained" in note


@pytest.mark.tier1
def test_nothing_is_held_and_every_board_mcc_cell_has_a_row():
    """Amended D6c: nothing held; both definitions registered, neither presented.

    The unconstrained optima became the tile-presence table's members and
    the carried-k cells are retained but not presented, so every one of the
    twenty cells must reach a registered condition. Three families offer a
    single vote count: their two cells hold byte-identical detections and
    the labels coincide, so one row serves both and the count is 17.
    """
    import hashlib

    assert r2reg.HELD_BASES == ()
    manifest = json.loads(
        (ROOT / R2_BOARD_REL / "cells_manifest.json").read_text())["cells"]
    free = [c["label"] for c in manifest
            if r2reg.TILE_PRESENCE_BASIS in c.get("basis", "")]
    pinned = [c["label"] for c in manifest
              if r2reg.MCC_CARRIED_BASIS in c.get("basis", "")]
    assert len(free) == 10 and len(pinned) == 10, (len(free), len(pinned))
    assert not set(free) & set(pinned)

    dec = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]
    registered = {Path(c["eval_path"]).parent.name
                  for run in dec.values() for c in run["conditions"]
                  if str(c.get("eval_path", "")).startswith(
                      f"{R2_BOARD_REL}/cells/")}
    assert set(pinned) <= registered, sorted(set(pinned) - registered)
    missing = sorted(set(free) - registered)
    assert len(missing) == 3, missing
    for cell in missing:
        # Registered through its identical twin, not dropped.
        twin = f"{cell}-k1"
        assert twin in registered, cell
        digest = lambda name: hashlib.sha256(  # noqa: E731
            (ROOT / R2_BOARD_REL / "cells" / name
             / "detections.geojson").read_bytes()).hexdigest()
        assert digest(cell) == digest(twin), cell


@pytest.mark.tier1
def test_the_cell_regex_reads_the_carried_k_suffix():
    """-mcc-oracle-k<N> parses; the older forms keep parsing."""
    cases = {
        "ARM1-N3-mcc-oracle-k3": ("ARM1", "3", "mcc-oracle", "3"),
        "FOURTH-N10-mcc-oracle-k10": ("FOURTH", "10", "mcc-oracle", "10"),
        "ARM2-N1-mcc-oracle": ("ARM2", "1", "mcc-oracle", None),
        "A-N3-carried": ("A", "3", "carried", None),
        "TH7-oracle": ("TH7", None, "oracle", None),
    }
    for label, want in cases.items():
        m = r2reg._CELL_RE.match(label)
        assert m, label
        assert (m.group("fam"), m.group("n"), m.group("basis"),
                m.group("ck")) == want, label


@pytest.mark.tier1
def test_a_carried_k_cell_whose_label_and_point_disagree_raises():
    """The pinned k is stated twice; a disagreement is a typo, not a row."""
    dec = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]
    manifest = [{"label": "ARM2-N3-mcc-oracle-k3", "det": "x/d.geojson",
                 "basis": r2reg.MCC_CARRIED_BASIS + " (post-hoc, 2026-09-20)",
                 "point": "(0.96, k2)", "committed_eval": False}]
    with pytest.raises(ValueError, match="label pins k3"):
        r2reg.author_board_rows(dec, manifest, None)


#: The image campaigns' MCC-oracle conditions after the 2026-09-20 re-point:
#: (run id, superseded label, its cell, successor label, its cell).
IMAGE_MCC_REPOINTS = [
    ("gemini37-image-55map-2026-09-13",
     "img-arm2-k3-mcc-oracle-p0.96-k2-r2-gt", "IMG-ARM2-K3-mcc-oracle",
     "img-arm2-k3-mcc-oracle-p0.90-k3-r2-gt"),
    ("gemini3-image-55map-2026-09-16",
     "g3img-arm1-k3-mcc-oracle-p0.35-k1-r2-gt", "G3IMG-ARM1-K3-mcc-oracle",
     "g3img-arm1-k3-mcc-oracle-p0.20-k3-r2-gt"),
    ("gemini3-image-55map-2026-09-16",
     "g3img-arm2-k3-mcc-oracle-p0.98-k1-r2-gt", "G3IMG-ARM2-K3-mcc-oracle",
     "g3img-arm2-k3-mcc-oracle-p0.96-k3-r2-gt"),
    ("gemini3-image-55map-2026-09-16",
     "g3img-arm1-k5-mcc-oracle-p0.40-k1-r2-gt", "G3IMG-ARM1-K5-mcc-oracle",
     "g3img-arm1-k5-mcc-oracle-p0.20-k5-r2-gt"),
    ("gemini3-image-55map-2026-09-16",
     "g3img-arm2-k5-mcc-oracle-p0.98-k1-r2-gt", "G3IMG-ARM2-K5-mcc-oracle",
     "g3img-arm2-k5-mcc-oracle-p0.98-k5-r2-gt"),
]


@pytest.mark.tier1
def test_the_superseded_image_rows_keep_their_id_and_gain_a_successor():
    """A signed row's citation must keep resolving to what the PI was shown.

    Two SIGNED analysis rows cite the five superseded ids in
    conditions_compared, so the id survives and is re-pointed to the
    -unconstrained cell -- the same bytes under a new name. The carried-k
    selection is registered as a NEW id, which no signature covers.
    """
    dec = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]
    for run_id, old, cell, new in IMAGE_MCC_REPOINTS:
        by = {c["label"]: c for c in dec[run_id]["conditions"]}
        assert old in by, f"{run_id}: superseded id {old} must not be deleted"
        assert new in by, f"{run_id}: successor {new} missing"
        base = f"results/{run_id}/cells"
        assert by[old]["eval_path"] == f"{base}/{cell}-unconstrained/evaluation.json"
        assert by[new]["eval_path"] == f"{base}/{cell}/evaluation.json"
        assert "SUPERSEDED 2026-09-20" in by[old]["_note"]
        assert new in by[old]["_note"]        # names its successor
        assert old in by[new]["_note"]        # and is named by it
        for lb in (old, new):
            assert (ROOT / by[lb]["eval_path"]).exists(), by[lb]["eval_path"]


@pytest.mark.tier1
def test_every_image_mcc_row_matches_its_cells_n_detections():
    """Wrong-source guard: each row's eval must hold that cell's own count."""
    dec = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]
    for run_id in ("gemini37-image-55map-2026-09-13", "gemini3-image-55map-2026-09-16"):
        manifest = json.loads(
            (ROOT / f"results/{run_id}/cells_manifest.json").read_text())["cells"]
        n_of = {c["label"]: c["n_detections"] for c in manifest}
        seen = 0
        for cond in dec[run_id]["conditions"]:
            if "-mcc-oracle-" not in (cond.get("label") or ""):
                continue
            cell = Path(cond["eval_path"]).parent.name
            ev = json.loads((ROOT / cond["eval_path"]).read_text())
            assert ev["summary"]["n_detections"] == n_of[cell], cond["label"]
            seen += 1
        # Six original rungs each, plus one successor per rung that moved:
        # one in the 3.7 campaign, four in the Gemini 3 campaign.
        assert seen == (7 if run_id.startswith("gemini37") else 10), (run_id, seen)


@pytest.mark.tier1
def test_registration_is_idempotent_per_cell_not_per_label():
    """A relabel upstream must not plan a second row for a scored cell.

    The registrar reads ``posthoc`` off the manifest's free-text basis, so
    the label scheme depends on prose an adjacent agent rewrites. On
    2026-09-21 the board agent dropped "post-hoc" from both MCC bases and
    this step planned TWENTY additions over seventeen already-registered
    cells -- two of them twice within one plan, which apply() would have
    appended without complaint. Presence is therefore decided on
    ``eval_path``: whatever the label scheme does, a cell that something
    already scores is present.
    """
    dec = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]
    manifest = json.loads(
        (ROOT / R2_BOARD_REL / "cells_manifest.json").read_text())["cells"]
    board_path = ROOT / R2_BOARD_REL / "final_board_50m.json"
    board = json.loads(board_path.read_text()) if board_path.exists() else None

    plan = r2reg.author_board_rows(dec, manifest, board)
    adds = [row["label"] for _r, row, s in plan if s == "add"]
    assert adds == [], adds

    # And the guard is the eval_path, not the label: rename the board rows'
    # labels out of the way and the plan must still add nothing. (Only
    # theirs -- _template resolves the 3.7 and fourth-cell schemes by label
    # prefix, which is a separate, legitimate use.)
    renamed = json.loads(json.dumps(dec))
    touched = 0
    for run in renamed.values():
        for cond in run["conditions"]:
            if str(cond.get("eval_path", "")).startswith(f"{R2_BOARD_REL}/cells/"):
                cond["label"] = "renamed-" + cond["label"]
                touched += 1
    assert touched > 30, touched
    plan = r2reg.author_board_rows(renamed, manifest, board)
    adds = [Path(row["eval_path"]).parent.name
            for _r, row, s in plan if s == "add"]
    # Exactly the three cells that were never registered in their own right:
    # their free and pinned optima are the same point, so the -k1 twin's row
    # already scores those bytes and a second row would be a duplicate
    # measurement. They are present by label coincidence, which is the
    # documented mechanism, so a rename is the one thing that exposes them.
    assert sorted(adds) == ["ARM1-N1-mcc-oracle", "ARM2-N1-mcc-oracle",
                            "FOURTH-N1-mcc-oracle"], adds
    import hashlib
    for cell in adds:
        digest = lambda name: hashlib.sha256(  # noqa: E731
            (ROOT / R2_BOARD_REL / "cells" / name
             / "detections.geojson").read_bytes()).hexdigest()
        assert digest(cell) == digest(f"{cell}-k1"), cell
