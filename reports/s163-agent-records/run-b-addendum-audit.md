# Run B addendum: pre-launch audit of the three added arms

> **Last revised**: 2026-10-07 (re-check of the fixes; see
> [§ Re-check of the fixes](#re-check-of-the-fixes-2026-10-07-later)).
> See [§ Changelog](#changelog) for revision history.

- **Auditor**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), as the independent pre-launch auditor of Session 163.
- **Date**: 2026-10-07.
- **Repository**: `map-reader-llm`.
- **Commit audited**: `main` at `6b554e8e3`. `main` has since moved to
  `f79507ef8` with planning and probe-data commits only:
  `git log 6b554e8e3..origin/main -- scripts/ prompts/ inputs/ config.py tests/`
  is empty, so the code audited is the code at today's head. Sapphire's
  checkout is at `9f19110b0`, which contains `6b554e8e3`.
- **Scope**: the card `planning/modality-bridge-2026-10-07.md` (§ 4.5, § 4.8,
  § 6.1, § 10), the launcher `scripts/modality-bridge-2026-10-07-stage1.sh`
  (diff `33a66d6ae..6b554e8e3`), the rehearsal addendum
  `planning/modality-bridge-2026-10-07-rehearsal-addendum.json` and its
  sapphire outputs, today's code changes on the Run B path (`36a8243ac`,
  `af53b0491`), the Batch API explicit-cache path in `scripts/lib_batch_api.py`,
  and the cost and File API arithmetic. The Session 162 audit (card § 7) is
  not redone.
- **No API call was made.** The launcher was exercised in a scratch copy with
  a fake detector that never imports `google-genai`. Sapphire was read
  through file reads and read-only Python scans of its metas and of one
  request file.

## Verdict

**GO WITH FIXES.** Nothing found would send a request different from the
rehearsed ones. But one finding, F1, means Stage 1 as written cannot be
lodged in one day. The launch's own uploads stay registered and are never
released, and 37.36 GB of requests have to fit through a 19.47 GB budget.
Fix F1 (code, or the operator step given) before any lodge, and at the
latest before `lodge all`. F2 is a free change to the gate and should go in
with it. The rest are low-severity corrections.

## Findings, by severity

### F1 (high): the safe sweep can reclaim none of Run B's uploads, so Stage 1 stalls part-way

The card's storage plan (§ 4.3, lines 208–213; § 4.8, lines 320–323) relies
on the preflight's safe sweep reclaiming the input files of completed jobs.
It cannot do that for detector uploads:

- `upload_jsonl` registers every upload in `outputs/.active_files.json`
  (`scripts/lib_batch_api.py:1391–1399`).
- `sweep_stale_files_safe` never deletes a registered file
  (`lib_batch_api.py:929–931`).
- Registry entries are pruned only after 48 h
  (`scripts/lib_file_registry.py:54`, `_STALE_ENTRY_HOURS = 48.0`).
- The detector's batch path never releases its input. `run_batch_unit`
  discards the uploaded name (`job_name, _uploaded_name = submit_batch_unit(`
  at `lib_batch_api.py:3467`), and neither it, `complete_batch_unit` nor
  `4_detect_mounds_batch.py` calls `deregister_upload`,
  `cleanup_batch_files` or `files.delete`. The verifier path does release
  its input: `run_pv.py:977` deregisters "so another process's sweep can
  reclaim the space (audit finding M6)". The detector never got that change.
- Sapphire's registry holds 0 entries today, so the only registered files
  during Stage 1 will be Stage 1's own.

These are the request bytes, recomputed from the addendum's `full_build`
records:

| Quantity | Bytes |
|---|---:|
| The 30 D49 passes | 30,427,477,950 |
| All 45 passes | 37,363,480,680 |
| Preflight budget (21,474,836,480 cap less 2,000,000,000) | 19,474,836,480 |
| D49 alone over budget | 10,952,641,470 |
| All 45 over budget | 17,888,644,200 |

I simulated the launcher's order with nothing reclaimed and no chunk-0 job
finishing early. The loop stops at `g37-image-cache:4`, with 19.24 GB stored
and 0.46 GB more needed against 19.47 GB. Every `g37-image` chunk 1
(1.25 GB) is then refused. Each of the five `g37-image` passes ends with
chunks 1 and 2 failed, the merge withheld and exit 2. If chunk-0 jobs do
finish early, chunks 1 and 2 take the space instead, and the refusal falls
on the tail of the D49 order (`g3-text`). Either way, part of D49 and all
the additions miss the day. Re-running `lodge all` "later" (§ 4.3, § 4.8)
cannot help for 48 h.

The card's "a storage refusal can only delay an addition" (line 316) is
wrong even without the registry problem. Chunks 1 and 2 of `g37-image` are
lodged by the running pass processes, not by the loop. They compete for the
same headroom as the additions.

No money is spent wrongly, because the preflight refuses before uploading.
The exception is the cached arms, which leak a cache on every refused
attempt (F4). The cost is the one-day design and a stalled campaign that
needs hand work.

**Fix, preferred (code, off the request path):** in `run_batch_unit`, keep
`uploaded_name`. After `complete_batch_unit` returns for a job seen in a
terminal state, release the input with
`cleanup_batch_files(client, [uploaded_name], label="input")`. That call
deregisters first, then deletes. Input deletion works; only output-file IDs
hit bug #1759 (`docs/notes/reflections/session-log.md:2193`). The minimum
is `deregister_upload(uploaded_name)`, as `run_pv` does. Never release on
`poll_error` or `poll_timeout`, because the job may still be reading the
file. Add a tier-1 test with a stub client: the input is released after a
terminal state and untouched after a poll error. Then re-run the harness on
pass 1 of one arm to show the signature is unchanged. Correct § 4.3 and
§ 4.8 to match.

**Fix, alternative (no code):** add an operator step to § 4.4. For each
`Submitted batch job:` line in `outputs/modality-bridge-2026-10-07/logs/*.log`,
call `client.batches.get(name)`. If the job is terminal and its pass or
chunk sidecar exists, call `cleanup_batch_files(client, [job.src.file_name])`.
Run the step whenever `status` shows newly landed jobs, and before every
re-run of `lodge all`.

### F2 (medium): the first batch explicit cache is on Gemini 3, not 3.7, and is ungated

Ten D49 passes would use it before any of them lands.

Card § 4.8 (lines 327–328) says `g37-image-cache` is "the first explicit
cache on Gemini 3.7 in this project". The record says the opposite.

- **55-map passes 4 and 5** (2026-09-17, `gemini-3.7-flash`, thinking low,
  T 0.7, Batch API, explicit cache). Each has 24,561 responses, and every
  chunk meta records 20,020 input and 18,909 cached tokens per response
  (`outputs/gemini37-image-55map-2026-09-13/batch-staging-run{4,5}/…`,
  commits `22ffe6b43` and `dffa7fb75`). `post_run_report.md:105` and `:453`
  read "explicit context caching", with a 0.945 cached share.
- **Drift probe** (`outputs/batch-drift-probe-2026-09-17`, on sapphire,
  untracked). Its request file has the keys `cached_content`, `contents`
  and `generation_config`, the same keys as today's. It completed 500 of
  500 tiles.
- **Every batch meta on sapphire.** I scanned all of them. The only ones
  with per-response usage and cached tokens above 0 are four 3.7 metas:
  the merged and the per-pass meta of each of those two passes. No
  `gemini-3-flash-preview` batch meta has any. One `gemini-3-flash` meta
  (`outputs/h11/pv-diag-384/…`, started 2026-03-23) records cached tokens
  without per-response usage, from before the batch cache builder existed.
  That builder dates from 2026-09-17 (`1a1e8393f`, `a18901cbc`).

So 3.7's explicit prefix is measured, at 18,909 tokens (the card's
assumption holds), and the 3.7 cached request has been served. The first
batch explicit cache on `gemini-3-flash-preview` will be `g3-image` run 1,
and `lodge all` lodges `g3-image` 1–10 back to back. Suppose the Gemini 3
cache were referenced but its reads billed as fresh input. The request
shape would pass the guard, and ten passes would cost about US$52.9 extra
(18,916 × (0.25 − 0.05) / 10⁶ × 13,980) before anyone read a cached share.
This is unlikely: real-time explicit caches on this model worked, and batch
references work on 3.7. But bounding it costs nothing.

