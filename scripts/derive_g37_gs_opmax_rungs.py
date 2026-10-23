#!/usr/bin/env python3
"""
Derive the sweep-optimal point for the committed 3.7 GS screen K=5/K=10 rungs
============================================================================

Description:
    Tier D of the K-ladder Phase 2 gap-fill buys the K = 1 and K = 3 rungs of
    the Gemini 3.7 proposer screened on the gold standard, so that a second
    model family carries a four-rung fixed-parameter ladder. Its committed
    K = 5 and K = 10 rungs, however, are registered at their **carried** point
    only — ``g37-text-k5-verified-carried-p0.10-k5`` and its K = 10 sibling —
    so the family's ``-opmax`` column would stop at K = 3 while the pv-diag-384
    families carry it at all four rungs.

    Those two stages' unions, probabilities and prepared passes are all
    committed, so the sweep-optimal point is reachable at **US$0**. This script
    sweeps each on both 487-tile gold-standard frames, takes the F1@20 argmax on
    the board frame (ruling R2), materialises it, and emits the board-frame
    evaluation job. No API call is made; no register row is written.

    **On the origin route (PR #42, D62 (1); fixed 2026-10-15).** The two
    unions (``union_k5.geojson``, ``union_k10.geojson``) record one legacy
    ``source_tile`` per row and no member list, so a row is scored on that
    tile's sheet unless its members are attached first. The gold-standard
    chain's own loaders do that, and so does this script, exactly as
    ``image_b_analysis.py`` does for these stages:
    ``image_b_analysis.load_image_union`` (the union joined to its leg under
    the leg rule), ``stride_verifier_analysis.reassign_gate``, then
    ``lib_cluster_origins.union_on_origin`` with the cell's prepared passes.
    The board-frame and Era-2 sweeps run in-process on that union with
    ``sweep_f1_greedy_pv.py``'s grid, scorer and row schema, and the argmax is
    materialised from it as ``image_b_analysis.py`` writes its best set.
    Before the fix the sweeps read the crops manifest and the cells were
    materialised from the bare union, so the re-verified wrong-sheet rows of
    D62 (1) scored on the wrong sheet: 0.8984 at (0.10, k5) and (0.10, k10)
    against the origin-routed board cells' 0.9165 and 0.9169
    (``reports/s164-agent-records/restatement-pass.md`` § 1.4).

    Ruling R1 holds without a swap: both committed stages were verified by the
    carried Gemini 3 verifier, not by a 3.7 one (the ``verify_swap37`` and
    ``verify_swap38`` stages beside them are the swaps, and are excluded).

    **Which probabilities (D62 (1) step 2, 2026-10-13).** Both stages' wrong-
    sheet rows were re-verified on crops from their own sheet and booked in
    ``verify_repaired/`` and ``verify_k10_repaired/``. Each stage is read under
    the shared leg rule (``scripts/lib_verify_dirs.py``): the repaired copy by
    default, the fixed-name leg under ``MAP_READER_VERIFY_DIRS=fixed``. The
    directory read is recorded per stage as ``verifier_probabilities``, and the
    carried cross-check is keyed by it (:data:`CARRIED_CROSSCHECK`). On the
    re-verified rows the argmax is the carried point, (0.10, k5) F1@20 0.9165
    (451) and (0.10, k10) 0.9169 (431). On the legs as run the origin route
    reproduces the committed carried cells at (0.10, k = K), 0.9066 (443) and
    0.9068 (423), but its argmax is (0.05, k5) 0.9073 and (0.0, k10) 0.9140:
    the wrong-sheet rows the blind verifier scored at 0.05 or 0 then enter as
    true positives on their own sheet (surprise S2 of
    ``reports/s164-agent-records/rescore-repaired-gs.md``). The committed
    opmax cells, at (0.10, k = K), predate the origin route.

    **Same assessed area (PI ruling D51, 2026-10-07).** These two stages'
    unions were clipped to the grid-common footprint upstream; the family's
    K = 1 and K = 3 rungs were not. Before sweeping, the four rungs' assessed
    areas are compared on the board frame (``scripts/lib_assessed_area.py``),
    and the run REFUSES unless ``--clip-to-common-area`` is given (then the
    sweeps and cells are clipped to the common area, which removes nothing
    from these two stages, and the output names the clip).

Usage::

    python scripts/derive_g37_gs_opmax_rungs.py prepare [--clip-to-common-area]
    xargs -P 4 -I CMD bash -c CMD < \
        results/k-ladder-2026-09-12/phase2/g37-opmax-jobs.txt
    python scripts/derive_g37_gs_opmax_rungs.py collect

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.build_k_ladder_phase2_tables import new_rung_pools  # noqa: E402
from scripts.grid_analysis import load_cell_passes  # noqa: E402
from scripts.grid_verifier_analysis import verified_subset  # noqa: E402
from scripts.image_b_analysis import load_image_union  # noqa: E402
from scripts.lib_advanced_metrics import calculate_f1_internal  # noqa: E402
from scripts.lib_cluster_origins import union_on_origin  # noqa: E402
from scripts.lib_verify_dirs import (  # noqa: E402
    resolve_verify_dir,
    verify_dir_provenance,
)
from scripts.lib_assessed_area import (  # noqa: E402
    COMMON_AREA_CLIP_NAME,
    add_area_gate_arguments,
    clip_geojson_file,
    clip_points_to_area,
    read_area_geojson,
    run_area_gate,
)
from scripts.stride_verifier_analysis import (  # noqa: E402
    COMMON_BOUNDS,
    reassign_gate,
)
from scripts.sweep_f1_greedy_pv import PROB_THRESHOLDS  # noqa: E402
from scripts.sweep_f1_wbf import load_ground_truth  # noqa: E402
from scripts.score_k_ladder_phase2_rungs import (  # noqa: E402
    BOARD_BOUNDS,
    BOOTSTRAP,
    BUFFERS,
    ERA2_BOUNDS,
    GROUND_TRUTH,
    HEADLINE_BUFFER,
    PHASE2_DIR,
    SEED,
    SWEEP_BUFFERS,
    argmax_at_headline,
    cell_dir_name,
    eval_command,
)

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

RUN_ID = "gemini37-screen-2026-08-28"
#: The proposer cell, as ``image_b_analysis.py --cell`` names it.
CELL = "g384_ov192_g37"
VERIFIER_ROOT = (
    "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37"
)
#: The cell's prepared passes (``<SCORING>/common/<CELL>/run_<i>/``), from
#: which the origin route rebuilds each union row's member tiles.
SCORING = "outputs/gemini37-screen-2026-08-28/scoring"

#: The project CRS every sweep scores in (``sweep_f1_greedy_pv.py``'s).
SCORING_CRS = "EPSG:32635"

#: Cross-check: the K = 5 stage's committed carried set holds this many
#: features at (vote_t 5, prob_t 0.10). The same filter applied to the
#: origin-routed union must reproduce it, or the join has moved and the
#: derivation is not trustworthy. The count is keyed by the leg directory
#: read (the leg rule, ``scripts/lib_verify_dirs.py``): 443 on the leg as run
#: (``verify/``, the committed rung; ``MAP_READER_VERIFY_DIRS=fixed``) and,
#: DATED UPDATE 2026-10-15, 451 with the wrong-sheet rows re-verified on
#: their own sheet (``verify_repaired/``; PI ruling D62 (1)), the count of
#: the carried set as the S164 restatement pass regenerates it (rulings
#: D65 (2) and (3); ``reports/s164-agent-records/restatement-pass.md``
#: § 1.4). A leg with no entry here refuses.
CARRIED_CROSSCHECK = {
    5: {"vote_t": 5, "prob_t": 0.10,
        "n_detections": {"verify": 443, "verify_repaired": 451},
        "source": "results/gemini37-screen-2026-08-28/verified_best_20m.geojson"},
}

OUT_DIR = PHASE2_DIR / "g37-opmax"
JOBS_FILE = PHASE2_DIR / "g37-opmax-jobs.txt"
POINTS_JSON = OUT_DIR / "operating-points.json"
SCORES_JSON = OUT_DIR / "scores.json"

#: The two committed stages, each verified by the carried Gemini 3 verifier.
#: ``union`` is the file the stage's crops manifest names as its
#: ``source_geojson``; ``carried`` is the point the register already holds.
STAGES: list[dict[str, Any]] = [
    {
        "k": 5,
        "verify_dir": f"{VERIFIER_ROOT}/verify",
        "crops_dir": f"{VERIFIER_ROOT}/crops",
        "union": f"{VERIFIER_ROOT}/union_k5.geojson",
        "stage_id": "g384_ov192_g37-union-k5-verify",
        "carried_condition_id": (
            "gemini37-screen-2026-08-28::"
            "g37-text-k5-verified-carried-p0.10-k5-era2b"
        ),
    },
    {
        "k": 10,
        "verify_dir": f"{VERIFIER_ROOT}/verify_k10",
        "crops_dir": f"{VERIFIER_ROOT}/crops_k10",
        "union": f"{VERIFIER_ROOT}/union_k10.geojson",
        "stage_id": "g384_ov192_g37-union-k10-verify",
        "carried_condition_id": (
            "gemini37-screen-2026-08-28::"
            "g37-text-k10-verified-carried-p0.10-k10-era2b"
        ),
    },
]


def common_bounds() -> gpd.GeoDataFrame:
    """The grid-common carrier frame the gold-standard chain tiles unions on."""
    return gpd.read_file(COMMON_BOUNDS)


def origin_union(stage: dict[str, Any], leg: str) -> gpd.GeoDataFrame:
    """One stage's union on the origin route, as the gold-standard chain loads it.

    The union is joined to its leg's probabilities under the leg rule
    (``image_b_analysis.load_image_union``), its carrier tiles are checked
    (``stride_verifier_analysis.reassign_gate``), and each row's member tiles
    are rebuilt from the cell's first ``k`` prepared passes and the row is
    re-tiled on its own sheet (``lib_cluster_origins.union_on_origin``), the
    sequence ``image_b_analysis.main`` runs for these stages.

    Args:
        stage: One entry of :data:`STAGES`.
        leg: The leg's fixed directory name (``verify`` or ``verify_k10``).

    Returns:
        The union in the project CRS, indexed by verifier candidate number,
        with ``vote_count``, ``mound_probability``, ``source_tile`` on the
        row's origin sheet and the member tiles (``origin_tiles``). Its
        ``attrs["verifier_probabilities"]`` names the directory read.
    """
    union = load_image_union(BASE_DIR / VERIFIER_ROOT, Path(stage["union"]).name, leg)
    provenance = union.attrs.get("verifier_probabilities")
    bounds = common_bounds()
    union = reassign_gate(union, bounds, CELL)
    passes = load_cell_passes(BASE_DIR / SCORING, CELL, n_passes=stage["k"])
    union = union_on_origin(union, passes, bounds, label=CELL, n_passes=stage["k"])
    union.attrs["verifier_probabilities"] = provenance
    return union


def sweep_rows(
    union: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame, gt: gpd.GeoDataFrame, *,
    config: str, buffers: list[int], clip_area: str | None = None,
) -> list[dict[str, Any]]:
    """Sweep an origin-routed union over ``sweep_f1_greedy_pv.py``'s grid.

    The same vote thresholds (1 to the union's largest vote count), the same
    probability grid (``sweep_f1_greedy_pv.PROB_THRESHOLDS``), the same scorer
    (``calculate_f1_internal``, which reads the rows' member tiles) and the
    same row schema and rounding, so :func:`argmax_at_headline` reads it
    unchanged. With ``clip_area`` the candidates outside the D51 common area
    are removed first and every row names the clip, as the tool's
    ``--clip-area`` does.

    Args:
        union: The stage's union on the origin route (:func:`origin_union`).
        bounds: The frame, in the project CRS.
        gt: The reference set (``sweep_f1_wbf.load_ground_truth``).
        config: The ``config`` label every row carries.
        buffers: Match radii in metres.
        clip_area: The common-area GeoJSON, or ``None``.

    Returns:
        One row per (buffer, vote_t, prob_t), buffers outermost.
    """
    cands = union.to_crs(SCORING_CRS)
    clip_tag: dict[str, Any] = {}
    if clip_area is not None:
        area, clip_name = read_area_geojson(clip_area)
        cands, n_clipped = clip_points_to_area(cands, area)
        clip_tag = {"clip_area": clip_name, "clip_area_file": str(clip_area),
                    "clip_n_removed": n_clipped}
    max_votes = int(union["vote_count"].max()) if len(union) else 1
    rows: list[dict[str, Any]] = []
    for buffer_m in buffers:
        for vote_t in range(1, max_votes + 1):
            for prob_t in PROB_THRESHOLDS:
                sub = cands[(cands["vote_count"] >= vote_t)
                            & (cands["mound_probability"] >= prob_t)]
                if len(sub) == 0:
                    p = r = f1 = 0.0
                else:
                    p, r, f1 = calculate_f1_internal(sub, gt, bounds, buffer_metres=buffer_m)
                rows.append({"config": config, "vote_t": vote_t, "prob_t": prob_t,
                             "n": int(len(sub)), "p": round(p, 4), "r": round(r, 4),
                             "f1": round(f1, 4), "buffer_m": buffer_m, **clip_tag})
    return rows


def sweep(
    stage: dict[str, Any], union: gpd.GeoDataFrame, *, bounds: str, out_name: str,
    clip_area: str | None = None,
) -> Path:
    """Sweep one stage's origin-routed union on one frame and write the rows.

    Args:
        stage: The stage, its ``verify_dir`` the directory the leg rule read.
        union: The stage's union on the origin route.
        bounds: The frame's bounds file (repository-relative).
        out_name: The sweep file's name in the stage's verify directory.
        clip_area: The D51 common-area GeoJSON, or ``None``.

    Returns:
        The written sweep path.
    """
    output = BASE_DIR / stage["verify_dir"] / out_name
    frame = gpd.read_file(BASE_DIR / bounds).to_crs(SCORING_CRS)
    rows = sweep_rows(union, frame, load_ground_truth(), config=f"g37-text-k{stage['k']}",
                      buffers=SWEEP_BUFFERS, clip_area=clip_area)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, indent=2))
    return output


def materialise_origin(
    union: gpd.GeoDataFrame, *, vote_t: int, prob_t: float, output: Path,
) -> int:
    """Write one operating point of an origin-routed union, as the chain does.

    ``image_b_analysis.py`` writes its best set the same way
    (``verified_subset`` then WGS84 GeoJSON), so the rows keep their member
    tiles and the scorer books each to its own sheet.

    Returns:
        The feature count written.
    """
    subset = verified_subset(union, prob_t, vote_t)
    output.parent.mkdir(parents=True, exist_ok=True)
    subset.to_crs("EPSG:4326").to_file(output, driver="GeoJSON")
    return int(len(subset))


def cmd_prepare(args: argparse.Namespace) -> None:
    """Sweep, pick the board-frame argmax, materialise, write the eval jobs."""
    entries: list[dict[str, Any]] = []
    jobs: list[str] = []

    # PI ruling D51: these stages and the family's K = 1 and K = 3 rungs must
    # have searched the same area of the board frame before they are compared.
    pools = {f"K = {k}": union for k, union in new_rung_pools("g384_ov192_g37").items()}
    pools.update({f"K = {stage['k']}": stage["crops_dir"] for stage in STAGES})
    comparison = run_area_gate(
        pools,
        frame=BOARD_BOUNDS,
        tolerance_km2=args.area_tolerance_km2,
        clip_to_common=args.clip_to_common_area,
        allow_undetermined=args.allow_undetermined_area,
        clip_geojson=OUT_DIR / "common-assessed-area.geojson",
        what="the 3.7 GS ladder",
    )
    clip_area = comparison.record.get("clip_geojson")

    for fixed_stage in STAGES:
        # The shared leg rule picks the directory; everything below reads it.
        leg = Path(fixed_stage["verify_dir"]).name
        vdir = resolve_verify_dir(BASE_DIR / VERIFIER_ROOT, leg)
        stage = {**fixed_stage, "verify_dir": str(vdir.relative_to(BASE_DIR))}
        provenance = verify_dir_provenance(vdir, BASE_DIR)
        # The union on the origin route, as the gold-standard chain loads it;
        # every sweep and cell below reads this frame, never the bare union.
        union = origin_union(fixed_stage, leg)
        # Before trusting the join, reproduce a point whose feature count is
        # already committed (the feedback_feature_count_crosscheck rule).
        check = CARRIED_CROSSCHECK.get(stage["k"])
        if check:
            want = check["n_detections"].get(vdir.name)
            probe = OUT_DIR / "crosscheck" / f"k{stage['k']}-carried.geojson"
            got = materialise_origin(
                union, vote_t=check["vote_t"], prob_t=check["prob_t"], output=probe,
            )
            if want is None or got != want:
                logger.error(
                    "K=%d cross-check FAILED: re-applying (%d, %.2f) to this "
                    "stage (leg %s) yields %d features, but %s holds %s. The "
                    "index join has moved, or this leg has no committed count; "
                    "refusing to derive an operating point from it.",
                    stage["k"],
                    check["vote_t"],
                    check["prob_t"],
                    vdir.name,
                    got,
                    check["source"],
                    want,
                )
                sys.exit(8)
            logger.info(
                "K=%d cross-check OK: (%d, %.2f) reproduces %d features",
                stage["k"],
                check["vote_t"],
                check["prob_t"],
                got,
            )

        board = argmax_at_headline(
            sweep(stage, union, bounds=BOARD_BOUNDS, out_name="sweep_2d_era2b.json",
                  clip_area=clip_area)
        )
        era2 = argmax_at_headline(
            sweep(stage, union, bounds=ERA2_BOUNDS, out_name="sweep_2d.json",
                  clip_area=clip_area)
        )
        agree = (board["vote_t"], board["prob_t"]) == (
            era2["vote_t"],
            era2["prob_t"],
        )
        label = f"g37-text-k{stage['k']}-verified-opmax"
        detections = OUT_DIR / "materialised" / f"{label}.geojson"
        count = materialise_origin(
            union, vote_t=board["vote_t"], prob_t=board["prob_t"], output=detections,
        )
        if clip_area is not None:
            count -= clip_geojson_file(
                detections, comparison.common, name=COMMON_AREA_CLIP_NAME,
            )
        cell = cell_dir_name(RUN_ID, label)
        jobs.append(
            eval_command(detections, cell, label).replace(
                "results/k-ladder-2026-09-12/phase2/cells/",
                "results/k-ladder-2026-09-12/phase2/g37-opmax/cells/",
            )
        )
        entries.append(
            {
                "k": stage["k"],
                "label": label,
                "run_id": RUN_ID,
                "stage_id": stage["stage_id"],
                "union": stage["union"],
                "probabilities": f"{stage['verify_dir']}/probabilities.json",
                "opmax": {
                    "vote_t": board["vote_t"],
                    "prob_t": board["prob_t"],
                    "sweep_f1_20": board["f1"],
                    "sweep_n": board["n"],
                    "n_ties_at_argmax": board["n_ties"],
                },
                "opmax_on_era2_frame": {
                    "vote_t": era2["vote_t"],
                    "prob_t": era2["prob_t"],
                    "sweep_f1_20": era2["f1"],
                },
                "frames_agree_on_argmax": agree,
                "n_detections": count,
                "detections": str(detections.relative_to(BASE_DIR)),
                "cell": cell,
                "eval_path": (
                    "results/k-ladder-2026-09-12/phase2/g37-opmax/cells/"
                    f"{cell}/evaluation.json"
                ),
                "carried_condition_id": stage["carried_condition_id"],
                "verifier_probabilities": provenance,
                "scoring_route": (
                    "origin: image_b_analysis.load_image_union, "
                    "stride_verifier_analysis.reassign_gate, "
                    f"lib_cluster_origins.union_on_origin over {SCORING}/common/"
                    f"{CELL} runs 1-{stage['k']} (PR #42, D62 (1))"
                ),
            }
        )
        logger.info(
            "K=%2d  opmax (%d, %.2f) sweep F1 %.4f n=%d  frames agree: %s",
            stage["k"],
            board["vote_t"],
            board["prob_t"],
            board["f1"],
            count,
            agree,
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(POINTS_JSON, "w") as handle:
        json.dump(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "script": "scripts/derive_g37_gs_opmax_rungs.py",
                "script_version": __version__,
                "api_calls": 0,
                "registered": False,
                "assessed_area": comparison.record,
                "stages": entries,
            },
            handle,
            indent=2,
        )
        handle.write("\n")
    with open(JOBS_FILE, "w") as handle:
        handle.write("\n".join(jobs) + "\n")
    logger.info("%d eval job(s) -> %s", len(jobs), JOBS_FILE.relative_to(BASE_DIR))


def cmd_collect(args: argparse.Namespace) -> None:
    """Read the two derived opmax evaluations into a scores JSON."""
    with open(POINTS_JSON) as handle:
        points = json.load(handle)
    missing: list[str] = []
    for stage in points["stages"]:
        path = BASE_DIR / stage["eval_path"]
        if not path.exists():
            missing.append(stage["eval_path"])
            continue
        with open(path) as handle:
            evaluation = json.load(handle)
        summary = evaluation["summary"]
        headline = next(
            entry
            for entry in summary["buffers"]
            if int(entry["buffer_metres"]) == HEADLINE_BUFFER
        )
        mcc = (summary.get("tile_classification") or {}).get("mcc") or {}
        stage["f1_20"] = headline.get("f1")
        stage["tile_mcc"] = mcc.get("point")
        logger.info(
            "K=%2d  F1@20 %.4f  tile-MCC %.4f",
            stage["k"],
            stage["f1_20"],
            stage["tile_mcc"],
        )
    with open(SCORES_JSON, "w") as handle:
        json.dump(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "recipe": {
                    "bounds": BOARD_BOUNDS,
                    "ground_truth": GROUND_TRUTH,
                    "buffers": BUFFERS,
                    "bootstrap": BOOTSTRAP,
                    "seed": SEED,
                    "mcc": True,
                },
                "n_missing_evaluations": len(missing),
                "missing_evaluations": missing,
                "stages": points["stages"],
            },
            handle,
            indent=2,
        )
        handle.write("\n")
    logger.info("-> %s", SCORES_JSON.relative_to(BASE_DIR))


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Derive the sweep-optimal point for the committed 3.7 GS screen "
            "K = 5 / K = 10 rungs (US$0, no API calls, not registered)"
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare")
    add_area_gate_arguments(prepare)
    prepare.set_defaults(func=cmd_prepare)
    collect = subparsers.add_parser("collect")
    collect.set_defaults(func=cmd_collect)
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    args.func(args)


if __name__ == "__main__":
    main()
