#!/usr/bin/env python3
"""
Run B Stage 2: the union chain over batch-layout passes, with a layout adapter.

Why this exists
---------------
Run B (``planning/modality-bridge-2026-10-07.md``) re-runs the four proposer
arms of the modality claim on the Batch API. Its Stage 2 builds each arm's
union exactly as the original legs' unions were built (card § 2.2: E80 20 m
within-pass deduplication, E72 exact coverage with additive recovery merge,
carrier clip to the grid's common footprint, c = 1 union with per-cluster
``vote_count``, passes taken in numeric order). The originals' chain
(``scripts/image_b_prepare_and_union.py``) resolves passes with
``stride_prepare_and_union.resolve_pass_paths``, which expects the real-time
layout::

    <cell>/run_<N>/detections-*.geojson          (main pass)
    <cell>/run_<N>_recovery/detections-*.geojson (one additive fragment)

The batch detector writes a different layout (Stage 1 launcher,
``scripts/modality-bridge-2026-10-07-stage1.sh``)::

    <arm>/<version>/run_<N>/detections_<version>_run<NN>.geojson
    <arm>/<version>/run_<N>/detections_<version>_run<NN>_chunk<C>.geojson
    <arm>/recovery_rd<R>/<version>/run_<N>/detections_<version>_run<NN>.geojson

The chunk files of a chunked pass are merged into the un-suffixed file once
every chunk has landed, so they must be EXCLUDED (reading them as well would
double every detection), and a pass may carry several recovery rounds, so
EVERY fragment must be folded, in round order. :func:`resolve_batch_pass_paths`
is that adapter. Everything after pass resolution is the originals' chain,
called through the same functions in the same order.

Gates (nothing is written unless all pass):

- every pass resolves (batch layout: the arm holds exactly ``run_1`` ..
  ``run_K``, each with its merged file; a chunked pass whose merge was
  withheld is refused);
- E72 exact coverage: the union of each pass's ``processed_tiles`` equals the
  pinned manifest (1,398 tiles), with nothing missing and nothing extra;
- no tile is recorded as processed by two files of one pass (a fragment that
  re-ran a completed tile would double its detections; none of the original
  passes overlaps);
- the union written to disk has as many features as were built.

``--compare-to`` checks a built union against a committed one (feature count,
order, coordinates, ``vote_count`` and ``source_tile``): the validation gate
that rebuilds the original legs' unions with this chain (Stage 2 card).

Usage::

    # Gates only (no files written)
    python scripts/modality_bridge_union.py --layout batch \\
        --cell-dir outputs/modality-bridge-2026-10-07/g3-text/detect_brief-text \\
        --k 10 --out-root outputs/modality-bridge-2026-10-07/g3-text

    # Build: dedup passes under <out-root>/scoring/common/<cell>/run_<N>/ and
    # the union at <out-root>/verifier/<cell>/union_k<K>.geojson
    python scripts/modality_bridge_union.py --layout batch ... --write

    # Validation: rebuild an original union into scratch and compare
    python scripts/modality_bridge_union.py --layout legacy \\
        --cell-dir outputs/grid-2026-08-18/g384_ov192 --k 10 \\
        --out-root /scratch/g3-text --write \\
        --compare-to outputs/grid-2026-08-18/verifier/g384_ov192/union_k10.geojson

Zero API. Run on sapphire beside the outputs.

Created: 2026-10-07
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

#: The pinned tile manifest every Run B pass dispatches (1,398 tiles).
DEFAULT_MANIFEST = PROJECT_ROOT / "inputs/grid-2026-08-18/grid_384_ov192_manifest.json"

#: A batch recovery round directory: ``recovery_rd<R>`` with a numeric R.
_RECOVERY_RD_RE = re.compile(r"^recovery_rd(\d+)$")

#: A batch pass directory: ``run_<N>`` with a numeric N.
_RUN_RE = re.compile(r"^run_(\d+)$")

#: Coordinate agreement for :func:`compare_union_files`, in degrees
#: (1e-9 degrees is about 0.1 mm on the ground).
COORD_TOL_DEG = 1e-9


class LayoutError(FileNotFoundError):
    """A pass cannot be resolved unambiguously from its directory layout."""


class OverlapError(RuntimeError):
    """A tile is recorded as processed by more than one file of one pass."""


def _run_number(run: str) -> int:
    """Return N for a ``run_<N>`` directory name.

    Args:
        run: Directory name such as ``run_3``.

    Returns:
        The run number.

    Raises:
        LayoutError: If the name is not ``run_`` followed by digits.
    """
    match = _RUN_RE.match(run)
    if not match:
        raise LayoutError(f"not a pass directory name: {run!r}")
    return int(match.group(1))


def _merged_pass_file(run_dir: Path, version: str, number: int) -> Path | None:
    """Return a batch pass directory's merged detections file, if it has one.

    Chunk files (``…_chunk<C>.geojson``) are never returned: the merged file
    already holds their features.

    Args:
        run_dir: A ``run_<N>`` directory written by the batch detector.
        version: The config version (the name of the directory above
            ``run_<N>``), which the detector puts in the filename.
        number: N.

    Returns:
        The merged file, or None when the directory holds no detections
        file at all.

    Raises:
        LayoutError: If the directory holds chunk files but no merged file
            (a chunk has not landed, so the detector withheld the merge), or
            a non-chunk detections file under any other name.
    """
    expected = f"detections_{version}_run{number:02d}.geojson"
    found = sorted(run_dir.glob("detections_*.geojson"))
    chunks = [p for p in found if "_chunk" in p.name]
    merged = [p for p in found if "_chunk" not in p.name]
    if not merged:
        if chunks:
            raise LayoutError(
                f"{run_dir}: {len(chunks)} chunk file(s) but no merged "
                f"{expected} — a chunk has not landed, so the detector withheld "
                "the merge; resume the pass before building a union")
        return None
    if len(merged) != 1 or merged[0].name != expected:
        raise LayoutError(
            f"{run_dir}: expected exactly one merged file named {expected}, "
            f"found {[p.name for p in merged]}")
    return merged[0]


def resolve_batch_pass_paths(cell_dir: Path, run: str) -> list[Path]:
    """Return one batch pass's detection files: the merged main file, then fragments.

    The batch counterpart of ``stride_prepare_and_union.resolve_pass_paths``
    (same signature, same return contract), for the layout the batch
    detector writes::

        <arm>/<version>/run_<N>/detections_<version>_run<NN>.geojson
        <arm>/recovery_rd<R>/<version>/run_<N>/detections_<version>_run<NN>.geojson

    ``cell_dir`` is ``<arm>/<version>``. Chunk files are excluded; every
    recovery round's fragment for this pass is appended in numeric round
    order (rd1, rd2, …, rd10), which is the order the fragments were
    produced. A round directory that holds no fragment for this pass is
    skipped (the round did not touch it, or its lodge wrote nothing): the
    coverage gate, not the resolver, decides whether the pass is complete.

    Args:
        cell_dir: The arm's config-version directory (``<arm>/<version>``).
        run: Pass directory name, ``run_<N>``.

    Returns:
        Paths in merge order (main first, then fragments by round).

    Raises:
        LayoutError: If the main file is absent or ambiguous, a chunked pass
            or fragment was never merged, or the arm holds a recovery
            directory that is not ``recovery_rd<R>``.

    Examples:
        >>> resolve_batch_pass_paths(  # doctest: +SKIP
        ...     Path("outputs/modality-bridge-2026-10-07/g3-text/detect_brief-text"),
        ...     "run_4")
        [.../g3-text/detect_brief-text/run_4/detections_detect_brief-text_run04.geojson,
         .../g3-text/recovery_rd1/detect_brief-text/run_4/detections_detect_brief-text_run04.geojson]
    """
    number = _run_number(run)
    version = cell_dir.name
    main = _merged_pass_file(cell_dir / run, version, number)
    if main is None:
        raise LayoutError(
            f"{cell_dir / run}: no merged detections_{version}_run{number:02d}.geojson "
            "— the pass has not landed")
    paths = [main]

    rounds: list[tuple[int, Path]] = []
    for child in sorted(cell_dir.parent.iterdir()):
        if not child.is_dir() or not child.name.startswith("recovery"):
            continue
        match = _RECOVERY_RD_RE.match(child.name)
        if not match:
            raise LayoutError(
                f"{child}: unrecognised recovery directory (expected "
                "recovery_rd<R>); archive it or rename it before building a union")
        rounds.append((int(match.group(1)), child))
    for _, rd_dir in sorted(rounds):
        frag_dir = rd_dir / version / run
        if not frag_dir.is_dir():
            continue
        frag = _merged_pass_file(frag_dir, version, number)
        if frag is None:
            logger.warning("%s: no fragment file (round left no output) — skipped",
                           frag_dir)
            continue
        paths.append(frag)
    return paths


def resolve_legacy_pass_paths(cell_dir: Path, run: str) -> list[Path]:
    """The originals' resolver (real-time layout), re-exported unchanged.

    Args:
        cell_dir: The cell's run root.
        run: Pass directory name, ``run_<N>``.

    Returns:
        Paths in merge order (main first, then the ``run_<N>_recovery``
        fragment where one exists).
    """
    from scripts.stride_prepare_and_union import resolve_pass_paths

    return resolve_pass_paths(cell_dir, run)


#: Layout name -> pass resolver.
RESOLVERS: dict[str, Callable[[Path, str], list[Path]]] = {
    "legacy": resolve_legacy_pass_paths,
    "batch": resolve_batch_pass_paths,
}


def check_batch_run_dirs(cell_dir: Path, k: int) -> None:
    """Require a batch arm to hold exactly the passes ``run_1`` .. ``run_K``.

    Every pass of the arm must have been lodged, and nothing else may sit
    beside them (a stray ``run_6`` under a K = 5 arm means an unplanned
    lodge).

    Args:
        cell_dir: The arm's config-version directory.
        k: The arm's pass count.

    Raises:
        LayoutError: If the run directories are not exactly ``run_1..run_K``.
    """
    present = sorted(
        (int(m.group(1)) for d in cell_dir.iterdir()
         if d.is_dir() and (m := _RUN_RE.match(d.name))),
    ) if cell_dir.is_dir() else []
    if present != list(range(1, k + 1)):
        raise LayoutError(
            f"{cell_dir}: pass directories {present}, expected runs 1..{k}")


def processed_by_file(paths: list[Path]) -> list[set[str]]:
    """Read each file's ``processed_tiles`` coverage record.

    Args:
        paths: The detection files of one pass.

    Returns:
        One set of tile names per file, in order.
    """
    return [set(json.loads(p.read_text()).get("processed_tiles") or []) for p in paths]


def overlapping_tiles(per_file: list[set[str]]) -> set[str]:
    """Return the tiles that more than one file of a pass records as processed.

    Args:
        per_file: Coverage records, one set per file.

    Returns:
        Tile names counted more than once.
    """
    counts = Counter(t for s in per_file for t in s)
    return {t for t, n in counts.items() if n > 1}


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file's bytes.

    Args:
        path: The file.

    Returns:
        Hex digest.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    """Return *path* relative to the repository root when it lies inside it."""
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _git_head() -> str | None:
    """Return the repository's HEAD commit, or None outside a git checkout."""
    try:
        return subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def gate_passes(cell_dir: Path, k: int, layout: str,
                manifest: set[str]) -> list[dict[str, Any]]:
    """Resolve and coverage-gate the first K passes of a cell (no writes).

    Args:
        cell_dir: The cell (legacy) or the arm's config-version directory
            (batch).
        k: Passes to take, ``run_1`` .. ``run_K`` in numeric order.
        layout: ``legacy`` or ``batch``.
        manifest: The pinned tile names.

    Returns:
        One record per pass: files, their SHA-256, tiles per file, coverage
        and raw detection count; the loaded features are kept under
        ``_raw`` for :func:`build_union`.

    Raises:
        LayoutError: From the resolver, or (batch) if the arm's run
            directories are not exactly ``run_1..run_K``.
        CoverageError: If a pass's coverage is not exactly the manifest.
        OverlapError: If a tile is processed by two files of one pass.
    """
    from scripts.grid_prepare_scoring import CoverageError, load_pass

    resolver = RESOLVERS[layout]
    if layout == "batch":
        check_batch_run_dirs(cell_dir, k)
    records: list[dict[str, Any]] = []
    for i in range(1, k + 1):
        run = f"run_{i}"
        paths = resolver(cell_dir, run)
        # The originals' loader, unchanged: features concatenated main first.
        raw, processed = load_pass(paths)
        per_file = processed_by_file(paths)
        overlap = overlapping_tiles(per_file)
        missing = manifest - processed
        extra = processed - manifest
        if missing or extra:
            raise CoverageError(
                f"{cell_dir.name}/{run}: {len(processed)} tiles vs {len(manifest)} "
                f"pinned ({len(missing)} missing, {len(extra)} extra). "
                f"Missing: {sorted(missing)[:5]}")
        if overlap:
            raise OverlapError(
                f"{cell_dir.name}/{run}: {len(overlap)} tile(s) processed by more "
                f"than one file: {sorted(overlap)[:5]}")
        records.append({
            "run": run,
            "files": [_rel(p) for p in paths],
            "file_sha256": [sha256_file(p) for p in paths],
            "tiles_per_file": [len(s) for s in per_file],
            "processed_tiles": len(processed),
            "raw_detections": len(raw),
            "_raw": raw,
        })
    return records


