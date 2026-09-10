# Uplift supplement + corpus dataset: consensus and verifier, quantified

> **Last revised**: 2026-08-29 (build steps 1–3 EXECUTED and merged;
> scoring worklists running on sapphire). See
> [§ Changelog](#changelog).

**PI concept (2026-08-28, in-session)**: anchor every consensus run
with K = 1 metrics (with and without verifier) so consensus uplift is
captured; report every verified cell with-and-without its verifier so
verifier uplift is captured; flatten the entire run corpus into a
digestible table as (a) the paper's comprehensive supplement with
brief in-text uplift analysis, (b) a dataset for carefully considered
post-hoc pattern characterisation, (c) the benchmark corpus's tabular
face (see `planning/benchmark-prior-art-note-2026-08-28.md`).

## Heterogeneity design (PI + assistant, agreed 2026-08-28)

The corpus mixes buffers (20/50 m), references (curator / canonical /
standardised), frames (340 / 487 / 8,541 tiles) and instruments with
different noise floors. Structural safeguards, machine-enforced:

1. **Master long-form CSV** with a mandatory `stratum_id` composite
   key (corpus × reference × buffer × frame). The builder REFUSES any
   derived aggregate spanning strata unless flagged
   `transfer=true`.
2. **`strata.csv` companion**: one row per stratum with n_tiles,
   n_refs, permutation null-σ and MDE80 (joined from
   `results/sensitivity-mde-2026-08-28/`) — every rendered table's
   caption states its stratum's resolution.
3. **Transfer-pairs table**: cross-stratum comparisons exist ONLY as
   explicit (source cell ↔ target cell) pairs with deltas/taxes —
   the project's transfer-tax shape as a first-class object.

## Build order (all $0, sapphire, background-able)

1. **Flatten**: one row per registered condition from the manifests
   (factors: geometry, modality, thinking, temperature, K, operating
   point; metrics: F1/P/R/MCC + CIs; context: stratum, cost where
   audited). Per-pass grain from the passes-manifest as a second
   table for variance columns.
2. **K = 1 gap-fill**: derive K=1-no-verifier cells for the K=5
   incumbents from committed per-pass detections (modern runs already
   have N=1 rungs). K=1-WITH-verifier for incumbents is BLOCKED by
   verifier coverage (vote≥3 shells only — singletons never verified)
   and is DISCLOSED, not approximated; A/B/image are fully covered.
3. **With/without-verifier pairing**: for every verified cell, the
   pre-verifier consensus set at the same vote threshold from the
   committed unions → the verifier-uplift column corpus-wide
   (generalises Obs 172, the 256-rescue, the dividend-obsolescence
   finding from episodes to a fitted pattern).
4. **The Quarto literate-reporting pilot** (PI-agreed): the
   supplement as .qmd — per-stratum sections whose code chunks filter
   to one stratum_id by construction; tables and figures regenerate
   from the CSVs at render.
5. **Post-hoc mining, LAST and labelled**: exploratory,
   hypothesis-generating, stratified; candidate patterns to test
   corpus-wide: verifier uplift vs proposer precision deficit
   (Obs 172-class), consensus uplift vs pass diversity (Obs 141),
   saturation onset vs per-pass look multiplicity (the Obs 438
   interpretive hypothesis).

## Notation

All symbols and column names conform to the canonical key
`docs/methodology/notation-key.md` (PI-commissioned 2026-08-29); the
CSV builder validates its columns against that key's §§ 6-7.

## Registration

The flattening and pairing are derivations over registered artefacts —
registered as analyses (not new conditions) when built, per the
sweep-interior ruling; any cell the supplement headline-cites gets
promoted on citation as usual.

## Changelog

### 2026-09-10 — Board-frame exclusion rule implemented and the supplement rebuilt (S152)

**Trigger**: the GS Era-2 verified board (`planning/gs-era2-verified-board-2026-09-08.md`)
registered 39 `-era2b` rows (S151-d) and, for its symmetry fix, 43 `-opmax`
rows (S152), all but three with `scope_override.test_set_id = era2-b-487`.
**Rule (PI, 2026-09-10)**: a condition whose `scope_override` names a
leaderboard scoring frame is a board artefact, not a measurement of its own
(the `-era2b` rows re-score registered cells that already carry their
committed-frame row here; the `-opmax` rows are in-sample optima registered
for the board), and is excluded from the flatten and from the pairing on
both sides. Implemented as `lib_uplift_supplement.BOARD_FRAMES` and
`is_board_frame_condition` (read from the hand-authored spec, so a row that
post-dates the manifest is still recognised); the build and pairing reports
list the exclusions. Landed at `300473765`.

| Quantity | Before | After |
|---|---:|---:|
| Board-frame rows excluded | — | 79 (39 `-era2b` + 40 on-board `-opmax`) |
| `conditions.csv` rows | 438 | 441 |
| Pairing worklist rows | 169 | 172 |
| Uplift computed (F1 and MCC) | 69 | 71 |
| Blocked pairs | 100 | 100 |
| Strata | 130 | 130 |

The three new rows are the archived board's K = 3 `-opmax` cells
(`pv-min-text-t0.0-n3`, `pv-high-text-t0.0-n3`, `pv-n1-image-t0-n3`): off
the board by its K ≥ 5 rule, they carry no override and enter the supplement
as ordinary registered conditions on the Era-2 frame (two paired to
already-registered twins, one ready). **Not decided by the rule**: whether
the archived board's 40 sweep-optimal Gemini 3 cells should also enter the
supplement, with pre-verifier twins materialised at their vote thresholds;
they are E56-class in-sample optima and the rule keeps them out with the
other board-frame rows. What did NOT change: the 100 blocked pairs, the
130 strata, every previously computed uplift.

### 2026-08-29 — Build executed (S144)

Steps 1–3 built by a background worktree agent, hardened through a
two-lens audit plus three fix/verify rounds (merge `8f0d6e033`), and
merged: strata-enforced flatten (374 conditions / 113 strata /
54 columns), K=1 gap-fill worklist (115 ready scoring jobs; the
with-verifier floors MEASURED per stage — note the card's "vote ≥ 3
shells" premise was wrong: 11 runs verified from vote ≥ 1, five only
from vote ≥ 4; see `results/uplift-supplement/k1-gapfill-disclosure.md`),
verifier pairing (15 ready pairs; 21 more await a vote-shell
materialiser, not yet built), and the uplift computer. Scoring
launched on sapphire same day. Registration and any headline citation
remain gated on PI sign-off per § Registration. Notation-key § 6/§ 7
extensions proposed, canonical key untouched
(`results/uplift-supplement/notation-extension-proposal.md`).

### 2026-08-28 — Original publication

Queued at PI direction ("add to queue... something we could be
running in the background while we focus on other work").
