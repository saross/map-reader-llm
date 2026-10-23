#!/usr/bin/env python3
"""
trial_origin.py — S164 restatement pass, lane-bridge TRIAL (not the pass's code).

Runs ``scripts/modality_bridge_floors.py`` and then
``scripts/modality_bridge_verifier_sd.py`` from a disposable copy, in ONE
process, with three in-memory patches. Nothing in the copy's files changes.

1. ``image_b_analysis.load_image_union``, when called WITHOUT an explicit
   ``policy`` (the floors' arm loader, ``original_sets``, the verifier SD's
   replicates), returns the joined union re-tiled on its members' own sheets
   by ``lib_cluster_origins.union_on_origin`` from the cell's prepared passes,
   as ``image_b_analysis.main`` does since D62 (1). Calls with an explicit
   policy (the six-cell anchor gate, ``policy="fixed"``) are untouched.
2. ``modality_bridge_floors.build_rung`` clusters with
   ``cluster_votes_with_members`` and tiles with
   ``points_on_origin(drop_unassigned=False)``, as ``image_b_analysis``'s
   first-N ladder does since D62 (1).
3. ``multiprocessing.Pool`` in the floors module is replaced by a serial
   in-process map, so the run is one process.

With ``--no-patch`` only patch 3 is applied (the scripts as committed).

Usage::

    python trial_origin.py <copy_root> <out_dir> [--no-patch] [--workers N]

Writes ``<out_dir>/floors/`` and ``<out_dir>/verifier-sd/``.
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path


def main() -> int:
    """Patch, then run the floors and the verifier SD; return the first non-zero exit."""
    copy_root = Path(sys.argv[1]).resolve()
    out_dir = Path(sys.argv[2]).resolve()
    patch = "--no-patch" not in sys.argv[3:]
    sys.path.insert(0, str(copy_root))

    import geopandas as gpd
    import numpy as np

    from scripts import image_b_analysis as iba
    from scripts import modality_bridge_floors as fl
    from scripts import modality_bridge_verifier_sd as vsd
    from scripts.grid_analysis import CRS, load_cell_passes
    from scripts.lib_cluster_origins import (
        cluster_votes_with_members,
        points_on_origin,
        union_on_origin,
    )
    from scripts.stride_verifier_analysis import COMMON_BOUNDS

    class SerialPool:
        """Stand-in for multiprocessing.Pool: map in this process."""

        def __init__(self, *_a, **_k) -> None:
            pass

        def __enter__(self) -> SerialPool:
            return self

        def __exit__(self, *_a) -> None:
            return None

        def map(self, fn, items, chunksize=1):  # noqa: ARG002
            return [fn(x) for x in items]

    fl.Pool = SerialPool
    log = {"origin_calls": []}

    if patch:
        orig_load = iba.load_image_union
        bounds = gpd.read_file(COMMON_BOUNDS)

        def load_on_origin(vroot=None, union_name=None, verify_dir="verify", policy=None):
            """iba.load_image_union, then (no explicit policy) union_on_origin."""
            u = orig_load(vroot, union_name, verify_dir, policy)
            if policy is not None:
                return u
            prov = u.attrs.get("verifier_probabilities")
            vroot_p = Path(vroot)
            m = re.match(r"union_k(\d+)\.geojson$", union_name or "")
            if not m:
                raise RuntimeError(f"trial patch: cannot infer K from {union_name!r}")
            n = int(m.group(1))
            scoring = vroot_p.parent.parent / "scoring"
            passes = load_cell_passes(scoring, vroot_p.name, n_passes=n)
            out = union_on_origin(u, passes, bounds, label=f"{vroot_p}", n_passes=n)
            out.attrs["verifier_probabilities"] = prov
            log["origin_calls"].append((str(vroot_p), union_name, verify_dir, len(u), len(out)))
            return out

        iba.load_image_union = load_on_origin

        def build_rung_on_origin(passes):
            """fl.build_rung with member tiles kept and each cluster on its own sheet."""
            centroids, votes, members = cluster_votes_with_members(passes, 1)
            gdf, _ = points_on_origin(
                np.asarray(centroids), fl._G["bounds"], members, CRS,
                columns={"vote_count": np.asarray(votes)}, drop_unassigned=False)
            return gdf

        fl.build_rung = build_rung_on_origin

    t0 = time.time()
    if "--quick" in sys.argv[3:]:
        # The verifier SD's gates only, against the copy's committed floors:
        # does the (patched) path reproduce every committed cell set?
        rc = vsd.main(["--gate-only", "--floors-dir",
                       str(copy_root / "results/modality-bridge-2026-10-07/floors"),
                       "--out-dir", str(out_dir / "unused")])
        print(f"TRIAL quick gate-only exit {rc} ({time.time() - t0:.0f} s); "
              f"origin calls {len(log['origin_calls'])}", flush=True)
        for c in log["origin_calls"]:
            print("TRIAL origin", c, flush=True)
        return rc
    rc = fl.main(["--out-dir", str(out_dir / "floors"), "--workers", "1"])
    print(f"TRIAL floors exit {rc} ({time.time() - t0:.0f} s)", flush=True)
    if rc != 0:
        return rc
    t1 = time.time()
    rc = vsd.main(["--floors-dir", str(out_dir / "floors"),
                   "--out-dir", str(out_dir / "verifier-sd")])
    print(f"TRIAL verifier-sd exit {rc} ({time.time() - t1:.0f} s)", flush=True)
    print(f"TRIAL origin calls: {len(log['origin_calls'])}", flush=True)
    for c in log["origin_calls"]:
        print("TRIAL origin", c, flush=True)
    print(f"TRIAL DONE total {time.time() - t0:.0f} s", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
