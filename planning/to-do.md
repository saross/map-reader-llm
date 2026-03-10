# To-Do Items

## Urgent

- [x] **Document Phase 2e carry-forward parameters** — Phase 2e (H4 ordering)
  was executed in Session 33 (2026-02-12) with result "no significant ordering
  effect after FDR correction; config-default ordering carried forward." Results
  are in the session log and git history (commits `8f34ed4`, `de6ac2e`,
  `8118eb5`, `7a038b6`) but no `results/phase2e-carry-forward-parameters.md`
  was created. Needed for completeness alongside the 2a–2d carry-forward docs.
  *(Completed 2026-03-09, Session 43)*

## Pending

### Two-Stage Pipeline Optimisation (Post Phase 3d Pilot)

**Context**: Phase 3d pilot showed two-stage proposer→verifier architecture
achieves F1=0.711 (image) / 0.796 (text) with adversarial verifier,
substantially exceeding single-stage baselines. These tasks explore how
to push performance further with purpose-built proposer and verifier
configurations.

#### Free analyses (no API calls)

- [x] **Plot precision-recall curves** from existing Phase 3d pilot probability
  data — reveals optimal thresholds more precisely than 0.1-step grid, and
  visualises the trade-off space for each verifier strategy × track.
  *(Completed 2026-03-09, Session 44)*. Results: adversarial verifier
  optimal at t=0.21 (image F1=0.711) and t=0.16 (text F1=0.796);
  standard/checklist are step functions due to bimodal distributions.
  See `results/figures/phase3d-pr-curves.png` and `results/phase3d-pr-curves.csv`
- [x] **Cross-modal overlap analysis** — match Phase 3d proposer outputs (132
  image candidates, 140 text candidates) to ground truth. *(Completed
  2026-03-09, Session 44)*. Key finding: **union recall = 0.866 (84/97)**;
  65 mounds found by both, 6 image-only, 13 text-only, 13 by neither.
  Cross-modal union proposer is strongly supported.
  See `results/figures/phase3d-cross-modal-venn.png`
- [x] **Multi-verifier ensemble** (revised from "reconstruct consensus") —
  original item was wrong: pilot had K=1 verifier passes, not K=10.
  Instead tested ensemble of 3 verifier strategies (average, majority,
  union vote). *(Completed 2026-03-09, Session 44)*. Finding: standard
  and checklist are 100% redundant on image track; ensemble adds marginal
  +0.007 F1 over adversarial alone. Not worth pursuing.

#### Low-cost experiments (~$7 each)

- [ ] **Pilot high-recall text proposer** — T=0.7, HIGH thinking,
  recall-biased prompt ("flag anything plausible"), no negative examples,
  single pass; target: recall > 0.85 even at precision ~0.35
- [ ] **Pilot high-recall image proposer** — same approach for image track;
  may also test reduced/no visual examples to avoid anchoring
- [x] **HIGH-thinking verifier test** — run adversarial verifier with HIGH
  thinking on existing pilot candidates; compare to MINIMAL-thinking
  baseline. *(Completed 2026-03-10, Session 45)*. NEGATIVE RESULT:
  F1 dropped from 0.768 to 0.747. See `results/phase3d-high-thinking-results.md`

#### Medium-cost experiments (~$35 each)

- [ ] **Full 1-of-5 union proposer + adversarial verifier** (text track) —
  5 passes at T=0.7 + HIGH thinking with recall-biased prompt, union all
  candidates, then adversarial verifier filters; target F1 > 0.80
- [x] **Cross-modal union proposer + verifier** — union of image-track and
  text-track proposer candidates, then single adversarial verifier; exploits
  complementary detection profiles across modalities. *(Completed 2026-03-10,
  Session 45)*. Results: F1=0.768 (P=0.711, R=0.835) at t=0.11 — recall
  exceeds both single tracks (0.784 text, 0.711 image) but F1 is −0.028
  below text-only (0.796). Provenance: both-track candidates strongest
  (P=0.867), image-only weakest (P=0.318). Cost: ~$2 (184 API calls).
  See `results/phase3d-union-results.md`
- [ ] **Multi-pass verifier for borderline candidates** — first verifier pass
  on all candidates, second pass (different framing) only on borderline
  candidates (probability 0.3–0.7); targets recall preservation

#### Verifier improvement experiments (planned)

See `planning/phase3d-verifier-experiments.md` for full details.

- [x] **A: Provenance-informed verification** (~$1) — tell verifier that
  text track did NOT flag image-only candidates. *(Completed 2026-03-10,
  Session 46)*. Best result: ΔF1=+0.011, removed 3 FPs. Did not reach
  F1>0.796 target. See `results/phase3d-verifier-experiments-abc.md`
- [x] **B: Visual examples for image-only** (~$0.50) — test
  include_examples=True on 44 image-only candidates. *(Completed
  2026-03-10, Session 46)*. Paradoxical: best image-only P (+0.073) but
  worst whole-pool F1 (−0.004) due to greedy matching non-additivity.
- [x] **C: Temperature variation + majority vote** (~$1.50) — T=0.5,
  3 samples per candidate, test whether T=0 confidence is genuine.
  *(Completed 2026-03-10, Session 46)*. Negative result at both T=0.5
  (ΔF1=+0.004) and T=1.0 (ΔF1=0.000). Errors are systematic, not
  stochastic.
- [ ] **D: Cascaded verification** (~$0.50) — second-stage comparative
  verifier on candidates that pass first stage
- [ ] **E: High-recall text proposer** (~$3.50 via Batch API) —
  recall-biased proposer config targeting R>0.85

#### Design tasks

- [ ] **Draft proposer-specific prompt** — modify system instructions for
  high-recall mode: remove negative examples, add explicit "err on the side
  of inclusion" framing, consider removing or reducing example images
- [ ] **Draft text-only verifier for image-track candidates** — test whether
  text-only adversarial verification works as well on image-originated
  candidates as on text-originated ones
