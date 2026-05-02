# Temperature, transient errors, and failure-recovery on the 55-map proposer cross-run — synthesis report

**Date**: 2026-04-30
**Sessions**: 79–80 (working-notes Obs 281)
**Primary observation**: Obs 281 in `docs/notes/reflections/working-notes.md`
**Companion observations**: Obs 286 (verifier-T pilot Stage A), Obs 287 (Stage B + production-default recommendation), Obs 297 (T=0.7 vs T=MIN paired permutation at 55-map scope)
**Status**: Methods-load-bearing synthesis. No new compute; consolidates existing artefacts.

## 1. Executive summary

The pre-investigation framing of "~6 % verifier failure rate at T=0.3" was a **misreading of the
`finish_reason_counts.error` field in `run.meta.json`**. That field counts **transient API errors
that the in-run retry layer subsequently recovered**, not unrecovered post-pipeline failures. The
genuine post-pipeline residual on the T=0.3 generalisation run was **18 unrecovered proposer
tile-passes (out of 42,705 = 0.042 %) plus 1 unrecovered verifier candidate (out of 9,909 =
0.010 %)** — roughly **two orders of magnitude smaller** than the misread headline.

A subsequent single-round recovery (`run_pv.py cleanup` style) closed both residuals at a total
cost of **$0.034** versus the inflated $1.10 estimate that would have followed from the
misreading. This makes recovery a standard cheap post-run step, regardless of decoding
temperature.

