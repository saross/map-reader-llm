#!/usr/bin/env python3
"""
K-ladder tier E: verify the grid 384 px / 50 % MINIMAL text K = 1, 3, 5 rungs
============================================================================

Description:
    Tier E of the K-ladder review, approved by the Principal Investigator (PI)
    on the evening of 2026-09-12 as the ONLY API spend permitted in the
    closeout job. It completes the one remaining verified B-geometry MINIMAL
    text ladder the corpus can have: the grid study's 384 px / 50 % overlap
    pool already holds a verified K = 10 cell (the committed
    ``grid-postverifier-2026-08-18`` 384/50 cell), and this tier buys its
    K = 1, K = 3 and K = 5 siblings.

    The gate this script may spend under, and nothing wider (ruling R1: the
    carried Gemini 3 verifier at every rung, no swapping):

    ============  ==================================================
    pool          ``outputs/grid-2026-08-18/g384_ov192`` runs 1-10
    model         ``gemini-3-flash`` (resolves to
                  ``gemini-3-flash-preview``)
    config        ``prompts/configs/verify_adversarial-text.json``
    temperature   0.0 (from the config; never overridden)
    thinking      MINIMAL (from the config; never overridden)
    iterations    1
    tier          real-time **flex**
    budget        US$5.02 at the audited US$0.000693 per candidate,
                  **hard stop at US$7.00**
    ============  ==================================================

    **The union-count STOP.** The PI's approval names the expected candidate
    count of each rung (1,826 / 2,481 / 2,932). A measured count more than
    :data:`TOLERANCE_FRACTION` away from its expected figure is a STOP for
    that rung: the rung is not verified, and the mismatch is reported.

    **The flex correction.** ``scripts/run_pv.py`` passes ``--service-tier``
    to the API but stamps nothing about it into ``run.meta.json`` — the meta
    records ``cost_basis: "list"`` with ``discount: 1.0`` even under flex
    (``reports/k-ladder-phase2-deltas-2026-09-12.md`` section 1). So the
    audited figure is recomputed here from the meta's own token counts, on the
    basis the whole corpus uses, by reusing Phase 2's
    :func:`~scripts.run_k_ladder_phase2_verifier.audited_flex_usd`.

    **One construction asymmetry, recorded rather than hidden.** The three
    rungs this script builds are ``merge_passes.py`` unions over the pool's
    native footprint. The committed K = 10 rung's union
    (``outputs/grid-2026-08-18/verifier/g384_ov192/union_k10.geojson``, 3,319
    candidates) was built by ``scripts/materialise_grid_unions.py``, which
    additionally filters to the grid study's common 487-tile carrier footprint
    (``scripts/grid_analysis.as_gdf`` drops points with no primary carrier
    tile). A ``merge_passes`` K = 10 union of the same ten passes holds 3,591
    candidates, of which 3,325 survive that filter. The K = 1/3/5 rungs are
    therefore verified over a slightly wider candidate universe than their
    K = 10 sibling. Scoring every rung on the board frame normalises the
    comparison at scoring time, but the difference is real and is reported in
    the pre-launch audit and the findings document.

Usage::

    # Step 1, US$0: build the three unions and gate their counts
    python scripts/run_k_ladder_tier_e.py unions

    # Step 2, US$0: what would run and what it would cost
    python scripts/run_k_ladder_tier_e.py verify --plan-only

    # Step 3, a few cents: the five-candidate smoke run
    python scripts/run_k_ladder_tier_e.py smoke

    # Step 4, the three rungs
    python scripts/run_k_ladder_tier_e.py verify --workers 20

    # Step 5, US$0: sweep, materialise, and write the evaluation jobs file
    python scripts/run_k_ladder_tier_e.py prepare
    xargs -P 6 -I CMD bash -c CMD \
        < results/k-ladder-2026-09-12/tier-e/score-jobs.txt
    python scripts/run_k_ladder_tier_e.py collect

    # Any time, US$0: rebuild the ledger from the committed metas
    python scripts/run_k_ladder_tier_e.py verify --recompute-ledger

Outputs:
    outputs/grid-2026-08-18/g384_ov192/consensus-n{1,3,5}/
    outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder/k{1,3,5}/
    results/k-ladder-2026-09-12/tier-e/{unions,spend-ledger,operating-points,
        scores}.json
    results/k-ladder-2026-09-12/tier-e/cells/<cell>/evaluation.json

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
sys.path.insert(0, str(BASE_DIR))

from scripts.run_k_ladder_phase2_verifier import (  # noqa: E402
    PADDING_PX,
    VERIFIER_CONFIG,
    audited_flex_usd,
)
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

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

# --- Fixed inputs -----------------------------------------------------------

TIER_E_DIR = BASE_DIR / "results" / "k-ladder-2026-09-12" / "tier-e"
UNIONS_JSON = TIER_E_DIR / "unions.json"
LEDGER_JSON = TIER_E_DIR / "spend-ledger.json"
POINTS_JSON = TIER_E_DIR / "operating-points.json"
SCORES_JSON = TIER_E_DIR / "scores.json"
JOBS_FILE = TIER_E_DIR / "score-jobs.txt"
CELLS_DIR = TIER_E_DIR / "cells"
MATERIALISED_DIR = TIER_E_DIR / "materialised"
SMOKE_DIR = TIER_E_DIR / "smoke"

#: The proposer pool, and the tile set its crops come from (the committed
#: K = 10 crops manifest records ``inputs/tiles_384_ov192``).
POOL_DIR = "outputs/grid-2026-08-18/g384_ov192"
TILES_DIR = "inputs/tiles_384_ov192"

#: Where the verifier stages land, per the PI's brief.
VERIFY_ROOT = "outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder"

#: The register run and pool slug the new rungs join, read from the committed
#: grid conditions in ``results/run-conditions.json`` (run ``grid-2026-08-18``,
#: ``proposer_pool: "brief-text"``).
RUN_ID = "grid-2026-08-18"
POOL_SLUG = "brief-text"
LABEL_STEM = "g384-ov192"

#: The carried probability threshold of the committed grid cells
#: (``g384-ov192-k10-verified-p0.15-k10``), so the ladder stays a ladder.
CARRIED_PROB = 0.15

#: The PI's approved per-rung candidate counts. A measured count further than
#: TOLERANCE_FRACTION from these is a STOP for that rung.
EXPECTED_CANDIDATES: dict[int, int] = {1: 1826, 3: 2481, 5: 2932}
TOLERANCE_FRACTION = 0.02

#: Audited Gemini 3 verifier rate, USD per candidate
#: (``reports/token-load-audit-2026-06-12.md`` section 5, ``VF_CALL_USD``).
USD_PER_CANDIDATE = 0.000693

#: Approved budget and the hard stop the PI set above it.
APPROVED_USD = 5.02
HARD_STOP_USD = 7.00

#: The committed K = 10 sibling, for the record in the unions file.
COMMITTED_K10 = {
    "union": "outputs/grid-2026-08-18/verifier/g384_ov192/union_k10.geojson",
    "candidates": 3319,
    "builder": "scripts/materialise_grid_unions.py",
    "footprint": "grid common 487-tile carrier (tile-filtered)",
    "merge_passes_equivalent": 3591,
    "merge_passes_on_carrier": 3325,
}


def rungs() -> list[dict[str, Any]]:
    """Return the three tier-E rungs in ascending K order.

    Returns:
        One dict per rung, shaped like a Phase 2 ``unions.json`` rung so the
        Phase 2 helpers can be reused unchanged.
    """
    out: list[dict[str, Any]] = []
    for row, n_passes in enumerate(sorted(EXPECTED_CANDIDATES), start=1):
        out.append(
            {
                "row": row,
                "tier": "E",
                "family": "Gemini 3 MINIMAL text 384 px / 50 %, grid pool",
                "run_id": RUN_ID,
                "pool_slug": POOL_SLUG,
                "label_stem": LABEL_STEM,
                "modality": "text",
                "pool_dir": POOL_DIR,
                "n_passes": n_passes,
                "pass_list": ",".join(
                    str(index) for index in range(1, n_passes + 1)
                ),
                "expected_candidates": EXPECTED_CANDIDATES[n_passes],
                "consensus_dir": f"{POOL_DIR}/consensus-n{n_passes}",
                "verify_dir": f"{VERIFY_ROOT}/k{n_passes}",
                "crops_dir": f"{VERIFY_ROOT}/k{n_passes}/crops",
                "tiles_dir": TILES_DIR,
                "verifier_stage": (
                    f"g384_ov192-k-ladder-k{n_passes}-verify"
                ),
            }
        )
    return out


def ledger_key(rung: dict[str, Any]) -> str:
    """The ledger key for one rung."""
    return f"row{rung['row']:02d}-{rung['verifier_stage']}"


# --- Step 1: the unions -----------------------------------------------------


def build_union(rung: dict[str, Any], *, check_only: bool) -> dict[str, Any]:
    """Build (or re-check) one rung's first-N consensus union.

    Args:
        rung: One entry of :func:`rungs`.
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
            "row %d  K=%d  building union from passes %s",
            rung["row"],
            rung["n_passes"],
            rung["pass_list"],
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
            sys.exit(1)

    with open(union_path) as handle:
        measured = len(json.load(handle).get("features", []))

    expected = rung["expected_candidates"]
    delta = measured - expected
    fraction = abs(delta) / expected if expected else 0.0
    verdict = "OK" if fraction <= TOLERANCE_FRACTION else "STOP"

    out = dict(rung)
    out.update(
        measured_candidates=measured,
        delta=delta,
        delta_fraction=round(fraction, 6),
        verdict=verdict,
        usd_estimate=round(measured * USD_PER_CANDIDATE, 4),
    )
    logger.info(
        "row %d  K=%d  union %d (expected %d, delta %+d, %.3f %%)  %s",
        rung["row"],
        rung["n_passes"],
        measured,
        expected,
        delta,
        fraction * 100.0,
        verdict,
    )
    return out


