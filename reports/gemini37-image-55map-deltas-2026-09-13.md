# Gemini 3.7 image, 55-map K = 3 — launch deltas and what the gates measured

> **Last revised**: 2026-09-14 (**§ 10.7 added — the campaign's rungs were not
> booked onto the scoring frame.** The proposer's 192 px-stride tiling shares
> only 660 tile names with the 336 px-stride scoring frame, so the published
> `id` join credited 192 of 6,250 detections and the per-tile invariant refused.
> Fixed by applying the established map-constrained standard-tile assignment
> every other 55-map cell goes through, confirmed idempotent on three
> comparators at 100.00 %; two new gates close the blind spot. Earlier:
> steward hand-over — § 10 added: Q1 discharged
> by dated addenda, Q7 settled with a provenance sidecar, and a NEW delta —
> the brief's "corrected-F1 engine" is not the r2 board's engine, so scoring
> follows the board's `evaluate_detections.py` recipe; the five-test family
> declared before any score exists. Earlier: relaunch — blockers B1–B4 all
> discharged, the Gold Standard calibration leg run and the carried operating
> points fixed, the 55-map proposer's pass 1 launched. The campaign is **IN
> FLIGHT and incomplete**, so P1–P5 remain UNTESTED). See
> [§ Changelog](#changelog) for revision history.

Report on the run specified by `planning/gemini37-image-55map-2026-09-13.md`.
The first attempt was correctly **BLOCKED** at the pre-launch audit at US$0
(`outputs/gemini37-image-55map-2026-09-13/pre_launch_audit.md`); this revision
records the relaunch. **All four blockers are discharged** (§ 7), the GS
calibration leg has run, the carried operating points are fixed in the card
§ 2, and **pass 1 of the 55-map proposer is in flight**. Every claim below
carries its anchor; the original figures were read on 2026-09-13 at worktree
commit `dd5baf771`, the relaunch figures at `5a91463dc` on branch
`gemini37-image-55map-2026-09-13`.

## 1. Audited spend per leg

| Leg | Card | Audited / corrected | Actual | Basis |
|---|---:|---:|---:|---|
| GS calibration leg | US$1.2 | US$0.75 (est. ≈ 450 cands) | **US$1.1221** | flex, 3.7 rate card; the union came in at **622**, not ≈ 450 |
| 5-tile mechanism smoke | — | — | **≈ US$0.025** | 101,278 tokens; the meta's US$0.0398 is on the wrong rate card |
| 55-map proposer, 3 × 24,561 | US$237 | US$237 | **pass 1 in flight** | confirmed — see § 2 |
| K = 3 union, two arms (≈ 8,500) | US$22.7 | **US$14.1** | not reached | card is on the list basis; verify runs flex |
| K = 1 union, two arms (≈ 5,500) | US$9.1 (card: 14.7) | **US$9.1** | not reached | same correction |
| **Total** | **US$276** | **≈ US$261** | **US$1.15 committed so far** | |

The card's envelope holds; the corrections are all in the favourable
direction. The verifier legs are on the list basis in the card because the
verify path stamps `cost_basis: list, discount 1.0`, which the card notes;
`run_pv.py verify` defaults `--service-tier flex`, so the true arm rates are
half the stamped ones. Corrected per-candidate, flex: arm 1 (Gemini 3)
≈ US$0.00071, arm 2 (3.7) ≈ US$0.00095 — arm 2's stamped figure additionally
carries the rate-card error of § 2.

**The one adverse correction** is the GS calibration leg, at US$1.1221
(arm 1 US$0.4417 + arm 2 US$0.6804) against the audit's US$0.75 estimate,
because the K = 3 first-N union holds **622** candidates where the card
extrapolated ≈ 450 from the K = 5 union's 674. The extrapolation assumed
candidates fall off with K faster than they do: at K = 5 the vote histogram is
{1: 115, 2: 50, 3: 34, 4: 30, 5: 445}, at K = 3 it is {1: 105, 2: 57, 3: 460},
so dropping two passes removes only 52 candidates — a K = 5 → K = 3 ratio of
**0.923**, where the card's ≈ 450 implies 0.67.

**What this does and does not do to the 55-map verifier legs.** Transferring the
measured K = 3 density straight across — 622 / 1,398 = 0.4449 candidates per
tile — would put the 55-map K = 3 union at ≈ 10,900 rather than the card's
≈ 8,500. But that transfer assumes the two corpora propose at the same rate per
tile, and pass 1 is already measuring that they do not. Over its first 1,572
tiles the 55-map pass returns **0.9726 raw detections per tile** against the GS
pass 1's **1.1824** (main plus recovery, 1,653 over 1,398) — a density ratio of
**0.823**. Folding that in gives **≈ 9,000** at K = 3, which is close to the
card's ≈ 8,500 and comfortably inside its cost line.

So the card's number survives, but for a different reason than it gave: it
under-estimated the K = 5 → K = 3 ratio (0.67 assumed, 0.923 measured) and
over-estimated the 55-map detection density (GS-equal assumed, 0.823 measured),
and the two errors largely cancel. The corrected components are what should be
carried forward, not the coincidence. Two caveats on the 0.823: it rests on
6 % of the pass, and the manifest is walked in map order, so early maps need
not represent the corpus. The committed 3.7 **text** 55-map union ran to 12,715
candidates on this same geometry, which is the reminder that modality moves
this number too. Price the verifier stage from the union that actually gets
built.

## 2. The cost basis — reproduced exactly, and a stop rule that would misfire

The card's central basis is **correct**. Applying the audited rule
(`reports/token-load-audit-2026-06-12.md` § 2) with the **Gemini 3.7** rate card
to all ten committed GS fragments returns **US$22.5004 over 6,990 tile-passes =
US$0.00322 per tile-pass**, reproducing
`reports/gemini37-image-55map-costing-2026-09-10.md` § "Arithmetic" to four
decimal places.

Getting there required correcting the rate card. `run.meta.json` stamps
`pricing_used: {input_per_1m: 0.5, output_per_1m: 3.0}` for
`model: gemini-3.7-flash`, which are the **Gemini 3** rates; 3.7 lists at
**0.75 / 3.75**, per the conclusion of
`reports/billing-reconciliation-2026-09-11.md` § 3.2, which identifies that
same substitution as a candidate origin of the discredited "billed at roughly
0.6 × the token basis" expectation. Context caching is **not** tier-discounted
("$0.05 / 1M … at all tiers", token-load audit § 2), so for 3.7 it is
0.075 / 1M at flex as at standard — discounting it returns US$18.33 where the
committed figure is US$22.50, a 19 % understatement on a cache-heavy leg. Both
corrections are encoded, with the exact-reproduction test as the guard, in
`scripts/audit_proposer_cost.py` (landed this session; `ruff check` clean).

**The delta that matters operationally**: three figures exist for the same
metas, and the one the run itself prints sits on the wrong side of the card's
hard stop.

| Basis | USD / tile-pass | Pass 1 (24,561) | vs the US$110 stop |
|---|---:|---:|---|
| Audited (card's basis, reproduced) | 0.00322 | **US$79** | inside, 28 % headroom |
| Invoice-derived (`billing-reconciliation` § 3.2) | 0.00245 | US$60 | inside |
| **`run.meta.json` `cost_estimate`** | 0.00512 | **US$126** | **trips the stop** |

An operator or an unattended driver checking the pass-1 gate against the meta
would abort a pass that is US$31 inside budget on the card's own basis. The
meta is wrong in three compounding ways: Gemini-3 rates for a 3.7 model
(1.5 × understatement), cached input priced at the full input rate (the
dominant error at 79 % cached, overstating), and thinking tokens omitted
although Gemini bills them at the output rate (understating).

A caveat in the other direction: aborted and failed calls do not appear in
`usage_stats` — `run_2` recorded 20,932 retries at a recorded cost of US$0.032
for 4 tiles — so on a storm-hit pass the audited figure is a **floor**. The
billing reconciliation records the same mechanism and puts the leg's billed
cost within 2 % of the audited basis in USD.

## 3. Cache share per pass

Pass 1 is in flight, so its share is not yet measurable (§ 3.1). These are the
GS anchors that the gate must be read against.

| Fragment | Tiles | Cached / input |
|---|---:|---:|
| 5-tile parallel probe | 5 | **0.163** |
| 15-tile sequential probe | 15 | **0.542** |
| `run_1` | 1,292 | 0.788 |
| `run_1_recovery` | 106 | 0.751 |
| `run_2_recovery` | 1,394 | 0.794 |
| `run_3_recovery` | 1,397 | **0.806** |
| `run_4` | 132 | 0.782 |
| `run_4_recovery` | 1,266 | 0.800 |
| `run_5` | 1,273 | 0.795 |
| `run_5_recovery` | 125 | 0.767 |

The two storm fragments that processed 4 and 1 tiles recorded 0.000.

**Delta to the brief**: the instruction to gate the *smoke* at ≥ 70 % cached
cannot be met. Implicit prefix caching warms with volume, and a 5-tile probe
reads 16.3 % — the GS run measured exactly this and recorded it as verdict I5,
"79.5 % at scale (probe 16 % parallel-cold / 54 % sequential)"
(`results/gemini37-image-gs-2026-09-01/findings.md`). Applying the gate to the
smoke would stop the campaign on an expected, harmless reading. The gate is
sound at pass scale, where the GS floor across eight substantive fragments is
**0.751**; the smoke's gate should be mechanism-only.

The relaunch's own 5-tile smoke read **0.488** cached — three times the GS
probe's 0.163 at the same tile count, because the GS calibration leg had
already warmed the prefix. This confirms the mechanism engages and confirms
that a smoke reading is a function of what ran before it, not of the
configuration: exactly why B4's rescoping to a pass-scale gate is right.

### 3.1 Both pass-1 gates are POST-pass, not in-flight

A delta the audit did not catch. `4_detect_mounds_batch.py` saves the
detections GeoJSON incrementally after every tile (`_save_geojson`, called at
line 1255), but writes `*.meta.json` — the only place `usage_stats` and
therefore `total_cached_tokens` and the token counts live — **once, at the end**
(line 1355). So while a pass runs, neither the audited cost nor the cache share
can be computed; only the completed-tile count is observable.

Consequence for the card's § 3 wording: "**abort** the proposer if pass 1
exceeds US$110 on the audited basis" cannot execute as an in-flight abort. It
operates as a **go/no-go gate on passes 2–3**, applied the moment pass 1's meta
lands. The exposure this leaves unguarded is bounded and small: on the audited
GS basis pass 1 costs US$79, and for it to reach US$110 the per-tile cost would
have to run 39 % above the GS basis — which is the same thing as the cache
share collapsing, so the two gates fail together and are read together, once,
at pass end. An operator wanting a genuine in-flight tripwire would have to
patch periodic meta flushing into the runner; that is not on this card.

## 4. Union sizes

| Union | Card | Built |
|---|---:|---:|
| GS K = 5 first-N (the B2 verification) | 674 committed | **674 — byte-identical** |
| GS K = 3 first-N (the calibration leg) | ≈ 450 | **622** (votes {1: 105, 2: 57, 3: 460}) |
| 55-map K = 1 | ≈ 5,500 | not reached (≈ 6,900 on the measured ratios, § 1) |
| 55-map K = 3 | ≈ 8,500 | not reached (≈ 9,000 on the measured ratios, § 1) |

The GS K = 5 rebuild is the load-bearing one: run through the same chain that
produced the committed artefact, with the fixed code, it reproduces
`union_k5.geojson` **byte for byte**, with all five passes gated at 1,398/1,398
tiles after the recovery fold. That is what licenses trusting the K = 3 union
built beside it, and it is the verification the brief asked for before the
calibration leg was allowed to fix the carried points.

## 5. P1–P5 verdicts

**All five are UNTESTED.** Pass 1 of three is in flight; no union, no 55-map
verifier arm, no score, no permutation test. The predictions stand as written
in the card. Three observations bear on how they should be read:

- **P1's mechanism is weaker than card § 1 implies.** The nine top-MCC GS
  cells are indeed all image, but they carry F1 0.7112–0.7767 in tiers 6–8:
  `verified-adv-image-baseline-pro-vf` is MCC 0.8887 at F1 0.7309
  (`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md`).
  They are tight, high-specificity single-pass cells and their MCC rank is
  largely a precision artefact. The card's own chosen cell (MCC 0.8264) is
  outside that top nine. The image-MCC advantage is real on the GS but its
  carrier is not the configuration the card is buying.
- **P1's two comparators have never been co-tiered.** IM-k3 (0.7110) is one of
  the eight cells on `results/metric-leaderboards/55map-mcc-tiering-r2.md`;
  FOURTH-N1-oracle (0.7471) is on the 35-cell
  `results/55map-final-board-r2-2026-09-06/final_board_50m.json` and is absent
  from the MCC tiering. Card § 1 calls the first "sole MCC Tier 1" and the
  second "the 55-map MCC leader today" in adjacent rows; they are two
  populations. The five-test family in step 7 covers both, and the findings
  document should say so explicitly.
- **Both carried points select unanimity, which loads the dice against P2 and
  P5.** The GS calibration leg put arm 1 at (prob_t 0.10, k 3) and arm 2 at
  (0.88, k 3) — both at k = K, so the carried 55-map K = 3 cell is a
  3-of-3 consensus. P2 predicts the K = 1 rung's MCC is at least the K = 3
  rung's; but the K = 1 rung cannot carry k = 3, so its k collapses to 1 and the
  comparison is no longer a clean one-factor contrast in pass count — it varies
  the vote threshold too. P5's carried-versus-oracle tax is also likelier to
  bind at a corner of the sweep grid than in its interior. Neither invalidates
  the prediction; both should be stated when the rungs are read, so the
  interpretation is not chosen after the numbers exist.

## 6. What did NOT change

- **No 55-map union, no 55-map verifier run, no score, no permutation test,
  no P1–P5 verdict.** Pass 1 of three is in flight; everything downstream of
  the proposer is untouched.
- **The 55-map board and the MCC tiering are untouched**; no re-tiering, no
  MCC re-tiering, no signed row touched, no analysis row authored. The single
  UNSIGNED analysis row `gemini37-image-55map-2026-09-13` the card calls for
  cannot be written until the rungs are scored.
- **`prompts/`, `inputs/` and every configuration are untouched.** The
  configuration is byte-identical to the GS image run, re-confirmed live this
  session: the smoke's `system_instruction_hash` is
  `e169b7237b853eeaad990fc2e54fbd7214afb435d85c8e444a4a784432200e12`, the same
  payload fingerprint the audit's dry run reproduced, with
  `include_example_images: true`, thinking `low`, T = 0.7 and tile size 384.
- **`scripts/merge_passes.py` was not touched by this session.** The fix is the
  PI's, landed as `75d7c8d4c` on `main` after the ruling recorded in
  `reports/recovery-fragment-drop-2026-09-13.md`; this session only verified it
  (§ 7, B2) and ran its tier-1 tests.
- **No committed union was rebuilt or overwritten.** The GS `union_k5.geojson`
  rebuild is byte-identical, so the committed artefact is unchanged in content
  as well as in fact.
- **Nothing on sapphire's main checkout was written, moved or removed.** All
  work ran in the isolated worktree `~/worktrees/map-reader-llm/claude-image55`,
  reading the main checkout's tiles, rasters and GS pass directories through
  symlinks and one 95 MB copy.

## 7. Blocker status — all four discharged

Two governance-and-tooling blockers and two gate definitions that would
misfire. All four are now closed; the detail of the original findings stands in
the audit, and what follows records both the finding and its discharge.

**B1 — approval provenance.** The card's banner still reads "awaiting the PI's
API-gate approval". The only committed record of a PI decision on a 55-map 3.7
image run is a **decline**: "55-map 3.7 image run COSTED AND DECLINED (PI: too
dear, trigger not met)" (`planning/paper-writeup-continuity.md`, S152 item 4).
The GS screen's own escalation section goes further and dismisses the MCC route
in the same breath: "There is no resolvable new F1 high, so the pre-agreed
trigger … is NOT met. (Arm 2's image MCC 0.8322 likewise does not approach the
committed GS MCC crown.)"
(`results/gemini37-image-gs-2026-09-01/findings.md`). The card's tile-MCC case
at K = 3 for US$276 is a new and reasonable argument, and it may well have
carried — but a ~102,000-call campaign should not start while the repository's
record reads "declined" and the card reads "awaiting".

> **DISCHARGED.** The PI's approval of 2026-09-13, given in session on the
> condition that caching is in effect, is now minuted in the card's banner and
> its changelog, with the caching condition confirmed at source (the GS 3.7
> image run's full passes read 0.751–0.806 cached). The self-contradiction the
> audit flagged is *not* resolved: `planning/paper-writeup-continuity.md`
> S152 item 4 still reads "COSTED AND DECLINED" and the GS findings' escalation
> sentence still reads "trigger … is NOT met". Annotating those two is a PI
> call this session did not take, and it remains open as question 1 of § 8.

**B2 — the union builder drops recovery fragments, silently and plausibly.**
`resolve_pass_files` parses the pass number as
`int(pass_name.replace("run_", ""))`, so `run_1_recovery` raises `ValueError`
and is skipped (`scripts/merge_passes.py`, lines 408–471). On the GS image
passes that is where the data is: `run_2`'s main directory holds **4 tiles / 7
features** and `run_3`'s holds **1 tile / 0 features**, against 1,394 and 1,397
tiles in their recovery fragments. Run live, `merge_passes.py --passes 1,2,3,4,5
--threshold 1` returns **650 features against the committed 674** — only 3.6 %
low, so no count check would catch it. The deeper error is the vote
denominator: `total_passes` counts pass *directories*, so it reads 5 while two
passes contributed nothing, corrupting every `vote_count` and every `vote_t`
operating point. The 55-map passes will need recovery fragments, because the
flex-storm window guarantees residue.

Related: the single-merge path (`--output`) computes `pass_provenance` and then
discards it — `main()` ignores the return value. Only `--sweep --output-dir`
writes it, into `voting_summary.json`. Unions must be built via the sweep path.

> **DISCHARGED, and with a correction to how the blocker was framed.** The fix
> landed on `main` as `75d7c8d4c`: `_PASS_DIR_RE` now folds `run_<N><suffix>`
> into pass `<N>`, main files first so within-pass dedup precedence is
> unchanged, and `tests/test_merge_passes_recovery.py` passes 9 with 3
> characterisation tests skipping now the patch is present.
>
> **The correction.** The GS calibration leg was never actually gated by this
> defect. `merge_passes.resolve_pass_files` is not on the path that built the
> committed GS union: `image_b_prepare_and_union.py` resolves its passes through
> `stride_prepare_and_union.resolve_pass_paths`, which globs `{run}_recovery`
> and has always been fragment-inclusive — exactly as
> `reports/recovery-fragment-drop-2026-09-13.md` § 2.2 concluded when it found
> the drop's reach into committed unions to be 0 MATERIAL / 5 NEGLIGIBLE / 23
> UNAFFECTED. Rebuilding the K = 5 union through that chain reproduces the
> committed 674 **byte-identically** (the verification the brief required), and
> the K = 3 union built the same way is therefore sound. The audit's live
> demonstration of 650-against-674 was a demonstration of what
> `merge_passes.py` *would* have produced had it been used, not of a defect in
> the artefact the calibration leg depends on. `merge_passes.py` still matters
> downstream: it is where the 55-map `pass_provenance` has to come from.
>
> **An open design question it leaves.** The 55-map unions face a conflict the
> card does not resolve. Comparability with the 3.7 **text** arms — which the
> card's deployment-scale modality difference-in-differences depends on —
> requires `stride55_prepare_and_union.py`, the builder those arms used (no
> carrier clip, full-extent scoring). But that builder writes no
> `pass_provenance`; only `merge_passes.py --sweep --output-dir` does. Building
> the image unions with `merge_passes.py` to get the provenance block would make
> the modality contrast a comparison across two builders. The recommendation is
> to build with `stride55_prepare_and_union.py` and emit the provenance record
> as a sidecar from `merge_passes.build_pass_provenance` over the same resolved
> fragment set — same union geometry, provenance requirement met. It needs the
> PI's assent because it is a deviation from the card's literal wording, and it
> is question 7 of § 8.

**B3 — the stop-rule basis.** **DISCHARGED.** `scripts/audit_proposer_cost.py`
runs clean over the ten committed GS fragments and returns **US$22.5004 over
6,990 tile-passes = US$0.00322 per tile-pass**, against the metas' own
US$35.8176 — reproducing the committed basis to four decimal places and
confirming the tool is the gate. § 3.1 above records the one thing this does
not buy: the figure is only computable once a pass finishes.

**B4 — the smoke cache gate.** **DISCHARGED.** The card's § 5 step 1 now scopes
the ≥ 70 % gate to pass 1 and makes the smoke mechanism-only. The smoke duly
read 0.488 — a figure that would have failed the original gate and told nobody
anything useful.

## 8. Open questions after the relaunch

Questions 2, 3 and 4 of the original list are answered and closed (§ 7, B2–B4).
What remains, plus what the relaunch added:

- **Q1 — does the PI want the contradictory record annotated?** The approval is
  minuted in the card, but `planning/paper-writeup-continuity.md` S152 item 4
  still reads "COSTED AND DECLINED" and
  `results/gemini37-image-gs-2026-09-01/findings.md` still reads "the
  pre-agreed trigger … is NOT met". A reader arriving at either first will
  conclude this campaign should not have run. One annotated sentence in each
  would close it.
- **Q5 — who finishes it?** Still the binding question, and still unanswered. The
  storm-resilient driver exists now
  (`scripts/gemini37-image-55map-driver.sh`, W3 closed) and **pass 1 is in
  flight**, its first 699 tiles clearing at ≈ 5,200 tiles/h — above the
  3,884–4,608 the audit measured, which would land pass 1 in ≈ 4.7 h rather
  than 5.3–6.3, on the strength of an eight-minute sample. But the flex queue is
  measurably more congested than it was during the GS run — the GS calibration
  leg's arm 2 logged **824 server-error retries in 893 s for 622 candidates**
  against the GS run's 420 for 674 — and the storm window opens ≈ 13:00 UTC.
  Passes 2–3, four verifier arms, scoring and the permutation family remain
  **24–48 h of work that this session cannot finish**, and the driver applies
  no gate of its own: it records and continues. This needs a named owner.
- **Q6 — should P1's interpretation be pre-committed given § 5?** Unchanged, and
  now with a third strand: both carried points select unanimity, so the K = 1
  rung varies the vote threshold as well as the pass count.
- **Q7 (new) — which builder produces the 55-map unions?** New. Comparability with the
  text arms points at `stride55_prepare_and_union.py`; the card's
  `pass_provenance` requirement points at `merge_passes.py --sweep`. The
  recommendation is the first plus a provenance sidecar from the second
  (§ 7, B2). This needs settling **before** the unions are built, because
  rebuilding them later re-fixes the operating points.
- **Q8 (new) — should the verifier legs be re-priced from the union actually
  built?** The card's ≈ 8,500 survives, but on two cancelling errors: the
  K = 5 → K = 3 candidate ratio is 0.923 where the card assumed ≈ 0.67, and the
  55-map detection density is 0.823 of the GS's where the card assumed parity
  (§ 1). Reading the built union's count before the arms run costs nothing and
  removes both guesses.

## 9. What passed, so it is not re-litigated

The configuration is sound. Proposer config, image instruction file, verifier
config and verifier instruction are **byte-identical blobs** between the GS
run's commit `7187e81354582ba2ddd09a5a5207977a0c0c605a` and `dd5baf771`, and
`inputs/examples` is unchanged; the dry run reproduces the GS payload
fingerprint `e169b7237b853eeaad990fc2e54fbd7214afb435d85c8e444a4a784432200e12`.
All ten transmission checks pass, including `include_example_images: true`, the
four command-line overrides reaching the payload, and no `--use-cache` so
implicit caching works as it did on the GS run. The manifest resolves
**24,561 of 24,561** tiles at measured tile size 384 with 17 examples loaded.
Both verifier arms match the card exactly. The GS passes are complete at
1,398/1,398 each. The scoring recipe is confirmed at 5,018 reference mounds
over 8,541 evaluation tiles, corroborated by IM-k3's confusion matrix summing
to 8,541. All eight of the card's § 1 anchors re-read correctly.

Note for provenance work: `library_hash` changed from a filename hash to a
content hash on 2026-09-12, so a new run will not reproduce the GS value
`8580ecb2258b64a0fdbcee707714bc9dd8f8e698a29d304e3980dac18a831cb4` despite
identical images. Argue identity from `system_instruction_hash` and the blob
comparison, and read `configuration.library_hash_basis` first.

## 10. Deltas the steward session found, before any further spend

Three, recorded as they were settled rather than at the end, because the
campaign spans more wall clock than one session.

### 10.1 Q1 discharged — the contradictory record is annotated

`planning/paper-writeup-continuity.md` S152 item 4 and
`results/gemini37-image-gs-2026-09-01/findings.md`'s escalation section each
carry a **dated addendum** (2026-09-13) saying that the decline they record was
on **F1** grounds and still stands, and that the PI's approval of this campaign
is on **tile-MCC** grounds — a different question, with the deployment-scale
case set out in the card § 1. Neither original sentence was rewritten. The GS
findings document took a revision-policy banner and changelog entry recording
that no numerical claim moved.

### 10.2 Q7 settled — stride builder plus a provenance sidecar

The parent session ruled the recommendation of § 7 (B2): build both 55-map
unions with `scripts/stride55_prepare_and_union.py`, for text-arm
comparability, and emit the `pass_provenance` block as a **sidecar**. The
sidecar tool is `scripts/emit_union_pass_provenance.py`, which imports
`stride55_prepare_and_union.resolve_pass_paths` (rather than re-implementing
pass resolution) and hands the resolved set to
`merge_passes.build_pass_provenance`, so the union and its provenance record
cannot describe different files. It writes
`union_k<K>_pass_provenance.json` beside each union, carrying the
`consensus-pass-provenance/1` keys the existing guard
`build_all_consensus.compare_pass_provenance` reads, plus the union described,
its feature count and the builder. Seven tier-1 tests; `ruff` clean.

### 10.3 NEW — the brief's scoring engine is not the r2 board's engine

The steward brief specified scoring "on r2 at 50 m with the corrected-F1
engine (`scripts/compute_corrected_f1_multi_buffer.py --compute-mcc`), the
recipe under `results/55map-final-board-r2-2026-09-06/`". Those two clauses
name different instruments, and the second is the one that matters.

Read at source, the r2 board's recipe is **`scripts/evaluate_detections.py`**,
driven per cell by `scripts/r2_score_cells.py --stage board`:

> Stage 2: `evaluate_detections.py`, 14 buffers, tile-level BCa bootstrap
> 10,000 / seed 42, `--mcc`, `--require-clean-inputs`, per cell
> (`r2_score_cells.py --stage board`).
> — `results/55map-final-board-r2-2026-09-06/final-board-50m.md` § "Provenance and gates"

with `--ground-truth inputs/vectors/references/best-available-gt-55maps-r2.geojson`
and `--bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`;
every cell's `score.log` records `Reference: 5018 mounds, 8541 evaluation
tiles`, and `cells/FOURTH-N1-oracle/evaluation.json` stamps
`"script_path": "scripts/evaluate_detections.py"`.

`compute_corrected_f1_multi_buffer.py` is the **canonical adjudicated
extended-GT (Track 2)** engine — a different reference and a different
matching chain. `planning/reference-revision-2026-09-06.md` § 2 places it
explicitly on the other side of the r2 revision ("The existing 'corrected F1'
… corrects against a REVIEWED extended GT"), and its § 4f records the one
companion cell scored on that chain as "the only one not on r2".
`scripts/gemini37_sweep_oracle.py`'s own header states the hazard in terms for
this campaign's predecessor: "Cross-reference comparisons … mix instruments
and are not valid deltas".

**Consequence, and the call taken.** P1–P5 are all differences against cells
on the r2 board (`FOURTH-N1-oracle` 0.7471, `ARM2-N3-oracle`, `ARM2-N5-oracle`,
`IM-k3`). Scoring this campaign's rungs with the Track-2 engine would compare
them across instruments, which is exactly the error the predecessor script
warns against, and the paired tile-swap would be incoherent — its per-tile
vectors would come from two different references. The campaign therefore scores
on **the board's recipe**: `evaluate_detections.py`, 14 buffers, bootstrap
10,000, seed 42, `--mcc`, `--require-clean-inputs`, against r2 and the
8,541-tile bounds. The brief's clause naming the corrected-F1 engine is read as
a slip for "the r2 board's engine", and this subsection is the minute of that
reading. Anyone who wants the Track-2 figures as well can have them as a
secondary column; they are not the instrument P1–P5 are stated in.

A consequence for sequencing, from the same reading: `--require-clean-inputs`
aborts with exit 4 on any `modified` or `untracked` input
(`evaluate_detections.py`, `enforce_input_hygiene`), so every materialised
detections file must be **committed before it is scored**.

### 10.4 The five-test family, declared before the numbers exist

The card § 5 step 4 names four comparators and calls the family a "five-test
family". The fifth is not written down. The predecessor text campaign's family
was "the four 2×2 edges plus the all-3.7 vs incumbent diagonal"
(`scripts/gemini37_sweep_oracle.py` header), i.e. external edges plus one
within-campaign contrast. This campaign therefore declares its family, **before
any 55-map score exists**, as the four named comparators plus the
within-campaign **K = 1 versus K = 3** contrast, which P2 requires a test for
in any case. Benjamini–Hochberg at q = 0.05 runs across those five, separately
on MCC and on F1.

### 10.5 What P1 actually requires, read off the comparators' confusion matrices

Stated before any 55-map score exists, because it is the kind of reading that
is worthless once the numbers are in.

The deltas report already noted (§ 5) that on the Gold Standard the top-MCC
image cells are "tight, high-specificity single-pass cells and their MCC rank
is largely a precision artefact". The same mechanism is visible at deployment,
in the four comparators' own committed tile confusion matrices — read from each
cell's `evaluation.json` `summary.tile_classification.confusion` on 2026-09-13,
over the same 8,541 tiles:

| Cell | tp | fp | fn | tn | sens | spec | MCC |
|---|---:|---:|---:|---:|---:|---:|---:|
| `FOURTH-N1-oracle` | 2,473 | **45** | 1,056 | 4,967 | 0.7008 | **0.9910** | **0.7471** |
| `ARM2-N3-oracle` | 2,534 | 198 | 995 | 4,814 | 0.7181 | 0.9605 | 0.7163 |
| `ARM2-N5-oracle` | 2,502 | 178 | 1,027 | 4,834 | 0.7090 | 0.9645 | 0.7147 |
| `IM-k3` | 2,486 | 178 | 1,043 | 4,834 | 0.7044 | 0.9645 | 0.7110 |

Sensitivity and specificity are recomputed here from the committed counts (each
row sums to 8,541); the engine's own rounded points agree — `IM-k3` reads
0.704 / 0.965 on `results/metric-leaderboards/55map-mcc-tiering-r2.md`.

The leader does **not** find more mound-bearing tiles than the field: its
sensitivity, 0.7008, is the *lowest* of the four. Its whole advantage is
false-positive tile suppression — 45 FP tiles against 178 for the two text
cells and for the incumbent image campaign. So the target P1 has to clear is a
specificity target, not a recall target, and there are only two routes to it:
lift sensitivity well above 0.7181 — the field's best — while holding FP tiles
near 180, or push FP tiles down towards 45. The second is what a tighter, higher-threshold image
cell does, and it is the route the carried points — both at unanimity — are
pointed at.

This also sharpens the informative-failure reading the card already allows. If
the K = 3 image cell lands at ≤ +0.01, the result is not "image does not
transfer": it is that the 55-map MCC ceiling is being set by FP-tile
suppression, which a K = 3 consensus at unanimity buys only so much of. Either
way the campaign settles the modality question at deployment scale, which is
what card § 6 says it is for.

### 10.6 The difference-in-differences, pre-specified from the text arms

Card § 2 says the two verifier arms "mirror the 3.7 text 2×2
(`gemini37-55map-grid-2026-08-31`) so the modality difference-in-differences
exists at deployment". The text side of that 2×2 is already committed on the r2
board, and writing it down now fixes what the contrast will be computed against
— read from `results/55map-final-board-r2-2026-09-06/final_board_50m.json` on
2026-09-13:

| Rung | Text arm 1 (Gemini 3 verifier) | Text arm 2 (3.7 verifier) | verifier effect, arm 2 − arm 1 |
|---|---|---|---|
| K = 1 | `ARM1-N1-oracle` F1 0.8413 / MCC 0.7246 | `ARM2-N1-oracle` F1 0.8610 / MCC 0.7422 | F1 **+0.0197**, MCC **+0.0176** |
| K = 3 | `ARM1-N3-oracle` F1 0.8705 / MCC 0.7179 | `ARM2-N3-oracle` F1 0.8848 / MCC 0.7163 | F1 **+0.0143**, MCC **−0.0016** |
| K = 5 | `ARM1-N5-oracle` F1 0.8727 / MCC 0.7147 | `ARM2-N5-oracle` F1 0.8871 / MCC 0.7147 | F1 **+0.0144**, MCC **0.0000** |

The difference-in-differences is therefore, per rung and per metric,
(image arm 2 − image arm 1) − (text arm 2 − text arm 1), computed at matched K
on the same 8,541-tile frame. At K = 3 the text baseline for the verifier seat
is **−0.0016 MCC**, which is what P4's "arm 2 beats arm 1 on MCC by ≥ +0.01"
has to be read against: on text, at this rung, the 3.7 verifier seat buys F1
and nothing at all on MCC.

**Two priors this table supplies, both stated before the image numbers exist.**

- **P2 already holds on every committed deployment ladder.** Tile-MCC falls
  monotonically with K while F1 rises, on all three: text arm 1 (0.7246 →
  0.7179 → 0.7147), text arm 2 (0.7422 → 0.7163 → 0.7147), and the fourth cell
  (`FOURTH-N1` 0.7471 → `FOURTH-N3` 0.7376 → `FOURTH-N10` 0.7359, F1 0.8352 →
  0.8747 → 0.8813). P2 is thus a low-risk prediction, and its interest is in
  the size of the K = 1 → K = 3 MCC drop for an image pool, not its sign.
- **P1's comparator is the K = 1 corner of a ladder whose K = 3 rung it beats
  by 0.0095.** `FOURTH-N1-oracle` 0.7471 leads `FOURTH-N3-oracle` 0.7376. A
  K = 3 image cell is being asked to beat a K = 1 cell by ≥ 0.02 on a metric
  that every ladder says K = 3 pays a penalty on — which is the tension § 10.5
  describes from the confusion-matrix side, seen from the K axis.

### 10.7 NEW — the campaign's rungs were not booked onto the scoring frame

Found by the second steward on 2026-09-14, when the sweep died on its first
run. It is the most consequential delta of the campaign, and the four gates of
§ 6 could not have caught it.

**The symptom.** `--stage sweep` crashed with a `TypeError` inside
`multiprocessing`'s result handler — `TileJoinRefusalError.__init__() missing 4
required keyword-only arguments`. That is a masking error: the exception cannot
round-trip through the pickler, so the real failure never reached the log.
Reproduced in-process, it reads:

> per-tile TP/FP/FN table refused: **192 of 6,250** in-frame detections were
> credited to a tile under the `id` tile join, a shortfall of **6,058**.

**The cause.** Two different tilings, and nothing in the harness bridged them:

| | Tiling | Tiles |
|---|---|---:|
| Proposer (`g384_ov192_55map`) | 384 px on a **192 px** stride | 24,561 |
| Scoring frame (`55maps_evaluation_bounds.geojson`) | 384 px on a **336 px** stride | 8,541 |

Only **660** tile names are common to the two, and only **142** of a rung's
4,857 distinct `source_tile` values are in the frame. The published tile-MCC
convention is the name-based `id` join (PI ruling, § 0 of
`reports/tile-mcc-geometric-join-2026-09-12.md`), and that report states the
precondition plainly: `id` is "well defined only when the cell's proposer
tiling **is** the scoring frame." It is not, here, so the invariant was right
to refuse.

**This is not the geometric-join question.** That question — whether to adopt
`geometric-primary` or `geometric-contains` — remains open with the PI, moves
146 committed cells by roughly a tenth of an MCC, and was not touched. What was
missing is a step *every other 55-map cell already goes through*:
`stride55_score.assign_standard_tile` over
`stride55_score.build_map_constrained_index`, which re-stamps `source_tile` to
the nearest standard-grid tile centroid **within the origin raster's own map**.
The map constraint is load-bearing, and `stride55_score.py` lines 119–127 say
why: the sheet rasters overlap, so an unconstrained nearest-centroid assignment
flips about 10 % of candidates to the adjacent sheet and moves corrected F1 by
about 0.04.

**The rule was confirmed, not assumed.** Re-applying it to the committed
comparators must be a fixed point if it is the writer that produced them:

| Cell | Features | Idempotent |
|---|---:|---:|
| `FOURTH-N1-oracle` | 5,337 | **100.00 %** |
| `ARM2-N3-oracle` | 5,097 | **100.00 %** |
| `ARM2-N5-oracle` | 4,924 | **100.00 %** |
| `IM-k3` | 4,680 | 83.65 % |

So it is provably the writer for the three cells P1, P3 and P4 are chiefly
stated against. `IM-k3`'s partial is a property of that comparator, not of the
rule: the MCC tiering scored the original verified file **in place**, so it
never passed through this writer — a caveat now attached to the one test in the
five-test family that uses it.

**Why § 6's four gates were blind to it.** Gates 2, 3 and 4 all consume
*comparator* detection sets, and those already carry scoring-frame
`source_tile`. No gate ever ran a *campaign* rung through the per-tile path. The
gates were therefore both passing and uninformative about the campaign's own
cells — the exact failure mode a gate is supposed to prevent. Two gates were
added to close it:

- **Gate 5** asserts the assignment rule is idempotent on the three comparators
  that went through it, and reports `IM-k3`'s expected partial.
- **Gate 6** asserts every campaign rung books **100 %** of its candidates on
  the scoring frame. All four rungs now read 6,985 / 6,985 and 8,337 / 8,337.

**The near miss.** The tile-join report's § 1 site 2 records that under a
vocabulary mismatch the per-tile table loses *every* TP and FP, leaving pure
false negatives and a micro-F1 of 0.0000 — and that the per-tile bootstrap CIs
and the pairwise permutation tests would then resample exactly that. Had the
invariant not been added on 2026-09-12, this campaign would have produced a
full set of P1–P5 verdicts, a board row and a findings document off a table of
pure false negatives. The invariant is what turned a silent wrong answer into a
crash, and the crash is what produced this section.

## Changelog

### 2026-09-14 — § 10.7: the rungs were not booked onto the scoring frame

**Trigger**: `--stage sweep` crashed on its first run with a masked
`TileJoinRefusalError`. Diagnosis, fix and gates in § 10.7.

| Claim | Before | After |
|---|---:|---:|
| Campaign rung `source_tile` | proposer tiling (192 px stride) | **scoring frame** (336 px stride) |
| Detections booked under the `id` join | **192 of 6,250** | **100 %**, all four rungs |
| Mechanism gates | four, all PASS | **six**, all PASS |
| Assignment rule | absent from the harness | `stride55_score.assign_standard_tile`, idempotent on three comparators at 100.00 % |
| `IM-k3` join provenance | unstated | 83.65 % idempotent — scored in place, caveat attached |
| Geometric-join question | open with the PI | **still open, untouched** |

**What did NOT change**: no join variant, no default, no committed cell, and no
figure on any board or tiering. The carried operating points, the five-test
family, the scoring instrument and the US$420 hard stop all stand. The fix puts
the campaign's own detections into the vocabulary the published join already
requires.

### 2026-09-13 (steward hand-over) — § 10: two open questions closed, one new delta

**Trigger**: the campaign acquired a named owner for passes 2–3 onward
(question Q5), and that owner's first act had to be to settle the two
questions that block the unions and the scoring — Q7 (which builder) and the
instrument the rungs are scored on.

| Claim | Before | After |
|---|---|---|
| Q1, contradictory record | open | **closed** — dated addenda in both documents, originals unrewritten |
| Q7, union builder | recommendation, unassented | **settled** — `stride55_prepare_and_union.py` + `emit_union_pass_provenance.py` sidecar |
| Scoring engine | brief said `compute_corrected_f1_multi_buffer.py` | **`evaluate_detections.py`**, the r2 board's own recipe (§ 10.3) |
| Five-test family | four comparators named, fifth unwritten | **declared** — four external + the K = 1 vs K = 3 contrast (§ 10.4) |
| P1's required mechanism | "the image MCC advantage transfers" | **a specificity target** — the leader has the field's LOWEST sensitivity (§ 10.5) |
| Spend committed | US$1.15 | **US$1.15** — nothing new spent for this revision |

**What did NOT change**: pass 1 is still in flight and passes 2–3 are still
unlaunched, so the pass-1 gate verdict, both unions, all four verifier arms,
every score and every P1–P5 verdict remain as § 5 and § 6 record them —
UNTESTED and unbuilt. No board, no tiering, no signed row, no configuration
and no committed union was touched. The GS findings document was edited, but
only to append an addendum and its changelog; no figure in it moved.

### 2026-09-13 (relaunch) — blockers discharged, calibration leg run, pass 1 in flight

**Trigger**: the PI's API-gate approval minuted in the card banner, and the
`merge_passes.py` recovery-fragment fix landing on `main` as `75d7c8d4c`
(itself the ruling recorded in `reports/recovery-fragment-drop-2026-09-13.md`),
which together lifted B1 and B2. Work ran on branch
`gemini37-image-55map-2026-09-13` in the isolated sapphire worktree
`~/worktrees/map-reader-llm/claude-image55`.

All four blockers discharged (§ 7). B2's discharge came with a **correction to
how the blocker was framed**: the GS calibration leg never ran through
`merge_passes.resolve_pass_files` at all — `image_b_prepare_and_union.py`
resolves passes through the always-fragment-inclusive
`stride_prepare_and_union.resolve_pass_paths` — so the leg was blocked on a
defect that did not reach it. The verification the brief required nevertheless
passed decisively: the rebuilt K = 5 first-N union reproduces the committed
674-candidate `union_k5.geojson` **byte-identically**.

| Claim | Before | After |
|---|---:|---:|
| GS K = 3 first-N union | ≈ 450 (card estimate) | **622** |
| GS calibration leg, audited | US$0.75 (estimate) | **US$1.1221** |
| GS K = 5 rebuild vs committed 674 | 650 via the defective path | **674, byte-identical** |
| Carried point, arm 1 | not fixed | **(prob_t 0.10, k 3)**, GS F1@20 0.9197 |
| Carried point, arm 2 | not fixed | **(prob_t 0.88, k 3)**, GS F1@20 0.9245 |
| 5-tile smoke cache share | 0.163 (GS probe) | **0.488** (prefix pre-warmed) |
| 55-map K = 3 union, expected | ≈ 8,500 | ≈ 9,000 on the measured ratios |
| 55-map raw detections per tile | assumed GS-equal | **0.823 of the GS's** (pass 1, first 1,572 tiles) |
| Spend committed | US$0.00 | **US$1.15** |

Two deltas the first audit did not catch, both recorded above: **§ 3.1**, that
the pass-1 audited-cost and cache-share gates are only computable once a pass
finishes, because `4_detect_mounds_batch.py` writes `*.meta.json` once at the
end — so the card's "abort the proposer" is in practice a go/no-go on passes
2–3; and **§ 7 B2's design question**, that the 55-map unions cannot satisfy
both text-arm comparability and the card's `pass_provenance` requirement from a
single builder.

**What did NOT change**: the 55-map board and the MCC tiering (no re-tiering of
either, no signed row touched, no analysis row authored); every configuration
in `prompts/` and `inputs/`; `scripts/merge_passes.py` (the fix is the PI's, not
this session's); any committed union's content; and anything in sapphire's main
checkout. P1–P5 remain **UNTESTED** — pass 1 of three is in flight and
everything downstream of the proposer is unbuilt.

Also re-derives the verifier-leg sizing. The card's ≈ 8,500 survives, but on
two cancelling errors: the K = 5 → K = 3 candidate ratio is **0.923** where the
card assumed ≈ 0.67, and pass 1's measured detection density is **0.823** of the
GS's where the card assumed parity. The corrected components should be carried
forward, not the coincidence.

Tier-1 suite on sapphire after the changes: **2,496 passed, 4 skipped, 27
deselected, 3 xfailed**. `ruff check` clean on
`scripts/audit_proposer_cost.py`, `scripts/merge_passes.py` and
`scripts/stride55_prepare_and_union.py`; `markdownlint-cli2` clean on the card,
this report and the post-run record.

Commits: `c9294473d` (driver), `30e36bcd1` (calibration leg), `5a91463dc`
(card carried points), `e2fa3fc99` (this report's first relaunch revision),
`05349e9ff` (post-run launch-state record), `713a8c617` (card audited actuals),
and the commit that lands this correction.

### 2026-09-13 — Original publication

Pre-launch stage only; audit verdict BLOCKED, US$0 spent, nothing launched.
The card's cost basis was reproduced exactly (US$22.5004 over 6,990 GS
tile-passes, US$0.00322 per tile-pass) once the Gemini 3.7 rate card replaces
the Gemini 3 rates the metas stamp and the cache read is left undiscounted by
tier. Four items returned to the PI: approval provenance, the union builder's
recovery-fragment blind spot (demonstrated at 650 against 674), a stop-rule
basis under which the run's own metadata aborts a pass that is inside budget,
and a cache gate a 5-tile smoke reads at 16.3 %. `scripts/audit_proposer_cost.py`
landed with the exact-reproduction test as its guard.
