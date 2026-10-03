#!/usr/bin/env python3
"""
Assemble the K-ladder tables and the Pareto figure from committed artefacts.

Every metric comes from a cell's own committed ``evaluation.json`` (via
``results/k-ladder-2026-09-12/inventory.json``, which the inventory builder
produced from the register). A rung with no cost is written ``null`` and the
reason is recorded beside it — never estimated silently.

Cost sources (since 2026-10-04, WP4b)
-------------------------------------
Every cost is the configuration's own passes-register tokens at the uniform
discounted tier (PI ruling D19, amended 2026-10-04), priced by
``scripts/lib_frontier_cost.py`` from ``data/pricing/frontier-configurations.json``:

``k_ladder_phase1_gs_stride_a``
    The gold-standard stride-A ladder: N passes of the 487-tile pool plus that
    rung's own verified union leg. It reproduces the hand-copied figures it
    replaced (``results/stride-2026-08-25/findings.md``: 1.38 / 2.64 / 3.81 /
    6.56) to the cent.
``board_families``
    The 55-map rungs, priced as the r2 final board prices them: stride A and B,
    the two 3.7 arms, and the fourth cell, each ladder routed to its family by
    pool AND verifier model. Before 2026-10-04 the lookup was keyed by pool
    alone, so the fourth cell's ladder (stride B's union, Gemini 3.7 verifier)
    was given stride B's Gemini 3 verifier costs, although this docstring said
    its costs were not supplied; and the arms' N < 5 rungs carried the full
    K = 5 union's verifier, an upper bound. Both now price their own rungs.

The 55-map projection column
----------------------------
``pass-budget-pareto-v2`` projected gold-standard rungs to the 55-map corpus by
the tile factor 8,541 / 487. That factor is right only for a 487-tile gold
standard cell. The stride-A gold-standard rungs run 820 tiles per pass
(``results/stride-2026-08-25/findings.md``), and their 55-map counterpart is not
a projection at all — it is the committed ``stride-55map-2026-08-25`` A ladder.
So this script reports BOTH: the 8,541 / 487 projection for comparability with
the registered Pareto row, and the measured 55-map cost of the same geometry,
with the ratio between them as the projection's error.

Usage::

    python scripts/build_k_ladder_tables.py \\
        --out-dir results/k-ladder-2026-09-12

Writes ``ladders.json`` and ``figures/k-ladder-pareto.png``. Zero API.

Created: 2026-09-12 (Session 154, K-ladder Phase 1 step 5)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_frontier_cost import default_coster  # noqa: E402
INVENTORY = PROJECT_ROOT / "results/k-ladder-2026-09-12/inventory.json"
BOARD_FRAME_DIR = PROJECT_ROOT / "results/k-ladder-2026-09-12/board-frame"

#: GS tile factor the registered Pareto row used to project to 55 maps.
GS_TO_55MAP_TILE_FACTOR = 8541 / 487

#: Board-frame evaluations of those rungs, written by this run (step 5).
GS_STRIDE_A_BOARD_EVAL = {
    1: "stride-phaseb__g384-ov128-ladder-n1",
    3: "stride-phaseb__g384-ov128-ladder-n3",
    5: "stride-phaseb__g384-ov128-ladder-n5",
    10: "stride-phaseb__g384-ov128-k10",
}

#: The frontier mapping (WP4b): the board's families and the GS stride-A ladder.
FRONTIER_MAPPING = json.loads(
    (PROJECT_ROOT / "data/pricing/frontier-configurations.json").read_text(encoding="utf-8"))


def board_family(pool: str, verifier_model: str, label: str) -> str | None:
    """The r2 board family a 55-map ladder's rungs belong to, by pool AND verifier.

    The pool alone is ambiguous: stride B's union was verified twice, by the
    Gemini 3 verifier (family B) and by Gemini 3.7 (the fourth cell, FOURTH).

    Examples:
        >>> board_family("g384_ov192_55map", "gemini-3.7-flash", "x")
        'FOURTH'
        >>> board_family("g384_ov192_55map", "gemini-3-flash-preview", "x")
        'B'
        >>> board_family("g384_ov192_55map_g37", "gemini-3.7-flash", "arm2-n1") is None
        False
    """
    if pool == "g384_ov128_55map":
        return "A"
    if pool == "g384_ov192_55map":
        return "FOURTH" if verifier_model.startswith("gemini-3.7") else "B"
    if pool == "g384_ov192_55map_g37":
        return "ARM1" if "arm1" in label else "ARM2"
    return None


def priced_rung(spec: dict[str, Any], what: str) -> dict[str, Any]:
    """A rung's cost entry from a mapping spec: dollars, basis, and its register rows."""
    priced = default_coster().configuration_cost(spec)
    return {
        "usd": round(priced.usd, 4),
        "basis": ("measured at the uniform tier" if priced.basis == "measured"
                  else "completed at the uniform tier (a floor leg priced at "
                       "comparable legs' unit, D19)"),
        "why": (f"{what}: data/pricing/frontier-configurations.json priced by "
                "scripts/lib_frontier_cost.py from the passes register (D19, "
                "amended 2026-10-04)"),
        "register_rows": list(priced.sources),
    }


