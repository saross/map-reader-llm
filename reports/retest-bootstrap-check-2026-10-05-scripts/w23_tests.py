"""W2.3 step 3: run both tests on every replicate pair (read-only).

(a) The retest bootstrap EXACTLY as coded in fc832dfa9
    lib_advanced_metrics.bootstrap_effect_size_ci (:635-751): paired tile
    resampling (same tile draw for both arms), micro-F1/P/R from pooled
    TP/FP/FN, B = 1000, default_rng(42), p = max(2*min(P(d<=0), P(d>0)), 1/B).
    Vectorised; rng.integers(0, n, (B, n)) is the same stream as B calls of
    rng.choice(tiles, n, replace=True) (checked). Tile order = bounds order
    (the original used list(set(...)), so its order and hence its digits
    depend on PYTHONHASHSEED; distributionally identical).
(b) permutation_test_float imported from n1_baseline_leaderboard_tiering
    (the kernel era1_leaderboard_tiering.py imports), 10,000 perms, seed 42.
Both run on the same per-tile arrays (the board's scoring path).
"""
import itertools
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

REPO = Path.home() / "Code/map-reader-llm"
sys.path.insert(0, str(REPO / "scripts"))
from n1_baseline_leaderboard_tiering import permutation_test_float  # noqa: E402

B = 1000
SEED = 42
ARR = {}


def prf(s):
    tp, fp, fn = s[..., 0], s[..., 1], s[..., 2]
    p = np.divide(tp, tp + fp, out=np.zeros_like(tp), where=(tp + fp) > 0)
    r = np.divide(tp, tp + fn, out=np.zeros_like(tp), where=(tp + fn) > 0)
    f = np.divide(2 * p * r, p + r, out=np.zeros_like(tp), where=(p + r) > 0)
    return p, r, f


def boot_p(d):
    return float(max(2.0 * min(np.mean(d <= 0), np.mean(d > 0)), 1.0 / len(d)))


def retest_bootstrap(a, b):
    n = a.shape[0]
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, (B, n))
    sa = a[idx].sum(axis=1)
    sb = b[idx].sum(axis=1)
    pa, ra, fa = prf(sa)
    pb, rb, fb = prf(sb)
    df, dp, dr = fa - fb, pa - pb, ra - rb
    return {"boot_mean": float(df.mean()), "boot_ci_lo": float(np.percentile(df, 2.5)),
            "boot_ci_hi": float(np.percentile(df, 97.5)), "boot_p_f1": boot_p(df),
            "boot_p_prec": boot_p(dp), "boot_p_rec": boot_p(dr),
            "boot_frac_zero": float(np.mean(df == 0))}


def run_pair(job):
    a = ARR[job["file"]][job["ia"]]
    b = ARR[job["file"]][job["ib"]]
    out = dict(job["meta"])
    out["k_discordant"] = int((a != b).any(axis=1).sum())
    out.update(retest_bootstrap(a, b))
    pt = permutation_test_float(a[:, 0], a[:, 1], a[:, 2], b[:, 0], b[:, 1], b[:, 2], 10_000, SEED)
    out.update({"f1_a": pt["f1_a"], "f1_b": pt["f1_b"], "obs_diff": pt["observed_diff"],
                "perm_p": pt["p_value"], "perm_null_std": pt["null_std"], "n_tiles": pt["n_tiles"]})
    return out


def init(files):
    for f in files:
        d = np.load(f)
        ARR[f] = d["arr"]


if __name__ == "__main__":
    index = {r["key"]: r for r in json.loads(Path("/tmp/w2/pass_index.json").read_text())}
    files = sorted(str(p) for p in Path("/tmp/w2").glob("pertile_*m.npz"))
    jobs_small, jobs_big = [], []
    arm_jobs = []
    for f in files:
        d = np.load(f)
        keys = list(d["keys"])
        scope, buf = Path(f).stem.split("_")[1], int(Path(f).stem.split("_")[2][:-1])
        pos = {k: i for i, k in enumerate(keys)}
        by_group = {}
        for k in keys:
            by_group.setdefault(index[k]["group"], []).append(k)
        for g, ks in sorted(by_group.items()):
            rng = np.random.default_rng(1000 + g)
            perm = list(rng.permutation(len(ks)))
            disjoint = {frozenset((ks[perm[i]], ks[perm[i + 1]])) for i in range(0, len(perm) - 1, 2)}
            for ka, kb in itertools.combinations(ks, 2):
                ra, rb = index[ka], index[kb]
                same_arm = (ra["run_id"], ra["arm"]) == (rb["run_id"], rb["arm"])
                first_pair = (not same_arm) and ka == min((k for k in ks if index[k]["arm"] == ra["arm"] and index[k]["run_id"] == ra["run_id"]), key=lambda k: int(index[k]["run_dir"].rsplit("_", 1)[1])) \
                    and kb == min((k for k in ks if index[k]["arm"] == rb["arm"] and index[k]["run_id"] == rb["run_id"]), key=lambda k: int(index[k]["run_dir"].rsplit("_", 1)[1]))
                meta = {"group": g, "scope": scope, "buffer": buf, "key_a": ka, "key_b": kb,
                        "same_arm": same_arm, "first_pass_pair": bool(first_pair),
                        "disjoint": frozenset((ka, kb)) in disjoint,
                        "temperature": "|".join(str(t) for t in sorted(set(ra["temperature"]) | set(rb["temperature"]), key=str))}
                job = {"file": f, "ia": pos[ka], "ib": pos[kb], "meta": meta}
                (jobs_big if scope == "maps55" else jobs_small).append(job)
    print(len(jobs_small), "small pairs;", len(jobs_big), "55-map pairs", flush=True)
    with Pool(20, initializer=init, initargs=(files,)) as pool:
        res = pool.map(run_pair, jobs_small, chunksize=8)
    with Pool(6, initializer=init, initargs=(files,)) as pool:
        res += pool.map(run_pair, jobs_big, chunksize=1)
    Path("/tmp/w2/calibration_pairs.json").write_text(json.dumps(res))
    import csv
    with open("/tmp/w2/calibration_pairs.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(res[0].keys()))
        w.writeheader()
        w.writerows(res)
    print("done", len(res), flush=True)
