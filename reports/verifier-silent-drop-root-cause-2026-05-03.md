# Verifier Silent-Drop Root-Cause Analysis (2026-05-03)

## Executive summary

This is **one bug** with several contributing failure modes that all funnel
through the same surfacing gap.

The dominant mechanism is straightforward: in
`scripts/run_pv.py:_verify_realtime()`, when a worker returns an empty result
dict (because `lib_verifier._call_verifier_api()` exhausted its three retries),
the driver increments a local `failed_count` integer but **never calls
`metadata_tracker.log_failure(candidate_id, ...)` and never records the
candidate identity anywhere**. The candidate is simply absent from
`all_results`, which is written verbatim to `probabilities.json`. There is
**no post-run cardinality check** comparing manifest size to results size, so
the driver exits 0 even when 460 candidates are missing.

A second mechanism amplifies the first: the verifier's per-call retry policy
is markedly weaker than the proposer's (`_MAX_RETRIES = 3` with 2/4/8 s
backoff and a single bare `except Exception`), with **no `MAX_TOKENS`
finish-reason handling, no `parse_response_with_repair()` three-tier JSON
recovery, and no error-class-specific backoff** (proposer differentiates 429
/ 503 / DeadlineExceeded with up to 15 retries and minute-scale waits). More
candidates therefore *exhaust retries* in the verifier than in the proposer
for the same upstream noise, and *every* exhausted-retry candidate is
silently dropped because of the surfacing gap above.

**Smallest viable fix:** add `metadata_tracker.log_failure(...)` with
`candidate_id` in the `as_completed()` loop in `_verify_realtime()` (one call
site, ~5 lines), and add a post-run cardinality assertion before returning
success. This converts every silent drop into a visible `failed_items[]`
entry and a non-zero exit code — recovery via `run_pv.py cleanup` already
works and would not need changes.

## Failure-mode taxonomy

For each transient failure mode the verifier API call can hit, the table
records (a) what the runtime sees, (b) what the runtime does, (c) what ends
up in `probabilities.json`, and (d) whether a per-candidate identifier is
surfaced anywhere.

| # | Failure mode | Runtime detection | Runtime action | Effect on `probabilities.json` | Per-candidate ID surfaced? |
|---|---|---|---|---|---|
| 1 | HTTP 429 rate limit | `Exception` containing `"429"` / `ResourceExhausted` | Caught by bare `except Exception` (`lib_verifier.py:938`); error metadata logged via `create_error_metadata()`; retry up to 3× with 2/4/8 s backoff. After 3rd failure: `return None`. | Candidate absent from `results` | **No.** Aggregate `parse_failures` / per-attempt error metadata exists in `run.meta.json`'s `response_metadata[]` (when `_store_per_item=True`), but the candidate identity is not appended to `failed_items[]`. |
| 2 | HTTP 5xx / `InternalServerError` | Same `Exception` branch | Same as 429 — undifferentiated | Same | Same |
| 3 | Network timeout / `DeadlineExceeded` | Same `Exception` branch | Same — undifferentiated | Same | Same |
| 4 | JSON parse failure (truncated, malformed, prose-wrapped) | `json.JSONDecodeError` raised at `lib_verifier.py:904` | Caught at line 918; `parse_success=False`, `parse_error` populated; retry up to 3× with 2/4/8 s backoff; after 3rd failure: `return None`. | Candidate absent from `results` | **No.** `parse_failures` aggregate count is incremented, the per-attempt metadata records `parse_error`, but no `failed_items[]` entry. |
| 5 | List-wrapped JSON (`[{...}]`) | `_unwrap_verdict_payload` accepts since 2026-04 (commit `acba8999`) | **Recovered** since the cand_01563 fix. Pre-fix: would raise `AttributeError` and fall into the bare `except Exception` retry path; deterministic, so retries exhausted and silent drop. | Now resolved | n/a (historical) |
| 6 | Other shape (e.g. JSON literal, empty array, nested) | `_unwrap_verdict_payload` raises `ValueError` | Same as JSON parse failure (`except (json.JSONDecodeError, ValueError)`) | Candidate absent | Same as #4 |
| 7 | Safety-block / refusal | `response.text` raises `ValueError` ("BLOCKED") | Caught at `lib_verifier.py:877`; `parse_error="BLOCKED: ..."`; **`return None` immediately — no retry** | Candidate absent | **No.** `safety_blocks` aggregate is incremented but no `failed_items[]` entry. |
| 8 | `response.text is None` (empty response) | Explicit `if txt is None` check at line 887 | `parse_error="EMPTY_RESPONSE"`; **`return None` immediately — no retry** | Candidate absent | **No.** `empty_responses` aggregate incremented; no `failed_items[]` entry. |
| 9 | `MAX_TOKENS` finish reason (truncated output) | **Not detected.** `lib_verifier._call_verifier_api()` does not inspect `finish_reason`. | Truncated text reaches `json.loads()`, fails as `JSONDecodeError` → handled like #4. **Deterministic** if thinking-token budget cap is hit, so the same crop fails on every retry → silent drop. | Candidate absent | Same as #4 |
| 10 | Schema-validation (missing `mound_probability`) | None — `verdict.get("mound_probability", 0.0)` is permissive | Result is recorded with prob=0.0 and empty fields | Candidate present with prob=0 (NOT a silent drop) | n/a |
| 11 | Unhandled exception in post-processing | Outer `as_completed` `except Exception` (`run_pv.py:780`) | `failed_count += 1`, `logger.error("Candidate %s failed: %s", cid, e)` — **NOT logged to metadata tracker** | Candidate absent | Logged to stderr only. Lost on log rotation. |
| 12 | Process kill / OOM mid-run | n/a | Incremental save every 100 candidates (atomic via tmp+rename); next launch resumes via existing-results merge | Last incomplete batch (≤ 100 candidates) absent until resumed | n/a — by design, but is recoverable through resume |
| 13 | Crop file missing (extraction error) | `FileNotFoundError` at `lib_verifier.py:739` | `logger.warning`, `return ({}, [])` from `verify_candidate_realtime` | Candidate absent | **No.** No `failed_items[]` entry. |

