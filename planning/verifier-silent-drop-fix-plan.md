# Plan: Verifier silent-drop fix (Layer 1 + Layer 2, Layer 3 optional)

**Author:** Agent 2 (planning), 2026-05-03
**Predecessor:** Agent 1 root-cause report (`reports/verifier-silent-drop-root-cause-2026-05-03.md`, commit `0808cb91`)
**Successor:** Agent 3 (implementation)

---

## 1. Scope and goals

### Problem (one paragraph, sourced from Agent 1)

Between commit `5d725930` (March 2026 dual-mode refactor) and 2026-05-03, 30 verifier cells silently dropped 835 candidates with no per-candidate failure record. The proximate cause is in `scripts/run_pv.py:_verify_realtime()` (lines 763–793): when `_call_verifier_api()` exhausts its three retries and returns `None`, the driver increments a local `failed_count` integer but never calls `metadata_tracker.log_failure(candidate_id, ...)`, never appends the candidate identity to `execution_stats.failed_items[]`, and never asserts cardinality before exit. A weaker secondary cause amplifies the rate of retry exhaustion: `lib_verifier._call_verifier_api()` has a markedly weaker retry policy than `4_detect_mounds_batch.py:process_single_tile()` — three retries vs fifteen, fixed 2/4/8 s backoff vs error-class-specific exponential with jitter, no `MAX_TOKENS` finish-reason handling, and `json.loads()` only vs the `parse_response_with_repair()` three-tier recovery pipeline.

### Layer 1 target — surfacing fix

Every retry-exhausted candidate must appear in `run.meta.json:execution_stats.failed_items[]` with its `item_id`. A post-run cardinality assertion compares `len(parsed_results)` against the expected count and emits a clear warning + non-zero exit code when a gap exists.

### Layer 2 target — retry-handling parity with the proposer pipeline

`_call_verifier_api()` ports the proposer's retry policy so fewer transient failures reach Layer 1's surfacing layer in the first place: `parse_response_with_repair()` for malformed JSON, error-class-specific backoff (429 / 503 / DeadlineExceeded), `MAX_TOKENS` retry, `_MAX_RETRIES` raised to 15.

### Layer 3 (optional, defer if Layer 1 + 2 land cleanly)

Auto-cleanup-on-gap (the driver invokes `cmd_cleanup` itself when a gap is detected); a `verifier_completeness.json` sidecar artefact; pipeline-level guard converting the Phase 3a audit into a guard-rail.

### Out of scope

- Verifier prompt changes
- Verifier model selection changes
- Consensus pipeline changes
- Recovery of the 30 historical gap-positive cells (handled by `planning/phase3a-verifier-recovery-runbook.md`, separate agent)

### Plan corrections to root-cause findings

Agent 1's report estimates Layer 1 as "~5 LoC + tests, half a day". Re-reading the code path slightly understates two surface areas the implementing agent will actually touch:

1. **`_verify_realtime()` will need `log_response()` to mark item-attempt metadata as `parse_success=False` before falling through to a missing result.** The current `log_response()` call (line 770–772) already happens for all metadata entries, including failures — that part is fine. But the `iteration_id` used by `_call_verifier_api()` (e.g. `cand_0042_iter1`) does not match the `item_id` the cardinality check expects (`candidate_00042` or `candidate_00042_iter1`). The Layer 1 fix needs to pick **one** id convention for `log_failure()` — recommended: `_candidate_result_key(cand, iterations)` so `failed_items[]` IDs align with `probabilities.json` keys (and with the missing-set computation in `_compute_missing_candidates`). This is a deliberate design decision the implementer should not have to make.

2. **`verify_candidate_realtime()` returns `({}, [])` when `build_candidate_content()` raises `FileNotFoundError` (line 739–741)** — there is no retry, no metadata, and no candidate identity in the metadata list. The Layer 1 fix in `run_pv.py` will catch this case (empty results dict) generically, but the failure reason will read "no result returned" rather than "crop file missing". For Layer 1 we accept this cosmetic loss; for Layer 2 the implementer should propagate the reason via the metadata list (one extra `LLMResponseMetadata` entry with `parse_error="CROP_FILE_MISSING: <path>"`).

3. **`_verify_batch()` already computes the `missing` set at line 526–533 via `validate_batch_results()`** but only logs a warning. Layer 1 must also apply there: emit `log_failure()` for each `missing` ID, and let `_write_verification_outputs()` do the cardinality assertion uniformly across both modes. This is briefly mentioned in Agent 1's "Touch points" but easy to overlook.

Realistically Layer 1 is ~30–50 LoC of production code (not 5) and ~80–120 LoC of tests. Still half a day, just budgeting more carefully than Agent 1's headline figure.

---

## 2. File-by-file change plan

### 2.1 `scripts/run_pv.py`

**Function `_verify_realtime()` (lines 633–820)**

*Modified:* the `as_completed()` loop body (lines 763–793).

After `cand_results, metadata_list = future.result()` (line 767), introduce these branches:

