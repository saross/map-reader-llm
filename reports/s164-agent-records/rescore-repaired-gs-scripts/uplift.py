#!/usr/bin/env python3
"""
Recompute the verifier-uplift summary with the re-scored verified cells.

Part of the S164 re-score. ``verifier-uplift-pairing`` (signed) pairs each of
170 verified cells with its pre-verifier twin; 21 of them are the gold-standard
grid-common cells the wrong-sheet legs feed (grid, stride, winner ladder,
Image-B, Gemini 3.7/3.8 screen, fourth cell, 3.7 image arms). This replaces,
for those 21 rows only, the verified value with the value at the cell's
REGISTERED operating point read off one copy's regenerated sweep
(``extract.py`` ``regpoint/...``; F1 at 4 dp as ``conditions.csv`` holds it,
tile MCC likewise), and the one regenerated twin (the grid 384/50 K = 10
consensus condition, moved by PR #42), then recomputes the statistics the
register outcome quotes. Every other twin and row is as committed: none reads
a verifier leg.

Usage: python uplift.py <committed_f1_csv> <committed_mcc_csv> <extract.json> <out.json>
                         [<twins.json>]

With ``twins.json`` (``twins.py --json``), every twin that is its cell's union at
the same vote threshold is also replaced by that set scored on the origin route
(the regenerated sweep's ``prob_t = 0`` row), the reading PR #42's fix implies
for the twins, which were scored before it.

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""
import csv
import json
import statistics
import sys

VERIFIED = {
    "grid-2026-08-18::g512-ov064-k10-verified-p0.15-k5": "grid/g512_ov064",
    "grid-2026-08-18::g512-ov256-k10-verified-p0.15-k9": "grid/g512_ov256",
    "grid-2026-08-18::g384-ov048-k10-verified-p0.20-k7": "grid/g384_ov048",
    "grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10": "grid/g384_ov192",
    "grid-2026-08-18::g384-ov192-k10-verified37-p0.98-k10": "g37/fourth_cell",
    "stride-phaseb-2026-08-25::g512-ov176-k10-verified-p0.15-k6": "stride/g512_ov176",
    "stride-phaseb-2026-08-25::g384-ov128-k10-verified-p0.15-k8": "stride/g384_ov128",
    "stride-phaseb-2026-08-25::g256-ov064-k10-verified-p0.15-k8": "stride/g256_ov064",
    "stride-phaseb-2026-08-25::g512-ov320-k10-verified-p0.15-k10": "stride/g512_ov320",
    "stride-phasec-2026-08-25::g384-ov240-k10-verified-p0.15-k10": "stride/g384_ov240",
    "image-b-gs-2026-08-28::g384-ov192-image-min-k10-verified-p0.15-k9": "image_b/min",
    "image-b-gs-2026-08-28::g384-ov192-image-high-k10-verified-p0.20-k8": "image_b/high",
    "gemini37-screen-2026-08-28::g37-text-k5-verified-carried-p0.10-k5": "g37/k5",
    "gemini37-screen-2026-08-28::g37-text-k10-verified-carried-p0.10-k10": "g37/k10",
    "gemini37-screen-2026-08-28::g37-text-k5-verified-swap37-p0.80-k5": "g37/swap37",
    "gemini37-screen-2026-08-28::g37-text-k5-verified-swap38-p0.88-k5": "g38/armv",
    "gemini37-image-gs-2026-09-01::g37-image-k5-verified-carried-p0.10-k5": "g37img/arm1",
    "gemini37-image-gs-2026-09-01::g37-image-k5-verified-swap37-p0.90-k5": "g37img/arm2",
}
#: The winner-ladder rungs: their registered point is the exact ladder's best,
#: read from the regenerated evaluation (the ladder's points are N-specific).
LADDER = {
    f"stride-phaseb-2026-08-25::g384-ov128-ladder-n{n}-verified-p0.15-k{k}":
        f"stride/g384_ov128-ladder-n{n}"
    for n, k in ((1, 1), (3, 3), (5, 4))
}
TWIN = {"grid-2026-08-18::g384-ov192-k10-c2-k10": "grid/condition/g384_ov192"}

f1_csv, mcc_csv, ext_path, out_path = sys.argv[1:5]
ext = json.load(open(ext_path))
twins = json.load(open(sys.argv[5])) if len(sys.argv) > 5 else {}


def summary(rows):
    """The register outcome's statistics over the computed rows."""
    vals = [float(r["uplift"]) for r in rows if r["uplift"] not in ("", None)]
    by_frame = {}
    for r in rows:
        if r["uplift"] in ("", None):
            continue
        by_frame.setdefault(r["frame_id"], []).append(float(r["uplift"]))
    return {"n": len(vals), "median": round(statistics.median(vals), 4),
            "min": round(min(vals), 4), "max": round(max(vals), 4),
            "n_negative": sum(v < 0 for v in vals),
            "by_frame": {f: {"n": len(v), "median": round(statistics.median(v), 4)}
                         for f, v in sorted(by_frame.items())}}


def rescore(path, metric):
    rows = list(csv.DictReader(open(path)))
    changed = {}
    for r in rows:
        vid, uid = r["verified_condition_id"], r["unverified_condition_id"]
        new_v = None
        if vid in VERIFIED and f"regpoint/{VERIFIED[vid]}" in ext:
            rp = ext[f"regpoint/{VERIFIED[vid]}"]
            new_v = rp["f1"] if metric == "F1" else rp["mcc"]
        elif vid in LADDER and f"eval/{LADDER[vid]}" in ext:
            ev = ext[f"eval/{LADDER[vid]}"]
            new_v = ev["f1"] if metric == "F1" else ev["tile_mcc"]
        new_u = None
        if uid in TWIN and f"{TWIN[uid]}" in ext:
            c = ext[TWIN[uid]]
            new_u = c["rescored_f1_at_20m"] if metric == "F1" else c["tile_mcc"]
        elif uid == "" and vid in twins:
            new_u = twins[vid]["f1" if metric == "F1" else "mcc"]
        if new_v is None and new_u is None:
            continue
        old = (r["verified_value"], r["unverified_value"], r["uplift"])
        if new_v is not None:
            r["verified_value"] = f"{round(new_v, 4)}"
        if new_u is not None:
            r["unverified_value"] = f"{round(new_u, 4)}"
        if r["verified_value"] and r["unverified_value"]:
            r["uplift"] = f"{round(float(r['verified_value']) - float(r['unverified_value']), 4)}"
        changed[vid] = {"before": old, "after": (r["verified_value"], r["unverified_value"],
                                                 r["uplift"])}
    return rows, changed


out = {}
for metric, path in (("F1", f1_csv), ("MCC", mcc_csv)):
    committed = list(csv.DictReader(open(path)))
    rows, changed = rescore(path, metric)
    out[metric] = {"committed": summary(committed), "rescored": summary(rows),
                   "rows_changed": changed}
json.dump(out, open(out_path, "w"), indent=1)
print(json.dumps({m: {k: v for k, v in o.items() if k != "rows_changed"} for m, o in out.items()},
                 indent=1))
