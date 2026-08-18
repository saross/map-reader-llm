#!/usr/bin/env python3
"""
Canonical resolution of per-pass detection GeoJSON files.

Two filename conventions coexist under ``outputs/``, and the split is
structural rather than accidental. ``scripts/4_detect_mounds_batch.py``
contains two independently-built execution engines behind
``--mode {realtime,batch}``, each computing its output filename inline with no
shared helper:

======================  ==========================================  ===========
Convention              Shape                                       Engine
======================  ==========================================  ===========
**A** (batch)           ``detections_<config>_run<NN>.geojson``      Batch API
**B** (realtime)        ``detections-<config>-<model>-<date>.geojson``  real-time
======================  ==========================================  ===========

Convention A is emitted by ``lib_batch_api.py`` and the batch branch of
``4_detect_mounds_batch.py``; convention B by its realtime branch, which is the
CLI default. The project ran on the Batch API, then switched to real-time flex
when flex gained the same 50 % discount — so a proposer pool whose passes
straddle that switch contains both shapes.

**The failure this module exists to prevent.** A glob of ``detections_*``
matches only convention A. Applied to a mixed pool it returns fewer passes with
no error and no warning — the caller simply scores less data than it thinks.
Across the committed corpus three pools of 162 are mixed, and against them an
A-only glob resolves 3-of-5, 1-of-3 and 1-of-3 passes:

* ``outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text``
* ``outputs/h11/pv-diag-384/pro-medium-image-baseline/image-t0.0``
* ``outputs/h11/pv-diag-384/pro-medium-text-baseline/text-t0.0``

This is not hypothetical: Session 136's exposure survey scored
``pv-diag-384::baseline-pro-text-medium-t-0-0`` on one pass of three (F1 0.7764
against the committed three-run mean 0.7921), and that condition is a Tier-1
member of two leaderboards.

**Why a shared module rather than a wider glob.** Matching both conventions
fixes today's instance; it does not stop tomorrow's. The codebase had already
solved this five or six times independently and inconsistently — a
``PASS_GLOBS`` tuple, four near-duplicate tolerant-glob loaders, a
``detections[-_]*`` character class — while the one loader living in a
``lib_*.py`` remained convention-A-only. So this module supplies both the union
and, more importantly, :func:`resolve_pool_passes`'s **pass-count assertion**:
a resolver that returns the wrong number loudly is worth more than one that
returns the right number quietly.

Usage::

    from scripts.lib_detection_paths import (
        find_pass_geojsons, resolve_pool_passes, PassCountMismatch,
    )

    # Every pass file in one run directory
    files = find_pass_geojsons(run_dir)

    # Every pass in a pool, guarded against a silent undercount
    passes = resolve_pool_passes(pool_dir, expected_passes=condition["n_passes"])

Created: 2026-08-18 (Session 136, defect D6)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import re
from pathlib import Path

__all__ = [
    "PASS_GLOBS",
    "POOL_PASS_GLOBS",
    "AmbiguousPassError",
    "PassCountMismatch",
    "find_pass_geojsons",
    "resolve_pool_passes",
    "run_sort_key",
]

#: Glob patterns for per-pass detection GeoJSONs, one per naming convention.
#: Both must be expanded and unioned; expanding only the first is precisely the
#: defect this module exists to prevent. Moved here from
#: ``n1_baseline_leaderboard_tiering.py``, which held the de-facto canonical
#: copy, and re-exported there for its existing importers.
PASS_GLOBS: tuple[str, ...] = (
    "detections_*.geojson",   # convention A — Batch API
    "detections-*.geojson",   # convention B — real-time
)

#: The same patterns expressed relative to a POOL directory (one level above
#: the ``run_<N>`` directories). Some callers glob at pool level rather than
#: walking run directories; they need the ``*/`` prefix. Derived from
#: :data:`PASS_GLOBS` so the two forms cannot drift apart.
POOL_PASS_GLOBS: tuple[str, ...] = tuple(f"*/{g}" for g in PASS_GLOBS)

#: Sidecar suffixes that sit beside a pass file and are not themselves passes.
#: The ``.geojson`` extension in :data:`PASS_GLOBS` already excludes these; the
#: explicit check is a second line of defence for callers that widen the glob.
_SIDECAR_SUFFIXES: tuple[str, ...] = (".meta.json", ".tiles.json")

#: Aggregation artefacts — consensus, weighted-box-fusion, greedy and verified
#: outputs. They live alongside passes in some trees but come from a different
#: code path and, as ``lib_advanced_metrics.read_processed_tiles`` documents,
#: do not carry a ``processed_tiles`` record. They are never passes.
_AGGREGATION_PREFIXES: tuple[str, ...] = (
    "consensus", "accepted", "verified", "merged", "wbf", "greedy",
)

#: A pass directory is ``run_<N>`` with a purely numeric suffix. Additive
#: fragments such as ``run_1_recovery`` are deliberately excluded, matching
#: ``generate_post_run_report.extract_passes``: they supplement a pass rather
#: than constituting one, and counting them would inflate the pass count.
_RUN_DIR_RE = re.compile(r"^run_(\d+)$")


class PassCountMismatch(RuntimeError):
    """Raised when a pool resolves to a different pass count than expected.

    Carries the directory and both counts so the message is actionable
    without re-running the resolution by hand.
    """


class AmbiguousPassError(RuntimeError):
    """Raised when one run directory holds more than one candidate pass file.

    Exactly one directory in the committed corpus does — a complete re-run
    superseding an incomplete earlier attempt (see :func:`find_pass_geojsons`).
    Picking one silently would be the same class of error this module exists to
    prevent, so the caller must choose explicitly.
    """


def run_sort_key(path: Path) -> tuple[int, str]:
    """Sort key ordering ``run_2`` before ``run_10``.

    Args:
        path: A ``run_<N>`` directory, or any path whose name should sort last.

    Returns:
        ``(run_number, name)`` for a numeric run directory; a large sentinel
        paired with the name otherwise, so unparsable names sort last
        deterministically rather than raising.
    """
    match = _RUN_DIR_RE.match(path.name)
    return (int(match.group(1)) if match else 1 << 30, path.name)


def _is_pass_file(path: Path) -> bool:
    """Return whether a path is a per-pass detection GeoJSON.

    Args:
        path: Candidate file.

    Returns:
        True unless the path is a sidecar or an aggregation artefact.
    """
    name = path.name
    if any(name.endswith(suffix) for suffix in _SIDECAR_SUFFIXES):
        return False
    stem = name.split("-", 1)[0].split("_", 1)[0].lower()
    return stem not in _AGGREGATION_PREFIXES


def find_pass_geojsons(run_dir: Path) -> list[Path]:
    """Return every per-pass detection GeoJSON in one run directory.

    Expands both naming conventions and unions the results, so a directory is
    resolved correctly regardless of which execution engine wrote it.

    Ordinarily this returns zero or one file: of 1,074 run directories in the
    committed corpus, 1,069 hold exactly one and four hold none. Exactly one —
    ``outputs/flash35-pv-2x2/proposer/run_3`` — holds two, a complete 487-tile
    re-run dated 2026-06-11 superseding an incomplete 486-tile attempt dated
    2026-06-10. Callers wanting a single file per run should use
    :func:`resolve_pool_passes`, which refuses to choose for them.

    Args:
        run_dir: A ``run_<N>`` directory.

    Returns:
        Matching paths, deduplicated and sorted by filename. Empty when the
        directory holds no pass file or does not exist — an absent directory is
        not an error here, because callers routinely probe optional pools.
    """
    if not run_dir.is_dir():
        return []
    found: set[Path] = set()
    for pattern in PASS_GLOBS:
        found.update(p for p in run_dir.glob(pattern) if _is_pass_file(p))
    return sorted(found, key=lambda p: p.name)


def resolve_pool_passes(
    pool_dir: Path,
    expected_passes: int | None = None,
    allow_multiple: bool = False,
) -> list[Path]:
    """Resolve every pass file in a proposer pool, guarded against undercounts.

    Walks the pool's numeric ``run_<N>`` subdirectories in run order and
    resolves each with :func:`find_pass_geojsons`.

    The ``expected_passes`` guard is the substantive part. A resolver that
    merely matches both conventions repairs the known instance; the assertion
    is what surfaces the next one, including causes this module cannot
    anticipate — a pass that failed to write, a directory renamed by hand, a
    third naming convention. ``n_passes`` in ``results/run-conditions.json`` is
    populated for all 333 committed conditions and is the natural source.

    Args:
        pool_dir: Directory containing ``run_<N>`` subdirectories.
        expected_passes: Pass count the caller believes it should find. When
            given and not matched, :class:`PassCountMismatch` is raised. When
            ``None``, no assertion is made.
        allow_multiple: Permit a run directory to contribute more than one
            file. Defaults to False, which raises :class:`AmbiguousPassError`
            rather than picking silently.

    Returns:
        Pass file paths in run order.

    Raises:
        PassCountMismatch: If ``expected_passes`` is given and not matched.
        AmbiguousPassError: If a run directory holds several candidate files
            and ``allow_multiple`` is False.
    """
    run_dirs = sorted(
        (d for d in pool_dir.glob("run_*") if d.is_dir() and _RUN_DIR_RE.match(d.name)),
        key=run_sort_key,
    )

    passes: list[Path] = []
    for run_dir in run_dirs:
        found = find_pass_geojsons(run_dir)
        if len(found) > 1 and not allow_multiple:
            raise AmbiguousPassError(
                f"{run_dir} holds {len(found)} candidate pass files "
                f"({', '.join(p.name for p in found)}). Choose explicitly: pass "
                f"allow_multiple=True to take all, or select the intended file "
                f"and pass it directly. Refusing to guess."
            )
        passes.extend(found)

    if expected_passes is not None and len(passes) != expected_passes:
        raise PassCountMismatch(
            f"{pool_dir} resolved {len(passes)} pass file(s) across "
            f"{len(run_dirs)} run directory(ies), expected {expected_passes}. "
            f"Both naming conventions were expanded ({', '.join(PASS_GLOBS)}), "
            f"so this is not the convention-A-only undercount (defect D6); "
            f"check for a missing pass, a non-numeric run directory, or a "
            f"stale expected count."
        )

    return passes
