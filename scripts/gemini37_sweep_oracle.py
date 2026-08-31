#!/usr/bin/env python3
"""
Gemini 3.7 55-map campaign: sweeps, oracles, and the paired 2x2 family.

Answers the PI's queued oracle question for the 3.7 deployment campaign
(`planning/gemini37-55map-2026-08-29.md` § 4c; queued 2026-08-31): the
full (prob_t x min_votes) corrected-F1 @ 50 m sweep for each campaign
cell, the deployment oracle per cell, and — pointedly — whether arm 2's
carried point (0.80, k5) hit its 55-map oracle exactly ("if so, that's
a story worth telling").

Cells (the proposer-model x verifier-model 2x2, plus the committed
Gemini-3 incumbents from the final board):

- ``arm1``  — 3.7 proposer + carried Gemini-3 verifier, K=5 union
  (12,715), carried point (0.10, k5).
- ``arm2``  — all-3.7 stack, same union, carried point (0.80, k5).
- ``fourth`` — Gemini-3 Run B K=10 union (57,482) under the 3.7
  verifier, carried point (0.98, k10) — the fourth grid cell.
- Incumbents (not swept here; committed final-board sets): B-N5-carried
  (Gemini-3, K=5 first-N, (0.15, k5), 0.8502) and B-N10-carried
  (Gemini-3, K=10, (0.15, k10), 0.8422).

Paired per-sheet sign-swap permutation (10,000, seed 42) at the carried
points over the declared five-test family — the four 2x2 edges plus the
all-3.7 vs incumbent diagonal — with Benjamini-Hochberg FDR at q = 0.05
across the family. Prediction verdicts D1/D6/D7 read from these tests
(`planning/gemini37-55map-2026-08-29.md` § 2, § 4c).

REPLICATION GATES (nothing is written unless every processed cell
passes): the sweep's value at each cell's carried point must equal the
engine's committed primary evaluation @ 50 m to 1e-6; each incumbent's
per-map recomputation must match its final-board F1@50 to 1e-4 (the
board publishes 4 d.p.).

Usage::

    python scripts/gemini37_sweep_oracle.py               # all cells
    python scripts/gemini37_sweep_oracle.py --cells arm1,arm2

Zero API. Run on sapphire (~500 sweep points x 55 Hungarian problems).

Created: 2026-08-31 (Session 145)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv as csvmod
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.compute_corrected_f1_multi_buffer import (  # noqa: E402
    DEFAULT_CRS,
    build_extended_gt,
    build_phantom_gdf,
    compute_counts_at_r,
    compute_point_estimate,
)
from scripts.stride55_score import (  # noqa: E402
    assign_standard_tile,
    build_map_constrained_index,
)
from scripts.stride55_sweep_oracle import (  # noqa: E402
    BOUNDS,
    BUFFER_R,
    CANONICAL_REVIEW,
    STUDENT_GT,
    f1_from_map_counts,
    paired_permutation,
    per_map_counts,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

OUT_DIR = PROJECT_ROOT / "results/gemini37-55map-2026-08-31/sweeps"
BOARD = PROJECT_ROOT / "results/55map-final-board-2026-08-27"
BH_Q = 0.05

#: Campaign cells: verifier root, cell directory, verify subdirectory,
#: expected union size, committed carried point, vote ceiling, and the
#: committed primary evaluation the replication gate reads.
CELLS: dict[str, dict] = {
    "arm1": {
        "vroot": PROJECT_ROOT / "outputs/gemini37-55map-2026-08-29/verifier",
        "cell": "g384_ov192_55map_g37",
        "verify_dir": "verify_arm1",
        "union_n": 12715,
        "carried": (0.10, 5),
        "k_max": 5,
        "committed": PROJECT_ROOT / "results/gemini37-55map-2026-08-31"
                     "/arm1/g384_ov192_55map_g37/primary/eval/corrected-f1.csv",
        "role": "3.7 proposer + carried Gemini-3 verifier",
    },
    "arm2": {
        "vroot": PROJECT_ROOT / "outputs/gemini37-55map-2026-08-29/verifier",
        "cell": "g384_ov192_55map_g37",
        "verify_dir": "verify_arm2",
        "union_n": 12715,
        "carried": (0.80, 5),
        "k_max": 5,
        "committed": PROJECT_ROOT / "results/gemini37-55map-2026-08-31"
                     "/arm2/g384_ov192_55map_g37/primary/eval/corrected-f1.csv",
        "role": "all-3.7 stack (3.7 proposer + 3.7 verifier)",
    },
    "fourth": {
        "vroot": PROJECT_ROOT / "outputs/stride-55map-2026-08-25/verifier",
        "cell": "g384_ov192_55map",
        "verify_dir": "verify_37",
        "union_n": 57482,
        "carried": (0.98, 10),
        "k_max": 10,
        "committed": PROJECT_ROOT / "results/gemini37-fourth-cell/55map"
                     "/g384_ov192_55map/primary/eval/corrected-f1.csv",
        "role": "Gemini-3 Run B K=10 union + 3.7 verifier",
    },
}

#: Final-board incumbent cells (committed detection sets, Gemini-3
#: proposer + carried Gemini-3 verifier) and their published F1@50.
INCUMBENTS: dict[str, dict] = {
    "BN5": {"dir": BOARD / "cells/B-N5-carried", "f1_50": None},
    "BN10": {"dir": BOARD / "cells/B-N10-carried", "f1_50": None},
}

#: The declared paired family at the carried points: the four 2x2 edges
#: plus the diagonal. (test, minuend, subtrahend, requires-fourth).
PAIRED_FAMILY: list[tuple[str, str, str, bool]] = [
    ("D1_proposer_under_G3vf__arm1_vs_BN5", "arm1", "BN5", False),
    ("D6_verifier_under_37prop__arm2_vs_arm1", "arm2", "arm1", False),
    ("headline_diagonal__arm2_vs_BN5", "arm2", "BN5", False),
    ("verifier_under_G3prop__fourth_vs_BN10", "fourth", "BN10", True),
    ("proposer_under_37vf__arm2_vs_fourth", "arm2", "fourth", True),
]


def load_board_f1(spec: dict) -> float:
    """Published F1@50 for a final-board cell (evaluation.json, 4 d.p.)."""
    payload = json.loads((spec["dir"] / "evaluation.json").read_text())
    for buf in payload["summary"]["buffers"]:
        if int(buf["buffer_metres"]) == BUFFER_R:
            return float(buf["f1"])
    raise RuntimeError(f"{spec['dir'].name}: no {BUFFER_R} m buffer row")


def load_candidates(tag: str, spec: dict) -> gpd.GeoDataFrame:
    """Full candidate set with probabilities and standard-grid tiles.

    Mirrors `stride55_sweep_oracle.load_candidates` with the verifier
    root and verify subdirectory parameterised, so the same loading
    chain serves the 3.7 arms and the fourth grid cell.
    """
    vdir = spec["vroot"] / spec["cell"]
    manifest = json.loads(
        (vdir / "crops" / "candidate_manifest.json").read_text())
    results = json.loads(
        (vdir / spec["verify_dir"] / "probabilities.json").read_text())["results"]
    cands = manifest["candidates"]
    if len(cands) != spec["union_n"] or len(results) != spec["union_n"]:
        raise RuntimeError(
            f"{tag}: count gate failed — manifest {len(cands)}, "
            f"results {len(results)}, expected {spec['union_n']}")
    if set(results) != {f"candidate_{i:05d}" for i in range(spec["union_n"])}:
        raise RuntimeError(f"{tag}: key gate failed")
    index = build_map_constrained_index()
    tiles = [assign_standard_tile(index, c["source_tile"],
                                  c["centroid_x"], c["centroid_y"])
             for c in cands]
    gdf = gpd.GeoDataFrame(
        {
            "candidate_id": [c["candidate_id"] for c in cands],
            "vote_count": [c.get("properties", {}).get("vote_count", 0)
                           for c in cands],
            "mound_probability": [
                float(results[f"candidate_{c['candidate_id']:05d}"]
                      ["mound_probability"]) for c in cands],
            "source_tile": tiles,
        },
        geometry=gpd.points_from_xy([c["centroid_x"] for c in cands],
                                    [c["centroid_y"] for c in cands]),
        crs=DEFAULT_CRS)
    return gdf


def committed_f1_at_50(csv_path: Path) -> float:
    """The engine's committed corrected-F1 @ 50 m for a campaign cell."""
    with csv_path.open() as fh:
        for row in csvmod.DictReader(fh):
            if int(row["R_m"]) == BUFFER_R:
                return float(row["F1"])
    raise RuntimeError(f"{csv_path}: no R_m={BUFFER_R} row")


