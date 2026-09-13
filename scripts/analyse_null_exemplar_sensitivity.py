#!/usr/bin/env python3
# ============================================================================
# analyse_null_exemplar_sensitivity.py
# ----------------------------------------------------------------------------
# Sensitivity of the Gold-Standard boards to the few-shot NULL-exemplar leak.
#
# THE LEAK
# --------
# Three "null" (empty) exemplar tiles in the few-shot library were never
# excluded from the Gold-Standard evaluation frames. Byte-identical copies of
# them are `example_15/16/17.png` in `inputs/examples/neutral-naming/`
# (verified by SHA-256), carried in every proposer config's example list with
# `"category": "null"`. A configuration that transmitted the example IMAGES
# therefore showed the model those pixels labelled "no mounds here" and was
# then scored on them; a text-only configuration
# (`include_example_images: false`) sent only the labels, no pixels. No
# `verify_*.json` config carries a null-category example, so the verifier
# stage never transmitted them, and a cell whose `-image`/`-text` suffix names
# its VERIFIER variant is classified by its PROPOSER pool.
#
# No reference mound lies inside any of the three null windows, so the leak can
# only have suppressed FALSE POSITIVES. That is the signature this script
# looks for first.
#
# WHAT IT COMPUTES
# ----------------
# 1. `signature` — the leak-signature test, on the FULL frame. For every board
#    cell, the per-tile TP/FP/FN table the board's own instruments build, split
#    into the exposed tiles and the rest. If the leak bit, image-bearing cells
#    should show a LOWER false-positive rate on the exposed tiles relative to
#    the rest of the frame than text-only cells do. Tested by a permutation
#    test on the image-minus-text difference of log FP-rate ratios.
# 2. `rescore` — every cell re-scored on the REDUCED frame (frame minus the
#    exposed tiles) with the board's own recipe, via `evaluate_detections.py`.
#    Excluding a tile from the evaluation must also exclude what the model said
#    about it, so each cell's detections are filtered to drop every feature
#    booked to an exposed tile. This is not optional book-keeping: the
#    published name-based (`id`) tile join books a detection by its
#    `source_tile` STRING, so a detection reported from a dropped tile but
#    lying inside a retained one has no frame tile to be credited to, and the
#    shortfall invariant refuses the cell's whole per-tile table. Filtering
#    restores the invariant by construction AND is the correct counterfactual.
# 3. `swap` — the paired round-robin tile-swap permutation (10,000 draws,
#    seed 42) between each image cell and its nearest text comparator, on the
#    FULL frame and on the REDUCED frame, so a change in the verdict can be
#    attributed to the leak rather than to the frame.
# 4. `assemble` — the before/after tables and `analysis.json`.
#
# The Era-2 F1 tiering, its Hsu MCB set and the tile-MCC family are rebuilt on
# the reduced frame by the board's own instruments
# (`era1_leaderboard_tiering.py --permute-mcc`, `selection_aware_intervals.py
# --board`) driven by the register overrides this script writes in the
# `override` stage. Nothing under `results/leaderboard/**` is touched: this is
# a sensitivity analysis BESIDE the boards.
#
# Usage:
#     python scripts/analyse_null_exemplar_sensitivity.py --stage inventory
#     python scripts/analyse_null_exemplar_sensitivity.py --stage filter
#     python scripts/analyse_null_exemplar_sensitivity.py --stage rescore \
#         --workers 12
#     python scripts/analyse_null_exemplar_sensitivity.py --stage signature
#     python scripts/analyse_null_exemplar_sensitivity.py --stage override
#     python scripts/analyse_null_exemplar_sensitivity.py --stage swap
#     python scripts/analyse_null_exemplar_sensitivity.py --stage assemble
#
# Created: 2026-09-13
# Author: Shawn Ross, Claude Code
# Licence: Apache 2.0
# ============================================================================

from __future__ import annotations

import argparse
import glob
import json
import logging
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))

from era1_leaderboard_tiering import (  # noqa: E402
    cell_detections,
    cell_per_tile,
    cell_per_tile_classification,
    load_board_refs,
    resolve_condition,
)
from lib_advanced_metrics import TileJoinRefusalError  # noqa: E402
from n1_baseline_leaderboard_tiering import (  # noqa: E402
    micro_f1,
    permutation_test_float,
)
from pairwise_permutation_test import permutation_test_mcc_arrays  # noqa: E402

LOG = logging.getLogger("null-exemplar-sensitivity")

OUT_DIR = BASE_DIR / "results/null-exemplar-sensitivity-2026-09-13"
OVERLAP = OUT_DIR / "overlap_tiles.json"
CONDITIONS = BASE_DIR / "results/run-conditions.json"
GROUND_TRUTH = "inputs/vectors/references/mounds-reference.geojson"
TARGET_CRS = "EPSG:32635"

#: The board's own recipe, read off its score-commands.sh.
BUFFERS = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150]
BOOTSTRAP = 10_000
SEED = 42
HEADLINE_BUFFER = 20
N_PERMUTATIONS = 10_000

ERA2_BOARD = "results/leaderboard/era2/gs-era2-verified-board-2026-09-10"

#: The boards under test: (board key, frame id, analyses file, analysis id).
BOARDS: list[tuple[str, str, str, str]] = [
    ("era2-verified", "era2-b-487",
     f"{ERA2_BOARD}/tiering-input/run-analyses.json",
     "gs-era2-verified-board-2026-09-10"),
    ("era1-leaderboard", "era1-full-340",
     "results/run-analyses.json", "era1-leaderboard"),
    ("era1-single-pass", "era1-full-340",
     "results/run-analyses.json", "era1-single-pass-baseline-matrix"),
    ("tile-size-sweep-512", "era1-full-340",
     "results/run-analyses.json", "tile-size-sweep"),
]

#: Roots a proposer pool's output directory may sit under.
POOL_ROOTS = ["outputs/h11", "outputs", "outputs/retest"]

#: `include_example_images` defaults to TRUE in the pipeline —
#: scripts/4_detect_mounds_batch.py:885. A config without the key sent images.
PIPELINE_INCLUDE_IMAGES_DEFAULT = True


# ── helpers ──────────────────────────────────────────────────────────────

def load_overlap() -> dict[str, Any]:
    """Load the overlap record written by compute_null_exemplar_overlap.py.

    Returns:
        The parsed record, keyed for convenience by frame id under "by_frame".
    """
    rec = json.loads(OVERLAP.read_text())
    rec["by_frame"] = {f["frame_id"]: f for f in rec["frames"]}
    return rec


def cli_of(cond: dict) -> dict:
    """Read a condition's recorded evaluate_detections.py invocation.

    Mirrors the fallbacks in ``era1_leaderboard_tiering.load_cells`` so every
    cell shape (single set, list, pass directory, batch-scored) resolves.

    Args:
        cond: A decomposed condition dict from run-conditions.json.

    Returns:
        The cell's ``cli_args``, with ``bounds``/``ground_truth``/detection
        keys filled from ``input_files`` where the recorded args are null.
    """
    meta = json.loads((BASE_DIR / cond["eval_path"]).read_text())["_metadata"]
    cli = dict(meta.get("cli_args") or {})
    inf = meta.get("input_files") or {}
    cli.setdefault("bounds", inf.get("bounds"))
    cli.setdefault("ground_truth", inf.get("ground_truth"))
    if not (cli.get("detections") or cli.get("detections_dir")):
        fallback = inf.get("detections")
        if isinstance(fallback, str):
            cli["detections_dir"] = fallback
        elif isinstance(fallback, list) and fallback:
            cli["detections"] = fallback
    return cli


