# Post-run report — Gemini 3.7 image at 55-map scale, K = 3

> **Last revised**: 2026-09-13 (steward hand-over — the resume path in § 4 now
> names the two drivers that replace its ad-hoc commands, records the corrected
> scoring instrument, and § 6 lists what is built and gated ahead of the data;
> the run is still **IN FLIGHT** at pass 1 of 3, so this remains a launch-state
> and handover record, not a completed post-run report). See
> [§ Changelog](#changelog) for revision history.

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

# 3. Coverage gate, both unions, both provenance sidecars, crops, and the
#    four verifier arms — one idempotent driver. Question Q7 is SETTLED
#    (deltas § 10.2): the stride builder, for text-arm comparability, with
#    the pass_provenance block emitted as a sidecar over the same resolved
#    fragment set. A finished arm is skipped on a resumed run, so this never
#    re-spends.
WORKERS=50 nohup bash scripts/gemini37-image-55map-unions-and-arms.sh \
    >> outputs/gemini37-image-55map-2026-09-13/arms.nohup 2>&1 &

# 4. Sweeps, materialisation, scoring, and the five-test family. Run the
#    gates FIRST — they reproduce all four comparators' committed F1 and tile
#    confusion through this campaign's own code path, and passed on
#    2026-09-13 before any 55-map data existed.
.venv/bin/python scripts/gemini37_image_55map_r2.py --stage selftest
.venv/bin/python scripts/gemini37_image_55map_r2.py --stage sweep --workers 12
.venv/bin/python scripts/gemini37_image_55map_r2.py --stage materialise
#    COMMIT the materialised detections here: the engine's
#    --require-clean-inputs exits 4 on an untracked input.
.venv/bin/python scripts/gemini37_image_55map_r2.py --stage score \
    --workers 5 --jobs 4
.venv/bin/python scripts/gemini37_image_55map_r2.py --stage tests
```

**The scoring instrument, corrected.** Scoring is
`scripts/evaluate_detections.py` against
`inputs/vectors/references/best-available-gt-55maps-r2.geojson` over
`inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` — 14 buffers,
bootstrap 10,000, seed 42, `--mcc`, `--require-clean-inputs` — which is the r2
board's own stage-2 recipe, NOT the canonical Track-2 corrected-F1 engine. The
two are different references and different matching chains, and every
prediction P1–P5 is a difference against a cell on the r2 board, so the
Track-2 engine would have made each one a cross-instrument comparison and the
paired tile-swap incoherent. Reasoning and anchors:
`reports/gemini37-image-55map-deltas-2026-09-13.md` § 10.3. The recipe is
pinned by a tier-1 test against a committed board cell's own `cli_args`.

Cells are scored at the carried points above **and** at each rung's oracle,
where the sweep records both an F1 oracle (the board's convention) and an MCC
oracle (this campaign's primary metric). The paired tile-swap runs at 10,000
draws, seed 42, on tile-MCC and on micro-F1 @ 50 m, against `FOURTH-N1-oracle`
(MCC 0.7471, F1 0.8352), `ARM2-N3-oracle` (0.7163 / 0.8848), `ARM2-N5-oracle`
(0.7147 / 0.8871) and `IM-k3` (0.7110 / 0.8008), plus the within-campaign
K = 1 versus K = 3 contrast that P2 requires — the five-test family declared in
the deltas report § 10.4 before any score existed. Benjamini–Hochberg at
q = 0.05 runs across those five, separately per metric.

`IM-k3`'s detection set is **not** under its evaluation directory: the MCC
tiering scored `outputs/55maps-image-generalisation/verified/verified_detections.geojson`
in place, and that file — not the board's re-serialised `IM-oracle` copy, which
has the same 4,680 features but a different CRS and property names — is the one
its committed confusion matrix belongs to.

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
- Second sapphire worktree `~/worktrees/map-reader-llm/claude-steward`, added
  2026-09-13 (detached, `.venv` and `.env` symlinked): everything that is not
  the campaign's own state runs there, so the campaign worktree is never
  fast-forwarded or otherwise disturbed while a pass is writing. The mechanism
  gates and the tier-1 suite ran there.

## 6. What is built and gated, ahead of the data

Recorded because the campaign outlasts a session and the expensive failure mode
is discovering a broken instrument after the API spend, not before.

| Piece | State | Evidence |
|---|---|---|
| Union builder ruling (Q7) | settled | deltas § 10.2 |
| `scripts/emit_union_pass_provenance.py` | landed, 7 tier-1 tests | schema `consensus-pass-provenance/1` |
| `scripts/gemini37-image-55map-unions-and-arms.sh` | landed | coverage gate, idempotent arms |
| `scripts/gemini37_image_55map_r2.py` | landed, 13 tier-1 tests | four stages |
| Materialiser identity gate | **PASS** | reproduces the calibration leg's 444 and 433 |
| F1 mechanism gate | **PASS** | all four comparators' committed F1 @ 50 m to 1e-4 |
| MCC mechanism gate | **PASS** | all four comparators' committed tile confusion, exactly |
| Cost auditor, in this session's hands | **validated** | reproduces the GS leg's US$22.5004 / 0.00322 / 0.7948 |
| Tier-1 suite on sapphire | **2,516 passed**, 4 skipped, 27 deselected, 3 xfailed | `claude-steward`, 193 s |

## Changelog

### 2026-09-13 (steward hand-over) — resume path rebuilt, instrument corrected

**Trigger**: the campaign acquired a named owner for passes 2–3 onward
(question Q5 of the deltas report), and the resume path as published named
ad-hoc commands plus an unresolved open question where it now needs two
reviewed drivers and a settled ruling.

| Claim | Before | After |
|---|---|---|
| Union builder | "open question … no single builder gives both" | **settled** — stride builder + provenance sidecar (deltas § 10.2) |
| Resume steps 3–4 | ad-hoc command fragments | two drivers, both idempotent |
| Scoring engine | "the corrected-F1 engine" | **`evaluate_detections.py`** on the r2 board's recipe (deltas § 10.3) |
| Test family | four comparators | **five**, the fifth declared (deltas § 10.4) |
| `IM-k3` detection set | unstated | named, with the `IM-oracle` near-miss recorded |
| Gates ahead of the data | none run | **three PASS** + cost auditor validated (§ 6) |
| Tier-1 on sapphire | 2,496 passed | **2,516 passed** (20 new tests) |

**Numerical claims that moved**: none of the campaign's own. The carried
operating points, the calibration leg's US$1.1221, the 622-candidate GS union
and the ≈ US$1.15 committed total are unchanged; no 55-map number exists yet.

**What did NOT change**: pass 1 is still in flight and passes 2–3 unlaunched,
so both pass-1 gates remain PENDING, both unions and all four verifier arms
remain unbuilt, and P1–P5 remain UNTESTED. No board, no tiering, no signed row,
no configuration and no committed union was touched. Nothing on sapphire's main
checkout was written.

### 2026-09-13 — Original publication

Written at launch, not at completion, because the campaign spans more wall
clock than one session: the GS calibration leg is complete with the carried
points fixed, the mechanism smoke passed on the GS payload fingerprint, and
pass 1 of the 55-map proposer is in flight from ≈ 07:28 UTC. ≈ US$1.15 audited
committed against a ≈ US$261–276 envelope. Records the two post-pass gates and
their reason (§ 3) and a resume path (§ 4) because the handover owner is still
unnamed — question Q5 of the deltas report.
