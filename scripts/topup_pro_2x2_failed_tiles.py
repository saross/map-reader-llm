#!/usr/bin/env python3
"""
Top up the D64 Pro 2x2 replication's 15 batch-failed tiles (PI-approved).

Why this exists
---------------
The D64 same-day Gemini 3.1 Pro replication of h6 A-06's 2x2
(`outputs/pro-2x2-replication-2026-10-13/`, commit f53ae836b; ruling D64 in
`planning/pi-decisions-2026-09-20.md`) finished with 15 tiles failed as
``batch_api_error`` in three text HIGH passes: text-high-t0.7 run 3 (2),
text-high-t0.0 run 3 (3), and text-high-t0.0 run 4 (10). A-06's registered
rule pairs tiles across corners, so the gaps are topped up before the
analysis. The PI approved the top-up on 2026-10-14 (AEDT): real-time, flex
tier, about US$0.03, run before 00:00 UTC so every pass stays on one UTC date.

Parameter control
-----------------
``lib_batch_api.patch_failed_tiles`` rebuilds each call from the pass's own
meta: model, system instruction, temperature, thinking level, and
``include_example_images`` (False for these text passes, so no example images
are sent, as in the batch requests: about 1,502 input tokens each). The
patcher's second tier normally retries at a reduced ``max_output_tokens``
(2,048); here it is given each pass's own value (8,192), so every attempt runs
at the recorded conditions. The one difference from the batch passes is the
mode: these 15 calls are synchronous (flex), not Batch API.

Safety
------
1. Scope gate: each pass's sidecar ``failed`` list must equal its meta's
   ``failed_items`` and the approved count, or nothing is sent.
2. Archive, never delete: each pass's pre-top-up ``.geojson``, ``.meta.json``,
   and ``.tiles.json`` are copied to ``archive/pre-topup-2026-10-13/`` first.
3. Dry run by default; ``--live`` is required to spend.

Usage::

    python scripts/topup_pro_2x2_failed_tiles.py            # dry run, no API
    python scripts/topup_pro_2x2_failed_tiles.py --live     # the approved top-up

Results: ``outputs/pro-2x2-replication-2026-10-13/topup-2026-10-13.json``.

Created: 2026-10-14 (S164)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

BASE = REPO_ROOT / "outputs/pro-2x2-replication-2026-10-13"
TILES_384 = REPO_ROOT / "inputs/tiles_384"
ARCHIVE_DIR = REPO_ROOT / "archive/pre-topup-2026-10-13"
RESULTS = BASE / "topup-2026-10-13.json"
SERVICE_TIER = "flex"  # the approved tier; same rate as batch on the rate card

#: The three passes and their approved failed-tile counts (15 in all).
UNITS: dict[str, int] = {
    "text-high-t0.7/detect_brief-text/run_3": 2,
    "text-high-t0.0/detect_brief-text/run_3": 3,
    "text-high-t0.0/detect_brief-text/run_4": 10,
}


def unit_paths(unit_dir: Path) -> dict[str, Path]:
    """Return the pass's GeoJSON, meta, and tiles sidecar (exactly one each)."""
    meta = sorted(unit_dir.glob("*.meta.json"))
    tiles = sorted(unit_dir.glob("*.tiles.json"))
    geo = [p for p in sorted(unit_dir.glob("*.geojson"))
           if not p.name.endswith((".meta.json", ".tiles.json"))]
    if not (len(meta) == len(tiles) == len(geo) == 1):
        raise SystemExit(f"{unit_dir}: expected one geojson/meta/tiles, found "
                         f"{len(geo)}/{len(meta)}/{len(tiles)}")
    return {"geojson": geo[0], "meta": meta[0], "tiles": tiles[0]}


def scope_gate(rel: str, expected: int) -> tuple[list[str], int]:
    """Check the sidecar failed list against the meta and the approved count.

    Returns:
        The sorted failed tiles and the pass's own ``max_output_tokens``.
    """
    paths = unit_paths(BASE / rel)
    sidecar = sorted(json.loads(paths["tiles"].read_text()).get("failed", []))
    meta = json.loads(paths["meta"].read_text())
    from_meta = sorted(fi["item_id"] for fi in meta["execution_stats"]["failed_items"])
    if sidecar != from_meta or len(sidecar) != expected:
        raise SystemExit(f"{rel}: scope gate failed (sidecar {len(sidecar)}, "
                         f"meta {len(from_meta)}, approved {expected})")
    missing = [t for t in sidecar if not list(TILES_384.rglob(t))]
    if missing:
        raise SystemExit(f"{rel}: tiles not found under {TILES_384}: {missing}")
    return sidecar, int(meta["configuration"]["max_output_tokens"])


def preserve(rel: str) -> Path:
    """Copy the pass's pre-top-up artefacts to the archive (idempotent)."""
    dest = ARCHIVE_DIR / rel.replace("/", "__")
    dest.mkdir(parents=True, exist_ok=True)
    for src in unit_paths(BASE / rel).values():
        target = dest / src.name
        if not target.exists():
            shutil.copy2(src, target)
    return dest


def main() -> None:
    """CLI entry point: gate, archive, patch, record."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--live", action="store_true",
                        help="make the approved API calls (default: dry run)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    plan = {rel: scope_gate(rel, n) for rel, n in UNITS.items()}
    total = sum(len(tiles) for tiles, _ in plan.values())
    for rel, (tiles, mot) in plan.items():
        print(f"{rel}: {len(tiles)} tiles, max_output_tokens {mot}")
    print(f"total {total} tiles; tier {SERVICE_TIER}; live={args.live}")
    if not args.live:
        return

    from google import genai

    from config import GOOGLE_API_KEY
    from scripts.lib_batch_api import patch_failed_tiles

    client = genai.Client(api_key=GOOGLE_API_KEY)
    started = datetime.now(timezone.utc).isoformat()
    results = []
    for rel, (tiles, mot) in plan.items():
        archived = preserve(rel)
        res = patch_failed_tiles(unit_dir=BASE / rel, client=client,
                                 max_output_tokens=mot, tiles_dir=TILES_384,
                                 service_tier=SERVICE_TIER)
        results.append({"pass": rel, "failed_before": tiles,
                        "recovered": res["recovered"],
                        "recovered_second_tier": res["recovered_safe_mode"],
                        "still_failed": res["still_failed"],
                        "archived_to": str(archived.relative_to(REPO_ROOT))})
        print(f"{rel}: recovered {len(res['recovered'])} + "
              f"{len(res['recovered_safe_mode'])}, still failed {len(res['still_failed'])}")
    RESULTS.write_text(json.dumps({
        "ruling": "D64 top-up, PI-approved 2026-10-14 (AEDT)",
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "service_tier": SERVICE_TIER,
        "second_tier_max_output_tokens": "each pass's own (no reduction)",
        "units": results,
    }, indent=1) + "\n")
    print(f"wrote {RESULTS.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
