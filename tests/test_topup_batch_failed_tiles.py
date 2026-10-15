"""Tier-1 tests for ``scripts/topup_batch_failed_tiles.py`` (ruling D67 (1)).

The tool sends a batch pass's failed tiles as their own Batch API job with
the pass's own command and merges the result into the pass. These tests run
on synthetic passes written by the project's own batch writer
(``lib_batch_api.write_batch_outputs``), so the metas have the real shape,
and a fake detector stands in for the API. They check that:

- the manifest holds exactly the failed tiles, in the full manifest's format;
- the command is the pass's own (``run_pass`` in
  ``scripts/run_pro_2x2_replication.sh``) apart from the manifest and output;
- the parameter gate and the request gate refuse a mismatched configuration,
  leaving the pass byte for byte as it was;
- a merge produces the expected GeoJSON, sidecar, and meta (counts, ids,
  usage sums, the ``recovery_history`` entry) and archives the pass first;
- a pass with no failures is untouched.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from scripts import topup_batch_failed_tiles as tb
from scripts.lib_batch_api import write_batch_outputs

pytestmark = pytest.mark.tier1

MODEL = "gemini-3.1-pro-preview"
SYSTEM = "# Mound Detection\n\nSynthetic instruction for the top-up tests.\n"
TILES = [f"K-00-000-0_Test_x{i * 336}_y0.png" for i in range(8)]
CACHED_PER_RESPONSE = 14549
CACHE = "cachedContents/test-cache"
GEN_HIGH_T0 = {"temperature": 0.0, "max_output_tokens": 8192,
               "response_mime_type": "application/json",
               "thinking_config": {"thinking_level": "HIGH"}}


def prompt_config(**overrides: Any) -> dict[str, Any]:
    """A prompt config shaped like ``library_plus-hp.json`` after CLI overrides."""
    cfg: dict[str, Any] = {
        "version": "library_plus-hp", "instruction_file": "detect_brief-text-image.md",
        "model": MODEL, "include_example_images": True, "temperature": 0.0,
        "max_output_tokens": 8192, "thinking_level": "high",
        "examples": [
            {"path": "synthetic/example_01.png", "label": "Positive",
             "category": "canonical_positive"},
            {"path": "synthetic/example_02.png", "label": "Negative",
             "category": "canonical_negative"},
        ],
    }
    cfg.update(overrides)
    return cfg


def usage(n: int, cached_per: int = CACHED_PER_RESPONSE, fresh_per: int = 1111,
          out_per: int = 80, thoughts_per: int = 2) -> dict[str, Any]:
    """Per-response usage summed over *n* responses, as aggregate_batch_usage emits it."""
    return {
        "total_input_tokens": n * (cached_per + fresh_per),
        "total_cached_tokens": n * cached_per,
        "total_output_tokens": n * out_per,
        "total_thoughts_tokens": n * thoughts_per,
        "total_tokens": n * (cached_per + fresh_per + out_per + thoughts_per),
        "n_responses_with_usage": n,
        "usage_source": "batch results file (per-response usageMetadata)",
        "cached_share": cached_per / (cached_per + fresh_per) if n else None,
    }


def feature(tile: str, k: int = 0) -> dict[str, Any]:
    """One detection feature from *tile*."""
    return {"type": "Feature",
            "geometry": {"type": "Polygon",
                         "coordinates": [[[k, 0], [k + 1, 0], [k + 1, 1], [k, 1], [k, 0]]]},
            "properties": {"source_tile": tile, "label": "mound", "subtype": "burial_mound",
                           "confidence": "high", "method": "library_plus-hp",
                           "model": MODEL}}


def write_pass(unit_dir: Path, run: int, completed: list[str], failed: list[str], *,
               cfg: dict[str, Any] | None = None, model: str = MODEL,
               system: str = SYSTEM, usage_stats: dict[str, Any] | None = None,
               per_tile: int = 1) -> None:
    """Write a pass with the project's batch writer (geojson, sidecar, meta)."""
    features = [feature(t, k) for t in completed for k in range(per_tile)]
    write_batch_outputs(
        features=features, processed_tiles=set(completed), failed_tiles=list(failed),
        output_file=unit_dir / f"detections_library_plus-hp_run{run:02d}.geojson",
        config=cfg or prompt_config(), model_name=model, system_instruction=system,
        total_detections=len(features),
        usage_stats=usage_stats if usage_stats is not None else usage(len(completed)))


