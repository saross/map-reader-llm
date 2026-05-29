#!/usr/bin/env python3
"""Generate the experimental manifests (and, later, per-run post-run reports).

This is the **Phase 1 generator** for the four-entity manifest model resolved in
``planning/manifest-schema-design.md``. It is the *only* writer of the machine-
extracted manifests (``runs`` / ``conditions`` / ``passes`` / ``run-registry``):
humans edit the *source-of-truth* files (``*.meta.json``, ``evaluation/*.json``,
YAML configs) and a small set of human-authored fields; the generator
re-extracts everything else.

Design references
-----------------
* Entity model + field lists: ``planning/manifest-schema-design.md`` (§§ 1A, 2).
* Machine-readable contract: ``docs/manifest-schemas/*.schema.json`` (draft
  2020-12). These are authoritative; this module validates every row it emits
  against them before writing.
* Anti-confabulation rule (``~/.claude/CLAUDE.md``): every extracted value must
  trace to a source file recorded in ``provenance.source_files``; a value that
  cannot be read is ``null``, never guessed. In particular ``model_used`` is
  read from ``per_item_metadata.model_used`` and NEVER inferred from a
  directory name (erratum-backed gotcha: a ``pro-``named condition ran Flash).

Build status
------------
This commit lands the **scaffold**: schema loading with cross-file ``$ref``
resolution, single-row and whole-manifest validation, a provenance builder, and
a ``--self-test`` that proves the harness round-trips. The per-entity extractors
(passes → conditions → runs row → registry) are built in the following steps,
starting with the ``gold-standard-v2`` vertical slice.

Usage
-----
    # prove the validation harness loads all schemas and round-trips a row
    python scripts/generate_post_run_report.py --self-test

    # (later) extract and validate the manifests for one run, writing nothing
    python scripts/generate_post_run_report.py --run gold-standard-v2 --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

#: Repository root (this file lives in ``<repo>/scripts/``).
REPO_ROOT: Path = Path(__file__).resolve().parents[1]

#: Directory holding the six JSON Schema files (the output contract).
SCHEMA_DIR: Path = REPO_ROOT / "docs" / "manifest-schemas"

#: Semantic version of THIS generator script. Written into every row's
#: ``provenance.extractor_version`` (tracks the script, distinct from the
#: manifest *format* ``schema_version``). Bump on any extraction-logic change.
GENERATOR_VERSION: str = "0.1.0"

#: Manifest format version embedded at the top of each emitted manifest. Must
#: match the ``schema_version`` const in the schema files.
SCHEMA_VERSION: str = "1.0"

#: Map of manifest name → schema filename. The per-row item definition is
#: derived from each schema (see :func:`_row_def_name`) rather than hard-coded,
#: so a schema rename cannot silently desynchronise this module.
MANIFEST_SCHEMAS: dict[str, str] = {
    "runs": "runs-manifest.schema.json",
    "conditions": "conditions-manifest.schema.json",
    "passes": "passes-manifest.schema.json",
    "analyses": "analyses-manifest.schema.json",
    "run-registry": "run-registry.schema.json",
}


# --------------------------------------------------------------------------- #
# Schema loading and validation
# --------------------------------------------------------------------------- #


def load_schema_registry(schema_dir: Path = SCHEMA_DIR) -> tuple[Registry, dict[str, dict]]:
    """Load every ``*.schema.json`` into a ``referencing`` registry.

    Each schema is registered under its own ``$id`` so the relative cross-file
    references in the schemas (e.g. ``common-defs.schema.json#/$defs/provenance``)
    resolve against the referring schema's base URI.

    Args:
        schema_dir: Directory containing the schema files.

    Returns:
        A ``(registry, contents_by_id)`` pair, where ``contents_by_id`` maps each
        schema's ``$id`` to its parsed JSON (handy for introspection).

    Raises:
        FileNotFoundError: If ``schema_dir`` contains no schema files.
    """
    schema_files = sorted(schema_dir.glob("*.schema.json"))
    if not schema_files:
        raise FileNotFoundError(f"No *.schema.json files found in {schema_dir}")

    resources: list[tuple[str, Resource]] = []
    contents_by_id: dict[str, dict] = {}
    for path in schema_files:
        contents = json.loads(path.read_text(encoding="utf-8"))
        schema_id = contents["$id"]
        contents_by_id[schema_id] = contents
        resources.append((schema_id, Resource.from_contents(contents, default_specification=DRAFT202012)))

    registry = Registry().with_resources(resources)
    return registry, contents_by_id


def _schema_id(manifest: str) -> str:
    """Return the ``$id`` of the given manifest's schema file."""
    contents = json.loads((SCHEMA_DIR / MANIFEST_SCHEMAS[manifest]).read_text(encoding="utf-8"))
    return contents["$id"]


def _row_def_name(manifest: str) -> str:
    """Derive the ``$defs`` name of a manifest's per-row item schema.

    Reads the manifest schema, finds its single top-level array property (``runs``
    / ``passes`` / ``conditions`` / ``analyses`` / ``registry``), and returns the
    ``$defs`` key its ``items.$ref`` points at (e.g. ``run``, ``pass``, ``entry``).
    Deriving this avoids hard-coding the mapping, so a schema edit cannot silently
    desync the validator.
    """
    contents = json.loads((SCHEMA_DIR / MANIFEST_SCHEMAS[manifest]).read_text(encoding="utf-8"))
    for prop in contents.get("properties", {}).values():
        if isinstance(prop, dict) and prop.get("type") == "array":
            ref = prop.get("items", {}).get("$ref", "")
            if ref.startswith("#/$defs/"):
                return ref.rsplit("/", 1)[-1]
    raise ValueError(f"Could not locate the per-row array definition in {manifest} schema")


def make_row_validator(manifest: str, registry: Registry) -> jsonschema.Draft202012Validator:
    """Build a validator for a single *row* of the given manifest.

    The schema files validate a whole manifest object (``{schema_version, runs:
    [...]}``); to validate one extracted row in isolation we point a validator at
    the per-row ``$defs`` entry via the registry, which keeps the row's relative
    ``common-defs`` references resolvable.

    Args:
        manifest: One of :data:`MANIFEST_SCHEMAS` keys.
        registry: A registry from :func:`load_schema_registry`.

    Returns:
        A draft 2020-12 validator with date-time format checking enabled.
    """
    ref = f"{_schema_id(manifest)}#/$defs/{_row_def_name(manifest)}"
    return jsonschema.Draft202012Validator(
        {"$ref": ref},
        registry=registry,
        format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER,
    )


def validate_row(manifest: str, row: dict, registry: Registry) -> list[str]:
    """Validate one extracted row; return a list of human-readable error strings.

    An empty list means the row conforms. Errors are sorted by JSON path so the
    output is stable across runs.

    Args:
        manifest: Which manifest the row belongs to.
        row: The extracted row object.
        registry: A registry from :func:`load_schema_registry`.

    Returns:
        Sorted error messages (``"<path>: <message>"``); empty if valid.
    """
    validator = make_row_validator(manifest, registry)
    errors = sorted(validator.iter_errors(row), key=lambda e: list(e.path))
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors]


