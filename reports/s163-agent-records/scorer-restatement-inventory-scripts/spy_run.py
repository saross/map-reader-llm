#!/usr/bin/env python3
"""
Spy harness: run a per_map_counts consumer and record OLD versus NEW counts.

Scratch tool for the Phase 5 scorer-restatement sweep (2026-10-12). It runs
one consumer script's ``main()`` in-process with every ``per_map_counts``
binding replaced by a spy that computes BOTH the pre-fix rule (a verbatim
copy of the function as it stood on ``main`` at c546f6901) and the fixed
function, records the two per-sheet tables, the shared scorer's detection
scope diagnostics, and the calling line, and returns the FIXED counts (so
every downstream gate sees today's rule).

It writes the generator's outputs in place in whatever tree it runs in, so
run it only in a disposable tree and restore the outputs afterwards.

Usage::

    python spy_run.py <tree> <module> <records.json> [script args...]

Example::

    python spy_run.py ~/scratch/x/repo stride55_sweep_oracle out.json
"""

from __future__ import annotations

import importlib
import inspect
import json
import sys
from pathlib import Path


def main() -> int:
    """Install the spy, run the consumer, and write the call records."""
    tree = Path(sys.argv[1]).resolve()
    module_name = sys.argv[2]
    out_path = Path(sys.argv[3])
    sys.path.insert(0, str(tree))

    from scripts import lib_advanced_metrics as lam
    from scripts import stride55_sweep_oracle as so

    fixed = so.per_map_counts
    # The fixed function must be the one under test: it routes through
    # iter_sheet_scopes. Refuse to run against an unfixed tree.
    if "iter_sheet_scopes" not in inspect.getsource(fixed):
        raise SystemExit("tree's per_map_counts is not the fixed version")

    def legacy(gdf_det, gdf_ext, bounds):
        """Verbatim pre-fix per_map_counts (main c546f6901, lines 123-146)."""
        maps = {lam.get_map_name(n) for n in bounds["tile_name"].unique()}
        maps.discard("Unknown")
        out = {}
        for m in sorted(maps):
            mb = bounds[bounds["tile_name"].str.startswith(m)]
            ref = gdf_ext[gdf_ext[so.REF_MAP_COL] == m]
            ref = lam.scope_references_to_tiles(ref, mb) if not ref.empty else ref
            det = gdf_det[gdf_det["source_tile"].str.startswith(m)]
            if det.empty and ref.empty:
                out[m] = (0, 0, 0)
                continue
            if det.empty:
                out[m] = (0, 0, len(ref))
                continue
            if ref.empty:
                out[m] = (0, len(det), 0)
                continue
            md, _, ud, ur = lam.match_detections_to_references(
                list(det.geometry), list(ref.geometry), so.BUFFER_R)
            out[m] = (len(md), len(ud), len(ur))
        return out

    records: list[dict] = []

    def f1(counts):
        return so.f1_from_map_counts(counts)

    def spy(gdf_det, gdf_ext, bounds):
        frame = inspect.stack()[1]
        new = fixed(gdf_det, gdf_ext, bounds)
        old = legacy(gdf_det, gdf_ext, bounds)
        diag = lam.scope_detections_to_frame(gdf_det, bounds).diagnostics
        moved = {m: {"old": list(old[m]), "new": list(new[m])}
                 for m in new if tuple(old.get(m, ())) != tuple(new[m])}
        records.append({
            "caller": f"{Path(frame.filename).name}:{frame.lineno}",
            "function": frame.function,
            "n_detections": int(len(gdf_det)),
            "columns": [c for c in gdf_det.columns if c != "geometry"],
            "keys_equal": sorted(old) == sorted(new),
            "f1_old": f1(old), "f1_new": f1(new),
            "totals_old": [sum(c[i] for c in old.values()) for i in range(3)],
            "totals_new": [sum(c[i] for c in new.values()) for i in range(3)],
            "sheets_moved": moved,
            "scope": {k: v for k, v in diag.items() if k.startswith("n_")
                      or k in ("origin_columns", "applied")},
        })
        return new

    so.per_map_counts = spy
    mod = importlib.import_module(f"scripts.{module_name}")
    if hasattr(mod, "per_map_counts"):
        mod.per_map_counts = spy
    sys.argv = [str(tree / "scripts" / f"{module_name}.py"), *sys.argv[4:]]
    rc = 0
    try:
        rc = mod.main() or 0
    except BaseException as exc:  # record the failure, then re-raise
        records.append({"exception": f"{type(exc).__name__}: {exc}"})
        out_path.write_text(json.dumps(records, indent=1) + "\n")
        raise
    out_path.write_text(json.dumps(records, indent=1) + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
