#!/usr/bin/env python3
"""
Assessed-area provenance and the same-area check (PI ruling D51)
================================================================

Description:
    A candidate pool — the union of K proposer passes a verifier then scores,
    or a detection set materialised from it — can only find mounds in the
    area its passes were shown, minus anything an upstream step clipped away.
    Two pools meant to differ in ONE lever (a K-ladder's rungs, two cells of a
    contrast) are only comparable if that area is the same. On the Gemini 3.7
    gold-standard (GS) K-ladder it was not: the K = 5 and K = 10 unions had
    been clipped to the grid study's common footprint upstream, the K = 1 and
    K = 3 unions had not, and the lower rungs could reach 7 reference mounds
    in a 37.94 km² band the upper rungs could not
    (``reports/k-ladder-frames-2026-10-07.md`` § 4). Nothing in any union file
    recorded the clip, so the difference was invisible until a frames check
    stumbled on it.

    The PI's ruling D51 (``planning/pi-decisions-2026-09-20.md``): compare
    rungs on the area every rung searched, and "build in confirmation that the
    areas assessed are the same". This module is that confirmation:

    1. :func:`determine_assessed_area` derives the area a pool assessed from
       its PROVENANCE — an assessed-area record its builder wrote, a declared
       record for a legacy pool, or the pass provenance its consensus step
       recorded (each pass's ``processed_tiles`` on its tiling's polygons).
       If none of these exists it returns an *undetermined* area with the
       reason, never a guess.
    2. :func:`compare_assessed_areas` checks a set of pools against each
       other, within a stated tolerance, on the scoring frame. It REFUSES
       (:class:`AssessedAreaMismatchError`) when they differ, unless the
       caller asks to clip to the common area, in which case the result names
       the clip and the area each pool loses. An undetermined pool raises
       :class:`AssessedAreaUndeterminedError` unless the caller explicitly
       allows it, and even then the result's status says so.
    3. :func:`write_area_record` is what union builders call so that future
       pools are determinable: it records the footprint (tiling polygons and
       the tile manifest), the clip geometry and the passes, beside the union.

    **Effective area.** Scores are computed on a frame, so the comparison is
    made on each pool's assessed area intersected with the frame's tile union
    (the area that can contribute to a score). The raw assessed areas are
    reported beside it.

    **Tolerance.** :data:`DEFAULT_TOLERANCE_KM2` (0.01 km², a 100 m square) is
    far below the area of one tile's unshared part, so a single pass that
    skipped one tile is reported, and far above floating-point noise on
    polygon unions. A pool "matches" when its effective area exceeds the area
    common to all pools by no more than the tolerance; because the common
    area is the intersection, this catches two areas of equal size in
    different places as well as two of different size.

Usage::

    from scripts.lib_assessed_area import (
        compare_assessed_areas, determine_assessed_area,
    )
    areas = [determine_assessed_area(p, label=f"K = {k}") for k, p in pools]
    comparison = compare_assessed_areas(areas, frame=board_bounds)

    # Or from the shell (exit 0 same / clipped, 3 mismatch, 4 undetermined):
    python scripts/check_assessed_areas.py --frame BOUNDS --pool K1=PATH ...

Created: 2026-10-07 (Session 163)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import functools
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely.geometry.base import BaseGeometry

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.lib_advanced_metrics import read_processed_tiles  # noqa: E402

logger = logging.getLogger(__name__)

#: Projected CRS every area here is measured in (UTM zone 35N, metres).
AREA_CRS = "EPSG:32635"

#: Default tolerance in km²: how far a pool's effective assessed area may
#: exceed the area common to every pool and still count as the same.
DEFAULT_TOLERANCE_KM2 = 0.01

#: Schema tag of an assessed-area record.
RECORD_SCHEMA = "assessed-area/1"

#: Suffix of the record a builder writes beside a union
#: (``union_k5.geojson`` -> ``union_k5.assessed-area.json``).
RECORD_SUFFIX = ".assessed-area.json"

#: Records declared after the fact for legacy pools whose builders wrote
#: none. Each entry carries the evidence it was reconstructed from.
DECLARATIONS_PATH = BASE_DIR / "inputs" / "provenance" / "assessed-area-declarations.json"

#: Tilings whose tile polygons are known, keyed by the tile manifest a pass's
#: meta records (``configuration.full_config_snapshot.manifest_path``). Each
#: mapping is verified at use: the polygon file's tile names must equal the
#: manifest's exactly, or the area is undetermined.
KNOWN_TILINGS: dict[str, str] = {
    "inputs/tiles_384/full_evaluation_manifest.json":
        "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
    "inputs/grid-2026-08-18/grid_384_ov048_manifest.json":
        "outputs/grid-2026-08-18/scoring/bounds/grid_g384_ov048_bounds.geojson",
    "inputs/grid-2026-08-18/grid_384_ov192_manifest.json":
        "outputs/grid-2026-08-18/scoring/bounds/grid_g384_ov192_bounds.geojson",
    "inputs/grid-2026-08-18/grid_512_ov064_manifest.json":
        "outputs/grid-2026-08-18/scoring/bounds/grid_g512_ov064_bounds.geojson",
    "inputs/grid-2026-08-18/grid_512_ov256_manifest.json":
        "outputs/grid-2026-08-18/scoring/bounds/grid_g512_ov256_bounds.geojson",
}

#: How a pool's area was determined.
METHOD_RECORD = "record"
METHOD_DECLARED = "declared"
METHOD_PASS_PROVENANCE = "pass-provenance"
METHOD_UNDETERMINED = "undetermined"

#: Comparison outcomes.
STATUS_SAME = "same"
STATUS_CLIPPED = "clipped-to-common-area"
STATUS_UNDETERMINED = "undetermined"

#: The name a clip to the common area carries in every output.
COMMON_AREA_CLIP_NAME = "clip-to-common-assessed-area"


class AssessedAreaError(ValueError):
    """Base class: the assessed-area check refused."""


class AssessedAreaUndeterminedError(AssessedAreaError):
    """At least one pool's assessed area cannot be determined from provenance."""


