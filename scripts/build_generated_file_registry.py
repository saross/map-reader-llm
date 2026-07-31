#!/usr/bin/env python3
"""Build the generated-file registry for the C4 quantitative sweep.

Phase 3 deliverable 1 (GATE 0 decision 2; ``planning/audit-charter.md``
§ 7 Phase 3): harden the Phase 0 heuristic generated/hand-written
classification of the mine's markdown corpus into a committed registry
naming, for every generated file, its generator script and the committed
source artefact(s) it is re-derivable from.

Classification inputs, in order:

1. A generation **marker** in the file head (first ``HEAD_LINES`` lines):
   ``**Generated**:``, ``> Generated``, ``<!-- GENERATED``, or
   ``GENERATED FILE`` — the Phase 0 marker set.
2. The **generator map** (``reports/verification/apparatus/generator-map.json``):
   ordered pattern rules assembled from write-site evidence (attribution
   agents, Session 122); first matching rule wins. Rules with
   ``requires_marker`` only apply to marker-carrying files (for basenames
   shared between generated and hand-curated siblings, e.g. ``report.md``).

Verdict logic: rule match → ``generated`` (attributed); marker without a
rule → ``generated`` but **unattributed** (build warns; ``--strict``
fails); neither → ``hand-written``.

The registry is deterministic given the tree and the map. ``--check``
rebuilds and diffs against the committed registry (ignoring the
``generated_at`` stamp) so the Phase 5 monitor can detect drift.

Usage::

    python3 scripts/build_generated_file_registry.py            # write + summary
    python3 scripts/build_generated_file_registry.py --check    # drift check (exit 1 on diff)
    python3 scripts/build_generated_file_registry.py --strict   # fail on unattributed files
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAP_PATH = REPO_ROOT / "reports" / "verification" / "apparatus" / "generator-map.json"
DEFAULT_OUT = REPO_ROOT / "reports" / "verification" / "generated-file-registry.json"

HEAD_LINES = 15
MARKER_RE = re.compile(r"\*\*Generated\*\*:|^> Generated|<!-- GENERATED|GENERATED FILE")

# The six preregistration-tracking documents inside the mine (charter § 2).
PREREG_MINE_DOCS = (
    "protocol-errata.md",
    "decisions-log.md",
    "hypothesis-tracking.md",
    "execution-plan.md",
    "execution-checklist.md",
    "analysis-summary.md",
)


def enumerate_mine(root: Path) -> list[Path]:
    """Enumerate the mine's markdown corpus per charter § 2.

    Includes ``results/**.md``; ``reports/**.md`` excluding the
    ``reports/d17-inventory/`` audit apparatus; the ``docs/methodology``
    mine subset (top-level docs, ``reports/``, ``transparency/``, and the
    six tracking/errata docs inside ``preregistration/``); and
    ``docs/methods-outline.md``. The lodged registration is anchor-only
    (charter § 2) and is deliberately NOT enumerated.

    Args:
        root: Repository root.

    Returns:
        Sorted list of paths relative to ``root``.
    """
    files: set[Path] = set()
    files.update(root.glob("results/**/*.md"))
    files.update(
        p for p in root.glob("reports/**/*.md") if "d17-inventory" not in p.parts
    )
    methodology = root / "docs" / "methodology"
    files.update(methodology.glob("*.md"))
    files.update(methodology.glob("reports/**/*.md"))
    files.update(methodology.glob("transparency/**/*.md"))
    for name in PREREG_MINE_DOCS:
        candidate = methodology / "preregistration" / name
        if candidate.exists():
            files.add(candidate)
    outline = root / "docs" / "methods-outline.md"
    if outline.exists():
        files.add(outline)
    return sorted(p.relative_to(root) for p in files)


