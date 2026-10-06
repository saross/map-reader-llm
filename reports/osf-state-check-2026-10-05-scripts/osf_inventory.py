"""Read-only inventory of the OSF project h9x4g and registration tybgq.

GET requests only. The token is read from ~/personal-assistant/.env and never
printed. Output: a JSON dump of every node, registration, update (schema
response) and file (with size, dates and hashes), plus a short text summary.
"""

import json
import sys
from pathlib import Path

import requests

API = "https://api.osf.io/v2"
OUT = Path(sys.argv[1])


def token() -> str:
    for line in (Path.home() / "personal-assistant/.env").read_text().splitlines():
        if line.startswith("OSF_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("no OSF_API_KEY")


S = requests.Session()
S.headers["Authorization"] = f"Bearer {token()}"


def get(url: str) -> dict:
    r = S.get(url if url.startswith("http") else API + url, timeout=60)
    return {"status": r.status_code, "json": r.json() if r.content else None}


def get_all(url: str) -> list[dict]:
    """Follow pagination; return the data items (or an error marker)."""
    items, nxt = [], url if url.startswith("http") else API + url
    while nxt:
        r = S.get(nxt, timeout=60)
        if r.status_code != 200:
            return [{"_error": r.status_code, "_url": nxt, "_body": r.text[:300]}]
        j = r.json()
        items.extend(j.get("data", []))
        nxt = (j.get("links") or {}).get("next")
    return items


def walk_files(url: str, depth: int = 0) -> list[dict]:
    out = []
    for it in get_all(url):
        if "_error" in it:
            out.append(it)
            continue
        a = it["attributes"]
        rec = {
            k: a.get(k)
            for k in (
                "kind",
                "name",
                "materialized_path",
                "size",
                "date_created",
                "date_modified",
                "current_version",
            )
        }
        rec["hashes"] = (a.get("extra") or {}).get("hashes")
        rec["downloads"] = (a.get("extra") or {}).get("downloads")
        rec["id"] = it.get("id")
        rec["download"] = (it.get("links") or {}).get("download")
        out.append(rec)
        if a.get("kind") == "folder" and depth < 6:
            rel = it["relationships"]["files"]["links"]["related"]["href"]
            out.extend(walk_files(rel, depth + 1))
    return out


def storage(kind: str, gid: str) -> dict:
    res = {}
    for prov in get_all(f"/{kind}/{gid}/files/"):
        if "_error" in prov:
            res["_error"] = prov
            continue
        name = prov["attributes"]["name"]
        rel = prov["relationships"]["files"]["links"]["related"]["href"]
        res[name] = walk_files(rel)
    return res


def node_summary(kind: str, gid: str) -> dict:
    n = get(f"/{kind}/{gid}/")
    d = {"id": gid, "kind": kind, "http": n["status"]}
    if n["status"] != 200:
        d["body"] = n["json"]
        return d
    a = n["json"]["data"]["attributes"]
    keep = (
        "title",
        "category",
        "public",
        "date_created",
        "date_modified",
        "date_registered",
        "registration_supplement",
        "revision_state",
        "reviews_state",
        "pending_withdrawal",
        "withdrawn",
        "embargo_end_date",
        "description",
        "registration_responses",
    )
    d["attributes"] = {k: a.get(k) for k in keep if k in a}
    rels = n["json"]["data"].get("relationships", {})
    for r in ("registered_from", "root", "parent"):
        if r in rels:
            d[r] = ((rels[r].get("links") or {}).get("related") or {}).get("href")
    d["storage"] = storage(kind, gid)
    kids = get_all(f"/{kind}/{gid}/children/")
    d["children"] = [node_summary(kind, k["id"]) if "_error" not in k else k for k in kids]
    d["wikis"] = [
        {"name": w["attributes"].get("name"), "date_modified": w["attributes"].get("date_modified")}
        if "_error" not in w
        else w
        for w in get_all(f"/{kind}/{gid}/wikis/")
    ]
    return d


report = {}
report["project"] = node_summary("nodes", "h9x4g")
regs = get_all("/nodes/h9x4g/registrations/")
report["project_registrations"] = [
    {
        "id": r.get("id"),
        "title": r["attributes"].get("title"),
        "date_registered": r["attributes"].get("date_registered"),
        "registration_supplement": r["attributes"].get("registration_supplement"),
        "revision_state": r["attributes"].get("revision_state"),
    }
    if "_error" not in r
    else r
    for r in regs
]
report["registration"] = node_summary("registrations", "tybgq")
sr = get_all("/registrations/tybgq/schema_responses/")
report["updates"] = [
    {
        "id": s.get("id"),
        **{
            k: s["attributes"].get(k)
            for k in (
                "date_created",
                "date_modified",
                "date_submitted",
                "reviews_state",
                "revision_justification",
                "updated_response_keys",
                "is_original_response",
                "is_pending_current_user_approval",
            )
        },
    }
    if "_error" not in s
    else s
    for s in sr
]
OUT.write_text(json.dumps(report, indent=1, ensure_ascii=False))
print("written", OUT)