class AssessedAreaMismatchError(AssessedAreaError):
    """The pools' assessed areas differ by more than the tolerance."""

    def __init__(self, message: str, comparison: dict[str, Any]) -> None:
        super().__init__(message)
        self.comparison = comparison


@dataclass
class AssessedArea:
    """The area one candidate pool assessed, and how that was established.

    Attributes:
        label: The caller's name for the pool (e.g. ``"K = 5"``).
        source: The path the caller gave (crop manifest, directory or union).
        union: The union / detection GeoJSON the area was determined for.
        geometry: The assessed area in :data:`AREA_CRS`, or ``None`` when
            undetermined.
        method: One of the ``METHOD_*`` constants.
        clip: The upstream clip the pool's builder applied, if any:
            ``{"name", "bounds"}``.
        evidence: Human-readable provenance trail (files read, checks made).
        warnings: Provenance anomalies that did not prevent a determination
            but a reader should see (e.g. a union rebuilt after its crops).
        reason: Why the area is undetermined (``None`` when determined).
    """

    label: str
    source: str
    union: str | None
    geometry: BaseGeometry | None
    method: str
    clip: dict[str, Any] | None = None
    evidence: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    reason: str | None = None

    @property
    def determined(self) -> bool:
        """Whether the area could be established from provenance."""
        return self.geometry is not None

    @property
    def area_km2(self) -> float | None:
        """The assessed area in km² (``None`` when undetermined)."""
        return None if self.geometry is None else self.geometry.area / 1e6

    def to_record(self) -> dict[str, Any]:
        """A JSON-serialisable summary (geometry omitted)."""
        return {
            "label": self.label,
            "source": self.source,
            "union": self.union,
            "method": self.method,
            "area_km2": _round(self.area_km2),
            "clip": self.clip,
            "evidence": self.evidence,
            "warnings": self.warnings,
            "reason": self.reason,
        }


def _round(value: float | None, digits: int = 4) -> float | None:
    """Round a number for the record, keeping ``None``."""
    return None if value is None else round(float(value), digits)


def _rel(path: Path | str) -> str:
    """Repository-relative path when possible, else the path as given.

    A relative path is taken to be repository-relative already (never
    resolved against the working directory).
    """
    path = Path(path)
    if not path.is_absolute():
        return str(path)
    try:
        return str(path.resolve().relative_to(BASE_DIR))
    except ValueError:
        return str(path)


def _abs(path: str | Path) -> Path:
    """Resolve a repository-relative (or frozen-snapshot) path to a real one."""
    text = str(path)
    if "/frozen/" in text:
        text = text.split("/frozen/", 1)[1]
    candidate = Path(text)
    return candidate if candidate.is_absolute() else BASE_DIR / candidate


@functools.lru_cache(maxsize=64)
def _read_bounds(path: str) -> gpd.GeoDataFrame:
    """Read a tile-polygon GeoJSON once, in :data:`AREA_CRS`.

    Raises:
        AssessedAreaUndeterminedError: If the file does not exist, so a
            missing polygon file reads as an undetermined area, not a crash.
    """
    if not _abs(path).exists():
        raise AssessedAreaUndeterminedError(f"polygon file missing: {path}")
    gdf = gpd.read_file(_abs(path))
    if gdf.crs is None:
        gdf = gdf.set_crs(AREA_CRS)
    elif gdf.crs.to_epsg() != 32635:
        gdf = gdf.to_crs(AREA_CRS)
    return gdf


def _union_of(gdf: gpd.GeoDataFrame) -> BaseGeometry:
    """The union of a GeoDataFrame's geometries."""
    return gdf.geometry.union_all()


