#!/usr/bin/env python3
"""Verify that every bootstrap confidence-interval entry still matches its source file.

Why
---
``results/all-bootstrap-cis.json`` (and its byte-identical duplicate
``results/pv/all-bootstrap-cis.json``) holds 496 bootstrap confidence-interval
(CI) entries keyed by a condition path-string. Each entry records a
``source_file`` path and the ``n_detections`` the bootstrap resampled, but
nothing binds the entry to that file's *content*. The file can be
re-materialised, or grown in place, under the same name; the CI then goes on
serving with no error and no warning.

That is exactly what happened. The March 2026 out-of-band tile-recovery
campaign disclosed as E70
(``docs/methodology/preregistration/protocol-errata.md:3154-3199``) ran
``patch_failed_tiles()``, which appends recovered detections into an existing
pass GeoJSON. Passes patched after their CI was computed now hold more features
than the CI recorded — the CI is a pre-recovery number wearing a post-recovery
file's name. The audit that established this is
``reports/name-keyed-cache-audit-2026-09-12.md`` § 4 Finding 1; the repair is
``reports/bootstrap-cis-repair-2026-09-12.md``.

The decisive diagnostic is cheap and this script performs it: re-count the
GeoJSON's features and compare with the recorded ``n_detections``. It is the
``feedback_feature_count_crosscheck`` signal, applied to the CI store.

Twenty-four entries do not resolve to a file at all and are reported separately
rather than as failures-to-count: their ``source_file`` is a
``consensus:<label>`` pseudo-path, because the N=30 consensus merge they scored
was built in memory and never written to disk. The 2026-09-12 repair marks each
of them ``"source_status": "unresolved"``.

After that repair no entry should ever *mismatch* again: the 85 stale ones were
re-run on their present source files rather than annotated as uncitable
(the Principal Investigator's ruling, 2026-09-12 — the store is to be wholly
current). A mismatch is therefore always a failure, never a known state, and
this check is the tier-1 gate that makes future drift fail loudly.

Modes
-----
``--check``
    Resolve, count, and compare every entry; print a summary and the full
    mismatch list. Exit 1 on any mismatch, and on any unresolved entry unless
    ``--allow-annotated`` is given — which treats the 24 entries the repair
    marked ``"source_status": "unresolved"`` as known. A mismatch is never
    excused by ``--allow-annotated``, and an unresolved entry that carries no
    annotation still fails.

``--remap``
    Apply the documented ``data/`` prefix remaps before resolving. Needed only
    for a pre-repair file: after the 2026-09-12 path repair the committed
    ``source_file`` values already name the files that exist today, so
    ``--check`` alone suffices.

Usage
-----
Reproduce the audit finding against the archived pre-repair file — 472 resolved
/ 24 unresolved / 387 match / 85 mismatch, or 456 / 40 / 371 / 85 with only the
``data/retest/`` remap, which is what the audit report quotes::

    python scripts/check_bootstrap_cis.py --check --remap \\
        archive/superseded-bootstrap-cis-2026-09-12/all-bootstrap-cis.json

The per-commit gate over the repaired store (exit 0, zero mismatches)::

    python scripts/check_bootstrap_cis.py --check --allow-annotated \\
        results/all-bootstrap-cis.json

Machine-readable summary for a downstream check::

    python scripts/check_bootstrap_cis.py --check --allow-annotated --json \\
        results/all-bootstrap-cis.json

No API call, no network, no write: this script only reads.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# The prefix remaps the audit inferred and this repository's history confirms.
#
# ``data/retest/`` -> ``outputs/retest/``: the retest pass tree lives under
# ``outputs/``, never ``data/`` (no ``data/`` directory has ever existed here).
#
# ``data/consensus-proposers/`` ->
# ``archive/outputs-experimental-pilot/pv/consensus-proposers/``: these sixteen
# files were created at ``outputs/pv/consensus-proposers/`` by ``2de117096``
# (the same commit that first wrote the CI store) and moved to their archive
# location by ``276e4ca80`` ("refactor(archive): prune non-production results
# and superseded outputs"). All sixteen still match their recorded
# ``n_detections`` exactly, which corroborates the mapping.
REMAPS: tuple[tuple[str, str], ...] = (
    ("data/retest/", "outputs/retest/"),
    (
        "data/consensus-proposers/",
        "archive/outputs-experimental-pilot/pv/consensus-proposers/",
    ),
)

# ``source_file`` values with this prefix are condition labels, not paths.
PSEUDO_PATH_PREFIX = "consensus:"

# Entry status vocabulary used in the summary and the JSON output.
STATUS_MATCH = "match"
STATUS_MISMATCH = "mismatch"
STATUS_UNRESOLVED = "unresolved"


@dataclass
class EntryResult:
    """One entry's verdict.

    Attributes:
        key: The entry's key in the ``results`` mapping (a condition
            path-string, e.g. ``single:phase3c/track2-text/h9-E-p2/run_5``).
        status: One of ``match``, ``mismatch``, ``unresolved``.
        source_file: The ``source_file`` string as recorded in the JSON.
        resolved_path: The path actually opened, or ``None`` when unresolved.
        recorded: The entry's recorded ``n_detections``.
        counted: Features counted in the resolved GeoJSON, or ``None``.
        patched: The ``.tiles.json`` sidecar's ``patched`` count when a sidecar
            exists and records one, else ``None``.
        annotated: True when the entry carries a repair annotation marking this
            verdict as already known (``source_status``; unresolved only).
        reason: Short human-readable note for unresolved entries.
    """

    key: str
    status: str
    source_file: str
    resolved_path: Path | None
    recorded: int | None
    counted: int | None = None
    patched: int | None = None
    annotated: bool = False
    reason: str = ""

    @property
    def delta(self) -> int | None:
        """Return ``counted - recorded`` when both are known, else ``None``."""
        if self.counted is None or self.recorded is None:
            return None
        return self.counted - self.recorded


def count_geojson_features(path: Path) -> int:
    """Count the features of a GeoJSON FeatureCollection.

    Args:
        path: Path to a GeoJSON file.

    Returns:
        The length of the file's ``features`` array (0 when the key is absent,
        which is how an empty pass is written).

    Raises:
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return len(payload.get("features", []))


