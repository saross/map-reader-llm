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
``generated_at`` stamp and the ``git_head`` source-commit stamp) so the
Phase 5 monitor — and the registry's own test — can detect drift.

**Charter extension, 2026-09-13** (checklist item 11a;
``planning/interim-docs-review.md`` § 11.5 item 3): the corpus now also
enumerates ``outputs/**/*.md``. The May charter covered ``results/``,
``reports/`` and part of ``docs/methodology`` only, so the three
``outputs/`` document classes the revision-policy table registers
(``post_run_report.md``, ``experiment_intent.md``, ``evaluation.md``,
plus ``pre_launch_audit.md``) had no classification at all — and it is
those classes that the 2026-09-11 generated-projections ruling governs.

**Regime-2 audit fields, 2026-09-13** (checklist item 11b). The same
ruling gives a generated Markdown projection three obligations: a
``GENERATED FILE`` banner, a source-commit stamp, and a ``--check`` drift
guard exercised by a test. Every generated row therefore records
whether the *document* carries the banner and the stamp, and whether its
*generator* offers a ``--check`` mode with a tier-1 test that runs it —
so "which generated documents are in neither compliance regime?" is a
query over the registry rather than a hand audit.

Usage::

    python3 scripts/build_generated_file_registry.py            # write + summary
    python3 scripts/build_generated_file_registry.py --check    # drift check (exit 1 on diff)
    python3 scripts/build_generated_file_registry.py --strict   # fail on unattributed files
    python3 scripts/build_generated_file_registry.py --gaps     # list regime-2 gaps
"""

from __future__ import annotations

import argparse
import ast
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

#: The 2026-09-11 ruling's banner. Narrower than ``MARKER_RE`` on purpose: a
#: bare ``**Generated**:`` timestamp is a *claim about when the file was
#: written*, not the "do not hand-edit, here is the generator" banner the
#: ruling asks for. All 46 ``outputs/**/evaluation.md`` files carry the former
#: and none the latter, which is exactly the distinction the audit drew.
REGIME2_BANNER_RE = re.compile(r"GENERATED FILE", re.IGNORECASE)

#: A source-commit stamp: a git hash the document names as the commit its
#: inputs were read at. Requires the hash, so prose about commits does not
#: count (e.g. "put before/after notes in the commit message").
SOURCE_COMMIT_RE = re.compile(r"commit[s]?\s+`?[0-9a-f]{7,40}`?", re.IGNORECASE)

#: A ``--check``-family CLI mode is read out of the generator's argparse
#: declarations, not grepped for: a quoted ``check-…`` string is as likely to
#: be ``git check-ignore`` as a drift mode (it is, in
#: ``scripts/evaluate_detections.py``), and crediting 2,396 cell evaluations
#: with a drift guard on that evidence would make the whole audit worthless.
CHECK_MODE_PREFIX = "--check"

TESTS_DIR = REPO_ROOT / "tests"

#: Directory buckets for the per-directory counts in ``_meta``.
DIR_BUCKETS = ("results/", "reports/", "outputs/", "docs/")

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
    ``reports/d17-inventory/`` audit apparatus; ``outputs/**.md`` (the
    2026-09-13 charter extension — see the module docstring); the
    ``docs/methodology`` mine subset (top-level docs, ``reports/``,
    ``transparency/``, and the six tracking/errata docs inside
    ``preregistration/``); and ``docs/methods-outline.md``. The lodged
    registration is anchor-only (charter § 2) and is deliberately NOT
    enumerated.

    ``outputs/`` is enumerated in full, literature notes included: the
    registry's job is to classify what is in the tree, not to decide what
    the revision policy covers, and an exclusion list would be one more
    place for a class to hide.

    Args:
        root: Repository root.

    Returns:
        Sorted list of paths relative to ``root``.
    """
    files: set[Path] = set()
    files.update(root.glob("results/**/*.md"))
    files.update(root.glob("outputs/**/*.md"))
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


