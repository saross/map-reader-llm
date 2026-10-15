#!/usr/bin/env python3
"""Score every distinct consensus/PV arm recorded in committed pairwise outputs.

D60 (3) task 4: which committed outputs of ``run_pairwise_tests.py`` would
move under the fixed route, without regenerating them. Each output records
its arms' sources (``condition_a.source`` / ``condition_b.source``) and its
buffer. This builds each distinct arm once through the given tree's loaders
and scores it at every buffer an output needs; running it in the OLD and
NEW trees and comparing tells, per output, whether an arm's F1 moves.

Usage:
    python probe_sources.py --tree <root> --root <clone root> \
        --files <list of output JSONs, one per line> --bounds <g> --ref <g>
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

OLD_PREFIX = "/home/shawn/Code/map-reader-llm/"


def main() -> None:
    """Build, score and print every distinct arm as JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--files", type=Path, required=True)
    parser.add_argument("--bounds", type=Path, required=True)
    parser.add_argument("--ref", type=Path, required=True)
    args = parser.parse_args()

    sys.path.insert(0, str(args.tree / "scripts"))
    logging.basicConfig(level=logging.WARNING)
    import geopandas as gpd  # noqa: PLC0415
    import pairwise_permutation_test as ppt  # noqa: PLC0415
    from lib_advanced_metrics import calculate_f1_internal  # noqa: PLC0415

    assert Path(ppt.__file__).resolve().is_relative_to(args.tree.resolve())
    root = args.root.resolve()

    def local(path: str) -> Path:
        """Map a recorded absolute path into the clone."""
        return root / path.removeprefix(OLD_PREFIX) if path.startswith("/") else root / path

    arms: dict[str, dict] = {}
    for line in args.files.read_text().split():
        d = json.loads((root / line).read_text())
        buf = int(d["metadata"]["buffer_metres"])
        for side in ("condition_a", "condition_b"):
            src = d[side]["source"]
            if src["mode"] not in ("pv", "consensus"):
                continue
            key = json.dumps(src, sort_keys=True)
            rec = arms.setdefault(key, {"source": src, "buffers": set(), "files": 0})
            rec["buffers"].add(buf)
            rec["files"] += 1

    gdf_bounds = gpd.read_file(args.bounds).to_crs("EPSG:32635")
    gdf_ref = gpd.read_file(args.ref).to_crs("EPSG:32635")
    for rec in arms.values():
        src = rec["source"]
        if src["mode"] == "pv":
            gdf = ppt.load_pv_detections(
                local(src["probabilities"]), local(src["manifest"]), float(src["threshold"]),
            )
        else:
            config = f"{src['temperature']},{src['pool_size']},{src['threshold']}"
            gdf = ppt.load_consensus_detections(local(src["study_dir"]), config, gdf_bounds)
        rec["n_detections"] = len(gdf)
        rec["f1"] = {}
        for buf in sorted(rec["buffers"]):
            _p, _r, f1 = calculate_f1_internal(gdf, gdf_ref, gdf_bounds, buffer_metres=buf)
            rec["f1"][str(buf)] = round(f1, 6)
        rec["buffers"] = sorted(rec["buffers"])
        print(src["mode"], rec["n_detections"], rec["f1"], file=sys.stderr, flush=True)
    print(json.dumps({"tree": str(args.tree), "arms": list(arms.values())}, indent=1))


if __name__ == "__main__":
    main()