def read_patched_count(geojson_path: Path) -> int | None:
    """Return the E70 ``patched`` tile count from a pass's ``.tiles.json`` sidecar.

    The sidecar sits beside the detections GeoJSON with the same stem, e.g.
    ``detections_h9-B-v4_run02.geojson`` -> ``detections_h9-B-v4_run02.tiles.json``.
    ``patch_failed_tiles()`` writes ``patched`` (and ``patch_timestamp``) into it;
    an unpatched pass's sidecar has neither.

    Args:
        geojson_path: Path to the detections GeoJSON.

    Returns:
        The ``patched`` value, or ``None`` when no sidecar exists, the sidecar
        is unreadable, or it records no patch.
    """
    # ``with_suffix`` replaces only the final suffix, so a stem containing dots
    # (e.g. ``...t0.3...``) survives intact.
    sidecar = geojson_path.with_suffix(".tiles.json")
    if not sidecar.exists():
        return None
    try:
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    value = payload.get("patched")
    if isinstance(value, list):
        # ``patch_failed_tiles()`` records the recovered tile *names*; the count
        # this check reports is the length of that list.
        return len(value)
    if isinstance(value, int):
        return value
    return None


def resolve_source(source_file: str, repo_root: Path, remap: bool) -> tuple[Path | None, str]:
    """Resolve an entry's ``source_file`` to an existing path.

    Args:
        source_file: The recorded ``source_file`` string.
        repo_root: Repository root that relative paths resolve against.
        remap: Whether to apply the ``data/retest/`` -> ``outputs/retest/``
            prefix remap before resolving.

    Returns:
        A ``(path, reason)`` pair. ``path`` is the existing file, or ``None``
        when nothing could be resolved; ``reason`` is a short note in that case
        (empty string on success).
    """
    if source_file.startswith(PSEUDO_PATH_PREFIX):
        return None, "condition label, not a file path"

    candidate = source_file
    if remap:
        for prefix, replacement in REMAPS:
            if candidate.startswith(prefix):
                candidate = replacement + candidate[len(prefix):]
                break

    path = Path(candidate)
    if not path.is_absolute():
        path = repo_root / path
    if path.exists():
        return path, ""

    return None, f"no file at {candidate}"


