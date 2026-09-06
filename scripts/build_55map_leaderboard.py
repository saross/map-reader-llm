#!/usr/bin/env python3
# ============================================================================
# build_55map_leaderboard.py
# ----------------------------------------------------------------------------
# Session 112: the 55-map generalisation leaderboard at the canonical 50 m
# working buffer (Shawn-approved 2026-06-11; derivation:
# results/working-precision/55maps-csr-noise-floor.json — observed gains die
# at 50 m, CSR chance-matching negligible, attribution ambiguity rises
# steeply beyond).
#
# CELLS: the seven canonical-GT conditions (the S105 two-reference set) +
# the S113 min11-uplift cell (Run B; manifest run 55maps-text-min-n10-uplift).
# REFERENCE: the canonical adjudicated GT at R=50 — 4,746 reviewed student
# points + the 415 phantoms gated <= 50 m (per-buffer gating per
# build_canonical_gt; phantoms ARE additional GT points for matching).
#
# METHOD (project-canonical): per-tile TP/FP/FN at 50 m (Hungarian per map,
# 8,541-tile order) -> full round-robin tile-swap micro-F1 permutation
# tests (10k, seed 42, two-sided) -> BH-FDR q=0.05 -> greedy-clique tiers.
# GATE: each cell's per-tile micro-F1 must reproduce its committed
# evaluation F1@50m within 0.003 (mechanism equivalence check).
#
# COST: $0 (on-disk). Run on zbook (8,541-tile Hungarian x 7 cells).
#
# Usage:
#   .venv/bin/python scripts/build_55map_leaderboard.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))
from scripts.apply_fdr_correction import apply_bh_correction  # noqa: E402
from scripts.compute_corrected_f1_multi_buffer import (  # noqa: E402
    ATTRIBUTION_RESOLUTION_NOTE,
    PAIRED_CI_NOTE_PERCENTILE,
    R2_ATTRIBUTION_NOTE,
    STANDARDISED_ATTRIBUTION_NOTE,
    build_extended_gt,
    load_standardised_extension,
)
from scripts.lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    greedy_clique_tiers,
    micro_f1,
    permutation_test_float,
)
from scripts.pairwise_permutation_test import assign_source_tiles  # noqa: E402

BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
STUDENT_GT = BASE_DIR / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
PHANTOMS = BASE_DIR / "results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv"
STD_DIR = BASE_DIR / "results/deployment-oracle-2026-06-06/canonical-gt/standardised"
STUDENT_STD = STD_DIR / "student-mounds-55maps-standardised.geojson"
EXTENSION_STD = STD_DIR / "extension-mounds-standardised.csv"
R2_REFERENCE = BASE_DIR / "inputs/vectors/references/best-available-gt-55maps-r2.geojson"

#: r2's committed census, read from the file itself (2026-09-06). The loader
#: gates on these so a silently-rebuilt or half-applied reference cannot enter
#: a board: the whole point of a revision is that its size is a stated fact.
R2_EXPECTED_LAYERS = {
    "student_standardised": 4726,
    "extension_standardised": 278,
    "audit_reviewed": 14,
}
R2_EXPECTED_N = 5018

#: The channel-duplicate tolerance the engine applies when it builds the
#: extended GT from layers (``build_extended_gt(dedup_tolerance_m=5.0)``).
#: r2 arrives pre-merged, so :func:`r2_gt` re-asserts the invariant here
#: rather than trusting that it held upstream.
DEDUP_TOLERANCE_M = 5.0

#: Final-board home per reference vintage. The r1 home is READ-ONLY during an
#: r2 build: G3 (final_board_build) and G4 (final_board_sweeps) reproduce the
#: committed r1 board from those files at 1e-9, so a run that rewrote them
#: would destroy its own regression evidence (MAJOR 6 of the r2-chain audit,
#: Session 149 — elevated to a pre-step-3 blocker). Scripts resolve their home
#: through :func:`board_home` rather than a module constant so the vintage is
#: always an explicit argument.
BOARD_HOME_BY_REFERENCE = {
    "standardised": BASE_DIR / "results/55map-final-board-2026-08-27",
    "r2": BASE_DIR / "results/55map-final-board-r2-2026-09-06",
}

RUN_CONDS = BASE_DIR / "results/run-conditions.json"
OUT_DIR = BASE_DIR / "results/55map-leaderboard"
BUFFER_M = 50
GATE_TOL = 0.003

