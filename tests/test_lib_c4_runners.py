"""Tier-1 tests for ``scripts/lib_c4_runners.py`` (runner registry).

Synthetic tmp fixtures only — no real corpus I/O. Covers each census
primitive, the predicate grammar, and registry loading.
"""

from __future__ import annotations

import json

import pytest

import scripts.lib_c4_runners as runners
from scripts.lib_c4_runners import (
    execute_spec,
    load_registry,
    run_glob_count,
    run_json_aggregate,
    run_json_subset_count,
    run_regex_count,
)


@pytest.fixture()
def runner_repo(tmp_path, monkeypatch):
    """Point the runner library at a tmp repo with countable content."""
    (tmp_path / "outputs" / "a").mkdir(parents=True)
    (tmp_path / "outputs" / "b").mkdir()
    (tmp_path / "outputs" / "a" / "post_run_report.md").write_text("x\n")
    (tmp_path / "outputs" / "b" / "post_run_report.md").write_text("x\n")
    (tmp_path / "outputs" / "run_1").mkdir()
    (tmp_path / "outputs" / "run_2").mkdir()
    (tmp_path / "script.py").write_text(
        'A = "outputs/h11/e47/x"\nB = "outputs/h11/e47/y"\nC = "other"\n')
    (tmp_path / "inventory.json").write_text(json.dumps([
        {"id": "one", "path": "outputs/h11/e47/x", "K": 5},
        {"id": "two", "path": "outputs/h11/wbf/y", "K": 3},
        {"id": "three", "path": "outputs/h11/e47/z", "K": 5},
    ]))
    (tmp_path / "consensus.json").write_text(json.dumps(
        {"features": [{"properties": {"votes": 17}},
                      {"properties": {"votes": 16}},
                      {"properties": {"votes": 30}}]}))
    monkeypatch.setattr(runners, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(runners, "REGISTRY_PATH", tmp_path / "registry.json")
    return tmp_path


@pytest.mark.tier1
def test_glob_count(runner_repo):
    assert run_glob_count({"root": "outputs", "glob": "*/post_run_report.md"}) == 2
    assert run_glob_count({"root": "outputs", "glob": "run_*", "kind": "dir"}) == 2


@pytest.mark.tier1
def test_regex_count_lines_and_occurrences(runner_repo):
    assert run_regex_count({"file": "script.py",
                            "pattern": r"outputs/h11/e47/"}) == 2
    assert run_regex_count({"file": "script.py", "pattern": r'"',
                            "scope": "occurrences"}) == 6


@pytest.mark.tier1
def test_json_subset_count_predicates(runner_repo):
    assert run_json_subset_count({
        "file": "inventory.json", "list_path": "$",
        "where": [{"key": "path", "op": "regex", "value": "e47"}]}) == 2
    assert run_json_subset_count({
        "file": "inventory.json", "list_path": "$",
        "where": [{"key": "path", "op": "regex", "value": "e47"},
                  {"key": "K", "op": "eq", "value": 5}]}) == 2
    assert run_json_subset_count({
        "file": "inventory.json", "list_path": "$",
        "where": [{"key": "path", "op": "contains", "value": "nowhere"}]}) == 0


@pytest.mark.tier1
def test_json_aggregate_min_over_features(runner_repo):
    # The effective vote threshold of a consensus pool: min over votes.
    assert run_json_aggregate({
        "file": "consensus.json", "list_path": "$.features",
        "key": "properties.votes", "agg": "min"}) == 16
    assert run_json_aggregate({
        "file": "consensus.json", "list_path": "$.features",
        "key": "properties.votes", "agg": "count-distinct"}) == 3


@pytest.mark.tier1
def test_registry_roundtrip_and_execute(runner_repo):
    assert load_registry() == {}  # absent registry -> empty index
    spec = {"batch": "038-h11", "claim_index": 9, "value_index": 0,
            "runner": "json-subset-count",
            "params": {"file": "inventory.json", "list_path": "$",
                       "where": [{"key": "path", "op": "regex",
                                  "value": "wbf"}]}}
    (runner_repo / "registry.json").write_text(json.dumps({"specs": [spec]}))
    index = load_registry()
    assert ("038-h11", 9, 0) in index
    assert execute_spec(index[("038-h11", 9, 0)]) == 1


@pytest.mark.tier1
def test_runner_errors_fail_loudly(runner_repo):
    with pytest.raises(KeyError):
        execute_spec({"runner": "no-such-runner", "params": {}})
    with pytest.raises(ValueError):
        run_json_subset_count({"file": "consensus.json", "list_path": "$",
                               "where": []})  # root is a dict, not a list
    with pytest.raises(ValueError):
        run_json_subset_count({"file": "inventory.json", "list_path": "$",
                               "where": [{"key": "id", "op": "explode",
                                          "value": "x"}]})
