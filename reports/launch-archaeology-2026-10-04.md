# Launch-command archaeology: the billed tier of the 188 upper-bound passes

> **Last revised**: 2026-10-05 (§ 5 ruled as D34 and applied in the
> Session 160 register repair; § 4 dispositions in § 6). See
> [§ Changelog](#changelog) for revision history.

**Status: RULED and APPLIED.** The PI ruled § 5 as recommended (D34,
`planning/pi-decisions-2026-09-20.md`). The register now derives 84 of the 188
rows from machine-readable evidence (D34 (1) and (8)), and the residue's 54
attestations are in `data/pricing/tier-attestations.json`; all 188 re-extract
as `audited` at the proposed US$510.12. The 69 drafts stay in
[`launch-archaeology-2026-10-04-proposed-attestations.json`](launch-archaeology-2026-10-04-proposed-attestations.json)
as proposed; see § 6.

## 1. The question

The passes register (`results/passes-manifest.json`) prices each pass as
billed. 188 rows have `cost_basis: audited-upper-bound`: their served tier
could not be pinned by the committed evidence, so they are priced at the
highest candidate tier (standard), with `cost_source.bounds_usd`. Total:
high US$642.04, low US$407.79, gap US$234.24 (S158's figures, reproduced).
This is item 4 of S158's close, the as-billed honest total. The frontiers
are unaffected: they price every configuration at the uniform tier (D19).

## 2. Result

Every one of the 188 rows resolves to one billed tier per fragment, at high
confidence, from launch commands in the session archives (`~/cc-archives/`,
both project names), committed logs, the per-request cached-token
signature, the code at each recorded commit, and the invoice's per-day
volumes. **Proposed as-billed total: US$510.12** (US$131.92 below the
published high, US$102.33 above the low). Re-priced through the project's
own `PassCoster` with a scratch attestation file: all 188 rows come back
`audited`, with no conflict.

| Run | Rows | Classification | High | Low | Proposed |
|---|---:|---|---:|---:|---:|
| pv-diag-384 | 127 | standard 55, flex 72 | 363.82 | 192.55 | 255.52 |
| n1-outstanding-384 | 7 | standard 6, flex 1 | 34.29 | 17.68 | 33.81 |
| image-b-gs-2026-08-28 | 16 | standard 5, mixed 9, flex 2 | 86.10 | 70.59 | 76.95 |
| n1-pro-rerun-384 | 12 | standard 6, flex 6 | 30.11 | 19.30 | 24.25 |
| proposer-verifier-384 | 8 | standard 8 | 15.22 | 7.61 | 15.22 |
| e47-propose-brief | 2 | flex 2 | 9.95 | 4.98 | 4.98 |
| h12-v2 | 4 | standard 4 | 9.36 | 5.30 | 9.36 |
| h8-v2 | 2 | flex 2 | 3.55 | 1.78 | 1.78 |
| h7-escalation-2026-08-28 | 6 | flex 6 | 2.74 | 1.37 | 1.37 |
| gemini37-55map-2026-08-29 | 3 | mixed 3 | 86.69 | 86.54 | 86.69 |
| proposer-verifier-512 | 1 | standard 1 | 0.20 | 0.10 | 0.20 |
| **Total** | **188** | **standard 85, flex 91, mixed 12** | **642.04** | **407.79** | **510.12** |

## 3. What decides each tier

- **The cached-path defect covers every explicit-cache image run from April
  to August.** Until `2df65047e` (2026-10-03) the runner's cache-call
  `GenerateContentConfig` carried `cached_content` but not `service_tier`
  (at `b57cf6c22`, the pv-diag launch commit, the block sets only
  `cached_content`; `service_tier` is set on the main path alone). Such a
  run printed `Service tier: flex` and was billed at standard. Checked: the
  fix is an ancestor of none of the recorded commits.
- **`--use-cache` alone proves nothing.** When cache creation fails the
  runner falls back to the main path, which carries the tier. The text
  config (`detect_brief-text`) always fails ("Cached content is too small",
  393 tokens against a 1,024 minimum; committed in
  `outputs/h11/n1-pro-rerun-384/_run_log.txt`), so text runs launched with
  `--use-cache --service-tier flex` were billed at flex.
- **The cached-token signature.** An explicit cache reports its exact size on
  every request: `pv-diag-384::flash-high-image-n5-image-t0.3::run2` shows
  14,549 cached input tokens on all 487 requests; the matching text pass
  shows 0 on all 487 (both checked 2026-10-04).
- **Verifier scripts.** `run_pv.py` forwarded `--service-tier` from
  `2a2cd81c7` (2026-04-09) with no cached path. `5_verify_crops.py` had no
  tier option until `9932dbe46` (2026-09-21), so its legs were standard.
- **Invoice volumes agree.** After flex arrived, the invoice billed Flash at
  standard only on Pacific 04-14 to 04-17 and 08-27 to 08-28, and Pro only on
  06-02 to 06-03: exactly the days of the explicit-cache image runs.
  Pacific 08-27 is the one tight day (flex 0.75 % over billed, on a linear
  time split of a verifier leg that crosses midnight).

Per-run evidence, with session directory, UTC time and command excerpt for
every launch and recovery, is in each draft attestation's `evidence` field.

## 4. Findings beyond the tier question (for the register repair)

1. **The cached-path defect forfeited the flex discount on every explicit-
   cache image run** (pv-diag 55 rows, h12-v2, n1-pro-rerun, image-b):
   caching meant to save money cost the 50 % flex discount instead.
2. **The run-log sweep misses committed `.txt` logs.**
   `scripts/derive_tier_evidence.py` reads only `*.log` (`rglob("*.log")`,
   line 519), so the two n1-pro-rerun logs, the only machine records for 16
   rows, were never read.
3. **The E71 rerun's own spend (2026-07-30, flex) appears nowhere in the
   register**: 15 metas show `recovery_cost_usd: 0.0`, `recovery_run_id:
   null` and launch-day usage only.
4. **Two pv-diag rows look mispriced as batch**: the pro-medium baseline
   run 1 rows carry a batch marker, but their metas include a 2026-06-03
   real-time resume (text flex, image cached so standard); the day's
   billing shows no batch for 3.1 Pro.
5. **Possibly unregistered spend**: image-t0.0 run 1's first launch (454 of
   487 tiles) is unregistered (E71 defect 3); e47 runs 4–5's Batch API jobs
   were abandoned, not confirmed cancelled; a killed gemini37 run 2 flex
   recovery attempt's directory was deleted rather than archived.

## 5. Decisions for the PI

1. Is the per-request cached-token signature (every request reporting the
   explicit cache's exact size) enough to establish the cached path when
   that pass's own "Context cache created" line did not survive? (Decides 51
   pv-diag image passes, image-b and h12 r3; the draft treats it as
   decisive.)
2. Should `--use-cache` on a launch line, with no log, count as the cached
   path? (The draft says no, and never relies on it alone.)
3. Should transcript evidence of uncommitted code override a meta's recorded
   commit? (e47 at `ed04977d6`; n1-outstanding at `bb73b52f5`.)
4. Should the requested tier count as the served tier before 2026-10-03,
   where no meta records `served_tier_counts` and no defect applies?
5. Should the 15 fragments whose end date comes from the E71 recovery be
   held to their launch day for billing-day evidence, as the draft does
   (the recovery added no usage to them)?
6. Should exact-match volume reasoning rest on day exports whose project
   filter is "unverified"?
7. Is a linear time split of the 08-27 verifier leg acceptable?
8. Attestations, or tooling: apply these as attestations, or extend the
   evidence code (read `*.txt` logs; treat the cached-token signature as
   machine evidence) so the register derives them itself?

## 6. Disposition (Session 160, register repair)

- **§ 5, ruled D34 as recommended.** (1) and (8): `scripts/derive_tier_evidence.py`
  reads `*.txt` logs and records every explicit-cache size a log prints
  (schema 5); `scripts/lib_pass_cost.py` reads the cached-token signature, but
  only at a logged explicit-cache size, because implicit caching hit every
  request of image-b's no-cache recoveries at 16,272 tokens (the pool's
  explicit cache is 18,909). A fragment whose billed requests report no cached
  token is exempt from a directory's logged cache (the n1-pro-rerun text
  pools, D34 (2)). The 84 rows this resolves all agree with their drafts; the
  other 15 drafts are superseded by the derivation and 54 are applied.