def write_intent(rung: dict[str, Any]) -> None:
    """Write the rung's ``experiment_intent.md`` beside its union."""
    path = BASE_DIR / rung["consensus_dir"] / "experiment_intent.md"
    today = datetime.now(timezone.utc).date().isoformat()
    body = f"""# Experiment intent — tier E K = {rung['n_passes']} union

> **Last revised**: {today} (original publication — built by
> `scripts/run_k_ladder_tier_e.py unions`). See [§ Changelog](#changelog).

**What this directory is.** The first-{rung['n_passes']} sub-pool consensus
union of the grid study's 384 px / 50 % overlap MINIMAL text pool, built for
tier E of the K-ladder review (`planning/k-ladder-review-2026-09-11.md`,
rulings R1 and R2).

| field | value |
|---|---|
| pool | `{rung['pool_dir']}` |
| passes | `{rung['pass_list']}` (runs 1–{rung['n_passes']}) |
| `merge_passes.py --passes` | `{rung['pass_list']}` |
| K | {rung['n_passes']} |
| expected candidates (PI's approval) | {rung['expected_candidates']:,} |
| measured candidates (vote ≥ 1) | {rung['measured_candidates']:,} |
| delta | {rung['delta']:+d} ({rung['delta_fraction'] * 100:.3f} %) |
| verdict | **{rung['verdict']}** |
| planned verifier stage | `{rung['verifier_stage']}` |
| verifier output | `{rung['verify_dir']}` |

**How it was built.**

```bash
python scripts/merge_passes.py \\
    --input-dir {rung['pool_dir']} \\
    --output-dir {rung['consensus_dir']} \\
    --sweep \\
    --passes {rung['pass_list']}
```

`merge_passes.py` deduplicates within each pass at 20 m, clusters across
passes at 20 m, and records each cluster's MEAN centroid, so a first-N union
is **not** a positional prefix or a coordinate subset of a longer union. The
pass filter selects directories by the integer after `run_`, so the pool's
`run_4_recovery`, `run_8_recovery` and `run_10_recovery` directories are
skipped (`int("4_recovery")` raises and the directory is passed over) —
verified rather than assumed. The union's own `voting_summary.json` carries a
machine-readable `pass_provenance` block with a `git_blob_hash` per
contributing pass file.

**The K = 10 sibling is built differently, and that is recorded here.** The
committed K = 10 rung of this family is
`{COMMITTED_K10['union']}`
({COMMITTED_K10['candidates']:,} candidates), built by
`{COMMITTED_K10['builder']}`, which filters the union to the grid study's
common 487-tile carrier footprint. A `merge_passes` union of the same ten
passes holds {COMMITTED_K10['merge_passes_equivalent']:,} candidates, of which
{COMMITTED_K10['merge_passes_on_carrier']:,} survive that filter. This rung is
therefore built on the pool's native footprint, as the PI's expected counts
require, and the difference is reported in
`results/k-ladder-2026-09-12/tier-e/pre_launch_audit.md`.

## Changelog

### {today} — Original publication

Built as step 1 of tier E, at US$0. No API call was made by this step.
"""
    path.write_text(body)


