"""Task A of D57 (3): declare the tiling of the four T 0.7 ladders' passes.

D51 gate refusal reason for every rung of the four T 0.7 pv-diag-384 ladders
(``reports/scorer-frames-d50-d51-2026-10-08.md`` § 5.6): "pass … has no meta
file recording its tile manifest". The passes' GeoJSONs do record
``processed_tiles``; what the gate lacks is which tiling those names belong
to. This script assembles the evidence for that tiling and writes one
``pass_tilings`` declaration entry per cell (runs 1-10, every pass a K <= 10
rung uses), each pass anchored by its git blob hash.

Evidence gathered and CHECKED per pass (a failed check aborts the cell):

1. meta ``environment``: the commit and script that wrote the pass, and the
   meta ``configuration`` (model, prompt version, temperature, thinking);
   ``full_config_snapshot.manifest_path`` must be ABSENT (else no
   declaration is needed and none is written);
2. the study YAML at that commit whose ``execution.output_dir`` is the
   cell's parent and which has a condition named the cell's directory (a
   lookup by recorded fields, unique match required): its
   ``inputs.manifest``, and its condition's prompt config and temperature
   against the meta's;
3. the batch writer at that commit (``scripts/lib_batch_api.py``) reads the
   tile list from the study's ``inputs["manifest"]``;
4. the manifest's bytes at that commit equal its bytes now;
5. tile for tile: the pass's ``.tiles.json`` ``completed`` union ``failed``
   equals the manifest exactly, and is equal to no other registered tiling;
   ``processed_tiles`` is a subset of the manifest.

Validation (``--validate``): check 5 alone identifies a tiling from a pass's
``.tiles.json``. Run on the K = 1 and K = 3 passes (runs 1-3) of the nine
ladders whose metas DO record a manifest, it must name that manifest every
time; the identified tiling is written as a scratch declaration so the gate
survey can recompute those rungs' areas through the declared route.

Usage (sapphire; read-only on the repository)::

    PYTHONDONTWRITEBYTECODE=1 ~/Code/map-reader-llm/.venv/bin/python t07_tilings.py \
        --code ~/worktrees/map-reader-llm/claude-d51-ladder-provenance \
        --out out/t07_tilings.json \
        --validation-declarations ~/scratch/d51-ladder-provenance-2026-10-08/validation-tilings.json

Created: 2026-10-08 (D57 (3), Session 163 follow-up)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

#: The four T 0.7 ladders (pool slug as in build_k_ladder_phase2_tables.FAMILIES).
T07_POOLS = [
    "flash-minimal-text-n30-t07-text-t0.7",
    "flash-high-text-n5-text-t0.7",
    "image-n5-image-t0.7",
    "flash-high-image-n5-image-t0.7",
]
#: The nine ladders whose K = 1 / K = 3 passes' metas record their manifest.
DETERMINABLE_POOLS = [
    "flash-minimal-text-n30-t07-text-t0.3",
    "flash-minimal-text-n30-t07-text-t1.0",
    "flash-high-text-n5-text-t0.3",
    "flash-high-text-n5-text-t1.0",
    "image-n5-image-t0.3",
    "image-n5-image-t1.0",
    "flash-high-image-n5-image-t0.3",
    "flash-high-image-n5-image-t1.0",
    "scale-4-optimal-487",
]
OPERATING_POINTS = "results/k-ladder-2026-09-12/phase2/operating-points.json"


def git(code: Path, *args: str) -> str:
    """Run a read-only git command in the code checkout and return stdout."""
    return subprocess.run(["git", "-C", str(code), *args], check=True,
                          capture_output=True, text=True).stdout


def cell_dir(code: Path, pool: str) -> Path:
    """A ladder's pass directory, from its recorded K = 1 union (not its name).

    ``operating-points.json`` records each Phase 2 rung's union, written by
    ``merge_passes.py --sweep`` into ``<cell>/consensus-n1/``; the cell is
    that union's grandparent, and the union's ``voting_summary.json`` names
    its pass under the same cell (checked).
    """
    points = json.loads((code / OPERATING_POINTS).read_text())
    union = next(r["union"] for r in points["rungs"]
                 if r["pool_slug"] == pool and r["n_passes"] == 1)
    cell = (code / union).parent.parent
    summary = json.loads(((code / union).parent / "voting_summary.json").read_text())
    pass_path = summary["pass_provenance"][0]["path"]
    if not (code / pass_path).resolve().is_relative_to(cell.resolve()):
        raise SystemExit(f"{pool}: K = 1 pass {pass_path} is not under {cell}")
    return cell


def pass_file(run: Path) -> Path:
    """The single detection GeoJSON of a run directory (meta sidecars excluded)."""
    files = [f for f in run.glob("*.geojson") if ".meta" not in f.name]
    if len(files) != 1:
        raise SystemExit(f"{run}: expected one detection GeoJSON, found {len(files)}")
    return files[0]


def blob(path: Path) -> str:
    """Git blob hash of a file (identical to ``git hash-object``)."""
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def registered_tilings(code: Path) -> dict[str, set[str]]:
    """Every registered tiling's manifest tile set (lib_assessed_area.KNOWN_TILINGS)."""
    sys.path.insert(0, str(code))
    from scripts.lib_assessed_area import KNOWN_TILINGS  # noqa: PLC0415

    return {m: set(json.loads((code / m).read_text())) for m in KNOWN_TILINGS
            if (code / m).exists()}


