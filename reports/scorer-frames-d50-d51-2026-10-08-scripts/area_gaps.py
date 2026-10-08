"""What lies in the area one rung assessed and a sibling did not.

D50/D51 impact measurement, 2026-10-08 (Session 163). Read-only.

The D51 gate survey (``ladders_new.py``) refused five Phase 2 ladders on
determined areas. For the four ``pv-diag-384`` families among them the K = 1
rung's single pass assessed less of the board frame than the K = 3 rung. This
script names the tiles involved (processed by some K = 3 pass, by no K = 1
pass) and counts the board-frame reference mounds lying in each gap — the
mounds the smaller rung could not have found, which its evaluation books as
false negatives. It does the same for the 3.7 GS ladder's 37.94 km² band.

Usage::

    PYTHONDONTWRITEBYTECODE=1 ~/Code/map-reader-llm/.venv/bin/python area_gaps.py \
        --code WORKTREE --survey out/ladders_new.json --out out/area_gaps.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import meas_lib as ml  # noqa: E402

BOARD = "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"
GT = "inputs/vectors/references/mounds-reference.geojson"


def processed(code: Path, union: str) -> set[str]:
    """Every tile any pass of a consensus union processed (its pass provenance)."""
    from scripts.lib_advanced_metrics import read_processed_tiles  # noqa: PLC0415

    summary = json.loads((code / union).parent.joinpath("voting_summary.json").read_text())
    tiles: set[str] = set()
    for entry in summary["pass_provenance"]:
        tiles |= read_processed_tiles(code / entry["path"]) or set()
    return tiles


def main() -> int:
    """Measure each refused ladder's gap."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--survey", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    code = args.code.expanduser().resolve()
    ml.setup(code)
    import scripts.build_k_ladder_phase2_tables as tables  # noqa: PLC0415
    import scripts.lib_assessed_area as laa  # noqa: PLC0415

    board = laa.frame_union(BOARD)
    ref = ml.load_geojson(code / GT)
    in_board = ref[ref.intersects(board)]
    survey = json.loads(args.survey.read_text())["phase2_gate_survey"]
    out: list[dict[str, Any]] = []
    for fam in survey:
        if fam["status"] != "refused":
            continue
        pools = {**tables.new_rung_pools(fam["pool"]),
                 **tables.committed_sibling_pools(fam["pool"])}
        areas = {k: laa.determine_assessed_area(p, label=f"K = {k}") for k, p in pools.items()}
        determined = {k: a for k, a in areas.items() if a.determined}
        common = None
        for a in determined.values():
            eff = a.geometry.intersection(board)
            common = eff if common is None else common.intersection(eff)
        rec: dict[str, Any] = {"pool": fam["pool"], "rungs": {}}
        for k, a in sorted(determined.items()):
            gap = a.geometry.intersection(board).difference(common)
            refs_in_gap = in_board[in_board.intersects(gap)]
            rec["rungs"][k] = {"gap_km2": round(gap.area / 1e6, 4),
                               "board_refs_in_gap": int(len(refs_in_gap)),
                               "method": a.method}
        if 1 in pools and 3 in pools and areas[1].determined and areas[3].determined \
                and areas[1].method == laa.METHOD_PASS_PROVENANCE:
            k1, k3 = processed(code, pools[1]), processed(code, pools[3])
            rec["tiles_k3_not_k1"] = sorted(k3 - k1)
            rec["tiles_k1_not_k3"] = sorted(k1 - k3)
        out.append(rec)
        print(json.dumps(rec), flush=True)
    args.out.write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
