#!/usr/bin/env python3
"""
Measure which committed outputs the consensus library copies' fix would move.

D62 (1) workstream ``origin-gap-h13-copies`` (2026-10-13), step 2. The fix
adds one column, ``source_tiles`` (each row's contributing tiles), to the
frames built by ``lib_consensus.generate_consensus_gdf``,
``lib_consensus.build_pv_gdf`` and ``analyse_diversity.consensus_to_gdf``;
every other column is unchanged. So, arm by arm, this driver builds each
frame with the code in ``--code`` and scores it twice: as built, and with
``source_tiles`` dropped (which is, by construction, the pre-fix frame; the
driver run on origin/main's code checks that). An arm moves exactly when
the shared scorer's scope (``scope_detections_to_frame``: which rows are
kept, and on which sheet each is matched) differs between the two; F1,
precision, and recall at the output's buffer are recorded beside it. When
the scope is identical, every per-tile table, interval, and permutation p
built from the frame is identical too, because ``source_tile`` (the per-tile
booking key) is unchanged.

Sections (``--section``):

``diversity-track1`` / ``diversity-track2``
    ``scripts/analyse_diversity.py``'s 125 + 100 arms (condition x
    replication x vote threshold) behind ``results/phase3c-diversity/``,
    from each track's recorded study YAML, output directory, and bounds.
``pes``
    ``scripts/compute-pairwise-effect-sizes.py``'s distinct PV and N = 30
    consensus conditions, for the v1 inputs (``--sc``'s ``data`` and
    ``pv-data``, as PR D42's ``run_classb.sh`` ran them) and the v2 inputs
    (the March layout remapped as ``regen_pes_v2.py`` remaps it).
``p3a``
    ``scripts/consensus-sweep-phase3a-high-text.py``'s 135 HIGH and 45
    minimal consensus arms and its two PV arms, on ``--sc``'s data.

Usage::

    python measure_copies.py --code <tree> --data <clone> --sc <dir>
        --section <name> --out <json> [--march-sweeps <dir>]

Author: Claude Code (Opus 5.5) for Shawn Ross
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import geopandas as gpd


def load_module(name: str, path: Path) -> Any:
    """Import a script file as a module (hyphenated names included).

    Args:
        name: Module name to register.
        path: The script file.

    Returns:
        The executed module.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Scorer:
    """Score frames with the tree's shared library, as built and list-dropped."""

    def __init__(self, lam: Any) -> None:
        """Keep the library module.

        Args:
            lam: The tree's ``lib_advanced_metrics`` module.
        """
        self.lam = lam

    def one(self, gdf: gpd.GeoDataFrame, ref: gpd.GeoDataFrame,
            bounds: gpd.GeoDataFrame, buffer: int) -> dict[str, Any]:
        """Scope signature, scope counters, and P/R/F1 for one frame.

        Args:
            gdf: Detections. ref: References. bounds: Frame tiles.
            buffer: Matching radius in metres.

        Returns:
            A record; ``scope_sig`` hashes the kept row positions and the
            sheet each is matched on.
        """
        gdf = gdf.reset_index(drop=True)
        scope = self.lam.scope_detections_to_frame(gdf, bounds)
        kept = [int(i) for i in scope.detections.index]
        sheets = [str(s) for s in scope.sheets]
        sig = hashlib.sha256(json.dumps([kept, sheets]).encode()).hexdigest()[:16]
        diag = {k: scope.diagnostics[k] for k in (
            "n_in_scope", "n_out_of_frame", "n_origin_restored",
            "n_origin_switched", "n_origin_only", "n_unattributed")}
        diag["n_retained"] = int(len(scope.retained))
        p, r, f1 = self.lam.calculate_f1_internal(gdf, ref, bounds, buffer_metres=buffer)
        return {"scope_sig": sig, "diag": diag, "precision": p, "recall": r, "f1": f1}

    def arm(self, gdf: gpd.GeoDataFrame, ref: gpd.GeoDataFrame,
            bounds: gpd.GeoDataFrame, buffer: int = 20) -> dict[str, Any]:
        """Score a frame as built and, if it carries the list, without it.

        Args:
            gdf: Detections. ref: References. bounds: Frame tiles.
            buffer: Matching radius in metres.

        Returns:
            ``{"n", "has_list", "as_built", "dropped"?, "moves"?}``.
        """
        rec: dict[str, Any] = {"n": int(len(gdf)), "has_list": "source_tiles" in gdf.columns}
        if len(gdf) == 0:
            return rec
        rec["as_built"] = self.one(gdf, ref, bounds, buffer)
        if rec["has_list"]:
            rec["dropped"] = self.one(gdf.drop(columns="source_tiles"), ref, bounds, buffer)
            rec["moves"] = rec["dropped"]["scope_sig"] != rec["as_built"]["scope_sig"]
        return rec