def polygons_identical(code: Path, manifest_a: str, manifest_b: str) -> bool:
    """Whether two registered tilings give every shared tile the same polygon.

    ``inputs/grid-2026-08-18/grid_384_ov048_manifest.json`` (registered
    2026-08-18) holds the same 487 names as the 384 px evaluation manifest,
    so tile-for-tile matching alone cannot tell them apart; it is harmless
    for area only if their polygons coincide, which this checks (symmetric
    difference of every same-named pair, EPSG:32635, at most 1e-6 m²).
    """
    import geopandas as gpd  # noqa: PLC0415
    from scripts.lib_assessed_area import KNOWN_TILINGS  # noqa: PLC0415

    a = gpd.read_file(code / KNOWN_TILINGS[manifest_a]).to_crs(32635).set_index("tile_name")
    b = gpd.read_file(code / KNOWN_TILINGS[manifest_b]).to_crs(32635).set_index("tile_name")
    if set(a.index) != set(b.index):
        return False
    return all(a.loc[n].geometry.symmetric_difference(b.loc[n].geometry).area <= 1e-6
               for n in a.index)


def identify_tiling(tiles_json: Path, tilings: dict[str, set[str]]) -> dict[str, Any]:
    """Check 5: the registered tilings whose manifest equals completed ∪ failed."""
    record = json.loads(tiles_json.read_text())
    attempted = set(record.get("completed") or []) | set(record.get("failed") or [])
    matches = [m for m, names in tilings.items() if names == attempted]
    return {"tiles_json": tiles_json.name, "attempted": len(attempted),
            "completed": len(record.get("completed") or []),
            "failed": sorted(record.get("failed") or []),
            "matches": matches}


def find_study(code: Path, commit: str, out_dir: str, condition: str) -> tuple[str, dict]:
    """Check 2: the study YAML at ``commit`` that wrote ``out_dir/condition``."""
    hits = []
    for name in git(code, "ls-tree", "--name-only", commit, "studies/").split():
        if not name.endswith((".yaml", ".yml")):
            continue
        try:
            doc = yaml.safe_load(git(code, "show", f"{commit}:{name}"))
        except yaml.YAMLError:
            continue
        if not isinstance(doc, dict):
            continue
        execution = doc.get("execution") or {}
        names = [c.get("name") for c in doc.get("conditions") or []]
        if execution.get("output_dir") == out_dir and condition in names:
            hits.append((name, doc))
    if len(hits) != 1:
        raise SystemExit(f"{out_dir}/{condition} at {commit}: {len(hits)} study YAMLs match")
    return hits[0]


#: Cache of :func:`polygons_identical` results, keyed by manifest pair.
POLYGONS_IDENTICAL: dict[tuple[str, str], bool] = {}


