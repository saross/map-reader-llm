# NAS Migration Plan

**Status**: Draft 2026-04-20, revised 2026-04-20 after user feedback. Plan-only
— no bytes move until stages are explicitly executed. Produced by Plan agent
brief, informed by live disk reconnaissance across amd-tower, sapphire, zbook,
and rpi-server.

## Revisions log

- 2026-04-20 (initial): Plan drafted.
- 2026-04-20 (rev 1): User decisions applied. D2/D3/D4/D5/D6 confirmed. D7/D8
  resolved to R2 (not Google Drive) with rationale in Stage 5.1. D1 resolved as
  pragmatically irreplaceable (gift from colleague; possible GDrive source copy
  to check). D9 resolved as active Syncthing for personal files, orthogonal to
  project — no audit needed. Added QNAP→Vantec mirror (Stage 2.5) since user
  already has Vantec encrypted external drive that travels on long trips.
- 2026-04-20 (rev 2): GDrive verified to hold a complete `Russian1981_4326/`
  raster backup from Barbora Weissova at
  `My Drive/2023-MapDigitisation-ML/Maps/Russian1981_4326/` (plus a
  `FaimsMaps3857/` sibling in EPSG:3857). This gives a 5th redundancy tier for
  source material. R2 tier switched from Standard to **Infrequent Access**
  (storage $0.01/GB-month, 30-day min retention, $0.01/GB retrieval — matches
  our monthly-write / rare-read pattern; saves ~$0.20/mo now, scales with
  workspace growth).

## Executive summary

Three workstations hold ~109 GB of project data with significant divergence.
zbook is critically full (59 GB free of 944 GB). `/opt/encrypted/workspace` on
rpi-server (300 GB free, NVMe-backed, LUKS) is the right target for the
**active** working set. `/mnt/qnap` and `/mnt/vantec` are the right targets for
**archival superseded** data.

**Key reframing from repo scouting:** `archive/ARCHIVE-MANIFEST.md` declares
`outputs/phase3a/`, `outputs/phase3a-replication/`, `outputs/phase3c/`, and
`outputs/pv/` as **superseded** by `outputs/retest/phase3a*`,
`outputs/retest/phase3c`, and `outputs/h11/proposer-verifier-384/` respectively.
These paths were moved to `archive/` on amd-tower but the zbook copies (~43 GB
combined) and amd-tower's `pv/` (1.9 GB) appear to be pre-archive originals
never cleaned up. That collapses zbook pressure from "77 GB of live project
data" to "~35 GB live + ~42 GB archival" — the archival portion belongs on
QNAP, not on the encrypted active workspace.

**Recommended tooling**: plain `rsync` for the migration itself (simple,
inspectable, stateless). Defer DVC adoption until post-consolidation /
post-publication — or replace it with a lightweight MANIFEST-in-git approach
(see Stage 3.3). Details in Stage 3.

**Recommended R2 role**: cold off-site backup of the NAS canonical workspace
via monthly `rclone sync`, plus ad-hoc selective pulls when travelling. Not a
working tier. Cost estimate ~USD $1/month at consolidated size.

**Syncthing on rpi-server**: `/opt/encrypted/workspace/syncthing` directory is
likely orphan from a prior experiment. Audit in Stage 0.4 but it does not play
a role in the plan.

---

## Decision points summary

| # | Decision | Default recommendation | Stage |
|---|---|---|---|
| D1 | Are the Soviet 1981 rasters re-downloadable? | **RESOLVED**: Gift from Barbora Weissova (2017 Yambol campaign). GDrive has a complete `Russian1981_4326/` backup at `2023-MapDigitisation-ML/Maps/` (plus `FaimsMaps3857/` sibling). Effectively an additional cold-copy tier. Document in `inputs/rasters/SOURCES.md`. | Stage 0 |
| D2 | Keep `phase3a` / `phase3c` / legacy `pv/`? | **RESOLVED**: Archive to QNAP, mirror to Vantec, remove from active workspace. | Stage 1 |
| D3 | Canonical `outputs/h11/` copy? | **RESOLVED**: Sapphire (7.6 GB) — purely file-merge mechanics, H11 is scientifically done. Top up with `--ignore-existing` from others. | Stage 2 |
| D4 | Directory layout on NAS? | **RESOLVED**: Mirror repo structure under `/opt/encrypted/workspace/map-reader-llm/`; `archive/` tree on QNAP. | Stage 2 |
| D5 | DVC vs rsync vs hybrid? | **RESOLVED**: rsync now; MANIFEST-in-git for reproducibility; defer DVC to a future project. | Stage 3 |
| D6 | What stays on zbook for travel? | **RESOLVED**: Produce `planning/zbook-travel-checkout.md` + `scripts/sync_zbook_travel.sh`. Minimal set: `Russian1981_32635/`, `tiles_384_55maps/`, current h11 condition, git content. | Stage 4 |
| D7 | Off-site backup: R2 vs Google Drive? | **RESOLVED**: R2 primary (rate-limit-free, vendor-independent, zero egress). GDrive retained for source-material copies (e.g. Soviet rasters if found) and sharing. | Stage 5 |
| D8 | R2 sync cadence? | **RESOLVED**: Monthly cron + post-milestone manual. | Stage 5 |
| D9 | Is the `syncthing/` dir on rpi active? | **RESOLVED**: Active — user's personal-file sync infrastructure, orthogonal to project. No audit needed. | — |

