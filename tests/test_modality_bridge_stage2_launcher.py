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

Run C (2026-10-08) adds replicates (``REP=<n>``): the unset path keeps every
name; a replicate writes only ``verify_<v>_rep<n>`` and ``-rep<n>`` names,
refuses an unlanded leg and the build steps, and its rehearsal requires the
original leg's requests line for line (fail-closed without them).
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
    assert "< /dev/null 9>&- &" in text  # the launched leg drops the lock


def test_logs_stay_out_of_the_stage1_log_directory() -> None:
    assert re.search(r"^ST2=\$\{ST2:-\$OUT/stage2\}$", SCRIPT.read_text(), re.M)


def test_signatures_match_the_rehearsal_record() -> None:
    text = SCRIPT.read_text()
    sig = {v: re.search(rf"^SIG_{v.upper()}=([0-9a-f]{{64}})$", text, re.M).group(1)
           for v in ("g3", "g37")}
    full = {v: re.search(rf"^SIGF_{v.upper()}=([0-9a-f]{{64}})$", text, re.M).group(1)
            for v in ("g3", "g37")}
    record = json.loads(RECORD.read_text())
    assert record["verifier_signatures"] == sig
    assert record["verifier_full_signatures"] == full


# ---------------------------------------------------------------------------
# A1 and A4 (Stage 2 audit): relaunch and locking, through a test double
# ---------------------------------------------------------------------------

FAKE_PY = """#!/usr/bin/env bash
# Test double: a live `scripts/run_pv.py verify` is simulated (no API);
# every other call goes to the real interpreter.
if [ "${1:-}" = scripts/run_pv.py ] && [ "${2:-}" = verify ]; then
  sleep "${FAKE_DELAY:-2}"
  for i in $(seq 1 "${FAKE_CHUNKS:-1}"); do
    echo "INFO - Submitted batch job $i/${FAKE_CHUNKS:-1}: batches/new-$$-$i"
  done
  sleep "${FAKE_SLEEP:-3}"
  exit "${FAKE_RC:-0}"
fi
exec "$REAL_PY" "$@"
"""


def _double(tmp_path: Path) -> Path:
    fake = tmp_path / "fakepy.sh"
    fake.write_text(FAKE_PY)
    fake.chmod(0o755)
    return fake


def _sourced(script: str, out: Path, fake: Path, **env: str) -> subprocess.CompletedProcess:
    """Run *script* in a shell that has sourced the launcher (no dispatch)."""
    full = dict(os.environ, OUT=str(out), PY=str(fake), REAL_PY=sys.executable,
                LODGE_GAP="0", LODGE_POLL="1", WAIT_POLL="1", SCRATCH=str(out / "scratch"),
                **env)
    return subprocess.run(["bash", "-c", f'source "{SCRIPT}"\n{script}'],
                          capture_output=True, text=True, cwd=PROJECT_ROOT, env=full,
                          timeout=120)


def _stale_attempt(out: Path, name: str, lines: list[str]) -> Path:
    """A previous attempt's log and a dead pid in its pid file."""
    (out / "stage2" / "logs").mkdir(parents=True)
    (out / "stage2" / "pids").mkdir(parents=True)
    log = out / "stage2" / "logs" / f"{name}.log"
    log.write_text("\n".join(lines) + "\n")
    dead = subprocess.Popen(["true"])
    dead.wait()
    (out / "stage2" / "pids" / f"{name}.pid").write_text(f"{dead.pid}\n")
    return log