def diversity(code: Path, data: Path, track: str, sc: Scorer, lam: Any) -> dict:
    """The diversity arms of one track.

    Args:
        code: Tree whose scripts are imported. data: Clone holding inputs.
        track: ``track1-image`` or ``track2-text``. sc: Scorer. lam: Library.

    Returns:
        ``{arm_key: record}`` with the committed F1 attached.
    """
    import analyse_diversity as ad  # noqa: E402  (scripts/ on sys.path)

    report = json.loads((data / "results/phase3c-diversity" / track
                         / "diversity-analysis-report.json").read_text())
    meta = report["metadata"]
    committed = {(r["condition"], r["replication"], r["threshold"]): r["f1"]
                 for r in report["results"]}
    study = ad.load_study_yaml(data / meta["study_yaml"])
    design = ad.extract_consensus_design(study)
    study_dir = data / meta["study_dir"]
    ref = gpd.read_file(data / meta["ground_truth"]).to_crs(ad.TARGET_CRS)
    bounds = gpd.read_file(data / meta["bounds"]).to_crs(ad.TARGET_CRS)
    out: dict[str, Any] = {}
    for label in sorted(design):
        for rep in range(1, meta["n_replications"] + 1):
            passes = ad.load_replication_passes(study_dir, design[label], rep)
            clusters = ad.cluster_across_passes(passes)
            for x in meta["thresholds"]:
                fc = ad.apply_threshold(clusters, x, len(design[label]))
                gdf = ad.consensus_to_gdf(fc, bounds)
                rec = sc.arm(gdf, ref, bounds, meta["buffer_metres"])
                rec["committed_f1"] = committed.get((label, rep, x))
                out[f"{label}|rep{rep}|t{x}"] = rec
                print(track, label, rep, x, rec.get("moves"), flush=True)
    return out


def remap_v2(comps: list[dict], data: Path, march_sweeps: Path) -> list[dict]:
    """Remap the March layout exactly as ``regen_pes_v2.py`` does.

    Args:
        comps: Comparisons defined against ``/DATA`` and ``/PV``.
        data: Clone root. march_sweeps: Directory holding the one sweep
            E39 regenerated (``git show e686e695e:...``).

    Returns:
        The comparisons with every path remapped.
    """
    arch = data / "archive/outputs-experimental-pilot/pv"
    table = [
        ("/DATA/consensus-proposers", arch / "consensus-proposers"),
        ("/DATA/retest", data / "outputs/retest"),
        ("/PV/results", arch / "results"),
        ("/PV/crops", arch / "crops-150"),
        ("/PV/sweeps/phase1/adversarial-text-150",
         march_sweeps / "phase1/adversarial-text-150"),
        ("/PV/sweeps", data / "results/pv"),
    ]

    def remap(value: Any) -> Any:
        """Map one March-layout path onto its current location."""
        if not isinstance(value, Path):
            return value
        text = str(value)
        for old, new in table:
            if text == old or text.startswith(old + "/"):
                return Path(str(new) + text[len(old):])
        return value

    for comp in comps:
        for side in ("condition_a", "condition_b"):
            comp[side] = {k: remap(v) for k, v in comp[side].items()}
    return comps