---

## Stage 0 — Pre-flight (read-only verification, no bytes move)

**Goal:** verify every assumption later stages rest on. Resolve D1 and D9.

### 0.1 Verify free space and mount state on rpi-server

```bash
ssh -p 2222 rpi-server '\
  df -h /opt/encrypted/workspace /mnt/qnap /mnt/vantec; \
  mount | grep -E "(workspace|qnap|vantec)"; \
  ls -la /opt/encrypted/workspace/'
```

Expected: 300 GB free on workspace, QNAP/Vantec mounted, workspace accessible.
If workspace is NOT unlocked, stop — the reboot rule prevents easy recovery.

### 0.2 Verify SSH key auth to rpi-server from all three hosts

From each of amd-tower, sapphire, zbook:

```bash
ssh -p 2222 -o BatchMode=yes rpi-server 'hostname; date'
```

If any machine prompts for password, fix with `ssh-copy-id` before Stage 1.

### 0.3 Snapshot current sizes (baseline for later verification)

Run on each machine:

```bash
cd ~/Code/map-reader-llm && {
  echo "=== $(hostname) $(date -Iseconds) ===";
  du -sh inputs outputs archive results logs 2>/dev/null;
  echo "--- inputs/ top-level ---";
  du -sh inputs/*/ 2>/dev/null;
  echo "--- outputs/ top-level ---";
  du -sh outputs/*/ 2>/dev/null;
  echo "--- disk ---";
  df -h .;
} | tee planning/nas-migration-baseline-$(hostname)-$(date +%Y%m%d).txt
```

### 0.4 Syncthing on rpi-server — no action needed

User confirmed: Syncthing on rpi-server handles everyday personal-file sync
across machines. Orthogonal to this plan. Project data uses rsync+cron for
explicit, controlled sync. Do not configure Syncthing shares for project data
under `/opt/encrypted/workspace/map-reader-llm/`.

### 0.5 Soviet raster source copy on Google Drive — CONFIRMED

Verified 2026-04-20 via GDrive MCP connector. A complete `Russian1981_4326/`
folder exists on Shawn's Google Drive:

- Canonical path: `My Drive/2023-MapDigitisation-ML/Maps/Russian1981_4326/`
- Folder URL: <https://drive.google.com/drive/folders/1ITscB4V2dyv1UkesEBXa3e4Bri0GMHTk>
- Files uploaded 2023-03-06, original modification timestamps preserved from
  2022-09-13.
- File naming matches zbook exactly: `K-35-*_*_4326.tif`, ~45 MB each.
- Sibling folder `FaimsMaps3857/` contains the same sheets in EPSG:3857 (Web
  Mercator) — NOT currently on any workstation; pull only if needed.
- Source attribution: Barbora Weissova (`barabora.weissova@gmail.com`);
  originating campaign evidenced by document "Soviet Topo maps and Burial
  Mounds in the Yambol District, Campaign of 2017" on her account.

**Outcome**: rasters now have a 5th redundancy tier for free. R2 raster backup
shifts from "only off-site copy" to "one of two off-site copies."

**Action**: create `inputs/rasters/SOURCES.md` documenting source, colleague
attribution, GDrive URL, available projections, and a note to check licence /
redistribution permission with Barbora before Zenodo release. Draft content:

```markdown
# Raster Source Documentation

## Provenance
Soviet military 1:50,000 topographic sheets, 1981 edition, covering the Yambol
District, Bulgaria. Received from Barbora Weissova as part of collaboration
originating in the 2017 Yambol field campaign (see "Soviet Topo maps and
Burial Mounds in the Yambol District, Campaign of 2017" on shared GDrive).

## Canonical backup
My Drive/2023-MapDigitisation-ML/Maps/Russian1981_4326/
  <https://drive.google.com/drive/folders/1ITscB4V2dyv1UkesEBXa3e4Bri0GMHTk>

## Projection variants
- EPSG:4326 (WGS84 lat/lon) — source files on GDrive and zbook `inputs/rasters/Russian1981_4326/`
- EPSG:32635 (UTM 35N) — reprojected via gdalwarp; present on all workstations
- EPSG:3857 (Web Mercator) — GDrive sibling `FaimsMaps3857/`; not currently on workstations

## Reference material
- `SovietTopoSymbols.pdf` on GDrive (symbol key, 25 MB)

## Redistribution / licensing (TODO)
Confirm with Barbora Weissova before including rasters in any public Zenodo
release. Original Soviet military cartography is typically out of copyright
(pre-1973 origin; Soviet state materials) but the georeferenced derivatives
Barbora produced may have separate attribution requirements.
```

The `inputs/rasters/K-35-*.tif` files are Soviet 1981 1:50,000 topographic
sheets. Questions:

1. Can you re-download the exact files from a documented source?
2. `Russian1981_4326/` (17 GB, zbook-only) vs `Russian1981_32635/` (2.4 GB
   everywhere): the `_32635/` versions are reprojected derivatives of `_4326/`
   via `gdalwarp`. If `_4326/` is public-archive-sourced, even it is
   regeneratable.

Check:

```bash
# on zbook
ls -la ~/Code/map-reader-llm/inputs/rasters/Russian1981_4326/ | head
find ~/Code/map-reader-llm/inputs/rasters/ -name "README*" -o -name "SOURCES*"
```

