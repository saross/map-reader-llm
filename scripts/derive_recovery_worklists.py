#!/usr/bin/env python3
"""
Derive per-pass dead-tile worklists for the E71 recovery rerun.

For each of the 15 genuine-shortfall passes identified by the Phase 2
(C3) provenance triage (`reports/verification/c3-rederivation/
c3-triage-tiles.json`, ruling GENUINE_DISCREPANCY, field-semantics root
cause) plus the segment-scoped pass, compute the authoritative dead-tile
list as **corpus tiles minus the detection GeoJSON's `processed_tiles`**
— the least-writable artefact (charter § 4 authority #1) — and
cross-check against the `.tiles.json` sidecar's `failed` list where that
sidecar is corpus-scoped.

Output: `reports/verification/recovery-rerun-worklists.json`, committed
with the rule-10 registration BEFORE any API call. Zero API cost.

Usage:
    python scripts/derive_recovery_worklists.py
"""

from __future__ import annotations

import glob
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]

#: The shortfall passes: (pass_id, run_dir, corpus_bounds, model_note).
#: Membership per the C3 triage's GENUINE_DISCREPANCY field-semantics rows
#: (E71); the 55maps GAP-8 row is excluded (crop-scale bookkeeping, not a
#: tile shortfall).
ERA2_BOUNDS = "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
ERA3_BOUNDS = "inputs/vectors/bounds/h10-384/test_bounds.geojson"

PASSES: list[dict] = [
    # --- LIVE: feed evaluated pv-diag-384 t0.0 consensus conditions ---
    {"pass_id": "pv-diag-384::flash-high-image-n5-image-t0.0::run1",
     "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/run_1",
     "group": "live-pv-diag-t0.0", "model": "gemini-3-flash-preview (HIGH, T=0.0, image)"},
    {"pass_id": "pv-diag-384::flash-high-image-n5-image-t0.0::run2",
     "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/run_2",
     "group": "live-pv-diag-t0.0", "model": "gemini-3-flash-preview (HIGH, T=0.0, image)"},
    {"pass_id": "pv-diag-384::flash-high-image-n5-image-t0.0::run3",
     "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/run_3",
     "group": "live-pv-diag-t0.0", "model": "gemini-3-flash-preview (HIGH, T=0.0, image)"},
    {"pass_id": "pv-diag-384::flash-high-text-n5-text-t0.0::run1",
     "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/run_1",
     "group": "live-pv-diag-t0.0", "model": "gemini-3-flash-preview (HIGH, T=0.0, text)"},
    {"pass_id": "pv-diag-384::flash-high-text-n5-text-t0.0::run2",
     "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/run_2",
     "group": "live-pv-diag-t0.0", "model": "gemini-3-flash-preview (HIGH, T=0.0, text)"},
    {"pass_id": "pv-diag-384::flash-high-text-n5-text-t0.0::run3",
     "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/run_3",
     "group": "live-pv-diag-t0.0", "model": "gemini-3-flash-preview (HIGH, T=0.0, text)"},
    # --- QUARANTINED: n1-outstanding E57 mis-dispatched FLASH corners (off-board;
    #     model verified per-pass 2026-07-30: gemini-3-flash-preview in ALL four
    #     identity fields — these were never Pro) ---
    {"pass_id": "n1-outstanding-384::pro-image-high-t0::run1",
     "run_dir": "outputs/h11/n1-outstanding-384/pro-image-high-t0/run_1",
     "group": "n1-outstanding-flash-corners", "model": "gemini-3-flash-preview (HIGH, T=0.0, image; E57 mis-dispatched Flash corner)"},
    {"pass_id": "n1-outstanding-384::pro-image-high-t0::run2",
     "run_dir": "outputs/h11/n1-outstanding-384/pro-image-high-t0/run_2",
     "group": "n1-outstanding-flash-corners", "model": "gemini-3-flash-preview (HIGH, T=0.0, image; E57 mis-dispatched Flash corner)"},
    {"pass_id": "n1-outstanding-384::pro-image-high-t0::run3",
     "run_dir": "outputs/h11/n1-outstanding-384/pro-image-high-t0/run_3",
     "group": "n1-outstanding-flash-corners", "model": "gemini-3-flash-preview (HIGH, T=0.0, image; E57 mis-dispatched Flash corner)"},
    {"pass_id": "n1-outstanding-384::pro-text-high-t0::run1",
     "run_dir": "outputs/h11/n1-outstanding-384/pro-text-high-t0/run_1",
     "group": "n1-outstanding-flash-corners", "model": "gemini-3-flash-preview (HIGH, T=0.0, text; E57 mis-dispatched Flash corner)"},
    {"pass_id": "n1-outstanding-384::pro-text-high-t0::run2",
     "run_dir": "outputs/h11/n1-outstanding-384/pro-text-high-t0/run_2",
     "group": "n1-outstanding-flash-corners", "model": "gemini-3-flash-preview (HIGH, T=0.0, text; E57 mis-dispatched Flash corner)"},
    {"pass_id": "n1-outstanding-384::pro-text-high-t0::run3",
     "run_dir": "outputs/h11/n1-outstanding-384/pro-text-high-t0/run_3",
     "group": "n1-outstanding-flash-corners", "model": "gemini-3-flash-preview (HIGH, T=0.0, text; E57 mis-dispatched Flash corner)"},
    # --- SINGLE-TILE shortfalls ---
    {"pass_id": "e47-propose-brief::propose_brief-text::run4",
     "run_dir": "outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text/run_4",
     "group": "single-tile", "model": "gemini-3-flash-preview (propose_brief-text)"},
    {"pass_id": "h12-v2::r3-hp-heavy::run3",
     "run_dir": "outputs/h12-v2/r3-hp-heavy/run_3",
     "group": "single-tile", "model": "gemini-3-flash-preview (era-3)"},
    {"pass_id": "h12-v2::r3-hp-heavy::run5",
     "run_dir": "outputs/h12-v2/r3-hp-heavy/run_5",
     "group": "single-tile", "model": "gemini-3-flash-preview (era-3)"},
    {"pass_id": "flash35-pv-2x2::flash35-min-text-1of10::run3",
     "run_dir": "outputs/flash35-pv-2x2/proposer/run_3",
     "group": "single-tile", "model": "gemini-3.5-flash (minimal, text)"},
]


