# Run B (modality bridging pair): configuration, Stage 1 gate and audit — agent report

Date: 2026-10-07. Branch: `modality-bridge-2026-10-07` (pushed, not merged,
no PR), rebased onto `origin/main` `930456695`. Commits:

- `144f20188` feat(scripts): add API-free proposer rehearsal
  (`scripts/bridge_dryrun_harness.py`, `tests/test_bridge_dryrun_harness.py`)
- `33a66d6ae` feat(scripts): add Run B Stage 1 batch launcher
  (`scripts/modality-bridge-2026-10-07-stage1.sh`)
- `a5e6e14c7` docs(planning): Run B card, rehearsal and audit
  (`planning/modality-bridge-2026-10-07.md`,
  `planning/modality-bridge-2026-10-07-rehearsal.json`)
- `9a27eb13a` docs(planning): Run B preconditions after Stage 0

No API call was made. Every rehearsal ran on sapphire in a disposable worktree
(`~/worktrees/map-reader-llm/claude-bridge-dryrun`, now removed with its
scratch; the tile tree it linked to is intact, 1,760 PNGs) under a stub client
with sockets blocked: 0 breaches. Tier-1 suite on sapphire with the new files:
3,890 passed, 5 skipped, 3 xfailed. `ruff` and `markdownlint-cli2` clean.

## 1. Reconstruction per arm (sources)

Sources: pass metas `configuration`/`environment` (sapphire, read 2026-10-07);
drivers `scripts/image-b-gs-overnight.sh`, `scripts/gemini37-overnight.sh`,
`scripts/gemini37-image-gs-driver.sh`,
`outputs/gemini37-image-gs-2026-09-01/image-gs-recovery-driver.sh`; the grid's
launch from the session archive
`~/cc-archives/vlm-burial-mound-detection/2026-08-18T00-27_complete-h13-overlap-scoring-and-analyze/`;
launch attestations A61/A63/A65
(`reports/launch-archaeology-2026-10-04-proposed-attestations.json`);
`results/passes-manifest.json`; `results/run-conditions.json`; run cards.

| Field | G3 text | G3 image | 3.7 text | 3.7 image |
|---|---|---|---|---|
| Run / pool | grid-2026-08-18 / g384_ov192 | image-b-gs-2026-08-28 / g384_ov192_image | gemini37-screen-2026-08-28 / g384_ov192_g37 | gemini37-image-gs-2026-09-01 / g384_ov192_g37img |
| Passes used | 1–10 | 1–10 | 1–5 | 1–5 |
| Detector commit(s) | 8e59c9555 | c9f178bf7 (1–3), 221031f95 (4–10) | 4cc079f95 (1–4), 8802a9c01 (5, recoveries) | 7187e8135 (1), 1c46243d2 (2–5, recoveries) |
| Config | detect_brief-text.json (a389b24e…) | detect_brief-text-image.json (3cd75a01…; md5 9ff5e64d…) | detect_brief-text.json | detect_brief-text-image.json |
| Model | gemini-3-flash-preview (CLI) | config gemini-3-flash → resolved -preview | gemini-3.7-flash (CLI) | gemini-3.7-flash (CLI) |
| Thinking / T | minimal / 0.7 (CLI; config 1.0) | minimal / 0.7 | low / 0.7 | low / 0.7 |
| Instruction | detect_brief-text.md e169b723… | detect_brief-text-image.md e169b723… (byte-identical file) | e169b723… | e169b723… |
| Examples sent | none (include_example_images false; E90) | 17 labelled images | none | 17 labelled images |
| library_hash (filename basis) | 8580ecb2… | 8580ecb2… | 8580ecb2… | 8580ecb2… |
| Output budget | 8,192, application/json | same | same | same |
| Tiles | grid_384_ov192_manifest.json (484e00cb…, 1,398), inputs/tiles_384_ov192, 384 px | same | same | same |
| Caching | none | explicit cache (instruction + preamble + 17 examples, 18,909 tokens every call, 1 h TTL): two user turns | none | implicit only (79.5 %): one inline user turn |
| Mode / tier | real-time flex | real-time, served **standard** (cached path dropped service_tier, A61) | real-time flex | real-time flex |
| Recoveries | 3 × 1 tile | 6 tiles (inline, no cache, A63) | 24 tiles | large (fd/SSL and flex storms) |
| Union | materialise_grid_unions.py, K10, 3,319 | image_b_prepare_and_union.py, K10, 4,065 | same chain, K5, 791 | same chain, K5, 674 |
| Union params | E80 20 m dedup, E72 exact coverage + additive recovery merge, carrier clip to grid_common_bounds (487 tiles), c = 1 with vote_count | same | same | same |
| Crops | run_pv.py extract (v2.0, 150 px, padding 75, inputs/rasters, inputs/tiles_384_ov192) | same | same | same |
| Verifier | verify_adversarial-text.json (357d8a87…), verify_adversarial.md (2518d529…), T 0, n 1; G3 at 7f13952ac, 2026-08-24, real-time flex, 3,319, US$2.27 | G3 at 2ccf1b334, 2026-08-28, real-time flex --no-strict (A65), 4,065, US$2.80 | G3 verify (b8e130fd3, 791, US$0.56); 3.7 swap37 (5bd514542, 789 + 2 cleanup; meta overwritten; ≈ US$0.87) | arm1 G3 and arm2 3.7, 1c46243d2, 674 each, US$0.48 / US$0.74 |
| Cell (own sweep best, 20 m) | (0.15, k10) 0.8961 | (0.15, k9) 0.8412 | (0.10, k5) 0.9139; swap37 (0.80, k5) 0.9265 | arm1 (0.10, k5) 0.9254; arm2 (0.90, k5) 0.9308 |

