# Session 121 — Principal Investigator (PI) morning rulings (2026-07-30)

**Status**: RECORD. Verbatim PI rulings collected interactively on
2026-07-30 (Session 121, Claude Fable 5), governing the Phase 2 landing
sequence: the GATE 1 erratum queue (drafts at
`reports/verification/drafts/errata-drafts-2026-07-29.md`), the three
new erratum candidates born from the C3 provenance triage
(`reports/verification/c3-rederivation/c3-triage-tiles.json`), and the
family-level Benjamini–Hochberg false discovery rate (BH-FDR)
registration (`reports/verification/drafts/family-fdr-registration-draft.md`
§ 11). Rulings via structured question (options quoted as selected) or
free text (quoted verbatim).

**Authority**: `planning/audit-charter.md` § 7 (gates belong to the PI)
and § 10 (PI review decisions). This record is referenced by the GATE 2
package.

---

## 1. Erratum-draft decision points (beacon items 1a–1e)

### (a) `verifier_thinking_level=medium` — SPLIT

Context presented: provenance traced in-session — the 13 census sites
carry configuration-side (`run.meta.json` `configuration.thinking_level`)
AND API-side corroboration (non-zero `total_thoughts_tokens`: 1,933 on
the Flash-medium union segment, 4,013 on a Pro-medium meta), plus
behavioural evidence (Obs 187: minimal-vs-medium verifier ΔF1 = +0.010,
p = 0.001). The lodged registration enumerates the parameter's values as
"(`minimal`, `low`, `high`)" (`osf/preregistration.md:2110`) — `medium`
is absent from the registration's vocabulary. Census evidence splits the
13 sites: 7 Pro-verifier cells within E40's *rationale* (the
`gemini-3.1-pro-preview` endpoint cannot run MINIMAL — Obs 185), 6
Flash-verifier cells that nothing forced (deliberate Session 57
exploration, Obs 187).

**PI ruling (verbatim)**: "ok, that makes sense. For Pro we had no
choice, that's an existing erratum. For Flash it was an unlicensed
exploratory run that needs a new erratum. Yes, keep the two separate,
each with their own erratum."

**Implementation**: E62 narrows to the three unlicensed families plus
the verifier-parameter levels those families themselves carry. A NEW
erratum (E69) covers the deliberate-but-unlicensed Flash-verifier
thinking exploration in `pv-diag-384` (6 medium sites + the 1
`pv-diag-384` Flash-at-HIGH site, folded in as the same family — noted
to PI, no objection). E40 gains a dated clarification block recording
this ruling — its endpoint-constraint rationale extends to the 7
Pro-as-verifier medium sites. Census re-verdicts at the ledger stage.

### (b) `pv-diag-256` null `purpose` — POPULATE

**PI ruling**: "Populate (Recommended)" — write the tile-size-diagnostic
purpose at the generator source so it survives manifest regeneration;
E62 cites the manifest directly.

### (c) E64(iii) subtype materiality figure — COMPUTE TRUE FIGURE NOW

Context presented: the draft's 17.2% reproduced exactly in-session
(phase3c track-1 H9-A run-1 pool, 4,954 detections: 4,102/501/316/35);
the gate package's ~21% is a defence-pass figure with **no recorded pool
or denominator** (unanchored, cannot be re-verified). Both are loose
upper bounds; the true materiality quantity is the fraction of spatial
(20 m) clusters whose members disagree on subtype, and the
vote-threshold consequence of splitting them.

**PI ruling**: "Compute true figure now" — run the cluster-level
heterogeneity analysis on sapphire before E64 lands.

### (d) E36 misreport propagation — APPROVED AS PROPOSED

**PI ruling**: "Approve (Recommended)" — in-place edit + changelog for
`reports/experimental-progression.md:83` and
`reports/gs-tile-pool-mapping-2026-05-28.md:45` per the document
revision policy; an append-only Obs rider (never an edit) for
`docs/notes/working-notes.md:3397`.

### (e) E68 — APPROVED

**PI ruling**: "Approve E68 (Recommended)" — the CMT-0109 rider retiring
the "academic baseline" designation (gate package § 3 item 6,
finding 10).

## 2. Triage-born erratum candidates (beacon item 2)

### 2.1 `--patch-tiles` recovery campaign — FILE ERRATUM

