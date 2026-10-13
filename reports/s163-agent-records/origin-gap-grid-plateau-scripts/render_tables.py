"""Render the delta report's tables from the extracted JSON, so no number is retyped.

Usage: python render_tables.py <ext_dir>   (reads committed.json, runA.json, rekeyed-runA.json)
"""

import json
import sys
from pathlib import Path

ext = Path(sys.argv[1])
c = json.loads((ext / "committed.json").read_text())
a = json.loads((ext / "runA.json").read_text())
r = json.loads((ext / "rekeyed-runA.json").read_text())

LABEL = {
    "g512_ov064": "512 px / 12.5 %",
    "g512_ov256": "512 px / 50 %",
    "g384_ov048": "384 px / 12.5 %",
    "g384_ov192": "384 px / 50 %",
}
CELLS = list(LABEL)


def f4(x):
    return "null" if x is None else f"{x:.4f}"


def arrow(b, f):
    return f4(b) if b == f else f"{f4(b)} → {f4(f)}"


print("### Grid consensus-only, K = 10 best per cell\n")
print(
    "| Cell | Operating point (c, k) | F1 @ 20 m | Precision | Recall | Tile MCC "
    "| Registered CI95 |"
)
print("|---|---|---|---|---|---|---|")
for cell in CELLS:
    b, f = c[f"grid/k10best/{cell}"], a[f"grid/k10best/{cell}"]
    cb, cf = c[f"grid/condition/{cell}"], a[f"grid/condition/{cell}"]
    assert (b["min_corroboration"], b["min_votes"]) == (f["min_corroboration"], f["min_votes"])
    print(
        f"| {LABEL[cell]} | c ≥ {b['min_corroboration']}, k ≥ {b['min_votes']} | "
        f"{arrow(b['f1'], f['f1'])} | {arrow(b['precision'], f['precision'])} | "
        f"{arrow(b['recall'], f['recall'])} | {arrow(b['mcc'], f['mcc'])} | "
        f"[{cb['f1_ci_lower']:.4f}, {cb['f1_ci_upper']:.4f}] → "
        f"[{cf['f1_ci_lower']:.4f}, {cf['f1_ci_upper']:.4f}] |"
    )

print("\n### Grid single pass (mean of ten) and K = 10 union\n")
print("| Cell | Single-pass F1 | Single-pass tile MCC | K = 10 union recall | K = 10 union F1 |")
print("|---|---|---|---|---|")
for cell in CELLS:
    sb, sf = c[f"grid/single/{cell}"], a[f"grid/single/{cell}"]
    ub, uf = c[f"grid/k10union/{cell}"], a[f"grid/k10union/{cell}"]
    print(
        f"| {LABEL[cell]} | {arrow(sb['f1'], sf['f1'])} | {arrow(sb['mcc'], sf['mcc'])} | "
        f"{arrow(ub['recall'], uf['recall'])} | {arrow(ub['f1'], uf['f1'])} |"
    )

print("\n### Grid single-pass contrasts (paired tile bootstrap, B = 10,000)\n")
print("| Contrast | ΔF1 | CI95 | p |")
print("|---|---|---|---|")
for k in sorted(x for x in c if x.startswith("grid/contrast/")):
    b, f = c[k], a[k]
    print(
        f"| {k.split('/', 2)[2]} | {b['delta']:+.4f} → {f['delta']:+.4f} | "
        f"[{b['ci_lower']:+.4f}, {b['ci_upper']:+.4f}] → [{f['ci_lower']:+.4f}, "
        f"{f['ci_upper']:+.4f}] | {b['p_two_sided']} → {f['p_two_sided']} |"
    )
b, f = c["grid/interaction"], a["grid/interaction"]
print(
    f"| interaction (difference of differences) | {b['difference_of_differences']:+.4f} → "
    f"{f['difference_of_differences']:+.4f} | [{b['ci_lower']:+.4f}, {b['ci_upper']:+.4f}] → "
    f"[{f['ci_lower']:+.4f}, {f['ci_upper']:+.4f}] | {b['p_two_sided']} → {f['p_two_sided']} |"
)

