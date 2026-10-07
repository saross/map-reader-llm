# W2.7 floors v2: subsampling floors for the 55-map board, validated

Agent report, 2026-10-07. Read-only on the repository; no Application Programming Interface (API)
call; compute on sapphire (`/tmp/floors2/`). Scripts, gates and results are in `floors-v2/` beside
this file. The question: the 55-map proposer floors of W2.7 § 6 rest on one to three disjoint pairs
per rung. How can they be specified more precisely, and can between-pass variation inside x-of-k
consensus serve as a model?

## 1. Method

- **Every subset, the board's own rung:** each of the C(N, K) pass subsets was rebuilt with W2.7's
  `cluster_subset` + `inherit` (verifier fixed) and scored at 50 m on r2 at every (prob_t, k ≤ K)
  the board uses. That is 16,260 cells: A, B and FOURTH at K = 1–5 of 10; ARM1, ARM2 and the image
  pools at K = 1–4 of 5.
- **Finite-population correction (FPC):** with V_sub the variance of F1 over all C(N, K) subsets
  (divisor C(N, K)), the run-to-run standard deviation (SD) is **SD_run = sqrt(V_sub · N/(N − K))**
  and the floor is **1.96 · √2 · SD_run** (95th percentile of |ΔF1| between two independent runs
  under normality). *Assumption:* the passes of one execution are exchangeable. The variance
  estimate is exactly unbiased for an additive statistic (a mean over passes). For consensus F1,
  Hoeffding's inequality (ζ_c / c rises with c) makes it conservative in expectation, more so as K/N
  grows. The brief's sqrt((N − 1)/(N − K)) is this times sqrt((N − 1)/N): 5 % low at N = 10, 11 %
  low at N = 5.
- **An assumption-free cross-check** (K ≤ N/2): for disjoint subsets, E[ΔF1²] = 2 · Var exactly, so
  the mean of ΔF1²/2 over all disjoint pairs is unbiased (126 pairs at K = 5 of 10). On 55-map it
  gives 0.90 of the FPC SD at K = 5 (median; 0.73–1.00). **Uncertainty:** a leave-one-pass-out
  jackknife standard error (SE).
- **Gates, all passed** (`results/gates55.json`, `gates_gs.json`). The clustering and scorer
  restatements equal the committed functions exactly (tile for tile). All six W2.7 § 2 rung counts
  and ten top-rung counts are reproduced, as are **all 460 W2.7 subset cells and 486 coincident
  gold-standard (GS) cells, to the last bit of F1**.

## 2. New proposer-stage floors (verifier fixed)

The floor is shown ± 1.96 · √2 · jackknife SE. "All disjoint pairs" is the uncorrected empirical
95th percentile over every disjoint subset pair. The old value is W2.7 § 6's (one pair at N5, three
at N3). Fitted rows (§ 4) are point [low, high]. Add 0.001 (verifier re-invocation) for the full
within floor. Every (prob_t, k) is in `results/floors55_all.csv`.

