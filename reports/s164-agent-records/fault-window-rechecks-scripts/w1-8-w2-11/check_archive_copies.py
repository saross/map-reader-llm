#!/usr/bin/env python3
"""
Check the 2026-09-08 rebuilds' archive copies and e7ebc1695's vote-4 claim.

Fault-window re-check (2026-10-14), row W2-11. Each 2026-09-08 rebuild
(185681674, e01b8617a, c053f5a41, e7ebc1695) archived the files it replaced
under archive/pre-recovery-2026-09-08/. An archive copy is exact when its
blob equals the source file's blob at the commit's parent. Also tests
e7ebc1695's statement that the rebuilt WBF candidates at vote >= 4 are
feature-for-feature identical to the unchanged wbf_vote4.geojson, using the
regenerated wbf_candidates.geojson.

Usage: python check_archive_copies.py REPO REGEN_WBF_CANDIDATES OUT_JSON

Author: Claude (Opus 5.5) for Shawn Ross; Licence: Apache 2.0
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

A = "archive/pre-recovery-2026-09-08"
#: commit -> [(archive dir, source dir at the parent)]
MOVES = {
    "185681674": [(f"{A}/n1-outstanding-384__pro-image-high-t0__consensus",
                   "outputs/h11/n1-outstanding-384/pro-image-high-t0/consensus"),
                  (f"{A}/n1-outstanding-384__pro-text-high-t0__consensus",
                   "outputs/h11/n1-outstanding-384/pro-text-high-t0/consensus")],
    "e01b8617a": [(f"{A}/e47-propose-brief__propose_brief-text__consensus",
                   "outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text/consensus")],
    "c053f5a41": [(f"{A}/h12-v2__r3-hp-heavy__run3-meta", "outputs/h12-v2/r3-hp-heavy/run_3")],
    "e7ebc1695": [(f"{A}/h12-v2__r3-hp-heavy__consensus", "outputs/h12-v2/greedy/r3-hp-heavy"),
                  (f"{A}/h12-v2__r3-hp-heavy__wbf", "outputs/h12-v2/wbf/r3-hp-heavy")],
}


def git(repo: str, *a: str) -> str:
    """git stdout, stripped ('' on failure)."""
    r = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def main() -> int:
    """Run both checks."""
    repo, regen_wbf, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    rows = []
    for c, moves in MOVES.items():
        for adir, sdir in moves:
            for name in git(repo, "ls-tree", "--name-only", f"{c}:{adir}").split():
                a = git(repo, "rev-parse", f"{c}:{adir}/{name}")
                s = git(repo, "rev-parse", f"{c}^:{sdir}/{name}")
                rows.append({"commit": c, "archive": f"{adir}/{name}", "source": f"{sdir}/{name}",
                             "exact": bool(a) and a == s})
    vote4 = json.loads(git(repo, "show",
                           "e7ebc1695:outputs/h12-v2/wbf/r3-hp-heavy/wbf_vote4.geojson"))
    cands = json.loads(Path(regen_wbf).read_text())
    key = "vote_count" if "vote_count" in cands["features"][0]["properties"] else None
    sel = [f for f in cands["features"] if key and f["properties"].get(key, 0) >= 4]
    same = [json.dumps(f, sort_keys=True) for f in sel] == \
           [json.dumps(f, sort_keys=True) for f in vote4["features"]]
    res = {"archive_copies": len(rows), "archive_exact": sum(r["exact"] for r in rows),
           "not_exact": [r for r in rows if not r["exact"]],
           "vote4": {"vote_key": key, "n_regen_vote_ge_4": len(sel),
                     "n_committed_vote4": len(vote4["features"]),
                     "features_identical_in_order": same}}
    out.write_text(json.dumps({"summary": res, "rows": rows}, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