def scan_head(path: Path) -> tuple[str | None, str]:
    """Scan a file head for a generation marker and capture its H1 line.

    Args:
        path: Absolute path to a markdown file.

    Returns:
        Tuple of (marker line stripped, or None; first line stripped —
        the H1 signature used by disambiguating rules).
    """
    marker: str | None = None
    first_line = ""
    try:
        with path.open(encoding="utf-8", errors="replace") as fh:
            for i in range(HEAD_LINES):
                line = fh.readline()
                if not line:
                    break
                if i == 0:
                    first_line = line.strip()
                if marker is None and MARKER_RE.search(line):
                    marker = line.strip()
    except OSError:
        return None, ""
    return marker, first_line


def load_generator_map(map_path: Path) -> list[dict]:
    """Load and validate the ordered generator-map rules.

    Args:
        map_path: Path to ``generator-map.json``.

    Returns:
        List of rule dicts with compiled ``_regex`` added.

    Raises:
        ValueError: On malformed rules (missing keys, bad regex,
            duplicate rule_ids).
    """
    data = json.loads(map_path.read_text(encoding="utf-8"))
    rules = data.get("rules", [])
    seen: set[str] = set()
    required = {"rule_id", "match", "scope", "generator", "source_rule"}
    for rule in rules:
        missing = required - rule.keys()
        if missing:
            raise ValueError(f"rule {rule.get('rule_id', '?')}: missing keys {sorted(missing)}")
        if rule["rule_id"] in seen:
            raise ValueError(f"duplicate rule_id {rule['rule_id']}")
        seen.add(rule["rule_id"])
        if rule.get("stratum", "generated") not in ("generated", "hand-written"):
            raise ValueError(f"rule {rule['rule_id']}: bad stratum {rule['stratum']!r}")
        try:
            rule["_regex"] = re.compile(rule["match"])
            rule["_h1_regex"] = re.compile(rule["h1"]) if rule.get("h1") else None
        except re.error as exc:
            raise ValueError(f"rule {rule['rule_id']}: bad regex ({exc})") from exc
    return rules


def match_rule(relpath: str, has_marker: bool, rules: list[dict],
               h1: str = "") -> dict | None:
    """Return the first map rule matching a repo-relative path.

    Args:
        relpath: Repo-relative POSIX path of the file.
        has_marker: Whether the file head carries a generation marker.
        rules: Rules from :func:`load_generator_map`.
        h1: The file's first line, for rules carrying an ``h1``
            signature regex (basename collisions — three scripts write
            ``tiering_20m.md``; the H1 heading disambiguates).

    Returns:
        The matching rule, or None.
    """
    for rule in rules:
        if rule.get("requires_marker") and not has_marker:
            continue
        if not relpath.startswith(rule["scope"]):
            continue
        if not rule["_regex"].search(relpath):
            continue
        if rule["_h1_regex"] is not None and not rule["_h1_regex"].search(h1):
            continue
        return rule
    return None


def resolve_sources(root: Path, relpath: str, source_rule: str) -> list[str]:
    """Resolve a rule's source_rule to concrete committed artefact paths.

    Supported forms: ``sibling:NAME`` (file NAME in the same directory),
    ``sibling-stem:EXT`` (same stem, extension EXT), ``dir-glob:GLOB``
    (glob within the same directory), and free-text descriptions (kept
    unresolved — returned empty; the description itself stays in the
    registry row via the rule).

    Args:
        root: Repository root.
        relpath: Repo-relative path of the generated file.
        source_rule: The rule's source specification.

    Returns:
        Sorted repo-relative paths of source artefacts that exist.
    """
    parent = (root / relpath).parent
    if source_rule.startswith("sibling:"):
        candidates = [parent / source_rule.split(":", 1)[1]]
    elif source_rule.startswith("sibling-stem:"):
        ext = source_rule.split(":", 1)[1]
        candidates = [parent / (Path(relpath).stem + ext)]
    elif source_rule.startswith("dir-glob:"):
        candidates = sorted(parent.glob(source_rule.split(":", 1)[1]))
    else:
        return []
    return sorted(
        str(c.relative_to(root)) for c in candidates if c.exists() and c.is_file()
    )


