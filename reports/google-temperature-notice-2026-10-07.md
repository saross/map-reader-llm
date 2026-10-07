# Google's sampling-parameter notice: claims at risk, the bound, and the request builders

> **Last revised**: 2026-10-07 (original publication, Session 163). See
> [§ Changelog](#changelog) for revision history.

**Status: FOR THE PI.** An agent's offline, read-only record (Session 163),
spot-checked by the main session before filing: the grid's temperature
pairs (`tiering_20m.json`), the 3.7 verifier's agreement table, the
text-MIN pools' date and path confound, and the spliced sentence in
`docs/paper/results-draft.md:386-388` were re-read at source. Added
unchanged below this header.

> Prepared 2026-10-07. Offline and read-only: no model Application Programming Interface (API)
> call, no repository edit. Repository `/home/shawn/Code/map-reader-llm` at `f01ac3043`; all
> paths are repository-relative and every `file:line` anchor was re-read for this report.
> Trigger: `planning/paper-writeup-continuity.md:123-142` (Google states that from Gemini 3.6
> Flash on, temperature, top_p and top_k are held at defaults; unverified by the project).

Conventions. G3 = Gemini 3 Flash (`gemini-3-flash-preview`); 3.7 / 3.8 = `gemini-3.7-flash` /
`gemini-3.8-flash`. "Logged T 0.7" means the request carried 0.7 and the meta records 0.7; under
Google's notice a 3.7/3.8 request ran at the model's (unknown) default instead. Gold standard
(GS); proposer–verifier (PV); Matthews correlation coefficient (MCC); Benjamini–Hochberg (BH);
difference-in-differences (DiD); confidence interval (CI). For temperature contrasts,
Δ = F1(T 0.7) − F1(T 1.0), so a positive Δ favours T 0.7.

## 1. Summary

- **24 claims rows are affected; 16 touch the paper drafts, 8 are internal records** (§ 2). All
  are cross-generation: a G3 seat at a real temperature against a 3.7/3.8 seat at a nominal one.
  The D19 framing claim — "the calibrated configuration carries across model versions"
  (`docs/paper/results-outline.md:197-199`, `:556-561`) — is affected in kind: temperature was a
  component of that configuration and, on Google's account, never reached 3.7 or 3.8.
- **The project already holds the right bound, and it is modality-dependent.** In the
  `pv-diag-384` grid (G3 proposers at T 0.0/0.3/0.7/1.0, all under the G3 verifier at T 0.0, GS
  487-tile frame, 20 m), T 0.7 → 1.0 moves text cells by at most 0.008 F1 at N ≥ 3 (none
  significant) but image cells by +0.013 to +0.053 (three of six BH-significant), and N = 1
  cells by +0.020 to +0.079. A single-pass G3 verifier moved from T 0.0 to 1.0 loses 0.010 F1 and
  0.033 MCC at the carried point (CIs overlap). E43's matched pools are inside that grid: the
  verifier turns E43's consensus Δ of −0.021/−0.034 into +0.003/−0.006 (§ 4).
- **If 3.7 responded to temperature as G3 Flash does and its default were 1.0, every
  cross-generation advantage claimed for 3.7 would be understated, not inflated.** Claims of the
  bound's own size can nonetheless be produced or erased: the proposer axis (+0.0099 to +0.0107,
  R7.3-06), D1 (+0.0056, R7.3-04), the single-pass economy (+0.0107, R7.3-19), the GS
  same-union verifier swap (+0.0126), 3.8 against G3 (+0.0119) and the 55-map image verifier MCC
  gains (+0.016 to +0.025). The headline (+0.027/+0.031), the verifier axis (+0.023/+0.027), I1
  (+0.084/+0.090), the deployment image proposer effect (+0.10 F1) and the calibration shift
  exceed the bound. **R7.3-22's "parity rather than inversion" is the reading most at risk**:
  under the analogy the 3.7 gap would move further negative.
- **No saved model listing records a default temperature.** Run A/B's Stage 0 (2026-10-07)
  printed served/not-served flags only, and only into a session transcript. The 3.6+ default
  remains unverified. Indirect only: the 3.7 verifier logged at T 0.0 agrees with its own
  re-invocation on 63.5 % of probabilities (κ 0.50) against G3 at T 0.0's 81.8 % (κ 0.77),
  which fits sampling above zero but is confounded by thinking level (low against minimal).
- **Every request builder sends a temperature; none sends top_p, top_k or thinking_budget.**
  Defaults when the configuration omits it are inconsistent: 0.1 (detector, batch JSONL, sync
  retry, `5_verify_crops.py`), 0.0 (verifier, `patch_failed_tiles`), 0.7 (consensus verifier)
  (§ 6).

## 2. Affected claims

"Paper" = `docs/paper/results-draft.md`, the claims inventory
`docs/paper/results-claims-inventory-2026-09-12.md`, the outline or the skeleton. "Internal" =
findings documents, register outcomes, planning cards. Every G3 seat named below ran at the
logged value; every 3.7/3.8 seat ran, per Google, at the default.

### 2a. Cross-generation proposer contrasts

