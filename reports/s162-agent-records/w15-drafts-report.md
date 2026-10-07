# W1.5 for W2.7: drafted floor edits, report (2026-10-07)

Branch `w15-floors-drafts` (from `origin/main` at `443ae9877`, fast-forwarded
to `76e1af87a` to pick up Run A and § 6c), pushed, not merged.

| Commit | Subject |
|---|---|
| `0d221c6f6` | docs(paper): draft W2.7 floor edits for PI review |
| `607753e3d` | docs(paper): annotate claims inventory with floors |
| `5074571ae` | docs(planning): draft D9 floor notes, 55-map rows |
| `99d587041` | docs(paper): split long W2.7 draft sentences |

Abbreviations: **REP** = `reports/w27-replicate-floors-2026-10-06.md`;
**RS** = `reports/w27-replicate-floors-2026-10-06-scripts/floors-v2/results/rescreen.csv`;
**FB** = `results/55map-final-board-r2-2026-09-06/final_board_50m.json` (`cells`,
`pairwise`); **LB8** = `results/55map-leaderboard/55map_leaderboard_50m_r2.json`;
**REG** = `results/passes-manifest.json` `timestamps`; **RA** = `results/run-analyses.json`.
All were re-read in this session.

## `docs/paper/results-draft.md` (every edit marked `[DRAFT NOTE, W2.7, 2026-10-07: …]`)

