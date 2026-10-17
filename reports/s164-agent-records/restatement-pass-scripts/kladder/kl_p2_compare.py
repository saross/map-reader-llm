#!/usr/bin/env python3
"""
kl_p2_compare.py -- check the K-ladder lane's part 2 candidate trees.

Purpose:
    S164 restatement pass, K-ladder lane, part 2. For clones A and B of
    64382beea after ``kl_p2_run.sh``:

    1. the set of files each run changed or created (git status), which must
       be equal;
    2. A against B, file by file: JSON leaf by leaf with timestamps and each
       run's root path removed; Markdown with its generated-time line removed;
       every other file byte for byte;
    3. every value against its prediction: the 2026-10-13 re-score's REPAIRED
       outputs (``~/scratch/s164-rescore-2026-10-13/board/repairedA``) for the
       five board-frame cells, both tierings and the two-ladder MCB; part 1's
       patched-derivation harness (``p1/hG``) for the 3.7 opmax rungs; the S9
       values for the collected scores; and this lane's inventory values;
    4. that every committed ladder the splices keep is byte-identical.

Usage:
    python kl_p2_compare.py <cloneA> <cloneB> <rescore_board_dir> <p1_hG> > report.json

Author: Claude (Opus 5.5) for Shawn Ross, S164 restatement pass, 2026-10-15.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

A, B, RS, HG = (Path(p).resolve() for p in sys.argv[1:5])
K = "results/k-ladder-2026-09-12"
VOLATILE = {"generated_at_utc", "generated_at", "timestamp"}
GEN_LINE = re.compile(r"^.*(\*\*Generated\*\*|GENERATED FILE|Generated \d{4}-).*$", re.M)


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


def norm_json(path: Path, root: Path) -> dict:
    """Flattened JSON without volatile keys, the run root rewritten."""
    out = {}
    for k, v in flat(json.loads(path.read_text())).items():
        if k.rsplit("/", 1)[-1] in VOLATILE:
            continue
        out[k] = v.replace(str(root), "<ROOT>") if isinstance(v, str) else v
    return out


def changed(root: Path) -> list[str]:
    """Files the run modified or created, relative to the clone."""
    lines = subprocess.run(["git", "-C", str(root), "status", "--porcelain",
                            "--untracked-files=all"], capture_output=True, text=True,
                           check=True).stdout.splitlines()
    return sorted(line[3:] for line in lines)


def committed(root: Path, rel: str) -> dict:
    """A file's committed JSON at HEAD."""
    return json.loads(subprocess.run(["git", "-C", str(root), "show", f"HEAD:{rel}"],
                                     capture_output=True, text=True, check=True).stdout)


rep: dict = {}
ca, cb = changed(A), changed(B)
rep["changed_files_A"] = ca
rep["changed_sets_equal"] = ca == cb

# ---- 2. A against B --------------------------------------------------------
ab = {}
for rel in ca:
    pa, pb = A / rel, B / rel
    if rel.endswith(".json"):
        na, nb = norm_json(pa, A), norm_json(pb, B)
        diff = sorted(k for k in set(na) | set(nb) if na.get(k) != nb.get(k))
        ab[rel] = "identical" if not diff else diff[:10]
    elif rel.endswith(".md"):
        ta = GEN_LINE.sub("", pa.read_text()).replace(str(A), "<ROOT>")
        tb = GEN_LINE.sub("", pb.read_text()).replace(str(B), "<ROOT>")
        ab[rel] = "identical" if ta == tb else "DIFFERS"
    else:
        ab[rel] = "identical" if pa.read_bytes() == pb.read_bytes() else "DIFFERS"
rep["A_vs_B"] = ab
rep["A_vs_B_all_identical"] = all(v == "identical" for v in ab.values())


# ---- 3a. the five board-frame cells against the re-score ------------------
def summary_leaves(path: Path) -> dict:
    """Every summary and per_run leaf of an evaluation, volatile keys dropped."""
    d = json.loads(path.read_text())
    return {k: v for k, v in flat({"summary": d["summary"], "per_run": d.get("per_run")}).items()
            if k.rsplit("/", 1)[-1] not in VOLATILE}


cells = {
    f"{K}/board-frame/stride-phaseb__g384-ov128-{c}/evaluation.json":
        RS / f"ladders/board-frame/stride-phaseb__g384-ov128-{c}/evaluation.json"
    for c in ("ladder-n1", "ladder-n3", "ladder-n5", "k10")}
cells[f"{K}/tier-e/cells/grid-2026-08-18__g384-ov192-k10-verified-p0_15-k10-boardframe/"
      "evaluation.json"] = RS / "ladders/tier-e-k10-boardframe-evaluation.json"