**Fix:** fold it into the existing gate. Run
`lodge g37-image:1 g3-image:1`, and continue only when `g37-image` chunk 0
shows a cached share of 0.5 or more and `g3-image` run 1 shows about 0.944
(18,909 of 20,028 per call). Correct lines 327–328 and cite the 3.7
precedent. In § 4.7 item 2, expect 18,909 cached tokens per call on
`g37-image-cache` and `g3-image-temp1` as well.

### F3 (low): the fifth leg's headline cost uses the cache-read rate the invoices contradict

§ 4.8 prices `g37-image-cache` at US$12.39, which assumes cache reads at
US$0.0375/M. It gives US$17.35, at US$0.075/M, as the alternative "if the
invoice rate applies to explicit reads". The invoices read 3.7 cache reads
on the September batch legs at US$0.075/M
(`planning/cost-accounting-fix-plan-2026-09-21.md`, § 8 item 10), and those
legs include the two explicit-cache passes of F2. Card § 5 already uses
US$0.075/M as "likely" for `g37-image`.

Recomputed from `data/pricing/gemini-rate-card.json`:

| Basis | `g37-image-cache` | Additions | Stage 1 likely |
|---|---:|---:|---:|
| Card's headline (US$0.0375/M) | US$12.39 | US$28.65 | US$92.3 |
| Invoice rate (US$0.075/M) | US$17.35 | US$33.61 | about US$97.2 |

