# Launch archaeology § 4: findings A to E, and how the register should represent them

Investigation of `reports/launch-archaeology-2026-10-04.md` § 4, items 2 to 5,
for the register repair (D30, D31). Read-only over the repository; session
archives read from `~/cc-archives/` (both project names); never
`~/.claude/projects`. Written 2026-10-04.

**Repository state.** I started at `b66307e96` (branch `register-repair`). During
the investigation another session committed `7360ba939`, `eb494f500`,
`7277f46b1` and `b715c2813`. The last two implement D34 (1) and (8), which
bears directly on finding A, so A is assessed against `b715c2813`. Code line
numbers below are at `b715c2813` unless a commit is named. Nothing in the
repository was modified. Scratch files: `sess_grep.py`, `estimates.py`,
`run-log-tiers-*.json`, `e47-*.txt` and `g37-window.txt`, all beside this report.

## Summary

| | Finding | Register consequence | Proposed representation | PI needed? |
|---|---|---|---|---|
| A | 2 committed `.txt` logs (16 rows). D34 (8) is now implemented at `7277f46b1` + `b715c2813`. Simulated: 14 of 16 rows resolve correctly; 2 pv-diag text rows do not | 12 n1-pro-rerun rows → audited (−US$5.853774); 2 pv-diag image rows → audited (US$0). Residue: 2 pv-diag text rows (−US$1.90594 once resolved) | Attestation A16 (already drafted), or attribute each log segment by its `Output:` line | Only which of the two |
| B | E71 rerun: 3 stages, 1,183 to 1,783 Gemini 3 Flash flex calls. No usage recorded anywhere, by construction | Not recoverable as rows. Invoice: **US$11.41** (A$16.504595 ÷ 1.4468), bracketed by a token model of US$8.51 to US$19.56 | Invoice-derived ledger entry (not D22: it is not superseded spend) | Yes: ledger home; whether to apportion. **Surprise**: about 3× the registered estimate |
| C | `pv-diag-384::pro-medium-{image,text}-baseline-*::run1`: usage is only a 2026-06-03 real-time resume (26 requests each); the batch marker comes from the March batch meta | Image: batch → standard, US$0.135529 → **US$0.195403** (+US$0.059874). Text: batch → flex, US$0.046666 unchanged. Both rows should read lower bound (March batch usage unrecorded) | A code rule, because **an attestation cannot override a batch marker** (tested). Plus `audited-lower-bound` overrides | Yes: the rule |
| D | `pv-diag-384::flash-high-image-n5-image-t0.0::run1`: first launch (454 tiles, 2026-04-16 08:11Z) never had a committed meta. The transcript keeps the runner's summary | Missing ≈ **US$5.387839** (standard); the row prices only the 33-request resume (US$0.644706) | `audited-lower-bound` override on the row, plus a transcript-reconstructed ledger entry | Yes: transcript evidence for usage, not only tier |
| E1 | e47 runs 4–5: 2 or 3 batch jobs abandoned, plus **1 that completed** (03:36:41Z 2026-04-09; its output is the archived "spurious zero-duration copy") | Completed job ≈ US$2.3 to 3.0, unrecorded. Abandoned jobs ≤ US$7.55 (≤ about US$9 with truncations), and if billed at all they were billed on Pacific 04-08 | Completed job: D22 ledger entry (null cost, estimate noted). Abandoned jobs: note with bound | Optional zero-cost `batches.get` check (API gate) |
| E2 | gemini37 run 2 flex recovery attempt (95 tiles, 07:16 to 08:35Z 2026-08-30) killed and deleted | ≤ US$0.124 at flex; zero completions observed at 07:30 and 07:41Z | Note only | No |

## A. The `.txt` run logs

### What is true

- **Exactly two committed `.txt` files exist under `outputs/`, and both are
  runner logs**: `outputs/h11/n1-pro-rerun-384/_run_log.txt` (338 lines; launch
  2026-06-03T05:39:33Z, 8 segments) and `outputs/h11/n1-pro-rerun-384/_topup_run_log.txt`
  (356 lines; launch 11:53:09Z, 8 segments). `git ls-files 'outputs/**/*.txt'`
  returns these two. `find outputs -name '*.txt'` returns the same two on the
  workstation and on sapphire (sapphire at `8ed4864cd`). No `.txt` under
  `outputs/` is a non-log today.
