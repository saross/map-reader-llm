# Session 111 — discoveries dossier (for review, 2026-06-11 AM)

> **Last revised**: 2026-06-10 (original publication, end of Session 111
> overnight block). See [§ Changelog](#changelog) for revision history.

Compiled at Shawn's request before the morning review: every substantive
finding of the session, with anchors. Findings 1–5 belong to the
verifier-robustness/Pareto thread (citable home:
`results/verifier-robustness/verifier-robustness-findings.md` §§ 8–12, to be
extended with §§ on findings 3–5); findings 6–7 open the working-precision
thread (`results/working-precision/`).

## 1. The opmax lift is noise — 0.890 stands (S111 priority question)

16of30 + N=5 verifier (0.8951) vs 16of30 + n=1 verifier (0.8902): paired
tile-swap permutation **p = 0.363** (diff +0.0049 ≈ the null SD). Per the
cost rule, the n=1 carry-forward verifier stays the practical ceiling.
Anchor: `results/verifier-robustness/opmax_vs_headline_permutation.json`.

## 2. The pass-budget Pareto ladder is ONE statistical tier (6 → 35 passes)

Round-robin over five rungs (cheap6 0.8641 / min10 0.8739 / nof10 0.8769 /
headline31 0.8902 / opmax35 0.8951): 0/10 pairs significant after BH-FDR.
The largest span (raw p = 0.012, BH 0.096) is suggestive, unprovable on the
487-tile instrument (Obs 347 plateau limit). Anchor:
`results/verifier-robustness/pareto/pareto_leaderboard.{json,png}`.

## 3. The diversity dividend does NOT survive the verifier (min ≈ high)

At equal pass count, MINIMAL-thinking proposers reach statistical parity
with HIGH (min6 0.8708 vs high6 0.8641, p = 0.66; min11 0.8835 vs high11
0.8769, p = 0.59) — and **min11 vs the 31-pass headline is p = 0.56** at
roughly 1/8 the estimated cost. min11 carries the best MCC on the PV board
(0.807). The consensus-era dividend (Obs 141) is real for consensus-only
architectures and obsolete under PV. Cost-recast frontier: HIGH proposer
passes ≈ 3× minimal, so the dollar-axis frontier collapses onto the
minimal-thinking rungs. Anchors:
`results/verifier-robustness/min_thinking_pv.log`,
`min_vs_high_permutations.json`. **Proposed Obs (morning): the
strongest new-finding candidate of the session.**

## 4. Mechanism: the verifier shifts the binding constraint to pool recall

Recall ceilings (union GT coverage): Flash-MIN-T0.7 saturates at **0.920 in
5 passes** (the 10-pass lineage is also exactly 0.9195 — passes 6–10 added
zero new mounds, only vote evidence); Flash-HIGH adds volume (union/pass
2.46 vs 1.44) but only +0.023 ceiling; **Pro 3.1 samples near-
deterministically at T=0.7 (union/pass 1.15)**, so its 0.832 ceiling caps
its PV F1 — temperature cannot supply diversity for Pro. Temperature-
sampled diversity is the cheapest way to raise reachable recall for Flash;
thinking-level diversity is mostly surplus volume. Zero-diversity anchor
(1 × minimal T=0.0 pass + n=1 verifier): **0.8142** (+0.057 from
temperature diversity; ~60 % of the gain is the ceiling lift) — with the
board's highest tile-MCC, 0.833. Anchors:
`results/verifier-robustness/pool_recall_ceilings.{json,log}`,
`zero_diversity_anchor.json`.

## 5. The verify-once-at-n=10 shortcut is valid only method-matched

Deriving n=5 post-hoc from a verified 10-pass union (contributing_passes,
first-5 rule) reproduces a true 5-pass merge's geometry to 0.07 m but runs
**systematically +0.005..+0.011 F1 high** (cluster topology + crop
centring). All Flash 3.5 n=5 comparisons are therefore method-matched
(both models derived the same way). Anchor:
`results/verifier-robustness/first5of10-validation/validation.json`.

## 6. GS working precision: text plateaus at 30 m, image at 75 m

All 259 GS conditions with full buffer curves: plateau onset (every later
step ≤ 0.005) — PV 30 m < consensus 35 < single-pass 40; **text 30 m vs
image 75 m** (image localisation ~2.5× looser — modality is the dominant
factor). For the production text-PV family, F1@30 = F1@50 exactly (flat
plateau); e.g. opmax 0.916/P 0.929 at 30 m ≈ 6 px. Groups are
observational (confounded), caveated in the doc. Anchor:
`results/working-precision/gs-plateau-characterisation.{json,md}`.

## 7. 55-map working buffer: cap at 50 m, on three converging lines

(1) The CSR chance-matching null is negligible at every canonical buffer
(null F1 ≤ 0.015 at 150 m) — the signal never fades into *random* noise;
(2) observed marginal gains die at 50 m (zero/negative beyond, while
chance creep continues); (3) the **attribution-ambiguity bound bites
first**: GT nearest-neighbour p10 = 65 m, so 21 % of mounds are at
cross-match risk at R = 50 and 42 % at 125. Caveat: 415/773 phantoms gate
at exactly 50 m (the review SOP anchor), so the 45→50 F1 jump is partly GT
composition. 50 m ≈ 2× student jitter; median mound spacing 375 m.
Tighter than, and consistent with, the 100–125 m preliminary. Anchor:
`results/working-precision/55maps-csr-noise-floor.{json,log}`.

## 8. Flash 3.5 tranche (approved ~$34, in flight overnight)

`gemini-3.5-flash` is live as a **stable** model name; smoke passed
(10 tiles, 0 failures, minimal thinking accepted, instruction-payload hash
identical to both comparator lineages, three-source model verification);
`/audit-config` READY (0 blockers). Per-call tokens (~1.2 K) run below
estimate → expect under-budget. Design upgraded to **2×2×2** (proposer
model × verifier model × n ∈ {5,10}) by the verify-once shortcut. Stage P
runs an aggressive failed-tile policy (resume ×4 per pass, 485/487 floor)
after pass 1 lost one tile to a transient JSON-parse failure and `set -e`
halted the first launch. Runbook: `scripts/run_flash35_tranche1.sh`; log:
`outputs/flash35-pv-2x2/tranche-full.log` (zbook).

## 9. Data-integrity catches (all repaired + committed)

- **S110 opmax overwrote the Stage-2 T0.3 grid/summary** (filename keyed
  only on temperature+thinking): restored from git, opmax re-homed to
  `-16of30` names, `--out-suffix` guard added (commit `7d85b00ef`).
- **`text-1of5` is a partial-coverage stale union** (974 cands, 230/471
  tiles; built mid-study before pass resumes): excluded with diagnosis;
  make-up plan awaiting approval
  (`planning/min6-makeup-run-plan-2026-06-10.md`, ≈ $1.15 option B).
- **`evaluate_detections.py` DEFAULT_BUFFERS = [20]**: the 14
  registration evaluations initially carried one buffer; re-run at the
  canonical 14 and manifests regenerated.
- **Untracked S110 logs on zbook** (incl. the continuity-cited
  `opmax.log`) committed; smoke API outputs committed per policy.

## 10. Manifest registration (Shawn-approved full decomposition)

Run #29 `verifier-robustness`: 8 conditions + 6 pv-diag-384 additions + 2
analyses (`verifier-robustness-matrix`, `pass-budget-pareto`). Manifest:
**29 runs / 295 conditions / 1114 passes / 12 analyses, ALL VALID;
drift-check 16 pass / 13 partial / 0 fail** (partials unchanged,
documented family). Every condition gated on eval-F1 reproduction + the
feature-count cross-check. No new champion (recorded in
`headline_rationale`).

## Decisions awaiting Shawn (morning)

1. **GS working precision**: 30 m (plateau-onset criterion, text-PV) vs
   50 m (single cross-track value; identical numbers for text-PV) — then
   the working-precision leaderboard (F1/P/R/CIs + MCC) gets built at it.
2. **55-map working buffer 50 m** — confirm (the three-line case above).
3. **Make-up run option B** (≈ $1.15) — approve/decline
   (`planning/min6-makeup-run-plan-2026-06-10.md`).
4. **Metric-board flags**: P or R < 0.5 floor + min/max < 0.6 imbalance
   marker — confirm thresholds (boards deferred until Flash 3.5 can join).
5. **Sign-off** (`manually_verified_at`): the two new analyses;
   plus proposed new Obs for findings 3–4 and 6–7.
6. **Pareto v2** (cost axis, min6/min11 rungs, `cheap6`→`high6` rename) —
   queued, will fold findings 3–5 into the findings doc alongside it.

## Changelog

### 2026-06-10 — Original publication

End-of-session-111 compilation, written overnight while the Flash 3.5
tranche runs; supersedes nothing.
