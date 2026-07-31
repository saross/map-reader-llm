#!/usr/bin/env python3
"""Validate C4 extraction files (``reports/verification/c4-extraction/``).

Checks, in order (mirroring ``validate_commitments.py``):

1. JSON Schema validation against
   ``docs/manifest-schemas/c4-claims.schema.json``.
2. **Verbatim spans**: every ``claim_text`` must appear
   character-for-character within its cited line range in the source
   document (audit-charter § 6: verbatim spans are load-bearing — a
   paraphrase logged as a quote is itself a fabrication class), and
   every ``value_verbatim`` must appear within its ``claim_text``.
3. **Anchor invariants**: a null ``anchor`` is only legal for methods
   ``anchor-unknown`` / ``historical`` / ``unverifiable-era`` /
   ``external``; method ``arithmetic`` requires ``expression`` plus
   ``operands`` whose names cover the expression's variables; anchored
   files must exist in the working tree.
4. **Source blob pinning**: the recorded ``git_blob`` matches the
   working tree (detects drift between extraction and validation).

Exit status 0 = all checks pass; 1 = any failure (fail loudly).

Usage::

    python3 scripts/validate_c4_extraction.py [paths...]   # default: whole directory
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "docs" / "manifest-schemas"
DEFAULT_DIR = REPO_ROOT / "reports" / "verification" / "c4-extraction"

NULL_ANCHOR_METHODS = {"anchor-unknown", "historical", "unverifiable-era", "external"}
_VAR_RE = re.compile(r"\b([a-z])\b")


def build_validator() -> jsonschema.Draft202012Validator:
    """Build a schema validator with the local $ref registry."""
    schema = json.loads((SCHEMA_DIR / "c4-claims.schema.json").read_text(encoding="utf-8"))
    common = json.loads((SCHEMA_DIR / "common-defs.schema.json").read_text(encoding="utf-8"))
    registry = Registry().with_resource(
        "common-defs.schema.json", Resource.from_contents(common)
    )
    return jsonschema.Draft202012Validator(schema, registry=registry)


def git_blob(path: str) -> str | None:
    """Return the working-tree blob hash of a repo-relative file."""
    try:
        out = subprocess.run(["git", "hash-object", path], cwd=REPO_ROOT,
                             capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        return None
    return out.stdout.strip()


def validate_file(path: Path, validator: jsonschema.Draft202012Validator) -> list[str]:
    """Validate one extraction file; return a list of error strings."""
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path.name}: unreadable ({exc})"]

    for err in validator.iter_errors(data):
        errors.append(f"{path.name}: schema: {err.message} at {list(err.absolute_path)}")
    if errors:
        return errors  # structural failures make the rest unreliable

    src = data["source_document"]["file"]
    src_path = REPO_ROOT / src
    if not src_path.exists():
        return [f"{path.name}: source document missing: {src}"]
    src_lines = src_path.read_text(encoding="utf-8", errors="replace").splitlines()

    blob = git_blob(src)
    recorded = data["source_document"]["git_blob"]
    if blob is None or not blob.startswith(recorded):
        errors.append(f"{path.name}: git_blob {recorded} does not match working tree {blob}")

    for i, claim in enumerate(data["claims"]):
        tag = f"{path.name}#{i}"
        lo, hi = claim["source"]["lines"]
        if not (1 <= lo <= hi <= len(src_lines)):
            errors.append(f"{tag}: line range {lo}-{hi} outside document (1-{len(src_lines)})")
            continue
        window = "\n".join(src_lines[lo - 1:hi])
        text = claim["claim_text"]
        if text not in window:
            errors.append(f"{tag}: claim_text not verbatim within lines {lo}-{hi}")
        for j, value in enumerate(claim["values"]):
            if value["value_verbatim"] not in text:
                errors.append(f"{tag}: values[{j}] verbatim {value['value_verbatim']!r} "
                              "not inside claim_text")

        method = claim["method"]
        anchor = claim["anchor"]
        # Effective methods include per-value overrides (v1.2: the
        # first recompute run surfaced 12 effective-arithmetic values
        # with no expression — the claim-level-only check missed them).
        effective = {value.get("method") or method for value in claim["values"]}
        if anchor is None:
            if not effective <= NULL_ANCHOR_METHODS:
                errors.append(f"{tag}: null anchor illegal for effective methods "
                              f"{sorted(effective - NULL_ANCHOR_METHODS)}")
            continue
        if not (REPO_ROOT / anchor["file"]).exists():
            errors.append(f"{tag}: anchor file missing: {anchor['file']}")
        # Each effective-arithmetic value needs an expression: its own
        # (schema 1.1 per-value form) or the claim anchor's (legal for
        # exactly one derived value per claim).
        for j, value in enumerate(claim["values"]):
            if (value.get("method") or method) != "arithmetic":
                continue
            source = value if value.get("expression") else anchor
            expr = source.get("expression")
            operands = source.get("operands") or []
            if not expr or not operands:
                errors.append(f"{tag}: arithmetic requires expression + operands"
                              f" (values[{j}])")
                continue
            names = {op["name"] for op in operands}
            used = set(_VAR_RE.findall(expr))
            if not used <= names:
                errors.append(f"{tag}: expression vars {sorted(used - names)} "
                              f"missing from operands (values[{j}])")
            for op in operands:
                if not (REPO_ROOT / op["file"]).exists():
                    errors.append(f"{tag}: operand file missing: {op['file']}")
    return errors


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path,
                        help="extraction files (default: all in the c4-extraction directory)")
    args = parser.parse_args(argv)

    paths = args.paths or sorted(DEFAULT_DIR.glob("*.json"))
    if not paths:
        print("no extraction files found", file=sys.stderr)
        return 1
    validator = build_validator()
    failures = 0
    total_claims = 0
    for path in paths:
        errs = validate_file(Path(path), validator)
        if errs:
            failures += 1
            for e in errs:
                print(e, file=sys.stderr)
        else:
            n = len(json.loads(Path(path).read_text(encoding="utf-8"))["claims"])
            total_claims += n
            print(f"ok {Path(path).name}: {n} claims")
    if failures:
        print(f"FAIL: {failures}/{len(paths)} files with errors", file=sys.stderr)
        return 1
    print(f"all {len(paths)} files valid; {total_claims} claims")
    return 0


if __name__ == "__main__":
    sys.exit(main())