# Short display names for the board cells, keyed by (run_id, label).
# Matches the S105 findings-doc naming. The standardised board (Session
# 132, queue item 5) uses the same display names with the
# `-standardised-gt` condition labels.
NAMES = {
    ("55maps-text-high-t0-3-generalisation", "verified-k3-canonical-gt"): "T03-k3 (oracle)",
    ("55maps-text-high-t0-3-generalisation", "verified-k4-canonical-gt"): "T03-k4",
    ("55maps-text-high-generalisation", "verified-k3-canonical-gt"): "TH7-k3",
    ("55maps-text-high-generalisation", "verified-k4-canonical-gt"): "TH7-k4 (carry-forward)",
    ("55maps-text-min-generalisation", "verified-k3-canonical-gt"): "TM-k3",
    ("55maps-text-min-generalisation", "verified-k4-canonical-gt"): "TM-k4",
    ("55maps-image-generalisation", "verified-k3-canonical-gt"): "IM-k3",
    ("55maps-text-min-n10-uplift", "verified-5of10-canonical-gt"): "TM-n10-k5 (uplift)",
}
NAMES_STANDARDISED = {
    (run, label.replace("-canonical-gt", "-standardised-gt")): name
    for (run, label), name in NAMES.items()
}
#: Reference revision r2 (card `planning/reference-revision-2026-09-06.md`).
#: Same cells, same detections, `-r2-gt` condition rows — written by
#: ``register_standardised_gt_conditions.py --reference r2`` (step 7a), which
#: MUST run before this board: :func:`main` resolves each cell's numbers from
#: its registered ``eval_path``, so the register row is this board's data
#: pointer, not merely its index.
NAMES_R2 = {
    (run, label.replace("-canonical-gt", "-r2-gt")): name
    for (run, label), name in NAMES.items()
}


def canonical_gt_at(r_m: float) -> gpd.GeoDataFrame:
    """The canonical GT at buffer R: reviewed students + phantoms gated <= R.

    Carries ``source_map`` (required by the per-map Hungarian matcher):
    students from their own property, phantoms from the review CSV.
    """
    s = gpd.read_file(STUDENT_GT).to_crs("EPSG:32635")
    pts = list(s.geometry)
    maps = list(s["source_map"])
    with open(PHANTOMS) as fh:
        for row in csv.DictReader(fh):
            if float(row["buffer_metres"]) <= r_m:
                pts.append(Point(float(row["x"]), float(row["y"])))
                maps.append(row["map_name"])
    return gpd.GeoDataFrame({"geometry": pts, "source_map": maps}, crs="EPSG:32635")


def standardised_gt() -> gpd.GeoDataFrame:
    """The ruling-21 standardised reference (buffer-invariant).

    Standardised student layer + the whole 279-record extension layer at
    marked centres — no ring gate (queue items 2–3 semantics), built
    through the engine's :func:`build_extended_gt` so the 5 m
    channel-duplicate audit applies identically to the scoring runs
    (expected drops: 0).
    """
    s = gpd.read_file(STUDENT_STD).to_crs("EPSG:32635")
    ext = load_standardised_extension(EXTENSION_STD, crs="EPSG:32635")
    gdf = build_extended_gt(s, ext)
    if gdf.attrs.get("n_phantom_duplicates_dropped", 0) != 0:
        sys.exit("GATE FAIL: standardised reference dropped extension "
                 "records in de-duplication — layer drift")
    return gdf


def board_home(reference: str = "standardised") -> Path:
    """The final-board results home for one reference vintage.

    Args:
        reference: ``standardised`` (r1, default) or ``r2``.

    Returns:
        The directory that vintage's board artefacts are written to.

    Raises:
        SystemExit: On an unknown vintage. Defaulting to r1 here would let a
            typo silently overwrite the committed board.
    """
    try:
        return BOARD_HOME_BY_REFERENCE[reference]
    except KeyError:
        sys.exit(f"unknown board reference {reference!r}; "
                 f"expected one of {sorted(BOARD_HOME_BY_REFERENCE)}")