- The sweep's own `parse_log` reads each log as
  `tiers ['flex'], tier_lines 8, explicit_cache_lines 4`.
- **The 16 rows they cover.** `_run_log.txt` covers
  `n1-pro-rerun-384::pro-{text,image}-high-t0::run1-3` and
  `pro-{text,image}-medium-t07::run1`.
  `_topup_run_log.txt` covers `n1-pro-rerun-384::pro-{text,image}-medium-t07::run2-3`
  and `pv-diag-384::pro-medium-{text,image}-baseline-*::run2-3`.
  - Every text segment prints `Service tier: flex` and then
    `WARNING: Cache creation failed (... total_token_count=393, min_total_token_count=1024)`
    (for example `_run_log.txt:14-15`, `_topup_run_log.txt:14-15`).
  - Every image segment prints `Service tier: flex` and then
    `Context cache created: ... (14549 tokens, TTL=1h)` (`_run_log.txt:131-132`,
    `_topup_run_log.txt:95-96`).
  - Per-item signature: every text pass shows 0 cached tokens on all its
    requests; every image pass shows 14,549 on all of them.
- **As found (`b66307e96`).** `scripts/derive_tier_evidence.py:519` swept
  `rglob("*.log")` only. Entries are keyed by the log's parent directory (`:531`),
  with `explicit_cache` OR-ed across the directory (`:548`). `lib_pass_cost`'s
  `_log_evidence` walks up from a fragment's directory to the run directory.
  `cached-path` outranks every request record in `PIN_PRIORITY`
  (`scripts/lib_pass_cost.py:193`).
- **The naive change is wrong.** I simulated adding `*.txt` to that sweep in
  memory: all 12 n1-pro-rerun rows pin to standard by `cached-path`, the 6 text
  rows included. They inherit the run-level flag of a log that also records the
  image pools' caches, which overstates them by US$5.853774. The 4 pv-diag rows
  get nothing, because the top-up log sits in a sibling run's directory, outside
  their upward walk.
- **What `HEAD` now does.** `7277f46b1` sets `LOG_GLOBS = ("*.log", "*.txt")`
  (`derive_tier_evidence.py:147`, used at `:538`) and adds the cached-token
  signature. `b715c2813` (`lib_pass_cost.py:859-862`) exempts from the
  cached-path rule any fragment whose billed requests all report 0 cached tokens.
  Its commit message says the sapphire dry run hit the same text-row hazard.
- **Simulated against `HEAD`.** I rebuilt the schema-5 evidence in memory with
  `HEAD`'s `build_log_evidence` (126 logs on this clone; the committed schema-4
  sweep from sapphire scanned 152; the committed `run-log-tiers.json` is still
  schema 4) and re-priced with `HEAD`'s `PassCoster`:
  - n1-pro-rerun text, 6 rows: flex by `run-log-inherited`.
  - n1-pro-rerun image, 6 rows: standard by `cached-path`.
  - pv-diag image baseline run 2 and 3: standard by `cached-path` (signature).
  - **pv-diag text baseline run 2 and 3: still unresolved** (upper bound
    US$1.905592 + US$1.906288).
  - The two run 1 rows: still batch (finding C).

### Register consequence

- The 16 rows move from `audited-upper-bound` to `audited` once all resolve.
- n1-pro-rerun: from US$30.105534 to US$24.25176 (−US$5.853774). This matches
  the archaeology's 30.11 → 24.25.
- pv-diag top-up rows: text from US$3.81188 to US$1.90594 (−US$1.90594); image
  unchanged at US$6.007558.
- `HEAD` alone delivers −US$5.853774. The −US$1.90594 waits on the residue.

### Proposed representation

