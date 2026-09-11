# § R7.2–R7.3 gaps — claims-with-anchors deltas for PI ruling (S153)

> **Last revised**: 2026-09-11 (original publication; the six scheduled
> R7.2–R7.3 gap items of S153 item (A)). See [§ Changelog](#changelog) for
> revision history.

**What this is.** Every sentence and number added to or changed in
`docs/paper/results-draft.md` this session, one claim per row, with the
file and line it was verified from. The PI rules per item. All new prose
in the draft is marked `[DRAFT, S153 — pending PI ruling]` inline; nothing
is final.

**Anti-confabulation.** Every figure below was re-read from its source
file during this session. Nothing is carried from
`planning/paper-writeup-continuity.md`, from a memory, or from the draft's
own prior text. Two provisional figures did **not** survive re-reading and
are flagged as corrections (§ 2.3, § 2.5).

**Cost of the session**: US$0 API. The only compute was one bootstrap,
run on sapphire.

**Branch**: `worktree-agent-a0eb70c8484c74422`. Commits are named per
section.

---

## 1. Item (i) — the Gemini 3.8 verifier-seat leg into § R7.3

Commit `c9d081943`. Four sentences inserted after the verifier-seat
mechanism paragraph (`docs/paper/results-draft.md:714`), immediately before
the r2 board paragraph.

| # | Claim as drafted | Anchor (re-read this session) |
|---|---|---|
| 1.1 | Gemini 3.8 Flash was published 2026-09-02 at 3.7's list price | Obs 448 provenance paragraph, `docs/notes/working-notes.md:31328`; rates 0.75 in / 3.75 out confirmed independently at `scripts/lib_llm_metadata.py:1055` |
| 1.2 | It re-verified the identical 791-candidate union at its lowest thinking level, so the two verifiers differ in model version alone | Obs 448, `docs/notes/working-notes.md:31333-31338`; register row `_note`, `results/run-conditions.json:12466`; `verifier_config` model `gemini-3.8-flash`, thinking `low`, T = 0.0, `n_candidates` 791 at `results/run-conditions.json:12448-12463` |
| 1.3 | 0.9258 F1 @ 20 m against the all-3.7 stack's 0.9265, difference −0.0007 at p = 0.78 | `results/gemini38-screen-2026-09-04/armV/pair_test.json`: `armv_best.f1` 0.9257950530035335, `pairs["all-3.7"].f1_b` 0.926488, `observed_diff` −0.000693, `p_value` 0.7769 |
| 1.4 | Because both arms score the same candidates the paired instrument resolves about 0.011 | same file, `pairs["all-3.7"].null_std` 0.00379 over `n_tiles` 487; 2.8 σ ≈ 0.0106. Obs 448 § (a) states the same, `working-notes.md:31353-31358` |
| 1.5 | This is a measured tie, not an underpowered one | observed 0.18 σ against a resolvable 2.8 σ, from the two figures in 1.3/1.4 |
| 1.6 | On the Era-2 board of § R4 the 3.8 cell joins Tier 1 at 0.9182, third of the five | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json`: `ranking[2]` rank 3, `eval_f1` 0.9182, `tier` 1; `tie_set` has five members, all `g37-*` |
| 1.7 | In that seat 3.8 thinks 28 % less per candidate than 3.7 (76 against 106) | Obs 448 § (c) table, `working-notes.md:31377-31382` |
| 1.8 | For about $0.85 | Obs 448 provenance, `working-notes.md:31341-31344`; repeated in the register row `_note`, `results/run-conditions.json:12466` |
| 1.9 | The 3.8 proposer seat was never measured, so nothing bears on 3.8 as a proposer | Obs 448 § (f), the PI's STOP-after-Arm-V ruling and the untested E2, `working-notes.md:31441-31452` |

**Frame distinction the drafting had to get right.** Obs 448's headline
0.9258 and the board's 0.9182 are the **same cell on two frames**, not a
discrepancy. 0.9258 is the screen's own committed evaluation
(`results/gemini38-screen-2026-09-04/armV/best-eval/evaluation.json`, the
path the register row's `eval_path` names); 0.9182 is the same recipe
re-scored on the Era-2 ∩ B-union frame, `era2-b-487`
(`results/run-conditions.json:12570,12578`, and confirmed by reading
buffer 20 out of the board cell's `evaluation.json`: f1 0.9182, precision
0.9335, recall 0.9034). The draft uses the screen figure for the
head-to-head and the board figure for the tier claim, and says which is
which. Note that the screen's **recall** is also 0.9182 — numerically
equal to the board F1 and easy to conflate; both were read separately.

**Jargon translated at writing time** (PI's standing rule): "Era-2" is
glossed in place as "the 487-tile gold-standard frame". "swap38" does not
appear in the prose at all — the leg is described as the successor model
re-verifying the same candidate union.

**Draft note (c)** rewritten to read RESOLVED, naming the two register
rows it was waiting on.

**Not changed**: Obs 448 itself; the register rows; the board; any § R7.3
figure that existed before this session; draft notes (a) and (d); the
image-screen paragraph that follows.

---

## 2. Item (ii) — the 3.7 cost column, audited basis

Commit `ef1385ebb`.

### 2.1 Method

Follows `reports/token-load-audit-2026-06-12.md` § 2 exactly:

1. **Clean load** = the sum of `per_item_metadata` token records over
   **unique `item_id` with `finish_reason == "success"`** (final attempt
   per tile). The merged `usage_stats` block is ignored, which is what
   excludes retry and recovery-merge double-counting. In `run_1` the
   difference is visible directly: `usage_stats.request_count` is 24,561
   against 24,242 unique successes.
2. **Thinking billed at the output rate** — `thoughts_tokens` added to
   `output_tokens` before pricing. (`total_reasoning_tokens` is 0
   throughout; this family records thinking under `thoughts_tokens`.)
3. **Cached input** priced at the cache rate and deducted from fresh
   input. Measured `cached_input_tokens` is **zero on every meta in
   this campaign**, so the cached-input discount is inert here and the
   cache rate is not load-bearing on any figure below.
4. **Flex tier** = 0.5 × list (`FLEX_DISCOUNT`,
   `scripts/lib_llm_metadata.py:1082`).

**Rates, on file** — `scripts/lib_llm_metadata.py:1054-1055`:
`gemini-3.7-flash` and `gemini-3.8-flash` both `{input: 0.75, output:
3.75}` per 1M, standard tier, with the source comment "verified 2026-09-04
against ai.google.dev/gemini-api/docs/pricing (page dated 2026-09-03)".
Flex therefore 0.375 / 1.875. `gemini-3-flash-preview` is
`{input: 0.50, output: 3.00}` (line 1045), flex 0.25 / 1.50.
**No rate here was invented.**

Working script kept in the session scratchpad (throwaway, no
reproducibility value beyond this table); the method above is sufficient
to reproduce every figure from the committed metas.

### 2.2 Proposer — five 3.7 passes, `outputs/gemini37-55map-2026-08-29/g384_ov192_55map_g37/`

| meta | calls | input | cached | output | thinking | USD (flex) |
|---|---:|---:|---:|---:|---:|---:|
| `run_1` | 24,242 | 36,411,484 | 0 | 1,293,053 | 6,518,509 | $28.30 |
| `run_1_recovery` | 322 | 483,644 | 0 | 19,925 | 90,279 | $0.39 |
| `run_2` | 24,469 | 36,752,438 | 0 | 1,307,695 | 6,619,966 | $28.65 |
| `run_2_recovery` | 95 | 142,690 | 0 | 4,894 | 32,855 | $0.12 |
| `run_3` | 9,186 | 13,797,372 | 0 | 389,601 | 2,460,525 | $10.52 |
| `run_3_recovery` | 15,366 | 23,079,732 | 0 | 923,200 | 4,233,987 | $18.32 |
| `run_3_recovery2` | 9 | 13,518 | 0 | 1,029 | 3,531 | $0.01 |
| `run_4` | 24,556 | 36,883,112 | 0 | 1,318,571 | 6,720,795 | $28.90 |
| `run_4_recovery` | 6 | 9,012 | 0 | 530 | 3,145 | $0.01 |
| `run_5` | 24,561 | 36,890,622 | 0 | 1,315,033 | 6,795,508 | $29.04 |
| `run_5_recovery` | 1 | 1,502 | 0 | 74 | 371 | $0.00 |
| **total** | | | | | | **$144.27** |

Two integrity checks passed:

- **Pass 3 reconstructs exactly.** `run_3` is the only meta stored
  gzipped (`…meta.json.gz`), which is why a `-name "*.meta.json"` sweep
  misses it; its primary covers 9,186 tiles and its two recoveries 15,366
  + 9, summing to **24,561** — the per-pass tile count of this tiling,
  matching `run_5`'s complete pass exactly. Had the gzipped meta been
  missed, the proposer total would have read $133.76.
- **The pass count is 5, not more.** Five primaries, no double-counted
  pass.

$144.27 corroborates the continuity's provisional "$144" to the cent,
which is the one provisional figure in this item that survived
re-reading.

### 2.3 Verifier arms — and a correction

The verify path writes no `per_item_metadata`, so these are priced from
`usage_stats` (one merged block per run; `items_failed` is 0 on both, so
there is no recovery to exclude).

| arm | verifier model | candidates | input | output | thinking | rate basis | USD (flex) |
|---|---|---:|---:|---:|---:|---|---:|
| arm 1 | `gemini-3-flash-preview` | 12,715 | 22,785,280 | 2,129,268 | 0 | 0.50 / 3.00 | **$8.89** |
| arm 2 | `gemini-3.7-flash` | 12,715 | 22,785,280 | 1,608,503 | 1,464,066 | 0.75 / 3.75 | **$14.31** |

Anchors: `outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/verify_arm1/run.meta.json`
and `…/verify_arm2/run.meta.json`, keys under `usage_stats`, plus
`configuration.model`, `execution_stats.items_processed`.

> ⚠ **CORRECTION — the provisional $12.54 was wrong.** The draft (and the
> continuity) named the verifier arms as "$12.54 and $14.31". $14.31
> reproduces exactly. The $12.54 does **not**: it is arm 1 priced at
> 3.7's own rates, i.e. 0.5 x (22.78528 x 0.75 + 2.129268 x 3.75) =
> $12.5369. But arm 1's verifier is `gemini-3-flash-preview`, and at its
> own rates arm 1 is $8.89, so the provisional figure overstated it by
> $3.65.

**Why the metas' own `cost_estimate` cannot be used.** Two independent
recording defects, both visible in the files:

- Every 3.7 meta records `pricing_used: {input_per_1m: 0.5, output_per_1m:
  3.0}` — the Gemini 3 rates. This is the fuzzy-matcher fall-through the
  pricing fix was written to close (`scripts/lib_llm_metadata.py:1048-1053`
  comment: "Without these keys the fuzzy matcher fell through to
  ``default`` and the 3.7 screen metas were priced at Gemini 3 rates").
  `run_1`'s recorded $11.04 against an audited $28.30 is the 2.56× effect.
- The verify path stamps `cost_basis: "list"` with `discount: 1.0` **even
  under flex** — Obs 448 § (g) records this as a runner gotcha; confirmed
  on all eight verifier metas read this session.

### 2.4 What went into the table and the paragraph

| Cell / claim | Value | Basis |
|---|---|---|
| § R7.2 table, 3.7 arm 1 cost | **$153** | $144.27 proposer + $8.89 verifier = $153.16 |
| § R7.2 table, 3.7 arm 2 cost | **$159** | $144.27 proposer + $14.31 verifier = $158.58 |
| § R7.2 table, fourth cell cost | **not supplied** | see § 2.5 |
| § R7.3, "the campaign spent $167 to place both" | $167 | 144.27 + 8.89 + 14.31 = $167.47; arms 1 and 2 share one proposer, so the per-row figures are not additive |
| § R7.3, billed reconciliation | still pending | **no billing record found in the repo.** Searched for a 3.7 invoice or billing-console figure; the only billing corroboration on file is `reports/token-load-audit-2026-06-12.md` § 10, which is the April/June Gemini 3 dailies and predates this family. The draft therefore keeps the "roughly 0.6 ×" note as a flagged expectation, not a measurement. |

Both arms are noted in the table as sharing one proposer, so a reader
cannot sum the column.

### 2.5 Fourth cell — not supplied, and why

Its verifier is `outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/verify_37/run.meta.json`
(located via the register row `_note` at `results/run-conditions.json:11626`,
which records 57,482 candidates). That meta records
`items_processed: 29` — it is the **cleanup pass**, which overwrote the
main run's metadata. The directory holds only `probabilities.json` and
that one meta, so the 57,482-candidate token load is **not on file**. Its
GS calibration leg (`outputs/grid-2026-08-18/verifier/g384_ov192/verify_37/`)
is the same story at `items_processed: 1`.

**For the PI to rule.** A simulated figure is available on the precedent
the § R7.2 table already sets ("the N < 10 rungs' costs are simulated from
audited per-call rates"): arm 2's audited 3.7-verifier rate is
$14.3055 / 12,715 = **$0.001125 per candidate**, giving about **$64.7** over
57,482 candidates, and with B's K = 10 proposer cost of **$173.59**
(`results/55map-final-board-r2-2026-09-06/final_board_50m.json`,
`B-N10-oracle.cost_usd`) a full-stack of about $238. I have **not** put
this in the table, because every other filled cell in that column is
audited and mixing bases silently would be worse than a gap. Ruling
wanted: table it as "about $238 (verifier simulated)", or leave the gap.

### 2.6 Disclosed lower bound

Two aborted partial runs,
`g384_ov192_55map_g37/archive-run2-partial-aborted-2026-08-30/` and
`archive-run3-partial-aborted-2026-08-30/`, hold `experiment_intent.md`
(and one GeoJSON) but **no meta**. They consumed real tokens that no file
records, so $144.27 and the two arm totals are **lower bounds**. This is
the same caveat `token-load-audit-2026-06-12.md` § 8 attaches to the
Gemini 3 figures, so the column stays internally consistent.

**Not changed**: the Gemini 3 cost cells ($207 / $261 / $23 / $195 / $104
/ $97), which are the 2026-06-12 audit's figures and were not re-derived;
the F1, MCC, tier, and operating-point columns of every row; § R6's
frontier, which is still not extended to this family; § 5.4 of the
methods outline.

---

## 3. Item (iii) — back-reference from § R7.3 to § R4

Commit `6b3dac728`. One sentence appended to the r2 board paragraph.

| # | Claim | Anchor |
|---|---|---|
| 3.1 | All five Tier-1 cells on the § R4 Era-2 board are Gemini 3.7 or 3.8 | `tiering_20m.json` `tie_set`: five entries, all `g37-*` (three `gemini37-screen`, two `gemini37-image-gs`) |
| 3.2 | Every Gemini 3 cell falls to Tier 2 or below at both its committed and its sweep-optimal operating point | `tiering_20m.md`: ranks 1–5 are the five 3.7/3.8 cells, rank 6 (`g37-text-k5-verified-carried`) opens tier 2; the best Gemini 3 committed cell is rank 8 (`verified-384-16of30-t0-3-n5-opmax`, 0.895) and the best `-opmax` sweep optimum rank 11 (`pv-high-text-t0.3-n5-opmax`, 0.887), both tier 2 |
| 3.3 | 487 curated tiles | `tiering_20m.json` `n_tiles`: 487 |
| 3.4 | 55 deployment sheets | the 55-map corpus of § R7.2, unchanged |

The sentence **restates no § R4 number**, by design: it makes a
membership claim that § R4 already carries, so it cannot drift from the
paragraph it cites if § R4's figures are later refreshed. § R4 already
points forward to § R7.3 (`results-draft.md:330`); this closes the pair.

**Not changed**: the § R4 paragraph itself, including its `[DRAFT NOTE,
S152]` and its unsigned-ruling status; any figure in § R4.

---

## 4. Item (iv) — the "+0.0267 above the entire Gemini 3 board" claim

Commit `3ef24e98a`. **The figure HOLDS, and it is an r2-chain figure.**

Recomputed from the register's cell values in
`results/55map-final-board-r2-2026-09-06/final_board_50m.json` (analysis
`55map-final-board-r2-2026-09-06`, `results/run-analyses.json:1940`;
`reference: "r2"`, `buffer_m: 50`, 35 cells):

| quantity | value | source |
|---|---:|---|
| arm 2 N = 5 carried | 0.8827 | `ARM2-N5-carried.f1_50` |
| arm 2 N = 5 oracle | 0.8871 | `ARM2-N5-oracle.f1_50` |
| best Gemini 3 cell, oracles included | 0.8560 | `B-N10-oracle.f1_50` (the max over all 23 non-`ARM*`/`FOURTH*` cells) |
| carried − best Gemini 3 | **+0.0267** | 0.8827 − 0.8560 |
| oracle − best Gemini 3 | **+0.0311** | 0.8871 − 0.8560 |

So **+0.0267 belongs to arm 2's *carried* point**, measured against B's
own N = 10 oracle, on the r2 chain. It is not a canonical-chain figure and
it is not the oracle's margin.

**Why the sentence was still touched.** The old wording put "+0.0267"
after a clause naming *both* 0.8871 and 0.8827, and the oracle's margin
against the same comparator is +0.0311. A reader attaching the figure to
the nearer headline number would be out by 0.0044 with nothing in the
sentence to catch it. The edit names the comparator and gives both
margins. **This is a disambiguation, not a correction** — no number in
the draft was wrong.

Three neighbouring figures were re-verified in passing and all hold:
arm 2 N = 3 oracle 0.8848, within 0.0023 of N = 5 (`ARM2-N3-oracle`);
the fourth cell's tile-MCC 0.726 at precision 0.9522 and recall 0.8057
(`FOURTH-N10-carried`); tier assignments T1/T2/T3/T4 for
`ARM2-N5-oracle` / `ARM2-N5-carried` / `FOURTH-N10-carried` /
`ARM1-N5-carried` (the `tiers` list, positions 0–3).

**Not changed**: the r2 board; the analysis row; the canonical-chain
figures in the surrounding sentences; the fourth-cell and arm-1
sentences.

---

## 5. Item (v) — the 44th pending twin, and the signed row

Commit `5ed589fe1`.

**Ran where it belonged.** The bootstrap ran on **sapphire** (`ssh
sapphire`, `~/Code/map-reader-llm` on `main` at `54ae2dc03`, its own
`.venv`), using verbatim the command committed at
`results/uplift-supplement/verifier-pairing-commands.sh:256` — 14 buffers,
`--bootstrap 10000 --seed 42 --mcc`. Output copied back with `scp` to the
same relative path. No bootstrap ran on the local machine.

| # | Claim | Anchor |
|---|---|---|
| 5.1 | Twin F1 @ 20 m 0.5431, precision 0.3964, recall 0.8621, 946 detections | `results/uplift-supplement/verifier-pairing/pv-diag-384__pv-min-text-t0_0-n3-opmax/evaluation.json`, `summary.buffers[buffer_metres=20]`, `summary.n_detections` |
| 5.2 | Twin tile MCC 0.1072 (confusion tp 213 / tn 35 / fp 223 / fn 16) | same file, `summary.tile_classification` |
| 5.3 | F1 uplift **+0.3192** (verified 0.8623 − twin 0.5431) | `results/uplift-supplement/verifier-uplift.csv`, the `pair::pv-diag-384::pv-min-text-t0.0-n3-opmax` row |
| 5.4 | MCC uplift **+0.6762** (verified 0.7834 − twin 0.1072) | `results/uplift-supplement/verifier-uplift-mcc.csv`, same row |
| 5.5 | 172 rows, **129 computed / 43 pending**, both metrics | generator stdout and a recount of both CSVs |
| 5.6 | All 43 remaining are `blocked` (no twin locatable) | `results/uplift-supplement/verifier-pairing-report.md:43,139`: `blocked` 43 |

Regeneration used `scripts/compute_verifier_uplift.py` (F1) and
`… --metric MCC`. Checked first: the script has **no** `--dry-run`; its
only flags are `--repo-root`, `--out-dir`, `--metric`, so it writes by
default. `scripts/build_uplift_supplement.py` was **not** re-run — the
flatten is unaffected by a twin score, and re-running it would churn
`conditions.csv` for no reason.

The diff is **one row in each CSV**, `pending` → `computed`. Nothing else
in either file moved.

**Research-calibration note.** The twin is 946 detections at precision
0.396 — a near-indiscriminate proposer set — and the verifier lifts tile
MCC from 0.107 to 0.783. This is the largest F1 uplift on the GS Era-2
frame and it replicates the S152 finding on the single-pass baseline twin
(MCC −0.004 → 0.833, continuity WN-C22). It is consistent, not anomalous:
the verifier is acting as the tile classifier, which is the mechanism that
case established. Flagged rather than passed over.

### 5.1 The SIGNED `verifier-uplift-pairing` row — NOT touched

`results/run-analyses.json:2798`. `manually_verified_at`
`2026-09-10T22:55:40Z`, `_signature_note` "Approved as drafted and signed
… by the PI (S152 registration walk-through, ruling 2(v))". Its `outcome`
still reads **"85 of 172 pairs computed"** and `conditions_compared` holds
**85** entries — its signing state. I verified that neither generator
writes to this file (the only paths either touched were the two CSVs), so
no amendment was made by accident and none was made on purpose.

The row is now **two** amendments behind, not one: 85 → 128 was already
item B1 of the schedule, and this session adds 128 → 129. Figures for the
amended row, recomputed from the current CSVs this session:

| field | signed value | current value |
|---|---|---|
| computed / total | 85 of 172 | **129 of 172** |
| blocked | 86 | **43** |
| F1 uplift median | +0.212 | **+0.2467** |
| F1 uplift range | −0.0003 to +0.486 | **−0.0003 to +0.4860** (1 negative) |
| MCC uplift median | not in the row | **+0.4909** (3 negatives, min −0.0230, max +0.8410) |
| `conditions_compared` length | 85 | **129** |

By frame, computed pairs (identical counts on both metrics):

| frame | n | F1 median | MCC median |
|---|---:|---:|---:|
| `55maps-8541` | 59 | +0.3532 | +0.5749 |
| `era-2-487` | 43 | +0.1486 | +0.3005 |
| `grid-common-487` | 21 | +0.1935 | +0.3348 |
| `era-3-327` | 4 | +0.0047 | +0.0633 |
| `px256-1032` | 2 | +0.4011 | +0.5872 |

The single row added this session is on `era-2-487`, which is why that
frame moves 42 → 43 and nothing else does.

**Not changed**: the signed row's counts, `outcome`,
`conditions_compared`, `manually_verified_at`, or `_signature_note`; the
40 `-opmax` rows, still out of the supplement by design (E56);
`conditions.csv`; the 43 blocked disclosures.

**No `results/uplift-supplement/*.md` refreshed, so no changelog
attached.** Checked all four: `build-report.md`,
`verifier-pairing-report.md`, `notation-extension-proposal.md`,
`k1-gapfill-disclosure.md`. None states the computed count in its body —
the count lives in the CSVs — and the `blocked` 43 that
`verifier-pairing-report.md` does state is **unchanged** by this scoring
(the twin was `ready`, never `blocked`).

**Observation, not fixed** (outside the six items):
`verifier-pairing-report.md:140` still narrates "the ceiling after a clean
run … is **34 computed, 138 pending**", a 2026-08-29 statement four
campaigns stale. It is generated prose, so it needs a generator change
rather than an edit. Flagged for the PI.

---

## 6. Item (vi) — hypothesis-outcome table and the notation test

Commit `0ec5a599e`.

### 6.1 `test_live_register_projects_and_matches_committed_output` — real drift, regenerated

The table is a pure projection of `results/analyses-manifest.json` (D17),
so registering `verifier-uplift-pairing` in S152 changed what it projects.
Regenerated with `scripts/generate_hypothesis_outcome_table.py` (per its
header; `--check` confirmed STALE before, clean after).

**Before → after — the complete diff, three lines:**

| Location | Before | After |
|---|---|---|
| H2 post-hoc row | eight analyses, ending `verifier-robustness-matrix [post-hoc]` | nine — gains `verifier-uplift-pairing [post-hoc]` |
| unreferenced-analyses list | ends `tile-level-f1` | gains `uplift-supplement-flatten` |
| source-commit stamp | `97f166355` | `54ae2dc03` |

**What did NOT change**: every disposition, every registered tier, every
preregistration label, every deviation, the H1–H8 family BH-FDR verdict,
and the hypothesis count (15). No other H-row moved — H1 already carried
`gs-era2-verified-board-2026-09-10`.

Test now passes (9 passed in that module).

> ⚠ **POLICY COLLISION — for the PI to rule.** The Document Revision
> Policy asks for a banner and a `## Changelog` on `results/**.md`. This
> file **cannot carry one**: it is stamped "GENERATED FILE — do not
> hand-edit", the generator emits no changelog section, and the generator's
> own `--check` drift guard asserts byte-equality against a fresh
> projection — so a hand-added changelog would fail the very tier-1 test
> this commit fixes. I did not force it. The before→after note lives in
> this report and in the commit message instead. Three routes: (a) teach
> the generator to emit a `## Changelog` from a data file, which sits
> awkwardly with D17's "no cell is hand-maintained"; (b) declare generated
> projections out of revision-policy scope in
> `docs/methodology/output-directory-standard.md` § "Documents in Revision
> Policy Scope", whose scope line already says "anchor docs only";
> (c) leave it, with the revision trail in git and in reports like this.
> My recommendation is (b) — the policy's purpose is answering "is this
> current?", and a generated file with a source-commit stamp plus a drift
> guard already answers that better than a changelog would.

### 6.2 `test_no_extension_duplicates_a_sanctioned_name` — the TEST was wrong

**Diagnosis.** The test asserts that no name in `COLUMN_EXTENSIONS` is
also sanctioned by the canonical key. It reported **85** overlaps — every
extension at once, which is the shape of a premise failure, not of a
duplicate-name defect.

Root cause: on **2026-09-10** the PI sanctioned the builder's declared
extensions *into* the key as **§ 7.1 "Uplift-supplement dataset columns"**
(`docs/methodology/notation-key.md:124-126`, which names the ruling: "PI
ruling 2(i) of the supplement's registration walk-through … from the
builder's declared extensions"). `NotationKey` harvests `## 6.` through
`## 8.` (`scripts/lib_uplift_supplement.py:487`), so § 7.1 is inside the
harvest and every folded-in column now reads as a shadow. The fold-in
itself became the failure.

**Measured, this session:**

| quantity | value |
|---|---:|
| `COLUMN_EXTENSIONS` entries | 86 |
| § 7.1 table rows | 85 |
| in § 7.1 but not a declared extension | **0** |
| declared extensions not in § 7.1 | **1** (`crop_manifest_path`) |
| extension ∩ key, **outside § 7.1** | **0** |

So § 7.1 *is* the extension table folded into the key, and the invariant's
real content — an extension shadowing a name the key sanctions
**elsewhere** — holds with zero violations.

**Decision: fix the test, minimally.** Rescoped the assertion to the key's
vocabulary excluding § 7.1, via a documented `_section_7_1_columns()`
helper that returns the empty set if § 7.1 disappears (so the check keeps
full strength rather than silently passing). Rejected alternatives:

- **Change the data** — delete 85 entries from `COLUMN_EXTENSIONS`. This
  would strip each column's warrant and break
  `notation-extension-proposal.md`, which is generated from them, and the
  lib's own contract says a builder "must not amend the canonical key"
  (`scripts/lib_uplift_supplement.py:266`). The extension table is still
  the generator; § 7.1 is its published form.
- **Change the key** — not available and not attempted: § 7.1 is a
  **PI-signed artefact** (sanctioned by ruling 2(i)). Per the brief I
  stopped short of it.

Module now 122 passed, `ruff check` clean.

**Disclosure for the PI**: `crop_manifest_path` is the one declared
extension § 7.1 does not list, so the key and the proposal document have
drifted by exactly one column since the fold-in. Left alone — amending
§ 7.1 is a PI-signed-artefact change. It needs a ruling at the next
notation-key touch.

### 6.3 Tier-1 suite

```text
FAILED tests/test_per_arch_md_ownership.py::test_verify_run_leaves_the_working_tree_clean
= 1 failed, 2219 passed, 1 skipped, 27 deselected, 3 xfailed, 4 warnings in 236.61s (0:03:56) =
```

Both target failures are fixed. The one remaining failure is an
**environment artefact of worktree isolation, not a defect**: the test
shells out to the relative path `.venv/bin/python`
(`tests/test_per_arch_md_ownership.py:267`) with `cwd=PROJECT_ROOT`, and a
worktree has no `.venv` of its own — the venv lives in the main checkout.
It fails as `FileNotFoundError: '.venv/bin/python'` before running any
project code. Proved environmental by running that exact test in a real
checkout with a venv (sapphire, `~/Code/map-reader-llm` on `main`): **1
passed**. Not fixed here — outside the six items, and hard-coding a venv
path is a pre-existing fragility worth its own decision (it would also
fail for any contributor whose venv sits elsewhere).

---

## 7. Ruling summary

| # | Item | State | Ruling wanted |
|---|---|---|---|
| i | 3.8 verifier-seat prose in § R7.3 | drafted, note (c) resolved | approve / revise the four sentences |
| ii | 3.7 cost column | arms 1 and 2 audited and filled; fourth cell gapped | (a) accept $153 / $159; (b) fourth cell — table ≈ $238 with "verifier simulated", or leave the gap; (c) accept the $12.54 → $8.89 correction |
| iii | § R7.3 → § R4 back-reference | drafted | approve / revise the one sentence |
| iv | "+0.0267" | verified, holds, r2-chain, carried point | approve the disambiguation |
| v | 44th twin | scored, 129 of 172 | B1: amend and re-sign the pairing row with § 5.1's figures |
| vi | two tests | both fixed | (a) approve the test rescope; (b) rule the generated-file/revision-policy collision (§ 6.1); (c) `crop_manifest_path` fold-in |

Also raised, no action taken:

- `results-draft.md:341` (§ R4's S152 draft note) dates the
  mis-materialised `-opmax` rebuild to **2026-04-19**. The continuity and
  Obs 466 place it in **S152, 2026-09-10**. Likely a typo in a paragraph
  outside my six items, so untouched — worth a look on the next § R4 pass.
- `verifier-pairing-report.md:140`'s stale "34 computed, 138 pending"
  narration (§ 5).
- The hard-coded `.venv/bin/python` in
  `tests/test_per_arch_md_ownership.py` (§ 6.3).

---

## Changelog

### 2026-09-11 — Original publication

Written in S153 by a worktree-isolated agent (branch
`worktree-agent-a0eb70c8484c74422`) executing item (A) of the S152
schedule: the six R7.2–R7.3 gap items, as claims-with-anchors deltas for
the PI to rule on per item rather than as silent prose. Initial state:
§§ 1–6 covering items (i)–(vi), each with its claims table, its anchors,
and an explicit "not changed" list; § 2 carries the full cost-audit
working (per-run token table and method); § 7 is the ruling summary.

Commits landed: `c9d081943` (i), `ef1385ebb` (ii), `6b3dac728` (iii),
`3ef24e98a` (iv), `5ed589fe1` (v), `0ec5a599e` (vi). US$0 API; one
bootstrap on sapphire.

Two provisional figures did not survive re-reading and are recorded as
corrections: the verifier arm cost $12.54 → **$8.89** (§ 2.3, arm 1
priced at the wrong model's rates) and the fourth cell's cost, which is
**not recoverable** from committed metadata (§ 2.5). Two claims were
checked and **held**: the proposer total $144 → $144.27 (§ 2.2) and the
"+0.0267" margin (§ 4).