def detection_paths(cli: dict) -> list[str]:
    """Resolve a cell's detection files from its recorded cli_args.

    Args:
        cli: The cell's ``cli_args``.

    Returns:
        Sorted repository-relative detection file paths.
    """
    if cli.get("detections_dir"):
        pattern = cli.get("glob") or "*.geojson"
        hits = sorted(glob.glob(str(BASE_DIR / cli["detections_dir"] / pattern)))
        if not hits:
            hits = sorted(glob.glob(str(BASE_DIR / cli["detections_dir"] / "*/*.geojson")))
        return [str(Path(h).resolve().relative_to(BASE_DIR)) for h in hits]
    det = cli.get("detections")
    det = [det] if isinstance(det, str) else list(det or [])
    return [str(d) for d in det]


def pool_output_dir(run: str, pool: str, pool_path: str) -> str | None:
    """Locate a proposer pool's output directory under ``outputs/``.

    Args:
        run: The run id the pool belongs to.
        pool: The pool key as the register names it.
        pool_path: The pool's registered relative path (often equal to ``pool``).

    Returns:
        A repository-relative directory path, or None if none exists.
    """
    candidates: list[str] = []
    for name in (pool_path, pool):
        if not name:
            continue
        for root in POOL_ROOTS:
            candidates += [f"{root}/{run}/{name}", f"{root}/{name}"]
        if run.startswith("retest-"):
            candidates.append(f"outputs/retest/{run[len('retest-'):]}/{name}")
    for cand in candidates:
        if (BASE_DIR / cand).is_dir():
            return cand
    return None


def read_run_meta(path: Path) -> dict[str, Any] | None:
    """Read one run.meta.json's example-image state.

    Args:
        path: Path to a ``*.meta.json`` written by the detection pipeline.

    Returns:
        ``{"config": version, "include_example_images": bool,
        "n_null_examples": int}``, or None when the file carries no
        configuration block.
    """
    try:
        cfg = json.loads(path.read_text()).get("configuration") or {}
    except (OSError, json.JSONDecodeError):
        return None
    if not cfg:
        return None
    snapshot = cfg.get("full_config_snapshot") or {}
    include = cfg.get("include_example_images")
    if include is None:
        include = snapshot.get("include_example_images")
    if include is None:
        include = PIPELINE_INCLUDE_IMAGES_DEFAULT
    examples = snapshot.get("examples") or []
    return {
        "config": cfg.get("version") or snapshot.get("version"),
        "include_example_images": bool(include),
        "n_null_examples": sum(1 for e in examples
                               if isinstance(e, dict) and e.get("category") == "null"),
    }


def proposer_metas(pool_dir: str) -> list[dict[str, Any]]:
    """Collect the PROPOSER run metadata under a pool directory.

    Verifier metadata is excluded: a `verify_*` config carries no
    null-category example, so it says nothing about the leak, and a pool
    directory usually contains a `verified/` subtree whose metas would
    otherwise be mistaken for the proposer's.

    Args:
        pool_dir: Repository-relative pool output directory.

    Returns:
        One dict per distinct proposer configuration found.
    """
    root = BASE_DIR / pool_dir
    paths = sorted(set(glob.glob(str(root / "*.meta.json"))
                       + glob.glob(str(root / "*/*.meta.json"))
                       + glob.glob(str(root / "*/*/*.meta.json"))))
    seen: dict[tuple, dict] = {}
    for p in paths:
        meta = read_run_meta(Path(p))
        if meta is None or not meta["config"]:
            continue
        if str(meta["config"]).startswith("verify_"):
            continue
        seen.setdefault((meta["config"], meta["include_example_images"],
                         meta["n_null_examples"]), meta)
    return list(seen.values())


def config_file_state(pool: str) -> dict[str, Any] | None:
    """Read a proposer config by name from ``prompts/configs/``.

    The last-resort source: some pool keys ARE config version names
    (``detect_brief-text``), so the config file itself records whether the
    images went out.

    Args:
        pool: The pool key.

    Returns:
        The same shape as :func:`read_run_meta`, or None if no such config.
    """
    for stem in (pool, f"detect_{pool}"):
        for path in sorted(glob.glob(str(BASE_DIR / "prompts/configs" / f"{stem}.json"))
                           + glob.glob(str(BASE_DIR / "prompts/configs/**" / f"{stem}.json"),
                                       recursive=True)):
            cfg = json.loads(Path(path).read_text())
            include = cfg.get("include_example_images", PIPELINE_INCLUDE_IMAGES_DEFAULT)
            examples = cfg.get("examples") or []
            return {
                "config": cfg.get("version") or stem,
                "include_example_images": bool(include),
                "n_null_examples": sum(
                    1 for e in examples
                    if isinstance(e, dict) and e.get("category") == "null"),
                "source_file": str(Path(path).resolve().relative_to(BASE_DIR)),
            }
    return None


def name_modality(text: str) -> str | None:
    """Classify a pool or label string as image / text / both by its tokens.

    Args:
        text: A pool key or condition label.

    Returns:
        "image", "text", "both", or None.
    """
    has_image, has_text = "image" in text, "text" in text
    if has_image and has_text:
        return "both"
    if has_image:
        return "image"
    if has_text:
        return "text"
    return None


# ── stage: inventory ─────────────────────────────────────────────────────

def classify_cell(run: str, label: str, cond: dict,
                  decomposition: dict) -> dict[str, Any]:
    """Decide whether a board cell's proposer transmitted the null images.

    Four sources are consulted and ALL that are available are recorded, so a
    disagreement is visible rather than silently resolved:

    1. the proposer pool's run metadata (`include_example_images` AND a
       null-category example in the snapshot) — the record of what was
       actually sent, and therefore authoritative;
    2. the register's `proposer_pools[...].modality`;
    3. the proposer config file, when the pool key names one;
    4. the pool key's own image/text token.

    Args:
        run: Run id.
        label: Condition label.
        cond: The decomposed condition dict.
        decomposition: The whole ``run-conditions.json`` decomposition.

    Returns:
        A record with ``exposed`` (bool), ``exposure_source``, and every
        source's verdict.
    """
    pool = cond.get("proposer_pool") or ""
    pools = decomposition[run].get("proposer_pools") or {}
    registered = pools.get(pool) or next(
        (v for v in pools.values() if v.get("path") == pool), {})
    register_modality = registered.get("modality")
    pool_path = registered.get("path", pool)

    pool_dir = pool_output_dir(run, pool, pool_path)
    metas = proposer_metas(pool_dir) if pool_dir else []
    meta_verdict = None
    if metas:
        # Exposed if ANY proposer pass sent images alongside a null example.
        meta_verdict = any(m["include_example_images"] and m["n_null_examples"] > 0
                           for m in metas)

    cfg = config_file_state(pool)
    cfg_verdict = None
    if cfg is not None:
        cfg_verdict = cfg["include_example_images"] and cfg["n_null_examples"] > 0

    token = name_modality(pool)

    if meta_verdict is not None:
        exposed, source = meta_verdict, "run-metadata"
    elif register_modality in ("image", "text"):
        exposed, source = register_modality == "image", "register-modality"
    elif cfg_verdict is not None:
        exposed, source = cfg_verdict, "config-file"
    elif token in ("image", "text"):
        exposed, source = token == "image", "pool-name-token"
    else:
        raise ValueError(f"{run}::{label}: no modality signal (pool {pool!r})")

    # Every source that spoke must agree with the verdict, or the cell is
    # flagged. `both` is not a disagreement — a "text+image" config IS
    # image-bearing.
    votes = {
        "run_metadata": meta_verdict,
        "register_modality": (None if register_modality not in ("image", "text")
                              else register_modality == "image"),
        "config_file": cfg_verdict,
        "pool_name_token": (None if token is None else token in ("image", "both")),
    }
    stated = {k: v for k, v in votes.items() if v is not None}
    return {
        "proposer_pool": pool,
        "pool_output_dir": pool_dir,
        "proposer_configs": metas or ([cfg] if cfg else []),
        "exposed": exposed,
        "exposure_source": source,
        "votes": votes,
        "sources_disagree": len(set(stated.values())) > 1,
    }