| family | rung | point | subsets | new floor | all disjoint pairs 95th (pairs) | old § 6 floor (pairs) |
|---|---|---|---:|---:|---:|---:|
| A | N1 oracle | (0.20, k1) | 10 | 0.0090 ± 0.0016 | 0.0082 (45) | 0.0082 (45) |
| A | N3 carried | (0.15, k3) | 120 | 0.0093 ± 0.0023 | 0.0087 (2100) | 0.0051 (3) |
| A | N3 oracle | (0.20, k2) | 120 | 0.0061 ± 0.0013 | 0.0058 (2100) | 0.0013 (3) |
| A | N5 carried = oracle | (0.15, k4) | 252 | 0.0068 ± 0.0026 | 0.0065 (126) | 0.0027 (1) |
| A | N10 carried | (0.15, k8) | extrap. | 0.0068 [0.0049, 0.0107] | — | — (0.005 used) |
| B | N1 oracle | (0.20, k1) | 10 | 0.0080 ± 0.0012 | 0.0069 (45) | 0.0069 (45) |
| B | N3 carried | (0.15, k3) | 120 | 0.0051 ± 0.0010 | 0.0046 (2100) | 0.0049 (3) |
| B | N5 carried | (0.15, k5) | 252 | 0.0056 ± 0.0013 | 0.0046 (126) | 0.0023 (1) |
| B | N10 carried | (0.15, k10) | extrap. | 0.0056 [0.0037, 0.0083] | — | — (0.005 used) |
| FOURTH | N1 carried | (0.98, k1) | 10 | 0.0069 ± 0.0009 | 0.0060 (45) | 0.0060 (45) |
| FOURTH | N3 carried | (0.98, k3) | 120 | 0.0051 ± 0.0010 | 0.0047 (2100) | 0.0038 (3) |
| FOURTH | N5 carried | (0.98, k5) | 252 | 0.0054 ± 0.0019 | 0.0041 (126) | 0.0020 (1) |
| FOURTH | N10 carried | (0.98, k10) | extrap. | 0.0054 [0.0034, 0.0088] | — | — (0.005 used) |
| ARM1 | N1 carried | (0.10, k1) | 5 | 0.0058 ± 0.0020 | 0.0049 (10) | 0.0049 (10) |
| ARM1 | N3 carried | (0.10, k3) | 10 | 0.0050 ± 0.0034 | — | — |
| ARM1 | N5 carried | (0.10, k5) | fit, K ≤ 4 | 0.0050 [—, 0.0117] | — | — |
| ARM2 | N1 carried | (0.80, k1) | 5 | 0.0030 ± 0.0006 | 0.0023 (10) | 0.0023 (10) |
| ARM2 | N3 carried | (0.80, k3) | 10 | 0.0049 ± 0.0038 | — | — |
| ARM2 | N3 oracle | (0.95, k3) | 10 | 0.0056 ± 0.0036 | — | — |
| ARM2 | N5 carried | (0.80, k5) | fit, K ≤ 4 | 0.0069 [—, 0.0144] | — | — |
| ARM2 | N5 oracle | (0.95, k5) | fit, K ≤ 4 | 0.0072 [—, 0.0143] | — | — |

**The N5 floors were underestimated by 2.4 to 3.9 times** (A 0.0027 → 0.0068; B 0.0023 → 0.0056; B
oracle 0.0014 → 0.0055; FOURTH 0.0020 → 0.0054), and A's N3 floors by 1.8 to 4.7 times. At N1 the
pairs are the same 45, and the normal-theory floor sits 10–16 % above their 95th percentile. **The
floor hardly shrinks with K:** at the board's points SD_run is 0.0017–0.0024 from K = 3 to 5 (from K
= 2 for B and FOURTH). The verifier absorbs most proposer drift; what remains is which borderline
candidates cross the vote threshold. The full within floors are about **0.007 at N5 (old 0.005),
0.006–0.010 at N3 (old 0.007), 0.008–0.010 at N1 (old 0.009) and 0.006–0.008 at N10** (up to 0.012).
The Gemini 3 image pool stays at 0.017–0.021 (N1 and K = 3; `results/floors55_all.csv`).

## 3. Validation on the 30-pass gold-standard pools

Nine 30-pass pools (two 384-px `pv-diag-384`, seven Era-1 `retest-phase3a*`) were used. Each 10-pass
slice was treated as the only 10 passes (every K-subset; 69,120 cells) and compared with the SD
across the disjoint subsets of all 30 passes: W2.7's committed cells, 10 at K = 3 and 6 at K = 5.
The ratio is sqrt(mean est² / mean truth²) pooled over 21 or 6 slices. Floors are set against the
disjoint 30-pass pairs' 95th percentile. All t: `results/gs_validation_summary.csv`.