1. Keep `HEAD`'s mechanism, and close the residue in one of two ways:
   - **(a) Simplest:** apply drafted attestation **A16** (meta-scoped to
     `pv-diag-384/pro-medium-text-baseline/text-t0.0/run_[23]`, tier flex).
     D34 (8) allows hand attestations for the residue.
   - **(b) More general:** split a combined log at its
     `=== <ts> START ... ===` lines and attribute each segment to the parent
     directory of its own `Output: <path>` line. Each segment has exactly one
     such line, printed after its tier and cache lines (the runner prints it at
     `scripts/4_detect_mounds_batch.py:1099`). This keys tier and cache evidence
     to each pass's own directory: correct for both logs, no inheritance, and it
     reaches the sibling run.
2. **Residual risks to test:**
   - `TIER_LINE` (`derive_tier_evidence.py:130`) is unanchored and
     case-insensitive. A future prose `.txt` containing "service tier: flex"
     would count as a log. Anchor `^Service tier: ` for `.txt` files, or restrict
     them to `*log*.txt`.
   - The `uncached` exemption needs per-item records with every request at 0.
     A fragment with no `per_item_metadata`, or one with occasional implicit
     cache hits beneath a cache-logging directory, would still be pinned to
     standard. Under (b) neither case arises.
   - Regenerate on sapphire as the docstring says (152 versus 126 logs).

### Open question for the PI

(a) or (b) for the two remaining rows. Both give flex at −US$1.90594.

## B. The E71 rerun's own spend

### What is true

- **What it was.** The registered dead-tile recovery rerun (protocol errata E71,
  `docs/methodology/preregistration/protocol-errata.md` from line 3217, rider of
  2026-08-02; `reports/verification/recovery-rerun-registration.md`). Driver:
  `scripts/run_recovery_rerun.py` (`e8c2a5d0d`). It used the `--patch-tiles`
  path (`lib_batch_api.patch_failed_tiles` → `_retry_tile_sync`), all calls
  `gemini-3-flash-preview` with `service_tier="flex"`. It ran on **amd-tower**,
  not sapphire. Session: `~/cc-archives/vlm-burial-mound-detection/2026-07-30T00-59_execute-family-fdr-registration-land-errata`
  (archived only under the alias name).

  | Stage | Launch (UTC) | Results written (UTC) | Pacific day | Scope | Outcome |
  |---|---|---|---|---|---|
  | Pass 1 (3 + 3 ladder) | 04:41:25Z (`toolu_01CSaJp1NXcwZ919DFwCvjU5`) | 05:24:13Z | **2026-07-29** | 288 tiles, 15 passes | 245 + 10 safe-mode recovered, 33 failed |
  | Sweep A (10 + 10) | 07:30:29Z, relaunched 07:33:32Z | 08:09:27Z | 2026-07-30 | 33 tiles | +10 recovered |
  | Sweep B (5 + 5 at 1,024) | 08:09:56Z | 08:26:09Z | 2026-07-30 | 23 tiles | 0 recovered |

  The 07:30:29Z launch was relaunched three minutes later "with fixed suffix
  arg". Whether it made any API calls is unverified (probably none).
  Commits: `99ae28ec4` (pass 1), `d01ea4412` (sweeps), `bff914c02` (close-out).
  The archaeology's "2026-07-30" is the UTC date; the spend falls on **two
  Pacific days**.