| # | Claim (ID) | Where | Compared | Logged T, each side | Claimed effect | Status |
|---|---|---|---|---|---|---|
| A1 | R7.3-01/-02, G1 fired | `results-draft.md:776-782`; inventory `:1005-1006`; register `results/run-analyses.json:2423` | GS screen: 3.7 text proposer (thinking low) vs the G3 text-B anchor (minimal), both under the G3 verifier | 3.7 0.7 vs G3 0.7 (`planning/gemini37-screen-2026-08-28.md:23-25`); verifier 0.0 both | 0.9139 vs 0.8934; +0.0178, p = 0.1697 (register; the draft omits the p, `reports/w27-replicate-floors-2026-10-06.md:585`) | Paper |
| A2 | R7.3-04 (D1) | `results-draft.md:789-793`; inventory `:1008`; `results/gemini37-55map-2026-08-31/findings.md:126` | 55-map arm 1 vs incumbent B N = 5, proposer axis under the G3 verifier | 3.7 0.7 vs G3 0.7 (`results/stride55-2026-08-27/findings.md:276-279`) | +0.0056, p = 0.35 (r2: +0.0048, p = 0.27, `w27…:624`) | Paper |
| A3 | R7.3-06, proposer axis under the 3.7 verifier | `results-draft.md:795-798`; inventory `:1010`; findings `:139` | arm 2 (3.7 pool, K = 5) vs fourth cell (G3 B pool, K = 10), both verified by 3.7 | 3.7 0.7 vs G3 0.7; verifier both nominal 0.0 | +0.0107, per-sheet p = 0.074; r2 tile-swap +0.0099, p = 0.0198, BH 0.024 (`w27…:627`) | Paper |
| A4 | R7.3-08 | `results-draft.md:802-805`; inventory `:1012` | 3.7 union "about 3.5× tighter", recall-led | 3.7 0.7 vs G3 0.7 profile | 12,715 vs ~44,000 candidates; recall 0.855 vs 0.809 | Paper |
| A5 | R7.3-09 | `results-draft.md:805-808`; inventory `:1013` | arm 1 oracle vs incumbent | as A2 | +0.0224 (no test) | Paper |
| A6 | R7.3-19 | `results-draft.md:842-846`; inventory `:1023` | one 3.7 pass under the 3.7 verifier (rung oracle) vs the G3 five-pass incumbent | both seats differ | 0.8563 vs 0.8438; r2 +0.0107, p = 0.0125, BH 0.015 (`w27…:630`) | Paper |
| A7 | R7.3-21 (I1) | `results-draft.md:856-860`; inventory `:1025`; `results/gemini37-image-gs-2026-09-01/findings.md:53` | 3.7 image proposer vs the G3 image anchor (K = 10) | 3.7 0.7 vs G3 0.7 (`planning/gate-2026-10-07-verifier-date-and-bridge.md:76,78`) | +0.0842 (G3 verifier) / +0.0896 (3.7 verifier); no p stated | Paper |
| A8 | R7.3-22/-23, with the § R2 and § R4 echoes | `results-draft.md:220-224`, `:386-388`, `:860-864`; inventory `:1026-1027`; `results/gemini37-image-gs-2026-09-01/findings.md:37-47` | text − image gap, G3 vs 3.7 | G3 gap: both arms 0.7 (real); 3.7 gap: both arms nominal 0.7 | +0.0549 (p = 0.001) → −0.0115 (p = 0.25) and −0.0043 (p = 0.68); change −0.059 to −0.066; read as "parity, not inversion" | Paper |
| A9 | D19 framing: "the calibrated configuration carries across model versions" | `docs/paper/results-outline.md:197-199`, `:556-561`; `docs/paper/manuscript-skeleton-isprs.md:76-78`; `docs/paper/discussion-outline.md:272-273` | the carry-over claim itself | temperature component not transmitted to 3.7/3.8 | qualitative | Paper |
| A10 | Image 2×2 at deployment, T1/T2 (proposer effect) | `results/gemini3-image-55map-2026-09-16/findings.md:58-61` | 3.7 image vs G3 image proposer under each verifier, K = 3 carried | 3.7 0.7 vs G3 0.7 (run_1 metas: `outputs/gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img/run_1/…meta.json`, `outputs/gemini3-image-55map-2026-09-16/g384_ov192_55map_g3img/run_1/…meta.json`) | F1 +0.107 / +0.100; MCC +0.041 / +0.024 (BH p < 0.0001 each) | Internal |
| A11 | 3.7 image K = 3 against `FOURTH-N1-oracle` and `IM-k3` | `results/gemini37-image-55map-2026-09-13/findings.md:55`, `:58` | cross-generation proposer (and, for `IM-k3`, verifier) | as A10 | +0.0848 F1 / +0.0177 MCC; +0.1191 F1 / +0.0538 MCC | Internal |
| A12 | k-ladder: the three ladders whose MCC falls with K are "the three with a Gemini 3.7 component" | `results/k-ladder-2026-09-12/findings.md:511-513` | association of a K-trend with the 3.7 family | — | qualitative | Internal |

