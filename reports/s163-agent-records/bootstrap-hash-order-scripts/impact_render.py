#!/usr/bin/env python3
"""
Render the D63 impact rows (``impact_summary.py`` output) as Markdown tables.

Writes ``impact-tables.md`` beside the rows file: a per-output summary, every
verdict crossing, and per-comparison tables for the smaller outputs. The
numbers are copied from ``impact-rows.json`` and rounded to four decimals.

Usage::

    python impact_render.py --rows <dir>/impact-rows.json
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def f4(x: float | None) -> str:
    """Four-decimal signed number, or a dash."""
    return "–" if x is None else f"{x:+.4f}"


def ci(v: dict | None) -> str:
    """``[lo, hi]`` to four decimals."""
    if not v or v.get("lo") is None:
        return "–"
    return f"[{f4(v['lo'])}, {f4(v['hi'])}]"


def spread(row: dict) -> float:
    """Largest range of either bound across the main hash seeds."""
    vals = [v for v in row["main"].values() if v and v.get("lo") is not None]
    if len(vals) < 2:
        return 0.0
    return max(max(v[k] for v in vals) - min(v[k] for v in vals) for k in ("lo", "hi"))


def shift(row: dict, rel: str) -> float | None:
    """Largest bound change committed (``rel``) -> fixed."""
    c = row["committed"].get(rel)
    f = row["fixed"]
    if not c or c.get("lo") is None or f.get("lo") is None:
        return None
    return max(abs(f["lo"] - c["lo"]), abs(f["hi"] - c["hi"]))


def main() -> int:
    """Render the tables."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--rows", type=Path, required=True)
    args = ap.parse_args()
    data = json.loads(args.rows.read_text())
    rows = data["rows"]
    out: list[str] = []

    # Per-output summary.
    by_out: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_out[r["output"]].append(r)
    out += ["| Output | Intervals | Max hash-seed spread (main) | "
            "Max shift committed → fixed | Excludes-zero flips within main | "
            "Committed → fixed flips |", "|---|---|---|---|---|---|"]
    crossings: list[str] = []
    for name, rs in by_out.items():
        ivs = [r for r in rs if not r["metric"].startswith("_")]
        first_rel = next(iter(ivs[0]["committed"])) if ivs else None
        shifts = [s for r in ivs if (s := shift(r, first_rel)) is not None]
        within = [r for r in ivs if len(r["main_excl0"]) > 1]
        flips = [r for r in ivs
                 if r["committed_excl0"].get(first_rel) is not None
                 and r["committed_excl0"][first_rel] != r["fixed_excl0"]]
        out.append(f"| `{name}` | {len(ivs)} | {max((spread(r) for r in ivs), default=0):.4f} | "
                   f"{max(shifts, default=0):.4f} | {len(within)} | {len(flips)} |")
        seen: set[tuple[str, str]] = set()
        for r in within + flips:
            if (r["id"], r["metric"]) in seen:
                continue
            seen.add((r["id"], r["metric"]))
            mains = ", ".join(f"s{s} {ci(v)}" for s, v in sorted(r["main"].items()))
            crossings.append(
                f"| `{name}` | {r['id']} | {r['metric']} | "
                f"{ci(r['committed'].get(first_rel))} | {mains} | {ci(r['fixed'])} |")
        for r in rs:
            if r["metric"] in ("_flag", "_bh"):
                vals = {json.dumps(v) for v in r["main"].values()}
                com = r["committed"].get(first_rel)
                if len(vals) > 1 or (com is not None and com != r["fixed"]):
                    crossings.append(
                        f"| `{name}` | {r['id']} | {r['metric']} | {com} | "
                        f"{dict(sorted(r['main'].items()))} | {r['fixed']} |")
        # p values: the D63 fix must not move them.
        for r in ivs:
            ps = {v["p"] for v in r["main"].values() if v}
            if len(ps) > 1 or (ps and r["fixed"].get("p") not in ps):
                crossings.append(f"| `{name}` | {r['id']} | {r['metric']} p | – | {sorted(ps)} | "
                                 f"{r['fixed'].get('p')} |")
    out += ["", "| Output | Comparison | Metric | Committed | main by hash seed | Fixed |",
            "|---|---|---|---|---|---|", *crossings]
    (args.rows.parent / "impact-tables.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
