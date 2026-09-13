# Post-run report — Gemini 3.7 image at 55-map scale, K = 3

> **Last revised**: 2026-09-13 (original publication — the run is **IN FLIGHT**;
> this is a launch-state and handover record, not a completed post-run report).
> See [§ Changelog](#changelog) for revision history.

Card: `planning/gemini37-image-55map-2026-09-13.md`. Deltas and blocker status:
`reports/gemini37-image-55map-deltas-2026-09-13.md`. Pre-launch audit:
`outputs/gemini37-image-55map-2026-09-13/pre_launch_audit.md`.

**Status: pass 1 of 3 in flight.** The Gold Standard (GS) calibration leg is
complete and the carried operating points are fixed in the card § 2. Nothing
downstream of the proposer exists: no 55-map union, no verifier arm, no score,
no permutation test, no P1–P5 verdict, no analysis row. This document records
what ran, what the gates measured, and exactly how to resume.

## 1. What ran

| Stage | State | Audited USD | Note |
|---|---|---:|---|
| B2 verification — GS K = 5 first-N rebuild | **PASS** | 0.00 | reproduces the committed 674 **byte-identically** |
| GS K = 3 first-N union | **built**, 622 candidates | 0.00 | votes {1: 105, 2: 57, 3: 460} |
| GS K = 3 crop extraction | **622/622** from rasters | 0.00 | `crops_k3/`; PNGs untracked per `.gitignore:72` |
| GS calibration, arm 1 | **622/622**, 0 failed | 0.4417 | `gemini-3-flash-preview`, MINIMAL, T = 0.0, 51 s |
| GS calibration, arm 2 | **622/622**, 0 failed | 0.6804 | `gemini-3.7-flash`, low, T = 0.0, 893 s, 824 retries |
| GS sweep, both arms, 20 m | **carried points fixed** | 0.00 | anchor gate 0.89614 vs registered 0.8961 |
| 5-tile mechanism smoke | **PASS** | ≈ 0.025 | payload fingerprint matches the GS run |
| 55-map proposer pass 1 | **IN FLIGHT** | pending | launched 2026-09-13 ≈ 07:28 UTC |
| 55-map proposer passes 2–3 | not started | — | |
| Unions, four verifier arms, scoring, tests | not started | — | |
| **Committed so far** | | **≈ 1.15** | against a ≈ US$261–276 envelope |

Carried operating points, from the GS K = 3 calibration leg swept at the
GS-primary 20 m buffer:

| Arm | Verifier | Carried (prob_t, k) | GS F1@20 | P | R |
|---|---|---|---:|---:|---:|
| arm 1 | `gemini-3-flash-preview`, `verify_adversarial-text`, T = 0.0, MINIMAL | (0.10, k3) | 0.9197 | 0.9032 | 0.9369 |
| arm 2 | `gemini-3.7-flash`, same config, thinking `low` | (0.88, k3) | 0.9245 | 0.9192 | 0.9299 |

## 2. Gates

| Gate | Basis | Reading |
|---|---|---|
| Mechanism (smoke, B4-rescoped) | stamped configuration | **PASS** — `gemini-3.7-flash`, thinking `low`, T = 0.7, tile 384, `include_example_images: true`, `system_instruction_hash` `e169b7237b853eeaad990fc2e54fbd7214afb435d85c8e444a4a784432200e12` (the GS payload fingerprint), thinking 228 tokens/call |
| Pass-1 audited cost ≤ US$110 | `scripts/audit_proposer_cost.py` | **PENDING** — post-pass only (§ 3) |
| Pass-1 cached share ≥ 0.70 | `usage_stats` | **PENDING** — post-pass only (§ 3) |
| Running audited total ≤ US$420 | same | ≈ US$1.15 so far |

`library_hash` differs from the GS run's by design: the basis changed to
`example-bytes+path-label-category/1` on 2026-09-12. Argue identity from
`system_instruction_hash` and the blob comparison, per the audit's provenance
note.

## 3. Why both pass-1 gates are post-pass

`4_detect_mounds_batch.py` writes the detections GeoJSON incrementally after
every tile (`_save_geojson`, called at line 1255) but writes `*.meta.json` —
the only home of `usage_stats`, and therefore of the token counts and
`total_cached_tokens` — once, at the end (line 1355). In flight, only the
completed-tile count is observable. The card's "abort the proposer if pass 1
exceeds US$110" therefore operates as a **go/no-go on passes 2–3**, read the
moment pass 1's meta lands. Exposure left unguarded is bounded: pass 1 costs
US$79 on the audited GS basis, and reaching US$110 would require the per-tile
cost to run 39 % high, which is the same event as the cache share collapsing —
so the two gates fail together and are read together, once.

## 4. How to resume

All commands from the isolated sapphire worktree
`~/worktrees/map-reader-llm/claude-image55` on branch
`gemini37-image-55map-2026-09-13`, with `.venv/bin/python`. Read the gates
before spending anything further.

```bash
# 1. Pass-1 gates, the moment the driver logs "PASS 1 COMPLETE".
.venv/bin/python scripts/audit_proposer_cost.py \
    outputs/gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img
#   -> audited USD must be <= 110, and the per-fragment cache column >= 0.70.
#      STOP and report if either fails.

# 2. Passes 2 and 3, sequentially (the PI's 2026-08-30 rule: never two
#    concurrent Gemini 3.7 runs).
WORKERS=150 nohup bash scripts/gemini37-image-55map-driver.sh 2 3 \
    >> outputs/gemini37-image-55map-2026-09-13/driver.nohup 2>&1 &

# 3. Unions. See the open question in the deltas report § 7 (B2) FIRST:
#    stride55 gives text-arm comparability, merge_passes --sweep gives
#    pass_provenance, and no single builder gives both.
.venv/bin/python scripts/stride55_prepare_and_union.py \
    --root outputs/gemini37-image-55map-2026-09-13 \
    --cell g384_ov192_55map_g37img \
    --manifest inputs/stride-55map-2026-08-25/g384_ov192_55map_manifest.json \
    --k 1 --write
#    ... and again with --k 3.

# 4. Crops, then the four verifier arms (K = 1 and K = 3, each under both
#    arms), on the pattern the GS calibration leg used:
.venv/bin/python scripts/run_pv.py extract \
    --proposer <union>.geojson --output-dir <crops-dir> \
    --tiles-dir inputs/tiles_384_ov192_55maps --padding 75
.venv/bin/python scripts/run_pv.py verify \
    --crops-dir <crops-dir> \
    --verifier-config prompts/configs/verify_adversarial-text.json \
    --output-dir <verify-dir> --mode realtime \
    --model gemini-3-flash-preview --thinking-level minimal \
    --temperature 0.0 --service-tier flex --workers 50
#    arm 2: --model gemini-3.7-flash --thinking-level low
```

Scoring then follows the 55-map board's recipe under
`results/55map-final-board-r2-2026-09-06/` — reference r2 at 50 m with the
corrected-F1 engine and tile-MCC on 8,541 tiles, at the carried points above
and at each rung's oracle — and the paired tile-swap (10,000 draws, seed 42) on
MCC and F1 against `FOURTH-N1-oracle` (MCC 0.7471, F1 0.8352), `ARM2-N3-oracle`
(0.7163 / 0.8848), `ARM2-N5-oracle` (0.7147 / 0.8871) and `IM-k3` (0.7110 /
0.8008), Benjamini–Hochberg within that five-test family.

**Do not** re-tier the 55-map board or the tile-MCC tiering, and touch no
signed row.

## 5. Environment

- Isolated sapphire worktree `~/worktrees/map-reader-llm/claude-image55`;
  sapphire's main checkout was read only, never written, moved or removed.
- `inputs/tiles_384_ov192`, `inputs/tiles_384_ov192_55maps`, `inputs/rasters`,
  `.venv` and `.env` are symlinks into the main checkout; the GS pass
  directories are a 95 MB copy.
- Driver log `outputs/gemini37-image-55map-2026-09-13/driver.log`; residual
  manifests `residual_run_<N>.json`.
- `.pre-merge-backup/` holds the twelve calibration artefacts as first
  generated, before the byte-identical committed versions were checked out over
  them (md5 parity verified both ways). Archived, not deleted.

## Changelog

### 2026-09-13 — Original publication

Written at launch, not at completion, because the campaign spans more wall
clock than one session: the GS calibration leg is complete with the carried
points fixed, the mechanism smoke passed on the GS payload fingerprint, and
pass 1 of the 55-map proposer is in flight from ≈ 07:28 UTC. ≈ US$1.15 audited
committed against a ≈ US$261–276 envelope. Records the two post-pass gates and
their reason (§ 3) and a resume path (§ 4) because the handover owner is still
unnamed — question Q5 of the deltas report.
