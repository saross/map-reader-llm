# The passes register repair (D30-D41)

> **Last revised**: 2026-10-05 (original publication, Session 160). See
> [§ Changelog](#changelog) for revision history.

**Status: built on branch `register-repair`, for audit and PR.** The PI ruled
D30 on 2026-10-04 (the register MUST be repaired) and D31-D41 during this
session (`planning/pi-decisions-2026-09-20.md`); D40 is open.

## 1. What was wrong

The passes register (`results/passes-manifest.json`) is the project's
as-billed record of every API pass. Three gaps were known when D30 was ruled:
the S104 vote-3 increments, the `verifier-robustness` run, and
`grid-2026-08-18`'s proposer passes. Looking for their cause found more:

- **A silent skip.** The extractor dropped a verifier hint that resolved to
  no meta without a word. `verifier-robustness`'s eight hints stopped one
  directory short of `.../verified/run.meta.json`, so US$51.44 never reached
  the register.
- **37 more real legs outside it** (D31), listed by the WP4 sidecars:
  Era-1 Stage D, the D8 replicates, the GS calibration legs, the `-v2`
  legs (corrected verifier configurations, not identical re-runs: tracker
  C-19), the WBF legs and others, about US$61.89.
- **188 upper-bound rows** whose tier the committed evidence could not pin
  (the launch-command archaeology, `reports/launch-archaeology-2026-10-04.md`).
- **734 archive metas with usage** that neither the register nor the sidecars
  had ever read (D38).

## 2. What changed

| | Before | After |
|---|---:|---:|
| Register rows | 1,339 | 1,431 |
| Register total (as billed) | US$3,094.05 | US$3,108.61 |
| `audited` rows | 312 (US$2,434.08) | 579 (US$3,073.22) |
| `audited-upper-bound` rows | 188 (US$642.04) | 8 (US$14.66) |
| `audited-lower-bound` rows | 27 (US$0.96) | 33 (US$3.76) |

The total moves little because the new spend (about US$146) is almost offset
by the 188 upper bounds resolving downward (US$642.04 high to US$510.12).

**Extraction (D30-D32, D38, D41).** 92 new rows: D30's three gaps (51 rows,
US$77.19), D31's other legs (35 rows, US$61.89), and the archive's six real
legs (h10's pool_160 cold-start mining passes, US$6.92; a 2026-04-10
verifier cleanup, US$0.02). New extractor mechanisms, each tested with a red
sentinel: `repo_path` for a leg outside its run's tree (verifier and proposer),
`single_pass` for a flat pool, `run_N/retry/` folds (spend, never coverage),
and a warning plus a drift guard for any hint that resolves to no meta.

**Tier evidence (D34, D36).** The log sweep reads `*.txt` and records every
explicit-cache size a log prints; the coster reads the per-request
cached-token signature at a logged size only (implicit caching hit every
request of image-b's no-cache recoveries at 16,272 tokens). Requests with no
cached token retire a directory's logged cache; a `batch_api` block carried
by a real-time resume merge pins nothing. 84 of the 188 rows now derive
their tier; 54 attestations cover the transcript-only residue.

**Pricing corrections.** One carry-forward rule for the register and the
sidecars (the 3.7 screen's recovery-fixed legs); verifier candidates counted
per fragment, preferring successful responses to requests (20 rows; T03's
count now equals its results, 9,910); pv-384's v1-prompt main leg restored
from git (D37).

**Ledgers for the project total (WP6).** D22's superseded ledger gains two
executions (US$1.22). A new unmetered-executions ledger (D35) carries spend
that left no usage record, by derivation: US$26.73 estimated, US$7.68 of
exposure bounds. A generated archive ledger (D38) prices the archive's 687
superseded metas at about US$361 (20 unpriceable: models not on the rate
card); the zero-usage tail is WP6's invoice residual (D39).

**Frontiers (D30, D33).** The tile-presence legs move to their register
rows at unchanged cost; the r2 board's TH7, T03 and TM oracle cells add their
vote-3 increments (US$2.97, US$2.74, US$1.51); no frontier membership changes.

## 3. Findings worth keeping

- The E71 recovery rerun cost about US$11.41, three times its registered
  estimate; the patch path still discards usage.
- The archive's "spurious copy" of e47 run 5 was a real, billed batch job.
- Runner estimates of February-March understate their spend about four times
  (US$0.10/0.40 rates for Gemini 3 Flash).
- `analyses-manifest.json` had lacked D25's second signature note since
  `1c5e8fb84`: no guard checks the generated manifests against their inputs.

## 4. Open

- D40: the Phase 1 library and Experiment E (and two related groups) are
  being investigated for registration consistent with similar runs.
- Eight newly extracted March legs were upper bounds. The three WBF legs are
  now flex by D21's precedent (A73-A75, accepted by the PI 2026-10-05); the
  five `pv-384`/`pv-512` `-v2` legs remain upper bounds, with which set the
  conditions should cite still open.
- 20 archive metas need rate-card entries (3 Pro preview, 3.1 Flash-Lite,
  Flash-latest, 2.5 Flash) under D18 before they can be priced (accepted,
  low priority).
- Done 2026-10-05 on the PI's acceptance: `baseline-single-pass` names its own
  pool; the E71 registration records the actual spend; the sync patch path
  records its usage (the in-batch retries do not yet: tracker W6.5); the two
  abandoned e47 batch jobs were looked up, both purged (U4 stays a bound).

## Changelog

### 2026-10-05 — Original publication (Session 160)

Written during the repair, before the PR's audit; figures from the trial
regeneration on sapphire.