bf = {}
for rel, ref in cells.items():
    mine, theirs = summary_leaves(A / rel), summary_leaves(ref)
    diff = sorted(k for k in set(mine) | set(theirs) if mine.get(k) != theirs.get(k))
    s = json.loads((A / rel).read_text())["summary"]
    b20 = next(b for b in s["buffers"] if int(b["buffer_metres"]) == 20)
    bf[rel.split("/")[-2]] = {"f1_20": b20["f1"], "n": s.get("n_detections"),
                              "mcc": ((s.get("tile_classification") or {}).get("mcc") or {})
                              .get("point"), "leaves": len(mine),
                              "diff_vs_rescore": diff[:10]}
rep["board_frame_cells"] = bf


# ---- 3b. the two tierings against the re-score ----------------------------
def pairs(t: dict, key: str) -> dict:
    """Pair results keyed by the unordered pair of condition ids."""
    rows = t["pairwise"] if key == "f1" else t["mcc_permutation"]["pairwise"]
    out = {}
    for r in rows:
        a = r.get("ref_a") or r.get("a")
        b = r.get("ref_b") or r.get("b")
        diff = r.get("observed_diff", r.get("observed_mcc_diff"))
        out[frozenset((a, b))] = (round(abs(diff), 6), r["p_value"], r["bh_adjusted_p"],
                                  r["significant"])
    return out


def tier_sets(t: dict) -> list:
    """Tier memberships as sets."""
    return sorted(sorted(x["members"]) for x in t["tiers"])


tiers = {}
TIERINGS = (
    (f"{K}/tier-e/tiering/tiering_20m.json", RS / "ladders/tier-e-tiering/tiering_20m.json"),
    (f"{K}/mcc-test/tiering/gs-stride-a/tiering_20m.json",
     RS / "ladders/gs-stride-a-tiering/tiering_20m.json"),
)
for rel, ref in TIERINGS:
    mine, theirs = json.loads((A / rel).read_text()), json.loads(ref.read_text())
    tiers[rel] = {
        "f1_pairs_equal": pairs(mine, "f1") == pairs(theirs, "f1"),
        "mcc_pairs_equal": pairs(mine, "mcc") == pairs(theirs, "mcc"),
        "tiers_equal": tier_sets(mine) == tier_sets(theirs),
        "tie_set_equal": sorted(mine["tie_set"]) == sorted(theirs["tie_set"]),
        "ranking": [(r["label"], r.get("f1"), r["observed_micro_f1"], r["mcc"], r["tier"])
                    for r in mine["ranking"]],
        "pairs_f1": {" vs ".join(sorted(x.split("::")[1] for x in k)): v
                     for k, v in pairs(mine, "f1").items()},
        "pairs_mcc": {" vs ".join(sorted(x.split("::")[1] for x in k)): v
                      for k, v in pairs(mine, "mcc").items()},
    }
# The findings § 6.1 command's output against the MCC test's re-run of it.
t61 = A.parent / "A" / "gs-tiering-61" / "tiering_20m.json"
mine = json.loads((A / f"{K}/mcc-test/tiering/gs-stride-a/tiering_20m.json").read_text())
other = json.loads(t61.read_text())
tiers["s6_1_vs_mcc_test_run"] = {"f1_pairs_equal": pairs(mine, "f1") == pairs(other, "f1"),
                                 "mcc_pairs_equal": pairs(mine, "mcc") == pairs(other, "mcc"),
                                 "ranking_equal": mine["ranking"] == other["ranking"]}
rep["tierings"] = tiers

# ---- 3c. the two-ladder MCB against the re-score; the splice keeps the rest -
mcb_new = json.loads((A / f"{K}/mcb/summary.json").read_text())
mcb_rs = json.loads((RS / "ladder-mcb/summary.json").read_text())
mcb_old = committed(A, f"{K}/mcb/summary.json")
KEYS = ("best_K", "best_statistic", "hsu_admissible_K", "hsu_w_upper", "hsu_w_lower",
        "two_sided_band_K", "theta_by_K", "statistic_by_K", "contains_K3", "excludes_K10",
        "whole_ladder")
mcb = {}
for slug in ("gs-stride-a", "tier-e"):
    n = next(x for x in mcb_new["ladders"] if x["slug"] == slug)
    r = next(x for x in mcb_rs["ladders"] if x["slug"] == slug)
    mcb[slug] = {m: {k: (n[m].get(k), r[m].get(k) == n[m].get(k)) for k in KEYS}
                 for m in ("f1", "mcc")}
    mcb[slug]["gates_passed"] = [g["passed"] for g in n["gates"]]
kept = [x["slug"] for x in mcb_new["ladders"] if x["slug"] not in ("gs-stride-a", "tier-e")]
mcb["other_ladders_identical_to_committed"] = all(
    next(x for x in mcb_new["ladders"] if x["slug"] == s)
    == next(x for x in mcb_old["ladders"] if x["slug"] == s) for s in kept)
mcb["n_kept"] = len(kept)
mcb["roll_up_committed"] = mcb_old["roll_up"]
mcb["roll_up_new"] = mcb_new["roll_up"]
mcb["gate_all_passed"] = mcb_new["gate_all_passed"]
rep["mcb"] = mcb

