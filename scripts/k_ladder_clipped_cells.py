#!/usr/bin/env python3
"""
Clipped (PI ruling D51) per-tile evaluations for the K ladders whose tile-MCC
the clip withholds
=============================================================================

Description:
    PI ruling D51 compares a ladder's rungs on the area every rung searched:
    where rungs' candidate pools cover different areas, the larger-area rungs'
    detections are clipped to the area common to all rungs, and the frame's
    reference set is kept (option 1). The Phase 2 table builder
    (``scripts/build_k_ladder_phase2_tables.py --clip-to-common-area``)
    re-scores F1 on that basis in memory (``lib_assessed_area.
    rescore_clipped_evaluation``) but writes no clipped detections and no
    clipped evaluation, so it WITHHOLDS tile-MCC, its interval and the per-tile
    table on every clipped point. The K-ladder tile-MCC permutation test
    (``scripts/k_ladder_mcc_test.py``) and the Hsu MCB driver
    (``scripts/k_ladder_mcb.py``) resolve each rung to an evaluation, so on the
    clipped basis they had nothing to read.

    This driver supplies what they read, for the ladders the job card names
    (``planning/paper-writeup-continuity.md``, "Planned: one $0 MCC
    robustness job", part (a); PI ruling D69 decision C):

    * tier E — the grid study's 384 px / 50 % overlap MINIMAL text ladder,
      K = 1, 3, 5, 10 (findings § 8.4);
    * the six Gemini 3 ``pv-diag-384`` Phase 2 ladders the D51 gate clips
      (findings § 4.3, the rows marked with a double dagger).

    The Gemini 3.7 text ladder is also clipped, but its K = 1 and K = 3
    tile-MCC is withheld by the tile-join invariant (findings § 7.3), which a
    clip does not lift, so it is out of scope here.

    It reimplements neither the clip nor the scorer:

    * the common area is the library's own gate
      (``lib_assessed_area.determine_assessed_area`` and
      ``compare_assessed_areas`` with ``clip_to_common``), on each rung's pool
      exactly as the builder resolves it
      (``build_k_ladder_phase2_tables.new_rung_pools`` /
      ``committed_sibling_pools``) and as the tier E driver names it
      (``run_k_ladder_tier_e.rungs`` / ``COMMITTED_K10``);
    * a detection is kept when ``lib_assessed_area.clip_points_to_area`` keeps
      it, and the kept features are written back VERBATIM (the raw GeoJSON
      feature dicts, in their original order), so every property the scorer
      reads (``source_tile``, the origin columns of PI ruling D50) is the
      cell's own; a rung the clip leaves whole is copied byte for byte;
    * each clipped cell is scored by ``scripts/evaluate_detections.py`` with
      the as-evaluated cell's RECORDED recipe (every ``_metadata.cli_args``
      key replayed, as ``reports/s164-agent-records/restatement-pass-scripts/
      kladder/kl_s9_cmds.py`` does), only the detections, output directory
      and label changed.

    **The reference set and frame are kept whole** (D51 option 1, as the
    committed clipped F1 is): the board frame ``era2-b-487`` (487 tiles,
    1,402.41 km²) and the curator reference inside it (435 mounds). So a
    clipped rung's tile-MCC is scored on all 487 tiles, and a tile in the
    clipped-away band that holds a reference mound counts as a false-negative
    tile on every clipped rung, as the 7 mounds there count as false
    negatives in its F1.

    **Gates, in order, each refusing rather than warning:**

    1. ``prepare`` — the D51 area gate over ALL fourteen Phase 2 ladders and
       tier E, with no ``--allow-undetermined-area`` escape: every pool's area
       must be determined from provenance (a partial copy leaves areas
       undetermined; exit 4), every ladder's common area and excess must equal
       its committed record (exit 3), and exactly the seven expected Phase 2
       ladders plus tier E must clip (exit 3). Then, per rung, the number of
       detections the clip removes must equal the committed count, and the
       clipped F1@20 of the WRITTEN file must reproduce the committed clipped
       F1 (exit 5).
    2. ``collect`` — each clipped evaluation's F1@20 must reproduce the
       committed clipped F1 to the committed precision and its detection count
       the kept count (exit 6). Tile-MCC is not read before this passes.
    3. ``report`` — after the two instruments ran: every cell's rebuilt
       micro-F1 equals its evaluation's F1 (``f1_gap``), every cell passed the
       tiering harness's confusion gate, tier E's K = 1, 3, 5 micro-F1 equal
       the committed unrounded clipped values to 6 dp, and, where the clip
       removed nothing, the clipped tile confusion equals the as-evaluated one.

Usage (sapphire, in a whole-tree copy)::

    python scripts/k_ladder_clipped_cells.py prepare
    # run every line of jobs.tsv with scripts/evaluate_detections.py
    python scripts/k_ladder_clipped_cells.py collect
    python scripts/k_ladder_mcc_test.py --ladders OUT/ladders-clipped.json \\
        --conditions OUT/tiering-input/run-conditions.json \\
        --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson \\
        --output-dir OUT/mcc-test
    python scripts/k_ladder_mcb.py --registry OUT/mcb-registry.json \\
        --output-dir OUT/mcb
    python scripts/k_ladder_clipped_cells.py report

Outputs (``OUT`` = ``results/k-ladder-2026-09-12/clipped-mcc-2026-10-30``):
    areas/<slug>.common-assessed-area.geojson, materialised/<label>.geojson,
    cells/<run>__<label>/evaluation.json, prepare.json, jobs.tsv, gate.json,
    tiering-input/run-conditions.json, ladders-clipped.json, mcb-registry.json,
    summary.json

Zero Application Programming Interface (API) calls. All computation is local.

Created: 2026-10-30 (Session 166)
Author: Shawn Ross, Claude Code (Opus 5.5)
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely.geometry import shape

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.lib_assessed_area import (  # noqa: E402
    AREA_CRS,
    COMMON_AREA_CLIP_NAME,
    STATUS_CLIPPED,
    STATUS_SAME,
    AssessedAreaMismatchError,
    AssessedAreaUndeterminedError,
    clip_points_to_area,
    compare_assessed_areas,
    determine_assessed_area,
    write_area_geojson,
)

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

# --- Fixed inputs ------------------------------------------------------------

K_LADDER = Path("results/k-ladder-2026-09-12")
DEFAULT_OUT = K_LADDER / "clipped-mcc-2026-10-30"
PHASE2_LADDERS = K_LADDER / "phase2" / "ladders.json"
TIER_E_LADDER = K_LADDER / "tier-e" / "ladder.json"
PHASE2_MCC_DIR = K_LADDER / "phase2" / "mcc-test"
COMMITTED_MCB = K_LADDER / "mcb" / "summary.json"
GRID_OVERLAP = K_LADDER / "tension" / "grid-overlap.json"

#: Tier E's clipped re-score as committed (the S163 scorer-frames job, at
#: full precision). Its K = 10 row predates the D62 (1) re-verification, so it
#: is used for K = 1, 3 and 5 only (findings § 8.4).
TIER_E_CLIPPED = Path("reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json")

#: The scoring frame every ladder here is on (era2-b-487).
BOARD_BOUNDS = "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"

#: The six Gemini 3 ``pv-diag-384`` ladders whose tile-MCC the clip withholds.
TARGET_PHASE2_POOLS: tuple[str, ...] = (
    "flash-minimal-text-n30-t07-text-t0.3",
    "flash-minimal-text-n30-t07-text-t1.0",
    "flash-high-text-n5-text-t1.0",
    "image-n5-image-t0.3",
    "image-n5-image-t0.7",
    "image-n5-image-t1.0",
)

#: The 3.7 text ladder clips too; it is gated, not rebuilt (module docstring).
G37_POOL = "g384_ov192_g37"

#: Every Phase 2 ladder the D51 gate is expected to clip (the restatement
#: pass's whole-tree run, ``reports/s164-agent-records/restatement-pass.md``
#: § 5 item 8: "the gate determined all areas and clipped seven").
EXPECTED_CLIPPED_PHASE2: frozenset[str] = frozenset({*TARGET_PHASE2_POOLS, G37_POOL})

#: Tier E's slug, run id and the cells' architecture in the conditions sidecar.
TIER_E_SLUG = "d51clip-tier-e"
TIER_E_RUN = "grid-2026-08-18"
PHASE2_RUN = "pv-diag-384"

#: Suffix every clipped cell's label carries, so no clipped condition id can be
#: mistaken for (or resolve to) its as-evaluated twin.
LABEL_SUFFIX = "-d51clip"

#: The recorded ``evaluate_detections.py`` keys this driver knows how to
#: replay; any other key refuses (an unknown recipe is not replayed blind).
KNOWN_RECIPE_KEYS = frozenset({
    "detections", "detections_dir", "batch", "glob", "buffers", "ground_truth",
    "bounds", "bootstrap", "seed", "output_dir", "label", "mcc", "workers",
    "tile_join", "require_clean_inputs",
})

#: Gate tolerances. Committed F1 is recorded to 4 dp (half a unit in the last
#: place); tier E's unrounded clipped F1 is compared to the tiering harness's
#: 6 dp micro-F1 (half a unit in the sixth place).
F1_4DP_TOL = 5e-5
F1_6DP_TOL = 5e-7
#: The committed area record rounds km² to 4 dp.
AREA_TOL_KM2 = 5e-5

#: Exit codes (``lib_assessed_area`` uses 3 and 4 for the area gate).
EXIT_AREA_MISMATCH = 3
EXIT_AREA_UNDETERMINED = 4
EXIT_PREPARE_GATE = 5
EXIT_EVAL_GATE = 6
EXIT_REPORT_GATE = 7


class GateError(RuntimeError):
    """A reproduction gate failed; the run must stop, not explain it away."""


# --- Small helpers -----------------------------------------------------------


def load(path: Path | str) -> Any:
    """Read a JSON file (repository-relative paths are resolved against the repo)."""
    return json.loads(_abs(path).read_text(encoding="utf-8"))


def _abs(path: Path | str) -> Path:
    """A repository-relative path made absolute; an absolute path unchanged."""
    path = Path(path)
    return path if path.is_absolute() else BASE_DIR / path


def _rel(path: Path | str) -> str:
    """A path relative to the repository root when it lies inside it."""
    path = _abs(path)
    try:
        return str(path.relative_to(BASE_DIR))
    except ValueError:
        return str(path)


def sha256(path: Path | str) -> str:
    """SHA-256 of a file's bytes."""
    return hashlib.sha256(_abs(path).read_bytes()).hexdigest()