def build_inventory() -> dict[str, Any]:
    """Build the per-board cell inventory with exposure classification.

    Returns:
        The inventory record (also written to ``cell_inventory.json``).
    """
    overlap = load_overlap()
    decomposition = json.loads(CONDITIONS.read_text())["decomposition"]
    boards: list[dict[str, Any]] = []
    for key, frame_id, analyses, analysis_id in BOARDS:
        frame = overlap["by_frame"][frame_id]
        try:
            refs = load_board_refs(BASE_DIR / analyses, analysis_id)
        except StopIteration:
            LOG.warning("%s: analysis %s absent — skipped", key, analysis_id)
            continue
        cells = []
        for ref in refs:
            run, label = ref.split("::", 1)
            cond = resolve_condition(CONDITIONS, ref)
            cli = cli_of(cond)
            # A board's frame is the one its own cells were scored on. A cell
            # scored on another frame (the 256/384 legs of the tile-size
            # sweep) is out of scope for THIS frame's reduction.
            if cli.get("bounds") != frame["bounds"]:
                continue
            rec = classify_cell(run, label, cond, decomposition)
            rec.update({
                "ref": ref,
                "run": run,
                "label": label,
                "architecture": cond.get("architecture"),
                "eval_path": cond["eval_path"],
                "committed_bounds": cli.get("bounds"),
                "detections": detection_paths(cli),
            })
            cells.append(rec)
        n_exposed = sum(c["exposed"] for c in cells)
        LOG.info("%s (%s): %d cells in frame — %d image-bearing, %d text control",
                 key, frame_id, len(cells), n_exposed, len(cells) - n_exposed)
        disagree = [c["ref"] for c in cells if c["sources_disagree"]]
        if disagree:
            LOG.warning("  %d cell(s) whose modality sources disagree: %s",
                        len(disagree), ", ".join(disagree))
        boards.append({
            "board": key,
            "frame_id": frame_id,
            "analyses": analyses,
            "analysis_id": analysis_id,
            "bounds_full": frame["bounds"],
            "bounds_reduced": frame["reduced_bounds"],
            "n_exposed_tiles": frame["n_overlap"],
            "n_cells": len(cells),
            "n_image_bearing": n_exposed,
            "n_text_control": len(cells) - n_exposed,
            "cells": cells,
        })
    record = {
        "_README": (
            "Board cells classified by whether their PROPOSER transmitted the "
            "three null exemplar images, for the null-exemplar leak "
            "sensitivity analysis of 2026-09-13. `exposed` true means the "
            "cell's proposer sent example IMAGES including at least one "
            "null-category exemplar; false means it is a text control that "
            "sent the labels only. Verifier stages carry no null exemplar, so "
            "a cell whose label names an image VERIFIER over a text proposer "
            "is a text control."
        ),
        "generated_by": "scripts/analyse_null_exemplar_sensitivity.py --stage inventory",
        "include_example_images_pipeline_default": PIPELINE_INCLUDE_IMAGES_DEFAULT,
        "boards": boards,
    }
    (OUT_DIR / "cell_inventory.json").write_text(json.dumps(record, indent=2) + "\n")
    LOG.info("wrote %s", (OUT_DIR / "cell_inventory.json").relative_to(BASE_DIR))
    return record


# ── stage: filter ────────────────────────────────────────────────────────

def filter_one(src: str, dest: Path, drop: set[str],
               full_bounds: gpd.GeoDataFrame) -> dict[str, Any]:
    """Write ``src`` without the features booked to a dropped tile.

    The features are filtered in the RAW GeoJSON so every property and the
    file's CRS declaration survive byte-for-byte; only the feature list
    shrinks. Where a file carries no ``source_tile`` property, the booking
    tile is back-filled by the same spatial join ``evaluate_detections.py``
    uses (first intersecting frame tile), so the filter matches the scorer's
    own rule.

    Args:
        src: Repository-relative source detection GeoJSON.
        dest: Absolute destination path.
        drop: Tile names to drop.
        full_bounds: The FULL frame in ``TARGET_CRS``, for the back-fill.

    Returns:
        A manifest entry with the feature counts and the destination path.
    """
    payload = json.loads((BASE_DIR / src).read_text())
    features = payload.get("features") or []
    booked: list[str | None] = []
    if features and "source_tile" in (features[0].get("properties") or {}):
        booked = [(f.get("properties") or {}).get("source_tile") for f in features]
        backfilled = False
    elif features:
        gdf = gpd.read_file(BASE_DIR / src)
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        gdf = gdf.to_crs(TARGET_CRS)
        joined = gpd.sjoin(gdf, full_bounds[["tile_name", "geometry"]],
                           how="left", predicate="intersects")
        joined = joined[~joined.index.duplicated(keep="first")]
        booked = [None if v is None or v != v else str(v)
                  for v in joined["tile_name"].tolist()]
        backfilled = True
    else:
        backfilled = False

    keep = [i for i, tile in enumerate(booked) if tile not in drop]
    payload["features"] = [features[i] for i in keep]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload) + "\n")
    return {
        "source": src,
        "filtered": str(dest.resolve().relative_to(BASE_DIR)),
        "n_features": len(features),
        "n_dropped": len(features) - len(keep),
        "n_kept": len(keep),
        "source_tile_backfilled": backfilled,
    }


def cell_slug(ref: str) -> str:
    """Turn a ``<run>::<label>`` ref into a filesystem-safe directory name.

    Args:
        ref: The board ref.

    Returns:
        A slug with ``::`` as ``__`` and every other awkward character as ``-``.
    """
    return re.sub(r"[^A-Za-z0-9_.-]", "-", ref.replace("::", "__"))


