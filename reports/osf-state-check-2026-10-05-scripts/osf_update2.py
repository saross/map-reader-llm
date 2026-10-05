"""Create (or resume), fill and optionally submit registration update 2 on tybgq.

Usage: python osf_update2.py prepare   # create/patch the draft, print stored state
       python osf_update2.py submit    # submit the prepared draft (and approve if needed)
"""

import sys
from pathlib import Path
import requests

API = "https://api.osf.io/v2"
REG = "tybgq"
DRAFT = Path(
    "/home/shawn/Code/map-reader-llm/planning/osf-registration-update-2-draft-2026-10-05.md"
)
ORIGINAL = "697dfb712617a8b6769712bb"
LODGED = ["697dfb7636fdb129fdcd84e1", "697dfb7636fdb129fdcd84e2", "697dfb7636fdb129fdcd84e3"]
tok = [
    ln.split("=", 1)[1].strip().strip('"').strip("'")
    for ln in (Path.home() / "personal-assistant/.env").read_text().splitlines()
    if ln.startswith("OSF_API_KEY=")
][0]
S = requests.Session()
S.headers.update({"Authorization": f"Bearer {tok}", "Content-Type": "application/vnd.api+json"})


def text():
    t = DRAFT.read_text()
    start = t.index("## Update 2 (2026-10-05)")
    end = t.index("\n---\n", start)
    # OSF's sanitiser strips <https://...> autolinks (it removed the
    # February update's repository URL), so send them as plain URLs.
    import re

    return re.sub(r"<(https?://[^>]+)>", r"\1", t[start:end].strip()) + "\n"


def responses():
    return S.get(f"{API}/registrations/{REG}/schema_responses/", timeout=60).json()["data"]


mode = sys.argv[1]
existing = [r for r in responses() if r["attributes"]["reviews_state"] == "in_progress"]
if mode == "prepare":
    if existing:
        sid = existing[0]["id"]
        print("resuming in-progress draft", sid)
    else:
        r = S.post(
            f"{API}/schema_responses/",
            json={
                "data": {
                    "type": "schema-responses",
                    "relationships": {
                        "registration": {"data": {"type": "registrations", "id": REG}}
                    },
                }
            },
            timeout=60,
        )
        if r.status_code not in (200, 201):
            raise SystemExit(f"create failed {r.status_code}: {r.text[:500]}")
        sid = r.json()["data"]["id"]
        print("created draft", sid)
    orig = S.get(f"{API}/schema_responses/{ORIGINAL}/", timeout=60).json()["data"]["attributes"][
        "revision_responses"
    ]["uploader"]
    files = [f for f in orig if f["file_id"] in LODGED]
    assert [f["file_name"] for f in files] and len(files) == 3, files
    body = {
        "data": {
            "type": "schema-responses",
            "id": sid,
            "attributes": {
                "revision_justification": text(),
                "revision_responses": {"uploader": files},
            },
        }
    }
    r = S.patch(f"{API}/schema_responses/{sid}/", json=body, timeout=60)
    if r.status_code != 200:
        raise SystemExit(f"patch failed {r.status_code}: {r.text[:800]}")
    a = S.get(f"{API}/schema_responses/{sid}/", timeout=60).json()["data"]["attributes"]
    print("state:", a["reviews_state"], "| updated keys:", a["updated_response_keys"])
    print(
        "uploader:",
        [
            (f["file_name"], f["file_hashes"]["sha256"][:12])
            for f in a["revision_responses"]["uploader"]
        ],
    )
    j = a["revision_justification"]
    print("justification chars:", len(j), "| matches draft:", j.strip() == text().strip())
    print(
        "summary unchanged:",
        a["revision_responses"].get("summary")
        == S.get(f"{API}/registrations/{REG}/", timeout=60).json()["data"]["attributes"][
            "registration_responses"
        ]["summary"],
    )
elif mode == "submit":
    assert len(existing) == 1, f"expected one in-progress draft, found {len(existing)}"
    sid = existing[0]["id"]

    def act(trigger):
        r = S.post(
            f"{API}/schema_responses/{sid}/actions/",
            json={
                "data": {
                    "type": "schema-response-actions",
                    "attributes": {"trigger": trigger},
                    "relationships": {"target": {"data": {"type": "schema-responses", "id": sid}}},
                }
            },
            timeout=60,
        )
        print(trigger, r.status_code, r.text[:300] if r.status_code >= 300 else "")

    act("submit")
    st = S.get(f"{API}/schema_responses/{sid}/", timeout=60).json()["data"]["attributes"]
    print("after submit:", st["reviews_state"], st["date_submitted"])
    if st["reviews_state"] == "unapproved":
        act("approve")
        st = S.get(f"{API}/schema_responses/{sid}/", timeout=60).json()["data"]["attributes"]
    print("final:", sid, st["reviews_state"], st["date_submitted"], st["date_modified"])
