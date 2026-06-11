#!/usr/bin/env python3
# ============================================================================
# sweep_unswept_pools.py
# ----------------------------------------------------------------------------
# Session 112 ($0): sweep every verified proposer-verifier (PV) pool on disk
# that was never swept into a CURRENT-ERA results artefact, and write a single
# consolidated results file. "Current era" means the Session 109-111 scoring
# stack: scripts.lib_advanced_metrics.score_detection_set (point F1 @ 20 m,
# Hungarian matching, tile-MCC), curator ground truth, GS 384 px / 487-tile
# bounds. The March-2026 results/h11-384-pv-diagnostic threshold sweeps used a
# superseded ground truth and a prob-threshold-only sweep, so they do NOT
# count as swept (precedent: flash-high-image-1of5 was treated as unswept and
# scored fresh into results/working-precision/gs-image-pv-cell.json).
#
# ENUMERATION SCOPE (146 directories):
#   outputs/h11/pv-diag-384/verified/*            (138 dirs)
#   outputs/verifier-robustness/*/T*/verified     (8 dirs)
#
# CLASSIFICATION (constants below; verified against the anchors named there):
#   - 11 pv-diag dirs + all 8 verifier-robustness dirs: already swept.
#   - 6 dirs: byte-identical duplicate-format regenerations of an already
#     classified dir (probabilities compared value-for-value; n_diff = 0).
#   - 103 dirs: k-of-N band directories. Two sub-kinds, recorded per dir:
#     "derived_subset" (probabilities.json carries source/vote_threshold —
#     a post-hoc vote filter of the 1ofN draw, identical probabilities) and
#     "independent_draw" (own run.meta.json; March-era separate T=0.0 verify
#     draws that differ on ~3-5% of shared candidates). Neither is a distinct
#     pool: the k-of-N sweep over the 1ofN union covers the same subsets, so
#     band dirs are counted, not swept.
#   - 18 dirs: genuinely unswept (pool x verifier-config) cells — swept here.
#
# SWEEP (mirrors scripts/score_min_thinking_pv.py exactly): join the crops
# candidate_manifest.json (centroids in EPSG:32635 == evaluation CRS) to the
# n=1 verifier probabilities via load_candidate_table, sweep proposer-k x
# prob_t in {0.05..0.5} under the n=1 "mean" rule, score each accepted set
# with score_detection_set (buffer 20 m, compute_mcc=True), then re-score the
# best operating point at the shared 50 m operational buffer. Single-pass
# baseline pools have no vote_count in the manifest; their vote is set to 1
# (the k sweep degenerates to k=1, as it must for one proposer pass).
#
# Verifier identities follow the THREE-SOURCE rule (protocol-errata.md E42):
# configuration.model is unreliable pre-Session-57, so every verifier model
# below was confirmed from cost_estimate.pricing_used.model, and proposer
# lineages from the detection-GeoJSON feature properties.
#
# COST: $0 (on-disk re-score). Run on zbook per the project compute rule.
#
# Usage:
#   .venv/bin/python scripts/sweep_unswept_pools.py \
#       2>&1 | tee results/verifier-robustness/unswept_pools_sweep.log
#
# Output:
#   results/verifier-robustness/unswept_pools_sweep.json
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from scripts.analyse_verifier_robustness import (  # noqa: E402
    BOUNDS_BY_SIZE,
    EVAL_CRS,
    GROUND_TRUTH,
    accepted_cids,
    load_candidate_table,
)
from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_advanced_metrics import score_detection_set  # noqa: E402

PV = BASE_DIR / "outputs" / "h11" / "pv-diag-384"
CROPS = PV / "crops"
VERIFIED = PV / "verified"
VR = BASE_DIR / "outputs" / "verifier-robustness"
OUT_JSON = BASE_DIR / "results" / "verifier-robustness" / "unswept_pools_sweep.json"
PROB_TS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]

# ---------------------------------------------------------------------------
# Registry of the 18 genuinely unswept (pool x verifier-config) cells.
# manifest = crops manifest the verifier consumed (candidate_id key space);
# probs    = verified dir holding that draw's probabilities.json.
# Verifier model from cost_estimate.pricing_used.model (E42 three-source rule);
# proposer model from detection-GeoJSON properties.model.
# ---------------------------------------------------------------------------
FLASH_MIN_VF = "gemini-3-flash adversarial-text, minimal thinking, T=0.0, n=1"
FLASH_MED_VF = "gemini-3-flash adversarial-text, medium thinking, T=0.0, n=1"
PRO_MED_VF = "gemini-3.1-pro-preview adversarial-text, medium thinking, T=0.0, n=1"

