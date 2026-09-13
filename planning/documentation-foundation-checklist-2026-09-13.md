# Documentation foundation checklist — the preregistration → outcome chain

> **Last revised**: 2026-09-13 (later — items 3, 4 and 5 closed: Obs
> 477–481, § M.x current to E85 and the 67-row register, and the
> documentation audit refreshed; earlier that day: original publication,
> Session 153, when the PI asked for the chain's remaining documentation
> to be externalised as a checklist to work through before the paper's
> outline pass). See [§ Changelog](#changelog).

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
| Experiments → runs and conditions | `results/runs-manifest.json`, `results/conditions-manifest.json`, `scripts/verify_run_conditions.py` | 41 runs, 593 conditions all with metrics; verifier 22 pass / 19 partial / 0 fail | the 19 partials are WARNs, mostly cross-run pools lacking a `source_run` note (§ 2 item 2) |
| Runs → post-run reports | `outputs/**/post_run_report.md` | 2 of 36 run directories | § 2 item 1 |
| Results → analyses → signatures | `results/run-analyses.json`; findings documents | 67 rows, 66 signed, 1 unsigned by design; every findings doc bannered | boards pending one rebuild each (§ 2 items 4–5); the image run's row (§ 2 item 6) |
| Deviations → errata | `docs/methodology/preregistration/protocol-errata.md` (E1–E85) | complete register | **none** — § M.x brought current to E85 and to the S153 rulings, 2026-09-13 (§ 2 item 4) |
| Working notes | `docs/notes/working-notes.md` (Obs 1–481) | current | **none** — Obs 477–481 written 2026-09-13 (§ 2 item 3) |
| Paper-facing | `docs/paper/results-draft.md`, `results-outline.md`, `results-claims-inventory-2026-09-12.md`, `methods-draft.md`, `discussion-outline.md`, `discussion-seeds.md`, `manuscript-skeleton-isprs.md` | outline decisions D1–D22 settled; inventory built for R0–R2, R4–R5, R7–R9; Methods zero-draft; Discussion outline current to August | § 2 items 8–10; D-1..D-5 and D.9 stay DEFERRED |
| The project's own documentation audit | `planning/interim-docs-review.md` (2026-04-22, § 11 re-score 2026-09-13), `docs/methodology/output-directory-standard.md` compliance table (recounted 2026-09-13, May counts kept as history) | refreshed | six generated documents in neither compliance regime, and a stale generated-file registry (§ 11.5); second pass is § 2 item 11 |

## 2. Items (tick with date + commit; never delete)

**Batch 1 — $0, Opus agents, can run now**

- [ ] **1. Post-run reports for every run directory** (34 missing of 36):
  generated from the manifests, metas and intent files with the
  revision-policy banner; bulk back-fill requested by the PI 2026-09-13
  ("can the post-run reports be done with Opus agents?" — yes; it
  supersedes "back-fill on touch" for this item only).
  Owner: Opus agent. Anchor: `docs/methodology/output-directory-standard.md`
  § "Documents in Revision Policy Scope".
- [ ] **2. Resolve the 19 partial runs**: add `source_run` notes for
  cross-run proposer pools and clear every other WARN class the verifier
  reports (`scripts/verify_run_conditions.py --run <id>`), until 41 pass;
  no metric changes. Owner: Opus agent.
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
  - [ ] **6a. Prerequisite**: the tile-join invariant currently raises
    inside `bootstrap_ci` and aborts the WHOLE evaluation of a refused
    cell, so the k3 cell's moved F1 cannot be written to its evaluation
    or register row. Under ruling 6 (name-based join published; refused
    cells' F1 reported in full, per-tile table withheld) the invariant
    must withhold the per-tile table and let F1 and its bootstrap proceed.
    Code fix + test, then write the k3 evaluation. Also promote
    `carry_probabilities.py` (integer-crop-window coverage test) to
    `scripts/`. Owner: Opus agent.
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
