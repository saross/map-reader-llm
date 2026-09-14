#!/usr/bin/env python3
"""
Content anchors for INPUT manifests that declare provenance from another set.

This extends the content-anchor discipline of
``reports/name-keyed-cache-audit-2026-09-12.md`` (and the fixes landed in pull
request (PR) #14) from *derived* artefacts — caches, unions, evaluations — to
the **input manifests and the few-shot example library**. The defect class is
the same shape: an artefact is bound to its source by a **name** (``"selected
from the training tiles"``, ``"reference_bounds": "…/validation_bounds.geojson"``)
rather than by the **content** of that source. Re-select the source under the
same name and nothing errors; the dependent artefact simply goes on declaring a
provenance it no longer has.

Erratum **E86** is the demonstrated instance. The three null exemplars in
``inputs/examples/null-tiles/null_tiles_manifest.json`` were selected on
2025-12-23 from ``inputs/training_manifest.json`` (commit ``3f66fc3f8``, blob
``c5056693d…``). On 2026-01-04 (``4d011a839``) that set was re-selected under a
new seed; only 3 of the 20 earlier tiles survived and none of the three null
tiles did. The null manifest was never regenerated, so it still declares a pool
it is no longer drawn from — and, because the evaluation exclusion geometry was
built from the *current* calibration set, the three null tiles were never
excluded from evaluation.

**What this script does**: for every dependency in the registry
(``inputs/provenance/manifest-dependencies.json``) it compares the source's
recorded blob hash against the source file's hash on disk today, and reports
``CURRENT`` or ``STALE``.

**Two check modes, and why there are two**

* ``--check`` is the raw guard: exit 1 if ANY dependency is stale. This is what
  a rebuild script or a pre-flight should call — "is every declared provenance
  literally true right now?"
* ``--check-expected`` compares each dependency's observed state against the
  ``expect`` field the registry records for it, and exits 1 only on a
  *disagreement*. This is the mode the tier-1 test runs. E86's staleness is a
  settled, documented fact that will not be repaired (the library cannot be
  rebuilt without invalidating every run that used it — E86 remediation 2), so
  a bare ``--check`` in continuous integration would be permanently red, and a
  permanently red guard is an ignored guard. ``--check-expected`` stays green
  on the documented staleness and turns red the moment a **new** source is
  re-selected under an old declaration, which is the event worth catching.

Every ``expect: "stale"`` row must name an ``erratum``, so the registry cannot
be used to quietly normalise an undocumented divergence.

Usage::

    # Human-readable report over every declared dependency
    python scripts/check_manifest_provenance.py

    # Raw guard — exit 1 on any stale declaration (E86 makes this exit 1 today)
    python scripts/check_manifest_provenance.py --check

    # Expectation guard — exit 1 only on an UNDECLARED change (the tier-1 gate)
    python scripts/check_manifest_provenance.py --check-expected

    # JSON for a report or a downstream check
    python scripts/check_manifest_provenance.py --json

    # After a deliberate, documented rebuild: re-stamp one row's source anchor
    python scripts/check_manifest_provenance.py --restamp null-tiles-from-calibration

Inputs:
    - ``inputs/provenance/manifest-dependencies.json`` — the registry (or any
      path given to ``--registry``)
    - the artefact and source files the registry names

Outputs:
    - stdout report (or JSON with ``--json``)
    - exit code 0/1 per the mode above

Created: 2026-09-13 (E86 remediation 4)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from lib_content_anchor import git_blob_hash  # noqa: E402

#: Schema tag the registry must declare, so a future format change is visible.
REGISTRY_SCHEMA = "manifest-provenance-registry/1"

#: Default registry location, relative to the repository root.
DEFAULT_REGISTRY = Path("inputs/provenance/manifest-dependencies.json")

#: Observed states.
CURRENT = "CURRENT"
STALE = "STALE"
SOURCE_MISSING = "SOURCE-MISSING"
ARTEFACT_MISSING = "ARTEFACT-MISSING"

#: States the registry may legitimately expect. Anything else is a schema error.
VALID_EXPECTATIONS = (CURRENT, STALE)


def repo_root() -> Path:
    """Return the repository root (the parent of this script's directory)."""
    return Path(__file__).resolve().parent.parent


def load_registry(path: Path) -> dict[str, Any]:
    """Load and schema-check the dependency registry.

    Args:
        path: Registry JSON path.

    Returns:
        The parsed registry.

    Raises:
        SystemExit: If the file is absent, unparseable, carries an unexpected
            schema tag, or contains a dependency that violates the registry's
            own rules (unknown ``expect`` value, or ``expect: "stale"`` with no
            erratum named).
    """
    if not path.is_file():
        sys.exit(f"ERROR: registry not found: {path}")
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"ERROR: registry is not valid JSON ({path}): {exc}")

    schema = registry.get("schema")
    if schema != REGISTRY_SCHEMA:
        sys.exit(
            f"ERROR: registry schema is {schema!r}, expected {REGISTRY_SCHEMA!r}"
        )

    seen: set[str] = set()
    for dep in registry.get("dependencies", []):
        dep_id = dep.get("id")
        if not dep_id:
            sys.exit("ERROR: a dependency has no 'id'")
        if dep_id in seen:
            sys.exit(f"ERROR: duplicate dependency id {dep_id!r}")
        seen.add(dep_id)
        expect = dep.get("expect", CURRENT)
        if expect not in VALID_EXPECTATIONS:
            sys.exit(
                f"ERROR: dependency {dep_id!r} expects {expect!r}; "
                f"valid values are {VALID_EXPECTATIONS}"
            )
        if expect == STALE and not dep.get("erratum"):
            sys.exit(
                f"ERROR: dependency {dep_id!r} expects STALE but names no "
                f"erratum. A tolerated divergence must be documented."
            )
        if not dep.get("sources"):
            sys.exit(f"ERROR: dependency {dep_id!r} declares no sources")
    return registry


