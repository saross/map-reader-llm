# Pre-launch audit — K-ladder tier E, the grid 384/50 MINIMAL text ladder

> **Last revised**: 2026-09-12 (original publication — the pre-spend gate for
> tier E, the only API spend the Principal Investigator (PI) approved for the
> closeout job). Controlling card: `planning/k-ladder-review-2026-09-11.md`
> (rulings R1 and R2). Pattern: `results/k-ladder-2026-09-12/phase2/pre_launch_audit.md`.
> See [§ Changelog](#changelog).

**Verdict: READY TO LAUNCH.** 0 blockers, 4 warnings, all four recorded in § 7
and none of them a reason to hold the run. Every candidate count is measured,
not extrapolated; the smoke run is executed and reproduces the carried
verifier's configuration hash exactly.

## 0. What is being launched, and what the gate authorises

| Field | Value | Anchor |
|---|---|---|
| Stage | one verifier pass per rung over a freshly built first-N consensus union | the PI's brief; Phase 2's pattern |
| Rungs | **3** (K = 1, 3, 5) | `unions.json`, `n_rungs` |
| Candidates | **7,239** measured (1,826 + 2,481 + 2,932) | `unions.json`, `total_candidates` |
| Model | `gemini-3-flash`, resolved by the client to `gemini-3-flash-preview` | `prompts/configs/verify_adversarial-text.json`; smoke meta |
| Config | `prompts/configs/verify_adversarial-text.json`, unmodified | ruling R1 |
| Thinking / temperature / iterations | MINIMAL / 0.0 / n = 1 | config, unmodified; smoke meta |
| Tier | real-time **flex** (`--service-tier flex`) | Phase 2's basis |
| Estimated cost | **US$5.0166** at 0.000693 USD per candidate | `unions.json`, `total_usd_estimate` |
| Approved | **US$5.02** | the PI's brief |
| Hard stop | running total above **US$7.00** | the PI's brief; `HARD_STOP_USD` |

Anything outside those three rows — a different model, a different config, a
re-run of a failed union, a proposer pass, a fourth rung — is **not** approved
and is not launched. The driver enforces the ceiling after every rung and exits
rather than starting another.

## 1. What the purchase completes

The grid study's 384 px / 50 % overlap pool is the **B geometry**, the same
tiling the deployment stride-B ladders use, and it already holds a verified
K = 10 cell: the committed `grid-postverifier-2026-08-18` 384/50 cell
(`results/grid-2026-08-18/conditions-verified/g384_ov192/`, best operating
point p ≥ 0.15, k ≥ 10, F1@20 0.8961 on the grid-common frame). Its K = 1, 3
and 5 siblings have never been verified — `results/grid-2026-08-18/findings.md`
lines 196–202 report that ladder **consensus-only**.

So tier E buys the corpus's only **verified MINIMAL-text ladder on the B
geometry at gold-standard scale**, which is the missing term in the comparison
`findings.md` § "Tension: MINIMAL ladders on the two corpora" needs: the
deployment stride-B MINIMAL ladder gains +0.0547 F1 from K = 1 to K = 10 and
the gold-standard MINIMAL ladders gain +0.0139 to +0.0629, and until now no
gold-standard MINIMAL ladder shared the deployment ladders' geometry.

## 2. Preregistration requirements (9 extracted, all HARD unless noted)

The requirement set is Phase 2's, unchanged: the same verifier stage, the same
config, the same crop standard. Re-read this session:
`results/k-ladder-2026-09-12/phase2/pre_launch_audit.md` § 1 and the config.

| # | Requirement | Source | Class | Verdict |
|---:|---|---|---|---|
| 1 | Verifier crops from the **source GeoTIFF rasters**, not tile PNGs | E33 | HARD | **MATCHES** — smoke: 5 raster, 0 tile-fallback; the driver refuses to verify a rung whose manifest reports any `tile_fallback_crops` |
| 2 | Crop size 150 × 150 px (`--padding 75`) | E33 | HARD | **MATCHES** — `PADDING_PX = 75`, imported from the Phase 2 driver; smoke manifest `crop_dimensions: "150x150"` |
| 3 | The verifier is fed a **consensus union**, not a single detection pass | E37 | HARD | **MATCHES** — each rung's input is `consensus-n<N>/consensus_t1.geojson` from `merge_passes.py --sweep --passes 1..N` |
| 4 | Verifier model `gemini-3-flash` | E37 | HARD | **MATCHES** — no `--model` passed; smoke meta `gemini-3-flash-preview` |
| 5 | Adversarial strategy (`verify_adversarial.md`) | E39 | HARD | **MATCHES** — instruction SHA-256 `2518d5298d9b84bac6810bb0d11e59ef534c46853f65cb25dc1454af3497e15d` |
| 6 | Verifier consensus n = 1 | E37 deviation 5 | RECOMMENDED | **MATCHES** — `--iterations` left at its default |
| 7 | Thinking level MINIMAL | config `_config_notes.thinking_level` | HARD | **MATCHES** — smoke meta `minimal` |
| 8 | Temperature 0.0 | config `_config_notes.temperature`; E37 | HARD | **MATCHES** — smoke meta `0.0` |
| 9 | A `prob_t`-thresholded F1 from these diagnostics is in-sample and test-set-optimised, and must be reported as such | E56 | HARD (reporting) | **MATCHES** — R2's sweep-optimal point is reported as `-opmax`, the convention that names the selection |

## 3. Config diff across the three rungs

**One config file, byte-identical, unmodified.** K lives in the *input* — the
union the verifier sees — not in any config field, so the expected diff table is
"everything controlled, nothing manipulated inside the config".

| Field | Identical across 3 rungs? | Value | Classification |
|---|:---:|---|---|
| `version` | YES | `verify_adversarial-text` | Controlled |
| `model` | YES | `gemini-3-flash` → `gemini-3-flash-preview` | Controlled (R1) |
| `instruction_file` | YES | `verify_adversarial.md` | Controlled (R1, E39) |
| `temperature` | YES | `0.0` | Controlled (R1) |
| `thinking_level` | YES | `minimal` | Controlled (R1) |
| `max_output_tokens` | YES | `8192` | Controlled |
| `examples` | YES | `[]` | Controlled (text-only track) |
| `text_only_labels` | YES | 6 labels | Controlled |
| `crop_label` | YES | "Now classify the candidate symbol…" | Controlled |
| `hypothesis` | YES | `H2` | Metadata |
| — | — | — | — |
| **union (the input)** | **NO — by design** | 1,826 / 2,481 / 2,932 candidates | **MANIPULATED — expected** |

**Intent → config check.** The factor the ladder tests (K) does differ between
conditions: the three unions differ by 655 and 451 candidates. The experiment
tests something.

**Config → intent check.** No config field differs. **Confounds: NONE inside
the config.** One confound *outside* it, in the K = 10 rung, is § 7 warning 1 —
it is a property of the committed sibling, not of this purchase.

## 4. The union gate — measured, not extrapolated

`scripts/run_k_ladder_tier_e.py unions`, on sapphire, US$0.

| row | K | passes | expected (PI) | measured | delta | % | verdict |
|---:|---:|---|---:|---:|---:|---:|---|
| 1 | 1 | `1` | 1,826 | **1,826** | +0 | 0.000 | **OK** |
| 2 | 3 | `1,2,3` | 2,481 | **2,481** | +0 | 0.000 | **OK** |
| 3 | 5 | `1,2,3,4,5` | 2,932 | **2,932** | +0 | 0.000 | **OK** |
| | | **total** | **7,239** | **7,239** | **+0** | | **0 STOP** |

Every rung reproduces the PI's expected count **exactly**, so nothing is within
three orders of magnitude of the 2 % STOP. The approval's US$5.02 and the
measured US$5.0166 agree to 0.3 cents.

**The pass filter was verified rather than assumed.** The pool holds thirteen
`run_*` directories: `run_1` … `run_10` plus `run_4_recovery`,
`run_8_recovery` and `run_10_recovery`. `merge_passes.resolve_pass_files`
parses the integer after `run_`, so `int("4_recovery")` raises and those three
directories are passed over — which is why a first-1 union is 1,826 and not
some doubled figure. Confirmed by the exact count reproduction above.

## 5. Transmission verification — the five-candidate smoke run

Executed on sapphire before this document was written, following Phase 2's
precedent: `results/k-ladder-2026-09-12/tier-e/smoke/` (5 of 5 succeeded, 0
failed, US$0.003449 audited flex). Its record is `smoke/smoke.json`.

| Error mode | Check | Verdict |
|---|---|---|
| Image flag off | Text-only track: `examples` is `[]`; no image payload expected or sent | **PASS** |
| Temperature shadowed | No `--temperature` passed; smoke meta records `0.0` from the config | **PASS** |
| Thinking level dropped | No `--thinking-level` passed; Flash, so no MEDIUM floor (E40/E58); smoke meta `minimal` | **PASS** |
| Model version drift | No `--model` passed; smoke meta `gemini-3-flash-preview`, the model R1 fixes | **PASS** |
| Tile size mismatch | N/A to a verifier pass — crops are 150 × 150 from rasters, independent of the proposer's tiling. Checked anyway: `padding: 75`, `crop_dimensions: "150x150"` | **PASS** |
| Wrong tile set | `--tiles-dir inputs/tiles_384_ov192`, the tile set the committed K = 10 crops manifest records for this pool (`outputs/grid-2026-08-18/verifier/g384_ov192/crops/candidate_manifest.json`, `tiles_dir`). It is a **fallback only**: 0 crops came from it in the smoke run | **PASS** |
| Wrong instruction file | `verify_adversarial.md`, SHA-256 `2518d5298d9b84bac6810bb0d11e59ef534c46853f65cb25dc1454af3497e15d` — **byte-identical to the hash Phase 2's 28 rungs stamped and to the August 3.7-screen verifier's.** The carried verifier's prompt has not moved | **PASS** |
| Example paths broken | No example images (`examples: []`) | **PASS (vacuous)** |
| Example image dimensions | Same | **PASS (vacuous)** |
| Agent model unpinned | Model pinned in the config, stamped into `run.meta.json` with `environment.git_commit`. No agent-spawning step | **PASS** |
| **E33 raster-crop mode** | Smoke extraction: 5 from rasters, 0 tile-fallback. The driver makes this a **pre-spend gate per rung**, not an after-the-fact check | **PASS** |
| **The flex correction** | Smoke meta records `cost_basis: "list"` under `--service-tier flex`, reproducing the defect Phase 2 documented. The driver therefore recomputes the audited figure from token counts rather than reading the meta | **PASS (defect confirmed, corrected)** |

**The rate is corroborated a sixth time.** The smoke run's US$0.003449 over 5
candidates is **US$0.00069 per candidate**, inside the audited 0.000684–0.000698
spread (`reports/token-load-audit-2026-06-12.md` § 5) and 0.4 % below the
adopted `VF_CALL_USD = 0.000693`.

**Blockers from transmission: NONE.**

## 6. Evaluation scope

Every rung will be swept and scored on the **board frame** `era2-b-487`
(`inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson`, 487 tiles,
435 curator reference mounds), per ruling R2, and additionally swept on the
Era-2 frame `full_evaluation_bounds.geojson` so the two frames' argmax
agreement can be reported as Phase 2 reported it. Both operating points are
materialised and scored:

- **sweep-optimal** (`-opmax`): the F1@20 argmax on the board frame, tie-broken
  highest F1 → lowest `vote_t` → lowest `prob_t`, the rule Phase 2 fixed;
- **carried**: `prob_t = 0.15`, `vote_t = K` — 0.15 because that is the
  committed grid cells' probability threshold
  (`g384-ov192-k10-verified-p0.15-k10`), so the ladder stays a ladder.

Evaluation recipe, identical to the board's and to Phase 2's: 14 buffers,
`mounds-reference.geojson`, 10,000 BCa draws, seed 42, `--mcc`.

**Tile vocabulary: checked, and it matches.** The tile-join invariant
(`reports/tile-mcc-geometric-join-2026-09-12.md` § 3) refuses an MCC when a
cell's `source_tile` vocabulary is not the frame's. Measured this session:
`outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson` and
`inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson` carry **the same
487 `tile_name` values, set-identical** (0 only in one, 0 only in the other), so
these cells are not the 3.7 family's case and their MCC is expected to compute.
The two frames' tile *polygons* differ slightly — union areas 1,364,471,339.5 m²
against 1,402,406,728.4 m², symmetric difference 37,935,388.9 m² — which is
§ 7 warning 3.

## 7. Warnings — four, none a blocker

### Warning 1 — the K = 10 rung of this ladder is built by a different rule

This is the substantive one, and it is a property of the **committed sibling**,
not of the purchase.

| union | candidates | builder | footprint |
|---|---:|---|---|
| K = 1 (this run) | 1,826 | `merge_passes.py` | pool native |
| K = 3 (this run) | 2,481 | `merge_passes.py` | pool native |
| K = 5 (this run) | 2,932 | `merge_passes.py` | pool native |
| **K = 10 (committed)** | **3,319** | `materialise_grid_unions.py` | **grid common 487-tile carrier (filtered)** |

`materialise_grid_unions.union_with_votes` assigns each cluster a primary
carrier tile via `prepare_h13_scoring.assign_primary_tiles` and then drops every
cluster with none (`gdf[gdf["source_tile"].notna()]`), and it clusters
*prepared* passes (`grid_analysis.load_cell_passes`, reading
`detections_dedup.geojson`) rather than the raw run GeoJSONs `merge_passes`
reads. Measured this session:

| K | `merge_passes` union | of those, on the common carrier | committed |
|---:|---:|---:|---:|
| 1 | 1,826 | 1,685 | — |
| 3 | 2,481 | 2,295 | — |
| 5 | 2,932 | 2,714 | — |
| 10 | 3,591 | **3,325** | **3,319** |

The carrier-filtered counts reproduce `results/grid-2026-08-18/sweep.csv`'s
`min_corroboration = 1, min_votes = 1` rows exactly at K = 1, 3 and 5 (1,685 /
2,295 / 2,714), and at K = 10 to within 6 features, so the mechanism is
identified rather than inferred.

**Why this is not a blocker, and what it costs.** The PI's expected counts are
the native `merge_passes` figures, so building the carrier-filtered union
instead would itself trip the 2 % STOP. Scoring normalises most of the
difference: the ~141–218 extra candidates per rung lie outside the board
frame's tile union, so they are excluded from the confusion and counted in
`n_outside_union` rather than mis-booked (out-of-frame points do not trip the
invariant — `tile-mcc-geometric-join` § 2). What it costs is about 7 % of the
spend on candidates that cannot score, and a ladder whose top rung's candidate
universe was assembled by a different rule. **Both are reported in
`findings.md` and put to the PI as a morning question rather than resolved
here.**

### Warning 2 — the committed K = 10 cell is scored on the grid-common frame

`results/grid-2026-08-18/conditions-verified/g384_ov192/eval/evaluation.json`
is on `grid_common_bounds.geojson`, not on `era2_b_intersection_bounds.geojson`.
Its F1@20 of 0.8961 is therefore **not** directly comparable with the
board-frame figures this run will produce. The board's own membership rule
treats `grid_common_bounds.geojson` as an admissible committed frame and
re-scores such cells on the board frame, so the remedy is the board's: the
K = 10 rung is re-scored on the board frame as part of the ladder. Recorded
because the pre-existing number must not be quoted beside the new ones.

### Warning 3 — the two 487-tile frames share a vocabulary but not a geometry

§ 6 measures it: identical `tile_name` sets, union areas differing by 2.7 %.
Consequence: a candidate can be inside one frame's tile union and outside the
other's, so the Era-2-frame sweep and the board-frame sweep are not guaranteed
to agree on the argmax. Phase 2 found they agreed on 28 of 28 rungs; this run
records the agreement per rung rather than assuming it.

### Warning 4 — `probabilities.json` is an envelope

Its top level holds six keys (`version`, `mode`, `verifier_config`,
`iterations`, `total_results`, `results`), so a per-candidate count is
`total_results`, not the number of top-level keys. Noted because the first
smoke report printed the latter; the driver was corrected before launch.

## 8. Completeness — what this audit did not check

- **The ladder's statistical instrument.** Whether the four rungs separate is
  measured after the run by `scripts/era1_leaderboard_tiering.py`, not here.
- **Board membership.** Whether these cells join the Era-2 board is the PI's
  under "ladder, then board", and is a separate decision from this spend.
- **The Hsu MCB admissible set** for this ladder — a different instrument
  (`scripts/selection_aware_intervals.py`), outstanding across the whole
  K-ladder job (`findings.md` § 6.1).
- **The grid study's other three geometries.** Tier E is the B geometry only.

## 9. Verdict

```text
Requirements extracted:        9 (8 HARD, 1 RECOMMENDED)
Requirements matched:          9 of 9
Transmission modes checked:   12
Transmission modes passed:    12 (2 vacuous)
Union count gate:              3 of 3 OK, delta +0 on every rung
Smoke run:                     5 of 5 verified, 0 failed, US$0.003449
Blockers:                      0
Warnings:                      4 (§ 7; warning 1 is substantive and reported
                                  onward, not resolved)

OVERALL: READY TO LAUNCH
Authorised spend: US$5.02 approved; US$5.0166 estimated; hard stop US$7.00
```

## Changelog

### 2026-09-12 — Original publication (tier E pre-spend gate)

Written before the three rungs ran, after the unions were built and the
five-candidate smoke run executed, both at the approved gate's parameters.
Sources read this session: `prompts/configs/verify_adversarial-text.json`;
`results/k-ladder-2026-09-12/tier-e/unions.json` and `smoke/smoke.json`;
`results/k-ladder-2026-09-12/phase2/pre_launch_audit.md` (the pattern and the
nine requirements); `outputs/grid-2026-08-18/verifier/g384_ov192/crops/candidate_manifest.json`
and `union_k10.geojson`; `results/grid-2026-08-18/sweep.csv` and
`findings.md`; `scripts/materialise_grid_unions.py`,
`scripts/grid_analysis.py` and `scripts/merge_passes.py` for warning 1's
mechanism; and the two 487-tile bounds files, measured directly for § 6 and
warning 3. No committed artefact was altered by this audit.
