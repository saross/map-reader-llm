# Recovering the overwritten verifier metadata from git history

> **Last revised**: 2026-09-14 (original publication — the PI's first ruling
> of 2026-09-14, on the 26 stages
> `reports/cleanup-meta-fix-2026-09-14.md` § 4 called unrecoverable). See
> [§ Changelog](#changelog) for revision history.

**Scope.** `reports/cleanup-meta-fix-2026-09-14.md` § 4 censused 29 verifier
stages whose `run.meta.json` carries the cleanup/resume overwrite signature,
recovered 3 from files on disc, and called the other **26 unrecoverable from
the working tree**. The PI asked whether git history holds the pre-overwrite
metadata. It does, for **17 of the 26**. This report records what was found,
per stage, with the blob hash and commit that hold it; what the remaining
**9** would need instead; the `--temperature` blind spot that same report left
for the PI, now closed; and a Gemini 3.1 Pro rate card read from Google's
pricing page, which prices the three Pro verifier stages the sweep could not
price at all.

Every figure below is reproducible from two artefacts committed with this
report: the register `outputs/verifier-meta-recovery-2026-09-14.json` and the
script that wrote it, `scripts/recover_verifier_meta_from_git.py`.

**Headline**: 17 recovered, 0 partial, 9 not in history.
**US$41.2226** of verifier spend that no audit could see is now audited.
The fourth cell is **not** among the recoveries.

## 1. Why history holds anything at all

This repository commits `outputs/**` (the PI's standing rule: every API-run
output is committed). A stage whose results were committed **before** its
second pass overwrote the metadata therefore still carries the pre-overwrite
`run.meta.json` as a git blob, even though nothing in the working tree does.
The 26 stages divide exactly on that timing:

- 17 were committed in April 2026 with their main pass's metadata intact
  (commits dated 2026-04-09 to 2026-04-25), and cleaned up weeks later, the
  damaged meta arriving in commits dated 2026-05-03 and 2026-05-06. The April
  blob is the main pass.
- 9 hold no usable pre-overwrite metadata. For **six** of them the only blob
  their `run.meta.json` has ever had is the damaged one: single-session
  campaigns, committed hours after the cleanup had already run. The other
  **three** do have an earlier blob, and it records zero tokens — a different
  failure entirely (§ 3.2).

### 1.1 Method

`scripts/recover_verifier_meta_from_git.py` takes the sweep's JSON
(`audit_verifier_cost.py --sweep outputs --json`) and, for the stages named:

1. **One** history walk over all 26 stage directories at once
   (`git log --all -M --name-status -- <26 paths>`). A walk per stage over
   140,000-plus commits and a 25 GB tree would cost an hour for the same
   answer; the single walk takes about two minutes on sapphire.
2. Every distinct blob of every metadata-shaped file that has ever lived in
   each stage directory (`git rev-parse <commit>:<path>`, then
   `git cat-file blob`), plus every deletion the history records
   (`--name-status` status `D`) and the tree of the stage's first commit.
3. A verdict per stage, and for a recovered stage a pass block carrying the
   blob's `usage_stats` **verbatim**.

Run as (on sapphire, which holds the history and the 48 GB tree):

```bash
python scripts/audit_verifier_cost.py --sweep outputs --json > sweep.json
python scripts/recover_verifier_meta_from_git.py \
    --sweep sweep.json --repo ~/Code/map-reader-llm \
    --stages-file stages26.txt --index-root outputs \
    --out outputs/verifier-meta-recovery-2026-09-14.json
```

**The search for sibling evidence came back empty, across all 26 stages.**
History records **zero deletions** in any of the 26 stage directories, and
every one of the 37 metadata blobs found is a version of `run.meta.json`
itself — no `.backup`, no `*.meta.json`, no `*.nohup`, nothing the overwrite
left behind and a later commit removed. Twenty stages have two blobs of that
file (the pre-overwrite meta and the damaged one); six have only one. That
count, 20 + 6, is the whole finding: 17 of the 20 second blobs carry usable
tokens, three do not (§ 3.2). One driver log survives outside a stage
directory and is used in § 4.

### 1.2 Two reconstructions, kept apart

| | What it is | Counted in audits? |
|---|---|---|
| `recovered_passes` | a blob's `usage_stats` **verbatim** — the money is exact | **Yes**, by `audit_verifier_cost.py` |
| `residual_estimate` | the missing candidates priced at the per-candidate token rates of the pass that *did* survive in the same stage | **Never** — surfaced as a note |

Only the *item count* of a recovered pass is reconstructed. The pre-2026-05
tracker never incremented `execution_stats.items_processed` — every April blob
reads `items_processed: 0` while `finish_reason_counts.success` carries the
real count — so the register uses that count and records
`items_processed_source` saying which field it came from. In five stages the
success count exceeds the missing-candidate count by 1 to 3 (e.g. 3,738
against a 3,735 shortfall): calls that succeeded but whose result was
superseded. The tokens are the pass's own either way.

### 1.3 The validity check that makes these recoveries safe

For every one of the 17, the **input tokens per candidate of the recovered
main pass equal those of the surviving cleanup pass to one decimal place**:

| Per-candidate input tokens | Stages |
|---:|---|
| 1,792.0 | 11 (text and image crops at 384 px) |
| 1,934.0 | 2 (checklist-text) |
| 1,567.0 | 2 (brief-text) |
| 1,889.0 | 1 (`55maps-generalisation/verified-v2`) |
| 8,452.0 | 1 (`image-t0.7/session-78-matrix/verified-checklist`) |

A blob that was an unrelated re-run, a different prompt, or a different crop
size would not reproduce the surviving pass's per-candidate load exactly. The
figures are in the register under `cross_check`. Where the stage also recorded
a `cleanup_history`, its `initial_missing` independently predicts the main
pass's coverage, and it agrees in all 17.

## 2. The 17 recovered

Columns: **meta n** = what the surviving damaged meta covers; **recovered n**
= what the blob covers; **audited US$** = the stage total at flex rates over
both passes; **was** = what an audit of the working tree alone reported.

| Stage (under `outputs/`) | results | meta n | recovered n | blob | commit | date | audited US$ | was | cache |
|---|---:|---:|---:|---|---|---|---:|---:|---:|
| `h11/pv-diag-384/verified/flash-high-text-1of5-flash-medium-verifier` | 3,736 | 1 | 3,738 | `8485af7d8e` | `3d22184d6` | 2026-04-15 | **7.5015** | 0.0036 | 0.000 |
| `55maps-generalisation/verified-v2` | 8,942 | 3 | 8,939 | `e09169f549` | `060a5240b` | 2026-04-10 | **6.4463** | 0.0022 | 0.000 |
| `h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist` | 2,017 | 1 | 2,019 | `df77e977a0` | `400e6fbcb` | 2026-04-25 | **4.7309** | 0.0023 | 0.001 |
| `h11/e47-propose-brief/verified/flash-high-text-1of5` | 4,358 | 57 | 4,301 | `25e47351cc` | `52b0215a6` | 2026-04-09 | **2.9857** | 0.0389 | 0.000 |
| `h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-checklist-text` | 3,736 | 21 | 3,717 | `a0e2f0a8ac` | `5cee158bc` | 2026-04-25 | **2.6849** | 0.0150 | 0.000 |
| `h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-adversarial-text` | 3,736 | 41 | 3,698 | `e77e0ac4c0` | `96a6ac235` | 2026-04-25 | **2.5623** | 0.0280 | 0.000 |
| `h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10` | 3,601 | 1 | 3,600 | `287a2188f2` | `b8961e56f` | 2026-04-17 | **2.4947** | 0.0007 | 0.000 |
| `h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5` | 2,840 | 1 | 2,839 | `c872b0d0ed` | `b8961e56f` | 2026-04-17 | **1.9618** | 0.0007 | 0.000 |
| `h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-brief-text` | 3,736 | 27 | 3,709 | `fd8216c029` | `bd0a4d091` | 2026-04-25 | **1.8533** | 0.0135 | 0.000 |
| `h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5` | 2,190 | 11 | 2,179 | `249cff9ecd` | `b8961e56f` | 2026-04-17 | **1.5163** | 0.0078 | 0.000 |
| `h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist-text` | 2,017 | 19 | 1,999 | `dfab48aeeb` | `f36e7bef9` | 2026-04-25 | **1.4407** | 0.0135 | 0.000 |
| `h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-adversarial-text` | 2,017 | 26 | 1,991 | `1eac65ac15` | `35b380a6d` | 2026-04-25 | **1.4037** | 0.0182 | 0.000 |
| `h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5` | 2,017 | 1 | 2,016 | `f06d1f8461` | `b8961e56f` | 2026-04-17 | **1.4028** | 0.0008 | 0.000 |
| `h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-brief-text` | 2,017 | 19 | 1,998 | `45c6fafa12` | `e85c62902` | 2026-04-25 | **0.9971** | 0.0094 | 0.000 |
| `h8-v2/wbf/scale-4/verified` | 1,114 | 15 | 1,099 | `4686d05de8` | `2e84d4a65` | 2026-04-16 | **0.7724** | 0.0109 | 0.000 |
| `h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10` | 802 | 460 | 342 | `9938edb9b3` | `b8961e56f` | 2026-04-17 | **0.5620** | 0.3246 | 0.000 |
| `h11/proposer-verifier-384/verified-adversarial-text-v1-prompt` | 572 | 1 | 571 | `131b4561f2` | `f33058f01` | 2026-04-10 | **0.3969** | 0.0006 | 0.000 |

**Every recovered stage's shortfall closes to zero**: the blob plus the
surviving pass account for every result key. Cache share is 0.000 in 16 of 17
(each crop is a distinct image) and 0.001 in the seventeenth, so the cache
rate barely matters to any of these figures.

The understatement the overwrite caused, per stage, ranges from **1.7×**
(`image-t0.0/verified-v1-n10`, whose resume kept 460 of 802) to **3,362×**
(`scale-4-optimal-487/verified-v1-n10`, whose cleanup covered 1 of 3,601).
The largest single recovery is US$7.50 for
`flash-high-text-1of5-flash-medium-verifier`, a MEDIUM-thinking verifier whose
main pass burnt 3.31 M thinking tokens — recorded in the blob, billed at the
output rate, and absent from every audit until now.

## 3. The nine not in history

| Stage (under `outputs/`) | results | meta n | missing | first commit | what it held | why | est. US$ |
|---|---:|---:|---:|---|---|---|---:|
| `stride-55map-2026-08-25/verifier/g384_ov192_55map/verify_37` | 57,482 | 29 | 57,453 | `a73d64346` 2026-09-01 | `probabilities.json`, `run.meta.json` | no pre-overwrite blob | 69.24 |
| `stride-55map-2026-08-25/verifier/g384_ov128_55map/verify` | 38,713 | 6 | 38,707 | `c368c9db7` 2026-08-26 | `probabilities.json`, `run.meta.json` | no pre-overwrite blob | 26.27 |
| `grid-2026-08-18/verifier/g384_ov192/verify_37` | 3,319 | 1 | 3,318 | `bce396250` 2026-08-31 | `probabilities.json`, `run.meta.json` | no pre-overwrite blob | 3.95 |
| `verifier-robustness/384-flash-high-text-ge3of5/T0.3/verified` | 4,275 | 2,775 | 1,500 | `af9214554` 2026-06-09 | `consensus.json`, `probabilities.json`, `run.meta.json` | no pre-overwrite blob | 1.03 |
| `flash35-pv-2x2/verified-f3vf` | 1,132 | 1 | 1,131 | `68c4f0e29` 2026-06-11 | `probabilities.json`, `run.meta.json` | no pre-overwrite blob | 0.79 |
| `h11/pv-diag-384/verified/text-baseline-pro-verifier` | 1,047 | 21 | 1,026 | `3d22184d6` 2026-04-15 | `probabilities.json`, `run.meta.json` | **Batch API main pass: tokens never recorded** | 5.21 |
| `h11/pv-diag-384/verified/pro-high-image-1of5-pro-verifier` | 841 | 8 | 833 | `3d22184d6` 2026-04-15 | `probabilities.json`, `run.meta.json` | **Batch API main pass** | 4.03 |
| `gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_swap37` | 791 | 2 | 789 | `3039d3ac9` 2026-08-29 | `probabilities.json`, `run.meta.json` | no pre-overwrite blob | 0.84 |
| `h11/pv-diag-384/verified/pro-medium-image-baseline-pro-verifier` | 519 | 10 | 509 | `3d22184d6` 2026-04-15 | `probabilities.json`, `run.meta.json` | **Batch API main pass** | 2.60 |

`est. US$` is the **estimate** of § 1.2, at flex rates, never an audited
figure: US$113.96 in all, of which US$95.51 is the two stride-campaign legs.
For the six "no pre-overwrite blob" stages the stage directory's first commit
is also its only commit for `run.meta.json`: the overwrite happened between
the run and the commit, in the same session.

### 3.1 The fourth cell: NOT recovered

`outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/verify_37`, at
**29 of 57,482 candidates**, is the worst case in the census and history does
not hold it. Its stage directory enters history at `a73d64346` (2026-09-01,
"results(gemini37): fourth cell harvested…") already carrying the 29-item
meta, five days after the campaign began and hours after the cleanup at
2026-09-01T03:57Z. Its audited figure stays **US$0.0349**, a lower bound over
29 candidates, and the tool still exits non-zero on it.

Two independent reconstructions of what it actually cost now exist, and they
disagree by about a fifth:

| Basis | USD (flex) | Source |
|---|---:|---|
| Day-isolated from the invoice | ≈ 58 | `reports/billing-reconciliation-2026-09-11.md` § 3.1, 31 August Pacific day |
| Simulated at arm 2's per-candidate rate | 64.7 | same report § 3 |
| This report's estimate, from the stage's own surviving 29-candidate pass | 69.24 | register `residual_estimate` |

The gap is consistent with the main pass **straddling the 30–31 August
Pacific billing boundary**: the day-isolation attributes only the 31 August
share. The estimate assumes 1,792 input, 132.4 output and 151.9 thinking
tokens per candidate, which the sibling 3-flash leg
`.../g384_ov192_55map/verify` corroborates exactly on the input side
(103,007,744 tokens over the same 57,482 candidates = 1,792.0 each). Nothing
here is a recovery; the PI should treat US$58–69 as the band.

### 3.2 The three Pro stages: the overwrite destroyed nothing

The three `*-pro-verifier` stages are a different failure. Their pre-overwrite
blob **exists** — `b622725518`, `f733735187`, `2354b48989`, all at
`3d22184d6` (2026-04-15) — and records **zero tokens**, because the main pass
ran through the async Batch API, which returns no per-response metadata. The
blobs' own windows date those batch passes to **2026-03-25** (08:27, 10:31 and
14:17 UTC), and the probabilities file at that commit reads `mode: batch` with
1,026 of 1,047 results already present.

