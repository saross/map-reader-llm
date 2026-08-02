#!/usr/bin/env python3
# ============================================================================
# author_e43_matched_temperature.py
# ----------------------------------------------------------------------------
# E72 remediation, item 3 (protocol-errata.md § E72): file the four MATCHED
# temperature consensus cells of the E43 remediation "as their own first-class
# analysis (14-buffer + MCC, manifest-registered)".
#
# WHAT THIS SCRIPT DOES *NOT* DO, AND WHY
# ---------------------------------------
# It does NOT mint four new conditions. The four operating points are ALREADY
# first-class ``pv-diag-384`` conditions, scored at the identical house grain
# (the 14 uniform buffers 5-150 m + tile-level Matthews Correlation Coefficient
# (MCC), BCa bootstrap 10,000 iterations, seed 42, 487-tile Era-2 bounds) on
# 2026-06-05 under ``results/rescore-2026-06-05/pv-diag-384/consensus-sweep/``:
#
#   pv-diag-384::flash-minimal-text-n30-t07-text-t0.7-consensus-n5-5of5
#   pv-diag-384::flash-minimal-text-n30-t07-text-t1.0-consensus-n5-5of5
#   pv-diag-384::flash-minimal-text-n30-t07-text-t0.7-consensus-n10-10of10
#   pv-diag-384::flash-minimal-text-n30-t07-text-t1.0-consensus-9of10
#
# Minting parallel ``matched-temp-*`` labels for the same GeoJSONs and the same
# metrics would double-count them in every downstream board built from
# ``results/conditions-manifest.json`` (leaderboards, tier tables, condition
# counts). The house precedent is explicit — ``author_sweep_promotions.py``
# refused to promote sweep cell #1 for exactly this reason ("promotion would
# duplicate it"). So the filing lands as the missing ARTEFACT: one registered
# ANALYSIS over the four existing condition ids.
#
# The independent 14-buffer + MCC re-score under
# ``results/e43-matched-temperature/paper-eval/`` (worklist
# ``planning/rescore-worklists/e43-matched-temperature-2026-08-02.json``, run
# through ``scripts/rescore_conditions.py``) gives the E43 findings document its
# own self-contained house-grain artefacts and independently reproduces the
# 2026-06-05 numbers under the current scripts. Because those four
# ``evaluation.json`` files re-score detections that a registered condition
# already claims, they are waived into ``pv-diag-384``'s ``_ignored_evals`` —
# the designed home for deliberate exclusions — so the completeness verifier
# (``scripts/verify_run_conditions.py``) stays a sharp guard.
#
# VALIDATION GATES (the script refuses to write on any failure):
#   1. each reproduction eval exists and carries the 14 canonical buffers;
#   2. each carries a tile_classification block with an MCC point estimate;
#   3. F1@20 m reproduces the operating-point value recorded in
#      results/e43-matched-temperature/findings.md § 3 to 4 decimal places;
#   4. n_detections equals the consensus GeoJSON's feature count;
#   5. the already-registered sibling condition exists, points at the same
#      detections file, and its eval agrees with the reproduction on F1@20 m
#      and MCC to 1e-9 (this equality is what licenses gate 6);
#   6. no duplicate condition is created — asserted, not assumed.
#
# DRY-RUN BY DEFAULT — pass --execute to write. After executing:
#   .venv/bin/python scripts/generate_post_run_report.py --all --write
#   .venv/bin/python scripts/verify_run_conditions.py --run pv-diag-384
#
# Usage:
#   .venv/bin/python scripts/author_e43_matched_temperature.py
#   .venv/bin/python scripts/author_e43_matched_temperature.py --execute
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-08-02 | Apache 2.0
# ============================================================================
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONDS = REPO / "results" / "run-conditions.json"
ANALYSES = REPO / "results" / "run-analyses.json"

RUN_ID = "pv-diag-384"
ANALYSIS_ID = "e43-matched-temperature"
PAPER_EVAL = "results/e43-matched-temperature/paper-eval"
STUDY = "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07"

#: The 14 uniform buffers (metres) — the project standard since 2026-05-31
#: (``scripts/rescore_conditions.BUFFERS_STANDARD``); repeated here so the gate
#: fails loudly if a reproduction was scored at some other grain.
BUFFERS_STANDARD: tuple[int, ...] = (
    5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150,
)

