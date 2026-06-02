# The 55-map generalisation runs — identities, relationships, and assessment coverage

**Last updated**: 2026-06-02 (Session 95 follow-up).
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