def write_request_file(path: Path, keys: list[str], *, gen: dict[str, Any] | None = None,
                       cache: str | None = CACHE) -> Path:
    """A request JSONL shaped like ``build_jsonl_file``'s (no image bytes)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for key in keys:
            request: dict[str, Any] = {"contents": [], "generation_config": gen or GEN_HIGH_T0}
            if cache:
                request["cached_content"] = cache
            f.write(json.dumps({"key": key, "request": request}) + "\n")
    return path


def write_topup(spec: tb.PassSpec, out_dir: Path, recovered: list[str], still: list[str],
                **kwargs: Any) -> Path:
    """Write what the detector leaves for a top-up; return its request file."""
    gen = kwargs.pop("gen", None)
    cache = kwargs.pop("cache", CACHE)
    keys = kwargs.pop("keys", None)
    unit = tb.topup_unit_dir(spec, out_dir)
    write_pass(unit, spec.run, recovered, still, per_tile=2, **kwargs)
    return write_request_file(tb.request_file_path(spec, out_dir),
                              keys if keys is not None else recovered + still,
                              gen=gen, cache=cache)


def snapshot(pass_dir: Path) -> dict[str, bytes]:
    """Every file's bytes in a pass directory."""
    return {p.name: p.read_bytes() for p in sorted(pass_dir.iterdir()) if p.is_file()}


@pytest.fixture
def world(tmp_path: Path) -> SimpleNamespace:
    """A synthetic replication root with one pass (5 completed, 3 failed)."""
    base = tmp_path / "outputs" / "rep"
    spec = tb.PassSpec(corner="image-high-t0.0", run=5, temperature="0.0",
                       thinking_level="high", base=base)
    full = tmp_path / "full_evaluation_manifest.json"
    full.write_text(json.dumps(TILES, indent=2))
    completed, failed = TILES[:5], TILES[5:]
    write_pass(spec.pass_dir, spec.run, completed, failed)
    return SimpleNamespace(tmp=tmp_path, base=base, spec=spec, full=full,
                           completed=completed, failed=failed,
                           out=tmp_path / "work" / "runs" / spec.corner,
                           archive=tmp_path / "archive" / "pre-topup",
                           extra={"mode": "batch", "batch_job_name": "batches/test-job",
                                  "request_file": "files/test-upload",
                                  "context_cache": CACHE, "ruling": tb.RULING})


# ─────────────────────────────────────────────────────────────────────
# Manifest, scope gate, command
# ─────────────────────────────────────────────────────────────────────


def test_the_manifest_holds_exactly_the_failed_tiles(world: SimpleNamespace) -> None:
    failed = tb.scope_failed_tiles(world.spec.pass_dir, 3)
    assert failed == sorted(world.failed)
    out = world.tmp / "manifest.json"
    tiles = tb.write_failed_manifest(failed, world.full, out)
    expected = [t for t in TILES if t in set(world.failed)]
    assert tiles == expected
    # The full manifest's format: a JSON list of names, two-space indent.
    assert out.read_text() == json.dumps(expected, indent=2) + "\n"
    assert not set(json.loads(out.read_text())) & set(world.completed)


def test_the_scope_gate_refuses_a_disagreeing_or_unapproved_pass(
        world: SimpleNamespace) -> None:
    with pytest.raises(tb.TopupError, match="approved"):
        tb.scope_failed_tiles(world.spec.pass_dir, 2)
    sidecar = next(world.spec.pass_dir.glob("*.tiles.json"))
    data = json.loads(sidecar.read_text())
    data["failed"] = data["failed"][:-1]
    sidecar.write_text(json.dumps(data))
    with pytest.raises(tb.TopupError, match="scope gate"):
        tb.scope_failed_tiles(world.spec.pass_dir, None)


