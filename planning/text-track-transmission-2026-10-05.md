# Text-track transmission gap: claims, surprises and work plan

> **Last revised**: 2026-10-05 (Session 161: X1 approved and recorded). See
> [§ Changelog](#changelog) for revision history.

**Status: OPEN.** The PI's working document for the finding of 2026-10-05:
"a major issue, I'm happy you uncovered it now". Every affected claim, every
surprise and every task is listed here and ticked off as it is handled
(`[x]` with a date, never deleted). Evidence base:
`reports/manipulation-check-2026-10-05.md` (all 44 registered runs, 426
arms, 2,867 metas) and Obs 496 (`docs/notes/working-notes.md`). Rulings go
in `planning/pi-decisions-2026-09-20.md`.

## 1. The finding

- **What a text-only request sends.** The detection runner
  (`scripts/4_detect_mounds_batch.py`, lines ~925-960; the batch builder
  `scripts/lib_batch_api.py` likewise) sends NO example when a configuration
  sets `include_example_images: false`: no image, no label, no text
  description. A text request is the system instruction, two fixed
  sentences and the tile, a zero-shot request: 1,502 input tokens with the
  standard instruction, in every one of 1,042 metas that record per-request
  tokens. An image request sends each example as a short label then its
  image (about 1,090 tokens each).
- **Why it misled.** Every text-only configuration still LISTS examples (7
  to 41, inherited from base configs). The list is read by nothing that
  sends. The second fixed sentence still asks the model to match "the
  above Reference Examples", which are not there.
- **What the registration says.** Brief-text is "Text-only with concise
  symbol descriptions" (`osf/preregistration.md:415`): the pipeline did
  what was registered. The descriptions written since, and three
  experiments, assumed otherwise.
- **The image track is unaffected**: its library, ordering-by-code and
  pool manipulations reached the model (report § D).

## 2. Claims affected

Kind: **D** = direction (void or withdraw), **S** = strength (survives,
weaker), **L** = labelling (conclusion stands, description wrong). Workstream
in brackets (§ 4).

### Null manipulations

- [ ] **C-01 (D, W1).** `results/retest/retest-production-summary.md:23`,
  `:94-104` (§ 5.2), `:240-244` (§ 11.4): "scale-4 > plus-hp on text
  (ΔF1 = +0.013, p = 0.001)". The Phase 2c text arms are identical
  requests; withdraw.
- [ ] **C-02 (L, W1).** Same file `:30`, `:302`, `:316`, `:320`: "null on
  both tracks". Only the image track tested H8; drop "both tracks".
- [ ] **C-03 (D, W1/W2).** `results/retest/pairwise-bootstrap-comparisons.json`
  `comparisons[40-49]` (Phase 2c T2): ten replicate contrasts reported as
  library tests; `[45]` significant (p 0.001) between identical requests.
- [ ] **C-04 (L, W1).** `docs/paper/results-draft.md:192-215` and
  `docs/paper/results-claims-inventory-2026-09-12.md:360/363/366` (R2-01,
  R2-04, R2-07): the 36 Era-1 single-pass cells are 26 transmitted
  configurations; the 15-cell Tier 1 is 9; six Tier-1 cells are one text
  configuration. (The "23 (7)" alternative is withdrawn: W3 showed the
  orderings transmitted.)
- [ ] **C-05 (L, W1).** `results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.{md,json}`;
  analyses `era1-single-pass-baseline-matrix`, `era1-leaderboard`
  (`results/run-analyses.json`, both SIGNED): five Phase 2c text cells
  ranked as distinct configurations. No tier is driven by a replicate
  difference on that instrument (none of 20 replicate pairs significant).
- [ ] **C-06 (L, W1).** `protocol-errata.md:4262-4275` (E81 table): five
  Phase 2c text conditions listed separately.
- [ ] **C-07 (D, W1).** Experiment E: `results/phase3d-experiment-e-results.md:101`,
  `:122` (Finding 2) void; Obs 156 void (Obs 496 corrects it).
- [ ] **C-08 (S, W1/W5).** Obs 155 (`working-notes.md:2757`) and Obs 157
  (`:2877`): real manipulations, each one 60-tile run inside a 0.050
  replicate spread; unsupported as stated. Obs 158 (`:2917`) weakened.
- [x] **C-09 (S/D, W1).** DONE 2026-10-05: dated notes added at both. `docs/paper/discussion-seeds.md:528-531`
  (strength) and `:553-556` (direction unsupported): Experiment E
  citations with no dated note yet.
- [x] **C-10 (S).** `docs/paper/discussion-outline.md:293-297`: dated D40
  note added 2026-10-05 (`ac42e456a`).

### Descriptions of what the text condition sends

- [ ] **C-11 (L, W1).** `docs/paper/methods-draft.md:524-530`: "presented
  as images, text descriptions, or both". Text-only sends none; only the
  verifier's `-text` configs send text (six labels). Correction drafted in
  the report § E.
- [ ] **C-12 (L, W1).** `methods-draft.md:497-502` and `:756`: "the
  twenty-two text-only configurations carry them as labels alone" should
  read "transmit no exemplar at all".
- [ ] **C-13 (L, W1).** `methods-draft.md:577-588`: says Track 2 skipped
  Phase 2c; the Era-1 retest ran it (five inert arms) and Phase 2d.
- [ ] **C-14a (L, W1).** `scripts/analyse_null_exemplar_sensitivity.py:485`
  still writes "sent the labels only" into its `analysis.json` note; correct
  it at the script's next run (the findings document it feeds is generated
  and was corrected through its renderer, 2026-10-05).
