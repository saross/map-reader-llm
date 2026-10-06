#!/usr/bin/env python
"""Cross-date verifier check for the TM family (read-only; scratch in /tmp/vdate).

Matches TM candidates (April k4 set + June-6 vote-3 shell) to the June-11 UPL
re-verification by mutual-nearest centroid, compares probabilities, and
re-scores the TM family on the r2 board path with June-11 probabilities.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from multiprocessing import Pool
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

ROOT = Path.home() / "Code/map-reader-llm"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from scripts.final_board_sweeps import (  # noqa: E402
    BUFFER_M, DEPLOY, load_manifest_probs, prob_key)
from scripts.build_55map_leaderboard import BOUNDS, reference_gt  # noqa: E402
from scripts.lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import micro_f1  # noqa: E402
from scripts.pairwise_permutation_test import assign_source_tiles  # noqa: E402
from scripts.lib_permutation import paired_permutation_test  # noqa: E402
from scripts.extract_candidates import crop_region, resolve_raster_path  # noqa: E402

SCR = Path("/tmp/vdate")
RUN = "55maps-text-min-generalisation"
K4C, K4V = ROOT / "outputs" / RUN / "crops", ROOT / "outputs" / RUN / "verified"
SHC, SHV = DEPLOY / RUN / "crops", DEPLOY / RUN / "verified"
UPD = ROOT / "outputs/55maps-text-min-n10-uplift"
UPC, UPV = UPD / "crops-3of10", UPD / "verified-3of10"
RASTERS = ROOT / "inputs/rasters/Russian1981_32635"
TOLS = (1.0, 2.0, 5.0)
POINTS = [(0.15, 3), (0.15, 4), (0.20, 3), (0.20, 4)]


def extras(cdir: Path, subset: str) -> pd.DataFrame:
    """Per-candidate fields load_manifest_probs drops (manifest order)."""
    cands = json.loads((cdir / "candidate_manifest.json").read_text())["candidates"]
    return pd.DataFrame({
        "subset": subset,
        "candidate_id": [c["candidate_id"] for c in cands],
        "crop_path": [str(cdir / c["crop_file"]) for c in cands],
        "passes": [frozenset(c["properties"]["contributing_passes"]) for c in cands],
        "cx": [c["centroid_x"] for c in cands],
        "cy": [c["centroid_y"] for c in cands],
    })


def sha(path: str) -> str | None:
    p = Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def regen(task):
    """Regenerate one crop with the repo's crop_region; return its sha256."""
    tag, src_tile, cx, cy = task
    raster = resolve_raster_path(src_tile, RASTERS)
    if raster is None:
        return None
    out = SCR / "crops" / f"{tag}.png"
    ok = crop_region(raster, (cx, cy), 75, out)
    if not ok:
        return None
    h = hashlib.sha256(out.read_bytes()).hexdigest()
    out.unlink()
    return h


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def newcombe(k1, n1, k2, n2):
    """Newcombe hybrid-score 95 % CI for p1 - p2."""
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    d = p1 - p2
    lo = d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return d, lo, hi


def agree(p0: np.ndarray, p1: np.ndarray) -> dict:
    d = p1 - p0
    n = len(d)
    out = {"n": n, "identical": float(np.mean(d == 0)),
           "mean_abs": float(np.mean(np.abs(d))),
           "median_abs": float(np.median(np.abs(d))),
           "signed_mean": float(np.mean(d))}
    for t in (0.15, 0.20):
        a0, a1 = p0 >= t, p1 >= t
        k = int((a0 != a1).sum())
        out[f"flip_{t}"] = [k, n, k / n if n else float("nan"), *wilson(k, n)]
        out[f"acc_early_{t}"] = int(a0.sum())
        out[f"acc_late_{t}"] = int(a1.sum())
        out[f"up_{t}"] = int((~a0 & a1).sum())
        out[f"down_{t}"] = int((a0 & ~a1).sum())
    return out


