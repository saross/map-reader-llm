#!/usr/bin/env python
"""Follow-up diagnostics for the TM cross-date check (scratch only)."""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

sys.path.insert(0, "/tmp/vdate")
import vdate_check as V  # noqa: E402

_G: dict = {}


def score(g, pt, k):
    sub = g[(g["mound_probability"] >= pt) & (g["vote_count"] >= k)]
    t = V.compute_per_tile_tp_fp_fn(sub, _G["ref"], _G["bounds"],
                                    buffer_metres=V.BUFFER_M)
    t = t.sort_values("tile_name").reset_index(drop=True)
    return t


def null_draw(seed):
    """Flip random k4 decisions matched on earlier-p composition; F1 delta."""
    rng = np.random.default_rng(seed)
    p = _G["p0"].copy()
    for idx_pool, counts in _G["strata"]:
        for v, c in counts.items():
            cand = idx_pool[v]
            pick = rng.choice(cand, size=c, replace=False)
            # flip decision: below-threshold -> 0.5, above -> 0.0
            p[pick] = np.where(p[pick] >= 0.15, 0.0, 0.5)
    g = _G["base"].copy()
    g["mound_probability"] = p
    t = score(g, 0.15, 4)
    return V.micro_f1(int(t.tp.sum()), int(t.fp.sum()), int(t.fn.sum()))


