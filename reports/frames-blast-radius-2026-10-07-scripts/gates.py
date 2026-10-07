"""Validation gates (ii) and (iii) for the geometric detection-scope wrapper.

Frames blast-radius measurement, Session 163 (2026-10-07). Read-only.

Gate (ii): with the wrapper ON, reproduce the clipped numbers of
``reports/k-ladder-frames-2026-10-07.md`` § 4 for the Gemini 3.7 gold-standard (GS) ladder's
K = 1 and K = 3 operating points (board frame 0.8747 / 0.9135; detections clipped to the
grid-common footprint, still scored on the board frame, 0.8682 / 0.9073). Both the direct
wrapper (``geometric_detection_scope``) and the monkeypatch path (``patched_scorers``) are
exercised, since the sweep re-runs use the latter.

Gate (iii): a red sentinel. The wrapper is deliberately broken (every prefix-matched
detection scoped to an EMPTY tile set) on the same two cells and on one cell with no
out-of-frame detection; the outputs must change, which proves the wrapper is in the
scoring path rather than bypassed.

Usage::

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python gates.py --repo ~/Code/map-reader-llm \
        --out out/gates.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blast_lib as bl  # noqa: E402

BOARD = "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"
GRID_COMMON = "outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson"
GT = "inputs/vectors/references/mounds-reference.geojson"
OPS = "results/k-ladder-2026-09-12/phase2/operating-points.json"
#: A board cell with no out-of-frame detection, for the sentinel's control.
CONTROL = "results/k-ladder-2026-09-12/phase2/materialised/pv-min-text-t1.0-n3-opmax.geojson"
#: Expected values, reports/k-ladder-frames-2026-10-07.md § 4 table (and its
#: universe_counterfactual.out): (committed, clip-board, clip-grid-common).
EXPECTED = {27: (0.8495, 0.8747, 0.8682), 28: (0.8860, 0.9135, 0.9073)}


def f1(det: Any, ref: Any, bounds: Any) -> float:
    """Project point F1 at 20 m."""
    return float(bl.LIB.calculate_f1_internal(det, ref, bounds, buffer_metres=20)[2])


def main() -> int:
    """Run gates (ii) and (iii) and write a JSON record."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    bl.add_repo_to_path(repo)
    board = bl.load_geojson(repo / BOARD)
    grid = bl.load_geojson(repo / GRID_COMMON)
    ref = bl.load_geojson(repo / GT)
    ops = {r["row"]: r for r in json.loads((repo / OPS).read_text())["rungs"]}
    record: dict[str, Any] = {"gate_ii": [], "gate_iii": []}
    all_ok = True
    for row, (exp_off, exp_board, exp_grid) in EXPECTED.items():
        path = ops[row]["opmax"]["detections"]
        det = bl.load_detections(repo / path, board)
        off = f1(det, ref, board)
        on_board, diag = bl.geometric_detection_scope(det, board)
        on = f1(on_board, ref, board)
        # Grid-common clip: detections scoped to grid-common geometry, references board-scoped.
        on_grid, diag_g = bl.geometric_detection_scope(det, grid)
        clip_grid = f1(on_grid, ref, board)
        with bl.patched_scorers("geometric") as counter:
            patched = f1(det, ref, board)
        ok = all(abs(round(a, 4) - b) < 1e-9 for a, b in (
            (off, exp_off), (on, exp_board), (clip_grid, exp_grid), (patched, exp_board)))
        all_ok &= ok
        record["gate_ii"].append({
            "row": row, "detections": path, "n": len(det),
            "off": off, "on_board": on, "clip_grid_common_scored_on_board": clip_grid,
            "patched_path_on_board": patched, "patched_calls": counter["calls"],
            "dropped_board": diag["n_out_of_frame"], "dropped_grid": diag_g["n_out_of_frame"],
            "expected": {"off": exp_off, "board": exp_board, "grid_common": exp_grid},
            "pass": ok,
        })
        print(f"gate ii row {row}: off {off:.4f} on {on:.4f} grid {clip_grid:.4f} "
              f"patched {patched:.4f} -> {'PASS' if ok else 'FAIL'}")
    record["gate_ii_pass"] = all_ok

    sentinel_ok = True
    for label, path in (("row27", ops[27]["opmax"]["detections"]),
                        ("row28", ops[28]["opmax"]["detections"]), ("control", CONTROL)):
        det = bl.load_detections(repo / path, board)
        on, _ = bl.geometric_detection_scope(det, board)
        broken, _ = bl.geometric_detection_scope(det, board, sentinel_empty=True)
        good = f1(on, ref, board)
        bad = f1(broken, ref, board) if len(broken) else 0.0
        with bl.patched_scorers("sentinel"):
            bad_patched = f1(det, ref, board)
        changed = abs(good - bad) > 1e-6 and abs(good - bad_patched) > 1e-6
        sentinel_ok &= changed
        record["gate_iii"].append({
            "cell": label, "detections": path, "on": good, "sentinel_direct": bad,
            "n_after_sentinel": len(broken), "sentinel_patched": bad_patched,
            "outputs_changed": changed,
        })
        print(f"gate iii {label}: on {good:.4f} sentinel {bad:.4f} / patched {bad_patched:.4f}"
              f" -> {'RED (changed)' if changed else 'NOT RED'}")
    # After the context managers exit, the library must be restored.
    det = bl.load_detections(repo / ops[27]["opmax"]["detections"], board)
    restored = f1(det, ref, board)
    record["restored_after_patch"] = restored
    record["gate_iii_pass"] = sentinel_ok and abs(round(restored, 4) - 0.8495) < 1e-9
    print(f"library restored: {restored:.4f}; gate iii "
          f"{'PASS' if record['gate_iii_pass'] else 'FAIL'}")
    args.out.write_text(json.dumps(record, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