def stage_filter(inventory: dict[str, Any]) -> dict[str, Any]:
    """Write leak-filtered copies of every cell's detections.

    Args:
        inventory: The record from :func:`build_inventory`.

    Returns:
        The filter manifest (also written to ``detections_manifest.json``).
    """
    overlap = load_overlap()
    out: list[dict[str, Any]] = []
    # A cell can belong to more than one board on the same frame (the Era-1
    # single-pass matrix is a subset of the Era-1 leaderboard). It is filtered
    # and scored ONCE per (frame, ref); the boards it belongs to are listed.
    seen: dict[tuple[str, str], dict[str, Any]] = {}
    for board in inventory["boards"]:
        frame = overlap["by_frame"][board["frame_id"]]
        drop = set(frame["overlap_tiles"])
        full_bounds = gpd.read_file(BASE_DIR / frame["bounds"]).to_crs(TARGET_CRS)
        for cell in board["cells"]:
            key = (board["frame_id"], cell["ref"])
            if key in seen:
                seen[key]["boards"].append(board["board"])
                continue
            slug = cell_slug(cell["ref"])
            entries = []
            for src in cell["detections"]:
                dest = OUT_DIR / "detections" / board["frame_id"] / slug / Path(src).name
                # A pass directory can repeat a file name across runs; keep the
                # parent directory when that happens.
                if sum(1 for s in cell["detections"]
                       if Path(s).name == Path(src).name) > 1:
                    dest = (OUT_DIR / "detections" / board["frame_id"] / slug
                            / Path(src).parent.name / Path(src).name)
                entries.append(filter_one(src, dest, drop, full_bounds))
            seen[key] = {
                "boards": [board["board"]],
                "frame_id": board["frame_id"],
                "ref": cell["ref"],
                "slug": slug,
                "exposed": cell["exposed"],
                "n_features": sum(e["n_features"] for e in entries),
                "n_dropped": sum(e["n_dropped"] for e in entries),
                "files": entries,
            }
            out.append(seen[key])
            LOG.info("  %-70s %d/%d features dropped", cell["ref"],
                     seen[key]["n_dropped"], seen[key]["n_features"])
    manifest = {
        "_README": (
            "Leak-filtered detection copies: each cell's detections with every "
            "feature booked to an exposed tile removed, so the reduced-frame "
            "re-score drops the exposed tiles AND what the model said about "
            "them. The filtered GeoJSONs themselves are gitignored — they are "
            "a deterministic function of committed inputs and this script — "
            "but every feature count is recorded here."
        ),
        "generated_by": "scripts/analyse_null_exemplar_sensitivity.py --stage filter",
        "cells": out,
    }
    (OUT_DIR / "detections_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    LOG.info("wrote %s", (OUT_DIR / "detections_manifest.json").relative_to(BASE_DIR))
    return manifest


# ── stage: rescore ───────────────────────────────────────────────────────

def score_command(entry: dict[str, Any], bounds_reduced: str,
                  out_dir: Path) -> list[str]:
    """Build the evaluate_detections.py command for one reduced-frame cell.

    Args:
        entry: The cell's manifest entry from :func:`stage_filter`.
        bounds_reduced: Repository-relative reduced bounds GeoJSON.
        out_dir: Where the cell's evaluation is written.

    Returns:
        The argv list.
    """
    files = [e["filtered"] for e in entry["files"]]
    return [
        sys.executable, "scripts/evaluate_detections.py",
        "--detections", *files,
        "--ground-truth", GROUND_TRUTH,
        "--bounds", bounds_reduced,
        "--buffers", *[str(b) for b in BUFFERS],
        "--bootstrap", str(BOOTSTRAP),
        "--seed", str(SEED),
        "--mcc",
        "--output-dir", str(out_dir),
        "--label", entry["slug"],
    ]


def _run_one(argv: list[str]) -> tuple[int, str]:
    """Run one scoring subprocess from the repository root.

    Args:
        argv: The command to run.

    Returns:
        ``(returncode, tail of combined output)``.
    """
    proc = subprocess.run(argv, cwd=BASE_DIR, capture_output=True, text=True)
    tail = (proc.stdout + proc.stderr).strip().splitlines()[-3:]
    return proc.returncode, " | ".join(tail)


def stage_rescore(manifest: dict[str, Any], inventory: dict[str, Any],
                  workers: int) -> None:
    """Re-score every cell on its board's reduced frame.

    Args:
        manifest: The filter manifest.
        inventory: The cell inventory (for each board's reduced bounds).
        workers: Number of concurrent scoring subprocesses.
    """
    reduced = {b["frame_id"]: b["bounds_reduced"] for b in inventory["boards"]}
    jobs = []
    for entry in manifest["cells"]:
        out_dir = OUT_DIR / "cells" / entry["frame_id"] / entry["slug"]
        jobs.append((entry["ref"], score_command(entry, reduced[entry["frame_id"]],
                                                 out_dir)))
    LOG.info("scoring %d cell(s) with %d worker(s)", len(jobs), workers)
    failures = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_run_one, argv): ref for ref, argv in jobs}
        for i, fut in enumerate(as_completed(futures), 1):
            ref = futures[fut]
            code, tail = fut.result()
            if code != 0:
                failures.append((ref, tail))
                LOG.error("[%d/%d] FAILED %s: %s", i, len(jobs), ref, tail)
            else:
                LOG.info("[%d/%d] %s", i, len(jobs), ref)
    if failures:
        raise SystemExit(f"{len(failures)} cell(s) failed to score: "
                         + "; ".join(f"{r} ({t})" for r, t in failures))


# ── per-tile tables (full and reduced frames) ────────────────────────────

def per_tile_tables(cli: dict, gdf_ref: gpd.GeoDataFrame,
                    gdf_bounds: gpd.GeoDataFrame, tile_order: list[str],
                    ) -> dict[str, Any]:
    """Build a cell's per-tile F1 counts and one-hot tile classification.

    Args:
        cli: The cell's ``cli_args`` (detections pointed wherever wanted).
        gdf_ref: References in ``TARGET_CRS``.
        gdf_bounds: The frame in ``TARGET_CRS``.
        tile_order: Fixed tile order.

    Returns:
        ``{"tp","fp","fn","n_passes"}`` always, plus ``{"ctp","ctn","cfp","cfn"}``
        when the tile classification could be built, plus ``"refusal"`` when the
        tile-join invariant refused something.
    """
    out: dict[str, Any] = {}
    tp, fp, fn, n_passes = cell_per_tile(cli, gdf_ref, gdf_bounds, tile_order,
                                         HEADLINE_BUFFER)
    out.update({"tp": tp, "fp": fp, "fn": fn, "n_passes": n_passes})
    try:
        gdf_det = cell_detections(cli, gdf_bounds)
        ctp, ctn, cfp, cfn, _diag = cell_per_tile_classification(
            gdf_det, gdf_ref, gdf_bounds, tile_order)
        out.update({"ctp": ctp, "ctn": ctn, "cfp": cfp, "cfn": cfn})
    except (TileJoinRefusalError, ValueError) as error:
        out["refusal"] = str(error)
    return out


def mcc_from_confusion(tp: int, tn: int, fp: int, fn: int) -> float | None:
    """Matthews correlation coefficient from a 2x2 confusion.

    Args:
        tp: True positives.
        tn: True negatives.
        fp: False positives.
        fn: False negatives.

    Returns:
        The MCC, or None when a denominator term is zero.
    """
    num = tp * tn - fp * fn
    den = float((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)) ** 0.5
    return None if den == 0 else num / den


# ── stage: signature ─────────────────────────────────────────────────────