print("\n### Post-verifier: like-for-like K = 10 consensus baseline contrasts, and verifier gain\n")
print("| Contrast | ΔF1 | p |")
print("|---|---|---|")
for k in sorted(x for x in c if x.startswith("pv/baseline/")):
    b, f = c[k], a[k]
    print(
        f"| {k.split('/', 2)[2]} | {b['delta']:+.4f} → {f['delta']:+.4f} | "
        f"{b['p_two_sided']} → {f['p_two_sided']} |"
    )
print()
print("| Cell | Verified best F1 (unchanged) | Consensus-only K = 10 best | Verifier gain |")
print("|---|---|---|---|")
for cell in CELLS:
    print(
        f"| {LABEL[cell]} | {f4(a[f'pv/best/{cell}']['f1'])} | "
        f"{arrow(c[f'pv/consensus_committed/{cell}'], a[f'pv/consensus_committed/{cell}'])} | "
        f"{c[f'pv/gain/{cell}']:+.4f} → {a[f'pv/gain/{cell}']:+.4f} |"
    )

print("\n### Plateau board (13 cells), F1 @ 20 m\n")
print("| Rank after | Cell | F1 before | F1 after | Tier before → after |")
print("|---:|---|---|---|---|")
tb = {cell: i + 1 for i, t in enumerate(c["plateau/tiers"]) for cell in t}
ta = {cell: i + 1 for i, t in enumerate(a["plateau/tiers"]) for cell in t}
for i, cell in enumerate(a["plateau/order"], 1):
    print(
        f"| {i} | {cell} | {f4(c['plateau/f1'][cell])} | {f4(a['plateau/f1'][cell])} | "
        f"{tb[cell]} → {ta[cell]} |"
    )
print(
    f"\nsignificant pairs: {c['plateau/n_pairs_significant']} → "
    f"{a['plateau/n_pairs_significant']} of {a['plateau/n_pairs']}"
)
print("before:", c["plateau/significant_pairs"])
print("after: ", a["plateau/significant_pairs"])

print("\n### Phase A incumbents on the common footprint\n")
print(
    "| Incumbent | F1 @ 20 m | F1 @ 30 m | Tile MCC @ 20 m | Grid winner − incumbent @ 20 m (p) |"
)
print("|---|---|---|---|---|")
for k in sorted(x for x in c if x.startswith("phaseA/")):
    b, f = c[k], a[k]
    print(
        f"| {k.split('/', 1)[1]} | {arrow(b['f1_20'], f['f1_20'])} | "
        f"{arrow(b['f1_30'], f['f1_30'])} | "
        f"{arrow(b['mcc_20'], f['mcc_20'])} | {b['vs_winner_delta']:+.4f} ({b['vs_winner_p']}) → "
        f"{f['vs_winner_delta']:+.4f} ({f['vs_winner_p']}) |"
    )

print("\n### Verifier inputs the legacy re-key sent to the wrong sheet\n")
print(
    "| Union | Rows | Re-keyed | Highest probability among them | Within 20 m of a mound | "
    "Black share of their crops (median; lowest) | Black share, 200 other crops (median) | "
    "F1 at best point | If verified as mounds | Bound |"
)
print("|---|---:|---:|---:|---:|---|---:|---:|---:|---:|")
total = 0
for k, e in r.items():
    b = e["optimistic_bound_at_best_point"]
    total += e["n_rekeyed"]
    print(
        f"| {k} | {e['n_rows']:,} | {e['n_rekeyed']} | {e['rekeyed_max_prob']:.2f} | "
        f"{e['rekeyed_n_within_20m_of_a_mound']} | {e['crop_dark_share_rekeyed_median']:.3f}; "
        f"{e['crop_dark_share_rekeyed_min']:.3f} | "
        f"{e['crop_dark_share_others_sample_median']:.4f} | "
        f"{b['f1_fixed']:.4f} | {b['f1_if_rekeyed_verified_mounds']:.4f} | {b['delta']:+.4f} |"
    )
print(f"\ntotal re-keyed verifier candidates: {total}")
print("prob>=0.15 among re-keyed / share >=0.15 among others / crops found:")
print(
    {
        k: (e["rekeyed_n_prob_ge_0p15"], round(e["others_share_prob_ge_0p15"], 3), e["crops_found"])
        for k, e in r.items()
    }
)

print("\n### Unchanged keys")
print(sorted(k for k in a if a[k] == c.get(k)))
print("\n### Changed keys")
print(sorted(k for k in set(a) | set(c) if a.get(k) != c.get(k)))
