#!/usr/bin/env python3
"""
Run the carried Gemini 3 verifier over the 28 K-ladder Phase 2 unions
=====================================================================

Description:
    Phase 2 of the K-ladder review, tiers A-D, approved by the PI on
    2026-09-12 at US$24.84 (`reports/k-ladder-phase2-costing-2026-09-12.md`
    sections 3 and 5). For each rung this script extracts 150 x 150 px crops
    from the source rasters and runs ONE verifier pass over the rung's first-N
    consensus union, with the carried production verifier and nothing else
    (ruling R1: no verifier swaps).

    The gate this script is allowed to spend under, and nothing wider:

    ============  ==================================================
    model         ``gemini-3-flash`` (resolves to
                  ``gemini-3-flash-preview``)
    config        ``prompts/configs/verify_adversarial-text.json``
    temperature   0.0 (from the config; never overridden)
    thinking      MINIMAL (from the config; never overridden)
    iterations    1
    tier          real-time **flex**
    budget        US$24.84 estimated, **hard stop at US$30**
    ============  ==================================================

    **The flex correction.** ``scripts/run_pv.py`` passes ``--service-tier`` to
    the API but stamps nothing about it into ``run.meta.json``: the meta records
    ``cost_basis: "list"``, ``discount: 1.0`` and
    ``discount_reason: "no discount applied"`` even for a flex run, and no field
    names the tier (``reports/r7-gaps-deltas-2026-09-11.md`` section 2.3;
    re-confirmed on a smoke run in
    ``results/k-ladder-2026-09-12/phase2/pre_launch_audit.md`` warning 1). So
    this script computes the audited flex cost itself, from the meta's token
    counts, on the basis every cost column in the corpus uses:

        USD = input_tokens x 0.25 / 1e6
            + (output_tokens + thoughts_tokens) x 1.50 / 1e6

    which is half of list (0.50 / 3.00 per million). The running total is
    checked against :data:`HARD_STOP_USD` after every rung, and the script
    exits rather than starting another rung once it is exceeded.

Usage::

    # One tier at a time, in the approved order
    python scripts/run_k_ladder_phase2_verifier.py --tier A --workers 20
    python scripts/run_k_ladder_phase2_verifier.py --tier B --workers 20
    python scripts/run_k_ladder_phase2_verifier.py --tier C --workers 20
    python scripts/run_k_ladder_phase2_verifier.py --tier D --workers 20

    # What would run, and what it would cost, without calling the API
    python scripts/run_k_ladder_phase2_verifier.py --tier A --plan-only

    # Re-read the ledger from the committed metas (no API calls)
    python scripts/run_k_ladder_phase2_verifier.py --recompute-ledger

Outputs:
    outputs/**/verified-v1-n<N>/{probabilities.json,run.meta.json}
    outputs/**/verified-v1-n<N>/crops/candidate_manifest.json
    results/k-ladder-2026-09-12/phase2/spend-ledger.json

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

UNIONS_JSON = (
    BASE_DIR / "results" / "k-ladder-2026-09-12" / "phase2" / "unions.json"
)
LEDGER_JSON = (
    BASE_DIR
    / "results"
    / "k-ladder-2026-09-12"
    / "phase2"
    / "spend-ledger.json"
)

VERIFIER_CONFIG = (
    BASE_DIR / "prompts" / "configs" / "verify_adversarial-text.json"
)

#: Flex-tier rates, USD per million tokens: half of the list 0.50 / 3.00.
FLEX_INPUT_PER_M = 0.25
FLEX_OUTPUT_PER_M = 1.50

#: The run stops rather than starting another rung once the audited flex
#: total passes this. The PI approved US$24.84.
HARD_STOP_USD = 30.00

#: Crop padding: 75 px each side, giving the 150 x 150 verifier standard
#: (E33's fix; every committed pv-diag-384 crops manifest records it).
PADDING_PX = 75

#: Pools whose verifier stage does not live inside the proposer pool
#: directory. The 3.7 GS screen keeps its verifier tree separate, with crops
#: as a sibling of the verify directory (``crops`` / ``crops_k10`` beside
#: ``verify`` / ``verify_k10``), so the new rungs follow that family.
STAGE_OVERRIDES: dict[str, dict[int, dict[str, str]]] = {
    "outputs/gemini37-screen-2026-08-28/g384_ov192_g37": {
        1: {
            "verify_dir": (
                "outputs/gemini37-screen-2026-08-28/verifier/"
                "g384_ov192_g37/verify_k1"
            ),
            "crops_dir": (
                "outputs/gemini37-screen-2026-08-28/verifier/"
                "g384_ov192_g37/crops_k1"
            ),
            "verifier_stage": "g384_ov192_g37-union-k1-verify",
            "tiles_dir": "inputs/tiles_384_ov192",
        },
        3: {
            "verify_dir": (
                "outputs/gemini37-screen-2026-08-28/verifier/"
                "g384_ov192_g37/verify_k3"
            ),
            "crops_dir": (
                "outputs/gemini37-screen-2026-08-28/verifier/"
                "g384_ov192_g37/crops_k3"
            ),
            "verifier_stage": "g384_ov192_g37-union-k3-verify",
            "tiles_dir": "inputs/tiles_384_ov192",
        },
    }
}


def resolve_paths(rung: dict[str, Any]) -> dict[str, str]:
    """Resolve a rung's verify directory, crops directory and tiles directory.

    Args:
        rung: One rung of ``unions.json``.

    Returns:
        A dict with ``verify_dir``, ``crops_dir``, ``verifier_stage`` and
        ``tiles_dir``, relative to the repository root.
    """
    override = STAGE_OVERRIDES.get(rung["pool_dir"], {}).get(rung["n_passes"])
    if override:
        return dict(override)
    return {
        "verify_dir": rung["verify_dir"],
        "crops_dir": f"{rung['verify_dir']}/crops",
        "verifier_stage": rung["verifier_stage"],
        "tiles_dir": "inputs/tiles",
    }


def audited_flex_usd(meta: dict[str, Any]) -> dict[str, float]:
    """Recompute a verifier run's cost on the audited flex basis.

    The meta's own ``cost_estimate`` is list price with ``discount: 1.0``
    regardless of the tier actually used, so the flex figure is derived from
    the token counts rather than read from the file.

    Args:
        meta: A parsed ``run.meta.json``.

    Returns:
        ``input_tokens``, ``output_tokens``, ``thoughts_tokens``,
        ``flex_usd`` and ``list_usd_recorded``.
    """
    stats = meta.get("execution_stats", {})
    finish = stats.get("finish_reason_counts", {})
    usage = meta.get("usage_stats", {})
    input_tokens = int(usage.get("total_input_tokens", 0))
    output_tokens = int(usage.get("total_output_tokens", 0))
    thoughts = int(usage.get("total_thoughts_tokens", 0) or 0)
    flex = (
        input_tokens * FLEX_INPUT_PER_M
        + (output_tokens + thoughts) * FLEX_OUTPUT_PER_M
    ) / 1_000_000.0
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "thoughts_tokens": thoughts,
        "flex_usd": round(flex, 6),
        "list_usd_recorded": float(
            meta.get("cost_estimate", {}).get("total_cost_usd", 0.0)
        ),
        # Two different counts, kept apart because they diverge whenever the
        # API returns a retryable error: `candidates_verified` is how many
        # candidates got a probability, `api_requests` is how many calls were
        # billed (successes plus retried attempts). Row 10 of tier A, for
        # instance, verified 2,755 candidates in 2,898 requests after 143
        # server-error retries, all of which returned empty and so cost
        # almost nothing.
        "candidates_verified": int(finish.get("success", 0))
        or int(stats.get("items_processed", 0)),
        "api_requests": int(
            usage.get("by_provider", {})
            .get("google_gemini", {})
            .get("request_count", 0)
        )
        or sum(int(value) for value in finish.values()),
        "retries_total": int(stats.get("retries_total", 0)),
        "retries_server_error": int(stats.get("retries_server_error", 0)),
        "retries_rate_limit_meta": int(stats.get("retries_rate_limit", 0)),
    }


def load_ledger() -> dict[str, Any]:
    """Read the spend ledger, or start a fresh one."""
    if LEDGER_JSON.exists():
        with open(LEDGER_JSON) as handle:
            return json.load(handle)
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "basis": (
            "flex: input x 0.25 + (output + thinking) x 1.50 per million USD, "
            "recomputed from run.meta.json token counts because the verify "
            "path stamps cost_basis 'list' with discount 1.0 under flex"
        ),
        "hard_stop_usd": HARD_STOP_USD,
        "approved_usd": 24.84,
        "rungs": {},
    }


def save_ledger(ledger: dict[str, Any]) -> None:
    """Write the spend ledger, refreshing its derived totals."""
    rungs = ledger["rungs"]
    by_tier: dict[str, dict[str, float]] = {}
    for entry in rungs.values():
        tier = by_tier.setdefault(
            entry["tier"],
            {
                "rungs": 0,
                "candidates": 0,
                "calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "thoughts_tokens": 0,
                "flex_usd": 0.0,
                "list_usd_recorded": 0.0,
                "wall_seconds": 0.0,
            },
        )
        tier["rungs"] += 1
        tier["candidates"] += entry["candidates"]
        tier["calls"] += entry.get("api_requests") or entry["items_processed"]
        tier["candidates_verified"] = tier.get("candidates_verified", 0) + (
            entry.get("candidates_verified") or entry["items_processed"]
        )
        tier["retries_total"] = tier.get("retries_total", 0) + entry.get(
            "retries_total", 0
        )
        tier["input_tokens"] += entry["input_tokens"]
        tier["output_tokens"] += entry["output_tokens"]
        tier["thoughts_tokens"] += entry["thoughts_tokens"]
        tier["flex_usd"] += entry["flex_usd"]
        tier["list_usd_recorded"] += entry["list_usd_recorded"]
        tier["wall_seconds"] += entry["wall_seconds"]
    for tier in by_tier.values():
        tier["flex_usd"] = round(tier["flex_usd"], 4)
        tier["list_usd_recorded"] = round(tier["list_usd_recorded"], 4)
        tier["wall_seconds"] = round(tier["wall_seconds"], 1)
        tier["flex_usd_per_candidate"] = (
            round(tier["flex_usd"] / tier["candidates"], 8)
            if tier["candidates"]
            else None
        )

    ledger["updated_at_utc"] = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )
    ledger["by_tier"] = dict(sorted(by_tier.items()))
    ledger["total"] = {
        "rungs": len(rungs),
        "candidates": sum(tier["candidates"] for tier in by_tier.values()),
        "candidates_verified": sum(
            tier.get("candidates_verified", 0) for tier in by_tier.values()
        ),
        "calls": sum(tier["calls"] for tier in by_tier.values()),
        "retries_total": sum(
            tier.get("retries_total", 0) for tier in by_tier.values()
        ),
        "flex_usd": round(
            sum(tier["flex_usd"] for tier in by_tier.values()), 4
        ),
        "list_usd_recorded": round(
            sum(tier["list_usd_recorded"] for tier in by_tier.values()), 4
        ),
        "wall_seconds": round(
            sum(tier["wall_seconds"] for tier in by_tier.values()), 1
        ),
    }
    LEDGER_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_JSON, "w") as handle:
        json.dump(ledger, handle, indent=2)
        handle.write("\n")


def run_step(command: list[str], label: str) -> tuple[bool, str]:
    """Run one subprocess step, returning success and its tail of output."""
    completed = subprocess.run(
        command, cwd=BASE_DIR, capture_output=True, text=True, check=False
    )
    tail = (completed.stdout[-1500:] + completed.stderr[-2500:]).strip()
    if completed.returncode != 0:
        logger.error("%s FAILED (exit %d)\n%s", label, completed.returncode, tail)
        return False, tail
    return True, tail


def verify_rung(
    rung: dict[str, Any], *, workers: int, ledger: dict[str, Any]
) -> dict[str, Any] | None:
    """Extract crops for one rung and run a single verifier pass over it.

    Args:
        rung: One rung of ``unions.json``.
        workers: Real-time concurrency passed to ``run_pv.py verify``.
        ledger: The spend ledger, updated in place and saved per rung.

    Returns:
        The ledger entry for the rung, or ``None`` if a step failed.
    """
    paths = resolve_paths(rung)
    key = f"row{rung['row']:02d}-{paths['verifier_stage']}"
    union = f"{rung['consensus_dir']}/consensus_t1.geojson"
    started = time.time()

    logger.info(
        "=== row %d  tier %s  %s  K=%d  (%d candidates, ~US$%.2f) ===",
        rung["row"],
        rung["tier"],
        rung["family"],
        rung["n_passes"],
        rung["measured_candidates"],
        rung["usd_estimate"],
    )

    ok, _ = run_step(
        [
            sys.executable,
            "scripts/run_pv.py",
            "extract",
            "--proposer",
            union,
            "--output-dir",
            paths["crops_dir"],
            "--padding",
            str(PADDING_PX),
            "--tiles-dir",
            paths["tiles_dir"],
        ],
        f"{key} extract",
    )
    if not ok:
        return None

    manifest_path = BASE_DIR / paths["crops_dir"] / "candidate_manifest.json"
    with open(manifest_path) as handle:
        manifest = json.load(handle)
    if manifest["successful_extractions"] != rung["measured_candidates"]:
        logger.error(
            "%s: extracted %d crops for %d candidates — refusing to verify",
            key,
            manifest["successful_extractions"],
            rung["measured_candidates"],
        )
        return None
    if manifest["tile_fallback_crops"]:
        logger.error(
            "%s: %d crops came from tile PNGs, not rasters (E33) — "
            "refusing to verify",
            key,
            manifest["tile_fallback_crops"],
        )
        return None

    ok, _ = run_step(
        [
            sys.executable,
            "scripts/run_pv.py",
            "verify",
            "--crops-dir",
            paths["crops_dir"],
            "--verifier-config",
            str(VERIFIER_CONFIG.relative_to(BASE_DIR)),
            "--output-dir",
            paths["verify_dir"],
            "--mode",
            "realtime",
            "--workers",
            str(workers),
            "--service-tier",
            "flex",
        ],
        f"{key} verify",
    )
    if not ok:
        return None

    with open(BASE_DIR / paths["verify_dir"] / "run.meta.json") as handle:
        meta = json.load(handle)
    cost = audited_flex_usd(meta)
    stats = meta.get("execution_stats", {})
    finish = stats.get("finish_reason_counts", {})
    # items_processed is 0 in some historical metas; the finish-reason counts
    # are the reliable call count.
    calls = sum(int(value) for value in finish.values()) or int(
        meta.get("usage_stats", {})
        .get("by_provider", {})
        .get("google_gemini", {})
        .get("request_count", 0)
    )

    entry = {
        "row": rung["row"],
        "tier": rung["tier"],
        "family": rung["family"],
        "n_passes": rung["n_passes"],
        "run_id": rung["run_id"],
        "pool_slug": rung["pool_slug"],
        "verifier_stage": paths["verifier_stage"],
        "verify_dir": paths["verify_dir"],
        "crops_dir": paths["crops_dir"],
        "union": union,
        "candidates": rung["measured_candidates"],
        "items_processed": calls,
        "items_failed": int(stats.get("items_failed", 0)),
        "parse_failures": int(stats.get("parse_failures", 0)),
        "retries_rate_limit": int(stats.get("retries_rate_limit", 0)),
        "model": meta.get("configuration", {}).get("model"),
        "thinking_level": meta.get("configuration", {}).get("thinking_level"),
        "temperature": meta.get("configuration", {}).get("temperature"),
        "instruction_hash": meta.get("configuration", {}).get(
            "system_instruction_hash"
        ),
        "service_tier_requested": "flex",
        "service_tier_recorded_in_meta": None,
        "cost_basis_in_meta": meta.get("cost_estimate", {}).get("cost_basis"),
        "discount_in_meta": meta.get("cost_estimate", {})
        .get("pricing_used", {})
        .get("discount"),
        "wall_seconds": round(time.time() - started, 1),
        **cost,
    }
    ledger["rungs"][key] = entry
    save_ledger(ledger)

    logger.info(
        "row %d done: %d calls, %d failed, US$%.4f flex "
        "(US$%.4f list recorded), %.0f s",
        rung["row"],
        entry["items_processed"],
        entry["items_failed"],
        entry["flex_usd"],
        entry["list_usd_recorded"],
        entry["wall_seconds"],
    )
    return entry


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Run the carried Gemini 3 verifier over the K-ladder Phase 2 "
            "unions (tiers A-D, US$24.84 approved, hard stop US$30)"
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--tier", action="append", choices=["A", "B", "C", "D"],
        help="Restrict to one or more tiers (default: all)",
    )
    parser.add_argument(
        "--row", action="append", type=int,
        help="Restrict to one or more costing-table row numbers",
    )
    parser.add_argument(
        "--workers", type=int, default=20,
        help="Real-time concurrency (default: 20, the project precedent in "
             "scripts/run_verifier_stage_refresh.sh). Never set in a YAML",
    )
    parser.add_argument(
        "--plan-only", action="store_true",
        help="Print what would run and what it would cost; call no API",
    )
    parser.add_argument(
        "--recompute-ledger", action="store_true",
        help="Rebuild the ledger from committed run.meta.json files only",
    )
    parser.add_argument(
        "--skip-done", action="store_true", default=True,
        help="Skip rungs already in the ledger (default: on)",
    )
    parser.add_argument(
        "--redo", dest="skip_done", action="store_false",
        help="Re-run rungs already in the ledger (spends again)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    with open(UNIONS_JSON) as handle:
        rungs = json.load(handle)["rungs"]

    rungs = [rung for rung in rungs if rung["verdict"] == "OK"]
    if args.tier:
        rungs = [rung for rung in rungs if rung["tier"] in set(args.tier)]
    if args.row:
        rungs = [rung for rung in rungs if rung["row"] in set(args.row)]
    rungs.sort(key=lambda rung: ("ABCD".index(rung["tier"]), rung["row"]))

    ledger = load_ledger()

    if args.recompute_ledger:
        rebuilt = {
            "created_at_utc": ledger["created_at_utc"],
            "basis": ledger["basis"],
            "hard_stop_usd": HARD_STOP_USD,
            "approved_usd": 24.84,
            "rungs": {},
        }
        for rung in rungs:
            paths = resolve_paths(rung)
            meta_path = BASE_DIR / paths["verify_dir"] / "run.meta.json"
            if not meta_path.exists():
                continue
            key = f"row{rung['row']:02d}-{paths['verifier_stage']}"
            previous = ledger["rungs"].get(key, {})
            with open(meta_path) as handle:
                meta = json.load(handle)
            entry = dict(previous)
            entry.update(
                row=rung["row"],
                tier=rung["tier"],
                family=rung["family"],
                n_passes=rung["n_passes"],
                candidates=rung["measured_candidates"],
                verifier_stage=paths["verifier_stage"],
                verify_dir=paths["verify_dir"],
                **audited_flex_usd(meta),
            )
            entry.setdefault("wall_seconds", 0.0)
            entry.setdefault("items_processed", 0)
            rebuilt["rungs"][key] = entry
        save_ledger(rebuilt)
        logger.info(
            "Ledger rebuilt from %d metas: US$%.4f flex",
            len(rebuilt["rungs"]),
            rebuilt["total"]["flex_usd"],
        )
        return

    spent = sum(entry["flex_usd"] for entry in ledger["rungs"].values())
    planned = sum(rung["usd_estimate"] for rung in rungs)
    logger.info(
        "%d rung(s) selected; US$%.2f estimated; US$%.4f already spent "
        "(hard stop US$%.2f)",
        len(rungs),
        planned,
        spent,
        HARD_STOP_USD,
    )

    if args.plan_only:
        for rung in rungs:
            paths = resolve_paths(rung)
            logger.info(
                "  row %2d tier %s  %-40s K=%d  %5d cand  ~US$%.2f  -> %s",
                rung["row"],
                rung["tier"],
                rung["family"],
                rung["n_passes"],
                rung["measured_candidates"],
                rung["usd_estimate"],
                paths["verify_dir"],
            )
        return

    done = 0
    for rung in rungs:
        paths = resolve_paths(rung)
        key = f"row{rung['row']:02d}-{paths['verifier_stage']}"
        if args.skip_done and key in ledger["rungs"]:
            logger.info("row %d already in the ledger — skipping", rung["row"])
            continue
        if spent >= HARD_STOP_USD:
            logger.error(
                "HARD STOP: US$%.4f spent, ceiling US$%.2f. "
                "Not starting row %d. Report and get a new approval.",
                spent,
                HARD_STOP_USD,
                rung["row"],
            )
            sys.exit(3)
        entry = verify_rung(rung, workers=args.workers, ledger=ledger)
        if entry is None:
            logger.error(
                "row %d failed; stopping so the failure is reported rather "
                "than spent past. A re-run of a failed union is NOT approved.",
                rung["row"],
            )
            sys.exit(4)
        spent += entry["flex_usd"]
        done += 1
        logger.info(
            "running total: US$%.4f flex over %d rung(s)", spent, len(ledger["rungs"])
        )

    logger.info(
        "Finished %d rung(s) this invocation; ledger total US$%.4f flex "
        "over %d rung(s) -> %s",
        done,
        ledger["total"]["flex_usd"],
        ledger["total"]["rungs"],
        LEDGER_JSON.relative_to(BASE_DIR),
    )


if __name__ == "__main__":
    main()
