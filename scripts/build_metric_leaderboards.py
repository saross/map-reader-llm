#!/usr/bin/env python3
# ============================================================================
# build_metric_leaderboards.py
# ----------------------------------------------------------------------------
# Session 112 ($0): metric-led leaderboards (Shawn: "there are circumstances
# where one of these metrics needs to be emphasised") — MCC-led, precision-
# led, and recall-led rankings for (a) the GS Era-2 PV/consensus family at
# the 30 m characterisation precision and (b) the 55-map canonical-GT cells
# at the 50 m operational buffer.
#
# Degenerate-trade-off FLAGS (markers, not exclusions, per Shawn):
#   P!  precision < 0.5 at the cell's operating point
#   R!  recall    < 0.5
#   ~   imbalance: min(P,R)/max(P,R) < 0.6
#
# Rankings carry the evaluations' bootstrap CIs. Statistical TIERING remains
# F1-led (the per-architecture and 55-map boards); alternate-metric
# permutation tiering is available on demand (same tile-swap machinery with
# a micro-P / micro-R statistic) but is not run here.
#
# Usage:  .venv/bin/python scripts/build_metric_leaderboards.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VR = BASE_DIR / "results/verifier-robustness/evals"
F35 = BASE_DIR / "results/flash35-2x2/evals"
M55 = BASE_DIR / "results/55maps-extended-gt-2026-06-07"
OUT_DIR = BASE_DIR / "results/metric-leaderboards"

GS_CELLS = {
    "headline31 (30-prop+1vf)": "results/era1-pv-stage-d/384-consensus-text-high/evaluation.json",
    "opmax35 (30-prop+5vf)": f"{VR.relative_to(BASE_DIR)}/verified-384-16of30-t0-3-n5-opmax/evaluation.json",
    "min11 (10-MIN-prop+1vf)": f"{F35.relative_to(BASE_DIR)}/min11/evaluation.json",
    "min6-true (5-MIN-prop+1vf)": f"{F35.relative_to(BASE_DIR)}/min6-true/evaluation.json",
    "min6-n30lineage": f"{F35.relative_to(BASE_DIR)}/min6-n30lineage/evaluation.json",
    "high6 (5-HIGH-prop+1vf)": f"{VR.relative_to(BASE_DIR)}/verified-adv-text-4of5/evaluation.json",
    "high11 (10-HIGH-prop+1vf)": f"{VR.relative_to(BASE_DIR)}/verified-adv-text-6of10/evaluation.json",
    "matrix-minT0.3 (5-HIGH+5vf)": f"{VR.relative_to(BASE_DIR)}/verified-384-ge3of5-t0-3-n5/evaluation.json",
    "matrix-highT0.3": f"{VR.relative_to(BASE_DIR)}/verified-384-ge3of5-t0-3-high-n5/evaluation.json",
    "matrix-minT0.7": f"{VR.relative_to(BASE_DIR)}/verified-384-ge3of5-t0-7-n5/evaluation.json",
    "matrix-highT0.7": f"{VR.relative_to(BASE_DIR)}/verified-384-ge3of5-t0-7-high-n5/evaluation.json",
    "union-T0.0-N5 (384)": f"{VR.relative_to(BASE_DIR)}/verified-384-union-t0-0-n5/evaluation.json",
    "high-vf-n1 (thinking prior)": f"{VR.relative_to(BASE_DIR)}/verified-adv-text-high-vf-4of5/evaluation.json",
    "medium-vf-n1": f"{VR.relative_to(BASE_DIR)}/verified-adv-text-medium-vf-4of5/evaluation.json",
    "pro-prop+flash-vf (3of5)": f"{VR.relative_to(BASE_DIR)}/verified-adv-pro-text-flash-vf-3of5/evaluation.json",
    "pro-prop+pro-vf (3of5)": f"{VR.relative_to(BASE_DIR)}/verified-adv-pro-text-pro-vf-3of5/evaluation.json",
    "f35prop+f3vf (4of10)": f"{F35.relative_to(BASE_DIR)}/f35prop-f3vf-n10-4of10-pt0.15/evaluation.json",
    "f35prop+f35vf (4of10)": f"{F35.relative_to(BASE_DIR)}/f35prop-f35vf-n10-4of10-pt0.25/evaluation.json",
    "f3prop+f35vf (6of10)": f"{F35.relative_to(BASE_DIR)}/f3prop-f35vf-n10-6of10-pt0.25/evaluation.json",
    "f35prop-bare (10of10)": f"{F35.relative_to(BASE_DIR)}/f35prop-bare-n10-10of10/evaluation.json",
}

