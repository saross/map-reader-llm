#!/usr/bin/env python3
"""Stage the 6-crop manual review for GS-side strict (>125 m) burial-mound FPs.

Purpose
-------
The GS FP-classification driver (``scripts/gs-fp-classify.py``, v2) labelled
six of the fourteen FP-side detections at the strictest distance stratum
(> 125 m from any curator GT mound) as either ``burial-mound`` or
``triangulation-point-on-burial-mound``. The user wants to manually inspect
each of those six crops to decide whether each is:

- a genuine missed mound (curator GT incomplete) — strengthens the
  "curator-GT-incompleteness" narrative; or
- a v2 prompt over-claim — strengthens Obs 307's prompt-bias caveat; or
- an edge case where reasonable people could disagree.

This script does not adjudicate. It only **stages** the review by:

1. filtering the GS FP-classification JSON to the 6 target rows;
2. rendering each crop (150 m window, upscaled to 768 px — the exact view
   the v2 classifier saw, via ``render_crop`` re-imported from
   ``scripts/gs-fp-classify.py``);
3. saving each crop as ``crops/cand_NNNNN_<sheet>.png``;
4. emitting an ``index.md`` with embedded crops, pre-filled per-candidate
   context (sheet, coordinates, v2 label + confidence + rationale,
   distance to nearest curator GT, sheet-level FP-side rate), and a
   blank verdict field for the user to fill in.

Outputs
-------
Under ``results/gs-125m-fp-side-6-crop-review/``:

- ``crops/cand_NNNNN_<sheet>.png`` — six 768 px crop images.
- ``index.md`` — review interface with embedded crops + verdict fields.
- ``README.md`` — usage notes (written separately, not by this script).

Usage
-----
    .venv/bin/python scripts/stage_gs_125m_fp_review.py

Reproducible: idempotent, deterministic, no API calls.

Author: Shawn Ross, Claude Code (Opus 4.7)
Licence: Apache 2.0
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Path setup. Import ``render_crop`` from scripts/gs-fp-classify.py via
# importlib because the filename contains a hyphen (not a valid Python
# module identifier).
# --------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
sys.path.insert(0, str(_SCRIPT_DIR))

_FP_CLASSIFY_PATH = _SCRIPT_DIR / "gs-fp-classify.py"
_spec = importlib.util.spec_from_file_location(
    "gs_fp_classify", _FP_CLASSIFY_PATH,
)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Failed to load module from {_FP_CLASSIFY_PATH}")
_mod = importlib.util.module_from_spec(_spec)
sys.modules["gs_fp_classify"] = _mod
_spec.loader.exec_module(_mod)
render_crop = _mod.render_crop

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

FP_CLASSIFICATIONS_PATH = (
    _REPO_ROOT / "results/gs-fp-classification/fp_classifications.json"
)
OUT_DIR = _REPO_ROOT / "results/gs-125m-fp-side-6-crop-review"
CROPS_DIR = OUT_DIR / "crops"
INDEX_PATH = OUT_DIR / "index.md"

# The exact stratum in question — see report.md line 25:
# "GS-side burial-mound-adjacent share at > 125 m | 6 / 14 (42.9 %) —
#  burial-mound + triangulation-point-on-burial-mound".
DIST_THRESHOLD_M = 125.0
TARGET_CATEGORIES = {
    "burial-mound",
    "triangulation-point-on-burial-mound",
}

# Sheet-level totals (curator GT counts; verified against
# inputs/vectors/references/mounds-reference.geojson via the ``Map``
# property at staging time).
CURATOR_GT_PER_SHEET: dict[str, int] = {
    "K-35-052-4_32635": 136,
    "K-35-053-3_Elenovo": 217,
    "K-35-062-2_Rakovski": 196,
    "K-35-078-1_Lesovo": 20,
}


# --------------------------------------------------------------------------
# Main staging logic
# --------------------------------------------------------------------------


def main() -> int:
    """Render the 6 crops + emit index.md. Returns 0 on success."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CROPS_DIR.mkdir(parents=True, exist_ok=True)

    with open(FP_CLASSIFICATIONS_PATH) as f:
        all_rows = json.load(f)

    # 1. Filter to the 6 target rows: dist > 125 m AND mound-family category.
    targets = [
        r for r in all_rows
        if r.get("dist_to_nearest_curator_GT_m", 0) > DIST_THRESHOLD_M
        and r.get("category") in TARGET_CATEGORIES
    ]
    print(f"Found {len(targets)} target rows (expected 6).")
    if len(targets) != 6:
        print(
            "WARNING: target count differs from expected 6. "
            "Continuing anyway — index.md will document whatever was found.",
        )

    # 2. Compute per-sheet FP-side context for the cohort. Mirror the
    #    framing in report.md so the user has consistent denominators.
    per_sheet: dict[str, dict[str, int]] = {}
    for r in all_rows:
        m = r["map_name"]
        if m not in per_sheet:
            per_sheet[m] = {
                "total_classified": 0,
                "tp_side_50m": 0,
                "fp_side_gt125m": 0,
            }
        per_sheet[m]["total_classified"] += 1
        if r.get("bucket_primary") == "tp_side":
            per_sheet[m]["tp_side_50m"] += 1
        if r.get("dist_to_nearest_curator_GT_m", 0) > DIST_THRESHOLD_M:
            per_sheet[m]["fp_side_gt125m"] += 1

    # 3. Sort the 6 by sheet then by candidate ID for stable order.
    targets.sort(key=lambda r: (r["map_name"], int(r["candidate_id"])))

    # 4. Render each crop and persist.
    rendered: list[dict] = []
    for r in targets:
        cand_id = int(r["candidate_id"])
        sheet = r["map_name"]
        x = float(r["x"])
        y = float(r["y"])

        crop_filename = f"cand_{cand_id:05d}_{sheet}.png"
        crop_path = CROPS_DIR / crop_filename

        if crop_path.exists():
            print(f"  [skip render] cand {cand_id} — exists: {crop_path}")
        else:
            print(
                f"  [render] cand {cand_id} ({sheet}) at "
                f"({x:.1f}, {y:.1f}) -> {crop_path}",
            )
            img = render_crop(x, y)
            if img is None:
                print(
                    f"  WARNING: render_crop returned None for cand {cand_id}; "
                    "no raster covers the point. Skipping save.",
                )
                rendered.append({"row": r, "crop_path": None})
                continue
            img.save(crop_path, format="PNG")

        rendered.append(
            {"row": r, "crop_path": crop_path.relative_to(OUT_DIR)},
        )

    # 5. Write index.md.
    write_index_md(rendered, per_sheet)
    print(f"Wrote {INDEX_PATH}")
    return 0