def pes(code: Path, data: Path, scdir: Path, march_sweeps: Path, sc: Scorer) -> dict:
    """compute-pairwise-effect-sizes.py's PV and N = 30 consensus arms, v1 and v2.

    Args:
        code: Tree. data: Clone. scdir: The class-B ``bootstrap-cis`` dir.
        march_sweeps: See :func:`remap_v2`. sc: Scorer.

    Returns:
        ``{variant: {condition_key: record}}``.
    """
    m = load_module("cpes", code / "scripts/compute-pairwise-effect-sizes.py")
    import lib_consensus as lc  # noqa: E402

    out: dict[str, Any] = {}
    for variant in ("v1", "v2"):
        if variant == "v1":
            comps = m.define_all_comparisons(scdir / "data", scdir / "pv-data")
            data_dir = scdir / "data"
            ref, bounds = m.load_shared_data(scdir / "data")
        else:
            comps = remap_v2(m.define_all_comparisons(Path("/DATA"), Path("/PV")),
                             data, march_sweeps)
            data_dir = data / "outputs"
            ref, bounds = lc.load_shared_data(data / "inputs/vectors")
        seen: dict[str, Any] = {}
        for comp in comps:
            for side in ("condition_a", "condition_b"):
                cond = comp[side]
                key = json.dumps({k: str(v) for k, v in cond.items()}, sort_keys=True)
                if key in seen:
                    continue
                if cond["type"] not in ("pv", "consensus_n30"):
                    seen[key] = {"type": cond["type"], "skipped": "loader not changed"}
                    continue
                rec = sc.arm(m._build_condition_gdf(cond, data_dir), ref, bounds)
                rec["type"] = cond["type"]
                seen[key] = rec
                print(variant, cond["type"], rec.get("moves"), flush=True)
        out[variant] = seen
    return out


def p3a(code: Path, scdir: Path, sc: Scorer) -> dict:
    """consensus-sweep-phase3a-high-text.py's consensus and PV arms.

    Args:
        code: Tree. scdir: The class-B ``bootstrap-cis`` dir. sc: Scorer.

    Returns:
        ``{arm_key: record}``.
    """
    m = load_module("p3a", code / "scripts/consensus-sweep-phase3a-high-text.py")
    data_dir, pv_dir = scdir / "data", scdir / "pv-data"
    high = data_dir / "retest/phase3a-high/track2-text"
    low = data_dir / "retest/phase3a/track2-text"
    ref, bounds = m.load_shared_data(data_dir)
    out: dict[str, Any] = {}
    for temp in m.TEMPERATURES:
        for pool, thresholds in m.POOL_CONFIGS.items():
            run_dirs = m.get_run_dirs(high, temp, pool)
            for t in thresholds:
                out[f"high|{temp}|N{pool}|t{t}"] = sc.arm(
                    m.generate_consensus_gdf(run_dirs, t), ref, bounds, m.BUFFER_METRES)
            print("high", temp, pool, flush=True)
    for pool in (5, 10, 30):
        run_dirs = m.get_run_dirs(low, "T0.7", pool)
        for t in range(1, pool + 1):
            out[f"minimal|T0.7|N{pool}|t{t}"] = sc.arm(
                m.generate_consensus_gdf(run_dirs, t), ref, bounds, m.BUFFER_METRES)
        print("minimal", pool, flush=True)
    for sub in ("09-text-5of10", "08-text-3of10"):
        gdf = m.build_pv_gdf(pv_dir / "results/phase2" / sub, pv_dir / "crops" / sub,
                             pv_dir / "sweeps/phase2" / sub)
        out[f"pv|{sub}"] = sc.arm(gdf, ref, bounds, m.BUFFER_METRES)
    return out


def main() -> int:
    """Run one section and write its records.

    Returns:
        Process exit status (0 on success).
    """
    parser = argparse.ArgumentParser(description="Measure the library copies' fix.")
    parser.add_argument("--code", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--sc", type=Path, required=True)
    parser.add_argument("--march-sweeps", type=Path)
    parser.add_argument("--section", required=True,
                        choices=("diversity-track1", "diversity-track2", "pes", "p3a"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    code = args.code.resolve()
    sys.path.insert(0, str(code))
    sys.path.insert(0, str(code / "scripts"))
    import lib_advanced_metrics as lam  # noqa: E402

    assert Path(lam.__file__).resolve().is_relative_to(code), lam.__file__
    sc = Scorer(lam)
    if args.section.startswith("diversity"):
        track = {"diversity-track1": "track1-image",
                 "diversity-track2": "track2-text"}[args.section]
        result = diversity(code, args.data, track, sc, lam)
    elif args.section == "pes":
        result = pes(code, args.data, args.sc, args.march_sweeps, sc)
    else:
        result = p3a(code, args.sc, sc)
    for name in ("analyse_diversity", "lib_consensus", "cpes", "p3a"):
        mod = sys.modules.get(name)
        if mod is not None:
            assert Path(mod.__file__).resolve().is_relative_to(code), mod.__file__
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
