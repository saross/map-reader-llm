#!/usr/bin/env python3
"""
Write the comparison spec for the W1-8 (Run B) regenerations.

Fault-window re-check (2026-10-14). Pairs every regenerated file under
OUT (runb_sequence.sh) with the committed file and the commit that
generated it, for compare_files.py. The only declared ignores: the
validate-chain record's ``…comparison.built`` (the scratch path the rebuilt
union was written to, a machine path), and log lines' wall-clock stamps.

Usage: python runb_spec.py OUT SPEC_JSON

Author: Claude (Opus 5.5) for Shawn Ross; Licence: Apache 2.0
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

B = "outputs/modality-bridge-2026-10-07"
#: arm -> (K, union/manifest adding commit, provenance/metas commit, coverage commit)
ARMS = {
    "g3-text": (10, "2b6edde9a", "2b6edde9a", "2b6edde9a"),
    "g3-image": (10, "2b6edde9a", "2b6edde9a", "2b6edde9a"),
    "g3-text-temp1": (5, "2b6edde9a", "2b6edde9a", "2b6edde9a"),
    "g3-image-temp1": (5, "2b6edde9a", "2b6edde9a", "2b6edde9a"),
    "g37-text": (5, "a3ea389c2", "a3ea389c2", "a3ea389c2"),
    "g37-image-cache": (5, "94be8b01a", "a3ea389c2", "94be8b01a"),
    "g37-image": (5, "69eb32132", "69eb32132", "69eb32132"),
}
#: repaired copy -> adding commit
REPAIRS = {("g3-image-temp1", "g3"): "2b6edde9a", ("g37-text", "g3"): "3c155685a",
           ("g37-text", "g37"): "3c155685a", ("g37-image-cache", "g3"): "94be8b01a",
           ("g37-image-cache", "g37"): "94be8b01a", ("g37-image", "g3"): "69eb32132",
           ("g37-image", "g37"): "69eb32132"}
TS = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}"


def ver(arm: str) -> str:
    """Config version directory for an arm."""
    return "detect_brief-text-image" if "image" in arm else "detect_brief-text"


def main() -> int:
    """Build the spec."""
    out, spec_path = Path(sys.argv[1]), Path(sys.argv[2])
    spec = []
    for arm, (k, add, chk, cov) in ARMS.items():
        r = out / "regen" / arm
        vr = f"{B}/{arm}/verifier/{ver(arm)}"
        spec += [
            {"label": f"{arm} union", "regen": str(r / f"union_k{k}.geojson"),
             "commit": add, "path": f"{vr}/union_k{k}.geojson"},
            {"label": f"{arm} union build record", "regen": str(r / f"union_k{k}.build.json"),
             "commit": add, "path": f"{vr}/union_k{k}.build.json"},
            {"label": f"{arm} crop manifest", "regen": str(r / "candidate_manifest.json"),
             "commit": add, "path": f"{vr}/crops/candidate_manifest.json"},
            {"label": f"{arm} provenance check", "regen": str(r / "provenance.json"),
             "commit": chk, "path": f"{B}/stage2/checks/{arm}-provenance.json"},
            {"label": f"{arm} coverage check", "regen": str(r / "coverage.json"),
             "commit": cov, "path": f"{B}/stage2/checks/{arm}-coverage.json"},
            {"label": f"{arm} metas check", "regen": str(r / "metas.json"),
             "commit": chk, "path": f"{B}/stage2/checks/{arm}-metas.json"},
            {"label": f"{arm} union log", "regen": str(r / "union.log"), "commit": add,
             "path": f"{B}/stage2/logs/union-{arm}.log", "strip_re": r"^=== "},
            {"label": f"{arm} extract log", "regen": str(r / "extract.log"), "commit": add,
             "path": f"{B}/stage2/logs/extract-{arm}.log", "strip_re": r"^=== ",
             "sub_re": TS},
        ]
    for (arm, v), add in REPAIRS.items():
        leg = f"{B}/{arm}/verifier/{ver(arm)}/verify_{v}_repaired"
        for name in ("parse_repair.json", "probabilities.json", "run.meta.json"):
            spec.append({"label": f"{arm}:{v} repaired {name}",
                         "regen": str(out / "repair" / f"{arm}-{v}" / name),
                         "commit": add, "path": f"{leg}/{name}"})
    spec.append({"label": "validate-chain", "regen": str(out / "validate/validate-chain.json"),
                 "commit": "2b6edde9a", "path": f"{B}/stage2/checks/validate-chain.json",
                 "ignore": [r"originals\..*\.comparison\.built"]})
    spec.append({"label": "anchor-gate", "regen": str(out / "anchor/anchor-gate.json"),
                 "commit": "2b6edde9a", "path": f"{B}/stage2/checks/anchor-gate.json"})
    spec_path.write_text(json.dumps(spec, indent=1) + "\n")
    print(f"{len(spec)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