| # | Site | Before → after (one line) | Numbers and their source |
|---|---|---|---|
| 1 | § R0, new paragraph and Table [N+1] | none → what the tile-swap test cannot see; D45/D46; D48's seven-day rule; Obs 497; the floors table | rejection 11–24 % (REP § 6); 55-map within 0.007 / 0.006–0.010 / 0.008–0.010, image 0.017–0.021 (REP § 6b); nested 0.002–0.007 (RS); cross 0.010–0.018 and 0.004–0.007 (REP § 7.2); GS 0.034 / 0.030, consensus 0.019–0.058 (REP § 3); GS cross 0.03–0.07 on three of six configurations (REP § 4); Obs 497 (`docs/notes/working-notes.md`) |
| 2 | § R6, the uplift (R6-12a/b) | "closes about half … significantly below … a priced trade rather than a tie" → ten passes from two executions; +0.0170 clears the floor but is confounded with date; −0.0108 is inside it, so "half" and "trade or tie" are open | r2 +0.0172 / −0.0106, BH 0.021 (LB8); floor 0.0117, ratios 1.48 / 0.91 (RS); 54 days, 06-11 (REG); 0.018–0.030 proposer-only (REP § 4); 0.003–0.006 through the verifier (REP § 6). R6-12a's wording was added beyond the brief, from REP § 7.2's own verdict. Text figures stay on the standardised vintage. |
| 3 | § R7.1 table | five columns → plus "run dates, 2026 (proposer; verifier)" and a note (‡ = 06-06 vote-3 legs) | REG; TM and IM main verifier legs from their post-run reports (line 6 of each) |
| 4 | § R7.1 lesson (i) (R7.1-05/08/09) | threshold contrasts without dates → date mix named; Run A's one-date reading; R7.1-09a's "pending Run A" note replaced with the settled result, per the coordinator | 06-06, 40–49 days (REG); T03 +0.0092 → +0.0084, p = 0.0013; TM +0.0275 → +0.0264; 4-of-5 shifts +0.0021 / +0.0020, p = 0.36 / 0.38 (REP § 6c); TM June +0.0264 (REP § 6a); floor 0.0069, upper 0.0111, ratio 1.2 (RS; REP § 6c); "at most about 0.002" (REP §§ 6a, 6c) |
| 5 | § R7.2, P5 decomposition (R7.2-11/12) | stated without a chain, "the geometry found few additional mounds" → canonical as before; on r2 +0.0336 = +0.0237 + 0.0161 − 0.0062, a difference between runs, not geometry alone | FB pairwise (+0.033570, +0.023715, +0.016082 p = 0.0001, −0.006227 p = 0.0033); canonical and "0.010 / 0.03" (`results/stride55-2026-08-27/findings.md` § "The P5 overshoot, decomposed"); floor verdict REP § 7.2 |
| 6 | § R7.2, P6 (R7.2-13a) | "B beats A" unqualified → carried primaries narrow (at the upper bound); oracles and N = 5 carry it | floor 0.0072, upper 0.0106 (RS); r2 −0.0106 / −0.0141 / −0.0120 (FB) |
| 7 | § R7.2, R7.2-15 | "although its sign held at every rung tested" → held at N = 3, 5, 10; reversed at N = 1 | A-N1-oracle 0.8227 vs B-N1-oracle 0.8013, +0.021399, p < 0.0001; N = 3 −0.0186 / −0.0170 (FB); N = 1 floor 0.008–0.010 (REP § 6b) |
| 8 | § R7.2, P7 (R7.2-16b) | "small BH-significant residue … saturation is real but not complete" → inside the nested floor, no evidence the tenth pass helps | r2 +0.0036 BH 0.0096, +0.0043 BH 0.0038 (FB); floors 0.0069 / 0.0058, uppers 0.0122 / 0.0091 (RS) |
| 9 | § R7.2 family table | six columns → plus a run-dates column and a note (A's main leg bounded by its 2026-08-26T21:14 cleanup; the fourth cell's seven rounds) | REG; `results/gemini37-55map-2026-08-31/findings.md` changelog 2026-09-01 (04:07 UTC). A's main-leg start is unsourced, marked as such in the draft note. |
| 10 | § R7.2, R7.2-30 | B "above every incumbent cell" → B N = 5 carried above T03's oracle by 0.010, inside the cross-date floor; N = 10 oracle clears it (at the N = 5 pair's upper bound) | +0.010441 p = 0.0177, +0.016082 (FB); floor 0.0106, upper 0.016 (RS) |
| 11 | § R7.2, R7.2-31 | "highest tile-MCC among Gemini 3 cells (0.711)" → among carried and as-shipped cells; two oracle cells exceed it | MCC 0.7110, 0.7128, 0.7123 (FB cells) |
| 12 | § R7.2, R7.2-32a | "above its own N = 10 carried point" → "equals" (+0.0006, p = 0.72, inside 0.0059) | FB +0.000586, p = 0.7161; RS 0.0059 |
| 13 | § R7.2, chain sentence (R7.2-35) | "no verdict depends on the chain" → true for A versus B; the incumbent's cells move (0.8152 → 0.8162, 0.8476 → 0.8399) | stride findings (0.8152, 0.8476); FB cells |
| 14 | § R7.3, R7.3-06b | "both proposer-axis contrasts are not" → both tests reported; +0.0099 BH 0.024, 1.4 times its D48 floor; "lives mostly in the verifier seat" (also "Because most of the family gain …" in the next paragraph) | FB +0.009905, p = 0.0198, BH 0.023704; +0.004762, p = 0.2723; RS within parts 0.0072 / 0.0063. "Mostly" changes the Obs 444 synthesis and is flagged for a PI ruling. |
| 15 | § R7.3, R7.3-07 | "a tax of only +0.0043" → "a small tax … small but real", twice its nested floor | adjusted p 0.000162 (RA `gemini37-55map-gridboard-2026-08-31`); r2 +0.0044 (FB); floor 0.0020, upper 0.0033 (RS) |
| 16 | § R7.3, R7.3-18b | "does not replicate for arm 1 (+0.0076 … significant)" → above the point floor, inside its upper bound | adjusted p 0.000162 (RA); 0.0053 / 0.0127 (RS) |
| 17 | § R7.3, R7.3-19 | one 3.7 pass above the incumbent at its rung oracle → plus r2 +0.0107, 1.9 times its D48 floor | FB 0.861042 vs 0.850318, p = 0.0125, BH 0.015367; RS 0.0055 |
| 18 | Banner and Changelog | → new "Last revised" 2026-10-07 and the entry "2026-10-07 — Drafted 2026-10-07 for PI review (W1.5, W2.7); not finalised" | — |

