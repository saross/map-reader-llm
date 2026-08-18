# Two scoring-path suspicions that cleared: calibration leakage and the detection-file naming split

> **Last revised**: 2026-08-18 (original publication — two negative results from
> the Session 136 scoring audit). See [§ Changelog](#changelog) for revision
> history.

**Date**: 2026-08-18 (Session 136)
**Author**: Claude Code (Opus 5), amd-tower; geometry recomputed on sapphire
**API spend**: US$0.00 — no model was called; every number below is recomputed
from committed inputs or read from committed text
**Purpose**: put two *negative* audit results on the record. Both were live
suspicions during the Session 136 scoring audit; both were checked and both
cleared. Neither warrants an erratum, and that is precisely why they need
writing down — a suspicion that is raised, resolved, and then forgotten gets
raised again, and the second time round there is no record that it was ever
answered.

The one finding from the same audit that *did* warrant an erratum — undefined
tile-level Matthews Correlation Coefficient (MCC) published as `0.0` — is
recorded as **E81** in
[`protocol-errata.md`](../docs/methodology/preregistration/protocol-errata.md),
not here.

---

## 1. The calibration exclusion is sound

**The suspicion**: the 20 calibration tiles and the 340 evaluation tiles are cut
from the same four map sheets. Because the study tiles at 12.5 % overlap in both
axes, calibration and evaluation tiles could share ground even when they share
no tile name — and if the model was shown calibration ground before being scored
on evaluation ground, the evaluation is contaminated.

**The verdict**: **cleared.** The exclusion is implemented at the tile level,
which is the level at which the model is shown data, and the residual areal
overlap is smaller than the overlap an evaluation tile already has with its own
neighbours.

### 1.1 What was recomputed

All figures below were recomputed from source on sapphire (`geopandas`,
EPSG:32635, areas by `unary_union`), after confirming by `md5sum` that the four
input files are byte-identical on amd-tower and sapphire. Sources:

| Quantity | Source file | Value |
|---|---|---|
| Calibration tiles | `inputs/tiles/calibration_manifest.json` | **20** |
| Calibration bounds features | `inputs/vectors/bounds/calibration_bounds.geojson` | 20 (tile-name set identical to the manifest) |
| Evaluation tiles (512 px) | `inputs/vectors/bounds/full_evaluation_bounds.geojson` | **340** |
| Evaluation tiles (384 px, Era 2) | `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` | **487** |

Derived:

| Measure | Value |
|---|---|
| Tile-name intersection, calibration × 512 px evaluation | **0** |
| Tile-name intersection, calibration × 384 px Era-2 evaluation | **0** |
| Calibration footprint | **129.3182 km²** |
| 512 px evaluation footprint | 1751.2430 km² |
| 384 px Era-2 evaluation footprint | 1415.8230 km² |
| Calibration ∩ 512 px evaluation | **50.1202 km² = 38.76 % of the calibration footprint** |
| Calibration ∩ 384 px Era-2 evaluation | **0.000000 km² = 0.0000 %** |
| Share of an evaluation tile's area covered by its own neighbours (n = 340) | median **43.75 %**, mean 41.10 %, min 12.50 %, max 97.81 % |

### 1.2 Why 38.8 % is not leakage

The 38.76 % areal share sounds alarming in isolation. It is not, because it is
*below* the overlap an evaluation tile already has with the rest of the
evaluation set. The median evaluation tile shares **43.75 %** of its own area
with its own neighbours — and that number is not an empirical accident but the
arithmetic of the tiling. With `TILE_SIZE = 512` and `OVERLAP = 64`
(`config.py:66-68`), an interior tile's neighbour-free core is
(512 − 2 × 64)² / 512² = (384/512)² = 56.25 % of its area, leaving exactly
43.75 % shared. The recomputed median matches to the digit.

So the calibration footprint's areal relationship to the evaluation footprint is
*weaker* than the relationship any two adjacent evaluation tiles already have
with each other. Whatever "sharing ground with a scored tile" means as a
contamination mechanism, it is a property the evaluation set has with itself, at
a higher rate, by design and by preregistration. It cannot be a
calibration-specific defect.

The substantive point is that the exclusion operates at the **tile** level. A
tile is the unit the model sees: it is handed one 512 × 512 px image and asked
about that image. No calibration tile image was ever scored, and no scored tile
image was ever used for calibration. Areal intersection of footprints is a
different and weaker relation than identity of inputs.

### 1.3 The 384 px corpus is stricter, not different-in-kind

The 384 px Era-2 487-tile footprint has **0.000000 km²** overlap with the
calibration footprint — not merely no shared tile names, but no shared ground at
all. `inputs/vectors/bounds/384/calibration_bounds.geojson` contains **0**
features, consistent with a corpus built to exclude calibration ground by area
rather than by tile identity.

This is a **difference between eras, not an error in either**. The 512 px corpus
excluded calibration tiles; the 384 px corpus additionally buffered out
calibration *area*. Both are defensible; the second is stricter. Anyone
comparing a 512 px result to a 384 px result should know that the two corpora
differ in this respect, but neither is contaminated.

---

## 2. The detection-file naming split did not reach committed results

**The suspicion**: two detection-file naming conventions coexist under
`outputs/`, and the scorer's default glob matches only one of them. If any
committed evaluation pointed at a directory holding the *other* convention, it
would have silently scored fewer passes than intended — an under-read that
produces a plausible-looking number with no error.

**The verdict**: **cleared for everything already committed; real as a
forward-looking hazard.**

### 2.1 The two conventions and the single writer that emits both

Both names are written by `scripts/4_detect_mounds_batch.py`:

- **Hyphen convention** — `:951`,
  `filename = f"detections-{version_tag}-{sanitized_model}-{current_date}.geojson"`,
  the default when no `output_name` is supplied.
- **Underscore convention** — `:1450` and `:1523`,
  `f"detections_{config_version}_run{run_number:02d}.geojson"`, written by the
  multi-run study path into a per-run directory.

Counts under `outputs/` at the time of writing (untracked trees included):
**815** files matching `detections_*.geojson`, **241** matching
`detections-*.geojson`. The hyphen-named files are concentrated in the recent
H13 and grid work.

`scripts/evaluate_detections.py` defaults its `--glob` to
`*/detections_*.geojson` (`:1299`, help text at `:1300-1303`; the same default
appears at `:362` and `:1625`). Underscore matches; hyphen does not. A
directory of hyphen-named passes handed to `--detections-dir` without an
explicit `--glob` would produce **zero** matches, or — worse for detectability —
a partial match if the directory happened to hold both conventions.

### 2.2 The audit

Every `evaluation.json` tracked under `results/` was re-read
(`git ls-files results`), its `_metadata.cli_args` inspected, and for every one
that used `--detections-dir` the recorded glob was re-executed against the
recorded directory and compared with every `*.geojson` present at the same path
depth. Any file whose basename began with `detections` but was missed by the
glob would count as an under-read.

| Quantity | Count |
|---|---|
| Tracked `results/**/evaluation.json` | 1673 |
| Used `--detections-dir` (glob-based, therefore in scope) | **156** |
| Used `--detections` / `--batch` (single artefact named explicitly, out of scope) | 1517 |
| `detections_dir` no longer present on disk | 0 |
| **Under-reads found** | **0** |

Glob patterns actually used by those 156 evaluations:

| Pattern | Count |
|---|---|
| `*/detections_*.geojson` (the default) | 105 |
| `replication_*/consensus_t{1..5}.geojson` | 45 (9 each) |
| `run_*/detections_*.geojson` | 4 |
| `accepted_run*.geojson` | 2 |

No committed evaluation pointed at a directory of hyphen-named artefacts. The
two conventions have so far stayed in disjoint parts of the tree: the
underscore convention is what the multi-run study path emits, and the multi-run
study path is what `--detections-dir` was built to consume.

### 2.3 Why this still needs recording

The hazard is real and it is silent. The glob returns an empty or short list;
nothing raises; the scorer reports whatever it found. The reason no committed
result is affected is a coincidence of which code path wrote which files, not a
guard. As the hyphen convention spreads — it is the *default* branch of the
filename builder, and it is what the recent H13 and grid runs emit — the chance
that someone points `--detections-dir` at a hyphen-named directory rises.

A resolver that recognises both conventions (or a hard failure when a glob
matches zero files) is the right fix, and is being handled as a separate change
rather than in this note. Until then, pass `--glob` explicitly whenever the
target directory was not written by the multi-run study path.

---

## 3. Summary

| Suspicion | Verdict | Erratum? |
|---|---|---|
| Calibration tiles leak into the evaluation corpus through overlap-band geometry | Cleared — exclusion is at the tile level; 38.76 % areal share is below the 43.75 % median an evaluation tile has with its own neighbours | No |
| The `detections_*` glob default under-read some committed evaluations | Cleared — 156 glob-based evaluations audited, 0 under-reads; hazard remains for future code | No |

---

## See also

- `docs/methodology/preregistration/protocol-errata.md` — **E81** (undefined
  tile MCC published as `0.0`), the one Session 136 scoring-audit finding that
  did require an erratum; E79 and E80 are the two scoring-path findings that
  preceded it
- `reports/scoring-sensitivity-review-2026-08-18.md` — the measurement review
  from the same audit
- `reports/dedup-gap-compliance-2026-08-18.md` — the compliance reading behind
  E80
- `results/dedup-metric-impact-2026-08-18/findings.md` — the deduplication
  impact campaign, § 2.6 of which first flagged the undefined-MCC infelicity

---

## Changelog

### 2026-08-18 — Original publication

Written to preserve two negative results from the Session 136 scoring audit that
would otherwise have been lost, since neither produced an erratum. Both were
verified independently rather than carried forward from the prior session's
notes: the calibration geometry was recomputed from
`inputs/tiles/calibration_manifest.json`,
`inputs/vectors/bounds/calibration_bounds.geojson`,
`inputs/vectors/bounds/full_evaluation_bounds.geojson`, and
`inputs/vectors/bounds/384/full_evaluation_bounds.geojson` on sapphire after an
`md5sum` cross-check against amd-tower; the glob audit was re-run across all
1673 tracked `results/**/evaluation.json`. Two figures were refined against the
values that prompted the check: the neighbour-share median is **43.75 %**, not
43.7 % (and it is exactly (1 − (384/512)²), the arithmetic of a 12.5 %-overlap
tiling, not an empirical near-miss), and the calibration ∩ evaluation share is
**38.76 %**, which rounds to the 38.8 % previously quoted. Everything else
reproduced as stated. Landed alongside erratum E81 in commit `503e21daf`.
