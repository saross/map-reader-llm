"""W2.3 step 1: enumerate replicate sets (arms.json flags) down to pass files.

Read-only. For every arm carrying a replicate-group flag in
reports/manipulation-check-2026-10-05-arms.json, resolve its pass detection
GeoJSONs from the meta paths (one per run directory; Batch chunks of one pass
are unioned), and find the ground truth / bounds its scored conditions used.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path.home() / "Code/map-reader-llm"
sys.path.insert(0, str(REPO / "scripts"))
from lib_detection_paths import find_pass_geojsons, pass_identity  # noqa: E402

arms = json.loads((REPO / "reports/manipulation-check-2026-10-05-arms.json").read_text())["arms"]
conds = json.loads((REPO / "results/run-conditions.json").read_text())["decomposition"]

groups = defaultdict(list)
for a in arms:
    for f in a.get("flags", []):
        m = re.match(r"replicate-group-(\d+)", f)
        if m:
            groups[int(m.group(1))].append(a)


def scoring_scope(run_id, pool):
    """GT/bounds recorded by evals of conditions built on this pool."""
    out = set()
    for c in conds.get(run_id, {}).get("conditions", []):
        if c.get("proposer_pool") != pool:
            continue
        if not c.get("eval_path"):
            continue
        ep = REPO / c["eval_path"]
        if not ep.exists():
            continue
        meta = json.loads(ep.read_text()).get("_metadata", {})
        cli = meta.get("cli_args") or {}
        inf = meta.get("input_files") or {}
        gt = cli.get("ground_truth") or inf.get("ground_truth")
        bd = cli.get("bounds") or inf.get("bounds")
        out.add((c["architecture"], gt, bd))
    return sorted(out, key=str)


result = {}
for g in sorted(groups):
    members = []
    for a in groups[g]:
        meta_dirs = sorted({Path(p).parent for p in a["meta_paths"]}, key=str)
        # arms.json lists at most 12 meta paths per arm, so expand to the
        # pool: every numeric run_<N> directory under the meta dirs' parent.
        parents = sorted({d.parent for d in meta_dirs if re.match(r"run_\d+$", d.name)}, key=str)
        if len(parents) == 1 and all(re.match(r"run_\d+$", d.name) for d in meta_dirs):
            run_dirs = sorted((d.relative_to(REPO) for d in (REPO / parents[0]).glob("run_*")
                               if re.match(r"run_\d+$", d.name)),
                              key=lambda d: int(d.name.split("_")[1]))
        else:
            run_dirs = meta_dirs
        passes = []
        problems = []
        for rd in run_dirs:
            files = find_pass_geojsons(REPO / rd)
            if not files:
                problems.append(f"no pass file in {rd}")
                continue
            ids = defaultdict(list)
            for f in files:
                ids[pass_identity(f)].append(str(f.relative_to(REPO)))
            if len(ids) > 1:
                problems.append(f"{rd}: {len(ids)} distinct pass identities {sorted(ids)}")
            for ident, fl in sorted(ids.items()):
                passes.append({"run_dir": str(rd), "identity": ident, "files": sorted(fl)})
        members.append({
            "run_id": a["run_id"], "arm": a["arm"], "n_metas": a["n_metas"],
            "manifest": a.get("manifest_paths"), "items": a.get("items_processed"),
            "signatures": list(a["signatures"].keys()),
            "flags": a["flags"], "passes": passes, "problems": problems,
            "pool_parents": [str(x) for x in parents],
            "scoring_scope": scoring_scope(a["run_id"], a["arm"]),
        })
    result[g] = members

out = Path("/tmp/w2/replicate_sets.json")
out.write_text(json.dumps(result, indent=1))
for g, mem in result.items():
    print("GROUP", g)
    for m in mem:
        print("  ", m["run_id"], m["arm"], "n_metas", m["n_metas"], "passes:", len(m["passes"]), "problems:", m["problems"][:2], m["pool_parents"])
