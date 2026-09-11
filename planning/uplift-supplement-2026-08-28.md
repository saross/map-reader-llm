# Uplift supplement + corpus dataset: consensus and verifier, quantified

> **Last revised**: 2026-09-11 (the 70 "no committed pre-verifier set"
> pairs surveyed and 43 closed by four new absence-refusal rules —
> blocked 86 → 43, uplift computed 85 → 128 on both metrics, every one
> of the 43 positive; the 27 that stay are first-N ladder rungs whose
> universe was never committed. Prior: 2026-09-10, the 14 ambiguous verifier-pairing twins
> resolved by the new `crop-manifest` rule — blocked 100 → 86, uplift
> computed 71 → 85 on both metrics; earlier the same day: the board-frame
> exclusion rule implemented and the supplement rebuilt; prior:
> 2026-08-29, build steps 1–3 EXECUTED and merged, scoring worklists
> running on sapphire). See [§ Changelog](#changelog).

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

**Registered and signed 2026-09-10/11 (S152)**: analysis rows `uplift-supplement-flatten` (diagnostic; 441 conditions; `conditions.csv`) and `verifier-uplift-pairing` (comparison, H2; the 85 verified cells with a computed uplift; `verifier-uplift.csv` and the MCC companion), approved as drafted by the PI (ruling 2(v)); signature notes on the rows.

## Changelog

### 2026-09-11 — The 70 "no committed pre-verifier set" pairs surveyed; 43 closed

**Trigger**: PI, 2026-09-11 — survey the 70 rows blocked with "no committed
pre-verifier set was found" and close every pair that can be closed exactly.
The `crop-manifest` rule below resolved AMBIGUITY (several committed consensus
sets, none attributable); these 70 were the absence class, and the entry below
said so: "this rule resolves ambiguity, not absence".

**What the survey found.** The refusal conflated two states. "No consensus
GeoJSON names this cell's shell" is true of all 70. "No candidate universe is
recorded anywhere" is true of only 27. For the other 43 the corpus records the
universe — in the cell's own verifier crop manifest, in a second run the
register itself names, or across two files — and the shell at the cell's `k` is
exactly its `vote_count >= k` subset, because **vote shells nest**: a universe
counted over N passes and recorded from its `j of N` floor contains every
candidate at `vote >= k` for any `k >= j`, and nothing else.

**Four rules** (`scripts/build_verifier_pairing_worklist.py`), each firing ONLY
on the absence refusal and each ranked below `registered`, `consensus-file`,
`union` and `crop-manifest`, never overriding one:

| basis | rows | the attribution it reads |
|---|---:|---|
| `source-run-consensus` | 5 | the condition row names another run as its proposer's home (`source_run`), so the consensus and union searches run under THAT run's tree |
| `stage-manifest` | 13 | the candidate universe the cell's OWN verifier stage cropped, matched by the same lineage matcher the union rule cross-checks with — or, where token matching is ambiguous, by the manifest's recorded `source_geojson` naming the cell's pool |
| `shell-manifests` | 13 | the universe recorded across a base manifest and the committed S104 vote-3 increment; accepted only when the two shells are disjoint and join into an unbroken range reaching `k` |
| `single-pass-manifest` | 12 | `N = 1`, where the pool recorded no `vote_count` because there were no votes to record; the shell at `k = 1` is the whole universe |

Each refuses rather than approximates: `stage-manifest` requires the manifest's
vote basis to equal the cell's N and its floor to be at or below `k` (a
different rung of the pass ladder, or a universe that starts above `k`, is
refused); `shell-manifests` refuses overlapping shells (double counting) and
gaps (missing candidates); `single-pass-manifest` fires at `N = 1, k = 1` only
and refuses a manifest that does record votes. The materialiser
(`scripts/materialise_pairing_twin.py`) gains the two modes they need: a
repeatable `--crop-manifest` that unions manifests and re-keys candidate ids,
and an explicit `--single-pass` — a missing `vote_count` column must never be
read as zero votes by default.