#: One tuple per matched operating point:
#: ``(cell_dir, arm, n_passes, threshold_label, expected_f1_at_20m,
#:   detections_rel, registered_condition_label)``.
#: ``expected_f1_at_20m`` is the § 3 operating-point table of
#: ``results/e43-matched-temperature/findings.md`` (commit ``6176b985e``) — the
#: sanity anchor the whole filing is gated on.
CELLS: tuple[tuple[str, str, int, str, float, str, str], ...] = (
    (
        "t07-n5-5of5", "T=0.7", 5, "5-of-5", 0.6397,
        f"{STUDY}/text-t0.7/consensus-n5/consensus_t5.geojson",
        "flash-minimal-text-n30-t07-text-t0.7-consensus-n5-5of5",
    ),
    (
        "t10-n5-5of5", "T=1.0", 5, "5-of-5", 0.6610,
        f"{STUDY}/text-t1.0/consensus-n5/consensus_t5.geojson",
        "flash-minimal-text-n30-t07-text-t1.0-consensus-n5-5of5",
    ),
    (
        "t07-n10-10of10", "T=0.7", 10, "10-of-10", 0.6332,
        f"{STUDY}/text-t0.7/consensus-n10/consensus_t10.geojson",
        "flash-minimal-text-n30-t07-text-t0.7-consensus-n10-10of10",
    ),
    (
        "t10-n10-9of10", "T=1.0", 10, "9-of-10", 0.6667,
        f"{STUDY}/text-t1.0/consensus/consensus_t9.geojson",
        "flash-minimal-text-n30-t07-text-t1.0-consensus-9of10",
    ),
)

CROSSREF_NOTE = (
    " | E72 remediation (2026-08-02): the four MATCHED-temperature consensus "
    "cells (text-t0.7 / text-t1.0 x N=5/N=10, both arms 487/487 tiles) are "
    "filed as the 'e43-matched-temperature' analysis over the EXISTING "
    "conditions listed above — no parallel 'matched-temp-*' conditions were "
    "minted, because that would duplicate them (same GeoJSONs, same 14-buffer "
    "+ MCC metrics). Their independent house-grain re-score lives at "
    "results/e43-matched-temperature/paper-eval/ and is waived into "
    "_ignored_evals below."
)

ANALYSIS_NOTE = (
    "E72 remediation item 3 (protocol-errata.md § E72; PI-approved 2026-08-02). "
    "The registered erratum E43 reported that T=0.7 'dramatically outperforms' "
    "T=1.0 (ΔF1 ≈ +0.15–0.19, p ≈ 0 at every pool size). That comparison scored "
    "a 240-tile T=1.0 arm (outputs/h11/consensus-384-UNINTENDED-T1.0) against "
    "487-tile bounds, charging 193 of 435 in-bounds ground-truth mounds to it as "
    "automatic false negatives (recall ceiling 0.5563). This analysis is the "
    "matched-scope replacement: both arms live under "
    "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/, both cover 487/487 "
    "tiles, and both are scored at the house grain (14 buffers 5–150 m + "
    "tile-level MCC, BCa 10,000, seed 42) against "
    "inputs/vectors/bounds/384/full_evaluation_bounds.geojson. Evidence: four "
    "paired permutation tests (10,000 permutations, seed 42, 20 m and 30 m) in "
    "results/e43-matched-temperature/n{5,10}-{20,30}m/, plus the per-cell "
    "14-buffer + MCC evaluations in "
    "results/e43-matched-temperature/paper-eval/. NO new conditions were minted: "
    "all four operating points were already first-class pv-diag-384 conditions "
    "(scored at this identical grain on 2026-06-05, "
    "results/rescore-2026-06-05/pv-diag-384/consensus-sweep/), and duplicate "
    "labels would double-count them in every board built from the conditions "
    "manifest — the author_sweep_promotions.py precedent. NOT a finding board "
    "and NOT the paper's temperature evidence: the citable anchor remains the "
    "preregistered Phase 2b sweep (results/retest/phase2b/, text +0.072 FDR "
    "p=0.004; image +0.014 n.s.). tie_set is deliberately left empty: the F1 "
    "contrasts are non-significant (a tie), but the tile-level MCC contrasts "
    "separate the arms with non-overlapping BCa 95 % intervals, so recording a "
    "blanket tie would misdescribe half the evidence."
)

