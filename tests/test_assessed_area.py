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
  outside it; the ladder builder re-scores its points clipped;
* **undetermined** — a union with no record, no declaration and no pass
  provenance is undetermined with a reason, and the comparison raises
  :class:`AssessedAreaUndeterminedError` (exit 4) unless explicitly allowed,
  in which case the status is never "same";
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

    def payload() -> dict:
        return {"ladders": [{
            "family": "test", "frame_file": str(world["tiling"]),
            "rungs": [
                {"K": 1, "pool": str(world["native"]),
                 "opmax": {"eval_path": str(evaluation)}, "carried": {}},
                {"K": 5, "pool": str(world["clipped"]), "opmax": None, "carried": {}},
            ]}]}

    refused = payload()
    messages = tables.apply_area_gate(refused)
    assert len(messages) == 1 and "DIFFER" in messages[0]
    assert refused["ladders"][0]["assessed_area"]["status"] == "refused"

    clipped = payload()
    assert tables.apply_area_gate(clipped, clip_to_common=True) == []
    point = clipped["ladders"][0]["rungs"][0]["opmax"]["clipped_to_common_area"]
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
