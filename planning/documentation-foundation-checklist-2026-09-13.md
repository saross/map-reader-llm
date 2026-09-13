# Documentation foundation checklist — the preregistration → outcome chain

> **Last revised**: 2026-09-13 (later still — item 6a closed: the
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
| Results → analyses → signatures | `results/run-analyses.json`; findings documents | 67 rows, 66 signed, 1 unsigned by design; every findings doc bannered | boards pending one rebuild each (§ 2 items 4–5); the image run's row (§ 2 item 6) |
| Deviations → errata | `docs/methodology/preregistration/protocol-errata.md` (E1–E85) | complete register | **none** — § M.x brought current to E85 and to the S153 rulings, 2026-09-13 (§ 2 item 4) |
| Working notes | `docs/notes/working-notes.md` (Obs 1–481) | current | **none** — Obs 477–481 written 2026-09-13 (§ 2 item 3) |
| Paper-facing | `docs/paper/results-draft.md`, `results-outline.md`, `results-claims-inventory-2026-09-12.md`, `methods-draft.md`, `discussion-outline.md`, `discussion-seeds.md`, `manuscript-skeleton-isprs.md` | outline decisions D1–D22 settled; inventory built for R0–R2, R4–R5, R7–R9; Methods zero-draft; Discussion outline current to August | § 2 items 8–10; D-1..D-5 and D.9 stay DEFERRED |
| The project's own documentation audit | `planning/interim-docs-review.md` (2026-04-22, § 11 re-score 2026-09-13), `docs/methodology/output-directory-standard.md` compliance table (recounted 2026-09-13, May counts kept as history) | refreshed | six generated documents in neither compliance regime, and a stale generated-file registry (§ 11.5); second pass is § 2 item 11 |

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

- [ ] **6. Era-2 board rebuild and re-signature**: the four re-scored
  cells (recovery-fragment fix, landed `eda4ab70e`: three unchanged, k3
  0.8870 → 0.8860), the tile-MCC permutation family (ruling 7), one
  rebuild, one signature (PI: "I'll wait"). Owner: Opus agent; PI signs.
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
- [ ] **9. Results draft housekeeping**: clear the four `[DRAFT, S153 —
  pending PI ruling]` markers now ruled; extend the claims inventory to
  R3, R6 and R1b against the ladder findings; regenerate the cross-section
  summary. Owner: Opus agent.
- [ ] **10. Uplift supplement currency**: re-pair if any new verified cell
  gains a twin by construction; amend and re-sign the pairing row only if
  counts move.
- [ ] **11. Second documentation audit pass** after items 6–10, so the
  scorecard describes the foundation the outline pass starts from.
  - [ ] **11a.** Rebuild the generated-file registry (built 2026-08-20 at
    `06f7b8ea5`; short by 814 `results/**.md` and 48 `reports/**.md`;
    does not enumerate `outputs/`) before item 11. Owner: Opus agent.
  - [ ] **11b.** Verify a source-commit stamp and a tier-1 drift guard for
    each of the five register renderings and the six generated documents
    in neither compliance regime (the Era-2 board's `tiering_20m.md` and
    `frame-deltas.md`, the four 55-map leaderboard tables); add where
    missing. Owner: Opus agent.
  - [ ] **11c.** `PaperImp` blocks on the 15 of 17 findings documents
    that lack one — on touch during the outline pass, not in bulk.
- [ ] **12. Verdict-model decision (PI)**: a `disclosures` list beside
  `discrepancies` in the run-conditions verifier, so the 12 deliberate
  WARNs (3 `n-passes-over` on the mixed-provenance uplift pool, 9
  `pinned-vintage` disclosures) count as passes and 41 of 41 is
  reachable — it changes what a signature attests, so it is the PI's.

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
