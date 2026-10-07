# PR #25 review fixes: report

Date: 2026-10-07. Branch `gate-coverage-fixes`, pushed as a fast-forward to
the PR branch `gate-coverage-2026-10-06` (`8cc5b3078..595e16790`, ten
commits). The PR is not merged.

Governing principle applied throughout: the gate must never PASS on evidence
it does not have. Missing, unreadable, partial or self-declared-incomplete
evidence now makes that half of the arm UNVERIFIABLE with a named reason.

## How the full-register runs were made

- Scratch clone on sapphire: `git clone --shared --no-checkout` of
  `~/Code/map-reader-llm` into `/tmp/gate-fixes/repo`, the PR branch fetched
  from GitHub, later the fix commits fetched from a git bundle. Nothing was
  written into the sapphire checkout.
- The gate ran from the clone's code and bindings file, reading the sapphire
  checkout's registers, metas (tracked and untracked) and git history
  read-only, via `/tmp/gate-fixes/run_gate.py` (overrides `BASE_DIR` in
  `check_manipulation` and `derive_condition_modality`; bytecode writing off).
  The four registers in the clone and the checkout have identical SHA-256.
- The harness reproduced the stated baseline exactly at `8cc5b3078`:
  71 analyses, 66 PASS, 5 REFUSE (2 known, 3 with a new pair),
  0 UNVERIFIABLE.
- After each fix commit the gate was re-run and compared arm by arm
  (`/tmp/gate-fixes/after-*.json`, `compare-*.txt`).

## Findings: verification, change, commit, test

All ten findings were confirmed at source; none was wrong. Findings 1, 2, 3,
5, 6, 7, 8 and 9 are latent on the committed register: after each of those
commits no verdict, no arm's verifier basis, stage, reason or meta list
moved. Only finding 4 moves verdicts.