def benjamini_hochberg(pvals: dict[str, float], q: float) -> dict[str, bool]:
    """Standard BH step-up over the family; True = significant at q."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    cutoff = 0
    for i, (_, p) in enumerate(items, start=1):
        if p <= q * i / m:
            cutoff = i
    return {name: (rank <= cutoff)
            for rank, (name, _) in enumerate(items, start=1)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--cells", default="arm1,arm2,fourth",
                    help="comma-separated subset of: " + ",".join(CELLS))
    args = ap.parse_args()
    tags = [t.strip() for t in args.cells.split(",") if t.strip()]
    unknown = set(tags) - set(CELLS)
    if unknown:
        raise SystemExit(f"unknown cells: {sorted(unknown)}")

    import pandas as pd  # local import keeps module surface minimal

    student = gpd.read_file(STUDENT_GT).to_crs(DEFAULT_CRS)
    bounds = gpd.read_file(BOUNDS).to_crs(DEFAULT_CRS)
    empty_y = pd.DataFrame(columns=[
        "candidate_id", "human_label", "buffer_metres", "x", "y", "map_name"])
    review_t = pd.read_csv(CANONICAL_REVIEW)
    phantoms = build_phantom_gdf(empty_y, review_t, BUFFER_R)
    ext_gt = build_extended_gt(student, phantoms)
    logger.info("extended GT at %dm: %d (student %d + phantoms %d, deduped)",
                BUFFER_R, len(ext_gt), len(student), len(phantoms))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload: dict = {"buffer_m": BUFFER_R, "cells_processed": tags,
                     "runs": {}, "incumbents": {}}
    map_counts_at: dict[str, dict] = {}

    # Incumbents: committed final-board sets, gated against the board.
    for name, spec in INCUMBENTS.items():
        det = gpd.read_file(spec["dir"] / "detections.geojson").to_crs(DEFAULT_CRS)
        counts = per_map_counts(det, ext_gt, bounds)
        f1 = f1_from_map_counts(counts)
        board_f1 = load_board_f1(spec)
        if abs(f1 - board_f1) > 1e-4:
            raise RuntimeError(
                f"{name}: incumbent gate FAILED — per-map {f1:.6f} vs "
                f"board {board_f1:.4f}")
        logger.info("%s: incumbent gate OK (per-map %.6f vs board %.4f)",
                    name, f1, board_f1)
        map_counts_at[name] = counts
        payload["incumbents"][name] = {
            "source": str(spec["dir"].relative_to(PROJECT_ROOT)),
            "f1_per_map": f1, "f1_board": board_f1, "n_detections": len(det)}

    for tag in tags:
        spec = CELLS[tag]
        gdf = load_candidates(tag, spec)
        thresholds = sorted({0.0} | {round(float(v), 4)
                                     for v in gdf["mound_probability"]})
        rows = []
        for prob_t in thresholds:
            for k in range(1, spec["k_max"] + 1):
                sub = gdf[(gdf["mound_probability"] >= prob_t)
                          & (gdf["vote_count"] >= k)]
                tp, fp, fn, _ = compute_counts_at_r(sub, ext_gt, bounds,
                                                    BUFFER_R)
                p, r, f1 = compute_point_estimate(tp, fp, fn)
                rows.append({"cell": tag, "prob_t": prob_t, "min_votes": k,
                             "n_detections": int(len(sub)), "tp": tp,
                             "fp": fp, "fn": fn, "precision": p, "recall": r,
                             "corrected_f1": f1})

        # Replication gate against the engine's committed primary value.
        pt, pk = spec["carried"]
        prim = next(r for r in rows
                    if r["prob_t"] == pt and r["min_votes"] == pk)
        committed = committed_f1_at_50(spec["committed"])
        if abs(prim["corrected_f1"] - committed) > 1e-6:
            raise RuntimeError(
                f"{tag}: replication gate FAILED — sweep carried "
                f"{prim['corrected_f1']:.6f} vs committed {committed:.6f}")
        logger.info("%s: replication gate OK (%.6f)", tag,
                    prim["corrected_f1"])

        best = max(rows, key=lambda r: r["corrected_f1"])
        ties = [r for r in rows
                if abs(r["corrected_f1"] - best["corrected_f1"]) < 1e-12]
        carried_is_oracle = any(
            t["prob_t"] == pt and t["min_votes"] == pk for t in ties)
        logger.info(
            "%s: CARRIED %.4f at (%.2f, k%d) | ORACLE %.4f at (%.2f, k%d)%s "
            "| transfer gap %+.4f | carried==oracle: %s",
            tag, prim["corrected_f1"], pt, pk, best["corrected_f1"],
            best["prob_t"], best["min_votes"],
            f" (+{len(ties) - 1} tied)" if len(ties) > 1 else "",
            best["corrected_f1"] - prim["corrected_f1"], carried_is_oracle)
        payload["runs"][tag] = {
            "role": spec["role"], "carried_point": [pt, pk],
            "carried": prim, "oracle": best,
            "oracle_ties": [[t["prob_t"], t["min_votes"]] for t in ties],
            "carried_hit_oracle_exactly": carried_is_oracle,
            "transfer_gap": best["corrected_f1"] - prim["corrected_f1"],
            "n_sweep_rows": len(rows)}

        out_csv = OUT_DIR / f"sweep_{tag}_50m.csv"
        with out_csv.open("w", newline="") as fh:
            w = csvmod.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

        sub = gdf[(gdf["mound_probability"] >= pt) & (gdf["vote_count"] >= pk)]
        counts = per_map_counts(sub, ext_gt, bounds)
        # Consistency note: the paired instrument must agree with the sweep.
        gap = abs(f1_from_map_counts(counts) - prim["corrected_f1"])
        if gap > 1e-6:
            raise RuntimeError(f"{tag}: per-map vs sweep mismatch {gap:.2e}")
        map_counts_at[tag] = counts

    # Paired per-sheet permutation family + BH across whatever ran.
    payload["paired"] = {}
    for test, a, b, needs_fourth in PAIRED_FAMILY:
        if needs_fourth and "fourth" not in tags:
            continue
        res = paired_permutation(map_counts_at[a], map_counts_at[b])
        res["convention"] = f"delta = {a} - {b}, corrected-F1@{BUFFER_R}m"
        payload["paired"][test] = res
        logger.info("%s: dF1=%+.4f p=%.4f", test,
                    res["delta_f1"], res["p_two_sided"])
    sig = benjamini_hochberg(
        {t: r["p_two_sided"] for t, r in payload["paired"].items()}, BH_Q)
    for test in payload["paired"]:
        payload["paired"][test]["bh_significant_q05"] = sig[test]
    payload["bh"] = {"q": BH_Q, "family_size": len(payload["paired"]),
                     "note": ("family = the declared five tests; a subset "
                              "run (arms-only preview) adjusts over the "
                              "subset and is superseded by the full run")}

    (OUT_DIR / "sweep_oracle.json").write_text(
        json.dumps(payload, indent=2) + "\n")
    logger.info("CAMPAIGN SWEEP-ORACLE COMPLETE -> %s",
                OUT_DIR.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
