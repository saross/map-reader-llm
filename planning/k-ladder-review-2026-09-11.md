# K-ladder review: pass count at fixed parameters, Pareto-framed

> **Last revised**: 2026-09-13 (latest — the review's **three withheld rungs
> and its MCC reading both reach the Era-2 board**, which was REBUILT under
> checklist item 6 and awaits the PI's re-signature. The board now carries a
> **tile-MCC permutation family** on the same swap masks as F1 (ruling 7),
> reported beside the preregistered F1 tiering and not replacing it: 2,982 of
> 11,175 pairs significant, 6 MCC tiers, MCC tie set 33, MCC MCB 59 of 150. It
> **corroborates § 4 and the MCB job's PARETO MCC SET reading at board scale** —
> no F1 Tier-1 cell is in MCC Tier 1, MCC Tier 1 is 33 cells drawn entirely
> from F1 tiers 6–12 and led by single-pass image cells, and the two admissible
> sets share only 9 members of 65 and 59. The three Gemini 3.7 gold-standard
> text rungs stay admitted-and-withheld from BOTH families under ruling 6, now
> with the shortfall counts and both tile vocabularies published; the K = 3
> rung's board figure is corrected to F1@20 **0.8860** / 495. Deltas:
> `reports/era2-board-mcc-family-2026-09-13.md`. Before that — the **MCB job**
> executed at zero API
> cost: the PI's two afternoon rulings landed and the review's analysis row is
> **ready for signature**. The per-family **Hsu MCB sets are supplied** for all 22
> tiered ladders on F1 and tile-MCC with the Era-2 board's own MCB step, each
> ladder on its own frame — K = 3 admissible on 12 of 22 and the cheapest
> admissible rung on 10, **no** ladder's F1 set excludes K = 10, K = 1 ruled out
> on F1 on 20 of 22 and admissible on tile-MCC on **22 of 22**, one family
> withheld — and the **carried convention is settled**: the stride ladder's own
> vote shell is the carried point, `k = K` stays as a disclosed column, no number
> recomputed. § 6's step-5 scope note is corrected accordingly; closing report
> `reports/k-ladder-mcb-deltas-2026-09-13.md`. Before that — the **ADMISSION job**
> executed: the PI
> ruled the close-out's morning list and all four items landed at zero API cost:
> the 46 Phase 2 rungs and the 4 tier E rungs admitted to the Era-2 board by (a)
> (103 → 153 cells admitted, 150 tiered; Tier 1 unchanged), the signed
> `uplift-supplement-flatten` rename confirmed, the stride-B K = 5 rung under the
> 3.7 verifier finished and registered without re-tiering the 55-map board, and
> the verifier-stage tile-MCC reversal stated as a claim in `findings.md` § 8.6;
> per-item outcome in [§ 9](#9-the-admission-job-what-landed-2026-09-13). Before
> that — the CLOSEOUT job executed: tier E at
> US$4.9595 against a US$5.02 approval, the tension analyses answered, the
> analysis row authored UNSIGNED, two items stopped; per-item outcome in
> [§ 8](#8-the-closeout-what-landed-2026-09-12). Before that — **Phase 2 EXECUTED at
> US$24.8065** against the PI's US$24.84 approval of tiers A–D; per-step
> outcome in [§ 7](#7-phase-2-what-landed-2026-09-12). Earlier the same day:
> **Phase 1 EXECUTED at US$0**, steps 0–7, per-step outcome in
> [§ 6](#6-phase-1-what-landed-2026-09-12); before that R1–R5 RULED and two
> project principles recorded, B3 ruled, the 27 first-N twins derived inside
> this job; prior 2026-09-11: DRAFT scaffold, S153, from committed material
> only). See [§ Changelog](#changelog).

**Status**: SCOPING CARD; the run card it produced is
`planning/k-ladder-phase1-run-2026-09-12.md`. **Both phases have been
executed** — Phase 1 at US$0 (§ 6) and Phase 2 at US$24.8065 (§ 7), the latter
against the costing in `reports/k-ladder-phase2-costing-2026-09-12.md`. The PI
asked in Session 152 for
a review of the pass-count ladder — K = 1, 3, 5, 10 at fixed parameters,
framed as a Pareto (cost-against-F1) question, together with a ruling on
whether re-materialised and current-vintage cells belong on the board
(`planning/paper-writeup-continuity.md`, "STATE AFTER S152", item B4).
This card scopes that review so the PI can rule on it before anything
is computed. Every number below is re-read from the file cited beside it.

## 1. The question

Across the study the number of proposer passes (K) has been treated as a
cost lever whose F1 return saturates early. Three registered analyses
already say so on three instruments, but each ladder varies something
besides K, and the Gold Standard (GS) Era-2 verified board excludes
K = 1 cells by rule. The review asks:

1. **At genuinely fixed parameters** (one tile geometry, one thinking
   level, one temperature, one verifier, one operating-point rule), what
   does F1 do across K = 1, 3, 5, 10?
2. **On a Pareto framing**, which rungs are efficient once the audited
   per-pass cost is attached, on GS and projected to the 55-map corpus?
3. **Board membership**: should the K = 1 rungs (excluded as
   "single-pass proposer + verifier") and any rung that exists only as a
   re-materialised or current-vintage cell sit on the Era-2 board, or on
   a separate ladder table?

## 2. What already exists ($0, committed)

| Ladder | K rungs | Fixed | Varies besides K | Result | Anchor |
|---|---|---|---|---|---|
| `pass-budget-pareto-v2` (GS, Era-2 frame) | 6, 11, 31, 35 total passes | 384 px, curator GT, 20 m | thinking level (min vs HIGH), temperature, verifier input rule | all seven rungs one statistical tier; efficient set min6 $2.43 / 0.8784, min11 $4.00 / 0.8835, high31 $69.21 / 0.8902, high35 $71.23 / 0.8951; MCB admissible 6 of 7 | `results/run-analyses.json` row `pass-budget-pareto-v2`, outcome text; signed 2026-06-12 |
| `grid-2026-08-18` K-ladder (GS, grid-common frame) | 1, 3, 5, 10 | per cell: geometry, MINIMAL text, T 0.7 | consensus-only until the 2026-08-24 verifier stage; only K = 10 verified | union recall 0.8972 → 0.9229 → 0.9393 → 0.9416 at 512 / 50 %; "diminishing returns in K are steep"; vote optimum at the grid edge at K = 3 | `results/grid-2026-08-18/findings.md` lines 196–202 |
| `stride-winner-ladder-exact-2026-08-25` (GS, B geometry) | N = 1, 3, 5 (of K = 10) | 384 / 50 %, MINIMAL text, carried verifier | first-N sub-pools of one K = 10 run, not independent runs | N = 1 0.8677; N = 3 0.8911 (~$2.64 all-in); N = 5 0.8856; N = 3 within noise of K = 10 (0.8982) | `results/run-analyses.json` row `stride-winner-ladder-exact-2026-08-25`; Obs 436 |
| `stride55-ladder-2026-08-27` (55-map, r2) | first-N rungs of A and B | as above at deployment | first-N sub-pools | P2 pass exact; saturation by N = 3 for the all-3.7 stack (§ R7.3) | `results/run-analyses.json` row `stride55-ladder-2026-08-27` |
| Gemini 3.7 screen (GS, grid-common) | 5, 10 | B geometry, 3.7-low text, T 0.7 | none | K = 10 adds +0.0003 over K = 5 (0.9142 vs 0.9139) | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/membership.txt`; `planning/gemini38-screen-2026-09-04.md` cells table |

Rung inventory in the conditions register, verified cells on the GS
pools (`results/conditions-manifest.json`, field `n_passes`, counted
2026-09-11): `pv-diag-384` has K = 1 (24 conditions), 3 (6), 5 (65),
10 (31), 30 (2); `verifier-robustness` K = 1 (2), 5 (12);
`grid-2026-08-18` K = 10 only (11); `gemini37-screen` K = 5 (6), 10 (2).
So a K = 1 / 3 / 5 / 10 ladder at fixed parameters **may already be
scorable from committed pools** for the Gemini 3 MINIMAL-text 384 px
family in `pv-diag-384`, if its K = 3 and K = 1 conditions share the
K = 5 / K = 10 cells' temperature, thinking level, and verifier. That
check is § 3 step 1, and it is $0.

## 3. Proposed review, in order (all $0 unless stated)

1. **Inventory the fixed-parameter ladders that exist.** For each GS
   family (Gemini 3 MINIMAL text 384 px; Gemini 3 HIGH text; Gemini 3
   image; 3.7 text; 3.7 image), list the committed verified cells at
   K = 1, 3, 5, 10 whose non-K parameters are identical, from
   `results/conditions-manifest.json`. Output: one table, gaps marked.
   Expected: the Gemini 3 MINIMAL text family is complete or nearly so;
   3.7 has K = 5 and 10 only; image has K = 5 and 10 only.
2. **Fill gaps from existing pools where the first-N rule permits**
   (sub-pool consensus with `merge_passes --passes 1..N`, the
   preregistered rule used in Session 106) and re-verify only where a
   verifier pass over a smaller union is missing. Any verifier call is
   API spend and is gated: cost it per family before running.
3. **Score every rung on the board's own frame** (`era2-b-487`, 20 m,
   tile-MCC alongside F1) with the board instrument
   (`scripts/era1_leaderboard_tiering.py`), on sapphire. Paired
   tile-swap permutation between adjacent rungs; BH q = 0.05; Hsu MCB
   admissible set per family.
4. **Attach audited cost per rung** on the token-load-audit basis
   (`reports/token-load-audit-2026-06-12.md` pattern; the 3.7 rates
   from the S153 R7 deltas report once it lands). Pareto frontier per
   family on GS, then the 55-map projection column as
   `pass-budget-pareto-v2` did (tile factor 8,541 / 487).
5. **Write one findings document** with the Pareto figure and a
   per-family ladder table, and register one analysis row for the PI to
   sign. Feed the Results outline (§ R6 frontier) as a claims-with-anchors
   delta, not prose.

## 4. Rulings — given by the PI on 2026-09-12 (originally "needed before step 1")

**Two principles the PI stated with the rulings, recorded as project rules:**

- **Keep history, present the best available.** Registers keep every
  run; nothing is rewritten. Anything paper-facing — leaderboards,
  ladders, tables, results documents — carries, for each configuration,
  the best-QUALITY cell available: the one on the most complete inputs,
  the sound vintage, the current reference and frame, usually the newest;
  never chosen on F1. When a board's representative for a configuration
  changes, the board's changelog says so and the superseded cell stays in
  the register and the supplement.
- **Ladder, then board.** Each major lever (pass count K, stride, tile
  size, temperature, thinking level, model family) is analysed in
  isolation as a ladder at otherwise fixed parameters, registered as its
  own analysis; then every cell, ladder rungs included, feeds the board.
  This is the preregistration's factor-at-a-time intent, reached by a
  different road.

- **R1 — RULED: the carried Gemini 3 verifier at every rung, no
  swapping.** The ladder's question is the proposer's pass count.
- **R2 — RULED: report both operating points; tier on the sweep-optimal
  on the board frame (the `-opmax` convention, Obs 466 gate); show the
  carried point (prob 0.15, k = K) as the transfer-tax column.**
- **R3 — RULED: the ladder carries K = 1, AND a K = 1 cell that earns a
  place on a board is admitted.** The board's twenty single-pass
  exclusions were a scope choice of the inventory builder (architecture
  class), not a statistical one; under "ladder, then board" the board
  takes every verified cell on its frame regardless of K, and the
  Era-2 board is re-tiered and re-signed with them in.
- **R4 — RULED (with a clarification): compare like with like by
  rebuilding older cells on the best available inputs, and let the best
  available cell per configuration stand on ladders and boards.** The
  PI's framing was "the ground truth is a moving target"; the
  clarification (accepted 2026-09-12) is that three things move
  separately. (a) The REFERENCE (ground truth) and (b) the FRAME are
  already held fixed by the board: every cell is re-scored on one
  reference and one frame (gate G1), and the 55-map cells on r2. The
  Gold Standard curator reference has not moved. (c) The CANDIDATE
  VINTAGE is what B2 was about: a union rebuilt from recovered passes is
  a different input set, and a verifier's probabilities are API output
  tied to the candidates it saw, so an old cell cannot be "re-scored" on
  a new union — it has to be re-verified (API spend). The vintage guard
  (`scripts/check_pv_sweep_vintage.py`) says the exposure is small: of
  the 30 registry cells, 24 same-vintage, 4 probabilities-grew (already
  re-swept 2026-09-08), 1 union-rebuilt (`pv-high-text-t0.0-n3`, whose
  current-vintage pair was re-verified 2026-09-08 for US$1.82), 1
  manifest-mode. So R4 in practice: register the September pair of
  `pv-high-text-t0.0-n3` under its own name as the best available cell
  for that configuration (the April pair stays as the archived board's
  cell — B2); re-verify any other cell whose union is newer than its
  probabilities, costed under R5; and every cell is scored on the current
  reference and frame by the board as now.
- **R5 — RULED: up to US$50 for loose ends, every run costed and
  approved by the PI first; batching approvals is fine.** The 3.8
  screen's verifier arm cost about US$0.82 billed per 791-candidate
  union, so gap-filling verifier passes are cents to a few dollars each.

## 5. What this card does not do

It does not re-open the pass-budget Pareto's efficient set, the E83 MCB
ruling, or the stride ladders' registered outcomes. **It DOES now own
the uplift supplement's 27 truly-absent first-N twins**: the PI ruled on
2026-09-12 (B3) that their pre-verifier universes are derived inside this
ladder job, under its gates, rather than by a separate re-run — the
rungs of `stride-55map-2026-08-25` A and B (23 pairs) and
`gemini37-55map-2026-08-29` arms 1 and 2 (4 pairs), re-clustered from
the first N passes exactly as `scripts/stride55_ladder.py` and
`scripts/gemini37_arm_ladder.py` do, materialised, registered as
conditions, and scored on the cells' own recipes. Step 2 therefore
includes the 55-map rungs, not only the GS families, and the uplift
supplement is regenerated when they land.

## 6. Phase 1: what landed (2026-09-12)

Executed on branch `worktree-agent-a51feb87262e915a2` under
`planning/k-ladder-phase1-run-2026-09-12.md`. **Zero API calls.** Every
scoring, permutation, bootstrap, clustering and tiering step ran on sapphire.

| Step | Outcome | Artefact |
|---:|---|---|
| 0 | **landed** — written before anything ran | `planning/k-ladder-phase1-run-2026-09-12.md` |
| 1 | **landed** — 187 (run, pool, verifier, frame, reference) groups; 24 with ≥ 2 rungs; **8 ladders with ≥ 3 of {1, 3, 5, 10}, all already committed**; 30 gaps need a verifier pass and **none is fillable at US$0 exactly** | `results/k-ladder-2026-09-12/inventory.md` + `.json` + `inventory-tables.md` + `subpool-coverage-probe.json` |
| 2 | **landed** — all 9 distinct first-N rungs materialised and gated; the worklist's 27 `blocked` rows are `ready` on basis `first-n-recluster`; 170 rows, **0 blocked** | `scripts/materialise_first_n_ladder_twin.py`, `results/uplift-supplement/verifier-pairing/first-n/`, regenerated worklist and uplift CSVs |
| 3 | **landed** — the September pair registered as `pv-diag-384::pv-high-text-t0.0-n3-recovery-2026-09-08-opmax`; the April cell untouched | `results/run-conditions.json`, `docs/methodology/notation-key.md` § 7.2 |
| 4 | **landed** — K = 1 admitted; board 79 → **103** cells; all gates pass; re-tiered and MCB recomputed; `re_sign_pending` recorded. **Superseded 2026-09-13** by the admission job (§ 9): the board is now **153 cells admitted, 150 tiered** | the board directory; `archive/superseded-leaderboards/gs-era2-verified-board-2026-09-10-79cell-pre-k1/` |
| 5 | **partial** — see the scope note below | `results/k-ladder-2026-09-12/findings.md` |
| 6 | **landed** — 28 rungs, 35,844 candidates, **US$24.84** at the audited Gemini 3 verifier rate; R4 re-verification exposure **nil** | `reports/k-ladder-phase2-costing-2026-09-12.md` |
| 7 | **landed** | `reports/k-ladder-phase1-deltas-2026-09-12.md` |

**Two expectations in this card did not survive execution**, both recorded in
the inventory:

- § 3 step 1 expected the Gemini 3 MINIMAL text family to be "complete or nearly
  so" at K = 1/3/5/10. It is not: every Gemini 3 `pv-diag-384` family holds
  exactly two rungs, K = 5 and K = 10, at each of T 0.3 / 0.7 / 1.0. The K = 1
  and K = 3 counts this card quoted (24 and 6) were over all 128 conditions of
  that run, not the verified ones.
- § 3 step 2 assumed gaps could be filled "from existing pools where the first-N
  rule permits", re-verifying "only where a verifier pass over a smaller union
  is missing". Measured, that exception is the rule: a first-N sub-pool union is
  neither a positional prefix of a longer committed union nor a coordinate
  subset of it, because the consensus builder records each cluster's MEAN
  centroid, so adding passes moves it. **Every** gap needs a verifier pass.

**Step 5's scope, stated plainly.** The ladder tables cover all eight families
at their own headline buffer from committed evaluations, with audited cost per
rung where a committed figure exists, and the gold-standard stride-A ladder was
re-scored on the board frame and tiered with the board instrument verbatim. The
55-map ladders' pairwise significance is **cited from their own registered
instrument** (the per-map paired sign-swap permutation of `stride55_ladder.py`
and `gemini37_arm_ladder.py`) rather than re-run under the board's tile-swap
instrument, which is defined on a tile grid and a different scoring engine. A
per-family Hsu MCB set is supplied for the gold-standard ladder only. What is
missing is named in the findings document, not glossed.

**Step 5's scope, closed 2026-09-13.** Both gaps that note left open are now
filled and the two sentences above are superseded:

- The 55-map ladders' pairwise significance **was** re-run under the board's
  tile-swap instrument on 2026-09-12 (`findings.md` § 4.1,
  `reports/k-ladder-mcc-test-2026-09-12.md`), gated against the committed board
  `pairwise` tables on all 25 pairs, with the registered per-map sign-swap
  reported beside it as the cross-check; the PI's choice of instrument is ruled
  and recorded in the analysis row.
- A per-family Hsu MCB set is supplied for **all 22 tiered ladders**, not the
  gold standard alone, on F1 and on tile-MCC (`findings.md` § 6.1,
  `results/k-ladder-2026-09-12/mcb/`, driver `scripts/k_ladder_mcb.py`, gate
  passed on 170 candidate rows). The twenty-third ladder — the Gemini 3.7
  gold-standard text screen — has none on either metric, because the tile-join
  invariant withholds three of its four rungs' per-tile table; it is listed
  rather than dropped.

**With both filled, the review's analysis row `k-ladder-2026-09-12` is ready for
the PI's signature.** It is still UNSIGNED (`manually_verified_at: null`), its
outcome now states the MCB result and the carried convention, and its
`_signature_note` records the one thing still open — the corpus-wide tile-join
decision — which is the board's question rather than this row's.

## 7. Phase 2: what landed (2026-09-12)

Executed on branch `worktree-agent-ae87367bcee3e0e5c` against the PI's approval
of all four tiers of `reports/k-ladder-phase2-costing-2026-09-12.md` § 5 at
**US$24.84**. Spent **US$24.8065** audited flex — 28 rungs, 35,844 candidates
offered, **35,844 verified, 0 failed**, no rung stopped. Closing report:
`reports/k-ladder-phase2-deltas-2026-09-12.md`.

| Step | Outcome | Artefact |
|---:|---|---|
| 1 | **landed** — 28 first-N unions at US$0; all 28 candidate counts reproduce the costing table **exactly** (delta +0), and an independent re-derivation classifies all 28 `SUBPOOL-CONSISTENT`, zero `STALE` | `scripts/build_k_ladder_phase2_unions.py`, `phase2/unions.json`, `phase2/union-provenance.json` |
| 2 | **landed — READY**, 0 blockers, 3 warnings; 9 preregistration requirements, 12 transmission modes all PASS, one deliberate deviation (E56), a 5-candidate smoke run | `phase2/pre_launch_audit.md` |
| 3 | **landed** — tiers A (4.4641), B (8.7115), C (8.9654), D (2.6655); every per-tier rate inside the audit's 0.000684–0.000698 spread; the flex correction applied by the accounting because the verify path records the tier nowhere | `phase2/spend-ledger.json` |
| 4 | **landed** — 46 cells swept on both 487-tile frames (which agree on the argmax **28 of 28**), materialised, scored on the board recipe, and registered as **46 condition rows** (542 → 588, all schema-valid, validator profile unchanged); 13 of 14 ladders tiered with the board instrument and `--permute-mcc`, all gates passed | `phase2/scores.json`, `phase2/ladders.json`, `phase2/mcc-test/`, `findings.md` § 7 |
| 5 | **landed** — the closing report; the uplift supplement needs no re-pairing and the signed uplift row is untouched (all 46 rows are board-frame rows, excluded by the PI's 2026-09-10 rule: exclusions 103 → 149, pairable 170 unchanged) | `reports/k-ladder-phase2-deltas-2026-09-12.md` |

**What the purchase answered.** § 6.3 of the findings had recorded that no
Gemini 3 `pv-diag-384` family reached the three-rung bar. All thirteen now carry
four rungs, and so does the 3.7 gold-standard screen. The result is that **K's
return is governed by the proposer's thinking level, and within a level by its
temperature**: the K = 1 → best-rung F1 gain is significant on 7 of 7
HIGH-thinking ladders and 2 of 6 MINIMAL ones, and **four ladders — all
MINIMAL — are a single statistical tier in which K buys nothing detectable**.
The § 4 tile-MCC direction is corroborated on fourteen more ladders and gains
the corpus's first significant instance.

**Three things this card should record as not settled.** (a) The 46 new cells
are not on the Era-2 board; admitting them is a re-tier and a re-signature and
so a PI matter under "ladder, then board". (b) The corpus holds two readings of
R2's "carried point" and they diverge sharply above K = 3; both are computed and
the choice is put back. (c) Tile-MCC is computed by a **string** join on
`source_tile`, so a cell scored on a frame whose tile vocabulary differs from
its proposer's tiling gets a correct F1 beside a meaningless MCC — measured on
3 of 47 Phase 2 cells, withheld rather than published, and the repair put to the
PI (deltas § 6.3, § 8).

**One expectation in this card did not survive Phase 2**, and it is recorded
here as § 6 recorded Phase 1's two. § 5's ruling R5 budget framing held, but the
costing's tier-A rationale claimed the two T 0.7 pools "also hold a K = 30
rung", making five rungs possible. They do not: both K = 30 cells are
`aggregation: "consensus"` with `verifier_config: null`, so ruling R1 excludes
them. The correction is in the costing's own changelog.

## 8. The closeout: what landed (2026-09-12)

Executed on branch `worktree-agent-ae1e65fd9508397ec`. Eight items briefed;
**five landed complete, one partially, two stopped.** The only API spend was
tier E, approved by the PI that evening at US$5.02 and executed for
**US$4.9595** — 7,239 of 7,239 candidates verified, 0 failed, hard stop US$7.00
never approached. Closing report:
`reports/k-ladder-closeout-deltas-2026-09-12.md`.

| # | Item | Outcome | Artefact |
|---:|---|---|---|
| 1 | Tier E: the grid 384/50 MINIMAL text K = 1, 3, 5 rungs | **landed** — US$4.9595 audited flex; all three union counts reproduce the PI's approved figures exactly (delta +0); READY audit, 0 blockers | `results/k-ladder-2026-09-12/tier-e/`, `scripts/run_k_ladder_tier_e.py` |
| 2 | The K = 5 fill for stride B under the 3.7 verifier | **partial** — the generator defect found and fixed, the sweep regenerated with every gate passing; the register row and the 55-map board re-tier are put back | `scripts/final_board_sweeps.py`, deltas § 5 |
| 3 | The tension analyses | **landed, and they answer the question** — the two corpora agree once resolution is accounted for | `results/k-ladder-2026-09-12/tension/`, `findings.md` § 8 |
| 4 | The analysis row | **landed, UNSIGNED** — `conditions_compared` derived from the ladder inventories, every id checked against the register | `results/run-analyses.json` row `k-ladder-2026-09-12` |
| 5 | The five stale T = 1.0 unions | **landed** — relabelled `consensus-{1..5}of5` with `n_passes: 5`, propagated, erratum **E85** | `docs/methodology/preregistration/protocol-errata.md` |
| 6 | The two stale h10 consensus files | **landed** — archived and rebuilt to 1,474 / 477, reproducing the retrospective's prediction exactly; `t3`–`t5` deliberately left | `archive/superseded-consensus-2026-09-12/` |
| 7 | E72 propagation | **landed** — a nullable `caveat` field through the manifest generator and its schema, and the register caveat into the supplement's `notes` | `scripts/generate_post_run_report.py`, `scripts/build_uplift_supplement.py` |
| 8 | The Era-2 board rebuild | **STOPPED** — the builder refuses all 46 cells by two rules that are correct behaviour; admitting them is a design decision | deltas § 8 |

**What the closeout settled that this card could not.** § 4's ruling R2 and the
Phase 2 § 7 note both left open whether the gold standard's MINIMAL null results
meant K does not pay there or that 487 tiles cannot see it. The subsample test
answers it: the deployment ladders' **own cells**, scored on random 487-tile
subsets of their own 8,541 tiles, keep BH significance in 197 of 200 draws at
ΔF1 +0.0547 and in only 39 of 200 at +0.0192. **At 487 tiles the instrument
resolves a ΔF1 of about 0.03 and above, and not below** — and the nine MINIMAL
ladders sort by effect size rather than by corpus.

**Three expectations in the brief did not survive execution**, recorded here as
§ 6 and § 7 recorded Phase 1's and Phase 2's.

- The brief named `scripts/gemini37_fourth_cell_ladder.py` as the script that
  built § 3.3's ladder. It is not: that script's own committed output computes
  different numbers against a different reference. The provenance is
  `final_board_sweeps.build_g37_families`, and the missing K = 5 rung was a
  one-line asymmetry in its rung loop (deltas § 5).
- The brief supposed the Era-2 board could be rebuilt with the 46 Phase 2 cells
  admitted. The builder refuses **all 46**, on the frame rule and the
  `scope_override` rule, and both refusals are correct: the cells are already
  scored on the board's own frame, which is what those rules exist to exclude.
  Admission needs a mechanism, and the choice has consequences (deltas § 8).
- The brief supposed tier E's cells would score cleanly. They did not: the tile-
  join invariant refused all six, because the grid pool's proposer ran on the
  192 px stride ov192 tiling and only **12 of 308** of its tile names appear in
  the board frame's 336 px stride vocabulary. The remedy was already in use on
  this family — the committed K = 10 rung is re-keyed to the carrier grid by
  `materialise_grid_unions.py` — so tier E's cells are now re-keyed the same
  way, and the invariant earned its place by catching it.

**One number in this card is now superseded.** § 2's inventory table quotes the
grid K-ladder as "consensus-only until the 2026-08-24 verifier stage; only
K = 10 verified". Tier E verified its K = 1, 3 and 5 rungs, so that family is a
four-rung verified ladder.

## 9. The admission job: what landed (2026-09-13)

The PI ruled on the close-out's morning list
(`reports/k-ladder-closeout-deltas-2026-09-12.md` § 10) on the morning of
2026-09-13. Four items; **all four landed**. Zero API calls; every scoring,
sweep, permutation and tiering step ran on sapphire in an isolated worktree.
Closing report: `reports/k-ladder-admission-deltas-2026-09-13.md`.

| # | Ruling | Outcome | Artefact |
|---:|---|---|---|
| 1 (question 1) | Board admission of the 46 Phase 2 rungs and tier E — **route (a)** | **landed** — a third membership source the builder defers to by condition id before its two refusal rules; board 103 → **153 cells admitted, 150 tiered, 3 withheld**; Tier 1 and its five members **unchanged** | `…/gs-era2-verified-board-2026-09-10/k-ladder/membership.json`, `scripts/build_gs_era2_board.py`, `scripts/author_k_ladder_board_membership.py` |
| 2 (question 2) | The five renamed ids in the signed `uplift-supplement-flatten` row — **confirmed** | **landed** — `_conditions_note` records the confirmation; 441 ids, all `…of5`, signature fields untouched; the FK guard and its tier-1 test pass | `results/run-analyses.json` |
| 3 (question 5) | Stride B K = 5 under the 3.7 verifier — **finish and register, do NOT re-tier** | **landed** — swept, scored and registered; § 3.3's K = 5 row filled (F1@50 **0.8758**, tile-MCC **0.7326**); the 55-map board untouched | `results/55map-final-board-r2-2026-09-06/cells/FOURTH-N5-oracle/`, `findings.md` § 3.3 |
| 4 (question 4 of the list's numbering, item 4 of the ruling) | The verifier-stage reversal of tile-MCC's response to K — **add as a claim** | **landed** — `findings.md` **§ 8.6**, four numbers re-read at source, mechanism in two sentences, added to the UNSIGNED analysis row's outcome | `results/k-ladder-2026-09-12/findings.md` § 8.6 |

**Two things the rulings did not anticipate, both found by measuring.**

- **The tile-join invariant refuses the F1 arm, not only the MCC arm.** § 8 of
  the close-out expected an uncaught `ConfusionGateError` on the MCC side. The
  three Gemini 3.7 gold-standard text rungs in fact abort in
  `compute_per_tile_tp_fp_fn`, with a plain `ValueError` stamped
  `tile_join_detection_shortfall`, because `assign_source_tiles` preserves a
  non-null `source_tile` column instead of re-joining it to the frame. Their
  whole per-tile table is therefore unavailable on this frame, so they are
  **admitted and withheld** — ranked nowhere, in no BH family, in no admissible
  set, with only their (sound) whole-frame F1 quoted. Measured across all 50
  admitted cells: exactly these three refuse. The four tier E cells carry **no**
  `source_tile` and so are joined geometrically from the frame; the 43
  `pv-diag-384` cells already speak the frame's vocabulary. This is close-out
  question 4 — the corpus-wide tile-join decision — now blocking three cells'
  whole statistics rather than only their MCC.
- **Regenerating the 55-map r2 sweep dropped two committed board cells from the
  manifest.** `final_board_sweeps.py` writes `cells_manifest.json` from stage 1
  alone, and the emergent post-hoc `A-N3-carried` / `B-N3-carried` cells come
  from a later step (`final_board_n3_carried.py`, PI direction 2026-08-28), so
  any regeneration silently shrank the board by two cells. The generator now
  carries post-hoc cells forward. Nothing published was affected — the defect
  was caught in the diff before anything was committed.

**What the admission job did NOT do**, because no ruling covered it: it did not
re-tier the 55-map final board (question 5's ruling), did not re-score any
admitted cell, did not touch a signature field anywhere, did not adopt a
geometric tile join, and did not add the MCC permutation family to the Era-2
board — the board's committed instrument does not include `--permute-mcc`, and
adding a statistic family to a signed board is a change the PI did not rule.

## Changelog

### 2026-09-13 (latest) — the review's MCC reading corroborated at board scale; the three withheld rungs disclosed

**Trigger**: checklist item 6
(`planning/documentation-foundation-checklist-2026-09-13.md`) rebuilt the GS
Era-2 verified board, which holds this review's 46 Phase 2 rungs and 4 tier E
rungs. Nothing in this card's own numbers changed; what changed is that two of
its findings now have a board-scale counterpart, and one of its cells has a
corrected figure.

| Claim | this card's reading | the board's, on 150 cells |
|---|---|---|
| tile-MCC's resolution | the MCC-admissible set is the whole ladder on 12 of 22 ladders; tile-MCC separates on none of tier E's six pairs | tile-MCC separates **2,982 of 11,175** pairs against F1's 7,961, and cliques into **6** tiers against F1's 14 |
| the two objectives select different rungs | K = 1 ruled out on F1 on 20 of 22 ladders, admissible on tile-MCC on **22 of 22**, highest tile-MCC on 13 | **no F1 Tier-1 cell is in MCC Tier 1**; MCC Tier 1 is 33 cells drawn entirely from F1 tiers 6–12, led by single-pass image cells; the two Hsu sets share **9** members of 65 and 59 |
| the three withheld 3.7 GS text rungs | tile-MCC withheld with a named reason; raw 0.1337 / 0.1422 / 0.1337 quoted as not-published | withheld from **both** families, with the shortfall counts (22 of 526, 21 of 475, 20 of 467 booked) and **both tile vocabularies** published, and each interval stated **withdrawn** rather than superseded |
| `g37-text-k3-verified-opmax` F1@20 | 0.8870 | **0.8860** / 495 detections (the recovery-fragment fix; its raw tile-MCC is no longer quoted, because its re-scored artefact withholds the tile block at source) |

**What this does NOT change in this card**: no ladder's ΔF1 or ΔMCC, no
BH verdict, no per-family MCB set, no admissible rung, no cost figure, and no
signature — the review's analysis row was signed 2026-09-13T06:58:12Z and was
not touched. The board's own F1 arm reproduced byte-identically, so the
review's ladder rungs keep the board-frame F1 they were admitted with.

### 2026-09-13 — the MCB job executed at US$0; the row is ready for signature

**Trigger**: the PI's two rulings of 2026-09-13 (afternoon) — (1) "wait for the
sets": supply the per-family Hsu multiple-comparisons-with-the-best admissible
sets before the review's analysis row is signed; (2) the carried convention: the
stride ladder's own vote shell is *the* carried point and `k = K` stays as a
disclosed column. Both landed. Zero API calls; all MCB compute ran on sapphire in
an isolated worktree. Closing report:
`reports/k-ladder-mcb-deltas-2026-09-13.md`.

**§ 6's step-5 scope note is corrected**, because both gaps it named are now
filled: the 55-map ladders' pairwise significance was re-run under the board
instrument on 2026-09-12, and the MCB set is supplied for all 22 tiered ladders
rather than the gold standard alone.

| claim | before | after |
|---|---:|---:|
| ladders with a Hsu MCB admissible set | 1 (the gold standard) | **22** (F1 and tile-MCC each) |
| MCB runs, and their gate | — | **44 runs, 170 candidate rows, all passed** |
| ladders whose F1 set contains K = 3 | — | **12 of 22** |
| ladders whose F1 set excludes K = 10 | — | **0 of the 20 that have one** |
| ladders whose tile-MCC set contains K = 1 | — | **22 of 22** |
| ladders with no admissible set | — | **1** (3.7 GS text screen, 3 rungs withheld) |
| the carried point, as reported | ambiguous (two readings) | **the stride shell**; `k = K` disclosed |
| the review's analysis row | UNSIGNED, waiting on the MCB | **UNSIGNED, ready for signature** |

**One disclosure the ruling surfaced.** Read back against the 55-map tables,
stride A's committed carried cells are the stride shell (k = 3 / 4 / 8) while
stride B's, stride B's 3.7-verifier cell and both 3.7 arms' are `k = K`. No
number was recomputed; `findings.md` § 3 now carries a disclosure table and says
those transfer taxes are an upper bound on the transfer cost.

**One methodological finding, flagged for the PI.** The admissible set and the
committed greedy-clique tie set disagree in both directions (E83, D20): of the
four MINIMAL ladders `findings.md` § 7.1 reports as a single tier where "K buys
nothing detectable at all", only **two** are admissible whole under MCB. § 7.1
stands as a within-ladder pairwise result and is not withdrawn, but "one tier"
must not be read as "every rung could be the best one".

**Landed in** `b7e2821ba`.

**What did NOT change**: every F1 and tile-MCC point estimate anywhere in the
review; every spend figure (this job spent **US$0**); §§ 1–5, 7, 8 and 9 of this
card; the rulings R1–R5; the Era-2 board (not re-tiered, not re-signed, not
re-scored) and the 55-map final board; and every signature field, the review
row's `manually_verified_at` included.

### 2026-09-13 — the admission job executed at US$0 (§ 9)

**Trigger**: the PI's rulings of 2026-09-13 (morning) on the close-out's morning
list (`reports/k-ladder-closeout-deltas-2026-09-12.md` § 10, questions 1, 2, 5
and 8 — questions 3, 4, 6 and 7 stay open).

**New § 9** records all four items. **§ 6's step-4 row** is annotated as
superseded, because the board it reports at 103 cells is now 153 admitted.

| claim | before | after |
|---|---:|---:|
| Era-2 board cells admitted | 103 | **153** |
| — of which tiered | 103 | **150** (3 withheld) |
| Tier 1 (greedy clique) | the five 3.7/3.8 cells | **the same five, same order, same F1** |
| findings.md § 3.3's rungs | K = 1, 3, 10 | **K = 1, 3, 5, 10** |
| findings.md § 8 sections | 8.1–8.5 | **8.1–8.6** |

**What did NOT change**: §§ 1–5, 7 and 8 in their entirety; every spend figure
(this job spent **US$0**); every ruling R1–R5; the 55-map final board's tiering
and its 595-pair BH family; and every signature field in the register and in the
board's provenance.

### 2026-09-12 — the closeout job executed; tier E at US$4.9595 (§ 8)

Eight items: five landed, one partial, two stopped. Tier E was the only API
spend, approved at US$5.02 and executed for US$4.9595 with 0 failures. The
tension the card's § 7 left open is answered by measurement rather than argued.
Three of the brief's expectations did not survive execution and are recorded in
§ 8 rather than left standing. No signature field was altered anywhere; the
Era-2 board was not rebuilt and the 55-map board was not re-tiered.

### 2026-09-12 (later still) — Phase 2 executed at US$24.8065 (§ 7)

Tiers A–D approved and run; 28 rungs verified, 46 cells registered, 14 ladders
completed to four rungs, 13 of them tiered. No analysis row authored or
amended, no signature field touched, the board not rebuilt, and the 55-map
instrument ruling not pre-empted. § 7 records the per-step outcome and the three
questions handed back.

### 2026-09-12 (later) — Phase 1 executed at US$0 (Session 154)

Steps 0–4, 6 and 7 landed; step 5 partial, with its scope stated in § 6. No API
call was made. The card's two stale expectations (§ 6) are corrected against
measurement rather than left standing.

### 2026-09-12 — R1–R5 ruled; two principles recorded; B3 folded in (Session 153)

The PI ruled R1–R5 (§ 4) and stated the "keep history, present the best
available" and "ladder, then board" principles, both recorded at the head
of § 4. R4 was accepted with the clarification that reference, frame and
candidate vintage move separately. B3: the 27 blocked first-N ladder
rungs get their twins from this job (§ 5). The card is no longer a
scaffold; the job can be planned (Phase 1 at $0, Phase 2 costed).

### 2026-09-11 — Original publication (S153, DRAFT scaffold)

Scoped from the PI's Session-152 intent. Sources re-read this session:
the three ladder register rows in `results/run-analyses.json`, the grid
findings' K-ladder passage, the signed Era-2 board's `membership.txt`,
and the conditions register's `n_passes` field. No compute, no API, no
register change. Awaiting the § 4 rulings.
