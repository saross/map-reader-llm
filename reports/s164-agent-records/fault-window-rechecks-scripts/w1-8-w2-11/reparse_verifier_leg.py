#!/usr/bin/env python3
"""
Re-derive a batch verifier leg's probabilities and cost booking offline.

Fault-window re-check (2026-10-14), rows W1-8 and W2-11. A batch verifier
leg commits the raw Batch API results (``batch_results.jsonl``) beside the
``probabilities.json`` and ``run.meta.json`` that ``run_pv.py`` wrote from
them. This driver re-derives both from the committed JSONL with the SAME
functions ``run_pv._finish_batch_outputs`` calls, imported from a replay
tree checked out at the leg's recorded ``environment.git_commit``:

- ``lib_batch_api.validate_batch_results`` (expected keys from the crop
  manifest), ``lib_verifier.parse_verifier_results``, and the payload
  ``run_pv._write_verification_outputs`` dumps (``json.dump(indent=2)``);
- ``lib_batch_api.aggregate_batch_usage`` for the usage the meta books, and
  ``lib_llm_metadata.estimate_cost`` at the tier ``lib_cost.tier_from_cli``
  gives a batch leg, priced ``at`` the committed meta's own end time.

It imports the parsing functions only. It never imports or calls anything
that lodges, polls or retrieves a job, and never builds a client (no
``google.genai`` import happens on these paths); run it with the API-key
variables blanked. Inputs are read with ``git show`` at the commit that
added them, so the replay tree may sit at an earlier commit.

Usage:
    python reparse_verifier_leg.py --tree TREE --repo REPO --leg LEG_DIR \
        --added COMMIT [--manifest MANIFEST] --out result.json

Author: Claude (Opus 5.5) for Shawn Ross; Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def git_show(repo: Path, commit: str, path: str) -> bytes:
    """Bytes of ``commit:path`` in ``repo`` (raises when absent)."""
    return subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"],
                          capture_output=True, check=True).stdout


def main() -> int:
    """Re-derive one leg and compare with the committed files."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, required=True,
                    help="Replay tree at the leg's recorded git_commit")
    ap.add_argument("--repo", type=Path, required=True,
                    help="Any checkout holding the history (for git show)")
    ap.add_argument("--leg", required=True, help="Leg dir, repo-relative")
    ap.add_argument("--added", required=True, help="Commit that added the leg's files")
    ap.add_argument("--manifest", default=None,
                    help="Crop manifest, repo-relative (default: ../crops/...)")
    ap.add_argument("--vconfig", default="prompts/configs/verify_adversarial-text.json")
    ap.add_argument("--expected-n", type=int, default=None,
                    help="No tracked crop manifest: synthesise candidate ids 0..N-1 "
                         "(the extractor numbers a union's features in order; N is the "
                         "union's feature count). Recorded in the output.")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    sys.path.insert(0, str(args.tree))
    from scripts.lib_batch_api import aggregate_batch_usage, validate_batch_results
    from scripts.lib_llm_metadata import AggregatedUsage, LLMProvider, estimate_cost
    from scripts.lib_verifier import parse_verifier_results
    try:  # the tiered cost path (lib_cost, 2026-09-21 onwards)
        from scripts.lib_cost import tier_from_cli
    except ImportError:  # before it, run_pv priced with estimate_cost(usage, provider, model)
        tier_from_cli = None

    leg = args.leg.rstrip("/")
    if args.expected_n is not None:
        manifest_path = f"<synthesised ids 0..{args.expected_n - 1}>"
        manifest = {"candidates": [{"candidate_id": i} for i in range(args.expected_n)]}
    else:
        manifest_path = args.manifest or str(Path(leg).parent / "crops"
                                             / "candidate_manifest.json")
        manifest = json.loads(git_show(args.repo, args.added, manifest_path))
    raw_bytes = git_show(args.repo, args.added, f"{leg}/batch_results.jsonl")
    raw = [json.loads(line) for line in raw_bytes.decode().splitlines() if line.strip()]
    committed_probs = git_show(args.repo, args.added, f"{leg}/probabilities.json")
    meta = json.loads(git_show(args.repo, args.added, f"{leg}/run.meta.json"))
    config = json.loads((args.tree / args.vconfig).read_text())
    iterations = json.loads(committed_probs)["iterations"]

    # Expected keys exactly as _finish_batch_outputs builds them.
    expected: list[str] = []
    for cand in manifest.get("candidates", []):
        cid = cand["candidate_id"]
        if iterations > 1:
            expected += [f"candidate_{cid:05d}_iter{i}" for i in range(1, iterations + 1)]
        else:
            expected.append(f"candidate_{cid:05d}")
    matched, missing, errored = validate_batch_results(expected, raw)
    parsed = parse_verifier_results(matched)
    payload = {"version": "1.0", "mode": "batch",
               "verifier_config": config.get("version", "unknown"),
               "iterations": iterations, "total_results": len(parsed),
               "results": parsed}
    regen = json.dumps(payload, indent=2).encode()

    # The usage and cost the meta books (record_batch_usage + estimate_cost).
    usage = aggregate_batch_usage(raw)
    agg = AggregatedUsage()
    for name in ("total_input_tokens", "total_output_tokens", "total_cached_tokens",
                 "total_thoughts_tokens", "total_tokens"):
        setattr(agg, name, int(usage.get(name, 0)))
    model = meta["configuration"]["model"]
    if tier_from_cli is not None:
        tier, tier_source = tier_from_cli(None, batch=True)
        cost = estimate_cost(usage=agg, provider=LLMProvider.GEMINI.value, model=model,
                             tier=tier, tier_source=tier_source,
                             at=(meta.get("timestamp") or {}).get("end"), strict=False)
    else:
        tier = tier_source = None
        cost = estimate_cost(usage=agg, provider=LLMProvider.GEMINI.value, model=model)
    batch_usage = {"n_responses_with_usage": usage["n_responses_with_usage"],
                   "n_results": len(raw), "usage_source": usage["usage_source"],
                   "cached_share": usage["cached_share"],
                   "raw_results": "batch_results.jsonl"}
    checks: dict[str, Any] = {}
    for name in ("total_input_tokens", "total_output_tokens", "total_cached_tokens",
                 "total_thoughts_tokens", "total_tokens"):
        checks[f"usage_stats.{name}"] = [int(usage.get(name, 0)),
                                         meta["usage_stats"].get(name)]
    checks["results_summary.batch_usage"] = [batch_usage,
                                             meta["results_summary"].get("batch_usage")]
    checks["execution_stats.items_processed"] = [len(matched),
                                                 meta["execution_stats"]["items_processed"]]
    checks["cost_estimate"] = [cost, meta.get("cost_estimate")]
    if tier_from_cli is not None:
        checks["billing"] = [{"service_tier": tier, "tier_source": tier_source},
                             meta.get("billing")]
    meta_equal = {k: v[0] == v[1] for k, v in checks.items()}
    n_parse_error = sum(1 for r in parsed.values()
                        if str(r.get("reasoning", "")).startswith("PARSE_ERROR"))
    out = {
        "leg": leg, "added": args.added, "manifest": manifest_path,
        "code_commit": subprocess.run(["git", "-C", str(args.tree), "rev-parse", "HEAD"],
                                      capture_output=True, text=True).stdout.strip(),
        "meta_git_commit": meta["environment"]["git_commit"],
        "n_expected": len(expected), "n_raw_rows": len(raw), "n_matched": len(matched),
        "n_missing": len(missing), "n_errored": len(errored),
        "n_parse_error_rows": n_parse_error,
        "probabilities_regen_sha256": hashlib.sha256(regen).hexdigest(),
        "probabilities_committed_sha256": hashlib.sha256(committed_probs).hexdigest(),
        "probabilities_byte_identical": regen == committed_probs,
        "meta_fields_equal": meta_equal,
        "meta_all_equal": all(meta_equal.values()),
        "audited_total_cost_usd": cost.get("total_cost_usd"),
        "meta_mismatches": {k: v for k, v in checks.items() if not meta_equal[k]},
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(f"{leg}: probs {'IDENTICAL' if out['probabilities_byte_identical'] else 'DIFFER'}; "
          f"meta fields {'EQUAL' if out['meta_all_equal'] else 'DIFFER'}; "
          f"{len(matched)}/{len(expected)} matched; cost {out['audited_total_cost_usd']}")
    return 0 if out["probabilities_byte_identical"] and out["meta_all_equal"] else 1


if __name__ == "__main__":
    sys.exit(main())