Both bases still sit inside the PI's ceiling for the fifth leg ("up to
double" of US$18, about US$36). **Fix:** make US$17.35 the headline.

### F4 (low): cached arms leak a paid cache on every refused or failed lodge

`run_batch_unit` creates the cache (`lib_batch_api.py:3393–3401`) before it
builds the request file and runs the preflight (`:3464–3466`). The batch
path never deletes a cache. The card's "exits before uploading (no spend)"
(line 211, and line 322) is therefore not true of `g3-image`,
`g37-image-cache` or `g3-image-temp1`.

Each leaked 24 h cache of 18,909 tokens costs US$0.454 on Gemini 3 and
US$0.227 on 3.7. Under F1, refusals of cached arms are expected, and every
recovery fragment of a cached arm creates one more cache. Neither is in
§ 4.8's estimate. The temperature-matched pair is estimated at US$16.3 plus
about US$4 of Stage 2 against the US$21 quoted (§ 4.8), which leaves under
US$1. Two leaked Gemini 3 caches would use that up.

**Fix:** create the cache only after the preflight passes, or delete it on
the `submit_error` path. Add the expected fragment caches to § 4.8.

### F5 (low): the § 4.4 gate bounds a pass, not a chunk

The detector runs a pass's chunks in one process: chunk 1 starts as soon as
chunk 0 completes (`4_detect_mounds_batch.py:1684`, `:1738`). `lodge_one`
waits only for the first submission. So by the time `status` shows chunk 0
of `g37-image-run1` landed, chunk 1 is already being built or submitted,
and the card forbids killing a polling pass.

§ 5 (lines 372–373) says the gate "caps that exposure at the first chunk of
one pass (about US$3.7 if uncached)". The real exposure is the whole pass,
1,398 × US$0.007992 = US$11.17 uncached (one chunk is US$3.72). That is
still inside the approved ceiling. **Fix:** correct the text.

### F6 (low): `lodge` accepts any arm and run

