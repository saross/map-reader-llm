# Observation drafts — 2026-09-19 (S155), for PI review before entry

Four candidate entries for `docs/notes/working-notes.md`, drafted by Claude on
the PI's request. Numbers are re-derived from the committed files named in
each entry. The next free number in the notes is 484; the numbers below are
provisional until entered. Nothing here is in the notes yet.

---

## Observation 484 (draft): K = 5 confirms the image-pool mechanism and finds its knee — pass count buys precision, not recall, and the third step is inside verifier drift

**Context**: Session 155 (2026-09-18/19). The Gemini 3.7 image 55-map campaign
(Obs 481–483 lineage; card `planning/gemini37-image-55map-2026-09-13.md`) was
extended from K = 3 to K = 5 by two Batch-API proposer passes, a K = 5 first-N
union of 9,173 candidates, both verifier arms, and the campaign-table r2 chain
(`scripts/gemini37_image_55map_r2.py --rungs 5`; PR #19, merged `eb8c68038`).
Cells scored on the r2 board's instrument (micro-F1 @ 50 m, tile-MCC on the
8,541-tile frame), carried points fixed on the GS before any 55-map score
(`results/gemini37-image-55map-2026-09-13/sweeps.json`, `cells/`).

**The observation**: the ladder is monotone on both arms and the gain is
almost entirely precision.

| K | arm 2 n | P | R | F1@50 | tile-MCC | FP detections | FP tiles |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5,997 | 0.8007 | 0.9570 | 0.8719 | 0.7569 | 1,195 | 165 |
| 3 | 5,357 | 0.8908 | 0.9510 | 0.9199 | 0.7648 | 585 | 127 |
| 5 | 5,219 | 0.9092 | 0.9456 | 0.9270 | 0.7659 | 474 | 114 |

Arm 1 runs 0.8477 → 0.9025 → 0.9130 (F1) and 0.7324 → 0.7490 → 0.7529 (MCC).
The findings document's § 3 mechanism (passes largely agree, so unanimity is
a precision filter) holds at the third rung: recall gives up 0.011 across the
whole ladder while false-positive detections fall by 60 %. The increments
shrink: K = 1 → 3 is +0.048 F1 / +0.0078 MCC (both BH-significant in the
declared family); K = 3 → 5 is +0.0071 / +0.0011.

Two things make K = 3 the knee rather than K = 5 the target. Cost: each
proposer pass is ≈ US$62–82, so K = 5 costs 1.5x K = 3 for a seventh of its
gain. Drift: erratum E89 and the 2026-09-19 batch-vs-flex probe put
independent re-invocation of this verifier at ~40 % of probabilities moving
and 3.5–5.3 % of decisions flipping at the operating point, so +0.007 F1 at
n ≈ 5,200 is inside the band verifier nondeterminism alone can produce. The
K = 3 → 5 contrast was not preregistered (the card stopped the ladder at 3)
and is declared exploratory; no permutation test has been run on it.

**Also**: every carried point sits within 0.001 F1 of its rung's oracle
(K = 5 arm 2: carried 0.9270 at 0.90, oracle 0.9280 at 0.95), so the GS
calibration transfers to the 55-map corpus with no hidden headroom.

**Why it matters**: the paper can state the image ladder's shape with three
points instead of two, name K = 3 as the operating rung on a cost basis, and
report K = 5 as the best cell (F1 0.9270, MCC 0.7659, the corpus leader on
both metrics) without claiming the last step is real.

Search terms: Obs 484, K = 5 image ladder, pass count precision filter,
ladder knee, verifier drift band, exploratory contrast, IMG-ARM2-K5-carried.

---

## Observation 485 (draft, PRELIMINARY until K = 3 and K = 5 land): the Gemini 3 image proposer at a single pass over-generates threefold, halving micro-F1 while tile-MCC barely moves

**Context**: Session 155. The second row of the image proposer x verifier 2x2
at deployment scale: the Gemini 3 image pool (`gemini3-image-55map-2026-09-16`,
5 x 24,561 tiles, `detect_brief-text-image`, `minimal`, T 0.7), verified by
the same two arms as the 3.7 row at operating points fixed on the GS from
`image-b-gs-2026-08-28` (`results/gemini3-image-55map-2026-09-16/gs-calibration/`).
K = 1 rung scored 2026-09-19 (`results/gemini3-image-55map-2026-09-16/cells/`,
`ba19eebd1`); every chain gate passed (booking 22,785/22,785, calibration
constants verified against the sweep files).

**The observation**: at K = 1 the Gemini 3 row is far below the 3.7 row on
micro-F1 and close to it on tile-MCC.

| cell (K = 1, carried) | n | P | R | F1@50 | tile-MCC | FP tiles |
|---|---:|---:|---:|---:|---:|---:|
| Gemini 3 pool, arm 1 (0.15) | 8,529 | 0.529 | 0.900 | 0.6664 | 0.7144 | 301 |
| Gemini 3 pool, arm 2 (0.88) | 9,172 | 0.514 | 0.939 | 0.6644 | 0.7063 | 405 |
| 3.7 pool, arm 2 (0.88) | 5,997 | 0.801 | 0.957 | 0.8719 | 0.7569 | 165 |

