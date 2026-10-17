"""Re-materialise the committed cells that read the re-verified legs (scratch only).

Run from the root of a SCRATCH clone. Writes each cell's detections.geojson
in place with the campaign scripts' own functions (rung_frame, inherit,
materialise, to_file), at the operating point recorded in the committed
sweeps.json / cells_manifest.json. ``git status`` then shows which cells'
detections changed. Prints one JSON line per cell.

Usage (cwd = scratch clone): python rematerialise_cells.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import scripts.gemini37_image_55map_r2 as r2  # noqa: E402


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def point_str(p: float, v: int) -> str:
    return f"({float(p):.2f}, k{int(v)})"


out = []
# --- Gemini 3 image campaign, arm 2 cells (own legs) -----------------------
r2.select_campaign("g3")
sweeps = json.loads((r2.RESULTS_HOME / "sweeps.json").read_text())["rungs"]
manifest = json.loads((r2.RESULTS_HOME / "cells_manifest.json").read_text())["cells"]
frames = {}
for c in manifest:
    if c["arm"] != "arm2":
        continue
    rung = sweeps[c["rung"]]
    label = c["label"]
    if label.endswith("-mcc-oracle-unconstrained"):
        pt = rung["mcc_argmax_unconstrained"]
        p, v = pt["prob_t"], pt["min_votes"]
    elif label.endswith("-mcc-oracle"):
        pt = rung["mcc_argmax_at_carried_k"]
        p, v = pt["prob_t"], pt["min_votes"]
    elif label.endswith("-f1-oracle"):
        p, v = rung["f1_oracle"]["prob_t"], rung["f1_oracle"]["min_votes"]
    elif label.endswith("-carried"):
        p, v = rung["carried_point"]
    else:
        raise SystemExit(f"unknown basis: {label}")
    if point_str(p, v) != c["point"]:
        raise SystemExit(f"{label}: sweeps point {point_str(p, v)} != manifest {c['point']}")
    k = c["k"]
    if k not in frames:
        frames[k] = r2.rung_frame("arm2", k)
    sub = r2.materialise(frames[k], float(p), int(v))
    dest = ROOT / c["det"]
    sub.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
    out.append({"label": label, "point": [p, v], "n_committed": c["n_detections"],
                "n_now": int(len(sub))})

# --- Gemini 3 image inheritance study, arm 2 cells (read verify_k5_arm2) ---
inh = load(ROOT / "results/gemini37-image-55map-2026-09-13/inheritance-2026-09-20/"
           "inheritance_ladder.py", "inheritance_ladder")
inh.bind_campaign("g3")
inh_manifest = json.loads((inh.HOME / "cells_manifest.json").read_text())["cells"]
for c in inh_manifest:
    if c["arm"] != "arm2":
        continue
    k = c["k"]
    inherited, _own, _rec = inh.inherit("arm2", k)
    p, v = inh.carried_point("arm2", k)
    if point_str(p, v) != c["point"]:
        raise SystemExit(f"{c['label']}: carried {point_str(p, v)} != manifest {c['point']}")
    sub = inh.materialise(inherited, float(p), int(v))
    dest = ROOT / c["det"]
    sub.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
    out.append({"label": c["label"], "point": [p, v], "n_committed": c["n_detections"],
                "n_now": int(len(sub))})

for row in out:
    print(json.dumps(row))