- Resolve the canonical key once: `result_key = _candidate_result_key(cand, iterations)` (where `cand = future_to_cand[future]`).
- Existing `for meta in metadata_list: metadata_tracker.log_response(...)` is preserved.
- New: if `cand_results` is truthy, call `metadata_tracker.log_success(result_key)` for symmetry with the proposer (mirrors `4_detect_mounds_batch.py:649`).
- New: if `cand_results` is falsy (empty dict), call `metadata_tracker.log_failure(result_key, _summarise_failure_reason(metadata_list))`. The helper `_summarise_failure_reason()` (new, ~10 LoC, defined alongside) walks `metadata_list` looking for the last `parse_error` and returns a string like `"BLOCKED: ..."`, `"EMPTY_RESPONSE"`, `"JSONDecodeError: ..."`, `"API error after 3 attempts: ..."`, defaulting to `"no result returned (retries exhausted)"` if `metadata_list` is empty (the `FileNotFoundError` path).
- New: in the outer `except Exception as e:` branch (line 780–786), call `metadata_tracker.log_failure(result_key, f"unhandled in driver: {e}")` after `failed_count += 1`.

*Preserved:* the incremental save loop (line 795–801), `verified_count` / `failed_count` counters (still used for the live progress log), `executor.submit()` mapping logic, `existing_results` resume merge.

**Function `_write_verification_outputs()` (lines 828–933)**

*Added:* a new helper invocation immediately after `output_dir.mkdir()` and before the `prob_path` write — call `_assert_completeness(parsed_results, manifest, iterations, mode, metadata_tracker, strict)` where `strict` is a parameter threaded through from the caller (default True; see § 5 for the `--no-strict` escape hatch).

*Added:* `_assert_completeness()` (new private helper, ~30 LoC, immediately above `_write_verification_outputs`):

- Compute `expected = {_candidate_result_key(c, iterations) for c in manifest["candidates"]}` (single-iteration) or the `_iter1`…`_iterN` set for consensus.
- Compute `actual = set(parsed_results.keys())`.
- Compute `gap = expected - actual`.
- If `gap` is empty, return silently.
- Else: log `logger.error("Completeness gap: %d candidates missing from results (mode=%s, expected=%d, actual=%d)", len(gap), mode, len(expected), len(parsed_results))`, log up to first 10 gap IDs at WARNING level, and:
  - Backfill `failed_items[]` for gap members **not already present** (defensive: in batch mode the `validate_batch_results()` path may have already logged some): `for mid in gap: metadata_tracker.log_failure(mid, "absent from results — completeness assertion")` only if `mid not in {f["item_id"] for f in metadata_tracker.stats.failed_items}`.
  - Set a sentinel in `metadata_tracker.results_summary["completeness_gap"] = {"expected": ..., "actual": ..., "missing_ids": sorted(gap)[:100]}` (truncate at 100 IDs to keep meta size sane; full list lives in `failed_items[]`).
  - If `strict` is True, the *caller* (`cmd_verify` / `_verify_realtime` / `_verify_batch`) returns 1; the helper returns the gap count.

*Modified:* `_verify_realtime()` and `_verify_batch()` should both check the return value of `_write_verification_outputs` (newly returns an int gap count) and propagate it: `return 1 if gap_count > 0 and strict else 0`.

**Function `_verify_batch()` (lines 409–564)**

*Modified:* in the existing `if missing:` branch (line 529), call `metadata_tracker.log_failure(...)` for each missing ID before logging the warning, using a fresh `LLMMetadataTracker` instance — but `_verify_batch` currently constructs `batch_metadata` *after* the missing check (line 542–550). Re-order: hoist `LLMMetadataTracker` instantiation up to immediately after `manifest = json.load(...)` so it is available before the missing-set logging. Then `for mid in missing: batch_metadata.log_failure(mid, "absent from batch response")`.

**Function `cmd_cleanup()` (lines 259–401)**

*Modified:* per-attempt cleanup loop should propagate `strict=False` to its inner `_verify_realtime()` call. Rationale: the cleanup driver itself owns the cardinality check (via `_compute_missing_candidates()` after the loop, line 367) and reports `still_missing_ids` in the `cleanup_history` audit trail; if the inner call also asserted strict, every cleanup invocation that did not fully recover would early-exit without writing the audit history. Thread `strict` through the `_verify_realtime` signature; `cmd_cleanup` passes False; `cmd_verify` passes the value of the new `--no-strict` CLI flag (default True i.e. strict).

*Modified:* in the `final_missing` block (line 370), after the existing `cleanup_history` append, also call `_log_cleanup_failures_to_meta(args.verified_dir, final_missing)` — a new helper that loads `run.meta.json`, ensures each ID in `final_missing` appears in `execution_stats.failed_items[]` (idempotent — does not duplicate), and writes back. This addresses the "should `run_pv.py cleanup` itself be updated?" question in § 4 below: yes.

**CLI parser (`_build_parser`, lines 1005+, particularly the `verify_parser` block lines 1054–1099)**

*Added:* `verify_parser.add_argument("--no-strict", dest="strict", action="store_false", default=True, help="Allow incomplete results without exit-1; the default fails on completeness gaps.")`

