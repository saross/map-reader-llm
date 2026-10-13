#!/usr/bin/env python3
"""
Resolve a verifier leg to its ``_repaired`` sibling, and record which one was read.

Why this exists
---------------
A Batch API verifier leg books its probabilities in
``<leg>/probabilities.json``. Two later steps write a corrected copy BESIDE the
leg rather than over it, so the committed leg stays as it was run:

* ``scripts/modality_bridge_stage2_checks.py repair`` re-parses every row the
  batch parser booked as an unparseable 0.0 with the real-time path's repair
  chain, and writes ``<leg>_repaired/`` (``parse_repair.json`` records what it
  changed and what it could not recover);
* ``scripts/reverify_unparseable_rows.py book`` (PI decision D55 Q4) re-sends
  the rows no repair could parse and books the answers into the same
  ``<leg>_repaired/`` (``reverify-<date>.json`` records each row and its cost).

Run B's Stage 2 scored from those copies, and Run C's verifier-SD script reads
them by name (``modality_bridge_verifier_sd.load_replicates``). The 55-map
image scorers read their legs by fixed name, ``verify_k{k}_{arm}``, so the
corrections D55 Q4 paid for never reached them. PI decision D58 Q8 extends the
adoption to every 55-map reader of those legs (the r2 campaign sweeps and
cells, the 3.7 K = 5 replicate, the inheritance ladder, the W2.7 subset
floors, and the tile-presence cost legs). This module is the one rule they
share, so it is stated once:

    a leg's probabilities are read from ``<leg>_repaired/`` when that
    directory holds ``probabilities.json``, and from ``<leg>/`` otherwise.

A ``_repaired`` directory without ``probabilities.json`` is NOT used: it is a
half-written copy, and falling back to the leg is the conservative reading.

Before and after
----------------
A re-score must show what the adoption moved under ONE scorer, so the rule can
be switched off without touching code: set ``MAP_READER_VERIFY_DIRS=fixed`` in
the environment and every caller reads the fixed-name leg, as before the
change. The default, ``repaired``, applies the rule. Any other value is an
error rather than a silent default. Every caller records the directory it
read with :func:`verify_dir_provenance`, including the policy in force, so an
output always says which reading produced it.

Usage::

    from scripts.lib_verify_dirs import resolve_verify_dir, verify_dir_provenance

    vdir = resolve_verify_dir(vroot, "verify_k5_arm2")
    probs = json.loads((vdir / "probabilities.json").read_text())
    record["verifier_probabilities"] = verify_dir_provenance(vdir, PROJECT_ROOT)

Created: 2026-10-09
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

#: The suffix a corrected copy of a leg carries (Stage 2's convention).
REPAIRED_SUFFIX = "_repaired"

#: The environment variable that selects the rule, and its two values.
POLICY_ENV = "MAP_READER_VERIFY_DIRS"
POLICY_REPAIRED = "repaired"
POLICY_FIXED = "fixed"
POLICIES = (POLICY_REPAIRED, POLICY_FIXED)

#: The file whose presence makes a ``_repaired`` directory usable.
PROBABILITIES = "probabilities.json"


def verify_dir_policy(policy: str | None = None) -> str:
    """The rule in force: an explicit ``policy``, else the environment, else ``repaired``.

    Args:
        policy: ``"repaired"`` or ``"fixed"``; ``None`` reads
            :data:`POLICY_ENV`.

    Returns:
        The policy name.

    Raises:
        ValueError: When the value is neither policy, so a mistyped
            environment variable cannot silently select a default.

    Examples:
        >>> verify_dir_policy("fixed")
        'fixed'
    """
    value = policy if policy is not None else os.environ.get(POLICY_ENV, POLICY_REPAIRED)
    value = value.strip()
    if value not in POLICIES:
        raise ValueError(f"{POLICY_ENV}={value!r}: expected one of {', '.join(POLICIES)}")
    return value


def repaired_sibling(leg: Path) -> Path:
    """The ``_repaired`` sibling of a leg directory (whether or not it exists).

    Examples:
        >>> repaired_sibling(Path("v/verify_k5_arm2")).name
        'verify_k5_arm2_repaired'
    """
    return leg.with_name(leg.name + REPAIRED_SUFFIX)


def resolve_verify_dir(vroot: Path, name: str, policy: str | None = None) -> Path:
    """The directory a leg's probabilities are read from.

    Args:
        vroot: The directory holding the leg (``verifier/<cell>/``).
        name: The leg's fixed name, e.g. ``verify_k5_arm2``.
        policy: ``"repaired"`` or ``"fixed"``; ``None`` reads the environment
            (:func:`verify_dir_policy`).

    Returns:
        ``vroot / f"{name}_repaired"`` when the policy is ``repaired`` and
        that directory holds ``probabilities.json``; ``vroot / name``
        otherwise. A name that already ends in ``_repaired`` is returned as
        given.
    """
    leg = vroot / name
    if verify_dir_policy(policy) == POLICY_FIXED or name.endswith(REPAIRED_SUFFIX):
        return leg
    repaired = repaired_sibling(leg)
    return repaired if (repaired / PROBABILITIES).is_file() else leg


def resolve_leg(leg: Path, policy: str | None = None) -> Path:
    """:func:`resolve_verify_dir` for a leg given as one path."""
    return resolve_verify_dir(leg.parent, leg.name, policy)


def sha256_file(path: Path) -> str:
    """Hex SHA-256 of a file's bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _display(path: Path, root: Path | None) -> str:
    """Repository-relative when ``path`` is under ``root``, absolute otherwise."""
    if root is not None and path.resolve().is_relative_to(root.resolve()):
        return str(path.resolve().relative_to(root.resolve()))
    return str(path)