`expand` passes `ARM:RUN` through unchecked (launcher line 330). In the
fake-detector test, `lodge g3-text-temp1:7` started and "submitted" a pass
outside the plan; on the real service that is spend. `lodge
g37-image-cached:1` started the detector with an empty argument list, which
is harmless because argparse refuses it. But it left a log that makes
`status` exit 1 with `KeyError: 'g37-image-cached'` (line 377) until the log
is removed.

**Fix:** in `expand`, reject an arm not in `$ARMS` and a run not in
`passes_for`. In `status`, report a log whose arm is unknown instead of
crashing.

### F7 (low): "matched on temperature" is an inference

The card also credits the rehearsal with a comparison it did not make.

§ 4.8 (lines 308–310) says `g37-image-cache` differs from `g3-image-temp1`
"in model and thinking level only (rehearsal, § 6.1)". The addendum's
`twin_diff` compares `g37-image-cache` with `g3-image`, which runs at
T 0.7. Against `g3-image-temp1`, the requests also differ in the temperature
sent: 0.7 against 1.0, from the `full_build` first lines. The same holds for
`g3-text-temp1` against `g37-text`.

The effective match rests on the probe's verifier-seat result, extended to
the proposer by inference (`planning/temperature-probe-2026-10-07.md` § 6).

**Fix:** say that the pairs differ in model, thinking level and the
temperature value sent, and that Gemini 3.7 ignores the value (probe § 7
and § 8.5, verifier seat, applied to the proposer by inference).

### F8 (low): retried tiles of the cached arms go out inline

Parse-failure retries are built inline, with the 17 example images, no
cache and flex tier (`_retry_tile_sync`, `lib_batch_api.py:2455`,
`include_images` read at `:2498`). For `g37-image-cache`, a retried tile is
therefore served in exactly the shape the arm exists to remove. § 7 warning
5 records this for `g3-image` only.

**Fix:** in § 4.7, record `retry_usage.n_tiles_retried` per pass for the
three cached arms, and flag the retried tiles in Stage 2.

### F9 (low): the submission line is buffered

The detector prints `Submitted batch job` without flushing
(`lib_batch_api.py:3005`), and its stdout is redirected to a file (launcher
line 278). Normally the first poll's flushed print follows within seconds.
But a run of poll errors writes only WARNING lines to stderr, for up to
10 min (`max_consecutive_errors = 20` at 30 s).

If the process dies by a signal in that window, the log never records a
job that exists. `lodge_one`'s refusal check counts submissions from the
log, so it would then allow a second, billed lodge of the pass.

**Fix:** launch with `PYTHONUNBUFFERED=1 nohup "$PY" …` (or `"$PY" -u`) at
line 278.

### Nits (documentation)

- Card line 7 points to an "addendum audit in § 7.1", which does not exist.
  Point it to this report.
- § 4.1 items 3 and 4 (lines 152–155) still read "Open", although § 10
  records the PI's approval and sapphire's checkout (`9f19110b0`) contains
  `6b554e8e3`.
- § 4.8 line 320 gives 37.37 GB; the bytes sum to 37,363,480,680, which is
  37.36 GB.
- § 4.8 line 352 prices the two `temp1` unions' Stage 2 at "about US$4.1",
  but § 5 (line 387) gives US$3.93 for the same union sizes (2,932 and
  2,788). Use one figure, or say why they differ.
- The guard tells the operator to "discard this pass" without saying how.
  The procedure should be: let its job land, never kill it, move the pass
  directory to `archive/`, then re-lodge with `FORCE=1`. Without `FORCE=1`
  the refusal check blocks the re-lodge.
- `status` can print `gone` beside the state `running`, which is the
  orphaned-job case, and does not flag it. Printing `CRASHED?` there would
  help.
- Informational: the safe sweep protects only the `src` file of
  non-terminal jobs (`lib_batch_api.py:833–845`), not a terminal job's
  unretrieved results file. That is harmless today, because deleting an
  output file fails under bug #1759. If an SDK upgrade fixes #1759, a sweep
  could delete results before a lagging poller reads them.

## Checked and found sound