### 2b. Verifier-swap contrasts (G3 verifier at T 0.0, real, against 3.7/3.8 logged at T 0.0)

| # | Claim (ID) | Where | Compared | Logged T | Claimed effect | Status |
|---|---|---|---|---|---|---|
| B1 | R7.3-05/-06, verifier axis | `results-draft.md:793-799`; inventory `:1009-1010`; findings `:136-138` | 3.7 vs G3 verifier on the 3.7 pool; and on the G3 pool | G3 0.0 vs 3.7 0.0 (`outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_swap37/run.meta.json` records 0.0) | +0.0270, p = 0.0001; +0.0234, p = 0.0001 | Paper |
| B2 | R7.3-05 diagonal and R7.3-14/-15 (the D19 headline) | `results-draft.md:793`, `:826-834`; inventory `:1018-1019` | all-3.7 stack vs the G3 stack and vs B's N = 10 oracle | both seats | +0.0325, p = 0.0001; +0.0267 carried / +0.0311 oracle on r2 | Paper (headline) |
| B3 | GS swap37, source of the headline 0.9265 | `results/run-analyses.json:2423`; `planning/gemini37-screen-2026-08-28.md:103-111`; quoted at `results-draft.md:814-815`, `results-outline.md:187` | 3.7 vs G3 verifier on the same 791-candidate union | as B1 | +0.0126 over the same union (no test in the register); +0.0304 vs the K = 10 anchor, p = 0.0105 | Paper |
| B4 | R7.3-07 (first half); G2 falsified — "a verifier's operating threshold does not transfer across verifier models" | `results-draft.md:800-802`; inventory `:1011`; register `:2423`; card `:109-111` | probability scale by verifier model | as B1 | mean probability 0.687 vs 0.587 on identical candidates; optimum 0.80–0.95 vs 0.10–0.20 | Paper |
| B5 | R7.3-16 | `results-draft.md:835-838`; inventory `:1020` | fourth cell (G3 pool + 3.7 verifier) holds the board's highest carried tile-MCC | as B1 | 0.726 against the family table's next carried value, 0.711 (`results-draft.md:722`) | Paper |
| B6 | R4-19 to R4-26 and R7.3-20 | `results-draft.md:381-401`, `:847-851`; inventory `:569-576`, `:1024` | Era-2 board: all five Tier-1 cells are 3.7/3.8; vs the best G3 sweep optimum | 3.7/3.8 nominal vs G3 HIGH text **T 0.3** (comparator never matched, even nominally) | lowest Tier-1 +0.0195, p = 0.178, BH 0.244; top cell +0.036, p = 0.016, BH 0.028 (`results-draft.md:393-396`) | Paper |
| B7 | R7.3-12 (3.8 joins Tier 1 among G3 cells); 3.8 vs the carried G3 verifier | `results-draft.md:817-820`; register `:2594` | 3.8 vs G3 verifier on the 791 union | G3 0.0 vs 3.8 0.0 (`…/verify_swap38/run.meta.json`) | Tier 1 at 0.9182; +0.0119, p = 0.0969 | Paper / internal |
| B8 | E4: "threshold insensitivity is a 3.7/3.8-generation property" | register `:2594`; `planning/gemini38-screen-2026-09-04.md:186-191` | flat 3.7/3.8 sweep surfaces vs a peaked G3 surface | as B1 | spread 0.0022 vs 0.0497 | Internal |
| B9 | Fourth-cell GS leg | register `:2560` | 3.7 verifier on the G3 K = 10 pool vs the anchor | as B1 | +0.0179, p = 0.0563; mean probability 0.209 on that pool | Internal |
| B10 | 3.7 image GS, arm 2 vs arm 1 | `results/gemini37-image-gs-2026-09-01/findings.md:21-22` | verifier swap on the 3.7 image pool | as B1 | 0.9308 vs 0.9254 (+0.0054, no test); both values quoted in R7.3-21 | Internal |
| B11 | 3.7 image 55-map P4 and § 4 DiD; G3 image row T3 and T4 | `results/gemini37-image-55map-2026-09-13/findings.md:46`, `:176-188`; `results/gemini3-image-55map-2026-09-16/findings.md:62-65` | the 3.7 verifier seat on image vs text pools | as B1 | P4 MCC +0.0158 (K = 3) / +0.0245 (K = 1); DiD +0.0174 MCC; T3 +0.0103 F1, −0.0013 MCC; T4 +0.0170 MCC (BH p = 0.0052), +0.0071 F1 (0.019) | Internal |
| B12 | Run B gate: arms re-run "exactly as it was (same model, thinking, temperature …)" | `planning/gate-2026-10-07-verifier-date-and-bridge.md:66-67`, `:77-78` | Run B's 3.7 arms | nominal 0.7 / 0.0 | procedural (continuity item (c)) | Internal |

## 3. Unaffected boundary

These compare two seats that both ran 3.7 (or 3.7 and 3.8) and therefore both sat at the
default, so the notice changes their description, not their comparison:

- **R7.3-11**: 3.8 vs 3.7 verifier on the identical union, −0.0007, p = 0.78
  (`results-draft.md:811-817`). Unaffected *provided both models share one default*, which is
  itself unverified.