*Added:* `cmd_verify` (line 132) reads `args.strict` and passes it down through `_verify_realtime` / `_verify_batch`.

**New helpers added to `run_pv.py`**

```python
def _summarise_failure_reason(metadata_list: list) -> str: ...
def _assert_completeness(parsed_results, manifest, iterations, mode,
                         metadata_tracker, strict) -> int: ...
def _log_cleanup_failures_to_meta(verified_dir: Path, missing: set[str]) -> None: ...
```

All three are private (`_`-prefixed), tier-1-tested, and live in the helper region around line 567–626.

---

### 2.2 `scripts/lib_verifier.py`

**Module-level constants (line 72–74)**

*Modified:*

```python
_MAX_RETRIES = 15  # was 3 — match proposer (4_detect_mounds_batch.py)
_BASE_WAIT_SECONDS = 30  # new — base for exponential backoff with jitter
_MAX_BACKOFF_SECONDS = 300  # new — match proposer cap
_RETRY_BACKOFF_SECONDS = [2, 4, 8]  # PRESERVED for back-compat, deprecated;
                                    # used only by code paths not yet ported
```

**Function `_call_verifier_api()` (lines 820–964)**

*Modified:* the retry loop is restructured to mirror `4_detect_mounds_batch.py:process_single_tile()` (lines 363–544). Key changes:

1. *Add* `import random` at module top.
2. *Add* a `metadata_tracker` parameter (currently the function only mutates `metadata_list`; for parity with the proposer it needs to call `log_retry()` per attempt). Updated signature:

   ```python
   def _call_verifier_api(
       client, model_name, content, gen_config, iteration_id,
       metadata_list, metadata_tracker=None,  # NEW (optional for back-compat)
   ) -> dict | None:
   ```

   Default `None` so callers that have not been updated still work; `verify_candidate_realtime()` passes the tracker through (see below).

3. *Add* `MAX_TOKENS` finish-reason check (mirrors `4_detect_mounds_batch.py:421–437`). When `finish_reason` contains `"MAX"` or `"TOKEN"`, log a retry via `metadata_tracker.log_retry(iteration_id, attempt, reason, "other")` and `continue` to the next loop iteration after a 5 s sleep. This explicitly handles the deterministic-truncation case Agent 1 identified as taxonomy mode #9.
4. *Replace* the bare `except Exception as e:` block (line 938–962) with the proposer's error-class-specific branch:
   - `"429" in error_str or "ResourceExhausted"` → `error_type="rate_limit"`, `backoff = min(base_wait * 2**attempt + random.uniform(0, base_wait), MAX_BACKOFF_SECONDS)`.
   - `"503" in error_str or "InternalServerError"` → `error_type="server_error"`, `backoff = 30 + random.uniform(0, 10)`.
   - `"DeadlineExceeded"` → `error_type="timeout"`, same 30 ± 10 s.
   - `"404" in error_str and "models/"` → fatal, return None immediately (matches proposer).
   - else → `error_type="other"`, 20 ± 10 s for first two attempts, then break.
   - Each branch calls `metadata_tracker.log_retry(iteration_id, attempt, error_str, error_type)` if tracker present.
5. *Replace* the `json.loads(txt)` call (line 904) with `parse_response_with_repair(txt)`. Update the import block at the top of the file: `from scripts.lib_batch_api import _encode_image_base64, _mime_type_for, parse_response_with_repair`. The `_unwrap_verdict_payload(data)` call (line 905) is preserved unchanged — it operates on the parsed object regardless of which parser produced it.
6. *Preserve:* the safety-block / empty-response immediate-return paths (lines 875–895). These are deterministic and should not retry, exactly as the current code does.
7. *Add* a final `metadata_tracker.log_response(iteration_id, response_metadata)` mirror call site is *not* needed here — the existing `metadata_list.append(response_metadata)` is consumed by `run_pv.py`'s `for meta in metadata_list: log_response(...)` (line 770–772). Preserve current contract.

**Function `verify_candidate_realtime()` (lines 688–768)**

*Modified:* signature gains `metadata_tracker` parameter (default None for back-compat). Pass it through to each `_call_verifier_api()` call (line 756–763). Caller in `run_pv.py:_verify_realtime` (line 749) passes `metadata_tracker=metadata_tracker`.

*Preserved:* the `FileNotFoundError` catch (lines 739–741). Add — for Layer 2 — a synthetic metadata entry on this branch:

```python
except FileNotFoundError as e:
    logger.warning("Skipping candidate %s: %s", cid, e)
    from scripts.lib_llm_metadata import LLMResponseMetadata, LLMProvider
    md = LLMResponseMetadata(
        provider=LLMProvider.GEMINI.value,
        model_requested="<crop-missing>",
        item_id=f"cand_{cid:04d}_iter1",
        attempt=1,
        parse_success=False,
        parse_error=f"CROP_FILE_MISSING: {e}",
        # ...other required fields per dataclass
    )
    return {}, [md]
```

This means the `_summarise_failure_reason()` helper in `run_pv.py` can produce a meaningful failure reason for crop-missing rather than the generic "no result returned".