def stage_signature(inventory: dict[str, Any]) -> dict[str, Any]:
    """The leak-signature test, on the FULL frame.

    For each cell the per-tile false-positive count is summed over the exposed
    tiles and over the rest of the frame, and turned into FP-per-tile rates.
    The leak, if it bit, suppressed false positives on the exposed tiles of
    image-bearing cells only, so the statistic is each cell's log ratio

        r = log((FP_exposed / n_exposed + 0.5) / (FP_rest / n_rest + 0.5))

    and the test is whether the image cells' mean r is lower than the text
    cells'. The reference distribution is a 10,000-draw label permutation of
    the image/text assignment across cells (seed 42), which is exact under the
    null that exposure does not change the rate and needs no distributional
    assumption. The 0.5 continuity term keeps the ratio finite for a cell with
    no false positive on the 20 (or 25) exposed tiles.

    Args:
        inventory: The cell inventory.

    Returns:
        The signature record (also written to ``leak_signature.json``).
    """
    overlap = load_overlap()
    gdf_ref = gpd.read_file(BASE_DIR / GROUND_TRUTH).to_crs(TARGET_CRS)
    # A cell can sit on more than one board of the same frame; its per-tile
    # table is built once.
    cache: dict[tuple[str, str], dict[str, Any] | str] = {}
    bounds_cache: dict[str, tuple[gpd.GeoDataFrame, list[str]]] = {}
    boards_out = []
    for board in inventory["boards"]:
        frame = overlap["by_frame"][board["frame_id"]]
        exposed = set(frame["overlap_tiles"])
        if frame["bounds"] not in bounds_cache:
            gdf = gpd.read_file(BASE_DIR / frame["bounds"]).to_crs(TARGET_CRS)
            bounds_cache[frame["bounds"]] = (gdf, list(gdf["tile_name"].unique()))
        gdf_bounds, tile_order = bounds_cache[frame["bounds"]]
        mask = np.array([t in exposed for t in tile_order])
        n_exp, n_rest = int(mask.sum()), int((~mask).sum())
        LOG.info("%s: %d exposed / %d unexposed tiles", board["board"],
                 n_exp, n_rest)

        rows = []
        for cell in board["cells"]:
            key = (board["frame_id"], cell["ref"])
            if key not in cache:
                cond = resolve_condition(CONDITIONS, cell["ref"])
                cli = cli_of(cond)
                try:
                    cache[key] = per_tile_tables(cli, gdf_ref, gdf_bounds, tile_order)
                except (TileJoinRefusalError, ValueError) as error:
                    cache[key] = str(error)
                    LOG.warning("  WITHHELD %s: %s", cell["ref"], str(error)[:120])
            tables = cache[key]
            if isinstance(tables, str):
                rows.append({"ref": cell["ref"], "exposed": cell["exposed"],
                             "withheld": tables})
                continue
            fp_exp = float(tables["fp"][mask].sum())
            fp_rest = float(tables["fp"][~mask].sum())
            tp_exp = float(tables["tp"][mask].sum())
            tp_rest = float(tables["tp"][~mask].sum())
            rate_exp = fp_exp / n_exp
            rate_rest = fp_rest / n_rest
            rows.append({
                "ref": cell["ref"],
                "exposed": cell["exposed"],
                "n_passes": tables["n_passes"],
                "fp_exposed": round(fp_exp, 4),
                "fp_rest": round(fp_rest, 4),
                "tp_exposed": round(tp_exp, 4),
                "tp_rest": round(tp_rest, 4),
                "fp_per_tile_exposed": round(rate_exp, 5),
                "fp_per_tile_rest": round(rate_rest, 5),
                "log_ratio": round(float(np.log((rate_exp + 0.5) / (rate_rest + 0.5))), 6),
            })

        usable = [r for r in rows if "log_ratio" in r]
        img = np.array([r["log_ratio"] for r in usable if r["exposed"]])
        txt = np.array([r["log_ratio"] for r in usable if not r["exposed"]])
        test: dict[str, Any] = {
            "n_image_cells": int(img.size),
            "n_text_cells": int(txt.size),
            "mean_log_ratio_image": None if not img.size else round(float(img.mean()), 6),
            "mean_log_ratio_text": None if not txt.size else round(float(txt.mean()), 6),
        }
        if img.size and txt.size:
            observed = float(img.mean() - txt.mean())
            labels = np.array([r["exposed"] for r in usable])
            values = np.array([r["log_ratio"] for r in usable])
            rng = np.random.default_rng(SEED)
            null = np.empty(N_PERMUTATIONS)
            for i in range(N_PERMUTATIONS):
                shuffled = rng.permutation(labels)
                null[i] = values[shuffled].mean() - values[~shuffled].mean()
            p_two = float((np.abs(null) >= abs(observed) - 1e-12).mean())
            p_lower = float((null <= observed + 1e-12).mean())
            test.update({
                "observed_image_minus_text": round(observed, 6),
                "p_value_two_sided": round(p_two, 6),
                "p_value_image_lower": round(p_lower, 6),
                "n_permutations": N_PERMUTATIONS,
                "seed": SEED,
                "interpretation": (
                    "a NEGATIVE observed difference with a small "
                    "p_value_image_lower is the leak's signature: image-bearing "
                    "cells suppressing false positives on the exposed tiles "
                    "relative to the rest of the frame, more than text cells do"
                ),
            })
            # Aggregate rates, the plainer reading of the same table.
            for name, subset in (("image", [r for r in usable if r["exposed"]]),
                                 ("text", [r for r in usable if not r["exposed"]])):
                fe = sum(r["fp_exposed"] for r in subset)
                fr = sum(r["fp_rest"] for r in subset)
                test[f"pooled_{name}"] = {
                    "fp_per_tile_exposed": round(fe / (n_exp * len(subset)), 5),
                    "fp_per_tile_rest": round(fr / (n_rest * len(subset)), 5),
                    "ratio": round((fe / n_exp) / (fr / n_rest), 5) if fr else None,
                }
        boards_out.append({
            "board": board["board"],
            "frame_id": board["frame_id"],
            "n_exposed_tiles": n_exp,
            "n_unexposed_tiles": n_rest,
            "test": test,
            "cells": rows,
        })
        LOG.info("  image mean log-ratio %s vs text %s (p_lower %s)",
                 test.get("mean_log_ratio_image"), test.get("mean_log_ratio_text"),
                 test.get("p_value_image_lower"))

    record = {
        "_README": (
            "The leak-signature test. No reference mound lies in the three null "
            "windows, so the leak can only have suppressed FALSE POSITIVES on "
            "the exposed tiles, and only for cells whose proposer transmitted "
            "the example images. This compares each cell's false-positive rate "
            "on the exposed tiles with its rate on the rest of the same frame, "
            "then asks whether image-bearing cells sit lower than text controls."
        ),
        "generated_by": "scripts/analyse_null_exemplar_sensitivity.py --stage signature",
        "statistic": "log((FP_exposed/n_exposed + 0.5) / (FP_rest/n_rest + 0.5))",
        "boards": boards_out,
    }
    (OUT_DIR / "leak_signature.json").write_text(json.dumps(record, indent=2) + "\n")
    LOG.info("wrote %s", (OUT_DIR / "leak_signature.json").relative_to(BASE_DIR))
    return record


# ── stage: override (register inputs for the board instruments) ───────────

