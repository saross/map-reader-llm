# Run B Stage 2: pre-launch audit of the unions, crops and verifier legs

> **Last revised**: 2026-10-08 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Auditor**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), as the independent pre-launch auditor of Stage 2.
- **Date**: 2026-10-08 (Sydney); sapphire times below are Coordinated
  Universal Time (UTC), 2026-10-07.
- **Repository**: `map-reader-llm`.
- **Commit audited**: `main` at `01bdbc53d`
  (`01bdbc53d1f6a6b7a076ec6e37fa70bd9a57d3db`), which is also the head of
  sapphire's main checkout. The Stage 2 commits audited are `db21944eb`,
  `5d868f032`, `06e15d304`, `ad6cd464e`, `2956c4250`, `1421f3dc0`,
  `dadf935b4`, `e1795c1a1` and `97d883b8f`.
- **Scope**: the Stage 2 card `planning/modality-bridge-2026-10-07-stage2.md`
  and its record `planning/modality-bridge-2026-10-07-stage2-rehearsal.json`,
  against the Stage 1 card `planning/modality-bridge-2026-10-07.md` (§ 2.2,
  § 4.8, § 8, § 10) and the Principal Investigator's (PI's) rulings D2, D49
  and D52 (`planning/pi-decisions-2026-09-20.md`); the launcher
  `scripts/modality-bridge-2026-10-07-stage2.sh`; `scripts/modality_bridge_union.py`,
  `scripts/verifier_dryrun_harness.py`, `scripts/modality_bridge_anchors.py`,
  and the edits to `scripts/image_b_analysis.py` and
  `scripts/gemini37_image_gap_test.py`; the batch verifier path of
  `scripts/run_pv.py` as Stage 2 invokes it; and the cost and File API
  arithmetic.
- **No Application Programming Interface (API) call was made.** Everything
  that wrote ran in two disposable `git clone --shared` copies under
  `~/worktrees/map-reader-llm/` on sapphire, which held no API key
  (`config.GOOGLE_API_KEY` was `None`, no key variable was set, and
  `find_dotenv()` found no `.env`). A live `run_pv.py verify` was replaced by
  a test double. Sapphire's main checkout and
  `outputs/modality-bridge-2026-10-07/` were only read. The copies were
  removed when done.

## Verdict

**GO WITH FIXES.** Nothing found would verify the wrong candidates, send a
request that differs from the original legs' beyond the two differences the
card already records (no `OFF` safety settings, batch tier), or use the
wrong model, thinking level, temperature or verifier configuration. The
union chain, the crops, the request comparison, the dry run's API-freedom
and the six-cell anchor gate all reproduced independently at `01bdbc53d`.

Two medium findings need action. **A1** must be fixed before `verify`: a
relaunched leg is judged by the previous attempt's log lines and pid file,
so after a storage refusal (the case the card anticipates) the launcher
reports `LODGING FAILED` while the new leg lodges and bills, and `wait`
returns a false terminal state. **A2** must be settled before scoring: the
batch path books a malformed but repairable verifier response as
probability 0.0, where every original leg's real-time path repaired or
retried it, and the card's commit list omits `batch_results.jsonl`, the only
record from which those rows can be re-parsed. The rest are low.

The PI's explicit go is still required (D49 returns Stage 2 to the PI; the
card's § 8 flag that D52's delegation may not cover Stage 2 stands).

## Findings, by severity

### A1 (medium): a relaunch reads the previous attempt's log lines and pid file

`verify_one` appends every attempt to one log (`>> "$log"`, launcher lines
357 and 361–362) and then judges the new attempt on the whole file: it counts
`Submitted batch job N/M:` lines (line 367), greps for lodging failures
(line 374), and waits for the pid file to be non-empty (line 363), which a
previous attempt's pid file already is. `status` (line 409) and `wait`
(lines 430–434, through `wait_for_run.py`, whose classifier takes the last
marker in the file) read the same file. The Stage 1 launcher avoids the
first of these by counting from a `base` taken at launch
(`scripts/modality-bridge-2026-10-07-stage1.sh` lines 275 and 288); Stage 2
does not.

Exercised on sapphire (test T1: a stand-in `g37-text` arm in batch layout,
`OUT=standin`, a test double for the live `run_pv.py verify`):