---

### 2.3 `scripts/lib_llm_metadata.py`

*No code changes required.* The existing `log_failure(item_id, reason)` signature (line 411–419) is exactly what we need. Reason type is `str`, item_id is a flexible string — both compatible with `_candidate_result_key()` outputs (`candidate_00042` or `candidate_00042_iter1`).

*Preserved:* the merge_meta defensive cleanup in lines 1145–1175 (commit `7f328c62`) — its logic of dropping `failed_items` whose IDs are also in `completed_items` is precisely what we want, and the new code paths in `run_pv.py` will produce data that respects that invariant.

*Preserved:* `_store_per_item` flag (line 305–306). Layer 1 + 2 do not touch per-item storage policy.

---

### 2.4 New test files

**`tests/test_run_pv_completeness.py`** (new file, ~250 LoC, all tier-1)

Covers Layer 1 surfacing. See § 3 for the test list. Imports `_verify_realtime`, `_assert_completeness`, `_summarise_failure_reason`, `_log_cleanup_failures_to_meta`, the existing `_make_manifest` / `_make_args` fixtures from `test_run_pv.py` (factor those into `tests/conftest.py` if convenient, or duplicate — the new file is intentionally separate from `test_run_pv.py` to keep `cmd_cleanup` tests untouched).

**Extension to `tests/test_lib_verifier.py`** (new test class `TestCallVerifierApi`, append to file, ~150 LoC, tier-1)

Covers Layer 2 retry parity. Uses `unittest.mock.MagicMock` for `client.models.generate_content` to simulate transient failures — the `lib_verifier.py:_call_verifier_api` boundary is the right test surface.

---

## 3. Test plan

All tests are tier-1 (critical path; the bug suppressed evaluation-blocking data).

### 3.1 Layer 1 — surfacing tests (in `tests/test_run_pv_completeness.py`)

| # | Test name | Asserts |
|---|---|---|
| L1-A | `test_verify_realtime_logs_failure_on_empty_results` | Mock `verify_candidate_realtime` to return `({}, [])` for one of three candidates. After `_verify_realtime` returns, `metadata_tracker.stats.failed_items` contains an entry with `item_id == "candidate_00001"` (or the canonical key for that candidate). |
| L1-B | `test_verify_realtime_logs_success_on_results` | Mock the worker to return populated results. Assert `metadata_tracker.stats.completed_items` lists all candidate keys. (Symmetry test, mirrors proposer.) |
| L1-C | `test_verify_realtime_logs_failure_on_worker_exception` | Mock `verify_candidate_realtime` to raise `RuntimeError`. Assert `failed_items[]` has an entry whose `reason` includes `"unhandled in driver"` and `"RuntimeError"`. |
| L1-D | `test_assert_completeness_no_gap` | Build a manifest with 5 candidates and a parsed_results dict with all 5; call `_assert_completeness` with strict=True; returns 0; no warnings logged (use `caplog`); no entries added to failed_items. |
| L1-E | `test_assert_completeness_gap_strict` | Build a manifest of 5 candidates and a parsed_results dict with only 3; call `_assert_completeness(strict=True)`; returns 2; `failed_items[]` gains 2 entries; `results_summary["completeness_gap"]` is populated. |
| L1-F | `test_assert_completeness_gap_already_logged_no_dup` | Pre-populate `failed_items[]` with one of the missing IDs; call `_assert_completeness`; the existing entry is preserved (not duplicated), only the second missing ID is added. |
| L1-G | `test_assert_completeness_consensus_iterations` | Manifest with 3 candidates × 3 iterations = 9 expected keys (`candidate_00001_iter1`…`candidate_00003_iter3`); parsed_results has 7; assert gap of 2 with the correct iteration suffixes. |
| L1-H | `test_verify_realtime_strict_returns_nonzero_on_gap` | End-to-end through `_verify_realtime`: mock the worker so 1 of 5 candidates yields empty results; with strict=True, `_verify_realtime` returns 1; with strict=False, returns 0; in both cases `failed_items[]` is populated. |
| L1-I | `test_verify_realtime_writes_failed_items_to_meta` | After a `_verify_realtime` run with one failure, load `run.meta.json` from disk; assert `execution_stats.failed_items[0]["item_id"] == "candidate_00001"`. End-to-end through the file-write boundary. |
| L1-J | `test_summarise_failure_reason_extracts_parse_error` | Pass a `metadata_list` with a final entry whose `parse_error == "JSONDecodeError: Expecting value"`; helper returns a string containing `"JSONDecodeError"`. |
| L1-K | `test_summarise_failure_reason_handles_empty_list` | Pass `[]` (the `FileNotFoundError` early-return path); helper returns `"no result returned (retries exhausted)"`. |
| L1-L | `test_log_cleanup_failures_idempotent` | Pre-populate `run.meta.json` with `failed_items: [{"item_id": "candidate_00003"}]`; call `_log_cleanup_failures_to_meta(verified_dir, {"candidate_00003", "candidate_00007"})`; verify only one new entry added (for `candidate_00007`); existing entry untouched. |
| L1-M | `test_cmd_cleanup_propagates_strict_false` | Mock `_verify_realtime` with assert-on-call to confirm `strict=False` is in the call kwargs. Prevents regression where someone tightens cleanup to strict=True and breaks the audit-trail flow. |
| L1-N | `test_no_strict_cli_flag_default` | Build a parser, parse `["verify", "--crops-dir", ".", "--verifier-config", "x.json", "--output-dir", "."]`; assert `args.strict is True`. Then parse with `--no-strict`; assert `args.strict is False`. |

