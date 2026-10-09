"""
Tier-1 tests for the D51 same-area check (``scripts/lib_assessed_area.py``).

PI ruling D51 (2026-10-07, ``planning/pi-decisions-2026-09-20.md``): rungs of
a ladder are compared on the area every rung searched, and the comparison
code must confirm the areas assessed are the same — refusing otherwise, or
clipping to the common area and naming the clip — and must say so loudly
when a pool's area cannot be determined from its provenance.

The contract exercised here, on synthetic tilings, passes and unions written
to a temporary directory:

* **refusal** — pools whose assessed areas differ beyond the tolerance raise
  :class:`AssessedAreaMismatchError` (exit 3 from the CLI and the gate);
* **clip** — with ``clip_to_common`` the comparison names the clip and the
  area each pool loses, and the clip helpers drop exactly the points
  outside it; the ladder builder re-scores its points clipped; a clip
  never removes a reference (D51 option 1);
* **publishing** — the ladder builder's tables, gains, export and figure
  report the clipped score as their named basis, keep the as-evaluated
  score as a named historical basis, withhold what the clip did not
  regenerate, refuse (exit 5) a clip that cannot re-score a reported point,
  and name no basis at all without a clip (Astra's review of 2026-10-09,
  finding 1);
* **undetermined** — a union with no record, no declaration and no pass
  provenance is undetermined with a reason, and the comparison raises
  :class:`AssessedAreaUndeterminedError` (exit 4) unless explicitly allowed,
  in which case the status is never "same";
* **both options** — with a clip and undetermined pools allowed, a mismatch
  among the determined pools clips EVERY pool to their common area and the
  status names both facts, never a bare "undetermined" (PR #26 review,
  finding 1);
* **provenance** — a consensus union's area is the union of its passes'
  processed tiles (recovery fragments resolved through a subset manifest),
  and a builder's record and a declared record are read and checked against
  the pool's candidates;
* **frame** — areas are compared within the scoring frame, so a difference
  wholly outside it is not a mismatch.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import lib_assessed_area as laa  # noqa: E402

pytestmark = pytest.mark.tier1

CRS = "EPSG:32635"


# ── Synthetic world: a 4 × 1 strip of 1 km tiles on sheet "S" ─────────────


def write_tiles(path: Path, xs: list[int]) -> Path:
    """Write 1 km tiles named S_x<x>_y0.png at the given kilometre offsets."""
    gdf = gpd.GeoDataFrame(
        {"tile_name": [f"S_x{x}_y0.png" for x in xs]},
        geometry=[box(x * 1000, 0, (x + 1) * 1000, 1000) for x in xs], crs=CRS,
    )
    gdf.to_file(path, driver="GeoJSON")
    return path


def write_points(path: Path, xy: list[tuple[float, float]], **props) -> Path:
    """Write points (metres) as a GeoJSON in EPSG:32635."""
    gdf = gpd.GeoDataFrame(props or {"vote_count": [1] * len(xy)},
                           geometry=[Point(x, y) for x, y in xy], crs=CRS)
    gdf.to_file(path, driver="GeoJSON")
    return path


def write_record(union: Path, footprint: Path, clip: Path | None = None,
                 manifest: Path | None = None) -> Path:
    """Write a builder's assessed-area record beside a union."""
    record = {
        "schema": laa.RECORD_SCHEMA, "pool": str(union), "builder": "test",
        "footprint": {"bounds": str(footprint),
                      "manifest": str(manifest) if manifest else None},
        "clip": {"name": "test-clip", "bounds": str(clip)} if clip else None,
    }
    target = laa.record_path_for(union)
    target.write_text(json.dumps(record))
    return target


@pytest.fixture()
def world(tmp_path: Path) -> dict[str, Path]:
    """A four-tile tiling, a two-tile clip, and two unions (native, clipped)."""
    tiling = write_tiles(tmp_path / "tiling.geojson", [0, 1, 2, 3])
    clip = write_tiles(tmp_path / "clip.geojson", [0, 1])
    native = write_points(tmp_path / "native.geojson", [(500, 500), (2500, 500)])
    clipped = write_points(tmp_path / "clipped.geojson", [(500, 500), (1500, 500)])
    write_record(native, tiling)
    write_record(clipped, tiling, clip=clip)
    return {"tmp": tmp_path, "tiling": tiling, "clip": clip,
            "native": native, "clipped": clipped}


# ── Refusal, sameness, clip ───────────────────────────────────────────────


def test_different_areas_are_refused(world):
    """The 3.7 ladder's shape: one rung clipped upstream, one not."""
    areas = [laa.determine_assessed_area(world["native"], label="K = 1"),
             laa.determine_assessed_area(world["clipped"], label="K = 5")]
    assert [a.method for a in areas] == [laa.METHOD_RECORD, laa.METHOD_RECORD]
    assert areas[0].area_km2 == pytest.approx(4.0)
    assert areas[1].area_km2 == pytest.approx(2.0)
    with pytest.raises(laa.AssessedAreaMismatchError) as caught:
        laa.compare_assessed_areas(areas)
    record = caught.value.comparison
    assert record["status"] == "refused"
    assert record["max_excess_km2"] == pytest.approx(2.0)


def test_same_areas_pass(world):
    """Two pools on the same footprint and clip are the same area."""
    other = write_points(world["tmp"] / "other.geojson", [(700, 700)])
    write_record(other, world["tiling"], clip=world["clip"])
    areas = [laa.determine_assessed_area(world["clipped"], label="a"),
             laa.determine_assessed_area(other, label="b")]
    comparison = laa.compare_assessed_areas(areas)
    assert comparison.status == laa.STATUS_SAME
    assert comparison.record["max_excess_km2"] == pytest.approx(0.0)


