# WP4 back-fill: gap analysis and design

**Created**: 2026-10-04 (Session 159). **Status**: on branch
`wp4-backfill`, D built (`34edba875`), B a recorded no-op, C built
(`ca2726fbe` library, `310a45757` stage, `959ae8a3f` data, `e6787427c`
findings) after the PI's choices C1 and C2 (D30); A built (729 sidecars).
Audited by two fresh-context lenses and a fresh-context re-audit of the first
fix round; the second fix round was verified by mutation tests in session.

WP4 is row 4 of § 5 of `planning/cost-accounting-fix-plan-2026-09-21.md`.
The plan budgeted it as "one sapphire regeneration". The dry run below
(the project's gap-analysis rule: execute each step mentally against the
files before writing code) finds that only one of its four deliverables
is a regeneration. Rulings that govern it: D14 (historical metas left as
written, audited sidecars beside them), D19 amended (the uniform
discounted tier for frontier costs), D28 (sidecars copy the register) and
D29 (tile-presence costs move to the uniform tier), all in
`planning/pi-decisions-2026-09-20.md`.

## Summary

| Item | Plan's wording | What the dry run found | State |
|---|---|---|---|
| D | the September CSV row re-derived from the invoice, FX 1.3904 | no writer existed; the full-month invoice export is present; FX by precedent is the header's 1.3905 | **built** (`scripts/derive_gemini_spend_by_sku.py`; gated on nine months exact) |
| B | hypothesis table re-projected | the generator reads no costs; `--check` passes (15 hypotheses) | **no-op**, recorded |
| C | the tile-presence `verifier-costs.json` re-run | a re-run would keep the old auditor; D29 moves it to the register at the uniform tier; 5 of 25 legs need a rule | **built** (§ C); the PI chose C1 (a) and C2 (a) plus a required register repair (D30) |
| A | `cost_audit.json` sidecars for every meta with usage | no writer exists; 723 of 1,539 metas carry token usage; none has a sidecar | designed (§ A) |

## D — the per-SKU spend table (built)

The table `reports/billing/gemini-spend-by-sku.csv` had no writer: the
Session 153 rows were made by hand. The new script reproduces that method
exactly. It reads the monthly Cost table export in `docs/costs/`, keeps the
project's `Gemini API` rows, and computes USD from the ROUNDED AUD at the
invoice header's rate. It refuses to write unless every month already on
the `invoice` basis re-derives byte for byte; all nine did.

- September moves from 14 provisional rows (the 2026-09-11 partial export
  at August's rate, AUD 30.58) to 30 invoice rows, AUD 1,225.45 =
  US$881.30 at 1.3905.
- **FX**: every earlier month uses its invoice header's stated rate; the
  September header states 1.3905. The plan's 1.3904 was derived from one
  line item. Settled by precedent, recorded beside D29.
- **No Gemini 3.6 SKU** appears in the September invoice for any project.
  The plan's § 8, finding 10, says September bills 3.6 Flash with no
  registered pass. That statement probably came from an unfiltered export
  (§ 8, finding 9, notes that the 2026-10-03 re-exports lack the project
  filter); WP6 should re-trace it.
- The committed file is CRLF, as the console exports are; the writer keeps
  the file's own terminator (an LF rewrite churned all 128 lines on the
  first attempt, caught before push).

## B — the hypothesis table (no-op)

`scripts/generate_hypothesis_outcome_table.py` projects
`results/analyses-manifest.json` and prices nothing. `--check` passes. It
needs re-running only when an analysis row changes, which WP7's re-reads
of signed rows may do.

## C — tile-presence verifier costs at the uniform tier

`scripts/build_tile_presence_board.py --stage costs` prices 25 verifier
legs by shelling out to `scripts/audit_verifier_cost.py` (the dated rate
card and a hand formula, on the as-billed tier). It cross-checks six image
legs against their campaigns' published figures. D29 moves the stage to
`scripts/lib_frontier_cost.py` over the passes register. Every leg's stage
directory maps to exactly one register row through the row's
`provenance.source_files`, except the three noted below.

