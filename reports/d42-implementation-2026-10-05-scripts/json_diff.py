"""Classify differences between a committed JSON (git HEAD) and the working copy.

Usage: python json_diff.py <repo-relative path> [...]
Prints, per file, the leaf paths that differ, split into p-value fields
(expected to move under D42) and everything else (must be explained).
"""
import json
import subprocess
import sys

P_KEYS = {"p_two_sided", "p_value", "p_method", "n_permutations", "n_discordant_tiles",
          "prop_le_zero", "prop_gt_zero", "p_at_floor", "p_raw", "p", "bh_adjusted_p",
          "f1_bh_adjusted_p", "significant", "fdr_significant", "initially_significant",
          "fdr_adjusted_p", "ci_excludes_zero", "permutation", "p_is_zero"}
VOLATILE = {"generated_at", "generated", "timestamp", "run_at", "created_at"}


def leaves(x, path=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, f"{path}/{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, x


def classify(path):
    keys = {seg.split("[")[0] for seg in path.split("/") if seg}
    if keys & P_KEYS:
        return "p"
    if keys & VOLATILE:
        return "volatile"
    return "other"


for rel in sys.argv[1:]:
    old = json.loads(subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True,
                                    text=True, check=True).stdout)
    new = json.load(open(rel))
    lo, ln = dict(leaves(old)), dict(leaves(new))
    out = {"p": [], "volatile": [], "other": []}
    for k in sorted(set(lo) | set(ln)):
        a, b = lo.get(k, "<absent>"), ln.get(k, "<absent>")
        if a != b:
            if isinstance(a, float) and isinstance(b, float) and abs(a - b) < 1e-12:
                continue
            out[classify(k)].append((k, a, b))
    print(f"== {rel}: p-fields {len(out['p'])}, volatile {len(out['volatile'])}, "
          f"OTHER {len(out['other'])}")
    for k, a, b in out["other"][:40]:
        print(f"   OTHER {k}: {str(a)[:60]} -> {str(b)[:60]}")
    for k, a, b in out["p"]:
        if k.split("/")[-1] in ("p_two_sided", "p_value", "p", "p_raw", "significant",
                                "fdr_significant"):
            print(f"   p {k}: {a} -> {b}")