**DECISION D1**: record source URLs / accession info in
`inputs/rasters/SOURCES.md` (or update existing README). This documentation is
needed for Zenodo release anyway.

### 0.6 Verify sapphire has the most complete `outputs/h11/`

```bash
# Run on each machine, collect to one place
cd ~/Code/map-reader-llm && find outputs/h11 -type d | sort > /tmp/h11-dirs-$(hostname).txt
```

`scp` the three files and `diff` them. Sapphire should be a proper superset.
If not, Stage 2 merge strategy changes.

### 0.7 Confirm `phase3a/c` on zbook really are superseded

```bash
# on zbook
ls -la ~/Code/map-reader-llm/outputs/retest/ | grep phase3
du -sh ~/Code/map-reader-llm/outputs/retest/phase3* 2>/dev/null
du -sh ~/Code/map-reader-llm/outputs/phase3a ~/Code/map-reader-llm/outputs/phase3c 2>/dev/null
```

If `outputs/retest/phase3a*` is missing or much smaller on zbook, supersession
is incomplete and pruning is unsafe.

### 0.8 Check non-obvious large files

```bash
# on each machine
cd ~/Code/map-reader-llm && du -sh results/ logs/ archive/cc-sessions/ 2>/dev/null
```

If `results/` is >few hundred MB, include in NAS plan.

### 0.9 Git state check

```bash
cd ~/Code/map-reader-llm && git status && git rev-parse HEAD
```

All three should be clean and on the same HEAD. Stash/commit dirty state first.

**Stage 0 exit criterion**: D1 and D9 resolved; baselines captured; free space
confirmed; SSH working; supersession of phase3a/c confirmed on zbook; h11
superset confirmed on sapphire.

---

## Stage 1 — Consolidate unique data to NAS (highest-risk first)

**Goal**: eliminate single-copy risk. Every byte that exists on only one machine
gets a second copy on rpi-server before anything else happens.

### 1.1 NAS directory layout

**DECISION D4**: mirror repo structure under a project root, parallel
`archive/` tree for superseded data.

```text
/opt/encrypted/workspace/
  map-reader-llm/                     # LIVE canonical working set (~70 GB target)
    inputs/
      rasters/
        Russian1981_4326/             # from zbook (17 GB)
        Russian1981_32635/            # from any (2.4 GB)
      tiles/
      tiles_256/
      tiles_384/
      tiles_384_55maps/               # from sapphire or zbook (2 GB)
      vectors/
    outputs/
      h11/                            # canonical from sapphire (7.6 GB)
      retest/
      55maps-generalisation/
      55maps-image-generalisation/
      55maps-text-high-generalisation/
      55maps-text-min-generalisation/
      h10/
      h8-v2/
      h12-v2/
      figures/
      qgis-*/
      results/
    results/

/mnt/qnap/map-reader-llm-archive/
  2026-04-pre-migration-snapshots/    # per-host safety snapshots
    amd-tower/
    sapphire/
    zbook/
  superseded/
    outputs-phase3a/                  # from zbook, 20 GB
    outputs-phase3a-replication/      # from zbook, 2.2 GB
    outputs-phase3c/                  # from zbook, 21 GB
    outputs-pv-legacy/                # from amd-tower, 1.9 GB
```

Create the scaffolding:

```bash
ssh -p 2222 rpi-server '\
  mkdir -p /opt/encrypted/workspace/map-reader-llm/{inputs,outputs,results} && \
  mkdir -p /mnt/qnap/map-reader-llm-archive/{superseded,2026-04-pre-migration-snapshots}'
```

### 1.2 Safety net: pre-migration raw snapshot (optional)

Before deleting anything, consider a flat `rsync` of each host's `inputs/`,
`outputs/`, `archive/` into
`/mnt/qnap/map-reader-llm-archive/2026-04-pre-migration-snapshots/$HOST/`.
Insurance against a bad merge. QNAP has 15 TB free; costs only time.

```bash
# Example for zbook (repeat for amd-tower and sapphire)
rsync -aHhP --numeric-ids \
  --log-file=/tmp/rsync-zbook-snapshot.log \
  ~/Code/map-reader-llm/inputs \
  ~/Code/map-reader-llm/outputs \
  ~/Code/map-reader-llm/archive \
  -e "ssh -p 2222" \
  rpi-server:/mnt/qnap/map-reader-llm-archive/2026-04-pre-migration-snapshots/zbook/
```

Time estimate: zbook ~80 GB; gigabit Ethernet ~15 min, 100 Mb/s ~2 hours.

### 1.3 Pull unique-to-zbook LIVE data to encrypted workspace

```bash
# From zbook — dry-run first
rsync -aHhP --dry-run --stats \
  -e "ssh -p 2222" \
  ~/Code/map-reader-llm/inputs/rasters/Russian1981_4326/ \
  rpi-server:/opt/encrypted/workspace/map-reader-llm/inputs/rasters/Russian1981_4326/

# Real run
rsync -aHhP --stats \
  --log-file=$HOME/nas-migration-logs/zbook-russian4326.log \
  -e "ssh -p 2222" \
  ~/Code/map-reader-llm/inputs/rasters/Russian1981_4326/ \
  rpi-server:/opt/encrypted/workspace/map-reader-llm/inputs/rasters/Russian1981_4326/
```