**The 70, classified**

| run | rows | verdict |
|---|---:|---|
| `stride-55map-2026-08-25` | 23 | **truly absent** |
| `pv-diag-384` (four baselines) | 12 | resolvable — `single-pass-manifest` |
| `verifier-robustness` | 7 | resolvable — 5 `stage-manifest`, 2 `source-run-consensus` |
| `55maps-text-high-t0-3-generalisation` | 5 | resolvable — `shell-manifests` |
| `55maps-text-min-generalisation` | 5 | resolvable — `shell-manifests` |
| `gemini37-55map-2026-08-29` | 4 | **truly absent** |
| `55maps-text-high-generalisation` | 3 | resolvable — `shell-manifests` |
| `verifier-t-pilot` | 3 | resolvable — `source-run-consensus` |
| `flash35-pv-2x2` | 3 | resolvable — `stage-manifest` |
| `55maps-text-min-n10-uplift` | 3 | resolvable — `stage-manifest` |
| `55maps-image-generalisation` | 2 | resolvable — `stage-manifest` |

**The 27 that stay blocked, and why.** All are first-N rungs of a longer pass
ladder. `stride-55map`'s A and B cells and `gemini37-55map`'s two arms commit
one candidate universe each — `union_k10.geojson` (38,713 / 57,482) and
`union_k5.geojson` (12,715) — counted over 10 and 5 passes. Their N = 1 / 3 / 5
rungs are not subsets of those: each is re-clustered from the committed passes
at analysis time (`scripts/stride55_ladder.py` and
`scripts/gemini37_arm_ladder.py`, `cluster_first_n`, which clusters
`passes[:n]` and inherits the K-pass probabilities by nearest neighbour within
10 m). Clustering over 3 passes is not clustering over 10 restricted to 3, so
filtering the committed union at the rung's `k` would pair the cell with a
universe of a different vote basis — the "different rung of the ladder" refusal
the pairing rules already make. The rung's pre-verifier counts ARE recorded, in
the final board's sweep CSVs at `prob_t = 0.0`
(`results/55map-final-board-2026-08-27/sweep_A-N3.csv` and siblings), so a
derived twin is possible — but it would be a re-aggregation, which this
builder refuses by design, and it needs the ladder re-run under its own gates.
**That is a PI decision, not this rule's shape.**

| Quantity | Before | After |
|---|---:|---:|
| Blocked pairs | 86 | 43 |
| `ready` | 20 | 25 |
| `ready-after-materialise` | 57 | 95 |
| Uplift computed (F1) | 85 | **128** |
| Uplift computed (MCC) | 85 | **128** |
| Pairing worklist rows | 172 | 172 |

**The 43, by twin** (verified − twin at the cell's own headline buffer and
reference; every one positive on both metrics). Rows sharing a twin share its
value, which is the parameter control an uplift number is supposed to isolate.

