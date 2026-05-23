# Session 86 — Per-Architecture Tier Regression Investigation

**Investigator:** overnight Claude (Opus 4.7 1M-context).
**Date:** 2026-05-05 (overnight).
**Scope:** read-only investigation; no tracked files modified.

## TL;DR

The post-recovery rebuild thinned the per-architecture leaderboards because it
was launched via `scripts/run_per_arch_leaderboards.sh` (default `--top-n 20`),
not `scripts/build_per_arch_redesign.sh` (`--top-n 0`). The original
12-stratum tier tree at commit `b4c28d5b` was built by the redesign driver
with comprehensive coverage (all conditions admitted to tiering); the recovery
runbook directs the wrong driver, and so the rebuild applied a top-20 union
filter. The resulting 26-condition / 3-tier era2/pv view is **not** an
intended new canonical state — it is a forgotten configuration default
re-asserting itself. Three strata are affected: era1/consensus (72 → 37),
era2/consensus (29 → 22), era2/pv (44 → 26). The other four strata are
unaffected because they start with ≤ 20 conditions.

The root cause is **a script choice, not a code change**. No script logic in
the recovery window altered tier-build behaviour for the conditions that
remain. The 38 unchanged conditions in era2/pv have byte-identical F1 values
between pre- and post-recovery runs; only the six cleaned cells show the
expected small ΔF1 (≤ 0.010 absolute).

The most defensible morning move is **(a) run a tier-only re-build with
`--top-n 0` against the existing post-recovery evaluation cache** — no API
spend, ~10–30 min CPU on sapphire to compute the missing 621 era2/pv pairwise
tests (and the corresponding extras in era1/consensus and era2/consensus).
Step 4 (`build_combined_leaderboard.sh 2`) and Step 5 should NOT proceed
until this is fixed.

## 1. What changed between `b4c28d5b` and HEAD that affects tier-build behaviour?

Two commits modified `scripts/build_tiered_leaderboard.py` in this window:

| Commit     | Date         | Subject                                                              |
|------------|--------------|----------------------------------------------------------------------|
| `8c9a841d` | 2026-04-26   | feat(tier-builder): per-buffer F1 cache key + `--threshold-buffer` flag |
| `bea135af` | 2026-04-26   | fix(per-arch): tier-builder MD per primary buffer + regenerator (Task #13) |

Both commits were verified by reading their diffs in full.

**Commit `8c9a841d`** — adds a buffer-aware F1 cache layout
(`pairwise_f1_<B>m/...`) and a new `--threshold-buffer` CLI argument that
defaults to `--primary-buffer`. The commit message explicitly states the
patch is "additive and backwards-compatible: invoking the script with
`--primary-buffer 20` (and no `--threshold-buffer`) reproduces the existing
12-stratum build via cache hits on the legacy `pairwise/` files." A
`_cache_path_pairwise_read` helper falls back to the legacy `pairwise/`
layout when buffer = 20 m and the new path does not exist. This commit
**does not change tier composition** for a 20 m re-tier.

**Commit `bea135af`** — restricts the Markdown writer to one `.md` per
invocation (named for `--primary-buffer`) instead of one per buffer in
`--buffers`. The JSON writer was already one-per-invocation. This commit
**does not change tier composition either**; it only changes which Markdown
files get rewritten per call.

No other tier-affecting scripts changed between `b4c28d5b` and HEAD (verified
by `git log` against `scripts/run_per_arch_leaderboards.sh`,
`scripts/augment_per_arch_with_mcc.py`,
`scripts/enrich_per_arch_markdown.py`,
`scripts/build_cross_arch_comparison.py`,
`scripts/summarise_per_arch_headlines.py`,
`scripts/verify_per_arch_leaderboard.py`,
`scripts/finalise_per_arch_leaderboard.sh`, and `scripts/lib_*.py`). The
inventory file `planning/condition-inventory-with-s78.json` was last touched
at `03bf71c8` and is unchanged.

Bottom line: **no script change made between `b4c28d5b` and HEAD changes
tier-construction logic at 20 m primary buffer with no `--threshold-buffer`
override.** The Stage-3 `select_best_thresholds` top-N filter is the same
function as in the pre-recovery state, with `top_n=0` defined by the script
as "include every condition".

## 2. Is the regression caused by a script change or by data?

**Neither — the regression is caused by driver choice.**

Two driver scripts exist in the repository:

- `scripts/build_per_arch_redesign.sh` — passes `--top-n 0` for every
  invocation (line 89). Per the planning document
  `planning/leaderboard-construction-plan.md` § 7 (line 436):
  > **`--top-n 0` ("include all conditions").** The original build filtered
  > to top-20 at any buffer; the redesign uses `--top-n 0` for comprehensive
  > paper-table coverage.
- `scripts/run_per_arch_leaderboards.sh` — does **not** pass `--top-n`,
  so the script default of `DEFAULT_TOP_N = 20` (line 113 of
  `scripts/build_tiered_leaderboard.py`) applies.

The original 12-stratum tier tree committed at `b4c28d5b` was built by
`build_per_arch_redesign.sh`. The commit message at `b4c28d5b` confirms this:
"All previous tier tables under `results/leaderboard/per-architecture/` are
replaced with the new build using `--top-n 0` (comprehensive coverage)…"
The original logs in `logs/per-arch-leaderboards-rebuild-2026-04-25/` confirm
`top_n=0` was active during that build (line "Top-N filter disabled
(top_n=0); including all 44 conditions" appears in
`era2-pv-f1-q005.log` at `13:33:54`).

The recovery rebuild on 2026-05-05 used `run_per_arch_leaderboards.sh`. The
on-disk log `logs/per-arch-leaderboards/era2-pv.log` records the filter being
applied at this run: "Top-20 filter: 44 → 26 conditions (union across 5
buffers)" at `2026-05-05T19:35:20`.