def check_pass(code: Path, cell: Path, run: int, tilings: dict[str, set[str]],
               writer_checked: dict[str, bool]) -> dict[str, Any]:
    """Checks 1-5 for one T 0.7 pass; raises SystemExit on any failure."""
    geo = pass_file(cell / f"run_{run}")
    rel = str(geo.relative_to(code))
    meta = json.loads(geo.with_name(geo.name.replace(".geojson", ".meta.json")).read_text())
    env = meta.get("environment") or {}
    cfg = meta.get("configuration") or {}
    snapshot = cfg.get("full_config_snapshot") or {}
    if snapshot.get("manifest_path"):
        raise SystemExit(f"{rel}: meta records a manifest; no declaration needed")
    commit = env["git_commit"]
    out_dir = str(cell.parent.relative_to(code))
    study_path, study = find_study(code, commit, out_dir, cell.name)
    manifest = study["inputs"]["manifest"]
    condition = next(c for c in study["conditions"] if c["name"] == cell.name)
    config_stem = Path(condition["config"]).stem
    problems = []
    if config_stem != cfg.get("version"):
        problems.append(f"config {config_stem} != meta version {cfg.get('version')}")
    if float(condition.get("temperature", -1)) != float(cfg.get("temperature", -2)):
        problems.append("temperature differs")
    if condition.get("thinking_level") not in (None, cfg.get("thinking_level")):
        problems.append("thinking level differs")
    # Check 3, once per commit: the writer reads the study's manifest.
    if commit not in writer_checked:
        source = git(code, "show", f"{commit}:scripts/lib_batch_api.py")
        writer_checked[commit] = 'inputs["manifest"]' in source and \
            "_resolve_tile_paths(manifest_path" in source
    if not writer_checked[commit]:
        problems.append(f"lib_batch_api.py at {commit} does not read inputs['manifest']")
    # Check 4: the manifest's bytes then and now.
    then = hashlib.sha256(git(code, "show", f"{commit}:{manifest}").encode()).hexdigest()
    now = hashlib.sha256((code / manifest).read_text().encode()).hexdigest()
    if then != now:
        problems.append(f"{manifest} changed since {commit}")
    # Check 5: tile for tile. Another registered tiling with the same names
    # is tolerated only if its polygons are identical (so the area cannot
    # depend on which is named) and it did not exist at the writer commit.
    ident = identify_tiling(geo.with_name(geo.name.replace(".geojson", ".tiles.json")),
                            tilings)
    if manifest not in ident["matches"]:
        problems.append(f"completed ∪ failed matches {ident['matches']}, not {manifest}")
    ident["same_names_elsewhere"] = []
    for other in ident["matches"]:
        if other == manifest:
            continue
        key = (manifest, other)
        if key not in POLYGONS_IDENTICAL:
            POLYGONS_IDENTICAL[key] = polygons_identical(code, manifest, other)
        existed = subprocess.run(["git", "-C", str(code), "cat-file", "-e",
                                  f"{commit}:{other}"], capture_output=True).returncode == 0
        ident["same_names_elsewhere"].append({
            "manifest": other, "polygons_identical": POLYGONS_IDENTICAL[key],
            "existed_at_writer_commit": existed})
        if not POLYGONS_IDENTICAL[key] or existed:
            problems.append(f"{other} also matches tile for tile (polygons identical: "
                            f"{POLYGONS_IDENTICAL[key]}, existed then: {existed})")
    processed = set(json.loads(geo.read_text()).get("processed_tiles") or [])
    outside = processed - tilings[manifest]
    if outside:
        problems.append(f"{len(outside)} processed tile(s) outside {manifest}")
    if problems:
        raise SystemExit(f"{rel}: " + "; ".join(problems))
    return {
        "path": rel, "git_blob_hash": blob(geo), "writer": f"{env.get('script')} "
        f"{env.get('script_version')} at {commit[:9]}",
        "timestamp": (meta.get("timestamp") or {}).get("start"),
        "meta_configuration": {k: cfg.get(k) for k in ("model", "version", "temperature",
                                                       "thinking_level")},
        "study": study_path, "study_manifest": manifest,
        "study_condition": {"name": cell.name, "config": condition["config"],
                            "temperature": condition.get("temperature"),
                            "thinking_level": condition.get("thinking_level")},
        "tiles_json": ident, "processed_tiles": len(processed),
        "unprocessed": sorted(tilings[manifest] - processed),
    }