### 3.2 Layer 2 — retry parity tests (append to `tests/test_lib_verifier.py`)

| # | Test name | Asserts |
|---|---|---|
| L2-A | `test_call_verifier_api_429_retries_with_jitter_backoff` | Mock `client.models.generate_content` to raise `Exception("429 ResourceExhausted")` twice then return a valid response. Assert `_call_verifier_api` returns the parsed dict; mock called 3×; sleep was called with values that respect the jittered exponential backoff bounds (use `unittest.mock.patch("time.sleep")` and check call args). |
| L2-B | `test_call_verifier_api_503_uses_30s_backoff` | Mock raises `Exception("503 InternalServerError")` once then succeeds. Assert sleep called with value in range `[30, 40]`. |
| L2-C | `test_call_verifier_api_deadline_uses_30s_backoff` | Mock raises `Exception("DeadlineExceeded")`. Same backoff range. |
| L2-D | `test_call_verifier_api_404_model_is_fatal` | Mock raises `Exception("404 models/foo not found")`. Assert returns None on first attempt without retry. |
| L2-E | `test_call_verifier_api_max_tokens_retries` | Mock returns a response whose `candidates[0].finish_reason == "MAX_TOKENS"` once then a STOP response with valid JSON. Assert returns the parsed dict; the metadata tracker received a `log_retry(error_type="other")` call with reason containing "MAX_TOKENS". |
| L2-F | `test_call_verifier_api_parse_repair_recovers_trailing_comma` | Mock returns a response whose `text` is `'{"mound_probability": 0.7, "reasoning": "ok",}'` (trailing comma — would fail strict json.loads). Assert returns `{"mound_probability": 0.7, ...}` — `parse_response_with_repair` Tier 1 caught it. |
| L2-G | `test_call_verifier_api_parse_repair_recovers_extra_data` | Mock returns `'{"mound_probability": 0.5, "reasoning": "ok"}\nextra prose'`. Assert returns parsed dict — Tier 3 caught it. |
| L2-H | `test_call_verifier_api_parse_repair_exhausts_retries_returns_none` | Mock returns garbage that none of the three tiers can repair. Assert returns None after `_MAX_RETRIES` attempts. |
| L2-I | `test_call_verifier_api_safety_block_returns_none_immediately` | Mock returns a response where `response.text` raises `ValueError("BLOCKED: harm")`. Assert returns None on attempt 1 — no retry. (Regression guard for the existing deterministic-no-retry contract.) |
| L2-J | `test_call_verifier_api_max_retries_respects_constant` | Mock raises `Exception("429")` continuously. Assert returns None after exactly `_MAX_RETRIES` (15) attempts. |
| L2-K | `test_call_verifier_api_logs_retry_per_attempt_with_error_type` | Mock raises 429 twice, 503 once, then succeeds. Assert `metadata_tracker.log_retry` was called 3× with error_types `["rate_limit", "rate_limit", "server_error"]` in order. |

### 3.3 Regression / fixture against the gap=57 cell shape

| # | Test name | Asserts |
|---|---|---|
| L1-R | `test_regression_flash_high_text_gap57_shape` | Construct a fixture where `_verify_realtime` runs against a 5-candidate manifest and the worker returns `({}, [LLMResponseMetadata(parse_success=False, parse_error="EMPTY_RESPONSE", ...)])` for every candidate (mirroring the empirical cell where `parse_failures==1147, empty_responses==1147, failed_items==[]`). After the run, assert `failed_items[]` has 5 entries with reasons containing "EMPTY_RESPONSE", `completed_items[]` is empty, exit code is 1. **This is the canary the bug would have triggered if the surfacing path had existed.** |

### 3.4 Existing tests that must continue to pass

- All 56 test files / ~926 tier-1 tests run cleanly (no regressions).
- Specifically spot-check:
  - `tests/test_run_pv.py::TestCleanupSubcommand::test_cleanup_merges_in_place` — covers cleanup audit trail.
  - `tests/test_aggregate_cost_with_backups.py` — covers the Session-83 `7f05f529` pre-cleanup-backup path.
  - `tests/test_clean_meta_failed_items.py` — covers the merge_meta defensive cleanup `7f328c62`.
  - `tests/test_lib_verifier.py::TestUnwrapVerdictPayload` — covers `_unwrap_verdict_payload`, which Layer 2 keeps unchanged.

---

## 4. Migration / data-state considerations