The recovery is **driver-induced, not data-induced**. Confirmation: of the
44 conditions in era2/pv, the 38 untouched ones have **byte-identical** F1
values between pre-recovery (`b4c28d5b`'s `leaderboard_all_evaluations.json`)
and post-recovery (current `leaderboard_all_evaluations.json`); only the
six cleaned Session-78 cells show the expected small ΔF1 (verified by direct
JSON diff in this investigation):

```text
session-78-image-brief-text          pre F1=0.7679  post F1=0.7782  Δ=+0.0103
session-78-text-brief-text           pre F1=0.8456  post F1=0.8519  Δ=+0.0063
session-78-image-checklist-text      pre F1=0.7805  post F1=0.7852  Δ=+0.0047
session-78-text-checklist-text       pre F1=0.8599  post F1=0.8639  Δ=+0.0040
session-78-text-adversarial-text     pre F1=0.8575  post F1=0.8603  Δ=+0.0028
session-78-image-adversarial-text    pre F1=0.7725  post F1=0.7718  Δ=−0.0007
```

These deltas match the AUC deltas reported in commit `b3ed509e` (≤ 0.005
absolute on six cells), as expected from a 1–41-candidate addition against
pools of 2,000–4,000.

The **mechanics** of the top-N filter at `top_n=20` are also reproduced
exactly. Replicating the union-across-five-buffers logic from
`select_best_thresholds` in `scripts/build_tiered_leaderboard.py`
(lines 878–897) against the post-recovery `leaderboard_all_evaluations.json`
produces the same 26-condition kept set and 18-condition dropped set as the
post-recovery `leaderboard_tiers_20m.json`. The script logic is
deterministic and reproduces.

### Where the runbook went wrong

The phase 3a recovery runbook
(`planning/phase3a-verifier-recovery-runbook.md`) § 6.1 step 4 says only
"`bash scripts/finalise_per_arch_leaderboard.sh` **(auto)** — regenerates
`results/leaderboard/per-architecture/era2/consensus/leaderboard_tiers_*.{json,md}`."
This is wrong on two counts: (a) `finalise_per_arch_leaderboard.sh` is a
post-processing script (MCC augmentation, Markdown enrichment, cross-arch
table, headlines, verification spot-check), not a tier rebuild; (b) it
references `era2/consensus`, but the affected stratum is `era2/pv`. The
actual tier rebuild is implicit and was filled in by the planner of Session
86 (`planning/session-86-tier1-propagation-plan.md` § 3) as
`run_per_arch_leaderboards.sh`. Both the runbook and the Session 86 plan
inherited the wrong driver from `03bf71c8`'s commit, which packaged the
runner script alongside the original Session-79 tier tree without the
`--top-n 0` flag (and without re-deriving from `build_per_arch_redesign.sh`,
which was added later in `7c090d96` / `ad38ffbd`).

## 3. Was the new tier composition (26 conditions / 3 tiers) intended?

**No.** The leaderboard construction plan at
`planning/leaderboard-construction-plan.md` line 436 explicitly states the
12-stratum redesign's intent:

> The original build filtered to top-20 at any buffer; the redesign uses
> `--top-n 0` for comprehensive paper-table coverage.

The Session 86 propagation plan
(`planning/session-86-tier1-propagation-plan.md` § 3.3) explicitly expected
**zero tier flips** from the rebuild:

> Tier-membership of Session-78 cells in
> `era2/pv/leaderboard_tiers_20m.json`: **expected zero tier flips** (AUC
> deltas of 0.0001–0.0010 against pools of 2K–4K should not move tier).
> Halt criterion: any tier-rank flip on the 6 cells → halt, capture state,
> ask the user.

No reflection note (working-notes.md latest entry is Obs 322), planning doc,
or commit message in the recovery window mentions a deliberate decision to
re-introduce the top-20 filter. The change is **unintended** — a regression
against the canonical 12-stratum redesign.

## 4. Remediation paths

Three options, plus a hybrid. All are reversible if the working tree
modifications are kept staged but uncommitted (which they currently are).

### Option 1 — Tier-only re-build with `--top-n 0` against the existing cache

**What it does.** Re-invoke `build_tiered_leaderboard.py` with
`--top-n 0 --skip-evaluation` for the three thinned strata
(era1/consensus, era2/consensus, era2/pv), reading the post-recovery
evaluation cache. Tiers are reconstructed; missing pairwise tests are
computed fresh. All other artefacts (`leaderboard_all_evaluations.json`,
the cache, MCC and q01 variants which weren't touched) are left as-is.

**Cost.** Cache-only evaluation (no fresh detection runs, no API calls).
Pairwise: era2/pv needs C(44,2) − C(26,2) = **621 new pairwise tests at
20 m**. era1/consensus needs at least C(72,2) − C(37,2) = 1,890 new tests.
era2/consensus needs C(29,2) − C(22,2) = 175 new tests. With 8 workers and
10,000 permutations each, sapphire wall-clock estimate is **~30–90 min for
all three strata combined** (era1/consensus dominates). Re-running
`finalise_per_arch_leaderboard.sh` after takes another ~5 min for MD
enrichment and cross-arch table.

**Risk.** Low. The fix is surgical: it only changes which conditions appear
in tier files, not the underlying evaluation data. It will move the tier
composition back to the 44-condition view that matches `b4c28d5b` modulo the
six cleaned cells.

**Reversible.** Yes — the entire working-tree state can be reverted to
`b4c28d5b` if needed.

**Caveat.** This option uses the buffer-aware `pairwise_f1_20m/` cache and
will end up with cache content distinct from `b4c28d5b` (which stored
pairwise results in the legacy `pairwise/` layout). That's fine — the
`_cache_path_pairwise_read` fallback handles the legacy layout if needed.

### Option 2 — Restore pre-recovery tier files from `b4c28d5b` and surgically re-run only the 6-cleaned-cell evaluations

**What it does.** Check out `b4c28d5b`'s 20 m tier files for the affected
strata, then re-run only the six Session-78 *-text cells through the
evaluation + tiering pipeline so their post-cleanup F1 values replace the
pre-cleanup ones. Other 38 conditions in era2/pv (and similar in
era1/consensus, era2/consensus) keep their `b4c28d5b`-era F1 numbers.

**Cost.** Cheaper than Option 1 in raw CPU (only 6 cells × 5 buffers
re-evaluated, plus pairwise tests involving any of the 6 cells against the
other 43, i.e. 6 × 43 = 258 new pairwise tests at era2/pv 20 m). Roughly
**~10–20 min wall-clock**.

**Risk.** Moderate. Mixing pre- and post-recovery F1 values within one
tier file is a provenance hazard: the JSON metadata block becomes ambiguous
about which date / commit produced each row. Tier construction at the
`b4c28d5b` snapshot used the legacy pairwise cache; bringing the cleaned
cells in requires care that the new pairwise tests are computed against the
same evaluation snapshot for the other 38 conditions, otherwise the BH-FDR
clique structure could shift inconsistently. This is delicate enough that
the user explicitly preserved this option — but it should not be the
default.

**Reversible.** Yes, but the audit trail is harder to reconstruct
afterwards.

**Caveat.** This option **does not** address the root cause (driver bug);
the next time someone runs `run_per_arch_leaderboards.sh` the regression
will reappear. So it is only acceptable if paired with a separate
script-fix commit that either changes the runner default or fixes the
runbook.

### Option 3 — Full rebuild via `build_per_arch_redesign.sh`

**What it does.** Invoke the canonical redesign driver, which re-runs all
seven populated strata × four passes (F1 q05, F1 q01, MCC q05, MCC q01),
applies `--top-n 0`, and produces the full set of artefacts the 12-stratum
redesign was designed to emit.

**Cost.** Per the original `b4c28d5b` log, ~73 minutes Stage-2 wall-clock
on sapphire with 8 workers. Plus Stage 3 (tier-stability), Stage 4
(cross-architecture tables), Stage 5 (documentation). Total ~90–120 min.
With cache reuse this should be much shorter for the unaffected six cells'
neighbours, but the q01 / MCC variants would also be regenerated — possibly
desirable since those JSONs currently date from May 2 and pre-date the
six-cell cleanup.

**Risk.** Low for correctness. Medium for inadvertent collateral damage —
this overwrites every tier file in `results/leaderboard/per-architecture/`
including the q01 and MCC variants that the recovery rebuild left
untouched. But the q01 / MCC variants are *also* currently stale relative
to the recovery (their F1 / MCC numbers reflect pre-cleanup probabilities
for the six cells), so rebuilding them is arguably correct.

**Reversible.** Yes via working-tree revert.

**Caveat.** This option re-derives all post-processing artefacts (headlines,
cross-architecture tables, README files), which lengthens the diff for
review. Some of those files have human-curated content that may have been
edited downstream — worth a `git status` audit before launching.

### Hybrid recommendation (preferred)

**Step A:** fix the regression with Option 1 (cheapest, smallest blast
radius, restores the canonical view).

**Step B:** fix the runbook and the runner. Either (a) edit
`run_per_arch_leaderboards.sh` to add `--top-n 0` matching
`build_per_arch_redesign.sh`, or (b) edit
`planning/phase3a-verifier-recovery-runbook.md` § 6.1 step 4 to point at
`build_per_arch_redesign.sh` instead. Probably both (a) is the safer
default since it makes the convenient runner produce the canonical output;
the redesign driver covers more (4 passes per stratum) but also costs
more.

**Step C:** consider whether to also rebuild q01 and MCC variants since
those JSONs date from May 2 and pre-date the cleanup. They should still
be approximately correct (small F1/AUC deltas only), but a paper-citation
audit may turn up tier-membership claims that depend on those views.

**Cost summary:** Step A ~30–90 min sapphire CPU, no API spend. Steps B
and C are documentation / config edits with no compute cost (B) or another
~73 min sapphire CPU (C, optional).

## 5. Should Step 4 (`build_combined_leaderboard.sh 2`) and Step 5 (`build_combined_tier_stability.sh 2`) proceed?

**No, not until the per-architecture tier files are restored.**

Detailed reasoning:

`build_combined_leaderboard.sh` reads the **per-architecture caches**
(hardlinked from `results/leaderboard/per-architecture/era<N>/<arch>/.cache/`)
and the **inventory** file. It does **not** read the per-architecture tier
JSONs as input. It also passes `--top-n 0` (lines 165, 229), so the
combined output is built with comprehensive coverage and would tier all
44 era2/pv conditions correctly.

So in principle Step 4 *would* produce a correct combined leaderboard even
with the per-arch tier files thinned, because it bypasses them. But:

1. **The combined output is meant to be downstream of, and consistent
   with, the per-architecture view.** Producing a 44-condition combined
   tier on top of a 26-condition per-architecture stratum creates an
   internal inconsistency that will confuse anyone reading both files.
2. **Step 5 (`build_combined_tier_stability.sh 2`) reads `leaderboard_tiers_<B>m.json`
   files** in the combined output dir (per the script header). If Step 4
   also ends up writing thinned tiers — which it shouldn't given
   `--top-n 0`, but worth double-checking — Step 5 would propagate the
   error.
3. **Sanity rule:** when an upstream artefact is wrong and the operator
   knows it is wrong, the right move is to fix it, not to keep building
   on top.

Recommendation: **do not run Step 4 or Step 5** until Step A (Option 1
re-tier) is complete and the per-architecture tier files at 20 m are
back to 44 / 72 / 29 conditions matching `b4c28d5b`. Once that is done,
Step 4 and Step 5 are both safe to launch.

## 6. What should morning-Claude do first?

Ordered checklist for the morning operator:

1. **Verify** the working tree is still in the state captured by this
   investigation. Run `git status results/leaderboard/per-architecture/`
   and confirm only the seven `leaderboard_tiers_20m.json` files (one per
   populated stratum) plus their MD siblings, plus
   `leaderboard_all_evaluations.json`, plus the untracked
   `leaderboard_rows_<B>m.json` files appear as modified or untracked.
   Confirm `era1/{pv,single-pass+PV}`, `era3/{single-pass,single-pass+PV,pv}`
   contain only stub files (those untracked dirs are expected — they are
   newly emitted stubs reflecting the documented "empty stratum" pattern).

2. **Read this report end-to-end** (including the Caveats / methodological
   notes about pre-cleanup F1 deltas) before taking any action.

3. **Confirm with the user** that Option 1 (tier-only re-build with
   `--top-n 0` against the existing cache) is the preferred path, given
   the runbook bug. The user has explicitly preserved Option 2 as on the
   table; if the user prefers Option 2 for any reason (e.g. paper-citation
   provenance concerns about mixing pre- and post-cleanup pairwise tests),
   defer to that judgement.

4. **Do NOT run** `run_per_arch_leaderboards.sh` again in its current form
   — it will reproduce the same regression. Either edit it inline to add
   `--top-n 0`, or invoke `build_tiered_leaderboard.py` directly with
   `--skip-evaluation --top-n 0` for the three affected strata.

5. **Do NOT run** Step 4 (`build_combined_leaderboard.sh 2`) or Step 5
   (`build_combined_tier_stability.sh 2`) until the per-arch tier files
   are restored.

6. **After fixing the per-arch tier files**, run `finalise_per_arch_leaderboard.sh`
   to refresh the MCC augmentation, Markdown enrichment, cross-arch
   comparison, and headlines. This is cheap (~5 min).

7. **Either before or after the fix**, decide whether to rebuild the
   q01 and MCC variants for the three affected strata. They currently
   pre-date the cleanup; small F1/MCC deltas may shift tier membership
   for a handful of cells. If the paper cites any q01 or MCC tier
   numbers, this matters; if not, it can wait.

8. **Patch the runbook and / or runner.** Add `--top-n 0` to
   `scripts/run_per_arch_leaderboards.sh` (one-line change) **and** update
   `planning/phase3a-verifier-recovery-runbook.md` § 6.1 step 4 to
   reference the actual tier-rebuild step (currently it references
   `finalise_per_arch_leaderboard.sh`, which is post-processing only, and
   names `era2/consensus` instead of the correct `era2/pv`). Commit
   separately under `fix(per-arch):` and `docs(runbook):` prefixes.

9. **Document the regression and recovery** as an Observation in
   `docs/notes/reflections/working-notes.md`. Likely Obs 323 or 324
   depending on what else is captured first. The pattern is worth
   recording: "two driver scripts in the same project, one with a critical
   flag (`--top-n 0`) and one without, and the runbook silently directed
   the wrong one." This is a `convention-propagation failure` per the
   project's recurring-pattern taxonomy in MEMORY.md.

10. **Consider archiving** `scripts/run_per_arch_leaderboards.sh` to
    `archive/deprecated-scripts/` per the project's "archive, never
    delete" policy, and removing it from the active codebase, IF the
    driver is genuinely redundant with `build_per_arch_redesign.sh`. If
    it serves a distinct purpose (e.g. lighter single-stratum re-builds),
    keep it but rename or annotate to make the intent clear.

## Caveats / methodological notes

**On Option 1's pairwise computation.** The pairwise permutation test
results depend on the candidate probability distributions (specifically,
the tile-level paired binary outcome). For the six cleaned cells, those
distributions changed under recovery. For the other 38 cells they did not.
So the 621 new pairwise tests in era2/pv that Option 1 needs to compute
are a mix of (cleaned-cell vs cleaned-cell) — already at most 6×5/2 = 15
tests — and (cleaned-cell vs unchanged-cell) and (unchanged-cell vs
unchanged-cell). The unchanged-vs-unchanged tests should produce results
identical to what `b4c28d5b` would have produced if it had used `--top-n 0`
on those pairs (modulo permutation-seed determinism, which is preserved
via `--seed 42` in both drivers). So the resulting tier structure for the
other 38 cells should match `b4c28d5b` exactly. This is a useful
audit-anchor: if the morning re-tier under Option 1 produces a different
tier composition for the 38 unchanged cells than `b4c28d5b` did, something
else is wrong and a deeper investigation is warranted.

**On the q01 and MCC variants.** Those JSONs (`leaderboard_tiers_q01_*.json`,
`leaderboard_tiers_mcc_*.json`, `leaderboard_tiers_mcc_q01_*.json`) were
**not** rewritten by the May 5 rebuild. They date from May 2 (the last
git checkout's mtime) and reflect the pre-cleanup F1/MCC numbers for the
six cells. So:

- **Their tier composition is correct** (44 conditions / appropriate tier
  structure under `--top-n 0`). The regression does not affect them.
- **Their per-condition F1/MCC values are slightly stale** (small ΔF1 ≤
  0.010 absolute on six of 44 cells; ΔMCC values not measured but expected
  to be similarly small).

So they are simultaneously *correct in tier composition* and *slightly
stale in scores*. Whether this matters depends on whether the paper or any
downstream artefact cites those tier numbers / scores at granularity
finer than ~0.01 F1.

**On `headlines.md` and `cross-architecture-20m.md`.** Both were
overwritten by the May 5 `finalise_per_arch_leaderboard.sh` run and now
reflect the thinned 26-condition view. After Option 1 fix, re-running
`finalise_per_arch_leaderboard.sh` will refresh both correctly.

**On the buffer-aware F1 cache layout.** Commit `8c9a841d` introduced
`pairwise_f1_<B>m/` directories. The pre-recovery cache was in the legacy
`pairwise/` layout. The May 5 rebuild created `pairwise_f1_20m/` from
scratch (containing 325 files for 26 cells in C(26, 2) pairs). The legacy
`pairwise/` directory was archived to (now-missing) `archive/leaderboard-caches/`
per `a80a9de9` and `94c75918`. Re-tiering with `--top-n 0` in Option 1
will compute the missing 621 pairs into the new `pairwise_f1_20m/` cache.
Both caches yield identical results when rerun — `--seed 42` is honoured.

**On what's NOT in scope.** This investigation does not address:

- Whether `b4c28d5b`'s 12-stratum redesign was itself the right
  methodological choice (it is — that decision is documented and approved
  in the leaderboard construction plan).
- Whether the six-cell cleanup at `414ee8a4` / `b3ed509e` was correct
  (it is — verified by the AUC delta analysis in `b3ed509e`'s commit
  message; deltas all within expected magnitude for 1–41-candidate gaps
  against pools of 2,000–4,000).
- Whether the recovery should have been done at all (it was correct;
  the verifier-completeness audit at `adf95dbf` identified 153 silently-
  dropped candidates that the cleanup recovered).

## Source-of-truth references

- `planning/leaderboard-construction-plan.md` § 7 (line 436) — `--top-n 0` is
  the redesign default.
- `scripts/build_per_arch_redesign.sh` line 89 — canonical driver.
- `scripts/run_per_arch_leaderboards.sh` (no `--top-n` flag) — wrong driver.
- `scripts/build_tiered_leaderboard.py` lines 113 (`DEFAULT_TOP_N = 20`),
  878–897 (`select_best_thresholds` top-N logic), 879 ("`top_n=0` (or `None`)
  disables the filter").
- `logs/per-arch-leaderboards-rebuild-2026-04-25/era2-pv-f1-q005.log` —
  pre-recovery log proving `top_n=0` was active at that build.
- `logs/per-arch-leaderboards/era2-pv.log` — post-recovery log proving
  `top_n=20` was active at the May 5 rebuild.
- Commits `8c9a841d`, `bea135af` — the only two `build_tiered_leaderboard.py`
  changes in the regression window; both verified backwards-compatible.
- `planning/phase3a-verifier-recovery-runbook.md` § 6.1 step 4 — runbook
  bug (says `finalise_per_arch_leaderboard.sh` regenerates tier files; it
  does not).
- `planning/session-86-tier1-propagation-plan.md` § 3 — Session 86 plan
  inheriting the runbook bug.
- `b4c28d5b:results/leaderboard/per-architecture/era2/pv/leaderboard_tiers_20m.json`
  metadata: `top_n=0`, 6 tiers, 44 conditions, `n_conditions_input=44`.
- `results/leaderboard/per-architecture/era2/pv/leaderboard_tiers_20m.json`
  (post-recovery) metadata: `top_n=20`, `threshold_buffer=20`, 3 tiers,
  26 conditions, `n_conditions_input=44`.