def main():
    res = {}
    orig = V.load_manifest_probs(V.K4C, V.K4V)
    inc = V.load_manifest_probs(V.SHC, V.SHV)
    tm = pd.concat([orig, inc], ignore_index=True)
    ex = pd.concat([V.extras(V.K4C, "k4"), V.extras(V.SHC, "shell")], ignore_index=True)
    tm["subset"] = ex["subset"].values
    tm["candidate_id"] = ex["candidate_id"].values
    upl = V.load_manifest_probs(V.UPC, V.UPV)
    T = np.c_[tm.geometry.x, tm.geometry.y]
    U = np.c_[upl.geometry.x, upl.geometry.y]
    d, j = cKDTree(U).query(T)
    _d, i = cKDTree(T).query(U)
    mutual = i[j] == np.arange(len(T))
    tm["p_upl"] = upl["mound_probability"].to_numpy()[j]
    rep2 = mutual & (d <= 2.0)
    rep5 = mutual & (d <= 5.0)

    bounds = gpd.read_file(V.BOUNDS)
    if bounds.crs is None:
        bounds = bounds.set_crs("EPSG:4326")
    bounds = bounds.to_crs("EPSG:32635")
    ref = V.reference_gt("r2")
    _G["ref"], _G["bounds"] = ref, bounds
    base = gpd.GeoDataFrame(
        tm[["vote_count", "mound_probability", "source_tile", "geometry"]].copy(),
        geometry="geometry", crs="EPSG:32635")
    base = V.assign_source_tiles(base, bounds)
    _G["base"] = base

    # 1. delta-p by earlier-p band (2 m matched)
    bands = [(-0.01, 0.0), (0.0, 0.149), (0.149, 0.5), (0.5, 0.79), (0.79, 1.0)]
    tab = {}
    for s in ("k4", "shell"):
        m = (tm.subset == s) & rep2
        p0, p1 = tm.loc[m, "mound_probability"], tm.loc[m, "p_upl"]
        for lo, hi in bands:
            b = (p0 > lo) & (p0 <= hi)
            tab[f"{s} ({lo},{hi}]"] = [int(b.sum()), float((p1[b] - p0[b]).mean()),
                                       float((p1[b] == p0[b]).mean())]
    res["dp_by_band"] = tab

    # 2. flip direction vs reference proximity (nearest r2 point <= 50 m)
    rtree = cKDTree(np.c_[ref.geometry.x, ref.geometry.y])
    dref, _ = rtree.query(T)
    near = dref <= 50.0
    prox = {}
    for s in ("k4", "shell"):
        m = (tm.subset == s) & rep2
        p0, p1 = tm.mound_probability.to_numpy(), tm.p_upl.to_numpy()
        for t in (0.15, 0.20):
            up = m & (p0 < t) & (p1 >= t)
            dn = m & (p0 >= t) & (p1 < t)
            prox[f"{s}@{t}"] = {"up_n": int(up.sum()), "up_near": float(near[up].mean()),
                                "down_n": int(dn.sum()), "down_near": float(near[dn].mean()),
                                "all_matched_near": float(near[m].mean())}
    res["flip_proximity"] = prox

    # 3. 5 m replacement variant
    variants = {"A": tm.mound_probability.to_numpy(),
                "B5": np.where(rep5, tm.p_upl, tm.mound_probability)}
    res["kept_original_B5"] = {s: float((~rep5[tm.subset == s]).mean())
                               for s in ("k4", "shell")}
    tiles, scores = {}, {}
    for v, p in variants.items():
        g = base.copy()
        g["mound_probability"] = p
        for pt, k in V.POINTS:
            t = score(g, pt, k)
            tiles[(v, pt, k)] = t
            tp, fp, fn = int(t.tp.sum()), int(t.fp.sum()), int(t.fn.sum())
            scores[f"{v}|{pt}|k{k}"] = [len(g[(g.mound_probability >= pt)
                                              & (g.vote_count >= k)]), tp, fp, fn,
                                        V.micro_f1(tp, fp, fn)]
    res["scores"] = scores

    def arm(key):
        t = tiles[key]
        return {c: t[c].to_numpy(dtype=float) for c in ("tp", "fp", "fn")}

    tests = {}
    for lab, ka, kb in [("B5 k3-k4@0.15", ("B5", 0.15, 3), ("B5", 0.15, 4)),
                        ("B5 (0.20,k3)-(0.15,k4)", ("B5", 0.20, 3), ("B5", 0.15, 4)),
                        ("TM-k4 B5-A @(0.15,k4)", ("B5", 0.15, 4), ("A", 0.15, 4))]:
        r = V.paired_permutation_test(arm(ka), arm(kb), n_permutations=10_000, seed=42)
        f = r["metrics"]["f1"]
        tests[lab] = [f["a"], f["b"], f["observed_diff"], f["p_value"], f["null_std"]]
    res["tests"] = tests

    # 4. random-flip null for the TM-k4 June-April shift (2 m variant, 0.15)
    p0 = tm.mound_probability.to_numpy()
    pB = np.where(rep2, tm.p_upl, tm.mound_probability)
    k4 = (tm.subset == "k4").to_numpy()
    up = k4 & (p0 < 0.15) & (pB >= 0.15)
    dn = k4 & (p0 >= 0.15) & (pB < 0.15)
    strata = []
    for sel, side in ((up, p0 < 0.15), (dn, p0 >= 0.15)):
        counts = pd.Series(p0[sel]).value_counts().to_dict()
        pool_idx = {v: np.flatnonzero(k4 & side & (p0 == v)) for v in counts}
        strata.append((pool_idx, counts))
    _G["p0"], _G["strata"] = p0, strata
    with Pool(16) as pool:
        null = np.array(pool.map(null_draw, range(1000), chunksize=8))
    fA = scores["A|0.15|k4"][4]
    dnull = null - fA
    obs = 0.7866999  # placeholder replaced below
    gB = base.copy()
    gB["mound_probability"] = pB
    t = score(gB, 0.15, 4)
    obs = V.micro_f1(int(t.tp.sum()), int(t.fp.sum()), int(t.fn.sum())) - fA
    res["random_flip_null"] = {"n_up": int(up.sum()), "n_down": int(dn.sum()),
                               "obs_delta": obs, "null_mean": float(dnull.mean()),
                               "null_sd": float(dnull.std()),
                               "null_q": [float(x) for x in np.quantile(
                                   dnull, [0.025, 0.5, 0.975])],
                               "p_one_sided": float(np.mean(dnull >= obs)),
                               "p_two_sided_abs": float(np.mean(np.abs(dnull - dnull.mean())
                                                                >= abs(obs - dnull.mean())))}
    Path("/tmp/vdate/results_extra.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