CELLS = [
    {
        "label": "flash-high-text-30pass + flash-min vf",
        "manifest": "flash-high-text-1of30",
        "probs": "flash-high-text-1of30",
        "proposer": "gemini-3-flash-preview HIGH text T0.7, 30-pass union (11771 cands)",
        "verifier": FLASH_MIN_VF,
        "note": "full 1of30 union never PV-swept — headline 0.8902 (high31) used only "
                "the 729-crop 16of30 subset (pool_recall_ceilings.json best_pv_f1=null)",
    },
    {
        "label": "flash-high-text-5pass + PRO vf",
        "manifest": "flash-high-text-1of5",
        "probs": "flash-high-text-1of5-pro-verifier",
        "proposer": "gemini-3-flash-preview HIGH text T0.7, 5-pass union (3736 cands)",
        "verifier": PRO_MED_VF,
        "note": "high_thinking_prior.log swept minimal/medium/high FLASH verifiers over "
                "this union but not the Pro verifier draw",
    },
    {
        "label": "image-min-t07-5pass + flash-min vf",
        "manifest": "image-1of5",
        "probs": "image-1of5",
        "proposer": "gemini-3-flash-preview MINIMAL image T0.7, 5-pass union "
                    "(first 5 of the 10-run image-n5 study; 1123 cands)",
        "verifier": FLASH_MIN_VF,
        "note": "image twin of the swept text-min lineage (min_thinking_pv.log)",
    },
    {
        "label": "image-min-t07-10pass + flash-min vf",
        "manifest": "image-1of10",
        "probs": "image-1of10",
        "proposer": "gemini-3-flash-preview MINIMAL image T0.7, 10-pass union (1444 cands)",
        "verifier": FLASH_MIN_VF,
        "note": "image twin of the swept text-min 10-pass cell (min11)",
    },
    {
        "label": "image-min-t00-baseline + flash-min vf",
        "manifest": "image-baseline",
        "probs": "image-baseline",
        "proposer": "gemini-3-flash-preview MINIMAL image T0.0, single pass (746 cands)",
        "verifier": FLASH_MIN_VF,
        "note": "single-pass pool; proposer-k degenerates to 1",
    },
    {
        "label": "image-min-t00-baseline + flash-med vf",
        "manifest": "image-baseline",
        "probs": "flash-minimal-image-medium-verifier",
        "proposer": "gemini-3-flash-preview MINIMAL image T0.0, single pass (746 cands)",
        "verifier": FLASH_MED_VF,
        "note": "",
    },
    {
        "label": "image-min-t00-baseline + pro vf",
        "manifest": "image-baseline",
        "probs": "image-baseline-pro-verifier",
        "proposer": "gemini-3-flash-preview MINIMAL image T0.0, single pass (746 cands)",
        "verifier": PRO_MED_VF,
        "note": "",
    },
    {
        "label": "text-min-t00-baseline + flash-min vf",
        "manifest": "text-baseline",
        "probs": "text-baseline",
        "proposer": "gemini-3-flash-preview MINIMAL text T0.0, single pass (1047 cands)",
        "verifier": FLASH_MIN_VF,
        "note": "single-pass pool; proposer-k degenerates to 1",
    },
    {
        "label": "text-min-t00-baseline + flash-med vf",
        "manifest": "text-baseline",
        "probs": "flash-minimal-text-medium-verifier",
        "proposer": "gemini-3-flash-preview MINIMAL text T0.0, single pass (1047 cands)",
        "verifier": FLASH_MED_VF,
        "note": "",
    },
    {
        "label": "text-min-t00-baseline + pro vf",
        "manifest": "text-baseline",
        "probs": "text-baseline-pro-verifier",
        "proposer": "gemini-3-flash-preview MINIMAL text T0.0, single pass (1047 cands)",
        "verifier": PRO_MED_VF,
        "note": "",
    },
    {
        "label": "pro-high-text-5pass + flash-med vf",
        "manifest": "pro-high-text-1of5",
        "probs": "pro-high-text-1of5",
        "proposer": "gemini-3.1-pro-preview HIGH text T0.7, 5-pass union (504 cands)",
        "verifier": FLASH_MED_VF,
        "note": "third verifier draw over the pro text union — pro_pv.log swept only the "
                "flash-minimal and pro draws; probabilities differ from both",
    },
    {
        "label": "pro-high-image-5pass + pro vf",
        "manifest": "pro-high-image-1of5",
        "probs": "pro-high-image-1of5-pro-verifier",
        "proposer": "gemini-3.1-pro-preview HIGH image T0.7, 5-pass union (841 cands)",
        "verifier": PRO_MED_VF,
        "note": "only verifier draw over the pro image union",
    },
    {
        "label": "pro-med-text-baseline + flash-min vf",
        "manifest": "pro-medium-text-baseline",
        "probs": "pro-text-minimal-verifier",
        "proposer": "gemini-3.1-pro-preview MEDIUM text T0.0, single pass (430 cands)",
        "verifier": FLASH_MIN_VF,
        "note": "",
    },
    {
        "label": "pro-med-text-baseline + flash-med vf",
        "manifest": "pro-medium-text-baseline",
        "probs": "pro-text-medium-verifier",
        "proposer": "gemini-3.1-pro-preview MEDIUM text T0.0, single pass (430 cands)",
        "verifier": FLASH_MED_VF,
        "note": "",
    },
    {
        "label": "pro-med-text-baseline + pro vf",
        "manifest": "pro-medium-text-baseline",
        "probs": "pro-medium-text-baseline-pro-verifier",
        "proposer": "gemini-3.1-pro-preview MEDIUM text T0.0, single pass (430 cands)",
        "verifier": PRO_MED_VF,
        "note": "",
    },
    {
        "label": "pro-med-image-baseline + flash-min vf",
        "manifest": "pro-medium-image-baseline",
        "probs": "pro-image-minimal-verifier",
        "proposer": "gemini-3.1-pro-preview MEDIUM image T0.0, single pass (519 cands)",
        "verifier": FLASH_MIN_VF,
        "note": "",
    },
    {
        "label": "pro-med-image-baseline + flash-med vf",
        "manifest": "pro-medium-image-baseline",
        "probs": "pro-image-medium-verifier",
        "proposer": "gemini-3.1-pro-preview MEDIUM image T0.0, single pass (519 cands)",
        "verifier": FLASH_MED_VF,
        "note": "",
    },
    {
        "label": "pro-med-image-baseline + pro vf",
        "manifest": "pro-medium-image-baseline",
        "probs": "pro-medium-image-baseline-pro-verifier",
        "proposer": "gemini-3.1-pro-preview MEDIUM image T0.0, single pass (519 cands)",
        "verifier": PRO_MED_VF,
        "note": "",
    },
]

