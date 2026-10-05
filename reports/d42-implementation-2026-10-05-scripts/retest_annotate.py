"""Restore the committed retest evaluations and annotate their pairwise rows (D42).

Run on sapphire in the repo root after the D42 regeneration. For each of the
nine results/retest/phase2*-evaluation.json files: read the regenerated
version (working tree) and the committed one (HEAD); measure the drift;
write the COMMITTED content back with a permutation_retest block on each
pairwise row and a d42_annotation note at the phase level.
"""
import json
import subprocess
import sys
from pathlib import Path

FILES = sorted(Path("results/retest").glob("phase2*-evaluation.json"))
NOTE = ("PI ruling D42 (2026-10-05): 'significant' in each pairwise row is the "
        "RETIRED reading (bootstrap CI excludes zero, uncorrected), kept as "
        "published. The authoritative test is permutation_retest: the paired "
        "tile-swap permutation test (10,000 permutations, seed 42, 20 m) with BH "
        "within the phase, computed 2026-10-05 by scripts/evaluate_retest_all.py "
        "at commit {commit} on the input files as they now stand. Those inputs "
        "re-score within {drift:.4f} F1 of the values recorded here (evaluator "
        "changes since March); the recorded point estimates and CIs are left as "
        "published. See reports/d42-implementation-2026-10-05.md.")
commit = subprocess.run(["git", "rev-parse", "--short=9", "HEAD"], capture_output=True,
                        text=True, check=True).stdout.strip()
summary = []
for f in FILES:
    raw = subprocess.run(["git", "show", f"HEAD:{f}"], capture_output=True, text=True,
                         check=True).stdout
    old = json.loads(raw)
    new = json.loads(f.read_text())
    key = next(iter(old))
    o, n = old[key], new[key]
    drift = max(abs(o["conditions"][c]["f1"] - n["conditions"][c]["f1"])
                for c in o["conditions"])
    newpw = {(r["condition_a"], r["condition_b"]): r for r in n["pairwise"]}
    for row in o["pairwise"]:
        r = newpw[(row["condition_a"], row["condition_b"])]
        fd = r["f1_difference"]
        row["permutation_retest"] = {
            "f1_p": fd["p_value"],
            "precision_p": r["precision_difference"]["p_value"],
            "recall_p": r["recall_difference"]["p_value"],
            "f1_bh_within_phase": r["f1_bh_adjusted_p"],
            "significant_bh_within_phase": r["significant"],
            "method": "paired tile-swap permutation, 10,000, seed 42, 20 m (D42)",
        }
        summary.append((f.name, row["condition_a"], row["condition_b"], row["significant"],
                        r["significant"], fd["p_value"], r["f1_bh_adjusted_p"]))
    o["d42_annotation"] = NOTE.format(commit=commit, drift=drift)
    indent = 2 if raw.startswith('{\n  "') else 1
    f.write_text(json.dumps(old, indent=indent) + ("\n" if raw.endswith("\n") else ""))
    print(f"{f.name}: max per-condition F1 drift {drift:.4f}")
changed = [s for s in summary if s[3] != s[4]]
print(f"{len(summary)} pairwise rows; verdict changes (old CI-uncorrected -> new BH): {len(changed)}")
for s in changed:
    print("  ", s)
json.dump(summary, open("/tmp/d42/retest_annotation_summary.json", "w"), indent=1)
