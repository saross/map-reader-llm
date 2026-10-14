#!/usr/bin/env python3
"""
Write the comparison spec for the W2-11 regenerations (w2_11_sequence.sh).

Fault-window re-check (2026-10-14). For each rebuilt directory, every
committed file in the generating commit's directory (prose excluded) is
paired with the regenerated file of the same name. Declared ignores, all
machine paths: a crop manifest's ``rasters_dir`` / ``tiles_dir`` where the
original run took the extractor's ABSOLUTE default (the recorded value is
the original machine's checkout path).

Usage: python w2_11_spec.py REPO O2 SPEC_JSON

Author: Claude (Opus 5.5) for Shawn Ross; Licence: Apache 2.0
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ABS_DEFAULT_PATHS = [r"rasters_dir", r"tiles_dir"]


def ls(repo: str, commit: str, d: str) -> list[str]:
    """Files directly in ``d`` at ``commit`` (no recursion)."""
    out = subprocess.run(["git", "-C", repo, "ls-tree", "--name-only", f"{commit}:{d}"],
                         capture_output=True, text=True).stdout.split()
    return [n for n in out if "." in n]


def main() -> int:
    """Build the spec."""
    repo, o2, spec_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    spec: list[dict] = []

    def dir_pairs(label: str, regen_dir: Path, commit: str, cdir: str,
                  skip: tuple[str, ...] = (".md",)) -> None:
        for name in ls(repo, commit, cdir):
            if name.endswith(skip):
                continue
            spec.append({"label": f"{label} {name}", "regen": str(regen_dir / name),
                         "commit": commit, "path": f"{cdir}/{name}"})

    # e9d1db0d0: the three recorded merge_passes commands
    for regen, cdir in (
            ("g384_ov192_g37-consensus-n1",
             "outputs/gemini37-screen-2026-08-28/g384_ov192_g37/consensus-n1"),
            ("g384_ov192_g37-consensus-n3",
             "outputs/gemini37-screen-2026-08-28/g384_ov192_g37/consensus-n3"),
            ("g384_ov192-consensus-n5", "outputs/grid-2026-08-18/g384_ov192/consensus-n5")):
        dir_pairs(f"e9d1db0d0 {regen}", o2 / "e9d1db0d0" / regen, "e9d1db0d0", cdir)
    # 2026-09-08 consensus rebuilds
    for c, pool in (("185681674", "pro-image-high-t0"), ("185681674", "pro-text-high-t0"),
                    ("e01b8617a", "propose_brief-text"), ("e7ebc1695", "r3-hp-heavy")):
        cdir = (o2 / f"{c}-{pool}.consensus-dir").read_text().strip()
        dir_pairs(f"{c} {pool}", o2 / c / pool, c, cdir)
    dir_pairs("e7ebc1695 wbf", o2 / "e7ebc1695" / "wbf", "e7ebc1695",
              "outputs/h12-v2/wbf/r3-hp-heavy")
    # 43516df9a: crop manifests (absolute default dirs) and sweeps
    for label, stage in (
            ("pv-diag-image-t0.0-v1", "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/"
                                      "verified-v1-n10-recovery-2026-09-08"),
            ("pv-diag-text-t0.0-v1", "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/"
                                     "verified-v1-n3-recovery-2026-09-08"),
            ("e47-1of5-v1", "outputs/h11/e47-propose-brief/verified/"
                            "flash-high-text-1of5-recovery-2026-09-08")):
        r = o2 / "43516df9a" / label
        spec.append({"label": f"43516df9a {label} crop manifest",
                     "regen": str(r / "candidate_manifest.json"), "commit": "43516df9a",
                     "path": f"{stage}/crops/candidate_manifest.json",
                     "ignore": ABS_DEFAULT_PATHS})
        spec.append({"label": f"43516df9a {label} sweep_2d", "regen": str(r / "sweep_2d.json"),
                     "commit": "43516df9a", "path": f"{stage}/sweep_2d.json"})
    # f8e0eb600: crop manifests, carry records, sweeps
    v = "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37"
    g = "outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder/k5_recovery-fixed"
    for key, crops, stage, sweeps in (
            ("k1", f"{v}/crops_k1_recovery-fixed", f"{v}/verify_k1_recovery-fixed",
             ("sweep_2d_era2b.json", "sweep_2d.json")),
            ("k3", f"{v}/crops_k3_recovery-fixed", f"{v}/verify_k3_recovery-fixed",
             ("sweep_2d_era2b.json", "sweep_2d.json")),
            ("k5", f"{g}/crops", g, ("sweep_board.json", "sweep_era2.json"))):
        r = o2 / "f8e0eb600" / key
        spec.append({"label": f"f8e0eb600 {key} crop manifest",
                     "regen": str(r / "candidate_manifest.json"), "commit": "f8e0eb600",
                     "path": f"{crops}/candidate_manifest.json"})
        spec.append({"label": f"f8e0eb600 {key} carry_provenance",
                     "regen": str(r / "carry" / "carry_provenance.json"),
                     "commit": "f8e0eb600", "path": f"{stage}/carry_provenance.json"})
        if key == "k5":  # no call was made: the seeded file IS the stage's file
            spec.append({"label": "f8e0eb600 k5 probabilities (all carried)",
                         "regen": str(r / "carry" / "probabilities.json"),
                         "commit": "f8e0eb600", "path": f"{stage}/probabilities.json"})
        for s in sweeps:
            spec.append({"label": f"f8e0eb600 {key} {s}", "regen": str(r / s),
                         "commit": "f8e0eb600", "path": f"{stage}/{s}"})
    # image campaign unions, provenance sidecars and crop manifests
    for c, out, cell, ks in (
            ("b9d4032bb", "outputs/gemini37-image-55map-2026-09-13", "g384_ov192_55map_g37img",
             (1, 3)),
            ("bd5de9f80", "outputs/gemini37-image-55map-2026-09-13", "g384_ov192_55map_g37img",
             (5,)),
            ("7d61f1ff9", "outputs/gemini3-image-55map-2026-09-16", "g384_ov192_55map_g3img",
             (1, 3, 5))):
        r = o2 / "image-unions" / c
        vr = f"{out}/verifier/{cell}"
        for k in ks:
            spec.append({"label": f"{c} {cell} union_k{k}", "regen": str(r / f"union_k{k}.geojson"),
                         "commit": c, "path": f"{vr}/union_k{k}.geojson"})
            spec.append({"label": f"{c} {cell} union_k{k} pass provenance",
                         "regen": str(r / f"union_k{k}_pass_provenance.json"),
                         "commit": c, "path": f"{vr}/union_k{k}_pass_provenance.json"})
            if "g37img" in cell:
                spec.append({"label": f"{c} {cell} crops_k{k} manifest",
                             "regen": str(r / f"crops_k{k}" / "candidate_manifest.json"),
                             "commit": c, "path": f"{vr}/crops_k{k}/candidate_manifest.json",
                             "ignore": ABS_DEFAULT_PATHS})
    spec_path.write_text(json.dumps(spec, indent=1) + "\n")
    print(f"{len(spec)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
