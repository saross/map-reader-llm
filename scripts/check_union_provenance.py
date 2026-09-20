#!/usr/bin/env python3
"""
Check a committed consensus union against the pool it was built from.
=====================================================================

Finding 4 of ``reports/name-keyed-cache-audit-2026-09-12.md``: a consensus
union built before 2026-09-12 records only ``total_passes`` in its
``voting_summary.json``. It carries no pass list, so a **declared sub-pool**
union (``consensus-n5`` under a 30-pass pool) and a **stale** union (built
when the pool held fewer passes, or before a pass was rewritten in place by
the E57 / E70 recovery campaigns) are indistinguishable from the artefact
alone. Pull request #14 fixed that for FUTURE unions by having
``merge_passes.py`` write a ``pass_provenance`` block; this script settles the
question for unions that already exist, by re-deriving each one from its pool
and comparing the result with the committed file.

The re-derivation reuses ``scripts/merge_passes.py``'s own functions — the
same clustering implementation that produced the committed unions — so a
difference is a difference in inputs, not in algorithm. Nothing is ever
written over a committed artefact: re-derived unions go to a scratch
directory (``--scratch-dir``, default a temporary directory that is removed
on exit).

Classification
--------------
``REPRODUCES``
    The re-derivation from the union's whole pool yields the same feature
    count and the same coordinates (bidirectional nearest neighbour within
    ``--tolerance-m``).
``SUBPOOL-CONSISTENT``
    The union declares a first-N sub-pool (a ``consensus-nN`` directory, the
    ``--passes 1,..,N`` rule of ``scripts/build_phase3_subpool_consensus.py``)
    and reproduces from those N passes, while the pool holds more.
``STALE``
    Neither reproduces. The pool now holds passes, or pass content, the union
    does not reflect. The report names which.
``UNRESOLVED``
    The parameters are not recoverable — most often the pool's passes were
    never materialised as ``run_*`` / ``pass_*`` directories.

A second mode: a crop manifest against its union
------------------------------------------------
``--manifest`` answers the adjacent question — not "was this union built from
the pool it claims?" but "does the crop manifest the verifier is about to be
handed still agree with the union it was cut from?". It compares both the
count of detections and every candidate's ``vote_count``, and classifies
``AGREES`` / ``DISAGREES`` / ``NOT-APPLICABLE`` (neither side carries votes —
a single-pass proposer output) / ``UNRESOLVED`` (the union is not on this
machine). Only ``DISAGREES`` exits non-zero, and ``scripts/run_pv.py verify``
runs this check before either the batch or the real-time path and refuses a
``DISAGREES`` manifest unless ``--allow-stale-manifest`` is passed.

The mode exists because the drift is real and was silent:
``results/im-june-pool-grid-2026-09-20/findings.md`` § 7 found five manifests
from the April/May 2026 recovery campaign carrying a ``vote_count`` one low on
15 to 110 candidates each, and one manifest a whole candidate short of its
union, none of which any artefact flagged.

Usage
-----
    # One union
    python scripts/check_union_provenance.py \\
        --union outputs/retest/phase3a/track2-text/T1.0/consensus/consensus_t22.geojson

    # Every union a registered condition reads (the retrospective)
    python scripts/check_union_provenance.py --all \\
        --json-out results/union-staleness-2026-09-12.json

    # Re-use a scratch tree across invocations (skips finished unions)
    python scripts/check_union_provenance.py --all \\
        --scratch-dir /tmp/union-check --workers 8

    # A crop manifest against the union it declares (exit 1 on disagreement)
    python scripts/check_union_provenance.py \\
        --manifest outputs/.../crops/candidate_manifest.json

Run the ``--all`` sweep on sapphire: the clustering is O(n^2) per pass and a
30-pass pool takes minutes.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-09-12
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from merge_passes import (  # noqa: E402
    apply_threshold,
    cluster_across_passes,
    deduplicate_within_pass,
    geojson_coords_to_utm,
    load_pass_detections,
    resolve_pass_files,
)

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

REPO_ROOT = _SCRIPT_DIR.parent

#: Default coordinate tolerance for calling two features "the same detection".
#: One metre is two orders of magnitude below the 20 m clustering tolerance,
#: so it separates "identical output" from "same pool, different clustering"
#: without tripping on float round-tripping through GeoJSON.
DEFAULT_TOLERANCE_M = 1.0

#: Manifest of registered conditions — the set of unions worth checking.
CONDITIONS_MANIFEST = Path("results/conditions-manifest.json")

# ---------------------------------------------------------------------------
# Pool resolution
# ---------------------------------------------------------------------------
#
# For most unions the pool is the parent of the consensus directory, because
# ``build_all_consensus.build_merge_command`` invokes
# ``merge_passes.py --input-dir <cell> --output-dir <cell>/consensus --sweep``.
# A handful of runs predate that driver and put the union elsewhere. Each
# exception below carries the anchor that establishes its pool, so a reader can
# re-verify the mapping rather than trust this table.

#: union directory (repo-relative) -> pool directory (repo-relative).
POOL_OVERRIDES: dict[str, str] = {
    # Anchor: results/run-conditions.json, decomposition.gold-standard-v2
    # .proposer_pools = {"detect_brief-text": "text"}; the passes are at
    # outputs/gs/gold-standard-v2/proposer/detect_brief-text/run_1..run_5.
    "outputs/gs/gold-standard-v2/consensus":
        "outputs/gs/gold-standard-v2/proposer/detect_brief-text",
    # Anchor: results/run-conditions.json, decomposition.consensus-384-t1-0
    # .proposer_pools = {"384": {"path": "384"}}.
    "outputs/h11/consensus-384-UNINTENDED-T1.0/voting":
        "outputs/h11/consensus-384-UNINTENDED-T1.0/384",
    # Anchor: results/run-conditions.json, decomposition.h8-v2.proposer_pools
    # — each cell's pool is the sibling directory of the same name.
    "outputs/h8-v2/greedy/canonical": "outputs/h8-v2/canonical",
    "outputs/h8-v2/greedy/plus-hp": "outputs/h8-v2/plus-hp",
    "outputs/h8-v2/greedy/pure-positive-canon": "outputs/h8-v2/pure-positive-canon",
    "outputs/h8-v2/greedy/scale-4": "outputs/h8-v2/scale-4",
    "outputs/h8-v2/greedy/scale-8": "outputs/h8-v2/scale-8",
    "outputs/h8-v2/greedy/scale-16": "outputs/h8-v2/scale-16",
    "outputs/h8-v2/greedy/scale-32": "outputs/h8-v2/scale-32",
    # Anchor: results/run-conditions.json, decomposition.h12-v2.proposer_pools.
    "outputs/h12-v2/greedy/r1-hn-heavy": "outputs/h12-v2/r1-hn-heavy",
    "outputs/h12-v2/greedy/r3-hp-heavy": "outputs/h12-v2/r3-hp-heavy",
    # r2-balanced has no pool of its own: it reuses the h10 pool_160_hp4hn4
    # passes. Anchors: results/run-facts.json facts.h12-v2._flags
    # ("r2-balanced reuses h10 pool") and scripts/fuse_detections_wbf.py:136-142,
    # which names outputs/h10/evaluation-v2/pool_160_hp4hn4/run_{1..5}.
    "outputs/h12-v2/greedy/r2-balanced": "outputs/h10/evaluation-v2/pool_160_hp4hn4",
}

#: union directory -> why its parameters are not recoverable.
UNRESOLVABLE: dict[str, str] = {
    # Anchor: results/run-conditions.json, decomposition.pv-diag-256._note —
    # "Proposer passes were NOT materialised as run_* dirs (only consensus +
    # crops), so proposer_pools is empty".
    "outputs/h11/pv-diag-256/consensus":
        "proposer passes were never materialised as run_*/pass_* directories "
        "(results/run-conditions.json, decomposition.pv-diag-256._note)",
}

#: Union filenames, and how to read the vote threshold out of them.
_T_PATTERNS = (
    re.compile(r"^consensus_t(?P<t>\d+)\.geojson$"),
    re.compile(r"^(?:consensus|text|image)-(?P<t>\d+)of(?P<n>\d+)\.geojson$"),
)

#: A ``consensus-nN`` directory declares the first-N sub-pool. Anchor:
#: scripts/build_phase3_subpool_consensus.py:23-28 ("``--passes 1,..,N`` which
#: restricts to ``run_1..run_N`` *by parsed run number* … the first N passes")
#: and scripts/run_phase3a_image_analysis.sh:105-117 (``"1,2,3,4,5"``).
_SUBPOOL_DIR = re.compile(r"^consensus-n(?P<n>\d+)$")


@dataclass
class UnionSpec:
    """The parameters needed to re-derive one committed union.

    Attributes:
        union_path: Repo-relative path of the committed union GeoJSON.
        union_dir: Repo-relative directory holding the union.
        pool_dir: Repo-relative directory holding the pool's pass
            subdirectories, or ``None`` when it could not be resolved.
        threshold: The vote threshold the union was written at.
        pass_filter: The ``--passes`` selection for a declared sub-pool, or
            ``None`` for a whole-pool union.
        declared_subpool_n: ``N`` when the union directory declares a
            first-N sub-pool, else ``None``.
        unresolved_reason: Set when the union cannot be re-derived at all.
    """

    union_path: str
    union_dir: str
    pool_dir: str | None
    threshold: int | None
    pass_filter: list[int] | None
    declared_subpool_n: int | None
    unresolved_reason: str | None = None


@dataclass
class UnionResult:
    """The outcome of re-deriving and comparing one union."""

    union_path: str
    classification: str
    pool_dir: str | None = None
    threshold: int | None = None
    declared_subpool_n: int | None = None
    committed_features: int | None = None
    rederived_features: int | None = None
    rederived_from: str | None = None
    pool_passes: list[str] = field(default_factory=list)
    union_passes_used: list[str] = field(default_factory=list)
    passes_not_reflected: list[str] = field(default_factory=list)
    unmatched_committed: int | None = None
    unmatched_rederived: int | None = None
    max_match_distance_m: float | None = None
    vs_total_passes: int | None = None
    reflects_subset: list[str] | None = None
    detail: str = ""
    seconds: float | None = None


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


def resolve_union_spec(union_path: Path, repo_root: Path = REPO_ROOT) -> UnionSpec:
    """Work out how a committed union would be rebuilt.

    Args:
        union_path: Path of the committed union GeoJSON, absolute or
            relative to ``repo_root``.
        repo_root: Repository root the returned paths are relative to.

    Returns:
        The :class:`UnionSpec` for the union. ``unresolved_reason`` is set
        when the union cannot be re-derived; the other fields are then
        best-effort.

    Examples:
        >>> spec = resolve_union_spec(Path(
        ...     "outputs/retest/phase3a/track2-text/T1.0/consensus-n5/consensus_t4.geojson"
        ... ))  # doctest: +SKIP
        >>> spec.pass_filter  # doctest: +SKIP
        [1, 2, 3, 4, 5]
    """
    rel = _repo_relative(union_path, repo_root)
    union_dir = str(Path(rel).parent)
    name = Path(rel).name

    threshold: int | None = None
    for pattern in _T_PATTERNS:
        m = pattern.match(name)
        if m:
            threshold = int(m.group("t"))
            break

    sub = _SUBPOOL_DIR.match(Path(union_dir).name)
    declared_n = int(sub.group("n")) if sub else None
    pass_filter = list(range(1, declared_n + 1)) if declared_n else None

    if union_dir in UNRESOLVABLE:
        return UnionSpec(rel, union_dir, None, threshold, pass_filter, declared_n,
                         UNRESOLVABLE[union_dir])

    pool_dir = POOL_OVERRIDES.get(union_dir)
    if pool_dir is None:
        pool_dir = str(Path(union_dir).parent)

    if not _has_passes(repo_root / pool_dir):
        return UnionSpec(
            rel, union_dir, None, threshold, pass_filter, declared_n,
            f"no run_*/pass_* directories under the resolved pool {pool_dir}",
        )
    if threshold is None:
        return UnionSpec(
            rel, union_dir, pool_dir, None, pass_filter, declared_n,
            f"vote threshold not readable from the filename {name!r}",
        )
    return UnionSpec(rel, union_dir, pool_dir, threshold, pass_filter, declared_n)


def _repo_relative(path: Path, repo_root: Path = REPO_ROOT) -> str:
    """Return ``path`` relative to ``repo_root`` using forward slashes."""
    try:
        return str(Path(path).resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def _has_passes(directory: Path) -> bool:
    """True when ``directory`` holds ``run_*`` or ``pass_*`` subdirectories."""
    if not directory.is_dir():
        return False
    return any(
        d.is_dir() for d in list(directory.glob("run_*")) + list(directory.glob("pass_*"))
    )


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


def _utm_points(features: Iterable[dict]) -> list[tuple[float, float]]:
    """Project each feature's point geometry to UTM metres.

    Consensus unions are ``Point`` features written by
    ``merge_passes.apply_threshold``, stored in WGS84 (RFC 7946).

    Args:
        features: GeoJSON features.

    Returns:
        One ``(easting, northing)`` pair per feature, in input order.
    """
    points: list[tuple[float, float]] = []
    for feat in features:
        geom = feat.get("geometry") or {}
        coords = geom.get("coordinates")
        if not coords:
            continue
        x, y = float(coords[0]), float(coords[1])
        points.append(geojson_coords_to_utm(x, y))
    return points


def compare_feature_sets(
    committed: list[dict],
    rederived: list[dict],
    tolerance_m: float = DEFAULT_TOLERANCE_M,
) -> dict[str, Any]:
    """Compare two union feature sets by count and by coordinate.

    The coordinate test is a bidirectional nearest-neighbour match: every
    committed feature must have a re-derived feature within ``tolerance_m``
    and vice versa. Matching both ways catches a union that is a strict
    subset or superset of the re-derivation as well as one that has moved.

    Args:
        committed: Features read from the committed union.
        rederived: Features from the re-derived union.
        tolerance_m: Match radius in metres.

    Returns:
        Dict with ``identical`` (bool), ``unmatched_committed``,
        ``unmatched_rederived``, and ``max_match_distance_m`` (the largest
        distance among matched pairs, ``None`` when nothing matched).
    """
    a = _utm_points(committed)
    b = _utm_points(rederived)

    unmatched_a, max_dist_a = _count_unmatched(a, b, tolerance_m)
    unmatched_b, max_dist_b = _count_unmatched(b, a, tolerance_m)
    dists = [d for d in (max_dist_a, max_dist_b) if d is not None]

    return {
        "identical": (
            len(a) == len(b) and unmatched_a == 0 and unmatched_b == 0
        ),
        "unmatched_committed": unmatched_a,
        "unmatched_rederived": unmatched_b,
        "max_match_distance_m": max(dists) if dists else None,
    }


def _count_unmatched(
    source: list[tuple[float, float]],
    target: list[tuple[float, float]],
    tolerance_m: float,
) -> tuple[int, float | None]:
    """Count points in ``source`` with no ``target`` point within tolerance.

    Uses a grid index so a 5,000-point union compares in milliseconds rather
    than the 25 M distance computations of the naive double loop.

    Args:
        source: Points to look up.
        target: Points to look up against.
        tolerance_m: Match radius in metres.

    Returns:
        ``(unmatched_count, largest_matched_distance)``.
    """
    if not target:
        return len(source), None

    cell = max(tolerance_m, 1e-6)
    index: dict[tuple[int, int], list[tuple[float, float]]] = {}
    for x, y in target:
        index.setdefault((int(x // cell), int(y // cell)), []).append((x, y))

    unmatched = 0
    max_dist: float | None = None
    for x, y in source:
        gx, gy = int(x // cell), int(y // cell)
        best: float | None = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for tx, ty in index.get((gx + dx, gy + dy), ()):
                    dist = ((x - tx) ** 2 + (y - ty) ** 2) ** 0.5
                    if best is None or dist < best:
                        best = dist
        if best is None or best > tolerance_m:
            unmatched += 1
        elif max_dist is None or best > max_dist:
            max_dist = best
    return unmatched, max_dist


# ---------------------------------------------------------------------------
# Re-derivation
# ---------------------------------------------------------------------------


def rederive_union(
    pool_dir: Path,
    threshold: int,
    pass_filter: list[int] | None,
    scratch_path: Path | None = None,
) -> tuple[list[dict], list[str]]:
    """Rebuild one union from its pool with ``merge_passes``' own algorithm.

    Args:
        pool_dir: Directory holding the pool's ``run_*`` / ``pass_*`` dirs.
        threshold: Vote threshold to apply.
        pass_filter: ``--passes`` selection, or ``None`` for the whole pool.
        scratch_path: Optional path to write the re-derived union to, for
            inspection. Never a committed path — the caller is responsible
            for pointing this at a scratch tree.

    Returns:
        ``(features, pass_ids)`` — the re-derived features and the sorted
        pass identifiers that contributed.
    """
    raw = load_pass_detections(pool_dir, pass_filter)
    if not raw:
        return [], []
    deduped = {pid: deduplicate_within_pass(feats) for pid, feats in raw.items()}
    clusters = cluster_across_passes(deduped)
    consensus = apply_threshold(clusters, threshold, len(raw))
    features = list(consensus.get("features", []))
    if scratch_path is not None:
        scratch_path.parent.mkdir(parents=True, exist_ok=True)
        scratch_path.write_text(json.dumps(consensus, indent=2))
    return features, sorted(raw.keys())


def check_union(
    union_path: Path,
    scratch_dir: Path,
    tolerance_m: float = DEFAULT_TOLERANCE_M,
    repo_root: Path = REPO_ROOT,
) -> UnionResult:
    """Re-derive one committed union and classify the comparison.

    Args:
        union_path: The committed union GeoJSON.
        scratch_dir: Directory for re-derived output. Never written inside
            the repository's committed trees.
        tolerance_m: Coordinate match radius in metres.
        repo_root: Repository root.

    Returns:
        The :class:`UnionResult` for this union.
    """
    started = time.time()
    spec = resolve_union_spec(union_path, repo_root)
    committed_file = repo_root / spec.union_path
    committed: list[dict] = []
    if committed_file.exists():
        committed = list(json.loads(committed_file.read_text()).get("features", []))

    vs_file = repo_root / spec.union_dir / "voting_summary.json"
    vs_total = None
    if vs_file.exists():
        try:
            vs_total = json.loads(vs_file.read_text()).get("total_passes")
        except json.JSONDecodeError:
            vs_total = None

    if spec.unresolved_reason:
        return UnionResult(
            union_path=spec.union_path,
            classification="UNRESOLVED",
            pool_dir=spec.pool_dir,
            threshold=spec.threshold,
            declared_subpool_n=spec.declared_subpool_n,
            committed_features=len(committed) if committed_file.exists() else None,
            vs_total_passes=vs_total,
            detail=spec.unresolved_reason,
            seconds=round(time.time() - started, 2),
        )

    assert spec.pool_dir is not None and spec.threshold is not None
    pool_dir = repo_root / spec.pool_dir
    pool_passes = sorted(resolve_pass_files(pool_dir, None).keys(), key=_pass_sort_key)

    slug = spec.union_path.replace("/", "__")
    attempts: list[tuple[str, list[int] | None]] = []
    if spec.pass_filter is not None:
        attempts.append(("declared sub-pool", spec.pass_filter))
        attempts.append(("whole pool", None))
    else:
        attempts.append(("whole pool", None))

    best: UnionResult | None = None
    for label, pass_filter in attempts:
        features, used = rederive_union(
            pool_dir, spec.threshold, pass_filter,
            scratch_dir / f"{slug}.{label.replace(' ', '-')}.geojson",
        )
        cmp = compare_feature_sets(committed, features, tolerance_m)
        not_reflected = [p for p in pool_passes if p not in used]
        if cmp["identical"]:
            classification = (
                "SUBPOOL-CONSISTENT"
                if pass_filter is not None and not_reflected
                else "REPRODUCES"
            )
            return UnionResult(
                union_path=spec.union_path,
                classification=classification,
                pool_dir=spec.pool_dir,
                threshold=spec.threshold,
                declared_subpool_n=spec.declared_subpool_n,
                committed_features=len(committed),
                rederived_features=len(features),
                rederived_from=label,
                pool_passes=pool_passes,
                union_passes_used=used,
                passes_not_reflected=not_reflected,
                unmatched_committed=cmp["unmatched_committed"],
                unmatched_rederived=cmp["unmatched_rederived"],
                max_match_distance_m=cmp["max_match_distance_m"],
                vs_total_passes=vs_total,
                detail=f"reproduces from the {label}",
                seconds=round(time.time() - started, 2),
            )
        candidate = UnionResult(
            union_path=spec.union_path,
            classification="STALE",
            pool_dir=spec.pool_dir,
            threshold=spec.threshold,
            declared_subpool_n=spec.declared_subpool_n,
            committed_features=len(committed),
            rederived_features=len(features),
            rederived_from=label,
            pool_passes=pool_passes,
            union_passes_used=used,
            passes_not_reflected=not_reflected,
            unmatched_committed=cmp["unmatched_committed"],
            unmatched_rederived=cmp["unmatched_rederived"],
            max_match_distance_m=cmp["max_match_distance_m"],
            vs_total_passes=vs_total,
            detail=(
                f"re-derivation from the {label} "
                f"({len(used)} passes) gives {len(features)} features against "
                f"{len(committed)} committed; {cmp['unmatched_committed']} committed "
                f"features have no re-derived match within {tolerance_m:g} m and "
                f"{cmp['unmatched_rederived']} re-derived features have no committed match"
            ),
            seconds=round(time.time() - started, 2),
        )
        if best is None or abs(
            (candidate.rederived_features or 0) - (candidate.committed_features or 0)
        ) < abs((best.rederived_features or 0) - (best.committed_features or 0)):
            best = candidate

    assert best is not None
    # Nothing the union declares reproduces it. Name what it DOES reflect, so
    # the verdict says which passes are missing rather than only that some are.
    # The candidate is the first-N prefix for the pass count the union's own
    # voting_summary.json recorded, which is the only provenance a pre-fix
    # union carries.
    if vs_total and 0 < vs_total < len(pool_passes):
        features, used = rederive_union(
            pool_dir, spec.threshold, list(range(1, vs_total + 1)),
            scratch_dir / f"{slug}.identified-first-{vs_total}.geojson",
        )
        if compare_feature_sets(committed, features, tolerance_m)["identical"]:
            missing = [p for p in pool_passes if p not in used]
            best.reflects_subset = used
            best.passes_not_reflected = missing
            best.detail = (
                f"reproduces exactly from the FIRST {vs_total} of "
                f"{len(pool_passes)} passes ({', '.join(used)}) and from no "
                f"declared selection: the union does not reflect "
                f"{', '.join(missing)}, and nothing on disk declares it a "
                f"sub-pool (its directory is {Path(spec.union_dir).name!r}, "
                f"not consensus-n{vs_total})"
            )
    best.seconds = round(time.time() - started, 2)
    return best


def _pass_sort_key(pass_id: str) -> tuple[str, int]:
    """Sort ``run_2`` before ``run_10`` rather than lexicographically."""
    m = re.match(r"^(run|pass)_(\d+)$", pass_id)
    return (m.group(1), int(m.group(2))) if m else (pass_id, 0)


# ---------------------------------------------------------------------------
# Enumeration of unions a registered condition reads
# ---------------------------------------------------------------------------


def enumerate_registered_unions(
    repo_root: Path = REPO_ROOT,
    manifest_path: Path | None = None,
) -> dict[str, list[str]]:
    """Find every consensus union that a registered condition reads.

    A condition reaches its union either directly (a ``.geojson`` in
    ``provenance.source_files``) or through the ``evaluation.json`` that
    scored it (``_metadata.input_files.detections``). Both hops are followed.
    Single-pass detections, verifier-accepted sets, and Weighted Box Fusion
    (WBF) outputs are excluded: they are not ``merge_passes.py`` unions.

    Args:
        repo_root: Repository root.
        manifest_path: Override for ``results/conditions-manifest.json``.

    Returns:
        Mapping of repo-relative union path to the sorted condition ids
        that read it.
    """
    manifest_path = manifest_path or (repo_root / CONDITIONS_MANIFEST)
    manifest = json.loads(Path(manifest_path).read_text())

    readers: dict[str, set[str]] = {}
    for cond in manifest.get("conditions", []):
        cid = cond["condition_id"]
        for src in cond.get("provenance", {}).get("source_files", []):
            for path in _detection_paths(repo_root, src):
                readers.setdefault(path, set()).add(cid)

    return {
        path: sorted(cids)
        for path, cids in readers.items()
        if _is_union_path(repo_root, path)
    }


def _detection_paths(repo_root: Path, source: str) -> list[str]:
    """Resolve one ``source_files`` entry to the detection files behind it."""
    if source.endswith(".geojson"):
        return [source]
    if not source.endswith("evaluation.json"):
        return []
    path = repo_root / source
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return []
    dets = ((data.get("_metadata") or {}).get("input_files") or {}).get("detections") or []
    if isinstance(dets, str):
        dets = [dets]
    return [d for d in dets if isinstance(d, str) and d.endswith(".geojson")]


def _is_union_path(repo_root: Path, path: str) -> bool:
    """True when ``path`` looks like a ``merge_passes.py`` consensus union."""
    if not path.startswith("outputs/"):
        return False
    p = Path(path)
    if p.name.startswith(("detections", "accepted_", "wbf_")):
        return False
    if not any(pattern.match(p.name) for pattern in _T_PATTERNS):
        return False
    in_consensus_dir = p.parent.name == "voting" or p.parent.name.startswith("consensus")
    beside_summary = (repo_root / p.parent / "voting_summary.json").exists()
    return in_consensus_dir or beside_summary


# ---------------------------------------------------------------------------
# A crop manifest against its source union
# ---------------------------------------------------------------------------
#
# The union is the record of what the proposer passes agreed on; the crop
# manifest is the record of what the verifier was actually shown, and the file
# the boards read vote counts out of. They are written by different code at
# different times, and when they drift the drift is silent:
# ``results/im-june-pool-grid-2026-09-20/findings.md`` § 7 found five legacy
# manifests carrying a ``vote_count`` one low on 15 to 110 candidates each,
# and one manifest a whole candidate short of its union, because the
# 2026-05-03 recovery campaign's incremental extractor matched greedily and
# never refreshed a matched entry. This check is the standing guard against
# that class: before any verifier spend, the manifest must agree with the
# union it declares.

#: Match radius for pairing a manifest entry with a union feature when the
#: candidate-id index does not line up. 20 m is the radius the unions are
#: clustered at, so a counterpart further away than that is a different
#: detection rather than the same one written twice.
DEFAULT_MANIFEST_MATCH_RADIUS_M = 20.0

#: How many disagreeing ids a one-line summary names before eliding.
_DETAIL_ID_LIMIT = 20


@dataclass
class ManifestVoteResult:
    """The outcome of checking one crop manifest against its source union.

    Attributes:
        manifest_path: Repo-relative path of the crop manifest.
        union_path: Repo-relative path of the union it was compared against.
        classification: ``AGREES``, ``DISAGREES``, ``NOT-APPLICABLE`` (no
            vote counts on either side — a single-pass proposer output) or
            ``UNRESOLVED`` (the union could not be read).
        manifest_candidates: Candidate count in the manifest.
        union_features: Feature count in the union.
        pairing: How entries were paired — ``candidate-id-index`` or
            ``spatial-nearest``.
        vote_mismatches: One record per candidate whose ``vote_count``
            differs, with both values.
        manifest_only: Candidate ids with no union counterpart.
        union_only: Union feature indices with no manifest candidate.
        reconciled_failed_extractions: Union features with no candidate that
            the manifest's own ``failed_extractions`` accounts for.
        detail: One-line human summary.
    """

    manifest_path: str
    union_path: str | None
    classification: str
    manifest_candidates: int = 0
    union_features: int = 0
    pairing: str | None = None
    vote_mismatches: list[dict[str, Any]] = field(default_factory=list)
    manifest_only: list[Any] = field(default_factory=list)
    union_only: list[int] = field(default_factory=list)
    reconciled_failed_extractions: int = 0
    detail: str = ""

    @property
    def ok(self) -> bool:
        """True unless the manifest demonstrably disagrees with its union.

        ``UNRESOLVED`` is deliberately not a failure: a union that has been
        archived off the machine must not block a verifier run that is
        otherwise sound. Only a comparison that ran and found a difference
        stops the chain.
        """
        return self.classification != "DISAGREES"


def _indexed_utm_points(features: Iterable[dict]) -> list[tuple[float, float] | None]:
    """Project features to UTM metres, keeping input positions.

    Unlike :func:`_utm_points` this never drops a feature, because the
    manifest comparison pairs by position and a silent drop would shift
    every id after it.

    Args:
        features: GeoJSON features.

    Returns:
        One ``(easting, northing)`` pair per feature, ``None`` where the
        geometry is unusable.
    """
    points: list[tuple[float, float] | None] = []
    for feat in features:
        coords = ((feat.get("geometry") or {}).get("coordinates")) or []
        if len(coords) < 2:
            points.append(None)
            continue
        x, y = float(coords[0]), float(coords[1])
        # Unions are WGS84 (RFC 7946); a manifest-shaped input may already
        # be in metres, which the magnitude test separates.
        if abs(x) <= 180 and abs(y) <= 90:
            points.append(geojson_coords_to_utm(x, y))
        else:
            points.append((x, y))
    return points


def _candidate_points(
    candidates: Iterable[dict],
) -> list[tuple[float, float] | None]:
    """Read each manifest candidate's UTM centroid, keeping input positions."""
    points: list[tuple[float, float] | None] = []
    for cand in candidates:
        x, y = cand.get("centroid_x"), cand.get("centroid_y")
        points.append((float(x), float(y)) if x is not None and y is not None else None)
    return points


