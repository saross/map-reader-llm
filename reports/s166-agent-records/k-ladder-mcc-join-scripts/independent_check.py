#!/usr/bin/env python3
"""
An independent re-implementation of the three tile joins, to check every rung's tile-MCC.

Part of the S166 K-ladder tile-join job
(``reports/s166-agent-records/k-ladder-mcc-join.md``). The tiering harness
builds each rung's per-tile labels through
``lib_advanced_metrics.calculate_tile_classification`` and gates them against
the same library's aggregate, so under a geometric join no check outside the
library has seen the numbers. This script books points to tiles with its own
code — one ``geopandas.sjoin`` (``intersects``) per point set, and the rules
of ``reports/tile-mcc-geometric-join-2026-09-12.md`` § 2 written out again
here — and computes the tile confusion and MCC itself:

* ``id``: a detection is booked to the tile its ``source_tile`` names; a
  reference to every tile it intersects;
* ``geometric-primary``: every point (detection or reference) to the one
  intersected tile with the nearest centroid, ties to the smallest
  ``tile_name``;
* ``geometric-contains``: every point to every tile it intersects.

A tile is predicted positive when a detection is booked to it and truly
positive when a reference is. The detections are read as the harness reads
them (``era1_leaderboard_tiering.cell_detections``, which also writes a
missing ``source_tile``); everything after that is this file's. For every
rung of the 29 ladders and each join, its MCC is compared with the MCC the
join's tiering ranked on (four decimals).

Usage: python independent_check.py <clone_root> <phase2_compat_json> <out_json>

Author: Shawn Ross, Claude Code (S166). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

JOINS = ("id", "geometric-primary", "geometric-contains")
GROUP_DIR = {"phase 1": "mcc-test", "phase 2": "phase2-mcc-test",
             "clipped": "clipped-mcc-test", "tier E": "tier-e"}
R = "results/k-ladder-2026-09-12/mcc-join-2026-10-30"


def mcc(tp: int, tn: int, fp: int, fn: int) -> float | None:
    """Matthews correlation coefficient, None when a marginal is zero."""
    den = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    return None if den == 0 else (tp * tn - fp * fn) / math.sqrt(den)


def main() -> int:
    """Recompute every rung's tile confusion under each join and compare."""
    root, compat, target = (Path(sys.argv[1]).resolve(), Path(sys.argv[2]),
                            Path(sys.argv[3]))
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "scripts"))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import geopandas as gpd  # noqa: PLC0415

    import era1_leaderboard_tiering as t  # noqa: PLC0415
    from ladder_files import cli_of, ladder_specs, resolve  # noqa: PLC0415

    cache: dict[str, gpd.GeoDataFrame] = {}

    def frame(path: str) -> gpd.GeoDataFrame:
        if path not in cache:
            cache[path] = gpd.read_file(root / path).to_crs(t.TARGET_CRS)
        return cache[path]

    def book(points: gpd.GeoDataFrame, tiles: gpd.GeoDataFrame,
             rule: str) -> set[str]:
        """The tiles a point set is booked to under a geometric rule."""
        pts = gpd.GeoDataFrame(geometry=points.geometry.values, crs=tiles.crs)
        pts["pid"] = range(len(pts))
        hit = gpd.sjoin(pts, tiles[["tile_name", "geometry"]],
                        predicate="intersects", how="inner")
        if rule == "geometric-contains":
            return set(hit["tile_name"])
        cent = tiles.set_index("tile_name").geometry.centroid
        booked: set[str] = set()
        for pid, grp in hit.groupby("pid"):
            point = pts.geometry.iloc[pid]
            best = min(grp["tile_name"],
                       key=lambda n: (point.distance(cent[n]), n))
            booked.add(best)
        return booked

    def confusion(pred: set[str], truth: set[str], names: list[str]) -> dict:
        tp = sum(1 for n in names if n in pred and n in truth)
        fp = sum(1 for n in names if n in pred and n not in truth)
        fn = sum(1 for n in names if n not in pred and n in truth)
        return {"tp": tp, "fp": fp, "fn": fn, "tn": len(names) - tp - fp - fn}

    # The MCC each join's tiering ranked on, by (ladder, ref).
    ranked: dict[str, dict[tuple[str, str], float]] = {j: {} for j in JOINS}
    for join in JOINS:
        sfx = "" if join == "id" else f"_{join}"
        for gdir in ("mcc-test", "phase2-mcc-test", "clipped-mcc-test"):
            for path in (root / R / join / gdir / "tiering").glob(f"*/tiering_*m{sfx}.json"):
                for row in json.loads(path.read_text())["mcc_permutation"]["ranking"]:
                    ranked[join][(path.parent.name, row["ref"])] = row["mcc"]
        path = root / R / join / "tier-e" / f"tiering_20m{sfx}.json"
        for row in json.loads(path.read_text())["mcc_permutation"]["ranking"]:
            ranked[join][("tier-e", row["ref"])] = row["mcc"]

    rows, mismatches = [], []
    for spec in ladder_specs(root, compat):
        clis = [cli_of(root, resolve(root, spec["conditions"], r["ref"])["eval_path"])
                for r in spec["rungs"]]
        refs = frame(next(iter({c["ground_truth"] for c in clis})))
        tiles = frame(spec["bounds_override"] or next(iter({c["bounds"] for c in clis})))
        names = list(tiles["tile_name"].unique())
        truth = {"id": book(refs, tiles, "geometric-contains"),
                 "geometric-primary": book(refs, tiles, "geometric-primary"),
                 "geometric-contains": book(refs, tiles, "geometric-contains")}
        for rung, cli in zip(spec["rungs"], clis, strict=True):
            det = t.cell_detections(cli, tiles)
            pred = {"id": set(det["source_tile"]) & set(names),
                    "geometric-primary": book(det, tiles, "geometric-primary"),
                    "geometric-contains": book(det, tiles, "geometric-contains")}
            row = {"ladder": spec["slug"], "K": rung["K"], "ref": rung["ref"]}
            for join in JOINS:
                conf = confusion(pred[join], truth[join], names)
                value = mcc(**conf)
                want = ranked[join].get((spec["slug"], rung["ref"]))
                row[join] = {"confusion": conf,
                             "mcc": None if value is None else round(value, 6),
                             "tiering_mcc": want}
                if want is None or value is None or round(value, 4) != round(want, 4):
                    mismatches.append({"ladder": spec["slug"], "K": rung["K"],
                                       "join": join, "independent": value,
                                       "tiering": want})
            rows.append(row)
            print(f"{spec['slug']:46s} K={rung['K']:2d} " + " ".join(
                f"{j[:9]}={row[j]['mcc']}/{row[j]['tiering_mcc']}" for j in JOINS),
                flush=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({
        "what": ("an independent re-implementation of the three tile joins; "
                 "every rung's MCC against the MCC its join's tiering ranked on"),
        "n_rungs": len(rows), "n_comparisons": len(rows) * len(JOINS),
        "n_mismatches": len(mismatches), "mismatches": mismatches,
        "rows": rows}, indent=2) + "\n")
    print(f"{len(rows)} rungs, {len(mismatches)} mismatch(es)", flush=True)
    return 0 if not mismatches else 3


if __name__ == "__main__":
    raise SystemExit(main())