So for these three stages the main pass's token load was **never in any
metadata to lose**. The 2026-05-06 realtime cleanup replaced an all-zero meta
with a 21-, 8- and 10-candidate one; the money was already invisible. This
also means the sweep's exclusion rule — `items_processed == 0` is a legitimate
batch stage, not damage — is doing real work, and that a batch main pass
followed by a realtime cleanup is the one shape that slips **into** the
damaged census while being a metadata gap of a different kind.

## 4. What the PI would need to export

Google bills on **Pacific** days and the project's exports are on that basis
(`reports/billing-reconciliation-2026-09-11.md` § 3.1), so the dates below are
Pacific. A daily project-filtered export bounds a stage when every *other* run
of the same model on that day has its own tokens on record, so their audited
cost can be subtracted from the day's SKU total. The register records the full
same-day inventory per stage under `billing_export`.

| Pacific day | For | Same-model runs that day | Status |
|---|---|---:|---|
| **2026-03-25** | the three Pro stages | 4 recorded metas, of which **3 record no tokens** | **not separable** — see below |
| **2026-06-09** | `verifier-robustness/…/T0.3/verified` | 9, all with tokens recorded | needed; boundable by subtraction |
| **2026-06-10** | `flash35-pv-2x2/verified-f3vf` | 4, all recorded | needed; boundable by subtraction |
| **2026-08-26** (and 2026-08-25 as a hedge) | `stride-…/g384_ov128_55map/verify` | 21, all recorded | needed; boundable by subtraction |
| 2026-08-29 | `verify_swap37` | 2, both recorded | **already exported** (§ 3.1 of the billing report) |
| 2026-08-30 | `grid-…/verify_37` | 8, all recorded | **already exported** |
| 2026-08-31 (and 2026-08-30) | the fourth cell | 3, all recorded | **already exported**; day-isolated at ≈ US$58 |

