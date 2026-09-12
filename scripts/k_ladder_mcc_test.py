#!/usr/bin/env python3
# ============================================================================
# k_ladder_mcc_test.py
# ----------------------------------------------------------------------------
# Does the tile-MCC direction of `results/k-ladder-2026-09-12/findings.md` § 4
# survive testing?
#
# WHY THIS SCRIPT EXISTS
# ----------------------
# § 4 of the K-ladder findings reports that F1 rises with pass count K on all
# eight fixed-parameter ladders while tile-level Matthews Correlation
# Coefficient (MCC) FALLS on five, is flat on two, and rises only on the
# gold-standard ladder — and says plainly that none of those differences had
# been permutation-tested (§ 6.1). The Principal Investigator (PI) ruled the
# direction must be TESTED rather than described. This driver runs that test.
#
# WHAT IT DOES NOT REIMPLEMENT, AND WHY
# -------------------------------------
# Nothing statistical. The test is the project's canonical round-robin
# tile-swap permutation, run through `scripts/era1_leaderboard_tiering.py`
# (the instrument `findings.md` § 6.1 names for the gold-standard ladder, and
# the same chain whose `permutation_test_float` + Benjamini-Hochberg (BH) +
# greedy-clique machinery produced the committed 55-map board). That harness
# was extended on 2026-09-12 with `--permute-mcc`, which carries MCC through
# the IDENTICAL per-tile swap masks as F1 (one `default_rng(seed)` stream, one
# tile order), so a ladder's ΔF1 and ΔMCC are two statistics of one
# permutation. This driver only:
#
#   1. reads the ladder inventory (`ladders.json`) and selects each ladder's
#      rungs on the ORACLE basis — the basis § 4's table is built on;
#   2. writes a minimal per-ladder analysis row so the tiering harness can
#      read its cell set from `conditions_compared` as it always does, without
#      minting a placeholder row into the register;
#   3. runs the harness per ladder, at that ladder's own headline buffer;
#   4. GATES the run by reproducing the committed F1 permutation p-values,
#      where the ladder has them (see below);
#   5. collates the pairs the ruling asks for — (K = 1 vs best rung) and every
#      adjacent-rung pair — into one JSON per ladder.
#
# THE GATE
# --------
# The seven 55-map ladders' rungs are all cells of a committed final board
# (`results/55map-final-board-r2-2026-09-06/final_board_50m.json` for the r2
# ladders, `results/55map-final-board-2026-08-27/...` for the standardised
# siblings), whose `pairwise` table records the SAME tile-swap micro-F1
# permutation (10,000, seed 42) for every pair of cells. Each tested pair's
# reproduced `f1_a`, `f1_b`, `observed_diff` and raw `p_value` must match that
# committed entry to the recorded precision before any MCC number from the
# same run is trusted. `bh_adjusted_p` is deliberately NOT gated: the board
# adjusts over its own 595-pair family, this run adjusts within each ladder.
#
# The gold-standard ladder has no committed pairwise p-values at all (that is
# exactly the § 6.1 gap), so its gate is the harness's own: each cell's
# rebuilt micro-F1 against its committed evaluation F1, and each cell's
# rebuilt tile confusion and MCC against its committed
# `tile_classification` block (a hard ConfusionGateError otherwise).
#
# THE INSTRUMENT QUESTION IS LEFT OPEN, DELIBERATELY
# --------------------------------------------------
# `findings.md` § 6.1 records that the PI has not yet ruled which instrument
# the seven 55-map ladders should be tested under. This driver runs the board
# instrument, which is the one that actually tiered these cells and the only
# one with committed F1 p-values for every pair asked about. The per-map
# paired sign-swap of `scripts/stride55_ladder.py` is run separately by that
# script's own `--pairs-output-dir` mode, for the two Gemini-3 stride ladders
# where it is registered. Neither result is presented as the answer to the
# other's question.
#
# Usage (sapphire):
#   .venv/bin/python scripts/k_ladder_mcc_test.py \
#       --output-dir results/k-ladder-2026-09-12/mcc-test
#
# Zero application programming interface (API) calls. All computation is local.
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-09-12 | Apache 2.0
# ============================================================================
"""Test the tile-MCC direction of each K ladder with the board instrument."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LADDERS_JSON = BASE_DIR / "results/k-ladder-2026-09-12/ladders.json"
RUN_CONDITIONS = BASE_DIR / "results/run-conditions.json"
GS_TIERING_INPUT = BASE_DIR / "results/k-ladder-2026-09-12/tiering-input/gs-stride-a"
GS_ANALYSIS_ID = "k-ladder-gs-stride-a-2026-09-12"
GS_BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"

#: Committed boards whose `pairwise` table gates a ladder's F1 p-values, keyed
#: by the board results directory that a rung's eval_path sits under.
BOARDS = {
    "results/55map-final-board-r2-2026-09-06":
        "results/55map-final-board-r2-2026-09-06/final_board_50m.json",
    "results/55map-final-board-2026-08-27":
        "results/55map-final-board-2026-08-27/final_board_50m.json",
}

#: Gate tolerances. The committed pairwise table rounds F1 and the observed
#: difference to 6 dp and the p-value to 4 dp, so the gate is set at half a
#: unit in each last place: an exact reproduction, to the recorded precision.
F1_GATE_TOL = 5e-7
P_GATE_TOL = 5e-5


def repo_relative(path: Path) -> str:
    """Render a path relative to the repo root when it sits inside it.

    Output paths are usually inside the repository, but a smoke test may point
    them at a scratch directory; a provenance field should degrade to the
    absolute path rather than raising.

    Args:
        path: Any path.

    Returns:
        The repo-relative string, or the absolute string when outside.
    """
    try:
        return str(path.relative_to(BASE_DIR))
    except ValueError:
        return str(path)


def slug_for(ladder: dict) -> str:
    """Build a stable directory-safe identifier for one ladder.

    The inventory keys ladders by family plus reference file, which is not a
    filename. This composes the board-cell prefix (A / B / FOURTH / ARM1 /
    ARM2, or `gs` for the gold standard) with the reference vintage, so the
    eight ladders get eight stable, self-describing slugs.

    Args:
        ladder: One entry of `ladders.json`'s `ladders` list.

    Returns:
        A lowercase hyphenated slug, e.g. ``55map-stride-a-r2``.
    """
    if ladder["corpus"] == "4-map-gs":
        return "gs-stride-a"
    first = ladder["rungs"][0]["eval_path"]
    cell_prefix = Path(first).parent.name.split("-")[0].lower()
    vintage = ("r2" if Path(ladder["reference_file"]).stem.endswith("-r2")
               else "standardised")
    names = {"a": "55map-stride-a", "b": "55map-stride-b",
             "fourth": "55map-stride-b-g37vf", "arm1": "37arm1", "arm2": "37arm2"}
    return f"{names[cell_prefix]}-{vintage}"


def select_rungs(ladder: dict) -> list[dict]:
    """One rung per K, on the oracle basis — the basis § 4's table uses.

    Several 55-map ladders commit two cells per rung: the *carried* operating
    point (the threshold transferred from the gold standard) and the rung
    *oracle* (that rung's own sweep argmax). `findings.md` § 4 tabulates the
    oracle column, so this selects the oracle wherever both exist and the sole
    cell otherwise.

    Args:
        ladder: One entry of `ladders.json`'s `ladders` list.

    Returns:
        The selected rungs, ordered by ascending K.

    Raises:
        ValueError: if a K has neither a unique cell nor an oracle cell.
    """
    by_k: dict[int, list[dict]] = {}
    for rung in ladder["rungs"]:
        by_k.setdefault(int(rung["K"]), []).append(rung)
    out = []
    for k in sorted(by_k):
        candidates = by_k[k]
        if len(candidates) == 1:
            out.append(candidates[0])
            continue
        oracles = [c for c in candidates
                   if Path(c["eval_path"]).parent.name.endswith("-oracle")]
        if len(oracles) != 1:
            raise ValueError(
                f"K={k}: cannot pick one rung from "
                f"{[c['condition_id'] for c in candidates]}"
            )
        out.append(oracles[0])
    return out


def requested_pairs(rungs: list[dict]) -> list[dict]:
    """The pairs the ruling asks for: K = 1 vs best rung, and adjacent rungs.

    Args:
        rungs: One rung per K, ascending, each with `K` and `f1_headline`.

    Returns:
        A list of ``{kind, k_a, k_b}`` dicts, ordered K = 1-vs-best first then
        the adjacent pairs. A pair that is both is emitted once, as ``both``.
    """
    best = max(rungs, key=lambda r: r["f1_headline"])
    adjacent = [(rungs[i]["K"], rungs[i + 1]["K"]) for i in range(len(rungs) - 1)]
    headline = (rungs[0]["K"], best["K"])
    pairs = []
    if headline[0] != headline[1]:
        kind = "k1-vs-best+adjacent" if headline in adjacent else "k1-vs-best"
        pairs.append({"kind": kind, "k_a": headline[0], "k_b": headline[1]})
    for k_a, k_b in adjacent:
        if (k_a, k_b) == headline:
            continue
        pairs.append({"kind": "adjacent", "k_a": k_a, "k_b": k_b})
    return pairs


def write_analysis_row(out_dir: Path, slug: str, ladder: dict,
                       rungs: list[dict]) -> tuple[Path, str]:
    """Write the minimal analyses file the tiering harness reads its cells from.

    `era1_leaderboard_tiering.py` takes board membership from a named analysis
    row's `conditions_compared`, which is the right single source of truth —
    but these ladders have no registered analysis row yet (`findings.md` § 6.2
    explains why one cannot be authored until this test lands). A one-row file
    breaks the circularity without touching `results/run-analyses.json`.

    Args:
        out_dir: The run's output directory.
        slug: This ladder's slug.
        ladder: The ladder inventory entry.
        rungs: The selected rungs.

    Returns:
        ``(path, analysis_id)`` of the written file.
    """
    analysis_id = f"k-ladder-mcc-{slug}-2026-09-12"
    path = out_dir / "tiering-input" / slug / "run-analyses.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "_README": (
            "TIERING INPUT — NOT REGISTERED. One analysis row naming this K "
            "ladder's oracle-basis rungs, so scripts/era1_leaderboard_tiering."
            "py can tier them with the board instrument verbatim. Written by "
            "scripts/k_ladder_mcc_test.py; results/run-analyses.json is not "
            "modified and this file must never be written back over it."
        ),
        "schema_version": "1.0",
        "analyses": [{
            "analysis_id": analysis_id,
            "type": "comparison",
            "_note": (
                f"K ladder {ladder['family_base']} "
                f"[{Path(ladder['reference_file']).name}], oracle basis, "
                f"headline buffer {ladder['headline_buffer_m']} m."
            ),
            "conditions_compared": [r["condition_id"] for r in rungs],
            "hypothesis_refs": ["H3"],
            "outcome": "PENDING: this is a tiering input, not a registered result",
            "paper_section": "Results",
            "output_path": None,
            "working_notes_obs": [],
            "preregistered": "post-hoc",
            "deviations": [],
        }],
    }, indent=2) + "\n")
    return path, analysis_id


def run_tiering(analyses: Path, conditions: Path, analysis_id: str,
                out_dir: Path, buffer_m: int, bounds: Path | None,
                n_perms: int, seed: int) -> dict:
    """Invoke the extended tiering harness and return its result JSON.

    Args:
        analyses: Analyses file naming the board.
        conditions: Conditions sidecar to resolve refs through.
        analysis_id: The analysis row to tier.
        out_dir: Where the harness writes `tiering_<buffer>m.{json,md}`.
        buffer_m: Headline buffer for the F1 statistic.
        bounds: Optional bounds override (the gold-standard board frame).
        n_perms: Permutation count.
        seed: Random seed.

    Returns:
        The parsed `tiering_<buffer>m.json`.

    Raises:
        subprocess.CalledProcessError: if the harness fails a gate.
    """
    cmd = [sys.executable, str(BASE_DIR / "scripts/era1_leaderboard_tiering.py"),
           "--analysis-id", analysis_id,
           "--conditions", str(conditions),
           "--analyses", str(analyses),
           "--output-dir", str(out_dir),
           "--buffer", str(buffer_m),
           "--n-permutations", str(n_perms),
           "--seed", str(seed),
           "--permute-mcc"]
    if bounds is not None:
        cmd += ["--bounds", str(bounds)]
    print("  $ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=BASE_DIR)
    return json.loads((out_dir / f"tiering_{buffer_m}m.json").read_text())


def board_for(rung: dict) -> tuple[str, str] | None:
    """The committed board that gates a rung's F1 p-values, and its cell label.

    Args:
        rung: A rung with an `eval_path`.

    Returns:
        ``(board_json_path, cell_label)``, or None when the rung sits under no
        gating board (the gold-standard ladder).
    """
    eval_path = rung["eval_path"]
    for prefix, board in BOARDS.items():
        if eval_path.startswith(prefix):
            return board, Path(eval_path).parent.name
    return None


def gate_against_board(rung_a: dict, rung_b: dict, f1_entry: dict,
                       board_cache: dict) -> dict:
    """Compare one reproduced F1 permutation against its committed board entry.

    Args:
        rung_a: The rung the harness treated as condition A.
        rung_b: The rung the harness treated as condition B.
        f1_entry: The harness's `pairwise` entry for that pair.
        board_cache: Board-path -> parsed board JSON, filled in place.

    Returns:
        A gate record: the committed values, the reproduced values, the
        absolute deltas, and a `passed` flag. `available` is False when the
        ladder has no committed pairwise table.
    """
    ba, bb = board_for(rung_a), board_for(rung_b)
    if ba is None or bb is None or ba[0] != bb[0]:
        return {"available": False,
                "why": "no committed pairwise table covers both rungs"}
    board_path, label_a = ba
    _, label_b = bb
    if board_path not in board_cache:
        board_cache[board_path] = json.loads((BASE_DIR / board_path).read_text())
    board = board_cache[board_path]
    entry = next((e for e in board["pairwise"]
                  if {e["a"], e["b"]} == {label_a, label_b}), None)
    if entry is None:
        return {"available": False,
                "why": f"{label_a} vs {label_b} absent from {board_path}"}
    flip = entry["a"] != label_a
    committed = {
        "f1_a": entry["f1_b"] if flip else entry["f1_a"],
        "f1_b": entry["f1_a"] if flip else entry["f1_b"],
        "observed_diff": -entry["observed_diff"] if flip else entry["observed_diff"],
        "p_value": entry["p_value"],
        "n_tiles": entry["n_tiles"],
    }
    reproduced = {k: f1_entry[k] for k in
                  ("f1_a", "f1_b", "observed_diff", "p_value", "n_tiles")}
    deltas = {k: abs(reproduced[k] - committed[k])
              for k in ("f1_a", "f1_b", "observed_diff", "p_value")}
    passed = (deltas["f1_a"] <= F1_GATE_TOL and deltas["f1_b"] <= F1_GATE_TOL
              and deltas["observed_diff"] <= F1_GATE_TOL
              and deltas["p_value"] <= P_GATE_TOL
              and reproduced["n_tiles"] == committed["n_tiles"])
    return {"available": True, "board": board_path,
            "cell_a": label_a, "cell_b": label_b,
            "committed": committed, "reproduced": reproduced,
            "abs_delta": {k: round(v, 9) for k, v in deltas.items()},
            "tolerance": {"f1": F1_GATE_TOL, "p_value": P_GATE_TOL},
            "passed": bool(passed)}


def verdict_for(d_f1: float, p_f1: float, d_mcc: float, p_mcc: float,
                q: float) -> str:
    """One-line verdict for a pair: what survives BH at q.

    Args:
        d_f1: ΔF1 (higher K minus lower K).
        p_f1: BH-adjusted p for ΔF1.
        d_mcc: ΔMCC (higher K minus lower K).
        p_mcc: BH-adjusted p for ΔMCC.
        q: The BH level.

    Returns:
        A short verdict string.
    """
    f1_sig = p_f1 < q
    mcc_sig = p_mcc < q
    f1_word = "F1 up" if d_f1 > 0 else "F1 down" if d_f1 < 0 else "F1 flat"
    mcc_word = "MCC up" if d_mcc > 0 else "MCC down" if d_mcc < 0 else "MCC flat"
    if f1_sig and mcc_sig:
        return f"{f1_word} (sig), {mcc_word} (sig)"
    if f1_sig and not mcc_sig:
        return f"{f1_word} (sig), {mcc_word} n.s."
    if mcc_sig and not f1_sig:
        return f"{f1_word} n.s., {mcc_word} (sig)"
    return "neither separates"


def main() -> int:
    """CLI entry point: test every ladder, gate it, and write the collation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=BASE_DIR / "results/k-ladder-2026-09-12/mcc-test")
    parser.add_argument("--n-permutations", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--only", type=str, default=None,
                        help="Run a single ladder slug (for a smoke test).")
    args = parser.parse_args()

    inventory = json.loads(LADDERS_JSON.read_text())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    board_cache: dict = {}
    summary: list[dict] = []

    for ladder in inventory["ladders"]:
        slug = slug_for(ladder)
        if args.only and slug != args.only:
            continue
        rungs = select_rungs(ladder)
        by_k = {int(r["K"]): r for r in rungs}
        print(f"\n=== {slug}: K = {sorted(by_k)} "
              f"@ {ladder['headline_buffer_m']} m ===", flush=True)

        if slug == "gs-stride-a":
            analyses = GS_TIERING_INPUT / "run-analyses.json"
            conditions = GS_TIERING_INPUT / "run-conditions.json"
            analysis_id = GS_ANALYSIS_ID
            bounds: Path | None = GS_BOUNDS
        else:
            analyses, analysis_id = write_analysis_row(
                args.output_dir, slug, ladder, rungs)
            conditions = RUN_CONDITIONS
            bounds = None

        tiering_dir = args.output_dir / "tiering" / slug
        tiering = run_tiering(analyses, conditions, analysis_id, tiering_dir,
                              int(ladder["headline_buffer_m"]), bounds,
                              args.n_permutations, args.seed)

        ref_to_k = {r["condition_id"]: int(r["K"]) for r in rungs}
        f1_by_pair = {frozenset((ref_to_k[e["ref_a"]], ref_to_k[e["ref_b"]])):
                      (e, ref_to_k[e["ref_a"]]) for e in tiering["pairwise"]}
        mcc_by_pair = {frozenset((ref_to_k[e["ref_a"]], ref_to_k[e["ref_b"]])):
                       (e, ref_to_k[e["ref_a"]])
                       for e in tiering["mcc_permutation"]["pairwise"]}

        rows = []
        gates = []
        for pair in requested_pairs(rungs):
            k_lo, k_hi = pair["k_a"], pair["k_b"]
            key = frozenset((k_lo, k_hi))
            f1_entry, f1_a_k = f1_by_pair[key]
            mcc_entry, mcc_a_k = mcc_by_pair[key]
            # Orient every reported delta as (higher K) - (lower K), whatever
            # order the round-robin happened to put the pair in.
            f1_sign = 1.0 if f1_a_k == k_hi else -1.0
            mcc_sign = 1.0 if mcc_a_k == k_hi else -1.0
            d_f1 = round(f1_sign * f1_entry["observed_diff"], 6)
            d_mcc = round(mcc_sign * mcc_entry["observed_mcc_diff"], 6)
            gate = gate_against_board(by_k[f1_a_k],
                                      by_k[k_lo if f1_a_k == k_hi else k_hi],
                                      f1_entry, board_cache)
            gates.append({"pair": f"K{k_lo}-vs-K{k_hi}", **gate})
            rows.append({
                "pair": f"K{k_lo}-vs-K{k_hi}",
                "kind": pair["kind"],
                "k_low": k_lo, "k_high": k_hi,
                "condition_low": by_k[k_lo]["condition_id"],
                "condition_high": by_k[k_hi]["condition_id"],
                "delta_convention": "higher K minus lower K",
                "f1": {
                    "low": by_k[k_lo]["f1_headline"],
                    "high": by_k[k_hi]["f1_headline"],
                    "delta": d_f1,
                    "p_raw": f1_entry["p_value"],
                    "p_bh": f1_entry["bh_adjusted_p"],
                    "significant": f1_entry["significant"],
                },
                "mcc": {
                    "low": by_k[k_lo]["tile_mcc"],
                    "high": by_k[k_hi]["tile_mcc"],
                    "delta": d_mcc,
                    "p_raw": mcc_entry["p_value"],
                    "p_bh": mcc_entry["bh_adjusted_p"],
                    "significant": mcc_entry["significant"],
                },
                "verdict": verdict_for(d_f1, f1_entry["bh_adjusted_p"],
                                       d_mcc, mcc_entry["bh_adjusted_p"],
                                       tiering["fdr_q"]),
            })
            print(f"  {rows[-1]['pair']:<14} dF1 {d_f1:+.4f} "
                  f"(p_bh {f1_entry['bh_adjusted_p']:.4f}) | dMCC {d_mcc:+.4f} "
                  f"(p_bh {mcc_entry['bh_adjusted_p']:.4f}) | "
                  f"{rows[-1]['verdict']}", flush=True)

        gate_pass = all(g["passed"] for g in gates if g.get("available"))
        n_gated = sum(1 for g in gates if g.get("available"))
        payload = {
            "ladder": slug,
            "family": ladder["family_base"],
            "run_id": ladder["run_id"],
            "proposer_pool": ladder["proposer_pool"],
            "corpus": ladder["corpus"],
            "reference_file": ladder["reference_file"],
            "frame_file": ladder["frame_file"],
            "headline_buffer_m": ladder["headline_buffer_m"],
            "basis": "oracle",
            "instrument": {
                "name": "round-robin tile-swap permutation (the board chain)",
                "script": "scripts/era1_leaderboard_tiering.py --permute-mcc",
                "f1_statistic": (
                    f"micro-average F1 @ {ladder['headline_buffer_m']} m over "
                    f"{tiering['n_tiles']} tiles, per-tile TP/FP/FN swapped"
                ),
                "mcc_statistic": (
                    "tile-level MCC, buffer-invariant; per-tile one-hot "
                    "(TP, TN, FP, FN) swapped under the SAME mask as F1"
                ),
                "kernels": [
                    "n1_baseline_leaderboard_tiering.permutation_test_float",
                    "pairwise_permutation_test.permutation_test_mcc_arrays",
                ],
                "n_permutations": tiering["n_permutations"],
                "seed": tiering["seed"],
                "n_tiles": tiering["n_tiles"],
                "bh_q": tiering["fdr_q"],
                "bh_family": (
                    f"within this ladder: the full round-robin of "
                    f"{len(tiering['pairwise'])} pair(s), F1 and MCC adjusted "
                    f"as separate families"
                ),
                "instrument_ruling": (
                    "This is the instrument that tiered these cells and the "
                    "only one with committed F1 p-values for every pair asked "
                    "about. findings.md § 6.1 records that the PI's ruling on "
                    "the 55-map ladders' instrument is pending; the per-map "
                    "paired sign-swap of scripts/stride55_ladder.py is "
                    "reported separately where it is registered."
                ),
            },
            "gate": {
                "kind": ("committed board pairwise F1 permutation"
                         if n_gated else
                         "harness-internal only (no committed pairwise table "
                         "exists for this ladder — findings.md § 6.1)"),
                "n_pairs_gated": n_gated,
                "passed": bool(gate_pass),
                "pairs": gates,
                "cell_gates": tiering["mcc_permutation"]["gates"],
            },
            "pairs": rows,
            "tiering_artefact": repo_relative(
                tiering_dir / f"tiering_{ladder['headline_buffer_m']}m.json"),
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        (args.output_dir / f"{slug}.json").write_text(
            json.dumps(payload, indent=2) + "\n")
        print(f"  gate: {n_gated} pair(s) against a committed board -> "
              f"{'PASS' if gate_pass else 'FAIL'}", flush=True)
        summary.append({
            "ladder": slug, "family": ladder["family_base"],
            "buffer_m": ladder["headline_buffer_m"],
            "gate_passed": bool(gate_pass), "n_pairs_gated": n_gated,
            "n_pairs": len(rows),
            "mcc_direction_k1_to_best": next(
                (r["mcc"]["delta"] for r in rows if "k1-vs-best" in r["kind"]),
                None),
            "mcc_p_bh_k1_to_best": next(
                (r["mcc"]["p_bh"] for r in rows if "k1-vs-best" in r["kind"]),
                None),
            "f1_delta_k1_to_best": next(
                (r["f1"]["delta"] for r in rows if "k1-vs-best" in r["kind"]),
                None),
            "f1_p_bh_k1_to_best": next(
                (r["f1"]["p_bh"] for r in rows if "k1-vs-best" in r["kind"]),
                None),
            "any_mcc_pair_significant": any(
                r["mcc"]["significant"] for r in rows),
        })

    (args.output_dir / "summary.json").write_text(json.dumps({
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_inventory": repo_relative(LADDERS_JSON),
        "n_permutations": args.n_permutations,
        "seed": args.seed,
        "n_ladders": len(summary),
        "gate_all_passed": all(s["gate_passed"] for s in summary),
        "ladders": summary,
    }, indent=2) + "\n")
    print(f"\nWrote {repo_relative(args.output_dir)}/summary.json",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
