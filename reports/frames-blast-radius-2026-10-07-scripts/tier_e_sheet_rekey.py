"""Separate the two scope effects in the K-ladder tier E cells: frame scope and sheet re-keying.

Frames blast-radius measurement, Session 163 (2026-10-07). Read-only.

Tier E's sweep (``sweep_f1_greedy_pv.py`` on the crop manifest) and its evaluated cells
(materialised, then re-keyed by ``run_k_ladder_tier_e.reassign_carrier_tiles``) disagree on
F1 at the same operating point. Two mechanisms are possible:

* frame scope — the sweep books out-of-frame candidates; the re-key nulls them;
* sheet re-keying — ``assign_primary_tiles`` picks the nearest tile centroid among ALL frame
  tiles a point intersects, so a detection seen on sheet M can be re-keyed to a tile of the
  neighbouring sheet N where the two sheets' tiles overlap. ``calculate_f1_internal`` matches
  per sheet, so such a detection can no longer match its own sheet's reference.

For each tier E cell this script matches every cell detection to its sweep candidate (same
coordinates), counts the detections re-keyed to another sheet, and scores the cell three
ways: as committed; with the ORIGIN sheet names restored and the geometric frame scope
applied (which equals the ON sweep row at that point); and as committed but with the geometric
scope (identical to committed, because the re-key already nulled the out-of-frame rows).

Usage::

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tier_e_sheet_rekey.py \
        --repo ~/Code/map-reader-llm --out out/tier_e_sheet_rekey.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blast_lib as bl  # noqa: E402

BOARD = "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"
GT = "inputs/vectors/references/mounds-reference.geojson"
OPS = "results/k-ladder-2026-09-12/tier-e/operating-points.json"
#: Further cells re-keyed by ``assign_primary_tiles`` (``materialise_grid_unions.py``) whose
#: files keep no origin tile: (label, detections, the crop manifest of their universe).
EXTRA = (
    ("tier E K = 10 rung (grid g384_ov192 K = 10, verified, p0.15 k10)",
     "results/grid-2026-08-18/conditions-verified/g384_ov192/detections.geojson",
     "outputs/grid-2026-08-18/verifier/g384_ov192/crops/candidate_manifest.json"),
    ("grid g384_ov192 K = 10 under the 3.7 verifier (p0.98 k10)",
     "results/gemini37-fourth-cell/gs-leg/verified_best_20m.geojson",
     "outputs/grid-2026-08-18/verifier/g384_ov192/crops/candidate_manifest.json"),
)


def map_of(value: Any) -> str | None:
    """Sheet name of a tile name, or None for a null."""
    return bl.LIB.get_map_name(value) if isinstance(value, str) and value else None


def main() -> int:
    """Score every tier E cell three ways and write the record."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    bl.add_repo_to_path(repo)
    import scripts.sweep_f1_wbf as wbf  # noqa: PLC0415

    board = bl.load_geojson(repo / BOARD)
    ref = bl.load_geojson(repo / GT)
    out = []
    for rung in json.loads((repo / OPS).read_text())["rungs"]:
        vd = repo / rung["verify_dir"]
        cands = wbf.load_candidates_as_gdf(vd / "crops/candidate_manifest.json",
                                           vd / "probabilities.json")
        for kind in ("opmax", "carried"):
            pt = rung[kind]
            sub = cands[(cands["vote_count"] >= pt["vote_t"])
                        & (cands["mound_probability"] >= pt["prob_t"])].reset_index(drop=True)
            cell = bl.load_detections(repo / pt["detections"], board)
            tree = cKDTree(np.c_[sub.geometry.x, sub.geometry.y])
            dist, idx = tree.query(np.c_[cell.geometry.x, cell.geometry.y])
            origin_names = sub["source_tile"].iloc[idx].to_numpy()
            origin = np.array([map_of(v) for v in origin_names], dtype=object)
            rekey = np.array([map_of(v) for v in cell["source_tile"]], dtype=object)
            in_frame = np.array([v is not None for v in rekey])
            cross = int(((origin != rekey) & in_frame).sum())
            restored = cell.copy()
            restored["source_tile"] = origin_names
            scoped, diag = bl.geometric_detection_scope(restored, board)
            committed = bl.LIB.calculate_f1_internal(cell, ref, board, buffer_metres=20)
            origin_geo = bl.LIB.calculate_f1_internal(scoped, ref, board, buffer_metres=20)
            rec = {
                "K": rung["K"], "point": kind, "vote_t": pt["vote_t"], "prob_t": pt["prob_t"],
                "detections": pt["detections"], "n": len(cell),
                "max_match_distance_m": float(dist.max()),
                "n_null_after_rekey": int((~in_frame).sum()),
                "n_rekeyed_to_other_sheet": cross,
                "n_out_of_frame_origin_names": diag["n_out_of_frame"],
                "f1_committed_scope": committed[2], "recall_committed_scope": committed[1],
                "precision_committed_scope": committed[0],
                "f1_origin_sheet_geometric": origin_geo[2],
                "recall_origin_sheet_geometric": origin_geo[1],
                "precision_origin_sheet_geometric": origin_geo[0],
            }
            out.append(rec)
            print(f"K={rec['K']} {kind}: n {rec['n']}; null {rec['n_null_after_rekey']}; "
                  f"re-keyed to another sheet {cross}; committed-scope F1 {committed[2]:.4f} "
                  f"(R {committed[1]:.4f}); origin-sheet + geometric F1 {origin_geo[2]:.4f} "
                  f"(R {origin_geo[1]:.4f})")
    for label, det_path, manifest in EXTRA:
        mf = json.loads((repo / manifest).read_text())["candidates"]
        xy = np.array([[c["centroid_x"], c["centroid_y"]] for c in mf])
        names = np.array([c.get("source_tile", "") for c in mf], dtype=object)
        cell = bl.load_detections(repo / det_path, board)
        dist, idx = cKDTree(xy).query(np.c_[cell.geometry.x, cell.geometry.y])
        origin = np.array([map_of(v) for v in names[idx]], dtype=object)
        rekey = np.array([map_of(v) for v in cell["source_tile"]], dtype=object)
        in_frame = np.array([v is not None for v in rekey])
        cross = int(((origin != rekey) & in_frame).sum())
        restored = cell.copy()
        restored["source_tile"] = names[idx]
        scoped, diag = bl.geometric_detection_scope(restored, board)
        committed = bl.LIB.calculate_f1_internal(cell, ref, board, buffer_metres=20)
        origin_geo = bl.LIB.calculate_f1_internal(scoped, ref, board, buffer_metres=20)
        rec = {"cell": label, "detections": det_path, "n": len(cell),
               "max_match_distance_m": float(dist.max()),
               "n_null_after_rekey": int((~in_frame).sum()),
               "n_rekeyed_to_other_sheet": cross,
               "n_out_of_frame_origin_names": diag["n_out_of_frame"],
               "f1_committed_scope": committed[2], "recall_committed_scope": committed[1],
               "f1_origin_sheet_geometric": origin_geo[2],
               "recall_origin_sheet_geometric": origin_geo[1]}
        out.append(rec)
        print(f"{label}: n {len(cell)}; max match {dist.max():.3f} m; re-keyed to another "
              f"sheet {cross}; committed-scope F1 {committed[2]:.4f} (R {committed[1]:.4f}); "
              f"origin-sheet + geometric F1 {origin_geo[2]:.4f} (R {origin_geo[1]:.4f})")
    args.out.write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