**Four new export dates**, then: **25 March, 9 June, 10 June and 26 August
2026** (plus 25 August as a hedge). Filter to the project and to the model's
SKU lines; the June and August days need Gemini 3 Flash flex SKUs, 25 March
needs Gemini 3.1 Pro.

Three qualifications the PI should know before asking:

- **25 March cannot isolate any one Pro stage.** Six Pro *batch* passes ran
  that day — the three damaged ones (1,026 + 833 + 509 = 2,368 candidates)
  and three whose zero-token metas survive intact (746 + 430 + 3,736 = 4,912
  candidates) — plus one realtime Pro pass that did record its tokens
  (504 candidates, 903,168 input, priced at US$2.709 in its own meta). The
  day's **Pro batch-tier** SKU line would bound all six batch passes jointly;
  apportioned by candidate count the three damaged stages are 32.5 % of that
  load. That is a joint bound and an apportionment, not a measurement.
- **The main pass's day is inferred for the six non-batch stages.** Only the
  surviving (later) pass carries a timestamp, so the register anchors on its
  Pacific day and flags that the main pass may have begun on the previous one.
  One stage is better anchored than that:
  `outputs/flash35-pv-2x2/tranche-full.log` (committed, lines 6360–6383)
  records the f3vf main pass finishing at 04:37 on 2026-06-11 AEST —
  2026-06-10T18:37Z, Pacific 10 June — and logs "Verification complete:
  1131/1132 candidates succeeded". It records no token totals: `run_pv.py`
  does not log usage, so a driver log can date a pass but never price it.
