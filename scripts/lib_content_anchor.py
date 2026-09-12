#!/usr/bin/env python3
"""
Content anchors for derived artefacts: blob hashes, config hashes, ``.done`` markers.

The defect class this module exists to close is documented in
``reports/name-keyed-cache-audit-2026-09-12.md``: a cache, registry, index, or
completion marker keyed by a **name** (a label, a path, a stage name, or merely
"a file is present") rather than by the **content** it was built from. Nothing
errors when the content changes under the same name — the derived value simply
goes on serving. The cure is always the same shape: record a hash of what the
artefact was built from, and compare it before reusing the artefact.

Three helpers, all dependency-free and usable from any script:

* :func:`git_blob_hash` — the content anchor for a FILE. Returns exactly the
  value ``git hash-object <path>`` prints, computed in pure Python so it works
  for paths outside the repository (temporary materialisations, test fixtures)
  and needs no subprocess. ``scripts/materialise_opmax_cells.py:125-141``
  records the same anchor by shelling out to git for repository-relative paths;
  this is that helper generalised.
* :func:`config_hash` — the content anchor for a CONFIGURATION (any
  JSON-serialisable object). Canonical JSON, sorted keys, SHA-256.
* :func:`write_done_marker` / :func:`read_done_marker` /
  :func:`done_marker_matches` — a ``.done`` marker that records the config hash
  of the work it marks complete, plus the checker that reads it.

Why the ``.done`` marker helpers exist (audit § 5 fix 7, candidate row 26):
the project's shell drivers (``scripts/gemini37-overnight.sh`` and its
siblings) mark a completed pass by ``touch``-ing an empty ``.done`` file. An
empty marker records only THAT something ran, never WHAT ran, so a driver
re-invoked after its config was edited skips the pass it should redo. Existing
drivers are deliberately **not** retrofitted — their campaigns are complete,
and rewriting their markers would rewrite history. New drivers should use the
command-line interface (CLI) below instead of ``touch``.

Usage from Python::

    from lib_content_anchor import config_hash, done_marker_matches, write_done_marker

    cfg_hash = config_hash(resolved_config)          # any JSON-able object
    ok, reason = done_marker_matches(marker, cfg_hash)
    if not ok:
        run_the_work()
        write_done_marker(marker, cfg_hash, extra={"pass": "run_07"})

Usage from a shell driver (the documented replacement for ``touch <marker>``)::

    ANCHOR="python scripts/lib_content_anchor.py"

    # Before the work: skip only when the marker was written from THIS config.
    if $ANCHOR check-done outputs/run_07/.done --config prompts/configs/x.json; then
        echo "run_07 already done under this config — skipping"
    else
        ...do the work...
        $ANCHOR write-done outputs/run_07/.done --config prompts/configs/x.json
    fi

    # Or hash several inputs at once (order-independent):
    $ANCHOR write-done outputs/run_07/.done \\
        --config prompts/configs/x.json --config prompts/system-instructions/y.md

``check-done`` exits 0 only on a verified match. It exits 1 for every other
state — marker missing, marker written from a different config, or a legacy
marker with no recorded hash — because "unknown provenance" must never be
read as "match" (that conflation is the defect class itself).

Created: 2026-09-12 (Session 153, audit § 5 fix 7)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

#: Schema tag written into every marker this module writes, so a reader can
#: tell a content-anchored marker from a legacy ``touch``-ed one.
DONE_MARKER_SCHEMA = "content-anchored-done-marker/1"

#: Reasons :func:`done_marker_matches` can return. ``match`` is the only
#: state that licenses a skip.
MATCH = "match"
MISSING = "missing"
MISMATCH = "mismatch"
UNKNOWN_PROVENANCE = "unknown-provenance"


# ---------------------------------------------------------------------------
# Content anchors
# ---------------------------------------------------------------------------


def git_blob_hash(path: str | Path) -> str | None:
    """Git blob hash of a file's current bytes, or ``None`` if absent.

    Computes ``SHA-1("blob " + size + "\\0" + bytes)`` — the identity git
    gives a blob — in pure Python, so the anchor is available for files
    outside any repository and without a subprocess. The value is
    byte-identical to ``git hash-object <path>``.

    Args:
        path: File to hash. A directory or a missing path yields ``None``.

    Returns:
        The 40-character hex blob hash, or ``None`` when *path* is not a
        readable file.

    Example:
        >>> git_blob_hash("/nonexistent") is None
        True
    """
    p = Path(path)
    if not p.is_file():
        return None
    try:
        data = p.read_bytes()
    except OSError:
        return None
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324 - git's own identity


def config_hash(config: Any) -> str:
    """SHA-256 of a configuration's canonical JSON form.

    Keys are sorted and non-JSON-serialisable values (``Path``, for
    instance) are stringified, so the hash is stable across dict ordering
    and across the ``Path``/``str`` distinction that command-line
    overrides introduce.

    Args:
        config: Any JSON-serialisable object (typically a dict).

    Returns:
        A 64-character hex digest.

    Example:
        >>> config_hash({"a": 1, "b": 2}) == config_hash({"b": 2, "a": 1})
        True
    """
    canonical = json.dumps(
        config, sort_keys=True, separators=(",", ":"), default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def config_hash_of_files(paths: list[str | Path]) -> str:
    """SHA-256 over the blob hashes of several files (order-independent).

    Use for a shell driver whose "configuration" is a set of files (a
    prompt config plus its system-instruction markdown, say). A missing
    file contributes the literal ``"missing"`` so its absence changes the
    hash rather than being silently ignored.

    Args:
        paths: The files whose contents define the configuration.

    Returns:
        A 64-character hex digest.
    """
    entries = sorted(
        (str(Path(p)), git_blob_hash(p) or "missing") for p in paths
    )
    return config_hash(entries)


# ---------------------------------------------------------------------------
# ``.done`` markers that record what was run
# ---------------------------------------------------------------------------


def write_done_marker(
    marker_path: str | Path,
    cfg_hash: str,
    *,
    extra: dict[str, Any] | None = None,
) -> Path:
    """Write a ``.done`` marker recording the config hash of the finished work.

    Args:
        marker_path: Marker file to write (parents are created).
        cfg_hash: The hash from :func:`config_hash` or
            :func:`config_hash_of_files`.
        extra: Optional extra provenance fields (pass label, command line,
            input counts). Recorded verbatim beside the hash.

    Returns:
        The path written.
    """
    path = Path(marker_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "schema": DONE_MARKER_SCHEMA,
        "config_hash": cfg_hash,
        "written_at": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        payload.update(extra)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def read_done_marker(marker_path: str | Path) -> dict[str, Any] | None:
    """Return a marker's recorded payload, or ``None``.

    ``None`` means "no usable provenance": the marker is absent, empty (a
    legacy ``touch``-ed file), or not JSON. Callers must treat all three
    as unknown provenance, never as a match.

    Args:
        marker_path: Marker file to read.

    Returns:
        The parsed payload dict, or ``None``.
    """
    path = Path(marker_path)
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def done_marker_matches(
    marker_path: str | Path,
    cfg_hash: str,
) -> tuple[bool, str]:
    """Report whether a ``.done`` marker was written from *cfg_hash*.

    Args:
        marker_path: Marker file to check.
        cfg_hash: The current configuration's hash.

    Returns:
        ``(is_match, reason)`` where *reason* is one of :data:`MATCH`,
        :data:`MISSING`, :data:`MISMATCH`, or
        :data:`UNKNOWN_PROVENANCE` (a legacy marker with no recorded
        hash — never reported as a match).
    """
    path = Path(marker_path)
    if not path.exists():
        return False, MISSING
    payload = read_done_marker(path)
    recorded = (payload or {}).get("config_hash")
    if not recorded:
        return False, UNKNOWN_PROVENANCE
    if recorded == cfg_hash:
        return True, MATCH
    return False, MISMATCH


# ---------------------------------------------------------------------------
# CLI for shell drivers
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    """Construct the CLI parser (see the module docstring for driver usage)."""
    parser = argparse.ArgumentParser(
        description=(
            "Content anchors for shell drivers: hash a config, write a "
            ".done marker that records it, or check one before skipping work."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    hash_p = sub.add_parser(
        "hash-config", help="Print the config hash of one or more files.",
    )
    hash_p.add_argument(
        "--config", action="append", required=True, type=Path,
        help="A file whose content defines the configuration (repeatable).",
    )

    write_p = sub.add_parser(
        "write-done", help="Write a .done marker recording the config hash.",
    )
    write_p.add_argument("marker", type=Path, help="Marker path to write.")
    write_p.add_argument(
        "--config", action="append", required=True, type=Path,
        help="A file whose content defines the configuration (repeatable).",
    )
    write_p.add_argument(
        "--note", default=None, help="Optional free-text note recorded in the marker.",
    )

    check_p = sub.add_parser(
        "check-done",
        help="Exit 0 only when the marker was written from this config.",
    )
    check_p.add_argument("marker", type=Path, help="Marker path to check.")
    check_p.add_argument(
        "--config", action="append", required=True, type=Path,
        help="A file whose content defines the configuration (repeatable).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code.

    ``check-done`` returns 0 only on a verified match; every other state
    (missing marker, different config, legacy marker without a hash)
    returns 1 so a shell ``if`` re-runs the work.
    """
    args = _build_parser().parse_args(argv)
    cfg_hash = config_hash_of_files(args.config)

    if args.command == "hash-config":
        print(cfg_hash)
        return 0

    if args.command == "write-done":
        extra = {"config_files": [str(p) for p in args.config]}
        if args.note:
            extra["note"] = args.note
        path = write_done_marker(args.marker, cfg_hash, extra=extra)
        print(f"wrote {path} (config_hash {cfg_hash[:12]})")
        return 0

    matched, reason = done_marker_matches(args.marker, cfg_hash)
    print(f"{args.marker}: {reason} (config_hash {cfg_hash[:12]})")
    return 0 if matched else 1


if __name__ == "__main__":
    sys.exit(main())
