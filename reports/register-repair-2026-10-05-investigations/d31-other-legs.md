# Other legs outside the passes register: findings

Read-only investigation, 2026-10-04, branch `register-repair`. Nothing in the
repository was modified.

## 0. Scope, method and caveats

- **Gap set.** `git ls-files '*cost_audit.json'` gives 729 sidecars. Of those
  with `"in_register": false`, removing the excluded groups (`grid-2026-08-18`,
  `verifier-robustness`, `vote3-verify`, `batch-staging`, `tier-cache-probe`,
  any path containing `smoke`, `probe`, `/tests/`, `tier-e` or `fd-storm`)
  leaves **38 metas, US$63.114601**. That is D31's "37 further real legs (about
  US$61.90)" plus "the 3.7 screen's wrong-instrument leg, US$1.21, not yet in
  [the D22 ledger]" (`planning/pi-decisions-2026-09-20.md:35`):
  61.905 + 1.2097 = 63.1146.
- **Duplicate test.** Each meta was checked against every register row in
  `results/passes-manifest.json` on three keys: the
  (`input_billed`, `output`) token pair, the start instant, and the `run_id`
  of every meta any row cites. **No meta matched any row on any key.**
  Same-tile/same-crop legs share input tokens by construction (for example the
  55-map K = 5 replicates: 16,438,016 input tokens, like the originals); those
  were checked by hand and differ in `run_id`, time window and output tokens.
- **Dry-run.** Every proposed entry was passed through
  `generate_post_run_report.extract_passes` in memory with only the new entries
  in the decomposition (scratch scripts `proposed.py` and `dryrun.py` beside
  this file; results in `dryrun-main.json` and `dryrun-alt.json`). **All 34
  reachable entries extract, none clashes with an existing key or `pass_id`,
  and every row's `cost_usd` equals its sidecar's to the cent; 32 of 34 also
  carry the sidecar's `cost_basis`** (the two exceptions are in § 3).
