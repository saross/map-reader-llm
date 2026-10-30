# The 3.7 image screen: the modality gap is eliminated

> **Last revised**: 2026-10-15 (restated with the re-verified wrong-sheet
> rows, PI ruling D65 (2): every F1 moves; I3 now fails on the carried arm,
> whose optimum moved to (0.05, k5); parity and the escalation decision
> hold). Prior: 2026-09-13 (addendum only — the escalation section records
> that the F1-grounds decline stands while a tile-MCC-grounds K = 3
> campaign was approved; no finding, figure or verdict changed). See
> [§ Changelog](#changelog) for revision history.

**Classification**: registered-by-card GS screen
(`planning/gemini37-image-gs-2026-08-30.md`; expectations I1–I5
committed at PI go). Instruments: the image-B campaign machinery
(union → both verifier arms → sweep at 20 m vs the curated GS
reference), per-tile tile-swap micro-F1 permutation (10,000, seed
42) for every head-to-head. All gates green throughout (coverage
1,398/1,398 ×5 after recovery; verifier arms 674/674 with zero
failures each; every replication gate 1e-3 or better).

## Headlines

| Cell | Best @20 m | Point | P | R | MCC |
|---|---:|---|---:|---:|---:|
| 3.7-image + carried G3 verifier (arm 1) | **0.9381** | (0.05, k5) | 0.9212 | 0.9556 | 0.8345 |
| 3.7-image + 3.7 verifier (arm 2) | **0.9408** | (0.90, k5) | 0.9353 | 0.9463 | 0.8436 |
| 3.7-text screen best (committed) | 0.9238 | (0.10, k5) | — | — | — |
| all-3.7 text swap best (committed) | 0.9364 | (0.80, k5) | — | — | — |
| G3 image anchor (committed) | 0.8458 | (0.15, k9) | 0.8731 | 0.8201 | 0.8139 |

Since the 2026-10-15 restatement arm 1's best point is (0.05, k5), no
longer its registered (0.10, k5). Under PI ruling D65 (3) its registered
condition keeps (0.10, k5): F1 0.9353 [0.9110, 0.9535], P 0.9247,
R 0.9463, MCC 0.8307, 438 detections (`arm1/verified_op_20m.geojson`,
evaluated in `arm1/op-eval/`). The gap test and I1 below compare best
points.

Union: 674 candidates, 66 % unanimous (vs the text screen's 791 at
59 % — the image proposer proposes fewer, more consensual
candidates; per-pass raw detections varied under 1 % across the five
passes).

## The gap test (I2) — the campaign's question, answered

Within-family (text − image) at 20 m, tile-swap paired
(`gap_test.json`):

| Family | text − image | p | Verdict |
|---|---:|---:|---|
| Gemini 3 (committed) | **+0.0559** | 0.0005 | text significantly ahead |
| Gemini 3.7, carried-verifier pair | −0.0143 | 0.158 | statistically zero |
| Gemini 3.7, all-3.7 pair | −0.0044 | 0.677 | statistically zero |

**The modality gap is ELIMINATED at 3.7** (gap change −0.060 to
−0.070, roughly 2.4–2.8× the GS verified-set resolution, MDE₈₀
0.0246). The nominal sign flip is not significant — the honest claim
is parity, not inversion. I2 predicted "narrower by more than the resolution
(< ~0.031)"; the outcome overshoots the prediction to zero.

## Verdicts I1–I5

| # | Prediction | Verdict |
|---|---|---|
| I1 | 3.7-image above the G3 image anchor 0.8412 | **CONFIRMED at about four times the text-side gain** — +0.0923 (arm 1) / +0.0950 (arm 2) over the anchor's restated 0.8458, against the text side's +0.0221; the vision upgrade concentrated on the image track |
| I2 | Gap narrower than 0.0549 by > resolution | **CONFIRMED, overshot to parity** (above) |
| I3 | Lattices: carried arm prob 0.10–0.20; 3.7 arm ≥ 0.6 | **FAILS on the carried arm** since the 2026-10-15 restatement — its optimum is (0.05, k5) (0.9381, against 0.9353 at its registered (0.10, k5)), outside the predicted 0.10–0.20; the 3.7-verifier limb holds at (0.90, k5). Until then it read "CONFIRMED exactly — (0.10, k5) and (0.90, k5)" |
| I4 | Thinking < 1,000, ≈ text's 276 | **CONFIRMED, lighter** — 88–157 t/call (clean passes ~155) |
| I5 | Caching ≥ 90 % of input | **INFORMATIVE FAILURE** — 79.5 % at scale (probe 16 % parallel-cold / 54 % sequential); cost still under projection ($22.50 token-basis all-in proposer vs $32–36 projected) |

## The escalation question (PI economics rule)

All-3.7 image 0.9408 vs the all-3.7 text swap 0.9364: **+0.0044, not
significant** (and under the MDE80 ≈ 0.025). There is **no
resolvable new F1 high**, so the pre-agreed trigger for considering
the expensive 55-map image extension is NOT met. (Arm 2's image MCC
0.8436 likewise does not approach the committed GS MCC crown.) The
finding stands on the GS instrument: parity, at image-track prices
that caching makes comparable to text.

> **Addendum, 2026-09-13.** The paragraph above is unrevised (apart from
> the 2026-10-15 restatement of its numbers) and still correct: there is no resolvable new F1 high on the GS instrument, so
> the pre-agreed **F1** trigger for a 55-map image extension is NOT met.
> On 2026-09-13 the PI nonetheless approved a **K = 3** 55-map 3.7 image
> campaign on **tile-MCC** grounds — a distinct question this section did
> not weigh. The parenthetical above compares arm 2's GS image MCC
> (0.8322 when this addendum was written; 0.8436 since 2026-10-15) against the *GS* MCC crown, which is a GS-internal ranking;
> the approved campaign's case is the *deployment*-scale one
> (`planning/gemini37-image-55map-2026-09-13.md` § 1): on the 55-map
> board the sole tile-MCC Tier 1 is an image campaign, the image-over-text
> MCC gap is +0.03 to +0.07 there, and the 8,541-tile instrument resolves
> ΔMCC ≈ 0.01. So the F1-grounds decline recorded here stands, and the
> MCC question is what `results/gemini37-image-55map-2026-09-13/` answers.

## Operational notes (runner-fix queue; paper cost section)

Two flex-era lessons from execution: image mode at WORKERS=400 blew
the default fd ulimit (17 example images per call; passes died in
fd/SSL storms — fixed with ulimit 8192 + a 150-worker image cap,
`scripts/gemini37-image-gs-driver.sh`), and the daily ~13:00–19:00
UTC flex-storm window consumed two pass attempts before the
storm-resilient recovery driver swept all 4,288 residual tiles in
one 74-minute clear-window round. Total proposer spend including
every retry and recovery: $22.50 token-basis.

## Changelog

### 2026-10-15 — Restated with the re-verified rows (PI ruling D65 (2))

**Refresh trigger**: PI ruling D65 (2) (`planning/pi-decisions-2026-09-20.md`),
executed by the S164 restatement pass
(`reports/s164-agent-records/restatement-pass.md`). The legacy
nearest-tile rule had cut some union candidates' verifier crops from the
neighbouring sheet's raster, past the edge of its map, where the
verifier rejected them for want of a picture; PR #43 (`0e8a1fa7a`)
re-verified them on crops from their own sheet, the reader routing
(`9c843b980`) reads the re-verified rows, and PR #42 (`dddfcc0af`)
scores each candidate on its own sheet. Every comparison cell moved with
it (the text-B anchor, the Gemini 3 image anchor, the 3.7 text screen
and its swap), so the gap test's hand-typed `PAIRS` and `G3_GAP` got a
dated update (`3b240a4ac`). Both arms (arm 1 also at its registered
point, `--operating-point 0.10,5`), the gap test, and the best-set
evaluations were re-run on sapphire in two independent copies that agree
apart from timestamps and run roots, and committed at `f6f10d605`; the register's two
rows for the carried arm were re-pointed to its registered set at
`41acb3d50`. Every value equals the REPAIRED column of the 2026-10-13
re-score (`reports/s164-agent-records/rescore-repaired-gs.md` §§ 3–5,
surprise S6).

**One prediction fails, and the text now says so**: I3 on the carried
arm, whose optimum moved to (0.05, k5), outside the predicted 0.10–0.20.
I1's "about five times the text-side gain" becomes about four times; that
is new wording, not a new verdict.

| Quantity | Before | After |
|---|---|---|
| **Arm 1 best point; F1 there** | (0.10, k5); 0.9254 | **(0.05, k5); 0.9381 (I3 fails on this limb)** |
| Arm 1 at its registered (0.10, k5) | 0.9254 (its best) | 0.9353 [0.9110, 0.9535], P 0.9247, R 0.9463, MCC 0.8307, 438 detections (kept under D65 (3)) |
| Arm 1 best P; R; MCC | 0.9233; 0.9276; 0.8192 | 0.9212; 0.9556; 0.8345 |
| Arm 2 best F1 (0.90, k5); P; R; MCC | 0.9308; 0.9341; 0.9276; 0.8322 | 0.9408; 0.9353; 0.9463; 0.8436 |
| 3.7 text screen best (0.10, k5); all-3.7 text swap (0.80, k5) | 0.9139; 0.9265 | 0.9238; 0.9364 |
| G3 image anchor (0.15, k9); P; R; MCC | 0.8412; 0.8741; 0.8107; 0.7985 | 0.8458; 0.8731; 0.8201; 0.8139 |
| Gemini 3 gap (text − image) | +0.0549, p 0.001 | +0.0559, p 0.0005 |
| 3.7 gap, carried-verifier pair | −0.0115, p 0.253 | −0.0143, p 0.158 |
| 3.7 gap, all-3.7 pair | −0.0043, p 0.677 | −0.0044, p 0.677 (Δ −0.004345 → −0.004350; unrounded −0.0043504) |
| Gap change against Gemini 3; multiple of the resolution | −0.059 to −0.066; roughly 2.5× | −0.060 to −0.070; roughly 2.4–2.8× (MDE₈₀ 0.0246) |
| I1 gains over the G3 image anchor (arm 1, arm 2); text-side gain; ratio | +0.0842, +0.0896; +0.0178; ~5× | +0.0923, +0.0950; +0.0221; about four times |
| Escalation: all-3.7 image against the all-3.7 text swap | 0.9308 against 0.9265, +0.0043 | 0.9408 against 0.9364, +0.0044 (p 0.677) |
| MDE₈₀ quoted in the escalation section | ≈ 0.024 | ≈ 0.025 |
| Arm 2's image MCC (escalation, addendum) | 0.8322 | 0.8436 |

Sources: `arm1/analysis.json` (`image_best`, `operating_point`),
`arm1/op-eval/evaluation.json` (20 m interval), `arm2/analysis.json`
(`image_best`), `gap_test.json` (`pairs`),
`results/gemini37-screen-2026-08-28/analysis.json` and
`swap37/analysis.json` (`image_best`),
`results/image-b-gs-2026-08-28/analysis.json` (`image_best`,
`head_to_head_20m`), and `results/sensitivity-mde-2026-08-28/sensitivity.json`
(`mde_table[2].mde_80pc_power`); each read at `718d0ee08` (before) and at
the pass's head (after). The Gemini 3 gap's p is quoted from Image-B's
`analysis.json` (`head_to_head_20m`, 0.0005), the source the gap test's
`G3_GAP` names; the gap test's own copy (`g3_gap_committed.p`) read
0.001 at `f6f10d605` and was corrected to 0.0005 in `fc45ed53c`.

**What did NOT change**: parity (both 3.7 gaps statistically zero) and
the I2 verdict; I1, I4, I5 and their verdicts; I3's 3.7-verifier limb
at (0.90, k5); the escalation decision (no resolvable new F1 high, the
F1 trigger unmet) and the 2026-09-13 addendum's reading; the union
(674 candidates, 66 % unanimous), thinking volumes, caching rate, and
every spend figure. The Prediction column quotes the card's registered
text, so it keeps that card's values (0.8412, 0.0549). Older changelog
entries keep the figures they reported.

**Commits**: `3b240a4ac` and `fc45ed53c` (the dated gap-test constants); `f6f10d605`
(the regenerated arms, gap test, and evaluations); `41acb3d50` (the
register's carried-arm rows re-pointed to the registered set); this
document refresh in the restatement pass's document commit.

**Corrected the same day** (review of the pass's outputs): the all-3.7
gap and the escalation delta were first printed as −0.0043 and +0.0043.
The unrounded value is −0.0043504 (`gap_test.json` stores −0.00435), which
rounds to −0.0044, as the drafted register outcome prints it; the four
places above now read −0.0044 / +0.0044. The p value (0.677) is unchanged.

### 2026-09-13 — Escalation-section addendum (no findings changed)

**Trigger**: the PI's 2026-09-13 approval of a K = 3 55-map 3.7 image
campaign on tile-MCC grounds (`planning/gemini37-image-55map-2026-09-13.md`
§ 1) sat in direct contradiction with this document's escalation section,
which reads "the pre-agreed trigger … is NOT met". A reader arriving here
first would conclude the campaign should not have run. Recorded as the
residue of blocker B1 and as question Q1 in
`reports/gemini37-image-55map-deltas-2026-09-13.md` § 8.

**What changed**: an addendum blockquote appended to § "The escalation
question (PI economics rule)", plus this banner and entry. The original
text is untouched.

**Numerical claims that moved**: none. The I1–I5 verdicts, the 0.9308 /
0.9265 F1 pair, the +0.0043 delta, arm 2's image MCC 0.8322 and the
US$22.50 token-basis proposer spend are all unchanged.

**What did NOT change**: the F1 trigger is still recorded as unmet, because
it is; no GS board or tiering was touched; no operating point was refixed.

### 2026-09-02 — Original publication

Full screen executed and analysed (Session 145): five passes +
recovery to exact coverage, union 674, both verifier arms clean,
sweeps, the corrected within-family gap test (the campaign script's
built-in head-to-head pairs against the G3 anchor by design and was
not used for I2), verdicts I1–I5. Data commit `ada9822fe`.