def evaluate_dependency(dep: dict[str, Any], root: Path) -> dict[str, Any]:
    """Compare one dependency's declared source anchors against disk.

    A dependency may declare several sources; the dependency is ``CURRENT``
    only when every source's blob hash still matches the anchor recorded for
    it. Missing files are reported as their own states rather than folded into
    ``STALE``, because "the file is gone" and "the file changed" call for
    different responses.

    Args:
        dep: One registry dependency entry.
        root: Repository root that the registry's relative paths resolve
            against.

    Returns:
        A result dict with the observed ``state``, the per-source detail, and
        whether the observation matches the registry's expectation.
    """
    artefact = root / dep["artefact"]
    sources: list[dict[str, Any]] = []
    state = CURRENT

    if not artefact.is_file():
        state = ARTEFACT_MISSING

    for src in dep["sources"]:
        src_path = root / src["path"]
        observed = git_blob_hash(src_path)
        declared = src["declared_blob"]
        if observed is None:
            src_state = SOURCE_MISSING
        elif observed == declared:
            src_state = CURRENT
        else:
            src_state = STALE
        sources.append({
            "path": src["path"],
            "declared_blob": declared,
            "observed_blob": observed,
            "state": src_state,
            "anchor_basis": src.get("anchor_basis", "registry-creation"),
            "declared_at": src.get("declared_at"),
            "declared_at_commit": src.get("declared_at_commit"),
        })
        # Precedence: a missing file is the loudest state, then a changed one.
        if src_state == SOURCE_MISSING:
            state = SOURCE_MISSING
        elif src_state == STALE and state == CURRENT:
            state = STALE

    expect = dep.get("expect", CURRENT)
    return {
        "id": dep["id"],
        "artefact": dep["artefact"],
        "declares": dep.get("declares"),
        "erratum": dep.get("erratum"),
        "expect": expect,
        "state": state,
        "as_expected": state == expect,
        "sources": sources,
    }


