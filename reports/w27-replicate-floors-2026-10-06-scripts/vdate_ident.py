#!/usr/bin/env python
"""Identical-crop-only June-vs-April test at TM-k4 (scratch only)."""
import json
import sys
from multiprocessing import Pool

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

sys.path.insert(0, "/tmp/vdate")
import vdate_check as V  # noqa: E402


def main():
    orig = V.load_manifest_probs(V.K4C, V.K4V)
    inc = V.load_manifest_probs(V.SHC, V.SHV)
    tm = pd.concat([orig, inc], ignore_index=True)
    ex = pd.concat([V.extras(V.K4C, "k4"), V.extras(V.SHC, "shell")], ignore_index=True)
    tm["subset"] = ex["subset"].values
    tm["crop_path"] = ex["crop_path"].values
    upl = V.load_manifest_probs(V.UPC, V.UPV)
    T = np.c_[tm.geometry.x, tm.geometry.y]
    U = np.c_[upl.geometry.x, upl.geometry.y]
    d, j = cKDTree(U).query(T)
    _d, i = cKDTree(T).query(U)
    m5 = (i[j] == np.arange(len(T))) & (d <= 5.0)
    tm["sha_disk"] = [V.sha(p) for p in tm.crop_path]
    idx = np.flatnonzero(m5)
    tasks = [(f"up{r}", upl.source_tile.iat[j[r]], upl.geometry.x.iat[j[r]],
              upl.geometry.y.iat[j[r]]) for r in idx]
    with Pool(16) as pool:
        uh = pool.map(V.regen, tasks, chunksize=64)
    ident = np.zeros(len(tm), bool)
    ident[idx] = np.array(uh, dtype=object) == tm.sha_disk.to_numpy()[idx]
    p_upl = upl["mound_probability"].to_numpy()[j]
    bounds = gpd.read_file(V.BOUNDS)
    if bounds.crs is None:
        bounds = bounds.set_crs("EPSG:4326")
    bounds = bounds.to_crs("EPSG:32635")
    ref = V.reference_gt("r2")
    base = gpd.GeoDataFrame(
        tm[["vote_count", "mound_probability", "source_tile", "geometry"]].copy(),
        geometry="geometry", crs="EPSG:32635")
    base = V.assign_source_tiles(base, bounds)
    out = {"n_ident": int(ident.sum()),
           "n_ident_k4": int((ident & (tm.subset == "k4")).sum())}
    arms = {}
    for lab, p in (("A", tm.mound_probability.to_numpy()),
                   ("I", np.where(ident, p_upl, tm.mound_probability)),
                   ("Ik4", np.where(ident & (tm.subset == "k4").to_numpy(), p_upl,
                                    tm.mound_probability))):
        g = base.copy()
        g["mound_probability"] = p
        for pt, k in ((0.15, 4), (0.20, 3), (0.15, 3)):
            sub = g[(g.mound_probability >= pt) & (g.vote_count >= k)]
            t = V.compute_per_tile_tp_fp_fn(sub, ref, bounds, buffer_metres=V.BUFFER_M)
            t = t.sort_values("tile_name").reset_index(drop=True)
            arms[(lab, pt, k)] = {c: t[c].to_numpy(dtype=float) for c in ("tp", "fp", "fn")}
            out[f"{lab}|{pt}|k{k}"] = [int(t.tp.sum()), int(t.fp.sum()), int(t.fn.sum()),
                                       V.micro_f1(t.tp.sum(), t.fp.sum(), t.fn.sum())]
    for lab, a, b in (("I-A @(0.15,k4)", ("I", 0.15, 4), ("A", 0.15, 4)),
                      ("Ik4: k3-k4@0.15", ("Ik4", 0.15, 3), ("Ik4", 0.15, 4)),
                      ("Ik4: (0.20,k3)-(0.15,k4)", ("Ik4", 0.20, 3), ("Ik4", 0.15, 4))):
        r = V.paired_permutation_test(arms[a], arms[b], n_permutations=10_000, seed=42)
        f = r["metrics"]["f1"]
        out[lab] = [f["a"], f["b"], f["observed_diff"], f["p_value"], f["null_std"],
                    r["n_discordant_tiles"]]
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