def phase2_slug(pool: str) -> str:
    """The committed Phase 2 slug convention (``build_k_ladder_phase2_tables``)."""
    return "phase2-" + pool.replace(".", "-").replace("_", "-").lower()


def clipped_slug(pool: str) -> str:
    """The slug a clipped Phase 2 ladder carries in every output here."""
    return "d51clip-" + phase2_slug(pool)


def cell_dir_name(run_id: str, label: str) -> str:
    """Board convention: ``<run_id>__<label with dots as underscores>``."""
    return f"{run_id}__{label.replace('.', '_')}"


def f1_at(evaluation: dict[str, Any], buffer_m: int = 20) -> float | None:
    """An evaluation's F1 at one buffer, as its summary records it."""
    for row in (evaluation.get("summary") or {}).get("buffers") or []:
        if int(row.get("buffer_metres", -1)) == buffer_m:
            return row.get("f1")
    return None


def same_4dp(a: float | None, b: float | None) -> bool:
    """Whether two F1 values agree to 4 dp (half a unit in the last place)."""
    return a is not None and b is not None and abs(float(a) - float(b)) <= F1_4DP_TOL


# --- The clip, written verbatim ----------------------------------------------


def clip_geojson_verbatim(
    source: Path, target: Path, area: Any,
) -> dict[str, Any]:
    """Write ``source``'s detections that the D51 clip keeps to ``target``, verbatim.

    The keep decision is the library's (:func:`lib_assessed_area.
    clip_points_to_area`, which the committed clipped F1 used). The features
    written are the source file's own feature dicts, in their original order,
    so no property and no coordinate is re-serialised; the top-level members
    (``type``, ``name``, ``crs``, …) are kept. A source the clip leaves whole
    is copied byte for byte.

    Args:
        source: The as-evaluated cell's detection GeoJSON.
        target: Where the clipped detections are written.
        area: The common assessed area, in :data:`lib_assessed_area.AREA_CRS`.

    Returns:
        ``{"source", "target", "n_source", "n_kept", "n_removed",
        "source_sha256", "target_sha256", "byte_copy"}``.

    Raises:
        GateError: If the file declares no CRS, or the features geopandas
            reads do not correspond one to one, in order, with the raw ones
            (the mask could then not be applied to the raw features).
    """
    raw = json.loads(source.read_text(encoding="utf-8"))
    features = raw.get("features") or []
    gdf = gpd.read_file(source)
    if gdf.crs is None:
        raise GateError(f"{_rel(source)} declares no CRS; refusing to guess one")
    if len(gdf) != len(features):
        raise GateError(
            f"{_rel(source)}: geopandas read {len(gdf)} features, the file holds "
            f"{len(features)}"
        )
    for index, (feature, geometry) in enumerate(zip(features, gdf.geometry, strict=True)):
        if not shape(feature["geometry"]).equals_exact(geometry, 1e-9):
            raise GateError(
                f"{_rel(source)}: feature {index} differs between the raw file and "
                f"geopandas' reading, so the keep mask cannot be applied verbatim"
            )
    kept, n_removed = clip_points_to_area(gdf.reset_index(drop=True), area)
    keep = set(int(i) for i in kept.index)
    target.parent.mkdir(parents=True, exist_ok=True)
    if n_removed == 0:
        shutil.copyfile(source, target)
    else:
        out = {key: value for key, value in raw.items() if key != "features"}
        out["features"] = [f for i, f in enumerate(features) if i in keep]
        target.write_text(json.dumps(out) + "\n", encoding="utf-8")
    return {
        "source": _rel(source),
        "target": _rel(target),
        "n_source": len(features),
        "n_kept": len(keep),
        "n_removed": int(n_removed),
        "source_sha256": sha256(source),
        "target_sha256": sha256(target),
        "byte_copy": n_removed == 0,
    }


