# Evaluator-diversity management in crowdsourcing — exploratory scoping note

> Agent-produced EXPLORATORY scoping pass (Sonnet subagent, Session
> 145, 2026-09-01), commissioned by the PI while calibrating the
> model-consistency observation ("you might have an agent do a
> quick, exploratory check"). **Not a systematic review; claims
> marked [search-snippet only] are UNVERIFIED and must not be cited
> without tracing the original.** A full lit-scout with per-claim
> verification stays in reserve (PI: "keep that in our back
> pocket").

## 1. Standard mechanisms for annotator/volunteer quality variance

The field has a well-established toolkit — volunteer variance is
managed, not merely suffered:

- **Repeated/redundant labelling + majority vote.** Canonical start:
  Sheng, Provost & Ipeirotis, "Get Another Label?", KDD 2008
  (extended in *Data Mining and Knowledge Discovery*, 2014) —
  repeated labelling beats single labelling once labels are noisy;
  selective (uncertainty-targeted) re-labelling is the efficient
  variant [search-snippet only].
- **Reliability-weighted aggregation.** Dawid & Skene (1979), EM
  over per-annotator confusion matrices [search-snippet only, but
  textbook-canonical]. Modern descendant: CROWDLAB (cleanlab,
  arXiv:2210.06812), claims to beat majority vote and Dawid-Skene
  [checked at source for the qualitative claim; percentages not on
  the fetched page].
- **Gold-standard seeding / dynamic filtering.** CrowdDQS-style
  adaptive gold questions with real-time worker-accuracy estimates
  [search-snippet only].
- **Platforms at scale**: Geo-Wiki land-cover validation — See et
  al. 2013, *PLoS ONE* 8(7):e69958, DOI 10.1371/journal.pone.0069958
  [checked at source]; Zooniverse/Galaxy Zoo vote-fraction
  aggregation with consistency-based user weighting (Willett et al.
  2013) [mechanism checked at source; the ~38–40
  classifications/object figure snippet-only]; OpenStreetMap QA
  tradition (no built-in voting) [snippet-only].

## 2. Reported improvement magnitudes

Domain-specific, no universal constant:

- Geo-Wiki: expert 69.2–84.6 % vs non-expert 61.9–65.9 % across
  three control sets [checked at source, PMC3729953].
- Snippet-level synthesis: one aggregation model +10–30 % over
  majority vote; another case 85.8 % (majority) → 97.9 %
  (reliability-weighted) [search-snippet only — provenance unclear,
  weakest-sourced numbers here; do NOT cite untraced].
- Sheng et al. 2008: "considerable advantage" once labelling is
  imperfect; magnitude regime-dependent [search-snippet only].

## 3. Geospatial digitisation specifically

- **Polygon Consensus** — Budig, van Dijk, Feitsch & Giraldo
  Arteaga, ACM SIGSPATIAL 2016 (NYPL fire-insurance atlas building
  footprints): consensus polygons reportedly correct for 96 % of
  footprints vs 85 % for individual crowd polygons [venue/authors
  partially confirmed; the 96 %/85 % figures are search-snippet only
  — three direct-fetch attempts blocked; verify before use]. NOTE:
  this work is already cited in Sobotkova et al. 2023's reference
  list (see the 2023-paper synopsis), so the Zotero/TRAP collection
  may already hold it.
- Sobotkova et al. 2023 itself [checked at source]: the error rate
  is reported as an outcome with **no redundancy mechanism** — the
  full-paper synopsis (`claude-sobotkova-2023-synopsis.md`) confirms
  redundancy appears only as a future-work recommendation.

## 4. Human redundancy vs model ensemble — the thin patch

Conceptual treatments exist ("inner crowd" vs "outer crowd" likened
to ML ensembling, gains requiring diverse/weakly-correlated errors)
[search-snippet only], plus adjacent cautionary work on consensus
failure modes [snippet-only]. **No empirical head-to-head of
human-crowd redundancy against model-ensemble consensus as the same
class of variance-control mechanism surfaced within budget.** If a
deeper pass confirms the gap, the comparison is a potential novelty
pocket for the paper's discussion — flagged, not claimed.

## Status

Exploratory only. Consumers: Obs (model consistency vs novice
variance, S145) cites this note as banked pointers; any promotion
into paper text requires the full lit-scout + verifier pipeline
first.