def cmd_unions(args: argparse.Namespace) -> None:
    """Build the three unions and gate their candidate counts."""
    built = [build_union(rung, check_only=args.check_only) for rung in rungs()]
    for rung in built:
        write_intent(rung)

    stops = [rung for rung in built if rung["verdict"] == "STOP"]
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "tier": "E",
        "card": "planning/k-ladder-review-2026-09-11.md",
        "approved_usd": APPROVED_USD,
        "hard_stop_usd": HARD_STOP_USD,
        "usd_per_candidate": USD_PER_CANDIDATE,
        "tolerance_fraction": TOLERANCE_FRACTION,
        "committed_k10_sibling": COMMITTED_K10,
        "n_rungs": len(built),
        "n_stop": len(stops),
        "total_candidates": sum(r["measured_candidates"] for r in built),
        "total_usd_estimate": round(
            sum(r["usd_estimate"] for r in built), 4
        ),
        "rungs": built,
    }
    UNIONS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(UNIONS_JSON, "w") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    logger.info(
        "%d rung(s), %d candidates, US$%.4f estimated, %d STOP -> %s",
        summary["n_rungs"],
        summary["total_candidates"],
        summary["total_usd_estimate"],
        summary["n_stop"],
        UNIONS_JSON.relative_to(BASE_DIR),
    )


# --- Step 2-4: the verifier -------------------------------------------------


def load_ledger() -> dict[str, Any]:
    """Read the spend ledger, or start a fresh one."""
    if LEDGER_JSON.exists():
        with open(LEDGER_JSON) as handle:
            return json.load(handle)
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "tier": "E",
        "basis": (
            "flex: input x 0.25 + (output + thinking) x 1.50 per million USD, "
            "recomputed from run.meta.json token counts because the verify "
            "path stamps cost_basis 'list' with discount 1.0 under flex"
        ),
        "hard_stop_usd": HARD_STOP_USD,
        "approved_usd": APPROVED_USD,
        "rungs": {},
    }