**rsync flags**:
- `-a` archive (perms, times, symlinks, recursion)
- `-H` preserve hardlinks
- `-h` human-readable sizes
- `-P` = `--partial --progress` (resume + show progress)
- `--stats` end-of-run summary
- Trailing slash on source = copy contents.

Repeat for `inputs/tiles_384_55maps/` (from zbook OR sapphire).

### 1.4 Push superseded data to QNAP (not encrypted workspace)

**DECISION D2**: strong recommendation to archive on QNAP.

From zbook:

```bash
rsync -aHhP --stats --log-file=$HOME/nas-migration-logs/zbook-phase3a.log \
  -e "ssh -p 2222" \
  ~/Code/map-reader-llm/outputs/phase3a/ \
  rpi-server:/mnt/qnap/map-reader-llm-archive/superseded/outputs-phase3a/

rsync -aHhP --stats --log-file=$HOME/nas-migration-logs/zbook-phase3c.log \
  -e "ssh -p 2222" \
  ~/Code/map-reader-llm/outputs/phase3c/ \
  rpi-server:/mnt/qnap/map-reader-llm-archive/superseded/outputs-phase3c/

rsync -aHhP --stats \
  -e "ssh -p 2222" \
  ~/Code/map-reader-llm/outputs/phase3a-replication/ \
  rpi-server:/mnt/qnap/map-reader-llm-archive/superseded/outputs-phase3a-replication/
```

From amd-tower:

```bash
rsync -aHhP --stats \
  -e "ssh -p 2222" \
  ~/Code/map-reader-llm/outputs/pv/ \
  rpi-server:/mnt/qnap/map-reader-llm-archive/superseded/outputs-pv-legacy/
```

### 1.5 Verify each rsync

```bash
rsync -avnP --checksum \
  -e "ssh -p 2222" \
  ~/Code/map-reader-llm/outputs/phase3a/ \
  rpi-server:/mnt/qnap/map-reader-llm-archive/superseded/outputs-phase3a/ \
  | tail -20
```

Zero files needing transfer = verified complete.

**Stage 1 exit criterion**: all unique live data on workspace; all superseded
data on QNAP; verified; nothing deleted from source.

---

## Stage 2 — Converge on NAS as canonical

### 2.1 Canonical-version election

| Path | Canonical source | Rationale |
|---|---|---|
| `inputs/rasters/Russian1981_32635/` | any (checksum-verify identical) | identical across hosts |
| `inputs/rasters/K-35-*.tif` (other) | amd-tower | canonical committed set |
| `inputs/tiles_384_55maps/` | sapphire (verify) | generation machine |
| `inputs/tiles_384/`, `tiles_256/`, `tiles/` | sapphire | same |
| `inputs/vectors/` | whichever has most files | diff-check |
| `outputs/h11/` | **sapphire (7.6 GB)** | generation + largest |
| `outputs/retest/` | sapphire or amd-tower (checksum-diff 20 MB delta) | nearly tied |
| `outputs/55maps-*` | compare directly | biggest wins iff superset |

### 2.2 Merge strategy per directory

Three shapes:

1. **Pure overwrite**: sapphire is superset → single rsync.
2. **Union merge** (common): sapphire authoritative + other-host additions with `--ignore-existing`.
3. **Conflict**: pause, diff, resolve.

```bash
# Union merge for h11:
# Step 1: sapphire authoritative base (run from sapphire)
rsync -aHhP -e "ssh -p 2222" \
  ~/Code/map-reader-llm/outputs/h11/ \
  rpi-server:/opt/encrypted/workspace/map-reader-llm/outputs/h11/

# Step 2: amd-tower additions only (run from amd-tower)
rsync -aHhP --ignore-existing -e "ssh -p 2222" \
  ~/Code/map-reader-llm/outputs/h11/ \
  rpi-server:/opt/encrypted/workspace/map-reader-llm/outputs/h11/

# Step 3: zbook additions only (run from zbook)
rsync -aHhP --ignore-existing -e "ssh -p 2222" \
  ~/Code/map-reader-llm/outputs/h11/ \
  rpi-server:/opt/encrypted/workspace/map-reader-llm/outputs/h11/
```

Always `--dry-run` first. Many "unique" files from amd-tower or zbook = flag
to re-evaluate D3.

### 2.3 Detect cross-host conflicts

```bash
# After rpi has sapphire's h11, check from zbook:
rsync -aHhP --dry-run --checksum --itemize-changes \
  -e "ssh -p 2222" \
  ~/Code/map-reader-llm/outputs/h11/ \
  rpi-server:/opt/encrypted/workspace/map-reader-llm/outputs/h11/ \
  | grep -E "^>f\.st\.\.\.\.\.\." | head
```

Lines starting `>f.st......` = content differs. Review manually.

### 2.4 Regeneratable items — consider skipping

Exclude via `planning/rsync-exclude-regeneratable.txt`:

```text
crops/
crops/crops/
batch_working/
_archive-*/
_stale-files/
cleanup-records/
*.log
.active_files.*
```

Usage: `rsync -aHhP --exclude-from=planning/rsync-exclude-regeneratable.txt ...`

### 2.5 Handle `archive/` on each machine

Send each host's `archive/` to
`/mnt/qnap/map-reader-llm-archive/per-host-archive-snapshots/$HOST/` — deep
archival, not active workspace.