- **§ 5 (7) could not be carried out as written.** Verifier metas record no
  per-request times, so the 08-27 leg that crosses Pacific midnight (image-b's
  HIGH union verifier, 06:12 to 07:34 UTC) cannot be split by request. Bounded
  instead: billed flex holds the day if at most 56.8 % of that leg's output
  fell before midnight; it spent 57.9 % of its wall time there. Consistent,
  not decisive; no tier rests on it (D34 (6)).
- **§ 4.** (2) fixed by the `*.txt` sweep. (3) the E71 rerun: about US$11.41
  by the July invoice, three times its registered estimate, in the new
  unmetered-executions ledger (`data/pricing/unmetered-executions.json` U1,
  D35). (4) the two pro-medium baseline rows: a carried `batch_api` block no
  longer pins a real-time resume (D36); image standard, text flex (A72), both
  lower bounds. (5) image-t0.0 run 1's first launch: U2 (about US$5.39,
  transcript-reconstructed); the e47 run 5 batch job, which completed and was
  billed: U3, and its archive README corrected; the abandoned e47 jobs and the
  3.7 flex attempt: exposure bounds U4 and U5.

## Provenance

Investigation by an Opus subagent of Session 159, read-only over the
repository and `~/cc-archives/`. Spot-checked in session before
publication: the defect's code at `b57cf6c22`, the committed n1-pro-rerun
logs, the `*.log`-only sweep, the 14,549 / 0 cached-token signature, the 69
drafts (43 flex, 26 standard; no id collision), and the US$510.12 total
from the simulation output (188 rows, all `audited`).

## Changelog

### 2026-10-05 — Ruled and applied (Session 160)

Trigger: the PI's rulings D34 (§ 5) and D35-D36 (§ 4), applied on branch
`register-repair`. Status line and § 6 added; §§ 1-5 unchanged.

| Claim | Before | After |
|---|---|---|
| Rows resolved | 0 of 188 (proposal) | 188 of 188 audited, 84 by derived evidence |
| Attestations applied | 0 of 69 | 54 (15 superseded by derivation) |
| As-billed total of the 188 | US$642.04 high | US$510.12 |
| 08-27 check | linear split, 0.75 % over | bounded; per-request split impossible |

### 2026-10-04 — Original publication (Session 159)

Written after S158's item 4 was attempted on the PI's instruction ("if you
don't run into any other issues, go ahead"). Stopped at a proposal because
turning launch evidence into register attestations needs the PI's rulings
on evidence standards (§ 5) and is a register change, which belongs with
the D30 repair.