def test_equal_sizes_in_different_places_are_still_refused(world):
    """The common area is the intersection, so position counts, not size."""
    east = write_tiles(world["tmp"] / "east.geojson", [2, 3])
    shifted = write_points(world["tmp"] / "shifted.geojson", [(2500, 500)])
    write_record(shifted, world["tiling"], clip=east)
    areas = [laa.determine_assessed_area(world["clipped"], label="west"),
             laa.determine_assessed_area(shifted, label="east")]
    with pytest.raises(laa.AssessedAreaMismatchError):
        laa.compare_assessed_areas(areas)


def test_clip_names_the_clip_and_the_area_removed(world):
    """With clip_to_common the result names the clip and each pool's loss."""
    areas = [laa.determine_assessed_area(world["native"], label="K = 1"),
             laa.determine_assessed_area(world["clipped"], label="K = 5")]
    comparison = laa.compare_assessed_areas(areas, clip_to_common=True)
    assert comparison.status == laa.STATUS_CLIPPED
    clip = comparison.record["clip"]
    assert clip["name"] == laa.COMMON_AREA_CLIP_NAME
    assert clip["area_removed_km2"] == {"K = 1": pytest.approx(2.0), "K = 5": 0.0}
    assert comparison.common.area / 1e6 == pytest.approx(2.0)
    points = gpd.read_file(world["native"])
    kept, removed = laa.clip_points_to_area(points, comparison.common)
    assert (len(kept), removed) == (1, 1)


def test_difference_outside_the_frame_is_not_a_mismatch(world):
    """Compared within a frame that lies inside the clip, the pools agree."""
    frame = write_tiles(world["tmp"] / "frame.geojson", [0])
    areas = [laa.determine_assessed_area(world["native"], label="a"),
             laa.determine_assessed_area(world["clipped"], label="b")]
    comparison = laa.compare_assessed_areas(areas, frame=frame)
    assert comparison.status == laa.STATUS_SAME
    assert comparison.record["frame_area_km2"] == pytest.approx(1.0)


def test_tolerance_is_honoured(world):
    """A difference within the stated tolerance counts as the same area."""
    areas = [laa.determine_assessed_area(world["native"], label="a"),
             laa.determine_assessed_area(world["clipped"], label="b")]
    comparison = laa.compare_assessed_areas(areas, tolerance_km2=2.5)
    assert comparison.status == laa.STATUS_SAME


# ── Undetermined ──────────────────────────────────────────────────────────


def test_a_pool_without_provenance_is_undetermined_and_refused(world):
    """No record, no declaration, no pass provenance: say so, never guess."""
    bare = write_points(world["tmp"] / "bare.geojson", [(500, 500)])
    area = laa.determine_assessed_area(bare, label="bare")
    assert area.method == laa.METHOD_UNDETERMINED
    assert not area.determined
    assert "no assessed-area record" in area.reason
    with pytest.raises(laa.AssessedAreaUndeterminedError, match="UNDETERMINED"):
        laa.compare_assessed_areas(
            [area, laa.determine_assessed_area(world["native"], label="n")])


def test_allowing_undetermined_never_reports_the_same_area(world):
    """Explicitly allowed, the status is 'undetermined', never 'same'."""
    bare = write_points(world["tmp"] / "bare.geojson", [(500, 500)])
    areas = [laa.determine_assessed_area(bare, label="bare"),
             laa.determine_assessed_area(world["native"], label="n")]
    comparison = laa.compare_assessed_areas(areas, allow_undetermined=True)
    assert comparison.status == laa.STATUS_UNDETERMINED
    assert comparison.record["undetermined"] == ["bare"]


# ── Both options: a clip AND undetermined pools (PR #26 review, finding 1) ──
#
# The four refused pv-diag-384 ladders have K = 1 and K = 3 determined but
# different, and K = 5 and K = 10 undetermined. With --clip-to-common-area
# and --allow-undetermined-area both given, the gate used to return a bare
# "undetermined" with no clip, and every driver then swept unclipped.


def mixed_pools(world) -> list:
    """K = 1 (4 km²) and K = 3 (2 km²) determined; K = 5 undetermined."""
    bare = write_points(world["tmp"] / "bare.geojson", [(500, 500)])
    return [laa.determine_assessed_area(world["native"], label="K = 1"),
            laa.determine_assessed_area(world["clipped"], label="K = 3"),
            laa.determine_assessed_area(bare, label="K = 5")]


def test_both_options_clip_every_pool_to_the_determined_common_area(world):
    """A mismatch among the determined pools is clipped, never passed as undetermined."""
    comparison = laa.compare_assessed_areas(
        mixed_pools(world), clip_to_common=True, allow_undetermined=True)
    assert comparison.status == laa.STATUS_CLIPPED_UNDETERMINED
    assert comparison.status != laa.STATUS_UNDETERMINED
    assert comparison.clips
    record = comparison.record
    assert record["status"] == laa.STATUS_CLIPPED_UNDETERMINED
    assert record["undetermined"] == ["K = 5"]
    clip = record["clip"]
    assert clip["name"] == laa.COMMON_AREA_CLIP_NAME
    assert clip["common_to"] == ["K = 1", "K = 3"]
    assert clip["undetermined_clipped"] == ["K = 5"]
    # What the undetermined pool loses is unknown, and recorded as such.
    assert clip["area_removed_km2"] == {"K = 1": pytest.approx(2.0), "K = 3": 0.0,
                                        "K = 5": None}
    assert comparison.common.area / 1e6 == pytest.approx(2.0)