def save_ledger(ledger: dict[str, Any]) -> None:
    """Write the spend ledger, refreshing its derived total."""
    entries = list(ledger["rungs"].values())
    ledger["updated_at_utc"] = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )
    candidates = sum(entry["candidates"] for entry in entries)
    flex = sum(entry["flex_usd"] for entry in entries)
    ledger["total"] = {
        "rungs": len(entries),
        "candidates": candidates,
        "candidates_verified": sum(
            entry.get("candidates_verified", 0) for entry in entries
        ),
        "calls": sum(
            entry.get("api_requests") or entry["items_processed"]
            for entry in entries
        ),
        "retries_total": sum(
            entry.get("retries_total", 0) for entry in entries
        ),
        "flex_usd": round(flex, 4),
        "list_usd_recorded": round(
            sum(entry["list_usd_recorded"] for entry in entries), 4
        ),
        "flex_usd_per_candidate": (
            round(flex / candidates, 8) if candidates else None
        ),
        "wall_seconds": round(
            sum(entry["wall_seconds"] for entry in entries), 1
        ),
    }
    LEDGER_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_JSON, "w") as handle:
        json.dump(ledger, handle, indent=2)
        handle.write("\n")


def run_step(command: list[str], label: str) -> tuple[bool, str]:
    """Run one subprocess step, returning success and a tail of its output."""
    completed = subprocess.run(
        command, cwd=BASE_DIR, capture_output=True, text=True, check=False
    )
    tail = (completed.stdout[-1500:] + completed.stderr[-2500:]).strip()
    if completed.returncode != 0:
        logger.error(
            "%s FAILED (exit %d)\n%s", label, completed.returncode, tail
        )
        return False, tail
    return True, tail


def extract_crops(rung: dict[str, Any], *, crops_dir: str) -> dict[str, Any] | None:
    """Extract the rung's verifier crops from the source rasters.

    Args:
        rung: One rung of the unions file.
        crops_dir: Where the crops go, relative to the repository root.

    Returns:
        The crops manifest, or ``None`` if extraction or a gate failed.
    """
    union = f"{rung['consensus_dir']}/consensus_t1.geojson"
    ok, _ = run_step(
        [
            sys.executable,
            "scripts/run_pv.py",
            "extract",
            "--proposer",
            union,
            "--output-dir",
            crops_dir,
            "--padding",
            str(PADDING_PX),
            "--tiles-dir",
            rung["tiles_dir"],
        ],
        f"row{rung['row']} extract",
    )
    if not ok:
        return None

    with open(BASE_DIR / crops_dir / "candidate_manifest.json") as handle:
        manifest = json.load(handle)
    if manifest["successful_extractions"] != rung["measured_candidates"]:
        logger.error(
            "row %d: extracted %d crops for %d candidates — refusing to verify",
            rung["row"],
            manifest["successful_extractions"],
            rung["measured_candidates"],
        )
        return None
    if manifest["tile_fallback_crops"]:
        logger.error(
            "row %d: %d crops came from tile PNGs, not rasters (E33) — "
            "refusing to verify",
            rung["row"],
            manifest["tile_fallback_crops"],
        )
        return None
    return manifest


def verify_rung(
    rung: dict[str, Any], *, workers: int, ledger: dict[str, Any]
) -> dict[str, Any] | None:
    """Extract crops for one rung and run a single verifier pass over it."""
    key = ledger_key(rung)
    started = time.time()
    logger.info(
        "=== row %d  tier E  K=%d  (%d candidates, ~US$%.2f) ===",
        rung["row"],
        rung["n_passes"],
        rung["measured_candidates"],
        rung["usd_estimate"],
    )

    if extract_crops(rung, crops_dir=rung["crops_dir"]) is None:
        return None

    ok, _ = run_step(
        [
            sys.executable,
            "scripts/run_pv.py",
            "verify",
            "--crops-dir",
            rung["crops_dir"],
            "--verifier-config",
            str(VERIFIER_CONFIG.relative_to(BASE_DIR)),
            "--output-dir",
            rung["verify_dir"],
            "--mode",
            "realtime",
            "--workers",
            str(workers),
            "--service-tier",
            "flex",
        ],
        f"row{rung['row']} verify",
    )
    if not ok:
        return None

    with open(BASE_DIR / rung["verify_dir"] / "run.meta.json") as handle:
        meta = json.load(handle)
    cost = audited_flex_usd(meta)
    stats = meta.get("execution_stats", {})
    finish = stats.get("finish_reason_counts", {})
    calls = sum(int(value) for value in finish.values()) or int(
        meta.get("usage_stats", {})
        .get("by_provider", {})
        .get("google_gemini", {})
        .get("request_count", 0)
    )

    entry = {
        "row": rung["row"],
        "tier": "E",
        "family": rung["family"],
        "n_passes": rung["n_passes"],
        "run_id": rung["run_id"],
        "pool_slug": rung["pool_slug"],
        "verifier_stage": rung["verifier_stage"],
        "verify_dir": rung["verify_dir"],
        "crops_dir": rung["crops_dir"],
        "union": f"{rung['consensus_dir']}/consensus_t1.geojson",
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
        "row %d done: %d calls, %d failed, US$%.4f flex, %.0f s",
        rung["row"],
        entry["items_processed"],
        entry["items_failed"],
        entry["flex_usd"],
        entry["wall_seconds"],
    )
    return entry