mcc_new = json.loads((A / f"{K}/mcc-test/summary.json").read_text())
mcc_old = committed(A, f"{K}/mcc-test/summary.json")
rep["mcc_test"] = {
    "gs_entry": next(x for x in mcc_new["ladders"] if x["ladder"] == "gs-stride-a"),
    "gs_entry_committed": next(x for x in mcc_old["ladders"] if x["ladder"] == "gs-stride-a"),
    "others_identical": all(x == y for x, y in zip(mcc_new["ladders"], mcc_old["ladders"],
                                                   strict=True) if x["ladder"] != "gs-stride-a"),
    "gate_all_passed": mcc_new["gate_all_passed"],
}

# ---- 3d. the 3.7 opmax derivation against part 1's patched harness --------
g37 = {}
for rel in sorted(r for r in ca if "/g37-opmax/" in r or r.endswith("g37-opmax-jobs.txt")
                  or "verify_repaired/sweep" in r or "verify_k10_repaired/sweep" in r):
    pa, ph = A / rel, HG / rel
    if not ph.exists():
        g37[rel] = "absent in p1/hG"
    elif rel.endswith("evaluation.json"):
        g37[rel] = "summary equal" if summary_leaves(pa) == summary_leaves(ph) else "DIFFERS"
    elif rel.endswith(".json"):
        g37[rel] = "equal" if norm_json(pa, A) == norm_json(ph, HG) else "DIFFERS"
    elif rel.endswith(".md"):
        g37[rel] = "n/a (render)"
    else:
        g37[rel] = "byte-identical" if pa.read_bytes() == ph.read_bytes() else "DIFFERS"
sc = json.loads((A / f"{K}/phase2/g37-opmax/scores.json").read_text())
g37["_stages"] = [(s["k"], s["opmax"]["vote_t"], s["opmax"]["prob_t"], s["f1_20"],
                   s["tile_mcc"], s["n_detections"]) for s in sc["stages"]]
rep["g37_opmax"] = g37

# ---- 3e. the collected scores ----------------------------------------------
te = json.loads((A / f"{K}/tier-e/scores.json").read_text())
rep["tier_e_scores"] = [(r["K"], r["opmax"]["f1_20"], r["opmax"]["tile_mcc"],
                         r["opmax"]["n_detections"], r["carried"]["f1_20"]) for r in te["rungs"]]
lad = json.loads((A / f"{K}/tier-e/ladder.json").read_text())
rep["tier_e_ladder"] = {"rungs": [(r["n_passes"], r["f1_20"], r["tile_mcc"]) for r in lad["rungs"]],
                        "n_significant_f1": lad["n_significant_f1"],
                        "n_significant_mcc": lad["n_significant_mcc"], "n_tiers": lad["n_tiers"]}
p2 = json.loads((A / f"{K}/phase2/scores.json").read_text())
rep["phase2_scores_g37"] = [(r["n_passes"], r["candidates"], r["verifier_stage"],
                             r["opmax"]["f1_20"], r["opmax"]["n_detections"],
                             r["carried"]["f1_20"], r["opmax"]["tile_mcc"])
                            for r in p2["rungs"] if r["pool_slug"] == "g384_ov192_g37"]
p2_old = committed(A, f"{K}/phase2/scores.json")
rep["phase2_scores_other_rows_identical"] = all(
    x == y for x, y in zip(p2["rungs"], p2_old["rungs"], strict=True)
    if x["pool_slug"] != "g384_ov192_g37")

# ---- 3f. inventory, Phase 1 tables, tension --------------------------------
rep["inventory_moved"] = json.loads((A.parent / "A" / "inventory" / "moved.json").read_text())
lj = json.loads((A / f"{K}/ladders.json").read_text())
gs = next(x for x in lj["ladders"] if "GS, exact" in x["family"])
rep["ladders_json_gs"] = [(r["K"], r["f1_headline"], r["tile_mcc"], r["n_detections"],
                           r["board_frame"]["f1_20"], r["board_frame"]["mcc"],
                           r["board_frame"]["n_detections"], r["frame_tax_f1_20"])
                          for r in gs["rungs"]]
lj_old = committed(A, f"{K}/ladders.json")
rep["ladders_json_other_ladders_identical"] = all(
    x == y for x, y in zip(lj["ladders"], lj_old["ladders"], strict=True) if x is not gs)
go = json.loads((A / f"{K}/tension/grid-overlap.json").read_text())
rep["grid_overlap"] = {c["cell"]: ({k: (v["f1_20"], v["mcc"]) for k, v in c["rungs"].items()},
                                   c["K_best"], c["delta_f1_k1_to_best"],
                                   c["delta_mcc_k1_to_best"]) for c in go["cells"]}
rep["grid_overlap_tier_e"] = go["tier_e_verified_b_geometry"]["rungs"]
es = json.loads((A / f"{K}/tension/effect-sizes.json").read_text())
rep["effect_sizes"] = [(r["ladder"][:48], r["f1_low"], r["f1_best"], r["delta_f1"],
                        r.get("p_bh")) for r in es["rows"]]
print(json.dumps(rep, indent=1, default=str))
