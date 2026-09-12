#!/usr/bin/env python3
"""
Assemble the K-ladder tables and the Pareto figure from committed artefacts.

Every metric comes from a cell's own committed ``evaluation.json`` (via
``results/k-ladder-2026-09-12/inventory.json``, which the inventory builder
produced from the register) and every cost from a committed audited figure. A
rung with no committed cost figure is written ``null`` and the reason is recorded
beside it — never estimated silently.

Cost sources, all committed
---------------------------
``results/stride-2026-08-25/findings.md``
    The gold-standard stride-A ladder's measured all-in flex cost per rung
    ("Exact winner ladder … $3.407 flex measured vs $3.41 priced"): N = 1 $1.38,
    N = 3 $2.64, N = 5 $3.81, N = 10 $6.56.
``results/55map-final-board-r2-2026-09-06/final_board_50m.json``
    ``cost_usd`` per 55-map rung, the audited proposer plus union-verifier
    all-in: A $20.53 / $41.22 / $59.75 / $103.91 and B $30.99 / $65.48 /
    $97.22 / $173.59.
``reports/r7-gaps-deltas-2026-09-11.md`` §§ 2.2, 2.3, 2.5
    The 3.7 arms' audited proposer (US$144.27 over five passes) and verifier arms
    (arm 1 US$8.89, arm 2 US$14.31 over 12,715 candidates), and the fourth
    cell's verifier, whose meta was overwritten by a cleanup pass — so that
    ladder's rung costs are NOT supplied.

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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INVENTORY = PROJECT_ROOT / "results/k-ladder-2026-09-12/inventory.json"
BOARD_FRAME_DIR = PROJECT_ROOT / "results/k-ladder-2026-09-12/board-frame"
R2_BOARD = PROJECT_ROOT / "results/55map-final-board-r2-2026-09-06/final_board_50m.json"

#: GS tile factor the registered Pareto row used to project to 55 maps.
GS_TO_55MAP_TILE_FACTOR = 8541 / 487

#: The gold-standard stride-A ladder's measured all-in flex cost per rung.
#: `results/stride-2026-08-25/findings.md`, "Exact winner ladder" table.
GS_STRIDE_A_COST_USD = {1: 1.38, 3: 2.64, 5: 3.81, 10: 6.56}

#: Board-frame evaluations of those rungs, written by this run (step 5).
GS_STRIDE_A_BOARD_EVAL = {
    1: "stride-phaseb__g384-ov128-ladder-n1",
    3: "stride-phaseb__g384-ov128-ladder-n3",
    5: "stride-phaseb__g384-ov128-ladder-n5",
    10: "stride-phaseb__g384-ov128-k10",
}

#: The 3.7 arms' audited costs (`reports/r7-gaps-deltas-2026-09-11.md` §§ 2.2, 2.3).
ARM_PROPOSER_USD_TOTAL = 144.27
ARM_PROPOSER_PASSES = 5
ARM_VERIFIER_USD = {"arm1": 8.890222, "arm2": 14.3055}
ARM_VERIFIER_CANDIDATES = 12715

#: Which 55-map final-board label each ladder family's rungs carry, so the
#: audited ``cost_usd`` can be joined. Keyed by (pool, N).
R2_BOARD_LABEL = {
    ("g384_ov128_55map", 1): "A-N1-oracle",
    ("g384_ov128_55map", 3): "A-N3-oracle",
    ("g384_ov128_55map", 5): "A-N5-oracle",
    ("g384_ov128_55map", 10): "A-N10-oracle",
    ("g384_ov192_55map", 1): "B-N1-oracle",
    ("g384_ov192_55map", 3): "B-N3-oracle",
    ("g384_ov192_55map", 5): "B-N5-oracle",
    ("g384_ov192_55map", 10): "B-N10-oracle",
}


def board_costs() -> dict[str, float | None]:
    """``cost_usd`` per label from the r2 55-map final board."""
    doc = json.loads(R2_BOARD.read_text(encoding="utf-8"))
    return {c["label"]: c.get("cost_usd") for c in doc["cells"]}


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


def arm_cost(n: int, arm: str) -> dict[str, Any]:
    """A 3.7-arm rung's simulated all-in cost, flagged as simulated."""
    proposer = ARM_PROPOSER_USD_TOTAL * n / ARM_PROPOSER_PASSES
    verifier = ARM_VERIFIER_USD[arm]
    return {
        "usd": round(proposer + verifier, 2),
        "basis": "part-audited, part-simulated",
        "why": (f"proposer {proposer:.2f} = audited US$"
                f"{ARM_PROPOSER_USD_TOTAL} over {ARM_PROPOSER_PASSES} passes "
                f"scaled to {n}; verifier {verifier:.2f} is the arm's audited "
                f"figure over the FULL K = 5 union of "
                f"{ARM_VERIFIER_CANDIDATES} candidates, not the rung's smaller "
                "one, so the all-in is an upper bound on the verifier leg"),
    }


def build() -> dict[str, Any]:
    """Every multi-rung ladder, with metrics from the register and cost per rung."""
    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    costs = board_costs()
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
                if pool == "g384_ov128" and fam["corpus"] == "4-map-gs":
                    rung["cost"] = {
                        "usd": GS_STRIDE_A_COST_USD[k],
                        "basis": "audited (measured flex)",
                        "why": ("results/stride-2026-08-25/findings.md, 'Exact "
                                "winner ladder' table; $3.407 flex measured "
                                "against $3.41 priced over the four rungs"),
                    }
                    rung["projection_55map_usd"] = round(
                        GS_STRIDE_A_COST_USD[k] * GS_TO_55MAP_TILE_FACTOR, 2)
                    if frame.get(k, {}).get("available"):
                        rung["board_frame"] = frame[k]
                        rung["frame_tax_f1_20"] = round(
                            frame[k]["f1_20"] - cell["f1_20"], 4)
                elif (pool, k) in R2_BOARD_LABEL:
                    board_label = R2_BOARD_LABEL[(pool, k)]
                    usd = costs.get(board_label)
                    rung["cost"] = (
                        {"usd": usd, "basis": "audited (measured flex)",
                         "why": (f"results/55map-final-board-r2-2026-09-06/"
                                 f"final_board_50m.json, cell {board_label}, "
                                 f"cost_usd")}
                        if usd is not None else
                        {"usd": None, "basis": "not supplied",
                         "why": f"the r2 final board records no cost_usd for {board_label}"})
                elif pool == "g384_ov192_55map_g37":
                    rung["cost"] = arm_cost(k, "arm1" if "arm1" in label else "arm2")
                else:
                    rung["cost"] = {
                        "usd": None, "basis": "not supplied",
                        "why": ("no committed audited cost figure covers this "
                                "family's rungs; the fourth cell's verifier meta "
                                "was overwritten by a 29-item cleanup pass "
                                "(reports/r7-gaps-deltas-2026-09-11.md § 2.5)"),
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
            "gs_cost": "results/stride-2026-08-25/findings.md",
            "55map_cost": "results/55map-final-board-r2-2026-09-06/final_board_50m.json",
            "arm_cost": "reports/r7-gaps-deltas-2026-09-11.md §§ 2.2, 2.3, 2.5",
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
