# Run B, the modality bridging pair: configuration, Stage 1 launch plan, and audit

> **Last revised**: 2026-10-07 (original publication, Session 162). See
> [§ Changelog](#changelog) for revision history.

**Status: Stage 1 PREPARED and AUDITED, not launched. Awaiting the PI's
approval of the commands, the cost ceiling (§ 5) and the decisions in § 10.**
No Application Programming Interface (API) call was made to prepare this
card: every rehearsal ran under a stub client with network sockets blocked
(§ 6). Design: PI ruling D49 (`planning/pi-decisions-2026-09-20.md`), gate
`planning/gate-2026-10-07-verifier-date-and-bridge.md` § 2. Launcher:
`scripts/modality-bridge-2026-10-07-stage1.sh`. Rehearsal evidence:
`planning/modality-bridge-2026-10-07-rehearsal.json`.

## 1. What Run B measures

The modality claim (R7.3-22/23; `results/gemini37-image-gs-2026-09-01/findings.md`)
says "text beats image" is a property of the Gemini 3 family: the within-family
text − image gap at 20 m moved from +0.0549 (Gemini 3) to −0.0115 (Gemini 3.7
proposers under the Gemini 3 verifier) and −0.0043 (all-3.7 stack). Its four
proposer arms ran on four dates (2026-08-18 to 2026-09-01), and on this corpus
same-request runs 20 days apart differed by 0.04–0.06 F1 (S-9). Run B re-runs
the four arms on one day, each with its original configuration, so that both
gaps, and the change between them, carry no date component. The K mismatch in
the original claim (Gemini 3 at K = 10, Gemini 3.7 at K = 5) is addressed by a
K = 5 rung for the Gemini 3 arms (§ 9, § 10 item 4).

What differs from the originals, by design: the **date**, and the **serving
mode** — the originals ran real-time (flex, or standard on the cached path),
Run B runs on the Batch API, as D49 approved and the 2026-09-18 ruling makes
the default for Gemini 3.7. Within-bridge comparisons (the gaps and the gap
change) share the mode, so the mode cancels there; bridge-against-original
comparisons combine date and mode (§ 9).

## 2. The original legs, reconstructed

Sources: each pass meta's `configuration` and `environment` blocks (read on
sapphire, 2026-10-07), the launch drivers in `scripts/`, the session archive
for the grid run, the launch-archaeology attestations
(`reports/launch-archaeology-2026-10-04-proposed-attestations.json` A61, A63,
A65), the passes register (`results/passes-manifest.json`), the
run-conditions register (`results/run-conditions.json`) and each run's card.

### 2.1 Proposer legs