| cell | twin n | verified | twin | uplift F1 | uplift MCC |
|---|---:|---:|---:|---:|---:|
| `verifier-robustness::verified-256-union-t0-0-n5` | 1,165 | 0.8637 | 0.4599 | +0.4038 | +0.5970 |
| `verifier-robustness::verified-256-ge3of5-t0-3-n5` | 1,165 | 0.8582 | 0.4599 | +0.3983 | +0.5774 |
| `55maps-text-high-t0-3-generalisation::verified-oracle-p0.20-k3-standardised-gt` | 13,945 | 0.8406 | 0.4651 | +0.3755 | +0.4975 |
| `55maps-text-high-t0-3-generalisation::verified-k3-canonical-gt` | 13,945 | 0.8476 | 0.4727 | +0.3750 | +0.4936 |
| `55maps-text-high-t0-3-generalisation::verified-oracle-p0.20-k3-r2-gt` | 13,945 | 0.8399 | 0.4651 | +0.3748 | +0.4976 |
| `55maps-text-high-t0-3-generalisation::verified-k3-standardised-gt` | 13,945 | 0.8393 | 0.4651 | +0.3742 | +0.4909 |
| `55maps-text-high-t0-3-generalisation::verified-k3-r2-gt` | 13,945 | 0.8387 | 0.4651 | +0.3736 | +0.4910 |
| `55maps-text-high-generalisation::verified-k3-standardised-gt` | 13,572 | 0.8387 | 0.4688 | +0.3699 | +0.4715 |
| `55maps-text-high-generalisation::verified-k3-r2-gt` | 13,572 | 0.8380 | 0.4690 | +0.3690 | +0.4705 |
| `55maps-text-high-generalisation::verified-k3-canonical-gt` | 13,572 | 0.8425 | 0.4745 | +0.3680 | +0.4726 |
| `55maps-text-min-n10-uplift::verified-5of10-standardised-gt` | 12,276 | 0.8279 | 0.4708 | +0.3571 | +0.6144 |
| `55maps-text-min-n10-uplift::verified-5of10-r2-gt` | 12,276 | 0.8274 | 0.4709 | +0.3565 | +0.6132 |
| `55maps-text-min-n10-uplift::verified-5of10-canonical-gt` | 12,276 | 0.8290 | 0.4749 | +0.3541 | +0.6166 |
| `55maps-text-min-generalisation::verified-oracle-p0.20-k3-standardised-gt` | 12,390 | 0.8110 | 0.4570 | +0.3540 | +0.6121 |
| `55maps-text-min-generalisation::verified-k3-standardised-gt` | 12,390 | 0.8109 | 0.4570 | +0.3538 | +0.6066 |
| `55maps-text-min-generalisation::verified-oracle-p0.20-k3-r2-gt` | 12,390 | 0.8103 | 0.4571 | +0.3532 | +0.6112 |
| `55maps-text-min-generalisation::verified-k3-r2-gt` | 12,390 | 0.8102 | 0.4571 | +0.3531 | +0.6057 |
| `55maps-text-min-generalisation::verified-k3-canonical-gt` | 12,390 | 0.8127 | 0.4614 | +0.3513 | +0.6083 |
| `pv-diag-384::verified-adv-text-baseline-pro-vf` | 1,047 | 0.8263 | 0.5196 | +0.3067 | +0.8366 |
| `pv-diag-384::verified-adv-text-baseline-medium-vf` | 1,047 | 0.8244 | 0.5196 | +0.3048 | +0.8410 |
| `flash35-pv-2x2::f3prop-f35vf-6of10` | 929 | 0.8689 | 0.5704 | +0.2985 | +0.6566 |
| `flash35-pv-2x2::f35prop-f3vf-4of10` | 859 | 0.8480 | 0.5502 | +0.2978 | +0.6768 |
| `pv-diag-384::verified-adv-text-baseline` | 1,047 | 0.8142 | 0.5196 | +0.2946 | +0.8366 |
| `flash35-pv-2x2::f35prop-f35vf-4of10` | 859 | 0.8362 | 0.5502 | +0.2860 | +0.6462 |
| `verifier-t-pilot::verified-t0-5` | 608 | 0.8561 | 0.6999 | +0.1562 | +0.3157 |
| `verifier-robustness::verified-384-ge3of5-t0-3-high-n5` | 584 | 0.8764 | 0.7223 | +0.1541 | +0.2850 |
| `verifier-robustness::verified-384-ge3of5-t0-3-n5` | 584 | 0.8739 | 0.7223 | +0.1516 | +0.2673 |
| `verifier-robustness::verified-384-ge3of5-t0-7-high-n5` | 584 | 0.8739 | 0.7223 | +0.1516 | +0.2887 |
| `verifier-t-pilot::verified-t0-0` | 608 | 0.8507 | 0.6999 | +0.1508 | +0.3221 |
| `verifier-robustness::verified-384-union-t0-0-n5` | 584 | 0.8722 | 0.7223 | +0.1499 | +0.2581 |
| `verifier-robustness::verified-384-ge3of5-t0-7-n5` | 584 | 0.8709 | 0.7223 | +0.1486 | +0.2673 |
| `verifier-t-pilot::verified-t1-0` | 608 | 0.8422 | 0.6999 | +0.1423 | +0.3005 |
| `pv-diag-384::verified-adv-image-baseline-pro-vf` | 746 | 0.7309 | 0.5995 | +0.1314 | +0.5763 |
| `pv-diag-384::verified-adv-image-baseline-medium-vf` | 746 | 0.7300 | 0.5995 | +0.1305 | +0.5724 |
| `pv-diag-384::verified-adv-image-baseline` | 746 | 0.7167 | 0.5995 | +0.1172 | +0.5642 |
| `55maps-image-generalisation::verified-k4-standardised-gt` | 4,982 | 0.7400 | 0.6669 | +0.0731 | +0.1609 |
| `55maps-image-generalisation::verified-k4-r2-gt` | 4,982 | 0.7398 | 0.6668 | +0.0730 | +0.1602 |
| `pv-diag-384::verified-adv-pro-text-baseline-pro-vf` | 430 | 0.7861 | 0.7630 | +0.0231 | +0.0393 |
| `pv-diag-384::verified-adv-pro-image-baseline-medium-vf` | 519 | 0.6281 | 0.6059 | +0.0222 | +0.0992 |
| `pv-diag-384::verified-adv-pro-text-baseline-medium-vf` | 430 | 0.7842 | 0.7630 | +0.0212 | +0.0357 |
| `pv-diag-384::verified-adv-pro-image-baseline` | 519 | 0.6196 | 0.6059 | +0.0137 | +0.0896 |
| `pv-diag-384::verified-adv-pro-image-baseline-pro-vf` | 519 | 0.6178 | 0.6059 | +0.0119 | +0.0992 |
| `pv-diag-384::verified-adv-pro-text-baseline` | 430 | 0.7696 | 0.7630 | +0.0066 | +0.0308 |