| Legs | Register basis | Rule under D29 |
|---|---|---|
| 16 (TH7, T03, uplift, stride B, both 3.7 text arms, ten image legs) | audited | the leg's own tokens at the uniform tier |
| 4 (TM, IM, stride A, the fourth cell's 3.7 leg) | audited lower bound (cleanup-overwritten) | completed from the same nominated comparable legs the r2 board uses (`data/pricing/frontier-configurations.json`), marked † |
| 2 (3.7 image arm 2 at K = 1 and K = 3) | published (D13: the post-run report's figure; `lib_frontier_cost` refuses this basis) | **choice C1** |
| 3 (the vote-3 increments of TH7, T03 and TM, under `results/deployment-oracle-2026-06-06/vote3-verify/`) | not in the register | **choice C2** |

**C1, the two published legs.** Either (a) complete them as floors, from
the per-candidate unit of the audited legs with an identical verifier
configuration (3.7 image arm 2 at K = 5, same campaign and verifier), which
keeps every frontier on one rule; or (b) keep the published figure, which is
an audited as-billed amount and equals the uniform tier only if those legs
were served at flex or batch. Recommendation: (a), checked against the
published figure and with any disagreement beyond US$0.05 reported, as the
stage already does.

**C2, the three vote-3 increments.** Either (a) price each from its own
meta through `scripts/lib_pass_cost.py` at the uniform tier, marked "not in
register" (D28's rule for metas outside the register); or (b) extract the
S104 vote-3 campaign into the register first, as a register fix alongside
the queued `verifier-robustness` extraction. Recommendation: (a) now, with
(b) queued; (a) gives the same figure (b) would, without widening WP4.

**Ruled (D30)**: C1 (a), and C2 (a) WITH (b) as a required deliverable: the
register is repaired (the vote-3 campaign and `verifier-robustness`
extracted) in its own PR after WP4's. **Built**: `lib_frontier_cost` gains
`stage_leg` and `stage_leg_cost` (one shared rule for counting calls and
reading configurations); the stage routes each stage by its register state.
All 35 configurations are priced (23 measured, 12 completed; 12 had been
unpriced). The vote-3 increments price at US$2.97, US$2.74 and US$1.51; the
two completed image legs differ from their published figures by +US$0.048
and −US$0.014; the ten measured legs with a published figure agree to under
US$0.0001. A drift test pins the out-of-register stages, so the repair
turns it red on purpose.

**Downstream.** `leaderboard.md`, `leaderboard.json`, `frontier/` and
`findings.md` in `results/tile-presence-2026-09-21/` read the cost file.
The leaderboard and frontier stages are regenerated after it, and the
findings' prose figures refreshed under the revision policy. The
`--stage all --check` drift guard covers the generated files. Tests: the
stage's existing tests (`tests/test_tile_presence_board.py`) are updated,
plus one per rule above, each with a red sentinel. Run on sapphire.

## A — the `cost_audit.json` sidecars

No writer exists. Counts, re-verified 2026-10-04: 1,539 `*.meta.json`
files under `outputs/` (223 named `run.meta.json`), 723 with token usage,
no sidecar anywhere. Only five directories hold more than one meta.

**Design (D28).** A new script, `scripts/backfill_cost_audit_sidecars.py`,
dry run by default:

- **One sidecar per meta with usage**, named for its meta:
  `<stem>.cost_audit.json` beside `<stem>.meta.json`, and `cost_audit.json`
  beside `run.meta.json` (the plan's own name). The rule cannot collide,
  including in the five shared directories.
- **Contents copy the register**: for each register fragment whose
  `provenance.source_files` names the meta, the row's `pass_id`, `cost_usd`,
  `cost_basis`, `cost_source` and served-tier evidence, plus the register's
  `generated_at` and extractor version. The register stays the source of
  truth; the sidecar is a pointer a reader of the meta finds beside it.
- **A meta outside the register** (smoke tests, superseded executions, the
  vote-3 increments) gets a sidecar priced by `scripts/lib_pass_cost.py`,
  marked `"in_register": false`, with the reason.
- **Zero-usage metas get no sidecar** (the plan's § 4.5: they stay
  zero-usage; their passes are `null` with `cost_basis: unrecorded`).
- **Drift guard**: `--check` regenerates in memory and compares, so a
  register regeneration without a sidecar refresh turns red. Tier-1 tests
  on synthetic metas, with a red sentinel for the naming rule and for a
  meta whose register row moved.

Sidecars are committed beside their metas (the metas are tracked). About
723 new small files land in one commit, so the PR is reviewed on the
script, the tests and a sample, not file by file.

## Order of work

1. C on the branch, after the PI's choices C1 and C2; regenerate the four
   tile-presence stages on sapphire; refresh `findings.md`.
2. A on the branch; generate the sidecars on sapphire.
3. Two-lens `/audit` and a re-audit (the plan's practice for every PR);
   full tier-1 on sapphire; PR from `wp4-backfill`.

## Changelog

### 2026-10-04 (later still) — A built; audited

A built (a sub-branch, merged), its scope widened to `results/` and narrowed
to git-tracked metas (a sapphire-only untracked meta had made the drift
check machine-dependent). Two-lens audit, two fix rounds, one fresh re-audit;
tier-1 and tier-2 on sapphire. Findings for the PI: a third register gap
(grid-2026-08-18 proposer metas) and the board's vote-3 increment pricing (X1).

### 2026-10-04 (later) — C built after D30

The PI's choices recorded and C built and regenerated on sapphire (commits
in the status line). A is being built on a sub-branch.

### 2026-10-04 — Original publication (Session 159)

Written after D was built and B checked, from a dry run of C and A against
the committed code, the register and the exports.
