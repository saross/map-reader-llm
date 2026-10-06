#!/usr/bin/env python3
"""
Currency guard for generated outputs: is each committed output newer than
everything it was generated from?

Why this script exists
----------------------
A committed generated file is only as current as the last time its generator
was run on its inputs. Nothing enforced that, and on 2026-10-05 two stale
outputs surfaced by accident: the analyses manifest after D25's note, and the
K-ladder unions after their builder was fixed but never re-run (tracker C-22;
``planning/text-track-transmission-2026-10-05.md`` § W6.3). Both were caught
by a person reading closely, not by a check.

``reports/verification/generated-file-registry.json`` (written by
``scripts/build_generated_file_registry.py``) already records, for every
generated file it classifies, its generator script and the committed source
files it is re-derivable from. This script turns that record into a guard: an
output whose last commit PREDATES the last commit of any of its sources, or of
its generator, is a STALE CANDIDATE.

"Candidate", because a commit time is evidence, not proof. A generator commit
may not have changed what the output contains (a comment, a different code
path); a source commit may have touched a field the output never reads. A
stale candidate is a file to regenerate and diff, not a file known to be
wrong. Conversely, a CURRENT verdict says only that nothing upstream was
committed after the output: it cannot see a block inside a freshly
regenerated file that was carried forward stale (e.g. a costing block that
still says "not run" after the run).

Scope and limits
----------------
- Only registry entries carrying BOTH a ``generator`` and a non-empty
  ``sources`` list are checked. Entries with a generator but no committed
  sources (launch-time records, projections whose sources the registry names
  only in prose) are counted as out of scope, not checked.
- The registry classifies the MARKDOWN corpus only (4,027 ``.md`` files on
  2026-10-05): a generated JSON output (a union, a manifest, an analysis
  file) is covered only where a Markdown projection lists it as a source. A
  JSON output's own currency needs a registry that lists it.
- Times are committer timestamps from git history (``%ct``); uncommitted
  working-tree edits are invisible. Merge commits contribute no file list
  (git's default), so a change made only in a merge resolution is missed.

How it stays cheap
------------------
One ``git log --name-only`` walk over the whole history (about a second on
this repository) yields the last commit time of every path ever committed;
a path the walk did not see falls back to one ``git log -1 --format=%ct --
<path>`` call, cached. No file is read or regenerated.

Usage
-----
    # Markdown report to stdout; exit 1 if any output is stale
    python3 scripts/check_generated_currency.py

    # The same, as JSON
    python3 scripts/check_generated_currency.py --json

    # Report only, never fail (e.g. in a session-close sweep)
    python3 scripts/check_generated_currency.py --warn-only

    # Ignore generator commits: flag only outputs older than a SOURCE
    python3 scripts/check_generated_currency.py --sources-only

Exit codes: 0 no stale candidate (or ``--warn-only``); 1 at least one stale
candidate; 2 the registry could not be read.
"""

from __future__ import annotations

import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent

#: The registry this guard reads by default.
DEFAULT_REGISTRY = "reports/verification/generated-file-registry.json"

#: The verdicts an entry can receive.
STALE = "stale"
CURRENT = "current"
UNTRACKED_OUTPUT = "output-not-committed"


class GitClock:
    """Last-commit times of repository paths, cached.

    Attributes:
        repo: The repository root.
        times: Path → last committer time (Unix seconds), filled by
            :meth:`prefill` and by per-path lookups.
        commits: Path → abbreviated hash of that last commit.
        n_fallback_calls: Per-path git calls made for paths the walk missed.
    """

    def __init__(self, repo: Path) -> None:
        """Create an empty clock for one repository.

        Args:
            repo: The repository root (any directory inside the work tree).
        """
        self.repo = repo
        self.times: dict[str, int | None] = {}
        self.commits: dict[str, str] = {}
        self.n_fallback_calls = 0

    def _git(self, *args: str) -> str:
        """Run git in the repository and return its standard output.

        Args:
            *args: Arguments after ``git``.

        Returns:
            Standard output as text.
        """
        return subprocess.run(
            ["git", "-c", "core.quotePath=false", *args], cwd=self.repo,
            capture_output=True, text=True, check=True).stdout

    def prefill(self) -> int:
        """Record every committed path's last change, in one history walk.

        ``--no-renames`` keeps each commit's file list literal (a rename
        lists the new path as added), and the maximum time per path is kept,
        so commit order in the log does not matter.

        Returns:
            The number of distinct paths recorded.
        """
        out = self._git("log", "--no-renames", "--format=@@%ct %h", "--name-only")
        current, commit = 0, ""
        for line in out.splitlines():
            if line.startswith("@@"):
                stamp, commit = line[2:].split(" ", 1)
                current = int(stamp)
            elif line:
                previous = self.times.get(line)
                if previous is None or current > previous:
                    self.times[line] = current
                    self.commits[line] = commit
        return len(self.times)

    def last_change(self, path: str) -> int | None:
        """The last committer time of a path, or None if never committed.

        Args:
            path: Repository-relative path.

        Returns:
            Unix seconds, or None.
        """
        if path not in self.times:
            self.n_fallback_calls += 1
            out = self._git("log", "-1", "--format=%ct %h", "--", path).strip()
            if out:
                stamp, self.commits[path] = out.split(" ", 1)
                self.times[path] = int(stamp)
            else:
                self.times[path] = None
        return self.times[path]

    def commit_of(self, path: str) -> str | None:
        """The abbreviated hash of a path's last commit, if known.

        Args:
            path: Repository-relative path (looked up first if need be).

        Returns:
            The hash, or None when the path was never committed.
        """
        self.last_change(path)
        return self.commits.get(path)