@pytest.mark.parametrize("pools", ["none-determined", "determined-agree"])
def test_both_options_without_a_mismatch_stay_undetermined(world, pools):
    """No pool determined, or the determined pools agree: no clip, as before."""
    bare = write_points(world["tmp"] / "bare.geojson", [(500, 500)])
    other = write_points(world["tmp"] / "other.geojson", [(700, 700)])
    if pools == "none-determined":
        areas = [laa.determine_assessed_area(bare, label="a"),
                 laa.determine_assessed_area(other, label="b")]
    else:
        same = write_points(world["tmp"] / "same.geojson", [(600, 600)])
        write_record(same, world["tiling"], clip=world["clip"])
        areas = [laa.determine_assessed_area(world["clipped"], label="a"),
                 laa.determine_assessed_area(same, label="b"),
                 laa.determine_assessed_area(bare, label="c")]
    comparison = laa.compare_assessed_areas(areas, clip_to_common=True,
                                            allow_undetermined=True)
    assert comparison.status == laa.STATUS_UNDETERMINED
    assert not comparison.clips
    assert "clip" not in comparison.record


def test_the_gate_writes_the_clip_when_some_rungs_are_undetermined(world):
    """run_area_gate: with both options the drivers get a clip_geojson to sweep with."""
    bare = write_points(world["tmp"] / "bare.geojson", [(500, 500)])
    target = world["tmp"] / "gate" / "common.geojson"
    comparison = laa.run_area_gate(
        {"K = 1": str(world["native"]), "K = 3": str(world["clipped"]),
         "K = 5": str(bare)},
        frame=world["tiling"], clip_to_common=True, allow_undetermined=True,
        clip_geojson=target)
    assert comparison.status == laa.STATUS_CLIPPED_UNDETERMINED
    assert comparison.record["clip_geojson"]
    area, name = laa.read_area_geojson(target)
    assert name == laa.COMMON_AREA_CLIP_NAME
    assert area.area / 1e6 == pytest.approx(2.0)


def test_consensus_without_pass_provenance_is_undetermined(world):
    """A voting summary written before pass provenance existed says why."""
    pool = world["tmp"] / "consensus-n5"
    pool.mkdir()
    union = write_points(pool / "consensus_t1.geojson", [(500, 500)])
    (pool / "voting_summary.json").write_text(json.dumps({"total_passes": 5}))
    area = laa.determine_assessed_area(union, label="old")
    assert area.method == laa.METHOD_UNDETERMINED
    assert "no pass_provenance" in area.reason


def test_the_gate_exits_4_on_undetermined_and_3_on_mismatch(world):
    """run_area_gate: refusals are exits a driver cannot walk past."""
    bare = write_points(world["tmp"] / "bare.geojson", [(500, 500)])
    with pytest.raises(SystemExit) as undetermined:
        laa.run_area_gate({"a": str(bare), "b": str(world["native"])},
                          frame=world["tiling"])
    assert undetermined.value.code == laa.EXIT_AREA_UNDETERMINED
    with pytest.raises(SystemExit) as mismatch:
        laa.run_area_gate({"a": str(world["native"]), "b": str(world["clipped"])},
                          frame=world["tiling"])
    assert mismatch.value.code == laa.EXIT_AREA_MISMATCH


def test_the_cli_writes_the_common_area_when_asked_to_clip(world):
    """check_assessed_areas.py: exit 3 refused, exit 0 and a file when clipping."""
    from scripts.check_assessed_areas import main

    pools = ["--pool", f"K = 1={world['native']}", "--pool", f"K = 5={world['clipped']}"]
    assert main(pools) == 3
    out = world["tmp"] / "common.geojson"
    report = world["tmp"] / "comparison.json"
    assert main([*pools, "--clip-to-common", str(out), "--json", str(report)]) == 0
    area, name = laa.read_area_geojson(out)
    assert name == laa.COMMON_AREA_CLIP_NAME
    assert area.area / 1e6 == pytest.approx(2.0)
    assert json.loads(report.read_text())["status"] == laa.STATUS_CLIPPED
    bare = write_points(world["tmp"] / "bare.geojson", [(500, 500)])
    assert main(["--pool", f"a={bare}", "--pool", f"b={world['native']}"]) == 4


# ── Provenance routes ─────────────────────────────────────────────────────


@pytest.fixture()
def passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    """A registered tiling and three passes: two full, one partial + recovery."""
    tiling = write_tiles(tmp_path / "tiling.geojson", [0, 1, 2, 3])
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([f"S_x{x}_y0.png" for x in range(4)]))
    recovery_manifest = tmp_path / "recovery.json"
    recovery_manifest.write_text(json.dumps(["S_x3_y0.png"]))
    # Hermetic: only the synthetic tiling is registered.
    monkeypatch.setattr(laa, "KNOWN_TILINGS", {str(manifest): str(tiling)})

    def write_pass(name: str, tiles: list[int], man: Path) -> Path:
        path = tmp_path / name / "detections.geojson"
        path.parent.mkdir()
        path.write_text(json.dumps({
            "type": "FeatureCollection", "features": [],
            "processed_tiles": [f"S_x{x}_y0.png" for x in tiles],
        }))
        path.with_name("detections.meta.json").write_text(json.dumps(
            {"configuration": {"full_config_snapshot": {"manifest_path": str(man)}}}))
        return path

    return {
        "tmp": tmp_path,
        "run_1": write_pass("run_1", [0, 1, 2], manifest),
        "run_1_recovery": write_pass("run_1_recovery", [3], recovery_manifest),
        "run_2": write_pass("run_2", [0, 1], manifest),
    }


