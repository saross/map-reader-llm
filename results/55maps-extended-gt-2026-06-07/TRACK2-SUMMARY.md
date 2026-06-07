# 55-map canonical extended-GT re-score (Track 2) — headline @ 50 m

**Validation gate**: ✅ PASS (corrected-F1 @ 50 m vs findings §4b, 4 d.p.)

| cell | config | k | role | F1@50m | MCC@50m |
|---|---|---:|---|---:|---:|
| TH7-k4 | text-high-T0.7 | 4 | carry-forward | 0.8152 | 0.6666 |
| TH7-k3 | text-high-T0.7 | 3 | threshold (new) | 0.8425 | 0.6796 |
| T03-k4 | text-high-T0.3 | 4 | config | 0.8359 | 0.6711 |
| T03-k3 | text-high-T0.3 | 3 | ORACLE | 0.8476 | 0.6903 |
| TM-k4 | text-min | 4 | config | 0.7831 | 0.6411 |
| TM-k3 | text-min | 3 | threshold (new) | 0.8127 | 0.6580 |
| IM-k3 | image | 3 | config (carried) | 0.7987 | 0.7104 |

## Validation gate detail

| cell | kind | target | got | Δ | verdict |
|---|---|---:|---:|---:|---|
| TH7-k4 | GATE | 0.815228 | 0.815228 | +1.18e-07 | PASS |
| TH7-k3 | sanity (per-run §1) | 0.850000 | 0.842465 | -7.53e-03 | info |
| T03-k4 | GATE | 0.835874 | 0.835874 | +2.51e-07 | PASS |
| T03-k3 | GATE | 0.847606 | 0.847606 | +1.98e-07 | PASS |
| TM-k4 | GATE | 0.783071 | 0.783071 | +1.28e-07 | PASS |
| TM-k3 | sanity (per-run §1) | 0.822000 | 0.812712 | -9.29e-03 | info |
| IM-k3 | GATE | 0.798699 | 0.798699 | +3.19e-07 | PASS |
