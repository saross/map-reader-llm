#!/usr/bin/env python3
"""Floors v2: render the report's Markdown tables from the result CSVs (no new computation).

Author: Shawn Ross & Claude (Anthropic) | Created: 2026-10-07 | Apache 2.0
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RES = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/floors2/results")
F = 1.96 * np.sqrt(2)
fl = pd.read_csv(RES / "floors55_all.csv")
ex = pd.read_csv(RES / "extrapolation55.csv")
cs = pd.read_csv(RES / "cell_sds.csv").set_index("cell")


def row(f, K, p, k):
    r = fl[(fl.family == f) & (fl.K == K) & np.isclose(fl.prob_t, p) & (fl.k == k)].iloc[0]
    se = f" ± {r.floor_jack_se:.4f}" if np.isfinite(r.floor_jack_se) else ""
    e95 = f"{r.emp95_disjoint:.4f} ({int(r.n_disjoint_pairs)})" if r.n_disjoint_pairs else "—"
    old = f"{r.old95:.4f} ({int(r.old_pairs)})" if np.isfinite(r.old95) else "—"
    return f"{r.n_subsets} | {r.floor:.4f}{se} | {e95} | {old}"


def ext(label):
    g = ex[(ex.label == label) & (ex.basis == "fpc")].iloc[0]
    d = ex[(ex.label == label) & (ex.basis == "dp")]
    pts = ast.literal_eval(g.sd_points)
    rec = max(g.power, g.hyper, pts[-1])
    up = np.nanmax([rec, g.hyper + 1.96 * g.se_hyper, g.power + 1.96 * g.se_power])
    lo = d.power.iloc[0] if len(d) else min(g.power, g.hyper)
    return f"extrap. | {F * rec:.4f} [{F * lo:.4f}, {F * up:.4f}] | — | — (0.005 used)"


spec = [
    ("A", 1, 0.20, 1, "N1 oracle"),
    ("A", 3, 0.15, 3, "N3 carried"),
    ("A", 3, 0.20, 2, "N3 oracle"),
    ("A", 5, 0.15, 4, "N5 carried = oracle"),
    ("A", 10, 0.15, 8, "N10 carried"),
    ("A", 10, 0.15, 7, "N10 oracle"),
    ("B", 1, 0.20, 1, "N1 oracle"),
    ("B", 3, 0.15, 3, "N3 carried"),
    ("B", 3, 0.20, 3, "N3 oracle"),
    ("B", 5, 0.15, 5, "N5 carried"),
    ("B", 5, 0.20, 5, "N5 oracle"),
    ("B", 10, 0.15, 10, "N10 carried"),
    ("B", 10, 0.20, 9, "N10 oracle"),
    ("FOURTH", 1, 0.98, 1, "N1 carried"),
    ("FOURTH", 1, 0.96, 1, "N1 oracle"),
    ("FOURTH", 3, 0.98, 3, "N3 carried"),
    ("FOURTH", 3, 0.96, 3, "N3 oracle"),
    ("FOURTH", 5, 0.98, 5, "N5 carried"),
    ("FOURTH", 10, 0.98, 10, "N10 carried"),
    ("FOURTH", 10, 0.96, 9, "N10 oracle"),
    ("ARM1", 1, 0.10, 1, "N1 carried"),
    ("ARM1", 1, 0.20, 1, "N1 oracle"),
    ("ARM1", 3, 0.10, 3, "N3 carried"),
    ("ARM1", 3, 0.15, 3, "N3 oracle"),
    ("ARM1", 5, 0.10, 5, "N5 carried"),
    ("ARM2", 1, 0.80, 1, "N1 carried"),
    ("ARM2", 1, 0.98, 1, "N1 oracle"),
    ("ARM2", 3, 0.80, 3, "N3 carried"),
    ("ARM2", 3, 0.95, 3, "N3 oracle"),
    ("ARM2", 5, 0.80, 5, "N5 carried"),
    ("ARM2", 5, 0.95, 5, "N5 oracle"),
    ("G37IMG-ARM1", 1, 0.10, 1, "N1"),
    ("G37IMG-ARM1", 3, 0.10, 3, "K3 unanimity"),
    ("G37IMG-ARM2", 1, 0.88, 1, "N1"),
    ("G37IMG-ARM2", 3, 0.88, 3, "K3 unanimity"),
    ("G3IMG-ARM1", 1, 0.15, 1, "N1"),
    ("G3IMG-ARM1", 3, 0.15, 3, "K3 unanimity"),
    ("G3IMG-ARM2", 1, 0.88, 1, "N1"),
    ("G3IMG-ARM2", 3, 0.88, 3, "K3 unanimity"),
]
print(
    "| family | rung | point | subsets | new floor ± jackknife SE "
    "| all disjoint pairs, 95th pct (pairs) | old § 6 floor (pairs) |"
)
print("|---|---|---|---:|---:|---:|---:|")
for f, K, p, k, lab in spec:
    if K == 10:
        body = ext(f"{f}-N10-{lab.split()[1]}")
    elif K == 5 and f in ("ARM1", "ARM2"):
        c = cs.loc[f"{f}-N5-{lab.split()[1]}"]
        body = f"fit, K ≤ 4 | {F * c.sd:.4f} [—, {F * c.up:.4f}] | — | —"
    else:
        body = row(f, K, p, k)
    print(f"| {f} | {lab} | ({p:.2f}, k{k}) | {body} |")

print()
v = pd.read_csv(RES / "gs_validation_summary.csv")
print(
    "| corpus | K | t | pools × slices | est. SD (RMS) | disjoint-30 SD (RMS) | ratio, corrected "
    "| ratio, brief's form | ratio, disjoint-pair est. | single-slice ratio IQR | predicted floor "
    "| empirical 95th (pairs) |"
)
print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|")
for r in v.itertuples():
    print(
        f"| {r.scope} | {r.K} | {r.t} | {r.pools} × 3 | {r.rms_est:.4f} | {r.rms_emp:.4f} "
        f"| {r.pooled_ratio:.2f} | "
        f"{r.pooled_ratio_brief:.2f} | {r.pooled_ratio_dp:.2f} | {r.q25:.2f}–{r.q75:.2f} "
        f"| {r.floor_pred:.4f} | {r.emp95:.4f} ({r.npairs}) |"
    )

print()
k10 = pd.read_csv(RES / "gs_k10_summary.csv")
print(
    "| corpus | t at K = 10 | pools | empirical SD₁₀ (RMS, 3 disjoint per pool) | fpc power "
    "| fpc hyperbola | flat (SD₅) | dp power | empirical 95th (pairs) "
    "| predicted floor (fpc hyperbola) |"
)
print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
for (sc, t), g in k10.groupby(["scope", "t10"]):
    a = g[g.basis == "fpc"].iloc[0]
    d = g[g.basis == "dp"].iloc[0]
    print(
        f"| {sc} | {t} | {a.pools} | {a.rms_emp10:.4f} | {a.r_power:.2f} | {a.r_hyper:.2f} "
        f"| {a.r_flat5:.2f} | {d.r_power:.2f} | "
        f"{a.emp95_10:.4f} ({a.npairs}) | {a.floor_hyp:.4f} |"
    )
