"""W2.4: re-test the class-C2 contrasts with the paired tile-swap permutation.

Read-only harness. Imports each committed C2 script, wraps its
paired_bootstrap so that every call ALSO runs permutation_test_float
(10,000 perms, seed 42) on the very same per-tile arrays, redirects every
output path to /tmp/w2/c2/, and runs the script's own main().
Usage: python c2_retest.py <script_name>
"""
import importlib
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path.home() / "Code/map-reader-llm"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
from n1_baseline_leaderboard_tiering import permutation_test_float  # noqa: E402

name = sys.argv[1]
OUT = Path("/tmp/w2/c2") / name
OUT.mkdir(parents=True, exist_ok=True)
mod = importlib.import_module(f"scripts.{name}")
orig = mod.paired_bootstrap
captured = []
seen = {}


def wrapped(a, b, n_iter, seed=42):
    res = orig(a, b, n_iter, seed=seed)
    A = np.stack([np.asarray(a[k], float) for k in ("tp", "fp", "fn")], 1)
    B = np.stack([np.asarray(b[k], float) for k in ("tp", "fp", "fn")], 1)
    key = (A.tobytes(), B.tobytes())
    if key not in seen:
        pt = permutation_test_float(A[:, 0], A[:, 1], A[:, 2], B[:, 0], B[:, 1], B[:, 2],
                                    10_000, 42)
        seen[key] = {"perm_p": pt["p_value"], "perm_obs": pt["observed_diff"],
                     "n_tiles": pt["n_tiles"],
                     "k_discordant": int((A != B).any(1).sum())}
    captured.append({"call": len(captured), "n_iter": n_iter, "boot_delta": res["delta"],
                     "boot_p": res["p_two_sided"], "boot_ci": [res["ci_lower"], res["ci_upper"]],
                     **seen[key]})
    return res


mod.paired_bootstrap = wrapped
argv = [name]
if name == "stride_verifier_analysis":
    mod.OUT_DIR = OUT
    # The committed JSON carries two ladder contrasts the committed script
    # does not define; add them (cells inferred from their names, confirmed
    # by reproducing the committed bootstrap delta and p).
    mod.CONTRASTS["ladder384: 256-stride - 336-stride"] = ("g384_ov128", "g384_ov048")
    mod.CONTRASTS["ladder384: 144-stride - 256-stride"] = ("g384_ov240", "g384_ov128")
elif name == "grid_incumbent_rescore":
    mod.OUT_PATH = OUT / "incumbents_common_footprint.json"
else:
    argv += ["--output-dir", str(OUT)]
sys.argv = argv
rc = None
try:
    rc = mod.main()
except ValueError as exc:  # grid_incumbent_rescore logs OUT_PATH relative to the repo
    print("main raised after its contrasts:", exc)
finally:
    (OUT / "permutation_capture.json").write_text(json.dumps(captured, indent=1, default=float))
print("rc", rc, "calls", len(captured))
for c in captured:
    print(c)