- **Arms table.** `passes_for`, `version_for`, `temperature_for`,
  `uses_cache` and `arm_table` are right for all seven arms. `plan` prints
  45 commands, with the output directories split 5, 5, 5, 10, 5, 10 and 5;
  20 use `--use-cache`, and the 10 with `--temperature 1.0` are exactly the
  two `temp1` arms.
- **Arguments.** For all 45 passes, `print-args` at head equals the
  addendum's `argv`. For the 30 D49 passes, the addendum's argument lists
  and chunk plans equal the original rehearsal record's.
- **Addendum claims, re-derived independently.**
  - 45 of 45 passes exit 0, with 0 breaches and one stub client each, in
    the JSON and in sapphire's `rehearsal-out/progress.txt`.
  - Every pass dispatches 1,398 tiles; `g37-image` does so as 3 × 466 at
    offsets 0, 466 and 932.
  - Temperature, thinking level, model, tile size 384, retry tier `flex`
    and cache TTL 86,400 s are as designed on every pass.
- **Signatures.** For the four D49 arms, the pass-1 signatures and request
  byte counts are equal in both rehearsal JSONs: `58cf1f1f…`, `167b1c95…`,
  `6d349600…`, and `4eef5736…` in all three chunks. The first-line fields
  and cache records are equal too.
- **Twin diffs, reproduced from the build records.**
  - `temp1` arms against their twins: temperature only.
  - `g37-image-cache` against `g3-image`: thinking level only, with
    identical cache contents.
  - `g37-image`'s inline parts equal the cache parts plus the cached
    request's parts (37 = 37), with the same system-instruction hash
    `e169b723…`.
- **Cache guard, exercised with the fake detector.**
  - It passes a cached request file and fires on an inline fallback and on
    a missing file.
  - Its path, `pass_dir/batch_working`, matches the detector's
    `run_dir/batch_working` (`lib_batch_api.py:2938`).
  - Its check exits 0 on the real cached request file of 2026-09-17 on
    sapphire.
  - It cannot falsely pass on a stale file: the request file is rewritten,
    under the same name, before every upload. No cached arm is chunked, so
    the first-line check covers the whole job.
- **Status and residuals.** Both parse every arm name and recovery-log name
  (`…-run2_rd1`). `recover` passes the right arguments to the added arms:
  `--use-cache` on both cached arms, `--temperature 1.0` on
  `g3-image-temp1`, and thinking low on `g37-image-cache`. `residuals`
  clears the residual files once fragments complete.
- **Corrected watcher bullet (§ 4.5).** The three detector batch logs on
  sapphire hold 0 INFO lines from `lib_batch_api`. Each counts exactly one
  `Submitted batch job` per job (7 for 7 chunks), so the INFO duplicate at
  `lib_batch_api.py:1430` never doubles the count.
- **`36a8243ac`.** The detector temperature fallback changes no Run B
  request (the signatures are unchanged) and no recorded value: every arm
  passes an explicit temperature, which `detector_temperature` returns as
  the same float.
- **`af53b0491`.** In the verifier resolver an explicit `--temperature` wins
  (`override is not None`), so Stage 2's `--temperature 0.0` sends 0.0.
- **Cache path arithmetic.** On 3.7, the cached prefix (18,909 tokens) is
  far above the 1,024-token floor. The cache and the batch job are bound to
  the same `model_name`, and the request carries `cached_content` without
  `system_instruction`. The same shape was served on 3.7 on 2026-09-17
  (F2).
- **§ 4.8 cost arithmetic.** Every figure reproduces to the cent from the
  rate card: US$12.39 or US$17.35, US$4.19, US$12.07, US$28.65 or US$33.61,
  likely US$92.25 and a range of US$88.15–130.61.
- **Sapphire state.** No `outputs/modality-bridge-2026-10-07/` exists yet,
  `google-genai` is at 1.71.0, and 346 GB of disk is free.

## Re-check of the fixes (2026-10-07, later)

