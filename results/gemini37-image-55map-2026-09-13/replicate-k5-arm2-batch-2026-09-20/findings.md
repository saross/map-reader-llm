# Arm 2 K = 5 replicate: does the K = 3 → K = 5 gain survive re-invocation?

> **Last revised**: 2026-09-20 (original publication — the batch replicate of
> the arm 2 K = 5 verifier leg, its two cells, the four paired permutation
> tests, and the verdict against the declaration's replicate rule). See
> [§ Changelog](#changelog) for revision history.

## 1. The question and the rule it is answered against

The 3.7 image campaign's pure stack — arm 2, a `gemini-3.7-flash` proposer
verified by `gemini-3.7-flash` at low thinking and T = 0 — gains **+0.0071
micro-F1 @ 50 m** going from the K = 3 carried point (0.88, k3) to the K = 5
carried point (0.90, k5), at *p* < 0.0001 on a paired tile-swap permutation
test, while tile-MCC moves only +0.0012 at *p* = 0.61
(`reports/text-vs-image-tracks-2026-09-20.md` § 4.6).

That F1 gain is smaller than the verifier's own re-invocation noise. The
image-2x2 declaration records the floor as caveat 1
(`reports/image-2x2-tests-declaration-2026-09-19.md` § 5): independent
re-invocations of these verifiers at T = 0 "differ in ~40 % of probabilities
and flip 3.5–5.3 % of decisions at the operating point", and the rule it
attaches is explicit —

> A null result is uninformative about small effects; a significant result
> smaller than the floor is not claimed without a replicate arm.

The PI approved that replicate arm on 2026-09-20 (up to US$20). This note
reports it.

## 2. What was run

A second, independent invocation of the **same** verifier over the **same**
9,173-candidate K = 5 union — same crops (`…/crops_k5/`), same union
(`…/union_k5.geojson`), same model, thinking level and temperature — on the
Batch API rather than realtime flex, per the 2026-09-18 routing ruling.

| item | value |
|---|---|
| Leg | `outputs/gemini37-image-55map-2026-09-13/verifier/g384_ov192_55map_g37img/verify_k5_arm2_replicate-batch-2026-09-20/` |
| Original leg | `…/verify_k5_arm2/` (realtime flex) |
| Model / thinking / temperature | `gemini-3.7-flash` / low / 0.0 |
| Candidates | 9,173 of 9,173, 0 failed |
| Route | Batch API, three jobs |
| Data commit | `3f8af3a65` |
| Audited cost | **US$10.2033** (US$0.001112/candidate) |

The cost is the `STAGE TOTAL (audited)` line of
`scripts/audit_verifier_cost.py <leg> --tier flex`, re-run for this note:

```text
  STAGE TOTAL (audited)          n=   9173             audited=$   10.2033  $0.001112/candidate
```

Note that the leg's own `run.meta.json` `cost_estimate` reads US$20.4066 —
exactly double — and the auditor marks it "do NOT use at a gate". The audited
figure is the one quoted.

Every derived artefact below was produced by *importing*
`scripts/gemini37_image_55map_r2.py` — its `rung_frame` inputs, its
`assign_eval_frame_tiles` re-stamping, its `materialise` predicate, its
`achievable_points` grid, its `engine_command` recipe, its `load_frames`,
`read_detections`, `per_tile_arrays`, `tile_vectors`, `permutation_test_float`
and `permutation_test_mcc`. Nothing in `scripts/` was modified. The replicate
therefore lands on the same instrument as the cells it is compared against:
the r2 reference (`best-available-gt-55maps-r2.geojson`, 5,018 points), the
8,541-tile evaluation frame, 50 m matching, BCa intervals from 10,000
bootstrap draws at seed 42, `--mcc`, `--require-clean-inputs`.

## 3. Agreement between the two invocations

Computed over all 9,173 shared `candidate_id` keys (`agreement.json`;
recomputed for this note, not carried from the commit message):

| statistic | replicate vs original | 2026-09-19 probe, batch vs flex |
|---|---:|---:|
| n compared | 9,173 | 171 |
| identical probabilities | 5,826 = **63.5 %** | 60 % |
| decision flips at 0.90 | 226 = **2.46 %** | 5.3 % |
| \|Δp\| > 0.5 | 186 = 2.03 % | 6 = 3.5 % |
| mean \|Δp\| | 0.0254 | — |
| median \|Δp\| | 0.0000 | — |

The probe figures are from
`…/probe-batch-vs-flex-2026-09-19/README.md`, whose three-row table gives
60 % / 5.3 % / 6-of-171 for the batch-K5-vs-flex-K5 comparison.

Two things follow. First, the identical-probability share at full scale
(63.5 %) sits right on the probe's 171-twin estimate (60 %) and on E89's
"~40 % differ" — the probe was not a small-sample fluke. Second, the **flip
rate is about half** what the probe measured: 2.46 % against 5.3 %, and below
the declared 3.5–5.3 % floor. The probe's 171 twins were a seed-42 sample, and
about 9 flips of 171 carries a wide interval; 226 of 9,173 is the better estimate for
this leg. The flips are also close to balanced — 110 candidates the replicate
keeps and the original drops, 116 the reverse — so the retained set barely
changes size (7,122 against 7,128 above 0.90 before the vote filter; 5,202
against 5,219 after it).

## 4. The cells

All five are at 50 m on the r2 reference, BCa 10,000, seed 42. Replicate cells
are in `cells/` beside this note; the three comparators are the campaign's own
committed cells in `results/gemini37-image-55map-2026-09-13/cells/`.

| cell | point | n | P @ 50 m | R @ 50 m | F1 @ 50 m | tile-MCC |
|---|---|---:|---|---|---|---|
| **IMG-ARM2-K5-carried-replicate** | (0.90, k5) | 5,202 | 0.9114 [0.9031, 0.9193] | 0.9448 [0.9382, 0.9508] | **0.9278** [0.9223, 0.9329] | **0.7655** [0.7523, 0.7783] |
| IMG-ARM2-K5-carried (original) | (0.90, k5) | 5,219 | 0.9092 [0.9010, 0.9172] | 0.9456 [0.9390, 0.9517] | 0.9270 [0.9215, 0.9322] | 0.7659 [0.7528, 0.7790] |
| **IMG-ARM2-K5-f1-oracle-replicate** | (0.95, k5) | 5,184 | 0.9142 [0.9061, 0.9219] | 0.9444 [0.9378, 0.9505] | **0.9290** [0.9235, 0.9342] | **0.7674** [0.7545, 0.7801] |
| IMG-ARM2-K5-f1-oracle (original) | (0.95, k5) | 5,197 | 0.9121 [0.9039, 0.9199] | 0.9446 [0.9381, 0.9507] | 0.9280 [0.9225, 0.9331] | 0.7681 [0.7552, 0.7811] |
| IMG-ARM2-K3-carried (original) | (0.88, k3) | 5,357 | 0.8908 [0.8820, 0.8993] | 0.9510 [0.9447, 0.9568] | 0.9199 [0.9142, 0.9254] | 0.7648 [0.7516, 0.7776] |

Three observations before the tests.

**The replicate's own F1 oracle lands at the same point as the original's** —
(0.95, k5) on both, out of a 130-point achievable grid for the replicate
(`sweep_IMG-ARM2-K5-replicate.csv`) against 120 for the original
(`results/gemini37-image-55map-2026-09-13/sweeps.json`, `rungs.IMG-ARM2-K5`).
The carried-versus-oracle tax is therefore the same shape on both legs:
+0.0012 F1 on the replicate (0.9278 → 0.9290), +0.0010 on the original
(0.9270 → 0.9280). Re-invocation moves individual probabilities a great deal
and moves the *selected operating point* not at all.

**Every interval overlaps heavily.** The replicate's F1 CI [0.9223, 0.9329]
contains the original's point estimate and vice versa, and both K = 5 CIs
overlap the K = 3 CI substantially. The BCa intervals here are unpaired and so
are the wrong instrument for a within-union contrast — which is exactly why the
paired permutation tests below exist.

**Precision, not recall, carries the K difference.** K = 3 → K = 5 buys
+0.021 precision on the replicate (0.8908 → 0.9114) for −0.006 recall
(0.9510 → 0.9448). That is unanimity working as the image pool's precision
filter, and it is why F1 moves while tile-MCC — which is driven by whether a
tile has *any* detection — does not.

## 5. The four tests

Paired tile-swap permutation, 10,000 permutations, seed 42, over all 8,541
tiles, on both metrics, using the script's own `permutation_test_float` and
`permutation_test_mcc`. Truth vectors were asserted equal for every pair. Full
output with null means and standard deviations: `tests.json`.

### Micro-F1 @ 50 m

| test | A | B | F1 A | F1 B | observed Δ | *p* | null mean | null SD |
|---|---|---|---:|---:|---:|---:|---:|---:|
| **(a)** drift only | K5 replicate | K5 original | 0.927789 | 0.927029 | **+0.000759** | 0.4015 | −0.000005 | 0.000904 |
| **(b)** the claim | K5 replicate | K3 original | 0.927789 | 0.919904 | **+0.007885** | **< 0.0001** | +0.000004 | 0.001471 |
| **(c)** for the record | K5 original | K3 original | 0.927029 | 0.919904 | **+0.007126** | **< 0.0001** | +0.000009 | 0.001494 |
| **(d)** drift at the oracles | K5 oracle replicate | K5 oracle original | 0.929034 | 0.928047 | **+0.000987** | 0.2861 | −0.000003 | 0.000921 |

### Tile-MCC

| test | A | B | MCC A | MCC B | observed Δ | *p* | null mean | null SD |
|---|---|---|---:|---:|---:|---:|---:|---:|
| **(a)** drift only | K5 replicate | K5 original | 0.765482 | 0.765934 | **−0.000452** | 0.8225 | +0.000006 | 0.001648 |
| **(b)** the claim | K5 replicate | K3 original | 0.765482 | 0.764766 | **+0.000716** | 0.7459 | −0.000014 | 0.002077 |
| **(c)** for the record | K5 original | K3 original | 0.765934 | 0.764766 | **+0.001168** | 0.6141 | −0.000020 | 0.002218 |
| **(d)** drift at the oracles | K5 oracle replicate | K5 oracle original | 0.767412 | 0.768146 | **−0.000734** | 0.7100 | +0.000018 | 0.001724 |

*p* = 0 over 10,000 permutations is reported as *p* < 0.0001, per the
campaign's convention.

**Test (c) reproduces the briefed figures exactly**: +0.007126 F1 at
*p* < 0.0001 and +0.001168 tile-MCC at *p* = 0.6141, against the +0.0071 and
+0.0012 / *p* = 0.61 of `reports/text-vs-image-tracks-2026-09-20.md` § 4.6. The
pipeline reproduced here is therefore the same pipeline, and (a), (b) and (d)
can be read against (c) without a mechanism caveat.

No Benjamini–Hochberg adjustment is applied. These four are a replication probe
of one already-declared contrast, not a new declared family; raw *p*-values are
reported, and the strongest claim below would survive a ×4 adjustment anyway.

## 6. Verdict

**The K = 3 → K = 5 micro-F1 gain is claimable. The tile-MCC gain is not.**

The declaration's rule asks two things of a replicate arm, and this one answers
both in the same direction. First, is the contrast still significant when the
K = 5 leg is a fresh invocation? Test (b) puts it at **+0.0079 F1, *p* <
0.0001** — not merely surviving but nominally *larger* than the original
+0.0071 of test (c), because the replicate's own carried F1 (0.9278) came out
slightly above the original's (0.9270). Second, does that effect exceed what
re-invocation alone produces? Test (a), the drift-only contrast — same union,
same operating point, same model, same temperature, only a different
invocation — gives **+0.0008 F1, *p* = 0.4015**, and test (d) repeats the
exercise at each leg's own F1 oracle for **+0.0010, *p* = 0.2861**. The K
effect is about **ten times** the measured drift effect, and the drift effect
is itself indistinguishable from zero: both drift contrasts sit inside their
nulls at under 1.1 null standard deviations, where the K contrast sits at
about 5.4. The margin is not marginal. On tile-MCC nothing is claimable at any
of the four contrasts — (b) gives +0.0007 at *p* = 0.75, (c) +0.0012 at
*p* = 0.61, and the two drift contrasts are *negative*, which is the signature
of a metric whose movement here is noise. That is not a new finding but it is
now a replicated one: **K = 5 buys precision at the detection level and buys
nothing at the tile level.**

The residual caution worth recording is that a single replicate arm measures
the drift band with one degree of freedom. Tests (a) and (d) agree with each
other (+0.0008 and +0.0010, both null) and the flip rate agrees with the
independent 2026-09-19 probe to within a factor of two, so the band is
consistently characterised — but "the drift effect on F1 is ≈ +0.001" rests on
two contrasts from one pair of legs, not on a distribution of re-invocations.
The claim that the K effect exceeds drift by an order of magnitude is robust to
that; a claim about the drift effect's own size would not be.

## Changelog

### 2026-09-20 — Original publication

First publication. The arm 2 K = 5 verifier leg was re-run on the Batch API
over the same 9,173-candidate union (data commit `3f8af3a65`, audited
US$10.2033) to test the image-2x2 declaration's replicate rule
(`reports/image-2x2-tests-declaration-2026-09-19.md` § 5 caveat 1) against the
+0.0071 F1 gain reported in `reports/text-vs-image-tracks-2026-09-20.md` § 4.6.

State at publication: the replicate was materialised at the carried point
(0.90, k5) and at its own F1 oracle, which fell at (0.95, k5) — the same point
as the original leg's — from a 130-point achievable sweep; both cells were
scored on the r2 board's own engine recipe; four paired tile-swap permutation
tests were run at 10,000 permutations, seed 42. Verdict: the K = 3 → K = 5
micro-F1 gain **is** claimable (test (b), +0.0079, *p* < 0.0001, against a
drift-only contrast of +0.0008, *p* = 0.40); the tile-MCC gain is **not**
(*p* = 0.61–0.75 across all contrasts). No board was re-tiered, no signed row
touched, and no campaign cell or manifest was modified — the replicate's
artefacts live entirely in this directory.
