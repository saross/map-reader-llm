#!/usr/bin/env python3
"""Summarise the sweep-optimism runs of the GS Era-2 board's screen cells.

Reads every ``selection_aware_intervals.py --sweep-union`` artefact under
``<board>/optimism/`` (one per cell and frame: ``<slug>_committed_b20_m1.json``
on the cell's committed frame, ``<slug>_board_b20_m1.json`` on the board
frame) and writes ``<board>/optimism/README.md``: per cell and frame the
candidate count, the apparent (argmax) F1, the Efron–Gong optimism with its
Monte Carlo standard error, the corrected F1, the selection-aware 95 %
interval, the argmax stability, and the two gates (the committed sweep
reproduced row for row; the argmax equal to the committed evaluation).

Usage::

    python scripts/summarise_sweep_optimism.py [--board-dir DIR]
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BOARD = REPO_ROOT / "results/leaderboard/era2/gs-era2-verified-board-2026-09-10"


def load_runs(opt_dir: Path) -> list[dict]:
    """Every optimism artefact in the directory, tagged by cell and frame."""
    runs = []
    for path in sorted(opt_dir.glob("*_b20_m1.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        stem = path.name[: -len("_b20_m1.json")]
        cell, _, frame = stem.rpartition("_")
        sel = doc["candidates"][doc["selected_index"]]
        runs.append({
            "cell": cell, "frame": frame, "file": path.name,
            "n_candidates": doc["n_candidates"], "apparent": doc["apparent_f1"],
            "optimism": doc["optimism"], "mcse": doc["optimism_mcse"],
            "corrected": doc["corrected_f1"], "sa_ci": doc["selection_aware_ci"],
            "naive_ci": doc["naive_ci"], "stability": doc["argmax_stability"],
            "n_distinct": doc["n_distinct_argmax"], "selected": sel.get("label"),
            "gate_csv": (doc.get("gate_sweep_csv") or {}).get("rows"),
            "gate_anchor_delta": (doc.get("gate_anchor_eval") or {}).get("delta"),
            "bounds": Path(doc.get("bounds", "")).name,
        })
    return runs


def render(runs: list[dict]) -> str:
    """The README body."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        "# Sweep optimism of the screen cells (Efron–Gong, argmax replayed per tile resample)",
        "",
        f"> **Last revised**: {now[:10]} (original publication). Instrument: "
        "`scripts/selection_aware_intervals.py --sweep-union` (the verifier "
        "(prob_t × min_votes) sweep rebuilt in process as the candidate set; "
        "10,000 tile resamples, seed 42, 20 m). Each cell is run on its committed "
        "frame (grid-common; gate: the screen's committed `sweep_20m.csv` reproduced "
        "row for row) and on the board frame (`era2-b-487`; gate: the argmax equals "
        "the board cell's evaluation to four decimals). See [§ Changelog](#changelog).",
        "",
        "Optimism = apparent F1 − the mean out-of-resample F1 of the replayed argmax; "
        "corrected = apparent − optimism. Argmax stability = the share of resamples "
        "that pick the committed operating point.",
        "",
        "| cell | frame | candidates | apparent F1 | optimism (MCSE) | corrected F1 | "
        "selection-aware 95 % | argmax stability | gates |",
        "|---|---|---:|---:|---:|---:|---|---:|---|",
    ]
    for r in sorted(runs, key=lambda x: (x["cell"], x["frame"] != "committed")):
        gates = []
        if r["gate_csv"] is not None:
            gates.append(f"sweep {r['gate_csv']} rows")
        if r["gate_anchor_delta"] is not None:
            gates.append(f"anchor Δ {r['gate_anchor_delta']:+.1e}")
        lines.append(
            f"| `{r['cell']}` | {r['frame']} | {r['n_candidates']} | {r['apparent']:.4f} | "
            f"{r['optimism']:+.4f} ({r['mcse']:.5f}) | **{r['corrected']:.4f}** | "
            f"[{r['sa_ci'][0]:.4f}, {r['sa_ci'][1]:.4f}] | {r['stability']:.3f} "
            f"({r['n_distinct']} winners) | {'; '.join(gates) or '—'} |"
        )
    board = [r for r in runs if r["frame"] == "board"]
    if board:
        lines += ["", f"Board frame: optimism ranges {min(r['optimism'] for r in board):+.4f} to "
                  f"{max(r['optimism'] for r in board):+.4f} over {len(board)} cells (the board's "
                  "own tier margins are in `tiering_20m.json`).", ""]
    lines += ["## Changelog", "", f"### {now[:10]} — Original publication", "",
              "Run on sapphire (S152) for the board's symmetry fix (card changelog 2026-09-10 later)."]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--board-dir", type=Path, default=DEFAULT_BOARD)
    args = ap.parse_args()
    opt_dir = args.board_dir / "optimism"
    runs = load_runs(opt_dir)
    if not runs:
        raise SystemExit(f"no optimism artefacts under {opt_dir}")
    (opt_dir / "README.md").write_text(render(runs), encoding="utf-8")
    (opt_dir / "summary.json").write_text(json.dumps(runs, indent=1) + "\n", encoding="utf-8")
    print(f"{len(runs)} runs summarised -> {opt_dir / 'README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