- **A subtraction residue is a difference of large numbers.** On 26 August the
  day's other recorded Gemini 3 Flash runs print about US$158 in their own
  metadata at **list** rates — six 24,5xx-tile proposer passes at about
  US$13.35 each, plus the sibling 57,482-candidate verifier at US$78.36 — and
  the residue sought is US$26 at **flex**, US$53 at list. So the wanted figure
  is about a third of the day's recorded spend on either basis: recoverable,
  but sensitive to any unrecorded aborted pass, which is exactly the residue
  § 3 of the billing report attributes to two aborted 30 August passes. Read
  the export on one basis throughout, and note that these older metas print
  list for realtime runs (the pre-2026-08-18 convention).

### 4.1 A discrepancy worth the PI's attention

`reports/billing-reconciliation-2026-09-11.md` line 104 prices "the grid
`verify_37`" as **913 candidates**, sharing a US$1.9 line with the 791-candidate
swap-37 verifier. The stage holds **3,319** result keys at `iterations: 1`
(`outputs/grid-2026-08-18/verifier/g384_ov192/verify_37/probabilities.json`,
`total_results: 3319`), of which 3,318 are unaccounted, and this report
estimates it at **US$3.95** rather than a share of US$1.9. The errata file and
the register belong to another agent this session; this is flagged, not
edited.

