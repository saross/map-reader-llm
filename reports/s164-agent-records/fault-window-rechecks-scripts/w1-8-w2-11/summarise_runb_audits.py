#!/usr/bin/env python3
"""
Summarise the re-run Run B cost audits against the figures the record quotes.

Fault-window re-check (2026-10-14), row W1-8. Run B's audited costs exist
only as figures in commit bodies (92b151058, 2b6edde9a, 2718be084,
60aceebdd, 987718a66) and in results/modality-bridge-2026-10-07/findings.md
§ 9; no audit record was committed. This reads the re-run audits
(audit_proposer_cost.py per Stage 1 arm, audit_verifier_cost.py over the ten
Stage 2 legs, both --tier batch, at 69eb32132) and compares each total, as
rounded in the record, with the quoted figure.

Usage: python summarise_runb_audits.py AUDIT_DIR OUT_JSON

Author: Claude (Opus 5.5) for Shawn Ross; Licence: Apache 2.0
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

#: Quoted Stage 1 figures (US$, two decimals): commit bodies and findings § 9.
STAGE1_QUOTED = {"g3-text": 8.39, "g3-image": 19.52, "g37-text": 8.64,
                 "g37-image": 18.93, "g37-image-cache": 12.33,
                 "g3-text-temp1": 4.26, "g3-image-temp1": 9.76}
#: Quoted Stage 2 per-leg figures for the four Gemini 3 legs (2b6edde9a body,
#: four decimals) and the ten-leg total (findings § 9, two decimals).
STAGE2_QUOTED = {"g3-text": 2.2302, "g3-image": 2.3829, "g3-text-temp1": 2.1786,
                 "g3-image-temp1": 2.1270}
QUOTED_TOTALS = {"stage1": 81.83, "stage2": 12.69, "all": 94.52}


def main() -> int:
    """Compare and write the summary."""
    audit, out = Path(sys.argv[1]), Path(sys.argv[2])
    rows, s1 = [], 0.0
    for arm, quoted in STAGE1_QUOTED.items():
        d = json.loads((audit / f"stage1-{arm}.json").read_text())
        s1 += d["audited_usd"]
        rows.append({"stage": 1, "arm": arm, "audited_usd": d["audited_usd"],
                     "quoted": quoted, "match_2dp": round(d["audited_usd"], 2) == quoted,
                     "n_fragments": len(d["fragments"]),
                     "fragments": [f["meta"] for f in d["fragments"]]})
    s2, legs = 0.0, json.loads((audit / "stage2.json").read_text())
    for st in legs:
        arm = st["stage"].split("/")[2]
        leg = st["stage"].split("/")[-1]
        s2 += st["audited_usd"]
        q = STAGE2_QUOTED.get(arm) if leg == "verify_g3" else None
        rows.append({"stage": 2, "arm": arm, "leg": leg, "audited_usd": st["audited_usd"],
                     "complete": st["complete"], "items": st["items_covered"],
                     "shortfall": st["shortfall"], "quoted": q,
                     "match_4dp": None if q is None else round(st["audited_usd"], 4) == q})
    totals = {"stage1": s1, "stage2": s2, "all": s1 + s2}
    res = {"rows": rows, "totals": totals,
           "totals_match_2dp": {k: round(v, 2) == QUOTED_TOTALS[k] for k, v in totals.items()},
           "quoted_totals": QUOTED_TOTALS}
    out.write_text(json.dumps(res, indent=1) + "\n")
    for r in rows:
        tag = r.get("leg", "")
        ok = r.get("match_2dp", r.get("match_4dp"))
        print(f"stage{r['stage']} {r['arm']:16s} {tag:10s} {r['audited_usd']:.6f} "
              f"quoted {r['quoted']} match {ok}")
    for k, v in totals.items():
        print(f"total {k}: {v:.6f} quoted {QUOTED_TOTALS[k]} "
              f"match {round(v, 2) == QUOTED_TOTALS[k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
