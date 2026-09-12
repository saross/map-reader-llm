# Bootstrap CI store: path repair and E70 stale-source re-run

> **Last revised**: 2026-09-12 (original publication). See [§ Changelog](#changelog) for revision history.
>
> **Scope**: implements fix 1 of `reports/name-keyed-cache-audit-2026-09-12.md`
> § 5, under the Principal Investigator's (PI's) 2026-09-12 ruling that the
> store be made *wholly current* rather than annotated as partly uncitable.
> Every `path:line` and every number below was re-derived in this session
> against the files named. No Application Programming Interface (API) call was
> made; all compute ran on sapphire.

## 1. What was wrong

`results/all-bootstrap-cis.json` and `results/pv/all-bootstrap-cis.json` were
byte-identical copies of a 496-entry bootstrap confidence-interval (CI) store,
keyed by a condition path-string. Both are listed in
`results/ci-metadata-registry.md` as `YES`-complete, paper-citable CI sources.
Two independent defects, both established by
`reports/name-keyed-cache-audit-2026-09-12.md` § 4 Finding 1:

1. **Every** `source_file` named a path under `data/**` — a directory that has
   never existed in this repository. The registry's provenance chain
   (`results/ci-metadata-registry.md`, § "Provenance chains") recorded the same
   dead prefix, so a reader had no way to reach the raw detections at all.
2. **85 entries** recorded an `n_detections` smaller than their source file's
   feature count today. The March 2026 out-of-band tile-recovery campaign
   disclosed as **E70**
   (`docs/methodology/preregistration/protocol-errata.md:3154-3199`) appends
   recovered detections into the *existing* pass GeoJSON, so each of those 85
   CIs is a pre-recovery number serving under a post-recovery file's name. The
   class is a name-keyed derived artefact: nothing bound the entry to its
   input's content, and nothing in the pipeline ever performed the one-line
   cross-check that would have caught it.

## 2. Reproduction of the finding (step 1)

`scripts/check_bootstrap_cis.py --check` resolves each entry's `source_file`,
counts the GeoJSON's features, and compares with the recorded `n_detections`.
Run against the pre-repair store, now archived at
`archive/superseded-bootstrap-cis-2026-09-12/all-bootstrap-cis.json`:

| remap applied | resolved | unresolved | match | mismatch |
|---|---:|---:|---:|---:|
| `data/retest/` only (the audit's remap) | 456 | 40 | 371 | 85 |
| plus `data/consensus-proposers/` | 472 | 24 | 387 | 85 |

The first row **reproduces the audit exactly**: 456 / 40 / 371 / 85. The second
row is this session's addition — see § 3.

The mechanism reproduces too: of the 85 mismatching entries, **84 carry a
non-empty `patched` list** in their pass's `.tiles.json` sidecar (65 with one
patched tile, 15 with two, and one each with 3, 4, 10 and 15) and **one records
no patch at all** — `single:phase3c/track2-text/h9-E-p2/run_5`, whose source
nevertheless gained 119 features. That is precisely the 84-of-85 split the audit
reported.

One implementation note worth recording, because it is the kind of thing that
makes a check silently useless: `patched` in the sidecars is a **list of
recovered tile names**, not a count. A first version of the checker read it as a
scalar and reported `None` for all 85 entries — the diagnostic would have run
clean while telling the operator nothing. `tests/test_check_bootstrap_cis.py`
now pins the list shape.

## 3. Path repair (step 2)

`scripts/repair_bootstrap_cis.py repair-paths` rewrote both stores. Two prefix
remaps, each anchored in repository history rather than inferred from shape
alone:

| recorded prefix | repaired prefix | entries | anchor |
|---|---|---:|---|
| `data/retest/` | `outputs/retest/` | 456 | no `data/` directory has ever existed here; 371 of the 456 then match their recorded counts exactly |
| `data/consensus-proposers/` | `archive/outputs-experimental-pilot/pv/consensus-proposers/` | 16 | created at `outputs/pv/consensus-proposers/` by `2de117096` — the same commit that first wrote the CI store — and moved to the archive tree by `276e4ca80` |

The second remap is new in this session and reduces the audit's 40 unresolvable
entries to 24. It corroborates itself: **all 16 match their recorded
`n_detections` exactly** (503, 1082, 654, 1689, 847, 2617, 425, 547, 1678, 1607,
590, 1112, 946, 2419, 789, 11253), which a wrong mapping would not produce.

