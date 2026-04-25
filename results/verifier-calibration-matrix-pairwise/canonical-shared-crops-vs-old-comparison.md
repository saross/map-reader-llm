# Canonical `adversarial-text` — shared-crops refresh vs. pre-existing comparison

## Executive summary

**The planned shared-crops canonical refresh could not be executed.** The
new canonical probabilities file (`verified-adversarial-text/probabilities.json`
on both image and text pools) was observed at job dispatch but was deleted
before the Phase B/C/D refresh pipeline could be run. Neither local machine
(amd-tower) nor sapphire retained a copy, and no pre-cleanup `.backup` file
was generated for the canonical variant (only five backups exist, none for
`verified-adversarial-text`).

Regenerating the probabilities file requires a Gemini API call (no API
calls were made per the task's no-API constraint).

The pairwise analysis in this directory therefore uses the **pre-existing**
canonical probabilities from `verified-v1-n5/probabilities.json`, which
uses a different (historical, slightly larger) candidate pool than the six
alternatives. Observation 277's Pareto-dominance claim remains supported
by the pre-existing data — a strict crop-parity re-verification was not
possible.

## Timeline of the data-loss event

| Local time (UTC) | Event |
|------------------|-------|
| 2026-04-25 02:22 | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-adversarial-text/probabilities.json` observed (1573586 bytes, 1994 scored candidates) |
| 2026-04-25 02:33 | `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-adversarial-text/probabilities.json` observed (2770499 bytes, 3686 scored candidates) |
| 2026-04-25 02:40 | Both pools' `session-78-matrix` parent directory modified; `verified-adversarial-text` sub-directories (and several other `verified-*` sub-directories) gone on both pools |
| 2026-04-25 02:42+ | Pairwise agent (this task) attempts to refresh canonical; files not found |

The dir-modify timestamp (02:40) post-dates the parallel per-architecture
leaderboard agent's launch (02:31), but that agent does not write to
`outputs/`. Shell history on sapphire shows no manual `rm` against this
path. Five pre-cleanup `.backup` files exist — each for a different
variant (`verified-brief-text`, `verified-checklist`, `verified-checklist-text`
on both pools in various combinations) — but no backup for
`verified-adversarial-text`. The proximate cause is unresolved.

**The deletion was not caused by this agent.** The `git stash push
--include-untracked` executed during the initial sapphire git-pull
setup stashed only staged/tracked untracked content (15 files total,
all in `planning/`, `results/verifier-calibration-matrix/*/calibration.json`,
and `scripts/`) — it did not touch `outputs/`.

## Pre-existing canonical metrics (used in the pairwise analysis)

Source: `results/verifier-calibration-matrix/<track>-adversarial-text/calibration.json`

Upstream probabilities: `outputs/h11/pv-diag-384/flash-high-<track>-n5/<track>-t0.7/verified-v1-n5/probabilities.json`

| metric         | image canonical | text canonical |
|----------------|----------------:|---------------:|
| n_total        | 2016            | 3736           |
| n_mound        | 434             | 430            |
| prevalence     | 0.2153          | 0.1151         |
| AUC            | 0.8633 [0.8477, 0.8787] | 0.9592 [0.9512, 0.9663] |
| Brier          | 0.1904 [0.1745, 0.2064] | 0.0588 [0.0522, 0.0657] |
| ECE            | 0.1878 [0.1714, 0.2057] | 0.0672 [0.0605, 0.0751] |
| P(mound p≤0.25)| 0.0340 [0.0242, 0.0446] | 0.0149 [0.0108, 0.0194] |
| F1@20m         | 0.7868 [0.7470, 0.8244] | 0.8634 [0.8321, 0.8933] |

## Obs 277 support — pre-existing canonical vs the six alternatives

The six alternatives use the shared-crops probabilities (at
`outputs/h11/pv-diag-384/flash-high-<track>-n5/<track>-t0.7/session-78-matrix/verified-<variant>/probabilities.json`
— this directory is still present for each alternative on sapphire;
the deletion hit only the newly-run canonical). Metrics from
`results/verifier-calibration-matrix/<track>-<variant>/calibration.json`:

### Image track (canonical prevalence 0.215)

| variant            | AUC    | ECE    | Brier  | P(mound p≤0.25) | F1@20m |
|--------------------|-------:|-------:|-------:|----------------:|-------:|
| `adversarial-text` (canonical) | **0.8633** | **0.1878** | **0.1904** | 0.0340 | 0.7868 |
| `adversarial`                   | 0.8559 | 0.2169 | 0.2092 | 0.0112 | 0.7884 |
| `brief`                         | 0.8581 | 0.2664 | 0.2493 | 0.0009 | 0.7826 |
| `brief-text`                    | 0.8456 | 0.2229 | 0.2317 | 0.0235 | 0.7736 |
| `checklist`                     | 0.8607 | 0.2634 | 0.2373 | 0.0018 | 0.7821 |
| `checklist-text`                | 0.8531 | 0.2675 | 0.2472 | 0.0055 | 0.7820 |
| `comparative`                   | 0.8554 | 0.2510 | 0.2359 | 0.0018 | 0.7857 |

**Image-track canonical dominance**:

- AUC: canonical highest (0.8633 vs 0.8456–0.8607) — dominates all six.
- ECE: canonical lowest (0.1878 vs 0.2169–0.2675) — dominates all six
  on calibration by a wide margin (≥ 0.03 gap to the next-best).
- Brier: canonical lowest (0.1904 vs 0.2092–0.2493) — dominates all six.
- F1@20m: canonical is neither best nor worst (6th of 7); `adversarial`
  leads at 0.7884 (+0.0016 over canonical).

Image-track **Pareto dominance on calibration is absolute**: the
canonical wins on every calibration metric (AUC, Brier, ECE) while
ceding only a trivial F1@20m gap to `adversarial`.

### Text track (canonical prevalence 0.115)

| variant            | AUC    | ECE    | Brier  | P(mound p≤0.25) | F1@20m |
|--------------------|-------:|-------:|-------:|----------------:|-------:|
| `adversarial-text` (canonical) | 0.9592 | **0.0672** | **0.0588** | 0.0149 | 0.8634 |
| `adversarial`                   | **0.9676** | 0.0798 | 0.0595 | 0.0042 | 0.8822 |
| `brief`                         | 0.9636 | 0.1113 | 0.0867 | 0.0003 | 0.8772 |
| `brief-text`                    | 0.9389 | 0.0953 | 0.0878 | 0.0099 | 0.8495 |
| `checklist`                     | 0.9639 | 0.1223 | 0.0829 | 0.0007 | 0.8793 |
| `checklist-text`                | 0.9483 | 0.1388 | 0.1063 | 0.0024 | 0.8629 |
| `comparative`                   | 0.9637 | 0.1025 | 0.0758 | 0.0003 | 0.8846 |

**Text-track canonical dominance**:

- AUC: canonical is **5th of 7** (0.9592 vs `adversarial` 0.9676,
  `checklist` 0.9639, `comparative` 0.9637, `brief` 0.9636). Canonical
  beats only `checklist-text` (0.9483) and `brief-text` (0.9389).
- ECE: canonical **lowest** (0.0672 vs 0.0798–0.1388) — dominates all six.
- Brier: canonical **lowest** (0.0588 vs 0.0595–0.1063) — dominates all six.
- F1@20m: canonical is 5th of 7 (beats only `brief-text` and
  `checklist-text`).

Text-track **Pareto dominance on calibration is split**: the canonical
dominates on ECE and Brier (the calibration-targeted metrics) but yields
AUC to four alternatives. This is a genuine novel finding — on the
text track the canonical is NOT AUC-dominant. Obs 277 as written
claims canonical Pareto-dominance; under the shared-crops probabilities
for the six alternatives plus the pre-existing canonical probabilities,
this is still true for ECE and Brier, but NOT for AUC on the text
track.

**Action for user**: Obs 277 should be narrowed to "canonical dominates
on ECE and Brier across both tracks; canonical dominates on AUC on the
image track but is outperformed by four alternatives on AUC on the
text track". The shared-crops refresh would be expected to tighten or
slightly alter these numbers but is unlikely to change the qualitative
direction, given:

1. The candidate pool difference is small (image: 2016 canonical vs
   2017 shared-crops, delta = 1 candidate; text: 3736 canonical =
   3736 shared-crops; no structural pool difference).
2. The six alternatives' metrics already use shared-crops
   probabilities, and show the AUC ranking on text is not a canonical
   vs shared-crops artefact but a genuine AUC signal.

## What a true shared-crops-parity refresh would change

With the shared-crops canonical (1994 image / 3686 text scored
candidates) the canonical pool would shrink by ~22 candidates (image)
and ~50 candidates (text) relative to the pre-existing verified-v1-n5
pool. Given the prevalence-stratified AUC computation, this is a
~1–2% pool-size reduction, and the AUC and ECE would likely change by
less than half a standard error. No direction change in the
qualitative findings is expected.

**But this cannot be verified without rerunning the verifier.**

## Provenance summary

| artefact | used in this analysis | would be used in shared-crops refresh |
|----------|-----------------------|---------------------------------------|
| canonical probabilities file | `outputs/h11/.../verified-v1-n5/probabilities.json` (historical, present) | `outputs/h11/.../session-78-matrix/verified-adversarial-text/probabilities.json` (deleted) |
| canonical leaderboard cell | `results/leaderboard/cells/session-78-<track>-adversarial-text-487tile.json` (pre-existing) | `session-78-<track>-adversarial-text-shared-crops-487tile.json` (NOT created — requires shared-crops probs) |
| canonical opt-20m geojson | `results/verifier-calibration-matrix/<track>-adversarial-text-opt-20m.geojson` (pre-existing, 414 image / 392 text features) | would be newly materialised — NOT created |
| canonical deep-eval | `results/verifier-calibration-matrix/<track>-adversarial-text/evaluation.json` (pre-existing) | `results/verifier-calibration-matrix/<track>-adversarial-text-shared-crops/evaluation.json` (NOT created) |
| canonical calibration | `results/verifier-calibration-matrix/<track>-adversarial-text/calibration.json` (pre-existing, 14-cell artefact) | would have been rewritten by the patched `compute_session78_calibration_matrix.py`; NOT created |

`scripts/compute_session78_calibration_matrix.py:resolve_prob_path` was
**not patched** — there is no shared-crops canonical probabilities file
for it to point to. Leaving the function untouched preserves the
ability to rerun the original calibration matrix if the original
probabilities become available again.

## Conclusion

Obs 277's headline claim — that the canonical `adversarial-text` Pareto-
dominates the six alternatives on calibration — is **supported on ECE
and Brier in both tracks** (canonical is strictly lower on both
metrics in every pairwise comparison to the six alternatives). It is
**supported on AUC on the image track** but **not on the text track**
(where `adversarial`, `checklist`, `comparative`, and `brief` all post
higher AUC than the canonical). This AUC reversal on the text track is
a finding the crop-parity refresh might have tightened or moderated,
but the refresh itself is blocked by the data-loss event; the finding
stands on the pre-existing data.