def consensus(tmp: Path, name: str, pass_paths: list[Path],
              xy: list[tuple[float, float]]) -> Path:
    """A merge_passes-style consensus union with its pass provenance."""
    pool = tmp / name
    pool.mkdir()
    union = write_points(pool / "consensus_t1.geojson", xy)
    (pool / "voting_summary.json").write_text(json.dumps({
        "pass_provenance_schema": "consensus-pass-provenance/1",
        "pass_provenance": [{"pass_id": p.parent.name, "path": str(p)} for p in pass_paths],
    }))
    return union


def test_pass_provenance_unions_the_processed_tiles(passes):
    """run_1 + its recovery fragment cover all four tiles; run_2 covers two."""
    full = consensus(passes["tmp"], "k1", [passes["run_1"], passes["run_1_recovery"]],
                     [(500, 500), (3500, 500)])
    part = consensus(passes["tmp"], "k2", [passes["run_2"]], [(500, 500)])
    a_full = laa.determine_assessed_area(full, label="full")
    a_part = laa.determine_assessed_area(part, label="part")
    assert a_full.method == laa.METHOD_PASS_PROVENANCE
    assert a_full.area_km2 == pytest.approx(4.0)
    assert a_part.area_km2 == pytest.approx(2.0)
    assert any("subset manifest" in line for line in a_full.evidence)
    with pytest.raises(laa.AssessedAreaMismatchError):
        laa.compare_assessed_areas([a_full, a_part])


def test_an_unregistered_tiling_is_undetermined(passes, monkeypatch):
    """A pass on a tiling with no registered polygons: undetermined, not guessed."""
    monkeypatch.setattr(laa, "KNOWN_TILINGS", {})
    union = consensus(passes["tmp"], "k2", [passes["run_2"]], [(500, 500)])
    area = laa.determine_assessed_area(union, label="k2")
    assert area.method == laa.METHOD_UNDETERMINED
    assert "no tile polygons are registered" in area.reason or \
        "no registered tiling" in area.reason


def test_a_missing_polygon_file_is_undetermined(world, tmp_path):
    """A record whose footprint file is gone reads as undetermined, not a crash."""
    union = write_points(tmp_path / "gone.geojson", [(500, 500)])
    write_record(union, tmp_path / "no-such-tiling.geojson")
    area = laa.determine_assessed_area(union, label="gone")
    assert area.method == laa.METHOD_UNDETERMINED
    assert "missing" in area.reason


def test_a_pass_without_processed_tiles_is_undetermined(passes):
    """No coverage record on a pass: the area cannot be established."""
    passes["run_2"].write_text(json.dumps({"type": "FeatureCollection", "features": []}))
    union = consensus(passes["tmp"], "k2", [passes["run_2"]], [(500, 500)])
    area = laa.determine_assessed_area(union, label="k2")
    assert area.method == laa.METHOD_UNDETERMINED
    assert "processed_tiles" in area.reason


def test_candidates_outside_the_determined_area_raise_a_warning(world):
    """A record that does not describe its pool is caught by its candidates."""
    wrong = write_points(world["tmp"] / "wrong.geojson", [(3500, 500)])
    write_record(wrong, world["tiling"], clip=world["clip"])
    area = laa.determine_assessed_area(wrong, label="wrong")
    assert area.determined
    assert any("OUTSIDE" in warning for warning in area.warnings)


def test_a_declared_record_is_read_for_a_legacy_pool(world, monkeypatch):
    """Legacy pools are determinable only through an evidenced declaration."""
    legacy = write_points(world["tmp"] / "legacy.geojson", [(500, 500)])
    declarations = world["tmp"] / "declarations.json"
    declarations.write_text(json.dumps({"declarations": [{
        "schema": laa.RECORD_SCHEMA, "pool": str(legacy),
        "footprint": {"bounds": str(world["tiling"]), "manifest": None},
        "clip": {"name": "c", "bounds": str(world["clip"])},
        "evidence": ["builder line 1"],
    }]}))
    monkeypatch.setattr(laa, "DECLARATIONS_PATH", declarations)
    laa._declarations.cache_clear()
    try:
        area = laa.determine_assessed_area(legacy, label="legacy")
    finally:
        laa._declarations.cache_clear()
    assert area.method == laa.METHOD_DECLARED
    assert area.area_km2 == pytest.approx(2.0)
    assert any("builder line 1" in line for line in area.evidence)


def test_a_stale_crop_manifest_is_flagged(world):
    """Crops cut from a union that was later rebuilt: warn, report the rebuilt."""
    crops = world["tmp"] / "crops"
    crops.mkdir()
    (crops / "candidate_manifest.json").write_text(json.dumps(
        {"source_geojson": str(world["native"]), "total_detections": 5,
         "candidates": []}))
    area = laa.determine_assessed_area(crops, label="crops")
    assert area.union.endswith("native.geojson")
    assert any("rebuilt" in warning for warning in area.warnings)


def test_write_area_record_round_trips(world):
    """What a builder writes, determine_assessed_area reads back."""
    union = write_points(world["tmp"] / "built.geojson", [(500, 500)])
    target = laa.write_area_record(
        union, builder="test", footprint_bounds=str(world["tiling"]),
        footprint_manifest=None, clip_name="c", clip_bounds=str(world["clip"]),
        passes=["p1"])
    assert json.loads(target.read_text())["area_km2"] == pytest.approx(2.0)
    assert laa.determine_assessed_area(union).method == laa.METHOD_RECORD


# ── Wiring: the ladder builder and the sweep ──────────────────────────────


