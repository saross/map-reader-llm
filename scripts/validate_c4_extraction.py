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
   files must exist in the working tree; in a multi-value claim whose
   anchor carries a path, every effective-``read`` value must carry its
   own ``path`` (instrument v1.2 amendment 3 — the recompute harness
   refuses the anchor-path fallback there, because it silently compares
   the wrong quantity; Obs 379).
4. **Source blob pinning**: the recorded ``git_blob`` matches the
   working tree (detects drift between extraction and validation).

**Era mode** (``--at-era``): checks 2 and 4 above assume a stationary
corpus — that a source document has not moved since it was extracted.
That assumption fails by design in this programme: ruling 1 (dated-
snapshot corrections), ruling 17 (living documents refreshed in place)
and every repair wave rewrite mine documents *after* their claims were
extracted, at which point the working-tree body no longer carries the
spans the extraction faithfully quoted. Under ``--at-era`` the source
body is resolved from the recorded ``git_blob`` instead of the working
tree, so verbatim spans are checked against the text the extractor
actually read; blob drift is then reported as an informational note
rather than an error. This is the same era logic ruling 9 gave the
recompute harness for anchor resolution, applied to document bodies.
Anchor and operand file existence is still checked against the working
tree in both modes — anchors are artefacts the harness resolves today,
not text the extractor quoted.

Exit status 0 = all checks pass; 1 = any failure (fail loudly).

Usage::

    python3 scripts/validate_c4_extraction.py [paths...]   # default: whole directory
    python3 scripts/validate_c4_extraction.py --at-era     # verbatim checks at each
                                                           # file's extraction blob
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


def blob_text(blob: str) -> str | None:
    """Return the contents of a git blob, or None if it is unresolvable."""
    try:
        out = subprocess.run(["git", "cat-file", "-p", blob], cwd=REPO_ROOT,
                             capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        return None
    return out.stdout


def check_arithmetic(tag: str, index: int, source: dict) -> list[str]:
    """Check one arithmetic derivation's expression and operands.

    ``source`` is whichever object supplies the derivation — the value
    itself (schema 1.1 per-value form) or the claim anchor. Returns the
    error strings for that derivation.
    """
    errors: list[str] = []
    expr = source.get("expression")
    operands = source.get("operands") or []
    if not expr or not operands:
        return [f"{tag}: arithmetic requires expression + operands (values[{index}])"]
    names = {op["name"] for op in operands}
    used = set(_VAR_RE.findall(expr))
    if not used <= names:
        errors.append(f"{tag}: expression vars {sorted(used - names)} "
                      f"missing from operands (values[{index}])")
    for op in operands:
        if not (REPO_ROOT / op["file"]).exists():
            errors.append(f"{tag}: operand file missing: {op['file']}")
    return errors


def validate_file(path: Path, validator: jsonschema.Draft202012Validator,
                  at_era: bool = False) -> tuple[list[str], list[str]]:
    """Validate one extraction file.

    Returns ``(errors, notes)``. Notes are informational only and never
    affect exit status; under ``at_era`` they carry the blob-drift
    report that is an error in working-tree mode.
    """
    errors: list[str] = []
    notes: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path.name}: unreadable ({exc})"], notes

    for err in validator.iter_errors(data):
        errors.append(f"{path.name}: schema: {err.message} at {list(err.absolute_path)}")
    if errors:
        return errors, notes  # structural failures make the rest unreliable

    src = data["source_document"]["file"]
    src_path = REPO_ROOT / src
    if not src_path.exists() and not at_era:
        return [f"{path.name}: source document missing: {src}"], notes

    blob = git_blob(src) if src_path.exists() else None
    recorded = data["source_document"]["git_blob"]
    drifted = blob is None or not blob.startswith(recorded)

    if at_era:
        # Check the spans against the body the extractor actually read.
        # A document deleted or rewritten since extraction is fine here —
        # the blob is the authority — but an unresolvable blob is not.
        text = blob_text(recorded)
        if text is None:
            return [f"{path.name}: recorded git_blob {recorded} is unresolvable "
                    "(object missing from the repository)"], notes
        src_lines = text.splitlines()
        if drifted:
            notes.append(f"{path.name}: source moved since extraction "
                         f"(extracted at {recorded}, working tree {blob}); "
                         "spans checked at the extraction blob")
    else:
        src_lines = src_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if drifted:
            errors.append(
                f"{path.name}: git_blob {recorded} does not match working tree {blob}")

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
            # An arithmetic value that carries its OWN expression and
            # operands (schema 1.1 / instrument v1.2 amendment 1) is
            # self-describing: every operand names its own file, so the
            # harness evaluates it without ever reading the claim anchor
            # (recompute_c4_claims: `source = value if
            # value.get("expression") else (anchor or {})`). Requiring a
            # claim anchor there rejects a shape the harness handles.
            illegal = effective - NULL_ANCHOR_METHODS - {"arithmetic"}
            if illegal:
                errors.append(f"{tag}: null anchor illegal for effective methods "
                              f"{sorted(illegal)}")
            for j, value in enumerate(claim["values"]):
                if (value.get("method") or method) != "arithmetic":
                    continue
                if not (value.get("expression") and value.get("operands")):
                    errors.append(f"{tag}: values[{j}] arithmetic under a null anchor "
                                  "requires its own expression + operands (nothing "
                                  "else can supply them)")
                    continue
                errors.extend(check_arithmetic(tag, j, value))
            continue
        if not (REPO_ROOT / anchor["file"]).exists():
            errors.append(f"{tag}: anchor file missing: {anchor['file']}")
        # Each effective-arithmetic value needs an expression: its own
        # (schema 1.1 per-value form) or the claim anchor's (legal for
        # exactly one derived value per claim).
        for j, value in enumerate(claim["values"]):
            if (value.get("method") or method) != "arithmetic":
                continue
            errors.extend(check_arithmetic(
                tag, j, value if value.get("expression") else anchor))
        # v1.2 amendment 3: in a multi-value claim whose anchor carries
        # a path, a pathless read value would silently inherit that path
        # at recompute time and be compared against the wrong quantity
        # (Obs 379: "5 passes" vs a temperature of 0.7). Require an
        # explicit per-value path in that configuration.
        if len(claim["values"]) > 1 and anchor.get("path"):
            for j, value in enumerate(claim["values"]):
                if (value.get("method") or method) == "read" and not value.get("path"):
                    errors.append(
                        f"{tag}: values[{j}] pathless read in a multi-value claim "
                        "with an anchored path (v1.2 amendment 3 — the recompute "
                        "harness refuses the anchor-path fallback)")
    return errors, notes


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path,
                        help="extraction files (default: all in the c4-extraction directory)")
    parser.add_argument("--at-era", action="store_true",
                        help="check verbatim spans against each file's recorded "
                             "extraction blob rather than the working tree; blob "
                             "drift becomes an informational note")
    args = parser.parse_args(argv)

    paths = args.paths or sorted(DEFAULT_DIR.glob("*.json"))
    if not paths:
        print("no extraction files found", file=sys.stderr)
        return 1
    validator = build_validator()
    failures = 0
    total_claims = 0
    drifted = 0
    for path in paths:
        errs, notes = validate_file(Path(path), validator, at_era=args.at_era)
        for note in notes:
            drifted += 1
            print(f"note {note}")
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
    suffix = f"; {drifted} checked at their extraction blob" if drifted else ""
    print(f"all {len(paths)} files valid; {total_claims} claims{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
