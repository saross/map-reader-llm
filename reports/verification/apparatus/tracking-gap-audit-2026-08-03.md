# Tracking-gap audit — untracked analysis artefacts under `outputs/` and `archive/`

> **Last revised**: 2026-08-03 (created; ruling 15 phase 1).
> See [§ Changelog](#changelog) for revision history.

**Mandate**: phase 3 ruling 15 (Programme Investigator (PI)-approved
2026-08-03), phase 1 — "tracking-gap audit + commit of small analysis-relevant
strays (the 044-class)". See `reports/verification/phase3-rulings-2026-07-31.md`
§ 15.

**Executed**: 2026-08-03, Session 125, at commit `fabd07a9d`. Both hosts were
swept: **amd-tower** locally and **sapphire** over `ssh` (read-only), both at
`fabd07a9d` after `git pull --ff-only`. Zero Application Programming Interface
(API) calls.

## Why both hosts

Observation 383 established that neither working tree is a superset of the
other, so a single-host sweep would have produced a single-host answer to a
cross-host question — the precise error Observation 385's fourth carry-forward
warns against. The audit confirmed the point concretely: the two
never-committed `044` anchors exist **only on amd-tower**, and six
`pv-diag-256` manifests exist **only on sapphire**. A sweep of either host
alone would have missed one group entirely.

## Method

For each host, at `fabd07a9d`:

```bash
find outputs archive -type f \( -name '*.json' -o -name '*.geojson' \) -printf '%s\t%p\n'
git ls-files outputs archive | grep -E '\.(json|geojson)$'
```

Untracked set = live set minus tracked set, per host; the audit population is
the **union** across hosts. `find` was run without `-L`, matching the census
convention fixed in Session 125 after Observation 385. A supplementary sweep
covered `*.csv`, `*.tsv`, `*.yaml`, `*.yml` under the same roots, and
`*.json`/`*.geojson`/`*.csv` under `results/`.

**An instrument bug found in the audit's own first pass.** The sweep initially
used `find ... -size -5M` to impose the 5 MB ceiling. GNU `find` rounds `-size`
**up** to whole units, so `-5M` means "fewer than five whole megabytes after
rounding up" — and `outputs/wbf/fh-text-n30/crops/candidate_manifest.json`, at
4,984,186 bytes (4.75 MiB), rounds to 5 and was silently excluded. One of the
two files the mandate named by hand was missing from the first result set. The
sweep was re-run with no `-size` predicate and the ceiling applied offline in
bytes. Recorded here because it is the same failure shape as Observation 385:
a hand-set threshold that quietly disagreed with the instrument's semantics,
caught only because an expected member failed to appear.

## Decision rule

A file is **should-track** when all of the following hold:

1. It is a small, analysis-relevant JSON/GeoJSON artefact — a candidate
   manifest, evaluation, probabilities file, run metadata, or threshold sweep
   — under the 5 MB ceiling; and
2. it is untracked on at least one host; and
3. its **content** is not already recoverable from git at any path; and
4. tracking it is consistent with `.gitignore`'s own stated intent, rather
   than a reversal of a deliberate exclusion.

Criterion 4 is the load-bearing one, and `.gitignore` states the intent
explicitly at lines 63–67:

> Verifier/proposer crop PNGs are large reproducible binaries … NEVER
> git-track them … **the `candidate_manifest.json` siblings are small metadata
> and remain tracked (`.png` only)**.

The project acts on that intent at scale: **253 `candidate_manifest.json` files
are already tracked**, including ones under `archive/` for retracted probes and
superseded experiments. So tracking a candidate manifest is the norm, and an
untracked one is the anomaly requiring explanation — not the reverse.

Criterion 3 rules out files whose bytes are already in git under a different
path. Git deduplicates by blob hash, so adding such a file costs almost nothing
in repository size — but it is not a *tracking gap*, because an external reader
can already recover the content. Ruling 15's concern is recoverability, not
path coverage.

## Results

### Population

| Sweep | amd-tower | sapphire |
| :--- | --: | --: |
| Live `*.json`/`*.geojson` under `outputs/` + `archive/` | 12,673 | 19,647 |
| Tracked (identical set on both hosts) | 12,669 | 12,669 |
| **Untracked** | **4** | **6,978** |

The union across hosts is **6,981** rows: 4 + 6,978 minus the single file
untracked on both (`outputs/test-phase2b/study_manifest.json`).

### Classification

| Class | Files | Bytes | Action |
| :--- | --: | --: | :--- |
| **should-track** | **2** | **7,068,397** | **committed (`git add -f`)** |
| already-preserved (content in git at an archive path) | 6 | 4,641,881 | none |
| regenerable (gitignored with stated rationale) | 6,971 | 1,684,797 | none |
| runtime/ephemeral (gitignored with stated rationale) | 1 | 34 | none |
| test residue (gitignored with stated rationale) | 1 | 863 | none |

Total 6,981 rows, matching the cross-host union above.

The should-track set is **2 files / 6.7 MiB** — an order of magnitude inside
the mandate's stop-and-escalate ceiling of ~50 files or ~50 MB, so the audit
proceeded to commit rather than escalating.

### should-track (committed)

| File | Bytes | Host(s) present | Blocked by |
| :--- | --: | :--- | :--- |
| `outputs/wbf/fh-text-n30/crops/candidate_manifest.json` | 4,984,186 | amd-tower only | `.gitignore:131` `outputs/wbf/*/crops/` |
| `outputs/wbf/fh-text-n5/crops/candidate_manifest.json` | 2,084,211 | amd-tower only | `.gitignore:131` `outputs/wbf/*/crops/` |

**Justification.** These are the by-omission strays ruling 15 phase 1 was
written for. `.gitignore:131` excludes the whole `crops/` directory in order to
exclude its PNG bulk, and sweeps up the small metadata sibling that lines 63–67
say should remain tracked — an over-capture, not a decision. `git log --all`
over the path returns nothing: the blobs have never been in git on any commit
(Observation 383), so no machine could recover them. They exist on exactly one
host, which is why the four `044` verification rows resolved as `MATCH` when
the repair agent happened to run on amd-tower and as `UNRESOLVED` on sapphire.

Verified at source before committing: each file's `$.candidates` list holds
exactly the count the claims quote — **5,862** for `fh-text-n30` and **2,724**
for `fh-text-n5`.

### The four `044` rows become resolvable at the next recompute

Attribution: Observation 382 (a semantics-driven repair surrendered these to
honest `UNRESOLVED`); Observation 383 (they were only ever `MATCH` because the
repair agent ran on the one machine holding the files).

`scripts/recompute_c4_claims.py` resolves a `read` anchor in three ordered
steps: the working tree at the quoted path; failing that, the era commit; and
failing that, a unique suffix match over **tracked** files. On sapphire all
three failed. Committing the manifests fixes the first step on every host that
has pulled, and would independently fix the third. The `arithmetic` rows have
no era fallback at all — they failed with a bare `FileNotFoundError` — and are
fixed by the file simply existing.

| Row | Method | Quoted | Predicted `actual` | Current | Predicted |
| :--- | :--- | --: | --: | :--- | :--- |
| `044#84[0]` | `read` | 5862 | 5862 | UNRESOLVED | **MATCH** |
| `044#84[2]` | `arithmetic` | 0 | 5862 − 5862 = 0 | UNRESOLVED | **MATCH** |
| `044#88[0]` | `read` | 2724 | 2724 | UNRESOLVED | **MATCH** |
| `044#88[2]` | `arithmetic` | 0 | 2724 − 2724 = 0 | UNRESOLVED | **MATCH** |

The `arithmetic` operand `b` is `len($.results)` of
`outputs/wbf/fh-text-{n30,n5}/verified/probabilities.json`, which is tracked
and already resolves to 5,862 and 2,724 respectively (rows `044#84[1]` and
`044#88[1]` are `MATCH` in the current canonical report). Note that era
resolution at `5d91c2a97` will still fail — committing today does not put a
blob in a past commit — so these rows resolve via the working tree, which is
now populated identically on every host.

### already-preserved — the six `pv-diag-256` manifests (no action)

| Live path (sapphire only) | Bytes | Tracked mirror | Blob (identical) |
| :--- | --: | :--- | :--- |
| `outputs/h11/pv-diag-256/crops/text-baseline/candidate_manifest.json` | 942,528 | `archive/outputs-non-production-tile-sizes/crops/text-baseline/` | `294953f0…` |
| `…/text-1of5/candidate_manifest.json` | 1,087,498 | `…/text-1of5/` | `158ffa7b…` |
| `…/text-2of5/candidate_manifest.json` | 811,768 | `…/text-2of5/` | `cd30c84f…` |
| `…/text-3of5/candidate_manifest.json` | 699,438 | `…/text-3of5/` | `092052d6…` |
| `…/text-4of5/candidate_manifest.json` | 605,185 | `…/text-4of5/` | `68af569e…` |
| `…/text-5of5/candidate_manifest.json` | 495,464 | `…/text-5of5/` | `219d2569…` |

All six `git hash-object` values are **identical** to their tracked archive
mirrors, so the bytes are already in git and criterion 3 fails. The archived
copies are the correct referent: `.gitignore:42–43` deliberately excludes the
legacy 256 px crops tree ("superseded by 384 px"), and the archive directory
name `outputs-non-production-tile-sizes` matches. Provenance was confirmed
positively, not just by hash: the mirrored manifest's `source_geojson` field
reads `outputs/h11/pv-diag-256/consensus/text-1of5.geojson`.

**Residual, recorded not remediated.** No registry spec anchors these paths
(0 of 88 census specs mention `pv-diag-256`), so nothing is currently exposed.
Were a future claim to quote the *live* path rather than the archive path, it
would be sapphire-only and would reproduce the Observation 383 hazard. The
recommendation is that any such claim quote the tracked archive path.

### regenerable, runtime, and test residue (no action)

Every remaining file is gitignored under a rule whose rationale comment states
why, verified with `git check-ignore -v`:

| Files | Rule | Stated rationale |
| :--- | :--- | :--- |
| 6,971 under `archive/leaderboard-caches/` | `.gitignore:87` | "preserved for provenance via the 'archive, never delete' policy but still regenerable from source — untracked to keep the repo size small" |
| `outputs/.active_files.json` | `.gitignore:46` | runtime active-file state |
| `outputs/test-phase2b/study_manifest.json` | `.gitignore:153` | "Integration-test working dirs … shouldn't surface as dirty" |

### Supplementary sweeps

- **Tabular artefacts** (`*.csv`, `*.tsv`, `*.yaml`, `*.yml`) under `outputs/`
  and `archive/`: 210 live, 210 tracked, **zero untracked** on both hosts.
- **`results/`**: 4,669 untracked on amd-tower and 88,573 on sapphire —
  **100 % under `results/leaderboard/**/.cache/`**, gitignored at
  `.gitignore:81` as "regenerable from tracked condition-inventory + source
  detections". Zero untracked artefacts outside `.cache/`.
- **`*.jsonl` under `outputs/`**: 5 on amd-tower (38–154 MB each), more on
  sapphire; all are base64-image request payloads under `batch_working/` or
  named `verifier_requests.jsonl`, both gitignored bulk. Out of scope as bulk
  media, per the mandate.

## Findings worth carrying forward

1. **The tracking gap was two files.** The commit-API-outputs policy is being
   followed almost perfectly: 12,669 tracked artefacts against 2 genuine
   strays, both caused by a single over-broad directory rule.
2. **The two hosts are complementary, not ordered.** amd-tower holds the only
   copy of the `044` manifests; sapphire holds the only live copy of the
   `pv-diag-256` manifests. "sapphire has the fullest tree" is true for crop
   bulk and false in general.
3. **Directory-level ignores over-capture.** Both gaps trace to a rule of the
   form `<path>/crops/` written to exclude PNGs. `.gitignore:68–69` already
   expresses the correct narrow form (`**/crops/*.png`). Narrowing
   `.gitignore:131` and `:43` to match would prevent recurrence; not done here,
   because changing ignore rules has repository-wide effects that belong in a
   deliberate change rather than an audit.

## Changelog

### 2026-08-03 — Original publication

Created under ruling 15 phase 1 (Session 125). Swept both hosts at commit
`fabd07a9d`; classified 6,981 untracked-artefact rows; committed 2 should-track
files (`outputs/wbf/fh-text-{n30,n5}/crops/candidate_manifest.json`, 6.7 MiB)
with `git add -f`. Predicts four `044` rows transitioning `UNRESOLVED` →
`MATCH` at the next recompute. Documents an instrument bug in the audit's own
first pass (`find -size -5M` rounding) and the discovery that the six
`pv-diag-256` manifests are byte-identical to already-tracked archive mirrors.