def load_gated_rungs() -> list[dict[str, Any]]:
    """Read the unions file and return the rungs whose count gate passed."""
    if not UNIONS_JSON.exists():
        logger.error(
            "%s does not exist — run `unions` first",
            UNIONS_JSON.relative_to(BASE_DIR),
        )
        sys.exit(2)
    with open(UNIONS_JSON) as handle:
        data = json.load(handle)
    kept = [rung for rung in data["rungs"] if rung["verdict"] == "OK"]
    dropped = [rung for rung in data["rungs"] if rung["verdict"] != "OK"]
    for rung in dropped:
        logger.error(
            "row %d (K=%d) is a STOP: %d measured against %d expected "
            "(%.3f %%) — not verifying it",
            rung["row"],
            rung["n_passes"],
            rung["measured_candidates"],
            rung["expected_candidates"],
            rung["delta_fraction"] * 100.0,
        )
    return kept


def cmd_smoke(args: argparse.Namespace) -> None:
    """Verify five candidates of the K = 1 union, as the pre-spend smoke test."""
    rung = load_gated_rungs()[0]
    smoke_crops = f"{SMOKE_DIR.relative_to(BASE_DIR)}/crops"
    smoke_verify = f"{SMOKE_DIR.relative_to(BASE_DIR)}/verify"
    SMOKE_DIR.mkdir(parents=True, exist_ok=True)

    # A five-feature slice of the union, so the smoke run cannot spend more
    # than five candidates' worth whatever else goes wrong.
    union_path = BASE_DIR / rung["consensus_dir"] / "consensus_t1.geojson"
    with open(union_path) as handle:
        union = json.load(handle)
    union["features"] = union["features"][:5]
    slice_path = SMOKE_DIR / "union_first5.geojson"
    with open(slice_path, "w") as handle:
        json.dump(union, handle)

    ok, _ = run_step(
        [
            sys.executable,
            "scripts/run_pv.py",
            "extract",
            "--proposer",
            str(slice_path.relative_to(BASE_DIR)),
            "--output-dir",
            smoke_crops,
            "--padding",
            str(PADDING_PX),
            "--tiles-dir",
            rung["tiles_dir"],
        ],
        "smoke extract",
    )
    if not ok:
        sys.exit(3)

    with open(BASE_DIR / smoke_crops / "candidate_manifest.json") as handle:
        manifest = json.load(handle)
    logger.info(
        "smoke crops: %d extracted, %d raster, %d tile-fallback",
        manifest["successful_extractions"],
        manifest["raster_crops"],
        manifest["tile_fallback_crops"],
    )
    if manifest["tile_fallback_crops"]:
        logger.error("smoke: tile-fallback crops present (E33) — stopping")
        sys.exit(3)
    if args.plan_only:
        logger.info("plan-only: not calling the API")
        return

    ok, _ = run_step(
        [
            sys.executable,
            "scripts/run_pv.py",
            "verify",
            "--crops-dir",
            smoke_crops,
            "--verifier-config",
            str(VERIFIER_CONFIG.relative_to(BASE_DIR)),
            "--output-dir",
            smoke_verify,
            "--mode",
            "realtime",
            "--workers",
            "5",
            "--service-tier",
            "flex",
        ],
        "smoke verify",
    )
    if not ok:
        sys.exit(3)

    with open(BASE_DIR / smoke_verify / "run.meta.json") as handle:
        meta = json.load(handle)
    with open(BASE_DIR / smoke_verify / "probabilities.json") as handle:
        probabilities = json.load(handle)
    cost = audited_flex_usd(meta)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "candidates": len(union["features"]),
        # `probabilities.json` is an envelope, so the per-candidate count is
        # its `total_results`, not the number of its top-level keys.
        "probabilities_returned": probabilities.get(
            "total_results", len(probabilities.get("results", []))
        ),
        "model": meta.get("configuration", {}).get("model"),
        "thinking_level": meta.get("configuration", {}).get("thinking_level"),
        "temperature": meta.get("configuration", {}).get("temperature"),
        "instruction_hash": meta.get("configuration", {}).get(
            "system_instruction_hash"
        ),
        "flex_usd": cost["flex_usd"],
        "list_usd_recorded": cost["list_usd_recorded"],
        "cost_basis_in_meta": meta.get("cost_estimate", {}).get("cost_basis"),
    }
    with open(SMOKE_DIR / "smoke.json", "w") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    logger.info("smoke: %s", json.dumps(report, indent=2))


