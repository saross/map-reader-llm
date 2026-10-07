"""
Tests for ``scripts/modality-bridge-2026-10-07-stage2.sh`` — Run B's Stage 2 launcher.

Pins what the card commits to without running anything that could spend:
the ten planned verifier legs and their exact flags (``plan``), the refusal
of an unplanned leg or an unknown arm, the refusal of an arm whose passes
have not landed, the launch wrapper's exit capture (``$?`` taken before
``$(date)``, which would otherwise report date's status), and that the
request signatures the launcher enforces are the ones the rehearsal record
holds. The full refusal and launch-mechanics run against stand-in passes
is recorded in the Stage 2 card (it needs the original passes and crops).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT_ROOT / "scripts" / "modality-bridge-2026-10-07-stage2.sh"
RECORD = PROJECT_ROOT / "planning" / "modality-bridge-2026-10-07-stage2-rehearsal.json"

pytestmark = pytest.mark.tier1

LEGS = {"g3-text:g3", "g3-image:g3", "g37-text:g3", "g37-text:g37", "g37-image:g3",
        "g37-image:g37", "g37-image-cache:g3", "g37-image-cache:g37",
        "g3-text-temp1:g3", "g3-image-temp1:g3"}


def _run(*args: str, out: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, PY=sys.executable, OUT=str(out), SCRATCH=str(out / "scratch"))
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True,
                          cwd=PROJECT_ROOT, env=env, timeout=120)


def test_syntax() -> None:
    assert subprocess.run(["bash", "-n", str(SCRIPT)]).returncode == 0


def test_plan_lists_the_ten_legs_with_their_flags(tmp_path: Path) -> None:
    proc = _run("plan", out=tmp_path)
    assert proc.returncode == 0, proc.stderr
    verify = [ln for ln in proc.stdout.splitlines() if "run_pv.py verify" in ln]
    assert len(verify) == 10
    seen = set()
    for ln in verify:
        arm = re.search(r"--crops-dir \S+/([^/]+)/verifier/", ln).group(1)
        v = re.search(r"/verify_(g3|g37) ", ln).group(1)
        seen.add(f"{arm}:{v}")
        assert "--mode batch" in ln and "--temperature 0.0" in ln
        assert "--verifier-config prompts/configs/verify_adversarial-text.json" in ln
        assert "--dry-run" not in ln
        if v == "g3":
            assert "--model gemini-3-flash-preview" in ln and "--thinking-level" not in ln
        else:
            assert "--model gemini-3.7-flash --thinking-level low" in ln
    assert seen == LEGS
    # K = 10 unions for the two Gemini 3 D49 arms, K = 5 elsewhere; extraction
    # with the originals' rasters and tiles.
    assert "g3-text/verifier/detect_brief-text/union_k10.geojson" in proc.stdout
    assert "g3-text-temp1/verifier/detect_brief-text/union_k5.geojson" in proc.stdout
    extract = [ln for ln in proc.stdout.splitlines() if "run_pv.py extract" in ln]
    assert len(extract) == 7
    assert all("--tiles-dir inputs/tiles_384_ov192 --rasters-dir inputs/rasters" in ln
               for ln in extract)


def test_unplanned_leg_and_unknown_arm_are_refused(tmp_path: Path) -> None:
    proc = _run("verify", "g3-text:g37", out=tmp_path)
    assert proc.returncode == 2 and "not a planned leg" in proc.stderr
    assert _run("check", "g4-text", out=tmp_path).returncode == 2
    assert not (tmp_path / "stage2" / "logs").exists()


def test_arm_without_landed_passes_is_refused(tmp_path: Path) -> None:
    proc = _run("check", "g37-text", out=tmp_path)
    assert proc.returncode == 1 and "REFUSED" in proc.stdout


def test_launch_wrapper_captures_the_exit_status_first() -> None:
    text = SCRIPT.read_text()
    assert "rc=$?; echo \"=== $(date -Is) EXIT $rc\"" in text
    assert "echo $$ > \"$0\"" in text  # the pid is written from inside the job
    assert "< /dev/null &" in text


def test_logs_stay_out_of_the_stage1_log_directory() -> None:
    assert re.search(r"^ST2=\$\{ST2:-\$OUT/stage2\}$", SCRIPT.read_text(), re.M)


def test_signatures_match_the_rehearsal_record() -> None:
    text = SCRIPT.read_text()
    sig = {v: re.search(rf"^SIG_{v.upper()}=([0-9a-f]{{64}})$", text, re.M).group(1)
           for v in ("g3", "g37")}
    record = json.loads(RECORD.read_text())
    assert record["verifier_signatures"] == sig