def load_registry(path: Path) -> list[dict[str, Any]]:
    """Read the registry's file entries.

    Args:
        path: The registry JSON (``{"_meta": ..., "files": [...]}``).

    Returns:
        The ``files`` list.

    Raises:
        OSError, ValueError, KeyError: The file is absent or malformed.
    """
    return json.loads(path.read_text(encoding="utf-8"))["files"]


def check_entry(entry: dict[str, Any], clock: GitClock,
                sources_only: bool = False) -> dict[str, Any]:
    """Judge one registry entry's currency.

    Args:
        entry: A registry entry with ``path``, ``generator`` and ``sources``.
        clock: The git clock.
        sources_only: Ignore the generator's commits.

    Returns:
        ``{"path", "generator", "verdict", "output_time", "newer_sources",
        "generator_newer", "uncommitted_sources", "hand_edited"}``.
        ``newer_sources`` lists ``{"path", "time"}`` for each source
        committed after the output.
    """
    out_time = clock.last_change(entry["path"])
    newer: list[dict[str, Any]] = []
    uncommitted: list[str] = []
    for src in entry.get("sources") or []:
        t = clock.last_change(src)
        if t is None:
            uncommitted.append(src)
        elif out_time is not None and t > out_time:
            newer.append({"path": src, "time": t})
    gen_time = clock.last_change(entry["generator"]) if entry.get("generator") else None
    generator_newer = (not sources_only and out_time is not None
                       and gen_time is not None and gen_time > out_time)
    if out_time is None:
        verdict = UNTRACKED_OUTPUT
    elif newer or generator_newer:
        verdict = STALE
    else:
        verdict = CURRENT
    # The newest upstream commit that outdated the output: the one a triage
    # would read first (a single metadata-only commit can outdate thousands).
    upstream = [(s["time"], s["path"]) for s in newer]
    if generator_newer:
        upstream.append((gen_time, entry["generator"]))
    outdated_by = clock.commit_of(max(upstream)[1]) if upstream else None
    return {
        "path": entry["path"],
        "generator": entry.get("generator"),
        "verdict": verdict,
        "output_time": out_time,
        "newer_sources": newer,
        "generator_newer": generator_newer,
        "generator_time": gen_time,
        "uncommitted_sources": uncommitted,
        "hand_edited": bool(entry.get("hand_edited")),
        "outdated_by": outdated_by,
    }


def check_registry(entries: list[dict[str, Any]], clock: GitClock,
                   sources_only: bool = False) -> dict[str, Any]:
    """Judge every in-scope registry entry.

    Args:
        entries: Registry entries.
        clock: The git clock (prefilled or not).
        sources_only: Ignore generator commits.

    Returns:
        A summary dict: counts by verdict and by reason, the out-of-scope
        count, and one record per checked entry (stale ones first, then by
        path).
    """
    in_scope = [e for e in entries if e.get("generator") and e.get("sources")]
    records = [check_entry(e, clock, sources_only) for e in in_scope]
    records.sort(key=lambda r: (r["verdict"] != STALE, r["path"]))
    stale = [r for r in records if r["verdict"] == STALE]
    by_generator = collections.Counter(r["generator"] for r in stale)
    by_commit = collections.Counter(r["outdated_by"] for r in stale)
    return {
        "n_entries": len(entries),
        "n_checked": len(in_scope),
        "n_out_of_scope": {
            "generator_without_sources": sum(
                1 for e in entries if e.get("generator") and not e.get("sources")),
            "no_generator": sum(1 for e in entries if not e.get("generator")),
        },
        "sources_only": sources_only,
        "verdicts": dict(collections.Counter(r["verdict"] for r in records)),
        "n_stale": len(stale),
        "n_stale_by_reason": {
            "source_newer": sum(1 for r in stale if r["newer_sources"]),
            "generator_newer_only": sum(
                1 for r in stale if r["generator_newer"] and not r["newer_sources"]),
        },
        "n_stale_hand_edited": sum(1 for r in stale if r["hand_edited"]),
        "stale_by_generator": dict(by_generator.most_common()),
        "stale_by_outdating_commit": dict(by_commit.most_common()),
        "n_uncommitted_sources": sum(len(r["uncommitted_sources"]) for r in records),
        "records": records,
    }


def _iso(ts: int | None) -> str:
    """Format a Unix time as an ISO date-time (UTC), or a dash.

    Args:
        ts: Unix seconds, or None.

    Returns:
        ``YYYY-MM-DD HH:MM`` in UTC, or ``"—"``.
    """
    if ts is None:
        return "—"
    import datetime
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime(
        "%Y-%m-%d %H:%M")