def test_the_ladder_builder_refuses_and_clips(world):
    """apply_area_gate: a refusal by default; with a clip, clipped re-scores."""
    from scripts import build_k_ladder_phase2_tables as tables

    refs = write_points(world["tmp"] / "refs.geojson",
                        [(500, 500), (2500, 500)], Map=["S", "S"])
    detections = write_points(world["tmp"] / "dets.geojson", [(501, 500), (2501, 500)],
                              source_tile=["S_x0_y0.png", "S_x2_y0.png"])
    evaluation = world["tmp"] / "evaluation.json"
    evaluation.write_text(json.dumps({"_metadata": {"input_files": {
        "detections": str(detections), "bounds": str(world["tiling"]),
        "ground_truth": str(refs)}}}))

    # As evaluated, both detections match both references: F1@20 = 1.
    as_evaluated = {"eval_path": str(evaluation), "vote_t": 1, "prob_t": 0.5,
                    "f1_20": 1.0, "f1_20_ci": [0.9, 1.0], "precision_20": 1.0,
                    "recall_20": 1.0, "tile_mcc": 0.8, "n_detections": 2}

    def payload() -> dict:
        return {"ladders": [{
            "family": "test", "frame_file": str(world["tiling"]),
            "rungs": [
                {"K": 1, "pool": str(world["native"]),
                 "opmax": dict(as_evaluated), "carried": {}},
                {"K": 5, "pool": str(world["clipped"]), "opmax": None, "carried": {}},
            ]}]}

    refused = payload()
    messages = tables.apply_area_gate(refused)
    assert len(messages) == 1 and "DIFFER" in messages[0]
    assert refused["ladders"][0]["assessed_area"]["status"] == "refused"
    # A refused ladder's points are untouched.
    assert refused["ladders"][0]["rungs"][0]["opmax"] == as_evaluated

    clipped = payload()
    assert tables.apply_area_gate(clipped, clip_to_common=True) == []
    reported = clipped["ladders"][0]["rungs"][0]["opmax"]
    point = reported["clipped_to_common_area"]
    assert point["n_removed"] == 1
    assert (point["precision"], point["recall"]) == (1.0, 0.5)
    assert point["clip"] == laa.COMMON_AREA_CLIP_NAME
    # Astra's review of 2026-10-09, finding 1: the clipped score is the
    # REPORTED one, in the fields every product reads — 2/3, not the
    # unclipped 1 — and nothing unregenerated is paired with it.
    assert reported["score_basis"] == tables.BASIS_CLIPPED
    assert reported["f1_20"] == pytest.approx(2 / 3, abs=1e-4)
    assert (reported["precision_20"], reported["recall_20"]) == (1.0, 0.5)
    assert (reported["n_detections"], reported["n_removed_by_clip"]) == (1, 1)
    assert (reported["vote_t"], reported["prob_t"]) == (1, 0.5)
    for key in ("f1_20_ci", "tile_mcc", "eval_path"):
        assert reported[key] is None and key in reported["withheld"]
    assert reported["rescored_from_eval_path"] == str(evaluation)
    # The original values survive whole, under a named historical basis.
    history = reported[tables.HISTORICAL_KEY]
    assert history["score_basis"] == tables.BASIS_AS_EVALUATED
    assert {k: history[k] for k in as_evaluated} == as_evaluated
    assert clipped["ladders"][0]["score_basis"]["reported"] == tables.BASIS_CLIPPED
    assert clipped["score_basis"]["clip_requested"] is True


def write_evaluation(tmp: Path, tiling: Path) -> Path:
    """Two references and two matching detections, one in each half of the strip.

    The clip of the ``world`` fixture (tiles x0 and x1) holds one of each.
    """
    refs = write_points(tmp / "refs.geojson", [(500, 500), (2500, 500)], Map=["S", "S"])
    detections = write_points(tmp / "dets.geojson", [(501, 500), (2501, 500)],
                              source_tile=["S_x0_y0.png", "S_x2_y0.png"])
    evaluation = tmp / "evaluation.json"
    evaluation.write_text(json.dumps({"_metadata": {"input_files": {
        "detections": str(detections), "bounds": str(tiling),
        "ground_truth": str(refs)}}}))
    return evaluation


def test_a_clip_never_removes_references(world):
    """D51 option 1: clip the detections, keep the frame's reference set whole.

    A direct pin on :func:`rescore_clipped_evaluation`. The PR #26 review's
    mutation M7 (clip the references too) was caught only by the ladder
    builder's wiring test. Here the clip removes the detection in the east
    half (precision 1.0), and the east reference stays a false negative
    (recall 0.5); had the clip removed that reference too, recall would read
    1.0.
    """
    evaluation = write_evaluation(world["tmp"], world["tiling"])
    area = gpd.read_file(world["clip"]).union_all()
    out = laa.rescore_clipped_evaluation(evaluation, area, buffer_m=20)
    assert (out["n_detections"], out["n_removed"]) == (1, 1)
    assert (out["precision"], out["recall"]) == (1.0, 0.5)
    # The same cell unclipped finds both: the 0.5 is the clip's doing.
    whole = gpd.read_file(world["tiling"]).union_all()
    assert laa.rescore_clipped_evaluation(evaluation, whole)["recall"] == 1.0