ANALYSIS_OUTCOME = (
    "At matched 487-tile scope the E43 temperature effect does not survive: the "
    "four paired permutation tests are all non-significant and all four point "
    "estimates favour T=1.0 (ΔF1 −0.021 p=0.335 and −0.020 p=0.358 at N=5 for "
    "20 m / 30 m; −0.034 p=0.082 and −0.032 p=0.096 at N=10), against the "
    "+0.168 to +0.194 (p=0.0) reported by the confounded group_4 tests. The "
    "tile-level MCC contrast is stronger and points the same way: 0.3148 vs "
    "0.4065 at N=5 and 0.3655 vs 0.4153 at N=10, with non-overlapping BCa 95 % "
    "confidence intervals in both pairs (an unpaired comparison — no paired MCC "
    "permutation test was run; the operating points were also selected on "
    "F1@20 m, so the MCC values sit on F1-selected thresholds). Honest summary: "
    "no reliable matched-scope temperature advantage for T=0.7 at consensus "
    "level, and on MCC the advantage runs the other way."
)


# --------------------------------------------------------------------------- #
# Loading helpers
# --------------------------------------------------------------------------- #
def eval_rel(cell: str) -> str:
    """Repository-relative path to one reproduction cell's ``evaluation.json``."""
    return f"{PAPER_EVAL}/{cell}/evaluation.json"


def ignored_eval_paths() -> list[str]:
    """The four reproduction eval paths, sorted — the ``_ignored_evals`` addition."""
    return sorted(eval_rel(c[0]) for c in CELLS)


def condition_ids() -> list[str]:
    """The four ALREADY-registered condition ids this analysis compares.

    Returns:
        ``<run_id>::<label>`` foreign keys, in the CELLS order (T=0.7 before
        T=1.0 within each pool size), matching the findings-document tables.
    """
    return [f"{RUN_ID}::{c[6]}" for c in CELLS]


def _summary(path: Path) -> dict:
    """Load an ``evaluation.json`` and return its ``summary`` block."""
    return json.loads(path.read_text())["summary"]


def _f1_at(summary: dict, buffer_m: int) -> float | None:
    """F1 at one buffer, or ``None`` when that buffer was not scored."""
    for row in summary.get("buffers", []):
        if row.get("buffer_metres") == buffer_m:
            return row.get("f1")
    return None


def _mcc(summary: dict) -> float | None:
    """Tile-level MCC point estimate, or ``None`` when absent."""
    return ((summary.get("tile_classification") or {}).get("mcc") or {}).get("point")


def _feature_count(path: Path) -> int:
    """Feature count of a GeoJSON FeatureCollection (no geospatial parse needed)."""
    return len(json.loads(path.read_text()).get("features", []))


def _json_style(raw: str) -> tuple[int, str, bool]:
    """Infer ``(indent, trailing, ensure_ascii)`` from a JSON file's raw text.

    The hand-authored sidecars ``run-conditions.json`` / ``run-analyses.json``
    are stored at **indent 1, no trailing newline, non-ASCII characters
    written literally** — whereas ``json.dumps`` defaults to indent ``None``
    and ``ensure_ascii=True``. Re-emitting a sidecar under the defaults turns a
    four-line edit into a seven-thousand-line diff (every indent level shifts,
    and every em dash becomes ``\\u2014``), which buries the actual change from
    review. The style is therefore measured off the file rather than assumed,
    and the measurement is round-trip-checked in the tier-1 tests.

    Args:
        raw: The file's current text.

    Returns:
        The indent width (from the first top-level key line, defaulting to 1),
        the trailing string ("\\n" or ""), and whether non-ASCII characters
        should be escaped.
    """
    indent = 1
    for line in raw.splitlines()[1:]:
        stripped = line.lstrip(" ")
        if stripped.startswith('"'):
            indent = len(line) - len(stripped)
            break
    return indent, "\n" if raw.endswith("\n") else "", raw.isascii()


def _write_json_in_place(path: Path, obj: dict, raw: str) -> None:
    """Serialise ``obj`` back to ``path`` in the file's own formatting style."""
    indent, trailing, ensure_ascii = _json_style(raw)
    path.write_text(
        json.dumps(obj, indent=indent, ensure_ascii=ensure_ascii) + trailing
    )