The Gemini 3 pool yields 1.7x the raw detections per pass and its K = 1
union is 3.3x the 3.7 pool's (22,785 vs 6,985). At the GS-carried point the
verifier keeps about half of that union, and the kept half carries ~4,000
more false positives than the 3.7 cell. Micro-F1 halves its distance to 1;
tile-MCC moves 0.05 because surplus detections land on tiles that were
already counted (301–405 FP tiles against 165). The oracles do not rescue
it: the best F1 the rung can reach is 0.6923 (arm 2, at 0.98).

**Reading**: consistent with the GS calibration, where Gemini 3 image sat
0.08–0.10 F1@20 below 3.7 image at every rung, amplified by scale. It is a
proposer-family effect, not a verifier one: both arms see it. K = 3 and K = 5
impose unanimity, which on an image pool is a precision filter (Obs 484), so
the gap is expected to close at the higher rungs — that comparison, at
matched K, is what the 2x2 was built to make. Until those rungs are scored
this entry is a single-rung reading and must not be cited alone.

Search terms: Obs 485, Gemini 3 image pool over-generation, 2x2 proposer
family row, micro-F1 vs tile-MCC divergence, G3IMG-ARM2-K1-carried.

---

## Observation 486 (draft): the Batch API route is inside the verifier's own re-invocation drift — an E89 corollary that licensed a route switch

**Context**: Session 155. The PI ruled (2026-09-18) that Gemini 3.7/3.8 legs
run the Batch API by default after a 3.7 realtime-flex verifier arm fell to
~1 candidate/min under a 503 storm (44,091 retries, 21 hours). Before the
Gemini 3 row's arm 2 legs went to batch, the phase gate asked whether the
route changes the answers: the 3.7 row's arm 2 had run on flex.

**The observation**: 200 candidates of the 3.7 K = 5 union (seed 42), whose
flex arm 2 probabilities were on file, were re-verified on batch in four
50-candidate jobs (`outputs/gemini37-image-55map-2026-09-13/verifier/g384_ov192_55map_g37img/probe-batch-vs-flex-2026-09-19/`,
`cab5d1b91`, audited US$0.2248).

| comparison | n | identical p | flips at 0.90 | abs dp > 0.5 |
|---|---:|---:|---:|---:|
| flex K5 vs flex K3 twin (same route, same mound's crop from the K = 3 union) | 171 | 61 % | 3.5 % | 5 |
| batch K5 vs flex K5 (same crop, route differs) | 171 | 60 % | 5.3 % | 6 |
| batch K5 vs flex K3 twin | 171 | 61 % | 4.1 % | 7 |

The twin baseline is the same verifier re-invoked on flex against the K = 3
union's crop of the same mound (matched within 5 m, median 0.57 m). The
batch route's drift is indistinguishable from the route's own re-invocation
drift: nine flips against six of 171 is noise at this n. The probe also
proved the multi-chunk batch orchestration on four jobs before it carried
45,786-request legs.

**Why it matters**: E89 (T = 0 is not deterministic across independent calls)
now has a route corollary: batch versus realtime is not a parameter of the
experiment for this verifier, only of its bookkeeping. It also fixes the
floor for any within-cell increment the paper may claim: below ~5 % of
decisions at the operating point, a difference between two verifier passes
is not distinguishable from drift without replication.

Search terms: Obs 486, batch vs flex route equivalence, E89 corollary,
verifier re-invocation drift 3.7 low, phase-gate probe.

---

## Observation 487 (draft): a blocked launch session is a queued command — it executed 21 hours late and rebuilt correct artefacts with a rejected builder

**Context**: Session 155. An `ssh host 'nohup job … & ; <more commands>'`
line launched the day's first verifier arms at 23:26 UTC on 2026-09-17. The
`nohup` inherited the session's descriptors, so the SSH call did not return;
the harness moved it to the background and the session went on. Later that
evening the union builder named in that line's tail (`merge_passes.py`) was
rejected for the GS calibration in favour of `image_b_prepare_and_union.py`,
the correct unions were built, their crops extracted, and arm 1 verified.

**The observation**: at 20:47 UTC on 2026-09-18, when the arms driver
exited, the blocked session ran the rest of its command line: it rebuilt the
GS calibration unions with the rejected builder (2,396 / 3,005 candidates over
the correct 2,227 / 2,788) and re-extracted the crops over the correct ones.
The next leg's union-versus-crops count gate then PASSED on the wrong pair,
and a batch job of 2,396 requests was lodged (≈ US$2.85) before the mismatch
was seen by reading the committed manifest against the working tree. Reverted
with `git checkout`, crops re-extracted byte-identically, leg relaunched.

**Why it matters**: three of the session's defects share one family — a step
that reports success while its artefact is wrong (a progress line reading
9173/9173 with 1,471 failed; a normaliser taking the right file by sort-order
coincidence; chunk metadata inherited from chunk 0) — and this one adds the
temporal form: a command that succeeds, but a day later, against a world that
has changed under it. The gate that should have caught it compared two
artefacts both written by the stale command, so they agreed. The defence is
procedural and now in `docs/agent-guidance.md`: redirect all three descriptors
on a launch, put nothing after a launch on the same line, and treat a launch
call that "timed out" as holding an unexecuted tail until its process is
gone. For reproducibility the lesson is that a count gate is only as good as
the independence of the two counts it compares.

Search terms: Obs 487, blocked ssh session, deferred command execution,
count gate independence, stale-session rerun, image-b-gs mergebuilt archive.