**Reading.** Every one of the 43 is positive on both metrics, and the spread
runs the same way the corpus already reads it: a Pro proposer's single pass is
precise enough that a verifier adds 0.007–0.023 F1 (the four
`pro-medium-*-baseline` cells), while a Flash single text pass gains +0.29–0.31
F1 — and, at tile level, the whole of its discriminative power. The
`text-baseline` twin's tile MCC is **−0.0038**: one unverified Flash text pass
fires somewhere on almost every tile of the 487, so as a tile classifier it is
indistinguishable from chance; the verifier lifts the same candidate set to
0.833. That is the single largest uplift in the supplement on either metric,
and it is a baseline cell — the class the pairing could not reach until now.
The three 55-map text families gain +0.35–0.38 F1 and +0.47–0.62 MCC from their
3-of-5 and 5-of-10 shells, which is where the deployment argument for a
verifier actually lives.

**Gates**: every materialised twin's feature count equals its universe's count
at `vote >= k` 4,982 / 13,572 / 13,945 / 12,390 / 12,276 / 1,047 / 746 / 519 / 430 / 859 / 929 / 584 — each equal to the count an independent pre-computed shell of the same universe gives, and the two `source-run` twins are committed files scored as they stand (608 and 1,165); blocked dropped by exactly 43, the number
of pairs resolved; no previously computed uplift changed on either metric and
none was lost; no already-resolved row changed basis, path or command. Twin
evaluations waived into their runs' `_ignored_evals` by
`scripts/waive_uplift_anchor_evals.py`; manifests regenerated;
`verify_run_conditions.py` 22 pass / 19 partial / 0 fail, unchanged.

**The registered analysis row `verifier-uplift-pairing` is SIGNED and was not
touched.** Its counts move with this work and the PI amends it.

### 2026-09-10 (later) — The 14 ambiguous verifier-pairing twins resolved by crop manifest