- **Passes re-run.** These 15 (`flash35-pv-2x2::...::run3` dropped out,
  registration § 1):
  - `e47-propose-brief::propose_brief-text::run4`;
  - `h12-v2::r3-hp-heavy::run3` and `::run5`;
  - `n1-outstanding-384::pro-{image,text}-high-t0::run1-3` (all Flash, per the
    registration's 2026-07-30 correction);
  - `pv-diag-384::flash-high-{image,text}-n5-*-t0.0::run1-3`.
- **No committed file records any of its token usage.**
  - The 15 metas carry 22 `recovery_history` entries (pass 1 at 04:54 to
    05:24Z, sweep A at 07:42 to 08:09Z), all with `recovery_cost_usd: 0.0` and
    `recovery_run_id: null`.
  - Every `per_item_metadata` timestamp is from the launch day (March or
    April). Sweep B recovered nothing, so it left no trace in any meta.
  - **Mechanism:** at `99ae28ec4`, `_retry_tile_sync`
    (`scripts/lib_batch_api.py:1138`) returns only `response.text` and discards
    `usage_metadata` (return dict at `:1257`). `patch_failed_tiles` merges a
    fresh meta with `total_cost_usd: 0.0` and no `usage_stats` (`~:2310-2350`).
    **`HEAD` is unchanged**: no usage capture in `_retry_tile_sync`
    (`lib_batch_api.py:2258` onwards). Any future `--patch-tiles` use will be
    unmetered too.
  - The results files `reports/verification/recovery-rerun-results{,-deep,-deep-b}.json`
    hold tile outcomes only.
  - The driver logs went to `/tmp/claude-1000/.../a72a9a25-.../scratchpad/*.log`
    on amd-tower and no longer exist (checked).
  - There are no `run_N_recovery` directories and no batch results.
- **Invoice.** July 2026 cost table (`docs/costs/`, gitignored), project
  `map-reader-llm`, invoice rate 1.4468. Gemini 3 Flash is the only Gemini
  model billed:

  | SKU | Tokens | A$ (unrounded) | Usage window |
  |---|---:|---:|---|
  | output, text, flex | 6,272,963 | 13.613099 | 07-26 → 07-31 |
  | input, image, flex | 6,279,100 | 2.271057 | 07-26 → 07-31 |
  | input, text, flex | 722,101 | 0.261162 | 07-26 → 07-31 |
  | cached input, image | 4,831,901 | 0.349521 | **07-29 → 07-30** |
  | cached input, text | 134,939 | 0.009756 | **07-29 → 07-30** |

  - Total A$16.504595 ÷ 1.4468 = **US$11.4077**
    (`reports/billing/gemini-spend-by-sku.csv` rows 93-97 round to US$11.41).
  - There are no day exports for July.
  - The cached lines' window is exactly the rerun's two Pacific days.
  - The flex lines' wider window (07-26 → 07-31) implies some other Gemini 3
    Flash flex use. **Unidentified:** no other launch in the map-reader sessions
    of 07-25 to 08-01. The personal-assistant bake-off calls of 07-28 used 3.5
    and 3.6 Flash, which are not on this invoice.
  - The rerun loaded its API key from `~/personal-assistant/.env`. Its billing
    project rests on the timing match (unverified directly).
- **Token model** (`estimates.py`):
  - Calls are bounded from the results files and the patcher's ladder:
    1,183 to 1,783 (image 616 to 892, text 567 to 891).
  - Per-call loads come from the pre-recovery metas: 15,659 input per image
    request, about 1,500 per text request, 8,178 output plus thinking per
    truncated call against an 8,192 cap.
  - Priced at flex (US$0.25/M fresh, US$0.05/M cached, US$1.50/M output): pass 1
    US$3.03 to 11.47, sweep A US$3.79 to 5.96, sweep B US$1.70 to 2.13. Total
    **US$8.51 to 19.56**.
  - The invoice's US$11.41 sits inside this range, near the low end (most
    recoveries took one attempt). Invoice input (11,968,041) is consistent with
    the low-end call count.

### Conclusion and register consequence

The spend is **not recoverable as register rows**: no usage was ever captured.
It is recoverable only as an invoice-derived figure, **US$11.41**.

- It is an upper bound if the unidentified other-day flex use is real; the
  model puts the rerun alone at no less than US$8.51.
- Tier flex. Pacific 2026-07-29 (pass 1) and 2026-07-30 (sweeps).
- Separately, the 15 fragments carry `priced_at: 2026-07-30`, the E71 end date,
  though their usage is from March and April. The rate card has one row for
  `gemini-3-flash-preview` (from 2025-12-01), so the price does not move;
  D34 (5) already holds their billing-day evidence to the launch day.

### Proposed representation

A ledger entry beside D22's, but **not in `superseded-executions.json`**: the
rerun completed these passes' coverage rather than being superseded. A small
"unmetered executions" ledger (or a new `kind` in the D22 ledger) would hold:

- basis `invoice-derived`, US$11.41 (A$16.50 at 1.4468);
- the token-model bracket;
- tier flex, both Pacific days;
- evidence citing the commits, results files and invoice lines above.