def test_the_manifest_refuses_a_tile_outside_the_full_manifest(
        world: SimpleNamespace) -> None:
    with pytest.raises(tb.TopupError, match="not in"):
        tb.write_failed_manifest(["not-a-gs-tile.png"], world.full, world.tmp / "m.json")


def test_the_command_is_the_passes_own(world: SimpleNamespace) -> None:
    cmd = tb.detector_command(world.spec, Path("/w/m.json"), Path("/w/out"),
                              python="PY", dry_run=False)
    assert cmd == [
        "PY", "scripts/4_detect_mounds_batch.py",
        "--config", "prompts/configs/library_plus-hp.json",
        "--model", "gemini-3.1-pro", "--temperature", "0.0", "--thinking-level", "high",
        "--manifest", "/w/m.json", "--tiles-dir", "inputs/tiles_384", "--tile-size", "384",
        "--output-dir", "/w/out", "--mode", "batch", "--run", "5",
        "--use-cache", "--skip-intent-check", "--allow-inert-fields",
        "--service-tier", "flex",
    ]
    assert tb.detector_command(world.spec, Path("m"), Path("o"), python="PY",
                               dry_run=True)[-1] == "--dry-run"


def test_the_corner_table_matches_the_replication_driver() -> None:
    # Drift guard: the tool's corners, model, tiles, and flags are run_pass's.
    script = (tb.REPO_ROOT / "scripts" / "run_pro_2x2_replication.sh").read_text()
    for corner, (temp, think) in tb.CORNERS.items():
        assert f'[{corner}]="library_plus-hp.json {temp} {think} 3"' in script
    assert f"MODEL={tb.MODEL_CLI}\n" in script
    assert f"TILES_DIR={tb.TILES_DIR}\n" in script
    end = script.index('echo "=== $(date -u +%FT%TZ) $STAGE')
    run_pass = script[script.index("run_pass() {"):end]
    for flag in ("--mode batch", f"--tile-size {tb.TILE_SIZE}", "--skip-intent-check",
                 "--allow-inert-fields", f"--service-tier {tb.RETRY_SERVICE_TIER}",
                 'cache_flag="--use-cache"'):
        assert flag in run_pass
    assert sum(tb.APPROVED_FAILED.values()) == 152
    assert len(tb.wave3_specs()) == 12


# ─────────────────────────────────────────────────────────────────────
# Gates
# ─────────────────────────────────────────────────────────────────────


MISMATCHES = {
    "model": ({"model": "gemini-3-flash-preview"}, "model"),
    "system_instruction_hash": ({"system": SYSTEM + "edited\n"}, "system_instruction_hash"),
    "library_hash": ({"cfg": prompt_config(examples=[
        {"path": "synthetic/other.png", "label": "Positive",
         "category": "canonical_positive"}])}, "library_hash"),
    "temperature": ({"cfg": prompt_config(temperature=0.7)}, "temperature"),
    "thinking_level": ({"cfg": prompt_config(thinking_level="medium")}, "thinking_level"),
    "include_example_images": ({"cfg": prompt_config(include_example_images=False)},
                               "include_example_images"),
    "max_output_tokens": ({"cfg": prompt_config(max_output_tokens=2048)}, "max_output_tokens"),
    "uncached": ({"usage_stats": usage(2, cached_per=0)}, "caching"),
    "other_cache": ({"usage_stats": usage(2, cached_per=CACHED_PER_RESPONSE + 7)}, "caching"),
}


@pytest.mark.parametrize("case", sorted(MISMATCHES))
def test_the_gate_refuses_a_mismatched_configuration(world: SimpleNamespace,
                                                      case: str) -> None:
    kwargs, field = MISMATCHES[case]
    before = snapshot(world.spec.pass_dir)
    jsonl = write_topup(world.spec, world.out, world.failed[:2], world.failed[2:], **kwargs)
    result = tb.merge_topup(world.spec.pass_dir, tb.topup_unit_dir(world.spec, world.out),
                            world.failed, world.archive / "p", world.extra,
                            request_file=jsonl)
    assert result["merged"] is False
    assert result["reason"] == "parameter gate failed"
    assert result["gate"]["fields"][field]["equal"] is False
    assert snapshot(world.spec.pass_dir) == before
    assert not world.archive.exists()