## 5. The auditor's third source

`scripts/audit_verifier_cost.py` now reads the register after the fixed merged
schema and the legacy backup convention:

- A register pass is priced at **its own** rate card and appears in the report
  as `register:git-blob:<blob>`, so every dollar traces to a blob hash.
- **Double-counting is refused.** A register pass whose `run_id` is already
  counted from a file on disc is skipped with a note. Register passes are
  never added to a stage carrying a merged (`meta_merge_schema`) meta, which
  already holds every pass.
- `residual_estimate` is reported as a note and **never** counted; the
  stage stays incomplete and the tool still exits non-zero.
- A register whose `schema` is not `verifier-meta-recovery/1` is ignored with
  a warning rather than mis-read.
- `--no-recovery-register` shows a stage as the working tree alone reports it.
- The sweep gained a class, `RECOVERED-FROM-GIT`. Its footer now reads, run on
  sapphire against the committed register:

  ```text
  stages with the cleanup-overwrite signature: 29 —
      RECOVERABLE 1, RECOVERED-FROM-GIT 17, UNRECOVERABLE 11
  ```

  The 11 are the nine of § 3 plus the two stages § 4.1 of the fix report
  recovered by **sibling adjudication**: the sweep still classes those
  UNRECOVERABLE because their evidence is a comparison of result keys, a
  judgement rather than a file, and deliberately stays manual. All three Pro
  stages now carry a figure instead of "not priced".

