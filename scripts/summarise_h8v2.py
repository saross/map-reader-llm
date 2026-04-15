"""Collate H8 v2 evaluation results into a single summary table.

Reads all evaluation.json files under results/h8-v2/ and prints per-method
tables plus a best-of-method summary per condition.
"""

import json
from pathlib import Path

CONDITIONS = [
    "pure-positive-canon",
    "canonical",
    "plus-hp",
    "scale-4",
    "scale-8",
    "scale-16",
    "scale-32",
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
print("H8 v2 LIBRARY-COMPOSITION RESULTS  (20 m buffer, 1000 bootstrap, 327 test tiles)")
print("=" * 100)

# WBF
print()
print("### WBF (Variant C: IoU=0.25, min_sep=60m, unconditional merge)")
print("-" * 100)
print(f"{'Condition':<24}F1 [95% CI]                        P       R")
print("-" * 100)
for cond in CONDITIONS:
    m = read_20m(Path(f"results/h8-v2/wbf/{cond}/evaluation.json"))
    print(f"{cond:<24}{fmt(m)}")

# Greedy sweep
for t in (1, 2, 3, 4, 5):
    print()
    print(f"### Greedy t={t} ({t}-of-5 consensus, 20 m clustering)")
    print("-" * 100)
    print(f"{'Condition':<24}F1 [95% CI]                        P       R")
    print("-" * 100)
    for cond in CONDITIONS:
        m = read_20m(Path(f"results/h8-v2/greedy/{cond}/t{t}/evaluation.json"))
        print(f"{cond:<24}{fmt(m)}")

# Condition-centric best-of
print()
print("=" * 100)
print("Best F1 per condition (across WBF + greedy t1..t5)")
print("=" * 100)
print(f"{'Condition':<24}{'Best F1':<10}{'95% CI':<22}{'P':<8}{'R':<8}{'Method'}")
print("-" * 100)
for cond in CONDITIONS:
    best = None
    best_label = None
    for label, path in [
        ("WBF", f"results/h8-v2/wbf/{cond}/evaluation.json"),
        *[(f"greedy-t{t}", f"results/h8-v2/greedy/{cond}/t{t}/evaluation.json") for t in (1, 2, 3, 4, 5)],
    ]:
        m = read_20m(Path(path))
        if m is None:
            continue
        if best is None or m["f1"] > best["f1"]:
            best = m
            best_label = label
    if best is not None:
        print(
            f"{cond:<24}{best['f1']:<10.3f}"
            f"[{best['f1_ci_lower']:.3f}, {best['f1_ci_upper']:.3f}]      "
            f"{best['precision']:<8.3f}{best['recall']:<8.3f}{best_label}"
        )

# Contrasts at t=4 (the production operating point)
print()
print("=" * 100)
print("Preregistered contrasts at greedy t=4 (production operating point)")
print("=" * 100)


def get(cond, method, t=None):
    if method == "wbf":
        return read_20m(Path(f"results/h8-v2/wbf/{cond}/evaluation.json"))
    return read_20m(Path(f"results/h8-v2/greedy/{cond}/t{t}/evaluation.json"))


contrasts = [
    ("C1 (add Canon-)",    "pure-positive-canon", "canonical"),
    ("C2 (add HP)",        "canonical",           "plus-hp"),
    ("C3 (add HN)",        "plus-hp",             "scale-8"),
    ("B1 (HP-only vs balanced at size 13)", "plus-hp", "scale-4"),
    ("S1 (Scale-4 -> 8)",  "scale-4",             "scale-8"),
    ("S2 (Scale-8 -> 16)", "scale-8",             "scale-16"),
    ("S3 (Scale-16 -> 32)","scale-16",            "scale-32"),
]
for label, a_name, b_name in contrasts:
    a = get(a_name, "greedy", t=4)
    b = get(b_name, "greedy", t=4)
    if a and b:
        delta = b["f1"] - a["f1"]
        a_ci = (a["f1_ci_lower"], a["f1_ci_upper"])
        b_ci = (b["f1_ci_lower"], b["f1_ci_upper"])
        # Quick check whether CIs overlap
        ci_overlap = not (a_ci[1] < b_ci[0] or b_ci[1] < a_ci[0])
        marker = "  (CIs overlap)" if ci_overlap else "  (CIs disjoint!)"
        print(
            f"{label:<42}"
            f"{a_name} {a['f1']:.3f} -> "
            f"{b_name} {b['f1']:.3f}  "
            f"Δ={delta:+.3f}{marker}"
        )
