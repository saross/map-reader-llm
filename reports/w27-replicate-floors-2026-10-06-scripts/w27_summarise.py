#!/usr/bin/env python3
"""
Summarise the W2.7 replicate-floor runs into markdown tables (read-only).

Inputs (from sapphire /tmp/w27, copied beside this script under results/):
  gs_consensus_pairs.csv   - gold-standard corpora: within/across consensus pairs
  subset_pairs.csv         - 55-map board: disjoint-subset PV pairs (verifier fixed)
  calibration_pairs.csv    - W2's single-pass pairs (reports/retest-bootstrap-check-2026-10-05-scripts/)
Output: markdown tables on stdout, for pasting into the report. Every number
in the report's tables comes from here, not from transcription.

Usage: python w27_summarise.py [--results results/]
"""
import argparse
import csv
import statistics as st
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CAL = REPO / "reports/retest-bootstrap-check-2026-10-05-scripts/calibration_pairs.csv"

GAP = {1: ("384-px GS", "text HIGH T0.7", 17, "03-24 / 04-10"), 2: ("384-px GS", "text MIN T0.3", 21, "03-27 / 04-17"),
       4: ("384-px GS", "image MIN T0.3", 20, "03-27 / 04-16"), 5: ("384-px GS", "image HIGH T0.0", 20, "03-27 / 04-16"),
       6: ("384-px GS", "text HIGH T0.0", 21, "03-27 / 04-17"), 7: ("384-px GS", "text MIN T0.0", 23, "03-25 / 04-17"),
       8: ("384-px GS", "text MIN T0.7", 2, "03-22 / 03-24"), 10: ("H10 327", "image HIGH T0.7 (h8-v2 / h10)", 0, "04-15 same day"),
       11: ("55-map", "text HIGH T0.7", 8, "04-10 / 04-18"), 12: ("55-map", "text MIN T0.7 (TM / uplift)", 54, "04-18 / 06-11"),
       13: ("Era-1", "text MIN T1.0", 0, "03-15 hours"), 17: ("Era-1", "text MIN T0.3", 0, "03-15 hours"),
       18: ("Era-1", "text MIN T0.7", 1, "03-15 / 03-17"), 21: ("Era-1", "text HIGH T0.7", 2, "03-16/17 / 03-18..22"),
       22: ("Era-1", "text HIGH T1.0", 2, "03-17..21 / 03-19..21"), 23: ("Era-1", "image HIGH T0.7 (3c pools)", 1, "03-21..25"),
       24: ("Era-1", "text HIGH diversity pools", 1, "03-18..22")}


def pct(v, q):
    v = sorted(v)
    i = (len(v) - 1) * q
    lo = int(i)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)


def cell(v):
    if not v:
        return "—"
    d = [x[0] for x in v]
    return f"{len(v)} / {st.median(d):.3f} / {pct(d, 0.95):.3f} / {max(d):.3f} / {sum(x[1] for x in v) / len(v):.0%}"