def test_the_gate_passes_an_identical_configuration(world: SimpleNamespace) -> None:
    write_topup(world.spec, world.out, world.failed[:2], world.failed[2:])
    pass_meta = json.loads(next(world.spec.pass_dir.glob("*.meta.json")).read_text())
    topup_meta = json.loads(next(tb.topup_unit_dir(world.spec, world.out)
                                 .glob("*.meta.json")).read_text())
    gate = tb.parameter_gate(pass_meta, topup_meta)
    assert gate["passed"], gate
    assert set(tb.REQUIRED_GATE_FIELDS) <= set(gate["fields"])
    assert gate["fields"]["caching"]["topup"]["cached_tokens_per_response"] == CACHED_PER_RESPONSE


@pytest.mark.parametrize("bad", ["temperature", "uncached", "keys", "missing"])
def test_the_request_gate_refuses_a_request_file_that_differs(world: SimpleNamespace,
                                                              bad: str) -> None:
    before = snapshot(world.spec.pass_dir)
    kwargs: dict[str, Any] = {
        "temperature": {"gen": {**GEN_HIGH_T0, "temperature": 0.7}},
        "uncached": {"cache": None},
        "keys": {"keys": world.failed[:2]},
        "missing": {},
    }[bad]
    jsonl = write_topup(world.spec, world.out, world.failed[:2], world.failed[2:], **kwargs)
    if bad == "missing":
        jsonl.unlink()
    result = tb.merge_topup(world.spec.pass_dir, tb.topup_unit_dir(world.spec, world.out),
                            world.failed, world.archive / "p", world.extra,
                            request_file=jsonl)
    assert result["merged"] is False
    assert result["reason"] == "request gate failed"
    assert snapshot(world.spec.pass_dir) == before


def test_a_top_up_covering_other_tiles_is_refused(world: SimpleNamespace) -> None:
    before = snapshot(world.spec.pass_dir)
    jsonl = write_topup(world.spec, world.out, world.failed + [world.completed[0]], [])
    with pytest.raises(tb.TopupError, match="manifest"):
        tb.merge_topup(world.spec.pass_dir, tb.topup_unit_dir(world.spec, world.out),
                       world.failed, world.archive / "p", world.extra, request_file=jsonl)
    assert snapshot(world.spec.pass_dir) == before


# ─────────────────────────────────────────────────────────────────────
# The merge
# ─────────────────────────────────────────────────────────────────────