def evaluate_registry(registry: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    """Evaluate every dependency in *registry* against the tree at *root*."""
    return [evaluate_dependency(dep, root) for dep in registry["dependencies"]]


def format_report(results: list[dict[str, Any]]) -> str:
    """Render the human-readable report.

    Args:
        results: Output of :func:`evaluate_registry`.

    Returns:
        The report text (no trailing newline).
    """
    lines = ["Manifest provenance anchors", "=" * 27, ""]
    width = max((len(r["id"]) for r in results), default=0)
    for res in results:
        flag = "ok " if res["as_expected"] else "!! "
        note = ""
        if res["state"] == STALE and res["erratum"]:
            note = f"  (documented: {res['erratum']})"
        elif res["state"] == STALE:
            note = "  (UNDOCUMENTED — no erratum named)"
        lines.append(
            f"{flag}{res['id']:<{width}}  {res['state']:<16}"
            f"expected {res['expect']}{note}"
        )
        lines.append(f"    artefact: {res['artefact']}")
        for src in res["sources"]:
            obs = src["observed_blob"] or "—"
            lines.append(
                f"    source:   {src['path']}  [{src['state']}]"
            )
            if src["state"] != CURRENT:
                lines.append(
                    f"              declared {src['declared_blob'][:12]} "
                    f"({src['anchor_basis']}, {src['declared_at']}) "
                    f"→ on disk {obs[:12]}"
                )
        lines.append("")

    n_stale = sum(1 for r in results if r["state"] == STALE)
    n_unexpected = sum(1 for r in results if not r["as_expected"])
    lines.append(
        f"{len(results)} dependencies: {len(results) - n_stale} current, "
        f"{n_stale} stale ({n_unexpected} not as declared)."
    )
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    """Construct the command-line interface parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Verify that every input manifest declaring provenance from "
            "another set still names the content it was built from."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Modes:\n"
            "  (default)          print the report, always exit 0\n"
            "  --check            exit 1 if ANY declaration is stale\n"
            "  --check-expected   exit 1 only when the observed state differs\n"
            "                     from the registry's 'expect' field\n"
        ),
    )
    parser.add_argument(
        "--registry", type=Path, default=None,
        help=f"Registry path (default: {DEFAULT_REGISTRY})",
    )
    parser.add_argument(
        "--root", type=Path, default=None,
        help="Repository root the registry's paths resolve against.",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Exit 1 if any declared provenance is stale.",
    )
    parser.add_argument(
        "--check-expected", action="store_true",
        help="Exit 1 only when an observation differs from its expectation.",
    )
    parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Emit the results as JSON instead of the text report.",
    )
    parser.add_argument(
        "--restamp", metavar="ID", default=None,
        help=(
            "Re-record the current source blob hashes for one dependency "
            "(use only after a deliberate, documented rebuild)."
        ),
    )
    return parser


def restamp(registry_path: Path, registry: dict[str, Any], dep_id: str,
            root: Path) -> int:
    """Re-record a dependency's source anchors from the files on disk.

    The legitimate workflow after a deliberate rebuild: the declaration is now
    true of today's source, so the anchor should say so. Writes the registry
    back in place and prints what changed.

    Args:
        registry_path: Where to write the updated registry.
        registry: The loaded registry (mutated).
        dep_id: The dependency to re-stamp.
        root: Repository root for relative paths.

    Returns:
        Process exit code (0 on success, 1 if the id is unknown or a source
        file is missing).
    """
    for dep in registry["dependencies"]:
        if dep["id"] != dep_id:
            continue
        for src in dep["sources"]:
            observed = git_blob_hash(root / src["path"])
            if observed is None:
                print(f"ERROR: source missing: {src['path']}", file=sys.stderr)
                return 1
            if observed != src["declared_blob"]:
                print(
                    f"{src['path']}: {src['declared_blob'][:12]} "
                    f"→ {observed[:12]}"
                )
                src["declared_blob"] = observed
                src["anchor_basis"] = "restamped"
        registry_path.write_text(
            json.dumps(registry, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"re-stamped {dep_id} in {registry_path}")
        return 0
    print(f"ERROR: no dependency with id {dep_id!r}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns a process exit code."""
    args = _build_parser().parse_args(argv)
    root = args.root.resolve() if args.root else repo_root()
    registry_path = args.registry if args.registry else root / DEFAULT_REGISTRY
    registry = load_registry(registry_path)

    if args.restamp:
        return restamp(registry_path, registry, args.restamp, root)

    results = evaluate_registry(registry, root)

    if args.as_json:
        print(json.dumps({"registry": str(registry_path), "results": results},
                         indent=1))
    else:
        print(format_report(results))

    if args.check:
        stale = [r["id"] for r in results if r["state"] != CURRENT]
        if stale:
            print(
                f"\n--check FAILED: {len(stale)} declaration(s) not current: "
                f"{', '.join(stale)}",
                file=sys.stderr,
            )
            return 1
        return 0

    if args.check_expected:
        bad = [r["id"] for r in results if not r["as_expected"]]
        if bad:
            print(
                f"\n--check-expected FAILED: {len(bad)} dependency/ies differ "
                f"from the registry's expectation: {', '.join(bad)}",
                file=sys.stderr,
            )
            return 1
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