# --------------------------------------------------------------------------- #
# Provenance
# --------------------------------------------------------------------------- #


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string (seconds precision)."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_provenance(source_files: list[str], extracted_at: str | None = None) -> dict[str, Any]:
    """Build a ``provenance`` object for an extracted row.

    Args:
        source_files: Repository-relative paths every value in the row was read
            from. Must be non-empty (the schema requires ``minItems: 1``); a row
            with no traceable source should not be emitted.
        extracted_at: ISO 8601 timestamp; defaults to now (UTC). Passed in
            explicitly by batch runs so all rows share one extraction timestamp.

    Returns:
        A ``{source_files, last_extracted_at, extractor_version}`` dict matching
        ``common-defs.schema.json#/$defs/provenance``.
    """
    if not source_files:
        raise ValueError("provenance.source_files must list at least one source file")
    return {
        "source_files": source_files,
        "last_extracted_at": extracted_at or utc_now_iso(),
        "extractor_version": GENERATOR_VERSION,
    }


# --------------------------------------------------------------------------- #
# Self-test (proves the harness round-trips before any extractor is wired in)
# --------------------------------------------------------------------------- #


def _self_test() -> int:
    """Validate that all schemas load and a minimal hand-written row round-trips.

    Returns a process exit code (0 = pass).
    """
    registry, contents_by_id = load_schema_registry()
    print(f"Loaded {len(contents_by_id)} schema files from {SCHEMA_DIR.relative_to(REPO_ROOT)}")
    for manifest in MANIFEST_SCHEMAS:
        print(f"  {manifest:13s} → row def '$defs/{_row_def_name(manifest)}'")

    # A minimal valid run-registry entry exercises the row validator + the
    # slug pattern; a deliberately invalid one proves errors are caught.
    good_entry = {"run_id": "gold-standard-v2", "directory_path": "outputs/gs/gold-standard-v2"}
    bad_entry = {"run_id": "Gold/Standard", "directory_path": "outputs/gs/gold-standard-v2"}

    good_errors = validate_row("run-registry", good_entry, registry)
    bad_errors = validate_row("run-registry", bad_entry, registry)

    print("\nSelf-test:")
    print(f"  valid registry entry  → {len(good_errors)} errors (expect 0)")
    print(f"  invalid run_id slug    → {len(bad_errors)} errors (expect ≥1): {bad_errors or 'NONE'}")

    # A provenance object must validate against the common-defs sub-schema by
    # validating a full run row that embeds it would be heavier; here we confirm
    # the builder produces the required keys.
    prov = build_provenance(["docs/manifest-schemas/run-registry.schema.json"])
    prov_ok = set(prov) == {"source_files", "last_extracted_at", "extractor_version"}
    print(f"  provenance builder keys → {'ok' if prov_ok else 'WRONG: ' + str(set(prov))}")

    passed = not good_errors and bool(bad_errors) and prov_ok
    print(f"\n{'PASS' if passed else 'FAIL'} — validation harness {'round-trips' if passed else 'is broken'}")
    return 0 if passed else 1


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def build_arg_parser() -> argparse.ArgumentParser:
    """Construct the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate experimental manifests from source-of-truth files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Validate that all schemas load and the validation harness round-trips, then exit.",
    )
    parser.add_argument(
        "--run",
        metavar="RUN_ID",
        help="(not yet implemented) Extract + validate the manifests for one run.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="(not yet implemented) Extract and validate but write nothing.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    args = build_arg_parser().parse_args(argv)

    if args.self_test:
        return _self_test()

    if args.run:
        print(
            f"Extraction for run '{args.run}' is not yet implemented — the passes/"
            "conditions/runs extractors land in the next steps (gold-standard-v2 "
            "vertical slice). Run with --self-test to exercise the harness.",
            file=sys.stderr,
        )
        return 2

    build_arg_parser().print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
