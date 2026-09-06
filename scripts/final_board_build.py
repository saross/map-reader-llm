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

import argparse
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
    board_home,
    reference_gt,
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

#: The r1 board home. Retained as documentation; the output directory is now
#: resolved per run through ``board_home(--reference)``.
OUT = PROJECT_ROOT / "results/55map-final-board-2026-08-27"
STD_REF_DIR = PROJECT_ROOT / "results/55maps-standardised-ref-2026-08-14"

#: Per-cell scoring home by reference vintage. The hard-coded r1 paths in
#: COMMITTED_CARRIED and COINCIDENT below are rewritten through this at run
#: time, so an r2 board reads r2 evaluations for its carried incumbents too.
#: Without that, the four carried cells would stay on r1 while the other 19
#: moved to r2 — precisely the mixed-vintage board the count gate exists to
#: prevent (BLOCKER 1, r2-chain audit, Session 149).
REF_DIR_BY_VINTAGE = {
    "standardised": "results/55maps-standardised-ref-2026-08-14",
    "r2": "results/55maps-r2-ref-2026-09-06",
}


def retarget(path: str, reference: str) -> str:
    """Point an r1-scoring path at the equivalent artefact for a vintage.

    Args:
        path: Repo-relative path containing the r1 scoring home.
        reference: ``standardised`` (identity) or ``r2``.

    Returns:
        The path with its scoring-home component swapped for the vintage's.
        Detection sources under ``outputs/`` are unaffected — the detections
        do not change between references, only the scoring of them does.
    """
    return path.replace(REF_DIR_BY_VINTAGE["standardised"],
                        REF_DIR_BY_VINTAGE[reference])
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

# Run cost, est. all-in flex, FULL basis (proposer x N/10 + full-union
# verification for A/B, from the stride55 findings Pareto; audited
# whole-run spend for the incumbents, token-load audit § 6; uplift at
# full-cost basis 10 x $4.66 + $11.27). Both of a run's cells (carried
# and oracle) share the run's cost — the operating point is free.
FAMILY_COST = {
    "A-N1": 20.53, "A-N3": 41.22, "A-N5": 59.75, "A-N10": 103.91,
    "B-N1": 30.99, "B-N3": 65.48, "B-N5": 97.22, "B-N10": 173.59,
    "TM": 23.4, "TH7": 207.4, "T03": 261.0, "IM": 195.4, "UPL": 57.87,
}


def family_of(label: str) -> str:
    """Cost family for a board cell label."""
    for fam in sorted(FAMILY_COST, key=len, reverse=True):
        if label == fam or label.startswith(fam + "-"):
            return fam
    raise KeyError(label)


def compact_letters(ordered_labels: list[str],
                    significant: dict) -> dict[str, str]:
    """Compact letter display from the BH-adjusted pairwise matrix.

    Cells sharing a letter are NOT significantly different: letters are
    the maximal cliques of the non-significance graph (Bron–Kerbosch;
    21 nodes), lettered in order of their best-ranked member.
    """
    adj = {a: set() for a in ordered_labels}
    for i, a in enumerate(ordered_labels):
        for b in ordered_labels[i + 1:]:
            if not significant[frozenset({a, b})]:
                adj[a].add(b)
                adj[b].add(a)
    cliques: list[set] = []

    def bk(r: set, p: set, x: set) -> None:
        if not p and not x:
            cliques.append(r)
            return
        for v in sorted(p):
            bk(r | {v}, p & adj[v], x & adj[v])
            p = p - {v}
            x = x | {v}

    bk(set(), set(ordered_labels), set())
    rank = {lab: i for i, lab in enumerate(ordered_labels)}
    cliques.sort(key=lambda c: (min(rank[m] for m in c),
                                -len(c)))
    letters: dict[str, list[str]] = {lab: [] for lab in ordered_labels}
    for i, clique in enumerate(cliques):
        letter = chr(ord("a") + i) if i < 26 else f"z{i - 25}"
        for m in clique:
            letters[m].append(letter)
    return {lab: "".join(sorted(v)) for lab, v in letters.items()}