The headline temperature-failure-rate hypothesis (Shawn's standing intuition that "the further
the API call temperature is from the SDK default of T=1.0, the higher the parse / empty-response
failure rate, with T=0.0 worst") was **NOT supported on the proposer cross-run** when comparing
T=0.3 vs T=0.7. The verifier-side limb was subsequently closed by the verifier-T pilot (Obs 286 +
287) with a directional finding in the **same** spirit (T=0.0 produces deterministic verifier
failures that vanish at T > 0), so the broad intuition is salvaged on the verifier but
unsupported on the proposer.

> **Flagged contradiction (see § 4 and § 11)**: Obs 281's proposer comparison table cites
> "25 / 42,545 = 0.059 %" as the T=0.7 unrecovered failure count. Re-reading the on-disk meta
> files and `cost_manifest.json` for `outputs/55maps-text-high-generalisation/` shows
> **160 / 42,705 unrecovered failures (0.375 %)** as the actual T=0.7 residual. The "25" appears
> to be the run_1 row of the per_pass cost-manifest table mistaken for the total. Under the
> corrected number, **T=0.3 (18 / 42,705 = 0.042 %) has a far lower unrecovered rate than T=0.7
> (160 / 42,705 = 0.375 %)** — opposite to Obs 281's tabulation but in the **same direction** as
> Obs 281's headline conclusion (lower T → fewer unrecovered failures on this corpus). The
> headline conclusion stands; the magnitude in the table needs correction in any paper-Methods
> citation.

## 2. The transient-vs-truly-missing distinction (Methods-paragraph payload)

This section is the load-bearing Methods note for any paper paragraph citing failure rates from
the runtime artefacts.

### 2.1 What `finish_reason_counts.error` does measure

`run.meta.json`'s `execution_stats.finish_reason_counts` is a histogram of **per-API-call
outcomes**, summed across all retry attempts within the run. Counts include attempts that the
in-run retry layer subsequently re-issued. The field is therefore an **upper bound on attempt-
level error events**, not a count of post-pipeline failures.

A typical lifecycle for one item:

1. First API call → 503 / parse-failure / empty content → `finish_reason: error` (count + 1).
2. Retry layer waits and re-issues → success → `finish_reason: success` (count + 1).
3. Item completes successfully; the response in `probabilities.json` / `detections.geojson` is
   the success-branch output.

The histogram has accumulated **one error and one success** for a single item that completed
successfully. Summing `error` therefore overstates true failure when retries succeed.

### 2.2 What `finish_reason_counts.error` does NOT measure

It does not measure **truly-missing items** at the end of the run. Truly-missing items are those
whose final state — after the retry budget is exhausted — has no entry in the canonical output
file (`probabilities.json` for the verifier, the per-pass `*.geojson` plus `failed_items[]` for
the proposer).

### 2.3 The canonical post-pipeline failure formula

For the verifier (Obs 286 codified this):

```text
n_failures = len(consensus_manifest) − len(probabilities['results'])
```

Compute the candidate-id set difference between the consensus input and the verifier
`probabilities.json`; the count of missing IDs is the truly-unrecovered failure count.

For the proposer (Obs 281, recovery script `scripts/55maps-t0.3-recovery.sh` § Phase 1):

```text
unrecovered_per_pass = len(execution_stats['failed_items'])  # authoritative per-pass meta
total_unrecovered    = sum(unrecovered_per_pass for pass in 1..K)
```

The aggregated cross-pass count is also exposed as `tiles_failed` in
`cost_manifest.json::by_stage.proposer`, which is the cleanest single read for downstream
analysis.

> **Schema gotcha** (Obs 281 explicit caveat): `execution_stats.items_processed` and
> `execution_stats.items_failed` in the per-pass meta are broken accounting fields when the
> resume mode of `4_detect_mounds_batch.py` rewrites `meta.json`. Use `failed_items[]` (the
> array) and the cost-manifest `tiles_failed` (the post-aggregation count) as authoritative;
> **do not** trust `items_failed: 0` after a resume / recovery has touched the meta.

### 2.4 Mechanism note

`finish_reason: error` captures heterogeneous causes: HTTP 5xx, rate-limit 429, parse failures
on returned content, and empty responses (`empty_responses` and `parse_failures` in the same
stats block typically over-count for the same retry events). For sampling temperatures > 0,
re-issuing the call typically traverses a different decoding path and recovers the item; for
T = 0.0, the call is deterministic and a problematic crop produces the same response on retry —
the retry-loop cannot escape a degenerate parse path. This mechanism is verified at the
verifier in Obs 286 (T = 0.0 → 154 transients / 10 unrecovered; T = 0.5 → 20 / 0; T = 1.0 →
7 / 0).

## 3. Empirical data — 55-map proposer cross-run

Both runs use the same `detect_brief-text` proposer config (`gemini-3-flash`, `thinking_level:
high`, K = 5 passes, 8,541 tiles per pass = 42,705 total proposer attempts), seed 42, identical
55-map manifest. Verifier held at T = 0.0 in both (the verifier-T limb was tested separately by
Obs 286).

### 3.1 Proposer (verified from `cost_manifest.json::by_stage.proposer`)

| Run                                       | T   | Unrecovered failures (current files) | Rate    | Source                                               |
|:------------------------------------------|:---:|:-------------------------------------|:--------|:-----------------------------------------------------|
| `55maps-text-high-generalisation`         | 0.7 | **160 / 42,705**                     | 0.375 % | `outputs/55maps-text-high-generalisation/cost_manifest.json` (`tiles_failed: 160`) |
| `55maps-text-high-t0.3-generalisation` (pre-recovery) | 0.3 | 18 / 42,705                          | 0.042 % | Obs 281 (was on disk before commit `548604d9`)        |
| `55maps-text-high-t0.3-generalisation` (post-recovery) | 0.3 | 0 / 42,705                           | 0.000 % | `outputs/55maps-text-high-t0.3-generalisation/cost_manifest.json` (`tiles_failed: 0`) |

Re-verified on disk on 2026-04-30: T=0.7 cost manifest reports `tiles_failed: 160` with per-pass
breakdown 25 / 42 / 38 / 28 / 27 (sum = 160). T=0.3 cost manifest reports `tiles_failed: 0`
across all five passes (post-recovery state; the recovery overwrote per-pass metas, then
`merge_recovery_meta.py` consolidated them).

### 3.2 Verifier (current files match Obs 281)

| Source                                               | Date         | Candidates | Truly missing post-pipeline | Rate    |
|:-----------------------------------------------------|:-------------|:----------:|:---------------------------:|:-------:|
| T=0.7 source pool                                    | 2026-04-18   | 9,131      | 0                           | 0.000 % |
| T=0.3 source pool (pre-recovery)                     | 2026-04-26   | 9,909      | 1 (`candidate_05396`)       | 0.010 % |
| T=0.3 source pool (post-recovery)                    | 2026-04-27   | 9,910      | 0                           | 0.000 % |

Re-verified on disk: T=0.3 `verified/run.meta.json` shows `finish_reason_counts.error: 629`,
`parse_failures: 629`, `empty_responses: 629` and `probabilities.json` contains 9,910 results.
The 629-error misreading would have been "6.35 % verifier failures"; the actual unrecovered
count was 1 of 9,909 candidates pre-recovery (0.010 %), recovered to 0 of 9,910 post-recovery
at $0.003 cost.

### 3.3 Hypothesis verdict

The standing intuition predicted T = 0.3 should have a **higher** failure rate than T = 0.7
(further from SDK default T = 1.0). Empirically:

- **T = 0.3 (0.042 % unrecovered) was lower than T = 0.7 (0.375 % unrecovered)**.
- Direction is **opposite to the hypothesis** on the proposer.
- One plausible mechanism: lower-temperature outputs are more deterministic and less likely to
  produce malformed JSON variations the parser cannot handle.

The proposer-side hypothesis is therefore **not supported**. The verifier-side limb is closed
separately by Obs 286 (§ 5 below) with a directional finding in the spirit of the original
intuition (T = 0.0 worst, T > 0 better), but for a different reason — the deterministic
dead-end mechanism rather than a generic distance-from-SDK-default heuristic.

## 4. Caveat — Obs 281 magnitude correction needed

Obs 281's proposer comparison table cites **"25 / 42,545"** for the T = 0.7 row. Re-reading the
files on 2026-04-30:

- `outputs/55maps-text-high-generalisation/cost_manifest.json::by_stage.proposer.tiles_failed`
  = **160** (with per-pass 25 / 42 / 38 / 28 / 27).
- The `42,545` denominator matches `tiles_processed` = `total tiles − tiles_failed` =
  42,705 − 160. Using `tiles_processed` as the denominator inflates the rate-of-success view; the
  proper failure-rate denominator is **42,705** (total attempts), giving 160 / 42,705 = 0.375 %.
- T=0.7 was not subjected to a recovery pass (no recovery commit in
  `git log -- outputs/55maps-text-high-generalisation/proposer/`); the 160 is therefore both the
  pre- and post-recovery state.

Most plausible cause of the Obs 281 number: the per-pass table in the cost manifest's
`per_pass[]` list shows pass 1 as `tiles_processed: 8516, tiles_failed: 25`. The "25" may have
been read as the cross-pass total. Working forward in the paper Methods, **use 160 / 42,705
(0.375 %) for T = 0.7**, not 25 / 42,545.

The correction does not invalidate the headline qualitative finding — T = 0.3's 0.042 % is still
lower than T = 0.7's 0.375 %, in the same direction Obs 281 reported, just at a wider margin.
But the magnitude difference (factor of ~9 vs the originally-implied factor of ~1.4) is
methodologically informative and worth getting right.

## 5. Companion verifier-side findings (Obs 286 + 287)

Obs 286 (Stage A verifier-T pilot, commit `f27842a5`) re-verified the same gold-standard 4-map
4-of-5 consensus candidate set (n = 607) at three verifier temperatures, using the canonical
`verify_adversarial-text` v1 verifier config and applying the Obs 281-corrected formula
`n_failures = len(consensus) − len(probabilities['results'])`.

| Verifier T | failures / 607 | failure rate | Wilson 95 % CI    |
|:----------:|:--------------:|:------------:|:------------------|
| 0.0        | 10             | **1.65 %**   | [0.90 %, 3.01 %]  |
| 0.5        | 0              | **0.00 %**   | [0.00 %, 0.63 %]  |
| 1.0        | 0              | **0.00 %**   | [0.00 %, 0.63 %]  |

Re-verified on disk in `results/verifier-t-pilot/per-t-stats.json` on 2026-04-30 — the table
above matches. T = 0.0 failures are deterministic (re-running at T = 0.0 reproduces the same
missing candidates), confirming the "deterministic dead-end" mechanism for T = 0.0.

Stage B (Obs 287, commits `b9f73bbf` + `74edfb16`) re-evaluated the T = 0.0 / 0.5 / 1.0 verifier
outputs at the canonical operating point (`vote_t = 4`, `prob_t = 0.15`, buffer = 20 m) and
confirmed F1 / MCC are not degraded by raising T:

| Verifier T | n_candidates | F1 (95 % CI)              | MCC (95 % CI)            |
|:----------:|:------------:|:-------------------------:|:------------------------:|
| 0.0        | 371          | 0.8536 [0.821, 0.882]     | 0.7781 [0.726, 0.828]    |
| 0.5        | 377          | **0.8645** [0.832, 0.892] | 0.7707 [0.719, 0.821]    |
| 1.0        | 376          | 0.8434 [0.808, 0.874]     | 0.7454 [0.689, 0.799]    |

Headline: **T = 0.5 dominates T = 1.0** on F1 and MCC; reliability gain over T = 0.0 (Stage A:
1.65 % → 0.00 %) plus marginal F1 improvement (+0.011 within CI) plus negligible MCC cost
(−0.007 within CI) plus operational simplification (no straggler-cleanup pass) constitute the
**adoption case for T = 0.5 as the production verifier default**. Recommendation only — no
config change has been applied as of 2026-04-30.

## 6. Recovery cost-effectiveness — observed numbers

Single-round recovery on the T = 0.3 generalisation run (commit `548604d9` on 2026-04-27):

| Stage                | Recovered | Cost     | Notes                                                       |
|:---------------------|:---------:|:--------:|:------------------------------------------------------------|
| Proposer (Phase 1)   | 18 / 18   | $0.031   | Resume mode of `4_detect_mounds_batch.py`; one stubborn tile (`K-35-051-3_x2016_y0.png`) recovered on retry attempt 12 in pass 5. |
| Re-consensus         | n/a       | $0       | 9,909 → 9,910 features; +1 new candidate from the recovered run_3 tile. |
| Crop extraction      | 1 new     | $0       | `scripts/55maps-t0.3-extract-new-candidates.py` (deterministic). |
| Verifier (Phase 4)   | 2 / 2     | $0.003   | `candidate_05396` (original gap) + `candidate_09909` (recovery). |
| **Total**            | **20 / 20** | **$0.034** | vs $1.10 inflated initial estimate from the 629-error misreading. |

Phase 5 re-evaluation post-recovery: F1@50m moved from 0.8023 → 0.8024 (negligible);
n_detections 4,349 → 4,350.

Operational implication: **plan recovery as a standard post-run step regardless of temperature;
do not budget heavily for it.** The unit cost is dominated by the per-call API rate, not by
recovery overhead.

## 7. Cross-references

- **Obs 281** (primary; Sessions 79–80; commits `4b4a87b3` for the T=0.3 run, `548604d9` for the
  recovery, `06f994d0` for the recovery scripts). Captures the proposer-side hypothesis test,
  the misreading, and the recovery cost summary.
- **Obs 286** (verifier-T pilot Stage A, commit `f27842a5`). Closes the verifier limb that Obs 281
  could not test (verifier T held at 0.0 in both 55-map runs). Finding: T = 0.0 has
  deterministic ~1.65 % verifier failures on the gold-standard corpus; T > 0 has 0.00 %.
- **Obs 287** (Stage B accuracy verdict, commits `b9f73bbf` + `74edfb16`). Closes the production-
  default gate Obs 286 set. Finding: F1 / MCC not degraded at T = 0.5; T = 0.5 dominates T = 1.0.
  Recommendation: adopt T = 0.5 as production verifier default.
- **Obs 297** (4-run paired-permutation grid; HIGH thinking earns its tokens at 55-map scope).
  Provides the production-context for the T=0.7 reference run used in Obs 281: T=0.7 HIGH beats
  T=MIN by +0.0296 F1 at R = 50 m (BH p < 0.001), confirming T=0.7 was the appropriate
  production-stable temperature on this corpus when Obs 281 ran. The choice of T = 0.7 (not
  T = 1.0) for production text-HIGH was already empirically justified before the temperature
  cross-run test.

## 8. Caveats

1. **Verifier-T held at 0.0 in both 55-map runs.** The T=0.3-vs-T=0.7 comparison can only test
   the proposer-temperature limb of the hypothesis. The verifier-side limb was untestable on
   the cross-run; Obs 286 closed it separately, on a different (4-map gold-standard) corpus.

2. **Wall-clock difference is server-side, not temperature-driven.** The T=0.3 proposer's
   per-pass wall clock was approximately 2× the T=0.7 reference run. Most plausibly explained by
   server-side capacity variation between 2026-04-18 and 2026-04-26 (8 days apart); the
   favourable failure-rate comparison for T=0.3 argues against a temperature-driven explanation.

3. **Magnitude error in Obs 281.** Section 4 documents the 25 → 160 unrecovered-failure
   correction for the T=0.7 row. Headline qualitative finding (T=0.3 < T=0.7 unrecovered) is
   unchanged; the rate-of-failure difference is ~9× rather than the implied ~1.4×. **Use the
   corrected numbers in any paper Methods citation.**

4. **Schema bugs surfaced by recovery (carry-over technical debt)**:
   - `4_detect_mounds_batch.py` resume mode overwrites per-pass `meta.json`, breaking
     `cost_manifest.json` aggregation. Worked around by `scripts/merge_recovery_meta.py`.
   - `run_generalisation.py aggregate-cost` rewrites `launch_manifest.json` and
     `experiment_intent.md` from current invocation, breaking original-launch provenance.
     Worked around by `git checkout` restore.
   - These are flagged in Obs 281 § "Findable later" and are pre-existing operational bugs
     beyond the scope of this synthesis.

5. **Single proposer cross-run.** The T=0.3-vs-T=0.7 comparison is N = 1 per condition.
   Resampling-based confidence intervals on the failure-rate difference are not meaningful at
   this design; the qualitative claim ("not supported") rests on the directional sign of the
   point estimates. A formal verifier-T comparison was conducted by Obs 286 with Wilson CIs (CIs
   do not overlap between T = 0.0 and T > 0); no equivalent statistical test was conducted on
   the proposer side.

## 9. Paper implications

For the paper Methods section's failure-rate paragraph:

1. **Cite both transient-error counts and post-pipeline residuals — and clearly distinguish
   them.** The transient/recovered/unrecovered three-state framing should be explicit. A typical
   wording: "After in-run retries, X / N items remained unrecovered (Y % residual failure rate);
   the runtime additionally observed Z transient errors that the retry layer recovered, but
   these are not failures of the final output."

2. **Use the canonical post-pipeline failure formula** (§ 2.3). The verifier formula
   (`len(consensus) − len(probabilities['results'])`) and the proposer formula
   (`sum(len(failed_items))` across passes, equivalently `cost_manifest.json::tiles_failed`) are
   the authoritative reads.

3. **Adopt the corrected T=0.7 figure** (160 / 42,705 = 0.375 % unrecovered) rather than the
   Obs 281 tabulated 25 / 42,545.

4. **The proposer hypothesis test result is a methodological footnote**, not a headline finding:
   "On the T=0.3 vs T=0.7 cross-run at 55-map scope (N = 1 per condition, 42,705 attempts each),
   T=0.3 had a lower unrecovered failure rate than T=0.7 (0.042 % vs 0.375 %), opposite to the
   prior 'distance from SDK default T=1.0' intuition."

5. **The verifier T = 0.5 production-default recommendation (Obs 287) is the operationally-
   actionable headline.** Cite Obs 286 + 287 in the verifier-temperature methods paragraph.

6. **Recovery is cheap and effective; document the unit cost.** $0.034 for 20 unrecovered items
   across both stages is roughly the cost of a single typical Gemini API call and should be
   budgeted as a standard post-run step.

## 10. Reproducibility

This is a **synthesis report; no new compute was performed.** All numerical claims trace back
to existing artefacts:

- **T=0.7 reference run**: `outputs/55maps-text-high-generalisation/`
  - `cost_manifest.json::by_stage.proposer.tiles_failed = 160` (re-verified 2026-04-30)
  - Per-pass meta files in `proposer/detect_brief-text/run_{1..5}/*.meta.json`
  - Launch metadata: `launch_manifest.json` shows `started_at: 2026-04-18T14:27:03Z`,
    `seed: 42`, `proposer.temperature: 0.7`
- **T=0.3 run + recovery**: `outputs/55maps-text-high-t0.3-generalisation/`
  - `cost_manifest.json::by_stage.proposer.tiles_failed = 0` (post-recovery; re-verified 2026-04-30)
  - `verified/run.meta.json` shows `finish_reason_counts.error: 629` (the misreading),
    `parse_failures: 629`, `empty_responses: 629`
  - `verified/probabilities.json` results count: 9,910 (re-verified 2026-04-30)
  - Launch metadata: `started_at: 2026-04-26T08:18:16Z`, `seed: 42`,
    `proposer.temperature: 0.3`
  - Run commit: `4b4a87b3`; recovery commit: `548604d9`; recovery scripts commit: `06f994d0`
- **Verifier-T pilot Stage A**: `results/verifier-t-pilot/per-t-stats.json`
  (re-verified 2026-04-30; commit `f27842a5`)
- **Verifier-T pilot Stage B**: `results/verifier-t-pilot/stage-b-report.md`
  + `stage-b-summary.json` (commits `b9f73bbf` + `74edfb16`)
- **Recovery scripts**: `scripts/55maps-t0.3-recovery.sh`,
  `scripts/55maps-t0.3-extract-new-candidates.py`,
  `scripts/55maps-t0.3-rebuild-verified-geojson.py`,
  `scripts/merge_recovery_meta.py`

All on-disk numbers were re-verified from source files on 2026-04-30 in preparation for this
report (per the project anti-confabulation protocol). The discrepancy with Obs 281's "25 /
42,545" T=0.7 cell is documented in § 4 and § 11.

Re-derivation commands (from repo root):

```bash
# T=0.7 unrecovered failure count (verified)
python3 -c "import json; d = json.load(open('outputs/55maps-text-high-generalisation/cost_manifest.json')); print(d['by_stage']['proposer']['tiles_failed'])"

# T=0.3 unrecovered failure count (post-recovery)
python3 -c "import json; d = json.load(open('outputs/55maps-text-high-t0.3-generalisation/cost_manifest.json')); print(d['by_stage']['proposer']['tiles_failed'])"

# Verifier-T pilot per-T failure rates
python3 -c "import json; print(json.dumps(json.load(open('results/verifier-t-pilot/per-t-stats.json')), indent=2))"
```

No random seed is relevant to this synthesis; the underlying runs used seed 42 (recorded in
`launch_manifest.json` for both 55-map runs).

## 11. Verified vs unverified claims in this report

To support the project anti-confabulation protocol, this section enumerates which numerical
claims were re-derived from source files on 2026-04-30 versus carried forward from Obs 281 / 286
/ 287 without re-verification.

**Verified on 2026-04-30 from source files:**

- T=0.7 proposer unrecovered failures: 160 / 42,705 (0.375 %) — re-derived from
  `outputs/55maps-text-high-generalisation/cost_manifest.json` and per-pass meta files.
- T=0.3 proposer post-recovery: 0 / 42,705 — re-derived from
  `outputs/55maps-text-high-t0.3-generalisation/cost_manifest.json`.
- T=0.3 verifier `finish_reason_counts.error: 629`, probabilities.json results count 9,910 —
  re-derived from `outputs/55maps-text-high-t0.3-generalisation/verified/`.
- Verifier-T pilot Stage A per-T failure counts (10 / 0 / 0 at T=0.0 / 0.5 / 1.0) — re-derived
  from `results/verifier-t-pilot/per-t-stats.json`.
- Run dates and seeds — re-derived from `launch_manifest.json` for both 55-map runs.
- Recovery commit `548604d9` text — re-derived via `git show 548604d9`.

**Carried forward from Obs 281 without independent re-derivation (file backups not present):**

- T=0.3 proposer pre-recovery unrecovered failures: 18 / 42,705 (0.042 %). The current
  `cost_manifest.json` shows 0 (post-recovery state); the pre-recovery 18 number relies on
  Obs 281's recording. Recovery commit `548604d9` independently states "18 tile-pass failures
  across runs 1-5 (5+2+4+5+2)" which matches Obs 281 — treat as cross-confirmed by two
  independent sources but not re-derived from raw meta files (which were overwritten by the
  recovery).
- T=0.3 verifier pre-recovery unrecovered: 1 (`candidate_05396`). Cross-confirmed by recovery
  commit message; not independently re-derived (the `probabilities.json` is post-recovery).
- T=0.7 verifier "9,131 candidates, 0 truly missing" (Obs 281 verifier table). Not independently
  re-verified for this synthesis; relies on Obs 281.
- T=0.7 reference F1@50m = 0.7883 raw; recovery $0.034 detail. Carried forward from Obs 281 and
  the recovery commit message; not independently re-derived.

**Flagged contradiction (per § 4):**

- Obs 281's tabulated T=0.7 row "25 / 42,545 = 0.059 %" does not match the on-disk file state
  re-derived on 2026-04-30 (160 / 42,705 = 0.375 %). The qualitative direction of the
  hypothesis-test verdict is unchanged (T=0.3 < T=0.7 in unrecovered rate), but the magnitude
  needs correction in any downstream citation. **User judgement requested**: confirm the
  correction before paper Methods citation.

## 12. Files in this directory

| File        | Contents                                  |
|:------------|:------------------------------------------|
| `report.md` | This document (the synthesis report)      |

No new computational artefacts were generated — this is a documentation-only synthesis.

---

**End of report.**
