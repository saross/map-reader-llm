#!/usr/bin/env python3
"""
Final 55-map board, stage 3: the 21-cell tiered board.

Executes § 4 of `planning/55map-final-board-2026-08-27.md`: round-robin
tile-swap micro-F1 permutation (10,000, seed 42) over all 21 cells on
the shared 8,541-tile frame, Benjamini–Hochberg q = 0.05 across the
210 pairs, greedy-clique tiers — the GS board instrument imported
verbatim (`permutation_test_float`, `apply_bh_correction`,
`greedy_clique_tiers`), continuing the unbroken methodological chain.

GATES (card § 5; nothing is written unless all pass):

- G3 board-regression gate: the harness re-run on the 8 legacy cells
  alone reproduces the committed standardised board exactly — f1_50
  per cell, pairwise p-values, and tier assignment.
- In-loop mechanism gate: each cell's per-tile micro-F1 must sit
  within 0.003 of its evaluation F1@50 (the board's documented bound).
- Coincidence gates: the three re-derived oracles that land on their
  committed detection sets (TH7, IM, uplift) must reproduce the
  committed evaluations' F1@50 exactly — a free end-to-end validation
  of the stage-1/stage-2 chain.

Inputs: `results/55map-final-board-2026-08-27/cells_manifest.json`
(stage 1) and the stage-2 evaluations; committed evaluations for the
four carried incumbent cells from
`results/55maps-standardised-ref-2026-08-14/`.

Outputs: `final_board_50m.json` + `final-board-50m.md` (ranked board
+ the run × carried/oracle paper table) in the final-board results
directory.

Usage::

    python scripts/final_board_build.py

Zero API. Run on sapphire.

Created: 2026-08-27 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.apply_fdr_correction import apply_bh_correction  # noqa: E402
from scripts.build_55map_leaderboard import (  # noqa: E402
    BOUNDS,
    standardised_gt,
)
from scripts.lib_advanced_metrics import (  # noqa: E402
    compute_per_tile_tp_fp_fn,
)
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    greedy_clique_tiers,
    micro_f1,
    permutation_test_float,
)
from scripts.score_55maps_standardised_reference import (  # noqa: E402
    CELLS as LEGACY_CELLS,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

OUT = PROJECT_ROOT / "results/55map-final-board-2026-08-27"
STD_REF_DIR = PROJECT_ROOT / "results/55maps-standardised-ref-2026-08-14"
COMMITTED_BOARD = (PROJECT_ROOT / "results/55map-leaderboard"
                   / "55map_leaderboard_50m_standardised.json")
BUFFER_M = 50
GATE_TOL = 0.003
N_PERMS = 10_000
SEED = 42

# The four committed carried incumbent cells: (board label, det path,
# committed evaluation path).
COMMITTED_CARRIED = [
    ("TH7-k4", "outputs/55maps-text-high-generalisation/verified/"
               "verified_detections.geojson",
     "results/55maps-standardised-ref-2026-08-14/TH7-k4/evaluation.json"),
    ("T03-k4", "outputs/55maps-text-high-t0.3-generalisation/verified/"
               "verified_detections.geojson",
     "results/55maps-standardised-ref-2026-08-14/T03-k4/evaluation.json"),
    ("TM-k4", "outputs/55maps-text-min-generalisation/verified/"
              "verified_detections.geojson",
     "results/55maps-standardised-ref-2026-08-14/TM-k4/evaluation.json"),
    ("IM-k4", "results/55maps-standardised-ref-2026-08-14/IM-k4/"
              "k4_verified_detections.geojson",
     "results/55maps-standardised-ref-2026-08-14/IM-k4/evaluation.json"),
]

# Oracle cells whose argmax landed on a committed detection set: the
# stage-2 evaluation must equal the committed one exactly.
COINCIDENT = {
    "TH7-oracle": "results/55maps-standardised-ref-2026-08-14/TH7-k3/"
                  "evaluation.json",
    "IM-oracle": "results/55maps-standardised-ref-2026-08-14/IM-k3/"
                 "evaluation.json",
    "UPL-oracle": "results/55maps-standardised-ref-2026-08-14/TM-n10-k5/"
                  "evaluation.json",
}

# Paper-table rows: run -> (carried cell, oracle cell); None = no cell.
PAPER_ROWS = [
    ("B, N = 10 (384/50 %)", "B-N10-carried", "B-N10-oracle"),
    ("B, N = 5", "B-N5-carried", "B-N5-oracle"),
    ("B, N = 3", None, "B-N3-oracle"),
    ("B, N = 1", None, "B-N1-oracle"),
    ("A, N = 10 (384/33 %)", "A-N10-carried", "A-N10-oracle"),
    ("A, N = 5", "A-N5-carried", "A-N5-oracle"),
    ("A, N = 3", None, "A-N3-oracle"),
    ("A, N = 1", None, "A-N1-oracle"),
    ("T0.3 (HIGH, K = 5)", "T03-k4", "T03-oracle"),
    ("T0.7 (HIGH, K = 5)", "TH7-k4", "TH7-oracle"),
    ("min-uplift (K = 10)", None, "UPL-oracle"),
    ("text-min (K = 5)", "TM-k4", "TM-oracle"),
    ("image (HIGH, K = 5)", "IM-k4", "IM-oracle"),
]


def eval50(eval_path: Path) -> dict:
    ev = json.loads(eval_path.read_text())["summary"]
    b = next(x for x in ev["buffers"] if x["buffer_metres"] == BUFFER_M)
    mcc = ev.get("tile_classification", {}).get("mcc")
    return {"f1_50": b["f1"], "ci": [b["f1_ci_lower"], b["f1_ci_upper"]],
            "precision_50": b["precision"], "recall_50": b["recall"],
            "mcc": mcc.get("point") if isinstance(mcc, dict) else mcc,
            "n_detections": ev["n_detections"]}


def per_tile_arrays(det_path: Path, ref, bounds, tile_index, n_tiles):
    det = gpd.read_file(det_path)
    crs = ("EPSG:32635" if abs(det.geometry.x.iloc[0]) > 180 else "EPSG:4326")
    det = det.set_crs(crs, allow_override=True).to_crs("EPSG:32635")
    if "source_tile" not in det.columns:
        raise RuntimeError(f"{det_path}: no source_tile — attribution "
                           "must be origin-tile (S143 lesson)")
    tm = compute_per_tile_tp_fp_fn(det, ref, bounds, buffer_metres=BUFFER_M)
    tp = np.zeros(n_tiles)
    fp = np.zeros(n_tiles)
    fn = np.zeros(n_tiles)
    for _, row in tm.iterrows():
        i = tile_index.get(row["tile_name"])
        if i is not None:
            tp[i], fp[i], fn[i] = (float(row["tp"]), float(row["fp"]),
                                   float(row["fn"]))
    return tp, fp, fn


def round_robin(cells: list[dict]) -> tuple[list[dict], dict, list[list[str]]]:
    pairs, significant = [], {}
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            a, b = cells[i], cells[j]
            r = permutation_test_float(a["tp"], a["fp"], a["fn"],
                                       b["tp"], b["fp"], b["fn"],
                                       n_permutations=N_PERMS, seed=SEED)
            pairs.append({"a": a["label"], "b": b["label"], **r})
    adjusted = apply_bh_correction([p["p_value"] for p in pairs], q=0.05)
    for p, adj in zip(pairs, adjusted):
        p["bh_adjusted_p"] = round(adj, 6)
        p["significant"] = bool(adj < 0.05)
        significant[frozenset({p["a"], p["b"]})] = p["significant"]
    ordered = sorted(cells, key=lambda c: c["f1_50"], reverse=True)
    tiers = greedy_clique_tiers([c["label"] for c in ordered], significant)
    return pairs, significant, tiers


def main() -> int:
    ref = standardised_gt()
    bounds = gpd.read_file(BOUNDS)
    if bounds.crs is None:
        bounds = bounds.set_crs("EPSG:4326")
    bounds = bounds.to_crs("EPSG:32635")
    tile_order = sorted(bounds["tile_name"].tolist())
    tile_index = {t: i for i, t in enumerate(tile_order)}
    n_tiles = len(tile_order)

    # ---- G3: reproduce the committed 8-cell standardised board. ----
    committed = json.loads(COMMITTED_BOARD.read_text())
    legacy = []
    for spec in LEGACY_CELLS:
        label = spec["label"]
        det_path = PROJECT_ROOT / spec["det"]
        ev = eval50(STD_REF_DIR / label / "evaluation.json")
        tp, fp, fn = per_tile_arrays(det_path, ref, bounds, tile_index,
                                     n_tiles)
        if abs(micro_f1(tp.sum(), fp.sum(), fn.sum()) - ev["f1_50"]) \
                > GATE_TOL:
            raise RuntimeError(f"G3 mechanism FAILED {label}")
        legacy.append({"label": label, "tp": tp, "fp": fp, "fn": fn, **ev})
    pairs, _sig, tiers = round_robin(legacy)
    com_f1 = {c["name"].split(" ")[0]: c["f1_50"] for c in committed["cells"]}
    for c in legacy:
        if abs(c["f1_50"] - com_f1[c["label"]]) > 1e-9:
            raise RuntimeError(f"G3 f1 FAILED {c['label']}")
    com_p = {frozenset({p["a"].split(" ")[0], p["b"].split(" ")[0]}):
             p["p_value"] for p in committed["pairwise"]}
    for p in pairs:
        key = frozenset({p["a"], p["b"]})
        if key not in com_p or abs(p["p_value"] - com_p[key]) > 1e-9:
            raise RuntimeError(f"G3 pairwise FAILED {p['a']} vs {p['b']}")
    com_tiers = [[n.split(" ")[0] for n in t] for t in committed["tiers"]]
    if [sorted(t) for t in tiers] != [sorted(t) for t in com_tiers]:
        raise RuntimeError(f"G3 tiers FAILED: {tiers} vs {com_tiers}")
    logger.info("G3 OK: 8-cell board reproduced (f1, %d pairwise p-values, "
                "%d tiers)", len(pairs), len(tiers))

    # ---- Coincidence gates. ----
    for label, committed_eval in COINCIDENT.items():
        new = eval50(OUT / "cells" / label / "evaluation.json")
        old = eval50(PROJECT_ROOT / committed_eval)
        # The current evaluate_detections stores f1 rounded to 4 d.p.;
        # the 2026-08-14 committed evaluations stored full precision.
        # Half a 4-d.p. ulp is therefore identity at stored precision.
        if abs(new["f1_50"] - old["f1_50"]) > 5e-5:
            raise RuntimeError(
                f"coincidence gate FAILED {label}: {new['f1_50']} vs "
                f"{old['f1_50']}")
        logger.info("coincidence OK %-11s F1@50 %.6f == committed", label,
                    new["f1_50"])

    # ---- Assemble the 21 cells. ----
    manifest = json.loads((OUT / "cells_manifest.json").read_text())["cells"]
    cells = []
    for label, det, ev_path in COMMITTED_CARRIED:
        ev = eval50(PROJECT_ROOT / ev_path)
        tp, fp, fn = per_tile_arrays(PROJECT_ROOT / det, ref, bounds,
                                     tile_index, n_tiles)
        entry = next(m for m in manifest if m["label"] == label)
        cells.append({"label": label, "basis": "carried",
                      "point": entry["point"], "tp": tp, "fp": fp,
                      "fn": fn, **ev})
    for m in manifest:
        if m["committed_eval"]:
            continue
        ev = eval50(OUT / "cells" / m["label"] / "evaluation.json")
        tp, fp, fn = per_tile_arrays(PROJECT_ROOT / m["det"], ref, bounds,
                                     tile_index, n_tiles)
        f1m = micro_f1(tp.sum(), fp.sum(), fn.sum())
        if abs(f1m - ev["f1_50"]) > GATE_TOL:
            raise RuntimeError(
                f"mechanism FAILED {m['label']}: micro {f1m:.4f} vs eval "
                f"{ev['f1_50']:.4f}")
        basis = ("oracle" if m["basis"].startswith("oracle")
                 else m["basis"])
        cells.append({"label": m["label"], "basis": basis,
                      "point": m["point"], "tp": tp, "fp": fp, "fn": fn,
                      **ev})
    logger.info("assembled %d cells", len(cells))

    # ---- The 21-cell board. ----
    pairs, _sig, tiers = round_robin(cells)
    tier_of = {n: t for t, members in enumerate(tiers, 1) for n in members}
    n_sig = sum(1 for p in pairs if p["significant"])
    logger.info("%d/%d pairs significant -> %d tiers", n_sig, len(pairs),
                len(tiers))
    ordered = sorted(cells, key=lambda c: c["f1_50"], reverse=True)
    for i, c in enumerate(ordered, 1):
        logger.info("%2d. %-14s T%d %-8s F1@50 %.4f  MCC %s  %s", i,
                    c["label"], tier_of[c["label"]], c["basis"],
                    c["f1_50"],
                    f"{c['mcc']:.3f}" if c["mcc"] is not None else "—",
                    c["point"])

    payload = {
        "buffer_m": BUFFER_M, "reference": "standardised",
        "instrument": ("round-robin tile-swap micro-F1 permutation "
                       f"({N_PERMS}, seed {SEED}) + BH q=0.05 + "
                       "greedy-clique tiers (the GS chain)"),
        "tiers": tiers,
        "cells": [{k: v for k, v in c.items()
                   if k not in ("tp", "fp", "fn")} for c in ordered],
        "pairwise": pairs,
    }
    (OUT / "final_board_50m.json").write_text(
        json.dumps(payload, indent=2, default=float) + "\n")

    # ---- Markdown: ranked board + the run x carried/oracle table. ----
    lines = [
        "# The final 55-map board @ 50 m — every run, carried and oracle",
        "",
        "> **Last revised**: 2026-08-27 (original publication). Card:",
        "> `planning/55map-final-board-2026-08-27.md`. Reference:",
        "> ruling-21 standardised (4,731 student + 279 extension).",
        "> Instrument: " + payload["instrument"] + ".",
        f"> {n_sig}/{len(pairs)} pairs significant.",
        "",
        "| rank | cell | basis | tier | point | F1@50 | 95% CI | P@50 "
        "| R@50 | tile-MCC | n |",
        "|---:|---|---|---:|---|---:|---|---:|---:|---:|---:|",
    ]
    for i, c in enumerate(ordered, 1):
        mcc = f"{c['mcc']:.3f}" if c["mcc"] is not None else "—"
        lines.append(
            f"| {i} | {c['label']} | {c['basis']} | "
            f"{tier_of[c['label']]} | {c['point']} | {c['f1_50']:.4f} | "
            f"[{c['ci'][0]:.4f}, {c['ci'][1]:.4f}] | "
            f"{c['precision_50']:.4f} | {c['recall_50']:.4f} | {mcc} | "
            f"{c['n_detections']} |")
    lines += [
        "",
        "## Runs: as run versus theoretical maximum",
        "",
        "One row per run: the carried (\"as run / GS-chosen\") result and",
        "the oracle (standardised-reference argmax within the verified",
        "sweep space). Tiers from the 21-cell board above.",
        "",
        "| run | carried F1@50 (tier) | oracle F1@50 (tier) | oracle point |",
        "|---|---|---|---|",
    ]
    by_label = {c["label"]: c for c in ordered}
    for row_name, carried, oracle in PAPER_ROWS:
        def fmt(lbl):
            if lbl is None:
                return "—"
            c = by_label[lbl]
            return f"{c['f1_50']:.4f} (T{tier_of[lbl]})"
        opoint = by_label[oracle]["point"] if oracle else "—"
        lines.append(f"| {row_name} | {fmt(carried)} | {fmt(oracle)} | "
                     f"{opoint} |")
    lines += [
        "",
        "## Provenance and gates",
        "",
        "- Stage 1 (`final_board_sweeps.py`): G4 scorer gate ×9 exact;",
        "  identity gates ×9 exact counts; mechanism gates ×5 exact",
        "  (TP, FP, FN) triples; A/B geometry gates 0.0000 m. Oracle",
        "  argmaxes re-derived on the standardised reference — 11 of 13",
        "  equal the previously selected points (T03 and TM nudge",
        "  prob 0.15 → 0.20 by +0.0013 / +0.0001).",
        "- Stage 2: `evaluate_detections.py`, 14 buffers, tile-level BCa",
        "  bootstrap 10,000 / seed 42, `--mcc`, per cell.",
        "- Stage 3 (this build): G3 board-regression gate — the 8-cell",
        "  committed standardised board reproduced exactly (f1, all 28",
        "  pairwise p-values, tiers); coincidence gates — TH7/IM/uplift",
        "  oracles landed on committed detection sets and reproduce the",
        "  committed evaluations exactly; per-cell mechanism bound 0.003.",
        "- Incumbent oracles are best-within-VERIFIED-space (vote ≥ 3",
        "  shells / the ≥ 3-of-10 band); A/B oracles search the full",
        "  vote ≥ 1 unions. N = 1/3 rungs are oracle-only (no carried",
        "  point was ever registered there).",
        "",
        "## Changelog",
        "",
        "### 2026-08-27 — Original publication",
        "",
        "Built by Session 143 per the signed card; $0 API, sapphire.",
    ]
    (OUT / "final-board-50m.md").write_text("\n".join(lines) + "\n")
    logger.info("FINAL BOARD WRITTEN -> %s", (OUT / "final-board-50m.md"
                                              ).relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