**Summary of the surfacing gap:** modes 1–4 and 6–9, 11, 13 all converge on
"candidate absent from `probabilities.json`, no `failed_items[]` entry,
aggregate counters incremented but candidate identity not recorded". Modes
1–4 were the dominant ones in the affected cells, judging by the gap=57 cell
inspected (`outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/run.meta.json`)
which has `parse_failures: 1147`, `empty_responses: 1147`, `finish_reason_counts.error: 1147`,
yet `failed_items: []`, `completed_items: []`.

Note that aggregate counters being non-zero while `failed_items[]` is empty
*could* have been used as a tripwire by an operator who knew to look — but
the project never had such a tripwire and `failed_items[]` was the canonical
"who failed" record (per the proposer pipeline's contract).

## Code-path map

### Silent-drop mechanism A — `run_pv.py` does not call `log_failure`

- **File**: `scripts/run_pv.py`, function `_verify_realtime()`, lines 763–793
- **Trace**:
  - Line 767: `cand_results, metadata_list = future.result()`
  - Line 770–772: per-call metadata is logged (`log_response`) — this captures
    aggregate counts and per-call response metadata
  - Line 774: `if cand_results: all_results.update(cand_results); verified_count += 1`
  - Line 777–778: `else: failed_count += 1`
  - **No `metadata_tracker.log_failure(candidate_id, ...)` is called.**
    `metadata_tracker.log_success(candidate_id)` is also missing — but the
    omission of `log_failure` is the load-bearing one because it is the only
    record that ties a *candidate identity* to a terminal failure
- **Comparison**: `scripts/5_verify_crops.py:647 / 651` — the legacy verifier
  *does* call `log_failure` on both result-dict-empty and exception paths
  (using a `cand_NNNN` counter rather than the candidate_id, but the
  identity-to-failure mapping is at least present)

### Silent-drop mechanism B — no post-run cardinality check

- **File**: `scripts/run_pv.py`, function `_write_verification_outputs()`,
  lines 856–869
- **Trace**:
  - Line 859–868: writes `probabilities.json` with
    `total_results: len(parsed_results)`
  - **No comparison against `len(manifest["candidates"]) × iterations`.**
    Driver returns 0 (success) regardless of cardinality.
- **Comparison**: the batch path at `_verify_batch` (lines 526–533) does
  surface a `missing` warning via `validate_batch_results()`, but it is a log
  line only — does not raise, does not affect exit code, and does not write
  the missing IDs to `run.meta.json`

### Silent-drop mechanism C — weak retry policy in the verifier API call

- **File**: `scripts/lib_verifier.py`, function `_call_verifier_api()`,
  lines 820–964
- **Trace**:
  - Line 73–74: `_MAX_RETRIES = 3`, `_RETRY_BACKOFF_SECONDS = [2, 4, 8]`
  - Line 938: bare `except Exception as e:` — does not differentiate 429 /
    5xx / DeadlineExceeded
  - No 429 detection → no longer-cooldown branch → no governor signal
  - No `parse_response_with_repair()` invocation — line 904 calls plain
    `json.loads(txt)` after only stripping ``` ```json ``` fences
- **Comparison**: `scripts/4_detect_mounds_batch.py:363–537`:
  - `max_retries=15` default (line 673)
  - 429 → exponential backoff up to `MAX_BACKOFF_SECONDS`, governor signalled
  - 503 / `InternalServerError` → 30 ± 10 s wait, separate counter
  - `DeadlineExceeded` → 30 ± 10 s wait, separate counter
  - `MAX_TOKENS` finish reason explicitly retried (line 422–437)
  - Final parse goes through `parse_response_with_repair()` (line 580 — three
    tiers: trailing-comma → json5 → longest-valid-prefix), which handles
    ~92 % of historical malformed responses per the audit on the canonical
    runs. Verifier path bypasses this entirely.

### Auxiliary mechanism — `_unwrap_verdict_payload` (already fixed)

- **File**: `scripts/lib_verifier.py:771–817`
- **Status**: fixed in commit `acba8999` after the cand_01563 forensic
  exercise. Pre-fix, list-wrapped responses raised `AttributeError` in the
  verdict-extraction code, which was caught by the bare `except Exception`,
  retried, and — because the model deterministically returned the same shape
  — exhausted retries and silently dropped. Post-fix, list-wrapped responses
  unwrap correctly and produce results.
- **Lesson**: a deterministic-failure mode hidden inside a generic retry
  loop and surfaced only as an aggregate counter is exactly the failure
  pattern the present taxonomy describes. The cand_01563 fix closed the
  specific shape; the surfacing gap that hid it for months remains.

## Comparison with proposer pipeline

| Aspect | Proposer (`4_detect_mounds_batch.py`) | Verifier (`run_pv.py` + `lib_verifier.py`) |
|---|---|---|
| Per-item failure record | `metadata_tracker.log_failure(tile_filename, str(e))` on every terminal failure (line 655, 596, 556) | **Missing.** Only an integer `failed_count` and a stderr line. |
| Per-item success record | `log_success(tile_filename)` at end of pipeline (line 649) | **Missing.** |
| Failed-item retrievable from `run.meta.json` | Yes — `execution_stats.failed_items[]` lists `{item_id, reason, timestamp}` | No. `failed_items[]` always empty. |
| Cardinality check after run | Implicit via `failed_items[]`; recovery driver iterates `failed_items[]` ids | None — the only check is the audit script (post-hoc, manual). |
| Retry budget | `max_retries=15` (line 673) | `_MAX_RETRIES = 3` (lib_verifier.py:73) |
| Error-class differentiation | 429 vs 503 vs DeadlineExceeded vs MAX_TOKENS, each with own backoff and counter (lines 474–514) | Single bare `except Exception` (lib_verifier.py:938) |
| Backoff strategy | Exponential with jitter, capped at `MAX_BACKOFF_SECONDS`, minute-scale | Fixed 2 / 4 / 8 s |
| Governor / 429 feedback | TPM governor signalled on rate-limit (line 521–531) | None |
| `MAX_TOKENS` handling | Detected and retried (line 422–437) | Not detected; falls through as `JSONDecodeError` |
| JSON parse repair | `parse_response_with_repair()` 3-tier (line 580) | `json.loads(txt)` only (lib_verifier.py:904) |
| TPM/RPM governance | Yes (`TPMGovernor`) | None |

The cleanup driver works because it does not depend on any of the missing
runtime surfacing — it computes
`set(manifest_ids) − set(probabilities.json keys)`, which is independent of
*why* the original drop happened and *whether* the failure was logged
anywhere. That set difference is the recovery key.

## Recommendations for fix scope

Three nested layers, each strictly larger than the previous. Listed by
effort, not priority — Shawn / the planning agent should pick the layer
based on how much defence-in-depth is wanted.

### Layer 1 — Surfacing fix (smallest viable; ~5 LoC + tests)

**What it covers:** every silent-drop mode in the taxonomy becomes visible
in `run.meta.json:execution_stats.failed_items[]`, with the candidate ID as
the canonical key. Operator sees `items_failed: N` in the log summary at
end-of-run; downstream tooling can parse `failed_items[]` and trigger
`run_pv.py cleanup` automatically.

**Touch points:**

1. `run_pv.py:_verify_realtime()` lines 763–793: in the `cand_results` empty
   branch, call `metadata_tracker.log_failure(f"candidate_{cid:05d}", "no result returned")`.
   In the outer `except Exception` branch, call `log_failure(..., str(e))`.
   In the success branch, call `log_success(...)` for symmetry with the
   proposer.
2. `run_pv.py:_write_verification_outputs()`: emit a warning (and ideally
   set a non-zero `incomplete` flag in `run.meta.json`) when
   `len(parsed_results) < expected`.
3. Same fix needed in `_verify_batch()` for the `missing` set returned by
   `validate_batch_results()` (already computed, just not logged).

**What it misses:**

- It does not reduce the *rate* of silent drops — only their visibility.
  The same crops will still exhaust retries; they will simply now show up
  in `failed_items[]` instead of vanishing.
- Crop-file-not-found (mode #13) happens inside
  `verify_candidate_realtime()` and the worker still returns
  `({}, [])` — so the surfacing logic correctly catches it but the
  failure reason will read "no result returned" rather than the
  upstream `FileNotFoundError`. This is a minor cosmetic issue.

**Estimated effort:** half a day, including test updates. Tests in
`tests/test_run_pv.py` already exist for cleanup; only one or two new tests
are needed to confirm `failed_items[]` is populated on empty `cand_results`.

### Layer 2 — Surfacing + retry-parity (medium; ~50–100 LoC)

Layer 1, plus:

**What it adds:**

1. Adopt `parse_response_with_repair()` from `lib_batch_api.py` in
   `_call_verifier_api()` — recovers ~92 % of malformed-JSON responses
   per the audit, so most parse-failure drops simply stop happening.
2. Differentiate exception classes in the bare `except Exception`:
   429 / 5xx / DeadlineExceeded / other, each with its own backoff and
   counter, mirroring the proposer.
3. Increase `_MAX_RETRIES` to 10–15 with longer waits for rate-limit and
   server-error classes.
4. Add `MAX_TOKENS` finish-reason check; if hit, retry once with
   `max_output_tokens` reduced (the cleanup driver's safe-mode pattern,
   `--safe-mode-tokens`, exists already; the same logic inline in the
   verifier API call would prevent the deterministic-truncation drop
   path entirely).

**What it misses:**

- Still does not eliminate truly stubborn cases — some crops repeatedly
  trigger model refusals or content-filter blocks. Cleanup with
  `--safe-mode-tokens` already handles a fraction of these; the residual
  is fundamental.
- Does not add a cardinality assertion at the script level — Layer 3.

**Estimated effort:** 2–3 days, including porting tests for the parse
repair path and adding new retry-class tests.

### Layer 3 — Pipeline-level assertion + audit-on-write (large; ~150 LoC)

Layer 1 + Layer 2, plus:

**What it adds:**

1. After every verifier run, before exit, compute
   `gap = expected_input − len(probabilities.results)`. If `gap > 0`,
   either (a) auto-invoke cleanup with `--max-attempts 3 --safe-mode-tokens`,
   or (b) write `run.meta.json:incomplete: true` and exit 1.
2. Emit a `verifier_completeness.json` sidecar with the same shape as the
   audit script's per-cell row, so downstream analyses can guard against
   incomplete cells. This makes the Phase 3a audit script's job into a
   guard-rail rather than a forensic exercise.
3. Add a Tier-1 test that simulates the silent-drop surfaced-correctly
   pathway (mock `_call_verifier_api` to return `None` for one candidate
   and confirm the run exits non-zero with a populated `failed_items[]`).

**What it misses:**

- Nothing structural. This is the comprehensive defence-in-depth posture
  that prevents a recurrence of the May 2026 Phase 3a audit ever needing
  to be run again — every future completeness gap surfaces at the run
  level rather than three months later in a forensic sweep.

**Estimated effort:** 3–5 days, including the cardinality assertion in
both real-time and batch paths, the sidecar schema, and tests.

## Open questions

These could not be resolved from static analysis alone.

1. **Empirically, what is the modal failure mode in the 30 affected cells?**
   The gap=57 cell inspected has `parse_failures: 1147` and
   `empty_responses: 1147` (suspicious that they are exactly equal — could
   be the same 1147 individual API attempts being double-counted, or
   coincidence). A scripted sweep over the 30 cells'
   `run.meta.json:execution_stats` would let us distinguish (a) parse
   failures from malformed JSON, (b) `MAX_TOKENS` truncation, (c) safety
   blocks, (d) 429 / 5xx exceptions. **This affects which Layer-2 sub-fix
   has the highest leverage.** Recommended: a one-off diagnostic script
   that aggregates `(parse_failures, empty_responses, safety_blocks,
   retries_*)` across the 30 cells and correlates with their gap
   magnitude.

2. **Why are some cells `gap=1` and others `gap=460`?** Random concurrent
   noise should give Poisson-ish counts; gap=460 (out of 802) on
   `flash-high-image-n5/image-t0.0/verified-v1-n10` is 57.4 %, far higher
   than any other cell. Either (a) that cell ran at a different time when
   the API was unhealthy, (b) a deterministic property of the crops in
   that cell triggers a refusal or `MAX_TOKENS` cliff, or (c) the run was
   killed mid-batch and never resumed. Inspecting the cell's
   `run.meta.json` `timestamp`, `start_time` / `end_time` (if present),
   and comparing wall-time to the expected count would distinguish (a/c)
   from (b). Cannot determine from code alone.

3. **Does the batch API path have the same surfacing gap?**
   `validate_batch_results()` computes a `missing` set and the driver
   logs a warning at line 530, but never persists the missing set to
   `run.meta.json` and does not affect exit code. Inspecting an existing
   batch-run cell with a known gap (none of the 30 cells in the audit
   are confirmed batch runs from the table; would need to cross-reference
   `run.meta.json:configuration.mode` per cell) would confirm whether
   batch runs are equally vulnerable. Worth resolving because the fix
   for Layer 1 should land in both `_verify_realtime()` and
   `_verify_batch()`.

4. **Is `_store_per_item=True` always set in production?** The
   `LLMMetadataTracker._store_per_item` flag controls whether per-call
   metadata (with `parse_error` / `item_id`) is retained in the final
   `run.meta.json`. If it is ever set False (for memory reasons on big
   runs), even the per-attempt forensic trail is lost. From a quick
   read it appears to default True and is never flipped in
   `run_pv.py`, but a runtime confirmation across the 30 affected
   cells' meta files would be reassuring.

5. **Does `extract_gemini_metadata()` capture the candidate identity in
   per-call metadata?** Inspecting `lib_llm_metadata.py:extract_gemini_metadata`
   suggests `item_id` is passed in by `_call_verifier_api()` (line 866 —
   `item_id=iteration_id`), but I did not verify that the per-call
   metadata in `run.meta.json:response_metadata[]` retains the
   `iteration_id` after `log_response()` is called. If it does, the
   surfacing gap is partially mitigable from existing data — a
   post-processing script could parse `response_metadata[]`, identify
   attempts whose `parse_success=False` and which never had a
   subsequent successful attempt for the same `item_id`, and reconstruct
   `failed_items[]` retroactively. Worth checking before committing to
   Layer 1, in case the fix can be applied retroactively to the 30
   already-affected cells without re-running cleanup.

6. **Why are `parse_failures` and `empty_responses` identical (both 1147)
   in the gap=57 cell?** Suggests they may be triggered by the same
   underlying mechanism (e.g. `response.text is None` is being counted
   as both an empty response and a parse failure, or the
   `extract_gemini_metadata` logic increments both flags on the same
   event). Worth a one-line check at `lib_llm_metadata.py:710` and
   `log_response()` lines 396–399 to confirm whether they are
   double-counting or genuinely capturing two distinct events that
   happen to occur in equal number. If double-counted, the actual
   number of distinct failed attempts in that cell is 1147, not 2294 —
   which changes the assumed retry-exhaustion rate.
