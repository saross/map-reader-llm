"""Compare the 'examples' arrays of configs at two git revisions."""

import json
import subprocess
import sys

a, b = sys.argv[1], sys.argv[2]
files = subprocess.run(
    ["git", "ls-tree", "--name-only", a, "prompts/configs/"], capture_output=True, text=True
).stdout.split()
for f in files:
    if not f.endswith(".json"):
        continue

    def load(rev):
        r = subprocess.run(["git", "show", f"{rev}:{f}"], capture_output=True, text=True)
        return json.loads(r.stdout) if r.returncode == 0 else None

    x, y = load(a), load(b)
    if y is None:
        print(f"{f}: absent at {b[:9]}")
        continue
    ex_x = [e["path"] for e in x.get("examples", [])]
    ex_y = [e["path"] for e in y.get("examples", [])]
    print(
        f"{f}: n={len(ex_x)} examples_identical={ex_x == ex_y}"
        + ("" if ex_x == ex_y else f" NOW n={len(ex_y)}")
    )