The project total (WP6) adds it. Do not apportion it to the 15 pass rows: any
split would be modelled, not measured. The frontier (D19) is unaffected; this
is operational retry spend, like the unrecorded retries everywhere else
(`reports/token-load-audit-2026-06-12.md` § 8).

### Flag (research calibration)

The registration estimated US$2 to 4 (worst case US$5). Its changelog says
"spend for both sweeps well under US$1"
(`recovery-rerun-registration.md`, deep-sweep changelog). The invoice says about
US$11.41, and the model puts the sweeps alone at US$5.49 to 8.09. The
estimate's per-tile basis missed that every failed attempt burns about 8,178
thinking tokens.

### Open questions for the PI

- Where should the ledger live?
- Should the registration's spend statements be corrected under the revision
  policy?
- Should `_retry_tile_sync` be fixed to record usage?

## C. The two pv-diag rows priced as batch

### What is true

- **Rows:**
  - `pv-diag-384::pro-medium-image-baseline-image-t0.0::run1`: one fragment
    (`.../image-t0.0/run_1/detections_image-t0.0_run01.meta.json`), tier batch,
    method `batch-marker`, cost US$0.135529.
  - `pv-diag-384::pro-medium-text-baseline-text-t0.0::run1`: one fragment
    (`.../text-t0.0/run_1/detections_text-t0.0_run01.meta.json`), tier batch,
    method `batch-marker`, cost US$0.046666.
  - Both cite `batch-marker: ... batch_api block -> batch` and a billing-day
    line ("resumed over 2026-03-23..2026-06-03 ... standard|flex"), and both
    record the **conflict** "batch-marker pins batch but billing-day ... standard|flex".
- **Meta evidence.**
  - The original executions were Batch API runs on 2026-03-23
    (`lib_batch_api.py` 1.5.0 at `2f425fc8a`). At their first commit
    (`3d22184d6`) their `usage_stats` are all zero, there is no
    `per_item_metadata`, and duration is 0.000235 s.
  - The 2026-06-03 resume (`c07c57766`; session
    `~/cc-archives/map-reader-llm/2026-06-03T06-59_complete-n-1-baseline-matrix-re-score`,
    identical under the alias) ran on the workstation:
    - text at 12:25:05Z (`toolu_01Csj9ueNThKn9bZeEcWjCeP`);
    - image at 12:26:33Z (`toolu_019jY8Ux3SMWngL1T3kX32rU`);
    - both
      `4_detect_mounds_batch.py ... --mode realtime --service-tier flex --use-cache --max-retries 15`.
  - The merged metas' `usage_stats` are **only the resume's 26 requests each**
    (`request_count: 26`; per-item timestamps 12:25:08Z text and 12:26:39Z
    image). Text shows 0 cached on all 26; image shows **14,549 cached on all 26**,
    the explicit cache. The cached-path fix `2df65047e` is from 2026-10-03.
  - The 2026-06-03 day export (filter "unverified") bills 3.1 Pro at standard
    and flex, **no batch**.
- **Correct tiers and costs** (`lib_cost.price_usage`, 3.1 Pro, 2026-06-03):
  - text flex = **US$0.046666**: unchanged, because flex and batch rates are
    equal for 3.1 Pro (`data/pricing/gemini-rate-card.json`);
  - image standard (cached path) = **US$0.195403**, against batch or flex at
    US$0.135529 (**+US$0.059874**).
- **Mechanism.**
  - `direct_evidence` adds a `batch-marker` whenever `meta.get("batch_api")`
    (`lib_pass_cost.py:804`). The `batch_api` block was inherited from the March
    batch meta through the resume merge.
  - `batch-marker` ranks second in `PIN_PRIORITY` (`:193`), above `cached-path`
    and `attestation`.
  - The batch marker also exempts the fragment from the cached-path rule and
    from the new cached-token signature (`BATCH_KINDS` clause, `:861`).
  - **Tested:** a scratch meta-scoped attestation (flex for text, standard for
    image) leaves both rows at batch with a "pins disagree" conflict.
  - The `HEAD` simulation in A confirms the signature does not reach the image
    row either.