def test_relaunch_after_a_storage_refusal_reads_only_its_own_attempt(tmp_path: Path) -> None:
    """Audit A1, test T1: the first attempt refused at the storage preflight."""
    out = tmp_path / "out"
    name = "verify-g37-text-g3"
    _stale_attempt(out, name, [
        "=== 2026-10-08T00:00:00+00:00 LAUNCH verify-g37-text-g3: ...",
        "ERROR - Batch verification failed: FileStorageCapExceeded (fake)",
        "=== 2026-10-08T00:00:05+00:00 EXIT 1"])
    proc = _sourced("launch_leg g37-text g3 791 && wait_leg g37-text:g3", out,
                    _double(tmp_path), FAKE_DELAY="2", FAKE_SLEEP="2")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "LODGING FAILED" not in proc.stdout
    assert re.search(r"submitted \(batches/new-\d+-1 \)", proc.stdout)
    logs = sorted((out / "stage2" / "logs").glob(f"{name}.log*"))
    assert len(logs) == 2  # the earlier attempt's log is kept, renamed
    current = (out / "stage2" / "logs" / f"{name}.log").read_text()
    assert "Batch verification failed" not in current
    assert re.search(r"^=== .* EXIT 0$", current, re.M)
    old = next(p for p in logs if p.name != f"{name}.log").read_text()
    assert "Batch verification failed" in old and "EXIT 1" in old


def test_relaunch_waits_for_its_own_submissions(tmp_path: Path) -> None:
    """A two-chunk leg's earlier Submitted lines must not satisfy the new count."""
    out = tmp_path / "out"
    _stale_attempt(out, "verify-g3-image-g3", [
        "INFO - Submitted batch job 1/2: batches/old-1",
        "INFO - Submitted batch job 2/2: batches/old-2",
        "=== 2026-10-08T00:00:05+00:00 EXIT 1"])
    proc = _sourced("launch_leg g3-image g3 4065", out, _double(tmp_path),
                    FAKE_CHUNKS="2", FAKE_DELAY="2", FAKE_SLEEP="1")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "batches/old" not in proc.stdout
    assert re.search(r"submitted \(batches/new-\d+-1 batches/new-\d+-2 \)", proc.stdout)
    # The started pid is the new attempt's, not the dead one.
    assert re.search(r"started pid \d+", proc.stdout)


def test_wait_is_not_fooled_by_an_earlier_exit_line(tmp_path: Path) -> None:
    out = tmp_path / "out"
    _stale_attempt(out, "verify-g37-text-g37", ["=== 2026-10-08T00:00:05+00:00 EXIT 1"])
    proc = _sourced("launch_leg g37-text g37 791 && wait_leg g37-text:g37; echo WAIT=$?",
                    out, _double(tmp_path), FAKE_DELAY="1", FAKE_SLEEP="3")
    assert "WAIT=0" in proc.stdout, proc.stdout + proc.stderr


def test_wait_uses_an_hour_staleness_window() -> None:
    assert "--stale-seconds 3600" in SCRIPT.read_text()
    assert "--stale-seconds 90000" not in SCRIPT.read_text()