def verify_dir_provenance(vdir: Path, root: Path | None = None,
                          policy: str | None = None) -> dict[str, Any]:
    """Which directory was read, its probabilities' SHA-256, and what repaired it.

    The field names follow ``modality_bridge_verifier_sd.load_replicates``
    (``dir``, ``probabilities_sha256``, ``parse_error_rows``, ``repaired``,
    ``unrecovered``), so a reader of Run C's gates reads these alike. Two
    fields are added for the D55 Q4 re-verification, which ``parse_repair.json``
    predates: ``reverified`` (rows booked by every ``reverify-*.json`` in the
    directory) and ``reverify_usd`` (their audited cost).

    Args:
        vdir: The directory read (from :func:`resolve_verify_dir`).
        root: The repository root, for a relative ``dir``; ``None`` keeps
            the path as given.
        policy: The policy that chose ``vdir``; ``None`` reads the
            environment.

    Returns:
        ``{"dir", "policy", "probabilities_sha256", "n_results",
        "parse_error_rows", "repaired", "unrecovered", "reverified",
        "reverify_usd", "reverify_records"}``. The repair and re-verification
        counts are ``None`` when the directory has no such record (a leg read
        as run).
    """
    probs_path = vdir / PROBABILITIES
    results = json.loads(probs_path.read_text())["results"]
    rec = vdir / "parse_repair.json"
    repair = json.loads(rec.read_text()) if rec.is_file() else None
    reverify_files = sorted(vdir.glob("reverify-*.json"))
    rows = [row for f in reverify_files for row in json.loads(f.read_text()).get("rows", [])]
    return {
        "dir": _display(vdir, root),
        "policy": verify_dir_policy(policy),
        "probabilities_sha256": sha256_file(probs_path),
        "n_results": len(results),
        "parse_error_rows": None if repair is None else repair["n_parse_error_rows"],
        "repaired": None if repair is None else len(repair["changed"]),
        "unrecovered": None if repair is None else len(repair["unrecovered"]),
        "reverified": len(rows) if reverify_files else None,
        "reverify_usd": (round(sum(float(r.get("cost_usd") or 0.0) for r in rows), 6)
                         if reverify_files else None),
        "reverify_records": [_display(f, root) for f in reverify_files],
    }
