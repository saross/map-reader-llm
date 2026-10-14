"""Test whether a regenerated JSON differs from the committed one ONLY in order and named leaves.

Usage: python w1-4_conform_check.py REGENERATED.json COMMIT:PATH [KEY,KEY,...]

For the class B pool steps (compute-pairwise-effect-sizes.py and
consensus-sweep-phase3a-high-text.py gather results in worker-completion
order). The regenerated object is conformed to the committed one: dict keys
put in committed order, lists of {"comparison": ...} rows aligned by that
name, and the value of each named KEY (run metadata such as elapsed time and
worker count) replaced by the committed value. It is then serialised the way
the producer writes (json.dump, indent 2) and compared byte for byte with the
committed file. Prints True/False and the keys substituted with both values.
"""
import json
import subprocess
import sys
from pathlib import Path

GIT = str(Path.home() / "scratch/s164-fw-recheck-2026-10-14/wt")
new = json.loads(Path(sys.argv[1]).read_text())
old_raw = subprocess.run(["git", "-C", GIT, "show", sys.argv[2]], capture_output=True, text=True,
                         check=True).stdout
old = json.loads(old_raw)
subst = set(sys.argv[3].split(",")) if len(sys.argv) > 3 and sys.argv[3] else set()
log = []


def conform(n, o, path=""):
    if isinstance(n, dict) and isinstance(o, dict):
        if set(n) != set(o):
            log.append(f"key sets differ at {path or '/'}")
            return n
        out = {}
        for k in o:
            if k in subst:
                if n[k] != o[k]:
                    log.append(f"substituted {path}/{k}: "
                               f"regenerated {n[k]!r} -> committed {o[k]!r}")
                out[k] = o[k]
            else:
                out[k] = conform(n[k], o[k], f"{path}/{k}")
        return out
    if isinstance(n, list) and isinstance(o, list) and len(n) == len(o):
        if n and all(isinstance(i, dict) and "comparison" in i for i in n + o):
            idx = {i["comparison"]: i for i in n}
            if len(idx) == len(n) and set(idx) == {i["comparison"] for i in o}:
                if [i["comparison"] for i in n] != [i["comparison"] for i in o]:
                    log.append(f"list re-aligned by 'comparison' at {path}")
                return [conform(idx[i["comparison"]], i, f"{path}[{i['comparison']}]") for i in o]
        return [conform(a, b, f"{path}[{j}]") for j, (a, b) in enumerate(zip(n, o))]
    return n


c = conform(new, old)
order_changed = list(new) != list(old) or json.dumps(new) != json.dumps(c)
out = json.dumps(c, indent=2)
same = out == old_raw or out + "\n" == old_raw
print(f"{sys.argv[2]}: byte-identical after conforming: {same}; order differed: {order_changed}")
for line in log:
    print("   " + line)
