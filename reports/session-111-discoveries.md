# Session 111 — discoveries dossier (for review, 2026-06-11 AM)

> **Last revised**: 2026-06-12 (§ 3 cost ratios corrected from the
> token-load audit: 1/8 → 1/17, HIGH ≈ 3× → 8.6× minimal). See
> [§ Changelog](#changelog) for revision history.

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
roughly ~~1/8~~ **1/17 (audited)** the estimated cost. min11 carries the
best MCC on the PV board (0.807). The consensus-era dividend (Obs 141) is
real for consensus-only architectures and obsolete under PV. Cost-recast
frontier: HIGH proposer passes ≈ ~~3×~~ **8.6× (token-load audit,
2026-06-12 — thinking tokens bill at the output rate)** minimal, so the
dollar-axis frontier collapses onto the minimal-thinking rungs — more
strongly than first estimated. Anchors:
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

## 11. Flash 3.5 verdict: it wins in NO role at the minimal operating point

The tranche completed overnight (≈ on budget; 10 clean passes, all three
verifier legs, the single 503-dropped candidate patched via cleanup). The
2×2×2 at best (k, prob_t), n=5 method-matched (F1@20m / tile-MCC):

| | F3 verifier | F3.5 verifier |
|---|---|---|
| **F3 proposer** (n10 / n5) | **0.8835** / 0.8681 | 0.8689 / 0.8547 |
| **F3.5 proposer** (n10 / n5) | 0.8480 / 0.8462 | 0.8362 / 0.8345 |
| bare consensus (n10) | F3 0.6204 | F3.5 0.6196 |

- **Harness self-validation**: the F3×F3 cell reproduces the committed
  min11 exactly (0.8835 at 6of10/pt0.2).
- **As a bare proposer**: dead tie (0.620 vs 0.620) — the "stronger model
  might be a better proposer" angle closes at minimal thinking.
- **As a PV proposer**: −0.036 — the recall-ceiling mechanism (§ 4) again:
  F3.5's union is 1,132 candidates vs F3's 1,939, with **53 % at 10/10
  votes** (union/pass 1.33; the Pro pattern — consistency without
  coverage, and PV needs coverage).
- **As a verifier**: −0.012..−0.015 on both pools — the carry-forward F3
  verifier wins outright at a third of the price.
- ~~Significance tests pending (morning, $0)~~ **RUN (S113,
  `results/flash35-2x2/flash35_permutations.json`)**: the −0.0355
  proposer gap is resolved (p = 0.035 raw, targeted tile-swap); both
  verifier-role gaps are within-noise ties (p = 0.17 / p = 0.10) — the
  verifier verdict rests on the cost meta-rule (3× price for no measured
  gain). Anchors: `results/flash35-2x2/analysis-full.{json,log}`,
  `outputs/flash35-pv-2x2/` (commits `68c4f0e29`, `f04063513`).

## Decisions (status as of 2026-06-11)

1. **RESOLVED — buffers**: 30 m = GS characterisation precision; 50 m =
   shared operational buffer (55-map canonical + any cross-track table);
   difference explained via ~2× student jitter. 55-map leaderboard built
   at 50 m (`results/55map-leaderboard/`, 5 tiers).
2. **RESOLVED — make-up plan**: A (derived min6 0.8681) + B (true min6
   0.8784, 1,586/1,586 verified, ≈$1.11) both executed; stale union
   archived.
3. **RESOLVED — GT epistemics presentation**: report the +3 %/+5 %
   sensitivity band with the measured 2.4–2.7 % central estimate
   (double-miss correlation 1.5–1.7×, Obs 361) — wide band preferred
   because the ratio rests on 4 events.
4. **OPEN — metric-board flags**: P or R < 0.5 floor + min/max < 0.6
   imbalance marker — confirm thresholds (Flash 3.5 cells now available).
5. **OPEN — sign-off** (`manually_verified_at`): verifier-robustness-matrix
   + pass-budget-pareto analyses; Obs 358–361 are staged.
6. **OPEN — Pareto v2** (cost axis, min6/min11 rungs, `cheap6`→`high6`
   rename) + the findings-doc fold-in of the post-S111 results.

## Changelog

### 2026-06-12 — § 3 cost ratios corrected from the token-load audit

**Refresh trigger**: the token-load audit
(`reports/token-load-audit-2026-06-12.md`). § 3's "1/8 the cost" and
"HIGH ≈ 3× minimal" were pre-audit estimates; audited rates make them
1/17 and 8.6× — the minimal-rung conclusion strengthens. The F1 values
and p-values are untouched.

### 2026-06-11 (S113) — Flash 3.5 significance tests run (§ 11)

**Refresh trigger**: Session 113 ran the three pending role permutations
($0, zbook). § 11's "significance tests pending" bullet is struck and
replaced with the results: proposer-role loss resolved (p = 0.035 raw);
verifier-role losses are within-noise ties (p = 0.17 / p = 0.10) decided
by the cost meta-rule. The § 11 verdict is unchanged.

### 2026-06-11 — Flash 3.5 verdict added (§ 11)

**Refresh trigger**: the tranche completed overnight; § 11 records the
2×2×2 outcome (Flash 3.5 wins in no role at minimal thinking; the
all-Flash-3 stack stands). § 8's "in flight" status is superseded by § 11.
Nothing else changed.

### 2026-06-10 — Original publication

End-of-session-111 compilation, written overnight while the Flash 3.5
tranche runs; supersedes nothing.