# --------------------------------------------------------------------------- #
# Gates
# --------------------------------------------------------------------------- #
def check_gates(repo: Path | None = None) -> list[str]:
    """Run every validation gate; return a list of human-readable failures.

    An empty list means the filing is safe to write. Every gate is a statement
    about on-disk artefacts, so the check is deterministic and needs no API,
    no bootstrap, and no network.

    Args:
        repo: Repository root (defaults to the one this script lives in) —
            parameterised so the tier-1 test can point at a fixture tree.

    Returns:
        Zero or more failure descriptions, each naming the offending cell.
    """
    root = repo or REPO
    failures: list[str] = []

    conds_doc = json.loads((root / "results/run-conditions.json").read_text())
    run_entry = conds_doc.get("decomposition", {}).get(RUN_ID)
    if run_entry is None:
        return [f"run '{RUN_ID}' is not decomposed in results/run-conditions.json"]
    by_label = {c["label"]: c for c in run_entry.get("conditions", [])}

    for cell, arm, n, thr, expect_f1, det_rel, sibling in CELLS:
        tag = f"{cell} ({arm}, N={n}, {thr})"

        eval_path = root / eval_rel(cell)
        if not eval_path.is_file():
            failures.append(f"{tag}: reproduction eval missing at {eval_rel(cell)}")
            continue
        summary = _summary(eval_path)

        # Gate 1 — the house buffer grain, exactly.
        got = tuple(b.get("buffer_metres") for b in summary.get("buffers", []))
        if got != BUFFERS_STANDARD:
            failures.append(f"{tag}: buffers {list(got)} != the 14 standard buffers")

        # Gate 2 — MCC present.
        mcc = _mcc(summary)
        if mcc is None:
            failures.append(f"{tag}: no tile_classification MCC in the reproduction")

        # Gate 3 — the findings.md sanity anchor.
        f20 = _f1_at(summary, 20)
        if f20 is None or abs(round(f20, 4) - expect_f1) >= 5e-4:
            failures.append(
                f"{tag}: F1@20 m {f20} does not reproduce findings.md's {expect_f1}"
            )

        # Gate 4 — detection count agrees with the GeoJSON on disk.
        det_path = root / det_rel
        if not det_path.is_file():
            failures.append(f"{tag}: detections GeoJSON missing at {det_rel}")
        else:
            n_feat = _feature_count(det_path)
            if summary.get("n_detections") != n_feat:
                failures.append(
                    f"{tag}: n_detections {summary.get('n_detections')} != "
                    f"{n_feat} features in {det_rel}"
                )

        # Gate 5 — the registered sibling exists and agrees to 1e-9.
        sib = by_label.get(sibling)
        if sib is None:
            failures.append(
                f"{tag}: expected an already-registered condition "
                f"'{RUN_ID}::{sibling}' and found none — the no-duplicate "
                f"premise of this filing does not hold; re-check before writing"
            )
            continue
        if sib.get("detections") != det_rel:
            failures.append(
                f"{tag}: registered condition '{sibling}' points at "
                f"{sib.get('detections')}, not {det_rel}"
            )
        sib_eval = root / sib["eval_path"]
        if not sib_eval.is_file():
            failures.append(f"{tag}: registered eval missing at {sib['eval_path']}")
            continue
        sib_summary = _summary(sib_eval)
        sib_f20, sib_mcc = _f1_at(sib_summary, 20), _mcc(sib_summary)
        if f20 is None or sib_f20 is None or abs(f20 - sib_f20) > 1e-9:
            failures.append(
                f"{tag}: reproduction F1@20 m {f20} != registered {sib_f20}"
            )
        if mcc is None or sib_mcc is None or abs(mcc - sib_mcc) > 1e-9:
            failures.append(f"{tag}: reproduction MCC {mcc} != registered {sib_mcc}")

    # Gate 6 — assert the no-duplicate outcome rather than assuming it.
    minted = [lbl for lbl in by_label if lbl.startswith("matched-temp-")]
    if minted:
        failures.append(
            f"{RUN_ID} already carries duplicate matched-temperature "
            f"condition(s): {sorted(minted)}"
        )
    return failures


# --------------------------------------------------------------------------- #
# Spec construction
# --------------------------------------------------------------------------- #
def build_analysis_spec() -> dict:
    """Build the ``run-analyses.json`` spec for the matched-temperature filing.

    Human-authored judgement fields that require Shawn's sign-off
    (``paper_section``, ``manually_verified_at``) are left ``null``; the
    ``outcome`` is a factual restatement of the committed artefacts.
    ``predicted_outcome`` is ``null`` because nothing was predicted — this is a
    post-hoc remediation, and the write-once field must not be back-filled once
    the result is known.

    Returns:
        A spec dict ready to append to ``results/run-analyses.json``.
    """
    return {
        "analysis_id": ANALYSIS_ID,
        "type": "comparison",
        "_note": ANALYSIS_NOTE,
        "conditions_compared": condition_ids(),
        "hypothesis_refs": ["H7"],
        "preregistered": "exploratory",
        "deviations": ["E43", "E72"],
        "predicted_outcome": None,
        "tie_set": [],
        "outcome": ANALYSIS_OUTCOME,
        "paper_section": None,
        "output_path": "results/e43-matched-temperature/findings.md",
        "working_notes_obs": [],
        "manually_verified_at": None,
    }