def cmd_verify(args: argparse.Namespace) -> None:
    """Run the carried verifier over each gated rung, under the hard stop."""
    selected = load_gated_rungs()
    if args.row:
        selected = [
            rung for rung in selected if rung["row"] in set(args.row)
        ]
    ledger = load_ledger()

    if args.recompute_ledger:
        rebuilt = {
            "created_at_utc": ledger["created_at_utc"],
            "tier": "E",
            "basis": ledger["basis"],
            "hard_stop_usd": HARD_STOP_USD,
            "approved_usd": APPROVED_USD,
            "rungs": {},
        }
        for rung in selected:
            meta_path = BASE_DIR / rung["verify_dir"] / "run.meta.json"
            if not meta_path.exists():
                continue
            key = ledger_key(rung)
            entry = dict(ledger["rungs"].get(key, {}))
            with open(meta_path) as handle:
                meta = json.load(handle)
            entry.update(
                row=rung["row"],
                tier="E",
                family=rung["family"],
                n_passes=rung["n_passes"],
                candidates=rung["measured_candidates"],
                verifier_stage=rung["verifier_stage"],
                verify_dir=rung["verify_dir"],
                **audited_flex_usd(meta),
            )
            entry.setdefault("wall_seconds", 0.0)
            entry.setdefault("items_processed", 0)
            rebuilt["rungs"][key] = entry
        save_ledger(rebuilt)
        logger.info(
            "Ledger rebuilt from %d meta(s): US$%.4f flex",
            len(rebuilt["rungs"]),
            rebuilt["total"]["flex_usd"],
        )
        return

    spent = sum(entry["flex_usd"] for entry in ledger["rungs"].values())
    planned = sum(rung["usd_estimate"] for rung in selected)
    logger.info(
        "%d rung(s) selected; US$%.2f estimated; US$%.4f already spent "
        "(approved US$%.2f, hard stop US$%.2f)",
        len(selected),
        planned,
        spent,
        APPROVED_USD,
        HARD_STOP_USD,
    )
    if args.plan_only:
        for rung in selected:
            logger.info(
                "  row %d  K=%-2d  %5d cand  ~US$%.2f  -> %s",
                rung["row"],
                rung["n_passes"],
                rung["measured_candidates"],
                rung["usd_estimate"],
                rung["verify_dir"],
            )
        return

    for rung in selected:
        key = ledger_key(rung)
        if args.skip_done and key in ledger["rungs"]:
            logger.info("row %d already in the ledger — skipping", rung["row"])
            continue
        if spent >= HARD_STOP_USD:
            logger.error(
                "HARD STOP: US$%.4f spent, ceiling US$%.2f. Not starting "
                "row %d. Report and get a new approval.",
                spent,
                HARD_STOP_USD,
                rung["row"],
            )
            sys.exit(3)
        entry = verify_rung(rung, workers=args.workers, ledger=ledger)
        if entry is None:
            logger.error(
                "row %d failed; stopping so the failure is reported rather "
                "than spent past.",
                rung["row"],
            )
            sys.exit(4)
        spent += entry["flex_usd"]
        logger.info("running total: US$%.4f flex", spent)

    logger.info(
        "ledger total US$%.4f flex over %d rung(s) -> %s",
        ledger["total"]["flex_usd"],
        ledger["total"]["rungs"],
        LEDGER_JSON.relative_to(BASE_DIR),
    )


# --- Step 5: sweep, materialise, score --------------------------------------


def condition_labels(rung: dict[str, Any]) -> dict[str, str]:
    """Return the ``-opmax`` and carried condition labels for one rung.

    The grid family's committed convention is
    ``g384-ov192-k10-verified-p0.15-k10`` (run ``grid-2026-08-18``), so the
    new rungs take ``g384-ov192-k<K>-verified-opmax`` for the sweep-optimal
    point and ``g384-ov192-k<K>-verified-p0.15-k<K>`` for the carried one.
    """
    k = rung["n_passes"]
    return {
        "opmax": f"{LABEL_STEM}-k{k}-verified-opmax",
        "carried": f"{LABEL_STEM}-k{k}-verified-p{CARRIED_PROB:.2f}-k{k}",
    }


