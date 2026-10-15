"""Compare committed (git BASE) and scratch evaluation.json per cell (throwaway).

Usage (cwd = scratch clone): python compare_evals.py BASE cell_dir [cell_dir ...]
Prints one JSON line per cell: n, F1/P/R at 50 m and tile MCC (stored, 4 dp),
the tile confusion, and exact MCC from the confusion, before and after.
"""
import json
import math
import subprocess
import sys
from pathlib import Path


def mcc(c: dict) -> float:
    tp, tn, fp, fn = c["tp"], c["tn"], c["fp"], c["fn"]
    den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return (tp * tn - fp * fn) / den if den else 0.0


def summarise(e: dict) -> dict:
    s = e["summary"]
    b = next(x for x in s["buffers"] if x["buffer_metres"] == 50)
    tc = s["tile_classification"]
    return {"n": s["n_detections"], "f1": b["f1"], "p": b["precision"], "r": b["recall"],
            "mcc": tc["mcc"]["point"], "confusion": tc["confusion"],
            "mcc_exact": round(mcc(tc["confusion"]), 6)}


base = sys.argv[1]
for d in sys.argv[2:]:
    path = Path(d) / "evaluation.json"
    before = json.loads(subprocess.run(["git", "show", f"{base}:{path}"], check=True,
                                       capture_output=True, text=True).stdout)
    after = json.loads(path.read_text())
    sb, sa = summarise(before), summarise(after)
    same = all(sb[k] == sa[k] for k in ("n", "f1", "p", "r", "mcc", "confusion"))
    print(json.dumps({"cell": Path(d).name, "identical": same, "before": sb, "after": sa}))