def r2_gt() -> gpd.GeoDataFrame:
    """Reference revision r2, loaded from its committed merged artefact.

    r2 enters the chain as ONE file — the same
    ``best-available-gt-55maps-r2.geojson`` that step 3 hands to
    ``evaluate_detections.py --ground-truth``. That is deliberate (PI ruling,
    Session 149, adjudicating MAJOR 5 of the r2-chain audit): the scorer takes
    a single path, so building the board's reference by a *second*, in-process
    route would create two constructions of the same object that could drift
    apart. One file, one construction, no equivalence gate needed.

    What that costs is the engine's own de-duplication pass, which
    :func:`standardised_gt` gets for free by calling ``build_extended_gt``.
    So this function re-asserts the same three invariants directly:

    1. **Census** — total and per-layer counts match the committed revision.
    2. **Channel duplicates** — no two reference points within
       ``DEDUP_TOLERANCE_M``, the tolerance ``build_extended_gt`` enforces.
       Verified on r2 as built: the nearest audit addition sits 68.35 m from
       any existing point (13.7x tolerance), so this gate is a guardrail for
       future revisions rather than a live correction.
    3. **Identity** — ``gt_id`` unique.

    Returns:
        The r2 reference in EPSG:32635, buffer-invariant (every layer is at a
        marked centre or better, so no ring gate applies at any radius).

    Raises:
        SystemExit: On any gate failure. A reference that does not reconcile
            must never reach a board — a wrong instrument silently rescales
            every number downstream.
    """
    gdf = gpd.read_file(R2_REFERENCE).to_crs("EPSG:32635")

    if len(gdf) != R2_EXPECTED_N:
        sys.exit(f"GATE FAIL: r2 reference has {len(gdf)} points, "
                 f"expected {R2_EXPECTED_N}")
    counts = gdf["layer"].value_counts().to_dict()
    if counts != R2_EXPECTED_LAYERS:
        sys.exit(f"GATE FAIL: r2 layer census {counts} != {R2_EXPECTED_LAYERS}")
    if gdf["gt_id"].duplicated().any():
        sys.exit("GATE FAIL: duplicate gt_id in the r2 reference")

    # The 5 m channel-duplicate audit, applied to the merged file. k=2 because
    # every point's nearest neighbour is itself.
    tree = cKDTree(np.c_[gdf.geometry.x, gdf.geometry.y])
    dist, _ = tree.query(np.c_[gdf.geometry.x, gdf.geometry.y], k=2)
    n_close = int((dist[:, 1] < DEDUP_TOLERANCE_M).sum())
    if n_close:
        sys.exit(f"GATE FAIL: {n_close} r2 reference points lie within "
                 f"{DEDUP_TOLERANCE_M} m of another — channel duplicates that "
                 f"build_extended_gt would have dropped")

    print(f"r2 reference: {len(gdf)} points "
          f"({counts['student_standardised']} student + "
          f"{counts['extension_standardised']} extension + "
          f"{counts['audit_reviewed']} audit-reviewed); "
          f"min separation {dist[:, 1].min():.2f} m", flush=True)
    return gdf


def reference_gt(reference: str) -> gpd.GeoDataFrame:
    """Dispatch to the reference a BOARD BUILD is targeting.

    Deliberately NOT used by the G3/G4 regression gates in
    ``final_board_build.py`` / ``final_board_sweeps.py``, which keep calling
    :func:`standardised_gt` directly. "The mechanism still reproduces the
    committed r1 board" is a claim about the *code*, not about the reference
    under test, so those gates must stay pinned to r1 and stay LIVE during an
    r2 build (PI ruling, Session 149, adjudicating BLOCKER 4).

    Args:
        reference: ``canonical``, ``standardised`` or ``r2``.

    Returns:
        The reference frame in EPSG:32635.
    """
    if reference == "r2":
        return r2_gt()
    if reference == "standardised":
        return standardised_gt()
    return canonical_gt_at(BUFFER_M)