# Cells promoted to first-class on 2026-06-12 (the unswept-pools sweep
# promotion, commit a70198c6a; disposition in Obs 366 § 5) plus the
# Session-113 registrations (Run A T0.3 GS cell, the image-PV cells, the
# Pro-verifier-over-Flash-pool cells). Labelled by their pv-diag-384
# condition IDs — see results/conditions-manifest.md for each cell's
# composition. Added to the board 2026-06-13 (Session 114 currency sweep).
PROMOTED_GS_CELLS = [
    "verified-adv-text-t03-4of5",
    "verified-adv-text-pro-vf-4of5",
    "verified-adv-text-baseline",
    "verified-adv-text-baseline-medium-vf",
    "verified-adv-text-baseline-pro-vf",
    "verified-adv-image-3of5",
    "verified-adv-image-min-3of5",
    "verified-adv-image-min-6of10",
    "verified-adv-image-baseline",
    "verified-adv-image-baseline-medium-vf",
    "verified-adv-image-baseline-pro-vf",
    "verified-adv-pro-text-medium-vf-3of5",
    "verified-adv-pro-text-baseline",
    "verified-adv-pro-text-baseline-medium-vf",
    "verified-adv-pro-text-baseline-pro-vf",
    "verified-adv-pro-image-pro-vf-3of5",
    "verified-adv-pro-image-baseline",
    "verified-adv-pro-image-baseline-medium-vf",
    "verified-adv-pro-image-baseline-pro-vf",
]
for _cid in PROMOTED_GS_CELLS:
    GS_CELLS[_cid] = f"{VR.relative_to(BASE_DIR)}/{_cid}/evaluation.json"

M55_CELLS = {
    "T03-k3 (oracle)": "T03-k3", "T03-k4": "T03-k4", "TH7-k3": "TH7-k3",
    "TH7-k4 (carry-forward)": "TH7-k4", "TM-k3": "TM-k3", "TM-k4": "TM-k4",
    "IM-k3": "IM-k3",
    # The Run-B min11 uplift cell (added to the canonical board in S113).
    "TM-n10-k5 (uplift)": "TM-n10-k5",
}

# min11 (text-n10 MINIMAL pool) and high11 (flash-high HIGH pool,
# the registered verified-adv-text-6of10) are DISTINCT cells.
DROP: set[str] = set()


def load_cell(path: Path, buffer_m: int) -> dict | None:
    """Pull P/R/F1 (+CIs) at the buffer and the tile MCC from one eval."""
    s = json.loads(path.read_text())["summary"]
    row = next((b for b in s["buffers"] if b["buffer_metres"] == buffer_m), None)
    if row is None:
        return None
    mcc = s.get("tile_classification", {}).get("mcc")
    if isinstance(mcc, dict):
        mcc_ci = [mcc.get("ci_lower"), mcc.get("ci_upper")]
        mcc = mcc.get("point")
    else:
        mcc_ci = [None, None]
    return {"f1": row["f1"], "p": row["precision"], "r": row["recall"],
            "p_ci": [row.get("p_ci_lower"), row.get("p_ci_upper")],
            "r_ci": [row.get("r_ci_lower"), row.get("r_ci_upper")],
            "mcc": mcc, "mcc_ci": mcc_ci, "n": s["n_detections"]}


def flags(c: dict) -> str:
    """Degenerate-trade-off markers (flag, never exclude)."""
    out = []
    if c["p"] < 0.5:
        out.append("P!")
    if c["r"] < 0.5:
        out.append("R!")
    if min(c["p"], c["r"]) / max(c["p"], c["r"]) < 0.6:
        out.append("~")
    return "".join(out) or "—"


