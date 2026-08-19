#!/usr/bin/env python3
"""
Re-run every register-backing evaluation that ran below B = 10 000, at B = 10 000.

The 2026-08-19 Principal-Investigator ruling standardises the study on 10 000
bootstrap iterations rather than the 1 000 Decision 10 pre-specified, and
requires that every recorded declaration match what was actually run. 49 of the
evaluations backing `results/conditions-manifest.json` ran at B = 1 000. This
script replays each from its own `_metadata.cli_args` with the iteration count
overridden, so nothing changes except the resampling effort.

Scope is taken from the conditions manifest rather than a file sweep. A sweep
also reaches `archive/`, whose evaluations are superseded by definition, and
pre-2026-04-30 artefacts that predate the BCa migration and carry no CI method
at all. Neither backs a live claim; both are covered as history by E82.

Two guards, because this rewrites committed artefacts:

- **Point-estimate gate.** F1, precision, and recall are deterministic given the
  inputs and must not move. Any drift beyond 1e-9 aborts that cell and leaves the
  committed file untouched.
- **Replay fidelity.** The detections, ground truth, bounds, buffers, seed, and
  MCC flag all come from the committed `cli_args`. Only `bootstrap` is changed.

Intervals WILL move, and will generally widen: at B = 10 000 against 340-487
evaluation tiles this is the `B > n` regime, where the D15 axis defect made
committed intervals too narrow.

Usage::

    python scripts/rerun_evals_at_10k.py --dry-run     # report, write nothing
    python scripts/rerun_evals_at_10k.py               # rewrite in place

Notes:
    - Zero API spend.
    - Run on sapphire: 49 evaluations x 10 000 resamples x 14 buffers.

Created: 2026-08-19 (Session 137)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

TARGET_B = 10_000
POINT_KEYS = ("f1", "precision", "recall")
SIBLINGS = ("evaluation.json", "evaluation.csv", "evaluation.md")
TOLERANCE = 1e-9


def needs_rerun(path: Path) -> int | None:
    """Return the declared iteration count if it is below target, else None."""
    try:
        doc = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    b = (doc.get("_metadata", {}).get("bootstrap") or {}).get("n_iterations")
    return b if isinstance(b, int) and b != TARGET_B else None


def point_table(doc: dict) -> dict[tuple[int, str], float]:
    """Extract every deterministic point estimate, keyed by (buffer, metric)."""
    out: dict[tuple[int, str], float] = {}
    for b in doc.get("summary", {}).get("buffers", []):
        for k in POINT_KEYS:
            if b.get(k) is not None:
                out[(b["buffer_metres"], k)] = b[k]
    return out


def replay(path: Path, workdir: Path) -> Path:
    """Re-run one evaluation at the target iteration count into ``workdir``."""
    args = json.loads(path.read_text())["_metadata"]["cli_args"]
    cmd = [sys.executable, str(PROJECT_ROOT / "scripts/evaluate_detections.py")]
    # `--detections` is nargs="+", so every file goes under ONE flag. Repeating
    # the flag makes argparse keep only the last, which silently turns a
    # three-run averaged evaluation into a single-pass one — caught here by the
    # point-estimate gate on the three H13 arms rather than written to disk.
    if args.get("detections"):
        cmd += ["--detections"] + list(args["detections"])
    elif args.get("detections_dir"):
        cmd += ["--detections-dir", args["detections_dir"]]
        if args.get("glob"):
            cmd += ["--glob", args["glob"]]
    else:
        raise ValueError(f"{path}: cli_args names no detections input")
    cmd += [
        "--ground-truth", args["ground_truth"],
        "--bounds", args["bounds"],
        "--bootstrap", str(TARGET_B),
        "--seed", str(args.get("seed", 42)),
        "--output-dir", str(workdir),
    ]
    if args.get("buffers"):
        cmd += ["--buffers"] + [str(b) for b in args["buffers"]]
    if args.get("label"):
        cmd += ["--label", args["label"]]
    if args.get("mcc"):
        cmd += ["--mcc"]
    subprocess.run(cmd, check=True, cwd=PROJECT_ROOT, capture_output=True, text=True)
    return workdir / "evaluation.json"


def main() -> int:
    """Re-run every below-target evaluation, gated on point-estimate stability."""
    parser = argparse.ArgumentParser(
        description="Re-run register-backing evaluations at B=10,000.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would change; write nothing.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Process at most N evaluations (for smoke-testing).")
    args = parser.parse_args()

    # Drive off the conditions manifest, not a blind file sweep. The register is
    # what has to be true, and a sweep also picks up `archive/`, whose evaluations
    # are superseded BY DEFINITION and must not be rewritten. It also picks up
    # pre-2026-04-30 artefacts that predate the BCa migration entirely and carry
    # no CI method at all; those are history, covered by E82, not live claims.
    manifest = json.loads(
        (PROJECT_ROOT / "results/conditions-manifest.json").read_text())
    sources: list[str] = []
    for cond in manifest["conditions"]:
        for src in (cond.get("provenance") or {}).get("source_files") or []:
            if src.endswith("evaluation.json") and not src.startswith("archive/"):
                sources.append(src)
    targets = []
    for rel in sorted(set(sources)):
        p = PROJECT_ROOT / rel
        if not p.exists():
            continue
        b = needs_rerun(p)
        if b is not None:
            targets.append((rel, b))
    if args.limit:
        targets = targets[:args.limit]
    logger.info("evaluations below B=%d: %d", TARGET_B, len(targets))

    report: list[dict[str, Any]] = []
    failures = 0
    for i, (rel, old_b) in enumerate(targets, 1):
        path = PROJECT_ROOT / rel
        before = json.loads(path.read_text())
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            try:
                new_path = replay(path, work)
            except subprocess.CalledProcessError as exc:
                logger.error("[%d/%d] %s: replay FAILED\n%s", i, len(targets), rel,
                             (exc.stderr or "")[-800:])
                failures += 1
                continue
            after = json.loads(new_path.read_text())

            pb, pa = point_table(before), point_table(after)
            moved = {k: (pb[k], pa[k]) for k in pb
                     if k in pa and abs(pb[k] - pa[k]) > TOLERANCE}
            missing = set(pb) - set(pa)
            if moved or missing:
                logger.error("[%d/%d] %s: POINT ESTIMATES MOVED (%d) / missing (%d) "
                             "— left untouched", i, len(targets), rel,
                             len(moved), len(missing))
                for k, (o, n) in list(moved.items())[:3]:
                    logger.error("      %s: %.6f -> %.6f", k, o, n)
                failures += 1
                continue

            def ci20(doc):
                for b in doc["summary"]["buffers"]:
                    if b["buffer_metres"] == 20:
                        return b.get("f1_ci_lower"), b.get("f1_ci_upper")
                return (None, None)

            lo_b, hi_b = ci20(before)
            lo_a, hi_a = ci20(after)
            row = {
                "evaluation": rel,
                "bootstrap_before": old_b,
                "bootstrap_after": TARGET_B,
                "f1_ci20_before": [lo_b, hi_b],
                "f1_ci20_after": [lo_a, hi_a],
            }
            if None not in (lo_b, hi_b, lo_a, hi_a):
                wb, wa = hi_b - lo_b, hi_a - lo_a
                row["width_before"], row["width_after"] = wb, wa
                row["width_ratio"] = (wa / wb) if wb else None
                logger.info("[%d/%d] %s | B %d->%d | CI20 width %.4f -> %.4f (%.2fx)",
                            i, len(targets), Path(rel).parent.name, old_b, TARGET_B,
                            wb, wa, wa / wb if wb else float("nan"))
            else:
                logger.info("[%d/%d] %s | B %d->%d | no 20 m CI",
                            i, len(targets), Path(rel).parent.name, old_b, TARGET_B)
            report.append(row)

            if not args.dry_run:
                for name in SIBLINGS:
                    src = work / name
                    if src.exists():
                        shutil.copy2(src, path.parent / name)

    out = PROJECT_ROOT / "results/bootstrap-10k-restandardisation.json"
    payload = {
        "target_bootstrap": TARGET_B,
        "rationale": "2026-08-19 PI ruling, erratum E82: the study standardises on "
                     "10,000 iterations. Point estimates are gated to zero drift; "
                     "only interval widths move.",
        "dry_run": args.dry_run,
        "n_rerun": len(report),
        "n_failed": failures,
        "evaluations": report,
    }
    if not args.dry_run:
        out.write_text(json.dumps(payload, indent=2))
        logger.info("wrote %s", out)

    widths = [r["width_ratio"] for r in report if r.get("width_ratio")]
    if widths:
        widths.sort()
        logger.info("CI20 width ratio: min %.3f, median %.3f, max %.3f",
                    widths[0], widths[len(widths)//2], widths[-1])
        logger.info("  widened: %d of %d", sum(1 for w in widths if w > 1), len(widths))
    if failures:
        logger.error("%d evaluation(s) failed and were left untouched", failures)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
