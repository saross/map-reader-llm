# Results rulings — claims-with-anchors deltas (S153, 2026-09-12)

> **Last revised**: 2026-09-12 (original publication; execution of the PI's
> seven Results rulings of 2026-09-12). See [§ Changelog](#changelog) for
> revision history.

**What this is.** Every number changed in `docs/paper/results-draft.md`
under the PI's rulings of 2026-09-12, one claim per row, with the draft
value, the anchor value, and the `file:line` the anchor was read from. Then
the reference-r2 sweep table, where the rulings were recorded, the new
block's claim count, and what did not change.

**Anti-confabulation.** Every anchor below was opened and re-read in this
session before the edit was made. Nothing was copied from
`docs/paper/results-claims-inventory-2026-09-12.md`, which is the document
being acted on and is therefore not an authority for the values it
reports; nothing was taken from `planning/paper-writeup-continuity.md`,
from a memory, or from the draft's own prior text. **Every anchor
reproduced the inventory's value.** No claim had to be stopped on, so the
three-value stop report the brief provides for is empty.

**Cost of the session**: US$0 API, and no compute — the whole pass is
reads of committed files plus edits to five Markdown documents. Nothing
was recomputed; where an r2 value was needed it was found in a committed
artefact or recorded as absent.

**Branch**: `worktree-agent-ade6eca3c3102284a`. Commits are named per
section.

---

## 1. Ruling 4 — the fourteen DRIFTED and two UNANCHORED claims

Commit `0b9caf33b`. Thirteen of the fourteen DRIFTED claims took an edit;
R4-28 took a note rather than a number, because ruling 7 resolves it in
the draft's favour (§ 1.3). Both UNANCHORED figures were found to have
sources and are anchored rather than cut (§ 1.2).

### 1.1 The numeric deltas

| # | claim | draft value | anchor value | anchor read at |
|---|---|---|---|---|
| R0-02 | 55-map instrument composition | 4,731 student + 279 extension (r1) | 4,726 + 278 + 14 audit-reviewed = 5,018 (r2) | `results/55map-leaderboard/55map-leaderboard-50m-r2.md:31,34,36,40` |
| R0-03 | as-digitised student records | 4,090 | 4,085 (= 4,726 − 641 stated at `:31`), p90 18.3 m at `:33` | same file `:31-33` |
| R1-02 | conditions in the plateau analysis | 259 | **306** (skipped: 86 non-GS corpus, 46 with < 10 buffers) | `results/working-precision/gs-plateau-characterisation.md:5` |
| R1-03 | single-pass plateau onset | 40 m | **75 m** (`single-pass/none`, n = 133) | same file `:17` |
| R1-05 | "modality, not architecture, is dominant" | modality dominant | modality 30 → 75 m (text `:34`, image `:35`); architecture 30 → 75 m (PV `:19`, single-pass `:17`) — the same range | same file `:17-19,34-35` |
| R4 heading | architecture claim | "is the best architecture on every tile size" | E83 retracted "sole"/"single best" as statistical claims; the surviving claim is point-estimate | `results/run-analyses.json` → `era1-leaderboard` outcome, E83 block |
| R4-12 | consensus tile-size preference | "consensus prefers 384 px" | "Text MINIMAL consensus still prefers 512 (+0.02..+0.05 over 384 across T0.3/0.7/1.0) … Text HIGH consensus FLIPS to 384 (T0.7 0.814 > 512 0.773)" | `results/run-analyses.json` → `tile-size-sweep` outcome |
| R4-13 | consensus + verifier at 512 px | 0.792 | **0.793** ("View 3 … 384=0.890 > 256=0.856 > 512=0.793") | same row |
| R4-23 | lowest Tier-1 vs best sweep optimum | +0.020, p = 0.16 | `observed_diff` **0.019453**, `p_value` **0.1783**, `bh_adjusted_p` **0.243827**, `significant: false` | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json`, pairwise row `gemini37-screen-2026-08-28::g37-text-k10-verified-carried-p0.10-k10-era2b` vs `pv-diag-384::pv-high-text-t0.3-n5-opmax` |
| R4-24 | top cell vs best sweep optimum | +0.037, p = 0.011, BH 0.021 | `observed_diff` **0.035949**, `p_value` **0.0158**, `bh_adjusted_p` **0.028401**, `significant: true` | same file, pairwise row `gemini37-image-gs-2026-09-01::g37-image-k5-verified-swap37-p0.90-k5-era2b` vs the same cell |
| R4-29 | nine `-opmax` cells, mechanism | "found mis-materialised … rebuilt from their stages" | "it is **not staleness** … in all nine it is the **327-tile Era-3 frame's** optimum recorded in `pv_registry_327.json`"; magnitudes +0.0004 to +0.0081 confirmed independently | Obs 466 heading `docs/notes/working-notes.md:33812`, mechanism `:33825-33831`; magnitudes at `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md:156-157` |
| R5-15 | min6 vs high6 | 0.8784 vs 0.8641, p = 0.66 | "min6 (**n30-lineage, 0.8708**) vs high6 (0.8641) p=0.656 … The TRUE min6 merge (**0.8784**) sits numerically above its permuted n30-lineage stand-in" | `results/run-analyses.json` → `min-vs-high-thinking-pv` outcome |
| R7.1-07 | correction across cells | "uniform across cells" | "below it for 32 of 35 cells … at it for one, marginally above it for the two lowest-recall cells" | `results/run-analyses.json` → `estimated-correction-r2` outcome |
| R7.1-13 | text-only cells on the MCC board | "the six text-only cells keep their F1 ordering" | **seven** text-only cells (IM-k3 is the only image cell); TM-n10-k5 MCC **0.6695** at rank 4 overtakes T03-k4 **0.6691** at rank 5, inverting their F1 ranks 4 and 3 | `results/metric-leaderboards/55map-mcc-tiering-r2.md:7-14` |
| R7.2-19 | estimated-correction direction | "every cell by −0.0004 to −0.0007" | within 0.0007 of the r2 point; below for 32 of 35, at it for one, **above** for two (TM-k4 **+0.0003**, IM-k4 **+0.0007**) | `results/run-analyses.json` → `estimated-correction-r2` outcome |
| R7.2-23 | uplift family row cost | "none" | **$58** (row 28, `UPL-oracle`, basis oracle, tier 8) | `results/55map-final-board-r2-2026-09-06/final-board-50m.md:38` |

Sixteen rows: the fourteen DRIFTED claims of the inventory's cross-section
summary, R4 heading (listed there as wrong-without-being-drifted), and
R7.1-07, which the corrected R7.2-19 forces. R4-28 is at § 1.3.

### 1.2 The two UNANCHORED figures — both anchored, neither cut

**R5-01, the "≈ $54 flex as-run" programme cost.** The inventory could
not locate a programme total, and there is none: no artefact carries the
sum. But all four component stage costs are anchored in the findings
document, and they sum to the quoted figure:

| stage | cost | anchor |
|---|---:|---|
| Stage 1, T = 0.0 (31,470 calls, 0 failures) | $21.93 flex | `results/verifier-robustness/verifier-robustness-findings.md:57` |
| Stage 2, one rung per temperature | $8.71 flex | same file `:212` |
| Thinking × temperature matrix, three new cells × 4,275 calls | $20.86 flex | same file `:224` |
| Operational maximum, 16of30 + N = 5 T0.3 | $2.54 flex | same file `:294` |
| **sum** | **$54.04** | — |

The draft now states it as a sum with the four line anchors inline, and
says explicitly that the document carries no programme total. That is
honest and keeps a figure the PI may still prefer to cut; the inventory's
own recommendation was to drop it, and dropping it remains a one-line
edit. *Independent corroboration of the derivation, not used as its
anchor:* the draft's own 2026-06-13 changelog entry records the same four
addends.

**R8-07, the "+3 %/+5 %" recall band.** The band is not a computed
interval, and the inventory was right that its endpoints do not follow
arithmetically from the measured 2.4–2.7 %. They are the two rows of Obs
361's "Sensitivity framing for the paper" table — "+3% true population →
~0.836" and "+5% true population → ~0.829"
(`docs/notes/working-notes.md:19945-19950`) — chosen to bracket the
measured inflation from above. The decision to present the band rather
than a point correction is recorded at
`reports/session-111-discoveries.md:170-173`: "report the +3 %/+5 %
sensitivity band with the measured 2.4–2.7 % central estimate … wide band
preferred because the ratio rests on 4 events." The draft now carries both
anchors in an `[ANCHOR: …]` note and says the band should be stated as a
judgement rather than a measurement. The measured basis it brackets is
`results/working-precision/gs-miss-correlation.json`:
`implied_55map_recall_inflation_factor` 1.0242 at 20 m and 1.0271 at 30
and 50 m, `both_miss` 4 of `n_curator_in_bounds` 435, `fisher_p`
0.281–0.323 — so the correlation the band widens for is itself
non-significant, which the draft already implies.

### 1.3 R4-28 — no number changed, on ruling 7

The inventory marked this "DRIFTED — conflicting record" across three
artefacts. Ruling 7 resolves it: the timestamp is real. The three records
as re-read this session:

| record | says | read at |
|---|---|---|
| register | `manually_verified_at: 2026-09-10T12:34:56Z` | `results/run-analyses.json` → `gs-era2-verified-board-2026-09-10` |
| board README, changelog entry "2026-09-10 (evening) — Signed" | "The PI ruled G1 satisfied on the true-input reproduction and signed the analysis row at 2026-09-10T12:34:56Z" | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md:202-204` |
| board README, two earlier entries' closing lines | "The analysis row remains UNSIGNED; the publication ruling is the PI's." | same file `:200` and `:248` |

The README therefore contradicts itself rather than contradicting the
register: its "Signed" entry is the newer record and the two "remains
UNSIGNED" lines are boilerplate carried on entries the signing entry
supersedes. The draft's "SIGNED by the PI on 2026-09-10" stands; its note
now names the register field, cites ruling 7, and flags the two stale
README lines. **Left undone deliberately**: the README itself is a results
artefact, not a paper document, and correcting a results artefact's
changelog was outside this brief — it is a one-line fix in two places and
is listed in § 6.

---

## 2. Ruling 1 — the reference-r2 sweep across R0, R8, and R9

Commit `a6ac82e0d` (R0's composition landed in `0b9caf33b`, being also a
DRIFTED row). § R7 had been on r2 since erratum E84; §§ R0, R8, and R9
had not, so a reader met the instrument one or two revisions behind the
boards it introduces.

| figure | old reference | r2 value, or "no r2 twin" | anchor |
|---|---|---|---|
| § R0 instrument composition | r1: 4,731 student + 279 extension | **4,726 + 278 + 14 = 5,018** | `results/55map-leaderboard/55map-leaderboard-50m-r2.md:31,34,36,40` |
| § R0 positional provenance | r1: 641 reviewed + 279 extension marked; 4,090 as-digitised | **641 reviewed + 278 extension + 14 audit-reviewed marked; 4,085 as-digitised**, median 8.6 m, p90 18.3 m | same file `:31-38` |
| § R8 phantom-pool adjudication | standardised: 278 of 773 + 1 marking-pass extra | **278 of 773 stand in r2**; the audits then removed 6 and added 14 | same file `:26-40` |
| § R8 reference residual | not stated in the draft | **≈ 50 mounds (≈ 1 % of GT)** unseen by both channels, carried by the estimated-correction column not the point estimate | same file `:44-51` |
| § R8 recall inflation ~2.4–2.7 % | GS curator twin, pre-r2 | **no r2 twin** — marked `[REF: r1]` | `results/working-precision/gs-miss-correlation.json` (`implied_55map_recall_inflation_factor` 1.0242 / 1.0271) |
| § R8 double-miss correlation 1.5–1.7× | GS curator twin, pre-r2 | **no r2 twin** — marked `[REF: r1]` | same file (`both_miss` 4, `n_curator_in_bounds` 435, `correlation_ratio` 1.5 / 1.67) |
| § R8 ~370 residual duplicates, ≈ 0.03 F1 | standardised README | **no r2 twin** — marked `[REF: r1]`; the r2 board doc explicitly refers the reader back to the standardised README and Obs 396 for this account | `results/55map-leaderboard/55map-leaderboard-50m-r2.md:51` |
| § R8 net reference bias ≈ −0.017 | standardised README | **no r2 twin** — marked `[REF: r1]` | as above |
| § R8 "+3 %/+5 %" band | GS-derived (Obs 361) | **no r2 twin** — the band is a judgement (§ 1.2) and covered by the same `[REF: r1]` marker | `docs/notes/working-notes.md:19945-19950` |
| § R9 GT-free top pick vs true winner | canonical p = 0.127; standardised p = 0.857 | **r2 p = 0.8553**, added alongside | `results/55map-leaderboard/55map_leaderboard_50m_r2.json`, pairwise `T03-k3 (oracle)` vs `TH7-k3`: `observed_diff` 0.000632, `p_value` 0.8553, `bh_adjusted_p` 0.8553 |
| § R9 Spearman ρ = +0.881 | canonical board | **unchanged on r2** — the r2 board's eight ranks are cell-for-cell the standardised board's, so any rank correlation against the true board is invariant; the draft now says so | r2 ranks `results/55map-leaderboard/55map-leaderboard-50m-r2.md:7-14` against standardised ranks `results/55map-leaderboard/55map-leaderboard-50m-standardised.md:6-13` |
| § R9 unanimity inversion ρ = −0.095 | canonical board | **unchanged on r2**, by the same invariance; covered by the clause above rather than restated | `results/gtfree-selection/gtfree-selection-findings.md:62-66` |

**Counts**: 12 figures swept. **6 re-pointed to an r2 value** (R0 ×2,
R8 ×2 including the newly-added r2 residual, R9 ×2 counting the
invariance statement); **5 marked `[REF: r1]`** with no r2 twin, all in
R8, all under one marker so the prose is not littered; **1** (R9's
unanimity ρ) covered by another row's clause.

**Out of scope by instruction.** § R6's transfer table quotes the
standardised vintage and its register row already flags a divergence of up
to 0.008 from the canonical-vintage deltas. R3 and R6 were left untouched
for the parallel K-ladder job; D18 in the outline records that R6 inherits
ruling 1 when that job lands. A further r2 candidate also out of scope
here: `results/uplift-supplement/conditions.csv` carries 37 rows at
`reference` r2 / `frame_id` `55maps-8541` / `buffer_m` 50 with `n_refs`
5018, which is the machine-readable r2 stratum a supplement table could be
generated from directly.

---

## 3. Where the rulings are now recorded

Commit `269fb8d29`.

| ruling | recorded at | form |
|---|---|---|
| 1 — r2 throughout | `docs/paper/results-outline.md` § D18 | new SETTLED decision, D-series, with the R6 inheritance noted |
| 2 — the Gemini 3.7 stack as headline | `docs/paper/results-outline.md` § D19; cross-noted at § D2 (numbers superseded, placement intact), at the R0 block (the echo), and at the R7 block (the home) | new SETTLED decision; the "models improve, the configuration carries across" point recorded as a Results-level claim with R7.3 as its home and a one-clause R0 echo |
| 3 — information into tables, coverage over polish | `docs/paper/results-outline.md` § D20 | new SETTLED decision, named as the standard against which D5, D7, D11, and D13 are executed |
| 4 — fix the drifted and unanchored claims | `docs/paper/results-draft.md` § Changelog 2026-09-12; this report § 1 | executed, with a 19-row before→after table in the draft's changelog |
| 5 — the stride/geometry block | `docs/paper/results-outline.md` § D21 and § R1b; `docs/paper/results-draft.md` § R1b | new SETTLED decision plus the block itself |
| 6 — figures and tables | `docs/paper/results-outline.md` § D22 and § Figures and tables | new SETTLED decision plus the per-block plan |
| 7 — the signing timestamp is real | `docs/paper/results-draft.md` § R4 draft note | note; no number moved (§ 1.3) |
| all seven, with status | `docs/paper/results-claims-inventory-2026-09-12.md` § Rulings 2026-09-12 | new section at the top of the inventory, with what was *not* ruled on listed explicitly |
| headline only | `docs/paper/manuscript-skeleton-isprs.md` § 5 Results | "Headline ruling (PI, 2026-09-12)" paragraph; D-1 to D-5 untouched and explicitly not re-opened |

**The headline numbers as re-read for D19**, since they are the ones a
reader will check first:

| claim | value | anchor |
|---|---|---|
| all-3.7 text stack, GS screen frame | F1@20 m **0.9265** | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md` rank table row 2, "committed F1@20" column 0.9265 |
| the same cell on the Era-2 board frame | **0.9190**, **Tier 1**, rank 2 of 79 | same table, "F1@20 (board frame)" column; `Δ frame` −0.0075 |
| all-3.7 stack at deployment, r2 @ 50 m | carried **0.8827** (T2), oracle **0.8871** (T1) | `results/55map-final-board-r2-2026-09-06/final-board-50m.md` rows 3 and 1; independently in `results/uplift-supplement/conditions.csv`, `arm2-n5-carried-p0.80-k5-r2-gt` F1 0.8827 and `arm2-n5-oracle-p0.95-k5-r2-gt` F1 0.8871 |
| Gemini 3 calibrated result, retained not headlined | GS 0.890 / MCC 0.790; deployment carry-forward 0.8162 | `results/run-analyses.json` → `unswept-pools-completeness`, `tile-level-f1`; `results/55map-leaderboard/55map-leaderboard-50m-r2.md:11` |

**Note on the ruling's wording.** Ruling 2 gives "GS F1 0.9265, Tier 1 on
the Era-2 board" as one clause. Those are two frames: 0.9265 is the
screen's committed evaluation on the 791-candidate union, and the cell's
board-frame value is 0.9190, which is what carries the Tier-1 claim. Both
are recorded, each with its frame named, because conflating them is the
error the R7.3 drafting already had to avoid once.

---

## 4. Ruling 5 — § R1b, the GS stride/geometry block

Commit `b6db0f6c6`. **Twenty-three anchored claims**, R1b-01 to R1b-23,
in `docs/paper/results-outline.md` § R1b. `results-draft.md` carries a
heading and a `[BLOCK PENDING]` pointer only — no prose, per ruling 3.

**Numbering.** Proposed and taken as **R1b**, between R1 and R2. The
alternative — inserting a new R2 and shifting R2–R9 up — would have
invalidated every `§ Rn` cross-reference in the draft, the outline, the
inventory, the ISPRS skeleton, and the register's `paper_section` values.
R1b is the cheap choice and the brief allowed for it.

**Sources drawn on**, all re-read this session:

| source | what it supplied |
|---|---|
| `results/grid-2026-08-18/findings.md` | the 2 × 2 design and spend (`:10-22,215`), the single-pass contrasts (`:77-81`), the corroboration mechanism (`:101-117`), the consensus-only board (`:133-140`), the K ladder and the passes-versus-overlap verdict (`:160-185`), the post-verifier board (`:337-345`), the like-for-like baseline table (`:351-366,368-375`), the verifier-gain and mechanism passage (`:347-349,376-388`), the overlap-survives passage (`:389-397`), the pure-verifier ceiling (`:399-404`), the selection caveat (`:384-388`) |
| `results/stride-2026-08-25/findings.md` | the three questions answered (`:44-70`), the cost frontier (`:72-81`), the 13-cell tiered board (`:144-146`), the k-curves note (`:147-148`), the exact winner ladder (`:149-163`) |
| `results/stride-2026-08-25/plateau_analyses.json` | `k_curves` — the GS ladder that selected § R7.2's carried points: `g384_ov128` `best_k` 8, `k_within_0p005` [6,7,8,9] at `prob_t` 0.15; `g384_ov192` `best_k` 10, single-point top. Also `winner_ladder_exact` |
| register `grid-tilesize-overlap-2026-08-18` | the consensus-only board values and the two overturned priors; **unsigned** |
| register `grid-postverifier-2026-08-18` | the post-verifier board, both settled questions, the complements-not-substitutes finding, the 2026-08-24 audit revision that corrected the pre/post framing; **unsigned** |
| register `h13-overlap-2026-08-18` | H13's prediction split, the arm values, the edge-mound subgroup, the negative cost-efficiency slope, and the registered cost multiplier's 2× versus 2.99× error; **unsigned** |
| register `stride-plateau-2026-08-25` | the plateau-not-winner verdict; signed 2026-08-28T12:16:45Z |
| register `stride-winner-ladder-exact-2026-08-25` | the exact rungs N = 1/3/5 and the $2.64 N = 3 reading; signed 2026-08-28T12:16:45Z |
| Obs 435, `docs/notes/working-notes.md:28698` | the nine-cell board, the iso-stride contrasts, the interior optimum, the cost reading |
| Obs 436, `docs/notes/working-notes.md:28878` | **used sparingly and deliberately**: its own epistemic-status header declares §§ 1–2 an ideas registry, "candidate directions: PI-endorsed for recording, not commitments", carrying "no evidentiary weight at all". Only its settled § 3 ceiling attribution informed the block, and no claim rests on it |
| Obs 437, `docs/notes/working-notes.md:29072` | the deployment hand-off at R1b-23 only; the leg itself is § R7.2's |
| register `stride55-*-2026-08-27` (three rows) | R1b-23's hand-off figures; all signed 2026-08-28 |

**Two gaps closed.** § R7.2's "(§ R1, Obs 435)" pointed at a section that
does not contain the geometry grid, and now reads "(§ R1b, Obs 435)". More
substantively, R1b-18 anchors the GS k-curves, so a reader can now verify
the claim that § R7.2's carried points were selected on GS and not on the
deployment sweeps — the block's central discipline claim, previously
uncheckable. § R7.2's carried-point sentence gains a clause to that effect.

---

## 5. Ruling 6 — the figures and tables plan

Commit `845a8f5d1`. `docs/paper/results-outline.md` § Figures and tables:
one row per Results block (R0, R1, R1b, R2, R3, R4, R5, R6, seam, R7.1,
R7.2, R7.3, R8, R9), each naming the carrier and either the existing
artefact or "to be made", plus a priority order. No figure was made and no
prose was cut.

**A finding worth the PI's attention.** The inventory concluded that "no
paper figure has been made", on the evidence that `docs/paper/figures/`
holds only `review-app-examples/`. That is true of that directory, but
`git ls-files results/ | grep '\.png$'` returns about a hundred committed
figures, and three of them serve the ISPRS skeleton's exhibits directly
while being referenced nowhere in the draft:

| artefact | serves | generated by |
|---|---|---|
| `results/verifier-robustness/pareto/pareto_v2.png` | exhibit (ii), the cost/F1 frontier | `scripts/build_pareto_v2.py:167` |
| `results/55map-final-board-r2-2026-09-06/significance-groups.png` | exhibit (iii), the 35-cell dot-and-interval plot | `scripts/final_board_build.py:520` |
| `results/gs-fp-classification/figures/cross_corpus_comparison.png` | the error-mode comparison | — |

Also unused and relevant: `results/double-miss-crops-2026-09-06/contact-sheet.png`
(the double-miss cases § R8 counts, as images) and
`results/student-gt-fn-rate-analysis*/figures/` (the reference's own
omission structure). So the exhibits gap is **selection and adaptation**,
not creation from nothing.

**Tally**: 3 figures and 1 table exist and are unused; 4 figures and 7
tables are to be made, all from committed numbers at $0 compute. The
priority order is led by **R5's D11 summary table** — settled since
Session 133, still absent, and the single change that saves the most
words.

---

## 6. What did NOT change

- **No tier, tie set, or admissible-set membership**, on any board.
- **No registration status, hypothesis verdict, or family-FDR p-value.**
- **No headline point estimate.** The Gemini 3 headline (0.890 / 0.790)
  and the deployment carry-forward (0.8162) are unchanged as *values*;
  ruling 2 changes which number the paper leads with, not what any number
  is.
- **§§ R3 and R6** — untouched throughout, reserved for the parallel
  K-ladder job (`planning/k-ladder-review-2026-09-11.md`), which will add
  the pass-count ladder. R1b explicitly excludes the pass-count ladder as
  a *cost* object for that reason.
- **The R6 Pareto table's min6 row** at 0.8784 — the true-merge cell, and
  already correct; only § R5's *pairing* of 0.8784 with the stand-in's
  p-value was wrong.
- **The inventory's claim rows, counts, and anchors** — they are the
  evidence the rulings were taken on, and are left exactly as published.
  Only a rulings section and a changelog entry were added.
- **D-1 to D-5 in the ISPRS skeleton** — deferred by the PI on 2026-09-10
  and not re-opened; only § 5's headline statement was added.
- **No results artefact was edited**, so the two stale "remains UNSIGNED"
  lines in the Era-2 board README (`:200`, `:248`) still stand alongside
  its own "Signed" entry. That is the one loose end this pass leaves.

## 7. Left undone, for the PI

1. **The Era-2 board README's self-contradiction** (§ 1.3) — a one-line
   fix in two places, in a results artefact rather than a paper document.
2. **§ R4-15's "the study headline" framing.** Ruling 2 settles which
   number the paper leads with; the draft's prose still calls 0.890 /
   0.790 "the study headline" and never says which number the paper
   headlines. That is a prose re-framing, not a number fix, and ruling 3
   sends prose to the re-draft — so it is recorded at D19 and left for it.
3. **The five unsigned register rows** the whole of § R7.3 rests on, plus
   the three unsigned rows § R1b rests on — eight rows outside the
   `manually_verified_at` discipline every other section's rows observe.
4. **The four remaining `[DRAFT NOTE]` decisions** in the draft's own
   markers, and the per-block word allocation: ruling 3 sets the method
   for hitting 2,200 words but not the split across eleven blocks (now
   twelve, with R1b).
5. **Obs 447's obligation** on §§ R2 and R4 — reframe "text beats image"
   as Gemini-3-specific. The register row states it as an obligation on
   the paper; it is one clause in each section and was not in this brief.

---

## Changelog

### 2026-09-12 — Original publication

Execution of the PI's seven Results rulings of 2026-09-12, taken on the
evidence of `docs/paper/results-claims-inventory-2026-09-12.md`. Sixteen
numbers changed in `docs/paper/results-draft.md` (§ 1), twelve 55-map
figures swept for reference r2 with six re-pointed and five marked
`[REF: r1]` (§ 2), the rulings recorded in the outline, the inventory, and
the ISPRS skeleton (§ 3), a twenty-three-claim § R1b added as an outline
(§ 4), and a per-block figures-and-tables plan added (§ 5). Every anchor
was re-read at source before its edit and every one reproduced the
inventory's value, so no claim had to be stopped on. US$0 API, no compute.
Commits `0b9caf33b`, `a6ac82e0d`, `269fb8d29`, `b6db0f6c6`, `845a8f5d1`,
and the commit that lands this report, which also tightens eleven
line-anchor spans in § R1b of the outline to the exact first and last
lines of the passages they cite — the values were already correct, the
ranges were approximate.
