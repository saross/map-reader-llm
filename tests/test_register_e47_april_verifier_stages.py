"""Tier-1 tests for ``scripts/register_e47_april_verifier_stages.py`` (PI ruling 2026-09-08).

The registrar must plan exactly two inventory rows and one run note on an
unapplied register, be idempotent, and not demand a sweep file for stages that
were never swept in place.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts import register_e47_april_verifier_stages as r
from scripts import register_verifier_stage_refresh as base

pytestmark = pytest.mark.tier1


def _register() -> dict:
    return json.loads(base.RUN_CONDITIONS.read_text(encoding="utf-8"))


def _strip(rc: dict) -> dict:
    """The register as it stood before the ruling was applied."""
    rc = copy.deepcopy(rc)
    run = rc["decomposition"]["e47-propose-brief"]
    for stage in r.STAGES:
        run.get("verifier_passes", {}).pop(stage["key"], None)
    note = r.NOTES["e47-propose-brief"]
    run["_note"] = (run.get("_note") or "").replace(f" | {note}", "").replace(note, "")
    return rc


def test_plan_on_the_unapplied_register_is_two_rows_and_one_note():
    actions = base.plan(_strip(_register()), stages=r.STAGES, notes=r.NOTES)
    kinds = [a["kind"] for a in actions]
    assert kinds.count("row") == 2 and kinds.count("note") == 1
    rows = {a["key"]: a["path"] for a in actions if a["kind"] == "row"}
    assert rows == {
        "verified-flash-high-text-1of5": "verified/flash-high-text-1of5",
        "verified-text-baseline": "verified/text-baseline",
    }


def test_apply_then_plan_is_empty_and_the_refreshed_row_is_untouched():
    rc = _strip(_register())
    base.apply(rc, base.plan(rc, stages=r.STAGES, notes=r.NOTES))
    assert base.plan(rc, stages=r.STAGES, notes=r.NOTES) == []
    passes = rc["decomposition"]["e47-propose-brief"]["verifier_passes"]
    assert "verified-flash-high-text-1of5-recovery-2026-09-08" in passes
    assert passes["verified-text-baseline"] == {"modality": "text", "path": "verified/text-baseline"}
    assert "PI ruling 2026-09-08" in rc["decomposition"]["e47-propose-brief"]["_note"]


def test_disk_check_does_not_demand_a_sweep_for_unswept_stages(tmp_path: Path):
    stage = dict(r.STAGES[1], n_candidates=2)
    stage_dir = tmp_path / stage["run_id"] / stage["path"]
    stage_dir.mkdir(parents=True)
    (stage_dir / "run.meta.json").write_text("{}", encoding="utf-8")
    results = {f"candidate_{i:05d}": {"mound_probability": 0.4} for i in range(2)}
    (stage_dir / "probabilities.json").write_text(json.dumps({"results": results}), encoding="utf-8")
    assert base.check_stage_on_disk(stage, outputs=tmp_path) == []
    # a stage that IS expected to carry a sweep still reports its absence
    swept = dict(stage, has_sweep=True)
    assert base.check_stage_on_disk(swept, outputs=tmp_path) == [
        f"{stage['key']}: sweep_2d.json missing"]