| K | t | Era-1 ratio: corrected / brief / disjoint-pair | Era-1 floor: predicted / empirical | 384-px ratio | 384-px floor |
|---:|---:|---|---|---|---|
| 3 | 3 | 1.10 / 1.04 / 1.04 | 0.0385 / 0.0324 | 0.91 / 0.86 / 0.85 | 0.0362 / 0.0467 |
| 5 | 3 | 1.31 / 1.25 / 1.15 | 0.0298 / 0.0277 | 1.94 / 1.84 / 1.71 | 0.0276 / 0.0150 |
| 5 | 4 | 1.16 / 1.10 / 1.01 | 0.0322 / 0.0238 | 1.45 / 1.37 / 1.24 | 0.0311 / 0.0215 |
| 5 | 5 | 1.01 / 0.96 / 0.91 | 0.0416 / 0.0403 | 1.05 / 0.99 / 0.94 | 0.0364 / 0.0305 |

**Pooled over K = 3 and 5 and every t, one slice's corrected estimate is 1.08 times the 30-pass
truth on Era-1 and 1.15 times on 384-px: conservative, as predicted.** The disjoint-pair estimator
gives 0.99 and 1.05, and the brief's form 1.03 and 1.09. The overshoot sits at mid thresholds (1.16
to 1.94 at K = 5, t = 2–4); at unanimity the ratio is 0.91–1.10. A single slice is noisy. On Era-1
the per-slice ratio has an interquartile range of 0.94–1.48 and a 10–90 % range of 0.71–1.96,
matching the 55-map jackknife SEs (15–40 % of the floor for 10-pass families, up to 100 % for
five-pass ones).

## 4. K = 10, and K = 5 for the five-pass families

SD_run for K = 1–5, along the path to the board's N10 point (k = round(frac · K); A carried, 8/10,
gives k = 1, 2, 2, 3, 4), was fitted as c · K^−a and as a + b/K and read at K = 10. The point is
max(power, hyperbola, flat), where flat means SD at K = 10 equals SD at K = 5; the 55-map SDs are
flat beyond K = 2. Low is the disjoint-pair power fit. High is the point + 1.96 · jackknife SE of
the refit. The FPC exponents run from −0.13 to −0.30, not −0.5. The N10 SDs are A 0.0024 [0.0018,
0.0039], B 0.0020 [0.0013, 0.0030] and FOURTH 0.0019 [0.0012, 0.0032]. For the five-pass families at
K = 5, the point is max(fit, direct K = 3, direct K = 4; the latter has five subsets and FPC 5):
ARM1 0.0018, ARM2 0.0025–0.0026. These are the weakest numbers here; FOURTH at K = 5, 0.0019,
agrees. A check on Era-1 GS, where three disjoint 10-pass subsets per pool give the truth (ratio =
extrapolated / empirical, root mean square (RMS) over seven pools; `results/gs_k10_summary.csv`).
Power, hyperbola, flat and disjoint-pair fits give ratios of 0.88, 0.77, 0.78 and 0.76 at t = 10;
1.15, 1.01, 1.02 and 1.00 at t = 9; 0.89, 0.89, 0.91 and 0.75 at t = 8; and 1.30, 1.27, 1.41 and
1.10 at t = 5. The extrapolation is **short at unanimity** and over at majority. On 384-px (two
pools) it overshoots 1.2–2.3 times. The 55-map N10 points sit where Era-1 ran short (unanimity, or
0.7–0.8 of K); the "high" end in § 2, 1.5–1.6 times the point, covers that 12–23 % shortfall with
room.

## 5. Between-pass variation as a model (the Principal Investigator's (PI's) suggestion)

