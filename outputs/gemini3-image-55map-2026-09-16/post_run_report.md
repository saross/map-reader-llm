# Post-run report — Gemini 3 image at 55-map scale, K = 1, 3 and 5

> **Last revised**: 2026-09-20 (original publication — **ROW COMPLETE AND
> REGISTERED, UNSIGNED**. Five proposer passes, three first-N unions, six
> verifier legs, eighteen scored cells, and the declared family run at all
> three rungs. Audited **US$432.1121**, of which the six verifier legs
> account for **US$189.4717** against the Principal Investigator's (PI)
> US$200 provisional. Every registration field the PI signs is left null.)
> See [§ Changelog](#changelog) for revision history.

Declaration of the tests and their caveats:
`reports/image-2x2-tests-declaration-2026-09-19.md`. Findings and the
per-cell numbers: `results/gemini3-image-55map-2026-09-16/findings.md`.
Row A of the same 2×2, whose structure this record mirrors:
`outputs/gemini37-image-55map-2026-09-13/post_run_report.md`.

**Status: ROW COMPLETE, REGISTERED, UNSIGNED.** All three rungs are scored on
both arms. K = 3 is the declared primary rung; K = 1 and K = 5 are exploratory
replicates whose test JSONs were being regenerated under a four-member
Benjamini–Hochberg (BH) family when this report was written (PI ruling
2026-09-20, declaration § 3).

## 1. What ran

| Stage | State | Audited USD | Note |
|---|---|---:|---|
| Gold Standard (GS) K = 3 union, `image-b-gs-2026-08-28` | **built**, 2,227 candidates | 0.00 | `image_b_prepare_and_union.py` first-N |
| GS K = 5 union | **built**, 2,788 candidates | 0.00 | same builder |
| GS calibration, K = 3 arm 1 | **2,227 / 2,227**, 0 failed | **1.5383** | `gemini-3-flash-preview`, minimal, T = 0.0; 2026-09-17 23:50–23:52 UTC (`276e25dcb`) |
| GS calibration, K = 5 arm 1 | **2,788 / 2,788**, 0 failed | **1.9219** | 2026-09-17 23:52–23:56 UTC (`276e25dcb`) |
| GS calibration, K = 3 arm 2 | **2,227 / 2,227**, 0 failed | **2.4629** | `gemini-3.7-flash`, low, T = 0.0; 2026-09-18 22:13–22:47 UTC (`99afa6a4d`) |
| GS calibration, K = 5 arm 2 | **2,788 / 2,788**, 0 failed | **3.0878** | 2026-09-18 22:47–22:59 UTC (`99afa6a4d`) |
| GS sweeps, both arms, 20 m | **carried points fixed** | 0.00 | anchor gate 0.8961352657 against the registered 0.8961 |
| 55-map proposer pass 1 | **COMPLETE**, 24,561 / 24,561 | **46.7033** | 2026-09-16 13:06:48 → 15:23:32 UTC; 13 tiles to recovery |
| 55-map proposer pass 2 | **COMPLETE**, 24,561 / 24,561 | **46.6927** | 15:24:04 → 17:33:58 UTC; 10 tiles to recovery |
| 55-map proposer pass 3 | **COMPLETE**, 24,561 / 24,561 | **46.7196** | 17:34:00 → 19:41:38 UTC; 13 tiles, two recovery rounds |
| 55-map proposer pass 4 | **COMPLETE**, 24,561 / 24,561 | **46.7307** | 19:41:41 → 21:47:45 UTC; 17 tiles to recovery |
| 55-map proposer pass 5 | **COMPLETE**, 24,561 / 24,561 | **46.7831** | 21:47:47 → 23:56:12 UTC; 18 tiles, two recovery rounds |
| Recovery, all five passes | **COMPLETE** | (in the pass rows) | 2026-09-17 00:00:44 → 00:02:41 UTC, two rounds; `recovery.log` |
| **55-map proposer pool, five passes** | **COMPLETE**, 122,805 tile-passes | **233.6295** | US$0.00190 per tile-pass (`1553a7b24`) |
| Coverage gate, all five passes | **PASS** | 0.00 | 24,561 / 24,561 each, base plus recovery fragments |
| K = 1 union (pass 1, first-N) | **built**, 22,785 candidates | 0.00 | `union_k1.geojson` |
| K = 3 union (first-N) | **built**, 36,389 candidates | 0.00 | votes {1: 17,677; 2: 6,476; 3: 12,236} |
| K = 5 union (first-N) | **built**, 45,786 candidates | 0.00 | votes {1: 21,406; 2: 6,697; 3: 3,889; 4: 3,441; 5: 10,353} |
| K = 1 arm 1 (`gemini-3-flash-preview`, minimal) | **22,785 / 22,785**, 0 failed | **15.7559** | realtime flex, 2026-09-19 00:37:48 → 01:04:12 UTC (26 m 24 s), 8 server-error retries (`34fd61920`) |
| K = 3 arm 1 | **36,389 / 36,389**, 0 failed | **25.1020** | realtime flex, 01:04:13 → 01:45:19 UTC (41 m 06 s), 19 retries (`fc5079d0a`) |
| K = 5 arm 1 | **45,786 / 45,786**, 0 failed | **31.5422** | realtime flex, 01:45:21 → 02:35:40 UTC (50 m 19 s), 58 retries (`79a2afc0d`) |
| K = 1 arm 2 (`gemini-3.7-flash`, low) | **22,785 / 22,785**, 0 failed | **25.3978** | **Batch API**, chunks of ≤ 4,000 requests; folded in by `batch-recover` 04:10:10 UTC; no job ledger committed (§ 3.2) (`cda04a952`) |
| K = 3 arm 2 | **36,389 / 36,389**, 0 failed | **40.5813** | **Batch API**, ten jobs all SUCCEEDED; lodged 04:12 UTC, drained 13:58:15 UTC (9 h 46 m) (`e21b5295a`) |
| K = 5 arm 2 | **45,786 / 45,786**, 0 failed | **51.0925** | **Batch API**, twelve jobs across two ledgers after a File API 429 (§ 3.1); recovered 22:11:18 UTC (`880c207f7`) |
| **Six verifier legs** | **COMPLETE**, 209,920 verifications | **189.4717** | US$0.000689–0.000692 (arm 1) / US$0.001115–0.001116 (arm 2) per candidate |
| Sweep, K = 1, both arms | **complete** | 0.00 | 20 and 26 achievable points (`8491f9c78`) |
| Sweep, K = 3, both arms | **complete** | 0.00 | 60 and 84 achievable points (`5d106e1d5`) |
| Sweep, K = 5, both arms | **complete** | 0.00 | 100 and 145 achievable points (`983018037`) |
| Materialisation, 18 cells | **complete** | 0.00 | carried + F1 oracle + MCC oracle per arm per rung |
| Scoring, K = 1 cells | **complete** | 0.00 | r2 engine, 2026-09-19 (`ba19eebd1`) |
| Scoring, K = 3 cells | **complete** | 0.00 | r2 engine (`e29bc17db`) |
| Scoring, K = 5 cells | **complete** | 0.00 | r2 engine (`6e30bcc5a`) |
| Tests, K = 3 (declared PRIMARY family) | **complete** | 0.00 | `results/image-2x2-2026-09-19/tests_2x2_K3.json` (`ed3861cac`) |
| Tests, K = 1 and K = 5 (exploratory) | **complete, being regenerated** | 0.00 | `tests_2x2_K1.json` (`615636acb`), `tests_2x2_K5.json` (`8308f039f`); four-member BH family ruled 2026-09-20 |
| Registration | **complete, UNSIGNED** | 0.00 | 1 registry row, 1 facts row, 18 conditions, 6 verifier passes, 1 analysis row |
| Findings document | **complete** | 0.00 | `results/gemini3-image-55map-2026-09-16/findings.md` |
| **ROW TOTAL** | | **432.1121** | proposer 233.6295 + six legs 189.4717 + four GS legs 9.0109 |

Carried operating points, from the GS calibration legs swept at the GS-primary
20 m buffer:

| Arm | Verifier | K = 3 carried | K = 5 carried | K = 1 carried analogue | GS F1 @ 20 (K = 3) |
|---|---|---|---|---|---:|
| arm 1 | `gemini-3-flash-preview`, `verify_adversarial-text`, T = 0.0, minimal | (0.15, k3) | (0.15, k5) | (0.15, k1) | 0.8200 |
| arm 2 | `gemini-3.7-flash`, same configuration, thinking `low` | (0.88, k3) | (0.95, k5) | (0.88, k1) | 0.8408 |

The K = 1 points are **carried analogues**: no K = 1 Gold Standard leg was run,
so each arm takes its K = 3 leg's probability with the vote threshold collapsed
to 1. The registration records `basis: "carried-analogue"` on those six
conditions rather than `"carried"`. Arm 2's K = 5 probability is **0.95**, not
the K = 3 leg's 0.88, because each rung carries its own calibration leg's
point.

## 2. Gates

| Gate | Basis | Reading |
|---|---|---|
| Proposer coverage, per pass | `driver.log` plus each pass's base and recovery metas | **PASS** — 24,561 / 24,561 on all five passes (24,548 + 13; 24,551 + 10; 24,548 + 10 + 3; 24,544 + 17; 24,543 + 17 + 1) |
| Verifier booking, per leg | `run.meta.json` `items_processed` against the union's feature count | **PASS** — 22,785 / 22,785, 36,389 / 36,389, and 45,786 / 45,786 on **both** arms, `items_failed` 0 everywhere |
| Calibration constants | `scripts/gemini37_image_55map_r2.py` `G3.carried` against the four `gs-calibration/*/analysis.json` `image_best` blocks | **PASS** — (0.15, k3), (0.15, k5), (0.88, k3), and (0.95, k5) agree exactly |
| GS anchor | `gs-calibration/*/analysis.json` `anchor` | **PASS** — 0.8961352657 re-scored against the registered 0.8961 on all four legs |
| Tile join | each cell's `evaluation.json` tile confusion | **PASS** — all eighteen cells sum to 8,541 tiles, `tile_join` `id` |
| Cell ↔ sweep agreement | `cells_manifest.json` against `sweeps.json` | **PASS** — every cell's `(prob_t, min_votes)` and `n_detections` reproduce the sweep record |
| Per-candidate rate stability | `audit_verifier_cost.py` | **PASS** — arm 1 US$0.000689–0.000692, arm 2 US$0.001115–0.001116 across three rungs spanning a 2 × candidate range |
| Registration | `verify_run_conditions.py --run gemini3-image-55map-2026-09-16` | **PASS** — `1 run(s): 1 pass, 0 partial, 0 fail` |
| Manifest validation | `generate_post_run_report.py --all` | **PASS** — `ALL VALID (43 runs + 629 conditions + 1339 passes + 70 analyses vs schemas)`, no registry ↔ facts drift block |

**On the cost gate.** There was no per-pass hard stop of row A's kind. The PI
approved a **US$200 provisional for the row's verifier legs**
(`planning/paper-writeup-continuity.md`, the S156 rulings block), with a stop
rule of "any leg more than 10 % over its estimate, or short of its union count
after cleanup, halts the sequence". No leg tripped it; the six legs closed at
**US$189.4717**, US$10.53 inside the provisional.

## 3. Incidents

### 3.1 The File API 20 GiB cap split the K = 5 arm 2 job ledger

The K = 5 arm 2 leg lodged twelve batch jobs of at most 4,000 requests. Chunks
0–3 lodged; chunks 4–11 failed with **429 `FileStorageBytesPerProject`** — the
Gemini File Application Programming Interface's (API) 20 GiB per-project cap,
against which every batch request JSONL counts for thirty days. Space was
freed by deleting the completed K = 1 and K = 3 verifier input files, and
chunks 4–11 were re-lodged between 14:34:18 and 14:42:35 UTC on 2026-09-19.

The consequence for the record is that **this leg's job ledger lives in two
files**:

- `verify_k5_arm2/batch_jobs.json` — the driver's ledger, chunks 0–11, whose
  re-lodged entries carry the state string `JOB_STATE_SUCCEEDED (re-lodged
  after FileStorageBytesPerProject 429; folded in by batch-recover 2026-09-19
  22:11 UTC)`;
- `verify_k5_arm2/batch_jobs_relodged.json` — the eight re-lodged chunks with
  their own job names and `lodged_at` stamps, and the `reason` field
  `re-lodged after 429 FileStorageBytesPerProject at first lodging`.

Both are committed (`880c207f7`). The leg's `run.meta.json`
`results_summary.batch_recover.jobs` lists the twelve job names it folded in,
and `recovered_rows` is 45,786. The pre-recovery probabilities file is
preserved beside it as
`probabilities.json.pre-recover-20260919T221118.backup`.

**The hardening this asks for** (not done here, recorded for the PI):
`scripts/lib_batch_api.py` gained `preflight_file_storage` on the proposer
path, but the verifier batch path did not call it before lodging at the time
of this run. A storage preflight on the verifier path would have caught the
cap before eight chunks failed.

### 3.2 Two legs' metas are post-recovery, not whole-leg, records

`verify_k1_arm2/run.meta.json` and `verify_k5_arm2/run.meta.json` carry
timestamps of 0.43 s and 0.79 s, because the surviving meta is the
`batch-recover` step's, not the leg's. Their `usage_stats` and
`execution_stats` **are** whole-leg — 22,785 and 45,786 items with the full
token counts, sourced from `batch_results.jsonl` per-response
`usageMetadata` — so `audit_verifier_cost.py` prices them correctly, but the
`timestamp` block must not be read as a leg duration. Each of the two legs also
keeps a `run.meta.pre-rerun-1.json` sidecar, which the auditor flags as a
"merge sidecar present without a merged primary meta" and correctly does
**not** add in.

`verify_k1_arm2` has **no** `batch_jobs.json` committed. Its `run.meta.json`
`results_summary.batch_recover.jobs` names one job (`recovered_rows` 4,000), so
the names of that leg's remaining chunks are not recoverable from the working
tree. This is a gap in the audit trail, not in the data — the leg books
22,785 / 22,785 from `batch_results.jsonl`, whose per-response `usageMetadata`
is what the cost audit prices.

### 3.3 The proposer driver's completion line ignores its return code

`driver.log` records `PASS 2 end rc=2 completed=24561/24561` and the same for
passes 3, 4, and 5: the driver
(`scripts/run_g3_image_55map_passes.sh`, per the S155 code-audit note in
`planning/paper-writeup-continuity.md`) parses the progress bar for the tile
count and ignores the process return code, so a non-zero `rc` did not stop the
sequence. In this run the coverage gate closes the question independently —
every pass is 24,561 / 24,561 once its recovery fragments are counted — but the
driver should not be reused without the fix.

### 3.4 A flex 503 window ran through the whole proposer day

`flex-watch.log` records a blocked-and-retried sentinel every ~15 minutes from
2026-09-16 13:24:55 UTC, with block durations from 1.3 s to 116.0 s, and
`flex capacity RETURNED` at 22:55:01 UTC. The passes ran through it at a flat
cost (0.19 % spread) and a flat cached share (0.812 on every pass), so the
congestion cost wall-clock rather than money. Arm 1's verifier legs, run on
2026-09-19, took 8, 19, and 58 server-error retries across 104,960
verifications with zero failures.

## 4. How this ran, and how to reproduce it

All stages come from the campaign-generic drivers with `CAMPAIGN=g3`; nothing
in this row needed a bespoke script.

```bash
# 1. The Gold Standard calibration legs, which FIX the carried points.
#    Ran 2026-09-17/18; both arms, K = 3 and K = 5, over image-b-gs-2026-08-28.
bash scripts/gemini3-image-55map-gs-calibration.sh
#    -> results/gemini3-image-55map-2026-09-16/gs-calibration/k{3,5}/arm{1,2}/
#       analysis.json; the anchor gate re-scores text-B at 0.8961.

# 2. The five proposer passes, sequentially, on realtime flex.
#    Complete 2026-09-16 23:56:13 UTC; recovery 2026-09-17 00:02:41 UTC.
#    Audited US$233.6295 -- audit with the RIGHT rate card:
.venv/bin/python scripts/audit_proposer_cost.py \
    outputs/gemini3-image-55map-2026-09-16/g384_ov192_55map_g3img \
    --model gemini-3-flash-preview
#    WITHOUT --model this prices at gemini-3.7-flash and reads US$345.9024.

# 3. Unions, crops and the verifier arms, one rung and arm at a time.
#    Arm 1 on realtime flex; arm 2 on the Batch API (PI ruling 2026-09-18).
CAMPAIGN=g3 STAGES=arms ARMS=arm1 KS='1 3 5' WORKERS=50 \
    nohup bash scripts/image-55map-unions-and-arms.sh \
    > outputs/gemini3-image-55map-2026-09-16/arms_arm1.log 2>&1 < /dev/null &
#    NOTHING after the & on that line (agent-guidance, blocked-launch rule).
#    Gate each leg on run.meta.json items_processed == the union's feature
#    count, then audit:
.venv/bin/python scripts/audit_verifier_cost.py \
    outputs/gemini3-image-55map-2026-09-16/verifier/g384_ov192_55map_g3img/verify_k3_arm1 \
    --tier flex
#    -> use the STAGE TOTAL (audited) line, never cost_estimate.

# 4. Sweep, materialise, score and test, per rung.
.venv/bin/python scripts/gemini37_image_55map_r2.py --stage selftest --campaign g3
.venv/bin/python scripts/gemini37_image_55map_r2.py --stage sweep --campaign g3 \
    --rungs 3 --workers 12
.venv/bin/python scripts/gemini37_image_55map_r2.py --stage materialise \
    --campaign g3 --rungs 3
#    COMMIT the materialised detections here: the engine's
#    --require-clean-inputs exits 4 on an untracked input.
.venv/bin/python scripts/gemini37_image_55map_r2.py --stage score --campaign g3 \
    --rungs 3 --workers 5 --jobs 4
.venv/bin/python scripts/gemini37_image_55map_r2.py --stage tests-2x2 --rungs 3

# 5. Registration. FOUR hand-authored inputs, then two machine steps. There is
#    no generic registrar; scripts/register_r2_conditions.py is a one-shot
#    r1-to-r2 migration tool with its run ids as module constants.
#      (a) results/run-registry.json  -- one entry
#      (b) results/run-facts.json     -- the sibling the drift check pairs with
#      (c) results/run-conditions.json -- proposer_pools, six verifier_passes,
#          eighteen conditions; metrics are NOT hand-authored, the generator
#          extracts them from each row's eval_path
#      (d) results/run-analyses.json  -- ONE row, manually_verified_at null
.venv/bin/python scripts/verify_run_conditions.py \
    --run gemini3-image-55map-2026-09-16
#    -> "1 run(s): 1 pass, 0 partial, 0 fail"
.venv/bin/python scripts/generate_post_run_report.py --all
#    -> "ALL VALID (...)" and NO "=== registry <-> facts drift ===" block
.venv/bin/python scripts/generate_post_run_report.py --all --write
```

**The scoring instrument.** `scripts/evaluate_detections.py` against
`inputs/vectors/references/best-available-gt-55maps-r2.geojson` over
`inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` — 14 buffers,
bootstrap 10,000, seed 42, `--mcc`, `--require-clean-inputs` — which is the r2
board's own stage-2 recipe and row A's instrument, chosen so the 2×2's four
cells are compared within one instrument.

**Do not** re-tier the 55-map board or the tile-MCC tiering, and touch no
signed row. This run's cells live only in its own results tree.

## 5. Environment

- The proposer passes, the verifier legs, and the analysis stages all ran on
  **sapphire** (`planning/paper-writeup-continuity.md`, S155 and S156 blocks;
  the metas' `environment` blocks record the script and its git commit, not a
  hostname, so the host is recorded there rather than in the artefacts).
- The proposer passes ran at `--service-tier flex --workers 12`, sequentially,
  from `scripts/run_g3_image_55map_passes.sh`.
- `outputs/gemini3-image-55map-2026-09-16/` holds `driver.log`,
  `flex-watch.log`, `pass{1..5}.log`, `recover*.log`, `recovery.log`, the
  residual manifests `missing_run_{1..5}.json`, and the second-round residuals
  `still_run_3.json` and `still_run_5.json`.
- **Neither the crop directories nor the batch request JSONLs survive in the
  working tree.** `verifier/g384_ov192_55map_g3img/` holds only the three
  unions, their provenance sidecars, and the six leg directories; the
  per-chunk `verifier_requests_chunk*.jsonl` files named in each
  `batch_jobs.json` were deleted after their legs completed — the K = 1 and
  K = 3 ones deliberately, to free File API storage for the K = 5 lodging
  (§ 3.1). They are reproducible from the unions and the crops.
- Committed per leg: `probabilities.json`, `run.meta.json`, and — on the batch
  legs — `batch_results.jsonl` and the job ledgers.

## 6. Registration, and what is left for the PI

Registered 2026-09-20, **entirely unsigned**:

| File | What was added | Signature state |
|---|---|---|
| `results/run-registry.json` | one entry, `status` `active` | n/a |
| `results/run-facts.json` | one entry: purpose, scope `55maps-8541`, headline condition, five `_flags` | n/a |
| `results/run-conditions.json` | one proposer pool, **six** verifier passes (`modality` `text`), **eighteen** conditions | n/a |
| `results/run-analyses.json` | **one** analysis row | `manually_verified_at` null; `signature.status` `unsigned`; `outcome` null |
| `results/analyses-manifest.json` and the four sibling manifests | regenerated by the generator | the analysis row carries the unsigned signature through |

**Verifier-pass modality.** All six legs are registered `"text"`. Each leg's
`run.meta.json` `configuration` records `example_count` 0, `library_hash`
`"no_examples"`, and an empty `library_manifest`, which is exactly the E88
derivation rule's "text" (`results/run-conditions.json` `_README`;
`scripts/derive_condition_modality.py`). Row A's six verifier passes are
recorded `"image"` on byte-identical evidence, which
`reports/comparability-inventory-37-runs-2026-09-20.md` § 5 finding 13 records
as a register inconsistency awaiting an erratum (§ 6 item 5). Row B does not
replicate it, so the two rows' blocks differ on this field **by intent, not by
accident**.

