#!/usr/bin/env python3
"""
Floors v2 analysis: corrected subsampling floors, validation, K = 10 extrapolation,
vote-propensity comparison and nested contrasts.
==================================================================================

Inputs (written by floors2_55map.py and floors2_gs.py): ``subset_cells_all.csv``,
``sim_cells.csv``, ``gs_slice_cells.csv``; and W2.7's committed
``subset_pairs.csv`` / ``gs_consensus_cells.csv`` (old floors, GS truth).

Estimator. For a statistic computed on every K-subset of N exchangeable passes,
with V_sub the variance (divisor C(N, K)) of the subset values,

    SD_run(K) = sqrt(V_sub * N / (N - K))

is exactly unbiased for the run-to-run variance of a K-pass MEAN, and for any
symmetric statistic its expectation is an upper bound on the run-to-run
variance (Hoeffding 1948: zeta_c / c rises with c, so Var(U_N) <= (K / N)
zeta_K and E[V_sub] = zeta_K - Var(U_N) >= zeta_K (N - K) / N). The brief's
form sqrt(V_sub (N - 1) / (N - K)) is reported beside it; it is lower by
sqrt((N - 1) / N). The floor is 1.96 * sqrt(2) * SD_run.

Zero API. Run on sapphire:
    .venv/bin/python floors2_analyse.py --out55 /tmp/floors2/out55 --outgs /tmp/floors2/outgs \
        --res /tmp/floors2/results

Author: Shawn Ross & Claude (Anthropic) | Created: 2026-10-07 | Apache 2.0
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(os.environ.get("REPO", str(Path.home() / "Code/map-reader-llm")))
W27 = REPO / "reports/w27-replicate-floors-2026-10-06-scripts"
Z = 1.96
NFAM = {
    "A": 10,
    "B": 10,
    "FOURTH": 10,
    "ARM1": 5,
    "ARM2": 5,
    "G37IMG-ARM1": 5,
    "G37IMG-ARM2": 5,
    "G3IMG-ARM1": 5,
    "G3IMG-ARM2": 5,
}


def sd_run(vals: np.ndarray, N: int, K: int, brief: bool = False) -> float:
    """Corrected run-to-run SD from the values over ALL K-subsets of N passes."""
    v = float(np.var(vals))  # divisor C(N, K)
    return float(np.sqrt(v * ((N - 1) if brief else N) / (N - K)))


def sd_dp(subs: list, vals: np.ndarray) -> float:
    """Unbiased run-to-run SD from all DISJOINT subset pairs: sqrt(mean(diff^2) / 2)."""
    d = [
        vals[i] - vals[j]
        for i, j in itertools.combinations(range(len(subs)), 2)
        if not set(subs[i]) & set(subs[j])
    ]
    return float(np.sqrt(np.mean(np.square(d)) / 2)) if d else float("nan")


def sd_any(subs: list, vals: np.ndarray, N: int, K: int, basis: str) -> float:
    """Run-to-run SD on the chosen basis: 'fpc' (corrected subsampling) or 'dp' (disjoint pairs)."""
    return sd_run(vals, N, K) if basis == "fpc" else sd_dp(subs, vals)


def jack_sd(subs: list[tuple], vals: np.ndarray, N: int, K: int) -> tuple[float, list[float]]:
    """Leave-one-pass-out jackknife SE of ``sd_run`` (subsets avoiding pass j; N - 1 passes)."""
    if N - 1 <= K:
        return float("nan"), []
    reps = []
    for j in range(N):
        m = np.array([j not in s for s in subs])
        reps.append(sd_run(vals[m], N - 1, K))
    reps = np.asarray(reps)
    return float(np.sqrt((N - 1) / N * ((reps - reps.mean()) ** 2).sum())), reps.tolist()


def k_path(frac: float, K: int) -> int:
    """Vote threshold at rung K on a relative-threshold path (round half up, >= 1)."""
    return max(1, int(np.floor(frac * K + 0.5)))


def fit_extrapolate(Ks: list[int], sds: list[float], Kt: int) -> dict:
    """Power law (log-log OLS) and hyperbola (SD = a + b / K, OLS) fits, read at Kt."""
    Ks, sds = np.asarray(Ks, float), np.asarray(sds, float)
    b, a = np.polyfit(np.log(Ks), np.log(sds), 1)
    pw = float(np.exp(a + b * np.log(Kt)))
    bh, ah = np.polyfit(1 / Ks, sds, 1)
    hy = float(ah + bh / Kt)
    return {
        "power": pw,
        "power_exp": float(b),
        "hyper": hy,
        "hyper_a": float(ah),
        "hyper_b": float(bh),
    }


def load55(out55: Path) -> pd.DataFrame:
    df = pd.read_csv(out55 / "subset_cells_all.csv")
    df["sub"] = df["subset"].astype(str).map(lambda s: tuple(int(x) for x in s.split("-")))
    return df


def floors55(df: pd.DataFrame) -> pd.DataFrame:
    """Corrected SD, floor, jackknife SE, and the all-disjoint-pairs empirical 95th pct."""
    rows = []
    for (f, K, p, k), g in df.groupby(["family", "K", "prob_t", "k"]):
        N = NFAM[f]
        subs, vals = list(g["sub"]), g["f1"].to_numpy()
        sd = sd_run(vals, N, K)
        se, _ = jack_sd(subs, vals, N, K)
        d = {s: v for s, v in zip(subs, vals)}
        diffs = [
            abs(d[a] - d[b]) for a, b in itertools.combinations(subs, 2) if not set(a) & set(b)
        ]
        rows.append(
            {
                "family": f,
                "N": N,
                "K": K,
                "prob_t": p,
                "k": k,
                "n_subsets": len(subs),
                "mean_f1": float(vals.mean()),
                "sd_sub": float(np.std(vals)),
                "sd_run": sd,
                "sd_run_brief": sd_run(vals, N, K, brief=True),
                "sd_jack_se": se,
                "floor": Z * np.sqrt(2) * sd,
                "floor_jack_se": Z * np.sqrt(2) * se,
                "n_disjoint_pairs": len(diffs),
                # E[(h(S) - h(S'))^2] = 2 Var(h) for DISJOINT S, S' of exchangeable passes,
                # so this is unbiased with no additivity assumption (K <= N / 2 only).
                "sd_dp": float(np.sqrt(np.mean(np.square(diffs)) / 2)) if diffs else np.nan,
                "emp95_disjoint": float(np.percentile(diffs, 95)) if diffs else np.nan,
            }
        )
    return pd.DataFrame(rows)


def old_floors() -> pd.DataFrame:
    """W2.7 § 6's 95th percentile per (family, N, prob_t, k) from its subset_pairs.csv."""
    sp = pd.read_csv(W27 / "subset_pairs.csv")
    sp = sp[sp["family"] != "UPL"]
    g = sp.groupby(["family", "n_rung", "prob_t", "k"])["abs_dF1"]
    return (
        pd.DataFrame({"old95": g.quantile(0.95), "old_pairs": g.size()})
        .reset_index()
        .rename(columns={"n_rung": "K"})
    )


