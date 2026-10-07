#!/usr/bin/env python3
"""
Floors v2: per-cell run-to-run SDs (direct, extrapolated, proxy) and the § 7.2 re-screen.
=======================================================================================

Reads ``floors55_all.csv``, ``extrapolation55.csv``, ``nested_threshold55.csv`` and
``nested_rung55.csv`` (floors2_analyse.py) and writes ``cell_sds.csv`` and
``rescreen.csv``. Floor rules (point / upper):

* independent cells: 1.96 * sqrt(SD_x^2 + SD_y^2) + 0.001 (verifier re-invocation band,
  additive as in W2.7 § 6); upper uses each SD's upper value (SD + 1.96 jackknife SE).
* cross-execution: the above + 0.004 to 0.007 (verifier vintage, W2.7 § 6a).
* nested rung (first-N inside first-M of one pool): 1.96 * rho * sqrt(SD_s^2 + SD_b^2)
  + 0.001, rho = median nesting ratio measured on (2 in 4) and (3 in 5) analogues;
  upper takes rho = 1 (independent) and upper SDs.
* nested threshold (two operating points on the same passes): 1.96 * SD_D + 0.001,
  SD_D measured by subsampling the contrast itself; upper SD_D + 1.96 SE.

Zero API. Author: Shawn Ross & Claude (Anthropic) | Created: 2026-10-07 | Apache 2.0
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RES = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/floors2/results")
Z = 1.96
fl = pd.read_csv(RES / "floors55_all.csv")
ex = pd.read_csv(RES / "extrapolation55.csv")
nt = pd.read_csv(RES / "nested_threshold55.csv")
nr = pd.read_csv(RES / "nested_rung55.csv")


def direct(f, K, p, k):
    r = fl[(fl.family == f) & (fl.K == K) & (np.isclose(fl.prob_t, p)) & (fl.k == k)].iloc[0]
    se = r.sd_jack_se if np.isfinite(r.sd_jack_se) else np.nan
    return float(r.sd_run), float(r.sd_run + Z * se) if np.isfinite(se) else np.nan


def extrap(label):
    g = ex[(ex.label == label) & (ex.basis == "fpc")].iloc[0]
    pts = ast.literal_eval(g.sd_points)
    rec = max(g.power, g.hyper, pts[-1])
    up = np.nanmax([rec, g.hyper + Z * g.se_hyper, g.power + Z * g.se_power])
    dp = ex[(ex.label == label) & (ex.basis == "dp")]
    lo = float(dp.power.iloc[0]) if len(dp) else float(min(g.power, g.hyper))
    return float(rec), float(up), lo


cells = {}
for lab, f, K, p, k in (
    ("A-N5-carried", "A", 5, 0.15, 4),
    ("B-N5-carried", "B", 5, 0.15, 5),
    ("A-N5-oracle", "A", 5, 0.15, 4),
    ("B-N5-oracle", "B", 5, 0.20, 5),
    ("ARM2-N1-oracle", "ARM2", 1, 0.98, 1),
    ("ARM1-N3-carried", "ARM1", 3, 0.10, 3),
    ("ARM2-N3-oracle", "ARM2", 3, 0.95, 3),
):
    sd, up = direct(f, K, p, k)
    cells[lab] = {"sd": sd, "up": up, "source": f"direct, {f} K={K} ({p}, k{k})"}
for lab in ("A-N10-carried", "A-N10-oracle", "B-N10-carried", "B-N10-oracle", "FOURTH-N10-carried"):
    rec, up, lo = extrap(lab)
    cells[lab] = {
        "sd": rec,
        "up": up,
        "lo": lo,
        "source": "extrapolated K=1..5 -> 10 (max of power, hyperbola, flat)",
    }
for lab, fam, p in (
    ("ARM1-N5-carried", "ARM1", 0.10),
    ("ARM2-N5-carried", "ARM2", 0.80),
    ("ARM2-N5-oracle", "ARM2", 0.95),
):
    rec, _, _ = extrap(lab)
    d3, u3 = direct(fam, 3, p, 3)
    d4, _ = direct(fam, 4, p, 4)
    sd = max(rec, d3, d4)
    cells[lab] = {
        "sd": sd,
        "up": sd + (u3 - d3),
        "source": "K=5 of 5 passes: max(fit K=1..4, direct K=3, K=4); upper + K=3 jackknife",
    }
for lab, p, k in (("T03-oracle", 0.20, 3), ("TM-k3", 0.15, 3), ("TH7-k3", 0.15, 3)):
    a, au = direct("A", 5, p, k)
    b, bu = direct("B", 5, p, k)
    cells[lab] = {"sd": max(a, b), "up": max(au, bu), "source": f"PROXY: max(A, B) K=5 ({p}, k{k})"}
ua, uau, _ = extrap("A@0.5 (UPL proxy)")
ub, ubu, _ = extrap("B@0.5 (UPL proxy)")
cells["UPL"] = {
    "sd": max(ua, ub),
    "up": max(uau, ubu),
    "source": "PROXY: max(A, B) extrapolated to K=10 (0.15, k5)",
}
pd.DataFrame([{"cell": k, **v} for k, v in cells.items()]).to_csv(RES / "cell_sds.csv", index=False)

half = nr[((nr.Ks == 2) & (nr.Kb == 4)) | ((nr.Ks == 3) & (nr.Kb == 5))]
half = half[half.family.isin(["A", "B", "FOURTH"])]
rho = float(half.ratio.median())
rho_rng = (float(half.ratio.min()), float(half.ratio.max()))


def indep(x, y, cross=False):
    pt = Z * np.hypot(cells[x]["sd"], cells[y]["sd"]) + 0.001
    up = Z * np.hypot(cells[x]["up"], cells[y]["up"]) + 0.001
    return (pt + 0.004, up + 0.007, pt) if cross else (pt, up, None)


def nested_rung(s, b):
    pt = Z * rho * np.hypot(cells[s]["sd"], cells[b]["sd"]) + 0.001
    up = Z * np.hypot(cells[s]["up"], cells[b]["up"]) + 0.001
    return pt, up, None


def nested_thr(rows, extra=0.0):
    sd = max(rows.sd_D)
    se = np.nanmax(rows.sd_D_jack_se.fillna(0))
    return (
        Z * sd + 0.001 + extra,
        Z * (sd + Z * se) + 0.001 + 2 * extra if extra else Z * (sd + Z * se) + 0.001,
        None,
    )


k34 = nt[(nt.K == 5) & (nt.family.isin(["A", "B"]))]
tax = nt[(nt.family == "ARM2")]
claims = [
    (
        "R7.2-13a",
        "A-N10-carried vs B-N10-carried",
        -0.0106,
        "same day",
        "0.005",
        "Stands",
        indep("A-N10-carried", "B-N10-carried"),
    ),
    (
        "R7.2-13b",
        "A-N10-oracle vs B-N10-oracle",
        -0.0141,
        "same day",
        "0.005",
        "Stand",
        indep("A-N10-oracle", "B-N10-oracle"),
    ),
    (
        "R7.2-13c",
        "A-N5-carried vs B-N5-carried",
        -0.0120,
        "same day",
        "0.005",
        "Stand",
        indep("A-N5-carried", "B-N5-carried"),
    ),
    (
        "R7.2-16a",
        "A N5 vs N10 carried (B: +0.0006)",
        -0.0009,
        "nested",
        "0.005",
        "Tie",
        nested_rung("A-N5-carried", "A-N10-carried"),
    ),
    (
        "R7.2-16b",
        "A oracle N5 vs N10 (r2 +0.0036)",
        0.0036,
        "nested",
        "0.005",
        "Inside",
        nested_rung("A-N5-oracle", "A-N10-oracle"),
    ),
    (
        "R7.2-16b",
        "B oracle N5 vs N10 (r2 +0.0043)",
        0.0043,
        "nested",
        "0.005",
        "Inside",
        nested_rung("B-N5-oracle", "B-N10-oracle"),
    ),
    (
        "R7.2-30",
        "B-N5-carried vs T03-oracle",
        0.0104,
        "cross ~4 months",
        "0.011-0.013",
        "Inside",
        indep("B-N5-carried", "T03-oracle", True),
    ),
    (
        "R7.2-32a",
        "B-N5-carried vs B-N10-carried",
        0.0006,
        "nested",
        "0.005",
        "Tie",
        nested_rung("B-N5-carried", "B-N10-carried"),
    ),
    (
        "R7.3-04",
        "ARM1-N5-carried vs B-N5-carried",
        0.0048,
        "cross 3-6 d",
        "0.011-0.013",
        "Tie",
        indep("ARM1-N5-carried", "B-N5-carried", True),
    ),
    (
        "R7.3-06b",
        "ARM2-N5-carried vs FOURTH-N10-carried",
        0.0099,
        "cross 3-6 d",
        "0.011-0.013",
        "Inside, unresolved",
        indep("ARM2-N5-carried", "FOURTH-N10-carried", True),
    ),
    (
        "R7.3-07",
        "ARM2 tax: (0.95,k5) - (0.80,k5), same passes",
        0.0043,
        "nested threshold",
        "0.005",
        "Inside",
        nested_thr(tax),
    ),
    (
        "R7.3-18a",
        "ARM2 N3-oracle vs N5-oracle",
        -0.0023,
        "nested",
        "0.007",
        "Tie",
        nested_rung("ARM2-N3-oracle", "ARM2-N5-oracle"),
    ),
    (
        "R7.3-18b",
        "ARM1 N3 vs N5 carried",
        0.0076,
        "nested",
        "0.007",
        "At the floor",
        nested_rung("ARM1-N3-carried", "ARM1-N5-carried"),
    ),
    (
        "R7.3-19",
        "ARM2-N1-oracle vs B-N5-carried",
        0.0107,
        "cross 3-6 d",
        "0.011-0.013",
        "Inside",
        indep("ARM2-N1-oracle", "B-N5-carried", True),
    ),
    (
        "R6-12a",
        "UPL vs TM-k3 (passes 1-5 shared)",
        0.0172,
        "mixed",
        "0.011-0.013",
        "Clears, confounded",
        indep("UPL", "TM-k3", True),
    ),
    (
        "R6-12b",
        "UPL vs TH7-k3",
        -0.0106,
        "mixed",
        "0.011-0.013",
        "Inside",
        indep("UPL", "TH7-k3", True),
    ),
    (
        "R7.1-09a",
        "T03 k3 vs k4 (same passes; verifier dates differ)",
        0.0092,
        "nested threshold, mixed verifier dates",
        "n/a (verifier date)",
        "Reword",
        nested_thr(k34, extra=0.0015),
    ),
]
rows = []
for cid, what, d, ex_, old, oldv, (pt, up, within) in claims:
    a = abs(d)
    v = (
        "clears"
        if a > up
        else ("clears the point floor; inside its upper bound" if a > pt else "inside")
    )
    rows.append(
        {
            "claim": cid,
            "contrast": what,
            "diff": d,
            "executions": ex_,
            "old_floor": old,
            "old_verdict": oldv,
            "new_floor_point": round(pt, 4),
            "new_floor_upper": round(up, 4),
            "within_part": round(within, 4) if within else None,
            "ratio_to_point": round(a / pt, 2),
            "new_verdict": v,
        }
    )
pd.DataFrame(rows).to_csv(RES / "rescreen.csv", index=False)
print(f"nesting ratio rho median {rho:.3f} range {rho_rng}")
print(
    pd.DataFrame(
        [
            {
                "cell": k,
                **{kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()},
            }
            for k, v in cells.items()
        ]
    ).to_string()
)
print(pd.DataFrame(rows).to_string())