### 2.5 QNAP → Vantec mirror (local deep-storage redundancy)

User has a Vantec encrypted external drive on rpi-server (14.6 TB, 4.5 TB
free) that travels on longer trips. Mirror the QNAP archive to Vantec as a
scheduled rsync. Rationale: local RAID-like redundancy within the home, and
when the Vantec drive physically travels, it carries the archival data for
off-network reference.

Initial manual mirror:

```bash
ssh -p 2222 rpi-server '\
  rsync -aHhP --stats \
    --log-file=/var/log/rsync-qnap-vantec-$(date +%Y%m%d).log \
    /mnt/qnap/map-reader-llm-archive/ \
    /mnt/vantec/map-reader-llm-archive/'
```

Scheduled sync (after initial load) — weekly cron:

```text
# /etc/cron.d/qnap-vantec-mirror on rpi-server
# Sunday 02:00
0 2 * * 0 shawn rsync -aHh --delete \
  --log-file=/var/log/rsync-qnap-vantec-$(date +\%Y\%m\%d).log \
  /mnt/qnap/map-reader-llm-archive/ \
  /mnt/vantec/map-reader-llm-archive/
```

`--delete` is intentional here: Vantec is a **mirror**, not a union — deletions
on QNAP should propagate. For this to be safe, the QNAP side must never be
modified casually; archival data is write-rarely by design.

**Note on Vantec-while-travelling**: if the Vantec drive is unmounted (travel
scenario), the weekly cron rsync will fail silently. Add a check to the cron
wrapper that only runs if `/mnt/vantec` is actually mounted:

```bash
#!/usr/bin/env bash
# /home/shawn/bin/qnap-vantec-mirror.sh
mountpoint -q /mnt/vantec || exit 0
rsync -aHh --delete \
  --log-file=/var/log/rsync-qnap-vantec-$(date +%Y%m%d).log \
  /mnt/qnap/map-reader-llm-archive/ \
  /mnt/vantec/map-reader-llm-archive/
```

### 2.6 Record canonical-selection decisions

Create `planning/nas-canonical-decisions.md` with path → canonical-host →
verification-method → log-file rows. Auditable.

**Stage 2 exit criterion**: canonical live set on workspace; QNAP archive
populated and mirrored to Vantec (when present); every directory has
documented source-of-truth; no unresolved conflicts; source machines untouched.

---

## Stage 3 — Tooling: DVC vs rsync vs hybrid

### 3.1 Tool comparison

**rsync**: inspectable, stateless, no infrastructure, robust, resumes cleanly.
No versioning, no commit-data linking, manual cadence.

**DVC (`ssh://` to rpi-server)**: data-git commit linking, checksums per file,
`dvc pull` reproduces a snapshot. Adds state, CAS layout on remote (files by
hash, not path — loses `ls` browsability), new tool dependency. Risky
mid-flight near publication.

### 3.2 Recommendation (DECISION D5)

**Use rsync for this migration. Do not DVC-init anything.**

1. Migration's primary risk is "lose or corrupt unique data"; rsync is easier
   to reason about.
2. DVC's CAS layout breaks `ls` browsability on the NAS — contrary to the goal
   of consolidating for readability.
3. Near publication — adding a new tool is confusing for reviewers and for you.
4. rsync works with zero setup beyond SSH keys.

Post-publication, revisit DVC (or `git-annex`) with less pressure.

### 3.3 Lightweight version-pinning alternative (recommended)

After Stage 2:

```bash
ssh -p 2222 rpi-server '\
  cd /opt/encrypted/workspace/map-reader-llm && \
  find inputs outputs results -type f -printf "%p\t%s\t" -exec sha256sum {} \; \
  | awk "{print \$3\"  \"\$1\"  \"\$2}" \
  > MANIFEST-$(date +%Y%m%d).tsv'
```

`(sha256, path, size)` per file. Commit MANIFEST to git — few MB for ~100k
files. For any git commit, the matching MANIFEST records exactly what data was
live. No DVC, no CAS, no state.

### 3.4 If you decide DVC is right anyway

Reference only:

- Remote: `dvc remote add -d nas ssh://rpi-server:2222/opt/encrypted/workspace/map-reader-llm/.dvc-remote`
- Initial add: one directory at a time, check `.gitignore` updates between.

---

## Stage 4 — Thin local caches

**Goal**: reclaim space on amd-tower and (critically) zbook.

### 4.1 Pre-flight: verify NAS is authoritative

```bash
rsync -avnP --checksum -e "ssh -p 2222" \
  ~/Code/map-reader-llm/outputs/phase3a/ \
  rpi-server:/mnt/qnap/map-reader-llm-archive/superseded/outputs-phase3a/ \
  | tail -5
```

Zero differences = safe to delete locally.

### 4.2 zbook pruning (priority)

```bash
cd ~/Code/map-reader-llm
du -sh outputs/phase3a outputs/phase3c outputs/phase3a-replication
rm -rf outputs/phase3a
rm -rf outputs/phase3c
rm -rf outputs/phase3a-replication
rm -rf inputs/rasters/Russian1981_4326
df -h ~
```

Reclaim: ~60 GB. Takes zbook from 94% full → ~73% full.

**DECISION D6 (resolved)**: explicit check-out manifest for zbook travel set.

Create `planning/zbook-travel-checkout.md` with the concrete list of paths and
sizes. Minimum set:

- `inputs/rasters/Russian1981_32635/` (2.4 GB) — active UTM rasters
- `inputs/tiles_384_55maps/` (2 GB) — current phase tiling
- `inputs/vectors/` (~9 MB) — hand-digitised GT + bounds
- Most recent h11 condition subdir only (~500 MB – 1 GB)
- All git-tracked content (scripts, configs, prompts, docs, results)

Create `scripts/sync_zbook_travel.sh` as a one-shot pull from NAS:

```bash
#!/usr/bin/env bash
# scripts/sync_zbook_travel.sh — refresh zbook's travel working set from NAS
set -euo pipefail

NAS_ROOT="rpi-server:/opt/encrypted/workspace/map-reader-llm"
LOCAL_ROOT="$HOME/Code/map-reader-llm"
SSH_OPTS="-e ssh -p 2222"

# List of paths to sync (edit for phase-specific needs)
PATHS=(
  "inputs/rasters/Russian1981_32635"
  "inputs/tiles_384_55maps"
  "inputs/vectors"
  # "outputs/h11/CURRENT-CONDITION"  # uncomment and edit for active phase
)

for p in "${PATHS[@]}"; do
  echo "=== Syncing $p ==="
  rsync -aHhP --update $SSH_OPTS \
    "$NAS_ROOT/$p/" \
    "$LOCAL_ROOT/$p/"
done

echo "Travel checkout complete: $(date -Iseconds)"
```

Run before leaving home network. Everything else is pulled from R2 on demand.

Everything not listed: pull on demand from R2 via `rclone copy`.

### 4.3 amd-tower pruning

Remove superseded `outputs/pv/` (1.9 GB, now on QNAP) after verification.
Leave inputs/ in place — it's the primary workstation.

### 4.4 sapphire pruning

Sapphire is the compute box. Do NOT prune aggressively. Keep `inputs/` local
for detection runs. Prune only `archive/` (2.0 GB, snapshot on QNAP) and
fully-finished experiment outputs.

### 4.5 Do NOT modify .gitignore

Paths moved are already gitignored. Nothing changes in git.

**Stage 4 exit criterion**: zbook <80% full; every deletion checksum-verified
against NAS; amd-tower and sapphire pruned conservatively.

---

## Stage 5 — R2 off-site backup

### 5.1 Scope (DECISION D7, resolved)

**Use R2 (not Google Drive) for off-site backup of the LIVE encrypted
workspace.**

R2 vs Google Drive rationale:

| Factor | R2 | Google Drive |
|---|---|---|
| Incremental cost at 70 GB | ~$1/month | $0 (spare quota) |
| Rate limits | None that matter | 750 GB/day upload cap; per-file API throttling kills bulk sync of many small files |
| rclone performance | First-class, unfussy | Flaky on many small files; best perf needs own OAuth client ID |
| Egress cost | Zero | Free but rate-limited on restore |
| Failure-mode independence | Separate vendor, separate credentials | Same Google account as email/drive/etc. — single compromise = all gone |
| Versioning | Configurable | Exists but limited |

The "spare quota" argument is opportunity cost, not savings — the Google
Workspace monthly fee is the same whether 500 GB or 5 TB used. At $1/month, R2
pays for itself the first time GDrive rate-limits a restore during a real
incident.

**Google Drive retained role** (complementary, not competing):

- Source-material copy: if the Soviet raster set exists on GDrive from the
  colleague hand-off, leave it there as an additional cold copy.
- Ad-hoc sharing with collaborators.
- Zenodo pre-release staging if helpful.

Do NOT put the automated rclone backup on GDrive.

**Scope of R2 backup**:

- Live workspace (~70 GB) = what you need if NAS dies before publication.
- QNAP archive (~45 GB superseded) = redundant deep storage; covered by
  QNAP→Vantec mirror (Stage 2.5) within the home.
- Rasters (pragmatically irreplaceable per D1): on NAS live workspace and
  therefore automatically included in R2 backup. Plus optional GDrive source
  copy.

### 5.2 R2 setup — use Infrequent Access tier

Cloudflare dashboard: create bucket `map-reader-llm-backup` in APAC region,
**select Infrequent Access storage class**, create R2 API token scoped to the
bucket.

Pricing math (verified 2026-04-20 against current R2 rates):

| | Standard | Infrequent Access |
|---|---|---|
| Storage | $0.015/GB-mo | **$0.01/GB-mo** |
| Class A writes | $4.50/M | $9.00/M |
| Class B reads | $0.36/M | $0.90/M |
| Data retrieval | — | $0.01/GB |
| Egress | $0 | $0 |
| Min retention | — | 30 days |
| Free tier | 10 GB + 1M/10M ops | none |

At 70 GB live backup, monthly sync cadence, rare reads: Standard nets ~$0.90/mo
(after free tier); IA nets ~$0.72/mo. Savings are modest at current size but
scale with workspace growth (~$0.75/mo saving at 150 GB). The usage pattern
(write-heavy monthly, read-only in emergency) matches IA's design. 30-day
retention is a non-issue for monthly cadence. A full 70 GB restore under IA
costs $0.70 one-time — the "insurance pays out" moment where that's trivial.