## 2. Code equivalence

- Configs, both instruction files, the manifest and the 17 example images
  (symlink targets) have identical blob hashes at every original commit and
  HEAD. Tile tree: untracked, restored from `stash@{0}^3` on 2026-08-19 00:18
  UTC after the grid run (defect register N1); all PNGs still carry that
  mtime; the 1,398 manifest tiles digest to `ecc20ef388c010bb…`.
- Real-time request code, original commits against HEAD: content assembly in
  `process_single_tile` unchanged; the cached call now copies the full config
  (`2df65047e`, carries service_tier); TTL 1 h → 24 h; inert-field guard;
  tile-size inference; cost/logging. Nothing reaches request content.
- Executed comparison (harness captured the originals' real-time requests and
  the bridge's batch requests for the same tiles): parts (texts, all example
  images by sha256 in config order, tile bytes), system instruction,
  temperature, thinking level, max tokens, mime type and the G3 image cache
  contents are SAME. DIFF: safety settings (real-time sends four categories
  OFF; the batch builder sends none — the Batch API rejects them); serving
  tier; role field and cache name are representation only.
- Hashes against original metas: instruction e169b723… matches; old-basis
  library hash recomputed = 8580ecb2…; bridge metas will record the content
  basis 7c9bbcec… (not comparable by design); tile set 1,398 = originals'.
- Not verifiable offline: model snapshot behind the aliases (metas record only
  the name); batch safety defaults; SDK version at the original runs (lock
  1.71.0 unchanged since 2026-04-09; installed 1.71.0).

## 3. Stage 1 gate

All 30 passes on the **Batch API**, lodged one at a time by
`scripts/modality-bridge-2026-10-07-stage1.sh lodge all` (exact commands:
`… plan`; card § 4.2). Models pinned: `gemini-3-flash-preview` (both G3 arms),
`gemini-3.7-flash` (both 3.7 arms). Stage 0 (both served) and Run A (uploads
deleted) are recorded on main (`b56300cdc`).

| Arm | Calls | Estimated cost (batch rates, original token profiles) |
|---|---:|---:|
| G3 text, K10 | 13,980 | US$8.38 |
| G3 image, K10 (explicit cache) | 13,980 | US$19.60 + US$4.54 cache storage (ten 24 h caches) |
| 3.7 text, K5 | 6,990 | US$8.60 |
| 3.7 image, K5 (inline) | 6,990 | US$22.50 likely (79.5 % implicit hits at the US$0.075 cache rate the September batch invoices show); US$18.33 at the card's rate; **US$55.86 if batch gives no implicit hits** |
| **Stage 1** | **41,940** | **likely US$63.6; range US$59.5–97.0** |