**Open for the PI**: the signature on this row's analysis entry; whether its
`outcome` should be written now or after the K = 1 and K = 5 test JSONs are
rebuilt under the four-member BH family; row A's verifier-pass `modality`
erratum; and the File API storage hardening in § 3.1.

## Changelog

### 2026-09-20 — Original publication

Written on the row's completion and registration. State at publication: five
proposer passes at 24,561 / 24,561 each (audited US$233.6295), three first-N
unions at 22,785 / 36,389 / 45,786, six verifier legs each booking its full
union with zero failures (audited US$189.4717 of the US$200 provisional), four
Gold Standard calibration legs (US$9.0109), eighteen scored cells, and the
declared five-test family run at K = 3 with exploratory replicates at K = 1 and
K = 5. Row total audited **US$432.1121**.

Registration landed the same day and is **unsigned throughout**:
`verify_run_conditions.py --run gemini3-image-55map-2026-09-16` reported
`1 run(s): 1 pass, 0 partial, 0 fail`, and `generate_post_run_report.py --all`
reported `ALL VALID (43 runs + 629 conditions + 1339 passes + 70 analyses vs
schemas)` with no registry ↔ facts drift block.

Not done at publication, and recorded as open: the verifier batch path's
storage preflight (§ 3.1); the recovery of the K = 1 arm 2 leg's five missing
job names (§ 3.2); and the proposer driver's return-code gate (§ 3.3).