def test_a_second_writing_command_is_refused_while_one_holds_the_lock(tmp_path: Path) -> None:
    import fcntl

    out = tmp_path / "out"
    (out / "stage2").mkdir(parents=True)
    with open(out / "stage2" / "stage2.lock", "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for cmd in (["verify", "g37-text:g3"], ["prepare", "g37-text"],
                    ["rehearse", "g37-text:g3"]):
            proc = _run(*cmd, out=out)
            assert proc.returncode == 1 and "holds" in proc.stderr, (cmd, proc.stderr)
    # Read-only subcommands do not take the lock.
    with open(out / "stage2" / "stage2.lock", "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert _run("plan", out=out).returncode == 0


def test_a_launched_leg_does_not_hold_the_lock(tmp_path: Path) -> None:
    out = tmp_path / "out"
    script = ('mkdir -p "$OUT/stage2"; exec 9> "$OUT/stage2/stage2.lock"; flock -n 9; '
              'launch_leg g37-text g3 791; exec 9>&-; '
              'flock -n "$OUT/stage2/stage2.lock" true && echo LOCK=free || echo LOCK=held')
    proc = _sourced(script, out, _double(tmp_path), FAKE_DELAY="1", FAKE_SLEEP="5")
    assert "LOCK=free" in proc.stdout, proc.stdout + proc.stderr


def test_launch_leg_refuses_while_the_previous_attempt_is_alive(tmp_path: Path) -> None:
    out = tmp_path / "out"
    (out / "stage2" / "pids").mkdir(parents=True)
    live = subprocess.Popen(["sleep", "30"])
    try:
        (out / "stage2" / "pids" / "verify-g37-text-g3.pid").write_text(f"{live.pid}\n")
        proc = _sourced("launch_leg g37-text g3 791", out, _double(tmp_path))
        assert proc.returncode == 1 and "still running" in proc.stdout
        assert not (out / "stage2" / "logs" / "verify-g37-text-g3.log").exists()
    finally:
        live.kill()


# ---------------------------------------------------------------------------
# Re-check R1 and nits: per-leg band override, no-union message, repair all
# ---------------------------------------------------------------------------


def _build_record(out: Path, arm: str, version: str, k: int, n: int) -> None:
    d = out / arm / "verifier" / version
    d.mkdir(parents=True, exist_ok=True)
    (d / f"union_k{k}.build.json").write_text(json.dumps({"union_features": n}))


def test_verify_without_a_union_says_so(tmp_path: Path) -> None:
    proc = _run("verify", "g37-text:g3", out=tmp_path)
    assert proc.returncode == 1
    assert "no union built yet" in proc.stdout
    assert "outside the review band" not in proc.stdout


def test_a_blanket_band_ok_is_refused(tmp_path: Path) -> None:
    _build_record(tmp_path, "g37-text", "detect_brief-text", 5, 950)  # out of band
    env_run = lambda band_ok, leg: subprocess.run(  # noqa: E731
        ["bash", str(SCRIPT), "verify", leg], capture_output=True, text=True,
        cwd=PROJECT_ROOT, timeout=120,
        env=dict(os.environ, PY=sys.executable, OUT=str(tmp_path), BAND_OK=band_ok,
                 SCRATCH=str(tmp_path / "scratch")))
    proc = env_run("1", "g37-text:g3")
    assert proc.returncode == 1 and "BAND_OK must name legs" in proc.stdout
    # Naming another leg does not let this one through.
    proc = env_run("g37-text:g37", "g37-text:g3")
    assert proc.returncode == 1 and "BAND_OK=g37-text:g3 overrides" in proc.stdout
    assert not (tmp_path / "stage2" / "logs" / "verify-g37-text-g3.log").exists()


def _repair_leg_dir(out: Path, v: str, text: str) -> Path:
    leg = out / "g37-text" / "verifier" / "detect_brief-text" / f"verify_{v}"
    leg.mkdir(parents=True)
    results = {"candidate_00000": {"mound_probability": 0.0, "reasoning": "PARSE_ERROR: x"}}
    (leg / "probabilities.json").write_text(json.dumps({"results": results}))
    row = {"key": "candidate_00000",
           "response": {"candidates": [{"content": {"parts": [{"text": text}]}}]}}
    (leg / "batch_results.jsonl").write_text(json.dumps(row) + "\n")
    (leg / "run.meta.json").write_text("{}")
    return leg


def test_repair_all_goes_on_past_a_leg_it_cannot_finish(tmp_path: Path) -> None:
    _repair_leg_dir(tmp_path, "g3", "not JSON")                     # unrecoverable
    _repair_leg_dir(tmp_path, "g37", '{"mound_probability": 0.3}\n}')  # recoverable
    proc = _run("repair", "g37-text:g3", "g37-text:g37", out=tmp_path)
    assert proc.returncode == 1
    assert "REPAIR INCOMPLETE for: g37-text:g3" in proc.stdout
    repaired = (tmp_path / "g37-text" / "verifier" / "detect_brief-text"
                / "verify_g37_repaired" / "probabilities.json")
    assert json.loads(repaired.read_text())["results"]["candidate_00000"][
        "mound_probability"] == 0.3


# ---------------------------------------------------------------------------
# Run C (2026-10-08): replicates, REP=<n>
# ---------------------------------------------------------------------------


def _run_rep(rep: str, *args: str, out: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, PY=sys.executable, OUT=str(out), SCRATCH=str(out / "scratch"),
               REP=rep)
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True,
                          cwd=PROJECT_ROOT, env=env, timeout=120)