def board_frame_metrics() -> dict[int, dict[str, Any]]:
    """The gold-standard stride-A rungs' board-frame F1@20, MCC and count."""
    out: dict[int, dict[str, Any]] = {}
    for k, slug in GS_STRIDE_A_BOARD_EVAL.items():
        path = BOARD_FRAME_DIR / slug / "evaluation.json"
        if not path.is_file():
            out[k] = {"available": False,
                      "why": f"{path.relative_to(PROJECT_ROOT)} not present"}
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        summary = doc["summary"]
        f1 = next(b["f1"] for b in summary["buffers"]
                  if b.get("buffer_metres") == 20)
        mcc = (summary.get("tile_classification") or {}).get("mcc") or {}
        out[k] = {"available": True, "f1_20": f1,
                  "mcc": mcc.get("point") if isinstance(mcc, dict) else mcc,
                  "n_detections": summary.get("n_detections"),
                  "eval_path": str(path.relative_to(PROJECT_ROOT))}
    return out


def build() -> dict[str, Any]:
    """Every multi-rung ladder, with metrics from the register and cost per rung."""
    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    frame = board_frame_metrics()

    ladders = []
    for fam in inv["families"]:
        rungs_asked = [k for k in ("1", "3", "5", "10") if k in fam["cells"]]
        if len(rungs_asked) < 3:
            continue
        pool = fam["proposer_pool"]
        entry: dict[str, Any] = {
            "family": fam["family"],
            "family_base": fam["family_base"],
            "run_id": fam["run_id"],
            "proposer_pool": pool,
            "corpus": fam["corpus"],
            "frame_file": fam["frame_file"],
            "reference_file": fam["reference_file"],
            "headline_buffer_m": fam["headline_buffer_m"],
            "verifier": fam["verifier"],
            "r1_verifier": fam["r1_verifier"],
            "rungs": [],
        }
        for key in rungs_asked:
            k = int(key)
            for cell in fam["cells"][key]:
                headline = (cell["f1_20"] if fam["headline_buffer_m"] == 20
                            else cell["f1_50"])
                rung: dict[str, Any] = {
                    "K": k,
                    "condition_id": cell["condition_id"],
                    "vote_threshold": cell["vote_threshold"],
                    "prob_threshold": cell["prob_threshold"],
                    "f1_headline": headline,
                    "f1_20": cell["f1_20"],
                    "f1_50": cell["f1_50"],
                    "tile_mcc": cell["mcc"],
                    "n_detections": cell["n_detections"],
                    "eval_path": cell["eval_path"],
                    "cost": None,
                }
                label = cell["condition_id"].split("::", 1)[1]
                family = board_family(pool, fam["verifier"]["model"], label)
                if pool == "g384_ov128" and fam["corpus"] == "4-map-gs":
                    rung["cost"] = priced_rung(
                        FRONTIER_MAPPING["k_ladder_phase1_gs_stride_a"][str(k)],
                        f"GS stride-A rung N = {k}")
                    rung["projection_55map_usd"] = round(
                        rung["cost"]["usd"] * GS_TO_55MAP_TILE_FACTOR, 2)
                    if frame.get(k, {}).get("available"):
                        rung["board_frame"] = frame[k]
                        rung["frame_tax_f1_20"] = round(
                            frame[k]["f1_20"] - cell["f1_20"], 4)
                elif family and f"{family}-N{k}" in FRONTIER_MAPPING["board_families"]:
                    rung["cost"] = priced_rung(
                        FRONTIER_MAPPING["board_families"][f"{family}-N{k}"],
                        f"r2 board family {family}-N{k}")
                else:
                    rung["cost"] = {
                        "usd": None, "basis": "not supplied",
                        "why": (f"no frontier mapping covers {pool} at N = {k} "
                                f"(verifier {fam['verifier']['model']})"),
                    }
                entry["rungs"].append(rung)
        ladders.append(entry)

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "card": "planning/k-ladder-review-2026-09-11.md",
        "run_card": "planning/k-ladder-phase1-run-2026-09-12.md",
        "gs_to_55map_tile_factor": GS_TO_55MAP_TILE_FACTOR,
        "sources": {
            "metrics": "results/k-ladder-2026-09-12/inventory.json (from the register)",
            "cost": ("the passes register at the uniform discounted tier (PI ruling "
                     "D19, amended 2026-10-04): data/pricing/frontier-configurations.json "
                     "(k_ladder_phase1_gs_stride_a, board_families) priced by "
                     "scripts/lib_frontier_cost.py"),
            "board_frame_evals": "results/k-ladder-2026-09-12/board-frame/",
        },
        "n_ladders": len(ladders),
        "ladders": ladders,
    }