| # | Verified at source | Change | Commit | Regression tests (tier 1 unless noted) |
| --- | --- | --- | --- | --- |
| 1 | Yes: `stage_metas` returned manifest paths unchecked; `arm_from_metas` then gave `verifier_basis` None and `transmission_relation` DIFFER. Same hole in the binding's stage route. On sapphire no stage lists only unreadable metas. | A fourth verifier basis, `"unverifiable"`, with `verifier_unverifiable_reason`: a non-empty verifier list with zero readable verifier records (absent, corrupt, or not a verifier pass) is unverifiable on both routes. Like a declared half it separates a pair only through the proposer half; two arms reading one unverifiable stage are judged on the proposer half. `stage_metas` falls back to the W4.4 resolver when no manifest meta is readable, and is memoised. | `67bbee1a7` | `test_a_register_stage_with_no_readable_meta_is_unverifiable_not_absent`, `test_a_bound_stage_with_no_readable_meta_is_unverifiable_not_absent`, `test_a_stage_listing_only_a_proposer_meta_is_unverifiable`, `test_two_arms_reading_one_unverifiable_stage_are_judged_on_the_proposer` |
| 2 | Yes: `_from_sources` results were used when only some sources resolved. No committed binding has a dead source (no BINDING GAP line before or after). | A binding is used whole or not at all: any dead verifier source leaves the verifier half unverifiable (not the declared fallback); any dead proposer source leaves the arm unverifiable. BINDING GAP line kept. | `e9dd5cdfc` | `test_one_dead_verifier_source_voids_the_half`, `test_one_dead_proposer_source_voids_the_arm`; `test_a_dead_source_is_named_not_silently_skipped` updated (now unverifiable, not declared) |
| 3 | Yes, on the real register: `55maps-generalisation/verified-cleanup-20260410` (path `.`) made `outputs/55maps-generalisation` and its `gs`, `h11` and `retest` twins stage directories. `verifier_stage_of` (the register's route) had the same catch-all. No source or condition matched it. | `_stage_homes`: a `repo_path` stage lives at `<repo_path>/<path>` only; a candidate that is a run's whole tree is dropped. Used by `_stage_dirs` and `verifier_stage_of`. `dcm.stage_path_candidates` itself is unchanged. | `20b058dc7` | `test_a_dot_path_stage_is_not_a_catch_all`, `test_a_repo_path_stage_does_not_claim_the_run_tree`; tier-2 `test_the_committed_bindings_agree_with_the_register` now fails on any run-root stage directory and checks each source's matched home |
| 4 | Yes: the gate never read `meta_beside_source` or `caveats`. | Gate: `incomplete_meta: true` + one-line `incomplete_meta_reason` (validated). The flag is applied to the STAGE (`_incomplete_stages`), so every arm reading that stage is unverifiable on its verifier half, by any route; the partial meta is listed in `verifier_metas_set_aside`. Data: 28 entries flagged (list below); README updated. | `bca9d4c82` (gate), `1c6a7d48d` (data), `595e16790` (one reason's article) | `test_an_incomplete_meta_binding_leaves_the_half_unverifiable`, `test_an_incomplete_stage_is_unverifiable_by_every_route`, `test_an_invalid_incomplete_meta_flag_is_named` (5 cases); tier-2 `test_every_binding_with_a_partial_meta_is_flagged` pins the wording |
| 5 | Yes (read): route 1 kept absent, unparseable and non-meta manifest hits and they suppressed routes 2 and 3; route 2 accepted a single-file source unread. | Route 1 answers only if a hit is a readable proposer meta (keeps unreadable meta-named hits so the arm names them, drops `run.log` and the register); otherwise falls through. Route 2 requires a readable proposer meta. | `16b296dd0` | `test_unreadable_manifest_hits_do_not_stop_the_disk_route`, `test_a_readable_manifest_hit_keeps_its_unreadable_sibling_visible`, `test_a_single_file_source_must_be_a_readable_proposer_meta` |
| 6 | Yes (read): the tail was sliced from the NEW path by the old source's length. | `dcm.git_renames` returns `(old, new)` pairs (`git_renamed_to` delegates to it); the route tests the OLD path's place below the source. | `16b296dd0` | `test_a_git_renamed_meta_is_judged_by_where_it_sat`; `test_git_renamed_to_follows_an_archived_leg` extended |
| 7 | Yes (read): a binding to a different stage silently replaced a register-identified stage with no metas, and `stage` became a route name. | Refused: verifier half unverifiable, reason naming both stages; stage field keeps the register's stage. A binding whose sources all lie inside the register's stage is followed. The stage field always names a stage (`run/key`, or `<dir> (unregistered)`); routes move to `verifier_route`. | `7caf11f9d` (stage-label part in `e9dd5cdfc`) | `test_a_binding_to_another_stage_does_not_override_the_register`, `test_a_binding_inside_the_registers_stage_is_followed` |
| 8 | Yes (read): str sources TypeError, missing `bindings` KeyError, str evidence AttributeError, unhashable id TypeError; `[]`/null passed. | Every field type-checked; absent, null, empty or non-list `bindings` is a problem (delete the file to run without bindings); unreadable file reported. All exit 1 with `ERROR:`. | `d84c37dbf` | `test_a_malformed_bindings_file_exits_1_with_an_error` (15 cases through `main`) |
| 9 | Yes (read): route 2 parsed before the path filter (pinning verified metas in the unbounded loader cache); route 1 inlined `_is_verifier_meta`; verifier route 2 harvested absolute paths and returned relative ones. | Shared `_proposer_metas_under` (filter before parse) serves `proposer_metas_of` and route 2; `_is_proposer_meta` beside `_is_verifier_meta`; all `meta_record` calls go through `_rel`; both resolvers memoised (return tuples). | `16b296dd0` | `test_the_disk_route_never_parses_a_verified_subtree`, `test_a_meta_reached_by_two_spellings_is_harvested_once` |
| 10 | Yes: `8cc5b3078` subject is 52 characters, `32178f74a` 51; nested `proposer_side()` had no docstring. | `proposer_side` replaced by documented `_on_proposer_side`; docstrings added to nested `readable()`, `values()`, `norm()` (new), and the legacy `add()`, `bump()` (dcm) and test helpers `arm()`, `git()`. The two pushed subjects are NOT rewritten (that needs a force-push). | `73455051d` (plus `67bbee1a7`) | n/a |

Mutation check (sapphire, real copies, `/tmp/gate-fixes/mutate.py`): a
control run of the unmutated copy was green (56 passed); each of 13
mutations that reverts one fix turned its tests red (F1, F2 ×2, F3 ×2, F4,
F5 ×2, F6, F7, F8, F9 ×2). For F4 the stage-level test catches the mutation;
the binding-level test is also held by the binding's own flag (by design,
two paths).

## Design decisions to review

- **Half-level, not whole-arm.** An unverifiable verifier half behaves like a
  declared one: a pair whose proposer requests differ still DIFFERs on
  evidence the gate has; a pair whose proposer requests match is an
  UNVERIFIABLE PAIR. Hence four analyses with unverifiable halves stay PASS
  (below). A whole-arm rule would have made them UNVERIFIABLE too.
- **`incomplete_meta` applies to the stage, not only the binding.** It is a
  fact about the stage's surviving metas. On the full register this extends
  to exactly one register-route arm, `gold-standard-v2::verified-v1`, which
  sits only in two analyses that REFUSE either way, so no verdict depends on
  this choice.
- **Partial evidence could prove DIFFER.** E.g. stride B's `verify` (complete,
  gemini-3-flash) versus the fourth cell's `verify_37`, whose surviving
  29-item round records gemini-3.7-flash: one differing request refutes
  "identical transmissions". Per the brief, a partial half is unverifiable
  instead; a later refinement could let a partial meta prove DIFFER (never
  SAME) and would honestly restore some of these PASSes.