- **Concurrency caveat.** While this ran, another session committed
  `7360ba939` (D32's `repo_path` key; verifier-robustness and vote-3 hints),
  `eb494f500` (grid-2026-08-18 pools), `7277f46b1` and `b715c2813` (D34 cache
  signature). The dry-run was re-run on the clean tree at `b715c2813` with the
  same result: 34 rows, US$61.296184, no key or `pass_id` clash, and the same
  two basis differences.
- **Extractor reach** (current `scripts/generate_post_run_report.py`):
  proposer pools glob `run_*` under the pool directory (line 647) and fold in
  `run_N_recovery*` siblings (line 701); `_meta_files` is non-recursive
  (lines 325-333). Verifier passes resolve `<root>/<path>/run.meta.json` or
  `<root>/<path>.meta.json`, where `<root>` is the run directory or a D32
  `repo_path` (`_verifier_leg_root`, line 556; no `..` allowed). Every
  verifier row is stamped `"status": "ok"` (line 923).

## 1. Totals by verdict

| Verdict | Metas | Sidecar US$ |
|---|---:|---:|
| DUPLICATE | 0 | 0.000000 |
| SUPERSEDED (to `data/pricing/superseded-executions.json`) | 1 | 1.209725 |
| REAL, reachable with a `run-conditions.json` entry | 33 | 61.286768 |
| REAL, NOT reachable by the extractor as it stands | 3 | 0.608692 |
| UNSURE | 1 | 0.009416 |
| **Total** | **38** | **63.114601** |

## 2. Per-meta table

All paths are relative to the repository root; "pass id" is what the dry-run
produced. Sidecar figures are each sidecar's `cost_usd` / `cost_basis`.

| # | Meta | Sidecar US$ (basis) | Verdict | Owning run (registered?) | Proposed entry (key → spec) | Evidence |
|---:|---|---:|---|---|---|---|
| 1 | `outputs/era1-pv-stage-d/256-consensus-text-5of5/pass_1/verified/run.meta.json` | 0.799018 (audited) | REAL | `pv-diag-256` (yes; dir not under it) | `verified-adv-text-consensus-5of5` → `{"modality":"text","repo_path":"outputs/era1-pv-stage-d","path":"256-consensus-text-5of5/pass_1/verified"}` | Condition `verified-adv-text-consensus-5of5`, `source_run` pv-diag-256 (`results/run-conditions.json:12138`); Stage D API commit `0ed0b2b37` ("9 run.meta.json ... ~$5 flex"); `results/era1-pv-stage-d/stage-d-findings.md:16`. Pass id `pv-diag-256::verified-adv-text-consensus-5of5::run1` |
| 2 | `outputs/era1-pv-stage-d/512-consensus-image/pass_1/verified/run.meta.json` | 0.376132 (audited) | REAL | `retest-phase3a` (yes) | `verified-adv-image-t0.7-n30-18of30` → `{"modality":"text","repo_path":"outputs/era1-pv-stage-d","path":"512-consensus-image/pass_1/verified"}` | Condition `verified-adv-image-t0.7-n30-18of30` (`run-conditions.json:10897`); verifier is `verify_adversarial-text`, `example_count` 0 → text (E88 rule) |
| 3 | `outputs/era1-pv-stage-d/512-consensus-text-high/pass_1/verified/run.meta.json` | 0.311520 (audited) | REAL | `retest-phase3a-high` (yes) | `verified-adv-text-high-t1.0-n30-23of30` → `{"modality":"text","repo_path":"outputs/era1-pv-stage-d","path":"512-consensus-text-high/pass_1/verified"}` | Condition `verified-adv-text-high-t1.0-n30-23of30` (`run-conditions.json:11370`) |
| 4 | `outputs/era1-pv-stage-d/512-single-image-t0.0/pass_1/verified/run.meta.json` | 0.546981 (audited) | REAL | `retest-phase2b` (yes) | `verified-adv-image-t0.0-pass1` → `{"modality":"text","repo_path":"outputs/era1-pv-stage-d","path":"512-single-image-t0.0/pass_1/verified"}` | Condition `verified-adv-image-t0.0` reads `accepted_t0.15_passes` over passes 1-3 (`run-conditions.json:10173-10174`) |
| 5 | `…/512-single-image-t0.0/pass_2/verified/run.meta.json` | 0.541063 (audited) | REAL | `retest-phase2b` | `verified-adv-image-t0.0-pass2` → same, `path` `512-single-image-t0.0/pass_2/verified` | as row 4 |
| 6 | `…/512-single-image-t0.0/pass_3/verified/run.meta.json` | 0.539996 (audited) | REAL | `retest-phase2b` | `verified-adv-image-t0.0-pass3` → same, `path` `512-single-image-t0.0/pass_3/verified` | as row 4 |
| 7 | `…/512-single-text-t0.0/pass_1/verified/run.meta.json` | 0.614730 (audited) | REAL | `retest-phase2b` | `verified-adv-text-t0.0-pass1` → `{"modality":"text","repo_path":"outputs/era1-pv-stage-d","path":"512-single-text-t0.0/pass_1/verified"}` | Condition `verified-adv-text-t0.0` reads `accepted_t0.2_passes` (`run-conditions.json:10154-10155`) |
| 8 | `…/512-single-text-t0.0/pass_2/verified/run.meta.json` | 0.613907 (audited) | REAL | `retest-phase2b` | `verified-adv-text-t0.0-pass2` → same, `path` `512-single-text-t0.0/pass_2/verified` | as row 7 |
| 9 | `…/512-single-text-t0.0/pass_3/verified/run.meta.json` | 0.617163 (audited) | REAL | `retest-phase2b` | `verified-adv-text-t0.0-pass3` → same, `path` `512-single-text-t0.0/pass_3/verified` | as row 7 |
| 10 | `outputs/gemini37-image-55map-2026-09-13/verifier/g384_ov192_55map_g37img/verify_k5_arm1_replicate-batch-2026-09-20/run.meta.json` | 6.490936 (audited) | REAL | `gemini37-image-55map-2026-09-13` (yes) | `g384_ov192_55map_g37img-union-k5-verify-arm1-replicate-batch-2026-09-20` → `{"modality":"text","path":"verifier/g384_ov192_55map_g37img/verify_k5_arm1_replicate-batch-2026-09-20"}` | D8 (`planning/pi-decisions-2026-09-20.md:57`, "leg 5778b5569, audited US$6.4909"); `results/gemini37-image-55map-2026-09-13/replicate-k5-arm1-batch-2026-09-20/findings.md:64`. Not a duplicate of the K = 5 arm 1 row: run_id 876d9a9c vs the row's meta, 2026-09-20 05:32 vs 2026-09-17 23:28 UTC, 1,587,621 vs 1,586,724 output tokens |
| 11 | `…/verify_k5_arm2_replicate-batch-2026-09-20/run.meta.json` | 10.203315 (audited) | REAL | `gemini37-image-55map-2026-09-13` | `g384_ov192_55map_g37img-union-k5-verify-arm2-replicate-batch-2026-09-20` → `{"modality":"text","path":"verifier/g384_ov192_55map_g37img/verify_k5_arm2_replicate-batch-2026-09-20"}` | Commit `3f8af3a65` ("audited US$10.2033"); `…/replicate-k5-arm2-batch-2026-09-20/findings.md:45`. Batch, 2026-09-19 23:35 UTC vs the row's flex leg 2026-09-17/18 |
| 12 | `outputs/gemini37-image-gs-2026-09-01/verifier/g384_ov192_g37img/verify_k3_arm1/run.meta.json` | 0.441725 (audited) | REAL | Recommended `gemini37-image-gs-2026-09-01` (yes); alternative `gemini37-image-55map-2026-09-13` | `g384_ov192_g37img-union-k3-verify-arm1` → `{"modality":"text","path":"verifier/g384_ov192_g37img/verify_k3_arm1"}`. Alt: `gs-calibration-g384_ov192_g37img-union-k3-verify-arm1` → `{"modality":"text","repo_path":"outputs/gemini37-image-gs-2026-09-01","path":"verifier/g384_ov192_g37img/verify_k3_arm1"}` (same price) | Commit `30e36bcd1` (GS calibration K = 3, 622 candidates, "US$1.12"); `planning/gemini37-image-55map-2026-09-13.md:123` ("1.1221 (arm 1 0.4417 + arm 2 0.6804)"); booked in row A's campaign total (`results/gemini37-image-55map-2026-09-13/findings.md:201`). 622-candidate K = 3 union, distinct from the registered 674-candidate K = 5 legs |
| 13 | `…/g384_ov192_g37img/verify_k3_arm2/run.meta.json` | 0.680415 (audited) | REAL | as row 12 | `g384_ov192_g37img-union-k3-verify-arm2` → `{"modality":"text","path":"verifier/g384_ov192_g37img/verify_k3_arm2"}` (alt as row 12) | as row 12 |
| 14 | `outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/archive-wrong-instrument-5verifycrops/verify_k10.meta.json` | 1.209725 (audited-upper-bound) | SUPERSEDED | n/a (ledger) | Ledger entry, `superseded_by` `gemini37-screen-2026-08-28::g384_ov192_g37-union-k10-verify::run1` | Meta's `environment.script` is `5_verify_crops.py` v5.3.0 (the wrong instrument); 06:45-06:48 UTC 2026-08-29, immediately before the registered `verify_k10` leg (06:49-06:54, same 913 candidates); `planning/gemini37-screen-2026-08-28.md:102` ("A wrong-instrument stray — `5_verify_crops.py`, ~$0.60 — archived beside the real run"); D31 (`pi-decisions-2026-09-20.md:35`). Tier unresolved: US$0.604862 at flex (matches the card's ~$0.60), US$1.209725 at standard (the sidecar's upper bound) |
| 15 | `…/g384_ov192_g37/verify_k1_recovery-fixed/run.meta.json` | 0.000757 (audited) | REAL | `gemini37-screen-2026-08-28` (yes) | `g384_ov192_g37-union-k1-verify-recovery-fixed` → `{"modality":"text","path":"verifier/g384_ov192_g37/verify_k1_recovery-fixed"}` | Commit `f8e0eb600` ("639 carried + 1 call US$0.000757"; PI-approved under the 2026-09-13 "fix properly" ruling). No condition cites it. Row extracts as `audited-lower-bound`, sidecar says `audited` (§ 3) |
| 16 | `…/g384_ov192_g37/verify_k3_recovery-fixed/run.meta.json` | 0.002026 (audited) | REAL | `gemini37-screen-2026-08-28` | `g384_ov192_g37-union-k3-verify-recovery-fixed` → `{"modality":"text","path":"verifier/g384_ov192_g37/verify_k3_recovery-fixed"}` | Commit `f8e0eb600` ("756 carried + 3 calls US$0.002027"). Same basis note as row 15 |
| 17 | `outputs/h11/consensus-384-UNINTENDED-T1.0/384/run_4/retry/retry_K-35-078-1_Lesovo_x3360_y0.meta.json` | 0.000976 (audited) | REAL, UNREACHABLE | `consensus-384-t1-0` (yes), pass `384::run4` | None possible: the meta is nested in `run_4/retry/`, which neither `_meta_files(run_4)` (non-recursive) nor the `run_4_recovery*` glob reaches. Needs an extractor extension (fold `run_N/retry/*.meta.json` in as recovery fragments) | Own run_id 58e868fd, 2026-03-14 11:14 UTC; one tile; its feature is geometrically identical to run 4's feature for that tile, so it fed run 4. The register row `consensus-384-t1-0::384::run4` is `unrecorded` (its meta records 0 tokens), so this would be its only priced fragment. Records `temperature` 0.7 inside a T = 1.0 pass (unexplained; § 4) |
| 18 | `outputs/h11/e47-propose-brief/text-baseline/detections-propose_brief-text-3-flash-2026-04-08.meta.json` | 0.606548 (audited) | REAL, UNREACHABLE | `e47-propose-brief` (yes) | Intended pool `propose_brief-text-baseline` → `{"modality":"text","path":"text-baseline"}`, but the extractor globs `text-baseline/run_*` and finds nothing (no `run_N/`). Needs an extension for a flat single-pass directory. The verifier sidecar form would reach the file but mint a verifier row (wrong stage) | Registered condition `baseline-single-pass` cites this pass's geojson (`run-conditions.json:166-167`). MINIMAL, T 0.0, 487 tiles, 2026-04-08 06:15 UTC; not a duplicate of pool `propose_brief-text` run 5 (same 744,136 input tokens by construction, but HIGH, T 0.7, 1,444,336 thinking tokens, 2026-04-09). Commit `42f07bc3b` |
| 19 | `outputs/h11/proposer-verifier-384/proposer/detections-detect_brief-text-3-flash-2026-03-15.meta.json` | 0.001168 (audited) | REAL, UNREACHABLE | `proposer-verifier-384` (yes) | Intended pool `detect_brief-text` → `{"modality":"text","path":"proposer"}`; unreachable for the same reason as row 18 | A 2-tile resume round that overwrote the 238-tile main meta (`outputs/h11/proposer-verifier-384/proposer.log:13-28`: "Resuming: 238 tiles already processed ... Tiles processed: 2"). A floor. The decomposition note deliberately left `proposer_pools` empty for this reason (`run-conditions.json:8320`); D31 now asks for every real leg, so the PI should confirm a floor row is wanted |
| 20 | `outputs/h11/proposer-verifier-384/verified-adversarial-image-v2.meta.json` | 2.653615 (audited-upper-bound) | REAL | `proposer-verifier-384` | `verified-adversarial-image-v2` → `"image"` (sidecar form) | Corrected-config re-run: commit `9b023aef8` ("The 384 PV factorial must be re-run"), meta's `git_commit` 9b023aef8, 6 examples vs the registered leg's 9, adds `crop_label`; `docs/notes/working-notes.md:3222` ("re-run with corrected configs (v2)"). 2026-03-14 23:35 UTC vs registered 13:16 |
| 21 | `…/proposer-verifier-384/verified-adversarial-text-v1-prompt/run.meta.json` | 0.000638 (audited-lower-bound) | REAL (floor) | `proposer-verifier-384` | `verified-adversarial-text-v1-prompt` → `"text"` (dir form) | The live meta is a 1-call cleanup (2026-05-06, commit `6683952ac`) that overwrote the 571/572-candidate leg of 2026-04-10 (commit `f33058f01`, "single-pass v1 verifier (571/572) for v1-vs-v2 comparison"). That original meta is recoverable from git: run_id 0e695515, 623 requests, 1,023,232 in / 93,604 out, US$0.396214 flex / US$0.792428 standard (priced here with `lib_cost.price_usage`). Restoring it beside the live meta as `run.meta.main-2026-04-10.json` would let `_preserved_main_legs` (line 442) price both; that is a write needing PI sign-off (D20 precedent) |
| 22 | `…/proposer-verifier-384/verified-adversarial-text-v2.meta.json` | 0.798139 (audited-upper-bound) | REAL | `proposer-verifier-384` | `verified-adversarial-text-v2` → `"text"` | As row 20 (adds `text_only_labels` and `crop_label`) |
| 23 | `…/proposer-verifier-384/verified-brief-image-v2.meta.json` | 2.434360 (audited-upper-bound) | REAL | `proposer-verifier-384` | `verified-brief-image-v2` → `"image"` | As row 20 |
| 24 | `…/proposer-verifier-384/verified-brief-text-v2.meta.json` | 0.572977 (audited-upper-bound) | REAL | `proposer-verifier-384` | `verified-brief-text-v2` → `"text"` | As row 22 |
| 25 | `…/proposer-verifier-384/verified-checklist-image-v2.meta.json` | 0.009416 (audited) | UNSURE | `proposer-verifier-384` if kept | `verified-checklist-image-v2` → `"image"` | Failed leg: 2 of 572 succeeded, 570 empty responses / parse failures in 75 s (meta `execution_stats`); `working-notes.md:17002` ("2 features ... F1=0 ... likely a pipeline error"). No re-run found. The extractor would stamp it `ok` with 2 candidates |
| 26 | `…/proposer-verifier-384/verified-checklist-text-v2.meta.json` | 0.666129 (audited-upper-bound) | REAL | `proposer-verifier-384` | `verified-checklist-text-v2` → `"text"` | As row 22; 462 of 572 succeeded, 110 failed (scored, `working-notes.md:17002`); the row would read `ok` |
| 27 | `outputs/h11/proposer-verifier-512/verified-adversarial-text-v2.meta.json` | 0.196954 (audited-upper-bound) | REAL | `proposer-verifier-512` (yes) | `verified-adversarial-text-v2` → `"text"` | Commit `cad5d3365` ("the 512 PV re-run silently changed non-target parameters"); meta's `git_commit` cad5d3365; 2026-03-14 23:10 vs registered 22:12 UTC; `working-notes.md:3273` (Obs 165) |
| 28 | `outputs/h11/pv-diag-384/verified/flash-high-text-t03-1of5/run.meta.json` | 2.008812 (audited) | REAL | `pv-diag-384` (yes) | `verified-flash-high-text-t03-1of5` → `{"modality":"text","path":"verified/flash-high-text-t03-1of5"}` | Commit `c59292360` ("T0.3 GS verifier run ... ~$2.06, 0 failures", 2,954 crops); conditions at `run-conditions.json:3044`, `:3924` |
| 29 | `outputs/h11/pv-diag-384/verified/text-min-t07-true-1of5/run.meta.json` | 1.086094 (audited) | REAL | `pv-diag-384` | `verified-text-min-t07-true-1of5` → `{"modality":"text","path":"verified/text-min-t07-true-1of5"}` | Commit `8913cab2c` ("Make-up B (approved ~$1.15, actual 1,586 calls, 0 failures)"); conditions at `run-conditions.json:2978`, `:3866` |
| 30 | `outputs/image-b-gs-2026-08-28/verifier/g384_ov192_image/verify_k3_arm1/run.meta.json` | 1.538320 (audited) | REAL | Recommended `image-b-gs-2026-08-28` (yes); alternative `gemini3-image-55map-2026-09-16` | `g384_ov192_image-union-k3-verify-arm1` → `{"modality":"text","path":"verifier/g384_ov192_image/verify_k3_arm1"}`. Alt: `gs-calibration-g384_ov192_image-union-k3-verify-arm1` → `{"modality":"text","repo_path":"outputs/image-b-gs-2026-08-28","path":"verifier/g384_ov192_image/verify_k3_arm1"}` (same price) | Gemini 3 row's GS calibration legs: commit `276e25dcb`; `results/gemini3-image-55map-2026-09-16/findings.md:274` (1.5383); conditions say "FIXED on the Gold Standard K = 3 calibration leg of image-b-gs-2026-08-28" (`run-conditions.json:16732`) |
| 31 | `…/g384_ov192_image/verify_k3_arm2/run.meta.json` | 2.462861 (audited) | REAL | as row 30 | `g384_ov192_image-union-k3-verify-arm2` → as row 30 with `verify_k3_arm2` | Commit `99afa6a4d` (Batch API); `findings.md:275` (2.4629) |
| 32 | `…/g384_ov192_image/verify_k5_arm1/run.meta.json` | 1.921866 (audited) | REAL | as row 30 | `g384_ov192_image-union-k5-verify-arm1` → as row 30 with `verify_k5_arm1` | Commit `276e25dcb`; `findings.md:276` (1.9219); condition note `run-conditions.json:16820` |
| 33 | `…/g384_ov192_image/verify_k5_arm2/run.meta.json` | 3.087765 (audited) | REAL | as row 30 | `g384_ov192_image-union-k5-verify-arm2` → as row 30 with `verify_k5_arm2` | Commit `99afa6a4d`; `findings.md:277` (3.0878); four legs total US$9.0109 (`findings.md:283`) |
| 34 | `outputs/wbf/e47-propose-brief-n5/verified-v1/run.meta.json` | 0.001367 (audited-lower-bound) | REAL (floor) | `e47-propose-brief` (yes); `outputs/wbf` is not a run | `wbf-n5-verified-v1` → `{"modality":"text","repo_path":"outputs/wbf","path":"e47-propose-brief-n5/verified-v1"}` | `wbf` ruled "OMIT as a run ... `aggregation=wbf` conditions of their source runs" (`planning/run-registry-draft-review.md:80-87`); source pool in `scripts/fuse_detections_wbf.py:61-69`. The live meta is the 1-request cleanup ("1 cleanup retry on v1", `working-notes.md:8208`); probabilities hold 3,890 results. The main leg's meta was overwritten before its first commit (`1e6f2e9ce`), so it is not recoverable; the only figure is the estimate "v1 verifier ... ~$8" (`working-notes.md:8519`) |
| 35 | `outputs/wbf/e47-propose-brief-n5/verified-v2/run.meta.json` | 5.518004 (audited-upper-bound) | REAL | `e47-propose-brief` | `wbf-n5-verified-v2` → `{"modality":"text","repo_path":"outputs/wbf","path":"e47-propose-brief-n5/verified-v2"}` | `verify_adversarial-text_v2`, 3,953 requests; estimate "~$8" (`working-notes.md:8520`) |
| 36 | `outputs/wbf/fh-text-n30/verified/run.meta.json` | 8.002287 (audited) | REAL | `pv-diag-384` (yes) | `wbf-fh-text-n30-verified` → `{"modality":"text","repo_path":"outputs/wbf","path":"fh-text-n30/verified"}` | Source `pv-diag-384/flash-high-text-n5/text-t0.7/run_1-30` (`fuse_detections_wbf.py:82-88`); 5,862 candidates; commit `973005816` |
| 37 | `outputs/wbf/fh-text-n5/verified/run.meta.json` | 3.734028 (audited) | REAL | `pv-diag-384` | `wbf-fh-text-n5-verified` → `{"modality":"text","repo_path":"outputs/wbf","path":"fh-text-n5/verified"}` | Source `run_1-5` of the same pool (`fuse_detections_wbf.py:73-78`); 2,724 candidates |
| 38 | `outputs/wbf/gold-standard-v2-detect/verified-v1/run.meta.json` | 1.822868 (audited-upper-bound) | REAL | `gold-standard-v2` (yes) | `wbf-verified-v1` → `{"modality":"text","repo_path":"outputs/wbf","path":"gold-standard-v2-detect/verified-v1"}` | Commit `0dede119f`; source `outputs/gs/gold-standard-v2/proposer/detect_brief-text/run_1-5` (`fuse_detections_wbf.py:92-100`); Obs 233 "Total cost ~$5–6 Flex" for v1 + v2 (`working-notes.md:8846`) |

## 3. Proposed `run-conditions.json` additions, grouped by run

All under `decomposition[<run>].verifier_passes`. None of the four Stage D
owners has any `verifier_passes` today. No run needs registering:
`outputs/era1-pv-stage-d` and `outputs/wbf` are not runs, and their legs go to
registered source runs through D32's `repo_path` (as `7360ba939` does for the
vote-3 increments).

