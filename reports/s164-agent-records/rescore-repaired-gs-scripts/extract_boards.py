#!/usr/bin/env python3
"""
Pull the Era-2 board, GS K-ladder, and bridge numbers from one run (or a git ref).

Part of the S164 re-score (``reports/s164-agent-records/rescore-repaired-gs.md``).
The same named quantities are read from the committed files
(``git:<ref>:<repo>``) and from each run's outputs, so the record's tables
and the run A = run B check use identical keys.

Usage::

    python extract_boards.py git:<ref>:<repo> <out.json>
    python extract_boards.py <scratch_root> <run> <out.json>   # e.g. repairedA

For a run, the board and ladders are read from ``<scratch_root>/board/<run>/``
and the bridge from ``<scratch_root>/copies/<run>/results/modality-bridge-2026-10-07``.

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BOARD = "results/leaderboard/era2/gs-era2-verified-board-2026-09-10"
BOARD_ID = "gs-era2-verified-board-2026-09-10"
K = "results/k-ladder-2026-09-12"
BRIDGE = "results/modality-bridge-2026-10-07"
BRIDGE_CELLS = ("g3-text-g3v", "g3-image-g3v", "g37-text-g3v", "g37-text-g37v",
                "g37-image-g3v", "g37-image-g37v", "g37-image-cache-g3v",
                "g37-image-cache-g37v", "g3-text-temp1-g3v", "g3-image-temp1-g3v")
#: The ten Era-2 members downstream of the wrong-sheet legs.
MOVED = (
    "g37-image-k5-verified-carried-p0.10-k5-era2b",
    "g37-image-k5-verified-swap37-p0.90-k5-era2b",
    "g37-text-k10-verified-carried-p0.10-k10-era2b",
    "g37-text-k5-verified-carried-p0.10-k5-era2b",
    "g37-text-k5-verified-swap37-p0.80-k5-era2b",
    "g37-text-k5-verified-swap38-p0.88-k5-era2b",
    "g384-ov192-k10-verified-p0.15-k10-era2b",
    "g384-ov192-k10-verified37-p0.98-k10-era2b",
    "g384-ov192-image-high-k10-verified-p0.20-k8-era2b",
    "g384-ov192-image-min-k10-verified-p0.15-k9-era2b",
)

if sys.argv[1].startswith("git:"):
    _, REF, REPO = sys.argv[1].split(":", 2)
    OUT = sys.argv[2]
    PATHS = {"tiering": f"{BOARD}/tiering_20m.json",
             "mcb_f1": f"{BOARD}/mcb/{BOARD_ID}_b20_m1.json",
             "mcb_mcc": f"{BOARD}/mcb/{BOARD_ID}_mcc_b20_m1.json",
             "lad_a": f"{K}/mcc-test/tiering/gs-stride-a/tiering_20m.json",
             "lad_e": f"{K}/tier-e/tiering/tiering_20m.json",
             "mcb_a_f1": f"{K}/mcb/gs-stride-a/k-ladder-gs-stride-a-2026-09-12_b20_m1.json",
             "mcb_a_mcc": f"{K}/mcb/gs-stride-a/k-ladder-gs-stride-a-2026-09-12_mcc_b20_m1.json",
             "mcb_e_f1": f"{K}/mcb/tier-e/k-ladder-tier-e-2026-09-12_b20_m1.json",
             "mcb_e_mcc": f"{K}/mcb/tier-e/k-ladder-tier-e-2026-09-12_mcc_b20_m1.json",
             "bridge": BRIDGE}

    def load(key, sub=None):
        rel = PATHS[key] if sub is None else f"{PATHS[key]}/{sub}"
        r = subprocess.run(["git", "-C", REPO, "show", f"{REF}:{rel}"], capture_output=True,
                           text=True, check=False)
        return json.loads(r.stdout) if r.returncode == 0 else None
else:
    ROOT, RUN, OUT = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    RUN_DIR = ROOT / "board" / RUN
    PATHS = {"tiering": RUN_DIR / "tiering/tiering_20m.json",
             "mcb_f1": RUN_DIR / f"mcb/{BOARD_ID}_b20_m1.json",
             "mcb_mcc": RUN_DIR / f"mcb/{BOARD_ID}_mcc_b20_m1.json",
             "lad_a": RUN_DIR / "ladders/gs-stride-a-tiering/tiering_20m.json",
             "lad_e": RUN_DIR / "ladders/tier-e-tiering/tiering_20m.json",
             "mcb_a_f1": RUN_DIR / "ladder-mcb/gs-stride-a"
             / "k-ladder-gs-stride-a-2026-09-12_b20_m1.json",
             "mcb_a_mcc": RUN_DIR / "ladder-mcb/gs-stride-a"
             / "k-ladder-gs-stride-a-2026-09-12_mcc_b20_m1.json",
             "mcb_e_f1": RUN_DIR / "ladder-mcb/tier-e/k-ladder-tier-e-2026-09-12_b20_m1.json",
             "mcb_e_mcc": RUN_DIR / "ladder-mcb/tier-e/k-ladder-tier-e-2026-09-12_mcc_b20_m1.json",
             "bridge": ROOT / "copies" / RUN / BRIDGE}

    def load(key, sub=None):
        p = Path(PATHS[key]) if sub is None else Path(PATHS[key]) / sub
        return json.loads(p.read_text()) if p.is_file() else None

out: dict = {}


def tiering(prefix, t, top=None):
    """Counts, tiers, tie set, ranking and (for ladders) every pair."""
    if t is None:
        return
    pw = t["pairwise"]
    out[f"{prefix}/n_pairs"] = len(pw)
    out[f"{prefix}/n_significant"] = sum(bool(p["significant"]) for p in pw)
    out[f"{prefix}/n_tiers"] = len(t["tiers"])
    out[f"{prefix}/tie_set"] = sorted(t["tie_set"])
    out[f"{prefix}/withheld"] = sorted(w.get("label", w.get("ref", "")) for w in
                                       t.get("withheld_cells", []))
    rank = t["ranking"] if top is None else t["ranking"][:top]
    out[f"{prefix}/ranking"] = [[r["label"], r["tier"], round(r["eval_f1"], 4),
                                 r.get("mcc")] for r in rank]
    mp = t.get("mcc_permutation") or {}
    if mp:
        out[f"{prefix}/mcc/n_significant"] = mp.get("n_significant")
        out[f"{prefix}/mcc/n_tiers"] = mp.get("n_tiers")
        out[f"{prefix}/mcc/tie_set_size"] = len(mp.get("tie_set", []))
    if top is None:
        mcc_pw = {(p["ref_a"], p["ref_b"]): p for p in mp.get("pairwise", [])}
        for p in pw:
            a, b = p["ref_a"].split("::")[1], p["ref_b"].split("::")[1]
            m = mcc_pw.get((p["ref_a"], p["ref_b"]), {})
            out[f"{prefix}/pair/{a} vs {b}"] = {
                "f1_a": p["f1_a"], "f1_b": p["f1_b"], "d_f1": p["observed_diff"],
                "p": p["p_value"], "bh": p["bh_adjusted_p"], "sig": p["significant"],
                "d_mcc": m.get("observed_diff"), "p_mcc": m.get("p_value"),
                "bh_mcc": m.get("bh_adjusted_p")}


t = load("tiering")
tiering("era2", t, top=12)
if t is not None:
    for r in t["ranking"]:
        if r["label"] in MOVED:
            out[f"era2/member/{r['label']}"] = {"rank": r["rank"], "tier": r["tier"],
                                                "f1": round(r["eval_f1"], 4), "mcc": r.get("mcc")}
for key, tag in (("mcb_f1", "era2/mcb_f1"), ("mcb_mcc", "era2/mcb_mcc"),
                 ("mcb_a_f1", "ladder_a/mcb_f1"), ("mcb_a_mcc", "ladder_a/mcb_mcc"),
                 ("mcb_e_f1", "ladder_e/mcb_f1"), ("mcb_e_mcc", "ladder_e/mcb_mcc")):
    m = load(key)
    if m is not None:
        out[f"{tag}/n_admissible"] = len(m["hsu_not_ruled_out"])
        out[f"{tag}/admissible"] = sorted(m["candidates"][i]["label"]
                                          for i in m["hsu_not_ruled_out"])
        out[f"{tag}/hsu_w_upper"] = m.get("hsu_w_upper")
tiering("ladder_a", load("lad_a"))
tiering("ladder_e", load("lad_e"))

for cell in BRIDGE_CELLS:
    a = load("bridge", f"{cell}/analysis.json")
    if a is None:
        continue
    b, op = a["image_best"], a.get("operating_point", {})
    out[f"bridge/{cell}"] = {"best_f1": round(b["f1"], 4),
                             "best_point": [b["prob_t"], b["min_votes"]],
                             "op_f1": round(op["f1"], 4) if op else None,
                             "op_mcc": round(op["mcc"], 4) if op and op.get("mcc") else None}
for sub in ("gap_test.json", "k5/gap_test.json", "additions/gap_test.json"):
    g = load("bridge", sub)
    if g is None:
        continue
    for lab, r in g["pairs"].items():
        out[f"bridge/gap/{sub.split('/')[0]}/{lab}"] = {"d": round(r["observed_diff"], 4),
                                                       "p": r["p_value"]}
    for lab, v in (g.get("gap_change") or {}).items():
        out[f"bridge/gapchange/{sub.split('/')[0]}/{lab}"] = round(v, 4)

Path(OUT).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
print(f"{len(out)} keys -> {OUT}")
