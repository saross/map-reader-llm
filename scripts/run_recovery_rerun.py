#!/usr/bin/env python3
"""
Execute the registered E71 dead-tile recovery rerun.

Drives `lib_batch_api.patch_failed_tiles()` over EXACTLY the passes and
tiles registered at `reports/verification/recovery-rerun-registration.md`
(worklists: `reports/verification/recovery-rerun-worklists.json`) —
deliberately NOT the study-file `--patch-tiles` path, whose tree-wide
rglob could sweep units outside the registered scope.

Safety properties:

1. **Worklist equality is enforced per pass**: the unit's `.tiles.json`
   `failed` list must equal the registered dead-tile set exactly, or the
   pass is skipped with an error (nothing outside the registration can
   be spent on).
2. **Pre-recovery artefacts are preserved** (archive, never delete;
   registration § 2): each unit's `.geojson` / `.meta.json` /
   `.tiles.json` are copied to
   `archive/pre-recovery-2026-07-30/<pass_id>/` before patching.
3. **Flex service tier** on every call (standing PI instruction
   2026-07-30) — passed explicitly, asserted non-None.
4. **Per-pass own model**: `patch_failed_tiles` reconstructs each call
   from the pass's own meta (model, temperature, thinking level,
   examples), so no mixed models are possible within a pass.

Dry run (no API):

    python scripts/run_recovery_rerun.py --dry-run

Live (requires GOOGLE_API_KEY in the environment; PI-gated):

    python scripts/run_recovery_rerun.py --workers 6

Results are written to
`reports/verification/recovery-rerun-results.json`.
"""

from __future__ import annotations

import argparse
import glob
import json
import logging
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPTS_DIR.parent))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = SCRIPTS_DIR.parent
WORKLISTS = REPO_ROOT / "reports/verification/recovery-rerun-worklists.json"
RESULTS = REPO_ROOT / "reports/verification/recovery-rerun-results.json"
ARCHIVE_DIR = REPO_ROOT / "archive/pre-recovery-2026-07-30"
TILES_384 = REPO_ROOT / "inputs/tiles_384"
SERVICE_TIER = "flex"


def unit_files(run_dir: Path) -> dict[str, list[Path]]:
    """The unit's geojson / meta / tiles files (may be multi-segment)."""
    all_geo = sorted(glob.glob(str(run_dir / "*.geojson")))
    return {
        "geojson": [Path(p) for p in all_geo
                    if ".meta" not in p and ".tiles" not in p],
        "meta": [Path(p) for p in sorted(glob.glob(str(run_dir / "*.meta.json")))],
        "tiles": [Path(p) for p in sorted(glob.glob(str(run_dir / "*.tiles.json")))],
    }


def sidecar_failed(spec: dict) -> set[str]:
    """Union of the unit's current sidecar ``failed`` lists."""
    run_dir = REPO_ROOT / spec["run_dir"]
    union_failed: set[str] = set()
    for t in unit_files(run_dir)["tiles"]:
        with open(t) as f:
            union_failed |= set(json.load(f).get("failed", []))
    return union_failed


def check_worklist_equality(spec: dict, residue: bool = False) -> tuple[bool, str]:
    """Scope gate against the registered dead set.

    Fresh mode: the sidecar failed set must EQUAL the registered set.
    Residue mode (after a prior sweep recovered part of the set): the
    current sidecar failures must be a SUBSET of the registered set —
    recovered tiles are legitimately absent, but nothing outside the
    registration may appear.
    """
    union_failed = sidecar_failed(spec)
    registered = set(spec["dead_tiles"])
    if residue:
        outside = union_failed - registered
        if outside:
            return False, (
                f"{len(outside)} sidecar failure(s) OUTSIDE the registered set: "
                f"{sorted(outside)[:3]}")
        return True, f"{len(union_failed)} residue of {len(registered)} registered"
    if union_failed != registered:
        return False, (
            f"sidecar failed set ({len(union_failed)}) != registered dead set "
            f"({len(registered)}); only-sidecar={sorted(union_failed - registered)[:3]} "
            f"only-registered={sorted(registered - union_failed)[:3]}")
    return True, f"{len(registered)} tiles"


def check_tiles_resolvable(spec: dict) -> list[str]:
    """Return registered dead tiles that do NOT resolve under tiles_384."""
    missing = []
    for name in spec["dead_tiles"]:
        if not list(TILES_384.rglob(name)):
            missing.append(name)
    return missing


def preserve_unit(spec: dict) -> Path:
    """Copy the unit's pre-recovery artefacts to the archive (idempotent)."""
    run_dir = REPO_ROOT / spec["run_dir"]
    dest = ARCHIVE_DIR / spec["pass_id"].replace("::", "__")
    dest.mkdir(parents=True, exist_ok=True)
    files = unit_files(run_dir)
    for group in files.values():
        for src in group:
            target = dest / src.name
            if not target.exists():
                shutil.copy2(src, target)
    return dest


