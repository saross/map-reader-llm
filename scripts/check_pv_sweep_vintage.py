#!/usr/bin/env python3
"""Detect and repair cross-vintage joins in the archived PV materialisation registry.

Why
---
Every ``pv_registry.json`` cell is defined by an operating point ``(vote_t,
prob_t)`` applied to a candidate universe: the proposer consensus union at
``consensus_path``, joined to the verifier stage's ``probabilities.json`` by
candidate index (union feature *i* <-> results key ``candidate_{i:05d}``).
That join is only meaningful while the union file still holds the SAME
features, in the SAME order, that the verifier cropped.

``scripts/materialise_opmax_cells.py`` performs the join but cannot tell a
union that has since been rebuilt from one that has not: it fails soft,
dropping candidates with no probability entry and silently pairing every
other index with whatever feature now sits there.  For
``pv-high-text-t0.0-n3`` that produced a plausible-looking 410 detections
against a registered 403 — an artefact, not an operating point (2026-09-11).

The cheap, decisive diagnostic is the sweep's own universe size.  Every
committed ``sweep_2d.json`` records ``n`` at ``(vote_t 1, prob_t 0.0)``, which
is the number of candidates the sweep saw.  When that differs from the union's
feature count, the sweep and the union are different vintages, and one of two
things happened:

``probabilities-grew``
    ``n_sweep < n_union == n_probabilities``.  The union is unchanged; the
    verifier's probabilities were completed after the sweep ran (the Obs 461
    class, ruled on 2026-09-08 for four image stages).  The index join is
    still sound — the sweep is merely stale.
``union-rebuilt``
    ``n_probabilities < n_union``.  The union file was re-materialised after
    the verifier ran, so its feature ORDER no longer matches the probability
    keys.  The index join is invalid, and any count it produces is noise.

Subcommands
-----------
``survey``
    Run the diagnostic over every ``pv_registry`` cell and print (optionally
    write) the classification.
``manifests``
    For one cell in the ``union-rebuilt`` class, materialise the two candidate
    universes as ``candidate_manifest.json`` files that
    ``scripts/sweep_f1_greedy_pv.py`` can sweep directly: the ORIGINAL vintage
    (the union blob at a named git commit, joined to the registered
    probabilities) and the CURRENT vintage (the union as committed today,
    joined to a named complete probabilities file).  Sweeping both with the
    same tool answers "is the registered operating point still the argmax?"
    without ever performing the invalid cross-vintage join.
``materialise``
    Apply an operating point to one vintage and write the detection GeoJSON
    plus a provenance sidecar, reusing the canonical filter in
    ``scripts/materialise_opmax_cells.py`` so the output is shape-identical to
    the board's other ``-opmax`` cells.

Manifest fidelity: the manifest's ``centroid_x`` / ``centroid_y`` are the
union's WGS84 coordinates transformed to EPSG:32635, which is exactly how the
pipeline built them — checked against the committed
``verified-v1-n3-recovery-2026-09-08/crops/candidate_manifest.json``, where all
1,319 centroids reproduce to 0 m (2026-09-11).

Usage::

    python scripts/check_pv_sweep_vintage.py survey --write results/…/vintage.json
    python scripts/check_pv_sweep_vintage.py manifests --cell pv-high-text-t0.0-n3 \\
        --original-commit 09fe46a7f \\
        --current-probabilities outputs/h11/…/verified-v1-n3-recovery-2026-09-08/probabilities.json \\
        --out-dir results/…/staleness-2026-09-11
    python scripts/check_pv_sweep_vintage.py materialise --cell pv-high-text-t0.0-n3 \\
        --union outputs/h11/…/consensus/consensus_t1.geojson \\
        --probabilities outputs/h11/…/verified-v1-n3-recovery-2026-09-08/probabilities.json \\
        --vote-t 3 --prob-t 0.15 --stage-id … --output results/…/cell.geojson

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from materialise_opmax_cells import (  # noqa: E402
    OUTPUT_CRS_URN,
    classify_vintage as classify,
    filter_pv_union,
    git_blob_hash,
    git_last_commit,
    sweep_universe,
)

PV_REGISTRY = ("archive/superseded-leaderboards/leaderboard/era2/pv-materialised/"
               "pv_registry.json")
#: The CRS the crop manifests record centroids in (the pipeline's working CRS).
MANIFEST_CRS = "EPSG:32635"


def _load(rel: str | Path) -> Any:
    """Load a repository-relative JSON file."""
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


def survey() -> dict[str, Any]:
    """Classify every ``pv_registry`` cell.

    Returns:
        The survey report (also printed by :func:`main`).
    """
    rows = []
    for entry in _load(PV_REGISTRY):
        if "consensus_path" not in entry:
            # The one manifest-mode cell (``mode`` = ``manifest``): its universe
            # is a committed candidate manifest keyed by candidate_id, not a
            # union addressed by index, so no cross-vintage join is possible.
            rows.append({"id": entry["id"], "K": entry.get("K"), "track": entry.get("track"),
                         "verdict": "manifest-mode",
                         "why": "the cell's universe is a candidate manifest keyed by "
                                "candidate_id; there is no index join to go stale"})
            continue
        union_rel, prob_rel = entry["consensus_path"], entry["probabilities_path"]
        n_union = len(_load(union_rel).get("features", []))
        n_prob = len(_load(prob_rel).get("results", {}))
        n_sweep = sweep_universe(entry.get("sweep_path"))
        verdict, why = classify(n_union, n_prob, n_sweep)
        rows.append({
            "id": entry["id"], "K": entry.get("K"), "track": entry.get("track"),
            "registered_point": entry.get("best_at_20m"),
            "union": union_rel, "probabilities": prob_rel, "sweep": entry.get("sweep_path"),
            "n_union": n_union, "n_probabilities": n_prob, "n_sweep": n_sweep,
            "verdict": verdict, "why": why,
            "union_last_commit": git_last_commit(union_rel),
            "probabilities_last_commit": git_last_commit(prob_rel),
            "sweep_last_commit": git_last_commit(entry["sweep_path"]) if entry.get("sweep_path") else None,
        })
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    return {"checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "registry": PV_REGISTRY, "n_cells": len(rows), "counts": counts, "cells": rows}


def union_at_commit(union_rel: str, commit: str) -> list[dict[str, Any]]:
    """The union's features as they stood at a git commit.

    Args:
        union_rel: Repository-relative union GeoJSON.
        commit: Any git revision.

    Returns:
        The feature list from that blob.

    Raises:
        RuntimeError: If the blob cannot be read.
    """
    out = subprocess.run(["git", "-C", str(REPO_ROOT), "show", f"{commit}:{union_rel}"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"cannot read {union_rel} at {commit}: {out.stderr.strip()}")
    return json.loads(out.stdout).get("features", [])


def manifest_from_union(features: list[dict[str, Any]], source_geojson: str) -> dict[str, Any]:
    """Build a sweepable ``candidate_manifest.json`` from a union's features.

    ``scripts/sweep_f1_greedy_pv.py`` reads ``candidate_id``, ``source_tile``,
    ``centroid_x`` / ``centroid_y`` (EPSG:32635) and ``properties.vote_count``.
    The union's index order IS the candidate id order, which is what makes the
    manifest a faithful reconstruction of what the verifier cropped.

    Args:
        features: Union features, in file order.
        source_geojson: Repository-relative path the features came from.

    Returns:
        A manifest document in the pipeline's shape.
    """
    from pyproj import Transformer  # imported here so `survey` needs no geo stack

    transformer = Transformer.from_crs("EPSG:4326", MANIFEST_CRS, always_xy=True)
    candidates = []
    for index, feature in enumerate(features):
        lon, lat = feature["geometry"]["coordinates"][:2]
        x, y = transformer.transform(lon, lat)
        props = dict(feature.get("properties") or {})
        tiles = props.get("source_tiles") or []
        source_tile = props.get("source_tile") or (tiles[0] if tiles else "")
        props.setdefault("source_tile", source_tile)
        candidates.append({
            "candidate_id": index,
            "crop_file": f"crops/candidate_{index:05d}.png",
            "source_tile": source_tile,
            "centroid_x": x, "centroid_y": y,
            "cropped_from": "reconstructed-from-union",
            "properties": props,
        })
    return {
        "version": "1.0",
        "source_geojson": source_geojson,
        "reconstructed_by": "scripts/check_pv_sweep_vintage.py manifests",
        "reconstructed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "crs": MANIFEST_CRS,
        "total_detections": len(candidates),
        "successful_extractions": len(candidates),
        "failed_extractions": 0,
        "candidates": candidates,
    }


def write_manifest_dir(out_dir: Path, manifest: dict[str, Any], probabilities_rel: str) -> None:
    """Write a ``crops/`` + ``verified/`` pair the sweep tool can consume.

    Args:
        out_dir: Vintage directory to create.
        manifest: The manifest document.
        probabilities_rel: Repository-relative probabilities to copy in.
    """
    (out_dir / "crops").mkdir(parents=True, exist_ok=True)
    (out_dir / "verified").mkdir(parents=True, exist_ok=True)
    (out_dir / "crops" / "candidate_manifest.json").write_text(
        json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    (out_dir / "verified" / "probabilities.json").write_text(
        (REPO_ROOT / probabilities_rel).read_text(encoding="utf-8"), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_survey = sub.add_parser("survey", help="classify every pv_registry cell")
    p_survey.add_argument("--write", type=Path, help="also write the report as JSON")

    p_man = sub.add_parser("manifests", help="build the two vintages' sweepable manifests")
    p_man.add_argument("--cell", required=True, help="pv_registry id")
    p_man.add_argument("--original-commit", required=True,
                       help="commit whose union blob the registered stage verified")
    p_man.add_argument("--current-probabilities", required=True,
                       help="complete probabilities for the union as committed today")
    p_man.add_argument("--out-dir", type=Path, required=True)

    p_mat = sub.add_parser("materialise", help="apply an operating point to one vintage")
    p_mat.add_argument("--cell", required=True)
    p_mat.add_argument("--union", required=True, help="union GeoJSON (repo-relative)")
    p_mat.add_argument("--probabilities", required=True)
    p_mat.add_argument("--vote-t", type=int, required=True)
    p_mat.add_argument("--prob-t", type=float, required=True)
    p_mat.add_argument("--stage-id", required=True)
    p_mat.add_argument("--output", type=Path, required=True)
    p_mat.add_argument("--why", default="", help="one line recorded in the sidecar")

    args = parser.parse_args(argv)

    if args.command == "survey":
        report = survey()
        print(f"{report['n_cells']} cells: " +
              ", ".join(f"{k} {v}" for k, v in sorted(report["counts"].items())))
        for row in report["cells"]:
            if row["verdict"] == "same-vintage":
                continue
            print(f"  {row['verdict']:<18} {row['id']:<26} union {str(row.get('n_union')):<6}"
                  f"probs {str(row.get('n_probabilities')):<6}"
                  f"sweep {str(row.get('n_sweep')):<6}")
        if args.write:
            args.write.parent.mkdir(parents=True, exist_ok=True)
            args.write.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
            print(f"wrote {args.write}")
        return 0

    entry = next(e for e in _load(PV_REGISTRY) if e["id"] == args.cell)

    if args.command == "manifests":
        union_rel = entry["consensus_path"]
        original = union_at_commit(union_rel, args.original_commit)
        current = _load(union_rel).get("features", [])
        args.out_dir.mkdir(parents=True, exist_ok=True)
        write_manifest_dir(args.out_dir / "original-vintage",
                           manifest_from_union(original, f"{union_rel}@{args.original_commit}"),
                           entry["probabilities_path"])
        write_manifest_dir(args.out_dir / "current-vintage",
                           manifest_from_union(current, union_rel),
                           args.current_probabilities)
        record = {
            "cell": args.cell,
            "built_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "union": union_rel,
            "original_vintage": {
                "commit": args.original_commit, "n_candidates": len(original),
                "probabilities": entry["probabilities_path"],
                "n_probabilities": len(_load(entry["probabilities_path"])["results"]),
            },
            "current_vintage": {
                "commit": "HEAD", "n_candidates": len(current),
                "probabilities": args.current_probabilities,
                "n_probabilities": len(_load(args.current_probabilities)["results"]),
            },
        }
        (args.out_dir / "vintages.json").write_text(json.dumps(record, indent=1) + "\n",
                                                    encoding="utf-8")
        print(f"original vintage {len(original)} candidates; current vintage {len(current)}")
        print(f"wrote {args.out_dir}/{{original,current}}-vintage/ and vintages.json")
        return 0

    features, stats = filter_pv_union(args.union, args.probabilities, args.vote_t,
                                      args.prob_t, args.stage_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({
        "type": "FeatureCollection", "name": args.cell,
        "crs": {"type": "name", "properties": {"name": OUTPUT_CRS_URN}},
        "features": features}), encoding="utf-8")
    sidecar = args.output.with_suffix(".provenance.json")
    sidecar.write_text(json.dumps({
        "cell": args.cell,
        "written_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "written_by": "scripts/check_pv_sweep_vintage.py materialise",
        "why": args.why,
        "operating_point": {"vote_t": args.vote_t, "prob_t": args.prob_t,
                            "filter": "vote_count >= vote_t AND mound_probability >= prob_t"},
        "stage_id": args.stage_id,
        "inputs": {name: {"path": rel, "git_blob_sha1": git_blob_hash(rel),
                          "last_commit": git_last_commit(rel)}
                   for name, rel in (("union", args.union),
                                     ("probabilities", args.probabilities))},
        "counts": stats,
        "output_crs": "EPSG:4326",
    }, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {args.output} ({stats['n_kept']} features) + {sidecar.name}")
    print(f"  stats: {stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