def plan(repo: Path | None = None) -> dict:
    """Compute what a write would change, without touching a file.

    Returns:
        ``{"analysis": "add"|"skip", "ignored_evals_added": [...]}`` — the
        idempotency contract: a second run reports ``skip`` and an empty
        addition list.
    """
    root = repo or REPO
    analyses = json.loads((root / "results/run-analyses.json").read_text())
    existing_ids = {a["analysis_id"] for a in analyses.get("analyses", [])}
    conds = json.loads((root / "results/run-conditions.json").read_text())
    entry = conds.get("decomposition", {}).get(RUN_ID, {})
    already = set(entry.get("_ignored_evals", []))
    return {
        "analysis": "skip" if ANALYSIS_ID in existing_ids else "add",
        "ignored_evals_added": [p for p in ignored_eval_paths() if p not in already],
    }


def apply(repo: Path | None = None) -> dict:
    """Write the analysis spec and the ``_ignored_evals`` waivers. Idempotent.

    Returns:
        The same shape as :func:`plan`, describing what was actually written.
    """
    root = repo or REPO
    todo = plan(root)

    conds_path = root / "results/run-conditions.json"
    conds_raw = conds_path.read_text()
    conds = json.loads(conds_raw)
    entry = conds["decomposition"][RUN_ID]
    if todo["ignored_evals_added"]:
        entry["_ignored_evals"] = sorted(
            set(entry.get("_ignored_evals", [])) | set(ignored_eval_paths())
        )
    if "E72 remediation (2026-08-02)" not in entry.get("_note", ""):
        entry["_note"] = entry.get("_note", "") + CROSSREF_NOTE
    _write_json_in_place(conds_path, conds, conds_raw)

    if todo["analysis"] == "add":
        analyses_path = root / "results/run-analyses.json"
        analyses_raw = analyses_path.read_text()
        analyses = json.loads(analyses_raw)
        analyses["analyses"].append(build_analysis_spec())
        _write_json_in_place(analyses_path, analyses, analyses_raw)
    return todo


def main(argv: list[str] | None = None) -> int:
    """Entry point. Dry-run by default; ``--execute`` writes. Exit 1 on a gate."""
    parser = argparse.ArgumentParser(
        description=(
            "Register the E72 matched-temperature filing: one analysis over the "
            "four EXISTING pv-diag-384 conditions, plus _ignored_evals waivers "
            "for the independent 14-buffer + MCC reproduction. Mints no "
            "conditions (they already exist)."
        )
    )
    parser.add_argument(
        "--execute", action="store_true",
        help="Write the changes (default: dry-run, print the plan only).",
    )
    args = parser.parse_args(argv)

    failures = check_gates()
    if failures:
        print("VALIDATION FAILURES:", flush=True)
        for f in failures:
            print(f"  - {f}", flush=True)
        return 1
    print(f"All {len(CELLS)} cells pass every gate "
          f"(14 buffers + MCC; F1@20 m reproduces findings.md; n_detections "
          f"matches the GeoJSON; registered sibling agrees to 1e-9).", flush=True)

    todo = plan()
    print(f"\nPLAN\n  analysis '{ANALYSIS_ID}': {todo['analysis']}")
    print(f"  conditions minted: 0 (the four cells are already registered: "
          f"{', '.join(condition_ids())})")
    print(f"  _ignored_evals to add ({len(todo['ignored_evals_added'])}):")
    for p in todo["ignored_evals_added"]:
        print(f"    + {p}")

    if not args.execute:
        print("\nDRY-RUN (no files written). Re-run with --execute to author.",
              flush=True)
        return 0

    done = apply()
    print(f"\nWrote results/run-conditions.json "
          f"(+{len(done['ignored_evals_added'])} _ignored_evals) and "
          f"results/run-analyses.json (analysis: {done['analysis']}).")
    print("Next: generate_post_run_report.py --all --write, then "
          "verify_run_conditions.py --run pv-diag-384.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