def figure(payload: dict[str, Any], out: Path) -> None:
    """Cost against headline F1, one line per ladder, log cost axis."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8.2, 5.4))
    markers = ["o", "s", "^", "v", "D", "P", "X", "*"]
    for index, ladder in enumerate(payload["ladders"]):
        points = []
        for rung in ladder["rungs"]:
            usd = (rung["cost"] or {}).get("usd")
            f1 = rung["f1_headline"]
            if usd is None or f1 is None:
                continue
            points.append((rung["K"], usd, f1))
        if len(points) < 2:
            continue
        # One point per K: the best headline F1 at that K.
        best: dict[int, tuple[float, float]] = {}
        for k, usd, f1 in points:
            if k not in best or f1 > best[k][1]:
                best[k] = (usd, f1)
        ks = sorted(best)
        xs = [best[k][0] for k in ks]
        ys = [best[k][1] for k in ks]
        ax.plot(xs, ys, marker=markers[index % len(markers)], linewidth=1.4,
                markersize=6, label=ladder["family"].split(" [")[0]
                + f" ({ladder['headline_buffer_m']} m)")
        for k, x, y in zip(ks, xs, ys):
            ax.annotate(f"K={k}", (x, y), textcoords="offset points",
                        xytext=(5, -9), fontsize=7.5)
    ax.set_xscale("log")
    ax.set_xlabel("Audited all-in cost per rung, US$ (flex), log scale")
    ax.set_ylabel("Headline F1 (20 m gold standard / 50 m corrected, 55-map)")
    ax.set_title("Pass count against cost: the fixed-parameter K ladders")
    ax.grid(True, which="both", alpha=0.25, linewidth=0.6)
    ax.legend(fontsize=7.5, loc="lower right", framealpha=0.9)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    """Write ``ladders.json`` and the Pareto figure."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--out-dir", type=Path,
                        default=PROJECT_ROOT / "results/k-ladder-2026-09-12")
    args = parser.parse_args(argv)
    payload = build()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "ladders.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    figure(payload, args.out_dir / "figures/k-ladder-pareto.png")
    print(f"{payload['n_ladders']} ladder(s)")
    for ladder in payload["ladders"]:
        priced = sum(1 for r in ladder["rungs"] if (r["cost"] or {}).get("usd"))
        print(f"  {ladder['family']:<96s} rungs={len(ladder['rungs'])} priced={priced}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