## The 28 incomplete-meta entries (24 distinct stages)

Every one of the 181 entries' `meta_beside_source` and `caveats` was read.

| # | Binding | Stage | `incomplete_meta_reason` |
| ---: | --- | --- | --- |
| 1 | `stride-a-k10-primary-canonical` | `stride-55map-2026-08-25/g384_ov128_55map-union-k10-verify` | run.meta.json records only the 6-item cleanup leg (2026-08-26); no meta survives for the main 38,713-candidate leg |
| 2 | `stride-a-k10-oracle-canonical` | same | same |
| 3 | `stride-a-final-board-cells` | same | same |
| 4 | `stride-a-n3-carried-posthoc` | same | same |
| 5 | `fourth-cell-k10-primary` | `stride-55map-2026-08-25/g384_ov192_55map-union-k10-verify37` | run.meta.json records only the final 29-item driver round (gemini-3.7-flash, low); the earlier rounds that verified the bulk of 57,482 candidates overwrote theirs (a73d64346) |
| 6 | `fourth-r2-board-cells` | same | same |
| 7 | `g37img-k1-arm2` | `gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img-union-k1-verify-arm2` | 13-item cleanup pass only; the 6,972-item main pass's meta (gitignored backup) not found |
| 8 | `g37img-k3-arm2` | `gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img-union-k3-verify-arm2` | 1-item cleanup pass only; the 8,336-item main pass's meta not found |
| 9 | `g37-screen-k5-swap37` | `gemini37-screen-2026-08-28/g384_ov192_g37-union-k5-verify-swap37` | 2-item cleanup pass of 791 requests; no main-run meta |
| 10 | `grid-g384ov192-k10-verify37-gs-leg` | `grid-2026-08-18/g384_ov192-union-k10-verify37` | 1-item cleanup pass of 3,319 requests; no main-run meta |
| 11 | `s78-text-checklist-text` | `pv-diag-384/...-session-78-matrix-verified-checklist-text` (text pool) | last leg only (21 items, 414ee8a4b); earlier leg's meta only in git (5cee158bc) |
| 12 | `s78-text-adversarial-text` | `...verified-adversarial-text` (text pool) | last leg only (41, 414ee8a4b); earlier in git (96a6ac235) |
| 13 | `s78-text-brief-text` | `...verified-brief-text` (text pool) | last leg only (27, 414ee8a4b); earlier in git (bd0a4d091) |
| 14 | `pv-archived-pv-high-image-t0.7-n5` | `pv-diag-384/flash-high-image-n5-image-t0.7-verified-v1-n5` | last leg only (1, c6b5e6b10); earlier in git (b8961e56f) |
| 15 | `s78-image-checklist-text` | `...verified-checklist-text` (image pool) | last leg only (19, 414ee8a4b); earlier in git (f36e7bef9) |
| 16 | `s78-image-checklist` | `...verified-checklist` (image pool) | last leg only (1, c6b5e6b10); earlier in git (400e6fbcb) |
| 17 | `s78-image-brief-text` | `...verified-brief-text` (image pool) | last leg only (19, 414ee8a4b); earlier in git (e85c62902) |
| 18 | `s78-image-adversarial-text` | `...verified-adversarial-text` (image pool) | last leg only (26, 414ee8a4b); earlier in git (35b380a6d) |
| 19 | `pv-archived-pv-scale4-optimal-n10` | `pv-diag-384/scale-4-optimal-487-verified-v1-n10` | last leg only (1, c6b5e6b10); earlier in git (b8961e56f) |
| 20 | `pv-archived-pv-high-image-t0.3-n5` | `pv-diag-384/flash-high-image-n5-image-t0.3-verified-v1-n5` | last leg only (11, c6b5e6b10); earlier in git (b8961e56f) |
| 21 | `pv-archived-pv-high-image-t1.0-n5` | `pv-diag-384/flash-high-image-n5-image-t1.0-verified-v1-n5` | last leg only (1, c6b5e6b10); earlier in git (b8961e56f) |
| 22 | `sweep-text-baseline-pro-vf` | `pv-diag-384/verified-text-baseline-pro-verifier` | 21-candidate cleanup leg (2026-05-06); original leg's meta overwritten |
| 23 | `sweep-pro-image-pro-vf-3of5` | `pv-diag-384/verified-pro-high-image-1of5-pro-verifier` | 8-candidate cleanup leg (2026-05-06); original overwritten |
| 24 | `sweep-pro-image-baseline-pro-vf` | `pv-diag-384/verified-pro-medium-image-baseline-pro-verifier` | 10-candidate cleanup leg (2026-05-06); original overwritten |
| 25 | `cset-medium-vf-4of5` | `pv-diag-384/verified-flash-high-text-1of5-flash-medium-verifier` | registered stage's meta is a 1-item cleanup leg (2026-05-06); original overwritten |
| 26 | `matrix-min-T0.3` | `verifier-robustness/384-ge3of5-t0-3` | covers only the last (resumed) segment: 2,775 items against 4,275 results |
| 27 | `flash35-f35prop-f3vf` | `flash35-pv-2x2/verified-f3vf` | 1-item cleanup leg of 1,132 requests; original V1 leg's meta overwritten (tranche-full.log:6382-6383) |
| 28 | `vtpilot-t0-0` | `gold-standard-v2/verified-v1` | a 2026-05-03 cleanup leg, after the product; original leg's meta overwritten |

