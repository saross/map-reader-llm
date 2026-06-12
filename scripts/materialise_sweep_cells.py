#!/usr/bin/env python3
# ============================================================================
# materialise_sweep_cells.py
# ----------------------------------------------------------------------------
# Session 113 ($0): materialise best-operating-point detection sets for the
# 16 promotable completeness-sweep cells (Shawn, 2026-06-12: "make
# everything that can be first-class first-class"). Cells 1-2 of the sweep
# are excluded: #1's optimum IS the registered headline condition
# (verified-adv-text-consensus-16of30 — promotion would duplicate it) and
# #2 (the Pro-verifier cell) was minted earlier this session.
#
# Driven directly by the committed sweep record
# (results/verifier-robustness/unswept_pools_sweep.json): each cell's
# (k, prob_t) is parsed from its best_op and the selection is gated on
# exact reproduction of the recorded n_accepted (the Session-77
# feature-count rule applied at materialisation time). Selection rule
# accepted_cids(table, k, "mean", prob_t) — the rule the sweep used.
#
# Usage:  .venv/bin/python scripts/materialise_sweep_cells.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-12 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from scripts.analyse_verifier_robustness import (  # noqa: E402
    EVAL_CRS,
    accepted_cids,
    load_candidate_table,
)

SWEEP = BASE_DIR / "results/verifier-robustness/unswept_pools_sweep.json"
OUT_DIR = BASE_DIR / "results/verifier-robustness/sweep-sets"

# sweep-cell label -> condition label (the geojson slug). The first two
# sweep cells are deliberately absent (see header).
CONDITION_LABELS: dict[str, str] = {
    "image-min-t07-5pass + flash-min vf": "verified-adv-image-min-3of5",
    "image-min-t07-10pass + flash-min vf": "verified-adv-image-min-6of10",
    "image-min-t00-baseline + flash-min vf": "verified-adv-image-baseline",
    "image-min-t00-baseline + flash-med vf":
        "verified-adv-image-baseline-medium-vf",
    "image-min-t00-baseline + pro vf": "verified-adv-image-baseline-pro-vf",
    "text-min-t00-baseline + flash-min vf": "verified-adv-text-baseline",
    "text-min-t00-baseline + flash-med vf":
        "verified-adv-text-baseline-medium-vf",
    "text-min-t00-baseline + pro vf": "verified-adv-text-baseline-pro-vf",
    "pro-high-text-5pass + flash-med vf":
        "verified-adv-pro-text-medium-vf-3of5",
    "pro-high-image-5pass + pro vf": "verified-adv-pro-image-pro-vf-3of5",
    "pro-med-text-baseline + flash-min vf": "verified-adv-pro-text-baseline",
    "pro-med-text-baseline + flash-med vf":
        "verified-adv-pro-text-baseline-medium-vf",
    "pro-med-text-baseline + pro vf": "verified-adv-pro-text-baseline-pro-vf",
    "pro-med-image-baseline + flash-min vf": "verified-adv-pro-image-baseline",
    "pro-med-image-baseline + flash-med vf":
        "verified-adv-pro-image-baseline-medium-vf",
    "pro-med-image-baseline + pro vf": "verified-adv-pro-image-baseline-pro-vf",
}


def main() -> int:
    """Materialise each promotable cell's best-op set, gating n exactly."""
    cells = json.loads(SWEEP.read_text())["cells"]
    by_label = {c["label"]: c for c in cells}
    missing = set(CONDITION_LABELS) - set(by_label)
    if missing:
        sys.exit(f"sweep cells not found: {sorted(missing)}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for sweep_label, cond_label in CONDITION_LABELS.items():
        cell = by_label[sweep_label]
        m = re.fullmatch(r"(\d+)of\d+/pt([0-9.]+)", cell["best_op"])
        if not m:
            sys.exit(f"cannot parse best_op {cell['best_op']!r} ({sweep_label})")
        k, prob_t = int(m.group(1)), float(m.group(2))
        table = load_candidate_table(BASE_DIR / cell["manifest"],
                                     BASE_DIR / cell["probabilities"])
        # Single-pass baseline pools carry no vote_count in the manifest;
        # coerce to 1 (the same rule sweep_unswept_pools.py applied, so the
        # gate reproduces the recorded n exactly).
        if table and max(r["vote_count"] for r in table) == 0:
            for r in table:
                r["vote_count"] = 1
        by_cid = {r["cid"]: r for r in table}
        sel = [by_cid[c] for c in sorted(accepted_cids(table, k, "mean", prob_t))]
        if len(sel) != cell["n_accepted"]:
            sys.exit(f"GATE FAIL {cond_label}: n={len(sel)} != recorded "
                     f"{cell['n_accepted']} ({cell['best_op']})")
        gdf = gpd.GeoDataFrame(
            {"geometry": [Point(r["x"], r["y"]) for r in sel],
             "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)
        out = OUT_DIR / f"{cond_label}.geojson"
        gdf.to_crs("EPSG:4326").to_file(out, driver="GeoJSON")
        print(f"  {cond_label}: n={len(sel)} ({cell['best_op']}, gate ok)",
              flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