def _vote_of(properties: dict | None) -> Any:
    """Read ``vote_count`` out of a properties dict, or ``None``."""
    return (properties or {}).get("vote_count")


def resolve_manifest_union(
    manifest: dict,
    manifest_path: Path,
    repo_root: Path = REPO_ROOT,
) -> Path | None:
    """Find the union a crop manifest was cut from.

    ``extract_candidates.extract_candidates`` records it as
    ``source_geojson``. The value may be repo-relative (the usual case),
    absolute, or relative to the manifest itself.

    Args:
        manifest: Parsed ``candidate_manifest.json``.
        manifest_path: Where that manifest was read from.
        repo_root: Repository root.

    Returns:
        An existing path, or ``None`` when the declaration is missing or
        points at a file that is not on this machine.
    """
    declared = manifest.get("source_geojson")
    if not declared:
        return None
    for candidate in (
        Path(declared),
        repo_root / declared,
        manifest_path.parent / declared,
    ):
        if candidate.exists():
            return candidate
    return None


def _pair_by_candidate_id(
    candidate_points: list[tuple[float, float] | None],
    candidate_ids: list[Any],
    feature_points: list[tuple[float, float] | None],
    tolerance_m: float,
) -> dict[int, int] | None:
    """Pair manifest entries to union features by ``candidate_id`` index.

    ``extract_candidates`` numbers a candidate with its feature's index in
    the source union, so the index IS the pairing when it holds up. It is
    accepted only when every id is a distinct in-range integer and every
    paired centroid agrees within ``tolerance_m``; otherwise the caller
    falls back to spatial pairing.

    Returns:
        Manifest position to feature index, or ``None`` when the index
        convention does not hold.
    """
    n_features = len(feature_points)
    if len(set(candidate_ids)) != len(candidate_ids):
        return None
    pairing: dict[int, int] = {}
    for position, cid in enumerate(candidate_ids):
        if not isinstance(cid, int) or isinstance(cid, bool) or not 0 <= cid < n_features:
            return None
        mpt, fpt = candidate_points[position], feature_points[cid]
        if mpt is not None and fpt is not None:
            dist = ((mpt[0] - fpt[0]) ** 2 + (mpt[1] - fpt[1]) ** 2) ** 0.5
            if dist > tolerance_m:
                return None
        pairing[position] = cid
    return pairing


