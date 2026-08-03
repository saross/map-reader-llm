# Wave-6 triage — pre-registered draft stories (2026-08-03, Session 126)

**Discipline**: ruling 11 — author-side hypotheses committed BEFORE the
blind passes. Blind adjudicators do not read this file.

**Scope**: 209 wave-6 MISMATCH rows + 4 pre-wave rows the filtered-
subset locator extension newly exposed (051#0[0]; 020#49[0];
004#40[1]/#42[1]) + 3 APPROX rows whose markers cannot absorb their
errors (061#27[0] ~150 vs 702; 071#38[5] ~95 vs 95,168,363;
078#17[3] ~14 vs 16). The wave-6 Obs 382 join ran CLEAN: 53
status/actual transitions + 9 reason-string drifts, every one
attributed to this session's named fixes (1e4a13ff7, 963ab91dc,
6af00ffad) — the 17 MISMATCH→MATCH and 7 MISMATCH→SKIPPED sets equal
the wave-5 predictions exactly; 24 UNRESOLVED→MATCH are multi-match
filter shapes the locator extension resolved.

## Families and predictions

**α — pre-audit cost/token figures (069#12/13/14, 071#34–41,
072#13/15/18/25/53/54/55; APPROX 071#38[5]).** The cross-track and
production reports quote the PRE-AUDIT cost manifests ($364.70 image /
$126.81 text-HIGH / $60.79 text-MIN, ratios 2.9/6.0, token totals in
millions, cache-hit 91 %); anchors return the audited/regenerated
figures ($200.83 / $207.34 / $30.44). Predicted: SNAPSHOT-DIVERGENCE
where the document predates the 2026-06-12 token-load audit
(era-faithful against the superseded manifests archived at
`archive/superseded-cost-manifests-2026-06-12/`), with a scale/unit
sub-shape (millions and percent quotes vs raw-scalar anchors) that is
extraction-side unit-bridging, not value defects. One caution: the
text-HIGH pair looks INVERTED ($126.81 quoted vs $207.34 audited —
the audit RAISED it; 072#54's $69.60 vs $207.34 is a different era
again) — per-row era resolution required; some rows may be
DOC-DEFECT-AT-ERA if the manifests never held the quoted figure.
These rows are also the natural first clients of the queued
cost/token runner (tranche 2): flex pricing derives from tokens ×
rates × 0.5, never `cost_estimate.total_cost_usd` (Obs 380).

**β — post-recovery F1/count third-decimal drift (070 CI/F1 rows,
072#9/19/21/30, 075 F1/TP/detections rows, 077#12/13, 078 all,
079-corrected-f1 rows).** Quoted 0.832/0.8333/4,110 TP/4,665
detections vs actual 0.833215/4,124/4,680 — the recovery campaign's
final re-scores nudged the curve upward AFTER these documents were
written. Predicted: SNAPSHOT-DIVERGENCE for rows quoting pre-final
values; the '0.8333 post-recovery' quotes may reflect an intermediate
recovery state (era resolution decides divergence vs defect).
075#6[0]/#66[0] (5,216 vs 4,746) is predicted a DIFFERENT mechanism —
the doc's extended-GT count vs an anchor returning the student-only
layer (possible extraction wrong-layer binding).

**γ — GT-count drift (067#16, 069#32, 073#2, 074#39, 077#19,
079-corrected-f1#22).** 4,744 → 4,745 → 4,746 across eras as curator
adjudications landed. Predicted: SNAPSHOT-DIVERGENCE, each doc
faithful to its era's layer.

**δ — verification-programme self-counts (061, 062, 063,
064-phase2-gate-package; APPROX 061#27[0]; pre-wave 051#0[0],
020#49[0], 004#40[1]/#42[1]).** The corpus the programme audits grew
under it: passes-manifest fields 20→23, analyses 18→21, generated
stratum 2,136→2,192, hand-written 148→142 (splits/moves), field
checks 28,682→32,123, commitment ledger states moved (211→208 open),
n1-pro-rerun-384 runs 8→12, unsigned analyses 7→4. Predicted:
SNAPSHOT-DIVERGENCE throughout — this family QUANTIFIES the Phase-0
scope-growth flag already carried for GATE 3; no document defect
expected. 064-phase2-gate-package#18/23/24 (0→1, 326→327, 486→487)
are specifically the 0.7.1 sorted-glob/completed-union fix
(75aa47125) — divergence with a named instrument cause. The
commitment-estimate rows (~150–250 vs 702) are ESTIMATES in prose —
predicted ledger-only (the C1 census superseded them; materiality
nil).

**ε — H9-A pool wrong-anchor repeat (064-phase2-rulings#7[1], 4,954
vs 1,032).** Same mechanism as wave-5's 056#41[0]: single-arm file
bound where the five-arm run-1 sum is meant. Predicted:
EXTRACTION-DEFECT; repair with the same five-operand sum.

**ζ — verifier-silent-drop counters (066 rows, 1147 vs 0).**
Predicted: SNAPSHOT-DIVERGENCE — the 2026-05-03 investigation
recorded live failure counters; the recovery re-ran the verifier and
the current meta's counters are clean. Era resolution should find
1,147 at the document's date.

**η — attractor-pull-v2 bias-corrected stats (067#19–49, 067#61).**
Third/fourth-decimal drifts in bias-corrected rates/lifts/p-values.
Predicted: SNAPSHOT-DIVERGENCE via regenerated artefacts (GT drift
propagating through the bias correction), NOT doc defects; if the
sibling JSON was regenerated in place, era resolution decides.

**θ — bootstrap-N (070#1/8, 072#61: 1,000 quoted vs 10,000).**
Two readings: the docs under-report the iterations actually run
(DOC-DEFECT-AT-ERA), or the artefact was re-run at 10,000 after the
docs (divergence). No prediction preferred; era resolution decides.
BCa caveat noted: iteration COUNT is not a CI value; the caveat does
not shield this row.

**ι — small human-review count drift (071#43[2]/#45[2]/#46,
073#50/57/61/62, 074#18/20/21/23, 078#17[3] APPROX).** One-off count
and third-decimal stat drifts. Predicted: mostly divergence via
re-scores; per-row check.

## Non-mismatch dispositions (proposed)

- UNRESOLVED 318 and SKIPPED 876: same structural classes as wave 5;
  runner tranches 2–3 (queue item (c)) own the recompute-script
  SKIPPED mass; NAMED lines carry to GATE 3.