def render_markdown(summary: dict[str, Any], registry: str, limit: int,
                    subjects: dict[str, str] | None = None) -> str:
    """Render the summary as a Markdown report.

    Args:
        summary: From :func:`check_registry`.
        registry: The registry path, for the heading.
        limit: Stale entries to list (all when 0).
        subjects: Commit hash → subject line, for the outdating-commit table.

    Returns:
        The report text.
    """
    subjects = subjects or {}
    stale = [r for r in summary["records"] if r["verdict"] == STALE]
    lines = [
        "# Generated-output currency check",
        "",
        f"Registry: `{registry}`. Entries: {summary['n_entries']:,}; checked "
        f"(generator and committed sources): {summary['n_checked']:,}; out of scope: "
        f"{summary['n_out_of_scope']['generator_without_sources']:,} with a generator "
        f"but no listed sources, {summary['n_out_of_scope']['no_generator']:,} "
        "hand-written.",
        "",
        f"- Stale candidates: **{summary['n_stale']:,}** "
        f"(a source newer: {summary['n_stale_by_reason']['source_newer']:,}; "
        f"only the generator newer: "
        f"{summary['n_stale_by_reason']['generator_newer_only']:,}"
        + ("; generator commits ignored" if summary["sources_only"] else "") + ")",
        "- Verdicts: " + ", ".join(f"{k} {v:,}" for k, v in
                                    sorted(summary["verdicts"].items())),
        f"- Stale entries marked hand-edited: {summary['n_stale_hand_edited']:,}",
        f"- Listed sources never committed: {summary['n_uncommitted_sources']:,}",
        "",
    ]
    if summary["stale_by_generator"]:
        lines += ["## Stale candidates by generator", "",
                  "| Generator | Stale |", "| --- | ---: |"]
        lines += [f"| `{g}` | {n:,} |" for g, n in summary["stale_by_generator"].items()]
        lines.append("")
    if summary["stale_by_outdating_commit"]:
        lines += ["## Stale candidates by the upstream commit that last outdated them",
                  "", "| Commit | Subject | Stale |", "| --- | --- | ---: |"]
        for commit, n in list(summary["stale_by_outdating_commit"].items())[:15]:
            lines.append(f"| `{commit}` | {subjects.get(commit, '')} | {n:,} |")
        lines.append("")
    if stale:
        shown = stale if limit == 0 else stale[:limit]
        lines += [f"## Stale candidates ({len(shown):,} of {len(stale):,} listed)", "",
                  "| Output | Output committed | Newer upstream |", "| --- | --- | --- |"]
        for r in shown:
            upstream = [f"`{s['path']}` ({_iso(s['time'])})" for s in r["newer_sources"]]
            if r["generator_newer"]:
                upstream.append(f"generator `{r['generator']}` ({_iso(r['generator_time'])})")
            lines.append(f"| `{r['path']}` | {_iso(r['output_time'])} | "
                         f"{'; '.join(upstream)} |")
        lines.append("")
    lines += ["A stale candidate is an output to regenerate and diff, not one known to "
              "be wrong; a current verdict cannot see a stale block carried forward "
              "inside a regenerated file (see the module docstring).", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point.

    Args:
        argv: Arguments (defaults to ``sys.argv[1:]``).

    Returns:
        The process exit status.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--registry", default=DEFAULT_REGISTRY,
                    help=f"Registry JSON, relative to --repo (default: {DEFAULT_REGISTRY}).")
    ap.add_argument("--repo", default=str(BASE_DIR),
                    help="Repository root (default: this script's repository).")
    ap.add_argument("--json", action="store_true",
                    help="Print the summary as JSON instead of Markdown.")
    ap.add_argument("--warn-only", action="store_true",
                    help="Report, but exit 0 even when stale candidates exist.")
    ap.add_argument("--sources-only", action="store_true",
                    help="Ignore generator commits; flag only outputs older than a source.")
    ap.add_argument("--limit", type=int, default=50,
                    help="Stale entries listed in the Markdown report (0 = all; default 50).")
    args = ap.parse_args(argv)

    repo = Path(args.repo)
    registry_path = Path(args.registry)
    if not registry_path.is_absolute():
        registry_path = repo / registry_path
    try:
        entries = load_registry(registry_path)
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: cannot read the registry {registry_path}: {exc}", file=sys.stderr)
        return 2

    clock = GitClock(repo)
    clock.prefill()
    summary = check_registry(entries, clock, sources_only=args.sources_only)
    summary["n_git_fallback_calls"] = clock.n_fallback_calls

    if args.json:
        print(json.dumps({"registry": args.registry, **summary}, indent=1))
    else:
        top = list(summary["stale_by_outdating_commit"])[:15]
        subjects = {c: clock._git("log", "-1", "--format=%s", c).strip()
                    for c in top if c}
        print(render_markdown(summary, args.registry, args.limit, subjects))
    if summary["n_stale"] and not args.warn_only:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
