#!/usr/bin/env python3
"""Compare a candidate e45_bootstrap_pairings.json with the trial prediction.

Usage: cmp_e45.py <candidate json> <trial-e45.json>
"""
import json
import sys

c = json.load(open(sys.argv[1]))
t = json.load(open(sys.argv[2]))
bad = 0
for h in ("H2", "H3"):
    g = c["results"][h]["reproduction_gate"]
    print(h, "gate:", {k: (v["recomputed"], v["committed"], v["pass"]) for k, v in g.items()})
    for tag, tv in t[h]["bootstrap"].items():
        cv = c["results"][h]["bootstrap"][tag]
        for k, v in tv.items():
            ok = cv[k] == v
            bad += not ok
            print(f"  {h} {tag} {k}: candidate {cv[k]} trial {v} {'OK' if ok else 'DIFF'}")
print("contrasts:", json.dumps(c["contrasts"]["H2"]))
print("MISMATCHES", bad)
