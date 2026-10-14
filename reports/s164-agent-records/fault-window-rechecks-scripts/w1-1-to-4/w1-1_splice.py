"""W1-1 splice: carry over the two blocks the original commit kept (5986316b5).

Replays, in the replay tree at 7aef6d2ff, the two in-session splices of
2026-10-05 (Session 161 transcript, 07:10:31Z and 07:14:53Z): the
`conditions` block of verifier_analysis.json and the `verifier_costing`
block of grid_analysis.json are taken from the committed HEAD versions, in
committed key order, with the committed indent and trailing newline. Run
from the replay tree's root after w1-1_regen.sh.
"""
import json
import subprocess

# verifier_analysis.json: every key only in the committed file (07:10:31Z)
rel = "results/grid-2026-08-18/verifier_analysis.json"
raw = subprocess.run(["git", "show", "HEAD:" + rel], capture_output=True, text=True,
                     check=True).stdout
old = json.loads(raw)
new = json.load(open(rel))
missing = [k for k in old if k not in new]
print("keys only in committed:", missing)
for k in missing:
    new[k] = old[k]
ordered = {k: new[k] for k in old}
ordered.update({k: v for k, v in new.items() if k not in ordered})
indent = 2 if raw.startswith("{\n  \"") else 1
open(rel, "w").write(json.dumps(ordered, indent=indent) + ("\n" if raw.endswith("\n") else ""))
print(rel, "indent", indent)

# grid_analysis.json: verifier_costing from the committed file (07:14:53Z)
rel = "results/grid-2026-08-18/grid_analysis.json"
raw = subprocess.run(["git", "show", "HEAD:" + rel], capture_output=True, text=True,
                     check=True).stdout
old = json.loads(raw)
new = json.load(open(rel))
new["verifier_costing"] = old["verifier_costing"]
indent = 2 if raw.startswith("{\n  \"") else 1
open(rel, "w").write(json.dumps({k: new[k] for k in list(old) + [k for k in new if k not in old]},
                                indent=indent) + ("\n" if raw.endswith("\n") else ""))
print(rel, "indent", indent)
