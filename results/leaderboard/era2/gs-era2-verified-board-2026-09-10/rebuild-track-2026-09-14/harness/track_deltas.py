#!/usr/bin/env python3
"""Record the Era-2 board's membership delta for ruling 4 of 2026-09-14.

`track` now derives from the transmitted configuration and a `track_basis`
sibling names the route. This writes the before-vs-after delta over the same
110 members and asserts that nothing else about a member moved.
"""
import collections
import json

B = "results/leaderboard/era2/gs-era2-verified-board-2026-09-10"
J = B + "/rebuild-track-2026-09-14"

a = json.load(open(J + "/membership-before.json"))
b = json.load(open(B + "/membership.json"))
ma = {m["condition_id"]: m for m in a["members"]}
mb = {m["condition_id"]: m for m in b["members"]}

track, other = [], []
for cid in sorted(mb):
    x, y = ma.get(cid), mb[cid]
    if x is None:
        continue
    for k in sorted(set(x) | set(y)):
        if x.get(k) != y.get(k):
            rec = {"condition_id": cid, "field": k,
                   "before": x.get(k), "after": y.get(k)}
            (track if k in ("track", "track_basis") else other).append(rec)

label = [r for r in track if r["field"] == "track"]
basis = collections.Counter(r["after"] for r in track if r["field"] == "track_basis")

doc = {
    "_README": (
        "Ruling 4 of the PI's four rulings of 2026-09-14: the Era-2 board rebuilt "
        "with the membership 'track' field DERIVED from the transmitted proposer "
        "configuration (scripts/derive_condition_modality.py) instead of a "
        "substring test on the condition label, and a new 'track_basis' sibling "
        "naming the derivation route. This is the membership delta, computed "
        "before vs after over the same 110 members; every other member field is "
        "asserted unchanged, and the tiering never reads 'track', so no rank, "
        "tier, tie set, Hsu set or metric can move. Erratum E88."),
    "board_id": b["board_id"],
    "n_members_before": len(ma),
    "n_members_after": len(mb),
    "member_ids_added": sorted(set(mb) - set(ma)),
    "member_ids_removed": sorted(set(ma) - set(mb)),
    "n_excluded_before": len(a.get("excluded") or []),
    "n_excluded_after": len(b.get("excluded") or []),
    "n_track_labels_changed": len(label),
    "track_labels_changed": label,
    "n_track_basis_added": sum(1 for r in track if r["field"] == "track_basis"),
    "track_basis_distribution": dict(basis),
    "n_other_member_field_changes": len(other),
    "other_member_field_changes": other,
    "passed": (len(other) == 0 and len(label) == 7
               and not (set(mb) ^ set(ma)) and len(mb) == 110),
}
open(J + "/track-deltas.json", "w").write(json.dumps(doc, indent=1) + "\n")
print("members:", len(ma), "->", len(mb))
print("excluded:", doc["n_excluded_before"], "->", doc["n_excluded_after"])
print("track labels changed:", len(label))
for r in label:
    print("   ", r["condition_id"], r["before"], "->", r["after"])
print("track_basis added:", doc["n_track_basis_added"], dict(basis))
print("other member field changes:", len(other))
print("passed:", doc["passed"])