**Trigger**: PI, 2026-09-10 — resolve the 14 ambiguous pairings rather
than accept them as disclosed. All 14 are `pv-diag-384` verified cells on
the Era-2 frame, blocked with "N committed `<k>`-of-`<N>` consensus
set(s) sit under the run tree, which serves 41 distinct pool/geometry
lineages, and none carries this cell's tokens".

**Why they were answerable after all.** The `consensus-file` rule asks
which committed consensus set belongs to a cell; in a 41-lineage run tree
that question has no answer, and refusing was right. A different question
does have one: the cell's REGISTERED `proposer_pool` names its lineage at
the vote >= 1 shell (`<lineage>-1of<N>`), and `pv-diag-384` records one
candidate manifest per lineage under a directory of exactly that name.
The twin is then the shell `vote_count >= k` of the universe the cell's
own verifier cropped — an attribution the registry already made, not a
guess about which file belongs to whom.

**Implementation** (`scripts/build_verifier_pairing_worklist.py`, new
`crop-manifest` rule; `5a0ab3d2a`). It fires ONLY on an ambiguity refusal
— where nothing was found at all, the run holds no pre-verifier set and
blocking stays the right answer — and is ranked below both `registered`
and an unambiguous `consensus-file`, never overriding either. It refuses
unless the pool names a vote >= 1 shell whose N equals the cell's, so a
manifest that is already vote-filtered, or one from another rung of the
pass ladder, cannot be filtered a second time. The stage path, universe
size, vote range and count at threshold go into the row's notes, and the
path into a new `crop_manifest_path` column declared through
`COLUMN_EXTENSIONS` (the builder's proposal channel; the canonical
notation key stays the PI's to amend). Twins built by
`scripts/materialise_pairing_twin.py --crop-manifest`, scored on sapphire
with each cell's own recorded recipe (curator reference, 487-tile Era-2
frame, 14 buffers, 10,000-draw bootstrap, seed 42, `--mcc`).

**Evidence the manifest is the right universe**, checked before the rule
was written. For 12 of the 14 the run also holds a per-`k` stage manifest
(`flash-high-text-4of5`, `flash-high-text-6of10`,
`pro-high-text-pro-vf-3of5`, `image-6of10`, …), and the base manifest
filtered at `vote >= k` reproduces its candidate count exactly in all 12.
The remaining two lineages (`flash-high-text-t03`, `text-min-t07-true`)
have no per-`k` stage anywhere; for them the base manifest's candidate
count equals its verifier stage's `probabilities.json` entry count
exactly — 2,954 and 1,586 — so the verifier demonstrably consumed that
whole universe.

| Quantity | Before | After |
|---|---:|---:|
| Blocked pairs | 100 | 86 |
| `ready-after-materialise` | 43 | 57 |
| `pairing_basis` = `crop-manifest` | — | 14 |
| Uplift computed (F1) | 71 | 85 |
| Uplift computed (MCC) | 71 | 85 |
| Pairing worklist rows | 172 | 172 |

**The 14, F1@20 m** (verified − twin; twin = the same candidate universe
at the same vote threshold, unfiltered by probability):