# ---------------------------------------------------------------------------
# Already-swept cells (pv-diag-384/verified dirs), each with its anchor — the
# current-era results artefact that recorded the sweep.
# ---------------------------------------------------------------------------
ALREADY_SWEPT = {
    "flash-high-image-1of5":
        "results/working-precision/gs-image-pv-cell.json (F1@20=0.7778, 3of5/pt0.15)",
    "flash-high-text-1of5":
        "results/verifier-robustness/pareto/pareto_v2.{json,log} rung high6 (0.8641) + "
        "high_thinking_prior.log minimal_n1 column",
    "flash-high-text-1of10":
        "results/verifier-robustness/nof10_comparison.log (0.8769, 6of10/pt0.2) + "
        "pareto_v2 rung high11",
    "flash-high-text-16of30":
        "headline cell 0.8902 — opmax_vs_headline.log + pareto_v2 rung high31 + "
        "robustness_{grid,summary}_T0.3-16of30.json (N=5 re-verification); also a "
        "derived vote-subset of flash-high-text-1of30",
    "flash-high-text-1of5-flash-medium-verifier":
        "results/verifier-robustness/high_thinking_prior.log medium_n1 column",
    "flash-high-text-1of5-flash-high-verifier":
        "results/verifier-robustness/high_thinking_prior.log high_n1 column",
    "flash-minimal-text-t07-1of5":
        "results/verifier-robustness/min_thinking_pv.log (0.8708, 4of5/pt0.15)",
    "text-1of10":
        "results/verifier-robustness/min_thinking_pv.log (0.8835, 6of10/pt0.2) + "
        "pareto_v2 rung min11",
    "text-min-t07-true-1of5":
        "results/verifier-robustness/min6_true_makeup.json (0.8784, 3of5/pt0.15) + "
        "pareto_v2 rung min6",
    "pro-high-text-1of5-flash-minimal-verifier":
        "results/verifier-robustness/pro_pv.log (0.8491, 3of5/pt0.15)",
    "pro-high-text-1of5-pro-verifier":
        "results/verifier-robustness/pro_pv.log (0.8506, 3of5/pt0.15)",
}

