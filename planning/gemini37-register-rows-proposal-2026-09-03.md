# Register rows for the Gemini 3.7 arc — proposal for PI signature

> **Last revised**: 2026-09-03 (original publication — proposal only;
> nothing is written to the register by this document).
> See [§ Changelog](#changelog) for revision history.

**What this is**: a row-by-row proposal the Principal Investigator (PI)
can walk interactively. Neither `results/conditions-manifest.json` (342
condition rows) nor `results/analyses-manifest.json` (39 analysis rows)
carries a single Gemini 3.7 row today — `grep -c "gemini37\|g37"`
returns 0 against both manifests **and** against the four
human-authored source-of-truth files (`results/run-conditions.json`,
`run-analyses.json`, `run-facts.json`, `run-registry.json`), so there
are no identifier collisions to work around.

**Where rows actually land.** The two manifests are *generated*.
`scripts/generate_post_run_report.py` is their only writer
(`MANIFEST_FILES`, line 1369–1375), and the sub-step-3c authoring
scripts (`scripts/register_pass1_author.py`,
`register_pass3_author.py`, `author_second_wave_registration.py`, …)
write into `results/run-conditions.json`, `run-registry.json`,
`run-facts.json`, and `run-analyses.json`, then the manifests are
regenerated. **This proposal therefore describes rows for the
`run-*.json` source files.**

⚠ **The manifests are already behind their sources.** Both were
generated 2026-08-24 (`ls -la results/`), while `run-conditions.json`
was last written 2026-08-28. Five runs
(`stride-phaseb-2026-08-25`, `stride-phasec-2026-08-25`,
`stride-55map-2026-08-25`, `image-b-gs-2026-08-28`,
`h7-escalation-2026-08-28`) and ten analyses already sit in the
sources and not in the manifests. Any regeneration for the 3.7 arc
will also publish those. Flagging so the PI is not surprised by a
+40-row diff.

**Anti-confabulation note.** Every number below was re-read from the
named file in the course of drafting this document. Where a campaign
card or an observation disagrees with the artefact, both are shown and
the disagreement is flagged in [§ 6](#6-disagreements-and-cross-checks).

## Terms expanded on first use

Gold Standard (GS); Ground Truth (GT); Matthews Correlation
Coefficient (MCC); confidence interval (CI); bias-corrected and
accelerated bootstrap (BCa); Benjamini–Hochberg (BH); False Discovery
Rate (FDR); minimum detectable effect at 80 % power (MDE80);
Principal Investigator (PI).

## 0. The two instruments — every row must declare one

The Obs 444 § (b) correction is load-bearing for this register. Three
distinct evaluation chains appear in the 3.7 arc, and a row that does
not name its chain is not auditable:

| Chain | Reference file | Scored by | Primary buffer |
|---|---|---|---|
| **GS curator** | `inputs/vectors/references/mounds-reference.geojson` | `image_b_analysis.py` sweep + `evaluate_detections.py` | 20 m |
| **55-map canonical** | canonical adjudicated extended GT, 5,160 refs at 50 m | `gemini37_sweep_oracle.py` / `corrected-f1.csv` | 50 m |
| **55-map standardised** | `inputs/vectors/references/best-available-gt-55maps.geojson` (ruling 21; 5,010 refs) | `scripts/evaluate_detections.py` | 50 m |

Session 144's interim headlines mixed chains 2 and 3. The correction
is recorded in `results/gemini37-55map-2026-08-31/findings.md`
§ "⚠ Reference instruments — read first" (lines 17–39) and in
**Obs 444 § (b)** (`docs/notes/working-notes.md`, Obs 444 starts at
line 30534). It is **not** in Obs 442 — see
[§ 6](#6-disagreements-and-cross-checks), item D5.

Precedent for dual registration: the incumbent 55-map cells carry
*two* rows per operating point, distinguished by a
`-canonical-gt` / `-standardised-gt` label suffix (e.g.
`stride-55map-2026-08-25::g384-ov192-55map-verified-carried-p0.15-k10-canonical-gt`
alongside
`stride-55map-2026-08-25::g384-ov192-55map-n5-carried-p0.15-k5-standardised-gt`).
This proposal follows that convention.

## 1. Inventory — proposed condition rows

### 1.1 Run rows required first

| Proposed `run_id` | `directory_path` | New? |
|---|---|---|
| `gemini37-screen-2026-08-28` | `outputs/gemini37-screen-2026-08-28` | new |
| `gemini37-55map-2026-08-29` | `outputs/gemini37-55map-2026-08-29` | new |
| `gemini37-image-gs-2026-09-01` | `outputs/gemini37-image-gs-2026-09-01` | new |
| `grid-2026-08-18` | `outputs/grid-2026-08-18` | **existing** |
| `stride-55map-2026-08-25` | `outputs/stride-55map-2026-08-25` | **existing** |

The fourth cell has **no output tree of its own**: its two
verifications live inside existing runs —
`outputs/grid-2026-08-18/verifier/g384_ov192/verify_37` (GS leg) and
`outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/verify_37`
(55-map leg). Proposal: register them as new `verifier_passes` entries
plus new conditions inside those two existing decompositions, which is
what the schema's "condition belongs to the proposer pool's run"
convention requires. **PI decision 6.**

Note the run-directory / results-directory skew: the 55-map campaign's
outputs are under `outputs/gemini37-55map-2026-08-29` while its results
are under `results/gemini37-55map-2026-08-31`. Precedent for the
mismatch exists (`55maps-text-high-t0-3-generalisation` →
`outputs/55maps-text-high-t0.3-generalisation`); `directory_path`
carries the truth.

### 1.2 Verifier configurations (read from `run.meta.json`)

Two configurations only, both `verify_adversarial-text` with identical
system-instruction hash `2518d5298d…`:

```json
{"variant": "v1", "instruction_file": "verify_adversarial.md",
 "model": "gemini-3-flash-preview", "thinking_level": "minimal",
 "temperature": 0.0, "iterations": 1}
```

```json
{"variant": "v1", "instruction_file": "verify_adversarial.md",
 "model": "gemini-3.7-flash", "thinking_level": "low",
 "temperature": 0.0, "iterations": 1}
```

Verified in `configuration.model` / `.thinking_level` / `.temperature`
/ `.system_instruction_hash` of every `verify*/run.meta.json` under
`outputs/gemini37-*/verifier/` and the two `verify_37` directories.

### 1.3 Tier A — GS cells (curator reference, 20 m, 487-tile common footprint)

All GS proposer pools are K = 5 or K = 10, `detect_brief-text`
(or `detect_brief-text-image`) byte-identical with two command-line
overrides `--model gemini-3.7-flash --thinking-level low`.
Architecture `proposer-verifier`, aggregation `verified` throughout.

| # | Proposed `condition_id` | Pool | n | Point | F1@20 | P | R | tile-MCC | n det | Source (JSON key) |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | `gemini37-screen-2026-08-28::g37-text-k5-verified-carried-p0.10-k5` | `g384_ov192_g37` | 5 | (0.10, k5) | 0.913892 | 0.898420 | 0.929907 | 0.779696 | 443 | `results/gemini37-screen-2026-08-28/analysis.json` → `image_best` |
| A2 | `gemini37-screen-2026-08-28::g37-text-k10-verified-carried-p0.10-k10` | `g384_ov192_g37` | 10 | (0.10, k10) | 0.914219 | 0.919622 | 0.908879 | 0.781683 | 423 | `.../k10/analysis.json` → `image_best` |
| A3 | `gemini37-screen-2026-08-28::g37-text-k5-verified-swap37-p0.80-k5` | `g384_ov192_g37` | 5 | (0.80, k5) | 0.926488 | 0.925408 | 0.927570 | 0.807772 | 429 | `.../swap37/analysis.json` → `image_best` |
| A4 | `gemini37-screen-2026-08-28::g37-text-ladder-n1-verified-carried-p0.15-k1` | `g384_ov192_g37` | 1 | (0.15, k1) | 0.858757 | 0.831510 | 0.887850 | 0.811564 | 457 | `.../k10/analysis.json` → `ladder.1.best` |
| A5 | `gemini37-screen-2026-08-28::g37-text-ladder-n3-verified-carried-p0.10-k3` | `g384_ov192_g37` | 3 | (0.10, k3) | 0.901826 | 0.881696 | 0.922897 | 0.788074 | 448 | `.../k10/analysis.json` → `ladder.3.best` |
| A6 | `gemini37-screen-2026-08-28::g37-text-ladder-n5-verified-carried-p0.10-k5` | `g384_ov192_g37` | 5 | (0.10, k5) | 0.913094 | 0.905747 | 0.920561 | 0.777108 | 435 | `.../k10/analysis.json` → `ladder.5.best` |
| A7 | `gemini37-image-gs-2026-09-01::g37-image-k5-verified-carried-p0.10-k5` | `g384_ov192_g37img` | 5 | (0.10, k5) | 0.925408 | 0.923256 | 0.927570 | 0.819173 | 430 | `results/gemini37-image-gs-2026-09-01/arm1/analysis.json` → `image_best` |
| A8 | `gemini37-image-gs-2026-09-01::g37-image-k5-verified-swap37-p0.90-k5` | `g384_ov192_g37img` | 5 | (0.90, k5) | 0.930832 | 0.934118 | 0.927570 | 0.832206 | 425 | `.../arm2/analysis.json` → `image_best` |
| A9 | `grid-2026-08-18::g384-ov192-k10-verified37-p0.98-k10` | `brief-text` | 10 | (0.98, k10) | 0.914005 | 0.963731 | 0.869159 | 0.823915 | 386 | `results/gemini37-fourth-cell/gs-leg/analysis.json` → `image_best` |

Verifier: A1, A2, A4–A7 use the carried `gemini-3-flash-preview`
config; A3, A8, A9 use the `gemini-3.7-flash` config.

**A1 versus A6 is a real distinction, not a duplicate.** Both read
"(0.10, k5) on the first five passes", but A1 is scored against the
K = 5 union's own verification (`verify/`, 791 items) and A6 against
the K = 10 re-verification (`verify_k10/`, 913 items) restricted to
the first five passes — different probability vintages, hence
443 versus 435 detections and 0.913892 versus 0.913094. Obs 441 § (b)
records the same 0.0003-scale distinction. If the PI prefers one, A6
is the ladder-internal comparator and A1 is the standalone screen
result; both are cited in Obs 441's tables.

**Detections cross-check** (per the standing feature-count rule):
`json.load(...)['features']` lengths are 443 / 423 / 429 / 386 / 430 /
425 for A1 / A2 / A3 / A9 / A7 / A8 against
`results/gemini37-screen-2026-08-28/verified_best_20m.geojson`,
`k10/…`, `swap37/…`, `results/gemini37-fourth-cell/gs-leg/…`, and the
two `results/gemini37-image-gs-2026-09-01/arm*/…` files — all match
the `n_detections` in the table. A4–A6 have **no materialised
GeoJSON** (see [§ 4](#4-gaps)).

**Blocking gap for all nine.** These sources carry F1 / P / R / MCC as
bare points. The condition schema requires
`metrics.tile_classification` with integer `tp`/`tn`/`fp`/`fn`, and the
house standard supplies a BCa CI per buffer. Neither exists on disk for
any 3.7 GS cell. The remedy is a $0 local re-score with
`scripts/evaluate_detections.py` against
`inputs/vectors/references/mounds-reference.geojson` with
`--bounds outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson
--buffers 5 10 15 20 25 30 35 40 45 50 75 100 125 150 --mcc
--bootstrap 10000 --seed 42`, exactly as
`results/image-b-gs-2026-08-28/best-eval/evaluation.json` was
produced (its `_metadata.cli_args` confirms those arguments).

### 1.4 Tier A — 55-map cells, both chains

Six rows: three cells × two chains. Canonical values come from
`primary/eval/corrected-f1.csv` (`R_m` = 50 row) and
`primary/eval/summary.json` (`results[2]`); standardised values from
`standardised-ref/evaluation.json` (`summary.buffers[9]`, i.e.
`buffer_metres` 50, and `summary.tile_classification`).

| # | Proposed `condition_id` | Cell | Point | Chain | F1@50 | 95 % CI | P | R | tile-MCC | n det |
|---|---|---|---|---|---|---|---|---|---|---|
| B1 | `gemini37-55map-2026-08-29::arm1-n5-carried-p0.10-k5-canonical-gt` | arm 1 | (0.10, k5) | canonical | 0.849360 | [0.841013, 0.857383] | 0.843756 | 0.855039 | 0.666469 | 5,229 |
| B2 | `gemini37-55map-2026-08-29::arm1-n5-carried-p0.10-k5-standardised-gt` | arm 1 | (0.10, k5) | standardised | 0.8550 | [0.8465, 0.8630] | 0.8371 | 0.8737 | 0.6665 | 5,229 |
| B3 | `gemini37-55map-2026-08-29::arm2-n5-carried-p0.80-k5-canonical-gt` | arm 2 | (0.80, k5) | canonical | 0.876316 | [0.868574, 0.883690] | 0.890066 | 0.862984 | 0.707291 | 5,003 |
| B4 | `gemini37-55map-2026-08-29::arm2-n5-carried-p0.80-k5-standardised-gt` | arm 2 | (0.80, k5) | standardised | 0.8825 | [0.8746, 0.8897] | 0.8831 | 0.8818 | 0.7073 | 5,003 |
| B5 | `stride-55map-2026-08-25::g384-ov192-55map-k10-verified37-p0.98-k10-canonical-gt` | fourth | (0.98, k10) | canonical | 0.865618 | [0.857387, 0.873612] | 0.958785 | 0.788953 | 0.726802 | 4,246 |
| B6 | `stride-55map-2026-08-25::g384-ov192-55map-k10-verified37-p0.98-k10-standardised-gt` | fourth | (0.98, k10) | standardised | 0.8732 | [0.8649, 0.8810] | 0.9517 | 0.8066 | 0.7268 | 4,246 |

Pools and passes: B1–B4 draw on `g384_ov192_55map_g37`, n_passes 5
(union 12,715 candidates, `verify_arm1`/`verify_arm2` both
`items_processed` 12,715, `items_failed` 0). B5–B6 draw on
`g384_ov192_55map`, n_passes 10 (union 57,482;
`verify_37/probabilities.json` `total_results` 57482).

**Tile-classification identity, verified.** For all three cells the
standardised `summary.tile_classification.confusion` is *byte-identical*
to the canonical `R_m` = 50 tile confusion: arm 1
tp 2533 / tn 4632 / fp 385 / fn 991; arm 2 2516 / 4798 / 219 / 1008;
fourth 2358 / 4985 / 32 / 1166. The two chains therefore share one
tile-level MCC per cell. Worth a PI eye — it is the expected behaviour
if tile occupancy is invariant to the two reference builds, but it has
not been asserted anywhere in the campaign documents.

**Detections cross-check**: `verified_detections.geojson` feature
counts are 5,229 / 5,003 / 4,246, matching `summary.n_detections` and
`sweep_oracle.json`'s `runs.*.carried.n_detections` exactly.

### 1.5 Tier B — cells with numbers but no registerable evidence

Eleven further 55-map cells appear on the 16-cell grid board
(`results/gemini37-55map-2026-08-31/grid-board/grid_board.json`,
`cells`), all on the **canonical** chain:

| Board label | Point | Basis | F1@50 | Tier | n det |
|---|---|---|---|---|---|
| `arm2-N5-oracle` | (0.95, k5) | oracle | 0.880603 | 1 | 4,924 |
| `arm2-N3-oracle` | (0.95, k3) | oracle | 0.879009 | 1 | 5,097 |
| `fourth-N10-oracle` | (0.96, k9) | oracle | 0.875816 | 2 | 4,495 |
| `arm2-N3-carried` | (0.80, k3) | carried-analogue | 0.874456 | 2 | 5,187 |
| `arm1-N5-oracle` | (0.15, k5) | oracle | 0.866203 | 3 | 4,616 |
| `arm1-N3-oracle` | (0.15, k3) | oracle | 0.864478 | 3 | 4,772 |
| `arm2-N1-oracle` | (0.98, k1) | oracle | 0.856301 | 3 | 5,021 |
| `arm2-N1-carried` | (0.80, k1) | carried-analogue | 0.842105 | 4 | 5,936 |
| `arm1-N3-carried` | (0.10, k3) | carried-analogue | 0.841759 | 5 | 5,482 |
| `arm1-N1-oracle` | (0.20, k1) | oracle | 0.837846 | 5 | 5,219 |
| `arm1-N1-carried` | (0.10, k1) | carried-analogue | 0.783418 | 6 | 6,660 |

Precision/recall exist for the seven *oracle* points only
(`sweeps/sweep_oracle.json` `runs.*.oracle`; `ladder/ladder.json`
`arms.*.N.oracle`; `results/gemini37-fourth-cell/55map/g384_ov192_55map/ladder.json`
`N.*.oracle`). The four `carried-analogue` cells carry **F1 and
n_detections only**. None of the eleven has a materialised detections
GeoJSON, an `evaluation.json`, a CI, or a tile confusion matrix — so
none can be authored against the schema as it stands. **PI decision 4.**

The equivalent Gemini-3 rungs *were* registered (see
`results/run-conditions.json` → `stride-55map-2026-08-25` →
labels `…-n1-oracle-…-standardised-gt`, `…-n3-oracle-…`,
`…-n5-carried-…`), but only after
`planning/55map-final-board-2026-08-27.md` § 3 materialised six
detection sets and scored them with `evaluate_detections.py`. That
card's § 2 (lines 33–47) is the precedent: N = 5 rows kept, N = 1 / 3
rows *added as oracle-only*, oracles redefined as
standardised-reference argmaxes.

**Tier A totals: 15 condition rows** (9 GS + 6 55-map).
**Tier B: 11 further cells**, blocked pending a materialisation pass.

## 2. Proposed analysis rows

Five rows. All conditions_compared use the Tier A identifiers above
plus existing registered identifiers, which are quoted verbatim from
`results/run-conditions.json`.

### R1 — `gemini37-screen-2026-08-28`

- **type**: `comparison`
- **conditions_compared**: A1, A2, A3, A4, A5, A6,
  `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10` (the committed
  Gemini-3 text-B anchor, F1@20 0.8961)
- **hypothesis_refs**: `[]`
- **preregistered**: **`post-hoc`** proposed — see PI decision 1
- **deviations**: `[]` (the K = 10 full-union re-verification instead
  of increment-stitching is disclosed on the card, lines 99–102; the
  PI may prefer an E-number)
- **predicted_outcome** (quote the card verbatim):
  `planning/gemini37-screen-2026-08-28.md:38–41` —
  "G1 Verified best @20 m | 3.7 at-or-below the Gemini 3 plateau
  (≤ 0.8934 + GS resolution); G2 Operating lattice | prob ∈ {0.15,
  0.20}, mid-to-high k; G3 Cost | proposer $5.5–16 flex; G4 Thinking
  at `low` | nonzero but < HIGH-class volumes (< 1,000 t/tile)", with
  the pre-named informative outcome at line 43: "3.7 ABOVE the plateau
  (verified best > 0.8961 + resolution)".
- **draft outcome**: "G1's pre-named informative outcome FIRED and G2
  is falsified. The carried-verifier K = 5 cell reaches 0.9139 @20 m at
  (0.10, k5) on a 791-candidate union, nominally above every Gemini-3
  cell on this corpus, but the paired tile-swap permutation (10,000
  draws, 487 tiles) returns +0.0178 at p = 0.1697 against a null SD of
  0.0129 — below the GS instrument's 50 %-power floor, so the screen
  can name the direction and not the size. K = 10 adds +0.0003
  (0.9142, p = 0.2076) and the ladder's own N5−N10 contrast is
  −0.0011 at p = 0.7928: **saturated by N = 5**, the Gemini-3 shape
  exactly (0.8588 / 0.9018 / 0.9131 / 0.9142 at N = 1/3/5/10). The
  headline is the role swap: re-verifying the *same* 791 candidates
  with gemini-3.7-flash reaches **0.9265 @20 m at (0.80, k5), P 0.9254
  / R 0.9276 / tile-MCC 0.8078 — +0.0304 vs the anchor, p = 0.0105**,
  the study's first GS-resolvable model-swap margin and the only cell
  in the arc beating the anchor on F1 and MCC together. The mechanism
  is calibration, not judgement: the 3.7 verifier's mean
  `mound_probability` is 0.687 against the carried verifier's 0.587 on
  identical candidates, so its optimum migrates four rungs up a lattice
  that has sat at 0.10–0.20 across every model the study has run — G2
  falsified, and the portable claim is that **a verifier's operating
  threshold does not transfer across verifier models**. Cost ordering
  is the practitioner lesson: five extra passes cost ≈ $5.4 and bought
  +0.0003; the role swap cost ≈ $0.7 and bought +0.0126 over the same
  union. Caveats: both sides of every contrast are sweep-selected
  argmaxes scored on the same reference, this is a single comparison
  with no family correction on four GS sheets, and 3.7-`low` emits 276
  thinking tokens/tile against Gemini-3 MINIMAL's zero, so model and
  thinking stay confounded. Obs 441."
- **paper_section**: `Results`
- **output_path**: `results/gemini37-screen-2026-08-28`
- **working_notes_obs**: `["Obs 441 — Gemini 3.7 Flash clears the
  Gemini 3 plateau but resolves only in the verifier role"]`

### R2 — `gemini37-55map-grid-2026-08-31`

The 2×2 proposer × verifier grid and its declared five-test family.

- **type**: `comparison`
- **conditions_compared**: B1, B3, B5 (canonical primaries) plus the
  registered incumbents
  `stride-55map-2026-08-25::g384-ov192-55map-verified-carried-p0.15-k10-canonical-gt`
  and
  `stride-55map-2026-08-25::g384-ov192-55map-n5-carried-p0.15-k5-standardised-gt`
  — **but see PI decision 3**: the canonical B N = 5 comparator
  (0.8437752627324171, sourced by
  `sweeps/sweep_oracle.json` `incumbents.BN5` from
  `results/55map-final-board-2026-08-27/cells/B-N5-carried/detections.geojson`
  and reproduced in `results/stride55-2026-08-27/ladder.json`) has **no
  registered condition row on the canonical chain**. The registered
  B-N5 row is standardised (0.8502). Registering a canonical B-N5
  companion row would make this analysis's foreign keys honest.
- **hypothesis_refs**: `[]`
- **preregistered**: **`post-hoc`** proposed (PI decision 1)
- **deviations**: `[]` — but consider an erratum for the S144
  instrument mixing, which the campaign self-corrected
- **predicted_outcome** (verbatim, `planning/gemini37-55map-2026-08-29.md`):
  `:41` "D1 Headline vs B-Gemini-3 | 3.7 carried ABOVE B-N5-carried
  0.8502 by ≥ MDE80 0.013 — a resolvable win"; `:42` "D2 Direction of
  the gain | recall-led"; `:43` "D3 Operating lattice | prob_t ∈
  {0.10, 0.15}, k4–k5"; `:44` "D4 Thinking volume | ≈ the GS-measured
  276 t/tile"; `:45` "D5 Cost | within § 4's envelope"; `:47`
  pre-named informative failure "3.7 ≈ Gemini 3 at deployment (|Δ| <
  MDE80 against B-N5-carried)"; `:152` "D6 Arm 2 vs arm 1 at deployment
  | arm 2 ahead by ≈ +0.013 — at the MDE80 boundary, direction
  positive"; `:153` "D7 Arm-2 lattice | oracle prob_t stays high
  (≥ 0.6)".
- **draft outcome**: "The complete proposer × verifier 2×2, every
  corner at an operating point committed on the card before any
  deployment scoring (`:140–141` for both arms, `:201` for the fourth
  cell's (0.98, k10) fixed from a separate ≈ $3 GS calibration leg).
  Canonical chain, corrected-F1 @50 m against the adjudicated extended
  GT (5,160 references), per-sheet paired sign-swap permutation
  (10,000 draws, seed 42) with BH-FDR at q = 0.05 over the declared
  five-test family: arm 1 (3.7 proposer + carried Gemini-3 verifier)
  0.8494, arm 2 (all-3.7) 0.8763, fourth cell (Gemini-3 K = 10 union +
  3.7 verifier) 0.8656, against incumbents B N = 5 0.8438 and
  B K = 10 0.8422. **The family gain lives in the verifier seat on the
  complete grid, not on one diagonal**: both verifier-axis tests are
  BH-significant (arm 2 − arm 1 +0.0270, p = 0.0001; fourth − B K = 10
  +0.0234, p = 0.0001) and neither proposer-axis test is (arm 1 − B N =
  5 +0.0056, p = 0.3488; arm 2 − fourth +0.0107, p = 0.0738); the
  all-3.7 diagonal reads +0.0325, p = 0.0001. **D1 is the pre-named
  informative failure** — the GS proposer-seat gain (+0.018) did not
  transfer as a resolvable deployment win against a 55-map MDE80 of
  0.013 — while **D6 is confirmed at twice its predicted magnitude**;
  D2, D3, D7 confirmed, D4 confirmed at 265–277 t/call, D5 a
  provisional token-basis pass (proposer $144 against a $93–150
  envelope; verifier arms $12.54 and $14.31). The fourth cell takes
  the grid's precision (0.9588) and tile-MCC (0.7268) crowns: the
  discriminating 3.7 verifier trades recall for precision hard on a
  noisy pool, which is the calibration story pointed the other way.
  On the board's own standardised instrument arm 2 reads 0.8825
  [0.8746, 0.8897] — **+0.0267 above the entire final board including
  its oracles** (ceiling B-N10-oracle 0.8558) — the fourth cell 0.8732,
  and arm 1 0.8550 against B-N5-carried 0.8502 with overlapping CIs;
  the instrument offset is a roughly uniform +0.005–0.006, which is why
  nothing substantive moves between chains. Caveat carried forward: the
  grid is **not square in pass count** (the Gemini-3 row is K = 10, the
  3.7 row K = 5), which is why the two proposer-axis tests use
  different comparators. Obs 444."
- **paper_section**: `Results`
- **output_path**: `results/gemini37-55map-2026-08-31`
- **working_notes_obs**: `["Obs 444 — the complete proposer × verifier
  2×2: the family gain lives in the verifier seat"]`

### R3 — `gemini37-55map-gridboard-2026-08-31`

The 16-cell grid board, its carried→oracle contrasts and its ladder.
Separable from R2 because it is a `leaderboard`, and because it is the
row whose `conditions_compared` depends on PI decision 4.

- **type**: `leaderboard`
- **conditions_compared**: B1, B3, B5 plus whichever Tier B cells the
  PI rules registerable; the two incumbents. **If Tier B stays
  unregistered this row still validates** (it needs ≥ 1 condition), and
  the oracle/rung cells are described in `outcome` as re-derived, which
  is the treatment `planning/55map-final-board-2026-08-27.md` § 2 gave
  the Gemini-3 N = 1/3 rungs before they were materialised.
- **hypothesis_refs**: `[]`; **preregistered**: `post-hoc`
- **predicted_outcome**: `null` (the board was not pre-registered as a
  prediction; the card's queued-oracle question is asked, not bet on)
- **tie_set**: candidate — the six greedy-clique tiers are
  `[["arm2-N5-oracle","arm2-N3-oracle"], ["arm2-N5-carried",
  "fourth-N10-oracle","arm2-N3-carried"], …]`; only tiers whose members
  are registered conditions can be expressed, so the tie_set is
  contingent on decision 4.
- **draft outcome**: "120 pairs, 89 BH-significant, six greedy-clique
  tiers on the canonical chain. **All seven carried→oracle contrasts
  are BH-significant**, including arm 2's +0.0043 (adjusted p =
  0.000162) — threshold-transfer costs are sheet-consistent real
  effects at every scale, even where practically negligible — and the
  gap shrinks with N in both arms (arm 1 +0.0544/+0.0227/+0.0168,
  arm 2 +0.0142/+0.0046/+0.0043 at N = 1/3/5), so **consensus
  partially substitutes for a correctly calibrated probability
  threshold**, while the cross-model arm pays roughly four times the
  same-model arm's tax at every rung. Saturation at N = 3 is now
  *tested* and *arm-specific*: arm 2's N3→N5 is non-significant on
  both bases (carried adjusted p = 0.258824, oracle 0.335192) and the
  fourth cell's independent ladder saturates identically (N = 3
  0.8688 against N = 5 0.8697, oracle prob_t pinned at 0.96 on every
  rung), whereas arm 1's carried N3→N5 *is* significant at +0.0076
  (adjusted p = 0.000162). Tier structure: Tier 1 is arm 2's N5 and N3
  oracles alone; Tier 2 holds arm2-N5-carried, fourth-N10-oracle and
  **arm2-N3-carried at 3/5 the proposer spend**; **both Gemini-3
  incumbents sit in Tier 4 of six**. The N = 1 economy is an *oracle*
  statement — a single 3.7 pass under the 3.7 verifier reaches 0.8563
  at its rung oracle, beating the canonical five-pass incumbent 0.8438
  on ~one-fifth the proposer spend, but the honest carried N = 1 reads
  0.8421, a Tier 4 tie with the very incumbents it is set against, and
  rung oracles below N = 5 are descriptive by the screening protocol.
  Obs 444 § (c)–(d)."
- **paper_section**: `Results`
- **output_path**: `results/gemini37-55map-2026-08-31/grid-board`
- **working_notes_obs**: as R2

### R4 — `gemini37-image-gs-2026-09-01`

- **type**: `comparison`
- **conditions_compared**: A7, A8, A1, A3,
  `image-b-gs-2026-08-28::g384-ov192-image-min-k10-verified-p0.15-k9`
  (the committed Gemini-3 image anchor, 0.8412), and
  `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10` (the 0.8961
  text-B anchor)
- **hypothesis_refs**: `["H1"]` proposed — H1 is the modality
  hypothesis, and `image-b-modality-2026-08-28` carries `["H1"]` for
  the Gemini-3 half of this exact difference-in-differences. **PI
  decision 2.**
- **preregistered**: `post-hoc` proposed (PI decision 1); note that
  the Gemini-3 sibling row carries `registered-exploratory`
- **predicted_outcome** (verbatim,
  `planning/gemini37-image-gs-2026-08-30.md`): `:44` "I1 Family gain on
  image | 3.7-image verified best ABOVE the G3 image anchor 0.8412";
  `:45` "I2 The gap | (text − image) within 3.7 NARROWER than 0.0549 by
  more than the resolution — i.e. gap < ~0.031"; `:46` "I3 Lattices |
  carried-verifier arm optimum at prob ∈ {0.10–0.20}, mid-to-high k;
  3.7-verifier arm optimum at prob_t ≥ 0.6"; `:47` "I4 Thinking at
  `low` on image prompts | nonzero, < 1,000 t/tile, ≈ the text
  screen's 276"; `:48` "I5 Cost and caching | implicit caching engages
  as on G3 (cached fraction ≥ 90 % of input)".
- **draft outcome**: "**The modality gap is eliminated at Gemini 3.7.**
  A difference-in-differences on one geometry and one reference:
  (text − image) within Gemini 3 was +0.0549 at p = 0.001; within 3.7
  it is **−0.0115 (p = 0.2533) on the carried-verifier pair and
  −0.0043 (p = 0.6767) on the all-3.7 pair** — a gap change of −0.059
  to −0.066, roughly 2.5× the GS verified-set resolution (MDE80 ≈
  0.024), so a resolved change and not instrument noise. **The honest
  claim is parity, not inversion**: image leads nominally in both
  pairs and neither sign flip is close to significant. I2 predicted
  the gap would land below ~0.031 and the outcome overshot to zero.
  I1 is confirmed at ~5× the text-side family gain — 3.7-image reaches
  0.9254 (carried verifier) and 0.9308 (3.7 verifier) against the
  0.8412 Gemini-3 image anchor, gains of +0.0842/+0.0896 where the
  same family step on text was +0.018 — so **the gap closed because
  image caught up, not because text regressed**, and the 3 → 3.7 step
  delivers most of its value where pixels are read. I3 confirmed
  exactly at (0.10, k5) and (0.90, k5): the 3.7 verifier's
  high-probability calibration shift replicates on image candidates,
  a second instrument for the non-transferring-threshold claim. I4
  confirmed and lighter than predicted (88–157 t/call). **I5 is an
  informative failure** — implicit caching engaged at 79.5 % of input
  against a registered ≥ 90 % bar, with the probe warm-up-confounded
  (16 % cold-parallel, 54 % sequential), yet the proposer side cost
  $22.50 token-basis against a $32–36 projection. **The escalation
  trigger is NOT met**: all-3.7 image 0.9308 against the all-3.7 text
  swap 0.9265 is +0.0043 at p = 0.677, far inside MDE80, no resolvable
  new high, so the 55-map image extension does not proceed. A methods
  warning attaches: `scripts/image_b_analysis.py:79` hard-codes
  `ANCHOR_F1_20 = 0.8961`, so the built-in `head_to_head_20m` blocks
  in `arm1/analysis.json` and `arm2/analysis.json` (−0.0293 p = 0.0235;
  −0.0347 p = 0.0065) pair a 3.7 image cell against a *Gemini-3* text
  cell and mix the family step into the modality contrast — the I2
  verdict uses the within-family pairs in `gap_test.json`, and any
  future reader quoting a modality delta off this campaign must check
  which anchor it was paired against. **Obliges the paper**: the
  study's 'text examples beat image examples' claim must be reframed
  as Gemini-3-specific. Obs 447."
- **paper_section**: `Results`
- **output_path**: `results/gemini37-image-gs-2026-09-01`
- **working_notes_obs**: `["Obs 447 — the modality gap is eliminated at
  Gemini 3.7"]`

### R5 — `gemini37-fourth-cell-gs-leg-2026-08-31`

Optional; folds into R2 if the PI prefers four rows.

- **type**: `diagnostic`
- **conditions_compared**: A9,
  `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10`
- **hypothesis_refs**: `[]`; **preregistered**: `post-hoc`
- **predicted_outcome**: `null` — this was a calibration leg run
  *to fix* the fourth cell's carried point, not a bet.
  Registering it with `predicted_outcome: null` is the honest option;
  a retrospective quotation would be a Session-143-style authoring
  disclosure (cf. `h13-overlap-2026-08-18`).
- **draft outcome**: "A ≈ $3 GS calibration leg run before the 55-map
  fourth cell so its operating point would be a carry-forward, not an
  argmax: the Gemini-3 grid `g384_ov192` K = 10 union (3,319
  candidates) re-verified with the 3.7 verifier reaches **0.9140 @20 m
  at (0.98, k10), P 0.9638 / R 0.8692 / tile-MCC 0.8239** against the
  0.8961 text-B anchor (+0.0179, p = 0.0563 on 10,000 permutations
  over 487 tiles). The lattice moves the whole way to the scale's top:
  the 3.7 verifier's mean probability is 0.209 on the noisy Gemini-3
  pool against 0.687 on its own union, so the same verifier calibrates
  *differently against different candidate pools* — the
  threshold-transfer claim extended from model to pool. (0.98, k10) was
  committed as the 55-map fourth cell's carried point at
  `planning/gemini37-55map-2026-08-29.md:201` before any deployment
  scoring."
- **paper_section**: `Methods`
- **output_path**: `results/gemini37-fourth-cell/gs-leg`
- **working_notes_obs**: `["Obs 444 — the complete proposer × verifier
  2×2 (§ (e), campaign mechanics)"]`

## 3. PI decisions required

1. **The `preregistered` label for every 3.7 analysis row.**
   *Rule*: vocabulary v2 (`docs/manifest-schemas/analyses-manifest.schema.json`,
   `preregistered` enum) offers `confirmatory`,
   `confirmatory-with-deviation`, `registered-exploratory`,
   `post-hoc`, `not-executed`, `null`. Its own S134 sorting rule says
   "extending a registered method to an unregistered factor, corpus,
   or pool is post-hoc".
   *Reason*: these were **post-registration campaigns with
   pre-committed predictions** (G1–G4, D1–D7, I1–I5, all committed by
   commit before launch). The register has gone both ways on that
   pattern: `image-b-modality-2026-08-28` and
   `image-b-thinking-pair-2026-08-28` are `registered-exploratory`
   ("predictions IP1-IP5 registered by commit before launch"), while
   `flash35-model-roles` — the *direct ancestor*, a proposer × verifier
   model-role 2×2 — is **`post-hoc`** with `hypothesis_refs: ["H2"]`.
   *What to check*: whether the preregistration registers any
   hypothesis about model version. If not, `post-hoc` per the sorting
   rule and the flash35 precedent, with the card's pre-commitment
   carried in `predicted_outcome` (which is where the foresight is
   evidenced, and is write-once). **Recommendation: `post-hoc`
   throughout**, so the arc's register semantics match the Flash-3.5
   arc it replicates and contradicts.

2. **Whether R4 (image) carries `hypothesis_refs: ["H1"]`.**
   *Rule*: `hypothesis_refs` is a human-authored controlled vocabulary,
   H1–H15 plus named programmes.
   *Reason*: R4 is literally the H1 modality contrast, re-run one model
   generation later, and its Gemini-3 half
   (`image-b-modality-2026-08-28`) carries `["H1"]`. Leaving it empty
   would orphan the finding from the hypothesis it overturns.
   *What to check*: that a `post-hoc` row is permitted to carry an
   H-number — it is; `flash35-model-roles` is `post-hoc` with `["H2"]`.

3. **Which chain is primary for the 55-map rows.**
   *Rule*: the register carries one row per (operating point,
   instrument), suffixed `-canonical-gt` / `-standardised-gt`.
   *Reason*: the campaign's committed primaries are **canonical**
   (the sweep harness's 1e-6 incumbent gate is anchored there —
   `scripts/gemini37_sweep_oracle.py`, cited in Obs 444), while the
   final board and every board rebuild are **standardised**. Obs 444
   § (b) says conclusions survive on both.
   *What to check*: (a) confirm both rows are wanted per cell (B1–B6 as
   proposed); (b) rule which one the paper's headline cites; (c)
   **decide whether to register a canonical B N = 5 incumbent
   companion row**, because R2's D1 comparator (0.8437752627324171)
   currently exists only inside
   `results/stride55-2026-08-27/ladder.json` and
   `sweeps/sweep_oracle.json` `incumbents.BN5`, with no condition row
   to point at.

4. **Whether Tier B (oracles and N = 1 / N = 3 rungs) gets condition
   rows or stays "re-derived".**
   *Rule*: `planning/55map-final-board-2026-08-27.md` § 2 (lines
   33–47) kept N = 5 rows and added N = 1 / N = 3 as **oracle-only**
   rows — but only after § 3 materialised detection GeoJSONs and
   scored them with `evaluate_detections.py`.
   *Reason*: the 3.7 rungs have no materialised detections and no
   evaluations; the four `carried-analogue` cells have F1 only. The
   schema requires a tile confusion matrix, so they cannot be
   registered as they stand.
   *What to check*: whether the board rebuild (§ 5) needs them as
   registered conditions. If yes, authorise the $0 materialise +
   `evaluate_detections.py` pass (compute on sapphire) before the
   register session; if no, R3's `outcome` describes them as re-derived
   and they stay out.

5. **Whether the image-GS cells register at all, given the escalation
   trigger was NOT met.**
   *Rule*: the register's unit is "one evaluable scored result", not
   "one result that changed a decision".
   *Reason*: the trigger governs *further spend*, not registration —
   and Obs 447 § (h) makes this campaign the reason a published claim
   must be reframed, which is exactly the kind of finding the register
   exists to anchor.
   *What to check*: that the PI is content for a not-escalated screen
   to sit on the GS leaderboard (§ 5, item 2). **Recommendation:
   register** — the negative escalation decision is itself a
   registered outcome.

6. **Where the fourth cell's two conditions live.**
   *Rule*: a condition's `run_id` is the run that owns its proposer
   pool; verifier variants are `verifier_passes` within that run's
   decomposition.
   *Reason*: the fourth cell is a re-verification of two *existing*
   Gemini-3 unions, and its outputs are physically inside
   `outputs/grid-2026-08-18/` and `outputs/stride-55map-2026-08-25/`.
   *What to check*: whether the PI prefers this (A9 under
   `grid-2026-08-18`, B5/B6 under `stride-55map-2026-08-25`) or a
   dedicated `gemini37-fourth-cell-2026-08-31` run row for campaign
   legibility. The former respects the schema's pool convention; the
   latter keeps the 3.7 arc greppable as one run family.

7. **Whether A1 and A6 both register** (the standalone K = 5 screen at
   0.913892 and the K = 10-vintage ladder N = 5 rung at 0.913094).
   *Rule*: one row per evaluable scored result.
   *Reason*: they are different verification vintages over the same
   five passes, and Obs 441 § (b) uses both.
   *What to check*: nothing on disk resolves this; it is a judgement
   about register density.

8. **Whether the 3.7 arc disturbs the H14 / H15 dispositions.**
   *Rule*: `h14-cross-model-consistency` and `h15-cross-model-voting`
   are `not-executed` disposition rows citing errata E76 / E77.
   *Reason*: H14 registers *cross-vendor* consistency (Claude / GPT);
   the 3.7 arc is within-vendor family stepping.
   *What to check*: confirm the dispositions stand unchanged, so a
   reader does not infer that the 3.7 grid discharged them.

## 4. Gaps

Stated plainly, in the order they will block the register session.

1. **No GS evaluations exist for any 3.7 GS cell (A1–A9).** The nine
   sources carry only point F1/P/R/MCC. The schema requires
   `metrics.tile_classification` with `tp`/`tn`/`fp`/`fn`, and the
   house standard supplies per-buffer BCa CIs. Fix: a $0 local
   `evaluate_detections.py` pass on the six committed
   `verified_best_20m.geojson` files, mirroring
   `results/image-b-gs-2026-08-28/best-eval/evaluation.json`.
2. **A4–A6 (the GS ladder rungs) have no materialised detections at
   all** — only the `ladder` block in `k10/analysis.json`. They need a
   materialisation step before they can be evaluated, or they stay out.
3. **Tier B (11 cells) has no detections, no evaluations, no CIs, and
   no tile matrices**; four of the eleven have F1 only, with no
   precision or recall anywhere on disk.
4. **The canonical B N = 5 incumbent has no condition row** — see PI
   decision 3(c).
5. **Cost fields cannot be reconstructed for three verifier stages.**
   `verify_swap37/run.meta.json` records `items_processed` 2 (the
   two-candidate cleanup pass overwrote the 789-item main pass);
   `outputs/stride-55map-2026-08-25/.../verify_37/run.meta.json`
   records `items_processed` 29 and `cost_estimate.total_cost_usd`
   $0.037501 — **round-7 usage only**, the storm-resilient loop driver
   having overwritten each round;
   `outputs/grid-2026-08-18/verifier/g384_ov192/verify_37/run.meta.json`
   records `items_processed` 1. The true item counts survive in
   `probabilities.json` (`total_results` 791 / 57,482 / 3,319), so the
   *condition* rows are safe; only cost provenance is lost. The
   per-invocation meta-stamping fix is still on the runner queue
   (continuity beacon, STATE AFTER S145).
6. **The live cost estimator mis-prices 3.7.** Obs 441 records that
   the runner prices the 3.7 SKU at Gemini-3 list rates and excludes
   thinking tokens, so every `cost_estimate` on a 3.7 run is an
   under-estimate. Nothing in the condition schema consumes cost, but
   any cost sentence in an `outcome` must say token-basis or billed.
7. **Billed-versus-token reconciliation is unfinished** — D5 is a
   *provisional* pass on the token basis. If the PI wants D5's verdict
   final in R2's `outcome`, that reconciliation is a prerequisite.

## 5. Sequencing — which rebuild consumes which row

The 55-map campaign card records both rebuilds as PI-directed
2026-09-02 and NOT started
(`planning/gemini37-55map-2026-08-29.md:168–188`), with the explicit
rule at `:187` — "register rows first (boards build from registered
conditions), then membership rulings, then rebuilds".

1. **55-map final-board fold-in** (standardised chain, the
   `planning/55map-final-board-2026-08-27.md` machinery). Consumes
   **B2, B4, B6** — the three standardised carried cells, whose
   evaluations are already banked (0.8550 / 0.8825 / 0.8732). If the
   PI's membership ruling adds oracles or N = 3 rungs, it *also*
   consumes Tier B, which then needs standardised evaluations that do
   not yet exist (only the canonical chain was swept for those cells) —
   so decision 4 is the gate on the fold-in's scope, and the added
   membership is a second materialisation pass, not a re-tiering.
2. **GS leaderboard refresh.** The card names five unboarded 3.7 GS
   cells (`:180–185`); this proposal supplies them as **A1, A3, A7,
   A8, A9** (text screen 0.9139; all-3.7 swap 0.9265; image arms
   0.9254 / 0.9308; fourth-cell GS leg 0.9140). The card's prediction
   that "the all-3.7 image cell would top the GS F1@20 ranking" is
   consistent with A8 at 0.930832. Both A2 (K = 10, 0.914219) and the
   ladder rungs A4–A6 are additional membership candidates, not
   required ones. Every one of these five needs gap 1 closed first.
3. **The student-baseline programme already consumes B3/B4** — its
   card cites `results/gemini37-55map-2026-08-31/` as the model arm
   (`planning/student-baseline-2026-08-31.md:8`, `:250`), so the arm-2
   carried condition_id is a downstream dependency of Obs 443's
   comparison as well.

## 6. Disagreements and cross-checks

Everything below was found by re-reading artefacts against the cards
and observations.

- **D1 — `swap37` sweep argmax is a tie the card does not mention.**
  `swap37/sweep_20m.csv` contains two rows with identical
  F1 0.9264877479579929, P 0.9254079254079254, R 0.927570093457944 and
  429 detections, at `prob_t` **0.80** and **0.85**. `analysis.json`
  reports 0.8 and the card commits (0.80, k5). No consequence, but the
  register should not imply a unique argmax.
- **D2 — the image arm-2 argmax is likewise tied.**
  `arm2/sweep_20m.csv` has identical rows at `prob_t` 0.90 and 0.95
  (F1 0.9308323563892146, 425 detections); `analysis.json` reports 0.9
  and the findings table says (0.90, k5).
- **D3 — the analysis JSONs' key is named `image_best` on cells that
  are not image cells.** `results/gemini37-screen-2026-08-28/analysis.json`,
  `k10/`, `swap37/` and `results/gemini37-fourth-cell/gs-leg/analysis.json`
  are all **text** cells whose best point sits under `image_best` —
  the campaign reused `image_b_analysis.py`. Anyone reading the key
  name as a modality claim will be wrong. Worth a sentence in the
  provenance note of each affected row.
- **D4 — `head_to_head_20m` in the image analysis JSONs is
  mis-anchored** (Obs 447 § (f), reproduced here from
  `scripts/image_b_analysis.py:79`, `ANCHOR_F1_20 = 0.8961`). The
  register must never quote `arm1/analysis.json` → `head_to_head_20m`
  (−0.029273, p = 0.0235) or `arm2/…` (−0.034697, p = 0.0065) as a
  modality delta; `gap_test.json` is the instrument.
- **D5 — the task brief's pointer to Obs 442 is wrong.** Obs 442
  (`docs/notes/working-notes.md:30048`) is *"The four GS sheets were
  randomly selected, not quality-selected"*. The reference-instrument
  correction is **Obs 444 § (b)** (`:30534`) and
  `results/gemini37-55map-2026-08-31/findings.md:17–39`. The
  continuity beacon's STATE AFTER S145 also attributes it to
  "Obs 442", so the mis-pointer is in the repository, not only in the
  brief — worth correcting at the beacon when it is next touched.
- **D6 — findings.md's `ladder.json` pointer for the canonical B N = 5
  incumbent resolves to a different file.** The value 0.843775 is in
  `results/stride55-2026-08-27/ladder.json`, not the campaign's own
  `ladder/ladder.json`. Obs 444's source block already records this
  correction; repeating it in the R2 provenance note would stop the
  next reader chasing it.
- **D7 — a resolved miscount, for the record.** The findings doc's
  original "five carried→oracle contrasts" was corrected to seven on
  2026-09-01; `grid_board.json` `named_contrasts` holds 15 entries of
  which **seven** are carried-versus-oracle, all significant. The
  current findings text says seven. No action.
- **Cross-check that passed** — every headline in
  `results/gemini37-55map-2026-08-31/findings.md` § Headlines
  reproduces its artefact to the digits shown (arm 1 0.8494/0.844/
  0.855/0.666; arm 2 0.8763/0.890/0.863/0.707; fourth
  0.8656/0.959/0.789/0.727), and every `n_detections` matches its
  GeoJSON feature count.

## Changelog

### 2026-09-03 — Original publication

Drafted from a full read of the four campaign cards, the four results
trees, Obs 441 / 442 / 444 / 447, the two manifest schemas, five
precedent authoring scripts, and the continuity beacon. Proposes 15
Tier A condition rows, flags 11 Tier B cells as blocked, proposes five
analysis rows, and records eight PI decisions, seven gaps, and seven
artefact-versus-document disagreements. Nothing written to the
register.