- **No migration of historical `outputs/**/run.meta.json` files.** The 30 cells with `failed_items: []` reflect the broken state at write time; the recovery campaign (separate agent, `planning/phase3a-verifier-recovery-runbook.md`) populates the missing candidates by re-running `cmd_cleanup`. The new `_log_cleanup_failures_to_meta` helper means a re-run cleanup will also populate the meta correctly.
- **`run_pv.py cleanup` itself updated:** yes — `cmd_cleanup` calls `_log_cleanup_failures_to_meta(verified_dir, final_missing)` after the cleanup loop, so any persistent gap appears in `failed_items[]` with reason `"absent after cleanup max_attempts"`. This is the small bonus tidy-up the brief asked about.
- **Downstream consumers of `failed_items[]`:**
  - `scripts/clean_meta_failed_items.py` — already expects `failed_items[]` to be a list of `{"item_id", "reason", "timestamp"}` dicts (line 74 helper). New entries match this shape.
  - `scripts/merge_recovery_meta.py` — the merge logic (`lib_llm_metadata.merge_meta`, lines 1145–1175) handles the case where a freshly-populated `failed_items[]` overlaps with `completed_items[]` from a recovery run. Defensive cleanup is already in place and works.
  - `scripts/run_generalisation.py:1089` — iterates `failed_items[]` to retry. New entries are valid input.
  - `scripts/clean_meta_failed_items.py` test suite — covers the post-cleanup state we are now producing earlier in the lifecycle.
  No downstream changes required.

---

## 5. Backwards compatibility and run-resume safety

- **Cardinality check is non-destructive:** `_assert_completeness` only logs and populates `failed_items[]`. It never deletes results, never modifies crops, never overwrites prior `run.meta.json` content other than appending to `failed_items[]` and setting `results_summary["completeness_gap"]`. Cleanup is operator-explicit via `run_pv.py cleanup`.
- **Resume semantics — partial vs completed-with-gap distinction:**
  - The current `_verify_realtime()` already supports resume by reading existing `probabilities.json` and skipping verified candidates. If a prior run was interrupted at, say, 60 % completion, the second run will see only the remaining 40 % in `candidates`, run them, and then call `_assert_completeness` against the manifest's full list. The merged result set should be complete; if it is not, `_assert_completeness` correctly flags the residual gap.
  - **Sentinel decision:** we do not need a separate "in-progress" sentinel file. The combination of (a) `probabilities.json` existing as the canonical persisted state, and (b) the manifest-vs-results cardinality check at the end of every `_verify_realtime()` call, gives us correct semantics: an interrupted run produces a partial probabilities.json with no run.meta.json (the latter is only written at the end of `_write_verification_outputs`); a re-run resumes from probabilities.json, completes the remainder, and writes run.meta.json with `failed_items[]` populated for any genuinely-failed candidates. There is no ambiguity that a sentinel would resolve.
- **`--no-strict` escape hatch:**
  - Default-on strict mode is the right call given the impact of the silent-drop bug. Operators (Shawn) explicitly want completeness gaps to fail loud.
  - The escape hatch covers two cases: (i) deliberate sub-corpus runs (rare — usually handled by manifest filtering instead), and (ii) the recovery campaign agent who may want to allow partial recoveries to write meta without exit-1 (although the recovery runbook should pass `strict=False` explicitly per cleanup-loop semantics).
  - Default value of the new `--no-strict` flag: `dest=strict, action="store_false", default=True`. So `args.strict` is True unless the operator explicitly opts out.

---

## 6. Order of implementation (for Agent 3)

Strict ordering — each step's tests must pass before moving on. **One commit per step or per logically-cohesive group; commit messages follow Conventional Commits.**

| # | Step | Files touched | Commit |
|---|---|---|---|
| 1 | Add `_assert_completeness()` helper + `_summarise_failure_reason()` helper to `run_pv.py`. | `scripts/run_pv.py` | `feat(run_pv): add completeness-assertion helper for verifier results` |
| 2 | Wire `log_failure` / `log_success` calls into `_verify_realtime()` `as_completed` loop. | `scripts/run_pv.py` | `fix(run_pv): record per-candidate verifier failures via metadata_tracker` |
| 3 | Wire `_assert_completeness` into `_write_verification_outputs`; add `--no-strict` CLI flag; thread `strict` through callers; add `_log_cleanup_failures_to_meta` to `cmd_cleanup`. | `scripts/run_pv.py` | `fix(run_pv): assert verifier completeness before exit; add --no-strict opt-out` |
| 4 | Tier-1 tests for Layer 1 (new file `tests/test_run_pv_completeness.py`). | `tests/test_run_pv_completeness.py` | `test(run_pv): tier-1 coverage for completeness assertion + failure logging` |
| 5 | Run `pytest -m tier1` — confirm green; spot-check the existing `test_run_pv.py` and `test_clean_meta_failed_items.py` suites. | (verification only) | (no commit; this is gate to next step) |
| 6 | Port `parse_response_with_repair` into `_call_verifier_api` (replace `json.loads`); update import. | `scripts/lib_verifier.py` | `fix(lib_verifier): use parse_response_with_repair to recover malformed JSON` |
| 7 | Restructure `_call_verifier_api` retry loop with error-class branches (429 / 503 / DeadlineExceeded / 404 / other), `MAX_TOKENS` finish-reason check, raised `_MAX_RETRIES` to 15. Thread `metadata_tracker` parameter through `verify_candidate_realtime` and the call sites in `run_pv.py`. | `scripts/lib_verifier.py`, `scripts/run_pv.py` | `fix(lib_verifier): mirror proposer retry policy for parity (15 retries, error-class backoff, MAX_TOKENS handling)` |
| 8 | Tier-1 tests for Layer 2 (extend `tests/test_lib_verifier.py`). | `tests/test_lib_verifier.py` | `test(lib_verifier): tier-1 coverage for retry parity (429/503/DeadlineExceeded/MAX_TOKENS/parse-repair)` |
| 9 | Run `pytest -m tier1` — full suite green; sample `pytest -m tier2` if time permits. | (verification only) | (no commit) |
| 10 | Run `/audit` skill on the four modified files (`scripts/run_pv.py`, `scripts/lib_verifier.py`, `tests/test_run_pv_completeness.py`, `tests/test_lib_verifier.py`). Address any blocker findings. | (audit only) | (commit only if audit suggests fixes) |
| 11 | (Optional, scope-permitting) Layer 3: auto-cleanup-on-gap + `verifier_completeness.json` sidecar. | `scripts/run_pv.py` (+/- new module) | `feat(run_pv): auto-cleanup-on-gap and completeness sidecar` |

