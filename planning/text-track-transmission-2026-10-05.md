# Text-track transmission gap: claims, surprises and work plan

> **Last revised**: 2026-10-05 (original publication, Session 160). See
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

### W2. The retest-era bootstrap

- [ ] W2.1 Diagnose: how the retest bootstrap resamples (pairing, the unit
  of resampling, the statistic) and why it rejects between replicates.
- [ ] W2.2 Inventory every claim tested with it (W3 found H4's six:
  `pairwise-bootstrap-comparisons.json` `[55]-[60]`, p 0.124 (H4's
  confirmatory input), 0.678, 0.138, 0.158, 0.002, 0.046; on the board's
  permutation 0.137, 0.640, 0.122, 0.186, 0.002, 0.056, so
  "config-default > random" does not survive) (retest summary, findings,
  decisions, errata, Obs, paper).
- [ ] W2.3 Calibrate: run the bootstrap and the paired permutation test on
  every replicate set the project holds (S-2 and § B.5 of the report);
  measure each test's false-positive rate.
- [ ] W2.4 Decide (PI): re-test the inventoried claims with a calibrated
  test, on sapphire; report which conclusions change.

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

## 5. Also open (from the same session)

- [ ] The X1 signature note on the r2 board (D33): text drafted, awaiting
  the PI's approval; the board refresh is written on sapphire, uncommitted.
- [ ] The register-repair PR (D30-D41): audit, then merge.
- [ ] The manipulation check as a maintained tool: promote
  `reports/manipulation-check-2026-10-05-scripts/` to a tested script and a
  guard (map-reader-bench is designing the same gate).

## Changelog

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