def run_sweep(rung: dict[str, Any], *, bounds: str, out_name: str) -> Path:
    """Run ``sweep_f1_greedy_pv.py`` for one rung on one frame."""
    output = BASE_DIR / rung["verify_dir"] / out_name
    command = [
        sys.executable,
        "scripts/sweep_f1_greedy_pv.py",
        "--config",
        f"{POOL_SLUG}-g384-ov192-k{rung['n_passes']}",
        "--crops-dir",
        rung["crops_dir"],
        "--verified-dir",
        rung["verify_dir"],
        "--output",
        str(output.relative_to(BASE_DIR)),
        "--bounds",
        bounds,
        "--buffer-m",
        *[str(buffer) for buffer in SWEEP_BUFFERS],
    ]
    completed = subprocess.run(
        command, cwd=BASE_DIR, capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        logger.error(
            "sweep failed for row %d on %s:\n%s",
            rung["row"],
            bounds,
            completed.stderr[-2000:],
        )
        sys.exit(5)
    return output


def materialise(
    rung: dict[str, Any], *, vote_t: int, prob_t: float, output: Path
) -> int:
    """Materialise one operating point's detections, returning its count."""
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "scripts/materialise_pv_geojson.py",
        "--consensus",
        f"{rung['consensus_dir']}/consensus_t1.geojson",
        "--probabilities",
        f"{rung['verify_dir']}/probabilities.json",
        "--vote-t",
        str(vote_t),
        "--prob-t",
        str(prob_t),
        "--output",
        str(output.relative_to(BASE_DIR)),
    ]
    completed = subprocess.run(
        command, cwd=BASE_DIR, capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        logger.error(
            "materialise failed for row %d at (%s, %s):\n%s",
            rung["row"],
            vote_t,
            prob_t,
            completed.stderr[-2000:],
        )
        sys.exit(6)
    with open(output) as handle:
        return len(json.load(handle).get("features", []))


def eval_command(detections: Path, cell: str, label: str) -> str:
    """Build the board-frame evaluation command line for one cell."""
    return " ".join(
        [
            "python",
            "scripts/evaluate_detections.py",
            "--detections",
            str(detections.relative_to(BASE_DIR)),
            "--ground-truth",
            GROUND_TRUTH,
            "--bounds",
            BOARD_BOUNDS,
            "--buffers",
            *[str(buffer) for buffer in BUFFERS],
            "--bootstrap",
            str(BOOTSTRAP),
            "--seed",
            str(SEED),
            "--mcc",
            "--output-dir",
            f"{CELLS_DIR.relative_to(BASE_DIR)}/{cell}",
            "--label",
            label,
        ]
    )


def cmd_prepare(args: argparse.Namespace) -> None:
    """Sweep both frames, choose operating points, materialise, write jobs."""
    selected = [
        rung
        for rung in load_gated_rungs()
        if (BASE_DIR / rung["verify_dir"] / "probabilities.json").exists()
    ]
    if not selected:
        logger.error("no rung has a probabilities.json yet")
        sys.exit(7)

    points: list[dict[str, Any]] = []
    jobs: list[str] = []
    for rung in selected:
        board = argmax_at_headline(
            run_sweep(rung, bounds=BOARD_BOUNDS, out_name="sweep_board.json")
        )
        era2 = argmax_at_headline(
            run_sweep(rung, bounds=ERA2_BOUNDS, out_name="sweep_era2.json")
        )
        labels = condition_labels(rung)
        k = rung["n_passes"]
        carried = {"vote_t": k, "prob_t": CARRIED_PROB}
        same = (
            board["vote_t"] == carried["vote_t"]
            and abs(board["prob_t"] - carried["prob_t"]) < 1e-9
        )

        entry: dict[str, Any] = {
            "row": rung["row"],
            "K": k,
            "family": rung["family"],
            "run_id": rung["run_id"],
            "consensus_dir": rung["consensus_dir"],
            "verify_dir": rung["verify_dir"],
            "candidates": rung["measured_candidates"],
            "opmax": {
                "vote_t": board["vote_t"],
                "prob_t": board["prob_t"],
                "sweep_f1_20": board["f1"],
                "n_ties": board["n_ties"],
                "label": labels["opmax"],
            },
            "era2_frame_argmax": {
                "vote_t": era2["vote_t"],
                "prob_t": era2["prob_t"],
                "sweep_f1_20": era2["f1"],
            },
            "frames_agree": (
                era2["vote_t"] == board["vote_t"]
                and abs(era2["prob_t"] - board["prob_t"]) < 1e-9
            ),
            "carried": {**carried, "label": labels["carried"]},
            "carried_is_opmax": same,
        }

        for basis in ("opmax", "carried"):
            if basis == "carried" and same:
                entry["carried"]["detections"] = entry["opmax"]["detections"]
                entry["carried"]["n_detections"] = entry["opmax"][
                    "n_detections"
                ]
                entry["carried"]["cell"] = entry["opmax"]["cell"]
                continue
            label = entry[basis]["label"]
            cell = cell_dir_name(rung["run_id"], label)
            detections = (
                MATERIALISED_DIR / f"{cell}" / "detections.geojson"
            )
            count = materialise(
                rung,
                vote_t=entry[basis]["vote_t"],
                prob_t=entry[basis]["prob_t"],
                output=detections,
            )
            entry[basis]["detections"] = str(
                detections.relative_to(BASE_DIR)
            )
            entry[basis]["n_detections"] = count
            entry[basis]["cell"] = cell
            jobs.append(eval_command(detections, cell, label))
            logger.info(
                "row %d %s: (k>=%d, p>=%.2f) -> %d detections, cell %s",
                rung["row"],
                basis,
                entry[basis]["vote_t"],
                entry[basis]["prob_t"],
                count,
                cell,
            )
        points.append(entry)

    POINTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(POINTS_JSON, "w") as handle:
        json.dump(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "board_bounds": BOARD_BOUNDS,
                "era2_bounds": ERA2_BOUNDS,
                "ground_truth": GROUND_TRUTH,
                "headline_buffer_m": HEADLINE_BUFFER,
                "carried_prob": CARRIED_PROB,
                "n_rungs": len(points),
                "n_cells": len({p[b]["cell"] for p in points
                                for b in ("opmax", "carried")}),
                "rungs": points,
            },
            handle,
            indent=2,
        )
        handle.write("\n")
    JOBS_FILE.write_text("\n".join(jobs) + "\n")
    logger.info(
        "%d evaluation job(s) -> %s",
        len(jobs),
        JOBS_FILE.relative_to(BASE_DIR),
    )