- **Auditor**: as above (Claude, Opus 5.5 lane).
- **Commits re-checked**: `a0488a440` (F1), `580c7c494` (F4, D52) and
  `fdc0624ed` (F6, F9, card § 4.9 and in-place corrections). Sapphire's
  checkout is at `fdc0624ed`.
- **How**: read-only and API-free. The tests ran in a `git archive` copy of
  `fdc0624ed` (`scripts/`, `tests/`, `config.py`) in my scratch directory.
  The launcher ran there with the fake detector of the first audit. The
  deleter's selection functions ran offline on a synthetic campaign tree.
  On sapphire I read files only.

### Verdict

**Fixes sound, with one exception.** `lodge all` may proceed after the
§ 4.4 gates. **Do not run `scripts/delete_landed_caches.py` as written.**
In two reachable cases it deletes a cache that a running batch job can
still be reading, and a one-line change closes both (R1).

The guard's new discard message needs one more clause (R2). R3 and R4 are
minor.

### Fix by fix

- **F1: sound.**
  - `release_terminal_job_input` (`lib_batch_api.py:624`) does nothing
    unless the job is terminal. `run_batch_unit` calls it in a `finally`
    only after `poll_batch_job` has returned a terminal job. `poll_error`
    and `poll_timeout` return earlier and keep the registry protection.
  - Resumed jobs release `job.src`, and the sweep still protects every
    non-terminal job's `src`.
  - A chunked `g37-image` pass releases chunk k before chunk k+1's
    preflight, so the sweep can reclaim chunk k's input.
  - The four new tests pass (48 of 48 in `tests/test_file_storage_preflight.py`
    and `tests/test_delete_landed_caches.py`).
- **F2, F3, F5 and the nits: sound.** Card § 4.4 gates `g3-image-run1`. The
  fifth leg's headline is US$17.35, the gate's exposure reads one pass at
  about US$11.17, and 37.36 GB, § 4.1 and the US$3.93 figure are corrected.
- **F6: sound.** In the copy, `lodge g3-text-temp1:7`,
  `lodge g37-image-cached:1`, `lodge g37-image-cache:0`, `lodge nosuch` and
  the mixed `lodge g3-image:1 g37-image-cached:1` each exit 2 with nothing
  started and no log written. A valid spec still lodges.
- **F9: sound.** The fake detector saw `PYTHONUNBUFFERED=1` in its
  environment.
- **F7 and F8: mostly sound.** See R4 for the one sentence left over.
- **F4 (`580c7c494`): not safe as written.** See R1.

### R1 (medium): the cache deleter can delete a cache that a running job still reads

`select_deletable` protects only the cache named by each live or in-flight
pass's **newest** request file (`delete_landed_caches.py:186–195`). Every
other detector-named cache created since `--since` and older than 90
minutes is deleted. Two cases reachable tonight lose a running job's cache.

**Case 1: re-lodge over an orphan.** A cached pass's process dies while
its job runs. A 10-minute run of poll errors does this: `poll_error`, and
the 2026-09-17 55-map pass 5 hit one. The operator then re-lodges with
`FORCE=1`, which the launcher's REFUSED message offers and the new guard
message implies. The re-lodge rewrites `batch_working/…_runNN.jsonl` with a
new cache name. The orphan's cache is then named by nothing, so it is
deleted while the orphan may still be running.

**Case 2: other work's caches.** `--since` does not scope the deleter to
this campaign. Any other detector batch cache on the project, created after
`--since` (from any machine, same display name
`batch-detect-shared-prefix`), is deleted after 90 minutes. The docstring's
"caches from other work are never touched" (line 20) holds only for work
started before `--since`.

A latent third case: a chunked cached pass whose chunk k ends in
`poll_error` moves on to chunk k+1, and chunk k's cache stops being the
newest. No Run B cached pass is chunked (1,398 or fewer tiles against the
default 4,000), so this cannot happen tonight.

Evidence, offline, on a synthetic tree under the launcher's layout, with
the module's own `pass_states` and `select_deletable`:

```text
g3-image-run1        landed                     c/landed
g3-image-run2        process live (re-lodged)   c/new   (orphan job on c/old)
g37-image-cache-run1 exited without submitting  c/refused
caches: c/old, c/new, c/landed, c/refused, c/foreign (all past the grace)
current rule deletes:           ['c/old', 'c/landed', 'c/refused', 'c/foreign']
positive-ownership rule deletes: ['c/landed', 'c/refused']
```

**Fix (one line, plus a test):** delete only caches this campaign provably
owns and has finished with. In `select_deletable`, add
`owned = {s.cache for s in states if not s.protects and s.cache}` and skip
any cache not in `owned`. That set holds the caches named by a landed
pass's request file or by a lodge that exited without submitting. It closes
all three cases and still deletes what D52 asks for: landed passes' caches
and refused lodges' caches. The only cost is that a refused lodge whose
request file a re-lodge later overwrote keeps its cache until the 24 h
expiry (US$0.23–0.45).

`tests/test_delete_landed_caches.py:41–44` currently asserts that
`c/orphan`, a cache no pass names, *is* deleted. That assertion encodes the
hole, so it should flip to "kept", and a new test should cover the
overwritten-orphan case. Until the patch lands, run the deleter only with
`--dry-run`, and delete by hand only the caches it lists that a landed
pass's request file names.

### R2 (low): "move $d to archive/" must wait for the pass to exit

The guard's new message (launcher line 305) says to move the pass
directory to `archive/` and re-lodge. But the inline job's process is still
polling. When the job lands, `write_batch_outputs` recreates the directory
(`output_file.parent.mkdir(parents=True, exist_ok=True)`,
`lib_batch_api.py:2703`) and writes the inline-shape pass there.
`lodge` then calls the pass "already landed" and skips it, and the wrong
shape silently enters the arm. If the operator re-lodged in between, the
two processes race for the same files.

**Fix:** "when `status` shows the pass `gone` with a terminal state, move
`$d` (and the pass's log and pid file) to `archive/`, then `lodge ARM:RUN`".
If the log stays in place, `FORCE=1` is needed. Say the same in card § 4.5,
line 267.

### R3 (low): an upload whose submission fails is never released

If `client.batches.create` fails after the upload succeeded, `run_batch_unit`
returns `submit_error` (`lib_batch_api.py:3508–3509`). The uploaded name
never reached the caller, so the file stays registered for 48 h, holding
0.46–1.26 GB of the budget per occurrence.

**Fix (later):** have `submit_batch_unit` deregister its own upload when
`submit_batch_job` raises. This is rare and not a blocker.

### R4 (nit): one sentence still says the opposite

Card lines 314–315 still read "`g37-image-cache` differs from
`g3-image-temp1` in model and thinking level only (rehearsal, § 6.1)", and
the new text that follows contradicts it. Change it to "in model, thinking
level and the temperature value sent".

### Seen on sapphire (read only)

`g37-image-run1` was lodged at 11:55:33 UTC under `fdc0624ed`. Its chunk 0
of 3 (466 tiles) was submitted at 11:59:49 as
`batches/lhz0bogn15x372skpdyzqbgxwxvfu6odq4u8`, and its pid was alive and
polling when read. For the deleter, set `--since` before the first cached
lodge (`g3-image:1`). An early `--since` is harmless under the
positive-ownership rule.

## Changelog

### 2026-10-07 — Re-check of the fixes

Appended § Re-check of the fixes, after `a0488a440`, `580c7c494` and
`fdc0624ed`. F1, F2, F3, F5, F6 and F9 are sound. The cache deleter
(F4) can delete a cache a running job reads (R1; one-line fix given).
The guard's discard message must wait for the pass to exit (R2). R3
and R4 are minor. Nothing in the original findings changed.

### 2026-10-07 — Original publication

The pre-launch audit of Run B's three added arms, the launcher's cache guard
and the 45-pass rehearsal addendum, written before any Stage 1 lodge.
