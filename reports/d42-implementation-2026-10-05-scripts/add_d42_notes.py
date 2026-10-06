"""Append the PI-approved D42 batch signature note to four signed analyses."""

import json
from pathlib import Path

PATH = Path("results/run-analyses.json")
APPROVED = "2026-10-05T11:34:51Z"
TEMPLATE = (
    "SIGNATURE NOTE 2026-10-05 (D9 pattern; re-testing; ruling D42, approved by the PI "
    f"{APPROVED}, Session 161). Every p-value in this analysis's artefact is now the paired "
    "tile-swap permutation test's (scripts/lib_permutation.py; 10,000 permutations, seed 42; "
    "for a 2 x 2 interaction, a per-tile swap of the two factor-level pairs), not the "
    "bootstrap's 2 x min-tail p, which D42 retired; the artefact was regenerated on sapphire "
    "(5986316b5). CHANGED: {changed}. UNCHANGED: every delta, CI, F1 and verdict at 0.05. "
    "The outcome text keeps its signed figures; the regenerated JSON carries these. The "
    "signature of {signed} stands; the PI approves the re-tested p-values as of this note. "
    "Walkthrough: reports/d42-implementation-2026-10-05.md."
)
CHANGED = {
    "e45-bootstrap-pairings": "H2 and H3, 0.001 / 0.0001 (bootstrap floors at B = 1,000 / 10,000) -> < 0.0001",
    "h13-overlap-2026-08-18": "A - B 0.0416 (B = 10,000) / 0.0500 (B = 1,000) -> 0.0385; A - C and B - C, "
    "0.0001 / 0.0010 (floors) -> < 0.0001",
    "grid-tilesize-overlap-2026-08-18": "overlap at 512 px, overlap at 384 px and tile size at 50 %, 0.0001 (floor) -> "
    "< 0.0001; tile size at 12.5 %, 0.0001 (floor) -> 0.0002; interaction 0.4902 -> 0.4681",
    "grid-postverifier-2026-08-18": "post-verifier tile size at 12.5 % / 50 %, 0.034 / 0.2308 -> 0.0373 / 0.2353; "
    "overlap at 512 / 384 px, 0.0004 / 0.0208 -> 0.0003 / 0.0235; interaction 0.2336 -> "
    "0.2257; K = 10 consensus baseline tile size at 12.5 % / 50 %, 0.2808 / 0.0886 -> "
    "0.2975 / 0.0939, overlap at 512 / 384 px, 0.0004 / 0.0026 -> 0.0008 / 0.0032",
}
data = json.loads(PATH.read_text(encoding="utf-8"))
for aid, changed in CHANGED.items():
    (row,) = [a for a in data["analyses"] if a["analysis_id"] == aid]
    sig = row["signature"]
    assert sig["status"] == "signed"
    assert "ruling D42" not in sig["attests"], f"{aid}: note already present"
    prior = sig["attests"]
    note = TEMPLATE.format(changed=changed, signed=sig["signed_at"])
    sig["attests"] = prior + "\n\n" + note
    sig.setdefault("history", []).append(
        {
            "noted_at": APPROVED,
            "kind": "signature note (D9 pattern): re-testing under D42 (permutation p-values)",
            "prior_attests": prior,
            "presentation": "Session 161 conversation; reports/d42-implementation-2026-10-05.md § 7",
        }
    )
    print(f"noted {aid} (signature of {sig['signed_at']})")
PATH.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
