"""Recompute the G3 arm 2 inheritance agreement block; diff it with ladder.json (throwaway).

Run from the scratch clone (after-state legs in place). Prints the leaf
fields of ladder.json arms.arm2.<k>.agreement / ambiguity that differ.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import scripts.gemini37_image_55map_r2 as r2  # noqa: E402,F401
from scripts.modality_bridge_stage2_checks import diff_paths  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "inheritance_ladder",
    ROOT / "results/gemini37-image-55map-2026-09-13/inheritance-2026-09-20/inheritance_ladder.py")
inh = importlib.util.module_from_spec(spec)
sys.modules["inheritance_ladder"] = inh
spec.loader.exec_module(inh)
inh.bind_campaign("g3")
ladder = json.loads((inh.HOME / "ladder.json").read_text())
for k in (1, 3):
    inherited, own, rec = inh.inherit("arm2", k)
    rec["agreement"] = inh.agreement(inherited, own, "arm2", k)
    committed = ladder["arms"]["arm2"][str(k)]
    new = json.loads(json.dumps({key: rec[key] for key in committed if key in rec}))
    old = {key: committed[key] for key in new}
    paths = diff_paths(old, new)
    print(f"arm2 K{k}: {len(paths)} differing field(s)")

    def get(d, p):
        for part in p.replace("[", ".[").split("."):
            if part.startswith("["):
                d = d[int(part[1:-1])]
            elif part:
                d = d[part]
        return d
    for p in paths:
        print(f"  {p}: {get(old, p)} -> {get(new, p)}")
