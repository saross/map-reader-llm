#!/usr/bin/env python3
"""
Carry committed verifier probabilities onto a rebuilt union's candidate ids
==========================================================================

Description:
    A rebuilt consensus union re-numbers its candidates, so a committed
    ``probabilities.json`` keyed to the OLD numbering cannot be read against
    the NEW ``candidate_manifest.json``. This script re-keys the committed
    results onto the new numbering by matching candidate positions, and
    reports which new candidates the committed stage does not cover — which
    is exactly the set a subsequent verifier run must pay for.

    Matching uses the manifests' own ``centroid_x`` / ``centroid_y``, which
    are already projected (EPSG:32635, metres), so no reprojection is
    involved. Matching is greedy nearest-neighbour under ``--tolerance``,
    one-to-one, over a uniform grid of buckets so the search is local.

    **Coverage is decided on the integer pixel window, not on metric
    distance.** That is the lesson this script was promoted to ``scripts/``
    for (``reports/recovery-drop-fix-2026-09-13.md`` § 6.1). It re-derives,
    for every matched pair, the whole-pixel window that
    ``extract_candidates._crop_from_raster`` would cut —
    ``rasterio.DatasetReader.index`` floors the projected centroid to a whole
    (row, col) — so the claim "the carried probability is valid because the
    crop did not change" is measured rather than asserted. At the ~5.02 m/px
    ground resolution of these sheets a sub-metre centroid shift is a
    sub-pixel shift and usually lands in a byte-identical window. Testing
    coverage on a 2 m positional tolerance instead cost one confirmatory
    API call on 2026-09-13: the candidate's centroid had moved 3.026 m, its
    crop window was ``(3177, 3192)`` before and after, and the verifier
    returned the committed 0.95 because it was shown the same image.

    The seeded ``probabilities.json`` is written in the exact schema
    ``run_pv.py`` reads for its resume filter (``results`` keyed
    ``candidate_NNNNN``), so a subsequent ``run_pv.py verify`` over the new
    crops directory calls the API for the uncovered candidates ONLY. Check
    ``carry_provenance.json``'s ``uncovered`` count against the number of
    calls you expect to pay for BEFORE launching that run.

Usage::

    python scripts/carry_probabilities.py \\
        --old-manifest  <committed crops>/candidate_manifest.json \\
        --old-probs     <committed verify stage>/probabilities.json \\
        --new-manifest  <rebuilt crops>/candidate_manifest.json \\
        --out-dir       <new verify stage> \\
        --rasters-dir   inputs/rasters \\
        --label         k3

    # Coverage census only — writes nothing, prints the counts:
    python scripts/carry_probabilities.py ... --dry-run

Outputs:
    <out-dir>/probabilities.json  — seeded with the carried results
    <out-dir>/carry_provenance.json — which candidates were carried, which
        are uncovered, and the pixel-window comparison

History:
    Written on 2026-09-13 as
    ``results/k-ladder-2026-09-12/recovery-fix-2026-09-13/harness/carry_probabilities.py``
    for the recovery-fragment fix, and promoted here under checklist item 6a
    (``planning/documentation-foundation-checklist-2026-09-13.md``) because
    re-keying probabilities onto a new candidate numbering is a general need
    whenever a union is rebuilt. The matching and window logic are unchanged,
    so the committed ``carry_provenance.json`` files that job produced remain
    reproducible; the original is archived under
    ``archive/promoted-scripts/``.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import rasterio

#: A tile filename embeds its raster sheet name before the ``_x<N>_y<N>`` offset.
_TILE_RE = re.compile(r"^(?P<sheet>.+?)_x\d+_y\d+\.png$")

#: Half the crop edge in pixels, as ``extract_candidates`` cuts it.
DEFAULT_PADDING: int = 75

#: Positional match tolerance in metres. Deliberately loose: it decides only
#: which OLD candidate a NEW one is the same mound as, not whether the carried
#: probability is valid — that question is the pixel window's.
DEFAULT_TOLERANCE: float = 2.0

#: Resolves a candidate's integer crop window. ``(sheet, cx, cy)`` in, the
#: window's ``(col_off, row_off)`` out, or ``None`` when it cannot be
#: determined. Injectable so the matching logic is testable without rasters.
WindowResolver = Callable[[str | None, float, float], "tuple[int, int] | None"]


def sheet_of(source_tile: str | None) -> str | None:
    """Return the raster sheet name a tile filename belongs to.

    Args:
        source_tile: A tile filename such as
            ``K-35-052-4_32635_x2880_y3072.png``.

    Returns:
        The sheet stem (``K-35-052-4_32635``), or ``None`` if the name does
        not match the tiling convention.

    Examples:
        >>> sheet_of("K-35-052-4_32635_x2880_y3072.png")
        'K-35-052-4_32635'
        >>> sheet_of("not-a-tile.png") is None
        True
        >>> sheet_of(None) is None
        True
    """
    if not source_tile:
        return None
    match = _TILE_RE.match(source_tile)
    return match.group("sheet") if match else None


class RasterWindowResolver:
    """Resolve crop windows from the GeoTIFF sheets, caching open datasets.

    Mirrors ``scripts/extract_candidates._crop_from_raster``:
    ``DatasetReader.index`` floors the projected centroid to a whole
    ``(row, col)``, and the window is offset by ``padding`` from there. Two
    centroids less than a pixel apart therefore usually produce a
    byte-identical crop, which is the whole basis for carrying a probability
    rather than re-verifying it.

    Use as a context manager so the datasets are closed.

    Args:
        rasters_dir: Directory holding the GeoTIFF sheets, one
            ``<sheet>.tif`` per sheet.
        padding: Half the crop edge, in pixels.

    Example:
        >>> with RasterWindowResolver(Path("inputs/rasters")) as resolve:
        ...     resolve("K-35-052-4_32635", 400000.0, 4700000.0)  # doctest: +SKIP
        (3177, 3192)
    """

    def __init__(
        self, rasters_dir: Path, padding: int = DEFAULT_PADDING,
    ) -> None:
        self.rasters_dir = rasters_dir
        self.padding = padding
        self._cache: dict[str, Any] = {}

    def __call__(
        self, sheet: str | None, cx: float, cy: float,
    ) -> tuple[int, int] | None:
        """Return ``(col_off, row_off)``, or ``None`` if the sheet is absent."""
        if sheet is None:
            return None
        if sheet not in self._cache:
            path = self.rasters_dir / f"{sheet}.tif"
            self._cache[sheet] = (
                rasterio.open(path) if path.exists() else None
            )
        src = self._cache[sheet]
        if src is None:
            return None
        row, col = src.index(cx, cy)
        return (int(col) - self.padding, int(row) - self.padding)

    def __enter__(self) -> RasterWindowResolver:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        """Close every cached dataset."""
        for src in self._cache.values():
            if src is not None:
                src.close()
        self._cache.clear()


@dataclass
class CarryReport:
    """What one carry produced: the seeded results, and what they do not cover.

    Attributes:
        carried: ``{new candidate key: committed result}``, ready to write as
            a ``probabilities.json`` ``results`` block.
        carry_log: One entry per carried candidate — the old and new keys,
            the centroid displacement in metres, both integer crop windows,
            whether they are identical, and the carried probability.
        uncovered: One entry per NEW candidate with no carried result. This
            is the set a subsequent verifier run pays for.
    """

    carried: dict[str, dict] = field(default_factory=dict)
    carry_log: list[dict[str, Any]] = field(default_factory=list)
    uncovered: list[dict[str, Any]] = field(default_factory=list)

    @property
    def displaced(self) -> list[dict[str, Any]]:
        """Carried candidates whose centroid moved at all."""
        return [e for e in self.carry_log if e["distance_m"] > 1e-9]

    @property
    def window_changed(self) -> list[dict[str, Any]]:
        """Carried candidates whose integer crop window is NOT identical.

        These are the carries that need a judgement call: the probability was
        measured on a different image from the one the new candidate would be
        shown. A carry here is an assumption; a re-verification is a
        measurement.
        """
        return [e for e in self.carry_log if not e["window_identical"]]


def _candidate_key(candidate: dict[str, Any]) -> str:
    """Format a candidate's ``probabilities.json`` key.

    Args:
        candidate: A ``candidate_manifest.json`` entry.

    Returns:
        ``candidate_NNNNN``.

    Examples:
        >>> _candidate_key({"candidate_id": 49})
        'candidate_00049'
    """
    return f"candidate_{candidate['candidate_id']:05d}"


def _uncovered_entry(
    candidate: dict[str, Any], note: str | None = None,
) -> dict[str, Any]:
    """Describe one new candidate that no committed result covers.

    Args:
        candidate: The new ``candidate_manifest.json`` entry.
        note: Optional explanation, used when the candidate matched an old
            one positionally but that key carries no committed result.

    Returns:
        The uncovered record written into ``carry_provenance.json``.
    """
    entry = {
        "new_key": _candidate_key(candidate),
        "centroid_x": candidate["centroid_x"],
        "centroid_y": candidate["centroid_y"],
        "source_tile": candidate.get("source_tile"),
        "vote_count": candidate.get("properties", {}).get("vote_count"),
    }
    if note is not None:
        entry["note"] = note
    return entry


def carry_probabilities(
    old_candidates: list[dict[str, Any]],
    new_candidates: list[dict[str, Any]],
    old_results: dict[str, dict],
    *,
    tolerance: float = DEFAULT_TOLERANCE,
    window_resolver: WindowResolver | None = None,
) -> CarryReport:
    """Re-key committed results onto a rebuilt union's candidate numbering.

    Greedy nearest-neighbour, one-to-one, within ``tolerance`` metres. Old
    candidates are bucketed on a uniform grid of side ``max(tolerance, 1.0)``
    so each new candidate searches its own bucket and the eight around it;
    within that neighbourhood the nearest unclaimed old candidate wins. The
    result is deterministic for a given input order, which is what makes a
    committed ``carry_provenance.json`` reproducible.

    Args:
        old_candidates: ``candidates`` from the committed crops manifest.
        new_candidates: ``candidates`` from the rebuilt crops manifest.
        old_results: ``results`` from the committed ``probabilities.json``.
        tolerance: Positional match tolerance in metres.
        window_resolver: Resolves each candidate's integer crop window.
            ``None`` skips the window comparison, which records
            ``window_identical`` as ``True`` — acceptable only when the
            caller is not deciding coverage on it.

    Returns:
        A :class:`CarryReport`.

    Example:
        >>> old = [{"candidate_id": 1, "centroid_x": 0.0, "centroid_y": 0.0}]
        >>> new = [{"candidate_id": 7, "centroid_x": 0.5, "centroid_y": 0.0}]
        >>> report = carry_probabilities(
        ...     old, new, {"candidate_00001": {"mound_probability": 0.95}},
        ... )
        >>> report.carried["candidate_00007"]["mound_probability"]
        0.95
    """
    cell = max(tolerance, 1.0)
    buckets: dict[tuple[int, int], list[int]] = {}
    for index, candidate in enumerate(old_candidates):
        key = (
            int(candidate["centroid_x"] // cell),
            int(candidate["centroid_y"] // cell),
        )
        buckets.setdefault(key, []).append(index)

    report = CarryReport()
    taken: set[int] = set()

    for candidate in new_candidates:
        nx, ny = candidate["centroid_x"], candidate["centroid_y"]
        bx, by = int(nx // cell), int(ny // cell)
        best_index: int | None = None
        best_distance: float | None = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for index in buckets.get((bx + dx, by + dy), ()):
                    if index in taken:
                        continue
                    distance = math.hypot(
                        nx - old_candidates[index]["centroid_x"],
                        ny - old_candidates[index]["centroid_y"],
                    )
                    if distance <= tolerance and (
                        best_distance is None or distance < best_distance
                    ):
                        best_index, best_distance = index, distance

        if best_index is None:
            report.uncovered.append(_uncovered_entry(candidate))
            continue

        taken.add(best_index)
        old_candidate = old_candidates[best_index]
        old_key = _candidate_key(old_candidate)
        if old_key not in old_results:
            report.uncovered.append(_uncovered_entry(
                candidate,
                note=(
                    f"matched old {old_key} positionally but that key is "
                    "absent from the committed probabilities"
                ),
            ))
            continue

        new_key = _candidate_key(candidate)
        report.carried[new_key] = old_results[old_key]
        if window_resolver is None:
            old_window = new_window = None
        else:
            old_window = window_resolver(
                sheet_of(old_candidate.get("source_tile")),
                old_candidate["centroid_x"],
                old_candidate["centroid_y"],
            )
            new_window = window_resolver(
                sheet_of(candidate.get("source_tile")), nx, ny,
            )
        report.carry_log.append({
            "new_key": new_key,
            "old_key": old_key,
            "distance_m": round(best_distance, 6),
            "old_window": old_window,
            "new_window": new_window,
            "window_identical": old_window == new_window,
            "mound_probability": old_results[old_key].get("mound_probability"),
        })

    return report


def build_provenance(
    report: CarryReport,
    *,
    label: str,
    old_probs_path: Path,
    old_manifest_path: Path,
    new_manifest_path: Path,
    old_manifest: dict[str, Any],
    new_manifest: dict[str, Any],
    tolerance: float,
) -> dict[str, Any]:
    """Assemble the ``carry_provenance.json`` record.

    Args:
        report: The carry result.
        label: Operator-supplied name for this carry (e.g. ``k3``).
        old_probs_path: The committed ``probabilities.json``.
        old_manifest_path: The committed crops manifest.
        new_manifest_path: The rebuilt crops manifest.
        old_manifest: The loaded committed crops manifest.
        new_manifest: The loaded rebuilt crops manifest.
        tolerance: The positional tolerance used.

    Returns:
        The provenance dict, with the displaced detail capped at the 60
        largest displacements so the file stays readable.
    """
    return {
        "schema": "verifier-stage-carry/1",
        "label": label,
        "extends_stage": str(old_probs_path.parent),
        "extends_crops": str(old_manifest_path.parent),
        "new_crops": str(new_manifest_path.parent),
        "new_union": new_manifest.get("source_geojson"),
        "old_union": old_manifest.get("source_geojson"),
        "match_tolerance_m": tolerance,
        "old_candidates": len(old_manifest["candidates"]),
        "new_candidates": len(new_manifest["candidates"]),
        "carried": len(report.carried),
        "uncovered": len(report.uncovered),
        "carried_but_displaced": len(report.displaced),
        "carried_with_changed_pixel_window": len(report.window_changed),
        "displaced_detail": sorted(
            report.displaced, key=lambda entry: -entry["distance_m"],
        )[:60],
        "uncovered_detail": report.uncovered,
    }


def build_seeded_probabilities(
    report: CarryReport, old_probs: dict[str, Any],
) -> dict[str, Any]:
    """Assemble the seeded ``probabilities.json``.

    The schema is the one ``run_pv.py`` reads for its resume filter, and the
    header fields are carried from the committed stage rather than restated,
    so the new stage cannot silently claim a different verifier.

    Args:
        report: The carry result.
        old_probs: The committed ``probabilities.json``, loaded.

    Returns:
        The document to write.
    """
    return {
        "version": "1.0",
        "mode": old_probs.get("mode", "realtime"),
        "verifier_config": old_probs.get("verifier_config", "unknown"),
        "iterations": old_probs.get("iterations", 1),
        "total_results": len(report.carried),
        "results": report.carried,
    }


def main() -> None:
    """Re-key the committed results onto the rebuilt union's candidate ids."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-manifest", type=Path, required=True)
    parser.add_argument("--old-probs", type=Path, required=True)
    parser.add_argument("--new-manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--rasters-dir", type=Path, required=True)
    parser.add_argument("--label", type=str, required=True)
    parser.add_argument("--padding", type=int, default=DEFAULT_PADDING)
    parser.add_argument(
        "--tolerance",
        type=float,
        default=DEFAULT_TOLERANCE,
        help=(
            "Positional match tolerance in metres (default: "
            f"{DEFAULT_TOLERANCE}). Decides WHICH old candidate a new one "
            "is; the pixel window decides whether the carry is valid."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the coverage census and write nothing",
    )
    args = parser.parse_args()

    old_manifest = json.loads(args.old_manifest.read_text())
    new_manifest = json.loads(args.new_manifest.read_text())
    old_probs = json.loads(args.old_probs.read_text())

    with RasterWindowResolver(args.rasters_dir, args.padding) as resolver:
        report = carry_probabilities(
            old_manifest["candidates"],
            new_manifest["candidates"],
            old_probs["results"],
            tolerance=args.tolerance,
            window_resolver=resolver,
        )

    provenance = build_provenance(
        report,
        label=args.label,
        old_probs_path=args.old_probs,
        old_manifest_path=args.old_manifest,
        new_manifest_path=args.new_manifest,
        old_manifest=old_manifest,
        new_manifest=new_manifest,
        tolerance=args.tolerance,
    )

    if not args.dry_run:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        (args.out_dir / "probabilities.json").write_text(
            json.dumps(build_seeded_probabilities(report, old_probs)),
        )
        (args.out_dir / "carry_provenance.json").write_text(
            json.dumps(provenance, indent=2),
        )

    print(json.dumps(
        {
            key: provenance[key]
            for key in (
                "label",
                "old_candidates",
                "new_candidates",
                "carried",
                "uncovered",
                "carried_but_displaced",
                "carried_with_changed_pixel_window",
            )
        },
        indent=2,
    ))
    print("uncovered:", json.dumps(report.uncovered, indent=2))
    if args.dry_run:
        print("DRY RUN — nothing written")


if __name__ == "__main__":
    main()