def dead_tiles_for_pass(run_dir: Path) -> tuple[list[str], dict]:
    """
    Dead tiles = corpus − GeoJSON ``processed_tiles`` (authority #1),
    cross-checked against the ``.tiles.json`` ``failed`` list when that
    sidecar is corpus-scoped.

    Returns:
        (sorted dead-tile list, diagnostics dict).
    """
    geojsons = [p for p in glob.glob(str(run_dir / "*.geojson"))
                if ".meta" not in p and ".tiles" not in p]
    if not geojsons:
        raise SystemExit(f"no detection geojson in {run_dir}")

    # Union processed_tiles across all detection GeoJSONs in the run dir
    # (a pass patched in segments can carry more than one file — e.g.
    # flash35 run_3's two dated segments).
    processed_set: set[str] = set()
    for gp in geojsons:
        with open(gp) as f:
            g = json.load(f)
        pt = g.get("processed_tiles")
        if pt is None:
            raise SystemExit(f"no processed_tiles record in {gp}")
        processed_set |= set(pt)

    diag = {
        "n_processed": len(processed_set),
        "geojsons": [str(Path(p).relative_to(REPO_ROOT)) for p in geojsons],
    }

    # Corpus membership: the sidecar's completed ∪ failed when that union
    # is corpus-sized (dual-listed tiles collapse in the set union — the
    # clean_meta_failed_items class); otherwise the pool-union of sibling
    # passes' records.
    corpus: set[str] = set()
    for gp in geojsons:
        tiles_json = gp.rsplit(".geojson", 1)[0] + ".tiles.json"
        try:
            with open(tiles_json) as f:
                sidecar = json.load(f)
        except FileNotFoundError:
            continue
        if isinstance(sidecar.get("completed"), list):
            cand = set(sidecar["completed"]) | set(sidecar.get("failed", []))
            if sidecar.get("total_tiles") and len(cand) == sidecar["total_tiles"]:
                corpus |= cand
    if corpus and len(corpus) >= len(processed_set):
        diag["derivation"] = (
            f"corpus = sidecar completed∪failed ({len(corpus)}) minus GeoJSON "
            "processed_tiles (authority #1)")
    else:
        corpus = set()
        pool_dir = run_dir.parent
        for sib in sorted(pool_dir.glob("run_*")):
            for sj in glob.glob(str(sib / "*.tiles.json")):
                with open(sj) as f:
                    s = json.load(f)
                if isinstance(s.get("completed"), list):
                    corpus |= set(s["completed"]) | set(s.get("failed", []))
            for gpath in [p for p in glob.glob(str(sib / "*.geojson"))
                          if ".meta" not in p and ".tiles" not in p]:
                with open(gpath) as f:
                    gg = json.load(f)
                if gg.get("processed_tiles"):
                    corpus |= set(gg["processed_tiles"])
        diag["derivation"] = (
            f"corpus = pool-union of sibling records ({len(corpus)}) minus "
            "GeoJSON processed_tiles (authority #1)")

    dead = sorted(corpus - processed_set)
    return dead, diag


def main() -> None:
    """Derive all worklists and write the committed JSON."""
    out = {
        "_README": (
            "Per-pass dead-tile worklists for the E71 recovery rerun (PI ruling "
            "2026-07-30, phase2-rulings S 2.2: 'Erratum + fixes + rerun to sweep up "
            "failed tiles (through usual API-gate process...)'). Derived from the "
            "detection GeoJSONs' processed_tiles (charter S 4 authority #1), "
            "cross-checked against .tiles.json sidecars. Committed with the rule-10 "
            "registration BEFORE any API call."),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passes": [],
    }
    total = 0
    for spec in PASSES:
        run_dir = REPO_ROOT / spec["run_dir"]
        dead, diag = dead_tiles_for_pass(run_dir)
        total += len(dead)
        out["passes"].append({**spec, "n_dead": len(dead), "dead_tiles": dead,
                              "diagnostics": diag})
        logger.info("%s: %d dead tiles (%s)", spec["pass_id"], len(dead),
                    diag["derivation"])
    out["total_dead_tiles"] = total

    dest = REPO_ROOT / "reports/verification/recovery-rerun-worklists.json"
    with open(dest, "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nTotal: {total} dead tiles across {len(PASSES)} passes -> {dest}")


if __name__ == "__main__":
    main()