def point_f1(detections: Path, bounds: str, reference: str,
             buffer_m: int = 20) -> dict[str, float]:
    """Point F1 of a detection file, loaded as the committed clipped re-score loads it.

    Mirrors ``lib_assessed_area.rescore_clipped_evaluation`` (CRS handling,
    ``source_tile`` synthesised by a spatial join when absent, the project
    scorer) without its clip and without its rounding, so the written file can
    be checked against the committed value at full precision.

    Args:
        detections: A detection GeoJSON.
        bounds: The frame's tile polygons.
        reference: The reference GeoJSON.
        buffer_m: Match radius.

    Returns:
        ``{"precision", "recall", "f1", "n_detections"}`` unrounded.
    """
    from scripts.lib_advanced_metrics import calculate_f1_internal  # noqa: PLC0415

    gdf_bounds = gpd.read_file(_abs(bounds))
    gdf_bounds = (gdf_bounds.set_crs(AREA_CRS) if gdf_bounds.crs is None
                  else gdf_bounds.to_crs(AREA_CRS))
    gdf_ref = gpd.read_file(_abs(reference))
    gdf_ref = gdf_ref.set_crs(AREA_CRS) if gdf_ref.crs is None else gdf_ref.to_crs(AREA_CRS)
    gdf = gpd.read_file(_abs(detections))
    gdf = gdf.set_crs(AREA_CRS) if gdf.crs is None else gdf.to_crs(AREA_CRS)
    if "source_tile" not in gdf.columns and not gdf.empty:
        joined = gpd.sjoin(gdf, gdf_bounds[["tile_name", "geometry"]],
                           how="left", predicate="intersects")
        joined = joined[~joined.index.duplicated(keep="first")]
        gdf["source_tile"] = joined["tile_name"]
    if gdf.empty:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "n_detections": 0}
    p, r, f = calculate_f1_internal(gdf, gdf_ref, gdf_bounds, buffer_metres=buffer_m)
    return {"precision": float(p), "recall": float(r), "f1": float(f),
            "n_detections": int(len(gdf))}


# --- The recorded recipe -----------------------------------------------------


def recipe_argv(cli: dict[str, Any], *, detections: str, output_dir: str,
                label: str) -> list[str]:
    """``evaluate_detections.py`` arguments replaying a cell's recorded recipe.

    Every recorded key is replayed as ``kl_s9_cmds.argv_for`` does; only the
    detections, the output directory and the label are replaced. A recipe
    with an unknown key, a batch or directory input, a glob, or more than one
    detection file refuses: those are not the single-set cells this driver
    clips.

    Args:
        cli: The as-evaluated cell's ``_metadata.cli_args``.
        detections: The clipped detection file (repository-relative).
        output_dir: The clipped cell's directory (repository-relative).
        label: The clipped cell's label.

    Returns:
        The argument list (without the interpreter or script path).

    Raises:
        GateError: On a recipe this driver cannot replay faithfully.
    """
    unknown = set(cli) - KNOWN_RECIPE_KEYS
    if unknown:
        raise GateError(f"unknown recipe keys {sorted(unknown)}")
    if cli.get("batch") or cli.get("detections_dir") or cli.get("glob"):
        raise GateError("recipe is a batch / directory / glob cell, not a single set")
    recorded = cli.get("detections")
    recorded = [recorded] if isinstance(recorded, str) else list(recorded or [])
    if len(recorded) != 1:
        raise GateError(f"recipe names {len(recorded)} detection files, not one")
    for key in ("buffers", "ground_truth", "bounds", "bootstrap", "seed"):
        if cli.get(key) is None:
            raise GateError(f"recipe records no {key!r}")
    argv = ["--detections", detections,
            "--buffers", *[str(int(b)) for b in cli["buffers"]],
            "--ground-truth", str(cli["ground_truth"]),
            "--bounds", str(cli["bounds"]),
            "--bootstrap", str(int(cli["bootstrap"])),
            "--seed", str(int(cli["seed"])),
            "--output-dir", output_dir,
            "--label", label]
    if cli.get("mcc"):
        argv.append("--mcc")
    if cli.get("tile_join"):
        argv += ["--tile-join", str(cli["tile_join"])]
    if cli.get("require_clean_inputs"):
        argv.append("--require-clean-inputs")
    if cli.get("workers") is not None:
        argv += ["--workers", str(int(cli["workers"]))]
    return argv


# --- Step 1: the area gate ---------------------------------------------------


def phase2_pools(pool: str) -> dict[str, str]:
    """A Phase 2 ladder's rung pools, resolved exactly as the builder resolves them."""
    from scripts.build_k_ladder_phase2_tables import (  # noqa: PLC0415
        committed_sibling_pools,
        new_rung_pools,
    )
    pools = {**new_rung_pools(pool), **committed_sibling_pools(pool)}
    return {f"K = {k}": pools[k] for k in sorted(pools)}


def tier_e_pools() -> dict[str, str]:
    """Tier E's rung pools, as ``run_k_ladder_tier_e.py prepare`` gates them."""
    from scripts.run_k_ladder_tier_e import COMMITTED_K10, rungs  # noqa: PLC0415
    pools = {f"K = {r['n_passes']}": r["crops_dir"] for r in rungs()}
    pools["K = 10"] = COMMITTED_K10["union"]
    return pools


def check_against_record(label: str, record: dict[str, Any],
                         committed: dict[str, Any]) -> list[str]:
    """Differences between a recomputed area record and the committed one.

    Args:
        label: The ladder, for the messages.
        record: ``compare_assessed_areas(...).record``.
        committed: The committed record (same shape; values rounded to 4 dp).

    Returns:
        One message per difference (empty when they agree).
    """
    problems: list[str] = []
    for key in ("common_area_km2", "max_excess_km2", "frame_area_km2"):
        a, b = record.get(key), committed.get(key)
        if a is None or b is None or abs(float(a) - float(b)) > AREA_TOL_KM2:
            problems.append(f"{label}: {key} {a} != committed {b}")
    mine = {p["label"]: p for p in record.get("pools", [])}
    theirs = {p["label"]: p for p in committed.get("pools", [])}
    if set(mine) != set(theirs):
        problems.append(f"{label}: pools {sorted(mine)} != committed {sorted(theirs)}")
        return problems
    for name, pool in mine.items():
        other = theirs[name]
        if pool.get("source") != other.get("source"):
            problems.append(f"{label} {name}: source {pool.get('source')} != "
                            f"committed {other.get('source')}")
        for key in ("effective_area_km2", "excess_over_common_km2"):
            a, b = pool.get(key), other.get(key)
            if a is None or b is None or abs(float(a) - float(b)) > AREA_TOL_KM2:
                problems.append(f"{label} {name}: {key} {a} != committed {b}")
    return problems


