#!/usr/bin/env python3
"""
Bootstrap-CI N=10K follow-up sweep verification.

Runs the §7.1–7.5 verification queries from
``archive/planning-completed-session-81-82/daylight-followup-sweep-plan-2026-04-29.md`` against the 165 cells
produced by the daylight follow-up sweep.

* §7.1 — N=10K presence query (binding pass/fail)
* §7.2 — Detection-count cross-check (random 5-cell sample)
* §7.3 — F1 point-estimate stability (random 5-cell sample, |Δ| < 5e-4)
* §7.4 — CI-width comparison (informational only, NOT pass/fail)
* §7.5 — MCC point-estimate stability for the 51 MCC-flag cells (NEW —
         added per user confirmation 2026-04-29; revised 2026-04-29 to
         compare deterministic ``mcc.point`` rather than the bootstrap
         ``mcc.mean``, with graceful fallback when ``mcc.point`` is
         absent — see ``check_mcc_stability`` for full semantics).

Reads the queue at ``/tmp/bootstrap-10k-jobs-followup.csv`` (or the path
passed via ``--queue``); compares each cell's current ``evaluation.json``
against the version captured under git tag ``pre-bootstrap-10k-followup-
2026-04-29`` (or another tag passed via ``--pre-tag``).

Usage:
    python3 scripts/verify_bootstrap_10k_followup.py
    python3 scripts/verify_bootstrap_10k_followup.py --sample-n 10
    python3 scripts/verify_bootstrap_10k_followup.py --pre-tag pre-bootstrap-10k-followup-2026-04-29

Exit codes:
    0 — all binding checks passed (§7.1 + §7.3 sample + §7.5)
    1 — at least one binding check failed
    2 — invocation error (e.g., queue not found)

Author: Claude Code (Opus 4.7) for Shawn Ross's daylight follow-up sweep,
2026-04-29.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUEUE = Path("/tmp/bootstrap-10k-jobs-followup.csv")
DEFAULT_PRE_TAG = "pre-bootstrap-10k-followup-2026-04-29"
# Tolerance accounts for the fact that older evaluation.json files round F1/MCC to 3 or 4
# decimal places, so a re-evaluation against the same inputs can produce |Δ|<5e-4 purely from
# rounding. A real bug shifts F1 by O(1e-2) or larger (cf. the pairwise-bounds dry-run finding,
# which produced ΔF1=0.07 — well above any rounding tolerance).
F1_TOLERANCE = 5e-4         # §7.3 binding tolerance (deterministic F1 point estimate)
MCC_POINT_TOLERANCE = 5e-4  # §7.5 binding tolerance when ``mcc.point`` is available
# Fallback tolerance for when only the bootstrap ``mcc.mean`` is serialised (pre-BCa schema).
# Per Obs 303, the bootstrap mean is itself a Monte-Carlo estimate, so cross-N (N=1K → N=10K)
# drift of O(1e-2) is structural and expected — not a bug. Genuine pipeline corruption shifts
# MCC by O(1e-2) or more (matching the F1 bug-class threshold). The 1e-2 fallback therefore
# still catches real bugs while accepting expected MC noise.
MCC_MEAN_FALLBACK_TOLERANCE = 1e-2  # §7.5 fallback tolerance (bootstrap mean, Obs 303)

#: Rendered wherever the tile-level MCC is not computable (erratum
#: E81). Matches ``evaluate_detections.UNDEFINED_DISPLAY``.
UNDEFINED_DISPLAY = "undefined"


def _fmt_mcc(val: float | None, digits: int = 4) -> str:
    """Format a possibly-undefined MCC for a failure message.

    Args:
        val: The coefficient, or ``None`` when it is undefined
            (degenerate 2 x 2 tile confusion matrix — erratum E81).
        digits: Decimal places for the numeric case.

    Returns:
        The formatted number, or :data:`UNDEFINED_DISPLAY`. A genuine
        zero still renders as ``'0.0000'``, so a definedness-change
        message never reads as though 0 and undefined were the same
        thing.
    """
    return UNDEFINED_DISPLAY if val is None else f"{val:.{digits}f}"


def load_queue(path: Path) -> list[dict[str, str]]:
    """Load the queue CSV."""
    with open(path) as f:
        return list(csv.DictReader(f))


def show_pre_tag(tag: str, repo_path: str) -> dict | None:
    """Return JSON for ``repo_path`` at ``tag`` or None if missing.

    Args:
        tag: Git tag to read from.
        repo_path: Repository-relative path (e.g. ``results/.../evaluation.json``).
    """
    try:
        out = subprocess.check_output(
            ["git", "show", f"{tag}:{repo_path}"],
            cwd=str(REPO_ROOT),
            stderr=subprocess.DEVNULL,
        )
        return json.loads(out.decode())
    except subprocess.CalledProcessError:
        return None


def check_n10k_presence(rows: list[dict[str, str]]) -> tuple[int, int, list[tuple[str, Any]]]:
    """§7.1: every cell's evaluation.json must show ``cli_args.bootstrap == 10000``.

    Returns:
        (n_pass, n_fail, list of (path, observed_value) for failures).
    """
    fails: list[tuple[str, Any]] = []
    n_pass = 0
    for row in rows:
        ep = REPO_ROOT / row["eval_path"]
        if not ep.exists():
            fails.append((row["eval_path"], "MISSING_FILE"))
            continue
        try:
            with open(ep) as f:
                d = json.load(f)
        except json.JSONDecodeError as e:
            fails.append((row["eval_path"], f"JSON_DECODE_ERROR: {e}"))
            continue
        cli = (d.get("_metadata") or {}).get("cli_args") or {}
        bs = cli.get("bootstrap")
        if bs == 10000:
            n_pass += 1
        else:
            fails.append((row["eval_path"], bs))
    return n_pass, len(fails), fails


def check_detection_counts(
    rows: list[dict[str, str]], pre_tag: str, sample_n: int
) -> tuple[int, int, list[str]]:
    """§7.2: per_run.n_detections (or summary.n_detections) must match pre/post.

    Returns:
        (n_match, n_mismatch, list of mismatch descriptions).
    """
    sampled = random.sample(rows, min(sample_n, len(rows)))
    mismatches: list[str] = []
    n_match = 0
    for row in sampled:
        ep_rel = row["eval_path"]
        cur = json.load(open(REPO_ROOT / ep_rel))
        pre = show_pre_tag(pre_tag, ep_rel)
        if pre is None:
            mismatches.append(f"{ep_rel}: pre-tag version missing")
            continue
        cur_pr = cur.get("per_run") or []
        pre_pr = pre.get("per_run") or []
        if cur_pr or pre_pr:
            cur_n = sorted([r.get("n_detections") for r in cur_pr])
            pre_n = sorted([r.get("n_detections") for r in pre_pr])
            if cur_n == pre_n:
                n_match += 1
            else:
                mismatches.append(f"{ep_rel}: per_run pre={pre_n} cur={cur_n}")
        else:
            cur_n = (cur.get("summary") or {}).get("n_detections")
            pre_n = (pre.get("summary") or {}).get("n_detections")
            if cur_n == pre_n:
                n_match += 1
            else:
                mismatches.append(f"{ep_rel}: summary.n_detections pre={pre_n} cur={cur_n}")
    return n_match, len(mismatches), mismatches


def check_f1_stability(
    rows: list[dict[str, str]], pre_tag: str, sample_n: int
) -> tuple[int, int, list[str]]:
    """§7.3: F1 point estimates per buffer must shift by < ``F1_TOLERANCE``.

    Returns:
        (n_pass, n_fail, list of failure descriptions).
    """
    sampled = random.sample(rows, min(sample_n, len(rows)))
    failures: list[str] = []
    n_pass = 0
    for row in sampled:
        ep_rel = row["eval_path"]
        cur = json.load(open(REPO_ROOT / ep_rel))
        pre = show_pre_tag(pre_tag, ep_rel)
        if pre is None:
            failures.append(f"{ep_rel}: pre-tag version missing")
            continue
        cur_b = (cur.get("summary") or {}).get("buffers") or []
        pre_b = (pre.get("summary") or {}).get("buffers") or []
        cell_ok = True
        for cb, pb in zip(cur_b, pre_b):
            df1 = abs(cb.get("f1", 0) - pb.get("f1", 0))
            if df1 >= F1_TOLERANCE:
                failures.append(
                    f"{ep_rel} @ {cb.get('buffer_metres')}m: "
                    f"F1 pre={pb.get('f1'):.4f} cur={cb.get('f1'):.4f} "
                    f"Δ={df1:.5f}"
                )
                cell_ok = False
        if cell_ok:
            n_pass += 1
    return n_pass, len(failures), failures


def check_ci_widths(
    rows: list[dict[str, str]], pre_tag: str, sample_n: int
) -> dict:
    """§7.4: CI widths should be near-identical (informational only).

    Returns a dict of summary statistics on the ratio cur/pre of widths.
    """
    sampled = random.sample(rows, min(sample_n, len(rows)))
    ratios: list[float] = []
    for row in sampled:
        ep_rel = row["eval_path"]
        cur = json.load(open(REPO_ROOT / ep_rel))
        pre = show_pre_tag(pre_tag, ep_rel)
        if pre is None:
            continue
        cur_b = (cur.get("summary") or {}).get("buffers") or []
        pre_b = (pre.get("summary") or {}).get("buffers") or []
        for cb, pb in zip(cur_b, pre_b):
            cur_w = cb.get("f1_ci_upper", 0) - cb.get("f1_ci_lower", 0)
            pre_w = pb.get("f1_ci_upper", 0) - pb.get("f1_ci_lower", 0)
            if pre_w > 0:
                ratios.append(cur_w / pre_w)
    return {
        "n": len(ratios),
        "min": min(ratios) if ratios else None,
        "max": max(ratios) if ratios else None,
        "median": statistics.median(ratios) if ratios else None,
        "mean": statistics.fmean(ratios) if ratios else None,
        "stdev": statistics.pstdev(ratios) if len(ratios) > 1 else None,
    }


def check_mcc_stability(
    rows: list[dict[str, str]], pre_tag: str
) -> tuple[int, int, int, list[str], list[str]]:
    """§7.5 (NEW): for every MCC-flag cell, the deterministic MCC point estimate
    must shift by < ``MCC_POINT_TOLERANCE`` between pre-tag and post-sweep.

    Checks ALL MCC-flag cells (51 total) since the cohort is small.

    Semantics
    ---------
    The original §7.5 implementation compared ``tile_classification.mcc.mean``
    (the *bootstrap* mean) across the N=1K → N=10K upgrade, but per Obs 303
    the bootstrap mean is itself a Monte-Carlo estimate whose drift across N
    is structural and expected (typical magnitude ~O(1e-2)). That produced
    22/51 false-positive failures against the planned 5e-4 tolerance.

    The fix is to compare the deterministic ``tile_classification.mcc.point``
    field instead — a property of the data, not of the resampling procedure
    — which is the right question ("is the underlying data stable?") and is
    semantically aligned with §7.3's F1-point-estimate check.

    Schema availability and fallback
    --------------------------------
    The ``mcc.point`` field is being added by a parallel agent's BCa /
    Mitigation-3 implementation in ``scripts/lib_advanced_metrics.py`` and
    ``scripts/evaluate_detections.py``. Eval JSONs generated *before* that
    landing date will not carry ``mcc.point``. This verifier does NOT
    silently treat the missing field as a pass; it falls back to
    ``mcc.mean`` with a relaxed ``MCC_MEAN_FALLBACK_TOLERANCE`` (1e-2) and
    emits a per-cell warning, so the operator can see how many cells were
    judged on the soft fallback. A bug-class pipeline shift remains
    detectable through the fallback (genuine corruption shifts MCC by
    O(1e-2) or more, matching the F1 bug-class threshold).

    Undefined MCC (erratum E81)
    ---------------------------
    From 2026-08-18 an MCC that is not computable — the 2 x 2 tile
    confusion matrix is degenerate, so the denominator vanishes — is
    serialised as JSON ``null`` instead of a coerced ``0.0``. "Value is
    ``None``" therefore no longer means "field absent", and the check is
    made on DEFINEDNESS first:

    * both sides undefined — PASS. There is no value, hence no drift;
      the old code reported this as "neither mcc.point nor mcc.mean
      available", a spurious failure.
    * one side undefined, the other a number — FAIL. Whether the
      coefficient exists at all changed between the baseline and the
      current file, which is a larger event than any tolerance breach.
    * both sides defined — the tolerance comparison below, unchanged, so
      a genuine MCC of 0.0 is still compared as a number.

    Args:
        rows: Queue rows (with the ``mcc`` flag column).
        pre_tag: Git tag whose committed eval JSONs are the comparison baseline.

    Returns:
        (n_pass, n_fail, n_fallback, failures, fallback_warnings,
        undefined_notes).

        * ``n_pass`` includes strict-mode passes (mcc.point available),
          fallback-mode passes (mcc.mean within 1e-2), and matched-
          undefined passes.
        * ``n_fallback`` is the subset of ``n_pass`` that used the fallback.
        * ``failures`` are cells whose drift exceeded the active tolerance,
          or whose definedness changed.
        * ``fallback_warnings`` lists the cells that used fallback semantics.
        * ``undefined_notes`` lists the cells that passed because both
          sides record the coefficient as undefined.
    """
    mcc_rows = [r for r in rows if r.get("mcc") == "1"]
    failures: list[str] = []
    fallback_warnings: list[str] = []
    undefined_notes: list[str] = []
    n_pass = 0
    n_fallback = 0
    for row in mcc_rows:
        ep_rel = row["eval_path"]
        ep = REPO_ROOT / ep_rel
        if not ep.exists():
            failures.append(f"{ep_rel}: MISSING_FILE")
            continue
        cur = json.load(open(ep))
        pre = show_pre_tag(pre_tag, ep_rel)
        if pre is None:
            failures.append(f"{ep_rel}: pre-tag version missing")
            continue
        cur_tc = (cur.get("summary") or {}).get("tile_classification") or {}
        pre_tc = (pre.get("summary") or {}).get("tile_classification") or {}
        cur_mcc_block = cur_tc.get("mcc") or {}
        pre_mcc_block = pre_tc.get("mcc") or {}

        # Preferred path: deterministic point estimate (BCa-onward schema).
        # E81: gate on key PRESENCE, not on truthiness — a present
        # ``point`` of ``None`` is an assertion that the coefficient is
        # undefined, and must be compared, not skipped.
        cur_point = cur_mcc_block.get("point")
        pre_point = pre_mcc_block.get("point")
        if "point" in cur_mcc_block and "point" in pre_mcc_block:
            if cur_point is None and pre_point is None:
                n_pass += 1
                undefined_notes.append(
                    f"{ep_rel}: mcc.point is {UNDEFINED_DISPLAY} on BOTH "
                    "sides (degenerate tile confusion matrix) — matched "
                    "definedness, nothing to drift"
                )
                continue
            if (cur_point is None) != (pre_point is None):
                failures.append(
                    f"{ep_rel}: mcc.point DEFINEDNESS CHANGED — "
                    f"pre={_fmt_mcc(pre_point)} cur={_fmt_mcc(cur_point)} "
                    "(one side records the coefficient as undefined, the "
                    "other as a number)"
                )
                continue
            dmcc = abs(cur_point - pre_point)
            if dmcc < MCC_POINT_TOLERANCE:
                n_pass += 1
            else:
                failures.append(
                    f"{ep_rel}: mcc.point pre={pre_point:.4f} cur={cur_point:.4f} "
                    f"Δ={dmcc:.5f} (tol={MCC_POINT_TOLERANCE})"
                )
            continue

        # Fallback path: bootstrap mean with relaxed tolerance, with explicit warning.
        cur_mean = cur_mcc_block.get("mean")
        pre_mean = pre_mcc_block.get("mean")
        if "mean" in cur_mcc_block and "mean" in pre_mcc_block:
            if cur_mean is None and pre_mean is None:
                n_pass += 1
                undefined_notes.append(
                    f"{ep_rel}: mcc.mean is {UNDEFINED_DISPLAY} on BOTH "
                    "sides (degenerate tile confusion matrix; mcc.point "
                    "unavailable) — matched definedness, nothing to drift"
                )
                continue
            if (cur_mean is None) != (pre_mean is None):
                failures.append(
                    f"{ep_rel}: FALLBACK mcc.mean DEFINEDNESS CHANGED — "
                    f"pre={_fmt_mcc(pre_mean)} cur={_fmt_mcc(cur_mean)} "
                    "(one side records the coefficient as undefined, the "
                    "other as a number; mcc.point unavailable)"
                )
                continue
        if cur_mean is None or pre_mean is None:
            failures.append(
                f"{ep_rel}: neither mcc.point nor mcc.mean available "
                f"(cur tile_classification keys: {sorted(cur_tc.keys())})"
            )
            continue
        dmcc = abs(cur_mean - pre_mean)
        n_fallback += 1
        if dmcc < MCC_MEAN_FALLBACK_TOLERANCE:
            n_pass += 1
            fallback_warnings.append(
                f"{ep_rel}: FALLBACK mcc.mean pre={pre_mean:.4f} cur={cur_mean:.4f} "
                f"Δ={dmcc:.5f} (fallback tol={MCC_MEAN_FALLBACK_TOLERANCE}; "
                "mcc.point unavailable)"
            )
        else:
            failures.append(
                f"{ep_rel}: FALLBACK mcc.mean pre={pre_mean:.4f} cur={cur_mean:.4f} "
                f"Δ={dmcc:.5f} (fallback tol={MCC_MEAN_FALLBACK_TOLERANCE} EXCEEDED; "
                "mcc.point unavailable — drift exceeds bug-class threshold)"
            )
    return (n_pass, len(failures), n_fallback, failures,
            fallback_warnings, undefined_notes)


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--queue", type=Path, default=DEFAULT_QUEUE,
        help=f"Queue CSV path (default: {DEFAULT_QUEUE})",
    )
    parser.add_argument(
        "--pre-tag", type=str, default=DEFAULT_PRE_TAG,
        help=f"Git tag to compare against (default: {DEFAULT_PRE_TAG})",
    )
    parser.add_argument(
        "--sample-n", type=int, default=5,
        help="Sample size for §7.2-7.4 spot-checks (default: 5)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for sampling (default: 42)",
    )
    args = parser.parse_args()

    if not args.queue.exists():
        print(f"ERROR: queue {args.queue} not found", file=sys.stderr)
        return 2

    random.seed(args.seed)
    rows = load_queue(args.queue)
    print(f"Loaded {len(rows)} cells from {args.queue}")
    print(f"Pre-tag: {args.pre_tag}")
    print()

    # ── §7.1 — binding ───────────────────────────────────────
    print("§7.1 — N=10K presence (BINDING)")
    n_pass, n_fail, fails = check_n10k_presence(rows)
    print(f"  PASS: {n_pass}/{len(rows)} cells at N=10K")
    print(f"  FAIL: {n_fail}")
    for path, val in fails[:10]:
        print(f"    {path}: bootstrap={val}")
    if n_fail > 10:
        print(f"    ... and {n_fail - 10} more failures")
    print()

    # ── §7.2 — sanity sample ────────────────────────────────
    print(f"§7.2 — Detection-count cross-check (random {args.sample_n} cells)")
    n_match, n_mismatch, mismatches = check_detection_counts(rows, args.pre_tag, args.sample_n)
    print(f"  MATCH:    {n_match}/{args.sample_n}")
    print(f"  MISMATCH: {n_mismatch}")
    for m in mismatches:
        print(f"    {m}")
    print()

    # ── §7.3 — F1 stability (binding for spot-check) ────────
    print(f"§7.3 — F1 point-estimate stability (random {args.sample_n} cells; tolerance |Δ|<{F1_TOLERANCE})")
    n_pass_f1, n_fail_f1, f1_fails = check_f1_stability(rows, args.pre_tag, args.sample_n)
    print(f"  PASS: {n_pass_f1}/{args.sample_n} cells with stable F1")
    print(f"  FAIL: {n_fail_f1}")
    for f in f1_fails:
        print(f"    {f}")
    print()

    # ── §7.4 — informational ────────────────────────────────
    print(f"§7.4 — CI-width comparison (random {args.sample_n} cells; INFORMATIONAL)")
    width_stats = check_ci_widths(rows, args.pre_tag, args.sample_n)
    print(f"  n={width_stats['n']} buffer-bands; ratio cur_width/pre_width:")
    print(f"  min={width_stats['min']}, median={width_stats['median']}, "
          f"max={width_stats['max']}, mean={width_stats['mean']}, stdev={width_stats['stdev']}")
    print()

    # ── §7.5 — MCC stability (BINDING for MCC cells) ────────
    print("§7.5 — MCC point-estimate stability for ALL MCC-flag cells (BINDING)")
    print(
        "       Strict: mcc.point comparison, |Δ|<"
        f"{MCC_POINT_TOLERANCE}. Fallback (when mcc.point absent): "
        f"mcc.mean, |Δ|<{MCC_MEAN_FALLBACK_TOLERANCE} (Obs 303 expected drift)."
    )
    (n_pass_mcc, n_fail_mcc, n_fallback_mcc, mcc_fails, mcc_warns,
     mcc_undefined) = check_mcc_stability(rows, args.pre_tag)
    n_mcc = sum(1 for r in rows if r.get("mcc") == "1")
    # Decomposition: every fallback case (pass or fail) appears in either ``mcc_warns``
    # (fallback-PASS) or as a FALLBACK-tagged entry in ``mcc_fails`` (fallback-FAIL).
    n_fallback_fail = sum(1 for f in mcc_fails if "FALLBACK" in f)
    n_fallback_pass = len(mcc_warns)
    # E81: matched-undefined cells pass on neither the strict-value nor
    # the fallback-value path, so they are decomposed out separately.
    n_undefined_pass = len(mcc_undefined)
    n_strict_pass = n_pass_mcc - n_fallback_pass - n_undefined_pass
    print(f"  Total MCC-flag cells: {n_mcc}")
    print(
        f"  PASS: {n_pass_mcc}/{n_mcc} "
        f"(strict-mcc.point: {n_strict_pass}; fallback-mcc.mean: "
        f"{n_fallback_pass}; matched-{UNDEFINED_DISPLAY}: {n_undefined_pass})"
    )
    print(f"  FAIL: {n_fail_mcc} (of which {n_fallback_fail} on fallback path)")
    for f in mcc_fails[:20]:
        print(f"    {f}")
    if n_fail_mcc > 20:
        print(f"    ... and {n_fail_mcc - 20} more failures")
    if mcc_warns:
        print(
            f"  WARNING: {len(mcc_warns)} cell(s) judged on soft fallback "
            "(mcc.point absent — re-run after BCa schema lands for strict semantics):"
        )
        for w in mcc_warns[:10]:
            print(f"    {w}")
        if len(mcc_warns) > 10:
            print(f"    ... and {len(mcc_warns) - 10} more fallback warnings")
    if mcc_undefined:
        print(
            f"  NOTE: {len(mcc_undefined)} cell(s) record an "
            f"{UNDEFINED_DISPLAY} MCC on BOTH sides (erratum E81 — "
            "degenerate tile confusion matrix). Matched definedness is a "
            "PASS; it is NOT a measured agreement at 0:"
        )
        for u in mcc_undefined[:10]:
            print(f"    {u}")
        if len(mcc_undefined) > 10:
            print(f"    ... and {len(mcc_undefined) - 10} more")
    print()

    # ── Final verdict ────────────────────────────────────────
    binding_failed = (n_fail > 0) or (n_fail_mcc > 0) or (n_fail_f1 > 0)
    if binding_failed:
        print("VERDICT: FAIL — binding checks did not pass")
        return 1
    print("VERDICT: PASS — all binding checks passed (§7.1 + §7.3 sample + §7.5)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
