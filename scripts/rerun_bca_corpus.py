#!/usr/bin/env python3
"""E82 corpus re-emission: replay every BCa-era evaluation at B = 10,000.

Executes the campaign specified in
``planning/e82-corpus-reemission-2026-08-20.md`` (pre-run-review contract,
PI-approved 2026-08-20): every git-tracked, non-archive evaluation whose
metadata vintage is 1.1 or 1.2 — the BCa era, selected by VINTAGE rather than
by declared method so the 22 method-silent register-backing cells are included
without assuming what they ran (the D17 principle) — is replayed from its own
recovered recipe with only the bootstrap effort standardised, through the
fixed wrapper (``122104b8a``) and the current writer. Re-emitted files land at
metadata 1.3, which is also the resume criterion: a restart processes exactly
the remainder.

Guards, per the contract's stop states:

* **Point gate** — F1/precision/recall per buffer, the observed tile points,
  and the confusion counts must reproduce exactly (1e-9); a moving point
  leaves the committed file untouched and counts as a failure.
* **Width tripwire** — a 20 m F1 interval that NARROWS below 0.8x on replay
  is impossible under the D15 model and is treated as a failure.
* **Systematic-failure abort** — more than 5 failures aborts the run.
* Recipes are recovered via the D22 fallback chain
  (``build_bca_migration_queue.recover_recipe``); buffers and the MCC flag
  come from what the evaluation MEASURED (``summary``), not from the recorded
  argparse namespace; batch-vintage globs are dropped so the canonical
  resolver applies (defect D6).

Usage::

    python scripts/rerun_bca_corpus.py --dry-run          # census only
    python scripts/rerun_bca_corpus.py --pilot 10 --workers 4
    python scripts/rerun_bca_corpus.py --workers 10

$0 API. Run on sapphire (contract § 3.4). Created 2026-08-20 (Session 138).
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.build_bca_migration_queue import (  # noqa: E402
    buffers_that_ran,
    recover_recipe,
)
from scripts.rerun_evals_at_10k import (  # noqa: E402
    SIBLINGS,
    TARGET_B,
    TOLERANCE,
    point_table,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REPORT_PATH = PROJECT_ROOT / "results/e82-corpus-reemission-2026-08-20.json"
SELECT_VINTAGES = ("1.1", "1.2")
DONE_VINTAGE = "1.3"
MAX_FAILURES = 5
MIN_WIDTH_RATIO = 0.8
MEDIAN_BAND = (1.05, 6.0)
TILE_METRICS = ("mcc", "sensitivity", "specificity")


def select_targets(tracked: list[str]) -> tuple[list[str], dict[str, int]]:
    """Partition tracked evaluations into the worklist and skip census."""
    worklist: list[str] = []
    census: dict[str, int] = {"selected": 0, "done_1.3": 0, "other_vintage": 0,
                              "unparseable": 0, "no_recipe": 0}
    for rel in tracked:
        if rel.startswith("archive/"):
            continue
        try:
            doc = json.loads((PROJECT_ROOT / rel).read_text())
        except (json.JSONDecodeError, OSError):
            census["unparseable"] += 1
            continue
        ver = str((doc.get("_metadata") or {}).get("metadata_version", ""))
        if ver == DONE_VINTAGE:
            census["done_1.3"] += 1
            continue
        if ver not in SELECT_VINTAGES:
            census["other_vintage"] += 1
            continue
        recipe = recover_recipe(doc)
        paths_ok = _recipe_paths_exist(recipe)
        if not paths_ok:
            census["no_recipe"] += 1
            continue
        census["selected"] += 1
        worklist.append(rel)
    return worklist, census


def _recipe_paths_exist(recipe: dict[str, Any]) -> bool:
    """True when every input the recipe names exists on disk."""
    det = recipe.get("detections") or recipe.get("detections_dir")
    gt, bounds = recipe.get("ground_truth"), recipe.get("bounds")
    if not (det and gt and bounds):
        return False
    dets = det if isinstance(det, list) else [det]
    return (all((PROJECT_ROOT / d).exists() for d in dets)
            and (PROJECT_ROOT / str(gt)).exists()
            and (PROJECT_ROOT / str(bounds)).exists())


def build_command(doc: dict, recipe: dict[str, Any], workdir: Path) -> list[str]:
    """Assemble the replay invocation from measurements, not declarations."""
    cmd = [sys.executable, str(PROJECT_ROOT / "scripts/evaluate_detections.py")]
    original_cli = (doc.get("_metadata") or {}).get("cli_args") or {}
    recovered = not (original_cli.get("detections")
                     or original_cli.get("detections_dir"))
    if recipe.get("detections"):
        det = recipe["detections"]
        cmd += ["--detections"] + (det if isinstance(det, list) else [det])
    else:
        cmd += ["--detections-dir", str(recipe["detections_dir"])]
        # A batch-vintage glob names only one filename convention and
        # under-reads mixed pools (D6); recovered rows use the canonical
        # resolver instead. A directly recorded glob is replayed verbatim.
        if recipe.get("glob") and not recovered:
            cmd += ["--glob", recipe["glob"]]
    cmd += ["--ground-truth", str(recipe["ground_truth"]),
            "--bounds", str(recipe["bounds"]),
            "--bootstrap", str(TARGET_B),
            "--seed", str(recipe.get("seed", 42)),
            "--output-dir", str(workdir)]
    buffers = buffers_that_ran(doc, recipe)
    if buffers:
        cmd += ["--buffers"] + [str(b) for b in buffers]
    label = recipe.get("label") or (doc.get("summary") or {}).get("label")
    if label:
        cmd += ["--label", str(label)]
    if isinstance((doc.get("summary") or {}).get("tile_classification"), dict):
        cmd += ["--mcc"]
    return cmd


def tile_point_table(doc: dict) -> dict[str, Any]:
    """Observed tile points and confusion counts, for the extended gate."""
    tc = (doc.get("summary") or {}).get("tile_classification") or {}
    out: dict[str, Any] = {}
    for metric in TILE_METRICS:
        block = tc.get(metric)
        if isinstance(block, dict) and block.get("point") is not None:
            out[metric] = block["point"]
        elif isinstance(block, (int, float)):
            out[metric] = block
    conf = tc.get("confusion")
    if isinstance(conf, dict):
        out["confusion"] = {k: conf.get(k) for k in ("tp", "tn", "fp", "fn")}
    return out


def ci20_width(doc: dict) -> float | None:
    """The 20 m F1 interval width, where present."""
    for b in (doc.get("summary") or {}).get("buffers", []):
        if b.get("buffer_metres") == 20:
            lo, hi = b.get("f1_ci_lower"), b.get("f1_ci_upper")
            return (hi - lo) if lo is not None and hi is not None else None
    return None


def process_one(rel: str) -> dict[str, Any]:
    """Replay one evaluation and gate it; runs in a worker process.

    Returns a row dict with ``status`` in {ok, failed}; on ``ok`` the
    committed siblings have been replaced.
    """
    path = PROJECT_ROOT / rel
    before = json.loads(path.read_text())
    recipe = recover_recipe(before)
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        cmd = build_command(before, recipe, work)
        try:
            subprocess.run(cmd, check=True, cwd=PROJECT_ROOT,
                           capture_output=True, text=True)
        except subprocess.CalledProcessError as exc:
            return {"evaluation": rel, "status": "failed",
                    "reason": "replay error",
                    "detail": (exc.stderr or "")[-500:]}
        after = json.loads((work / "evaluation.json").read_text())

        pb, pa = point_table(before), point_table(after)
        moved = {f"{k[0]}m/{k[1]}": (pb[k], pa[k]) for k in pb
                 if k in pa and abs(pb[k] - pa[k]) > TOLERANCE}
        missing = sorted(f"{k[0]}m/{k[1]}" for k in set(pb) - set(pa))
        tb, ta = tile_point_table(before), tile_point_table(after)
        tile_moved = {k: (tb[k], ta.get(k)) for k in tb if tb[k] != ta.get(k)}
        if moved or missing or tile_moved:
            return {"evaluation": rel, "status": "failed",
                    "reason": "point estimates moved",
                    "moved": {**moved, **tile_moved}, "missing": missing}

        wb, wa = ci20_width(before), ci20_width(after)
        ratio = (wa / wb) if (wb and wa) else None
        if ratio is not None and ratio < MIN_WIDTH_RATIO:
            return {"evaluation": rel, "status": "failed",
                    "reason": f"width ratio {ratio:.3f} < {MIN_WIDTH_RATIO}",
                    "width_ratio": ratio}

        for name in SIBLINGS:
            src = work / name
            if src.exists():
                shutil.copy2(src, path.parent / name)
    return {"evaluation": rel, "status": "ok",
            "bootstrap_before": (before["_metadata"].get("bootstrap") or {})
            .get("n_iterations"),
            "width_ratio": ratio}


def main() -> int:
    """Census, pilot, or full corpus run with the contract's tripwires."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="Census the worklist; write nothing.")
    ap.add_argument("--pilot", type=int, default=None,
                    help="Process only the first N files.")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--report-out", type=Path, default=REPORT_PATH)
    args = ap.parse_args()

    tracked = subprocess.run(["git", "ls-files", "*evaluation.json"],
                             capture_output=True, text=True, check=True,
                             cwd=PROJECT_ROOT).stdout.split()
    worklist, census = select_targets(tracked)
    logger.info("census: %s", census)
    if args.dry_run:
        return 0
    if args.pilot:
        worklist = sorted(worklist)[:args.pilot]
    logger.info("processing %d file(s) with %d worker(s)",
                len(worklist), args.workers)

    rows: list[dict[str, Any]] = []
    failures = 0
    aborted = False
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pending = {pool.submit(process_one, rel): rel for rel in worklist}
        for i, fut in enumerate(as_completed(pending), 1):
            row = fut.result()
            rows.append(row)
            if row["status"] == "failed":
                failures += 1
                logger.error("[%d/%d] FAILED %s: %s", i, len(worklist),
                             row["evaluation"], row["reason"])
                if failures > MAX_FAILURES:
                    aborted = True
                    logger.error("aborting: > %d failures (contract § 3.1)",
                                 MAX_FAILURES)
                    for f in pending:
                        f.cancel()
                    break
            elif i % 25 == 0 or i == len(worklist):
                logger.info("[%d/%d] ok (latest ratio %.2fx)", i,
                            len(worklist), row.get("width_ratio") or 0)

    ratios = sorted(r["width_ratio"] for r in rows
                    if r["status"] == "ok" and r.get("width_ratio"))
    median = ratios[len(ratios) // 2] if ratios else None
    ok = [r for r in rows if r["status"] == "ok"]
    logger.info("ok %d / failed %d; width ratio min %.3f median %.3f max %.3f",
                len(ok), failures,
                ratios[0] if ratios else float("nan"),
                median if median else float("nan"),
                ratios[-1] if ratios else float("nan"))

    existing = (json.loads(args.report_out.read_text())
                if args.report_out.exists() else {"runs": []})
    existing.setdefault("contract",
                        "planning/e82-corpus-reemission-2026-08-20.md")
    existing["runs"].append({
        "pilot": args.pilot, "workers": args.workers, "aborted": aborted,
        "n_ok": len(ok), "n_failed": failures,
        "width_ratio_median": median, "rows": rows,
    })
    args.report_out.write_text(json.dumps(existing, indent=2) + "\n")
    logger.info("report -> %s", args.report_out)

    if aborted or failures > MAX_FAILURES:
        return 1
    if median is not None and not (MEDIAN_BAND[0] <= median <= MEDIAN_BAND[1]):
        logger.error("median width ratio %.3f outside %s (contract § 3.2)",
                     median, MEDIAN_BAND)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
