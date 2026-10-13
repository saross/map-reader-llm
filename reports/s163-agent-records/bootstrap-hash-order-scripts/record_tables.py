#!/usr/bin/env python3
"""
Print the Markdown tables of ``reports/s163-agent-records/bootstrap-hash-order.md``
from the impact rows and the March-library replays (ruling D63).

Every number in the record's impact section is printed by this script from
``impact-rows.json`` (``impact_summary.py``) and the ``fair384-march``
replays, so none is transcribed by hand.

Usage::

    python record_tables.py --rows out/impact-rows.json --work /tmp/d63-runs \\
        --repo <clone>
"""

from __future__ import annotations

import argparse
import json
import statistics as st
from pathlib import Path


def ci(v: dict | None) -> str:
    """Interval to four decimals."""
    if not v or v.get("lo") is None:
        return "–"
    return f"[{v['lo']:+.4f}, {v['hi']:+.4f}]"


def rng(vals: list[float]) -> str:
    """``min..max`` to four decimals."""
    return f"{min(vals):+.4f} to {max(vals):+.4f}"


def excl(v: dict | None) -> str:
    """Yes/no: does the interval exclude zero."""
    if not v or v.get("lo") is None:
        return "–"
    return "yes" if (v["lo"] > 0 or v["hi"] < 0) else "no"


