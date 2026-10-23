#!/usr/bin/env python3
"""Compare two era1_leaderboard_tiering outputs: pairs, tiers, ranking, MCC.

Usage: cmp_tiering.py <pred.json> <regen.json>
Prints scalar summaries for both, then every member whose tier, rank,
eval_f1 or observed_micro_f1 differs, and the count of pairwise rows whose
p, BH p, observed difference or significance differ.

Part of the S164 restatement pass (reports/s164-agent-records/
restatement-pass.md § 1.3, the Era-2 board lane).

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""
import json
import sys

a, b = (json.load(open(p)) for p in sys.argv[1:3])


def summ(d):
    m = d["mcc_permutation"]
    return dict(n_pairs=len(d["pairwise"]), sig=sum(p["significant"] for p in d["pairwise"]),
                tiers=len(d["tiers"]), tie=d["tie_set"], withheld=d["n_cells_withheld"],
                n_cells=d["n_cells"], mcc=(m["n_significant"], m["n_tiers"], len(m["tie_set"])),
                leaders=[(r["ref"].split("::")[1], r["eval_f1"], r["observed_micro_f1"])
                         for r in d["ranking"][:5]])


sa, sb = summ(a), summ(b)
for k in sa:
    print(k, "SAME" if sa[k] == sb[k] else "DIFF", sb[k] if k != "tie" else len(sb[k]))
    if sa[k] != sb[k]:
        print("   pred:", sa[k])
ra = {r["ref"]: r for r in a["ranking"]}
rb = {r["ref"]: r for r in b["ranking"]}
nd = 0
for ref in sorted(set(ra) | set(rb)):
    x, y = ra.get(ref), rb.get(ref)
    f = ("tier", "rank", "eval_f1", "observed_micro_f1", "mcc")
    if x is None or y is None or any(x[k] != y[k] for k in f):
        nd += 1
        print(" member", ref.split("::")[1], {k: (x[k] if x else None, y[k] if y else None)
                                               for k in f if not x or not y or x[k] != y[k]})
print("members differing:", nd)
pa = {(p["ref_a"], p["ref_b"]): p for p in a["pairwise"]}
pb = {(p["ref_a"], p["ref_b"]): p for p in b["pairwise"]}
print("pair keys equal:", set(pa) == set(pb))
for fld in ("observed_diff", "p_value", "bh_adjusted_p", "significant", "f1_a", "f1_b"):
    print(" pairs differing on", fld, sum(pa[k][fld] != pb[k][fld] for k in pa if k in pb))