`--pass-file` was added for the explicit-file case the PI named: it prices any
set of metadata files as one stage, summed — a main-pass backup beside its
cleanup, or blobs extracted with `git cat-file blob <hash> > /tmp/pass.json`.
Its gate is the S144 swap-38 arm, whose two files sum to US$0.8469 when named
explicitly, the same figure the directory-mode audit reports.

## 6. `--temperature` now reaches the configuration gate

§ 2.2 of the fix report recorded a blind spot: a `--temperature` override
reached `build_generation_config` as a separate argument and never touched the
`configuration` block, so the gate — which fingerprints that block, and does
list `temperature` among `CLEANUP_GATE_FIELDS` — could not see a temperature
change between a main pass and its cleanup. It is closed.

`LLMMetadataTracker` takes `cli_overrides` and merges the
**configuration-valued** ones over the config file before building the block
it records:

```text
CONFIG_OVERRIDE_KEYS = ("temperature", "max_output_tokens", "thinking_level")
```

- `configuration.temperature`, `.max_output_tokens`, `.thinking_level` and
  `full_config_snapshot` are now the **effective** configuration — the file
  merged with the command line.
- `configuration.cli_overrides` lists what came from the command line, so the
  two are never confused. `cli_overrides` on the `cleanup_passes` entry is
  kept as it was.
- Every key in `CONFIG_OVERRIDE_KEYS` is in `CLEANUP_GATE_FIELDS` — asserted
  by a test, because an override that cannot block is an override the gate
  cannot see.
- `--model` keeps its own path (`model_override`), which records the
  SDK-resolved name rather than the typed one; `--service-tier`,
  `--iterations` and `--workers` are not configuration fields and are ignored
  by the merge.
- **A run with no overrides writes exactly the key set it always wrote** — no
  `cli_overrides` key, the same config object — which is a regression test.

