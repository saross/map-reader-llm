"""Collate H8 v2 permutation test results and apply Benjamini-Hochberg FDR.

Reads the 7 preregistered contrasts under results/h8-v2/permutation-t4/ and
produces a summary with raw p-values, BH-adjusted p-values, and significance
decisions at q=0.05.
"""

import json
from pathlib import Path

CONTRASTS = [
    ("C1", "add Canon-",                              "pure-positive-canon", "canonical"),
    ("C2", "add HP",                                  "canonical",           "plus-hp"),
    ("C3", "add HN",                                  "plus-hp",             "scale-8"),
    ("B1", "HP-only vs balanced at size 13",          "plus-hp",             "scale-4"),
    ("S1", "Scale-4 -> Scale-8",                      "scale-4",             "scale-8"),
    ("S2", "Scale-8 -> Scale-16",                     "scale-8",             "scale-16"),
    ("S3", "Scale-16 -> Scale-32",                    "scale-16",            "scale-32"),
]

BASE = Path("results/h8-v2/permutation-t4")


def load_result(code, a, b):
    path = BASE / f"{code}-{a}-vs-{b}" / "pairwise_permutation_result.json"
    if not path.exists():
        return None
    return json.load(open(path))


rows = []
for code, desc, a, b in CONTRASTS:
    d = load_result(code, a, b)
    if d is None:
        rows.append({"code": code, "desc": desc, "a": a, "b": b, "p": None})
        continue
    pt = d["permutation_test"]
    ca = d["condition_a"]
    cb = d["condition_b"]
    rows.append({
        "code": code,
        "desc": desc,
        "a": a,
        "b": b,
        "f1_a": ca["f1"],
        "f1_b": cb["f1"],
        "p_a": ca["precision"],
        "r_a": ca["recall"],
        "p_b": cb["precision"],
        "r_b": cb["recall"],
        "delta": pt["observed_f1_diff"],
        "p": pt["p_value"],
        "wins_a": pt["wins_a"],
        "losses_a": pt["losses_a"],
        "ties": pt["ties"],
        "n_tiles": pt["n_tiles"],
    })

# Benjamini-Hochberg FDR at q=0.05
m = sum(1 for r in rows if r.get("p") is not None)
q = 0.05
ranked = sorted(
    [r for r in rows if r.get("p") is not None],
    key=lambda r: r["p"],
)
for k, r in enumerate(ranked):
    r["rank"] = k + 1
    r["bh_adjusted_p"] = min(r["p"] * m / (k + 1), 1.0)
# Running max from bottom (monotone)
for k in range(len(ranked) - 2, -1, -1):
    ranked[k]["bh_adjusted_p"] = min(
        ranked[k]["bh_adjusted_p"],
        ranked[k + 1]["bh_adjusted_p"],
    )
for r in ranked:
    r["significant_at_q05"] = r["bh_adjusted_p"] < q

by_code = {r["code"]: r for r in ranked}

print("=" * 108)
print("H8 v2 — tile-level permutation tests, greedy t=4, 10,000 permutations, seed 42")
print("Benjamini-Hochberg FDR correction at q=0.05 over 7 preregistered contrasts")
print("=" * 108)
print()
print(
    f"{'Code':<5}{'Contrast':<38}"
    f"{'F1 (a -> b)':<22}{'ΔF1':>9}{'raw p':>10}{'BH-adj p':>11}{'signif?':>10}"
)
print("-" * 108)
for row in rows:
    if row.get("p") is None:
        print(f"{row['code']:<5}{row['desc']:<38}{'MISSING':<22}")
        continue
    adj = by_code.get(row["code"], {})
    f1str = f"{row['f1_a']:.3f} -> {row['f1_b']:.3f}"
    sig = "YES" if adj.get("significant_at_q05") else "no"
    print(
        f"{row['code']:<5}{row['desc']:<38}"
        f"{f1str:<22}"
        f"{row['delta']:+9.4f}"
        f"{row['p']:>10.4f}"
        f"{adj.get('bh_adjusted_p', 0):>11.4f}"
        f"{sig:>10}"
    )

print()
print("=" * 108)
print("Per-tile pairing (327 tiles, paired micro-F1 swap)")
print("=" * 108)
print(f"{'Code':<5}{'Contrast':<38}{'A wins':>10}{'B wins':>10}{'Ties':>10}")
print("-" * 108)
for row in rows:
    if row.get("p") is None:
        continue
    print(
        f"{row['code']:<5}{row['desc']:<38}"
        f"{row['wins_a']:>10}"
        f"{row['losses_a']:>10}"
        f"{row['ties']:>10}"
    )

# Overall summary
any_sig = any(r.get("significant_at_q05") for r in ranked)
print()
print("=" * 108)
print("OVERALL:")
if any_sig:
    sig_contrasts = [r["code"] for r in ranked if r.get("significant_at_q05")]
    print(f"  {len(sig_contrasts)} contrast(s) significant after BH-FDR (q=0.05): {', '.join(sig_contrasts)}")
else:
    print("  ZERO contrasts are significant after BH-FDR correction at q=0.05.")
    print("  All seven preregistered H8 contrasts are NULL.")
    print("  Combined with the H10 null (pool size), this gives a strong null result")
    print("  for the entire hard-example library axis at the proposer stage.")
print("=" * 108)

# Write JSON summary
out = {
    "method": "Benjamini-Hochberg FDR at q=0.05 over 7 H8 preregistered contrasts",
    "operating_point": "greedy t=4, 20 m buffer, 327-tile H10 test set",
    "n_contrasts": m,
    "n_permutations": 10000,
    "seed": 42,
    "q": q,
    "any_significant": any_sig,
    "contrasts": rows,
}
out_path = BASE / "fdr_summary.json"
with open(out_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"\nSummary written to: {out_path}")