def gate_one(label: str, pools: dict[str, str], frame: str) -> Any:
    """Determine and compare one ladder's areas; refuse undetermined pools.

    Unlike the ladder drivers' ``--allow-undetermined-area``, there is no
    escape: an undetermined pool (the partial-copy hazard) exits 4.

    Returns:
        The :class:`lib_assessed_area.AreaComparison`.
    """
    areas = [determine_assessed_area(path, label=name) for name, path in pools.items()]
    try:
        return compare_assessed_areas(areas, frame=frame, clip_to_common=True,
                                      allow_undetermined=False)
    except AssessedAreaUndeterminedError as exc:
        logger.error("D51 gate: %s has an UNDETERMINED pool: %s", label, exc)
        raise SystemExit(EXIT_AREA_UNDETERMINED) from exc
    except AssessedAreaMismatchError as exc:  # pragma: no cover - clip_to_common set
        logger.error("D51 gate refused %s: %s", label, exc)
        raise SystemExit(EXIT_AREA_MISMATCH) from exc


def check_clip_set(statuses: dict[str, str]) -> list[str]:
    """Which ladders clip, against the expected seven Phase 2 ladders.

    Args:
        statuses: Phase 2 proposer pool to gate status.

    Returns:
        One message per discrepancy (empty when exactly the expected set
        clips and every other ladder is the same area).
    """
    problems: list[str] = []
    clipped = {pool for pool, status in statuses.items() if status == STATUS_CLIPPED}
    other = {pool: status for pool, status in statuses.items()
             if status not in (STATUS_CLIPPED, STATUS_SAME)}
    if other:
        problems.append(f"ladders neither clipped nor the same area: {other}")
    if clipped != EXPECTED_CLIPPED_PHASE2:
        problems.append(
            f"clipped {sorted(clipped)} (n = {len(clipped)}), expected "
            f"{sorted(EXPECTED_CLIPPED_PHASE2)} (n = {len(EXPECTED_CLIPPED_PHASE2)})"
        )
    return problems


# --- Step 2: the rungs --------------------------------------------------------


def phase2_rungs(ladder: dict[str, Any]) -> list[dict[str, Any]]:
    """One opmax rung per K of a committed clipped Phase 2 ladder.

    Returns:
        ``[{"K", "label", "as_evaluated_eval_path", "committed_clipped_f1_20",
        "committed_n_removed", "as_evaluated": {...}}, ...]`` ascending in K.

    Raises:
        GateError: If a rung is not on the clipped basis or names no evaluation.
    """
    out = []
    for rung in sorted(ladder["rungs"], key=lambda r: int(r["K"])):
        point = rung["opmax"]
        if point.get("score_basis") != COMMON_AREA_CLIP_NAME:
            raise GateError(f"{ladder['family']} K = {rung['K']}: opmax is not on the "
                            f"clipped basis ({point.get('score_basis')!r})")
        history = point.get("historical_as_evaluated") or {}
        eval_path = point.get("rescored_from_eval_path")
        if not eval_path or eval_path != history.get("eval_path"):
            raise GateError(f"{ladder['family']} K = {rung['K']}: no consistent "
                            f"as-evaluated evaluation")
        label = (rung.get("labels") or {}).get("opmax") or (
            (rung.get("condition_id") or "").split("::", 1)[-1])
        if not label:
            raise GateError(f"{ladder['family']} K = {rung['K']}: no opmax label")
        out.append({
            "K": int(rung["K"]),
            "label": label,
            "vote_t": point.get("vote_t"),
            "prob_t": point.get("prob_t"),
            "as_evaluated_eval_path": eval_path,
            "committed_clipped_f1_20": point["f1_20"],
            "committed_n_removed": point.get("n_removed_by_clip"),
            "committed_n_detections": point.get("n_detections"),
            "committed_full_precision_f1": None,
            "as_evaluated": {"f1_20": history.get("f1_20"),
                             "tile_mcc": history.get("tile_mcc"),
                             "n_detections": history.get("n_detections")},
        })
    return out


def tier_e_rungs() -> list[dict[str, Any]]:
    """Tier E's four rungs with their committed clipped values.

    K = 1, 3 and 5 take the clipped re-score committed in
    :data:`TIER_E_CLIPPED` (unrounded, and its operating point must be the
    rung's); K = 10 is the restated rung, whose clip findings § 8.4 says
    removes nothing, so its committed clipped F1 is its as-evaluated 0.8942
    and the expected removal is 0 (checked, not assumed).

    Raises:
        GateError: If an operating point disagrees with the committed record.
    """
    ladder = load(TIER_E_LADDER)
    clipped = {int(r["K"]): r for r in load(TIER_E_CLIPPED)["tier_e"]["rungs"]}
    out = []
    for rung in ladder["rungs"]:
        k = int(rung["n_passes"])
        entry = {
            "K": k,
            "label": rung["label"],
            "vote_t": rung["vote_threshold"],
            "prob_t": rung["prob_threshold"],
            "as_evaluated_eval_path": rung["eval_path"],
            "as_evaluated": {"f1_20": rung["f1_20"], "tile_mcc": rung["tile_mcc"],
                             "n_detections": rung.get("n_detections")},
        }
        if k == 10:
            entry.update({"committed_clipped_f1_20": rung["f1_20"],
                          "committed_n_removed": 0,
                          "committed_full_precision_f1": None,
                          "committed_source": "findings § 8.4: the restated K = 10 "
                                              "rung's clip removes nothing"})
        else:
            point = clipped[k]["points"]["opmax"]
            if (point["vote_t"], point["prob_t"]) != (entry["vote_t"], entry["prob_t"]):
                raise GateError(f"tier E K = {k}: committed clipped point "
                                f"({point['vote_t']}, {point['prob_t']}) is not the "
                                f"rung's ({entry['vote_t']}, {entry['prob_t']})")
            entry.update({"committed_clipped_f1_20": round(point["d51_clipped"]["f1"], 4),
                          "committed_n_removed": point["d51_clipped"]["n_removed"],
                          "committed_n_detections": point["d51_clipped"]["n_detections"],
                          "committed_full_precision_f1": point["d51_clipped"]["f1"],
                          "committed_source": _rel(TIER_E_CLIPPED)})
        out.append(entry)
    return sorted(out, key=lambda r: r["K"])


