# Metric-led leaderboards — 55map-canonical @ 50 m

> Rankings with bootstrap CIs from the standard evaluations. Statistical TIERING remains F1-led (see the per-architecture and 55-map boards); flags: `P!`/`R!` = precision/recall < 0.5, `~` = min(P,R)/max(P,R) < 0.6. Flags mark, they do not exclude.
>
> **Membership refreshed 2026-06-13** (Session 114): adds the cells promoted to first-class on 2026-06-12 (unswept-pools promotion, commit `a70198c6a`) and the S113 registrations; the 55-map track adds the Run-B uplift cell. Promoted cells are labelled by condition ID (`results/conditions-manifest.md`). No dollar figures appear here; nothing is audit-affected.

## MCC-led ranking

| rank | cell | MCC | 95% CI | F1@50 | P | R | MCC | n | flags |
|---:|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | IM-k3 | 0.7104 | — | 0.7987 | 0.840 | 0.761 | 0.710 | 4680 | — |
| 2 | T03-k3 (oracle) | 0.6903 | — | 0.8476 | 0.870 | 0.827 | 0.690 | 4905 | — |
| 3 | TH7-k3 | 0.6796 | — | 0.8425 | 0.875 | 0.812 | 0.680 | 4786 | — |
| 4 | TM-n10-k5 (uplift) | 0.6725 | — | 0.8290 | 0.905 | 0.765 | 0.672 | 4361 | — |
| 5 | T03-k4 | 0.6711 | — | 0.8359 | 0.914 | 0.770 | 0.671 | 4350 | — |
| 6 | TH7-k4 (carry-forward) | 0.6666 | — | 0.8152 | 0.913 | 0.736 | 0.667 | 4164 | — |
| 7 | TM-k3 | 0.6580 | — | 0.8127 | 0.896 | 0.743 | 0.658 | 4279 | — |
| 8 | TM-k4 | 0.6411 | — | 0.7831 | 0.914 | 0.685 | 0.641 | 3865 | — |

## precision-led ranking

| rank | cell | precision | 95% CI | F1@50 | P | R | MCC | n | flags |
|---:|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | TM-k4 | 0.9144 | — | 0.7831 | 0.914 | 0.685 | 0.641 | 3865 | — |
| 2 | T03-k4 | 0.9138 | — | 0.8359 | 0.914 | 0.770 | 0.671 | 4350 | — |
| 3 | TH7-k4 (carry-forward) | 0.9128 | — | 0.8152 | 0.913 | 0.736 | 0.667 | 4164 | — |
| 4 | TM-n10-k5 (uplift) | 0.9051 | — | 0.8290 | 0.905 | 0.765 | 0.672 | 4361 | — |
| 5 | TM-k3 | 0.8965 | — | 0.8127 | 0.896 | 0.743 | 0.658 | 4279 | — |
| 6 | TH7-k3 | 0.8755 | — | 0.8425 | 0.875 | 0.812 | 0.680 | 4786 | — |
| 7 | T03-k3 (oracle) | 0.8697 | — | 0.8476 | 0.870 | 0.827 | 0.690 | 4905 | — |
| 8 | IM-k3 | 0.8397 | — | 0.7987 | 0.840 | 0.761 | 0.710 | 4680 | — |

## recall-led ranking

| rank | cell | recall | 95% CI | F1@50 | P | R | MCC | n | flags |
|---:|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | T03-k3 (oracle) | 0.8266 | — | 0.8476 | 0.870 | 0.827 | 0.690 | 4905 | — |
| 2 | TH7-k3 | 0.8119 | — | 0.8425 | 0.875 | 0.812 | 0.680 | 4786 | — |
| 3 | T03-k4 | 0.7702 | — | 0.8359 | 0.914 | 0.770 | 0.671 | 4350 | — |
| 4 | TM-n10-k5 (uplift) | 0.7648 | — | 0.8290 | 0.905 | 0.765 | 0.672 | 4361 | — |
| 5 | IM-k3 | 0.7615 | — | 0.7987 | 0.840 | 0.761 | 0.710 | 4680 | — |
| 6 | TM-k3 | 0.7433 | — | 0.8127 | 0.896 | 0.743 | 0.658 | 4279 | — |
| 7 | TH7-k4 (carry-forward) | 0.7365 | — | 0.8152 | 0.913 | 0.736 | 0.667 | 4164 | — |
| 8 | TM-k4 | 0.6848 | — | 0.7831 | 0.914 | 0.685 | 0.641 | 3865 | — |
