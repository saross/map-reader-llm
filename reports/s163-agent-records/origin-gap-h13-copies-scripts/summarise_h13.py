#!/usr/bin/env python3
"""
Summarise what the D62 (1) H13 fix moves: OLD (pre-fix) against NEW.

D62 (1) workstream ``origin-gap-h13-copies`` (2026-10-13). Reads the
``old`` and one ``new`` output tree written by ``run-h13.sh`` and writes a
JSON summary with, for every swept cell of the tier-0 aggregation sweep,
the K-sensitivity diagnostic, and the tile-size grid: the before and after
point estimates (and, for tier-0, the F1 intervals), plus, for every cell
file, how many detections changed sheet and how many lost their tile. It
also lists the best cell per arm, per (pool, K), and per (configuration,
K) before and after, which are the readings the documents quote.

Usage::

    python summarise_h13.py --old <out/old> --new <out/new1> --json-out <file>

Author: Claude Code (Opus 5.5) for Shawn Ross
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def sheet(tile: str | None) -> str | None:
    """The sheet prefix of a tile name (``None`` for a null tile).

    Args:
        tile: A tile name such as ``K-35-052-4_32635_x0_y0.png``.

    Returns:
        The text before ``_x``, or ``None``.
    """
    return None if tile is None else tile.split("_x")[0]


def cell_moves(old: Path, new: Path) -> dict[str, int]:
    """Count detections whose tile, or sheet, differs between two cell files.

    Both files hold the same clusters in the same order (the clustering is
    unchanged by the fix); this is asserted on the coordinates.

    Args:
        old: Pre-fix cell GeoJSON.
        new: Post-fix cell GeoJSON.

    Returns:
        Counts ``n``, ``tile_changed``, ``sheet_changed`` and ``now_null``.
    """
    fo = json.loads(old.read_text())["features"]
    fn = json.loads(new.read_text())["features"]
    assert len(fo) == len(fn), (old, len(fo), len(fn))
    assert all(a["geometry"] == b["geometry"] for a, b in zip(fo, fn)), old
    tiles = [(a["properties"]["source_tile"], b["properties"]["source_tile"])
             for a, b in zip(fo, fn)]
    return {
        "n": len(fo),
        "tile_changed": sum(1 for a, b in tiles if a != b),
        "sheet_changed": sum(1 for a, b in tiles if b is not None and sheet(a) != sheet(b)),
        "now_null": sum(1 for a, b in tiles if a is not None and b is None),
    }


def pair_cells(old: list[dict], new: list[dict], keys: tuple[str, ...],
               fields: tuple[str, ...]) -> list[dict[str, Any]]:
    """Pair two cell lists by ``keys`` and report each field before and after.

    Args:
        old: Pre-fix cells. new: Post-fix cells.
        keys: Fields identifying a cell. fields: Fields to compare.

    Returns:
        One row per cell with ``<field>_old`` / ``<field>_new``.
    """
    index = {tuple(c[k] for k in keys): c for c in old}
    rows = []
    for c in new:
        k = tuple(c[x] for x in keys)
        o = index[k]
        row = {x: c[x] for x in keys}
        for f in fields:
            row[f"{f}_old"], row[f"{f}_new"] = o.get(f), c.get(f)
        row["moved"] = any(o.get(f) != c.get(f) for f in fields)
        rows.append(row)
    assert len(rows) == len(old)
    return rows


def best(rows: list[dict], group: tuple[str, ...], side: str) -> dict:
    """Best F1 per group on one side (``old`` or ``new``); first wins a tie.

    Args:
        rows: Paired rows. group: Grouping fields. side: ``old`` or ``new``.

    Returns:
        Mapping of a group label to the winning row's key fields and F1.
    """
    out: dict[str, Any] = {}
    for r in rows:
        g = "|".join(str(r[x]) for x in group)
        if g not in out or r[f"f1_{side}"] > out[g][f"f1_{side}"]:
            out[g] = r
    return {g: {k: v for k, v in r.items() if not k.endswith("_old" if side == "new"
                                                              else "_new")}
            for g, r in out.items()}


def main() -> int:
    """Write the summary JSON.

    Returns:
        Process exit status (0 on success).
    """
    parser = argparse.ArgumentParser(description="Summarise the H13 fix's moves.")
    parser.add_argument("--old", type=Path, required=True)
    parser.add_argument("--new", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    out: dict[str, Any] = {}

    # Tier-0 aggregation sweep.
    t_old = json.loads((args.old / "tier0/tier0_sweep.json").read_text())["cells"]
    t_new = json.loads((args.new / "tier0/tier0_sweep.json").read_text())["cells"]
    rows = pair_cells(t_old, t_new, ("arm", "min_corroboration", "min_votes"),
                      ("n_detections", "precision", "recall", "f1",
                       "f1_ci_lower", "f1_ci_upper"))
    for r in rows:
        name = f"{r['arm']}_c{r['min_corroboration']}_k{r['min_votes']}.geojson"
        r["detections"] = cell_moves(args.old / "tier0/cells" / name,
                                     args.new / "tier0/cells" / name)
    out["tier0"] = {
        "cells": rows,
        "n_moved": sum(r["moved"] for r in rows),
        "best_old": best(rows, ("arm",), "old"),
        "best_new": best(rows, ("arm",), "new"),
    }

    # K-sensitivity diagnostic.
    k_old = json.loads((args.old / "ksens/k_sensitivity.json").read_text())
    k_new = json.loads((args.new / "ksens/k_sensitivity.json").read_text())
    ks: dict[str, Any] = {}
    for pool in k_new["k_sensitivity"]:
        rows = pair_cells(
            k_old["k_sensitivity"][pool]["cells"], k_new["k_sensitivity"][pool]["cells"],
            ("K", "min_corroboration", "min_votes"),
            ("precision", "recall", "f1", "n_detections"))
        for r in rows:
            r["pool"] = pool
        ks[pool] = {
            "cells": rows,
            "n_moved": sum(r["moved"] for r in rows),
            "max_abs_df1": max(abs(r["f1_new"] - r["f1_old"]) for r in rows),
            "best_old": best(rows, ("K",), "old"),
            "best_new": best(rows, ("K",), "new"),
            "profile_same": k_old["k_sensitivity"][pool]["corroboration_profile"]
            == k_new["k_sensitivity"][pool]["corroboration_profile"],
        }
    ks["decomposition"] = {"old": k_old["decomposition"], "new": k_new["decomposition"]}
    out["ksens"] = ks

    # Tile-size x overlap grid.
    g_old = json.loads((args.old / "tilesize/tilesize_grid.json").read_text())
    g_new = json.loads((args.new / "tilesize/tilesize_grid.json").read_text())
    rows = pair_cells(g_old["cells"], g_new["cells"],
                      ("cell", "K_label", "min_corroboration", "min_votes"),
                      ("n_detections", "precision", "recall", "f1"))
    for r in rows:
        name = (f"{r['cell']}_{r['K_label']}_c{r['min_corroboration']}"
                f"_k{r['min_votes']}.geojson")
        r["detections"] = cell_moves(args.old / "tilesize/cells" / name,
                                     args.new / "tilesize/cells" / name)
    out["tilesize"] = {
        "scope_same": g_old["scope"] == g_new["scope"],
        "cells": rows,
        "n_moved": sum(r["moved"] for r in rows),
        "best_old": best(rows, ("cell", "K_label"), "old"),
        "best_new": best(rows, ("cell", "K_label"), "new"),
    }
    args.json_out.write_text(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
