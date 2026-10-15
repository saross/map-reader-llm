"""Which phase2 materialised file has no cell (read-only, tree = cwd)."""
import json
import subprocess

m = subprocess.run(["git", "ls-files", "results/k-ladder-2026-09-12/phase2/materialised"],
                   capture_output=True, text=True).stdout.split()
c = subprocess.run(["git", "ls-files", "results/k-ladder-2026-09-12/phase2/cells"],
                   capture_output=True, text=True).stdout.split()
cells = {p.split("/")[4] for p in c}
labels = {p.split("/")[-1][:-8] for p in m}
op = json.load(open("results/k-ladder-2026-09-12/phase2/operating-points.json"))
used = set()
for r in op["rungs"]:
    for pt in ("opmax", "carried"):
        used.add(r[pt]["detections"].split("/")[-1][:-8])
print("materialised not referenced:", sorted(labels - used))
print("referenced, not materialised:", sorted(used - labels))
mapped = {("gemini37-screen-2026-08-28" if lab.startswith("g37") else "pv-diag-384")
          + "__" + lab.replace(".", "_") for lab in labels}
print("materialised without a cell:", sorted(mapped - cells))
print("cell without materialised:", sorted(cells - mapped))
