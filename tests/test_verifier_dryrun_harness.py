"""
Tests for ``scripts/verifier_dryrun_harness.py`` — the API-free verifier rehearsal.

The harness installs process-wide guards (sockets blocked, the SDK client
stubbed), so every end-to-end test runs it in a subprocess on a two-candidate
synthetic crop set. The tests pin the claims Stage 2 relies on:

- ``run_pv.py verify --mode batch --dry-run`` builds one request per
  candidate and returns WITHOUT constructing a client (zero stub instances,
  zero breaches);
- the real-time capture sees the request the real-time path sends (and the
  stub counter does register a construction, so the batch zero is evidence);
- the comparison names the fields that differ, with the content fields kept
  apart from representation-only ones.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.verifier_dryrun_harness import compare_requests  # noqa: E402

pytestmark = pytest.mark.tier1

HARNESS = PROJECT_ROOT / "scripts" / "verifier_dryrun_harness.py"
CONFIG = PROJECT_ROOT / "prompts" / "configs" / "verify_adversarial-text.json"


def _crops(tmp_path: Path) -> Path:
    """Two candidates with distinct tiny PNG crops; no source_geojson."""
    from PIL import Image

    crops = tmp_path / "crops"
    (crops / "crops").mkdir(parents=True)
    cands = []
    for i, colour in enumerate(((200, 10, 10), (10, 200, 10))):
        Image.new("RGB", (8, 8), colour).save(crops / "crops" / f"candidate_{i:05d}.png")
        cands.append({"candidate_id": i, "crop_file": f"crops/candidate_{i:05d}.png",
                      "source_tile": "t.png", "properties": {}})
    (crops / "candidate_manifest.json").write_text(json.dumps(
        {"version": "2.0", "candidates": cands}))
    return crops


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HARNESS)] + args, capture_output=True,
                          text=True, cwd=PROJECT_ROOT, timeout=300)


def _verify_args(crops: Path, out: Path, mode: str) -> list[str]:
    return ["--crops-dir", str(crops), "--verifier-config", str(CONFIG),
            "--output-dir", str(out), "--mode", mode, "--temperature", "0.0"]


def test_batch_dry_run_constructs_no_client(tmp_path: Path) -> None:
    crops = _crops(tmp_path)
    out = tmp_path / "out"
    summary = tmp_path / "b.json"
    proc = _run(["batch", "--summary-json", str(summary), "--first", "2", "--"]
                + _verify_args(crops, out, "batch")
                + ["--dry-run", "--model", "gemini-3-flash-preview"])
    assert proc.returncode == 0, proc.stdout + proc.stderr
    s = json.loads(summary.read_text())
    assert s["stub_client_instances"] == 0 and s["breaches"] == []
    b = s["batch"]
    assert b["n_lines"] == 2 and b["keys_match_manifest"]
    assert len(b["elided_signatures"]) == 1
    first = b["first_requests"][0]
    assert first["temperature"] == 0.0 and first["thinking_level"] == "MINIMAL"
    assert first["safety_settings"] is None
    # The request file is deleted after summary.
    assert not list(out.glob("verifier_requests*.jsonl"))


def test_batch_mode_refuses_a_live_invocation(tmp_path: Path) -> None:
    crops = _crops(tmp_path)
    proc = _run(["batch", "--"] + _verify_args(crops, tmp_path / "out", "batch"))
    assert proc.returncode != 0 and "--dry-run" in proc.stderr


def test_realtime_capture_and_compare(tmp_path: Path) -> None:
    crops = _crops(tmp_path)
    b_json, r_json = tmp_path / "b.json", tmp_path / "r.json"
    assert _run(["batch", "--summary-json", str(b_json), "--first", "2", "--"]
                + _verify_args(crops, tmp_path / "ob", "batch")
                + ["--dry-run"]).returncode == 0
    proc = _run(["realtime", "--served", "gemini-3-flash-preview",
                 "--summary-json", str(r_json), "--"]
                + _verify_args(crops, tmp_path / "or", "realtime")
                + ["--workers", "1"])
    assert proc.returncode == 0, proc.stdout + proc.stderr
    r = json.loads(r_json.read_text())
    # The counter registers a construction: the batch zero is evidence.
    assert r["stub_client_instances"] == 1 and r["breaches"] == []
    assert r["realtime_model"] == ["gemini-3-flash-preview"]
    assert sorted(x["key"] for x in r["realtime_requests"]) == [
        "candidate_00000", "candidate_00001"]
    result = compare_requests(json.loads(b_json.read_text()), r)
    assert all(row["captured"] for row in result["rows"])
    # Same parts, instruction, temperature, thinking, budget and format; the
    # real-time call sends safety settings and a tier, the batch line neither.
    assert result["content_diff_fields"] == ["safety_settings", "service_tier"]
    assert "parts" in result["rows"][0]["same"]


def test_compare_flags_a_temperature_difference() -> None:
    base = {"key": "candidate_00000", "temperature": 0.0, "parts": [["text", "a", "a"]],
            "roles": ["user"]}
    batch = {"batch": {"first_requests": [base]}}
    realtime = {"realtime_requests": [dict(base, temperature=0.7, roles=[None])]}
    result = compare_requests(batch, realtime)
    assert result["content_diff_fields"] == ["temperature"]
    assert result["representation_diff_fields"] == ["roles"]


@pytest.mark.parametrize("flags, pin", [
    (["--model", "gemini-3-flash-preview"], "SIGF_G3"),
    (["--model", "gemini-3.7-flash", "--thinking-level", "low"], "SIGF_G37"),
])
def test_full_request_signature_matches_the_launcher_pin(tmp_path: Path, flags: list[str],
                                                          pin: str) -> None:
    """The full signature hashes every request field but the key and crop bytes.

    It is crop-independent by construction, so synthetic crops give the value
    the launcher pins (Stage 2 audit nit: the five-field signature would not
    see a generation-config field added to the builder).
    """
    import re

    crops = _crops(tmp_path)
    summary = tmp_path / "b.json"
    proc = _run(["batch", "--summary-json", str(summary), "--first", "1", "--"]
                + _verify_args(crops, tmp_path / "out", "batch") + ["--dry-run"] + flags)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    b = json.loads(summary.read_text())["batch"]
    assert b["generation_config_keys"] == {
        "max_output_tokens,response_mime_type,temperature,thinking_config": 2}
    launcher = (PROJECT_ROOT / "scripts" / "modality-bridge-2026-10-07-stage2.sh").read_text()
    pinned = re.search(rf"^{pin}=([0-9a-f]{{64}})$", launcher, re.M).group(1)
    assert list(b["full_elided_signatures"]) == [pinned]


def test_full_signature_moves_when_a_request_field_is_added() -> None:
    from scripts.verifier_dryrun_harness import full_elided_signature

    line = {"key": "candidate_00000", "request": {
        "contents": [{"role": "user", "parts": [
            {"text": "label"}, {"inline_data": {"mime_type": "image/png", "data": "AAA"}}]}],
        "generation_config": {"temperature": 0.0}}}
    other_crop = json.loads(json.dumps(line))
    other_crop["request"]["contents"][0]["parts"][1]["inline_data"]["data"] = "BBB"
    other_crop["key"] = "candidate_00001"
    assert full_elided_signature(line) == full_elided_signature(other_crop)
    extra = json.loads(json.dumps(line))
    extra["request"]["generation_config"]["top_p"] = 0.9
    assert full_elided_signature(line) != full_elided_signature(extra)
