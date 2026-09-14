# Documentation foundation checklist — the preregistration → outcome chain

> **Last revised**: 2026-09-14 (latest — **item 14 closed**: the cleanup
> metadata overwrite fixed permanently. `run.meta.json` now carries the sum
> across the main pass and every cleanup or resume pass, with `main_pass`
> verbatim, a `cleanup_passes` list and a never-overwritten sidecar; a
> cleanup under a changed configuration is refused before any API call; the
> verifier-leg auditor is `scripts/audit_verifier_cost.py`, gated on the GS
> arms' US$0.4417 / US$0.6804. Two findings beyond the brief: the fourth
> cell's overwrite cannot be attributed to `cleanup` (no `cleanup_history`
> survives, and the results-file rewrite that erased it is now fixed too),
> and the retrospective census found **29** affected stages — 3 recoverable,
> 26 not, the fourth cell and its GS leg among them. No committed meta was
> rewritten. Deltas: `reports/cleanup-meta-fix-2026-09-14.md`. Before
> that — 2026-09-13, **item 13 added and closed**:
> errata **E86** (the null exemplars' stale provenance — 25 of the 340
> Era-1 tiles overlap null-exemplar pixels, nil on measurement, image
> modality only) and **E87** (the lodged per-tile mound counts — 36 → 50,
> 79 → 97, and 10 of 20 / 27 of 60 tiles change density stratum) inserted,
> with a manifest-provenance guard, the Methods corrections and
> `osf/errata-pointers.md`, which exists because the lodged registration
> copy turned out to be blob-pinned and line-anchored by 702 commitments and
> so cannot carry inline pointers. Item **13a**, the sensitivity re-score,
> is the sibling session's and remains open. Before that — **items 11a and
> 11b closed**: the
> generated-file registry rebuilt over `outputs/` as well as `results/` and
> `reports/` — 3,619 files, 3,318 generated, 0 unattributed — and extended
> to record the 2026-09-11 ruling's three obligations per generated
> document, so the audit's "six generated documents in neither compliance
> regime" is now a query that returns **0**: the five register renderings
> gained a source commit and a tested `--check-renderings`, and the Era-2
> board's `tiering_20m.md` and `frame-deltas.md` plus the three generated
> 55-map boards gained a banner, a stamp and a tested `--check`, each
> regenerated once with zero content drift. Deltas:
> `reports/generated-file-registry-2026-09-13.md`. Before that —
> **item 9 closed**: five ruled
> markers cleared from the Results draft, so it carries zero open PI
> decisions in its own notes, and the claims inventory extended to
> §§ R1b, R3 and R6 — 181 claims over 10 of 12 blocks → **237 over 12 of
> 12**, 214 VERIFIED / 19 DRIFTED / 1 SUPERSEDED / 3 UNANCHORED, plus **10
> ladder findings verified at anchor that no draft sentence makes**. § R6's
> cost table is one signature behind `pass-budget-pareto-v2` and §§ R3/R6
> drift only by reference vintage. Before that — **item 6
> closed, awaiting PI re-signature**: the Era-2 board rebuilt once carrying all three ruled
> changes, so the PI signs once. The F1 arm reproduced **byte-identically**
> (11,175 pairwise records and the F1 MCB artefact; Tier 1 and its five
> members unchanged); the k3 cell's withheld row and G6 row read **0.8860** /
> 495; ruling 7's tile-MCC family is reported beside the F1 tiering
> (2,982/11,175 significant, 6 MCC tiers, MCC tie set 33, MCC MCB 59 of 150)
> and **disagrees with it systematically** — no F1 Tier-1 cell is in MCC
> Tier 1 and the two admissible sets share 9 members of 65 and 59; ruling 6's
> withheld-cell disclosure carries the shortfall counts and both tile
> vocabularies. Ten signature-bearing paths byte-equal, no signature field
> touched. Deltas: `reports/era2-board-mcc-family-2026-09-13.md`. Before that
> — item 6a closed: the
> tile-join invariant now withholds rather than aborts, the k3 cell's
> evaluation is written at 0.8860 / 495, and `carry_probabilities.py` is
> promoted to `scripts/`; earlier: Batch 1's five documentation items all
> closed — 41 of 41 run reports, verifier 38 pass / 3 partial / 0 fail,
> Obs 477–481, § M.x current to E85 and the 67-row register, the audit
> refreshed; original publication, Session 153, when the PI asked for the
> chain's remaining documentation to be externalised as a checklist). See
> [§ Changelog](#changelog).

**Purpose**: make sure every primary and intermediate document on the
chain preregistration → experiment → result → analysis → outcome is
complete and current, so the paper is written from a closed foundation.
Items are ticked with a date and the commit that closed them; nothing is
deleted. Agent tier per item follows the subagent policy: Opus for all
agent work; Fable only for the PI-facing orchestration turns.

## 1. The chain, link by link (state on 2026-09-13)

| Link | Artefact | State | Gap |
|---|---|---|---|
| Preregistration → hypotheses | `results/hypothesis-outcome-table/` (generated, drift-guarded) | complete: 15 hypotheses, every row with analyses, status, errata | none (paper sentence on H6 not-executed rests on E40/E41/E74) |
| Experiments → runs and conditions | `results/runs-manifest.json`, `results/conditions-manifest.json`, `scripts/verify_run_conditions.py` | 41 runs, 593 conditions all with metrics; verifier ~~22 pass / 19 partial~~ → **38 pass / 3 partial / 0 fail** (2026-09-13, `f4fd90c71` + `e88fd5bfa`) | closed to the annotation limit (§ 2 item 2); the 3 remaining partials are by-design disclosures, and reaching 41 needs a PI verdict-model call |
| Runs → post-run reports | `outputs/**/post_run_report.md` | ~~2 of 36 run directories~~ → **41 of 41** (2026-09-13, `c4edf1328`): 39 generated projections + 2 hand-authored | closed (§ 2 item 1) |
| Results → analyses → signatures | `results/run-analyses.json`; findings documents | 67 rows, 66 signed, 1 unsigned by design; every findings doc bannered | the **Era-2 board is rebuilt** and awaits ONE PI re-signature (§ 2 item 6, done 2026-09-13); the 55-map board still pending its r2 rebuild (§ 2 item 7); the image run's row (§ 2 item 8) |
| Deviations → errata | `docs/methodology/preregistration/protocol-errata.md` (E1–E85) | complete register | **none** — § M.x brought current to E85 and to the S153 rulings, 2026-09-13 (§ 2 item 4) |
| Working notes | `docs/notes/working-notes.md` (Obs 1–481) | current | **none** — Obs 477–481 written 2026-09-13 (§ 2 item 3) |
| Paper-facing | `docs/paper/results-draft.md`, `results-outline.md`, `results-claims-inventory-2026-09-12.md`, `methods-draft.md`, `discussion-outline.md`, `discussion-seeds.md`, `manuscript-skeleton-isprs.md` | outline decisions D1–D22 settled; inventory built for R0–R2, R4–R5, R7–R9; Methods zero-draft; Discussion outline current to August | § 2 items 8–10; D-1..D-5 and D.9 stay DEFERRED |
| The project's own documentation audit | `planning/interim-docs-review.md` (2026-04-22, § 11 re-score 2026-09-13), `docs/methodology/output-directory-standard.md` compliance table (recounted 2026-09-13, May counts kept as history) | refreshed | ~~six generated documents in neither compliance regime, and a stale generated-file registry (§ 11.5)~~ → **both closed 2026-09-13** (items 11a/11b, `86ba12413` + `acd4ed054` + `b16954d4c` + `80e897049`): the registry rebuilt over `outputs/` as well (3,619 files, 0 unattributed, guards recorded per document) and the neither-regime six closed to **0**. Remaining: 11c (`PaperImp` blocks, back-fill on touch) and the 46 `outputs/**/evaluation.md` files named as the ruling's open class |

## 2. Items (tick with date + commit; never delete)

**Batch 1 — $0, Opus agents, can run now**

- [x] **1. Post-run reports for every run directory** — done 2026-09-13,
  commit `c4edf1328`. The gap was **39 of 41**, not 34 of 36: the registry
  holds 41 runs at 41 distinct directory paths, all present and tracked,
  and 2 carried a report. Taken via the GENERATED-PROJECTION route the
  2026-09-11 ruling opened — 39 reports emitted by the new
  `scripts/generate_run_reports.py` with a GENERATED banner, a
  source-commit stamp and a `--check` drift guard run by a tier-1 test,
  rather than 39 hand changelogs that would each go stale at the next
  manifest rebuild. The 2 hand-authored narrative reports were NOT
  overwritten (their Dawid-Skene corrections and paired comparisons are
  not re-derivable from the manifests) and took the banner + Changelog
  instead — which corrected the standard's "2 compliant" cell, since
  neither had carried either. Deltas:
  `reports/documentation-batch1-deltas-2026-09-13.md` § 2.
  Anchor: `docs/methodology/output-directory-standard.md`
  § "Documents in Revision Policy Scope" (scope table and changelog
  updated in the same commit).
- [x] **2. Resolve the 19 partial runs** — done 2026-09-13, commits
  `f4fd90c71` (verifier) and `e88fd5bfa` (annotations). Verifier
  **22 pass / 19 partial → 38 pass / 3 partial / 0 fail**; 221 open WARNs
  → 12. Cleared: 115 `pool-unresolved` by `source_run` annotation across
  seven runs (each with its filesystem or authoring-script anchor), 13
  `unclaimed-eval` by `_ignored_evals` waivers with reasons, and 81
  instrument false positives by two verifier corrections — 79
  `geojson-missing` that were directory-valued detections (aggregated
  multi-pass cells, all present) and 2 `pool-dir-not-found` that were
  materialised pool files. No metric, evaluation, detection or threshold
  changed; every runs/conditions/passes manifest row is identical modulo
  extraction timestamps.
  **Target was 41 pass; 38 is the honest maximum by annotation.** The
  remaining 3 runs hold 12 WARNs that are by-design disclosures the
  project has already settled — `n-passes-over` on
  `55maps-text-min-n10-uplift` (the mixed-provenance pool's "honest
  by-design signal", S106) and `pinned-vintage` on `e47-propose-brief`
  and `n1-outstanding-384` (ruling 3a, raised only when the pin CHECKS
  OUT). Clearing either would delete a disclosure. **Open for the PI**: a
  verdict-model change — a third `disclosures` list beside
  `discrepancies`, with PASS defined over `discrepancies` alone — would
  reach 41 pass without losing the disclosures, but it changes what a
  signature attests, so it was flagged rather than done
  (`reports/documentation-batch1-deltas-2026-09-13.md` § 3.4).
- [x] **3. Obs for the 2026-09-12/13 findings**: the tile-join class (a
  metric keyed by a name beside one keyed by geometry; overlapping frames);
  the recovery-fragment class (a count can hold while the set changes; a
  fragment can lower the count); the verifier-stage reversal of tile-MCC's
  response to K; the MCB-versus-greedy disagreement in both directions;
  the AUD-against-USD corroboration. Owner: obs-writer (Opus).
  **Done 2026-09-13, `79a4d3c0e`** — Obs 477–481, next free number
  collision-checked (max was 476, nothing at 477+), no existing entry
  edited.
- [x] **4. Methods amendments section currency** (`docs/paper/methods-draft.md`
  § M.x) to E85 and the S153 rulings (generated projections; the
  name-based tile join as published convention; the carried-point
  convention). Owner: Opus agent.
  **Done 2026-09-13, `34c6d4be0`** — errata E78 → E85 (composites 26 → 33,
  the defensible range 18–30 → 18–31, bare tallies unchanged); register
  32 → 67 rows with the 66-signed / 1-unsigned-by-design layer; E82 and
  E83 added to the registered-inference disclosure; the three S153
  conventions carried with inline anchors. One stale claim corrected —
  H13 is registered-exploratory **with a result**, not silently dropped,
  so § M.x had been contradicting the generated hypothesis-outcome table
  it vouches for.
- [x] **5. Refresh the project's documentation audit**: re-run the
  interim-docs scorecard against today's inventory and update the
  output-directory standard's compliance table with current counts.
  Owner: Opus agent.
  **Done 2026-09-13, `d52ec49af`** — `planning/interim-docs-review.md`
  § 11 (the April scorecard untouched); the compliance table recounted
  with the May counts kept as history. Headline: two compliance regimes
  now, and six generated documents sit in **neither** — two of them the
  Era-2 board's own tiering and frame-delta tables, plus all 46
  `outputs/**/evaluation.md`, which that row is reclassified to.
  Feeds item 11: rebuild
  `reports/verification/generated-file-registry.json` first (last built
  2026-08-20 at `06f7b8ea5`, and it does not enumerate `outputs/`).

**Batch 2 — after the image run lands ($0 except as noted)**

- [x] **6. Era-2 board rebuild and re-signature** — **DONE 2026-09-13,
  AWAITING PI RE-SIGNATURE**, commits `30a27f361` + `c1285136d` +
  `736c39c0e` (the MCC family in the instrument and the builder, 18 tier-1
  tests), `b3c56a221` (the rebuilt board), `a7ab9c1c0` (the generated
  reports and the hypothesis table regenerated, zero content drift),
  `9a440644d` (the board README's banner and changelog), `fc0aaf38f` (both
  cards), `ab1f33fd3` (the deltas report). One rebuild carried all three
  ruled changes so the PI signs **once**: the four re-scored cells at their
  current evaluations (`g37-text-k3-verified-opmax` 0.8870 → **0.8860** /
  495 in the withheld table and in G6, its committed tile-MCC no longer
  quoted because its own re-scored artefact withholds the tile block at
  source; the two K = 1 cells and tier E's K = 5 unchanged, nothing
  re-scored here), ruling 7's tile-MCC permutation family, and ruling 6's
  withheld-cell disclosure. US$0, no API call, all compute on sapphire.
  **The F1 arm reproduced byte-identically** — `ranking`, `tiers`,
  `tie_set` and all **11,175** pairwise records identical to the committed
  run (blob `f2f1af55a`), the F1 MCB artefact identical too, **Tier 1 and
  its five members unchanged**, 7,961/11,175 significant, 14 tiers, tie set
  5, MCB 65 of 150 (w_upper 0.0749), G2 0 / G3 0 / G4 110 / 110, G6 max
  |delta| 0.0078. Record:
  `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/rebuild-mcc-2026-09-13/f1-arm-identity.json`.
  **The MCC family is the finding, not the formality**: 2,982/11,175 pairs
  significant, **6 MCC tiers**, **MCC tie set 33**, **MCC MCB 59 of 150**
  (w_upper 0.0828) — and it ranks the board almost the opposite way.
  **No F1 Tier-1 cell is in MCC Tier 1**; MCC Tier 1 is 33 cells drawn
  entirely from F1 tiers 6–12, led by single-pass **image** proposer +
  verifier baselines (`verified-adv-image-baseline-pro-vf`, tile-MCC 0.8887,
  F1 rank 119 of 150); the two admissible sets share **9** members of 65 and
  59 (union 115 of 150); the MCC argmax is unstable at this resolution
  (stability 0.420, 36 distinct winners, against F1's 0.602 / 22). Reported
  BESIDE the preregistered F1 tiering and NOT replacing it, per ruling 7 —
  the board's tiering, ranks and Tier 1 remain the F1 ones.
  **Signature discipline**: `signed_at`, `signature_history` and
  `gates.G1.pi_ruling` carried forward, the previous PENDING block nested as
  `previous_pending` rather than overwritten (a gap this job closed), and
  **10 signature-bearing paths asserted byte-equal** before and after,
  register file included — `rebuild-mcc-2026-09-13/signature-paths.json`,
  PASS. No signature field altered; the signed analysis row not written.
  **Open for the PI**: the re-signature itself
  (`provenance.json` → `re_sign_pending`, whose `proposed_outcome` states
  both families and their overlap), plus a paper-facing call on which
  ranking the Results section leads with. Deltas:
  `reports/era2-board-mcc-family-2026-09-13.md`.
  - [x] **6a. Prerequisite** — done 2026-09-13, commits `3eeaf96f4`
    (scorer + 8 tier-1 tests), `987534c03` (the rebuilt 495-detection set,
    the 494 archived), `a8c03bb9e` (the re-score), `977df2995` (manifests
    and two renderers), `d2dd9539c` (board note resolved), `88e9f7cd3`
    (`carry_probabilities.py` promoted, 13 tier-1 tests). The invariant
    now **withholds** a refused cell's per-tile table, tile confusion,
    tile-MCC and every bootstrap interval — recording the named reason,
    the shortfall counts and both tile vocabularies in the evaluation
    JSON, CSV and Markdown — and lets the buffer-matched F1, precision and
    recall **point estimates** proceed.
    **The bootstrap is withheld with the tile block, and that was measured
    rather than assumed**: `bootstrap_ci` resamples TILES (Decision 10;
    `_metadata.bootstrap.resampling_unit` says so in every artefact), not
    matched pairs, so the refused per-tile table is its input too. The card
    anticipated "F1 and its bootstrap proceed"; a refused cell has a point
    and no interval, and the cell's previous interval is **withdrawn**, not
    superseded.
    The k3 cell reads F1@20 **0.8860** / **495 detections** (from 0.8870 /
    494; precision 0.8340 → 0.8323, recall 0.9471 unchanged — the added
    detection is a false positive), and `results/conditions-manifest.json`
    matches. **Regression**: tier E's K = 5 cell, re-scored on its own
    recipe, is dict-identical in summary and byte-identical in CSV and
    Markdown to what is committed; the two K = 1 cells are untouched; a
    matched synthetic cell reproduces a golden captured at `35dd1f254`
    byte for byte. Board **not** rebuilt or re-tiered: the `re_sign_pending`
    note already carried the k3 line, and its `blocked_artefact` claim was
    replaced by a `resolved` record under a 16-signature-path byte-equality
    guard. Two figures still reading 0.8870 — the board's `withheld_cells`
    row and `re_sign_pending.proposed_outcome` — are signature-bearing and
    left for the PI to restate at the rebuild.
    **Raised for the register's owner, not actioned**: the conditions
    extractor picks `gold-standard-v2::consensus-4of5`'s
    `provenance.source_files` nondeterministically between two
    uplift-supplement evaluation paths, so a regeneration with no input
    change moves that row. No metric is affected.
    Anchors: `reports/tile-mcc-geometric-join-2026-09-12.md`,
    `reports/recovery-drop-fix-2026-09-13.md` § 6.3,
    `results/k-ladder-2026-09-12/recovery-fix-2026-09-13/README.md`
    § Changelog.
  - [x] **6c. Board metadata** — **characterised and corrected at the
    source 2026-09-14**, on the PI's ruling of that morning. Report:
    `reports/modality-track-audit-2026-09-14.md`; artefacts
    `results/modality-track-audit-2026-09-14/`; derivation
    `scripts/derive_condition_modality.py`.
    **Characterised, corpus-wide**: of 593 registered conditions 591 are
    derivable and 547 from a transmitted configuration, with **zero**
    routes contradicting one another. **Eight conditions and one proposer
    pool** carry a wrong recorded label, across **four** artefacts — the
    board's `membership.json` `track` (7 of 110),
    `results/working-precision/gs-plateau-characterisation.json`
    `modality` (3 of 263), `results/tile-size-sweep/tile_size_sweep.json`
    `modality` (1 of 16, `retest-phase2e::canonical-last`), and
    `results/k-ladder-2026-09-12/phase2/unions.json` `modality` (1 pool
    of 14, `scale-4-optimal-487`). Clean: the register (0 of 459), the
    passes manifest (0 of 447), the opmax membership (0 of 86), the
    uplift supplement (0 of 357 + 0 of 357), `ladders.json` (0 of 14).
    The mechanism is a substring test on the condition label, in four
    scripts, failing two ways: the token naming the **verifier** over a
    text proposer, and **no** token falling through to `"text"`.
    **Reach**: 5 analyses UNAFFECTED, 2 LABEL-ONLY (the signed Era-2
    board and the signed K-ladder — neither groups by the field; the
    board's `tiering_20m.json` carries zero `track` occurrences and the
    tiering instruments never read it), 3 NUMBER-AT-RISK.
    **Recomputed** ($0, sapphire): the plateau tabulation's every group
    statistic **holds** (image onset median 75 m / p90 100 / max 150,
    text 30 / 75 / 150, before and after; all five sibling summaries
    byte-identical); the tile-size sweep moves exactly **2 of 15** legs,
    both at 512 px single-pass, with Views 1 and 3 byte-identical; and
    `era1-single-pass-baseline-matrix`'s image group goes from **17
    computable cells at MCC 0.094–0.291** to **21 of 22 at
    0.0665–0.2907**, the four phase-2e ordering cells having been in
    neither group.
    **No preregistered outcome and no hypothesis-outcome row changes** —
    H1's confirmatory contrast groups the five phase-2a conditions, all
    correctly labelled. **Two unsigned-but-verified registered outcomes**
    (`era1-single-pass-baseline-matrix`, `tile-size-sweep`) and the paper
    sentence at `docs/paper/results-draft.md:195-196` plus claims row
    R2-06 quote a figure that moves: **not amended**, erratum **E88**
    drafted in § 7 of the report for the PI.
    **The board is NOT rebuilt** (re-signature pending) and no signature
    was touched. The next rebuild will carry the three
    `verified-*-image` cells as **text**, the four `pv-scale4-optimal`
    cells as **image**, and a new `track_basis` field on all 110
    members; no rank, tier, tie set, Hsu set or metric moves.
    **New, for the register's owner**: the register's
    `verifier_passes[...].modality` field is **ambiguous, not wrong** —
    119 of 174 entries fit the "verifier's own exemplars" reading and 92
    of 100 resolvable ones fit the "track" reading, and the
    `scale-4-optimal-487` family is split across both conventions inside
    one run. Not actioned; nothing numerical rests on it. Owner: Opus
    agent (done); PI to rule on E88 and on the field's meaning.
  - [ ] **6b. PI decision**: one verifier call (≈ US$0.0007) to make
    tier E's K = 5 zero-delta unconditional (candidate_01335 carried 0.10
    across a 1 px crop shift against a 0.15 gate) — or accept as
    conditional and disclosed.
- [ ] **7. 55-map board r2 rebuild**: the K = 5 rung of stride B under the
  3.7 verifier, the image run's cells (K = 1, K = 3, both arms), the MCC
  tiering; signatures. Owner: Opus agent; PI signs.
- [ ] **8. The image run's analysis row** `gemini37-image-55map-2026-09-13`
  and findings; P1–P5 verdicts; the deployment-scale modality result into
  the Results inventory. PI signs.
- [x] **9. Results draft housekeeping** — done 2026-09-13, commits
  `384b80025` (part A) and `61bada6cb` (part B). **Five** markers cleared,
  not four: the four `[DRAFT, S153 — pending PI ruling]` markers in § R7.3
  (the 3.8 verifier-seat leg, the r2 tier-1 sentence, the gold-standard
  back-reference, the cost paragraph) plus the § R4 `[DRAFT NOTE, S152]`,
  each replaced by the ruling it was waiting for, and item (a) of § R7.3's
  closing note resolved by ruling 1 / § D18. The draft now carries **zero**
  open PI decisions in its own markers, down from four; the two that remain
  wait on Methods prose and on the word allocation, neither a ruling.
  The claims inventory went from **181 claims over 10 of 12 blocks to 237
  over 12 of 12** — 214 VERIFIED, 19 DRIFTED, 1 SUPERSEDED (a status this
  pass adds), 3 UNANCHORED, and **10 verified at a committed anchor that no
  sentence of the draft makes**, every one a K-ladder finding. § R1b's
  twenty-three outline claims reproduce whole; §§ R3 and R6 drift only by
  reference vintage and by two Era-1 claims, and neither section states the
  ladder's shape, price, MCB sets, tile-MCC direction, verifier-stage
  reversal or resolution result. § R6's cost table is **one signature
  behind** `pass-budget-pareto-v2`, re-signed 2026-09-12T09:03:09Z with a
  tile-MCC column whose efficient set is {min6, min11} rather than the F1
  set's four rungs. Cross-section summary regenerated for all twelve
  blocks, with the two new ladder Pareto figures, the MCB and Phase-2
  ladder tables, the board's 150-cell tile-MCC table, and twelve new
  jargon glosses. Also surfaced: § R1b's registration note calls three
  register rows unsigned that were signed 2026-09-12, and two
  `hypothesis-tracking.md` items are stale or unapplied (the U12
  propagation warning; the PI's 2026-08-28 H9 disclose-only ruling,
  recorded and NOT applied). US$0, no compute beyond reads and two
  recomputations from committed artefacts. Anchors:
  `docs/paper/results-claims-inventory-2026-09-12.md` § Changelog
  2026-09-13 and `docs/paper/results-draft.md` § Changelog 2026-09-13.
- [ ] **10. Uplift supplement currency**: re-pair if any new verified cell
  gains a twin by construction; amend and re-sign the pairing row only if
  counts move.
- [ ] **11. Second documentation audit pass** after items 6–10, so the
  scorecard describes the foundation the outline pass starts from.
  - [x] **11a.** Rebuild the generated-file registry — done 2026-09-13,
    commit `86ba12413`. Charter extended to `outputs/**.md`: **3,619**
    files (was 2,131 at `06f7b8ea5`) — `results/` 2,864, `reports/` 88 of
    the 104 present (16 excluded as d17 audit apparatus), `outputs/` 638,
    `docs/` 29; **3,318** generated, **301** hand-written, **0**
    unattributed (two files were marker-carrying-but-unattributed under
    the old map). Generator map v1.1, 100 rules. Every generated row now
    records the 2026-09-11 ruling's three obligations as evidence — banner,
    source-commit stamp, `--check` mode read out of the generator's
    argparse, and the tier-1 test that runs it — so `--gaps` answers
    "which documents are in neither regime?" as a query. The registry
    carries its own guard (`_meta.git_head`, `--check`, tier-1 test).
  - [x] **11b.** Verify a source-commit stamp and a tier-1 drift guard for
    each of the five register renderings and the six generated documents
    in neither compliance regime — done 2026-09-13, commits `acd4ed054`
    (register renderings), `b16954d4c` (Era-2 board), `80e897049` (55-map
    boards). **Neither-regime count: 6 → 0.** The five renderings had a
    banner but no source commit and no `--check` at all; both added
    (`--check-renderings`, `tests/test_manifest_renderings.py`). The Era-2
    board's `tiering_20m.md` and `frame-deltas.md` and the three generated
    55-map boards took a banner, a stamp and a tested `--check`. Each of
    the ten documents was regenerated once with **zero content drift** —
    the diff is the banner. One correction: the audit's fourth "55-map
    table", `gs-vs-55map-transfer.md`, is hand-written (no generator, no
    sidecar JSON) and took regime 1's banner + Changelog instead, so the
    four split across both regimes. Left named, not closed: the 46
    `outputs/**/evaluation.md` files (the ruling's open class) and 17
    further `tiering_20m.md`-family documents for earlier analyses, one
    `--render-md` away. Deltas:
    `reports/generated-file-registry-2026-09-13.md`.
  - [ ] **11c.** `PaperImp` blocks on the 15 of 17 findings documents
    that lack one — on touch during the outline pass, not in bulk.
- [ ] **11d. Registry currency discipline**: the registry enumerates the
  file tree, so its tier-1 `--check` fails whenever any Markdown file is
  added or removed by a later commit (it did on the first merge after
  11a landed). Rebuild it (`scripts/build_generated_file_registry.py
  --out reports/verification/generated-file-registry.json`) as the last
  step of every handoff and after any merge that adds documents; consider
  a pre-commit hook. Owner: the session at handoff. **Rebuild from the
  MAIN checkout only** — a rebuild from an agent worktree dropped 93
  valid `outputs/` entries (untracked outputs are absent there; found
  and reverted 2026-09-13, E86/E87 job).
  **Amendment needed (found 2026-09-13, item 13):** this instruction is
  **unsafe from a git worktree**. The registry enumerates untracked
  `outputs/` working files as well as tracked ones, so a rebuild in a
  fresh worktree silently *deletes* the entries for files only the main
  checkout has — attempted here, it produced 18 insertions and **938
  deletions**, dropping 93 `outputs/ab-plus/_work/*.overflow-notes.md`
  and sibling entries, and was reverted. Restrict the rebuild to the
  main checkout, or teach the builder to enumerate tracked files only.
  Detail: `reports/null-exemplar-errata-2026-09-13.md` § 10.
- [x] **14. Runner hardening — `run_pv.py cleanup` overwrites `run.meta.json`
  with the retry pass's usage only** — done 2026-09-14, commits
  `94bc5c7d9` (the merge and the configuration gate), `3e0cc9d8d` (the
  `cleanup_history` carry), `dc5cf5656` (the auditor) and `1a8bebc0e`
  (the `pgrep` process note). Found 2026-09-14 by the image campaign's
  steward: arm 2's true cost is the pre-cleanup backup
  US$7.6875 + the cleanup meta US$0.0153; a later audit reading only the
  meta would understate it by three orders of magnitude. This is the
  mechanism that lost the fourth cell's 57,482-candidate verifier load in
  August (`reports/r7-gaps-deltas-2026-09-11.md` § 2.5). **Fixed
  permanently**: the written `run.meta.json` now carries the SUM of usage
  and execution stats across the main pass and every later pass, a
  `main_pass` block holding the original verbatim, and a `cleanup_passes`
  list (one entry per pass with its own usage block, counts,
  configuration fingerprint and the gate's evidence — the
  `configuration_history` pattern from PR #14); the pre-merge file is
  copied to an indexed `run.meta.pre-<kind>-<N>.json` sidecar that is
  never overwritten, so the operator's ad-hoc convention became the
  tool's own. `verify`'s resume path had the same shape and is fixed by
  the same writer; `4_detect_mounds_batch.py` was already merging
  (line 1349), so no defect there. A cleanup whose effective
  configuration differs from the main pass's is now **refused before any
  API call** unless `--allow-config-change` declares it — which makes
  `--safe-mode-tokens` a declared change, so
  `planning/run-phase3a-recovery.sh` (line 228) would now need the flag.
  The steward's verifier-leg auditor is
  `scripts/audit_verifier_cost.py`, gated on the GS calibration arms'
  committed US$0.4417 / US$0.6804 (reproduced exactly) and on the
  campaign's K = 1 arm 2 from BOTH files (skips while that tree is only
  on sapphire). **Two findings beyond the brief.** (i) The fourth cell's
  overwrite cannot be pinned on `cleanup`: its `probabilities.json`
  carries no `cleanup_history`, and `cleanup` always writes one — either
  it was a `verify` resume (no backup discipline at all) or a cleanup
  whose history a later resume erased, because both writers of
  `probabilities.json` rebuilt the file and dropped the key. That second
  defect is now fixed too, and it had been degrading
  `audit_verifier_completeness.py`. (ii) **Retrospective: 29 stages** in
  `outputs/**` carry the signature — **3 RECOVERABLE** (`verify_swap38`
  US$0.8469 from its in-directory `run.meta.main-2026-09-04.json`, and
  `verify_k1_recovery-fixed` US$0.4529 / `verify_k3_recovery-fixed`
  US$0.5349 reconstructed from adjudicated sibling stages) and **26
  UNRECOVERABLE**, the fourth cell and its GS leg among them. Largest
  money loss is not the largest count: `verifier-robustness/
  384-flash-high-text-ge3of5/T0.3/verified` records US$1.9116 for 2,775
  of 4,275 — a plausible-looking meta understating by half. No committed
  meta was rewritten. Report:
  `reports/cleanup-meta-fix-2026-09-14.md`. **Open for the PI**: whether
  a `--temperature` override should be written into the meta's
  `configuration` block (it currently is not, on either side of the gate,
  so the gate cannot see a temperature change and records it under
  `cli_overrides` instead), and whether a Gemini Pro rate card with a
  verified cache-read rate should be added so the sweep's three
  Pro-verifier stages can be priced.
- [ ] **12. Verdict-model decision (PI)**: a `disclosures` list beside
  `discrepancies` in the run-conditions verifier, so the 12 deliberate
  WARNs (3 `n-passes-over` on the mixed-provenance uplift pool, 9
  `pinned-vintage` disclosures) count as passes and 41 of 41 is
  reachable — it changes what a signature attests, so it is the PI's.
- [x] **13. E86/E87 handling** — done 2026-09-13, commits `2a270af50`
  (the provenance guard), `bcf936ad2` (the two errata and their sidecars)
  and `92745b0c9` (the Methods corrections). The two errata drafted in
  `map-reader-bench` `wiki/planning/parent-errata-drafts.md` inserted as
  **E86** and **E87** (register 85 → 87, collision-checked), every
  anchored claim re-verified here first. **E86**: the three null
  exemplars were selected 2025-12-23 from a training set re-selected
  under a new seed on 2026-01-04, and the null manifest was never
  regenerated, so they were never entered into the exclusion geometry.
  Exposure recomputed per frame and extended with the Era-1 512 px
  frame the draft lacked — **25 of 340** (all three exemplars are
  themselves evaluation tiles there), 3 of the registered 60, 20 of 487,
  13 of 327, 0 of the 5 verification tiles — ids in
  `inputs/examples/null-tiles/null_overlap_by_frame.json`. Nil on
  measurement (0 of 569 references in a null window) and confined to
  the image modality: 37 of the 41 image-modality configs carry the
  nulls and the only four that do not are the `verify_*` configs, so the
  verifier stage is clean by construction. **E87**: the lodged per-tile
  counts came from a bounding-box approximation — 36 → **50** distinct
  references over the 20 calibration windows (52 summed, 39 over cores),
  79 → **97** over the 60 holdout windows — and, new here, the
  registered density strata move **10 of 20** and **27 of 60** tiles,
  with 3 + 12 "empty" tiles not empty. Three dispositions departed from
  the drafts, each recorded in the entry: the lodged registration copy
  **cannot** be annotated inline (`results/commitments.json` pins it by
  git blob and anchors 702 commitments to line ranges; the attempt
  produced 520 locator failures and two tier-1 failures), so the
  pointers became `osf/errata-pointers.md`; "361 tiles" is already
  adjudicated by E64 (ii) and was not re-opened; and
  `select_tiles_phase2.py` is **frozen and annotated** rather than fixed
  or archived, because either would cost the committed selections'
  reproducibility. Guard: `scripts/check_manifest_provenance.py` over
  `inputs/provenance/manifest-dependencies.json`, 8 dependencies, flags
  exactly the null-tile manifest. Report:
  `reports/null-exemplar-errata-2026-09-13.md`. **Open for the PI**: the
  E87 remediation-3 disposition, and whether the H10 rationale sentence
  should be restated from the mining campaign's actual yield.
  - [ ] **13a. Null-exemplar sensitivity re-score** — every affected
    board cell re-scored with the overlapping tiles of the sidecar
    excluded, landing in
    `results/null-exemplar-sensitivity-2026-09-13/`. Owner: the sibling
    session running it in parallel on 2026-09-13; **not this session's
    work**, and E86's Impact field names it as the quantification of an
    exposure this session could only bound. Close this item with its
    commit when the re-score lands, and update E86's Impact if any cell
    moves.

**Then**: the Results outline pass proper, section by section, with the
PI ruling per section (the standing "outline first" rule); the
literature-review walk-through alongside; D-1..D-5 and D.9 re-opened only
after that.

## 3. Standing rules that apply

- Signatures mean something: every re-signature is presented with what
  it attests, what changed, what did not.
- Keep history, present the best available; ladder, then board.
- Generated projections carry provenance, not a hand changelog.
- Compute on sapphire; at most three live worktrees on the local disk.

## Changelog

### 2026-09-14 (latest) — item 14 closed: the cleanup metadata overwrite fixed permanently

**Refresh trigger**: the PI's 2026-09-14 ruling "fix permanently" on item 14,
raised by the image campaign's steward when its K = 1 arm 2 came out of a
503 storm with its cost split across two files.

**The fix** (`94bc5c7d9`): `run_pv.py`'s verifier writer no longer replaces a
prior pass's metadata. `run.meta.json` carries the sum of usage, execution
and cost across the main pass and every later pass; `main_pass` holds the
original verbatim; `cleanup_passes` lists one entry per pass with its own
usage block, counts, configuration fingerprint and the configuration gate's
evidence; the pre-merge file is copied to an indexed
`run.meta.pre-<kind>-<N>.json` sidecar that is never overwritten. `verify`'s
resume path is fixed by the same writer; batch mode preserves without summing
(it redoes the whole set). A cleanup whose effective configuration differs
from the main pass's is refused before any API call unless
`--allow-config-change` declares it. `4_detect_mounds_batch.py` was already
merging on resume (line 1349) — no defect there.

**The auditor** (`dc5cf5656`): `scripts/audit_verifier_cost.py`, the
steward's method promoted from an ad-hoc import, gated on the GS calibration
arms' committed **US$0.4417 / US$0.6804** (reproduced exactly, leg
US$1.1221, per-candidate 0.000710 / 0.001094, and the meta's own figure
confirmed at exactly 2× the audited one — the flex correction) and on the
campaign's K = 1 arm 2 as main + cleanup from BOTH files, which skips while
that tree is only on sapphire.

**Numbers this entry adds** (none revised; both inherited figures reproduce):

| Claim | Before | After |
|---|---|---|
| Stages known to carry the overwrite | 2 (the fourth cell and its GS leg, § 2.5) | **29** enumerated — 3 recoverable, 26 not |
| `verify_swap38`'s audited cost | not audited; its meta reads US$0.0039 | **US$0.8469** (219× the meta), summed from its in-directory prior meta |
| `verify_k1_recovery-fixed` / `verify_k3_recovery-fixed` | not audited | **US$0.4529** / **US$0.5349**, reconstructed from adjudicated sibling stages |
| Worst money understatement | assumed to be the largest count | `verifier-robustness/384-flash-high-text-ge3of5/T0.3`: **US$1.9116 for 2,775 of 4,275** — understates by about half and looks plausible |

**Two findings beyond the brief.** The fourth cell's overwrite cannot be
attributed to `cleanup`: its `probabilities.json` carries no
`cleanup_history`, which `cleanup` always writes — so either the pass was a
`verify` resume (which had no backup discipline at all; the ad-hoc meta copy
lived only in `cmd_cleanup`, added 2026-08-31 in `2ce4536ea`) or a cleanup
whose history a later resume erased, because both writers of
`probabilities.json` rebuilt the file and dropped the key. That second defect
is fixed in `3e0cc9d8d`, and it had been degrading
`scripts/audit_verifier_completeness.py`, which reads the history to surface
residual gaps.

**What did NOT change**: no committed `run.meta.json` was rewritten — the
reconstructions live in the report, and every `outputs/` directory is
byte-for-byte as it was; no result, evaluation or board cell moved; a stage
that never sees a second pass writes exactly what it wrote before (a tier-1
regression test, not an assurance); nothing on sapphire or on the campaign
branch was touched. Process note `1a8bebc0e` adds the `pgrep -f` over `ssh`
prohibition to `docs/agent-guidance.md` § Compute Location.

**Open for the PI**: whether a `--temperature` override should be recorded in
the meta's `configuration` block (it is not, on either side of the gate, so a
temperature change is disclosed under `cli_overrides` rather than blocked),
and whether a Gemini Pro rate card with a verified cache-read rate should be
added so the sweep's three Pro-verifier stages can be priced.