**Crucial:** do not commit a partial Layer 1 (e.g. step 2 without step 3) — the cardinality assertion is the load-bearing user-visible change. Steps 1–4 must all land before tests reflect the full Layer 1 contract.

---

## 7. Effort estimate

| Layer | Best | Expected | Worst |
|---|---|---|---|
| Layer 1 (steps 1–5) | 3 hr | 4–5 hr | 7 hr |
| Layer 2 (steps 6–9) | 5 hr | 6–8 hr | 10 hr |
| `/audit` + final tidy (step 10) | 30 min | 1 hr | 2 hr |
| **Sum (Layer 1 + 2 + audit)** | **~9 hr** | **~12 hr** | **~19 hr** |
| Layer 3 (step 11, optional) | +3 hr | +5 hr | +8 hr |

Best case = familiar codebase, no SDK gotchas, tests pass first time. Worst case = mock-finagling for `client.models.generate_content` takes a session, plus discovery of an `LLMResponseMetadata` dataclass field requirement that complicates the `FileNotFoundError`-synthetic-metadata path. Expected case (~12 hr ≈ 1.5 working days) lines up with Agent 1's Layer-1 + Layer-2 estimate of "half day + 2–3 days" for the comprehensive scope.

Layer 3 is a clear "if scope allows" — it is purely defensive (auto-cleanup-on-gap is a convenience over the existing-and-tested explicit `cmd_cleanup`), and the completeness-sidecar duplicates information already in `run.meta.json:execution_stats`.

---

## 8. Triage of Agent 1's six open questions

| # | Question | Blocking? | Disposition |
|---|---|---|---|
| 1 | Modal failure mode in the 30 cells (parse_failures, empty_responses, etc. distribution)? | **No.** | Defer to a one-off diagnostic script during the recovery campaign. The Layer-2 retry-parity port covers all classes uniformly — we do not need to know which class dominates to know the port helps. **Action:** the recovery agent (separate) can produce the distribution as a side-effect; it informs Layer-3 prioritisation but not Layer 1/2 design. |
| 2 | Why gap=1 vs gap=460? | **No.** | Defer. The 57.4 % gap on `flash-high-image-n5/image-t0.0/verified-v1-n10` is interesting (suggests a stuck batch, time-of-day API health, or a deterministic content-filter trigger), but the surfacing fix and retry parity are agnostic to the cause. **Action:** post-recovery analysis. |
| 3 | Does the batch API path have the same surfacing gap? | **Partially blocking.** | The `_verify_batch` change in § 2.1 above addresses this without needing empirical confirmation: any `missing` set computed by `validate_batch_results()` is now fed into `log_failure` and the cardinality assertion. **No explicit defer needed — handled by the plan as designed.** |
| 4 | Is `_store_per_item=True` always set in production? | **No.** | Defer. Static read of `lib_llm_metadata.py:262–306` shows the default is True and `run_pv.py` never flips it. **Action:** add a one-line assertion in `LLMMetadataTracker.__init__` if paranoid; the implementation agent may include this as a defensive guard but it is not blocking. |
| 5 | Does `extract_gemini_metadata()` retain `iteration_id` in `response_metadata[]`? | **No.** | Defer. The `_summarise_failure_reason()` helper in `run_pv.py` walks `metadata_list` (the ephemeral, pre-`log_response` list) — we do not depend on the persisted `response_metadata[]` to reconstruct anything. **Action:** if a future agent wants to retroactively populate `failed_items[]` for the 30 historical cells from existing `response_metadata[]`, they should answer this question first. The recovery campaign avoids this need by simply re-running cleanup. |
| 6 | Why are `parse_failures==empty_responses==1147`? | **No.** | Defer to a one-line check at `lib_llm_metadata.py:710` and `log_response()` lines 396–399. **Action:** the implementing agent may incidentally answer this while reading `extract_gemini_metadata`; if so, it goes in a follow-up doc note, not the code change. |