def test_rep_unset_leaves_every_name_unchanged(tmp_path: Path) -> None:
    script = ('for x in "g37-text g3" "g3-image g3"; do set -- $x; '
              'echo "$(leg_dir "$1" "$2") $(leg_name "$1" "$2") [$(sfx)]"; done')
    proc = _sourced(script, tmp_path, _double(tmp_path))
    assert proc.returncode == 0, proc.stderr
    lines = proc.stdout.splitlines()
    assert lines[0].endswith("/g37-text/verifier/detect_brief-text/verify_g3 "
                             "verify-g37-text-g3 []")
    assert lines[1].endswith("/verify_g3 verify-g3-image-g3 []")
    proc = _sourced(script, tmp_path, _double(tmp_path), REP="3")
    lines = proc.stdout.splitlines()
    assert lines[0].endswith("/verify_g3_rep3 verify-g37-text-g3-rep3 [-rep3]")


def test_rep_plan_sends_each_leg_to_its_replicate_directory(tmp_path: Path) -> None:
    proc = _run_rep("2", "plan", out=tmp_path)
    assert proc.returncode == 0, proc.stderr
    verify = [ln for ln in proc.stdout.splitlines() if "run_pv.py verify" in ln]
    assert len(verify) == 10
    seen = set()
    for ln in verify:
        arm = re.search(r"--crops-dir \S+/([^/]+)/verifier/", ln).group(1)
        v = re.search(r"/verify_(g3|g37)_rep2 ", ln).group(1)
        seen.add(f"{arm}:{v}")
        # The same crops, config, mode and temperature as the original legs.
        assert ln.split("--crops-dir ", 1)[1].split()[0].endswith("/crops")
        assert "--mode batch" in ln and "--temperature 0.0" in ln
        assert "--verifier-config prompts/configs/verify_adversarial-text.json" in ln
    assert seen == LEGS
    # Unset, the original directories (the existing plan test pins the rest).
    assert not re.search(r"/verify_g37?_rep\d", _run("plan", out=tmp_path).stdout)


@pytest.mark.parametrize("rep", ["1", "0", "x", "2a", "-2"])
def test_rep_must_be_an_integer_of_two_or_more(tmp_path: Path, rep: str) -> None:
    proc = _run_rep(rep, "plan", out=tmp_path)
    assert proc.returncode == 2 and f"REFUSED: REP={rep}" in proc.stderr


@pytest.mark.parametrize("cmd", [["union", "g37-text"], ["extract", "g37-text"],
                                 ["prepare", "all"], ["validate-chain"], ["anchor-gate"]])
def test_rep_refuses_the_build_steps(tmp_path: Path, cmd: list[str]) -> None:
    proc = _run_rep("2", *cmd, out=tmp_path)
    assert proc.returncode == 2 and "REP applies to verifier legs" in proc.stderr
    assert not (tmp_path / "stage2").exists()