- **Scope check.** Of the register's 7 batch fragments, only these 2 carry
  real-time recovery usage. Of all proposer rows, only these 2 and D's row show
  `n_tiles_processed` exceeding `n_tiles_dispatched` by 20 or more (487 against
  26). Their March batch executions are unrecorded like the 145 `unrecorded`
  pv-diag rows, yet the rows read `audited`.

### Register consequence

+US$0.059874 (image). The text row's label changes but its cost does not. Both
rows also understate the pass, because the March batch execution of about 461
tiles each is unrecorded (D12).

### Proposed representation

1. **A code rule, not an attestation.** For example: a `batch_api` block is a
   batch marker only when the meta has no real-time records. If
   `per_item_metadata` exists alongside `recovery_history` and
   `tpm_governor_recovery` (the runner's real-time governor), the usage is the
   real-time resume's, so the marker should not pin. Then
   `cached-path`/signature (image → standard) and the 2026-06-03 run-log
   evidence (text) can resolve. A meta-scoped attestation of flex could pin the
   text row once the marker no longer outranks it.
2. Add `cost-overrides.json` entries with basis `audited-lower-bound` for both
   pass ids (supported at `lib_pass_cost.py:1239`). The source text should say
   the 2026-03-23 batch execution recorded no usage.
3. A drift test: proposer rows where `n_tiles_processed − n_tiles_dispatched` is
   large signal unrecorded executions. Today exactly these 3 rows.

### Open question for the PI

Approve the rule in item 1 (or an alternative), and the lower-bound label for
the two rows.

## D. image-t0.0 run 1's first launch

### What is true

- **Pass:** `pv-diag-384::flash-high-image-n5-image-t0.0::run1`
  (`outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/run_1/`), 3 Flash,
  HIGH thinking, T 0.0.
- **First launch.** 2026-04-16T08:11:47Z on sapphire, via
  `scripts/run_phase3a_image_matrix.sh` (session
  `~/cc-archives/map-reader-llm/2026-04-16T05-56_b089991e`,
  `toolu_016sukiS8qtSEe8MWjj58D2w`; log `/tmp/phase3a-image-matrix.log`).
  - Head, read at 08:13:53Z: `Service tier: flex`, then
    `Context cache created: cachedContents/olf84bem... (14549 tokens, TTL=1h)`.
  - **Runner summary, read at 08:27:19.949Z** (`toolu_01PWdid5PNMDjG2P8uWQ6FbL`):
    `Tiles processed: 454 / Tiles failed: 33 / Total detections: 788 / Tokens used: 9,213,695 / Estimated cost: $4.0055`.
  - The relaunch at 09:22:24Z resumed with "Resuming: 454 tiles already
    processed ... Processing 33 new tiles". Its segment meta (33 requests,
    09:22:26 to 09:35:58Z) replaced the first launch's meta **before the first
    commit** (`2e8cc6481`, 2026-04-16T14:20:49Z). The tracked meta has never
    held the first launch.
  - The sapphire `/tmp` logs are gone (sapphire booted 2026-09-05).
  - **No committed file records the first launch's usage.**
