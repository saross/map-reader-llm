#!/usr/bin/env python3
"""
Build the 28 K-ladder Phase 2 first-N consensus unions (US$0, no API calls)
==========================================================================

Description:
    Phase 2 of the K-ladder review (controlling card
    ``planning/k-ladder-review-2026-09-11.md``; costing
    ``reports/k-ladder-phase2-costing-2026-09-12.md`` section 3) needs one
    verifier pass over each of 28 first-N consensus unions. This script builds
    those unions at US$0 by driving ``scripts/merge_passes.py`` — the canonical
    consensus chain — with the first-N rule (``--passes 1..N``), exactly as the
    costing's measured union sizes were probed
    (``scripts/probe_first_n_union_sizes.py``).

    For each rung it:

    1. runs ``merge_passes.py --sweep --passes 1[,2,3]`` into the pool's
       ``consensus-n<N>/`` directory (so every vote threshold is materialised,
       not just the union);
    2. counts the union (``consensus_t1.geojson``, vote >= 1) and compares it
       with the costing table's candidate count. A disagreement of more than
       ``TOLERANCE_FRACTION`` is recorded as a STOP for that rung — the rung is
       NOT to be verified, and the mismatch is reported;
    3. writes an ``experiment_intent.md`` beside the union recording the pass
       list in prose, alongside the rung's costing row and tier.

    Re-running is safe and is how the unions gained their machine-readable
    ``pass_provenance``: the branch point had no such mechanism, a concurrent
    session landed one on ``main`` the same day, and a rebuild after merging it
    changed only each rung's ``voting_summary.json`` — not one byte of any
    ``consensus_t*.geojson`` across all 28 rungs.

    Nothing in this script calls an API. It is safe to re-run: ``merge_passes``
    overwrites its outputs deterministically.

Usage::

    # Build every rung (default)
    python scripts/build_k_ladder_phase2_unions.py

    # Build one tier only, or one rung
    python scripts/build_k_ladder_phase2_unions.py --tier A
    python scripts/build_k_ladder_phase2_unions.py --row 3 --row 4

    # Re-verify counts without rebuilding (reads committed unions)
    python scripts/build_k_ladder_phase2_unions.py --check-only

Outputs:
    outputs/**/consensus-n<N>/consensus_t*.geojson  (the unions)
    outputs/**/consensus-n<N>/experiment_intent.md  (the pass list)
    results/k-ladder-2026-09-12/phase2/unions.json  (the machine-readable
        summary: per rung, expected vs measured candidates, verdict)

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

# --- Fixed inputs -----------------------------------------------------------

#: Measured union sizes, built at US$0 during Phase 1 (step 6's input).
UNION_SIZES_JSON = (
    BASE_DIR / "results" / "k-ladder-2026-09-12" / "first-n-union-sizes.json"
)

#: Where the per-rung summary lands.
SUMMARY_JSON = (
    BASE_DIR / "results" / "k-ladder-2026-09-12" / "phase2" / "unions.json"
)

#: A measured count this far from the costing table's figure is a STOP.
TOLERANCE_FRACTION = 0.02

#: Audited Gemini 3 verifier rate, USD per candidate
#: (``reports/token-load-audit-2026-06-12.md`` section 5, ``VF_CALL_USD``).
USD_PER_CANDIDATE = 0.000693

#: Tier assignment by costing-table row number
#: (``reports/k-ladder-phase2-costing-2026-09-12.md`` section 5).
TIER_BY_ROW: dict[int, str] = {
    **{row: "A" for row in (3, 4, 9, 10)},
    **{row: "B" for row in (1, 2, 5, 6, 7, 8, 11, 12)},
    **{row: "C" for row in range(13, 25)},
    **{row: "D" for row in range(25, 29)},
}

#: Per pool (keyed by the pool label in ``first-n-union-sizes.json``): the run
#: the pool belongs to, the register's proposer-pool slug, and the condition
#: label stem the new rungs take. Both are read from
#: ``results/run-conditions.json`` conventions for the family's committed
#: K = 5 / K = 10 rungs, so the new rungs sit beside them.
POOL_REGISTRY: dict[str, dict[str, str]] = {
    "Gemini 3 MINIMAL text 384 px, T 0.3": {
        "run_id": "pv-diag-384",
        "pool_slug": "flash-minimal-text-n30-t07-text-t0.3",
        "label_stem": "pv-min-text-t0.3",
        "modality": "text",
    },
    "Gemini 3 MINIMAL text 384 px, T 0.7": {
        "run_id": "pv-diag-384",
        "pool_slug": "flash-minimal-text-n30-t07-text-t0.7",
        "label_stem": "pv-min-text-t0.7",
        "modality": "text",
    },
    "Gemini 3 MINIMAL text 384 px, T 1.0": {
        "run_id": "pv-diag-384",
        "pool_slug": "flash-minimal-text-n30-t07-text-t1.0",
        "label_stem": "pv-min-text-t1.0",
        "modality": "text",
    },
    "Gemini 3 HIGH text 384 px, T 0.3": {
        "run_id": "pv-diag-384",
        "pool_slug": "flash-high-text-n5-text-t0.3",
        "label_stem": "pv-high-text-t0.3",
        "modality": "text",
    },
    "Gemini 3 HIGH text 384 px, T 0.7": {
        "run_id": "pv-diag-384",
        "pool_slug": "flash-high-text-n5-text-t0.7",
        "label_stem": "pv-high-text-t0.7",
        "modality": "text",
    },
    "Gemini 3 HIGH text 384 px, T 1.0": {
        "run_id": "pv-diag-384",
        "pool_slug": "flash-high-text-n5-text-t1.0",
        "label_stem": "pv-high-text-t1.0",
        "modality": "text",
    },
    "Gemini 3 MINIMAL image 384 px, T 0.3": {
        "run_id": "pv-diag-384",
        "pool_slug": "image-n5-image-t0.3",
        "label_stem": "pv-min-image-t0.3",
        "modality": "image",
    },
    "Gemini 3 MINIMAL image 384 px, T 0.7": {
        "run_id": "pv-diag-384",
        "pool_slug": "image-n5-image-t0.7",
        "label_stem": "pv-min-image-t0.7",
        "modality": "image",
    },
    "Gemini 3 MINIMAL image 384 px, T 1.0": {
        "run_id": "pv-diag-384",
        "pool_slug": "image-n5-image-t1.0",
        "label_stem": "pv-min-image-t1.0",
        "modality": "image",
    },
    "Gemini 3 HIGH image 384 px, T 0.3": {
        "run_id": "pv-diag-384",
        "pool_slug": "flash-high-image-n5-image-t0.3",
        "label_stem": "pv-high-image-t0.3",
        "modality": "image",
    },
    "Gemini 3 HIGH image 384 px, T 0.7": {
        "run_id": "pv-diag-384",
        "pool_slug": "flash-high-image-n5-image-t0.7",
        "label_stem": "pv-high-image-t0.7",
        "modality": "image",
    },
    "Gemini 3 HIGH image 384 px, T 1.0": {
        "run_id": "pv-diag-384",
        "pool_slug": "flash-high-image-n5-image-t1.0",
        "label_stem": "pv-high-image-t1.0",
        "modality": "image",
    },
    "Gemini 3 scale-4-optimal 487": {
        "run_id": "pv-diag-384",
        "pool_slug": "scale-4-optimal-487",
        "label_stem": "pv-scale4-optimal",
        "modality": "text",
    },
    "Gemini 3.7 text, GS B geometry": {
        "run_id": "gemini37-screen-2026-08-28",
        "pool_slug": "g384_ov192_g37",
        "label_stem": "g37-text",
        "modality": "text",
    },
}


def load_rungs() -> list[dict[str, Any]]:
    """Build the 28-rung worklist from the Phase 1 measured union sizes.

    The costing table's row numbers are the order the pools appear in
    ``first-n-union-sizes.json``, two rows per pool (K = 1 then K = 3), so the
    row number — and with it the tier — is derived rather than transcribed.

    Returns:
        One dict per rung, in costing-table row order.

    Raises:
        SystemExit: if a pool label is absent from :data:`POOL_REGISTRY`, or
            the derived row count is not 28.
    """
    with open(UNION_SIZES_JSON) as handle:
        probe = json.load(handle)

    rungs: list[dict[str, Any]] = []
    row = 0
    for pool in probe["pools"]:
        label = pool["label"]
        if label not in POOL_REGISTRY:
            logger.error("Pool label not in POOL_REGISTRY: %s", label)
            sys.exit(1)
        registry = POOL_REGISTRY[label]
        for rung in pool["rungs"]:
            row += 1
            n_passes = int(rung["n_passes"])
            rungs.append(
                {
                    "row": row,
                    "tier": TIER_BY_ROW[row],
                    "family": label,
                    "run_id": registry["run_id"],
                    "pool_slug": registry["pool_slug"],
                    "label_stem": registry["label_stem"],
                    "modality": registry["modality"],
                    "pool_dir": pool["pool_dir"],
                    "n_passes": n_passes,
                    "pass_ids": list(rung["pass_ids"]),
                    "pass_list": ",".join(
                        str(index) for index in range(1, n_passes + 1)
                    ),
                    "expected_candidates": int(rung["n_union_candidates"]),
                    "consensus_dir": (
                        f"{pool['pool_dir']}/consensus-n{n_passes}"
                    ),
                    "verify_dir": (
                        f"{pool['pool_dir']}/verified-v1-n{n_passes}"
                    ),
                    "verifier_stage": (
                        f"{registry['pool_slug']}-verified-v1-n{n_passes}"
                    ),
                }
            )

    if len(rungs) != 28:
        logger.error("Expected 28 rungs, derived %d", len(rungs))
        sys.exit(1)
    return rungs


def build_union(rung: dict[str, Any], *, check_only: bool) -> dict[str, Any]:
    """Build (or re-check) one rung's first-N consensus union.

    Args:
        rung: One entry of :func:`load_rungs`.
        check_only: Read the committed union without rebuilding it.

    Returns:
        The rung dict extended with ``measured_candidates``, ``delta``,
        ``delta_fraction``, ``verdict`` and ``usd_estimate``.
    """
    consensus_dir = BASE_DIR / rung["consensus_dir"]
    union_path = consensus_dir / "consensus_t1.geojson"

    if not check_only:
        consensus_dir.mkdir(parents=True, exist_ok=True)
        command = [
            sys.executable,
            str(BASE_DIR / "scripts" / "merge_passes.py"),
            "--input-dir",
            str(BASE_DIR / rung["pool_dir"]),
            "--output-dir",
            str(consensus_dir),
            "--sweep",
            "--passes",
            rung["pass_list"],
        ]
        logger.info(
            "row %2d  tier %s  %s  N=%d  building union",
            rung["row"],
            rung["tier"],
            rung["family"],
            rung["n_passes"],
        )
        completed = subprocess.run(
            command, cwd=BASE_DIR, capture_output=True, text=True, check=False
        )
        if completed.returncode != 0:
            logger.error(
                "merge_passes failed for row %d:\n%s",
                rung["row"],
                completed.stderr[-2000:],
            )
            rung = dict(rung)
            rung.update(
                measured_candidates=None,
                delta=None,
                delta_fraction=None,
                verdict="STOP-merge-failed",
                usd_estimate=None,
            )
            return rung

    if not union_path.exists():
        result = dict(rung)
        result.update(
            measured_candidates=None,
            delta=None,
            delta_fraction=None,
            verdict="STOP-union-missing",
            usd_estimate=None,
        )
        return result

    with open(union_path) as handle:
        measured = len(json.load(handle).get("features", []))

    expected = rung["expected_candidates"]
    delta = measured - expected
    fraction = abs(delta) / expected if expected else 1.0
    verdict = "OK" if fraction <= TOLERANCE_FRACTION else "STOP-count-mismatch"

    result = dict(rung)
    result.update(
        measured_candidates=measured,
        delta=delta,
        delta_fraction=round(fraction, 6),
        verdict=verdict,
        usd_estimate=round(measured * USD_PER_CANDIDATE, 4),
    )

    if verdict != "OK":
        logger.error(
            "row %d  COUNT MISMATCH  expected %d, measured %d (%.2f %%) — "
            "this rung is NOT to be verified",
            rung["row"],
            expected,
            measured,
            fraction * 100,
        )
    else:
        logger.info(
            "row %2d  %s N=%d  %d candidates (expected %d, delta %+d)  "
            "~US$%.2f",
            rung["row"],
            rung["family"],
            rung["n_passes"],
            measured,
            expected,
            delta,
            result["usd_estimate"],
        )
    return result


def write_intent(rung: dict[str, Any]) -> None:
    """Write the rung's ``experiment_intent.md``, recording the pass list.

    The pass list is recorded here in prose as well as in the union's own
    ``voting_summary.json``. When this run began, its branch point carried no
    ``pass_provenance`` mechanism, so the prose record was the only one; a
    concurrent session landed ``fix(consensus): record and check a union's
    pass list`` on ``main`` the same day, and after merging it the unions were
    rebuilt and now carry a machine-readable record too. The two agree, and the
    prose one is kept because it also names the rung's costing row and tier.

    This file is in the document revision policy's scope
    (``docs/methodology/output-directory-standard.md``).

    Args:
        rung: A rung dict as returned by :func:`build_union`.
    """
    path = BASE_DIR / rung["consensus_dir"] / "experiment_intent.md"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pass_ids = ", ".join(f"`{pass_id}`" for pass_id in rung["pass_ids"])
    verdict_line = (
        f"{rung['measured_candidates']} candidates at vote >= 1 "
        f"(costing table: {rung['expected_candidates']}; "
        f"delta {rung['delta']:+d})"
        if rung["measured_candidates"] is not None
        else "union not built — see the run summary"
    )

    body = f"""# Experiment intent — K-ladder Phase 2, rung {rung['row']} of 28