def prepare_rung(rung: dict[str, Any], run_id: str, area: Any,
                 out_dir: Path) -> dict[str, Any]:
    """Clip one rung's detections, pre-gate the file, and write its job.

    Returns:
        The rung extended with the clip record, the pre-gate and the job argv.

    Raises:
        GateError: If the removal count or the written file's F1 disagree with
            the committed clipped values.
    """
    evaluation = load(rung["as_evaluated_eval_path"])
    cli = (evaluation.get("_metadata") or {}).get("cli_args") or {}
    recorded = cli.get("detections")
    recorded = [recorded] if isinstance(recorded, str) else list(recorded or [])
    if len(recorded) != 1:
        raise GateError(f"{rung['label']}: recorded detections {recorded}")
    label = rung["label"] + LABEL_SUFFIX
    target = out_dir / "materialised" / f"{label}.geojson"
    clip = clip_geojson_verbatim(_abs(recorded[0]), _abs(target), area)
    where = f"{run_id}::{rung['label']}"
    if rung.get("committed_n_removed") is not None and \
            clip["n_removed"] != int(rung["committed_n_removed"]):
        raise GateError(f"{where}: the clip removed {clip['n_removed']}, the "
                        f"committed re-score removed {rung['committed_n_removed']}")
    if rung.get("committed_n_detections") is not None and \
            clip["n_kept"] != int(rung["committed_n_detections"]):
        raise GateError(f"{where}: the clip kept {clip['n_kept']}, the committed "
                        f"re-score scored {rung['committed_n_detections']}")
    scored = point_f1(_abs(target), cli["bounds"], cli["ground_truth"])
    pre_gate = {"f1_20_written_file": scored["f1"],
                "committed_clipped_f1_20": rung["committed_clipped_f1_20"],
                "passed_4dp": same_4dp(scored["f1"], rung["committed_clipped_f1_20"])}
    if rung.get("committed_full_precision_f1") is not None:
        # The committed record is unrounded; the job card quotes it to 6 dp
        # (0.860360), so the gate is half a unit in the sixth place.
        delta = abs(scored["f1"] - float(rung["committed_full_precision_f1"]))
        pre_gate["full_precision_abs_delta"] = delta
        pre_gate["passed_6dp"] = delta <= F1_6DP_TOL
    if not pre_gate["passed_4dp"] or pre_gate.get("passed_6dp") is False:
        raise GateError(f"{where}: written clipped file scores F1@20 {scored['f1']:.6f}, "
                        f"committed clipped {rung['committed_clipped_f1_20']}")
    cell = out_dir / "cells" / cell_dir_name(run_id, label)
    argv = recipe_argv(cli, detections=_rel(target), output_dir=_rel(cell), label=label)
    return {**rung, "run_id": run_id, "clipped_label": label,
            "condition_id": f"{run_id}::{label}",
            "clipped_detections": _rel(target), "clipped_cell": _rel(cell),
            "clipped_eval_path": _rel(cell / "evaluation.json"),
            "recorded_recipe": cli, "clip": clip, "pre_gate": pre_gate, "argv": argv}


def cmd_prepare(args: argparse.Namespace) -> int:
    """Gate every area, clip every target rung, pre-gate it, and write the jobs."""
    out_dir = _abs(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    committed = load(PHASE2_LADDERS)
    problems: list[str] = []
    statuses: dict[str, str] = {}
    gate_records: dict[str, Any] = {}
    commons: dict[str, Any] = {}
    for ladder in committed["ladders"]:
        pool = ladder["proposer_pool"]
        pools = phase2_pools(pool)
        recorded = {p["label"]: p["source"] for p in ladder["assessed_area"]["pools"]}
        if pools != recorded:
            problems.append(f"{pool}: builder pools {pools} != committed {recorded}")
            continue
        comparison = gate_one(pool, pools, ladder["frame_file"])
        statuses[pool] = comparison.status
        problems += check_against_record(pool, comparison.record, ladder["assessed_area"])
        gate_records[pool] = {"status": comparison.status,
                              "common_area_km2": comparison.record["common_area_km2"],
                              "max_excess_km2": comparison.record["max_excess_km2"],
                              "methods": {p["label"]: p["method"]
                                          for p in comparison.record["pools"]}}
        commons[pool] = comparison
        logger.info("D51 gate %-40s %s (common %.4f km², excess %.4f km²)", pool,
                    comparison.status, comparison.record["common_area_km2"],
                    comparison.record["max_excess_km2"])
    problems += check_clip_set(statuses)
    tier_e = gate_one("tier E", tier_e_pools(), BOARD_BOUNDS)
    problems += check_against_record("tier E", tier_e.record,
                                     load(TIER_E_CLIPPED)["tier_e"]["assessed_area"])
    if tier_e.status != STATUS_CLIPPED:
        problems.append(f"tier E: status {tier_e.status!r}, expected {STATUS_CLIPPED!r}")
    gate_records["tier-e"] = {"status": tier_e.status,
                              "common_area_km2": tier_e.record["common_area_km2"],
                              "max_excess_km2": tier_e.record["max_excess_km2"],
                              "methods": {p["label"]: p["method"]
                                          for p in tier_e.record["pools"]}}
    if problems:
        for line in problems:
            logger.error("AREA GATE: %s", line)
        (out_dir / "prepare.json").write_text(json.dumps(
            {"status": "REFUSED", "problems": problems, "gate": gate_records},
            indent=2) + "\n", encoding="utf-8")
        return EXIT_AREA_MISMATCH

    ladders_out: list[dict[str, Any]] = []
    jobs: list[str] = []
    targets = [(clipped_slug(L["proposer_pool"]), L, PHASE2_RUN, commons[L["proposer_pool"]])
               for L in committed["ladders"] if L["proposer_pool"] in TARGET_PHASE2_POOLS]
    targets.append((TIER_E_SLUG, None, TIER_E_RUN, tier_e))
    try:
        for slug, ladder, run_id, comparison in targets:
            area_file = out_dir / "areas" / f"{slug}.common-assessed-area.geojson"
            write_area_geojson(comparison.common, area_file, name=COMMON_AREA_CLIP_NAME)
            rungs = phase2_rungs(ladder) if ladder is not None else tier_e_rungs()
            prepared = [prepare_rung(r, run_id, comparison.common, out_dir) for r in rungs]
            for rung in prepared:
                jobs.append(rung["clipped_cell"] + "\t" + json.dumps(rung["argv"]))
                logger.info("  %-44s removed %3d kept %3d  F1@20 %.4f (committed %.4f)",
                            rung["condition_id"], rung["clip"]["n_removed"],
                            rung["clip"]["n_kept"], rung["pre_gate"]["f1_20_written_file"],
                            rung["committed_clipped_f1_20"])
            ladders_out.append({
                "slug": slug,
                "family": (ladder or {}).get("family") or
                          "Gemini 3 MINIMAL text 384 px / 50 %, grid pool (tier E)",
                "proposer_pool": (ladder or {}).get("proposer_pool") or "g384_ov192",
                "run_id": run_id,
                "frame_file": BOARD_BOUNDS,
                "reference_file": (ladder or {}).get("reference_file") or
                                  "inputs/vectors/references/mounds-reference.geojson",
                "headline_buffer_m": 20,
                "common_area_geojson": _rel(area_file),
                "assessed_area": comparison.record,
                "rungs": prepared,
            })
    except GateError as exc:
        logger.error("PREPARE GATE: %s", exc)
        (out_dir / "prepare.json").write_text(json.dumps(
            {"status": "REFUSED", "problems": [str(exc)], "gate": gate_records},
            indent=2) + "\n", encoding="utf-8")
        return EXIT_PREPARE_GATE

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/k_ladder_clipped_cells.py",
        "script_version": __version__,
        "status": "PREPARED",
        "ruling": "PI ruling D51 (2026-10-07), option 1: detections clipped to the "
                  "area every rung searched; frame (era2-b-487) and reference set kept",
        "area_gate": {
            "allow_undetermined": False,
            "n_phase2_ladders_gated": len(statuses),
            "n_phase2_ladders_clipped": sum(s == STATUS_CLIPPED for s in statuses.values()),
            "phase2_clipped": sorted(p for p, s in statuses.items() if s == STATUS_CLIPPED),
            "tier_e_status": tier_e.status,
            "per_ladder": gate_records,
            "checked_against": [_rel(PHASE2_LADDERS), _rel(TIER_E_CLIPPED)],
        },
        "ladders": ladders_out,
    }
    (out_dir / "prepare.json").write_text(json.dumps(payload, indent=2) + "\n",
                                          encoding="utf-8")
    (out_dir / "jobs.tsv").write_text("\n".join(jobs) + "\n", encoding="utf-8")
    logger.info("prepared %d cells over %d ladders; jobs in %s", len(jobs),
                len(ladders_out), _rel(out_dir / "jobs.tsv"))
    return 0