**Report**: `reports/cleanup-meta-fix-2026-09-14.md`.

### 2026-09-13 — item 13 added and closed: E86/E87 handled; 13a left with the sibling

**Trigger**: `map-reader-bench`
`wiki/planning/parent-errata-drafts.md`, two errata drafted in that
repository against this one's format and anchored to this repository's
paths and commits, with PI approval of the handling on 2026-09-13. Every
anchored claim was re-verified here before landing, and the numbers below
were computed in this session rather than carried from the drafts.

**Before → after table for numerical claims that moved**:

| Claim | Draft / prior | After | Source recomputed |
|---|---|---|---|
| Errata register size | 85 entries | **87** (E86, E87; collision-checked) | `protocol-errata.md`, `### E<n>` headings |
| Null-exemplar exposure, Era-1 512 px 340-tile frame | not in the draft | **25 of 340**, all three exemplars themselves evaluation tiles | `inputs/tiles/full_evaluation_manifest.json` via `scripts/audit_null_exemplar_overlap.py` |
| Era-2 487 / Era-2 240 / 512 px 60 / Era-3 327 | 20 / 6 / 3 / 13 | **20 / 6 / 3 / 13** (all four reproduced exactly) | same |
| Calibration references, affine-correct | 50 | **50 distinct, 52 summed** (the draft's 50 is the union; two references sit in a tile overlap) | `scripts/recount_prereg_tile_mounds.py` |
| Holdout references, affine-correct | not in the draft | **97 distinct, 106 summed, 82 over cores** (published 79) | same |
| Approximation vs affine row agreement | "45 of 80 against 7 of 20" | **45 of 80 against 31 of 80** (the draft compared different denominators; per set 10/20 and 35/60 against 7/20 and 24/60) | same |
| Density strata under corrected counts | not in the draft | **10 of 20 calibration and 27 of 60 holdout tiles change stratum**; 3 + 12 "empty" tiles are not empty | same |
| Configs transmitting null pixels | "image-modality configs" | **37 of 41**; the only four that do not are the `verify_*` configs | census over `prompts/configs/*.json` with the pipeline's `include_example_images` default |

**Three claims in the drafts that did not survive verification**, each
corrected in the entry rather than carried: "the verifier config carries
no examples" (it carries six, none of them null — so the conclusion holds
and the reason was wrong); the null-pool statement's location, given as
§ 8.4.1 (it is §§ 8.4.2–8.4.3); and "361 tiles at preregistration line 78"
as a live minor item (**E64 (ii)** adjudicated it on 2026-07-30 — what was
actually outstanding is that the paper draft had carried 361 forward
without that reading, which is what the Methods commit fixes).