Stage 2 (own gate): six verifier legs ≈ 10,314 calls, US$7.72; optional G3 K5
legs US$3.93 dedicated (the gate's ~US$1.50 understates the register's own K5
legs) or US$0 inherited. Run B likely ≈ US$71–75; ceiling ≈ US$109 (D49
approved ~US$69–71).

File API: 30.4 GB of requests (3.7 image alone 18.85 GB) against a 19.47 GB
budget — not all storable at once; lodging order gives a 17.86 GB peak and the
3.7 image chunks 2–3 lodge as earlier jobs finish.

## 4. Dry runs (no API)

| Arm | Passes | Requests/pass (jobs) | Dispatched tiles bridge / original | Exit; breaches |
|---|---:|---|---|---|
| g3-text | 10 | 1,398 (1) | 1,398 / 1,398 | 0; 0 |
| g3-image | 10 | 1,398 (1) | 1,398 / 1,398 | 0; 0 |
| g37-text | 5 | 1,398 (1) | 1,398 / 1,398 | 0; 0 |
| g37-image | 5 | 1,398 (3 × 466) | 1,398 / 1,398 | 0; 0 |

Full builds: keys match the manifest in order; one request signature per arm;
tile digest ecc20ef3…; files 464.0 / 461.6 / 464.0 / 3,770.3 MB per pass.
Negative control: a text arm without `--allow-inert-fields` is refused before
any client exists.

## 5. Audit (adapted /audit-config) — summary

16 requirements from the original legs. Config diff: 9 controlled fields
identical; differing fields are the modality bundle, the family (model and
thinking), `--use-cache` on G3 image (as originally run), and launch-only flags.
Transmission matrix: all PASS. Alignment: 13 matches now (R14 coverage checked
post-run); 2 deliberate deviations (serving mode and the absent safety
settings, both from D49's Batch API; the safety item is not named in the gate
and needs the PI's explicit acknowledgement); 0 undocumented. Dry run PASS.
Scope PASS. Blockers: none outstanding — one found and fixed (the 3.7 image
pass would have built a 3.77 GB request file, over the 2 GB per-file limit;
`--max-batch-tiles 466` gives three 1.26 GB files). **OVERALL: READY TO
LAUNCH**, once the PI approves the card and the branch is merged on sapphire.
Full block: card § 7.

## 6. What blocks or differs from the original

1. Serving mode: batch, not real-time flex/standard (D49); batch sends no
   safety settings (originals: four categories OFF; 0 safety blocks recorded).
2. **Finding about the original claim:** the G3 image arm used an explicit
   cache (two user turns, served standard) while the 3.7 image arm sent
   everything inline (one turn, flex). The original gap change carries this
   structure-and-tier asymmetry; Run B replicates it as run. Optional fifth
   leg to isolate it: 3.7 image K5 with `--use-cache` (~US$16 + storage).
3. Cost uncertainty on the 3.7 image arm (US$18–56); recommended gate: lodge
   `g37-image:1` first, continue only if its first chunk's cached share ≥ 0.5.
4. Launch flags beyond the originals: `--allow-inert-fields` (text arms; the
   guard post-dates them), `--model gemini-3-flash-preview` on G3 image (pins
   the alias the original resolved), `--max-batch-tiles 466` (3.7 image),
   `--skip-intent-check`. None changes a request.
5. Parse-failure retries in batch are synchronous inline calls (bypass the
   cache for the few retried G3 image tiles).
6. Stage 2 needs: a tested layout adapter (batch writes
   `detections_<version>_runNN.geojson` under `<arm>/<version>/run_N/`; the
   union chain globs `detections-*.geojson`), unions with pass order pinned,
   `run_pv.py extract`, the union-provenance guard, batch verifier legs
   rehearsed against the original real-time verifier requests, and
   parameterised analysis scripts with an anchor gate reproducing the six
   original cells to 1e-3.
7. Hazards found, not fixed: the detector's `--dry-run` is not API-free
   (batch: client + model listing; real-time with `--use-cache`: creates a
   billable cache it never deletes); `run_batch_unit` reads
   `include_example_images` from the study config, so a text config with
   `--use-cache` in batch would cache the example images (latent; not
   triggered); the batch path never deletes its caches; a dead polling
   process orphans its job (name only in the log).
