"""
Tests for ``scripts/check_generated_currency.py`` (tracker W6.3).

The guard flags a committed generated output whose last commit predates the
last commit of any of its registered sources or of its generator. These
tests build a synthetic repository with a mini-registry and commits at
controlled dates, so every verdict is known in advance:

- ``current.md`` committed after its source and generator → current;
- ``stale-source.md`` whose source was re-committed later → stale (source);
- ``stale-generator.md`` whose generator was edited later → stale
  (generator only), current under ``--sources-only``;
- ``launch.md`` with a generator but no sources → out of scope;
- ``never.md`` registered but never committed → output-not-committed.

Tier 2: each test creates a git repository and runs several git processes.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from scripts import check_generated_currency as cgc

pytestmark = pytest.mark.tier2


def _commit(repo: Path, files: dict[str, str], when: str, message: str) -> str:
    """Write files and commit them at a fixed date.

    Args:
        repo: The repository root.
        files: Relative path → content.
        when: ISO date for both author and committer.
        message: Commit message.

    Returns:
        The new commit's abbreviated hash.
    """
    for rel, text in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    subprocess.run(["git", "add", *files], cwd=repo, check=True, env=env)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=repo, check=True, env=env)
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=repo, check=True,
                          capture_output=True, text=True).stdout.strip()


def _entry(path: str, generator: str | None, sources: list[str]) -> dict:
    """A registry entry in the committed registry's shape."""
    return {"path": path, "stratum": "generated" if generator else "hand-written",
            "rule_id": None, "generator": generator, "source_rule": None,
            "sources": sources, "marker": None, "hand_edited": False}


@pytest.fixture()
def repo(tmp_path: Path) -> dict:
    """A repository whose history makes every verdict known in advance."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    _commit(tmp_path, {"gen.py": "v1", "gen2.py": "v1", "a.json": "1", "b.json": "1",
                       "c.json": "1"}, "2026-01-01T00:00:00Z", "inputs")
    _commit(tmp_path, {"current.md": "x", "stale-source.md": "x",
                       "stale-generator.md": "x", "launch.md": "x"},
            "2026-01-02T00:00:00Z", "outputs")
    outdating = _commit(tmp_path, {"b.json": "2"}, "2026-01-03T00:00:00Z",
                        "data: re-emit b")
    _commit(tmp_path, {"gen2.py": "v2"}, "2026-01-04T00:00:00Z", "fix: generator 2")
    registry = {"_meta": {}, "files": [
        _entry("current.md", "gen.py", ["a.json"]),
        _entry("stale-source.md", "gen.py", ["b.json"]),
        _entry("stale-generator.md", "gen2.py", ["c.json"]),
        _entry("launch.md", "gen.py", []),
        _entry("never.md", "gen.py", ["a.json"]),
        _entry("notes.md", None, []),
    ]}
    (tmp_path / "registry.json").write_text(json.dumps(registry))
    return {"root": tmp_path, "outdating": outdating}


def _summary(repo: dict, sources_only: bool = False) -> dict:
    """Run the check in-process over the synthetic repository."""
    clock = cgc.GitClock(repo["root"])
    clock.prefill()
    entries = cgc.load_registry(repo["root"] / "registry.json")
    return cgc.check_registry(entries, clock, sources_only=sources_only)


def test_each_verdict_is_the_one_the_history_implies(repo) -> None:
    """Current, stale by a source, stale by the generator, never committed."""
    s = _summary(repo)
    verdicts = {r["path"]: r["verdict"] for r in s["records"]}
    assert verdicts == {"current.md": cgc.CURRENT, "stale-source.md": cgc.STALE,
                        "stale-generator.md": cgc.STALE,
                        "never.md": cgc.UNTRACKED_OUTPUT}
    assert s["n_stale"] == 2
    assert s["n_stale_by_reason"] == {"source_newer": 1, "generator_newer_only": 1}
    # Out of scope, never silently checked: a generator without sources, and
    # a hand-written file.
    assert s["n_out_of_scope"] == {"generator_without_sources": 1, "no_generator": 1}


def test_a_stale_record_names_the_commit_that_outdated_it(repo) -> None:
    """Triage reads the outdating commit first: it is the source's re-emit."""
    s = _summary(repo)
    rec = next(r for r in s["records"] if r["path"] == "stale-source.md")
    assert [n["path"] for n in rec["newer_sources"]] == ["b.json"]
    assert rec["outdated_by"] == repo["outdating"]
    assert s["stale_by_outdating_commit"][repo["outdating"]] == 1


def test_sources_only_ignores_generator_commits(repo) -> None:
    """A generator edit need not change the output; --sources-only says so."""
    s = _summary(repo, sources_only=True)
    verdicts = {r["path"]: r["verdict"] for r in s["records"]}
    assert verdicts["stale-generator.md"] == cgc.CURRENT
    assert verdicts["stale-source.md"] == cgc.STALE


def test_the_cli_exits_one_on_stale_unless_warn_only(repo, capsys) -> None:
    """Exit 1 on any stale candidate; --warn-only reports and exits 0; the
    JSON and Markdown outputs both carry the findings."""
    args = ["--repo", str(repo["root"]), "--registry", "registry.json"]
    assert cgc.main(args) == 1
    md = capsys.readouterr().out
    assert "Stale candidates: **2**" in md and "`stale-source.md`" in md
    assert "data: re-emit b" in md
    assert cgc.main([*args, "--warn-only", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["n_stale"] == 2 and data["registry"] == "registry.json"
    assert cgc.main([*args, "--sources-only"]) == 1


def test_an_unreadable_registry_exits_two(tmp_path, capsys) -> None:
    """A missing registry is a usage error, not a pass."""
    assert cgc.main(["--repo", str(tmp_path), "--registry", "absent.json"]) == 2
    assert "cannot read the registry" in capsys.readouterr().err


def test_a_path_the_walk_missed_falls_back_to_one_git_call(repo) -> None:
    """The bulk walk records every committed path; anything else costs one
    cached git call, and an uncommitted path reads as never committed."""
    clock = cgc.GitClock(repo["root"])
    clock.prefill()
    assert clock.last_change("a.json") is not None and clock.n_fallback_calls == 0
    assert clock.last_change("no-such-file") is None
    assert clock.last_change("no-such-file") is None
    assert clock.n_fallback_calls == 1