- **R7.3-12's thinking comparison** (76 against 106 tokens per candidate, `:819-820`) and
  **R7.3-29** (3.7 thinking volume).
- **R7.3-07's second half**: the 3.7 verifier's own carried-to-oracle tax, +0.0043 (nested, one
  leg).
- **R7.3-18a/b**: N = 3 → 5 within each arm (`results-draft.md:839-842`).
- **R7.3-22's two within-3.7 gaps taken singly** (−0.0115 and −0.0043): each pair shares
  proposer conditions and a verifier. Only the *change* from the G3 gap is affected (A8).
- **R7.3-24**: all-3.7 image vs all-3.7 text, +0.0043, p = 0.677 (`:865-867`).
- **3.7 image 55-map P2, P3 and P5** (`results/gemini37-image-55map-2026-09-13/findings.md:44-47`),
  e.g. P3's +0.0351 over the all-3.7 text arm; its replicate legs; every within-arm K step of
  the 3.7 ladders in `results/k-ladder-2026-09-12/findings.md:468-473`; R6-16's 3.7 ladder
  economics.
- **Out of scope by the notice's own terms**: every G3-only contrast; Gemini 3.5 Flash (the
  S113 precedent) and `gemini-3.1-pro-preview`, which predate 3.6 Flash.

## 4. The bound

### 4.1 Measured G3 Flash T 0.7 → T 1.0 differences (proposer)