# Paper-table rows: run -> (carried cell, oracle cell); None = no cell.
PAPER_ROWS = [
    ("B, N = 10 (384/50 %)", "B-N10-carried", "B-N10-oracle"),
    ("B, N = 5", "B-N5-carried", "B-N5-oracle"),
    ("B, N = 3", "B-N3-carried", "B-N3-oracle"),
    ("B, N = 1", None, "B-N1-oracle"),
    ("A, N = 10 (384/33 %)", "A-N10-carried", "A-N10-oracle"),
    ("A, N = 5", "A-N5-carried", "A-N5-oracle"),
    ("A, N = 3", "A-N3-carried", "A-N3-oracle"),
    ("A, N = 1", None, "A-N1-oracle"),
    ("T0.3 (HIGH, K = 5)", "T03-k4", "T03-oracle"),
    ("T0.7 (HIGH, K = 5)", "TH7-k4", "TH7-oracle"),
    ("min-uplift (K = 10)", None, "UPL-oracle"),
    ("text-min (K = 5)", "TM-k4", "TM-oracle"),
    # PI ruling 2026-08-28: image's real-world column shows the cell the
    # run actually shipped (k3); for image the shipped point coincides
    # with the standardised-reference argmax, so carried and oracle are
    # the same cell. IM-k4 (E82) stays as the comparability derivation.
    ("image (HIGH, K = 5) — as shipped (k3)", "IM-oracle", "IM-oracle"),
    ("image comparability (k4, E82)", "IM-k4", None),
]
DISPLAY_BASIS = {
    "image (HIGH, K = 5) — as shipped (k3)": "as-shipped (k3)",
    "image comparability (k4, E82)": "comparability (k4)",
}


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


