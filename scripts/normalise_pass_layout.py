#!/usr/bin/env python3
"""Put a detection pass into the canonical layout, whatever mode produced it.

The three execution modes write their outputs differently, which makes passes
from different modes hard to combine into one pool even when the detections are
equivalent:

    real-time (flex or standard)
        <pool>/run_N/detections-<version>-<model>-<date>.geojson
                    /detections-<version>-<model>-<date>.meta.json
                    /detections-<version>-<model>-<date>.tiles.json

    batch
        <dir>/<condition>/run_N/detections_<condition>_runNN.geojson
                               /detections_<condition>_runNN.meta.json
                               /...

A K-ladder needs its rungs side by side in one pool, and this project now has
reason to mix modes within a pool: `gemini-3.7-flash` flex capacity failed for
twelve hours on 2026-09-16/17 while batch served the same model in 104 seconds,
so a pass may be produced by whichever route is available on the day.

This module normalises to the REAL-TIME layout, because that is what the
existing pools and the manifest generators already read.

The normaliser COPIES rather than moves by default: the source is the run's
own record and stays where the mode put it, so the operation is repeatable and
nothing is destroyed if the mapping turns out wrong.

Usage:
    python scripts/normalise_pass_layout.py --src <batch run dir> \
        --pool outputs/<run>/<cell> --run 4 --version detect_brief-text-image \
        --model gemini-3.7-flash --date 2026-09-17 [--move] [--dry-run]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

#: Suffixes a pass is made of. The geojson is the detections; the meta carries
#: usage and configuration for the cost audit; the tiles list is what the
#: completeness check reads.
PASS_SUFFIXES = (".geojson", ".meta.json", ".tiles.json")


def canonical_stem(version: str, model: str, date: str) -> str:
    """Return the real-time filename stem.

    The model is shortened the way the real-time path does it — ``gemini-`` is
    dropped — so a normalised file is indistinguishable from a natively
    produced one.

    Args:
        version: Config version, e.g. ``detect_brief-text-image``.
        model: Full model id, e.g. ``gemini-3.7-flash``.
        date: ISO date the pass ran, e.g. ``2026-09-17``.

    Returns:
        The stem, without a suffix.

    Examples:
        >>> canonical_stem("detect_brief-text-image", "gemini-3.7-flash", "2026-09-17")
        'detections-detect_brief-text-image-3.7-flash-2026-09-17'
    """
    return f"detections-{version}-{model.replace('gemini-', '')}-{date}"


def find_pass_files(src: Path) -> dict[str, Path]:
    """Locate a pass's three files under *src*, whatever they are named.

    Matching is by SUFFIX rather than by name, because the naming is exactly
    what differs between modes. Searched recursively, since the batch layout
    nests a condition directory and a run directory below the one given.

    Args:
        src: Directory holding one pass's output.

    Returns:
        Mapping of suffix to path, for those found.

    Raises:
        FileNotFoundError: No detections geojson anywhere under *src*.
    """
    found: dict[str, Path] = {}
    for suffix in PASS_SUFFIXES:
        # ``.meta.json`` and ``.tiles.json`` both end ``.json``; match the
        # longest suffix first by checking the whole name.
        hits = sorted(p for p in src.rglob("*")
                      if p.is_file() and p.name.endswith(suffix)
                      and "batch_working" not in p.parts)
        if suffix == ".geojson":
            hits = [h for h in hits if "detections" in h.name]
        found_one = select_pass_file(hits, suffix, src)
        if found_one is not None:
            found[suffix] = found_one
    if ".geojson" not in found:
        raise FileNotFoundError(f"no detections geojson under {src}")
    return found


def select_pass_file(hits: list[Path], suffix: str, src: Path) -> Path | None:
    """Choose the one file of a suffix that IS the pass, or refuse.

    A chunked batch run leaves per-chunk files (``..._chunk0.tiles.json``,
    ``..._chunk1.tiles.json``, ...) beside the merged pass file
    (``..._run01.tiles.json``). The merged file is the pass; a chunk is one
    seventh of it. Before 2026-09-18 this chose by SORT ORDER, and took the
    merged file only because ``run01.tiles.json`` happens to sort before
    ``run01_chunk0.tiles.json`` — a coincidence, not a rule. Had it gone the
    other way, one chunk's tile list would have been normalised into the pool
    as the whole pass, and every downstream reader would have seen an
    ordinary-looking file covering one seventh of the corpus.

    The rule now: chunk files (any name containing ``_chunk``) are never
    candidates. If only chunk files exist the pass has not been merged and
    the caller must merge it first — refusing is the right answer, because
    the alternative is a well-formed wrong one. If more than one non-chunk
    file remains the layout is ambiguous, and that too is refused rather
    than resolved by sort order.

    Args:
        hits: All files under *src* ending in *suffix*, sorted.
        suffix: The suffix being resolved (for messages).
        src: The searched directory (for messages).

    Returns:
        The single non-chunk file, or ``None`` when *hits* is empty.

    Raises:
        FileNotFoundError: Only chunk files exist — the pass is unmerged.
        ValueError: More than one non-chunk candidate — the layout is
            ambiguous and must be resolved by the operator, not by sorting.
    """
    if not hits:
        return None
    whole = [h for h in hits if "_chunk" not in h.name]
    chunks = [h for h in hits if "_chunk" in h.name]
    if not whole:
        raise FileNotFoundError(
            f"only chunk files for {suffix} under {src} "
            f"({len(chunks)} chunks, e.g. {chunks[0].name}); the pass has "
            "not been merged — merge the chunks first, never normalise one")
    if len(whole) > 1:
        raise ValueError(
            f"{len(whole)} non-chunk candidates for {suffix} under {src}: "
            f"{[h.name for h in whole]}; refusing to choose by sort order")
    if chunks:
        print(f"  {len(chunks)} chunk file(s) for {suffix} ignored; "
              f"taking the merged {whole[0].name}", file=sys.stderr)
    return whole[0]


def normalise(src: Path, pool: Path, run: int, version: str, model: str,
              date: str, move: bool = False, dry_run: bool = False) -> Path:
    """Place one pass's files under ``pool/run_<run>/`` with canonical names.

    Args:
        src: Directory the producing mode wrote into.
        pool: Pool directory the rung belongs to.
        run: Pass number within the pool.
        version: Config version for the canonical name.
        model: Model id for the canonical name.
        date: ISO date for the canonical name.
        move: Move instead of copy. Off by default — the source is the run's
            own record, and copying keeps the operation repeatable.
        dry_run: Report the mapping and change nothing.

    Returns:
        The destination directory.
    """
    files = find_pass_files(src)
    dest = pool / f"run_{run}"
    stem = canonical_stem(version, model, date)
    print(f"{src}  ->  {dest}")
    for suffix, path in sorted(files.items()):
        target = dest / f"{stem}{suffix}"
        size = path.stat().st_size
        print(f"  {path.name}  ->  {target.name}  ({size / 1e6:.1f} MB)")
        if dry_run:
            continue
        dest.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise FileExistsError(
                f"{target} exists; refusing to overwrite a committed pass")
        (shutil.move if move else shutil.copy2)(str(path), str(target))
    if dry_run:
        print("  [DRY RUN] nothing written")
    return dest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, type=Path)
    ap.add_argument("--pool", required=True, type=Path)
    ap.add_argument("--run", required=True, type=int)
    ap.add_argument("--version", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--move", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    normalise(src=args.src, pool=args.pool, run=args.run, version=args.version,
              model=args.model, date=args.date, move=args.move,
              dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
