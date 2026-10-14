#!/usr/bin/env python3
"""W2-2 part (a): cross-read every r2 board cell against the evaluation it cites.

Reads (via ``git show``, read-only) the three r2 boards at BOARD_COMMIT and
the per-cell ``evaluation.json`` files at EVAL_COMMIT, re-derives each cell's
published fields exactly as the builders at 22353e660 derive them
(``final_board_build.eval50``, ``build_55map_leaderboard.main``,
``mcc_tiering_55map._load_cell_inputs``), and reports exact equality per
field. No tolerance: published and re-derived values are both JSON numbers.

Usage: crossread.py <repo> <board_commit> <eval_commit> <out.json>
Author: Claude (Opus 5.5), Session 164 W2-2 re-check sub-agent, 2026-10-14.
"""
import json
import subprocess
import sys

repo, board_c, eval_c, out_path = sys.argv[1:5]
FB = "results/55map-final-board-r2-2026-09-06"
R2 = "results/55maps-r2-ref-2026-09-06"


def show(commit: str, path: str):
    """Return parsed JSON of path at commit, or None if absent."""
    r = subprocess.run(["git", "-C", repo, "show", f"{commit}:{path}"],
                       capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


def eval50(ev: dict) -> dict:
    """Mirror final_board_build.eval50 at 22353e660 (plus mcc CI)."""
    s = ev["summary"]
    b = next(x for x in s["buffers"] if x["buffer_metres"] == 50)
    mcc = s.get("tile_classification", {}).get("mcc")
    out = {"f1_50": b["f1"], "ci": [b["f1_ci_lower"], b["f1_ci_upper"]],
           "precision_50": b["precision"], "recall_50": b["recall"],
           "mcc": mcc.get("point") if isinstance(mcc, dict) else mcc,
           "n_detections": s["n_detections"]}
    if isinstance(mcc, dict):
        out["mcc_ci"] = [mcc.get("ci_lower"), mcc.get("ci_upper")]
    return out


report = {"board_commit": board_c, "eval_commit": eval_c, "boards": {}}
CARRIED = {"TH7-k4", "T03-k4", "TM-k4", "IM-k4"}

# ---- Final board: tiered cells and (if present) addendum cells. ----
fb = show(board_c, f"{FB}/final_board_50m.json")
rows = []
for section in ("cells", "addendum_cells"):
    for c in fb.get(section, []):
        lab = c["label"]
        path = (f"{R2}/{lab}/evaluation.json" if lab in CARRIED
                else f"{FB}/cells/{lab}/evaluation.json")
        ev = show(eval_c, path)
        if ev is None:
            rows.append({"section": section, "label": lab, "eval": path,
                         "status": "EVAL MISSING"})
            continue
        d = eval50(ev)
        keys = ["f1_50", "ci", "precision_50", "recall_50", "mcc",
                "n_detections"] + (["mcc_ci"] if "mcc_ci" in c else [])
        diffs = {k: [c.get(k), d.get(k)] for k in keys if c.get(k) != d.get(k)}
        rows.append({"section": section, "label": lab, "eval": path,
                     "status": "EQUAL" if not diffs else "DIFF", "diffs": diffs})
report["boards"]["final_board_50m.json"] = rows

# ---- F1 leaderboard: each cell's register condition -> eval_path. ----
lb = show(board_c, "results/55map-leaderboard/55map_leaderboard_50m_r2.json")
rc = show("22353e660", "results/run-conditions.json")["decomposition"]
rows = []
for c in lb["cells"]:
    run, label = c["condition_id"].split("::")
    cond = next(x for x in rc[run]["conditions"] if x["label"] == label)
    ev = show(eval_c, cond["eval_path"])
    d = eval50(ev)
    keys = ["f1_50", "ci", "precision_50", "recall_50", "mcc", "n_detections"]
    diffs = {k: [c.get(k), d.get(k)] for k in keys if c.get(k) != d.get(k)}
    rows.append({"label": c["name"], "eval": cond["eval_path"],
                 "status": "EQUAL" if not diffs else "DIFF", "diffs": diffs})
report["boards"]["55map_leaderboard_50m_r2.json"] = rows

# ---- MCC board: each cell's condition_dir/evaluation.json. ----
mb = show(board_c, "results/metric-leaderboards/55map-mcc-tiering-r2.json")
rows = []
for c in mb["cells"]:
    path = f"{c['condition_dir']}/evaluation.json"
    tc = show(eval_c, path)["summary"]["tile_classification"]
    d = {"mcc": tc["mcc"]["point"],
         "mcc_ci": [tc["mcc"]["ci_lower"], tc["mcc"]["ci_upper"]],
         "sensitivity": tc["sensitivity"]["point"],
         "specificity": tc["specificity"]["point"],
         "confusion": {k: tc["confusion"][k] for k in ("tp", "tn", "fp", "fn")}}
    pub = {"mcc": c["mcc"], "mcc_ci": c["mcc_ci"],
           "sensitivity": c["sensitivity"], "specificity": c["specificity"],
           "confusion": c["confusion"]}
    diffs = {k: [pub[k], d[k]] for k in d if pub[k] != d[k]}
    rows.append({"label": c["name"], "eval": path,
                 "status": "EQUAL" if not diffs else "DIFF", "diffs": diffs})
report["boards"]["55map-mcc-tiering-r2.json"] = rows

summary = {b: {"n": len(r), "equal": sum(x["status"] == "EQUAL" for x in r),
               "other": [x for x in r if x["status"] != "EQUAL"]}
           for b, r in report["boards"].items()}
report["summary"] = summary
with open(out_path, "w") as fh:
    json.dump(report, fh, indent=1)
for b, s in summary.items():
    print(f"{b}: {s['equal']}/{s['n']} cells equal")
    for x in s["other"]:
        print("   ", json.dumps(x)[:400])
