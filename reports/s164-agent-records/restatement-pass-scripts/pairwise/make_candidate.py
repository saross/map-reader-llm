#!/usr/bin/env python3
"""Reduce one candidate copy to the L1 layout and export the candidate tree.

In runs/<X>/repo (a disposable clone after run_candidate.sh):
  1. every modified tracked file is classified against HEAD;
  2. a per-pair file under results/pairwise/{20m,30m}/group_1_architecture/
     or results/pairwise/leaderboard-{20m,30m}/group_8/ that reads the
     single-pass arm (study outputs/retest/h11-single-pass-384-t0) is moved
     to results/rescore-2026-10-15/pairwise/<dir>/<same path> and the HEAD
     (March) file restored at its path;
  3. any other file equal to HEAD after dropping `timestamp` keys and
     replacing the run root is restored to HEAD byte for byte;
  4. the rest stay changed in place.
The README is copied beside. The candidate tree (only files to copy in) is
written to runs/<X>/candidate/ with candidate-files.tsv listing every
decision. Writes nothing outside runs/<X>/.

Usage: make_candidate.py <lane dir> <X> <readme template>
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

lane, X, readme = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3])
R = lane / "runs" / X / "repo"
OUT = lane / "runs" / X / "candidate"
BESIDE = Path("results/rescore-2026-10-15/pairwise")
ROOTS = [str(R) + "/", "/home/shawn/Code/map-reader-llm/"]
DRIFT = "outputs/retest/h11-single-pass-384-t0"
DRIFT_DIRS = {"20m": "group_1_architecture", "30m": "group_1_architecture",
              "leaderboard-20m": "group_8", "leaderboard-30m": "group_8"}


def git(*a, text=True):
    """Run git in the copy and return stdout."""
    return subprocess.run(["git", "-C", str(R), *a], check=True, capture_output=True,
                          text=text).stdout


def norm(o):
    """Drop `timestamp` keys and replace run roots."""
    if isinstance(o, dict):
        return {k: norm(v) for k, v in o.items() if k != "timestamp"}
    if isinstance(o, list):
        return [norm(v) for v in o]
    if isinstance(o, str):
        for r in ROOTS:
            o = o.replace(r, "<ROOT>/")
    return o


def reproduces(rel):
    """True if the working file equals HEAD after normalisation."""
    head = git("show", f"HEAD:{rel}", text=False)
    cur = (R / rel).read_bytes()
    if head == cur:
        return True
    if rel.endswith(".json"):
        return norm(json.loads(head)) == norm(json.loads(cur))
    h, c = head.decode(), cur.decode()
    for r in ROOTS:
        h, c = h.replace(r, "<ROOT>/"), c.replace(r, "<ROOT>/")
    return h == c


def drifted(rel):
    """True if rel is a per-pair file whose arm reads the single-pass study."""
    p = Path(rel)
    parts = p.parts
    if len(parts) != 5 or parts[:2] != ("results", "pairwise"):
        return False
    if DRIFT_DIRS.get(parts[2]) != parts[3]:
        return False
    d = json.loads((R / rel).read_text())
    return any(d[s]["source"].get("study_dir", "").rstrip("/").endswith(DRIFT)
               for s in ("condition_a", "condition_b"))


status = git("status", "--porcelain", "--untracked-files=all").splitlines()
unexpected = [s for s in status if not s.startswith(" M ")]
if unexpected:
    sys.exit(f"unexpected status lines: {unexpected[:10]}")
rows = []
for line in status:
    rel = line[3:]
    if drifted(rel):
        dest = BESIDE / Path(rel).relative_to("results/pairwise")
        (R / dest).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(R / rel), str(R / dest))
        git("checkout", "HEAD", "--", rel)
        rows.append(("kept-march", rel))
        rows.append(("beside", str(dest)))
    elif reproduces(rel):
        git("checkout", "HEAD", "--", rel)
        rows.append(("reproduces-restored", rel))
    else:
        rows.append(("changed-in-place", rel))
shutil.copy(readme, R / BESIDE / "README.md")
rows.append(("beside-readme", str(BESIDE / "README.md")))
if OUT.exists():
    shutil.rmtree(OUT)
for kind, rel in rows:
    if kind in ("changed-in-place", "beside", "beside-readme"):
        (OUT / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(R / rel, OUT / rel)
(lane / "runs" / X / "candidate-files.tsv").write_text(
    "".join(f"{k}\t{r}\n" for k, r in sorted(rows)))
from collections import Counter  # noqa: E402
c = Counter((k, "/".join(Path(r).parts[:3])) for k, r in rows)
for (k, d), n in sorted(c.items()):
    print(f"{k:22s} {d:45s} {n}")