- **Reconstruction from the two transcript figures** (`estimates.py`):
  - The runner's estimator is input × US$0.50/M plus output excluding thinking
    × US$3/M. Checked on run 2: 7,625,933 × 0.5/M + 64,312 × 3/M = 4.005903,
    against its recorded 4.005902.
  - The first launch has 487 per-item records (454 completed plus 33 failed),
    each at 15,659 input including 14,549 cached, as in run 2 and run 3.
  - Result: input 7,625,933 (cached 7,085,363), output 64,178, thinking
    1,523,584. Compare run 2 (64,312 / 1,545,495) and run 3 (64,314 / 1,544,296).
  - Priced (`lib_cost.price_usage`, 2026-04-16): **standard US$5.387839**
    (cached path: the transcript's cache line, D34 (1) and (3)); flex
    US$2.871054.
  - Rounding of $4.0055 moves output by ±17 tokens: no change at 6 decimal
    places.
  - As everywhere in the register, this excludes retries. The governor showed
    ≥952 requests at 14:05 into the run; run 2's governor records 963 requests
    and 20.58 M tokens against 9.24 M in `usage_stats`.
- **Current row:** `audited-upper-bound` US$0.644706 for the 33-request segment
  (the same at standard), `n_tiles_processed` 484 against `n_tiles_dispatched`
  33.

### Register consequence

The pass is short by about **US$5.39** (standard), roughly 89 % of its own
spend. Its true cost on the register basis is about US$6.03.

### Proposed representation

It cannot be a register fragment: there is no meta, D14 forbids editing
historical metas, and a synthetic meta would be fabricated data.

- **Recommended:** a `cost-overrides.json` `audited-lower-bound` entry for the
  pass, plus a ledger entry (the same "unmetered" ledger as B), basis
  `transcript-reconstructed`, US$5.387839 standard, citing the session, tool
  ids and arithmetic. The figure is the pass's own spend, not superseded.
- **Alternative:** a new override basis that adds the reconstruction to the
  row's own cost.

### Open questions for the PI

- Is transcript evidence acceptable for **usage** (D34 (3) ruled only on tier
  and commit)?
- Ledger only, or added to the pass's cost?

## E. Possibly unregistered spend

### E1. e47 runs 4–5 Batch API jobs

Session `~/cc-archives/map-reader-llm/2026-04-07T23-44_automated-mound-detection-pipeline`.
All times UTC, on 2026-04-08 and 04-09.

- **Two overlapping submit loops**, neither of which cancelled jobs (no cancel
  or signal handling in `lib_batch_api.py` or `4_detect_mounds_batch.py` at
  `ed04977d6`):
  - Loop `b696g16k1` (12:39:33Z, runs 2–5 sequentially). Runs 2 and 3
    completed. Its run-4 job **`batches/ta2p44lj7ym24euqp52xo67ohncrha7wm8ua`**
    (submitted about 21:17Z) was still `JOB_STATE_PENDING` at 22:15Z when its
    poller (PID 1234171) was killed and `run_4/` and `run_5/batch_working`
    deleted (22:16:53Z). The loop went on to run 5 (PID 1263410, 22:16Z).
  - Loop `bqkbtf9t9` (22:17:12Z, runs 4 and 5) submitted run 4 (PID 1263649).
    Its output was polling **`batches/z3yhm81fy9wjnp3xrcakrbfro01jaa7lxmuu`**
    (pending) at 23:42Z.
  - Both PIDs were killed at 23:45:16Z, and runs 4–5 relaunched real-time flex
    at 23:51:13Z.
  - **But `bqkbtf9t9` then ran its run-5 iteration in batch mode and completed
    at 2026-04-09T03:36:42Z, exit 0.**
- **That job completed and was billed.** Its output is the trio archived by
  `ad87e55fa` as a "spurious zero-duration copy"
  (`archive/reorg-artifacts/e47-propose-brief-run5-zero-duration-copy/`; first
  committed in `52b0215a6`). Its meta has:
  - `timestamp.start` 2026-04-09T03:36:41.716Z, one second before the loop's
    completion notice;
  - `execution_mode: batch`, `lib_batch_api.py` 1.5.0;
  - 447 completed and 40 failed items, 1,403 detections, zero usage.

  The 0.0002 s "runtime" is that batch writer's timestamp artefact (the pv-diag
  March batch metas show 0.000235 s). **The archive README's diagnosis ("not a
  real run", "reorganisation artifact") is wrong.** This trio is also the
  "second filename convention" behind E71's 2026-09-08 rider (i): the April e47
  consensus double-read.
- **Abandoned jobs:** `ta2p44lj7...` and `z3yhm81fy9...`, and run 5's first
  submission (PID 1263410; id not captured), unless `bqkbtf9t9`'s run 5 resumed
  that job, which is unverified. So 2 or 3 jobs, cancellation never confirmed.
- **Billing.**
  - The April cost table bills Gemini 3 Flash at batch **only on Pacific
    2026-04-08** (usage start and end both 04-08).
  - Across all invoices, Flash-batch windows are 02-14..15, 03-07..25, 04-08
    and 09-19 (`data/pricing/billing-day-tiers.json`, intervals).
  - The day exports show Pacific 04-09 flex only and 04-10 standard only.
  - So any of these jobs that ran was billed on Pacific 04-08 (before 07:00Z on
    04-09); none was billed later in April or in May to August.
  - Pacific 04-08's batch volume (39.7 M output) is shared with e47 runs 2–3
    and the 55-map generalisation pass-1 batch chunks, all zero-usage metas, so
    it cannot isolate them.