def main() -> int:
    """Print the tables."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--repo", type=Path, required=True)
    args = ap.parse_args()
    rows = json.loads(args.rows.read_text())["rows"]
    iv = [r for r in rows if not r["metric"].startswith("_")]

    # A. Per-output summary.
    print("### Table A\n")
    print("| Output (committed file) | Intervals | Hash-seed spread on `main` "
          "(largest bound range, seeds 0–3) | Largest bound shift committed → fixed | "
          "Excludes-zero reading varies with the seed | Flips committed → fixed |")
    print("|---|---|---|---|---|---|")
    by: dict[str, list[dict]] = {}
    for r in iv:
        by.setdefault(r["output"], []).append(r)
    for out, rs in by.items():
        rel = next(iter(rs[0]["committed"]))
        spreads, shifts, within, flips = [], [], 0, 0
        for r in rs:
            vals = [v for v in r["main"].values() if v]
            spreads.append(max(max(v[k] for v in vals) - min(v[k] for v in vals)
                               for k in ("lo", "hi")))
            c = r["committed"][rel]
            if c and c.get("lo") is not None:
                shifts.append(max(abs(r["fixed"]["lo"] - c["lo"]),
                                  abs(r["fixed"]["hi"] - c["hi"])))
                flips += excl(c) != excl(r["fixed"])
            within += len({excl(v) for v in vals}) > 1
        print(f"| `{rel}` | {len(rs)} | {max(spreads):.4f} | {max(shifts):.4f} | "
              f"{within} | {flips} |")

    # B. Retest rows whose excludes-zero reading moves.
    print("\n### Table B\n")
    print("| Phase: pair | Metric | Committed (March) | `main`, seeds 0–3 (lower; upper) | "
          "Fixed | Excludes zero: committed → fixed | Permutation p (unchanged) | "
          "D42 BH significant (unchanged) |")
    print("|---|---|---|---|---|---|---|---|")
    bh = {r["id"]: r for r in rows if r["metric"] == "_bh"}
    for r in iv:
        if r["family"] != "retest":
            continue
        c = next(iter(r["committed"].values()))
        vals = [v for v in r["main"].values() if v]
        within = len({excl(v) for v in vals}) > 1
        if not within and excl(c) == excl(r["fixed"]):
            continue
        b = bh[r["id"]]
        print(f"| {r['id']} | {r['metric']} | {ci(c)} | "
              f"{rng([v['lo'] for v in vals])}; {rng([v['hi'] for v in vals])} | "
              f"{ci(r['fixed'])} | {excl(c)} → {excl(r['fixed'])} | {r['fixed']['p']} | "
              f"{b['fixed']} |")

    # C. Interaction contrasts.
    print("\n### Table C\n")
    print("| Track | Metric | Committed | `main`, seeds 0–3 (lower; upper) | Fixed | "
          "Interaction detected: committed → fixed |")
    print("|---|---|---|---|---|---|")
    flags = {(r["output"], r["id"]): r for r in rows if r["metric"] == "_flag"}
    for r in iv:
        if r["family"] != "interaction" or r["metric"] != "dod":
            continue
        track = "image" if r["output"].endswith("image.json") else "text"
        m = r["id"].split(":")[0]
        f = flags[(r["output"], f"{m}: interaction_detected")]
        c = next(iter(r["committed"].values()))
        vals = [v for v in r["main"].values() if v]
        print(f"| {track} | {m} | {ci(c)} | {rng([v['lo'] for v in vals])}; "
              f"{rng([v['hi'] for v in vals])} | {ci(r['fixed'])} | "
              f"{next(iter(f['committed'].values()))} → {f['fixed']} |")

    # D. SD v1 slopes.
    print("\n### Table D\n")
    print("| Stratum | β₁ committed | β₁ on `main`, seeds 0–3 | β₁ fixed | "
          "β₁ interval (all) | Slower than i.i.d. (all) |")
    print("|---|---|---|---|---|---|")
    for r in iv:
        if r["family"] != "sd-v1" or r["metric"] != "beta_1":
            continue
        c = next(iter(r["committed"].values()))
        f = flags[(r["output"], r["id"])]
        same_ci = all(v["lo"] == c["lo"] and v["hi"] == c["hi"]
                      for v in [*r["main"].values(), r["fixed"]])
        fl = {json.dumps(x) for x in [*f["main"].values(), f["fixed"],
                                      next(iter(f["committed"].values()))]}
        print(f"| {r['id'].replace('slope ', '')} | {c['mean']:+.4f} | "
              f"{rng([v['mean'] for v in r['main'].values()])} | {r['fixed']['mean']:+.4f} | "
              f"{ci(c)}{'' if same_ci else ' (moves)'} | {', '.join(sorted(fl))} |")

    # E. fair-384, pairwise-384px, and the two PV comparisons: F1 only.
    print("\n### Table E\n")
    print("| File: comparison | Committed (March) | D42 class-B record (hash seed 0) | "
          "`main`, seeds 0–3 (lower; upper) | Fixed | March library, seeds 0–7 "
          "(lower; upper) |")
    print("|---|---|---|---|---|---|")
    march = {}
    for fname in ("fair-384-vs-512.json", "pairwise-384px.json"):
        march[fname] = {}
        for s in range(8):
            tag = "s0123" if s < 4 else "s4567"
            p = args.work / "fair384-march" / f"1ca43283e-{tag}-run1" / f"seed-{s}" / "out" / fname
            march[fname][s] = json.loads(p.read_text())
    for r in iv:
        if r["family"] not in ("fair384", "pvpair") or r["metric"] != "f1":
            continue
        rels = list(r["committed"])
        c = r["committed"][rels[0]]
        cb = r["committed"].get(rels[1]) if len(rels) > 1 else None
        vals = [v for v in r["main"].values() if v]
        fname = Path(r["output"]).name
        mar = "–"
        if fname in march:
            ms = [march[fname][s][r["id"]]["result"]["f1_difference"] for s in range(8)]
            mar = f"{rng([m['ci_lower'] for m in ms])}; {rng([m['ci_upper'] for m in ms])}"
        label = f"{fname.replace('.json', '')}: {r['id']}"
        if fname == "comparison.json":
            label = r["output"].split("/")[1] + ": " + r["id"]
        print(f"| {label} | {ci(c)} | {ci(cb)} | {rng([v['lo'] for v in vals])}; "
              f"{rng([v['hi'] for v in vals])} | {ci(r['fixed'])} | {mar} |")

    # F. March-library z-scores of the committed March values.
    zs = []
    for fname, rel in (("fair-384-vs-512.json",
                        "results/h11-384-pv-diagnostic/pairwise/fair-384-vs-512.json"),
                       ("pairwise-384px.json",
                        "results/h11-384-pv-diagnostic/pairwise/pairwise-384px.json")):
        com = json.loads((args.repo / rel).read_text())
        for key, entry in com.items():
            if not isinstance(entry, dict) or "result" not in entry:
                continue
            for m in ("f1", "precision", "recall"):
                for b in ("ci_lower", "ci_upper", "mean"):
                    v = [march[fname][s][key]["result"][f"{m}_difference"][b] for s in range(8)]
                    zs.append(abs(entry["result"][f"{m}_difference"][b] - st.mean(v))
                              / st.stdev(v))
    print("\n### March-library check\n")
    print(f"values: {len(zs)}; median |z| {st.median(zs):.2f}; |z| > 2: "
          f"{sum(z > 2 for z in zs)}; |z| > 3: {sum(z > 3 for z in zs)}; "
          f"max {max(zs):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