def patch_unit(
    spec: dict,
    client,
    max_attempts: int | None = None,
    safe_tokens: int | None = None,
) -> dict:
    """Run the two-tier patcher on one unit at flex tier."""
    from scripts.lib_batch_api import patch_failed_tiles

    run_dir = REPO_ROOT / spec["run_dir"]
    kwargs: dict = {}
    if max_attempts is not None:
        kwargs["max_attempts"] = max_attempts
    if safe_tokens is not None:
        kwargs["max_output_tokens"] = safe_tokens
    result = patch_failed_tiles(
        unit_dir=run_dir,
        client=client,
        tiles_dir=TILES_384,
        service_tier=SERVICE_TIER,
        **kwargs,
    )
    return {
        "pass_id": spec["pass_id"],
        "n_registered": spec["n_dead"],
        "recovered": result["recovered"],
        "recovered_safe_mode": result["recovered_safe_mode"],
        "still_failed": result["still_failed"],
    }


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Execute the registered E71 dead-tile recovery rerun")
    parser.add_argument("--dry-run", action="store_true",
                        help="Verify worklists and tile resolution; no API calls")
    parser.add_argument("--workers", type=int, default=6,
                        help="Concurrent units (default 6; tiles within a unit "
                             "run sequentially)")
    parser.add_argument("--residue", action="store_true",
                        help="Residue mode (registered 2026-07-30 scope "
                             "extension): target the CURRENT sidecar failures, "
                             "gated as a subset of the registered dead set; "
                             "passes with no remaining failures are skipped")
    parser.add_argument("--max-attempts", type=int, default=None,
                        help="Override the patcher's per-tier attempt count "
                             "(default: lib_batch_api.MAX_SYNC_RETRIES = 3)")
    parser.add_argument("--safe-tokens", type=int, default=None,
                        help="Override the tier-2 safe-mode max_output_tokens "
                             "(default: 2048)")
    parser.add_argument("--results-suffix", type=str, default="",
                        help="Suffix for the results filename (e.g. '-deep')")
    args = parser.parse_args()

    with open(WORKLISTS) as f:
        worklists = json.load(f)
    passes = [p for p in worklists["passes"] if p["n_dead"] > 0]
    if args.residue:
        passes = [p for p in passes if sidecar_failed(p)]
        total = sum(len(sidecar_failed(p)) for p in passes)
        logger.info("Residue scope: %d tiles across %d passes (flex tier; "
                    "max_attempts=%s, safe_tokens=%s)",
                    total, len(passes), args.max_attempts, args.safe_tokens)
    else:
        total = sum(p["n_dead"] for p in passes)
        logger.info("Registered scope: %d tiles across %d passes (flex tier)",
                    total, len(passes))

    # ── Gate checks (always run, dry or live) ─────────────────
    failures = []
    for spec in passes:
        ok, msg = check_worklist_equality(spec, residue=args.residue)
        status = "ok" if ok else "MISMATCH"
        logger.info("  worklist %s: %s (%s)", status, spec["pass_id"], msg)
        if not ok:
            failures.append(spec["pass_id"])
        missing = check_tiles_resolvable(spec)
        if missing:
            logger.error("  UNRESOLVED tiles for %s: %s", spec["pass_id"], missing[:5])
            failures.append(spec["pass_id"])
    if failures:
        raise SystemExit(f"gate checks failed for: {sorted(set(failures))}")
    logger.info("All gate checks passed (%d passes)", len(passes))

    if args.dry_run:
        print(f"\n[DRY RUN] Would patch {total} tiles across {len(passes)} passes "
              f"at service tier '{SERVICE_TIER}'. No API calls made.")
        return

    # ── Live: preserve, then patch ────────────────────────────
    from google import genai

    from config import GOOGLE_API_KEY
    if not GOOGLE_API_KEY:
        raise SystemExit("GOOGLE_API_KEY not set")
    client = genai.Client(api_key=GOOGLE_API_KEY)

    for spec in passes:
        dest = preserve_unit(spec)
        logger.info("preserved pre-recovery artefacts: %s",
                    dest.relative_to(REPO_ROOT))

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(patch_unit, spec, client,
                        args.max_attempts, args.safe_tokens): spec
            for spec in passes
        }
        for fut in as_completed(futures):
            spec = futures[fut]
            try:
                r = fut.result()
            except Exception as e:  # noqa: BLE001 — record and continue
                logger.error("unit FAILED %s: %s", spec["pass_id"], e)
                r = {"pass_id": spec["pass_id"], "error": str(e)}
            results.append(r)
            if "error" not in r:
                logger.info(
                    "unit done %s: %d recovered + %d safe-mode, %d still failed",
                    r["pass_id"], len(r["recovered"]),
                    len(r["recovered_safe_mode"]), len(r["still_failed"]))

    summary = {
        "_README": (
            "Results of the registered E71 dead-tile recovery rerun "
            "(recovery-rerun-registration.md; PI approval 2026-07-30, flex tier). "
            "Pre-recovery artefacts preserved under archive/pre-recovery-2026-07-30/."),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "service_tier": SERVICE_TIER,
        "mode": "residue" if args.residue else "fresh",
        "max_attempts_override": args.max_attempts,
        "safe_tokens_override": args.safe_tokens,
        "registered_total": total,
        "results": sorted(results, key=lambda r: r["pass_id"]),
        "totals": {
            "recovered": sum(len(r.get("recovered", [])) for r in results),
            "recovered_safe_mode": sum(
                len(r.get("recovered_safe_mode", [])) for r in results),
            "still_failed": sum(len(r.get("still_failed", [])) for r in results),
            "unit_errors": sum(1 for r in results if "error" in r),
        },
    }
    results_path = (RESULTS.with_name(RESULTS.stem + args.results_suffix + ".json")
                    if args.results_suffix else RESULTS)
    with open(results_path, "w") as f:
        json.dump(summary, f, indent=1)
    t = summary["totals"]
    print("\n=== Recovery rerun complete ===")
    print(f"  recovered:  {t['recovered']} (original params) + "
          f"{t['recovered_safe_mode']} (safe mode)")
    print(f"  still failed: {t['still_failed']}  |  unit errors: {t['unit_errors']}")
    print(f"  results: {results_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