def _pair_spatially(
    candidate_points: list[tuple[float, float] | None],
    feature_points: list[tuple[float, float] | None],
    radius_m: float,
) -> dict[int, int]:
    """Pair manifest entries to union features nearest-first, one to one.

    The same rule the incremental extractor now matches by: every pair
    inside ``radius_m`` sorted by distance, each side claimable once, so
    two detections inside one radius cannot collapse into one pairing.

    Args:
        candidate_points: Manifest centroids, by position.
        feature_points: Union centroids, by index.
        radius_m: Match radius in metres.

    Returns:
        Manifest position to feature index.
    """
    cell = max(radius_m, 1e-6)
    index: dict[tuple[int, int], list[int]] = {}
    for fi, pt in enumerate(feature_points):
        if pt is None:
            continue
        index.setdefault((int(pt[0] // cell), int(pt[1] // cell)), []).append(fi)

    pairs: list[tuple[float, int, int]] = []
    for mi, pt in enumerate(candidate_points):
        if pt is None:
            continue
        gx, gy = int(pt[0] // cell), int(pt[1] // cell)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for fi in index.get((gx + dx, gy + dy), ()):
                    fpt = feature_points[fi]
                    assert fpt is not None
                    dist = ((pt[0] - fpt[0]) ** 2 + (pt[1] - fpt[1]) ** 2) ** 0.5
                    if dist <= radius_m:
                        pairs.append((dist, mi, fi))

    pairs.sort()
    pairing: dict[int, int] = {}
    claimed: set[int] = set()
    for _dist, mi, fi in pairs:
        if mi in pairing or fi in claimed:
            continue
        pairing[mi] = fi
        claimed.add(fi)
    return pairing


def _elide(ids: list[Any]) -> str:
    """Render an id list for a one-line summary, eliding a long tail."""
    head = ", ".join(str(i) for i in ids[:_DETAIL_ID_LIMIT])
    if len(ids) > _DETAIL_ID_LIMIT:
        return f"{head}, ... and {len(ids) - _DETAIL_ID_LIMIT} more"
    return head


def check_manifest_votes(
    manifest_path: Path,
    union_path: Path | None = None,
    repo_root: Path = REPO_ROOT,
    tolerance_m: float = DEFAULT_TOLERANCE_M,
    match_radius_m: float = DEFAULT_MANIFEST_MATCH_RADIUS_M,
) -> ManifestVoteResult:
    """Check that a crop manifest agrees with the union it was cut from.

    Compares, per candidate, the ``vote_count`` the manifest carries against
    the one the union feature carries, and compares the two counts of
    detections. A manifest that fails has been patched out of step with its
    union — the 2026-05-03 defect — and any verifier spend against it would
    book votes the consensus does not support.

    Args:
        manifest_path: Path to a ``candidate_manifest.json``.
        union_path: The union to compare against. Defaults to the manifest's
            own ``source_geojson`` declaration.
        repo_root: Repository root, for resolving that declaration.
        tolerance_m: Centroid agreement required before the ``candidate_id``
            index is trusted as the pairing.
        match_radius_m: Radius for the spatial pairing fallback.

    Returns:
        A :class:`ManifestVoteResult`. ``DISAGREES`` is the only
        classification that should stop a run.

    Example:
        >>> res = check_manifest_votes(Path("outputs/x/crops/candidate_manifest.json"))
        ... # doctest: +SKIP
        >>> res.ok  # doctest: +SKIP
        True
    """
    manifest_rel = _repo_relative(manifest_path, repo_root)
    try:
        manifest = json.loads(Path(manifest_path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return ManifestVoteResult(
            manifest_path=manifest_rel, union_path=None,
            classification="UNRESOLVED",
            detail=f"manifest could not be read: {exc}",
        )

    candidates = manifest.get("candidates") or []
    resolved_union = Path(union_path) if union_path else resolve_manifest_union(
        manifest, Path(manifest_path), repo_root,
    )
    if resolved_union is None or not resolved_union.exists():
        declared = manifest.get("source_geojson") or "(none declared)"
        return ManifestVoteResult(
            manifest_path=manifest_rel, union_path=None,
            classification="UNRESOLVED",
            manifest_candidates=len(candidates),
            detail=(
                f"source union not on this machine: {declared}. The vote "
                f"agreement of {len(candidates)} candidates is UNCHECKED."
            ),
        )

    union_rel = _repo_relative(resolved_union, repo_root)
    try:
        features = (json.loads(resolved_union.read_text()).get("features")) or []
    except (OSError, json.JSONDecodeError) as exc:
        return ManifestVoteResult(
            manifest_path=manifest_rel, union_path=union_rel,
            classification="UNRESOLVED",
            manifest_candidates=len(candidates),
            detail=f"union could not be read: {exc}",
        )

    if not candidates:
        return ManifestVoteResult(
            manifest_path=manifest_rel, union_path=union_rel,
            classification="NOT-APPLICABLE", union_features=len(features),
            detail="manifest holds no candidates",
        )

    manifest_votes = [_vote_of(c.get("properties")) for c in candidates]
    union_votes = [_vote_of(f.get("properties")) for f in features]
    if all(v is None for v in manifest_votes) and all(v is None for v in union_votes):
        return ManifestVoteResult(
            manifest_path=manifest_rel, union_path=union_rel,
            classification="NOT-APPLICABLE",
            manifest_candidates=len(candidates), union_features=len(features),
            detail=(
                "neither side carries vote_count — a single-pass proposer "
                "output has no votes to compare"
            ),
        )

    candidate_ids = [c.get("candidate_id") for c in candidates]
    candidate_points = _candidate_points(candidates)
    feature_points = _indexed_utm_points(features)

    pairing = _pair_by_candidate_id(
        candidate_points, candidate_ids, feature_points, tolerance_m,
    )
    how = "candidate-id-index"
    if pairing is None:
        pairing = _pair_spatially(candidate_points, feature_points, match_radius_m)
        how = "spatial-nearest"

    mismatches = [
        {
            "candidate_id": candidate_ids[position],
            "manifest_vote_count": manifest_votes[position],
            "union_vote_count": union_votes[feature_index],
            "union_feature_index": feature_index,
        }
        for position, feature_index in sorted(pairing.items())
        if manifest_votes[position] != union_votes[feature_index]
    ]
    manifest_only = [
        candidate_ids[position]
        for position in range(len(candidates)) if position not in pairing
    ]
    paired_features = set(pairing.values())
    union_only = [i for i in range(len(features)) if i not in paired_features]

    # A union feature with no candidate is expected when extraction failed on
    # it, and the manifest books that count itself. Anything beyond the booked
    # number is a candidate the verifier was never shown.
    booked_failures = manifest.get("failed_extractions") or 0
    reconciled = (
        len(union_only) if union_only and len(union_only) == booked_failures else 0
    )
    unexplained_union_only = [] if reconciled else union_only

    problems: list[str] = []
    if mismatches:
        problems.append(
            f"{len(mismatches)} candidate(s) disagree on vote_count: "
            f"{_elide([m['candidate_id'] for m in mismatches])}"
        )
    if manifest_only:
        problems.append(
            f"{len(manifest_only)} candidate(s) have no union counterpart: "
            f"{_elide(manifest_only)}"
        )
    if unexplained_union_only:
        problems.append(
            f"{len(unexplained_union_only)} union feature(s) have no candidate: "
            f"index {_elide(unexplained_union_only)}"
        )

    counts = (
        f"{len(candidates)} candidates against {len(features)} union features, "
        f"paired by {how}"
    )
    if problems:
        detail = f"{counts}. " + "; ".join(problems)
    else:
        detail = f"{counts}. Every vote_count agrees."
        if reconciled:
            detail += (
                f" {reconciled} union feature(s) without a candidate are "
                f"accounted for by the manifest's failed_extractions."
            )

    return ManifestVoteResult(
        manifest_path=manifest_rel, union_path=union_rel,
        classification="DISAGREES" if problems else "AGREES",
        manifest_candidates=len(candidates), union_features=len(features),
        pairing=how, vote_mismatches=mismatches, manifest_only=manifest_only,
        union_only=union_only, reconciled_failed_extractions=reconciled,
        detail=detail,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _run_one(args: tuple[str, str, float, str]) -> dict[str, Any]:
    """Worker entry point: check one union and return its result as a dict."""
    union, scratch, tol, root = args
    return asdict(check_union(Path(union), Path(scratch), tol, Path(root)))


def _run_manifest_checks(args: argparse.Namespace, repo_root: Path) -> int:
    """Run ``--manifest`` checks and report them. Returns 1 on any disagreement.

    Args:
        args: Parsed CLI arguments.
        repo_root: Repository root.

    Returns:
        1 when any manifest classified ``DISAGREES``, else 0.
    """
    if args.manifest_union and len(args.manifest) != 1:
        print(
            "--manifest-union applies to exactly one --manifest.", file=sys.stderr,
        )
        return 2

    failed = 0
    results: list[dict[str, Any]] = []
    for manifest in args.manifest:
        result = check_manifest_votes(
            manifest,
            union_path=args.manifest_union,
            repo_root=repo_root,
            tolerance_m=args.tolerance_m,
            match_radius_m=args.manifest_match_radius_m,
        )
        print(f"{result.classification:16s} {result.manifest_path}")
        print(f"  union: {result.union_path}")
        print(f"  {result.detail}")
        for mismatch in result.vote_mismatches[:_DETAIL_ID_LIMIT]:
            print(
                f"    candidate {mismatch['candidate_id']}: manifest "
                f"vote_count {mismatch['manifest_vote_count']} against union "
                f"{mismatch['union_vote_count']} "
                f"(union feature {mismatch['union_feature_index']})",
            )
        if len(result.vote_mismatches) > _DETAIL_ID_LIMIT:
            print(
                f"    ... and {len(result.vote_mismatches) - _DETAIL_ID_LIMIT} "
                f"more disagreeing candidates",
            )
        if not result.ok:
            failed = 1
        results.append(asdict(result))

    if args.json_out and results:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(
            {"script_version": __version__, "manifest_results": results}, indent=2,
        ))
        print(f"Wrote {args.json_out}")
    return failed


def build_cli_parser() -> argparse.ArgumentParser:
    """Construct the command-line parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Re-derive a committed consensus union from its pool and classify it "
            "REPRODUCES / SUBPOOL-CONSISTENT / STALE / UNRESOLVED (audit Finding 4)"
        ),
    )
    parser.add_argument(
        "--union", type=Path, action="append", default=[],
        help="A committed union GeoJSON to check (repeatable)",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Check every union a registered condition reads",
    )
    parser.add_argument(
        "--manifest", type=Path, action="append", default=[],
        help=(
            "A candidate_manifest.json to check against the union it "
            "declares in source_geojson (repeatable). Exits 1 on any "
            "vote_count or count disagreement."
        ),
    )
    parser.add_argument(
        "--manifest-union", type=Path, default=None,
        help=(
            "Union to compare --manifest against, overriding its own "
            "source_geojson declaration. Only valid with a single --manifest."
        ),
    )
    parser.add_argument(
        "--manifest-match-radius-m", type=float,
        default=DEFAULT_MANIFEST_MATCH_RADIUS_M,
        help=(
            "Radius for the spatial pairing fallback when candidate ids are "
            f"not union indices (default: {DEFAULT_MANIFEST_MATCH_RADIUS_M:g})"
        ),
    )
    parser.add_argument(
        "--scratch-dir", type=Path,
        help=(
            "Directory for re-derived unions. Default: a temporary directory "
            "removed on exit. Never a committed path."
        ),
    )
    parser.add_argument(
        "--tolerance-m", type=float, default=DEFAULT_TOLERANCE_M,
        help=f"Coordinate match radius in metres (default: {DEFAULT_TOLERANCE_M:g})",
    )
    parser.add_argument(
        "--workers", type=int, default=1,
        help="Parallel worker processes (default: 1)",
    )
    parser.add_argument(
        "--json-out", type=Path,
        help="Write the full result list to this JSON file",
    )
    parser.add_argument(
        "--repo-root", type=Path, default=REPO_ROOT,
        help="Repository root (default: the parent of scripts/)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Debug logging",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the checker. Returns 0 unless a STALE union was found (then 1)."""
    args = build_cli_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(message)s",
    )
    repo_root = args.repo_root.resolve()

    manifest_rc = _run_manifest_checks(args, repo_root) if args.manifest else 0

    unions: list[str] = [_repo_relative(u, repo_root) for u in args.union]
    readers: dict[str, list[str]] = {}
    if args.all:
        readers = enumerate_registered_unions(repo_root)
        unions.extend(u for u in readers if u not in unions)
    if not unions:
        if args.manifest:
            return manifest_rc
        print(
            "Nothing to check: pass --union PATH, --manifest PATH or --all.",
            file=sys.stderr,
        )
        return 2

    tmp: Path | None = None
    if args.scratch_dir:
        scratch = args.scratch_dir.resolve()
        scratch.mkdir(parents=True, exist_ok=True)
    else:
        tmp = Path(tempfile.mkdtemp(prefix="union-check-"))
        scratch = tmp

    try:
        jobs = [(u, str(scratch), args.tolerance_m, str(repo_root)) for u in sorted(unions)]
        results: list[dict[str, Any]] = []
        if args.workers > 1:
            with ProcessPoolExecutor(max_workers=args.workers) as pool:
                futures = {pool.submit(_run_one, job): job[0] for job in jobs}
                for fut in as_completed(futures):
                    results.append(fut.result())
                    print(f"[{len(results)}/{len(jobs)}] {futures[fut]}", file=sys.stderr)
        else:
            for i, job in enumerate(jobs, 1):
                results.append(_run_one(job))
                print(f"[{i}/{len(jobs)}] {job[0]}", file=sys.stderr)
    finally:
        if tmp is not None:
            shutil.rmtree(tmp, ignore_errors=True)

    results.sort(key=lambda r: r["union_path"])
    for res in results:
        if readers:
            res["read_by"] = readers.get(res["union_path"], [])

    counts: dict[str, int] = {}
    for res in results:
        counts[res["classification"]] = counts.get(res["classification"], 0) + 1
    for cls in ("REPRODUCES", "SUBPOOL-CONSISTENT", "STALE", "UNRESOLVED"):
        if cls in counts:
            print(f"{cls:20s} {counts[cls]}")
    for res in results:
        if res["classification"] in ("STALE", "UNRESOLVED"):
            print(f"\n{res['classification']}: {res['union_path']}\n  {res['detail']}")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(
            {"script_version": __version__, "tolerance_m": args.tolerance_m,
             "counts": counts, "results": results}, indent=2,
        ))
        print(f"\nWrote {args.json_out}")

    return 1 if (counts.get("STALE") or manifest_rc) else 0


if __name__ == "__main__":
    sys.exit(main())
