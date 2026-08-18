# Defect D8 — `pro-medium-image-baseline` provenance mismatch, resolved

> **Last revised**: 2026-08-18 (original publication). See [§ Changelog](#changelog)
> for revision history.

**Verdict up front. D8 is CLEARED.** The 519-versus-587 gap is not corruption,
not a lost artefact, and not an artefact of defect D6. It is the expected
signature of a **documented failure-recovery top-up** (commit `c07c57766`,
2026-06-03, disclosed as E57's completeness addendum and Obs 339) that appended
68 detections to a raw pass **after** that pass's verifier crops had already
been extracted on 2026-03-24. Every artefact in the chain is internally
consistent, the pre-recovery version is recoverable from git, and all three
dependent `gs-era2` rows reproduce exactly from committed data.

What survives the investigation is a narrower and genuinely open issue —
crop manifests cite a **mutable path with no version anchor**, so three cells
corpus-wide now name a source whose content has changed under them. That is
carried forward as D14 in `defect-register-2026-08-18.md`, not as D8.

Zero API calls were made in producing this report.

## 1. The four hypotheses, tested

The register asked which of four explanations held. Each was tested against
committed artefacts rather than assumed.

| # | Hypothesis | Verdict | Evidence |
|---|---|---|---|
| H-a | The pass was re-run or topped up after crops were extracted | **HOLDS** | § 2 |
| H-b | Crops were extracted from a filtered or thresholded subset | Rejected | The 519 crops are the pass's first 519 features in file order, unfiltered (§ 3) |
| H-c | The manifest counts something other than input features | Rejected | `total_detections` is `len(features)` of the source at `scripts/extract_candidates.py:403` |
| H-d | 519 and 587 were measured against different **pass sets** (a D6 artefact) | **Rejected** | § 1.1 |

### 1.1 The D6 hypothesis, tested first and falsified

This was the cheapest test and would have changed the finding entirely, so it
was run first. It does not hold.

`587` is the feature count of **one file** —
`image-t0.0/run_1/detections_image-t0.0_run01.geojson` — not of the pool. The
pool's three passes hold 587, 544 and 544 features respectively; a three-pass
total would be **1,675**, not 587. The 519-versus-587 difference is therefore
*within one file across time*, not *across files at one time*, which is the only
thing a `detections_*` glob under-read can produce.

D6 **is** live in this pool — a sweep of all 173 pools holding `run_<N>`
detection files finds exactly **3** with split naming conventions, and this is
one of them (batch `run_1` as `detections_…`, realtime `run_2`/`run_3` as
`detections-…`), so a `detections_*` glob resolves 1 of 3 files here. But that
is a separate defect, and it cannot generate this particular gap. (The other
two mixed pools are `pro-medium-text-baseline/text-t0.0` — the sibling touched
by the same recovery, § 6 — and `e47-propose-brief/flash-high-text-n5/propose_brief-text`.)

## 2. What actually happened

The raw pass was topped up three months after its crops were cut.

| Date | Event | Anchor |
|---|---|---|
| 2026-03-24 | 519 crops extracted from the then-519-feature pass | `outputs/h11/pv-diag-384/crops/pro-medium-image-baseline/crops/` (519 PNGs) |
| 2026-03-24, 2026-05-06 | Flash and Pro verifier legs run over those 519 crops | `.../verified/*/run.meta.json` timestamps |
| 2026-06-03 | **Recovery**: 26 unretried tile failures resolved by resume-merge; geojson grew in place, 519 → 587 | commit `c07c57766` |
| 2026-06-03 12:32 UTC | Raw-pass condition re-evaluated on the recovered pass | `results/paper-eval/n1/384px-14buf-mcc/pro-image-medium-t-0-0/evaluation.json` |
| 2026-06-12 | Verified cells scored — still from the 2026-03-24 crop set | `results/verifier-robustness/evals/*/evaluation.json` |

Feature counts of `image-t0.0/run_1/detections_image-t0.0_run01.geojson`
recovered directly from git:

| Commit | Date | Features |
|---|---|--:|
| `3d22184d6` | 2026-04-15 | 519 |
| `49703010b` | 2026-05-06 | 519 |
| `c07c57766` | 2026-06-03 | **587** |
| `e612f7ac0` | 2026-08-18 | 587 |

The pass's own `recovery_history` block corroborates: `initial_failed` 26,
`recovered` 26, `still_failing` 0, at 2026-06-03T12:27:04Z, with 26 named
recovered tile ids — of which 18 yielded at least one detection. (The commit
message says "25/23" for the two pools; both passes' `recovery_history` records
26. A slip in the prose, not in the data — the artefact is authoritative.)

`c07c57766`'s message records the operation explicitly: *"both now
completed=487, failed=0 in a single round … merged into run_1 in place (geojson
grew, not clobbered; recovery_history recorded; pre-recovery state preserved in
git history). run_1 micro-F1@20m: text 0.763->0.776, image 0.606->0.624."*

The event was disclosed at the time. `docs/methodology/preregistration/protocol-errata.md:2093`
(E57, "Completeness addendum") and `docs/notes/working-notes.md:17352` (Obs 339)
both describe it. What was missing was any link **from the crop manifest** to
that disclosure — the manifest names a path and a count, and nothing else.

**The manifest was never wrong.** `total_detections = 519` is a correct record
of the pass as it stood when the crops were cut. The pass on disk is a correct
record of the pass as it stands now. Only their juxtaposition, absent a
timestamp, looked like a contradiction.

## 3. Are the artefacts sound? Yes — four checks, all clean

1. **The pre-recovery pass is an exact prefix of the current one.** Comparing
   the 519-feature blob at `49703010b` with the 587-feature file at `HEAD` on
   (x, y, source_tile) keys: 0 pre-only features, 68 post-only, and the
   pre-recovery sequence is a positional prefix of the post-recovery sequence.
   Tiles: 240 → 258, 18 new, 0 lost. The recovery was purely additive.
2. **The manifest's candidates match the pass exactly.** All 519 manifest
   `centroid_x`/`centroid_y` pairs agree with the corresponding features to
   within 1e-6, in order — and, because the addition is a prefix-preserving
   append, they agree with the **current** file's first 519 features too. Every
   crop PNG therefore depicts a detection that still exists at an unchanged
   location.
3. **The crop set is unfiltered.** 519 crops, 519 manifest candidates, 519
   source features, `failed_extractions = 0`, `missing_sources = []`. No
   thresholding or subsetting occurred.
4. **All three dependent rows reproduce from committed data.** Re-deriving each
   cell's accept count from its committed probabilities at its recorded
   threshold:

   | Verified cell | Threshold | Recomputed | Committed `n_detections` |
   |---|--:|--:|--:|
   | `pro-image-minimal-verifier` | 0.10 | 485 | 485 |
   | `pro-image-medium-verifier` | 0.05 | 463 | 463 |
   | `pro-medium-image-baseline-pro-verifier` | 0.05 | 465 | 465 |

   Exact matches. The scoring chain for these cells is sound.

## 4. Blast radius

### 4.1 Unaffected — the raw-pass condition is current

`pv-diag-384::baseline-pro-image-medium-t-0-0` derives from
`results/paper-eval/n1/384px-14buf-mcc/pro-image-medium-t-0-0/evaluation.json`,
generated 2026-06-03T12:32:32Z — four minutes after the recovery commit. Its
`per_run` block reads `n_detections` 587 / 544 / 544 with `n_runs = 3`, so it
already scores the recovered pass and all three passes. Its run_1 F1@20m of
**0.6243** matches the recovery commit's stated 0.624 exactly.

Four analyses in `results/analyses-manifest.json` consume that condition —
`n1-baseline-matrix-384`, `diversity-dividend-384`, `tile-size-sweep`,
`h6-a06-decision-rule`. **All four are clean.** Nothing in `docs/paper/**`
references the cell by name (grep over the five prose drafts under `docs/paper/`).

### 4.2 Stale but superseded — two 2026-05-06 leaderboards

Two boards were built before the recovery and still carry the pre-recovery
figure for the raw pass:

| Board | Built | Row | `n_detections` | F1@20m |
|---|---|---|--:|--:|
| `results/leaderboard/combined/era2/leaderboard_all_evaluations.json` | 2026-05-06T01:12:50Z | `h11-pvd-pro-medium-image-baseline` | 519 | 0.6059 |
| `results/leaderboard/per-architecture/era2/single-pass/leaderboard_all_evaluations.json` | 2026-05-06T09:33:36Z | same | 519 | 0.6059 |

Both are superseded by the 2026-06-03 paper-eval (587 features, 0.6243 for the
same pass). This is ordinary board staleness, not a D8 consequence, and it
resolves on the next rebuild. Reported only — `results/leaderboard/**` is owned
by a concurrent session.

### 4.3 The real residue — three `gs-era2` PV rows verified an 88.4 % feed

The three rows the register named are on
`results/metric-leaderboards/gs-era2-pv-family-30m.json`:

| Row | `n` | F1@30m | MCC |
|---|--:|--:|--:|
| `verified-adv-pro-image-baseline` | 485 | 0.7522 | 0.8232 |
| `verified-adv-pro-image-baseline-medium-vf` | 463 | 0.7617 | 0.8328 |
| `verified-adv-pro-image-baseline-pro-vf` | 465 | 0.7533 | 0.8328 |

They feed `unswept-pools-completeness` in `results/analyses-manifest.json`.

**Their numbers are not wrong.** Each is a correct evaluation of a correct
accepted set derived from a correct crop set (§ 3). What is true, and what
nothing in the committed artefacts currently says, is that their proposer feed
is **519 of the current pass's 587 features (88.4 %), covering 240 of 258
tiles**. The verifier never saw the 68 detections from the 18 recovered tiles.

Direction of the likely effect: on the raw pass the same 68 detections moved
F1@20m from 0.606 to 0.624 (+0.018), so the PV cells are, if anything, modestly
**understated** on recall. That is a bound-by-analogy, not a measurement.

## 5. Remediation

### 5.1 Done at $0 (this report)

- The provenance chain is established, anchored, and linked to E57 / Obs 339.
- The 519-feature feed is confirmed recoverable two ways: `git show
  49703010b:outputs/h11/pv-diag-384/pro-medium-image-baseline/image-t0.0/run_1/detections_image-t0.0_run01.geojson`,
  or equivalently the **first 519 features** of the current file (the append is
  prefix-preserving).

### 5.2 Handed to the deduplication correction campaign ($0, not this agent's file)

`dedup-correction-worklist-2026-08-18.md` § 2.8 and § 3.3 measured this pool's
feed on the **post-recovery 587-feature pass**, which is the wrong feed for a
question about crops and verifier cost. Reproducing the worklist's method
against both feeds (its 587-basis figures reproduce exactly, validating the
comparison):

| Basis | Feed | Deduplicated | Crops never extracted | Inflation | Crops whose centre moves |
|---|--:|--:|--:|--:|--:|
| As published (587, current pass) | 587 | 520 | 67 | 11.4 % | 64 |
| **Corrected (519, crop-pipeline feed)** | **519** | **465** | **54** | **10.4 %** | **53** |

Consequences for the worklist:

- § 2.8 and § 3.3's `pro-medium-image-baseline` rows should read 519 / 465 / 54
  / 10.4 % / 53. The other three baseline rows are already on the correct basis
  (`text-baseline` 1047 and `image-baseline` 746 both match their sources
  exactly; `pro-medium-text-baseline` 430 is the manifest count).
- § 3.4's three unresolved `pro-medium-image-baseline` cells are **no longer
  blocked**: the feed is the 519-feature blob, and § 3's check 4 shows the
  accept counts reproduce exactly. The nine-of-twelve resolution becomes
  twelve-of-twelve at $0.
- § 5.3 should be replaced by a pointer to this report.
- Tier C1's call count falls from (71 + 60 + 45 + 64) × 3 = 720 to
  (71 + 60 + 45 + **53**) × 3 = **687**.

### 5.3 Costed, NOT spent — bringing the three PV rows onto the full pass

To make the three `gs-era2` rows reflect the current 587-feature pass, the 68
recovered detections would need crops (free, local) and verification under each
of the three verifier variants.

Basis: `results/verifier-robustness/pareto/pareto_v2.json` `cost_model`, whose
`vf_call_usd = 0.000693` is already the **flex** rate (its own note records
"flex == batch pricing on Gemini 3", measured in
`reports/token-load-audit-2026-06-12.md`). The Pro leg is priced from its own
measured metadata — `verified/pro-medium-image-baseline-pro-verifier/run.meta.json`
records 10 requests using 17,920 input, 1,507 output and 4,013 thinking tokens
at $2.00/$12.00 per 1M, which is $0.010208 per call at list and $0.005104 at
flex once thinking is billed at the output rate.

| Leg | Model / thinking | Calls | Flex $/call | Flex $ |
|---|---|--:|--:|--:|
| `verified-adv-pro-image-baseline` | Flash, minimal | 68 | 0.000693 | 0.05 |
| `-medium-vf` | Flash, medium | 68 | 0.000693 | 0.05 |
| `-pro-vf` | Pro 3.1, medium | 68 | 0.005104 | 0.35 |
| **Total** | | **204** | | **≈ $0.45** |

Re-scoring is free on sapphire.

**Recommendation: do not spend this in isolation.** $0.45 buys currency on three
rows whose present numbers are already correct for the feed they name. If Tier
C1 of the deduplication campaign is ever executed, fold these 204 calls into
that queue (687 + 204 = 891 calls, ≈ $0.95 flex total) so the whole PV baseline
family moves onto one basis in one commit. Absent that, the honest and cheaper
disposition is a one-line provenance note on the three rows: *scored on the
2026-03-24 crop set, 519 of the pass's present 587 features.*

## 6. Two further instances found by a corpus sweep

Since the mechanism is "source regenerated after crops were cut", every crop
manifest in the corpus was checked against the source it names: 203 manifests,
104 exact matches, 91 explained by the k-of-N vote-threshold design pattern (the
manifest names the 1-of-N union geojson and counts the k-of-N subset), leaving
**4 anomalies and 4 dangling sources**.

| Manifest | Records | Source now holds | Diagnosis |
|---|--:|--:|---|
| `outputs/h11/pv-diag-384/crops/pro-medium-image-baseline/` | 519 | 587 | **D8** — recovery `c07c57766` |
| `outputs/h11/pv-diag-384/crops/pro-medium-text-baseline/` | 430 | (path gone) 446 | **Same event, same commit.** The manifest cites `pro-pilot-text/…`, a pool since renamed `pro-medium-text-baseline`; that pass went 430 → 446 in `c07c57766` |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10/crops/` | 802 | 889 | **Same class, different event.** `consensus_t1.geojson` was re-materialised 802 → 885 → 889 on 2026-07-30 (`f6116cba0`, `77bb342b4`) |
| `outputs/55maps-text-high-generalisation/crops/` | 9,205 | 9,206 | Off by one, manifest and source written in the same commit (`d7f85978d`). Unexplained; low priority |
| `outputs/h11/pv-diag-384/crops/text-1of5/`, `outputs/wbf/fh-text-n{5,30}/crops/` | 974 / 2,724 / 5,862 | source path absent | Dangling paths from directory moves |
| `outputs/h11/e47-propose-brief/crops/flash-high-text-1of5-v2-failed/` | `null` | 4,358 | Directory name declares the extraction failed |

The `pro-medium-text-baseline` case is why D8 surfaced on the image pool alone:
the worklist's analysis read the on-disk pass where the manifest's path resolved
(587, image) and fell back to the manifest count where it did not (430, text).
That mixed basis made one of four rows look anomalous when in fact **two** rows
were affected by the same recovery commit.

None of these are corruption. All are the same schema weakness — a manifest that
names a mutable path with no content hash, commit, or timestamp
(`scripts/extract_candidates.py:396-410`). That is registered as **D14**.

## 7. Reproduction

All measurement ran on **sapphire** (`ssh sapphire`, `~/Code/map-reader-llm`,
`source .venv/bin/activate`), at commit `e612f7ac0`. **Zero API calls.** Total
wall clock under two minutes. Three throwaway probes were used, each a thin
wrapper over committed library code and reproduced here in outline rather than
committed:

- the prefix and manifest-alignment check reads the pre-recovery blob via `git
  show 49703010b:<path>` and compares centroids from
  `merge_passes.centroid_from_geometry` unchanged;
- the feed correction calls `merge_passes.deduplicate_within_pass` unchanged and
  reproduces the worklist's published 587-basis row exactly before reporting the
  519-basis one;
- the corpus sweep globs `outputs/**/candidate_manifest.json`, compares
  `total_detections` against `len(features)` of the named `source_geojson`, and
  classifies the k-of-N pattern by regex on the manifest directory name.

## See also

- **Defect register**: `reports/defect-register-2026-08-18.md` — D8 (cleared
  here), D14 (the residual schema defect), D6 (the hypothesis this rules out).
- **Correction campaign**: `reports/dedup-correction-worklist-2026-08-18.md` —
  § 2.8, § 3.3, § 3.4 and § 5.3 carry the figures corrected in § 5.2 above.
- **Context in which D8 surfaced**: `reports/scoring-sensitivity-review-2026-08-18.md`.
- **Run output directory**: `outputs/h11/pv-diag-384/pro-medium-image-baseline/`
  and `outputs/h11/pv-diag-384/crops/pro-medium-image-baseline/`.
- **Working-notes Observations**: Obs 339 (`docs/notes/working-notes.md:17352`) —
  the n=3 top-up that triggered the recovery.
- **Decisions / Errata**: E57 (`docs/methodology/preregistration/protocol-errata.md:2093`,
  "Completeness addendum") — the canonical disclosure of the recovery itself.

## Changelog

### 2026-08-18 — Original publication

D8 investigated and cleared. Established from git history that the 519/587 gap
is the signature of recovery commit `c07c57766` (2026-06-03), which appended 68
detections to a pass whose crops had been extracted on 2026-03-24; confirmed the
addition is prefix-preserving, the crop manifest aligns exactly with the pass,
and all three dependent `gs-era2` rows reproduce their committed accept counts.
Falsified the D6 hypothesis (587 is a single-file count; the three-pass total is
1,675). Corrected the deduplication worklist's feed for this pool from 587 to
519 and unblocked its three unresolved § 3.4 cells at $0. Costed, and
recommended against, the $0.45 flex remediation that would bring the three PV
rows onto the full pass. A corpus sweep of 203 crop manifests found two further
instances of the same mechanism, registered as D14.