def test_the_ladder_builder_clips_an_undetermined_rung_too(world):
    """With both options, every rung is re-scored on the determined rungs' common area.

    The four refused pv-diag-384 ladders' shape (PR #26 review, finding 1):
    K = 1 and K = 3 determined but different, K = 5 with no provenance. The
    K = 5 point is clipped like the K = 1 point, and the ladder's status
    names both the clip and the undetermined rung.
    """
    from scripts import build_k_ladder_phase2_tables as tables

    evaluation = write_evaluation(world["tmp"], world["tiling"])
    bare = write_points(world["tmp"] / "bare.geojson", [(500, 500)])
    payload = {"ladders": [{
        "family": "test", "frame_file": str(world["tiling"]),
        "rungs": [
            {"K": 1, "pool": str(world["native"]),
             "opmax": {"eval_path": str(evaluation)}, "carried": {}},
            {"K": 3, "pool": str(world["clipped"]), "opmax": None, "carried": {}},
            {"K": 5, "pool": str(bare),
             "opmax": {"eval_path": str(evaluation)}, "carried": {}},
        ]}]}
    assert tables.apply_area_gate(payload, clip_to_common=True,
                                  allow_undetermined=True) == []
    ladder = payload["ladders"][0]
    assert ladder["assessed_area"]["status"] == laa.STATUS_CLIPPED_UNDETERMINED
    assert ladder["assessed_area"]["undetermined"] == ["K = 5"]
    for index in (0, 2):
        point = ladder["rungs"][index]["opmax"]["clipped_to_common_area"]
        assert point["n_removed"] == 1
        assert (point["precision"], point["recall"]) == (1.0, 0.5)
        assert point["clip"] == laa.COMMON_AREA_CLIP_NAME


def test_the_ladder_builder_refuses_a_rung_with_no_pool(world):
    """A rung the builder cannot trace to a pool is undetermined, not skipped."""
    from scripts import build_k_ladder_phase2_tables as tables

    ladder = {"family": "test", "frame_file": str(world["tiling"]),
              "rungs": [{"K": 1, "pool": None, "opmax": None, "carried": {}},
                        {"K": 5, "pool": str(world["clipped"]), "opmax": None,
                         "carried": {}}]}
    messages = tables.apply_area_gate({"ladders": [ladder]})
    assert len(messages) == 1 and "records no candidate pool" in messages[0]


# ── End to end: gate → tables, export and figure (Astra, 2026-10-09) ──────


def write_cell(tmp: Path, name: str, tiling: Path, xy: list[tuple[float, float]]) -> Path:
    """Write one evaluated cell: detections at ``xy``, the strip's two references.

    The references sit at x = 500 and x = 2500, one in each half of the
    strip; the ``world`` clip (tiles x0 and x1) holds the west one only.
    """
    refs = tmp / "refs.geojson"
    if not refs.exists():
        write_points(refs, [(500, 500), (2500, 500)], Map=["S", "S"])
    dets = write_points(tmp / f"{name}.geojson", xy,
                        source_tile=[f"S_x{int(x // 1000)}_y0.png" for x, _ in xy])
    evaluation = tmp / f"{name}.evaluation.json"
    evaluation.write_text(json.dumps({"_metadata": {"input_files": {
        "detections": str(dets), "bounds": str(tiling), "ground_truth": str(refs)}}}))
    return evaluation


def full_rung(k: int, pool: Path, evaluation: Path | None, f1: float, p: float,
              r: float, n: int) -> dict:
    """A rung shaped as build() makes it, costing US$K, one carried point shared."""
    point = {"vote_t": 1, "prob_t": 0.5, "n_detections": n, "f1_20": f1,
             "f1_20_ci": [round(f1 - 0.1, 4), f1], "precision_20": p, "recall_20": r,
             "tile_mcc": 0.5, "tile_mcc_ci": [0.4, 0.6]}
    if evaluation is not None:
        point["eval_path"] = str(evaluation)
    shell = dict(point)
    return {"K": k, "source": "test", "candidates": n, "pool": str(pool),
            "condition_id": f"run::k{k}", "opmax": point,
            "carried": {"k-equals-K": shell, "stride-shell": shell},
            "proposer_flex_usd": float(k), "verifier_flex_usd": 0.0,
            "all_in_flex_usd": float(k)}


def full_ladder(family: str, pool_slug: str, tiling: Path, rungs: list[dict]) -> dict:
    """A ladder shaped as build() makes it."""
    return {"family": family, "proposer_pool": pool_slug, "run_id": "run",
            "thinking_level": "minimal", "modality": "text", "temperature": 0.3,
            "pass_usd": 1.0, "pass_usd_anchor": "test", "corpus": "test",
            "frame": "test", "frame_file": str(tiling), "reference_file": "refs",
            "headline_buffer_m": 20, "r1_verifier": True, "n_rungs": len(rungs),
            "rungs": rungs}


@pytest.fixture()
def two_ladders(world) -> dict:
    """One ladder the gate must clip, one whose rungs searched the same area.

    The clipped ladder's rungs, as evaluated and clipped to tiles x0–x1:

    * K = 1 (native pool): detections at x 501, 1501, 2501 — as evaluated
      P 2/3, R 1, F1 0.8; clipped P 0.5, R 0.5, F1 0.5;
    * K = 3 (native pool): Astra's fixture, x 501 and 2501 — as evaluated
      F1 1; clipped P 1, R 0.5, F1 2/3;
    * K = 5 (clipped pool): x 501 — F1 2/3 either way.

    So the reported gain is +0.1667 (K = 1 0.5 → K = 3 0.6667) where the
    as-evaluated gain is +0.2 (0.8 → 1.0).
    """
    tmp, tiling = world["tmp"], world["tiling"]
    k1 = write_cell(tmp, "k1", tiling, [(501, 500), (1501, 500), (2501, 500)])
    k3 = write_cell(tmp, "k3", tiling, [(501, 500), (2501, 500)])
    k5 = write_cell(tmp, "k5", tiling, [(501, 500)])
    clipped = full_ladder("Clipped ladder", "clip-pool", tiling, [
        full_rung(1, world["native"], k1, 0.8, 2 / 3, 1.0, 3),
        full_rung(3, world["native"], k3, 1.0, 1.0, 1.0, 2),
        full_rung(5, world["clipped"], k5, 0.6667, 1.0, 0.5, 1),
    ])
    same = full_ladder("Same-area ladder", "same-pool", tiling, [
        full_rung(1, world["native"], k1, 0.8, 2 / 3, 1.0, 3),
        full_rung(3, world["native"], k3, 1.0, 1.0, 1.0, 2),
        full_rung(5, world["native"], k5, 0.6667, 1.0, 0.5, 1),
    ])
    return {"generated_at_utc": "2026-10-10T00:00:00+00:00", "n_ladders": 2,
            "ladders": [clipped, same]}