# --- Step 3: collect and gate the evaluations ---------------------------------


def evaluation_gate(rung: dict[str, Any]) -> dict[str, Any]:
    """Gate one clipped evaluation's F1 and count, without reading its tile-MCC.

    Returns:
        ``{"condition_id", "f1_20", "committed_clipped_f1_20", "n_detections",
        "n_kept", "passed", "problems"}``.
    """
    path = _abs(rung["clipped_eval_path"])
    problems: list[str] = []
    if not path.exists():
        return {"condition_id": rung["condition_id"], "passed": False,
                "problems": [f"no evaluation at {rung['clipped_eval_path']}"]}
    evaluation = json.loads(path.read_text(encoding="utf-8"))
    f1 = f1_at(evaluation)
    n_det = (evaluation.get("summary") or {}).get("n_detections")
    if not same_4dp(f1, rung["committed_clipped_f1_20"]):
        problems.append(f"F1@20 {f1} != committed clipped {rung['committed_clipped_f1_20']}")
    if n_det != rung["clip"]["n_kept"]:
        problems.append(f"n_detections {n_det} != kept {rung['clip']['n_kept']}")
    cli = (evaluation.get("_metadata") or {}).get("cli_args") or {}
    scored = cli.get("detections")
    scored = [scored] if isinstance(scored, str) else list(scored or [])
    if scored != [rung["clipped_detections"]]:
        problems.append(f"evaluation scored {scored}, not [{rung['clipped_detections']}]")
    if "tile_classification" not in (evaluation.get("summary") or {}):
        problems.append("evaluation carries no tile_classification block")
    return {"condition_id": rung["condition_id"], "f1_20": f1,
            "committed_clipped_f1_20": rung["committed_clipped_f1_20"],
            "n_detections": n_det, "n_kept": rung["clip"]["n_kept"],
            "passed": not problems, "problems": problems}


def conditions_sidecar(ladders: list[dict[str, Any]]) -> dict[str, Any]:
    """A ``run-conditions.json``-shaped sidecar naming only the clipped cells.

    The tiering harness and the MCB tool resolve ``<run>::<label>`` through a
    conditions file's ``decomposition``; this one holds the clipped cells
    alone, so neither can resolve a clipped id to an as-evaluated cell.
    """
    decomposition: dict[str, Any] = {}
    for ladder in ladders:
        for rung in ladder["rungs"]:
            run = decomposition.setdefault(rung["run_id"], {"conditions": []})
            run["conditions"].append({
                "label": rung["clipped_label"],
                "architecture": "proposer-verifier",
                "aggregation": "verified",
                "proposer_pool": ladder["proposer_pool"],
                "n_passes": rung["K"],
                "vote_threshold": rung["vote_t"],
                "prob_threshold": rung["prob_t"],
                "eval_path": rung["clipped_eval_path"],
                "detections": rung["clipped_detections"],
                "_note": (f"D51-clipped twin of {rung['run_id']}::{rung['label']} "
                          f"({rung['as_evaluated_eval_path']}): its detections "
                          f"clipped to the ladder's common assessed area, frame and "
                          f"reference kept. NOT REGISTERED."),
            })
    return {
        "_README": ("TIERING INPUT — NOT REGISTERED. The D51-clipped K-ladder cells, "
                    "written by scripts/k_ladder_clipped_cells.py so "
                    "scripts/k_ladder_mcc_test.py and scripts/k_ladder_mcb.py can "
                    "read them. results/run-conditions.json is not modified and this "
                    "file must never be written over it."),
        "schema_version": "1.0",
        "decomposition": decomposition,
    }


def mcc_inventory(ladders: list[dict[str, Any]]) -> dict[str, Any]:
    """The clipped ladders in the Phase-1 inventory schema ``k_ladder_mcc_test`` reads.

    ``f1_headline`` is the clipped F1@20, so the driver's best rung is the
    clipped basis's best rung. ``tile_mcc`` is the clipped evaluation's.
    """
    out = []
    for ladder in ladders:
        rungs = []
        for rung in ladder["rungs"]:
            evaluation = load(rung["clipped_eval_path"])
            mcc = ((evaluation["summary"].get("tile_classification") or {})
                   .get("mcc") or {}).get("point")
            rungs.append({"K": rung["K"], "condition_id": rung["condition_id"],
                          "eval_path": rung["clipped_eval_path"],
                          "f1_headline": f1_at(evaluation), "f1_20": f1_at(evaluation),
                          "tile_mcc": mcc,
                          "n_detections": evaluation["summary"].get("n_detections"),
                          "vote_threshold": rung["vote_t"],
                          "prob_threshold": rung["prob_t"]})
        out.append({"slug": ladder["slug"],
                    "family": f"{ladder['family']} [opmax, D51 clipped]",
                    "family_base": ladder["family"],
                    "operating_point_basis": "opmax",
                    "score_basis": COMMON_AREA_CLIP_NAME,
                    "run_id": ladder["run_id"], "proposer_pool": ladder["proposer_pool"],
                    "corpus": "4-map-gs", "frame_file": ladder["frame_file"],
                    "reference_file": ladder["reference_file"],
                    "headline_buffer_m": ladder["headline_buffer_m"],
                    "r1_verifier": True, "rungs": rungs})
    return {"generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "script": "scripts/k_ladder_clipped_cells.py",
            "schema_note": ("Phase-1 ladders.json schema on PI ruling D51's clipped "
                            "basis, for scripts/k_ladder_mcc_test.py --ladders"),
            "n_ladders": len(out), "ladders": out}


def mcb_registry(ladders: list[dict[str, Any]], out_dir: Path) -> list[dict[str, Any]]:
    """Registry entries for ``k_ladder_mcb.py --registry`` over the clipped ladders.

    Each entry reads the analysis row ``k_ladder_mcc_test.py`` writes and is
    gated against the clipped tiering that run produces, exactly as the
    committed registry gates against the committed tierings.
    """
    out = []
    for ladder in ladders:
        slug = ladder["slug"]
        out.append({
            "slug": slug,
            "analysis_id": f"k-ladder-mcc-{slug}-2026-09-12",
            "analyses": _rel(out_dir / "mcc-test" / "tiering-input" / slug /
                             "run-analyses.json"),
            "conditions": _rel(out_dir / "tiering-input" / "run-conditions.json"),
            "bounds": BOARD_BOUNDS,
            "buffer_m": 20,
            "tiering": _rel(out_dir / "mcc-test" / "tiering" / slug / "tiering_20m.json"),
            "group": "D51 clipped",
            "family": f"{ladder['family']} (D51 clipped)",
            "k_by_label": {r["clipped_label"]: r["K"] for r in ladder["rungs"]},
        })
    return out


