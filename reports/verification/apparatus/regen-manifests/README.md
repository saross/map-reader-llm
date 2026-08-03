# Regeneration manifests — tracked proxies for untracked trees

> **Last revised**: 2026-08-03 (created; ruling 15 phase 2 pilots).
> See [§ Changelog](#changelog) for revision history.

## What a regeneration manifest is

A **regeneration manifest** is a small, git-tracked JSON file that stands in
for a directory tree that is *not* git-tracked. It records the generator, the
inputs, the parameters, and the expected census of that tree, so that a
quantitative claim about the tree has a referent an external reader can
actually open.

This is the machinery adopted by **phase 3 ruling 15** (Programme
Investigator (PI)-approved 2026-08-03, in
`reports/verification/phase3-rulings-2026-07-31.md` § 15):

> Mechanical verification scope = git-tracked artefacts PLUS tracked proxies:
> a **regeneration manifest** (generator + tracked inputs + params + expected
> count/content-hash) is the tracked, machine-independent referent for a
> regenerable untracked tree.

## The proxy semantics — read this before anchoring a spec

**A census claim anchors to the manifest, not to the tree.** This is the whole
point, and it is a real change in what "verified" means.

Before ruling 15, a spec such as `006-output-dir-standard#32[1]` walked
`outputs/h11/pv-diag-384` with `glob-count` and compared the live file count to
the figure quoted in the document. That walk is a measurement of *the host it
runs on*. Observation 383 (Session 124) showed the consequence: the same spec
returned 48,707 on amd-tower and 127,281 on sapphire, and a sibling spec's
verdict flipped `MATCH` ↔ `MISMATCH` purely by machine. The committed report
recorded whichever number the operator's machine happened to hold, with no
field saying so.

After ruling 15, the spec reads a **recorded** count out of a tracked manifest.
The consequences are worth stating plainly:

1. **The number becomes machine-independent.** Every host, and every external
   reader with a clone, computes the same `actual`. The verdict is a property
   of the repository, not of a laptop.
2. **The number becomes a dated observation rather than a live measurement.**
   The manifest says "this tree held N files on 2026-08-03, measured thus".
   That is a weaker epistemic object than a live count — but a live count of an
   untracked tree was never available to a reader in the first place, so the
   trade is strictly in the reader's favour.
3. **Drift moves from silent to loud.** If the tree changes, the manifest is
   now wrong in a checkable way. Re-measuring a tree against its manifest is a
   deliberate, reviewable act (see [Refreshing a manifest](#refreshing-a-manifest)).
4. **The manifest does not certify that the tree exists anywhere.** It
   certifies what the tree contained when surveyed, and how to rebuild it. A
   reader who wants the bytes needs the bundle (ruling 15 phase 3/5:
   cross-machine sync now, Zenodo deposit at publication).

## Honesty requirements

These are not stylistic. A manifest that overstates its own authority is worse
than no manifest, because it launders a machine-relative number into an
apparently repo-reproducible one.

- **Never assert content hashes you have not tested.** Crop generation *may*
  be byte-deterministic; whether it is depends on the generator, the image
  library, and the compression settings. Test it, or record counts and
  filename-set digests only, and say which you did. Both pilot manifests carry
  a `determinism` block that states the evidence and its limits.
- **Name untracked inputs as untracked.** The source GeoTIFF rasters this
  project crops from are gitignored and cannot be tracked at their size. A
  manifest that lists them under `tracked_inputs` would be false. They belong
  in `untracked_inputs`, bound by checksum, and flagged as the bundle-index
  stratum.
- **Distinguish a recipe expectation from an observation.** If the tracked
  recipes expect more files than the tree holds, record the shortfall rather
  than quietly reporting the observed number as "expected"
  (`h11-pv-diag-384.json` § `known_shortfall` does exactly this, for 4,540
  files).
- **Say which hosts were surveyed, and when.** A single-host figure cannot
  settle a cross-host question — Observation 385's fourth carry-forward.

## Schema (`regen-manifest/1.0`)

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `schema` | yes | `regen-manifest/1.0` |
| `slug` | yes | Filename stem; unique within this directory |
| `tree` | yes | Repo-relative path of the tree being proxied |
| `ruling` | yes | The governance decision authorising the proxy |
| `assembled`, `assembled_at_commit` | yes | Date and commit at which figures were measured |
| `purpose` | yes | Why this tree needs a proxy, with the observation that motivated it |
| `determinism` | yes | `status`, `evidence`, and the limits of that evidence |
| `generator` | yes | Script path, blob hash, last commit, invocation, API-call count |
| `tracked_inputs` | yes | Inputs recoverable from git, with blob hashes |
| `untracked_inputs` | if any | Inputs not in git, bound by `sha256` |
| `parameters` | yes | The generation parameters, or a pointer to where they live |
| `census` | yes | `scope`, `scope_definition`, `total`, `by_extension[]`, `per_host_observed[]` |
| `files` | optional | Per-file `kind`/`name`/`bytes`/`sha256`, for trees small enough to enumerate |
| `anchored_specs` | yes | The registry spec identifiers that read this manifest |
| `tree_kind` | optional | `mixed` when the tree is not wholly regenerable |
| `known_shortfall` | optional | Recipe-versus-reality gap, when one exists |

### How specs read a manifest

Two runner shapes cover both pilots. Neither needed new runner code.

- **Small, enumerable trees** — `json-subset-count` over `$.files`. The count
  is derived from the recorded content, so the manifest cannot claim a total
  that disagrees with its own file list:

  ```json
  { "runner": "json-subset-count",
    "params": { "file": "reports/verification/apparatus/regen-manifests/gs-125m-fp-side-6-crop-review.json",
                "list_path": "$.files",
                "where": [{ "key": "kind", "op": "eq", "value": "crop-png" }] } }
  ```

- **Large trees** — `json-aggregate` summing `$.census.by_extension`. The total
  is the sum of the per-extension breakdown, so a typo in one row shows up in
  the total rather than hiding behind it:

  ```json
  { "runner": "json-aggregate",
    "params": { "file": "reports/verification/apparatus/regen-manifests/h11-pv-diag-384.json",
                "list_path": "$.census.by_extension", "key": "count", "agg": "sum",
                "where": [{ "key": "scope", "op": "eq", "value": "common" }] } }
  ```

Note that a re-anchored spec is no longer a `glob-count`, so
`scripts/recompute_c4_claims.py::_census_scope` stops stamping it with
`machine_scope`. That is correct: the row is no longer a filesystem census and
has no host to be relative to.

## Predicted verdict transitions at the next recompute

Recorded before the fact so the re-anchoring can be scored rather than
rationalised. All three specs were executed against the manifests on
2026-08-03 and returned the `actual` column below; the `value_verbatim` column
was read out of `reports/verification/c4-extraction/`.

| Spec | Quoted in doc | `actual` | Before (host-dependent) | After (all hosts) |
| :--- | :--- | --: | :--- | :--- |
| `006-output-dir-standard#32[1]` | `48,666` | 48,707 | MISMATCH, `abs_error` 41 (amd-tower) / 78,615 (sapphire) | **MISMATCH**, `abs_error` 41 |
| `006-output-dir-standard#34[1]` | `48,666` | 48,707 | as above | **MISMATCH**, `abs_error` 41 |
| `037#37[0]` | `six` | 6 | **MATCH** (amd-tower) / **MISMATCH** (sapphire) | **MATCH** |

Two further consequences follow mechanically:

- All three rows stop carrying `machine_scope`, `census_total` and
  `census_tracked`, because `_census_scope` stamps `glob-count` rows only. The
  stamped-row population drops from 29 to 26, and no stamped row should remain
  `machine-relative` — the two that were (`006#32[1]`, `#34[1]`) have just left
  the census family, and the row Observation 385 showed being mis-stamped
  (`037#37[0]`) has left with them.
- The `glob-count` tranche falls 29 → 26 while `json-subset-count` rises
  35 → 36 and `json-aggregate` 21 → 23. The census spec total is unchanged at
  88, so GATE 3 accounting (`specced + sum(row_count) == recompute_script_rows`)
  is undisturbed.

**The two `006` rows stay MISMATCH, and that is the correct outcome.** The
claims are changelog rows describing a Status refresh dated 2026-05-26, whose
working census was "1,497 of 48,666 files tracked". Today the same tree holds
**1,538 tracked of 48,707** — both figures up by exactly **41**, i.e. the 41
files added to the tree since that date were all tracked ones. This is era
drift in a snapshot entry, not a defect in the spec or the tree, and under
ruling 14 (the snapshot unit is the entry) it should triage as
SNAPSHOT-DIVERGENCE rather than DOC-DEFECT-AT-ERA. What the re-anchoring buys
is that the divergence is now the *same* 41 for every reader, instead of 41 or
78,615 depending on whose laptop ran the harness.

**Opportunity, not taken here.** `#32[0]` and `#34[0]` quote the tracked-file
side of the same span (`1,497`) and are unspecced — the original spec note
records that they "need `git ls-files` and stay unspecced".
`h11-pv-diag-384.json` now records that count (1,538) as a tracked-core digest,
so those two rows could be specced against the manifest. Not done here: adding
specs changes the census tranche total and therefore the GATE 3 accounting
identity, which is a governance change rather than a re-anchoring.

## Refreshing a manifest

A manifest is a dated observation, so it goes stale by design. Refresh it when
the tree is deliberately regenerated, when a shortfall is repaired, or when a
toolchain bump invalidates recorded content hashes. When refreshing:

1. Re-measure on **every** host that holds the tree, not just the convenient one.
2. Update `assembled` and `assembled_at_commit`.
3. Add a changelog entry to this README naming the manifest, the figures that
   moved, and the commit.
4. Re-run the recompute so the anchored specs' verdicts move in the open.

## Current manifests

| Manifest | Tree | Census total | Anchored specs |
| :--- | :--- | --: | :--- |
| `h11-pv-diag-384.json` | `outputs/h11/pv-diag-384` | 48,707 | `006-output-dir-standard#32[1]`, `#34[1]` |
| `gs-125m-fp-side-6-crop-review.json` | `results/gs-125m-fp-side-6-crop-review/crops` | 6 | `037#37[0]` |

## Changelog

### 2026-08-03 — Original publication

Created under ruling 15 phase 2 (Session 125). Two pilot manifests assembled at
commit `fabd07a9d`, both measured on amd-tower locally and on sapphire over
`ssh` on 2026-08-03. Establishes `regen-manifest/1.0`, the proxy semantics
above, and the two runner shapes for anchoring specs. The three previously
machine-scope-flagged specs (`006-output-dir-standard#32[1]`, `#34[1]`,
`037#37[0]`) were re-anchored to these manifests in the same commit.
