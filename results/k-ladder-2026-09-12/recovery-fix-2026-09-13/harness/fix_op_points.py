#!/usr/bin/env python3
"""
Restore the tier-E row to operating-points.json and make its paths portable.

The re-score driver writes ``operating-points.json`` wholesale, so the second
invocation (the three Gemini 3.7 cells) overwrote the first one's tier-E row.
This rebuilds that row from COMMITTED artefacts — the stage's own
``sweep_board.json`` and ``sweep_era2.json``, and the reproduced
``evaluation.json`` — rather than from a transcript, and rewrites the absolute
scratch paths as repository-relative ones.

The argmax tie-break is restated here exactly as
``score_k_ladder_phase2_rungs.argmax_at_headline`` documents it — highest F1 at
the headline buffer, then lowest ``vote_t``, then lowest ``prob_t`` — and the
result is asserted against the operating point the committed cell recorded, so a
mistake in restating it cannot pass silently.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("results/k-ladder-2026-09-12/recovery-fix-2026-09-13")
STAGE = Path("outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder/k5_recovery-fixed")
HEADLINE = 20


def argmax(sweep: Path) -> dict:
    """Return the sweep's F1 argmax at the headline buffer, with tie count."""
    rows = [r for r in json.loads(sweep.read_text()) if r["buffer_m"] == HEADLINE]
    best = max(rows, key=lambda r: (r["f1"], -r["vote_t"], -r["prob_t"]))
    ties = [
        r
        for r in rows
        if r["f1"] == best["f1"]
        and (r["vote_t"], r["prob_t"]) != (best["vote_t"], best["prob_t"])
    ]
    return {**best, "n_ties": len(ties)}


def main() -> None:
    """Insert the tier-E row and normalise every materialised path."""
    board = argmax(STAGE / "sweep_board.json")
    era2 = argmax(STAGE / "sweep_era2.json")

    assert (board["vote_t"], board["prob_t"]) == (5, 0.15), (
        f"tier-E argmax moved to {(board['vote_t'], board['prob_t'])} — "
        "that would contradict the committed operating point and must not be "
        "written silently"
    )

    evaluation = json.loads(
        (ROOT / "reproduced-k5-evaluation" / "evaluation.json").read_text()
    )
    summary = evaluation["summary"]
    row = next(r for r in summary["buffers"] if r["buffer_metres"] == HEADLINE)
    tile = summary["tile_classification"]

    k5 = {
        "key": "k5",
        "run_id": "grid-2026-08-18",
        "label": "g384-ov192-k5-verified-opmax",
        "committed_point": [5, 0.15],
        "new_point": [5, 0.15],
        "point_moved": False,
        "board_argmax": {
            "vote_t": board["vote_t"],
            "prob_t": board["prob_t"],
            "f1": board["f1"],
            "n": board["n"],
            "n_ties": board["n_ties"],
        },
        "era2_argmax": {
            "vote_t": era2["vote_t"],
            "prob_t": era2["prob_t"],
            "f1": era2["f1"],
        },
        "frames_agree": (board["vote_t"], board["prob_t"])
        == (era2["vote_t"], era2["prob_t"]),
        "committed_f1_20": 0.8905,
        "new_f1_20": row["f1"],
        "new_f1_ci_20": [row["f1_ci_lower"], row["f1_ci_upper"]],
        "new_precision_20": row["precision"],
        "new_recall_20": row["recall"],
        "committed_n_detections": 435,
        "new_n_detections": summary["n_detections"],
        "new_tile_mcc": tile["mcc"]["point"],
        "new_tile_confusion": tile["confusion"],
        "tile_mcc_withheld": None,
        "tile_mcc_withheld_reason": None,
        "cell_dir": str(ROOT / "reproduced-k5-evaluation"),
        "materialised": str(ROOT / "materialised" / "k5.geojson"),
        "evaluated": True,
        "evaluation_note": (
            "full recorded recipe; summary block is dict-identical to the "
            "committed results/k-ladder-2026-09-12/tier-e/cells/"
            "grid-2026-08-18__g384-ov192-k5-verified-opmax/evaluation.json"
        ),
    }

    k5["delta_f1_20"] = round(k5["new_f1_20"] - k5["committed_f1_20"], 4)

    path = ROOT / "operating-points.json"
    rows = json.loads(path.read_text())
    rows = [r for r in rows if r["key"] != "k5"]
    for entry in rows:
        name = Path(entry["materialised"]).name
        entry["materialised"] = str(ROOT / "materialised" / name)
        # The driver could not evaluate these three (the tile-join invariant
        # refuses their per-tile table), so backfill the F1 arm from the
        # f1_only.py measurement, making this file self-contained.
        measurement = ROOT / "f1-only" / f"{entry['key']}.json"
        entry["cell_dir"] = None
        entry["f1_only_measurement"] = str(measurement)
        if measurement.is_file():
            data = json.loads(measurement.read_text())
            after = data["sets"]["after"]["per_buffer"][str(HEADLINE)]
            before = data["sets"]["before"]["per_buffer"][str(HEADLINE)]
            entry["new_f1_20"] = after["f1"]
            entry["new_precision_20"] = after["precision"]
            entry["new_recall_20"] = after["recall"]
            entry["new_n_detections"] = data["sets"]["after"]["n_detections"]
            entry["delta_f1_20"] = round(after["f1"] - before["f1"], 4)
            entry["new_f1_ci_20"] = None
            entry["new_tile_mcc"] = None
            entry["tile_mcc_withheld"] = True
            entry["tile_mcc_withheld_reason"] = data["withheld"][
                "tile_classification"
            ]
    rows.append(k5)
    path.write_text(json.dumps(rows, indent=2) + "\n")
    print("rows now:", [r["key"] for r in rows])
    print("k5 F1@20:", k5["new_f1_20"], "MCC:", k5["new_tile_mcc"])
    print("k5 board argmax:", k5["board_argmax"])


if __name__ == "__main__":
    main()