def write_index_md(
    rendered: list[dict],
    per_sheet: dict[str, dict[str, int]],
) -> None:
    """Emit the Markdown review interface to ``index.md``."""
    lines: list[str] = []
    lines.append(
        "# GS-side strict (>125 m) FP-side burial-mound review",
    )
    lines.append("")
    lines.append(
        "**Purpose**: visual inspection of the six "
        "Gold Standard (GS)-side false positives that the v2 "
        "burial-mound FP-classifier labelled as `burial-mound` or "
        "`triangulation-point-on-burial-mound` at the strictest "
        "distance stratum (> 125 m from any curator ground-truth "
        "(GT) mound). See `results/gs-fp-classification/report.md` "
        "line 25 for the headline framing (\"6 / 14 = 42.9 %\")."
    )
    lines.append("")
    lines.append("**For each candidate, record one verdict**:")
    lines.append("")
    lines.append(
        "- `real_mound_curator_omission` — this is a real mound; "
        "curator GT is incomplete here.",
    )
    lines.append(
        "- `v2_overclaim` — v2 classifier is wrong; not a mound.",
    )
    lines.append(
        "- `edge_case_ambiguous` — reasonable people could disagree.",
    )
    lines.append("")
    lines.append(
        "Crop view: 150 m × 150 m metric window, upscaled to 768 px "
        "(matches the exact view the v2 classifier saw). Centroid "
        "is the centre pixel.",
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Per-sheet context table
    lines.append("## Per-sheet context")
    lines.append("")
    lines.append(
        "| Sheet | Curator GT | Classified detns | TP-side @ 50 m "
        "| FP-side @ > 125 m |",
    )
    lines.append("|---|---:|---:|---:|---:|")
    for s in sorted(per_sheet):
        d = per_sheet[s]
        cur = CURATOR_GT_PER_SHEET.get(s, 0)
        lines.append(
            f"| {s} | {cur} | {d['total_classified']} | "
            f"{d['tp_side_50m']} | {d['fp_side_gt125m']} |",
        )
    lines.append("")
    lines.append(
        "Note: \"TP-side @ 50 m\" = detections within 50 m of any curator "
        "GT mound (a proxy for true positive (TP), not a strict TP per "
        "the IoU-based evaluators). \"FP-side @ > 125 m\" is the "
        "strict-stratum FP set this review draws from.",
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Per-candidate sections
    lines.append("## Candidates")
    lines.append("")
    for i, item in enumerate(rendered, start=1):
        r = item["row"]
        crop_path = item["crop_path"]
        cand_id = int(r["candidate_id"])
        sheet = r["map_name"]

        lines.append(
            f"### {i}. cand {cand_id} — {sheet} — `{r['category']}`",
        )
        lines.append("")
        if crop_path is None:
            lines.append(
                "**CROP NOT RENDERED** — `render_crop` returned `None` "
                "(no raster covered this point). Investigate before "
                "adjudicating.",
            )
        else:
            lines.append(f"![cand {cand_id}]({crop_path.as_posix()})")
        lines.append("")
        lines.append("**Context**:")
        lines.append("")
        lines.append(f"- candidate ID: `{cand_id}`")
        lines.append(f"- sheet: `{sheet}`")
        lines.append(
            f"- centroid (EPSG:32635): "
            f"({r['x']:.3f}, {r['y']:.3f})",
        )
        lines.append(f"- source tile: `{r.get('source_tile', '?')}`")
        lines.append(
            "- distance to nearest curator GT mound: "
            f"**{r['dist_to_nearest_curator_GT_m']:.1f} m**",
        )
        lines.append(f"- v2 label: **`{r['category']}`**")
        lines.append(
            f"- v2 classifier confidence: {r.get('confidence', '?')}",
        )
        lines.append(
            f"- v2 classifier rationale: "
            f"\"{r.get('rationale', '').strip()}\"",
        )
        lines.append("")
        lines.append("**Verdict**:")
        lines.append("")
        lines.append("```text")
        lines.append("verdict: <real_mound_curator_omission "
                     "| v2_overclaim | edge_case_ambiguous>")
        lines.append("note: <optional one-liner>")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    INDEX_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