def cmd_collect(args: argparse.Namespace) -> int:
    """Gate every clipped evaluation, then write the instruments' inputs."""
    out_dir = _abs(args.output_dir)
    prepared = load(out_dir / "prepare.json")
    if prepared.get("status") != "PREPARED":
        logger.error("prepare.json status is %r", prepared.get("status"))
        return EXIT_PREPARE_GATE
    gates = [evaluation_gate(rung) for ladder in prepared["ladders"]
             for rung in ladder["rungs"]]
    passed = all(g["passed"] for g in gates)
    (out_dir / "gate.json").write_text(json.dumps({
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate": "each clipped evaluation's F1@20 reproduces the committed clipped F1 "
                "to 4 dp and its detection count the clip's kept count",
        "passed": passed, "n_cells": len(gates), "cells": gates,
    }, indent=2) + "\n", encoding="utf-8")
    for g in gates:
        logger.info("  %-48s %s %s", g["condition_id"], "PASS" if g["passed"] else "FAIL",
                    "; ".join(g.get("problems") or []))
    if not passed:
        logger.error("EVALUATION GATE FAILED: nothing downstream is written")
        return EXIT_EVAL_GATE
    sidecar = out_dir / "tiering-input" / "run-conditions.json"
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text(json.dumps(conditions_sidecar(prepared["ladders"]), indent=2) + "\n",
                       encoding="utf-8")
    (out_dir / "ladders-clipped.json").write_text(
        json.dumps(mcc_inventory(prepared["ladders"]), indent=2) + "\n", encoding="utf-8")
    (out_dir / "mcb-registry.json").write_text(
        json.dumps(mcb_registry(prepared["ladders"], out_dir), indent=2) + "\n",
        encoding="utf-8")
    logger.info("evaluation gate PASSED on %d cells; instrument inputs written", len(gates))
    return 0


# --- Step 4: the report ---------------------------------------------------------


def _pair(tiering: dict[str, Any], key: str, k_of: dict[str, int], k_lo: int,
          k_hi: int) -> dict[str, Any]:
    """One pair of a tiering's round-robin, oriented as (higher K) - (lower K)."""
    rows = tiering["pairwise"] if key == "f1" else tiering["mcc_permutation"]["pairwise"]
    stat = "observed_diff" if key == "f1" else "observed_mcc_diff"
    for row in rows:
        ka, kb = k_of[row["ref_a"]], k_of[row["ref_b"]]
        if {ka, kb} == {k_lo, k_hi}:
            sign = 1.0 if ka == k_hi else -1.0
            return {"delta": round(sign * row[stat], 6), "p_raw": row["p_value"],
                    "p_bh": row["bh_adjusted_p"], "significant": row["significant"]}
    raise KeyError(f"pair K{k_lo}-K{k_hi} absent")


def report_gates(prepared: dict[str, Any], out_dir: Path) -> list[str]:
    """The post-instrument gates; one message per failure."""
    problems: list[str] = []
    for ladder in prepared["ladders"]:
        tiering = load(out_dir / "mcc-test" / "tiering" / ladder["slug"] / "tiering_20m.json")
        ranking = {row["ref"]: row for row in tiering["ranking"]}
        cell_gates = tiering["mcc_permutation"]["gates"]
        if tiering.get("n_cells_withheld") or tiering["mcc_permutation"].get("withheld"):
            problems.append(f"{ladder['slug']}: the harness withheld a cell")
        for rung in ladder["rungs"]:
            ref = rung["condition_id"]
            row = ranking.get(ref)
            if row is None:
                problems.append(f"{ref}: absent from the tiering")
                continue
            if abs(row["f1_gap"]) > F1_4DP_TOL:
                problems.append(f"{ref}: rebuilt micro-F1 gap {row['f1_gap']}")
            if not (cell_gates.get(ref) or {}).get("passed"):
                problems.append(f"{ref}: confusion gate did not pass")
            if rung.get("committed_full_precision_f1") is not None:
                delta = abs(row["observed_micro_f1"] -
                            round(float(rung["committed_full_precision_f1"]), 6))
                if delta > F1_6DP_TOL:
                    problems.append(f"{ref}: micro-F1 {row['observed_micro_f1']} != "
                                    f"committed {rung['committed_full_precision_f1']:.6f}")
            if rung["clip"]["n_removed"] == 0:
                clipped = load(rung["clipped_eval_path"])["summary"]["tile_classification"]
                original = load(rung["as_evaluated_eval_path"])["summary"].get(
                    "tile_classification") or {}
                if clipped.get("confusion") != original.get("confusion"):
                    problems.append(f"{ref}: nothing clipped, yet the confusion "
                                    f"{clipped.get('confusion')} differs from the "
                                    f"as-evaluated {original.get('confusion')}")
    return problems


def committed_unclipped(slug: str) -> dict[str, Any]:
    """The committed (as-evaluated) MCC test and MCB readings for a clipped ladder."""
    mcb = {lad["slug"]: lad for lad in load(COMMITTED_MCB)["ladders"]}
    if slug == TIER_E_SLUG:
        ladder = load(TIER_E_LADDER)
        k_of = {f"{TIER_E_RUN}::{r['label']}": int(r["n_passes"]) for r in ladder["rungs"]}
        best = max(ladder["rungs"], key=lambda r: r["f1_20"])
        k_best = int(best["n_passes"])
        tiering = {"pairwise": ladder["pairwise_f1"],
                   "mcc_permutation": {"pairwise": ladder["pairwise_mcc"]}}
        k1_best_mcc = _pair(tiering, "mcc", k_of, 1, k_best)
        k1_best_f1 = _pair(tiering, "f1", k_of, 1, k_best)
        k1_k10_mcc = _pair(tiering, "mcc", k_of, 1, 10)
        k1_k10_f1 = _pair(tiering, "f1", k_of, 1, 10)
        block = mcb.get("tier-e") or {}
        return {"source": [_rel(TIER_E_LADDER), _rel(COMMITTED_MCB)], "best_K": k_best,
                "k1_to_best": {"f1": k1_best_f1, "mcc": k1_best_mcc},
                "k1_to_k10": {"f1": k1_k10_f1, "mcc": k1_k10_mcc},
                "mcb_f1_set": (block.get("f1") or {}).get("hsu_admissible_K"),
                "mcb_mcc_set": (block.get("mcc") or {}).get("hsu_admissible_K"),
                "mcb_mcc_best_K": (block.get("mcc") or {}).get("best_K")}
    base = slug.removeprefix("d51clip-")
    test = load(PHASE2_MCC_DIR / f"{base}.json")
    head = next(r for r in test["pairs"] if "k1-vs-best" in r["kind"])
    block = mcb.get(base) or {}
    return {"source": [_rel(PHASE2_MCC_DIR / f"{base}.json"), _rel(COMMITTED_MCB)],
            "best_K": head["k_high"],
            "k1_to_best": {"f1": {k: head["f1"][k] for k in ("delta", "p_raw", "p_bh",
                                                             "significant")},
                           "mcc": {k: head["mcc"][k] for k in ("delta", "p_raw", "p_bh",
                                                               "significant")}},
            "mcb_f1_set": (block.get("f1") or {}).get("hsu_admissible_K"),
            "mcb_mcc_set": (block.get("mcc") or {}).get("hsu_admissible_K"),
            "mcb_mcc_best_K": (block.get("mcc") or {}).get("best_K")}