| Field | Gemini 3 text | Gemini 3 image | Gemini 3.7 text | Gemini 3.7 image |
|---|---|---|---|---|
| Run / pool | `grid-2026-08-18` / `g384_ov192` | `image-b-gs-2026-08-28` / `g384_ov192_image` | `gemini37-screen-2026-08-28` / `g384_ov192_g37` | `gemini37-image-gs-2026-09-01` / `g384_ov192_g37img` |
| Passes the claim uses | run_1–10 (K = 10), dates 2026-08-18 | run_1–10 (K = 10), 2026-08-28 | run_1–5 (K = 5), 2026-08-28 | run_1–5 (K = 5), 2026-09-01/02 |
| Recovery fragments | run_4, 8, 10: 1 tile each | run_1, 3, 6, 8: 1 tile; run_9: 2 | run_1–4: 6, 9, 7, 2 tiles | run_1–5: 106, 1,394, 1,397, 1,266, 125 tiles (fd/SSL-storm and flex-storm recovery) |
| Script and commit (meta `environment`) | `4_detect_mounds_batch.py` 6.0.0 at `8e59c9555` | at `c9f178bf7` (runs 1–3), `221031f95` (runs 4–10, recoveries) | at `4cc079f95` (runs 1–4), `8802a9c01` (run 5, recoveries 1–4) | at `7187e8135` (run 1), `1c46243d2` (runs 2–5, recoveries) |
| Launch | session archive `vlm-burial-mound-detection/2026-08-18T00-27_…`: `--model gemini-3-flash-preview --temperature 0.7 --thinking-level minimal --tile-size 384 --tiles-dir inputs/tiles_384_ov192 --mode realtime` (tier default flex) | `scripts/image-b-gs-overnight.sh` (A61): `--mode realtime --service-tier flex --temperature 0.7 --use-cache --workers 12` | `scripts/gemini37-overnight.sh`: `--mode realtime --service-tier flex --temperature 0.7 --model gemini-3.7-flash --thinking-level low` | `scripts/gemini37-image-gs-driver.sh` and `outputs/gemini37-image-gs-2026-09-01/image-gs-recovery-driver.sh`: same flags as 3.7 text, no `--use-cache` |
| Config (sha256) | `detect_brief-text.json` (`a389b24e…`) | `detect_brief-text-image.json` (`3cd75a01…`, md5 `9ff5e64d…`) | `detect_brief-text.json` | `detect_brief-text-image.json` |
| Model requested → recorded | `gemini-3-flash-preview` (CLI) → same | config `gemini-3-flash`, resolved → `gemini-3-flash-preview` | `gemini-3.7-flash` (CLI) → same | `gemini-3.7-flash` (CLI) → same |
| Thinking | minimal (0 thinking tokens) | minimal (0) | low (279 per call) | low (179 per call) |
| Temperature | 0.7 (CLI; config 1.0) | 0.7 | 0.7 | 0.7 |
| Instruction (sha256) | `detect_brief-text.md` `e169b723…` | `detect_brief-text-image.md` `e169b723…` (byte-identical file) | `e169b723…` | `e169b723…` |
| Examples transmitted | none (`include_example_images: false`; E90) | 17 labelled images, config order | none | 17 labelled images |
| `library_hash` recorded (filename basis) | `8580ecb2…` | `8580ecb2…` | `8580ecb2…` | `8580ecb2…` |
| Output budget / format | 8,192 / `application/json` | same | same | same |
| Tile manifest | `inputs/grid-2026-08-18/grid_384_ov192_manifest.json` (`484e00cb…`, 1,398 tiles) | same | same | same |
| Tile tree / size | `inputs/tiles_384_ov192` / 384 px | same | same | same |
| Context caching | none (prefix ~393 tokens) | **explicit** cache: system instruction + preamble + 17 examples, 18,909 tokens on every request, 1 h TTL; the request is the cache's user turn plus a second user turn (transition + tile) | none | **implicit** only (79.5 % of input cached); everything inline in one user turn |
| Serving tier | flex | **standard** (the cached path dropped `service_tier` until `2df65047e`, A61) | flex | flex |
| Per call (mean) | 1,502 in, 149.3 out | 20,028 in (18,916 cached), 118.7 out | 1,502 in, 76.6 out, 279.0 thinking | 20,018 in (15,911 cached), 79.7 out, 179.1 thinking |
| Register cost (K passes) | US$8.38 (flex) | US$25.96 (standard) | US$8.60 (passes 1–5, flex) | US$18.33 (flex) |

### 2.2 Unions, crops and verifier legs