def test_the_merge_produces_the_expected_pass(world: SimpleNamespace) -> None:
    pdir = world.spec.pass_dir
    before = snapshot(pdir)
    old_geo = json.loads(next(pdir.glob("*.geojson")).read_text())
    old_meta = json.loads(next(pdir.glob("*.meta.json")).read_text())
    recovered, still = sorted(world.failed[:2]), [world.failed[2]]
    jsonl = write_topup(world.spec, world.out, recovered, still)
    tdir = tb.topup_unit_dir(world.spec, world.out)
    topup_meta = json.loads(next(tdir.glob("*.meta.json")).read_text())

    result = tb.merge_topup(pdir, tdir, world.failed, world.archive / "p", world.extra,
                            request_file=jsonl)
    assert result["merged"] is True, result
    assert (result["recovered"], result["still_failing"]) == (recovered, still)
    assert result["features_added"] == 4  # two per recovered tile

    geo = json.loads(next(pdir.glob("*.geojson")).read_text())
    assert geo["features"][:5] == old_geo["features"]
    assert len(geo["features"]) == 5 + 4
    assert {f["properties"]["source_tile"] for f in geo["features"][5:]} == set(recovered)
    assert geo["processed_tiles"] == sorted(world.completed + recovered)
    assert geo["crs"] == old_geo["crs"]

    tiles = json.loads(next(pdir.glob("*.tiles.json")).read_text())
    assert tiles["total_tiles"] == 8
    assert tiles["completed"] == sorted(world.completed + recovered)
    assert tiles["failed"] == still
    assert tiles["patched"] == recovered and tiles["patch_timestamp"]

    meta = json.loads(next(pdir.glob("*.meta.json")).read_text())
    es = meta["execution_stats"]
    assert es["items_processed"] == 7 and es["items_failed"] == 1
    assert sorted(es["completed_items"]) == sorted(world.completed + recovered)
    assert [fi["item_id"] for fi in es["failed_items"]] == still
    for key in ("total_input_tokens", "total_cached_tokens", "total_output_tokens",
                "total_thoughts_tokens", "total_tokens", "n_responses_with_usage"):
        assert meta["usage_stats"][key] == (old_meta["usage_stats"][key]
                                            + topup_meta["usage_stats"][key]), key
    assert meta["results_summary"]["total_detections"] == 9
    assert meta["configuration"] == old_meta["configuration"]
    assert meta["configuration_history"][-1]["differs_from_previous"] is False
    assert meta["cost_estimate"]["total_cost_usd"] == pytest.approx(
        old_meta["cost_estimate"]["total_cost_usd"]
        + topup_meta["cost_estimate"]["total_cost_usd"], abs=1e-5)

    entry = meta["recovery_history"][-1]
    assert len(meta["recovery_history"]) == 1
    assert entry["mode"] == "batch"
    assert entry["batch_job_name"] == "batches/test-job"
    assert entry["request_file"] == "files/test-upload"
    assert entry["context_cache"] == CACHE
    assert entry["tool"] == tb.TOOL_NAME
    assert entry["initial_failed"] == 3 and entry["recovered"] == 2
    assert entry["recovered_ids"] == recovered and entry["still_failing_ids"] == still
    assert entry["recovery_cost_usd"] == topup_meta["cost_estimate"]["total_cost_usd"]
    assert entry["recovery_usage"]["total_input_tokens"] == (
        topup_meta["usage_stats"]["total_input_tokens"])
    assert entry["recovery_service_tier"] == "batch"
    assert entry["recovery_run_id"] == topup_meta["run_id"] != old_meta["run_id"]
    assert entry["timestamp"]

    # The pre-top-up files were archived first, byte for byte.
    assert snapshot(world.archive / "p") == before
    assert tb.already_topped_up(meta)


def test_a_full_recovery_completes_the_pass(world: SimpleNamespace) -> None:
    jsonl = write_topup(world.spec, world.out, sorted(world.failed), [])
    result = tb.merge_topup(world.spec.pass_dir, tb.topup_unit_dir(world.spec, world.out),
                            world.failed, world.archive / "p", world.extra,
                            request_file=jsonl)
    assert result["merged"] is True
    tiles = json.loads(next(world.spec.pass_dir.glob("*.tiles.json")).read_text())
    meta = json.loads(next(world.spec.pass_dir.glob("*.meta.json")).read_text())
    assert tiles["completed"] == sorted(TILES) and tiles["failed"] == []
    assert meta["execution_stats"]["items_failed"] == 0
    assert meta["execution_stats"]["failed_items"] == []
    assert meta["execution_stats"]["items_processed"] == 8


def test_a_pass_with_no_failures_is_untouched(world: SimpleNamespace) -> None:
    clean = tb.PassSpec(corner="image-high-t0.0", run=6, temperature="0.0",
                        thinking_level="high", base=world.base)
    write_pass(clean.pass_dir, clean.run, TILES, [])
    before = snapshot(clean.pass_dir)
    todo, untouched = tb.plan([world.spec, clean], {world.spec.key: 3, clean.key: 0})
    assert [s.key for s, _ in todo] == [world.spec.key]
    assert untouched == [f"{clean.key} (no failed tiles)"]
    # Even handed a top-up, the merge refuses a pass whose failed list is not
    # the manifest's, and writes nothing.
    jsonl = write_topup(clean, world.out, world.failed, [])
    with pytest.raises(tb.TopupError, match="not the manifest"):
        tb.merge_topup(clean.pass_dir, tb.topup_unit_dir(clean, world.out), world.failed,
                       world.archive / "clean", world.extra, request_file=jsonl)
    assert snapshot(clean.pass_dir) == before
    assert not (world.archive / "clean").exists()


