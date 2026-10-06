"""Append the PI-approved X1 signature note (D33) to the r2 board's signature."""

import json
from pathlib import Path

PATH = Path("results/run-analyses.json")
AID = "55map-final-board-r2-2026-09-06"
APPROVED = "2026-10-05T06:06:19Z"
NOTE = (
    "SIGNATURE NOTE 2026-10-05 (D9 pattern; re-pricing; ruling D33, approved by the PI "
    f"{APPROVED}, Session 161). The TH7, T03 and TM ORACLE cells (k3) now add the vote-3 "
    "increment their operating point drew on (results/deployment-oracle-2026-06-06/vote3-verify/; "
    "register rows <run>::vote3-increment::run1 since the S160 register repair), at the uniform "
    "tier: TH7-oracle US$207.35 -> 210.32, T03-oracle US$261.15 -> 263.89, TM-oracle "
    "US$30.40 -> 31.91 (TM's verifier leg stays completed from comparables, †). The board's "
    "sentence defining cost now says so. The other two oracle cells carry no increment: IM's "
    "carried and oracle cells are one shipped k3 cell and no image vote-3 increment was run; "
    "UPL's oracle is priced by its own verifier leg. UNCHANGED: the carried cells (k4), which "
    "never used the increment; every other family's cost (the repair moved none); the 35-cell "
    "tiering, every F1, MCC, tier and group; and both efficiency frontiers' membership (D24). "
    "The signature of 2026-09-17 stands for the tiering; the PI approves the re-priced cost "
    "axis as of this note."
)

raw = PATH.read_text(encoding="utf-8")
data = json.loads(raw)
(row,) = [a for a in data["analyses"] if a["analysis_id"] == AID]
sig = row["signature"]
assert "SIGNATURE NOTE 2026-10-05" not in sig["attests"], "note already present"
prior = sig["attests"]
sig["attests"] = prior + "\n\n" + NOTE
sig["history"].append(
    {
        "noted_at": APPROVED,
        "kind": "signature note (D9 pattern): re-pricing under D33 (the oracle cells' vote-3 increments)",
        "prior_attests": prior,
        "presentation": "Session 161 conversation; planning/text-track-transmission-2026-10-05.md § 5",
    }
)
out = json.dumps(data, indent=1, ensure_ascii=False) + "\n"
PATH.write_text(out, encoding="utf-8")
print("written")
