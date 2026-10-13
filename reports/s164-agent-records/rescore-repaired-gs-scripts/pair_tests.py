#!/usr/bin/env python3
"""
Run the 3.7 image gap test and the Arm V pair test against this copy's sets.

Part of the S164 re-score. ``gemini37_image_gap_test.py`` and
``gemini38_armv_pair_test.py`` gate each side's per-tile micro-F1 against a
hand-typed committed F1 (0.9139, 0.9254, 0.9265, 0.9308) before they test.
Under the repaired reading those sets move by design, so the gates would
refuse for a change of data, not of instrument. This wrapper runs both
scripts' own ``main`` unchanged, with only the gate constants replaced by the
values this copy's regenerated ``analysis.json`` files record (the same F1 the
scripts' parameterised ``--pair`` mode reads), and the Gemini 3 reference gap
by this copy's Image-B head-to-head. In an ORIGIN copy every replaced value
equals the committed constant, so the outputs must equal the committed files.

Usage: python pair_tests.py <copy_dir> {gap,armv}

Zero API. Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

COPY = Path(sys.argv[1]).resolve()
WHICH = sys.argv[2]
sys.path.insert(0, str(COPY))


def best_f1(rel: str) -> float:
    """``image_best.f1`` of one regenerated image_b_analysis output."""
    return float(json.loads((COPY / rel / "analysis.json").read_text())["image_best"]["f1"])


if WHICH == "gap":
    from scripts import gemini37_image_gap_test as gt

    g37 = "results/gemini37-screen-2026-08-28"
    img = "results/gemini37-image-gs-2026-09-01"
    gt.PAIRS = [
        ("carried-verifier",
         COPY / f"{g37}/verified_best_20m.geojson", round(best_f1(g37), 4),
         COPY / f"{img}/arm1/verified_best_20m.geojson", round(best_f1(f"{img}/arm1"), 4)),
        ("all-3.7",
         COPY / f"{g37}/swap37/verified_best_20m.geojson", round(best_f1(f"{g37}/swap37"), 4),
         COPY / f"{img}/arm2/verified_best_20m.geojson", round(best_f1(f"{img}/arm2"), 4)),
    ]
    head = json.loads((COPY / "results/image-b-gs-2026-08-28/analysis.json").read_text())[
        "head_to_head_20m"]
    gt.G3_GAP = {"delta_f1": round(float(head["observed_diff"]), 4),
                 "p": round(float(head["p_value"]), 3),
                 "source": "results/image-b-gs-2026-08-28/analysis.json"}
    print("gap test constants:", [(p[0], p[2], p[4]) for p in gt.PAIRS], gt.G3_GAP)
    sys.exit(gt.main([]))
elif WHICH == "armv":
    from scripts import gemini38_armv_pair_test as av

    g37 = "results/gemini37-screen-2026-08-28"
    av.INCUMBENTS = [
        ("all-3.7", COPY / f"{g37}/swap37/verified_best_20m.geojson",
         round(best_f1(f"{g37}/swap37"), 4)),
        ("carried-G3", COPY / f"{g37}/verified_best_20m.geojson", round(best_f1(g37), 4)),
    ]
    print("armV constants:", [(i[0], i[2]) for i in av.INCUMBENTS])
    sys.argv = [sys.argv[0]]
    sys.exit(av.main())
else:
    raise SystemExit(f"unknown test {WHICH!r}")