- **`pv-diag-256`** (+1): row 1.
- **`retest-phase3a`** (+1): row 2.
- **`retest-phase3a-high`** (+1): row 3.
- **`retest-phase2b`** (+6): rows 4-9.
- **`gemini37-image-55map-2026-09-13`** (+2): rows 10-11 (+2 more under the
  alternative owner for rows 12-13).
- **`gemini37-image-gs-2026-09-01`** (+2): rows 12-13 (recommended owner).
- **`gemini37-screen-2026-08-28`** (+2): rows 15-16.
- **`proposer-verifier-384`** (+6, or +7 if row 25 is kept): rows 20-26.
- **`proposer-verifier-512`** (+1): row 27.
- **`pv-diag-384`** (+4): rows 28-29, 36-37.
- **`image-b-gs-2026-08-28`** (+4): rows 30-33 (recommended owner; the
  alternative is `gemini3-image-55map-2026-09-16`).
- **`e47-propose-brief`** (+2): rows 34-35.
- **`gold-standard-v2`** (+1): row 38.

**Stage D `repo_path` must be the campaign root `outputs/era1-pv-stage-d`**,
not the pass directory. Both give US$0.799018 on row 1, but only the campaign
root lets the coster's upward walk reach `full-run.log` and reproduce the
sidecar's `run-log-inherited` tier evidence (the pass-directory root resolves
by `billing-day+verifier-mode` instead). `data/pricing/run-log-tiers.json` is
the only pricing file that names this directory.

