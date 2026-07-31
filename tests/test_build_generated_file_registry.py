"""Tier-1 tests for ``scripts/build_generated_file_registry.py``.

Covers the pure classification machinery — marker scanning, rule
matching (ordering, scope, ``requires_marker``), source resolution, and
map validation — against synthetic trees. The full-corpus build is
exercised at run time by the script's own ``--check`` drift mode; no
2,000-file walk belongs in tier 1.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.build_generated_file_registry import (
    enumerate_mine,
    load_generator_map,
    match_rule,
    registry_body,
    resolve_sources,
    scan_head,
)


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.tier1
def test_scan_head_detects_markers_and_h1(tmp_path):
    marked = _write(tmp_path / "a.md", "# Title\n\n**Generated**: 2026-04-30T06:52:29+00:00\n")
    unmarked = _write(tmp_path / "b.md", "# T\n\nHand-written prose with **Generated**\n")
    marker, h1 = scan_head(marked)
    assert marker == "**Generated**: 2026-04-30T06:52:29+00:00"
    assert h1 == "# Title"
    # The bare bold word without a colon is not a marker.
    marker, h1 = scan_head(unmarked)
    assert marker is None
    assert h1 == "# T"


@pytest.mark.tier1
def test_scan_head_ignores_deep_matches(tmp_path):
    # A marker beyond the head window must not classify the file.
    body = "# T\n" + "\n" * 20 + "**Generated**: late\n"
    marker, _ = scan_head(_write(tmp_path / "c.md", body))
    assert marker is None


@pytest.mark.tier1
def test_match_rule_ordering_scope_and_marker_gate():
    rules = load_rules([
        {"rule_id": "specific", "match": r"(^|/)evaluation\.md$",
         "scope": "results/special/", "generator": "scripts/special.py",
         "source_rule": "sibling:evaluation.json"},
        {"rule_id": "generic", "match": r"(^|/)evaluation\.md$",
         "scope": "results/", "generator": "scripts/evaluate_detections.py",
         "source_rule": "sibling:evaluation.json"},
        {"rule_id": "marked-report", "match": r"(^|/)report\.md$",
         "scope": "results/", "generator": "scripts/reporter.py",
         "source_rule": "sibling-stem:.json", "requires_marker": True},
    ])
    # First matching rule wins (most specific first).
    assert match_rule("results/special/x/evaluation.md", True, rules)["rule_id"] == "specific"
    assert match_rule("results/other/evaluation.md", False, rules)["rule_id"] == "generic"
    # Scope prefix excludes non-results paths.
    assert match_rule("reports/evaluation.md", False, rules) is None
    # requires_marker gates the shared-basename rule.
    assert match_rule("results/x/report.md", False, rules) is None
    assert match_rule("results/x/report.md", True, rules)["rule_id"] == "marked-report"


@pytest.mark.tier1
def test_match_rule_h1_signature_disambiguates():
    # Three scripts write tiering_20m.md; the H1 heading disambiguates
    # (agent-attributed write sites, Session 122).
    rules = load_rules([
        {"rule_id": "tiering-era1", "match": r"(^|/)tiering_20m\.md$",
         "scope": "results/", "generator": "scripts/era1_leaderboard_tiering.py",
         "source_rule": "sibling-stem:.json", "h1": r"^# Era-1 leaderboard"},
        {"rule_id": "tiering-n1", "match": r"(^|/)tiering_20m\.md$",
         "scope": "results/", "generator": "scripts/n1_baseline_leaderboard_tiering.py",
         "source_rule": "sibling-stem:.json", "h1": r"^# N=1 baseline leaderboard"},
    ])
    era1 = match_rule("results/era1-leaderboard/tiering_20m.md", False, rules,
                      h1="# Era-1 leaderboard — statistical tiering (20 m)")
    assert era1["rule_id"] == "tiering-era1"
    n1 = match_rule("results/paper-eval/n1/tiering/tiering_20m.md", False, rules,
                    h1="# N=1 baseline leaderboard — statistical tiering (20 m)")
    assert n1["rule_id"] == "tiering-n1"
    # No H1 match → no rule (falls through to unattributed/hand-written).
    assert match_rule("results/x/tiering_20m.md", False, rules, h1="# Other") is None


@pytest.mark.tier1
def test_hand_written_override_rule_beats_marker():
    # A hand-written file carrying a **Generated** line (e.g.
    # results/leaderboard/combined/README.md) is forced hand-written by a
    # stratum-override rule.
    rules = load_rules([
        {"rule_id": "combined-readme-hand", "match": r"^results/leaderboard/combined/README\.md$",
         "scope": "results/leaderboard/combined/", "generator": None,
         "source_rule": "none", "stratum": "hand-written"},
    ])
    rule = match_rule("results/leaderboard/combined/README.md", True, rules, h1="# X")
    assert rule["stratum"] == "hand-written"


def load_rules(rules: list[dict]):
    """Round-trip a rule list through load_generator_map via a temp file."""
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump({"map_version": "test", "rules": rules}, fh)
        name = fh.name
    return load_generator_map(Path(name))


@pytest.mark.tier1
def test_load_generator_map_rejects_bad_rules():
    with pytest.raises(ValueError, match="missing keys"):
        load_rules([{"rule_id": "x", "match": ".*"}])
    with pytest.raises(ValueError, match="duplicate rule_id"):
        load_rules([
            {"rule_id": "x", "match": ".*", "scope": "", "generator": "g",
             "source_rule": "none"},
            {"rule_id": "x", "match": ".*", "scope": "", "generator": "g",
             "source_rule": "none"},
        ])
    with pytest.raises(ValueError, match="bad regex"):
        load_rules([{"rule_id": "x", "match": "(", "scope": "", "generator": "g",
                     "source_rule": "none"}])


@pytest.mark.tier1
def test_resolve_sources_sibling_forms(tmp_path):
    _write(tmp_path / "results/run/evaluation.md", "x")
    _write(tmp_path / "results/run/evaluation.json", "{}")
    _write(tmp_path / "results/run/threshold_sweep.json", "{}")
    rel = "results/run/evaluation.md"
    assert resolve_sources(tmp_path, rel, "sibling:evaluation.json") == [
        "results/run/evaluation.json"
    ]
    assert resolve_sources(tmp_path, rel, "sibling-stem:.json") == [
        "results/run/evaluation.json"
    ]
    assert resolve_sources(tmp_path, rel, "dir-glob:*.json") == [
        "results/run/evaluation.json",
        "results/run/threshold_sweep.json",
    ]
    # Missing sibling resolves to nothing; free text stays unresolved.
    assert resolve_sources(tmp_path, rel, "sibling:absent.json") == []
    assert resolve_sources(tmp_path, rel, "eval JSONs across results/**") == []


@pytest.mark.tier1
def test_enumerate_mine_scope(tmp_path):
    keep = [
        "results/a.md",
        "results/deep/b.md",
        "reports/c.md",
        "docs/methodology/top.md",
        "docs/methodology/reports/r.md",
        "docs/methodology/transparency/t.md",
        "docs/methodology/preregistration/protocol-errata.md",
        "docs/methods-outline.md",
    ]
    drop = [
        "reports/d17-inventory/x.md",           # audit apparatus exclusion
        "docs/methodology/preregistration/osf/preregistration.md",  # anchor only
        "docs/methodology/references/lit.md",   # excluded from the mine
        "docs/paper/draft.md",                  # out of scope entirely
        "results/note.txt",                     # not markdown
    ]
    for rel in keep + drop:
        _write(tmp_path / rel, "# stub\n")
    got = [p.as_posix() for p in enumerate_mine(tmp_path)]
    assert got == sorted(keep)


@pytest.mark.tier1
def test_registry_body_drops_volatile_meta():
    reg = {"_meta": {"generated_at": "now", "git_head": "abc", "counts": {"total": 1}},
           "files": [{"path": "results/a.md"}]}
    body = registry_body(reg)
    assert "generated_at" not in body["_meta"]
    assert "git_head" not in body["_meta"]
    assert body["files"] == reg["files"]
