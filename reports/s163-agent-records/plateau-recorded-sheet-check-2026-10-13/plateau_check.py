"""Independent check of the plateau incumbents' recorded-sheet F1 (read-only).

Gate: the committed rebuild path (bare centroids through ``as_gdf``) must
reproduce ``board_13cell.f1`` in ``results/stride-2026-08-25/plateau_analyses.json``.
Then the same rows keep their own recorded ``source_tile`` as origin, and the
D50 function ``assign_primary_tiles_on_origin_sheet`` picks the carrier tile on
that sheet; the set is scored with the board's own ``score``.
"""
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np

root = Path(sys.argv[1])
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "scripts"))
import stride_plateau_analyses as sp  # noqa: E402
from scripts.grid_analysis import CRS, as_gdf, score  # noqa: E402
from scripts.lib_advanced_metrics import assign_primary_tiles_on_origin_sheet  # noqa: E402

bounds = gpd.read_file(sp.COMMON_BOUNDS)
ref = gpd.read_file(sp.GROUND_TRUTH)
committed = json.loads((root / "results/stride-2026-08-25/plateau_analyses.json").read_text())
board = committed.get("board_13cell") or committed.get("board") or {}
cf1 = board.get("f1", {})
for name, rel in sp.INCUMBENTS.items():
    inc = gpd.read_file(root / rel).to_crs(CRS)
    legacy = as_gdf(np.asarray([[g.x, g.y] for g in inc.geometry]), bounds)
    f_legacy = score(legacy, ref, bounds)["f1"]
    rec = gpd.GeoDataFrame({"origin_source_tile": inc["source_tile"].astype(str).values},
                           geometry=list(inc.geometry), crs=CRS)
    tiles, diag = assign_primary_tiles_on_origin_sheet(
        rec, bounds, origin=[[t] for t in rec["origin_source_tile"]])
    rec["source_tile"] = tiles
    rec = rec[rec["source_tile"].notna()].copy()
    f_rec = score(rec, ref, bounds)["f1"]
    moved = int(sum(a != b for a, b in zip(
        legacy.sort_index()["source_tile"], rec.reindex(legacy.index)["source_tile"])))
    gate_ok = cf1.get(name) is not None and abs(cf1[name] - f_legacy) < 1e-12
    print(f"{name:9s} committed={cf1.get(name)!s:.8} legacy={f_legacy:.6f} "
          f"gate={'PASS' if gate_ok else 'FAIL'} "
          f"recorded={f_rec:.6f} diff={f_rec - f_legacy:+.4f} n={len(inc)} "
          f"on_carrier_legacy={len(legacy)} on_carrier_rec={len(rec)} rekeyed={moved} diag={diag}")