**Basis mismatch on rows 15-16.** The register row extracts as
`audited-lower-bound` (1 and 3 candidates completed out of a 640/757-candidate
stage), while the sidecar says `audited` under D28's carry-forward rule ("a
carry-forward stage whose meta covers the carry file's uncovered count is its
whole spend", `pi-decisions-2026-09-20.md:29`). Same dollars; the extractor
does not read `carry_provenance.json`.

**Ledger entry for row 14** (`data/pricing/superseded-executions.json`, schema
`superseded-executions/1`): `meta` as row 14; `superseded_by`
`gemini37-screen-2026-08-28::g384_ov192_g37-union-k10-verify::run1`; `kind`
"wrong instrument (`5_verify_crops.py`); the full K = 10 union was re-verified
with `run_pv.py` minutes later"; `model` `gemini-3-flash-preview`; `tier`
unresolved (flex US$0.604862, standard US$1.209725; the card's "~$0.60" points
to flex, the billing-day evidence allows either).

## 4. Unreachable cases, UNSURE, and other flags

**Extractor cannot reach** (no decomposition entry works):

- Rows 18-19 are flat single-pass proposer directories with no `run_N/`. These
  are the only two such proposer metas found; `proposer-verifier-512/proposer/`
  holds only a geojson and `pv-diag-256` has no proposer meta. Fix: a pool spec
  that names a flat directory as pass 1.
