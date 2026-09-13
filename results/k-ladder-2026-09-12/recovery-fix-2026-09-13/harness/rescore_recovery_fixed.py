#!/usr/bin/env python3
"""
Re-score the four K-ladder cells whose unions were rebuilt for the drop fix
==========================================================================

Description:
    The recovery-fragment fix (commit ``75d7c8d4c``) changed five committed
    consensus unions, which four registered conditions read. This script
    re-runs those four cells on their **recorded** recipes, against the
    rebuilt unions and the extended verifier stages, without touching the
    committed drivers.

    It deliberately **imports** the selection logic from the committed
    drivers rather than restating it — ``argmax_at_headline`` and
    ``cell_dir_name`` from ``score_k_ladder_phase2_rungs``, and
    ``reassign_carrier_tiles`` from ``run_k_ladder_tier_e`` — so the
    operating point is chosen, the cell named, and the tier-E carrier tiles
    re-keyed by exactly the same code that produced the committed cells. Only
    the input paths differ: the ``*_recovery-fixed`` stages instead of the
    originals.

    Steps per cell, mirroring the drivers:

    1. sweep the 2-D (vote, probability) grid on the board frame AND on the
       Era-2 frame (``sweep_f1_greedy_pv.py``);
    2. take the board frame's argmax at the headline buffer (ruling R2) and
       compare it with the family's carried point;
    3. materialise the operating point (``materialise_pv_geojson.py``);
    4. for tier E only, re-key ``source_tile`` to the board frame's 336 px
       stride vocabulary, without which the tile-join invariant refuses the
       cell;
    5. evaluate on the recorded recipe — curator reference, board frame,
       14 buffers, 10,000 BCa draws, seed 42, MCC.

Usage::

    python rescore_recovery_fixed.py --out-root ~/scratch/recovery-drop-fix/rescore
    python rescore_recovery_fixed.py --out-root … --only k5   # one cell

Outputs:
    <out-root>/<cell dir>/evaluation.{json,csv,md}  — the re-scored cells
    <out-root>/operating-points.json                — chosen points, and
        whether each moved relative to the committed one
    the sweeps, in each ``*_recovery-fixed`` verifier stage directory

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
# The repository root is passed in; see --repo.

logger = logging.getLogger("rescore")


def load_driver_bits(repo: Path) -> dict[str, Any]:
    """Import the committed drivers' selection helpers.

    Args:
        repo: Repository root, prepended to ``sys.path`` so ``scripts.*``
            imports resolve.

    Returns:
        Mapping of helper name to the imported callable or constant.
    """
    sys.path.insert(0, str(repo))
    from scripts.score_k_ladder_phase2_rungs import (  # noqa: E402
        BOARD_BOUNDS,
        BOOTSTRAP,
        BUFFERS,
        ERA2_BOUNDS,
        GROUND_TRUTH,
        HEADLINE_BUFFER,
        SEED,
        SWEEP_BUFFERS,
        argmax_at_headline,
        cell_dir_name,
    )
    from scripts.run_k_ladder_tier_e import reassign_carrier_tiles  # noqa: E402

    return {
        "BOARD_BOUNDS": BOARD_BOUNDS,
        "ERA2_BOUNDS": ERA2_BOUNDS,
        "GROUND_TRUTH": GROUND_TRUTH,
        "BUFFERS": BUFFERS,
        "SWEEP_BUFFERS": SWEEP_BUFFERS,
        "BOOTSTRAP": BOOTSTRAP,
        "SEED": SEED,
        "HEADLINE_BUFFER": HEADLINE_BUFFER,
        "argmax_at_headline": argmax_at_headline,
        "cell_dir_name": cell_dir_name,
        "reassign_carrier_tiles": reassign_carrier_tiles,
    }


#: The four cells, with the rebuilt inputs each must read. ``committed_point``
#: and ``committed_f1`` are the values recorded in the cell's own
#: ``evaluation.json`` and ``operating-points.json``, carried here so the
#: script can report before -> after rather than only after.
CELLS: list[dict[str, Any]] = [
    {
        "key": "k1-opmax",
        "run_id": "gemini37-screen-2026-08-28",
        "label": "g37-text-k1-verified-opmax",
        "sweep_config": "g384_ov192_g37-n1",
        "consensus": (
            "outputs/gemini37-screen-2026-08-28/g384_ov192_g37/"
            "consensus-n1/consensus_t1.geojson"
        ),
        "crops": (
            "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/"
            "crops_k1_recovery-fixed"
        ),
        "verify": (
            "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/"
            "verify_k1_recovery-fixed"
        ),
        "board_sweep_name": "sweep_2d_era2b.json",
        "era2_sweep_name": "sweep_2d.json",
        "point": "opmax",
        "carried_prob": 0.10,
        "n_passes": 1,
        "committed_point": (1, 0.15),
        "committed_f1_20": 0.8495,
        "committed_n_detections": 502,
        "carrier_rekey": False,
        "committed_cell": (
            "results/k-ladder-2026-09-12/phase2/cells/"
            "gemini37-screen-2026-08-28__g37-text-k1-verified-opmax"
        ),
    },
    {
        "key": "k1-carried",
        "run_id": "gemini37-screen-2026-08-28",
        "label": "g37-text-k1-verified-carried-p0.10-k1",
        "sweep_config": "g384_ov192_g37-n1",
        "consensus": (
            "outputs/gemini37-screen-2026-08-28/g384_ov192_g37/"
            "consensus-n1/consensus_t1.geojson"
        ),
        "crops": (
            "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/"
            "crops_k1_recovery-fixed"
        ),
        "verify": (
            "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/"
            "verify_k1_recovery-fixed"
        ),
        "board_sweep_name": "sweep_2d_era2b.json",
        "era2_sweep_name": "sweep_2d.json",
        "point": "carried",
        "carried_prob": 0.10,
        "n_passes": 1,
        "committed_point": (1, 0.10),
        "committed_f1_20": 0.8338,
        "committed_n_detections": 558,
        "carrier_rekey": False,
        "committed_cell": (
            "results/k-ladder-2026-09-12/phase2/cells/"
            "gemini37-screen-2026-08-28__g37-text-k1-verified-carried-p0_10-k1"
        ),
    },
    {
        "key": "k3-opmax",
        "run_id": "gemini37-screen-2026-08-28",
        "label": "g37-text-k3-verified-opmax",
        "sweep_config": "g384_ov192_g37-n3",
        "consensus": (
            "outputs/gemini37-screen-2026-08-28/g384_ov192_g37/"
            "consensus-n3/consensus_t1.geojson"
        ),
        "crops": (
            "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/"
            "crops_k3_recovery-fixed"
        ),
        "verify": (
            "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/"
            "verify_k3_recovery-fixed"
        ),
        "board_sweep_name": "sweep_2d_era2b.json",
        "era2_sweep_name": "sweep_2d.json",
        "point": "opmax",
        "carried_prob": 0.10,
        "n_passes": 3,
        "committed_point": (3, 0.10),
        "committed_f1_20": 0.8870,
        "committed_n_detections": 494,
        "carrier_rekey": False,
        "committed_cell": (
            "results/k-ladder-2026-09-12/phase2/cells/"
            "gemini37-screen-2026-08-28__g37-text-k3-verified-opmax"
        ),
    },
    {
        "key": "k5",
        "run_id": "grid-2026-08-18",
        "label": "g384-ov192-k5-verified-opmax",
        "sweep_config": "brief-text-g384-ov192-k5",
        "consensus": (
            "outputs/grid-2026-08-18/g384_ov192/consensus-n5/consensus_t1.geojson"
        ),
        "crops": (
            "outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder/"
            "k5_recovery-fixed/crops"
        ),
        "verify": (
            "outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder/k5_recovery-fixed"
        ),
        "board_sweep_name": "sweep_board.json",
        "era2_sweep_name": "sweep_era2.json",
        "point": "opmax",
        "carried_prob": 0.15,
        "n_passes": 5,
        "committed_point": (5, 0.15),
        "committed_f1_20": 0.8905,
        "committed_n_detections": 435,
        "carrier_rekey": True,
        "committed_cell": (
            "results/k-ladder-2026-09-12/tier-e/cells/"
            "grid-2026-08-18__g384-ov192-k5-verified-opmax"
        ),
    },
]


def run(command: list[str], repo: Path, label: str) -> None:
    """Run one subprocess step from the repository root, failing loudly.

    Args:
        command: Argument vector.
        repo: Working directory.
        label: Human-readable step name for the log.

    Raises:
        SystemExit: If the step exits non-zero.
    """
    logger.info("%s: %s", label, " ".join(command[-8:]))
    done = subprocess.run(command, cwd=repo, capture_output=True, text=True)
    if done.returncode != 0:
        logger.error("%s FAILED\n%s\n%s", label, done.stdout[-3000:], done.stderr[-3000:])
        raise SystemExit(f"{label} failed")


def main() -> None:
    """Re-score every selected cell and write the operating-point report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, required=True)
    parser.add_argument("--python", type=str, default=sys.executable)
    parser.add_argument(
        "--only", action="append", default=None, help="Restrict to these cell keys"
    )
    parser.add_argument(
        "--no-evaluate",
        action="store_true",
        help=(
            "Stop after materialising. Needed for the three Gemini 3.7 cells, "
            "whose per-tile table the tile-join invariant refuses, so "
            "evaluate_detections.py cannot run at HEAD — score those with "
            "f1_only.py instead."
        ),
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    repo = args.repo.resolve()
    bits = load_driver_bits(repo)
    args.out_root.mkdir(parents=True, exist_ok=True)

    selected = [
        cell for cell in CELLS if args.only is None or cell["key"] in args.only
    ]
    report: list[dict[str, Any]] = []

    for cell in selected:
        verify = repo / cell["verify"]
        crops = repo / cell["crops"]

        # --- Step 1: the two sweeps -------------------------------------
        sweeps: dict[str, Path] = {}
        for frame_key, bounds, name in (
            ("board", bits["BOARD_BOUNDS"], cell["board_sweep_name"]),
            ("era2", bits["ERA2_BOUNDS"], cell["era2_sweep_name"]),
        ):
            out = verify / name
            run(
                [
                    args.python,
                    "scripts/sweep_f1_greedy_pv.py",
                    "--config",
                    cell["sweep_config"],
                    "--crops-dir",
                    str(crops),
                    "--verified-dir",
                    str(verify),
                    "--output",
                    str(out),
                    "--bounds",
                    str(bounds),
                    "--buffer-m",
                    *[str(b) for b in bits["SWEEP_BUFFERS"]],
                ],
                repo,
                f"{cell['key']} sweep {frame_key}",
            )
            sweeps[frame_key] = out

        # ``argmax_at_headline`` takes the sweep FILE, not its rows — reuse it
        # as-is so the tie-break is literally the committed driver's.
        board_best = bits["argmax_at_headline"](sweeps["board"])
        era2_best = bits["argmax_at_headline"](sweeps["era2"])

        # --- Step 2: the operating point ---------------------------------
        if cell["point"] == "opmax":
            vote_t = int(board_best["vote_t"])
            prob_t = float(board_best["prob_t"])
        else:
            vote_t = int(cell["n_passes"])
            prob_t = float(cell["carried_prob"])

        # --- Step 3: materialise ----------------------------------------
        materialised = args.out_root / f"{cell['key']}.geojson"
        run(
            [
                args.python,
                "scripts/materialise_pv_geojson.py",
                "--consensus",
                cell["consensus"],
                "--probabilities",
                str(verify / "probabilities.json"),
                "--vote-t",
                str(vote_t),
                "--prob-t",
                f"{prob_t}",
                "--output",
                str(materialised),
            ],
            repo,
            f"{cell['key']} materialise",
        )

        # --- Step 4: tier-E carrier re-key ------------------------------
        if cell["carrier_rekey"]:
            n_features = bits["reassign_carrier_tiles"](materialised)
            logger.info("%s re-keyed %d features", cell["key"], n_features)

        # --- Step 5: evaluate on the recorded recipe ---------------------
        cell_out = args.out_root / bits["cell_dir_name"](
            cell["run_id"], cell["label"]
        )
        if args.no_evaluate:
            report.append(
                {
                    "key": cell["key"],
                    "run_id": cell["run_id"],
                    "label": cell["label"],
                    "committed_point": list(cell["committed_point"]),
                    "new_point": [vote_t, prob_t],
                    "point_moved": [vote_t, prob_t] != list(cell["committed_point"]),
                    "board_argmax": {
                        "vote_t": board_best["vote_t"],
                        "prob_t": board_best["prob_t"],
                        "f1": board_best["f1"],
                        "n": board_best["n"],
                        "n_ties": board_best.get("n_ties"),
                    },
                    "era2_argmax": {
                        "vote_t": era2_best["vote_t"],
                        "prob_t": era2_best["prob_t"],
                        "f1": era2_best["f1"],
                    },
                    "frames_agree": (
                        board_best["vote_t"] == era2_best["vote_t"]
                        and board_best["prob_t"] == era2_best["prob_t"]
                    ),
                    "committed_f1_20": cell["committed_f1_20"],
                    "committed_n_detections": cell["committed_n_detections"],
                    "materialised": str(materialised),
                    "evaluated": False,
                    "evaluation_note": (
                        "per-tile table refused by the tile-join invariant; "
                        "scored on the F1 arm only by f1_only.py"
                    ),
                }
            )
            logger.info("%s MATERIALISED ONLY", cell["key"])
            continue
        run(
            [
                args.python,
                "scripts/evaluate_detections.py",
                "--detections",
                str(materialised),
                "--ground-truth",
                str(bits["GROUND_TRUTH"]),
                "--bounds",
                str(bits["BOARD_BOUNDS"]),
                "--buffers",
                *[str(b) for b in bits["BUFFERS"]],
                "--bootstrap",
                str(bits["BOOTSTRAP"]),
                "--seed",
                str(bits["SEED"]),
                "--mcc",
                "--output-dir",
                str(cell_out),
                "--label",
                cell["label"],
            ],
            repo,
            f"{cell['key']} evaluate",
        )

        evaluation = json.loads((cell_out / "evaluation.json").read_text())
        summary = evaluation["summary"]
        headline = int(bits["HEADLINE_BUFFER"])
        row = next(
            (
                candidate
                for candidate in summary["buffers"]
                if candidate.get("buffer_metres") == headline
            ),
            {},
        )
        tile = summary.get("tile_classification") or {}
        mcc_block = tile.get("mcc")
        tile_mcc = (
            mcc_block.get("point") if isinstance(mcc_block, dict) else mcc_block
        )

        report.append(
            {
                "key": cell["key"],
                "run_id": cell["run_id"],
                "label": cell["label"],
                "committed_point": list(cell["committed_point"]),
                "new_point": [vote_t, prob_t],
                "point_moved": [vote_t, prob_t] != list(cell["committed_point"]),
                "board_argmax": {
                    "vote_t": board_best["vote_t"],
                    "prob_t": board_best["prob_t"],
                    "f1": board_best["f1"],
                    "n": board_best["n"],
                },
                "era2_argmax": {
                    "vote_t": era2_best["vote_t"],
                    "prob_t": era2_best["prob_t"],
                    "f1": era2_best["f1"],
                },
                "frames_agree": (
                    board_best["vote_t"] == era2_best["vote_t"]
                    and board_best["prob_t"] == era2_best["prob_t"]
                ),
                "committed_f1_20": cell["committed_f1_20"],
                "new_f1_20": row.get("f1"),
                "new_f1_ci_20": [row.get("f1_ci_lower"), row.get("f1_ci_upper")],
                "new_precision_20": row.get("precision"),
                "new_recall_20": row.get("recall"),
                "committed_n_detections": cell["committed_n_detections"],
                "new_n_detections": summary.get("n_detections"),
                "new_tile_mcc": tile_mcc,
                "new_tile_confusion": tile.get("confusion"),
                "tile_mcc_withheld": tile.get("withheld"),
                "tile_mcc_withheld_reason": tile.get("withheld_reason"),
                "cell_dir": str(cell_out),
                "materialised": str(materialised),
            }
        )
        logger.info("%s DONE: %s", cell["key"], json.dumps(report[-1], indent=2))

    (args.out_root / "operating-points.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
