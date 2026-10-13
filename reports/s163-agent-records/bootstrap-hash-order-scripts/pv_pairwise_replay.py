#!/usr/bin/env python3
"""
Replay the D42 class-B B-17/B-18 "as is" PV pairwise comparisons (ruling D63).

``evaluate_pv_results.py compare --pairwise`` calls ``bootstrap_effect_size_ci``,
whose tile order followed the string-hash seed. This replay repeats the
steps of ``reports/d42-implementation-2026-10-05-scripts/run_classb.sh``
(steps ``b17-asis`` and ``b18-asis``): it writes the March-named sweep copies
with resolvable input paths, then runs the same ``compare`` command, inside
the code tree under test (the working directory; ``script_replay.py`` sets
it) instead of ``/tmp/regen-b``.

Usage::

    python pv_pairwise_replay.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Build the sweep copies and run both comparisons; return the worst exit code."""
    root = Path.cwd()
    sweeps = root / "replay-sweeps" / "h11-384-pv-diagnostic"
    # Same mapping as run_classb.sh: March "flash" = today's "minimal",
    # March "pro" = today's "medium".
    for track in ("text", "image"):
        for old, new in (("flash", "minimal"), ("pro", "medium")):
            src = (root / "results/h11-384-pv-diagnostic" / f"pro-{track}-{new}-verifier"
                   / "threshold_sweep.json")
            data = json.loads(src.read_text())
            pv = root / "outputs/h11/pv-diag-384"
            data["probabilities_file"] = str(
                pv / "verified" / f"pro-{track}-{new}-verifier" / "probabilities.json")
            data["manifest_file"] = str(
                pv / "crops" / f"pro-medium-{track}-baseline" / "candidate_manifest.json")
            out = sweeps / f"pro-{track}-{old}-verifier"
            out.mkdir(parents=True, exist_ok=True)
            (out / "threshold_sweep.json").write_text(json.dumps(data, indent=2))
    worst = 0
    for track in ("text", "image"):
        cmd = [sys.executable, "scripts/evaluate_pv_results.py",
               "--bounds", "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
               "compare", "--sweep-dirs",
               str(sweeps / f"pro-{track}-flash-verifier"),
               str(sweeps / f"pro-{track}-pro-verifier"),
               "--output-dir", f"out/{track}-asis", "--pairwise",
               "--bootstrap", "1000", "--seed", "42"]
        worst = max(worst, subprocess.run(cmd, cwd=root, check=False).returncode)
    return worst


if __name__ == "__main__":
    sys.exit(main())