def standardised_flip(src_p0, src_flip, tgt_p0) -> float:
    """Flip rate of src re-weighted to tgt's distribution of earlier p."""
    s = pd.DataFrame({"v": src_p0, "f": src_flip}).groupby("v")["f"].mean()
    w = pd.Series(tgt_p0).value_counts(normalize=True)
    w = w[w.index.isin(s.index)]
    w = w / w.sum()
    return float((s.reindex(w.index) * w).sum())


def main() -> None:
    SCR.mkdir(exist_ok=True)
    (SCR / "crops").mkdir(exist_ok=True)
    res: dict = {}

    # --- TM family exactly as build_families (TM branch) ---
    orig = load_manifest_probs(K4C, K4V)
    inc = load_manifest_probs(SHC, SHV)
    if not (orig["vote_count"] >= 4).all() or not (inc["vote_count"] == 3).all():
        raise RuntimeError("TM: unexpected vote structure")
    tm = pd.concat([orig, inc], ignore_index=True)
    ex = pd.concat([extras(K4C, "k4"), extras(SHC, "shell")], ignore_index=True)
    assert np.allclose(ex["cx"], tm.geometry.x) and np.allclose(ex["cy"], tm.geometry.y)
    for c in ("subset", "candidate_id", "crop_path", "passes"):
        tm[c] = ex[c].values
    pre = json.loads((K4V / "probabilities.json.pre-cleanup-20260503T015552.backup")
                     .read_text())["results"]
    tm["cleanup_0503"] = [(s == "k4") and (prob_key(c) not in pre)
                          for s, c in zip(tm["subset"], tm["candidate_id"])]
    res["n"] = {"k4": int((tm.subset == "k4").sum()),
                "shell": int((tm.subset == "shell").sum()),
                "k4_cleanup_0503": int(tm.cleanup_0503.sum())}

    upl = load_manifest_probs(UPC, UPV)
    uex = extras(UPC, "upl")
    upl["passes"] = uex["passes"].values
    upl["crop_path"] = uex["crop_path"].values
    res["n"]["upl"] = len(upl)

    # --- mutual-nearest matching ---
    T = np.c_[tm.geometry.x, tm.geometry.y]
    U = np.c_[upl.geometry.x, upl.geometry.y]
    d_tu, j = cKDTree(U).query(T)
    _d_ut, i = cKDTree(T).query(U)
    tm["u_idx"], tm["d"] = j, d_tu
    tm["mutual"] = i[j] == np.arange(len(T))
    tm["p_upl"] = upl["mound_probability"].to_numpy()[j]
    tm["upl_votes"] = upl["vote_count"].to_numpy()[j]
    first5 = {f"run_{n}" for n in range(1, 6)}
    tm["pass_consistent"] = [p == (q & first5) for p, q in
                             zip(tm["passes"], upl["passes"].to_numpy()[j])]
    tm["upl_src_same"] = (tm["source_tile"].to_numpy()
                          == upl["source_tile"].to_numpy()[j])
    match = {}
    for s in ("k4", "shell"):
        m = tm.subset == s
        match[s] = {"d_quantiles_mutual": [float(x) for x in np.quantile(
            tm.loc[m & tm.mutual, "d"], [0.25, 0.5, 0.75, 0.9, 0.99])],
            "mutual_any": int((m & tm.mutual).sum())}
        for t in TOLS:
            mm = m & tm.mutual & (tm.d <= t)
            match[s][f"{t:g}m"] = [int(mm.sum()), int(m.sum()),
                                   float(mm.sum() / m.sum()),
                                   float(tm.loc[mm, "pass_consistent"].mean()),
                                   float(tm.loc[mm, "upl_src_same"].mean())]
    res["match"] = match

    # --- crop identity (regenerate with the repo's crop_region) ---
    tm["sha_disk"] = [sha(p) for p in tm["crop_path"]]
    tasks = [(f"tm{r}", st, x, y) for r, (st, x, y) in
             enumerate(zip(tm.source_tile, tm.geometry.x, tm.geometry.y))]
    m5 = tm.mutual & (tm.d <= 5.0)
    utasks = [(f"up{r}", upl.source_tile.iat[u], upl.geometry.x.iat[u],
               upl.geometry.y.iat[u]) for r, u in zip(tm.index[m5], tm.u_idx[m5])]
    with Pool(16) as pool:
        tm["sha_regen"] = pool.map(regen, tasks, chunksize=64)
        uh = pool.map(regen, utasks, chunksize=64)
    tm["sha_upl_regen"] = None
    tm.loc[m5, "sha_upl_regen"] = uh
    res["crop_validation"] = {
        s: [int(((tm.subset == s) & (tm.sha_disk == tm.sha_regen)).sum()),
            int((tm.subset == s).sum()),
            int(((tm.subset == s) & tm.sha_disk.isna()).sum())]
        for s in ("k4", "shell")}
    tm["crop_identical"] = m5 & (tm.sha_upl_regen == tm.sha_disk)
    tm["crop_identical_regen"] = m5 & (tm.sha_upl_regen == tm.sha_regen)
    for s in ("k4", "shell"):
        for t in TOLS:
            mm = (tm.subset == s) & tm.mutual & (tm.d <= t)
            match[s][f"{t:g}m"].append(int((mm & tm.crop_identical).sum()))
            match[s][f"{t:g}m"].append(int((mm & tm.crop_identical_regen).sum()))

    # --- agreement ---
    agr = {}
    for s, excl in (("k4", True), ("shell", False)):
        base = (tm.subset == s) & ~(tm.cleanup_0503 if excl
                                    else pd.Series(False, index=tm.index))
        for t in TOLS:
            mm = base & tm.mutual & (tm.d <= t)
            agr[f"{s}_{t:g}m"] = agree(tm.loc[mm, "mound_probability"].to_numpy(),
                                       tm.loc[mm, "p_upl"].to_numpy())
        mm = base & tm.crop_identical
        agr[f"{s}_identical_crop"] = agree(tm.loc[mm, "mound_probability"].to_numpy(),
                                           tm.loc[mm, "p_upl"].to_numpy())
        mm = base & tm.mutual & (tm.d <= 2.0) & ~tm.crop_identical
        agr[f"{s}_2m_nonidentical"] = agree(tm.loc[mm, "mound_probability"].to_numpy(),
                                            tm.loc[mm, "p_upl"].to_numpy())
    # cleanup 39 separately (May 3 vs June 11)
    mm = tm.cleanup_0503 & tm.mutual & (tm.d <= 2.0)
    agr["k4cleanup_2m"] = agree(tm.loc[mm, "mound_probability"].to_numpy(),
                                tm.loc[mm, "p_upl"].to_numpy())
    res["agree"] = agr

    # drift estimates: k4 minus shell flip rate, raw and composition-adjusted
    drift = {}
    for lab, sel in (("2m", lambda s: (tm.subset == s) & tm.mutual & (tm.d <= 2.0)),
                     ("identical_crop", lambda s: (tm.subset == s) & tm.crop_identical)):
        a = sel("k4") & ~tm.cleanup_0503
        b = sel("shell")
        for t in (0.15, 0.20):
            fa = ((tm.loc[a, "mound_probability"] >= t) != (tm.loc[a, "p_upl"] >= t))
            fb = ((tm.loc[b, "mound_probability"] >= t) != (tm.loc[b, "p_upl"] >= t))
            d, lo, hi = newcombe(int(fa.sum()), int(a.sum()), int(fb.sum()), int(b.sum()))
            adj_shell = standardised_flip(tm.loc[b, "mound_probability"], fb,
                                          tm.loc[a, "mound_probability"])
            adj_k4 = standardised_flip(tm.loc[a, "mound_probability"], fa,
                                       tm.loc[b, "mound_probability"])
            drift[f"{lab}_{t}"] = {"k4": float(fa.mean()), "shell": float(fb.mean()),
                                   "diff": d, "ci": [lo, hi],
                                   "shell_std_to_k4": adj_shell,
                                   "k4_minus_shell_std": float(fa.mean()) - adj_shell,
                                   "k4_std_to_shell": adj_k4}
    res["drift"] = drift

    # --- scoring on the board path ---
    bounds = gpd.read_file(BOUNDS)
    if bounds.crs is None:
        bounds = bounds.set_crs("EPSG:4326")
    bounds = bounds.to_crs("EPSG:32635")
    ref = reference_gt("r2")
    base = tm[["vote_count", "mound_probability", "source_tile", "geometry"]].copy()
    base = gpd.GeoDataFrame(base, geometry="geometry", crs="EPSG:32635")
    base = assign_source_tiles(base, bounds)
    rep2 = tm.mutual & (tm.d <= 2.0)
    variants = {"A_committed": tm["mound_probability"].to_numpy(),
                "B_allJune": np.where(rep2, tm.p_upl, tm.mound_probability),
                "B_k4only": np.where(rep2 & (tm.subset == "k4"), tm.p_upl,
                                     tm.mound_probability),
                "B_identcrop": np.where(tm.crop_identical, tm.p_upl,
                                        tm.mound_probability)}
    res["kept_original_B"] = {s: float((~rep2[tm.subset == s]).mean())
                              for s in ("k4", "shell")}
    res["kept_original_identcrop"] = {s: float((~tm.crop_identical[tm.subset == s]).mean())
                                      for s in ("k4", "shell")}
    tiles = {}
    scores = {}
    for v, p in variants.items():
        g = base.copy()
        g["mound_probability"] = p
        for (pt, k) in POINTS:
            sub = g[(g["mound_probability"] >= pt) & (g["vote_count"] >= k)]
            tmx = compute_per_tile_tp_fp_fn(sub, ref, bounds, buffer_metres=BUFFER_M)
            tmx = tmx.sort_values("tile_name").reset_index(drop=True)
            tiles[(v, pt, k)] = tmx
            tp, fp, fn = int(tmx.tp.sum()), int(tmx.fp.sum()), int(tmx.fn.sum())
            scores[f"{v}|{pt}|k{k}"] = {"n": len(sub), "tp": tp, "fp": fp, "fn": fn,
                                        "f1": micro_f1(tp, fp, fn)}
    res["scores"] = scores
    names = None
    for key, tmx in tiles.items():
        if names is None:
            names = list(tmx.tile_name)
        assert list(tmx.tile_name) == names

    def arm(key):
        t = tiles[key]
        return {c: t[c].to_numpy(dtype=float) for c in ("tp", "fp", "fn")}

    tests = {}
    pairs = []
    for v in variants:
        pairs.append((f"{v}: k3-k4 @0.15", (v, 0.15, 3), (v, 0.15, 4)))
        pairs.append((f"{v}: (0.20,k3)-(0.15,k4)", (v, 0.20, 3), (v, 0.15, 4)))
    pairs.append(("TM-k4 June-April @(0.15,k4)", ("B_allJune", 0.15, 4),
                  ("A_committed", 0.15, 4)))
    pairs.append(("TM-k4 June-April @(0.20,k4)", ("B_allJune", 0.20, 4),
                  ("A_committed", 0.20, 4)))
    pairs.append(("TM-oracle June-mixed @(0.20,k3)", ("B_allJune", 0.20, 3),
                  ("A_committed", 0.20, 3)))
    pairs.append(("TM k3 June-mixed @(0.15,k3)", ("B_allJune", 0.15, 3),
                  ("A_committed", 0.15, 3)))
    for lab, ka, kb in pairs:
        r = paired_permutation_test(arm(ka), arm(kb), n_permutations=10_000, seed=42)
        f = r["metrics"]["f1"]
        tests[lab] = {"a": f["a"], "b": f["b"], "diff": f["observed_diff"],
                      "p": f["p_value"], "null_std": f["null_std"],
                      "n_tiles": r["n_tiles"], "discordant": r["n_discordant_tiles"]}
    res["tests"] = tests

    # flip counts among scored decisions for the k4 set (0.15) under A vs B
    k4m = (tm.subset == "k4")
    a15 = (tm.mound_probability >= 0.15) & k4m
    b15 = (variants["B_allJune"] >= 0.15) & k4m
    res["k4_decisions_015"] = {"accept_A": int(a15.sum()), "accept_B": int(b15.sum()),
                               "flips": int((a15 != b15).sum()), "n": int(k4m.sum())}
    (SCR / "results.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
