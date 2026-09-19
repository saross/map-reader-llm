# Code audit — Files API storage preflight and the 2x2 test family

> **Last revised**: 2026-09-20 (original publication). See [§ Changelog](#changelog) for revision history.

Audit of everything under `scripts/` and `tests/` changed since the previous
code audit, run under the project's `/audit` protocol
(`~/.claude/commands/audit.md`): two orthogonal lenses in fresh context —
implementation correctness and test adequacy — followed by adjudication,
fixes, and a re-check of the fixes.

## 1. Scope

Previous audit landed 2026-09-19 in `154ee4908`, `f0ef437aa`, `bafb359b5`,
`03d3c04a7`, `a1aa06b09`, `c9d848586`, `69d1ed6bf`. The range audited here is
`69d1ed6bf..HEAD`, computed with:

```console
$ git log --oneline 69d1ed6bf..HEAD -- scripts/ tests/
a0f40609e test(batch): pin the file-storage preflight
935865223 fix(batch): check file storage before lodging
3aa2b36d5 fix(image55-r2): vectorised micro-F1 inside the interaction permutation
74629993f feat(image55-r2): --stage tests-2x2, the declared 2x2 family with a four-cell interaction test
4fa478fc5 feat(run_pv): polling tolerates transient errors; batch-recover folds lost jobs back in
```

Six files, 1,276 insertions, 41 deletions:

| File | Change |
|---|---|
| `scripts/lib_batch_api.py` | +308 — the storage preflight; `poll_batch_job` error tolerance |
| `scripts/run_pv.py` | +270 — preflight wiring, `batch_jobs.json` record, `batch-recover` |
| `scripts/gemini37_image_55map_r2.py` | +221 — `--stage tests-2x2`, the four-cell interaction test |
| `tests/test_file_storage_preflight.py` | +352 (new) |
| `tests/test_image_2x2_tests.py` | +90 (new) |
| `tests/test_run_pv_batch_chunking.py` | +76 |

**Out of range, checked and confirmed**: the `--campaign g3` generalisation
named in the audit brief predates the anchor — it landed in `336651e0b`
(`git log -S'--campaign' -- scripts/gemini37_image_55map_r2.py`), before
`69d1ed6bf`. It is not part of this audit.

**Read-only constraints honoured**: no Gemini API call was made; nothing
under `outputs/` or `results/` was modified. Artefacts under `results/` were
read to verify numerical claims.

## 2. Method

Per the `/audit` protocol, the change was covered twice in fresh context by
two agents asked *different* questions, neither of which could edit, commit,
or run `git checkout`/`stash`/`restore`:

- **Lens A — implementation correctness.** Does the code do what it claims?
- **Lens B — test adequacy.** Assume the implementation is wrong; would
  these tests catch it? For each test, name a concrete one-line mutation
  and run it.

The audit lead (this document) read the change independently, adjudicated
both lenses' findings — they disagreed on one substantive point, resolved in
§ 3.2 M6 — re-verified every numerical claim and every line citation at its
source before recording it, and applied the fixes.

Three mutation experiments underpin the findings. None touched the shared
working tree:

1. **Caller tracing** (lead). `preflight_file_storage` was wrapped at
   runtime with a recorder that logs its caller's frame, and the batch suite
   was run. Result: the only production caller reached was
   `lib_batch_api.run_batch_unit`; `run_pv._verify_batch` was reached by
   **no test at all**.
2. **Call-site deletion** (lead). Both call sites resolve the helper from
   the `scripts.lib_batch_api` module namespace at call time, so replacing
   the module attribute *after* the test module has bound the real function
   is exactly equivalent to deleting both calls while leaving the helper
   intact. Before the fixes this left the entire suite green; after them it
   turns exactly the two new wiring tests red and nothing else.
3. **Source mutation against a copy** (Lens B). Eighteen candidate
   mutations were applied to file copies in a scratchpad and the suite run
   against each.

**A methodological warning worth keeping.** Lens B's first mutation harness
**symlinked** `tests/` into the copied tree. Every test module here begins
`sys.path.insert(0, str(Path(__file__).resolve().parent.parent))`, and
`Path.resolve()` follows symlinks — so the tests silently imported `scripts/`
from the *real* repository and **every mutation read green**. Lens B caught
this, rebuilt with real file copies, and validated the new harness with two
sentinel mutations that must be red before trusting any result. Any future
mutation testing in this repository must copy, not symlink, and must run a
red sentinel first. A mutation harness that cannot fail is worse than none:
it certifies the suite.

## 3. Findings

Severity tally: **1 critical, 6 major, 11 minor.** Status is one of
`FIXED` (landed in this audit), `RECOMMENDED` (real, but the fix is a
judgement call that changes numbers or behaviour someone may rely on), or
`NO ACTION` (checked, working as designed).

### 3.1 Critical

#### C1 — The storage preflight's wiring was untested; deleting either call site left the suite green — `FIXED`

`scripts/run_pv.py:1038`, `scripts/lib_batch_api.py:2887`

```python
        preflight_file_storage(client, jsonl_paths, log=logger)
```

```python
            preflight_file_storage(client, [ctx.jsonl_path])
```

The guard was thoroughly unit-tested in isolation — twelve tests over the
helper — but nothing proved it was **called**. This is the surviving
mutation the audit protocol names first, and it was live. Confirmed
independently by both lenses: deleting either call left **142 of 142 tests
green** across the four batch test modules.

- `run_pv._verify_batch` was reached by no test in the suite
  (`grep -rn "_verify_batch(" tests/` → zero hits), so deleting its
  preflight call changed nothing.
- `lib_batch_api.run_batch_unit` *was* reached, but only by
  `tests/test_batch_api.py`'s tests, which pass `client=MagicMock()`.
  Iterating a `MagicMock` raises `TypeError`, so `audit_file_storage` fails,
  `_audit()` returns `None`, and the preflight returns `None` without doing
  anything. The guard was inert in every test that touched it, and no
  assertion referred to it.

**Failure scenario.** A later refactor moves the lodging loop, drops the
preflight line, and ships green. The next full-project leg reproduces the
2026-09-19 14:05 UTC incident exactly: twelve chunks, four lodged and
billing, eight lost to `429 ... file_storage_bytes` one at a time — the
failure this change existed to prevent, with a passing test suite
certifying it.

**Fix** (`ac00a3ed7`): four tests that assert the *consequence*, not a
return value — a full project uploads nothing, writes no `batch_jobs.json`
and no `probabilities.json`, and exits non-zero; `run_batch_unit` refuses
before `submit_batch_unit` is reached; a dry run never audits storage at
all; and the budget boundary is pinned on both sides. Verified red under
the call-site-deletion mutation and green without it.

### 3.2 Major

#### M1 — A `meaningful: false` row sits inside the BH family, and carries a `significant: true` verdict — `RECOMMENDED`

`scripts/gemini37_image_55map_r2.py:1407-1416`

```python
        mcc_rows.append({"test": "T5", "name": "confound check vs IM-k3", "a": labels["B1"][1],
                         "b": "IM-k3", "meaningful": k == 3,
...
        for rows in (mcc_rows, f1_rows):
            adjusted = apply_bh_correction([r["p_value"] for r in rows], q=0.05)
```

All five rows are passed to the Benjamini–Hochberg correction, including the
T5 row the code has just self-labelled `"meaningful": False` at K ≠ 3.
`reports/image-2x2-tests-declaration-2026-09-19.md:63-64` says T5 "is
meaningful only at K = 3 … at K = 1 and K = 5 it is reported for
completeness and labelled as such."

**Verified at the source**, not inferred. In
`results/image-2x2-2026-09-19/tests_2x2_K5.json`, the MCC T3 row has raw
`p = 0.0629` and `bh_adjusted_p = 0.104833`. That is `0.0629 × 5/3 =
0.10483333…` exactly; with the non-meaningful row excluded (m = 4) it would
be `0.0629 × 4/3 = 0.083867`. **m = 5 is demonstrably the denominator at
every rung.**

Two distinct consequences:

- The four meaningful tests at K = 1 and K = 5 are corrected against an
  inflated family. This direction is **conservative** — it cannot manufacture
  a finding, only suppress one — so nothing already reported as significant
  is at risk.
- The non-meaningful row itself is written out with a verdict. At K = 5 the
  F1 T5 row reads `"meaningful": false, "p_value": 0.0009,
  "bh_adjusted_p": 0.001125, "significant": true`.

**Failure scenario.** The K = 5 exploratory replicate is cited in paper text
and T5's F1 row is read as a significant confound-check result at a rung
where the IM-k3 comparator is a three-vote cell and the contrast is
meaningless by the family's own declaration.

**Not fixed, deliberately.** Changing the BH family size rewrites adjusted
p-values in three committed, citable artefacts under `results/`, which this
audit was scoped not to touch, and the declaration is genuinely ambiguous:
it fixes the family at five "at the primary rung" and calls K = 1 and K = 5
"exploratory replicates of the same family". Whether a replicate of a
five-test family has five members or four is a PI call, not an auditor's.
**Decision needed** — see § 6.

#### M2 — `--iterations` defaults to 1 in `batch-recover` and a wrong value zeroes `probabilities.json` beside a stale `consensus.json` — `RECOMMENDED`

`scripts/run_pv.py:2375` (the flag), `:1086-1092` (the key builder), `:1980`
(where the correct value is already recorded)

```python
    recover_parser.add_argument("--iterations", type=int, default=1)
```

Recovering a K = 5 consensus leg without `--iterations 5` builds
`expected_keys` with no `_iter{i}` suffix, so `validate_batch_results`
matches nothing, `parsed` is empty, and `_write_verification_outputs` writes
`probabilities.json` unconditionally with `"total_results": 0`.
`probabilities.json` is backed up first, but `consensus.json` is rewritten
only when `iterations > 1` and is never backed up — so the leg is left with
a **stale K = 5 `consensus.json` beside a zeroed `probabilities.json`**.
`strict` defaults to `True`, so the command exits 1, but only after the files
are written.

The correct value is recoverable from disk: `probabilities.json` records
`"iterations"` (`scripts/run_pv.py:1980`).

**Not fixed**: defaulting the flag from the existing artefact changes CLI
behaviour, and the alternative (refusing to book a leg where every expected
key missed) changes the finisher's contract for both callers. Both are
reasonable; the choice is the PI's.

#### M3 — A storage 429 in the lodging loop is logged as terminal but the loop keeps uploading — `RECOMMENDED`

`scripts/run_pv.py:845-871`

```python
                    "lodge either. Run audit_file_storage() to see what "
...
            failed_chunks.append(i)
            save_record()
            continue
```

The loop prints "the remaining chunks will not lodge either" and then
attempts to lodge them. The commit rationale — "the chunks already lodged
are billing" — argues against `return`/`raise`, not against `break`: the
polling loop sits *after* the lodging loop, so a `break` would still poll
and retrieve every lodged chunk while skipping the futile uploads. A
12-chunk leg that hits the cap on chunk 5 attempts seven further uploads of
~1.3 GB each.

**Not fixed**: there is a real counter-argument — a concurrent process could
free space mid-loop, so a later chunk genuinely could succeed. Either the
control flow or the log line should change; which one is a judgement call.
This path is also now unreachable in normal operation, because the preflight
fires first.

#### M4 — The 5 % safety margin is smaller than the chunk it is documented to protect against — `RECOMMENDED`

`scripts/lib_batch_api.py:182-189`

```python
FILE_STORAGE_SAFETY_MARGIN = 0.05
```

The margin is documented as head-room for the race between the audit and the
lodge: "another process may upload between the audit and the lodge".
`21_474_836_480 − int(21_474_836_480 × 0.95) = 1_073_741_824` bytes =
exactly 1 GiB. The module's own comment at `scripts/lib_batch_api.py:2880`
states a proposer chunk's JSONL is ~1.3 GB — larger than the head-room.

**Failure scenario.** Two legs run in parallel, the normal campaign pattern.
Both preflights pass at ~18.9 GiB projected; both lodge; the second hits the
429 the preflight exists to prevent.

**Not fixed**: the right margin depends on how many concurrent lodgers the PI
expects, which the code cannot know. A margin of one maximum chunk size
(≈ 7 %), or a margin expressed in chunks rather than a percentage, would
close it.

#### M5 — `cmd_batch_recover` fetched every job unguarded; one bad name discarded the whole recovery — `FIXED`

`scripts/run_pv.py:1173-1174` (before the fix)

```python
    for name in job_names:
        job = client.batches.get(name=name)
```

Job names come from `batch_jobs.json` and from repeatable `--job` flags, so
an expired, mistyped, or foreign-project name is ordinary. An exception
raised straight out of the loop, discarding the results of every job already
fetched — on the recovery path for a leg that had *already* lost data once.
The non-SUCCEEDED branch two lines below already skipped and reported; the
exception path did not.

**Failure scenario.** A twelve-chunk leg loses four chunks to a polling
storm. `batch-recover` fetches three successfully, hits a fourth name that
has aged out of the service's retention, and exits with a traceback having
recovered nothing. The operator re-runs, and the same name kills it again.

**Fix** (`248c76499`): per-job `try`/`except` that logs, counts, and
continues, with a summary of unreachable names; a recovery where nothing was
reached still returns 1 without booking an empty leg over existing outputs.
Also closed a leaked file handle on `candidate_manifest.json` in the same
function. Two tests, plus a third in `97ab0a7cb` pinning the SUCCEEDED gate.

#### M6 — A Phase-2 storage sweep can delete a concurrent verifier leg's in-flight input — `RECOMMENDED`, escalate

`scripts/run_phase2.py:1919`, `:1936`; `scripts/lib_batch_api.py`
`sweep_stale_files_safe`, `upload_jsonl`

**The lenses disagreed here and the disagreement is the finding.** Lens A
held that `run_phase2`'s sweep is safe because that path registers its
uploads; Lens B held that it is exactly the sweep the preflight docstring
forbids. Adjudicated at source, both are half right, and the combination is
worse than either:

- `sweep_stale_files_safe` deletes **any** file not in the shared registry
  and older than its five-minute grace period.
- `scripts/run_phase2.py:1605` is the **only** place in the codebase that
  calls `register_file`.
- `upload_jsonl` — which `run_pv._verify_batch`'s lodging loop and
  `submit_batch_unit` both use — contains no registration at all (verified:
  zero `register` occurrences in its body).

So `run_phase2`'s own uploads are protected, and a **concurrent verifier
leg's are not**. When `run_phase2` hits a storage 429 it classifies it as
retryable and sweeps; any verifier request JSONL uploaded more than five
minutes earlier and still feeding a running batch job is unregistered, and
is deleted.

**Failure scenario.** A Phase-2 proposer campaign and a verifier leg run
concurrently — the normal pattern, and precisely the condition under which
the project is near the storage cap in the first place. Phase 2 hits the
429, sweeps, and deletes the verifier leg's in-flight inputs. The verifier's
jobs fail server-side with no local error, and the leg reports missing
results with no explanation in its own log.

**Not fixed**: making `upload_jsonl` register means owning the deregistration
lifecycle for two more call paths, which is a design change well beyond an
audit. Two cheaper mitigations to consider: have the verifier path register
its uploads, or narrow `run_phase2`'s sweep to files it registered itself.
**Escalated** because it is a cross-process data-loss path, and because the
new preflight docstring identifies exactly this hazard as its reason for not
sweeping — while the one path that does sweep still runs.

### 3.3 Minor

#### m1 — The vectorised micro-F1 was not bitwise equal to the scalar it is compared against — `FIXED`

`scripts/gemini37_image_55map_r2.py:1211-1217` (before the fix)

```python
        f1 = np.where((tp > 0) & (denom > 0), 2.0 * tp / np.where(denom > 0, denom, 1.0), 0.0)
```

`did_test_f1` computes the observed statistic with the board's scalar
`micro_f1` and every null statistic with `_micro_f1_vec`, then compares them
with `>=`. The closed form `2·tp / (2·tp + fp + fn)` is algebraically equal
to the board's `2PR / (P + R)` but not equal in floating point.

**Measured, not asserted.** Over 20,000 random integer count triples the
closed form differs from `micro_f1` in the last ULP on **7,526**; the board's
own spelling is bitwise identical on **20,000 / 20,000** (max absolute
difference 2.22e-16).

**Failure scenario.** A permutation that reproduces the observed sums exactly
falls on the wrong side of `np.abs(null) >= abs(observed)` through nothing
but a rounding difference between two spellings of one formula. Such
permutations are vanishingly rare, so the committed K = 1/3/5 results are
unaffected at the reported precision — but the divergence was gratuitous and
the docstring claimed parity with the board.

**Fix** (`f100ed110`): use the board's arithmetic. Two tests — bitwise
identity over 5,000 triples, and the `tp == 0` zero rule including the
all-zero case that must not produce NaN.

#### m2 — Nine surviving mutations across the guard, the poller and the 2x2 tests — `FIXED`

Lens B ran eighteen candidate mutations against copies of the tree; ten
stayed green. Nine are closed in `97ab0a7cb`, each with a behavioural
assertion rather than a restatement of the source:

| Mutation that survived | Now pinned by |
|---|---|
| `is_file_storage_quota_error` reduced to the quota-id clause | a 429 naming the metric but **not** the quotaId |
| `_largest_stored_files` sorted ascending | six files, the top five named in descending order |
| `consecutive_errors = 0` reset deleted | errors, a recovery, then errors again survive a budget of two |
| default `max_consecutive_errors` raised | the default itself tolerates exactly twenty |
| `entry["state"]` hard-coded to SUCCEEDED | a job polling `JOB_STATE_EXPIRED` is recorded as expired |
| `batch-recover`'s SUCCEEDED gate removed | a FAILED job is neither fetched nor booked |
| `// max(1, iterations)` deleted | `_verify_batch` at K = 5 produces five two-candidate chunks |
| swap probability 0.5 → 0.9 | the null is centred on zero to four standard errors |
| independent mask per cell | identical rows give a null with exactly zero spread |
| `default_rng(seed)` → `default_rng(0)` | two seeds give two draws; one seed reproduces |

The quota-matcher case is the one that mattered most: the fixture 429 carried
both the metric and the quota id, so the matcher could be reduced to the
quota-id test alone and stay green — and a body naming only the metric would
then fall back to the generic "failed to lodge" line, which is the
2026-09-19 symptom the specific message exists to replace.

The centredness assertion's margin was measured across four data seeds
before landing: the observed `null_mean` sits at 0.08–0.62 of the tolerance,
against a ratio of roughly 143 for the mutation it catches.

#### m3 — `p_value` of exactly 0.0 is reported (no `(1+k)/(1+n)` convention) — `NO ACTION`

`scripts/gemini37_image_55map_r2.py:1292`, `:1335`

```python
        "p_value": float(np.mean(np.abs(null) >= abs(observed))),
```

The observed statistic is not counted into its own null distribution, so a
p-value of exactly 0 is reportable and is present in the artefacts
(`tests_2x2_K3.json`, `_K5.json`, T1/T2 on both metrics). With 10,000
permutations the honest floor is `1/10001 = 9.999e-5`.

**No action, correctly.** This is not a regression and not local: it matches
`n1_baseline_leaderboard_tiering.permutation_test_float` and
`mcc_tiering_55map.permutation_test_mcc` exactly, and the declaration (§ 4)
specifies `p = mean(|null| ≥ |observed|)`. The new code does what it claims.
Recorded here because the defect is now *visible as literal zeros* in a
citable artefact, and because changing it is a project-wide decision.

#### m4 — The `meaningful` flag is invisible in the log and schema-asymmetric — `RECOMMENDED`

`scripts/gemini37_image_55map_r2.py:1435-1442`. The operator-facing log line
prints `T5 … SIG` at K = 5 with no marker; only the JSON carries the flag.
The key is also present on T5 rows only, so every consumer must use
`.get("meaningful", True)` or risk a `KeyError`. Bundled with the M1 decision,
since both touch the same artefacts.

#### m5 — `poll_batch_job`'s error path bypasses the `max_hours` check — `NO ACTION`

`scripts/lib_batch_api.py:1120-1127`. The `continue` skips the
`elapsed >= max_seconds` check, and `time.sleep(interval_seconds)` ignores
`remaining`. The overrun is **bounded** at `max_consecutive_errors ×
interval_seconds` = 20 × 30 s = 10 minutes past the deadline, so it cannot
hang. The consequence is a misclassification: the exception that finally
propagates is the endpoint error, not `TimeoutError`, and `run_batch_unit`
distinguishes `poll_timeout:` from `poll_error:` on exactly that type, so a
leg that overran its 25 h budget is reported as a poll error.

#### m6 — The polling tolerance retries non-transient errors for ten minutes — `RECOMMENDED`

`scripts/lib_batch_api.py:1120`. `except Exception` tolerates everything —
a 404 for a bad job name, a 401/403 auth failure, or a local `AttributeError`
— retrying twenty times at 30 s before propagating. This was observed
directly: the first call-site-deletion experiment in this audit *hung* rather
than failing, because a misconfigured client was retried for ten minutes.
The new `run_batch_unit` wiring test now patches `poll_batch_job` so its own
failure mode is fast, but the underlying breadth remains. Narrowing the
tolerated set changes behaviour the change deliberately made permissive, so
it is a judgement call. Note that `poll_all_batch_jobs` has the same broad
tolerance and is *unbounded*, which is the looser of the two.

#### m7 — `run_batch_jobs` retrieves unconditionally on any terminal state — `RECOMMENDED`

`scripts/run_pv.py:874-879`. `JOB_STATE_FAILED`, `CANCELLED`, `EXPIRED` and
`PARTIALLY_SUCCEEDED` are all in `_TERMINAL_STATES`, so such a job is not
added to `failed_chunks` and its partial or empty results are concatenated
with the rest.

The consequence is **narrower than it first appears**, and the audit checked
this rather than assuming it: a FAILED job has no `dest`, so
`retrieve_batch_results` raises and the per-chunk guard catches it and does
record the chunk as lost; and at the leg level `validate_batch_results` plus
`_assert_completeness` report every missing key regardless. What is genuinely
lost is the `failed_chunks` signal itself — the "N of M batch chunks returned
nothing" alarm and the "(this rerun lost chunks)" annotation on the
`probabilities.json` backup can both be absent for a partially-succeeded
chunk. **Not fixed**: gating on `state == "JOB_STATE_SUCCEEDED"` while still
keeping a partial chunk's paid-for results is the right shape, but it changes
what `failed_chunks` means to both callers.

#### m8 — `is_file_storage_quota_error` does not walk the exception chain, and self-matches — `NO ACTION` (watch item)

`scripts/lib_batch_api.py:248-252`

```python
    text = str(exc)
    return (
        "file_storage_bytes" in text
        or FILE_STORAGE_QUOTA_ID in text
    )
```

Two genuine properties, neither exploitable today:

- **False-miss**: only `str(exc)` is inspected, not `__cause__`/`__context__`.
  It works now because `upload_jsonl` and `submit_batch_job` let the SDK
  exception propagate bare and `google.genai.APIError.__str__` embeds the
  whole response JSON. It breaks silently the moment any retry wrapper
  re-raises `from exc`.
- **False-match**: `is_file_storage_quota_error(FileStorageCapExceeded(...))`
  is `True`, because the preflight's own message contains both tokens. Not
  reachable today, but it becomes live the moment a preflight is wired into a
  path that also has this check — notably `scripts/run_phase2.py:1919`, whose
  independent `"file_storage_bytes" in err_str` test would classify a
  preflight refusal as *retryable* and start a sweep-and-retry loop against
  an exception that can never clear. See M6.

No realistic non-storage SDK exception was found that matches: other Gemini
quota metrics (`generate_content_*`, TPM/RPM) contain neither token.

#### m9 — Provenance drift on the recovery path — `RECOMMENDED`

`scripts/run_pv.py:1206`, `:1213`, `:1216`. `_finish_batch_outputs` is
documented as booking a recovered leg "exactly as a first-time one". On three
fields it does not: `--temperature` defaults to `None` where the first-time
consensus path substitutes 0.7; the model name is used raw where the
first-time path resolves it through `_resolve_model_name` (the `-preview`
fallback); and `batch_recover.recovered_rows` books total rows fetched, not
rows actually new to the leg.

#### m10 — `size_bytes=None` is never modelled in the preflight fixtures — `RECOMMENDED`

`audit_file_storage` coerces `None` to 0, so an upload still `PROCESSING`
contributes nothing to the projection — meaning the preflight under-counts
exactly when a concurrent lodge is in flight, which is the case the safety
margin exists for (M4). `tests/test_batch_api.py` pins the coercion at the
`audit_file_storage` level; no preflight test exercises it. Bundled with the
M4 margin decision.

#### m11 — Lines over the project's 100-character limit — `NO ACTION`

`scripts/run_pv.py:2367` (104), `tests/test_run_pv_batch_chunking.py:164`
(105), `tests/test_image_2x2_tests.py:33` and `:44` (102–103). `ruff check`
passes because E501 is not in the effective rule set, but `pyproject.toml`
sets `line-length = 100`. Not fixed: the protocol for this audit excludes
style refactoring.

### 3.4 Surviving mutations still open

Nine were closed in `97ab0a7cb` (see m2) and four in `ac00a3ed7` / `f100ed110`.
These remain:

| One-line change | Location | What it lets through | Why not closed |
|---|---|---|---|
| Swap the arm axis instead of the row axis | `gemini37_image_55map_r2.py:1277`, `:1328` | The wrong null for the interaction; p moved 0.107 → 0.151 on a constructed asymmetric case | Needs an asymmetric fixture with a p bound tight enough to discriminate — a brittle test. Recipe below. |
| `"meaningful": k == 3` → `True` | `:1407`, `:1411` | An exploratory T5 row presented as a finding | Blocked on the M1 decision |
| BH over the wrong family | `:1416` | Wrong FDR family size on the declared 2x2 | Blocked on the M1 decision; also needs `stage_tests_2x2` coverage |
| `np.mean(...)` → `(count+1)/(n+1)` | `:1292`, `:1335` | The p-value convention changed silently | Project-wide convention (m3) |
| Delete the storage sweep branch | `run_phase2.py:1922-1937` | Phase-2 lodging's only storage handling vanishes | Blocked on the M6 design decision |

Recipe for the axis mutation, from Lens B's measurements: a design with a
large row main effect and a small arm effect separates the two nulls — the
row-swap null gave p = 0.1067 and the arm-swap null p = 0.1510, so a bound
like `0.09 < p < 0.13` discriminates. Recorded rather than landed because a
p bound that tight is a flaky test unless the fixture is chosen carefully.

### 3.5 Untested surfaces

Not mutations but absences, both confirmed by `grep` returning zero hits:

- **`stage_tests_2x2`** — the whole assembly of Change 2 — is executed by no
  test. Untested: the T1–T5 family composition, the BH call, the `meaningful`
  flag, the truth-vector identity gates (exit 3), the missing-cell gate
  (exit 2), and the written JSON's shape. The five synthetic-tile tests cover
  `did_test_f1` / `did_test_mcc` only. Closing this needs GeoJSON fixtures
  (detections, reference, bounds) and is a piece of work in its own right.
- **`run_phase2._submit_one`** and **`sweep_stale_files_safe`** — the third
  lodging path and the sweep at the centre of M6 — have no coverage at all.

### 3.6 Cross-file issues

#### X1 — `run_phase2.py` has no preflight — `NO ACTION` on the preflight, see M6 for the sweep

`scripts/run_phase2.py:1908` calls `submit_batch_unit` directly, bypassing
`run_batch_unit` and so the new guard. It would discover the cap one chunk at
a time, exactly as the verifier leg did. It is not simply unguarded, though:
`_submit_one` retries with 10/30/60 s backoff and sweeps on a storage 429, so
it is better covered reactively and worse proactively. The hazard in that
reactive path is M6.

Its discriminator is also a hand-rolled `"file_storage_bytes" in err_str`
rather than `is_file_storage_quota_error`, so it misses the
`FileStorageBytesPerProject`-only form the new helper deliberately matches —
duplicated logic in two files with different coverage.

#### X2 — The post-sweep re-audit contradicts the documented warn-and-proceed contract — `RECOMMENDED`

`scripts/lib_batch_api.py:404`, `:438`. If the re-audit after a sweep fails,
control falls through to `raise FileStorageCapExceeded` using the
**pre-sweep** `file_count` and `stored_bytes` — after files were deleted —
contradicting the docstring's "An audit that cannot run … is a warning, not
a failure" and making the warning `_audit()` just emitted false.
**Unreachable in production**: no call site passes `sweep`. Must be fixed
before any sweep is wired in.

#### X3 — `--campaign` is meaningless for `--stage tests-2x2` — `NO ACTION`

`scripts/gemini37_image_55map_r2.py:1360`, `:1369` read both `G37` and `G3`
homes unconditionally, while `rungs` is validated against the *selected*
campaign's `RUNGS`. Harmless today (both are `(1, 3, 5)`); it would silently
mis-scope if the two diverged.

## 4. Explicitly checked, nothing found

Recorded so the absence is on the record rather than an omission.

- **Projection arithmetic (the GB float → bytes round-trip).** The claim at
  `lib_batch_api.py:374` that the power-of-two rescale round-trips exactly is
  **true for every realistic byte count**. Dividing by 2³⁰ only adjusts a
  double's exponent, so it is exact for any integer below 2⁵³ (≈ 8 PiB);
  verified for 0, 1, 12,345, 21,474,836,479, 2⁵³−1 (all exact) and 2⁵³+1
  (first failure). `FILE_STORAGE_BUDGET_BYTES` = 20,401,094,656 = exactly
  19 GiB with no float error, and `1.0 - 0.05 == 0.95` holds in IEEE-754.
- **Files API pagination.** `audit_file_storage` iterates
  `client.files.list()`. Confirmed against the installed SDK
  (google-genai 1.73.1) that `Pager.__next__` auto-fetches subsequent pages,
  so the audit cannot silently undercount a project holding more files than
  one page — which would have been a silent hole in the guard.
- **Can the preflight fire after a partial upload?** No, at any call site.
  `run_pv.py:1038` precedes `run_batch_jobs`, which performs every upload;
  `lib_batch_api.py:2887` precedes `submit_batch_unit`, whose first statement
  is `upload_jsonl`. `run_batch_unit` is called serially (one production
  caller, `4_detect_mounds_batch.py:1672`), and chunk *k*'s preflight
  re-audits, so it correctly includes chunks 1…k−1.
- **`files.list()` raising.** Warn-and-proceed is honoured on every reachable
  path; `_largest_stored_files` returns `[]`; no caller reads the `None`
  return. The one exception is X2, which is unreachable.
- **Dry runs and resume.** `run_batch_unit`'s `dry_run` early return precedes
  the preflight, and the `resume_job_name` branch skips it — both correct,
  and the dry-run case is now pinned by test.
- **The `sweep` hook.** The docstring's claim that no production call site
  passes one is true: `grep -rn "preflight_file_storage" scripts/` returns
  two production calls, neither passing `sweep=`.
- **The T4 interaction test.** The construction is correct and matches the
  declaration statement for statement. A probability-0.5 per-tile mask swaps
  the `(A1, A2)` pair **wholesale** with `(B1, B2)`; all four permuted cells
  are read from the originals into a separate dict, so there is no aliasing.
  Under the complement mask, `D(M′) = −D(M)`, so the null is exactly
  symmetric about zero and a pure row main effect cancels in the
  difference-in-differences — the test is if anything conservative, not
  anti-conservative, when a main effect is present. Confirmed empirically:
  `null_mean` is −0.00013 to +0.00001 across all six committed cells. The
  `_PERM_CHUNK = 1000` chunking was verified bit-identical to a single
  10,000-row draw. `tile_vectors` returns `dtype=bool`, so `&` and `~` in
  `mcc_of` are boolean, not integer bitwise. The statistic's sign and the
  `>=` in its p-value comparison are pinned: negating the statistic,
  negating only the observed, and turning the difference-in-differences into
  a sum are all caught by the existing tests.
- **The BH implementation.** `apply_fdr_correction.apply_bh_correction` is
  correct: ascending sort, 1-based ranks, `p·m/rank`, reverse cumulative
  minimum for monotonicity, capped at 1.0, original order restored. Ties are
  handled correctly. Verified against the live artefact: `tests_2x2_K5.json`
  MCC T4 raw 0.4221 would be 0.5276 unadjusted and is reported as 0.4402 —
  exactly T5's rank-5 value carried back by the cummin. The defect is in what
  is passed in (M1), not in the function.
- **Watcher rules.** `poll_batch_job` waits on a terminal **state**
  (`_TERMINAL_STATES`), not a success string, which is the contract
  `docs/agent-guidance.md` prescribes. No `pgrep -f` in any changed file. A
  dead job returns `JOB_STATE_FAILED` rather than raising, so the new
  tolerance cannot mistake dead for live. Partial results cannot pass as
  complete at the leg level: every missing key is logged as a
  `failed_items[]` entry and `_assert_completeness` gates the exit code. The
  narrower `failed_chunks` gap is m7.
- **`submit_error` handling downstream.** `4_detect_mounds_batch.py:1693`
  sets `chunk_failed`, counts the chunk's tiles as failed, and withholds the
  merge, so a preflight refusal cannot silently drop units from a resumed run.
- **Fixture shape.** `google.genai.types.File.size_bytes` is `Optional[int]`
  and `.name` is `Optional[str]`, so the fakes' ints and strs match the SDK
  and the existing `audit_file_storage` mocks. The one un-modelled case is
  m10.
- **Security.** The error message prints Files API **resource names** only,
  never `display_name`, file contents, or the API key. No injection, path
  traversal, or credential surface in any changed line.
- **UK/Australian English.** Clean. Every added line across the range was
  grepped for the usual American forms; zero hits.
- **Tier markers.** Both new test modules carry `pytestmark =
  pytest.mark.tier1`; `-m "not tier1 and not tier2"` collects zero across the
  three files.
- **Index alignment.** `record["chunks"][i]` in the polling loop is correctly
  aligned: an entry is appended for every chunk including lodging failures,
  so index *i* always addresses chunk *i*. `failed_chunks` cannot contain
  duplicates.

## 5. Research-calibration note (not a code defect)

Flagged under `docs/agent-guidance.md` § Research Finding Calibration.

The T4 interaction effect declines monotonically with K and loses
significance by the K = 5 replicate:

| Rung | Status | MCC *d* | MCC p (BH) | F1 *d* | F1 p (BH) |
|---|---|---|---|---|---|
| K = 1 | exploratory | +0.0327 | 0.0000 (0.0000) | +0.0262 | 0.0000 (0.0000) |
| K = 3 | **primary** | +0.0170 | 0.0031 (0.0052) | +0.0071 | 0.0154 (0.0192) |
| K = 5 | exploratory | +0.0043 | 0.4221 (0.4402) | +0.0011 | 0.6710 (0.6710) |

The pattern is coherent rather than contradictory — more consensus votes
wash out the proposer-by-verifier interaction — but the primary rung's
finding does not replicate at K = 5, and any claim about the interaction
should carry that.

## 6. Decisions needed from the PI

Recorded rather than taken, because each changes numbers or behaviour someone
may rely on.

1. **M6** — how should the Phase-2 sweep be prevented from deleting an
   unregistered, in-flight verifier upload? Register in `upload_jsonl`, or
   narrow the sweep to self-registered files? This is the one to look at
   first: it is a live cross-process data-loss path.
2. **M1** — is the BH family at K ≠ 3 five tests or four, and should a
   `meaningful: false` row carry a `significant` verdict at all? A change
   rewrites three artefacts under `results/`. The direction of the current
   error is conservative for T1–T4.
3. **M2** — should `batch-recover` default `--iterations` from the leg's own
   `probabilities.json`, or refuse to book a leg where every expected key
   missed?
4. **M4 / m10** — what head-room does the preflight need, given how many
   concurrent lodgers a campaign runs, and should a `PROCESSING` upload
   reporting `size_bytes = None` be charged an estimate rather than zero?
5. **m7** — should a non-SUCCEEDED terminal state put a chunk into
   `failed_chunks` while still keeping its paid-for partial results?

## 7. Verification

All commands run from the repository root. Output verbatim.

```console
$ .venv/bin/ruff check scripts/lib_batch_api.py scripts/run_pv.py scripts/gemini37_image_55map_r2.py tests/test_file_storage_preflight.py tests/test_image_2x2_tests.py tests/test_run_pv_batch_chunking.py
All checks passed!
```

```console
$ .venv/bin/python -m pytest -q -m tier1 tests/test_file_storage_preflight.py tests/test_image_2x2_tests.py tests/test_run_pv_batch_chunking.py tests/test_batch_api.py tests/test_run_pv_batch_usage.py

tests/test_file_storage_preflight.py ...................                 [ 11%]
tests/test_image_2x2_tests.py ..........                                 [ 17%]
tests/test_run_pv_batch_chunking.py .....................                [ 30%]
tests/test_batch_api.py ................................................ [ 59%]
...............................................................          [ 96%]
tests/test_run_pv_batch_usage.py .....                                   [100%]

============================= 166 passed in 3.07s ==============================
```

Mutation check on the C1 fix — both preflight call sites neutered at runtime,
helper left intact:

```console
$ .venv/bin/python <scratchpad>/mutate_callsites.py
tests/test_file_storage_preflight.py:499: in test_run_batch_unit_checks_storage_before_submitting
    assert message.startswith("submit_error:")
E   AssertionError
=========================== short test summary info ============================
FAILED tests/test_file_storage_preflight.py::test_verify_batch_checks_storage_before_the_first_upload
FAILED tests/test_file_storage_preflight.py::test_run_batch_unit_checks_storage_before_submitting
========================= 2 failed, 15 passed in 0.73s =========================
```

Exactly the two wiring tests go red; the helper tests stay green, confirming
the new tests are orthogonal to the existing ones and target the mutation
they were written for.

## 8. Commits

| Commit | Subject |
|---|---|
| `ac00a3ed7` | `test(batch): pin the storage preflight wiring` |
| `f100ed110` | `fix(image55-r2): match the board's micro-F1 arithmetic` |
| `248c76499` | `fix(run_pv): guard each job in batch-recover` |
| `97ab0a7cb` | `test: close the audit's surviving mutations` |

## Changelog

### 2026-09-20 — Original publication

First audit of the `69d1ed6bf..HEAD` range (five commits, six files, 1,276
insertions). Two-lens protocol run per `~/.claude/commands/audit.md`, with
three mutation experiments. Severity tally 1 critical / 6 major / 11 minor.
Four fixes landed (`ac00a3ed7`, `f100ed110`, `248c76499`, `97ab0a7cb`),
closing the critical wiring hole and thirteen surviving mutations; the rest
are recorded as recommendations or closed as no-action with the reasoning
above. Five decisions are outstanding (§ 6), of which M6 — a Phase-2 sweep
able to delete a concurrent verifier leg's in-flight input — is the one to
look at first.
