"""Summarise the replicate calibration (light; pandas on a 10k-row CSV)."""
import json
import sys

import numpy as np
import pandas as pd
from scipy.stats import binomtest

df = pd.read_csv(sys.argv[1])
df["boot_rej"] = df["boot_p_f1"] < 0.05
df["perm_rej"] = df["perm_p"] < 0.05
df["boot_rej_prec"] = df["boot_p_prec"] < 0.05
df["boot_rej_rec"] = df["boot_p_rec"] < 0.05
df["kbin"] = pd.cut(df["k_discordant"], [-1, 0, 5, 10, 20, 50, 100, 200, 10_000],
                    labels=["0", "1-5", "6-10", "11-20", "21-50", "51-100", "101-200", ">200"])
out = {}


def rate(sub, col):
    n = len(sub)
    x = int(sub[col].sum())
    if n == 0:
        return None
    ci = binomtest(x, n).proportion_ci(0.95, method="wilson")
    return {"n": n, "rejections": x, "rate": round(x / n, 4), "ci95": [round(ci.low, 4), round(ci.high, 4)]}


def block(sub):
    return {"boot_f1": rate(sub, "boot_rej"), "perm_f1": rate(sub, "perm_rej"),
            "boot_prec": rate(sub, "boot_rej_prec"), "boot_rec": rate(sub, "boot_rej_rec")}


prim = df[(df["buffer"] == 20)]
out["all_pairs_20m"] = block(prim)
out["disjoint_pairs_20m"] = block(prim[prim["disjoint"]])
out["cross_arm_pairs_20m"] = block(prim[~prim["same_arm"]])
out["within_arm_pairs_20m"] = block(prim[prim["same_arm"]])
out["first_pass_cross_arm_20m (retest design)"] = block(prim[prim["first_pass_pair"]])
out["maps55_50m"] = block(df[(df["buffer"] == 50)])
out["by_scope_20m"] = {s: block(g) for s, g in prim.groupby("scope")}
out["by_group_20m"] = {int(s): block(g) for s, g in prim.groupby("group")}
out["by_temperature_20m"] = {str(s): block(g) for s, g in prim.groupby("temperature")}
out["by_k_discordant_20m"] = {str(s): block(g) for s, g in prim.groupby("kbin", observed=True)}
qs = [0.01, 0.05, 0.1, 0.25, 0.5]
out["p_quantiles_20m"] = {
    "boot_f1": {q: round(float(np.quantile(prim["boot_p_f1"], q)), 4) for q in qs},
    "perm_f1": {q: round(float(np.quantile(prim["perm_p"], q)), 4) for q in qs}}
out["p_ecdf_20m"] = {t: {"boot_f1": round(float((prim["boot_p_f1"] <= t).mean()), 4),
                         "perm_f1": round(float((prim["perm_p"] <= t).mean()), 4)}
                     for t in (0.001, 0.01, 0.05, 0.1, 0.2, 0.5)}
out["boot_p_at_floor_20m"] = int((prim["boot_p_f1"] <= 0.001).sum())
out["k_discordant_summary_20m"] = prim.groupby("temperature")["k_discordant"].describe().round(1).to_dict(orient="index")
# Co-occurrence of rejections.
out["crosstab_20m"] = pd.crosstab(prim["boot_rej"], prim["perm_rej"]).to_dict()
print(json.dumps(out, indent=1, default=str))