def _manifest_names(path: str | Path) -> set[str]:
    """Tile names in a tile manifest (a JSON list, or ``tiles``/``tile_names``)."""
    payload = json.loads(_abs(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("tiles") or payload.get("tile_names") or []
    return {str(name) for name in payload}


@functools.lru_cache(maxsize=64)
def _verified_tiling(manifest: str) -> tuple[gpd.GeoDataFrame, frozenset[str]]:
    """A registered tiling's polygons, checked to hold exactly its manifest's tiles."""
    bounds = KNOWN_TILINGS[manifest]
    gdf = _read_bounds(bounds)
    names = frozenset(gdf["tile_name"].astype(str))
    expected = _manifest_names(manifest)
    if names != expected:
        raise AssessedAreaUndeterminedError(
            f"the polygon file {bounds} does not hold exactly the tiles of "
            f"{manifest} ({len(names)} vs {len(expected)} names, "
            f"{len(expected - names)} missing)"
        )
    return gdf, names


def tiling_polygons(manifest: str) -> tuple[gpd.GeoDataFrame, str]:
    """The tile polygons for the tiles of one pass's manifest.

    A full pass records its tiling's own manifest (a key of
    :data:`KNOWN_TILINGS`, verified tile for tile against its polygon file).
    A recovery fragment records a manifest of just the tiles it re-ran; it
    resolves to the registered tiling whose tiles include every one of them.
    If several registered tilings include them all, they must give those
    tiles the same polygons, or the area is undetermined.

    Args:
        manifest: Repository-relative manifest path as a pass's meta
            records it.

    Returns:
        ``(polygons, description)``: the polygons of the manifest's tiles,
        and where they came from.

    Raises:
        AssessedAreaUndeterminedError: If no registered tiling holds every
            tile of the manifest, the match is ambiguous, or a registered
            tiling's polygon file disagrees with its own manifest.
    """
    if manifest in KNOWN_TILINGS:
        gdf, _names = _verified_tiling(manifest)
        return gdf, KNOWN_TILINGS[manifest]
    if not _abs(manifest).exists():
        raise AssessedAreaUndeterminedError(f"tile manifest missing: {manifest}")
    wanted = _manifest_names(manifest)
    matches = []
    for key in KNOWN_TILINGS:
        if not _abs(KNOWN_TILINGS[key]).exists() or not _abs(key).exists():
            continue  # a registered tiling absent from this checkout cannot match
        gdf, names = _verified_tiling(key)
        if wanted <= names:
            matches.append((key, gdf[gdf["tile_name"].astype(str).isin(wanted)]))
    if not matches:
        raise AssessedAreaUndeterminedError(
            f"no registered tiling (lib_assessed_area.KNOWN_TILINGS) holds every "
            f"tile of {manifest} ({len(wanted)} tiles); register its polygons"
        )
    first_key, first = matches[0]
    first_area = _union_of(first).area
    for key, other in matches[1:]:
        if abs(_union_of(other).area - first_area) > 1.0:
            raise AssessedAreaUndeterminedError(
                f"the tiles of {manifest} occur in two registered tilings with "
                f"different polygons ({first_key}, {key})"
            )
    return first, f"{KNOWN_TILINGS[first_key]} (subset manifest of {first_key})"


def pass_manifest(pass_path: Path) -> str | None:
    """The tile manifest a proposer pass ran on, from its sibling meta file.

    Args:
        pass_path: A per-pass detection GeoJSON written by the detector.

    Returns:
        The manifest path as the meta records it, or ``None``.
    """
    meta = pass_path.with_name(pass_path.name.replace(".geojson", ".meta.json"))
    if not meta.exists():
        return None
    try:
        payload = json.loads(meta.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    snapshot = (payload.get("configuration") or {}).get("full_config_snapshot") or {}
    manifest = snapshot.get("manifest_path")
    return str(manifest) if manifest else None


def area_from_passes(pass_paths: list[str]) -> tuple[BaseGeometry, list[str]]:
    """The union of the tiles a set of proposer passes processed.

    Each pass's own ``processed_tiles`` record (written by the detector) is
    read, its tiling is resolved from its meta's manifest, and the processed
    tiles' polygons are unioned across every pass (recovery fragments
    included, as the consensus step's pass provenance lists them).

    Args:
        pass_paths: Repository-relative pass GeoJSON paths.

    Returns:
        ``(geometry, evidence)``.

    Raises:
        AssessedAreaUndeterminedError: If any pass is missing, carries no
            ``processed_tiles``, records no manifest, or names a tile its
            tiling's polygons do not hold.
    """
    if not pass_paths:
        raise AssessedAreaUndeterminedError("the pool lists no passes")
    pieces: list[BaseGeometry] = []
    evidence: list[str] = []
    for rel in pass_paths:
        path = _abs(rel)
        if not path.exists():
            raise AssessedAreaUndeterminedError(f"pass file missing: {rel}")
        processed = read_processed_tiles(path)
        if processed is None:
            raise AssessedAreaUndeterminedError(
                f"pass {rel} carries no processed_tiles record"
            )
        manifest = pass_manifest(path)
        if manifest is None:
            raise AssessedAreaUndeterminedError(
                f"pass {rel} has no meta file recording its tile manifest"
            )
        polygons, bounds = tiling_polygons(manifest)
        chosen = polygons[polygons["tile_name"].astype(str).isin(processed)]
        if not processed <= set(_manifest_names(manifest)):
            raise AssessedAreaUndeterminedError(
                f"pass {rel} processed tile(s) outside its own manifest {manifest}"
            )
        unknown = processed - set(chosen["tile_name"].astype(str))
        if unknown:
            raise AssessedAreaUndeterminedError(
                f"pass {rel} processed {len(unknown)} tile(s) its tiling "
                f"{manifest} does not hold"
            )
        pieces.append(_union_of(chosen))
        evidence.append(
            f"{rel}: {len(processed)} processed tile(s) on {manifest} "
            f"(polygons {bounds})"
        )
    geometry = gpd.GeoSeries(pieces, crs=AREA_CRS).union_all()
    return geometry, evidence


def area_from_record(record: dict[str, Any]) -> tuple[BaseGeometry, dict | None, list[str]]:
    """The area an assessed-area record defines.

    A record's ``footprint`` names a tile-polygon file (``bounds``) and,
    optionally, the ``manifest`` whose tiles were assessed (all of the file's
    tiles when absent); its ``clip`` names the upstream clip geometry, if any.
    The area is the footprint's union intersected with the clip's union.

    Args:
        record: A parsed record (:data:`RECORD_SCHEMA`).

    Returns:
        ``(geometry, clip, evidence)``.

    Raises:
        AssessedAreaUndeterminedError: If the record is malformed or a file
            it names is missing or inconsistent.
    """
    if record.get("schema") != RECORD_SCHEMA:
        raise AssessedAreaUndeterminedError(
            f"record schema {record.get('schema')!r} is not {RECORD_SCHEMA!r}"
        )
    footprint = record.get("footprint") or {}
    bounds = footprint.get("bounds")
    if not bounds or not _abs(bounds).exists():
        raise AssessedAreaUndeterminedError(
            f"record footprint bounds missing: {bounds!r}"
        )
    polygons = _read_bounds(bounds)
    manifest = footprint.get("manifest")
    evidence = [f"footprint polygons {bounds}"]
    if manifest:
        names = _manifest_names(manifest)
        chosen = polygons[polygons["tile_name"].astype(str).isin(names)]
        if len(chosen) != len(names):
            raise AssessedAreaUndeterminedError(
                f"footprint manifest {manifest} names {len(names)} tiles, "
                f"{len(chosen)} of them in {bounds}"
            )
        polygons = chosen
        evidence.append(f"footprint tiles from {manifest} ({len(names)})")
    geometry = _union_of(polygons)
    clip = record.get("clip")
    if clip:
        clip_bounds = clip.get("bounds")
        if not clip_bounds or not _abs(clip_bounds).exists():
            raise AssessedAreaUndeterminedError(
                f"record clip bounds missing: {clip_bounds!r}"
            )
        clip_geom = _union_of(_read_bounds(clip_bounds))
        before = geometry.area
        geometry = geometry.intersection(clip_geom)
        evidence.append(
            f"clipped to {clip.get('name')!r} ({clip_bounds}): "
            f"{(before - geometry.area) / 1e6:.3f} km² removed upstream"
        )
    return geometry, clip, evidence


@functools.lru_cache(maxsize=1)
def _declarations() -> dict[str, dict[str, Any]]:
    """The declared records, keyed by repository-relative union path."""
    if not DECLARATIONS_PATH.exists():
        return {}
    payload = json.loads(DECLARATIONS_PATH.read_text(encoding="utf-8"))
    return {entry["pool"]: entry for entry in payload.get("declarations", [])}


def record_path_for(union: Path) -> Path:
    """Where a builder's record for ``union`` lives (beside it)."""
    return union.with_name(union.name.replace(".geojson", "") + RECORD_SUFFIX)


def resolve_union(source: str | Path) -> tuple[Path, list[str]]:
    """Follow a crop manifest (or its directory) to the union it was cut from.

    Args:
        source: A crops directory, a ``candidate_manifest.json``, or a union /
            detection GeoJSON.

    Returns:
        ``(union_path, warnings)``. A warning is raised when the crop
        manifest's candidate count differs from the union's feature count —
        the union was rebuilt after the crops were cut, so the area reported
        is the rebuilt union's.

    Raises:
        AssessedAreaUndeterminedError: If a crop manifest names no union.
    """
    path = _abs(source)
    if path.is_dir():
        path = path / "candidate_manifest.json"
    warnings: list[str] = []
    if path.suffix == ".json" and path.name != "voting_summary.json":
        manifest = json.loads(path.read_text(encoding="utf-8"))
        union_ref = manifest.get("source_geojson")
        if not union_ref:
            raise AssessedAreaUndeterminedError(
                f"crop manifest {_rel(path)} names no source_geojson"
            )
        union = _abs(union_ref)
        n_crops = manifest.get("total_detections")
        if union.exists() and n_crops is not None:
            n_union = len(json.loads(union.read_text(encoding="utf-8")).get("features", []))
            if n_union != n_crops:
                warnings.append(
                    f"crop manifest {_rel(path)} holds {n_crops} candidates but "
                    f"its union {_rel(union)} now holds {n_union}: the union "
                    f"was rebuilt after the crops were cut, so this is the "
                    f"rebuilt union's area"
                )
        return union, warnings
    return path, warnings


def _check_candidates_inside(union: Path, area: AssessedArea) -> None:
    """Warn (on the area) if any of the union's candidates lie outside it.

    Every candidate of a pool was found inside the area its passes assessed,
    so a candidate outside the determined area means the provenance — above
    all a declared record — does not describe this pool. Tolerance: 1 m, for
    centroids of clusters straddling a tile edge.

    Args:
        union: The union / detection GeoJSON.
        area: The area just determined (mutated: evidence and warnings).
    """
    if area.geometry is None or not union.exists():
        return
    gdf = gpd.read_file(union)
    if gdf.empty:
        return
    gdf = gdf.set_crs("EPSG:4326") if gdf.crs is None else gdf
    points = gdf.to_crs(AREA_CRS).geometry
    outside = int((~points.intersects(area.geometry.buffer(1.0))).sum())
    area.evidence.append(
        f"consistency: {len(points) - outside} of {len(points)} union candidates "
        f"lie inside the determined area"
    )
    if outside:
        area.warnings.append(
            f"{outside} of {len(points)} candidates of {_rel(union)} lie OUTSIDE "
            f"the determined area: its provenance does not describe this pool"
        )


def determine_assessed_area(source: str | Path, *, label: str | None = None) -> AssessedArea:
    """Determine a pool's assessed area and check its candidates lie inside it.

    See :func:`_determine_assessed_area` for the provenance order; this
    wrapper adds the consistency check (:func:`_check_candidates_inside`).

    Args:
        source: A crops directory, crop manifest, or union GeoJSON.
        label: The caller's name for the pool (defaults to the path).

    Returns:
        An :class:`AssessedArea`.
    """
    area = _determine_assessed_area(source, label=label)
    if area.union is not None:
        _check_candidates_inside(_abs(area.union), area)
    for warning in area.warnings:
        logger.warning("assessed area of %s: %s", area.label, warning)
    return area


def _determine_assessed_area(source: str | Path, *, label: str | None = None) -> AssessedArea:
    """Determine the area a candidate pool assessed, from its provenance only.

    Sources consulted, in order:

    1. **A builder's record** beside the union (:func:`record_path_for`),
       written by :func:`write_area_record`.
    2. **A declared record** for a legacy pool in :data:`DECLARATIONS_PATH`,
       reconstructed after the fact with its evidence cited.
    3. **The consensus step's pass provenance** (``voting_summary.json``
       beside the union, ``pass_provenance``): the union of every pass's
       processed tiles. ``merge_passes.py`` applies no clip, so none is
       added.

    Anything else — a union with no record and no pass provenance — is
    UNDETERMINED, with the reason. The function never infers an area from a
    directory layout or a naming convention.

    Args:
        source: A crops directory, crop manifest, or union GeoJSON.
        label: The caller's name for the pool (defaults to the path).

    Returns:
        An :class:`AssessedArea`.
    """
    label = label or str(source)
    try:
        union, warnings = resolve_union(source)
    except (AssessedAreaUndeterminedError, OSError, json.JSONDecodeError) as exc:
        return AssessedArea(label, str(source), None, None, METHOD_UNDETERMINED,
                            reason=str(exc))
    union_rel = _rel(union)
    base = {"label": label, "source": str(source), "union": union_rel,
            "warnings": warnings}

    record_file = record_path_for(union)
    try:
        if record_file.exists():
            record = json.loads(record_file.read_text(encoding="utf-8"))
            geometry, clip, evidence = area_from_record(record)
            return AssessedArea(geometry=geometry, method=METHOD_RECORD, clip=clip,
                                evidence=[f"record {_rel(record_file)}", *evidence],
                                **base)
        declared = _declarations().get(union_rel)
        if declared is not None:
            geometry, clip, evidence = area_from_record(declared)
            return AssessedArea(
                geometry=geometry, method=METHOD_DECLARED, clip=clip,
                evidence=[f"declared in {_rel(DECLARATIONS_PATH)}", *evidence,
                          *[f"basis: {item}" for item in declared.get("evidence", [])]],
                **base,
            )
        summary = union.parent / "voting_summary.json"
        if summary.exists():
            provenance = json.loads(summary.read_text(encoding="utf-8")).get(
                "pass_provenance")
            if provenance:
                passes = [entry["path"] for entry in provenance]
                geometry, evidence = area_from_passes(passes)
                return AssessedArea(
                    geometry=geometry, method=METHOD_PASS_PROVENANCE, clip=None,
                    evidence=[f"pass provenance {_rel(summary)} ({len(passes)} file(s))",
                              *evidence,
                              "merge_passes applies no clip"],
                    **base,
                )
            reason = (f"{_rel(summary)} records no pass_provenance (a consensus "
                      f"written before pass provenance existed)")
        else:
            reason = "no assessed-area record, no declaration, and no voting_summary.json"
    except AssessedAreaUndeterminedError as exc:
        reason = str(exc)
    return AssessedArea(geometry=None, method=METHOD_UNDETERMINED, reason=reason, **base)


def write_area_record(
    union: Path,
    *,
    builder: str,
    footprint_bounds: str,
    footprint_manifest: str | None,
    clip_name: str | None,
    clip_bounds: str | None,
    passes: list[str],
    notes: str | None = None,
) -> Path:
    """Write the assessed-area record a union builder owes its union.

    Call this from any step that builds a candidate pool, so the pool's area
    is determinable by :func:`determine_assessed_area` without reading the
    builder's code. The record is checked by recomputing the area before it
    is written: a record that does not resolve is an error at build time,
    not at comparison time.

    Args:
        union: The union GeoJSON just written.
        builder: The script that built it.
        footprint_bounds: Tile-polygon file of the tiling the passes ran on.
        footprint_manifest: The tile manifest the passes covered (every tile
            of ``footprint_bounds`` when ``None``).
        clip_name: A name for the clip the builder applied, if any.
        clip_bounds: The clip's polygon file, if any.
        passes: The pass files the union was built from.
        notes: Optional free text.

    Returns:
        The record's path.
    """
    record: dict[str, Any] = {
        "schema": RECORD_SCHEMA,
        "pool": _rel(union),
        "builder": builder,
        "status": "recorded-at-build",
        "footprint": {"bounds": footprint_bounds, "manifest": footprint_manifest},
        "clip": ({"name": clip_name, "bounds": clip_bounds} if clip_bounds else None),
        "passes": passes,
    }
    if notes:
        record["notes"] = notes
    geometry, _clip, _evidence = area_from_record(record)
    record["area_km2"] = _round(geometry.area / 1e6)
    target = record_path_for(union)
    target.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    logger.info("assessed-area record %s: %.3f km²", _rel(target), geometry.area / 1e6)
    return target


def frame_union(frame: gpd.GeoDataFrame | str | Path) -> BaseGeometry:
    """The union of a scoring frame's tiles (accepts a path or a GeoDataFrame)."""
    if isinstance(frame, (str, Path)):
        return _union_of(_read_bounds(_rel(frame)))
    gdf = frame if frame.crs is None or frame.crs.to_epsg() == 32635 else frame.to_crs(AREA_CRS)
    return _union_of(gdf)


@dataclass
class AreaComparison:
    """The outcome of :func:`compare_assessed_areas`.

    Attributes:
        status: :data:`STATUS_SAME`, :data:`STATUS_CLIPPED` or
            :data:`STATUS_UNDETERMINED`.
        common: The area common to every determined pool (effective, i.e.
            within the frame when one was given), or ``None``.
        record: The JSON-serialisable record a caller writes into its output.
    """

    status: str
    common: BaseGeometry | None
    record: dict[str, Any]


def compare_assessed_areas(
    areas: list[AssessedArea],
    *,
    frame: gpd.GeoDataFrame | str | Path | None = None,
    tolerance_km2: float = DEFAULT_TOLERANCE_KM2,
    clip_to_common: bool = False,
    allow_undetermined: bool = False,
) -> AreaComparison:
    """Confirm that pools meant to differ in one lever assessed the same area.

    Args:
        areas: One :class:`AssessedArea` per pool (rung, cell).
        frame: The scoring frame; each area is intersected with its tile
            union before comparison. ``None`` compares the raw areas.
        tolerance_km2: The largest excess (km²) of any pool's area over the
            area common to all pools that still counts as the same.
        clip_to_common: When the areas differ, return a clip to the common
            area (status :data:`STATUS_CLIPPED`, the clip named and the area
            each pool loses recorded) instead of refusing.
        allow_undetermined: Return (status :data:`STATUS_UNDETERMINED`)
            instead of raising when a pool's area is undetermined. The
            determined pools are still compared and still refused on a
            mismatch.

    Returns:
        An :class:`AreaComparison`.

    Raises:
        AssessedAreaUndeterminedError: If a pool's area is undetermined and
            ``allow_undetermined`` is false.
        AssessedAreaMismatchError: If the determined areas differ by more
            than the tolerance and ``clip_to_common`` is false.
    """
    undetermined = [a for a in areas if not a.determined]
    if undetermined and not allow_undetermined:
        lines = "; ".join(f"{a.label}: {a.reason}" for a in undetermined)
        raise AssessedAreaUndeterminedError(
            f"ASSESSED AREA UNDETERMINED for {len(undetermined)} of {len(areas)} "
            f"pool(s) — the comparison cannot confirm the pools searched the "
            f"same area (PI ruling D51). {lines}"
        )
    frame_geom = frame_union(frame) if frame is not None else None
    determined = [a for a in areas if a.determined]
    effective = {
        a.label: (a.geometry.intersection(frame_geom) if frame_geom is not None
                  else a.geometry)
        for a in determined
    }
    common: BaseGeometry | None = None
    for geometry in effective.values():
        common = geometry if common is None else common.intersection(geometry)
    common_km2 = None if common is None else common.area / 1e6
    pools = []
    worst = 0.0
    for a in areas:
        entry = a.to_record()
        if a.determined:
            eff_km2 = effective[a.label].area / 1e6
            excess = eff_km2 - (common_km2 or 0.0)
            worst = max(worst, excess)
            entry.update({"effective_area_km2": _round(eff_km2),
                          "excess_over_common_km2": _round(excess)})
        pools.append(entry)
    record: dict[str, Any] = {
        "check": "assessed-area/1 (PI ruling D51)",
        "frame": (None if frame is None else
                  (_rel(frame) if isinstance(frame, (str, Path)) else "<GeoDataFrame>")),
        "frame_area_km2": _round(None if frame_geom is None else frame_geom.area / 1e6),
        "tolerance_km2": tolerance_km2,
        "common_area_km2": _round(common_km2),
        "max_excess_km2": _round(worst),
        "pools": pools,
    }
    mismatch = worst > tolerance_km2
    if mismatch and not clip_to_common:
        record["status"] = "refused"
        table = ", ".join(
            f"{p['label']} {p.get('effective_area_km2')} km² "
            f"(+{p.get('excess_over_common_km2')})"
            for p in pools if p.get("effective_area_km2") is not None
        )
        raise AssessedAreaMismatchError(
            f"ASSESSED AREAS DIFFER (PI ruling D51): the pools did not search "
            f"the same area — common {_round(common_km2)} km², excess up to "
            f"{_round(worst)} km² against a tolerance of {tolerance_km2} km² "
            f"[{table}]. Refusing to compare them; re-run with a clip to the "
            f"common area to compare on the area every pool searched.",
            record,
        )
    if undetermined:
        status = STATUS_UNDETERMINED
        record["undetermined"] = [a.label for a in undetermined]
        logger.error(
            "ASSESSED AREA UNDETERMINED for %s — allowed by the caller, recorded "
            "as undetermined, NOT as the same area",
            ", ".join(a.label for a in undetermined),
        )
    elif mismatch:
        status = STATUS_CLIPPED
        record["clip"] = {
            "name": COMMON_AREA_CLIP_NAME,
            "common_area_km2": _round(common_km2),
            "area_removed_km2": {p["label"]: p["excess_over_common_km2"] for p in pools},
        }
        logger.warning(
            "assessed areas differ by up to %.3f km²: clipping every pool to "
            "the common %.3f km² (%s)", worst, common_km2, COMMON_AREA_CLIP_NAME,
        )
    else:
        status = STATUS_SAME
    record["status"] = status
    return AreaComparison(status=status, common=common, record=record)


def clip_points_to_area(
    gdf: gpd.GeoDataFrame, area: BaseGeometry,
) -> tuple[gpd.GeoDataFrame, int]:
    """Keep the points that intersect ``area`` (the clip D51 option 1 applies).

    Args:
        gdf: Candidates or detections (projected to :data:`AREA_CRS` here if
            they are in another CRS; the returned rows keep their own CRS).
        area: The common assessed area.

    Returns:
        ``(kept_rows, n_removed)``.
    """
    if gdf.empty:
        return gdf, 0
    projected = gdf if gdf.crs is not None and gdf.crs.to_epsg() == 32635 else (
        gdf.to_crs(AREA_CRS) if gdf.crs is not None else gdf.set_crs(AREA_CRS))
    keep = projected.geometry.intersects(area).to_numpy()
    return gdf[keep], int((~keep).sum())


def write_area_geojson(area: BaseGeometry, path: Path, *, name: str) -> Path:
    """Write a common area as a one-feature GeoJSON a sweep can read back.

    Args:
        area: The geometry.
        path: Target path.
        name: The clip's name, stored as the feature's ``name``.

    Returns:
        ``path``.
    """
    gdf = gpd.GeoDataFrame({"name": [name], "area_km2": [area.area / 1e6]},
                           geometry=[area], crs=AREA_CRS)
    path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(path, driver="GeoJSON")
    return path


#: Exit codes every ladder driver uses when the gate refuses.
EXIT_AREA_MISMATCH = 3
EXIT_AREA_UNDETERMINED = 4


def add_area_gate_arguments(parser: Any) -> None:
    """Add the D51 gate's three options to a ladder driver's argument parser.

    Args:
        parser: An :class:`argparse.ArgumentParser` (or sub-parser).
    """
    parser.add_argument(
        "--area-tolerance-km2", type=float, default=DEFAULT_TOLERANCE_KM2,
        help="D51: largest excess of a rung's assessed area over the area "
             "common to all rungs that still counts as the same "
             f"(default {DEFAULT_TOLERANCE_KM2})")
    parser.add_argument(
        "--clip-to-common-area", action="store_true",
        help="D51: when the rungs' assessed areas differ, clip every rung to "
             "the common area (named in the output) instead of refusing")
    parser.add_argument(
        "--allow-undetermined-area", action="store_true",
        help="D51: record a rung whose assessed area cannot be determined "
             "from provenance as undetermined instead of refusing")


def run_area_gate(
    pools: dict[str, str],
    *,
    frame: str | Path,
    tolerance_km2: float = DEFAULT_TOLERANCE_KM2,
    clip_to_common: bool = False,
    allow_undetermined: bool = False,
    clip_geojson: Path | None = None,
    what: str = "ladder",
) -> AreaComparison:
    """Determine and compare a set of rungs' areas; exit loudly on refusal.

    The one call a ladder driver makes before it sweeps or assembles rungs.
    On a mismatch (without ``clip_to_common``) or an undetermined area
    (without ``allow_undetermined``) it logs the refusal and exits with
    :data:`EXIT_AREA_MISMATCH` / :data:`EXIT_AREA_UNDETERMINED`; a driver
    must not continue to compare rungs the gate refused. When it clips and
    ``clip_geojson`` is given, the common area is written there for
    ``sweep_f1_greedy_pv.py --clip-area``.

    Args:
        pools: ``{rung label: crops dir / crop manifest / union path}``.
        frame: The scoring frame's bounds file.
        tolerance_km2: See :func:`compare_assessed_areas`.
        clip_to_common: See :func:`compare_assessed_areas`.
        allow_undetermined: See :func:`compare_assessed_areas`.
        clip_geojson: Where to write the common area when clipping.
        what: What is being gated, for the log line.

    Returns:
        The :class:`AreaComparison` (its ``record`` gains ``clip_geojson``
        when the area was written).
    """
    areas = [determine_assessed_area(path, label=label) for label, path in pools.items()]
    try:
        comparison = compare_assessed_areas(
            areas, frame=frame, tolerance_km2=tolerance_km2,
            clip_to_common=clip_to_common, allow_undetermined=allow_undetermined,
        )
    except AssessedAreaUndeterminedError as exc:
        logger.error("D51 gate REFUSED %s: %s", what, exc)
        raise SystemExit(EXIT_AREA_UNDETERMINED) from exc
    except AssessedAreaMismatchError as exc:
        logger.error("D51 gate REFUSED %s: %s", what, exc)
        raise SystemExit(EXIT_AREA_MISMATCH) from exc
    if comparison.status == STATUS_CLIPPED and clip_geojson is not None:
        write_area_geojson(comparison.common, clip_geojson, name=COMMON_AREA_CLIP_NAME)
        comparison.record["clip_geojson"] = _rel(clip_geojson)
    logger.info("D51 gate %s: %s (common %s km², max excess %s km²)", what,
                comparison.status, comparison.record["common_area_km2"],
                comparison.record["max_excess_km2"])
    return comparison


def clip_geojson_file(path: Path, area: BaseGeometry, *, name: str) -> int:
    """Clip a materialised detection GeoJSON to an area, in place.

    Args:
        path: The GeoJSON (rewritten; its CRS kept).
        area: The common assessed area (:data:`AREA_CRS`).
        name: The clip's name, logged.

    Returns:
        The number of features removed.
    """
    gdf = gpd.read_file(path)
    kept, removed = clip_points_to_area(gdf, area)
    if removed:
        kept.to_file(path, driver="GeoJSON")
    logger.info("  %s: %s removed %d feature(s), kept %d", _rel(path), name, removed,
                len(kept))
    return removed


def rescore_clipped_evaluation(
    eval_path: str | Path, area: BaseGeometry, *, buffer_m: int = 20,
) -> dict[str, Any] | None:
    """Point F1 of an evaluated cell with its detections clipped to an area.

    Reads the cell's own recorded inputs (detections, frame, references),
    loads them as ``evaluate_detections.py`` does (``source_tile`` synthesised
    by a spatial join when absent), drops detections outside ``area``, and
    scores with the project scorer. The reference set is the frame's, kept
    whole — option 1 of the D51 ruling ("clip the larger-area rungs to the
    area common to all rungs, keep the frame's reference set"). A multi-pass
    cell is the mean over its passes, as the evaluator reports it.

    Args:
        eval_path: The cell's ``evaluation.json``.
        area: The common assessed area.
        buffer_m: Match radius.

    Returns:
        ``{"f1", "precision", "recall", "n_detections", "n_removed",
        "buffer_m"}``, or ``None`` if the evaluation names no inputs.
    """
    from scripts.lib_advanced_metrics import calculate_f1_internal  # noqa: PLC0415

    payload = json.loads(_abs(eval_path).read_text(encoding="utf-8"))
    meta = payload.get("_metadata") or {}
    inputs = meta.get("input_files") or {}
    cli = meta.get("cli_args") or {}
    detections = inputs.get("detections") or cli.get("detections")
    bounds = inputs.get("bounds") or cli.get("bounds")
    reference = inputs.get("ground_truth") or cli.get("ground_truth")
    if not detections or not bounds or not reference:
        return None
    files = detections if isinstance(detections, list) else [detections]
    gdf_bounds = _read_bounds(_rel(_abs(bounds)))
    gdf_ref = gpd.read_file(_abs(reference))
    gdf_ref = gdf_ref.set_crs(AREA_CRS) if gdf_ref.crs is None else gdf_ref.to_crs(AREA_CRS)
    scores = []
    for item in files:
        gdf = gpd.read_file(_abs(item))
        gdf = gdf.set_crs(AREA_CRS) if gdf.crs is None else gdf.to_crs(AREA_CRS)
        if "source_tile" not in gdf.columns and not gdf.empty:
            joined = gpd.sjoin(gdf, gdf_bounds[["tile_name", "geometry"]],
                               how="left", predicate="intersects")
            joined = joined[~joined.index.duplicated(keep="first")]
            gdf["source_tile"] = joined["tile_name"]
        kept, removed = clip_points_to_area(gdf, area)
        if kept.empty:
            p = r = f = 0.0
        else:
            p, r, f = calculate_f1_internal(kept, gdf_ref, gdf_bounds, buffer_metres=buffer_m)
        scores.append((p, r, f, len(kept), removed))
    n = len(scores)
    return {
        "f1": round(sum(s[2] for s in scores) / n, 4),
        "precision": round(sum(s[0] for s in scores) / n, 4),
        "recall": round(sum(s[1] for s in scores) / n, 4),
        "n_detections": int(sum(s[3] for s in scores)),
        "n_removed": int(sum(s[4] for s in scores)),
        "buffer_m": buffer_m,
    }


def read_area_geojson(path: str | Path) -> tuple[BaseGeometry, str]:
    """Read a clip area written by :func:`write_area_geojson`.

    Returns:
        ``(geometry, name)``.
    """
    gdf = gpd.read_file(_abs(path))
    gdf = gdf.set_crs(AREA_CRS) if gdf.crs is None else gdf.to_crs(AREA_CRS)
    name = str(gdf["name"].iloc[0]) if "name" in gdf.columns else Path(path).stem
    return _union_of(gdf), name