# verifier-robustness/*/T*/verified dirs -> grid/summary anchors.
VR_SWEPT = {
    "256-text-1of5-union/T0.0/verified": "robustness_{grid,summary}_T0.0.json",
    "256-text-ge3of5/T0.3/verified": "robustness_{grid,summary}_T0.3.json",
    "384-flash-high-text-16of30/T0.3/verified": "robustness_{grid,summary}_T0.3-16of30.json",
    "384-flash-high-text-1of5-union/T0.0/verified": "robustness_{grid,summary}_T0.0.json",
    "384-flash-high-text-ge3of5/T0.3/verified": "robustness_{grid,summary}_T0.3.json",
    "384-flash-high-text-ge3of5/T0.3-high/verified": "robustness_{grid,summary}_T0.3-high.json",
    "384-flash-high-text-ge3of5/T0.7/verified": "robustness_{grid,summary}_T0.7.json",
    "384-flash-high-text-ge3of5/T0.7-high/verified": "robustness_{grid,summary}_T0.7-high.json",
}

# Byte-identical duplicate-format regenerations (probabilities compared
# value-for-value against the source dir; zero differences).
DUPLICATE_FORMAT = {
    "flash-high-text-high-vf-1of5": "flash-high-text-1of5-flash-high-verifier",
    "flash-high-text-medium-vf-1of5": "flash-high-text-1of5-flash-medium-verifier",
    "flash-high-text-pro-vf-1of5": "flash-high-text-1of5-pro-verifier",
    "pro-high-text-flash-min-vf-1of5": "pro-high-text-1of5-flash-minimal-verifier",
    "pro-high-text-pro-vf-1of5": "pro-high-text-1of5-pro-verifier",
    "pro-high-image-pro-vf-1of5": "pro-high-image-1of5-pro-verifier",
}


def classify_band_dirs() -> list[dict]:
    """Enumerate the k-of-N band directories (k >= 2) and tag each one.

    A band dir whose probabilities.json carries a ``source`` field is a
    "derived_subset" (post-hoc vote filter of the 1ofN draw — identical
    probabilities); one with its own run.meta.json is an "independent_draw"
    (a separate March-era T=0.0 verify call over the vote subset). Neither is
    a distinct pool, so they are recorded but not swept. ``text-2of5..5of5``
    are draws over the ARCHIVED partial text-1of5 union (superseded by
    text-min-t07-true-1of5) and are tagged accordingly.
    """
    classified_elsewhere = (
        set(ALREADY_SWEPT) | set(DUPLICATE_FORMAT)
        | {c["probs"] for c in CELLS}
    )
    out = []
    for d in sorted(VERIFIED.iterdir()):
        if not d.is_dir() or d.name in classified_elsewhere:
            continue
        probs_path = d / "probabilities.json"
        if not probs_path.exists():
            out.append({"dir": d.name, "kind": "no_probabilities"})
            continue
        head = json.loads(probs_path.read_text())
        kind = "derived_subset" if head.get("source") else (
            "independent_draw" if (d / "run.meta.json").exists() else "unknown")
        entry = {"dir": d.name, "kind": kind,
                 "n_candidates": len(head.get("results", {}))}
        if head.get("source"):
            entry["source"] = head["source"]
        if d.name.startswith("text-") and d.name.endswith("of5"):
            entry["note"] = ("draw over the archived partial text-1of5 union "
                             "(superseded; see archive/superseded-unions/)")
        out.append(entry)
    return out


