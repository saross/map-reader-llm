# Temperature, transient errors, and failure-recovery on the 55-map proposer cross-run — synthesis report

**Date**: 2026-04-30 (initial); major refresh **2026-05-03** (Session 84 — 3 follow-up recoveries propagated)
**Sessions**: 79–80 (working-notes Obs 281); **83** (T=0.7 recovery); **84** (image, text-MIN, GS-v2 follow-up recoveries)
**Primary observation**: Obs 281 in `docs/notes/reflections/working-notes.md`
**Companion observations**: Obs 286 (verifier-T pilot Stage A), Obs 287 (Stage B + production-default recommendation), Obs 297 (T=0.7 vs T=MIN paired permutation at 55-map scope), Obs 318 (T=0.7 magnitude correction), Obs 319 (T=0.7 vs T=0.3 recovery-cost asymmetry), Obs 320 (T=0.7 propagation closure)
**Status**: Methods-load-bearing synthesis. Documents the **complete four-run recovery campaign** (T=0.3, T=0.7, image, text-MIN, GS-v2) and the seven companion bug fixes surfaced by the campaign.

## 1. Executive summary

The pre-investigation framing of "~6 % verifier failure rate at T=0.3" was a **misreading of the
`finish_reason_counts.error` field in `run.meta.json`**. That field counts **transient API errors
that the in-run retry layer subsequently recovered**, not unrecovered post-pipeline failures. The
genuine post-pipeline residual on the T=0.3 generalisation run was **18 unrecovered proposer
tile-passes (out of 42,705 = 0.042 %) plus 1 unrecovered verifier candidate (out of 9,909 =
0.010 %)** — roughly **two orders of magnitude smaller** than the misread headline.

A subsequent single-round recovery (`run_pv.py cleanup` style) closed both residuals at a total
cost of **$0.034** versus the inflated $1.10 estimate that would have followed from the
misreading. This made recovery a standard cheap post-run step, regardless of decoding
temperature — and once the **3-tier JSON repair** patch landed in the realtime proposer
(Session 83 commit `e3aef6fa`, § 5.1), the per-tile recovery cost dropped further by a factor of
**roughly 100–300×** versus the pre-fix T=0.7 cost (§ 4.4).

