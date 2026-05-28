# BurrowMCP — Session 21 Notes
**Date:** 2026-05-13
**Machine:** Jynx13 (remote, NY)
**Participants:** JBird + Claude

---

## Overview

Extended session focused on fixing the Splunk integration in BurrowMCP, diagnosing and resolving a critical Splunk license violation caused by over-aggressive data collection, and bringing Krypton1t3's Splunk Universal Forwarder under full BurrowMCP remote control.

---

## 1. Splunk Path & SSH Fix (`tools/splunk_tools.py`)

### Problem
`splunk_search` was broken due to a hardcoded Splunk binary path (`/Applications/Splunk/bin/splunk`) that doesn't exist on Jynx13 or EagleEye11. The original `.bak` file had the correct path (`/Volumes/Bird's Nest/Applications/Splunk/bin/splunk`) pointing to the Bird's Nest external volume on EagleEye11, but this had been overwritten during a previous fix attempt.

### Attempted: REST API approach
Rewrote `splunk_tools.py` to use Splunk's REST API (port 8089) directly over Tailscale — cleaner than SSH+CLI, no subprocess overhead. Updated `config.py` to point `SPLUNK_HOST` at EagleEye11's Tailscale IP (`100.113.239.38`).

**Result:** Hit a hard Splunk Free limitation — the free license explicitly disables remote REST API access (HTTP 401: "Remote login disabled because you are using a free license").

### Final fix: SSH + CLI
Reverted to SSH+CLI approach with corrected details:
- **Binary path:** `/Volumes/Bird's Nest/Applications/Splunk/bin/splunk` (Bird's Nest external volume)
- **SSH user:** `EagleEye11` (Splunk runs as this macOS user, not `burrowuser`)
- **Time filtering:** `-earliest`/`-latest` CLI flags are silently ignored by Splunk Free — fixed by embedding time modifiers directly in the SPL query string: `earliest=-24h latest=now <query>`
- **`config.py`:** Removed unused `SPLUNK_HOST`, `SPLUNK_PORT`, `SPLUNK_USER`, `SPLUNK_PASS` — none apply to Splunk Free SSH+CLI approach. Added `SPLUNK_BIN` path.

---

## 2. Splunk License Violation — Root Cause & Fix

### Problem
Splunk Free's 500 MB/day indexing cap was being exceeded repeatedly, locking out all searches on user indexes. `index=_internal` searches still worked; everything else returned a license error.

### Diagnosis
Queried `_internal` for per-source ingest over 24h. Top offenders:

| Source | Daily Ingest |
|---|---|
| `/var/log/com.apple.xpc.launchd/launchd.log` | ~1.4 GB |
| Splunk `metrics.log` (self-indexing) | ~975 MB |
| `ps` command output (Unix TA) | ~906 MB |
| `top` command output (Unix TA) | ~797 MB |
| Forwarder log feedback loop | ~1.4 GB combined |

The Splunk Unix Technology Add-on (TA) was collecting `ps`, `top`, `who`, `openPorts`, and `openPortsEnhanced` output every **60 seconds**. macOS's `launchd.log` was being swept up by the `monitor:///var/log` stanza and generating enormous volume.

### Fix — `Splunk_TA_nix/local/inputs.conf` on EagleEye11
- `ps.sh`, `top.sh`, `who.sh`, `openPorts.sh`, `openPortsEnhanced.sh`: interval changed from **60s → 3600s**
- `monitor:///var/log`: added `blacklist = com\.apple\.xpc\.launchd` to exclude `launchd.log`
- Reloaded via `splunk reload monitor` (confirmed: "Monitor inputs reloaded")

**Projected result:** `ps` + `top` + `who` + `openPorts` drop from ~2.8 GB/day to ~47 MB/day. Combined with launchd.log exclusion, total daily ingest should fall well under 500 MB. License violation window clears automatically within a few days.

