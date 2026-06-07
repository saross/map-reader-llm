# 55-map deployment oracle — carry-forward vs oracle-best (Session 104)

> **Last revised**: 2026-06-07 (canonical adjudicated-GT re-score added — §4b; deltas hold, absolutes rise as duplicate phantoms clear). See [§ Changelog](#changelog) for revision history.

**Question.** The 4 GS (gold-standard) maps are the calibration+test instrument; the
55-map student corpus is the out-of-sample deployment. We carried forward a PV
(proposer → consensus → verifier) configuration calibrated on GS and deployed it on
the 55 maps. **How much did committing to the carried-forward operating point cost
versus the oracle-best we could have deployed?** And **was the carry-forward actually
the GS optimum?**

**Headline.** The carry-forward (proposer **text HIGH, T=0.7**; consensus **vote 4-of-5**;
text-adversarial verifier, prob≥0.15) was on the GS-optimal *plateau* but **left
+0.032 corrected-F1 @ 50 m on the table** versus the joint oracle (**text HIGH, T=0.3**;
consensus **3-of-5**) — significant (p<0.001). The gap is a genuine
**calibrate→deploy generalisation gap**: the deployment optimum is one consensus notch
looser and one temperature step lower than the carried configuration.

All deployment numbers are **corrected F1 @ 50 m** (extended GT = manually-reviewed
student GT + reviewer-promoted phantom mounds) under a **fixed-union** reference (both
compared cells scored against the *same* extended GT), via
`paired_permutation_corrected_55maps.py` (10 000 tile-swap permutations, seed 42).
GS numbers are **F1 @ 20 m** against the gold reference (`mounds-reference.geojson`,
Era-2 487 tiles).

---

## 1. Threshold axis — k3 (3-of-5) beats the carried k4 (4-of-5)

Within each deployed text config, the looser **3-of-5** significantly beats the carried
**4-of-5** in corrected F1 @ 50 m (fixed-union, per-config):

| run (config) | k4 = 4-of-5 (carried) | k3 = 3-of-5 (oracle) | ΔF1 (k3−k4) | p |
|---|---|---|---|---|
| text-high **T0.7** | 0.822 | **0.850** | **+0.028** [+0.022, +0.034] | <0.001 |
| text-high **T0.3** | 0.841 | **0.851** | +0.010 | <0.001 |
| **text-min** | 0.795 | **0.822** | +0.027 | <0.001 |

**Mechanism.** k3 trades ~3–5 pp precision for ~6–8 pp recall: relaxing consensus from
4-of-5 to 3-of-5 surfaces **99 / 117 / 61 additional real mounds** (verifier-passed and
human-confirmed) that 4-of-5 missed, and the verifier filters the extra false positives
well enough that recall dominates. This required a **vote=3-shell verifier run** (10 622
candidates, `gemini-3-flash` text-adversarial, real-time *flex*, prob≥0.15, **0 failures**,
≈ $7.4 billed) plus manual review of the new VLM-only candidates (357 genuinely-new
across the three runs + 238 auto-fill confirmations; 145 new real mounds in the
fresh-judgement pass alone).

## 2. GS calibration check — was 4-of-5 really the GS best?

In the **same PV pipeline** on the GS tiles (post-verifier F1 @ 20 m), the curve is
hump-shaped (the verifier inverts the pre-verifier monotone "stricter-is-better" into a
peak), and the point estimate peaks at **4-of-5**:

| GS post-verifier F1@20m | 3-of-5 | **4-of-5 (carried)** | 5-of-5 |
|---|---|---|---|
| HIGH-text T0.7 | 0.847 | **0.861** | 0.836 |
| HIGH-text T0.3 | 0.874 | **0.884** | 0.868 |
| MINIMAL T0.7 | 0.866 | **0.871** | 0.847 |

But the peak is a **plateau**: 4-of-5 vs 3-of-5 is **not significant** (p = 0.12 / 0.11 /
0.43), while 4-of-5 vs 5-of-5 **is** (p = 0.004 / 0.036 / 0.015). **So the carry-forward
(4-of-5) was a defensible GS choice — on the 3-of-5≈4-of-5 plateau, both clearly beating
5-of-5 — not an error.** GS simply could not resolve 3-of-5 from 4-of-5; **deployment
broke the tie toward the looser 3-of-5**. The cost of picking the stricter plateau end
(4-of-5) was invisible on GS and manifest only on deployment.

> Derivation was **free** (no new API for GS): the GS verifier had been run on the
> 1-of-N union, so post-verifier sets at every vote threshold are recovered by filtering
> `vote_count` + prob≥0.15 (`verify_adversarial-text` probabilities, candidate counts
> reconcile exactly with the pre-verifier consensus n_det).

## 3. Config axis — T0.3 is the best deployed config (fixed-union)

Comparing the four deployed configs at their carried operating points against a common
extended GT (reviewed + union of all four carried reviews), corrected F1 @ 50 m:

| rank | config | corrected F1 @ 50 m |
|---|---|---|
| 1 | text-high **T0.3** (k4) | **0.800** |
| 2 | text-high T0.7 (k4, carried) | 0.780 |
| 3 | image (k3) | 0.767 |
| 4 | text-min (k4) | 0.748 |

**All six pairwise contrasts are significant (p<0.001 except T0.7>image p=0.005).** In
particular **T0.3 > T0.7 = +0.020 (p<0.001)** — consistent with, and slightly stronger
than, the per-side v2 grid's +0.016. So switching to fixed-union does **not** overturn
the config ranking; it sharpens it.

## 4. Joint oracle — total deployment gap

Combining the axes, the joint oracle is **T0.3 × 3-of-5** and the carry-forward was
**T0.7 × 4-of-5**. Scored against the fixed-union of both cells' confirmed mounds:

| cell | corrected F1 @ 50 m | precision | recall |
|---|---|---|---|
| carry-forward (T0.7 × 4-of-5) | 0.799 | 0.913 | 0.710 |
| **joint oracle (T0.3 × 3-of-5)** | **0.830** | 0.868 | 0.795 |
| **Δ (oracle − carry-forward)** | **+0.032** [+0.024, +0.040] | | p<0.001 |

The carry-forward left **+0.032 corrected-F1** on the table, decomposing roughly into a
config component (T0.7→T0.3, ~+0.020) and a threshold component (4-of-5→3-of-5, ~+0.010–0.028).

## 4b. Canonical adjudicated-GT re-score (the rigorous reference)

The cross-run comparisons in §§3–4 first used a *naive* union of every run's
review (which double-counts a mound several runs found, and lets a `mound` label
override a `not_mound`). We rebuilt a **canonical adjudicated GT** — one point per
real feature: 740 auto-resolved clusters (agreed + min-ring-collapsed), 23 of 24
human-adjudicated conflicts, and 10 of 213 cross-config-corroborated **vote=2**
candidates that survived review (a GT-completeness pass toward GS quality; the low
4.7 % yield confirms the vote≥3 floor was already near-saturated). **773 canonical
mounds.** Re-scoring §§3–4 against it:

| | config: T0.3 | T0.7 | image | text-min | T0.3−T0.7 | joint oracle Δ |
|---|---|---|---|---|---|---|
| naive union | 0.800 | 0.780 | 0.767 | 0.748 | +0.020 (p<0.001) | +0.032 (p<0.001) |
| **canonical GT** | **0.836** | **0.815** | **0.799** | **0.783** | **+0.021 (p<0.001)** | **+0.032 (p<0.001)** |

**Deltas hold; absolutes rise** ~0.02–0.04 as the ~600 duplicate phantoms clear.
Canonical joint oracle: carry-forward (T0.7×4-of-5) = **0.815** vs oracle
(T0.3×3-of-5) = **0.848**, the carry-forward leaving **+0.032 corrected-F1** on the
table (p<0.001). The threshold-axis (§1) is unchanged — it never used cross-run
unions. Provenance: `scripts/build_canonical_gt.py`, `build_vote2_enrichment_kit.py`,
`results/.../canonical-gt/canonical-review.csv`, `results/.../canonical-rescore/`.

## 5. Two-script reconciliation (single-sourced numbers)

`compute_corrected_f1_multi_buffer.py` and `paired_permutation_corrected_55maps.py`
disagreed by ~0.01 absolute F1 (e.g. k4 T0.7 0.833 vs 0.822). Cause:
`build_phantom_gdf` includes **all** of "yesterday's" mounds unconditionally (correct only
when yesterday is a single-buffer-50 m review, as in the published per-run numbers). The
fixed-union invocations here pass a **multi-buffer** review as yesterday, so the standalone
corrected-F1 script over-promotes 86 wider-ring (75–150 m) phantoms at R=50, inflating it.
`paired_permutation_corrected_55maps.py` **pre-gates yesterday by `buffer_metres ≤ R`**
(its lines 406–407), so it is correct. **All numbers in this document are single-sourced
from the permutation script.** The ΔF1s are unaffected (the bias is common to both cells);
only the absolute F1 shifts ~0.01.

**Resolved (2026-06-07).** `build_phantom_gdf` was given the symmetric yesterday-gate
(`buffer_metres ≤ R`); the standalone corrected-F1 now matches the permutation **exactly**
(k4 T0.7 = 0.8222, k3 = 0.8501, etc. — all six cells agree to 4 d.p.). The gate is a no-op
for the empty/single-buffer-50 m "yesterday" the **published** corrected-F1 runs used
(text-high empty, image single-buffer — verified from their `summary.json` provenance), so
**published numbers are unchanged**. Fix + 3 tier-1 tests committed; standalone outputs
refreshed.

## 6. Recommendation on 2-of-5 (open)

Whether to extend the curve to **2-of-5** (to confirm 3-of-5 is the deployment peak, not
merely better than 4-of-5): **probably unnecessary, but defensible for completeness.**
Evidence against a further gain: (a) the GS post-verifier curve turns over hard below the
plateau (2-of-5 = 0.816 vs 3-of-5 0.847 for HIGH-text T0.7); (b) deployment shifted the
optimum only *one* notch looser, and k3 precision is already 0.87–0.91. Cost if pursued:
the deployment **vote=2 shell is ~8 400 candidates/text run** (≈2× the vote=3 shell) →
≈ $15–30 flex + ~400–500 new VLM-only review candidates/run. Decision deferred to the
operator; requires the API gate and a further (delta-from-3-of-5) manual review.

## 7. Caveats

- **GS vs deployment use different metrics/GT by necessity**: GS is the gold reference at
  F1@20 m; deployment is the manually-corrected student GT at corrected-F1@50 m (50 m
  because the student GT carries ~25 m digitisation jitter — Obs 260). The calibrate→deploy
  gap therefore blends "unseen test set" with "different GT regime"; state this in any
  write-up.
- The fixed-union extended GT is **run-specific by construction** (phantoms come from the
  reviewed cells); the GT scope (which cells' phantoms are unioned) is stated per comparison.
- The 'uncertain' text-min candidate at a sheet edge (cand 2128, prob=1.0, raster boundary —
  un-renderable for review) is **not** promoted; a negligible (1/1591) under-credit to k3.

## 8. Provenance and reproducibility

- **Verifier run** (vote=3 shells): `outputs`/`results/deployment-oracle-2026-06-06/vote3-verify/` —
  per-candidate probabilities + manifests committed; crop PNGs excluded (regenerable via
  `run_pv.py extract`).
- **k3 scoring inputs**: `scripts/build_k3_scoring_inputs.py` →
  `results/deployment-oracle-2026-06-06/k3-scoring/<run>/{k3_verified.geojson, k3-new-review.csv}`.
- **Manual review**: `scripts/build_k3_review_kit.py` + `review_candidates.py`; labels under
  `results/deployment-oracle-2026-06-06/k3-review/<run>/{pass1-new, pass2-review, pass2-mounds-confirm}/human-review.csv`.
- **Threshold scoring**: `compute_corrected_f1_multi_buffer.py` + `paired_permutation_corrected_55maps.py`
  → `k3-scoring/<run>/{k4-corrected, k3-corrected, perm-k3-vs-k4}/`.
- **GS post-verifier sweep**: `results/deployment-oracle-2026-06-06/gs-postverifier-sweep/` (derived
  from `outputs/h11/pv-diag-384/<pool>/<temp>/{consensus-n5/consensus_t1.geojson, verified-v1-n5/probabilities.json}`).
- **Config axis**: `results/deployment-oracle-2026-06-06/config-axis-fixedunion/`.
- **Joint oracle**: `results/deployment-oracle-2026-06-06/joint-oracle/`.
- Compute on sapphire (≤10 physical-core cap); GS derivation $0 API; only the vote=3 verifier
  run incurred spend (≈ $7.4 flex).

---

## Changelog

### 2026-06-07 — Canonical adjudicated-GT re-score (§4b)

Rebuilt the cross-run reference as a canonical, deduplicated, adjudicated GT (773
mounds: 740 auto + 23 of 24 conflict adjudications + 10 of 213 vote=2 enrichment),
replacing the naive review-union for the config-axis and joint-oracle. Config and
joint **deltas held** (T0.3−T0.7 +0.020→+0.021; joint +0.032 unchanged) while
**absolutes rose** (T0.3 0.800→0.836; joint oracle 0.830→0.848) as ~600 duplicate
phantoms cleared. Threshold-axis (§1) untouched. Run on zbook (sapphire engaged by
another session).

### 2026-06-07 — Phantom-gate fix

Applied the symmetric yesterday-gate to `build_phantom_gdf` (`buffer_metres ≤ R`); the
standalone `compute_corrected_f1_multi_buffer` now matches
`paired_permutation_corrected_55maps` to 4 d.p. across all six k4/k3 cells. No headline
number moved (the doc was already single-sourced from the permutation); §5 updated to
record the resolution. Published per-run corrected-F1 numbers verified unchanged (their
"yesterday" was empty or single-buffer-50 m). Fix + 3 tier-1 tests + refreshed standalone
outputs committed.

### 2026-06-07 — Original publication

First publication of the 55-map deployment-oracle analysis (Session 104). Establishes:
threshold axis (k3=3-of-5 > carried k4=4-of-5, all three text configs, p<0.001); GS
calibration check (4-of-5 on a 3-of-5≈4-of-5 GS plateau, both ≫ 5-of-5 — carry-forward not
an error); config axis fixed-union (T0.3 > T0.7 > image > text-min, all significant); joint
oracle T0.3×3-of-5 leaving the carry-forward T0.7×4-of-5 +0.032 corrected-F1 @ 50 m behind
(p<0.001). Includes the two-script reconciliation (permutation script authoritative) and a
deferred recommendation on 2-of-5. Vote=3-shell verifier run: 10 622 candidates, flex,
0 failures, ≈ $7.4.
