# Uplift supplement + corpus dataset: consensus and verifier, quantified

> **Last revised**: 2026-08-28 (original publication; QUEUED behind
> the skeleton/drafting work — background-able, $0 throughout). See
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

## Registration

The flattening and pairing are derivations over registered artefacts —
registered as analyses (not new conditions) when built, per the
sweep-interior ruling; any cell the supplement headline-cites gets
promoted on citation as usual.

## Changelog

### 2026-08-28 — Original publication

Queued at PI direction ("add to queue... something we could be
running in the background while we focus on other work").
