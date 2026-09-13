#!/usr/bin/env python3
"""
Emit a ``pass_provenance`` sidecar beside a union built by a stride builder.

Why this script exists
----------------------
Two requirements pull in opposite directions when a 55-map union is built
(`reports/gemini37-image-55map-deltas-2026-09-13.md` section 7, blocker B2,
open question Q7):

* **Comparability.** The Gemini 3.7 *text* arms' 55-map unions were built by
  ``scripts/stride55_prepare_and_union.py`` (no carrier clip, full-extent
  scoring). A modality difference-in-differences against those arms must use
  the same builder, or the contrast confounds modality with builder.
* **Provenance.** The campaign card requires a ``pass_provenance`` block —
  repository-relative pass paths plus content hashes — so a later reader can
  prove which files a union was built from. Only
  ``scripts/merge_passes.py --sweep --output-dir`` writes one, into
  ``voting_summary.json``; ``stride55_prepare_and_union.py`` writes no
  provenance at all.

No single builder satisfies both. This script is the resolution ruled by the
parent session: build the union with ``stride55_prepare_and_union.py`` and emit
the provenance record as a **sidecar**, computed by
``merge_passes.build_pass_provenance`` over the *same resolved fragment set*
the union builder used — that is, over
``stride55_prepare_and_union.resolve_pass_paths``, imported here rather than
re-implemented, so the two can never drift.

The sidecar's schema is the one ``merge_passes.threshold_sweep`` writes
(``consensus-pass-provenance/1``: ``pass_provenance_schema``,
``total_passes``, ``pass_ids``, ``pass_provenance``), so the existing guard
``build_all_consensus.compare_pass_provenance`` and the contract tests in
``tests/test_consensus_pass_provenance.py`` recognise it unchanged. Three
sidecar-only keys are added for traceability: the union the record describes,
its feature count, and the builder that produced it.

Usage::

    python scripts/emit_union_pass_provenance.py \
        --root outputs/gemini37-image-55map-2026-09-13 \
        --cell g384_ov192_55map_g37img --k 3 --write

Zero API. Zero network. Run anywhere the pass files are on disk.

Created: 2026-09-13
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.merge_passes import (  # noqa: E402
    PASS_PROVENANCE_SCHEMA,
    _repo_relative,
    build_pass_provenance,
)
from scripts.stride55_prepare_and_union import (  # noqa: E402
    resolve_pass_paths,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: The builder this sidecar stands in for. Recorded in the sidecar so a reader
#: knows the provenance was emitted beside, not by, the union builder.
BUILDER = "scripts/stride55_prepare_and_union.py"


class ProvenanceError(RuntimeError):
    """A gate failed: the union or its pass files are not where they must be."""


def sidecar_path(union_path: Path) -> Path:
    """
    The sidecar's path for a union.

    Args:
        union_path: The union GeoJSON, e.g. ``.../union_k3.geojson``.

    Returns:
        ``.../union_k3_pass_provenance.json`` — the union's stem with a
        ``_pass_provenance.json`` suffix, so union and sidecar sort together.

    Examples:
        >>> sidecar_path(Path("/tmp/verifier/cell/union_k3.geojson")).name
        'union_k3_pass_provenance.json'
    """
    return union_path.with_name(f"{union_path.stem}_pass_provenance.json")


def build_sidecar(
    root: Path,
    cell: str,
    k: int,
) -> tuple[dict[str, Any], Path]:
    """
    Build the provenance record for one union, and say where it belongs.

    Resolves ``run_1`` .. ``run_<k>`` through the union builder's own
    ``resolve_pass_paths`` (main detections file plus every
    ``run_<N>_recovery*`` fragment), then hands the resolved set to
    ``merge_passes.build_pass_provenance``.

    Args:
        root: The campaign output root, e.g.
            ``outputs/gemini37-image-55map-2026-09-13``.
        cell: The pass-pool directory name under ``root``, e.g.
            ``g384_ov192_55map_g37img``.
        k: The first-N pass count the union was built at.

    Returns:
        A ``(record, sidecar_path)`` pair. ``record`` carries the
        ``consensus-pass-provenance/1`` keys plus ``union_path``,
        ``union_feature_count`` and ``builder``.

    Raises:
        ProvenanceError: If the union GeoJSON is absent (the sidecar must
            describe an artefact that exists), if any pass resolves to no
            files, or if any resolved file could not be hashed.
    """
    if k < 1:
        raise ProvenanceError(f"--k must be at least 1, got {k}")

    union_path = root / "verifier" / cell / f"union_k{k}.geojson"
    if not union_path.is_file():
        raise ProvenanceError(
            f"no union at {union_path} — build it with {BUILDER} --write first"
        )

    cell_dir = root / cell
    pass_files: dict[str, list[Path]] = {}
    for i in range(1, k + 1):
        run = f"run_{i}"
        paths = resolve_pass_paths(cell_dir, run)
        if not paths:
            raise ProvenanceError(f"{cell}/{run}: resolved to no detections file")
        pass_files[run] = paths

    provenance = build_pass_provenance(pass_files)
    unhashed = [e["path"] for e in provenance if e["git_blob_hash"] is None]
    if unhashed:
        raise ProvenanceError(
            f"could not hash {len(unhashed)} resolved file(s): {unhashed[:3]}"
        )

    features = json.loads(union_path.read_text())["features"]
    record: dict[str, Any] = {
        "pass_provenance_schema": PASS_PROVENANCE_SCHEMA,
        "total_passes": k,
        "pass_ids": sorted(pass_files),
        "pass_provenance": provenance,
        "union_path": _repo_relative(union_path),
        "union_feature_count": len(features),
        "builder": BUILDER,
    }
    return record, sidecar_path(union_path)


def main() -> int:
    """Entry point. Returns a process exit status."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--root",
        required=True,
        help="Campaign output root holding the cell and verifier/ directories",
    )
    ap.add_argument(
        "--cell", required=True, help="Pass-pool directory name under --root"
    )
    ap.add_argument(
        "--k",
        type=int,
        required=True,
        help="First-N pass count the union was built at",
    )
    ap.add_argument(
        "--write",
        action="store_true",
        help="Write the sidecar (default: report it and exit without writing)",
    )
    args = ap.parse_args()

    root = Path(args.root)
    if not root.is_absolute():
        root = PROJECT_ROOT / root

    try:
        record, dest = build_sidecar(root, args.cell, args.k)
    except ProvenanceError as exc:
        logger.error("%s", exc)
        return 2

    logger.info(
        "K=%d union %s: %d features from %d pass(es), %d resolved file(s)",
        args.k,
        record["union_path"],
        record["union_feature_count"],
        record["total_passes"],
        len(record["pass_provenance"]),
    )
    for entry in record["pass_provenance"]:
        logger.info(
            "  %-18s %s  %s",
            entry["pass_id"],
            entry["git_blob_hash"][:12],
            entry["path"],
        )

    if not args.write:
        logger.info("dry run — pass --write to emit %s", dest.name)
        return 0

    dest.write_text(json.dumps(record, indent=2) + "\n")
    logger.info("wrote %s", _repo_relative(dest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