```bash
ssh -p 2222 rpi-server '\
  rclone config create r2 s3 \
    provider=Cloudflare \
    access_key_id=<FROM_DASHBOARD> \
    secret_access_key=<FROM_DASHBOARD> \
    endpoint=<ACCOUNT_ID>.r2.cloudflarestorage.com \
    acl=private'

# Test
ssh -p 2222 rpi-server 'rclone lsd r2:'
ssh -p 2222 rpi-server 'rclone mkdir r2:map-reader-llm-backup/test && rclone rmdir r2:map-reader-llm-backup/test'
```

### 5.3 Sync command

```bash
ssh -p 2222 rpi-server '\
  rclone sync \
    /opt/encrypted/workspace/map-reader-llm/ \
    r2:map-reader-llm-backup/live/ \
    --fast-list \
    --transfers 16 \
    --checkers 32 \
    --s3-chunk-size 64M \
    --s3-upload-concurrency 8 \
    --exclude ".dvc/cache/**" \
    --exclude "**/crops/crops/**" \
    --exclude "**/*.log" \
    --log-file /var/log/rclone-r2-$(date +%Y%m%d).log \
    --stats-one-line \
    --stats 30s'
```

`--fast-list` critical for R2 (per-op pricing). Excludes mirror rsync list from 2.4.

### 5.4 Cadence (DECISION D8)

- **Post-milestone snapshot**: after significant phase completes, manual run.
- **Monthly scheduled**: cron on rpi-server.

```text
# /etc/cron.d/map-reader-llm-r2-backup
0 3 1 * * shawn /home/shawn/bin/r2-sync-map-reader.sh
```

NOT daily — data doesn't change daily post-consolidation, and Class A ops cost.

### 5.5 Cost estimate (Infrequent Access tier)

At ~70 GB live:

- Storage: 70 × $0.01 = **$0.70/month**
- Monthly sync ops (~1k Class A): ~$0.01/month
- Egress on travel pulls: **$0** (IA still inherits R2's zero-egress)
- Emergency restore (70 GB full pull): $0.70 one-time retrieval + $0 egress
- **Total: ~$0.72/month** steady-state

Compare AWS S3 Standard-IA at same usage: ~$2/month storage + egress.
R2 IA's zero egress + $0.01/GB storage is the right choice.

### 5.6 Travel workflow

```bash
# Before leaving: sync to R2 (on rpi-server)
ssh -p 2222 rpi-server 'rclone sync /opt/encrypted/workspace/map-reader-llm/ r2:map-reader-llm-backup/live/'

# On zbook, while travelling, selective pull
rclone copy r2:map-reader-llm-backup/live/inputs/rasters/Russian1981_32635/ \
  ~/Code/map-reader-llm/inputs/rasters/Russian1981_32635/
```

### 5.7 Restore drill (mandatory before relying on it)

```bash
mkdir /tmp/r2-restore-test
rclone copy r2:map-reader-llm-backup/live/inputs/rasters/Russian1981_32635/ /tmp/r2-restore-test/
ls -la /tmp/r2-restore-test/
rm -rf /tmp/r2-restore-test
```

**Stage 5 exit criterion**: R2 bucket populated; first sync log clean; restore
drill passed; cron scheduled; costs recorded.

---

## Stage 6 — Long-term workflow

### 6.1 New data flow

```text
  Experiment generated on sapphire (GPU, big)
         |
         | rsync on run completion
         v
  rpi-server /opt/encrypted/workspace/map-reader-llm/  (LIVE canonical)
         |
         +--> rsync (curation) --> rpi-server /mnt/qnap/...-archive/ (DEEP)
         |                                |
         |                                +--> weekly rsync --> /mnt/vantec (MIRROR, travels)
         |
         +--> monthly rclone sync --> R2 (OFF-SITE disaster insurance)
         |
         +--> on-demand rsync pull --> amd-tower (office)
         |
         +--> scripts/sync_zbook_travel.sh --> zbook (selective travel set)
```

Five-tier redundancy (rasters) / four-tier (everything else):
1. **Live** — NAS encrypted NVMe workspace
2. **Deep** — NAS QNAP archive
3. **Mirror** — NAS Vantec (same machine, different disk, portable)
4. **Off-site** — Cloudflare R2 (Infrequent Access tier)
5. **Source** — Google Drive (rasters only: `2023-MapDigitisation-ML/Maps/Russian1981_4326/`)

Key principle: sapphire writes local-first (fast NVMe), then syncs to NAS.
Avoid making sapphire write directly to NAS during runs.

### 6.2 Post-run sync hook on sapphire

```bash
# scripts/post_run_sync_to_nas.sh
#!/usr/bin/env bash
set -euo pipefail
RUN_DIR="${1:?usage: post_run_sync_to_nas.sh <output_dir>}"
LOG_DIR="$HOME/nas-sync-logs"
mkdir -p "$LOG_DIR"
ts=$(date +%Y%m%d-%H%M%S)

rsync -aHhP \
  --log-file="$LOG_DIR/sync-$ts.log" \
  --stats \
  -e "ssh -p 2222" \
  "$RUN_DIR/" \
  "rpi-server:/opt/encrypted/workspace/map-reader-llm/${RUN_DIR#$HOME/Code/map-reader-llm/}/"

echo "Synced to NAS: $(date -Iseconds)" >> "$RUN_DIR/.nas-sync-marker"
```

Invoke from `scripts/4_detect_mounds_batch.py` success path, or manually.

### 6.3 Pulling work to amd-tower

```bash
rsync -aHhP --update -e "ssh -p 2222" \
  rpi-server:/opt/encrypted/workspace/map-reader-llm/outputs/h11/ \
  ~/Code/map-reader-llm/outputs/h11/
```

`--update` skips files where dest is newer. Safe to re-run.

### 6.4 Travel prep checklist for zbook

1. Post-run sync from sapphire if pending experiment.
2. `rclone sync` on rpi-server to update R2.
3. If long trip: ensure QNAP→Vantec mirror is current; take Vantec drive.
4. On zbook, run `scripts/sync_zbook_travel.sh` to refresh travel set from NAS.
5. Git push/pull any in-flight work.
6. Verify R2 credentials: `rclone lsd r2:map-reader-llm-backup/`.

### 6.5 Publication-time Zenodo release

1. Freeze a final commit in git.
2. Generate MANIFEST (as in 3.3) against NAS at that commit.
3. Decide Zenodo subset (probably final `outputs/h11/`, `results/`, curated
   tile set — not raw rasters unless journal expects).
4. Tar from NAS (canonical set):

   ```bash
   ssh -p 2222 rpi-server '\
     cd /opt/encrypted/workspace/map-reader-llm && \
     tar --exclude="**/crops/crops/**" -czf /tmp/zenodo-release.tar.gz \
         outputs/h11 results MANIFEST-*.tsv'
   ```

5. Upload to Zenodo, record DOI in `CITATION.cff` and `codemeta.json`.

### 6.6 When to revisit tooling

Post-publication, revisit DVC (or `git-annex`) without publication pressure.
By then: smaller data volume, settled canonical location, clearer trade-off.

---

## Appendix A — Regeneratable vs irreplaceable

| Data | Category | Implication |
|---|---|---|
| `inputs/rasters/Russian1981_4326/` | **Irreplaceable** (pending D1) | NAS + R2 |
| `inputs/rasters/Russian1981_32635/` | Regeneratable via gdalwarp | NAS only |
| `inputs/rasters/K-35-*_{Elenovo,Rakovski,Lesovo,Straldzha_4326}.tif` | Likely irreplaceable | NAS + R2 |
| `inputs/tiles_*/` | Regeneratable | NAS only |
| `inputs/vectors/` | Likely irreplaceable (hand-digitised) | NAS + R2 critical |
| `inputs/gis-map-mounds/` | Likely irreplaceable | NAS + R2 critical |
| `outputs/h11/` current | **Irreplaceable** (API costs to regenerate) | NAS + R2 |
| `outputs/retest/` | **Irreplaceable** | NAS + R2 |
| `outputs/55maps-*` | **Irreplaceable** | NAS + R2 |
| `outputs/phase3a/`, `phase3c/`, `pv/` | Superseded archival | QNAP only; no live, no R2 |
| `outputs/**/crops/` | Regeneratable | Skip entirely |
| `outputs/**/batch_working/`, `*.log` | Transient | Skip entirely |
| `results/` | Derivable (but slow) | NAS + R2 recommended |
| Git-tracked | Git is source of truth | Don't migrate |

## Appendix B — Commands quick reference

```bash
# Dry-run a transfer
rsync -aHhP --dry-run --stats -e "ssh -p 2222" SRC/ rpi-server:DEST/

# Real transfer with log
rsync -aHhP --stats --log-file=LOG -e "ssh -p 2222" SRC/ rpi-server:DEST/

# Verify completeness
rsync -aHhPn --checksum -e "ssh -p 2222" SRC/ rpi-server:DEST/ | grep -v "^$"

# Union merge (second/third with --ignore-existing)
rsync -aHhP --ignore-existing -e "ssh -p 2222" SRC/ rpi-server:DEST/

# R2 sync (from rpi-server)
rclone sync /opt/encrypted/workspace/map-reader-llm/ r2:map-reader-llm-backup/live/ --fast-list

# R2 selective pull
rclone copy r2:map-reader-llm-backup/live/PATH/ LOCAL_PATH/

# Disk snapshot
du -sh inputs outputs archive results 2>/dev/null | tee planning/baseline-$(hostname)-$(date +%Y%m%d).txt
```

## Appendix C — Things explicitly not being done

- Not modifying `.gitignore`.
- Not `dvc init`ing.
- Not moving any bytes (plan-only).
- Not rebooting rpi-server.
- Not touching `/opt/encrypted/workspace/syncthing/` beyond read-only audit.

---

## How to use this plan

Work through stages in order. Each stage has an exit criterion — do not proceed
past it until met. Expect to pause between stages, especially 1→2 (verify
unique data before reconciling shared) and 4→5 (verify NAS is authoritative
before treating as backup source).

Intentionally conservative: prefers duplication (Stage 1.2 snapshot, two-tier
NAS+R2) over cleverness; defers DVC until after risky consolidation is done.
For a more aggressive variant (skip pre-migration snapshot, adopt DVC during
migration), flag and we'll revise.

## Related documents

- `archive/ARCHIVE-MANIFEST.md` — source of phase3a/c/pv supersession claims
- `.gitignore` — confirms gitignored paths needing explicit migration
- `CLAUDE.md` — reboot-lock on rpi-server, sapphire-is-compute rule
- `inputs/rasters/README.md` — needs D1 source documentation
- `planning/repo-cleanup-backlog.md` — cross-reference before Stage 4 pruning