### Forwarder status at time of fix
- **EagleEye11:** ~543 MB/day (still slightly over; will normalise as throttled scripts cycle onto new intervals)
- **SkorpiOm:** ~74 MB/day ✅
- **Jynx13:** ~9 MB/day ✅
- **Krypton1t3:** not reporting (forwarder was down — see Section 3)

---

## 3. Daily Ingest Watchdog (`scripts/splunk_ingest_check.sh`)

Created `/Users/jbird13/BurrowMCP/scripts/splunk_ingest_check.sh` — a daily cron job that:
- SSHes into EagleEye11 and runs a per-source ingest query for the last 24h
- Fires a macOS notification if any source exceeds **400 MB** (80% of the 500 MB/day cap)
- Logs all results to `/Users/jbird13/BurrowMCP/logs/splunk_ingest_check.log`

Registered in Jynx13's crontab: **runs daily at 08:00**.

```
0 8 * * * /Users/jbird13/BurrowMCP/scripts/splunk_ingest_check.sh
```

---

## 4. Krypton1t3 — Splunk Forwarder & BurrowMCP Setup

### Problem
Krypton1t3's Splunk Universal Forwarder was not running and had never been registered as a systemd service. BurrowMCP had no SSH access for `burrowuser` on Krypton1t3.

### Actions taken (JBird, on Krypton1t3 directly)
- Started the Splunk forwarder manually
- Ran `splunk enable boot-start` → registered as `SplunkForwarder.service` (systemd, enabled)
- Set up passwordless sudo for `splunk` binary restart

### Actions taken (via BurrowMCP/Claude, remote from Jynx13)
- Confirmed `burrowuser` already existed on Krypton1t3 (created in a prior session)
- Added `burrow_ed25519` public key to `/home/burrowuser/.ssh/authorized_keys`
- Set correct permissions (700 `.ssh`, 600 `authorized_keys`) and ownership
- Ran `sudo restorecon -R /home/burrowuser/.ssh` to fix SELinux context
- Created `/etc/sudoers.d/burrowuser` with passwordless sudo for `SplunkForwarder` systemd operations (validated with `visudo -cf`)
- Added `SplunkForwarder` to `ALLOWED_SERVICES` in `config.py`

### Verification
`BurrowMCP → run_burrow_command(service_status, Krypton1t3, SplunkForwarder)` returned:
```
Active: active (running) since Wed 2026-05-13 13:47:58 EDT
```

---

## 5. Config Changes Summary

### `config.py`
- Removed: `SPLUNK_HOST`, `SPLUNK_PORT`, `SPLUNK_USER`, `SPLUNK_PASS`
- Added: `SPLUNK_BIN = "/Volumes/Bird's Nest/Applications/Splunk/bin/splunk"`
- Added: `"SplunkForwarder"` to `ALLOWED_SERVICES`

### `tools/splunk_tools.py`
- Rewrote to SSH+CLI approach (REST API ruled out by Splunk Free license)
- SSH user: `EagleEye11` (owns the Splunk process)
- Time filters embedded in SPL (CLI flags not honoured by Splunk Free)
- Noise filter retained for known harmless Splunk CLI stderr output

### `tools/ssh_tools.py`
- No net changes (per-node key override approach was explored and correctly reverted to maintain uniform `burrowuser` logging)

---

## 6. Outstanding / Follow-up

- **License violation window:** Will clear automatically within a few days. `index=*` searches (including Jynx13 and Krypton1t3 forwarder data) will resume working once cleared.
- **EagleEye11 ingest:** Still slightly over 500 MB/day as of this session. Throttled TA scripts need one full cycle (up to 1h) to fully take effect. Tomorrow's cron check will confirm.
- **`jynx13_to_krypton` key:** Exists on Jynx13 (`~/.ssh/jynx13_to_krypton`) and is authorised for `SuperSkorp_7` on Krypton1t3. Retained for direct admin access; BurrowMCP continues to use `burrowuser` + `burrow_ed25519` exclusively.
