# Design: `run_pv.py cleanup` Subcommand

## Problem

After a PV (Proposer-Verifier) verify run completes, some candidates
are missing from the `probabilities.json` output. Failures fall into
three categories:

1. **Transient** — network errors, 503 Service Unavailable (common
   with Flex mode's "sheddable traffic"), rate limits. Already handled
   by in-process backoff retries.
2. **Parse failures** — the verifier model's output JSON is truncated
   or malformed. With HIGH thinking, ~14% of responses hit token
   budget exhaustion and emit partial JSON. Currently counted as
   failed at end of run; data is lost.
3. **Deterministic failures** — specific crops that trigger consistent
   model errors (e.g., candidate_01645 in the E47 v2 run: 20+
   consecutive parse failures before eventually succeeding once).

The 55-map generalisation run's E47 v2 verifier produced 66 missing
candidates out of 4,358 (1.5% failure rate). Recovering them required
five manual steps:

1. Identify missing IDs (diff manifest vs probabilities)
2. Build a subset crops directory with symlinks
3. Write a filtered manifest
4. Run `run_pv.py verify` on the subset
5. Merge results back into the main `probabilities.json`

This pattern will recur in every verify run. It should be a single
idempotent command.

## Proposed Interface

```bash
python3 scripts/run_pv.py cleanup \
    --crops-dir outputs/h11/.../crops/flash-high-text-1of5 \
    --verified-dir outputs/h11/.../verified-v2/flash-high-text-1of5 \
    --verifier-config prompts/configs/verify_adversarial-text_v2.json \
    --mode realtime \
    --service-tier flex \
    --max-attempts 3 \
    [--safe-mode-tokens 2048] \
    [--workers 10] \
    [--dry-run]
```

### Arguments

- `--crops-dir`: Source crops directory with the full
  `candidate_manifest.json` and `crops/` subdirectory (same as the
  original `verify` command).
- `--verified-dir`: Existing verifier output directory containing
  the (possibly incomplete) `probabilities.json` to patch in place.
- `--verifier-config`: Same verifier config used in the original run.
- `--mode`, `--service-tier`, `--workers`, `--iterations`,
  `--temperature`, `--model`, `--thinking-level`: Pass-through to
  the verify code path.
- `--max-attempts`: Number of independent retry rounds (default 3).
  Each round operates on the set still missing after the previous
  round.
- `--safe-mode-tokens`: Optional override for `max_output_tokens`,
  applied on the final attempt. Default: use the config's value
  throughout. When set, the final attempt uses this reduced value
  (e.g., 2048 vs 8192) to constrain thinking budget and prevent
  output truncation.
- `--dry-run`: Identify missing candidates and report the set
  without making any API calls.

## Behaviour

### Step 1: Identify missing candidates

```python
manifest = json.load(open(crops_dir / "candidate_manifest.json"))
probs = json.load(open(verified_dir / "probabilities.json"))
all_ids = {f"candidate_{c['candidate_id']:05d}" for c in manifest["candidates"]}
verified_ids = set(probs.get("results", {}).keys())
missing = all_ids - verified_ids
```

If `missing` is empty, print status and exit 0.

### Step 2: Filter candidates in memory

Build a filtered candidates list (no temp directories, no symlinks):

```python
missing_cands = [
    c for c in manifest["candidates"]
    if f"candidate_{c['candidate_id']:05d}" in missing
]
```

### Step 3: Iterative attempt loop

```python
pending = set(missing)
new_results = {}
cost_per_attempt = []

for attempt in range(1, max_attempts + 1):
    logger.info(f"Attempt {attempt}/{max_attempts}: {len(pending)} missing")

    # Apply safe-mode tokens on final attempt
    token_override = safe_mode_tokens if attempt == max_attempts else None

    filtered_cands = [
        c for c in missing_cands
        if f"candidate_{c['candidate_id']:05d}" in pending
    ]

    # Call existing realtime verify path with filtered candidate list
    attempt_results, cost = _verify_realtime_filtered(
        crops_dir=crops_dir,
        candidates=filtered_cands,
        verifier_config=verifier_config,
        service_tier=service_tier,
        workers=workers,
        max_output_tokens_override=token_override,
    )

    # Record successes
    for key, entry in attempt_results.items():
        new_results[key] = entry
        pending.discard(key)

    cost_per_attempt.append(cost)

    if not pending:
        logger.info(f"All candidates recovered after attempt {attempt}")
        break
```

### Step 4: Merge back in place

```python
# Backup the existing probabilities.json
backup = verified_dir / f"probabilities.json.pre-cleanup-{timestamp}.backup"
shutil.copy(verified_dir / "probabilities.json", backup)

# Merge new results
probs["results"].update(new_results)
probs["total_results"] = len(probs["results"])

# Add audit trail
probs.setdefault("cleanup_history", []).append({
    "timestamp": iso_now(),
    "candidates_recovered": len(new_results),
    "candidates_remaining_missing": len(pending),
    "attempts_used": attempt,
    "cost_per_attempt_usd": cost_per_attempt,
    "total_cost_usd": sum(cost_per_attempt),
    "max_attempts": max_attempts,
    "safe_mode_tokens_used": safe_mode_tokens is not None,
})

with open(verified_dir / "probabilities.json", "w") as f:
    json.dump(probs, f, indent=2)
```

### Step 5: Report

```text
Cleanup Report
==============
Initial missing: 66
Recovered: 65
Still missing: 1 (ids: candidate_01645)
Attempts used: 3
Total cost: $0.0823
Backup: probabilities.json.pre-cleanup-20260409T221500.backup
```

If any candidates remain missing after all attempts, list them and
exit with code 1 (caller can pipe through a final manual retry or
accept the partial result).

## Implementation Requirements

### 1. New `_verify_realtime_filtered()` helper

Extract the realtime verification loop from `_verify_realtime()` into
a helper that accepts a pre-filtered candidate list. The original
`_verify_realtime()` can then become a thin wrapper that loads
candidates from the manifest and calls the helper with the full list.

Signature:

```python
def _verify_realtime_filtered(
    crops_dir: Path,
    candidates: list[dict],
    verifier_config: Path,
    service_tier: str | None,
    workers: int,
    iterations: int = 1,
    temperature: float | None = None,
    model_override: str | None = None,
    thinking_level_override: str | None = None,
    max_output_tokens_override: int | None = None,
) -> tuple[dict, float]:
    """Verify a pre-filtered candidate list. Returns (results_dict, cost_usd)."""
```

The `max_output_tokens_override` is the key addition for safe-mode
retries — when set, the generation config uses this value instead of
the config's default. This is the same mechanism as
`SAFE_MODE_MAX_OUTPUT_TOKENS` in `lib_batch_api.py`.

### 2. New `cmd_cleanup()` function

Mirror the structure of `cmd_verify()` and `cmd_extract()`. Loads the
manifest and existing probabilities, computes the diff, runs the
attempt loop, merges results, writes the output.

### 3. New `cleanup` subparser

```python
cleanup_parser = subparsers.add_parser(
    "cleanup",
    help="Re-verify missing candidates with iterative retries",
)
cleanup_parser.add_argument("--crops-dir", type=Path, required=True)
cleanup_parser.add_argument("--verified-dir", type=Path, required=True)
cleanup_parser.add_argument("--verifier-config", type=Path, required=True)
cleanup_parser.add_argument(
    "--mode", choices=["realtime"], default="realtime",
    help="Only realtime supported for cleanup (batch API has different semantics)",
)
cleanup_parser.add_argument("--service-tier", choices=["standard", "flex"])
cleanup_parser.add_argument("--workers", type=int, default=10)
cleanup_parser.add_argument("--iterations", type=int, default=1)
cleanup_parser.add_argument("--temperature", type=float)
cleanup_parser.add_argument("--model", type=str)
cleanup_parser.add_argument("--thinking-level", type=str)
cleanup_parser.add_argument("--max-attempts", type=int, default=3)
cleanup_parser.add_argument(
    "--safe-mode-tokens", type=int,
    help="Reduced max_output_tokens for final attempt "
    "(prevents thinking token budget exhaustion).",
)
cleanup_parser.add_argument("--dry-run", action="store_true")
cleanup_parser.set_defaults(func=cmd_cleanup)
```

### 4. Tests

Add to `tests/test_run_pv.py` (or create it if missing):

- `test_cleanup_identifies_missing_candidates`: Given a manifest
  with 10 candidates and a probabilities.json with 7 results,
  `cmd_cleanup` correctly identifies the 3 missing IDs.
- `test_cleanup_merges_in_place`: After cleanup, the target
  `probabilities.json` contains all verified candidates and a
  `cleanup_history` entry.
- `test_cleanup_backup_created`: Backup file with timestamp exists
  after merge.
- `test_cleanup_safe_mode_tokens_applied`: When `--safe-mode-tokens`
  is set, the generation config for the final attempt uses the
  reduced value (mock the API call and inspect config).
- `test_cleanup_idempotent`: Running cleanup a second time on the
  same directory processes 0 candidates and exits 0.
- `test_cleanup_dry_run_no_api_calls`: Dry-run mode identifies
  missing candidates but makes no API calls.

## Scope and Size

- `run_pv.py`: ~150 lines added (cleanup command + helper refactor)
- `test_run_pv.py`: ~100 lines for the six tests
- Documentation: Update `docs/methodology/` to describe the cleanup
  pattern and when to use safe-mode tokens.

## Future Extensions

- **Proposer-side cleanup** (`4_detect_mounds_batch.py cleanup`): The
  same pattern applies to the proposer's real-time mode. After a
  proposer run completes with stragglers, a cleanup pass can patch
  the missing tiles. Shares the diff-filter-retry-merge pattern but
  operates on `tiles.json` and GeoJSON features instead of
  `candidate_manifest.json` and `probabilities.json`.
- **Cross-run consolidation**: Given N runs of the same experiment
  (e.g., 5 proposer passes), a single command could identify tiles
  missing from any run and recover them all at once.
- **Safe-mode escalation schedule**: Instead of only applying
  safe-mode on the final attempt, escalate progressively (e.g.,
  attempt 1 at 8192, attempt 2 at 4096, attempt 3 at 2048).

## Reference Implementation Trace

The manual cleanup of E47 v2's 66 failed candidates on 2026-04-09
used this exact pattern:

1. Diff manifest vs probabilities → 66 missing IDs
2. Build subset crops dir with symlinks
3. Filter manifest to just those 66
4. Run `run_pv.py verify --mode realtime --service-tier flex` → 65 succeeded
5. Merge into main probabilities.json → 4,357/4,358
6. Manual single-candidate retry for stubborn candidate_01645 → succeeded
7. Final merge → 4,358/4,358 complete

Total time: ~15 minutes of manual shell/Python work. The subcommand
would reduce this to a single `run_pv.py cleanup` invocation.

## Timeline

- Implement once the 55-map run completes (avoid touching `run_pv.py`
  while the verifier stage is active).
- Target: next session after the overnight run finishes.