def stage_override(inventory: dict[str, Any]) -> None:
    """Write register overrides pointing the Era-2 board instruments at the
    reduced-frame evaluations.

    ``era1_leaderboard_tiering.py`` and ``selection_aware_intervals.py`` read
    board membership from a run-analyses file and each cell's scoring record
    from the condition's ``eval_path``. Copying both files and rewriting only
    the ``eval_path`` of this board's cells lets the board's own instruments
    run on the reduced frame with NOTHING under ``results/leaderboard/**``
    touched.

    Args:
        inventory: The cell inventory.
    """
    board = next(b for b in inventory["boards"] if b["board"] == "era2-verified")
    conditions = json.loads(CONDITIONS.read_text())
    wanted = {c["ref"]: c for c in board["cells"]}
    n = 0
    for ref, cell in wanted.items():
        run, label = ref.split("::", 1)
        cond = next(c for c in conditions["decomposition"][run]["conditions"]
                    if c["label"] == label)
        rel = (OUT_DIR / "cells" / board["frame_id"] / cell_slug(ref)
               / "evaluation.json").resolve().relative_to(BASE_DIR)
        assert (BASE_DIR / rel).exists(), f"missing reduced evaluation for {ref}"
        cond["eval_path"] = str(rel)
        n += 1
    conditions["_README"] = (
        "OVERRIDE for the null-exemplar sensitivity analysis of 2026-09-13: a "
        "copy of results/run-conditions.json whose "
        f"{n} gs-era2-verified-board-2026-09-10 cells point at their "
        "REDUCED-FRAME evaluations. Not the register."
    )
    dest = OUT_DIR / "tiering-input" / "run-conditions.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(conditions, indent=1) + "\n")
    LOG.info("wrote %s (%d cell eval_paths redirected)",
             dest.relative_to(BASE_DIR), n)

    analyses = json.loads((BASE_DIR / board["analyses"]).read_text())
    analyses["_README"] = (
        "OVERRIDE for the null-exemplar sensitivity analysis of 2026-09-13: a "
        "copy of the board's tiering-input run-analyses.json, unchanged in "
        "membership, carried so the reduced-frame rebuild names its own inputs."
    )
    dest = OUT_DIR / "tiering-input" / "run-analyses.json"
    dest.write_text(json.dumps(analyses, indent=1) + "\n")
    LOG.info("wrote %s", dest.relative_to(BASE_DIR))


# ── stage: swap (paired tile-swap, full and reduced frames) ───────────────

def nearest_text_comparator(board: dict[str, Any],
                            f1_full: dict[str, float]) -> dict[str, str]:
    """Pair each image cell with the text control nearest in full-frame F1.

    "Nearest" is the smallest absolute difference in F1 at the headline
    buffer on the FULL frame, so the pairing is fixed before the reduction and
    cannot be chosen by the result it produces.

    Args:
        board: One board's inventory entry.
        f1_full: Full-frame F1@20 per ref.

    Returns:
        ``{image_ref: text_ref}``.
    """
    texts = [c["ref"] for c in board["cells"]
             if not c["exposed"] and c["ref"] in f1_full]
    pairs = {}
    for cell in board["cells"]:
        if not cell["exposed"] or cell["ref"] not in f1_full or not texts:
            continue
        target = f1_full[cell["ref"]]
        pairs[cell["ref"]] = min(texts, key=lambda t: (abs(f1_full[t] - target), t))
    return pairs


def stage_swap(inventory: dict[str, Any]) -> dict[str, Any]:
    """Paired tile-swap permutation for every image cell against its comparator.

    Args:
        inventory: The cell inventory.

    Returns:
        The swap record (also written to ``paired_tile_swap.json``).
    """
    overlap = load_overlap()
    manifest = json.loads((OUT_DIR / "detections_manifest.json").read_text())
    filtered = {(e["frame_id"], e["ref"]): e for e in manifest["cells"]}
    gdf_ref = gpd.read_file(BASE_DIR / GROUND_TRUTH).to_crs(TARGET_CRS)
    # Per-tile tables are expensive and a cell can sit on more than one board
    # of the same frame, so they are built once per (which, frame, ref).
    cache: dict[tuple[str, str, str], dict[str, Any] | None] = {}
    bounds_cache: dict[str, tuple[gpd.GeoDataFrame, list[str]]] = {}
    boards_out = []
    for board in inventory["boards"]:
        frame = overlap["by_frame"][board["frame_id"]]
        tables: dict[str, dict[str, dict[str, Any]]] = {"full": {}, "reduced": {}}
        for which, bounds_rel in (("full", frame["bounds"]),
                                  ("reduced", frame["reduced_bounds"])):
            if bounds_rel not in bounds_cache:
                gdf = gpd.read_file(BASE_DIR / bounds_rel).to_crs(TARGET_CRS)
                bounds_cache[bounds_rel] = (gdf, list(gdf["tile_name"].unique()))
            gdf_bounds, tile_order = bounds_cache[bounds_rel]
            for cell in board["cells"]:
                key = (which, board["frame_id"], cell["ref"])
                if key not in cache:
                    cond = resolve_condition(CONDITIONS, cell["ref"])
                    cli = cli_of(cond)
                    if which == "reduced":
                        entry = filtered[(board["frame_id"], cell["ref"])]
                        cli = dict(cli)
                        cli["detections"] = [e["filtered"] for e in entry["files"]]
                        cli["detections_dir"] = None
                        cli["glob"] = None
                    try:
                        cache[key] = per_tile_tables(cli, gdf_ref, gdf_bounds,
                                                     tile_order)
                    except (TileJoinRefusalError, ValueError) as error:
                        cache[key] = None
                        LOG.warning("  %s/%s withheld: %s", which, cell["ref"],
                                    str(error)[:100])
                if cache[key] is not None:
                    tables[which][cell["ref"]] = cache[key]

        f1_full = {ref: micro_f1(t["tp"].sum(), t["fp"].sum(), t["fn"].sum())
                   for ref, t in tables["full"].items()}
        pairs = nearest_text_comparator(board, f1_full)
        LOG.info("%s: %d image cell(s) paired against a text comparator",
                 board["board"], len(pairs))

        rows = []
        for image_ref, text_ref in sorted(pairs.items()):
            row: dict[str, Any] = {"image_cell": image_ref, "text_cell": text_ref}
            for which in ("full", "reduced"):
                a = tables[which].get(image_ref)
                b = tables[which].get(text_ref)
                if a is None or b is None:
                    row[which] = {"withheld": True}
                    continue
                f1 = permutation_test_float(
                    a["tp"], a["fp"], a["fn"], b["tp"], b["fp"], b["fn"],
                    n_permutations=N_PERMUTATIONS, seed=SEED)
                block: dict[str, Any] = {
                    "f1_image": round(float(f1["f1_a"]), 6),
                    "f1_text": round(float(f1["f1_b"]), 6),
                    "delta_f1": round(float(f1["observed_diff"]), 6),
                    "p_value_f1": round(float(f1["p_value"]), 6),
                }
                if all(k in a for k in ("ctp", "ctn")) and all(k in b for k in ("ctp", "ctn")):
                    mcc = permutation_test_mcc_arrays(
                        a["ctp"], a["ctn"], a["cfp"], a["cfn"],
                        b["ctp"], b["ctn"], b["cfp"], b["cfn"],
                        n_permutations=N_PERMUTATIONS, seed=SEED)
                    block.update({
                        "mcc_image": round(float(mcc["mcc_a"]), 6),
                        "mcc_text": round(float(mcc["mcc_b"]), 6),
                        "delta_mcc": round(float(mcc["observed_mcc_diff"]), 6),
                        "p_value_mcc": round(float(mcc["p_value"]), 6),
                    })
                row[which] = block
            rows.append(row)
        boards_out.append({"board": board["board"], "frame_id": board["frame_id"],
                           "pairs": rows})

    record = {
        "_README": (
            "Paired round-robin tile-swap permutation (10,000 draws, seed 42) "
            "between each image-bearing cell and its nearest text comparator, "
            "run on the FULL frame and on the REDUCED frame. The pairing is "
            "fixed on the full frame before the reduction, so a change in the "
            "verdict is attributable to the reduction."
        ),
        "generated_by": "scripts/analyse_null_exemplar_sensitivity.py --stage swap",
        "n_permutations": N_PERMUTATIONS,
        "seed": SEED,
        "buffer_metres": HEADLINE_BUFFER,
        "boards": boards_out,
    }
    (OUT_DIR / "paired_tile_swap.json").write_text(json.dumps(record, indent=2) + "\n")
    LOG.info("wrote %s", (OUT_DIR / "paired_tile_swap.json").relative_to(BASE_DIR))
    return record


