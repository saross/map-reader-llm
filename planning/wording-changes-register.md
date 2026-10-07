# Wording-changes register

> **Last revised**: 2026-10-07 (probe follow-up cited, Session 163). See
> [§ Changelog](#changelog) for revision history.

**Purpose.** One list of every wording change the paper drafts and the
records are known to need, so none is lost before the Results re-draft. It
covers `docs/paper/` (Results draft, outline, skeleton, discussion outline,
claims inventory), register prose (`results/run-analyses.json` outcomes and
notes), findings documents, and planning cards that the paper cites. It was
opened at the Principal Investigator's (PI's) request on 2026-10-07.

**How to use it.** Add a row when a change is identified, with its source.
Never delete a row: mark it **DONE** with the date and commit, or **DROPPED**
with the reason. Status values: **OPEN** (to draft), **NEEDS RULING** (the
PI decides the wording or whether to change it), **DRAFTED** (written on a
branch, awaiting merge), **DONE**. Anchors are `file:line` as read on
2026-10-07; rows taken from an agent report name that report.

## A. Temperature (Google's notice of 2026-10-07 and the probe)

Sources: `reports/google-temperature-notice-2026-10-07.md` (§ 2 claim table,
§ 7 questions), `planning/temperature-probe-2026-10-07.md` §§ 7 and 8.5. Facts now
established: Gemini 3.6 Flash and later apply the model default whatever is
sent (Google; the probe confirms it for 3.7, and its pre-registered follow-up
finds no residual effect, a residual up to about 0.02 in mean |Δp| not
excluded; § 7's exploratory residual traces to one batch job); the default is 1.0 for `gemini-3.7-flash`, `gemini-3.8-flash` and
`gemini-3-flash-preview` (`outputs/temperature-probe-2026-10-07/models-get.json`).

| ID | Where | What must change | Status |
|---|---|---|---|
| T1 | Methods (model and sampling description) | State that 3.7 and 3.8 requests carried T 0.7 (proposer) and T 0.0 (verifier), that the provider applies the model default (1.0) from Gemini 3.6 Flash on, and that temperature is therefore part of the unseparated "model package" with thinking level (as `results/gemini37-image-55map-2026-09-13/findings.md:325-327` already does for thinking). Cite the probe. | OPEN |
| T2 | D19 carry claim: `docs/paper/results-outline.md:197-199`, `:556-561`; `docs/paper/manuscript-skeleton-isprs.md:76-78`; `docs/paper/discussion-outline.md:272-273` | "The calibrated configuration carries across model versions" — temperature was part of that configuration and never reached 3.7 or 3.8. Restate as the configuration minus temperature, or as transfer at the model's default sampling. | NEEDS RULING |
| T3 | R7.3-22/23: `docs/paper/results-draft.md:860-864` ("supports parity rather than inversion", `:862`), echoes at `:220-224` and `:386-388` | The gap change survives; whether the 3.7 gap inverts cannot be read while Gemini 3 ran at 0.7 and 3.7 at its default, because the Gemini 3 image track is temperature-sensitive (+0.013 to +0.053 F1 for 0.7 over 1.0 through the verifier). Await Run B (and the matched Gemini 3 pair, if approved). | NEEDS RULING |
| T4 | Small cross-generation claims of the size of the temperature bound: R7.3-04, R7.3-06 (proposer axis), R7.3-19, the GS swap37 +0.0126, R7.3-12 (3.8 +0.0119), the fourth-cell GS leg, the 3.7 image verifier swap, the image 55-map verifier MCC gains (report § 4.3 rows A2, A3, A6, B3, B7, B9–B11) | Mark as within the temperature analogy's bound, beside the replicate floors of W2.7 § 7, or leave as stated with T1's Methods caveat. | NEEDS RULING |
| T5 | § R4: "the text advantage of § R2 belongs to the Gemini 3 family, not to the task (Obs 447)" (`docs/paper/results-draft.md`, the sentence repaired in D5) | Carries T3's caveat: the family contrast is not temperature-matched. Follow T3's ruling. | OPEN |
| T6 | Discussion: every recommendation about settings | From Gemini 3.6 Flash on only the default temperature (1.0) is available, and upcoming models will reject a `temperature` field. Say what that means for practitioners: tuning moves to thinking level, pass count, vote threshold and verifier probability threshold; a verifier is no longer near-deterministic at "T 0" (3.7 reproduced its own probabilities on 64 % of candidates against Gemini 3's 80 %), which may favour more than one verifier pass; the project's Gemini 3 image track lost F1 from 0.7 to 1.0; cost may change as a result. (PI, 2026-10-07.) | OPEN |
| T7 | Run B gate: `planning/gate-2026-10-07-verifier-date-and-bridge.md:66-67` ("re-run exactly as it was (same model, thinking, temperature …)") | Add that the 3.7 arms' temperature is nominal (default 1.0 applied). | OPEN |
| T8 | Register rows and metas of every 3.7 and 3.8 leg (`configuration.temperature` 0.7 or 0.0) | A register-level note that the recorded value is the value sent, not the value applied. No metadata rewrite. | OPEN |
| T9 | R7.3-11, 3.8 against 3.7 on one union (`docs/paper/results-draft.md:811-817`) | Optional precision: both verifiers ran at the same default (1.0, now confirmed), so the tie is temperature-matched. | OPEN |

## B. § R4, the Era-2 gold-standard board

| ID | Where | What must change | Status |
|---|---|---|---|
| R1 | § R4 board figures, `docs/paper/results-draft.md:373-389` and the table at `:1304` ("79 cells … 3,081 pairs … seven tiers") | The board was rebuilt on 2026-09-14 and re-signed on 2026-09-16 (register row `gs-era2-verified-board-2026-09-10`): 153 cells admitted, 150 tiered, 11,175 pairs, 14 tiers. Refresh § R4 to the signed board. | OPEN |
| R2 | R4-21, R4-23, R4-24 (`docs/paper/results-claims-inventory-2026-09-12.md:571-574`) | (i) Refresh to the signed board: the best sweep optimum (`pv-high-text-t0.3-n5-opmax`, 0.8873) is now rank 12, Tier 2; lowest Tier-1 cell against it +0.0195 (p = 0.178, BH 0.220); top cell against it +0.0359 (p = 0.0158, BH 0.0234) (`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json`). (ii) Name the temperatures: the comparator is Gemini 3 at its best tested proposer temperature (0.3, of 0.0/0.3/0.7/1.0), the 3.7 and 3.8 cells ran at the default 1.0, so the comparison favours Gemini 3 if anything. (iii) Add the matched supplement against the best Gemini 3 T 1.0 cell (`pv-high-text-t1.0-n10-opmax`, 0.8804, rank 17, Tier 3): top Tier-1 cell +0.0429 (p = 0.0071, BH 0.0112); lowest Tier-1 cell +0.0264 (p = 0.082, BH 0.108, not significant). R4-21's "every Gemini 3 cell in Tier 2 or below" holds at every temperature (all 24 T 1.0 cells are Tier 3 or below). Caveat: no comparison here is date-matched. | OPEN |
| R3 | R4-21 naming (`results-claims-inventory-2026-09-12.md:571`) | The "best committed incumbent" `verifier-robustness::verified-384-16of30-t0-3-n5-opmax` carries `-opmax` in its id, and its `t0-3` is the verifier's consensus temperature, not the proposer's (the proposer is HIGH text at 0.7). Reword so neither reads as a sweep optimum or a T 0.3 proposer. | OPEN |

## C. The scorer's frame asymmetry (blast radius)

Source: `reports/frames-blast-radius-2026-10-07.md` (agent record, spot-checked
on filing) and `reports/k-ladder-frames-2026-10-07.md`. The PI's choice
between the scorer fix and per-analysis clipping, and two prior rulings
(sheet attribution; the 3.7 ladder's mixed universes), are pending.

| ID | Where | What must change | Status |
|---|---|---|---|
| F1 | 3.7 GS K-ladder: `results/k-ladder-2026-09-12/findings.md:602` ("0.8495 → 0.9068 (+0.0573)") and any draft citation | Scoped like references: K = 1 0.8747, K = 3 0.9135, so the K = 1 → 10 gain is +0.0320 and K = 3 sits above K = 10. Do not cite +0.0573 or the monotone shape until the universe ruling. | NEEDS RULING |
| F2 | "Their F1 is unaffected/sound": `reports/tile-mcc-geometric-join-2026-09-12.md:316-319`; `scripts/build_k_ladder_phase2_tables.py:222-227`; claims inventory R3-13 (`:461`) | Wrong for the 3.7 K = 1 and K = 3 rungs; correct after the ruling. | OPEN |
| F3 | Signed row `null-exemplar-sensitivity-2026-09-13` ("no cell's F1@20 moves more than 0.0074") | The 0.0074 cell is this defect; scoped, the maximum is 0.0068. Direction stands. Needs a D9 note. | OPEN |
| F4 | R3-14, "the verifier absorbs 40.6 %" (§ 8.6) | Sheet re-keying (tier E, h13) understates the verified cells; about 64 % provisionally. Await the sheet-attribution ruling. | NEEDS RULING |
| F5 | Tier E "like for like": `results/k-ladder-2026-09-12/findings.md:1337`; `reports/k-ladder-closeout-deltas-2026-09-12.md:541-542` | Half true: evaluations drop out-of-frame candidates through null re-keyed `source_tile`, sweeps count them. | OPEN |
| F6 | Frame-agreement wording (`reports/k-ladder-frames-2026-10-07.md` § 3A sites); "twenty of twenty-one" (§ 3B, two sites); tier E `pre_launch_audit.md:232-238` Warning 3 | "Agree" → "agree by construction"; correct the mis-citation and the warning's frame pair and percentage. | OPEN |

## D. Floors and W2.7 (branch `w15-floors-drafts`)

| ID | Where | What must change | Status |
|---|---|---|---|
| D1 | R7.3-06b and R7.3-19, eleven sites in three files | D48's caveat "assuming little proposer drift within a week". | DRAFTED, `5b549646f` (branch) |
| D2 | R7.3-06b draft note ("'mostly' … needs the PI's ruling") | The PI agreed "mostly in the verifier seat" at S162 close (`planning/paper-writeup-continuity.md:65`); update the note to record the ruling. | OPEN |
| D3 | Oracle-against-oracle differences (e.g. B's N = 10 oracle over T03's oracle, +0.0161) | Word descriptively as post-hoc maxima; make configuration claims on carried points (S162 recommendation (b)). | NEEDS RULING |
| D4 | D48's definition sites: `docs/paper/results-draft.md` § R0 floor table (branch, `:146-152`); D9 notes (branch, `:24`, `:52`) | Whether D48's proposer-drift assumption is stated where the rule is defined, not only at R7.3-06b/19. | NEEDS RULING |
| D5 | § R4 sentence spliced into "0.9068" | Repaired. | DRAFTED, `c3730dcee` (branch) |
| D6 | Claims-inventory census | Freeze as the 2026-09-12 snapshot with dated notes, or re-classify the 18 annotated rows and recount. | NEEDS RULING |

## E. Bookkeeping found on the way (not prose, kept here so it is not lost)

| ID | Where | What must change | Status |
|---|---|---|---|
| K1 | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md:3` | Banner says "awaiting the PI's re-signature"; the register records the re-signature of 2026-09-16. | OPEN |
| K2 | Register `_note` of `gemini37-image-55map-2026-09-13`, `gemini3-image-55map-2026-09-16`, `gemini37-image-55map-k5-replicate-2x2-2026-09-20` | Each says "UNSIGNED"; each `signature` is signed (2026-09-20, 2026-09-20, 2026-09-21). | OPEN |
| K3 | `results/retest/phase2b/analysis_summary.md:71` ("Tile size: 384 px") | The production summary (`results/retest/retest-production-summary.md:34`) and post-run report say 512 px; establish which and correct. | OPEN |
| K4 | `data/pricing/gemini-rate-card.json`, `gemini-3.7-flash` batch `input_cached` 0.0375 | September batch invoices bill 3.7 cache reads at USD 0.075/M (`planning/cost-accounting-fix-plan-2026-09-21.md` § 8 item 10); the register will under-price Run B's 3.7 image arm. | OPEN |

## Changelog

### 2026-10-07 — Probe follow-up (Session 163)

Section A's preamble now cites the follow-up (`planning/temperature-probe-2026-10-07.md`
§ 8.5, `36497fec2`): no residual temperature effect on 3.7. No row changed.

### 2026-10-07 — Original publication (Session 163)

Opened at the PI's request with the changes identified in Sessions 162–163:
the temperature notice and probe, the § R4 board refresh, the frames blast
radius, the W2.7 floors drafts, and four bookkeeping items.
