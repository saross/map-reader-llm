"""Tier-1 tests for ``scripts/register_verifier_stage_refresh.py`` (card step 5.1).

The registrar must plan exactly three inventory rows plus two run notes on an
unapplied register, be idempotent, refuse a key collision with a different path,
and treat a candidate count that disagrees with the card as a stop state.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts import register_verifier_stage_refresh as r

pytestmark = pytest.mark.tier1


def _register() -> dict:
    return json.loads(r.RUN_CONDITIONS.read_text(encoding="utf-8"))


def _strip(rc: dict) -> dict:
    """The register as it stood before this script was applied."""
    rc = copy.deepcopy(rc)
    for stage in r.STAGES:
        run = rc["decomposition"][stage["run_id"]]
        run.get("verifier_passes", {}).pop(stage["key"], None)
    for run_id, note in r.NOTES.items():
        run = rc["decomposition"][run_id]
        current = run.get("_note") or ""
        run["_note"] = current.replace(f" | {note}", "").replace(note, "") or None
        if run["_note"] is None:
            del run["_note"]
    return rc


def test_plan_on_the_unapplied_register_is_three_rows_and_two_notes():
    actions = r.plan(_strip(_register()))
    kinds = [a["kind"] for a in actions]
    assert kinds.count("row") == 3 and kinds.count("note") == 2
    rows = {(a["run_id"], a["key"]): a["path"] for a in actions if a["kind"] == "row"}
    assert rows[("e47-propose-brief", "verified-flash-high-text-1of5-recovery-2026-09-08")] == (
        "verified/flash-high-text-1of5-recovery-2026-09-08")
    assert all(path.endswith("-recovery-2026-09-08") for path in rows.values())


def test_apply_then_plan_is_empty_and_rows_sit_beside_the_originals():
    rc = _strip(_register())
    r.apply(rc, r.plan(rc))
    assert r.plan(rc) == []
    for stage in r.STAGES:
        passes = rc["decomposition"][stage["run_id"]]["verifier_passes"]
        assert passes[stage["key"]] == {"modality": stage["modality"], "path": stage["path"]}
        if stage["beside"]:
            assert stage["beside"] in passes  # the pre-recovery row is preserved
    # the note is appended with the register's pipe convention, never replacing
    assert rc["decomposition"]["pv-diag-384"]["_note"].startswith("GAP-7")
    assert " | Verifier-stage refresh" in rc["decomposition"]["pv-diag-384"]["_note"]


def test_key_collision_with_a_different_path_is_an_error():
    rc = _strip(_register())
    stage = r.STAGES[0]
    rc["decomposition"][stage["run_id"]]["verifier_passes"][stage["key"]] = {
        "modality": stage["modality"], "path": "somewhere/else"}
    with pytest.raises(ValueError, match="already registered"):
        r.plan(rc)


def test_disk_check_flags_a_count_that_disagrees_with_the_card(tmp_path: Path):
    stage = r.STAGES[2]
    stage_dir = tmp_path / stage["run_id"] / stage["path"]
    stage_dir.mkdir(parents=True)
    for name in ("run.meta.json", "sweep_2d.json"):
        (stage_dir / name).write_text("{}", encoding="utf-8")
    results = {f"candidate_{i:05d}": {"mound_probability": 0.5} for i in range(5)}
    results["candidate_00001"]["mound_probability"] = None
    (stage_dir / "probabilities.json").write_text(
        json.dumps({"results": results}), encoding="utf-8")
    problems = r.check_stage_on_disk(stage, outputs=tmp_path)
    assert any("holds 5 results" in p for p in problems)
    assert any("1 candidates without a probability" in p for p in problems)
    assert r.check_stage_on_disk(stage, outputs=tmp_path / "nowhere") == [
        f"{stage['key']}: directory missing: "
        f"{tmp_path / 'nowhere' / stage['run_id'] / stage['path']}"]
