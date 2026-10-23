"""Recount the K-ladder SHAPE clause on the restated tables (read-only).

For each of the 23 ladders: the F1 and all-in cost per rung, each step's
price per 0.001 F1 (a step that loses or holds F1 counts as infinitely
dear), whether the last step is the dearest, whether it loses F1, K = 3's
share of the K = 1 -> best gain, and K = 3's share of the top rung's cost.
"""
import json
import math
import sys
from pathlib import Path

W = Path(sys.argv[1])
KL = W / "results/k-ladder-2026-09-12"


def phase1(gs_frame: str = "own"):
    """Phase 1 ladders from ladders.json: best F1 per K (the oracle rows)."""
    d = json.loads((KL / "ladders.json").read_text())
    out = []
    names = ["3.7 arm 1", "3.7 arm 2", "55-map stride A r2", "55-map stride A std",
             "GS stride A", "55-map stride B r2", "fourth cell (stride B, 3.7 vf)",
             "55-map stride B std"]
    for name, lad in zip(names, d["ladders"]):
        rungs = {}
        for r in lad["rungs"]:
            k = r["K"]
            f1 = r["f1_headline"]
            if k not in rungs or f1 > rungs[k][0]:
                rungs[k] = (f1, r["cost"]["usd"])
        if name.startswith("fourth"):
            # K = 5 rung registered 2026-09-13, absent from ladders.json:
            # FOURTH-N5-oracle evaluation F1@50 0.8758; cost US$116.15
            # (findings § 3.3 table; reports/wp4b-frontier-repricing-2026-10-04.md:54)
            rungs[5] = (0.8758, 116.15)
        if name == "GS stride A" and gs_frame == "board":
            # board-frame F1 (findings § 5; mcb/summary.json gs-stride-a statistic_by_K)
            m = json.loads((KL / "mcb/summary.json").read_text())
            g = [x for x in m["ladders"] if x["slug"] == "gs-stride-a"][0]
            sb = g["f1"]["statistic_by_K"]
            rungs = {k: (round(sb[str(k)], 4), rungs[k][1]) for k in rungs}
        out.append((name, "P1", dict(sorted(rungs.items()))))
    return out


def phase2(basis: str = "reported"):
    """Phase 2 ladders: opmax F1@20 on the reported (or historical) basis."""
    d = json.loads((KL / "phase2/ladders.json").read_text())
    out = []
    for lad in d["ladders"]:
        rungs = {}
        for r in lad["rungs"]:
            o = r["opmax"]
            f1 = o["f1_20"]
            if basis == "historical" and o.get("historical_as_evaluated"):
                f1 = o["historical_as_evaluated"]["f1_20"]
            rungs[r["K"]] = (f1, r["all_in_flex_usd"])
        out.append((lad["family"], "P2", rungs))
    return out


def tier_e(basis: str = "unclipped"):
    """Tier E: F1 from tier-e/ladder.json; all-in costs from findings § 8.4."""
    d = json.loads((KL / "tier-e/ladder.json").read_text())
    f1 = [r["f1_20"] for r in d["rungs"]]
    if basis == "clipped":
        f1 = [0.8604, 0.8902, 0.8968, 0.8942]
    cost = [2.09, 4.21, 6.20, 10.66]  # findings § 8.4, "about"
    return [("tier E", "E", dict(zip([1, 3, 5, 10], zip(f1, cost))))]


def analyse(ladders):
    rows = []
    for name, ph, rungs in ladders:
        ks = sorted(rungs)
        steps = []
        for a, b in zip(ks, ks[1:]):
            df1 = rungs[b][0] - rungs[a][0]
            dusd = rungs[b][1] - rungs[a][1]
            price = dusd / (df1 * 1000) if df1 > 0 else math.inf
            steps.append((f"{a}->{b}", round(df1, 4), round(dusd, 4), price))
        last = steps[-1]
        others = steps[:-1]
        dearest = all(last[3] >= s[3] for s in others)
        # if last and another both lose, flag the tie
        tie_inf = last[3] == math.inf and any(s[3] == math.inf for s in others)
        f1s = {k: v[0] for k, v in rungs.items()}
        best_k = max(f1s, key=lambda k: (f1s[k], -k))
        gain = f1s[best_k] - f1s[ks[0]]
        share3 = (f1s[3] - f1s[ks[0]]) / gain if gain > 0 else None
        cshare3 = rungs[3][1] / rungs[ks[-1]][1]
        rows.append(dict(name=name, ph=ph, steps=steps, last_dearest=dearest,
                         last_loses=last[1] <= 0, tie_inf=tie_inf, share3=share3,
                         cshare3=cshare3, last_price=last[3]))
    return rows


def report(label, ladders):
    rows = analyse(ladders)
    print(f"\n===== {label}: {len(rows)} ladders")
    for r in rows:
        st = "; ".join(
            f"{s[0]} {s[1]:+.4f}/${s[2]:.2f}="
            + ("LOSS" if s[3] == math.inf else f"${s[3]:.2f}")
            for s in r["steps"]
        )
        print(
            f"{r['name'][:38]:38s} last_dearest={str(r['last_dearest']):5s} "
            f"loses={str(r['last_loses']):5s} tie={r['tie_inf']} "
            f"share3={r['share3']:.4f} cost3={r['cshare3']:.4f} | {st}"
        )
    n = len(rows)
    nd = sum(r["last_dearest"] for r in rows)
    nl = [r["name"] for r in rows if r["last_loses"]]
    exc = [r["name"] for r in rows if not r["last_dearest"]]
    gp = [r["last_price"] for r in rows if r["last_price"] != math.inf]
    print(f"-> last step dearest on {nd} of {n}; exceptions: {exc}")
    print(f"-> last step loses F1 on {len(nl)}: {nl}")
    print(f"-> last-step price where it gains: {min(gp):.3f} .. {max(gp):.3f}")
    g3 = [r["share3"] for r in rows]
    print(f"-> K=3 gain share {min(g3):.4f} .. {max(g3):.4f}")
    c3 = [r["cshare3"] for r in rows]
    print(f"-> K=3 cost share {min(c3):.4f} .. {max(c3):.4f}")


report("RESTATED, GS own frame, P2 reported basis, tier E unclipped",
       phase1("own") + phase2("reported") + tier_e("unclipped"))
report("RESTATED, GS board frame, P2 reported basis, tier E unclipped",
       phase1("board") + phase2("reported") + tier_e("unclipped"))
report("RESTATED, GS own frame, P2 historical (as evaluated), tier E clipped",
       phase1("own") + phase2("historical") + tier_e("clipped"))