- **Size** (`lib_cost.price_usage` on the committed flex run 5's usage: 744,136
  input, 110,389 output, 1,444,336 thinking; batch rates equal flex for 3 Flash):
  - one full pass = **US$2.518121**;
  - the completed job ≈ **US$2.31 (447/487) to about US$3.0** (if its 40
    failures were billed truncations at about 8,178 tokens);
  - abandoned jobs: ≤ 3 × US$2.52 = **US$7.55** (≤ about US$9 with
    truncations), and possibly US$0 (expired unprocessed).

**Representation.**

- The completed job goes in the D22 ledger
  (`data/pricing/superseded-executions.json`, which allows null where usage is
  absent): meta = the archived run05 meta, `superseded_by`
  `e47-propose-brief::propose_brief-text::run5`, kind "batch job completed
  after the run was relaunched on flex", `cost_usd: null`, with the estimate in
  the evidence.
- Correct the archive README.
- The abandoned jobs get a note with the bound, not a figure.
- **Optional:** `client.batches.get()` on the two captured names would show
  their terminal states at no token cost. It is still an API call under the
  approval gate, and records this old may have been purged (unverified).

### E2. gemini37 run 2 flex recovery attempt

Session `~/cc-archives/map-reader-llm/2026-08-29T02-01_launch-gemini-3-7-55-map-campaign-and`
(sapphire). Times UTC, 2026-08-30.

- **Timeline.**
  - Launched 07:16:36Z (`toolu_01DPmd4hhveJkqNXJbtcj3es`): 95 missing tiles,
    `--mode realtime --service-tier flex --workers 95`, output piped through
    `tail -3`, so there was no log file.
  - At 07:30:03Z and 07:41:20Z its directory held only `experiment_intent.md`.
  - At 08:35:00Z it was killed and the directory deleted; again at 08:35:21Z
    before the standard relaunch.
- **What the empty directory means.** The runner saves its GeoJSON after every
  successful tile (`4_detect_mounds_batch.py:1253-1255` at `9d4d9ef74`), so
  there were zero completions by 07:41Z. 07:41 to 08:35Z was unobserved. The
  failures were flex 503 storms; run 2 itself logged 30,545 server-error
  retries. 503s are not billed (unverified for this API; standard practice).
- **Exposure:** at most the 95 tiles once at flex. The standard replacement's
  committed usage (142,690 input, 4,894 output, 32,855 thinking) prices to
  **≤ US$0.124288** at flex. Most likely about US$0.
- Pacific 08-30's flex volume cannot isolate it: 148,607,532 input and
  29,217,899 output at flex (a "documented" export), so 95 tiles are under
  0.1 %. The day's standard volumes (168,514 / 46,705) match A69's four
  standard fragments to the token without it.

**Representation:** note only, with the bound. This is not a ledger figure.

## Surprises and items for the PI, in order of weight

1. **The E71 rerun cost about US$11.41**, roughly 3× its registered worst case,
   against the registration's "sweeps well under US$1". The patch path still
   discards usage at `HEAD`.
2. **The e47 "spurious zero-duration copy" is a genuine billed batch
   execution.** The archive README is wrong, and the job's existence explains
   E71 rider (i).
3. **An attestation cannot correct a batch-marker row.** C needs a code rule;
   the new cached-token signature does not reach it either.
4. **D34 (8) as first implemented would have mis-priced the 6 n1-pro-rerun text
   rows.** `b715c2813` fixes them. Two pv-diag text rows remain for A16 or
   segment attribution.
5. **Three rows read `audited` or upper-bound while pricing a fraction of their
   pass:** D (33 of 487 requests) and C (26 of 487 each). A
   coverage-versus-dispatched drift test would catch these.
6. For D: is transcript evidence acceptable for usage? For B and D: where does
   the "unmetered executions" ledger live?

## Changelog

### 2026-10-04 — Original publication

Scratch report for the session's lead; not in the repository's revision-policy
scope.
