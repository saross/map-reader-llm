"""The D51 gate over the fourteen Phase 2 ladders, before and after D57 (3).

Runs the gate exactly as ``scripts/build_k_ladder_phase2_tables.py`` would
(``build()`` then ``apply_area_gate``, unclipped, allowing undetermined
rungs, one ladder at a time — the method of the PR #26 survey,
``reports/scorer-frames-d50-d51-2026-10-08-scripts/ladders_new.py``) under
two declarations files:

* ``before`` — the base branch's declarations (the three legacy unions
  PR #26 declared), so the code change alone moves nothing;
* ``after`` — the declarations with Task A's tilings and Task B's pools.

Validation (``validation``): every declared route must reproduce the area
the gate already determines through recorded provenance. With the meta
reader disabled (``pass_manifest`` returns ``None``, so no pass can use its
meta's manifest) and a scratch declarations file holding the tilings
``t07_tilings.py`` identified for the K = 1 / K = 3 passes of the nine
determinable ladders, and the pool declarations ``rebuild_pools.py``
reproduced for their K = 1 / K = 3 pools, each of those eighteen pools'
declared-route area must equal its recorded-route area (symmetric
difference at most 1e-6 km²).

Independent cross-check (``independent``): for every rung of the thirteen
pv-diag-384 ladders after the change, the area recomputed without the
library — the union of the 487-tile polygons of every tile any of the
rung's first-K passes lists in ``processed_tiles``, intersected with the
board frame — must equal the gate's effective area.

Usage (sapphire)::

    PYTHONDONTWRITEBYTECODE=1 ~/Code/map-reader-llm/.venv/bin/python gate_survey.py \
        --code ~/worktrees/map-reader-llm/claude-d51-ladder-provenance \
        --base-declarations ~/scratch/d51-ladder-provenance-2026-10-08/base-declarations.json \
        --validation-tilings ~/scratch/d51-ladder-provenance-2026-10-08/validation-tilings.json \
        --rebuild out/rebuild_pools.json --out out/gate_survey.json

Created: 2026-10-08 (D57 (3), Session 163 follow-up)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

BOARD = "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"
TILING = "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
#: The nine ladders whose K = 1 / K = 3 rungs the gate determined before D57 (3)
#: (PR #26 survey, ``ladders_new.json`` → ``phase2_gate_survey``).
DETERMINABLE_POOLS = {
    "flash-minimal-text-n30-t07-text-t0.3", "flash-minimal-text-n30-t07-text-t1.0",
    "flash-high-text-n5-text-t0.3", "flash-high-text-n5-text-t1.0",
    "image-n5-image-t0.3", "image-n5-image-t1.0",
    "flash-high-image-n5-image-t0.3", "flash-high-image-n5-image-t1.0",
    "scale-4-optimal-487",
}


def survey(tables: Any, laa: Any, declarations: Path) -> list[dict[str, Any]]:
    """Run the gate over every Phase 2 ladder under one declarations file."""
    laa.DECLARATIONS_PATH = declarations
    laa.clear_declaration_caches()
    payload = tables.build()
    rows = []
    for ladder in payload["ladders"]:
        one = {"ladders": [copy.deepcopy(ladder)]}
        messages = tables.apply_area_gate(one, allow_undetermined=True)
        record = one["ladders"][0].get("assessed_area") or {}
        rows.append({
            "family": ladder["family"], "pool": ladder["proposer_pool"],
            "status": record.get("status") or ("refused" if messages else None),
            "common_area_km2": record.get("common_area_km2"),
            "max_excess_km2": record.get("max_excess_km2"),
            "undetermined": record.get("undetermined"),
            "pools": [{k: p.get(k) for k in ("label", "union", "method", "area_km2",
                                             "effective_area_km2",
                                             "excess_over_common_km2", "reason",
                                             "warnings")}
                      for p in record.get("pools", [])],
            "messages": messages,
        })
        print(declarations.name, ladder["proposer_pool"], rows[-1]["status"],
              rows[-1]["max_excess_km2"], flush=True)
    return rows


def validation(code: Path, tables: Any, laa: Any, tilings: Path, rebuild: dict,
               scratch: Path) -> list[dict[str, Any]]:
    """Declared-route areas against recorded-route areas on known rungs."""
    # Only the ladders whose K = 1 / K = 3 areas the gate determined BEFORE
    # D57 (3) — the T 0.7 ladders' rungs now depend on Task A's own
    # declarations, so they cannot validate it.
    pools = [row for row in rebuild["rows"]
             if row["role"] == "validation" and row["merger"] == "april"
             and row["pool"] in DETERMINABLE_POOLS]
    tiling_entries = json.loads(tilings.read_text())["pass_tilings"]
    declared_pools = []
    for row in pools:
        if not row["exact"]:
            continue
        declared_pools.append({
            "schema": laa.RECORD_SCHEMA, "pool": row["union"],
            "pass_provenance": [{"pass_id": Path(p).parent.name, "path": p,
                                 "git_blob_hash": laa.git_blob_hash(code / p)}
                                for p in row["read_order"]],
            "evidence": ["validation only (scratch)"]})
    validation_file = scratch / "validation-declarations.json"
    validation_file.write_text(json.dumps({"pass_tilings": tiling_entries,
                                           "declarations": declared_pools}, indent=1))
    frame = laa.frame_union(BOARD)
    out = []
    determinable = {e["pool"] for e in declared_pools}
    for row in pools:
        # Recorded route: the committed declarations, the meta reader on.
        laa.DECLARATIONS_PATH = code / "inputs/provenance/assessed-area-declarations.json"
        laa.clear_declaration_caches()
        recorded = laa.determine_assessed_area(row["union"], label="recorded")
        # Declared route: scratch declarations, the meta reader off.
        laa.DECLARATIONS_PATH = validation_file
        laa.clear_declaration_caches()
        original = laa.pass_manifest
        laa.pass_manifest = lambda _path: None
        try:
            declared = laa.determine_assessed_area(row["union"], label="declared")
        finally:
            laa.pass_manifest = original
        entry = {"pool": row["pool"], "K": row["K"], "union": row["union"],
                 "rebuild_exact": row["exact"], "recorded_method": recorded.method,
                 "declared_method": declared.method,
                 "declared_reason": declared.reason}
        if recorded.determined and declared.determined:
            sym = recorded.geometry.symmetric_difference(declared.geometry).area / 1e6
            entry.update({
                "recorded_effective_km2": round(recorded.geometry.intersection(frame).area
                                                / 1e6, 4),
                "declared_effective_km2": round(declared.geometry.intersection(frame).area
                                                / 1e6, 4),
                "symmetric_difference_km2": sym,
                "reproduces": sym <= 1e-6 and declared.method == laa.METHOD_DECLARED,
            })
        else:
            entry["reproduces"] = False
        entry["declared_in_scratch"] = row["union"] in determinable
        out.append(entry)
        print("validate", row["pool"], row["K"], entry["reproduces"], flush=True)
    laa.DECLARATIONS_PATH = code / "inputs/provenance/assessed-area-declarations.json"
    laa.clear_declaration_caches()
    return out


def independent(code: Path, after: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Each rung's area recomputed from processed_tiles without the library."""
    import geopandas as gpd  # noqa: PLC0415

    tiles = gpd.read_file(code / TILING).to_crs(32635).set_index("tile_name")
    frame = gpd.read_file(code / BOARD).to_crs(32635).geometry.union_all()
    out = []
    for ladder in after:
        if ladder["pool"] == "g384_ov192_g37":
            continue
        for pool in ladder["pools"]:
            union = code / pool["union"]
            k = int(pool["label"].split("=")[1])
            cell = union.parent.parent
            names: set[str] = set()
            for n in range(1, k + 1):
                for f in (cell / f"run_{n}").glob("*.geojson"):
                    if ".meta" not in f.name:
                        names |= set(json.loads(f.read_text()).get("processed_tiles") or [])
            area = tiles.loc[sorted(names)].geometry.union_all().intersection(frame).area / 1e6
            out.append({"pool": ladder["pool"], "K": k,
                        "independent_effective_km2": round(area, 4),
                        "gate_effective_km2": pool["effective_area_km2"],
                        "agrees": pool["effective_area_km2"] is not None
                        and abs(round(area, 4) - pool["effective_area_km2"]) < 1e-4})
    return out


def main() -> int:
    """Survey before and after, validate, cross-check, and write the JSON."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--base-declarations", type=Path, required=True)
    ap.add_argument("--validation-tilings", type=Path, required=True)
    ap.add_argument("--rebuild", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    code = args.code.expanduser().resolve()
    sys.path.insert(0, str(code))
    import scripts.build_k_ladder_phase2_tables as tables  # noqa: PLC0415
    import scripts.lib_assessed_area as laa  # noqa: PLC0415

    result: dict[str, Any] = {
        "before": survey(tables, laa, args.base_declarations.expanduser().resolve()),
        "after": survey(tables, laa, code / "inputs/provenance/"
                        "assessed-area-declarations.json"),
    }
    result["validation"] = validation(
        code, tables, laa, args.validation_tilings.expanduser().resolve(),
        json.loads(args.rebuild.read_text()), args.validation_tilings.parent)
    result["independent"] = independent(code, result["after"])
    result["checks"] = {
        "validation_all_reproduce": all(v["reproduces"] for v in result["validation"]),
        "n_validation": len(result["validation"]),
        "independent_all_agree": all(r["agrees"] for r in result["independent"]),
        "n_independent": len(result["independent"]),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, default=str) + "\n")
    print(json.dumps(result["checks"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
