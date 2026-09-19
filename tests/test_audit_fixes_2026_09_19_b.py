"""Audit fixes of 2026-09-19, second batch: r2 merge helpers, the watcher's
missing-log and boundary cases, the normaliser's CLI wiring, the provenance
sidecar's --write wiring, the flex warning, and the override call sites.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts import gemini37_image_55map_r2 as r2  # noqa: E402
from scripts import normalise_pass_layout as npl  # noqa: E402
from scripts import wait_for_run as wfr  # noqa: E402
from scripts.emit_union_pass_provenance import main as emit_main  # noqa: E402
from scripts.lib_batch_api import recommend_execution_mode  # noqa: E402

pytestmark = pytest.mark.tier1


# --- r2: a filtered sweep or materialisation keeps the other rungs ---------

def test_merge_cells_keeps_other_rungs_and_replaces_same_labels():
    existing = [{"label": "IMG-ARM1-K1-carried", "k": 1},
                {"label": "IMG-ARM2-K3-carried", "k": 3},
                {"label": "IMG-ARM2-K5-carried", "k": 5, "stale": True}]
    new = [{"label": "IMG-ARM2-K5-carried", "k": 5}, {"label": "IMG-ARM1-K5-carried", "k": 5}]
    merged = r2.merge_cells(existing, new)
    labels = [c["label"] for c in merged]
    assert labels == ["IMG-ARM1-K1-carried", "IMG-ARM2-K3-carried",
                      "IMG-ARM2-K5-carried", "IMG-ARM1-K5-carried"]
    assert "stale" not in merged[2]


def test_load_sweeps_keeps_existing_rungs(tmp_path):
    p = tmp_path / "sweeps.json"
    p.write_text(json.dumps({"buffer_m": 50, "rungs": {"IMG-ARM1-K1": {"n_sweep_points": 3}}}))
    s = r2.load_sweeps(p)
    assert s["rungs"]["IMG-ARM1-K1"]["n_sweep_points"] == 3
    fresh = r2.load_sweeps(tmp_path / "none.json")
    assert fresh["rungs"] == {} and fresh["buffer_m"] == r2.BUFFER_M


def test_stages_use_the_merge_helpers():
    src = (ROOT / "scripts" / "gemini37_image_55map_r2.py").read_text()
    assert "sweeps = load_sweeps(sweeps_path)" in src
    assert "merged = merge_cells(existing, cells)" in src
    assert 'f"{CAMPAIGN.prefix}-ARM2-K3-carried"' in src


# --- wait_for_run -----------------------------------------------------------

def test_a_log_that_never_appears_is_stale_not_forever(tmp_path):
    log = tmp_path / "never.log"
    t = [1000.0]

    def clock():
        return t[0]

    def sleep(s):
        t[0] += s

    state = wfr.wait_for_terminal(log, stale_seconds=100, poll_seconds=30,
                                  sleep=sleep, clock=clock)
    assert state == "stale"
    assert t[0] - 1000.0 <= 150


def test_one_failed_tile_is_partial():
    assert wfr.classify_log("Tiles processed: 9172\nTiles failed: 1\n") == "partial"
    assert wfr.classify_log("Tiles processed: 9173\nTiles failed: 0\n") == "success"


def test_a_failure_count_before_the_completion_line_does_not_downgrade_it():
    text = "Tiles failed: 3\nretrying\nBatch complete. Estimated cost: $1\nTiles processed: 9\n"
    assert wfr.classify_log(text) == "success"


def test_in_progress_batch_log_with_per_chunk_completion_lines_is_running():
    """The real log prints an indented 'Batch complete: 4000 tiles, ...' per
    chunk; only the unindented 'Batch complete.' at the end is terminal."""
    text = ("Chunking: 24561 tiles into 7 batch jobs\n"
            "--- Chunk 1/7 (tiles 1–4000) ---\n"
            "  Batch complete: 4000 tiles, 2755 detections, 0 failed, $32.8949\n"
            "--- Chunk 2/7 (tiles 4001–8000) ---\n")
    assert wfr.classify_log(text) == "running"


def test_extra_markers_extend_the_defaults_through_the_parser():
    table = wfr._parse_markers(["success=^ALL ARMS DONE"])
    assert r"^Batch complete\." in table["success"]
    assert "^ALL ARMS DONE" in table["success"]
    with pytest.raises(SystemExit):
        wfr._parse_markers(["success="])


@pytest.mark.parametrize("text,code", [
    ("Traceback (most recent call last):\nKeyError\n", 3),
    ("Batch complete.\nTiles processed: 3\n", 0),
])
def test_main_exit_status_follows_the_state(tmp_path, text, code):
    log = tmp_path / "run.log"
    log.write_text(text)
    assert wfr.main(["--log", str(log), "--poll", "0"]) == code


def test_main_reads_a_pidfile_and_reports_stopped(tmp_path):
    log = tmp_path / "run.log"
    log.write_text("working\n")
    import subprocess
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    proc.wait()
    (tmp_path / "pid").write_text(str(proc.pid))
    rc = wfr.main(["--log", str(log), "--pidfile", str(tmp_path / "pid"), "--poll", "0"])
    assert rc == 5


def test_stale_via_mtime_still_works(tmp_path):
    log = tmp_path / "run.log"
    log.write_text("x\n")
    old = time.time() - 7200
    os.utime(log, (old, old))
    assert wfr.wait_for_terminal(log, stale_seconds=3600, sleep=lambda s: None) == "stale"


# --- normaliser CLI wiring --------------------------------------------------

def _batch_layout(root: Path, stems: list[str]) -> Path:
    d = root / "detect_brief-text-image" / "run_1"
    d.mkdir(parents=True)
    for stem in stems:
        (d / f"{stem}.geojson").write_text('{"type":"FeatureCollection","features":[]}')
        (d / f"{stem}.meta.json").write_text("{}")
        (d / f"{stem}.tiles.json").write_text('{"total_tiles":1,"completed":["a.png"]}')
    return root


def test_cli_refuses_an_ambiguous_layout_instead_of_sorting(tmp_path):
    src = _batch_layout(tmp_path / "src", ["detections_x_run01", "detections_x_run02"])
    with pytest.raises(ValueError, match="sort order"):
        npl.main(["--src", str(src), "--pool", str(tmp_path / "pool"), "--run", "4",
                  "--version", "detect_brief-text-image", "--model", "gemini-3.7-flash",
                  "--date", "2026-09-17"])
    assert not (tmp_path / "pool").exists()


def test_cli_names_the_pool_file_from_version_then_model(tmp_path):
    src = _batch_layout(tmp_path / "src", ["detections_x_run01"])
    rc = npl.main(["--src", str(src), "--pool", str(tmp_path / "pool"), "--run", "4",
                   "--version", "detect_brief-text-image", "--model", "gemini-3.7-flash",
                   "--date", "2026-09-17"])
    assert rc == 0
    names = sorted(p.name for p in (tmp_path / "pool" / "run_4").iterdir())
    assert names[0] == "detections-detect_brief-text-image-3.7-flash-2026-09-17.geojson"


# --- provenance sidecar --write wiring ------------------------------------

def _campaign(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "outputs" / "campaign"
    cell = "g384_ov192_55map_g37img"
    for i in (1, 2):
        d = root / cell / f"run_{i}"
        d.mkdir(parents=True)
        (d / f"detections-run_{i}.geojson").write_text(f'{{"pass": {i}}}')
    union = root / "verifier" / cell / "union_k2.geojson"
    union.parent.mkdir(parents=True)
    union.write_text(json.dumps({"type": "FeatureCollection", "features": [1, 2]}))
    return root, cell


def test_sidecar_is_written_only_with_write(tmp_path):
    root, cell = _campaign(tmp_path)
    dest = root / "verifier" / cell / "union_k2_pass_provenance.json"
    assert emit_main(["--root", str(root), "--cell", cell, "--k", "2"]) == 0
    assert not dest.exists()
    assert emit_main(["--root", str(root), "--cell", cell, "--k", "2", "--write"]) == 0
    assert dest.exists()
    assert json.loads(dest.read_text())["union_feature_count"] == 2


# --- the flex warning -------------------------------------------------------

def test_flex_warning_fires_for_37_and_38_only_on_flex():
    assert recommend_execution_mode("gemini-3.7-flash", "batch") is None
    assert recommend_execution_mode("gemini-3-flash-preview", "realtime") is None
    warn = recommend_execution_mode("gemini-3.7-flash", "realtime")
    assert warn and "503" in warn
    assert recommend_execution_mode("gemini-3.8-flash", "realtime")


# --- the override call sites (erratum E42) --------------------------------

def test_override_call_sites_pass_the_overrides_to_the_tracker():
    a = (ROOT / "scripts" / "4_detect_mounds_batch.py").read_text()
    b = (ROOT / "scripts" / "run_pv.py").read_text()
    assert a.count("cli_overrides=") >= 1 and "cli_overrides={}" not in a
    assert b.count("cli_overrides=") >= 2 and "cli_overrides={}" not in b