def head_lines(path: Path, n: int = HEAD_LINES) -> list[str]:
    """Return the first ``n`` lines of a file, or ``[]`` if unreadable.

    Args:
        path: Absolute path to a text file.
        n: Number of lines to read.

    Returns:
        The lines with trailing newlines stripped.
    """
    lines: list[str] = []
    try:
        with path.open(encoding="utf-8", errors="replace") as fh:
            for _ in range(n):
                line = fh.readline()
                if not line:
                    break
                lines.append(line.rstrip("\n"))
    except OSError:
        return []
    return lines


def scan_regime2(path: Path) -> tuple[bool, bool]:
    """Scan a document head for the 2026-09-11 ruling's two document-side marks.

    Args:
        path: Absolute path to a markdown file.

    Returns:
        Tuple of (carries a ``GENERATED FILE`` banner, carries a
        source-commit stamp naming a git hash).
    """
    head = "\n".join(head_lines(path))
    return bool(REGIME2_BANNER_RE.search(head)), bool(SOURCE_COMMIT_RE.search(head))


def load_test_index(root: Path) -> list[tuple[str, str, bool]]:
    """Index every test module's source, once per build.

    Read once and reused for every generator: the alternative (re-walking
    ``tests/`` per generator) is ~60 × 250 file reads.

    Args:
        root: Repository root.

    Returns:
        List of (repo-relative test path, source text, carries a tier-1
        marker), one entry per test module.
    """
    index: list[tuple[str, str, bool]] = []
    tests_root = root / "tests"
    if not tests_root.is_dir():
        return index
    for test_path in sorted(tests_root.rglob("test_*.py")):
        text = test_path.read_text(encoding="utf-8", errors="replace")
        index.append((test_path.relative_to(root).as_posix(), text,
                      "tier1" in text))
    return index


def discover_check_modes(source: str) -> set[str]:
    """Return the ``check``-family CLI modes a generator's argparse declares.

    Parsed, not grepped. Two spellings count, and only from an
    ``add_argument`` call:

    * an option whose flag starts with ``--check`` (e.g. ``--check``,
      ``--check-renderings``);
    * a subcommand verb in a positional's ``choices`` — ``check`` itself or
      ``check-<something>``, as ``scripts/build_gs_era2_board.py`` spells
      ``check-renderings``.

    Args:
        source: The generator's source text.

    Returns:
        The declared mode strings. Empty for a file that will not parse
        (a shell script given a ``.py`` rule, say) — reported as "no
        check mode", which is the safe direction to be wrong in.
    """
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return set()
    modes: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        if name != "add_argument":
            continue
        for arg in node.args:
            if (isinstance(arg, ast.Constant) and isinstance(arg.value, str)
                    and arg.value.startswith(CHECK_MODE_PREFIX)):
                modes.add(arg.value)
        for keyword in node.keywords:
            if keyword.arg != "choices" or not isinstance(
                    keyword.value, (ast.List, ast.Tuple, ast.Set)):
                continue
            for element in keyword.value.elts:
                if (isinstance(element, ast.Constant)
                        and isinstance(element.value, str)
                        and (element.value == "check"
                             or element.value.startswith("check-"))):
                    modes.add(element.value)
    return modes


def check_tokens(flags: set[str]) -> set[str]:
    """Return the strings a test may use to exercise these CLI check modes.

    A test drives a check mode either through the CLI string
    (``main(["--check"])``) or through the function the mode calls
    (``check_renderings(board)``), so a named mode contributes both its CLI
    spelling and that spelling as an identifier. The bare ``--check``
    contributes only itself: ``check`` as a substring would match almost
    any test module.

    Args:
        flags: CLI check modes found in a generator's source.

    Returns:
        The set of strings that count as evidence in a test module.
    """
    tokens = set(flags)
    for flag in flags:
        bare = flag.lstrip("-")
        if bare != "check":
            tokens.add(bare.replace("-", "_"))
    return tokens


