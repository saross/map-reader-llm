#!/usr/bin/env python3
"""
kl_s9_compare.py -- S164 restatement pass, K-ladder lane, part 1 step 4.

Purpose:
    Compare the eight re-scored S9 cells (1) run A against run B, file by
    file, normalising only timestamps and each run's own root path (and the
    Markdown ``**Generated**`` line); (2) each against the S9 sweep's own full
    replay (``~/scratch/s164-s9-sweep-2026-10-14/runs/s1-A/cells``): every
    ``summary`` and ``per_run`` leaf exactly; (3) each against
    ``records/movers.json`` (F1, P, R at 20 and 50 m, detection count, scope
    counts, MCC point); and (4) list the leaves that moved against the
    committed file.

Usage:
    python kl_s9_compare.py <cloneA> <cloneB> <s9_run_cells_root> <movers.json> <cmds.tsv>

Author: Claude (Opus 5.5) for Shawn Ross, S164 restatement pass, 2026-10-15.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

A, B, S9, MOVERS, CMDS = (Path(x).resolve() for x in sys.argv[1:6])
cells = [line.split("\t")[0] for line in CMDS.read_text().splitlines()]
movers = {m["eval"]: m for m in json.loads(MOVERS.read_text())}
VOLATILE = {"generated_at_utc", "generated_at", "timestamp"}


def flat(obj, prefix=""):
    """Flatten JSON to {path: value}."""
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flat(v, f"{prefix}/{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flat(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out


def norm(d: dict, root: Path) -> dict:
    """Drop volatile keys and rewrite the run root."""
    out = {}
    for k, v in flat(d).items():
        if k.rsplit("/", 1)[-1] in VOLATILE:
            continue
        if isinstance(v, str):
            v = v.replace(str(root), "<ROOT>")
        out[k] = v
    return out


report = {"cells": {}}
for cell in cells:
    rec: dict = {}
    ja = json.loads((A / cell / "evaluation.json").read_text())
    jb = json.loads((B / cell / "evaluation.json").read_text())
    na, nb = norm(ja, A), norm(jb, B)
    rec["A_vs_B_json_diff"] = sorted(k for k in set(na) | set(nb) if na.get(k) != nb.get(k))
    rec["A_vs_B_csv_identical"] = ((A / cell / "evaluation.csv").read_bytes()
                                   == (B / cell / "evaluation.csv").read_bytes())
    gen = re.compile(r"^\*\*Generated\*\*.*$", re.M)
    ma = gen.sub("", (A / cell / "evaluation.md").read_text()).replace(str(A), "<ROOT>")
    mb = gen.sub("", (B / cell / "evaluation.md").read_text()).replace(str(B), "<ROOT>")
    rec["A_vs_B_md_identical_bar_generated"] = ma == mb
    # Against the S9 sweep's full replay: summary and per_run, exactly.
    js = json.loads((S9 / cell / "evaluation.json").read_text())
    fa = {k: v for k, v in flat({"summary": ja["summary"], "per_run": ja.get("per_run")}).items()}
    fs = {k: v for k, v in flat({"summary": js["summary"], "per_run": js.get("per_run")}).items()}
    fa = {k: v for k, v in fa.items() if k.rsplit("/", 1)[-1] not in VOLATILE}
    fs = {k: v for k, v in fs.items() if k.rsplit("/", 1)[-1] not in VOLATILE}
    rec["vs_S9_replay_summary_per_run_diff"] = sorted(k for k in set(fa) | set(fs)
                                                     if fa.get(k) != fs.get(k))
    rec["n_leaves_compared_vs_S9"] = len(fa)
    # Against movers.json.
    m = movers[f"{cell}/evaluation.json"]
    s = ja["summary"]
    bufs = {int(b["buffer_metres"]): b for b in s["buffers"]}
    tc = s.get("tile_classification") or {}
    mcc = tc.get("mcc")
    mcc_point = mcc.get("point") if isinstance(mcc, dict) else mcc
    checks = {
        "f1_20": (bufs[20]["f1"], m["at20"][1]["f1"]),
        "precision_20": (bufs[20]["precision"], m["at20"][1]["precision"]),
        "recall_20": (bufs[20]["recall"], m["at20"][1]["recall"]),
        "f1_50": (bufs[50]["f1"], m["at50"][1]["f1"]),
        "precision_50": (bufs[50]["precision"], m["at50"][1]["precision"]),
        "recall_50": (bufs[50]["recall"], m["at50"][1]["recall"]),
        "n_detections": (s.get("n_detections"), m["n_det"][1]),
        "mcc_point": (mcc_point, m["mcc_point"][1]),
    }
    scope = s.get("detection_scope") or {}
    for key, val in (m.get("scope") or {}).items():
        if key in ("origin_columns",):
            continue
        checks[f"scope/{key}"] = (scope.get(key), val)
    rec["vs_movers"] = {k: {"ours": a, "movers": b, "equal": a == b}
                        for k, (a, b) in checks.items()}
    rec["vs_movers_all_equal"] = all(v["equal"] for v in rec["vs_movers"].values())
    rec["tile_withheld"] = tc.get("withheld")
    # Against the committed file (HEAD).
    com = json.loads(subprocess.run(["git", "-C", str(A), "show", f"HEAD:{cell}/evaluation.json"],
                                    capture_output=True, text=True, check=True).stdout)
    fc = flat({"summary": com["summary"]})
    fn = flat({"summary": ja["summary"]})
    rec["vs_committed_summary_leaves_changed"] = sum(1 for k in set(fc) | set(fn)
                                                     if fc.get(k) != fn.get(k))
    rec["committed_f1_20"] = next(b["f1"] for b in com["summary"]["buffers"]
                                  if int(b["buffer_metres"]) == 20)
    rec["new_f1_20"] = bufs[20]["f1"]
    rec["script_git_commit"] = ja["_metadata"].get("script_git_commit")
    rec["script_git_status"] = ja["_metadata"].get("script_git_status")
    report["cells"][cell] = rec
report["all_A_eq_B"] = all(not r["A_vs_B_json_diff"] and r["A_vs_B_csv_identical"]
                           and r["A_vs_B_md_identical_bar_generated"]
                           for r in report["cells"].values())
report["all_eq_S9_replay"] = all(not r["vs_S9_replay_summary_per_run_diff"]
                                 for r in report["cells"].values())
report["all_eq_movers"] = all(r["vs_movers_all_equal"] for r in report["cells"].values())
print(json.dumps(report, indent=1, default=str))
