#!/usr/bin/env python3
# ============================================================================
# audit_verifier_completeness.py
# ----------------------------------------------------------------------------
# Walks the repository and audits every `probabilities.json` file for
# verifier-completeness: each file's `results` keyset must match the candidate
# IDs listed in its sibling `candidate_manifest.json`.
#
# Background:
#     The 2026-05-03 verifier-completeness audit
#     (`reports/phase3a-verifier-completeness-audit-2026-05-03.md`) was carried
#     out via an ad-hoc script at `/tmp/verifier_audit.py` that no longer
#     exists. This is the tracked, reproducible replacement. Running this
#     script can be promoted to a tier-2 pytest gate once the campaign-wide
#     state is gap-zero.
#
# Logic:
#     For every `probabilities.json` (post-exemption), look up the sibling
#     `candidate_manifest.json` in the same directory, then compute:
#         expected = len(manifest["candidates"])
#         actual   = len({k.split("_iter")[0] for k in probs["results"]})
#         gap      = expected - actual
#     Multi-iteration runs encode the iteration index as a `_iterK` suffix on
#     each result key; stripping it before deduplication mirrors the
#     `compute_gap()` helper in `planning/run-phase3a-recovery.sh`.
#
# Exemptions (silent — never reported):
#     - paths under `archive/**`           (historical / superseded snapshots)
#     - files ending in `.backup`          (pre-cleanup-* sibling snapshots)
#
# All other unusual cases (no sibling manifest, schema mismatch, non-empty
# `cleanup_history`, etc.) are surfaced as REVIEW entries rather than silently
# skipped, so the operator can confirm intentionality.
#
# Output:
#     - Per-cell verdicts in three buckets: PASS / FAIL / REVIEW
#     - Markdown-friendly summary table
#     - Optional JSON dump via --json for CI consumption
#     - Exit code 0 if no FAIL, 1 if any FAIL
#
# Usage:
#     .venv/bin/python scripts/audit_verifier_completeness.py
#     .venv/bin/python scripts/audit_verifier_completeness.py --verbose
#     .venv/bin/python scripts/audit_verifier_completeness.py --json out.json
#
# Author: Claude Opus 4.7 (1M context) / Shawn Ross (operator)
# Licence: Apache 2.0
# ============================================================================

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO_ROOT_DEFAULT = Path(__file__).resolve().parent.parent


@dataclass
class CellAudit:
    """Result of auditing a single `probabilities.json` against its manifest."""

    path: str  # repo-relative
    verdict: str  # PASS | FAIL | REVIEW
    expected: int | None  # candidates in manifest (None = unknown)
    actual: int | None  # unique candidate IDs in results (None = read error)
    gap: int | None  # expected - actual; None if either side unknown
    cleanup_history_entries: int  # how many cleanup_history records the file has
    review_reasons: list[str] = field(default_factory=list)


def is_exempt(rel_path: Path) -> bool:
    """Apply the silent exemption rules.

    Currently: paths under `archive/**` and files ending `.backup` are exempt
    from auditing. All other paths flow into the audit pipeline and either
    PASS, FAIL, or REVIEW (so the operator can review intentionality).
    """
    if any(part == "archive" for part in rel_path.parts):
        return True
    if str(rel_path).endswith(".backup"):
        return True
    return False


def find_probabilities_files(root: Path) -> list[Path]:
    """Return all non-exempt `probabilities.json` files under root."""
    found: list[Path] = []
    for p in root.rglob("probabilities.json"):
        rel = p.relative_to(root)
        if is_exempt(rel):
            continue
        found.append(p)
    return sorted(found)


def count_unique_candidates(results: dict | list | None) -> int:
    """Count unique candidate IDs in a `results` field, stripping `_iterK`.

    Multi-iteration runs encode the iteration index as a `_iterK` suffix on
    each result key. Mirrors the deduplication logic in `compute_gap()` in
    `planning/run-phase3a-recovery.sh`.
    """
    if not isinstance(results, dict):
        return 0
    seen: set[str] = set()
    for key in results:
        base = key.split("_iter")[0] if "_iter" in key else key
        seen.add(base)
    return len(seen)