def declaration(pool: str, checks: list[dict[str, Any]], n_tiles: int,
                manifest_history: str) -> dict[str, Any]:
    """One ``pass_tilings`` entry for a cell's checked passes.

    Args:
        pool: The ladder's pool slug.
        checks: :func:`check_pass` results for runs 1-10.
        n_tiles: Tiles in the declared manifest.
        manifest_history: ``git log`` abbreviated hashes touching the manifest.
    """
    manifest = checks[0]["study_manifest"]
    if any(c["study_manifest"] != manifest for c in checks):
        raise SystemExit(f"{pool}: passes name different manifests")
    commits = sorted({c["writer"] for c in checks})
    studies = sorted({c["study"] for c in checks})
    gaps = {c["path"]: c["unprocessed"] for c in checks if c["unprocessed"]}
    others = sorted({o["manifest"] for c in checks
                     for o in c["tiles_json"]["same_names_elsewhere"]})
    other_note = (
        f"; the only other registered tiling with the same names ({', '.join(others)}) "
        f"is absent at every writer commit and has identical polygons, so the area "
        f"cannot depend on which is named" if others else
        "; no other registered tiling has the same names")
    return {
        "schema": "pass-tiling/1",
        "label": f"{pool}, runs 1-10 (March 2026 batch passes)",
        "manifest": manifest,
        "status": "declared-retrospectively",
        "declared": "2026-10-08 (PI ruling D57 (3))",
        "evidence": [
            f"writer: {', '.join(commits)} (each pass's meta environment); the metas' "
            f"configuration snapshot is the prompt config only, with no manifest_path",
            f"study YAML at each writer commit: {', '.join(studies)}, the one whose "
            f"execution.output_dir and condition name are this cell's; inputs.manifest = "
            f"{manifest}; its condition's prompt config and temperature equal each "
            f"meta's configuration",
            "scripts/lib_batch_api.py at each writer commit: prepare_batch_unit reads "
            "inputs['manifest'] and resolves tiles with _resolve_tile_paths(manifest_path)",
            f"{manifest}: bytes at each writer commit equal its bytes now (commits "
            f"touching it: {manifest_history})",
            f"tile for tile: each pass's .tiles.json completed ∪ failed equals the "
            f"{n_tiles}-tile manifest exactly, and its processed_tiles lie inside it"
            + other_note,
            "unprocessed tiles (the area they leave out stays out): "
            + (json.dumps(gaps) if gaps else "none"),
            "checks: reports/d51-ladder-provenance-2026-10-08-scripts/t07_tilings.py; "
            "out/t07_tilings.json",
        ],
        "passes": [{"path": c["path"], "git_blob_hash": c["git_blob_hash"]} for c in checks],
    }


def main() -> int:
    """Check every T 0.7 pass, write the entries, and run the validation."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--validation-declarations", type=Path, required=True)
    args = ap.parse_args()
    code = args.code.expanduser().resolve()
    tilings = registered_tilings(code)
    writer_checked: dict[str, bool] = {}
    result: dict[str, Any] = {"t07": {}, "declarations": [], "validation": {}}
    for pool in T07_POOLS:
        cell = cell_dir(code, pool)
        checks = [check_pass(code, cell, run, tilings, writer_checked)
                  for run in range(1, 11)]
        manifest = checks[0]["study_manifest"]
        history = " ".join(git(code, "log", "--format=%h", "--", manifest).split())
        result["t07"][pool] = {"cell": str(cell.relative_to(code)), "passes": checks}
        result["declarations"].append(
            declaration(pool, checks, len(tilings[manifest]), history))
        print(pool, "OK", [c["processed_tiles"] for c in checks], flush=True)

    # Validation: check 5 (tile for tile, among tilings that existed at the
    # writer commit) on passes whose metas record the manifest; it must name
    # the recorded manifest every time.
    sys.path.insert(0, str(code))
    from scripts.lib_assessed_area import PASS_TILING_SCHEMA, pass_manifest  # noqa: PLC0415

    entries = []
    for pool in DETERMINABLE_POOLS:
        cell = cell_dir(code, pool)
        rows = []
        for run in (1, 2, 3):
            geo = pass_file(cell / f"run_{run}")
            ident = identify_tiling(geo.with_name(geo.name.replace(".geojson",
                                                                    ".tiles.json")), tilings)
            meta = json.loads(geo.with_name(geo.name.replace(".geojson", ".meta.json"))
                              .read_text())
            commit = (meta.get("environment") or {}).get("git_commit")
            then = [m for m in ident["matches"] if subprocess.run(
                ["git", "-C", str(code), "cat-file", "-e", f"{commit}:{m}"],
                capture_output=True).returncode == 0]
            recorded = pass_manifest(geo)
            rows.append({"path": str(geo.relative_to(code)), "recorded": recorded,
                         "writer_commit": commit, "same_names": ident["matches"],
                         "identified": then, "agrees": then == [recorded]})
            entries.append({"schema": PASS_TILING_SCHEMA, "label": f"validation {pool}",
                            "manifest": then[0] if len(then) == 1 else None,
                            "evidence": ["validation only (scratch)"],
                            "passes": [{"path": str(geo.relative_to(code)),
                                        "git_blob_hash": blob(geo)}]})
        result["validation"][pool] = rows
        print("validate", pool, all(r["agrees"] for r in rows), flush=True)
    result["validation_all_agree"] = all(r["agrees"] for rows in result["validation"].values()
                                         for r in rows)
    args.validation_declarations.write_text(json.dumps({"pass_tilings": entries}, indent=1))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1) + "\n")
    return 0 if result["validation_all_agree"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