def nested_threshold(df: pd.DataFrame, f: str, K: int, op1: tuple, op2: tuple) -> dict:
    """SD over runs of D = F1(op1) - F1(op2) on the SAME K passes (a nested contrast)."""
    a = df[(df.family == f) & (df.K == K) & (df.prob_t == op1[0]) & (df.k == op1[1])].set_index(
        "sub"
    )["f1"]
    b = df[(df.family == f) & (df.K == K) & (df.prob_t == op2[0]) & (df.k == op2[1])].set_index(
        "sub"
    )["f1"]
    D = (a - b.reindex(a.index)).to_numpy()
    subs = list(a.index)
    N = NFAM[f]
    sd = sd_run(D, N, K)
    se, _ = jack_sd(subs, D, N, K)
    return {
        "family": f,
        "K": K,
        "op1": op1,
        "op2": op2,
        "mean_D": float(D.mean()),
        "sd_D": sd,
        "sd_D_jack_se": se,
        "floor_nested": Z * sd,
    }


def nested_rung(df: pd.DataFrame, f: str, Ks: int, Kb: int, op_s: tuple, op_b: tuple) -> dict:
    """SD over runs of D = F1(S_big, op_b) - F1(S_small subset of S_big, op_s); degree-Kb kernel."""
    N = NFAM[f]
    a = df[(df.family == f) & (df.K == Kb) & (df.prob_t == op_b[0]) & (df.k == op_b[1])].set_index(
        "sub"
    )["f1"]
    b = df[(df.family == f) & (df.K == Ks) & (df.prob_t == op_s[0]) & (df.k == op_s[1])].set_index(
        "sub"
    )["f1"]
    D = np.asarray([a[sb] - b[ss] for sb in a.index for ss in itertools.combinations(sb, Ks)])
    sdD = sd_run(D, N, Kb)
    sd_s = sd_run(b.to_numpy(), N, Ks)
    sd_b = sd_run(a.to_numpy(), N, Kb)
    return {
        "family": f,
        "Ks": Ks,
        "Kb": Kb,
        "op_s": op_s,
        "op_b": op_b,
        "sd_D": sdD,
        "indep": float(np.hypot(sd_s, sd_b)),
        "ratio": sdD / float(np.hypot(sd_s, sd_b)),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out55", type=Path, default=Path("/tmp/floors2/out55"))
    ap.add_argument("--outgs", type=Path, default=Path("/tmp/floors2/outgs"))
    ap.add_argument("--res", type=Path, default=Path("/tmp/floors2/results"))
    ap.add_argument("--part", default="all")
    args = ap.parse_args()
    args.res.mkdir(parents=True, exist_ok=True)
    res: dict = {}

    # ---- 1. Corrected subsampling floors on the 55-map board -------------------------
    df = load55(args.out55)
    fl = floors55(df).merge(old_floors(), on=["family", "K", "prob_t", "k"], how="left")
    fl.to_csv(args.res / "floors55_all.csv", index=False)
    print(f"[1] {len(fl)} (family, K, prob, k) floors", flush=True)

    # ---- 3. K-scaling fits and extrapolation (55-map) ---------------------------------
    targets = [  # (label, family, prob, frac path, K target)
        ("A-N10-carried", "A", 0.15, 0.8, 10),
        ("A-N10-oracle", "A", 0.15, 0.7, 10),
        ("B-N10-carried", "B", 0.15, 1.0, 10),
        ("B-N10-oracle", "B", 0.20, 0.9, 10),
        ("FOURTH-N10-carried", "FOURTH", 0.98, 1.0, 10),
        ("FOURTH-N10-oracle", "FOURTH", 0.96, 0.9, 10),
        ("A@0.5 (UPL proxy)", "A", 0.15, 0.5, 10),
        ("B@0.5 (UPL proxy)", "B", 0.15, 0.5, 10),
        ("ARM1-N5-carried", "ARM1", 0.10, 1.0, 5),
        ("ARM1-N5-oracle", "ARM1", 0.15, 1.0, 5),
        ("ARM2-N5-carried", "ARM2", 0.80, 1.0, 5),
        ("ARM2-N5-oracle", "ARM2", 0.95, 1.0, 5),
        ("A-N5 (check)", "A", 0.15, 0.8, 5),
        ("B-N5 (check)", "B", 0.15, 1.0, 5),
        ("FOURTH-N5 (check)", "FOURTH", 0.98, 1.0, 5),
    ]
    ext = []
    for (lab, f, p, frac, Kt), basis in itertools.product(targets, ("fpc", "dp")):
        N = NFAM[f]
        Kfit = [K for K in range(1, 6) if K < N and K < Kt and (basis == "fpc" or 2 * K <= N)]
        if "check" in lab:
            Kfit = [K for K in (1, 2, 3, 4) if basis == "fpc" or 2 * K <= N]
        if len(Kfit) < 3:
            continue

        def cell(K, keep=None):
            g = df[(df.family == f) & (df.K == K) & (df.prob_t == p) & (df.k == k_path(frac, K))]
            subs, vals = list(g["sub"]), g["f1"].to_numpy()
            if keep is not None:
                m = np.array([keep not in sb for sb in subs])
                subs, vals = [sb for sb, mm in zip(subs, m) if mm], vals[m]
            return subs, vals

        sds = [sd_any(*cell(K), N, K, basis) for K in Kfit]
        fit = fit_extrapolate(Kfit, sds, Kt)
        reps = []
        for j in range(N):  # pass jackknife of the whole fit (each point on N - 1 passes)
            if any(N - 1 <= K or (basis == "dp" and 2 * K > N - 1) for K in Kfit):
                break
            sj = [sd_any(*cell(K, keep=j), N - 1, K, basis) for K in Kfit]
            fj = fit_extrapolate(Kfit, sj, Kt)
            reps.append((fj["power"], fj["hyper"]))
        if len(reps) == N:
            r = np.asarray(reps)
            se_pw = float(np.sqrt((N - 1) / N * ((r[:, 0] - r[:, 0].mean()) ** 2).sum()))
            se_hy = float(np.sqrt((N - 1) / N * ((r[:, 1] - r[:, 1].mean()) ** 2).sum()))
        else:
            se_pw = se_hy = float("nan")
        direct = None
        if Kt <= 5 and Kt < N:
            direct = sd_any(*cell(Kt), N, Kt, basis)
        ext.append(
            {
                "label": lab,
                "basis": basis,
                "family": f,
                "prob_t": p,
                "path": [(K, k_path(frac, K)) for K in Kfit],
                "K_target": Kt,
                "k_target": k_path(frac, Kt),
                "sd_points": sds,
                **fit,
                "se_power": se_pw,
                "se_hyper": se_hy,
                "direct_sd_at_target": direct,
            }
        )
    pd.DataFrame(ext).to_csv(args.res / "extrapolation55.csv", index=False)
    res["extrapolation55"] = ext
    print("[3] extrapolations written", flush=True)

    # ---- nested contrasts (55-map) -------------------------------------------------------
    nest = []
    for f in ("A", "B"):
        nest.append(nested_threshold(df, f, 5, (0.15, 3), (0.15, 4)))
        nest.append(nested_threshold(df, f, 5, (0.20, 3), (0.15, 4)))
    for f, o, c in (("ARM2", 0.95, 0.80), ("ARM1", 0.15, 0.10)):
        for K in (3, 4):
            nest.append(nested_threshold(df, f, K, (o, K), (c, K)))
    nest.append(nested_threshold(df, "FOURTH", 5, (0.96, 5), (0.98, 5)))
    rung = []
    for f, p in (("A", 0.15), ("B", 0.15), ("B", 0.20), ("FOURTH", 0.98)):
        for Ks, Kb, fr in (
            (2, 4, 1.0),
            (3, 5, 1.0),
            (2, 4, 0.8),
            (3, 5, 0.8),
            (1, 2, 1.0),
            (2, 3, 1.0),
        ):
            rung.append(nested_rung(df, f, Ks, Kb, (p, k_path(fr, Ks)), (p, k_path(fr, Kb))))
    for f, p in (("ARM1", 0.10), ("ARM2", 0.80), ("ARM2", 0.95)):
        for Ks, Kb in ((1, 2), (2, 3), (2, 4), (3, 4)):
            rung.append(nested_rung(df, f, Ks, Kb, (p, Ks), (p, Kb)))
    pd.DataFrame(nest).to_csv(args.res / "nested_threshold55.csv", index=False)
    pd.DataFrame(rung).to_csv(args.res / "nested_rung55.csv", index=False)
    res["nested_threshold55"] = nest
    res["nested_rung55"] = rung
    print("[nested] written", flush=True)

    # ---- 4. Vote-propensity models against subsampling ------------------------------
    simf = args.out55 / "sim_cells.csv"
    if simf.exists():
        sm = pd.read_csv(simf)
        rows = []
        for (f, K, p, k, model), g in sm.groupby(["family", "K", "prob_t", "k", "model"]):
            N = NFAM[f]
            vals = g["f1"].to_numpy()
            if model == "union-sub":
                sd = sd_run(vals, N, K)
            else:  # plug-in propensities v/N: variance x N/(N-1) (Bessel), ddof 1 over draws
                sd = float(np.std(vals, ddof=1) * np.sqrt(N / (N - 1)))
            rows.append(
                {
                    "family": f,
                    "K": K,
                    "prob_t": p,
                    "k": k,
                    "model": model,
                    "sd": sd,
                    "n_draws": len(vals),
                    "mean_f1": float(vals.mean()),
                }
            )
        pm = (
            pd.DataFrame(rows)
            .pivot_table(index=["family", "K", "prob_t", "k"], columns="model", values="sd")
            .reset_index()
        )
        pm = pm.merge(
            fl[["family", "K", "prob_t", "k", "sd_run"]],
            on=["family", "K", "prob_t", "k"],
            how="left",
        )
        pm.to_csv(args.res / "propensity55.csv", index=False)
        print("[4] propensity comparison written", flush=True)

    # ---- 2. GS validation -----------------------------------------------------------
    gsf = args.outgs / "gs_slice_cells.csv"
    if gsf.exists():
        gsd = pd.read_csv(gsf)
        truth = pd.read_csv(W27 / "gs_consensus_cells.csv")
        truth = truth[truth.member.isin(gsd.member.unique())]
        val = []
        for (mem, sl, K, t), g in gsd.groupby(["member", "slice", "K", "t"]):
            est = sd_run(g["f1_20"].to_numpy(), 10, K)
            est_b = sd_run(g["f1_20"].to_numpy(), 10, K, brief=True)
            dv = dict(zip(g["subset"], g["f1_20"]))
            sl_d = [
                dv[a] - dv[b]
                for a, b in itertools.combinations(dv, 2)
                if not set(json.loads(a)) & set(json.loads(b))
            ]
            est_dp = float(np.sqrt(np.mean(np.square(sl_d)) / 2)) if sl_d else np.nan
            if K == 1:
                tv = gsd[(gsd.member == mem) & (gsd.K == 1)]["f1_20"].to_numpy()
            else:
                tv = truth[(truth.member == mem) & (truth.K == K) & (truth.t == t)][
                    "f1_20"
                ].to_numpy()
            if K in (1, 3, 5) and len(tv) >= 3:
                emp = float(np.std(tv, ddof=1))
                diffs = [abs(a - b) for a, b in itertools.combinations(tv, 2)]
                val.append(
                    {
                        "member": mem,
                        "scope": g["scope"].iloc[0],
                        "slice": sl,
                        "K": K,
                        "t": t,
                        "est_sd": est,
                        "est_sd_brief": est_b,
                        "est_sd_dp": est_dp,
                        "emp_sd": emp,
                        "n_emp": len(tv),
                        "emp_pairs": json.dumps([float(x) for x in diffs]),
                    }
                )
        vd = pd.DataFrame(val)
        vd.to_csv(args.res / "gs_validation.csv", index=False)
        # K = 10 extrapolation check on the GS pools.
        gx = []
        for (mem, sl), g in gsd.groupby(["member", "slice"]):
            for (frac, tt), basis in itertools.product(
                ((1.0, 10), (0.9, 9), (0.8, 8), (0.5, 5)), ("fpc", "dp")
            ):
                Kfit = [1, 2, 3, 4, 5]
                sds = []
                for K in Kfit:
                    gg = g[(g.K == K) & (g.t == k_path(frac, K))]
                    sds.append(
                        sd_any(
                            [tuple(json.loads(x)) for x in gg["subset"]],
                            gg["f1_20"].to_numpy(),
                            10,
                            K,
                            basis,
                        )
                    )
                fit = fit_extrapolate(Kfit, sds, 10)
                tv = truth[(truth.member == mem) & (truth.K == 10) & (truth.t == tt)][
                    "f1_20"
                ].to_numpy()
                gx.append(
                    {
                        "member": mem,
                        "scope": g["scope"].iloc[0],
                        "slice": sl,
                        "t10": tt,
                        "frac": frac,
                        "basis": basis,
                        **fit,
                        "sd5": sds[-1],
                        "emp_sd10": float(np.std(tv, ddof=1)) if len(tv) >= 2 else np.nan,
                        "emp10_pairs": json.dumps(
                            [float(abs(a - b)) for a, b in itertools.combinations(tv, 2)]
                        ),
                    }
                )
        pd.DataFrame(gx).to_csv(args.res / "gs_k10_check.csv", index=False)
        print("[2] GS validation written", flush=True)
    (args.res / "results.json").write_text(json.dumps(res, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