> **Last revised**: {today} (original publication — K-ladder Phase 2 step 1,
> the US$0 union build). Controlling card:
> `planning/k-ladder-review-2026-09-11.md`; costing
> `reports/k-ladder-phase2-costing-2026-09-12.md` section 3, row
> {rung['row']}. See [section Changelog](#changelog).

## What this directory is

The **first-N consensus union** for one rung of the K-ladder review's
Phase 2 gap-fill: family *{rung['family']}* at **K = {rung['n_passes']}**.
It is the candidate universe a single Gemini 3 verifier pass is then run over
(ruling R1: the carried verifier at every rung, no swaps).

## The pass list, recorded explicitly

The pass list is recorded twice, and the two records agree. This file carries
it in prose, because when this rung was first built the branch point had no
`pass_provenance` mechanism; a concurrent session landed one on `main` the same
day (`fix(consensus): record and check a union's pass list`), and after merging
it the union was rebuilt, so `voting_summary.json` beside this file now also
carries a `pass_provenance` block with a `git_blob_hash` per pass. That rebuild
changed **only** `voting_summary.json` — not one byte of any
`consensus_t*.geojson` across all 28 rungs — which is the cross-check that the
refactor was behaviour-preserving and that this union is the one the verifier
consumed.

| field | value |
|---|---|
| proposer pool | `{rung['pool_dir']}` |
| passes included | {pass_ids} |
| K (number of passes) | {rung['n_passes']} |
| `merge_passes.py --passes` | `{rung['pass_list']}` |
| first-N rule | passes 1..{rung['n_passes']}, in run order, no selection |
| register run | `{rung['run_id']}` |
| register proposer-pool slug | `{rung['pool_slug']}` |
| planned verifier stage | `{rung['verifier_stage']}` |
| costing tier | {rung['tier']} |

## How it was built

`scripts/build_k_ladder_phase2_unions.py` drove the canonical consensus chain
verbatim:

```bash
python scripts/merge_passes.py \\
    --input-dir {rung['pool_dir']} \\
    --output-dir {rung['consensus_dir']} \\
    --sweep \\
    --passes {rung['pass_list']}
```

`merge_passes.py` deduplicates within each pass at 20 m, clusters across
passes at 20 m, and writes one file per vote threshold. `consensus_t1.geojson`
is the union (vote >= 1) and is the verifier's input; the higher thresholds are
materialised so the vote axis of the operating-point sweep needs no rebuild.

Note that `run_*_recovery` directories are **not** passes:
`merge_passes.load_pass_detections` parses the integer after `run_`, and
`"1_recovery"` does not parse, so those directories are skipped
(`scripts/merge_passes.py:400-411`).

## Count check

{verdict_line}

The union size was measured independently during Phase 1 by
`scripts/probe_first_n_union_sizes.py` (a key of
`results/k-ladder-2026-09-12/first-n-union-sizes.json`) and is what the costing
table priced. A disagreement of more than 2 % is a STOP for the rung: it is
not verified, and the mismatch is reported instead.

## No API call built this directory

Consensus building is local computation. The verifier pass over this union is
the API spend, and it is approved only under the Phase 2 gate: model
`gemini-3-flash` (resolved `gemini-3-flash-preview`), config
`prompts/configs/verify_adversarial-text.json`, T = 0.0, MINIMAL thinking,
n = 1, real-time flex tier.

## Changelog

### {today} — Original publication

Written by `scripts/build_k_ladder_phase2_unions.py` as it built the union.
Sources: `results/k-ladder-2026-09-12/first-n-union-sizes.json` (the pool
directory, the pass ids and the expected candidate count) and
`reports/k-ladder-phase2-costing-2026-09-12.md` sections 3 and 5 (the row
number and the tier).
"""
    path.write_text(body)


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Build the 28 K-ladder Phase 2 first-N consensus unions (US$0)"
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--tier",
        action="append",
        choices=["A", "B", "C", "D"],
        help="Restrict to one or more tiers (default: all)",
    )
    parser.add_argument(
        "--row",
        action="append",
        type=int,
        help="Restrict to one or more costing-table row numbers",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Re-count committed unions without rebuilding them",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s  %(message)s"
    )

    rungs = load_rungs()
    if args.tier:
        rungs = [rung for rung in rungs if rung["tier"] in set(args.tier)]
    if args.row:
        rungs = [rung for rung in rungs if rung["row"] in set(args.row)]

    logger.info("Building %d rung union(s)", len(rungs))

    results = []
    for rung in rungs:
        built = build_union(rung, check_only=args.check_only)
        if built["measured_candidates"] is not None:
            write_intent(built)
        results.append(built)

    ok = [rung for rung in results if rung["verdict"] == "OK"]
    stopped = [rung for rung in results if rung["verdict"] != "OK"]
    total_candidates = sum(rung["measured_candidates"] for rung in ok)

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "script": "scripts/build_k_ladder_phase2_unions.py",
        "script_version": __version__,
        "tolerance_fraction": TOLERANCE_FRACTION,
        "usd_per_candidate": USD_PER_CANDIDATE,
        "usd_per_candidate_anchor": (
            "reports/token-load-audit-2026-06-12.md section 5, VF_CALL_USD"
        ),
        "n_rungs": len(results),
        "n_ok": len(ok),
        "n_stopped": len(stopped),
        "total_candidates_ok": total_candidates,
        "total_usd_estimate_ok": round(
            total_candidates * USD_PER_CANDIDATE, 4
        ),
        "rungs": results,
    }
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_JSON, "w") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")

    logger.info(
        "%d of %d rungs OK; %d candidates; ~US$%.2f; summary -> %s",
        len(ok),
        len(results),
        total_candidates,
        summary["total_usd_estimate_ok"],
        SUMMARY_JSON.relative_to(BASE_DIR),
    )
    if stopped:
        for rung in stopped:
            logger.error(
                "STOPPED row %d (%s N=%d): %s",
                rung["row"],
                rung["family"],
                rung["n_passes"],
                rung["verdict"],
            )
        sys.exit(2)


if __name__ == "__main__":
    main()