def direction(delta: float | None, eps: float = 0.005) -> str:
    """The § 4 verdict word for a tile-MCC change (|Δ| below ``eps`` reads flat)."""
    if delta is None:
        return "—"
    if abs(delta) < eps:
        return "flat"
    return "up" if delta > 0 else "down"


def cmd_report(args: argparse.Namespace) -> int:
    """Gate the instruments' outputs and collate the clipped-versus-unclipped summary."""
    out_dir = _abs(args.output_dir)
    prepared = load(out_dir / "prepare.json")
    problems = report_gates(prepared, out_dir)
    mcb = {lad["slug"]: lad for lad in load(out_dir / "mcb" / "summary.json")["ladders"]}
    if not load(out_dir / "mcb" / "summary.json").get("gate_all_passed"):
        problems.append("the MCB driver's own gate did not pass")
    if not load(out_dir / "mcc-test" / "summary.json").get("gate_all_passed"):
        problems.append("the MCC test driver's own gate did not pass")
    ladders = []
    for ladder in prepared["ladders"]:
        slug = ladder["slug"]
        tiering = load(out_dir / "mcc-test" / "tiering" / slug / "tiering_20m.json")
        k_of = {r["condition_id"]: r["K"] for r in ladder["rungs"]}
        ranking = {row["ref"]: row for row in tiering["ranking"]}
        rungs = []
        for rung in ladder["rungs"]:
            evaluation = load(rung["clipped_eval_path"])
            tile = evaluation["summary"]["tile_classification"]
            rungs.append({
                "K": rung["K"], "condition_id": rung["condition_id"],
                "operating_point": [rung["vote_t"], rung["prob_t"]],
                "n_removed_by_clip": rung["clip"]["n_removed"],
                "n_detections": rung["clip"]["n_kept"],
                "f1_20_clipped": f1_at(evaluation),
                "f1_20_clipped_micro_6dp": ranking[rung["condition_id"]]["observed_micro_f1"],
                "f1_20_as_evaluated": rung["as_evaluated"]["f1_20"],
                "tile_mcc_clipped": (tile.get("mcc") or {}).get("point"),
                "tile_mcc_clipped_ci": [(tile.get("mcc") or {}).get("ci_lower"),
                                        (tile.get("mcc") or {}).get("ci_upper")],
                "tile_confusion_clipped": tile.get("confusion"),
                "tile_mcc_as_evaluated": rung["as_evaluated"]["tile_mcc"],
                "clipped_eval_path": rung["clipped_eval_path"],
            })
        best = max(rungs, key=lambda r: r["f1_20_clipped"])
        k_best = best["K"]
        clipped = {
            "best_K": k_best,
            "k1_to_best": {"f1": _pair(tiering, "f1", k_of, 1, k_best),
                           "mcc": _pair(tiering, "mcc", k_of, 1, k_best)},
            "k1_to_k10": {"f1": _pair(tiering, "f1", k_of, 1, 10),
                          "mcc": _pair(tiering, "mcc", k_of, 1, 10)},
            "all_pairs": [
                {"pair": f"K{a}-vs-K{b}", "f1": _pair(tiering, "f1", k_of, a, b),
                 "mcc": _pair(tiering, "mcc", k_of, a, b)}
                for i, a in enumerate(sorted(k_of.values()))
                for b in sorted(k_of.values())[i + 1:]],
            "mcb_f1_set": (mcb[slug].get("f1") or {}).get("hsu_admissible_K"),
            "mcb_mcc_set": (mcb[slug].get("mcc") or {}).get("hsu_admissible_K"),
            "mcb_mcc_best_K": (mcb[slug].get("mcc") or {}).get("best_K"),
            "mcb_w_upper": {"f1": (mcb[slug].get("f1") or {}).get("hsu_w_upper"),
                            "mcc": (mcb[slug].get("mcc") or {}).get("hsu_w_upper")},
        }
        clipped["mcc_direction_k1_to_best"] = direction(clipped["k1_to_best"]["mcc"]["delta"])
        unclipped = committed_unclipped(slug)
        unclipped["mcc_direction_k1_to_best"] = direction(
            unclipped["k1_to_best"]["mcc"]["delta"])
        ladders.append({"slug": slug, "family": ladder["family"],
                        "n_removed_by_clip": [r["n_removed_by_clip"] for r in rungs],
                        "rungs": rungs, "clipped": clipped, "as_evaluated": unclipped})

    tier_e = next(lad for lad in ladders if lad["slug"] == TIER_E_SLUG)
    grid = next(c for c in load(GRID_OVERLAP)["cells"] if c["cell"] == "g384_ov192")
    consensus_mcc = grid["rungs"]["10"]["mcc"] - grid["rungs"]["1"]["mcc"]
    consensus_f1 = grid["rungs"]["10"]["f1_20"] - grid["rungs"]["1"]["f1_20"]
    verified = tier_e["clipped"]["k1_to_k10"]
    section_8_6 = {
        "consensus_only": {"delta_f1_k1_to_k10": round(consensus_f1, 6),
                           "delta_mcc_k1_to_k10": round(consensus_mcc, 6),
                           "source": _rel(GRID_OVERLAP) + " cells[g384_ov192]",
                           "reference": "428 mounds on the grid study's common footprint"},
        "verified_clipped": {"delta_f1_k1_to_k10": verified["f1"]["delta"],
                             "delta_mcc_k1_to_k10": verified["mcc"]["delta"],
                             "mcc_p_bh": verified["mcc"]["p_bh"],
                             "reference": "435 mounds in era2-b-487 (D51 option 1)"},
        "verified_as_evaluated": tier_e["as_evaluated"]["k1_to_k10"],
        "sign_reversal_survives_clip": bool(
            consensus_mcc > 0 and verified["mcc"]["delta"] < 0),
        "mcc_swing_clipped": round(consensus_mcc - verified["mcc"]["delta"], 6),
        "f1_reduction_clipped": round(1 - verified["f1"]["delta"] / consensus_f1, 6),
    }
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/k_ladder_clipped_cells.py",
        "script_version": __version__,
        "basis": ("PI ruling D51 option 1: detections clipped to each ladder's common "
                  "assessed area; frame era2-b-487 (487 tiles) and the curator "
                  "reference inside it (435 mounds) kept whole"),
        "report_gate": {"passed": not problems, "problems": problems},
        "area_gate": prepared["area_gate"],
        "section_8_6": section_8_6,
        "ladders": ladders,
    }
    (out_dir / "summary.json").write_text(json.dumps(payload, indent=2) + "\n",
                                          encoding="utf-8")
    for line in problems:
        logger.error("REPORT GATE: %s", line)
    logger.info("summary written; report gate %s", "PASSED" if not problems else "FAILED")
    return 0 if not problems else EXIT_REPORT_GATE


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=("prepare", "collect", "report"))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    return {"prepare": cmd_prepare, "collect": cmd_collect, "report": cmd_report}[
        args.command](args)


if __name__ == "__main__":
    sys.exit(main())