def is_annotated(entry: dict[str, Any], status: str) -> bool:
    """Report whether an entry's verdict is already annotated as known.

    Only ``unresolved`` can be a known state. A mismatch is never annotated
    away: since the 2026-09-12 re-run every resolvable entry matches its source,
    so a mismatch means something changed under the store's feet and must fail.
    (An entry's ``pre_e70`` sub-object records values the re-run superseded — it
    is history, not an exemption.)

    Args:
        entry: The entry mapping from the ``results`` object.
        status: The verdict computed for it.

    Returns:
        True when an ``unresolved`` entry carries ``"source_status":
        "unresolved"``; False otherwise.
    """
    if status == STATUS_UNRESOLVED:
        return entry.get("source_status") == STATUS_UNRESOLVED
    return False


def check_entries(
    payload: dict[str, Any],
    repo_root: Path,
    remap: bool = False,
) -> list[EntryResult]:
    """Verify every entry in a loaded ``all-bootstrap-cis.json`` payload.

    Args:
        payload: The parsed JSON object (expects a ``results`` mapping).
        repo_root: Repository root that relative ``source_file`` paths resolve
            against.
        remap: Apply the documented ``data/retest/`` prefix remap.

    Returns:
        One :class:`EntryResult` per entry, in the payload's key order.
    """
    results: list[EntryResult] = []
    for key, entry in payload.get("results", {}).items():
        source_file = entry.get("source_file", "")
        recorded = entry.get("n_detections")
        path, reason = resolve_source(source_file, repo_root, remap)

        if path is None:
            status = STATUS_UNRESOLVED
            results.append(
                EntryResult(
                    key=key,
                    status=status,
                    source_file=source_file,
                    resolved_path=None,
                    recorded=recorded,
                    annotated=is_annotated(entry, status),
                    reason=reason,
                )
            )
            continue

        counted = count_geojson_features(path)
        status = STATUS_MATCH if counted == recorded else STATUS_MISMATCH
        results.append(
            EntryResult(
                key=key,
                status=status,
                source_file=source_file,
                resolved_path=path,
                recorded=recorded,
                counted=counted,
                patched=read_patched_count(path) if status == STATUS_MISMATCH else None,
                annotated=is_annotated(entry, status),
            )
        )
    return results


def summarise(results: list[EntryResult]) -> dict[str, int]:
    """Aggregate per-entry verdicts into the audit's four headline counts.

    Args:
        results: Per-entry verdicts from :func:`check_entries`.

    Returns:
        A mapping with ``total``, ``resolved``, ``unresolved``, ``match``,
        ``mismatch``, and the ``*_annotated`` / ``*_new`` splits of the two
        failing categories.
    """
    counts = {
        "total": len(results),
        "resolved": sum(1 for r in results if r.status != STATUS_UNRESOLVED),
        "unresolved": sum(1 for r in results if r.status == STATUS_UNRESOLVED),
        "match": sum(1 for r in results if r.status == STATUS_MATCH),
        "mismatch": sum(1 for r in results if r.status == STATUS_MISMATCH),
    }
    for status in (STATUS_UNRESOLVED, STATUS_MISMATCH):
        failing = [r for r in results if r.status == status]
        counts[f"{status}_annotated"] = sum(1 for r in failing if r.annotated)
        counts[f"{status}_new"] = sum(1 for r in failing if not r.annotated)
    return counts