(The full reason strings are in `results/manipulation-gate-bindings.json`.)
The original agent named 23 stages; I find 24, the difference most likely
being `matrix-min-T0.3` (resumed segment) or `vtpilot-t0-0` (cleanup leg
with no "only" in its caveat).

Considered and not flagged: `g37img-k5-arm2` (a MERGED meta over all three
passes), `g3img-k1-arm2` and `g3img-k5-arm2` (batch-recover metas with
whole-leg counts, only the timing is the recover step's),
`g37-screen-k5-swap38-armV` (the passes manifest lists both its metas, so
the gate reads all 791 requests), `g37-kladder-k3-verify-k3-recovery-fixed`
(binds both stages), the old-schema metas with `items_processed 0` (the
configuration block is complete), and `matrix-min-T0.7`, `matrix-high-T0.3`,
`matrix-high-T0.7`, `opmax-16of30`, `cset-vr-256-ge3of5-t0-3` (complete legs
whose metas record temperature 0.0, not the registered T: a manipulation
that leaves no trace in the meta, the W7 class, not a partial leg).

## Before and after (full register, sapphire)

| | PASS | REFUSE (known / new pair) | UNVERIFIABLE |
| --- | ---: | ---: | ---: |
| Before (`8cc5b3078`) | 66 | 5 (2 / 3) | 0 |
| After (`595e16790`) | 47 | 5 (2 / 3) | 19 |

58 of the 628 judged arms moved, all from `transmitted` to `unverifiable`
on the verifier half, all through finding 4. The five refusals and all 90
null pairs (with their KNOWN/NEW labels) are identical before and after.
`--all` still exits 2 (new refusals in `era1-leaderboard`,
`null-exemplar-sensitivity-2026-09-13`, `uplift-supplement-flatten`).

### The 19 analyses that moved PASS to UNVERIFIABLE (all finding 4)

Each holds at least one pair whose proposer requests match and whose
verifier half reads a flagged stage, so whether the configured difference
reached the model cannot be shown.

| Analysis | Unverifiable pairs | Flagged stage(s) behind it (binding) |
| --- | ---: | --- |
| 55map-final-board-r2-2026-09-06 | 28 | stride A K10 verify (stride-a-final-board-cells, stride-a-n3-carried-posthoc); stride verify37 (fourth-r2-board-cells) |
| estimated-correction-r2 | 28 | same as above |
| sensitivity-mde-r2 | 28 | same as above |
| k-ladder-2026-09-12 | 56 | stride A K10 verify (14 halves); stride verify37 (4) |
| flash35-model-roles | 1 | flash35 verified-f3vf (flash35-f35prop-f3vf) |
| gemini3-image-55map-2026-09-16 | 9 | g37img K1 and K3 arm 2 |
| gemini37-55map-grid-2026-08-31 | 4 | stride verify37 (fourth-cell-k10-primary) |
| gemini37-55map-gridboard-2026-08-31 | 1 | stride verify37 (fourth-cell-k10-primary) |
| gemini37-fourth-cell-gs-leg-2026-08-31 | 1 | grid verify37 (grid-g384ov192-k10-verify37-gs-leg) |
| gemini37-image-55map-2026-09-13 | 81 | g37img K1 and K3 arm 2 (3 halves each) |
| gemini37-image-55map-k5-replicate-2x2-2026-09-20 | 17 | g37img K1 and K3 arm 2 |
| gemini37-image-gs-2026-09-01 | 1 | g37-screen swap37 |
| gemini37-screen-2026-08-28 | 2 | g37-screen swap37 |
| gemini38-screen-armv-2026-09-04 | 2 | g37-screen swap37 |
| gs-era2-verified-board-2026-09-10 | 108 | 20 stages: all 7 session-78, the 4 pv-diag-384 last-leg verified-v1 stages, the 3 pro-verifier sweeps, flash-medium verifier, verifier-robustness T0.3, flash35 f3vf, swap37, grid verify37, gold-standard-v2 verified-v1 |
| pass-budget-pareto | 1 | verifier-robustness 384-ge3of5-t0-3 (matrix-min-T0.3) |
| pass-budget-pareto-v2 | 1 | same |
| unswept-pools-completeness | 4 | the 3 pro-verifier sweep stages |
| verifier-robustness-matrix | 5 | verifier-robustness 384-ge3of5-t0-3 (matrix-min-T0.3) |

### Unchanged verdicts that now carry unverifiable halves

- Still PASS: `55map-final-board-2026-08-27` (7 halves, stride A),
  `stride55-a5-vs-b5-2026-08-27` (1), `stride55-ladder-2026-08-27` (1),
  `stride55-sweep-oracle-2026-08-27` (2). Every pair touching these halves
  is separated by the proposer half (different geometry or rung) or shares
  the one flagged stage and the whole configuration; 0 unverifiable pairs.
- Still REFUSE, with new unverifiable pairs beside unchanged null pairs:
  `null-exemplar-sensitivity-2026-09-13` (153), `uplift-supplement-flatten`
  (137), `verifier-uplift-pairing` (136).

Full listings: `/tmp/gate-fixes/before.json`, `after-final.json`,
`compare-final.txt`, `summary-final.md` on sapphire (copies of the last two
in this scratchpad's `pr25fix/`).

## Test counts (scratch clone on sapphire, full checkout)

Full tier-1 suite, `python -m pytest -m tier1 -q -p no:cacheprovider -o addopts=""`:

```text
3875 passed, 5 skipped, 53 deselected, 3 xfailed, 4 warnings in 251.22s (0:04:11)
```

(Same counts at `73455051d` and at the final content `595e16790`.) The gate's
tier-2 tests in `tests/test_check_manipulation.py`,
`tests/test_lib_manipulation_signature.py` and
`tests/test_derive_condition_modality.py`: 9 passed. `ruff check` and
`ruff check --select E501` are clean on every touched file.

## Commits (all on the PR branch)

| Commit | Subject (characters) |
| --- | --- |
| `67bbee1a7` | fix(scripts): no PASS on unreadable verifier metas (50) |
| `e9dd5cdfc` | fix(scripts): a dead binding source voids its half (50) |
| `7caf11f9d` | fix(scripts): refuse bindings against the register (50) |
| `20b058dc7` | fix(scripts): keep run trees out of stage homes (47) |
| `d84c37dbf` | fix(scripts): type-check the bindings file (42) |
| `16b296dd0` | fix(scripts): harden the binding source resolvers (49) |
| `bca9d4c82` | feat(scripts): honour incomplete_meta in bindings (49) |
| `1c6a7d48d` | fix(results): flag 28 bindings with partial metas (49) |
| `73455051d` | docs(scripts): docstring the nested helpers (43) |
| `595e16790` | style(results): fix an article in one flag reason (49) |

Pushed subjects left as they were (finding 10): `8cc5b3078` (52 characters),
`32178f74a` (51).

## Residuals and follow-ups

1. `derive_condition_modality.stage_path_candidates` and the W4.4 resolver
   still treat a `.` path as the run tree. For `verified-cleanup-20260410`
   it is masked today (the passes manifest lists its archived meta, so the
   resolver is not consulted), but a stage with path `.` and no manifest
   entry would read the run's top-level metas. Not changed: it alters
   `derive_condition_modality`'s own outputs.
2. The register's own proposer route (`proposer_metas_of` route 1) still
   returns manifest files unchecked; all-unreadable lists make the arm
   unverifiable (no false PASS) but the pool directory is not then tried.
3. Partly unreadable meta lists (some unreadable beside readable ones) are
   tolerated as before; the full register has none among real metas.
4. Several verifier-robustness metas record temperature 0.0 for T0.3/T0.7
   legs (no `temperature_effective`): that manipulation is invisible to the
   gate (W7 class), not a partial-leg problem.
5. `tests/test_derive_condition_modality.py` keeps 12 legacy test functions
   without docstrings (untouched here).
6. The scratch clone `/tmp/gate-fixes/repo` on sapphire holds about 8.3 GB in
   tmpfs (RAM); remove it with `rm -rf /tmp/gate-fixes/repo` when no
   further re-runs are wanted.