- [x] **C-14 (L, W1).** DONE 2026-10-05 (E86/E88 annotated by E90; the rest corrected in place with revision trails, plus the modality audit's opening sentence, which framed the factor the same way): "Labels only" wording: `protocol-errata.md:5351`,
  `:5367` (E86), `:5640` (E88); `osf/errata-pointers.md:76` (OSF-facing);
  `results/null-exemplar-sensitivity-2026-09-13/findings.md:43-44`;
  `results/phase2c-carry-forward-parameters.md:16`;
  `reports/null-exemplar-errata-2026-09-13.md:98`;
  `reports/modality-track-audit-2026-09-14.md:367`;
  `decisions-log.md:1159` (Decision 25).
- [ ] **C-15 (L, W1).** `docs/paper/discussion-seeds.md:466-475`: "few-shot
  foundation-model extraction … TEXT-ONLY variant": the text variant is
  zero-shot. (`:492-501` "text specification beats few-shot image
  examples" is correct as worded; its E48 citation is wrong, C-16.)
- [ ] **C-16 (L, W1).** `discussion-seeds.md:499-501`: cites E48 (an HN-count
  correction) for H10/H12 "not executed as intended"; the v2 runs did
  transmit; the retraction is Obs 235.

### Phase 2e, ordering not recorded

- [x] **C-17 (S, W3).** RESOLVED 2026-10-05: the orderings DID reach the
  model (`reports/phase2e-ordering-check-2026-10-05.md`: an offline replay of
  the recorded commit's batch builder gives four requests differing only in
  order; the arms' outputs agree on at most 5 % of tiles against 91-99 % for
  identical requests; the predicted replicate, Phase 2c `plus-hp` ≡ Phase 2e
  `canonical-first`, agrees on 99.7 %). The claims stand; they should cite
  this evidence, say "single run" and "shares Tier 1", and describe
  `canonical-last` as sent (C-24). H4's p-values are W2's (the retest
  bootstrap; the board's permutation agrees H4's primary is null). Was: `results-draft.md:194-196` ("led numerically by …
  `canonical-last`, F1 0.631"), R2-02 (`results-claims-inventory-2026-09-12.md:361`),
  `retest-production-summary.md:25/145/250-251/300/320`, and H4's
  confirmatory input (canonical-first vs canonical-last, p = 0.124,
  `family-bh-fdr-confirmatory`): the ordering is inferred from code at the
  recorded commit, not shown by any artefact.

- [ ] **C-23 (L, W1).** The Era-1 retest's Phase 2b, 2c and 2d ran their image
  arms in canonical-first order (their study YAMLs set `fixed: ordering:
  canonical-first`, honoured by the batch runner since `ead94aa81`), where the
  February 60-tile runs used config order. No erratum records it; the retest
  summary's "baseline used in all prior phases" and "reused from Phase 2c" are
  wrong (W3.2).
- [ ] **C-25 (D, W1/W2).** Re-tested with the paired tile-swap permutation
  test (`reports/retest-bootstrap-check-2026-10-05.md`): A[45] (2c text
  scale-4 > plus-hp) 0.001 → 0.0588, the only verdict that flips after
  within-phase BH; at raw α also A[18] 0.042 → 0.0588 and A[60] (2e
  config-default > random) 0.046 → 0.0563, which voids "config-default
  significantly beats random" (`retest-production-summary.md:145`). The D17
  audit (`reports/d17-inventory/d17-inventory-h5-h8.md:905-919`) and E69
  reason from single-run differences in the same way. UNCHANGED: H7, H4, H5,
  the family rejection set {H2, H3, H7}, A[1] (E68's basis), all 33
  grid/stride/H13 rows, the verifier-thinking contrast (Obs 187, E69).
  Not re-tested: the 384-vs-512 and PV pairwise files (inputs moved), H1,
  the E45 companions.
- [ ] **C-26 (L, W1).** Reporting errors whatever the test: "FDR p = 0.004" is
  a raw p (`results-draft.md:231` and 24 other sites); "6/10 significant" is
  5/10.
- [x] **C-27 (D, W6).** DONE 2026-10-05 (S161, D42 implemented; `reports/d42-implementation-2026-10-05.md`): no live path reads p from a bootstrap, and the floor-pinning tests now assert p = 1 for identical arms. Was: the bootstrap p-value (2 × min(P(d ≤ 0), P(d > 0)),
  floored at 1/B, read off the uncentred distribution) is still live:
  `scripts/lib_advanced_metrics.py:1945-1955` and four other code paths;
  `tests/test_e45_bootstrap_pairings.py:71-89` pins identical arms at the
  floor. It also depends on which arm is labelled A (0.001 one way, 0.012
  the other on the same data).
- [ ] **C-24 (L, W1).** `canonical-last` was sent as null×3, hard positives,
  then canonical examples last, not the study YAML's [HP, null, C+, C−].
  Canonical placement, what the registration fixes, holds.

### Labels and register

- [x] **C-18 (L, W4).** DONE 2026-10-05: relabelled `text`; `outputs/gs` added to the checker's `POOL_ROOTS`. `gold-standard-v2::verified-v1` registered `image`;
  it sent six text labels (`verify_adversarial-text`, 1,792 tokens per
  request). `scripts/derive_condition_modality.py` cannot catch it
  (`POOL_ROOTS` never resolve `outputs/gs/`).
- [x] **C-19 (L, W4).** DONE 2026-10-05: the register note and the repair report corrected. `results/run-conditions.json` (proposer-verifier-384
  note) and `reports/register-repair-2026-10-05.md:22` call the `-v2` and
  `v1-prompt` legs "identical re-runs"; they sent different exemplars
  (text 1,727 vs 1,792 tokens; image 9 vs 6 images). Same for pv-512.
- [ ] **C-20 (L, W4).** Obs 280's table (`working-notes.md:13683`) labels
  `h4-canonical-last` "text"; it transmits 13 images.
- [ ] **C-21 (L, W1).** `retest-production-summary.md:320` says "Gemini 2.0
  Flash"; every retest meta records `gemini-3-flash` (with the retest
  summary's W2 revision). E51 (`protocol-errata.md:1629-1636`) said the
  scale-8 run was "not re-launched"; its metas show a fresh run. E51 half
  DONE 2026-10-05: annotated (the H8 v2 analysis already recorded the fresh
  run).

- [x] **C-22 (L, W4).** `results/k-ladder-2026-09-12/phase2/unions.json` labelled
  `pv-diag-384::scale-4-optimal-487` (an image pool, 13 exemplar images)
  `text`: its builder was corrected on 2026-09-14 but the output never
  regenerated. DONE 2026-10-05 (`eb6d797e0`): regenerated with
  `--check-only`; row 28's count also moved 757 → 759, the 3.7 screen K = 3
  union having been rebuilt after 2026-09-12. Found by running the modality
  checker, which now passes with no mismatch anywhere.

## 3. Surprises

- **S-1. The retest-era bootstrap is anti-conservative.** It gave p = 0.001
  between identical requests (C-03); the board's paired tile-swap
  permutation test gives p = 0.0588 for the same pair, and none of its 20
  replicate pairs is significant. Every retest-era claim tested with that
  bootstrap is suspect until re-tested (W2).
- **S-2. Run-to-run spread is large at small n.** Identical requests:
  0.050 F1 (Experiment E, 60 tiles); 0.597-0.609 F1 across six runs of one
  configuration (Phase 2c/2b text, 340 tiles).
- **S-3. Phase 2e's orderings are in no artefact** (W3).
- **S-4. The converse error**: a "replicate" that was not one (C-19).
- **S-5. A known-meaningless test was run and reported.** Decision 16
  (`decisions-log.md:737-738`) had called Phase 2c text "meaningless"; the
  February programme skipped it; the March retest ran it and reported it as
  a library test.
- **S-6. Thinking on Gemini 3.1 Pro is unconfirmed.** Pro HIGH metas
  record 0 thought tokens, Pro MEDIUM 6-43 per request (unverified: a
  usage-reporting gap or a dispatch failure).
- **S-7. The text prompt asks for absent examples**: "match the above
  Reference Examples" with none above (report § E).
- **S-9. One transmitted signature, two dates, different outputs.** Two
  replicate groups are not exchangeable across executions: `n1-outstanding`
  `image-t03` (F1 0.590-0.594) against `pv-diag` `image-n5` T = 0.3
  (0.548-0.570), and `n1-outstanding` `pro-image-high-t0` (0.540-0.548, about
  745 detections) against `pv-diag` `flash-high-image` T = 0.0 (0.476-0.487,
  about 890). Both tests reject 67-69 % of their cross-execution pairs and
  none within an execution. Cause unverified: serving drift between dates,
  or a request difference the signature does not record; for the second,
  E57's "intended Pro, dispatched Flash" should be re-checked (W7.5).
- **S-10. The tile-swap test compares two outputs, not two configurations.**
  It treats each output as fixed, so it rejects genuinely different outputs
  of one configuration: on the 55-map set, 4 of 20 within-execution pass
  pairs at 20 m. Configuration-level claims need the run-to-run variance
  (the drift floors of D4 and D8 do this for some claims; W2.5).
- **S-11. The registered pre-holdout OSF deposit was never made**
  (found 2026-10-05, S161; W8.4). The "exact ordering for each
  condition" it promised is what W3 had to reconstruct from code (S-3).
- **S-12. The February pseudo-p was conservative** (found 2026-10-05, S161,
  D42 re-test). Its "0.05 minus the CI bound" construction under-rejected:
  four 60-tile contrasts pass BH on real p-values that it never declared
  (Phase 2b text T0.3 > T1.0 and T1.0 > T1.3; Phase 2e config-default and
  canonical-last > random). No carry-forward rested on them; prose calling
  them null needs checking (W1).
- **S-8. 384 and 512 px tiles cost the same input tokens** (1,502): a fixed
  image-token budget whatever the tile size (relevant to how tile-size
  results are read).

## 4. Workstreams

### W1. Documentation, from metadata to paper

Order: metadata and register → low-level records → intermediate documents
→ paper text, so each layer cites a corrected one.

- [ ] W1.1 Metadata and register labels (W4's fixes land here first).
- [x] W1.2 A new erratum stating what a text-only request sends, correcting
  E86's and E88's descriptions (the originals stay as written) and
  recording the Phase 2c text null; OSF pointer updated. Done 2026-10-05:
  **E90** (`dbc59c046` on main). For the PI: re-upload
  `osf/errata-pointers.md` if it is on OSF.
- [ ] W1.3 Low-level records: withdraw C-01/C-02 in the retest summary
  under the revision policy; annotate `pairwise-bootstrap-comparisons.json`
  (C-03); the "labels only" sentences (C-14); E51 and "Gemini 2.0" (C-21).
- [ ] W1.4 Intermediate: a new Obs for the Phase 2c null and the bootstrap's
  false positive; decisions-log note (Decision 25); signature notes on the
  two signed Era-1 analyses if their outcome text needs one (C-05).
- [ ] W1.5 Paper: methods C-11/C-12/C-13; results C-04/C-17; discussion
  seeds C-09/C-15/C-16; claims inventory rows. Drafted for the PI's review.

### W2. The retest-era bootstrap — W2.1-W2.3 DONE 2026-10-05; W2.4 for the PI

Report: `reports/retest-bootstrap-check-2026-10-05.md`. Mechanism: the p-value
read off an uncentred bootstrap sits at its floor whenever two arms differ on
few tiles in one direction (identical outputs too). False-positive rates on
10,035 replicate pairs: 2.5 % (bootstrap) against 2.2 % (permutation) overall,
but 12.5 % against 6.2 % where the outputs differ on 50 tiles or fewer (the
T = 0 case). The re-test took under 30 minutes on sapphire.

- [x] W2.1 Diagnose: how the retest bootstrap resamples (pairing, the unit
  of resampling, the statistic) and why it rejects between replicates.
- [x] W2.2 (107 contrasts at about 740 sites; 30 reach paper text) Inventory every claim tested with it (W3 found H4's six:
  `pairwise-bootstrap-comparisons.json` `[55]-[60]`, p 0.124 (H4's
  confirmatory input), 0.678, 0.138, 0.158, 0.002, 0.046; on the board's
  permutation 0.137, 0.640, 0.122, 0.186, 0.002, 0.056, so
  "config-default > random" does not survive) (retest summary, findings,
  decisions, errata, Obs, paper).
- [x] W2.3 Calibrate: run the bootstrap and the paired permutation test on
  every replicate set the project holds (S-2 and § B.5 of the report);
  measure each test's false-positive rate.
- [x] W2.4 RULED 2026-10-05 (D42): the paired tile-swap permutation test with
  BH for every contrast; no p-value read from the bootstrap (CIs only).
- [ ] W2.6 IMPLEMENT D42. CODE, REGENERATION AND FINDINGS DONE 2026-10-05
  (S161; `reports/d42-implementation-2026-10-05.md`): seven paths converted
  (the five W2 named, the February pseudo-p, and the retest evaluator's
  uncorrected CI flag); eight analyses regenerated, the March pairwise file
  and nine retest evaluations annotated, the February 60-tile instrument
  re-tested; five findings documents updated; tier 1 green (3,750). STILL
  OPEN: the batch signature note on four signed analyses (report § 7, PI);
  class B (two PI choices: B-17's two-file mix, I4's sweep; report § 6);
  the C-25 documentation sites (W1). Was: replace the bootstrap p-value in
  live code (C-27: `scripts/lib_advanced_metrics.py:1945-1955` and four
  other paths; retire the test that pins the floor), apply the re-test
  results (C-25) to every inventoried site, and re-test what W2 could not
  (the 384-vs-512 and PV pairwise files, H1, the E45 companions).
- [ ] W2.7 FOLLOW UP S-10 (the PI's "two surprises", 2026-10-05): the
  tile-swap test compares two outputs, not two configurations. Decide how
  configuration-level claims are tested: a replicate-based floor (the D4/D8
  drift-floor pattern) or a test whose null includes run-to-run variance;
  find which paper claims compare configurations from single runs; fix
  them.
- [ ] W2.5 Widen the calibration to every significance test the paper relies
  on (added 2026-10-05 at the PI's request): the board's permutation test
  passed on 20 replicate pairs; the bootstrap CIs, the H-family tests
  (`family-bh-fdr-confirmatory`), the K-ladder tests and any other have not
  been checked against replicates. W2.3's harness serves all of them.

### W3. Phase 2e (H4 ordering) — DONE 2026-10-05

The orderings transmitted (C-17 resolved; C-23 and C-24 found). Report:
`reports/phase2e-ordering-check-2026-10-05.md`.

- [x] W3.1 Look for any surviving record of what the batch jobs sent: the
  batch request JSONL, `batch_jobs.json`, run logs, session transcripts.
- [x] W3.2 Test the code path: does `_reorder_examples_for_batch` at
  `5a57f586e` produce the four orderings for these configs (offline, no API)?
- [x] W3.3 Recommendation: "transmitted" is defensible on code plus output
  evidence; no run is needed for transmission. An optional fingerprint replay
  (4 arms × 40 of the same Era-1 tiles, Batch, about US$0.67; all 340 about
  US$5.6) would pin the exact orders, only if the model has not drifted since
  March: listed for W5.

### W4. Labels

- [x] W4.1 `gold-standard-v2::verified-v1` → `text` (C-18); `outputs/gs/`
  now resolves in `derive_condition_modality.py`; two tier-2 guards (every
  unresolved verifier stage named; no pool-keyed label disagrees). Done
  2026-10-05.
- [x] W4.2 The proposer-verifier-384/512 note and the repair report (C-19).
  Done 2026-10-05.
- [ ] W4.3 Obs 280's label (C-20), by a new Obs (entries are never edited);
  fold into W1.4's Obs.
- [ ] W4.4 The checker still cannot resolve 17 verifier stages (sidecar-form
  metas, a `t0.3`/`t0-3` directory spelling, an archived leg), named in
  `tests/test_derive_condition_modality.py`. Resolve stages from the
  register's own paths, as the passes extractor does, so none is out of
  scope. (The manipulation check covered all 17 by tokens: their labels are
  right today.)
- [ ] W4.5 Regenerate the register for C-18's label (with the next batch).

### W5. Follow-up runs (GS only; each needs the PI's approval and the API gate)

- [ ] W5.1 List the questions we believed answered and are not: e.g. null
  examples in a text prompt (never tested), Experiment E's thinking and
  temperature steps at adequate n, H4 ordering if W3 cannot verify it, Pro
  thinking (S-6), a text-with-examples arm (never run).
- [ ] W5.2 For each: whether it matters to the paper, the smallest GS-only
  design that answers it, and its cost; D10 (no new major runs) applies.
- [ ] W5.3 PI decides.

### W6. Prevention (added 2026-10-05 at the PI's request)

- [ ] W6.1 The manipulation check as a maintained guard: promote
  `reports/manipulation-check-2026-10-05-scripts/` to a tested script that
  refuses an analysis whose arms differ in configuration but not in payload
  (map-reader-bench is designing the same gate; share the design).
- [ ] W6.2 Configuration validation: an inert field is an error, not a no-op
  (first, an example list in a text-only configuration).
- [ ] W6.3 A currency guard for generated outputs: a committed output must
  match its generator run on committed inputs. Two stale outputs surfaced on
  2026-10-05 (the analyses manifest after D25's note; the K-ladder unions after
  their builder's fix, C-22); `reports/verification/generated-file-registry.json`
  may already list what such a guard would cover.
- [ ] W6.5 The in-batch parse-failure retries (`complete_batch_unit` in
  `scripts/lib_batch_api.py`) pass no service tier, so they ran at standard,
  and their usage enters no meta (found 2026-10-05 while fixing the sync patch
  path, `8ae31a585`, which now records its usage). Fix: pass the tier and
  record the retries' usage at their own tier. Past runs' retry spend is part
  of D39's invoice residual.
- [ ] W6.4 Decide (PI) the text prompt's fixed sentence asking the model to
  match "the above Reference Examples" (S-7), before any W5 run: keep it for
  comparability, or fix it.

### W7. Manipulations that leave no token trace (added 2026-10-05 at the PI's request)

- [ ] W7.1 Thinking on Gemini 3.1 Pro (S-6): Pro HIGH metas record 0 thought
  tokens. Establish offline (raw responses, usage fields, the SDK version's
  reporting) whether thinking ran.
- [ ] W7.2 Tile size (S-8): 384 and 512 px tiles cost the same 1,502 tokens.
  Establish the image-token budget the model received (the SDK's
  media-resolution default at each recorded commit) and what that means for
  H11's tile-size results.
- [ ] W7.3 Temperature and ordering are evidenced by configuration and code
  only (ordering now also by output fingerprint, W3): say so where the paper
  relies on them.
- [ ] W7.5 FOLLOW UP S-9 (the PI's "two surprises", 2026-10-05): why two
  executions of one transmitted signature differ systematically, and whether `n1-outstanding`'s "Pro" cells ran Pro after
  all (E57 read the model from a configuration field E57 itself calls an
  unreliable template default; the outputs differ from the Flash cells').
  If they did, correct E57, the register's model labels and every claim that
  reads those cells as Flash; if not, find what differed (serving drift
  between dates bears on every cross-date comparison).
- [ ] W7.4 Each finding feeds W5: no run is designed until W7 says what can be
  verified offline.

### W8. External communications (added 2026-10-05 at the PI's request)

- [ ] W8.1 List what has left the repository with the wrong description of
  the text condition, or a void claim: the OSF errata-pointers page (E90), the
  June colleague summary (`reports/key-findings-summary-2026-06-23.md`), any
  talk, abstract or slide, the participatory-GIS article if it cites this work,
  and map-reader-bench (informed 2026-10-05).
- [ ] W8.2 For each: the correction, and who sends it (outward messages are
  the PI's; Claude drafts).
- [x] W8.3 OSF (next session, before any upload). DONE 2026-10-05 (S161). The project's storage
  (`osf.io/h9x4g`, `preregistration-files/`) was found to hold only the
  31 January upload (the three lodged documents and a 1,686-byte README); no
  `errata-pointers.md` and no E87 tile-count files. The PI expected otherwise
  and recalls several updates to the preregistration. Investigate first:
  check the registration (`osf.io/tybgq`) and its versions or updates, every
  component and other storage of the project, and the newest preregistration
  version in the repository (`docs/methodology/preregistration/`) against
  OSF; the PI will check too. Then act: upload the pointers page (and, if
  confirmed, the E87 files and the current README) to the right place and
  remove any file they supersede. The OSF token is `OSF_API_KEY` in
  `~/personal-assistant/.env` (read by `scripts/check-credentials.py` there).
  INVESTIGATED 2026-10-05 (S161), read-only: `reports/osf-state-check-2026-10-05.md`.
  The project (private, no components) never had more than the January
  set: its log shows no upload after 2026-01-31 and no removal but the
  first-upload set. One registration update exists (2026-02-04, errata
  E1-E16), and it left the form's file field empty. The repository's
  three lodged documents are byte-identical to OSF. Upload waits for the
  PI's own check and his choice of channel (report § 5). PI 2026-10-05: state
  confirmed; project made public; registration update agreed; deposit with
  GitHub commit links. Uploads DONE 2026-10-05 (see W8.4); update 2
  submitted and approved 2026-10-05.
- [x] W8.4 (S-11) DONE 2026-10-05 (S161): erratum E91 (`690154d23`); the
  late deposit uploaded to OSF `late-deposit-2026-10-05/` and SHA-256
  verified (index `osf/late-deposit/deposit-index.md`); the errata pointers,
  E87 files and a new README version uploaded to `preregistration-files/`;
  project made public by the PI. Registration update 2 SUBMITTED AND
  APPROVED 2026-10-05 11:30 UTC through the OSF API (text approved by the PI;
  lodged documents re-attached; `planning/osf-registration-update-2-draft-2026-10-05.md`). Was: the
  registered pre-holdout deposit was never made
  (`osf/preregistration.md:1498-1500`, appendix `:161-167`: library
  manifest, prompt texts, mapping table, image filenames, H9 variants,
  the exact ordering per condition, seeds). No erratum records it. Needs
  an erratum and the PI's decision whether to deposit late (report § 3).

## 5. Also open (from the same session)

- [x] **The X1 signature note on the r2 board (D33): PRESENT IT TO THE PI IN
  FULL next session** (the exchange was lost from his transcript). DONE
  2026-10-05 (S161): presented in full; the PI approved the version with
  points (a) and (b) folded in at 06:06:19Z; refresh written and note
  recorded (`b044c486e`), manifests regenerated (`d35abeef0`); the five
  refresh tests pass (13 passed). Was:
  the board refresh is NOT committed (reverted on sapphire 2026-10-05; it
  regenerates in seconds with `scripts/final_board_cost_refresh.py --write`,
  and changes exactly three cells: TH7-oracle US$207.35 → 210.32, T03-oracle
  261.15 → 263.89, TM-oracle 30.40 → 31.91; tiers and both frontiers
  byte-identical). Context to give: (1) why a note: the board is a signed
  analysis (`55map-final-board-r2-2026-09-06` in `results/run-analyses.json`),
  so a change to what it reports is a dated D9 note the PI approves, the old
  text kept in `history`; this is its third (WP4b re-pricing; D24). (2) Why
  the change: the three text oracle cells (k3) score detections whose 3-of-5
  candidates include the S104 vote-3 increment; their cost counted only the
  main verifier leg; the carried cells (k4) never touched those candidates
  (D33). The draft:

  > SIGNATURE NOTE 2026-10-05 (D9 pattern; re-pricing; ruling D33, approved
  > by the PI ‹timestamp›, Session ‹n›). The TH7, T03 and TM ORACLE cells (k3)
  > now add the vote-3 increment their operating point drew on
  > (`results/deployment-oracle-2026-06-06/vote3-verify/`; register rows
  > `<run>::vote3-increment::run1` since the S160 register repair), at the
  > uniform tier: TH7-oracle US$207.35 → 210.32, T03-oracle US$261.15 →
  > 263.89, TM-oracle US$30.40 → 31.91 (TM's verifier leg stays completed from
  > comparables, †). UNCHANGED: the carried cells (k4), which never used the
  > increment; every other family's cost (the repair moved none); the 35-cell
  > tiering, every F1, MCC, tier and group; and both efficiency frontiers'
  > membership (D24). The signature of 2026-09-17 stands for the tiering; the
  > PI approves the re-priced cost axis as of this note.

  Three points for the PI: (a) add "the board's cost sentence says so": the
  board's prose definition of `cost` ("a run's carried and oracle cells
  share it") was rewritten by the refresh to say the three oracle cells add
  their increment, so the note should say the board's text moved too
  (recommended); (b) optionally name IM and UPL, the other two oracle cells,
  as having no increment (IM's carried and oracle cells are one shipped k3
  cell and no image vote-3 increment was run; UPL's oracle is priced by its
  own verifier leg); (c) the closing sentence is in the PI's voice (the WP4b
  note's formula); his reply is the approval, and its time is recorded. On
  approval: run the refresh with `--write`, add the note to the analysis's
  `signature.attests` with the prior text in `history`, regenerate the
  analyses manifest, commit.
- [ ] The register-repair PR (D30-D41): audit, then merge.
- [ ] The manipulation check as a maintained tool: promote
  `reports/manipulation-check-2026-10-05-scripts/` to a tested script and a
  guard (map-reader-bench is designing the same gate).

## Changelog

### 2026-10-05 (Session 161, later still) — D42 implemented; E91 and the late deposit

D42's code, regeneration and findings are done (W2.6; three items left for
the PI). S-11 is resolved by erratum E91 and a verified late deposit on OSF
(W8.4); registration update 2 is drafted. S-12 added: the February pseudo-p
was conservative.

### 2026-10-05 (Session 161, later) — W8.3 investigated; S-11 found

The OSF state check (`reports/osf-state-check-2026-10-05.md`): nothing was
lost from OSF; the expected files were never uploaded. The registered
pre-holdout deposit was never made either (S-11, W8.4).

### 2026-10-05 (Session 161) — X1 approved and recorded

The PI approved the r2 board's D33 signature note with points (a) and (b)
folded in (06:06:19Z). The board refresh is written (`b044c486e`), the
note is in the board's `signature.attests` with the prior text in
`history`, and the manifests carry it (`d35abeef0`). § 5's first item is
ticked; D33 records its execution.

### 2026-10-05 (session close) — the PI's rulings and hand-offs

D42 ruled (W2.4). The two surprises from W2 (S-9, S-10) are follow-up tasks
W7.5 and W2.7. W8.3 records the OSF investigation the PI asked for before
any upload. The X1 note's full draft and context are kept in § 5 for the
next session.

### 2026-10-05 (night) — W2 investigated

The bootstrap's mechanism, inventory, calibration and re-test: one verdict
flips after BH (A[45]) and one more at raw α (A[60]); C-25 to C-27, S-9 and
S-10 added; W7.5 opened.

### 2026-10-05 (evening) — W6, W7, W8 and W2.5 added

At the PI's request: prevention (W6), manipulations with no token trace (W7),
external communications (W8), and widening W2 to every significance test the
paper relies on (W2.5).

### 2026-10-05 (later still) — W3 done

The Phase 2e orderings transmitted: C-17 resolved, the "23 (7)" alternative
withdrawn, C-23 and C-24 found, and the manipulation-check report's § B.2 and
§ B.5 group 19 corrected.

### 2026-10-05 (later) — W4 labels done; C-22 found

C-18 and C-19 corrected; running the modality checker found C-22 (a stale
generated label in the K-ladder unions), now regenerated. The checker passes
with no mismatch; its 17 blind spots are named and guarded (W4.4).

### 2026-10-05 — Original publication (Session 160)

Written at the PI's request ("let's make sure that we've externalised the
list of claims affected, surprises, and to-dos, then let's work through
them"), from the manipulation check and Obs 496, with the PI's five
workstreams.