def run_builder(monkeypatch, tmp: Path, payload: dict, *flags: str) -> dict:
    """Run the ladder builder's CLI on ``payload``, writing into ``tmp``."""
    from scripts import build_k_ladder_phase2_tables as tables

    out = tmp / "phase2"
    monkeypatch.setattr(tables, "build", lambda: payload)
    monkeypatch.setattr(tables, "PHASE2", out)
    monkeypatch.setattr(tables, "FIGURE", tmp / "figure.png")
    monkeypatch.setattr(tables, "git_head", lambda: "test")
    monkeypatch.setattr(sys, "argv", ["build", *flags])
    tables.main()
    return {"ladders": json.loads((out / "ladders.json").read_text()),
            "tables": (out / "ladder-tables.md").read_text(),
            "compat": json.loads((out / "ladders-compat.json").read_text()),
            "figure": tmp / "figure.png"}


def table_row(markdown: str, section: str, k: int) -> list[str]:
    """The cells of rung K's row in one ladder's section of the tables."""
    body = markdown.split(f"## {section}\n", 1)[1].split("\n## ", 1)[0]
    row = next(line for line in body.splitlines() if line.startswith(f"| {k} |"))
    return [cell.strip() for cell in row.strip("|").split("|")]


def test_a_clipped_ladder_publishes_the_clipped_basis_end_to_end(
        world, two_ladders, monkeypatch):
    """Astra's finding 1: the tables, gains, export and figure report the clip.

    Before v1.4.0 the gate computed the clipped score in a nested block and
    every product published the unclipped one. Here the CLI runs from the
    gate to its written products, and each must carry the clipped value as
    its reported basis, name that basis, keep the as-evaluated value only as
    a named historical basis, and pair the clipped value with no interval,
    tile metric or evaluation it did not regenerate.
    """
    from scripts import build_k_ladder_phase2_tables as tables

    out = run_builder(monkeypatch, world["tmp"], two_ladders, "--clip-to-common-area")
    clipped, same = out["ladders"]["ladders"]

    # ladders.json: the reported fields carry the clip; history kept, named.
    assert out["ladders"]["score_basis"]["clip_requested"] is True
    assert clipped["score_basis"]["reported"] == tables.BASIS_CLIPPED
    expected = {1: (0.5, 0.8), 3: (0.6667, 1.0), 5: (0.6667, 0.6667)}
    for rung in clipped["rungs"]:
        reported, as_evaluated = expected[rung["K"]]
        for point in (rung["opmax"], rung["carried"]["stride-shell"]):
            assert point["f1_20"] == pytest.approx(reported, abs=1e-4)
            assert point[tables.HISTORICAL_KEY]["f1_20"] == pytest.approx(as_evaluated)
            assert point[tables.HISTORICAL_KEY]["score_basis"] == tables.BASIS_AS_EVALUATED
            for key in ("f1_20_ci", "tile_mcc", "tile_mcc_ci", "eval_path"):
                assert point[key] is None, (rung["K"], key)
    # The same-area ladder is reported as evaluated, its values untouched.
    assert same["score_basis"]["reported"] == tables.BASIS_AS_EVALUATED
    assert [r["opmax"]["f1_20"] for r in same["rungs"]] == [0.8, 1.0, 0.6667]
    assert tables.HISTORICAL_KEY not in same["rungs"][0]["opmax"]

    # The summary's gain is the clipped one; the as-evaluated gain is history.
    row = next(r for r in out["ladders"]["summary"] if r["family"] == "Clipped ladder")
    assert (row["f1_k1"], row["f1_best"], row["best_k"], row["gain"]) == (
        0.5, 0.6667, 3, 0.1667)
    assert row["score_basis"] == tables.BASIS_CLIPPED
    assert row["mcc_verdict"] == "withheld" and row["mcc_k1"] is None
    assert row[tables.HISTORICAL_KEY]["gain"] == pytest.approx(0.2)

    # The rendered tables: the basis named, clipped beside historical, MCC
    # withheld, the summary and Pareto rows on the clipped values.
    md = out["tables"]
    assert "**Score basis.**" in md
    assert "Score basis: **clipped to the common assessed area**" in md
    assert "Score basis: **as evaluated**" in md
    k1 = table_row(md, "Clipped ladder", 1)
    assert k1[4:8] == ["0.5000", "0.8000", "withheld", "2"]
    assert table_row(md, "Clipped ladder", 3)[4:6] == ["0.6667", "1.0000"]
    assert table_row(md, "Same-area ladder", 1)[4] == "0.8000"
    summary = next(line for line in md.splitlines()
                   if line.startswith("| Clipped ladder | clip-to-common"))
    assert "**+0.1667**" in summary and "withheld | withheld | withheld" in summary
    assert "+0.2000 (K=1 0.8000, K=3 1.0000)" in summary
    pareto = md.split("## Pareto", 1)[1]
    assert "| Clipped ladder | clip-to-common-assessed-area | " \
           "1 @ $1.00 → 0.5000; 3 @ $3.00 → 0.6667 |" in pareto

    # The export: the clipped ladder is withheld with what it lacks; the
    # same-area ladder is exported and names its basis.
    compat = out["compat"]
    assert [entry["family_base"] for entry in compat["ladders"]] == ["Same-area ladder"]
    assert compat["ladders"][0]["score_basis"] == tables.BASIS_AS_EVALUATED
    assert compat["score_basis"]["clip_requested"] is True
    withheld = next(e for e in compat["skipped"] if e["family"] == "Clipped ladder")
    assert withheld["score_basis"] == tables.BASIS_CLIPPED
    assert len(withheld["missing"]) == 3
    assert [(r["K"], r["f1_20"], r["f1_20_as_evaluated_historical"])
            for r in withheld["rungs"]] == [(1, 0.5, 0.8), (3, 0.6667, 1.0),
                                            (5, 0.6667, 0.6667)]

    # The figure plots the clipped values and labels the line.
    series = {s["family"]: s for s in tables.figure_series(out["ladders"])}
    assert series["Clipped ladder"]["label"].endswith("[clipped]")
    assert series["Clipped ladder"]["score_basis"] == tables.BASIS_CLIPPED
    assert [tuple(p) for p in series["Clipped ladder"]["points"]] == [
        (1, 1.0, 0.5), (3, 3.0, 0.6667), (5, 5.0, 0.6667)]
    assert [p[2] for p in series["Same-area ladder"]["points"]] == [0.8, 1.0, 0.6667]
    assert out["figure"].stat().st_size > 0


