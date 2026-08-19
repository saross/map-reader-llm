# The 55-map generalisation runs — identities, relationships, and assessment coverage

> **Last revised**: 2026-08-19 (Session 137 — **Track 3, the standardised
> reference, documented at last**; both references materialised as single
> scorable artefacts; all four 55-map boards re-tiered under Hsu MCB; two data
> hazards recorded). See [§ Changelog](#changelog) for revision history.

**Prior updates**: 2026-06-07 (Session 105 — the two-reference Track 1 / Track 2
framing and the canonical extended-GT re-score); 2026-06-02 (Session 95 follow-up).
**Purpose**: a single legible map of the five `55maps-*-generalisation` run
directories — what each one is, how they relate (one is a superseded original of
another), and which performance assessments each carries — so a reader (or
future-self) is not misled by the directory names. The 55-map corpus is the
**out-of-sample generalisation test**: 55 student-digitised maps, evaluated against
a student-annotated ground truth that contains digitisation errors (hence the
manual-review / corrected-F1 step below).

## The five directories

| directory (`outputs/`, `results/`) | what it is | distinct experiment? |
|---|---|---|
| `55maps-generalisation` | the **original** text (HIGH-thinking, T=0.7) generalisation run — `55maps-text-generalisation`, executed **2026-04-10** via bash scripts (`55maps-overnight.sh`) *before* the publishable `run_generalisation.py` launcher. Documented retrospectively (`outputs/55maps-generalisation/post_run_report_retrospective.md`). 4,068 verified. | **No — superseded** (see below) |
| `55maps-text-high-generalisation` | the **publishable** text-HIGH (T=0.7) run — the recovered/refreshed successor of the original (160 failed proposer passes recovered 2026-05-02; 4,068 → **4,164** verified). Same reconstruction config. | **Yes** (the T=0.7 text experiment) |
| `55maps-image-generalisation` | the image-track generalisation run. 4,680 verified. | **Yes** |
| `55maps-text-min-generalisation` | text, MINIMAL thinking. 3,865 verified. | **Yes** |
| `55maps-text-high-t0.3-generalisation` | text, HIGH thinking, **T=0.3** (vs the T=0.7 of `text-high`). 4,350 verified. | **Yes** |

## The superseded-original relationship (the one that trips people up)

`55maps-generalisation` and `55maps-text-high-generalisation` are the **same
experiment** (text, HIGH thinking, T=0.7): both reconstruct from the *same* config
(`configs/run-configs/55maps_text_generalisation_retrospective.yaml`), overlap 79 %
by tile, and report near-identical headline F1 (~0.790 @ 50 m). The base
`55maps-generalisation` is the **pre-recovery original**; `55maps-text-high-generalisation`
is its **recovered, publishable successor** (+160 recovered passes, +96 verified).

**Consequence**: the base run does **not** need its own manual review or
verifier-vs-human crosstab — those live under `55maps-text-high-generalisation`,
which is the cited version. Re-assessing the base would duplicate work on
superseded data. (`verified_detections_paired` is just the base run's verified-set
filename; the "paired" refers to its role in the paired-permutation comparisons,
not a distinct verifier.)

## The four distinct experiments and their assessment coverage

The four distinct generalisation experiments are **image, text-high (T=0.7),
text-min, and T=0.3**. All four carry the full assessment stack (verified
2026-06-02):

| run | manual review | verifier-vs-human 2×2 | DS-vs-human | corrected-F1 | Dawid-Skene | std re-score (14-buffer + MCC) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| image | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| text-high (T=0.7) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| text-min | ✓ | ✓ **(2026-06-02)** | ✓ | ✓ | ✓ | ✓ |
| T=0.3 | ✓ | ✓ **(2026-06-02)** | ✓ | ✓ | ✓ | ✓ |
| `55maps-generalisation` (superseded original) | — (carried by text-high) | — | — | — | original D-S | ✓ |

The **verifier-vs-human 2×2** for text-min and T=0.3 was completed on 2026-06-02
(`scripts/crosstab_verifier_vs_human.py`, commit `57fc1058`) — built from the
already-complete human-review CSVs (585 / 692 rows), **no new manual review
needed**. Text-track verifier ECE: text-min 0.096, T=0.3 0.090 (well-calibrated,
cf. the image track at 0.18–0.27 — see Obs 269/277 and `protocol-errata.md` E56).

## How the 55-map runs are assessed (the approach, in one place)

1. **Standardised re-score** at 14 uniform buffers + MCC against the reviewed
   student GT (Session 94/95).
2. **Manual review** of VLM-only candidates at five tolerance rings
   (`scripts/review_candidates.py`) → **corrected-F1** that credits real mounds
   the student GT missed or mis-placed (the student GT has ~25 m jitter and
   omissions — Obs 260).
3. **Dawid-Skene** 2-annotator model (student + VLM) as a model-based corrected F1.
4. **Verifier-vs-human 2×2 crosstab** (`crosstab_verifier_vs_human.py`):
   verifier probability vs the human label — the calibration check.

## Three evaluation references — Track 1 (historical), Track 2 (canonical), Track 3 (standardised)

Added Session 105 (2026-06-07) with two tracks; a third was created 2026-08-14
and is documented here from 2026-08-19. The 55-map deployment is reported against
**three ground-truth references**:

- **Track 1 — historical / as-measured.** The bare **reviewed student GT**
  (`student-mounds-55maps-reviewed.geojson`, 4,746 features). The honest "what a
  deployer measuring against the student digitisation alone would have seen."
  Already spec-complete: each carried condition at the full 14-buffer sweep +
  tile-MCC (`results/rescore-2026-05-31/<run>/verified*/evaluation.json`).
- **Track 2 — canonical / gold-standard-substitute (the paper reference).** The
  **canonical adjudicated extended GT** = reviewed student GT **+** the 773-mound
  deduplicated, adjudicated phantom set (`build_canonical_gt.py`,
  `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`). The
  phantom set **unions the earlier per-run manual corrections and the Session-104
  k3-shell corrections** into one point-per-feature reference, **per-buffer gated**
  (a phantom enters the GT at radius R only if its min-ring `buffer_metres ≤ R`;
  the 200 m ">150 m" sentinel shell is excluded everywhere). The earlier ad-hoc
  per-run corrections (`human-reviewed-corrected/`, `cleaned-gt-evaluation/`) are
  **folded into the canonical and superseded** — not reported as a third column.

- **Track 3 — standardised / best-available (the current reference).** Created
  2026-08-14 by applying PI ruling 21
  (`scripts/materialise_standardised_reference.py`,
  `results/deployment-oracle-2026-06-06/canonical-gt/standardised/`). Two layers:
  the student digitisation **standardised** (4,731 = 4,746 − 4 false positives −
  1 contradicted merge − 12 duplicates + 2 restored pre-merge originals) and an
  **extension** layer of 279 confirmed mounds the students missed (278 of the 773
  reviewed candidates that survived, plus one marking-pass extra), all at marked
  centres.

  Two properties matter for reuse. It is **buffer-invariant** — marked centres
  with no ring gate, so the same records are correct at every radius, unlike
  Track 2 — and it is explicitly a **best-possible reference, not a gold
  standard** (ruling 21b): mounds that both the students and every model missed
  are absent, because recovering them needs a fresh survey of the sheets. Its
  two-directional biases (≈370 residual long-range duplicates deflating recall;
  joint student+model false negatives inflating it ≈ 2.4–2.7 %) are set out in
  the layer README and must travel with any number computed against it.

### One-file references (added 2026-08-19)

Until Session 137 no reference existed as a **single scorable artefact**. Track 2
was a student GeoJSON plus an adjudication CSV to be gated per buffer; Track 3
was two layers in two formats. Since `evaluate_detections.py --ground-truth`
takes one path, neither could be scored through the generic engine, which is why
the four 55-map register boards could not be re-tiered under erratum E83 on the
first attempt.

`scripts/materialise_best_available_gt.py` now emits both, in GeoJSON and CSV:

| Artefact | Records | Vintage | Buffer |
|---|---:|---|---|
| `inputs/vectors/references/best-available-gt-55maps.{geojson,csv}` | **5,010** | Track 3 standardised (4,731 student + 279 extension) | invariant |
| `inputs/vectors/references/canonical-gt-55maps-r50.{geojson,csv}` | **5,161** | Track 2 canonical (4,746 student + 415 phantoms at ring ≤ 50 m) | **50 m only** |

Each record carries `gt_id`, `layer`, `symbol_code`, `source_map`, `symbol_type`,
`confidence_grade`, `position_source` and `provenance`, so provenance survives the
merge and a consumer can filter by positional quality without rejoining sources.
The canonical file is radius-stamped in its name because that vintage is
buffer-gated: a copy at 50 m is not valid at 75 m.

**Verified** against the committed boards before use: scoring
`55maps-text-high-t0.3-generalisation` k3 through the generic engine gives
F1@50 m = 0.8393 / MCC 0.689 against the standardised reference and 0.8476 /
0.690 against the canonical one, reproducing both committed cells exactly.

### Two hazards for anyone reusing these layers

- **`uuid` is a symbol code, not an identifier.** In the student layer 4,746
  records carry only 839 distinct `uuid` values, one repeated 1,152 times,
  because the field encodes the map-symbol type — every feature drawn with the
  same symbol shares a value. Geometries are all distinct, so nothing is corrupt,
  but any join or de-duplication keyed on `uuid` silently collapses rows. First
  flagged by the 2026-08-04 reference census; recorded as defect D21. The merged
  artefacts above key on `gt_id` and expose the field under its real name,
  `symbol_code`.
- **`buffer_metres` in `canonical-review.csv` is mixed-format** — both `"50"` and
  `"50.0"` occur. Parsing it with `int()` raises on the decimal rows, and
  catching that exception silently drops 33 of the 773 records. Parse through
  `float`.

Tracks 1 and 2 use **one trusted engine** (`evaluate_detections` /
`compute_corrected_f1_multi_buffer` — shared `calculate_f1_internal` and
`calculate_tile_classification`); **only the GT differs**, which is the clean
experimental control. Below 50 m the two tracks coincide exactly (no phantom has
a ring < 50 m, so the extended GT equals the student GT — verified: TH7-k4
F1@20m = 0.6260 and MCC@20m = 0.6480 reproduce the Track-1 manifest to 4 d.p.).
The Track-2 sweep reproduces findings §4b corrected-F1 @ 50 m to ~7 d.p. (the
validation gate, all 5 anchored cells).

### Track-2 results (canonical extended GT, corrected-F1 @ 50 m + tile-MCC)

Provenance: `results/55maps-extended-gt-2026-06-07/` (`TRACK2-SUMMARY.md`,
`consolidated-track2.csv`, per-cell `summary.json`); driver
`scripts/score_55maps_extended_gt_canonical.py`.

| cell | config | k | role | F1@50m | MCC@50m |
|---|---|---:|---|---:|---:|
| TH7-k4 | text-high T0.7 | 4 | carry-forward | 0.8152 | 0.6666 |
| TH7-k3 | text-high T0.7 | 3 | threshold | 0.8425 | 0.6796 |
| T03-k4 | text-high T0.3 | 4 | config | 0.8359 | 0.6711 |
| **T03-k3** | text-high T0.3 | 3 | **oracle** | **0.8476** | **0.6903** |
| TM-k4 | text-min | 4 | config | 0.7831 | 0.6411 |
| TM-k3 | text-min | 3 | threshold | 0.8127 | 0.6580 |
| IM-k3 | image | 3 | config | 0.7987 | **0.7104** |

**Three findings against the canonical GT:**

1. **Threshold axis (3-of-5 > carried 4-of-5)** holds for all three text configs
   — paired tile-swap permutation (`launch_threshold_permutations_canonical.sh`
   → `threshold-permutations/`), corrected-F1 @ 50 m, **all p<0.001**:
   TH7 ΔF1 +0.027 [+0.022, +0.033]; T03 +0.012 [+0.007, +0.017]; TM +0.030
   [+0.025, +0.035]. **MCC agrees** (k3 > k4 for all three), so the gain is not
   an F1/recall artefact.
2. **Carry-forward → oracle decomposition** (@ 50 m, from TH7-k4 = 0.8152):
   threshold alone (→ TH7-k3) **+0.027**; temperature alone (→ T03-k4) **+0.021**;
   both (→ oracle T03-k3) **+0.032** — sub-additive (the axes overlap), threshold
   slightly the larger lever. The carry-forward left **+0.032 corrected-F1** on the
   table (findings §4b, p<0.001).
3. **F1-vs-MCC divergence**: **image tops MCC (0.710)** despite mid-pack F1 — its
   tile-level discrimination (specificity) is strongest, echoing the Session-103
   F1-parity ≠ MCC-parity caveat. By F1 the oracle (T03-k3) leads; by MCC image
   does, with the oracle second.

See `results/deployment-oracle-2026-06-06/deployment-oracle-findings.md` for the
deployment-oracle write-up and `planning/55maps-gt-consolidation-spec-2026-06-07.md`
for the consolidation spec. The seven cells are **registered in the conditions
manifest** as `<run>::verified-{k4,k3}-canonical-gt` (e.g. the oracle
`55maps-text-high-t0-3-generalisation::verified-k3-canonical-gt`); the historical
`verified` conditions (Track 1) carry a cross-reference to them in
`run-conditions.json`.

## Bookkeeping notes / open items

- **GT harmonisation (2026-06-01)**: `55maps-text-high-t0.3` was re-scored against
  the **reviewed** GT (`student-mounds-55maps-reviewed.geojson`, 4,746 feats) to
  match the other four runs (it had used the non-reviewed 4,770-feat GT). Commit in
  the Session 95 sweep batch.
- **Carry-forward #10 (manifest scope)**: when the 55-map runs are authored into the
  manifest (Batch B, `planning/manifest-3b-conditions-plan.md`), the base
  `55maps-generalisation` condition (`verified_paired`) had its scope *inferred* —
  confirm it, and **decide whether to fold the superseded base into
  `55maps-text-high-generalisation` (as a `historical_alias`) or keep it as the
  cited original**. This is a manifest-decomposition item, NOT a review gap.

## Cross-references

- `outputs/55maps-generalisation/post_run_report_retrospective.md` — the base run's
  reconstructed audit trail.
- `planning/manifest-3b-conditions-plan.md` §Batch B; carry-forward #10.
- `docs/methodology/preregistration/protocol-errata.md` E56 (verifier threshold
  provenance / calibration).
- Obs 260 (student-GT jitter), Obs 269 + 277 (image-track verifier miscalibration).
- `planning/paper-writeup-continuity.md` Session 95 carry-forward to-dos.

## Board tiering under erratum E83 (2026-08-19)

All four 55-map register boards were re-tiered under the Hsu
multiple-comparisons-with-the-best admissible set, replacing the sequential
greedy-clique rule that defect D20 showed to be order-dependent. Each was scored
at its own **50 m** buffer against the matching materialised reference above,
with every cell reproducing its committed F1 to 0.0000.

| Board | Metric | Published tie set | Hsu MCB | Result |
|---|---|---:|---:|---|
| `55map-standardised-leaderboard-50m` | F1 | 2 | 2 | identical |
| `55map-standardised-leaderboard-mcc-50m` | MCC | 1 | 1 | identical |
| `55map-canonical-leaderboard-50m` | F1 | 2 | 2 | identical |
| `55map-canonical-leaderboard-mcc-50m` | MCC | 1 | 1 | identical |

**Membership is identical on all four**, so no published 55-map claim changes.
Notably the two MCC boards' **sole** Tier-1 cell survives the simultaneous
procedure, which the Era-1 leaderboard's sole-leader claim did not. Selection
optimism across the four is between +0.0000 and +0.0014, negligible against the
effects reported.

## Changelog

### 2026-08-19 — Track 3 documented; one-file references; boards re-tiered

**Trigger**: erratum E83 could not re-tier the 55-map boards because no reference
existed as a single scorable artefact, and the standardised reference created
2026-08-14 had never been documented here at all — this file still described the
corpus as a two-track study more than two months after it became three.

Added: Track 3 (standardised / best-available); the one-file references and their
verification against committed cells; the `uuid` symbol-code hazard (D21) and the
mixed-format `buffer_metres` hazard; the E83 tiering outcome for all four boards.

**What did NOT change**: no number in the Track-1 or Track-2 sections, no board
membership, no registered outcome. The tiering instrument changed and agreed with
what was published.