def audit_one(prob_path: Path, root: Path) -> CellAudit:
    """Audit a single probabilities.json against its sibling manifest."""
    rel = str(prob_path.relative_to(root))
    review_reasons: list[str] = []

    # Read probabilities.json
    try:
        prob = json.loads(prob_path.read_text())
    except Exception as exc:
        return CellAudit(
            path=rel,
            verdict="REVIEW",
            expected=None,
            actual=None,
            gap=None,
            cleanup_history_entries=0,
            review_reasons=[f"probabilities_read_error: {type(exc).__name__}: {exc}"],
        )

    if not isinstance(prob, dict):
        return CellAudit(
            path=rel,
            verdict="REVIEW",
            expected=None,
            actual=None,
            gap=None,
            cleanup_history_entries=0,
            review_reasons=["probabilities_root_not_object"],
        )

    results = prob.get("results")
    if results is None:
        review_reasons.append("missing_results_key")
    actual = count_unique_candidates(results)

    cleanup_history = prob.get("cleanup_history") or []
    cleanup_history_entries = len(cleanup_history) if isinstance(cleanup_history, list) else 0

    # Sibling manifest
    manifest_path = prob_path.parent / "candidate_manifest.json"
    if not manifest_path.exists():
        review_reasons.append("no_sibling_manifest")
        return CellAudit(
            path=rel,
            verdict="REVIEW",
            expected=None,
            actual=actual,
            gap=None,
            cleanup_history_entries=cleanup_history_entries,
            review_reasons=review_reasons,
        )

    try:
        manifest = json.loads(manifest_path.read_text())
    except Exception as exc:
        review_reasons.append(f"manifest_read_error: {type(exc).__name__}: {exc}")
        return CellAudit(
            path=rel,
            verdict="REVIEW",
            expected=None,
            actual=actual,
            gap=None,
            cleanup_history_entries=cleanup_history_entries,
            review_reasons=review_reasons,
        )

    candidates = manifest.get("candidates")
    if not isinstance(candidates, list):
        review_reasons.append("manifest_missing_candidates_list")
        return CellAudit(
            path=rel,
            verdict="REVIEW",
            expected=None,
            actual=actual,
            gap=None,
            cleanup_history_entries=cleanup_history_entries,
            review_reasons=review_reasons,
        )

    expected = len(candidates)
    gap = expected - actual

    # Anomaly: any cleanup_history record that itself reports residual
    # `still_missing > 0` is worth flagging even if the current state is
    # gap-zero (the audit trail records that a partial-cleanup state was
    # accepted at some point).
    if cleanup_history_entries > 0:
        last = cleanup_history[-1] if isinstance(cleanup_history[-1], dict) else {}
        still_missing = last.get("still_missing", 0)
        if isinstance(still_missing, int) and still_missing > 0:
            review_reasons.append(f"cleanup_history_still_missing={still_missing}")

    if gap > 0:
        verdict = "FAIL"
    elif review_reasons:
        verdict = "REVIEW"
    else:
        verdict = "PASS"

    # Record an unusual gap < 0 (more results than candidates — should not
    # happen unless the manifest was edited downstream).
    if gap < 0:
        verdict = "REVIEW"
        review_reasons.append(f"surplus_results: actual={actual} > expected={expected}")

    return CellAudit(
        path=rel,
        verdict=verdict,
        expected=expected,
        actual=actual,
        gap=gap,
        cleanup_history_entries=cleanup_history_entries,
        review_reasons=review_reasons,
    )


def audit_repo(root: Path) -> list[CellAudit]:
    """Audit every non-exempt probabilities.json under root."""
    probs = find_probabilities_files(root)
    return [audit_one(p, root) for p in probs]


def render_summary(audits: list[CellAudit], verbose: bool = False) -> str:
    """Render a Markdown-friendly summary string."""
    by_verdict = {"PASS": [], "FAIL": [], "REVIEW": []}
    for a in audits:
        by_verdict[a.verdict].append(a)

    lines: list[str] = []
    lines.append(f"Audited {len(audits)} probabilities.json files (post-exemption).")
    lines.append("")
    lines.append(f"  PASS:   {len(by_verdict['PASS'])}")
    lines.append(f"  FAIL:   {len(by_verdict['FAIL'])}")
    lines.append(f"  REVIEW: {len(by_verdict['REVIEW'])}")
    lines.append("")

    if by_verdict["FAIL"]:
        lines.append("=== FAIL — gap > 0 (must address) ===")
        lines.append("")
        for a in sorted(by_verdict["FAIL"], key=lambda x: -(x.gap or 0)):
            lines.append(f"  gap={a.gap:>5}  ({a.actual}/{a.expected})  {a.path}")
        lines.append("")

    if by_verdict["REVIEW"]:
        lines.append("=== REVIEW — unusual structure (confirm intentionality) ===")
        lines.append("")
        for a in sorted(by_verdict["REVIEW"], key=lambda x: x.path):
            reasons = "; ".join(a.review_reasons) or "(no specific reason captured)"
            lines.append(f"  {a.path}")
            lines.append(f"      reasons: {reasons}")
        lines.append("")

    if verbose and by_verdict["PASS"]:
        lines.append("=== PASS (verbose) ===")
        lines.append("")
        for a in sorted(by_verdict["PASS"], key=lambda x: x.path):
            lines.append(f"  ({a.actual}/{a.expected})  {a.path}")
        lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit verifier-output completeness across the repo."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT_DEFAULT,
        help="Repository root (defaults to the script's parent of parent).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show every PASS cell as well, not just FAIL/REVIEW.",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Optional path to dump the per-cell results as JSON.",
    )
    args = parser.parse_args(argv)

    audits = audit_repo(args.root)
    print(render_summary(audits, verbose=args.verbose))

    if args.json is not None:
        args.json.write_text(json.dumps([asdict(a) for a in audits], indent=2))
        print(f"JSON written: {args.json}")

    fails = sum(1 for a in audits if a.verdict == "FAIL")
    return 1 if fails > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
