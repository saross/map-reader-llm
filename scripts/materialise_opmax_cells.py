#!/usr/bin/env python3
"""Re-materialise the GS Era-2 board's mis-materialised ``-opmax`` cells from their registered stage.

Why
---
The 40 ``-opmax`` rows on the GS Era-2 verified board
(``planning/gs-era2-verified-board-2026-09-08.md``, changelog 2026-09-10)
are the archived per-architecture Era-2 PV board's sweep-optimal Gemini 3
cells.  Each was registered at the F1@20-argmax ``(vote_t, prob_t)`` of its
stage's own threshold sweep, and each carries a materialised detection
GeoJSON produced on 2026-04-19 (commit ``bd24293d4``).

Nine of the 40 carry a materialised file that does NOT hold the point the
registry registered (``membership.json`` marks them ``registry_vs_archived``
= ``differs …``; Obs 464-465).  The diagnosis (2026-09-10): joining the
proposer pool union (``consensus_path`` in the materialisation registry) to
the verifier stage's ``probabilities.json`` by candidate index — union
feature ``i`` <-> results key ``candidate_{i:05d}`` — and filtering

    vote_count >= vote_t  AND  mound_probability >= prob_t

at the REGISTERED point reproduces the registry's detection count exactly for
all nine, while the archived file holds a different set.  The union, the
probabilities and the sweep are all unchanged since 2026-04-17/18; only the
2026-04-19 materialisation moved.  The materialisation, not the registry, is
the defective side, so this script rebuilds the nine from the inputs.

What it does
------------
1. Reads the board's ``opmax/membership.json`` (the source of truth for each
   row's stage and registered ``(vote_t, prob_t)``) and the two archived
   materialisation registries.
2. Applies the filter above to EVERY membership row — the nine plus the 31
   other on-board cells and the 3 off-board (K = 3) cells — and compares the
   resulting count with the archived file's feature count.
3. Writes a fresh GeoJSON plus a provenance sidecar for the nine only
   (``--write``).  Every other row is reported, never rewritten: a mismatch
   there is a finding for the operator, not something this script decides.

The nine are DERIVED, not hard-coded: a row is re-materialised when its
``registry_vs_archived`` field starts with ``differs``.  Keep
``scripts/build_gs_era2_board_opmax.py membership`` as the source of truth
for that field.

Two candidate-pool shapes exist among the rows and both are handled:

``pv_registry.json`` rows
    Union = the proposer consensus GeoJSON at threshold 1
    (``consensus_path``); index-aligned to ``probabilities.json``.
``session-78-matrix-registry.json`` rows
    Union = the shared-crops ``candidate_manifest.json``; keyed by the
    manifest's own ``candidate_id`` and additionally restricted to the
    487-tile Era-2 bounds allowlist, exactly as
    ``scripts/materialise_session78_geojsons.py`` did.

Outputs (``--write``)
---------------------
``<board>/opmax/materialised/<label>.geojson``
    EPSG:4326 (the unions carry lat/lon coordinates and declare no CRS; the
    output declares 4326 explicitly so no loader has to guess).  Each
    feature keeps the union's properties and gains ``mound_probability``,
    ``vote_t``, ``prob_t``, ``source_stage``, ``candidate_id`` and the
    singular ``source_tile`` the evaluator needs.
``<board>/opmax/materialised/<label>.provenance.json``
    Inputs with their git blob hashes, the registered point, the counts
    (computed / registry / archived) and the check verdict.
``<board>/opmax/materialised/check.json``
    The all-rows check report (written on ``--write`` and on a dry run).

Usage::

    python scripts/materialise_opmax_cells.py              # dry run: report only
    python scripts/materialise_opmax_cells.py --write      # write the nine + sidecars

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

BOARD_DIR = "results/leaderboard/era2/gs-era2-verified-board-2026-09-10"
OPMAX_DIR = f"{BOARD_DIR}/opmax"
OUT_DIR = f"{OPMAX_DIR}/materialised"
MEMBERSHIP = f"{OPMAX_DIR}/membership.json"

ARCHIVE = "archive/superseded-leaderboards/leaderboard"
MATERIALISED = f"{ARCHIVE}/era2/pv-materialised"
PV_REGISTRY = f"{MATERIALISED}/pv_registry.json"
S78_REGISTRY = f"{MATERIALISED}/session-78-matrix-registry.json"

# The Era-2 evaluation frame: the scope the session-78 materialiser applied as
# a tile allowlist, and the frame the archived board's sweeps were scored on
# (scripts/run_verifier_matrix.sh BOUNDS).
ERA2_FRAME = "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"

# Session-78 shared-crops pools (mirrors materialise_session78_geojsons.py).
S78_POOL_BASE = {
    "image": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7",
    "text": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
}

# GeoJSON URN for the unions' (undeclared) storage CRS. RFC 7946 makes WGS84
# the default for a crs-less GeoJSON; declaring it removes the guess.
OUTPUT_CRS_URN = "urn:ogc:def:crs:EPSG::4326"


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------


def _load(rel: str | Path) -> Any:
    """Load a repository-relative JSON file."""
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


def git_blob_hash(rel: str) -> str | None:
    """Git blob hash of a repository file's CURRENT content, or ``None``.

    ``git hash-object`` is content-addressed, so this anchors a provenance
    record to the exact bytes read even for paths that are not tracked.
    """
    path = REPO_ROOT / rel
    if not path.is_file():
        return None
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "hash-object", str(path)],
            capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):  # pragma: no cover - git always present here
        return None
    return out.stdout.strip() or None


def git_last_commit(rel: str) -> dict[str, str] | None:
    """``{commit, date, subject}`` of the last commit touching ``rel``."""
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "log", "-1", "--date=short",
             "--pretty=format:%h\x02%ad\x02%s", "--", rel],
            capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):  # pragma: no cover
        return None
    if not out.stdout.strip():
        return None
    commit, date, subject = out.stdout.strip().split("\x02", 2)
    return {"commit": commit, "date": date, "subject": subject}


def era2_tile_allowlist() -> set[str]:
    """Tile names of the 487-tile Era-2 evaluation frame.

    Read straight from the GeoJSON rather than through geopandas: the only
    field needed is ``tile_name`` and this keeps the script import-light.
    """
    doc = _load(ERA2_FRAME)
    return {f["properties"]["tile_name"] for f in doc["features"]}


# ---------------------------------------------------------------------------
# the vintage guard
# ---------------------------------------------------------------------------


def sweep_universe(sweep_rel: str | None) -> int | None:
    """The candidate count a committed 2-D sweep saw.

    A sweep's ``(vote_t 1, prob_t 0.0)`` cell keeps every candidate, so its
    ``n`` IS the universe the sweep ran over — the cheapest available witness
    of the vintage the stage's inputs had when it was swept.

    Args:
        sweep_rel: Repository-relative ``sweep_2d.json``, or ``None``.

    Returns:
        The universe size, or ``None`` when there is no sweep or no such row.
    """
    if not sweep_rel or not (REPO_ROOT / sweep_rel).is_file():
        return None
    for row in _load(sweep_rel):
        if row.get("buffer_m", 20) == 20 and row.get("vote_t") == 1 \
                and float(row.get("prob_t", -1)) == 0.0:
            return int(row["n"])
    return None


def classify_vintage(n_union: int, n_probabilities: int,
                     n_sweep: int | None) -> tuple[str, str]:
    """Classify a cell's index join by its three universe sizes.

    The join union feature *i* <-> results key ``candidate_{i:05d}`` is only
    meaningful while the union still holds the features, in the order, the
    verifier cropped. Two ways it stops being so:

    ``probabilities-grew``
        ``n_sweep < n_union == n_probabilities``. The probabilities were
        completed after the sweep ran (Obs 461). The join stays SOUND; only
        the sweep is stale.
    ``union-rebuilt``
        ``n_probabilities < n_union``. The union file was re-materialised
        after the verifier ran, so its feature order no longer matches the
        keys and the join is INVALID — any count it produces is noise.

    Args:
        n_union: Features in the union GeoJSON as committed today.
        n_probabilities: Keys in the verifier stage's ``probabilities.json``.
        n_sweep: The sweep's own universe size, or ``None``.

    Returns:
        ``(verdict, explanation)``; ``verdict`` is ``same-vintage``,
        ``probabilities-grew``, ``union-rebuilt`` or ``unknown``.
    """
    if n_probabilities < n_union:
        return "union-rebuilt", (
            f"the union holds {n_union} features but the stage verified only "
            f"{n_probabilities}: the union at this path was re-materialised after the "
            "verifier ran, so feature order no longer matches the probability keys and "
            "the index join is invalid")
    if n_sweep is None:
        return "unknown", "no committed sweep records a (vote_t 1, prob_t 0.0) row"
    if n_sweep == n_union == n_probabilities:
        return "same-vintage", "sweep, union and probabilities agree on the universe size"
    if n_sweep < n_union == n_probabilities:
        return "probabilities-grew", (
            f"the sweep saw {n_sweep} of the {n_union} candidates now verified: the "
            "probabilities were completed after the sweep ran (Obs 461 class). The index "
            "join stays sound; the sweep is stale")
    return "unknown", (f"unexpected shape: sweep {n_sweep}, union {n_union}, "
                       f"probabilities {n_probabilities}")


# ---------------------------------------------------------------------------
# the filter
# ---------------------------------------------------------------------------


def filter_pv_union(
    consensus_path: str,
    probabilities_path: str,
    vote_t: int,
    prob_t: float,
    source_stage: str,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Filter a proposer-consensus union by the registered operating point.

    The union's feature order IS the verifier manifest order, so union index
    ``i`` addresses results key ``candidate_{i:05d}``.  A candidate with no
    probability entry is dropped (it was never verified); a feature with no
    ``vote_count`` is treated as zero votes and so dropped unless
    ``vote_t <= 0`` — both fail closed.

    Args:
        consensus_path: Repository-relative proposer consensus GeoJSON
            (threshold 1, canonical feature order).
        probabilities_path: Repository-relative verifier ``probabilities.json``.
        vote_t: Minimum proposer vote count (inclusive).
        prob_t: Minimum verifier ``mound_probability`` (inclusive).
        source_stage: Stage id stamped onto every kept feature.

    Returns:
        ``(features, stats)`` — GeoJSON features in union order, and counts
        ``{n_union, n_probabilities, n_kept, n_missing_probability}``.

    Raises:
        ValueError: If ``probabilities.json`` addresses a candidate index
            beyond the union's feature count (the index alignment that makes
            this join meaningful has broken).
    """
    union = _load(consensus_path).get("features", [])
    results = _load(probabilities_path).get("results", {})

    max_idx = -1
    for key in results:
        if key.startswith("candidate_"):
            try:
                max_idx = max(max_idx, int(key.split("_", 1)[1]))
            except ValueError:
                continue
    if max_idx >= len(union):
        raise ValueError(
            f"Indexing mismatch: {probabilities_path} addresses candidate_{max_idx:05d} "
            f"but {consensus_path} has only {len(union)} features."
        )

    features: list[dict[str, Any]] = []
    missing = 0
    for idx, feat in enumerate(union):
        entry = results.get(f"candidate_{idx:05d}")
        if entry is None:
            missing += 1
            continue
        prob = entry.get("mound_probability")
        if prob is None or float(prob) < prob_t:
            continue
        props = dict(feat.get("properties") or {})
        if props.get("vote_count", 0) < vote_t:
            continue
        features.append(_build_feature(feat["geometry"], props, float(prob), vote_t, prob_t,
                                       source_stage, idx))
    return features, {"n_union": len(union), "n_probabilities": len(results),
                      "n_kept": len(features), "n_missing_probability": missing}