def build_union(cell_dir: Path, k: int, layout: str, out_root: Path,
                manifest_path: Path = DEFAULT_MANIFEST, write: bool = False,
                overwrite: bool = False) -> dict[str, Any]:
    """Gate the passes and (with ``write``) build the c = 1 union, as the originals.

    The chain is ``image_b_prepare_and_union.py``'s, step for step: per pass
    (numeric order) E80 20 m within-pass deduplication, written in the common
    scope clipped to the carrier footprint and read back; then
    ``materialise_grid_unions.union_with_votes`` over the K prepared passes;
    then the union reprojected to EPSG:4326 and written.

    Args:
        cell_dir: Cell (legacy) or ``<arm>/<version>`` (batch) directory.
        k: Passes.
        layout: ``legacy`` or ``batch``.
        out_root: Where ``scoring/common/<cell>/run_<N>/detections_dedup.geojson``
            and ``verifier/<cell>/union_k<K>.geojson`` are written.
        manifest_path: The pinned tile manifest.
        write: Write the dedup passes and the union; otherwise gates only.
        overwrite: Replace an existing union (refused by default: crops and
            verifier legs are keyed to the union they were cut from).

    Returns:
        The build record (also written beside the union as
        ``union_k<K>.build.json`` when ``write``).

    Raises:
        FileExistsError: If the union exists and ``overwrite`` is False.
        CoverageError, LayoutError, OverlapError: From the gates.
    """
    import geopandas as gpd

    from scripts.grid_prepare_scoring import CoverageError
    from scripts.materialise_grid_unions import union_with_votes
    from scripts.merge_passes import deduplicate_within_pass
    from scripts.prepare_h13_scoring import write_dedup_geojson
    from scripts.stride_prepare_and_union import COMMON_BOUNDS, DEDUP_METRES

    cell = cell_dir.name
    manifest = set(json.loads(manifest_path.read_text()))
    dest = out_root / "verifier" / cell / f"union_k{k}.geojson"
    if write and dest.exists() and not overwrite:
        raise FileExistsError(
            f"{dest} exists; crops and verifier legs are keyed to it. Pass "
            "--overwrite only after archiving it and anything cut from it")

    common_gdf = gpd.read_file(COMMON_BOUNDS)
    common_tiles = sorted(common_gdf["tile_name"].tolist())
    common_geom = common_gdf.geometry.union_all()
    scoring = out_root / "scoring"

    passes = gate_passes(cell_dir, k, layout, manifest)
    for rec in passes:
        raw = rec.pop("_raw")
        deduped = deduplicate_within_pass(raw, distance_thresh=DEDUP_METRES)
        rec["dedup_detections"] = len(deduped)
        if write:
            stats = write_dedup_geojson(
                deduped, common_gdf, common_tiles,
                scoring / "common" / cell / rec["run"] / "detections_dedup.geojson",
                clip_geom=common_geom)
            rec["common_scope_detections"] = stats["n_out"]
        n_frag = len(rec["files"]) - 1
        logger.info("%s %s: tiles %d%s, raw %d -> dedup %d", cell, rec["run"],
                    rec["processed_tiles"],
                    f" (+{n_frag} fragment(s))" if n_frag else "",
                    rec["raw_detections"], rec["dedup_detections"])

    record: dict[str, Any] = {
        "script": "scripts/modality_bridge_union.py",
        "git_head": _git_head(),
        "layout": layout,
        "cell_dir": _rel(cell_dir),
        "k": k,
        "manifest": _rel(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "manifest_tiles": len(manifest),
        "common_bounds": _rel(COMMON_BOUNDS),
        "dedup_metres": DEDUP_METRES,
        "passes": passes,
        "written": bool(write),
    }
    if not write:
        return record

    # Read the prepared passes back exactly as image_b_prepare_and_union does.
    loaded: list[list[dict]] = []
    for i in range(1, k + 1):
        path = scoring / "common" / cell / f"run_{i}" / "detections_dedup.geojson"
        data = json.loads(path.read_text())
        loaded.append([
            {"centroid": tuple(f["geometry"]["coordinates"]),
             "label": f["properties"].get("label", "mound"),
             "source_tiles": (f["properties"].get("origin_tiles") or "").split(";"),
             "cluster_size": int(f["properties"].get("cluster_size", 1))}
            for f in data["features"]])
    gdf = union_with_votes(loaded, common_gdf)
    dest.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
    written = len(json.loads(dest.read_text())["features"])
    if written != len(gdf):
        raise CoverageError(f"{cell}: wrote {written} != built {len(gdf)}")
    votes = {int(v): int(n) for v, n in
             gdf["vote_count"].value_counts().sort_index().items()}
    record.update({
        "union": _rel(dest),
        "union_sha256": sha256_file(dest),
        "union_features": written,
        "vote_histogram": votes,
    })
    build_path = dest.with_name(dest.stem + ".build.json")
    build_path.write_text(json.dumps(record, indent=1) + "\n")
    logger.info("%s: union n=%d, votes %s -> %s", cell, written, votes, _rel(dest))
    return record


def compare_union_files(built: Path, committed: Path,
                        tol_deg: float = COORD_TOL_DEG) -> dict[str, Any]:
    """Compare two union GeoJSONs feature by feature, in order.

    Args:
        built: The rebuilt union.
        committed: The committed union.
        tol_deg: Coordinate agreement in degrees.

    Returns:
        ``equal`` (count, every coordinate within ``tol_deg``, every
        ``vote_count`` and ``source_tile`` the same, same property keys),
        the counts, the largest coordinate difference, mismatch counts and
        whether the files are byte-identical.
    """
    a = json.loads(built.read_text())["features"]
    b = json.loads(committed.read_text())["features"]
    out: dict[str, Any] = {
        "built": _rel(built), "committed": _rel(committed),
        "n_built": len(a), "n_committed": len(b),
        "bytes_identical": sha256_file(built) == sha256_file(committed),
        "committed_sha256": sha256_file(committed),
    }
    if len(a) != len(b):
        out.update({"equal": False, "reason": "feature counts differ"})
        return out
    max_diff = 0.0
    coord_bad = vote_bad = tile_bad = keys_bad = 0
    for fa, fb in zip(a, b):
        ca = fa["geometry"]["coordinates"]
        cb = fb["geometry"]["coordinates"]
        diff = max(abs(ca[0] - cb[0]), abs(ca[1] - cb[1]))
        max_diff = max(max_diff, diff)
        coord_bad += int(not diff <= tol_deg or math.isnan(diff))
        pa, pb = fa.get("properties") or {}, fb.get("properties") or {}
        vote_bad += int(pa.get("vote_count") != pb.get("vote_count"))
        tile_bad += int(pa.get("source_tile") != pb.get("source_tile"))
        keys_bad += int(sorted(pa) != sorted(pb))
    out.update({
        "max_coord_diff_deg": max_diff,
        "coord_mismatches": coord_bad,
        "vote_mismatches": vote_bad,
        "source_tile_mismatches": tile_bad,
        "property_key_mismatches": keys_bad,
        "vote_histogram_built": dict(sorted(Counter(
            (f.get("properties") or {}).get("vote_count") for f in a).items())),
        "equal": not (coord_bad or vote_bad or tile_bad or keys_bad),
    })
    return out


def main(argv: list[str] | None = None) -> int:
    """Gate, build and optionally compare one union.

    Args:
        argv: Command-line arguments (default ``sys.argv[1:]``).

    Returns:
        0 when every gate passed (and, with ``--compare-to``, the unions are
        equal); 1 on a gate failure or a difference.
    """
    from scripts.grid_prepare_scoring import CoverageError

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layout", choices=sorted(RESOLVERS), required=True,
                    help="Pass layout: legacy (real-time run_<N>/, "
                         "run_<N>_recovery/) or batch (Stage 1).")
    ap.add_argument("--cell-dir", type=Path, required=True,
                    help="The cell (legacy) or <arm>/<config version> (batch).")
    ap.add_argument("--k", type=int, required=True, help="Passes, run_1..run_K.")
    ap.add_argument("--out-root", type=Path, required=True,
                    help="Root for scoring/ and verifier/ outputs.")
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST,
                    help="Pinned tile manifest (default: the 1,398-tile grid).")
    ap.add_argument("--write", action="store_true",
                    help="Write dedup passes and the union (default: gates only).")
    ap.add_argument("--overwrite", action="store_true",
                    help="Replace an existing union (refused by default).")
    ap.add_argument("--compare-to", type=Path, default=None,
                    help="A committed union to compare the built one with.")
    ap.add_argument("--json-out", type=Path, default=None,
                    help="Write the build (and comparison) record here.")
    args = ap.parse_args(argv)

    try:
        record = build_union(args.cell_dir, args.k, args.layout, args.out_root,
                             args.manifest, write=args.write,
                             overwrite=args.overwrite)
    except (CoverageError, LayoutError, OverlapError, FileExistsError) as exc:
        logger.error("REFUSED: %s", exc)
        return 1
    status = 0
    if args.compare_to is not None:
        if not args.write:
            logger.error("--compare-to needs --write (there is no union to compare)")
            return 1
        built = (args.out_root / "verifier" / args.cell_dir.name
                 / f"union_k{args.k}.geojson")
        cmp = compare_union_files(built, args.compare_to)
        record["comparison"] = cmp
        logger.info("compare: built %d vs committed %d; equal=%s; max coord diff "
                    "%.3g deg; vote mismatches %s; bytes identical %s",
                    cmp["n_built"], cmp["n_committed"], cmp["equal"],
                    cmp.get("max_coord_diff_deg", float("nan")),
                    cmp.get("vote_mismatches"), cmp["bytes_identical"])
        status = 0 if cmp["equal"] else 1
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(record, indent=1) + "\n")
    if not args.write:
        logger.info("gates passed for %d pass(es) — re-run with --write to build",
                    args.k)
    return status


if __name__ == "__main__":
    sys.exit(main())