**PI ruling**: "File erratum (Recommended)". Discloses the March 2026
out-of-band tile-recovery mechanism once at the register level; the 127
vindicated C3 triage rows cite it. In-session recount from the triage
artefact: 127 passes / 350 patched tiles (beacon said 126/349; to be
reconciled at drafting).

### 2.2 Tile-count semantics + generator defects — ERRATUM + FIXES + GATED RERUN

**PI ruling (verbatim)**: "Erratum + fixes + rerun to sweep up failed
tiles (through usual API-gate process including dry-run, approval,
etc.)"

**Implementation**: one erratum covering the dispatched-vs-completed
column semantics (`generate_post_run_report.py:368` vs `:398`), the
GAP-8 request-count placeholder, and the live-condition impact (two live
t0.0 consensus conditions carrying 19–34 dead tiles as artificial false
negatives); generator fixed to a single consistent semantics; manifests
regenerated; AND a recovery rerun registered under rule 10
(`status: planned` before any API call), dry-run + `/audit-config` +
per-batch PI cost approval before spend.

### 2.3 E55 unfulfilled run.log-provenance promise — CORRECTION BLOCK + FIX

Context presented: verified in-session — no manifest row lists `run.log`
in `provenance.source_files`; the generator mentions it only in a
comment (`generate_post_run_report.py:307`). Temperature values
themselves are correct via the additive `temperature_effective` field.

**PI ruling**: "Correction block + fix (Recommended)".

### 2.4 Standing-policy items (presented; no objection — proceeding)

- Obs rider for `docs/notes/working-notes.md:17339` ("isolated to two
  cells" — counterexample: board cell
  `pv-diag-384::baseline-flash-image-minimal-t-0-0` at 483/487).
- Draft 5 lands as three separate entries (E65/E66/E67) per house style.

## 3. Family-FDR registration (§ 11 open questions)

### 3.1 H1 primary — OPTION (iv): RUN CMT-0106 NOW

Context presented: the four registered H1 contrasts with re-verified
p-values (0.006 / 0.94 / 0.38 / never-executed); the PI's recalled "main
contrast — image vs text-only" identified as registered contrast 4
(CMT-0106, the pooled modality contrast), never executed and
defectively specified (no metric, no pooling rule); the GATE 1
run-it-now policy covers it; a pre-registered pooling reconstruction
restores genuine outcome blindness to the only outcome-material
selection.

**PI ruling**: "(iv) Run CMT-0106 now" — pooling rule registered before
computing; sapphire, US$0.

### 3.2 H5 — ACCEPT SUBSTITUTE

**PI ruling**: "Accept substitute (Recommended)" — terse vs verbose,
image track, precision (`precision_p` = 0.756), with the divergence note
that the registered headline (Minimal vs Terse) never executed at the
current era.

### 3.3 H8 — OPTION (iii): WITHIN-H8 BH-ADJUSTED MINIMUM

Context presented on PI request (pros/cons of (i) vs (iii)): outcome
identical (H8 null either way); (iii) is the Simes global-null test of
"no H8 contrast has any effect", honours the registered within-H8 FDR
(`preregistration.md:821`), and is immune to the min-p selection
objection; (i) is symmetric but formally an invalid statistic carrying a
permanent caveat.

**PI ruling**: "(iii) Within-H8 BH min (Recommended)" — B1 at
`bh_adjusted_p` = 0.8344, Simes framing.

### 3.4 Bundled confirmations — ALL THREE CONFIRMED

**PI ruling**: "Confirm all three (Recommended)":

1. H7 primary = text track T0.3 vs T1.0, recorded as p ≤ 0.001
   (bootstrap floor).
2. E64 files BEFORE the FDR compute (anchors the two-sided tail
   reading).
3. H2 reported as a FALSIFIED directional prediction — two-stage
   significantly improves F1 (+0.076, p < 1 × 10⁻⁴), clearing the
   registered ≥ 0.05 stopping threshold in the direction the
   registration predicted against.

---

## 4. Consequences for the landing sequence

Order (dependencies respected): rulings record (this file) →
cluster-heterogeneity compute (sapphire; gates E64) → errata wave
E62–E71 + correction blocks (E36/E16/E20/E40/E55) → Obs riders (×2) →
report fixes (×2) → ledger/census updates → generator fixes + tests +
manifest regen → family-FDR registration finalised and committed →
CMT-0106 pooled contrast + BH family computed (sapphire) → recovery
rerun registered and STOPPED at API gate → GATE 2 package.
