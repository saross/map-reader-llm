# 55-map generalisation leaderboard — canonical GT @ 50 m

> Working buffer 50 m per the noise-floor derivation (`results/working-precision/55maps-csr-noise-floor.json`). Round-robin tile-swap permutation (10k, seed 42) + BH-FDR q=0.05 + greedy-clique tiers; 24/28 pairs significant.

| rank | cell | tier | F1@50 | 95% CI | P@50 | R@50 | tile-MCC | n |
|---:|---|---:|---:|---|---:|---:|---:|---:|
| 1 | T03-k3 (oracle) | 1 | 0.8476 | [0.8388, 0.8559] | 0.8697 | 0.8266 | 0.690 | 4905 |
| 2 | TH7-k3 | 1 | 0.8425 | [0.8335, 0.8512] | 0.8755 | 0.8119 | 0.680 | 4786 |
| 3 | T03-k4 | 2 | 0.8359 | [0.8265, 0.8447] | 0.9138 | 0.7702 | 0.671 | 4350 |
| 4 | TM-n10-k5 (uplift) | 2 | 0.8290 | [0.8190, 0.8385] | 0.9051 | 0.7648 | 0.672 | 4361 |
| 5 | TH7-k4 (carry-forward) | 3 | 0.8152 | [0.8051, 0.8251] | 0.9128 | 0.7365 | 0.667 | 4164 |
| 6 | TM-k3 | 3 | 0.8127 | [0.8025, 0.8227] | 0.8965 | 0.7433 | 0.658 | 4279 |
| 7 | IM-k3 | 4 | 0.7987 | [0.7887, 0.8081] | 0.8397 | 0.7615 | 0.710 | 4680 |
| 8 | TM-k4 | 5 | 0.7831 | [0.7719, 0.7940] | 0.9144 | 0.6848 | 0.641 | 3865 |
