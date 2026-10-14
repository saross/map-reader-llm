#!/usr/bin/env python3
"""
Re-merge a chunked batch proposer pass from its committed chunk files.

Fault-window re-check (2026-10-14), rows W1-8 and W2-11. The batch detector
(``scripts/4_detect_mounds_batch.py``) writes one triple per chunk
(``…_chunk<C>.geojson`` / ``.meta.json`` / ``.tiles.json``) and, once every
chunk has landed, merges them into the un-suffixed pass files. The chunk
files are API outputs (not re-obtainable without spend); the merged files
are a deterministic function of them, so they can be re-derived exactly.

This driver copies the committed chunk files (``git show`` at the commit that
holds them) into a scratch run directory and repeats the detector's merge:
the GeoJSON step is the detector's inline block, reproduced line for line
from the generating commit (it is not a callable function); the metadata
step calls ``lib_batch_api.merge_chunk_metadata`` imported from the replay
tree. Then it compares the three merged files with the committed ones.
Zero API: nothing here builds a client.

Usage:
    python remerge_chunks.py --tree TREE --repo REPO --run-dir RUN_DIR \
        --version CONFIG_VERSION --run-number N --chunks-commit C1 \
        --merged-commit C2 --scratch DIR --out result.json

Author: Claude (Opus 5.5) for Shawn Ross; Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def git(repo: Path, *a: str) -> bytes:
    """Run git in ``repo`` and return stdout (raises on failure)."""
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True,
                          check=True).stdout


def main() -> int:
    """Re-merge one pass and compare."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--run-dir", required=True, help="repo-relative run_<N> directory")
    ap.add_argument("--version", required=True)
    ap.add_argument("--run-number", type=int, required=True)
    ap.add_argument("--chunks-commit", required=True)
    ap.add_argument("--merged-commit", required=True)
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--targets", default=None,
                    help='JSON {".geojson": [commit, path], ".meta.json": [...], '
                         '".tiles.json": [...]}: compare with these committed files '
                         "instead of the merged files beside the chunks (a pass "
                         "copied into a pool under its real-time name)")
    args = ap.parse_args()
    sys.path.insert(0, str(args.tree))
    from scripts.lib_batch_api import merge_chunk_metadata

    run_dir = args.scratch
    run_dir.mkdir(parents=True, exist_ok=True)
    names = [n for n in git(args.repo, "ls-tree", "--name-only", args.chunks_commit,
                            args.run_dir + "/").decode().split("\n") if "_chunk" in n]
    for n in names:
        (run_dir / Path(n).name).write_bytes(git(args.repo, "show",
                                                 f"{args.chunks_commit}:{n}"))

    # --- the detector's inline GeoJSON merge (4_detect_mounds_batch.py) ---
    chunk_geojsons = sorted(run_dir.glob("*_chunk*.geojson"))
    merged_features: list = []
    merged_processed: list = []
    crs_obj = None
    for gj_path in chunk_geojsons:
        with open(gj_path) as f:
            gj_data = json.load(f)
        merged_features.extend(gj_data.get("features", []))
        merged_processed.extend(gj_data.get("processed_tiles", []))
        if crs_obj is None:
            crs_obj = gj_data.get("crs")
    merged_output = run_dir / f"detections_{args.version}_run{args.run_number:02d}.geojson"
    merged_data = {"type": "FeatureCollection", "features": merged_features,
                   "processed_tiles": sorted(set(merged_processed))}
    if crs_obj:
        merged_data["crs"] = crs_obj
    with open(merged_output, "w") as f:
        json.dump(merged_data, f)
    # --- the metadata merge ---
    chunk_metas = sorted(run_dir.glob("*_chunk*.meta.json"))
    chunk_tiles = sorted(run_dir.glob("*_chunk*.tiles.json"))
    merge_chunk_metadata(chunk_metas, chunk_tiles, merged_output.with_suffix(".meta.json"),
                         merged_output.with_suffix(".tiles.json"))

    rows = []
    targets = json.loads(args.targets) if args.targets else {}
    for suffix in (".geojson", ".meta.json", ".tiles.json"):
        mine = merged_output.with_suffix(suffix) if suffix != ".geojson" else merged_output
        commit, repo_path = targets.get(
            suffix, (args.merged_commit, f"{args.run_dir}/{mine.name}"))
        committed = git(args.repo, "show", f"{commit}:{repo_path}")
        regen = mine.read_bytes()
        rows.append({"path": repo_path, "commit": commit,
                     "byte_identical": regen == committed,
                     "regen_sha256": hashlib.sha256(regen).hexdigest(),
                     "committed_sha256": hashlib.sha256(committed).hexdigest()})
    out = {"run_dir": args.run_dir, "n_chunk_files": len(names),
           "n_chunks": len(chunk_geojsons), "n_features": len(merged_features),
           "n_tiles": len(merged_data["processed_tiles"]),
           "code_commit": git(args.tree, "rev-parse", "HEAD").decode().strip(),
           "files": rows, "all_identical": all(r["byte_identical"] for r in rows)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(f"{args.run_dir}: {len(chunk_geojsons)} chunks; "
          + ", ".join(f"{sfx} {'IDENTICAL' if r['byte_identical'] else 'DIFFERS'}"
                      for sfx, r in zip(("geojson", "meta", "tiles"), rows)))
    return 0 if out["all_identical"] else 1


if __name__ == "__main__":
    sys.exit(main())