def generator_guards(root: Path, generator: str,
                     test_index: list[tuple[str, str, bool]],
                     cache: dict[str, dict] | None = None) -> dict:
    """Report a generator's drift-guard apparatus, read from its own source.

    Deterministic and evidence-based, with no hand-maintained list: the
    ``--check`` verdict is the set of ``--check``-family CLI modes in the
    generator's own source, and a test counts only if it names the
    generator (by module stem) **and** uses one of that generator's own
    check modes (:func:`check_tokens`) — so a test that happens to mention
    some other script's ``--check`` cannot be credited here.

    Args:
        root: Repository root.
        generator: Repo-relative path of the generator script (a rule's
            ``generator`` field), e.g. ``scripts/generate_run_reports.py``.
        test_index: Output of :func:`load_test_index`.
        cache: Optional memo dict, keyed by ``generator``.

    Returns:
        Dict with ``generator_present``, ``check_mode`` (bool),
        ``check_flags`` (sorted list), ``check_tests`` (sorted list of
        repo-relative test paths), ``tier1_check_test`` (bool).
    """
    if cache is not None and generator in cache:
        return cache[generator]
    gen_path = root / generator
    flags: set[str] = set()
    present = gen_path.is_file()
    if present:
        flags = discover_check_modes(
            gen_path.read_text(encoding="utf-8", errors="replace"))
    stem = Path(generator).stem
    tokens = check_tokens(flags)
    tier1_tests: list[str] = []
    any_tests: list[str] = []
    for rel, text, is_tier1 in test_index:
        if stem not in text:
            continue
        if not any(token in text for token in tokens):
            continue
        any_tests.append(rel)
        if is_tier1:
            tier1_tests.append(rel)
    guards = {
        "generator_present": present,
        "check_mode": bool(flags),
        "check_flags": sorted(flags),
        "check_tests": sorted(any_tests),
        "tier1_check_test": bool(tier1_tests),
    }
    if cache is not None:
        cache[generator] = guards
    return guards


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

    test_index = load_test_index(root)
    guard_cache: dict[str, dict] = {}

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
        if entry["stratum"] == "generated":
            entry.update(regime2_fields(root, relstr, entry["generator"],
                                        test_index, guard_cache))
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
                "by_directory": count_by_directory(entries),
                "regime2": count_regime2(generated),
            },
        },
        "files": entries,
    }


def regime2_fields(root: Path, relpath: str, generator: str | None,
                   test_index: list[tuple[str, str, bool]],
                   guard_cache: dict[str, dict]) -> dict:
    """Return the 2026-09-11 ruling's audit fields for one generated document.

    Args:
        root: Repository root.
        relpath: Repo-relative path of the generated document.
        generator: Its generator script, or None (unattributed).
        test_index: Output of :func:`load_test_index`.
        guard_cache: Memo dict shared across the build.

    Returns:
        Dict with ``generated_banner``, ``source_commit_stamp``,
        ``check_mode``, ``check_flags``, ``check_tests``,
        ``tier1_check_test`` and ``regime2_compliant`` — the conjunction
        of banner, stamp and tier-1-tested check mode.
    """
    banner, stamp = scan_regime2(root / relpath)
    if generator:
        guards = generator_guards(root, generator, test_index, guard_cache)
    else:
        guards = {"generator_present": False, "check_mode": False,
                  "check_flags": [], "check_tests": [],
                  "tier1_check_test": False}
    return {
        "generated_banner": banner,
        "source_commit_stamp": stamp,
        "check_mode": guards["check_mode"],
        "check_flags": guards["check_flags"],
        "check_tests": guards["check_tests"],
        "tier1_check_test": guards["tier1_check_test"],
        "regime2_compliant": bool(
            banner and stamp and guards["check_mode"] and guards["tier1_check_test"]),
    }


def count_by_directory(entries: list[dict]) -> dict:
    """Count total / generated / hand-written per top-level corpus bucket.

    Args:
        entries: The registry's file rows.

    Returns:
        Mapping bucket → {total, generated, hand_written}. Paths outside
        every bucket land in ``other``.
    """
    buckets: dict[str, dict] = {
        b: {"total": 0, "generated": 0, "hand_written": 0}
        for b in (*DIR_BUCKETS, "other")
    }
    for entry in entries:
        bucket = next((b for b in DIR_BUCKETS if entry["path"].startswith(b)), "other")
        buckets[bucket]["total"] += 1
        key = "generated" if entry["stratum"] == "generated" else "hand_written"
        buckets[bucket][key] += 1
    return buckets