def render_md(payload: dict) -> str:
    """Render the F1 board markdown from the results dict (== the committed JSON).

    Split out from the compute path so the citable document can be regenerated
    verbatim — e.g. after a methodological note is revised — without re-running
    the permutation tests. ``main(rebuild_md_only=True)`` uses this against the
    committed ``55map_leaderboard_50m.json``.

    Args:
        payload: The mapping written to ``55map_leaderboard_50m.json``. Must
            carry ``cells`` (F1-descending), ``pairwise`` and ``tiers``.

    Returns:
        The full markdown document as a single string (no trailing newline).

    Example:
        >>> doc = render_md(json.loads(Path("55map_leaderboard_50m.json").read_text()))
        >>> doc.splitlines()[0]
        '# 55-map generalisation leaderboard — canonical GT @ 50 m'
    """
    tier_of = {n: t for t, members in enumerate(payload["tiers"], 1) for n in members}
    pairs = payload["pairwise"]
    n_sig = sum(1 for p in pairs if p["significant"])
    ref = payload.get("reference", "canonical")
    title = "# 55-map generalisation leaderboard — " + {
        "r2": "reference r2 @ 50 m",
        "standardised": "standardised reference @ 50 m",
    }.get(ref, "canonical GT @ 50 m")
    ref_note = {
        "r2": R2_ATTRIBUTION_NOTE,
        "standardised": STANDARDISED_ATTRIBUTION_NOTE,
    }.get(ref, ATTRIBUTION_RESOLUTION_NOTE)
    md = [title,
          "",
          f"> Working buffer 50 m per the noise-floor derivation "
          f"(`results/working-precision/55maps-csr-noise-floor.json`). "
          f"Round-robin tile-swap permutation (10k, seed 42) + BH-FDR q=0.05 "
          f"+ greedy-clique tiers; {n_sig}/{len(pairs)} pairs significant.",
          "",
          "| rank | cell | tier | F1@50 | 95% CI | P@50 | R@50 | tile-MCC | n |",
          "|---:|---|---:|---:|---|---:|---:|---:|---:|"]
    for i, c in enumerate(payload["cells"], 1):
        mcc = f"{c['mcc']:.3f}" if c["mcc"] is not None else "—"
        md.append(f"| {i} | {c['name']} | {tier_of[c['name']]} | {c['f1_50']:.4f} "
                  f"| [{c['ci'][0]:.4f}, {c['ci'][1]:.4f}] | {c['precision_50']:.4f} "
                  f"| {c['recall_50']:.4f} | {mcc} | {c['n_detections']} |")
    # D36: this board's per-cell intervals are the committed evaluations'
    # ``f1_ci_lower`` / ``f1_ci_upper``, which the Track-2 adapters computed
    # by the percentile bootstrap and record as ``"f1_ci_method":
    # "percentile"``. The shared note used to call them BCa.
    md += ["", "## Reading this board", "", PAIRED_CI_NOTE_PERCENTILE, "",
           ref_note]
    return "\n".join(md)


