#!/usr/bin/env python3
"""Re-derive tier E's two API-derived records offline, from committed files.

Fault-window re-check W2-3, part B (sub-agent w2-3b), 2026-10-15.

Tier E's ``smoke/smoke.json`` (98e54baf6) and ``spend-ledger.json``
(5167b9a5c) summarise real-time verifier calls, so they cannot be regenerated
without spend. Every number in them is, however, a function of the committed
``run.meta.json`` / ``probabilities.json`` of those calls and of the gated
unions file. This driver recomputes them with the replay tree's own module
(``scripts.run_k_ladder_tier_e`` at 5167b9a5c, whose cost function
``audited_flex_usd`` is the one both records were written with) and writes
them for an exact comparison. It makes no network call and runs no verifier.

* ``smoke.json`` follows ``cmd_smoke`` as it stood at 98b43e3be, the code that
  wrote the committed file: ``probabilities_returned`` was then
  ``len(probabilities)`` (the envelope's top-level key count, which 5b2f2c05d
  later corrected to ``total_results``). The re-derivation reports both.
* ``spend-ledger.json`` rebuilds each rung's entry as ``verify_rung`` builds
  it, from the rung's committed meta, and the totals with the module's own
  ``save_ledger``. Only wall-clock fields cannot be re-derived:
  ``wall_seconds`` is copied from the committed entry and the two timestamps
  are copied too, so they show up as equal by construction (and are named as
  set aside in the comparison).

Usage (cwd = the 5167b9a5c replay tree):
    python rederive_tier_e_records.py --out-dir OUT
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

import scripts.run_k_ladder_tier_e as te  # noqa: E402

SMOKE = Path("results/k-ladder-2026-09-12/tier-e/smoke")


def smoke_record() -> dict:
    """The smoke report as 98b43e3be's ``cmd_smoke`` built it."""
    union = json.loads((SMOKE / "union_first5.geojson").read_text())
    meta = json.loads((SMOKE / "verify" / "run.meta.json").read_text())
    probabilities = json.loads((SMOKE / "verify" / "probabilities.json").read_text())
    committed = json.loads((SMOKE / "smoke.json").read_text())
    cost = te.audited_flex_usd(meta)
    config = meta.get("configuration", {})
    return {
        "generated_at_utc": committed["generated_at_utc"],
        "candidates": len(union["features"]),
        "probabilities_returned": len(probabilities),
        "model": config.get("model"),
        "thinking_level": config.get("thinking_level"),
        "temperature": config.get("temperature"),
        "instruction_hash": config.get("system_instruction_hash"),
        "flex_usd": cost["flex_usd"],
        "list_usd_recorded": cost["list_usd_recorded"],
        "cost_basis_in_meta": meta.get("cost_estimate", {}).get("cost_basis"),
    }, {
        "probabilities_total_results": probabilities.get("total_results"),
        "probabilities_n_results": len(probabilities.get("results", [])),
        "probabilities_top_level_keys": sorted(probabilities),
    }


def ledger_entry(rung: dict, committed_entry: dict) -> dict:
    """One rung's ledger entry, as ``verify_rung`` builds it from the meta."""
    meta = json.loads((Path(rung["verify_dir"]) / "run.meta.json").read_text())
    cost = te.audited_flex_usd(meta)
    stats = meta.get("execution_stats", {})
    finish = stats.get("finish_reason_counts", {})
    calls = sum(int(value) for value in finish.values()) or int(
        meta.get("usage_stats", {}).get("by_provider", {})
        .get("google_gemini", {}).get("request_count", 0))
    config = meta.get("configuration", {})
    return {
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
        "model": config.get("model"),
        "thinking_level": config.get("thinking_level"),
        "temperature": config.get("temperature"),
        "instruction_hash": config.get("system_instruction_hash"),
        "service_tier_requested": "flex",
        "service_tier_recorded_in_meta": None,
        "cost_basis_in_meta": meta.get("cost_estimate", {}).get("cost_basis"),
        "discount_in_meta": meta.get("cost_estimate", {})
        .get("pricing_used", {}).get("discount"),
        "wall_seconds": committed_entry["wall_seconds"],
        **cost,
    }


def main() -> None:
    """Write both re-derived records under --out-dir."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    out = args.out_dir
    (out / "results/k-ladder-2026-09-12/tier-e/smoke").mkdir(parents=True, exist_ok=True)

    smoke, smoke_notes = smoke_record()
    (out / SMOKE / "smoke.json").write_text(json.dumps(smoke, indent=2) + "\n")

    committed = json.loads(te.LEDGER_JSON.read_text())
    ledger = {key: committed[key] for key in
              ("created_at_utc", "tier", "basis", "hard_stop_usd", "approved_usd")}
    ledger["basis"] = (
        "flex: input x 0.25 + (output + thinking) x 1.50 per million USD, "
        "recomputed from run.meta.json token counts because the verify "
        "path stamps cost_basis 'list' with discount 1.0 under flex")
    ledger["hard_stop_usd"] = te.HARD_STOP_USD
    ledger["approved_usd"] = te.APPROVED_USD
    ledger["rungs"] = {}
    for rung in te.load_gated_rungs():
        key = te.ledger_key(rung)
        ledger["rungs"][key] = ledger_entry(rung, committed["rungs"][key])
    te.LEDGER_JSON = out / "results/k-ladder-2026-09-12/tier-e/spend-ledger.json"
    te.save_ledger(ledger)
    data = json.loads(te.LEDGER_JSON.read_text())
    data["updated_at_utc"] = committed["updated_at_utc"]
    te.LEDGER_JSON.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps({"smoke_notes": smoke_notes, "ledger_total": data["total"]},
                     indent=2))


if __name__ == "__main__":
    main()