def build_table(cell: dict) -> list[dict]:
    """Load and join one cell's candidate table; default single-pass vote to 1.

    Args:
        cell: registry entry with ``manifest`` (crops dir name) and ``probs``
            (verified dir name).

    Returns:
        Candidate table as produced by
        :func:`scripts.analyse_verifier_robustness.load_candidate_table`,
        with ``vote_count`` coerced to 1 when the manifest carries none
        (single-pass baseline pools).
    """
    manifest = CROPS / cell["manifest"] / "candidate_manifest.json"
    probs = VERIFIED / cell["probs"] / "probabilities.json"
    table = load_candidate_table(manifest, probs)
    if table and max(r["vote_count"] for r in table) == 0:
        for r in table:
            r["vote_count"] = 1
    return table


def sweep_cell(cell: dict, table: list[dict], gdf_ref: gpd.GeoDataFrame,
               gdf_bounds: gpd.GeoDataFrame) -> dict:
    """Sweep proposer-k x prob_t (n=1 "mean" rule) for one cell.

    Mirrors score_min_thinking_pv.sweep: best F1@20 m + tile-MCC per proposer
    band, overall best operating point, then a 50 m re-score of the best set.

    Args:
        cell: registry entry (label/proposer/verifier metadata).
        table: joined candidate table from :func:`build_table`.
        gdf_ref: curator ground truth (EPSG:32635), loaded once.
        gdf_bounds: 384 px evaluation bounds (EPSG:32635), loaded once.

    Returns:
        Result dict for the JSON output (per-band bests, best op at 20 m,
        and the best set re-scored at 50 m).
    """
    by_cid = {r["cid"]: r for r in table}
    max_pk = max(r["vote_count"] for r in table)
    print(f"\n=== {cell['label']}: {len(table)} candidates, "
          f"proposer votes 1..{max_pk} ===", flush=True)

    def gdf_for(cids: frozenset[int]) -> gpd.GeoDataFrame:
        sel = [by_cid[c] for c in sorted(cids)]
        return gpd.GeoDataFrame(
            {"geometry": [Point(r["x"], r["y"]) for r in sel],
             "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)

    best: dict = {"f1": -1.0}
    per_band = []
    for pk in range(1, max_pk + 1):
        bpk: dict = {"f1": -1.0}
        for pt in PROB_TS:
            cids = accepted_cids(table, pk, "mean", pt)
            if not cids:
                continue
            res = score_detection_set(gdf_for(cids), gdf_ref, gdf_bounds,
                                      buffer_metres=20, compute_mcc=True)
            if res["f1"] > bpk["f1"]:
                bpk = {"f1": res["f1"], "mcc": res["mcc"],
                       "precision": res["precision"], "recall": res["recall"],
                       "pt": pt, "n": len(cids), "cids": cids}
        if bpk["f1"] < 0:
            continue
        mcc = f"{bpk['mcc']:.3f}" if bpk.get("mcc") is not None else "NA"
        print(f"  {pk}of{max_pk}: bestF1={bpk['f1']:.4f}  MCC={mcc}  "
              f"prob_t={bpk['pt']}  n={bpk['n']}", flush=True)
        per_band.append({"proposer_k": pk, "f1_20m": round(bpk["f1"], 4),
                         "mcc": round(bpk["mcc"], 4) if bpk["mcc"] is not None else None,
                         "prob_t": bpk["pt"], "n_accepted": bpk["n"]})
        if bpk["f1"] > best["f1"]:
            best = {**bpk, "pk": pk, "max_pk": max_pk}

    # Re-score the best operating point at the shared 50 m operational buffer.
    res50 = score_detection_set(gdf_for(best["cids"]), gdf_ref, gdf_bounds,
                                buffer_metres=50, compute_mcc=False)
    print(f"  >>> BEST {cell['label']}: F1@20m={best['f1']:.4f} "
          f"MCC={best['mcc']:.4f} at {best['pk']}of{best['max_pk']}/"
          f"pt{best['pt']} (n={best['n']}) | F1@50m={res50['f1']:.4f} "
          f"(P={res50['precision']:.4f} R={res50['recall']:.4f})", flush=True)

    return {
        "label": cell["label"],
        "proposer": cell["proposer"],
        "verifier": cell["verifier"],
        "manifest": str((CROPS / cell["manifest"] / "candidate_manifest.json")
                        .relative_to(BASE_DIR)),
        "probabilities": str((VERIFIED / cell["probs"] / "probabilities.json")
                             .relative_to(BASE_DIR)),
        "note": cell["note"],
        "n_candidates": len(table),
        "max_proposer_k": max_pk,
        "per_band_best": per_band,
        "best_op": f"{best['pk']}of{best['max_pk']}/pt{best['pt']}",
        "f1_20m": round(best["f1"], 4),
        "mcc": round(best["mcc"], 4) if best["mcc"] is not None else None,
        "precision_20m": round(best["precision"], 4),
        "recall_20m": round(best["recall"], 4),
        "n_accepted": best["n"],
        "f1_50m": round(res50["f1"], 4),
        "precision_50m": round(res50["precision"], 4),
        "recall_50m": round(res50["recall"], 4),
    }


def main() -> int:
    """Classify all in-scope pool dirs, sweep the unswept cells, write JSON."""
    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS_BY_SIZE[384])  # all unswept cells are 384 px

    band_dirs = classify_band_dirs()
    n_dirs = sum(1 for d in VERIFIED.iterdir() if d.is_dir()) + len(VR_SWEPT)
    print(f"in scope: {n_dirs} dirs | already swept: "
          f"{len(ALREADY_SWEPT) + len(VR_SWEPT)} | duplicate-format: "
          f"{len(DUPLICATE_FORMAT)} | band (draw-replicate/derived): "
          f"{len(band_dirs)} | unswept cells to sweep: {len(CELLS)}", flush=True)

    results = []
    for cell in CELLS:
        table = build_table(cell)
        n_probs = len(json.loads(
            (VERIFIED / cell["probs"] / "probabilities.json").read_text())["results"])
        if not table:
            print(f"\n!!! {cell['label']}: EMPTY JOIN — skipped", flush=True)
            results.append({"label": cell["label"], "error": "empty join",
                            "n_probabilities": n_probs})
            continue
        if len(table) != n_probs:
            print(f"  NOTE: joined {len(table)}/{n_probs} probability entries",
                  flush=True)
        results.append(sweep_cell(cell, table, gdf_ref, gdf_bounds))

    out = {
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scope": {
            "roots": ["outputs/h11/pv-diag-384/verified",
                      "outputs/verifier-robustness/*/T*/verified"],
            "ground_truth": str(GROUND_TRUTH.relative_to(BASE_DIR)),
            "bounds": str(BOUNDS_BY_SIZE[384].relative_to(BASE_DIR)),
            "corpus": "GS 384 px / 487 tiles / curator GT",
        },
        "method": {
            "sweep": "proposer-k x prob_t {0.05..0.5}, rule 'mean' (n=1 verifier)",
            "scorer": "scripts.lib_advanced_metrics.score_detection_set "
                      "(buffer 20 m, tile-MCC); best op re-scored at 50 m",
            "mirrors": "scripts/score_min_thinking_pv.py",
        },
        "classification": {
            "total_dirs_in_scope": n_dirs,
            "already_swept_pv_diag": ALREADY_SWEPT,
            "already_swept_verifier_robustness": VR_SWEPT,
            "duplicate_format_dirs": DUPLICATE_FORMAT,
            "band_dirs_not_swept": band_dirs,
            "counts": {
                "already_swept": len(ALREADY_SWEPT) + len(VR_SWEPT),
                "duplicate_format": len(DUPLICATE_FORMAT),
                "band_draw_replicates": len(band_dirs),
                "unswept_swept_now": len(CELLS),
            },
        },
        "cells": results,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nWrote {OUT_JSON.relative_to(BASE_DIR)}", flush=True)

    print("\n=== summary (F1@20m | MCC | F1@50m, GS 384/487, curator GT) ===",
          flush=True)
    for r in results:
        if "error" in r:
            print(f"  {r['label']:45s} SKIPPED ({r['error']})", flush=True)
            continue
        print(f"  {r['label']:45s} {r['f1_20m']:.4f} | "
              f"{r['mcc'] if r['mcc'] is not None else 'NA'} | "
              f"{r['f1_50m']:.4f}  ({r['best_op']}, n={r['n_accepted']})", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