**Bottom line:** zero open questions block Layer 1 + 2 implementation. Question 3 was concerning but the plan's `_verify_batch` change closes it without empirical confirmation.

---

## 9. Commit and review plan

- **Commit cadence:** as per the table in § 6 — one commit per step, with conventional-commits prefixes (`feat`, `fix`, `test`, `docs`). Total expected: 7–8 commits across Layer 1 + 2.
- **Each commit must pass `pytest -m tier1`.** No `--no-verify`, no `--amend`. Hooks must succeed; on failure, fix the issue and create a *new* commit.
- **Co-author line on every commit:** `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`
- **`/audit` skill** (Step 10): the implementing agent runs `/audit` against `scripts/run_pv.py`, `scripts/lib_verifier.py`, `tests/test_run_pv_completeness.py`, and the new tests in `tests/test_lib_verifier.py`. Any "blocker" findings get fixed in a new commit before declaring done. Any "advisory" findings get logged as TODO comments referencing this plan.
- **Do not push.** Shawn pushes at session boundaries.
- **Final state confirmation:** before declaring done, the implementing agent runs:
  - `pytest -m tier1` (must pass)
  - `pytest tests/test_run_pv.py tests/test_run_pv_completeness.py tests/test_lib_verifier.py tests/test_clean_meta_failed_items.py tests/test_aggregate_cost_with_backups.py -v` (focused regression spot-check)
  - `git log --oneline -10` (visual confirmation of commit list)
  - Reports back the test count, commit hashes, and any open issues.

---

## Appendix A — concrete change sketches (for the implementing agent only; not contracts)

### A.1 `_summarise_failure_reason` (new in `run_pv.py`)

```python
def _summarise_failure_reason(metadata_list: list) -> str:
    """Summarise the terminal failure reason from a metadata list.

    Walks back-to-front for the most recent parse_error or error_type
    annotation. Returns a generic fallback when metadata_list is empty
    (e.g. the FileNotFoundError early-return path before lib_verifier
    Layer-2 changes propagate a synthetic metadata entry).
    """
    for meta in reversed(metadata_list):
        err = getattr(meta, "parse_error", None)
        if err:
            return str(err)
        err_type = getattr(meta, "error_type", None)
        if err_type:
            return f"{err_type}: retries exhausted"
    return "no result returned (retries exhausted)"
```

### A.2 `_assert_completeness` (new in `run_pv.py`)

```python
def _assert_completeness(
    parsed_results: dict[str, dict],
    manifest: dict,
    iterations: int,
    mode: str,
    metadata_tracker,
    strict: bool,
) -> int:
    """Compare results against the manifest; backfill failed_items[] on gap.

    Returns the gap count (0 if complete). Idempotent — does not duplicate
    failed_items entries.
    """
    expected = set()
    for cand in manifest.get("candidates", []):
        cid = cand["candidate_id"]
        if iterations > 1:
            for i in range(1, iterations + 1):
                expected.add(f"candidate_{cid:05d}_iter{i}")
        else:
            expected.add(f"candidate_{cid:05d}")

    actual = set(parsed_results.keys())
    gap = expected - actual

    if not gap:
        return 0

    logger.error(
        "Completeness gap: %d candidates missing from results "
        "(mode=%s, expected=%d, actual=%d)",
        len(gap), mode, len(expected), len(parsed_results),
    )
    sample = sorted(gap)[:10]
    logger.warning("First %d missing IDs: %s", len(sample), sample)

    if metadata_tracker is not None:
        existing_ids = {f["item_id"] for f in metadata_tracker.stats.failed_items}
        for mid in sorted(gap):
            if mid not in existing_ids:
                metadata_tracker.log_failure(
                    mid, "absent from results — completeness assertion",
                )
        metadata_tracker.results_summary["completeness_gap"] = {
            "expected": len(expected),
            "actual": len(parsed_results),
            "missing_count": len(gap),
            "missing_ids_sample": sorted(gap)[:100],
        }

    if strict:
        logger.error(
            "Strict mode: returning non-zero exit code due to "
            "completeness gap. Run `run_pv.py cleanup` to retry "
            "missing candidates, or pass --no-strict to suppress.",
        )

    return len(gap)
```

(The implementer can refine signatures/logging; the above is illustrative.)

### A.3 `_call_verifier_api` retry-loop skeleton (Layer 2)

The implementer should mirror `4_detect_mounds_batch.py:363–544` near-line-for-line, with these differences:

- No TPM governor (verifier path does not use one currently — leave this future-work).
- Use `parse_response_with_repair` rather than the inline trailing-comma regex.
- Wrap the parsed object with `_unwrap_verdict_payload` (preserved from current).
- Preserve the safety-block / empty-response immediate-return paths.
- Pass `metadata_tracker.log_retry(iteration_id, attempt, reason, error_type)` per attempt for parity.