Call sites: `scripts/run_pv.py` `_verify_realtime` (the realtime and cleanup
path), `_verify_batch`, and `_cleanup_configuration_gate`, which must build
its candidate block the same way the pass's own meta will be or the gate
compares unlike with unlike.

`scripts/4_detect_mounds_batch.py` **did not have the same shape**: it writes
`args.temperature` into `config["temperature"]` (lines 800–805 and 1403–1404)
before the tracker is built, so its `configuration` block has always recorded
the effective temperature. It now also passes `cli_overrides` for provenance —
an idempotent merge whose only effect is to record which values came from the
command line.

**Longer-term direction (the PI's).** Overrides belong in proper config files
rather than on the command line; at that point the merge becomes a no-op and
`cli_overrides` stops appearing. Recorded in the `LLMMetadataTracker`
docstring so the next reader of that code meets it there.

## 7. The Gemini 3.1 Pro rate card

The three Pro verifier stages ran **`gemini-3.1-pro-preview`** on
**2026-05-06** (the surviving cleanup passes; their batch main passes ran
2026-03-25 — § 3.2). The model id is read from
`outputs/h11/pv-diag-384/verified/*-pro-verifier/run.meta.json`,
`configuration.model`.

Read from **<https://ai.google.dev/gemini-api/docs/pricing> on 2026-09-14**;
the page states **"Last updated 2026-09-11 UTC"**. It prices the exact model
id `gemini-3.1-pro-preview` (and `-customtools`), per 1M tokens in USD:

| | ≤ 200K-token prompts | > 200K-token prompts |
|---|---:|---:|
| Input, standard | 2.00 | 4.00 |
| Output, standard (thinking billed as output) | 12.00 | 18.00 |
| Context-caching read | 0.20 | 0.40 |
| Cache storage | 4.50 per 1M tokens per hour | not tiered on the page |
| Input, batch **and** flex | 1.00 | 2.00 |
| Output, batch **and** flex | 6.00 | 9.00 |

Recorded as `RATE_CARDS["gemini-3.1-pro-preview"] = {2.00, 12.00, 0.20}` in
`scripts/audit_proposer_cost.py`, in the same style as the 3.7/3.8 entries,
with the long-prompt tier in a new `LONG_PROMPT_RATE_CARDS`. No pass in this
project approaches a 200K-token prompt — the largest verifier prompt is about
8.5K tokens — so `rates()` prices the ≤ 200K tier unconditionally; the second
table exists so a future long-context pass is not priced silently wrong.

**On the date the rates applied.** The page read today is dated 2026-09-11,
four months after these stages ran, and no archived copy of the official page
for May 2026 could be obtained (the Internet Archive availability API reports
no snapshot of that URL, and `web.archive.org` is not fetchable from this
environment). Two things make the rates safe to use anyway, and neither is an
assumption about price stability:

1. **The runs recorded the rates they were charged at.** Each stage's own
   `cost_estimate.pricing_used` block, written on 2026-05-06, reads
   `input_per_1m: 2.0, output_per_1m: 12.0` — the same figures the page
   carries now. The input and output rates are therefore anchored *at run
   time*, in-repo.
2. **The cache read rate cannot matter here.** It is the one rate the metas
   never recorded, and the cached share of all three stages is 0.000 (every
   crop is a distinct image), so no dollar in § 7's figures depends on it.

A third-party listing dated July 2026 also quotes 2.00/12.00 for this model,
which is corroboration and not a source this report relies on. The three
stages now price, at flex:

| Stage | items | audited US$ | its own `cost_estimate` |
|---|---:|---:|---:|
| `text-baseline-pro-verifier` | 21 | 0.106662 | 0.111588 |
| `pro-medium-image-baseline-pro-verifier` | 10 | 0.051040 | 0.053924 |
| `pro-high-image-1of5-pro-verifier` | 8 | 0.038726 | 0.041272 |

These are the *surviving* passes only. The audited figure is close to the
meta's own despite the 50 % flex discount, because the meta omitted thinking
tokens — 8,478 of them in the first stage against 3,027 output tokens — which
the audited basis bills at the output rate. That is the 2026-09-04 change to
`estimate_cost` acting in reverse on old metadata, and it is why these stages'
metas understate rather than (as flex alone would imply) double.

## 8. What did NOT change

- **No committed `run.meta.json` was rewritten.** The register sits beside the
  stages; every stage directory in `outputs/` is byte-for-byte as it was. The
  recovery script and the auditor are read-only on `outputs/**`.
- **No probabilities, detections, evaluations, or board cell moved.**
- **No git history was rewritten**, and nothing was `git reset`.
- **The fix report's § 4 census stands**: 29 stages, 3 recoverable from disc.
  This report re-classifies 17 of its 26 unrecoverable stages as recoverable
  *from history* — a new source, not a correction to its arithmetic. Its
  per-stage `audited` column was and remains the lower bound over what the
  working tree holds.
- **Nothing on sapphire was modified.** The history walk, the sweep and the
  register generation ran read-only in `~/Code/map-reader-llm`; the campaign
  worktrees (`claude-image55`, `claude-steward2`) and the other agent's
  (`claude-rulings`) were not touched.
- **The register, the boards, the errata file and `docs/paper/**` were not
  touched** — another agent owns them this session. § 4.1 is a flag for them.

## 9. Tests

All tier-1.

| Module | Tests | Covers |
|---|---:|---|
| `tests/test_audit_verifier_cost.py` | 19 existing + **16 new** | the register as a third source: a recovered pass closes the shortfall and is summed at its own rates; a pass already counted on disc is skipped; a residual estimate is noted and never counted; an unknown schema is ignored; an absent register is not an error; the sweep's new class; the committed register parses and every counted pass carries a blob source, positive tokens and a positive item count. `--pass-file`: the swap-38 pair sums to US$0.8469 from explicit files, and a missing file raises. The Pro card: standard rates, the flex halving that leaves the cache rate alone, the long-prompt table, and all three Pro stages pricing to their audited figures |
| `tests/test_cli_override_metadata.py` | **12 new** | the effective configuration (a `--temperature` override is recorded, listed under `cli_overrides`, and `None` is not an override); non-configuration overrides are not merged; every merged key is a gate field; **an override changes the fingerprint, the same override twice does not**; an override equal to the config value is not a change; each of the three merged keys blocks |

```bash
python -m pytest tests/test_audit_verifier_cost.py \
    tests/test_cli_override_metadata.py -m tier1 -q
```

## Changelog

### 2026-09-14 — Original publication

Written for the PI's first ruling of 2026-09-14 on
`reports/cleanup-meta-fix-2026-09-14.md` § 4's 26 unrecoverable stages, and
carrying that ruling's other two items (the `--temperature` gate blind spot,
the Gemini 3 Pro rate card).

New findings: 17 of the 26 stages' main passes survive as git blobs
(US$41.2226 of spend now audited); the fourth cell and its Gold Standard
calibration leg do **not** (the stage directories enter history already
overwritten); and the three Pro verifier stages never recorded their main
pass's tokens at all, because it ran through the Batch API — the overwrite
destroyed nothing there.

No prior numerical claim was revised. The two figures inherited from the fix
report, its § 4 census counts and the per-stage lower bounds, are reproduced
unchanged; the ≈ US$58 day-isolated fourth-cell figure from
`reports/billing-reconciliation-2026-09-11.md` § 3.1 is quoted and compared
with this report's US$69.24 estimate rather than replacing it (§ 3.1). One
discrepancy in that report is flagged for its owner (§ 4.1).

Commits: the recovery register and script, the auditor's third source and
`--pass-file`, the `cli_overrides` merge, and the Pro rate card — see the
branch's log.
