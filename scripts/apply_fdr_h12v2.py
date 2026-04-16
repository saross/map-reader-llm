"""Collate H12 v2 permutation test results and apply Benjamini-Hochberg FDR.

Reads the 3 preregistered pairwise contrasts under
``results/h12-v2/permutation-t4/`` and produces a summary with raw p-values,
BH-adjusted p-values, and significance decisions at q=0.05.

H12 v2 tests the HP:HN ratio at fixed total hard count = 8 across three
conditions:

    R1  HN-heavy (1:3, 2 HP + 6 HN)
    R2  balanced (1:1, 4 HP + 4 HN)  — reused from H8 v2 Scale-8
    R3  HP-heavy (3:1, 6 HP + 2 HN)

All pairwise contrasts (R1-R2, R2-R3, R1-R3) are run because H12 has no
preferred directional pair — the goal is to establish whether ratio affects
F1 at all under the production carry-forward settings (T=0.7, thinking=high,
384 px, K=5, detect_brief-text-image.md). Adapted from apply_fdr_h8v2.py;
see also protocol-errata E52.
"""

import json
from pathlib import Path

CONTRASTS = [
    ("R12", "R1 (HN-heavy)   vs R2 (balanced)", "r1-hn-heavy",  "r2-balanced"),
    ("R23", "R2 (balanced)   vs R3 (HP-heavy)", "r2-balanced",  "r3-hp-heavy"),
    ("R13", "R1 (HN-heavy)   vs R3 (HP-heavy)", "r1-hn-heavy",  "r3-hp-heavy"),
]

BASE = Path("results/h12-v2/permutation-t4")


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
print("H12 v2 — tile-level permutation tests, greedy t=4, 10,000 permutations, seed 42")
print("Benjamini-Hochberg FDR correction at q=0.05 over 3 pairwise contrasts")
print("=" * 108)
print()
print(
    f"{'Code':<5}{'Contrast':<40}"
    f"{'F1 (a -> b)':<22}{'ΔF1':>9}{'raw p':>10}{'BH-adj p':>11}{'signif?':>10}"
)
print("-" * 108)
for row in rows:
    if row.get("p") is None:
        print(f"{row['code']:<5}{row['desc']:<40}{'MISSING':<22}")
        continue
    adj = by_code.get(row["code"], {})
    f1str = f"{row['f1_a']:.3f} -> {row['f1_b']:.3f}"
    sig = "YES" if adj.get("significant_at_q05") else "no"
    print(
        f"{row['code']:<5}{row['desc']:<40}"
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
print(f"{'Code':<5}{'Contrast':<40}{'A wins':>10}{'B wins':>10}{'Ties':>10}")
print("-" * 108)
for row in rows:
    if row.get("p") is None:
        continue
    print(
        f"{row['code']:<5}{row['desc']:<40}"
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
    print(
        f"  {len(sig_contrasts)} contrast(s) significant after BH-FDR (q=0.05): "
        f"{', '.join(sig_contrasts)}"
    )
else:
    print("  ZERO contrasts are significant after BH-FDR correction at q=0.05.")
    print("  All three H12 v2 pairwise contrasts are NULL.")
    print("  Combined with the H8 v2 null (library composition) and the H10 v2")
    print("  null (calibration-pool size), this closes the hard-example library")
    print("  axis at the proposer stage across all three preregistered factors.")
print("=" * 108)

# Write JSON summary
out = {
    "method": "Benjamini-Hochberg FDR at q=0.05 over 3 H12 pairwise contrasts",
    "operating_point": "greedy t=4, 20 m buffer, 327-tile H10 test set",
    "n_contrasts": m,
    "n_permutations": 10000,
    "seed": 42,
    "q": q,
    "any_significant": any_sig,
    "contrasts": rows,
}
out_path = BASE / "fdr_summary.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"\nSummary written to: {out_path}")