def format_report(
    results: list[EntryResult],
    source: Path,
    allow_annotated: bool,
) -> str:
    """Render the human-readable ``--check`` report.

    Args:
        results: Per-entry verdicts from :func:`check_entries`.
        source: The CI JSON that was checked (named in the header).
        allow_annotated: Whether annotated entries are being treated as known.

    Returns:
        The report as a single string, without a trailing newline.
    """
    counts = summarise(results)
    lines = [
        f"Bootstrap CI source check: {source}",
        f"  entries        : {counts['total']}",
        f"  resolved       : {counts['resolved']}",
        f"  unresolved     : {counts['unresolved']}"
        f" (annotated {counts['unresolved_annotated']}, new {counts['unresolved_new']})",
        f"  match          : {counts['match']}",
        f"  mismatch       : {counts['mismatch']}"
        f" (annotated {counts['mismatch_annotated']}, new {counts['mismatch_new']})",
    ]

    mismatches = [r for r in results if r.status == STATUS_MISMATCH]
    if mismatches:
        lines.append("")
        lines.append(f"Mismatching entries ({len(mismatches)}), largest divergence first:")
        lines.append(
            f"  {'entry':<58} {'recorded':>8} {'counted':>8} {'delta':>6} "
            f"{'patched':>7}  known"
        )
        for r in sorted(mismatches, key=lambda r: -(r.delta or 0)):
            patched = "-" if r.patched is None else str(r.patched)
            known = "yes" if r.annotated else "NEW"
            lines.append(
                f"  {r.key:<58} {r.recorded:>8} {r.counted:>8} "
                f"{r.delta:>+6} {patched:>7}  {known}"
            )

    unresolved = [r for r in results if r.status == STATUS_UNRESOLVED]
    if unresolved:
        lines.append("")
        lines.append(f"Unresolved entries ({len(unresolved)}):")
        for r in unresolved:
            known = "yes" if r.annotated else "NEW"
            lines.append(f"  {r.key:<58} {r.reason}  known={known}")

    failing = counts["mismatch"] + counts["unresolved"]
    if allow_annotated:
        failing = counts["mismatch"] + counts["unresolved_new"]
    lines.append("")
    if failing:
        mode = (
            "mismatching or newly unresolved"
            if allow_annotated
            else "unresolved or mismatching"
        )
        lines.append(f"FAIL: {failing} {mode} entries.")
    else:
        lines.append("OK: every entry accounted for.")
    return "\n".join(lines)


def exit_code(results: list[EntryResult], allow_annotated: bool) -> int:
    """Return the process exit status for a set of verdicts.

    Args:
        results: Per-entry verdicts.
        allow_annotated: Treat repair-annotated entries as known.

    Returns:
        0 when nothing fails, 1 otherwise.
    """
    counts = summarise(results)
    if allow_annotated:
        # Mismatches always count: ``is_annotated`` never marks one known.
        failing = counts["mismatch"] + counts["unresolved_new"]
    else:
        failing = counts["mismatch"] + counts["unresolved"]
    return 1 if failing else 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Re-count every bootstrap CI entry's source GeoJSON against its "
            "recorded n_detections."
        ),
    )
    parser.add_argument(
        "ci_json",
        nargs="?",
        default="results/all-bootstrap-cis.json",
        type=Path,
        help="Path to an all-bootstrap-cis.json (default: results/all-bootstrap-cis.json).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run the source re-count check (the only mode; kept explicit for symmetry "
        "with the repository's other --check gates).",
    )
    parser.add_argument(
        "--remap",
        action="store_true",
        help="Apply the documented data/ -> outputs/ and data/ -> archive/ prefix "
        "remaps before resolving (needed only for a pre-repair file).",
    )
    parser.add_argument(
        "--allow-annotated",
        action="store_true",
        help="Treat the entries the 2026-09-12 repair marked "
        "source_status=unresolved as known. Mismatches always fail.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root that relative source_file paths resolve against "
        "(default: the parent of this script's directory).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the summary counts and per-entry verdicts as JSON instead of text.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Argument vector (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit status.
    """
    args = build_parser().parse_args(argv)
    if not args.check:
        build_parser().error("nothing to do: pass --check")

    repo_root = args.repo_root or Path(__file__).resolve().parent.parent
    payload = json.loads(args.ci_json.read_text(encoding="utf-8"))
    results = check_entries(payload, repo_root=repo_root, remap=args.remap)

    if args.json:
        print(
            json.dumps(
                {
                    "source": str(args.ci_json),
                    "remap": args.remap,
                    "allow_annotated": args.allow_annotated,
                    "counts": summarise(results),
                    "entries": [
                        {
                            "key": r.key,
                            "status": r.status,
                            "source_file": r.source_file,
                            "resolved_path": None
                            if r.resolved_path is None
                            else str(r.resolved_path),
                            "n_detections_recorded": r.recorded,
                            "n_detections_counted": r.counted,
                            "delta": r.delta,
                            "patched": r.patched,
                            "annotated": r.annotated,
                            "reason": r.reason,
                        }
                        for r in results
                        if r.status != STATUS_MATCH
                    ],
                },
                indent=2,
            )
        )
    else:
        print(format_report(results, args.ci_json, args.allow_annotated))

    return exit_code(results, args.allow_annotated)


if __name__ == "__main__":
    sys.exit(main())