- Row 17 is nested in `run_4/retry/`. Fix: fold `run_N/retry/*.meta.json` in
  with the `run_N_recovery*` fragments.

**UNSURE, row 25** (`verified-checklist-image-v2`, US$0.009416): the leg ran
but 570 of 572 calls failed and it was never re-run. A row would read `ok` with
2 candidates. The PI needs to rule whether a failed, never-repeated leg
belongs in the register (preferably with a status or caveat the schema can
carry) or goes to the D22 ledger as an aborted execution.

**Owner choice for the PI, rows 12-13 and 30-33.** These are Gold Standard
calibration legs run for the two 55-map campaigns. The recommendation is the
run whose pool they verify (`gemini37-image-gs-2026-09-01`,
`image-b-gs-2026-08-28`). That follows the `wbf` precedent
(`run-registry-draft-review.md:80-87`) and D32's parent-run logic, and needs no
`repo_path`. The campaigns' own totals do include them, though: row A's
US$415.3174 (`findings.md:201`, `:221`) and the Gemini 3 row's US$432.1121
(`findings.md:283`). Under the recommended owner, those campaigns' register
run totals will not reproduce the findings' totals. Both options price
identically (dry-run).

**Findings worth flagging (the project's research-calibration rule):**

1. **The pv-384 and pv-512 register rows and all 16 + 1 conditions are on the
   pre-fix, drifted verifier configs.** The `-v2` legs are the corrected
   re-runs (`9b023aef8`, `cad5d3365`, `working-notes.md:3222`). The
   decomposition note calls them "identical T=0.0 config re-runs"
   (`run-conditions.json:8320`), which the metas contradict: the text configs
   add `text_only_labels` and `crop_label`, and the image configs drop 9
   examples to 6. Extraction is unaffected, but which set is canonical is a
   question for the PI.
2. Condition `baseline-single-pass` (`run-conditions.json:158-167`) names
   `proposer_pool` `propose_brief-text` (HIGH, T 0.7) for a MINIMAL, T 0.0
   pass.
3. Row 17 records T 0.7 inside the T = 1.0 run (unverified whether that tile
   really ran at 0.7).
4. Spend with no committed meta (not in this gap): the 238-tile main round of
   pv-384's proposer; the WBF e47 v1 main leg (~$8 estimate); the gs-v2 WBF
   **v2** verifier leg ("both ... v1 and v2", `working-notes.md:8843-8846`;
   only `verified-v1/` exists). The v1-prompt original is recoverable from git
   (row 21).
5. **Out of scope but material to D31/D22's project total:** 734 git-tracked
   metas under `archive/` record usage (about 563 M input tokens), and the WP4
   sidecars never scanned them (D28 covered `outputs/` and `results/`). Their
   real/superseded status was not checked.
6. Adding rows 10-11 raises `gemini37-image-55map-2026-09-13`'s register run
   total by US$16.69 (replicates are excluded from its findings total);
   `lib_frontier_cost` selects legs by `pass_id` (lines 168-207), so
   configuration costs are unaffected there. Other consumers were not checked.
