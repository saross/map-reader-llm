# D9 signature notes for the signed 55-map analyses: replicate floors — draft for the PI

> **Last revised**: 2026-10-07 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Status: DRAFT for the PI's approval; nothing has been written to
`results/run-analyses.json`.** Tracker W1.5 for W2.7
(`planning/text-track-transmission-2026-10-05.md`); basis
`reports/w27-replicate-floors-2026-10-06.md` § 8 item 2 ("a D9 note on the
signed 55-map analyses recording the floors … and the verifier-date
confound of the k3 cells; no tier changes"), under rulings D45, D46, D48
and D49 (`planning/pi-decisions-2026-09-20.md`).

**Why a signature note and not an amendment.** Every row below is
`signature.status: signed` (read 2026-10-07). Under D9 a signed row's
outcome text is left untouched: the signature stands, a dated note is
appended to `signature.attests`, and the prior attests text moves to
`signature.history`, as for the D19 and D33 notes on
`55map-final-board-r2-2026-09-06` (2026-10-04 and 2026-10-05). The notes
change how a difference is read, not any figure, tier or test, so no row's
outcome, tiering or verdict changes.

**What the notes record.** (1) The floors of the report's § 6b: within one
execution, or runs at most seven days apart (D48), about 0.007 F1 at
N = 5, 0.006–0.010 at N = 3, 0.008–0.010 at N = 1 and 0.006–0.008 at
N = 10 (the Gemini 3 image pool 0.017–0.021); a nested threshold or
pass-count contrast on the same passes its own floor, 0.002–0.007; runs
further apart about 0.010–0.018 (§ 7.2's floors line). (2) The
verifier-date mix of the k3 cells: TH7, T03 and TM at 3-of-5 add a vote-3
shell verified on 2026-06-06, 40–49 days after their 4-of-5 legs, and
Run A's one-date reading of T03 and TM (§ 6c). (3) The readings of each
row's outcome that the floors change.

Placeholders: `<APPROVED_AT>` is the PI's approval timestamp, filled at
application.

## 1. `55map-final-board-r2-2026-09-06`

Signed 2026-09-17T07:01:26Z; notes of 2026-10-04 (D19) and 2026-10-05
(D33) already appended. Outcome (unchanged): "512/595 pairs significant,
12 tiers. Top: ARM2-N5-oracle 0.8871; …".

> SIGNATURE NOTE 2026-10-07 (D9 pattern; replicate floors, rulings D45,
> D46 and D48; Run A, D49; approved by the PI `<APPROVED_AT>`). The
> tile-swap test behind "512/595 pairs significant" and the 12 tiers
> compares outputs, not configurations: between two verified single passes
> of one execution it rejects 11-24 % of pairs for the Gemini 3 text
> families on this corpus. Under D45 a
> configuration claim read from this board needs the difference to exceed
> the replicate floor for its rung and run dates
> (reports/w27-replicate-floors-2026-10-06.md section 6b): within one
> execution, or runs at most seven days apart (D48), about 0.007 F1 at
> N = 5, 0.006-0.010 at N = 3, 0.008-0.010 at N = 1 and 0.006-0.008 at
> N = 10 (Gemini 3 image pool 0.017-0.021); a nested threshold or
> pass-count contrast on the same passes, its own floor of 0.002-0.007;
> runs further apart, about 0.010-0.018. Significant pairs and adjacent
> tiers inside these floors are differences between these outputs. THE k3
> CELLS MIX VERIFIER DATES: TH7-oracle, T03-oracle and TM-oracle add a
> vote-3 shell verified 2026-06-06, 40-49 days after their 4-of-5 legs
> (2026-04-18 to 05-02, 2026-04-26/27 and 2026-04-18). Run A re-verified
> T03 and TM on one date (2026-10-07): T03 k3 - k4 +0.0092 -> +0.0084 and
> TM +0.0275 -> +0.0264, with no 4-of-5 cell moving significantly
> (section 6c); TH7 has no one-date reading. RUN DATES: the cells come
> from runs of 2026-04-18 to 06-11 (the Gemini 3 incumbents and the
> uplift), 08-25 to 08-27 (A and B) and 08-29 to 09-01 (the 3.7 arms and
> the fourth cell), and same-signature runs on different dates are not
> replicates (Obs 497). READINGS THE FLOORS CHANGE (section 7.2): A beats
> B at N = 1 (A-N1-oracle - B-N1-oracle +0.0214, p < 0.0001, above its
> floor), the reverse of N = 3, 5 and 10; B-N5-carried over T03-oracle
> (+0.0104) is inside the cross-date floor (0.0106); B-N5-carried and
> B-N10-carried are equal (+0.0006, p = 0.72); the N5-to-N10 oracle
> steps of A and B (0.0036, 0.0043) are inside their nested floors (0.0069,
> 0.0058); ARM2-N5-carried over FOURTH-N10-carried (+0.0099) and
> ARM2-N1-oracle over B-N5-carried (+0.0107) clear their within floors
> under D48 (1.4 and 1.9 times), assuming little proposer drift within a week. UNCHANGED: the 35-cell tiering, its
> 595-pair family, every F1, MCC, tier, group and cost, the addendum, and
> both efficiency frontiers. The signature of 2026-09-17 stands for the
> tiering; the PI approves this reading of it as of this note.

## 2. `55map-r2-leaderboard-50m`

Signed 2026-09-17T07:01:26Z; no note yet. Outcome (unchanged): "24/28
pairs significant, 5 tiers, identical tier structure to the r1
standardised board; leader T03-k3 (oracle) 0.8387."

> SIGNATURE NOTE 2026-10-07 (D9 pattern; verifier-date mix and replicate
> floors, rulings D45, D46 and D48; Run A, D49; approved by the PI
> `<APPROVED_AT>`). Three of the eight cells, T03-k3 (the leader), TH7-k3
> and TM-k3, mix verifier dates: their 4-of-5 candidates were verified
> with the run (2026-04-26/27, 2026-04-18 to 05-02, 2026-04-18) and their
> candidates with exactly three votes on 2026-06-06, 40-49 days later.
> TM-n10-k5's ten passes come from two executions 54 days apart
> (2026-04-18 and 06-11). Every k3-versus-k4 contrast on the board is
> therefore also a contrast between verifier dates. Run A re-verified
> T03's and TM's candidates on one date (2026-10-07): T03 k3 - k4
> +0.0092 -> +0.0084 (p = 0.0013), 1.2 times its replicate floor (0.0069,
> upper 0.0111); TM +0.0275 -> +0.0264; neither 4-of-5 cell moves
> significantly (+0.0021, +0.0020) (reports/w27-replicate-floors-2026-10-06.md
> section 6c; section 6a gives the same +0.0264 for TM from a June
> re-verification). TH7's +0.0219 has no one-date reading but is about ten
> times the largest measured date shift on these contrasts (about 0.002).
> Under D45 and D48 (section 7.2): T03-k3 over TH7-k4 (+0.0225, the joint
> oracle gap) clears the cross-execution floor (0.011-0.013); TH7-k3 over
> TM-k3 (+0.0279, same-day proposers and same-day shells) clears its
> floor; T03-k3 and TH7-k3 tie (+0.0006, p = 0.855); TM-n10-k5 over TM-k3
> (+0.0172) clears its mixed-date floor (0.0117) but cannot be separated
> from its second execution, and TH7-k3 over TM-n10-k5 (+0.0106) is inside
> that floor. UNCHANGED: the 28-pair family, the five tiers, every F1 and
> MCC. The signature of 2026-09-17 stands.

## 3. `stride55-sweep-oracle-2026-08-27`

Signed 2026-09-17T07:01:26Z; no note yet. Outcome (unchanged): "… P6 FAIL
— the pre-named informative failure: B beats A (primaries -0.0096
p=0.0147; oracles -0.0141 p=0.0001; BH-robust). … Transfer taxes
+0.0036/+0.0081 vs the incumbent's +0.0324 — the tax COLLAPSED. …"

> SIGNATURE NOTE 2026-10-07 (D9 pattern; replicate floors, rulings D45
> and D46; approved by the PI `<APPROVED_AT>`). Against the replicate
> floor for two same-day runs at N = 10 (0.0072, upper 0.0106;
> reports/w27-replicate-floors-2026-10-06.md sections 6b and 7.2), P6's
> "B beats A" holds at the oracles (-0.0141; r2 -0.0141, 2.0 times the
> floor) and only narrowly at the carried primaries (-0.0096; r2 -0.0106,
> at the floor's upper bound). The incumbent's +0.0324 tax is measured on
> the canonical chain against the T0.3 x 3-of-5 joint oracle, a cell whose
> vote-3 candidates were verified on 2026-06-06, 40 days after its run's
> own verifier leg. On r2 the same tax is +0.0237 and the oracle-to-oracle
> gap in the P5 decomposition is +0.0161 (p = 0.0001), not +0.0027, so the
> decomposition depends on the chain; A's and B's own r2 taxes are +0.0027
> and +0.0062, so the collapse holds on both chains. A and B (proposers
> 2026-08-25/26) are compared with an incumbent run four months earlier,
> with thinking level, pass count and tiling also different, so the
> comparison is between runs, not a geometry effect. UNCHANGED: every
> P-verdict and every figure in the outcome. The signature of 2026-09-17
> stands.

## 4. `stride55-ladder-2026-08-27`

Signed 2026-09-17T07:01:26Z; no note yet. Outcome (unchanged): "… P7 PASS
at the carried points (A -0.0004 p=0.82; B +0.0016 p=0.32 — B's N=5
carried ABOVE its N=10 carried); small real oracle residue (-0.0040
p=0.0131 / -0.0053 p=0.0003, BH-sig). …"

> SIGNATURE NOTE 2026-10-07 (D9 pattern; replicate floors, rulings D45
> and D46; approved by the PI `<APPROVED_AT>`). Two readings in the
> outcome sit inside the replicate floor of a pass-count step on the same
> passes (reports/w27-replicate-floors-2026-10-06.md section 6b;
> floors-v2/results/rescreen.csv). "B's N=5 carried ABOVE its N=10
> carried" (+0.0016 canonical; r2 +0.0006, p = 0.72; floor 0.0059) is a
> tie. The "small real oracle residue" (-0.0040 / -0.0053 canonical; on
> r2 N = 10 above N = 5 by 0.0036 and 0.0043) is inside the nested floors
> (0.0069 for A, 0.0058 for B), so it is a difference between these
> outputs, not evidence that the tenth pass helps at the oracle. P7's
> carried-point ties stand. UNCHANGED: every P-verdict and every figure.
> The signature of 2026-09-17 stands.

## 5. `gemini37-55map-grid-2026-08-31`

Signed 2026-09-12T09:03:09Z; no note yet. Outcome (unchanged): "… both
verifier-axis tests are BH-significant … and neither proposer-axis test is
(arm 1 - B N=5 +0.0056, p = 0.3488; arm 2 - fourth +0.0107, p = 0.0738)
…"

> SIGNATURE NOTE 2026-10-07 (D9 pattern; replicate floors, rulings D45,
> D46 and D48; ruling D42's test; approved by the PI `<APPROVED_AT>`). The
> outcome's "neither proposer-axis test is" significant holds on the
> declared per-sheet test. On D42's tile-swap test on the r2 final board,
> arm 2 over the fourth cell is +0.0099 (p = 0.0198, BH 0.024), 1.4 times
> its within-execution floor (0.0072), which D48 applies because the runs
> are at most seven days apart, assuming little proposer drift within a week; arm 1 over B N = 5 stays a tie on both
> tests (+0.0048, p = 0.27; floor 0.0063)
> (reports/w27-replicate-floors-2026-10-06.md sections 6b and 7.2). The
> proposer axis under the 3.7 verifier is therefore a small difference
> between pools of five and ten passes rather than a null, and the family
> gain lives mostly, not wholly, in the verifier seat. Both verifier-axis
> contrasts (+0.0270, +0.0234) and the all-3.7 diagonal (+0.0325) clear
> their floors. UNCHANGED: the declared five-test family, its verdicts on
> the per-sheet test, and every figure. The signature of 2026-09-12 stands.

[DRAFT NOTE: "mostly, not wholly" matches the drafted § R7.3 wording, which
is itself pending the PI's ruling. If the PI keeps "lives in the verifier
seat" in the paper, this sentence should go.]

## 6. `gemini37-55map-gridboard-2026-08-31`

Signed 2026-09-12T09:03:09Z; no note yet. Outcome (unchanged): "… All
seven carried-to-oracle contrasts are BH-significant, including arm 2's
+0.0043 (adjusted p = 0.000162) … whereas arm 1's carried N3-to-N5 IS
significant at +0.0076 (adjusted p = 0.000162). … The N = 1 economy is an
ORACLE statement …"

> SIGNATURE NOTE 2026-10-07 (D9 pattern; replicate floors, rulings D45,
> D46 and D48; approved by the PI `<APPROVED_AT>`). Against the floors of
> reports/w27-replicate-floors-2026-10-06.md section 6b: arm 2's +0.0043
> carried-to-oracle tax is about twice the replicate floor of a threshold
> step on the same passes (0.0020, upper 0.0033), so it is a small real
> effect, as the outcome says. Arm 1's carried N3-to-N5 step (+0.0076) is
> above the nested pass-count floor's point value (0.0053) but inside its
> upper bound (0.0127), so arm 1's non-saturation is narrow; arm 2's
> N3-to-N5 tie stands (floor 0.0066). The N = 1 economy's oracle cell
> clears its within floor under D48: on r2, ARM2-N1-oracle over
> B-N5-carried is +0.0107 (p = 0.0125), 1.9 times 0.0055, assuming little proposer drift within a week. UNCHANGED: the
> 120-pair family, the six tiers and every figure. The signature of
> 2026-09-12 stands.

## 7. Signed 55-map rows screened, no note proposed

| Row | Why no note is proposed |
|---|---|
| `stride55-a5-vs-b5-2026-08-27` | "B N=5 carried beats A N=5 carried … a real ~0.012" stands: r2 −0.0120 (p = 0.0024) is 1.7 times its floor (0.0072, upper 0.0111). A confirming note is optional. |
| `55map-r2-leaderboard-mcc-50m` | The leader, IM-k3 (MCC 0.7110), is a single-date verifier cell (2026-04-18); its runners-up T03-k3 and TH7-k3 mix dates. No MCC floor has been measured (W2.5), so the floors neither confirm nor qualify its outcome (report § 7.1, R7.1-12/15: "stands on F1 reasoning only"). |
| `55map-final-board-2026-08-27` | The standardised-reference board that r2 superseded in the paper (ruling 1). Its outcome makes two claims the report did not screen: "A does not [saturate at N = 3] (A-N3-carried sig below A-N5)" (on r2, −0.0075, p < 0.0001, against a nested floor not yet measured for A at N = 3 against N = 5) and "A single pass of A … ties the HIGH incumbent". If the PI wants a note here, it needs that screen first. |
| `gemini37-image-55map-2026-09-13`, `gemini3-image-55map-2026-09-16`, `gemini37-image-55map-k5-replicate-2x2-2026-09-20` | Their K-step and 2 × 2 claims are judged against the verifier's re-invocation drift (+0.0005 to +0.0008 F1), not a proposer floor. The report measured the 3.7 image pool's single-pass floor (0.0055–0.0066, § 6) and the Gemini 3 image pool's (0.017–0.021, § 6b), but no K = 3 or K = 5 image floor, and § 7 did not screen these rows (they are not draft claims). A screen should come before any note. |
| `uplift-supplement-flatten`, `verifier-uplift-pairing` | Not configuration contrasts between runs (a flattening of conditions; verifier-against-consensus twins on shared passes); the measured floors do not bear on their outcomes. |

## Evidence

- Signature status, outcome text and history of every row:
  `results/run-analyses.json`, read 2026-10-07.
- Floors: `reports/w27-replicate-floors-2026-10-06.md` § 6b (within and
  image-pool floors), § 7.2 (the floors line, the cross-execution band and
  every verdict quoted), and
  `reports/w27-replicate-floors-2026-10-06-scripts/floors-v2/results/rescreen.csv`
  (each claim's floor, upper bound and within part).
- Verifier dates: `results/passes-manifest.json` → `timestamps` (rows
  `<run>::verified::run1` and `<run>::vote3-increment::run1`); TM's main
  verifier leg from `outputs/55maps-text-min-generalisation/post_run_report.md`.
- Run A: `reports/w27-replicate-floors-2026-10-06.md` § 6c (outputs
  `f13f7b308`); the text MIN June reading, § 6a.
- r2 differences and p-values:
  `results/55map-final-board-r2-2026-09-06/final_board_50m.json` →
  `pairwise` and `results/55map-leaderboard/55map_leaderboard_50m_r2.json`
  → `pairwise`, read 2026-10-07.
- Canonical figures: `results/stride55-2026-08-27/findings.md` (headlines
  and § "The P5 overshoot, decomposed").

## Changelog

### 2026-10-07 — Original publication (W1.5, W2.7)

Drafted for the PI's approval alongside the same day's drafted edits to
`docs/paper/results-draft.md` and the claims inventory. Six notes drafted;
eight signed rows screened with no note proposed. Nothing written to the
register.