def filter_s78_manifest(
    pool: str,
    variant: str,
    vote_t: int,
    prob_t: float,
    source_stage: str,
    allowlist: set[str],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Filter a session-78 shared-crops manifest by the registered point.

    The session-78 matrix has no consensus GeoJSON: its union is the
    shared-crops ``candidate_manifest.json``, whose entries carry their own
    ``candidate_id`` and a UTM 35N centroid.  The original materialiser also
    restricted to the 487-tile Era-2 bounds, so this reproduction does too.

    Args:
        pool: ``"text"`` or ``"image"``.
        variant: Verifier instruction variant (e.g. ``"adversarial-text"``).
        vote_t: Minimum proposer vote count (inclusive).
        prob_t: Minimum verifier ``mound_probability`` (inclusive).
        source_stage: Stage id stamped onto every kept feature.
        allowlist: Tile names of the Era-2 frame.

    Returns:
        ``(features, stats)`` as for :func:`filter_pv_union`, with the extra
        count ``n_out_of_scope``.  Geometries stay in the manifest's UTM 35N.
    """
    base = S78_POOL_BASE[pool]
    manifest = _load(f"{base}/session-78-matrix/shared-crops/candidate_manifest.json")
    results = _load(f"{base}/session-78-matrix/verified-{variant}/probabilities.json").get("results", {})
    candidates = manifest["candidates"]

    features: list[dict[str, Any]] = []
    missing = out_of_scope = 0
    for cand in candidates:
        if cand["source_tile"] not in allowlist:
            out_of_scope += 1
            continue
        props = dict(cand.get("properties") or {})
        if props.get("vote_count", 0) < vote_t:
            continue
        entry = results.get(f"candidate_{int(cand['candidate_id']):05d}")
        if entry is None:
            missing += 1
            continue
        prob = entry.get("mound_probability")
        if prob is None or float(prob) < prob_t:
            continue
        geom = {"type": "Point", "coordinates": [cand["centroid_x"], cand["centroid_y"]]}
        features.append(_build_feature(geom, props, float(prob), vote_t, prob_t, source_stage,
                                       int(cand["candidate_id"])))
    return features, {"n_union": len(candidates), "n_probabilities": len(results),
                      "n_kept": len(features), "n_missing_probability": missing,
                      "n_out_of_scope": out_of_scope}


def _build_feature(
    geometry: dict[str, Any],
    props: dict[str, Any],
    prob: float,
    vote_t: int,
    prob_t: float,
    source_stage: str,
    candidate_id: int,
) -> dict[str, Any]:
    """Assemble one output feature: the union's properties plus provenance."""
    out = dict(props)
    out["mound_probability"] = prob
    out["vote_t"] = vote_t
    out["prob_t"] = prob_t
    out["source_stage"] = source_stage
    out["candidate_id"] = candidate_id
    # scripts/evaluate_detections.py needs the singular source_tile for the
    # tile-level metrics; the consensus writer emits the plural list only.
    if "source_tile" not in out:
        tiles = out.get("source_tiles") or []
        if tiles:
            out["source_tile"] = tiles[0]
    return {"type": "Feature", "geometry": geometry, "properties": out}


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------


def _is_resolved_target(row: dict[str, Any]) -> bool:
    """True when this row's archived materialisation disagrees with its registry."""
    return str(row.get("registry_vs_archived", "")).startswith("differs")


def build_rows() -> list[dict[str, Any]]:
    """Run the filter over every membership row and assemble a report row each.

    Returns:
        One dict per membership row with the computed feature list under
        ``_features``, the counts, and the comparison verdict.
    """
    membership = _load(MEMBERSHIP)
    pv = {e["id"]: e for e in _load(PV_REGISTRY)}
    s78 = {Path(c["output_geojson"]).stem: c for c in _load(S78_REGISTRY)["cells"]}
    allowlist = era2_tile_allowlist()

    rows: list[dict[str, Any]] = []
    for member in membership["members"]:
        label = member["label"]
        vote_t = int(member["vote_threshold"])
        prob_t = float(member["prob_threshold"])
        stage = member["stage_id"]
        vintage: dict[str, Any] | None = None
        if label in pv:
            entry = pv[label]
            inputs = {"union": entry["consensus_path"],
                      "probabilities": entry["probabilities_path"],
                      "sweep": entry.get("sweep_path")}
            # Vintage guard (2026-09-11): the index join is only meaningful
            # while the union still holds what the verifier cropped. Classify
            # BEFORE filtering, and refuse to publish a count for a rebuilt
            # union — a soft-failing join there returns a plausible number that
            # is not an operating point (pv-high-text-t0.0-n3: 410 vs 403).
            n_union = len(_load(entry["consensus_path"]).get("features", []))
            n_prob = len(_load(entry["probabilities_path"]).get("results", {}))
            n_sweep = sweep_universe(entry.get("sweep_path"))
            verdict, why = classify_vintage(n_union, n_prob, n_sweep)
            vintage = {"verdict": verdict, "why": why, "n_union": n_union,
                       "n_probabilities": n_prob, "n_sweep": n_sweep}
            if verdict == "union-rebuilt":
                features, stats = [], {"n_union": n_union, "n_probabilities": n_prob,
                                       "n_kept": None, "n_missing_probability": None}
            else:
                features, stats = filter_pv_union(entry["consensus_path"],
                                                  entry["probabilities_path"],
                                                  vote_t, prob_t, stage)
            pool_shape = "pv-consensus-union"
        elif label in s78:
            cell = s78[label]
            base = S78_POOL_BASE[cell["pool"]]
            inputs = {"union": f"{base}/session-78-matrix/shared-crops/candidate_manifest.json",
                      "probabilities": f"{base}/session-78-matrix/verified-{cell['variant']}/probabilities.json",
                      "sweep": None}
            features, stats = filter_s78_manifest(cell["pool"], cell["variant"], vote_t, prob_t,
                                                  stage, allowlist)
            pool_shape = "session-78-shared-crops-manifest"
        else:  # pragma: no cover - membership is derived from these two registries
            raise KeyError(f"{label}: in membership.json but in neither materialisation registry")

        archived_rel = member["detections"]
        archived_n = len(_load(archived_rel).get("features", [])) if (REPO_ROOT / archived_rel).is_file() else None
        rows.append({
            "label": label,
            "condition_id": member["condition_id"],
            "on_board": bool(member["on_board"]),
            "pool_shape": pool_shape,
            "stage_id": stage,
            "vote_t": vote_t,
            "prob_t": prob_t,
            "inputs": inputs,
            "archived_detections": archived_rel,
            "n_computed": stats["n_kept"],
            "n_registry": member.get("registry_n"),
            "n_archived": archived_n,
            "registry_vs_archived": member.get("registry_vs_archived"),
            "vintage": vintage,
            "matches_registry": member.get("registry_n") is None or stats["n_kept"] == member["registry_n"],
            "matches_archived": archived_n is not None and stats["n_kept"] == archived_n,
            "re_materialise": _is_resolved_target(member),
            "stats": stats,
            "_features": features,
        })
    return rows


def write_cell(row: dict[str, Any]) -> tuple[Path, Path]:
    """Write one cell's GeoJSON and its provenance sidecar.

    Args:
        row: A row from :func:`build_rows` (must carry ``_features``).

    Returns:
        ``(geojson_path, provenance_path)``.
    """
    out_dir = REPO_ROOT / OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    geo_path = out_dir / f"{row['label']}.geojson"
    prov_path = out_dir / f"{row['label']}.provenance.json"

    geo_path.write_text(json.dumps({
        "type": "FeatureCollection",
        "name": row["label"],
        "crs": {"type": "name", "properties": {"name": OUTPUT_CRS_URN}},
        "features": row["_features"],
    }), encoding="utf-8")

    inputs = {}
    for key, rel in row["inputs"].items():
        if not rel:
            continue
        inputs[key] = {"path": rel, "git_blob_sha1": git_blob_hash(rel),
                       "last_commit": git_last_commit(rel)}
    superseded = row["archived_detections"]
    prov_path.write_text(json.dumps({
        "label": row["label"],
        "condition_id": row["condition_id"],
        "board_id": Path(BOARD_DIR).name,
        "written_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "written_by": "scripts/materialise_opmax_cells.py",
        "why": ("the 2026-04-19 materialisation (bd24293d4) does not hold the point the "
                "materialisation registry registered; rebuilt from the registered stage at the "
                "registered (vote_t, prob_t) — the union, probabilities and sweep are unchanged "
                "since 2026-04-17/18"),
        "operating_point": {"vote_t": row["vote_t"], "prob_t": row["prob_t"],
                            "filter": "vote_count >= vote_t AND mound_probability >= prob_t"},
        "stage_id": row["stage_id"],
        "pool_shape": row["pool_shape"],
        "inputs": inputs,
        "membership": {"path": MEMBERSHIP, "git_blob_sha1": git_blob_hash(MEMBERSHIP)},
        "superseded_detections": {"path": superseded, "n_features": row["n_archived"],
                                  "git_blob_sha1": git_blob_hash(superseded),
                                  "registry_vs_archived": row["registry_vs_archived"]},
        "counts": {"n_computed": row["n_computed"], "n_registry": row["n_registry"],
                   "n_archived": row["n_archived"], **row["stats"]},
        "gate_a": {"expected_n": row["n_registry"], "observed_n": row["n_computed"],
                   "passed": bool(row["matches_registry"])},
        "output_crs": "EPSG:4326",
    }, indent=1) + "\n", encoding="utf-8")
    return geo_path, prov_path


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns 0 when Gate A passes for every target row."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--write", action="store_true",
                        help="write the re-materialised cells and their provenance sidecars")
    args = parser.parse_args(argv)

    rows = build_rows()
    targets = [r for r in rows if r["re_materialise"]]
    others = [r for r in rows if not r["re_materialise"]]

    print(f"{len(rows)} membership rows; {len(targets)} to re-materialise "
          f"({sum(r['on_board'] for r in targets)} on-board)")
    print("\n-- Gate A: re-materialisation targets (computed n must equal the registry's n) --")
    gate_a_fail = 0
    for r in sorted(targets, key=lambda r: r["label"]):
        ok = r["matches_registry"]
        gate_a_fail += not ok
        moved = (f"(archived -> computed {r['n_computed'] - (r['n_archived'] or 0):+d})"
                 if r["n_computed"] is not None
                 else f"(no count: {(r.get('vintage') or {}).get('verdict')})")
        print(f"  {'ok  ' if ok else 'FAIL'} {r['label']:<26} computed {str(r['n_computed']):<5} "
              f"registry {str(r['n_registry']):<5} archived {str(r['n_archived']):<5} {moved}")

    print("\n-- Vintage guard: is the union still the set the verifier cropped? --")
    unrebuilt = [r for r in rows if (r.get("vintage") or {}).get("verdict") == "union-rebuilt"]
    grew = [r for r in rows if (r.get("vintage") or {}).get("verdict") == "probabilities-grew"]
    for r in sorted(unrebuilt + grew, key=lambda r: r["label"]):
        v = r["vintage"]
        print(f"  {v['verdict']:<18} {r['label']:<26} union {v['n_union']:<6}"
              f"probs {v['n_probabilities']:<6}sweep {str(v['n_sweep']):<6}")
    print(f"  {len(unrebuilt)} union-rebuilt (join invalid, no count published), "
          f"{len(grew)} probabilities-grew (join sound, sweep stale)")

    print("\n-- Check: every other row (rewritten by nobody; a mismatch is a finding) --")
    checkable = [r for r in others if r["n_computed"] is not None]
    mismatches = [r for r in checkable if not r["matches_archived"]]
    for r in sorted(checkable, key=lambda r: r["label"]):
        if r["matches_archived"]:
            continue
        print(f"  MISMATCH {r['label']:<26} on_board={r['on_board']} computed {r['n_computed']:<5} "
              f"registry {str(r['n_registry']):<5} archived {str(r['n_archived']):<5}")
    print(f"  {len(checkable) - len(mismatches)}/{len(checkable)} reproduce their archived file "
          f"exactly ({len(others) - len(checkable)} not checkable: the union was rebuilt)")

    report = {
        "board_id": Path(BOARD_DIR).name,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_rows": len(rows),
        "n_re_materialised": len(targets),
        "gate_a_failures": gate_a_fail,
        "gate_a_passed": gate_a_fail == 0,
        "n_other_rows": len(others),
        "n_other_mismatches": len(mismatches),
        "n_union_rebuilt": len(unrebuilt),
        "n_probabilities_grew": len(grew),
        "written": bool(args.write),
        "rows": [{k: v for k, v in r.items() if k != "_features"} for r in rows],
    }

    if args.write:
        if gate_a_fail:
            print("\nGate A failed — refusing to write.", file=sys.stderr)
            return 1
        out_dir = REPO_ROOT / OUT_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        for r in targets:
            geo, prov = write_cell(r)
            print(f"  wrote {geo.relative_to(REPO_ROOT)} ({r['n_computed']} features) + "
                  f"{prov.name}")
        (out_dir / "check.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
        print(f"  wrote {OUT_DIR}/check.json")
    else:
        print("\n(dry run — pass --write to materialise)")

    return 0 if gate_a_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
