# The four modality rulings of 2026-09-14 — what moved, with anchors

> **Last revised**: 2026-09-14 (original publication). See [§ Changelog](#changelog) for revision history.

The PI gave four rulings on the morning of 2026-09-14, on
[`reports/modality-track-audit-2026-09-14.md`](modality-track-audit-2026-09-14.md)
and checklist item 6c
(`planning/documentation-foundation-checklist-2026-09-13.md`). All four were
executed in one session. **US$0 — no API call, no cell re-scored.** Every
number below is a group-membership consequence or a metadata correction; the
only compute was the board's permutation rebuild, on sapphire.

**The four rulings, and the one sentence each.**

| # | Ruling | Executed as |
|---|---|---|
| 1 | Insert the erratum drafted in § 7 of the audit report, index it in the companion pointer file | **E88** (E87 was the last), with three pointer rows: 12 → **15** |
| 2 | Amend the two registered-but-unsigned outcomes, the paper prose, claims row R2-06; regenerate the two tabulations and the run reports | image group **17 computable cells at MCC 0.0942–0.2907 → 21 of 22 at 0.0665–0.2907**; **two of fifteen** tile-size legs swap leaders |
| 3 | Settle `verifier_passes[...].modality` as the verifier's own exemplars and make it derive | **55 of 186** stages changed value (51 `image` → `text`, 4 `text` → `image`) |
| 4 | Rebuild the Era-2 board with corrected labels and present it for re-signature | **7 of 110** `track` labels corrected, `track_basis` on all 110, **no rank, tier, tie set, Hsu set or metric moved** |

## 1. Ruling 1 — erratum E88

**The number is E88.** `grep -c '^### E88'` returned 0 before insertion and E87
(`docs/methodology/preregistration/protocol-errata.md:5442`) was the last
entry; E88 is at `:5627`. The register goes from 87 to **88** entries.

The entry is the audit report's § 7 draft in the file's own format, with the
`Commit` field filled from the already-landed source-fix commits — `eb34ecbcc`
(the derivation and the board builder's derived `track` plus `track_basis`),
`cb9b1d7f2` (the plateau, tile-size-sweep, K-ladder-registry and pool-registry
fixes), `36b9821c4`, `c1b151bce`, `23158fc3c`, `d5eaeb1ee`, `22e69c00c` — plus
"this entry's commit" for the entry itself, which is the convention E84, E85,
E86 and E87 use (a commit cannot cite its own hash).

Three rows were added to
`docs/methodology/preregistration/osf/errata-pointers.md`, the index that
exists because the lodged registration copy is blob-pinned at `fa221b30f395`
and line-anchored by 702 commitments and so cannot carry inline pointers
(E87 remediation 1):

| § | Line | Why E88 touches it |
|---|-----:|---|
| H1 | 410–420 | The five-level factor definition — correct as lodged; what E88 corrects is how four analysis scripts RECORDED the factor's value |
| H1 | 432 | "Text-modality consistency" — the clause that makes modality a property of the *exemplar library*, and so the passage that licenses E88's derivation rule |
| H4 | 2017 | "Same instruction file per modality" — the four exemplar-ordering variants inherit their arm's image configuration, which is why they derive image and why the substring test left them in neither group |

`preregistration.md` is untouched and still at blob `fa221b30f395` (verified
with `git rev-parse HEAD:…`), so the 702 commitment anchors are undisturbed.

**The hypothesis-outcome table did NOT need regenerating.** Its deviations
column is the union over the `deviations` arrays in `results/run-analyses.json`
(`scripts/generate_hypothesis_outcome_table.py:175`), not a read of the errata
register. E88 is a revision erratum recorded inline in the outcome text — the
convention E81 and E83 followed on these same two rows, neither of which
appears in either row's `deviations` array — so no array changed and
`--check` reports **"hypothesis-outcome table up to date (15 hypotheses)"**.

## 2. Ruling 2 — the two amended outcomes, before → after

### 2.1 The signature gate, and why it did not stop the job

The brief's operational test was "verify `manually_verified_at` is absent
before editing; if either is signed, STOP". **That test does not hold, and it
is the wrong test.** Both rows carry `manually_verified_at`:

| row | `manually_verified_at` | `_signature_note` |
|---|---|---|
| `era1-single-pass-baseline-matrix` | `2026-06-09T01:22:50Z` | **absent** |
| `tile-size-sweep` | `2026-06-09T01:52:52Z` | **absent** |

In this register `manually_verified_at` is an **authoring** stamp — "set when a
human has authored/verified a row" (`results/run-analyses.json` `_README`) —
while a PI **signature** is recorded in `_signature_note` (present on
`uplift-supplement-flatten`, `verifier-uplift-pairing`,
`gs-era2-verified-board-2026-09-10`, `k-ladder-2026-09-12`, and explicitly
"UNSIGNED" on `null-exemplar-sensitivity-2026-09-13`). The audit report says
the same thing in words: "both unsigned but both carrying a verification
stamp" (§ 4, and § 1 point 4).

Neither row is PI-signed, so the amendment proceeded. The precedent is on the
rows themselves: both already carry `[REVISED 2026-08-18, erratum E81]` and
`[TIE SET REVISED 2026-08-19, erratum E83]` clauses, both later than the
2026-06-09 stamp. No signature field of any kind was touched.

### 2.2 `era1-single-pass-baseline-matrix`

| claim | before | after |
|---|---|---|
| image-bearing cells | **18**, of which **17** have a defined tile MCC | **22**, of which **21** do |
| image-bearing tile-MCC range | **0.0942–0.2907** ("0.094–0.291") | **0.0665–0.2907** |
| cells in neither modality group | **4** (`retest-phase2e::{canonical-first,canonical-last,config-default,random}`) | **0** |
| text-only cells | 14, of which 6 computable, all at 0.0665 | **unchanged** |
| text-only F1 range | 0.5016–0.6094 | **unchanged** |

Anchor: `results/modality-track-audit-2026-09-14/recomputation.md` § 3 and
`recomputation.json`, over the same 36 evaluations under
`results/paper-eval/phase2/512px-14buf-mcc/`. Mechanism: the four phase-2e
cells' pools name neither modality, and all four transmitted
`detect_brief-text-image.md` with `include_example_images` true over
`example_count` 13 — read from
`outputs/retest/phase2e/canonical-last/run_1/detections_canonical-last_run01.meta.json`.

Consumers brought to the corrected figures:

- `docs/paper/results-draft.md` § R2 prose (~`:195`), now "MCC 0.0665–0.291
  across the twenty-one computable of the twenty-two image-bearing cells
  `[E88]`", with a banner and a Changelog entry.
- The same file's 2026-08-18 changelog row, annotated rather than rewritten
  (it is the historical record of what E81 said).
- `docs/paper/results-claims-inventory-2026-09-12.md` row **R2-06**,
  re-anchored from `tiering_20m.json`-read-under-the-retired-rule to the
  audit's recomputation. **Status stays VERIFIED**, so the inventory's
  237 / 214 VERIFIED / 19 DRIFTED / 1 SUPERSEDED / 3 UNANCHORED census and
  every per-block count are unchanged.

### 2.3 `tile-size-sweep`

| leg | before | after |
|---|---|---|
| 512 `single-pass/image` | `retest-phase2d::image-terse` 0.6052 / 0.2239 | **`retest-phase2e::canonical-last` 0.6314 / 0.2132** |
| 512 `single-pass/text` | `retest-phase2e::canonical-last` 0.6314 / 0.2132 | **`retest-phase2c::text-scale-4` 0.6094 / undefined** |

The other thirteen legs are unchanged, and Views 1 and 3 are byte-identical.

**A judgement call, flagged.** The audit report left "which of the two readings
the ceiling ladder intends" open for the PI, and the ruling amends only the
legs. On inspection the published triple — "single-pass 512 (0.631) > 384
(0.520) > 256 (0.342)" — is the `single-pass/text` leg for its 384 and 256
entries but `canonical-last` for its 512 entry, so it is coherent **only**
under the retired labels: as the text leg it becomes 0.609 > 0.520 > 0.342, and
as the overall per-size ceiling 0.631 > **0.600** > 0.342 (the 384 entry moves
too). Leaving the triple unamended would have left an internally inconsistent
figure standing, so the amendment clause **states both readings** and notes
that 512 > 384 > 256 and the analysis's conclusion survive either way. The PI
may collapse it to one reading.

**The artefact regeneration carries three things beyond E88**, which is why the
2026-06-09 vintage is archived at
`archive/superseded-sweeps/tile-size-sweep-pre-e88-2026-09-14/` with its own
five-row delta table rather than silently replaced:

| # | Delta | Cause | Does it change a quoted figure? |
|---|---|---|---|
| 1 | the two 512 px legs above | **E88** | yes — amended |
| 2 | a `384 proposer-verifier/image` leg appears (`verified-adv-image-min-6of10` 0.789 / 0.8032) | register growth since the vintage | no |
| 3 | two Pro proposer-verifier rows appear in the Pro note (0.7309 / 0.8887 and 0.8792 / 0.7947) | register growth | no — "Pro single-pass ran only at 384" is still true |
| 4 | two 512 px View-1 text cells' `mcc` `0.0` → `null` | **E81** inheritance; this artefact had not been regenerated since that correction | no |
| 5 | one 384 px View-1 image cell's `mcc` 0.3295 → 0.3296 | a re-read of the cell's own evaluation | no |

### 2.4 The plateau tabulation

`results/working-precision/gs-plateau-characterisation.{json,md}` regenerated.
`summary.by_modality` is exactly the predicted result and the legacy `unknown`
bucket is empty. Three columns, because there are two different "befores" and
conflating them would misstate the effect — the **published** document covered
306 conditions, and the audit's A/B isolated the rule change at 459:

| group | published (306 conditions, legacy rule) | legacy rule at 459 | **now: derived at 459** |
|---|---|---|---|
| image | n = 99, onset median 75 m, p90 100, max 150, drift +0.0064 | n = 155, 75 m, 100, 150, +0.0064 | **n = 163**, 75 m, 100, 150, **+0.0065** |
| text | n = 164, 30 m, 75, 150, +0.0076 | n = 255, 30 m, 75, 150, +0.0070 | **n = 296**, 30 m, 75, 150, **+0.0072** |
| unknown | n = 43, 35 m, 75, 125, +0.0078 | n = 49, 40 m, 75, 125, +0.0078 | **group empty** |

Read the middle against the right-hand column and the rule change moves **no
onset median, no p90 and no maximum**, and the tail drifts by 0.0001–0.0002.
That is the audit's claim, and it holds.

**One correction to the brief's expectation.** "Nothing moves" is true of the
`by_modality` group statistics, and it was true of the audit's legacy-versus-
derived A/B at one commit. It is **not** true of the published document, which
had last been generated over **306** conditions and now covers **459**: the
`overall`, `by_architecture`, `by_tile_size`, `by_thinking` and `by_temperature`
summaries all move in n, and some in their medians (e.g. `proposer-verifier/
verified` n 71 → 224, onset median 30 m → 35 m). The tabulation is unregistered
— no analysis row cites it — so this is documentation catching up, not a
result changing.

Both tabulations are **generated projections** (registry rules
`gen-tile-size-sweep`, `gen-gs-plateau` in
`reports/verification/generated-file-registry.json`), which the PI's
2026-09-11 ruling exempts from the banner-and-changelog rule in favour of a
generated banner, a source-commit stamp and a drift guard. Neither carries a
`--check` yet — that is regime-2 work the registry already records as open —
so neither gained an in-document changelog here; their revision trail is the
archived README, the amended register rows and this report.

### 2.5 Generated projections refreshed

| artefact | command | result |
|---|---|---|
| manifests | `generate_post_run_report.py --all --write` | ALL VALID — 41 runs + 593 conditions + 1,317 passes + 68 analyses |
| register verifier | `verify_run_conditions.py` | 41 runs: **38 pass, 3 partial, 0 fail** |
| run reports | `generate_run_reports.py --all --write` then `--check` | 39 written (2 hand-authored skipped by design); **`--check` clean** |
| hypothesis-outcome table | `generate_hypothesis_outcome_table.py --check` | **up to date (15 hypotheses)** |

## 3. Ruling 3 — the verifier-modality convention

**The convention**: `verifier_passes[...].modality` records the **verifier
stage's own** exemplar modality — what that stage itself was sent — by the same
rule the proposer obeys (`include_example_images` over a non-empty exemplar
list in the transmitted configuration). It is **not** the track.

**How many stages changed value: 55 of 186.**

| | before | after |
|---|---|---|
| stages agreeing with the settled (verifier) reading | 119 of 174 derivable | **174 of 174** |
| stages contradicting it | **55** | **0** |
| direction of change | — | 51 `image` → `text`, 4 `text` → `image` |
| stages with no derivable reading | 12 | 12 — **recorded value kept, never guessed** |

The 4 `text` → `image` stages are the `session-78-matrix` family over the
`flash-high-text-n5/text-t0.7` pool
(`verified-{adversarial,brief,checklist,comparative}`), which ran the
exemplar-BEARING `verify_adversarial` / `verify_brief` / `verify_checklist` /
`verify_comparative` configs. The 51 the other way are `verify_*-text` stages
over image pools. **The split family § 6 predicted converges**:
`pv-diag-384::scale-4-optimal-487-verified-v1-{n1,n3,n5,n10}` all ran
`verify_adversarial-text` and all four now read `text` (n5 and n10 moved; n1
and n3 were already there for the wrong reason).

**Downstream**: exactly **55** verifier pass rows in
`results/passes-manifest.json` follow the register. The **447 proposer rows are
untouched**, which is the audit's "the passes manifest is clean" holding under
regeneration. No metric, rank, tier or interval anywhere — no analysis in the
corpus groups by this field.

**Where it is written, and what now derives it.**

| site | before | after |
|---|---|---|
| `scripts/derive_condition_modality.py` | the reading existed only inside the audit function | `verifier_stage_modality()` is the reusable derivation; `--fix-verifier-modality` brings the register to it; `--check` fails while any derivable stage disagrees |
| `scripts/register_k_ladder_phase2_conditions.modality` | derived the **track** | derives the stage's own modality, with the pool's modality then `"text"` as fallbacks |
| `scripts/register_verifier_stage_refresh` | hand-authored `STAGES` constant (`image` on the first entry, under the retired reading) | `apply()` derives; the constant corrected to `text` and demoted to a fallback |
| `scripts/build_gs_era2_board_opmax` | copied the membership row's **proposer** modality | derives, with the membership row's value as fallback |
| `author_second_wave_registration`, `author_verifier_robustness_registration` | hand-authored `"text"` | **left as they are** — all their values are already correct under the settled convention (they are `verify_*-text` stages), and they are one-off scripts already executed; the register-level `--check` is their guard |

**Documented** in `docs/methodology/notation-key.md` § 7 (one paragraph, beside
the proposer rule and the `text+image`-as-refinement note), in the register's
own `_README`, and in `docs/manifest-schemas/passes-manifest.schema.json`'s
`modality` description.

**Tested**: three tier-1 tests (the planner over all four cases,
`text+image` as a refinement of image, the unreadable stage returning `None`)
and one tier-2 corpus assertion. `tests/test_derive_condition_modality.py` now
holds 38 tests, all passing.

**The audit's own artefacts are deliberately frozen.**
`results/modality-track-audit-2026-09-14/verifier-pass-modality.json` still
records 119 / 55; it is the evidence the ruling rests on, and regenerating it
would erase the finding that produced the ruling.

## 4. Ruling 4 — the Era-2 board rebuilt

**The proposed outcome is: unchanged numbers, corrected metadata, and E86's
exposure disclosed.** The rebuild ran the whole 2026-09-13 chain — membership,
`build_board_tiering_input.py`, `era1_leaderboard_tiering.py --permute-mcc`
(10,000 permutations, seed 42, both families on one swap stream; 51 min
single-core), `selection_aware_intervals.py` for the **MCC** MCB and then the
**F1** MCB last over the final membership, `build_gs_era2_board.py gates`, and
`finalise --no-analysis-row` — on sapphire, in the worktree
`~/worktrees/map-reader-llm/claude-rulings`. US$0, no API call, no cell
re-scored.

### 4.1 The metadata that changed

| | before | after |
|---|---|---|
| `track` source | `"image" if "image" in label else "text"` | **derived from the transmitted proposer configuration** |
| `track` labels corrected | — | **7** |
| `track_basis` | absent | **on all 110 members**: `pass-metadata` 57, `run-metadata` 23, `config-file` 17, `pool-name-token` 12, `register` 1 |
| Members / excluded | 110 / 161 | **110 / 161**, identical id sets |
| Other member field changes | — | **0** |

| cell | before | after | mechanism |
|---|---|---|---|
| `proposer-verifier-384::verified-adversarial-image` | image | **text** | the token names the image **verifier**; proposer `detect_brief-text`, `include_example_images` false |
| `proposer-verifier-384::verified-brief-image` | image | **text** | as above |
| `proposer-verifier-384::verified-checklist-image` | image | **text** | as above |
| `pv-diag-384::pv-scale4-optimal-n1-opmax` | text | **image** | no modality token; the test fell through. Proposer `detect_h8_scale-4_v2`, instruction `detect_brief-text-image.md`, `include_example_images` true, 13 exemplars |
| `pv-diag-384::pv-scale4-optimal-n1-carried-p0.15-k1` | text | **image** | as above |
| `pv-diag-384::pv-scale4-optimal-n3-opmax` | text | **image** | as above |
| `pv-diag-384::pv-scale4-optimal-n3-carried-p0.15-k3` | text | **image** | as above |

Record: `rebuild-track-2026-09-14/track-deltas.json` (`passed: true`).

### 4.2 The board line — nothing numerical moved, and it was measured

| Quantity | before | after |
|---|---:|---:|
| Cells admitted / tiered / withheld | 153 / 150 / 3 | **153 / 150 / 3** |
| F1 pairs significant at BH q = 0.05 | 7,961 / 11,175 | **7,961 / 11,175** |
| F1 tiers | 14 | **14** |
| F1 Tier 1 / tie set | the five 3.7 / 3.8 cells / 5 | **the same five, same order / 5** |
| Top cell | `g37-image-k5-verified-swap37-p0.90-k5` 0.9233 | **the same cell, 0.9233** |
| Hsu F1 MCB admissible set | 65 of 150 | **65 of 150** — artefact byte-identical |
| MCC pairs significant | 2,982 / 11,175 | **2,982 / 11,175** |
| MCC tiers / tie set | 6 / 33 | **6 / 33** |
| Hsu tile-MCC MCB admissible set | 59 of 150, 9 shared with the F1 set | **59 of 150, 9 shared** — artefact byte-identical |
| Withheld cells | the three Gemini 3.7 GS text rungs, F1 0.8338 / 0.8495 / 0.8860 | **the same three, the same F1** |
| Gates | G2 0 / G3 0 / G4 110 / 110; G6 max abs delta 0.0078 | **identical** |
| Signature paths byte-equal | 10 of 10, PASS | **10 of 10, PASS** |

`rebuild-track-2026-09-14/both-arms-identity.json` reports
`f1_arm_identical` **true**, `mcc_arm_identical` **true**,
`both_arms_identical` **true**, and `keys_that_moved` **empty** — so even the
withheld-cell block is unmoved. This is a **stronger** check than the
2026-09-13 rebuild's, whose sibling harness deliberately exempted the then
brand-new `mcc_permutation` block from comparison; here both families are in
scope. Both MCB artefacts came back byte-identical under `git diff`. The only
things that moved in `tiering_20m.{json,md}`, `gates.json` and
`frame-deltas.md` are run stamps and the source commit.
`tiering-input/run-analyses.json` is a fresh register snapshot, so it picks up
this session's two E88 outcome amendments and the
`null-exemplar-sensitivity-2026-09-13` row registered since the last snapshot.

The before state is not duplicated in the job directory (git holds it, as the
2026-09-13 job also decided); `track-deltas.json` records the blob hashes —
`membership.json` `e9900fa370f2`, `tiering_20m.json` `b4a39f3a4350`,
`provenance.json` `1aecf12352ae`, `results/run-analyses.json` `fd5ffb3136ac`.

### 4.3 Signatures, untouched

`finalise --no-analysis-row` carried `signed_at` (still
`2026-09-12T06:04:30Z`), `signature_history` and `gates.G1.pi_ruling` forward
and nested the previous PENDING block as `re_sign_pending.previous_pending`
rather than overwriting it; the board's signed analysis row was not written at
all. **Ten signature-bearing paths asserted byte-equal**, the whole register
file included: `rebuild-track-2026-09-14/signature-paths.json`, **PASS**. No
signature field of any kind was altered. `re_sign_pending.reason` now names this
ruling, and the board awaits **one** re-signature covering both rebuilds'
changes.

### 4.4 E86's disclosure, added to the README

The board page now carries, immediately above the tile-MCC section: the
exposure (**20 of the 487** frame tiles overlap null-exemplar pixels, from
`inputs/examples/null-tiles/null_overlap_by_frame.json`), the fact that no
reference symbol lies inside a null window so no published value is invalid,
and the sensitivity result from
`results/null-exemplar-sensitivity-2026-09-13/findings.md` — image-bearing
cells' FP-rate ratio on the exposed tiles **0.561** against text controls'
**0.685** (mean log ratio −0.1433 against −0.0552, difference **−0.0881** at
*p* < 0.0001, **−0.0773** stratified within the single `pv-diag-384` run); the
largest movement of any Era-2 cell **0.0074** in F1@20 and **0.0120** in
tile-MCC; and the reduced-frame tie-set edges (F1 Tier 1 five cells → four, the
lost cell a *text* cell; F1 tiers 14 → 13; tile-MCC Tier 1 33 → 28; the two
admissible sets by one and two members, with the top of both rankings and the
selection-aware winner under both metrics unchanged). The board is **not**
re-scored on the reduced frame — which frame the paper reports is the PI's call.

### 4.5 One behaviour worth recording

`build_gs_era2_board.py renderings` **overwrites the README's `Last revised`
banner** with a generic "original publication" stub, as it did on 2026-09-13
(restored by hand in `9a440644d`). The hand-authored banner was restored here
with every prior revision preserved. A future rebuild will hit the same thing;
the fix belongs in the builder, which either should not write that line or
should be given the banner to write.

### 4.6 What the correction does to a reading, if not to a number

Two of the four `pv-scale4-optimal` cells sit in **tile-MCC Tier 1**. The
ruling-7 finding that MCC Tier 1 is "led by single-pass **image** proposer +
verifier baselines" is now correctly named for two more of its members, and
three cells the board would have called image are text controls. No count in
Obs 482 changes, because Obs 482 makes no by-track count of Tier 1 — but a
future by-track count would have been wrong on 7 of 110 cells, in both
directions.

## 5. What did NOT change

- **No preregistered outcome, and no hypothesis-outcome row.** H1's
  confirmatory contrast `h1-cmt0106-pooled-modality` groups the five phase-2a
  conditions, every one correctly labelled; the confirmatory family takes one
  *p* per hypothesis and none was recomputed.
  `generate_hypothesis_outcome_table.py --check`: up to date, 15 hypotheses.
- **No signed analysis row.** `uplift-supplement-flatten` (signed 2026-09-10),
  `verifier-uplift-pairing` and `gs-era2-verified-board-2026-09-10` (both
  2026-09-12) and `k-ladder-2026-09-12` (2026-09-13) are untouched; none of
  them groups by a modality field.
- **No cell re-scored, no API call, US$0.** Every movement above is group
  membership or metadata.
- **`results/k-ladder-2026-09-12/phase2/unions.json`** keeps its two `text`
  scale-4 rungs. Regenerating it would rebuild the consensus unions and
  rewrite `experiment_intent.md` files inside a **signed** analysis; the source
  constant is fixed and the artefact corrects at the next Phase 2 union
  rebuild. This is the audit's deliberate non-correction, unchanged by the
  rulings.
- **The direction of every claim.** The metric trade-off (20 of 21 computable
  image-bearing cells strictly above every computable text-only cell, the
  twenty-first tying it), the tile-size architecture dependence, Obs 351,
  Obs 352, Obs 447 and Obs 482 all stand.

**The state of the tripwire, for the record.** After all four rulings,
`scripts/derive_condition_modality.py --check` reports **0 condition
mismatches** (was 8 — the seven board `track` rows and
`retest-phase2e::canonical-last` in the tile-size sweep; the three plateau rows
are the same three board cells) and **1 pool mismatch**: the
`scale-4-optimal-487` rung in `results/k-ladder-2026-09-12/phase2/unions.json`,
deliberately deferred above. So `--check` still exits **1**, on exactly that one
known, documented deferral and nothing else. No test asserts a zero exit, so
nothing in the suite depends on the waiver; a reader running the command should
expect that single line.

## 6. Open for the PI

1. **The board's re-signature** — `provenance.json` → `re_sign_pending`.
2. **Which reading the `tile-size-sweep` ceiling ladder intends** (§ 2.3). The
   amendment states both; one could be chosen.
3. **The Obs candidate** in § 10 of the audit report — "a derived factor label
   is a measurement, and this corpus was deriving one by substring" — accepted
   or declined.
4. **The second nondeterministic `provenance.source_files` row**:
   `55maps-generalisation::verified-paired` joins
   `gold-standard-v2::consensus-4of5` (checklist item 6a) in alternating
   between two `results/uplift-supplement/verifier-pairing/` evaluation paths
   across regenerations with no input change. No metric is affected; the
   register's owner may want the extractor made deterministic.
5. **Regime-2 compliance for the two regenerated tabulations** — neither
   `tile_size_sweep` nor `gs-plateau-characterisation` has a generated banner,
   a source-commit stamp or a `--check`. Both are registered as generated and
   both are in the registry's open set.

## Changelog

### 2026-09-14 — Original publication

Claims-with-anchors record of the four PI rulings of 2026-09-14 on the
modality-track audit, all executed in one session: erratum **E88** and its
three pointer rows; the two registered-but-unsigned outcomes amended and their
consumers corrected; the register's `verifier_passes[...].modality` convention
settled as the verifier's own exemplars, with **55 of 186** stages changed; and
the Era-2 board rebuilt with derived `track` labels, a `track_basis` field on
all 110 members and E86's null-exemplar disclosure, with no numerical movement.
No prior revision to diff against.
