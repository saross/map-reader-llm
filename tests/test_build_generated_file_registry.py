"""Tier-1 tests for ``scripts/build_generated_file_registry.py``.

Covers the pure classification machinery — marker scanning, rule
matching (ordering, scope, ``requires_marker``), source resolution, map
validation, and (from 2026-09-13) the regime-2 audit fields — against
synthetic trees.

The full-corpus build is also exercised here from 2026-09-13: the
registry is itself a generated artefact under the 2026-09-11 ruling, so
its own ``--check`` drift guard needs a test, and the walk costs ~2 s
(the same bargain ``tests/test_generate_run_reports.py`` strikes for the
41 committed run reports).
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from scripts.build_generated_file_registry import (
    DEFAULT_OUT,
    count_by_directory,
    count_regime2,
    enumerate_mine,
    generator_guards,
    load_generator_map,
    load_test_index,
    main,
    match_rule,
    print_regime2_gaps,
    registry_body,
    resolve_sources,
    scan_head,
    scan_regime2,
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
        # 2026-09-13 charter extension (item 11a): outputs/ is enumerated in
        # full, so the three registered outputs/ document classes — and the
        # literature notes beside them — all get a classification.
        "outputs/run-a/post_run_report.md",
        "outputs/run-a/proposer/run_1/experiment_intent.md",
        "outputs/ab-plus/some_paper_2024.md",
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


# --------------------------------------------------------------------------- #
# Regime-2 audit fields (2026-09-11 ruling; checklist item 11a/11b)
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_scan_regime2_separates_banner_from_a_bare_generated_line(tmp_path):
    """A ``**Generated**:`` timestamp is not the ruling's banner.

    This is the distinction the audit drew over the 46
    ``outputs/**/evaluation.md`` files: they say *when* they were written,
    which is not a do-not-hand-edit banner naming a generator.
    """
    bare = _write(tmp_path / "a.md", "# E\n\n**Generated**: 2026-04-27T01:47:18+00:00\n")
    assert scan_regime2(bare) == (False, False)

    full = _write(tmp_path / "b.md",
                  "<!-- GENERATED FILE — do not hand-edit. -->\n# R\n\n"
                  "> Produced by `scripts/x.py` at source commit `736c39c0e`.\n")
    assert scan_regime2(full) == (True, True)

    # A banner with no hash is a banner without a stamp; prose about commit
    # messages must not be read as a stamp.
    no_stamp = _write(tmp_path / "c.md",
                      "<!-- GENERATED FILE — DO NOT EDIT. -->\n# R\n\n"
                      "> put before/after notes in the commit message\n")
    assert scan_regime2(no_stamp) == (True, False)


@pytest.mark.tier1
def test_scan_regime2_ignores_a_stamp_below_the_head_window(tmp_path):
    body = "<!-- GENERATED FILE -->\n" + "\n" * 20 + "commit `abcdef1`\n"
    assert scan_regime2(_write(tmp_path / "d.md", body)) == (True, False)


@pytest.mark.tier1
def test_generator_guards_credits_only_a_test_using_that_generators_flag(tmp_path):
    """A test earns the guard credit only by naming the script and its flag.

    Without the flag condition, any tier-1 test that merely mentioned some
    other script's ``--check`` would silently certify a generator that has
    no drift mode at all.
    """
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "gen_a.py").write_text(
        'ap.add_argument("--check", action="store_true")\n', encoding="utf-8")
    (tmp_path / "scripts" / "gen_b.py").write_text("no flags here\n", encoding="utf-8")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_gen_a.py").write_text(
        'import pytest\n@pytest.mark.tier1\ndef test_x():\n'
        '    assert gen_a.main(["--check"]) == 0\n', encoding="utf-8")
    # Mentions gen_b and a --check flag, but not one of gen_b's own flags
    # (gen_b declares none), so gen_b earns no credit.
    (tests / "test_gen_b.py").write_text(
        'import pytest\n@pytest.mark.tier1\ndef test_y():\n'
        '    assert gen_b.main([]) == 0  # a sibling script has --checkpoints\n',
        encoding="utf-8")

    index = load_test_index(tmp_path)
    guards_a = generator_guards(tmp_path, "scripts/gen_a.py", index)
    assert guards_a["check_mode"] is True
    assert guards_a["check_flags"] == ["--check"]
    assert guards_a["tier1_check_test"] is True
    assert guards_a["check_tests"] == ["tests/test_gen_a.py"]

    guards_b = generator_guards(tmp_path, "scripts/gen_b.py", index)
    assert guards_b["check_mode"] is False
    assert guards_b["tier1_check_test"] is False
    assert guards_b["check_tests"] == []

    # A missing generator is reported, not raised on.
    absent = generator_guards(tmp_path, "scripts/nope.py", index)
    assert absent["generator_present"] is False


@pytest.mark.tier1
def test_generator_guards_cache_is_used():
    cache: dict[str, dict] = {"scripts/x.py": {"sentinel": True}}
    assert generator_guards(Path("/nonexistent"), "scripts/x.py", [], cache) == {
        "sentinel": True
    }


@pytest.mark.tier1
def test_count_by_directory_buckets_every_row():
    entries = [
        {"path": "results/a.md", "stratum": "generated"},
        {"path": "reports/b.md", "stratum": "hand-written"},
        {"path": "outputs/run/c.md", "stratum": "generated"},
        {"path": "docs/methodology/d.md", "stratum": "hand-written"},
        {"path": "elsewhere/e.md", "stratum": "hand-written"},
    ]
    counts = count_by_directory(entries)
    assert counts["results/"] == {"total": 1, "generated": 1, "hand_written": 0}
    assert counts["outputs/"] == {"total": 1, "generated": 1, "hand_written": 0}
    assert counts["other"]["total"] == 1
    assert sum(b["total"] for b in counts.values()) == len(entries)


@pytest.mark.tier1
def test_count_regime2_conjunction_and_neither_regime():
    def row(banner, stamp, check, t1):
        return {"generated_banner": banner, "source_commit_stamp": stamp,
                "check_mode": check, "tier1_check_test": t1,
                "regime2_compliant": bool(banner and stamp and check and t1)}

    generated = [row(True, True, True, True), row(True, False, False, False),
                 row(False, False, False, False)]
    counts = count_regime2(generated)
    assert counts["compliant"] == 1
    assert counts["generated_banner"] == 2
    assert counts["neither_regime"] == 1


@pytest.mark.tier1
def test_print_regime2_gaps_groups_by_generator_and_names_what_is_missing():
    registry = {"files": [
        {"path": "results/a.md", "stratum": "generated", "generator": "scripts/g.py",
         "generated_banner": False, "source_commit_stamp": False,
         "check_mode": False, "tier1_check_test": False, "regime2_compliant": False},
        {"path": "results/b.md", "stratum": "generated", "generator": "scripts/g.py",
         "generated_banner": False, "source_commit_stamp": False,
         "check_mode": False, "tier1_check_test": False, "regime2_compliant": False},
        {"path": "results/c.md", "stratum": "generated", "generator": "scripts/ok.py",
         "generated_banner": True, "source_commit_stamp": True,
         "check_mode": True, "tier1_check_test": True, "regime2_compliant": True},
        {"path": "results/d.md", "stratum": "hand-written", "generator": None},
    ]}
    stream = io.StringIO()
    assert print_regime2_gaps(registry, stream) == 2
    text = stream.getvalue()
    assert "scripts/g.py" in text
    assert "scripts/ok.py" not in text
    assert "--check mode" in text and "tier-1 check test" in text


# --------------------------------------------------------------------------- #
# The registry as a generated artefact: its own drift guard
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_committed_registry_matches_a_rebuild():
    """``--check`` over the committed registry: the guard the ruling asks for.

    Fails when the mine gains, loses or re-classifies a document without
    the registry being rebuilt — the staleness that
    ``planning/interim-docs-review.md`` § 11.5 item 3 found (814
    ``results/**.md`` and 48 ``reports/**.md`` short of the tree).
    """
    assert DEFAULT_OUT.exists(), "the registry must be committed"
    assert main(["--check"]) == 0


@pytest.mark.tier1
def test_committed_registry_has_no_unattributed_generated_rows():
    """Every marker-carrying file resolves to a map rule (the ``--strict`` bar).

    Reads the committed registry rather than rebuilding: the rebuild is
    covered by the test above.
    """
    registry = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
    unattributed = [e["path"] for e in registry["files"]
                    if e["stratum"] == "generated" and e["rule_id"] is None]
    assert unattributed == []
    assert registry["_meta"]["counts"]["generated_unattributed"] == 0