@pytest.mark.parametrize("fault", ["no-eval-path", "no-inputs"])
def test_a_clip_that_cannot_rescore_a_point_refuses(world, two_ladders, monkeypatch,
                                                    fault):
    """A requested clip exits 5 and writes nothing when a point cannot be re-scored.

    Before v1.4.0 such a point was skipped silently and published unclipped
    beside its clipped siblings (Astra's review of 2026-10-09, finding 1).
    """
    from scripts import build_k_ladder_phase2_tables as tables

    point = two_ladders["ladders"][0]["rungs"][1]["opmax"]
    if fault == "no-eval-path":
        del point["eval_path"]
    else:
        bare = world["tmp"] / "bare.evaluation.json"
        bare.write_text(json.dumps({"_metadata": {}}))
        point["eval_path"] = str(bare)
    with pytest.raises(SystemExit) as stop:
        run_builder(monkeypatch, world["tmp"], two_ladders, "--clip-to-common-area")
    assert stop.value.code == tables.EXIT_CLIP_RESCORE_FAILED == 5
    assert not (world["tmp"] / "phase2").exists()
    # The refused ladder is left as it was: no half-clipped points.
    assert two_ladders["ladders"][0]["rungs"][0]["opmax"]["f1_20"] == 0.8
    assert "score_basis" not in two_ladders["ladders"][0]


def test_an_unclipped_build_names_no_basis(world, two_ladders, monkeypatch):
    """Without the flag the products carry no basis record, so they keep v1.3.0's bytes.

    The mismatched ladder still refuses (exit 3); the same-area ladder alone
    builds, with its values as evaluated and no score-basis text anywhere.
    """
    with pytest.raises(SystemExit) as stop:
        run_builder(monkeypatch, world["tmp"], two_ladders)
    assert stop.value.code == laa.EXIT_AREA_MISMATCH
    two_ladders["ladders"] = two_ladders["ladders"][1:]
    two_ladders["n_ladders"] = 1
    out = run_builder(monkeypatch, world["tmp"], two_ladders, "--no-figure")
    for product in ("ladders", "compat"):
        assert "score_basis" not in json.dumps(out[product])
        assert "historical_as_evaluated" not in json.dumps(out[product])
    assert "Score basis" not in out["tables"] and "score basis" not in out["tables"]
    assert table_row(out["tables"], "Same-area ladder", 1)[4:6] == ["0.8000", "0.5000"]


def test_the_sweep_clips_and_names_the_clip(world, monkeypatch, tmp_path):
    """sweep_f1_greedy_pv --clip-area: candidates outside go, rows say so."""
    from scripts import sweep_f1_greedy_pv as sweep

    crops = tmp_path / "crops"
    crops.mkdir()
    candidates = [
        {"candidate_id": i, "source_tile": f"S_x{x}_y0.png", "centroid_x": x * 1000 + 500,
         "centroid_y": 500, "properties": {"vote_count": 1}}
        for i, x in enumerate([0, 2])
    ]
    (crops / "candidate_manifest.json").write_text(json.dumps({"candidates": candidates}))
    verified = tmp_path / "verified"
    verified.mkdir()
    (verified / "probabilities.json").write_text(json.dumps({"results": {
        f"candidate_{i:05d}": {"mound_probability": 0.9} for i in range(2)}}))
    refs = gpd.read_file(write_points(tmp_path / "refs.geojson", [(500, 500), (2500, 500)],
                                      Map=["S", "S"]))
    monkeypatch.setattr(sweep, "load_ground_truth", lambda: refs)
    common = laa.write_area_geojson(gpd.read_file(world["clip"]).union_all(),
                                    tmp_path / "common.geojson", name="clip-name")
    output = tmp_path / "sweep.json"
    monkeypatch.setattr(sys, "argv", [
        "sweep", "--config", "t", "--crops-dir", str(crops), "--verified-dir",
        str(verified), "--output", str(output), "--bounds", str(world["tiling"]),
        "--vote-thresholds", "1", "--clip-area", str(common)])
    assert sweep.main() == 0
    rows = json.loads(output.read_text())
    top = next(r for r in rows if r["prob_t"] == 0.0)
    assert (top["n"], top["clip_area"], top["clip_n_removed"]) == (1, "clip-name", 1)
    assert (top["p"], top["r"]) == (1.0, 0.5)
