#!/usr/bin/env python3
"""Validate the commitment ledger (results/commitments.json).

Checks, in order:

1. JSON Schema validation against
   ``docs/manifest-schemas/commitments.schema.json`` (which enforces the
   five-element trigger rule and the status/discharged_by/waiver
   conditionals structurally).
2. **Verbatim statements**: every ``statement`` must appear
   character-for-character within its cited line range in the cited
   lodged document (audit-charter § 6: verbatim spans are load-bearing —
   a paraphrase logged as a quote is itself a fabrication class).
3. **Waiver resolution**: every ``waiver`` E-number must exist as an
   entry heading in the errata register.
4. **ID integrity**: commitment_ids unique.
5. **Source blob pinning**: each source document's recorded git blob
   matches the working tree (detects drift between authoring and
   validation).

Exit status 0 = all checks pass; 1 = any failure (fail loudly).

Usage::

    python3 scripts/validate_commitments.py [--ledger results/commitments.json]

Intended to run standalone, from tier-1 tests, and from the Phase 5
monitoring layer (``revalidate_ledgers.py``).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "docs" / "manifest-schemas" / "commitments.schema.json"
DEFAULT_LEDGER = REPO_ROOT / "results" / "commitments.json"
ERRATA_PATH = (
    REPO_ROOT / "docs" / "methodology" / "preregistration" / "protocol-errata.md"
)


def load_json(path: Path) -> dict:
    """Load and parse a JSON file (never line-grep structured files)."""
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def schema_errors(ledger: dict) -> list[str]:
    """Return JSON Schema validation error messages (empty if valid)."""
    import jsonschema
    from referencing import Registry, Resource

    schema = load_json(SCHEMA_PATH)
    common = load_json(SCHEMA_PATH.parent / "common-defs.schema.json")
    registry = Registry().with_resources(
        [
            ("common-defs.schema.json", Resource.from_contents(common)),
            (schema["$id"], Resource.from_contents(schema)),
        ]
    )
    validator = jsonschema.Draft202012Validator(schema, registry=registry)
    return [
        f"schema: {'/'.join(str(p) for p in err.absolute_path)}: {err.message}"
        for err in validator.iter_errors(ledger)
    ]


def verbatim_errors(ledger: dict) -> list[str]:
    """Check every statement appears verbatim within its cited lines."""
    errors: list[str] = []
    file_lines: dict[str, list[str]] = {}
    for cmt in ledger.get("commitments", []):
        src = cmt["source"]
        path = src["file"]
        if path not in file_lines:
            file_lines[path] = (
                (REPO_ROOT / path).read_text(encoding="utf-8").splitlines()
            )
        lines = file_lines[path]
        lo, hi = src["lines"]
        if lo > hi or hi > len(lines):
            errors.append(
                f"{cmt['commitment_id']}: line range {lo}-{hi} invalid "
                f"for {path} ({len(lines)} lines)"
            )
            continue
        window = "\n".join(lines[lo - 1 : hi])
        if cmt["statement"] not in window:
            errors.append(
                f"{cmt['commitment_id']}: statement not found verbatim in "
                f"{path}:{lo}-{hi}"
            )
    return errors


def waiver_errors(ledger: dict) -> list[str]:
    """Check every waiver E-number exists as an errata entry heading."""
    errata_ids = set(
        re.findall(
            r"^#{2,4}\s*(E\d+):",
            ERRATA_PATH.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
    )
    return [
        f"{cmt['commitment_id']}: waiver {cmt['waiver']} not in errata register"
        for cmt in ledger.get("commitments", [])
        if cmt.get("waiver") and cmt["waiver"] not in errata_ids
    ]


def id_errors(ledger: dict) -> list[str]:
    """Check commitment_id uniqueness."""
    seen: set[str] = set()
    errors: list[str] = []
    for cmt in ledger.get("commitments", []):
        cid = cmt["commitment_id"]
        if cid in seen:
            errors.append(f"duplicate commitment_id: {cid}")
        seen.add(cid)
    return errors


def blob_errors(ledger: dict) -> list[str]:
    """Check recorded source blobs match the working tree."""
    errors: list[str] = []
    for doc in ledger.get("source_documents", []):
        actual = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "hash-object", doc["file"]],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if not actual.startswith(doc["git_blob"]):
            errors.append(
                f"source blob drift: {doc['file']} recorded {doc['git_blob']}, "
                f"working tree {actual[:12]}"
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    """Run all checks; print failures; return process exit status."""
    parser = argparse.ArgumentParser(description="Validate the commitment ledger.")
    parser.add_argument(
        "--ledger",
        type=Path,
        default=DEFAULT_LEDGER,
        help="Path to commitments.json (default: results/commitments.json)",
    )
    args = parser.parse_args(argv)

    ledger = load_json(args.ledger)
    all_errors: list[str] = []
    for check in (schema_errors, verbatim_errors, waiver_errors, id_errors, blob_errors):
        all_errors.extend(check(ledger))

    n = len(ledger.get("commitments", []))
    if all_errors:
        for err in all_errors:
            print(f"FAIL {err}")
        print(f"\n{len(all_errors)} failure(s) across {n} commitment(s)")
        return 1
    by_status: dict[str, int] = {}
    for cmt in ledger.get("commitments", []):
        by_status[cmt["status"]] = by_status.get(cmt["status"], 0) + 1
    print(f"OK {n} commitments valid; status counts: {by_status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
