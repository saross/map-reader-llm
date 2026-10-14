# D62 (1): the gold-standard boards re-scored with the wrong-sheet rows re-verified (not published)

> **Last revised**: 2026-10-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), a background subagent of the main Session 164
  session (workstream `rescore-repaired-gs`). Every number below was read
  from the run outputs on sapphire, or from the committed files at
  `origin/main` `bfd1163b0`, by the workstream agent on 2026-10-13 before
  it was written here.
- **Date**: 2026-10-13 (UTC).
- **Repository**: `map-reader-llm`, branch `rescore-repaired-gs` from
  `origin/main` at `bfd1163b0`; the reader routing is commit `9c843b980`.
- **Ruling**: principal investigator (PI) ruling D62 (1)
  (`planning/pi-decisions-2026-09-20.md`): the origin gap fixed in the
  gold-standard (GS) chains (PR #42, `dddfcc0af`) and the H13 chain and
  library copies (PR #41, `602593ecb`), and the 1,029 wrong-sheet verifier
  rows re-verified on crops from their own sheet and booked in
  `<leg>_repaired/` copies (PR #43, `0e8a1fa7a`). Item 1 of the S163
  start-here block (`planning/paper-writeup-continuity.md`): re-score the
  boards once and report before any document changes. Also measured here:
  PR #37's moved artefacts (D60 (3)) and A-07 under the D50 scorer
  (D62 (5); report only).
- **Where the runs are**: `~/scratch/s164-rescore-2026-10-13/` on sapphire:
  `copies/` (disposable copies), `logs/`, `extract/` (the numbers below),
  `pairwise/`, `h13/`, `side/`, `uplift/`, `board/`. The drivers and the
  extracted numbers are committed beside this record in
  [`rescore-repaired-gs-scripts/`](rescore-repaired-gs-scripts/).
- **Guarantees**: no model Application Programming Interface (API) call;
  no committed file under `results/`, `outputs/`, or `docs/`, and no
  register row, was changed; nothing re-signed; nothing merged. Sapphire's
  shared checkout was read only (two gitignored prepared-pass directories
  were copied out of it). At most eight of this workstream's processes at
  a time.

**Conventions.** COMMITTED is the file at `origin/main` `bfd1163b0`.
ORIGIN is today's code (this branch) with `MAP_READER_VERIFY_DIRS=fixed`,
on the data as it was before PR #43 (`be252e57b`, so that the 27 Run B/C
`_repaired` copies PR #43 rewrote in place hold their earlier rows); it is
PR #42's and #41's fixes alone. REPAIRED is today's code with the default
leg rule on today's data: the fixes plus the re-verified rows. F1 is at
20 m on the 487-tile common footprint unless stated; MCC is tile-level
Matthews correlation coefficient; p values are the committed instruments'
(tile-swap permutation, 10,000 draws, seed 42; or the paired tile
bootstrap at B = 10,000 where the analysis uses it).

## Bottom line

1. **The readers are routed** (commit `9c843b980`, draft PR): every
   reader of the 95 affected legs goes through the D58 Q8 leg rule and
   records the directory it read; the three Run B `verify_g3` legs resolve
   to `verify_g3_repaired/`; two instrument gates read the legs as run, on
   purpose. Eight tier-1 tests, seven of them red on `main` in a copied
   harness.
2. **ORIGIN reproduces PR #42 and PR #41 exactly** (155 of 155 shared
   extract keys; the H13 sweeps byte for byte), and today's `main`
   reproduces PR #37's 32 comparisons and its § 4 move counts exactly.
3. **The re-verified rows lift every downstream verified cell by about
   +0.005 to +0.010 F1** (at the registered point: +0.0046, Image-B
   MINIMAL, to +0.0101, the 3.7 screen K = 10), close to PR #42's § 7
   bound, which four cells exceed (S4). Rankings hold everywhere they were
   tested.
4. **Most verdicts survive with restated numbers.** Survive verbatim:
   `stride-plateau-2026-08-25`'s row text, R1b-15's "6 of 78" (not the
   predicted 8: S1) and its tiers, R1b-18, R1b-13, `uplift-supplement-flatten`.
   Survive, numbers restate: R1b-05 (PR #42), R1b-08, R1b-10 to R1b-12,
   R1b-14, R1b-17, Image-B IP1–IP5 and HP1–HP5, the Gemini 3.7 screen,
   the 3.7 image parity reading, the fourth cell, Arm V, R7.3-01 to -03,
   -11, -21 to -23.
5. **Fail**: the overlap reversal at 384 px (grid post-verifier, R1b-09;
   p 0.0541, S5); I3 on the 3.7 image carried arm (optimum 0.05, S6);
   R1b-15's 30 m sentence and R1b-16's "share the 30 m shelf"; the grid
   findings' Phase A paragraph (leader at 20 m only, min6 not cleared).
   **Need new wording, not a new verdict**: R3-14 / R6-17's "the verifier
   absorbs 40.6 %" (about 60 %), R6-16's "about US$43 per 0.001 F1" (about
   US$22), R7.3-21's "about five times" (about four), and the K-ladder
   outcome's "seven ladders exclude K = 10 on tile-MCC" (six).
6. **Signatures that would lapse on publication**: `grid-postverifier`,
   `stride-winner-ladder-exact`, `image-b-modality`, `image-b-thinking-pair`,
   `gemini37-screen`, `gemini37-image-gs`, `gemini37-fourth-cell-gs-leg`,
   `gemini38-screen-armv`, `verifier-uplift-pairing`, and (§ 3.1, § 3.2)
   the Era-2 board and the K-ladder review; `null-exemplar-sensitivity`
   likely (not re-run). `grid-tilesize-overlap` lapses on PR #42 alone.
   `stride-plateau` and `uplift-supplement-flatten` hold.
7. **Surprises** (§ 5): besides S1 and S4 to S8, PR #42's origin route
   moves four Gemini 3.7 cells' best points that #42 never re-scored (S2,
   shown by a legacy control); the verifier-uplift twins move on the same
   route, turning the 3.7 image carried arm's uplift negative (S3); and
   four Era-2 members (tier E's K = 1, 3, 5 rungs) move on today's code
   with no repaired row at all, so ORIGIN does not reproduce the committed
   Era-2 tiering (7,961 → 8,014 significant pairs) or tier E's ladder (S9).
   The Era-2 board keeps its structure in REPAIRED (14 tiers, the same
   five-cell Tier 1 in the same order) but its F1 MCB set shrinks from 65
   to 52 (§ 3.1).
8. **A-07 under D50**: 25 leaves move, as predicted; no optimal k, flag,
   or verdict changes (§ 3.4).
9. **Integrity**: two runs per reading agree byte for byte apart from
   timestamps and copy paths; kernel bad-page count 0 before and after.

## 1. The reader routing (deliverable A; draft PR)

PR #43 booked the re-verified rows beside 95 committed legs, but every GS
reader read its leg by fixed name, so no board saw them. Commit `9c843b980`
routes every reader of those legs through the one rule D58 Q8 applied to
the 55-map image readers (`scripts/lib_verify_dirs.py`): a leg is read from
`<leg>_repaired/` when that copy holds `probabilities.json`, from `<leg>/`
otherwise, and always from `<leg>/` under `MAP_READER_VERIFY_DIRS=fixed`.
Each reader writes the directory it read, with its SHA-256 and repair and
re-verification counts, as `verifier_probabilities`.

- **The three union loaders**, through which almost every reader goes:
  `grid_verifier_analysis.load_verified_union`,
  `stride_verifier_analysis.load_stride_union` (and
  `load_stride_union_on_origin`, which keeps the record through the
  origin step), and `image_b_analysis.load_image_union` (which also takes
  a per-call `policy`). A new helper, `lib_verify_dirs.read_leg_results`,
  returns a leg's rows and its provenance in one call.
- **Outputs that now record the directory read**: `verifier_analysis.json`
  and `grid_verified_conditions.json` (and each condition entry),
  `stride_verifier_analysis.json`, `plateau_analyses.json`, every
  `image_b_analysis.py` `analysis.json` (Image-B, the Gemini 3.7 and 3.8
  screen cells, the fourth cell, the 3.7 image arms, the bridge cells),
  `pair_verdicts.json`, the selection-aware sweep metadata, the bridge
  floors' `gates.json`, the verifier-SD replicate record, the winner-ladder
  rung materialiser (a `verifier_probabilities.json` beside each rung), the
  3.7 GS opmax-rung derivation, and the temperature probe.
- **The three Run B legs** (`g3-text`, `g3-image`, `g3-text-temp1`): their
  replicate-1 readers in `modality_bridge_floors.py` (`ARMS`),
  `modality_bridge_verifier_sd.py`, and
  `scripts/modality-bridge-2026-10-07-score.sh` name the leg `verify_g3`,
  which the rule resolves to `verify_g3_repaired/` (committed by PR #43);
  the score driver previously named `verify_g3_repaired` explicitly, which
  did not exist before PR #43. The verifier-SD script's provenance now
  records the directory actually read rather than the name asked for.
- **Two gates read FIXED, on purpose**, and say so in code: the bridge's
  six-cell anchor gate (`modality_bridge_anchors.GATE_POLICY = "fixed"`)
  and the 55-map image campaigns' GS-calibration count gate
  (`gemini37_image_55map_r2.stage_selftest`). Both check the instrument
  against values registered on the legs as run; the repaired rows move
  those values by design, so reading them would refuse every bridge cell
  for a change of data, not of instrument. Callers that compare against an
  original's current set (`modality_bridge_floors.original_sets`) read it
  under the rule.
- **Historical gates stay hard**: `register_pass1_materialise.py` and
  `derive_g37_gs_opmax_rungs.py` read under the rule but keep their
  committed-count gates, so they refuse under the repaired reading and
  reproduce the committed rungs under `fixed`. That is the intended
  behaviour for registration-time reproduction scripts.

**Tests** (`tests/test_rescore_leg_routing.py`, 8 tier-1): the helper; each
of the three loaders reads the repaired copy by default, the leg under the
fixed policy, and records which; the origin loader keeps the record when
the origin step drops `attrs`; a `_repaired` name is read as named; the
anchor gate passes `policy="fixed"`; the bridge's replicate 1 resolves
`verify_g3` to `verify_g3_repaired` and records it; the probe reads under
the rule. **Red sentinel**, in a copied (not linked) harness of
`origin/main` with only the new library copied in: 7 of the 8 fail, and the
three loader tests fail on the value itself (`[0.9, 0.05] == [0.9, 0.95]`:
the loaders read the blind leg); on the branch all 8 pass. The touched
modules' existing tests pass (133 in the first run, 36 re-run after one
fix). `ruff check` is clean on every changed file. Full tier-1 at the
branch head `9c843b980` on sapphire, single process: 4,370 passed, 5
skipped, 132 deselected, 3 xfailed, 0 failed (`main` had 4,362 at PR #43's
merge; the 8 new tests make the difference).

## 2. How the boards were re-scored

**Copies.** Four disposable copies on sapphire, each a `git archive` of the
code at `9c843b980` and of the data the chain reads (about 1 GB each; the
gitignored prepared passes of the 3.7 image cell and the seven bridge arms
copied from the shared checkout, where the chains' row-for-row union gates
check them against the committed unions): `originA` and `originB` (data at
`be252e57b`, policy `fixed`) and `repairedA` and `repairedB` (data at
`9c843b980`, default policy). The ORIGIN copies hold no
`reverify-wrong-sheet-*` record and 27 `_repaired` directories (the
pre-PR #43 Run B/C parse repairs); the REPAIRED copies hold 65 of each.

**Chain** (`rescore-repaired-gs-scripts/chain.sh`, one process at a time
per copy, single-threaded): PR #42's chain (`grid_analysis.py --bootstrap
10000`, `grid_materialise_conditions.py`, `grid_verifier_analysis.py
--materialise-conditions`, `stride_verifier_analysis.py`,
`grid_incumbent_rescore.py`, `image_b_analysis.py` for Image-B MINIMAL and
HIGH, `image_b_pair.py`, `stride_plateau_analyses.py`), then the seven
Gemini 3.7 / 3.8 cells with the arguments their committed outputs imply
(the 3.7 screen K = 5 `verify`, K = 10 `verify_k10` and swap37
`verify_swap37`, Arm V `verify_swap38`, the fourth cell `verify_37` on the
grid union, the two 3.7 image arms; K = 5 cells run with `--k 5`, and a
first-N ladder only where the committed file has one, K = 10 and Arm V),
then the 3.7 image
gap test and the Arm V pair test (`pair_tests.py`: each script's own `main`,
with only its hand-typed gate constants replaced by this copy's
regenerated values; in an ORIGIN copy they equal the constants), then
`conditions.py`: the five stride K = 10 conditions and the three exact
winner-ladder rungs re-materialised at the regenerated best points (as
`grid_verifier_analysis.py --materialise-conditions` does for the grid's
four) and
scored with `evaluate_detections.py` (buffer 20 m, B = 10,000, seed 42,
`--mcc`, grid common bounds), and the nine `best-eval/` evaluations re-run
with each one's committed arguments. The text-B anchor F1 passed to every
`image_b_analysis.py` call is the copy's own re-scored value (0.8961 in
ORIGIN, 0.9017 in REPAIRED).

**Boards** (`board.sh`, `ladders.sh`): a board copy per chain copy holds
the Era-2 board directory and every file its 153 members' evaluations
read; the ten members whose detection set a chain regenerates are copied
in at their registered operating points (`regsets.py` builds the set at
the registered point through `image_b_analysis.py`'s own path wherever the
analysis's argmax moved) and re-scored on the board frame with their
committed arguments, then
the board's own instruments run (`era1_leaderboard_tiering.py
--permute-mcc`, `selection_aware_intervals.py --board` for F1 and MCC). The
two gold-standard K ladders (stride A, tier E) are re-tested the same way
with the K-ladder review's commands (findings § 6 and `k_ladder_mcb.py`).
**Bridge** (`bridge.sh`): Run B's ten cells and three gap tests, as
`scripts/modality-bridge-2026-10-07-score.sh` runs them, behind the
six-cell anchor gate.

**Extraction.** `extract.py` (PR #42's extractor plus the S164 keys) reads
249 named quantities from each copy and 234 from the committed files
(`git:origin/main`); `keydiff.py` compares them key by key.

## 3. Verdicts per signed analysis

Each row gives the numbers the analysis's registered outcome quotes, as
COMMITTED → ORIGIN → REPAIRED ("=" where a column equals the one before).
A signature lapses when the outcome text it attests would have to change;
the signatures attest the text, not the artefact (`results/run-analyses.json`,
`signature.attests`).

| Analysis (signed) | Quoted numbers: COMMITTED → ORIGIN → REPAIRED | Verdict (REPAIRED) | Signature |
|---|---|---|---|
| `grid-postverifier-2026-08-18` | Board 384/50, 512/50, 384/12.5, 512/12.5: 0.8961, 0.8815, 0.8677, 0.8311 → = → **0.9017, 0.8870, 0.8761, 0.8368** (384/12.5's point (0.20, k7) → (0.15, k7)). Tile size at 12.5 %: +0.0366, p 0.0373 → = → +0.0393 [+0.0052, +0.0741], p 0.0266; at 50 %: +0.0147, p 0.2353 → = → +0.0147, p 0.2454. Overlap at 512 px: −0.0504, p 0.0003 → = → −0.0502, p 0.0003; **at 384 px: −0.0285 [−0.0530, −0.0045], p 0.0235 → = → −0.0256 [−0.0517, +0.0001], p 0.0541**. Interaction −0.0220, p 0.2257 → = → −0.0246, p 0.1831. Pure verifier max 0.8153 → = → 0.8187; stacked lead 0.052–0.203 → = → 0.057–0.207. Gain +0.130 to +0.220 → +0.120 to +0.210 → +0.126 to +0.219. Union-recall ceilings 0.8925 / 0.9509 against 0.8715 / 0.9416 → 0.9112 / 0.9696 against 0.8879 / 0.9603 → =. MCC 0.775–0.801 → = → 0.785–0.809. K = 10 baseline (384 − 512) −0.0284, p 0.2975 and −0.0312, p 0.0939 → −0.0271, p 0.3081 and −0.0319, p 0.0862 → = | Ranking, tile-size reversal, complements reading survive. **"The overlap reversal survives the verifier: 50 % wins at both sizes" fails at 384 px** (p 0.0541, interval reaches +0.0001). | Lapses (ORIGIN: gains, ceilings, baseline; REPAIRED: every board value) |
| `stride-plateau-2026-08-25` | "12 of 13 cells one statistical tier; only g512_ov064 drops. 384 px at-or-above at every stride; interior optimum strides 192–256" → same → same (tiers 12 + 1 with the same membership; 384 px leads at strides 192, 256, 336; best cells 256 (0.9075) and 192 (0.9017)) | Survives verbatim | Holds (text unchanged; the findings' 30 m sentences and claims R1b-15 and R1b-16 change: § 4) |
| `stride-winner-ladder-exact-2026-08-25` | N = 1, 3, 5: 0.8677, 0.8911, 0.8856 against K = 10 0.8982 → = → **0.8737, 0.8993, 0.8937 against 0.9075** (points unchanged; all-in $1.38 / $2.64 / $3.81 / $6.56 unchanged); "N = 3 within noise of K = 10" | Numbers restate; the noise test is the K-ladder's (§ 3.2) | Lapses |
| `image-b-modality-2026-08-28` | IP1 text − image +0.0549, p 0.0010 → = → +0.0559, p 0.0005. IP2 gap 0.0549 → 0.0258 (20 → 75 m) → = → 0.0559, 0.0366, 0.0269, 0.0245 (monotone). IP3 MCC 0.7985 against 0.7965 → = → 0.8139 against 0.8037 (within ±0.02). IP4 probability 0.15 → = → 0.15. IP5 N3 − N10 −0.0159, p 0.069 → = → −0.0136, p 0.1189. Image N = 1 0.6974 → = → 0.6998 | IP1–IP4 confirmed; IP5 indeterminate (further from significance) | Lapses |
| `image-b-thinking-pair-2026-08-28` | HP1 HIGH − MIN −0.0079, p 0.62 → = → −0.0068, p 0.668. HP2 union +126 % → = → =. HP3 MCC +0.0008 → = → **−0.0031** (0.8108 against 0.8139; within the ±0.02 band). HP4 (0.20, k8) → = → =. HP5 2.91× → = → = | HP1–HP4 confirmed; HP5 narrow miss | Lapses (HP1, HP3) |
| `gemini37-screen-2026-08-28` | Carried K = 5: 0.9139 at (0.10, k5), +0.0178, p 0.1697 → best 0.9144 at (0.05, k5) (0.9139 at the registered point) → **0.9238 at (0.10, k5), +0.0221, p 0.0971**. K = 10: 0.9142 (+0.0003), p 0.2076 → 0.9213 at (0.0, k10) → 0.9243 (+0.0005), p 0.1231. N5 − N10 −0.0011, p 0.7928 → −0.0081, p 0.1536 → −0.0013, p 0.7921. Ladder 0.8588 / 0.9018 / 0.9131 / 0.9142 → 0.8588 / 0.9018 / 0.9132 / 0.9213 → 0.8652 / 0.9118 / 0.9231 / 0.9243. Swap: 0.9265 at (0.80, k5), P 0.9254, R 0.9276, MCC 0.8078, +0.0304, p 0.0105 → = → **0.9364**, P 0.9268, R 0.9463, MCC 0.8192, +0.0347, p 0.0065. Mean probability 0.687 against 0.587 → = → 0.699 against 0.594. "Five extra passes bought +0.0003; the role swap +0.0126" → +0.0005 and +0.0126 | G1 fired, G2 falsified, saturation by N = 5, the swap the only cell above the anchor on F1 and MCC: all survive | Lapses |
| `gemini37-image-gs-2026-09-01` | Gaps (text − image) carried −0.0115, p 0.2533 and all-3.7 −0.0043, p 0.6767 → **−0.0226, p 0.0253** and −0.0105, p 0.3288 → −0.0143, p 0.158 and −0.0043, p 0.6767. Gap change against Gemini 3's gap −0.059 to −0.066 → −0.0654 to −0.0775 → −0.0602 to −0.0702 (against +0.0559). I1: 0.9254 / 0.9308 against 0.8412 (+0.0842 / +0.0896) → 0.9370 / 0.9370 (both at (0.0, k5)) → 0.9381 / 0.9408 against 0.8458 (+0.0923 / +0.0950); "about five times the text-side gain" (+0.018) → about 4.2 times (+0.0221). **I3 "confirmed exactly at (0.10, k5) and (0.90, k5)" → carried arm (0.0, k5) → carried arm (0.05, k5)**, outside I3's 0.10–0.20 band. Escalation: 0.9308 against 0.9265, +0.0043, p 0.677 → = → 0.9408 against 0.9364, +0.0043, p 0.6767 | Parity, I1, I2, the escalation decision survive; **I3 fails on the carried arm** | Lapses |
| `gemini37-fourth-cell-gs-leg-2026-08-31` | 0.9140 at (0.98, k10), P 0.9637, R 0.8692, MCC 0.8239, +0.0179, p 0.0563 → = → **0.9220**, P 0.9643, R 0.8832, MCC 0.8350, +0.0203, **p 0.0311**. Mean probability 0.209 against 0.687 → = → 0.214 against 0.699 | Survives; the head-to-head now crosses 0.05 (the text claims no significance) | Lapses |
| `gemini38-screen-armv-2026-09-04` | 0.9258 at (0.88, k5), P 0.9335, R 0.9182, MCC 0.8218, 421 → = → **0.9358**, P 0.9347, R 0.9369, MCC 0.8331, 429. Against all-3.7 −0.0007, p 0.7769 → = → −0.0006, p 0.7769; against carried +0.0119, p 0.0969 → +0.0114, p 0.2171 → +0.0120, p 0.0764. MCC over 3.7 +0.0140 → = → +0.0139. E4 flat band (0.20–0.92, k5) within 0.0022 → = → within 0.0022 (0.9336–0.9358); 3.7 0.9243–0.9265 → = → 0.9343–0.9364; carried 0.8446–0.8942 (0.0497) → = → 0.8520–0.9021 (0.0502). Thinking 76 against 106 tokens and ~$0.85 unchanged | E1 tie and E4 survive | Lapses |
| `gs-era2-verified-board-2026-09-10` | Significant pairs 7,961 → 8,014 (S9) → 8,075; 14 tiers; Tier 1 the same five; F1 MCB 65 → 65 → **52**; leaders 0.9233 / 0.9190 / 0.9182 / 0.9179 / 0.9068 → = → 0.9332 / 0.9289 / 0.9282 / 0.9278 / 0.9169; MCC family 2,982 / 6 / 33 / 59 → = → 3,001 / 6 / 34 / 60 (§ 3.1) | Structure survives; numbers restate; F1 MCB set shrinks | Lapses |
| `k-ladder-2026-09-12` | GS ladder MCC +0.0135, BH p 0.7678 → = → +0.0131, 0.7633; § 8.6 40.6 %, swing 0.0752 → 68.8 % (S9) → about 60 %, 0.0682; the 3.7 last step about US$43 → = → about US$22 per 0.001 F1; "seven ladders exclude K = 10 on tile-MCC" → = → six (§ 3.2) | Shape, MCC readings, stage reversal survive; three figures restate | Lapses |
| `null-exemplar-sensitivity-2026-09-13` | Not re-run (§ 7); 10 of its 150 Era-2 cells move (4 image-bearing, 6 text) | Exposed: its signature statistic, per-cell deltas, reduced-frame tiers | Likely lapses (not measured) |
| `uplift-supplement-flatten` | "441 registered conditions flattened into 130 strata; 441 carry a headline-buffer F1; 79 board-frame rows excluded" → same → same | Survives verbatim (38 conditions' F1 values move under REPAIRED) | Holds (on this re-score; D50's own regeneration is separate) |
| `verifier-uplift-pairing` | F1 median +0.2631, range −0.0366 to +0.5265, 2 negative → = → =; grid-common median +0.194 → +0.1847 → +0.1927. **MCC range −0.0230 to +0.8410, 3 negative → = → −0.0115 to +0.8410, 1 negative**. With the twins on the origin route (surprise S3): F1 negatives 2 → 5 → 3, MCC negatives 3 → 3 → 1 | MCC clause restates | Lapses (REPAIRED) |

Not among the 14, for completeness: `grid-tilesize-overlap-2026-08-18`
(the consensus-only grid board) moves in ORIGIN exactly as PR #42 reported
(K = 10 board 0.7611 / 0.7293 / 0.6845 / 0.6574; single-pass contrasts
+0.1207, +0.1381, −0.0803, −0.0976; interaction −0.0173, p 0.4033) and does
not move further in REPAIRED (no verifier). Its signature lapses as #42
said.

### 3.1 The Era-2 board

`gs-era2-verified-board-2026-09-10` (signed 2026-09-16; re-sign pending
since 2026-09-14). Ten of its 153 members read the affected legs; each was
re-scored on the board frame at its registered operating point
(`regsets.py`; in ORIGIN four of the analyses' argmax sets sit elsewhere,
S2), then the board's own tiering and MCB ran (§ 2). Run A equals run B on
all 94 extracted keys and file by file in both readings.

| Quantity | COMMITTED → ORIGIN → REPAIRED |
|---|---|
| Members tiered / withheld | 150 / 3 → = → = (the same three 3.7 GS text rungs) |
| Significant pairs (BH q 0.05) of 11,175 | 7,961 → **8,014** → 8,075 |
| F1 tiers | 14 → = → = |
| Tier 1 (tie set) | the five 3.7 cells (image swap37, text swap37, swap38, image carried, text K = 10) → = → = |
| F1 MCB admissible set | 65 → = → **52** (13 text cells leave; none joins) |
| Tile-MCC family: significant pairs, tiers, tie set, MCB | 2,982, 6, 33, 59 → = → 3,001, 6, 34, 60 (Image-B MINIMAL joins the MCC MCB set) |
| Rank 1–5 F1 | 0.9233, 0.9190, 0.9182, 0.9179, 0.9068 → = → 0.9332, 0.9289, 0.9282, 0.9278, 0.9169 (same order) |
| 3.8 cell (R7.3-12) | 0.9182, Tier 1, third of five → = → 0.9282, Tier 1, third of five |
| Grid 384/50 verified (rank, tier) | 0.8886 (11, 2) → 0.8886 (11, **3**) → 0.8942 (9, 3) |
| Fourth cell, 3.7 text K = 5 carried | 0.9062 (7, 2), 0.9066 (6, 2) → = → 0.9141 (7, 2), 0.9165 (6, 2) |
| Image-B MINIMAL, HIGH | 0.8341 (70, 6), 0.8263 (74, 6) → = → 0.8387 (69, 6), 0.8319 (71, 6) |

**ORIGIN does not reproduce the committed tiering, and not because of the
repair** (surprise S9): four members the repair does not touch, tier E's
K = 1, 3, 5 rungs of the grid 384/50 ladder (`g384-ov192-k{1,3,5}-verified-opmax`
and `-k1-verified-p0.15-k1`), score +0.0133 to +0.0141 higher under
today's per-tile machinery than their committed evaluations (0.8546 →
0.8680 at K = 1, and so on); the committed tiering of 2026-09-14 recorded
no such gap. Today's `evaluate_detections.py` gives the same 0.8680 for
K = 1. Their detection files carry `source_tiles` member lists and their
evaluations date from 2026-09-12, before D50, so this is D50's origin
attribution reaching evaluations never re-scored under it, not the
wrong-sheet repair. It alone moves 7,961 → 8,014 and the grid cell's tier.
The ranking column still shows those cells' committed evaluation F1 while
the permutation tests use the recomputed tables.

**Verdict.** The outcome text quotes "7961/11175 pairs significant ... 14
tiers ... Tier 1 = 5 cell(s); MCB admissible set = 65; Top
g37-image-k5-verified-swap37 0.9233; ... 0.9190 (T1); 0.9182 (T1); 0.9179
(T1); 0.9068 (T1)" and the MCC family "2982/11175 ... 6 MCC tiers ... MCC
Tier 1 = 33 ... MCC MCB 59": the structure survives (14 tiers, the same
Tier 1, the same leaders in the same order), every quoted number restates,
and the F1 MCB set shrinks from 65 to 52. The signature lapses. Claims
R4-17 and R4-18 quote earlier versions of this board (79 cells; 3,081
pairs, 1,845 significant, seven tiers) and were already stale before this
re-score; R4-28 concerns the signature record.

### 3.2 The K ladders

`k-ladder-2026-09-12` (signed 2026-09-13). Three of its 23 ladders read
the affected legs: the GS stride A ladder (every rung), the grid 384/50
tier E ladder (its K = 10 rung), and the 3.7 GS text ladder (its K = 5 and
K = 10 rungs). The first two were re-tested with the review's own commands
(findings § 6; `k_ladder_mcb.py`); the third has no admissible set (three
rungs withheld, as committed), and its two moved rungs are the Era-2
members of § 3.1. Run A equals run B in both readings.

| Quantity | COMMITTED → ORIGIN → REPAIRED |
|---|---|
| GS stride A on the board frame, N = 1 / 3 / 5 / K = 10 (R1b-17's note) | 0.8605 / 0.8834 / 0.8782 / 0.8905 → = → 0.8665 / 0.8916 / 0.8862 / 0.8999 |
| GS stride A tiers; significant pairs; F1 and MCC MCB sets | {K10, N3, N5} + {N1}; 1 of 6 (N1 − K10); {K10, N3, N5}, all four → = → = (N1 − K10 −0.0334, BH p 0.0024) |
| GS stride A tile MCC K = 1 → best (R3-13) | 0.7834 → 0.7969, +0.0135, BH p 0.7678 → = → 0.7948 → 0.8079, +0.0131, BH p 0.7633 |
| GS stride A N = 3 against K = 10 ("within noise", R1b-17) | −0.0071, p 0.32 → = → −0.0083, p 0.2275 |
| Tier E K = 1 / 3 / 5 / 10, F1 the tests use | 0.8546 / 0.8840 / 0.8905 / 0.8886 → **0.8680 / 0.8979 / 0.9046** / 0.8886 → 0.8680 / 0.8979 / 0.9046 / **0.8942** |
| Tier E significant pairs; K = 1 − K = 10 | 3 of 6; −0.0340, BH p 0.0046 → **2 of 6; −0.0206, BH p 0.1057** → 3 of 6; −0.0262, BH p 0.0292 |
| Tier E MCB sets (F1; MCC) | {K10, K3, K5}; {K1, K3, K5} → = → {K10, K3, K5}; **{K1, K3, K5, K10}** |
| § 8.6 (R3-14, R6-17): K = 1 → 10 gain, consensus-only then verified | +0.0572 (0.6633 → 0.7205), MCC +0.0444; +0.0340 (0.8546 → 0.8886), MCC −0.0308; "the verifier absorbs 40.6 %", swing 0.0752 → +0.0660 (0.6633 → 0.7293); +0.0206 (0.8680 → 0.8886); 68.8 % → +0.0660; **+0.0262 (0.8680 → 0.8942), MCC −0.0238; 60.3 %; swing 0.0682** |
| 3.7 family's K = 5 → 10 step on the board frame (R6-16) | +0.0002 (0.9066 → 0.9068) for US$8.68, "about US$43 per 0.001 F1" → = → +0.0004 (0.9165 → 0.9169), about US$22 |

**Verdict.** The review's readings survive: the front-loaded shape (K = 3
on the efficient set; stride A's N = 3 share of the gain 76 % → 75 %),
"tile-MCC never rises with K" (no significant rise anywhere; the GS
counter-example +0.0131 at BH p 0.7633), "the pipeline stage, not K,
decides tile-MCC's sign" (consensus-only MCC rises +0.0444, verified falls
−0.0238). The numbers restate, and two need new wording: the share the
verifier absorbs on tier E (40.6 % → about 60 %), and R6-16's price of the
3.7 last step (about US$43 → about US$22 per 0.001 F1, carried board-frame
rungs). The MCC MCB reading "seven of the twenty ladders with a K = 10
rung exclude it on tile-MCC" becomes six (tier E now admits K = 10). Tier
E's K = 1 to K = 3 and K = 5 rungs move in ORIGIN already (S9), so its
committed tiering does not reproduce on today's code either way. The
signature lapses.

### 3.3 The modality bridge (unregistered)

`results/modality-bridge-2026-10-07/` (Run B; the R7.3-22/23 bridge),
re-scored with `bridge.sh`: the ten cells and three gap tests, each behind
the six-cell anchor gate, which passed in all four runs (it reads its
originals as run, § 1). Run A equals run B byte for byte in both readings
(73 of 73 files). In ORIGIN every operating-point value of the findings'
§ 2 table reproduces; the best points of four 3.7 image cells move to
probability 0 or 0.05 (the S2 mechanism), which moves the gap tests that
pair best sets.

| Quantity (findings §§ 2–3) | COMMITTED → ORIGIN → REPAIRED |
|---|---|
| Gemini 3 text K = 10, (0.15, k10) | 0.8916 → = → 0.8986 |
| Gemini 3 image K = 10, (0.15, k9); best | 0.8331; 0.8393 → = → 0.8386; 0.8449 |
| 3.7 text, Gemini 3 / 3.7 verifier | 0.9154 / 0.9265 → = → 0.9241 / 0.9352 |
| 3.7 image, Gemini 3 / 3.7 verifier (operating point) | 0.9160 / 0.9288 → = → 0.9259 / 0.9375 |
| 3.7 image cached, Gemini 3 / 3.7 verifier | 0.9318 / 0.9352 → = → 0.9404 / 0.9437 |
| Gemini 3 T 1.0 text / image (best) | 0.8824 / 0.8242 → = → 0.8908 / 0.8299 |
| Gap Gemini 3 K = 10 | +0.0523 (p 0.0029) → = → +0.0536 (p 0.0018) |
| Gap Gemini 3 K = 5 / T 1.0 | +0.0609 / +0.0582 → = → +0.0624 / +0.0608 |
| Gap 3.7, Gemini 3 verifier | −0.0006 (p 0.95) → −0.0102 (p 0.23) → −0.0026 (p 0.77) |
| Gap 3.7, 3.7 verifier | −0.0023 (p 0.75) → = → = |
| Gap 3.7 text − cached image, Gemini 3 / 3.7 verifier | −0.0164 (p 0.074) / −0.0098 → **−0.0245 (p 0.011)** / −0.0135 → −0.0168 (p 0.093) / −0.0096 |
| Gap change against Gemini 3 | −0.0529 / −0.0547 → −0.0626 / −0.0547 → −0.0562 / −0.0559 |
| Bridge − original, Gemini 3 text / image | −0.0045 / −0.0081 → = → −0.0031 / −0.0072 |
| Bridge − original, 3.7 text G3v / 3.7v; image G3v / 3.7v | +0.0015 / 0.0000; −0.0094 / −0.0020 → = → +0.0003 / −0.0012; −0.0094 / −0.0033 |

The bridge's reading (the gap closes within 3.7 whichever date and
serving mode) survives in REPAIRED. In ORIGIN alone one cached-image gap
would read as a significant image lead (p 0.011). The gap-change
interaction test (§ 5), the date components (§ 6), the floors (§ 7) and
the verifier-SD floors (§ 7a) were not re-run (§ 7).

### 3.4 PR #37's moved artefacts, PR #41's H13 outputs, and A-07

None of these reads a verifier leg, so ORIGIN and REPAIRED are the same
run; each was run twice from the branch worktree into scratch.

- **PR #37 (D60 (3)), the 32 pairwise comparisons.** `run_pairwise_tests.py`
  over `configs/pairwise-comparisons.yaml` (paths made absolute, as #37
  did; 10,000 permutations, seed 42) and `apply_fdr_correction.py`, at
  20 m and 30 m: each buffer's 36 files equal PR #37's `out/new1-*` exactly
  (2 byte-identical, 34 equal after dropping `timestamp` and the run
  root), and run A equals run B the same way. So `main` reproduces #37's
  NEW values (H2's arm B 0.816471, ΔF1 0.073730; no BH crossing).
- **PR #37 § 4, the other callers** (leaderboards at 20 m and 30 m, the
  factor analysis, the e45 H2 rerun). #37 did not regenerate them; it built
  every distinct arm the 702 committed outputs record and reported which
  outputs would move. Its own probe (`probe_sources.py`, copied here), run
  on today's code: all 51 arms equal #37's `sources-new.json` (F1 at each
  buffer and detection count), and the per-directory counts of committed
  outputs whose arm F1 moves are #37's exactly: 24 of 32 (20 m), 24 of 32
  (30 m), 280 of 325 and 264 of 300 (leaderboards), 5 of 12 (factor
  analysis), 1 of 1 (e45).
- **PR #41, the H13 sub-analyses**: § 6. The registered H13 overlap
  analysis was not re-run (PR #41 found it unmoved by the fix).
- **A-07 under D50** (D62 (5); report only). `h6_registered_analyses.py`
  in two disposable copies of today's code: `a07_voting_thresholds.json`
  differs from the committed file in **25 leaves**, the count the
  continuity note predicted, and run A equals run B. The Flash comparator
  curves rise (text 0.4634 / 0.5203 / 0.5748 → 0.4647 / 0.5217 / 0.5764;
  image 0.5614 / 0.5760 / 0.5854 → 0.5631 / 0.5778 / 0.5873), the Pro text
  curve rises (0.8602 / 0.8558 / 0.8494 → 0.8626 / 0.8582 / 0.8519), the
  Pro text margin is 0.004457 → 0.004423 (still under the 0.005 fragility
  line), the Flash text and image margins 0.054448 → 0.054612 and
  0.009411 → 0.00948 (the image caveat's "0.0094" reads "0.0095"). The Pro
  image curve does not move. Every optimal k (text Pro 1, Flash 3; image 3
  and 3), every fragility flag, and both matched-N verdicts are unchanged.
  These are the D57 (4) Phase 3 values, computed then inside the
  memory-fault window; two runs here reproduce them.

## 4. Verdicts per claim row

Claim rows from `docs/paper/results-claims-inventory-2026-09-12.md`: the
27 the wrong-sheet lineage names
(`sapphire:~/scratch/wrong-sheet-crops-2026-10-13/out/lineage.json`), the
four the handoff added (R1b-05, R1b-16, R1b-18, R7.3-22/23), and the grid
post-verifier and stride rows that quote moved numbers (R1b-09 to R1b-11,
R1b-13, R1b-14). Where a claim quotes the register text and the committed
file differs (the D42 regeneration of `verifier_analysis.json` replaced
several p values on 2026-10-05), COMMITTED is the file and the claim's
own value is given in brackets.

| Claim | What it says | COMMITTED → ORIGIN → REPAIRED | Verdict |
|---|---|---|---|
| R0-05 | Instrument: tile-swap permutation 10,000, seed 42, BH q 0.05, Hsu MCB | unchanged | Survives |
| R1b-05 | K = 10 consensus-only ranking 512/50 > 384/50 > 512/12.5 > 384/12.5 | 0.7518 / 0.7205 / 0.6759 / 0.6475 → 0.7611 / 0.7293 / 0.6845 / 0.6574 → = | Survives; numbers restate (PR #42) |
| R1b-08 | Post-verifier ranking 384/50 > 512/50 > 384/12.5 > 512/12.5 | 0.8961 / 0.8815 / 0.8677 / 0.8311 → = → 0.9017 / 0.8870 / 0.8761 / 0.8368 | Survives; numbers restate |
| R1b-09 | Overlap reversal survives the verifier at about half the margin, at both sizes | 512 px −0.0504, p 0.0003 [0.0004]; 384 px −0.0285, p 0.0235 [0.0208]; baselines −0.0758, p 0.0008 [0.0004] and −0.0730, p 0.0032 [0.0026] → baselines −0.0766, p 0.0006 and −0.0718, p 0.0037 → 512 px −0.0502, p 0.0003; **384 px −0.0256, p 0.0541** | **Fails at 384 px** (survives at 512 px) |
| R1b-10 | Like-for-like baseline non-significant; the verifier flips tile size, significantly at 12.5 % | baselines −0.0284, p 0.2975 [0.281] and −0.0312, p 0.0939 [0.089]; +0.0366, p 0.0373 [0.034]; +0.0147, p 0.2353 [0.231] → baselines −0.0271, p 0.3081 and −0.0319, p 0.0862 → +0.0393, p 0.0266; +0.0147, p 0.2454 | Survives; numbers restate |
| R1b-11 | Verifier gain +0.130 to +0.220, largest at 384 px; ceilings 0.8925 / 0.9509 against 0.8715 / 0.9416 | gain → +0.120 to +0.210 → +0.126 to +0.219 (384 px +0.219 and +0.172); ceilings → 0.9112 / 0.9696 against 0.8879 / 0.9603 → = | Survives; numbers restate |
| R1b-12 | Complements: every best point keeps k ≥ 5..10; pure verifier tops out at 0.8153, trailing by 0.052–0.203 | k 5–10 → = → =; 0.8153 → = → 0.8187; 0.052–0.203 → = → 0.057–0.207 | Survives; numbers restate |
| R1b-13 | Stride is not the lever; 384 px at or above every alternative at every stride | iso-stride contrasts all non-significant → = → = (iso256 +0.0206, p 0.0839; iso192 −0.0141 and −0.0163; iso336 −0.0043) | Survives |
| R1b-14 | 384 px ladder 0.8677 → 0.8982 → 0.8961 → 0.8860; 336 → 256 +0.0305, p 0.020; 256 vs 192 +0.0020, p 0.862; 144 falls away (p 0.297 / 0.360) | as quoted (file: p 0.0215, 0.8662, 0.2837 / 0.3522) → = → 0.8761 → 0.9075 → 0.9017 → 0.8938; +0.0314, p 0.0197; +0.0059, p 0.6395; p 0.2231 / 0.4807 | Survives; numbers restate |
| R1b-15 | Plateau: **6 of 78** pairs significant, all with 512/12.5; Tier 1 the other twelve; best new cell ties the grid winner (+0.0020, p 0.862); at 30 m the top three indistinguishable to the third decimal; shelf ~0.896–0.898 at 20 m, ~0.903 at 30 m | 6 → **8** → **6** (the committed six pairs exactly); tiers 12 + 1 → = → =; +0.0020 → = → +0.0059, p 0.6395; 30 m top three 0.9034 / 0.9031 / 0.9031 → opmax 0.9173, 0.9034, 0.9031 → opmax 0.9173, 0.9124, 0.9089 | "6 of 78" and the tiers **survive verbatim** (handoff predicted 8: surprise S1); the 30 m sentence **fails**; the shelf figures restate (geometry 0.902–0.908 at 20 m) |
| R1b-16 | Geometry bought cost, not F1; the HIGH-thinking incumbents share the 30 m shelf | 30 m: opmax 0.9031, headline 0.8958 → 0.9173, 0.9054 → = (geometry 0.9124 / 0.9089) | Cost claim survives; "share the 30 m shelf" **fails** (opmax above, headline below; no 30 m test exists) |
| Grid findings, Phase A paragraph | The grid winner is the point-estimate leader at both buffers and statistically clears min6 | against opmax +0.0120, p 0.352 → +0.0002, p 0.9858 → +0.0057, p 0.6554; against min6 +0.0339, p 0.020 → +0.0171, p 0.2383 → +0.0226, p 0.1107; 30 m 0.9034 against opmax 0.9031 → 0.9173 → 0.9089 against 0.9173 | **Fails** in REPAIRED too: leader at 20 m only, does not clear min6 ("joins the shelf as a tie" survives) |
| R1b-17 | Exact winner ladder 0.8677 / 0.8911 / 0.8856 / 0.8982; N = 3 within 0.007 of K = 10 at 40 % of its cost; on the board frame 0.8605 / 0.8834 / 0.8782 / 0.8905 | as quoted → = → 0.8737 / 0.8993 / 0.8937 / 0.9075; within 0.008; costs unchanged; board frame 0.8665 / 0.8916 / 0.8862 / 0.8999 (N = 3 − K = 10 −0.0083, p 0.2275) | Survives; numbers restate |
| R1b-18 | k-curves: A argmax k = 8, flat top 6–9; B argmax k = 10 | as quoted → = → = | Survives verbatim |
| R1b-22 | Selection space ~4–5× the consensus sweep's | 580 verifier-sweep rows → = → = | Survives |
| R3-10 | The return on K is governed by thinking level (7 of 7 HIGH, 2 of 6 MINIMAL ladders) | pv-diag-384 ladders only; unaffected | Survives |
| R3-11 | K = 3 on the efficient set of every ladder; 37–93 % of the gain for 31–62 % of the cost | GS stride A N = 3 share 76 % → = → 75 % | Survives |
| R3-12 | K = 3 MCB-admissible on 12 of 22; no ladder excludes K = 10 on F1; K = 1 ruled out on F1 on 20, admissible on MCC on 22 | the two GS ladders' F1 sets unchanged; tier E's MCC set adds K = 10 | Survives; "seven ladders exclude K = 10 on tile-MCC" (register outcome) becomes six |
| R3-13 | No significant tile-MCC rise; the GS ladder's +0.0135 at BH p 0.7678 | as quoted → = → +0.0131, BH p 0.7633 | Survives; number restates |
| R3-14, R6-17 | The verifier absorbs 40.6 % of K's F1 return; tile-MCC +0.0444 consensus-only against −0.0308 verified; swing 0.0752 | as quoted → 68.8 % (S9) → **60.3 %**; +0.0444 against −0.0238; swing 0.0682 | Sign reversal survives; **the 40.6 % and the swing need restating** |
| R3-15, R6-11 | 487 tiles resolve ΔF1 of about 0.03; GS range +0.0139 to +0.0629 | 55-map subsampling unaffected; GS stride A +0.0300 → +0.0334 and tier E within the range | Survives |
| R6-14 | The 8,541 / 487 tile-factor projection overstates by 11.0 % | cost model; unaffected | Survives |
| R6-16 | The last step's price: about US$43 per 0.001 F1 for the 3.7 family | +0.0002 → = → +0.0004 on the board frame: about US$22 | **Restates** (about US$22) |
| R6-18 | F1-efficient K = 3, MCC-efficient K = 1 (admissible on MCC 22 of 22, highest on 13) | the two GS ladders: K = 1 still admissible on MCC; tier E's K = 1 MCC 0.8211 still highest | Survives |
| R4-17 | 79 verified cells on one frame (487 tiles, 435 mounds) | already stale (153 admitted since 2026-09-13); membership unchanged here | Stale before this re-score; no change from it |
| R4-18 | 3,081 pairs, 1,845 significant, seven tiers | already stale (11,175 / 7,961 / 14) → 8,014 → 8,075 / 14 | Restates (current board: § 3.1) |
| R4-28 | The board's signature record | the board's signature lapses on publication | Needs re-signing |
| R7.3-01 | 3.7 screen 0.9139 at (0.10, k5), 791-candidate union, ~$7.4 | as quoted → best 0.9144 at (0.05, k5) → 0.9238 at (0.10, k5); union and cost unchanged | Survives; number restates |
| R7.3-02 | G1 fired (above the Gemini 3 plateau ≤ 0.8934 + resolution) | as quoted → = → = (0.9238) | Survives |
| R7.3-03 | Deployment points (0.10, k5), (0.80, k5), (0.98, k10) committed before scoring | GS argmax at those points → K = 5 moves to 0.05 → all three at their committed points | Survives |
| R7.3-11 | 3.8 0.9258 against 0.9265, −0.0007, p 0.78; the paired instrument resolves ~0.011 (null SD 0.00379) | as quoted → = → 0.9358 against 0.9364, −0.0006, p 0.7769; null SD 0.00375 | Survives; numbers restate |
| R7.3-12 | 3.8 joins Era-2 Tier 1 at 0.9182, third of five; 76 against 106 thinking tokens; ~$0.85 | as quoted → = → 0.9282, Tier 1, third of five; tokens and cost unchanged | Survives; number restates |
| R7.3-21 | 3.7 image 0.9254 / 0.9308, +0.084 / +0.090 over 0.8412; about five times the text gain | as quoted → 0.9370 / 0.9370 → 0.9381 / 0.9408, +0.092 / +0.095 over 0.8458; about four times (+0.0221) | Survives; "about five times" restates as about four |
| R7.3-22 | Gap +0.0549 (p 0.001) in Gemini 3 → −0.0115 (p 0.25) and −0.0043 (p 0.68) in 3.7: parity | as quoted → +0.0549; **−0.0226 (p 0.025)**, −0.0105 (p 0.33) → +0.0559 (p 0.0005); −0.0143 (p 0.16), −0.0043 (p 0.68) | Parity survives in REPAIRED; in ORIGIN alone the carried-verifier gap would read as a significant image lead |
| R7.3-23 | "Text beats image" is Gemini 3-specific | follows R7.3-22 | Survives |
| R7.3-29 | Thinking 265–277 t/call (text), 88–157 (image) | unchanged (proposer usage) | Survives |

## 5. Surprises

Flagged, not explained away; each with its evidence.

- **S1. "6 of 78" does not become 8.** The handoff predicted R1b-15's
  count would become 8 (PR #42's ORIGIN value, reproduced here exactly).
  With the re-verified rows it is **6 again, and the same six pairs as
  committed**: g512_ov064 itself rises (0.8311 → 0.8368), so min11 and
  min6 no longer separate from it after Benjamini–Hochberg (BH) correction
  (raw p 0.0054 and 0.0133, against 0.0018 and 0.0042 in ORIGIN).
  `rescore-repaired-gs-scripts/records/extract/{originA,repairedA}.json` →
  `plateau/significant_pairs`.
- **S2. PR #42's origin route moves four Gemini 3.7 cells it did not
  re-score.** In ORIGIN the best point of the 3.7 screen K = 5 cell moves
  from (0.10, k5) to (0.05, k5) (0.9139 → 0.9144), K = 10 from (0.10, k10)
  to (0.0, k10) (0.9142 → 0.9213), and both 3.7 image arms to (0.0, k5)
  (0.9254 and 0.9308 → 0.9370, one identical set). A legacy control at
  `main` just before PR #42 (`4974c3c2b`, the D50 scorer without the
  origin route; `rescore-repaired-gs-scripts/legacy_g37.sh`) reproduces all
  four committed values exactly, so the move is the origin route. The
  mechanism is the one PR #42 § 7 described: the wrong-sheet candidates
  were rejected for want of a picture (probability at most 0.05), so at
  thresholds of 0.05 or 0 they enter, and on the origin route they score
  on their own sheet as true mounds. On these small, precise unions that
  lowers the argmax; on the grid and stride unions it does not. Under
  ORIGIN alone, the 3.7 carried-verifier modality gap would read as a
  significant image lead (−0.0226, p 0.0253). The re-verified rows move
  every argmax back to its committed point except the 3.7 image carried
  arm (0.05, k5): see S6. The registered conditions at their points are
  unchanged in ORIGIN.
- **S3. The verifier-uplift twins move on the origin route, and one uplift
  turns negative.** 19 of the 21 grid-common twins in
  `verifier-uplift.csv` equal their cell's committed sweep row at
  probability 0 (the union at the same vote threshold, no verifier); the
  other two are the registered 384/50 consensus condition
  (`rescore-repaired-gs-scripts/twins.py`). On the origin route every one
  rises, by +0.0067 (512 px / 62.5 %) to +0.0183 (3.7 image arms). The twins were
  scored before PR #42 and read no verifier leg, so neither PR #42 nor this
  re-score regenerated them. With origin-route twins the 3.7 image carried
  arm's F1 uplift is **−0.0017** in REPAIRED (−0.0116 in ORIGIN): on that
  cell the carried verifier adds no F1 over unanimous five-pass consensus.
  `rescore-repaired-gs-scripts/records/uplift/repairedA-origintwins.json`.
- **S4. PR #42's § 7 "Bound" was not an upper bound.** It set every
  wrong-sheet candidate's probability to 1.0 at each cell's best point
  and called the result "the most any re-verification could add there".
  Four cells exceed it with the real re-verification: g256_ov064 0.8876
  (bound 0.8848), g512_ov320 0.8854 (0.8843), g384_ov240 0.8938 (0.8933),
  and Image-B MINIMAL 0.8458 (0.8438). The bound admitted every candidate,
  including those that are not mounds; the verifier admits only some. The
  other ten cells land at or below their bound (g512_ov064 and g512_ov256
  exactly at it).
- **S5. One registered verdict fails: the overlap reversal at 384 px.**
  `grid-postverifier-2026-08-18` and R1b-09 say 50 % overlap wins
  post-verifier at both tile sizes. With the re-verified rows, at 384 px
  it is −0.0256 [−0.0517, +0.0001], p 0.0541: no longer significant. At
  512 px it holds (−0.0502, p 0.0003).
- **S6. One registered prediction fails: I3 on the 3.7 image carried
  arm.** `gemini37-image-gs-2026-09-01` reads I3 as "confirmed exactly at
  (0.10, k5)"; I3 predicted the carried arm's optimum in 0.10–0.20. With
  the re-verified rows it is at (0.05, k5) (0.9381, against 0.9353 at
  0.10). The 3.7-verifier limb holds at (0.90, k5).
- **S7. A p value crosses 0.05.** The fourth cell's GS leg against the
  text-B anchor: +0.0179, p 0.0563 → +0.0203, p 0.0311. The outcome text
  claims no significance, so no verdict changes, but a reader of the old
  text would draw the opposite inference.
- **S8. The GS plateau rises as a whole, and geometry now leads the
  incumbents at 20 m.** Every verified cell downstream of the legs gains
  +0.0046 to +0.0101 F1 at its registered point. The plateau's leader (384 px / 33.3 %) reaches
  0.9075, 0.0116 above `opmax` (p 0.38; one tier), and the exact winner
  ladder's N = 3 rung 0.8993. The HIGH-thinking incumbents (scored on
  their own recorded sheets since PR #42) do not read the repaired legs and
  stay put, so "no new GS F1 high comes from geometry" (R1b-15) is no
  longer true of the point estimates, though the board still has one tier.
- **S9. Four Era-2 members move on today's code without the repair.** Tier
  E's K = 1, 3, 5 rungs of the grid 384/50 ladder (and the K = 1 carried
  cell) score +0.0133 to +0.0141 F1 higher under today's per-tile
  machinery than their committed evaluations of 2026-09-12 (K = 1 0.8546
  → 0.8680; today's `evaluate_detections.py` agrees, with tile MCC
  unchanged), and they are the only board members whose recomputed F1
  departs from their evaluation. Their detection files carry `source_tiles`
  lists, so this is D50's origin attribution reaching evaluations never
  re-scored under it. It makes ORIGIN miss the committed Era-2 tiering
  (7,961 → 8,014 significant pairs; the grid 384/50 cell tier 2 → 3) and
  tier E's ladder (K = 1 against K = 10 no longer significant in ORIGIN),
  and it moves R3-14's "40.6 %" before any repaired row enters. The
  committed board's ranking column shows those cells' old evaluation F1
  while its tests use the new tables (§ 3.1). The K-ladder Phase 2 cells
  were not checked for the same drift (§ 7).

## 6. Integrity

- **Two runs per reading, byte for byte.** `extract/originA.json` equals
  `originB.json` on all 249 keys, and `repairedA.json` equals
  `repairedB.json` on all 249. File by file over each copy's `results/`
  tree (439 files; `rescore-repaired-gs-scripts/cmp_tree.py`, ignoring
  only keys named `timestamp`, `generated_at_utc`, `generated_at` and the
  copy's own root path): 384 byte-identical, 30 identical after that
  normalisation, and 25 `evaluation.md` renders that differ only in their
  `**Generated**` line (checked by diff with that line removed), in both
  readings (`rescore-repaired-gs-scripts/records/integrity-*-results.txt`,
  `records/integrity-md.txt`).
  The board and ladder outputs (37 files; 4 `evaluation.md` renders differ
  only in their `**Generated**` line) and the bridge outputs (73 of 73
  byte-identical) agree the same way (`records/integrity-*-board.txt`,
  `records/integrity-*-bridge.txt`).
- **ORIGIN reproduces PR #42's reported "after" values exactly**: all 155
  keys this extract shares with PR #42's own run-A extract
  (`reports/s163-agent-records/origin-gap-grid-plateau-scripts/records/runA.json`)
  are equal, the HIGH N5 rung (0.8348) and the new HIGH N3 − N10 test
  (−0.0305, p 0.0022) among them.
- **Today's `main` reproduces PR #41's NEW H13 outputs**: the tier-0
  sweep (29 files), the K-sensitivity diagnostic, and the tile-size grid
  (59 files), re-run from the branch worktree into scratch, equal PR #41's
  `out/new1/` byte for byte except `generated_at_utc`, and run A equals
  run B the same way (`records/integrity-h13.txt`).
- **The registered points**: in ORIGIN every regenerated sweep's row at a
  registered condition's point equals the committed value (18 of 18
  `regpoint/*` keys, F1 and count).
- **Kernel memory errors** (sapphire has no error-correcting code memory):
  `journalctl -k -b | grep -c "Bad page state"` read 0 at 12:47 UTC before
  the chains and 0 at the end (`records/bad-page-count.txt`).
- **An incident, repaired and re-run.** The first ladder stage re-extracted
  committed files into each board copy, including the grid 384/50
  member's detection set, after the Era-2 tiering had loaded its cells
  (about 14:00 UTC) but before the two MCB runs read them (about 15:00). The
  set was restored from the chain copy, every moved member's board-frame
  evaluation was checked unchanged, and both MCB runs were repeated
  (`board_mcb.sh`); the ladder stage now restores the set after its archive
  step and re-scores tier E's own K = 10 evaluation. The MCB counts above
  are from the repeat (they equal the first run's); the tiering was not
  affected.
- **What is not a byte check**: the four Gemini 3.7 cells whose ORIGIN
  argmax moved were attributed by a legacy control (S2), not by a
  byte comparison against a committed file, because the committed files
  predate the origin route.

## 7. What was not done

- **No restatement.** No committed result, document, register row, or
  signature was touched; every "after" lives in scratch and in
  `rescore-repaired-gs-scripts/records/`.
- **The null-exemplar sensitivity analysis was not re-run.** Its pipeline
  re-scores every cell of four boards on reduced frames; only the Era-2
  board's ten moved cells read the repaired legs. Its signature test, the
  per-cell deltas, and the reduced-frame tiers are exposed through those
  ten cells (four image-bearing: the two 3.7 image arms and Image-B
  MINIMAL and HIGH; six text). Re-running it is a separate, heavier job.
- **The uplift tables were not regenerated by their own scripts.**
  `verifier-uplift-pairing`'s statistics were recomputed by substitution
  (`uplift.py`): the 21 grid-common verified values at their registered
  points from this re-score, and the twins either as committed or on the
  origin route (S3). `uplift-supplement-flatten`'s counts do not depend on
  the moved values.
- **The bridge's floors and verifier SD** (`modality_bridge_floors.py`,
  `modality_bridge_verifier_sd.py`; findings §§ 5–7a) were not re-run:
  § 3.3.
- **The K ladder's Phase 2, 55-map, and tension sections** read no
  affected leg and were not re-run; only the two gold-standard ladders the
  wrong-sheet legs feed were (§ 3.2). The 3.7 GS text ladder has no
  admissible set (three rungs withheld by the tile-join invariant, as
  committed); its K = 5 and K = 10 rungs are the Era-2 members of § 3.1.
- **The 55-map image campaigns' GS calibration analyses**
  (`results/gemini37-image-55map-2026-09-13/gs-calibration/`,
  `results/gemini3-image-55map-2026-09-16/gs-calibration/`) read the
  re-verified K = 3 arms but are not among the 14 signed analyses and were
  not re-run.
- **The temperature probe** reads re-verified rows in all eight legs; it
  is unregistered and was not re-run.
- **The 3.7 GS text ladder's opmax rungs** (`derive_g37_gs_opmax_rungs.py`,
  `results/k-ladder-2026-09-12/phase2/g37-opmax/`) were not re-derived: its
  committed-count cross-check refuses under the repaired reading, by
  design (§ 1).
- **S9's drift was checked only on the Era-2 board's members**: the
  K-ladder Phase 2 cells, the tier E cells' own evaluations, and other
  evaluations committed before D50 were not swept for it.
- **The selection-aware intervals** (`results/selection-aware/`) were not
  re-run.

## 8. For the PI

1. **Merge the routing PR?** It changes which legs every GS reader reads
   by default. Before it merges, `main`'s GS readers still read the blind
   legs. Two design choices to confirm: the instrument gates that read the
   legs as run (§ 1), and that registration-time scripts keep their
   committed-count gates.
2. **Publish the restatements?** The numbers are in §§ 3–4. The two
   verdicts that fail (S5: overlap at 384 px; S6: I3's carried limb), the
   two 30 m sentences, and the Phase A paragraph need new wording; every
   lapsed signature (Bottom line, item 6) needs re-signing on the new text.
3. **Which reading does a registered condition take when its argmax
   moves?** The analyses re-select their best point; the registered
   conditions are named by theirs. In REPAIRED two registered points are no
   longer the argmax: 384 px / 12.5 % (registered (0.20, k7), now best at
   (0.15, k7): 0.8752 against 0.8761) and 512 px / 34.4 % (registered
   (0.15, k6), now (0.15, k7): 0.8714 against 0.8718), and the 3.7 image
   carried arm (S6). This record reports both; the Era-2 board and the
   uplift tables use the registered points.
4. **The uplift twins** (S3): regenerate them on the origin route, as
   PR #42 did for the boards? Doing so turns one uplift negative.
5. **The null-exemplar analysis** (§ 7): re-run it on the repaired board,
   or record the exposure?
6. **The bridge's floors and verifier SD** (§ 3.3): re-run with the
   re-verified rows?

## Changelog

### 2026-10-13 — Original publication

First version: the reader routing (`9c843b980`), the re-score of every
generator the 14 signed analyses downstream of the wrong-sheet legs read,
in two ORIGIN and two REPAIRED copies on sapphire, the Era-2 board and the
two gold-standard K ladders re-tiered, the bridge cells re-scored, and the
PR #37, PR #41, and A-07 confirmations. No committed output changed.