def build_registry(root: Path, map_path: Path) -> dict:
    """Build the registry object for the whole mine corpus.

    Args:
        root: Repository root.
        map_path: Path to the generator map.

    Returns:
        Registry dict (see module docstring for semantics).
    """
    rules = load_generator_map(map_path)
    git_head = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=root, capture_output=True, text=True, check=True,
    ).stdout.strip()

    entries: list[dict] = []
    unattributed: list[str] = []
    for rel in enumerate_mine(root):
        relstr = rel.as_posix()
        marker, h1 = scan_head(root / rel)
        rule = match_rule(relstr, marker is not None, rules, h1)
        if rule is not None:
            stratum = rule.get("stratum", "generated")
            entry = {
                "path": relstr,
                "stratum": stratum,
                "rule_id": rule["rule_id"],
                "generator": rule["generator"] if stratum == "generated" else None,
                "source_rule": rule["source_rule"] if stratum == "generated" else None,
                "sources": (resolve_sources(root, relstr, rule["source_rule"])
                            if stratum == "generated" else []),
                "marker": marker,
                "hand_edited": bool(rule.get("hand_edited")),
            }
        elif marker is not None:
            unattributed.append(relstr)
            entry = {
                "path": relstr,
                "stratum": "generated",
                "rule_id": None,
                "generator": None,
                "source_rule": None,
                "sources": [],
                "marker": marker,
                "hand_edited": False,
            }
        else:
            entry = {
                "path": relstr,
                "stratum": "hand-written",
                "rule_id": None,
                "generator": None,
                "source_rule": None,
                "sources": [],
                "marker": None,
                "hand_edited": False,
            }
        entries.append(entry)

    generated = [e for e in entries if e["stratum"] == "generated"]
    return {
        "_meta": {
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "generator": "scripts/build_generated_file_registry.py",
            "generator_map": str(map_path.relative_to(root)),
            "git_head": git_head,
            "counts": {
                "total": len(entries),
                "generated": len(generated),
                "generated_unattributed": len(unattributed),
                "hand_written": len(entries) - len(generated),
            },
        },
        "files": entries,
    }


def registry_body(registry: dict) -> dict:
    """Return the registry minus volatile fields, for drift comparison."""
    meta = {k: v for k, v in registry["_meta"].items() if k not in ("generated_at", "git_head")}
    return {"_meta": meta, "files": registry["files"]}


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--map", type=Path, default=MAP_PATH)
    parser.add_argument("--check", action="store_true",
                        help="rebuild and diff against the committed registry (exit 1 on drift)")
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 if any marker-carrying file has no map rule")
    args = parser.parse_args(argv)

    registry = build_registry(REPO_ROOT, args.map)
    counts = registry["_meta"]["counts"]

    if args.check:
        if not args.out.exists():
            print(f"MISSING committed registry: {args.out}", file=sys.stderr)
            return 1
        committed = json.loads(args.out.read_text(encoding="utf-8"))
        if registry_body(committed) != registry_body(registry):
            print("DRIFT: rebuilt registry differs from the committed one", file=sys.stderr)
            return 1
        print(f"registry current: {counts['total']} files "
              f"({counts['generated']} generated / {counts['hand_written']} hand-written)")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(registry, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"wrote {args.out.relative_to(REPO_ROOT)}: {counts['total']} files — "
          f"{counts['generated']} generated ({counts['generated_unattributed']} unattributed), "
          f"{counts['hand_written']} hand-written")
    if counts["generated_unattributed"]:
        print("unattributed (marker, no rule):", file=sys.stderr)
        for e in registry["files"]:
            if e["stratum"] == "generated" and e["rule_id"] is None:
                print(f"  {e['path']}", file=sys.stderr)
        if args.strict:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
