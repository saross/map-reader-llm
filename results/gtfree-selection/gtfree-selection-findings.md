# GT-free run selection — findings

> **Last revised**: 2026-06-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

## 1. The question

Production discovery runs on new map corpora usually have **no ground
truth** — no legacy digitisation, no curated reference. Obs 366 § 2 showed
that curating a calibration reference big enough to ground configuration
decisions (~10–20 representative sheets, ~1,000–2,000 mounds) is too
expensive to construct routinely; Obs 367 showed that deploying the
calibration tie-set is cheap (~25 passes, ~$733 audited flex on an
8,541-tile corpus) — but deploy-and-evaluate still needs an *evaluator*.
Can the best run be identified **from the runs alone**?

## 2. Design — leave-one-family-out (LOFO) consensus pseudo-GT

The eight 55-map board cells group into four configuration **families** by
proposer recipe: T03 (text HIGH T = 0.3), TH7 (text HIGH T = 0.7), TM
(text MINIMAL T = 0.7, including the 10-pass uplift), and IM (image HIGH).
For each family F, a pseudo-ground-truth is built from the **other three
families'** k3 detection sets: union the three sets, single-linkage
cluster at 50 m, keep clusters supported by ≥ 2 distinct families
(primary; ≥ 3 as sensitivity), centroid = pseudo-mound. Every cell is then
scored against **its own family's** pseudo-GT with the standard board
machinery (Hungarian per map, 50 m), so no cell is evaluated against a
reference containing its own family's detections — the anti-circularity
device the design depends on.

Because the canonical extended GT exists for this corpus, the GT-free
ranking can be validated against the true board
(`results/55map-leaderboard/55map_leaderboard_50m.json`): Spearman rank
correlation plus top-pick agreement.

Script: `scripts/test_gtfree_selection.py`; results:
`results/gtfree-selection/gtfree_selection.json`.

## 3. Results

**Primary (vote ≥ 2 of the three other families)** — pseudo-GT sizes
4,399–4,539 points (true GT: 5,161):

| cell | pseudo-F1 (GT-free) | true F1@50 | true tier |
|---|--:|--:|--:|
| TH7-k3 | **0.8933** | 0.8425 | **1** |
| T03-k4 | 0.8895 | 0.8359 | 2 |
| T03-k3 (oracle) | 0.8844 | 0.8476 | 1 |
| TH7-k4 (carry-forward) | 0.8841 | 0.8152 | 3 |
| TM-n10-k5 (uplift) | 0.8675 | 0.8290 | 2 |
| TM-k3 | 0.8624 | 0.8127 | 3 |
| TM-k4 | 0.8387 | 0.7831 | 5 |
| IM-k3 | 0.8159 | 0.7987 | 4 |

**Spearman(pseudo, true) = +0.881** over all eight cells (+0.857 over the
seven text cells). The top pick, TH7-k3, is **statistically tied with the
true winner** T03-k3 on the real board (both Tier 1; their pairwise
p = 0.127, ns) — the GT-free "miss" sits inside a tie the 8,541-tile
instrument itself cannot resolve. At the resolution that exists, the
GT-free practitioner picks correctly, and the cost meta-rule (Obs 357)
then breaks the residual tie at exactly the scope Obs 362 qualified it to.

**Sensitivity (vote ≥ 3, unanimous-of-others)**: the ranking **collapses**
(Spearman −0.095 all eight; −0.536 text-only; reference 3,285–3,654
points). A unanimous consensus reference is so conservative it inverts
the ranking — the diagnostic *requires* permissive consensus.

## 4. The systematic bias — an amplified double-miss blind spot

The consensus pseudo-GT cannot contain mounds that fewer than two
families found: it inherits an amplified version of the double-miss
structure quantified for the real GT in Obs 361. Consequences, visible in
the table: the reference **under-rewards recall**, producing within-family
k4-above-k3 inversions (pseudo ranks T03-k4 over T03-k3; the truth is the
reverse) and a compressed pseudo-F1 spread (0.816–0.893 vs true
0.783–0.848). A practitioner should read the pseudo-ranking as
**precision-tilted** and apply a recall-permissive thumb on the scale —
the same direction as the deployment-threshold lesson of Obs 358,
arrived at by an independent route.

Pseudo-F1 **absolute values are not comparable to true F1** (the
reference differs in size and composition); only the ranks carry
information.

## 5. The protocol (the citable deliverable)

For a production discovery deployment with no ground truth:

1. **Deploy the calibration tie-set**, exploiting free post-hoc threshold
   sweeps and nested pass counts (the ~25-pass / ~$733 covering design,
   Obs 367).
2. **Rank candidates by LOFO vote ≥ 2 consensus agreement** (this
   document; permissive consensus only — vote ≥ 3 inverts).
3. **Expect the top picks to be statistically tied**; break the final tie
   by **cost** (Obs 357, within its Obs 362 scope qualification), with a
   recall-permissive lean (§ 4).
4. **Sanity-check with the free diagnostics**: vote-distribution diversity
   (union-growth per pass; unanimity fraction — the signal that predicted
   Flash 3.5's PV failure before any scoring, Obs 359), detection count
   against archaeological density priors, and nearest-neighbour spacing
   against known feature morphology. Detection count alone is a usable
   secondary signal in the PV regime (Spearman +0.71 over the eight
   cells; 3-for-3 within config families) but fails across modality —
   the image cell has the third-highest count and the second-worst F1.

## 6. Caveats

- **Retrodiction on one corpus, one symbol type, eight cells, four
  families.** The Spearman rests on eight points; the protocol has not
  been tested prospectively. A pre-registered application to a new corpus
  is the natural follow-up.
- **Families are unequally correlated**: T03 and TH7 share the HIGH-text
  recipe (temperature apart), so each flatters the other's pseudo-GT;
  IM contributes the most independent perspective. With fewer or more
  correlated candidate configurations the consensus reference would
  weaken — config diversity in the deployed tie-set is part of what makes
  the evaluator work.
- **Top-pick resolution is bounded by the true board's own tie** — the
  method cannot out-resolve the instrument it is validated against.
- The clustering (single-linkage, 50 m) is the same radius as the
  operational buffer; chain-merging risk is low at the corpus's 375 m
  median mound spacing but untested on denser feature types.

## See also

- **Obs 366 § 2** — the calibration power analysis this answers.
- **Obs 367** — the deploy-and-evaluate covering design (step 1).
- **Obs 361** — GT epistemics; § 4's bias is its amplified analogue.
- **Obs 358** — the recall-permissive deployment lesson.
- `results/55map-leaderboard/` — the true board used for validation.

## Changelog

### 2026-06-13 — Original publication

First write-up of the LOFO GT-free selection test (Session 113;
Shawn-directed). Test committed at `59f7e919a`, results at `3c38acc94`.
