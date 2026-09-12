# Tile-join audit

Every cell re-scored under all three tile joins; nothing rewritten.
`id` is the legacy string join, whose reproduction of the committed confusion is the refactor's regression test. The two geometric columns are what the same cell would score under each geometric rule — they differ from `id`, and from each other, because the evaluation frames overlap.

| verdict | count |
|---|---:|
| EXACT | 43 |
| REFUSED | 3 |

| cell | n det | committed MCC | id MCC | verdict | geometric-primary MCC | geometric-contains MCC |
|---|---:|---:|---:|---|---:|---:|
| g37-text-k1-verified-carried-p0.10-k1 | 558 | 0.1422 | REFUSED | REFUSED | 0.9059 | 0.8761 |
| g37-text-k1-verified-opmax | 502 | 0.1337 | REFUSED | REFUSED | 0.9535 | 0.9262 |
| g37-text-k3-verified-opmax | 494 | 0.1337 | REFUSED | REFUSED | 0.9121 | 0.8903 |
| pv-high-image-t0.3-n1-opmax | 469 | 0.8270 | 0.8270 | EXACT | 0.8956 | 0.8667 |
| pv-high-image-t0.3-n3-carried-p0.15-k3 | 342 | 0.7788 | 0.7788 | EXACT | 0.8816 | 0.8766 |
| pv-high-image-t0.3-n3-opmax | 441 | 0.8237 | 0.8237 | EXACT | 0.9161 | 0.8755 |
| pv-high-image-t0.7-n1-opmax | 474 | 0.8435 | 0.8435 | EXACT | 0.9170 | 0.8755 |
| pv-high-image-t0.7-n3-carried-p0.15-k3 | 303 | 0.7621 | 0.7621 | EXACT | 0.8467 | 0.8467 |
| pv-high-image-t0.7-n3-opmax | 426 | 0.8435 | 0.8435 | EXACT | 0.9320 | 0.8929 |
| pv-high-image-t1.0-n1-carried-p0.15-k1 | 503 | 0.8601 | 0.8601 | EXACT | 0.9136 | 0.8776 |
| pv-high-image-t1.0-n1-opmax | 490 | 0.8640 | 0.8640 | EXACT | 0.9121 | 0.8875 |
| pv-high-image-t1.0-n3-carried-p0.15-k3 | 281 | 0.7389 | 0.7389 | EXACT | 0.8219 | 0.8146 |
| pv-high-image-t1.0-n3-opmax | 418 | 0.8294 | 0.8294 | EXACT | 0.9021 | 0.8806 |
| pv-high-text-t0.3-n1-carried-p0.15-k1 | 454 | 0.8022 | 0.8022 | EXACT | 0.9086 | 0.8508 |
| pv-high-text-t0.3-n1-opmax | 443 | 0.8068 | 0.8068 | EXACT | 0.9121 | 0.8541 |
| pv-high-text-t0.3-n3-opmax | 387 | 0.8053 | 0.8053 | EXACT | 0.9154 | 0.9056 |
| pv-high-text-t0.7-n1-opmax | 464 | 0.7737 | 0.7737 | EXACT | 0.8748 | 0.8426 |
| pv-high-text-t0.7-n3-carried-p0.15-k3 | 369 | 0.7762 | 0.7762 | EXACT | 0.8939 | 0.8806 |
| pv-high-text-t0.7-n3-opmax | 427 | 0.7979 | 0.7979 | EXACT | 0.9237 | 0.9057 |
| pv-high-text-t1.0-n1-carried-p0.15-k1 | 469 | 0.8071 | 0.8071 | EXACT | 0.9036 | 0.8628 |
| pv-high-text-t1.0-n1-opmax | 451 | 0.8162 | 0.8162 | EXACT | 0.9073 | 0.8817 |
| pv-high-text-t1.0-n3-carried-p0.15-k3 | 346 | 0.7443 | 0.7443 | EXACT | 0.8627 | 0.8455 |
| pv-high-text-t1.0-n3-opmax | 422 | 0.7986 | 0.7986 | EXACT | 0.9405 | 0.8893 |
| pv-min-image-t0.3-n1-carried-p0.15-k1 | 456 | 0.8475 | 0.8475 | EXACT | 0.9215 | 0.8964 |
| pv-min-image-t0.3-n1-opmax | 440 | 0.8443 | 0.8443 | EXACT | 0.9283 | 0.8939 |
| pv-min-image-t0.3-n3-opmax | 396 | 0.8178 | 0.8178 | EXACT | 0.9022 | 0.8850 |
| pv-min-image-t0.7-n1-opmax | 453 | 0.8437 | 0.8437 | EXACT | 0.9245 | 0.8908 |
| pv-min-image-t0.7-n3-carried-p0.15-k3 | 344 | 0.7994 | 0.7994 | EXACT | 0.9154 | 0.8851 |
| pv-min-image-t0.7-n3-opmax | 423 | 0.8377 | 0.8377 | EXACT | 0.9363 | 0.8935 |
| pv-min-image-t1.0-n1-opmax | 465 | 0.8360 | 0.8360 | EXACT | 0.9198 | 0.8739 |
| pv-min-image-t1.0-n3-carried-p0.15-k3 | 329 | 0.7629 | 0.7629 | EXACT | 0.8769 | 0.8393 |
| pv-min-image-t1.0-n3-opmax | 424 | 0.8178 | 0.8178 | EXACT | 0.9067 | 0.8686 |
| pv-min-text-t0.3-n1-opmax | 409 | 0.7986 | 0.7986 | EXACT | 0.9192 | 0.8728 |
| pv-min-text-t0.3-n3-carried-p0.15-k3 | 364 | 0.7556 | 0.7556 | EXACT | 0.8727 | 0.8392 |
| pv-min-text-t0.3-n3-opmax | 401 | 0.8040 | 0.8040 | EXACT | 0.9192 | 0.8853 |
| pv-min-text-t0.7-n1-opmax | 414 | 0.7881 | 0.7881 | EXACT | 0.9064 | 0.8477 |
| pv-min-text-t0.7-n3-carried-p0.15-k3 | 360 | 0.7665 | 0.7665 | EXACT | 0.8899 | 0.8560 |
| pv-min-text-t0.7-n3-opmax | 404 | 0.7910 | 0.7910 | EXACT | 0.9149 | 0.8681 |
| pv-min-text-t1.0-n1-carried-p0.15-k1 | 423 | 0.7961 | 0.7961 | EXACT | 0.8941 | 0.8778 |
| pv-min-text-t1.0-n1-opmax | 415 | 0.8095 | 0.8095 | EXACT | 0.9065 | 0.8896 |
| pv-min-text-t1.0-n3-carried-p0.15-k3 | 338 | 0.7413 | 0.7413 | EXACT | 0.8569 | 0.8317 |
| pv-min-text-t1.0-n3-opmax | 400 | 0.8040 | 0.8040 | EXACT | 0.9234 | 0.8850 |
| pv-scale4-optimal-n1-carried-p0.15-k1 | 491 | 0.8599 | 0.8599 | EXACT | 0.9161 | 0.8908 |
| pv-scale4-optimal-n1-opmax | 484 | 0.8726 | 0.8726 | EXACT | 0.9283 | 0.9064 |
| pv-scale4-optimal-n3-carried-p0.15-k3 | 283 | 0.7354 | 0.7354 | EXACT | 0.8030 | 0.8352 |
| pv-scale4-optimal-n3-opmax | 412 | 0.8443 | 0.8443 | EXACT | 0.9235 | 0.8928 |
