# The Era-2 board rebuilt: a tile-MCC family beside the F1 tiering

> **Last revised**: 2026-09-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Verdict in one line.** The GS Era-2 verified board is rebuilt once, carrying
three separately ruled changes for one Principal Investigator (PI)
re-signature; the preregistered F1 tiering **reproduced byte-identically**,
Tier 1 and its five members are unchanged, and the new tile-MCC family — the
thing the rebuild existed to add — turns out to rank the board almost the
opposite way round, which is a finding and not a formality. US$0, zero
Application Programming Interface (API) calls, all compute on sapphire.

**What to read if you read one thing.** § 4. On the same 487 tiles, the same
10,000 permutations and byte-identical swap masks, **no F1 Tier-1 cell is in
tile-MCC Tier 1**, MCC Tier 1 is 33 cells drawn entirely from F1 tiers 6–12,
and the two Hsu Multiple-Comparisons-with-the-Best (MCB) admissible sets share
**9** members of 65 and 59. The board's tiering stays the preregistered F1 one,
which is exactly what ruling 7 asked for; but a reader who assumed the MCC
column was a second opinion on the same ordering would have been wrong.

**Scope.** Checklist item 6 of
`planning/documentation-foundation-checklist-2026-09-13.md`. Run in an isolated
worktree at `~/worktrees/map-reader-llm/claude-board` on sapphire, branch
`worktree-agent-af5346372ccc4c32b`. Nothing was re-scored: the four
recovery-fix cells were taken at the evaluations item 6a left on `main`.

---

## 1. The three ruled changes, and why they came as one rebuild

| # | Ruling | What it required | Anchor |
|---|---|---|---|
| 1 | recovery-fragment fix, PI ruling 2026-09-13 | pick up the four re-scored cells at the **next** rebuild rather than rebuilding for them | `reports/recovery-drop-fix-2026-09-13.md` § 5; `provenance.json` → `re_sign_pending.cells_pending_rescore` (now nested under `previous_pending`) |
| 2 | ruling 7 (S153) | the round-robin tile-swap carries tile-MCC on the **same swap masks** as F1, Benjamini-Hochberg (BH) q = 0.05 within its own family, **reported beside** the F1 tiering and not replacing it; withheld cells out of both | `planning/gs-era2-verified-board-2026-09-08.md` § Changelog, 2026-09-13; the `--permute-mcc` arm of `reports/k-ladder-mcc-test-2026-09-12.md` § 2 |
| 3 | ruling 6 (S153) | the name-based (`id`) tile join is the **published convention**; a refused cell is disclosed, not re-joined | `planning/gs-era2-verified-board-2026-09-08.md` § Changelog, 2026-09-13; `reports/tile-mcc-geometric-join-2026-09-12.md` |

One rebuild for all three, because a board signature is not free: the PI signs
what the board attests, and three rebuilds would have asked for three
signatures over the same 150 cells.

## 2. The command chain, in order

All on sapphire, venv `~/Code/map-reader-llm/.venv`, from the worktree root.
`B` is `results/leaderboard/era2/gs-era2-verified-board-2026-09-10`.

```text
1  scripts/build_gs_era2_board.py membership
2  scripts/build_board_tiering_input.py --board $B \
       --analysis-id gs-era2-verified-board-2026-09-10
3  scripts/era1_leaderboard_tiering.py --analysis-id gs-era2-verified-board-2026-09-10 \
       --analyses $B/tiering-input/run-analyses.json --output-dir $B --permute-mcc
4  scripts/selection_aware_intervals.py --board gs-era2-verified-board-2026-09-10 \
       --analyses $B/tiering-input/run-analyses.json --metric mcc \
       --bootstrap 10000 --m-frac 1.0 --buffer 20 --out $B/mcb
5  scripts/selection_aware_intervals.py … --metric f1 …   (the F1 MCB, LAST)
6  scripts/build_gs_era2_board.py gates
7  scripts/build_gs_era2_board.py finalise --no-analysis-row --re-sign-reason "…"
8  $B/rebuild-mcc-2026-09-13/harness/assert_signature_paths.py …
```

Steps 4 and 5 are in that order deliberately: the PI's standing rule is that an
admissible set is a property of its candidate set, so the **F1** MCB — the one
the board cites — is recomputed **last**, over the final membership. Step 3 ran
for 51 minutes of wall clock (≈ 34 min F1 arm, ≈ 15 min MCC arm) single-core at
100 % CPU; steps 4 and 5 in about a minute each.

## 3. Before → after

