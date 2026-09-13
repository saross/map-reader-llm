# Gemini 3.7 image, 55-map K = 3 — pre-launch deltas and morning questions

> **Last revised**: 2026-09-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

Report on the pre-launch stage of the run specified by
`planning/gemini37-image-55map-2026-09-13.md`. The audit verdict is **BLOCKED**;
**no Application Programming Interface (API) call was made** and **US$0 was
spent**. The full audit is
`outputs/gemini37-image-55map-2026-09-13/pre_launch_audit.md`. Every claim below
carries its anchor; figures were read on 2026-09-13 at worktree commit
`dd5baf771`.

## 1. Audited spend per leg

| Leg | Card | Audited / corrected | Basis |
|---|---:|---:|---|
| GS calibration leg | US$1.2 | **US$0.75** | flex, 3.7 rate card, ≈ 450 candidates × 2 arms |
| 55-map proposer, 3 × 24,561 | US$237 | **US$237** | confirmed — see § 2 |
| K = 3 union, two arms (≈ 8,500) | US$22.7 | **US$14.1** | card is on the list basis; verify runs flex |
| K = 1 union, two arms (≈ 5,500) | US$9.1 (card: 14.7) | **US$9.1** | same correction |
| **Total** | **US$276** | **≈ US$261** | |
| **Actually spent this session** | — | **US$0.00** | nothing launched |

The card's envelope holds; the corrections are all in the favourable
direction. The verifier legs are on the list basis in the card because the
verify path stamps `cost_basis: list, discount 1.0`, which the card notes;
`run_pv.py verify` defaults `--service-tier flex`, so the true arm rates are
half the stamped ones. Corrected per-candidate, flex: arm 1 (Gemini 3)
≈ US$0.00071, arm 2 (3.7) ≈ US$0.00095 — arm 2's stamped figure additionally
carries the rate-card error of § 2.

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

No 55-map pass ran, so these are the GS anchors that the gate must be read
against.

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

## 4. Union sizes

None built — deliberately. The union builder is defective for this data
(§ 5, B2), so building the GS K = 3 calibration union first would have
silently produced a wrong artefact and fixed the carried operating points on
it. Expected sizes remain the card's ≈ 5,500 (K = 1) and ≈ 8,500 (K = 3).

## 5. P1–P5 verdicts

**All five are UNTESTED.** No proposer pass, no verifier arm, no score. The
predictions stand as written in the card. Two observations bear on how they
should be read when the run does happen:

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

## 6. What did NOT change

- **No API call, no spend, nothing launched.** US$0.00.
- **No union, no verifier run, no score, no permutation test.**
- **The card is untouched** — no banner change, no § 2 carried points, no § 3
  actuals, no changelog entry. Fixing § 2 in advance of the PI's ruling would
  be recording a decision that has not been made.
- **The 55-map board and the MCC tiering are untouched**; no re-tiering, no
  signed row touched, no analysis row authored.
- **`scripts/merge_passes.py` is untouched.** The defect in § 7 is real and
  demonstrated, but fixing `resolve_pass_files` changes what any rebuilt union
  contains, which reaches committed artefacts across the project. That is a
  PI call, not an audit fix, and it is outside what the card approves.
- **`prompts/`, `inputs/` and every configuration are untouched.** The audit
  was read-only over them; the only files added are the audit, this report and
  `scripts/audit_proposer_cost.py`.

## 7. Why it is blocked

Two governance-and-tooling blockers, and two gate definitions that would
misfire. Full detail in the audit; in brief:

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

**B3, B4** are the stop-rule basis (§ 2) and the smoke cache gate (§ 3).

## 8. Morning questions

1. **Is the API gate approved, and is the card's banner to be updated to say
   so?** Recording the ruling in the card as the
   `gs-era2-verified-board-2026-09-10` sign-off was recorded would close B1. If
   it is approved, does the PI want the S152 decline and the GS findings'
   escalation sentence annotated, so the record is not self-contradictory?
2. **Which basis does the US$110 stop measure?** Recommend: the audited basis,
   computed with `scripts/audit_proposer_cost.py`, pinned in the card in those
   words. On that basis pass 1 is ≈ US$79; on the meta's own figure it is
   US$126 and the run aborts.
3. **How should `merge_passes.py` be repaired?** Recommend folding `run_N*`
   into pass N with a tier-1 test, then re-deriving the GS K = 3 union and
   checking it against the K = 5 union of 674. The wider question is whether
   any committed union was built through the defective path — the GS
   `union_k5.geojson` (674) was not, since the defective path yields 650, so
   some other builder produced it and should be identified before the fix
   changes anything.
4. **Does the smoke gate become mechanism-only?** Recommend yes: model,
   thinking, temperature and tier stamped, `include_example_images` true, 17
   examples, tile size 384 — with the ≥ 70 % cache gate applying from pass 1
   onwards, where the GS floor is 0.751.
5. **What is the schedule and who finishes it?** Clean-window throughput was
   **3,884–4,608 tiles/h** at `--workers 150`, so a pass is **5.3–6.3 h**;
   inside the flex-storm window it fell to **0.5–60 tiles/h**. Three passes
   plus crop extraction, four verifier arms and the scoring and permutation
   work is 24–48 h of wall clock. This needs a storm-resilient driver on the
   GS pattern and a named handover; it cannot be one session.
6. **Should P1's interpretation be pre-committed given § 5?** The image-MCC
   advantage on the GS is carried by F1-poor single-pass cells, and the two
   comparators are not co-tiered. Worth settling before the numbers exist, so
   the reading is not chosen after seeing them.

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

## Changelog

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