def count_regime2(generated: list[dict]) -> dict:
    """Summarise regime-2 compliance over the generated stratum.

    Args:
        generated: The registry's generated rows (already carrying the
            :func:`regime2_fields` keys).

    Returns:
        Mapping with the four requirement counts, the conjunction
        (``compliant``), and ``neither_regime`` — generated documents with
        no ``GENERATED FILE`` banner at all, which is the audit's state-3
        population.
    """
    return {
        "generated_banner": sum(1 for e in generated if e["generated_banner"]),
        "source_commit_stamp": sum(1 for e in generated if e["source_commit_stamp"]),
        "check_mode": sum(1 for e in generated if e["check_mode"]),
        "tier1_check_test": sum(1 for e in generated if e["tier1_check_test"]),
        "compliant": sum(1 for e in generated if e["regime2_compliant"]),
        "neither_regime": sum(1 for e in generated if not e["generated_banner"]),
    }


def registry_body(registry: dict) -> dict:
    """Return the registry minus volatile fields, for drift comparison."""
    meta = {k: v for k, v in registry["_meta"].items() if k not in ("generated_at", "git_head")}
    return {"_meta": meta, "files": registry["files"]}


def print_regime2_gaps(registry: dict, stream=sys.stdout) -> int:
    """Print the generated documents that fail a regime-2 requirement.

    Grouped by generator, because the fix is always a generator change:
    one ``--check`` mode and one banner close every document a generator
    owns at once.

    Args:
        registry: A built registry object.
        stream: Output stream (injectable for tests).

    Returns:
        The number of non-compliant generated documents.
    """
    gaps: dict[str, list[dict]] = {}
    for entry in registry["files"]:
        if entry["stratum"] != "generated" or entry.get("regime2_compliant"):
            continue
        gaps.setdefault(entry["generator"] or "(unattributed)", []).append(entry)
    total = sum(len(v) for v in gaps.values())
    print(f"{total} generated document(s) fail a regime-2 requirement, "
          f"over {len(gaps)} generator(s):", file=stream)
    for generator, rows in sorted(gaps.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        first = rows[0]
        missing = [
            name for name, ok in (
                ("banner", all(r["generated_banner"] for r in rows)),
                ("source-commit stamp", all(r["source_commit_stamp"] for r in rows)),
                ("--check mode", first["check_mode"]),
                ("tier-1 check test", first["tier1_check_test"]),
            ) if not ok
        ]
        print(f"  {len(rows):>4}  {generator}  — missing: {', '.join(missing)}",
              file=stream)
        for row in rows[:3]:
            print(f"          {row['path']}", file=stream)
        if len(rows) > 3:
            print(f"          … and {len(rows) - 3} more", file=stream)
    return total


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--map", type=Path, default=MAP_PATH)
    parser.add_argument("--check", action="store_true",
                        help="rebuild and diff against the committed registry (exit 1 on drift)")
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 if any marker-carrying file has no map rule")
    parser.add_argument("--gaps", action="store_true",
                        help="list the generated documents that fail a "
                             "regime-2 requirement (banner / source-commit "
                             "stamp / tested --check), then exit 0")
    args = parser.parse_args(argv)

    registry = build_registry(REPO_ROOT, args.map)
    counts = registry["_meta"]["counts"]

    if args.gaps:
        print_regime2_gaps(registry)
        return 0

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
    # ``--out`` may point outside the repository (a preview build in scratch
    # space); fall back to the absolute path rather than raising.
    try:
        shown = args.out.relative_to(REPO_ROOT)
    except ValueError:
        shown = args.out
    print(f"wrote {shown}: {counts['total']} files — "
          f"{counts['generated']} generated ({counts['generated_unattributed']} unattributed), "
          f"{counts['hand_written']} hand-written")
    for bucket, sub in counts["by_directory"].items():
        if sub["total"]:
            print(f"  {bucket:<12} {sub['total']:>5} "
                  f"({sub['generated']} generated / {sub['hand_written']} hand-written)")
    r2 = counts["regime2"]
    print(f"  regime 2: {r2['compliant']} of {counts['generated']} generated fully "
          f"compliant — banner {r2['generated_banner']}, source-commit stamp "
          f"{r2['source_commit_stamp']}, --check {r2['check_mode']}, tier-1 test "
          f"{r2['tier1_check_test']}; {r2['neither_regime']} carry no banner")
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
