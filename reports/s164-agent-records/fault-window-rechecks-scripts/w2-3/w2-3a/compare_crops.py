#!/usr/bin/env python3
"""
W2-3a: compare re-extracted crop manifests and crop PNGs with the originals.

For each of the 28 K-ladder Phase 2 rungs, ``run-g2-326181bcd.sh`` stage 7
re-extracted the crops into ``<extract-root>/rowNN/`` and wrote the rung's
original crops directory to ``rowNN.map``. This script:

1. compares each regenerated ``candidate_manifest.json`` with the committed
   blob at the generating commit, leaf by leaf, setting aside only
   ``rasters_dir`` (an absolute machine path: the original recorded sapphire's
   live checkout, the replay records its worktree);
2. compares every regenerated crop PNG, byte for byte, with the PNG still on
   disk in sapphire's live checkout (read only), recording the live files'
   modification-time range so it is clear they are the September originals,
   the images the verifier was sent.

Usage::

    python compare_crops.py --repo <git dir> --commit 326181bcd \
        --extract-root <out>/g2/extract --live-root ~/Code/map-reader-llm \
        --out result.json

Read-only on the repository and the live checkout; no network; no API call.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SET_ASIDE = ("rasters_dir",)


def sha(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def leaf_diffs(a: Any, b: Any, path: str = "") -> list[dict[str, Any]]:
    """List the differing leaves of two JSON values (set-aside keys skipped)."""
    out: list[dict[str, Any]] = []
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            if key in SET_ASIDE:
                continue
            if key not in a or key not in b:
                out.append({"path": f"{path}/{key}", "missing_in": "regen" if key not in a
                            else "committed"})
            else:
                out.extend(leaf_diffs(a[key], b[key], f"{path}/{key}"))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append({"path": path, "regen_len": len(a), "committed_len": len(b)})
        for i, (x, y) in enumerate(zip(a, b)):
            out.extend(leaf_diffs(x, y, f"{path}[{i}]"))
    elif a != b or type(a) is not type(b):
        out.append({"path": path, "regen": a, "committed": b})
    return out


def main() -> int:
    """Compare every rung's manifest and crops; write a JSON summary."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--extract-root", required=True, type=Path)
    parser.add_argument("--live-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    rows = []
    for mapfile in sorted(args.extract_root.glob("row*.map")):
        crops_dir = mapfile.read_text().strip()
        regen_dir = args.extract_root / mapfile.stem
        repo_path = f"{crops_dir}/candidate_manifest.json"
        committed = subprocess.run(
            ["git", "-C", str(args.repo), "cat-file", "blob", f"{args.commit}:{repo_path}"],
            capture_output=True, check=True).stdout
        regen_bytes = (regen_dir / "candidate_manifest.json").read_bytes()
        diffs = leaf_diffs(json.loads(regen_bytes), json.loads(committed))
        set_aside = {k: (json.loads(regen_bytes)[k], json.loads(committed)[k]) for k in SET_ASIDE}
        regen_pngs = sorted((regen_dir / "crops").glob("*.png"))
        live_dir = args.live_root / crops_dir / "crops"
        n_equal = n_differ = n_missing = 0
        mtimes = []
        differing = []
        for png in regen_pngs:
            live = live_dir / png.name
            if not live.exists():
                n_missing += 1
                continue
            mtimes.append(live.stat().st_mtime)
            if sha(png) == sha(live):
                n_equal += 1
            else:
                n_differ += 1
                differing.append(png.name)
        n_live = len(list(live_dir.glob("*.png"))) if live_dir.exists() else 0

        def iso(t: float) -> str:
            return datetime.fromtimestamp(t, timezone.utc).isoformat(timespec="seconds")

        rows.append({
            "row": mapfile.stem, "crops_dir": crops_dir,
            "manifest_byte_identical": regen_bytes == committed,
            "manifest_leaf_diffs_after_set_aside": diffs[:20],
            "manifest_n_leaf_diffs": len(diffs),
            "manifest_set_aside": set_aside,
            "n_regen_pngs": len(regen_pngs), "n_live_pngs": n_live,
            "png_equal": n_equal, "png_differ": n_differ, "png_missing_live": n_missing,
            "png_differing_first": differing[:10],
            "live_mtime_min": iso(min(mtimes)) if mtimes else None,
            "live_mtime_max": iso(max(mtimes)) if mtimes else None,
        })
    summary = {
        "n_rungs": len(rows),
        "manifests_field_identical": sum(1 for r in rows if r["manifest_n_leaf_diffs"] == 0),
        "manifests_byte_identical": sum(1 for r in rows if r["manifest_byte_identical"]),
        "pngs_regen": sum(r["n_regen_pngs"] for r in rows),
        "pngs_equal": sum(r["png_equal"] for r in rows),
        "pngs_differ": sum(r["png_differ"] for r in rows),
        "pngs_missing_live": sum(r["png_missing_live"] for r in rows),
    }
    args.out.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2) + "\n")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