| Quantity | before (2026-09-13, F1-only) | after |
|---|---:|---:|
| Cells admitted / tiered / withheld | 153 / 150 / 3 | **153 / 150 / 3** |
| F1 pairs significant at BH q = 0.05 | 7,961 / 11,175 | **7,961 / 11,175** |
| F1 tiers (sizes) | 14 | **14**, same sizes `5/8/15/15/24/14/20/16/9/9/4/4/6/1` |
| F1 Tier 1 (greedy clique) | the five 3.7 / 3.8 cells | **the same five, same order, same F1** |
| F1 tie set | 5 | **5** |
| Top cell | `g37-image-k5-verified-swap37-p0.90-k5` 0.9233 | **the same cell, 0.9233** |
| Hsu **F1** MCB admissible set | 65 of 150 (w_upper 0.0749) | **65 of 150 (w_upper 0.0749)** |
| F1 two-sided MCB band | 70 | **70** |
| Hsu **tile-MCC** MCB admissible set | — (no MCC family existed) | **59 of 150 (w_upper 0.0828, w_lower 0.1011), band 99** |
| MCC pairs significant at BH q = 0.05 | — | **2,982 / 11,175** |
| MCC tiers (sizes) | — | **6**, sizes `33/48/50/11/6/2` |
| MCC tie set | — | **33** |
| `g37-text-k3-verified-opmax` withheld row | F1@20 0.8870, tile-MCC 0.1337 | **F1@20 0.8860**, tile-MCC **withheld at source** |
| Its G6 row | 0.8870 / 494 features | **0.8860 / 495** |
| Gates | G2 0 / G3 0 / G4 110 / 110 | **unchanged** |
| G6 max abs frame delta | 0.0078 | **0.0078** |
| `membership.json` exclusions | 160 | **161** — one 55-map row registered since, correctly refused; members stay 110 |

**The F1 arm reproduced exactly, and that was measured, not assumed.**
`ranking`, `tiers`, `tie_set` and all **11,175** pairwise records are
byte-identical to the committed run (blob `f2f1af55a0a24418ab4ef626e84c4dbb1dff4bf0`,
`96bdb8629:…/tiering_20m.json`), and the F1 MCB artefact is byte-identical too —
`git diff` reports no change to
`mcb/gs-era2-verified-board-2026-09-10_b20_m1.json`. Record:
`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/rebuild-mcc-2026-09-13/f1-arm-identity.json`
(`f1_arm_identical: true`; the only key that moved is `withheld_cells`).

Why it had to: of the four cells the recovery-fragment fix moved, three are
already withheld from every statistic, and the fourth,
`g384-ov192-k5-verified-opmax` at rank 9, re-scores dict-identically because the
candidate the fix promoted to 5 votes carries probability 0.10 against that
rung's prob ≥ 0.15 gate. No F1 input changed, so no F1 output could.

## 4. The MCC family's headline — the two metrics select different cells

The table is at
`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md`
§ "Tile-level MCC"; the pairwise arm is `tiering_20m.json` →
`mcc_permutation.pairwise`; the admissible set is
`mcb/gs-era2-verified-board-2026-09-10_mcc_b20_m1.json`.

**It resolves much less than F1 does.** 2,982 of 11,175 pairs separate on
tile-MCC against 7,961 on F1, and the greedy clique gives 6 tiers against 14.
That is the power limitation the K-ladder MCC test already recorded for this
487-tile frame (`reports/k-ladder-mcc-test-2026-09-12.md` § 3, point 3), now
measured over a whole board rather than one ladder.

**Where it does resolve, it disagrees with the F1 reading.**

| Claim | Figure | Anchor |
|---|---|---|
| F1 Tier-1 cells in MCC Tier 1 | **0 of 5** | `tiering_20m.json` `tie_set` vs `mcc_permutation.tie_set` |
| where the MCC family puts the F1 Tier-1 cells | MCC ranks **36, 51, 54, 80, 119**; MCC tier 2 for four of them, tier 3 for `g37-text-k10-verified-carried-p0.10-k10` | `mcc_permutation.ranking` |
| MCC Tier 1's composition | **33 cells, all from F1 tiers 6–12** (3 / 7 / 8 / 5 / 4 / 3 / 3 across tiers 6→12) | same |
| MCC leader | `verified-adv-image-baseline-pro-vf`, tile-MCC **0.8887**, F1 rank **119 of 150**, F1 tier 9, F1@20 0.7309 | README rows 119 (F1 table) and 1 (MCC table) |
| admissible-set overlap | **9** of 65 (F1) and 59 (MCC); union 115 of 150; 56 F1-only, 50 MCC-only | the two `mcb/*.json` `hsu_not_ruled_out` sets |
| what the overlap is | five B-geometry grid rungs (K = 1 ×2, 3, 5, 10), three of the five 3.7 F1 Tier-1 cells, and `verified-adv-text-min-6of10` | same |
| the top F1 cell | **is** MCC-admissible (MCC rank 36) | same |
| the top MCC cell | is **not** F1-admissible | same |
| MCC argmax stability | **0.420**, 36 distinct winners (F1: 0.602, 22) | `mcb/*_mcc_b20_m1.json` `argmax_stability` |
| MCC selection optimism | apparent 0.8887, optimism **+0.0153**, corrected **0.8734** | same |