Not edited, though REP § 7 has verdicts on them: R7.1-12/15 (image MCC lead,
"stands on F1 reasoning only"), R7.3-01/21 (G1 "fired" on p = 0.17), R7.3-22/23
(modality reversal), R4-24, R5-10b and R2-09. They were outside this brief.

## `docs/paper/results-claims-inventory-2026-09-12.md`

Eighteen rows gain a dated `[2026-10-07, W2.7 …]` note matching the edits
above: R6-12, R7.1-05, -06, -08, -09, R7.2-11, -12, -13, -15, -16, -30, -31,
-32, -35, R7.3-06, -07, -18 and -19 (the note on R7.1-06 replaces "—"). R7.2-31
and R7.2-35 are recorded as **missed DRIFTED claims**; as on 2026-10-04 the
census is left as published and no status changes. A new banner and a
changelog entry follow the file's convention. The new § R0 paragraph and the
§ R7.2 date column are noted as not yet inventoried.

## `planning/d9-notes-55map-floors-draft-2026-10-07.md` (new)

Six D9 signature-note drafts, for the PI's approval (with an `<APPROVED_AT>`
placeholder). Nothing was written to `results/run-analyses.json`.

1. `55map-final-board-r2-2026-09-06`: the floors, the k3 cells' date mix and
   Run A, the run dates, and the readings that change.
2. `55map-r2-leaderboard-50m`: the date mix of T03-k3, TH7-k3 and TM-k3; Run A;
   the uplift's two executions.
3. `stride55-sweep-oracle-2026-08-27`: P6 is narrow at the primaries; the +0.0324
   tax and the decomposition depend on the chain.
4. `stride55-ladder-2026-08-27`: "B's N=5 ABOVE N=10" is a tie; the oracle
   residue is inside its nested floor.
5. `gemini37-55map-grid-2026-08-31`: the proposer-axis null depends on the test;
   "mostly" (carries a draft note tying it to the PI's ruling on the Results wording).
6. `gemini37-55map-gridboard-2026-08-31`: the arm 2 tax is real; arm 1's
   N3→N5 step is narrow; ARM2-N1-oracle clears under D48.

Screened with no note proposed (eight rows): `stride55-a5-vs-b5-2026-08-27`
(stands, 1.7 times its floor); `55map-r2-leaderboard-mcc-50m` (no MCC floor);
`55map-final-board-2026-08-27` (two of its claims were not screened by REP);
the three image-campaign rows (their K-step claims are judged against verifier
drift only, and no K = 3 or K = 5 image floor exists, so they need a screen
first); `uplift-supplement-flatten` and `verifier-uplift-pairing` (not
run-to-run contrasts).

## Checks

- `npx markdownlint-cli2`: 0 errors on all three files.
- Prose exit checks on the added body text (DRAFT NOTEs, banner and changelog
  excluded): about 1,800 words; em-dashes 0; boosters 0; "not X but Y" 0;
  announcement colons 0 after the prose pass; the remaining semicolons sit
  inside parenthetical citations; no runs of short sentences. Mean sentence
  length about 29 words, above the register's 21–24 target and inside its
  ±10 tolerance, because most sentences carry their figures in parentheses.
- Points for the PI: (a) the "mostly in the verifier seat" synthesis (edit 14
  and D9 note 5); (b) A's main verifier-leg date is bounded, not sourced; (c)
  B's N = 10 oracle over T03's oracle (+0.0161) sits at the upper bound
  re-screened for the N = 5 pair (0.016), although REP § 7.2 counts it as
  clearing; (d) the image-campaign rows have not been screened against any
  floor.