def render_figure(ordered: list[dict], tier_of: dict, sig: dict,
                  cld: dict[str, str], out_png: Path) -> None:
    """Two-panel significance figure: F1 dot-and-CI plot with tier bands
    and compact letters; BH-significance matrix, both rank-ordered."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = [c["label"] for c in ordered]
    n = len(labels)
    ys = list(range(n - 1, -1, -1))  # rank 1 at the top
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(13.5, 8.5), gridspec_kw={"width_ratios": [1.35, 1]})

    for c, y in zip(ordered, ys):
        if tier_of[c["label"]] % 2 == 0:
            ax1.axhspan(y - 0.5, y + 0.5, color="0.92", zorder=0)
        colour = ("#1a6faf" if c["basis"].startswith("carried")
                  else "#c25e00")
        marker = "o" if c["basis"].startswith("carried") else "s"
        ax1.plot([c["ci"][0], c["ci"][1]], [y, y], color=colour, lw=1.4,
                 zorder=2)
        ax1.plot(c["f1_50"], y, marker, color=colour, ms=6, zorder=3)
        ax1.text(1.001, y, f"T{tier_of[c['label']]}  {cld[c['label']]}",
                 transform=ax1.get_yaxis_transform(), fontsize=8,
                 va="center", family="monospace")
    ax1.set_yticks(ys, labels, fontsize=9)
    ax1.set_xlabel("corrected-F1 @ 50 m (95 % BCa CI)")
    ax1.set_title("Cells sharing a letter are statistically\n"
                  "indistinguishable (BH q = 0.05)", fontsize=10)
    ax1.grid(axis="x", color="0.85", lw=0.6, zorder=0)
    from matplotlib.lines import Line2D
    ax1.legend(handles=[
        Line2D([], [], marker="o", color="#1a6faf", ls="", label="carried"),
        Line2D([], [], marker="s", color="#c25e00", ls="", label="oracle")],
        loc="lower right", fontsize=9)

    mat = np.zeros((n, n))
    for i, a in enumerate(labels):
        for j, b in enumerate(labels):
            if i != j:
                mat[i, j] = 1.0 if sig[frozenset({a, b})] else 0.0
    ax2.imshow(mat, cmap="Greys", vmin=0, vmax=1.4, aspect="equal")
    ax2.set_xticks(range(n), labels, rotation=90, fontsize=7)
    ax2.set_yticks(range(n), labels, fontsize=7)
    ax2.set_title("Pairwise significance matrix\n(dark = significantly "
                  "different)", fontsize=10)
    for t in sorted(set(tier_of.values())):
        idx = [i for i, lab in enumerate(labels) if tier_of[lab] == t]
        lo, hi = min(idx) - 0.5, max(idx) + 0.5
        ax2.add_patch(plt.Rectangle((lo, lo), hi - lo, hi - lo, fill=False,
                                    edgecolor="#1a6faf", lw=1.2))
    fig.suptitle("The final 55-map board: statistical groups @ 50 m "
                 "(round-robin tile-swap, 10k, BH q = 0.05)", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    logger.info("figure -> %s", out_png.relative_to(PROJECT_ROOT))


def main(reference: str = "standardised") -> int:
    """Build the 50 m final board against one reference vintage.

    Args:
        reference: ``standardised`` (r1, default) or ``r2``.

    Returns:
        Process exit code.
    """
    out = board_home(reference)
    # TWO references, deliberately (BLOCKER 4, r2-chain audit; PI ruling,
    # Session 149). ``gate_ref`` is ALWAYS r1: G3 asks whether this code still
    # reproduces the committed r1 board, which is a regression test on the
    # mechanism and must stay live during an r2 build — pointing it at r2 would
    # compare r2 numbers to the r1 board and fail by construction, switching
    # the gate off exactly when a new reference makes it most valuable.
    # ``ref`` is the vintage the new board is actually scored against.
    gate_ref = standardised_gt()
    ref = reference_gt(reference) if reference != "standardised" else gate_ref
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
        tp, fp, fn = per_tile_arrays(det_path, gate_ref, bounds, tile_index,
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
        new = eval50(out / "cells" / label / "evaluation.json")
        old = eval50(PROJECT_ROOT / retarget(committed_eval, reference))
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
    manifest = json.loads((out / "cells_manifest.json").read_text())["cells"]
    cells = []
    for label, det, ev_path in COMMITTED_CARRIED:
        ev = eval50(PROJECT_ROOT / retarget(ev_path, reference))
        tp, fp, fn = per_tile_arrays(PROJECT_ROOT / det, ref, bounds,
                                     tile_index, n_tiles)
        entry = next(m for m in manifest if m["label"] == label)
        cells.append({"label": label, "basis": "carried",
                      "point": entry["point"], "tp": tp, "fp": fp,
                      "fn": fn, **ev})
    for m in manifest:
        if m["committed_eval"]:
            continue
        ev = eval50(out / "cells" / m["label"] / "evaluation.json")
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
    pairs, sig, tiers = round_robin(cells)
    tier_of = {n: t for t, members in enumerate(tiers, 1) for n in members}
    n_sig = sum(1 for p in pairs if p["significant"])
    logger.info("%d/%d pairs significant -> %d tiers", n_sig, len(pairs),
                len(tiers))
    ordered = sorted(cells, key=lambda c: c["f1_50"], reverse=True)
    cld = compact_letters([c["label"] for c in ordered], sig)
    for i, c in enumerate(ordered, 1):
        logger.info("%2d. %-14s T%d %-6s %-8s F1@50 %.4f  MCC %s  %s", i,
                    c["label"], tier_of[c["label"]], cld[c["label"]],
                    c["basis"], c["f1_50"],
                    f"{c['mcc']:.3f}" if c["mcc"] is not None else "—",
                    c["point"])
    render_figure(ordered, tier_of, sig, cld,
                  out / "significance-groups.png")

    payload = {
        "buffer_m": BUFFER_M, "reference": "standardised",
        "instrument": ("round-robin tile-swap micro-F1 permutation "
                       f"({N_PERMS}, seed {SEED}) + BH q=0.05 + "
                       "greedy-clique tiers (the GS chain)"),
        "tiers": tiers,
        "cells": [{**{k: v for k, v in c.items()
                      if k not in ("tp", "fp", "fn")},
                   "group": cld[c["label"]],
                   "cost_usd": FAMILY_COST[family_of(c["label"])]}
                  for c in ordered],
        "pairwise": pairs,
    }
    (out / "final_board_50m.json").write_text(
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
        "| rank | cell | basis | tier | group | cost | point | F1@50 "
        "| 95% CI | P@50 | R@50 | tile-MCC | n |",
        "|---:|---|---|---:|---|---:|---|---:|---|---:|---:|---:|---:|",
    ]
    for i, c in enumerate(ordered, 1):
        mcc = f"{c['mcc']:.3f}" if c["mcc"] is not None else "—"
        cost = FAMILY_COST[family_of(c["label"])]
        lines.append(
            f"| {i} | {c['label']} | {c['basis']} | "
            f"{tier_of[c['label']]} | {cld[c['label']]} | ${cost:.0f} | "
            f"{c['point']} | {c['f1_50']:.4f} | "
            f"[{c['ci'][0]:.4f}, {c['ci'][1]:.4f}] | "
            f"{c['precision_50']:.4f} | {c['recall_50']:.4f} | {mcc} | "
            f"{c['n_detections']} |")
    lines += [
        "",
        "**Reading the groups**: `tier` is the greedy-clique tier (disjoint",
        "bands); `group` is the compact letter display — cells sharing ANY",
        "letter are statistically indistinguishable under the BH-adjusted",
        "pairwise tests, so letters show the overlaps the disjoint tiers",
        "cannot. `cost` is the run's audited all-in flex spend (full",
        "basis); a run's carried and oracle cells share it. See",
        "`significance-groups.png` for the dot-and-CI plot and the full",
        "pairwise significance matrix.",
    ]
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
        "PI ruling 2026-08-28 on the image rows: the real-world column",
        "shows the cell the image run actually SHIPPED (k3 — which for",
        "image coincides with the standardised-reference argmax, so its",
        "carried and oracle entries are the same cell); IM-k4 remains on",
        "the board as E82's like-for-like comparability derivation.",
    ]
    # ---- Cost-efficiency table: one row per run, deployment basis. ----
    eff_rows = []
    for row_name, carried, oracle in PAPER_ROWS:
        lbl = carried or oracle
        c = by_label[lbl]
        cost = FAMILY_COST[family_of(lbl)]
        tp = round(c["precision_50"] * c["n_detections"])
        eff_rows.append({
            "name": row_name, "label": lbl,
            "basis": DISPLAY_BASIS.get(row_name, c["basis"]),
            "cost": cost, "f1": c["f1_50"],
            "tier": tier_of[lbl], "tp": tp,
            "usd_per_mound": cost / tp})
    eff_rows.sort(key=lambda r: r["cost"])
    best_so_far = 0.0
    for r in eff_rows:
        r["frontier"] = r["f1"] > best_so_far
        if r["frontier"]:
            best_so_far = r["f1"]
    prev = None
    for r in eff_rows:
        if r["frontier"]:
            if prev is not None:
                d_f1 = (r["f1"] - prev["f1"]) * 100
                r["marginal"] = (r["cost"] - prev["cost"]) / d_f1
            prev = r
    # T1 ceiling rows: the Tier-1 cell(s), shown for cost comparison
    # only — outside the deployment-basis frontier computation.
    for lbl in tiers[0]:
        c = by_label[lbl]
        cost = FAMILY_COST[family_of(lbl)]
        tp = round(c["precision_50"] * c["n_detections"])
        eff_rows.append({
            "name": f"{lbl} (T1 ceiling)", "label": lbl,
            "basis": c["basis"], "cost": cost, "f1": c["f1_50"],
            "tier": tier_of[lbl], "tp": tp,
            "usd_per_mound": cost / tp, "frontier": "ceiling"})
    eff_rows.sort(key=lambda r: r["cost"])
    lines += [
        "",
        "## Cost efficiency: what a dollar buys",
        "",
        "One row per run at its DEPLOYMENT basis (carried where one",
        "exists, otherwise the rung oracle, marked). `$/mound` is the",
        "run's full flex cost per true-positive mound at 50 m — the",
        "project's established per-mound economics. `marginal $/+0.01 F1`",
        "prices each step UP the cost-sorted Pareto frontier (— =",
        "dominated: a cheaper run scores higher). Plain F1-per-dollar is",
        "deliberately omitted — it is maximised by the cheapest run",
        "almost regardless of quality.",
        "",
        "| run | basis | cost | F1@50 (tier) | TP mounds | $/mound | "
        "frontier | marginal $/+0.01 F1 |",
        "|---|---|---:|---|---:|---:|---|---:|",
    ]
    for r in eff_rows:
        marg = (f"${r['marginal']:.2f}" if r.get("marginal") is not None
                and r["frontier"] and "marginal" in r else "—")
        front = ("ceiling" if r["frontier"] == "ceiling"
                 else "YES" if r["frontier"] else "—")
        lines.append(
            f"| {r['name']} | {r['basis']} | ${r['cost']:.0f} | "
            f"{r['f1']:.4f} (T{r['tier']}) | {r['tp']:,} | "
            f"${r['usd_per_mound']:.4f} | {front} | {marg} |")
    lines += [
        "",
        "## Post-hoc: the emergent N = 3 carried cells",
        "",
        "The `A-N3-carried` and `B-N3-carried` cells are **emergent",
        "post-hoc nominations**, not registered claims: the card carried",
        "operating points only at N = 5 and N = 10, so no N = 3 point was",
        "nominated before launch. They are on the board because the",
        "question \"could the N = 3 configuration have been specified in",
        "advance?\" turns out to have a documented answer: the committed",
        "GS stride ladder (`results/stride-2026-08-25/",
        "plateau_analyses.json`, built before the 55-map launch) had",
        "already selected **(0.15, k3-of-3) for BOTH geometries** at",
        "N = 3. These cells simply evaluate that pre-existing GS",
        "selection at deployment — the same derivation discipline as the",
        "registered P2/P4 points, applied one rung further down. The",
        "distinction that matters: the GS selection is pre-launch and",
        "committed; the DECISION to evaluate it is post-hoc (2026-08-28,",
        "PI-directed), motivated by the N = 3 oracle's position on the",
        "cost frontier. Read their tiers and group letters accordingly —",
        "instructive, not confirmatory. A registered replication (e.g.",
        "nominating N = 3 in any future deployment card, or the",
        "retro-N = 3 exploration of other runs the PI has flagged) is",
        "the honest path to promoting this rung.",
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
        "### 2026-08-28 (later) — Image rows per the as-shipped ruling",
        "",
        "PI ruling: image's real-world entry is the shipped k3 cell;",
        "IM-k4 relabelled as the E82 comparability derivation. Board",
        "membership, tiers, and all cell values unchanged — run-table",
        "and efficiency-table presentation only.",
        "",
        "### 2026-08-28 — Emergent N = 3 carried cells + T1 ceiling row",
        "",
        "PI direction: the GS-ladder-selected (0.15, k3) points for both",
        "geometries added as `carried (post-hoc)` cells (23-cell board,",
        "253 pairs re-tiered; see the post-hoc section for the emergent",
        "status), and the Tier-1 cell added to the efficiency table as a",
        "ceiling row for cost comparison.",
        "",
        "### 2026-08-27 (later) — Groups, costs, and efficiency",
        "",
        "PI request (interactive): compact-letter-display `group` column",
        "and the two-panel significance figure",
        "(`significance-groups.png`); run-cost column; the",
        "cost-efficiency section ($/mound + marginal frontier pricing).",
        "Board membership, tiers, and all cell values unchanged.",
        "",
        "### 2026-08-27 — Original publication",
        "",
        "Built by Session 143 per the signed card; $0 API, sapphire.",
    ]
    (out / "final-board-50m.md").write_text("\n".join(lines) + "\n")
    logger.info("FINAL BOARD WRITTEN -> %s", (out / "final-board-50m.md"
                                              ).relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    _ap = argparse.ArgumentParser(description=__doc__)
    _ap.add_argument(
        "--reference", choices=["standardised", "r2"], default="standardised",
        help="Reference vintage to tier against (default: r1, unchanged "
             "behaviour). With r2 the board is written to "
             "55map-final-board-r2-2026-09-06/, cells are read from the r2 "
             "scoring home, and the G3 regression gate STILL reproduces the "
             "committed r1 board.",
    )
    sys.exit(main(_ap.parse_args().reference))
