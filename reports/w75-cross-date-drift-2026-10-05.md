# W7.5 / S-9: same request on two dates, different outputs

> **Last revised**: 2026-10-05 (original publication, Session 161). See
> [§ Changelog](#changelog) for revision history.

**Status: investigated; leading explanation serving-side drift between
2026-03-27 and 2026-04-16 (not confirmable without a paid re-send).** Written
by a read-only research agent for tracker item W7.5; two load-bearing claims
were checked at source before use: `76a2cc719` (2026-03-28) is the commit that
landed the cached path, and between it and `b57cf6c22` no diff hunk touches the
per-tile parts, the cached-call configuration or the cache creation. The
`model_version` of all 1,461 `n1-outstanding` responses per group
(`gemini-3-flash-preview`) was re-checked separately; E57 stands.

Read-only investigation, 2026-10-05. No repository file was edited, and no Gemini Application Programming Interface (API) call was made. Request bodies were captured offline with the SDK's HTTP layer patched out (see § 5).

## Summary

Nothing in the request differs between March and April. The March run used `scripts/4_detect_mounds_batch.py` as nine uncommitted Edit calls had left it, on top of `bb73b52f5`. I replayed those edits onto `bb73b52f5` and the result is byte-identical to the file at commit `76a2cc719` (2026-03-28). Between `76a2cc719` and `b57cf6c22` the explicit-cache path did not change: the same cache contents, per-tile parts, `GenerateContentConfig` fields and raw-PNG encoding. The inputs are also the same: tiles, examples, config and instruction match in git history and hash identically on amd-tower and sapphire today. The google-genai Software Development Kit (SDK) did differ (1.67.0 in March, 1.71.0 in April). Even so, both versions serialise identical request bodies. Only the `user-agent` and `x-goog-api-client` headers differ.

The execution context did differ: the machine, the quota tier and governor, and concurrency (one request every ~1.2 s against 487 requests in ~40 s). Most likely the systematic difference is serving-side drift between 2026-03-27 and 2026-04-16. At T = 0.0 HIGH, runs on the same date agree tile by tile (300 of 312 tiles in March, 331 of 333 in April). Across the two dates, only 205 of 363 agree. No third execution of either setting exists. Caveat: the HIGH-group counts quoted in the brief include July 2026 recovery requests that were built differently (§ 6).

## 1. March code (n1-outstanding-384, 2026-03-27)

**Archive:** `~/cc-archives/map-reader-llm/2026-03-26T06-38_complete-multi-buffer-and-tile-level/session.jsonl.gz`. The alias `~/cc-archives/vlm-burial-mound-detection/` holds no March 2026 sessions; its earliest directory is `2026-05-23T07-46_…`. The line numbers below are 1-based lines of the decompressed JSONL.

### 1.1 Launch evidence

| JSONL line | UTC | Content |
|---:|---|---|
| 1818–1858 | 2026-03-27 05:34:33–05:36:36 | Nine `Edit` calls to `scripts/4_detect_mounds_batch.py`. They add `use_cache` (1818), the cache-creation block (1823), the `cache_name` parameter of `process_single_tile` (1827), the cached per-tile parts branch (1831), the cached `call_config` (1835), `cache_name` passed to the executor (1839), cache deletion (1850), the `--use-cache` CLI flag (1854), and `use_cache=args.use_cache` (1858). |
| 1869–2003 | 05:37:02–05:45:56 | Edits to `scripts/run_phase2.py` that forward `--use-cache` to each unit. |
| 2010 | 05:46:22 | `Write` of `studies/h11-384-n1-outstanding.yaml`. Both image cells use `config: prompts/configs/library_plus-hp.json`; `pro-image-high-t0` also lists `model: gemini-3.1-pro`. |
| 2015–2016 | 05:46:37 | Dry run printing the per-unit command: `… 4_detect_mounds_batch.py --config …/prompts/configs/<cfg>.json --manifest …/inputs/tiles_384/full_evaluation_manifest.json --output-dir … --output … --workers 12 --temperature 0.3 --thinking-level minimal --tile-size 384 --tiles-dir …/inputs/tiles_384 --use-cache`. |
| 2027 | 05:47:11 | Launch on amd-tower (local `.venv`): `nohup python scripts/run_phase2.py studies/h11-384-n1-outstanding.yaml --use-cache --workers 3 > outputs/h11/n1-outstanding-run.log 2>&1 &`. |
| 2117 | 10:24:29 (result) | A `grep` of the run log prints `Context cache created: cachedContents/… (14549 tokens, TTL=1h)` nine times, each followed by `Context cache deleted`. The log is not in the repository. |
| 2129 | 10:25:15 (result) | `--patch-tiles` for `pro-image-high-t0`: "Tiles recovered: 0" in both modes, so no March tile came from a patch request. |
| 1654 | 05:28:56 (subagent progress record) | A local `find` of `/home/shawn/Code/map-reader-llm/.venv/lib/python3.13/site-packages` lists `google_genai-1.67.0.dist-info` (dated Mar 13). |

The model ran on Flash, not Pro, because `run_phase2.py` passes `--model` only from its own CLI (`model_override`, line 739 of `run_phase2.py` at `76a2cc719`). It ignores the study YAML's per-condition `model`.

### 1.2 The March code is the file at `76a2cc719`

- **Replay check.** I applied the nine `old_string`→`new_string` edits (lines 1818–1858) to `git show bb73b52f5:scripts/4_detect_mounds_batch.py`. Each `old_string` occurs exactly once. The result is byte-identical to `git show 76a2cc719:scripts/4_detect_mounds_batch.py` (SHA-256 `2c28259244ee…` for both). `git diff bb73b52f5 76a2cc719 -- scripts/4_detect_mounds_batch.py` contains exactly these edits and nothing else.
- **The runner too.** Replaying the transcript's `run_phase2.py` edits onto `bb73b52f5` gives a file byte-identical to `run_phase2.py` at `76a2cc719`.
- **Commit `76a2cc719`** ("fix(scripts): tile detection bug fixes and context caching support", 2026-03-28T18:16:52+11:00) is the commit that landed the cache path. Its commit message also claims tiles_dir and tile-size fixes for the detect script, but its diff for that file holds only the cache edits.
- **No other route changed the file before launch.** No Bash `sed -i`, `git checkout`, `stash` or `restore`, and no scp or rsync, touches the detect script before line 2027. No subagent Edit or Write touches it. The 2026-03-27T12-24 and 2026-03-28T05-45 sessions do not edit it. One earlier edit (`2026-03-24T09-55…`, line 2453, 2026-03-25T04:48Z: `model_override=model_name_cfg`) is already in `bb73b52f5`.
- **One malformed line.** Line 1330 of the archive does not parse as JSON. It is a truncated `Write` of `scripts/sapphire-n1-eval.sh`, not the detect script.
- **Libraries.** The detect script imports `config`, `scripts.lib_llm_metadata` and `scripts.lib_token_bucket`. The session's one `lib_llm_metadata.py` edit (line 1299) changes only the `PRICING` table. `lib_batch_api.py` edits belong to the batch path, which the real-time path does not import at `76a2cc719`.

### 1.3 What the March code sent

Line numbers refer to `76a2cc719:scripts/4_detect_mounds_batch.py`, which is byte-identical to the March working file.

**(a) Cache** (`client.caches.create`, lines 872–908):

- `system_instruction` = the text of `prompts/system-instructions/detect_brief-text-image.md` (SHA-256 `e169b7237b85…`).
- `contents` = one `Content(role="user")` whose parts are, in order:
  1. text `"Here are the Reference Symbols you must find:"` (line 876);
  2. for each of the 13 examples in config order (loop at line 819), a text part carrying the label (line 826), then the image bytes (lines 830–833).
- The label sequence is `Positive` × 8 (examples 01–08), then `Negative` × 5 (09, 10, 15, 16, 17). The three null examples are labelled `Negative`; there is no separate null-tile text.
- `display_name="detect-library_plus-hp"`, `ttl="3600s"`.

**(b) Per-tile `contents`** (lines 319–329, wrapped at line 351): one `Content` with no role and two parts:

1. text `"Now, find detection instances that visually match ANY of the above Reference Examples in the Target Map Tile below:"`;
2. the tile bytes.

**(c) Cached-call config** (lines 376–385; `generate_content(..., config=call_config)` at line 391): `cached_content`, `temperature`, `max_output_tokens` (8192 from the config), `response_mime_type="application/json"`, `thinking_config=ThinkingConfig(thinking_level=…)` and `safety_settings` (four categories, all `OFF`). There is no `system_instruction` (it lives in the cache), no response schema, no `media_resolution`, no `service_tier` (the March code had none anywhere) and no seed. Client: `http_options={"api_version": "v1alpha"}` (line 755).

**(d) Image encoding.** Tiles are read with `open(tile_path, "rb").read()` (line 312) and sent as `image/png`. There is no decoding, resizing or re-encoding. Example images are sent the same way, as raw file bytes with the MIME type taken from the suffix (`image/png`). The tiles are 384 × 384 RGB. Example 01 is 212 × 189, example 05 is 128 × 128, and example 15 is 512 × 512.

## 2. April code (pv-diag-384, 2026-04-16, `b57cf6c22`)

**Archive:** `~/cc-archives/map-reader-llm/2026-04-16T05-56_b089991e/session.jsonl.gz`.

- **Launcher.** Lines 729 and 768 write and then fix `scripts/run_phase3a_image_matrix.sh`. Its `COMMON_FLAGS` are `--config prompts/configs/library_plus-hp.json --manifest inputs/tiles_384/full_evaluation_manifest.json --tiles-dir inputs/tiles_384 --tile-size 384 --mode realtime --service-tier flex --use-cache --workers 250`, plus `--output-dir … --temperature T --thinking-level L` per run. It ran on sapphire (relaunch at line 829, 09:22:24Z).
- **Sapphire's working tree was clean for the detect script.** At line 243, sapphire's HEAD is `b57cf6c2`. At line 245, `git pull --ff-only` failed because of local changes to `scripts/fuse_detections_wbf.py` only. The incoming range included `6a7c3ed8c`, which modifies `4_detect_mounds_batch.py`, and git did not list that file, so it had no local changes. No scp or rsync of the detect script to sapphire appears in the 04-15 or 04-16 sessions or their subagents.
- **SDK.** The session `2026-04-15T07-08…` shows sapphire at google-genai 1.68.0 (line 700), upgraded to 1.71.0 at 08:44:14Z (lines 708–709). The dist-info on sapphire today is dated 2026-04-15 08:44:15Z and is still 1.71.0. Separately, amd-tower went from 1.67.0 to 1.73.1 on 2026-04-15T06:23Z (`2026-04-14T13-21…`, lines 847–848 and 1108–1109); that confirms 1.67.0 was amd-tower's version until then.

The request code at `b57cf6c22` (lines of `git show b57cf6c22:scripts/4_detect_mounds_batch.py`) has the same text and structure as March. Every line moved by about 1 to 10 because of unrelated additions:

- **(a) Cache:** lines 882–918. The preamble text is at 886, `caches.create` at 893, `system_instruction` at 896, `role="user"` at 898 and `ttl="3600s"` at 901. The examples loop starts at line 822 (label 829, MIME type 833, bytes 834).
- **(b) Per-tile parts:** lines 320–330; `Content` at line 352.
- **(c) Cached-call config:** lines 377–386; `config=call_config` at line 392. The field list is the same as in March. `service_tier` is added only to `gen_config_kwargs` (lines 874–875), which the cached call does not copy, so `--service-tier flex` had no effect on these requests (as the launch archaeology states, § 3). Client `api_version="v1alpha"` at line 758.
- **(d) Encoding:** tile read at line 313, `image/png`; examples are raw bytes as in March.

`git diff 76a2cc719 b57cf6c22 -- scripts/4_detect_mounds_batch.py` has these hunks:

- import `PIL.Image`;
- the `service_tier` and `skip_intent_check` parameters, and `gen_config` rebuilt from a kwargs dict with an optional `service_tier`;
- `run_launch_checks` (experiment-intent guard, called after the cache and config are built);
- `glob` → `rglob` in tile discovery;
- a check that tile dimensions match;
- thread-pool size `max(60, workers)`;
- the new `_detect_mounds_batch` function and `--mode`, `--run`, `--max-batch-tiles`, `--service-tier` and `--skip-intent-check` flags.

No hunk touches the cache contents, the per-tile parts or the cached `call_config`. Across the imports, `lib_llm_metadata.py` and `config.py` are unchanged. `lib_token_bucket.py` changes only its default limits (from 1 M TPM / 2 K RPM to 20 M / 20 K).

## 3. Difference table

| # | Item | March (2026-03-27) | April (2026-04-16) | Request-level? | Could plausibly change output? |
|---|---|---|---|---|---|
| 1 | Cache: system instruction, preamble, 13 label/image pairs, order, TTL, display name | as § 1.3 (a) | identical | no difference | – |
| 2 | Per-tile `contents` (text + PNG, no role) | as § 1.3 (b) | identical | no difference | – |
| 3 | Cached `GenerateContentConfig` (T, 8192, JSON MIME, `thinking_level`, 4 × safety OFF, `cached_content`; no schema, no tier, no media resolution, no seed) | as § 1.3 (c) | identical. `--service-tier flex` was passed, but the cached call drops it. | no difference | – |
| 4 | Image encoding | raw PNG bytes, `image/png` | identical | no difference | – |
| 5 | Inputs: tiles (487), examples (13), config, instruction | committed versions | unchanged in git between `bb73b52f5` and `b57cf6c22`. Same SHA-256 on both machines today: tiles `bfa455c0580f3f67`, examples `16d1a3344813766e`, config `2fc4700a42a5`, instruction `e169b7237b85`. No nested PNG directories, so `rglob` = `glob`. | no difference | – |
| 6 | Serialised HTTP body (google-genai 1.67.0 vs 1.71.0) | – | byte-identical JSON for the cache create and both generate calls (SHA-256 prefixes `8b2afa63…`, `44cd64e2…`, `62795540…` under both SDKs) | no difference | – |
| 7 | `user-agent` / `x-goog-api-client` headers | `google-genai-sdk/1.67.0 gl-python/3.13.3` | `google-genai-sdk/1.71.0 gl-python/3.13.3` | header only, not model input | Not plausibly, unless the server routes by client version. There is no evidence either way. |
| 8 | Client machine / IP | amd-tower | sapphire | context | Not plausibly. |
| 9 | Quota tier and governor | TPM target 720,000, RPM 1,440 (meta `tpm_governor`) | Tier 3: TPM target 14.4 M, RPM 14,400; pool 250 | context | Possible only if serving is load- or tier-dependent. It cannot be tested from the repository. |
| 10 | Concurrency / wall time per T = 0.3 pass | ~596 s for 487 tiles, median latency 7.2 s | ~40 s for 487 tiles, median latency 14.7 s | context | As row 9. |
| 11 | Server date | 2026-03-27 | 2026-04-16 | serving side | **Yes, the leading explanation.** See § 4. |

Fields the API reports per request also match in both runs: model version, input tokens (15,659), cached tokens (14,549), and the modality breakdown (prompt 427 text + 15,232 image; cache 406 text + 14,143 image). That means the server tokenised the same content at the same media resolution.

## 4. Evidence on serving-side drift, and third executions

**Third execution: none.** I searched every `*.meta.json` under `outputs/`, `results/` and `archive/` (2,064 carry instruction hash `e169b7237b85`). I kept those with model `gemini-3-flash-preview`, library hash `3f7f028c2eb9` and either T = 0.3 minimal or T = 0.0 high. Only two dates appear:

- 2026-03-27: `n1-outstanding-384`, 3 + 3 passes;
- 2026-04-16: `pv-diag-384`, 10 passes at T = 0.3; 2 full passes + 1 33-tile resume at T = 0.0.

All of them carry the explicit-cache signature (14,549 cached tokens on every request). At other settings, each settings group falls on a single date: T = 0.0 minimal and T = 0.7 medium only on 03-27; T = 0.3 high, T = 1.0 high and T = 1.0 minimal only on 04-16. T = 0.7 high was run in `55maps-image-generalisation` on 04-18 and 05-03, but over a different tile set.

**Within-date spread versus between-date shift** (existing data, no new calls):

- **T = 0.3 minimal.** March gave 753, 749 and 747 detections. April gave 795–821 (mean 808.0). The ranges do not overlap.
- **T = 0.0 high, pre-recovery files** (`archive/pre-recovery-2026-07-30/`). March gave 692, 681 and 677; April gave 785 and 785. Per-tile detection counts agree:
  - within March, on 300–301 of 312–313 tiles;
  - within April, on 331 of 333 tiles;
  - between March run 2 and April run 2, on 205 of 363 tiles.
- **MAX_TOKENS failures** at T = 0.0 high: 19, 17 and 15 in March against 34 and 34 in April.
- **Thought tokens** at T = 0.0 high. The median over all 487 requests is 1,322, 1,315 and 1,323 in March and 1,601 and 1,599 in April. Over successful requests only, it is 1,293.5 (March run 2) against 1,453 (April run 2). I could not reproduce the brief's 1,648.

Identical requests, consistent within each date and shifted between dates: that pattern is what a server-side change (model weights, serving stack, or decoding) between 03-27 and 04-16 would produce. The context differences (rows 8–10) cannot be excluded.

**Weaker corroboration from the text track.** The same instruction with no images, 1,502 input tokens and 487 tiles also shifts between 2026-03-27 and 2026-04-17:

- T = 0.3 minimal: March 1,052–1,096 against April 1,007–1,056 (fewer in April);
- T = 0.0 high: March 1,060–1,112 against April 1,120–1,160, with median thought tokens 2,535–2,806 in March against 2,258–2,424 in April.

These are not identical requests. The April text launcher passed `--service-tier flex`, and text cache creation fails, so `serviceTier` reached the request. The March text runs had no tier.

**What would confirm drift:**

1. Re-send one stored request on a third date and compare per-tile outputs at T = 0.0 high. This needs paid calls, falls under D10 (no new runs) and the API gate, and `gemini-3-flash-preview` may no longer be served. Not done.
2. Find other projects or runs that sent byte-identical requests on both sides of the window. None exists in this repository (searched above).
3. Look for a Google model-update notice for `gemini-3-flash-preview` dated between 2026-03-27 and 2026-04-16. I did not search for one (unverified).

## 5. Offline request capture (method)

`capture.py` (in the scratchpad `sdk/` folder) rebuilds the cached-path request exactly as in both code versions:

- the real config, instruction and 13 examples;
- one real tile (`K-35-052-4_32635_x1344_y336.png`);
- a placeholder cache name;
- T = 0.3 minimal and T = 0.0 high.

It patches `google.genai._api_client.BaseApiClient._request` to record the built `HttpRequest` and raise an exception before any transport call. The API key is fake and `HTTP(S)_PROXY` points at a dead port. It ran under each SDK wheel (1.67.0 and 1.71.0, fetched with `pip download --no-deps`). The captured bodies:

- **Cache create:** `POST /v1alpha/cachedContents` with `{model, ttl, displayName, contents:[{parts:[text, (label, inlineData) × 13], role:"user"}], systemInstruction}`.
- **Generate:** `POST /v1alpha/models/gemini-3-flash-preview:generateContent` with `{contents:[{parts:[text, inlineData]}], safetySettings, cachedContent, generationConfig:{temperature, maxOutputTokens, responseMimeType, thinkingConfig:{thinking_level}}}`. The `thinkingConfig` key is `thinking_level` (snake case) under both SDKs.

## 6. Caveat: July 2026 recovery requests are inside the HIGH-group counts

The post-recovery files carry the HIGH-group counts quoted in the brief (~745 against ~890). Both runs were topped up on 2026-07-30 by the E71 recovery rerun (commit `99ae28ec4`, `scripts/lib_batch_api.py::_retry_tile_sync`). That builder makes a different request: one turn, no explicit cache, and a possible `max_output_tokens` override. The metas' `recovery_history` shows:

| Run | Tiles recovered | Detections before → after |
|---|---:|---|
| March run 1 | 14 | 692 → 750 |
| March run 2 | 18 | 681 → 744 |
| March run 3 | 15 | 677 → 741 |
| April run 2 | 30 | 785 → 892 |
| April run 3 | 32 | 785 → 897 |

`per_item_metadata` for those tiles still records the original March or April MAX_TOKENS attempts. The July requests left no usage record, so "every recorded per-request field matches" does not cover those tiles' detections. On the pre-recovery files the HIGH gap is about 683 → 785, not 745 → 894. The T = 0.3 minimal group has no recovery and no MAX_TOKENS failures, so it is a clean comparison.

## 7. Verification log (commands run)

1. `ls ~/cc-archives/` and `ls ~/cc-archives/map-reader-llm/ | grep 2026-03-2[5-8]`, plus the alias listing (no March sessions).
2. `git log bb73b52f5..b57cf6c22 -- scripts/4_detect_mounds_batch.py`, then `git show --stat 76a2cc719` and `git diff bb73b52f5 76a2cc719 -- scripts/4_detect_mounds_batch.py`.
3. Per-session `zcat … | grep -c` for `n1-outstanding` and the cache identifiers (03-24 to 03-28). The 03-26T06-38 session had 94 and 48 hits.
4. Decompressed the March session to the scratchpad. A Python lister (`tools.py`) printed every tool call with JSONL line and timestamp. Another script (`results.py`) printed the inputs and results at lines 1818–1858, 2010, 2015–2032, 2091–2130 and 1650–1656.
5. Replayed the nine edits onto `git show bb73b52f5:…`, then ran `diff` and `sha256sum` against `git show 76a2cc719:…`; the files were identical. Did the same for `run_phase2.py`; also identical.
6. Swept Edit and Write calls to the detect script and `lib_*` across the 03-24 to 03-28 sessions and subagents. Grepped Bash calls for `sed -i`, git checkout/stash/restore, scp and rsync.
7. `git diff 76a2cc719 b57cf6c22 -- scripts/4_detect_mounds_batch.py` (full), with `--stat` for the imports, and `git diff` for `lib_token_bucket.py`.
8. Summarised the metas (`summ.py`) for both cells in both runs: start time, commit, T, thinking level, example order, cached/input tokens, thought medians, finish reasons, detections and recovery history.
9. Read the April session at lines 242–246, 729, 768 and 829 for the launcher and the sapphire pull. Swept the 04-15 and 04-16 sessions and subagents for edits, scp and rsync. Ran `git show --stat 6a7c3ed8c` and `9009a65b5`.
10. Searched the 03-15 to 04-16 archives for SDK version records (`grep -o`). Read lines 847–848 and 1108–1109 (04-14 session) and 699–709 (04-15T07-08 session).
11. Checked `.venv` dist-info (amd-tower: 1.73.1, dated 2026-04-15). Ran a read-only `ssh sapphire` for git HEAD, `git status` on inputs, nested directories, the genai version (1.71.0) and the dist-info timestamp.
12. Ran `git diff --stat bb73b52f5 b57cf6c22` on the examples, tiles, manifest, config and instruction (no output), and `git status --porcelain` on the same paths (clean).
13. Ran `inputhash.py` locally and on sapphire (stdin over ssh); the hashes were identical.
14. Downloaded the SDK wheels (`pip download google-genai==1.67.0|1.71.0 --no-deps`), ran `capture.py` under each and diffed the outputs; only the headers differed.
15. Searched for a third execution: `grep -rl` for the instruction hash (2,064 metas), filtered by library hash and model (391), then `sig.py` and a grouping script by (T, thinking, date).
16. Compared per-tile counts on the `archive/pre-recovery-2026-07-30/` GeoJSONs (`source_tile` property).
17. Swept text-track metas (`detect_brief-text.md`, 680 files) for identical-request pairs on two dates. Read the April text launcher flags (session line 3206).
18. Read `reports/launch-archaeology-2026-10-04.md` (§§ 3, 5, 6) and D34 in `planning/pi-decisions-2026-09-20.md`.

## Changelog

### 2026-10-05 — Original publication (Session 161)

The agent's record, with this header added.