**What did NOT change**: no metric, evaluation, board cell, scope
membership or hypothesis outcome; no example image; no tile manifest
membership; and the lodged registration copy is byte-identical to before
(blob `fa221b30f395`, the pin `results/commitments.json` records).

**Landed**: `2a270af50` (guard + registry + 25 tier-1 tests),
`bcf936ad2` (E86, E87, the two sidecars, the four annotated artefacts,
`osf/errata-pointers.md`, 46 tier-1 tests) and `92745b0c9` (Methods).

### 2026-09-13 — items 11a and 11b closed: the registry rebuilt, the neither-regime count closed to 0

**Trigger**: § 11.5 of `planning/interim-docs-review.md` made these the
prerequisites for the second audit pass — the classifier that would answer
"which generated documents are in neither compliance regime?" was stale and
blind to `outputs/`, so the answer rested on a reading pass.

| Claim | Before | After |
|---|---|---|
| Registry corpus | 2,131 files at `06f7b8ea5` (2026-08-20), `outputs/` not enumerated | **3,619** — `results/` 2,864, `reports/` 88 of 104, `outputs/` 638, `docs/` 29 |
| Strata | 1,952 generated / 179 hand-written | **3,318** / **301**, 0 unattributed |
| Generator map | 89 rules, v1.0 | **100** rules, v1.1 |
| Generated documents meeting all three obligations | 45 claimed, 5 of them unverified | **50**, six generators, each with its check mode and tier-1 test named |
| Generated documents in neither regime (the audit's six) | 6 | **0** |

**What did NOT change**: every register row, board cell, rank, tier, tie
set, withheld-cell disclosure and signature field; the ten regenerated
documents moved by exactly their banner and stamp (zero content drift), and
the 150-cell tiering table and three 28-pair 55-map boards re-rendered
byte-identically from their committed JSON — which is itself the evidence
they were pure projections. `docs/paper/results-draft.md` and the claims
inventory were untouched (item 9 was running in parallel).

**Correction carried into the standard**: the audit's "four 55-map
leaderboard tables" are three generated boards plus one hand-written
transfer table, which took regime 1's banner and Changelog instead.

**Commits**: `86ba12413` (11a), `acd4ed054`, `b16954d4c`, `80e897049` (11b),
plus this entry's own commit.

### 2026-09-13 (later) — item 9 closed: the ruled markers cleared, and every Results block inventoried

**Refresh trigger**: item 9. Commits `384b80025` (part A, the markers) and
`61bada6cb` (part B, the inventory).

| Claim | Before | After |
|---|---|---|
| `[DRAFT, S153 — pending PI ruling]` markers in the draft | 4 | **0** |
| Open PI decisions in the draft's own markers | 4 | **0** (two markers remain, waiting on Methods prose and on the word allocation) |
| Blocks in the claims inventory | 10 of 12 (R3, R6 placeholders; R1b never inventoried) | **12 of 12** |
| Claims recorded | 181 | **237** (214 V / 19 D / 1 SUPERSEDED / 3 U) |
| Ladder findings verified at anchor but absent from the draft | not counted | **10** |
| Prose words inventoried | 6,389 of 7,186 | **7,186 — all of it** |
| Figures/tables existing but uncited | 3 figures + 1 table | **10 rows**, five new |

**The markers were all ruled, and one more than the card expected.** The card
named four; there were five, because the § R4 `[DRAFT NOTE, S152]` was also
settled by ruling 7. Each now names its ruling: the 3.8 verifier-seat leg
reported as drafted; the family-clears-incumbent framing and the
gold-standard back-reference standing on ruling 2 / § D19 (headline = the
all-3.7 stack, 0.9190 board frame / 0.9265 screen); the fourth cell's mixed
token-basis/invoice cost kept as marked; the § R4 board note retained
verbatim under ruling 7; and item (a) of § R7.3's closing note resolved by
ruling 1 / § D18.

**What the K-ladder did to §§ R3 and R6 was not to correct them.** Neither
section was found numerically wrong by it. It **replaced the basis** of one
claim — "the diversity dividend is obsolete once a verifier stage exists" is
superseded, because on the fourteen verified `pv-diag-384` ladders the return
on K is still thinking-governed (significant on 7 of 7 HIGH, 2 of 6 MINIMAL,
all four single-tier ladders MINIMAL) — and it **supplied ten findings
neither section states**: the front-loaded shape (K = 3 on every ladder's
efficient set, 37–93 % of the gain for 31–64 % of the cost), the Hsu MCB sets
(K = 3 admissible on 12 of 22, no F1 set excluding K = 10, K = 1 ruled out on
F1 on 20 of 22 and admissible on tile-MCC on 22 of 22), tile-MCC never rising
with K and falling significantly on four ladders, the verifier absorbing
40.6 % of K's F1 return while reversing the sign of its tile-MCC effect, the
two corpora reconciled as a 487-tile resolution effect, the tile-factor
projection's 10.7 % overstatement, and the MCC-efficient set {min6, min11}.
§§ R3 and R6's own drift is **entirely reference vintage** plus two Era-1
claims.

**Three things the pass surfaced that were not in its brief.** § R1b's
registration note calls three register rows unsigned that were signed
2026-09-12T09:03:09Z; `hypothesis-tracking.md`'s warning that D17 finding
U12 contaminated the draft is now stale, the draft having recorded the
correction; and the same file records the PI's 2026-08-28 H9 "disclose only"
ruling as **recorded, NOT applied**, while § R3 reports H9 as executed and
rejected without that disclosure.

### 2026-09-13 — item 6 closed: one rebuild, three ruled changes, awaiting the PI's re-signature

| Claim | Before | After |
|---|---|---|
| The Era-2 board's state | signed 2026-09-12 on 103 cells, with a PENDING 153-cell proposal and four cells noted as pending re-score | **rebuilt** on the current evaluations; one fresh PENDING proposal stating BOTH statistic families |
| The board's instrument | F1 only; ruling 7 "not applied to the current signed board" | **F1 and tile-MCC on byte-identical swap masks**, BH q = 0.05 per family, each with its own greedy-clique tiering and Hsu MCB set |
| `g37-text-k3-verified-opmax` on the board | withheld row 0.8870, tile-MCC 0.1337 quoted-as-not-published; G6 row 0.8870 / 494 | **0.8860**; tile-MCC **withheld at source**; G6 **0.8860 / 495** |
| The F1 tiering | 7,961/11,175 significant, 14 tiers, tie set 5, MCB 65 of 150 | **identical — byte for byte**, on ranking, tiers, tie set, all 11,175 pairwise records and the MCB artefact |
| tile-MCC on the board | a reported column, untested | **2,982/11,175 pairs significant, 6 MCC tiers, MCC tie set 33, MCC MCB 59 of 150** (w_upper 0.0828, band 99) |
| Withheld-cell disclosure | F1 point + one-line refusal | **+ interval withdrawn (with the retracted interval named), shortfall counts, both tile vocabularies, the published-convention sentence** |
| Generated reports and the hypothesis table | current | regenerated, `--check`-clean, **zero content drift** — only the source-commit stamp moved in all 40 files |

**The card's expectation held this time.** It asked for "one rebuild, one
signature", and that is what happened: three separately ruled changes landed
together, the F1 arm reproduced exactly, and one `re_sign_pending` block is
waiting.

**What the rebuild found that the card did not anticipate.** The MCC family is
not a second opinion on the F1 ordering — it is close to its reverse. **No F1
Tier-1 cell is in MCC Tier 1**; MCC Tier 1 is 33 cells drawn entirely from F1
tiers 6–12, led by single-pass **image** proposer + verifier baselines; the two
Hsu admissible sets share **9** members of 65 and 59 (union 115 of 150); and the
MCC argmax is unstable at this resolution (0.420 stability, 36 distinct winners,
against F1's 0.602 / 22). That is the K-ladder review's "the two objectives
select different rungs" measured over a whole board, and it raises a
paper-facing question — which ranking the Results section leads with — that is
the PI's, not an agent's.

**One gap closed on the way**: `finalise` used to **overwrite** a PENDING
`re_sign_pending` block, which is why the recovery-fragment note had to keep a
durable copy of its numbers in the board README's changelog. A rebuild landing
on a pending block now nests it as `previous_pending`.

**What did NOT change**: every F1 rank, tier, pairwise test, BH verdict and MCB
member; Tier 1 and its five members; the 153 / 150 / 3 counts; the frame,
reference, seed, permutation count and buffer; every gate's verdict and G6's
0.0078; the register, byte for byte; and every signature field — 10
signature-bearing paths asserted byte-equal
(`rebuild-mcc-2026-09-13/signature-paths.json`, PASS). Deltas:
`reports/era2-board-mcc-family-2026-09-13.md`.

### 2026-09-13 — item 6a closed: the invariant withholds, the k3 cell is written

| Claim | Before | After |
|---|---|---|
| A refused cell's evaluation | aborts inside `bootstrap_ci` — no F1 written | **F1 / P / R point estimates written; per-tile table, confusion, tile-MCC and every interval WITHHELD with the reason, counts and both vocabularies named** |
| `g37-text-k3-verified-opmax` F1@20 / detections | 0.8870 / 494 (stale, unwritable) | **0.8860 / 495** in its own evaluation and in `conditions-manifest.json` |
| That cell's tile-MCC and CI | 0.1337; CI [0.3684, 0.7732] | **withheld / withdrawn** — both were computed from a table the invariant refuses |
| `carry_probabilities.py` | in the recovery-fix harness | **`scripts/carry_probabilities.py`**, 13 tier-1 tests, original archived |
| Tier-1 suite | — | **2,552 passed, 4 skipped, 3 xfailed, 0 failed** in 185 s on sapphire, of which 21 are this item's new tests |

**Where the card's expectation had to be corrected**: it asked that "F1 and
its bootstrap proceed". The bootstrap cannot: `bootstrap_ci` resamples
**tiles**, so its input is exactly the table the invariant refuses. A refused
cell therefore reports a point and no interval, and the interval it used to
carry is withdrawn rather than replaced.

**What did NOT change**: the board — not rebuilt, not re-tiered, no signature
field, 16 signature-bearing paths asserted byte-equal when its pending note was
amended; the two K = 1 cells and tier E's K = 5, whose live artefacts are
untouched and whose re-score reproduces byte-identically; every number in
`reports/recovery-drop-fix-2026-09-13.md`; and the 593 / 41 / 1,317 / 67
manifest row counts.

### 2026-09-13 — Batch 1 items 1 and 2 closed (Session 153)

| Claim | Before | After |
|---|---|---|
| Run directories with a post-run report | 2 of 36 (card's figure) | 41 of 41 — the registry holds 41 runs at 41 distinct paths, so the gap was 39 |
| Verifier verdicts | 22 pass / 19 partial / 0 fail | 38 pass / 3 partial / 0 fail |
| Open verifier WARNs | 221 | 12, all by-design disclosures |

**What did NOT change**: no metric, evaluation, detection, threshold or
signature; 41 runs and 593 conditions before and after. Deltas with anchors:
`reports/documentation-batch1-deltas-2026-09-13.md`.

**Raised for the PI** (not actioned): reaching 41 pass needs a verifier
verdict-model change — a `disclosures` list beside `discrepancies`, with PASS
defined over `discrepancies` alone — because the remaining 12 WARNs are
satisfied checks the model has nowhere to put. That changes what a signature
attests, so it is a PI call, not an agent's.

### 2026-09-13 (later) — Items 3, 4 and 5 closed

Batch 1's documentation items, run on one Opus agent in an isolated
worktree, $0 and no API calls.

- **Item 3** (`79a4d3c0e`): Obs **477–481** appended to
  `docs/notes/working-notes.md` — the tile-join class, the
  recovery-fragment class, the verifier-stage tile-MCC reversal, the
  MCB-versus-greedy disagreement, and the AUD-against-USD corroboration.
  Next free number collision-checked; no existing entry edited.
- **Item 4** (`34c6d4be0`): § M.x of `docs/paper/methods-draft.md` current
  to E85 and the 67-row register, with the S153 conventions and two
  further inferential departures (E82, E83) disclosed. It also **found a
  contradiction**: § M.x said H13 was silently dropped, while the
  register and the generated hypothesis-outcome table both hold H13 as
  registered-exploratory *with a result* — the arms were built and the
  three registered analyses ran on 2026-08-17/18, the day after the
  erratum recording the omission.
- **Item 5** (`d52ec49af`): `planning/interim-docs-review.md` § 11
  (additive; the April scorecard untouched) and a recounted compliance
  table in `docs/methodology/output-directory-standard.md`.

**What this changes for the items still open.** The audit's headline is
that there are now two compliance regimes and **six generated documents
sit in neither** — including the Era-2 board's own `tiering_20m.md` and
`frame-deltas.md`, which carry the ranks, and all 46
`outputs/**/evaluation.md`. Item 6's board rebuild is the natural moment
to close the first two. Item 11 should be preceded by a rebuild of
`reports/verification/generated-file-registry.json`, last built
2026-08-20 at `06f7b8ea5` and by charter not covering `outputs/` at all.

### 2026-09-13 — Original publication (Session 153)

Externalised from the chain assessment given in session. Batch 1
launched the same day on Opus agents at the PI's request.
