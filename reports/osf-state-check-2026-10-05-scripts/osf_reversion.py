"""Upload new versions of two changed files on OSF h9x4g, then verify SHA-256."""

import hashlib
from pathlib import Path
import requests

NODE = "h9x4g"
API = "https://api.osf.io/v2"
WB = f"https://files.osf.io/v1/resources/{NODE}/providers/osfstorage"
REPO = Path("/home/shawn/Code/map-reader-llm/docs/methodology/preregistration/osf")
tok = [
    ln.split("=", 1)[1].strip().strip('"').strip("'")
    for ln in (Path.home() / "personal-assistant/.env").read_text().splitlines()
    if ln.startswith("OSF_API_KEY=")
][0]
S = requests.Session()
S.headers["Authorization"] = f"Bearer {tok}"


def listing(path):
    j = S.get(f"{API}/nodes/{NODE}/files/osfstorage/{path}", timeout=60).json()
    return {it["attributes"]["name"]: it for it in j["data"]}


root = listing("")
targets = [
    ("late-deposit-2026-10-05", "deposit-index.md", REPO / "late-deposit/deposit-index.md"),
    ("preregistration-files", "errata-pointers.md", REPO / "errata-pointers.md"),
]
for folder, name, local in targets:
    fid = root[folder]["attributes"]["path"].strip("/")
    item = listing(fid + "/")[name]
    file_id = item["attributes"]["path"].strip("/")
    want = hashlib.sha256(local.read_bytes()).hexdigest()
    have = (item["attributes"]["extra"]["hashes"] or {}).get("sha256")
    if have == want:
        print(f"{folder}/{name}: already current")
        continue
    r = S.put(f"{WB}/{file_id}?kind=file", data=local.read_bytes(), timeout=120)
    print(f"{folder}/{name}: upload {r.status_code}")
    item = listing(fid + "/")[name]
    have = (item["attributes"]["extra"]["hashes"] or {}).get("sha256")
    print(
        f"   verify: {'OK' if have == want else 'MISMATCH'}; version {item['attributes']['current_version']}"
    )