def gs_tables(rows):
    print("\n### Within-execution consensus floors on the gold-standard corpora (disjoint pass subsets; proposer-only consensus; 20 m)\n")
    print("| corpus | K | t | pairs | median \\|ΔF1\\| | 95th pct | max | tile-swap rejects |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    agg = defaultdict(list)
    for r in rows:
        if r["kind"] == "within":
            agg[(r["scope"], int(r["K"]), int(r["t"]))].append((float(r["abs_dF1"]), float(r["perm_p"]) < 0.05))
    for (scope, K, t), v in sorted(agg.items()):
        d = [x[0] for x in v]
        print(f"| {scope} | {K} | {t} | {len(v)} | {st.median(d):.4f} | {pct(d, 0.95):.4f} | {max(d):.4f} | {sum(x[1] for x in v) / len(v):.0%} |")


def atlas(rows, cal):
    print("\n### Replicate atlas: within- against cross-execution differences by time gap (n / median |ΔF1| / 95th pct / max / rejects at 0.05)\n")
    print("| group | corpus | configuration | gap (days) | dates | buffer | single-pass within | single-pass ACROSS | consensus within | consensus ACROSS |")
    print("|---:|---|---|---:|---|---:|---|---|---|---|")
    for g, (corpus, lab, days, dates) in sorted(GAP.items(), key=lambda kv: (kv[1][2], kv[0])):
        for buf in (["20", "50"] if g in (11, 12) else ["20"]):
            sp_w = [(abs(float(r["obs_diff"])), float(r["perm_p"]) < 0.05) for r in cal if int(r["group"]) == g and r["buffer"] == buf and r["same_arm"] == "True"]
            sp_x = [(abs(float(r["obs_diff"])), float(r["perm_p"]) < 0.05) for r in cal if int(r["group"]) == g and r["buffer"] == buf and r["same_arm"] == "False"]
            def sel(kind, g=g, buf=buf):
                return [(float(r["abs_dF1"]), float(r["perm_p"]) < 0.05) for r in rows
                        if int(r["group"]) == g and r["buffer"] == buf and r["kind"] == kind
                        and ((r["K"] == "3" and int(r["t"]) >= 2) or (r["K"] == "5" and int(r["t"]) >= 4))]
            print(f"| {g} | {corpus} | {lab} | {days} | {dates} | {buf} m | {cell(sp_w)} | {cell(sp_x)} | {cell(sel('within'))} | {cell(sel('across'))} |")


def maps55_pairs(rows):
    print("\n### 55-map cross-execution consensus pairs (proposer-only consensus of each execution's five passes; a = earlier, b = later; ΔF1 = a − b)\n")
    print("| group | buffer | K | t | n det a | n det b | F1 a | F1 b | ΔF1 | p |")
    print("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        if r["group"] in ("11", "12") and r["kind"] == "across" and int(r["t"]) >= 3:
            print(f"| {r['group']} | {r['buffer']} m | {r['K']} | {r['t']} | {r['n_det_a']} | {r['n_det_b']} | {float(r['f1_a']):.4f} | {float(r['f1_b']):.4f} | {float(r['dF1']):+.4f} | {float(r['perm_p']):.4f} |")


def board_tables(sub):
    print("\n### 55-map board: within-execution proposer-stage replicate differences (disjoint pass subsets; verifier probabilities inherited, so the verifier is held fixed; 50 m, reference r2)\n")
    print("| family | N (rung) | prob_t | k | pairs | median \\|ΔF1\\| | 95th pct | max | rejects |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    agg = defaultdict(list)
    for r in sub:
        agg[(r["family"], int(r["n_rung"]), float(r["prob_t"]), int(r["k"]), r["kind"])].append((float(r["abs_dF1"]), float(r["perm_p"]) < 0.05, float(r["dF1"]), float(r["f1_a"]), float(r["f1_b"])))
    for (f, n, p, k, kind), v in sorted(agg.items()):
        d = [x[0] for x in v]
        extra = f" (ΔF1 {v[0][2]:+.4f}; F1 {v[0][3]:.4f} vs {v[0][4]:.4f})" if len(v) == 1 else ""
        print(f"| {f}{' — ' + kind if kind != 'within-execution' else ''} | {n} | {p} | {k} | {len(v)} | {st.median(d):.4f} | {pct(d, 0.95):.4f} | {max(d):.4f} | {sum(x[1] for x in v) / len(v):.0%}{extra} |")
    print("\n### 55-map board: pooled proposer-stage floors by rung size (all families, all swept points; within-execution only)\n")
    print("| N (rung) | pairs | median \\|ΔF1\\| | 95th pct | max | rejects |")
    print("|---:|---:|---:|---:|---:|---:|")
    agg = defaultdict(list)
    for r in sub:
        if r["kind"] == "within-execution":
            agg[int(r["n_rung"])].append((float(r["abs_dF1"]), float(r["perm_p"]) < 0.05))
    for n, v in sorted(agg.items()):
        d = [x[0] for x in v]
        print(f"| {n} | {len(v)} | {st.median(d):.4f} | {pct(d, 0.95):.4f} | {max(d):.4f} | {sum(x[1] for x in v) / len(v):.0%} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=Path(__file__).parent / "results")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.results / "gs_consensus_pairs.csv")))
    cal = list(csv.DictReader(open(CAL)))
    gs_tables(rows)
    atlas(rows, cal)
    maps55_pairs(rows)
    sp = a.results / "subset_pairs.csv"
    if sp.exists():
        board_tables(list(csv.DictReader(open(sp))))


if __name__ == "__main__":
    main()