The **24 that remain unresolved** are the `consensus:consensus-n30:<family>/<k>of30`
entries (four families × six thresholds). Their `source_file` is a condition
label, not a path, because the N=30 consensus merge they scored was built in
memory by the March 2026 producer and never written to disk. They carry
`"source_status": "unresolved"` and cannot be re-verified against a file; a
grep for their recorded counts across `outputs/` and `archive/` found no
materialised merge matching them (the nearest candidates, the 16
consensus-proposer files, differ — e.g. `consensus-n30:high/25of30` records 421
against `3a-rep-high-25of30.geojson`'s 425).

Mechanics: `source_file_original` preserves the recorded string and is inserted
immediately after `source_file` so no other key moves; a top-level
`_path_repair` note records the date, the counts, both remaps and the audit
report's commit (`2fabf4e1d`). The committed files are
`json.dumps(..., indent=2)` with **no** trailing newline — verified
byte-identical on a no-op round trip before the first write — so the diff is
confined to changed fields. The subcommand is byte-idempotent.

## 4. Reproduction gate (step 3b)

Re-running any entry required identifying the estimator that produced the 411
entries left alone, since mixing two CI methods inside one store would be a
methodological error invisible to every existing gate. Two traps here:

- **The registry's source-script attribution was wrong.**
  `results/ci-metadata-registry.md:97` named
  `scripts/consolidate_pv_bootstrap_cis.py`. That script consolidates PV
  *threshold sweeps* and cannot write this schema; no committed script writes
  `_metadata.patched_consensus_count`, and `git log -S` finds it only in the two
  data commits. The March 2026 producer appears never to have been committed —
  its commit message (`2de117096`) says only "computed on sapphire".
- **The library function changed method.**
  `scripts/lib_advanced_metrics.py:1318` `bootstrap_ci` moved from the
  percentile method to Bias-Corrected and Accelerated (BCa) intervals on
  2026-04-29 (its own docstring, `:1332-1343`). Today's library would not
  reproduce a percentile-era store.

`scripts/repair_bootstrap_cis.py` therefore vendors the March estimator verbatim
from `git show 2de117096:scripts/lib_advanced_metrics.py` (`bootstrap_ci`, lines
554-632) and imports the per-tile true/false-positive machinery from the current
library, whose only change since March is an inert reference-column
auto-detection. The gate tests that claim rather than asserting it.

**Gate result — PASSED, 5 of 5, exactly.** Five already-matching entries, chosen
evenly through the store's key order so the gate spans phases, reproduced their
committed values to `|Δ| = 0.000e+00` on the mean and both bounds of all three
metrics:

| entry | verdict |
|---|---|
| `single:phase2a/brief-text/run_2` | reproduces, max \|Δ\| 0.000e+00 |
| `single:phase3a/track1-image/T1.0/run_25` | reproduces, max \|Δ\| 0.000e+00 |
| `single:phase3a/track2-text/T1.0/run_25` | reproduces, max \|Δ\| 0.000e+00 |
| `single:phase3a-high/track2-text/T1.0/run_12` | reproduces, max \|Δ\| 0.000e+00 |
| `single:phase3a-replication/minimal/run_28` | reproduces, max \|Δ\| 0.000e+00 |

Bit-exact reproduction pins every parameter at once: 1,000 tile-level
percentile resamples with replacement, `random_seed` 42, 20 m matching buffer,
reference `inputs/vectors/references/mounds-reference.geojson` (569 points,
EPSG:32635), bounds `inputs/vectors/bounds/full_evaluation_bounds.geojson` (340
tiles — the four-map retest corpus, **not** the 487-tile 384 px frame, which
would have failed). Wall time 4.7 s on 5 workers on sapphire.

## 5. The re-run (step 3c)

85 entries recomputed on their present source files, **37.6 s wall on 16 workers
on sapphire**, 0 errors. Each entry's superseded values moved into a `pre_e70`
sub-object (`n_detections`, `f1_mean`, `ci_low`, `ci_high`, `computed_at`) and
the new values were written in place with `n_detections` updated and a
`recomputed_at` timestamp; a top-level `_rerun` note records the estimator, its
pinned source, the frame, and the script.

### The 85 by run family

| run family | entries | detections added (min..max) | largest \|ΔF1 mean\| |
|---|---:|---:|---:|
| `phase3a/track1-image` | 44 | +1..+12 | 0.005727 |
| `phase2b/track1-image` | 7 | +1..+3 | 0.003400 |
| `phase2c/track1-image` | 5 | +1..+8 | 0.005726 |
| `phase2c/track2-text` | 5 | +2..+2 | 0.000599 |
| `phase3a/track2-text` | 4 | +2..+6 | 0.002914 |
| `phase3c/track2-text` | 4 | +16..+119 | 0.027611 |
| `phase2b/track2-text` | 3 | +1..+2 | 0.001032 |
| `phase3a-high/track2-text` | 3 | +3..+33 | 0.003888 |
| `phase2a/verbose-text-image` | 2 | +1..+2 | 0.000773 |
| `phase2c/track1-image-exploratory` | 2 | +2..+2 | 0.002336 |
| `phase2a/image-only` | 1 | +1..+1 | 0.001087 |
| `phase2d/track1-image` | 1 | +1..+1 | 0.000442 |
| `phase2e/canonical-first` | 1 | +3..+3 | 0.000187 |
| `phase2e/config-default` | 1 | +1..+1 | 0.001113 |
| `phase2e/random` | 1 | +1..+1 | 0.000442 |
| `phase3a-replication/minimal` | 1 | +1..+1 | 0.000403 |

464 detections were added across the 85. The concentration in
`phase3a/track1-image` (44 of 85) tracks the E70 campaign's own distribution
rather than anything about the CIs.

### Largest divergences, before → after

| entry | n | F1 mean | 95 % CI |
|---|---:|---|---|
| `single:phase3c/track2-text/h9-E-p2/run_5` | 1114 → 1233 (+119) | 0.453595 → 0.425984 (−0.027611) | [0.3946, 0.5086] → [0.3673, 0.4815] |
| `single:phase3c/track2-text/h9-B-v4/run_2` | 1340 → 1421 (+81) | 0.402443 → 0.386963 (−0.015480) | [0.3421, 0.4625] → [0.3261, 0.4439] |
| `single:phase3a-high/track2-text/T0.3/run_26` | 1108 → 1141 (+33) | 0.505245 → 0.503667 (−0.001579) | [0.4501, 0.5616] → [0.4504, 0.5590] |
| `single:phase3c/track2-text/h9-E-p2/run_3` | 1226 → 1259 (+33) | 0.437480 → 0.434049 (−0.003431) | [0.3793, 0.4928] → [0.3770, 0.4903] |
| `single:phase3c/track2-text/h9-E-p1/run_3` | 1210 → 1226 (+16) | 0.485275 → 0.480658 (−0.004617) | [0.4291, 0.5391] → [0.4241, 0.5345] |
| `single:phase3a-high/track2-text/T0.3/run_19` | 1189 → 1202 (+13) | 0.488229 → 0.484341 (−0.003888) | [0.4329, 0.5413] → [0.4297, 0.5370] |
| `single:phase3a/track1-image/T1.0/run_26` | 763 → 775 (+12) | 0.525698 → 0.531425 (+0.005727) | [0.4725, 0.5791] → [0.4786, 0.5834] |
| `single:phase2c/track1-image/canonical/run_1` | 712 → 720 (+8) | 0.574498 → 0.580225 (+0.005726) | [0.5283, 0.6225] → [0.5341, 0.6253] |

Across all 85 the median `|ΔF1 mean|` is **0.000583** and the maximum
**0.027611**; 81 of 85 moved by less than 0.005. Direction is mixed but skewed
down: 59 fell, 26 rose. That is the expected signature of recovered tiles adding
mostly false positives at the margin, and it means the stale numbers were
**optimistic** rather than pessimistic for the two largest cases.

**Note the audit's third-largest row has changed.** The audit's table (§ 4
Finding 1) gave `single:phase3c/track2-text/h9-E-p2/run_3` (+33) as third; this
session finds a fourth entry with the same +33,
`single:phase3a-high/track2-text/T0.3/run_26`, which the audit's three-row
excerpt did not list. Both are reported above. This is a difference in what the
audit chose to display, not a disagreement about the data.

## 6. What did NOT change

- **No CI value was altered outside the 85.** The 411 entries whose sources were
  already current were not recomputed and not touched: all 411 `f1`,
  `precision`, and `recall` blocks and all 411 `n_detections` values are
  **bit-identical** to the archived pre-repair file (checked field by field,
  2026-09-12).
- **The estimator did not change.** The 85 were re-run with the same percentile
  method, iteration count (1,000), seed (42), buffer (20 m), reference, and
  bounds as the 411, which is what the bit-exact gate establishes. The store
  remains internally consistent and remains "bootstrap percentile" in the
  registry.
- **No methodology, seed, or completeness state changed for any other row** of
  `results/ci-metadata-registry.md`.
- **The 24 unresolved entries' values were not touched.** They are flagged, not
  edited; re-running them would require reconstructing a consensus merge that
  was never written.
- **Nothing was deleted.** Both pre-repair stores are at
  `archive/superseded-bootstrap-cis-2026-09-12/` with a README and their
  SHA-256 (`dc6b3ce5f969c348a66ae4015b18d5070b7a5d8e13d2a24d45e0e9def1836b6f`,
  the same for both because they were byte-identical).

## 7. Is any pre-E70 value cited?

Swept every Markdown file under `docs/paper/**` and `results/**` (2,655 files,
excluding `results/ci-metadata-registry.md`, which documents the repair) for two
signatures: each of the 85 superseded values (F1 mean and both CI bounds) at
six-decimal precision, and each entry's condition id in three forms (full
condition path, last-two-segments, and the bare `h9-*` variant name).

