"""Read-only: OSF logs for h9x4g and tybgq, schema-response file attachments."""

import json
import sys
from pathlib import Path
import requests

API = "https://api.osf.io/v2"
tok = [
    ln.split("=", 1)[1].strip().strip('"').strip("'")
    for ln in (Path.home() / "personal-assistant/.env").read_text().splitlines()
    if ln.startswith("OSF_API_KEY=")
][0]
S = requests.Session()
S.headers["Authorization"] = f"Bearer {tok}"


def get_all(url):
    items, nxt = [], API + url
    while nxt:
        r = S.get(nxt, timeout=60)
        if r.status_code != 200:
            return [{"_error": r.status_code, "_body": r.text[:300]}]
        j = r.json()
        items.extend(j.get("data", []))
        nxt = (j.get("links") or {}).get("next")
    return items


out = {}
for kind, gid in (("nodes", "h9x4g"), ("registrations", "tybgq")):
    logs = get_all(f"/{kind}/{gid}/logs/?page[size]=100")
    out[f"{gid}_logs"] = [
        {
            "date": ln["attributes"].get("date"),
            "action": ln["attributes"].get("action"),
            "params": {
                k: v
                for k, v in (ln["attributes"].get("params") or {}).items()
                if k
                in (
                    "path",
                    "source",
                    "destination",
                    "urls",
                    "title_new",
                    "title_original",
                    "updated_fields",
                    "file",
                    "preprint",
                    "registration",
                    "kind",
                    "name",
                )
            },
        }
        if "_error" not in ln
        else ln
        for ln in logs
    ]
srs = get_all("/registrations/tybgq/schema_responses/")
out["schema_responses"] = [
    {"id": s["id"], "revision_responses": s["attributes"].get("revision_responses")} for s in srs
]
reg = S.get(API + "/registrations/tybgq/", timeout=60).json()["data"]["attributes"]
out["registration_responses"] = reg.get("registration_responses")
Path(sys.argv[1]).write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("ok")
