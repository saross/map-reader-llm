"""Upload the late deposit and the corrections to OSF project h9x4g (idempotent).

New files only where absent; README.md gets a new VERSION (OSF keeps the old
one). Verifies every uploaded file's SHA-256 against OSF's record afterwards.
"""

import hashlib
import sys
from pathlib import Path
import requests

NODE = "h9x4g"
WB = f"https://files.osf.io/v1/resources/{NODE}/providers/osfstorage"
API = "https://api.osf.io/v2"
REPO = Path("/home/shawn/Code/map-reader-llm")
UP = Path(sys.argv[1])
OSF_DIR = REPO / "docs/methodology/preregistration/osf"
PREREG_FOLDER_ID = "697dfa7936fdb129fdcd8486"
README_FILE_ID = "697dfa8af7e4cbafb5e8e628"
DEPOSIT_FOLDER = "late-deposit-2026-10-05"

tok = [
    ln.split("=", 1)[1].strip().strip('"').strip("'")
    for ln in (Path.home() / "personal-assistant/.env").read_text().splitlines()
    if ln.startswith("OSF_API_KEY=")
][0]
S = requests.Session()
S.headers["Authorization"] = f"Bearer {tok}"


def listing(url):
    out, nxt = {}, url
    while nxt:
        j = S.get(nxt, timeout=60).json()
        for it in j["data"]:
            out[it["attributes"]["name"]] = it
        nxt = (j.get("links") or {}).get("next")
    return out


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(url, path):
    r = S.put(url, data=Path(path).read_bytes(), timeout=300)
    if r.status_code not in (200, 201):
        raise SystemExit(f"upload failed {r.status_code}: {url} {r.text[:300]}")
    return r.json()


log = []
root = listing(f"{API}/nodes/{NODE}/files/osfstorage/")
if DEPOSIT_FOLDER in root:
    folder_id = root[DEPOSIT_FOLDER]["attributes"]["path"].strip("/")
else:
    r = S.put(f"{WB}/?kind=folder&name={DEPOSIT_FOLDER}", timeout=60)
    if r.status_code not in (200, 201):
        raise SystemExit(f"folder create failed {r.status_code} {r.text[:300]}")
    folder_id = r.json()["data"]["attributes"]["path"].strip("/")
    log.append(f"created folder {DEPOSIT_FOLDER}")

dep = listing(f"{API}/nodes/{NODE}/files/osfstorage/{folder_id}/")
for name in [
    "deposit-index.md",
    "A-public-before-holdout.zip",
    "B-finalised-after-holdout.zip",
    "A-ls-tree.txt",
    "B-ls-tree.txt",
]:
    if name in dep:
        log.append(f"skip (exists) {DEPOSIT_FOLDER}/{name}")
        continue
    put(f"{WB}/{folder_id}/?kind=file&name={name}", UP / name)
    log.append(f"uploaded {DEPOSIT_FOLDER}/{name}")

pre = listing(f"{API}/nodes/{NODE}/files/osfstorage/{PREREG_FOLDER_ID}/")
for name in [
    "errata-pointers.md",
    "tile-mound-counts-recomputed-2026-09-13.md",
    "tile-mound-counts-recomputed-2026-09-13.json",
]:
    if name in pre:
        log.append(f"skip (exists) preregistration-files/{name}")
        continue
    put(f"{WB}/{PREREG_FOLDER_ID}/?kind=file&name={name}", OSF_DIR / name)
    log.append(f"uploaded preregistration-files/{name}")
readme_sha_osf = (pre["README.md"]["attributes"]["extra"]["hashes"] or {}).get("sha256")
if readme_sha_osf != sha(OSF_DIR / "README.md"):
    put(f"{WB}/{README_FILE_ID}?kind=file", OSF_DIR / "README.md")
    log.append("README.md: new version uploaded")
else:
    log.append("README.md already current")

# verify
dep = listing(f"{API}/nodes/{NODE}/files/osfstorage/{folder_id}/")
pre = listing(f"{API}/nodes/{NODE}/files/osfstorage/{PREREG_FOLDER_ID}/")
checks = [
    (dep, n, UP / n)
    for n in [
        "deposit-index.md",
        "A-public-before-holdout.zip",
        "B-finalised-after-holdout.zip",
        "A-ls-tree.txt",
        "B-ls-tree.txt",
    ]
]
checks += [
    (pre, n, OSF_DIR / n)
    for n in [
        "errata-pointers.md",
        "README.md",
        "tile-mound-counts-recomputed-2026-09-13.md",
        "tile-mound-counts-recomputed-2026-09-13.json",
    ]
]
ok = True
for lst, n, local in checks:
    remote = (lst[n]["attributes"]["extra"]["hashes"] or {}).get("sha256") if n in lst else None
    match = remote == sha(local)
    ok &= match
    log.append(
        f"verify {n}: {'OK' if match else 'MISMATCH'} (versions {lst[n]['attributes'].get('current_version') if n in lst else '-'})"
    )
print("\n".join(log))
print("ALL VERIFIED" if ok else "VERIFICATION FAILED")