| cell | twin n | verified | twin | uplift F1 | uplift MCC |
|---|---:|---:|---:|---:|---:|
| `verified-adv-text-min-true-3of5` | 985 | 0.8784 | 0.5465 | +0.3319 | +0.7121 |
| `verified-adv-text-min-n30lineage-4of5` | 807 | 0.8708 | 0.6039 | +0.2669 | +0.5750 |
| `verified-adv-text-6of10` | 727 | 0.8769 | 0.6678 | +0.2091 | +0.3433 |
| `verified-adv-text-t03-4of5` | 659 | 0.8783 | 0.7002 | +0.1781 | +0.2768 |
| `verified-adv-text-pro-vf-4of5` | 584 | 0.8792 | 0.7223 | +0.1569 | +0.2907 |
| `verified-adv-text-4of5` | 584 | 0.8641 | 0.7223 | +0.1418 | +0.2653 |
| `verified-adv-text-medium-vf-4of5` | 584 | 0.8545 | 0.7223 | +0.1322 | +0.2168 |
| `verified-adv-text-high-vf-4of5` | 584 | 0.8519 | 0.7223 | +0.1296 | +0.1952 |
| `verified-adv-image-min-6of10` | 577 | 0.7890 | 0.6759 | +0.1131 | +0.4473 |
| `verified-adv-image-3of5` | 506 | 0.7778 | 0.7290 | +0.0488 | +0.1475 |
| `verified-adv-pro-image-pro-vf-3of5` | 471 | 0.7112 | 0.6998 | +0.0114 | +0.0437 |
| `verified-adv-pro-text-pro-vf-3of5` | 367 | 0.8506 | 0.8429 | +0.0077 | +0.0147 |
| `verified-adv-pro-text-medium-vf-3of5` | 367 | 0.8495 | 0.8429 | +0.0066 | +0.0147 |
| `verified-adv-pro-text-flash-vf-3of5` | 367 | 0.8491 | 0.8429 | +0.0062 | +0.0147 |

Every uplift is positive, and the spread is the story the corpus already
tells from the other direction: the four `pro-high-text-1of5` cells share
one twin at 0.8429 and gain 0.006–0.008, because a Pro proposer's 3-of-5
shell is already precise, while the minimal-thinking text pools gain
0.27–0.33 from a shell whose precision the verifier has to supply. The
three flash-verifier-variant rows over `flash-high-text-1of5` also share
a twin (0.7223) and separate only by their probability threshold, which
is the parameter control an uplift number is supposed to isolate.

**Gates**: every materialised twin's candidate count equals its
manifest's count at `vote >= k` (584/727/584/584/584/659/985/807/367/367/
367/506/577/471, all matching the pre-computed shells); blocked dropped
by exactly 14, the number of pairs resolved; no previously computed
uplift changed on either metric; no other worklist row changed in any
field. The 14 twin evaluations waived into `pv-diag-384`'s
`_ignored_evals` by `scripts/waive_uplift_anchor_evals.py` (whose reason
text now states the class rather than the 2026-09-07 batch's scoring
commit, which is not these rows'); manifests regenerated;
`verify_run_conditions.py` 22 pass / 19 partial / 0 fail, unchanged.

**Still blocked: 86.** The largest remaining classes are 23 stride-55map
rows and 16 rows whose verified cell records no vote threshold at all, so
there is no "same vote threshold" set to pair with. Those are not this
rule's shape: 14 of the 86 were ambiguous attributions, and this rule
resolves ambiguity, not absence.

### 2026-09-10 (later) — Registration walk-through rulings 2(i)–2(iv) (S152, PI present)

- **2(i)** The notation key sanctions the supplement's columns (§ 7.1) and
  names every frame in use (§ 6); the proposal now reports 0 pending
  (`f97bede45`).
- **2(ii)** r2 is the 55-map headline reference; canonical, standardised
  and student stay as disclosed strata (`headline_reference` column,
  `3dfa12c00`).
- **2(iii)** The 14 pairs blocked as "ambiguous consensus set under the
  `pv-diag-384` tree" are to be RESOLVED, not accepted as disclosed: the
  twin is the verifier stage's own candidate manifest at vote ≥ k (the
  crop-manifest basis), an exact construction; queued to the background
  agent with the board's re-materialisation. The remaining blocked pairs
  (16 with no vote threshold, and those with no committed pre-verifier
  set) are accepted as disclosed. Standing preference recorded: close a
  gap that can be closed exactly at modest cost rather than defer it.
- **2(iv)** The board's 40 `-opmax` rows (Gemini 3 sweep optima) stay
  OUT of the supplement by design: an uplift at an in-sample argmax is
  the maximum over the sweep, an optimistically biased quantity (E56),
  and the same pools are in the supplement at their committed points.

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