def cmd_collect(args: argparse.Namespace) -> None:
    """Read the finished evaluations back into a scores JSON."""
    with open(POINTS_JSON) as handle:
        points = json.load(handle)

    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for rung in points["rungs"]:
        row: dict[str, Any] = {
            "row": rung["row"],
            "K": rung["K"],
            "candidates": rung["candidates"],
            "frames_agree": rung["frames_agree"],
            "carried_is_opmax": rung["carried_is_opmax"],
        }
        for basis in ("opmax", "carried"):
            cell = rung[basis]["cell"]
            path = CELLS_DIR / cell / "evaluation.json"
            if not path.exists():
                missing.append(str(path.relative_to(BASE_DIR)))
                continue
            with open(path) as handle:
                evaluation = json.load(handle)
            summary = evaluation.get("summary", {})
            buffers = {
                int(entry["buffer_metres"]): entry
                for entry in summary.get("buffers", [])
            }
            headline = buffers.get(HEADLINE_BUFFER, {})
            tile = summary.get("tile_classification", {}) or {}
            mcc = tile.get("mcc")
            row[basis] = {
                "cell": cell,
                "label": rung[basis]["label"],
                "vote_t": rung[basis]["vote_t"],
                "prob_t": rung[basis]["prob_t"],
                "n_detections": rung[basis]["n_detections"],
                "f1_20": headline.get("f1"),
                "precision_20": headline.get("precision"),
                "recall_20": headline.get("recall"),
                "tile_mcc": (
                    mcc.get("point") if isinstance(mcc, dict) else mcc
                ),
                "tile_mcc_withheld": bool(tile.get("withheld")),
                "tile_mcc_withheld_reason": tile.get("withheld", {}).get(
                    "reason"
                )
                if isinstance(tile.get("withheld"), dict)
                else None,
                "eval_path": str(path.relative_to(BASE_DIR)),
            }
        rows.append(row)

    with open(LEDGER_JSON) as handle:
        ledger = json.load(handle)

    scores = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "tier": "E",
        "board_bounds": BOARD_BOUNDS,
        "ground_truth": GROUND_TRUTH,
        "headline_buffer_m": HEADLINE_BUFFER,
        "audited_flex_usd": ledger["total"]["flex_usd"],
        "n_missing_evaluations": len(missing),
        "missing_evaluations": missing,
        "rungs": rows,
    }
    with open(SCORES_JSON, "w") as handle:
        json.dump(scores, handle, indent=2)
        handle.write("\n")
    for row in rows:
        logger.info(
            "K=%-2d opmax F1@20 %.4f  MCC %s  | carried F1@20 %s",
            row["K"],
            row.get("opmax", {}).get("f1_20") or float("nan"),
            row.get("opmax", {}).get("tile_mcc"),
            row.get("carried", {}).get("f1_20"),
        )
    if missing:
        logger.warning("%d evaluation(s) missing", len(missing))
    logger.info("-> %s", SCORES_JSON.relative_to(BASE_DIR))


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "K-ladder tier E: the grid 384/50 MINIMAL text K = 1, 3, 5 rungs "
            "(US$5.02 approved, hard stop US$7.00)"
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_unions = subparsers.add_parser(
        "unions", help="Build the three first-N unions and gate their counts"
    )
    p_unions.add_argument(
        "--check-only",
        action="store_true",
        help="Read the committed unions without rebuilding them",
    )
    p_unions.set_defaults(func=cmd_unions)

    p_smoke = subparsers.add_parser(
        "smoke", help="Verify five candidates as the pre-spend smoke test"
    )
    p_smoke.add_argument(
        "--plan-only",
        action="store_true",
        help="Extract the crops but call no API",
    )
    p_smoke.set_defaults(func=cmd_smoke)

    p_verify = subparsers.add_parser(
        "verify", help="Run the carried verifier over each gated rung"
    )
    p_verify.add_argument(
        "--row", action="append", type=int, help="Restrict to one or more rows"
    )
    p_verify.add_argument(
        "--workers",
        type=int,
        default=20,
        help="Real-time concurrency (default: 20, the project precedent)",
    )
    p_verify.add_argument(
        "--plan-only",
        action="store_true",
        help="Print what would run and what it would cost; call no API",
    )
    p_verify.add_argument(
        "--recompute-ledger",
        action="store_true",
        help="Rebuild the ledger from committed run.meta.json files only",
    )
    p_verify.add_argument(
        "--skip-done", action="store_true", default=True,
        help="Skip rungs already in the ledger (default: on)",
    )
    p_verify.add_argument(
        "--redo", dest="skip_done", action="store_false",
        help="Re-run rungs already in the ledger (spends again)",
    )
    p_verify.set_defaults(func=cmd_verify)

    p_prepare = subparsers.add_parser(
        "prepare", help="Sweep, choose operating points, materialise, jobs"
    )
    p_prepare.set_defaults(func=cmd_prepare)

    p_collect = subparsers.add_parser(
        "collect", help="Read the finished evaluations into a scores JSON"
    )
    p_collect.set_defaults(func=cmd_collect)

    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    args.func(args)


if __name__ == "__main__":
    main()