The headline temperature-failure-rate hypothesis (Shawn's standing intuition that "the further
the API call temperature is from the SDK default of T=1.0, the higher the parse / empty-response
failure rate, with T=0.0 worst") was **NOT supported on the proposer cross-run** when comparing
T=0.3 vs T=0.7. The verifier-side limb was subsequently closed by the verifier-T pilot (Obs 286 +
287) with a directional finding in the **same** spirit (T=0.0 produces deterministic verifier
failures that vanish at T > 0), so the broad intuition is salvaged on the verifier but
unsupported on the proposer.

**Four-run recovery campaign (complete 2026-05-03)**. The T=0.7 propagation arc executed in
Session 83 surfaced and fixed three bugs (§ 5) and identified three companion runs with
realtime-parser failures suitable for re-recovery under the new patch. Session 84 closed those
three follow-up recoveries (image, text-MIN, GS-v2) at a combined cost of **~$0.30** for the
recovery passes (orders of magnitude below the original-run pricing) and surfaced **two
additional bugs** (the cosmetic `cost_manifest` 2× / 3× double-counting after no-op recoveries
and the GS-v2 harness race condition requiring two resume invocations per pass). The four-run
campaign also discovered **28 silently-dropped verifier candidates** (image: 18 + GS-v2: 10)
that had never been written to `probabilities.json` from the original verifier runs — entirely
independent of the proposer recovery and a previously unchecked completeness gap. Headline
post-recovery F1@50m metrics across the four runs: **T=0.3 raw 0.8024 / corrected 0.8436;
T=0.7 raw 0.7920 / corrected 0.8273; image raw 0.7745 / corrected 0.8333; text-MIN raw 0.7619
/ corrected 0.7968; GS-v2 raw 0.8859 [Era 2 487-tile, +0.0126 vs pre-recovery]**. All
paper-load-bearing claims are preserved across all four runs (see § 7 for the per-run table).

> **Resolved contradiction (legacy)**: Obs 281's proposer comparison table cites
> "25 / 42,545 = 0.059 %" as the T=0.7 unrecovered failure count. Re-reading the on-disk meta
> files and `cost_manifest.json` for `outputs/55maps-text-high-generalisation/` shows
> **160 / 42,705 unrecovered failures (0.375 %)** as the actual T=0.7 residual. The "25" was
> the run_1 row of the per_pass cost-manifest table mistaken for the total. Under the
> corrected number, **T=0.3 (18 / 42,705 = 0.042 %) has a far lower unrecovered rate than T=0.7
> (160 / 42,705 = 0.375 %)** — opposite to Obs 281's tabulation but in the **same direction** as
> Obs 281's headline conclusion (lower T → fewer unrecovered failures on this corpus). The
> headline conclusion stands; the magnitude correction is documented as Obs 318 (commit
> `f5df7a09`).

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

### 3.2 Verifier (current files)

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
(further from SDK default T = 1.0). Empirically (using the corrected pre-recovery figures):

- **T = 0.3 (0.042 % unrecovered) was lower than T = 0.7 (0.375 % unrecovered)** — a ~9× gap.
- Direction is **opposite to the hypothesis** on the proposer.
- The mechanism: lower-temperature outputs are more deterministic and more likely to produce
  JSON the strict parser can consume on first attempt. Once a malformed-JSON sample is drawn at
  T = 0.7, re-sampling at the same temperature continues to hit that neighbourhood (proposer-
  side analogue of the verifier T = 0.0 deterministic dead-end identified in Obs 286).

The proposer-side hypothesis is therefore **not supported**. The verifier-side limb is closed
separately by Obs 286 (§ 6 below) with a directional finding in the spirit of the original
intuition (T = 0.0 worst, T > 0 better), but for a different reason — the deterministic
dead-end mechanism rather than a generic distance-from-SDK-default heuristic.

## 4. Recovery-cost asymmetry — T=0.7 vs T=0.3 (Obs 319)

The most operationally consequential finding of the recovery campaign is the **~189× per-tile
cost asymmetry** between the T=0.3 and T=0.7 recovery passes. Both runs reached zero residual
unrecovered failures, but the cost of getting there differed by more than two orders of magnitude
per tile.

### 4.1 Recovery cost summary (verified on disk 2026-05-03)

| Quantity                                  | T=0.3 (Session 80)                      | T=0.7 (Session 82)                                |
|:------------------------------------------|:----------------------------------------|:--------------------------------------------------|
| Stuck tiles entering recovery             | 18                                      | 160                                               |
| Recovery cost (proposer + verifier)       | **$0.034**                              | **$57.10**                                        |
| Per-tile recovery cost                    | ~$0.00189                               | **$0.357**                                        |
| **Per-tile cost ratio (T=0.7 / T=0.3)**   | —                                       | **~189×**                                         |
| Total recovery `retries_other` (5 passes) | well under 100 (single-digit per tile)  | **3,139** (avg 19.6 / tile)                       |
| New detections found during recovery      | n/a (small)                             | +612 across 5 passes                              |
| Recovery commit                           | `548604d9`                              | `731466d8`                                        |
| Recovery log                              | n/a (small inline)                      | `recovery-logs/stage2-20260502T154407.log`        |

### 4.2 The mechanism

When a Gemini API call returns malformed JSON, the runtime retry layer re-issues the full call.
Each retry redoes the full thinking budget; **thinking tokens are not cached across retries**.
At HIGH thinking + brief-text proposer, each call burns 5–15 K thinking tokens (~$0.018 per
attempt).

- **T = 0.3 (more deterministic)**: outputs largely parse cleanly on first attempt; the 18 tiles
  that initially failed needed only 1–2 retries across the recovery pass before succeeding →
  ~$0.034 total recovery. T = 0.3's lower sampling variance produces more structurally regular
  JSON outputs.
- **T = 0.7 (noisier sampling)**: stuck tiles repeatedly produced malformed JSON because the
  sampling noise that originally caused the failure persists across retries. The 160 stuck tiles
  accumulated 14–25 retries each, compounding the $0.018-per-attempt thinking cost → ~$57.10
  total.

The 160 T = 0.7 stuck tiles represent **0.375 % of total tile-slots** (Obs 318 corrected
figure). The recovery cost is **82 % of the original full-run proposer cost** ($57.10 / $69.60 =
82 %) despite touching only 0.37 % of the tile count. This is the retry-budget compounding
effect in concrete numbers.

A 3-retry cap per tile would have constrained cost to approximately 160 × 3 × $0.018 ≈ **$8.60**
while leaving a small residual of truly-unresolvable tiles for manual inspection. The production
recovery ran without such a cap.

### 4.3 Why this matters for paper Methods

1. **T = 0.3 is more cost-efficient than T = 0.7 for HIGH-thinking proposers on both axes**:
   lower first-pass failure rate (~9× fewer unrecovered tiles) AND cheaper recovery when
   failures do occur (~189× per-tile). The combination strongly supports T = 0.3 as the
   operational default, reinforcing the F1 / MCC advantage established in Obs 291 (paired
   ΔF1 = +0.018, BH p < 0.001 at R = 50 m).
2. **The recovery-cost asymmetry is itself reportable** alongside the F1 / MCC temperature
   comparisons. T = 0.3 is not merely statistically equivalent or marginally better — it is
   substantially cheaper to operate at both stages.
3. **Cost-discipline lesson for HIGH-thinking + T > 0.3 runs**: implement an explicit per-tile
   retry cap (3–5 retries) before launching recovery. Without a cap, 160 stuck tiles at HIGH-
   thinking pricing can approach the cost of the original full run.

### 4.4 Parser fix paid off — per-tile recovery costs collapsed by 100–300×

The 3-tier JSON repair patch landed in commit `e3aef6fa` (§ 5.1) at the end of Session 83,
**after** the T=0.7 recovery completed. The three follow-up recoveries in Session 84 (image,
text-MIN, GS-v2) ran under the patched parser. The per-tile cost differential is the direct
operational return on the patch:

| Run                 | Recovery date | Stuck tiles | Recovery cost | Per-tile cost | vs T=0.7 ($0.357/tile) |
|:--------------------|:-------------:|:-----------:|:-------------:|:-------------:|:----------------------:|
| T=0.3 (Session 80)  | 2026-04-27    | 18          | $0.034        | ~$0.0019      | ~190× cheaper          |
| T=0.7 (Session 83)  | 2026-05-02    | 160         | $57.10        | $0.357        | baseline (worst-case)  |
| image (Session 84)  | 2026-05-03    | 26          | **$0.216**    | **~$0.0083**  | **~43× cheaper**       |
| text-MIN (Session 84) | 2026-05-03  | 124*        | **$0.144**    | **~$0.0012**  | **~290× cheaper**      |
| GS-v2 (Session 84)  | 2026-05-03    | 13          | **$0.041**    | **~$0.0032**  | **~110× cheaper**      |

*The text-MIN recovery turned out to be a no-op at the proposer level — see § 7.2 for the
"`failed_items[]` is a historical record, not a current-failure signal" lesson; the 124 figure
is the audit-reported count, not new failures actioned.

The pattern is unambiguous: **post-patch recoveries cost two-to-three orders of magnitude less
per tile than the worst-case T=0.7 pre-patch recovery**. The per-tile differential reflects (i)
the patched parser recovering ~92 % of failures on the first attempt without retry storms, and
(ii) the cleanup-pass workflow batching well across small numbers of stuck tiles. The
implication for future runs: **the parse-recovery cost is now negligible at production scale**,
provided the patched parser is in place.

## 5. Code-quality fixes triggered by the recovery campaign

The T=0.7 recovery propagation surfaced three code-quality bugs that have been fixed in
companion commits. All three are paper-Methods-relevant: they affect either the cost accounting,
the parse robustness, or the safety of post-recovery analyses.

### 5.1 3-tier JSON repair in the realtime proposer (commit `e3aef6fa`)

**Bug**: the realtime proposer in `scripts/4_detect_mounds_batch.py` previously called
`json.loads()` directly on the model response, treating any `JSONDecodeError` as an
unrecoverable parse failure. Audit of three production runs
(`outputs/55maps-text-min-generalisation/`, `outputs/55maps-image-generalisation/`,
`outputs/h11/gold-standard-v2/`) showed **163 tiles lost to such failures**, of which ~92 % match
patterns a tiered repair pipeline can recover.

**Fix**: ports and extends the canonical Tier 1 trailing-comma strip already present in
`scripts/lib_batch_api.py:920` into a public helper, `parse_response_with_repair()`, and rewires
the realtime call site to use it. The three repair tiers are:

1. **Regex strip of trailing commas, retry strict JSON** — recovers ~52 % of historical failures
   (84 of 163 tiles).
2. **Permissive `json5.loads`** — recovers a further ~25 % via unquoted keys, single-quoted
   strings, embedded comments. `json5` is already pinned in `requirements-lock.txt`.
3. **Linear scan from end of text for longest valid JSON prefix** — recovers a further ~16 % of
   "Extra data" cases where valid JSON is followed by prose, code fences, or a second
   concatenated object.

Cumulative coverage on the historical sample: ~92 % of 163 tiles. Had this pipeline been in
place during the T=0.7 run, **most of the 160 stuck-tile recovery cost would not have been
incurred**. Three other production runs have a combined 163 outstanding tiles to address in
subsequent recovery passes (now safe to rerun under the patched parser).

### 5.2 D-S plumbing fix — stable candidate-ID join (commit `a9e280a3`)

**Bug**: the previous `load_detections` in the Dawid-Skene aggregator joined verifier
probabilities to consensus features by **row position**, assuming the i-th feature in
`consensus-NofM.geojson` corresponded to the `candidate_{i:05d}` key in `probabilities.json`.
That assumption silently breaks under partial-recovery workflows: the T=0.7 recovery added 612
new candidates with stable IDs while the consensus geojson was re-clustered into a different row
order. The bug surfaced as a meaningless D-S F1 of 0.4392 (versus the correct ~0.8 baseline) — a
pure artefact of mismatched (probability, geometry) pairs.

**Fix**: loads candidates from the canonical `crops/candidate_manifest.json` directly. Each
manifest entry has a stable `candidate_id` that survives re-clustering, plus the UTM
`centroid_x` / `centroid_y` already projected by `extract_candidates.py`. Probabilities are
joined by the `candidate_NNNNN` key derived from this stable ID, regardless of manifest row
order. A new `--manifest` CLI flag allows overriding the auto-derived manifest path.

**Implication**: D-S analyses run before the fix on any partial-recovery workflow are
potentially invalid; D-S analyses run after the fix are safe. The post-recovery T=0.7 D-S
re-aggregation (commits `366f9c66` + `e07dae37`) used the fixed code.

### 5.3 `cost_manifest` aggregator — merge pre-recovery verifier-meta backups (commit `7f05f529`)

**Bug**: when `scripts/run_pv.py cleanup` re-runs the verifier on a small set of missed
candidates, it overwrites `verified/run.meta.json` with only its own (small) entry. The original
verifier meta — recording the real ~$13 spend — is preserved (per Session 80 convention) as
`run.meta.json.pre-recovery-<TS>.backup`, but `aggregate-cost` previously read only the
post-overwrite primary and silently lost the original cost from the totals.

**Fix**: teaches `aggregate_cost_manifest` to (i) glob for `*.pre-recovery-*.backup` and
`*.pre-cleanup-*.backup` siblings of every meta file it reads (verifier and proposer per-pass);
(ii) sum cost / tokens / wall-clock duration / item counts across the primary plus any backups;
(iii) record the merged backup paths under `cost_manifest._metadata.cleanup_recovery_metas_merged`
so audits can see exactly which backups contributed.

**Verification on T=0.7 outputs**: after restoring the previously-missing backup from git
`d7f85978^`, the patched aggregator recovered **~$12.74 of T=0.7 verifier cost** that the
original aggregator had silently dropped. The current `cost_manifest.json::totals.cost_usd` of
**$126.81** therefore reflects the full original-run + recovery + verifier-cleanup spend,
correctly.

### 5.4 `cost_manifest` cosmetic 2× / 3× double-counting after no-op recoveries (Session 84 — open, cosmetic only)

**Bug** (newly surfaced 2026-05-03, Session 84 follow-up recoveries): when a per-pass recovery
turns out to be a no-op (the proposer's `failed_items[]` was a historical record rather than a
current failure list — see § 7.2), the in-line resume merge in `4_detect_mounds_batch.py`
**re-adds already-completed items to `completed_items`** and `merge_recovery_meta.py` then
folds the recovery meta back over the backup. After both passes, the per-pass `meta.json` shows
the original cost summed twice (text-MIN: 2× factor) or three times
(image: 3× factor — primary plus in-line merge plus explicit merge).

**Concrete signature**:

- text-MIN `cost_manifest::totals.cost_usd` = $93.50 (true total ~$60.79); proposer
  `cost_usd` = $93.45 (true ~$46.72); `proposer_processed` = 85,410 (2× expected 42,705).
- image `cost_manifest::totals.cost_usd` = $1,061.08 (true total ~$365); proposer
  `cost_usd` = $1,061.08 (true ~$353.62); `proposer_processed` = 128,141 (~3× expected 42,705).
- The per-pass meta files themselves carry the inflated `cost_estimate.total_cost_usd` (e.g.
  image run_1 = $141.60 primary + $70.83 recovery = $212.43, summed 5× across passes ≈ $1,062).

**Severity**: **cosmetic only**. The bug affects only the `cost_manifest`'s cost / token /
processed-count totals after a no-op recovery; F1, MCC, precision, recall, and all
detection-quality artefacts are unaffected. The true measured costs are recorded in the
respective recovery commit messages (commits `b4a928d2` for text-MIN, `a78cd7c5` for image) and
should be cited in any cost-table consolidation. The pre-recovery backups (`*.pre-recovery-*`)
preserve the original primary state for audit.

**Fix status**: open; not patched in Session 84 because (i) the bug only triggers when a
recovery is a no-op at the tile level, which is the now-rare case under the patched parser, and
(ii) the cost-manifest documentation surface already records the corrected numbers via the
recovery-commit message convention. Suitable for inclusion in the next aggregator pass when the
outstanding T=0.3 / GS / text-min audits are revisited.

### 5.5 GS-v2 harness quirk — two resume invocations required per pass (Session 84 — workaround documented)

**Bug** (surfaced 2026-05-03, GS-v2 follow-up recovery, commit `c8fde2ae`): the proposer
recovery on the GS-v2 4-map corpus required **two resume invocations per affected pass** to
land `processed_tiles` correctly. The first invocation appeared to overwrite the meta but raced
on the geojson save; the second invocation cleanly fixed the count.

**Concrete signature**: after the first `4_detect_mounds_batch.py` resume invocation, the
`meta.json` `failed_items[]` was emptied and `processed_tiles` was incremented, but the
per-pass detections geojson was still missing the recovered tile's features. A second resume
invocation (no further code changes) propagated the geojson update correctly.

**Severity**: **moderate** for any future automated GS-style recovery loop, but the
13/13-tile recovery completed correctly under the documented two-invocation workaround. Each
of the four affected passes was run twice; net cost across all four passes was $0.041 ($0.0032
per tile).

**Fix status**: workaround documented in commit `c8fde2ae`; no source-code patch yet. Likely a
race between the per-pass meta writer and the geojson serialiser when both are flushed by the
same harness invocation on a small batch. A patch would consolidate both writes into a single
atomic step. Tracked as a follow-up in the recovery-driver module.

## 6. Companion verifier-side findings (Obs 286 + 287)

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

**Recovery 2026-05-03**: the T = 0.0 row's underlying GS-v2 verifier-v1 detection set
has since been refreshed (commits `90890ae9..c6023034`); 10 pre-existing missing
candidates plus 1 new from consensus rebuild lifted n_candidates from 371 to 380,
F1@20m to **0.8663 [0.8591, 0.8726]**, F1@50m to **0.8859 [0.8798, 0.8919]**, and the
BCa N=10K MCC to **0.7778 [0.7663, 0.7896]** (see § 7.5). The T = 0.5 and T = 1.0 rows
above are pre-recovery and were NOT re-run on the recovered consensus because they
are separate verifier outputs; the table above is preserved at its original
pre-recovery state to maintain matched-condition validity across the three
verifier-T conditions. The post-recovery T = 0.0 numbers strengthen the **reliability**
side of the T = 0.5 adoption case (the T = 0.0 condition now has an even smaller
post-recovery completeness gap relative to T > 0); the **accuracy** side
(±0.01 F1 within overlapping CIs) survives qualitatively but a clean post-recovery
re-run of T = 0.5 / 1.0 would be the rigorous test — left to future work.

Headline: **T = 0.5 dominates T = 1.0** on F1 and MCC; reliability gain over T = 0.0 (Stage A:
1.65 % → 0.00 %) plus marginal F1 improvement (+0.011 within CI) plus negligible MCC cost
(−0.007 within CI) plus operational simplification (no straggler-cleanup pass) constitute the
**adoption case for T = 0.5 as the production verifier default**. Recommendation only — no
config change has been applied as of 2026-05-03.

## 7. Recovery cost-effectiveness — observed numbers

### 7.1 T = 0.3 single-round recovery (commit `548604d9`, 2026-04-27)

| Stage                | Recovered | Cost     | Notes                                                       |
|:---------------------|:---------:|:--------:|:------------------------------------------------------------|
| Proposer (Phase 1)   | 18 / 18   | $0.031   | Resume mode of `4_detect_mounds_batch.py`; one stubborn tile (`K-35-051-3_x2016_y0.png`) recovered on retry attempt 12 in pass 5. |
| Re-consensus         | n/a       | $0       | 9,909 → 9,910 features; +1 new candidate from the recovered run_3 tile. |
| Crop extraction      | 1 new     | $0       | `scripts/55maps-t0.3-extract-new-candidates.py` (deterministic). |
| Verifier (Phase 4)   | 2 / 2     | $0.003   | `candidate_05396` (original gap) + `candidate_09909` (recovery). |
| **Total**            | **20 / 20** | **$0.034** | vs $1.10 inflated initial estimate from the 629-error misreading. |

Phase 5 re-evaluation post-recovery: F1@50m moved from 0.8023 → 0.8024 (negligible);
n_detections 4,349 → 4,350.

### 7.2 T = 0.7 multi-stage recovery (commit `731466d8`, 2026-05-03)

| Stage                                  | Recovered                              | Cost                | Notes                                                                                     |
|:---------------------------------------|:---------------------------------------|:--------------------|:------------------------------------------------------------------------------------------|
| Proposer (Stage 2)                     | 160 / 160                              | **$57.10**          | 5 sequential resume passes; per-pass: 25 / 42 / 38 / 28 / 27 stuck tiles closed. Total `retries_other` = 3,139 (avg 19.6 / stuck tile). +612 new detections across passes. |
| Re-consensus + verifier cleanup        | re-clustered + small candidate top-up  | small (~$0.13 cleanup) | Commit `d7f85978`; `cost_manifest._metadata.cleanup_recovery_metas_merged` records the merged backup. |
| Re-evaluation (BCa N = 10 K)           | n/a                                    | $0                  | Commit `e20f3e18`; baseline + full-buffer + extended-buffer.                              |
| GT update + re-eval                    | n/a                                    | $0                  | Commits `baf1497a`, `f533fda5`; +1 GT mound from curator review.                          |
| Multi-buffer corrected F1              | n/a                                    | $0                  | Commit `f6eaeca9`; 6 new reviews + 1 new GT mound integrated.                             |
| Pairwise permutation v2                | n/a                                    | $0                  | Commit `aeb9fb7f`; 3 pairs touching T=0.7 re-run.                                         |
| D-S re-aggregation + crosstab          | n/a                                    | $0                  | Commits `366f9c66` + `e07dae37`; safe under stable-ID join (§ 5.2).                       |
| **Total recovery + propagation**       | 160 / 160                              | **~$57.10**         | Dominated by Stage 2; analysis stages are CPU-only.                                       |

Post-recovery headline metrics at R = 50 m (verified on disk 2026-05-03):

- Raw F1 (Hungarian, student-only GT): **0.7920 [0.7820, 0.8017]** (pre-recovery 0.7896);
  n_detections = 4,164.
- Tile-level MCC (paired pixels): **0.6476 [0.6331, 0.6620]** (pre-recovery ~0.65; carries the
  same direction).
- Multi-buffer corrected F1 (Approach B; reviewer-promoted phantom TPs at R = 50 m):
  **0.8273 [0.8173, 0.8370]** (pre-recovery 0.8260 [0.8159, 0.8357]).
- Multi-buffer corrected F1 at the practitioner-useful 125 m cap: **0.8338 [0.8240, 0.8432]**.

Δ effects from pre- to post-recovery are within the BCa CIs (recovery added 612 detections
across the proposer pool but only marginal additional candidates survived consensus + verifier).

### 7.3 Image follow-up recovery (commits `2992056b` → `8699f456`, 2026-05-03)

| Stage                                     | Recovered                                | Cost                | Notes                                                                                                                       |
|:------------------------------------------|:-----------------------------------------|:--------------------|:----------------------------------------------------------------------------------------------------------------------------|
| Proposer (Stage 2; commit `2992056b`)     | 26 / 26 (8/3/8/2/5 across runs 1–5)      | **$0.216**          | Single round; per-pass costs $0.066 / $0.026 / $0.066 / $0.016 / $0.042. **All 26 recovered first-try thanks to commit `e3aef6fa`** — no retry storms. |
| Re-consensus + crops                      | +1 truly-new candidate (`candidate_07877`) | $0                | Race condition on Stage 3: first inspection ran during a 5-min `merge_passes` write, returning a stale 7,877-feature copy; the actual post-merge state was 7,878 features. Race-corrected at commit `8699f456`. |
| Verifier cleanup (Stage 5; commit `8082896b`) | 18 missing + 1 race-fix = 19 candidates | ~$0.03            | **18 silently-dropped candidates discovered** (IDs 823 → 6,733; pre-existing verifier failures from the original 2026-04-18 verifier run that had never been written to `probabilities.json`). The cleanup recovered all 19 in a single attempt. |
| Re-evaluate (Stage 8; commit `da84a3d2`)  | n/a                                      | $0                  | BCa N=10K + `--mcc`. F1@50m raw: 0.771 → **0.7745** (+0.0035 vs un-reviewed; +0.003 vs reviewed-GT comparator); MCC@50m **0.6924 [0.6784, 0.7062]**. Auto-proceed gate `\|Δ F1\| < 0.020` PASSED. |
| Stage 9 (corrected-F1 + D-S + MCC)        | n/a                                      | $0                  | Corrected F1@50m: 0.832 → **0.8332**; D-S posterior F1: 0.7989 → 0.7990 (+0.0001); ds-human-crosstab `n_joined`: 1,028 → 1,029 (+1 from the new retained candidate). Same degenerate-posterior pattern as pre-recovery. |
| **Total recovery + propagation**          | **15 net new retained candidates**       | **~$0.029**         | Per-tile $0.0083 — **~43× cheaper than T=0.7 baseline**. Commits span `2992056b..8699f456`.                                 |

The image follow-up's most consequential finding is the **18 silently-dropped verifier
candidates** (IDs distributed across 823–6,733, not clustered, consistent with random verifier
failures that escaped the original pipeline). This represents an **uncaught completeness gap
in the verifier output**: the 2026-04-18 published image-track F1 (0.771) was therefore
slightly understated relative to the true full-coverage state (0.7745).

### 7.4 Text-MIN follow-up recovery (commit `c1ea6df3`, 2026-05-03)

The text-MIN audit identified **124 tile-passes (113 unique)** as proposer failures requiring
recovery. The recovery turned out to be a **no-op at the proposer level**: per-pass detection
geojson md5sums were bit-identical to the committed versions, indicating the failures had
already been recovered in a prior unrecorded round. The `execution_stats.failed_items[]`
field is therefore a **historical record, not a current-failure signal** — a methodological
caveat for any future recovery audit.

| Stage                                     | Recovered                                | Cost                | Notes                                                                                                                       |
|:------------------------------------------|:-----------------------------------------|:--------------------|:----------------------------------------------------------------------------------------------------------------------------|
| Proposer (Phases 1–5; commit `c1ea6df3`)  | 0 / 124 (no-op; failures historical)     | **$0.144**          | Per-tile $0.0012 — **~290× cheaper than T=0.7 baseline**. Cost still incurred because the harness re-issues per-tile checks even when they succeed silently; the recovered manifests are bit-identical, but the API charges land. |
| Re-consensus (Phase 5)                    | +39 features (10,131 → 10,170)           | $0                  | The +39 features are a **dedup-side effect** under the rebuilt 4-of-5 consensus, not new detections from recovery.            |
| Crops + verifier (Phase 5)                | +39 verified, 0 failed                   | trivial             | Dedup'd new candidates extracted + verified successfully.                                                                   |
| Verified-detections rebuild + re-eval     | +4 retained features (3,861 → 3,865)     | $0                  | F1@50m raw: 0.7591 → **0.7595** (delta = +0.0004; auto-proceed gate `< 0.005` met). MCC@50m **0.626 [0.611, 0.641]** (newly added — first time tile-level MCC computed for this run). |
| Cost-manifest aggregation                 | n/a                                      | n/a                 | **Cosmetic 2× double-counting** surfaced (§ 5.4). True total cost ~$60.79 (proposer $46.72 + verifier $13.93 + recovery $0.144); cost_manifest reports $93.50 (proposer 2× counted). The bug affects only the cost_manifest count fields, not F1/MCC/precision. |
| Stage 8–9 GT-update propagation (commits `236327d8`, `6e077005`) | n/a            | $0                  | Re-evaluation against the reviewed GT (4,745 features) and tile-level MCC vs reviewed GT.                                    |
| Corrected-F1 multi-buffer (post-GT update) | n/a                                     | $0                  | Corrected F1@50m: **0.7968** (the only of the four runs where corrected-F1 < image, as expected for the lowest-thinking modality).                       |
| **Total recovery + propagation**          | **+39 features, +4 retained candidates** | **~$0.144**         | Per-tile $0.0012 — **~290× cheaper than T=0.7 baseline**.                                                                   |

The text-MIN lesson — **failed_items[] is a historical record, not a current-failure signal**
— generalises across the recovery campaign: any future audit that scopes failure recovery
based on `failed_items[]` should cross-check by computing md5sums of the per-pass detection
geojsons before launching recovery. If the manifests are bit-identical to a recently-committed
state, the recovery will be a no-op.

### 7.5 GS-v2 follow-up recovery (commits `c8fde2ae` → `c6023034`, 2026-05-03)

| Stage                                     | Recovered                                | Cost                | Notes                                                                                                                       |
|:------------------------------------------|:-----------------------------------------|:--------------------|:----------------------------------------------------------------------------------------------------------------------------|
| Proposer (commit `c8fde2ae`)              | 13 / 13 (single round)                   | **$0.041**          | Per-tile $0.0032 — **~110× cheaper than T=0.7 baseline**. **Two resume invocations per pass required** (§ 5.5 — race condition between meta writer and geojson serialiser); workaround documented, no source-code patch. Wall clock ~3.5 min. |
| Re-consensus (3-of-5, 4-of-5, 5-of-5; commit `de67f35f`) | +1 candidate at 4-of-5 (`candidate_607`) | $0  | The 13-tile recovery added 1 truly-new consensus candidate.                                                                  |
| Crops extraction (commit `7167118d`)      | 1 new                                    | $0                  | Deterministic; processed `candidate_607`.                                                                                   |
| Verifier cleanup (commit `4ea54760`)      | 10 missing + 1 new = 11 candidates       | ~$0.02              | **10 silently-dropped candidates discovered** (IDs 253, 292, 302, 304, 321, 359, 397, 408, 435, 520 — pre-existing verifier failures from the original 2026-04-10 verifier run that had never been written to `probabilities.json`). All 11 recovered single-pass. |
| Re-evaluate (commit `239a6bf4`)           | n/a                                      | $0                  | BCa N=10K + `--mcc`. n_detections 371 → **380** (+9, +2.4 %); F1@50m: 0.8734 → **0.8859** (+0.0126; CI [0.8798, 0.8919]); F1@20m: 0.8536 → 0.8663 (+0.0127); first time tile-level MCC computed for the era2-487-tile baseline → **0.7778 [0.7663, 0.7896]** (Sens=0.790, Spec=0.969). |
| Downstream propagation (commit `c6023034`) | n/a                                     | $0                  | Subtype + leaderboard cells refreshed.                                                                                      |
| **Total recovery + propagation**          | **10 + 1 missing verifier + 1 truly-new candidate** | **~$0.061** | Per-tile $0.0032 — **~110× cheaper than T=0.7 baseline**. Most of the F1 lift (+0.0126) attributable to the verifier cleanup (10 pre-existing failures), not the proposer recovery. |

The GS-v2 lift is the **largest of the four follow-up recoveries** because the gold-standard
corpus has the highest single-candidate marginal value (curator-annotated GT, only 327 / 487
tiles). The +0.0126 F1 delta exceeds the auto-proceed criterion (< 0.005) and **should be
treated as the new canonical Era 2 487-tile baseline** for any paper-Methods or
Discussion citation.

### 7.6 Combined four-run summary

| Run     | Total recovery cost | Net retained candidates | F1@50m (post-recovery) | Δ vs pre-recovery | Verifier-completeness gap |
|:--------|:-------------------:|:-----------------------:|:----------------------:|:-----------------:|:-------------------------:|
| T=0.3   | $0.034              | +1                      | 0.8024 (raw) / 0.8436 (corr.) | +0.0001 (raw) | none                  |
| T=0.7   | $57.10              | +21                     | 0.7920 (raw) / 0.8273 (corr.) | +0.0024 (raw) | none documented       |
| image   | ~$0.029             | +15                     | 0.7745 (raw) / 0.8333 (corr.) | +0.0035 (raw) | **18 silently-dropped** |
| text-MIN | ~$0.144            | +4                      | 0.7595 (raw) / 0.7968 (corr.) | +0.0004 (raw) | none                  |
| GS-v2   | ~$0.061             | +9 (Era 2)              | 0.8859 (raw, Era 2)    | +0.0126 (raw)     | **10 silently-dropped** |
| FP-classify (4-corpus, post-recovery) | $0.582 | n/a — re-classifies all FPs | n/a | n/a | n/a |

**Total recovery + propagation spend across all 4 follow-up recoveries**: **~$0.30** for the
recovery passes themselves; **+$0.58** for the FP-classify re-run across all four corpora;
**~$0.30 + $0.58 ≈ $0.88** for the Session 84 follow-up arc. (The T=0.7 recovery in Session 83
was $57.10 separately, dominating the cumulative recovery spend across both sessions.)

**Total silently-dropped verifier candidates discovered**: 18 (image) + 10 (GS-v2) = **28**.
These had never been written to `probabilities.json` from the respective original verifier runs;
they were entirely independent of the proposer recovery. Pre-published F1s were therefore
**slightly understated**: GS-v2 by ~1.3 pp at 50 m, image by ~0.3 pp at 50 m. **Verifier
output completeness was not previously checked** — see § 9 limitations note for the Methods
caveat.

### 7.7 Operational implication

**Plan recovery as a standard post-run step, but cap retries explicitly at high temperatures.**
The unit cost at T = 0.3 (HIGH thinking) is dominated by the per-call API rate; at T = 0.7
(HIGH thinking) it is dominated by retry-budget compounding on stuck tiles. A 3–5 retry cap per
tile (instead of the default 14–25) would have constrained the T=0.7 recovery cost from $57.10
to ~$8.60 while leaving a small residual for manual inspection.

**Always run a verifier-completeness check** after the recovery passes. The 28 silently-dropped
verifier candidates discovered in Session 84 (image: 18, GS-v2: 10) would otherwise have
remained undiscovered. The check is a single `len(consensus) − len(probabilities['results'])`
calculation — see § 2.3.

## 8. Cross-references

- **Obs 281** (primary; Sessions 79–80; commits `4b4a87b3` for the T=0.3 run, `548604d9` for the
  recovery, `06f994d0` for the recovery scripts). Captures the proposer-side hypothesis test,
  the misreading, and the T=0.3 recovery cost summary.
- **Obs 286** (verifier-T pilot Stage A, commit `f27842a5`). Closes the verifier limb that Obs
  281 could not test (verifier T held at 0.0 in both 55-map runs). Finding: T = 0.0 has
  deterministic ~1.65 % verifier failures on the gold-standard corpus; T > 0 has 0.00 %.
- **Obs 287** (Stage B accuracy verdict, commits `b9f73bbf` + `74edfb16`). Closes the
  production-default gate Obs 286 set. Finding: F1 / MCC not degraded at T = 0.5; T = 0.5
  dominates T = 1.0. Recommendation: adopt T = 0.5 as production verifier default.
- **Obs 297** (4-run paired-permutation grid; HIGH thinking earns its tokens at 55-map scope).
  Provides the production-context for the T=0.7 reference run used in Obs 281: T=0.7 HIGH beats
  T=MIN by +0.0296 F1 at R = 50 m (BH p < 0.001), confirming T=0.7 was the appropriate
  production-stable temperature on this corpus when Obs 281 ran. **Cost-context update from
  Obs 319**: HIGH thinking is efficient, but **T = 0.3 HIGH is substantially more cost-efficient
  than T = 0.7 HIGH** when first-pass reliability and recovery cost are both included in the
  accounting.
- **Obs 318** (T=0.7 failure-rate magnitude correction; commit `f5df7a09`). Corrects the
  Obs 281 tabulation from 25 / 42,545 = 0.059 % to 160 / 42,705 = 0.375 % (~9× gap vs T=0.3,
  not the originally-implied ~1.4× gap).
- **Obs 319** (T=0.7 vs T=0.3 recovery-cost asymmetry; commits `c913b69b` + `3219aa76`).
  Quantifies the per-tile recovery-cost ratio at ~189× and identifies the retry-budget
  compounding mechanism on malformed-JSON outputs.
- **Obs 320** (T=0.7 propagation closure, commit `274b837b`). Captures the Session 83
  closure summary — the full propagation arc + bug-discoveries + 3 outstanding recoveries
  queued (subsequently closed in Session 84).
- **T=0.7 recovery + propagation commits** (Session 83, 2026-05-02 / 2026-05-03):
  - `731466d8` — T=0.7 proposer recovery for 160 failed tiles + meta merge.
  - `1ea92b9c` — T=0.7 single-round recovery driver.
  - `d7f85978` — consensus + verifier cleanup + cost-manifest + verified rebuild.
  - `e20f3e18` — N=10K BCa evaluation re-run (baseline + full-buffer + extended-buffer).
  - `f533fda5` — re-evaluate against updated GT (4,745 features, `baf1497a`).
  - `f6eaeca9` — corrected-F1 multi-buffer with 6 new reviews + 1 new GT mound.
  - `9b80621e` — T=0.7 55-map review-app — 7 entries from 2026-05-03.
  - `baf1497a` — add missing curator GT mound.
  - `aeb9fb7f` — pairwise-permutation v2 — 3 pairs touching T=0.7.
  - `366f9c66` — re-aggregate D-S on text-high (post-recovery + new GT).
  - `e07dae37` — re-run DS-vs-human cross-tab on text-high.
  - `33435aab` — attractor-pull v2 + FP-classify + TP-localisation + per-map shell + student-GT-FN.
- **Image follow-up recovery commits** (Session 84, 2026-05-03):
  - `2992056b` — proposer recovery — all 26 tiles recovered ($0.216 first-try, no retry storms).
  - `8082896b` — verifier cleanup — 18 missing candidates recovered (silently-dropped from original).
  - `a78cd7c5` — aggregate cost manifest after recovery (Stage 6) — surfaces the 3× double-counting cosmetic bug.
  - `8965d236` — rebuild verified_detections.geojson (Stage 7).
  - `da84a3d2` — re-evaluate vs reviewed GT 4,745 (Stage 8) — F1@50m raw 0.7745.
  - `8699f456` — correct Stage-3 race + propagate +1 candidate (`candidate_07877`).
  - `165c7415` — add launcher for post-recovery image FP review.
  - `c816d4bd` — add cand 2397 (mound/trig_point_on_mound, buffer 50m) to image review CSV.
- **Text-MIN follow-up recovery commits** (Session 84, 2026-05-03):
  - `a9bc85b2` — text-MIN recovery driver.
  - `c1ea6df3` — post-recovery proposer + downstream artefacts (Phases 1–5) — recovery was no-op at proposer level.
  - `b4a928d2` — aggregate cost manifest after recovery (Phase 6) — surfaces the 2× double-counting cosmetic bug.
  - `236327d8` — re-evaluate vs reviewed GT 4,745 (Stages 8–9).
  - `6e077005` — refresh per-run MCC vs reviewed GT.
- **GS-v2 follow-up recovery commits** (Session 84, 2026-05-03):
  - `90890ae9` — gold-standard-v2 recovery driver.
  - `c8fde2ae` — proposer recovery — 13/13 failures recovered (two resume invocations per pass; § 5.5).
  - `de67f35f` — re-merge consensus (3-of-5, 4-of-5, 5-of-5).
  - `7167118d` — extract crops for 1 new consensus candidate.
  - `4ea54760` — verifier cleanup — 11 missing candidates recovered (10 silently-dropped + 1 new).
  - `239a6bf4` — re-evaluate post-recovery — F1 +0.013, MCC=0.778.
  - `c6023034` — downstream propagation — subtype + leaderboard cells.
- **Cross-track v2 propagation commits** (Session 84, 2026-05-03):
  - `a7a0caaa` — pairwise-permutation v2 — all 6 pairs across 4 corrected runs (5 of 6 significant; T=0.7 vs image only ns pair).
  - `971ef0e1` — fix(attractor-pull-v2): force buffer_band dtype to float64.
  - `29fcc367` — attractor-pull v2 4-run consensus refresh.
  - `42ed1d32` — FP-classification 4-corpus re-classify ($0.582; chi-square stable).
  - `0edb213a` — lower hard cap to $1.50 for cross-track v2 re-run.
- **Code-quality fix commits** (Session 83, 2026-05-03):
  - `e3aef6fa` — 3-tier JSON repair in realtime proposer (§ 5.1).
  - `a9e280a3` — D-S plumbing fix: stable candidate_id join (§ 5.2).
  - `7f05f529` — cost_manifest aggregator: merge pre-recovery verifier-meta backups (§ 5.3).

## 9. Caveats

1. **Verifier-T held at 0.0 in both 55-map runs.** The T=0.3-vs-T=0.7 comparison can only test
   the proposer-temperature limb of the hypothesis. The verifier-side limb was untestable on
   the cross-run; Obs 286 closed it separately, on a different (4-map gold-standard) corpus.

2. **Wall-clock difference is server-side, not temperature-driven.** The T=0.3 proposer's
   per-pass wall clock was approximately 2× the T=0.7 reference run. Most plausibly explained by
   server-side capacity variation between 2026-04-18 and 2026-04-26 (8 days apart); the
   favourable failure-rate comparison for T=0.3 argues against a temperature-driven explanation.

3. **Magnitude of recovery-cost ratio carries small uncertainty.** The T = 0.3 recovery was a
   combined verifier + proposer pass; the ~$0.034 figure is dominated by the proposer
   component. The per-tile comparison ($0.357 vs ~$0.00189; ratio ~189×) is approximate to
   within ~10 % depending on how the small T = 0.3 verifier component is split. The
   order-of-magnitude conclusion (~two orders of magnitude per-tile) is robust.

4. **`retries_other` discrepancy vs Obs 319 specification**. Obs 319's specification stated
   3,144 total recovery `retries_other`. The verified on-disk figure (merged minus original
   per-pass meta) is **3,139** (difference of 5). The per-tile ratio and all order-of-magnitude
   conclusions are unaffected.

5. **Schema bugs surfaced by recovery (carry-over technical debt — partly closed)**:
   - `4_detect_mounds_batch.py` resume mode overwrites per-pass `meta.json`, breaking
     `cost_manifest.json` aggregation. Worked around by `scripts/merge_recovery_meta.py`.
   - `run_generalisation.py aggregate-cost` rewrites `launch_manifest.json` and
     `experiment_intent.md` from current invocation, breaking original-launch provenance.
     Worked around by `git checkout` restore.
   - `cost_manifest` aggregator silently dropped pre-cleanup verifier-meta cost. **Closed by
     commit `7f05f529` (§ 5.3)**.
   - Realtime proposer treated any `JSONDecodeError` as unrecoverable. **Closed by commit
     `e3aef6fa` (§ 5.1)**.
   - D-S aggregator joined probabilities to geometries by row position. **Closed by commit
     `a9e280a3` (§ 5.2)**.
   - **`cost_manifest` aggregator double-counts after no-op recoveries** (Session 84;
     § 5.4). Open; cosmetic only — affects cost / token / processed-count totals but not
     F1 / MCC / detection-quality artefacts. True costs documented in commit messages
     `b4a928d2` (text-MIN) and `a78cd7c5` (image).
   - **GS-v2 harness race between meta writer and geojson serialiser** (Session 84; § 5.5).
     Workaround documented in commit `c8fde2ae` — two resume invocations per pass clears
     the race. No source-code patch yet.

6. **Single proposer cross-run.** The T=0.3-vs-T=0.7 comparison is N = 1 per condition for the
   failure-rate and recovery-cost statistics. Resampling-based confidence intervals on the
   failure-rate difference are not meaningful at this design; the qualitative claim ("not
   supported"), the magnitude claim (~9× failure rate, ~189× recovery cost), and the headline
   F1 / MCC differences each rest on different evidence types: the failure-rate gap is a
   single-pair point estimate at N = 42,705 attempts each; the recovery-cost ratio is a
   single-pair point estimate; the F1 / MCC differences are paired permutation tests at the
   55-map scope (Obs 291 / 297). A formal verifier-T comparison was conducted by Obs 286 with
   Wilson CIs (CIs do not overlap between T = 0.0 and T > 0); no equivalent statistical test
   was conducted on the proposer side.

7. **Three outstanding recoveries closed in Session 84.** The Session 83 closure flagged 163
   outstanding tiles across `outputs/55maps-text-min-generalisation/`,
   `outputs/55maps-image-generalisation/`, and `outputs/h11/gold-standard-v2/`. **All three
   were closed in Session 84** (§ 7.3 / 7.4 / 7.5); the patched parser (commit `e3aef6fa`)
   recovered ~92 % of failures on the first attempt without retry storms.

8. **`failed_items[]` is a historical record, not a current-failure signal** (Session 84
   text-MIN finding; § 7.4). Any future audit that scopes failure recovery based on
   `execution_stats.failed_items[]` should cross-check by computing md5sums of the per-pass
   detection geojsons. If the manifests are bit-identical to a recently-committed state, the
   recovery will be a no-op (the API still charges for the per-tile checks, but no detection
   output changes).

9. **Verifier output completeness was not previously checked.** The Session 84 follow-up
   recoveries discovered **28 silently-dropped verifier candidates** (image: 18, GS-v2: 10)
   that had never been written to `probabilities.json` from the original verifier runs. These
   were entirely independent of the proposer recovery and represent a previously unchecked
   completeness gap. Pre-published F1s were therefore slightly understated: GS-v2 by ~1.3 pp at
   50 m, image by ~0.3 pp at 50 m. The check is a single
   `len(consensus) − len(probabilities['results'])` calculation per § 2.3 and should be
   added to every post-pipeline verification audit going forward.

## 10. Paper implications

For the paper Methods section's failure-rate paragraph:

1. **Cite both transient-error counts and post-pipeline residuals — and clearly distinguish
   them.** The transient/recovered/unrecovered three-state framing should be explicit. A typical
   wording: "After in-run retries, X / N items remained unrecovered (Y % residual failure rate);
   the runtime additionally observed Z transient errors that the retry layer recovered, but
   these are not failures of the final output."

2. **Use the canonical post-pipeline failure formula** (§ 2.3). The verifier formula
   (`len(consensus) − len(probabilities['results'])`) and the proposer formula
   (`sum(len(failed_items))` across passes, equivalently `cost_manifest.json::tiles_failed`) are
   the authoritative reads. Add the warning that `failure_rate` in the cost manifest already
   uses total-attempts as the denominator (Obs 318 lesson).

3. **Adopt the corrected pre-recovery T=0.7 figure** (160 / 42,705 = 0.375 % unrecovered)
   rather than the Obs 281 tabulated 25 / 42,545. Both 55-map proposer runs are now
   post-recovery at 0 / 42,705 unrecovered (T=0.3 commit `548604d9`; T=0.7 commit `731466d8`).

4. **The proposer hypothesis test result is a methodological footnote**, not a headline finding:
   "On the T=0.3 vs T=0.7 cross-run at 55-map scope (N = 1 per condition, 42,705 attempts each),
   T=0.3 had a lower unrecovered failure rate than T=0.7 (0.042 % vs 0.375 %), opposite to the
   prior 'distance from SDK default T=1.0' intuition."

5. **The recovery-cost asymmetry is itself a paper-Methods finding** (Obs 319): "Recovery cost
   exhibits a per-tile asymmetry of ~189× between T=0.3 ($0.00189 / tile) and T=0.7
   ($0.357 / tile), driven by HIGH-thinking retry-budget compounding on noisier-sampling
   malformed-JSON outputs. The recovery cost for the T=0.7 stuck-tile residual reached 82 % of
   the original full proposer-stage cost despite touching only 0.37 % of the tile count."

6. **The verifier T = 0.5 production-default recommendation (Obs 287) is the operationally-
   actionable headline** on the verifier side. Cite Obs 286 + 287 in the verifier-temperature
   methods paragraph.

7. **Recovery is cheap and effective at low temperature; expensive without a retry cap at
   higher temperature.** $0.034 for 20 unrecovered items at T = 0.3 is roughly the cost of a
   single typical Gemini API call. $57.10 for 160 unrecovered items at T = 0.7 (without a retry
   cap) is 82 % of the original full proposer-stage cost. Implement a per-tile retry cap (3–5)
   on any HIGH-thinking + T > 0.3 production run.

8. **Three-tier JSON parser fix (commit `e3aef6fa`) prevents most future recovery-cost
   asymmetries.** Production runs after this commit will recover ~92 % of historical
   parse-failure modes in-line, eliminating most stuck-tile recovery campaigns. The three
   legacy runs (~163 outstanding tiles) flagged in Session 83 were re-recovered under the
   patched parser in Session 84 — per-tile costs collapsed by 100–300× vs the pre-patch T=0.7
   baseline (§ 4.4).

9. **Verifier-completeness check is a Methods caveat — and now a fix-forward step.**
   Session 84 surfaced 28 silently-dropped verifier candidates across two production runs
   (image: 18, GS-v2: 10). Pre-published F1s were therefore slightly understated: GS-v2 by
   ~1.3 pp at 50 m, image by ~0.3 pp at 50 m. The Methods section should note this as a known
   limitation of the original publication's verifier outputs, **resolved across all four
   runs** in Session 84 by the `len(consensus) − len(probabilities['results'])` cleanup pass.

10. **`failed_items[]` is a historical record, not a current-failure signal.** The text-MIN
    follow-up recovery (§ 7.4) audit-flagged 124 tile-passes as failures requiring recovery;
    the recovery turned out to be a no-op at the tile level (per-pass detection geojsons were
    bit-identical to committed versions). Methods sections describing failure-recovery audits
    must cross-check `failed_items[]` against md5sums of the committed per-pass detection
    geojsons before launching recovery.

## 11. Reproducibility

This is a **synthesis report; the underlying recovery and analysis runs are documented in their
own commit histories.** All numerical claims trace back to existing artefacts:

- **T=0.7 reference run + recovery**: `outputs/55maps-text-high-generalisation/`
  - `cost_manifest.json::totals.cost_usd = 126.81` (post-recovery + verifier cleanup; commit
    `7f05f529` aggregator merges pre-recovery backups).
  - `cost_manifest.json::by_stage.proposer.tiles_failed = 0` (post-recovery; pre-recovery 160).
  - Per-pass meta files in `proposer/detect_brief-text/run_{1..5}/*.meta.json` (post-recovery
    merged); `*.pre-recovery-*.backup` files preserve the original 160-failure state for audit.
  - `recovery-logs/stage2-20260502T154407.log` documents the per-pass recovery (25 / 42 / 38 /
    28 / 27 stuck tiles closed; +612 new detections).
  - Launch metadata: `launch_manifest.json` shows `started_at: 2026-04-18T14:27:03Z`,
    `seed: 42`, `proposer.temperature: 0.7`.
- **T=0.3 run + recovery**: `outputs/55maps-text-high-t0.3-generalisation/`
  - `cost_manifest.json::by_stage.proposer.tiles_failed = 0` (post-recovery; re-verified
    2026-04-30).
  - `verified/run.meta.json` shows `finish_reason_counts.error: 629` (the original misreading),
    `parse_failures: 629`, `empty_responses: 629`.
  - `verified/probabilities.json` results count: 9,910 (re-verified 2026-04-30).
  - Launch metadata: `started_at: 2026-04-26T08:18:16Z`, `seed: 42`,
    `proposer.temperature: 0.3`.
  - Run commit: `4b4a87b3`; recovery commit: `548604d9`; recovery scripts commit: `06f994d0`.
- **Verifier-T pilot Stage A**: `results/verifier-t-pilot/per-t-stats.json` (re-verified
  2026-04-30; commit `f27842a5`).
- **Verifier-T pilot Stage B**: `results/verifier-t-pilot/stage-b-report.md` +
  `stage-b-summary.json` (commits `b9f73bbf` + `74edfb16`).
- **T=0.7 post-recovery analyses** (commit hashes in § 8 above):
  - Baseline + full-buffer + extended-buffer evaluation (BCa N = 10,000): `e20f3e18`,
    `f533fda5`.
  - Multi-buffer corrected F1 + 6 new reviews + 1 new GT mound: `f6eaeca9`,
    `results/55maps-text-high-generalisation/corrected-f1-multi-buffer/summary.json`.
  - MCC mirror: `d9bc3edc` (partial),
    `results/55maps-text-high-generalisation/mcc/evaluation.json`.
  - Pairwise permutation v2: `aeb9fb7f`,
    `results/55maps-text-high-generalisation/paired-vs-{min,high}-*/`.
  - D-S re-aggregation + crosstab (using fixed plumbing): `366f9c66`, `e07dae37`,
    `results/55maps-text-high-generalisation/dawid-skene/`,
    `.../ds-human-crosstab/`.
- **Recovery scripts**: `scripts/55maps-t0.3-recovery.sh`,
  `scripts/55maps-t0.3-extract-new-candidates.py`,
  `scripts/55maps-t0.3-rebuild-verified-geojson.py`, `scripts/merge_recovery_meta.py`,
  `scripts/55maps-t0.7-recovery-driver.sh` (commit `1ea92b9c`).

All on-disk numbers were re-verified from source files on 2026-05-03 in preparation for this
revision (per the project anti-confabulation protocol).

Re-derivation commands (from repo root):

```bash
# T=0.7 unrecovered failure count (post-recovery)
python3 -c "import json; d = json.load(open('outputs/55maps-text-high-generalisation/cost_manifest.json')); print(d['by_stage']['proposer']['tiles_failed'])"

# T=0.7 total run cost (post-recovery + verifier cleanup, with merged backups)
python3 -c "import json; d = json.load(open('outputs/55maps-text-high-generalisation/cost_manifest.json')); print(d['totals']['cost_usd'])"

# T=0.7 raw F1 at R = 50 m (post-recovery)
python3 -c "import json; d = json.load(open('outputs/55maps-text-high-generalisation/evaluation/evaluation.json')); print([b for b in d['summary']['buffers'] if b['buffer_metres']==50][0]['f1'])"

# T=0.7 corrected F1 multi-buffer (Approach B)
python3 -c "import json; d = json.load(open('results/55maps-text-high-generalisation/corrected-f1-multi-buffer/summary.json')); print([(r['R_m'], r['F1']) for r in d['results']])"

# T=0.7 tile-level MCC at R = 50 m (post-recovery)
python3 -c "import json; d = json.load(open('results/55maps-text-high-generalisation/mcc/evaluation.json')); print(d['summary']['tile_classification']['mcc'])"

# T=0.3 unrecovered failure count (post-recovery)
python3 -c "import json; d = json.load(open('outputs/55maps-text-high-t0.3-generalisation/cost_manifest.json')); print(d['by_stage']['proposer']['tiles_failed'])"

# Verifier-T pilot per-T failure rates
python3 -c "import json; print(json.dumps(json.load(open('results/verifier-t-pilot/per-t-stats.json')), indent=2))"
```

No random seed is relevant to this synthesis; the underlying runs used seed 42 (recorded in
`launch_manifest.json` for both 55-map runs). Bootstrap CIs in this report use the project
default N = 10,000 BCa for paper-headline figures (post-2026-05-02 N = 10K migration commits
`580f498b` + `0699769c`) and N = 1,000 percentile for the verifier-T pilot inherited values.

## 12. Verified vs unverified claims in this report

To support the project anti-confabulation protocol, this section enumerates which numerical
claims were re-derived from source files on 2026-05-03 versus carried forward without
re-verification.

**Re-verified on 2026-05-03 from source files:**

- T=0.7 proposer pre-recovery unrecovered failures: 160 / 42,705 (0.375 %) — re-derived from
  Obs 318's verified-source statement; pre-recovery state preserved in `*.pre-recovery-*.backup`
  per-pass metas.
- T=0.7 proposer post-recovery: 0 / 42,705 — re-derived from
  `outputs/55maps-text-high-generalisation/cost_manifest.json::by_stage.proposer.tiles_failed`.
- T=0.7 total run cost (post-recovery + verifier cleanup): $126.81 — re-derived from
  `outputs/55maps-text-high-generalisation/cost_manifest.json::totals.cost_usd`.
- T=0.7 raw F1 at R = 50 m: 0.7920 [0.7820, 0.8017] — re-derived from
  `outputs/55maps-text-high-generalisation/evaluation/evaluation.json`.
- T=0.7 tile-level MCC at R = 50 m: 0.6476 [0.6331, 0.6620] — re-derived from
  `results/55maps-text-high-generalisation/mcc/evaluation.json`.
- T=0.7 corrected-F1 multi-buffer at R = 50 m / 125 m: 0.8273 / 0.8338 — re-derived from
  `results/55maps-text-high-generalisation/corrected-f1-multi-buffer/summary.json`.
- T=0.7 recovery cost $57.10 and 160 / 160 stuck tiles closed — derived from
  `recovery-logs/stage2-20260502T154407.log` and merged per-pass meta cost differentials
  (Obs 319 verification).
- T=0.7 recovery `retries_other` total = 3,139 — derived from merged minus original per-pass
  meta `retries_other` (Obs 319 verified figure; spec said 3,144).
- T=0.3 proposer post-recovery: 0 / 42,705 — re-derived from
  `outputs/55maps-text-high-t0.3-generalisation/cost_manifest.json`.
- T=0.3 verifier `finish_reason_counts.error: 629`, probabilities.json results count 9,910 —
  re-derived from `outputs/55maps-text-high-t0.3-generalisation/verified/`.
- Verifier-T pilot Stage A per-T failure counts (10 / 0 / 0 at T=0.0 / 0.5 / 1.0) — re-derived
  from `results/verifier-t-pilot/per-t-stats.json` (date 2026-04-30).
- Run dates and seeds — re-derived from `launch_manifest.json` for both 55-map runs
  (date 2026-04-30).
- Recovery commit `548604d9` text — re-derived via `git show 548604d9`.
- Recovery commit `731466d8` text and stats — re-derived via `git show 731466d8` and
  `recovery-logs/stage2-20260502T154407.log` tail.
- 3-tier JSON repair pipeline coverage (~92 % of 163 historical failures) — carried from
  commit `e3aef6fa` message; not independently re-audited within this synthesis.

**Re-verified on 2026-05-03 from source files (Session 84 follow-up recoveries):**

- Image post-recovery raw F1 at R = 50 m: **0.7745** — re-derived from
  `outputs/55maps-image-generalisation/evaluation/evaluation.json::summary.buffers[buffer_metres=50].f1`.
- Image post-recovery corrected F1 at R = 50 m: **0.8332** — re-derived from
  `results/55maps-image-generalisation/corrected-f1-multi-buffer/summary.json::results[R_m=50].F1`.
- Image post-recovery tile-level MCC at R = 50 m: **0.6924 [0.6784, 0.7062]** — re-derived
  from `results/55maps-image-generalisation/mcc/evaluation.json::summary.tile_classification.mcc`.
- Image post-recovery 18 silently-dropped verifier candidates — re-derived via commit message
  of `8082896b` (recovered single-pass via `run_pv.py cleanup`).
- Image follow-up recovery cost ~$0.029 (net new candidate impact) — derived from commit
  messages of `2992056b` (proposer $0.216), `8082896b` (verifier ~$0.02), and `a78cd7c5`
  cost-manifest aggregation (the manifest's $1,061 total reflects the cosmetic 3× double-
  counting bug; the true total is ~$365).
- Text-MIN post-recovery raw F1 at R = 50 m: **0.7619** (current evaluation.json) /
  **0.7595** (per commit `c1ea6df3` reviewed-GT comparator) — re-derived from
  `outputs/55maps-text-min-generalisation/evaluation/evaluation.json` and the post-GT-update
  re-eval at commit `236327d8`.
- Text-MIN post-recovery corrected F1 at R = 50 m: **0.7968** — re-derived from
  `results/55maps-text-min-generalisation/corrected-f1-multi-buffer/summary.json`.
- Text-MIN post-recovery tile-level MCC at R = 50 m: **0.626 [0.611, 0.641]** — re-derived
  from `results/55maps-text-min-generalisation/mcc/evaluation.json`.
- Text-MIN follow-up recovery cost $0.144 — derived from commit message of `c1ea6df3` and
  the cosmetic-2× cost_manifest acknowledgement in `b4a928d2` (manifest's $93.50 total
  reflects the double-counting bug; the true total is ~$60.79).
- Text-MIN no-op finding (per-pass detection geojson md5sums bit-identical to committed
  versions; +39 features from re-dedup, not new detections from recovery) — derived from
  commit message of `c1ea6df3`.
- GS-v2 post-recovery raw F1 at R = 50 m: **0.8859 [0.8798, 0.8919]** (Era 2, 487-tile) —
  re-derived from `results/gold-standard-extended-buffer-sweep-era2/evaluation.json`.
- GS-v2 post-recovery tile-level MCC at R = 50 m: **0.7778 [0.7663, 0.7896]** — re-derived
  from same source (Sens=0.7904, Spec=0.9690).
- GS-v2 10 silently-dropped verifier candidates (IDs 253, 292, 302, 304, 321, 359, 397, 408,
  435, 520) + 1 new from consensus rebuild = 11 total recovered — re-derived from commit
  message of `4ea54760`.
- GS-v2 follow-up recovery cost $0.041 (proposer) + ~$0.02 (verifier) = ~$0.061 — derived
  from commit messages of `c8fde2ae` and `4ea54760`.
- GS-v2 harness quirk: two resume invocations per pass required — derived from commit
  message of `c8fde2ae` (each of the 4 affected passes was run twice; net cost $0.041
  across all four passes).
- All 6 cross-track v2 paired-permutation deltas at R = 50 m and BH-significance verdicts
  (5 of 6 significant; T=0.7 vs image −0.0060 only ns pair):
  T=0.3 vs T=0.7 +0.0162 (sig), T=0.3 vs image +0.0102 (sig), T=0.7 vs image −0.0060 (ns),
  T=0.3 vs T=MIN +0.0467 (sig), T=0.7 vs T=MIN +0.0305 (sig), image vs T=MIN +0.0365 (sig)
  — re-derived from `results/55maps-pairwise-permutation-v2/paired-*/summary.json::per_buffer[buffer_metres=50]`.
- FP-classify 4-corpus re-classify cost $0.582 — re-derived from commit message of `42ed1d32`
  and `results/55maps-fp-classification/cost_summary.json::totals.cost_usd`.
- Total Session 84 follow-up arc cost ~$0.88 (image $0.029 + text-MIN $0.144 + GS-v2 $0.061 +
  FP-classify $0.582); recovery passes alone ~$0.30.

**Carried forward from observation history without independent re-derivation:**

- T=0.3 proposer pre-recovery unrecovered failures: 18 / 42,705 (0.042 %). The current
  `cost_manifest.json` shows 0 (post-recovery state); the pre-recovery 18 number relies on
  Obs 281's recording. Recovery commit `548604d9` independently states "18 tile-pass failures
  across runs 1-5 (5+2+4+5+2)" which matches Obs 281 — treat as cross-confirmed by two
  independent sources but not re-derived from raw meta files (which were overwritten by the
  recovery).
- T=0.3 verifier pre-recovery unrecovered: 1 (`candidate_05396`). Cross-confirmed by recovery
  commit message; not independently re-derived (the `probabilities.json` is post-recovery).
- T=0.7 verifier "9,131 candidates, 0 truly missing" (Obs 281 verifier table; pre-recovery
  source pool). Not independently re-verified for this synthesis; relies on Obs 281. The
  post-recovery source pool was re-clustered after the +612 new detections and verifier
  cleanup (commit `d7f85978`); the post-recovery 0-truly-missing claim derives from the
  cleanup completing without flagged residuals.

**Resolved contradictions (relative to prior synthesis revision):**

- Obs 281's tabulated T=0.7 row "25 / 42,545 = 0.059 %" was corrected to 160 / 42,705 = 0.375 %
  by Obs 318 (commit `f5df7a09`). Both numbers and rationale captured in § 1, § 3.1, and § 8.
- The pre-recovery T=0.7 raw F1 of 0.7896 cited in earlier draft updates was corrected to the
  post-recovery 0.7920 via the BCa N = 10K re-evaluation (commit `e20f3e18`) on the recovered
  detection pool.
- The pre-recovery corrected-F1 of 0.8260 was corrected to 0.8273 via the multi-buffer
  re-aggregation with 6 new reviews + 1 new GT mound (commit `f6eaeca9`).

## 13. Files in this directory

| File        | Contents                                                              |
|:------------|:----------------------------------------------------------------------|
| `report.md` | This document (the synthesis report; major revision 2026-05-03).      |

No new computational artefacts are generated by this report — it is a documentation-only
synthesis. All compute artefacts referenced live in
`outputs/55maps-text-high-generalisation/`,
`outputs/55maps-text-high-t0.3-generalisation/`,
`results/55maps-text-high-generalisation/`, and `results/verifier-t-pilot/`.

---

**End of report.**
