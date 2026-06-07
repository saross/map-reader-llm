# The 55-map generalisation runs — identities, relationships, and assessment coverage

**Last updated**: 2026-06-07 (Session 105 — added the **two-reference (Track 1 /
Track 2) framing** and the **canonical extended-GT re-score**; see
§ "Two evaluation references"). Prior: 2026-06-02 (Session 95 follow-up).
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

## Two evaluation references — Track 1 (historical) and Track 2 (canonical)

Added Session 105 (2026-06-07). The 55-map deployment is reported against **two
ground-truth references, side by side**:

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

Both tracks use **one trusted engine** (`evaluate_detections` /
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
for the consolidation spec. Formal manifest registration of the seven
`@canonical-gt` conditions is pending (a bookkeeping step; the analysis is
complete and committed).

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