def test_replicate_launch_and_wait_use_only_their_own_names(tmp_path: Path) -> None:
    """A replicate never rotates, reads or overwrites the original leg's log or pid."""
    out = tmp_path / "out"
    orig = _stale_attempt(out, "verify-g37-text-g3", [
        "INFO - Submitted batch job 1/1: batches/original-1",
        "=== 2026-10-07T20:07:37+00:00 EXIT 0"])
    before = orig.read_text()
    orig_pid = (out / "stage2" / "pids" / "verify-g37-text-g3.pid").read_text()
    proc = _sourced("launch_leg g37-text g3 789 && wait_leg g37-text:g3; echo WAIT=$?", out,
                    _double(tmp_path), REP="2", FAKE_DELAY="1", FAKE_SLEEP="2")
    assert "WAIT=0" in proc.stdout, proc.stdout + proc.stderr
    assert "batches/original" not in proc.stdout
    logs = out / "stage2" / "logs"
    assert orig.read_text() == before
    assert sorted(p.name for p in logs.iterdir()) == ["verify-g37-text-g3-rep2.log",
                                                      "verify-g37-text-g3.log"]
    rep_log = (logs / "verify-g37-text-g3-rep2.log").read_text()
    assert "/verify_g3_rep2 " in rep_log
    assert re.search(r"^=== .* EXIT 0$", rep_log, re.M)
    assert (out / "stage2" / "pids" / "verify-g37-text-g3-rep2.pid").exists()
    assert (out / "stage2" / "pids" / "verify-g37-text-g3.pid").read_text() == orig_pid


def test_replicate_verify_refuses_a_leg_that_has_not_landed(tmp_path: Path) -> None:
    _build_record(tmp_path, "g37-text", "detect_brief-text", 5, 789)  # in band
    proc = _run_rep("2", "verify", "g37-text:g3", out=tmp_path)
    assert proc.returncode == 1 and "re-verifies a landed leg" in proc.stdout
    assert not (tmp_path / "stage2" / "logs" / "verify-g37-text-g3-rep2.log").exists()
    # A replicate that has itself landed is skipped, never re-lodged.
    rep = tmp_path / "g37-text" / "verifier" / "detect_brief-text" / "verify_g3_rep2"
    rep.mkdir(parents=True)
    (rep / "probabilities.json").write_text("{}")
    proc = _run_rep("2", "verify", "g37-text:g3", out=tmp_path)
    assert proc.returncode == 0 and "already verified" in proc.stdout


