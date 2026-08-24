# H2-C (fine-to-coarse) full-run proposal — decision card

> **Last revised**: 2026-08-24 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Decision owner**: Shawn (PI). **Prepared by**: Claude, S142, per the
2026-08-24 decision-walk commission ("full-run proposal card QUEUED as
a decision").

**The decision**: execute H2's registered Condition C (fine-to-coarse
context expansion) as a late discharge, or leave it not-executed under
the standing E59 full disclosure. Money is not the constraint — the
whole run costs under a dollar — so the decision turns on registered
fidelity, confirmation value, and whether upgrading the scope of H2's
conclusions is worth a small implementation-and-caveat burden.

## 1. What the registration commits to

`docs/methodology/preregistration/osf/preregistration.md:478-484`:

- **Stage 1**: standard detection on 512 × 512 tiles with 5-pass
  voting, at the optimal single-stage configuration.
- **Uncertain candidates**: detections with **2/5 or 3/5 agreement**.
- **Stage 2**: for each uncertain candidate, extract a larger tile
  (~1024 × 1024) centred on it and re-query with a verification
  prompt.
- **Test** (`:486-489`): one-tailed, H0: two-stage ≥ single-stage;
  the registered prediction is that two-stage will *not* improve.
- **The registration's own caveat** (`:484`): *"Calibration testing
  found 1024px tiles achieve only 37% recall at 2/5 threshold,
  limiting confirmation value. The fine-to-coarse test remains valid
  for confirming the prediction that two-stage will not help, but
  practitioners should note this constraint."*

Status quo: the register row `h2-condition-c-fine-to-coarse` is
**not-executed** with E59 full disclosure — no `expand_*` config or
system instruction was ever created (the registered mapping at
`osf/preregistration.md:2015` names them), and every H2 conclusion is
currently scoped to coarse-to-fine, never "two-stage architectures"
generally (`results/analyses-manifest.json`, that row's outcome).

## 2. What the S141 probe settled — pricing

Ten K = 10-pool candidates across nine tiles, 1024 px crops, standard
adversarial text verifier
(`outputs/h2c-probe-2026-08-24/verify/run.meta.json`, committed
`3ab1c891f`-rebased): **$0.01367 list for 10 calls** = $1.367/1k list
= **$0.684/1k candidates at flex billing**. A 1024 px context crop
prices the same per call as standard verification — the larger crop
does not inflate the token load materially (17,920 input tokens for
ten calls).

## 3. What the registered definition counts — the missing number

Applying the registered uncertain-candidate rule (votes 2 or 3 in the
5-pass union) to the study's 512 px, 340-tile, 5-pass sub-pools (the
preregistered first-5 rule;
`outputs/retest/phase3a/<track>/<T>/consensus-n5/consensus_t1.geojson`,
counted S142):

| Cell (512 px, N = 5) | Union clusters | Votes 2 | Votes 3 | **Uncertain (2–3)** | Stage-2 flex $ |
|---|---:|---:|---:|---:|---:|
| text T = 0.3 (track-2 optimum) | 1,084 | 93 | 58 | **151** | $0.10 |
| text T = 0.7 | 1,333 | 152 | 89 | 241 | $0.16 |
| text T = 1.0 | 1,555 | 189 | 126 | 315 | $0.22 |
| image T = 0.3 | 1,024 | 123 | 84 | 207 | $0.14 |
| image T = 0.7 (track-1 optimum) | 1,314 | 172 | 127 | **299** | $0.20 |
| image T = 1.0 | 1,569 | 260 | 146 | 406 | $0.28 |

**Aggregate cost, stated per the implementation-review rule**: the
faithful two-cell run (each track at its consensus-optimal
temperature) is **450 calls ≈ $0.31 flex**, minutes of wall-clock at
modest concurrency; all six cells would be 1,619 calls ≈ $1.11 flex.
Scoring is $0 on existing machinery (threshold → combine → evaluate,
same chain as every verified condition).

## 4. What would need to be built

1. **The `expand_*` config and system instruction** — never created.
   Two options, and this is the real decision inside the decision:
   - **(a) Faithful**: author `expand_*` per the registered naming
     (`osf:2015`), a context-expansion verification prompt distinct
     from the adversarial crop verifier; pre-run `/audit-config`; the
     run then discharges the registered procedure as written.
   - **(b) Disclosed approximation**: reuse the standard adversarial
     text verifier at 1024 px (exactly what the probe did). Cheaper to
     stand up, but the register row must then say the registered
     prompt was substituted — an E59-class partial discharge, which
     rather defeats the purpose of running at all.
2. **Combination rule** (one sentence in the analysis spec): retained
   set = votes ≥ 4 clusters + accepted uncertain candidates; compare
   against Condition A (the same pool at its optimal plain vote
   threshold) with the registered one-tailed test.
3. **Caveats to carry**: E75-class out-of-sequence execution (the
   study's other phases are long closed) and E66-class
   pipeline-vintage asymmetry — same disclosures the H13 late
   discharge carries.

## 5. The case each way

**For running**: it completes the last third of H2's registered test,
letting every H2 conclusion be re-scoped from "coarse-to-fine" to
"two-stage architectures" (the register row and M.4/M.11 phrasing all
inherit the upgrade); it converts a not-executed row into an executed
one at trivial cost; and the H2 family story becomes fully symmetric —
the registered prediction ("neither architecture improves") is already
falsified by Condition B (+0.076, `family-bh-fdr-confirmatory`), so C
settles whether the falsification is architecture-specific.

**Against running**: the registration itself flags the 37 %-recall
pilot ceiling as "limiting confirmation value" — the PI weighed
exactly this class of argument when closing H6 disclose-only (E74);
E59's disclosure is already complete and defensible; the result cannot
rescue the registered prediction (dead via B) and a null here adds
little the pilot note has not already conceded; and the faithful path
requires authoring a new registered-named config for a test the
registration half-disowned.

## 6. Recommendation

**Run it — option (a), the faithful two-cell run — if and only if the
scope upgrade to "two-stage architectures generally" is wanted for the
paper's H2 claims; otherwise leave E59 standing.** The spend
(~$0.31 flex + ~$0.01 already spent on the probe) is noise; the real
costs are authoring `expand_*` faithfully (modest, auditable) and
carrying two more late-discharge caveats. If the Discussion will not
lean on the generality of the two-stage claim, the H6 precedent
(disclose-only, E74) applies cleanly here and nothing is lost.

Per the API gate: nothing runs without explicit approval of the model
(gemini-3-flash-preview), mode (real-time flex), call count (450 for
the two-cell run), and cost (~$0.31 flex expected, ~$0.62 list on the
metas).

## Changelog

### 2026-08-24 — Original publication

S142, per the 2026-08-24 decision-walk commission. Pricing from the
S141 probe metas; uncertain-candidate counts computed this session
from the committed phase-3a N = 5 union files; no API spend.