def main(rebuild_md_only: bool = False, reference: str = "canonical") -> int:
    """Build the 50 m board with round-robin tiers.

    Args:
        rebuild_md_only: When True, skip all computation and re-render the
            markdown from the committed JSON. Used to refresh prose in the
            citable document without disturbing any number.
        reference: ``canonical`` (legacy ring-gated pairing, default —
            unchanged behaviour) or ``standardised`` (ruling-21 layers,
            queue item 5; separate output files, `-standardised-gt`
            conditions).
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = {"standardised": "_standardised", "r2": "_r2"}.get(reference, "")
    md_name = f"55map-leaderboard-50m{suffix.replace('_', '-')}.md"
    json_name = f"55map_leaderboard_50m{suffix}.json"

    if rebuild_md_only:
        src = OUT_DIR / json_name
        payload = json.loads(src.read_text())
        (OUT_DIR / md_name).write_text(render_md(payload) + "\n")
        print(f"rebuilt {OUT_DIR.relative_to(BASE_DIR)}/{md_name} "
              f"from {src.name} (no recomputation)", flush=True)
        return 0

    gdf_bounds = gpd.read_file(BOUNDS)
    if gdf_bounds.crs is None:
        gdf_bounds = gdf_bounds.set_crs("EPSG:4326")
    gdf_bounds = gdf_bounds.to_crs("EPSG:32635")
    tile_order = sorted(gdf_bounds["tile_name"].tolist())
    tile_index = {t: i for i, t in enumerate(tile_order)}
    gdf_ref = reference_gt(reference)
    if reference == "canonical":
        print(f"canonical GT at {BUFFER_M} m: {len(gdf_ref)} points; "
              f"{len(tile_order)} tiles", flush=True)
    else:
        print(f"{reference} reference (buffer-invariant): {len(gdf_ref)} "
              f"points; {len(tile_order)} tiles", flush=True)

    dec = json.loads(RUN_CONDS.read_text())["decomposition"]
    names = {"standardised": NAMES_STANDARDISED,
             "r2": NAMES_R2}.get(reference, NAMES)
    cells = []
    for (run_id, label), name in names.items():
        cond = next(
            (c for c in dec[run_id]["conditions"] if c["label"] == label), None)
        if cond is None:
            # The board reads its numbers from the register row's eval_path,
            # so a missing row is a sequencing error, not a data gap: step 7a
            # (register) must precede step 4 (build). Say which row.
            sys.exit(f"MISSING REGISTER ROW: {run_id}::{label} is not in "
                     f"{RUN_CONDS.relative_to(BASE_DIR)}. Run "
                     f"register_standardised_gt_conditions.py "
                     f"--reference {reference} first (step 7a before step 4).")
        det = gpd.read_file(BASE_DIR / cond["detections"])
        crs = "EPSG:32635" if abs(det.geometry.x.iloc[0]) > 180 else "EPSG:4326"
        det = det.set_crs(crs, allow_override=True).to_crs("EPSG:32635")
        det = assign_source_tiles(det, gdf_bounds)
        tm = compute_per_tile_tp_fp_fn(det, gdf_ref, gdf_bounds, buffer_metres=BUFFER_M)
        tp = np.zeros(len(tile_order))
        fp = np.zeros(len(tile_order))
        fn = np.zeros(len(tile_order))
        for _, row in tm.iterrows():
            i = tile_index.get(row["tile_name"])
            if i is not None:
                tp[i], fp[i], fn[i] = float(row["tp"]), float(row["fp"]), float(row["fn"])

        ev = json.loads((BASE_DIR / cond["eval_path"]).read_text())["summary"]
        ev50 = next(b for b in ev["buffers"] if b["buffer_metres"] == BUFFER_M)
        board_f1 = micro_f1(tp.sum(), fp.sum(), fn.sum())
        ok = abs(board_f1 - ev50["f1"]) <= GATE_TOL
        print(f"  {name:<24} board F1@50={board_f1:.4f} eval={ev50['f1']:.4f} "
              f"{'ok' if ok else 'GATE FAIL'}", flush=True)
        if not ok:
            sys.exit(f"GATE FAIL: {name} board {board_f1:.4f} vs eval {ev50['f1']:.4f}")
        cells.append({
            "name": name, "condition_id": f"{run_id}::{label}",
            "f1_50": ev50["f1"], "ci": [ev50["f1_ci_lower"], ev50["f1_ci_upper"]],
            "precision_50": ev50["precision"], "recall_50": ev50["recall"],
            "mcc": (lambda m: m.get("point") if isinstance(m, dict) else m)(
                ev.get("tile_classification", {}).get("mcc")),
            "n_detections": ev["n_detections"],
            "tp": tp, "fp": fp, "fn": fn})

    print(f"\n=== round-robin ({len(cells)} cells, 10k tile-swap, seed 42) ===",
          flush=True)
    pairs, significant = [], {}
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            a, b = cells[i], cells[j]
            r = permutation_test_float(a["tp"], a["fp"], a["fn"],
                                       b["tp"], b["fp"], b["fn"],
                                       n_permutations=10000, seed=42)
            pairs.append({"a": a["name"], "b": b["name"], **r})
    adjusted = apply_bh_correction([p["p_value"] for p in pairs], q=0.05)
    for p, adj in zip(pairs, adjusted):
        p["bh_adjusted_p"] = round(adj, 6)
        p["significant"] = bool(adj < 0.05)
        significant[frozenset({p["a"], p["b"]})] = p["significant"]

    ordered = sorted(cells, key=lambda c: c["f1_50"], reverse=True)
    tiers = greedy_clique_tiers([c["name"] for c in ordered], significant)
    tier_of = {n: t for t, members in enumerate(tiers, 1) for n in members}
    n_sig = sum(1 for p in pairs if p["significant"])
    print(f"{n_sig}/{len(pairs)} pairs significant -> {len(tiers)} tier(s)", flush=True)

    for i, c in enumerate(ordered, 1):
        mcc = f"{c['mcc']:.3f}" if c["mcc"] is not None else "—"
        print(f"{i}. {c['name']:<24} T{tier_of[c['name']]}  F1@50 {c['f1_50']:.4f}  "
              f"MCC {mcc}", flush=True)

    payload = {
        "buffer_m": BUFFER_M, "reference": reference, "tiers": tiers,
        "cells": [{k: v for k, v in c.items() if k not in ("tp", "fp", "fn")}
                  for c in ordered],
        "pairwise": pairs}
    (OUT_DIR / md_name).write_text(render_md(payload) + "\n")
    (OUT_DIR / json_name).write_text(
        json.dumps(payload, indent=2, default=float) + "\n")
    print(f"\nWrote {OUT_DIR.relative_to(BASE_DIR)}/", flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rebuild-md",
        action="store_true",
        help="Re-render the board markdown from the committed JSON without "
             "re-running the permutation tests (prose-only refresh).",
    )
    parser.add_argument(
        "--reference",
        choices=["canonical", "standardised", "r2"],
        default="canonical",
        help="Reference to tier against: canonical (legacy, default), "
             "standardised (ruling 21; writes *_standardised outputs), or "
             "r2 (the 2026-09 audit revision; writes *_r2 outputs and reads "
             "-r2-gt register rows, which step 7a must have written).",
    )
    _args = parser.parse_args()
    raise SystemExit(main(
        rebuild_md_only=_args.rebuild_md, reference=_args.reference,
    ))
