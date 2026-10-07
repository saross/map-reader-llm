"""Why does tier E's re-key survive D50? Compare the three records of each detection's tile.

D50/D51 impact measurement, 2026-10-08 (Session 163). Read-only diagnostic.

For one tier E materialised cell, each detection is joined (identical
coordinates) to its crop-manifest candidate, and three tile records are put
side by side: the cell's ``source_tile`` (re-keyed onto the board frame by
``run_k_ladder_tier_e.reassign_carrier_tiles``), the first entry of the cell's
own ``source_tiles`` property (the consensus cluster's member tiles), and the
crop manifest's ``source_tile`` (what the blast radius restored as the origin,
``frames-blast-radius-2026-10-07-scripts/tier_e_sheet_rekey.py``). Rows where the
re-keyed sheet differs from either record are printed.

Usage::

    PYTHONDONTWRITEBYTECODE=1 ~/Code/map-reader-llm/.venv/bin/python tier_e_origin_probe.py \
        --code WORKTREE --k 3 --out out/tier_e_origin_probe.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import meas_lib as ml  # noqa: E402

BOARD = "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"
TIER_E = "results/k-ladder-2026-09-12/tier-e"


def main() -> int:
    """Print and record the rows whose tile records disagree on the sheet."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    code = args.code.expanduser().resolve()
    ml.setup(code)
    lam = ml.LIB
    import scripts.sweep_f1_wbf as wbf  # noqa: PLC0415

    ops = json.loads((code / TIER_E / "operating-points.json").read_text())
    rung = next(r for r in ops["rungs"] if r["K"] == args.k)
    bounds = ml.load_geojson(code / BOARD)
    cell = ml.load_detections(code / rung["opmax"]["detections"], bounds)
    cands = wbf.load_candidates_as_gdf(code / rung["verify_dir"] / "crops/candidate_manifest.json",
                                       code / rung["verify_dir"] / "probabilities.json")
    dist, idx = cKDTree(np.c_[cands.geometry.x, cands.geometry.y]).query(
        np.c_[cell.geometry.x, cell.geometry.y])
    sheets = sorted({lam.get_map_name(str(t)) for t in bounds["tile_name"]} - {"Unknown"})

    def sheet(name: object) -> str | None:
        return lam._sheet_of_tile_name(name, sorted(sheets, key=len, reverse=True))

    rows = []
    for pos in range(len(cell)):
        members = lam.parse_tile_list(cell["source_tiles"].iloc[pos])
        rec = {
            "pos": pos, "match_m": float(dist[pos]),
            "rekeyed": cell["source_tile"].iloc[pos],
            "members": members,
            "manifest_source_tile": cands["source_tile"].iloc[idx[pos]],
        }
        rec["sheets"] = {"rekeyed": sheet(rec["rekeyed"]),
                         "first_member": sheet(members[0]) if members else None,
                         "manifest": sheet(rec["manifest_source_tile"])}
        s = rec["sheets"]
        if s["rekeyed"] is not None and (s["rekeyed"] != s["first_member"]
                                         or s["rekeyed"] != s["manifest"]):
            rows.append(rec)
    diag = lam.scope_detections_to_frame(cell, bounds).diagnostics
    out = {"K": args.k, "cell": rung["opmax"]["detections"], "n": len(cell),
           "max_match_m": float(dist.max()), "scope": diag, "disagreeing_rows": rows}
    for r in rows:
        print(r["sheets"], r["rekeyed"], "| first member", r["members"][:1],
              "| manifest", r["manifest_source_tile"], f"| n members {len(r['members'])}")
    print("scope", {k: diag[k] for k in ("n_out_of_frame", "n_origin_restored",
                                         "n_origin_unrecognised", "origin_columns")})
    args.out.write_text(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