**Result: no paper citation of a pre-E70 value was found. Zero value hits.**

Three condition-id hits exist and are *not* citations of the re-run values:

- `results/phase3c-diversity/track2-text/diversity-analysis-summary.md:14` and
  `:16`, and `results/phase3c-diversity/track1-image/diversity-analysis-summary.md:14`
  and `:17` — family-membership tables listing `h9-B-v1, ... h9-B-v5` and
  `h9-E-p1, ... h9-E-p5`. They name the variants, not their CIs.
- `results/retest/retest-production-summary.md:198-200` — a table of per-family
  mean F1: `h9-B-v1 to v5` 0.4105 (:198), `h9-D-t1 to t5` 0.4335 (:199),
  `h9-E-p1 to p5` 0.4217 (:200). Two of those three rows average over a run
  whose CI moved — B over `h9-B-v4/run_2`, E over `h9-E-p1/run_3`,
  `h9-E-p2/run_3` and `h9-E-p2/run_5`; the D row is unaffected. The document's
  own text defers the analysis ("Full analysis is deferred until all 100 runs
  are bootstrapped"), so nothing downstream depends on those means, but the B
  and E figures would move slightly if ever refreshed.
- `results/uplift-supplement/k1-gapfill/55maps-image-generalisation__verified-k3-canonical-gt/report_autogen.md:98`
  and `.../verified-k3-standardised-gt/report_autogen.md:58` — a coincidental
  substring match on `plus-hp/run_1` inside a 55-maps generalisation path. Not
  related.

A three-decimal sweep was run first and discarded as uninformative: 46,996 hits
across the tree, essentially all coincidence (a value like `0.631` appears
everywhere and rounds from countless unrelated metrics). Reporting those as
citations would have been false precision, so only six-decimal matches — which
are effectively unique to this store — are counted above.

### One downstream artefact does carry superseded values

Outside the Markdown scope, and worth the PI's attention:
`planning/condition-inventory.json` and
`planning/condition-inventory-with-s78.json` each hold **23 `existing_f1`
values** copied verbatim from the pre-repair store, so each now disagrees with
the store for 23 conditions. Largest divergences:
`phase2c/track1-image/canonical/run_1` (0.574498 → 0.580225),
`phase3c/track2-text/h9-E-p1/run_3` (0.485275 → 0.480658), and
`phase3a/track2-text/T0.7/run_17` (0.580688 → 0.583602); the rest move by less
than 0.003.

These are name-keyed copies of the same kind the audit is about:
`scripts/build_condition_inventory.py:492-503` copies the F1 mean and CI into
the inventory, which was last written 2026-04-25 (`03bf71c8f`). The audit
established that the only current consumer, `scripts/lib_c4_runners.py:18-26`,
reads the inventory to **count** matching rows and not to read F1, so nothing
acts on the stale numbers today. **Not changed here** — regenerating a planning
artefact is a separate decision, and the inventory is a dated snapshot whose
value is partly that it records what was known in April. Flagged for a ruling.

## 8. Guard against recurrence

`scripts/check_bootstrap_cis.py --check --allow-annotated results/all-bootstrap-cis.json`
now exits 0 with 472 resolved, 472 match, 0 mismatch, and 24 known-unresolved,
on both stores. `tests/test_check_bootstrap_cis.py` runs that check against both
committed stores as a **tier-1** test, so any future re-materialisation under an
existing `source_file` fails the per-commit gate instead of surfacing in a paper
six months later. `--allow-annotated` forgives only the 24 annotated unresolved
entries; a mismatch is never forgiven, and a test pins that a `pre_e70` block
does not excuse one.

34 tier-1 tests across `tests/test_check_bootstrap_cis.py` (16) and
`tests/test_repair_bootstrap_cis.py` (18), 3.7 s combined.

## Changelog

### 2026-09-12 — Original publication

Implements fix 1 of `reports/name-keyed-cache-audit-2026-09-12.md` § 5 under the
PI's 2026-09-12 ruling. Reproduced the audit's 456 / 40 / 371 / 85 counts,
repaired 472 dead `source_file` paths in both stores, passed a five-entry
bit-exact reproduction gate, re-ran the 85 E70-stale entries on sapphire (37.6 s,
16 workers, 0 errors), refreshed `results/ci-metadata-registry.md`, and added 34
tier-1 tests. Landed across commits `1cd205856` (checker), `c10bf91b2` (path
repair), `c50bd5f19` (note ordering), `8c89ccebb` (re-run and registry), and
`013b32bb1` (tests); this report's own commit is recorded in the next entry if
it is ever revised.