def board(cells: dict[str, dict], metric: str, buffer_m: int) -> list[str]:
    """One metric-led table (markdown lines)."""
    key = {"MCC": "mcc", "precision": "p", "recall": "r"}[metric]
    ci_key = {"mcc": "mcc_ci", "p": "p_ci", "r": "r_ci"}[key]
    lines = [f"\n## {metric}-led ranking\n",
             f"| rank | cell | {metric} | 95% CI | F1@{buffer_m} | P | R | MCC | n | flags |",
             "|---:|---|---:|---|---:|---:|---:|---:|---:|---|"]
    ranked = sorted(cells.items(), key=lambda kv: -(kv[1][key] or 0))
    for i, (name, c) in enumerate(ranked, 1):
        lo, hi = c[ci_key]
        ci = f"[{lo:.3f}, {hi:.3f}]" if lo is not None and hi is not None else "—"
        lines.append(f"| {i} | {name} | {c[key]:.4f} | {ci} | {c['f1']:.4f} "
                     f"| {c['p']:.3f} | {c['r']:.3f} | {c['mcc']:.3f} | {c['n']} "
                     f"| {flags(c)} |")
    return lines


def emit(track: str, cells: dict[str, dict], buffer_m: int) -> None:
    """Write one track's metric boards (md + json)."""
    md = [f"# Metric-led leaderboards — {track} @ {buffer_m} m",
          "",
          "> Rankings with bootstrap CIs from the standard evaluations. "
          "Statistical TIERING remains F1-led (see the per-architecture and "
          "55-map boards); flags: `P!`/`R!` = precision/recall < 0.5, `~` = "
          "min(P,R)/max(P,R) < 0.6. Flags mark, they do not exclude.",
          ">",
          "> **Membership refreshed 2026-06-13** (Session 114): adds the "
          "cells promoted to first-class on 2026-06-12 (unswept-pools "
          "promotion, commit `a70198c6a`) and the S113 registrations; the "
          "55-map track adds the Run-B uplift cell. Promoted cells are "
          "labelled by condition ID (`results/conditions-manifest.md`). "
          "No dollar figures appear here; nothing is audit-affected.",
          ">",
          "> **Statistical tiering on the MCC axis** (55-map track): "
          "`55map-mcc-tiering.{md,json}` — round-robin tile-swap "
          "permutation on the MCC statistic (10k, seed 42) + BH-FDR + "
          "greedy-clique tiers, generated by "
          "`scripts/mcc_tiering_55map.py` (Session 114)."]
    for metric in ("MCC", "precision", "recall"):
        md += board(cells, metric, buffer_m)
    stem = OUT_DIR / f"{track}-{buffer_m}m"
    stem.with_suffix(".md").write_text("\n".join(md) + "\n")
    stem.with_suffix(".json").write_text(json.dumps(
        {"track": track, "buffer_m": buffer_m, "cells": cells}, indent=2) + "\n")
    print(f"wrote {stem.relative_to(BASE_DIR)}.{{md,json}} ({len(cells)} cells)")


def main() -> int:
    """Build both tracks' metric-led boards."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gs = {}
    for name, rel in GS_CELLS.items():
        if name in DROP:
            continue
        c = load_cell(BASE_DIR / rel, 30)
        if c:
            gs[name] = c
    emit("gs-era2-pv-family", gs, 30)

    m55 = {}
    for name, d in M55_CELLS.items():
        c = load_cell(M55 / d / "evaluation.json", 50)
        if c:
            # The manifest adapter drops the engine's BCa MCC CIs; recover
            # them from the Track-2 summary.json (tile_classification.mcc_CI
            # at the 50 m headline) so the MCC-led board carries intervals.
            summary = json.loads((M55 / d / "summary.json").read_text())
            row50 = next(r for r in summary["results"] if r["R_m"] == 50)
            ci = row50["tile_classification"].get("mcc_CI")
            if ci:
                c["mcc_ci"] = [round(ci[0], 4), round(ci[1], 4)]
            m55[name] = c
    emit("55map-canonical", m55, 50)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