**How to read it.** The cells that localise mounds best (high F1) are not the
cells that decide best which tiles hold a mound (high tile-MCC), and on this
board the ordering is close to reversed: MCC Tier 1 is dominated by
**single-pass image** proposer + verifier baselines, which sit in the F1
ranking's bottom half. The mechanism is the one the K-ladder review names — a
detection-level metric rewards extra true positives inside already-positive
tiles, which move no tile; a tile-level metric punishes the extra false
positives that flip negative tiles — so a configuration tuned for F1 buys
detections at the cost of tile-level discrimination. This is § 4 and the MCB
job's PARETO MCC SET reading measured over 150 cells at once rather than within
a ladder, and it is the argument for ruling 7's "reported, not replacing".

**Flagged as surprising, per `docs/agent-guidance.md` § Research Finding
Calibration.** The pipeline was checked before the result was accepted: the MCC
statistic passed its per-cell confusion gate on all 150 cells with zero
withholdings beyond the three tile-join refusals; the swap masks are pinned
byte-identical to the F1 test's by
`tests/test_k_ladder_mcc_instruments.py::test_f1_and_mcc_kernels_draw_identical_swap_masks`;
and the F1 arm computed in the same run reproduced the committed board exactly,
which is the strongest available evidence that the harness was not
misconfigured. The disagreement is a property of the two metrics, not of this
run.

## 5. The withheld cells, disclosed (ruling 6)

All three Gemini 3.7 gold-standard text rungs stay admitted-and-withheld, from
**both** families. What the board now publishes per cell:

| cell | F1@20 (whole frame) | interval | booked / in-frame | shortfall | committed tile-MCC |
|---|---:|---|---:|---:|---:|
| `g37-text-k1-verified-carried-p0.10-k1` | 0.8338 | withdrawn — was [0.3684, 0.7709] | 22 / 526 | 504 | 0.1422 (not published) |
| `g37-text-k1-verified-opmax` | 0.8495 | withdrawn — was [0.2712, 0.6667] | 21 / 475 | 454 | 0.1337 (not published) |
| `g37-text-k3-verified-opmax` | 0.8860 | withdrawn (none to retract) | 20 / 467 | 447 | — withheld at source |

Plus, per cell, both tile vocabularies: the frame's 487 names over four map
sheets against the cells' 351 / 319 / 306 distinct `source_tile` names, of which
only **12 / 11 / 11** are in the frame's vocabulary. The censuses come from
`lib_advanced_metrics.describe_tile_join_refusal`, the same describer
`evaluate_detections.py` writes into a refused cell's own artefact, so the board
and the cell do not grow two dialects of the same facts.

**"Withdrawn" is the precise word, and it is load-bearing.** The F1 bootstrap
resamples **tiles** (Decision 10; every artefact's
`_metadata.bootstrap.resampling_unit` says so), so the per-tile table the
invariant refuses is the interval's input too. A refused cell therefore has a
point estimate and **no** interval on this frame; the interval it used to carry
is not replaced by a better one, it is retracted. Two of the three still hold a
pre-invariant interval in their committed artefacts, so the board names the
number it is retracting rather than leaving a reader to discover the
discrepancy.

**Two of the three were NOT re-scored**, and their committed artefacts still
predate the invariant. That is deliberate — item 6's brief was to take the
evaluations as they stand — and it is why their pre-invariant tile-MCC still
exists to be quoted-as-not-published while the re-scored K = 3 cell's does not.

## 6. Signature discipline

`finalise` rebuilds `provenance.json` from the gate artefacts, so three fields
with no gate artefact behind them are carried forward:
`signed_at`, `signature_history`, `gates.G1.pi_ruling`. The run's own output
confirms it: *"carried forward from the previous provenance.json: signed_at,
signature_history, re_sign_pending (pending, nested as previous_pending),
gates.G1.pi_ruling"*.

**Ten signature-bearing paths asserted byte-equal before and after**, PASS —
`rebuild-mcc-2026-09-13/signature-paths.json`, harness
`rebuild-mcc-2026-09-13/harness/assert_signature_paths.py`:
`provenance.signed_at`, `.signed_by`, `.signature_history`,
`.gates.G1.pi_ruling`, `.re_sign_pending.previous_pending`, the whole of
`results/run-analyses.json`, and the board row's `manually_verified_at`,
`_signature_note`, `conditions_compared` and `outcome`. No signature field was
altered and the signed analysis row was not written at all
(`--no-analysis-row`).