1. First attempt: the double printed
   `ERROR - Batch verification failed: FileStorageCapExceeded (fake)` and
   exited 1, as a storage preflight refusal would. The launcher reported
   `LODGING FAILED` (correct). No `batch_jobs.json` was written.
2. Relaunch, the double now lodging after 20 s. The launcher printed
   `started pid 594322` (the first attempt's dead pid) and
   `LODGING FAILED — read …; verifying stops here` after 5 s, rc 1. The new
   leg process, 594563, was alive.
3. `wait g37-text:g3`: `STATE=partial`, rc 2, after 0 s, with the leg alive
   (the classifier read the first attempt's `=== … EXIT 1`).
4. `status`: `ALIVE … exit 1 submitted 0 … fail-lines 1`, the fail-line
   being the first attempt's.
5. 25 s later the log held `Submitted batch job 1/1: batches/fake-594566`
   and `batch_jobs.json` existed: the leg had lodged.
6. Re-running `verify g37-text:g3`: `process 594563 still running — skipped`,
   then `LODGING DONE`, rc 0.

No double lodge occurred: the alive check (line 337) and the
`batch_jobs.json` refusal (line 343) held. But the operator is told a
billing leg failed, `wait` hands any chain a false terminal state, and the
refusal message offers `FORCE=1`, which relaunches the whole leg (line 346).
On a two-chunk leg relaunched with `FORCE=1`, the old `Submitted` lines
would satisfy the chunk count before the new process uploads anything, and
lodging would move on.

Test T2 (five relaunches over a dead pid file after a crash): all five
printed the stale pid as `started pid`. In all five the alive check had read
the new pid by its first test (each call returned after 19.5–20.5 s, that
is the rehearsal plus one 15 s wait-loop sleep, not at once), so the false
`EXITED before every chunk was submitted` race did not fire, but it is
open.

**Fix** (launcher only, before `verify`): after the alive and
`batch_jobs.json` checks and before line 357, rotate the log and drop the
pid file, so each attempt has its own log and every reader sees only it:

```bash
[ -f "$log" ] && mv "$log" "$log.$(date -u +%Y%m%dT%H%M%SZ)"
rm -f "$pidf"
```

The rotated logs are the earlier attempts' record and should be committed
with the rest. Add a launcher test that relaunches after a refusal and
expects the wait loop to stay in it.

### A2 (medium): the batch path books a repairable malformed response as 0.0

The batch parser takes `parts[0].text` and calls plain `json.loads`
(`scripts/lib_verifier.py:1224–1235`); a failure is booked as
`mound_probability` 0.0 with reasoning `PARSE_ERROR: …` (line 1253). The key
is present, so `_assert_completeness` counts the candidate as verified, the
leg exits 0, and `status` shows results equal to candidates. The real-time
path parses with `parse_response_with_repair` (line 1076) and retries
(line 1099), and an exhausted candidate is reported missing. That real-time
path is what every original leg ran: `parse_response_with_repair(txt)`
appears in `scripts/lib_verifier.py` at all five original verifier commits
(`7f13952ac`, `2ccf1b334`, `b8e130fd3`, `5bd514542`, `1c46243d2`). This is a
results-handling difference between the bridge and the originals, beyond
the two request differences the PI is asked to acknowledge.

Evidence from the 20 committed batch verifier legs (`batch_results.jsonl`
beside `probabilities.json`): 9 `PARSE_ERROR` rows among 157,256 responses
(1, 3 and 3 in `outputs/gemini3-image-55map-2026-09-16/…/verify_k1_arm2`,
`verify_k3_arm2` and `verify_k5_arm2`; 2 in
`outputs/gemini37-image-55map-2026-09-13/…/verify_k5_arm1_replicate-batch-2026-09-20`;
0 elsewhere, including Run A's four legs). No response had more than one
part or a thought part first. In the `verify_k5_arm1_replicate-batch` leg,
`candidate_06537` and `candidate_08272` were booked 0.0; their raw texts end
with a stray `}`, and `parse_response_with_repair` recovers 0.2 and 0.05. A
0.2 sits above the 0.10 and 0.15 thresholds of four of the six original
operating points, so such a row would leave a set the originals' path would
have kept it in. At that rate Stage 2's 17,164 candidates expect about one.

The parse warning (`Failed to parse verifier result for …`) does reach the
leg log, and `status` counts it as a fail-line, so card § 7 item 11 would
mark the leg not done, but the card gives no remedy. Its commit list (§ 7
item 12, lines 484–489) names `probabilities.json`, `run.meta.json`,
`batch_jobs.json` and the logs, not `batch_results.jsonl`, which `run_pv.py`
writes (`record_batch_usage`) and Run A committed. Without it the rows
cannot be re-parsed and the usage cannot be re-audited.

**Fix:** add `batch_results.jsonl` to § 7 item 12 now. Then either (a)
before the spend, make `parse_verifier_results` parse with
`parse_response_with_repair`, the real-time path's own function (it changes
no request; it is shared code, so it wants its own small review); or (b)
add to § 7 item 11: count `PARSE_ERROR` rows in each leg's
`probabilities.json`, re-parse them from `batch_results.jsonl` with
`parse_response_with_repair` before scoring, and record the count and the
values recovered.

### A3 (low): a polling verifier is not silent, and `wait` gives up hang detection

The card (§ 2, lines 123–128; § 8, lines 505–506) and the launcher header
(lines 70–72) say a polling verifier writes nothing between submission and
its job's end, so `wait` uses a 90,000 s staleness window (line 433).
`run_pv.py` sets the root logger to INFO (line 94), which lets the HTTP
client log every poll. Run A's committed batch logs show it:
`outputs/verifier-date-2026-10-07/55maps-text-min-generalisation/increment.log`
has 10 `HTTP Request: GET …/batches/…` lines between `Submitted batch job`
and the terminal state, and `…/55maps-text-high-t0.3-generalisation/k4set.log`
has 12; in both the longest gap between log lines is 31 s. Log age is
therefore a sound liveness signal. The poll's 25 h cap
(`scripts/lib_batch_api.py:1475`, checked at line 1534 between polls) does
not bound a call that blocks, so a 25 h window leaves a hung leg unnoticed
for a day.

**Fix:** `--stale-seconds 3600` in `wait_leg`; correct the card's § 2
paragraph and § 8 flag and the launcher header.

### A4 (low): two concurrent `verify` invocations can lodge one leg twice

The alive check (line 337) and the `batch_jobs.json` check (line 343) run
before `rehearse` (line 351), which takes seconds (about 5 s on the
791-candidate stand-in, where T1's relaunch returned after 5 s with the
rehearsal included; longer for the K = 10 arms). Nothing locks the leg,
so two `verify` invocations naming the same leg (for example `verify all`
in one terminal and a single leg in another, or a chain re-running
`verify all`) can both pass the checks and both launch. This is from
reading; it was not exercised.

**Fix:** take a lock in the `rehearse|verify` branch, for example:

```bash
exec 9> "$ST2/verify.lock"
flock -n 9 || { echo "another verify holds $ST2/verify.lock"; exit 1; }
```

### A5 (low): the gate checks the passes' tiles, not what the tiles were sent with

`check` gates coverage only. Nothing reads the pass metas, yet the `temp1`
arms differ from their twins only in temperature, and `g37-image-cache`
only in cache use. A pass re-lodged by hand with the wrong flags, or a
cache-fallback pass that the Stage 1 card (§ 4.5) says must be discarded,
would pass every Stage 2 gate. § 7 item 1 asks the operator to check cached
share and thinking tokens, not temperature. The metas carry what is needed:
the landed `g3-image` pass 1 meta records `configuration.model`
`gemini-3-flash-preview`, `temperature` 0.7, `thinking_level` `minimal`, and
`usage_stats.cached_share` 0.9445.

**Fix:** in `check`, for every pass file (main and fragments) read the
sibling `.meta.json` and refuse unless the model, temperature (1.0 for the
two `temp1` arms, 0.7 otherwise), thinking level, and, for the three cached
arms, a cached share of at least 0.9 are as the Stage 1 card's § 4.2 and
§ 4.8 tables say.

### A6 (low): the ±15 % review band is applied by hand

Card § 3 makes a D49 union outside ±15 % of its guide a finding to raise
with the PI before verifying. `estimate` (lines 442–475) prints sizes and
costs only, and `verify` does not consult the band. **Fix:** have
`estimate` print each leg's band and an `OUT OF BAND` flag, and have
`verify` refuse a D49 leg outside it unless `BAND_OK=1`.

### A7 (low): no stated remedy for a short leg, and `FORCE=1` is offered lightly

`image_b_analysis.load_image_union` refuses unless every candidate has a
result (lines 127–131), so a leg with a lost chunk, a never-lodged chunk, a
`FAILED` or `EXPIRED` job, or `PARSE_ERROR` rows (A2) blocks scoring. The
card says a leg is done when results equal candidates (§ 7 item 11) but not
what to do otherwise, and the refusal message's `(FORCE=1 overrides)`
(line 346) does not say that `FORCE=1` lodges the whole leg again while the
earlier job may still bill. **Fix:** state the remedies in § 7 before
launch (`run_pv.py batch-recover` for a chunk lost while polling; a named
procedure, and whether it is batch or real-time, for candidates never
returned), and reword the message.

### A8 (low; Stage 1's tools): an unmerged chunked recovery fragment cannot be completed

Stage 1's `residuals` counts every `*.tiles.json` in a fragment directory,
chunk sidecars included, and has no not-landed branch for fragments
(`scripts/modality-bridge-2026-10-07-stage1.sh` lines 451–452; the branch at
lines 444–449 covers main passes only). If a chunked fragment loses a
chunk, `residuals` writes a residual for the lost chunk's tiles and the next
round re-covers them; Stage 2 then refuses the first fragment for holding
chunks without a merged file (`scripts/modality_bridge_union.py:171–177`),
and resuming that fragment would make the overlap gate refuse instead
(lines 397–400). Stage 2 fails closed, correctly; only `g37-image` (466
tiles per job) can produce a chunked fragment, and only for a residual over
466 tiles. **Fix (Stage 1):** report a fragment with chunk sidecars but no
merged sidecar as not landed, to be resumed, as main passes are.

### Nits (documentation)

- Card § 8 (line 507): "The tier-1 suite is red on main" is stale. `01bdbc53d`
  moved `scripts/delete_landed_caches.py` to the shared resolver, and
  `test_no_bare_convention_a_glob_outside_this_module` passes at `01bdbc53d`.
- The request signature (`bridge_dryrun_harness.summarise_jsonl_line`) hashes
  five named `generation_config` fields, not the field list. A field added
  to `build_generation_config` before launch would not change the signature.
  Adding `sorted(gen.keys())` to the summary would close that. Today the
  builder emits exactly those fields.
- The card's commit list (§ 7 item 12) could also name
  `outputs/modality-bridge-2026-10-07/stage2/checks/` (the coverage,
  provenance and rehearsal records the go/no-go rests on).

## Checked and found sound

- **Legs, flags and paths.** `plan` prints ten verify commands; the tier-1
  launcher test pins each leg's `--model`, `--thinking-level` (Gemini 3.7
  only), `--temperature 0.0`, `--mode batch` and
  `prompts/configs/verify_adversarial-text.json`. `verify_args` word-splits
  `vflags` into separate arguments. Each leg verifies its own arm's crops;
  `g3` and `g37` legs of one arm share crops and have separate directories.
  `k_for`, `version_for` and the pid glob `"$OUT"/pids/"$arm"-run*.pid`
  (which matches Stage 1's `_rd<R>` recovery names and does not match
  `g37-image-cache` from `g37-image`, or `g3-*-temp1` from `g3-*`) are right.
- **Request, model and temperature.** The verifier configuration and
  instruction hash to `357d8a87d612…` and `2518d5298d9b…` at all five
  original commits and at `01bdbc53d`. `resolve_verifier_temperature`
  returns an explicit `--temperature` unchanged, so 0.0 is sent and recorded
  (`cli_overrides`). `--model` reaches the job, not the request line;
  `_resolve_model_name` keeps `gemini-3-flash-preview` and
  `gemini-3.7-flash` as given when listed, and exits before any upload when
  not.
- **Chunking, preflight and booking.** 4,000 candidates per job, candidate
  ids preserved; every chunk lodged before polling; `batch_jobs.json`
  written after each submission, so a relaunch after any lodge is refused.
  The storage preflight runs before the first upload with the safe sweep.
  Run A's log records usage booked from 2,220 of 2,220 responses.
- **Launch hygiene.** The wrapper writes its own pid (`echo $$ > "$0"`), runs
  the leg as its child, captures `$?` before `$(date)`, and is launched with
  `nohup`, `PYTHONUNBUFFERED=1`, all three descriptors redirected and `&`
  ending the command, with nothing after it on its line. Liveness uses
  `kill -0`, never `pgrep -f`. The failure greps are case-insensitive and
  include the library's words.
- **Union chain, rebuilt independently** (`validate-chain` at `01bdbc53d`,
  57.5 s): all four originals `EQUAL`, legacy and batch-replica rebuilds both
  byte-identical to the committed unions: 3,319, 4,065, 791 and 674
  features; files per pass `[1,1,1,2,1,1,1,2,1,2]`, `[2,1,2,1,1,2,1,2,2,1]`,
  `[2,2,2,2,1]` and `[2,2,2,2,2]`; 30, 30, 15 and 15 decoy chunk files.
- **Red sentinel.** A mutant adapter that also returned each pass's chunk
  files was refused by the overlap gate (`1392 tile(s) processed by more
  than one file`, exit 1).
- **The launcher on a stand-in arm.** The 3.7 text passes laid out in batch
  layout with decoy chunks, then `prepare g37-text`: coverage 5 × 1,398
  tiles, files per pass `[2,2,2,2,1]`; union of 791 with SHA-256
  `3d315de606525941…`, identical to the committed
  `outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/union_k5.geojson`;
  791 raster crops, 0 tile fallback; the crop manifest equal to the
  original's except `source_geojson`; all 791 crop PNGs byte-identical to
  the original crops on sapphire; provenance `AGREES`.
- **Rehearsal.** `rehearse g37-text:g3 g37-text:g37`: 791 requests each,
  0 stub clients, 0 breaches, keys in manifest order, one signature each
  (`3b48d7193dcf…`, `51567e8e54f8…`, the launcher's pins), request files of
  46,357,605 and 46,354,441 bytes, equal to the record's.
- **The dry run is API-free, at the operating-system level.** A bare
  `run_pv.py verify --mode batch --dry-run` for the 3.7 leg, outside the
  harness, under `strace -f -e trace=connect,sendto,sendmsg`: exit 0,
  `[DRY RUN] JSONL written but not submitted`, and zero such system calls in
  the process tree. By code, `_verify_batch` returns at `if dry_run:` before
  `from google import genai`.
- **Request against the original real-time request** (the 3.7 text leg, 3.7
  verifier): the original real-time request captured from a clone at
  `5bd514542` under the stub (model sent `gemini-3.7-flash`), compared with
  the launcher's batch request for candidates 0–2. Same: parts, system
  instruction SHA-256, temperature 0.0, thinking `LOW`, 8,192 tokens,
  `application/json`, no cached content. Content differences: only the four
  `OFF` safety settings and the `flex` tier. Representation only: roles and
  request keys.
- **Anchor gate** (`anchor-gate` at `01bdbc53d`, about 8 min under load): all
  six cells exact, 0.8961 (0.15, k10), 0.8412 (0.15, k9), 0.9139 (0.10, k5),
  0.9265 (0.80, k5), 0.9254 (0.10, k5) and 0.9308 (0.90, k5), through both
  instruments; gaps +0.0549 (p 0.0010), −0.0115 (p 0.2533) and −0.0043
  (p 0.6767).
- **The analysis edits change no default.** `gemini37_image_gap_test.py`
  with no flags rewrote `results/gemini37-image-gs-2026-09-01/gap_test.json`
  byte-identically. `image_b_analysis.py` on the Gemini 3 image cell with
  only `--union-name union_k10.geojson` reproduced every key it writes, and
  its `sweep_20m.csv` and `verified_best_20m.geojson` were unchanged; the
  committed `saturation_N3_vs_N10` block predates today's code, as the card
  says. Other callers (`image_b_pair.py`, `selection_aware_intervals.py`,
  `gemini38_armv_pair_test.py`, `gemini3-image-55map-gs-calibration.sh`) use
  `load_image_union`, `sweep`, `N_PERMS`, `SEED` or the existing flags, all
  unchanged.
- **The inherited K = 5 rung** follows D2: lower rungs re-clustered from the
  first N deduplicated passes in numeric order, each candidate inheriting
  the nearest top-rung probability within 10 m; both rungs are clipped to
  the common footprint, so D51's same-area condition holds.
- **Tests and lint.** The Stage 2 tier-1 tests pass at `01bdbc53d` (55
  passed: union 25, harness 4, anchors 12, launcher 7, cache deleter 7);
  `ruff check` passes on the five scripts and four test files.
- **Costs.** The per-candidate rates re-derive from each original leg's
  `cost_audit.json` and `probabilities.json` (US$0.6843, 0.6880, 0.7022,
  0.7093 and 1.0935 per 1,000; the 3.7 text swap leg is
  `audited-lower-bound` at US$0.00213, so the card's US$0.87 token basis is
  the right one to use). The rate card's batch rows equal its flex rows for
  both models. At the guide sizes the ten legs come to 17,164 candidates and
  US$12.62–13.01 (D49 legs US$7.66–7.89, added legs US$4.96–5.12), as the
  card says; every union at +15 % would cost about US$14.96 at the higher
  rate. Run A's audited batch usage (3,978,240 input and 347,216 output
  tokens for 2,220 candidates) prices to US$0.68 per 1,000, in the card's
  range.
- **The 2,932 guide.** `outputs/grid-2026-08-18/g384_ov192/consensus-n5/consensus_t1.geojson`
  holds 2,932 features, 2,714 inside the common footprint and 218 outside,
  as § 3 says.
- **File API headroom.** The record's request files run 57,530–60,599 bytes
  per candidate, so the ten legs need about 0.99–1.04 GB; the largest single
  file is 235,871,520 bytes (`g3-image`, chunk 0), far under the 2 GB
  per-file limit. Run A's log prints the preflight's budget as "18.14 GB"
  against a "20.00 GB cap"; those are GiB, and the budget is the card's
  19.47 GB (21,474,836,480 bytes less one 2,000,000,000-byte chunk).
- **Stage 2 beside Stage 1.** Stage 2 writes `<arm>/scoring/`,
  `<arm>/verifier/` and `stage2/`; none is read by Stage 1's `status`,
  `residuals` or `delete_landed_caches.py` (whose `*/run_<N>` glob matches
  only `<arm>/<version>/run_<N>`). The gate is per arm: an arm whose passes
  have all landed can be prepared while other arms run, and nothing enforces
  Stage 1 card § 4.7 (audit, commits, upload deletion), which stays an
  operator step (§ 7 item 1).

## Seen on sapphire (read only)

At 13:28 UTC: sapphire's checkout at `01bdbc53d`; 17 pid files, with
`g37-image` 1–5, `g37-text` 1–5 and `g3-image` 6–7 alive and `g3-image` 1–5
gone. `g3-image` pass 1 had landed: `Batch complete: 1398 tiles, 2332
detections, 0 failed`. Its merged file has the same schema as the original
real-time pass (`crs`, `features`, `processed_tiles`, `type`; Polygon
features with `confidence`, `label`, `method`, `model`, `source_tile`,
`subtype`; EPSG:32635), so the chain validated on real-time files applies.

## Method note

Both copies were `git clone --shared` clones, not worktrees, so nothing was
written into the main checkout's `.git`; `inputs/tiles_384_ov192` and
`inputs/rasters` were symlinked, and the main checkout's interpreter was
used. One test script, sent to sapphire inside a quoted here-document, was
mangled and ran on amd-tower instead, in the local checkout: it created four
empty directories (`standin/stage2/{checks,logs,pids}`) and ran no Python,
because the interpreter path it named did not exist there. They were removed
at once; sapphire's main checkout was not touched.

## Changelog

### 2026-10-08 — Original publication

The pre-launch audit of Run B's Stage 2 at `01bdbc53d`, before any Stage 2
command ran on the live tree: verdict GO WITH FIXES, two medium findings
(A1 relaunch reads stale log lines; A2 batch parse failures booked as 0.0),
six low ones, three nits.