def test_replicate_repair_writes_its_own_copy(tmp_path: Path) -> None:
    leg = _repair_leg_dir(tmp_path, "g37", '{"mound_probability": 0.4}\n}')
    leg.rename(leg.with_name("verify_g37_rep2"))
    proc = _run_rep("2", "repair", "g37-text:g37", out=tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    vroot = tmp_path / "g37-text" / "verifier" / "detect_brief-text"
    assert (vroot / "verify_g37_rep2_repaired" / "probabilities.json").exists()
    assert not (vroot / "verify_g37_repaired").exists()


def test_replicate_status_names_the_replicate_legs(tmp_path: Path) -> None:
    proc = _run_rep("3", "status", out=tmp_path)
    assert proc.returncode == 0
    assert "verify-g3-text-g3-rep3" in proc.stdout
    assert "verify-g3-text-g3 " not in proc.stdout


def test_estimate_labels_a_replicate_and_keeps_the_cost(tmp_path: Path) -> None:
    rep = _run_rep("2", "estimate", out=tmp_path)
    orig = _run("estimate", out=tmp_path)
    assert rep.returncode == orig.returncode == 0
    assert "g37-text:g37 rep2" in rep.stdout and "total, replicate 2" in rep.stdout
    total = [ln.split("US$")[1] for ln in rep.stdout.splitlines() if ln.startswith("total")]
    assert total == [ln.split("US$")[1] for ln in orig.stdout.splitlines()
                     if ln.startswith("total")]


# The rehearsal under REP, with the harness and the union check replaced by a
# double: it must compare the replicate's requests with the original leg's,
# refuse a difference, fail closed without the original's file, and delete
# its own scratch request file on every path.
FAKE_HARNESS_PY = """#!/usr/bin/env bash
case "${1:-}" in
  scripts/modality_bridge_union.py) exit 0 ;;
  scripts/verifier_dryrun_harness.py)
    rec=""; od=""; prev=""
    for a in "$@"; do
      [ "$prev" = --summary-json ] && rec=$a
      [ "$prev" = --output-dir ] && od=$a
      prev=$a
    done
    mkdir -p "$od" "$(dirname "$rec")"
    cp "$FAKE_REQ" "$od/verifier_requests.jsonl"
    printf '{"batch": {"n_lines": 2, "elided_signatures": {"%s": 2},' "$FAKE_SIG" > "$rec"
    printf ' "full_elided_signatures": {"%s": 2}, "generation_config_keys": {}}}' \\
      "$FAKE_SIGF" >> "$rec"
    exit 0 ;;
esac
exec "$REAL_PY" "$@"
"""


def _request_line(key: str, temperature: float) -> str:
    return json.dumps({"key": key, "request": {
        "contents": [{"role": "user", "parts": [{"text": "x"},
                                                {"inline_data": {"data": "AAAA"}}]}],
        "generation_config": {"temperature": temperature}}})


def _rehearse_rep(tmp_path: Path, replicate_temp: float,
                  original: bool = True) -> tuple[subprocess.CompletedProcess, Path]:
    out = tmp_path / "out"
    leg = out / "g37-text" / "verifier" / "detect_brief-text" / "verify_g3"
    leg.mkdir(parents=True)
    if original:
        (leg / "verifier_requests.jsonl").write_text(
            "\n".join(_request_line(f"candidate_0000{i}", 0.0) for i in range(2)) + "\n")
    fake_req = tmp_path / "replicate.jsonl"
    fake_req.write_text("\n".join(_request_line(f"candidate_0000{i}", replicate_temp)
                                  for i in range(2)) + "\n")
    double = tmp_path / "fakeharness.sh"
    double.write_text(FAKE_HARNESS_PY)
    double.chmod(0o755)
    text = SCRIPT.read_text()
    sig = re.search(r"^SIG_G3=([0-9a-f]{64})$", text, re.M).group(1)
    sigf = re.search(r"^SIGF_G3=([0-9a-f]{64})$", text, re.M).group(1)
    proc = _sourced("check() { return 0; }; provenance() { return 0; }; "
                    "rehearse g37-text g3; echo RC=$?", out, double, REP="2",
                    FAKE_REQ=str(fake_req), FAKE_SIG=sig, FAKE_SIGF=sigf)
    return proc, out


def test_replicate_rehearsal_passes_on_identical_requests(tmp_path: Path) -> None:
    proc, out = _rehearse_rep(tmp_path, 0.0)
    assert "RC=0" in proc.stdout, proc.stdout + proc.stderr
    assert "requests IDENTICAL — 2 of 2" in proc.stdout
    rec = json.loads((out / "stage2" / "checks"
                      / "request-identity-g37-text-g3-rep2.json").read_text())
    assert rec["identical"] and rec["differing_fields"] == {}
    assert (out / "stage2" / "checks" / "rehearse-g37-text-g3-rep2.json").exists()
    assert not (out / "stage2" / "checks" / "rehearse-g37-text-g3.json").exists()
    assert not list((out / "scratch").rglob("verifier_requests*.jsonl"))


def test_replicate_rehearsal_refuses_a_changed_request(tmp_path: Path) -> None:
    proc, out = _rehearse_rep(tmp_path, 1.0)
    assert "RC=1" in proc.stdout and "are not the original leg's" in proc.stdout
    rec = json.loads((out / "stage2" / "checks"
                      / "request-identity-g37-text-g3-rep2.json").read_text())
    assert rec["differing_fields"] == {"request.generation_config.temperature": 2}
    assert not list((out / "scratch").rglob("verifier_requests*.jsonl"))


def test_replicate_rehearsal_fails_closed_without_the_original_requests(
        tmp_path: Path) -> None:
    proc, out = _rehearse_rep(tmp_path, 0.0, original=False)
    assert "RC=1" in proc.stdout and "no request file" in proc.stdout
    assert not list((out / "scratch").rglob("verifier_requests*.jsonl"))