# ── stage: assemble ──────────────────────────────────────────────────────

def read_eval(path: Path) -> dict[str, Any]:
    """Read F1/precision/recall at the headline buffer and the tile-MCC.

    Args:
        path: An ``evaluation.json`` written by ``evaluate_detections.py``.

    Returns:
        ``{"f1","precision","recall","mcc","n_detections","confusion"}``, with
        None wherever the quantity is withheld or absent.
    """
    doc = json.loads(path.read_text())
    summary = doc["summary"]
    row = next((b for b in summary["buffers"]
                if b.get("buffer_metres") == HEADLINE_BUFFER), None)
    classification = summary.get("tile_classification")
    mcc = None
    confusion = None
    if isinstance(classification, dict):
        confusion = classification.get("confusion")
        raw = classification.get("mcc")
        mcc = raw.get("point") if isinstance(raw, dict) else raw
    return {
        "f1": None if row is None else row.get("f1_point", row.get("f1")),
        "precision": None if row is None else row.get("p_point"),
        "recall": None if row is None else row.get("r_point"),
        "mcc": mcc,
        "n_detections": summary.get("n_detections"),
        "confusion": confusion,
    }


def summarise_deltas(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    """Summarise a delta column over image and text cells.

    Args:
        rows: Per-cell before/after rows.
        key: The delta key, e.g. ``"delta_f1"``.

    Returns:
        Mean and extreme delta per group, with the cell that carries the extreme.
    """
    out: dict[str, Any] = {}
    for name, want in (("image", True), ("text", False)):
        vals = [(r[key], r["ref"]) for r in rows
                if r["exposed"] is want and r.get(key) is not None]
        if not vals:
            out[name] = None
            continue
        arr = np.array([v for v, _ in vals])
        worst = max(vals, key=lambda v: abs(v[0]))
        out[name] = {
            "n": len(vals),
            "mean": round(float(arr.mean()), 6),
            "median": round(float(np.median(arr)), 6),
            "min": round(float(arr.min()), 6),
            "max": round(float(arr.max()), 6),
            "largest_absolute": {"ref": worst[1], "delta": round(worst[0], 6)},
        }
    if out.get("image") and out.get("text"):
        out["image_minus_text_mean"] = round(
            out["image"]["mean"] - out["text"]["mean"], 6)
    return out


def stage_assemble(inventory: dict[str, Any]) -> dict[str, Any]:
    """Build the before/after comparison and write ``analysis.json``.

    Args:
        inventory: The cell inventory.

    Returns:
        The analysis record.
    """
    signature = json.loads((OUT_DIR / "leak_signature.json").read_text())
    swap = json.loads((OUT_DIR / "paired_tile_swap.json").read_text())
    manifest = json.loads((OUT_DIR / "detections_manifest.json").read_text())
    dropped = {(e["frame_id"], e["ref"]): e for e in manifest["cells"]}

    # ── per-cell before -> after ──────────────────────────────────────
    boards_out = []
    for board in inventory["boards"]:
        rows = []
        for cell in board["cells"]:
            before = read_eval(BASE_DIR / cell["eval_path"])
            after_path = (OUT_DIR / "cells" / board["frame_id"]
                          / cell_slug(cell["ref"]) / "evaluation.json")
            after = read_eval(after_path)
            entry = dropped[(board["frame_id"], cell["ref"])]
            row = {
                "ref": cell["ref"],
                "exposed": cell["exposed"],
                "n_detections_before": before["n_detections"],
                "n_detections_after": after["n_detections"],
                "n_features_dropped": entry["n_dropped"],
                "f1_before": before["f1"],
                "f1_after": after["f1"],
                "mcc_before": before["mcc"],
                "mcc_after": after["mcc"],
            }
            if before["f1"] is not None and after["f1"] is not None:
                row["delta_f1"] = round(after["f1"] - before["f1"], 6)
            if before["mcc"] is not None and after["mcc"] is not None:
                row["delta_mcc"] = round(after["mcc"] - before["mcc"], 6)
            rows.append(row)
        boards_out.append({
            "board": board["board"],
            "frame_id": board["frame_id"],
            "n_cells": len(rows),
            "delta_f1": summarise_deltas(rows, "delta_f1"),
            "delta_mcc": summarise_deltas(rows, "delta_mcc"),
            "cells": rows,
        })

    # ── the Era-2 board's tiering, MCB and MCC family ─────────────────
    committed = json.loads(
        (BASE_DIR / ERA2_BOARD / "tiering_20m.json").read_text())
    reduced = json.loads(
        (OUT_DIR / "tiering-reduced" / "tiering_20m.json").read_text())

    def tier_of(doc: dict[str, Any]) -> dict[str, int]:
        return {r["ref"]: r["tier"] for r in doc["ranking"]}

    def mcc_tier_of(doc: dict[str, Any]) -> dict[str, int]:
        return {r["ref"]: r["mcc_tier"]
                for r in doc["mcc_permutation"]["ranking"]}

    before_tier, after_tier = tier_of(committed), tier_of(reduced)
    moved = sorted(ref for ref in before_tier
                   if ref in after_tier and before_tier[ref] != after_tier[ref])
    before_mcc_tier, after_mcc_tier = mcc_tier_of(committed), mcc_tier_of(reduced)
    moved_mcc = sorted(ref for ref in before_mcc_tier
                       if ref in after_mcc_tier
                       and before_mcc_tier[ref] != after_mcc_tier[ref])

    def tier1(doc: dict[str, Any]) -> list[str]:
        return sorted(next(t["members"] for t in doc["tiers"] if t["tier"] == 1))

    def mcc_tier1(doc: dict[str, Any]) -> list[str]:
        return sorted(next(t["members"] for t in doc["mcc_permutation"]["tiers"]
                           if t["tier"] == 1))

    mcb = {}
    for metric, committed_name, reduced_name in (
        ("f1", "gs-era2-verified-board-2026-09-10_b20_m1.json",
         "reduced_f1_b20_m1.json"),
        ("mcc", "gs-era2-verified-board-2026-09-10_mcc_b20_m1.json",
         "reduced_mcc_b20_m1.json"),
    ):
        before_doc = json.loads(
            (BASE_DIR / ERA2_BOARD / "mcb" / committed_name).read_text())
        after_doc = json.loads(
            (OUT_DIR / "mcb-reduced" / reduced_name).read_text())

        def admissible(doc: dict[str, Any]) -> list[str]:
            refs = [c if isinstance(c, str) else c.get("ref", c.get("label"))
                    for c in doc["candidates"]]
            return sorted(r for r, keep in zip(refs, doc["hsu_not_ruled_out"])
                          if keep)

        a_before, a_after = admissible(before_doc), admissible(after_doc)
        mcb[metric] = {
            "n_candidates_before": before_doc["n_candidates"],
            "n_candidates_after": after_doc["n_candidates"],
            "n_tiles_before": before_doc["n_tiles"],
            "n_tiles_after": after_doc["n_tiles"],
            "n_admissible_before": len(a_before),
            "n_admissible_after": len(a_after),
            "admitted_by_reduction": sorted(set(a_after) - set(a_before)),
            "dropped_by_reduction": sorted(set(a_before) - set(a_after)),
            "n_unchanged": len(set(a_before) & set(a_after)),
        }

    # ── swap verdict flips ────────────────────────────────────────────
    flips = []
    for board in swap["boards"]:
        for pair in board["pairs"]:
            full, red = pair.get("full"), pair.get("reduced")
            if not full or not red or full.get("withheld") or red.get("withheld"):
                continue
            for stat in ("f1", "mcc"):
                pf, pr = full.get(f"p_value_{stat}"), red.get(f"p_value_{stat}")
                if pf is None or pr is None:
                    continue
                if (pf < 0.05) != (pr < 0.05):
                    flips.append({
                        "board": board["board"],
                        "image_cell": pair["image_cell"],
                        "text_cell": pair["text_cell"],
                        "statistic": stat,
                        "p_full": pf, "p_reduced": pr,
                        "delta_full": full.get(f"delta_{stat}"),
                        "delta_reduced": red.get(f"delta_{stat}"),
                    })

    # ── a within-run robustness check on the Era-2 signature ──────────
    era2_sig = next(b for b in signature["boards"] if b["board"] == "era2-verified")
    strata = {}
    for row in era2_sig["cells"]:
        if "log_ratio" not in row:
            continue
        strata.setdefault(row["ref"].split("::", 1)[0], []).append(row)
    within_run = {}
    for run, rows in sorted(strata.items()):
        img = [r["log_ratio"] for r in rows if r["exposed"]]
        txt = [r["log_ratio"] for r in rows if not r["exposed"]]
        if not img or not txt:
            continue
        observed = float(np.mean(img) - np.mean(txt))
        labels = np.array([r["exposed"] for r in rows])
        values = np.array([r["log_ratio"] for r in rows])
        rng = np.random.default_rng(SEED)
        null = np.array([
            values[s].mean() - values[~s].mean()
            for s in (rng.permutation(labels) for _ in range(N_PERMUTATIONS))
        ])
        within_run[run] = {
            "n_image": len(img), "n_text": len(txt),
            "mean_log_ratio_image": round(float(np.mean(img)), 6),
            "mean_log_ratio_text": round(float(np.mean(txt)), 6),
            "observed_image_minus_text": round(observed, 6),
            "p_value_image_lower": round(float((null <= observed + 1e-12).mean()), 6),
        }

    record = {
        "_README": (
            "Null-exemplar leak sensitivity analysis, 2026-09-13. Machine-"
            "readable companion to findings.md. Nothing under "
            "results/leaderboard/** is modified: every 'after' number here "
            "comes from this directory's own re-scores on the reduced frames."
        ),
        "analysis_id": "null-exemplar-sensitivity-2026-09-13",
        "generated_by": "scripts/analyse_null_exemplar_sensitivity.py --stage assemble",
        "recipe": {
            "ground_truth": GROUND_TRUTH,
            "buffers": BUFFERS,
            "headline_buffer_m": HEADLINE_BUFFER,
            "bootstrap": BOOTSTRAP,
            "seed": SEED,
            "n_permutations": N_PERMUTATIONS,
            "tile_join": "id (name-based), the published convention",
            "reduction": ("the exposed tiles are dropped from the frame AND "
                          "every detection booked to one is dropped with them"),
        },
        "leak_signature": {
            "boards": [{"board": b["board"], "frame_id": b["frame_id"],
                        "n_exposed_tiles": b["n_exposed_tiles"],
                        "n_unexposed_tiles": b["n_unexposed_tiles"],
                        **b["test"]} for b in signature["boards"]],
            "era2_within_run_strata": within_run,
        },
        "per_cell": boards_out,
        "era2_tiering": {
            "n_tiles_before": committed["n_tiles"],
            "n_tiles_after": reduced["n_tiles"],
            "n_cells_before": committed["n_cells"],
            "n_cells_after": reduced["n_cells"],
            "n_withheld_before": committed["n_cells_withheld"],
            "n_withheld_after": reduced["n_cells_withheld"],
            "n_pairs_significant_before": sum(1 for p in committed["pairwise"]
                                              if p.get("significant")),
            "n_pairs_significant_after": sum(1 for p in reduced["pairwise"]
                                             if p.get("significant")),
            "n_tiers_before": len(committed["tiers"]),
            "n_tiers_after": len(reduced["tiers"]),
            "tie_set_before": sorted(committed["tie_set"]),
            "tie_set_after": sorted(reduced["tie_set"]),
            "tier1_before": tier1(committed),
            "tier1_after": tier1(reduced),
            "tier1_unchanged": tier1(committed) == tier1(reduced),
            "n_cells_changing_tier": len(moved),
            "cells_changing_tier": [
                {"ref": r, "tier_before": before_tier[r], "tier_after": after_tier[r]}
                for r in moved],
        },
        "era2_mcc_family": {
            "n_significant_before": committed["mcc_permutation"]["n_significant"],
            "n_significant_after": reduced["mcc_permutation"]["n_significant"],
            "n_tiers_before": committed["mcc_permutation"]["n_tiers"],
            "n_tiers_after": reduced["mcc_permutation"]["n_tiers"],
            "tie_set_size_before": len(committed["mcc_permutation"]["tie_set"]),
            "tie_set_size_after": len(reduced["mcc_permutation"]["tie_set"]),
            "tier1_before": mcc_tier1(committed),
            "tier1_after": mcc_tier1(reduced),
            "tier1_unchanged": mcc_tier1(committed) == mcc_tier1(reduced),
            "n_cells_changing_mcc_tier": len(moved_mcc),
            "cells_changing_mcc_tier": [
                {"ref": r, "tier_before": before_mcc_tier[r],
                 "tier_after": after_mcc_tier[r]} for r in moved_mcc],
        },
        "era2_mcb": mcb,
        "paired_tile_swap_flips": flips,
    }
    (OUT_DIR / "analysis.json").write_text(json.dumps(record, indent=2) + "\n")
    LOG.info("wrote %s", (OUT_DIR / "analysis.json").relative_to(BASE_DIR))
    LOG.info("F1 tiers %d -> %d; Tier 1 unchanged: %s; cells changing tier: %d",
             record["era2_tiering"]["n_tiers_before"],
             record["era2_tiering"]["n_tiers_after"],
             record["era2_tiering"]["tier1_unchanged"],
             record["era2_tiering"]["n_cells_changing_tier"])
    LOG.info("MCB admissible F1 %d -> %d; MCC %d -> %d",
             mcb["f1"]["n_admissible_before"], mcb["f1"]["n_admissible_after"],
             mcb["mcc"]["n_admissible_before"], mcb["mcc"]["n_admissible_after"])
    LOG.info("MCC Tier 1 unchanged: %s; swap verdict flips: %d",
             record["era2_mcc_family"]["tier1_unchanged"], len(flips))
    return record


# ── CLI ──────────────────────────────────────────────────────────────────

def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True,
                        choices=("inventory", "filter", "rescore", "signature",
                                 "override", "swap", "assemble"),
                        help="Which stage to run.")
    parser.add_argument("--workers", type=int, default=1,
                        help="Concurrent scoring subprocesses for --stage rescore.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.stage == "inventory":
        build_inventory()
        return 0
    inventory = json.loads((OUT_DIR / "cell_inventory.json").read_text())
    if args.stage == "filter":
        stage_filter(inventory)
    elif args.stage == "rescore":
        manifest = json.loads((OUT_DIR / "detections_manifest.json").read_text())
        stage_rescore(manifest, inventory, args.workers)
    elif args.stage == "signature":
        stage_signature(inventory)
    elif args.stage == "override":
        stage_override(inventory)
    elif args.stage == "swap":
        stage_swap(inventory)
    elif args.stage == "assemble":
        stage_assemble(inventory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
