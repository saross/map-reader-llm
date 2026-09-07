"""Tier-1 tests for ``scripts/register_post_e71_conditions.py`` (ruling 3a).

The registrar's plan must be exactly the nine ruled rows, read each pinned
commit from the evaluation's own vintage record, and be idempotent.
"""

from __future__ import annotations

import copy
import json

import pytest

from scripts import register_post_e71_conditions as r


def _register() -> dict:
    return json.loads(r.RUN_CONDITIONS.read_text(encoding="utf-8"))


def _strip(rc: dict) -> dict:
    """The register as it stood before the ruling was applied."""
    rc = copy.deepcopy(rc)
    for run in rc["decomposition"].values():
        run["conditions"] = [
            {k: v for k, v in c.items() if k != "input_vintage"}
            for c in run["conditions"] if not c["label"].endswith(r.SUFFIX)]
    return rc


@pytest.mark.tier1
def test_discovery_is_exactly_the_nine():
    assert set(r.discover_rescores()) == r.EXPECTED


@pytest.mark.tier1
def test_plan_on_the_unapplied_register_is_nine_stamps_and_nine_clones():
    actions = r.plan(_strip(_register()), r.discover_rescores())
    kinds = [a["kind"] for a in actions]
    assert kinds.count("stamp") == 9 and kinds.count("clone") == 9
    stamps = {(a["run_id"], a["label"]): a["input_vintage"] for a in actions
              if a["kind"] == "stamp"}
    # commits come from each evaluation's own e82_input_vintage, not a constant
    assert stamps[("n1-outstanding-384", "pro-image-high-t0-single-pass-run_1")][
        "detections_commit"] == "c3852ebad"
    assert stamps[("n1-outstanding-384", "baseline-pro-image-high-t-0-0")][
        "detections_commit"] == "1f443fd69"
    assert stamps[("e47-propose-brief", "single-pass-run_4")][
        "detections_commit"] == "52b0215a6"
    clones = [a["row"] for a in actions if a["kind"] == "clone"]
    assert all(c["label"].endswith(r.SUFFIX) for c in clones)
    assert all(c["eval_path"].startswith("results/rescore-2026-09-07/") for c in clones)


@pytest.mark.tier1
def test_apply_then_plan_is_empty_and_clone_sits_beside_its_row():
    rc = _strip(_register())
    actions = r.plan(rc, r.discover_rescores())
    r.apply(rc, actions)
    assert r.plan(rc, r.discover_rescores()) == []
    labels = [c["label"] for c in rc["decomposition"]["e47-propose-brief"]["conditions"]]
    i = labels.index("single-pass-run_4")
    assert labels[i + 1] == "single-pass-run_4" + r.SUFFIX
