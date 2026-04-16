"""Collate H12 v2 evaluation results into a single summary table.

Reads all evaluation.json files under ``results/h12-v2/`` and prints
per-method tables plus a best-of-method summary per condition, followed by
the three pairwise contrasts at the production operating point
(greedy t=4). Adapted from summarise_h8v2.py.

H12 v2 tests the HP:HN ratio at fixed total hard count = 8:

    r1-hn-heavy  (1:3, 2 HP + 6 HN)
    r2-balanced  (1:1, 4 HP + 4 HN)  — reused from H8 v2 Scale-8
    r3-hp-heavy  (3:1, 6 HP + 2 HN)

Greedy is the headline / primary aggregation method; WBF variant C is
reported alongside for comparability with H8 v2 and H10 v2.
"""

import json
from pathlib import Path

CONDITIONS = [
    "r1-hn-heavy",
    "r2-balanced",
    "r3-hp-heavy",
]


def read_20m(path: Path) -> dict | None:
    if not path.exists():
        return None
    d = json.load(open(path))
    for b in d.get("summary", {}).get("buffers", []):
        if b.get("buffer_metres") == 20:
            return b
    return None


def fmt(m: dict | None) -> str:
    if m is None:
        return "—"
    return (
        f"{m['f1']:.3f} [{m['f1_ci_lower']:.3f}, {m['f1_ci_upper']:.3f}]  "
        f"P={m['precision']:.3f}  R={m['recall']:.3f}"
    )


print("=" * 100)
print("H12 v2 HP:HN RATIO RESULTS  (20 m buffer, 1000 bootstrap, 327 test tiles)")
print("=" * 100)

# Greedy (headline / primary)
for t in (1, 2, 3, 4, 5):
    print()
    marker = " — PRIMARY / HEADLINE" if t == 4 else ""
    print(f"### Greedy t={t} ({t}-of-5 consensus, 20 m clustering){marker}")
    print("-" * 100)
    print(f"{'Condition':<20}F1 [95% CI]                        P       R")
    print("-" * 100)
    for cond in CONDITIONS:
        m = read_20m(Path(f"results/h12-v2/greedy/{cond}/t{t}/evaluation.json"))
        print(f"{cond:<20}{fmt(m)}")

# WBF (secondary, for cross-hypothesis comparability)
print()
print("### WBF variant C (IoU=0.25, min_sep=60 m)  — SECONDARY")
print("-" * 100)
print(f"{'Condition':<20}F1 [95% CI]                        P       R")
print("-" * 100)
for cond in CONDITIONS:
    m = read_20m(Path(f"results/h12-v2/wbf/{cond}/evaluation.json"))
    print(f"{cond:<20}{fmt(m)}")

# Condition-centric best-of
print()
print("=" * 100)
print("Best F1 per condition (across greedy t1..t5 and WBF)")
print("=" * 100)
print(f"{'Condition':<20}{'Best F1':<10}{'95% CI':<22}{'P':<8}{'R':<8}{'Method'}")
print("-" * 100)
for cond in CONDITIONS:
    best = None
    best_label = None
    for label, path in [
        *[(f"greedy-t{t}", f"results/h12-v2/greedy/{cond}/t{t}/evaluation.json") for t in (1, 2, 3, 4, 5)],
        ("WBF", f"results/h12-v2/wbf/{cond}/evaluation.json"),
    ]:
        m = read_20m(Path(path))
        if m is None:
            continue
        if best is None or m["f1"] > best["f1"]:
            best = m
            best_label = label
    if best is not None:
        print(
            f"{cond:<20}{best['f1']:<10.3f}"
            f"[{best['f1_ci_lower']:.3f}, {best['f1_ci_upper']:.3f}]      "
            f"{best['precision']:<8.3f}{best['recall']:<8.3f}{best_label}"
        )

# Pairwise contrasts at greedy t=4 (the production operating point)
print()
print("=" * 100)
print("Pairwise contrasts at greedy t=4 (primary operating point)")
print("=" * 100)


def get(cond, method, t=None):
    if method == "wbf":
        return read_20m(Path(f"results/h12-v2/wbf/{cond}/evaluation.json"))
    return read_20m(Path(f"results/h12-v2/greedy/{cond}/t{t}/evaluation.json"))


contrasts = [
    ("R12 (R1 HN-heavy -> R2 balanced)", "r1-hn-heavy", "r2-balanced"),
    ("R23 (R2 balanced -> R3 HP-heavy)", "r2-balanced", "r3-hp-heavy"),
    ("R13 (R1 HN-heavy -> R3 HP-heavy)", "r1-hn-heavy", "r3-hp-heavy"),
]
for label, a_name, b_name in contrasts:
    a = get(a_name, "greedy", t=4)
    b = get(b_name, "greedy", t=4)
    if a and b:
        delta = b["f1"] - a["f1"]
        a_ci = (a["f1_ci_lower"], a["f1_ci_upper"])
        b_ci = (b["f1_ci_lower"], b["f1_ci_upper"])
        ci_overlap = not (a_ci[1] < b_ci[0] or b_ci[1] < a_ci[0])
        marker = "  (CIs overlap)" if ci_overlap else "  (CIs disjoint!)"
        print(
            f"{label:<40}"
            f"{a_name} {a['f1']:.3f} -> "
            f"{b_name} {b['f1']:.3f}  "
            f"Δ={delta:+.3f}{marker}"
        )

# Precision vs recall differential across the ratio axis
print()
print("=" * 100)
print("Precision vs recall differential across the ratio axis (greedy t=4)")
print("Preregistered prediction: HN-heavy -> higher P, HP-heavy -> higher R")
print("=" * 100)
print(f"{'Condition':<20}{'Precision':<15}{'Recall':<15}{'P - R':<10}")
print("-" * 100)
for cond in CONDITIONS:
    m = get(cond, "greedy", t=4)
    if m is None:
        continue
    p_minus_r = m["precision"] - m["recall"]
    print(
        f"{cond:<20}"
        f"{m['precision']:<15.3f}"
        f"{m['recall']:<15.3f}"
        f"{p_minus_r:+.3f}"
    )