From the full N-pass union (the gated top rung), each candidate's propensity v_i/N was read from its
pass-membership row, and K-pass rungs were simulated with the verifier fixed. There were three
models. (a) **Independent Binomial(K, v_i/N)** votes per candidate (the suggestion). (b) A **pass
bootstrap** (K passes drawn with replacement, keeping each pass's joint pattern). (c) **Union
subsampling** (all K-subsets on the union clusters, no re-clustering, FPC). Models (a) and (b) use
200 draws each, Bessel-corrected for the plug-in propensities. The ratio is to SD_run at the board
points (k ≥ K − 1; `results/propensity55.csv`):

| model | Gemini 3 / 3.7 families, K = 1 / 3 / 5 (median; range) | Gemini 3 image pool, K = 1 / 3 |
|---|---|---|
| (a) independent Binomial | 0.79 / 0.78 / 0.68 (0.48–1.79) | 0.29 / 0.32 |
| (b) pass bootstrap | 1.05 / 3.29 / 1.27 (0.88–13.9) | 1.26 / 4.05 |
| (c) union subsampling | 1.02 / 0.88 / 0.91 (0.66–1.69) | 1.23 / 0.83 |

**The candidate-level propensity model understates the floor by 21–32 % (median) on the text and 3.7
families, and by a factor of three on the Gemini 3 image pool.** A generous, sparse or tile-missing
pass moves many candidates together; independence discards that shared component, which dominates
where passes differ most. The bootstrap keeps it but cannot represent a vote count: a pass drawn
twice votes twice for its own idiosyncratic detections, inflating the SD 1.3–3.3 times. Union
subsampling recovers 0.88–0.91, and re-clustering supplies the rest. No within-run model reaches
candidates that no pass found. **Verdict:** between-pass variation is the right raw material, but
only with the pass as the resampling unit, which is the all-subsets estimator of § 1.

## 6. Re-screen of the near-floor claims (§ 7.2)

Differences are as in § 7.2. Independent cells: 1.96 · sqrt(SD_x² + SD_y²) + 0.001. Cross adds
0.004–0.007 (verifier vintage, § 6a), with the within part [in brackets]. Nested first-N rungs: 1.96
· ρ · sqrt(SD_s² + SD_b²) + 0.001, with ρ = 0.87 (0.73–1.07, measured on nested 2-in-4 and 3-in-5
subsets). Nested threshold contrasts: 1.96 times the contrast's own subsampled SD, + 0.001. "Upper"
uses the SD upper bounds and ρ = 1. TH7, T03, TM and UPL take proxies, the larger of A and B at the
same point (`results/rescreen.csv`, `cell_sds.csv`).

| claim | Δ | runs | old floor → verdict | new floor: point (upper) | new verdict |
|---|---:|---|---|---|---|
| R7.2-13a B > A, N10 carried | −0.0106 | same day | 0.005 → stands | 0.0072 (0.0106) | **stands narrowly** (1.5× point; equals the upper bound) |
| R7.2-13b B > A, N10 oracle | −0.0141 | same day | 0.005 → stands | 0.0072 (0.0104) | stands |
| R7.2-13c B > A, N5 carried | −0.0120 | same day | 0.005 → stands | 0.0072 (0.0111) | stands |
| R7.2-16a N5 ≈ N10 carried (A; B +0.0006) | −0.0009 | nested | 0.005 → tie | 0.0069 (0.0123) | tie, unchanged |
| R7.2-16b oracle residues A / B | +0.0036 / +0.0043 | nested | 0.005 → inside | 0.0069 / 0.0058 | inside, unchanged |
| R7.2-30 B-N5-carried > T03-oracle | +0.0104 | cross, about 4 months | 0.011–0.013 → inside | 0.0106–0.0136 [0.0066] | inside, unchanged |
| R7.2-32a B N5 vs N10 carried | +0.0006 | nested | 0.005 → tie | 0.0059 (0.0092) | tie, unchanged |
| R7.3-04 ARM1 vs B, N5 | +0.0048 | cross, 3–6 days | 0.011–0.013 → tie | 0.0103–0.0133 [0.0063] | tie, unchanged |
| R7.3-06b ARM2-N5 vs FOURTH-N10 | +0.0099 | cross, 3–6 days | 0.011–0.013 → unresolved | 0.0112–0.0142 [0.0072] | unresolved, unchanged (clears the within part 1.4×) |
| R7.3-07 ARM2 tax, oracle − carried | +0.0043 | nested threshold | 0.005 → "noise-sized" | **0.0020 (0.0033)** | **changes: a small, resolved tax** |
| R7.3-18a ARM2 N3 vs N5 oracle | −0.0023 | nested | 0.007 → tie | 0.0066 (0.0145) | tie, unchanged |
| R7.3-18b ARM1 N3 vs N5 carried | +0.0076 | nested | 0.007 → at the floor | 0.0053 (0.0127) | narrow (1.4× point, inside upper): substance unchanged |
| R7.3-19 ARM2-N1-oracle > B-N5 | +0.0107 | cross, 3–6 days | 0.011–0.013 → inside | 0.0095–0.0125 [0.0055] | at the floor, unchanged (clears the within part 1.9×) |
| R6-12a UPL > TM-k3 | +0.0172 | mixed | 0.011–0.013 → clears, confounded | 0.0117–0.0147 (0.0177) | clears the range, inside upper; confound stands |
| R6-12b UPL < TH7-k3 | −0.0106 | mixed | 0.011–0.013 → inside | 0.0117–0.0147 [0.0077] | inside, unchanged |
| R7.1-09a T03 k3 > k4 | +0.0092 | nested threshold, mixed verifier dates | not applied → reword | 0.0069 (0.0111), with a 0.0015 date term | **narrow pass** (1.3×); keep the date caveat |

**What changes.** (1) **R7.3-07:** the old screen held a nested threshold contrast to an
independent-run floor. The tax's own replicate SD is 0.0005 (ARM2 K = 3; 0.0003 at K = 4), so the
0.004 tax is small but resolved. (2) **R7.2-13a** (P6, carried) clears its point floor by only 1.5×
and equals its upper bound; 13b and 13c (1.7–2.0×) carry "B beats A" better. (3) **R7.1-09a** gains
a measured proxy proposer floor (0.0043) and passes narrowly with the date term; a same-date
re-verification (about US$10) still settles it. Every other claim keeps its verdict, on thinner
margins. **The three 3–6-day CROSS claims hinge on the verifier-drift term.** § 6a's own five-day
control (June 6 against June 11) flipped decisions at the same-week rate (2.4–2.5 %). If that
control applies to a 3–6-day gap, R7.3-06b and R7.3-19 clear their within floors (1.4× and 1.9×) and
R7.3-04 stays a tie; that is the PI's call. UPL's cross-execution pair (0.003–0.006 at k3–k5) lies
inside or at the new N5 proposer floors at the same k (0.004–0.009), so no proposer-side
cross-execution shift is resolved on this corpus.

## 7. Limits

- Exchangeable passes are assumed; drift inside a run would break this. Greedy clustering depends on
  pass order, so the statistic is only nearly symmetric. Per-family precision is about ±15–40 %; the
  95th percentile assumes normal ΔF1 (on GS, within ±30 % of the empirical value but for one
  two-pool cell).
- N10 is extrapolated (−23 % to +30 % on Era-1 GS), and the 55-map shape is flatter than GS's. The
  five-pass N5 floors rest on K ≤ 4. The TH7, T03, TM and UPL proxies are Gemini 3 MIN families, and
  ρ is transferred between nesting depths.
- These are proposer-stage floors; the verifier terms are additive and come from single
  measurements. Incidental: with an int buffer, the committed matcher's `np.full(…, buffer * 1000)`
  truncates distances to whole metres before the Hungarian step. The gated scorer reproduces it; on
  18 cells, totals and per-tile splits equal the float version.

## 8. Wall-clock

Sapphire, 20–22 workers. 55-map: 367 s (gates 52 s; 16,260 subset cells 176 s; 57,576 simulated
cells 139 s). GS: 123 s (69,120 cells). Analysis and tables: under 15 s. Total compute was about 9
minutes against an expected hour, because the gated restatements (KD-tree shortlist; vectorised
Geometry Engine Open Source (GEOS) matching) run tens of times faster per cell than the W2.7 path.