| Source | Architecture | Model, thinking | Frame, tiles, size | Δ F1 at 20 m (positive favours T 0.7) | Test | Anchor |
|---|---|---|---|---|---|---|
| Phase 2b H7, image track | single pass, K = 3 replicate mean | `gemini-3-flash` resolved to `-preview` (erratum E3; `results/retest/retest-production-summary.md:301`), minimal | Era 1, 340 tiles, 512 px (`…production-summary.md:34`) | means 0.537 [0.489, 0.580] vs 0.527 [0.474, 0.561]; paired +0.014 | p = 0.48 (first run of each condition, `analysis_summary.md:14`) | `results/retest/phase2b/analysis_summary.md:85-86`, `:111` |
| Phase 2b H7, text track | as above | as above | as above | means 0.584 [0.521, 0.636] vs 0.533 [0.432, 0.583]; paired +0.072 | p = 0.0055, BH 0.011 | `…analysis_summary.md:121`, `:123`, `:145` |
| Phase 3a, consensus K = 30 | consensus, best threshold per arm | `gemini-3-flash`, minimal | Era 1, 340 tiles | image 0.6909 vs 0.6803 (+0.0106); text 0.6915 vs 0.6860 (+0.0055) | untested; the first-run image contrast is +0.054, p = 0.0070 | `results/retest/retest-production-summary.md:168-171`, `:280` |
| Phase 3a-HIGH, text | single pass, mean of 30 | G3, high | Era 1 | 0.4248 vs 0.4107 (+0.014) | untested | `…production-summary.md:189-190` |
| E43 matched, 487-tile | consensus, no verifier | G3, minimal, text | Era 2 GS, 487 tiles, 384 px | N = 5: −0.0213; N = 10: −0.0335 (T 1.0 ahead) | p = 0.3352; p = 0.0815 | `results/e43-matched-temperature/findings.md:158`, `:160` |
| E43, same cells, tile-MCC | as above | as above | as above | ΔMCC N = 5 −0.0918; N = 10 −0.0498 | p = 0.0255; p = 0.2114 | `…findings.md:642-643` |
| E43 archived 240-tile leg (the `consensus-384-t1-0` run, `results/run-registry.json:48-49`) | consensus | G3, minimal, text | 240 tiles | matched N: −0.0072 (5-of-5), +0.0090 (10 vs 9 of 10), +0.0393 (29-of-30); +0.0123 at each arm's own optimum | CIs overlap | `…findings.md:39`, `:222`, `:229-231` |
| **PV grid, text, N ≥ 3** | **proposer–verifier**, G3 verifier T 0.0 minimal, each arm at its sweep optimum | G3, minimal and high | Era 2 GS, 487 tiles, 384 px | MIN N3 +0.0078, N5 +0.0025, N10 −0.0055; HIGH N3 −0.0050, N5 −0.0054, N10 −0.0060 | p = 0.60 to 0.84, none significant | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json:140280`, `:150976`, `:149520`, `:124054`, `:153524`, `:147938` |
| **PV grid, text, N = 1** | as above | as above | as above | MIN +0.0340; HIGH +0.0199 | p = 0.0506; 0.3856 | same file `:138810`, `:122052` |
| **PV grid, image, N ≥ 3** | as above | G3, minimal and high, `library_plus-hp` | as above | MIN N3 +0.0312, N5 +0.0349, N10 +0.0453; HIGH N3 +0.0420, N5 +0.0531, N10 +0.0133 | MIN N10 p = 0.0121 (BH 0.018); HIGH N5 p = 0.0056 (BH 0.009); HIGH N3 p = 0.030 (BH 0.043); others p = 0.07–0.48 | same file `:133210`, `:158144`, `:155820`, `:113484`, `:156128`, `:157948` |
| **PV grid, image, N = 1** | as above | as above | as above | MIN +0.0208; HIGH +0.0790 | p = 0.3689; 0.0005 (BH 0.0009) | same file `:131488`, `:111202` |
| PV grid, tile-MCC (untested) | as above | as above | as above | text −0.027 to +0.016; image −0.002 to +0.036 (MCC(0.7) − MCC(1.0)) | — | board `README.md:25`, `:31`, `:36`, `:39`, `:41`, `:45`, `:50`, `:54`, `:92-93`, `:108-109`, `:120`, `:124-126` |

The PV-grid BH values belong to the board's 11,175-pair family (`README.md:5`). Union growth with
temperature (G3 minimal text, 487 tiles, 1-of-N): N = 5 1,593 → 1,926 (+21 %); N = 10 1,953 →
2,472 (+27 %) (`outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7/consensus-n5/voting_summary.json:4`,
`…/text-t1.0/consensus-n5/voting_summary.json:4`, `…/text-t0.7/consensus-n10/voting_summary.json:4`,
`…/text-t1.0/consensus/voting_summary.json:4`).

**Surprise — a date confound inside the PV grid.** Every T 0.7 pool ran 2026-03-22/24 on the
Batch API; every T 1.0 pool ran 2026-04-16/17 in real time (the run_1 metas of the eight pools
under `outputs/h11/pv-diag-384/`; for text MIN also `e43-matched-temperature/findings.md:759-766`).
On this corpus same-request runs 20 days apart differ by 0.037–0.061 single-pass
(`w27…:586`). The same-date check, T 0.3 against T 1.0 (both April, real time), gives:
text N ≥ 3 −0.0082 to +0.0242, none significant; MIN image N ≥ 3 +0.0383 to +0.0486 (N3
p = 0.0054, N10 p = 0.0167); HIGH image N ≥ 3 −0.0030 to +0.0138, none significant
(`tiering_20m.json:138096`, `:149044`, `:149562`, `:121072`, `:146384`, `:147980`, `:130648`,
`:157850`, `:157486`, `:110082`, `:158746`, `:158326`). The MIN-image sensitivity is therefore
real; the HIGH-image 0.7-vs-1.0 gaps may be partly date.

### 4.2 Verifier-temperature evidence (G3 Flash, minimal)

| Source | Regime | Frame | Result | Anchor |
|---|---|---|---|---|
| Verifier-temperature pilot, Stage B | single pass, T 0.0 / 0.5 / 1.0 on the 607-candidate GS 4-of-5 union | Era 2, 487 tiles, 20 m | at (vote 4, prob 0.15): 0.8536 [0.8206, 0.8825] → 0.8645 → 0.8434 [0.8081, 0.8736] (T 1.0: −0.0102, CIs overlap, no paired test); MCC 0.7781 → 0.7454 (−0.0327); over 40 cells T 1.0 mean −0.0100, 35/40 negative; best-to-best also −0.0102 | `results/verifier-t-pilot/stage-b-report.md:86-90`, `:102-116` |
| Same files, computed for this report (I/O only) | probability scale | 607 common candidates | mean mound_probability 0.5734 (T 0.0) → 0.5444 (T 1.0), −0.029; 42 of 607 (6.9 %) decisions flip at 0.15 | `outputs/gs/gold-standard-v2/verified-v1/probabilities.json`, `outputs/verifier-t-pilot/T1.0/probabilities.json` |
| Verifier robustness, Stage 2 | N = 5 consensus snowball, T 0.0 → 0.3 | 384 and 256 px, ≥ 3-of-5 band | +0.0017 and −0.0055; stalled, so T 0.7/1.0 never ran **in Stage 2** | `results/verifier-robustness/verifier-robustness-findings.md:204-210` |
| Verifier robustness, Stage 3 | N = 5 consensus, T 0.0 / 0.3 / 0.7, minimal and high | 384 px, 855 candidates | minimal T 0.0 0.8722, T 0.7 0.8709; all five N = 5 cells one tier (0/10 pairs significant) | `…findings.md:236-246` |
| Verifier robustness, single-run means | single pass, 4-of-5 input | as above | T 0.0 0.8601, T 0.3 0.8623, T 0.7 0.8534 (T 0.7: −0.0067) | `robustness_summary_T0.0.json:45`, `_T0.3.json:45`, `_T0.7.json:46` |
| Phase 3d, Experiment C | K = 3 mean probability | 44 image-only candidates | T 1.0: ΔF1 0.000; T 0.5: +0.004 | `results/phase3d-verifier-experiments-abc.md:27-28` |

**Flag on the brief.** "T 0.7/1.0 never ran" is true of Stage 2 only; Stage 3 did run verifier
T 0.7 at N = 5 (`…findings.md:228-242`), and the separate verifier-temperature pilot ran T 1.0.

### 4.3 The bound against each affected claim

Assumption for the "direction" column: 3.7/3.8 respond to temperature as G3 Flash does, and the
default is 1.0. Neither is known (§ 4.4).

| # | Effect | Applicable G3 bound | Can a shift of that size produce or erase it? | Direction under the assumption |
|---|---|---|---|---|
| A1 | +0.0178, n.s. | text PV, N = 5: ≤ 0.0054 | no change of verdict (already unresolved); attribution to the model weaker | sign-ambiguous |
| A2 | +0.0056, n.s. | text PV, N ≥ 3: ≤ 0.008 | **yes** (a tie either way) | sign-ambiguous |
| A3 | +0.0099 to +0.0107 | text PV ≤ 0.008, plus the K = 5 vs 10 mismatch | **yes**: the D48 rewording "a small difference, not a null" (`w27…:627`, `:648-649`) cannot be credited to the proposer model | sign-ambiguous |
| A4 | union ×3.5 smaller | union ×1.21–1.27 per 0.7 → 1.0 | no | 3.7 at T 0.7 would be tighter still |
| A5 | +0.0224 (oracle) | ≤ 0.008 | partly | sign-ambiguous |
| A6 | +0.0107, BH 0.015 | text N = 1: 0.020–0.034, plus verifier ≈ 0.010 | **yes in magnitude** | understated (a G3 single pass at T 1.0 loses 0.020–0.034 to T 0.7 through the verifier) |
| A7 | +0.084 / +0.090 | image PV: 0.013–0.053 (K = 5 cells 0.035 / 0.053) | no | understated |
| A8 | gap change −0.059 to −0.066 | image 0.013–0.053 against text ±0.008 | the change survives; **the "parity, not inversion" reading does not**: a T-matched 3.7 gap could sit at roughly −0.02 to −0.06 | the gap change grows |
| A9 | qualitative | — | needs rewording regardless | — |
| A10 | F1 +0.100 / +0.107; MCC +0.024 / +0.041 | image F1 ≤ 0.053; image MCC ≤ 0.036 | F1 no; **MCC yes for T2** (+0.024) | understated |
| A11 | +0.085 / +0.119 F1; +0.018 / +0.054 MCC | as A10 | F1 no; the +0.018 MCC yes | understated |
| A12 | MCC falls with K on 3.7 ladders | union +21–27 % per 0.7 → 1.0 | **yes**: a higher effective temperature is a candidate mechanism (more new false positives per extra pass) | — |
| B1 | +0.0270 / +0.0234 | verifier T 0.0 → 1.0: −0.010 F1 | no (2.3–2.7× the bound) | understated |
| B2 | +0.0267 / +0.0311 / +0.0325 | text proposer ≤ 0.008 plus verifier ≈ 0.010 | no in direction; magnitude uncertain by up to ≈ 0.02 | understated |
| B3 | +0.0126, untested | ≈ 0.010 | **yes in magnitude** | understated |
| B4 | mean probability +0.10; optimum up four rungs | G3 T 1.0: mean −0.029; optimum stays at 0.15 | no: wrong sign and a third of the size | — |
| B5 | MCC 0.726 vs 0.711 | verifier MCC −0.012 to −0.033 | **yes** as a ranking (margin 0.015) | understated |
| B6 | +0.0195 n.s.; +0.036, BH 0.028 | top cell is image: proposer ≤ 0.053 plus verifier ≈ 0.010 | R4-24 only if the assumption fails; already "inside the cross-date band" (`w27…:588`) | understated |
| B7 | +0.0119, p = 0.097 | ≈ 0.010 | **yes** (already n.s.) | understated |
| B8 | spread 0.0022 vs 0.0497 | G3 at T 1.0 is not flatter: spread 0.108 vs 0.092 at T 0.0 (`stage-b-report.md:104-111`) | no | — |
| B9 | +0.0179, p = 0.056 | ≈ 0.010 | **yes** | understated |
| B10 | +0.0054, untested | ≈ 0.010 | **yes** | understated |
| B11 | MCC +0.016 to +0.025; F1 +0.010; DiD/T4 +0.017 MCC | verifier MCC −0.012 to −0.033; F1 −0.010 | **yes**; DiD and T4 cancel the mismatch only if it acts equally on image and text pools (untested) | understated |

### 4.4 Caveats

1. **The default is unverified.** It may be 1.0 (the Gemini documentation's recommendation, as
   the project recorded it for Gemini 3: `docs/methodology/preregistration/decisions-log.md:201-215`)
   or not. If the default is below 0.7 the proposer-side mismatch shrinks or reverses sign, and
   the Phase 2b single-pass text track (best at T 0.0–0.3) becomes the relevant precedent.
2. **The bound measures G3 Flash, not 3.7.** It also measures thinking minimal and high, while
   3.7 ran at low with about 265–277 thinking tokens per call (`results-draft.md:891-892`).
   Temperature and thinking may interact. Every row in § 4.3 is an analogy, not a measurement.
3. **The verifier regime is different.** A verifier moving from T 0.0 to a default near 1.0 is
   covered only by the pilot's single pass (−0.010 F1, −0.033 MCC at the carried point, scale
   −0.029), Stage 3's N = 5 consensus to T 0.7, and 44 candidates in Phase 3d. All are G3
   minimal; the Stage B gold standard was itself filtered by the T 0.0 verifier, a bias against
   T > 0 (`stage-b-report.md:200-205`).
4. **Through a verifier: E43 and Phase 2b do not measure it, the PV grid does.** E43's matched
   cells are "proposer-consensus cells with no verification pass" (`e43…/findings.md:1052-1054`)
   and Phase 2b is single pass. But E43's matched pools are the proposer pools of
   `pv-min-text-t0.7-*` and `pv-min-text-t1.0-*` (`results/run-conditions.json:1825-1831`,
   `:4236-4240`, `:4317-4321`). Through the verifier, the text-MIN temperature effect falls from
   −0.021/−0.034 to +0.003/−0.006: the verifier absorbs it. It does not absorb the image-pool
   effect.
5. **Instrument transfer.** The bound is GS, 487 tiles, 20 m; the 55-map claims are corrected F1
   at 50 m. The 55-map within-execution floors (0.006–0.010, `w27…:597-601`) are of the same
   order as the text bound.
6. **Selection and configuration.** PV-grid cells are each arm's sweep optimum; the image cells
   use `library_plus-hp`, not the `detect_brief-text-image` configuration of the 3.7 and G3
   image arms; and the 0.7-vs-1.0 pairs carry the date confound of § 4.1.

## 5. Default-temperature evidence

- **No project file records a model's default `temperature` or `maxTemperature`.** A repository
  search for `maxTemperature`/`max_temperature` (excluding `.venv`) returns nothing, and
  `outputs/verifier-date-2026-10-07/` holds only Run A's verifier legs.
- **The Stage 0 listing of 2026-10-07 did not capture the fields.** Its script printed one
  served flag per name: `gemini-3-flash-preview` served, `gemini-3.7-flash` served,
  `gemini-3.8-flash` served, `gemini-3-flash` and `gemini-3.7-flash-preview` not served. It
  exists only in a live session transcript (session `efba6aeb…`, tool result at
  2026-10-07T05:13:25Z), not in the repository; the gate records only "both models served"
  (`planning/gate-2026-10-07-verifier-date-and-bridge.md:9-11`). **Values for
  `gemini-3.7-flash`, `gemini-3.8-flash` and `gemini-3-flash-preview`: not held.** No API call
  was made to obtain them.
- **No natural experiment exists.** All 61 run metas naming 3.7 or 3.8 record either 0.7
  (proposer, 44) or 0.0 (verifier, 17); none ran at another temperature (survey of
  `outputs/**/*.meta*.json` for this report).
- **What the project asserts about the default** concerns Gemini 3, from documentation: "the
  Gemini API defaults temperature to 1.0" (`results/retest/retest-production-summary.md:333`;
  `results/retest/phase2b/analysis_summary.md:31`). The project's own detector configurations
  also carry 1.0 (`prompts/configs/detect_brief-text.json:7`), overridden to 0.7 by `--temperature`
  at launch (e.g. `scripts/gemini37-escalation.sh:58`).
- **Indirect behavioural evidence.** On the same 9,173 candidates, two invocations of the 3.7
  verifier "at T 0.0" agree exactly on 63.51 % of probabilities (κ 0.4957), against 81.84 %
  (κ 0.7728) for G3 at T 0.0
  (`results/gemini37-image-55map-2026-09-13/replicate-k5-arm1-batch-2026-09-20/findings.md:125-130`);
  for reference, G3 T 0.0 against G3 T 1.0 agree on 251 of 607 (41 %; computed here). The
  3.7 figure fits sampling above zero, but model and thinking level (low emits tokens, minimal
  emits none) differ too, and the decision flip rates at each arm's own point are equal (2.41 %
  vs 2.46 %, `:135-136`). Suggestive, not diagnostic.

## 6. Code paths that send a temperature

No builder sends `top_p`, `top_k` or `thinking_budget` (repository search of `scripts/`); thinking
is sent as `thinking_level` only.

| Path | Where temperature is set | Default if the configuration omits it | Override |
|---|---|---|---|
| Detector, real time (`detect_mounds_versioned`) | `scripts/4_detect_mounds_batch.py:1003`, built at `:1025` | 0.1 | `--temperature` via `temperature_override`, `:844-849` |
| Detector, batch (`_detect_mounds_batch`) | config override `scripts/4_detect_mounds_batch.py:1519-1520` → `scripts/lib_batch_api.py:2883-2884` (`prepare_batch_unit`) → JSONL `generation_config`, `scripts/lib_batch_api.py:1218` (`build_jsonl_file`) | 0.1 | unit or CLI temperature |
| Batch synchronous retry (`_retry_tile_sync`) | `scripts/lib_batch_api.py:2510` | 0.1 | from the prompt configuration |
| Batch tile patching (`patch_failed_tiles`) | `scripts/lib_batch_api.py:3556`, read from the meta snapshot | **0.0** (inconsistent with the 0.1 above) | — |
| Verifier configuration (`build_generation_config`) | `scripts/lib_verifier.py:211-218` | 0.0 | `temperature_override` |
| Verifier real time (`_verify_realtime`) | `scripts/run_pv.py:1955` → `scripts/lib_verifier.py:284` (`gen_config_to_sdk`) | 0.0 | `--temperature` |
| Verifier batch, single pass (`_verify_batch`) | `scripts/run_pv.py:1082-1088` → `build_verifier_jsonl` → `lib_verifier.py:218` | 0.0 | `--temperature` |
| Verifier batch, consensus | `scripts/run_pv.py:1072`; `scripts/lib_verifier.py:542`, `:569` | **0.7** (warns at 0.0, `:561-565`) | `--temperature` |
| Auxiliary | `scripts/5_verify_crops.py:566` (0.1); `scripts/standalone_verification.py:246` (0.0); `scripts/55maps-fp-classify.py:1746` and `scripts/gs-fp-classify.py:2530` (0.0 fixed); `scripts/probe_cache_tier.py:93`, `:124` (0.0); `scripts/run_h2_pilot.py:339` (0.0, `:111`); `scripts/reverify_image_only_high_thinking.py:130` (0.0, `:32`); `scripts/reverify_image_only_experiments.py:141-159` (0.0, 0.5) | as stated | — |
| Configuration files | 67 of 69 `prompts/configs/*.json` carry `temperature` (e.g. `detect_brief-text.json:7` 1.0; `verify_adversarial-text.json:7` 0.0) | — | — |
| Metadata | `scripts/lib_llm_metadata.py:744` records the configured value | — | — |

For the follow-up rule: omitting temperature has to happen in every row above, and the metadata
writer must then record "omitted (model default)" rather than a number, or registers will go on
logging a value that was never applied.

## 7. Open questions for the PI

1. **Read the default for free?** One `models.get` per model (`gemini-3.7-flash`,
   `gemini-3.8-flash`, `gemini-3-flash-preview`) returns `temperature`, `maxTemperature`,
   `topP` and `topK`: no tokens, no cost, but an API call under the gate rule. It settles the
   default's value, not whether custom values are ignored.
2. **Test the notice directly?** A paired probe would settle it for the project's own requests:
   the 3.7 verifier on about 200 GS candidates at T 0.0 and at T 2.0, compared with same-T
   re-invocation agreement; or 50 tiles of the 3.7 proposer at T 0.0 and T 1.5. At the measured
   3.7 verifier rate of about US$0.0011 per candidate
   (`results/gemini3-image-55map-2026-09-16/findings.md:255`) the verifier probe would cost about
   US$0.45. It needs approval.
3. **Methods wording.** Report 3.7/3.8 sampling as "requested T 0.7 (proposer) / 0.0
   (verifier); per the provider, not applied from Gemini 3.6 Flash on, so the model default
   was used", and add temperature beside thinking level as an unseparated part of the "model
   package" (as `results/gemini37-image-55map-2026-09-13/findings.md:325-327` already does for
   thinking).
4. **D19's carry claim (A9).** Restate it as the configuration *minus temperature*, or drop
   "carries" for "transfers at the model's default sampling"?
5. **R7.3-22 (A8).** Replace "parity rather than inversion" with "the gap closed from +0.055 to
   about zero; whether it inverts cannot be read, because the 3.7 arms ran at an unknown default
   and the G3 image track is temperature-sensitive"? Run B re-runs the same nominal settings, so
   it removes the date component but not this one.
6. **Small proposer-axis claims (A2, A3, A6) and small verifier claims (B3, B7, B9–B11).** Mark
   them as within the temperature analogy's bound, alongside the floors of W2.7 § 7?
7. **Run B (B12).** State in the gate that the 3.7 arms' temperature is nominal. Before Stage 1,
   confirm that `gemini-3.7-flash` still *accepts* a temperature field: the notice says upcoming
   models will reject it with 400 INVALID_ARGUMENT, and a rejection would fail every request.
   Stripping the field for the 3.7 arms would change the request but, on Google's account, not
   the behaviour.

**Other surprises found while reading (outside the brief, for the PI's attention):**

- `docs/paper/results-draft.md:386-388`: a sentence is spliced into the number 0.9068 ("… under
  the carried verifier 0. That two of the five are image cells … (Obs 447).9068)").
- `results/retest/phase2b/analysis_summary.md:71` gives the Phase 2b tile size as 384 px; the
  production summary says 512 px (`results/retest/retest-production-summary.md:34`), as does the
  post-run report (`outputs/retest/phase2b/post_run_report.md:144`).
- § R4's board figures (79 cells, 3,081 pairs, seven tiers; `results-draft.md:373-382`) predate the
  2026-09-14 rebuild, which tiers 150 of 153 cells over 11,175 pairs and awaits re-signature
  (`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md:3-5`). The PV-grid p-values
  quoted in § 4.1 come from the rebuilt family.
- The comparator in R4-21/-23/-24 is a G3 **T 0.3** cell, so those cross-generation contrasts were
  never temperature-matched, even nominally.

## Changelog

### 2026-10-07 — Original publication (Session 163)

Written by a background agent at the PI's request (continuity item (2),
S162 close), from committed files only: no model API call. Filed by the
main session with this header and changelog; body unchanged.