**One gap closed while doing it.** Until this job, `finalise` **overwrote** a
PENDING `re_sign_pending` block outright — which is why the recovery-fragment
note had to keep a durable copy of its numbers in the board README's changelog
(`scripts/build_gs_era2_board.py`, the 2026-09-13 "Why this entry exists as well
as the provenance block" entry). A rebuild landing on a pending block now nests
it as `previous_pending`, so the previous proposal's text, its
`cells_pending_rescore` record and the resolved block one level further in all
survive. Nothing in it is a signature field; it is the trail of what was
proposed, and the project's rules say to keep history.

**The board awaits the PI's re-signature.** `provenance.json` →
`re_sign_pending`, whose `proposed_outcome` states both families, both
admissible-set sizes and their overlap, and ends *"The board's tiering remains
the F1 one."*

## 7. What did NOT change

- **Every F1 rank, tier, pairwise test, BH verdict and MCB member**; Tier 1 and
  its five members; the tie set; the top cell and its F1; the F1 MCB artefact,
  byte for byte.
- The 153 admitted / 150 tiered / 3 withheld counts, and the identity of the
  three withheld cells.
- The frame (`era2-b-487`, 487 tiles, 435 curator reference mounds), the
  reference, the seed (42), the permutation count (10,000) and the headline
  buffer (20 m).
- Every gate's verdict, and G6's maximum frame delta of 0.0078.
- **Every signature field**, and the register — `results/run-analyses.json` is
  byte-identical.
- The **39 generated run reports** and the **hypothesis-outcome table**: both
  regenerated and both `--check`-clean, with **zero content drift** — the only
  change in all 40 files is the source-commit stamp, which `--check` blanks
  before comparing. No manifest changed in this job, because the k3 cell's
  `conditions-manifest.json` row was already corrected under item 6a
  (`a8c03bb9e`).
- The K-ladder review's own numbers, and its analysis row signed
  2026-09-13T06:58:12Z.
- `TILE_JOIN_DEFAULT` is still `id`. Close-out question 4 — the corpus-wide
  tile-join decision — is still open and is still the only thing between the
  three withheld cells and full rows on the board.
- Item 11b's scope: the board's `tiering_20m.md` and `frame-deltas.md` still
  carry no source-commit stamp and no tier-1 drift guard. That was not in this
  job's brief and is left where the checklist put it.

## 8. Raised for the PI, not actioned

1. **The two-metric disagreement needs a paper-facing decision.** The board now
   publishes two rankings that disagree systematically. § 4's reading is that
   this is a real property of the metrics, not an artefact — but which of the
   two the Results section leads with, and whether the MCC family earns its own
   exhibit rather than a paragraph, is a PI call. A reader given only the F1
   board would draw a materially different conclusion about which
   configurations are good.
2. **The MCC argmax is unstable at this resolution** — stability 0.420 with 36
   distinct winners, against the F1 argmax's 0.602 with 22. Naming a single
   "best tile-MCC configuration" from this board would be over-reading it; the
   admissible set of 59 is the honest object.
3. **Item 6b is still open**: the one verifier call (≈ US$0.0007) that would
   make tier E's K = 5 zero-delta unconditional, or its acceptance as
   conditional and disclosed.

## 9. Verification

| Check | Result | Anchor |
|---|---|---|
| F1 arm reproduces the committed board | **byte-identical** on ranking, tiers, tie set and 11,175 pairs | `rebuild-mcc-2026-09-13/f1-arm-identity.json` |
| F1 MCB artefact reproduces | **byte-identical** (`git diff` empty) | `mcb/gs-era2-verified-board-2026-09-10_b20_m1.json` |
| every board cell is a single detection SET, so the MCC arm cannot abort mid-run | 153 of 153, checked **before** launching | probe run on sapphire before step 3 |
| MCC per-cell confusion gate | **150 of 150 pass**, 0 withheld beyond the 3 tile-join refusals | `tiering_20m.json` → `mcc_permutation.gates` |
| gates G2 / G3 / G4 / G6 | 0 / 0 / 110 of 110 / max abs delta 0.0078 | `gates.json`, `frame-deltas.md` |
| signature-bearing paths byte-equal | **10 of 10, PASS** | `rebuild-mcc-2026-09-13/signature-paths.json` |
| run reports drift guard | 39 of 39 up to date, 2 hand-authored skipped | `scripts/generate_run_reports.py --check` |
| hypothesis-outcome table drift guard | up to date, 15 hypotheses | `scripts/generate_hypothesis_outcome_table.py --check` |
| tier-1 suite | see § Changelog | `pytest -m tier1` on sapphire |

## Changelog

### 2026-09-13 — Original publication

Written with the rebuild, under checklist item 6. The board was rebuilt once
carrying three ruled changes; the F1 tiering reproduced byte-identically; the
new tile-MCC family disagrees with it systematically; ten signature-bearing
paths asserted byte-equal; the board awaits the PI's re-signature.