# ─────────────────────────────────────────────────────────────────────
# One pass end to end, with a fake detector
# ─────────────────────────────────────────────────────────────────────


class FakeCaches:
    """Stands in for ``client.caches``; records deletions."""

    def __init__(self) -> None:
        self.deleted: list[str] = []

    def get(self, name: str) -> Any:
        return SimpleNamespace(create_time="2026-10-15T10:00:00+00:00",
                               expire_time="2026-10-16T10:00:00+00:00",
                               usage_metadata=SimpleNamespace(
                                   total_token_count=CACHED_PER_RESPONSE))

    def delete(self, name: str) -> None:
        self.deleted.append(name)


def test_process_pass_sends_merges_and_deletes_its_cache(world: SimpleNamespace) -> None:
    client = SimpleNamespace(caches=FakeCaches())
    sent: list[list[str]] = []

    def fake_detector(cmd: list[str], log_path: Path) -> int:
        """Write what the detector writes for a top-up that recovers 2 of 3."""
        sent.append(cmd)
        manifest = json.loads(Path(cmd[cmd.index("--manifest") + 1]).read_text())
        out_dir = Path(cmd[cmd.index("--output-dir") + 1])
        write_topup(world.spec, out_dir, manifest[:2], manifest[2:])
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text("  Submitted batch job: batches/fake-job\n"
                            "  Accepting partial result: 1 tile(s) failed\n"
                            "  Released request file files/fake-upload (job terminal)\n")
        return 2

    work = world.tmp / "work"
    entry = tb.process_pass(world.spec, world.failed, work, run_command=fake_detector,
                            client=client, archive_dir=world.archive,
                            log_dir=world.tmp / "logs", full_manifest=world.full)
    assert entry["merged"] is True, entry
    assert len(sent) == 1 and "--dry-run" not in sent[0]
    assert entry["batch_job"] == "batches/fake-job"
    assert entry["request_file"] == "files/fake-upload"
    assert client.caches.deleted == [CACHE]
    assert entry["context_cache"]["deleted_at"]
    assert entry["recovered"] == sorted(world.failed[:2])
    assert entry["still_failing"] == [world.failed[2]]
    assert any(re.search("partial", line, re.I) for line in entry["log_failure_lines"])
    assert entry["cost_usd"]["batch_tokens_usd"] > 0
    assert entry["cost_usd"]["cache_estimate_usd"] > 0
    raw = world.archive / tb.RAW_ARCHIVE_SUBDIR / world.spec.archive_name
    assert {p.suffix for p in raw.iterdir()} == {".json", ".geojson"}
    assert (raw / f"{world.spec.corner}__run_{world.spec.run}.json").exists()
    meta = json.loads(next(world.spec.pass_dir.glob("*.meta.json")).read_text())
    assert meta["recovery_history"][-1]["batch_job_name"] == "batches/fake-job"
    assert meta["recovery_history"][-1]["context_cache"] == CACHE

    # A second run refuses to re-send, and the plan now skips the pass.
    with pytest.raises(tb.TopupError, match="already holds"):
        tb.process_pass(world.spec, world.failed, work, run_command=fake_detector,
                        client=client, archive_dir=world.archive,
                        log_dir=world.tmp / "logs", full_manifest=world.full)
    todo, untouched = tb.plan([world.spec], {world.spec.key: 3})
    assert todo == [] and "already topped up" in untouched[0]


def test_the_log_parser_matches_failures_in_any_case() -> None:
    info = tb.parse_detector_log("ERROR - Batch chunk 1/1 failed to lodge\n"
                                 "Traceback (most recent call last):\n"
                                 "Completeness gap: 3 tiles\nall fine\n")
    assert len(info["failure_lines"]) == 3
    assert info["batch_jobs"] == [] and info["request_files"] == []
