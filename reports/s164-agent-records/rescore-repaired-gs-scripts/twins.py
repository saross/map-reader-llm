#!/usr/bin/env python3
"""
Compare each grid-common uplift twin with its cell's sweep row at prob_t 0.

Part of the S164 re-score. A verified cell's pre-verifier twin in
``verifier-uplift.csv`` is the cell's union at the same vote threshold with no
verifier filter. The regenerated sweeps' row at ``prob_t = 0.0`` and the same
``min_votes`` is that set scored on the origin route (PR #42), independent of
the verifier, so it shows whether the committed twin values (scored before
PR #42) move. Prints committed twin, the committed sweep row, and each copy's.

Usage: python twins.py <repo_root_for_git> <copy> [<copy> ...]
       python twins.py <repo_root_for_git> --json <copy> <out.json>
         (the origin-route twin F1 and tile MCC per verified condition, for uplift.py)

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""
import csv
import io
import subprocess
import sys
from pathlib import Path

REPO = sys.argv[1]
JSON_OUT = None
if sys.argv[2] == "--json":
    COPIES, JSON_OUT = [sys.argv[3]], sys.argv[4]
else:
    COPIES = sys.argv[2:]
SWEEPS = {
    "grid-2026-08-18::g512-ov064": ("results/grid-2026-08-18/verifier_sweep.csv", "g512_ov064"),
    "grid-2026-08-18::g512-ov256": ("results/grid-2026-08-18/verifier_sweep.csv", "g512_ov256"),
    "grid-2026-08-18::g384-ov048": ("results/grid-2026-08-18/verifier_sweep.csv", "g384_ov048"),
    "grid-2026-08-18::g384-ov192-k10-verified-p": ("results/grid-2026-08-18/verifier_sweep.csv",
                                                   "g384_ov192"),
    "stride-phaseb-2026-08-25::g512-ov176": ("results/stride-2026-08-25/stride_verifier_sweep.csv",
                                             "g512_ov176"),
    "stride-phaseb-2026-08-25::g384-ov128-k10": (
        "results/stride-2026-08-25/stride_verifier_sweep.csv", "g384_ov128"),
    "stride-phaseb-2026-08-25::g256-ov064": ("results/stride-2026-08-25/stride_verifier_sweep.csv",
                                             "g256_ov064"),
    "stride-phaseb-2026-08-25::g512-ov320": ("results/stride-2026-08-25/stride_verifier_sweep.csv",
                                             "g512_ov320"),
    "stride-phasec-2026-08-25::g384-ov240": ("results/stride-2026-08-25/stride_verifier_sweep.csv",
                                             "g384_ov240"),
    "image-b-gs-2026-08-28::g384-ov192-image-min": ("results/image-b-gs-2026-08-28/sweep_20m.csv",
                                                    None),
    "image-b-gs-2026-08-28::g384-ov192-image-high": (
        "results/image-b-gs-2026-08-28/high/sweep_20m.csv", None),
    "gemini37-screen-2026-08-28::g37-text-k5-verified-carried": (
        "results/gemini37-screen-2026-08-28/sweep_20m.csv", None),
    "gemini37-screen-2026-08-28::g37-text-k10": (
        "results/gemini37-screen-2026-08-28/k10/sweep_20m.csv", None),
    "gemini37-screen-2026-08-28::g37-text-k5-verified-swap37": (
        "results/gemini37-screen-2026-08-28/swap37/sweep_20m.csv", None),
    "gemini37-screen-2026-08-28::g37-text-k5-verified-swap38": (
        "results/gemini38-screen-2026-09-04/armV/sweep_20m.csv", None),
    "gemini37-image-gs-2026-09-01::g37-image-k5-verified-carried": (
        "results/gemini37-image-gs-2026-09-01/arm1/sweep_20m.csv", None),
    "gemini37-image-gs-2026-09-01::g37-image-k5-verified-swap37": (
        "results/gemini37-image-gs-2026-09-01/arm2/sweep_20m.csv", None),
    "grid-2026-08-18::g384-ov192-k10-verified37": (
        "results/gemini37-fourth-cell/gs-leg/sweep_20m.csv", None),
}


def rows_of(text, cell):
    rows = list(csv.DictReader(io.StringIO(text)))
    return [r for r in rows if cell is None or r["cell"] == cell]


def at(rows, k, col="f1"):
    hit = [r for r in rows if float(r["prob_t"]) == 0.0 and int(r["min_votes"]) == k]
    if not hit or hit[0].get(col) in (None, ""):
        return None
    return float(hit[0][col])


TWINS = {}


uplift = subprocess.run(["git", "-C", REPO, "show",
                         "origin/main:results/uplift-supplement/verifier-uplift.csv"],
                        capture_output=True, text=True, check=True).stdout
print("verified cell | k | committed twin | committed sweep(0,k) | " + " | ".join(COPIES))
for r in csv.DictReader(io.StringIO(uplift)):
    if r["frame_id"] != "grid-common-487":
        continue
    key = next((k for k in SWEEPS if r["verified_condition_id"].startswith(k)), None)
    if key is None:
        continue
    rel, cell = SWEEPS[key]
    k = int(r["min_votes"])
    committed = subprocess.run(["git", "-C", REPO, "show", f"origin/main:{rel}"],
                               capture_output=True, text=True, check=True).stdout
    vals = [at(rows_of(committed, cell), k)]
    for c in COPIES:
        rows = rows_of((Path(c) / rel).read_text(), cell)
        vals.append(at(rows, k))
        if r["unverified_condition_id"] == "":
            TWINS[r["verified_condition_id"]] = {"f1": at(rows, k), "mcc": at(rows, k, "mcc")}
    print(r["verified_condition_id"].split("::")[1], k, r["unverified_value"],
          *[None if v is None else round(v, 4) for v in vals], sep=" | ")

if JSON_OUT:
    import json
    Path(JSON_OUT).write_text(json.dumps(TWINS, indent=1) + "\n")