| Field | Gemini 3 text | Gemini 3 image | Gemini 3.7 text | Gemini 3.7 image |
|---|---|---|---|---|
| Union builder | `materialise_grid_unions.py` (2026-08-24) | `image_b_prepare_and_union.py` | the same chain at `--root outputs/gemini37-screen-2026-08-28 --cell g384_ov192_g37 --k 5` (the script's own `--root` help names this run) | the same chain at K = 5 |
| Union parameters | E80 20 m within-pass dedup; E72 exact coverage with additive recovery merge; carrier clip to `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson` (487 tiles); c = 1 union with `vote_count` | same | same | same |
| Union | `union_k10.geojson`, 3,319 | `union_k10.geojson`, 4,065 | `union_k5.geojson`, 791 | `union_k5.geojson`, 674 |
| Crops | `run_pv.py extract` (manifest v2.0, 150 × 150, padding 75, `inputs/rasters`, `inputs/tiles_384_ov192`) | same | same | same |
| Verifier config | `verify_adversarial-text.json` (`357d8a87…`), `verify_adversarial.md` (`2518d529…`), T 0.0, n = 1 | same | same | same |
| Verifier leg(s) the claim used | Gemini 3 (`gemini-3-flash-preview`, minimal), `run_pv.py` at `7f13952ac`, 2026-08-24, real-time flex, 3,319/3,319, US$2.27 | Gemini 3, at `2ccf1b334`, 2026-08-28, real-time flex `--no-strict --workers 10` (A65), 4,065/4,065, US$2.80 | Gemini 3 `verify` (at `b8e130fd3`, 2026-08-28, 791, US$0.56); Gemini 3.7 `verify_swap37` (low, at `5bd514542`, 2026-08-29; 789 + a 2-candidate cleanup whose meta overwrote the main leg's, ≈ US$0.87 token basis per the card) | Gemini 3 `verify_arm1` and Gemini 3.7 `verify_arm2` (low), both at `1c46243d2`, 2026-09-01, 674 each, US$0.48 and US$0.74 |
| Operating point (own sweep best, 20 m) | (0.15, k10): F1 0.8961, P 0.9275, R 0.8668, MCC 0.7965 | (0.15, k9): 0.8412, P 0.8741, R 0.8107, MCC 0.7985 | Gemini 3 verifier (0.10, k5): 0.9139; 3.7 verifier (0.80, k5): 0.9265 | arm 1 (0.10, k5): 0.9254; arm 2 (0.90, k5): 0.9308 |

**A finding about the original claim.** The two image arms did not send the
same request shape: Gemini 3 image used an explicit cache (two user turns,
served at standard), Gemini 3.7 image sent everything inline (one user turn,
flex). The original gap change therefore also carries a request-structure and
a tier difference on the image side. Run B replicates each arm as it ran, so
it inherits this asymmetry; § 10 item 3 offers a leg that would isolate it.

## 3. Does today's code send the same requests?

**Inputs, byte for byte.** At every original commit and at HEAD (`443ae9877`)
the two configs, both instruction files and the tile manifest have identical
blob hashes, and so do the 17 example images (each `example_NN.png` is a
symlink; the link targets were hashed). The tile tree is untracked: it was
swept by a `git stash -u` after the grid run and restored from `stash@{0}^3`
on 2026-08-19 00:18 UTC (`reports/defect-register-2026-08-18.md` N1); all
1,760 PNGs still carry that timestamp, and the 1,398 manifest tiles hash to
`tile_set_sha256 ecc20ef388c010bb…` (sorted name–sha256 pairs). The three
later arms ran on this restored tree; the grid ran on the pre-stash tree,
whose bytes the stash preserved.

**Request-building code, original commits against HEAD.** In
`process_single_tile` the content assembly (preamble text, labelled examples,
transition text, tile) is unchanged at every original commit; the only change
on the request path is that a cached call now copies the whole request config
(`cached_call_config`, `2df65047e`), so it carries `service_tier` — the
original Gemini 3 image calls lost it and were served at standard. In
`detect_mounds_versioned`: the inert-field launch guard (W6.2, E90), tile-size
inference, the cache TTL (1 h → 24 h) and cost accounting changed; none reaches
the request content. The grid's commit `8e59c9555` differs further only in
logging around skipped detections.

**Batch request against the real-time request, executed.** Run B uses the
batch builder (`lib_batch_api.build_jsonl_file`, `create_shared_context_cache`),
which no original leg used. The harness (§ 6) captured the original legs'
real-time invocations at the request and compared them, field by field, with
the batch request for the same tile:

| Field | All four arms |
|---|---|
| Parts: texts, the 17 example images (image arms, by sha256, config order), the tile bytes | SAME |
| System instruction (sha256 `e169b723…`) | SAME (Gemini 3 image: in the cache, SAME) |
| Temperature 0.7; thinking MINIMAL / LOW; 8,192 tokens; `application/json` | SAME |
| Context-cache contents (Gemini 3 image: instruction + preamble + 17 labelled images, one user turn) | SAME |
| Safety settings | **DIFF**: real-time sends four categories at OFF; the batch builder sends none (the Batch API rejects them, `lib_batch_api.build_jsonl_file`) |
| Service tier | DIFF: flex (or standard on the original cached path) against batch |
| Content role, cache name | representation only (`user` against unset; placeholder name) |

**Hashes against the original metas.** System-instruction hash `e169b723…`
matches every original meta. The library hash the originals recorded
(`8580ecb2…`) is the pre-2026-09-12 filename hash; recomputed from today's
config it is `8580ecb2…`. The bridge metas will record the content-basis hash
`7c9bbcec…` (`library_hash_basis: example-bytes+path-label-category/1`),
which is not comparable by design (`reports/name-keyed-cache-audit-2026-09-12.md`
Finding 5). Tile set: every bridge pass dispatches the manifest's 1,398 tiles,
the same names the originals completed, with digest `ecc20ef3…`.

**Not verifiable offline.** The model snapshot behind each name (metas record
only the alias); the Batch API's default safety thresholds; the SDK version at
the original runs (the lock file pins `google-genai==1.71.0`, unchanged since
2026-04-09, and sapphire has 1.71.0; the batch request is hand-built JSON, not
SDK-serialised).

## 4. Stage 1: commands and launch

### 4.1 Preconditions

1. Stage 0 (gate § 2) shows both `gemini-3-flash-preview` and
   `gemini-3.7-flash` in the served-model listing. Its result is not recorded
   in the repository as of `443ae9877`.
2. Run A's legs are terminal and committed, and their File API uploads are
   deleted (agent guidance § Compute Location), so Stage 1 has its headroom
   (§ 4.3).
3. The PI approves this card: the commands, the ceiling of § 5 and the
   decisions of § 10.
4. This branch is merged and pulled into sapphire's main checkout, which holds
   `.env`, `.venv` and the untracked `inputs/tiles_384_ov192`.

### 4.2 Commands

From `~/Code/map-reader-llm` on sapphire. Every pass is one
`4_detect_mounds_batch.py --mode batch` invocation; `plan` prints all 30:

```bash
bash scripts/modality-bridge-2026-10-07-stage1.sh plan
```

Per arm, for pass N (`--output-dir outputs/modality-bridge-2026-10-07/<arm>`,
`--run N`; common to all: `--manifest inputs/grid-2026-08-18/grid_384_ov192_manifest.json
--tiles-dir inputs/tiles_384_ov192 --temperature 0.7 --mode batch
--service-tier flex --skip-intent-check`):

| Arm | Passes | Arm-specific flags |
|---|---|---|
| `g3-text` | 1–10 | `--config prompts/configs/detect_brief-text.json --model gemini-3-flash-preview --thinking-level minimal --tile-size 384 --allow-inert-fields` |
| `g3-image` | 1–10 | `--config prompts/configs/detect_brief-text-image.json --model gemini-3-flash-preview --use-cache` |
| `g37-text` | 1–5 | `--config prompts/configs/detect_brief-text.json --model gemini-3.7-flash --thinking-level low --allow-inert-fields` |
| `g37-image` | 1–5 | `--config prompts/configs/detect_brief-text-image.json --model gemini-3.7-flash --thinking-level low --max-batch-tiles 466` |

Why each flag beyond the originals': `--mode batch` (D49); `--model
gemini-3-flash-preview` on the image arm pins what the original resolved the
config's `gemini-3-flash` to, so no newer release can answer to the alias;
`--allow-inert-fields` lets the text configs launch exactly as the originals
were sent (the guard post-dates them; without it the launch is refused, § 6);
`--max-batch-tiles 466` cuts a 3.7 image pass into three jobs of 466 tiles,
because its inline requests average 2.70 MB and a 1,398-line file (3.77 GB)
would exceed the Batch API's 2 GB per-file limit; `--service-tier flex` sets
the tier of the runner's synchronous parse-failure retries; `--skip-intent-check`
prevents an interactive prompt under `nohup`. `--thinking-level minimal
--tile-size 384` on `g3-text` repeat the grid's own flags (both equal the
effective values). No flag changes a request against the originals except the
mode.

Outputs: `outputs/modality-bridge-2026-10-07/<arm>/<config version>/run_<N>/
detections_<version>_run<NN>.{geojson,meta.json,tiles.json}` (3.7 image also
per-chunk files, merged when all three land); logs and pid files under
`outputs/modality-bridge-2026-10-07/{logs,pids}/`; request files under
`…/batch_working/` (gitignored).

### 4.3 Lodging order and the File API

Request files measured in the rehearsal: `g3-text` 463,984,582 bytes per pass,
`g3-image` 461,610,778, `g37-text` 463,978,990, `g37-image` 3,770,325,880
(three files of 1.25–1.26 GB). All 30 passes total 30.4 GB, against a 20 GiB
(21.47 GB) project cap and a preflight budget of 19.47 GB (cap less one 2 GB
chunk). They cannot all be stored at once. `lodge all` therefore lodges in
this order, one pass at a time, starting the next only after the previous has
logged `Submitted batch job` (plus 60 s, so the upload leaves `PROCESSING`):
`g37-image` 1–5 (first chunk each), `g37-text` 1–5, `g3-image` 1–10,
`g3-text` 1–10. Peak storage is then 17.86 GB. Each 3.7 image pass lodges its
second and third chunks only after its previous chunk's job completes; by then
the safe sweep (`make_safe_sweep`) can reclaim completed jobs' inputs. If a
preflight still refuses, that pass exits before uploading (no spend) and
`lodge` stops; re-run `lodge all` later — it skips live and landed passes and
resumes a chunked pass at its first unlanded chunk.

### 4.4 Launch sequence

```bash
cd ~/Code/map-reader-llm
bash scripts/modality-bridge-2026-10-07-stage1.sh lodge g37-image:1
```

Then the recommended cost gate (§ 10 item 1): when `status` shows the first
chunk of `g37-image-run1` landed, read its `cached` share. At 0.5 or above,
continue; below, stop and return to the PI.

```bash
bash scripts/modality-bridge-2026-10-07-stage1.sh status
bash scripts/modality-bridge-2026-10-07-stage1.sh lodge all
```

If the PI waives the gate, `lodge all` alone submits everything. Launch
hygiene, as the launcher implements it: each pass starts detached with all
three descriptors redirected (`>> log 2>&1 < /dev/null &`) and nothing after
it on its line; its pid goes to a pid file; `lodge` refuses to re-lodge a pass
whose log shows more submitted jobs than landed chunks (a job may still be
running on the service, and its name lives only in the log). **Never kill a
polling pass**: its job keeps running and is orphaned.

### 4.5 Watcher

- `status` (no API): per pass, process alive or gone (`kill -0` on the pid
  file, never `pgrep -f`), log age, terminal state from
  `scripts/wait_for_run.py`'s classifier, tiles completed and failed, cached
  share, and failure lines matched case-insensitively on `failed|lost|partial|
  completeness gap|traceback|error|cache creation failed|refused`.
- For chains, wait on a terminal state, never a success string:
  `.venv/bin/python scripts/wait_for_run.py --log outputs/modality-bridge-2026-10-07/logs/<arm>-run<N>.log --pidfile outputs/modality-bridge-2026-10-07/pids/<arm>-run<N>.pid --stale-seconds 3600`
  (exit 0 success, 2 partial, 3 crashed, 4 stale, 5 stopped). A polling batch
  pass writes a line every 30 s, so an hour of silence is a hang.
- `g3-image` passes must each log `batch unit will reference cache`; a
  `context cache creation failed` line means that pass fell back to inline
  requests (a different request shape) and must be discarded and re-lodged.

### 4.6 Recovery to exact coverage

When every pass is terminal: `residuals` (no API) writes
`<arm>/residual_run_<N>.json` for each landed pass short of 1,398 tiles and
names any pass that has not landed (resume those with `lodge`, not
`recover`). `ROUND=1 … recover` lodges one additive fragment per residual with
the identical invocation (only `--manifest` and `--output-dir
<arm>/recovery_rd1` differ), the originals' additive-fragment pattern. Repeat
with `ROUND=2` until `residuals` reports none. Keep recovery on the same day.

### 4.7 After landing (before Stage 2)

1. Coverage 1,398/1,398 per pass, main plus fragments.
2. `g3-image`: about 18,909 cached tokens per call on every pass (the explicit
   cache engaged); thinking tokens 0 on both Gemini 3 arms and non-zero on
   both 3.7 arms; record the 3.7 image implicit cached share.
3. Finish reasons and safety blocks per pass (the originals had 0 safety
   blocks).
4. The served window per arm: from the launcher's `SUBMITTED` stamp in each
   log to the pass meta's write time (the batch meta records no job times).
   Later chunks of a 3.7 image pass are stamped only by the detector's own
   `Submitted batch job` line, so read their window from the chunk metas.
5. Audited cost per pass (`scripts/audit_proposer_cost.py`), against § 5.
6. Commit the pass outputs (geojson, meta, tiles.json, logs); delete the File
   API uploads once committed, and the `batch_working/` request files on
   sapphire (about 30 GB, trivially rebuilt). The ten `g3-image` caches expire
   after 24 h.

## 5. Calls and cost

Rates: `data/pricing/gemini-rate-card.json` v2026-09-21.2, batch rows; per-call
token profiles: the original legs' metas (main and recovery fragments).

| Arm | Calls | Basis | Estimated cost |
|---|---:|---|---:|
| Gemini 3 text | 13,980 | 1,502 in, 149.3 out per call, no cache | US$8.38 |
| Gemini 3 image | 13,980 | 18,916 of 20,028 in read from the explicit cache at US$0.05/M (the batch discount does not apply to cache reads on Gemini 3), 118.7 out; plus cache storage for ten 24 h caches of 18,909 tokens at US$1.00/M·h | US$19.60 + US$4.54 |
| Gemini 3.7 text | 6,990 | 1,502 in, 76.6 out + 279.0 thinking | US$8.60 |
| Gemini 3.7 image | 6,990 | 20,018 in, 79.7 out + 179.1 thinking; implicit-cache hits under batch are unknown | US$22.50 at the original 79.5 % share read at US$0.075/M (the rate the September batch invoices show for 3.7 cache reads, `planning/cost-accounting-fix-plan-2026-09-21.md` § 8 item 10); US$18.33 at the card's US$0.0375; **US$55.86 with no hits** |
| **Stage 1 total** | **41,940** | | **likely US$63.6; range US$59.5–97.0** |

Against the gate: its Gemini 3 image figure (US$25.96) was the original's
standard-tier cost; on batch it is US$19.60 plus storage. The 3.7 image figure
(US$18.33) assumed the original cache share at the card's cache rate; the
ceiling is US$37.5 higher. Stage 1 can therefore exceed the gate's "about
US$61" by up to US$36; the cost gate of § 4.4 caps that exposure at the first
chunk of one pass (about US$3.7 if uncached).

**Stage 2 (for its own gate)**, batch, at the original union sizes and the
register's per-candidate rates:

| Leg | Candidates (original) | Estimated cost |
|---|---:|---:|
| Gemini 3 text K = 10, Gemini 3 verifier | 3,319 | US$2.27 |
| Gemini 3 image K = 10, Gemini 3 verifier | 4,065 | US$2.80 |
| Gemini 3.7 text K = 5, Gemini 3 verifier | 791 | US$0.56 |
| Gemini 3.7 text K = 5, Gemini 3.7 verifier | 791 | US$0.87 |
| Gemini 3.7 image K = 5, Gemini 3 verifier | 674 | US$0.48 |
| Gemini 3.7 image K = 5, Gemini 3.7 verifier | 674 | US$0.74 |
| **Six legs** | **10,314** | **US$7.72** |
| Optional: Gemini 3 text and image K = 5 unions, Gemini 3 verifier | 2,932 + 2,788 | US$3.93 (the gate's "about US$1.50" is below the register's own K = 5 legs, `g384_ov192-k-ladder-k5-verify` US$2.01 and `g384_ov192_image-union-k5-verify-arm1` US$1.92); US$0 if inherited (§ 10 item 4) |

Run B likely total: about US$71 (inherited K = 5) to US$75 (dedicated);
ceiling about US$109.

## 6. API-free rehearsal (the Stage 1 dry runs)

**Why not the detector's `--dry-run`.** In batch mode it creates a
`genai.Client` and lists the served models before its dry-run branch
(`_detect_mounds_batch`, `scripts/4_detect_mounds_batch.py` lines 1583–1593).
In real-time mode it does the same, and with `--use-cache` it also creates a
billable context cache before returning (lines 889–1076 against the dry-run
return at 1235), which it never deletes. Neither is API-free.

**The harness.** `scripts/bridge_dryrun_harness.py` runs the detector's own
`__main__` with the launcher's exact arguments plus `--dry-run`, after (1)
blocking every socket connection and name lookup in the process, (2) replacing
`google.genai.Client` with a stub whose only capability is `models.list()`
returning the pinned name (every other attribute raises), and (3) setting a
placeholder key. Every refused call is recorded as a breach. It wraps
`run_batch_unit` to record each chunk's plan, and for pass 1 of each arm builds
the complete request file with the real `prepare_batch_unit`, summarises it and
deletes it. Tier-1 tests: `tests/test_bridge_dryrun_harness.py` (a deliberate
breakage of the connect guard turns the socket test red).

**Results** (sapphire, disposable worktree at `443ae9877` plus this branch's
files, 2026-10-07; full record in the rehearsal JSON):

| Arm | Passes | Requests per pass (jobs) | Dispatched tiles: bridge / original | Exit; breaches; stub clients | Request file per pass | Signature (tile elided) |
|---|---:|---|---|---|---:|---|
| `g3-text` | 10 | 1,398 (1) | 1,398 / 1,398 | 0; 0; 1 | 464.0 MB | one per arm, `58cf1f1f…` |
| `g3-image` | 10 | 1,398 (1) | 1,398 / 1,398 | 0; 0; 1 | 461.6 MB | `167b1c95…` (cache placeholder) |
| `g37-text` | 5 | 1,398 (1) | 1,398 / 1,398 | 0; 0; 1 | 464.0 MB | `6d349600…` |
| `g37-image` | 5 | 1,398 (3 × 466) | 1,398 / 1,398 | 0; 0; 1 | 3,770.3 MB | `4eef5736…`, the same in all three chunks |
| **Total** | **30** | **41,940** | | | **30.43 GB** | |

Each full build: line keys equal the manifest in order; every line of an arm
has one signature; tile digest `ecc20ef3…`. Model, cache use, temperature 0.7,
thinking level and tile size 384 are as § 4.2 on every pass. Negative control:
`g3-text` pass 1 without `--allow-inert-fields` is refused
(`InertConfigurationError`, exit 1) before any client is created.

## 7. Pre-launch audit (`/audit-config`, adapted to a replication)

The "requirements" are the original legs' recorded configurations (§ 2); the
preregistration does not govern this post-hoc replication (D47, D49).

```text
=== PRE-LAUNCH AUDIT: Run B Stage 1 (modality bridge, four proposer arms) ===

1. REQUIREMENTS: 16, from the original legs' metas, drivers and attestations
   R1  config file per arm (detect_brief-text / detect_brief-text-image)
   R2  model: gemini-3-flash-preview (G3 arms), gemini-3.7-flash (3.7 arms)
   R3  thinking: minimal (G3), low (3.7)
   R4  temperature 0.7 (CLI override of the config's 1.0)
   R5  system instruction sha256 e169b723…
   R6  examples: none transmitted (text), 17 labelled images in config order (image)
   R7  library composition hash 8580ecb2… (filename basis)
   R8  max_output_tokens 8192, response_mime_type application/json
   R9  tile manifest grid_384_ov192 (1,398 tiles, 484e00cb…), tile bytes unchanged
   R10 tile size 384
   R11 K: 10 / 10 / 5 / 5
   R12 request structure: G3 image explicit cache (two user turns); 3.7 image
       inline (one turn); text arms inline
   R13 example ordering: config default (no --ordering override)
   R14 coverage: exactly 1,398 tiles per pass after additive recovery (E72)
   R15 serving: real-time flex (G3 text, both 3.7), standard (G3 image)
   R16 safety settings: four categories at OFF (real-time path)

2. CONFIG DIFF across the four arms: 9 fields identical, 6 differ
   Controlled (identical): manifest, tiles dir, temperature 0.7, max tokens,
     response format, instruction text (the two files are byte-identical),
     example list and order, mode batch, retry tier flex
   Manipulated: config/include_example_images (modality) EXPECTED;
     model + thinking (family) EXPECTED;
     --use-cache (G3 image only) EXPECTED as originally run — inherited
       asymmetry, see WARNINGS;
     --max-batch-tiles (3.7 image only) packaging only, no request change;
     --allow-inert-fields (text arms) launch guard only, no request change;
     --thinking-level minimal --tile-size 384 (g3-text) equal the effective
       values
   Confounds: none introduced by Run B; one inherited (WARNING 1)

3. TRANSMISSION CHECK (rehearsed requests, every arm)
   Error mode              g3-text  g3-image  g37-text  g37-image
   Image flag              PASS     PASS      PASS      PASS
   Temperature shadowed    PASS     PASS      PASS      PASS
   Thinking level          PASS     PASS      PASS      PASS
   Model version drift     PASS     PASS      PASS      PASS   (pinned; Stage 0 confirms)
   Tile size               PASS     PASS      PASS      PASS
   Wrong tile set          PASS     PASS      PASS      PASS
   Wrong instruction       PASS     PASS      PASS      PASS
   Example paths           PASS     PASS      PASS      PASS
   Example dimensions      PASS     PASS      PASS      PASS   (bytes unchanged)
   Agent model unpinned    n/a      n/a       n/a       n/a    (no agents; API model pinned)
   Blockers: none

4. ALIGNMENT with R1–R16
   Matches: 13 now (R1–R13); R14 is checked after the run (§ 4.7)
   Deliberate deviations: 2 — R15 and R16, both consequences of the Batch API
     (D49; 2026-09-18 ruling). R16 is not named in the gate: recorded here
     for the PI's explicit acknowledgement (§ 10 item 2)
   Undocumented deviations: 0

5. DRY-RUN: PASS — 30/30 passes, 41,940 requests, 1,398 tiles per pass
   (original 1,398), 17 examples on image requests, 0 breaches,
   0 tile-size or missing-example warnings

6. EVALUATION SCOPE: PASS (Stage 1 scores nothing; Stage 2 uses the originals'
   frame: 487-tile common footprint, curator reference, 20 m; no holdout
   applies — every original cell was its own sweep oracle)

7. COMPLETENESS — not checkable offline: the model snapshot behind each name;
   Batch API safety defaults; 3.7 image implicit-cache hits under batch (cost
   only); the SDK version of the original runs; Run A's File API usage at
   launch; the Stage 0 listing (not recorded in the repository)

BLOCKERS: none outstanding. Found and fixed in the launcher: the 3.7 image
  pass's single request file (3.77 GB) exceeded the 2 GB per-file limit
  under the default chunking; --max-batch-tiles 466 gives three 1.26 GB files.
WARNINGS:
  1. Inherited asymmetry: G3 image cached (two turns), 3.7 image inline (one)
  2. Safety settings are not sent in batch (originals: OFF x 4; 0 blocks)
  3. 3.7 image cost depends on unmeasured implicit caching (US$18–56)
  4. File API: 30.4 GB of requests against a 19.47 GB budget; lodging is
     staged and Run A's uploads must be cleared first
  5. Parse-failure retries are synchronous inline calls (for G3 image they
     bypass the cache for the few retried tiles)
  6. Stage 0 result not recorded

OVERALL: READY TO LAUNCH, once the four preconditions of § 4.1 hold
```

## 8. Stage 2: plan, and what its own gate must check

1. **Layout adapter.** The union chain's `resolve_pass_paths`
   (`scripts/stride_prepare_and_union.py`) globs `run_<N>/detections-*.geojson`
   and `run_<N>_recovery/`; batch passes are `<arm>/<version>/run_<N>/
   detections_<version>_run<NN>.geojson` with fragments under
   `<arm>/recovery_rd<R>/<version>/run_<N>/`. A small, tested adapter is needed
   (exclude `_chunk` files; fold every fragment).
2. **Unions.** `image_b_prepare_and_union.py` chain (E80 20 m, E72 exact
   coverage, carrier clip, c = 1, `vote_count`): K = 10 for both Gemini 3 arms,
   K = 5 (runs 1–5) for both 3.7 arms; pass order pinned numerically
   (`reports/w27-replicate-floors-2026-10-06.md` § 8 item 4). Optional K = 5
   unions for the Gemini 3 arms.
3. **Crops.** `run_pv.py extract --proposer <union> --output-dir <crops>
   --tiles-dir inputs/tiles_384_ov192` (rasters and padding at their defaults,
   as the originals).
4. **Union provenance guard.** `scripts/check_union_provenance.py` on every
   crop manifest (`run_pv.py verify` runs it on both paths and refuses a
   disagreeing manifest).
5. **Verifier legs** on the Batch API: `run_pv.py verify --mode batch
   --verifier-config prompts/configs/verify_adversarial-text.json
   --temperature 0.0` with `--model gemini-3-flash-preview` (the originals
   resolved the config's `gemini-3-flash`) or `--model gemini-3.7-flash
   --thinking-level low`. Rehearse the batch verifier request against the
   original real-time verifier request with the same harness approach before
   any spend; the config and instruction blobs are unchanged (`357d8a87…`,
   `2518d529…`).
6. **Analysis scripts.** `image_b_analysis.py` and `gemini37_image_gap_test.py`
   hard-code the original roots and anchors; they need parameterised entry
   points, and an anchor gate that reproduces the six original cells (0.8961,
   0.8412, 0.9139, 0.9265, 0.9254, 0.9308) to 1e-3 before any bridge number is
   written.

## 9. Post-run scoring plan

Frame for every cell: the 487-tile common footprint
(`outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson`), curator
reference `inputs/vectors/references/mounds-reference.geojson`, 20 m primary
buffer (curves at 20, 30, 50 and 75 m), per-tile counts, round-robin tile-swap
permutation with 10,000 permutations and seed 42.

1. **Each cell at the original protocol:** the full (prob_t × k) sweep and its
   best point, as every original cell was chosen.
2. **Each cell at the original operating point:** Gemini 3 text (0.15, k10),
   Gemini 3 image (0.15, k9), 3.7 text under the Gemini 3 verifier (0.10, k5)
   and under the 3.7 verifier (0.80, k5), 3.7 image arm 1 (0.10, k5) and arm 2
   (0.90, k5).
3. **Gaps, text − image:** Gemini 3 (K = 10); 3.7 with the Gemini 3 verifier
   (K = 5); all-3.7 (K = 5), each with its tile-swap p.
4. **Gap change**, both 3.7 variants minus Gemini 3, with a tile-level
   interaction permutation (each tile's text and image labels swapped within
   both families together, the grid's interaction instrument) — the p the
   original could not compute across campaigns.
5. **K-matched:** the Gemini 3 gap at K = 5 (first five passes), inherited or
   dedicated (§ 10 item 4), against the 3.7 gaps.
6. **Date component per arm:** bridge minus original at the original point and
   at the oracle, with same-tile flip rates; reported as date plus serving
   mode, never as date alone.
7. **Against the floors** (D45, D46): the within-execution 487-tile floors
   apply, since all arms share one execution; the gap change needs its own
   floor, estimated from disjoint pass subsets as D46 prescribes.

## 10. Decisions for the PI

1. **Cost ceiling and the 3.7 image gate.** Approve Stage 1 at likely
   US$63.6, ceiling US$97.0. Recommended: the § 4.4 gate on the first chunk of
   `g37-image-run1` (continue at a cached share of 0.5 or more; otherwise
   return to the PI). Alternative: `lodge all` at once, accepting the ceiling.
2. **Batch request differences.** Acknowledge that the batch requests omit the
   four OFF safety settings the originals sent, and are served on the batch
   tier, not flex or standard.
3. **The inherited request-structure asymmetry** (§ 2.2). Default: replicate
   as run. Option: a fifth leg — 3.7 image K = 5 with `--use-cache` (about
   US$16 plus storage; outside D49) — would show whether the cached shape
   alone moves the 3.7 image cell.
4. **The Gemini 3 K = 5 rung:** inherited from the K = 10 verification (free;
   the image-B ladders' method) or dedicated K = 5 unions verified
   (US$3.93).
5. **The model pin** for the Gemini 3 image arm (`gemini-3-flash-preview`
   instead of the config's alias): recommended.

Hazards found on the way, not fixed here (each wants its own small change):
the detector's `--dry-run` is not API-free (§ 6), and with `--use-cache` in
real-time mode it leaves a billable cache; `run_batch_unit` passes
`include_example_images` from the study config rather than the prompt config
to `create_shared_context_cache`, so a text config run with `--use-cache` in
batch would cache the 17 example images (not triggered here: no text arm uses
the cache); the batch path never deletes its caches; and a dead polling
process orphans its job, whose name survives only in the log.

## Changelog

### 2026-10-07 — Original publication (Session 162)

Written at the PI's request after D49: reconstruction of the four original
legs, code-equivalence checks, the Stage 1 launcher
(`scripts/modality-bridge-2026-10-07-stage1.sh`), the API-free rehearsal
harness (`scripts/bridge_dryrun_harness.py`) and its record
(`planning/modality-bridge-2026-10-07-rehearsal.json`), costs, and the
pre-launch audit. Nothing was submitted.
