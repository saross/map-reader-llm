#!/usr/bin/env python3
"""
Re-materialise the 19 grid-common union twins on the origin route (D65 (4)).

Part of the S164 restatement pass (``reports/s164-agent-records/
restatement-pass.md``). ``verifier-uplift-pairing`` pairs each verified cell
with its pre-verifier twin: the cell's union at the same vote threshold, with
no verifier filter. Nineteen of the 21 gold-standard grid-common twins are
such union shells (``pairing_basis = union`` in
``results/uplift-supplement/verifier-pairing-worklist.csv``); the other two
read the registered 384/50 K = 10 consensus condition, which the GS chain
regenerates, and are not touched here.

The committed twins were written by ``scripts/materialise_pairing_twin.py
--union`` from the committed ``union_k<N>.geojson`` files, which record each
cluster's legacy nearest-centroid ``source_tile`` but not the tiles its members
were seen on. Under D50 such a row falls back to the legacy cross-sheet rule,
so a cluster near the Elenovo sheet edge can be scored against the
neighbouring sheet's references. PR #42 (D62 (1)) gave the GS chains the
origin route; the twins were scored before it and never re-scored (the S164
re-score's surprise S3; PI ruling D65 (4)).

What this driver does, per twin, in a disposable copy:

1. Loads the cell's union through the cell's OWN loader, exactly as its GS
   chain does, which rebuilds the clusters from the cell's prepared passes,
   gates the rebuild against the committed union row for row, attaches each
   row's member tiles, and books each row on its own sheet
   (``lib_cluster_origins.union_on_origin``):

   * grid: ``grid_verifier_analysis.load_verified_union`` +
     ``reassignment_gate`` + ``union_on_origin`` with
     ``grid_analysis.load_cell_passes`` (``grid_verifier_analysis.main``);
   * stride and the winner-ladder rungs:
     ``stride_verifier_analysis.load_stride_union_on_origin``;
   * Image-B and the Gemini 3.7 screen and image cells:
     ``image_b_analysis.load_image_union`` + ``reassign_gate`` +
     ``union_on_origin`` with the cell's prepared passes
     (``image_b_analysis.main``; the 3.7 image cell's passes are not tracked
     and must be copied in read only).

2. Re-selects the vote shell ``vote_count >= k`` from the committed union
   file with the committed writer's rule (``build_twin_from_union``) and
   refuses unless it equals the committed twin's features exactly, so the
   only change made is the origin.

3. Writes the twin in the committed format at the committed path: the
   committed document with every feature's geometry and properties kept,
   ``origin_tiles`` (the ``;``-joined member tiles the shared scorer reads,
   ``lib_advanced_metrics.ORIGIN_TILE_COLUMNS``) added, rows the origin route
   drops (on no tile of their own sheet) removed, ``_materialised.n_kept``
   updated only if rows were dropped, and an ``_materialised.origin_route``
   record added. ``source_tile`` is kept as committed unless
   ``--source-tile origin`` is passed, which writes the origin-sheet tile
   the chain books (the choice is recorded in the file).

4. Scores it with ``evaluate_detections.py`` using the committed
   ``evaluation.json``'s own ``_metadata.cli_args`` (bootstrap 10,000, seed
   42, MCC, the twin's buffers), overwriting that directory's evaluation.

A JSON record of every twin (counts, dropped rows, fields changed, F1 at
20 m and tile MCC before and after) is written to ``--record``.

Usage (inside a disposable copy whose root is the repository)::

    python twin_origin_driver.py --repo <copy> --record <out.json>
        [--jobs <verified_condition_id> ...] [--source-tile committed|origin]
        [--bootstrap N]   # testing only; the pass uses the committed value

Zero API. Never run in the shared checkout or a tracked worktree.

Author: Shawn Ross, Claude Code (S164, lane-uplift)
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

WORKLIST = "results/uplift-supplement/verifier-pairing-worklist.csv"
FRAME = "grid-common-487"

#: Loader spec per verified condition id prefix: chain, and its arguments.
#: Grid cells: (cell). Stride: (label, union_name, verify_dir, n_passes).
#: Image chain: (outputs_root, cell, union_name, verify_dir, k) as the GS
#: chain's image_b_analysis.py invocations pass them
#: (reports/s164-agent-records/rescore-repaired-gs-scripts/chain.sh:44-56).
SPECS: dict[str, tuple[str, tuple[Any, ...]]] = {
    "grid-2026-08-18::g512-ov064-k10-verified-p0.15-k5": ("grid", ("g512_ov064",)),
    "grid-2026-08-18::g512-ov256-k10-verified-p0.15-k9": ("grid", ("g512_ov256",)),
    "grid-2026-08-18::g384-ov048-k10-verified-p0.20-k7": ("grid", ("g384_ov048",)),
    "stride-phaseb-2026-08-25::g512-ov176-k10-verified-p0.15-k6":
        ("stride", ("g512_ov176", "union_k10.geojson", "verify", 10)),
    "stride-phaseb-2026-08-25::g384-ov128-k10-verified-p0.15-k8":
        ("stride", ("g384_ov128", "union_k10.geojson", "verify", 10)),
    "stride-phaseb-2026-08-25::g256-ov064-k10-verified-p0.15-k8":
        ("stride", ("g256_ov064", "union_k10.geojson", "verify", 10)),
    "stride-phaseb-2026-08-25::g512-ov320-k10-verified-p0.15-k10":
        ("stride", ("g512_ov320", "union_k10.geojson", "verify", 10)),
    "stride-phasec-2026-08-25::g384-ov240-k10-verified-p0.15-k10":
        ("stride", ("g384_ov240", "union_k10.geojson", "verify", 10)),
    "stride-phaseb-2026-08-25::g384-ov128-ladder-n1-verified-p0.15-k1":
        ("stride", ("g384_ov128", "union_k1.geojson", "verify_k1", 1)),
    "stride-phaseb-2026-08-25::g384-ov128-ladder-n3-verified-p0.15-k3":
        ("stride", ("g384_ov128", "union_k3.geojson", "verify_k3", 3)),
    "stride-phaseb-2026-08-25::g384-ov128-ladder-n5-verified-p0.15-k4":
        ("stride", ("g384_ov128", "union_k5.geojson", "verify_k5", 5)),
    "image-b-gs-2026-08-28::g384-ov192-image-min-k10-verified-p0.15-k9":
        ("image", ("outputs/image-b-gs-2026-08-28", "g384_ov192_image",
                   "union_k10.geojson", "verify", 10)),
    "image-b-gs-2026-08-28::g384-ov192-image-high-k10-verified-p0.20-k8":
        ("image", ("outputs/image-b-gs-2026-08-28", "g384_ov192_image_high",
                   None, "verify", 10)),
    "gemini37-screen-2026-08-28::g37-text-k5-verified-carried-p0.10-k5":
        ("image", ("outputs/gemini37-screen-2026-08-28", "g384_ov192_g37",
                   "union_k5.geojson", "verify", 5)),
    "gemini37-screen-2026-08-28::g37-text-k10-verified-carried-p0.10-k10":
        ("image", ("outputs/gemini37-screen-2026-08-28", "g384_ov192_g37",
                   "union_k10.geojson", "verify_k10", 10)),
    "gemini37-screen-2026-08-28::g37-text-k5-verified-swap37-p0.80-k5":
        ("image", ("outputs/gemini37-screen-2026-08-28", "g384_ov192_g37",
                   "union_k5.geojson", "verify_swap37", 5)),
    "gemini37-screen-2026-08-28::g37-text-k5-verified-swap38-p0.88-k5":
        ("image", ("outputs/gemini37-screen-2026-08-28", "g384_ov192_g37",
                   "union_k5.geojson", "verify_swap38", 5)),
    "gemini37-image-gs-2026-09-01::g37-image-k5-verified-carried-p0.10-k5":
        ("image", ("outputs/gemini37-image-gs-2026-09-01", "g384_ov192_g37img",
                   "union_k5.geojson", "verify_arm1", 5)),
    "gemini37-image-gs-2026-09-01::g37-image-k5-verified-swap37-p0.90-k5":
        ("image", ("outputs/gemini37-image-gs-2026-09-01", "g384_ov192_g37img",
                   "union_k5.geojson", "verify_arm2", 5)),
}


class TwinOriginError(RuntimeError):
    """A gate failed; nothing was written for this twin."""


def load_on_origin(repo: Path, chain: str, args: tuple[Any, ...]):
    """Load one cell's union on the origin route through its chain's loader.

    Returns:
        ``(gdf, union_path, passes_dir, n_passes)``: the union rows with
        ``origin_tiles`` and an origin-sheet ``source_tile`` (index = the
        union row), the union file read, the prepared-passes directory, and
        the number of passes the union was rebuilt from.
    """
    import geopandas as gpd

    from scripts.grid_analysis import load_cell_passes
    from scripts.lib_cluster_origins import union_on_origin

    if chain == "grid":
        from scripts import grid_verifier_analysis as gva
        (cell,) = args
        bounds = gpd.read_file(gva.COMMON_BOUNDS)
        gdf = gva.load_verified_union(cell)
        gdf = gva.reassignment_gate(gdf, bounds, cell)
        gdf = union_on_origin(gdf, load_cell_passes(gva.SCORING_DIR, cell), bounds,
                              label=cell, n_passes=gva.K_TOTAL)
        return (gdf, gva.VERIFIER_DIR / cell / "union_k10.geojson", gva.SCORING_DIR,
                gva.K_TOTAL)
    if chain == "stride":
        from scripts import stride_verifier_analysis as sva
        label, union_name, verify_dir, n_passes = args
        bounds = gpd.read_file(sva.COMMON_BOUNDS)
        gdf = sva.load_stride_union_on_origin(label, bounds, union_name=union_name,
                                              verify_dir=verify_dir, n_passes=n_passes)
        root = sva.PROJECT_ROOT / sva.STRIDE_CELLS[label][0]
        return gdf, root / "verifier" / label / union_name, root / "scoring", n_passes
    if chain == "image":
        from scripts import image_b_analysis as iba
        outputs_root, cell, union_name, verify_dir, k = args
        vroot = iba.PROJECT_ROOT / outputs_root / "verifier" / cell
        scoring = iba.PROJECT_ROOT / outputs_root / "scoring"
        bounds = gpd.read_file(iba.COMMON_BOUNDS)
        iba.CELL = cell  # the module reads its cell label in gate messages
        gdf = iba.load_image_union(vroot, union_name, verify_dir)
        gdf = iba.reassign_gate(gdf, bounds, cell)
        passes = load_cell_passes(scoring, cell, n_passes=k)
        gdf = union_on_origin(gdf, passes, bounds, label=cell, n_passes=k)
        if union_name is None:
            found = sorted(vroot.glob("union_k*.geojson"))
            union_path = found[0]
        else:
            union_path = vroot / union_name
        return gdf, union_path, scoring, k
    raise ValueError(f"unknown chain {chain!r}")


def eval_point(evaluation: dict[str, Any]) -> dict[str, Any]:
    """F1 at 20 m, tile MCC point and detection count of an evaluation."""
    summary = evaluation["summary"]
    b20 = next(b for b in summary["buffers"] if int(b["buffer_metres"]) == 20)
    mcc = (summary.get("tile_classification") or {}).get("mcc")
    if isinstance(mcc, dict):
        mcc = mcc.get("point")
    return {"f1_20": b20["f1"], "tile_mcc": mcc, "n_detections": summary.get("n_detections")}


def command_from_cli_args(cli: dict[str, Any], python: str, script: Path,
                          bootstrap: int | None) -> list[str]:
    """Rebuild an ``evaluate_detections.py`` command from recorded ``cli_args``."""
    cmd = [python, str(script)]
    for key, value in cli.items():
        if key == "bootstrap" and bootstrap is not None:
            value = bootstrap
        if value is None or value is False:
            continue
        flag = "--" + key.replace("_", "-")
        if value is True:
            cmd.append(flag)
        elif isinstance(value, list):
            cmd += [flag, *[str(v) for v in value]]
        else:
            cmd += [flag, str(value)]
    return cmd


def run_one(repo: Path, row: dict[str, str], source_tile_mode: str,
            bootstrap: int | None) -> dict[str, Any]:
    """Re-materialise and re-score one twin. Returns its record."""
    t0 = time.time()
    vid = row["verified_condition_id"]
    chain, args = SPECS[vid]
    k = int(row["min_votes"])
    out_dir = repo / row["output_dir"]
    twin_paths = sorted(out_dir.glob("twin-*.geojson"))
    if len(twin_paths) != 1:
        raise TwinOriginError(f"{vid}: expected one committed twin file, found {twin_paths}")
    twin_path = twin_paths[0]
    committed = json.loads(twin_path.read_text(encoding="utf-8"))
    eval_path = out_dir / "evaluation.json"
    committed_eval = json.loads(eval_path.read_text(encoding="utf-8"))
    before = eval_point(committed_eval)

    gdf, union_path, passes_dir, n_passes = load_on_origin(repo, chain, args)
    rel_union = str(union_path.relative_to(repo))
    if rel_union != row["union_path"]:
        raise TwinOriginError(f"{vid}: loader read {rel_union}, worklist names {row['union_path']}")
    if committed["_materialised"]["source_union"] != row["union_path"]:
        raise TwinOriginError(f"{vid}: committed twin's source_union differs from the worklist")

    # The committed writer's selection, re-done from the committed union file.
    from scripts.materialise_pairing_twin import build_twin_from_union
    union = json.loads(union_path.read_text(encoding="utf-8"))
    shell, _stats = build_twin_from_union(union, k)
    if shell != committed["features"]:
        raise TwinOriginError(f"{vid}: the committed twin is not the union's vote >= {k} shell")
    kept_rows = [i for i, f in enumerate(union["features"])
                 if f["properties"]["vote_count"] >= k]
    if len(kept_rows) != len(shell):
        raise TwinOriginError(f"{vid}: shell row count mismatch")

    features: list[dict[str, Any]] = []
    dropped: list[int] = []
    tile_rekeyed = 0
    for row_index, feature in zip(kept_rows, shell, strict=True):
        if row_index not in gdf.index:
            dropped.append(row_index)
            continue
        on_origin = gdf.loc[row_index]
        if int(on_origin["vote_count"]) != int(feature["properties"]["vote_count"]):
            raise TwinOriginError(f"{vid}: row {row_index} vote_count differs on origin")
        properties = dict(feature["properties"])
        properties["origin_tiles"] = on_origin["origin_tiles"]
        if on_origin["source_tile"] != properties["source_tile"]:
            tile_rekeyed += 1
            if source_tile_mode == "origin":
                properties["source_tile"] = on_origin["source_tile"]
        features.append({"type": feature["type"], "geometry": feature["geometry"],
                         "properties": properties})
    # Every origin-route row at vote >= k must be in the twin.
    expected = set(gdf.index[gdf["vote_count"] >= k].tolist())
    if expected != {i for i in kept_rows if i not in dropped}:
        raise TwinOriginError(f"{vid}: origin-route shell differs from the committed shell "
                              "minus its dropped rows")

    document = dict(committed)
    materialised = dict(committed["_materialised"])
    fields_changed = ["features[].properties.origin_tiles (added)",
                      "_materialised.origin_route (added)"]
    if dropped:
        materialised["n_kept"] = len(features)
        fields_changed.append(f"_materialised.n_kept {committed['_materialised']['n_kept']}"
                              f" -> {len(features)}")
    if source_tile_mode == "origin" and tile_rekeyed:
        fields_changed.append(f"features[].properties.source_tile ({tile_rekeyed} rows)")
    materialised["origin_route"] = {
        "ruling": "D65 (4); the D62 (1) origin route (PR #42)",
        "library": "scripts/lib_cluster_origins.py union_on_origin",
        "loader": {"grid": "grid_verifier_analysis.load_verified_union + reassignment_gate",
                   "stride": "stride_verifier_analysis.load_stride_union_on_origin",
                   "image": "image_b_analysis.load_image_union + reassign_gate"}[chain],
        "passes_dir": str(passes_dir.relative_to(repo)),
        "n_passes": n_passes,
        "n_dropped_off_origin_sheet": len(dropped),
        "dropped_union_rows": dropped,
        "n_source_tile_off_origin_sheet": tile_rekeyed,
        "source_tile": ("committed (legacy nearest-centroid tile; origin_tiles decides "
                        "the sheet)") if source_tile_mode == "committed"
        else "origin-sheet tile booked by the origin route",
    }
    document["_materialised"] = materialised
    document["features"] = features
    twin_path.write_text(json.dumps(document, indent=1), encoding="utf-8")

    cli = committed_eval["_metadata"]["cli_args"]
    cmd = command_from_cli_args(cli, sys.executable, repo / "scripts/evaluate_detections.py",
                                bootstrap)
    proc = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, check=False)
    record: dict[str, Any] = {
        "verified_condition_id": vid, "twin": str(twin_path.relative_to(repo)),
        "chain": chain, "k": k, "union": rel_union, "n_union": len(union["features"]),
        "n_committed": len(shell), "n_written": len(features), "dropped": dropped,
        "n_source_tile_off_origin_sheet": tile_rekeyed, "fields_changed": fields_changed,
        "evaluate_cmd": cmd[1:], "evaluate_rc": proc.returncode, "before": before,
    }
    if proc.returncode != 0:
        record["evaluate_stderr_tail"] = proc.stderr[-2000:]
    else:
        record["after"] = eval_point(json.loads(eval_path.read_text(encoding="utf-8")))
    record["seconds"] = round(time.time() - t0, 1)
    return record


def main() -> int:
    """Run the selected twins and write the record."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--record", type=Path, required=True)
    ap.add_argument("--jobs", nargs="*", default=None)
    ap.add_argument("--source-tile", choices=("committed", "origin"), default="committed")
    ap.add_argument("--bootstrap", type=int, default=None,
                    help="Override the committed bootstrap count (testing only).")
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    args.record = args.record.expanduser().resolve()
    sys.path.insert(0, str(repo))
    import os
    os.chdir(repo)
    rows = [r for r in csv.DictReader(open(repo / WORKLIST, encoding="utf-8"))
            if r["frame_id"] == FRAME and r["pairing_basis"] == "union"]
    if sorted(r["verified_condition_id"] for r in rows) != sorted(SPECS):
        raise SystemExit("the worklist's grid-common union twins are not the 19 this "
                         "driver knows")
    if args.jobs:
        rows = [r for r in rows if r["verified_condition_id"] in set(args.jobs)]
    records, failures = [], 0
    for row in rows:
        try:
            rec = run_one(repo, row, args.source_tile, args.bootstrap)
        except Exception as exc:  # noqa: BLE001 - recorded, run continues
            rec = {"verified_condition_id": row["verified_condition_id"],
                   "error": f"{type(exc).__name__}: {exc}"}
        failures += int("error" in rec or rec.get("evaluate_rc") != 0)
        records.append(rec)
        print(json.dumps({k: rec.get(k) for k in ("verified_condition_id", "n_written",
                                                   "dropped", "before", "after", "error",
                                                   "seconds")}), flush=True)
    args.record.write_text(json.dumps({"source_tile_mode": args.source_tile,
                                       "bootstrap_override": args.bootstrap,
                                       "n": len(records), "n_failed": failures,
                                       "twins": records}, indent=1) + "\n")
    print(f"DONE {len(records)} twins, {failures} failed", flush=True)
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
